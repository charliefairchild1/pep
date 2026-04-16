"""Bridge between PEP, Atria, Axona, and Lingora.

Atria posts matchmaking-related events (pool built, match chosen, behavior
flag toggled, residual observed, etc.) into PEP here, and reads PEP's live
introspection state plus recent Axona and Lingora events back out. Full mesh
across all three LAVAS front-ends: any surface can see what any other is
doing in real time.

Routes:
  POST /atria/event           — log an event from an Atria canvas
  GET  /atria/events          — recent Atria events (ring buffer)
  GET  /atria/pep-state       — PEP's live introspection + Axona/Lingora cross-reads
  GET  /atria/axona-events    — Axona's recent events, mirrored for Atria's UI
  GET  /atria/lingora-events  — Lingora's recent events, mirrored for Atria's UI
"""

from __future__ import annotations

import time
from collections import deque
from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()

_EVENTS: deque[dict[str, Any]] = deque(maxlen=200)


class AtriaEvent(BaseModel):
    type: str
    source: str = "atria"
    payload: dict[str, Any] = {}


@router.post("/atria/event")
async def post_event(event: AtriaEvent) -> dict[str, Any]:
    record = {
        "t": time.time(),
        "type": event.type,
        "source": event.source,
        "payload": event.payload,
    }
    _EVENTS.append(record)
    return {"ok": True, "stored": record, "count": len(_EVENTS)}


@router.get("/atria/events")
async def get_events(limit: int = 40) -> dict[str, Any]:
    items = list(_EVENTS)[-limit:]
    return {"count": len(_EVENTS), "items": items}


@router.get("/atria/pep-state")
async def pep_state(request: Request) -> dict[str, Any]:
    """PEP live introspection plus cross-reads of Axona and Lingora buffers."""
    out: dict[str, Any] = {
        "t": time.time(),
        "connected": True,
        "llm": None,
        "embeddings": None,
        "runs_recent": 0,
        "latest_run": None,
        "atria_events": len(_EVENTS),
        "axona_events": 0,
        "axona_latest": None,
        "lingora_events": 0,
        "lingora_latest": None,
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
        from pep.routes.lingora_bridge import _EVENTS as _LINGORA_EVENTS
        out["lingora_events"] = len(_LINGORA_EVENTS)
        if _LINGORA_EVENTS:
            last = list(_LINGORA_EVENTS)[-1]
            out["lingora_latest"] = {"type": last.get("type"), "t": last.get("t")}
    except Exception:
        pass
    return out


@router.get("/atria/axona-events")
async def axona_events(limit: int = 40) -> dict[str, Any]:
    """Mirror Axona's event buffer so Atria's bridge panel can display it."""
    try:
        from pep.routes.axona_bridge import _EVENTS as _AXONA_EVENTS
        items = list(_AXONA_EVENTS)[-limit:]
        return {"count": len(_AXONA_EVENTS), "items": items}
    except Exception as exc:
        return {"count": 0, "items": [], "error": str(exc)[:200]}


@router.get("/atria/lingora-events")
async def lingora_events(limit: int = 40) -> dict[str, Any]:
    """Mirror Lingora's event buffer so Atria's bridge panel can display it."""
    try:
        from pep.routes.lingora_bridge import _EVENTS as _LINGORA_EVENTS
        items = list(_LINGORA_EVENTS)[-limit:]
        return {"count": len(_LINGORA_EVENTS), "items": items}
    except Exception as exc:
        return {"count": 0, "items": [], "error": str(exc)[:200]}
