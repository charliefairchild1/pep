"""Interpreter heuristic tests."""

from __future__ import annotations

from pep.core.interpreter import interpret
from pep.schemas.input_schema import UserInput


def test_interpret_implementation_request() -> None:
    inp = UserInput(text="Build the PEP overlay with FastAPI and Pydantic.")
    result = interpret(inp)
    assert result.task_type == "implement"
    assert "PEP" in result.entities
    assert "FastAPI" in result.entities
    assert "Pydantic" in result.entities


def test_interpret_question() -> None:
    inp = UserInput(text="What is reactivation?")
    result = interpret(inp)
    assert result.task_type == "explain"


def test_interpret_short_input_high_ambiguity() -> None:
    inp = UserInput(text="ok go")
    result = interpret(inp)
    assert result.ambiguity_score >= 0.5


def test_interpret_explore_intent() -> None:
    inp = UserInput(text="Let me explore what if memory worked like a sky of stars.")
    result = interpret(inp)
    assert result.task_type == "explore"
