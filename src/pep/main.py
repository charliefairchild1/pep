"""FastAPI app for PEP. `uv run pep serve` boots this."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from pep import __version__
from pep.embed import Embedder
from pep.memory.store import MemoryStore
from pep.models.llm_client import get_llm_client
from pep.routes import chat, debug
from pep.routes.axona import router as axona_router
from pep.routes.axona_bridge import router as axona_bridge_router
from pep.routes.atria import router as atria_router
from pep.routes.atria_bridge import router as atria_bridge_router
from pep.routes.lingora import router as lingora_router
from pep.routes.lingora_bridge import router as lingora_bridge_router
from pep.routes.pep_home import router as pep_home_router
from pep.routes.strata import router as strata_router
from pep.routes.strata_bridge import router as strata_bridge_router
from pep.routes.vectora import router as vectora_router
from pep.routes.vectora_bridge import router as vectora_bridge_router
from pep.routes.math_playground import router as math_router
from pep.routes.openai_compat import router as openai_router
from pep.routes.ui import router as ui_router


def _resolve_db_path() -> str:
    custom = os.environ.get("PEP_DB_PATH")
    if custom:
        return custom
    return str(Path("data") / "pep.db")


@asynccontextmanager
async def lifespan(app: FastAPI):
    import threading
    app.state.store = MemoryStore(_resolve_db_path())
    app.state.embedder = Embedder()
    app.state.llm = get_llm_client()
    # Thread-safe stop flag for the dialogue runner. Only one dialogue runs
    # at a time, so a single Event is enough.
    app.state.dialogue_stop = threading.Event()
    yield
    app.state.store.close()


app = FastAPI(
    title="PEP — Predictive Encoding and Preparation",
    description=(
        "A predictive overlay that prepares an AI by activating likely-relevant "
        "memory, compressing the predictable, and highlighting useful novelty."
    ),
    version=__version__,
    lifespan=lifespan,
)

app.include_router(chat.router)
app.include_router(debug.router)
app.include_router(openai_router)
app.include_router(math_router)
app.include_router(axona_router)
app.include_router(axona_bridge_router)
app.include_router(lingora_router)
app.include_router(lingora_bridge_router)
app.include_router(atria_router)
app.include_router(atria_bridge_router)
app.include_router(pep_home_router)
app.include_router(strata_router)
app.include_router(strata_bridge_router)
app.include_router(vectora_router)
app.include_router(vectora_bridge_router)
app.include_router(ui_router)


@app.get("/")
async def root():
    return RedirectResponse(url="/ui")


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "llm": app.state.llm.name,
        "embeddings": "voyage" if app.state.embedder.using_real_embeddings else "pseudo",
    }
