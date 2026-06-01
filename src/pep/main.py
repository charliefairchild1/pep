"""FastAPI app for PEP. `uv run pep serve` boots this.

Works in two modes:
- Local dev: imports the heavy PEP-core infra (Embedder, MemoryStore, LLM
  client) and includes ALL route modules in pep.routes/
- Deploy: same code, but missing modules and missing infra are silently
  skipped. The Lemma app only needs lemma_backend + lemma_canvas +
  lemma_accounts; everything else is optional.

The route discovery happens via pkgutil.iter_modules(), so no master list
to maintain — drop a new file in pep/routes/ with `router = APIRouter()` and
it gets picked up automatically.
"""
from __future__ import annotations

import importlib
import os
import pkgutil
import threading
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from pep import __version__

# Heavy PEP-core dependencies — only used by /chat, /openai_compat, etc.
# Missing on the slim deploy is fine; Lemma + demo routes don't need them.
try:
    from pep.embed import Embedder
    from pep.memory.store import MemoryStore
    from pep.models.llm_client import get_llm_client
    _PEP_CORE_AVAILABLE = True
except Exception as _e:  # noqa: BLE001
    _PEP_CORE_AVAILABLE = False
    print(f"[main] PEP-core infra not available ({_e}); Lemma-only mode")


def _resolve_db_path() -> str:
    custom = os.environ.get("PEP_DB_PATH")
    if custom:
        return custom
    Path("data").mkdir(parents=True, exist_ok=True)
    return str(Path("data") / "pep.db")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if _PEP_CORE_AVAILABLE:
        try:
            app.state.store = MemoryStore(_resolve_db_path())
            app.state.embedder = Embedder()
            app.state.llm = get_llm_client()
            app.state.dialogue_stop = threading.Event()
        except Exception as e:  # noqa: BLE001
            print(f"[main] lifespan setup failed: {e}; continuing without it")
    yield
    if hasattr(app.state, "store"):
        try:
            app.state.store.close()
        except Exception:  # noqa: BLE001
            pass


app = FastAPI(
    title="Lemma + PEP",
    description=(
        "Lemma — daily warmup grading app for math teachers. Built on the PEP "
        "predictive memory-overlay architecture. Connects to Canvas LMS."
    ),
    version=__version__,
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Auto-discover and include every router in pep.routes/. Each module that
# exposes a top-level `router` gets wired up. Failures (missing imports,
# experimental files that don't compile, etc.) are logged and skipped.
# ---------------------------------------------------------------------------

def _include_all_routers(app: FastAPI) -> None:
    from pep import routes as routes_pkg
    included: list[str] = []
    skipped: list[tuple[str, str]] = []
    for _finder, name, _ispkg in pkgutil.iter_modules(routes_pkg.__path__):
        try:
            mod = importlib.import_module(f"pep.routes.{name}")
        except Exception as e:  # noqa: BLE001
            skipped.append((name, type(e).__name__ + ": " + str(e)[:80]))
            continue
        router = getattr(mod, "router", None)
        if router is None:
            continue
        try:
            app.include_router(router)
            included.append(name)
        except Exception as e:  # noqa: BLE001
            skipped.append((name, "include_router: " + str(e)[:80]))
    print(f"[main] auto-discovered routes: included {len(included)}, skipped {len(skipped)}")
    if skipped:
        for n, reason in skipped[:10]:
            print(f"  skip  {n}: {reason}")
        if len(skipped) > 10:
            print(f"  ... and {len(skipped) - 10} more")


def _include_chat_and_debug(app: FastAPI) -> None:
    """chat + debug live in pep.routes/ as full modules — they have hard deps
    on the lifespan-installed Embedder/MemoryStore/LLM. Only wire them up if
    PEP-core is available."""
    if not _PEP_CORE_AVAILABLE:
        return
    try:
        from pep.routes import chat as _chat, debug as _debug
        app.include_router(_chat.router)
        app.include_router(_debug.router)
    except Exception as e:  # noqa: BLE001
        print(f"[main] chat/debug not loaded: {e}")


# ---------------------------------------------------------------------------
# Root + health — registered FIRST so they win over any landing route in
# pep.routes/ that also claims "/"
# ---------------------------------------------------------------------------

@app.get("/")
async def root() -> RedirectResponse:
    """Land on Lemma marketing; teachers + students enter here."""
    return RedirectResponse("/lemma/teachers", status_code=302)


@app.get("/lemma")
async def lemma_root() -> RedirectResponse:
    return RedirectResponse("/lemma/teachers", status_code=302)


@app.get("/healthz")
async def health() -> dict:
    return {"ok": True, "version": __version__, "pep_core": _PEP_CORE_AVAILABLE}


_include_all_routers(app)
_include_chat_and_debug(app)
