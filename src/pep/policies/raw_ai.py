"""RawAIPolicy — the deliberately-amnesiac baseline.

This policy exists for one reason: to be the "without PEP" half of the
side-by-side comparison. It does NOTHING between the user and the LLM:

  - No interpretation
  - No state modulation
  - No prediction
  - No memory retrieval
  - No residual scoring
  - No memory storage
  - No state persistence

Just: take the user's text, hand it to the LLM, return the response.
The way every basic chat app works.

The contrast with PEPFullPolicy is the entire demo. Type one question,
see two answers, see what PEP adds.
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


class RawAIPolicy:
    name = "raw_ai"

    def run_turn(
        self,
        *,
        user_input: UserInput,
        store: MemoryStore,
        embedder: Embedder,
        llm: LLMClient,
    ) -> PolicyResult:
        # Build the minimum viable packet so llm.complete() works.
        # CRUCIAL: selected_memories is empty. The base AI sees the raw input
        # and nothing else. No prior context, no history, no retrieval.
        packet = PEPPacket(
            session_id=user_input.session_id,
            raw_input=user_input.text,
            interpreted=InterpretedInput(
                intent="raw",
                topic="",
                task_type="unknown",
                notes="raw_ai — no interpretation",
            ),
            prediction=Prediction(notes="raw_ai — no prediction"),
            state=State.neutral(),
            selected_memories=[],
            residual=ResidualReport(reason="raw_ai — no scoring"),
            activation_trace=ActivationTrace(notes="raw_ai — no overlay, no memory"),
            response_goal=(
                "Answer the user. You have NO prior context — no memory of "
                "earlier turns, no stored facts. Respond as if this is the "
                "first time you've seen them."
            ),
        )

        response = llm.complete(packet)

        # Don't store anything. Don't update state. Don't log a run.
        # Stay amnesiac. That's the whole point.
        return PolicyResult(
            packet=packet,
            response=response,
            state_before=State.neutral(),
            state_after=State.neutral(),
        )
