"""Shared market primitives for all Strata verticals.

Every vertical uses the same scoring shape: an asset gets an "unusual
score" based on how far its current move deviates from its historical
pattern, classified into named archetypes, with a news/catalyst overlay.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Asset:
    """One tradeable asset in any vertical."""

    id: str
    name: str
    sector: str = ""
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MoveSignal:
    """A price/value move to be scored."""

    asset_id: str
    price_change_pct: float
    relative_volume: float = 1.0
    persistence: float = 0.5  # [0, 1] — did the move hold?
    catalyst: str = ""  # optional news/event description


@dataclass
class ScoredSignal:
    """Result of scoring a move."""

    asset_id: str
    unusual_score: float  # 0-100
    label: str  # "normal" / "notable" / "unusual" / "extreme"
    classification: str  # archetype name
    explanation: str
    components: dict[str, float]


def score_move(
    signal: MoveSignal,
    *,
    hist_mean_pct: float = 1.2,
    hist_std_pct: float = 1.0,
    archetypes: dict[str, dict[str, Any]] | None = None,
) -> ScoredSignal:
    """Score a move using the universal formula:
    35% price-percentile + 25% volume + 25% volatility-adjusted + 15% persistence.
    """
    abs_move = abs(signal.price_change_pct)

    # Component 1: price-change vs historical (approximated)
    z = (abs_move - hist_mean_pct) / max(0.01, hist_std_pct)
    # Approximate percentile via sigmoid
    price_pct = min(100, max(0, 50 + z * 20))

    # Component 2: relative volume
    vol_pct = min(100, max(0, (signal.relative_volume - 0.5) / 4 * 100))

    # Component 3: volatility-adjusted
    vol_adj = min(100, max(0, 50 + abs(z) * 20))

    # Component 4: persistence
    persist_pct = signal.persistence * 100

    # Composite
    composite = price_pct * 0.35 + vol_pct * 0.25 + vol_adj * 0.25 + persist_pct * 0.15

    # Label
    if composite >= 85:
        label = "extreme"
    elif composite >= 70:
        label = "unusual"
    elif composite >= 50:
        label = "notable"
    else:
        label = "normal"

    # Classification
    classification = _classify(signal, composite, archetypes or {})

    return ScoredSignal(
        asset_id=signal.asset_id,
        unusual_score=round(composite, 2),
        label=label,
        classification=classification,
        explanation=_explain(signal, classification, composite),
        components={
            "price_percentile": round(price_pct, 2),
            "volume_percentile": round(vol_pct, 2),
            "volatility_adjusted": round(vol_adj, 2),
            "persistence": round(persist_pct, 2),
        },
    )


def _classify(signal: MoveSignal, score: float, archetypes: dict) -> str:
    """Simple rule-based classification."""
    pct = signal.price_change_pct
    rvol = signal.relative_volume

    if score < 50:
        return "normal_move"
    if pct > 10 and rvol > 5:
        return "breakout" if pct > 0 else "breakdown"
    if rvol > 6 and abs(pct) > 15:
        return "pump_risk" if pct > 0 else "capitulation"
    if abs(pct) > 5 and signal.persistence > 0.7:
        return "momentum"
    if abs(pct) > 3 and signal.persistence < 0.3:
        return "mean_reversion_candidate"
    if pct > 0 and rvol > 3:
        return "breakout"
    if pct < 0 and rvol > 3:
        return "breakdown"
    return "notable_move"


def _explain(signal: MoveSignal, classification: str, score: float) -> str:
    direction = "up" if signal.price_change_pct > 0 else "down"
    return (
        f"{abs(signal.price_change_pct):.1f}% {direction} on "
        f"{signal.relative_volume:.1f}x volume. "
        f"Classified as {classification} (score {score:.0f}). "
        f"{'Catalyst: ' + signal.catalyst if signal.catalyst else 'No identified catalyst.'}"
    )
