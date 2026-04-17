"""Vectora Context — state modulation on the retrieval graph.

Tracks per-session recent activity and uses it to modulate retrieval.
Recent activity becomes a weighted centroid in embedding space (the
"context vector"). At retrieval time, documents near the context vector
get boosted; documents far from it get damped. Same query returns
different results per user per context.
"""

from __future__ import annotations

import math
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Iterable

from .document import Document
from .embeddings import cosine_similarity
from .retrieval import RetrievalMode, RetrievalResult, VectoraRetriever


@dataclass
class ContextEvent:
    """A single recorded view/interaction on a document."""

    doc_id: str
    at: float = field(default_factory=time.time)
    weight: float = 1.0  # explicit weight if the caller wants to emphasize


@dataclass
class ContextConfig:
    """Per-session configuration for context tracking."""

    half_life_seconds: float = 900.0  # 15 min default
    max_window: int = 50  # cap on events retained
    context_weight: float = 0.4  # how strongly to weight context vs raw retrieval


class ContextTracker:
    """Per-session recent-activity tracker + context-modulated retrieval.

    Workflow:
        ct = ContextTracker(retriever)
        ct.record_view("user-42", "doc-17")
        ct.record_view("user-42", "doc-19")
        results = ct.contextual_retrieve("user-42", "merge strategy", k=10)

    Sessions are maintained in-memory. Call `clear_session(sid)` to honor
    user delete requests.
    """

    def __init__(
        self,
        retriever: VectoraRetriever,
        config: ContextConfig | None = None,
    ) -> None:
        self.retriever = retriever
        self.config = config or ContextConfig()
        self._sessions: dict[str, deque[ContextEvent]] = {}

    # ── session management ──────────────────────────────────────────────
    def record_view(self, session_id: str, doc_id: str, weight: float = 1.0) -> None:
        if self.retriever.graph.get_document(doc_id) is None:
            raise KeyError(f"doc_id not in corpus: {doc_id!r}")
        events = self._sessions.setdefault(
            session_id, deque(maxlen=self.config.max_window)
        )
        events.append(ContextEvent(doc_id=doc_id, weight=weight))

    def clear_session(self, session_id: str) -> bool:
        return self._sessions.pop(session_id, None) is not None

    def session_size(self, session_id: str) -> int:
        return len(self._sessions.get(session_id, []))

    def recent_views(self, session_id: str, limit: int = 10) -> list[ContextEvent]:
        events = self._sessions.get(session_id, deque())
        return list(events)[-limit:]

    # ── context vector ──────────────────────────────────────────────────
    def _decayed_weights(self, session_id: str, at: float | None = None) -> list[tuple[str, float]]:
        """Return [(doc_id, weight)] with time-decayed importance."""
        now = at if at is not None else time.time()
        events = self._sessions.get(session_id)
        if not events:
            return []
        out: list[tuple[str, float]] = []
        for e in events:
            elapsed = max(0.0, now - e.at)
            decay = 0.5 ** (elapsed / self.config.half_life_seconds)
            w = e.weight * decay
            if w > 0.01:
                out.append((e.doc_id, w))
        return out

    def context_vector(self, session_id: str, at: float | None = None) -> list[float] | None:
        """Weighted centroid of embeddings of recently-viewed documents.
        Returns None if the session has no decayed-in-window events."""
        weighted = self._decayed_weights(session_id, at)
        if not weighted:
            return None
        dim: int | None = None
        accum: list[float] = []
        total_w = 0.0
        for doc_id, w in weighted:
            doc = self.retriever.graph.get_document(doc_id)
            if doc is None or not doc.embedding:
                continue
            if dim is None:
                dim = len(doc.embedding)
                accum = [0.0] * dim
            total_w += w
            for i, x in enumerate(doc.embedding):
                accum[i] += w * x
        if dim is None or total_w <= 0:
            return None
        vec = [x / total_w for x in accum]
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]

    # ── context-modulated retrieval ─────────────────────────────────────
    def contextual_retrieve(
        self,
        session_id: str,
        query: str,
        k: int = 10,
        decay: float = 0.4,
        context_weight: float | None = None,
    ) -> list[RetrievalResult]:
        """Retrieve with context modulation.

        Score = (1 - w) × raw_vectora_score + w × cos(doc, context_vector),
        where w = context_weight (per-query override or config default).
        """
        if not self.retriever._graph_built:
            self.retriever.build_graph()

        w = context_weight if context_weight is not None else self.config.context_weight
        ctx_vec = self.context_vector(session_id)

        # Base retrieval — ask for more than k so we have room to re-rank
        candidates = self.retriever.retrieve(
            query, k=max(k * 3, 15), mode=RetrievalMode.VECTORA, decay=decay
        )
        if ctx_vec is None or w <= 0:
            return candidates[:k]

        # Re-score with context boost
        rescored: list[RetrievalResult] = []
        for res in candidates:
            ctx_sim = cosine_similarity(ctx_vec, res.doc.embedding) if res.doc.embedding else 0.0
            blended = (1 - w) * res.score + w * ctx_sim
            new_breakdown = dict(res.score_breakdown)
            new_breakdown["raw_vectora"] = res.score
            new_breakdown["context_boost"] = ctx_sim
            new_breakdown["blended_weight"] = w
            rescored.append(
                RetrievalResult(
                    doc=res.doc,
                    score=blended,
                    hop_distance=res.hop_distance,
                    score_breakdown=new_breakdown,
                )
            )
        rescored.sort(key=lambda r: r.score, reverse=True)
        return rescored[:k]

    def compare(
        self,
        session_id: str,
        query: str,
        k: int = 8,
        decay: float = 0.4,
    ) -> dict[str, list[RetrievalResult]]:
        """Return both plain retrieval and context-modulated retrieval
        side-by-side. Useful for the playground to show the delta."""
        plain = self.retriever.retrieve(query, k=k, mode=RetrievalMode.VECTORA, decay=decay)
        ctx = self.contextual_retrieve(session_id, query, k=k, decay=decay)
        return {"plain": plain, "contextual": ctx}
