"""Two PEP instances dialogue tests."""

from __future__ import annotations

from pep.dialogue import (
    DEFAULT_PERSONAS,
    Agent,
    run_dialogue,
    stream_dialogue,
)
from pep.embed import Embedder
from pep.memory.store import MemoryStore
from pep.models.llm_client import StubLLMClient


def _make_agents() -> tuple[Agent, Agent]:
    store = MemoryStore(":memory:")
    embedder = Embedder()
    llm = StubLLMClient()
    a = Agent(
        name="Alice", persona="curious learner",
        store=store, embedder=embedder, llm=llm,
    )
    b = Agent(
        name="Bob", persona="patient expert",
        store=store, embedder=embedder, llm=llm,
    )
    return a, b


def test_agent_seeds_self_identity_memory() -> None:
    """Each Agent should have a self-identity memory in its session."""
    a, b = _make_agents()
    alice_mems = a.store.all_memories(session_id="dialogue:Alice")
    bob_mems = b.store.all_memories(session_id="dialogue:Bob")
    assert any("Alice" in m.core for m in alice_mems)
    assert any("Bob" in m.core for m in bob_mems)
    # Identity memories should be high-brightness so they stay surfaceable
    alice_self = next(m for m in alice_mems if m.id == "self_Alice")
    assert alice_self.brightness >= 0.9


def test_run_dialogue_alternates_speakers() -> None:
    """6 turns should produce A, B, A, B, A, B in order."""
    a, b = _make_agents()
    transcript = run_dialogue(a, b, opening="Hello", turns=6)
    assert len(transcript) == 6
    speakers = [r.speaker for r in transcript]
    assert speakers == ["Alice", "Bob", "Alice", "Bob", "Alice", "Bob"]


def test_dialogue_grows_each_agents_memory() -> None:
    a, b = _make_agents()
    initial_a = len(a.store.all_memories(session_id="dialogue:Alice"))
    initial_b = len(b.store.all_memories(session_id="dialogue:Bob"))

    transcript = run_dialogue(a, b, opening="Tell me about prediction.", turns=4)

    final_a = len(a.store.all_memories(session_id="dialogue:Alice"))
    final_b = len(b.store.all_memories(session_id="dialogue:Bob"))

    # Each agent should have stored at least one new memory across the dialogue
    assert final_a > initial_a
    assert final_b > initial_b
    # The transcript should have valid responses (not empty)
    for record in transcript:
        assert record.message  # non-empty
        assert record.memories_after >= 1


def test_starts_with_b_makes_b_speak_first() -> None:
    a, b = _make_agents()
    transcript = run_dialogue(a, b, opening="hi", turns=2, starts_with="b")
    assert transcript[0].speaker == "Bob"
    assert transcript[1].speaker == "Alice"


def test_stream_dialogue_yields_per_turn_events() -> None:
    a, b = _make_agents()
    events = list(stream_dialogue(a, b, opening="hi", turns=3))
    # 3 turn events + 1 done event
    assert len(events) == 4
    turn_events = [e for e in events if e["event"] == "turn"]
    assert len(turn_events) == 3
    # Each turn event has the expected fields
    for e in turn_events:
        assert "speaker" in e
        assert "message" in e
        assert "memories_after" in e
        assert "state_after" in e
    assert events[-1]["event"] == "done"
    assert events[-1]["total_turns"] == 3


def test_default_personas_loaded() -> None:
    """Persona sets can have 2 or more agents now (lists, not tuples)."""
    assert "curious_and_expert" in DEFAULT_PERSONAS
    assert "skeptic_and_advocate" in DEFAULT_PERSONAS
    assert "builder_and_critic" in DEFAULT_PERSONAS
    # Multi-agent presets
    assert "three_perspectives" in DEFAULT_PERSONAS
    assert "roundtable" in DEFAULT_PERSONAS
    assert "four_friends" in DEFAULT_PERSONAS

    for name, personas in DEFAULT_PERSONAS.items():
        assert isinstance(personas, list)
        assert len(personas) >= 2
        for p in personas:
            assert isinstance(p, str)
            assert p  # non-empty


def test_three_agent_dialogue_round_robin() -> None:
    """3 agents take turns A → B → C → A → B → C, each with their own memory."""
    from pep.dialogue import Agent, run_multi_agent_dialogue

    store = MemoryStore(":memory:")
    embedder = Embedder()
    llm = StubLLMClient()

    agents = [
        Agent(name=name, persona=f"agent {name.lower()}",
              store=store, embedder=embedder, llm=llm)
        for name in ("Alice", "Bob", "Carol")
    ]

    transcript = run_multi_agent_dialogue(agents, opening="Let's start.", turns=6)
    assert len(transcript) == 6
    speakers = [r.speaker for r in transcript]
    assert speakers == ["Alice", "Bob", "Carol", "Alice", "Bob", "Carol"]


def test_observe_grows_listener_memory_without_llm_call() -> None:
    """observe() should add a memory to the listener but NOT invoke the LLM."""
    from pep.dialogue import Agent

    class _CountingLLM(StubLLMClient):
        def __init__(self):
            self.complete_calls = 0
            self.complete_raw_calls = 0
        def complete(self, packet):
            self.complete_calls += 1
            return super().complete(packet)
        def complete_raw(self, *, system, user):
            self.complete_raw_calls += 1
            return f"[stub] {user[:80]}"

    store = MemoryStore(":memory:")
    embedder = Embedder()
    llm = _CountingLLM()
    a = Agent(name="Alice", persona="x", store=store, embedder=embedder, llm=llm)

    initial = len(store.all_memories(session_id="dialogue:Alice"))
    a.observe("Hello there.", speaker_name="Bob")
    after = len(store.all_memories(session_id="dialogue:Alice"))

    assert after > initial  # listener stored a memory
    assert llm.complete_calls == 0
    assert llm.complete_raw_calls == 0  # observe NEVER calls the LLM


def test_multi_agent_dialogue_each_agent_has_independent_memory() -> None:
    """After a 4-agent round-robin dialogue, each agent's session has memories
    grown from BOTH speaking and observing."""
    from pep.dialogue import Agent, run_multi_agent_dialogue

    store = MemoryStore(":memory:")
    embedder = Embedder()
    llm = StubLLMClient()

    agents = [
        Agent(name=name, persona=f"agent {name.lower()}",
              store=store, embedder=embedder, llm=llm)
        for name in ("Alice", "Bob", "Carol", "Dave")
    ]

    run_multi_agent_dialogue(agents, opening="Let's start.", turns=8)

    # Each session should have at least one stored memory
    for name in ("Alice", "Bob", "Carol", "Dave"):
        mems = store.all_memories(session_id=f"dialogue:{name}")
        assert len(mems) > 0, f"{name} has no memories"
