"""Atria Mentor Match — asymmetric-compatibility matching for mentors.

Dating and hiring are symmetric problems: A-fit-for-B has the same
structure as B-fit-for-A. The existing Atria core scorer reflects that.

Mentorship is structurally different. "This mentor is a great fit for
this mentee" is not the same claim as "this mentee is a great fit for
this mentor." A senior mentor with 20+ years of experience might be an
incredible fit for a junior engineer in the abstract — but the junior
isn't a fit for the mentor if the mentor has no bandwidth, or the
mentor would find the mentee's questions too early-career to engage
with.

The real scoring lives on two directed edges per pair:

    mentor_fit_for_mentee  (what the mentee gets out of this)
    mentee_fit_for_mentor  (what the mentor gets out of this)

A good match requires both to be above threshold. Many ostensibly good
pairs fail the second test. The platform has to surface that.

This module implements asymmetric scoring + pool optimization:

    - Mentor / Mentee dataclasses with stage, focus areas, bandwidth,
      preferred cadence, growth goals.
    - score_mentor_to_mentee(m, e) → what mentee gains (learning delta,
      focus overlap, cadence compatibility).
    - score_mentee_to_mentor(e, m) → what mentor gains (mentee readiness,
      question depth, engagement signal, energy).
    - optimize_pool(mentors, mentees): Hungarian-lite greedy assignment
      that respects mentor bandwidth (each mentor has max_mentees).

Same LLM-free / deterministic constraints as the rest of the Atria
stack.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field


FOCUS_AREAS = [
    "engineering", "product", "design", "research", "ops",
    "career-navigation", "management", "communication", "entrepreneurship",
]
STAGES = ["intern", "junior", "mid", "senior", "staff", "principal", "exec"]
STAGE_IDX = {s: i for i, s in enumerate(STAGES)}


@dataclass
class Mentor:
    id: str
    name: str
    stage: str                              # one of STAGES
    focus: dict[str, float]                 # FOCUS_AREAS → weight 0..1
    teach_style: float                      # 0 (socratic) .. 1 (didactic)
    max_mentees: int = 3                    # capacity (bandwidth)
    energy: float = 0.7                     # 0..1 — how engaged with mentoring right now
    min_stage_gap: int = 2                  # wants mentees at least N stages below


@dataclass
class Mentee:
    id: str
    name: str
    stage: str
    focus: dict[str, float]                 # what they want to learn about
    learn_style: float                      # 0..1 — prefers socratic → didactic
    readiness: float = 0.6                  # 0..1 — ready-to-engage score
    cadence_wanted: float = 0.5             # 0 (ad hoc) .. 1 (weekly)


@dataclass
class DirectedScore:
    value: float                            # 0..1
    components: dict[str, float]
    notes: list[str]


# ─── Directed scoring ────────────────────────────────────────────────────

def _focus_overlap(a: dict[str, float], b: dict[str, float]) -> float:
    """Cosine-ish similarity on focus-area vectors."""
    dot = sum(a.get(k, 0.0) * b.get(k, 0.0) for k in FOCUS_AREAS)
    na = math.sqrt(sum(v * v for v in a.values())) or 1.0
    nb = math.sqrt(sum(v * v for v in b.values())) or 1.0
    return dot / (na * nb)


def _stage_gap(mentor: Mentor, mentee: Mentee) -> int:
    return STAGE_IDX[mentor.stage] - STAGE_IDX[mentee.stage]


def score_mentor_to_mentee(mentor: Mentor, mentee: Mentee) -> DirectedScore:
    """What does the mentee gain? Bigger = better for the mentee."""
    focus = _focus_overlap(mentor.focus, mentee.focus)
    gap = _stage_gap(mentor, mentee)
    # Too-close gap: mentee gets little. Too-far gap: mentor misses mentee's level.
    # Best gap ≈ 2–3 stages.
    if gap <= 0:
        stage_fit = 0.1                     # mentor at/below mentee = bad
    elif gap == 1:
        stage_fit = 0.55
    elif gap <= 3:
        stage_fit = 1.0
    elif gap <= 5:
        stage_fit = 0.7
    else:
        stage_fit = 0.45
    # Style alignment: mentee wants socratic, mentor is didactic = drift
    style = 1.0 - abs(mentor.teach_style - mentee.learn_style) * 0.8
    components = {"focus": focus, "stage_fit": stage_fit, "style": style}
    value = 0.5 * focus + 0.3 * stage_fit + 0.2 * style
    notes: list[str] = []
    if focus < 0.25:
        notes.append("focus overlap is weak — mentee's goals don't align with mentor's areas")
    if gap <= 0:
        notes.append("stage gap is zero or negative — mentor isn't ahead")
    if gap >= 6:
        notes.append("stage gap is too large — mentor may not engage with early-career questions")
    if abs(mentor.teach_style - mentee.learn_style) > 0.6:
        notes.append("teach/learn style mismatch — expect friction in how knowledge gets transferred")
    if not notes:
        notes.append("clean directional fit for the mentee")
    return DirectedScore(value=max(0.0, min(1.0, value)), components=components, notes=notes)


def score_mentee_to_mentor(mentee: Mentee, mentor: Mentor) -> DirectedScore:
    """What does the mentor gain from engaging? Bigger = better for the mentor."""
    focus = _focus_overlap(mentor.focus, mentee.focus)
    gap = _stage_gap(mentor, mentee)
    # Mentor wants the gap to be at least min_stage_gap
    if gap < mentor.min_stage_gap:
        gap_fit = 0.15
    elif gap <= mentor.min_stage_gap + 3:
        gap_fit = 1.0
    else:
        gap_fit = 0.55
    readiness_fit = mentee.readiness                # mentor gains more from ready mentees
    energy_fit = mentor.energy                      # mentor's own availability
    # Cadence fit
    cadence_gap = abs(mentee.cadence_wanted - 0.5)  # mentor prefers middle cadence by default
    cadence_fit = 1.0 - cadence_gap * 1.3
    components = {
        "focus": focus,
        "gap_fit": gap_fit,
        "readiness": readiness_fit,
        "energy": energy_fit,
        "cadence": max(0.0, cadence_fit),
    }
    value = (0.30 * focus
             + 0.25 * gap_fit
             + 0.20 * readiness_fit
             + 0.15 * energy_fit
             + 0.10 * max(0.0, cadence_fit))
    notes: list[str] = []
    if gap < mentor.min_stage_gap:
        notes.append("stage gap below mentor's minimum — mentor won't find it engaging")
    if readiness_fit < 0.4:
        notes.append("mentee readiness low — expect a lot of unscheduled onboarding work")
    if energy_fit < 0.35:
        notes.append("mentor's current bandwidth/energy is low — risk of drift")
    if not notes:
        notes.append("mentor gains enough to engage — balanced relationship")
    return DirectedScore(value=max(0.0, min(1.0, value)), components=components, notes=notes)


# ─── Pair score (combines both directions) ──────────────────────────────

@dataclass
class PairScore:
    mentor_to_mentee: float
    mentee_to_mentor: float
    balanced: float                         # symmetric harmonic-ish combo
    min_side: float                         # min of the two (the weakest direction)
    viable: bool                            # both sides above 0.4
    mentor_notes: list[str]
    mentee_notes: list[str]


def pair_score(mentor: Mentor, mentee: Mentee) -> PairScore:
    m2e = score_mentor_to_mentee(mentor, mentee)
    e2m = score_mentee_to_mentor(mentee, mentor)
    # Harmonic-style combo: a very bad side drags the overall down
    prod = m2e.value * e2m.value
    bal = 2 * prod / (m2e.value + e2m.value) if (m2e.value + e2m.value) else 0.0
    return PairScore(
        mentor_to_mentee=round(m2e.value, 3),
        mentee_to_mentor=round(e2m.value, 3),
        balanced=round(bal, 3),
        min_side=round(min(m2e.value, e2m.value), 3),
        viable=(m2e.value > 0.4 and e2m.value > 0.4),
        mentor_notes=m2e.notes,
        mentee_notes=e2m.notes,
    )


# ─── Pool optimization ──────────────────────────────────────────────────

def optimize_pool(
    mentors: list[Mentor],
    mentees: list[Mentee],
) -> list[tuple[Mentor, Mentee, PairScore]]:
    """Greedy assignment. Sort all (mentor, mentee) pairs by `balanced`
    descending; assign in order as long as the mentor has capacity left.
    Skip non-viable pairs entirely."""
    scored: list[tuple[float, Mentor, Mentee, PairScore]] = []
    for m in mentors:
        for e in mentees:
            s = pair_score(m, e)
            if s.viable:
                scored.append((s.balanced, m, e, s))
    scored.sort(key=lambda x: -x[0])

    load: dict[str, int] = {}
    used_mentees: set[str] = set()
    assignments: list[tuple[Mentor, Mentee, PairScore]] = []
    for _, m, e, s in scored:
        if e.id in used_mentees:
            continue
        if load.get(m.id, 0) >= m.max_mentees:
            continue
        load[m.id] = load.get(m.id, 0) + 1
        used_mentees.add(e.id)
        assignments.append((m, e, s))
    return assignments


# ─── Simulated pools ────────────────────────────────────────────────────

_MENTOR_NAMES = ["Priya", "Wen", "Sofía", "Ade", "Noor", "Mikkel", "Kenji", "Rhea"]
_MENTEE_NAMES = ["Ari", "Jo", "Tali", "Max", "Yui", "Dev", "Nia", "Sam",
                 "Rin", "Ezra", "Kaia", "Ode"]


def simulate_mentors(seed: int = 21) -> list[Mentor]:
    rng = random.Random(seed)
    out = []
    for i, name in enumerate(_MENTOR_NAMES):
        stage = rng.choice(["senior", "staff", "principal", "exec"])
        focus = {k: round(rng.random() * 0.4, 3) for k in FOCUS_AREAS}
        # Emphasize 2 specialties
        for k in rng.sample(FOCUS_AREAS, 2):
            focus[k] = round(0.7 + rng.random() * 0.3, 3)
        out.append(Mentor(
            id=f"mentor-{i:02d}", name=name, stage=stage, focus=focus,
            teach_style=round(rng.random(), 3),
            max_mentees=rng.choice([2, 3, 3, 4]),
            energy=round(0.4 + rng.random() * 0.6, 3),
            min_stage_gap=rng.choice([2, 2, 3]),
        ))
    return out


def simulate_mentees(seed: int = 31) -> list[Mentee]:
    rng = random.Random(seed)
    out = []
    for i, name in enumerate(_MENTEE_NAMES):
        stage = rng.choice(["intern", "junior", "mid", "senior"])
        focus = {k: round(rng.random() * 0.3, 3) for k in FOCUS_AREAS}
        for k in rng.sample(FOCUS_AREAS, 2):
            focus[k] = round(0.6 + rng.random() * 0.4, 3)
        out.append(Mentee(
            id=f"mentee-{i:02d}", name=name, stage=stage, focus=focus,
            learn_style=round(rng.random(), 3),
            readiness=round(0.3 + rng.random() * 0.7, 3),
            cadence_wanted=round(rng.random(), 3),
        ))
    return out
