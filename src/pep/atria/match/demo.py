"""Runnable demo for Atria Match.

    python -m pep.atria.match.demo

Builds a synthetic 20-player pool, picks a seed, ranks candidates with
Atria vs Elo, prints the comparison.
"""

from __future__ import annotations

import random

from .baseline import rank_by_elo
from .matcher import AtriaMatcher, ObjectiveWeights
from .player import BehaviorFlag, CommStyle, Player, SessionGoal


def _sample_pool(rng: random.Random, n: int = 20) -> list[Player]:
    comm = list(CommStyle); goal = list(SessionGoal); flag = list(BehaviorFlag)
    pool = []
    for i in range(n):
        flags = []
        if rng.random() < 0.15: flags.append(rng.choice(flag))
        pool.append(Player(
            id=f"p-{i:02d}",
            rating=rng.gauss(1500, 200),
            uncertainty=max(50, rng.gauss(100, 40)),
            tempo=max(0, min(1, rng.gauss(0.5, 0.25))),
            tilt_tolerance=max(0, min(1, rng.gauss(0.5, 0.25))),
            role_pref=rng.choice([None, "tank", "dps", "support"]),
            comm_style=rng.choice(comm),
            session_goal=rng.choice(goal),
            behavior_flags=flags,
        ))
    return pool


def run_demo() -> None:
    rng = random.Random(42)
    pool = _sample_pool(rng, 20)
    seed = pool[0]
    candidates = pool[1:]

    print(f"Seed: {seed.id} | rating={seed.rating:.0f} | tempo={seed.tempo:.2f} | "
          f"tilt={seed.tilt_tolerance:.2f} | comm={seed.comm_style.value} | goal={seed.session_goal.value} | "
          f"behavior_risk={seed.behavior_risk:.2f}\n")

    matcher = AtriaMatcher(weights=ObjectiveWeights.preset("ranked"))
    atria_results = matcher.rank(seed, candidates, k=5)
    elo_picks = rank_by_elo(seed, candidates, k=5)

    print("=== ATRIA top 5 (multi-objective) ===")
    for i, r in enumerate(atria_results, 1):
        print(f"  {i}. {r.candidate.id}  overall={r.overall_score:.3f}  rematch_prob={r.rematch_prob:.2f}  "
              f"weakest={r.weakest_dimension} ({getattr(r.dimension_scores, r.weakest_dimension):.2f})  "
              f"strongest={r.strongest_dimension}")

    print("\n=== ELO top 5 (rating-only) ===")
    for i, p in enumerate(elo_picks, 1):
        print(f"  {i}. {p.id}  rating={p.rating:.0f}  delta={abs(p.rating - seed.rating):.0f}")

    atria_ids = {r.candidate.id for r in atria_results}
    elo_ids = {p.id for p in elo_picks}
    overlap = atria_ids & elo_ids
    only_atria = atria_ids - elo_ids
    only_elo = elo_ids - atria_ids
    print(f"\nOverlap: {len(overlap)} / 5")
    if only_atria:
        print(f"Atria surfaced (Elo missed): {sorted(only_atria)}")
    if only_elo:
        print(f"Elo surfaced (Atria rejected): {sorted(only_elo)}")


if __name__ == "__main__":
    run_demo()
