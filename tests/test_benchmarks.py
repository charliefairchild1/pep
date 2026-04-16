"""Benchmark runner + evaluator + policy tests."""

from __future__ import annotations

from pep.embed import Embedder
from pep.evaluator import compare_policies, evaluate, format_comparison
from pep.models.llm_client import StubLLMClient
from pep.policies.pep_full import PEPFullPolicy
from pep.policies.recent_window import RecentWindowPolicy
from pep.policies.semantic_topk import SemanticTopKPolicy
from pep.runner import run_benchmark


def test_recent_window_policy_runs_a_benchmark() -> None:
    results = run_benchmark(
        "ambiguity",
        policy=RecentWindowPolicy(),
        llm=StubLLMClient(),
        embedder=Embedder(),
    )
    assert len(results) > 0
    for r in results:
        assert r["policy"] == "recent_window"
        assert "selected_memory_ids" in r
        assert "latency_s" in r


def test_semantic_topk_policy_runs_a_benchmark() -> None:
    results = run_benchmark(
        "ambiguity",
        policy=SemanticTopKPolicy(),
        llm=StubLLMClient(),
        embedder=Embedder(),
    )
    assert len(results) > 0
    for r in results:
        assert r["policy"] == "semantic_topk"
        # Semantic top-k should at least try to retrieve something
        assert r["memories_activated"] >= 0


def test_pep_full_policy_runs_a_benchmark() -> None:
    results = run_benchmark(
        "ambiguity",
        policy=PEPFullPolicy(),
        llm=StubLLMClient(),
        embedder=Embedder(),
    )
    assert len(results) > 0
    for r in results:
        assert r["policy"] == "pep_full"


def test_evaluator_produces_metrics() -> None:
    results = run_benchmark(
        "ambiguity",
        policy=PEPFullPolicy(),
        llm=StubLLMClient(),
        embedder=Embedder(),
    )
    metrics = evaluate(results)
    assert "latency_mean_s" in metrics
    assert "latency_p95_s" in metrics
    # ambiguity benchmark has expected_tags_in_context, so retrieval_precision should appear
    assert "retrieval_precision" in metrics
    assert "sense_accuracy" in metrics


def test_compare_three_policies_on_ambiguity() -> None:
    embedder = Embedder()
    llm = StubLLMClient()
    all_results = {}
    for p in (RecentWindowPolicy(), SemanticTopKPolicy(), PEPFullPolicy()):
        all_results[p.name] = run_benchmark("ambiguity", policy=p, llm=llm, embedder=embedder)

    comparison = compare_policies(all_results)
    assert set(comparison.keys()) == {"recent_window", "semantic_topk", "pep_full"}
    # Each policy should produce at least latency metrics
    for policy_name, metrics in comparison.items():
        assert "latency_mean_s" in metrics, f"{policy_name} missing latency"

    # The format_comparison function should produce a non-empty table
    table = format_comparison(comparison)
    assert "metric" in table
    assert "recent_window" in table
    assert "pep_full" in table


def test_long_horizon_recall_benchmark_runs() -> None:
    results = run_benchmark(
        "long_horizon_recall",
        policy=PEPFullPolicy(),
        llm=StubLLMClient(),
        embedder=Embedder(),
    )
    # 10 tasks total: 3 seed turns + 4 fillers + 3 recall tests
    assert len(results) == 10
    # Recall tests should have task_type "recall_test"
    recall = [r for r in results if r.get("task_type") == "recall_test"]
    assert len(recall) == 3


def test_distractor_resistance_benchmark_runs() -> None:
    results = run_benchmark(
        "distractor_resistance",
        policy=PEPFullPolicy(),
        llm=StubLLMClient(),
        embedder=Embedder(),
    )
    assert len(results) == 3
    metrics = evaluate(results)
    assert "distractor_resistance" in metrics
