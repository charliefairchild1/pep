"""HTTP endpoints that let sibling-app canvases call Vectora for retrieval.

The dogfood play: every LAVAS app's "spreading activation" canvas actually
calls Vectora instead of faking it in-browser. Proves that Vectora is the
retrieval layer the other siblings consume.

  GET /vectora/neighbors/{app}/{seed_id}?k=8&decay=0.35
  GET /vectora/seeds/{app}
  GET /vectora/dogfood/stats
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from pep.vectora import dogfood

router = APIRouter()


@router.get("/vectora/neighbors/{app}/{seed_id}")
async def neighbors(app: str, seed_id: str, k: int = 8, decay: float = 0.35):
    if app not in dogfood.APP_SEEDS:
        raise HTTPException(404, f"unknown app: {app}")
    try:
        hits = dogfood.neighbors(app, seed_id, k=k, decay=decay)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
    return {
        "app": app,
        "seed": seed_id,
        "hits": [
            {
                "id": h.id,
                "text": h.text,
                "score": h.score,
                "hop_distance": h.hop_distance,
                "metadata": h.metadata,
            }
            for h in hits
        ],
        "powered_by": "vectora",
    }


@router.get("/vectora/seeds/{app}")
async def seeds(app: str):
    if app not in dogfood.APP_SEEDS:
        raise HTTPException(404, f"unknown app: {app}")
    return {
        "app": app,
        "seeds": dogfood.seed_catalog(app),
        "stats": dogfood.stats(app),
    }


@router.get("/vectora/dogfood/stats")
async def all_stats():
    return {"apps": dogfood.all_stats()}
