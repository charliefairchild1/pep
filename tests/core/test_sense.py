"""Sense Mapper + Ambiguity Tracker tests."""

from __future__ import annotations

from pep.core.sense import disambiguate
from pep.schemas.memory_schema import MemoryObject


def test_detects_ambiguous_term_with_two_distinct_tag_neighborhoods() -> None:
    """'power' used in physics vs politics should be flagged as ambiguous."""
    memories = [
        MemoryObject(id="m1", core="physics power", tags=["power", "energy", "watts"]),
        MemoryObject(id="m2", core="physics power 2", tags=["power", "energy", "force"]),
        MemoryObject(id="m3", core="political power", tags=["power", "politics", "authority"]),
        MemoryObject(id="m4", core="political power 2", tags=["power", "politics", "election"]),
    ]

    resolved = disambiguate(
        cue_terms={"power"},
        query_context={"power", "energy"},  # context hints toward physics
        memories=memories,
    )

    assert len(resolved) == 1
    rt = resolved[0]
    assert rt.term == "power"
    assert rt.ambiguity_score > 0  # it is genuinely ambiguous
    # With "energy" in the context, the physics sense should win
    assert rt.chosen_sense is not None
    assert "energy" in rt.chosen_sense.context_tags or "watts" in rt.chosen_sense.context_tags
    assert len(rt.alternatives) >= 1


def test_no_resolution_for_unambiguous_term() -> None:
    """A term that only appears in one tag neighborhood should NOT be resolved."""
    memories = [
        MemoryObject(id="m1", core="chess", tags=["chess", "bishop", "pawn"]),
        MemoryObject(id="m2", core="chess 2", tags=["chess", "knight", "opening"]),
    ]

    resolved = disambiguate(
        cue_terms={"chess"},
        query_context={"chess", "bishop"},
        memories=memories,
    )

    # Only one sense cluster → not ambiguous → not returned
    assert len(resolved) == 0


def test_sense_mapper_picks_right_sense_given_context() -> None:
    """With 'state' used in CS vs. politics, the query context should guide the pick."""
    memories = [
        MemoryObject(id="cs1", core="state machine", tags=["state", "machine", "fsm", "code"]),
        MemoryObject(id="cs2", core="state variable", tags=["state", "variable", "code"]),
        MemoryObject(id="pol1", core="state government", tags=["state", "government", "law"]),
        MemoryObject(id="pol2", core="state power", tags=["state", "government", "election"]),
    ]

    resolved = disambiguate(
        cue_terms={"state"},
        query_context={"state", "machine", "code"},  # context = CS
        memories=memories,
    )

    assert len(resolved) == 1
    rt = resolved[0]
    assert rt.chosen_sense is not None
    # CS-related tags should be in the chosen sense
    assert any(
        t in rt.chosen_sense.context_tags
        for t in ("machine", "fsm", "code", "variable")
    )
