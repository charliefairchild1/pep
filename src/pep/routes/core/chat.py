"""POST /chat — main entry point. POST /chat/compare — side-by-side raw vs PEP."""

from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from pep.core.loop import run_turn, stream_turn
from pep.memory.store import MemoryStore
from pep.policies.pep_full import PEPFullPolicy
from pep.policies.raw_ai import RawAIPolicy
from pep.schemas.input_schema import UserInput

router = APIRouter()


class ChatRequest(BaseModel):
    text: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    response: str
    packet_id: str
    state_before: dict
    state_after: dict
    packet: dict


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request) -> ChatResponse:
    store = request.app.state.store
    embedder = request.app.state.embedder
    llm = request.app.state.llm

    user_input = UserInput(text=req.text, session_id=req.session_id)
    packet, response, state_before, state_after = run_turn(
        user_input=user_input,
        store=store,
        embedder=embedder,
        llm=llm,
    )

    return ChatResponse(
        response=response,
        packet_id=packet.id,
        state_before=state_before.model_dump(),
        state_after=state_after.model_dump(),
        packet=packet.model_dump(),
    )


def _run_raw_turn(user_input: UserInput, embedder, llm):
    """Synchronous wrapper for the raw AI policy. Run in a worker thread."""
    raw_store = MemoryStore(":memory:")
    try:
        return RawAIPolicy().run_turn(
            user_input=user_input,
            store=raw_store,
            embedder=embedder,
            llm=llm,
        )
    finally:
        raw_store.close()


def _run_pep_turn(user_input: UserInput, store: MemoryStore, embedder, llm):
    """Synchronous wrapper for the PEP policy. Run in a worker thread."""
    return PEPFullPolicy().run_turn(
        user_input=user_input,
        store=store,
        embedder=embedder,
        llm=llm,
    )


def _sse_format(event: str, data: dict) -> str:
    """Format one Server-Sent Event."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@router.post("/chat/stream")
async def chat_stream(req: ChatRequest, request: Request):
    """Stream a single PEP turn via Server-Sent Events.

    Runs the full PEP overlay (Interpreter, State, Predict, Reactivate, Score,
    Package) synchronously, then streams the LLM response chunk-by-chunk.
    After the model finishes, persists memory + state and emits a final
    "done" event with the full packet trace.

    Event types:
      - trace_pre: PEP packet before the LLM call (which memories activated)
      - chunk: one piece of the streaming response text
      - done: final state after memory updates, with the full response
    """
    store = request.app.state.store
    embedder = request.app.state.embedder
    llm = request.app.state.llm
    user_input = UserInput(text=req.text, session_id=req.session_id)

    async def event_generator():
        # Run the synchronous generator in a worker thread so we don't block the loop
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
            event_name = event.get("event", "message")
            yield _sse_format(event_name, event)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disable nginx buffering if proxied
        },
    )


class DialogueRequest(BaseModel):
    opening: str = "Hello — what's on your mind?"
    topic: str = ""  # meta-context shared by both agents (not a chat message)
    turns: int | None = 30
    personas: str = "curious_and_expert"
    fresh: bool = True
    auto_continue: bool = False


@router.post("/dialogue/stream")
async def dialogue_stream(req: DialogueRequest, request: Request):
    """Stream a dialogue between N PEP agents via Server-Sent Events.

    Picks the right runner based on the persona set's agent count: 2 agents
    use the simple alternating dialogue; 3+ use the round-robin multi-agent
    runner where every non-speaker observes each turn via the PEP overlay.
    Each agent's session id is `dialogue:<name>`. After the dialogue runs,
    the existing Sky View / Categories / Coherence tabs can inspect any
    individual agent or the joint memory.
    """
    from pep.dialogue import (
        DEFAULT_AGENT_NAMES,
        DEFAULT_PERSONAS,
        Agent as DialogueAgent,
        stream_dialogue,
        stream_multi_agent_dialogue,
    )

    if req.personas not in DEFAULT_PERSONAS:
        async def err():
            yield _sse_format("error", {"message": f"unknown personas: {req.personas}"})
        return StreamingResponse(err(), media_type="text/event-stream")

    persona_list = DEFAULT_PERSONAS[req.personas]
    n_agents = len(persona_list)
    if n_agents < 2 or n_agents > len(DEFAULT_AGENT_NAMES):
        async def err():
            yield _sse_format("error", {"message": f"unsupported agent count: {n_agents}"})
        return StreamingResponse(err(), media_type="text/event-stream")

    store = request.app.state.store
    embedder = request.app.state.embedder
    llm = request.app.state.llm

    if req.fresh:
        for name in DEFAULT_AGENT_NAMES[:n_agents]:
            store.clear_session(f"dialogue:{name}")

    agents = [
        DialogueAgent(
            name=DEFAULT_AGENT_NAMES[i],
            persona=persona_list[i],
            store=store, embedder=embedder, llm=llm, topic=req.topic,
        )
        for i in range(n_agents)
    ]

    # Reset the stop flag at the start of every dialogue
    stop_event = request.app.state.dialogue_stop
    stop_event.clear()

    async def event_generator():
        loop = asyncio.get_event_loop()
        queue: asyncio.Queue = asyncio.Queue()
        SENTINEL = object()

        # auto_continue → unlimited turns (None), only Stop ends it
        effective_turns = None if req.auto_continue else req.turns

        def producer():
            try:
                # Pick the right runner based on agent count
                if n_agents == 2:
                    iterator = stream_dialogue(
                        agents[0], agents[1],
                        opening=req.opening, turns=effective_turns,
                        should_stop=stop_event.is_set,
                    )
                else:
                    iterator = stream_multi_agent_dialogue(
                        agents,
                        opening=req.opening, turns=effective_turns,
                        should_stop=stop_event.is_set,
                    )
                for event in iterator:
                    asyncio.run_coroutine_threadsafe(queue.put(event), loop)
            except Exception as e:
                asyncio.run_coroutine_threadsafe(
                    queue.put({"event": "error", "message": str(e)}), loop
                )
            finally:
                asyncio.run_coroutine_threadsafe(queue.put(SENTINEL), loop)

        loop.run_in_executor(None, producer)

        # Send the opening as the first event so the UI can render it
        yield _sse_format("opening", {"message": req.opening, "personas": req.personas})

        while True:
            event = await queue.get()
            if event is SENTINEL:
                break
            event_name = event.get("event", "message")
            yield _sse_format(event_name, event)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/dialogue/personas")
async def list_personas() -> dict:
    """List available default persona sets (2 to N agents per set)."""
    from pep.dialogue import DEFAULT_AGENT_NAMES, DEFAULT_PERSONAS
    out: dict[str, dict] = {}
    for name, personas in DEFAULT_PERSONAS.items():
        agents = []
        for i, p in enumerate(personas):
            agent_name = DEFAULT_AGENT_NAMES[i] if i < len(DEFAULT_AGENT_NAMES) else f"Agent{i+1}"
            agents.append({"name": agent_name, "persona": p})
        out[name] = {
            "agents": agents,
            "count": len(agents),
        }
    return out


@router.post("/dialogue/stop")
async def stop_dialogue(request: Request) -> dict:
    """Signal a running dialogue to stop after the current turn finishes."""
    request.app.state.dialogue_stop.set()
    return {"stopped": True}


@router.post("/chat/compare")
async def chat_compare(req: ChatRequest, request: Request) -> dict:
    """Run the same input through both raw AI (no PEP) and PEP+AI in parallel.

    The raw AI uses an isolated in-memory store so it stays truly amnesiac
    across turns. PEP uses the persistent server store and gets the full loop.
    The two policies run concurrently in worker threads so the wall-clock
    time per turn is roughly max(raw_time, pep_time) instead of their sum —
    a meaningful speedup when each LLM call takes a few seconds.

    Returns both responses side-by-side so the UI can render them in two columns.
    """
    store = request.app.state.store
    embedder = request.app.state.embedder
    llm = request.app.state.llm

    user_input = UserInput(text=req.text, session_id=req.session_id)

    raw_result, pep_result = await asyncio.gather(
        asyncio.to_thread(_run_raw_turn, user_input, embedder, llm),
        asyncio.to_thread(_run_pep_turn, user_input, store, embedder, llm),
    )

    return {
        "raw": {
            "response": raw_result.response,
            "policy": "raw_ai",
        },
        "pep": {
            "response": pep_result.response,
            "policy": "pep_full",
            "packet_id": pep_result.packet.id,
            "state_after": pep_result.state_after.model_dump(),
            "packet": pep_result.packet.model_dump(),
        },
    }
