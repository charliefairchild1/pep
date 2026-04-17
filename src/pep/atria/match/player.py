"""Player data model — the input to every matcher operation.

Attributes are intentionally flat dimensions, not a black box. Each
scoring dimension has a clear cognitive interpretation and can be
individually weighted by the caller via ObjectiveWeights.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CommStyle(str, Enum):
    """How a player communicates in-game."""

    VOCAL = "vocal"        # uses voice chat, calls plays
    TEXT = "text"          # types but stays off voice
    MUTED = "muted"        # does not communicate
    REACTIVE = "reactive"  # responds if addressed, rarely initiates


class SessionGoal(str, Enum):
    """Why the player queued this session."""

    CASUAL = "casual"      # relaxing, no rank pressure
    LEARNING = "learning"  # improving, willing to lose for learning
    GRINDING = "grinding"  # climbing rank, takes it seriously
    COMPETITIVE = "competitive"  # tryhard, only wants wins


class BehaviorFlag(str, Enum):
    """Recent behavior signals that modulate compatibility."""

    TOXIC = "toxic"         # recent chat/voice toxicity reports
    AFK = "afk"             # recent AFK matches
    THROWING = "throwing"   # recent intentional losses
    LEAVER = "leaver"       # early-leave pattern


@dataclass
class Player:
    """One player in the pool. All fields are used by scoring.

    - rating: Elo-style skill rating (1000-3000 typical)
    - uncertainty: rating-deviation (wide for new/returning players)
    - tempo: [0, 1] — 0 = patient/methodical, 1 = aggressive/fast
    - tilt_tolerance: [0, 1] — 0 = tilts easily, 1 = unshakeable
    - role_pref: primary role (None = flexible)
    - comm_style: CommStyle
    - session_goal: SessionGoal
    - behavior_flags: list[BehaviorFlag] — recent flags
    - recent_matches: list[player_id] — cooldown tracker, avoid repeats
    - friends: list[player_id] — party-queue compatible
    - blocked: list[player_id] — will not be matched
    """

    id: str
    rating: float = 1500.0
    uncertainty: float = 100.0
    tempo: float = 0.5
    tilt_tolerance: float = 0.5
    role_pref: str | None = None
    comm_style: CommStyle = CommStyle.REACTIVE
    session_goal: SessionGoal = SessionGoal.CASUAL
    behavior_flags: list[BehaviorFlag] = field(default_factory=list)
    recent_matches: list[str] = field(default_factory=list)
    friends: list[str] = field(default_factory=list)
    blocked: list[str] = field(default_factory=list)
    # Free-form metadata (tier label, region, etc.)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("Player.id cannot be empty")
        if not (0.0 <= self.tempo <= 1.0):
            raise ValueError(f"Player.tempo must be in [0, 1], got {self.tempo}")
        if not (0.0 <= self.tilt_tolerance <= 1.0):
            raise ValueError(f"Player.tilt_tolerance must be in [0, 1], got {self.tilt_tolerance}")
        if self.uncertainty < 0:
            raise ValueError(f"Player.uncertainty must be >= 0, got {self.uncertainty}")

    @property
    def behavior_risk(self) -> float:
        """Aggregate behavior risk in [0, 1]. 0 = clean, 1 = multiple flags."""
        if not self.behavior_flags:
            return 0.0
        # Each flag adds ~0.35 risk, capped at 1.0
        weights = {
            BehaviorFlag.TOXIC: 0.40,
            BehaviorFlag.THROWING: 0.45,
            BehaviorFlag.AFK: 0.25,
            BehaviorFlag.LEAVER: 0.30,
        }
        total = sum(weights.get(f, 0.3) for f in self.behavior_flags)
        return min(1.0, total)

    @property
    def is_new_player(self) -> bool:
        """High uncertainty (wide placement window) signals a new player."""
        return self.uncertainty > 250


def make_player(
    id: str,
    rating: float = 1500,
    tempo: float = 0.5,
    tilt_tolerance: float = 0.5,
    **kwargs: Any,
) -> Player:
    """Shorthand constructor with sensible defaults."""
    return Player(id=id, rating=rating, tempo=tempo, tilt_tolerance=tilt_tolerance, **kwargs)
