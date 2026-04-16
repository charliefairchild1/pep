"""Tests for stream_complete() across all LLM clients + the SSE endpoint."""

from __future__ import annotations

import json

import httpx
from fastapi.testclient import TestClient

from pep.main import app
from pep.models.llm_client import StubLLMClient
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
        interpreted=InterpretedInput(intent="t", topic="t", task_type="ask_question"),
        prediction=Prediction(),
        state=State.neutral(),
        residual=ResidualReport(),
        activation_trace=ActivationTrace(),
    )


def test_stub_stream_yields_one_chunk() -> None:
    """The stub doesn't stream — it yields the full canned response in one chunk."""
    chunks = list(StubLLMClient().stream_complete(_empty_packet("hi")))
    assert len(chunks) == 1
    assert "[stub-llm]" in chunks[0]


def test_ollama_stream_parses_ndjson_chunks() -> None:
    """OllamaLLMClient.stream_complete should parse NDJSON line-by-line and
    yield each non-empty content fragment."""
    # Build an NDJSON response body that mimics Ollama's streaming format
    chunks_payload = [
        {"message": {"role": "assistant", "content": "Hello"}, "done": False},
        {"message": {"role": "assistant", "content": " world"}, "done": False},
        {"message": {"role": "assistant", "content": "!"}, "done": False},
        {"message": {"role": "assistant", "content": ""}, "done": True},
    ]
    body = "\n".join(json.dumps(c) for c in chunks_payload).encode("utf-8")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/chat"
        # Streaming requests have stream: true in the body
        body_json = json.loads(request.read())
        assert body_json["stream"] is True
        return httpx.Response(
            200,
            content=body,
            headers={"content-type": "application/x-ndjson"},
        )

    transport = httpx.MockTransport(handler)
    fake_client = httpx.Client(transport=transport)

    client = OllamaLLMClient(client=fake_client)
    out = list(client.stream_complete(_empty_packet("hi")))
    # The three non-empty fragments should be yielded; the empty done chunk skipped
    assert out == ["Hello", " world", "!"]


def test_ollama_stream_handles_unreachable() -> None:
    """If the daemon is unreachable, stream_complete yields an error message
    rather than raising — so the UI can display it cleanly."""
    def boom(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("daemon down")

    transport = httpx.MockTransport(boom)
    fake_client = httpx.Client(transport=transport)

    client = OllamaLLMClient(client=fake_client)
    out = list(client.stream_complete(_empty_packet()))
    assert len(out) >= 1
    assert "ollama" in out[0].lower() or "error" in out[0].lower()


def test_chat_stream_endpoint_returns_sse() -> None:
    """End-to-end: POST /chat/stream returns a text/event-stream with chunk
    events and a final done event."""
    with TestClient(app) as client:
        with client.stream(
            "POST",
            "/chat/stream",
            json={"text": "Hello PEP", "session_id": "stream_test"},
        ) as response:
            assert response.status_code == 200
            assert response.headers["content-type"].startswith("text/event-stream")

            # Collect all events
            events: list[tuple[str, dict]] = []
            buffer = ""
            for chunk in response.iter_text():
                buffer += chunk
                while "\n\n" in buffer:
                    block, buffer = buffer.split("\n\n", 1)
                    event_name = "message"
                    data_str = ""
                    for line in block.splitlines():
                        if line.startswith("event: "):
                            event_name = line[7:].strip()
                        elif line.startswith("data: "):
                            data_str += line[6:]
                    if data_str:
                        try:
                            events.append((event_name, json.loads(data_str)))
                        except json.JSONDecodeError:
                            pass

            # Should have at least one trace_pre, at least one chunk, and one done
            event_names = [name for name, _ in events]
            assert "trace_pre" in event_names
            assert "chunk" in event_names
            assert "done" in event_names

            # The done event must include the full packet and response
            done_payload = next(d for n, d in events if n == "done")
            assert "packet" in done_payload
            assert "response" in done_payload
            assert done_payload["response"]
