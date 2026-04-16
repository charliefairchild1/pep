"""Interpreter — turns raw input into a structured InterpretedInput.

Two paths:

1. **LLM path** (preferred when a real client is available): a single haiku
   call returns a JSON object matching the InterpretedInput schema. We trust
   it but validate with Pydantic before returning.

2. **Heuristic fallback** (regex + keyword): the original Phase 1 logic.
   Always available, deterministic, used when there is no real LLM client OR
   when the LLM call fails / returns garbage.

The function `interpret(user_input, llm)` is the only entry point. Callers
do not need to know which path ran — but the `notes` field on the result
records it for the trace.
"""

from __future__ import annotations

import re

from pep.core._llm_helpers import call_for_json
from pep.models.llm_client import LLMClient
from pep.schemas.input_schema import InterpretedInput, UserInput

# ----- Heuristic fallback (Phase 1, still used when no real LLM) -----

_QUESTION_MARKERS = ("?", "what", "why", "how", "when", "who", "where", "which")
_IMPLEMENT_MARKERS = ("build", "implement", "code", "write", "create", "make", "scaffold")
_PLAN_MARKERS = ("plan", "design", "architecture", "approach", "strategy")
_EXPLAIN_MARKERS = ("explain", "describe", "tell me about", "what is", "what's")
_EXPLORE_MARKERS = ("think about", "explore", "what if", "consider", "imagine")
_COMMAND_MARKERS = ("run", "deploy", "stop", "start", "restart", "kill")
_SMALL_TALK_MARKERS = ("hi", "hello", "thanks", "thank you", "ok", "good")

_URGENCY_MARKERS = ("urgent", "asap", "right now", "immediately", "quickly")

_ENTITY_RE = re.compile(r"\b([A-Z][a-zA-Z0-9_]+|[A-Z]{2,})\b|`([^`]+)`")

_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "for", "to", "of", "in", "on",
    "at", "is", "are", "be", "this", "that", "with", "as", "it", "its",
    "i", "you", "we", "they", "he", "she", "my", "your", "our",
}


def _topic_from(text: str) -> str:
    words = re.findall(r"[a-zA-Z][a-zA-Z\-]+", text.lower())
    content = [w for w in words if w not in _STOPWORDS and len(w) > 2]
    return " ".join(content[:5]) if content else text[:40]


def _classify_task(text_lower: str) -> str:
    for marker in _IMPLEMENT_MARKERS:
        if marker in text_lower:
            return "implement"
    for marker in _PLAN_MARKERS:
        if marker in text_lower:
            return "plan"
    for marker in _EXPLAIN_MARKERS:
        if marker in text_lower:
            return "explain"
    for marker in _EXPLORE_MARKERS:
        if marker in text_lower:
            return "explore"
    for marker in _COMMAND_MARKERS:
        if marker in text_lower:
            return "command"
    if any(marker == text_lower.strip() or text_lower.startswith(marker + " ")
           for marker in _SMALL_TALK_MARKERS):
        return "small_talk"
    if any(marker in text_lower for marker in _QUESTION_MARKERS):
        return "ask_question"
    return "unknown"


def _ambiguity_score(text: str) -> float:
    n_words = len(text.split())
    if n_words < 5:
        return 0.7
    if n_words < 12:
        return 0.4
    return 0.15


def _heuristic_interpret(user_input: UserInput) -> InterpretedInput:
    text = user_input.text
    text_lower = text.lower()

    entities: list[str] = []
    for match in _ENTITY_RE.finditer(text):
        candidate = match.group(1) or match.group(2)
        if candidate and candidate.lower() not in _STOPWORDS:
            entities.append(candidate)

    task_type = _classify_task(text_lower)
    intent = task_type if task_type != "unknown" else "ask_question"

    return InterpretedInput(
        intent=intent,
        topic=_topic_from(text),
        entities=list(dict.fromkeys(entities)),
        ambiguity_score=_ambiguity_score(text),
        task_type=task_type,
        notes=(
            f"heuristic; len={len(text)}; "
            f"urgency_markers={sum(m in text_lower for m in _URGENCY_MARKERS)}"
        ),
    )


# ----- LLM path -----

_INTERPRETER_SYSTEM = """\
You are PEP's Interpreter module. Your job is to take a user message and
return a structured InterpretedInput as a single JSON object. You do not
answer the user. You only classify the input.

Return JSON with exactly these keys:
- "intent": string. A short verb phrase describing what the user wants.
- "topic": string. 3-8 words, the substantive topic.
- "entities": array of strings. Distinct named things mentioned (people,
  systems, files, libraries, projects, concepts). Lowercase or canonical
  form. Empty array if none.
- "ambiguity_score": float in [0, 1]. How underspecified is this input?
  0 = perfectly clear, 1 = could mean almost anything.
- "task_type": one of: "ask_question", "explain", "implement", "explore",
  "plan", "command", "small_talk", "unknown".
- "notes": string. One-line explanation of why you classified it this way.

Output ONLY the JSON object, nothing else. No prose, no fences.
"""

_VALID_TASK_TYPES = {
    "ask_question", "explain", "implement", "explore",
    "plan", "command", "small_talk", "unknown",
}


def _llm_interpret(user_input: UserInput, llm: LLMClient) -> InterpretedInput | None:
    parsed = call_for_json(
        llm,
        system=_INTERPRETER_SYSTEM,
        user=user_input.text,
        model_tier="cheap",
    )
    if not parsed:
        return None
    try:
        task_type = parsed.get("task_type", "unknown")
        if task_type not in _VALID_TASK_TYPES:
            task_type = "unknown"
        entities = parsed.get("entities") or []
        if not isinstance(entities, list):
            entities = []
        return InterpretedInput(
            intent=str(parsed.get("intent", "unknown"))[:80],
            topic=str(parsed.get("topic", ""))[:120] or _topic_from(user_input.text),
            entities=[str(e)[:60] for e in entities if e][:20],
            ambiguity_score=float(parsed.get("ambiguity_score", 0.3)),
            task_type=task_type,  # type: ignore[arg-type]
            notes="llm; " + str(parsed.get("notes", ""))[:200],
        )
    except (TypeError, ValueError):
        return None


# ----- Public entry point -----

def interpret(user_input: UserInput, llm: LLMClient | None = None) -> InterpretedInput:
    """Interpret raw user input into structured form.

    Tries the LLM path first if a real client is available. Falls back to
    deterministic heuristics on any failure. Always returns a valid result.
    """
    if llm is not None and llm.is_real:
        result = _llm_interpret(user_input, llm)
        if result is not None:
            return result
    return _heuristic_interpret(user_input)
