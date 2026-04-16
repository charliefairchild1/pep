"""Base AI client adapters.

Two methods on every LLM client:

- `complete(packet)` is the *base AI reasoning* call. Goes to the strong model
  (sonnet by default). PEP hands a fully-prepared PEPPacket to it and gets back
  the user-visible response. There should be exactly one of these per turn.

- `support(system, user, model_tier)` is the *cheap structured* call. Used by
  the Interpreter, Predictor, State Modulator, Updater, etc. — every supporting
  module that wants a Claude call instead of a heuristic. Defaults to haiku
  (cheap) so the per-turn cost stays bounded.

The supporting calls all return raw strings. The supporting modules are
responsible for parsing JSON / extracting fields. They MUST handle the case
where the call returns garbage (or where the stub client returns canned text).
"""

from __future__ import annotations

import os
from typing import Iterator, Literal, Protocol

from pep.schemas.pep_packet import PEPPacket

ModelTier = Literal["cheap", "strong"]


class LLMClient(Protocol):
    """Minimal interface a base AI must implement to be plugged in below PEP."""

    name: str

    def complete(self, packet: PEPPacket) -> str:
        """The strong-model call. One per turn. Returns the user-facing response."""
        ...

    def stream_complete(self, packet: PEPPacket) -> Iterator[str]:
        """Streaming variant of complete().

        Yields content chunks as the model generates them. The full response
        is the concatenation of all chunks. Implementations that don't support
        streaming should yield the complete response in a single chunk.
        """
        ...

    def complete_raw(self, *, system: str, user: str) -> str:
        """Strong-model call with raw system+user strings, bypassing the
        PEPPacket formatter. Used by callers (like the dialogue Agent) that
        want to build their OWN system prompt — typically because the default
        packet formatter mentions PEP internals that should not appear in
        natural conversation.
        """
        ...

    def support(self, *, system: str, user: str, model_tier: ModelTier = "cheap") -> str:
        """A cheap structured call for supporting modules. Returns raw text.

        Implementations should default to haiku for `cheap` and sonnet for
        `strong`. Callers parse the result themselves and must handle failure.
        """
        ...

    @property
    def is_real(self) -> bool:
        """True if this client is calling a real model. Stubs return False."""
        ...


def _format_packet_for_llm(packet: PEPPacket) -> tuple[str, str]:
    """Render a PEPPacket into (system, user) strings — natural version.

    The model is told it's a helpful assistant with some background it
    "knows", presented as plain prose. No mention of PEP, packets, memory
    IDs, internal state, or activation traces. The activated memories
    become background context the model can draw on without being told to
    cite them.

    This is the chat-path formatter. The dialogue path uses a similar
    formatter in `pep/dialogue.py` that adds a persona block.
    """
    # Filter and clean activated memories the same way the dialogue formatter
    # does — strip PEP/stub/USER/ASSISTANT markers, drop self-identity memories
    background_lines: list[str] = []
    for mem in packet.selected_memories:
        mem_id = str(mem.get("id", ""))
        if mem_id.startswith("self_"):
            continue
        content = str(mem.get("content", "")).strip()
        if not content:
            continue
        # Strip stub-llm and ollama markers from old memories
        for marker in ("[stub-llm]", "[ollama"):
            if marker in content:
                content = content.split(marker)[0]
        # Strip USER:/ASSISTANT: prefixes from legacy memories
        cleaned = (
            content.replace("USER:", "")
                   .replace("ASSISTANT:", "")
                   .replace("\n", " ")
                   .strip()
        )
        if not cleaned:
            continue
        background_lines.append(cleaned[:240])

    background = ""
    if background_lines:
        background = (
            "\n\nThings you know that may be relevant (use only if helpful; "
            "do not list them or cite them):\n"
            + "\n".join(f"- {line}" for line in background_lines[:6])
        )

    system = (
        "You are a helpful assistant. Respond naturally and directly — like "
        "a real person in a real conversation, not a chatbot performing a "
        "task. Keep replies appropriately concise unless the user explicitly "
        "wants a long answer.\n\n"
        "IMPORTANT — no filler. Every response must add new substance:\n"
        "- Do NOT begin with 'That's a great point', 'I agree', 'Interesting', "
        "'Good question', or any other empty acknowledgement.\n"
        "- Do NOT narrate your own thinking ('I think...', 'Let me explain...').\n"
        "- Do NOT mention memories, IDs, citations, packets, or any internal "
        "machinery. The user does not want to see meta-commentary.\n"
        "- Just answer the question directly."
        f"{background}"
    )

    user = packet.raw_input
    return system, user


class StubLLMClient:
    """Canned responses. Lets the full PEP loop run with no API key.

    The stub's `support()` returns an empty string, which signals to all
    supporting modules that they should fall back to their heuristic path.
    """

    name = "stub"
    is_real = False

    def complete(self, packet: PEPPacket) -> str:
        n_memories = len(packet.selected_memories)
        intent = packet.interpreted.intent
        topic = packet.interpreted.topic
        novelty = packet.residual.novelty_score
        return (
            "[stub-llm] PEP packet received.\n"
            f"intent={intent} topic={topic} memories={n_memories} novelty={novelty:.2f}\n"
            f"(Phase 1 stub. Set ANTHROPIC_API_KEY to wire in real Claude.)\n"
            f"Echo of input: {packet.raw_input[:160]}"
        )

    def stream_complete(self, packet: PEPPacket) -> Iterator[str]:
        # Stub doesn't really stream — yield the canned response in one chunk
        yield self.complete(packet)

    def complete_raw(self, *, system: str, user: str) -> str:
        # Echo a short canned response so dialogue tests can run with no model
        return f"[stub-llm] (raw) {user[:160]}"

    def support(self, *, system: str, user: str, model_tier: ModelTier = "cheap") -> str:
        # Return empty so callers cleanly fall back to their heuristic path
        return ""


class AnthropicLLMClient:
    """Real Claude. Activated when ANTHROPIC_API_KEY is set."""

    name = "anthropic"
    is_real = True

    # Tier → model name. Override at construction if needed.
    DEFAULT_MODELS: dict[ModelTier, str] = {
        "cheap": "claude-haiku-4-5-20251001",
        "strong": "claude-sonnet-4-6",
    }

    def __init__(
        self,
        strong_model: str = "claude-sonnet-4-6",
        cheap_model: str = "claude-haiku-4-5-20251001",
        max_tokens: int = 1024,
        support_max_tokens: int = 512,
    ):
        from anthropic import Anthropic

        self._client = Anthropic()
        self._models: dict[ModelTier, str] = {
            "strong": strong_model,
            "cheap": cheap_model,
        }
        self.max_tokens = max_tokens
        self.support_max_tokens = support_max_tokens

    def complete(self, packet: PEPPacket) -> str:
        system, user = _format_packet_for_llm(packet)
        msg = self._client.messages.create(
            model=self._models["strong"],
            max_tokens=self.max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        parts = []
        for block in msg.content:
            text = getattr(block, "text", None)
            if text:
                parts.append(text)
        return "".join(parts) or "(no text returned)"

    def stream_complete(self, packet: PEPPacket) -> Iterator[str]:
        """Stream tokens via the Anthropic SDK's stream() context manager."""
        system, user = _format_packet_for_llm(packet)
        try:
            with self._client.messages.stream(
                model=self._models["strong"],
                max_tokens=self.max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            yield f"[anthropic stream error: {e}]"

    def complete_raw(self, *, system: str, user: str) -> str:
        """Strong-model call with raw system+user strings."""
        try:
            msg = self._client.messages.create(
                model=self._models["strong"],
                max_tokens=self.max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            parts = []
            for block in msg.content:
                text = getattr(block, "text", None)
                if text:
                    parts.append(text)
            return "".join(parts) or "(no text returned)"
        except Exception as e:
            return f"[anthropic error: {e}]"

    def support(self, *, system: str, user: str, model_tier: ModelTier = "cheap") -> str:
        try:
            msg = self._client.messages.create(
                model=self._models[model_tier],
                max_tokens=self.support_max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            parts = []
            for block in msg.content:
                text = getattr(block, "text", None)
                if text:
                    parts.append(text)
            return "".join(parts)
        except Exception:
            return ""


def get_llm_client() -> LLMClient:
    """Factory: prefer real Claude > local Ollama > stub.

    Order of preference:
      1. AnthropicLLMClient if ANTHROPIC_API_KEY is set
      2. OllamaLLMClient if a daemon is reachable on localhost:11434
      3. StubLLMClient (canned responses, lets the loop run with no real AI)
    """
    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            return AnthropicLLMClient()
        except Exception:
            pass

    # Try Ollama: cheap reachability check, then construct
    try:
        import httpx

        base_url = os.environ.get("PEP_OLLAMA_BASE_URL", "http://localhost:11434")
        r = httpx.get(f"{base_url.rstrip('/')}/api/tags", timeout=1.0)
        if r.status_code == 200:
            from pep.models.ollama_client import OllamaLLMClient

            return OllamaLLMClient()
    except Exception:
        pass

    return StubLLMClient()
