"""Schemas for raw input, interpretation, and prediction."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class UserInput(BaseModel):
    """Raw input from the user. The thing PEP gets handed."""

    text: str
    session_id: str = "default"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class InterpretedInput(BaseModel):
    """The Interpreter's structured read of a UserInput.

    Not the answer to the question — just what kind of question it is.
    """

    intent: str  # e.g. "ask_question", "implement", "explore", "command"
    topic: str
    entities: list[str] = Field(default_factory=list)
    ambiguity_score: float = 0.0
    task_type: Literal[
        "ask_question",
        "explain",
        "implement",
        "explore",
        "plan",
        "command",
        "small_talk",
        "unknown",
    ] = "unknown"
    notes: str = ""  # free-form Interpreter commentary, useful for tracing


class Prediction(BaseModel):
    """The Predictor's guess at what context and outputs will matter."""

    expected_context_tags: list[str] = Field(default_factory=list)
    expected_output_type: str = "text"
    likely_next_needs: list[str] = Field(default_factory=list)
    expected_entities: list[str] = Field(default_factory=list)
    confidence: float = 0.5
