"""RawAIPolicy must stay deliberately amnesiac — no storage, no state."""

from __future__ import annotations

from pep.embed import Embedder
from pep.memory.store import MemoryStore
from pep.models.llm_client import StubLLMClient
from pep.policies.raw_ai import RawAIPolicy
from pep.schemas.input_schema import UserInput


def test_raw_ai_does_not_store_anything() -> None:
    store = MemoryStore(":memory:")
    initial_count = len(store.all_memories())

    RawAIPolicy().run_turn(
        user_input=UserInput(text="hello"),
        store=store,
        embedder=Embedder(),
        llm=StubLLMClient(),
    )

    assert len(store.all_memories()) == initial_count
    # And no run was logged either
    assert store.list_runs() == []


def test_raw_ai_returns_neutral_state() -> None:
    """State before and after must both be neutral — no modulation happens."""
    result = RawAIPolicy().run_turn(
        user_input=UserInput(text="hello"),
        store=MemoryStore(":memory:"),
        embedder=Embedder(),
        llm=StubLLMClient(),
    )
    assert result.state_before.urgency == 0.0
    assert result.state_after.urgency == 0.0
    assert result.state_before.uncertainty == 0.0
    assert result.state_after.uncertainty == 0.0


def test_raw_ai_packet_has_no_selected_memories() -> None:
    """The whole point: empty selected_memories means the LLM sees only the input."""
    result = RawAIPolicy().run_turn(
        user_input=UserInput(text="anything at all"),
        store=MemoryStore(":memory:"),
        embedder=Embedder(),
        llm=StubLLMClient(),
    )
    assert result.packet.selected_memories == []


def test_raw_ai_calls_llm_and_returns_response() -> None:
    result = RawAIPolicy().run_turn(
        user_input=UserInput(text="hello"),
        store=MemoryStore(":memory:"),
        embedder=Embedder(),
        llm=StubLLMClient(),
    )
    assert result.response  # not empty
    assert "[stub-llm]" in result.response  # confirms the LLM was actually called
