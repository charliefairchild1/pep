"""Elo-only baseline — the one-scalar matcher Atria is replacing.

Kept as a reference implementation so eval can directly measure the
delta between Atria's multi-objective ranking and a pure rating-window
matcher.
"""

from __future__ import annotations

from .player import Player


def elo_score(a: Player, b: Player, *, rating_scale: float = 400.0) -> float:
    """The 'fair match' score Elo tries to optimize: closeness of
    ratings. Identical → 1.0; differing by `rating_scale` → 0.0."""
    delta = abs(a.rating - b.rating)
    return max(0.0, 1.0 - delta / rating_scale)


def rank_by_elo(seed: Player, candidates: list[Player], k: int = 10) -> list[Player]:
    """Return the top-k candidates by Elo closeness to the seed."""
    scored = [(elo_score(seed, c), c) for c in candidates if c.id != seed.id and c.id not in seed.blocked]
    scored.sort(key=lambda p: p[0], reverse=True)
    return [c for _, c in scored[:k]]
