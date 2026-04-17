"""Atria Found — cofounder compatibility scoring.

Dimensions: complementary skills, conflict resolution, equity philosophy,
work pace, life-stage stability, vision alignment.

The decision a YC partner makes by intuition, made explicit and queryable.
Identifies pairs most likely to still be talking in 18 months.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .core import GenericMatcher, ProfileBase


@dataclass
class FounderProfile(ProfileBase):
    skills: list[str] = field(default_factory=list)  # "technical", "business", "design", "sales", "ops"
    conflict_style: str = "debate"  # "debate" / "consensus" / "defer" / "avoid"
    equity_philosophy: str = "equal"  # "equal" / "merit-based" / "role-based" / "flexible"
    pace: float = 0.5             # 0=marathon → 1=sprint
    stability: float = 0.5        # 0=high-risk-tolerance → 1=needs-stability
    vision: list[str] = field(default_factory=list)  # key phrases: "ai", "b2b", "consumer", "impact", "scale"
    runway_months: int = 12


def _skill_complement(a: FounderProfile, b: FounderProfile) -> float:
    overlap = set(a.skills) & set(b.skills)
    union = set(a.skills) | set(b.skills)
    if not union:
        return 0.5
    # More coverage (diverse skills) is better; full overlap is worst
    diversity = 1 - (len(overlap) / len(union))
    return min(1.0, 0.3 + diversity * 0.7)


_CONFLICT_COMPAT = {
    ("debate", "debate"): 0.85,
    ("debate", "consensus"): 0.70,
    ("debate", "defer"): 0.50,
    ("debate", "avoid"): 0.30,
    ("consensus", "consensus"): 0.80,
    ("consensus", "defer"): 0.65,
    ("consensus", "avoid"): 0.40,
    ("defer", "defer"): 0.35,
    ("defer", "avoid"): 0.30,
    ("avoid", "avoid"): 0.20,
}


def _conflict_score(a: FounderProfile, b: FounderProfile) -> float:
    key = (a.conflict_style, b.conflict_style)
    if key not in _CONFLICT_COMPAT:
        key = (b.conflict_style, a.conflict_style)
    return _CONFLICT_COMPAT.get(key, 0.5)


def _equity_score(a: FounderProfile, b: FounderProfile) -> float:
    if a.equity_philosophy == b.equity_philosophy:
        return 1.0
    if "flexible" in (a.equity_philosophy, b.equity_philosophy):
        return 0.80
    return 0.40


def _pace_score(a: FounderProfile, b: FounderProfile) -> float:
    return max(0.0, 1.0 - abs(a.pace - b.pace))


def _stability_score(a: FounderProfile, b: FounderProfile) -> float:
    return max(0.0, 1.0 - abs(a.stability - b.stability) * 1.2)


def _vision_score(a: FounderProfile, b: FounderProfile) -> float:
    if not a.vision or not b.vision:
        return 0.4
    overlap = set(a.vision) & set(b.vision)
    union = set(a.vision) | set(b.vision)
    return len(overlap) / len(union) if union else 0.4


DIMENSIONS = {
    "skill_complement": _skill_complement,
    "conflict": _conflict_score,
    "equity": _equity_score,
    "pace": _pace_score,
    "stability": _stability_score,
    "vision": _vision_score,
}

DEFAULT_WEIGHTS = {
    "skill_complement": 0.20, "conflict": 0.25, "equity": 0.15,
    "pace": 0.15, "stability": 0.10, "vision": 0.15,
}


def make_matcher(weights: dict[str, float] | None = None) -> GenericMatcher:
    return GenericMatcher(DIMENSIONS, weights or DEFAULT_WEIGHTS)


SEED_PROFILES: list[FounderProfile] = [
    FounderProfile(id="f01", skills=["technical", "ops"], conflict_style="debate", equity_philosophy="equal", pace=0.7, stability=0.4, vision=["ai", "b2b", "scale"], metadata={"label": "Technical cofounder, fast pace"}),
    FounderProfile(id="f02", skills=["business", "sales"], conflict_style="consensus", equity_philosophy="equal", pace=0.6, stability=0.5, vision=["b2b", "scale"], metadata={"label": "Business cofounder, consensus"}),
    FounderProfile(id="f03", skills=["design", "business"], conflict_style="debate", equity_philosophy="merit-based", pace=0.8, stability=0.3, vision=["consumer", "ai"], metadata={"label": "Design+business, aggressive"}),
    FounderProfile(id="f04", skills=["technical"], conflict_style="avoid", equity_philosophy="flexible", pace=0.4, stability=0.8, vision=["ai", "impact"], metadata={"label": "Cautious solo technical"}),
    FounderProfile(id="f05", skills=["business", "ops", "sales"], conflict_style="consensus", equity_philosophy="role-based", pace=0.5, stability=0.6, vision=["b2b", "impact"], metadata={"label": "Ops-heavy business"}),
    FounderProfile(id="f06", skills=["technical", "design"], conflict_style="debate", equity_philosophy="equal", pace=0.7, stability=0.5, vision=["consumer", "scale"], metadata={"label": "Full-stack builder"}),
    FounderProfile(id="f07", skills=["sales"], conflict_style="defer", equity_philosophy="merit-based", pace=0.9, stability=0.2, vision=["scale"], metadata={"label": "Hyperactive sales-only"}),
    FounderProfile(id="f08", skills=["technical", "business"], conflict_style="consensus", equity_philosophy="equal", pace=0.6, stability=0.5, vision=["ai", "b2b", "impact"], metadata={"label": "Balanced generalist"}),
]
