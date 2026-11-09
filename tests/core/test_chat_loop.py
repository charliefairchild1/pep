"""End-to-end test of the full PEP loop using the stub LLM client.

This is the most important test in Phase 1. If this passes, every module
runs in sequence, the run ledger is populated, and the trace is recoverable.
"""

from __future__ import annotations

from pep.core.loop import run_turn
from pep.embed import Embedder
from pep.memory.store import MemoryStore
from pep.models.llm_client import StubLLMClient
from pep.schemas.input_schema import UserInput
from pep.schemas.memory_schema import MemoryObject


def test_full_loop_with_stub_llm() -> None:
    store = MemoryStore(":memory:")
    embedder = Embedder()
    llm = StubLLMClient()

    # Seed one relevant memory so the reactivator has something to pick up
    store.upsert_memory(MemoryObject(
        id="mem_seed",
        core="Prediction reduces storage and reaction cost.",
        faces={"semantic": "Prediction reduces storage and reaction cost."},
        fold_weights={"semantic": 1.0},
        tags=["prediction", "storage", "reaction"],
        brightness=0.7,
    ))

    user_input = UserInput(
        text="How does prediction help reduce storage in PEP?",
        session_id="test1",
    )
    packet, response, state_before, state_after = run_turn(
        user_input=user_input, store=store, embedder=embedder, llm=llm
    )

    # The base AI was called and produced text
    assert response
    assert "[stub-llm]" in response

    # The seed memory was activated
    activated_ids = {e.memory_id for e in packet.activation_trace.activated}
    assert "mem_seed" in activated_ids

    # Run was logged
    fetched = store.get_run(packet.id)
    assert fetched is not None
    assert fetched["session_id"] == "test1"

    # State was logged for this session
    assert store.turn_count("test1") == 1


def test_loop_preserves_state_across_turns() -> None:
    store = MemoryStore(":memory:")
    embedder = Embedder()
    llm = StubLLMClient()

    # First turn: signal urgency
    run_turn(
        user_input=UserInput(text="urgent: stop the deploy now", session_id="s2"),
        store=store, embedder=embedder, llm=llm,
    )
    state_after_t1 = store.latest_state("s2")
    assert state_after_t1.urgency > 0.0

    # Second turn: calmer input. State should retain some urgency due to blending
    run_turn(
        user_input=UserInput(text="ok thanks", session_id="s2"),
        store=store, embedder=embedder, llm=llm,
    )
    state_after_t2 = store.latest_state("s2")
    # urgency decays but doesn't snap to zero
    assert state_after_t2.urgency < state_after_t1.urgency
    assert store.turn_count("s2") == 2


def test_loop_stores_novel_exchange_as_memory() -> None:
    store = MemoryStore(":memory:")
    embedder = Embedder()
    llm = StubLLMClient()

    initial_count = len(store.all_memories())
    run_turn(
        user_input=UserInput(
            text="Tell me about Hexaflexagon Origami FortuneTeller memory architecture.",
            session_id="novel",
        ),
        store=store, embedder=embedder, llm=llm,
    )
    # Novel input → unexpected entities → should_store=True → new memory created
    assert len(store.all_memories()) > initial_count
