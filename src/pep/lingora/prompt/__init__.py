"""Lingora Prompt — treat prompts as linguistic objects.

Structural tokenization, role segmentation, antipattern detection,
compression, and per-provider cost forecasting. LLM-free by design:
no external API calls, no inference spend, deterministic output.

Public API:
    from pep.lingora.prompt import analyze, suggest_rewrite, estimate_costs

    report = analyze(my_prompt)
    print(report.total_tokens, [f.name for f in report.findings])

    rewrite = suggest_rewrite(my_prompt)
    print(rewrite.compressed_text, rewrite.token_savings_pct)

    costs = estimate_costs(my_prompt, daily_requests=10_000)
    for c in costs:
        print(c.provider, c.monthly_cost_usd)
"""

from .analysis import AnalysisReport, Finding, FindingSeverity, analyze
from .compression import Rewrite, suggest_rewrite
from .cost import PROVIDERS, CostEstimate, Provider, estimate_costs
from .segments import Segment, SegmentRole
from .tokenizer import estimate_tokens, tokenize

__all__ = [
    "AnalysisReport",
    "CostEstimate",
    "Finding",
    "FindingSeverity",
    "PROVIDERS",
    "Provider",
    "Rewrite",
    "Segment",
    "SegmentRole",
    "analyze",
    "estimate_costs",
    "estimate_tokens",
    "suggest_rewrite",
    "tokenize",
]
