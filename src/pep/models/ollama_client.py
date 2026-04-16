"""Local LLM client backed by Ollama (http://localhost:11434).

This is the "free real AI" path: PEP runs a small local model (default
llama3.2:3b) instead of paying for API calls. Implements the same
LLMClient protocol as StubLLMClient and AnthropicLLMClient, so PEP's
core loop is unchanged — only the LLM at the bottom of the stack swaps.

**Latency note:** small local models are slow (3-5s per call on Mac mini
for llama3.2:3b). PEP normally makes 5+ supporting LLM calls per turn
(Interpreter, Predictor, State Modulator, Updater face generation,
Trajectory scorer) plus the actual response — that adds up to 15-25s
per turn, which is too slow for interactive use.

So by default `support_calls=False`: the supporting modules fall back
to their fast heuristics, and only `complete()` actually hits Ollama.
The PEP overlay (memory + retrieval + state + reactivation) still runs
fully — it just uses heuristics instead of LLM calls for the parts that
don't need a real model. PEP per-turn time drops to ~3-5s.

If you have a powerful local model (or just want LLM-driven supporting
modules anyway), set `PEP_OLLAMA_SUPPORT_CALLS=1`.

Configuration via env vars:
  PEP_OLLAMA_BASE_URL       default: http://localhost:11434
  PEP_OLLAMA_STRONG_MODEL   default: llama3.2:3b   (used by complete())
  PEP_OLLAMA_CHEAP_MODEL    default: llama3.2:3b   (used by support() if enabled)
  PEP_OLLAMA_SUPPORT_CALLS  default: 0 (disabled)  (set to 1 to enable)
"""

from __future__ import annotations

import json
import os
from typing import Iterator

import httpx

from pep.models.llm_client import ModelTier, _format_packet_for_llm
from pep.schemas.pep_packet import PEPPacket


def _env_bool(name: str, default: bool = False) -> bool:
    val = os.environ.get(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


class OllamaLLMClient:
    """Talks to a local Ollama daemon. Free, no API costs, runs on the host."""

    name = "ollama"
    is_real = True

    def __init__(
        self,
        base_url: str | None = None,
        strong_model: str | None = None,
        cheap_model: str | None = None,
        timeout: float = 120.0,
        support_calls: bool | None = None,
        client: httpx.Client | None = None,
    ):
        self.base_url = (
            base_url
            or os.environ.get("PEP_OLLAMA_BASE_URL", "http://localhost:11434")
        ).rstrip("/")
        self._models: dict[ModelTier, str] = {
            "strong": strong_model or os.environ.get("PEP_OLLAMA_STRONG_MODEL", "llama3.2:3b"),
            "cheap": cheap_model or os.environ.get("PEP_OLLAMA_CHEAP_MODEL", "llama3.2:3b"),
        }
        # Support calls disabled by default for latency. The supporting modules
        # have heuristic fallbacks that work fine; only complete() needs the model.
        if support_calls is None:
            support_calls = _env_bool("PEP_OLLAMA_SUPPORT_CALLS", False)
        self._support_calls = support_calls
        self._client = client or httpx.Client(timeout=timeout)

    def complete(self, packet: PEPPacket) -> str:
        """The strong-model call: hands the prepared PEPPacket to the local model."""
        system, user = _format_packet_for_llm(packet)
        try:
            return self._call(self._models["strong"], system, user)
        except httpx.HTTPStatusError as e:
            return (
                f"[ollama error: HTTP {e.response.status_code}] "
                f"Is the model '{self._models['strong']}' pulled? "
                f"Run: ollama pull {self._models['strong']}"
            )
        except httpx.HTTPError as e:
            return f"[ollama unreachable: {e}]"
        except Exception as e:
            return f"[ollama error: {e}]"

    def stream_complete(self, packet: PEPPacket) -> Iterator[str]:
        """Stream the response chunk-by-chunk via Ollama's NDJSON streaming.

        Yields each new content fragment as it arrives. The full response is
        the concatenation of all yielded chunks. On any error, yields a single
        chunk containing the error message so the UI can display it.
        """
        system, user = _format_packet_for_llm(packet)
        payload = {
            "model": self._models["strong"],
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": True,
            "options": {"temperature": 0.7},
        }
        try:
            with self._client.stream(
                "POST", f"{self.base_url}/api/chat", json=payload
            ) as r:
                r.raise_for_status()
                for line in r.iter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    msg = chunk.get("message") or {}
                    content = msg.get("content")
                    if content:
                        yield content
                    if chunk.get("done"):
                        break
        except httpx.HTTPStatusError as e:
            yield (
                f"[ollama error: HTTP {e.response.status_code}] "
                f"Is the model '{self._models['strong']}' pulled? "
                f"Run: ollama pull {self._models['strong']}"
            )
        except httpx.HTTPError as e:
            yield f"[ollama unreachable: {e}]"
        except Exception as e:
            yield f"[ollama error: {e}]"

    def complete_raw(self, *, system: str, user: str) -> str:
        """Strong-model call with raw system+user strings (no PEPPacket).

        Always actually hits the model — not gated by support_calls. Used by
        the dialogue Agent to send a natural conversation prompt that doesn't
        leak PEP internals into the LLM's context.
        """
        try:
            return self._call(self._models["strong"], system, user)
        except httpx.HTTPStatusError as e:
            return (
                f"[ollama error: HTTP {e.response.status_code}] "
                f"Is the model '{self._models['strong']}' pulled? "
                f"Run: ollama pull {self._models['strong']}"
            )
        except httpx.HTTPError as e:
            return f"[ollama unreachable: {e}]"
        except Exception as e:
            return f"[ollama error: {e}]"

    def support(self, *, system: str, user: str, model_tier: ModelTier = "cheap") -> str:
        """The cheap structured call.

        Disabled by default for Ollama (returns "" so callers fall back to
        their heuristic path). With small local models the latency hit isn't
        worth it for the supporting modules — heuristics are fast and good
        enough. Enable via PEP_OLLAMA_SUPPORT_CALLS=1.
        """
        if not self._support_calls:
            return ""
        try:
            return self._call(self._models[model_tier], system, user)
        except Exception:
            return ""

    def _call(self, model: str, system: str, user: str) -> str:
        r = self._client.post(
            f"{self.base_url}/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "stream": False,
                "options": {"temperature": 0.7},
            },
        )
        r.raise_for_status()
        data = r.json()
        # Ollama /api/chat returns {"message": {"role": "assistant", "content": "..."}}
        msg = data.get("message", {})
        content = msg.get("content", "")
        return content or "(no content)"
