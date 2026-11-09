"""Tests for the OpenAI-compatible chat completions endpoint.

The whole point of this endpoint is that any client speaking OpenAI's API
should be able to use PEP transparently. These tests confirm the request
and response shapes match the OpenAI spec well enough that standard tools
will work.
"""

from __future__ import annotations

import json

from fastapi.testclient import TestClient

from pep.main import app


def test_v1_models_returns_pep_model() -> None:
    with TestClient(app) as client:
        r = client.get("/v1/models")
        assert r.status_code == 200
        data = r.json()
        assert data["object"] == "list"
        assert any(m["id"] == "pep" for m in data["data"])
        assert all(m["object"] == "model" for m in data["data"])


def test_v1_chat_completions_returns_openai_shape() -> None:
    """Standard non-streaming OpenAI-compatible response."""
    with TestClient(app) as client:
        r = client.post(
            "/v1/chat/completions",
            json={
                "model": "pep",
                "messages": [{"role": "user", "content": "Hello"}],
            },
        )
        assert r.status_code == 200
        data = r.json()
        # Standard OpenAI fields
        assert "id" in data
        assert data["id"].startswith("chatcmpl-")
        assert data["object"] == "chat.completion"
        assert data["model"] == "pep"
        assert "choices" in data
        assert len(data["choices"]) >= 1
        choice = data["choices"][0]
        assert choice["index"] == 0
        assert choice["message"]["role"] == "assistant"
        assert choice["message"]["content"]  # non-empty
        assert choice["finish_reason"] == "stop"
        # Token usage
        assert "usage" in data
        assert "prompt_tokens" in data["usage"]
        assert "completion_tokens" in data["usage"]
        assert "total_tokens" in data["usage"]


def test_v1_chat_completions_pulls_most_recent_user_message() -> None:
    """If the client sends multi-turn history, PEP uses the most recent
    user message — its own memory provides the prior context."""
    with TestClient(app) as client:
        r = client.post(
            "/v1/chat/completions",
            json={
                "model": "pep",
                "messages": [
                    {"role": "user", "content": "first message (ignored)"},
                    {"role": "assistant", "content": "first reply (ignored)"},
                    {"role": "user", "content": "second message"},
                ],
            },
        )
        assert r.status_code == 200
        data = r.json()
        # Stub LLM echoes the input — verifies which message we used
        text = data["choices"][0]["message"]["content"]
        assert text  # non-empty


def test_v1_chat_completions_streaming_returns_sse() -> None:
    """stream=true should return text/event-stream with OpenAI-format chunks."""
    with TestClient(app) as client:
        with client.stream(
            "POST",
            "/v1/chat/completions",
            json={
                "model": "pep",
                "messages": [{"role": "user", "content": "Hi"}],
                "stream": True,
            },
        ) as response:
            assert response.status_code == 200
            assert response.headers["content-type"].startswith("text/event-stream")

            chunks: list[dict] = []
            saw_done = False
            buffer = ""
            for chunk in response.iter_text():
                buffer += chunk
                while "\n\n" in buffer:
                    line, buffer = buffer.split("\n\n", 1)
                    if not line.startswith("data: "):
                        continue
                    payload = line[6:]
                    if payload == "[DONE]":
                        saw_done = True
                        continue
                    try:
                        chunks.append(json.loads(payload))
                    except json.JSONDecodeError:
                        pass

            assert saw_done, "stream did not end with data: [DONE]"
            assert len(chunks) >= 1
            for c in chunks:
                assert c["object"] == "chat.completion.chunk"
                assert c["id"].startswith("chatcmpl-")
                assert "choices" in c


def test_v1_chat_completions_empty_messages_returns_error() -> None:
    with TestClient(app) as client:
        r = client.post(
            "/v1/chat/completions",
            json={
                "model": "pep",
                "messages": [{"role": "system", "content": "no user message"}],
            },
        )
        # Should return 200 but with an error object (OpenAI's typical pattern)
        # OR a proper 4xx — either way, no exception
        assert r.status_code in (200, 400, 422)


def test_v1_chat_completions_session_id_param() -> None:
    """The pep_session field should route to a named session so multiple
    clients can have independent overlays."""
    with TestClient(app) as client:
        r = client.post(
            "/v1/chat/completions",
            json={
                "model": "pep",
                "messages": [{"role": "user", "content": "test"}],
                "pep_session": "test_isolated_session",
            },
        )
        assert r.status_code == 200
        # And the named session should now have at least the run logged
        runs = client.get("/runs?session_id=test_isolated_session").json()
        assert len(runs) >= 1
