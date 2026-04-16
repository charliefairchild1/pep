"""Baseline A: recent-window policy.

No retrieval at all. The base AI just sees the last N turns from the session
history. This is the dumbest useful baseline — it's what most chat apps do.
"""

from __future__ import annotations

from pep.embed import Embedder
from pep.memory.store import MemoryStore
from pep.models.llm_client import LLMClient
from pep.policies.base import PolicyResult
from pep.schemas.input_schema import InterpretedInput, Prediction, UserInput
from pep.schemas.pep_packet import (
    ActivationTrace,
    PEPPacket,
    ResidualReport,
)
from pep.schemas.state_schema import State

WINDOW_SIZE = 6  # last N messages to include


class RecentWindowPolicy:
    name = "recent_window"

    def run_turn(
        self,
        *,
        user_input: UserInput,
        store: MemoryStore,
        embedder: Embedder,
        llm: LLMClient,
    ) -> PolicyResult:
        state_before = store.latest_state(user_input.session_id)

        # Pull last N memories from this session (by creation time, most recent first)
        all_mems = store.all_memories(session_id=user_input.session_id)
        recent = all_mems[:WINDOW_SIZE]

        # Minimal interpretation — no real analysis
        interpreted = InterpretedInput(
            intent="unknown", topic=user_input.text[:40], task_type="unknown",
            notes="recent_window baseline — no interpretation",
        )
        prediction = Prediction(notes="recent_window baseline — no prediction")
        state_after = state_before  # no state modulation

        # No real activation — just dump the recent window
        selected = [
            {"id": m.id, "face": "semantic", "content": m.core[:300],
             "brightness": m.brightness, "tags": m.tags}
            for m in recent
        ]

        packet = PEPPacket(
            session_id=user_input.session_id,
            raw_input=user_input.text,
            interpreted=interpreted,
            prediction=prediction,
            state=state_after,
            selected_memories=selected,
            residual=ResidualReport(reason="recent_window — no residual scoring"),
            activation_trace=ActivationTrace(notes="recent_window — no activation"),
            response_goal="answer the user",
        )

        response = llm.complete(packet)

        # Store this turn as a memory (always, no gating)
        from pep.schemas.memory_schema import MemoryObject
        core = f"USER: {user_input.text[:200]}\nASSISTANT: {response[:200]}"
        store.upsert_memory(MemoryObject(
            core=core,
            faces={"semantic": core[:300]},
            fold_weights={"semantic": 1.0},
            tags=[w.lower() for w in user_input.text.split()[:8]],
            brightness=0.5,
            session_id=user_input.session_id,
            source_type="conversation",
        ))

        turn = store.turn_count(user_input.session_id) + 1
        store.log_state(user_input.session_id, turn, state_after)
        store.log_run(packet, response, state_before, state_after)

        return PolicyResult(packet, response, state_before, state_after)
