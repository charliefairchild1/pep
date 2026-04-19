"""Strata Strategy Decay — haze primitive applied to the strategy library.

A strategy library calcifies if backtest-overfit shapes never fade. A
strategy that worked brilliantly in 2019 but hasn't produced residual
alpha in 18 months is not a current strategy — the regime has changed,
the edge has been arbitraged away, the assumptions no longer hold. But
if the library treats it as a live strategy, newer signal can't claim
that capacity.

PEP's haze primitive fixes this. Each strategy carries an opacity that
decays over time since its last *residual event* (a trade that actually
captured the signal it was designed for). Reinforcement pushes opacity
back up. Below the reuse threshold a strategy's capacity is reclaimable.
Load-bearing strategies (live capital allocated) get flagged as stale
rather than archived, because deallocating is an active decision that
needs a human.

Module:
    - `Strategy` dataclass: strength, last_residual_days_ago, half-life,
       residual_count, capital_allocated, regulated
    - `build_synthetic_library(n)` — deterministic sim pool for the UI
    - `decay_report(...)` — reclaimable / deallocate-review /
       never-produced / currently-producing
    - `recommend_retire(...)` — safe-to-retire ranked list

LLM-free, deterministic, stub-friendly.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Iterable


_STRAT_FAMILIES = [
    "momentum", "mean-reversion", "pairs", "sector-rotation",
    "earnings-drift", "volatility-carry", "risk-parity",
    "breakout", "calendar", "statistical-arbitrage",
]


@dataclass
class Strategy:
    id: str
    name: str
    family: str
    strength: float = 1.0
    opacity_floor: float = 0.03
    last_residual_days_ago: float = 0.0
    half_life_days: float = 45.0
    residual_count: int = 0
    capital_allocated: float = 0.0       # notional $M; 0 = paper-only
    regulated_flag: bool = False         # LF&D / compliance footprint

    def effective_strength(self, t_elapsed: float = 0.0) -> float:
        total = max(0.0, self.last_residual_days_ago + t_elapsed)
        decayed = self.strength * (0.5 ** (total / self.half_life_days))
        return max(self.opacity_floor, decayed)

    def reinforce(self, amount: float = 0.35) -> None:
        cur = self.effective_strength()
        self.strength = min(1.0, cur + amount)
        self.last_residual_days_ago = 0.0
        self.residual_count += 1

    def load_bearing(self) -> bool:
        """Deployed-with-real-capital strategies aren't safely archived
        without a human deallocation decision."""
        return self.capital_allocated > 0.5 or self.regulated_flag


@dataclass
class DecayReport:
    total: int
    reclaimable: int
    deallocate_review: list[Strategy]    # reclaimable AND load-bearing
    retire_candidates: list[Strategy]    # reclaimable AND not load-bearing
    producing: int                       # currently above threshold
    never_produced: list[Strategy]       # 0 residuals even now
    histogram: list[int]
    mean_strength: float


def build_synthetic_library(n: int = 60, seed: int = 3) -> list[Strategy]:
    rng = random.Random(seed)
    out: list[Strategy] = []
    for i in range(n):
        family = rng.choice(_STRAT_FAMILIES)
        age = rng.choice([
            rng.expovariate(1 / 20.0),   # recently active
            rng.expovariate(1 / 80.0),   # typical
            rng.expovariate(1 / 300.0),  # long tail
        ])
        age = min(age, 3 * 365.0)
        strength = 0.55 + rng.random() * 0.45
        half_life = rng.choice([30.0, 45.0, 60.0, 90.0])
        # Residual count loosely tracks age + family
        if age < 30:
            residuals = rng.randint(5, 30)
        elif age < 120:
            residuals = rng.randint(0, 10)
        else:
            residuals = rng.randint(0, 3)
        # Some never produced at all (failed strategies kept in the library)
        if rng.random() < 0.15:
            residuals = 0
        capital = 0.0
        if residuals >= 8 and rng.random() < 0.35:
            capital = round(rng.uniform(0.6, 18.0), 2)
        regulated = rng.random() < 0.06
        out.append(Strategy(
            id=f"strat-{i:04d}",
            name=f"{family.upper()}-{i:02d}",
            family=family,
            strength=strength,
            last_residual_days_ago=age,
            half_life_days=half_life,
            residual_count=residuals,
            capital_allocated=capital,
            regulated_flag=regulated,
        ))
    return out


def decay_report(
    library: Iterable[Strategy],
    *,
    t_elapsed: float = 0.0,
    threshold: float = 0.12,
) -> DecayReport:
    library = list(library)
    hist = [0] * 10
    reclaimable = 0
    producing = 0
    never: list[Strategy] = []
    dealloc: list[Strategy] = []
    retire: list[Strategy] = []
    strengths = []
    for s in library:
        eff = s.effective_strength(t_elapsed)
        strengths.append(eff)
        hist[min(9, int(eff * 10))] += 1
        if eff < threshold:
            reclaimable += 1
            if s.load_bearing():
                dealloc.append(s)
            else:
                retire.append(s)
        else:
            producing += 1
        if s.residual_count == 0:
            never.append(s)
    retire.sort(key=lambda s: s.effective_strength(t_elapsed))
    dealloc.sort(key=lambda s: -s.capital_allocated)
    never.sort(key=lambda s: -s.last_residual_days_ago)
    return DecayReport(
        total=len(library),
        reclaimable=reclaimable,
        deallocate_review=dealloc,
        retire_candidates=retire,
        producing=producing,
        never_produced=never,
        histogram=hist,
        mean_strength=(sum(strengths) / len(strengths)) if strengths else 0.0,
    )


def recommend_retire(
    library: Iterable[Strategy],
    *,
    t_elapsed: float = 0.0,
    threshold: float = 0.12,
    limit: int = 20,
) -> list[Strategy]:
    out = [s for s in library
           if s.effective_strength(t_elapsed) < threshold and not s.load_bearing()]
    out.sort(key=lambda s: s.effective_strength(t_elapsed))
    return out[:limit]
