"""Axona Learn — encoding strength measurement for education.

Tracks learning interactions (study, test, practice) and measures
encoding strength over time. Uses the haze primitive: each concept has
an opacity that decays; reinforcement boosts it. The system distinguishes
surface pattern-matching (passed the test, forgot next week) from deep
integration (can apply the concept in a new context months later).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Concept:
    """One concept the student is learning."""

    id: str
    name: str
    topic: str = ""
    # Haze-based encoding state
    opacity: float = 0.0
    last_interaction: float = 0.0
    study_count: int = 0
    test_pass_count: int = 0
    test_fail_count: int = 0
    application_count: int = 0  # used the concept in a new context
    half_life_hours: float = 48.0

    def effective_strength(self, at: float | None = None) -> float:
        now = at if at is not None else time.time()
        if self.last_interaction <= 0 or self.opacity <= 0:
            return 0.0
        hours = max(0.0, (now - self.last_interaction) / 3600)
        return max(0.0, self.opacity * (0.5 ** (hours / self.half_life_hours)))

    def encoding_depth(self) -> str:
        s = self.effective_strength()
        if s > 0.8 and self.application_count > 0:
            return "deep"  # can apply in new contexts
        elif s > 0.6:
            return "integrated"  # solid but not yet generalized
        elif s > 0.3:
            return "surface"  # can recall, will forget
        elif self.study_count > 0:
            return "fading"
        return "unseen"

    def study(self) -> None:
        now = time.time()
        boost = 0.25 * (1 / (1 + self.study_count * 0.15))
        self.opacity = min(1.0, self.effective_strength(now) + boost)
        self.last_interaction = now
        self.study_count += 1
        self.half_life_hours = min(720, self.half_life_hours * 1.15)

    def test_pass(self) -> None:
        now = time.time()
        self.opacity = min(1.0, self.effective_strength(now) + 0.2)
        self.last_interaction = now
        self.test_pass_count += 1
        self.half_life_hours = min(720, self.half_life_hours * 1.4)

    def test_fail(self) -> None:
        now = time.time()
        self.opacity = max(0.1, self.effective_strength(now) * 0.5)
        self.last_interaction = now
        self.test_fail_count += 1
        self.half_life_hours = max(8, self.half_life_hours * 0.5)

    def apply(self) -> None:
        now = time.time()
        self.opacity = min(1.0, self.effective_strength(now) + 0.3)
        self.last_interaction = now
        self.application_count += 1
        self.half_life_hours = min(720, self.half_life_hours * 1.6)


@dataclass
class StudentProfile:
    concepts: dict[str, Concept] = field(default_factory=dict)

    def add_concept(self, c: Concept) -> None:
        self.concepts[c.id] = c

    def stats(self) -> dict[str, Any]:
        depths = {"deep": 0, "integrated": 0, "surface": 0, "fading": 0, "unseen": 0}
        for c in self.concepts.values():
            depths[c.encoding_depth()] += 1
        avg = sum(c.effective_strength() for c in self.concepts.values()) / max(1, len(self.concepts))
        return {
            "total_concepts": len(self.concepts),
            "depths": depths,
            "avg_strength": round(avg, 4),
        }

    def weakest(self, k: int = 5) -> list[Concept]:
        seen = [c for c in self.concepts.values() if c.study_count > 0]
        seen.sort(key=lambda c: c.effective_strength())
        return seen[:k]


SAMPLE_CONCEPTS = [
    Concept(id="c01", name="Photosynthesis", topic="Biology"),
    Concept(id="c02", name="Mitosis", topic="Biology"),
    Concept(id="c03", name="Pythagorean theorem", topic="Math"),
    Concept(id="c04", name="Quadratic formula", topic="Math"),
    Concept(id="c05", name="Newton's 2nd law", topic="Physics"),
    Concept(id="c06", name="Ohm's law", topic="Physics"),
    Concept(id="c07", name="Supply and demand", topic="Economics"),
    Concept(id="c08", name="Opportunity cost", topic="Economics"),
    Concept(id="c09", name="Conditional probability", topic="Statistics"),
    Concept(id="c10", name="Central limit theorem", topic="Statistics"),
]


def make_student() -> StudentProfile:
    sp = StudentProfile()
    for c in SAMPLE_CONCEPTS:
        sp.add_concept(Concept(id=c.id, name=c.name, topic=c.topic))
    return sp
