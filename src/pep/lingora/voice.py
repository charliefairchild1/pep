"""Lingora Voice — voice-aware writing analysis engine.

Scores a paragraph on eight mechanisms that define writing voice.
Generates voice-PRESERVING suggestions (not "fix your grammar") that
align with the writer's existing intent.

The key difference from Grammarly: Grammarly treats every deviation
as a bug. Lingora Voice treats every deviation as a possible stylistic
choice and only suggests changes that strengthen the existing voice.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class MechanismScore:
    """Score on one voice mechanism."""

    name: str
    value: float  # [0, 1]
    description: str


@dataclass
class VoiceDiagnostic:
    """One voice-preserving suggestion."""

    mechanism: str
    suggestion: str
    priority: str  # "high" / "medium" / "low"


@dataclass
class VoiceReport:
    text: str
    total_words: int
    total_sentences: int
    mechanisms: list[MechanismScore]
    voice_signature: str  # one-line label for the detected voice
    diagnostics: list[VoiceDiagnostic]
    overall_voice_strength: float  # [0, 1]


# ── Mechanism scorers ───────────────────────────────────────────────────

_SENTENCE_RE = re.compile(r"[.!?]+")
_WORD_RE = re.compile(r"\b\w+\b")


def _pov_score(text: str) -> tuple[float, str]:
    lower = text.lower()
    first = len(re.findall(r"\b(i|me|my|mine|we|us|our)\b", lower))
    second = len(re.findall(r"\b(you|your|yours)\b", lower))
    third = len(re.findall(r"\b(he|she|they|it|his|her|their|its|him|them)\b", lower))
    total = max(1, first + second + third)
    if first / total > 0.6:
        return 0.8, "first-person dominant"
    elif second / total > 0.5:
        return 0.7, "second-person (addressing reader)"
    elif third / total > 0.5:
        return 0.75, "third-person narrative"
    return 0.5, "mixed/neutral POV"


def _register_score(text: str) -> tuple[float, str]:
    lower = text.lower()
    formal = len(re.findall(r"\b(furthermore|nevertheless|hereby|shall|whom|thus|therefore|consequently)\b", lower))
    casual = len(re.findall(r"\b(gonna|wanna|kinda|yeah|nah|stuff|thing|cool|awesome|like)\b", lower))
    contractions = len(re.findall(r"\w+n't|\w+'re|\w+'ve|\w+'ll|\w+'d|\w+'s", lower))
    if formal > 2:
        return 0.85, "formal/academic"
    elif casual > 2 or contractions > 3:
        return 0.80, "casual/conversational"
    return 0.6, "neutral register"


def _irony_score(text: str) -> tuple[float, str]:
    lower = text.lower()
    markers = len(re.findall(r"\b(obviously|clearly|of course|surely|naturally|apparently|supposedly)\b", lower))
    scare_quotes = text.count('"') // 2
    ellipsis = text.count("...")
    score = min(1.0, (markers * 0.25 + scare_quotes * 0.2 + ellipsis * 0.15))
    if score > 0.5:
        return score, "ironic/sarcastic undertone"
    return score, "minimal irony"


def _subtext_score(text: str) -> tuple[float, str]:
    lower = text.lower()
    hedges = len(re.findall(r"\b(perhaps|maybe|might|seems?|appear|could|rather|somewhat|quite)\b", lower))
    implication = len(re.findall(r"\b(after all|you know|one might|let's just say|if you know what)\b", lower))
    score = min(1.0, hedges * 0.12 + implication * 0.3)
    if score > 0.4:
        return score, "significant subtext / indirectness"
    return max(0.1, score), "direct/on-the-surface"


def _pacing_score(text: str) -> tuple[float, str]:
    sentences = [s.strip() for s in _SENTENCE_RE.split(text) if s.strip()]
    if not sentences:
        return 0.5, "no sentences detected"
    lengths = [len(_WORD_RE.findall(s)) for s in sentences]
    if not lengths:
        return 0.5, "no words detected"
    avg = sum(lengths) / len(lengths)
    variance = sum((l - avg) ** 2 for l in lengths) / max(1, len(lengths))
    std = math.sqrt(variance)
    # High variance = varied pacing (stylistically strong)
    # Low variance + short = clipped
    # Low variance + long = monotonous
    if std > 5 and avg > 8:
        return 0.9, "varied pacing (strong rhythm)"
    elif avg < 8:
        return 0.85, "clipped/punchy (short sentences)"
    elif std < 2 and avg > 15:
        return 0.4, "monotonous (similar-length long sentences)"
    return 0.65, "moderate pacing"


def _voice_consistency(text: str) -> tuple[float, str]:
    sentences = [s.strip() for s in _SENTENCE_RE.split(text) if s.strip()]
    if len(sentences) < 2:
        return 0.7, "too short to assess consistency"
    # Check if register stays consistent across sentences
    formal_count = 0
    casual_count = 0
    for s in sentences:
        lower = s.lower()
        if re.search(r"\b(furthermore|nevertheless|thus|therefore)\b", lower):
            formal_count += 1
        if re.search(r"\b(gonna|wanna|kinda|yeah|cool|like)\b", lower):
            casual_count += 1
    if formal_count > 0 and casual_count > 0:
        return 0.35, "register inconsistency (formal + casual mixed)"
    return 0.85, "consistent voice throughout"


def _repetition_score(text: str) -> tuple[float, str]:
    words = _WORD_RE.findall(text.lower())
    stopwords = {"the", "a", "an", "is", "was", "are", "were", "be", "been",
                 "being", "have", "has", "had", "do", "does", "did", "will",
                 "would", "could", "should", "may", "might", "can", "shall",
                 "to", "of", "in", "for", "on", "with", "at", "by", "from",
                 "as", "into", "through", "during", "before", "after", "and",
                 "but", "or", "nor", "not", "so", "yet", "both", "either",
                 "neither", "each", "every", "all", "any", "few", "more",
                 "most", "other", "some", "such", "no", "only", "own",
                 "same", "than", "too", "very", "just", "that", "this",
                 "it", "its", "i", "me", "my", "he", "she", "they", "we",
                 "you", "his", "her", "their", "our", "your"}
    content = [w for w in words if w not in stopwords and len(w) > 2]
    if not content:
        return 0.3, "no significant content words"
    counts = Counter(content)
    repeated = sum(1 for w, c in counts.items() if c >= 3)
    total_unique = len(counts)
    ratio = repeated / max(1, total_unique)
    if ratio > 0.15:
        return 0.8, "deliberate repetition pattern"
    elif ratio > 0.05:
        return 0.5, "moderate repetition"
    return 0.2, "minimal repetition"


def _sound_score(text: str) -> tuple[float, str]:
    words = _WORD_RE.findall(text.lower())
    if len(words) < 4:
        return 0.3, "too short for sound analysis"
    # Check for alliteration (consecutive words starting with same letter)
    alliterations = 0
    for i in range(len(words) - 1):
        if words[i][0] == words[i + 1][0] and words[i][0].isalpha():
            alliterations += 1
    # Check for assonance (repeated vowel sounds in nearby words)
    vowel_patterns = [re.findall(r"[aeiou]+", w) for w in words]
    alliteration_rate = alliterations / max(1, len(words) - 1)
    if alliteration_rate > 0.15:
        return 0.8, "notable sound patterning (alliteration)"
    elif alliteration_rate > 0.08:
        return 0.5, "moderate sound awareness"
    return 0.2, "no notable sound patterning"


MECHANISMS = [
    ("pov", _pov_score),
    ("register", _register_score),
    ("irony", _irony_score),
    ("subtext", _subtext_score),
    ("pacing", _pacing_score),
    ("voice_consistency", _voice_consistency),
    ("repetition", _repetition_score),
    ("sound_symmetry", _sound_score),
]


# ── Voice signature detection ───────────────────────────────────────────

def _detect_signature(mechanisms: list[MechanismScore]) -> str:
    by_name = {m.name: m.value for m in mechanisms}
    pacing = by_name.get("pacing", 0.5)
    irony = by_name.get("irony", 0)
    subtext = by_name.get("subtext", 0)
    register = by_name.get("register", 0.5)
    repetition = by_name.get("repetition", 0.3)

    if pacing > 0.8 and subtext < 0.3 and register > 0.7:
        return "clipped declarative (Hemingway-like)"
    if pacing < 0.5 and repetition > 0.6:
        return "rhythmic/incantatory (Faulkner-like)"
    if irony > 0.5:
        return "ironic/sardonic"
    if subtext > 0.5:
        return "indirect/implicature-heavy"
    if register > 0.8:
        return "formal/academic"
    if register < 0.4:
        return "casual/conversational"
    return "moderate/neutral voice"


# ── Diagnostics ─────────────────────────────────────────────────────────

def _generate_diagnostics(mechanisms: list[MechanismScore]) -> list[VoiceDiagnostic]:
    out: list[VoiceDiagnostic] = []
    by_name = {m.name: m for m in mechanisms}

    consistency = by_name.get("voice_consistency")
    if consistency and consistency.value < 0.5:
        out.append(VoiceDiagnostic(
            mechanism="voice_consistency",
            suggestion="Register shifts mid-text. If intentional (code-switching), it's a feature; if accidental, pick one register and hold it.",
            priority="high",
        ))

    pacing = by_name.get("pacing")
    if pacing and "monotonous" in pacing.description:
        out.append(VoiceDiagnostic(
            mechanism="pacing",
            suggestion="Sentence lengths are uniform. Varying short and long sentences creates rhythm and emphasis.",
            priority="medium",
        ))

    subtext = by_name.get("subtext")
    if subtext and subtext.value > 0.6:
        out.append(VoiceDiagnostic(
            mechanism="subtext",
            suggestion="Heavy indirectness — effective if the audience can read it, but risky if clarity matters. Consider making one key point explicit as an anchor.",
            priority="low",
        ))

    irony = by_name.get("irony")
    if irony and irony.value > 0.6:
        out.append(VoiceDiagnostic(
            mechanism="irony",
            suggestion="Strong ironic undertone. Works well for opinion/essay; may misfire in instructional or cross-cultural contexts.",
            priority="low",
        ))

    repetition = by_name.get("repetition")
    if repetition and repetition.value > 0.7:
        out.append(VoiceDiagnostic(
            mechanism="repetition",
            suggestion="Deliberate repetition detected. If it's serving emphasis or rhythm, leave it. If it's accidental, vary the vocabulary.",
            priority="low",
        ))

    if not out:
        out.append(VoiceDiagnostic(
            mechanism="overall",
            suggestion="Voice is consistent and functional. No changes needed to preserve the current style.",
            priority="low",
        ))

    return out


# ── Public API ──────────────────────────────────────────────────────────

def analyze_voice(text: str) -> VoiceReport:
    """Run all eight mechanism scorers + diagnostics."""
    words = _WORD_RE.findall(text)
    sentences = [s.strip() for s in _SENTENCE_RE.split(text) if s.strip()]

    mechanisms: list[MechanismScore] = []
    for name, fn in MECHANISMS:
        value, desc = fn(text)
        mechanisms.append(MechanismScore(name=name, value=round(value, 4), description=desc))

    signature = _detect_signature(mechanisms)
    diagnostics = _generate_diagnostics(mechanisms)
    overall = sum(m.value for m in mechanisms) / max(1, len(mechanisms))

    return VoiceReport(
        text=text,
        total_words=len(words),
        total_sentences=len(sentences),
        mechanisms=mechanisms,
        voice_signature=signature,
        diagnostics=diagnostics,
        overall_voice_strength=round(overall, 4),
    )
