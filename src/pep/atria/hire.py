"""Atria Hire — candidate-team compatibility scoring.

Dimensions: skill complementarity, culture fit, communication match,
work pace alignment, growth trajectory, team-composition gap.

Scores a candidate AGAINST a team (not pairwise), looking at how the
candidate fills the gap the team has rather than matching a single other
person. This is the key structural difference from other Atria products.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .core import GenericMatcher, ProfileBase, RankResult


@dataclass
class TeamProfile(ProfileBase):
    skills_present: list[str] = field(default_factory=list)
    skills_needed: list[str] = field(default_factory=list)
    culture: list[str] = field(default_factory=list)  # e.g. ["fast-paced", "remote-first", "flat"]
    avg_communication: float = 0.5
    avg_pace: float = 0.5
    team_size: int = 5


@dataclass
class CandidateProfile(ProfileBase):
    skills: list[str] = field(default_factory=list)
    culture_prefs: list[str] = field(default_factory=list)
    communication: float = 0.5  # 0=async → 1=sync-heavy
    pace: float = 0.5           # 0=steady → 1=sprint-oriented
    seniority: str = "mid"      # "junior" / "mid" / "senior" / "lead"
    growth_orientation: float = 0.5  # 0=maintenance → 1=wants to grow rapidly


def _skill_gap_score(team: TeamProfile, cand: CandidateProfile) -> float:
    if not team.skills_needed:
        return 0.5
    filled = set(cand.skills) & set(team.skills_needed)
    return min(1.0, len(filled) / max(1, len(team.skills_needed)) + 0.2)


def _culture_fit(team: TeamProfile, cand: CandidateProfile) -> float:
    if not team.culture or not cand.culture_prefs:
        return 0.5
    overlap = set(team.culture) & set(cand.culture_prefs)
    return len(overlap) / max(1, len(team.culture))


def _communication_match(team: TeamProfile, cand: CandidateProfile) -> float:
    return max(0.0, 1.0 - abs(team.avg_communication - cand.communication))


def _pace_match(team: TeamProfile, cand: CandidateProfile) -> float:
    return max(0.0, 1.0 - abs(team.avg_pace - cand.pace))


def _growth_fit(team: TeamProfile, cand: CandidateProfile) -> float:
    # High growth-orientation + small team = great; low growth + large team = fine
    team_factor = max(0.3, 1.0 - team.team_size / 20)
    return min(1.0, cand.growth_orientation * 0.5 + team_factor * 0.5)


_SENIORITY_WEIGHT = {"junior": 0.3, "mid": 0.5, "senior": 0.7, "lead": 0.9}


def _seniority_score(team: TeamProfile, cand: CandidateProfile) -> float:
    # Just a neutral "does the seniority make sense for the team size"
    needed = "senior" if team.team_size > 8 else "mid" if team.team_size > 3 else "junior"
    target = _SENIORITY_WEIGHT.get(needed, 0.5)
    actual = _SENIORITY_WEIGHT.get(cand.seniority, 0.5)
    return max(0.3, 1.0 - abs(target - actual))


DIMENSIONS = {
    "skill_gap": _skill_gap_score,
    "culture": _culture_fit,
    "communication": _communication_match,
    "pace": _pace_match,
    "growth": _growth_fit,
    "seniority": _seniority_score,
}

DEFAULT_WEIGHTS = {
    "skill_gap": 0.30, "culture": 0.20, "communication": 0.15,
    "pace": 0.10, "growth": 0.10, "seniority": 0.15,
}


def make_matcher(weights: dict[str, float] | None = None) -> GenericMatcher:
    return GenericMatcher(DIMENSIONS, weights or DEFAULT_WEIGHTS)


SEED_TEAM = TeamProfile(
    id="team-alpha",
    skills_present=["python", "react", "devops"],
    skills_needed=["ml", "data-eng", "security"],
    culture=["remote-first", "async-heavy", "flat"],
    avg_communication=0.4,
    avg_pace=0.6,
    team_size=6,
    metadata={"label": "ML startup team — needs ML + data engineering"},
)

SEED_CANDIDATES: list[CandidateProfile] = [
    CandidateProfile(id="h01", skills=["ml", "python", "statistics"], culture_prefs=["remote-first", "flat"], communication=0.4, pace=0.6, seniority="senior", growth_orientation=0.7, metadata={"label": "ML engineer, culture match"}),
    CandidateProfile(id="h02", skills=["data-eng", "python", "spark"], culture_prefs=["remote-first", "async-heavy"], communication=0.3, pace=0.5, seniority="mid", growth_orientation=0.8, metadata={"label": "Data engineer, async pref"}),
    CandidateProfile(id="h03", skills=["security", "devops", "compliance"], culture_prefs=["office-first", "hierarchical"], communication=0.7, pace=0.3, seniority="senior", growth_orientation=0.3, metadata={"label": "Security, culture clash"}),
    CandidateProfile(id="h04", skills=["ml", "research", "writing"], culture_prefs=["remote-first", "flat", "async-heavy"], communication=0.3, pace=0.7, seniority="lead", growth_orientation=0.6, metadata={"label": "ML lead, perfect culture"}),
    CandidateProfile(id="h05", skills=["react", "typescript"], culture_prefs=["remote-first"], communication=0.5, pace=0.5, seniority="mid", growth_orientation=0.5, metadata={"label": "Frontend (team already has)"}),
    CandidateProfile(id="h06", skills=["data-eng", "ml", "python"], culture_prefs=["flat"], communication=0.5, pace=0.6, seniority="mid", growth_orientation=0.9, metadata={"label": "Ambitious ML+data generalist"}),
    CandidateProfile(id="h07", skills=["product", "design"], culture_prefs=["office-first", "hierarchical"], communication=0.9, pace=0.4, seniority="senior", growth_orientation=0.2, metadata={"label": "Product, wrong skills + culture"}),
    CandidateProfile(id="h08", skills=["ml", "data-eng"], culture_prefs=["remote-first", "async-heavy", "flat"], communication=0.35, pace=0.55, seniority="junior", growth_orientation=0.9, metadata={"label": "Junior double-hit ML+data"}),
]
