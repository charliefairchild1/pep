"""Multi-scale coherence experiment.

Tests whether PEP's memory architecture preserves meaningful structure
across zoom levels — the careful version of the original "fractal /
heartbeat" intuition.

The question: when you score every memory against a query (fine scale),
does the relevance ordering correlate with the relevance ordering of
each memory's parent **category** (coarse scale)? If yes, the memory
field has *scale coherence* — local structure mirrors global structure,
the way a fractal does. If no, the categories don't reflect what's
actually relevant, and the architecture is just a flat archive with
labels glued on top.

The metric is **Spearman rank correlation** between two rankings of
the same set of memories:
  - Their individual relevance scores (Reactivator-style scoring)
  - The aggregate relevance score of their parent category

A coefficient near 1.0 means memories that are individually relevant
also live in categories that are collectively relevant. A coefficient
near 0 means the two scales are decoupled.

This is **not** a Hausdorff dimension or any literal fractal calculation.
It is a statistical test of whether two scales of organization agree.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from pep.embed import Embedder, cosine
from pep.memory.store import MemoryStore
from pep.schemas.memory_schema import MemoryObject


# Reused from the Reactivator. We deliberately don't import the live
# Reactivator because it touches state, mutates brightness, and writes back
# to the store. Coherence analysis must be read-only and stateless.
DEFAULT_WEIGHTS = {
    "tag_overlap": 0.35,
    "semantic": 0.30,
    "recency": 0.10,
    "brightness": 0.25,
}


def _tag_overlap(query_tags: set[str], memory_tags: set[str]) -> float:
    if not query_tags or not memory_tags:
        return 0.0
    return len(query_tags & memory_tags) / max(1, len(query_tags))


def _recency(memory: MemoryObject, now: datetime) -> float:
    delta = (now - memory.last_activated).total_seconds()
    if delta <= 0:
        return 1.0
    half_life = 86400.0  # one day
    return 0.5 ** (delta / half_life)


def score_memory(
    memory: MemoryObject,
    *,
    cue_tags: set[str],
    query_vec: list[float] | None,
    embedder: Embedder,
    now: datetime,
    weights: dict[str, float] | None = None,
) -> float:
    """Read-only relevance score for a single memory against a query cue.

    Mirrors the Reactivator's scoring formula but without state modulation,
    spreading activation, or any side effects on the store. Used to compute
    "what is the fine-scale relevance of this memory to this query?"
    """
    weights = weights or DEFAULT_WEIGHTS
    m_tags = {t.lower() for t in memory.tags}

    tag_score = _tag_overlap(cue_tags, m_tags)

    sem_score = 0.0
    if query_vec is not None and memory.core:
        mem_vec = embedder.embed_query(memory.core)
        sem_score = max(0.0, cosine(query_vec, mem_vec))

    return (
        weights["tag_overlap"] * tag_score
        + weights["semantic"] * sem_score
        + weights["recency"] * _recency(memory, now)
        + weights["brightness"] * memory.brightness
    )


def spearman(xs: list[float], ys: list[float]) -> float:
    """Spearman rank correlation between two equal-length value lists.

    Returns a value in [-1, 1]. 1 = perfect monotonic agreement.
    Implemented from scratch (no scipy dependency).
    """
    if len(xs) != len(ys):
        raise ValueError("xs and ys must have the same length")
    n = len(xs)
    if n < 2:
        return 0.0

    def rank(values: list[float]) -> list[float]:
        # Average ranks for ties (standard Spearman tie handling)
        indexed = sorted(enumerate(values), key=lambda p: p[1])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and indexed[j + 1][1] == indexed[i][1]:
                j += 1
            avg_rank = (i + j) / 2
            for k in range(i, j + 1):
                ranks[indexed[k][0]] = avg_rank
            i = j + 1
        return ranks

    rxs = rank(xs)
    rys = rank(ys)

    mean_x = sum(rxs) / n
    mean_y = sum(rys) / n
    cov = sum((rxs[i] - mean_x) * (rys[i] - mean_y) for i in range(n))
    var_x = sum((rxs[i] - mean_x) ** 2 for i in range(n))
    var_y = sum((rys[i] - mean_y) ** 2 for i in range(n))

    if var_x == 0 or var_y == 0:
        return 0.0
    return round(cov / (var_x * var_y) ** 0.5, 4)


@dataclass
class CoherenceReport:
    query: str
    n_memories: int
    n_categories: int
    n_memories_in_categories: int

    # Fine-scale: each memory's score
    memory_scores: dict[str, float] = field(default_factory=dict)
    # Coarse-scale: each category's mean and max member score
    category_mean_scores: dict[str, float] = field(default_factory=dict)
    category_max_scores: dict[str, float] = field(default_factory=dict)

    # The headline number: rank correlation between (a) each memory's
    # individual score and (b) its parent category's MEAN score, restricted
    # to memories that have a category assignment.
    coherence_mean: float = 0.0
    # Same but using the category's MAX member score as the coarse signal
    coherence_max: float = 0.0

    notes: str = ""


def measure_coherence(
    store: MemoryStore,
    embedder: Embedder,
    query: str,
    *,
    weights: dict[str, float] | None = None,
    session_id: str | None = None,
) -> CoherenceReport:
    """Score everything, group by category, compute coherence.

    If `session_id` is given, restricts the analysis to memories from that
    session — used by the dialogue tab to compute coherence per agent.
    Returns a CoherenceReport. Read-only — does not mutate the store.
    """
    now = datetime.utcnow()
    memories = store.all_memories(session_id=session_id) if session_id else store.all_memories()
    if not memories:
        return CoherenceReport(
            query=query, n_memories=0, n_categories=0,
            n_memories_in_categories=0,
            notes=f"empty {'session ' + session_id if session_id else 'store'}",
        )

    # Build the cue
    query_lower = query.lower()
    cue_tags = {w for w in query_lower.split() if len(w) > 2}
    query_vec = embedder.embed_query(query) if query.strip() else None

    # 1. Fine-scale: score every memory
    memory_scores: dict[str, float] = {}
    for m in memories:
        memory_scores[m.id] = round(
            score_memory(
                m, cue_tags=cue_tags, query_vec=query_vec,
                embedder=embedder, now=now, weights=weights,
            ),
            4,
        )

    # 2. Coarse-scale: aggregate per category. When restricted to a session,
    # only count members that are themselves in this session (so a category
    # spanning multiple sessions still computes a per-session aggregate).
    categories = store.list_categories()
    cat_mean: dict[str, float] = {}
    cat_max: dict[str, float] = {}
    cat_member_ids: dict[str, list[str]] = {}
    in_scope = set(memory_scores.keys())

    for cat in categories:
        members = store.category_members(cat["id"])
        if not members:
            continue
        member_ids = [m.id for m in members if m.id in in_scope]
        if not member_ids:
            continue
        member_scores_list = [memory_scores[mid] for mid in member_ids]
        cat_mean[cat["id"]] = round(sum(member_scores_list) / len(member_scores_list), 4)
        cat_max[cat["id"]] = round(max(member_scores_list), 4)
        cat_member_ids[cat["id"]] = member_ids

    # 3. Coherence: per memory in a category, compare its individual score
    # to its category's aggregate score. Spearman the resulting parallel lists.
    member_scores_in_order: list[float] = []
    cat_mean_for_member: list[float] = []
    cat_max_for_member: list[float] = []

    for cat_id, member_ids in cat_member_ids.items():
        for mid in member_ids:
            member_scores_in_order.append(memory_scores.get(mid, 0.0))
            cat_mean_for_member.append(cat_mean[cat_id])
            cat_max_for_member.append(cat_max[cat_id])

    coherence_mean = spearman(member_scores_in_order, cat_mean_for_member) \
        if len(member_scores_in_order) >= 2 else 0.0
    coherence_max = spearman(member_scores_in_order, cat_max_for_member) \
        if len(member_scores_in_order) >= 2 else 0.0

    notes = ""
    if not categories:
        notes = "no categories — run `pep consolidate` to create them"
    elif not member_scores_in_order:
        notes = "no memories are assigned to any category"

    return CoherenceReport(
        query=query,
        n_memories=len(memories),
        n_categories=len(categories),
        n_memories_in_categories=len(member_scores_in_order),
        memory_scores=memory_scores,
        category_mean_scores=cat_mean,
        category_max_scores=cat_max,
        coherence_mean=coherence_mean,
        coherence_max=coherence_max,
        notes=notes,
    )


def compare_per_agent_coherence(
    store: MemoryStore,
    embedder: Embedder,
    query: str,
    *,
    sessions: list[str],
) -> dict:
    """Compute coherence per session AND across the union of sessions.

    Used by the Dialogue tab to answer the §8.8 research question:
    does the joint memory across two agents have different coherence
    than each agent's individual memory? Returns a dict of
    {session_name: CoherenceReport-like dict, "_combined": ...}.
    """
    result: dict[str, dict] = {}
    for session in sessions:
        report = measure_coherence(store, embedder, query, session_id=session)
        result[session] = {
            "n_memories": report.n_memories,
            "n_categories": report.n_categories,
            "n_memories_in_categories": report.n_memories_in_categories,
            "coherence_mean": report.coherence_mean,
            "coherence_max": report.coherence_max,
            "notes": report.notes,
        }
    # Combined: no session filter
    combined = measure_coherence(store, embedder, query)
    result["_combined"] = {
        "n_memories": combined.n_memories,
        "n_categories": combined.n_categories,
        "n_memories_in_categories": combined.n_memories_in_categories,
        "coherence_mean": combined.coherence_mean,
        "coherence_max": combined.coherence_max,
        "notes": combined.notes,
    }
    return result


def format_report(report: CoherenceReport, *, top_n: int = 8) -> str:
    """Render a CoherenceReport as a human-readable text block."""
    lines: list[str] = []
    lines.append(f"Multi-scale coherence for query: {report.query!r}")
    lines.append("-" * 60)
    lines.append(f"Memories: {report.n_memories}   Categories: {report.n_categories}")
    lines.append(f"Memories in categories: {report.n_memories_in_categories}")
    if report.notes:
        lines.append(f"Note: {report.notes}")
    lines.append("")

    lines.append(f"Coherence (Spearman ρ between memory rank and parent category rank):")
    lines.append(f"  using category MEAN as coarse signal: {report.coherence_mean:+.3f}")
    lines.append(f"  using category MAX  as coarse signal: {report.coherence_max:+.3f}")
    lines.append("")
    lines.append("Interpretation:")
    lines.append("  +1.0 = fine and coarse scales perfectly agree")
    lines.append("   0.0 = the two scales are decoupled (no shared structure)")
    lines.append("  -1.0 = scales actively disagree (categorization is fighting relevance)")
    lines.append("")

    if report.memory_scores:
        lines.append(f"Top {top_n} memories by individual relevance:")
        top_mems = sorted(report.memory_scores.items(), key=lambda kv: kv[1], reverse=True)[:top_n]
        for mid, score in top_mems:
            lines.append(f"  {score:>6.3f}  {mid}")
        lines.append("")

    if report.category_mean_scores:
        lines.append(f"Top {top_n} categories by mean member relevance:")
        top_cats = sorted(
            report.category_mean_scores.items(), key=lambda kv: kv[1], reverse=True
        )[:top_n]
        for cid, score in top_cats:
            mx = report.category_max_scores.get(cid, 0.0)
            lines.append(f"  mean={score:>6.3f}  max={mx:>6.3f}  {cid}")

    return "\n".join(lines)
