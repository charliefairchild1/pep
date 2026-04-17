"""Axona Wellness — biometric data → cognitive state mapping.

Takes consumer-grade biometric inputs (HRV, sleep quality, activity
level, stress markers) and maps them to the bandwidth + valence axes
of the cognitive state space. Simpler mapping than BCI because the
inputs are lower-resolution.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .core import CognitiveState, StateAlert, assess_alerts, clamp01, clamp_valence


@dataclass
class BiometricReading:
    """Consumer-grade biometric snapshot."""

    hrv_ms: float = 60.0           # heart-rate variability in ms (higher = calmer)
    resting_hr: float = 65.0       # resting heart rate bpm
    sleep_hours: float = 7.5       # last night
    sleep_quality: float = 0.7     # [0, 1] — 0 = terrible, 1 = excellent
    activity_minutes: int = 30     # exercise minutes today
    stress_events: int = 0         # self-reported stressful events today
    screen_hours: float = 4.0      # screen time today
    caffeine_mg: float = 200.0     # caffeine intake mg


def map_biometrics(reading: BiometricReading) -> CognitiveState:
    """Map biometric inputs to cognitive state."""
    r = reading

    # Bandwidth: heavily influenced by sleep, HRV, and fatigue indicators
    sleep_factor = clamp01(r.sleep_hours / 8) * clamp01(r.sleep_quality)
    hrv_factor = clamp01((r.hrv_ms - 20) / 80)  # 20ms = stressed, 100ms = very calm
    fatigue = clamp01(r.screen_hours / 12)
    activity_boost = clamp01(r.activity_minutes / 60) * 0.15
    bandwidth = clamp01(sleep_factor * 0.4 + hrv_factor * 0.3 + (1 - fatigue) * 0.2 + activity_boost)

    # Valence: HRV, stress events, sleep quality
    stress_penalty = min(0.6, r.stress_events * 0.15)
    hrv_valence = clamp01((r.hrv_ms - 30) / 70)
    valence = clamp_valence(hrv_valence * 0.4 + sleep_factor * 0.3 - stress_penalty)

    # Coherence: inferred from bandwidth + sleep quality (rested = coherent)
    coherence = clamp01(bandwidth * 0.6 + sleep_factor * 0.4)

    # Novelty: caffeine and activity push novelty-seeking; fatigue dampens it
    caffeine_factor = clamp01(r.caffeine_mg / 400) * 0.3
    novelty = clamp01(0.3 + caffeine_factor + activity_boost * 0.5 - fatigue * 0.2)

    return CognitiveState(
        novelty=novelty,
        coherence=coherence,
        bandwidth=bandwidth,
        valence=valence,
    )


def wellness_report(reading: BiometricReading) -> dict[str, Any]:
    state = map_biometrics(reading)
    alerts = assess_alerts(state)
    return {
        "state": state.as_dict(),
        "alerts": [{"level": a.level, "message": a.message, "recommendation": a.recommendation} for a in alerts],
        "inputs": {
            "hrv_ms": reading.hrv_ms,
            "resting_hr": reading.resting_hr,
            "sleep_hours": reading.sleep_hours,
            "sleep_quality": reading.sleep_quality,
            "activity_minutes": reading.activity_minutes,
            "stress_events": reading.stress_events,
            "screen_hours": reading.screen_hours,
            "caffeine_mg": reading.caffeine_mg,
        },
    }


SAMPLE_PROFILES = {
    "well_rested": BiometricReading(hrv_ms=85, resting_hr=58, sleep_hours=8, sleep_quality=0.9, activity_minutes=45, stress_events=0, screen_hours=3, caffeine_mg=100),
    "sleep_deprived": BiometricReading(hrv_ms=35, resting_hr=78, sleep_hours=4.5, sleep_quality=0.3, activity_minutes=0, stress_events=2, screen_hours=8, caffeine_mg=400),
    "active_morning": BiometricReading(hrv_ms=75, resting_hr=60, sleep_hours=7, sleep_quality=0.75, activity_minutes=60, stress_events=0, screen_hours=1, caffeine_mg=150),
    "burned_out": BiometricReading(hrv_ms=28, resting_hr=82, sleep_hours=5, sleep_quality=0.2, activity_minutes=0, stress_events=4, screen_hours=11, caffeine_mg=500),
    "weekend_chill": BiometricReading(hrv_ms=90, resting_hr=55, sleep_hours=9, sleep_quality=0.95, activity_minutes=20, stress_events=0, screen_hours=2, caffeine_mg=0),
}
