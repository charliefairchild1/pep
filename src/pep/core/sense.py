"""Sense Mapper + Ambiguity Tracker.

Detects terms in the query whose usage across existing memories spans
multiple distinct "senses" (operationalized as different tag neighborhoods).
For each such term, picks the most likely sense given the OTHER terms in the
current query, and records the decision + alternatives in the trace so the
dashboard can show it.

**Limitation (without real embeddings):** sense detection is entirely
tag-co-occurrence-based. It cannot distinguish *semantic* similarity, only
*lexical* co-occurrence. So "bank" as in "river bank" vs. "bank" as in
"investment bank" can only be distinguished if those two uses have
sufficiently different tag neighborhoods in stored memories. With pseudo-
embeddings, this works OK for well-tagged memories and poorly for thinly-
tagged ones. Real Voyage embeddings would make this module much more
powerful. Be honest about this in the trace.
"""

from __future__ import annotations

from collections import defaultdict

from pep.memory.store import MemoryStore
from pep.schemas.memory_schema import MemoryObject
from pep.schemas.pep_packet import ResolvedTerm, SenseCandidate

# A term needs this many distinct "sense clusters" to be flagged as ambiguous.
MIN_SENSES = 2
# Minimum memories that share a tag for it to be considered a query term candidate.
MIN_SUPPORT = 2
# Jaccard threshold: two tag neighborhoods count as "same sense" if overlap >= this.
# Set low because tag sets are typically small (3-6 tags), so even one shared
# tag often signals the same conceptual sense.
SAME_SENSE_THRESHOLD = 0.15
# If the margin between top sense and #2 is below this, ambiguity stays unresolved.
AMBIGUITY_MARGIN = 0.25


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _cluster_tag_neighborhoods(
    term: str, memories: list[MemoryObject],
) -> list[tuple[set[str], list[str]]]:
    """For each memory containing `term` in its tags, collect the other tags
    as its "tag neighborhood." Then cluster neighborhoods by Jaccard similarity
    so that the same conceptual sense collapses into one representative cluster.

    Returns a list of (cluster_tag_set, member_ids) pairs.
    """
    neighborhoods: list[tuple[set[str], str]] = []
    for m in memories:
        m_tags = {t.lower() for t in m.tags}
        if term not in m_tags:
            continue
        # The neighborhood is the other tags (minus the term itself)
        neighborhood = m_tags - {term}
        if not neighborhood:
            continue
        neighborhoods.append((neighborhood, m.id))

    if not neighborhoods:
        return []

    # Greedy clustering: assign each neighborhood to the first cluster it
    # overlaps sufficiently with. Otherwise start a new cluster.
    clusters: list[tuple[set[str], list[str]]] = []
    for nhood, mid in neighborhoods:
        assigned = False
        for cluster_tags, cluster_mids in clusters:
            if _jaccard(nhood, cluster_tags) >= SAME_SENSE_THRESHOLD:
                cluster_tags |= nhood
                cluster_mids.append(mid)
                assigned = True
                break
        if not assigned:
            clusters.append((set(nhood), [mid]))

    # Filter out clusters with too few supporting memories
    return [(tags, mids) for tags, mids in clusters if len(mids) >= MIN_SUPPORT]


def disambiguate(
    *,
    cue_terms: set[str],
    query_context: set[str],
    memories: list[MemoryObject],
) -> list[ResolvedTerm]:
    """Detect ambiguous terms in the cue and pick the most likely sense.

    `cue_terms`: the Reactivator's cue set (lowercased).
    `query_context`: all words in the query (lowercased, content words only).
    `memories`: all candidate memories from the store.

    Returns a ResolvedTerm for every ambiguous cue term (terms with only one
    sense are NOT returned — they're not interesting for the trace).
    """
    resolved: list[ResolvedTerm] = []

    for term in cue_terms:
        clusters = _cluster_tag_neighborhoods(term, memories)
        if len(clusters) < MIN_SENSES:
            continue

        # Build SenseCandidates from each cluster
        candidates: list[SenseCandidate] = []
        for cluster_tags, cluster_mids in clusters:
            # Score: overlap between this cluster's tags and the OTHER query words.
            # Higher = this sense is more consistent with what the user is asking.
            overlap = len(cluster_tags & query_context) / max(1, len(cluster_tags))
            label = term + ":" + "+".join(sorted(cluster_tags)[:4])
            candidates.append(SenseCandidate(
                sense_label=label,
                context_tags=sorted(cluster_tags)[:12],
                supporting_memory_ids=cluster_mids[:8],
                confidence=round(overlap, 4),
            ))

        candidates.sort(key=lambda c: c.confidence, reverse=True)
        top = candidates[0]
        alts = candidates[1:]
        margin = (top.confidence - alts[0].confidence) if alts else 1.0

        ambiguity_score = 1.0 - margin
        resolved.append(ResolvedTerm(
            term=term,
            ambiguity_score=round(ambiguity_score, 4),
            chosen_sense=top,
            alternatives=alts,
            margin=round(margin, 4),
            branched=False,  # Phase 2 doesn't branch, just detects + picks
        ))

    return resolved
