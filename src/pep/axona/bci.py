"""Axona BCI SDK — electrode signal → cognitive state mapping.

Takes raw EEG-style signal features (power-band ratios, coherence
metrics) and maps them to the cognitive state space. The mapping is a
calibrated weighted combination personalized per user.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .core import CognitiveState, StateAlert, assess_alerts, clamp01, clamp_valence


@dataclass
class SignalFeatures:
    """Raw features extracted from electrode signals."""

    # Power band ratios (normalized 0-1)
    theta_alpha_ratio: float = 0.5   # high = drowsy/meditative
    beta_ratio: float = 0.5          # high = alert/focused
    gamma_ratio: float = 0.3         # high = complex processing
    # Coherence between frontal electrodes
    frontal_coherence: float = 0.5   # high = integrated thinking
    # Asymmetry (frontal alpha)
    frontal_asymmetry: float = 0.0   # negative = withdrawal, positive = approach
    # Event-related: P300 amplitude (surprise response)
    p300_amplitude: float = 0.5      # high = strong surprise/novelty response


@dataclass
class BCICalibration:
    """Per-user calibration weights. Built during a 1-week calibration."""

    novelty_weights: dict[str, float] = field(default_factory=lambda: {
        "gamma_ratio": 0.4, "p300_amplitude": 0.4, "beta_ratio": 0.2,
    })
    coherence_weights: dict[str, float] = field(default_factory=lambda: {
        "frontal_coherence": 0.6, "beta_ratio": 0.2, "gamma_ratio": 0.2,
    })
    bandwidth_weights: dict[str, float] = field(default_factory=lambda: {
        "beta_ratio": 0.35, "theta_alpha_ratio": -0.3, "frontal_coherence": 0.35,
    })
    valence_weights: dict[str, float] = field(default_factory=lambda: {
        "frontal_asymmetry": 0.7, "theta_alpha_ratio": -0.15, "beta_ratio": 0.15,
    })


def map_signal(features: SignalFeatures, calibration: BCICalibration | None = None) -> CognitiveState:
    """Map electrode signal features to cognitive state coordinates."""
    cal = calibration or BCICalibration()
    f = {
        "theta_alpha_ratio": features.theta_alpha_ratio,
        "beta_ratio": features.beta_ratio,
        "gamma_ratio": features.gamma_ratio,
        "frontal_coherence": features.frontal_coherence,
        "frontal_asymmetry": features.frontal_asymmetry,
        "p300_amplitude": features.p300_amplitude,
    }

    def weighted(weights: dict[str, float]) -> float:
        total_w = sum(abs(w) for w in weights.values()) or 1.0
        return sum(weights.get(k, 0) * f.get(k, 0) for k in weights) / total_w

    return CognitiveState(
        novelty=clamp01(weighted(cal.novelty_weights)),
        coherence=clamp01(weighted(cal.coherence_weights)),
        bandwidth=clamp01(weighted(cal.bandwidth_weights)),
        valence=clamp_valence(weighted(cal.valence_weights)),
    )


def interpret(features: SignalFeatures, calibration: BCICalibration | None = None) -> dict[str, Any]:
    """Full interpretation: state + alerts."""
    state = map_signal(features, calibration)
    alerts = assess_alerts(state)
    return {
        "state": state.as_dict(),
        "alerts": [{"level": a.level, "message": a.message, "recommendation": a.recommendation} for a in alerts],
        "features": {
            "theta_alpha_ratio": features.theta_alpha_ratio,
            "beta_ratio": features.beta_ratio,
            "gamma_ratio": features.gamma_ratio,
            "frontal_coherence": features.frontal_coherence,
            "frontal_asymmetry": features.frontal_asymmetry,
            "p300_amplitude": features.p300_amplitude,
        },
    }


SAMPLE_READINGS = {
    "flow": SignalFeatures(theta_alpha_ratio=0.3, beta_ratio=0.85, gamma_ratio=0.7, frontal_coherence=0.9, frontal_asymmetry=0.4, p300_amplitude=0.6),
    "fatigued": SignalFeatures(theta_alpha_ratio=0.8, beta_ratio=0.25, gamma_ratio=0.15, frontal_coherence=0.4, frontal_asymmetry=-0.1, p300_amplitude=0.2),
    "stressed": SignalFeatures(theta_alpha_ratio=0.4, beta_ratio=0.7, gamma_ratio=0.5, frontal_coherence=0.3, frontal_asymmetry=-0.5, p300_amplitude=0.7),
    "relaxed": SignalFeatures(theta_alpha_ratio=0.6, beta_ratio=0.35, gamma_ratio=0.2, frontal_coherence=0.7, frontal_asymmetry=0.3, p300_amplitude=0.3),
    "tilt": SignalFeatures(theta_alpha_ratio=0.5, beta_ratio=0.6, gamma_ratio=0.8, frontal_coherence=0.15, frontal_asymmetry=-0.7, p300_amplitude=0.9),
}
