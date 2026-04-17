"""Top-level analyze() — runs tokenization, segmentation, antipatterns,
compression, and returns a full report."""

from __future__ import annotations

from dataclasses import dataclass, field

from .antipatterns import Finding, FindingSeverity, detect_all
from .compression import Rewrite, suggest_rewrite
from .segments import Segment, SegmentRole, segment_prompt, summarize_segments
from .tokenizer import TokenEstimate, estimate_tokens


@dataclass
class AnalysisReport:
    """Full structural + pattern report for one prompt."""

    original_text: str
    total_tokens: int
    total_words: int
    total_chars: int
    tokenizer_method: str
    segments: list[Segment] = field(default_factory=list)
    segment_tokens_by_role: dict[str, int] = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)
    rewrite: Rewrite | None = None

    @property
    def high_severity_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == FindingSeverity.HIGH)

    @property
    def medium_severity_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == FindingSeverity.MEDIUM)

    @property
    def low_severity_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == FindingSeverity.LOW)

    def has_issues(self, min_severity: FindingSeverity = FindingSeverity.MEDIUM) -> bool:
        levels = {FindingSeverity.LOW: 0, FindingSeverity.MEDIUM: 1, FindingSeverity.HIGH: 2}
        floor = levels[min_severity]
        return any(levels[f.severity] >= floor for f in self.findings)


def analyze(text: str, *, include_rewrite: bool = True) -> AnalysisReport:
    """Run the full analysis pipeline on a prompt."""
    tok_est: TokenEstimate = estimate_tokens(text)
    segments = segment_prompt(text)
    findings = detect_all(text, segments)
    rewrite = suggest_rewrite(text) if include_rewrite else None
    return AnalysisReport(
        original_text=text,
        total_tokens=tok_est.total,
        total_words=tok_est.words,
        total_chars=tok_est.chars,
        tokenizer_method=tok_est.method,
        segments=segments,
        segment_tokens_by_role=summarize_segments(segments),
        findings=findings,
        rewrite=rewrite,
    )
