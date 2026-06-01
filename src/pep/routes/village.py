"""/village — three minds, one substrate, sentences that travel.

Multi-mind demo: three NPCs running the same PEP cognitive engine with
different seed selves. After each conversation turn, a sentence from the
speaking NPC's hippocampus has a chance to propagate to one of the others
(the gossip mechanism). Tests cross-mind sentence propagation, shared
substrate vs distinct identity, and the foundation for Koin reputation
ledgers built on minds that actually remember.
"""
import os

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()
_DIST = os.path.join(os.path.dirname(__file__), "..", "..", "..", "dist")


@router.get("/village", response_class=HTMLResponse)
async def village() -> HTMLResponse:
    try:
        return HTMLResponse(open(os.path.join(_DIST, "village.html"), encoding="utf-8").read())
    except OSError:
        return HTMLResponse("<h1>The Village</h1><p>village.html not found in dist/.</p>")
