"""Role segmentation — split a prompt into structural pieces.

Rule-based + heuristic role detection. A prompt becomes a list of
`Segment`s, each labeled with its likely role (persona / instruction /
context / example / constraint / output_spec / user_turn / meta).
Downstream analysis (antipatterns, compression) operates on segments.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum

from .tokenizer import estimate_tokens


class SegmentRole(str, Enum):
    PERSONA = "persona"              # "You are a ..."
    INSTRUCTION = "instruction"      # imperative guidance
    CONTEXT = "context"              # background/supporting info
    EXAMPLE = "example"              # few-shot examples, code blocks
    CONSTRAINT = "constraint"        # "always", "never", "must not"
    OUTPUT_SPEC = "output_spec"      # "respond with JSON", "format: markdown"
    USER_TURN = "user_turn"          # "User: ..."
    ASSISTANT_TURN = "assistant_turn"  # "Assistant: ..."
    SYSTEM = "system"                # explicit system tag
    META = "meta"                    # filler / politeness / uncategorized
    SECTION_BREAK = "section_break"  # "###", "---"


@dataclass(frozen=True)
class Segment:
    role: SegmentRole
    text: str
    start: int  # char offset in the original prompt
    end: int
    tokens: int
    signals: tuple[str, ...] = ()  # which heuristics matched


# ── heuristic signatures ────────────────────────────────────────────────

_RE_SECTION = re.compile(r"^\s*(#{2,}\s*.*|-{3,}|={3,}|\*{3,})\s*$")
_RE_USER_TURN = re.compile(r"^\s*(user|human)\s*:\s*(.*)$", re.IGNORECASE)
_RE_ASSISTANT_TURN = re.compile(r"^\s*(assistant|ai|model)\s*:\s*(.*)$", re.IGNORECASE)
_RE_SYSTEM_TAG = re.compile(r"^\s*(system|\[system\])\s*:?\s*(.*)$", re.IGNORECASE)
_RE_PERSONA = re.compile(r"\b(you are|act as|imagine you are|pretend to be|role:)\b", re.IGNORECASE)
_RE_CONSTRAINT = re.compile(
    r"\b(always|never|must not|do not|don't|must|cannot|can't|only if|under no circumstances|required to|forbidden|refuse to)\b",
    re.IGNORECASE,
)
_RE_OUTPUT_SPEC = re.compile(
    r"(?i)("
    r"\brespond (?:in|with)\s+\w+|"
    r"\boutput\s+(?:format|in|as|should|must|will|is|=)|"
    r"\breturn (?:only |just )?a? ?(?:json|yaml|xml|markdown|list|table|csv|html|text)|"
    r"\breply (?:in|with)\s+\w+|"
    r"\bthe\s+(?:response|answer|output)\s+(?:should|must|will|is)|"
    r"\byour\s+(?:response|answer|output)\s+(?:should|must)|"
    r"\bformat\s*[:=]|"
    r"\bformatted?\s+as\b|"
    r"^\s*format\s"
    r")"
)
_RE_INSTRUCTION_START = re.compile(
    r"^\s*(please\s+)?(\d+[.)]\s+|[-*]\s+|[A-Z][a-z]+ing\s|(?:analyze|answer|describe|explain|find|generate|identify|list|output|parse|provide|respond|return|summarize|translate|write)\b)",
    re.IGNORECASE,
)
_RE_CODE_BLOCK = re.compile(r"```.*?```", re.DOTALL)
_RE_META_FILLER = re.compile(
    r"^\s*(please|kindly|thank you|thanks|make sure to|be sure to|remember to|take your time|think carefully|think step by step)\b",
    re.IGNORECASE,
)


def _classify_line(line: str, prev_role: SegmentRole | None) -> tuple[SegmentRole, tuple[str, ...]]:
    """Classify a single non-empty line into a role."""
    s = line.strip()
    signals: list[str] = []

    if _RE_SECTION.match(s):
        return SegmentRole.SECTION_BREAK, ("section-marker",)
    if _RE_USER_TURN.match(s):
        return SegmentRole.USER_TURN, ("user-turn-prefix",)
    if _RE_ASSISTANT_TURN.match(s):
        return SegmentRole.ASSISTANT_TURN, ("assistant-turn-prefix",)
    if _RE_SYSTEM_TAG.match(s):
        return SegmentRole.SYSTEM, ("system-tag",)
    if _RE_CODE_BLOCK.match(s):
        return SegmentRole.EXAMPLE, ("code-block",)

    if _RE_PERSONA.search(s):
        return SegmentRole.PERSONA, ("persona-keyword",)
    if _RE_OUTPUT_SPEC.search(s):
        return SegmentRole.OUTPUT_SPEC, ("output-spec-keyword",)
    if _RE_CONSTRAINT.search(s):
        return SegmentRole.CONSTRAINT, ("constraint-keyword",)
    if _RE_META_FILLER.match(s):
        return SegmentRole.META, ("filler-opener",)
    if _RE_INSTRUCTION_START.match(s):
        return SegmentRole.INSTRUCTION, ("instruction-verb",)
    # Carry over context if we're continuing a context block
    if prev_role in (SegmentRole.CONTEXT, SegmentRole.EXAMPLE):
        return prev_role, ("continuation",)
    return SegmentRole.CONTEXT, ("fallback-context",)


def segment_prompt(text: str) -> list[Segment]:
    """Split a prompt into role-tagged segments.

    Uses paragraph-level splits as the primary unit (separated by blank
    lines), then single-line fallback. Each segment gets a token estimate.
    """
    if not text.strip():
        return []

    # Split by double-newline first; fall back to line-level
    paragraphs = re.split(r"\n\s*\n", text)
    segments: list[Segment] = []
    cursor = 0
    prev_role: SegmentRole | None = None

    for para in paragraphs:
        if not para.strip():
            # Advance the cursor past the whitespace
            cursor = text.find(para, cursor) if para else cursor
            continue
        # Find this paragraph's position in the original text
        start = text.find(para, cursor)
        if start < 0:
            start = cursor
        end = start + len(para)
        # If the paragraph has multiple lines, classify each line
        lines = para.split("\n")
        if len(lines) > 1 and _multiline_mixed_signals(lines):
            # Treat each line as its own segment
            line_cursor = start
            for line in lines:
                if not line.strip():
                    line_cursor += len(line) + 1
                    continue
                role, sigs = _classify_line(line, prev_role)
                tok = estimate_tokens(line).total
                segments.append(Segment(
                    role=role, text=line,
                    start=line_cursor, end=line_cursor + len(line),
                    tokens=tok, signals=sigs,
                ))
                prev_role = role
                line_cursor += len(line) + 1  # +1 for the newline
        else:
            role, sigs = _classify_line(para, prev_role)
            tok = estimate_tokens(para).total
            segments.append(Segment(
                role=role, text=para,
                start=start, end=end,
                tokens=tok, signals=sigs,
            ))
            prev_role = role
        cursor = end

    return segments


def _multiline_mixed_signals(lines: list[str]) -> bool:
    """True if the paragraph's lines seem to serve different roles,
    justifying line-by-line segmentation instead of paragraph-level."""
    classes: set[SegmentRole] = set()
    for line in lines:
        if not line.strip():
            continue
        role, _ = _classify_line(line, None)
        classes.add(role)
        if len(classes) > 1:
            return True
    return False


def summarize_segments(segments: list[Segment]) -> dict[str, int]:
    """Token count per role. Useful as a structural fingerprint."""
    out: dict[str, int] = {}
    for seg in segments:
        out[seg.role.value] = out.get(seg.role.value, 0) + seg.tokens
    return out
