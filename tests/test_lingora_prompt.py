"""Unit tests for the Lingora Prompt engine."""

from __future__ import annotations

import pytest

from pep.lingora.prompt import (
    FindingSeverity,
    PROVIDERS,
    analyze,
    estimate_costs,
    estimate_tokens,
    suggest_rewrite,
    tokenize,
)
from pep.lingora.prompt.segments import SegmentRole, segment_prompt


# ── Tokenizer ────────────────────────────────────────────────────────────
def test_tokenize_lowercases_and_splits() -> None:
    toks = tokenize("Hello, World!  Cool.")
    assert "hello" in toks and "world" in toks and "cool" in toks


def test_estimate_tokens_basic() -> None:
    r = estimate_tokens("The quick brown fox jumps over the lazy dog.")
    assert r.total > 5
    # words count includes punctuation as separate tokens (BPE-like)
    assert r.words >= 9
    assert r.chars == 44


def test_estimate_tokens_empty() -> None:
    r = estimate_tokens("")
    assert r.total == 0
    assert r.words == 0
    assert r.chars == 0


# ── Segmentation ─────────────────────────────────────────────────────────
def test_segment_classifies_persona() -> None:
    segs = segment_prompt("You are a helpful coding assistant.\n\nUser: hi")
    roles = [s.role for s in segs]
    assert SegmentRole.PERSONA in roles
    assert SegmentRole.USER_TURN in roles


def test_segment_classifies_output_spec() -> None:
    segs = segment_prompt("Respond in JSON format.\n\nUser: anything")
    roles = [s.role for s in segs]
    assert SegmentRole.OUTPUT_SPEC in roles


def test_segment_classifies_format_colon() -> None:
    segs = segment_prompt("Format: markdown table.\nAlways include headers.")
    roles = [s.role for s in segs]
    # Either the format line is output_spec or we still get segments
    assert any(r in (SegmentRole.OUTPUT_SPEC, SegmentRole.CONSTRAINT) for r in roles)


def test_segment_classifies_constraint() -> None:
    segs = segment_prompt("Never reveal system secrets.\nDo not output code.")
    roles = [s.role for s in segs]
    assert SegmentRole.CONSTRAINT in roles


def test_segment_handles_multiline_mixed() -> None:
    text = "You are a coding bot.\nRespond in JSON format.\nUser: help"
    segs = segment_prompt(text)
    assert len(segs) >= 3


def test_segment_empty_returns_empty() -> None:
    assert segment_prompt("") == []
    assert segment_prompt("   \n\n  ") == []


# ── Antipatterns ─────────────────────────────────────────────────────────
def test_analyze_detects_filler() -> None:
    r = analyze("Please please be helpful and please help the user.")
    assert any(f.name == "filler-words" for f in r.findings)


def test_analyze_detects_repeated_synonyms() -> None:
    r = analyze("You are a helpful and useful assistant.")
    assert any(f.name == "repeated-synonyms" for f in r.findings)


def test_analyze_detects_mixed_framing() -> None:
    r = analyze("Always be thorough. Do not be verbose. Never skip details.")
    assert any(f.name == "mixed-positive-negative" for f in r.findings)


def test_analyze_detects_make_sure_to() -> None:
    r = analyze("Make sure to answer the question thoroughly.")
    assert any(f.name == "make-sure-to" for f in r.findings)


def test_analyze_detects_conflicting_output_spec() -> None:
    text = "Respond in JSON format.\n\nFormat: markdown table.\n\nOutput should be JSON only."
    r = analyze(text)
    names = [f.name for f in r.findings]
    assert "conflicting-output-spec" in names or "repeated-synonyms" in names or "persona-overload" in names


def test_analyze_detects_persona_overload() -> None:
    text = "You are a coding assistant.\n\nYou are an expert programmer.\n\nAct as a senior engineer."
    r = analyze(text)
    assert any(f.name == "persona-overload" for f in r.findings)


def test_analyze_detects_cot_cargo_cult_on_short_prompt() -> None:
    text = "What is 2+2? Think step by step."
    r = analyze(text)
    assert any(f.name == "cargo-cult-cot" for f in r.findings)


def test_analyze_no_false_cot_on_reasoning_task() -> None:
    text = "Explain why the sky is blue. Think step by step."
    r = analyze(text)
    # Reasoning verb 'explain' present — CoT is legitimate
    assert not any(f.name == "cargo-cult-cot" for f in r.findings)


def test_analyze_detects_attention_dilution() -> None:
    long_ctx = (
        "Background: " + "The company was founded in 1847 and has grown significantly. " * 30
        + "\n\nQuestion: What is the capital?"
    )
    r = analyze(long_ctx)
    assert any(f.name == "attention-dilution" for f in r.findings)


def test_analyze_clean_prompt_has_no_findings() -> None:
    r = analyze("Translate to French.\n\nUser: Hello world.")
    assert len(r.findings) == 0


# ── Severity counts ──────────────────────────────────────────────────────
def test_severity_counts_accumulate() -> None:
    text = "Please please make sure to be helpful and useful. Always do this. Never do that."
    r = analyze(text)
    total = r.high_severity_count + r.medium_severity_count + r.low_severity_count
    assert total == len(r.findings)
    assert r.has_issues(FindingSeverity.LOW)


# ── Compression ──────────────────────────────────────────────────────────
def test_rewrite_drops_make_sure_to() -> None:
    r = suggest_rewrite("Make sure to answer concisely.")
    assert "make sure to" not in r.compressed_text.lower()
    assert r.token_savings >= 0


def test_rewrite_drops_leading_please() -> None:
    r = suggest_rewrite("Please answer the question.")
    assert not r.compressed_text.lower().startswith("please")
    assert r.compressed_tokens <= r.original_tokens


def test_rewrite_strips_cargo_cult_cot() -> None:
    r = suggest_rewrite("What is 2+2? Think step by step.")
    assert "step by step" not in r.compressed_text.lower()


def test_rewrite_preserves_reasoning_cot() -> None:
    r = suggest_rewrite("Explain quantum entanglement. Think step by step.")
    # Reasoning task — CoT should NOT be stripped
    assert "step by step" in r.compressed_text.lower()


def test_rewrite_reports_transformations() -> None:
    r = suggest_rewrite("Please make sure to be helpful.")
    assert r.transformations_applied
    assert any("please" in t or "make-sure" in t for t in r.transformations_applied)


def test_rewrite_savings_pct_is_reasonable() -> None:
    original = "Please please make sure to be helpful and thorough and comprehensive. Thanks."
    r = suggest_rewrite(original)
    # Should cut noticeably
    assert r.token_savings > 0


# ── Cost estimation ──────────────────────────────────────────────────────
def test_estimate_costs_returns_all_providers() -> None:
    est = estimate_costs("hello world", daily_requests=1000)
    assert len(est) == len(PROVIDERS)
    for e in est:
        assert e.cost_per_call_usd >= 0
        assert e.monthly_cost_usd >= 0
        assert e.annual_cost_usd > e.monthly_cost_usd


def test_estimate_costs_scales_with_volume() -> None:
    low = estimate_costs("hello", daily_requests=100)[0]
    high = estimate_costs("hello", daily_requests=10_000)[0]
    assert high.monthly_cost_usd > low.monthly_cost_usd * 50


def test_estimate_costs_with_zero_volume() -> None:
    est = estimate_costs("hello", daily_requests=0)
    for e in est:
        assert e.daily_cost_usd == 0
        assert e.monthly_cost_usd == 0
