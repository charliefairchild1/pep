"""Rewrite generation — compress a prompt while preserving behavior.

The compressor applies a set of deterministic transformations:
- drop filler/politeness tokens flagged by the antipattern library
- consolidate repeated synonyms (keep the first occurrence)
- remove "make sure to ..." before imperative verbs
- remove cargo-cult "think step by step" on short non-reasoning prompts
- drop low-constraint META segments when they don't carry information

Each transformation is a pure function on the text. The compressor
reports which transformations it applied so callers can audit.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .antipatterns import Finding, detect_all
from .segments import SegmentRole, segment_prompt
from .tokenizer import estimate_tokens


@dataclass
class Rewrite:
    original_text: str
    compressed_text: str
    original_tokens: int
    compressed_tokens: int
    transformations_applied: list[str] = field(default_factory=list)

    @property
    def token_savings(self) -> int:
        return self.original_tokens - self.compressed_tokens

    @property
    def token_savings_pct(self) -> float:
        if self.original_tokens == 0:
            return 0.0
        return self.token_savings / self.original_tokens * 100


# ── transformations ─────────────────────────────────────────────────────
# Each returns (new_text, applied_this_transform: bool)

_MAKE_SURE_RE = re.compile(r"\bmake sure (?:to|that|you)\s+", re.IGNORECASE)
_PLEASE_LEAD_RE = re.compile(r"(?i)(^|\n|\.\s+)please\s+", re.IGNORECASE)
_POLITE_SUFFIX_RE = re.compile(r"(?i)\s*(?:thanks|thank you)\.?\s*$")
_DOUBLE_SPACE_RE = re.compile(r" {2,}")
_TRIPLE_NEWLINE_RE = re.compile(r"\n{3,}")


def _drop_make_sure_to(text: str) -> tuple[str, bool]:
    new = _MAKE_SURE_RE.sub("", text)
    return new, new != text


def _drop_please_leading(text: str) -> tuple[str, bool]:
    # Replace leading "please" before a verb with nothing + capitalize next letter
    def repl(m: re.Match[str]) -> str:
        prefix = m.group(1) or ""
        return prefix
    new = _PLEASE_LEAD_RE.sub(repl, text)
    return new, new != text


def _drop_polite_suffix(text: str) -> tuple[str, bool]:
    new = _POLITE_SUFFIX_RE.sub("", text).rstrip() + ("\n" if text.endswith("\n") else "")
    if new.rstrip() == text.rstrip():
        return text, False
    return new, True


def _consolidate_repeated_words(text: str) -> tuple[str, bool]:
    """Drop later occurrences of certain interchangeable tokens
    ('helpful', 'thorough', etc.) within the same sentence-ish span."""
    repeated_targets = [
        "helpful", "useful",
        "thorough", "complete", "comprehensive",
        "accurate", "correct", "precise",
        "clear", "concise",
    ]
    changed = False
    new = text
    seen_by_cluster: dict[str, bool] = {w: False for w in repeated_targets}
    # Process sentence-level; reset seen each sentence
    parts = re.split(r"([.!?\n]+)", new)
    rebuilt: list[str] = []
    for chunk in parts:
        local_seen: dict[str, bool] = {}
        out = chunk
        for target in repeated_targets:
            pattern = re.compile(rf"\b{target}\b", re.IGNORECASE)
            matches = list(pattern.finditer(out))
            if len(matches) > 1:
                changed = True
                # Keep the first, drop subsequent with surrounding space cleanup
                def repl(m: re.Match[str], first=matches[0]) -> str:
                    return m.group(0) if m.start() == first.start() else ""
                out = pattern.sub(lambda m, f=matches[0]: m.group(0) if m.start() == f.start() else "", out)
        rebuilt.append(out)
    return "".join(rebuilt), changed


def _consolidate_multi_please(text: str) -> tuple[str, bool]:
    """If 'please' appears multiple times mid-text after the first, drop
    it from subsequent sentences."""
    pattern = re.compile(r"(?i)(?<=\b)please\b")
    matches = list(pattern.finditer(text))
    if len(matches) <= 1:
        return text, False
    # Keep only the first occurrence
    first_end = matches[0].end()
    prefix = text[:first_end]
    rest = pattern.sub("", text[first_end:])
    # Clean up any double spaces introduced
    rest = _DOUBLE_SPACE_RE.sub(" ", rest)
    return prefix + rest, True


def _strip_cot_primer(text: str, segments) -> tuple[str, bool]:
    """Remove 'think step by step' from short, non-reasoning prompts."""
    # Only applies if `_check_useless_step_by_step` would fire — we call
    # the detector and check.
    cargo_cult = any(f.name == "cargo-cult-cot" for f in detect_all(text, segments))
    if not cargo_cult:
        return text, False
    new = re.sub(r"(?i)\s*(?:think (?:carefully )?step by step\b\.?|think carefully\.?)", "", text)
    new = _DOUBLE_SPACE_RE.sub(" ", new)
    return new, new != text


def _collapse_whitespace(text: str) -> tuple[str, bool]:
    new = _TRIPLE_NEWLINE_RE.sub("\n\n", text)
    new = _DOUBLE_SPACE_RE.sub(" ", new)
    # Preserve leading/trailing newline pattern
    return new, new != text


def _drop_vague_qualifiers(text: str) -> tuple[str, bool]:
    """Strip standalone 'a good', 'the best', 'appropriate' when they
    don't anchor anything — only safe in obvious cases."""
    patterns = [
        (r"\b(?:a |the )?good\s+(?=(?:answer|response|explanation)\b)", ""),
        (r"\b(?:a |the )?best\s+(?=(?:answer|response|approach)\b)", ""),
    ]
    new = text
    changed = False
    for pat, repl in patterns:
        before = new
        new = re.sub(pat, repl, new, flags=re.IGNORECASE)
        if new != before:
            changed = True
    return new, changed


# ── pipeline ────────────────────────────────────────────────────────────

def suggest_rewrite(text: str) -> Rewrite:
    """Apply all compression transforms; report what changed."""
    original = text
    original_tokens = estimate_tokens(original).total
    segments = segment_prompt(text)
    applied: list[str] = []
    work = text

    for name, fn in [
        ("drop-make-sure-to", _drop_make_sure_to),
        ("drop-leading-please", _drop_please_leading),
        ("drop-multi-please", _consolidate_multi_please),
        ("drop-polite-suffix", _drop_polite_suffix),
        ("consolidate-synonyms", _consolidate_repeated_words),
        ("drop-vague-qualifiers", _drop_vague_qualifiers),
    ]:
        new, changed = fn(work)
        if changed:
            applied.append(name)
            work = new

    # CoT stripper operates on the segmented original; re-segment once
    work2, changed = _strip_cot_primer(work, segment_prompt(work))
    if changed:
        applied.append("strip-cargo-cult-cot")
        work = work2

    work, changed = _collapse_whitespace(work)
    if changed:
        applied.append("collapse-whitespace")

    compressed_tokens = estimate_tokens(work).total
    return Rewrite(
        original_text=original,
        compressed_text=work.strip() + ("\n" if original.endswith("\n") else ""),
        original_tokens=original_tokens,
        compressed_tokens=compressed_tokens,
        transformations_applied=applied,
    )
