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


# ── Crisis guard ─────────────────────────────────────────────────────────
# A fixed phrase list, matched case-insensitively on word boundaries. It does
# not read context and does not score risk. Negated ("I'm not suicidal") and
# quoted ("she said 'I want to die'") phrases are flagged too, because the demo
# cannot tell them apart and flagging is the safe error. Idioms that contain a
# listed phrase ("cut myself some slack", "I'd rather die than...") are flagged
# as well. Crisis wording that is not on the list is missed.
CRISIS_HEADLINE = "Possible crisis language detected. This demo cannot assess risk."
CRISIS_ADVICE = (
    "If you or someone else may be in danger, contact local emergency services "
    "or a crisis line (in the US, call or text 988)."
)
CRISIS_MESSAGE = f"{CRISIS_HEADLINE} {CRISIS_ADVICE}"
NOT_ASSESSED = "not assessed"

_SELF = "(?:myself|yourself|himself|herself|themselves|themself|ourselves|oneself)"
_KIN = (
    "(?:wife|husband|partner|spouse|boyfriend|girlfriend|ex|mom|mother|dad|father|parents?"
    "|son|daughter|kids?|child|children|baby|babies|brother|sister|siblings?|family"
    "|boss|manager|coworkers?|co-workers?|colleagues?|neighbou?rs?|roommates?|teacher|friends?)"
)
_OTHERS = (
    "(?:him|her|them|you|someone|somebody|anyone|anybody|everyone|everybody|people|others"
    f"|other people|(?:my|his|her|their|your|the|that|this) {_KIN})"
)
_LETHAL = "(?:kill|murder|stab|shoot|strangle|choke)"
_LETHAL_ANY = (
    "(?:kill|kills|killed|killing|murder|murders|murdered|murdering|stab|stabs|stabbed|stabbing"
    "|shoot|shoots|shot|shooting|strangle|strangles|strangled|strangling|choke|chokes|choked|choking)"
)
_SELF_HARM_VERB = (
    "(?:kill|kills|killed|killing|hurt|hurts|hurting|harm|harms|harmed|harming|cut|cuts|cutting"
    "|burn|burns|burned|burnt|burning|hang|hangs|hanged|hung|hanging|shoot|shoots|shot|shooting"
    "|stab|stabs|stabbed|stabbing|poison|poisons|poisoned|poisoning|strangle|strangles|strangled"
    "|strangling|choke|chokes|choked|choking|starve|starves|starved|starving|injure|injures"
    "|injured|injuring|mutilate|mutilates|mutilated|mutilating|hit|hits|hitting|drown|drowns"
    "|drowned|drowning|suffocate|suffocates|suffocated|suffocating)"
)
_WHO = "(?:i|he|she|they|you)"
_PLACE = "(?:school|office|workplace|church|mall|store|party|class|building)"

# One space in a phrase matches any run of whitespace, line breaks included.
_CRISIS_PHRASES = (
    # Suicide, ideation or intent
    r"suicid\w*",
    r"unalive\w*",
    "kms",
    "kys",
    f"(?:kill|kills|killed|killing) {_SELF}",
    "(?:end|ends|ended|ending|take|takes|took|taking) (?:my|his|her|their|your|our|one's) (?:own )?(?:life|lives)",
    "(?:end|ends|ended|ending) it all",
    "(?:want|wants|wanted|wanting) to (?:just |really )?(?:die|be dead)",
    "wanna (?:just |really )?(?:die|be dead)",
    "(?:don'?t|do not|doesn'?t|does not|didn'?t|did not|no longer) (?:want|wants|wanted) to"
    r" (?:live|be alive|exist|wake up|go on living|keep living|be here any\s*more|be around any\s*more)",
    "(?:want|wants|wanted|wanting) (?:it|this|everything) (?:all )?to end",
    "(?:want|wants|wanted|wanting) to (?:go to )?sleep forever",
    "(?:won'?t|will not) be (?:around|here) (?:much longer|for long)",
    r"(?:won'?t|will not) be a burden (?:much longer|for long|any\s*more)",
    f"wish(?:es|ed|ing)? {_WHO} (?:was|were) (?:dead|never born|not alive)",
    f"wish(?:es|ed|ing)? {_WHO} (?:wasn'?t|weren'?t) alive",
    f"wish(?:es|ed|ing)? {_WHO}(?: could| would|'?d) (?:just )?die",
    f"wish(?:es|ed|ing)? {_WHO}(?: had|'?d) never been born",
    f"wish(?:es|ed|ing)? {_WHO} (?:didn'?t|did not) exist",
    "rather (?:be dead|die)",
    "(?:sleep|asleep) and (?:never|not) wake up",
    "no reason to (?:live|go on|keep going|keep living|be alive|stay alive)",
    "nothing (?:left )?to live for",
    "no point (?:in )?(?:living|being alive|going on)",
    "(?:not|isn'?t|wasn'?t|ain'?t|never) worth living",
    "(?:no|lost (?:the|my|his|her|their)) will to live",
    r"(?:can'?t|cannot|can not) go on (?:any\s*more|living|like this)",
    "(?:tired|sick|weary) of (?:living|being alive|life)",
    "done (?:with life|with living|living)",
    "better off (?:dead|without me)",
    f"better off if {_WHO} (?:was|were) (?:dead|gone)",
    f"better off if {_WHO} (?:died|disappeared)",
    f"better off if {_WHO} (?:wasn'?t|weren'?t|was not|were not) (?:here|around|alive)",
    "(?:thoughts?|thinking|thought) (?:of|about) (?:death|dying|being dead|ending it)",
    "overdos(?:e|es|ed|ing)",
    "jump(?:s|ed|ing)? (?:off|from) (?:a |the |my |this |that )?(?:bridge|building|roof|rooftop|cliff|ledge|balcony|overpass)",
    "(?:slit|slits|slitting|slash|slashes|slashed|slashing|cut|cuts|cutting) (?:my|his|her|their|your) wrists?",
    "gun to (?:my|his|her|their) head",
    "blow(?:s|ing)? (?:my|his|her|their) brains? out",
    # Clinical shorthand: SI = suicidal ideation, HI = homicidal ideation
    r"(?:si|hi)\s*/\s*(?:si|hi)",
    "(?:passive|active|denies|denied|denying|endorses|endorsed|endorsing|reports|reported|reporting"
    "|admits|admitted|hx of|history of) (?:si|hi)",
    r"si (?:with|without|w/o|w/)\s*(?:a )?(?:plan|intent)",
    "nssi",
    # Self-harm ("burned myself out" is burnout, not a burn)
    f"{_SELF_HARM_VERB} {_SELF}(?! out\\b)",
    "self(?:-| )?(?:harm|harms|harmed|harming|injury|injuries|injurious|injure|injuring"
    "|mutilation|mutilate|mutilating|mutilated)",
    # Harm to others
    r"homicid\w*",
    "murder(?:s|ed|er|ers|ing|ous)?",
    f"{_LETHAL_ANY} {_OTHERS}",
    f"(?:hurt|hurts|hurting|harm|harms|harmed|harming|attack|attacks|attacked|attacking)"
    f" (?:someone|somebody|anyone|anybody|everyone|everybody|people|others|other people|a child|children|kids"
    f"|(?:my|the|a|his|her|their) (?:baby|babies|kids?|child|children|son|daughter))",
    f"(?:want(?:s|ed|ing)? to|wanna|going to|gonna|plan(?:s|ned|ning)? to|intend(?:s|ed|ing)? to|urges? to"
    f"|tempted to|threat(?:en|ens|ened|ening) to) (?:{_LETHAL}|hurt|harm|attack|beat up) {_OTHERS}",
    f"(?:thoughts?|thinking|thought|urges?|images?|fantasies|fantasi[sz](?:e|es|ed|ing)) (?:of|about)"
    f" (?:killing|murdering|stabbing|shooting|strangling|choking|hurting|harming|attacking) {_OTHERS}",
    f"beat(?:s|en|ing)? (?:up {_OTHERS}|{_OTHERS} up)",
    f"(?:shoot|shoots|shooting|blow|blows|blowing) up (?:a|the|my|this|that) {_PLACE}",
    "violent (?:thoughts|urges|fantasies|impulses|ideation)",
)
_CRISIS = re.compile(
    r"\b(?:" + "|".join(p.replace(" ", r"\s+") for p in _CRISIS_PHRASES) + r")\b",
    re.IGNORECASE,
)
# Curly apostrophes and dashes, so "don’t" and "self–harm" match too.
_PUNCT = str.maketrans({"’": "'", "‘": "'", "ʼ": "'", "‐": "-", "‑": "-",
                        "‒": "-", "–": "-", "—": "-"})


def crisis_matches(text: str) -> list[str]:
    """Crisis phrases found in the text: lowercased, in order, without repeats."""
    found: list[str] = []
    for m in _CRISIS.finditer(text.translate(_PUNCT)):
        phrase = " ".join(m.group(0).lower().split())
        if phrase not in found:
            found.append(phrase)
    return found


def analyze_session(text: str) -> dict[str, Any]:
    """Map a session note / transcript to the cognitive state space.

    If the note contains crisis language, nothing in the result may read as
    reassurance: a `crisis` notice comes first, it replaces every alert, and
    quadrant and risk read "not assessed". The axis numbers stay, but they are
    keyword counts, not an assessment. A note without crisis language gets
    exactly the result it got before the guard existed.
    """
    state = CognitiveState(
        novelty=_count_ratio(text, _NOVELTY_HIGH, _NOVELTY_LOW),
        coherence=_count_ratio(text, _COHERENCE_HIGH, _COHERENCE_LOW),
        bandwidth=_count_ratio(text, _BANDWIDTH_HIGH, _BANDWIDTH_LOW),
        valence=_valence_ratio(text),
    )
    alerts = assess_alerts(state)
    result = {
        "state": state.as_dict(),
        "alerts": [{"level": a.level, "message": a.message, "recommendation": a.recommendation} for a in alerts],
    }
    matches = crisis_matches(text)
    if not matches:
        return result
    result["state"].update(quadrant=NOT_ASSESSED, risk=NOT_ASSESSED)
    return {
        "crisis": {"detected": True, "message": CRISIS_MESSAGE, "matches": matches},
        "state": result["state"],
        "alerts": [{"level": "critical", "message": CRISIS_HEADLINE, "recommendation": CRISIS_ADVICE}],
    }


SAMPLE_NOTES = {
    "progress": "Patient reported a breakthrough insight about their relationship pattern. They connected childhood experiences to current behavior for the first time. Felt hopeful and energized. Clarity about next steps. Ready to try new approaches.",
    "crisis": "Patient presenting in acute distress. Racing thoughts, can't think clearly. Overwhelmed and exhausted. Feeling hopeless and afraid. Reports suicidal ideation without plan. Fragmented speech, disconnected affect.",
    "plateau": "Session felt flat. Patient repeating the same themes from last week. Nothing new emerging. Stuck in a circular pattern. Tired but not distressed. Going through the motions.",
    "integration": "Patient integrating last week's insight into daily life. Reports seeing the pattern in real-time at work. Makes sense now. Calm and focused. Grateful for the progress. Bandwidth feels restored after a good week of sleep.",
    "tilt": "Patient arrived agitated. Angry about a work conflict. Racing thoughts, scattered. Can't focus on the session topic. Shame about losing control. Overwhelmed by the intensity of the reaction.",
}
