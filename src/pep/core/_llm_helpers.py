"""Shared helpers for the supporting modules that call LLMs.

The supporting modules ask the model for structured JSON. The model is not
always cooperative — it might wrap the JSON in ```json fences, prepend a
sentence, return invalid JSON, or return nothing at all (the stub does this).

This file gives every supporting module the same parsing posture: try once,
gracefully accept None on failure, let the caller fall back to heuristics.
"""

from __future__ import annotations

import json
import re
from typing import Any

from pep.models.llm_client import LLMClient, ModelTier

_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


def _strip_fences(raw: str) -> str:
    match = _JSON_FENCE_RE.search(raw)
    if match:
        return match.group(1).strip()
    return raw.strip()


def _first_json_object(raw: str) -> str | None:
    """Find the first balanced {...} block in raw text."""
    start = raw.find("{")
    if start < 0:
        return None
    depth = 0
    for i in range(start, len(raw)):
        c = raw[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return raw[start : i + 1]
    return None


def extract_json(raw: str) -> dict[str, Any] | None:
    """Best-effort: pull a JSON object out of an LLM response. None on failure."""
    if not raw:
        return None
    cleaned = _strip_fences(raw)
    candidate = _first_json_object(cleaned) or cleaned
    try:
        result = json.loads(candidate)
        return result if isinstance(result, dict) else None
    except json.JSONDecodeError:
        return None


def call_for_json(
    llm: LLMClient,
    *,
    system: str,
    user: str,
    model_tier: ModelTier = "cheap",
) -> dict[str, Any] | None:
    """One round-trip: ask for JSON, parse, return None on any failure.

    Callers MUST be able to fall back to a heuristic when this returns None,
    because (a) the stub client always returns nothing and (b) real models
    occasionally produce malformed output.
    """
    if not llm.is_real:
        return None
    raw = llm.support(system=system, user=user, model_tier=model_tier)
    return extract_json(raw)
