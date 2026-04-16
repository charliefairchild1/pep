"""Reactivator — flip the switchboard, see which lights turn on.

Slice 2C: spreading activation across the link graph + constellation detection.

The pipeline:
    1. Score every candidate memory directly from the cue (tag overlap +
       semantic + recency + brightness × state modulation).
    2. Take the strongest seeds and *spread* their activation through their
       outgoing links over N hops with multiplicative decay. A memory two hops
       away from a strong seed gets a small but real activation contribution
       proportional to (decay ** hop) * link_weight * seed_score.
    3. Re-rank everything (direct + spread).
    4. **Detect constellations**: connected components within the activated
       set, formed by mutual links of weight >= COHESION_FLOOR. Members of a
       coherent constellation get a small collective bonus on top of their
       individual score, because the cluster as a whole is brighter than any
       single star.
    5. Touch every activated memory (brightness bump, drift increment, last_activated).

The trace records cues, hops, every activated entry's component breakdown,
and every detected constellation. The dashboard reads this directly.
"""

from __future__ import annotations

from datetime import datetime

from pep.embed import Embedder, cosine
from pep.memory.store import MemoryStore
from pep.schemas.input_schema import InterpretedInput, Prediction
from pep.schemas.memory_schema import MemoryObject
from pep.core.sense import disambiguate
from pep.schemas.pep_packet import (
    ActivationEntry,
    ActivationTrace,
    CategoryDescent,
    Constellation,
)
from pep.schemas.state_schema import State


# Default scoring weights. Each policy can override these.
# `category_match` is the new "fortune-teller fold" signal: members of
# categories whose top_tags overlap the cue get a bonus, because the
# category itself is the right fold to open for this query.
DEFAULT_WEIGHTS = {
    "tag_overlap": 0.30,
    "semantic": 0.25,
    "recency": 0.10,
    "brightness": 0.15,
    "link_proximity": 0.10,
    "category_match": 0.10,
}

# How many top categories count as "descended into"
DESCENT_TOP_K = 3

# Tuning knobs
ACTIVATION_FLOOR = 0.05
TOP_K = 5
DEFAULT_HOPS = 2
DEFAULT_DECAY = 0.5
COHESION_FLOOR = 0.25         # min link weight to count toward a constellation
CONSTELLATION_BONUS = 0.08    # max additive bonus on a member's score
STRATEGIC_TRIGGER_FLOOR = 0.18  # max activation below this → invoke strategic search
STRATEGIC_FLOOR = 0.02          # the wider pass uses a lower floor


def _tag_overlap(query_tags: set[str], memory_tags: set[str]) -> float:
    if not query_tags or not memory_tags:
        return 0.0
    return len(query_tags & memory_tags) / max(1, len(query_tags))


def _recency(memory: MemoryObject, now: datetime) -> float:
    delta = (now - memory.last_activated).total_seconds()
    if delta <= 0:
        return 1.0
    half_life = 86400.0
    return 0.5 ** (delta / half_life)


def _state_modulation(memory: MemoryObject, state: State) -> float:
    if not memory.state_modulation:
        return 1.0
    multiplier = 1.0
    for state_var, factor in memory.state_modulation.items():
        value = getattr(state, state_var, 0.0)
        multiplier *= 1.0 + (factor - 1.0) * value
    return max(0.1, multiplier)


def _score_categories(
    cue_set: set[str], categories: list[dict],
) -> list[CategoryDescent]:
    """Score every category by tag overlap with the cue set.

    A category's "score" is the fraction of its top_tags that match a cue.
    Categories with zero overlap are dropped. The result is sorted descending.
    The top DESCENT_TOP_K categories become the "descended-into" folds.
    """
    scored: list[CategoryDescent] = []
    for cat in categories:
        top_tags = {t.lower() for t in (cat.get("top_tags") or [])}
        if not top_tags:
            continue
        overlap = len(cue_set & top_tags) / len(top_tags)
        if overlap > 0:
            scored.append(CategoryDescent(
                category_id=cat["id"],
                cue_match_score=round(overlap, 4),
                member_count=int(cat.get("member_count") or 0),
            ))
    scored.sort(key=lambda d: d.cue_match_score, reverse=True)
    return scored


def _category_match(
    memory_id: str,
    membership: dict[str, set[str]],
    top_category_ids: set[str],
) -> float:
    """How well does this memory belong to one of the descended categories?

    1.0 if it's a member of any top-scoring category, 0.0 otherwise. We
    don't reward multiple memberships — being in any top category is enough.
    """
    cat_ids = membership.get(memory_id)
    if not cat_ids:
        return 0.0
    return 1.0 if (cat_ids & top_category_ids) else 0.0


def _direct_score(
    *,
    memory: MemoryObject,
    cue_set: set[str],
    query_vec: list[float] | None,
    embedder: Embedder,
    now: datetime,
    state: State,
    weights: dict[str, float],
    membership: dict[str, set[str]],
    top_category_ids: set[str],
) -> tuple[float, dict[str, float]]:
    """Score one memory directly from the cue (no link spreading yet)."""
    m_tags = {t.lower() for t in memory.tags}
    tag_score = _tag_overlap(cue_set, m_tags)

    sem_score = 0.0
    if query_vec is not None and memory.core:
        mem_vec = embedder.embed_query(memory.core)
        sem_score = max(0.0, cosine(query_vec, mem_vec))

    components = {
        "tag_overlap": tag_score,
        "semantic": sem_score,
        "recency": _recency(memory, now),
        "brightness": memory.brightness * _state_modulation(memory, state),
        "link_proximity": 0.0,
        "category_match": _category_match(memory.id, membership, top_category_ids),
    }
    # Only sum components that exist in weights — protects against weight
    # configurations that don't include category_match.
    score = sum(weights.get(k, 0.0) * components.get(k, 0.0) for k in weights)
    return score, components


def _build_undirected_adjacency(
    candidates_by_id: dict[str, MemoryObject],
) -> dict[str, list[tuple[str, float]]]:
    """Build a single undirected adjacency view of the link graph.

    During reactivation, links propagate activation in BOTH directions.
    The link's `relation` type still records direction (semantic, causal,
    co_activated, etc.) for other modules, but for the switchboard a
    connection is a connection — activating one end lights the other.

    Returns: {memory_id: [(neighbor_id, weight), ...]}.
    Parallel edges are coalesced by max weight.
    """
    adj: dict[str, dict[str, float]] = {mid: {} for mid in candidates_by_id}
    for source_id, mem in candidates_by_id.items():
        for link in mem.links:
            target_id = link.to_id
            if target_id not in adj:
                # Pointer to a memory not in this candidate set; skip.
                continue
            adj[source_id][target_id] = max(adj[source_id].get(target_id, 0.0), link.weight)
            adj[target_id][source_id] = max(adj[target_id].get(source_id, 0.0), link.weight)
    return {k: list(v.items()) for k, v in adj.items()}


def _spread_activation(
    *,
    direct_scores: dict[str, float],
    adjacency: dict[str, list[tuple[str, float]]],
    hops: int,
    decay: float,
    weight: float,
) -> dict[str, float]:
    """Propagate activation N hops through the (undirected) link graph.

    Returns a dict of {memory_id: spread_score_contribution}. The contribution
    is added to each memory's link_proximity component by the caller.

    Strategy: take the strongest direct scorers as seeds. From each seed,
    activation flows to neighbors at decay × link_weight × seed_score, then
    to neighbors-of-neighbors at decay² × …, and so on for `hops` rounds.
    Activation does NOT loop back into the seed itself (a memory only ever
    receives spread, never re-spreads what it received in the same call).
    """
    spread: dict[str, float] = {}
    if not direct_scores:
        return spread

    sorted_seeds = sorted(direct_scores.items(), key=lambda kv: kv[1], reverse=True)
    seed_count = max(1, len(sorted_seeds) // 2)
    seed_ids = {mid for mid, _ in sorted_seeds[:seed_count]}

    # frontier: {memory_id: activation_at_this_hop}
    frontier: dict[str, float] = {mid: direct_scores[mid] for mid in seed_ids}

    for hop in range(1, hops + 1):
        next_frontier: dict[str, float] = {}
        hop_decay = decay ** hop
        for source_id, source_activation in frontier.items():
            for neighbor_id, link_weight in adjacency.get(source_id, []):
                if neighbor_id in seed_ids:
                    # Don't re-feed activation back to the seeds; that would
                    # create double-counting.
                    continue
                contribution = source_activation * hop_decay * link_weight * weight
                if contribution <= 0:
                    continue
                spread[neighbor_id] = spread.get(neighbor_id, 0.0) + contribution
                # Carry the contribution into the next frontier so it can spread
                # further at the next hop, but with that hop's own decay applied.
                next_frontier[neighbor_id] = max(
                    next_frontier.get(neighbor_id, 0.0), contribution
                )
        if not next_frontier:
            break
        frontier = next_frontier

    return spread


def _detect_constellations(
    *,
    activated: list[ActivationEntry],
    candidates_by_id: dict[str, MemoryObject],
) -> list[Constellation]:
    """Find connected components in the activated set, joined by mutual links.

    A constellation is a connected subgraph (>=2 nodes) where edges are links
    of weight >= COHESION_FLOOR between *currently activated* memories.
    """
    activated_ids = {e.memory_id for e in activated}
    if len(activated_ids) < 2:
        return []

    # Build undirected adjacency only between activated members
    adj: dict[str, set[str]] = {mid: set() for mid in activated_ids}
    edge_weights: dict[tuple[str, str], float] = {}
    for mid in activated_ids:
        mem = candidates_by_id.get(mid)
        if not mem:
            continue
        for link in mem.links:
            if link.to_id in activated_ids and link.weight >= COHESION_FLOOR:
                adj[mid].add(link.to_id)
                adj[link.to_id].add(mid)
                key = tuple(sorted((mid, link.to_id)))
                # If two parallel links exist, keep the strongest
                edge_weights[key] = max(edge_weights.get(key, 0.0), link.weight)

    # Connected components via DFS
    seen: set[str] = set()
    components: list[set[str]] = []
    for start in activated_ids:
        if start in seen:
            continue
        stack = [start]
        comp: set[str] = set()
        while stack:
            node = stack.pop()
            if node in comp:
                continue
            comp.add(node)
            stack.extend(n for n in adj[node] if n not in comp)
        seen |= comp
        if len(comp) >= 2:
            components.append(comp)

    # Build Constellation objects
    score_by_id = {e.memory_id: e.score for e in activated}
    constellations: list[Constellation] = []
    for i, comp in enumerate(components):
        # Internal edges only (within the component)
        internal_edges = [
            w for (a, b), w in edge_weights.items()
            if a in comp and b in comp
        ]
        cohesion = (sum(internal_edges) / len(internal_edges)) if internal_edges else 0.0
        collective = sum(score_by_id.get(mid, 0.0) for mid in comp)
        constellations.append(
            Constellation(
                id=i,
                member_ids=sorted(comp),
                collective_score=round(collective, 4),
                cohesion=round(cohesion, 4),
            )
        )

    return constellations


def _apply_constellation_bonus(
    *,
    activated: list[ActivationEntry],
    constellations: list[Constellation],
) -> None:
    """Add a small bonus to each constellation member's score in place.

    The bonus scales with cohesion: a tightly-linked cluster gives a bigger
    bump than a loose one. Also tags each entry with its constellation id.
    """
    for c in constellations:
        bonus = CONSTELLATION_BONUS * c.cohesion
        member_set = set(c.member_ids)
        for entry in activated:
            if entry.memory_id in member_set:
                entry.constellation_id = c.id
                entry.score += bonus
                entry.components["constellation"] = round(bonus, 4)


def _should_fallback(top: list[ActivationEntry]) -> tuple[bool, str]:
    """Decide whether the normal pass produced too little to be useful."""
    if not top:
        return True, "no_activation"
    if top[0].score < STRATEGIC_TRIGGER_FLOOR:
        return True, f"weak_activation(top_score={top[0].score:.2f})"
    return False, ""


def _strategic_search(
    *,
    candidates: list[MemoryObject],
    cue_set: set[str],
    embedder: Embedder,
    query_vec: list[float] | None,
    interpreted: InterpretedInput,
    state: State,
    weights: dict[str, float],
    now: datetime,
    excluded_ids: set[str],
    top_k: int,
) -> list[ActivationEntry]:
    """A wider, slower second pass when the main reactivation came up weak.

    Differences from the main pass:
      - Lower activation floor (let weaker matches through)
      - Substring tag matching (not just exact-token overlap)
      - Recency and brightness get a slightly higher relative weight
      - Doesn't apply spreading activation; this is a deliberate scan
    """
    boosted = dict(weights)
    boosted["recency"] = weights.get("recency", 0.10) + 0.05
    boosted["brightness"] = weights.get("brightness", 0.15) + 0.05

    cue_substrings = [c for c in cue_set if len(c) >= 4]

    found: list[ActivationEntry] = []
    for m in candidates:
        if m.id in excluded_ids:
            continue
        m_tags = {t.lower() for t in m.tags}

        # Exact overlap
        exact = _tag_overlap(cue_set, m_tags)
        # Substring overlap: any cue token appearing inside any tag
        substring_hits = sum(
            1
            for sub in cue_substrings
            for tag in m_tags
            if sub in tag and sub != tag
        )
        substring_score = min(1.0, substring_hits * 0.25)
        tag_score = max(exact, substring_score)

        sem_score = 0.0
        if query_vec is not None and m.core:
            mem_vec = embedder.embed_query(m.core)
            sem_score = max(0.0, cosine(query_vec, mem_vec))

        components = {
            "tag_overlap": round(tag_score, 4),
            "semantic": round(sem_score, 4),
            "recency": round(_recency(m, now), 4),
            "brightness": round(m.brightness * _state_modulation(m, state), 4),
            "link_proximity": 0.0,
            "strategic": 1.0,
        }
        score = sum(boosted.get(k, 0.0) * components.get(k, 0.0) for k in boosted)

        if score < STRATEGIC_FLOOR:
            continue

        found.append(
            ActivationEntry(
                memory_id=m.id,
                score=round(score, 4),
                components=components,
                face_used=_pick_face(m, interpreted),
            )
        )

    found.sort(key=lambda e: e.score, reverse=True)
    return found[:top_k]


def reactivate(
    *,
    store: MemoryStore,
    embedder: Embedder,
    interpreted: InterpretedInput,
    prediction: Prediction,
    state: State,
    session_id: str,
    weights: dict[str, float] | None = None,
    top_k: int = TOP_K,
    hops: int = DEFAULT_HOPS,
    decay: float = DEFAULT_DECAY,
) -> tuple[list[MemoryObject], ActivationTrace]:
    """Score every candidate, spread activation, detect constellations, return top set."""
    weights = weights or DEFAULT_WEIGHTS
    now = datetime.utcnow()

    cues = list(dict.fromkeys(
        [t.lower() for t in prediction.expected_context_tags]
        + [e.lower() for e in interpreted.entities]
        + [w.lower() for w in interpreted.topic.split()]
    ))
    cue_set = set(cues)
    query_text = interpreted.topic + " " + " ".join(interpreted.entities)
    query_vec = embedder.embed_query(query_text) if query_text.strip() else None

    candidates = store.all_memories()
    candidates_by_id = {m.id: m for m in candidates}

    # 0. Category descent — identify which categories the cue should "open".
    # Build a memory→categories membership map so the per-memory scorer can
    # check it in O(1).
    all_categories = store.list_categories()
    descended = _score_categories(cue_set, all_categories)
    top_categories = descended[:DESCENT_TOP_K]
    top_category_ids = {d.category_id for d in top_categories}

    membership: dict[str, set[str]] = {}
    for cat in all_categories:
        if cat["id"] not in top_category_ids:
            # Only build membership for descended categories (cheaper)
            continue
        for member in store.category_members(cat["id"]):
            membership.setdefault(member.id, set()).add(cat["id"])

    # 1. Direct scoring from the cue (now with category_match component)
    direct_scores: dict[str, float] = {}
    components_by_id: dict[str, dict[str, float]] = {}
    for m in candidates:
        score, components = _direct_score(
            memory=m,
            cue_set=cue_set,
            query_vec=query_vec,
            embedder=embedder,
            now=now,
            state=state,
            weights=weights,
            membership=membership,
            top_category_ids=top_category_ids,
        )
        if score >= ACTIVATION_FLOOR:
            direct_scores[m.id] = score
            components_by_id[m.id] = components

    # 2. Spreading activation across N hops (links treated as undirected)
    adjacency = _build_undirected_adjacency(candidates_by_id)
    spread = _spread_activation(
        direct_scores=direct_scores,
        adjacency=adjacency,
        hops=hops,
        decay=decay,
        weight=weights["link_proximity"],
    )

    # Combine direct + spread into final scores. Memories that only got there
    # via spreading activation (not direct cue match) still count.
    all_ids = set(direct_scores) | set(spread)
    scored: list[ActivationEntry] = []
    for mid in all_ids:
        components = components_by_id.get(mid, {
            "tag_overlap": 0.0, "semantic": 0.0, "recency": 0.0,
            "brightness": 0.0, "link_proximity": 0.0,
        })
        spread_amount = spread.get(mid, 0.0)
        if spread_amount:
            components = dict(components)
            components["link_proximity"] = round(spread_amount, 4)
        score = direct_scores.get(mid, 0.0) + spread_amount
        if score < ACTIVATION_FLOOR:
            continue
        mem = candidates_by_id.get(mid)
        if not mem:
            continue
        scored.append(
            ActivationEntry(
                memory_id=mid,
                score=round(score, 4),
                components=components,
                face_used=_pick_face(mem, interpreted),
            )
        )

    scored.sort(key=lambda e: e.score, reverse=True)
    top = scored[:top_k]

    # 3. Constellation detection on the top set
    constellations = _detect_constellations(
        activated=top,
        candidates_by_id=candidates_by_id,
    )
    _apply_constellation_bonus(activated=top, constellations=constellations)
    top.sort(key=lambda e: e.score, reverse=True)

    # 4. Sense disambiguation on the cue set (Slice 2D)
    query_context_words = {w.lower() for w in interpreted.topic.split()}
    query_context_words.update(e.lower() for e in interpreted.entities)
    resolved_terms = disambiguate(
        cue_terms=cue_set,
        query_context=query_context_words,
        memories=candidates,
    )
    # TODO (Phase 3): if any resolved_term has ambiguity_score > threshold
    # AND margin is low, branch the retrieval across senses. For now we just
    # record the resolution in the trace so the dashboard can display it.

    # 5. Strategic search fallback if the main pass came up weak
    fell_back, fallback_reason = _should_fallback(top)
    if fell_back:
        existing_ids = {e.memory_id for e in top}
        strategic_results = _strategic_search(
            candidates=candidates,
            cue_set=cue_set,
            embedder=embedder,
            query_vec=query_vec,
            interpreted=interpreted,
            state=state,
            weights=weights,
            now=now,
            excluded_ids=existing_ids,
            top_k=top_k,
        )
        # Merge: strategic results are appended after the (possibly weak) main top.
        # Final list is capped at top_k. If the main pass was completely empty,
        # strategic results take over entirely.
        merged = top + strategic_results
        merged.sort(key=lambda e: e.score, reverse=True)
        top = merged[:top_k]

    # 5. Touch activated memories
    activated_objects: list[MemoryObject] = []
    for entry in top:
        store.touch_memory(entry.memory_id)
        m = store.get_memory(entry.memory_id)
        if m:
            activated_objects.append(m)

    trace = ActivationTrace(
        cues=cues,
        candidates_considered=len(candidates),
        activated=top,
        constellations=constellations,
        resolved_terms=resolved_terms,
        descended_categories=top_categories,
        hops_used=hops,
        fallback_to_strategic_search=fell_back,
        fallback_reason=fallback_reason,
        notes=f"phase3; weights={weights}; top_k={top_k}; hops={hops}; decay={decay}; descended={len(top_categories)}",
    )
    return activated_objects, trace


def _pick_face(memory: MemoryObject, interpreted: InterpretedInput) -> str:
    """Choose which face of the memory to expose for this query."""
    if not memory.faces:
        return "semantic"
    task = interpreted.task_type
    preferred = {
        "implement": "action",
        "plan": "predictive",
        "explain": "semantic",
        "explore": "predictive",
        "ask_question": "semantic",
        "command": "action",
    }.get(task, "semantic")
    if preferred in memory.faces:
        return preferred
    return next(iter(memory.faces.keys()))
