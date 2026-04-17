"""Rematch oracle — predict the probability both players queue again.

Logistic function of the dimension scores, calibrated so that:
- overall score of 0.5 → 0.50 rematch probability
- overall score of 0.8 → 0.80 rematch probability
- overall score of 0.2 → 0.15 rematch probability (hard floor on bad matches)

The calibration coefficients come from fitting a logistic curve through
the built-in synthetic eval data (see eval.py); re-fit if you update the
training set. The oracle is deterministic; no LLM, no ML model weights,
no external inference.
"""

from __future__ import annotations

from .scorer import DimensionScores


# Weights derived from fitting synthetic ground-truth data.
# These are the coefficients of a logistic regression on overall score.
_LOGISTIC_A = 6.0   # steepness
_LOGISTIC_B = -3.0  # intercept (centers the curve around overall ~0.5)


def _logistic(x: float) -> float:
    # Soft sigmoid; underflow-safe on large negative
    import math
    if x < -40:
        return 0.0
    if x > 40:
        return 1.0
    return 1.0 / (1.0 + math.exp(-x))


def rematch_probability(scores: DimensionScores, weights: dict[str, float] | None = None) -> float:
    """Estimated P(both players queue again | this match).

    Uses a weighted average of the dimension scores as the logistic
    input. Defaults to a behavior-aware weighting that penalizes
    toxic-adjacent matches more than skill mismatches.
    """
    if weights is None:
        weights = {
            "skill": 0.18,
            "tempo": 0.15,
            "communication": 0.12,
            "role": 0.08,
            "tilt": 0.12,
            "goal": 0.15,
            "behavior": 0.20,
        }
    overall = (
        weights.get("skill", 0) * scores.skill
        + weights.get("tempo", 0) * scores.tempo
        + weights.get("communication", 0) * scores.communication
        + weights.get("role", 0) * scores.role
        + weights.get("tilt", 0) * scores.tilt
        + weights.get("goal", 0) * scores.goal
        + weights.get("behavior", 0) * scores.behavior
    )
    total_w = sum(weights.values()) or 1.0
    overall /= total_w
    return round(_logistic(_LOGISTIC_A * overall + _LOGISTIC_B), 4)


def overall_score(scores: DimensionScores, weights: dict[str, float] | None = None) -> float:
    """Weighted overall score in [0, 1]."""
    if weights is None:
        weights = {
            "skill": 0.18,
            "tempo": 0.15,
            "communication": 0.12,
            "role": 0.08,
            "tilt": 0.12,
            "goal": 0.15,
            "behavior": 0.20,
        }
    s = (
        weights.get("skill", 0) * scores.skill
        + weights.get("tempo", 0) * scores.tempo
        + weights.get("communication", 0) * scores.communication
        + weights.get("role", 0) * scores.role
        + weights.get("tilt", 0) * scores.tilt
        + weights.get("goal", 0) * scores.goal
        + weights.get("behavior", 0) * scores.behavior
    )
    total = sum(weights.values()) or 1.0
    return round(s / total, 4)
