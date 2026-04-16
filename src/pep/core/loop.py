"""The full PEP loop wired together. One function: run a turn.

This is what the FastAPI /chat route calls.
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Iterator

from pep.core.interpreter import interpret
from pep.core.packager import package
from pep.core.predictor import predict
from pep.core.reactivator import reactivate
from pep.core.residuals import score_residual
from pep.core.state import estimate_state
from pep.core.updater import update_memory
from pep.embed import Embedder
from pep.memory.store import MemoryStore
from pep.models.llm_client import LLMClient
from pep.schemas.input_schema import UserInput
from pep.schemas.pep_packet import PEPPacket
from pep.schemas.state_schema import State


@contextmanager
def _timed(metrics: dict[str, float], key: str):
    start = time.perf_counter()
    try:
        yield
    finally:
        metrics[key] = round(time.perf_counter() - start, 4)


def _prior_expected_entities(store: MemoryStore, session_id: str) -> list[str]:
    """Tags from memories activated in the most recent run for this session.

    These become the Predictor's `expected_entities` — what the system already
    knew before this turn. Anything *new* in the current turn is then genuine
    surprise rather than just being ignored by the residual scorer.
    """
    runs = store.list_runs(session_id=session_id, limit=1)
    if not runs:
        return []
    last_run = store.get_run(runs[0]["id"])
    if not last_run:
        return []
    packet = last_run.get("packet") or {}
    selected = packet.get("selected_memories") or []
    tags: list[str] = []
    for mem in selected:
        for t in mem.get("tags", []) or []:
            if t and t not in tags:
                tags.append(t)
    return tags[:30]


def run_turn(
    *,
    user_input: UserInput,
    store: MemoryStore,
    embedder: Embedder,
    llm: LLMClient,
) -> tuple[PEPPacket, str, State, State]:
    """Execute one full PEP turn. Returns (packet, response, state_before, state_after)."""
    metrics: dict[str, float] = {}
    state_before = store.latest_state(user_input.session_id)
    prior_known = _prior_expected_entities(store, user_input.session_id)

    # 1. Interpret  (LLM if real client, else heuristic)
    with _timed(metrics, "interpret_s"):
        interpreted = interpret(user_input, llm=llm)

    # 2. Modulate state  (LLM if real client, else heuristic; always smoothed)
    with _timed(metrics, "state_s"):
        state_after = estimate_state(state_before, user_input, interpreted, llm=llm)

    # 3. Predict  (LLM if real client, else heuristic)
    with _timed(metrics, "predict_s"):
        prediction = predict(
            interpreted,
            state_after,
            prior_expected_entities=prior_known,
            llm=llm,
        )

    # 4. Reactivate memory
    with _timed(metrics, "reactivate_s"):
        activated, trace = reactivate(
            store=store,
            embedder=embedder,
            interpreted=interpreted,
            prediction=prediction,
            state=state_after,
            session_id=user_input.session_id,
        )

    # 5. Score residual
    with _timed(metrics, "residual_s"):
        residual = score_residual(
            interpreted=interpreted,
            prediction=prediction,
            state=state_after,
        )

    # 6. Package
    packet = package(
        user_input=user_input,
        interpreted=interpreted,
        prediction=prediction,
        state=state_after,
        activated=activated,
        activation_trace=trace,
        residual=residual,
    )
    packet.metrics = metrics

    # 7. Hand off to base AI
    with _timed(metrics, "complete_s"):
        response = llm.complete(packet)

    # 8. Update memory  (LLM if real client, else heuristic)
    #    Storage is gated by the COMBINED novelty + trajectory score (PTO 2G).
    with _timed(metrics, "update_s"):
        update_memory(
            store=store,
            user_input=user_input,
            interpreted=interpreted,
            assistant_response=response,
            residual=residual,
            activated_ids=[m.id for m in activated],
            llm=llm,
        )

    # 9. Per-turn decay (PTO 2G option (c)): memories that weren't just
    #    activated lose a small amount of brightness. Memories that ARE
    #    activated already got a +0.05 bump in `touch_memory`. Net effect:
    #    used memories get brighter, unused memories slowly fade.
    activated_id_set = {m.id for m in activated}
    with _timed(metrics, "decay_s"):
        store.decay_unused_memories(decay=0.005, exclude_ids=activated_id_set)

    turn_number = store.turn_count(user_input.session_id) + 1
    store.log_state(user_input.session_id, turn_number, state_after)
    store.log_run(packet, response, state_before, state_after)

    return packet, response, state_before, state_after


def stream_turn(
    *,
    user_input: UserInput,
    store: MemoryStore,
    embedder: Embedder,
    llm: LLMClient,
) -> Iterator[dict]:
    """Streaming variant of run_turn().

    Yields a sequence of dicts in this order:
      1. {"event": "trace_pre", "packet": <packet snapshot before LLM>} — once
      2. {"event": "chunk", "text": "..."}                              — many times
      3. {"event": "done", "packet": <full packet>, "state_after": ...} — once

    All the PEP overlay work runs synchronously between yields. Memory updates
    and run logging happen AFTER the stream closes, in the final yield.
    Consumers (the SSE endpoint) iterate this generator and forward each event
    to the client.
    """
    metrics: dict[str, float] = {}
    state_before = store.latest_state(user_input.session_id)
    prior_known = _prior_expected_entities(store, user_input.session_id)

    with _timed(metrics, "interpret_s"):
        interpreted = interpret(user_input, llm=llm)
    with _timed(metrics, "state_s"):
        state_after = estimate_state(state_before, user_input, interpreted, llm=llm)
    with _timed(metrics, "predict_s"):
        prediction = predict(
            interpreted, state_after, prior_expected_entities=prior_known, llm=llm,
        )
    with _timed(metrics, "reactivate_s"):
        activated, trace = reactivate(
            store=store, embedder=embedder, interpreted=interpreted,
            prediction=prediction, state=state_after, session_id=user_input.session_id,
        )
    with _timed(metrics, "residual_s"):
        residual = score_residual(
            interpreted=interpreted, prediction=prediction, state=state_after,
        )

    packet = package(
        user_input=user_input, interpreted=interpreted, prediction=prediction,
        state=state_after, activated=activated, activation_trace=trace, residual=residual,
    )
    packet.metrics = metrics

    # Pre-LLM trace event so the UI can render the activated memories immediately
    yield {
        "event": "trace_pre",
        "packet": packet.model_dump(mode="json"),
    }

    # Stream the LLM response chunk by chunk
    chunks: list[str] = []
    stream_start = time.perf_counter()
    for chunk in llm.stream_complete(packet):
        chunks.append(chunk)
        yield {"event": "chunk", "text": chunk}
    metrics["complete_s"] = round(time.perf_counter() - stream_start, 4)

    response = "".join(chunks)

    # Post-LLM: store memory + decay + log
    with _timed(metrics, "update_s"):
        update_memory(
            store=store, user_input=user_input, interpreted=interpreted,
            assistant_response=response, residual=residual,
            activated_ids=[m.id for m in activated], llm=llm,
        )

    activated_id_set = {m.id for m in activated}
    with _timed(metrics, "decay_s"):
        store.decay_unused_memories(decay=0.005, exclude_ids=activated_id_set)

    turn_number = store.turn_count(user_input.session_id) + 1
    store.log_state(user_input.session_id, turn_number, state_after)
    store.log_run(packet, response, state_before, state_after)

    # Final event with the full packet (now including post-LLM metrics)
    yield {
        "event": "done",
        "packet": packet.model_dump(mode="json"),
        "state_before": state_before.model_dump(mode="json"),
        "state_after": state_after.model_dump(mode="json"),
        "response": response,
    }
