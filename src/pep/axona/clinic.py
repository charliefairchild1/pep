"""Axona Clinic — session transcript → cognitive state mapping.

Takes clinical session keywords/descriptors and maps them to the
cognitive state space. Uses keyword detection to infer novelty,
coherence, bandwidth, and valence from clinical language.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .core import CognitiveState, StateAlert, assess_alerts, clamp01, clamp_valence


_NOVELTY_HIGH = re.compile(r"\b(insight|breakthrough|realization|surprise|new perspective|shift|aha|never thought|first time)\b", re.IGNORECASE)
_NOVELTY_LOW = re.compile(r"\b(stuck|same|loop|repeating|circular|nothing new|stagnant|flat)\b", re.IGNORECASE)

_COHERENCE_HIGH = re.compile(r"\b(makes sense|connected|integrated|clarity|understand|pattern|see how|linked|whole picture)\b", re.IGNORECASE)
_COHERENCE_LOW = re.compile(r"\b(confused|fragmented|scattered|disconnected|can't think|foggy|jumbled|racing|disorganized)\b", re.IGNORECASE)

_BANDWIDTH_HIGH = re.compile(r"\b(energized|clear|capable|sharp|focused|ready|alert|present)\b", re.IGNORECASE)
_BANDWIDTH_LOW = re.compile(r"\b(exhausted|depleted|tired|overwhelmed|can't cope|shutdown|burned out|numb|drained)\b", re.IGNORECASE)

_VALENCE_POS = re.compile(r"\b(hopeful|grateful|relieved|happy|proud|calm|peaceful|motivated|warm|safe|loved)\b", re.IGNORECASE)
_VALENCE_NEG = re.compile(r"\b(anxious|depressed|angry|afraid|hopeless|guilty|shame|panicking|worthless|empty|suicidal|grief|rage)\b", re.IGNORECASE)


def _count_ratio(text: str, high_re: re.Pattern, low_re: re.Pattern) -> float:
    """Return a value in [0, 1]. 0.5 = neutral; high matches push toward 1; low toward 0."""
    high = len(high_re.findall(text))
    low = len(low_re.findall(text))
    total = high + low
    if total == 0:
        return 0.5
    return clamp01(0.5 + (high - low) / (total * 2))


def _valence_ratio(text: str) -> float:
    pos = len(_VALENCE_POS.findall(text))
    neg = len(_VALENCE_NEG.findall(text))
    total = pos + neg
    if total == 0:
        return 0.0
    return clamp_valence((pos - neg) / total)


def analyze_session(text: str) -> dict[str, Any]:
    """Map a session note / transcript to the cognitive state space."""
    state = CognitiveState(
        novelty=_count_ratio(text, _NOVELTY_HIGH, _NOVELTY_LOW),
        coherence=_count_ratio(text, _COHERENCE_HIGH, _COHERENCE_LOW),
        bandwidth=_count_ratio(text, _BANDWIDTH_HIGH, _BANDWIDTH_LOW),
        valence=_valence_ratio(text),
    )
    alerts = assess_alerts(state)
    return {
        "state": state.as_dict(),
        "alerts": [{"level": a.level, "message": a.message, "recommendation": a.recommendation} for a in alerts],
    }


SAMPLE_NOTES = {
    "progress": "Patient reported a breakthrough insight about their relationship pattern. They connected childhood experiences to current behavior for the first time. Felt hopeful and energized. Clarity about next steps. Ready to try new approaches.",
    "crisis": "Patient presenting in acute distress. Racing thoughts, can't think clearly. Overwhelmed and exhausted. Feeling hopeless and afraid. Reports suicidal ideation without plan. Fragmented speech, disconnected affect.",
    "plateau": "Session felt flat. Patient repeating the same themes from last week. Nothing new emerging. Stuck in a circular pattern. Tired but not distressed. Going through the motions.",
    "integration": "Patient integrating last week's insight into daily life. Reports seeing the pattern in real-time at work. Makes sense now. Calm and focused. Grateful for the progress. Bandwidth feels restored after a good week of sleep.",
    "tilt": "Patient arrived agitated. Angry about a work conflict. Racing thoughts, scattered. Can't focus on the session topic. Shame about losing control. Overwhelmed by the intensity of the reaction.",
}
