"""Reactivator scoring + spreading activation + constellation tests."""

from __future__ import annotations

from pep.core.reactivator import reactivate
from pep.embed import Embedder
from pep.memory.store import MemoryStore
from pep.schemas.input_schema import InterpretedInput, Prediction
from pep.schemas.memory_schema import Link, MemoryObject
from pep.schemas.state_schema import State


def _seed_store() -> MemoryStore:
    store = MemoryStore(":memory:")
    store.upsert_memory(MemoryObject(
        id="mem_predict",
        core="Prediction reduces storage and reaction cost.",
        tags=["prediction", "storage", "reaction"],
        brightness=0.6,
    ))
    store.upsert_memory(MemoryObject(
        id="mem_chess",
        core="A bishop is worth roughly three pawns.",
        tags=["chess", "bishop", "pawn"],
        brightness=0.5,
    ))
    store.upsert_memory(MemoryObject(
        id="mem_memory",
        core="Memory is reconstructive, not a flat archive.",
        tags=["memory", "reconstruction", "brain"],
        brightness=0.55,
    ))
    return store


def test_reactivator_picks_topic_relevant_memory() -> None:
    store = _seed_store()
    embedder = Embedder()
    interpreted = InterpretedInput(
        intent="explain",
        topic="prediction storage",
        entities=["prediction", "storage"],
        task_type="explain",
    )
    prediction = Prediction(expected_context_tags=["prediction", "storage"])

    activated, trace = reactivate(
        store=store,
        embedder=embedder,
        interpreted=interpreted,
        prediction=prediction,
        state=State.neutral(),
        session_id="default",
    )

    assert len(activated) > 0
    assert trace.activated[0].memory_id == "mem_predict"


def test_reactivator_link_proximity_boosts_neighbors() -> None:
    """A memory linked to a seed should appear in the activated set via spreading."""
    store = MemoryStore(":memory:")
    store.upsert_memory(MemoryObject(
        id="mem_a",
        core="A central concept about prediction.",
        tags=["prediction"],
        brightness=0.7,
    ))
    store.upsert_memory(MemoryObject(
        id="mem_b",
        core="A linked concept with no matching tags.",
        tags=["unrelated"],
        brightness=0.5,
        links=[Link(to_id="mem_a", weight=0.9)],
    ))

    embedder = Embedder()
    interpreted = InterpretedInput(
        intent="explain", topic="prediction", entities=["prediction"], task_type="explain"
    )
    prediction = Prediction(expected_context_tags=["prediction"])
    activated, trace = reactivate(
        store=store,
        embedder=embedder,
        interpreted=interpreted,
        prediction=prediction,
        state=State.neutral(),
        session_id="default",
    )

    activated_ids = {e.memory_id for e in trace.activated}
    assert "mem_a" in activated_ids
    assert "mem_b" in activated_ids
    b_entry = next(e for e in trace.activated if e.memory_id == "mem_b")
    # Spreading activation should have given mem_b some link_proximity component
    assert b_entry.components["link_proximity"] > 0


def test_two_hop_spreading_reaches_distant_memory() -> None:
    """A memory two hops from any seed should still get a (small) activation."""
    store = MemoryStore(":memory:")
    # mem_seed: directly matches the cue
    store.upsert_memory(MemoryObject(
        id="mem_seed",
        core="Seed memory about prediction.",
        tags=["prediction"],
        brightness=0.8,
        links=[Link(to_id="mem_one_hop", weight=1.0)],
    ))
    # mem_one_hop: linked to seed, no tag overlap
    store.upsert_memory(MemoryObject(
        id="mem_one_hop",
        core="One hop away from seed.",
        tags=["unrelated_one"],
        brightness=0.4,
        links=[Link(to_id="mem_two_hop", weight=1.0)],
    ))
    # mem_two_hop: linked to one_hop only — needs two hops to be reached
    store.upsert_memory(MemoryObject(
        id="mem_two_hop",
        core="Two hops away from seed.",
        tags=["unrelated_two"],
        brightness=0.4,
    ))

    embedder = Embedder()
    interpreted = InterpretedInput(
        intent="explain", topic="prediction", entities=["prediction"], task_type="explain"
    )
    prediction = Prediction(expected_context_tags=["prediction"])
    activated, trace = reactivate(
        store=store,
        embedder=embedder,
        interpreted=interpreted,
        prediction=prediction,
        state=State.neutral(),
        session_id="default",
        hops=2,
    )

    activated_ids = {e.memory_id for e in trace.activated}
    # Both hops should be reached
    assert "mem_seed" in activated_ids
    assert "mem_one_hop" in activated_ids
    assert "mem_two_hop" in activated_ids

    # Decay should make the two-hop entry weaker than the one-hop entry
    one_hop_entry = next(e for e in trace.activated if e.memory_id == "mem_one_hop")
    two_hop_entry = next(e for e in trace.activated if e.memory_id == "mem_two_hop")
    assert one_hop_entry.components["link_proximity"] > two_hop_entry.components["link_proximity"]


def test_constellation_detected_for_mutually_linked_cluster() -> None:
    """Three memories all linked together with strong weights form a constellation."""
    store = MemoryStore(":memory:")
    store.upsert_memory(MemoryObject(
        id="mem_x",
        core="First member of a tightly linked group about prediction.",
        tags=["prediction"],
        brightness=0.7,
        links=[
            Link(to_id="mem_y", weight=0.8),
            Link(to_id="mem_z", weight=0.7),
        ],
    ))
    store.upsert_memory(MemoryObject(
        id="mem_y",
        core="Second member of the linked group.",
        tags=["prediction"],
        brightness=0.65,
        links=[Link(to_id="mem_z", weight=0.75)],
    ))
    store.upsert_memory(MemoryObject(
        id="mem_z",
        core="Third member of the linked group.",
        tags=["prediction"],
        brightness=0.6,
    ))
    # An isolated memory that should NOT be in the constellation
    store.upsert_memory(MemoryObject(
        id="mem_loner",
        core="Isolated memory about prediction.",
        tags=["prediction"],
        brightness=0.55,
    ))

    embedder = Embedder()
    interpreted = InterpretedInput(
        intent="explain", topic="prediction", entities=["prediction"], task_type="explain"
    )
    prediction = Prediction(expected_context_tags=["prediction"])
    activated, trace = reactivate(
        store=store,
        embedder=embedder,
        interpreted=interpreted,
        prediction=prediction,
        state=State.neutral(),
        session_id="default",
    )

    # Exactly one constellation should be detected, with x/y/z as members
    assert len(trace.constellations) == 1
    cstn = trace.constellations[0]
    assert set(cstn.member_ids) == {"mem_x", "mem_y", "mem_z"}
    # Cohesion should be the average of the three internal link weights
    assert cstn.cohesion > 0.6

    # All three constellation members should be tagged with the constellation id
    for mid in ("mem_x", "mem_y", "mem_z"):
        entry = next((e for e in trace.activated if e.memory_id == mid), None)
        assert entry is not None
        assert entry.constellation_id == cstn.id

    # The loner should NOT be in any constellation
    loner_entry = next((e for e in trace.activated if e.memory_id == "mem_loner"), None)
    if loner_entry is not None:
        assert loner_entry.constellation_id is None


def test_strategic_fallback_triggers_when_no_direct_match() -> None:
    """If no memory directly matches the cue, strategic search should pick up
    weaker substring/recency-based matches."""
    store = MemoryStore(":memory:")
    # Memory with a tag that *contains* the cue word but doesn't exactly match
    store.upsert_memory(MemoryObject(
        id="mem_substring",
        core="A note about predictive coding in retrieval systems.",
        tags=["predictive_coding", "retrieval"],  # cue is "prediction"
        brightness=0.5,
    ))

    embedder = Embedder()
    interpreted = InterpretedInput(
        intent="explain",
        topic="prediction",
        entities=["prediction"],
        task_type="explain",
    )
    prediction = Prediction(expected_context_tags=["prediction"])
    activated, trace = reactivate(
        store=store,
        embedder=embedder,
        interpreted=interpreted,
        prediction=prediction,
        state=State.neutral(),
        session_id="default",
    )

    # Strategic fallback should have fired
    assert trace.fallback_to_strategic_search is True
    assert trace.fallback_reason
    # And it should have actually surfaced the substring-match memory
    activated_ids = {e.memory_id for e in trace.activated}
    assert "mem_substring" in activated_ids


def test_category_descent_boosts_members_of_matching_category() -> None:
    """Members of a category whose top_tags overlap the cue should get a
    `category_match` component bonus and outrank otherwise-equivalent
    memories that don't belong to a matching category."""
    store = MemoryStore(":memory:")
    embedder = Embedder()

    # Two memories with identical tags so the only difference will be
    # category membership
    store.upsert_memory(MemoryObject(
        id="mem_in_cat",
        core="A memory inside the matching category.",
        tags=["thing", "common"],
        brightness=0.5,
    ))
    store.upsert_memory(MemoryObject(
        id="mem_outside",
        core="A memory outside any category.",
        tags=["thing", "common"],
        brightness=0.5,
    ))

    # A category whose top_tags match the cue
    store.upsert_category(
        category_id="cat_match", name="match", member_count=1,
        top_tags=["prediction", "memory"],
    )
    store.assign_memory_to_category("mem_in_cat", "cat_match")

    interpreted = InterpretedInput(
        intent="explain", topic="prediction memory thing",
        entities=["prediction", "memory", "thing"], task_type="explain",
    )
    prediction = Prediction(expected_context_tags=["prediction", "memory", "thing"])
    activated, trace = reactivate(
        store=store, embedder=embedder,
        interpreted=interpreted, prediction=prediction,
        state=State.neutral(), session_id="default",
    )

    # mem_in_cat should outrank mem_outside because of the category bonus
    in_cat_entry = next(e for e in trace.activated if e.memory_id == "mem_in_cat")
    outside_entry = next((e for e in trace.activated if e.memory_id == "mem_outside"), None)
    assert outside_entry is not None
    assert in_cat_entry.score > outside_entry.score, (
        f"in-category memory ({in_cat_entry.score}) should outrank "
        f"out-of-category memory ({outside_entry.score})"
    )
    # The boost should come from the category_match component
    assert in_cat_entry.components.get("category_match", 0.0) > 0.0
    assert outside_entry.components.get("category_match", 0.0) == 0.0


def test_descended_categories_appear_in_trace() -> None:
    """The trace should record which categories were 'descended into'."""
    store = MemoryStore(":memory:")
    embedder = Embedder()
    store.upsert_memory(MemoryObject(
        id="m1", core="x", tags=["prediction", "stuff"], brightness=0.5,
    ))
    store.upsert_category(
        category_id="cat_pred", name="pred", member_count=1,
        top_tags=["prediction", "memory"],
    )
    store.assign_memory_to_category("m1", "cat_pred")

    interpreted = InterpretedInput(
        intent="explain", topic="prediction", entities=["prediction"], task_type="explain"
    )
    prediction = Prediction(expected_context_tags=["prediction"])
    _, trace = reactivate(
        store=store, embedder=embedder,
        interpreted=interpreted, prediction=prediction,
        state=State.neutral(), session_id="default",
    )

    assert len(trace.descended_categories) >= 1
    descent = trace.descended_categories[0]
    assert descent.category_id == "cat_pred"
    assert descent.cue_match_score > 0


def test_no_category_descent_when_no_categories_match() -> None:
    """If no category has top_tags overlapping the cue, descended_categories
    should be empty and category_match should be 0 for all memories."""
    store = MemoryStore(":memory:")
    embedder = Embedder()
    store.upsert_memory(MemoryObject(
        id="m1", core="x", tags=["unrelated"], brightness=0.5,
    ))
    store.upsert_category(
        category_id="cat_chess", name="chess", member_count=1,
        top_tags=["chess", "bishop"],
    )
    store.assign_memory_to_category("m1", "cat_chess")

    interpreted = InterpretedInput(
        intent="explain", topic="prediction", entities=["prediction"], task_type="explain"
    )
    prediction = Prediction(expected_context_tags=["prediction"])
    activated, trace = reactivate(
        store=store, embedder=embedder,
        interpreted=interpreted, prediction=prediction,
        state=State.neutral(), session_id="default",
    )

    assert trace.descended_categories == []
    for entry in trace.activated:
        assert entry.components.get("category_match", 0.0) == 0.0


def test_strategic_fallback_does_not_fire_when_strong_match() -> None:
    """When the main pass produces a strong activation, fallback should NOT fire."""
    store = MemoryStore(":memory:")
    store.upsert_memory(MemoryObject(
        id="mem_strong",
        core="Direct match for the prediction cue.",
        tags=["prediction", "storage"],
        brightness=0.8,
    ))

    embedder = Embedder()
    interpreted = InterpretedInput(
        intent="explain",
        topic="prediction storage",
        entities=["prediction", "storage"],
        task_type="explain",
    )
    prediction = Prediction(expected_context_tags=["prediction", "storage"])
    activated, trace = reactivate(
        store=store,
        embedder=embedder,
        interpreted=interpreted,
        prediction=prediction,
        state=State.neutral(),
        session_id="default",
    )

    assert trace.fallback_to_strategic_search is False
    assert "mem_strong" in {e.memory_id for e in trace.activated}
