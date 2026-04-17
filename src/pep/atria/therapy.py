"""Atria Therapy — patient-therapist matching.

Dimensions: communication style match, attachment compatibility, value
alignment, modality fit, availability alignment.

The single biggest predictor of therapy outcomes is the therapeutic
alliance quality, not the modality. This engine matches on the factors
that predict alliance quality instead of just insurance + zip code.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .core import GenericMatcher, ProfileBase


@dataclass
class PatientProfile(ProfileBase):
    communication: str = "verbal"  # "verbal" / "written" / "art-based" / "minimal"
    attachment: str = "secure"     # "secure" / "anxious" / "avoidant" / "disorganized"
    values: list[str] = field(default_factory=list)  # "spiritual", "evidence-based", "humanistic", "pragmatic"
    presenting: list[str] = field(default_factory=list)  # "anxiety", "depression", "trauma", "relationship", "grief"
    modality_pref: str | None = None  # "cbt" / "psychodynamic" / "emdr" / "dbt" / None (open)
    availability: str = "evenings"    # "mornings" / "afternoons" / "evenings" / "flexible"


@dataclass
class TherapistProfile(ProfileBase):
    communication: str = "verbal"
    attachment_competence: list[str] = field(default_factory=list)  # which attachment styles they work well with
    values: list[str] = field(default_factory=list)
    specialties: list[str] = field(default_factory=list)
    modalities: list[str] = field(default_factory=list)  # which they offer
    availability: str = "flexible"


def _comm_score(p: PatientProfile, t: TherapistProfile) -> float:
    if p.communication == t.communication:
        return 1.0
    compat = {
        ("verbal", "written"): 0.6,
        ("verbal", "art-based"): 0.5,
        ("verbal", "minimal"): 0.3,
        ("written", "art-based"): 0.55,
        ("written", "minimal"): 0.5,
        ("art-based", "minimal"): 0.4,
    }
    key = (p.communication, t.communication)
    return compat.get(key, compat.get((t.communication, p.communication), 0.5))


def _attachment_score(p: PatientProfile, t: TherapistProfile) -> float:
    if not t.attachment_competence:
        return 0.5
    if p.attachment in t.attachment_competence:
        return 0.95
    return 0.4


def _values_score(p: PatientProfile, t: TherapistProfile) -> float:
    if not p.values or not t.values:
        return 0.5
    overlap = set(p.values) & set(t.values)
    return min(1.0, len(overlap) / max(1, len(p.values)) + 0.2)


def _presenting_specialty(p: PatientProfile, t: TherapistProfile) -> float:
    if not p.presenting or not t.specialties:
        return 0.5
    overlap = set(p.presenting) & set(t.specialties)
    return min(1.0, len(overlap) / max(1, len(p.presenting)) + 0.2)


def _modality_score(p: PatientProfile, t: TherapistProfile) -> float:
    if p.modality_pref is None:
        return 0.75  # open to anything
    if not t.modalities:
        return 0.5
    return 0.95 if p.modality_pref in t.modalities else 0.3


def _availability_score(p: PatientProfile, t: TherapistProfile) -> float:
    if "flexible" in (p.availability, t.availability):
        return 0.9
    return 1.0 if p.availability == t.availability else 0.3


DIMENSIONS = {
    "communication": _comm_score,
    "attachment": _attachment_score,
    "values": _values_score,
    "specialty": _presenting_specialty,
    "modality": _modality_score,
    "availability": _availability_score,
}

DEFAULT_WEIGHTS = {
    "communication": 0.20, "attachment": 0.25, "values": 0.15,
    "specialty": 0.15, "modality": 0.10, "availability": 0.15,
}


def make_matcher(weights: dict[str, float] | None = None) -> GenericMatcher:
    return GenericMatcher(DIMENSIONS, weights or DEFAULT_WEIGHTS)


SEED_PATIENT = PatientProfile(
    id="patient-A",
    communication="verbal",
    attachment="anxious",
    values=["evidence-based", "humanistic"],
    presenting=["anxiety", "relationship"],
    modality_pref="cbt",
    availability="evenings",
    metadata={"label": "Anxious attachment, wants CBT evenings"},
)

SEED_THERAPISTS: list[TherapistProfile] = [
    TherapistProfile(id="t01", communication="verbal", attachment_competence=["anxious", "secure"], values=["evidence-based"], specialties=["anxiety", "relationship"], modalities=["cbt", "dbt"], availability="evenings", metadata={"label": "CBT specialist, anxiety focus"}),
    TherapistProfile(id="t02", communication="verbal", attachment_competence=["avoidant", "secure"], values=["humanistic"], specialties=["depression", "grief"], modalities=["psychodynamic"], availability="mornings", metadata={"label": "Psychodynamic, mornings only"}),
    TherapistProfile(id="t03", communication="written", attachment_competence=["anxious", "disorganized"], values=["evidence-based", "pragmatic"], specialties=["trauma", "anxiety"], modalities=["emdr", "cbt"], availability="flexible", metadata={"label": "Written-pref EMDR+CBT, flexible"}),
    TherapistProfile(id="t04", communication="verbal", attachment_competence=["anxious", "avoidant", "secure", "disorganized"], values=["humanistic", "spiritual"], specialties=["relationship", "grief", "anxiety"], modalities=["cbt", "psychodynamic", "dbt"], availability="evenings", metadata={"label": "Generalist, all attachments, evenings"}),
    TherapistProfile(id="t05", communication="art-based", attachment_competence=["secure"], values=["spiritual"], specialties=["trauma"], modalities=["emdr"], availability="afternoons", metadata={"label": "Art therapy, trauma only"}),
    TherapistProfile(id="t06", communication="verbal", attachment_competence=["anxious"], values=["evidence-based", "humanistic"], specialties=["anxiety", "relationship", "depression"], modalities=["cbt"], availability="evenings", metadata={"label": "Perfect match — CBT + anxiety + evenings + anxious-competent"}),
]
