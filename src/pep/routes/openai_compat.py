"""OpenAI-compatible chat completions endpoint.

Wraps the full PEP overlay (interpret → state → predict → reactivate → score
→ package → base AI → update memory → decay) behind the standard OpenAI
`/v1/chat/completions` request and response shape, so any tool that speaks
OpenAI's API can use PEP transparently as a memory layer.

This is what makes PEP a real overlay rather than just a demo: now you can
plug it into Open WebUI, Cursor, custom scripts, or any chat client that
already supports OpenAI-compatible APIs. The base AI underneath stays
Ollama (or whatever LLMClient is configured); PEP adds the memory + state
+ retrieval + everything else, and the client never knows.

Usage from a client:
    POST /v1/chat/completions
    {
      "model": "pep",
      "messages": [
        {"role": "system", "content": "..."},   # optional, ignored if PEP loop runs
        {"role": "user", "content": "..."}
      ],
      "stream": false                           # set true for SSE streaming
    }

Returns standard OpenAI response shape (or SSE chunks if stream=true).
The session_id is derived from a custom `pep_session` field on the request,
or defaults to "openai_compat" so multiple clients can share the same overlay.
"""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field

from pep.core.loop import run_turn, stream_turn
from pep.schemas.input_schema import UserInput

router = APIRouter()


class OpenAIMessage(BaseModel):
    role: str
    content: str


class OpenAIChatRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, protected_namespaces=())

    model: str = "pep"
    messages: list[OpenAIMessage]
    stream: bool = False
    # PEP extension: which session to attach this conversation to.
    # Defaults to "openai_compat" so all calls without a session id share
    # one running PEP overlay (i.e. memory accumulates across calls).
    pep_session: str | None = Field(default=None)
    # Standard OpenAI fields we accept and ignore (for compatibility):
    temperature: float | None = None
    max_tokens: int | None = None
    top_p: float | None = None
    n: int | None = None
    stop: Any | None = None
    presence_penalty: float | None = None
    frequency_penalty: float | None = None
    user: str | None = None


def _extract_user_text(messages: list[OpenAIMessage]) -> str:
    """Pull the most recent user message out of the OpenAI message list.

    PEP runs over a single user input at a time (the rest is in PEP's own
    memory). If the client sent multi-turn history, we use only the most
    recent user message — PEP's memory will fill in any prior context.
    """
    for msg in reversed(messages):
        if msg.role == "user":
            return msg.content
    return ""


def _make_openai_response(
    *,
    response_text: str,
    model: str,
    request_id: str,
    completion_tokens: int,
    prompt_tokens: int,
) -> dict:
    """Build a standard OpenAI chat completion response object."""
    return {
        "id": f"chatcmpl-{request_id}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_text,
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
    }


def _make_chunk_event(
    *,
    delta: str,
    model: str,
    request_id: str,
    finish_reason: str | None = None,
) -> str:
    """Build one OpenAI streaming chunk in the standard SSE format."""
    payload = {
        "id": f"chatcmpl-{request_id}",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "delta": {"content": delta} if delta else {},
                "finish_reason": finish_reason,
            }
        ],
    }
    return f"data: {json.dumps(payload)}\n\n"


@router.post("/v1/chat/completions")
async def chat_completions(req: OpenAIChatRequest, request: Request):
    """OpenAI-compatible chat completions endpoint, fronted by PEP.

    Drops the OpenAI request shape into PEP's loop, returns the OpenAI
    response shape. Streaming via stream=true uses standard OpenAI SSE
    chunks. Multi-turn history is implicit through PEP's memory — the
    client only needs to send the current user message.
    """
    user_text = _extract_user_text(req.messages)
    if not user_text:
        return {
            "error": {
                "message": "no user message provided",
                "type": "invalid_request_error",
            }
        }

    session_id = req.pep_session or "openai_compat"
    user_input = UserInput(text=user_text, session_id=session_id)

    store = request.app.state.store
    embedder = request.app.state.embedder
    llm = request.app.state.llm

    request_id = uuid.uuid4().hex[:24]

    if not req.stream:
        # Non-streaming: run the full loop synchronously, return the response
        loop = asyncio.get_event_loop()

        def runner():
            packet, response, _, _ = run_turn(
                user_input=user_input,
                store=store,
                embedder=embedder,
                llm=llm,
            )
            return packet, response

        packet, response = await loop.run_in_executor(None, runner)
        return _make_openai_response(
            response_text=response,
            model=req.model,
            request_id=request_id,
            prompt_tokens=len(user_text.split()),
            completion_tokens=len(response.split()),
        )

    # Streaming path: SSE chunks in OpenAI format
    async def event_generator():
        loop = asyncio.get_event_loop()
        queue: asyncio.Queue = asyncio.Queue()
        SENTINEL = object()

        def producer():
            try:
                for event in stream_turn(
                    user_input=user_input,
                    store=store,
                    embedder=embedder,
                    llm=llm,
                ):
                    asyncio.run_coroutine_threadsafe(queue.put(event), loop)
            except Exception as e:
                asyncio.run_coroutine_threadsafe(
                    queue.put({"event": "error", "message": str(e)}), loop
                )
            finally:
                asyncio.run_coroutine_threadsafe(queue.put(SENTINEL), loop)

        loop.run_in_executor(None, producer)

        while True:
            event = await queue.get()
            if event is SENTINEL:
                break
            if event.get("event") == "chunk":
                yield _make_chunk_event(
                    delta=event.get("text", ""),
                    model=req.model,
                    request_id=request_id,
                )
            elif event.get("event") == "done":
                yield _make_chunk_event(
                    delta="",
                    model=req.model,
                    request_id=request_id,
                    finish_reason="stop",
                )
            elif event.get("event") == "error":
                yield _make_chunk_event(
                    delta=f"\n[error: {event.get('message','?')}]",
                    model=req.model,
                    request_id=request_id,
                    finish_reason="stop",
                )

        # OpenAI streaming responses end with a literal "data: [DONE]\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )


@router.get("/v1/models")
async def list_models() -> dict:
    """OpenAI-compatible models endpoint. Lists `pep` as the only model.

    Some clients (Open WebUI, etc.) call this on connect to populate
    their model selector. We return PEP as a single virtual model that
    represents the full overlay over whatever base AI is configured.
    """
    return {
        "object": "list",
        "data": [
            {
                "id": "pep",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "pep",
            }
        ],
    }
