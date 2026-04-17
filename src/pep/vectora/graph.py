"""DocumentGraph — nodes (documents) and typed weighted edges."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable

from .document import Document
from .embeddings import cosine_similarity


@dataclass(frozen=True)
class Edge:
    """A typed weighted edge between two documents."""

    source: str
    target: str
    weight: float
    edge_type: str = "embedding"


class DocumentGraph:
    """Documents + typed weighted edges. Sparse adjacency by source id."""

    def __init__(self) -> None:
        self._docs: dict[str, Document] = {}
        # adjacency: source_id → list[Edge]
        self._adj: dict[str, list[Edge]] = defaultdict(list)
        self._all_edges: list[Edge] = []

    # ── nodes ───────────────────────────────────────────────────────────
    def add_document(self, doc: Document) -> None:
        if doc.id in self._docs:
            raise ValueError(f"duplicate document id: {doc.id}")
        self._docs[doc.id] = doc

    def get_document(self, doc_id: str) -> Document | None:
        return self._docs.get(doc_id)

    def documents(self) -> list[Document]:
        return list(self._docs.values())

    def __len__(self) -> int:
        return len(self._docs)

    def __contains__(self, doc_id: object) -> bool:
        return isinstance(doc_id, str) and doc_id in self._docs

    # ── edges ───────────────────────────────────────────────────────────
    def add_edge(self, edge: Edge) -> None:
        if edge.source not in self._docs or edge.target not in self._docs:
            raise ValueError(
                f"edge references unknown doc: {edge.source} → {edge.target}"
            )
        if edge.source == edge.target:
            return  # silently skip self-loops
        self._adj[edge.source].append(edge)
        self._all_edges.append(edge)

    def neighbors(self, doc_id: str) -> list[Edge]:
        return self._adj.get(doc_id, [])

    def edges(self) -> list[Edge]:
        return list(self._all_edges)

    def edge_count(self) -> int:
        return len(self._all_edges)

    # ── construction helpers ────────────────────────────────────────────
    def build_embedding_edges(self, top_m: int = 5, threshold: float = 0.1) -> int:
        """For each doc, add edges to its top-M nearest neighbors by embedding
        cosine similarity. Skips edges below `threshold`. Returns number of
        edges added."""
        docs = self.documents()
        if not docs or not docs[0].embedding:
            return 0
        added = 0
        for src in docs:
            sims: list[tuple[float, str]] = []
            for tgt in docs:
                if tgt.id == src.id:
                    continue
                sim = cosine_similarity(src.embedding, tgt.embedding)
                if sim < threshold:
                    continue
                sims.append((sim, tgt.id))
            sims.sort(reverse=True)
            for sim, tgt_id in sims[:top_m]:
                self.add_edge(Edge(src.id, tgt_id, sim, "embedding"))
                added += 1
        return added

    def build_keyword_edges(self, min_overlap: int = 2) -> int:
        """Add edges between documents sharing >= min_overlap meaningful tokens.
        Edge weight is Jaccard similarity of token sets. Returns edges added.
        """
        from .embeddings import _tokenize  # type: ignore[attr-defined]
        token_sets = {d.id: set(_tokenize(d.text)) for d in self.documents()}
        # Filter very common tokens (likely stopwords-ish)
        added = 0
        ids = list(token_sets.keys())
        for i, src_id in enumerate(ids):
            src_tokens = token_sets[src_id]
            for tgt_id in ids[i + 1 :]:
                tgt_tokens = token_sets[tgt_id]
                overlap = src_tokens & tgt_tokens
                if len(overlap) < min_overlap:
                    continue
                union = src_tokens | tgt_tokens
                jaccard = len(overlap) / len(union) if union else 0
                if jaccard < 0.05:
                    continue
                self.add_edge(Edge(src_id, tgt_id, jaccard, "keyword"))
                self.add_edge(Edge(tgt_id, src_id, jaccard, "keyword"))
                added += 2
        return added

    def add_typed_edges(self, edges: Iterable[Edge]) -> int:
        """Bulk-add edges (knowledge-graph relations, co-citation, etc.)."""
        n = 0
        for e in edges:
            self.add_edge(e)
            n += 1
        return n

    # ── opacity / haze primitive ────────────────────────────────────────
    def reusable_nodes(self, threshold: float = 0.15, at: float | None = None) -> list[Document]:
        """Documents whose effective opacity has decayed below the reuse
        threshold. These are candidates for eviction when new encoding
        needs capacity — the mechanism that makes memory finite."""
        return [d for d in self.documents() if d.is_reusable(threshold, at)]

    def reinforce(self, doc_id: str, amount: float = 0.5) -> bool:
        """Boost a document's opacity (e.g. on successful recall).
        Returns True if the doc existed, False otherwise."""
        doc = self._docs.get(doc_id)
        if doc is None:
            return False
        doc.reinforce(amount)
        return True

    def evict(self, doc_id: str) -> bool:
        """Remove a document and all its edges from the graph. Used when
        a reusable node is overwritten by new encoding."""
        if doc_id not in self._docs:
            return False
        del self._docs[doc_id]
        if doc_id in self._adj:
            del self._adj[doc_id]
        # Strip edges that point to the evicted node from other nodes' adj
        for src_id in list(self._adj.keys()):
            self._adj[src_id] = [e for e in self._adj[src_id] if e.target != doc_id]
        self._all_edges = [e for e in self._all_edges if e.source != doc_id and e.target != doc_id]
        return True

    def opacity_snapshot(self, at: float | None = None) -> dict[str, float]:
        """Current effective opacity per node. Useful for UIs that want to
        visualize the haze field across the graph."""
        return {d.id: d.effective_opacity(at) for d in self.documents()}
