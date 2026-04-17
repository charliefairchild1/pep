"""Lingora Learn — constellation-based language learning engine.

Teaches words via context and association, not flashcard drilling. A word
is a node in a semantic constellation; learning means building the
constellation, not memorizing a definition.

Uses PEP's haze primitive for spaced repetition: each word has an opacity
that decays over time; reinforcement (successful recall) boosts it.
The learning schedule is personalized per-word, not population-averaged.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class WordNode:
    """One word in the learner's constellation."""

    word: str
    definition: str
    contexts: list[str] = field(default_factory=list)  # example sentences
    associations: list[str] = field(default_factory=list)  # related words
    # Haze-based learning state
    opacity: float = 0.0  # 0 = never seen, 1 = fully acquired
    last_seen: float = 0.0  # timestamp
    times_seen: int = 0
    times_recalled: int = 0
    half_life_hours: float = 24.0  # personalized per word

    def effective_strength(self, at: float | None = None) -> float:
        now = at if at is not None else time.time()
        if self.last_seen <= 0 or self.opacity <= 0:
            return 0.0
        hours = max(0.0, (now - self.last_seen) / 3600)
        return max(0.0, self.opacity * (0.5 ** (hours / self.half_life_hours)))

    def study(self, at: float | None = None) -> None:
        now = at if at is not None else time.time()
        # Boost opacity on study; diminishing returns
        boost = 0.3 * (1.0 / (1 + self.times_seen * 0.2))
        current = self.effective_strength(now)
        self.opacity = min(1.0, current + boost)
        self.last_seen = now
        self.times_seen += 1
        # Extend half-life with successful study (spaced repetition effect)
        self.half_life_hours = min(720, self.half_life_hours * 1.3)

    def recall_success(self, at: float | None = None) -> None:
        now = at if at is not None else time.time()
        self.times_recalled += 1
        self.opacity = min(1.0, self.effective_strength(now) + 0.15)
        self.last_seen = now
        self.half_life_hours = min(720, self.half_life_hours * 1.5)

    def recall_failure(self, at: float | None = None) -> None:
        now = at if at is not None else time.time()
        current = self.effective_strength(now)
        self.opacity = max(0.1, current * 0.6)
        self.last_seen = now
        self.half_life_hours = max(4, self.half_life_hours * 0.5)

    @property
    def acquisition_depth(self) -> str:
        strength = self.effective_strength()
        if strength > 0.8:
            return "deep"
        elif strength > 0.5:
            return "moderate"
        elif strength > 0.2:
            return "shallow"
        elif self.times_seen > 0:
            return "fading"
        return "unseen"


@dataclass
class StudySession:
    """Result of one study event."""

    word: str
    action: str  # "study" / "recall_success" / "recall_failure"
    strength_before: float
    strength_after: float
    half_life_before: float
    half_life_after: float
    depth: str


@dataclass
class LearnerProfile:
    """Tracks all words the learner is working on."""

    words: dict[str, WordNode] = field(default_factory=dict)
    session_history: list[StudySession] = field(default_factory=list)

    def add_word(self, node: WordNode) -> None:
        self.words[node.word] = node

    def study_word(self, word: str) -> StudySession | None:
        node = self.words.get(word)
        if node is None:
            return None
        before = node.effective_strength()
        hl_before = node.half_life_hours
        node.study()
        after = node.effective_strength()
        sess = StudySession(
            word=word, action="study",
            strength_before=round(before, 4), strength_after=round(after, 4),
            half_life_before=round(hl_before, 2), half_life_after=round(node.half_life_hours, 2),
            depth=node.acquisition_depth,
        )
        self.session_history.append(sess)
        return sess

    def recall(self, word: str, success: bool) -> StudySession | None:
        node = self.words.get(word)
        if node is None:
            return None
        before = node.effective_strength()
        hl_before = node.half_life_hours
        if success:
            node.recall_success()
        else:
            node.recall_failure()
        after = node.effective_strength()
        sess = StudySession(
            word=word, action="recall_success" if success else "recall_failure",
            strength_before=round(before, 4), strength_after=round(after, 4),
            half_life_before=round(hl_before, 2), half_life_after=round(node.half_life_hours, 2),
            depth=node.acquisition_depth,
        )
        self.session_history.append(sess)
        return sess

    def next_review(self, k: int = 5) -> list[WordNode]:
        """Return the k words most in need of review (lowest effective
        strength among words that have been seen at least once)."""
        seen = [n for n in self.words.values() if n.times_seen > 0]
        seen.sort(key=lambda n: n.effective_strength())
        return seen[:k]

    def stats(self) -> dict[str, Any]:
        words = list(self.words.values())
        depths = {"deep": 0, "moderate": 0, "shallow": 0, "fading": 0, "unseen": 0}
        for w in words:
            depths[w.acquisition_depth] += 1
        avg_strength = sum(w.effective_strength() for w in words) / max(1, len(words))
        return {
            "total_words": len(words),
            "depths": depths,
            "avg_strength": round(avg_strength, 4),
            "total_study_events": len(self.session_history),
        }


# ── Sample vocabulary ───────────────────────────────────────────────────

SAMPLE_VOCABULARY: list[WordNode] = [
    WordNode(word="saudade", definition="a bittersweet longing for something absent and beloved",
             contexts=["She felt a deep saudade for the summers of her childhood.", "The fado singer's voice was full of saudade."],
             associations=["nostalgia", "melancholy", "yearning", "longing"]),
    WordNode(word="schadenfreude", definition="pleasure derived from another's misfortune",
             contexts=["He couldn't suppress a hint of schadenfreude when his rival's project failed.", "The schadenfreude was palpable in the office."],
             associations=["gloating", "spite", "satisfaction", "malice"]),
    WordNode(word="hygge", definition="a quality of coziness that contributes to contentment and well-being",
             contexts=["The candles and blankets created a perfect hygge atmosphere.", "Winter in Copenhagen revolves around hygge."],
             associations=["cozy", "warmth", "comfort", "contentment"]),
    WordNode(word="wabi-sabi", definition="the beauty of imperfection and transience",
             contexts=["The cracked teacup embodied wabi-sabi.", "She found wabi-sabi in the weathered garden wall."],
             associations=["imperfection", "transience", "simplicity", "acceptance"]),
    WordNode(word="ubuntu", definition="I am because we are — shared humanity and interconnectedness",
             contexts=["Ubuntu philosophy shaped the community's response to the crisis.", "The concept of ubuntu is central to South African ethics."],
             associations=["community", "humanity", "interdependence", "compassion"]),
    WordNode(word="ikigai", definition="a reason for being — the intersection of passion, mission, vocation, and profession",
             contexts=["He found his ikigai in teaching mathematics to children.", "The Okinawan centenarians attribute their longevity to having ikigai."],
             associations=["purpose", "meaning", "fulfillment", "vocation"]),
    WordNode(word="tsundoku", definition="the habit of acquiring books but letting them pile up unread",
             contexts=["Her nightstand was a monument to tsundoku.", "The bookshop encouraged tsundoku with its irresistible displays."],
             associations=["books", "collecting", "reading", "procrastination"]),
    WordNode(word="komorebi", definition="sunlight filtering through tree leaves",
             contexts=["They picnicked under the gentle komorebi of the oak canopy.", "The photographer specialized in capturing komorebi."],
             associations=["light", "trees", "nature", "dappled", "forest"]),
    WordNode(word="fernweh", definition="an ache for distant places; the opposite of homesickness",
             contexts=["Scrolling through travel photos only deepened her fernweh.", "Fernweh struck him hardest in January."],
             associations=["wanderlust", "travel", "longing", "adventure"]),
    WordNode(word="meraki", definition="doing something with soul, creativity, or love — putting yourself into your work",
             contexts=["She cooked with meraki, tasting every ingredient.", "The mural was painted with obvious meraki."],
             associations=["passion", "craft", "devotion", "artistry"]),
]


def make_learner(vocabulary: list[WordNode] | None = None) -> LearnerProfile:
    """Create a learner with the sample vocabulary pre-loaded."""
    lp = LearnerProfile()
    for w in (vocabulary or SAMPLE_VOCABULARY):
        lp.add_word(WordNode(
            word=w.word, definition=w.definition,
            contexts=list(w.contexts), associations=list(w.associations),
        ))
    return lp
