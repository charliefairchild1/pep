"""Tests for the trajectory score validation experiment (research note §8.1)."""

from __future__ import annotations

import pytest

from pep.analysis.trajectory_validation import (
    format_report,
    validate_trajectory_predictions,
)
from pep.memory.store import MemoryStore
from pep.schemas.memory_schema import MemoryObject


def _make_memory(
    mid: str, trajectory: float | None, activation_count: int = 0,
) -> MemoryObject:
    """Build a memory with an optional stored trajectory and a given count."""
    future_use = {"trajectory_at_storage": trajectory} if trajectory is not None else {}
    return MemoryObject(
        id=mid,
        core=f"memory {mid}",
        tags=["test"],
        brightness=0.5,
        future_use=future_use,
        activation_count=activation_count,
    )


def test_empty_store_returns_helpful_note() -> None:
    store = MemoryStore(":memory:")
    report = validate_trajectory_predictions(store)
    assert report.n_memories_total == 0
    assert report.n_memories_with_trajectory == 0
    assert "need at least 2" in report.notes or "have 0" in report.notes


def test_only_memories_with_trajectory_score_are_counted() -> None:
    store = MemoryStore(":memory:")
    store.upsert_memory(_make_memory("m1", trajectory=0.8, activation_count=5))
    store.upsert_memory(_make_memory("m2", trajectory=0.5, activation_count=2))
    store.upsert_memory(_make_memory("m3", trajectory=None, activation_count=10))
    store.upsert_memory(_make_memory("m4", trajectory=0.2, activation_count=0))

    report = validate_trajectory_predictions(store)
    assert report.n_memories_total == 4
    assert report.n_memories_with_trajectory == 3
    # m3 is excluded so the mean uses only m1, m2, m4
    assert report.mean_trajectory == pytest.approx((0.8 + 0.5 + 0.2) / 3, abs=0.001)


def test_high_correlation_when_trajectory_predicts_actual() -> None:
    """Construct a store where higher predicted trajectory means higher
    actual reactivation count. Spearman ρ should be near +1."""
    store = MemoryStore(":memory:")
    store.upsert_memory(_make_memory("m1", trajectory=0.1, activation_count=1))
    store.upsert_memory(_make_memory("m2", trajectory=0.3, activation_count=2))
    store.upsert_memory(_make_memory("m3", trajectory=0.5, activation_count=4))
    store.upsert_memory(_make_memory("m4", trajectory=0.7, activation_count=8))
    store.upsert_memory(_make_memory("m5", trajectory=0.9, activation_count=15))

    report = validate_trajectory_predictions(store)
    assert report.correlation > 0.9
    assert report.correlation_n == 5


def test_negative_correlation_when_trajectory_anti_predicts() -> None:
    """If higher predicted trajectory means LOWER actual reactivation, ρ
    should be near -1. (This would be alarming if it happened in real data.)"""
    store = MemoryStore(":memory:")
    store.upsert_memory(_make_memory("m1", trajectory=0.1, activation_count=10))
    store.upsert_memory(_make_memory("m2", trajectory=0.3, activation_count=8))
    store.upsert_memory(_make_memory("m3", trajectory=0.5, activation_count=4))
    store.upsert_memory(_make_memory("m4", trajectory=0.7, activation_count=2))
    store.upsert_memory(_make_memory("m5", trajectory=0.9, activation_count=1))

    report = validate_trajectory_predictions(store)
    assert report.correlation < -0.9


def test_top_predicted_and_top_actually_used_lists() -> None:
    store = MemoryStore(":memory:")
    store.upsert_memory(_make_memory("low_pred_high_actual", trajectory=0.1, activation_count=20))
    store.upsert_memory(_make_memory("high_pred_low_actual", trajectory=0.95, activation_count=1))
    store.upsert_memory(_make_memory("mid", trajectory=0.5, activation_count=5))

    report = validate_trajectory_predictions(store)
    # Top by predicted should put high_pred_low_actual first
    assert report.top_predicted[0]["id"] == "high_pred_low_actual"
    # Top by actual should put low_pred_high_actual first
    assert report.top_actually_used[0]["id"] == "low_pred_high_actual"


def test_source_filter_includes_only_matching_memories() -> None:
    """When source='llm' is passed, only memories with trajectory_source='llm'
    should be counted. Mixed populations should not contaminate each other."""
    store = MemoryStore(":memory:")
    # Two LLM-scored memories
    store.upsert_memory(MemoryObject(
        id="llm_1", core="x", tags=["test"], brightness=0.5,
        future_use={"trajectory_at_storage": 0.9}, activation_count=10,
        trajectory_source="llm",
    ))
    store.upsert_memory(MemoryObject(
        id="llm_2", core="x", tags=["test"], brightness=0.5,
        future_use={"trajectory_at_storage": 0.3}, activation_count=2,
        trajectory_source="llm",
    ))
    # Two heuristic-scored memories
    store.upsert_memory(MemoryObject(
        id="heu_1", core="x", tags=["test"], brightness=0.5,
        future_use={"trajectory_at_storage": 0.5}, activation_count=5,
        trajectory_source="heuristic",
    ))
    store.upsert_memory(MemoryObject(
        id="heu_2", core="x", tags=["test"], brightness=0.5,
        future_use={"trajectory_at_storage": 0.7}, activation_count=4,
        trajectory_source="heuristic",
    ))

    llm_report = validate_trajectory_predictions(store, source="llm")
    heu_report = validate_trajectory_predictions(store, source="heuristic")
    all_report = validate_trajectory_predictions(store)

    assert llm_report.n_memories_with_trajectory == 2
    assert heu_report.n_memories_with_trajectory == 2
    assert all_report.n_memories_with_trajectory == 4
    assert llm_report.source_filter == "llm"
    assert heu_report.source_filter == "heuristic"
    assert all_report.source_filter is None


def test_compare_trajectory_sources_returns_three_reports() -> None:
    from pep.analysis.trajectory_validation import compare_trajectory_sources

    store = MemoryStore(":memory:")
    store.upsert_memory(MemoryObject(
        id="llm_a", core="x", tags=[],
        future_use={"trajectory_at_storage": 0.8}, activation_count=4,
        trajectory_source="llm",
    ))
    store.upsert_memory(MemoryObject(
        id="llm_b", core="x", tags=[],
        future_use={"trajectory_at_storage": 0.4}, activation_count=2,
        trajectory_source="llm",
    ))
    store.upsert_memory(MemoryObject(
        id="heu_a", core="x", tags=[],
        future_use={"trajectory_at_storage": 0.6}, activation_count=3,
        trajectory_source="heuristic",
    ))

    result = compare_trajectory_sources(store)
    assert "all" in result
    assert "llm" in result
    assert "heuristic" in result
    assert result["llm"].n_memories_with_trajectory == 2
    assert result["heuristic"].n_memories_with_trajectory == 1
    assert result["all"].n_memories_with_trajectory == 3


def test_format_report_renders_text() -> None:
    store = MemoryStore(":memory:")
    store.upsert_memory(_make_memory("m1", trajectory=0.5, activation_count=2))
    store.upsert_memory(_make_memory("m2", trajectory=0.9, activation_count=8))

    report = validate_trajectory_predictions(store)
    text = format_report(report)
    assert "Trajectory score validation" in text
    assert "Spearman" in text
    assert "Top 5 by predicted trajectory" in text
