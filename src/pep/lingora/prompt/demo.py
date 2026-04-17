"""Sample prompts + runnable demo for the Lingora Prompt engine.

    python -m pep.lingora.prompt.demo

prints the analysis (segments, findings, compression) for a handful of
deliberately-flawed prompts. Useful for sanity-checking the engine.
"""

from __future__ import annotations

from . import analyze, estimate_costs, suggest_rewrite


SAMPLE_PROMPTS: dict[str, str] = {
    "polite-verbose": """You are a helpful assistant. Please be helpful and answer the user's question.
Please make sure to be accurate and thorough. Always provide complete answers.
Do not be unhelpful. Think step by step.

User: What is the capital of France?
""",
    "mixed-framing": """You are a coding assistant.
Always be thorough. Never skip details. Always explain your reasoning.
Do not be verbose. Make sure to be concise. Never write more than necessary.
Please answer thoroughly but do not include unnecessary detail.

User: Explain what a hashmap is.
""",
    "conflicting-format": """Respond in JSON format.
Format: markdown table.
Output should be a CSV.
User: List three prime numbers.
""",
    "attention-dilution": (
        "Background: " + (
            "Our company, Acme Corp, was founded in 1847 in the state of Delaware by Wilhelmina Acme. "
            "Since then we have expanded to over 42 countries and employ more than 18,000 people worldwide. "
            "Our core values are integrity, innovation, and teamwork. " * 10
        ) + "\n\nQuestion: What does Acme do?\n"
    ),
    "clean": """Translate the following English sentence to French.

User: The quick brown fox jumps over the lazy dog.
""",
}


def _format_report(name: str, text: str) -> str:
    r = analyze(text)
    lines = [f"\n{'=' * 70}", f"PROMPT: {name}", f"{'=' * 70}"]
    lines.append(f"Tokens: {r.total_tokens}  ·  Words: {r.total_words}  ·  Chars: {r.total_chars}  ·  Method: {r.tokenizer_method}")
    lines.append(f"Segments: {len(r.segments)}  ·  Findings: {len(r.findings)} "
                 f"(high={r.high_severity_count}, medium={r.medium_severity_count}, low={r.low_severity_count})")
    if r.segment_tokens_by_role:
        by_role = "  ·  ".join(f"{role}={tok}" for role, tok in sorted(r.segment_tokens_by_role.items()))
        lines.append(f"By role: {by_role}")
    lines.append("")
    if r.findings:
        lines.append("Findings:")
        for f in r.findings:
            lines.append(f"  [{f.severity.value.upper():6}] {f.name}: {f.message}")
            lines.append(f"           → {f.suggestion}")
    else:
        lines.append("No issues detected.")
    if r.rewrite:
        lines.append("")
        lines.append(f"Rewrite: {r.rewrite.original_tokens} → {r.rewrite.compressed_tokens} tokens "
                     f"({r.rewrite.token_savings_pct:.1f}% savings)")
        if r.rewrite.transformations_applied:
            lines.append(f"  applied: {', '.join(r.rewrite.transformations_applied)}")
    return "\n".join(lines)


def run_demo() -> None:
    for name, text in SAMPLE_PROMPTS.items():
        print(_format_report(name, text))

    # Cost spotlight on the most-abusable one
    print(f"\n\n{'=' * 70}\nCOST SPOTLIGHT — polite-verbose at 10K requests/day\n{'=' * 70}")
    rw = suggest_rewrite(SAMPLE_PROMPTS["polite-verbose"])
    print(f"\nOriginal ({rw.original_tokens} tokens):")
    print(f"  {rw.original_text.strip()}")
    print(f"\nCompressed ({rw.compressed_tokens} tokens, {rw.token_savings_pct:.1f}% savings):")
    print(f"  {rw.compressed_text.strip()}")
    print(f"\nMonthly cost (@10K/day, 100 output tokens):")
    print(f"  {'provider':<30} {'original':>12} {'compressed':>12} {'annual save':>14}")
    print("  " + "-" * 72)
    from .cost import compare_compressed
    records = compare_compressed(rw.original_text, rw.compressed_text, daily_requests=10_000)
    for r in records:
        print(f"  {r['provider']:<30} ${r['original_monthly']:>10.2f}  ${r['compressed_monthly']:>10.2f}  ${r['annual_savings_usd']:>12.2f}")


if __name__ == "__main__":
    run_demo()
