"""HTTP API for Lingora Prompt — backs the landing-page demos + standalone playground."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from pep.lingora.prompt import analyze, estimate_costs, suggest_rewrite
from pep.lingora.prompt.cost import compare_compressed

router = APIRouter()


class AnalyzeRequest(BaseModel):
    text: str
    include_rewrite: bool = True


class CompareRequest(BaseModel):
    original: str
    compressed: str | None = None  # if None, generate
    daily_requests: int = 10_000
    output_tokens: int = 100


class CostRequest(BaseModel):
    text: str
    daily_requests: int = 1000
    output_tokens: int = 100


@router.post("/lingora/prompt-api/analyze")
async def api_analyze(req: AnalyzeRequest) -> dict[str, Any]:
    if len(req.text) > 50_000:
        raise HTTPException(400, "prompt too long (max 50000 chars)")
    r = analyze(req.text, include_rewrite=req.include_rewrite)
    return {
        "total_tokens": r.total_tokens,
        "total_words": r.total_words,
        "total_chars": r.total_chars,
        "tokenizer_method": r.tokenizer_method,
        "segments": [
            {
                "role": s.role.value, "text": s.text,
                "start": s.start, "end": s.end,
                "tokens": s.tokens, "signals": list(s.signals),
            }
            for s in r.segments
        ],
        "segment_tokens_by_role": r.segment_tokens_by_role,
        "findings": [
            {
                "name": f.name, "severity": f.severity.value,
                "message": f.message, "suggestion": f.suggestion,
                "spans": [list(sp) for sp in f.spans],
            }
            for f in r.findings
        ],
        "severity_counts": {
            "high": r.high_severity_count,
            "medium": r.medium_severity_count,
            "low": r.low_severity_count,
        },
        "rewrite": {
            "compressed_text": r.rewrite.compressed_text,
            "original_tokens": r.rewrite.original_tokens,
            "compressed_tokens": r.rewrite.compressed_tokens,
            "token_savings": r.rewrite.token_savings,
            "token_savings_pct": round(r.rewrite.token_savings_pct, 2),
            "transformations_applied": r.rewrite.transformations_applied,
        } if r.rewrite else None,
    }


@router.post("/lingora/prompt-api/rewrite")
async def api_rewrite(req: AnalyzeRequest) -> dict[str, Any]:
    if len(req.text) > 50_000:
        raise HTTPException(400, "prompt too long (max 50000 chars)")
    r = suggest_rewrite(req.text)
    return {
        "original_text": r.original_text,
        "compressed_text": r.compressed_text,
        "original_tokens": r.original_tokens,
        "compressed_tokens": r.compressed_tokens,
        "token_savings": r.token_savings,
        "token_savings_pct": round(r.token_savings_pct, 2),
        "transformations_applied": r.transformations_applied,
    }


@router.post("/lingora/prompt-api/cost")
async def api_cost(req: CostRequest) -> dict[str, Any]:
    if len(req.text) > 50_000:
        raise HTTPException(400, "prompt too long (max 50000 chars)")
    est = estimate_costs(
        req.text,
        daily_requests=req.daily_requests,
        output_tokens=req.output_tokens,
    )
    return {
        "costs": [
            {
                "provider": c.provider,
                "input_tokens": c.input_tokens,
                "output_tokens": c.output_tokens,
                "cost_per_call_usd": c.cost_per_call_usd,
                "daily_cost_usd": c.daily_cost_usd,
                "monthly_cost_usd": c.monthly_cost_usd,
                "annual_cost_usd": c.annual_cost_usd,
            }
            for c in est
        ],
    }


@router.post("/lingora/prompt-api/compare")
async def api_compare(req: CompareRequest) -> dict[str, Any]:
    if len(req.original) > 50_000 or (req.compressed and len(req.compressed) > 50_000):
        raise HTTPException(400, "prompt too long (max 50000 chars)")
    compressed_text = req.compressed
    if compressed_text is None:
        compressed_text = suggest_rewrite(req.original).compressed_text
    records = compare_compressed(
        req.original, compressed_text,
        daily_requests=req.daily_requests,
        output_tokens=req.output_tokens,
    )
    return {
        "original": req.original,
        "compressed": compressed_text,
        "per_provider": records,
    }
