"""Axona — The Mind.

A keyless, client-side AI you can actually talk to, built from PEP primitives:
weighted self-graph (Origin), spreading activation, a predictor + residual
scorer, inhibition gating, and a walled workspace whose contents the system
can report on but whose machinery it cannot see (the Seeming).

The self persists in localStorage. The AI's voice is synthesized from the
workspace, not from a language model — every line is traceable to which
self-nodes lit up, how surprised the predictor was, and what the inhibition
gate let through. Served standalone from dist/mind.html.
"""
import os

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()
_DIST = os.path.join(os.path.dirname(__file__), "..", "..", "..", "dist")


@router.get("/axona/mind", response_class=HTMLResponse)
async def axona_mind() -> HTMLResponse:
    try:
        return HTMLResponse(open(os.path.join(_DIST, "mind.html"), encoding="utf-8").read())
    except OSError:
        return HTMLResponse("<h1>The Mind</h1><p>mind.html not found in dist/.</p>")
