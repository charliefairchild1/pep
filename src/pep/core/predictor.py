"""Predictor — guesses what context, entities, and output type will matter.

Two paths:

1. **LLM path** (preferred when a real client is available): a single haiku
   call returns a structured Prediction. The prompt is given the interpretation,
   the current state, and the prior_expected_entities so the model knows what
   the system already 'knew about' before this turn.

2. **Heuristic fallback** (rule-based dictionary lookup): the original Phase 1
   logic. Always available, deterministic, used as fallback.

The `expected_entities` field exists for the Residual Scorer's use — it must
reflect what the system EXPECTED before seeing this turn, not what it just
received. Otherwise novelty can never fire. In Phase 1 it defaulted to empty;
in Phase 2 the LLM path can be smarter (it can predict what entities are
*likely to be discussed* given prior context, even before they appear).
"""

from __future__ import annotations

from pep.core._llm_helpers import call_for_json
from pep.models.llm_client import LLMClient
from pep.schemas.input_schema import InterpretedInput, Prediction
from pep.schemas.state_schema import State

# ----- Heuristic fallback -----

_TASK_TO_OUTPUT_TYPE = {
    "implement": "code",
    "plan": "structured_plan",
    "explain": "explanation",
    "explore": "open_discussion",
    "ask_question": "answer",
    "command": "action_confirmation",
    "small_talk": "short_reply",
    "unknown": "text",
}

_TASK_TO_FOLLOWUPS = {
    "implement": ["test", "edge_cases", "next_module"],
    "plan": ["risks", "dependencies", "first_step"],
    "explain": ["example", "contrast", "deeper_question"],
    "explore": ["specific_case", "implication", "counterexample"],
    "ask_question": ["clarification", "follow_up_question"],
    "command": ["status_check", "rollback"],
    "small_talk": [],
    "unknown": ["clarification"],
}


def _heuristic_predict(
    interpreted: InterpretedInput,
    state: State,
    prior_expected_entities: list[str] | None,
) -> Prediction:
    expected_tags = list(interpreted.entities)
    expected_tags.extend(t for t in interpreted.topic.split() if t)

    if state.exploration > 0.6:
        expected_tags.append("__exploratory__")
    if state.urgency > 0.5:
        expected_tags.append("__urgent__")

    confidence = 0.7 - 0.4 * interpreted.ambiguity_score - 0.2 * state.uncertainty
    confidence = max(0.1, min(1.0, confidence))

    return Prediction(
        expected_context_tags=list(dict.fromkeys(expected_tags)),
        expected_output_type=_TASK_TO_OUTPUT_TYPE.get(interpreted.task_type, "text"),
        likely_next_needs=_TASK_TO_FOLLOWUPS.get(interpreted.task_type, []),
        expected_entities=list(prior_expected_entities or []),
        confidence=confidence,
    )


# ----- LLM path -----

_PREDICTOR_SYSTEM = """\
You are PEP's Predictor module. Given an interpreted user message, the
current PEP state, and the entities the system was already aware of from
prior turns, return a Prediction as a single JSON object.

Return JSON with exactly these keys:
- "expected_context_tags": array of strings. The cue tags PEP should retrieve
  by — concrete topics, entities, related concepts. Lowercase. 5-15 items.
- "expected_output_type": short string. What kind of output the user is
  asking for. Examples: "code", "structured_plan", "explanation",
  "open_discussion", "answer", "action_confirmation", "short_reply", "text".
- "likely_next_needs": array of strings. 2-4 short labels for what the user
  will probably need next, given this turn.
- "expected_entities": array of strings. Entities the system *already*
  expected to see (carried from prior turns). Items genuinely new in the
  current message should NOT appear here — only what was already known.
- "confidence": float in [0, 1]. How confident the prediction is.

Output ONLY the JSON object, no prose.
"""


def _llm_predict(
    *,
    interpreted: InterpretedInput,
    state: State,
    prior_expected_entities: list[str] | None,
    llm: LLMClient,
) -> Prediction | None:
    user_block = (
        f"Interpreted: {interpreted.model_dump()}\n"
        f"State: {state.model_dump()}\n"
        f"Prior known entities (do not invent new ones): {prior_expected_entities or []}\n"
    )
    parsed = call_for_json(llm, system=_PREDICTOR_SYSTEM, user=user_block, model_tier="cheap")
    if not parsed:
        return None
    try:
        tags = parsed.get("expected_context_tags") or []
        if not isinstance(tags, list):
            tags = []
        next_needs = parsed.get("likely_next_needs") or []
        if not isinstance(next_needs, list):
            next_needs = []
        expected_ents = parsed.get("expected_entities") or []
        if not isinstance(expected_ents, list):
            expected_ents = []
        return Prediction(
            expected_context_tags=[str(t).lower()[:60] for t in tags if t][:20],
            expected_output_type=str(parsed.get("expected_output_type", "text"))[:60],
            likely_next_needs=[str(n)[:60] for n in next_needs if n][:8],
            expected_entities=[str(e)[:60] for e in expected_ents if e][:20],
            confidence=max(0.0, min(1.0, float(parsed.get("confidence", 0.5)))),
        )
    except (TypeError, ValueError):
        return None


# ----- Public entry point -----

def predict(
    interpreted: InterpretedInput,
    state: State,
    prior_expected_entities: list[str] | None = None,
    llm: LLMClient | None = None,
) -> Prediction:
    """Build a Prediction. Tries LLM path first, falls back to heuristics."""
    if llm is not None and llm.is_real:
        result = _llm_predict(
            interpreted=interpreted,
            state=state,
            prior_expected_entities=prior_expected_entities,
            llm=llm,
        )
        if result is not None:
            return result
    return _heuristic_predict(interpreted, state, prior_expected_entities)
