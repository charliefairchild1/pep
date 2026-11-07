# Projects in this repo

Everything here runs from one FastAPI server (`uv run pep serve`), but the code
is grouped into one folder per project. Web routes live in
`src/pep/routes/<project>/` and are auto-discovered, so a new file with a
`router = APIRouter()` in any of these folders is picked up on its own.

| Project | What it is | Web routes | Engine code | Docs |
|---|---|---|---|---|
| **PEP core** | The engine: graph, spreading activation, residuals, state, haze. `/pep` home + mesh dashboard, chat/debug, OpenAI-compatible API | `routes/core/` | `core/`, `memory/`, `models/`, `policies/`, `schemas/`, `analysis/` | `docs/pep/` |
| **Lemma** | Daily-warmup grading app for math teachers (accounts, AI photo grading, Stripe billing, Canvas LMS). The live Render deploy | `routes/lemma/` | — (self-contained in routes) | `docs/lemma/` |
| **Vectora** | Data retrieval: Retrieval, Context, Watch, Graph | `routes/vectora/` | `vectora/` | — |
| **Lingora** | Language: Prompt, Translate, Voice, Learn | `routes/lingora/` | `lingora/` | — |
| **Atria** | Matching: Match, Date, Hire, Found, Therapy | `routes/atria/` | `atria/` | — |
| **Axona** | Cognition: Edge, BCI, Clinic, Learn, Wellness (+ Mind, Origin) | `routes/axona/` | `axona/` | — |
| **Strata** | Markets: Equities, Crypto, FX, Commodities, Predict, Bonds | `routes/strata/` | `strata/` | — |
| **PTO** | Theory surface behind PEP (`/pto`) | `routes/pto/` | — | `docs/pto/` |
| **Math playground** | The original math playground (`/math`) | `routes/math/` | — | — |
| **Demos** | Standalone HTML demos: `/encounter`, `/passage`, `/village`, `/robot` | `routes/demos/` | — | HTML in `dist/` |

All paths under `routes/` and the engine folders are relative to `src/pep/`.

**Not in this repo:** Koin (the manifesto) was moved out in commit `82e4f1e`
and lives in its own folder (`~/projects/koin/`). The Lingora, Atria and Strata
theory docs referenced in their pages live in `~/projects/<app>/docs/`.
