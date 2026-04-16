# PEP — Predictive Encoding and Preparation

**A memory and context overlay that sits on top of a base AI.** PEP doesn't reason — it makes sure the AI underneath has the right information to reason with. As you talk to it, PEP remembers what you've said, links related ideas, scores what's worth keeping, and feeds the most relevant context back into the model on every turn.

> PEP shapes cognition; the base AI does cognition. PEP controls relevance, not thought.

## What's actually in here

| | |
|---|---|
| **Tests** | 134 passing |
| **Base AI** | Local Ollama (`llama3.2:3b` default; `qwen2.5:7b` available with `PEP_OLLAMA_STRONG_MODEL=qwen2.5:7b`) |
| **Costs** | Zero — everything runs locally |
| **Web UI** | 8 tabs at `http://127.0.0.1:8000` |
| **CLI commands** | `serve`, `ask`, `ingest`, `replay`, `consolidate`, `bench`, `coherence`, `dialogue`, `trajectory-validate` |
| **HTTP** | Native PEP endpoints + **OpenAI-compatible `/v1/chat/completions`** |
| **Backbone document** | `docs/research_note.md` (459 lines) |
| **Theory document** | `docs/pto.md` |

## The three primitives PEP is built on

1. **Prediction** — what is likely about to matter
2. **Reactivation** — what lights up when the cue arrives (cue-based, not flat top-k search)
3. **Residual** — what was surprising enough to keep

These map directly to the **PTO** principle: maximize constructive transformation relative to total dissipation. PEP is one engineering implementation of that idea for AI overlays.

---

## 1-minute quickstart

If you've never run PEP before:

```sh
# 1. Install Ollama (one time)
brew install ollama
brew services start ollama
ollama pull llama3.2:3b   # ~2GB

# 2. Set up PEP
cd ~/projects/pep
uv sync --extra dev
uv run pytest             # should be 134 passing

# 3. Start the server
uv run pep serve

# 4. Open the browser
open http://127.0.0.1:8000
```

That's it. Click around the tabs. The Chat tab has a Demo Runner with scripted scenarios that explain themselves.

---

## Three ways to use PEP

### A. Web UI (the easiest)

`uv run pep serve` then open `http://127.0.0.1:8000`. Eight tabs:

| Tab | What it does |
|---|---|
| **Chat** | Talk to PEP directly. Streaming responses. Demo Runner has 4 scripted scenarios. Compare-with-raw-AI toggle shows side-by-side. |
| **Sky View** | Force-directed memory graph. Stars sized by brightness, linked memories pull together. Hover for content, click for full memory details. |
| **Dialogue** | 2-5 PEP-equipped agents talking to each other. Round-robin turns, each agent has its own memory. Auto-continue, save-transcript, per-agent coherence comparison. |
| **Categories** | Categories discovered from the link graph. Run consolidation, test multi-scale coherence with a query. |
| **Analysis** | Research findings against the live store. §8.1 trajectory validation with scatter plot, LLM-vs-heuristic comparison. |
| **Runs** | Drill into any past PEP run's full packet JSON. |
| **Ingest** | Paste text to load it as memories (splits by blank lines). |
| **Benchmarks** | Run comparison benchmarks (ambiguity, long-horizon recall, distractor resistance, state-dependent retrieval) across all 3 policies (recent_window, semantic_topk, pep_full). |

**Keyboard shortcuts:** `1`–`8` switch tabs, `⌘+↵` send/start (context-aware), `Esc` stops running things, `?` shows help.

### B. CLI (`pep ask`)

For one-shot questions from any terminal:

```sh
uv run pep ask "What is PEP?"
uv run pep ask "Tell me more about that" --trace
uv run pep ask "Explain it in plain terms" --session-id research
```

Memory persists across calls per session-id. Different `--session-id` values give independent memory streams.

Also:

```sh
uv run pep ingest path/to/notes.md          # bulk-load text as memories
uv run pep consolidate                      # dedup, summarize, redistill, discover categories
uv run pep dialogue --turns 12              # two PEP agents talk to each other
uv run pep coherence -q "memory"            # multi-scale coherence experiment
uv run pep trajectory-validate              # §8.1 research finding
uv run pep bench -b ambiguity               # benchmark vs baselines
```

### C. OpenAI-compatible HTTP endpoint (the real overlay)

PEP exposes `/v1/chat/completions` matching the OpenAI spec, so any tool that speaks OpenAI can use PEP transparently:

```sh
curl -X POST http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "pep",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

Streaming works the same way (OpenAI-format SSE chunks):

```sh
curl -N -X POST http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "pep",
    "messages": [{"role": "user", "content": "Hello"}],
    "stream": true
  }'
```

You can plug PEP into:
- **Open WebUI** — point it at `http://127.0.0.1:8000/v1` as the OpenAI base URL, model `pep`
- **Cursor / Continue / any IDE chat plugin** — same trick
- **Custom scripts** — works with the standard `openai` Python package by setting `base_url="http://127.0.0.1:8000/v1"`
- **Any tool that already supports OpenAI** — usually no code changes needed

PEP-specific extension: pass `pep_session: "<name>"` in the request body to route different clients to different memory streams.

---

## Architecture in one paragraph

Every turn flows through 7 modules: **Interpreter** parses the input, **State Modulator** updates a 6-variable state vector (urgency, uncertainty, novelty, conflict, exploration, stability_need), **Predictor** guesses what context will matter, **Reactivator** runs spreading activation across the memory graph and detects coherent constellations of co-activated memories, **Residual Scorer** decides what's surprising enough to store, **Packager** assembles the structured envelope, base AI generates the response, **Memory Updater** distills the exchange into a compressed memory with multi-face encoding (semantic / episodic / value / action / predictive / user), and the per-turn decay cycle reinforces what was used and fades what wasn't. See `docs/research_note.md` §3 for the full story.

---

## Recovery / troubleshooting

### Server not responding

```sh
# Find and kill any running pep server
lsof -i :8000 -t | xargs -r kill -9
# Restart it
cd ~/projects/pep && uv run pep serve
```

### Tabs not loading in the browser

Hard-refresh: **Cmd+Shift+R** on Mac. There's a JS validation guardrail in the test suite (`tests/test_ui_js.py`) so this should never ship broken — but a stale browser cache can still cause it.

### Ollama not responding

```sh
brew services restart ollama
# verify
curl http://localhost:11434/api/tags
# should return JSON listing your installed models
```

### Reset everything (nuclear option)

```sh
# Wipe the live PEP database
rm ~/projects/pep/data/pep.db
# Restart the server — fresh empty store
uv run pep serve
```

### Reset just one session (or just the dialogue agents)

```sh
# Via the API
curl -X POST http://127.0.0.1:8000/sessions/dialogue:Alice/clear
curl -X POST http://127.0.0.1:8000/sessions/dialogue:Bob/clear
# Or via the UI: Categories tab → Reset, or Dialogue tab → Reset agents
```

### Switch to the bigger model

```sh
# kill the existing server
lsof -i :8000 -t | xargs kill -9
# restart with qwen2.5:7b (4.7GB, smarter, slower)
cd ~/projects/pep
PEP_OLLAMA_STRONG_MODEL=qwen2.5:7b uv run pep serve
```

### Enable LLM-driven supporting calls (slower, smarter)

By default Ollama's `support()` is disabled because each support call adds ~5s of latency on `llama3.2:3b`. To enable LLM-driven Interpreter / State Modulator / Predictor / Updater face generation / trajectory scoring:

```sh
PEP_OLLAMA_SUPPORT_CALLS=1 uv run pep serve
```

With this on, every PEP turn does ~6 LLM calls (~30s/turn on llama3.2:3b). Use only when you specifically want LLM-driven supporting modules — e.g. for the §8.1 trajectory validation experiment.

---

## Documentation

- **`docs/research_note.md`** — the backbone document. PTO theory, PEP architecture, all 4 benchmarks with real numbers, the §8.1 trajectory finding, multi-scale coherence experiment, limitations, open questions. Read this first if you're returning to the project after a break.
- **`docs/pto.md`** — the user's PTO theory in their own words. The "why" behind every design decision in PEP.
- **The plan file** at `~/.claude/plans/lovely-hatching-stream.md` — historical roadmap

## Project layout

```
src/pep/
├── core/                  # the 7 PEP modules
│   ├── interpreter.py     # text → InterpretedInput
│   ├── state.py           # State Modulator
│   ├── predictor.py       # Prediction
│   ├── reactivator.py     # spreading activation + constellation detection + category descent
│   ├── sense.py           # Sense Mapper
│   ├── residuals.py       # local novelty
│   ├── updater.py         # multi-face memory + distillation + trajectory gating
│   ├── packager.py        # PEPPacket assembly
│   ├── categories.py      # Category Engine
│   ├── consolidation.py   # the "sleep cycle" (dedup, summarize, reconsolidate, redistill)
│   └── loop.py            # run_turn() and stream_turn()
├── memory/store.py        # SQLite + run ledger
├── models/                # LLM client adapters (Stub, Anthropic, Ollama)
├── schemas/               # Pydantic models
├── policies/              # raw_ai, recent_window, semantic_topk, pep_full
├── routes/                # FastAPI: chat, debug, openai_compat, ui
├── analysis/              # multi-scale coherence + trajectory validation experiments
├── dialogue.py            # multi-agent dialogue (2-5 PEP-equipped agents)
├── runner.py              # benchmark runner
├── evaluator.py           # benchmark metrics
├── demos.py               # 4 scripted demo scenarios
├── cli.py                 # all CLI commands
└── main.py                # FastAPI app entrypoint

benchmarks/                # 4 benchmark JSON files
docs/                      # research_note.md, pto.md
tests/                     # 134 tests
```

## Status

**v1 done.** All Phase 1, 2, and 3 features shipped. PEP is now a real, usable overlay — not just a demo. Open questions and next experiments are documented in `docs/research_note.md` §8.

**Last verified:** 134 tests passing, real Ollama under the hood, OpenAI-compatible endpoint live.
