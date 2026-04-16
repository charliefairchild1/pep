"""OllamaLLMClient tests using a mocked httpx transport.

We never hit a real Ollama daemon. The MockTransport responds the way Ollama
would, so we exercise the full code path including JSON parsing and error
handling — without needing the daemon installed.
"""

from __future__ import annotations

import httpx
import pytest

from pep.models.ollama_client import OllamaLLMClient
from pep.schemas.input_schema import InterpretedInput, Prediction
from pep.schemas.pep_packet import (
    ActivationTrace,
    PEPPacket,
    ResidualReport,
)
from pep.schemas.state_schema import State


def _empty_packet(text: str = "hello") -> PEPPacket:
    return PEPPacket(
        raw_input=text,
        interpreted=InterpretedInput(intent="test", topic="test", task_type="ask_question"),
        prediction=Prediction(),
        state=State.neutral(),
        residual=ResidualReport(),
        activation_trace=ActivationTrace(),
    )


def _ok_chat_handler(content: str = "Hello from Ollama!"):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/chat"
        body = request.read()
        assert b"messages" in body
        return httpx.Response(
            200,
            json={
                "model": "llama3.2:3b",
                "created_at": "2026-04-09T00:00:00Z",
                "message": {"role": "assistant", "content": content},
                "done": True,
            },
        )
    return handler


def _error_handler(status: int = 404):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, json={"error": "model not found"})
    return handler


def test_ollama_complete_returns_assistant_text() -> None:
    transport = httpx.MockTransport(_ok_chat_handler("Hi there from llama"))
    fake_client = httpx.Client(transport=transport)

    client = OllamaLLMClient(client=fake_client)
    response = client.complete(_empty_packet("hello"))
    assert "Hi there from llama" in response


def test_ollama_support_returns_text_when_enabled() -> None:
    """When support_calls=True, support() actually hits the model."""
    transport = httpx.MockTransport(_ok_chat_handler("structured response"))
    fake_client = httpx.Client(transport=transport)

    client = OllamaLLMClient(client=fake_client, support_calls=True)
    result = client.support(system="be a json bot", user="give me json")
    assert "structured response" in result


def test_ollama_support_disabled_by_default() -> None:
    """Default support_calls=False — return "" without hitting the daemon.

    This is the latency win: small local models are too slow to drive the
    supporting modules on every turn, so we let them use heuristics by default.
    """
    transport = httpx.MockTransport(_ok_chat_handler("would-be response"))
    fake_client = httpx.Client(transport=transport)

    client = OllamaLLMClient(client=fake_client)  # support_calls defaults to False
    result = client.support(system="x", user="y")
    assert result == ""


def test_ollama_support_returns_empty_on_error_when_enabled() -> None:
    """Even with support_calls=True, errors fall through to "" so callers
    can use their heuristic fallback path."""
    transport = httpx.MockTransport(_error_handler(500))
    fake_client = httpx.Client(transport=transport)

    client = OllamaLLMClient(client=fake_client, support_calls=True)
    result = client.support(system="x", user="y")
    assert result == ""


def test_ollama_complete_returns_friendly_message_on_404() -> None:
    """If the model isn't pulled, complete() should return a helpful error
    string instead of raising — so the chat UI can display it cleanly."""
    transport = httpx.MockTransport(_error_handler(404))
    fake_client = httpx.Client(transport=transport)

    client = OllamaLLMClient(client=fake_client, strong_model="missing-model")
    response = client.complete(_empty_packet())
    assert "ollama" in response.lower()
    assert "missing-model" in response


def test_ollama_complete_returns_message_on_unreachable() -> None:
    """If the daemon is unreachable, complete() should return a clear message."""
    def boom(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("daemon down")

    transport = httpx.MockTransport(boom)
    fake_client = httpx.Client(transport=transport)

    client = OllamaLLMClient(client=fake_client)
    response = client.complete(_empty_packet())
    assert "unreachable" in response.lower() or "ollama" in response.lower()


def test_ollama_client_is_real_flag() -> None:
    transport = httpx.MockTransport(_ok_chat_handler())
    client = OllamaLLMClient(client=httpx.Client(transport=transport))
    assert client.is_real is True
    assert client.name == "ollama"
