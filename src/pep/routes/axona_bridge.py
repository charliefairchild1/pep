"""Bidirectional bridge between PEP and Axona.

Axona posts cognitive events (flow entered, therapy step, trauma captured, etc.)
into PEP here, and reads PEP's live introspection state (runs, memory size, last
prediction error) back out to drive its own visualizations. A thin API, not a
full messaging bus — the point is to demonstrate that the two halves are a
single system.

Routes:
  POST /axona/event            — log a cognitive event from an Axona canvas
  GET  /axona/events           — recent events (ring buffer)
  GET  /axona/pep-state        — PEP's live introspection snapshot
"""

from __future__ import annotations

import time
from collections import deque
from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()

# In-memory ring buffer. Deliberately not persisted — this is a live telemetry
# channel, not an audit log. Restart = clear.
_EVENTS: deque[dict[str, Any]] = deque(maxlen=200)


class AxonaEvent(BaseModel):
    type: str
    source: str = "axona"
    payload: dict[str, Any] = {}


@router.post("/axona/event")
async def post_event(event: AxonaEvent) -> dict[str, Any]:
    record = {
        "t": time.time(),
        "type": event.type,
        "source": event.source,
        "payload": event.payload,
    }
    _EVENTS.append(record)
    return {"ok": True, "stored": record, "count": len(_EVENTS)}


@router.get("/axona/events")
async def get_events(limit: int = 40) -> dict[str, Any]:
    items = list(_EVENTS)[-limit:]
    return {"count": len(_EVENTS), "items": items}


@router.get("/axona/pep-state")
async def pep_state(request: Request) -> dict[str, Any]:
    """Return PEP's live introspection snapshot so Axona can display it.

    Also includes cross-reads from Lingora — the number of Lingora events and
    the type of the most recent one — so Axona can surface Lingora activity
    in its bridge panel and treat Lingora as a first-class peer.
    """
    out: dict[str, Any] = {
        "t": time.time(),
        "connected": True,
        "llm": None,
        "embeddings": None,
        "runs_recent": 0,
        "latest_run": None,
        "axona_events": len(_EVENTS),
        "lingora_events": 0,
        "lingora_latest": None,
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
    # Cross-read Lingora's event buffer (import here to avoid circular import)
    try:
        from pep.routes.lingora_bridge import _EVENTS as _LINGORA_EVENTS
        out["lingora_events"] = len(_LINGORA_EVENTS)
        if _LINGORA_EVENTS:
            last = list(_LINGORA_EVENTS)[-1]
            out["lingora_latest"] = {
                "type": last.get("type"),
                "t": last.get("t"),
            }
    except Exception:
        pass
    # Cross-read Atria's event buffer
    try:
        from pep.routes.atria_bridge import _EVENTS as _ATRIA_EVENTS
        out["atria_events"] = len(_ATRIA_EVENTS)
        if _ATRIA_EVENTS:
            last = list(_ATRIA_EVENTS)[-1]
            out["atria_latest"] = {
                "type": last.get("type"),
                "t": last.get("t"),
            }
    except Exception:
        pass
    return out


@router.get("/axona/lingora-events")
async def lingora_events(limit: int = 40) -> dict[str, Any]:
    """Mirror Lingora's event buffer so Axona's bridge panel can display it."""
    try:
        from pep.routes.lingora_bridge import _EVENTS as _LINGORA_EVENTS
        items = list(_LINGORA_EVENTS)[-limit:]
        return {"count": len(_LINGORA_EVENTS), "items": items}
    except Exception as exc:
        return {"count": 0, "items": [], "error": str(exc)[:200]}


@router.get("/axona/atria-events")
async def atria_events(limit: int = 40) -> dict[str, Any]:
    """Mirror Atria's event buffer so Axona's bridge panel can display it."""
    try:
        from pep.routes.atria_bridge import _EVENTS as _ATRIA_EVENTS
        items = list(_ATRIA_EVENTS)[-limit:]
        return {"count": len(_ATRIA_EVENTS), "items": items}
    except Exception as exc:
        return {"count": 0, "items": [], "error": str(exc)[:200]}
