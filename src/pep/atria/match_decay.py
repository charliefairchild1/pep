"""Atria Match Decay — haze primitive applied to matching.

The matching pool calcifies if old matches never fade. A pair that matched
two years ago but hasn't interacted in eighteen months is no longer a
current match — the people have changed, the context has changed, the
compatibility that existed then may not exist now. But if the pool treats
the historical match as a live edge, new matches can't claim that slot.

This is exactly what the opacity + haze primitive is for. Every match
gets an encoding strength that decays with time since last interaction;
reinforcement (a new interaction, a positive signal, a message thread)
pushes it back up. Below the reuse threshold the match slot becomes
available for fresh matching.

Module:
    - `Match` data class with match_strength, last_interact, half-life
    - `build_synthetic_pool(n)` — deterministic sim pool for the UI
    - `decay_report(pool, t_elapsed, threshold)` — stats: reclaimable,
       fresh-but-unreinforced, load-bearing-stale
    - `recommend_archive(pool, ...)` — match IDs safe to retire

LLM-free, deterministic, stub-friendly.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Iterable


@dataclass
class Match:
    id: str
    user_a: str
    user_b: str
    match_strength: float = 1.0            # initial encoding strength
    opacity_floor: float = 0.03
    last_interact_days_ago: float = 0.0    # resets on reinforcement
    half_life_days: float = 60.0           # match-memory half-life
    interactions: int = 0                  # cumulative, a proxy for "investment"
    exclusive: bool = False                # long-term / committed flag

    def effective_strength(self, t_elapsed: float = 0.0) -> float:
        total = max(0.0, self.last_interact_days_ago + t_elapsed)
        decayed = self.match_strength * (0.5 ** (total / self.half_life_days))
        return max(self.opacity_floor, decayed)

    def reinforce(self, amount: float = 0.4) -> None:
        cur = self.effective_strength()
        self.match_strength = min(1.0, cur + amount)
        self.last_interact_days_ago = 0.0
        self.interactions += 1

    def load_bearing(self) -> bool:
        """A match is load-bearing if there's real investment in it:
        exclusive commitment or many accumulated interactions."""
        return self.exclusive or self.interactions >= 12


@dataclass
class DecayReport:
    total: int
    reclaimable: int                       # below threshold, safe to archive
    load_bearing_stale: list[Match]        # below threshold but invested
    archive_candidates: list[Match]        # below threshold, low investment
    fresh: int                             # above threshold
    fresh_unreinforced: int                # above threshold, 0 reinforcements
    histogram: list[int]


def build_synthetic_pool(n: int = 80, seed: int = 7) -> list[Match]:
    rng = random.Random(seed)
    pool: list[Match] = []
    for i in range(n):
        age = rng.choice([
            rng.expovariate(1 / 30.0),     # recent
            rng.expovariate(1 / 120.0),    # older
            rng.expovariate(1 / 400.0),    # very old
        ])
        age = min(age, 2 * 365.0)
        strength = 0.7 + rng.random() * 0.3
        exclusive = rng.random() < 0.08
        # Interactions roughly scale with exclusive + recency
        if exclusive:
            interactions = rng.randint(12, 40)
        elif age < 30:
            interactions = rng.randint(1, 8)
        else:
            interactions = rng.randint(0, 4)
        pool.append(Match(
            id=f"m-{i:04d}",
            user_a=f"u-{(i * 7) % 100:03d}",
            user_b=f"u-{(i * 11 + 3) % 100:03d}",
            match_strength=strength,
            last_interact_days_ago=age,
            half_life_days=rng.choice([40.0, 60.0, 90.0]),
            interactions=interactions,
            exclusive=exclusive,
        ))
    return pool


def decay_report(
    pool: Iterable[Match],
    *,
    t_elapsed: float = 0.0,
    threshold: float = 0.12,
) -> DecayReport:
    pool = list(pool)
    histogram = [0] * 10
    reclaimable = 0
    fresh = 0
    fresh_unreinforced = 0
    lbs: list[Match] = []
    arch: list[Match] = []
    for m in pool:
        s = m.effective_strength(t_elapsed)
        bucket = min(9, int(s * 10))
        histogram[bucket] += 1
        if s < threshold:
            reclaimable += 1
            if m.load_bearing():
                lbs.append(m)
            else:
                arch.append(m)
        else:
            fresh += 1
            if m.interactions == 0:
                fresh_unreinforced += 1
    arch.sort(key=lambda m: m.effective_strength(t_elapsed))
    lbs.sort(key=lambda m: (-m.interactions, m.effective_strength(t_elapsed)))
    return DecayReport(
        total=len(pool),
        reclaimable=reclaimable,
        load_bearing_stale=lbs,
        archive_candidates=arch,
        fresh=fresh,
        fresh_unreinforced=fresh_unreinforced,
        histogram=histogram,
    )


def recommend_archive(
    pool: Iterable[Match],
    *,
    t_elapsed: float = 0.0,
    threshold: float = 0.12,
    limit: int = 20,
) -> list[Match]:
    """Ranked list of matches safe to retire: low strength, not load-bearing."""
    out: list[Match] = []
    for m in pool:
        if m.effective_strength(t_elapsed) < threshold and not m.load_bearing():
            out.append(m)
    out.sort(key=lambda m: m.effective_strength(t_elapsed))
    return out[:limit]
