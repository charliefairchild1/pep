"""Multi-scale coherence experiment tests.

Verifies the Spearman implementation, the per-memory scorer, and the
measure_coherence pipeline against hand-built fixtures with known
coherent and incoherent groupings.
"""

from __future__ import annotations

import pytest

from pep.analysis.coherence import (
    format_report,
    measure_coherence,
    score_memory,
    spearman,
)
from pep.embed import Embedder
from pep.memory.store import MemoryStore
from pep.schemas.memory_schema import MemoryObject


# ---- Spearman ----

def test_spearman_perfect_positive() -> None:
    assert spearman([1.0, 2.0, 3.0, 4.0], [10.0, 20.0, 30.0, 40.0]) == pytest.approx(1.0)


def test_spearman_perfect_negative() -> None:
    assert spearman([1.0, 2.0, 3.0, 4.0], [40.0, 30.0, 20.0, 10.0]) == pytest.approx(-1.0)


def test_spearman_uncorrelated_returns_near_zero() -> None:
    # Construct values where rank correlation is exactly 0
    rho = spearman([1.0, 2.0, 3.0, 4.0], [3.0, 1.0, 4.0, 2.0])
    assert -0.5 < rho < 0.5


def test_spearman_handles_constant_input() -> None:
    # When one side has zero variance, correlation is undefined → return 0
    assert spearman([1.0, 1.0, 1.0], [1.0, 2.0, 3.0]) == 0.0


# ---- score_memory ----

def test_score_memory_higher_for_tag_match() -> None:
    embedder = Embedder()
    from datetime import datetime
    now = datetime.utcnow()
    matching = MemoryObject(core="prediction matters", tags=["prediction"], brightness=0.5)
    unrelated = MemoryObject(core="something else", tags=["unrelated"], brightness=0.5)

    s_match = score_memory(
        matching, cue_tags={"prediction"}, query_vec=None,
        embedder=embedder, now=now,
    )
    s_no = score_memory(
        unrelated, cue_tags={"prediction"}, query_vec=None,
        embedder=embedder, now=now,
    )
    assert s_match > s_no


# ---- measure_coherence ----

def test_coherence_high_when_categories_match_relevance() -> None:
    """Construct a store where the highly-relevant memories are all in one
    category and irrelevant ones are in another. Coherence should be high."""
    store = MemoryStore(":memory:")
    embedder = Embedder()

    # 4 highly-relevant memories — all about "prediction"
    relevant_ids = []
    for i in range(4):
        m = MemoryObject(
            id=f"mem_rel_{i}",
            core=f"prediction is important #{i}",
            tags=["prediction", "important"],
            brightness=0.8,
        )
        store.upsert_memory(m)
        relevant_ids.append(m.id)

    # 4 irrelevant memories — all about chess
    irrelevant_ids = []
    for i in range(4):
        m = MemoryObject(
            id=f"mem_irr_{i}",
            core=f"chess opening #{i}",
            tags=["chess", "opening"],
            brightness=0.4,
        )
        store.upsert_memory(m)
        irrelevant_ids.append(m.id)

    # Two categories, each holds one cluster
    store.upsert_category(
        category_id="cat_pred", name="prediction", member_count=4,
        top_tags=["prediction", "important"],
    )
    store.upsert_category(
        category_id="cat_chess", name="chess", member_count=4,
        top_tags=["chess", "opening"],
    )
    for mid in relevant_ids:
        store.assign_memory_to_category(mid, "cat_pred")
    for mid in irrelevant_ids:
        store.assign_memory_to_category(mid, "cat_chess")

    report = measure_coherence(store, embedder, "prediction important")

    assert report.n_memories == 8
    assert report.n_categories == 2
    assert report.n_memories_in_categories == 8

    # The "prediction" category should outrank the "chess" category
    assert report.category_mean_scores["cat_pred"] > report.category_mean_scores["cat_chess"]

    # Coherence should be strongly positive — relevant memories ARE in the
    # category that scores higher.
    assert report.coherence_mean > 0.8


def test_coherence_low_when_categories_are_random() -> None:
    """Construct a store where category assignments are scrambled — relevant
    and irrelevant memories mixed in both categories. Coherence should be low."""
    store = MemoryStore(":memory:")
    embedder = Embedder()

    # Create 6 memories with varying relevance (alternating tags)
    for i in range(6):
        tags = ["prediction"] if i % 2 == 0 else ["chess"]
        store.upsert_memory(MemoryObject(
            id=f"mem_{i}",
            core=f"item {i}",
            tags=tags,
            brightness=0.5,
        ))

    # Two categories, but each gets a deliberately mixed bag
    store.upsert_category(
        category_id="cat_a", name="mixed_a", member_count=3,
        top_tags=["mixed"],
    )
    store.upsert_category(
        category_id="cat_b", name="mixed_b", member_count=3,
        top_tags=["mixed"],
    )
    # Scramble: each cat has one prediction memory and two chess memories
    store.assign_memory_to_category("mem_0", "cat_a")  # prediction
    store.assign_memory_to_category("mem_1", "cat_a")  # chess
    store.assign_memory_to_category("mem_3", "cat_a")  # chess
    store.assign_memory_to_category("mem_2", "cat_b")  # prediction
    store.assign_memory_to_category("mem_5", "cat_b")  # chess
    store.assign_memory_to_category("mem_4", "cat_b")  # prediction

    report = measure_coherence(store, embedder, "prediction")

    # When categories are scrambled, the per-category means should be similar,
    # so the rank correlation between memory and category rank should be weak.
    # Allow a wide tolerance — pseudo-embeddings add noise.
    assert abs(report.coherence_mean) < 0.7


def test_format_report_handles_empty_store() -> None:
    store = MemoryStore(":memory:")
    embedder = Embedder()
    report = measure_coherence(store, embedder, "anything")
    text = format_report(report)
    assert "Memories: 0" in text
    assert "empty store" in text


def test_format_report_handles_no_categories() -> None:
    store = MemoryStore(":memory:")
    embedder = Embedder()
    store.upsert_memory(MemoryObject(core="lone memory", tags=["solo"]))
    report = measure_coherence(store, embedder, "solo")
    text = format_report(report)
    assert "no categories" in text or "no memories are assigned" in text
