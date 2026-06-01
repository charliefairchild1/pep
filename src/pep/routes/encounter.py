"""/encounter — focused first-contact page.

Standalone atmospheric encounter with a single alien. Same cognitive engine
architecture as /axona/mind, simplified for one mind, with strong
scene-setting. Tests substrate-independence: can two minds with different
substrates find a shared workspace?
"""
import os

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()
_DIST = os.path.join(os.path.dirname(__file__), "..", "..", "..", "dist")


@router.get("/encounter", response_class=HTMLResponse)
async def encounter() -> HTMLResponse:
    try:
        return HTMLResponse(open(os.path.join(_DIST, "encounter.html"), encoding="utf-8").read())
    except OSError:
        return HTMLResponse("<h1>The Encounter</h1><p>encounter.html not found in dist/.</p>")
