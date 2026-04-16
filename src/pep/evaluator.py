"""Evaluator — compute metrics from benchmark results.

Standard metrics:
  - retrieval_precision: fraction of selected memories whose tags overlap expected tags
  - context_efficiency: score / context_tokens (approximated by selected memory count)
  - latency_mean / latency_p95

PTO-derived metrics:
  - distractor_resistance: 1 - fraction of selected tags that are distractors
  - recall_hit_rate: for recall tasks, did the expected info appear in context?
  - sense_accuracy: for ambiguity tasks, did expected-sense tags dominate?
"""

from __future__ import annotations

from collections import defaultdict


def evaluate(results: list[dict]) -> dict:
    """Compute aggregate metrics from a list of benchmark task results.

    Returns a dict of {metric_name: value}.
    """
    if not results:
        return {}

    # Filter to actual test tasks (skip seed_turn, filler, priming)
    tests = [r for r in results if r.get("task_type") not in ("seed_turn", "filler", "priming")]
    if not tests:
        tests = results  # fallback: evaluate everything

    metrics: dict[str, float] = {}

    # Latency
    latencies = [r["latency_s"] for r in tests]
    metrics["latency_mean_s"] = round(sum(latencies) / len(latencies), 4)
    sorted_lat = sorted(latencies)
    p95_idx = min(len(sorted_lat) - 1, int(0.95 * len(sorted_lat)))
    metrics["latency_p95_s"] = round(sorted_lat[p95_idx], 4)

    # Retrieval precision (tag-based)
    precisions = []
    for r in tests:
        expected = set(r.get("expected_tags_in_context", []) or r.get("expected_in_context", []))
        if not expected:
            continue
        selected = set(r.get("selected_tags", []))
        if not selected:
            precisions.append(0.0)
            continue
        hit = len(expected & selected)
        precisions.append(hit / len(expected))
    if precisions:
        metrics["retrieval_precision"] = round(sum(precisions) / len(precisions), 4)

    # Distractor resistance
    resistances = []
    for r in tests:
        distractors = set(r.get("distractor_tags", []) or r.get("distractor_memory_tags", []))
        if not distractors:
            continue
        selected = set(r.get("selected_tags", []))
        if not selected:
            resistances.append(1.0)
            continue
        distractor_hits = len(distractors & selected)
        resistances.append(1.0 - distractor_hits / len(selected))
    if resistances:
        metrics["distractor_resistance"] = round(sum(resistances) / len(resistances), 4)

    # Recall hit rate (for long_horizon_recall)
    recall_tasks = [r for r in tests if r.get("task_type") == "recall_test" or "expected_in_context" in r]
    if recall_tasks:
        hits = 0
        for r in recall_tasks:
            expected_words = [w.lower() for w in r.get("expected_in_context", [])]
            # Check if expected words appear in any selected memory content
            all_content = " ".join(
                str(tag) for tag in r.get("selected_tags", [])
            ).lower()
            # Also check the actual response
            all_content += " " + r.get("response", "").lower()
            if expected_words and any(w in all_content for w in expected_words):
                hits += 1
        metrics["recall_hit_rate"] = round(hits / len(recall_tasks), 4) if recall_tasks else 0.0

    # State-dependent retrieval: did the activated memories match the expected
    # state-conditioned set? state_match_rate = fraction of test tasks where
    # at least one expected_memory_id was activated AND no wrong_memory_id was.
    state_tasks = [r for r in tests if "expected_memory_ids" in r and "wrong_memory_ids" in r]
    if state_tasks:
        matched = 0
        for r in state_tasks:
            expected_ids = set(r.get("expected_memory_ids") or [])
            wrong_ids = set(r.get("wrong_memory_ids") or [])
            selected = set(r.get("selected_memory_ids") or [])
            expected_hits = len(expected_ids & selected)
            wrong_hits = len(wrong_ids & selected)
            # Strict: more correct than wrong
            if expected_hits > wrong_hits:
                matched += 1
        metrics["state_match_rate"] = round(matched / len(state_tasks), 4)

    # Sense accuracy (for ambiguity benchmark)
    sense_tasks = [r for r in tests if "expected_sense" in r]
    if sense_tasks:
        correct = 0
        for r in sense_tasks:
            expected_tags = set(r.get("expected_tags_in_context", []))
            selected = set(r.get("selected_tags", []))
            if expected_tags and len(expected_tags & selected) > 0:
                correct += 1
        metrics["sense_accuracy"] = round(correct / len(sense_tasks), 4)

    # Context efficiency (memories activated — lower is more efficient for same quality)
    mem_counts = [r.get("memories_activated", 0) for r in tests]
    metrics["avg_memories_activated"] = round(sum(mem_counts) / len(mem_counts), 2) if mem_counts else 0

    # Constellation rate (how often did PEP find constellations)
    c_counts = [r.get("constellations", 0) for r in tests]
    metrics["constellation_rate"] = round(sum(1 for c in c_counts if c > 0) / len(c_counts), 4) if c_counts else 0

    # Fallback rate
    fallbacks = [r.get("fallback", False) for r in tests]
    metrics["strategic_fallback_rate"] = round(sum(1 for f in fallbacks if f) / len(fallbacks), 4)

    return metrics


def compare_policies(all_results: dict[str, list[dict]]) -> dict[str, dict[str, float]]:
    """Run evaluate() for each policy and return a comparison table.

    Input: {policy_name: [results]}
    Output: {policy_name: {metric: value}}
    """
    return {name: evaluate(results) for name, results in all_results.items()}


def format_comparison(comparison: dict[str, dict[str, float]]) -> str:
    """Pretty-print a comparison table as aligned text."""
    if not comparison:
        return "(no results)"

    all_metrics = sorted({m for scores in comparison.values() for m in scores})
    policies = sorted(comparison.keys())

    # Header
    col_width = max(24, max(len(m) for m in all_metrics) + 2)
    policy_width = max(16, max(len(p) for p in policies) + 2)
    header = f"{'metric':<{col_width}}" + "".join(f"{p:>{policy_width}}" for p in policies)
    lines = [header, "-" * len(header)]

    for metric in all_metrics:
        row = f"{metric:<{col_width}}"
        for p in policies:
            val = comparison[p].get(metric)
            if val is None:
                row += f"{'—':>{policy_width}}"
            else:
                row += f"{val:>{policy_width}.4f}"
            # TODO: highlight best per row
        lines.append(row)

    return "\n".join(lines)
