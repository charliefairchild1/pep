"""The multi-face memory object — PEP's 'hexaflexagon'.

A memory is not a flat record. It is one object with several faces that
unfold differently depending on the cue.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

FaceName = Literal[
    "semantic",   # what it means
    "episodic",   # when/where it came up
    "value",      # significance / state-weighted importance
    "action",     # what it tends to lead to
    "predictive", # what it tends to connect with next
    "user",       # how this user tends to use it
]


class Link(BaseModel):
    """A weighted directed edge between memories. The link graph IS the switchboard."""

    to_id: str
    relation: Literal["semantic", "causal", "temporal", "co_activated", "user"] = "semantic"
    weight: float = 0.5


class SenseEntry(BaseModel):
    """One candidate sense of an ambiguous term, plus its confidence."""

    sense: str
    alternatives: list[str] = Field(default_factory=list)
    confidence: float = 0.5
    last_used_in_context: str = ""


class MemoryObject(BaseModel):
    """A single memory. One object, many faces, many possible openings."""

    id: str = Field(default_factory=lambda: f"mem_{uuid.uuid4().hex[:12]}")
    core: str

    # The faces — one object, six valid openings.
    # In Phase 1 we only fill `semantic` automatically; the rest get populated
    # by the Updater in Phase 2 via a small Claude call.
    faces: dict[FaceName, str] = Field(default_factory=dict)
    fold_weights: dict[FaceName, float] = Field(default_factory=dict)

    # Activation properties (the "star sky" model)
    brightness: float = 0.5
    tags: list[str] = Field(default_factory=list)
    links: list[Link] = Field(default_factory=list)

    # Sense / ambiguity tracking (Phase 2 fills this; Phase 1 leaves empty)
    sense_profile: dict[str, SenseEntry] = Field(default_factory=dict)

    # State-conditioned weighting — multipliers on brightness given current state
    state_modulation: dict[str, float] = Field(default_factory=dict)

    # Drift / reconsolidation
    confidence: float = 1.0
    drift_score: float = 0.0
    activation_count: int = 0

    # Forward-looking metadata. The Updater fills this in with the trajectory
    # score it computed at storage time. PTO 2G option (b).
    future_use: dict[str, float] = Field(default_factory=dict)

    # Which trajectory scorer produced future_use["trajectory_at_storage"]?
    # "llm" = LLM-driven (cheap haiku/ollama call), "heuristic" = the local
    # length-and-entity heuristic, None = no trajectory was scored.
    # Used by §8.1 follow-up: compare LLM vs heuristic predictive power.
    trajectory_source: str | None = None

    # Provenance
    source_type: Literal[
        "conversation",
        "document",
        "fact",
        "summary",
        "abstraction",
    ] = "conversation"
    session_id: str = "default"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activated: datetime = Field(default_factory=datetime.utcnow)
