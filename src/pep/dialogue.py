"""Two PEP instances talking to each other.

The most interesting research direction from §8.8 of the research note: what
happens when two PEP-equipped agents converse for many turns? Each one has
its own memory, its own state vector, its own categories. Do they form
complementary structures? Do their state vectors couple? Does coherence
measured at the joint memory level differ from coherence measured per agent?

This module provides:
  - `Agent` — wraps a MemoryStore + persona + the standard PEP loop
  - `run_dialogue(agent_a, agent_b, opening, turns)` — alternates turns,
    returns the full transcript + per-turn snapshots of both agents' state

Each agent's `respond_to(message)` reuses the existing PEP modules
(Interpreter, State Modulator, Predictor, Reactivator, Residual Scorer,
Packager, Updater) — the only thing that's different from a normal PEP
turn is that the packager's `response_goal` is overridden with the agent's
persona, so the base AI stays in character across turns.

Each agent's session_id is `dialogue:<name>`, so two agents writing to the
same SQLite store don't collide.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterator

from pep.core.interpreter import interpret
from pep.core.packager import package
from pep.core.predictor import predict
from pep.core.reactivator import reactivate
from pep.core.residuals import score_residual
from pep.core.state import estimate_state
from pep.core.updater import update_memory
from pep.embed import Embedder
from pep.memory.store import MemoryStore
from pep.models.llm_client import LLMClient
from pep.schemas.input_schema import UserInput
from pep.schemas.pep_packet import PEPPacket
from pep.schemas.state_schema import State


def format_packet_for_dialogue(
    packet: PEPPacket,
    *,
    agent_name: str,
    persona: str,
    speaker_name: str,
    topic: str = "",
) -> tuple[str, str]:
    """Build a natural conversation prompt that does NOT leak PEP internals.

    The default `_format_packet_for_llm` in models/llm_client.py tells the
    base AI things like:
      - "You are a base reasoning model receiving a structured PEPPacket..."
      - "...citing memory ids when you draw on them"
      - The state vector, the inferred intent, the response goal as a dict
    Those are useful for debugging but they DESTROY the conversation: the
    model becomes self-aware that it's reading retrieved memories and starts
    saying things like "Based on memory id [mem_xxx]...".

    This formatter strips ALL of that. The model just sees:
      - Who it is (the agent's persona, in the system prompt)
      - Background it knows (the activated memory cores, presented as natural
        prose, with no IDs and no mention of retrieval)
      - The conversation partner's last message

    PEP still runs and produces the trace — only the LLM-facing prompt changes.
    """
    # Filter out the agent's own self-identity memory (it's redundant with
    # the persona we're putting in the system prompt) and any PEP-flavored
    # memories that mention IDs literally.
    background_lines: list[str] = []
    for mem in packet.selected_memories:
        mem_id = mem.get("id", "")
        if mem_id.startswith("self_"):
            continue
        content = mem.get("content", "")
        if not content:
            continue
        # Strip leading "USER: ... ASSISTANT: ..." prefixes that conversation
        # memories have, and any "[stub-llm]" or "[ollama]" leakage.
        cleaned = content
        for marker in ("[stub-llm]", "[ollama"):
            if marker in cleaned:
                cleaned = cleaned.split(marker)[0]
        cleaned = cleaned.replace("USER:", "").replace("ASSISTANT:", "").strip()
        if not cleaned:
            continue
        # Cap length so we don't overflow context
        background_lines.append(cleaned[:240])

    background = ""
    if background_lines:
        background = (
            "\n\nThings you know (use only if relevant; do not list them or cite them):\n"
            + "\n".join(f"- {line}" for line in background_lines[:6])
        )

    topic_line = ""
    if topic.strip():
        topic_line = f"\nThe topic of your conversation: {topic.strip()}\n"

    system = (
        f"You are {agent_name}. {persona}\n"
        f"You are having a conversation with {speaker_name}. Stay in character. "
        f"Reply naturally in 1-3 sentences, like a real person in a real conversation. "
        f"Do not narrate your own thinking. Do not mention memories, IDs, citations, "
        f"or any internal machinery. Just talk."
        f"\n\nIMPORTANT — no filler. Every response must add new substance:\n"
        f"- Do NOT begin with 'That's a great point', 'I agree', 'Interesting', "
        f"'Good question', or any other empty acknowledgement.\n"
        f"- Do NOT restate what the other person just said back to them.\n"
        f"- Do NOT praise them or ask them to elaborate unless it's genuinely "
        f"the most useful next move.\n"
        f"- Just go straight to the new thing you have to say. One specific "
        f"point, not a hedge."
        f"{topic_line}"
        f"{background}"
    )
    user = f"{speaker_name}: {packet.raw_input}"
    return system, user


# Curated default persona sets. Each set defines N personas that take turns
# in round-robin order. 2-agent sets use the original tuple-style data;
# 3+-agent sets are lists.
DEFAULT_PERSONAS: dict[str, list[str]] = {
    "curious_and_expert": [
        "Curious novice. Ask thoughtful questions. Build on what the other "
        "person just said. Don't pretend to know things you don't.",
        "Patient expert. Explain clearly, in 2-3 sentences. Use concrete "
        "examples. Don't lecture; respond to what was actually asked.",
    ],
    "skeptic_and_advocate": [
        "Friendly skeptic. Probe assumptions. Ask 'what if' and 'how do we know'. "
        "Be polite but uncompromising about evidence.",
        "Thoughtful advocate. Defend a position with care. Acknowledge "
        "counter-arguments before answering them. Don't overstate.",
    ],
    "builder_and_critic": [
        "Creative builder. Propose concrete ideas, sketches, prototypes. "
        "Build on the critic's last point.",
        "Constructive critic. Find what's weak in the proposal and suggest "
        "specific improvements. Be precise, not destructive.",
    ],
    "two_researchers": [
        "Researcher A. Bring up findings, papers, and open questions in your area. "
        "Listen to what the others say and connect it to your work.",
        "Researcher B. Same as A — bring your own perspective and connect it.",
    ],
    "three_perspectives": [
        "Optimist. See the upside. Look for what could go right. "
        "Be earnest, not naive — acknowledge the risks but believe in the upside.",
        "Pessimist. See what could go wrong. Surface failure modes the others "
        "are missing. Be specific and concrete, not just gloomy.",
        "Realist. Find the middle. Hold both the optimist and the pessimist "
        "accountable. Ask 'what's actually likely?' Steer toward what's actionable.",
    ],
    "roundtable": [
        "The questioner. Drive the conversation forward by asking incisive "
        "questions. Don't answer them yourself — let the others.",
        "The expert. Bring deep knowledge and concrete examples. Acknowledge "
        "uncertainty where it exists.",
        "The devil's advocate. Push back on whatever just got said. Make "
        "the others defend their positions. Be polite but uncompromising.",
    ],
    "four_friends": [
        "The dreamer. Bring up big imaginative ideas. Ask 'what if'.",
        "The pragmatist. Bring it back to reality. Ask 'how would that actually work'.",
        "The historian. Connect what's being said to past examples and patterns.",
        "The synthesizer. Find the common thread. Reflect what everyone has said.",
    ],
}

# Default agent names, indexed by position. Up to 5 agents supported.
DEFAULT_AGENT_NAMES: list[str] = ["Alice", "Bob", "Carol", "Dave", "Eve"]


@dataclass
class TurnRecord:
    turn: int
    speaker: str
    message: str
    packet_id: str
    memories_after: int
    state_after: dict
    activated_memory_ids: list[str] = field(default_factory=list)


class Agent:
    """A single PEP-equipped agent in a dialogue."""

    def __init__(
        self,
        *,
        name: str,
        persona: str,
        store: MemoryStore,
        embedder: Embedder,
        llm: LLMClient,
        topic: str = "",
    ):
        self.name = name
        self.persona = persona
        self.store = store
        self.embedder = embedder
        self.llm = llm
        self.topic = topic
        self.session_id = f"dialogue:{name}"
        self._seed_self_memory()

    def _seed_self_memory(self) -> None:
        """Plant a high-brightness identity memory so the persona is in the
        agent's own memory, not just in the prompt."""
        from pep.schemas.memory_schema import MemoryObject

        self.store.upsert_memory(MemoryObject(
            id=f"self_{self.name}",
            core=f"I am {self.name}. {self.persona}",
            faces={"semantic": f"My name is {self.name}. {self.persona}"},
            fold_weights={"semantic": 1.0},
            tags=["self", "identity", self.name.lower(), "persona"],
            brightness=1.0,
            session_id=self.session_id,
            source_type="fact",
        ))

    def _run_pep_overlay(self, user_input: UserInput):
        """Run interpret → state → predict → reactivate → score → package.

        Returns a tuple of (state_before, state_after, interpreted, prediction,
        activated, trace, residual, packet). Shared by both respond_to (which
        adds the LLM call after) and observe (which doesn't).
        """
        state_before = self.store.latest_state(self.session_id)

        runs = self.store.list_runs(session_id=self.session_id, limit=1)
        prior_known: list[str] = []
        if runs:
            last_run = self.store.get_run(runs[0]["id"])
            if last_run:
                packet_dict = last_run.get("packet") or {}
                for mem in packet_dict.get("selected_memories") or []:
                    for t in mem.get("tags", []) or []:
                        if t and t not in prior_known:
                            prior_known.append(t)

        interpreted = interpret(user_input, llm=self.llm)
        state_after = estimate_state(state_before, user_input, interpreted, llm=self.llm)
        prediction = predict(
            interpreted, state_after,
            prior_expected_entities=prior_known, llm=self.llm,
        )
        activated, trace = reactivate(
            store=self.store, embedder=self.embedder,
            interpreted=interpreted, prediction=prediction,
            state=state_after, session_id=self.session_id,
        )
        residual = score_residual(
            interpreted=interpreted, prediction=prediction, state=state_after,
        )
        packet = package(
            user_input=user_input, interpreted=interpreted, prediction=prediction,
            state=state_after, activated=activated, activation_trace=trace, residual=residual,
        )
        return state_before, state_after, interpreted, prediction, activated, trace, residual, packet

    def respond_to(self, incoming_message: str, *, speaker_name: str) -> TurnRecord:
        """Receive a message from another agent and produce a response.

        Runs the full PEP loop and overrides the packager's response_goal
        with this agent's persona so the base AI stays in character.
        """
        user_input = UserInput(
            text=incoming_message,
            session_id=self.session_id,
            timestamp=datetime.utcnow(),
        )
        (
            state_before, state_after, interpreted, prediction,
            activated, trace, residual, packet,
        ) = self._run_pep_overlay(user_input)

        # Build a NATURAL conversation prompt. The default packet formatter
        # tells the model it's reading PEP traces and asks it to cite memory
        # IDs — that destroys conversation. Use the dialogue formatter, which
        # presents activated memories as natural background and never mentions
        # PEP, IDs, or internals.
        system, user = format_packet_for_dialogue(
            packet,
            agent_name=self.name,
            persona=self.persona,
            speaker_name=speaker_name,
            topic=self.topic,
        )
        packet.response_goal = f"[dialogue] {self.name} replies to {speaker_name}"

        response = self.llm.complete_raw(system=system, user=user)

        # Update memory just like a normal PEP turn — store the exchange
        update_memory(
            store=self.store, user_input=user_input, interpreted=interpreted,
            assistant_response=response, residual=residual,
            activated_ids=[m.id for m in activated], llm=self.llm,
        )

        # Per-turn decay
        activated_id_set = {m.id for m in activated}
        self.store.decay_unused_memories(decay=0.005, exclude_ids=activated_id_set)

        # State + run logging
        turn_number = self.store.turn_count(self.session_id) + 1
        self.store.log_state(self.session_id, turn_number, state_after)
        self.store.log_run(packet, response, state_before, state_after)

        return TurnRecord(
            turn=turn_number,
            speaker=self.name,
            message=response,
            packet_id=packet.id,
            memories_after=len(self.store.all_memories(session_id=self.session_id)),
            state_after=state_after.model_dump(),
            activated_memory_ids=[m.id for m in activated],
        )

    def observe(self, message: str, *, speaker_name: str) -> dict:
        """Passively listen to a message from another agent (no LLM call).

        Used in multi-agent dialogues: when one agent speaks, the others
        run their PEP overlay over the message and update their memory,
        but they don't generate a response. This is the "listening to a
        group conversation" path. State updates, memory grows, but the
        LLM is not invoked.
        """
        user_input = UserInput(
            text=message,
            session_id=self.session_id,
            timestamp=datetime.utcnow(),
        )
        (
            state_before, state_after, interpreted, _prediction,
            activated, _trace, residual, _packet,
        ) = self._run_pep_overlay(user_input)

        # Store the message as a memory — but as something HEARD from another
        # agent, not as something the agent themselves said. We tag it with
        # `observed_from` so it can be filtered later.
        from pep.schemas.memory_schema import MemoryObject
        observation = MemoryObject(
            core=f"{speaker_name} said: {message[:280]}",
            faces={
                "semantic": message[:300],
                "episodic": f"heard from {speaker_name}",
            },
            fold_weights={"semantic": 1.0, "episodic": 0.7},
            tags=[
                speaker_name.lower(),
                "observed",
            ] + [w.lower() for w in message.split()[:8] if len(w) > 3],
            brightness=0.4,  # observed memories are slightly less prominent than spoken ones
            session_id=self.session_id,
            source_type="conversation",
        )
        self.store.upsert_memory(observation)

        # State + decay (same housekeeping as respond_to, just no LLM call or run log)
        activated_id_set = {m.id for m in activated}
        self.store.decay_unused_memories(decay=0.003, exclude_ids=activated_id_set)
        turn_number = self.store.turn_count(self.session_id) + 1
        self.store.log_state(self.session_id, turn_number, state_after)

        return {
            "observed_by": self.name,
            "speaker": speaker_name,
            "stored_id": observation.id,
            "state_after": state_after.model_dump(),
            "memories_after": len(self.store.all_memories(session_id=self.session_id)),
        }


def run_dialogue(
    agent_a: Agent,
    agent_b: Agent,
    *,
    opening: str,
    turns: int = 30,
    starts_with: str = "a",
) -> list[TurnRecord]:
    """Run an alternating dialogue between two agents.

    The opening line is treated as if `starts_with` agent received it from
    the other agent. They alternate from there. Returns the full transcript
    in order.

    `turns` is the total number of agent turns (not turn-pairs). With
    turns=6 and starts_with='a', the order is A, B, A, B, A, B.
    """
    transcript: list[TurnRecord] = []
    speaker = agent_a if starts_with == "a" else agent_b
    listener = agent_b if starts_with == "a" else agent_a
    next_message = opening
    incoming_speaker_name = "interlocutor"

    for _ in range(turns):
        record = speaker.respond_to(next_message, speaker_name=incoming_speaker_name)
        transcript.append(record)
        next_message = record.message
        incoming_speaker_name = speaker.name
        speaker, listener = listener, speaker

    return transcript


def run_multi_agent_dialogue(
    agents: list[Agent],
    *,
    opening: str,
    turns: int = 30,
) -> list[TurnRecord]:
    """Round-robin dialogue across N agents.

    Each turn: one agent speaks (via respond_to), the others observe (via
    observe — passive PEP loop, no LLM call). The speaker rotates in
    turn % N order. Each agent's memory grows from BOTH speaking and
    listening, the way a real group conversation works.
    """
    if len(agents) < 2:
        raise ValueError("multi-agent dialogue needs at least 2 agents")

    transcript: list[TurnRecord] = []
    next_message = opening
    next_speaker_name = "interlocutor"

    for turn_idx in range(turns):
        speaker_idx = turn_idx % len(agents)
        speaker = agents[speaker_idx]

        record = speaker.respond_to(next_message, speaker_name=next_speaker_name)
        transcript.append(record)

        # Every other agent observes the speaker's message — they ingest it
        # via the PEP overlay (no LLM call) so their own memory grows.
        for i, listener in enumerate(agents):
            if i == speaker_idx:
                continue
            listener.observe(record.message, speaker_name=speaker.name)

        next_message = record.message
        next_speaker_name = speaker.name

    return transcript


def stream_multi_agent_dialogue(
    agents: list[Agent],
    *,
    opening: str,
    turns: int | None = 30,
    should_stop=None,
) -> Iterator[dict]:
    """Streaming variant of run_multi_agent_dialogue.

    Yields one event per turn (so the UI can render the conversation as it
    unfolds), plus an `observation` event each time a non-speaker agent
    finishes ingesting the speaker's message. If `turns` is None, runs
    indefinitely until should_stop fires.
    """
    if len(agents) < 2:
        raise ValueError("multi-agent dialogue needs at least 2 agents")

    next_message = opening
    next_speaker_name = "interlocutor"
    completed = 0
    turn_idx = 0

    while True:
        if turns is not None and turn_idx >= turns:
            break
        if should_stop is not None and should_stop():
            yield {"event": "stopped", "completed_turns": completed}
            return

        speaker_idx = turn_idx % len(agents)
        speaker = agents[speaker_idx]

        record = speaker.respond_to(next_message, speaker_name=next_speaker_name)
        completed += 1
        yield {
            "event": "turn",
            "index": turn_idx,
            "speaker": record.speaker,
            "message": record.message,
            "memories_after": record.memories_after,
            "state_after": record.state_after,
            "activated_memory_ids": record.activated_memory_ids,
            "packet_id": record.packet_id,
        }

        # Have every other agent observe — yield a brief event per observer
        # so the UI can show the listeners' state updating too.
        for i, listener in enumerate(agents):
            if i == speaker_idx:
                continue
            obs = listener.observe(record.message, speaker_name=speaker.name)
            yield {
                "event": "observation",
                "observer": listener.name,
                "speaker": speaker.name,
                "memories_after": obs["memories_after"],
                "state_after": obs["state_after"],
            }

        next_message = record.message
        next_speaker_name = speaker.name
        turn_idx += 1

    yield {"event": "done", "total_turns": completed}


def stream_dialogue(
    agent_a: Agent,
    agent_b: Agent,
    *,
    opening: str,
    turns: int | None = 30,
    starts_with: str = "a",
    should_stop=None,
) -> Iterator[dict]:
    """Generator variant: yield each turn as it completes.

    If `turns` is None, run until `should_stop` returns True (auto-continue
    mode — the dialogue keeps going until the user clicks Stop). Otherwise
    run at most `turns` turns. Either way, `should_stop` is checked before
    each turn and on True the generator yields `stopped` and exits cleanly.
    """
    speaker = agent_a if starts_with == "a" else agent_b
    listener = agent_b if starts_with == "a" else agent_a
    next_message = opening
    incoming_speaker_name = "interlocutor"

    completed = 0
    turn_idx = 0
    while True:
        if turns is not None and turn_idx >= turns:
            break
        if should_stop is not None and should_stop():
            yield {"event": "stopped", "completed_turns": completed}
            return

        record = speaker.respond_to(next_message, speaker_name=incoming_speaker_name)
        completed += 1
        yield {
            "event": "turn",
            "index": turn_idx,
            "speaker": record.speaker,
            "message": record.message,
            "memories_after": record.memories_after,
            "state_after": record.state_after,
            "activated_memory_ids": record.activated_memory_ids,
            "packet_id": record.packet_id,
        }
        next_message = record.message
        incoming_speaker_name = speaker.name
        speaker, listener = listener, speaker
        turn_idx += 1

    yield {"event": "done", "total_turns": completed}
