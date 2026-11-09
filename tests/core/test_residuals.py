"""Residual scoring tests."""

from __future__ import annotations

from pep.core.residuals import score_residual
from pep.schemas.input_schema import InterpretedInput, Prediction
from pep.schemas.state_schema import State


def test_residual_low_when_prediction_matches() -> None:
    interpreted = InterpretedInput(
        intent="explain", topic="prediction", entities=["prediction", "storage"], task_type="explain"
    )
    prediction = Prediction(expected_entities=["prediction", "storage"])
    report = score_residual(
        interpreted=interpreted, prediction=prediction, state=State.neutral()
    )
    assert report.novelty_score < 0.4
    assert not report.should_store


def test_residual_high_when_unexpected_entities_appear() -> None:
    interpreted = InterpretedInput(
        intent="ask_question",
        topic="hexaflexagon",
        entities=["hexaflexagon", "origami", "fortune_teller"],
        ambiguity_score=0.6,
        task_type="explore",
    )
    prediction = Prediction(expected_entities=[])  # nothing expected
    report = score_residual(
        interpreted=interpreted, prediction=prediction, state=State.neutral()
    )
    assert report.novelty_score > 0.4
    assert report.should_store
    assert "hexaflexagon" in report.unexpected_entities
