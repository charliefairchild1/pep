"""Atria Teams — n-person team formation with complementarity constraints.

Dating, hiring, and co-founder matching are all pairwise problems in the
existing Atria core. Team formation is structurally different: the
compatibility graph has to optimize over a set of n ≥ 3 simultaneously,
AND you don't want homogeneity. Four visionaries is a worse team than
one visionary + two builders + one skeptic. The scorer has to reward
*complementarity* alongside per-pair compatibility.

This module implements the minimum operational form:

    1. `Candidate` carries a role profile (weights on visionary / builder /
       skeptic / operator / community) plus a dimensional compatibility
       vector (tempo, risk, communication-style, ambition, curiosity).

    2. `score_team(candidates, required_roles)` returns:
         - pair_score  — average per-pair compatibility on dims
         - role_coverage — how well the required role profile is filled
         - diversity  — complementarity bonus (homogeneity is penalized)
         - overall  — weighted sum of the three
         - warnings — redundancy / gap flags

    3. `optimize_team(pool, size, required_roles)` greedily assembles a
       team: pick the candidate that maximizes marginal overall score
       given the partial team so far. LLM-free; deterministic given
       seeds.

The accompanying canvas (/atria#teamform-tab) shows role coverage as a
radar chart and rank-orders a pool of 12 candidates for a 4-person team
with configurable role requirements.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field


ROLE_KEYS = ["visionary", "builder", "skeptic", "operator", "community"]
DIM_KEYS = ["tempo", "risk", "communication", "ambition", "curiosity"]


@dataclass
class Candidate:
    id: str
    name: str
    role_profile: dict[str, float]    # weights on each ROLE_KEYS, sums ≈ 1.0
    dims: dict[str, float]            # each in [0, 1]
    notes: str = ""


# ─── Pairwise compatibility ─────────────────────────────────────────────

def pair_compat(a: Candidate, b: Candidate) -> float:
    """Pair compatibility in [0, 1].

    Pure distance is wrong — matched tempo helps, matched ambition helps,
    but matched communication is neutral (different styles can work) and
    matched risk is harmful (homogeneity of risk appetite is bad for a team).

    Rule: some dims reward similarity (tempo, ambition), others reward
    diversity (risk, curiosity), one is neutral (communication).
    """
    def close(x: float, y: float) -> float:
        return 1.0 - abs(x - y)

    def apart(x: float, y: float) -> float:
        return abs(x - y)

    tempo = close(a.dims["tempo"], b.dims["tempo"])
    amb   = close(a.dims["ambition"], b.dims["ambition"])
    risk  = apart(a.dims["risk"], b.dims["risk"])              # diversity good
    cur   = apart(a.dims["curiosity"], b.dims["curiosity"])    # diversity good
    comm  = 0.5 + 0.5 * close(a.dims["communication"], b.dims["communication"])
    score = 0.25 * tempo + 0.25 * amb + 0.20 * risk + 0.15 * cur + 0.15 * comm
    return max(0.0, min(1.0, score))


# ─── Team-level score ───────────────────────────────────────────────────

@dataclass
class TeamScore:
    pair_score: float
    role_coverage: float
    diversity: float
    overall: float
    warnings: list[str] = field(default_factory=list)
    role_totals: dict[str, float] = field(default_factory=dict)


def _role_totals(team: list[Candidate]) -> dict[str, float]:
    totals = {k: 0.0 for k in ROLE_KEYS}
    for c in team:
        for k in ROLE_KEYS:
            totals[k] += c.role_profile.get(k, 0.0)
    return totals


def _role_coverage(totals: dict[str, float], required: dict[str, float]) -> float:
    """How well does team's role distribution match the required profile?

    `required` is normalized target distribution (sums to 1). The team's
    totals are normalized by team size. Coverage is 1 minus the L1
    distance between the two distributions, divided by 2 (the max L1).
    """
    size_total = sum(totals.values()) or 1.0
    team_dist = {k: totals[k] / size_total for k in ROLE_KEYS}
    l1 = sum(abs(team_dist[k] - required.get(k, 0.0)) for k in ROLE_KEYS)
    return max(0.0, 1.0 - l1 / 2.0)


def _diversity(team: list[Candidate]) -> float:
    """Reward spread of role profiles across the team."""
    if len(team) < 2:
        return 0.5
    # Compute variance on role profile distribution per role, average it.
    per_role: list[float] = []
    for k in ROLE_KEYS:
        vals = [c.role_profile.get(k, 0.0) for c in team]
        mean = sum(vals) / len(vals)
        var = sum((v - mean) ** 2 for v in vals) / len(vals)
        per_role.append(var)
    avg_var = sum(per_role) / len(per_role)
    # Variance naturally caps near 0.25 in [0, 1]; rescale to [0, 1]
    return min(1.0, avg_var / 0.15)


def score_team(
    team: list[Candidate],
    required_roles: dict[str, float] | None = None,
) -> TeamScore:
    if required_roles is None:
        required_roles = {"visionary": 0.2, "builder": 0.3, "skeptic": 0.2,
                          "operator": 0.2, "community": 0.1}

    # Pairwise
    pairs = []
    n = len(team)
    for i in range(n):
        for j in range(i + 1, n):
            pairs.append(pair_compat(team[i], team[j]))
    pair_score = sum(pairs) / len(pairs) if pairs else 0.5

    totals = _role_totals(team)
    role_cov = _role_coverage(totals, required_roles)
    diversity = _diversity(team)

    overall = 0.40 * pair_score + 0.35 * role_cov + 0.25 * diversity

    warnings: list[str] = []
    # Redundancy: a role contributes >= 55% of a position share
    dist_total = sum(totals.values()) or 1.0
    for k, v in totals.items():
        share = v / dist_total
        target = required_roles.get(k, 0.0)
        if share > target + 0.2 and v > 1.2:
            warnings.append(f"{k} oversupplied ({share:.0%} of team vs {target:.0%} target)")
        elif target > 0.1 and share < target - 0.12:
            warnings.append(f"{k} undersupplied ({share:.0%} vs {target:.0%} target)")
    if diversity < 0.25:
        warnings.append("team is homogeneous — low role-profile variance; add a counterweight")
    if pair_score < 0.45:
        warnings.append("pairwise compatibility low — tempo / ambition mismatches across members")

    return TeamScore(
        pair_score=round(pair_score, 3),
        role_coverage=round(role_cov, 3),
        diversity=round(diversity, 3),
        overall=round(overall, 3),
        warnings=warnings,
        role_totals={k: round(v, 3) for k, v in totals.items()},
    )


# ─── Optimization ──────────────────────────────────────────────────────

def optimize_team(
    pool: list[Candidate],
    size: int = 4,
    required_roles: dict[str, float] | None = None,
) -> tuple[list[Candidate], TeamScore, list[tuple[Candidate, float]]]:
    """Greedy: at each step, add the candidate that maximizes overall score
    of the resulting partial team. Returns (team, final_score, pick_order_with_deltas)."""
    remaining = list(pool)
    team: list[Candidate] = []
    pick_log: list[tuple[Candidate, float]] = []

    # Seed: pick the candidate whose role_profile is closest to required.
    if required_roles is None:
        required_roles = {"visionary": 0.2, "builder": 0.3, "skeptic": 0.2,
                          "operator": 0.2, "community": 0.1}
    def seed_fit(c: Candidate) -> float:
        return sum(min(c.role_profile.get(k, 0), required_roles.get(k, 0)) for k in ROLE_KEYS)
    seed = max(remaining, key=seed_fit)
    team.append(seed)
    remaining.remove(seed)
    pick_log.append((seed, 0.0))

    while len(team) < size and remaining:
        prev = score_team(team, required_roles).overall
        best_delta = -float("inf")
        best = None
        for c in remaining:
            trial = team + [c]
            s = score_team(trial, required_roles).overall
            delta = s - prev
            if delta > best_delta:
                best_delta = delta
                best = c
        if best is None:
            break
        team.append(best)
        remaining.remove(best)
        pick_log.append((best, best_delta))

    return team, score_team(team, required_roles), pick_log


# ─── Simulated candidate pool ───────────────────────────────────────────

_NAMES = [
    "Amaya", "Ben", "Chinonye", "Darío", "Esin", "Felix",
    "Giri", "Hana", "Inez", "Jamal", "Kai", "Lena",
]


def simulate_pool(n: int = 12, seed: int = 11) -> list[Candidate]:
    """Generate a deterministic candidate pool with a mix of role profiles
    and dimensional values."""
    import random
    rng = random.Random(seed)
    archetypes = [
        {"visionary": 0.6, "builder": 0.1, "skeptic": 0.1, "operator": 0.1, "community": 0.1},
        {"visionary": 0.1, "builder": 0.7, "skeptic": 0.1, "operator": 0.05, "community": 0.05},
        {"visionary": 0.1, "builder": 0.1, "skeptic": 0.6, "operator": 0.1, "community": 0.1},
        {"visionary": 0.05, "builder": 0.15, "skeptic": 0.1, "operator": 0.65, "community": 0.05},
        {"visionary": 0.1, "builder": 0.1, "skeptic": 0.1, "operator": 0.1, "community": 0.6},
        {"visionary": 0.3, "builder": 0.3, "skeptic": 0.2, "operator": 0.1, "community": 0.1},
        {"visionary": 0.2, "builder": 0.4, "skeptic": 0.2, "operator": 0.1, "community": 0.1},
    ]
    pool: list[Candidate] = []
    for i in range(n):
        base = archetypes[i % len(archetypes)]
        # Perturb the archetype slightly
        perturbed = {k: max(0, v + (rng.random() - 0.5) * 0.15) for k, v in base.items()}
        s = sum(perturbed.values()) or 1.0
        role_profile = {k: v / s for k, v in perturbed.items()}
        dims = {k: round(rng.random(), 3) for k in DIM_KEYS}
        pool.append(Candidate(
            id=f"cand-{i:02d}",
            name=_NAMES[i % len(_NAMES)],
            role_profile=role_profile,
            dims=dims,
            notes="",
        ))
    return pool
