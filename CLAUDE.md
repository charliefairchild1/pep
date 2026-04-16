# PEP — Predictive Encoding and Preparation

The core engine of the LAVAS suite. A mathematical and computational framework
for weighted graphs, spreading activation, residual scoring, and state
modulation. Every LAVAS app (Axona, Lingora, Atria, Vectora, Strata) is an
application of PEP to a specific domain.

## What this is
PEP is not a single algorithm; it is a small vocabulary of primitives that
compose. The four canonical primitives are:
- **Weighted graph** — nodes with multi-dimensional feature vectors, edges
  weighted by typed compatibility measures.
- **Spreading activation** — the native search primitive. Activation radiates
  from a seed through weighted edges with decay, producing a neighborhood-
  shaped region rather than a sorted window.
- **Predictor + residual scorer** — a running forecast of the next input,
  and a scorer for the gap between forecast and reality. The residual is
  the learning signal.
- **State modulation** — slow-timescale state (mood, behavior, context) that
  shifts the weights and gains used by the other primitives on the fly.

Everything in Axona (cognition), Lingora (language), Atria (matching), and
the unbuilt LAVAS projects reduces to some configuration of these four
primitives.

## Live surfaces
- **`/pep`** — PEP's own teaching page. Hero, four primitive demos, live mesh
  dashboard, theory, and cross-links to the LAVAS siblings. Route at
  `pep/src/pep/routes/pep_home.py`.
- **`/math`** — the math playground. Legacy; some early demos.
- **`/axona`** — Axona's ~60 canvases applying PEP to cognition.
- **`/lingora`** — Lingora's ~70 canvases applying PEP to language.
- **`/atria`** — Atria's ~20 canvases applying PEP to matching.
- **`/chat`**, **`/ui`**, **`/openai/*`** — the conversational and API surfaces.

## The mesh
PEP, Axona, Lingora, and Atria talk to each other through a shared event bus.
Each LAVAS app has a bridge file (`{app}_bridge.py`) exposing
`POST /{app}/event`, `GET /{app}/events`, and `GET /{app}/pep-state`. Each
bridge cross-reads the other buffers so any surface can display recent events
from the others. The `/pep` home page shows the full mesh in one dashboard.

## Package structure
- `src/pep/core/` — core algorithms (graph, activation, residuals).
- `src/pep/memory/` — the MemoryStore (runs, sessions, brightness tracking).
- `src/pep/models/` — LLM client wrapper, embedder wrapper.
- `src/pep/policies/` — policy modules used by the chat runner.
- `src/pep/routes/` — FastAPI routes, including the LAVAS app pages and
  their bridges.
- `src/pep/analysis/` — offline analysis tools.
- `src/pep/schemas/` — Pydantic schemas for PEPPackets, runs, events.

## The LAVAS siblings
All five LAVAS sibling projects live as directories under `~/projects/`:
- `axona/` — brain and cognition. Already built: full interactive app.
- `lingora/` — language as a cognitive technology. Already built.
- `atria/` — matching, compatibility, relational alignment. Already built.
- `vectora/` — data organization, pattern analysis. Not yet scaffolded.
- `strata/` — markets, trading, financial decision-making. Not yet scaffolded.

Each sibling's live UI is served by PEP's FastAPI server at its route
(`/axona`, `/lingora`, `/atria`). The package at `~/projects/<name>/` holds
the theory doc, CLAUDE.md, and scaffold. The real code lives in PEP's routes.

## Development notes
- Server run: `cd ~/projects/pep && uv run pep serve --reload`
- Auto-reload is on — edits to the route files trigger a FastAPI restart.
- No API keys are configured (`ANTHROPIC_API_KEY` and `VOYAGE_API_KEY`
  unset) — the LLM client falls back to an Ollama stub; the embedder uses
  pseudo-embeddings. All canvases are built to work without real API
  responses.
- The session-length strategy is: rely on CLAUDE.md files and the memory
  system at `~/.claude/projects/-Users-adamsmith/memory/` for cross-session
  continuity; never assume session-internal context persists.

## Parent project
PEP Labs LLC — the umbrella company. PEP is the engine; LAVAS is the applied
suite; PEP Labs is the legal wrapper. Current pursuit order (from memory):
PEP core → Vectora internally → Atria as first market-facing product →
Strata as research sandbox → Lingora and Axona later. Axona and Lingora are
ahead of that schedule because they are teaching surfaces rather than
products; they got built first for demonstration value.
