"""Axona — The Origin.

A keyless, client-side demo of the user's insight: the first introduction of
the self becomes the substrate every later experience attaches to and is
interpreted through. Pick one starting introduction to watch a self develop,
or two to compare — same experiences fed in, divergent selves come out
(the primacy effect / Asch / schema theory / the haze primitive in action).

Served standalone from dist/origin.html.
"""
import os

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()
_DIST = os.path.join(os.path.dirname(__file__), "..", "..", "..", "dist")


@router.get("/axona/origin", response_class=HTMLResponse)
async def axona_origin() -> HTMLResponse:
    try:
        return HTMLResponse(open(os.path.join(_DIST, "origin.html"), encoding="utf-8").read())
    except OSError:
        return HTMLResponse("<h1>The Origin</h1><p>origin.html not found in dist/.</p>")
