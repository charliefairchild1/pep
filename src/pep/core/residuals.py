"""Residual Scorer — what was surprising enough to keep.

Compares actual input + interpretation to the Predictor's guesses, and
decides whether the new information should be stored.
"""

from __future__ import annotations

from pep.schemas.input_schema import InterpretedInput, Prediction
from pep.schemas.pep_packet import ResidualReport
from pep.schemas.state_schema import State


# Above this novelty score (after state modulation) we mark for storage.
DEFAULT_STORE_THRESHOLD = 0.45


def score_residual(
    *,
    interpreted: InterpretedInput,
    prediction: Prediction,
    state: State,
    threshold: float = DEFAULT_STORE_THRESHOLD,
) -> ResidualReport:
    """Diff actual against expected and decide whether to retain."""
    expected_entities = {e.lower() for e in prediction.expected_entities}
    actual_entities = {e.lower() for e in interpreted.entities}

    unexpected = sorted(actual_entities - expected_entities)
    if actual_entities:
        entity_mismatch = len(unexpected) / len(actual_entities)
    else:
        entity_mismatch = 0.0

    intent_mismatch = 0.0  # Phase 1 has no separate "expected intent" yet
    context_mismatch = entity_mismatch

    novelty = (
        0.5 * entity_mismatch
        + 0.3 * interpreted.ambiguity_score
        + 0.2 * context_mismatch
    )

    # High-novelty state lowers the storage bar (more curious mode).
    effective_threshold = threshold * (1.0 - 0.4 * state.novelty)
    should_store = novelty >= effective_threshold

    reason = (
        f"novelty={novelty:.2f} threshold={effective_threshold:.2f}; "
        f"unexpected_entities={len(unexpected)}; "
        f"ambiguity={interpreted.ambiguity_score:.2f}"
    )

    return ResidualReport(
        novelty_score=round(novelty, 4),
        unexpected_entities=unexpected,
        intent_mismatch=round(intent_mismatch, 4),
        context_mismatch=round(context_mismatch, 4),
        should_store=should_store,
        reason=reason,
    )
