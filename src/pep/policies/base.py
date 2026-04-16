"""Policy protocol — what every context policy must implement."""

from __future__ import annotations

from typing import Protocol

from pep.embed import Embedder
from pep.memory.store import MemoryStore
from pep.models.llm_client import LLMClient
from pep.schemas.input_schema import UserInput
from pep.schemas.pep_packet import PEPPacket
from pep.schemas.state_schema import State


class PolicyResult:
    """What a policy produces for one turn."""

    __slots__ = ("packet", "response", "state_before", "state_after")

    def __init__(
        self,
        packet: PEPPacket,
        response: str,
        state_before: State,
        state_after: State,
    ):
        self.packet = packet
        self.response = response
        self.state_before = state_before
        self.state_after = state_after


class ContextPolicy(Protocol):
    """Minimal interface for a swappable context policy."""

    name: str

    def run_turn(
        self,
        *,
        user_input: UserInput,
        store: MemoryStore,
        embedder: Embedder,
        llm: LLMClient,
    ) -> PolicyResult:
        ...
