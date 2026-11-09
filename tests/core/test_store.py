"""MemoryStore round-trip tests."""

from __future__ import annotations

from pep.memory.store import MemoryStore
from pep.schemas.memory_schema import Link, MemoryObject
from pep.schemas.state_schema import State


def test_upsert_and_get_memory() -> None:
    store = MemoryStore(":memory:")
    m = MemoryObject(
        core="Prediction reduces storage and reaction cost.",
        tags=["prediction", "storage", "reaction"],
        brightness=0.7,
    )
    store.upsert_memory(m)

    fetched = store.get_memory(m.id)
    assert fetched is not None
    assert fetched.core == m.core
    assert fetched.brightness == 0.7
    assert "prediction" in fetched.tags


def test_links_round_trip() -> None:
    store = MemoryStore(":memory:")
    m1 = MemoryObject(core="A", tags=["a"])
    m2 = MemoryObject(core="B", tags=["b"], links=[Link(to_id=m1.id, weight=0.8)])
    store.upsert_memory(m1)
    store.upsert_memory(m2)

    neighbors = store.neighbors(m2.id)
    assert len(neighbors) == 1
    assert neighbors[0].to_id == m1.id
    assert neighbors[0].weight == 0.8


def test_touch_memory_increments_activation_and_drift() -> None:
    store = MemoryStore(":memory:")
    m = MemoryObject(core="touch me", brightness=0.5)
    store.upsert_memory(m)

    store.touch_memory(m.id)
    fetched = store.get_memory(m.id)
    assert fetched is not None
    assert fetched.activation_count == 1
    assert fetched.brightness > 0.5
    assert fetched.drift_score > 0.0


def test_state_log_round_trip() -> None:
    store = MemoryStore(":memory:")
    s1 = State(urgency=0.7, exploration=0.4)
    store.log_state("sess1", 1, s1)

    latest = store.latest_state("sess1")
    assert latest.urgency == 0.7
    assert latest.exploration == 0.4
    assert store.turn_count("sess1") == 1
