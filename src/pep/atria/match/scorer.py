"""Pairwise compatibility scoring across multiple dimensions.

Given two Players, return a DimensionScores record with each axis in
[0, 1]. 1.0 = perfectly compatible on that dimension; 0.0 = maximally
incompatible. The matcher then takes a weighted sum for overall score.

Each scorer is a pure function and independently testable. This is the
opposite of the "one number" (Elo) approach: compatibility is structural,
not ordinal.
"""

from __future__ import annotations

from dataclasses import dataclass

from .player import BehaviorFlag, CommStyle, Player, SessionGoal


@dataclass(frozen=True)
class DimensionScores:
    skill: float
    tempo: float
    communication: float
    role: float
    tilt: float
    goal: float
    behavior: float


# ── individual dimension scorers ────────────────────────────────────────

def skill_score(a: Player, b: Player, *, rating_scale: float = 400.0) -> float:
    """Closeness on the Elo scale. Identical ratings → 1.0; ratings
    differing by `rating_scale` (default 400, Elo's natural unit) → 0.0.
    Accounts for uncertainty: if either player has high uncertainty
    (new / returning), the score is more forgiving."""
    delta = abs(a.rating - b.rating)
    combined_uncertainty = (a.uncertainty + b.uncertainty) / 2
    # Effective scale widens with uncertainty (new players get wider pools)
    effective_scale = rating_scale + combined_uncertainty * 0.5
    return max(0.0, 1.0 - delta / effective_scale)


def tempo_score(a: Player, b: Player) -> float:
    """Alignment of play tempo. |delta| = 0 → 1.0; delta = 1 → 0.0."""
    return max(0.0, 1.0 - abs(a.tempo - b.tempo))


_COMM_MATRIX = {
    (CommStyle.VOCAL, CommStyle.VOCAL): 1.0,
    (CommStyle.VOCAL, CommStyle.TEXT): 0.60,
    (CommStyle.VOCAL, CommStyle.MUTED): 0.25,
    (CommStyle.VOCAL, CommStyle.REACTIVE): 0.70,
    (CommStyle.TEXT, CommStyle.TEXT): 0.85,
    (CommStyle.TEXT, CommStyle.MUTED): 0.50,
    (CommStyle.TEXT, CommStyle.REACTIVE): 0.65,
    (CommStyle.MUTED, CommStyle.MUTED): 0.80,
    (CommStyle.MUTED, CommStyle.REACTIVE): 0.55,
    (CommStyle.REACTIVE, CommStyle.REACTIVE): 0.75,
}


def communication_score(a: Player, b: Player) -> float:
    """Empirical table-based compatibility between communication styles.
    Vocal + muted is the worst mismatch; vocal + vocal is best."""
    key = (a.comm_style, b.comm_style) if (a.comm_style, b.comm_style) in _COMM_MATRIX else (b.comm_style, a.comm_style)
    return _COMM_MATRIX.get(key, 0.5)


def role_score(a: Player, b: Player, *, team_mode: bool = True) -> float:
    """In team modes, complementary roles are best. In 1v1, role doesn't
    matter. If either player is flexible (role_pref=None), neutral score."""
    if not team_mode:
        return 0.75  # role is roughly irrelevant in 1v1
    if a.role_pref is None or b.role_pref is None:
        return 0.75  # one is flexible, decent match
    if a.role_pref == b.role_pref:
        return 0.40  # role clash in team modes
    return 0.95  # complementary roles


def tilt_score(a: Player, b: Player) -> float:
    """Tilt tolerance compatibility. A low-tolerance player paired with
    a high-tolerance partner is ok; two low-tolerance players can
    spiral. Score favors at least one partner being resilient."""
    avg_tolerance = (a.tilt_tolerance + b.tilt_tolerance) / 2
    # Base score is the average tolerance — higher is better
    base = avg_tolerance
    # Penalty when both players are fragile (both tolerances low)
    if a.tilt_tolerance < 0.35 and b.tilt_tolerance < 0.35:
        base *= 0.6
    return min(1.0, base)


def goal_score(a: Player, b: Player) -> float:
    """How aligned are the two players on what they want from this
    session? Grinding + casual is a classic bad-experience match."""
    goal_values = {
        SessionGoal.CASUAL: 0.0,
        SessionGoal.LEARNING: 0.35,
        SessionGoal.GRINDING: 0.7,
        SessionGoal.COMPETITIVE: 1.0,
    }
    va = goal_values.get(a.session_goal, 0.5)
    vb = goal_values.get(b.session_goal, 0.5)
    return max(0.0, 1.0 - abs(va - vb))


def behavior_score(a: Player, b: Player) -> float:
    """Behavior-risk compatibility. A player with recent toxicity drags
    the score even if the partner is clean — the match IS going to feel
    bad for the clean partner. Two flagged players can be matched with
    each other at a lower risk to everyone else."""
    risk_a = a.behavior_risk
    risk_b = b.behavior_risk
    # If BOTH are flagged, score is moderate (contained to each other)
    if risk_a > 0.3 and risk_b > 0.3:
        return max(0.4, 1.0 - (risk_a + risk_b) / 3)
    # If one is flagged and one is clean, score drops sharply
    return max(0.0, 1.0 - max(risk_a, risk_b))


# ── aggregate ───────────────────────────────────────────────────────────

def compatibility(
    a: Player, b: Player, *, team_mode: bool = True
) -> DimensionScores:
    """Full pairwise scoring across all dimensions. Returns the raw
    scores; weighting happens in the matcher."""
    return DimensionScores(
        skill=skill_score(a, b),
        tempo=tempo_score(a, b),
        communication=communication_score(a, b),
        role=role_score(a, b, team_mode=team_mode),
        tilt=tilt_score(a, b),
        goal=goal_score(a, b),
        behavior=behavior_score(a, b),
    )
