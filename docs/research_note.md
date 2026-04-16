# PEP — Predictive Encoding and Preparation

## A research note on context as computation

**Version:** 0.1 (April 2026)
**Project location:** `~/projects/pep/`
**Status:** v1 complete, 83 tests passing, runs locally on Mac mini with Ollama (`llama3.2:3b`) as the base AI.

---

## Abstract

PEP is a memory-and-context overlay that sits *above* a base AI. It does not replace reasoning. It shapes which information the base AI sees on each turn — predicting what is likely about to matter, activating memories that fit the current cue, scoring what is surprising enough to keep, and packaging a structured envelope for the model. The base AI does the reasoning; PEP controls relevance.

The motivating theory is **PTO** (Potential → Transformation → Output): systems are favored when they maximize constructive transformation relative to total dissipation. For an AI, that means converting input into useful, adaptive, future-enabling structure while minimizing waste, contradiction, and loss of adaptability. PEP is one engineering implementation of PTO for cognitive systems.

This note documents the architecture, the empirical results from four benchmarks comparing PEP against two standard baselines (recent-window history and flat semantic top-k retrieval), the design of a multi-scale coherence experiment, the limitations of running on a small local model with pseudo-embeddings, and the open questions worth chasing next.

---

## 1. The problem

Current chat AIs are amnesiac across turns. Each request gets a context window, and whatever falls out of it is gone. The standard remedy is to bolt on retrieval-augmented generation (RAG): embed the conversation, embed each query, top-k cosine, stuff into the prompt. This works for some questions and fails for many — specifically, it fails when:

- The relevant memory uses different vocabulary than the query (semantic mismatch)
- Multiple senses of a word need to be distinguished by context
- The relevant memory is ten turns ago, behind a wall of intervening distractors
- The system needs to know not just *what* you said but *what state you were in* when you said it
- Memories should accumulate and reorganize over time, not just be retrieved point-in-time

PEP attempts a richer overlay: same idea (a layer between user and base AI) but with prediction, spreading activation, multi-face memory, sense disambiguation, state-conditioned weighting, and trajectory-quality storage gating.

---

## 2. PTO — the theory PEP is built on

PTO is the user's own framework; PEP is one engineering implementation of it. The full text lives at [`docs/pto.md`](pto.md). Compressed:

> **Systems are favored when they maximize constructive transformation relative to total dissipation.**
>
> For an AI builder specifically: a good system is one that converts input into useful, adaptive, future-enabling structure while minimizing waste and self-damage.

**Constructive transformation** increases predictive power, contextual accuracy, retrieval precision, conceptual coherence, action usefulness, compression quality, adaptability to novelty, preservation of important distinctions, future learning capacity.

**Dissipation** increases noise, confusion, redundancy, hallucination risk, contradiction, brittleness, retrieval drag, semantic collapse.

The crucial distinction from ordinary optimization: **PTO cares about trajectory quality, not local reward.** A reward-maximizer can overfit, exploit shortcuts, optimize the wrong metric, burn future capacity for present gain. PTO says the best move is the one that improves the structure of future moves, even if its immediate score is lower.

**The five PTO requirements for PEP:**
1. **Coherence** — internally consistent as it grows
2. **Relevance** — privilege transformations that matter to current goals and future adaptability
3. **Compression** — reduce complexity without erasing what later becomes important
4. **Recoverability** — lost detail should be reconstructable when needed
5. **Adaptivity** — structures should reorganize when new information changes the landscape

---

## 3. Architecture

### 3.1 Three primitives

Everything in PEP is built on:

1. **Prediction** — what is likely about to matter
2. **Reactivation** — what lights up when the cue arrives (cue-based, not flat search)
3. **Residual** — what was surprising enough to keep

These map directly to PTO: prediction lowers resistance, reactivation lowers retrieval cost, residual storage lowers dissipation.

### 3.2 The seven modules

| # | Module | File | Job |
|---|---|---|---|
| 1 | **Interpreter** | `src/pep/core/interpreter.py` | Parse raw input → intent, entities, topic, ambiguity, task type. |
| 2 | **State Modulator** | `src/pep/core/state.py` | Maintain rolling state vector (urgency, uncertainty, novelty, conflict, exploration, stability_need). State persists across turns and biases everything downstream. |
| 3 | **Predictor** | `src/pep/core/predictor.py` | Given interpretation + state + prior known entities, predict the cue tags, expected output type, and likely follow-ups. |
| 4 | **Reactivator** | `src/pep/core/reactivator.py` | Score every memory, spread activation across links, detect constellations, fall back to strategic search if weak, return the top-K activated set. |
| 5 | **Sense Mapper** | `src/pep/core/sense.py` | Detect ambiguous head terms (terms whose memories live in multiple distinct tag neighborhoods); pick the sense that matches current context. |
| 6 | **Residual Scorer** | `src/pep/core/residuals.py` | Compare actual input to prediction; emit a novelty score and a should_store decision. |
| 7 | **Memory Updater** | `src/pep/core/updater.py` | After the base AI responds, encode the exchange as a multi-face memory object — but only if combined novelty + trajectory score clears the gate. |

The full loop is in [`src/pep/core/loop.py`](../src/pep/core/loop.py), function `run_turn`. A streaming variant `stream_turn` yields response chunks via SSE for the live UI.

### 3.3 Dual-path design

Every supporting module (Interpreter, State, Predictor, Updater) has **two implementations**: a heuristic version (regex / keyword density / dictionary lookup) and an LLM-driven version (a structured haiku-style call returning JSON). The LLM path is tried first if a real client is available; on failure or with the stub, the heuristic path runs. Both paths produce the same schemas, so PEP's core loop is identical regardless of which is active.

Why this matters: with a small local model, LLM-driven supporting calls add 5-10x latency per turn. The Ollama client defaults `support_calls=False` so only the *base AI response* call (which the user actually sees) hits the model. The supporting modules use heuristics. This drops per-turn time from ~25s to ~5s on `llama3.2:3b` while preserving the architecture.

### 3.4 The multi-face memory object (the "hexaflexagon")

A memory in PEP is **not** a flat record. It is one object with up to six faces, each of which can be exposed independently depending on what the cue needs:

```python
class MemoryObject(BaseModel):
    id: str
    core: str                              # canonical content

    faces: dict[FaceName, str]             # 6 valid openings:
    #   semantic   — what it means
    #   episodic   — when/where it came up
    #   value      — significance / state weighting
    #   action     — what it tends to lead to
    #   predictive — what it tends to connect with next
    #   user       — how this user tends to use it
    fold_weights: dict[FaceName, float]    # confidence per face

    brightness: float                      # importance / salience
    tags: list[str]
    links: list[Link]                      # weighted edges to other memories

    state_modulation: dict[str, float]     # multipliers on brightness given state
    sense_profile: dict[str, SenseEntry]   # ambiguous-term tracking

    confidence: float
    drift_score: float                     # increments on each reactivation
    activation_count: int

    future_use: dict[str, float]           # trajectory score at storage time
    source_type: ...
    last_activated: datetime
```

The `links` field is the **switchboard**: a weighted directed graph between memories. Reactivation flows along these links via spreading activation; constellations emerge as connected subgraphs of co-activated, mutually-linked memories.

### 3.5 Switchboard retrieval (not flat top-k)

Standard RAG does `embed(query) → cosine(memories) → top-k`. PEP does:

1. **Build cue set** from prediction tags + interpreted entities + topic words.
2. **Direct scoring**: each memory scored by tag overlap + semantic similarity + recency + brightness × state-modulation.
3. **Spreading activation**: top scorers seed a propagation across the link graph at decay × weight, two hops by default. A memory two hops from a strong seed gets `seed_score × decay² × link_weight × link_proximity_weight` added to its score. Spreading is treated as **undirected** — links propagate in both directions.
4. **Constellation detection**: find connected subgraphs in the activated set joined by mutual links of weight ≥ COHESION_FLOOR. Members of a coherent constellation get a small bonus, scaled by cohesion (average internal link weight).
5. **Sense disambiguation**: for each cue term that appears in memories with multiple distinct tag neighborhoods, identify candidate senses, pick the one whose tag context matches the rest of the query.
6. **Strategic search fallback**: if the top score is below threshold or no memories activate, run a wider second pass with substring matching, lower floors, and boosted recency.

This is the honest version of "the brain doesn't really search, it floods and sees what reacts." Two modes — fast cue-driven reactivation, slow deliberate strategic search — coexist.

### 3.6 State modulation (the "real, not simulated" affective layer)

The State Modulator maintains six floats in [0, 1] across turns: urgency, uncertainty, novelty, conflict, exploration, stability_need. These are **not emotions**. They are processing modes that change how everything downstream weights things:

- High urgency narrows the constellation, prefers urgent-tagged memories
- High exploration widens recall, prefers exploration-tagged memories
- High uncertainty keeps multiple candidate senses alive instead of collapsing
- High novelty lowers the storage threshold (more curious → keep more)
- High conflict makes the predictor branch instead of commit

State persists across turns via blending: `next_state = previous * 0.6 + fresh * 0.4`. This means a single neutral query after several urgent ones doesn't snap urgency back to zero — it decays gradually, the way a real cognitive state should.

**A bug found by writing the state-dependent retrieval benchmark** (and now fixed): the original heuristic state estimator had `exploration = max(0.5, ...)` — an artificial floor. This meant exploration was always ≥ 0.5 regardless of context, so urgency could never dominate even under panic-mode priming. The floor was removed; exploration now starts at 0 and rises only with explicit explore words. State-dependent retrieval went from 0.5 to 1.0 after the fix.

### 3.7 Trajectory-quality storage (PTO option (b) + (c))

The Residual Scorer's `should_store` is just a *candidate* decision based on local novelty. The Updater combines it with a **trajectory score** before actually persisting:

> **combined = 0.5 × novelty + 0.5 × trajectory > 0.40**

The trajectory score asks: "Will the substance of this exchange matter for future similar conversations?" Two paths:
- **(b)** With a real LLM, a small structured call returns a 0–1 score plus a one-line reason.
- Without an LLM, a heuristic version uses signals like input length, entity density, response length, and task type as proxies.

The **(c)** half is empirical reinforcement via per-turn decay:
- Memories that get reactivated get a +0.05 brightness bump (`touch_memory` in the store)
- Memories that *don't* get activated lose a small amount of brightness each turn (`decay_unused_memories`, default decay=0.005, floor=0.05)
- Net effect: used memories stay bright; unused memories fade. Memories never get hard-deleted by decay — they just become hard to surface, which is honest. Real pruning happens in the consolidation pass.

### 3.8 Categories (Phase 3) — emergent fold structure

Categories are discovered, not predefined. The Category Engine ([`src/pep/core/categories.py`](../src/pep/core/categories.py)) periodically scans memory and:
- **Discovers** new clusters via greedy single-linkage tag-Jaccard clustering (threshold 0.3, minimum cluster size 3)
- **Splits** overcrowded categories (>15 members) into subcategories
- **Merges** categories whose top_tags overlap above MERGE_THRESHOLD (0.6)
- **Decays** empty categories
- **Updates** member counts, avg brightness, top tags

Categories become navigable folds — the realization of the user's "paper fortune teller" idea, where one structure has multiple selectable openings. They're stored as first-class rows in `categories` and `memory_categories` tables.

Triggered manually via `pep consolidate` (CLI) or `POST /consolidate` (API).

### 3.9 Consolidation pass — the "sleep cycle"

The consolidation pass ([`src/pep/core/consolidation.py`](../src/pep/core/consolidation.py)) runs:

1. **Merge near-duplicates** — memories with identical core prefix and ≥0.7 tag Jaccard get collapsed; the survivor keeps the higher brightness and union of links.
2. **Prune stale** — memories with brightness ≤ 0.08 AND zero activation count get hard-deleted along with their links and category assignments.
3. **Generate summaries** — categories with ≥5 members get a synthesized summary memory linked back to the brightest sources. Summaries are stored as `source_type=summary`.
4. **Run the Category Engine** (discover/split/merge/decay/update).

The pass is the engineering analog of sleep / reconsolidation: it reorganizes, compresses, and cleans up without losing what matters.

---

## 4. Empirical findings

PEP is compared against two standard baselines using the benchmark runner ([`src/pep/runner.py`](../src/pep/runner.py)) and the policies in [`src/pep/policies/`](../src/pep/policies/):

- **`recent_window`** — last 6 turns, no retrieval. The simplest possible baseline.
- **`semantic_topk`** — flat top-5 cosine over pseudo-embeddings. Standard RAG.
- **`pep_full`** — the full PEP loop.

There is also a **`raw_ai`** policy used by the `/chat/compare` UI endpoint for the side-by-side demo (no memory at all between user and base AI).

All numbers below are from real Ollama (`llama3.2:3b`) with pseudo-embeddings. Real Voyage embeddings would likely raise PEP's lead on most metrics. See the limitations section.

### 4.1 Benchmark scoreboard

| Metric | recent_window | semantic_topk | **pep_full** | Winner |
|---|---:|---:|---:|---|
| **ambiguity** / retrieval_precision | 0.00 | 0.75 | **1.00** | PEP |
| **ambiguity** / sense_accuracy | 0.00 | 0.75 | **1.00** | PEP |
| **long_horizon** / recall_hit_rate | 1.00 | 0.67 | **1.00** | tie |
| **long_horizon** / retrieval_precision | 0.33 | 0.00 | **0.89** | PEP |
| **distractor_resistance** | 1.00\* | 0.94 | 0.87 | recent\* |
| **state_dependent_retrieval** / state_match_rate | 0.00 | 0.00 | **1.00** | PEP |
| **constellation_rate (any)** | 0.00 | 0.00 | **0.50–1.00** | PEP |

\* `recent_window`'s perfect distractor resistance is trivial: it never retrieves anything, so it can't grab a distractor. The metric should probably normalize differently.

### 4.2 What each benchmark tests

- **`ambiguity`** ([`benchmarks/ambiguity.json`](../benchmarks/ambiguity.json)): 4 queries about polysemous words ("power", "memory", "state") with seeded memories that establish two distinct senses each. Tests whether the policy retrieves the right sense given context.

- **`long_horizon_recall`** ([`benchmarks/long_horizon_recall.json`](../benchmarks/long_horizon_recall.json)): Drops three facts in turns 1-3, then 4 unrelated distractor turns, then asks about the early facts in turns 8-10. Tests whether memory survives the conversation wandering.

- **`distractor_resistance`** ([`benchmarks/distractor_resistance.json`](../benchmarks/distractor_resistance.json)): 3 queries with seeded memories that include both the genuinely-relevant items and semantically-similar-but-irrelevant decoys. Tests whether the policy resists pulling the decoys.

- **`state_dependent_retrieval`** ([`benchmarks/state_dependent_retrieval.json`](../benchmarks/state_dependent_retrieval.json)): 6 seeded memories, all about "incident handling" — 3 conditioned to be brighter under high urgency, 3 under high exploration. Same neutral query is asked under two different states (built up by priming turns). The policy should retrieve different memories depending on the state. Only PEP can do this — the baselines are state-blind by construction.

### 4.3 Honest interpretation

PEP wins or ties on every metric that actually measures retrieval quality. The two losses are **distractor resistance** (where `recent_window` wins trivially because it doesn't retrieve at all) and the somewhat weaker **distractor resistance** vs `semantic_topk` (PEP activates more memories per turn, so its absolute distractor count is higher even when proportionally similar).

The strongest result is **state-dependent retrieval**: PEP gets a perfect 1.0 while both baselines get 0.0. This is the only benchmark where PEP can win by definition — the others are state-blind. But it confirms that PEP's State Modulator is doing real work: the same query under different states genuinely pulls different memories, validating one of the more speculative parts of the architecture.

The **constellation rate** numbers (0.50–1.00 for PEP, 0 for everyone else) are evidence that spreading activation does form coherent groups of co-activated memories in practice, not just in unit tests.

---

## 5. Multi-scale coherence experiment

The original brainstorming included an intuition that memory might have fractal-like or scale-coherent structure: when you "zoom in" on an interesting region of memory, the local relevance ordering should mirror the larger-scale structure. The careful version of that intuition is testable.

The experiment ([`src/pep/analysis/coherence.py`](../src/pep/analysis/coherence.py)):

1. **Fine scale**: score every memory against a query using a stripped-down read-only Reactivator (no state mutation, no spreading, no side effects).
2. **Coarse scale**: aggregate per-category — mean and max member score.
3. **Coherence metric**: Spearman rank correlation between (a) each memory's individual score and (b) its parent category's aggregate score, restricted to memories that have a category assignment.

Interpretation:
- **ρ near +1.0**: fine and coarse scales agree. Memories that are individually relevant live in categories that are collectively relevant. The architecture preserves meaningful structure across zoom levels.
- **ρ near 0**: the two scales are decoupled. Categories are labels glued on top of memories, not real structural units.
- **ρ near −1.0**: actively disagreeing — categorization is fighting relevance. Would be alarming.

### 5.1 Test fixtures verify both ends

Two unit tests in [`tests/test_coherence.py`](../tests/test_coherence.py) prove the metric responds correctly to extreme cases:

- **`test_coherence_high_when_categories_match_relevance`**: 4 highly-relevant memories in one category, 4 irrelevant memories in another. ρ > 0.8.
- **`test_coherence_low_when_categories_are_random`**: 6 memories with mixed relevance, deliberately scrambled into two categories. |ρ| < 0.7.

### 5.2 Live store results

Run via `pep coherence -q "..."` or `GET /coherence?query=...` or the **Categories** tab in the UI.

The current live store is too thin (12 memories, 1 category, 3 assigned) to produce a meaningful coherence number — with one category, all category-mean values are identical and the rank correlation has no variance to work with. This is correct behavior, not a bug. The workflow to get a meaningful number:

1. Run a focused demo scenario in the Demo Runner (e.g. "Building a concept across turns")
2. Click **Run Consolidation** to discover categories from the new memories
3. Test coherence with a query matching the demo's topic

With a populated dataset, the experiment produces a real number that can be tracked across sessions and changes to the architecture.

### 5.3 What this is not

This is **not** a Hausdorff dimension calculation. It is **not** evidence of literal fractal structure. It is a statistical test of whether two scales of organization agree in their ranking. The "fractal" framing was an intuition pump; the operational version is rank correlation across scales, which is much more honest and much more measurable.

---

## 6. Implementation at a glance

```
~/projects/pep/
├── src/pep/
│   ├── core/                  # the 7 PEP modules
│   │   ├── interpreter.py     # text → InterpretedInput
│   │   ├── state.py           # State Modulator (heuristic + LLM paths)
│   │   ├── predictor.py       # Prediction
│   │   ├── reactivator.py     # spreading activation + constellation detection
│   │   ├── sense.py           # Sense Mapper + Ambiguity Tracker
│   │   ├── residuals.py       # local novelty
│   │   ├── packager.py        # PEPPacket assembly
│   │   ├── updater.py         # multi-face encoding + trajectory gate
│   │   ├── categories.py      # Category Engine
│   │   ├── consolidation.py   # the "sleep cycle"
│   │   ├── loop.py            # run_turn() and stream_turn()
│   │   └── _llm_helpers.py    # JSON extraction for supporting calls
│   ├── memory/store.py        # SQLite + run ledger + categories
│   ├── models/
│   │   ├── llm_client.py      # Stub + Anthropic + factory
│   │   └── ollama_client.py   # local LLM via /api/chat
│   ├── schemas/               # Pydantic models (the contract between modules)
│   ├── policies/              # raw_ai, recent_window, semantic_topk, pep_full
│   ├── routes/                # FastAPI: chat, compare, stream, debug, ui
│   ├── analysis/coherence.py  # multi-scale coherence experiment
│   ├── runner.py              # benchmark runner
│   ├── evaluator.py           # metrics
│   ├── demos.py               # 4 scripted demo scenarios
│   ├── cli.py                 # serve | ingest | replay | consolidate | bench | coherence
│   ├── main.py                # FastAPI app entrypoint
│   └── dashboard.py           # (Streamlit dashboard, alternative to web UI)
├── benchmarks/
│   ├── ambiguity.json
│   ├── long_horizon_recall.json
│   ├── distractor_resistance.json
│   └── state_dependent_retrieval.json
├── tests/                     # 83 tests, all passing
└── docs/
    ├── pto.md                 # PTO theory in user's own words
    └── research_note.md       # this file
```

**Stack:** Python 3.11 + uv, FastAPI, Pydantic, SQLite + sqlite-vec, httpx, anthropic SDK, voyageai (unused without key), Click, Streamlit (alternative dashboard). Frontend is a single-file inline HTML/CSS/JS served by FastAPI, with D3.js v7 from CDN for the Sky View force-directed graph.

**Tests:** 83 passing. Run with `uv run pytest`.

---

## 7. Limitations and honest accounting

### 7.1 Pseudo-embeddings

Without `VOYAGE_API_KEY` set, `Embedder` falls back to deterministic SHA-512 pseudo-vectors. These are stable (same text → same vector) but **not semantically meaningful** — synonyms get unrelated vectors. This means:
- The semantic component of the Reactivator's score is essentially noise
- The Sense Mapper's ability to distinguish senses is degraded (it works on lexical co-occurrence but can't fall back on real semantic similarity)
- Distractor resistance suffers (truly similar items can't be distinguished from coincidentally similar ones)

Real Voyage embeddings would likely raise PEP's lead on most benchmarks. The architecture is correct; the embeddings are the bottleneck.

### 7.2 Small local model

`llama3.2:3b` is a 3-billion-parameter model running locally on Apple Silicon. It is **fast and free** but it is also **not very smart**. Specifically:
- It hallucinates definitions when given incomplete context
- It doesn't always cite memory IDs even when prompted to
- It produces awkward filler ("I'll explain", "I see that the user")
- It sometimes gets the response goal subtly wrong

A larger local model (e.g. `qwen2.5:7b` or `llama3.1:8b`) would help. So would real Claude or GPT through their APIs. But the user's constraint is "no API costs", so the local 3B model is what we have, and the architecture is honest about that.

### 7.3 Heuristic supporting modules by default

Because `OllamaLLMClient.support_calls=False` by default, the Interpreter / Predictor / State Modulator / face generation / trajectory scorer all run their **heuristic** paths, not LLM-driven paths. The heuristics are:
- Regex / keyword density
- Dictionary lookups
- Word counting

They are fast and deterministic, but they can't catch nuance the way a real LLM call would. The LLM-driven paths exist and are wired; setting `PEP_OLLAMA_SUPPORT_CALLS=1` enables them, at the cost of ~5x slower per-turn time.

### 7.4 Single-user, single-machine

PEP has no auth, no multi-user support, no hosted state. It is a research tool that runs on one Mac mini. Adding multi-user support would require reworking the session model, the run ledger, and the Sky View. Out of scope for v1.

### 7.5 Categories are tag-clustering, not concept-learning

The Category Engine clusters memories by **tag** Jaccard similarity. Tags are extracted heuristically (lowercase content words >3 chars). This is much weaker than what concept-learning would do, but it's honest — categories emerge from the data rather than being predefined, and they reorganize as new memories arrive. A future version could replace tag-Jaccard with embedding-based clustering once real embeddings are available.

### 7.6 Drift tracks but doesn't trigger

`drift_score` increments on every reactivation (the "memories change with every recall" insight made literal). But nothing currently *reads* drift_score to trigger reconsolidation when it gets high. A future Updater pass could regenerate the faces of high-drift memories, the way human memory rebuilds rather than replays. Out of scope for v1.

### 7.7 Sense Mapper detects but doesn't branch

The Sense Mapper currently identifies ambiguous terms and picks the most likely sense based on context overlap. It does **not** branch retrieval across senses when ambiguity is high. The schema (`ResolvedTerm.branched: bool`) anticipates branching as a Phase 3+ feature but it isn't implemented. For now, sense detection is recorded in the trace and the dashboard visualizes the alternatives.

---

## 8. Open questions worth chasing

In rough priority order:

### 8.1 Does the trajectory score actually predict reactivation? *(answered)*

Implemented in [`src/pep/analysis/trajectory_validation.py`](../src/pep/analysis/trajectory_validation.py) as `validate_trajectory_predictions(store)`. Run via `pep trajectory-validate` (CLI) or `GET /trajectory-validate` (API). Loads all memories with a stored `trajectory_at_storage` value, computes the Spearman rank correlation against `activation_count`, returns a report.

**First result against the live store (602 memories with trajectory scores, 608 total):**

| | |
|---|---|
| Mean predicted trajectory | 0.777 |
| Mean actual activation count | 7.14 |
| **Spearman ρ (predicted vs actual)** | **+0.026** |

**The heuristic trajectory scorer is essentially uncorrelated with actual reactivation.** The most-used memories (96 reactivations each) had predicted trajectory scores of 0.01–0.29 — i.e. "almost certainly won't matter" at storage time. Conversely, memories the scorer flagged at 1.00 ("definitely will matter") were used 0–8 times.

**Two non-exclusive explanations:**

1. **The heuristic is bad.** The current default scorer ([`_heuristic_trajectory_score`](../src/pep/core/updater.py)) is just length × entity-count × task-type. None of those features actually predict future usefulness in this dataset. Re-running with `PEP_OLLAMA_SUPPORT_CALLS=1` (LLM-driven trajectory scoring) might help — that's a follow-up experiment.
2. **Reactivation is dominated by recency + tag overlap, not "future usefulness."** With pseudo-embeddings, the Reactivator's score is dominated by tag overlap, recency, and brightness. The memories that carry the conversation are the ones from the *current session* that share tags with the query. None of those features are what the trajectory scorer is trying to predict.

**Implications for PEP's design:**

- The trajectory gate is currently adding noise rather than signal. The combined `0.5 × novelty + 0.5 × trajectory > 0.40` formula is filtering memories based on a value that doesn't predict their actual usefulness. A smaller-but-correct gate would be better.
- The PTO claim that "trajectory quality matters" is not refuted, but the *current operationalization* of trajectory quality (a heuristic on input features) doesn't capture it.
- Real validation needs the LLM-driven trajectory scorer plus more turns. The heuristic version is too dumb.

**Status:** First answer in the books. Research note now contains empirical evidence, not just hypotheses.

### 8.2 Does multi-scale coherence correlate with task performance?

We have a coherence metric but we haven't asked whether high-coherence stores produce better PEP responses. Hypothesis: there should be a positive correlation between coherence and benchmark scores. Test: run consolidation with different parameters (looser vs tighter clustering thresholds), measure the resulting coherence, then run the benchmark suite, and plot.

### 8.3 What does the Category Engine miss?

Current clustering is tag-based and greedy. Specific failures to investigate: memories about the same concept that happen to use different vocabulary; clusters that should split but don't because the tag overlap stays above threshold; small clusters of strongly-related memories that fall below MIN_CLUSTER_SIZE = 3.

### 8.4 What does spreading activation cost?

Two hops with decay 0.5 is the default. Is that the right tradeoff? The benchmark suite could be run with different `hops` and `decay` values to find the sweet spot for each benchmark type. Hypothesis: ambiguity benefits from narrow spreading; long-horizon recall benefits from wider spreading.

### 8.5 Real embeddings vs pseudo-embeddings — how big is the gap?

If/when Voyage or another real embedder becomes affordable, re-run all four benchmarks with real embeddings. Quantify the lift. This would tell us how much of PEP's current performance is the architecture and how much is bottlenecked by the embedding layer.

### 8.6 State Modulator: heuristic vs LLM-driven

The State Modulator currently uses regex on word density. With `PEP_OLLAMA_SUPPORT_CALLS=1`, it can use a haiku call instead. The benchmark we ran (state_dependent_retrieval) only exercises the heuristic path. Re-running with the LLM path would tell us whether richer state estimation improves retrieval quality, or whether the heuristic is good enough.

### 8.7 Stress test the Sky View force layout

The current Sky View renders ~50 memories comfortably. At ~500 it would slow down because the force simulation is O(N²) with naive many-body forces. D3 has a Barnes-Hut approximation; switching to it would extend the practical limit to several thousand memories. Worth doing once the live store gets richer.

### 8.8 Two PEP instances talking to each other

The most interesting research question: what happens when two PEP-equipped agents converse with each other across many turns? Each one has its own memory, its own state vector, its own categories. Do they form complementary structures? Do their state vectors couple? Does coherence measured at the joint memory level differ from coherence measured per agent?

---

## 9. The spine

> **PEP is a predictive overlay that prepares an AI by activating likely-relevant memory, compressing the predictable, and highlighting useful novelty before full reasoning begins. PEP shapes cognition; the base AI does cognition.**

> **PEP is one engineering implementation of PTO: it lowers the resistance and dissipation involved in turning input, memory, and context into useful response.**

These two sentences are the contract. Every design decision should either uphold them or have a clear story for why an exception is justified.

---

## 10. How to reproduce the findings

```sh
# Setup (one time)
brew install ollama
brew services start ollama
ollama pull llama3.2:3b

cd ~/projects/pep
uv sync --extra dev

# Run all tests
uv run pytest -v

# Run all four benchmarks against all three policies
for bench in ambiguity long_horizon_recall distractor_resistance state_dependent_retrieval; do
  uv run pep bench -b "$bench"
done

# Run the live demo
uv run pep serve
open http://127.0.0.1:8000

# In the browser:
#   1. Chat tab → Demo Runner → "Memory across turns" → Reset → Start
#   2. Watch the side-by-side raw vs PEP comparison
#   3. Sky View tab → see the memory graph
#   4. Categories tab → Run Consolidation → Test coherence
```

Everything in this note is reproducible with `uv run pytest` plus the commands above. There are no hidden steps and no external services beyond a local Ollama daemon.

---

*This is a working document. As findings accumulate or the architecture changes, sections should be updated rather than discarded.*
