"""The full PEP policy — wraps the real PEP loop as a ContextPolicy.

This is what we're testing against the baselines. Everything PEP does —
interpretation, state modulation, prediction, spreading activation,
constellation detection, sense disambiguation, residual scoring,
trajectory gating, face selection, per-turn decay — all active.
"""

from __future__ import annotations

from pep.core.loop import run_turn
from pep.embed import Embedder
from pep.memory.store import MemoryStore
from pep.models.llm_client import LLMClient
from pep.policies.base import PolicyResult
from pep.schemas.input_schema import UserInput


class PEPFullPolicy:
    name = "pep_full"

    def run_turn(
        self,
        *,
        user_input: UserInput,
        store: MemoryStore,
        embedder: Embedder,
        llm: LLMClient,
    ) -> PolicyResult:
        packet, response, state_before, state_after = run_turn(
            user_input=user_input,
            store=store,
            embedder=embedder,
            llm=llm,
        )
        return PolicyResult(packet, response, state_before, state_after)
