"""Bridge between PEP, Vectora, and the LAVAS mesh.

Routes:
  POST /vectora/event          — log an event from a Vectora canvas
  GET  /vectora/events         — recent Vectora events (ring buffer)
  GET  /vectora/pep-state      — PEP introspection + mesh cross-reads
  GET  /vectora/axona-events   — Axona events mirrored
  GET  /vectora/lingora-events — Lingora events mirrored
  GET  /vectora/atria-events   — Atria events mirrored
"""

from __future__ import annotations

import time
from collections import deque
from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()

_EVENTS: deque[dict[str, Any]] = deque(maxlen=200)


class VectoraEvent(BaseModel):
    type: str
    source: str = "vectora"
    payload: dict[str, Any] = {}


@router.post("/vectora/event")
async def post_event(event: VectoraEvent) -> dict[str, Any]:
    record = {"t": time.time(), "type": event.type, "source": event.source, "payload": event.payload}
    _EVENTS.append(record)
    return {"ok": True, "stored": record, "count": len(_EVENTS)}


@router.get("/vectora/events")
async def get_events(limit: int = 40) -> dict[str, Any]:
    return {"count": len(_EVENTS), "items": list(_EVENTS)[-limit:]}


@router.get("/vectora/pep-state")
async def pep_state(request: Request) -> dict[str, Any]:
    out: dict[str, Any] = {
        "t": time.time(), "connected": True, "llm": None, "embeddings": None,
        "runs_recent": 0, "latest_run": None, "vectora_events": len(_EVENTS),
        "axona_events": 0, "lingora_events": 0, "atria_events": 0,
    }
    try:
        llm = getattr(request.app.state, "llm", None)
        if llm: out["llm"] = getattr(llm, "name", "unknown")
    except Exception: pass
    try:
        emb = getattr(request.app.state, "embedder", None)
        if emb: out["embeddings"] = "voyage" if getattr(emb, "using_real_embeddings", False) else "pseudo"
    except Exception: pass
    try:
        store = getattr(request.app.state, "store", None)
        if store:
            runs = store.list_runs(limit=5)
            out["runs_recent"] = len(runs)
            if runs: out["latest_run"] = {"id": str(runs[0].get("id", ""))[:16], "user_input": str(runs[0].get("user_input", ""))[:80]}
    except Exception: pass
    for name, mod in [("axona", "axona_bridge"), ("lingora", "lingora_bridge"), ("atria", "atria_bridge")]:
        try:
            from importlib import import_module
            m = import_module(f"pep.routes.{mod}")
            out[f"{name}_events"] = len(m._EVENTS)
        except Exception: pass
    return out


def _cross_read(mod: str, limit: int) -> dict[str, Any]:
    try:
        from importlib import import_module
        m = import_module(f"pep.routes.{mod}")
        return {"count": len(m._EVENTS), "items": list(m._EVENTS)[-limit:]}
    except Exception as exc:
        return {"count": 0, "items": [], "error": str(exc)[:200]}


@router.get("/vectora/axona-events")
async def axona_events(limit: int = 40) -> dict[str, Any]:
    return _cross_read("axona_bridge", limit)


@router.get("/vectora/lingora-events")
async def lingora_events(limit: int = 40) -> dict[str, Any]:
    return _cross_read("lingora_bridge", limit)


@router.get("/vectora/atria-events")
async def atria_events(limit: int = 40) -> dict[str, Any]:
    return _cross_read("atria_bridge", limit)
