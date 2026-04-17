"""Vectora Watch — anomaly + novelty scoring on streaming items.

Given a corpus (the baseline "pattern"), score new incoming items by how
far they lie from the pattern in embedding space and graph structure.
The residual is the signal; the threshold is adaptive.

Same primitive Strata's Unusual Move Scanner uses on equities, surfaced
as a general-purpose anomaly scorer for any content stream.
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass
from typing import Iterable

from .document import Document
from .embeddings import cosine_similarity
from .retrieval import VectoraRetriever


@dataclass
class WatchResult:
    """Per-item anomaly score with explanation components."""

    doc_id: str
    text: str
    residual: float  # 0-100, higher = more anomalous
    label: str  # "normal" / "notable" / "unusual" / "extreme"
    # Explanation: which components drove the score
    distance_component: float  # 0-100: how far from centroid
    neighbor_component: float  # 0-100: how weak its graph connections are
    novelty_component: float   # 0-100: how unlike recent history


@dataclass
class WatchConfig:
    """Thresholds and weights for the residual formula."""

    # Weight breakdown (must sum to ~1)
    weight_distance: float = 0.45
    weight_neighbor: float = 0.30
    weight_novelty: float = 0.25
    # Thresholds for the label
    notable_threshold: float = 40
    unusual_threshold: float = 70
    extreme_threshold: float = 85
    # Rolling window for "recent history" component
    recent_window: int = 30
    # Adaptive threshold: target this fraction of items flagged as unusual
    target_flag_rate: float = 0.05


class VectoraWatch:
    """Anomaly/novelty scorer layered on a VectoraRetriever.

    Workflow:
        watch = VectoraWatch(retriever)
        for item in incoming_stream:
            result = watch.score_item(item)
            if result.residual >= watch.config.unusual_threshold:
                alert(result)
    """

    def __init__(
        self,
        retriever: VectoraRetriever,
        config: WatchConfig | None = None,
    ) -> None:
        self.retriever = retriever
        self.config = config or WatchConfig()
        self._recent_scores: deque[float] = deque(maxlen=200)
        self._recent_items: deque[list[float]] = deque(maxlen=self.config.recent_window)

    # ── centroid + neighbor helpers ─────────────────────────────────────
    def _centroid(self) -> list[float] | None:
        docs = self.retriever.graph.documents()
        if not docs or not docs[0].embedding:
            return None
        dim = len(docs[0].embedding)
        accum = [0.0] * dim
        n = 0
        for d in docs:
            if not d.embedding:
                continue
            for i, x in enumerate(d.embedding):
                accum[i] += x
            n += 1
        if n == 0:
            return None
        centroid = [x / n for x in accum]
        norm = math.sqrt(sum(x * x for x in centroid)) or 1.0
        return [x / norm for x in centroid]

    def _nearest_neighbor_similarity(self, embedding: list[float]) -> float:
        best = 0.0
        for doc in self.retriever.graph.documents():
            if not doc.embedding:
                continue
            sim = cosine_similarity(embedding, doc.embedding)
            if sim > best:
                best = sim
        return best

    # ── scoring ─────────────────────────────────────────────────────────
    def score_item(self, item_text: str, item_id: str = "incoming") -> WatchResult:
        """Score a single incoming item against the current pattern."""
        if not self.retriever._graph_built:
            self.retriever.build_graph()
        embedding = self.retriever.embedder.embed([item_text])[0]

        # Component 1: distance from centroid (0-100)
        centroid = self._centroid()
        if centroid:
            centroid_sim = cosine_similarity(embedding, centroid)
            distance_comp = max(0.0, min(100.0, (1 - centroid_sim) * 100))
        else:
            distance_comp = 50.0

        # Component 2: weakness of graph connections (0-100)
        # If the nearest neighbor has low similarity, the item does not
        # fit into the existing graph
        nn_sim = self._nearest_neighbor_similarity(embedding)
        neighbor_comp = max(0.0, min(100.0, (1 - nn_sim) * 100))

        # Component 3: novelty vs recent history (0-100)
        # Compare against the mean of recently-scored items
        if self._recent_items:
            avg_sim = 0.0
            for recent in self._recent_items:
                avg_sim += cosine_similarity(embedding, recent)
            avg_sim /= len(self._recent_items)
            novelty_comp = max(0.0, min(100.0, (1 - avg_sim) * 100))
        else:
            novelty_comp = neighbor_comp  # fall back to graph when no history

        # Weighted sum
        c = self.config
        residual = (
            c.weight_distance * distance_comp
            + c.weight_neighbor * neighbor_comp
            + c.weight_novelty * novelty_comp
        )

        # Label thresholds
        if residual >= c.extreme_threshold:
            label = "extreme"
        elif residual >= c.unusual_threshold:
            label = "unusual"
        elif residual >= c.notable_threshold:
            label = "notable"
        else:
            label = "normal"

        # Update rolling state
        self._recent_items.append(embedding)
        self._recent_scores.append(residual)

        return WatchResult(
            doc_id=item_id,
            text=item_text,
            residual=round(residual, 2),
            label=label,
            distance_component=round(distance_comp, 2),
            neighbor_component=round(neighbor_comp, 2),
            novelty_component=round(novelty_comp, 2),
        )

    def score_stream(self, items: Iterable[tuple[str, str]]) -> list[WatchResult]:
        """Score a batch of (item_id, text) pairs in order."""
        return [self.score_item(text, item_id) for item_id, text in items]

    # ── adaptive threshold ──────────────────────────────────────────────
    def adaptive_threshold(self) -> float:
        """Compute the current adaptive flagging threshold. Targets
        `target_flag_rate` of recent items."""
        if len(self._recent_scores) < 20:
            return self.config.unusual_threshold
        sorted_scores = sorted(self._recent_scores, reverse=True)
        n_target = max(1, int(len(sorted_scores) * self.config.target_flag_rate))
        return sorted_scores[n_target - 1]

    def stats(self) -> dict[str, float]:
        if not self._recent_scores:
            return {"n": 0, "mean": 0, "threshold": self.config.unusual_threshold}
        return {
            "n": len(self._recent_scores),
            "mean": sum(self._recent_scores) / len(self._recent_scores),
            "max": max(self._recent_scores),
            "threshold": self.adaptive_threshold(),
        }
