"""Shared infrastructure for all Atria products.

Every Atria product (Match, Date, Hire, Found, Therapy) follows the same
pattern: a Profile with typed dimensions, a pairwise scorer, a weighted
ranker, and a rematch/re-engagement oracle. This module provides the
generic base classes so domain-specific products only define their
dimensions and weights.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Sequence


@dataclass(frozen=True)
class DimScore:
    """Score on one named dimension."""

    name: str
    value: float  # [0, 1]


@dataclass
class ProfileBase:
    """Base class for all Atria profiles. Subclasses add domain-specific
    typed fields; the scorer reads those fields by name."""

    id: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RankResult:
    """One ranked candidate with full breakdown."""

    candidate_id: str
    overall: float
    reengagement_prob: float
    dim_scores: dict[str, float]
    strongest: str
    weakest: str
    metadata: dict[str, Any] = field(default_factory=dict)


# Type alias for a dimension scorer: (profile_a, profile_b) → float in [0, 1]
DimScorerFn = Callable[[Any, Any], float]


def _logistic(x: float) -> float:
    if x < -40:
        return 0.0
    if x > 40:
        return 1.0
    return 1.0 / (1.0 + math.exp(-x))


class GenericMatcher:
    """Configurable multi-dimension ranker. Each product instantiates one
    of these with its own dimensions + weights + scorer functions.

    Usage:
        matcher = GenericMatcher(
            dimensions={"skill": skill_fn, "tempo": tempo_fn, ...},
            weights={"skill": 0.3, "tempo": 0.2, ...},
        )
        results = matcher.rank(seed_profile, candidate_profiles, k=5)
    """

    def __init__(
        self,
        dimensions: dict[str, DimScorerFn],
        weights: dict[str, float],
        *,
        logistic_a: float = 6.0,
        logistic_b: float = -3.0,
    ) -> None:
        self.dimensions = dimensions
        self.weights = weights
        self._la = logistic_a
        self._lb = logistic_b

    def score_pair(self, a: Any, b: Any) -> dict[str, float]:
        return {name: fn(a, b) for name, fn in self.dimensions.items()}

    def overall(self, dim_scores: dict[str, float]) -> float:
        total_w = sum(self.weights.values()) or 1.0
        return sum(
            self.weights.get(name, 0) * dim_scores.get(name, 0)
            for name in self.dimensions
        ) / total_w

    def reengagement(self, overall: float) -> float:
        return round(_logistic(self._la * overall + self._lb), 4)

    def rank(
        self,
        seed: Any,
        candidates: Sequence[Any],
        k: int = 10,
        *,
        exclude_ids: set[str] | None = None,
    ) -> list[RankResult]:
        exclude = exclude_ids or set()
        results: list[RankResult] = []
        for c in candidates:
            if c.id == seed.id or c.id in exclude:
                continue
            ds = self.score_pair(seed, c)
            ov = self.overall(ds)
            rp = self.reengagement(ov)
            strongest = max(ds, key=ds.get)
            weakest = min(ds, key=ds.get)
            results.append(RankResult(
                candidate_id=c.id, overall=round(ov, 4),
                reengagement_prob=rp, dim_scores={k: round(v, 4) for k, v in ds.items()},
                strongest=strongest, weakest=weakest,
                metadata=getattr(c, "metadata", {}),
            ))
        results.sort(key=lambda r: r.overall, reverse=True)
        return results[:k]
