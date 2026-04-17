"""Tests for Lingora Translate, Voice, and Learn engines."""

from pep.lingora import translate, voice, learn


# ── Translate ────────────────────────────────────────────────────────────
def test_translate_known_idiom() -> None:
    r = translate.translate("It's a piece of cake")
    assert r.lingora_output != r.mt_output
    assert r.lingora_overall_preservation > r.mt_overall_preservation


def test_translate_without_apostrophe() -> None:
    r = translate.translate("its a piece of cake")
    assert "chupado" in r.lingora_output.lower() or "pan comido" in r.lingora_output.lower()


def test_translate_sarcasm() -> None:
    r = translate.translate("yeah right")
    # Should detect pragmatic intent as sarcasm/disbelief
    pragmatic = [l for l in r.layers if l.layer.value == "pragmatic"][0]
    assert pragmatic.mt_preserves < pragmatic.lingora_preserves


def test_translate_four_layers() -> None:
    r = translate.translate("Break a leg")
    assert len(r.layers) == 4
    layer_names = {l.layer.value for l in r.layers}
    assert layer_names == {"denotation", "pragmatic", "register", "cultural"}


def test_translate_unknown_input() -> None:
    r = translate.translate("Some random sentence without idioms")
    assert r.mt_output  # Should still produce output
    assert len(r.layers) == 4


def test_translate_batch() -> None:
    results = translate.batch_translate(["piece of cake", "break a leg"])
    assert len(results) == 2


# ── Voice ────────────────────────────────────────────────────────────────
def test_voice_hemingway() -> None:
    text = "The old man was thin. He fished alone. He had not caught a fish in eighty-four days."
    r = voice.analyze_voice(text)
    assert r.total_words > 10
    assert r.total_sentences >= 2
    assert len(r.mechanisms) == 8
    assert r.voice_signature  # not empty


def test_voice_ironic_text() -> None:
    text = "Obviously, this is clearly the best approach. Of course, nobody could possibly disagree."
    r = voice.analyze_voice(text)
    irony = next(m for m in r.mechanisms if m.name == "irony")
    assert irony.value > 0.3


def test_voice_register_consistency_bad() -> None:
    text = "Furthermore, the analysis suggests. Yeah so like it's kinda cool though."
    r = voice.analyze_voice(text)
    consistency = next(m for m in r.mechanisms if m.name == "voice_consistency")
    assert consistency.value < 0.5


def test_voice_diagnostics_generated() -> None:
    r = voice.analyze_voice("Hello world. This is a test.")
    assert len(r.diagnostics) >= 1  # at least the default "no changes needed"


def test_voice_overall_strength_bounded() -> None:
    r = voice.analyze_voice("The quick brown fox jumps over the lazy dog.")
    assert 0 <= r.overall_voice_strength <= 1


def test_voice_all_mechanisms_named() -> None:
    r = voice.analyze_voice("Test text for mechanism coverage.")
    names = {m.name for m in r.mechanisms}
    expected = {"pov", "register", "irony", "subtext", "pacing", "voice_consistency", "repetition", "sound_symmetry"}
    assert names == expected


# ── Learn ────────────────────────────────────────────────────────────────
def test_learn_make_learner() -> None:
    lp = learn.make_learner()
    assert len(lp.words) == 10
    assert "saudade" in lp.words


def test_learn_study_boosts_strength() -> None:
    lp = learn.make_learner()
    w = lp.words["saudade"]
    before = w.effective_strength()
    w.study()
    after = w.effective_strength()
    assert after > before


def test_learn_recall_success_extends_halflife() -> None:
    lp = learn.make_learner()
    w = lp.words["hygge"]
    w.study()
    hl_before = w.half_life_hours
    w.recall_success()
    assert w.half_life_hours > hl_before


def test_learn_recall_failure_shortens_halflife() -> None:
    lp = learn.make_learner()
    w = lp.words["hygge"]
    w.study()
    hl_before = w.half_life_hours
    w.recall_failure()
    assert w.half_life_hours < hl_before


def test_learn_acquisition_depth_labels() -> None:
    lp = learn.make_learner()
    w = lp.words["ikigai"]
    assert w.acquisition_depth == "unseen"
    w.study()
    assert w.acquisition_depth in ("shallow", "moderate", "fading")


def test_learn_next_review() -> None:
    lp = learn.make_learner()
    lp.words["saudade"].study()
    lp.words["hygge"].study()
    review = lp.next_review(k=2)
    assert len(review) == 2


def test_learn_stats() -> None:
    lp = learn.make_learner()
    s = lp.stats()
    assert s["total_words"] == 10
    assert s["depths"]["unseen"] == 10


def test_learn_study_session_tracking() -> None:
    lp = learn.make_learner()
    sess = lp.study_word("saudade")
    assert sess is not None
    assert sess.word == "saudade"
    assert sess.action == "study"
    assert sess.strength_after > sess.strength_before


def test_learn_recall_session_tracking() -> None:
    lp = learn.make_learner()
    lp.study_word("komorebi")
    sess = lp.recall("komorebi", success=True)
    assert sess.action == "recall_success"
    assert len(lp.session_history) == 2
