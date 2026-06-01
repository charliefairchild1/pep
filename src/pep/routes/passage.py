"""/passage — wordless first contact.

A page where the player communicates with an alien using only signals — small
symbolic buttons — and the alien responds by changing a visual field. No
English exchanged. Tests whether two cognitions with no shared syntax can
find a stable rhythm of communication through tagged signals and gauge
readouts alone.
"""
import os

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()
_DIST = os.path.join(os.path.dirname(__file__), "..", "..", "..", "dist")


@router.get("/passage", response_class=HTMLResponse)
async def passage() -> HTMLResponse:
    try:
        return HTMLResponse(open(os.path.join(_DIST, "passage.html"), encoding="utf-8").read())
    except OSError:
        return HTMLResponse("<h1>The Passage</h1><p>passage.html not found in dist/.</p>")
