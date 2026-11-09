# PEP Labs — PEP engine + the LAVAS suite

**PEP (Predictive Encoding and Preparation)** is a framework for weighted
graphs, spreading activation, residual scoring, state modulation and
opacity-based "haze" (forgetting as a feature). Every app in this repo is PEP
applied to one domain: language, matching, retrieval, cognition, markets, and
Lemma for math teachers.

Everything is served by one FastAPI server, and the code is organized **one
folder per project**, the same way in `src/pep/routes/`, `tests/` and `docs/`.

Live site: https://lemma-2b0h.onrender.com (the home page is the LAVAS suite;
Lemma is at `/lemma`)

## Projects

| Project | What it is | Pages | Code | Docs |
|---|---|---|---|---|
| **PEP core** | The engine: memory overlay, 7-module turn loop, benchmarks. Engine home, mesh dashboard, chat UI, OpenAI-compatible API | `/pep`, `/ui`, `/v1/chat/completions` | [`routes/core`](src/pep/routes/core) · [`core`](src/pep/core) [`memory`](src/pep/memory) [`models`](src/pep/models) [`policies`](src/pep/policies) [`schemas`](src/pep/schemas) [`analysis`](src/pep/analysis) | [`docs/pep`](docs/pep) |
| **Lemma** | Daily-warmup grading app for math teachers: accounts, AI photo grading, Stripe billing, Canvas LMS. The live product | `/lemma/teachers` | [`routes/lemma`](src/pep/routes/lemma) | [`docs/lemma`](docs/lemma) |
| **Vectora** | Data retrieval: Retrieval, Context, Watch, Graph | `/vectora` | [`routes/vectora`](src/pep/routes/vectora) · [`vectora`](src/pep/vectora) | — |
| **Lingora** | Language: Prompt, Translate, Voice, Learn | `/lingora` | [`routes/lingora`](src/pep/routes/lingora) · [`lingora`](src/pep/lingora) | — |
| **Atria** | Matching: Match, Date, Hire, Found, Therapy | `/atria` | [`routes/atria`](src/pep/routes/atria) · [`atria`](src/pep/atria) | — |
| **Axona** | Cognition: Edge, BCI, Clinic, Learn, Wellness (+ Mind, Origin) | `/axona` | [`routes/axona`](src/pep/routes/axona) · [`axona`](src/pep/axona) | — |
| **Strata** | Markets: Equities, Crypto, FX, Commodities, Predict, Bonds | `/strata` | [`routes/strata`](src/pep/routes/strata) · [`strata`](src/pep/strata) | — |
| **PTO** | The theory behind PEP | `/pto` | [`routes/pto`](src/pep/routes/pto) | [`docs/pto`](docs/pto) |
| **Math playground** | The original math playground | `/math` | [`routes/math`](src/pep/routes/math) | — |
| **Demos** | Standalone interactive pieces | `/encounter` `/passage` `/village` `/robot` | [`routes/demos`](src/pep/routes/demos) · HTML in [`dist`](dist) | — |

The five LAVAS apps (**L**ingora, **A**tria, **V**ectora, **A**xona,
**S**trata) talk to each other through event bridges (`*_bridge.py` in each
app's routes folder); the `/pep` mesh dashboard polls all of them.

## Run it

```sh
uv sync --extra dev
uv run pep serve            # http://127.0.0.1:8000
uv run pytest tests/        # 370+ tests
```

No API keys are needed: every engine has a local or heuristic fallback. The
PEP engine's own guide (Ollama setup, CLI, OpenAI-compatible endpoint,
troubleshooting) is in [`docs/pep/README.md`](docs/pep/README.md).

## Repo layout

```
src/pep/
├── routes/<project>/      # web pages + APIs, one folder per project (auto-discovered)
├── core/ memory/ models/ policies/ schemas/ analysis/   # PEP engine
├── vectora/ lingora/ atria/ axona/ strata/              # LAVAS app engines
├── main.py                # FastAPI app: finds every router under routes/
└── cli.py                 # `pep` command
tests/<project>/           # tests, grouped the same way (+ suite/ for cross-app)
docs/<project>/            # pep/, pto/, lemma/
benchmarks/                # PEP benchmark datasets
dist/                      # hand-authored HTML served by the demo pages
```

To add a page: drop a file with `router = APIRouter()` into the right
`src/pep/routes/<project>/` folder. `main.py` picks it up automatically.

## Deployment

The whole server deploys to Render on every push to `main`. See [`docs/lemma/DEPLOY.md`](docs/lemma/DEPLOY.md);
Stripe, AI grading and domain setup are in the same folder.

## Kept outside this repo

- **Koin** (the manifesto) was moved out in `82e4f1e` and lives in its own
  folder, `~/projects/koin/`.
- The full theory write-ups for Lingora, Atria and Strata that their pages cite
  live in `~/projects/<app>/docs/theory.md`.

---
PEP Labs LLC
