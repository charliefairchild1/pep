"""Shared cognitive state space for all Axona products.

The four axes: novelty (how much new input the system is processing),
coherence (how well ideas hold together), bandwidth (spare processing
capacity), valence (emotional direction, negative to positive).

Every Axona product maps its domain-specific inputs into this shared
space. The state space IS the interpretation layer.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CognitiveState:
    """Position in the four-axis state space. Each axis in [-1, 1] for
    valence and [0, 1] for the others."""

    novelty: float      # [0, 1] — 0 = nothing new, 1 = overwhelmed by new
    coherence: float    # [0, 1] — 0 = fragmented, 1 = fully integrated
    bandwidth: float    # [0, 1] — 0 = depleted, 1 = fully available
    valence: float      # [-1, 1] — -1 = strongly negative, +1 = strongly positive

    def quadrant(self) -> str:
        if self.coherence > 0.6 and self.novelty > 0.4:
            return "genius"
        elif self.coherence < 0.4 and self.novelty > 0.6:
            return "chaos"
        elif self.coherence > 0.6 and self.novelty < 0.4:
            return "order"
        else:
            return "stagnation"

    def risk_level(self) -> str:
        if self.bandwidth < 0.25:
            return "high"
        if self.bandwidth < 0.45 or abs(self.valence) > 0.7:
            return "medium"
        return "low"

    def as_dict(self) -> dict[str, Any]:
        return {
            "novelty": round(self.novelty, 4),
            "coherence": round(self.coherence, 4),
            "bandwidth": round(self.bandwidth, 4),
            "valence": round(self.valence, 4),
            "quadrant": self.quadrant(),
            "risk": self.risk_level(),
        }


@dataclass
class StateAlert:
    """A flagged condition based on the cognitive state."""

    level: str       # "info" / "warning" / "critical"
    message: str
    recommendation: str


def assess_alerts(state: CognitiveState) -> list[StateAlert]:
    """Generate alerts from a cognitive state reading."""
    alerts: list[StateAlert] = []
    if state.bandwidth < 0.20:
        alerts.append(StateAlert("critical", "Bandwidth critically low", "Immediate break recommended; hand off high-stakes tasks"))
    elif state.bandwidth < 0.35:
        alerts.append(StateAlert("warning", "Bandwidth declining", "Consider a break before the next demanding task"))
    if state.coherence < 0.25 and state.novelty > 0.7:
        alerts.append(StateAlert("critical", "Coherence collapsed under high novelty — chaos state", "Reduce stimulus; structured task to restore coherence"))
    if state.valence < -0.6:
        alerts.append(StateAlert("warning", "Strong negative valence detected", "Emotional state may be affecting cognitive performance"))
    if state.valence < -0.6 and state.coherence < 0.3:
        alerts.append(StateAlert("critical", "Tilt detected — negative emotion disrupting coherence", "Coach or supervisor intervention recommended"))
    if state.coherence > 0.85 and state.bandwidth > 0.8 and state.novelty > 0.4:
        alerts.append(StateAlert("info", "Flow state detected", "Protect current conditions; do not interrupt"))
    if not alerts:
        alerts.append(StateAlert("info", "State within normal range", "No action needed"))
    return alerts


def clamp01(v: float) -> float:
    return max(0.0, min(1.0, v))


def clamp_valence(v: float) -> float:
    return max(-1.0, min(1.0, v))
