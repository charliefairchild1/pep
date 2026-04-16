"""Bidirectional bridge between PEP and Lingora.

Mirrors axona_bridge — Lingora canvases post cognitive/linguistic events up to
PEP, and read PEP's live introspection state back down. The point is to make
Lingora part of the same living system as PEP and Axona rather than a
stand-alone demo.

Routes:
  POST /lingora/event      — log a linguistic event from a Lingora canvas
  GET  /lingora/events     — recent events (ring buffer)
  GET  /lingora/pep-state  — PEP's live introspection snapshot for Lingora
"""

from __future__ import annotations

import time
from collections import deque
from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()

_EVENTS: deque[dict[str, Any]] = deque(maxlen=200)


class LingoraEvent(BaseModel):
    type: str
    source: str = "lingora"
    payload: dict[str, Any] = {}


@router.post("/lingora/event")
async def post_event(event: LingoraEvent) -> dict[str, Any]:
    record = {
        "t": time.time(),
        "type": event.type,
        "source": event.source,
        "payload": event.payload,
    }
    _EVENTS.append(record)
    return {"ok": True, "stored": record, "count": len(_EVENTS)}


@router.get("/lingora/events")
async def get_events(limit: int = 40) -> dict[str, Any]:
    items = list(_EVENTS)[-limit:]
    return {"count": len(_EVENTS), "items": items}


@router.get("/lingora/pep-state")
async def pep_state(request: Request) -> dict[str, Any]:
    """PEP live introspection plus cross-read of Axona's event buffer."""
    out: dict[str, Any] = {
        "t": time.time(),
        "connected": True,
        "llm": None,
        "embeddings": None,
        "runs_recent": 0,
        "latest_run": None,
        "lingora_events": len(_EVENTS),
        "axona_events": 0,
        "axona_latest": None,
        "atria_events": 0,
        "atria_latest": None,
    }
    try:
        llm = getattr(request.app.state, "llm", None)
        if llm is not None:
            out["llm"] = getattr(llm, "name", "unknown")
    except Exception:
        pass
    try:
        emb = getattr(request.app.state, "embedder", None)
        if emb is not None:
            out["embeddings"] = (
                "voyage" if getattr(emb, "using_real_embeddings", False) else "pseudo"
            )
    except Exception:
        pass
    try:
        store = getattr(request.app.state, "store", None)
        if store is not None:
            runs = store.list_runs(limit=5)
            out["runs_recent"] = len(runs)
            if runs:
                latest = runs[0]
                out["latest_run"] = {
                    "id": str(latest.get("id", ""))[:16],
                    "user_input": str(latest.get("user_input", ""))[:80],
                }
    except Exception as exc:
        out["store_error"] = str(exc)[:200]
    try:
        from pep.routes.axona_bridge import _EVENTS as _AXONA_EVENTS
        out["axona_events"] = len(_AXONA_EVENTS)
        if _AXONA_EVENTS:
            last = list(_AXONA_EVENTS)[-1]
            out["axona_latest"] = {"type": last.get("type"), "t": last.get("t")}
    except Exception:
        pass
    try:
        from pep.routes.atria_bridge import _EVENTS as _ATRIA_EVENTS
        out["atria_events"] = len(_ATRIA_EVENTS)
        if _ATRIA_EVENTS:
            last = list(_ATRIA_EVENTS)[-1]
            out["atria_latest"] = {"type": last.get("type"), "t": last.get("t")}
    except Exception:
        pass
    return out


@router.get("/lingora/axona-events")
async def axona_events(limit: int = 40) -> dict[str, Any]:
    """Mirror Axona's event buffer so Lingora's bridge panel can display it."""
    try:
        from pep.routes.axona_bridge import _EVENTS as _AXONA_EVENTS
        items = list(_AXONA_EVENTS)[-limit:]
        return {"count": len(_AXONA_EVENTS), "items": items}
    except Exception as exc:
        return {"count": 0, "items": [], "error": str(exc)[:200]}


@router.get("/lingora/atria-events")
async def atria_events(limit: int = 40) -> dict[str, Any]:
    """Mirror Atria's event buffer so Lingora's bridge panel can display it."""
    try:
        from pep.routes.atria_bridge import _EVENTS as _ATRIA_EVENTS
        items = list(_ATRIA_EVENTS)[-limit:]
        return {"count": len(_ATRIA_EVENTS), "items": items}
    except Exception as exc:
        return {"count": 0, "items": [], "error": str(exc)[:200]}
