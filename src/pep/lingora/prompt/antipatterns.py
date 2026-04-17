"""Antipattern library — known prompt-structure problems.

Each antipattern is a check function that returns a list of `Finding`s.
Checks operate on the raw prompt and/or the segment list. Findings
carry severity and a concrete suggestion for the rewriter.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import Callable

from .segments import Segment, SegmentRole
from .tokenizer import tokenize


class FindingSeverity(str, Enum):
    LOW = "low"        # cosmetic or token-efficiency
    MEDIUM = "medium"  # likely to affect behavior subtly
    HIGH = "high"      # strongly correlates with failure modes


@dataclass(frozen=True)
class Finding:
    """One detected issue, from one antipattern check."""

    name: str
    severity: FindingSeverity
    message: str
    suggestion: str
    # Locations in the prompt (char offsets) where the pattern was detected
    spans: tuple[tuple[int, int], ...] = ()


# ── specific checks ─────────────────────────────────────────────────────

_FILLER_WORDS = {
    "please", "kindly", "thanks", "thank",
    "carefully", "really", "very", "just",
}
_VAGUE_QUALIFIERS = {"good", "nice", "great", "proper", "appropriate", "best"}
_SYNONYM_CLUSTERS = [
    {"helpful", "useful", "beneficial"},
    {"thorough", "complete", "comprehensive", "exhaustive"},
    {"accurate", "correct", "precise", "exact"},
    {"clear", "concise", "plain"},
]


def _check_filler(text: str, segments: list[Segment]) -> list[Finding]:
    toks = tokenize(text)
    hits: Counter[str] = Counter()
    for tok in toks:
        if tok in _FILLER_WORDS:
            hits[tok] += 1
    if not hits:
        return []
    total_filler = sum(hits.values())
    total_words = max(1, len(toks))
    if total_filler / total_words < 0.01:
        return []  # tiny share, not worth flagging
    most = ", ".join(f'"{w}" ({c}x)' for w, c in hits.most_common(3))
    sev = FindingSeverity.LOW if total_filler < 5 else FindingSeverity.MEDIUM
    return [Finding(
        name="filler-words",
        severity=sev,
        message=f"Politeness/filler tokens add length without behavior: {most}",
        suggestion="Models don't need politeness markers. Drop them to cut tokens without changing behavior.",
    )]


def _check_repeated_synonyms(text: str, segments: list[Segment]) -> list[Finding]:
    toks = set(tokenize(text))
    findings: list[Finding] = []
    for cluster in _SYNONYM_CLUSTERS:
        hits = cluster & toks
        if len(hits) >= 2:
            findings.append(Finding(
                name="repeated-synonyms",
                severity=FindingSeverity.MEDIUM,
                message=f"Near-synonyms used together: {', '.join(sorted(hits))}",
                suggestion="Pick one. Repetition doesn't reinforce the instruction; it dilutes attention across near-identical constraints.",
            ))
    return findings


def _check_mixed_framing(text: str, segments: list[Segment]) -> list[Finding]:
    lower = text.lower()
    has_always = bool(re.search(r"\balways\b", lower))
    has_never = bool(re.search(r"\b(never|do not|don't|must not)\b", lower))
    if has_always and has_never:
        return [Finding(
            name="mixed-positive-negative",
            severity=FindingSeverity.MEDIUM,
            message='Mixed positive ("always") and negative ("never"/"do not") framing in the same prompt.',
            suggestion="Consolidate into positive constraints where possible. Positive framing produces cleaner attention than negative.",
        )]
    return []


def _check_make_sure_to(text: str, segments: list[Segment]) -> list[Finding]:
    matches = list(re.finditer(r"\bmake sure (?:to|that|you)\b", text, re.IGNORECASE))
    if not matches:
        return []
    spans = tuple((m.start(), m.end()) for m in matches)
    return [Finding(
        name="make-sure-to",
        severity=FindingSeverity.LOW,
        message=f'"{matches[0].group(0)}" is filler before an imperative verb.',
        suggestion='Replace "make sure to X" with just "X" (imperative). Shorter, same behavior.',
        spans=spans,
    )]


def _check_vague_qualifier(text: str, segments: list[Segment]) -> list[Finding]:
    toks = set(tokenize(text))
    vague = toks & _VAGUE_QUALIFIERS
    if not vague:
        return []
    return [Finding(
        name="vague-qualifier",
        severity=FindingSeverity.LOW,
        message=f"Vague quality words without operational meaning: {', '.join(sorted(vague))}",
        suggestion='Replace "good"/"appropriate"/"best" with a concrete criterion the model can check against.',
    )]


def _check_attention_dilution(text: str, segments: list[Segment]) -> list[Finding]:
    """Attention dilution: a wall of context with the actual question at
    the very end and no structural marker."""
    if not segments:
        return []
    total_tokens = sum(s.tokens for s in segments)
    if total_tokens < 300:
        return []
    # Last meaningful segment = the actual ask
    last = [s for s in segments if s.role not in (SegmentRole.SECTION_BREAK, SegmentRole.META)]
    if not last:
        return []
    last_seg = last[-1]
    ratio = last_seg.tokens / total_tokens
    if ratio < 0.08 and total_tokens > 300:
        return [Finding(
            name="attention-dilution",
            severity=FindingSeverity.MEDIUM,
            message=f"The final ask is {ratio*100:.1f}% of the prompt tokens in a {total_tokens}-token prompt.",
            suggestion="Move the ask earlier, or add a clear separator (### TASK) so the model's attention doesn't dissipate across context.",
        )]
    return []


def _check_conflicting_output_specs(text: str, segments: list[Segment]) -> list[Finding]:
    specs = [s for s in segments if s.role == SegmentRole.OUTPUT_SPEC]
    if len(specs) < 2:
        return []
    # Look for conflicting format keywords
    formats_seen: set[str] = set()
    for s in specs:
        for fmt in ("json", "yaml", "xml", "markdown", "csv", "table", "list"):
            if re.search(rf"\b{fmt}\b", s.text, re.IGNORECASE):
                formats_seen.add(fmt)
    if len(formats_seen) > 1:
        return [Finding(
            name="conflicting-output-spec",
            severity=FindingSeverity.HIGH,
            message=f"Multiple output formats requested: {', '.join(sorted(formats_seen))}",
            suggestion="Pick one output format. Conflicting specs force the model to guess and produce inconsistent output.",
        )]
    return []


def _check_persona_overload(text: str, segments: list[Segment]) -> list[Finding]:
    personas = [s for s in segments if s.role == SegmentRole.PERSONA]
    if len(personas) <= 1:
        return []
    return [Finding(
        name="persona-overload",
        severity=FindingSeverity.MEDIUM,
        message=f"{len(personas)} persona/role directives in one prompt.",
        suggestion="A single persona is usually stronger than stacked personas. Multiple roles dilute each other.",
    )]


def _check_contradicting_examples(text: str, segments: list[Segment]) -> list[Finding]:
    """Heuristic: if there's both an instruction saying X and an example
    violating X, flag it. Too subtle for a regex — do a simple variant:
    'respond in json' + an example block that isn't JSON."""
    instructions = [s for s in segments if s.role in (SegmentRole.INSTRUCTION, SegmentRole.OUTPUT_SPEC, SegmentRole.CONSTRAINT)]
    examples = [s for s in segments if s.role == SegmentRole.EXAMPLE]
    if not instructions or not examples:
        return []
    wants_json = any(re.search(r"\bjson\b", s.text, re.IGNORECASE) for s in instructions)
    if wants_json:
        for ex in examples:
            ex_body = re.sub(r"```.*?\n", "", ex.text, count=1, flags=re.DOTALL)
            ex_body = ex_body.replace("```", "").strip()
            # crude: does the example look like JSON?
            looks_json = ex_body.startswith("{") or ex_body.startswith("[")
            if ex_body and not looks_json:
                return [Finding(
                    name="example-contradicts-instruction",
                    severity=FindingSeverity.HIGH,
                    message="Prompt asks for JSON output but provides an example that isn't JSON.",
                    suggestion="Make your examples match your output spec. Models prioritize examples over instructions when they conflict.",
                )]
    return []


def _check_useless_step_by_step(text: str, segments: list[Segment]) -> list[Finding]:
    """`think step by step` added to every prompt without a concrete
    task that benefits from CoT is cargo-cult."""
    lower = text.lower()
    if "step by step" not in lower and "think carefully" not in lower:
        return []
    # Heuristic: if the prompt is short (< 200 tokens) and doesn't ask
    # for reasoning, CoT primer is probably filler
    total = sum(s.tokens for s in segments)
    has_reason_verb = bool(re.search(r"\b(explain|reason|derive|prove|why|analyze|compare|calculate|compute)\b", lower))
    if total < 200 and not has_reason_verb:
        return [Finding(
            name="cargo-cult-cot",
            severity=FindingSeverity.LOW,
            message='"Think step by step" added to a short, non-reasoning prompt.',
            suggestion='CoT primers add tokens and change model behavior. Only include them when the task actually needs multi-step reasoning.',
        )]
    return []


# ── registry ────────────────────────────────────────────────────────────

# Each entry: (name, check_fn). Ordered for stable output.
ANTIPATTERN_CHECKS: list[tuple[str, Callable[[str, list[Segment]], list[Finding]]]] = [
    ("filler-words", _check_filler),
    ("repeated-synonyms", _check_repeated_synonyms),
    ("mixed-framing", _check_mixed_framing),
    ("make-sure-to", _check_make_sure_to),
    ("vague-qualifier", _check_vague_qualifier),
    ("attention-dilution", _check_attention_dilution),
    ("conflicting-output-spec", _check_conflicting_output_specs),
    ("persona-overload", _check_persona_overload),
    ("example-contradicts-instruction", _check_contradicting_examples),
    ("cargo-cult-cot", _check_useless_step_by_step),
]


def detect_all(text: str, segments: list[Segment]) -> list[Finding]:
    """Run every antipattern check, collect findings. Stable order."""
    out: list[Finding] = []
    for _, check in ANTIPATTERN_CHECKS:
        out.extend(check(text, segments))
    return out
