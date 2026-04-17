"""Document data class — the node type in the Vectora graph."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Document:
    """A node in the Vectora document graph.

    `embedding` is populated by the retriever when added; callers do not need
    to provide one. `metadata` is free-form and surfaces in retrieval results
    so callers can attach IDs, URLs, source labels, anything.

    Opacity model (the haze primitive): `opacity` is the node's current
    encoding strength in [0, 1]. It decays over time toward `opacity_floor`
    with a configurable half-life. A node whose effective opacity drops
    below the reuse threshold is available to be overwritten by later
    encoding. This is why vivid memories are bright and old ones are hazy —
    the same capacity got partially reclaimed.
    """

    id: str
    text: str
    embedding: list[float] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    # Haze primitive
    opacity: float = 1.0
    opacity_floor: float = 0.0
    encoded_at: float = field(default_factory=time.time)
    half_life_seconds: float = 7 * 24 * 3600.0  # default: one week

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("Document.id cannot be empty")
        if not isinstance(self.text, str):
            raise TypeError("Document.text must be a string")
        if not (0.0 <= self.opacity <= 1.0):
            raise ValueError(f"Document.opacity must be in [0, 1], got {self.opacity}")
        if self.half_life_seconds <= 0:
            raise ValueError(f"Document.half_life_seconds must be > 0, got {self.half_life_seconds}")

    def effective_opacity(self, at: float | None = None) -> float:
        """Opacity after time-based decay. Exponential half-life model."""
        now = at if at is not None else time.time()
        elapsed = max(0.0, now - self.encoded_at)
        decayed = self.opacity * (0.5 ** (elapsed / self.half_life_seconds))
        return max(self.opacity_floor, decayed)

    def reinforce(self, amount: float = 0.5, at: float | None = None) -> None:
        """Boost opacity (like a successful recall or re-encoding event).
        Clamps to 1.0. Resets `encoded_at` to now so decay restarts from
        the current strength."""
        now = at if at is not None else time.time()
        self.opacity = min(1.0, self.effective_opacity(now) + amount)
        self.encoded_at = now

    def is_reusable(self, threshold: float = 0.15, at: float | None = None) -> bool:
        """A node is available for reuse when its effective opacity is
        below the threshold. The graph can then overwrite it with a new
        encoding; this is the mechanism that makes capacity finite."""
        return self.effective_opacity(at) < threshold
