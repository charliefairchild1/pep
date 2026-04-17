# PEP — Predictive Encoding and Preparation

The core engine of the LAVAS suite. A mathematical and computational framework
for weighted graphs, spreading activation, residual scoring, state modulation,
and opacity-based haze (the forgetting/reuse primitive). Every LAVAS app is an
application of PEP to a specific domain.

## Five primitives
1. **Weighted graph** — nodes with feature vectors, edges weighted by typed
   compatibility. Everything reduces to this.
2. **Spreading activation** — the search primitive. Activation radiates from a
   seed through weighted edges with decay.
3. **Predictor + residual scorer** — a running forecast; the gap between
   forecast and reality is the only learning signal.
4. **State modulation** — slow-timescale parameters (mood, fatigue, context,
   arousal) that rescale edge weights at runtime.
5. **Opacity / haze** — every node has an encoding strength that decays over
   time. Nodes below the reuse threshold can be overwritten. Forgetting is the
   feature that makes capacity finite.

## Real engines shipped (Python packages inside PEP)
- **`pep.vectora`** — Retrieval (spreading activation), Context (session
  modulation), Watch (anomaly scoring), KG (typed edges), plus eval harness
  and dogfood layer powering all LAVAS siblings.
- **`pep.lingora.prompt`** — Structural prompt analysis: tokenizer, role
  segmentation, 10 antipattern checks, compression pipeline, per-provider cost
  forecasting.
- **`pep.lingora.translate`** — Four-layer sentence decomposition (denotation,
  pragmatic, register, cultural) with curated translation example bank.
- **`pep.lingora.voice`** — Eight-mechanism voice analysis (POV, register,
  irony, subtext, pacing, consistency, repetition, sound) with diagnostics.
- **`pep.lingora.learn`** — Constellation-based vocabulary with haze-primitive
  spaced repetition.
- **`pep.atria.match`** — Multi-objective matchmaking: 7-dimension scorer,
  rematch oracle, ObjectiveWeights presets, eval harness (AUC 0.977 vs Elo
  0.655).
- **`pep.atria.core`** — Generic multi-dimension matcher shared by Date, Hire,
  Found, Therapy.
- **`pep.atria.{date,hire,found,therapy}`** — Domain-specific compatibility
  engines.
- **`pep.axona.core`** — Cognitive state space (novelty/coherence/bandwidth/
  valence) with quadrant detection and alert generation.
- **`pep.axona.{bci,clinic,learn,wellness}`** — Domain-specific state-mapping
  engines.
- **`pep.strata.core`** — Universal unusual-score formula + classification.
- **`pep.strata.{equities,crypto,fx,commodities,predict,bonds}`** — Per-
  vertical asset seed data.

## Live surfaces (all served by one FastAPI server)
- **`/pep`** — the engine's teaching page + mesh dashboard
- **`/axona`** — ~60 canvases on cognition (plus Haze, Media & Brain,
  Motor Prediction Errors, Biological Substrate, Arousal & Clarity)
- **`/lingora`** — ~70 canvases on language
- **`/atria`** — ~20 canvases on matching
- **`/vectora`** — 10 canvases on data retrieval
- **`/strata`** — canvases on markets + 294-strategy library
- **`/math`** — the original math playground

## Products (19 total, each with engine + API + playground + product page)
**Vectora:** Retrieval, Context, Watch, Graph
**Lingora:** Prompt, Translate, Voice, Learn
**Atria:** Match, Date, Hire, Found, Therapy
**Axona:** Edge, BCI, Clinic, Learn, Wellness
**Strata:** Equities, Crypto, FX, Commodities, Predict, Bonds

## The mesh
All LAVAS apps communicate through event bridges. Each has a `*_bridge.py`
with POST/GET endpoints. The `/pep` mesh dashboard polls all five siblings.
Vectora Retrieval is dogfooded across all four sibling apps — they call the
real engine over HTTP for spreading-activation queries.

## Development
- Server: `cd ~/projects/pep && uv run pep serve --reload`
- Tests: `uv run pytest tests/` — 370+ tests
- No API keys needed — all engines use local/heuristic fallbacks
- Git: 47+ commits tracking the full build history

## Parent
PEP Labs LLC → LAVAS suite (Lingora, Atria, Vectora, Axona, Strata).
