"""Axona Clinic crisis guard (docs/products/axona-claims.md, bug 3).

Before the guard, "suicidal" was one negative-valence word, so "suicidal but
grateful and hopeful" returned "State within normal range". Now:

- a note with crisis language gets the crisis notice and nothing that reads as
  reassurance, even when the phrase is negated or quoted (the demo cannot judge
  either, so it flags);
- every other note gets byte-for-byte the result it got before the guard.
  EXPECTED below was produced by the engine before the guard (clinic.py at
  576a3e6), serialized the way FastAPI sends it.
"""

from __future__ import annotations

import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from pep.axona import clinic
from pep.axona.core import CognitiveState, assess_alerts
from pep.routes import axona_products_api, product_pages

NOTICE = (
    "Possible crisis language detected. This demo cannot assess risk. If you or someone else may be "
    "in danger, contact local emergency services or a crisis line (in the US, call or text 988)."
)

# ── Normal notes ─────────────────────────────────────────────────────────
NORMAL = {
    "sample_progress": clinic.SAMPLE_NOTES["progress"],
    "sample_plateau": clinic.SAMPLE_NOTES["plateau"],
    "sample_integration": clinic.SAMPLE_NOTES["integration"],
    "sample_tilt": clinic.SAMPLE_NOTES["tilt"],
    "empty": "",
    "no_keywords": "We talked about the weekend and her plans for the garden.",
    "flow": "Clarity. It all makes sense, connected and integrated. Energized, sharp, focused and ready. A real insight.",
    "bandwidth_critical": "Exhausted, depleted and drained. Numb. Burned out after the move.",
    "bandwidth_declining": "Tired and overwhelmed, though still present for most of the session.",
    "chaos": "A breakthrough, a surprise, an aha moment, then confused, scattered, racing and jumbled.",
    "negative_valence": "Anxious, afraid and worthless. Says she feels empty.",
    "tilt_note": "Rage and shame after the argument; angry, racing, can't think, fragmented.",
    "near_miss_work": (
        "Deadline pressure this week. Skilled and killing it at work but dead tired. "
        "Cut back on caffeine; my back hurts. A cutting-edge project, harmless jokes, "
        "a hurtful comment from her manager."
    ),
    "near_miss_phrases": (
        "Took a break from the photo shoot. Life coach session about lifetime goals. "
        "End of my shift, so I take my time. No reason to worry; better off staying home. "
        "I would die for a good night's sleep."
    ),
    "near_miss_shorthand": "Hi, this is his sigh. Si, claro. Working on self-care and self-esteem.",
    "grief": "Grief about her father's death last spring. She keeps thinking about her father's death, but feels hopeful.",
    "curly_quotes": "She said “I’m doing better” and felt relieved — calm, even.",
    "uppercase": "PATIENT IS ANXIOUS AND OVERWHELMED BUT HOPEFUL.",
    "long": " ".join(["Calm and focused, grateful for the progress, stuck on the same loop at work."] * 40),
}

EXPECTED = {
    'sample_progress': '{"state":{"novelty":1.0,"coherence":1.0,"bandwidth":1.0,"valence":1.0,"quadrant":"genius","risk":"medium"},"alerts":[{"level":"info","message":"Flow state detected","recommendation":"Protect current conditions; do not interrupt"}]}',
    'sample_plateau': '{"state":{"novelty":0.0,"coherence":1.0,"bandwidth":0.0,"valence":0.0,"quadrant":"order","risk":"high"},"alerts":[{"level":"critical","message":"Bandwidth critically low","recommendation":"Immediate break recommended; hand off high-stakes tasks"}]}',
    'sample_integration': '{"state":{"novelty":1.0,"coherence":1.0,"bandwidth":1.0,"valence":1.0,"quadrant":"genius","risk":"medium"},"alerts":[{"level":"info","message":"Flow state detected","recommendation":"Protect current conditions; do not interrupt"}]}',
    'sample_tilt': '{"state":{"novelty":0.5,"coherence":0.0,"bandwidth":0.0,"valence":-1.0,"quadrant":"stagnation","risk":"high"},"alerts":[{"level":"critical","message":"Bandwidth critically low","recommendation":"Immediate break recommended; hand off high-stakes tasks"},{"level":"warning","message":"Strong negative valence detected","recommendation":"Emotional state may be affecting cognitive performance"},{"level":"critical","message":"Tilt detected — negative emotion disrupting coherence","recommendation":"Coach or supervisor intervention recommended"}]}',
    'empty': '{"state":{"novelty":0.5,"coherence":0.5,"bandwidth":0.5,"valence":0.0,"quadrant":"stagnation","risk":"low"},"alerts":[{"level":"info","message":"State within normal range","recommendation":"No action needed"}]}',
    'no_keywords': '{"state":{"novelty":0.5,"coherence":0.5,"bandwidth":0.5,"valence":0.0,"quadrant":"stagnation","risk":"low"},"alerts":[{"level":"info","message":"State within normal range","recommendation":"No action needed"}]}',
    'flow': '{"state":{"novelty":1.0,"coherence":1.0,"bandwidth":1.0,"valence":0.0,"quadrant":"genius","risk":"low"},"alerts":[{"level":"info","message":"Flow state detected","recommendation":"Protect current conditions; do not interrupt"}]}',
    'bandwidth_critical': '{"state":{"novelty":0.5,"coherence":0.5,"bandwidth":0.0,"valence":0.0,"quadrant":"stagnation","risk":"high"},"alerts":[{"level":"critical","message":"Bandwidth critically low","recommendation":"Immediate break recommended; hand off high-stakes tasks"}]}',
    'bandwidth_declining': '{"state":{"novelty":0.5,"coherence":0.5,"bandwidth":0.3333,"valence":0.0,"quadrant":"stagnation","risk":"medium"},"alerts":[{"level":"warning","message":"Bandwidth declining","recommendation":"Consider a break before the next demanding task"}]}',
    'chaos': '{"state":{"novelty":1.0,"coherence":0.0,"bandwidth":0.5,"valence":0.0,"quadrant":"chaos","risk":"low"},"alerts":[{"level":"critical","message":"Coherence collapsed under high novelty — chaos state","recommendation":"Reduce stimulus; structured task to restore coherence"}]}',
    'negative_valence': '{"state":{"novelty":0.5,"coherence":0.5,"bandwidth":0.5,"valence":-1.0,"quadrant":"stagnation","risk":"medium"},"alerts":[{"level":"warning","message":"Strong negative valence detected","recommendation":"Emotional state may be affecting cognitive performance"}]}',
    'tilt_note': '{"state":{"novelty":0.5,"coherence":0.0,"bandwidth":0.5,"valence":-1.0,"quadrant":"stagnation","risk":"medium"},"alerts":[{"level":"warning","message":"Strong negative valence detected","recommendation":"Emotional state may be affecting cognitive performance"},{"level":"critical","message":"Tilt detected — negative emotion disrupting coherence","recommendation":"Coach or supervisor intervention recommended"}]}',
    'near_miss_work': '{"state":{"novelty":0.5,"coherence":0.5,"bandwidth":0.0,"valence":0.0,"quadrant":"stagnation","risk":"high"},"alerts":[{"level":"critical","message":"Bandwidth critically low","recommendation":"Immediate break recommended; hand off high-stakes tasks"}]}',
    'near_miss_phrases': '{"state":{"novelty":1.0,"coherence":0.5,"bandwidth":0.5,"valence":0.0,"quadrant":"stagnation","risk":"low"},"alerts":[{"level":"info","message":"State within normal range","recommendation":"No action needed"}]}',
    'near_miss_shorthand': '{"state":{"novelty":0.5,"coherence":0.5,"bandwidth":0.5,"valence":0.0,"quadrant":"stagnation","risk":"low"},"alerts":[{"level":"info","message":"State within normal range","recommendation":"No action needed"}]}',
    'grief': '{"state":{"novelty":0.5,"coherence":0.5,"bandwidth":0.5,"valence":0.0,"quadrant":"stagnation","risk":"low"},"alerts":[{"level":"info","message":"State within normal range","recommendation":"No action needed"}]}',
    'curly_quotes': '{"state":{"novelty":0.5,"coherence":0.5,"bandwidth":0.5,"valence":1.0,"quadrant":"stagnation","risk":"medium"},"alerts":[{"level":"info","message":"State within normal range","recommendation":"No action needed"}]}',
    'uppercase': '{"state":{"novelty":0.5,"coherence":0.5,"bandwidth":0.0,"valence":0.0,"quadrant":"stagnation","risk":"high"},"alerts":[{"level":"critical","message":"Bandwidth critically low","recommendation":"Immediate break recommended; hand off high-stakes tasks"}]}',
    'long': '{"state":{"novelty":0.0,"coherence":0.5,"bandwidth":1.0,"valence":1.0,"quadrant":"stagnation","risk":"medium"},"alerts":[{"level":"info","message":"State within normal range","recommendation":"No action needed"}]}',
}

ALL_ALERTS = {
    "State within normal range", "Flow state detected", "Bandwidth critically low", "Bandwidth declining",
    "Coherence collapsed under high novelty — chaos state", "Strong negative valence detected",
    "Tilt detected — negative emotion disrupting coherence",
}


def _dumps(result: dict) -> str:
    return json.dumps(result, ensure_ascii=False, separators=(",", ":"))


@pytest.fixture(scope="module")
def client() -> TestClient:
    app = FastAPI()
    app.include_router(axona_products_api.router)
    app.include_router(product_pages.router)
    return TestClient(app)


def test_normal_set_exercises_every_alert() -> None:
    seen = {a["message"] for out in EXPECTED.values() for a in json.loads(out)["alerts"]}
    assert seen == ALL_ALERTS
    assert set(NORMAL) == set(EXPECTED)


@pytest.mark.parametrize("key", list(NORMAL))
def test_normal_note_is_byte_identical(key: str) -> None:
    assert clinic.crisis_matches(NORMAL[key]) == []
    assert _dumps(clinic.analyze_session(NORMAL[key])) == EXPECTED[key]


@pytest.mark.parametrize("key", list(NORMAL))
def test_normal_note_api_response_is_byte_identical(client: TestClient, key: str) -> None:
    resp = client.post("/axona/clinic-api/analyze", json={"text": NORMAL[key]})
    assert resp.status_code == 200
    assert resp.content == EXPECTED[key].encode("utf-8")


def test_samples_endpoint_unchanged_for_non_crisis_samples(client: TestClient) -> None:
    data = client.get("/axona/clinic-api/samples").json()
    for name in ("progress", "plateau", "integration", "tilt"):
        assert data[name]["text"] == clinic.SAMPLE_NOTES[name]
        assert _dumps(data[name]["analysis"]) == EXPECTED[f"sample_{name}"]


# ── Crisis language ──────────────────────────────────────────────────────
CRISIS = [
    # The exact case from the honesty pass, then the listed phrases in sentences
    "suicidal but grateful and hopeful",
    "Patient reports feeling suicidal.",
    "Some days I want to kill myself.",
    "She has thought about how to end her life.",
    "I just want to die.",
    "There is no reason to live.",
    "I'd be better off dead.",
    "They'd all be better off if I were gone.",
    "I hurt myself again last night.",
    "I cut myself when it gets bad.",
    # Harm to others
    "I want to kill him.",
    "Intrusive thoughts of hurting someone.",
    "Reports homicidal ideation toward a coworker.",
    "I'm going to hurt my wife.",
    "I'm scared I'll hurt my baby.",
    "I could kill my boss.",
    # Case, line breaks, curly apostrophes, dashes, shorthand, slang
    "SUICIDAL",
    "I want to KILL\nMYSELF",
    "I don’t want to live anymore.",
    "History of self–harm.",
    "Took an overdose in March.",
    "Pt endorses passive SI w/o plan.",
    "I wish I'd never been born.",
    "I can't go on anymore.",
    "I won't be around much longer.",
    "I just want it all to end.",
    "kms",
]
# The demo cannot judge negation or quotation, so it flags: the safe error.
NEGATED_OR_QUOTED = [
    "I'm not suicidal",
    "the patient said 'I want to die'",
    "Patient denies suicidal ideation.",
    "Denies SI/HI.",
    'He told me, "I would be better off dead," then laughed it off.',
    "I would never hurt myself.",
    "I don't want to hurt anyone.",
]
REASSURING = ("normal range", "no action needed", "flow state", "do not interrupt", '"low"', "genius")


def _assert_flagged(result: dict) -> None:
    assert list(result) == ["crisis", "state", "alerts"]
    assert result["crisis"]["detected"] is True
    assert result["crisis"]["message"] == NOTICE
    assert result["crisis"]["matches"]
    assert result["alerts"] == [
        {"level": "critical", "message": clinic.CRISIS_HEADLINE, "recommendation": clinic.CRISIS_ADVICE}
    ]
    assert result["state"]["quadrant"] == "not assessed"
    assert result["state"]["risk"] == "not assessed"
    dumped = json.dumps(result).lower()
    for phrase in REASSURING:
        assert phrase not in dumped


def test_notice_is_the_agreed_text() -> None:
    assert clinic.CRISIS_MESSAGE == NOTICE
    assert f"{clinic.CRISIS_HEADLINE} {clinic.CRISIS_ADVICE}" == NOTICE


def test_exact_case_from_the_honesty_pass() -> None:
    text = "suicidal but grateful and hopeful"
    # The keyword arithmetic alone still reads as reassurance...
    state = CognitiveState(
        novelty=clinic._count_ratio(text, clinic._NOVELTY_HIGH, clinic._NOVELTY_LOW),
        coherence=clinic._count_ratio(text, clinic._COHERENCE_HIGH, clinic._COHERENCE_LOW),
        bandwidth=clinic._count_ratio(text, clinic._BANDWIDTH_HIGH, clinic._BANDWIDTH_LOW),
        valence=clinic._valence_ratio(text),
    )
    assert [a.message for a in assess_alerts(state)] == ["State within normal range"]
    assert state.risk_level() == "low"
    # ...and the guard replaces all of it with the notice.
    result = clinic.analyze_session(text)
    _assert_flagged(result)
    assert result["crisis"]["matches"] == ["suicidal"]


@pytest.mark.parametrize("text", CRISIS)
def test_crisis_language_is_flagged(text: str) -> None:
    _assert_flagged(clinic.analyze_session(text))


@pytest.mark.parametrize("text", NEGATED_OR_QUOTED)
def test_negated_or_quoted_crisis_language_is_still_flagged(text: str) -> None:
    _assert_flagged(clinic.analyze_session(text))


def test_crisis_sample_note_is_flagged() -> None:
    _assert_flagged(clinic.analyze_session(clinic.SAMPLE_NOTES["crisis"]))


def test_matches_use_word_boundaries() -> None:
    assert clinic.crisis_matches("unskilled, killer app, deadline, hurtful, harmless, this, his") == []
    assert clinic.crisis_matches("Suicidal. SUICIDAL. suicidal.") == ["suicidal"]
    # "burned myself out" is burnout; "burned myself" is a burn.
    assert clinic.crisis_matches("I burned myself out at work") == []
    assert clinic.crisis_matches("I burned myself with a lighter") == ["burned myself"]


def test_api_returns_the_flag(client: TestClient) -> None:
    resp = client.post("/axona/clinic-api/analyze", json={"text": "suicidal but grateful and hopeful"})
    assert resp.status_code == 200
    _assert_flagged(resp.json())
    _assert_flagged(client.get("/axona/clinic-api/samples").json()["crisis"]["analysis"])


def test_playground_renders_the_notice_instead_of_the_state(client: TestClient) -> None:
    html = client.get("/axona/clinic/playground").text
    assert "if (data.crisis)" in html
    assert "esc(data.crisis.message)" in html
    assert "gets a crisis notice instead of a state: this demo cannot assess risk" in html
    assert "No state is shown for this note." in html


def test_product_page_copy_matches_the_flag(client: TestClient) -> None:
    html = client.get("/axona/clinic").text
    assert "Crisis flagging (not built)" not in html
    assert "Crisis detection is not built" not in html
    assert "Crisis language flag" in html
    assert "988" in html
    assert "it flags negated and quoted phrases too" in html
