"""The State Modulator's variables — synthetic processing modes, not emotions."""

from __future__ import annotations

from pydantic import BaseModel, Field


class State(BaseModel):
    """Persistent internal state vector that biases everything downstream.

    These are *processing modes*, not feelings. They change how the system
    weights novelty, retrieval breadth, urgency, ambiguity tolerance.
    """

    urgency: float = Field(0.0, ge=0.0, le=1.0)
    uncertainty: float = Field(0.0, ge=0.0, le=1.0)
    novelty: float = Field(0.0, ge=0.0, le=1.0)
    conflict: float = Field(0.0, ge=0.0, le=1.0)
    exploration: float = Field(0.5, ge=0.0, le=1.0)
    stability_need: float = Field(0.5, ge=0.0, le=1.0)

    def blended_with(self, other: "State", weight: float = 0.3) -> "State":
        """Smooth the state across turns. weight=1.0 means full replacement."""
        w = weight
        return State(
            urgency=(1 - w) * self.urgency + w * other.urgency,
            uncertainty=(1 - w) * self.uncertainty + w * other.uncertainty,
            novelty=(1 - w) * self.novelty + w * other.novelty,
            conflict=(1 - w) * self.conflict + w * other.conflict,
            exploration=(1 - w) * self.exploration + w * other.exploration,
            stability_need=(1 - w) * self.stability_need + w * other.stability_need,
        )

    @classmethod
    def neutral(cls) -> "State":
        return cls()
