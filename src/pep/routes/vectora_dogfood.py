"""HTTP endpoints that let sibling-app canvases call Vectora for retrieval.

The dogfood play: every LAVAS app's "spreading activation" canvas actually
calls Vectora instead of faking it in-browser. Proves that Vectora is the
retrieval layer the other siblings consume.

  GET /vectora/neighbors/{app}/{seed_id}?k=8&decay=0.35
  GET /vectora/seeds/{app}
  GET /vectora/dogfood/stats
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from pep.vectora import dogfood

router = APIRouter()


# ═══ Per-app Context ════════════════════════════════════════════════════
class ContextRecordBody(BaseModel):
    session_id: str
    doc_id: str


class ContextQueryBody(BaseModel):
    session_id: str
    seed_id: str
    k: int = 6
    decay: float = 0.35


class ContextClearBody(BaseModel):
    session_id: str


@router.post("/vectora/context/{app}/record")
async def ctx_record(app: str, body: ContextRecordBody) -> dict[str, Any]:
    if app not in dogfood.APP_SEEDS:
        raise HTTPException(404, f"unknown app: {app}")
    try:
        size = dogfood.record_context_view(app, body.session_id, body.doc_id)
    except KeyError as exc:
        raise HTTPException(400, str(exc)) from exc
    return {"ok": True, "session_size": size}


@router.post("/vectora/context/{app}/compare")
async def ctx_compare(app: str, body: ContextQueryBody) -> dict[str, Any]:
    if app not in dogfood.APP_SEEDS:
        raise HTTPException(404, f"unknown app: {app}")
    try:
        r = dogfood.contextual_neighbors(
            app, body.session_id, body.seed_id, k=body.k, decay=body.decay,
        )
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
    return {
        "app": app,
        "seed_id": body.seed_id,
        "session": dogfood.context_session_info(app, body.session_id),
        "plain": [
            {"id": h.id, "text": h.text, "score": h.score, "hop_distance": h.hop_distance, "metadata": h.metadata}
            for h in r["plain"]
        ],
        "contextual": [
            {"id": h.id, "text": h.text, "score": h.score, "hop_distance": h.hop_distance, "metadata": h.metadata}
            for h in r["contextual"]
        ],
    }


@router.post("/vectora/context/{app}/clear")
async def ctx_clear(app: str, body: ContextClearBody) -> dict[str, Any]:
    if app not in dogfood.APP_SEEDS:
        raise HTTPException(404, f"unknown app: {app}")
    return {"cleared": dogfood.clear_context_session(app, body.session_id)}


# ═══ Per-app Watch ══════════════════════════════════════════════════════
class WatchBody(BaseModel):
    text: str
    item_id: str = "incoming"


@router.post("/vectora/watch/{app}/score")
async def watch_score(app: str, body: WatchBody) -> dict[str, Any]:
    if app not in dogfood.APP_SEEDS:
        raise HTTPException(404, f"unknown app: {app}")
    return dogfood.watch_score(app, body.text, item_id=body.item_id)


# ═══ Per-app KG ═════════════════════════════════════════════════════════
class KGTripleBody(BaseModel):
    source: str
    relation: str
    target: str
    weight: float = 1.0
    confidence: float = 1.0


class KGTraverseBody(BaseModel):
    start: str
    relations: list[str] | None = None
    max_hops: int = 2


@router.post("/vectora/kg/{app}/triple")
async def kg_triple(app: str, body: KGTripleBody) -> dict[str, Any]:
    if app not in dogfood.APP_SEEDS:
        raise HTTPException(404, f"unknown app: {app}")
    try:
        edge = dogfood.kg_add_triple(
            app, body.source, body.relation, body.target,
            weight=body.weight, confidence=body.confidence,
        )
    except KeyError as exc:
        raise HTTPException(400, str(exc)) from exc
    return {"ok": True, "edge": edge}


@router.post("/vectora/kg/{app}/traverse")
async def kg_traverse(app: str, body: KGTraverseBody) -> dict[str, Any]:
    if app not in dogfood.APP_SEEDS:
        raise HTTPException(404, f"unknown app: {app}")
    try:
        results = dogfood.kg_traverse(
            app, body.start, relations=body.relations, max_hops=body.max_hops,
        )
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
    return {"start": body.start, "results": results}


@router.get("/vectora/kg/{app}/viz")
async def kg_viz(app: str) -> dict[str, Any]:
    if app not in dogfood.APP_SEEDS:
        raise HTTPException(404, f"unknown app: {app}")
    return dogfood.kg_viz(app)


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
