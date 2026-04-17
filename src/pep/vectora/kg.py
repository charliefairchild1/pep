"""Vectora Graph — hybrid knowledge-graph builder.

Layers typed, provenance-tagged edges on top of embedding similarity.
Same node set, multiple edge types. Queries can filter by edge type or
weight types separately.

Embedding edges come automatically from the retriever. Knowledge-graph
edges come from either explicit ingestion (manual triples) or an
extraction pass (LLM-backed, optional). Co-citation / co-occurrence
edges come from bulk ingestion.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable

from .document import Document
from .embeddings import cosine_similarity
from .graph import Edge
from .retrieval import VectoraRetriever


class EdgeProvenance(str, Enum):
    """Where did this edge come from?"""

    EMBEDDING = "embedding"  # derived from vector similarity
    KEYWORD = "keyword"      # derived from token overlap
    MANUAL = "manual"        # ingested by a human / curator
    EXTRACTED = "extracted"  # extracted by an LLM pipeline
    COOCCURRENCE = "cooccurrence"  # statistical co-mention


@dataclass(frozen=True)
class TypedEdge:
    """An edge with an explicit relation type and provenance."""

    source: str
    target: str
    relation: str  # e.g. "born_in", "part_of", "cites"
    weight: float = 1.0
    provenance: EdgeProvenance = EdgeProvenance.MANUAL
    confidence: float = 1.0  # [0, 1]; how trustworthy this edge is


@dataclass
class TraversalResult:
    """Result of a typed graph walk."""

    doc_id: str
    text: str
    relations_to_seed: list[tuple[str, str]]  # [(relation, intermediary_id), ...]
    total_weight: float
    hop_distance: int


class VectoraKG:
    """Hybrid knowledge graph layered on a VectoraRetriever.

    Workflow:
        kg = VectoraKG(retriever)
        kg.add_triple("einstein", "born_in", "ulm")
        kg.add_triple("einstein", "developed", "relativity")
        kg.add_triples([("einstein", "worked_at", "patent_office")])
        neighbors = kg.typed_neighbors("einstein", relations=["born_in"])
        paths = kg.traverse("einstein", max_hops=2)
    """

    def __init__(self, retriever: VectoraRetriever) -> None:
        self.retriever = retriever
        # source → list[TypedEdge]
        self._typed_adj: dict[str, list[TypedEdge]] = defaultdict(list)
        self._all_typed: list[TypedEdge] = []

    # ── ingestion ───────────────────────────────────────────────────────
    def add_triple(
        self,
        source: str,
        relation: str,
        target: str,
        weight: float = 1.0,
        provenance: EdgeProvenance = EdgeProvenance.MANUAL,
        confidence: float = 1.0,
    ) -> TypedEdge:
        if self.retriever.graph.get_document(source) is None:
            raise KeyError(f"unknown source doc: {source!r}")
        if self.retriever.graph.get_document(target) is None:
            raise KeyError(f"unknown target doc: {target!r}")
        edge = TypedEdge(
            source=source, target=target, relation=relation,
            weight=weight, provenance=provenance, confidence=confidence,
        )
        self._typed_adj[source].append(edge)
        self._all_typed.append(edge)
        return edge

    def add_triples(self, triples: Iterable[tuple]) -> int:
        """Bulk ingest. Each triple is (source, relation, target)
        or (source, relation, target, weight)
        or (source, relation, target, weight, provenance, confidence)."""
        n = 0
        for t in triples:
            if len(t) == 3:
                self.add_triple(t[0], t[1], t[2])
            elif len(t) == 4:
                self.add_triple(t[0], t[1], t[2], weight=t[3])
            elif len(t) == 6:
                self.add_triple(
                    t[0], t[1], t[2], weight=t[3],
                    provenance=EdgeProvenance(t[4]) if not isinstance(t[4], EdgeProvenance) else t[4],
                    confidence=t[5],
                )
            else:
                raise ValueError(f"triple must be 3, 4, or 6 elements; got {len(t)}")
            n += 1
        return n

    def edit_edge(
        self, source: str, relation: str, target: str, new_confidence: float | None = None
    ) -> TypedEdge | None:
        """Find and update an edge's confidence. Returns the updated edge
        or None if not found."""
        for i, edge in enumerate(self._typed_adj.get(source, [])):
            if edge.relation == relation and edge.target == target:
                updated = TypedEdge(
                    source=edge.source, target=edge.target, relation=edge.relation,
                    weight=edge.weight, provenance=edge.provenance,
                    confidence=new_confidence if new_confidence is not None else edge.confidence,
                )
                self._typed_adj[source][i] = updated
                return updated
        return None

    def remove_edge(self, source: str, relation: str, target: str) -> bool:
        adj = self._typed_adj.get(source, [])
        for i, edge in enumerate(adj):
            if edge.relation == relation and edge.target == target:
                adj.pop(i)
                self._all_typed = [
                    e for e in self._all_typed
                    if not (e.source == source and e.relation == relation and e.target == target)
                ]
                return True
        return False

    # ── queries ─────────────────────────────────────────────────────────
    def typed_neighbors(
        self,
        source: str,
        relations: list[str] | None = None,
        min_confidence: float = 0.0,
    ) -> list[TypedEdge]:
        """Direct typed neighbors of a node. If `relations` is given,
        filter to those; otherwise return all."""
        results = []
        for edge in self._typed_adj.get(source, []):
            if relations and edge.relation not in relations:
                continue
            if edge.confidence < min_confidence:
                continue
            results.append(edge)
        results.sort(key=lambda e: e.weight * e.confidence, reverse=True)
        return results

    def traverse(
        self,
        start: str,
        relations: list[str] | None = None,
        max_hops: int = 2,
        min_confidence: float = 0.0,
    ) -> list[TraversalResult]:
        """BFS walk through typed edges from `start`. Returns documents
        reachable within `max_hops`, with the relation path used."""
        if self.retriever.graph.get_document(start) is None:
            raise KeyError(f"unknown start doc: {start!r}")
        visited = {start}
        results: list[TraversalResult] = []
        frontier: list[tuple[str, int, list[tuple[str, str]], float]] = [(start, 0, [], 1.0)]
        while frontier:
            next_frontier: list[tuple[str, int, list[tuple[str, str]], float]] = []
            for src, hop, path, weight in frontier:
                if hop >= max_hops:
                    continue
                for edge in self._typed_adj.get(src, []):
                    if relations and edge.relation not in relations:
                        continue
                    if edge.confidence < min_confidence:
                        continue
                    if edge.target in visited:
                        continue
                    visited.add(edge.target)
                    new_path = path + [(edge.relation, edge.source)]
                    combined_weight = weight * edge.weight * edge.confidence
                    tgt_doc = self.retriever.graph.get_document(edge.target)
                    if tgt_doc:
                        results.append(TraversalResult(
                            doc_id=edge.target,
                            text=tgt_doc.text,
                            relations_to_seed=new_path,
                            total_weight=combined_weight,
                            hop_distance=hop + 1,
                        ))
                    next_frontier.append((edge.target, hop + 1, new_path, combined_weight))
            frontier = next_frontier
        results.sort(key=lambda r: r.total_weight, reverse=True)
        return results

    # ── stats ───────────────────────────────────────────────────────────
    def stats(self) -> dict:
        by_relation = defaultdict(int)
        by_provenance = defaultdict(int)
        for e in self._all_typed:
            by_relation[e.relation] += 1
            by_provenance[e.provenance.value] += 1
        return {
            "typed_edges": len(self._all_typed),
            "unique_relations": len(by_relation),
            "by_relation": dict(by_relation),
            "by_provenance": dict(by_provenance),
        }

    def all_edges(self) -> list[TypedEdge]:
        return list(self._all_typed)

    def to_viz_data(self) -> dict:
        """Return nodes + edges in a format a front-end visualizer can render."""
        return {
            "nodes": [
                {"id": d.id, "text": d.text, "metadata": dict(d.metadata)}
                for d in self.retriever.graph.documents()
            ],
            "edges": [
                {
                    "source": e.source, "target": e.target,
                    "relation": e.relation, "weight": round(e.weight, 3),
                    "provenance": e.provenance.value, "confidence": round(e.confidence, 3),
                }
                for e in self._all_typed
            ],
        }
