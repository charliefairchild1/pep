"""Earnings-call pragmatic analysis — the Lingora × Strata cross-app wedge.

Executives are trained to mask pragmatic content. They say positive words,
but the pragmatic markers (hedge density, subject drop, register shifts,
deflection patterns, qualifier stacking) carry the real signal. The gap
between *stated sentiment* and *pragmatic sentiment* is alpha that
number-only signal engines (EPS beats, guide revisions) don't see.

This module:

    1. Scores any text excerpt on four axes — stated, hedge, evasion,
       register — and synthesizes a pragmatic sentiment and gap.

    2. Runs entirely on curated regex/lexicon heuristics. No LLM calls.
       No API keys. The production version would use Claude on each
       excerpt; the engine here proves the decomposition works.

    3. Interprets the gap as a trading signal: CONFIRM / WARNING / FADE.

The Strata canvas (`/strata#pragmatic-tab`) consumes this on a handful of
curated fictional excerpts showing canonical patterns: clean positive,
hedged positive, deflection, register-shift, passive-subject-drop, etc.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


# ─── Lexicons ───────────────────────────────────────────────────────────

_POSITIVE_WORDS = [
    "strong", "grew", "growth", "expanded", "expanding", "outperformed",
    "beat", "beats", "record", "momentum", "accelerated", "accelerating",
    "raised", "raising", "confident", "pleased", "robust", "healthy",
    "leading", "leadership", "advance", "improving", "improved", "reiterating",
    "encouraged", "encouraging",
]
_NEGATIVE_WORDS = [
    "declined", "decline", "weakness", "softer", "soft", "challenge",
    "challenges", "pressure", "pressured", "impacted", "headwinds",
    "miss", "missed", "disappointing", "writedown", "impairment",
    "restructuring", "layoffs", "reduction", "downward",
]
_HEDGE_MARKERS = [
    "we remain", "we continue to", "we believe", "to some extent",
    "broadly speaking", "directionally", "on balance", "on the whole",
    "taking a measured approach", "dynamic macro", "near-term",
    "certain", "some", "in certain regions", "in certain markets",
    "measured approach", "prudent", "in the context of",
    "over time", "over the long term", "long-term thesis",
    "it is fair to say", "it would be fair to say",
]
_DEFLECTION_MARKERS = [
    "great question", "i'd point you to", "i would point you to",
    "we're really focused on", "what we've been focused on",
    "the broader", "the bigger picture", "at a high level",
    "we'll talk more about", "we plan to address that at",
]
_PASSIVE_SUBJECT_DROP = [
    r"\bdecisions were made\b",
    r"\blessons have been learned\b",
    r"\bactions are being taken\b",
    r"\bmitigations are being implemented\b",
    r"\bsteps are being taken\b",
    r"\bprocesses were reviewed\b",
    r"\bit was determined\b",
    r"\bit has been determined\b",
]
_REGISTER_CASUAL = [
    r"\byeah\b", r"\byou know\b", r"\blook,?\b", r"\bfrankly\b",
    r"\bnot a big deal\b", r"\bat the end of the day\b",
    r"\bhonestly\b", r"\bkinda\b",
]
_REGISTER_FORMAL = [
    r"\bwith respect to\b", r"\bquantum of\b", r"\bas disclosed\b",
    r"\bas previously communicated\b", r"\bas referenced\b",
    r"\bin accordance with\b", r"\bpursuant to\b",
    r"\bon a constant-currency basis\b", r"\binvestment community\b",
]


# ─── Analysis ──────────────────────────────────────────────────────────

@dataclass
class PragmaticAnalysis:
    text: str
    stated_sentiment: float        # [-1, +1] from lexicon
    hedge_density: float           # [0, 1] fraction of hedge markers
    deflection_count: int
    passive_drop_count: int
    register_shift: float          # [0, 1] mismatch between expected and observed register
    pragmatic_sentiment: float     # [-1, +1] — what they really signaled
    gap: float                     # stated - pragmatic  (big positive = hiding something)
    signal: str                    # CONFIRM / WARNING / FADE / REINFORCE
    rationale: list[str]           # human-readable notes on which markers fired


def _lexicon_score(text: str) -> float:
    t = text.lower()
    pos = sum(1 for w in _POSITIVE_WORDS if re.search(rf"\b{re.escape(w)}\b", t))
    neg = sum(1 for w in _NEGATIVE_WORDS if re.search(rf"\b{re.escape(w)}\b", t))
    if pos + neg == 0:
        return 0.0
    raw = (pos - neg) / (pos + neg)
    # Damp: lexicon sentiment is noisy; cap contribution
    return max(-1.0, min(1.0, raw * 0.9))


def _count_markers(text: str, markers: list[str], regex: bool = False) -> int:
    t = text.lower()
    if regex:
        return sum(1 for m in markers if re.search(m, t))
    return sum(1 for m in markers if m in t)


def _word_count(text: str) -> int:
    return max(1, len(text.split()))


def _context_register(text: str) -> str:
    """Crude classifier: is the topic serious enough to require formal register?
    Uses the presence of words/phrases that signal a weighty subject."""
    t = text.lower()
    heavy = [
        "writedown", "impairment", "restructuring", "sec", "investigation",
        "litigation", "breach", "outage", "miss", "shortfall", "accelerated",
        "goodwill", "european operations", "layoffs", "reduction",
    ]
    return "heavy" if any(w in t for w in heavy) else "normal"


def analyze(text: str) -> PragmaticAnalysis:
    """Full pragmatic analysis of one excerpt."""
    wc = _word_count(text)
    stated = _lexicon_score(text)
    hedge_n = _count_markers(text, _HEDGE_MARKERS, regex=False)
    hedge_density = min(1.0, hedge_n / max(5.0, wc / 20.0))
    deflection_n = _count_markers(text, _DEFLECTION_MARKERS, regex=False)
    passive_n = _count_markers(text, _PASSIVE_SUBJECT_DROP, regex=True)
    casual_n = _count_markers(text, _REGISTER_CASUAL, regex=True)
    formal_n = _count_markers(text, _REGISTER_FORMAL, regex=True)
    ctx = _context_register(text)

    # Register shift: heavy topic + casual markers OR neutral topic + defensive formal
    if ctx == "heavy" and casual_n >= 1:
        register_shift = min(1.0, 0.4 + 0.2 * casual_n)
    elif ctx == "normal" and formal_n >= 2:
        register_shift = min(1.0, 0.3 + 0.15 * (formal_n - 1))
    else:
        register_shift = 0.0

    # Pragmatic sentiment: start from stated, then discount for every marker.
    pragmatic = stated
    pragmatic -= 0.45 * hedge_density          # hedging flattens positives
    pragmatic -= 0.20 * deflection_n           # deflection = something to hide
    pragmatic -= 0.20 * passive_n              # passive subject drop = distancing
    pragmatic -= 0.35 * register_shift         # register shift = mismatch with topic gravity
    pragmatic = max(-1.0, min(1.0, pragmatic))

    gap = stated - pragmatic                   # big positive = hiding bad news

    if abs(gap) < 0.15 and stated > 0.3:
        signal = "CONFIRM"
    elif abs(gap) < 0.15 and stated < -0.2:
        signal = "CONFIRM (bear)"
    elif abs(gap) < 0.1:
        signal = "NEUTRAL"
    elif gap > 0.5:
        signal = "STRONG FADE"
    elif gap > 0.25:
        signal = "FADE"
    elif gap > 0.1:
        signal = "WARNING"
    elif gap < -0.15:
        signal = "REINFORCE"                   # pragmatic more positive than stated (rare)
    else:
        signal = "NEUTRAL"

    rationale: list[str] = []
    if hedge_n:
        rationale.append(f"{hedge_n} hedging marker(s) — density {hedge_density:.2f}")
    if deflection_n:
        rationale.append(f"{deflection_n} deflection marker(s) — not answering the question asked")
    if passive_n:
        rationale.append(f"{passive_n} passive subject-drop — who did what is being hidden")
    if register_shift > 0:
        rationale.append(
            f"register shift ({ctx} topic, {'casual' if casual_n else 'formal'} tone) — "
            "{:.2f}".format(register_shift)
        )
    if not rationale:
        rationale.append("no significant pragmatic markers — stated sentiment likely reliable")

    return PragmaticAnalysis(
        text=text,
        stated_sentiment=round(stated, 3),
        hedge_density=round(hedge_density, 3),
        deflection_count=deflection_n,
        passive_drop_count=passive_n,
        register_shift=round(register_shift, 3),
        pragmatic_sentiment=round(pragmatic, 3),
        gap=round(gap, 3),
        signal=signal,
        rationale=rationale,
    )


def analyze_transcript(excerpts: list[str]) -> list[PragmaticAnalysis]:
    return [analyze(e) for e in excerpts]


# ─── Curated fictional transcript (no copyright risk) ───────────────────

SAMPLE_TRANSCRIPT = [
    # 0 — clean positive, stated matches pragmatic
    "Revenue came in at $420M, up 18% year-over-year, driven by strong growth "
    "in our Enterprise segment. Gross margin expanded 150 basis points. We're "
    "reiterating guidance for the full year and raising our share buyback "
    "authorization.",
    # 1 — hedged positive (evasive on weak quarter)
    "We're encouraged by the trajectory we're seeing, and while there have been "
    "some near-term headwinds in certain regions, we remain confident in the "
    "long-term thesis. We're taking a measured approach to guidance given the "
    "dynamic macro environment.",
    # 2 — deflection (refusing to answer a question)
    "That's a great question. What we've been really focused on is the broader "
    "platform story, and we're seeing tremendous engagement across all our key "
    "verticals. I'd point you to the disclosures in the 10-Q for the specific "
    "metrics.",
    # 3 — register shift (too casual for gravity)
    "Yeah, so, look — we took a look at the carrying value of the European "
    "operations and, you know, felt it was prudent to adjust. Honestly it's not "
    "a big deal in the context of the overall business.",
    # 4 — passive / subject drop (distancing from ownership)
    "Certain strategic decisions were made regarding the European operations "
    "that in hindsight could have been executed differently. Lessons have been "
    "learned, and mitigations are being implemented.",
    # 5 — CEO confidence (low qualifier density, crisp)
    "We grew. We shipped. We expanded. Three things happened this quarter, and "
    "they're all in the right direction.",
    # 6 — formal register + unusual specificity on a writedown (defensive CYA)
    "With respect to the accelerated amortization of the prior-period "
    "adjustment, and as disclosed on page 42 of the supplementary deck, the "
    "quantum of impact is within the range previously communicated to the "
    "investment community.",
]
