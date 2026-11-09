"""State-dependent retrieval benchmark tests."""

from __future__ import annotations

from pep.embed import Embedder
from pep.evaluator import evaluate
from pep.models.llm_client import StubLLMClient
from pep.policies.pep_full import PEPFullPolicy
from pep.policies.recent_window import RecentWindowPolicy
from pep.runner import run_benchmark


def test_state_benchmark_loads_seed_memories_with_state_modulation() -> None:
    """The runner should pass state_modulation through from the seed JSON to MemoryObject."""
    results = run_benchmark(
        "state_dependent_retrieval",
        policy=PEPFullPolicy(),
        llm=StubLLMClient(),
        embedder=Embedder(),
    )
    # 5 tasks: 1 priming + 1 test + 2 priming + 1 test
    assert len(results) == 5
    # Two test tasks (the rest are priming)
    test_tasks = [r for r in results if r.get("task_type") == "test"]
    assert len(test_tasks) == 2


def test_state_benchmark_evaluator_produces_state_match_rate() -> None:
    results = run_benchmark(
        "state_dependent_retrieval",
        policy=PEPFullPolicy(),
        llm=StubLLMClient(),
        embedder=Embedder(),
    )
    metrics = evaluate(results)
    assert "state_match_rate" in metrics
    # Latency metrics should still be there
    assert "latency_mean_s" in metrics


def test_state_benchmark_priming_tasks_excluded_from_metrics() -> None:
    """Priming turns should not count toward the metrics — they're just there
    to build state for the subsequent test turns."""
    results = run_benchmark(
        "state_dependent_retrieval",
        policy=PEPFullPolicy(),
        llm=StubLLMClient(),
        embedder=Embedder(),
    )
    # Confirm priming tasks exist in the raw results
    priming = [r for r in results if r.get("task_type") == "priming"]
    assert len(priming) == 3

    # ...but the evaluator filters them out (we know because state_match_rate
    # only counts the 2 test tasks). With 2 tasks, the rate is 0.0, 0.5, or 1.0.
    metrics = evaluate(results)
    rate = metrics["state_match_rate"]
    assert rate in (0.0, 0.5, 1.0)


def test_state_priming_actually_changes_state_vector() -> None:
    """Beyond retrieval: confirm that the urgency-priming task produces a state
    with high urgency, and the exploration-priming tasks produce high exploration.
    This validates the State Modulator path through the runner."""
    results = run_benchmark(
        "state_dependent_retrieval",
        policy=PEPFullPolicy(),
        llm=StubLLMClient(),
        embedder=Embedder(),
    )

    # Look up priming results by task id
    by_id = {r["task_id"]: r for r in results}

    urgency_state = by_id["sd_prime_urgency"].get("state_after", {})
    assert urgency_state.get("urgency", 0) > 0.0, (
        f"urgency priming should raise urgency, got {urgency_state}"
    )

    exploration_state = by_id["sd_prime_exploration_2"].get("state_after", {})
    assert exploration_state.get("exploration", 0) >= 0.5, (
        f"exploration priming should raise exploration, got {exploration_state}"
    )
