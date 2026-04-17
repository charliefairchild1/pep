"""Lingora Translate — pragmatic-preserving translation engine.

Decomposes a source sentence into four semantic layers (denotation,
pragmatic intent, register, cultural framing), scores how much of each
layer survives a standard machine translation, and produces a
layer-aware translation that preserves what standard MT flattens.

LLM-free: uses heuristic layer detection + a curated example bank.
The production version would use Claude for the actual translation;
the engine here demonstrates the decomposition + scoring primitive.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Layer(str, Enum):
    DENOTATION = "denotation"
    PRAGMATIC = "pragmatic"
    REGISTER = "register"
    CULTURAL = "cultural"


@dataclass(frozen=True)
class LayerScore:
    layer: Layer
    description: str
    mt_preserves: float  # [0, 1] — how much standard MT preserves
    lingora_preserves: float  # [0, 1] — how much layer-aware translation preserves


@dataclass
class TranslationAnalysis:
    source: str
    source_lang: str
    target_lang: str
    layers: list[LayerScore]
    mt_output: str
    lingora_output: str
    mt_overall_preservation: float
    lingora_overall_preservation: float
    explanation: str


# ── Layer detection heuristics ──────────────────────────────────────────

_IDIOM_MARKERS = [
    (r"\bpiece of cake\b", "idiom: 'easy'", 0.1, 0.9),
    (r"\bbreak a leg\b", "idiom: 'good luck'", 0.05, 0.85),
    (r"\bhit the nail on the head\b", "idiom: 'exactly right'", 0.1, 0.9),
    (r"\bkick the bucket\b", "idiom: 'die'", 0.1, 0.85),
    (r"\blet the cat out of the bag\b", "idiom: 'reveal a secret'", 0.1, 0.9),
    (r"\bbite the bullet\b", "idiom: 'endure hardship'", 0.1, 0.85),
    (r"\bunder the weather\b", "idiom: 'feeling ill'", 0.15, 0.9),
    (r"\bcost an arm and a leg\b", "idiom: 'very expensive'", 0.1, 0.85),
    (r"\bspill the beans\b", "idiom: 'reveal information'", 0.1, 0.9),
]

_SARCASM_MARKERS = [
    (r"\byeah right\b", "sarcasm/disbelief"),
    (r"\boh great\b", "sarcastic enthusiasm"),
    (r"\bsure thing\b", "possible sarcasm"),
    (r"\bwonderful\b.*\bnot\b", "ironic understatement"),
    (r"\bbless your heart\b", "Southern US condescension"),
    (r"\bthat's just (great|wonderful|perfect)\b", "sarcastic praise"),
]

_REGISTER_MARKERS = {
    "formal": [r"\bwhom\b", r"\bfurthermore\b", r"\bnevertheless\b", r"\bhereby\b", r"\bshall\b"],
    "casual": [r"\bgonna\b", r"\bwanna\b", r"\bkinda\b", r"\byeah\b", r"\bnah\b", r"\blol\b", r"\bomg\b"],
    "technical": [r"\balgorithm\b", r"\blatency\b", r"\boptimize\b", r"\bdeployment\b", r"\binfrastructure\b"],
    "literary": [r"\bwhence\b", r"\bthither\b", r"\balas\b", r"\bforsooth\b"],
}

_CULTURAL_MARKERS = [
    (r"\bbless your heart\b", "Southern US politeness mask", 0.05, 0.85),
    (r"\bsaudade\b", "Portuguese untranslatable — yearning grief", 0.1, 0.8),
    (r"\bschadenfreude\b", "German — joy at others' misfortune", 0.7, 0.9),
    (r"\bwabi-sabi\b", "Japanese — beauty of imperfection", 0.1, 0.75),
    (r"\bhygge\b", "Danish — cozy contentment", 0.15, 0.8),
    (r"\bnamaste\b", "Hindi greeting — divine acknowledgment", 0.6, 0.9),
]


def _detect_register(text: str) -> tuple[str, float, float]:
    lower = text.lower()
    for reg, patterns in _REGISTER_MARKERS.items():
        for pat in patterns:
            if re.search(pat, lower):
                mt_score = 0.7 if reg in ("formal", "technical") else 0.3
                return reg, mt_score, 0.9
    return "neutral", 0.85, 0.9


def _detect_pragmatic(text: str) -> tuple[str, float, float]:
    lower = text.lower()
    # Check sarcasm
    for pat, desc in _SARCASM_MARKERS:
        if re.search(pat, lower):
            return desc, 0.1, 0.8
    # Check idioms
    for pat, desc, mt, lin in _IDIOM_MARKERS:
        if re.search(pat, lower):
            return desc, mt, lin
    # Default: literal intent
    return "literal/direct", 0.9, 0.95


def _detect_cultural(text: str) -> tuple[str, float, float]:
    lower = text.lower()
    for pat, desc, mt, lin in _CULTURAL_MARKERS:
        if re.search(pat, lower):
            return desc, mt, lin
    return "no specific cultural marker", 0.85, 0.9


def analyze_layers(text: str) -> list[LayerScore]:
    """Decompose a sentence into its four semantic layers with
    preservation scores for standard MT vs Lingora."""
    layers = []

    # Denotation — literal meaning. MT is generally good at this.
    layers.append(LayerScore(
        layer=Layer.DENOTATION,
        description="literal surface meaning",
        mt_preserves=0.90,
        lingora_preserves=0.92,
    ))

    # Pragmatic — what the speaker actually means
    prag_desc, prag_mt, prag_lin = _detect_pragmatic(text)
    layers.append(LayerScore(
        layer=Layer.PRAGMATIC,
        description=prag_desc,
        mt_preserves=prag_mt,
        lingora_preserves=prag_lin,
    ))

    # Register — formality level
    reg_name, reg_mt, reg_lin = _detect_register(text)
    layers.append(LayerScore(
        layer=Layer.REGISTER,
        description=f"{reg_name} register",
        mt_preserves=reg_mt,
        lingora_preserves=reg_lin,
    ))

    # Cultural — culture-specific framing
    cult_desc, cult_mt, cult_lin = _detect_cultural(text)
    layers.append(LayerScore(
        layer=Layer.CULTURAL,
        description=cult_desc,
        mt_preserves=cult_mt,
        lingora_preserves=cult_lin,
    ))

    return layers


# ── Pre-built translation examples ─────────────────────────────────────

EXAMPLES: dict[str, dict[str, str]] = {
    "it's a piece of cake": {
        "mt": "Es un trozo de pastel.",
        "lingora": "Está chupado.",
        "explanation": "Spanish idiom for 'trivially easy' — preserves pragmatic intent + casual register, drops the literal cake.",
    },
    "bless your heart": {
        "mt": "Bendice tu corazón.",
        "lingora": "Ay, pobrecito...",
        "explanation": "Preserves the Southern US passive-aggressive condescension. MT produces a sincere religious blessing.",
    },
    "break a leg": {
        "mt": "Rompe una pierna.",
        "lingora": "¡Mucha mierda!",
        "explanation": "Theater good-luck idiom. Spanish theater tradition uses '¡Mucha mierda!' for the same function.",
    },
    "yeah right": {
        "mt": "Sí, correcto.",
        "lingora": "Sí, claro... (con sarcasmo)",
        "explanation": "Sarcastic disbelief. MT renders it as a sincere agreement. Lingora preserves the sarcastic framing.",
    },
    "that's just wonderful": {
        "mt": "Eso es maravilloso.",
        "lingora": "Pues qué bien... (irónico)",
        "explanation": "Ironic understatement. MT takes it at face value. Lingora preserves the irony marker.",
    },
    "under the weather": {
        "mt": "Bajo el clima.",
        "lingora": "No me siento bien. / Estoy pachucho.",
        "explanation": "English idiom for 'feeling ill.' MT produces a literal weather reference. Lingora maps to the Spanish colloquial equivalent.",
    },
    "spill the beans": {
        "mt": "Derramar los frijoles.",
        "lingora": "Soltar la sopa.",
        "explanation": "English idiom for 'reveal a secret.' MT translates the literal beans. Lingora uses the Spanish equivalent idiom 'soltar la sopa' (spill the soup).",
    },
}


def translate(text: str, target_lang: str = "es") -> TranslationAnalysis:
    """Full translation analysis. Uses the example bank for known phrases;
    for unknown text, produces the layer decomposition + generic scores."""
    layers = analyze_layers(text)
    lower = text.lower().strip().rstrip(".!?")
    # Normalize: strip apostrophes for more forgiving matching
    normalized = lower.replace("'", "").replace("\u2019", "")

    # Check example bank (try exact, then without apostrophes)
    example = EXAMPLES.get(lower)
    if not example:
        # Try matching with apostrophes stripped from both sides
        for key, val in EXAMPLES.items():
            if key.replace("'", "").replace("\u2019", "") == normalized:
                example = val
                break
    if example:
        mt_out = example["mt"]
        lin_out = example["lingora"]
        explanation = example["explanation"]
    else:
        mt_out = f"[standard MT would produce a literal translation of: {text}]"
        lin_out = f"[Lingora would decompose into layers and translate each, preserving pragmatic + register + cultural framing]"
        explanation = "No pre-built example for this input. The layer scores show what standard MT would likely lose."

    mt_overall = sum(l.mt_preserves for l in layers) / len(layers)
    lin_overall = sum(l.lingora_preserves for l in layers) / len(layers)

    return TranslationAnalysis(
        source=text,
        source_lang="en",
        target_lang=target_lang,
        layers=layers,
        mt_output=mt_out,
        lingora_output=lin_out,
        mt_overall_preservation=round(mt_overall, 4),
        lingora_overall_preservation=round(lin_overall, 4),
        explanation=explanation,
    )


def batch_translate(texts: list[str], target_lang: str = "es") -> list[TranslationAnalysis]:
    return [translate(t, target_lang) for t in texts]
