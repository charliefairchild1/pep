"""VectoraRetriever — top-k baseline + spreading-activation graph retrieval."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Sequence

from .document import Document
from .embeddings import EmbedderProtocol, LocalEmbedder, cosine_similarity
from .graph import DocumentGraph, Edge


class RetrievalMode(str, Enum):
    """Retrieval algorithm to use."""

    TOPK = "topk"  # baseline: k nearest by embedding similarity
    VECTORA = "vectora"  # spreading activation across the graph


@dataclass
class RetrievalResult:
    """One result from a retrieval query."""

    doc: Document
    score: float
    hop_distance: int  # 0 = direct (top-k) match, 1 = first hop, 2 = second hop, etc.
    score_breakdown: dict[str, float] = field(default_factory=dict)


class VectoraRetriever:
    """The actual Vectora retrieval engine.

    Workflow:
        r = VectoraRetriever()
        r.add_documents([Document(id=..., text=...), ...])
        r.build_graph()  # embeds + builds edges
        results = r.retrieve("query", k=10)        # spreading activation
        baseline = r.retrieve("query", k=10, mode=RetrievalMode.TOPK)
    """

    def __init__(
        self,
        embedder: EmbedderProtocol | None = None,
        edge_top_m: int = 5,
        edge_threshold: float = 0.1,
    ) -> None:
        self.embedder: EmbedderProtocol = embedder or LocalEmbedder()
        self.graph = DocumentGraph()
        self.edge_top_m = edge_top_m
        self.edge_threshold = edge_threshold
        self._pending_docs: list[Document] = []
        self._graph_built = False

    # ── ingestion ───────────────────────────────────────────────────────
    def add_document(self, doc: Document) -> None:
        self._pending_docs.append(doc)
        self._graph_built = False

    def add_documents(self, docs: Iterable[Document]) -> None:
        for d in docs:
            self.add_document(d)

    def build_graph(self, include_keyword_edges: bool = True) -> dict[str, int]:
        """Embed all pending documents and construct the graph. Returns a
        dict with counts of nodes and edges per type.
        """
        # Move all pending docs into the graph
        if self._pending_docs:
            texts = [d.text for d in self._pending_docs]
            embeddings = self.embedder.embed(texts)
            for d, e in zip(self._pending_docs, embeddings):
                d.embedding = e
                self.graph.add_document(d)
            self._pending_docs.clear()

        emb_edges = self.graph.build_embedding_edges(
            top_m=self.edge_top_m, threshold=self.edge_threshold
        )
        kw_edges = 0
        if include_keyword_edges:
            kw_edges = self.graph.build_keyword_edges(min_overlap=2)
        self._graph_built = True
        return {
            "nodes": len(self.graph),
            "embedding_edges": emb_edges,
            "keyword_edges": kw_edges,
            "total_edges": self.graph.edge_count(),
        }

    # ── retrieval ───────────────────────────────────────────────────────
    def retrieve(
        self,
        query: str,
        k: int = 10,
        mode: RetrievalMode = RetrievalMode.VECTORA,
        decay: float = 0.4,
        max_hops: int = 3,
        seed_n: int | None = None,
    ) -> list[RetrievalResult]:
        if not self._graph_built:
            self.build_graph()
        if len(self.graph) == 0:
            return []

        # 1. Embed the query in the same space as the documents
        query_embedding = self.embedder.embed([query])[0]

        # 2. Score every doc by direct cosine similarity, attenuated by
        # the node's effective (time-decayed) opacity. Hazy memories
        # contribute less even when they're semantically relevant.
        sims: dict[str, float] = {}
        opacities: dict[str, float] = {}
        for doc in self.graph.documents():
            raw = cosine_similarity(query_embedding, doc.embedding)
            op = doc.effective_opacity()
            opacities[doc.id] = op
            sims[doc.id] = raw * op

        if mode == RetrievalMode.TOPK:
            ranked = sorted(sims.items(), key=lambda kv: kv[1], reverse=True)[:k]
            return [
                RetrievalResult(
                    doc=self.graph.get_document(doc_id),  # type: ignore[arg-type]
                    score=score,
                    hop_distance=0,
                    score_breakdown={"direct": score},
                )
                for doc_id, score in ranked
                if score > 0
            ]

        # 3. Vectora mode: spreading activation
        # Pick the top-N seeds (higher than k so we have a good starting set)
        n_seeds = seed_n or max(k, k * 2)
        seeds = sorted(sims.items(), key=lambda kv: kv[1], reverse=True)[:n_seeds]
        # Skip negligible seeds
        seeds = [(d, s) for d, s in seeds if s > 0.01]

        # 4. BFS-style spreading with decay
        # Each doc accumulates total received activation across hops
        activation: dict[str, float] = defaultdict(float)
        hop_distance: dict[str, int] = {}
        breakdown: dict[str, dict[str, float]] = defaultdict(dict)

        # Layer 0: direct seeds
        frontier: dict[str, float] = {}
        for doc_id, sim in seeds:
            activation[doc_id] += sim
            hop_distance[doc_id] = 0
            breakdown[doc_id]["direct"] = sim
            breakdown[doc_id]["opacity"] = opacities[doc_id]
            frontier[doc_id] = sim

        # Layers 1..max_hops. A relay node's outgoing activation is
        # attenuated by its own effective opacity — a hazy node not only
        # receives less directly, it also passes less along.
        for hop in range(1, max_hops + 1):
            next_frontier: dict[str, float] = defaultdict(float)
            edge_type_credit: dict[tuple[str, str], float] = defaultdict(float)
            for src_id, src_act in frontier.items():
                if src_act < 0.01:
                    continue
                src_op = opacities.get(src_id, 1.0)
                for edge in self.graph.neighbors(src_id):
                    tgt_op = opacities.get(edge.target, 1.0)
                    delivered = src_act * edge.weight * (1 - decay) ** hop * src_op * tgt_op
                    if delivered < 0.005:
                        continue
                    next_frontier[edge.target] += delivered
                    edge_type_credit[(edge.target, edge.edge_type)] += delivered
            for tgt_id, act in next_frontier.items():
                activation[tgt_id] += act
                if tgt_id not in hop_distance:
                    hop_distance[tgt_id] = hop
            for (tgt_id, etype), credit in edge_type_credit.items():
                key = f"hop{hop}_{etype}"
                breakdown[tgt_id][key] = breakdown[tgt_id].get(key, 0.0) + credit
            frontier = next_frontier

        # 5. Rank by total activation, return top-k
        ranked = sorted(activation.items(), key=lambda kv: kv[1], reverse=True)[:k]
        results: list[RetrievalResult] = []
        for doc_id, total in ranked:
            doc = self.graph.get_document(doc_id)
            if doc is None or total <= 0:
                continue
            results.append(
                RetrievalResult(
                    doc=doc,
                    score=total,
                    hop_distance=hop_distance.get(doc_id, 0),
                    score_breakdown=dict(breakdown[doc_id]),
                )
            )
        return results

    # ── stats ───────────────────────────────────────────────────────────
    def stats(self) -> dict[str, int]:
        return {
            "documents": len(self.graph),
            "edges": self.graph.edge_count(),
            "pending": len(self._pending_docs),
        }
