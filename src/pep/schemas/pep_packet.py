"""The PEPPacket — the structured envelope handed to the base AI.

Plus the trace types that record what PEP did and why.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from pep.schemas.input_schema import InterpretedInput, Prediction
from pep.schemas.state_schema import State


class ActivationEntry(BaseModel):
    """One memory that lit up during reactivation, with score breakdown."""

    memory_id: str
    score: float
    components: dict[str, float] = Field(default_factory=dict)
    face_used: str = "semantic"
    constellation_id: int | None = None  # which constellation it belongs to, if any


class Constellation(BaseModel):
    """A coherent group of co-activated, linked memories.

    A constellation is the "stars belong together" idea: when several
    memories activate AND are mutually linked, they form a brighter
    cluster than any one of them alone.
    """

    id: int
    member_ids: list[str] = Field(default_factory=list)
    collective_score: float = 0.0
    cohesion: float = 0.0  # average internal link weight, [0, 1]


class SenseCandidate(BaseModel):
    """One possible sense of an ambiguous term, identified by its tag cluster.

    Without real embeddings, "sense" here is operationalized as the tag
    neighborhood that this term appeared with in past memories. The 'freedom'
    used in political contexts will have a different `context_tags` set than
    the 'freedom' used in physics contexts.
    """

    sense_label: str  # short human-readable label, e.g. "political freedom"
    context_tags: list[str] = Field(default_factory=list)
    supporting_memory_ids: list[str] = Field(default_factory=list)
    confidence: float = 0.0


class ResolvedTerm(BaseModel):
    """Sense Mapper output for one ambiguous term in the query."""

    term: str
    ambiguity_score: float = 0.0      # [0, 1] — how unresolved is it
    chosen_sense: SenseCandidate | None = None
    alternatives: list[SenseCandidate] = Field(default_factory=list)
    margin: float = 0.0               # confidence gap between top sense and #2
    branched: bool = False            # did the Reactivator branch on this term


class CategoryDescent(BaseModel):
    """One category that the cue 'descended into' during retrieval.

    Fortune-teller-fold model: when a cue arrives, we first identify which
    categories its tags overlap with. Members of those categories get a
    bonus in the scoring formula because the category itself is the right
    fold to open. This struct records each opened fold for the trace.
    """

    category_id: str
    cue_match_score: float
    member_count: int


class ActivationTrace(BaseModel):
    """Why PEP picked what it picked. The audit record."""

    cues: list[str] = Field(default_factory=list)
    candidates_considered: int = 0
    activated: list[ActivationEntry] = Field(default_factory=list)
    constellations: list[Constellation] = Field(default_factory=list)
    resolved_terms: list[ResolvedTerm] = Field(default_factory=list)
    descended_categories: list[CategoryDescent] = Field(default_factory=list)
    hops_used: int = 1
    fallback_to_strategic_search: bool = False
    fallback_reason: str = ""
    notes: str = ""


class ResidualReport(BaseModel):
    """The Residual Scorer's verdict on novelty and what to store.

    `should_store` here is the *candidate* decision based on local novelty.
    The Updater combines it with a trajectory score (PTO: "will this matter
    for future turns?") before actually persisting anything.
    """

    novelty_score: float = 0.0
    unexpected_entities: list[str] = Field(default_factory=list)
    intent_mismatch: float = 0.0
    context_mismatch: float = 0.0
    should_store: bool = False
    reason: str = ""

    # Filled in by the Updater AFTER the base AI responds. PTO option (b).
    # Range [0, 1]; 0.5 = neutral default when no LLM available.
    trajectory_score: float = 0.5


class PEPPacket(BaseModel):
    """The structured envelope handed to the base AI.

    Everything the base AI needs to reason well — and nothing it doesn't.
    """

    id: str = Field(default_factory=lambda: f"run_{uuid.uuid4().hex[:12]}")
    session_id: str = "default"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    raw_input: str
    interpreted: InterpretedInput
    prediction: Prediction
    state: State

    # The selected, unfolded memories — only the faces relevant to this cue
    selected_memories: list[dict] = Field(default_factory=list)

    residual: ResidualReport
    activation_trace: ActivationTrace

    # The actual goal we're handing the base AI
    response_goal: str = ""
    constraints: list[str] = Field(default_factory=list)

    # Per-step timings (seconds). Populated by the loop. Used by the dashboard.
    metrics: dict[str, float] = Field(default_factory=dict)
