"""Confirm the dialogue formatter never leaks PEP internals into the LLM prompt.

The whole point of the rewrite: the previous setup told the model "you are a
base reasoning model receiving a structured PEPPacket from an overlay layer
... cite memory ids when you draw on them," which made the model literally
say things like "Based on memory id [mem_xxx]..." in the conversation.

This test suite is a guardrail. If anyone reintroduces PEP-flavored language
into the dialogue prompt, these tests fail loudly.
"""

from __future__ import annotations

import re

from pep.dialogue import (
    Agent,
    format_packet_for_dialogue,
    run_dialogue,
)
from pep.embed import Embedder
from pep.memory.store import MemoryStore
from pep.models.llm_client import StubLLMClient
from pep.schemas.input_schema import InterpretedInput, Prediction, UserInput
from pep.schemas.pep_packet import (
    ActivationTrace,
    PEPPacket,
    ResidualReport,
)
from pep.schemas.state_schema import State


def _make_packet_with_memories() -> PEPPacket:
    """Build a packet that has activated memories so the formatter has
    something to render in the background section."""
    return PEPPacket(
        raw_input="What's your favorite color?",
        interpreted=InterpretedInput(
            intent="ask_question", topic="color", task_type="ask_question",
        ),
        prediction=Prediction(),
        state=State.neutral(),
        residual=ResidualReport(),
        activation_trace=ActivationTrace(),
        selected_memories=[
            {
                "id": "mem_real_1",
                "face": "semantic",
                "content": "I am Alice. curious learner",
                "brightness": 0.9,
                "tags": ["self"],
            },
            {
                "id": "mem_real_2",
                "face": "semantic",
                "content": "USER: I love sunsets ASSISTANT: Sunsets are beautiful",
                "brightness": 0.7,
                "tags": ["sunset"],
            },
            {
                "id": "self_Alice",
                "face": "semantic",
                "content": "I am Alice. curious learner — should be filtered out",
                "brightness": 1.0,
                "tags": ["self"],
            },
        ],
    )


# ─── No PEP leakage allowed ────────────────────────────────────────────────

FORBIDDEN_TOKENS = [
    "PEP",
    "PEPPacket",
    "memory id",
    "memory_id",
    "[mem_",
    "mem_real_",
    "self_Alice",
    "activation_trace",
    "activated memories",
    "overlay layer",
    "structured packet",
    "Inferred intent",
    "Current PEP state",
    "Response goal:",
]


def test_dialogue_prompt_contains_no_pep_internals() -> None:
    packet = _make_packet_with_memories()
    system, user = format_packet_for_dialogue(
        packet, agent_name="Alice", persona="curious learner",
        speaker_name="Bob",
    )
    combined = (system + "\n" + user)
    for token in FORBIDDEN_TOKENS:
        assert token not in combined, (
            f"Forbidden token {token!r} appeared in dialogue prompt:\n"
            f"---\n{combined}\n---"
        )


def test_dialogue_prompt_contains_persona_and_partner() -> None:
    packet = _make_packet_with_memories()
    system, user = format_packet_for_dialogue(
        packet, agent_name="Alice", persona="curious learner asking thoughtful questions",
        speaker_name="Bob",
    )
    assert "Alice" in system
    assert "curious learner" in system
    assert "Bob" in system
    # The user message includes the partner's name + the actual incoming text
    assert "Bob:" in user
    assert "favorite color" in user


def test_dialogue_prompt_filters_self_identity_memory() -> None:
    """The self_<name> memory is in the persona system prompt; it should NOT
    appear again as background to avoid redundancy."""
    packet = _make_packet_with_memories()
    system, _ = format_packet_for_dialogue(
        packet, agent_name="Alice", persona="curious learner",
        speaker_name="Bob",
    )
    # The "should be filtered out" memory has that exact phrase in its content
    assert "should be filtered out" not in system


def test_dialogue_prompt_strips_user_assistant_markers() -> None:
    """Conversation memories are stored as 'USER: ... ASSISTANT: ...' but the
    dialogue formatter should clean those markers so they read as natural
    background to the model, not as past chat logs."""
    packet = _make_packet_with_memories()
    system, _ = format_packet_for_dialogue(
        packet, agent_name="Alice", persona="x", speaker_name="Bob",
    )
    assert "USER:" not in system
    assert "ASSISTANT:" not in system
    # The content itself should still be there (sunsets are beautiful)
    assert "sunsets" in system.lower() or "Sunsets" in system


def test_dialogue_prompt_strips_stub_llm_markers() -> None:
    """Memories from earlier turns may contain '[stub-llm]' or '[ollama' marker
    text from previous responses. Those leak the existence of an LLM and should
    be stripped before showing as background."""
    packet = _make_packet_with_memories()
    packet.selected_memories.append({
        "id": "mem_leaky",
        "face": "semantic",
        "content": "USER: hi ASSISTANT: [stub-llm] PEP packet received...",
        "brightness": 0.5,
        "tags": [],
    })
    system, _ = format_packet_for_dialogue(
        packet, agent_name="Alice", persona="x", speaker_name="Bob",
    )
    assert "stub-llm" not in system
    assert "PEP packet" not in system


# ─── Agent uses complete_raw, not complete ─────────────────────────────────

class _RecordingLLM:
    """A fake LLM that records what was passed to complete_raw vs complete.

    Used to confirm Agent.respond_to calls complete_raw (with the natural
    formatter) and NOT complete (which would use the PEP-flavored formatter).
    """

    name = "recording"
    is_real = True

    def __init__(self) -> None:
        self.complete_calls = 0
        self.complete_raw_calls = 0
        self.support_calls = 0
        self.last_raw_system = ""
        self.last_raw_user = ""

    def complete(self, packet):
        self.complete_calls += 1
        return "[should not happen]"

    def stream_complete(self, packet):
        yield "[should not happen]"

    def complete_raw(self, *, system, user):
        self.complete_raw_calls += 1
        self.last_raw_system = system
        self.last_raw_user = user
        return f"Sure, here is a reply from a fake LLM."

    def support(self, *, system, user, model_tier="cheap"):
        self.support_calls += 1
        return ""


def test_agent_respond_to_uses_complete_raw_not_complete() -> None:
    store = MemoryStore(":memory:")
    embedder = Embedder()
    rec = _RecordingLLM()
    a = Agent(name="Alice", persona="curious", store=store, embedder=embedder, llm=rec)

    a.respond_to("Tell me something interesting.", speaker_name="Bob")

    assert rec.complete_raw_calls == 1, "Agent should call complete_raw, not complete"
    assert rec.complete_calls == 0, "Agent must NOT call complete (PEP-flavored prompt)"

    # The prompt the LLM saw should not contain PEP-speak
    full = rec.last_raw_system + rec.last_raw_user
    for token in ["PEPPacket", "memory id", "[mem_", "self_Alice"]:
        assert token not in full, f"{token!r} leaked into LLM prompt"
    # ...but it should mention Alice and Bob
    assert "Alice" in rec.last_raw_system
    assert "Bob" in rec.last_raw_user


def test_full_dialogue_runs_with_natural_prompts() -> None:
    """End-to-end: 4-turn dialogue with the recording LLM. Every prompt
    should be PEP-free."""
    store = MemoryStore(":memory:")
    embedder = Embedder()
    rec = _RecordingLLM()
    a = Agent(name="Alice", persona="curious", store=store, embedder=embedder, llm=rec)
    b = Agent(name="Bob", persona="patient", store=store, embedder=embedder, llm=rec)

    transcript = run_dialogue(a, b, opening="Hello there", turns=4)
    assert len(transcript) == 4
    assert rec.complete_raw_calls == 4
    assert rec.complete_calls == 0


def test_dialogue_topic_appears_in_system_prompt() -> None:
    """When a topic is provided, it should appear in BOTH agents' system
    prompts as meta-context — but the user message should still be the
    actual incoming line, not the topic."""
    packet = _make_packet_with_memories()
    system, user = format_packet_for_dialogue(
        packet, agent_name="Alice", persona="curious",
        speaker_name="Bob",
        topic="how cities are designed",
    )
    assert "how cities are designed" in system
    assert "topic" in system.lower()
    # The topic should NOT have hijacked the user message — that's the
    # incoming line, not the topic
    assert "how cities are designed" not in user
    assert "favorite color" in user  # the original incoming text


def test_dialogue_topic_threads_through_agent() -> None:
    """An Agent constructed with a topic should pass that topic to the
    formatter on every respond_to call."""
    store = MemoryStore(":memory:")
    embedder = Embedder()
    rec = _RecordingLLM()
    a = Agent(
        name="Alice", persona="curious",
        store=store, embedder=embedder, llm=rec,
        topic="the philosophy of memory",
    )
    a.respond_to("Tell me what you think.", speaker_name="Bob")

    assert "the philosophy of memory" in rec.last_raw_system


def test_dialogue_prompt_forbids_filler() -> None:
    """The system prompt must explicitly forbid empty acknowledgements
    like 'that's a great point' that waste tokens without adding substance."""
    packet = _make_packet_with_memories()
    system, _ = format_packet_for_dialogue(
        packet, agent_name="Alice", persona="x", speaker_name="Bob",
    )
    # Sentinel phrases the instruction names explicitly
    assert "no filler" in system.lower() or "no empty" in system.lower() or "do not begin" in system.lower()
    # The forbidden phrases themselves should be mentioned (by negative example)
    s_low = system.lower()
    assert "great point" in s_low or "i agree" in s_low or "interesting" in s_low


def test_dialogue_topic_empty_string_is_omitted() -> None:
    """If no topic is given, the system prompt should NOT include an empty
    'You are discussing:' line."""
    packet = _make_packet_with_memories()
    system, _ = format_packet_for_dialogue(
        packet, agent_name="Alice", persona="curious",
        speaker_name="Bob",
        topic="",
    )
    # No topic line at all
    assert "topic of your conversation" not in system.lower()
