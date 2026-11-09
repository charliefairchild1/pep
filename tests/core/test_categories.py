"""Category Engine + Consolidation tests."""

from __future__ import annotations

from pep.core.categories import (
    discover_categories,
    decay_empty_categories,
    merge_similar_categories,
    run_category_engine,
)
from pep.core.consolidation import (
    merge_near_duplicates,
    generate_summary_memories,
    run_consolidation,
)
from pep.memory.store import MemoryStore
from pep.schemas.memory_schema import MemoryObject


def _make_cluster(store: MemoryStore, prefix: str, tags: list[str], n: int = 4) -> None:
    for i in range(n):
        store.upsert_memory(MemoryObject(
            id=f"mem_{prefix}_{i}",
            core=f"{prefix} memory #{i}",
            tags=tags + [f"{prefix}_specific_{i}"],
            brightness=0.5,
        ))


def test_discover_creates_category_from_cluster() -> None:
    store = MemoryStore(":memory:")
    _make_cluster(store, "predict", ["prediction", "storage", "pep"])

    new_ids = discover_categories(store)
    assert len(new_ids) >= 1

    cats = store.list_categories()
    assert len(cats) >= 1
    cat = cats[0]
    assert cat["member_count"] >= 3
    assert "prediction" in cat["top_tags"]

    # Members should be assigned
    members = store.category_members(cat["id"])
    assert len(members) >= 3


def test_discover_creates_separate_categories_for_different_clusters() -> None:
    store = MemoryStore(":memory:")
    _make_cluster(store, "predict", ["prediction", "storage", "pep"])
    _make_cluster(store, "chess", ["chess", "bishop", "opening"])

    new_ids = discover_categories(store)
    assert len(new_ids) == 2

    cats = store.list_categories()
    names = {c["name"] for c in cats}
    # Each cluster should have its own category with its own name
    assert len(names) == 2


def test_merge_combines_similar_categories() -> None:
    store = MemoryStore(":memory:")
    # Create two categories with nearly identical tags
    store.upsert_category(
        category_id="cat_a", name="a", member_count=3,
        top_tags=["prediction", "storage", "pep"],
    )
    store.upsert_category(
        category_id="cat_b", name="b", member_count=3,
        top_tags=["prediction", "storage", "pep", "memory"],  # Jaccard 3/4 = 0.75 > 0.6
    )
    # Need members for the merge to work on
    for i in range(3):
        m = MemoryObject(id=f"m_a{i}", core=f"a{i}", tags=["prediction", "storage"])
        store.upsert_memory(m)
        store.assign_memory_to_category(m.id, "cat_a")
    for i in range(3):
        m = MemoryObject(id=f"m_b{i}", core=f"b{i}", tags=["prediction", "storage"])
        store.upsert_memory(m)
        store.assign_memory_to_category(m.id, "cat_b")

    merged = merge_similar_categories(store)
    assert merged >= 1
    # One category should have absorbed the other
    remaining = store.list_categories()
    assert len(remaining) == 1


def test_decay_removes_empty_categories() -> None:
    store = MemoryStore(":memory:")
    store.upsert_category(category_id="cat_empty", name="empty", member_count=0, top_tags=[])
    assert len(store.list_categories()) == 1

    deleted = decay_empty_categories(store)
    assert deleted == 1
    assert len(store.list_categories()) == 0


def test_merge_near_duplicates() -> None:
    store = MemoryStore(":memory:")
    # Two memories with identical first 100 chars of core and overlapping tags
    core = "Prediction reduces storage and reaction cost by encoding only the residual error from expected vs actual input."
    store.upsert_memory(MemoryObject(
        id="dup1", core=core, tags=["prediction", "storage", "residual"], brightness=0.6,
    ))
    store.upsert_memory(MemoryObject(
        id="dup2", core=core, tags=["prediction", "storage", "residual", "reaction"], brightness=0.5,
    ))

    merged = merge_near_duplicates(store)
    assert merged == 1
    remaining = store.all_memories()
    assert len(remaining) == 1
    # The survivor should have the higher brightness
    assert remaining[0].brightness == 0.6


def test_generate_summary_memories() -> None:
    store = MemoryStore(":memory:")
    _make_cluster(store, "predict", ["prediction", "storage", "pep"], n=6)
    # Need a category first
    discover_categories(store)
    cats = store.list_categories()
    assert len(cats) >= 1

    created = generate_summary_memories(store)
    assert created >= 1

    # The summary should be in the store
    all_mems = store.all_memories()
    summaries = [m for m in all_mems if m.source_type == "summary"]
    assert len(summaries) >= 1
    assert "prediction" in summaries[0].core.lower()


def test_reconsolidate_skips_low_drift_memories() -> None:
    """Memories with drift_score below the threshold should be left alone."""
    from pep.core.consolidation import (
        RECONSOLIDATION_DRIFT_THRESHOLD,
        reconsolidate_drifted_memories,
    )

    store = MemoryStore(":memory:")
    store.upsert_memory(MemoryObject(
        id="mem_low",
        core="A memory with low drift",
        tags=["test"],
        brightness=0.5,
        drift_score=0.1,  # below the default threshold of 0.4
    ))

    affected = reconsolidate_drifted_memories(store, llm=None)
    assert affected == 0
    # The memory should still have its original drift score
    fetched = store.get_memory("mem_low")
    assert fetched is not None
    assert fetched.drift_score == 0.1


def test_reconsolidate_resets_drift_for_high_drift_memories() -> None:
    """A memory whose drift exceeds the threshold should have drift reset to 0
    after reconsolidation, even on the heuristic path (no LLM)."""
    from pep.core.consolidation import reconsolidate_drifted_memories

    store = MemoryStore(":memory:")
    store.upsert_memory(MemoryObject(
        id="mem_drifted",
        core="A heavily-used memory that has accumulated drift",
        tags=["important"],
        brightness=0.8,
        drift_score=0.6,  # above 0.4 default threshold
        confidence=0.9,
    ))

    affected = reconsolidate_drifted_memories(store, llm=None)
    assert affected == 1

    fetched = store.get_memory("mem_drifted")
    assert fetched is not None
    assert fetched.drift_score == 0.0
    # Confidence should be bumped slightly because we just refreshed
    assert fetched.confidence >= 0.95
    # Core text should be preserved on the heuristic path
    assert "heavily-used memory" in fetched.core


def test_reconsolidate_uses_llm_when_available() -> None:
    """When a real LLM is provided, reconsolidate should regenerate faces
    via _llm_encode and merge any new tags with the existing ones."""
    from pep.core.consolidation import reconsolidate_drifted_memories

    class _FakeLLM:
        name = "fake"
        is_real = True

        def complete(self, packet):
            return "ok"

        def stream_complete(self, packet):
            yield "ok"

        def complete_raw(self, *, system, user):
            return "ok"

        def support(self, *, system, user, model_tier="cheap"):
            # Mimic the multi-face encode response shape
            return (
                '{"core": "Refreshed memory about the topic.",'
                ' "tags": ["important", "fresh", "rebuilt"],'
                ' "faces": {"semantic": "the canonical refreshed content",'
                '           "action": "act on this knowledge"},'
                ' "fold_weights": {"semantic": 0.9, "action": 0.7}}'
            )

    store = MemoryStore(":memory:")
    store.upsert_memory(MemoryObject(
        id="mem_drifted_llm",
        core="Original content that has drifted",
        tags=["original"],
        brightness=0.7,
        drift_score=0.8,
    ))

    affected = reconsolidate_drifted_memories(store, llm=_FakeLLM())
    assert affected == 1

    fetched = store.get_memory("mem_drifted_llm")
    assert fetched is not None
    # Core was regenerated by the LLM
    assert "Refreshed memory" in fetched.core
    # New faces were rebuilt
    assert "semantic" in fetched.faces
    assert "action" in fetched.faces
    # Original tag is preserved (heuristic merge keeps the floor)
    assert "original" in fetched.tags
    # New tags are also present
    assert "rebuilt" in fetched.tags
    # Drift reset
    assert fetched.drift_score == 0.0


def test_consolidation_run_includes_reconsolidation_count() -> None:
    """run_consolidation() should report how many drifted memories were
    reconsolidated as part of its summary dict."""
    from pep.core.consolidation import run_consolidation

    store = MemoryStore(":memory:")
    store.upsert_memory(MemoryObject(
        id="mem_high_drift_a",
        core="content a",
        tags=["test"],
        brightness=0.5,
        drift_score=0.5,
    ))
    store.upsert_memory(MemoryObject(
        id="mem_high_drift_b",
        core="content b",
        tags=["test"],
        brightness=0.5,
        drift_score=0.7,
    ))
    store.upsert_memory(MemoryObject(
        id="mem_low_drift",
        core="content c",
        tags=["test"],
        brightness=0.5,
        drift_score=0.1,
    ))

    results = run_consolidation(store, llm=None)
    assert "reconsolidated_drifted" in results
    assert results["reconsolidated_drifted"] == 2  # two above threshold


def test_redistill_legacy_memories_rewrites_verbose_cores() -> None:
    """Memories with cores in the legacy USER:/ASSISTANT: paragraph format
    should be rewritten by the consolidation pass into distilled cores."""
    from pep.core.consolidation import redistill_legacy_memories

    store = MemoryStore(":memory:")
    legacy_core = (
        "USER: How does prediction work in PEP?\n"
        "ASSISTANT: Prediction in PEP is the mechanism by which the system "
        "anticipates likely user intent before the full input is processed, "
        "allowing memory to be pre-loaded and context to be staged in advance."
    )
    store.upsert_memory(MemoryObject(
        id="mem_legacy",
        core=legacy_core,
        faces={"semantic": legacy_core[:300]},
        tags=["prediction", "pep"],
        brightness=0.5,
    ))

    rewritten = redistill_legacy_memories(store)
    assert rewritten == 1
    fetched = store.get_memory("mem_legacy")
    assert fetched is not None
    # The old USER:/ASSISTANT: framing should be gone
    assert "USER:" not in fetched.core
    assert "ASSISTANT:" not in fetched.core
    # The substantive content should remain
    assert "prediction" in fetched.core.lower()


def test_redistill_legacy_skips_already_distilled_memories() -> None:
    """Memories whose core doesn't match the legacy verbose pattern should
    be left untouched by the redistill pass."""
    from pep.core.consolidation import redistill_legacy_memories

    store = MemoryStore(":memory:")
    distilled = "Prediction reduces storage by encoding only the residual error."
    store.upsert_memory(MemoryObject(
        id="mem_distilled",
        core=distilled,
        tags=["prediction"],
        brightness=0.5,
    ))

    rewritten = redistill_legacy_memories(store)
    assert rewritten == 0
    fetched = store.get_memory("mem_distilled")
    assert fetched is not None
    assert fetched.core == distilled


def test_full_consolidation_runs_without_error() -> None:
    store = MemoryStore(":memory:")
    _make_cluster(store, "predict", ["prediction", "storage", "pep"], n=6)
    _make_cluster(store, "chess", ["chess", "bishop", "opening"], n=4)

    results = run_consolidation(store)
    assert "categories_created" in results
    assert "duplicates_merged" in results
    assert results["categories_created"] >= 2
