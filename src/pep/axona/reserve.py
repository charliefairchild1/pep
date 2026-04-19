"""Axona Reserve — cognitive-reserve tracking and dementia-prevention signals.

Prevention-first framing of the opacity / haze primitive. The hypothesis:

  Dementia onset is delayed by graph redundancy. More reinforcement paths =
  more reconstructions surviving when pathology tears up the graph. Under
  PEP, "cognitive reserve" is a topology property of the episodic / semantic
  graph, not a scalar.

This module does three jobs:

  1. Ingest reinforcement windows (activity in modalities and topic areas)
     and compute a per-window contribution to the reserve estimate.
  2. Track pipeline-health signals (sleep, cardiovascular, hearing, etc.)
     that gate whether any reinforcement actually lands.
  3. Produce a ReserveSnapshot + interventions — under-stimulated
     modalities, topic monoculture, novelty drought, pipeline trouble.

All logic is heuristic (no API keys, per project constraint). Every
coefficient here is a starting point meant to be replaced once we have
real longitudinal data against clinical outcomes.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from .core import clamp01


# Known-important modalities. Order matters only for stable dict iteration
# in the snapshot. Additions are fine; removals break history comparisons.
MODALITIES = (
    "auditory",      # hearing, music, conversation, podcasts
    "linguistic",    # reading, writing, language production
    "spatial",       # navigation, spatial reasoning, visuospatial tasks
    "social",        # face-to-face / voice interactions (not messaging-only)
    "motor",         # physical activity, motor learning
    "abstract",      # math, argument, problem-solving in symbols
    "novel",         # genuine new-skill acquisition (anti-routine)
)


# ─── Data model ───────────────────────────────────────────────────────────

@dataclass
class ReinforcementWindow:
    """A single period of activity attributable to a modality + topic.

    intensity and novelty are in [0, 1] and are expected to be computed
    upstream from whatever tracker feeds this module (calendar, wearable,
    phone usage, self-report). Duration is in seconds.
    """
    modality: str
    topic: str
    duration_s: int
    intensity: float = 0.5
    novelty: float = 0.3
    ts: int = 0                         # unix seconds


@dataclass
class PipelineHealth:
    """Gates on whether reinforcement actually lands.

    All fields in [0, 1]; 1.0 is healthy. These are not reinforcement
    sources themselves — they are multipliers on the efficacy of any
    reinforcement the user does get. A brain with unmanaged hypertension
    and poor sleep will lose reserve faster than the window-log alone
    would predict.
    """
    sleep_quality: float = 0.7          # glymphatic clearance proxy
    sleep_hours_7d: float = 7.0
    cardiovascular: float = 0.7         # BP / resting HR / exercise proxy
    metabolic: float = 0.7              # glucose regulation / BMI
    hearing: float = 0.9                # audiogram / self-report
    vision: float = 0.9
    hydration: float = 0.8
    social_isolation: float = 0.2       # 0 = fully connected, 1 = isolated


@dataclass
class ReserveSnapshot:
    ts: int
    modality_coverage: dict[str, float]     # 7-day normalized reinforcement mass
    topic_entropy: float                    # Shannon entropy over topics, nats
    novelty_rate: float                     # new-node proxy per day
    graph_redundancy: float                 # mean connectivity proxy
    pipeline: PipelineHealth
    reserve_score: float                    # composite, [0, 1]


@dataclass
class ReserveAlert:
    level: str                              # "info" | "watch" | "act"
    code: str                               # stable id for UI dispatch
    message: str
    recommendation: str


# ─── Ingest + aggregate ───────────────────────────────────────────────────

def modality_coverage(windows: list[ReinforcementWindow], now_ts: int, window_days: int = 7) -> dict[str, float]:
    """Normalized reinforcement mass per modality over the last N days.

    Returns a dict summing to <= 1.0 (less if total activity is low).
    A value of e.g. 0.05 for 'auditory' means auditory accounts for 5%
    of this week's reinforcement mass — useful for detecting
    under-stimulated channels, not just low overall activity.
    """
    cutoff = now_ts - window_days * 86400
    mass: dict[str, float] = {m: 0.0 for m in MODALITIES}
    for w in windows:
        if w.ts < cutoff or w.modality not in mass:
            continue
        # Mass contribution = duration × intensity. Novelty is tracked
        # separately — we do not want to double-count it here.
        mass[w.modality] += (w.duration_s / 3600.0) * w.intensity
    total = sum(mass.values()) or 1.0
    return {m: mass[m] / (total + 1e-9) for m in MODALITIES}


def topic_entropy(windows: list[ReinforcementWindow], now_ts: int, window_days: int = 30) -> float:
    """Shannon entropy over topic distribution. Monoculture → 0, variety → ln(N)."""
    cutoff = now_ts - window_days * 86400
    mass: dict[str, float] = {}
    for w in windows:
        if w.ts < cutoff:
            continue
        mass[w.topic] = mass.get(w.topic, 0.0) + (w.duration_s / 3600.0)
    total = sum(mass.values())
    if total <= 0:
        return 0.0
    entropy = 0.0
    for v in mass.values():
        p = v / total
        if p > 0:
            entropy -= p * math.log(p)
    return entropy


def novelty_rate(windows: list[ReinforcementWindow], now_ts: int, window_days: int = 30) -> float:
    """Per-day novelty mass. Proxy for new-node creation rate."""
    cutoff = now_ts - window_days * 86400
    nov = 0.0
    for w in windows:
        if w.ts < cutoff:
            continue
        nov += (w.duration_s / 3600.0) * w.novelty
    return nov / max(1, window_days)


def graph_redundancy(coverage: dict[str, float], topic_ent: float) -> float:
    """Rough stand-in for 'how many reconstruction paths does this graph offer?'.

    Penalizes modality imbalance (concentration risk) and rewards topic
    breadth (more edges across subgraphs). Real computation would operate
    on the actual weighted graph — this is the no-graph-yet approximation.
    """
    # Modality balance: 1 - normalized variance. Max when all modalities
    # are used equally; 0 when everything lives in one modality.
    vals = list(coverage.values())
    n = len(vals)
    if n == 0 or sum(vals) == 0:
        return 0.0
    mean = sum(vals) / n
    var = sum((v - mean) ** 2 for v in vals) / n
    balance = clamp01(1.0 - var * n * n)   # var is tiny when balanced
    # Topic entropy normalized by ln(20) as a soft ceiling (20 topics = plenty).
    topic_breadth = clamp01(topic_ent / math.log(20))
    return 0.5 * balance + 0.5 * topic_breadth


# ─── Pipeline gate ────────────────────────────────────────────────────────

def pipeline_efficiency(p: PipelineHealth) -> float:
    """Multiplicative efficiency of the reinforcement pipeline in [0, 1].

    Sleep and vasculature are weighted hardest because they gate
    glymphatic clearance and reinforcement substrate respectively.
    Hearing is the single largest modifiable risk factor in the Lancet
    2020 analysis, so it gets real weight even though it only directly
    affects one modality — its downstream social-isolation effect
    multiplies.
    """
    isolation_term = 1.0 - p.social_isolation
    return clamp01(
        0.22 * p.sleep_quality +
        0.18 * p.cardiovascular +
        0.14 * p.metabolic +
        0.14 * p.hearing +
        0.08 * p.vision +
        0.04 * p.hydration +
        0.20 * isolation_term
    )


# ─── Composite reserve score ──────────────────────────────────────────────

def reserve_score(
    coverage: dict[str, float],
    topic_ent: float,
    novelty: float,
    redundancy: float,
    pipeline: PipelineHealth,
) -> float:
    """Composite in [0, 1]. Higher = more topology to spend against decline.

    Formula is intentionally stupid-simple so every coefficient is
    visible and testable. This is the number to calibrate once we have
    longitudinal outcomes.
    """
    # Raw cognitive-diet score (what is being reinforced).
    diet = 0.40 * redundancy + 0.25 * clamp01(topic_ent / math.log(20)) + 0.35 * clamp01(novelty * 2)
    # Pipeline gates how much of that diet actually lands.
    return clamp01(diet * pipeline_efficiency(pipeline))


def snapshot(
    windows: list[ReinforcementWindow],
    pipeline: PipelineHealth,
    now_ts: int,
) -> ReserveSnapshot:
    cov = modality_coverage(windows, now_ts)
    ent = topic_entropy(windows, now_ts)
    nov = novelty_rate(windows, now_ts)
    red = graph_redundancy(cov, ent)
    return ReserveSnapshot(
        ts=now_ts,
        modality_coverage=cov,
        topic_entropy=ent,
        novelty_rate=nov,
        graph_redundancy=red,
        pipeline=pipeline,
        reserve_score=reserve_score(cov, ent, nov, red, pipeline),
    )


# ─── Alerts + interventions ───────────────────────────────────────────────

# Thresholds below which a modality is considered under-stimulated.
# These are conservative defaults and must be tuned per-user against
# their own baseline once enough history exists.
_MODALITY_FLOOR = 0.05
_TOPIC_ENTROPY_FLOOR = 1.2      # < ~3-4 effective topics
_NOVELTY_FLOOR = 0.05
_SLEEP_FLOOR = 0.55
_HEARING_FLOOR = 0.7
_CV_FLOOR = 0.55


def _mod_suggestion(m: str) -> str:
    return {
        "auditory":   "podcasts, music with lyrics, phone calls, live conversation",
        "linguistic": "long-form reading, writing by hand, language practice",
        "spatial":    "navigation without GPS, drawing from life, spatial puzzles",
        "social":     "one voice or in-person interaction / day, beyond messaging",
        "motor":      "30+ min moderate activity, ideally learning a new movement",
        "abstract":   "math, programming, strategy games, non-routine problem-solving",
        "novel":      "a new skill started this month — instrument, language, craft",
    }.get(m, "targeted activity in this modality")


def detect_alerts(snap: ReserveSnapshot) -> list[ReserveAlert]:
    alerts: list[ReserveAlert] = []

    # 1. Modality collapse — any channel below the floor.
    for m, share in snap.modality_coverage.items():
        if share < _MODALITY_FLOOR:
            alerts.append(ReserveAlert(
                level="watch",
                code=f"modality_low:{m}",
                message=f"{m} accounts for {share:.0%} of this week's reinforcement",
                recommendation=f"add {_mod_suggestion(m)}",
            ))

    # 2. Topic monoculture.
    if snap.topic_entropy < _TOPIC_ENTROPY_FLOOR:
        alerts.append(ReserveAlert(
            level="watch",
            code="topic_monoculture",
            message=f"topic entropy {snap.topic_entropy:.2f} nats — narrow recent focus",
            recommendation="introduce one unrelated topic area per week; novelty needs distance",
        ))

    # 3. Novelty drought.
    if snap.novelty_rate < _NOVELTY_FLOOR:
        alerts.append(ReserveAlert(
            level="watch",
            code="novelty_drought",
            message=f"novelty rate {snap.novelty_rate:.2f} — mostly routine reinforcement",
            recommendation="start one genuinely new thing this month; routine does not grow new nodes",
        ))

    # 4. Pipeline signals — these gate everything else.
    p = snap.pipeline
    if p.sleep_quality < _SLEEP_FLOOR or p.sleep_hours_7d < 6.5:
        alerts.append(ReserveAlert(
            level="act",
            code="sleep_risk",
            message=f"sleep quality {p.sleep_quality:.2f} / {p.sleep_hours_7d:.1f}h avg",
            recommendation="glymphatic clearance degraded under 6.5h — sleep is the amyloid drain",
        ))
    if p.hearing < _HEARING_FLOOR:
        alerts.append(ReserveAlert(
            level="act",
            code="hearing_check",
            message=f"hearing signal {p.hearing:.2f} — largest modifiable Lancet factor",
            recommendation="audiogram; if fitted, consistent use of aids halves associated risk",
        ))
    if p.cardiovascular < _CV_FLOOR:
        alerts.append(ReserveAlert(
            level="act",
            code="cv_risk",
            message=f"cardiovascular signal {p.cardiovascular:.2f}",
            recommendation="BP, exercise, and metabolic health are reinforcement-pipeline upstream",
        ))
    if p.social_isolation > 0.6:
        alerts.append(ReserveAlert(
            level="act",
            code="isolation",
            message=f"isolation score {p.social_isolation:.2f}",
            recommendation="social engagement is high-bandwidth multi-modal reinforcement; 1 real interaction / day",
        ))

    return alerts


def assess(windows: list[ReinforcementWindow], pipeline: PipelineHealth, now_ts: int) -> dict[str, Any]:
    """End-to-end: windows + pipeline → snapshot + alerts. Route-friendly."""
    snap = snapshot(windows, pipeline, now_ts)
    alerts = detect_alerts(snap)
    return {
        "reserve_score": round(snap.reserve_score, 4),
        "modality_coverage": {k: round(v, 4) for k, v in snap.modality_coverage.items()},
        "topic_entropy": round(snap.topic_entropy, 4),
        "novelty_rate": round(snap.novelty_rate, 4),
        "graph_redundancy": round(snap.graph_redundancy, 4),
        "pipeline_efficiency": round(pipeline_efficiency(pipeline), 4),
        "alerts": [{"level": a.level, "code": a.code, "message": a.message, "recommendation": a.recommendation} for a in alerts],
    }


# ─── Per-user baseline calibration ────────────────────────────────────────

@dataclass
class UserBaseline:
    """Rolling personal baseline derived from the user's own history.

    When `days_observed` is below `MIN_DAYS`, alerts fall back to global
    floors; once enough history exists, per-user z-scores replace global
    thresholds. This is how the product moves from a generic "is sleep
    under 6.5h?" to a personalized "is sleep 2σ below your own baseline?"

    Updates: call `update(snap)` every time a new `ReserveSnapshot` is
    produced. Keeps exponentially-weighted mean/std with alpha tuned for
    a 60-day effective window.
    """
    MIN_DAYS: int = 30

    modality_mean: dict[str, float] = field(default_factory=dict)
    modality_var: dict[str, float] = field(default_factory=dict)
    topic_entropy_mean: float = 2.0
    topic_entropy_var: float = 0.25
    novelty_mean: float = 0.1
    novelty_var: float = 0.0025
    redundancy_mean: float = 0.5
    redundancy_var: float = 0.04
    reserve_mean: float = 0.55
    reserve_var: float = 0.02
    days_observed: int = 0

    def _ewma(self, prev: float, x: float, alpha: float = 1 / 60) -> float:
        return (1 - alpha) * prev + alpha * x

    def update(self, snap: ReserveSnapshot) -> None:
        a = 1 / 60  # ~60-day effective window
        for m, v in snap.modality_coverage.items():
            prev_mu = self.modality_mean.get(m, v)
            prev_var = self.modality_var.get(m, 0.01)
            new_mu = self._ewma(prev_mu, v, a)
            # Welford-style variance update (simplified for EWMA)
            new_var = self._ewma(prev_var, (v - new_mu) ** 2, a)
            self.modality_mean[m] = new_mu
            self.modality_var[m] = max(1e-6, new_var)
        self.topic_entropy_mean = self._ewma(self.topic_entropy_mean, snap.topic_entropy, a)
        self.topic_entropy_var = self._ewma(self.topic_entropy_var, (snap.topic_entropy - self.topic_entropy_mean) ** 2, a)
        self.novelty_mean = self._ewma(self.novelty_mean, snap.novelty_rate, a)
        self.novelty_var = self._ewma(self.novelty_var, (snap.novelty_rate - self.novelty_mean) ** 2, a)
        self.redundancy_mean = self._ewma(self.redundancy_mean, snap.graph_redundancy, a)
        self.redundancy_var = self._ewma(self.redundancy_var, (snap.graph_redundancy - self.redundancy_mean) ** 2, a)
        self.reserve_mean = self._ewma(self.reserve_mean, snap.reserve_score, a)
        self.reserve_var = self._ewma(self.reserve_var, (snap.reserve_score - self.reserve_mean) ** 2, a)
        self.days_observed += 1

    def is_calibrated(self) -> bool:
        return self.days_observed >= self.MIN_DAYS


def _z(x: float, mu: float, var: float) -> float:
    return (x - mu) / max(1e-6, math.sqrt(var))


def calibrated_alerts(snap: ReserveSnapshot, baseline: UserBaseline) -> list[ReserveAlert]:
    """Alerts using the user's own baseline once enough history exists.

    Before `MIN_DAYS`, returns the global-floor alerts unchanged — a cold
    start is still useful. After calibration, the alerts look at
    deviations from the user's personal mean, which catches subtle
    regressions that global floors miss (a bookish user whose reading
    drops 40% from their own norm vs. a global 'is reading > X'
    threshold).
    """
    if not baseline.is_calibrated():
        alerts = detect_alerts(snap)
        for a in alerts:
            a.message = f"[cold-start · {baseline.days_observed}/{baseline.MIN_DAYS}d observed] " + a.message
        return alerts

    alerts: list[ReserveAlert] = []

    # Modality regression — any modality 1.5σ below its own mean.
    for m, share in snap.modality_coverage.items():
        mu = baseline.modality_mean.get(m, share)
        var = baseline.modality_var.get(m, 0.01)
        z = _z(share, mu, var)
        if z < -1.5 and share < mu:
            alerts.append(ReserveAlert(
                level="act" if z < -2.5 else "watch",
                code=f"modality_regression:{m}",
                message=f"{m} {z:.1f}σ below your baseline ({share:.0%} vs {mu:.0%} norm)",
                recommendation=f"restore {_mod_suggestion(m)}",
            ))

    # Topic entropy regression.
    z_ent = _z(snap.topic_entropy, baseline.topic_entropy_mean, baseline.topic_entropy_var)
    if z_ent < -1.5:
        alerts.append(ReserveAlert(
            level="act" if z_ent < -2.5 else "watch",
            code="topic_regression",
            message=f"topic breadth {z_ent:.1f}σ below your baseline",
            recommendation="recent weeks have narrowed sharply vs. your norm — broaden inputs",
        ))

    # Novelty regression.
    z_nov = _z(snap.novelty_rate, baseline.novelty_mean, baseline.novelty_var)
    if z_nov < -1.5:
        alerts.append(ReserveAlert(
            level="act" if z_nov < -2.5 else "watch",
            code="novelty_regression",
            message=f"novelty {z_nov:.1f}σ below your baseline",
            recommendation="your own norm was higher — reintroduce new-skill acquisition",
        ))

    # Composite reserve regression — the headline score.
    z_res = _z(snap.reserve_score, baseline.reserve_mean, baseline.reserve_var)
    if z_res < -2.0:
        alerts.append(ReserveAlert(
            level="act",
            code="reserve_regression",
            message=f"reserve score {z_res:.1f}σ below your personal baseline",
            recommendation="multiple signals drifting together — review sleep, hearing, social, novelty",
        ))

    # Pipeline alerts still fire on global floors because their thresholds
    # are biological not personal (sleep < 6.5h damages everyone).
    p = snap.pipeline
    if p.sleep_quality < _SLEEP_FLOOR or p.sleep_hours_7d < 6.5:
        alerts.append(ReserveAlert(
            level="act", code="sleep_risk",
            message=f"sleep quality {p.sleep_quality:.2f} / {p.sleep_hours_7d:.1f}h avg",
            recommendation="glymphatic clearance degraded under 6.5h — sleep is the amyloid drain",
        ))
    if p.hearing < _HEARING_FLOOR:
        alerts.append(ReserveAlert(
            level="act", code="hearing_check",
            message=f"hearing signal {p.hearing:.2f} — largest modifiable Lancet factor",
            recommendation="audiogram; if fitted, consistent use of aids halves associated risk",
        ))
    return alerts


def assess_calibrated(
    windows: list[ReinforcementWindow],
    pipeline: PipelineHealth,
    now_ts: int,
    baseline: UserBaseline,
) -> dict[str, Any]:
    """End-to-end with baseline calibration. Updates baseline in place."""
    snap = snapshot(windows, pipeline, now_ts)
    alerts = calibrated_alerts(snap, baseline)
    baseline.update(snap)
    return {
        "reserve_score": round(snap.reserve_score, 4),
        "modality_coverage": {k: round(v, 4) for k, v in snap.modality_coverage.items()},
        "topic_entropy": round(snap.topic_entropy, 4),
        "novelty_rate": round(snap.novelty_rate, 4),
        "graph_redundancy": round(snap.graph_redundancy, 4),
        "pipeline_efficiency": round(pipeline_efficiency(pipeline), 4),
        "baseline_calibrated": baseline.is_calibrated(),
        "baseline_days_observed": baseline.days_observed,
        "alerts": [{"level": a.level, "code": a.code, "message": a.message, "recommendation": a.recommendation} for a in alerts],
    }


# Sample payload for the playground / product page.
SAMPLE = {
    "windows": [
        ReinforcementWindow("linguistic", "work",    3600 * 2, 0.8, 0.2, ts=0),
        ReinforcementWindow("auditory",   "podcast", 3600 * 1, 0.6, 0.4, ts=0),
        ReinforcementWindow("social",     "family",  3600 * 1, 0.9, 0.3, ts=0),
        ReinforcementWindow("motor",      "walk",    3600 * 1, 0.5, 0.1, ts=0),
        ReinforcementWindow("abstract",   "project", 3600 * 1, 0.8, 0.5, ts=0),
    ],
    "pipeline": PipelineHealth(
        sleep_quality=0.75, sleep_hours_7d=7.2,
        cardiovascular=0.7, metabolic=0.7,
        hearing=0.92, vision=0.95, hydration=0.8,
        social_isolation=0.15,
    ),
}
