"""Tests for the per-turn decay (PTO 2G option (c) — empirical reinforcement)."""

from __future__ import annotations

import pytest

from pep.memory.store import MemoryStore
from pep.schemas.memory_schema import MemoryObject


def test_decay_lowers_brightness_of_unused_memories() -> None:
    store = MemoryStore(":memory:")
    store.upsert_memory(MemoryObject(id="mem_a", core="A", brightness=0.6))
    store.upsert_memory(MemoryObject(id="mem_b", core="B", brightness=0.6))

    affected = store.decay_unused_memories(decay=0.05, exclude_ids=set())
    assert affected == 2

    a = store.get_memory("mem_a")
    b = store.get_memory("mem_b")
    assert a is not None and b is not None
    assert a.brightness == pytest.approx(0.55)
    assert b.brightness == pytest.approx(0.55)


def test_decay_excludes_specified_ids() -> None:
    """Memories that were just activated should NOT be decayed."""
    store = MemoryStore(":memory:")
    store.upsert_memory(MemoryObject(id="mem_kept", core="kept", brightness=0.7))
    store.upsert_memory(MemoryObject(id="mem_decayed", core="decayed", brightness=0.7))

    affected = store.decay_unused_memories(decay=0.1, exclude_ids={"mem_kept"})
    assert affected == 1

    kept = store.get_memory("mem_kept")
    decayed = store.get_memory("mem_decayed")
    assert kept is not None and decayed is not None
    assert kept.brightness == pytest.approx(0.7)  # untouched
    assert decayed.brightness == pytest.approx(0.6)


def test_decay_does_not_drop_below_floor() -> None:
    """Decay should never push brightness below the configured floor."""
    store = MemoryStore(":memory:")
    store.upsert_memory(MemoryObject(id="mem_dim", core="dim", brightness=0.06))

    store.decay_unused_memories(decay=0.5, floor=0.05, exclude_ids=set())
    dim = store.get_memory("mem_dim")
    assert dim is not None
    assert dim.brightness == pytest.approx(0.05)


def test_reinforcement_then_decay_net_positive_for_used_memory() -> None:
    """A memory that gets touched (activated) should net come out brighter
    than one that doesn't, after both reinforcement and decay run."""
    store = MemoryStore(":memory:")
    store.upsert_memory(MemoryObject(id="mem_used", core="used", brightness=0.5))
    store.upsert_memory(MemoryObject(id="mem_unused", core="unused", brightness=0.5))

    # Simulate: mem_used is activated, mem_unused is not
    store.touch_memory("mem_used")  # +0.05 brightness
    store.decay_unused_memories(decay=0.005, exclude_ids={"mem_used"})

    used = store.get_memory("mem_used")
    unused = store.get_memory("mem_unused")
    assert used is not None and unused is not None
    assert used.brightness > unused.brightness
    assert used.activation_count == 1
