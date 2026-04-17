"""Atria Date — dating compatibility scoring.

Dimensions: values alignment, communication warmth, pace/attachment,
conflict resolution, shared interests, life-stage alignment.

Replaces single-axis "attractiveness ranking" with multi-dimensional
compatibility. Uses spreading activation to surface candidates the
user would not have filtered for.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .core import GenericMatcher, ProfileBase, RankResult


@dataclass
class DateProfile(ProfileBase):
    values: list[str] = field(default_factory=list)  # e.g. ["family", "adventure", "career"]
    warmth: float = 0.5           # 0=reserved → 1=very warm
    attachment: float = 0.5       # 0=avoidant → 1=anxious (0.5=secure)
    conflict_style: str = "compromise"  # "compromise" / "avoidant" / "confronting" / "accommodating"
    interests: list[str] = field(default_factory=list)
    life_stage: str = "established"  # "student" / "early-career" / "established" / "retired"
    age: int = 30


def _values_score(a: DateProfile, b: DateProfile) -> float:
    if not a.values or not b.values:
        return 0.5
    overlap = set(a.values) & set(b.values)
    union = set(a.values) | set(b.values)
    return len(overlap) / len(union) if union else 0.5


def _warmth_score(a: DateProfile, b: DateProfile) -> float:
    return max(0.0, 1.0 - abs(a.warmth - b.warmth))


def _attachment_score(a: DateProfile, b: DateProfile) -> float:
    # Secure (0.5) + anything = good; avoidant + anxious = worst
    dist = abs(a.attachment - b.attachment)
    avg_from_secure = (abs(a.attachment - 0.5) + abs(b.attachment - 0.5)) / 2
    return max(0.0, 1.0 - dist * 0.5 - avg_from_secure * 0.3)


_CONFLICT_COMPAT = {
    ("compromise", "compromise"): 1.0,
    ("compromise", "accommodating"): 0.85,
    ("compromise", "confronting"): 0.55,
    ("compromise", "avoidant"): 0.50,
    ("accommodating", "accommodating"): 0.70,
    ("accommodating", "confronting"): 0.40,
    ("accommodating", "avoidant"): 0.55,
    ("confronting", "confronting"): 0.35,
    ("confronting", "avoidant"): 0.30,
    ("avoidant", "avoidant"): 0.45,
}


def _conflict_score(a: DateProfile, b: DateProfile) -> float:
    key = (a.conflict_style, b.conflict_style)
    if key not in _CONFLICT_COMPAT:
        key = (b.conflict_style, a.conflict_style)
    return _CONFLICT_COMPAT.get(key, 0.5)


def _interests_score(a: DateProfile, b: DateProfile) -> float:
    if not a.interests or not b.interests:
        return 0.4
    overlap = set(a.interests) & set(b.interests)
    return min(1.0, len(overlap) / 3 + 0.3) if overlap else 0.2


_STAGE_ORDER = {"student": 0, "early-career": 1, "established": 2, "retired": 3}


def _life_stage_score(a: DateProfile, b: DateProfile) -> float:
    diff = abs(_STAGE_ORDER.get(a.life_stage, 2) - _STAGE_ORDER.get(b.life_stage, 2))
    return max(0.1, 1.0 - diff * 0.3)


DIMENSIONS = {
    "values": _values_score,
    "warmth": _warmth_score,
    "attachment": _attachment_score,
    "conflict": _conflict_score,
    "interests": _interests_score,
    "life_stage": _life_stage_score,
}

DEFAULT_WEIGHTS = {
    "values": 0.25, "warmth": 0.15, "attachment": 0.20,
    "conflict": 0.15, "interests": 0.10, "life_stage": 0.15,
}


def make_matcher(weights: dict[str, float] | None = None) -> GenericMatcher:
    return GenericMatcher(DIMENSIONS, weights or DEFAULT_WEIGHTS)


SEED_PROFILES: list[DateProfile] = [
    DateProfile(id="d01", values=["family", "adventure"], warmth=0.8, attachment=0.5, conflict_style="compromise", interests=["hiking", "cooking", "travel"], life_stage="established", age=32, metadata={"label": "Warm adventurer"}),
    DateProfile(id="d02", values=["career", "independence"], warmth=0.3, attachment=0.2, conflict_style="avoidant", interests=["tech", "fitness", "reading"], life_stage="early-career", age=28, metadata={"label": "Driven introvert"}),
    DateProfile(id="d03", values=["family", "community"], warmth=0.9, attachment=0.6, conflict_style="accommodating", interests=["cooking", "volunteering", "music"], life_stage="established", age=35, metadata={"label": "Community builder"}),
    DateProfile(id="d04", values=["adventure", "creativity"], warmth=0.7, attachment=0.5, conflict_style="compromise", interests=["music", "travel", "art"], life_stage="early-career", age=26, metadata={"label": "Creative spirit"}),
    DateProfile(id="d05", values=["career", "adventure"], warmth=0.5, attachment=0.4, conflict_style="confronting", interests=["startup", "fitness", "hiking"], life_stage="early-career", age=29, metadata={"label": "Ambitious explorer"}),
    DateProfile(id="d06", values=["family", "stability"], warmth=0.7, attachment=0.55, conflict_style="compromise", interests=["cooking", "reading", "gardening"], life_stage="established", age=38, metadata={"label": "Gentle nester"}),
    DateProfile(id="d07", values=["independence", "creativity"], warmth=0.4, attachment=0.3, conflict_style="avoidant", interests=["art", "music", "coding"], life_stage="early-career", age=25, metadata={"label": "Solo creative"}),
    DateProfile(id="d08", values=["community", "adventure"], warmth=0.85, attachment=0.5, conflict_style="compromise", interests=["volunteering", "hiking", "travel"], life_stage="established", age=33, metadata={"label": "Social adventurer"}),
    DateProfile(id="d09", values=["family", "career"], warmth=0.6, attachment=0.45, conflict_style="confronting", interests=["tech", "cooking", "fitness"], life_stage="established", age=36, metadata={"label": "Balanced achiever"}),
    DateProfile(id="d10", values=["creativity", "independence"], warmth=0.5, attachment=0.7, conflict_style="accommodating", interests=["writing", "art", "music"], life_stage="student", age=23, metadata={"label": "Anxious artist"}),
]
