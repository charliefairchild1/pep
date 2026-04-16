"""State Modulator — synthetic processing modes that bias everything downstream.

Two paths:

1. **LLM path** (preferred when a real client is available): a single haiku
   call returns a JSON object with the six state variables. Smoothing across
   turns happens at the call site, not inside the model.

2. **Heuristic fallback** (regex/keyword density): the original Phase 1 logic.
   Always available, deterministic, used as fallback.

The state vector represents *processing modes*, not feelings: urgency,
uncertainty, novelty, conflict, exploration, stability_need. Each is in [0,1].
"""

from __future__ import annotations

from pep.core._llm_helpers import call_for_json
from pep.models.llm_client import LLMClient
from pep.schemas.input_schema import InterpretedInput, UserInput
from pep.schemas.state_schema import State

# ----- Heuristic fallback -----

_URGENCY_WORDS = ("urgent", "asap", "now", "quickly", "immediately", "rush", "hurry")
_UNCERTAINTY_WORDS = ("maybe", "perhaps", "not sure", "i think", "might", "could be")
_CONFLICT_WORDS = ("but", "however", "wait", "actually", "no,", "disagree", "contradict")
_NOVELTY_WORDS = ("new", "novel", "first time", "never", "unprecedented", "weird")
_EXPLORE_WORDS = ("explore", "what if", "imagine", "brainstorm", "consider", "wonder")
_STABILITY_WORDS = ("keep", "preserve", "stay", "don't change", "leave", "as is")


def _density(text_lower: str, words: tuple[str, ...]) -> float:
    hits = sum(1 for w in words if w in text_lower)
    return min(1.0, hits * 0.35)


def _clamp(x: float) -> float:
    return max(0.0, min(1.0, x))


def _heuristic_state(
    user_input: UserInput, interpreted: InterpretedInput
) -> State:
    """Estimate fresh state purely from word density.

    No artificial floor on exploration — that was a Phase 1 default that
    made urgency unable to dominate, because exploration was always >= 0.5
    even when the user was clearly in panic mode. Now exploration starts at
    0 and rises only with explore words, so urgency and exploration can
    actually trade off properly.
    """
    text_lower = user_input.text.lower()
    return State(
        urgency=_clamp(_density(text_lower, _URGENCY_WORDS)),
        uncertainty=_clamp(max(_density(text_lower, _UNCERTAINTY_WORDS), interpreted.ambiguity_score)),
        novelty=_clamp(_density(text_lower, _NOVELTY_WORDS)),
        conflict=_clamp(_density(text_lower, _CONFLICT_WORDS)),
        exploration=_clamp(_density(text_lower, _EXPLORE_WORDS)),
        stability_need=_clamp(_density(text_lower, _STABILITY_WORDS)),
    )


# ----- LLM path -----

_STATE_SYSTEM = """\
You are PEP's State Modulator. You read a user message and the previous
state vector, and you return the new state as a JSON object. The state
represents *processing modes*, not feelings.

Return JSON with exactly these keys (each a float in [0, 1]):
- "urgency": how time-critical does the user seem to be?
- "uncertainty": how much ambiguity / hedging / confusion is in this message?
- "novelty": how surprising or new is the topic, relative to the previous state?
- "conflict": how much disagreement, contradiction, or course-correction?
- "exploration": how much does the user want to range broadly vs. answer narrowly?
- "stability_need": how much does the user want existing structure preserved?

Output ONLY the JSON object. No prose.
"""


def _llm_state(
    *,
    previous: State,
    user_input: UserInput,
    interpreted: InterpretedInput,
    llm: LLMClient,
) -> State | None:
    user_block = (
        f"Previous state: {previous.model_dump()}\n"
        f"Interpreted: intent={interpreted.intent}, task_type={interpreted.task_type}, "
        f"ambiguity={interpreted.ambiguity_score}\n\n"
        f"User message:\n{user_input.text}"
    )
    parsed = call_for_json(llm, system=_STATE_SYSTEM, user=user_block, model_tier="cheap")
    if not parsed:
        return None

    def _f(key: str, default: float = 0.0) -> float:
        try:
            return max(0.0, min(1.0, float(parsed.get(key, default))))
        except (TypeError, ValueError):
            return default

    try:
        return State(
            urgency=_f("urgency"),
            uncertainty=_f("uncertainty"),
            novelty=_f("novelty"),
            conflict=_f("conflict"),
            exploration=_f("exploration", 0.5),
            stability_need=_f("stability_need", 0.5),
        )
    except (TypeError, ValueError):
        return None


# ----- Public entry point -----

def estimate_state(
    previous: State,
    user_input: UserInput,
    interpreted: InterpretedInput,
    llm: LLMClient | None = None,
) -> State:
    """Estimate the new state vector for this turn.

    Tries the LLM path first, falls back to heuristics. Either way, the
    result is blended with the previous state so the vector smooths across
    turns instead of jumping.
    """
    fresh: State | None = None
    if llm is not None and llm.is_real:
        fresh = _llm_state(
            previous=previous,
            user_input=user_input,
            interpreted=interpreted,
            llm=llm,
        )
    if fresh is None:
        fresh = _heuristic_state(user_input, interpreted)

    return previous.blended_with(fresh, weight=0.4)
