"""Cost forecasting per provider.

A table of current public prices per 1M tokens for the major LLM
providers. Given a prompt's token count and a daily volume, compute
monthly API cost for input tokens + a reasonable output-token estimate.

Prices updated from each provider's public page; not a live feed. Users
can pass their own prices if they have enterprise contracts.
"""

from __future__ import annotations

from dataclasses import dataclass

from .tokenizer import estimate_tokens


@dataclass(frozen=True)
class Provider:
    """One provider/model entry with per-1M-token pricing in USD."""

    name: str                # e.g. "OpenAI · GPT-4o"
    input_per_m: float       # input tokens $/M
    output_per_m: float      # output tokens $/M
    context_window: int = 128_000
    provider_short: str = ""


# Public pricing snapshot. Verified against provider pricing pages.
# Update as prices change.
PROVIDERS: list[Provider] = [
    Provider("OpenAI · GPT-5",          2.50, 10.00, 256_000, "openai"),
    Provider("OpenAI · GPT-5 mini",     0.15,  0.60, 128_000, "openai"),
    Provider("Anthropic · Opus 4.6",   15.00, 75.00, 1_000_000, "anthropic"),
    Provider("Anthropic · Sonnet 4.6",  3.00, 15.00, 1_000_000, "anthropic"),
    Provider("Anthropic · Haiku 4.5",   0.25,  1.25, 200_000, "anthropic"),
    Provider("Google · Gemini 2.5 Pro", 1.25,  5.00, 2_000_000, "google"),
    Provider("Google · Gemini 2.5 Flash",0.10, 0.40, 1_000_000, "google"),
    Provider("Meta · Llama 3.1 405B",   0.90,  0.90, 128_000, "meta"),
    Provider("Mistral · Large 2",       2.00,  6.00, 128_000, "mistral"),
    Provider("xAI · Grok 4",            3.00, 15.00, 256_000, "xai"),
]


@dataclass(frozen=True)
class CostEstimate:
    provider: str
    input_tokens: int
    output_tokens: int
    daily_requests: int
    cost_per_call_usd: float
    daily_cost_usd: float
    monthly_cost_usd: float     # 30-day month
    annual_cost_usd: float      # 365-day year


def estimate_costs(
    prompt_text: str,
    *,
    daily_requests: int = 1000,
    output_tokens: int = 100,
    providers: list[Provider] | None = None,
) -> list[CostEstimate]:
    """Cost per provider for the given prompt text + volume + expected
    output length. Input tokens are counted from the prompt; output
    tokens are assumed per the caller's estimate (default 100).
    """
    input_tokens = estimate_tokens(prompt_text).total
    provs = providers if providers is not None else PROVIDERS
    out: list[CostEstimate] = []
    for p in provs:
        cost_per_call = (
            input_tokens * p.input_per_m / 1_000_000
            + output_tokens * p.output_per_m / 1_000_000
        )
        daily = cost_per_call * daily_requests
        monthly = daily * 30
        annual = daily * 365
        out.append(CostEstimate(
            provider=p.name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            daily_requests=daily_requests,
            cost_per_call_usd=round(cost_per_call, 6),
            daily_cost_usd=round(daily, 4),
            monthly_cost_usd=round(monthly, 2),
            annual_cost_usd=round(annual, 2),
        ))
    return out


def compare_compressed(
    original_text: str,
    compressed_text: str,
    *,
    daily_requests: int = 10_000,
    output_tokens: int = 100,
    providers: list[Provider] | None = None,
) -> list[dict]:
    """Cost comparison between an original and its compressed variant.
    Returns per-provider records with annual savings."""
    orig = estimate_costs(original_text, daily_requests=daily_requests,
                          output_tokens=output_tokens, providers=providers)
    comp = estimate_costs(compressed_text, daily_requests=daily_requests,
                          output_tokens=output_tokens, providers=providers)
    records: list[dict] = []
    for o, c in zip(orig, comp):
        savings = o.annual_cost_usd - c.annual_cost_usd
        records.append({
            "provider": o.provider,
            "original_monthly": o.monthly_cost_usd,
            "compressed_monthly": c.monthly_cost_usd,
            "annual_savings_usd": round(savings, 2),
            "pct_savings": round(
                (savings / o.annual_cost_usd * 100) if o.annual_cost_usd else 0, 2
            ),
        })
    return records
