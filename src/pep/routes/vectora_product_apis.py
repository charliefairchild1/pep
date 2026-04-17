"""Live API + playground routes for Vectora Context, Watch, and KG.

All three share the curated demo corpus from dogfood.SAMPLE_CORPUS for
their demos. Each has an API set (for programmatic use) and a playground
UI (for developer exploration).

Routes:
  # Context
  GET  /vectora/context-playground
  POST /vectora/context-playground/record
  POST /vectora/context-playground/retrieve
  POST /vectora/context-playground/clear

  # Watch
  GET  /vectora/watch-playground
  POST /vectora/watch-playground/score

  # KG
  GET  /vectora/graph-playground
  POST /vectora/graph-playground/triple
  POST /vectora/graph-playground/traverse
  GET  /vectora/graph-playground/viz
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from pep.vectora import (
    ContextConfig,
    ContextTracker,
    Document,
    EdgeProvenance,
    VectoraKG,
    VectoraRetriever,
    VectoraWatch,
    WatchConfig,
)
from pep.vectora.demo import SAMPLE_CORPUS

router = APIRouter()


# ═══════════════════════════════════════════════════════════════════════
# Shared corpus (one retriever for all three playgrounds — built lazily)
# ═══════════════════════════════════════════════════════════════════════
_retriever: VectoraRetriever | None = None
_context: ContextTracker | None = None
_watch: VectoraWatch | None = None
_kg: VectoraKG | None = None


def _get_retriever() -> VectoraRetriever:
    global _retriever
    if _retriever is None:
        r = VectoraRetriever()
        r.add_documents(SAMPLE_CORPUS)
        r.build_graph()
        _retriever = r
    return _retriever


def _get_context() -> ContextTracker:
    global _context
    if _context is None:
        _context = ContextTracker(_get_retriever(), ContextConfig(context_weight=0.45))
    return _context


def _get_watch() -> VectoraWatch:
    global _watch
    if _watch is None:
        _watch = VectoraWatch(_get_retriever())
    return _watch


def _get_kg() -> VectoraKG:
    global _kg
    if _kg is None:
        _kg = VectoraKG(_get_retriever())
        # Seed some typed edges so the demo has structure from the start
        _kg.add_triples([
            ("cache-1", "depends_on", "memory-1"),
            ("cache-1", "alternative_to", "db-1"),
            ("cache-2", "refines", "cache-1"),
            ("rag-1", "uses", "embed-5"),
            ("rag-2", "refines", "rag-1"),
            ("rag-3", "component_of", "rag-1"),
            ("rate-1", "related_to", "backpres-3"),
            ("rate-2", "implements", "rate-1"),
            ("backpres-1", "mitigates", "rate-3"),
        ])
    return _kg


# ═══════════════════════════════════════════════════════════════════════
# Context — Pydantic models
# ═══════════════════════════════════════════════════════════════════════
class RecordViewRequest(BaseModel):
    session_id: str
    doc_id: str


class ContextRetrieveRequest(BaseModel):
    session_id: str
    query: str
    k: int = 8


class ClearSessionRequest(BaseModel):
    session_id: str


# ── Context API ─────────────────────────────────────────────────────────
@router.post("/vectora/context-playground/record")
async def ctx_record(req: RecordViewRequest) -> dict[str, Any]:
    try:
        _get_context().record_view(req.session_id, req.doc_id)
    except KeyError as exc:
        raise HTTPException(400, str(exc)) from exc
    return {
        "ok": True,
        "session_size": _get_context().session_size(req.session_id),
    }


@router.post("/vectora/context-playground/retrieve")
async def ctx_retrieve(req: ContextRetrieveRequest) -> dict[str, Any]:
    ct = _get_context()
    cmp = ct.compare(req.session_id, req.query, k=req.k)
    recent = ct.recent_views(req.session_id, limit=10)
    return {
        "query": req.query,
        "session_id": req.session_id,
        "recent_views": [{"doc_id": e.doc_id, "weight": e.weight} for e in recent],
        "session_size": ct.session_size(req.session_id),
        "plain": [_serialize_result(r) for r in cmp["plain"]],
        "contextual": [_serialize_result(r) for r in cmp["contextual"]],
    }


@router.post("/vectora/context-playground/clear")
async def ctx_clear(req: ClearSessionRequest) -> dict[str, Any]:
    ok = _get_context().clear_session(req.session_id)
    return {"cleared": ok}


def _serialize_result(r) -> dict[str, Any]:
    return {
        "id": r.doc.id,
        "text": r.doc.text,
        "score": round(r.score, 4),
        "hop_distance": r.hop_distance,
        "breakdown": {k: round(v, 4) for k, v in r.score_breakdown.items()},
    }


# ═══════════════════════════════════════════════════════════════════════
# Watch — Pydantic models
# ═══════════════════════════════════════════════════════════════════════
class WatchScoreRequest(BaseModel):
    text: str
    item_id: str = "incoming"


@router.post("/vectora/watch-playground/score")
async def watch_score(req: WatchScoreRequest) -> dict[str, Any]:
    w = _get_watch()
    r = w.score_item(req.text, item_id=req.item_id)
    return {
        "id": r.doc_id,
        "text": r.text,
        "residual": r.residual,
        "label": r.label,
        "components": {
            "distance": r.distance_component,
            "neighbor": r.neighbor_component,
            "novelty": r.novelty_component,
        },
        "stats": w.stats(),
    }


# ═══════════════════════════════════════════════════════════════════════
# KG — Pydantic models
# ═══════════════════════════════════════════════════════════════════════
class AddTripleRequest(BaseModel):
    source: str
    relation: str
    target: str
    weight: float = 1.0
    confidence: float = 1.0


class TraverseRequest(BaseModel):
    start: str
    relations: list[str] | None = None
    max_hops: int = 2


@router.post("/vectora/graph-playground/triple")
async def kg_add_triple(req: AddTripleRequest) -> dict[str, Any]:
    try:
        edge = _get_kg().add_triple(
            req.source, req.relation, req.target,
            weight=req.weight, confidence=req.confidence,
        )
    except KeyError as exc:
        raise HTTPException(400, str(exc)) from exc
    return {
        "ok": True,
        "edge": {
            "source": edge.source, "target": edge.target, "relation": edge.relation,
            "weight": edge.weight, "confidence": edge.confidence,
            "provenance": edge.provenance.value,
        },
        "stats": _get_kg().stats(),
    }


@router.post("/vectora/graph-playground/traverse")
async def kg_traverse(req: TraverseRequest) -> dict[str, Any]:
    kg = _get_kg()
    try:
        results = kg.traverse(req.start, relations=req.relations, max_hops=req.max_hops)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
    return {
        "start": req.start,
        "results": [
            {
                "doc_id": r.doc_id,
                "text": r.text,
                "hop_distance": r.hop_distance,
                "total_weight": round(r.total_weight, 4),
                "relations_to_seed": r.relations_to_seed,
            }
            for r in results
        ],
    }


@router.get("/vectora/graph-playground/viz")
async def kg_viz() -> dict[str, Any]:
    kg = _get_kg()
    return {**kg.to_viz_data(), "stats": kg.stats()}


@router.get("/vectora/graph-playground/sample")
async def kg_sample() -> dict[str, Any]:
    """List of documents (node IDs) available for typed-edge construction."""
    return {
        "nodes": [{"id": d.id, "text": d.text} for d in _get_retriever().graph.documents()],
        "relations": [
            "depends_on", "refines", "alternative_to", "uses",
            "component_of", "related_to", "implements", "mitigates",
            "part_of", "cites", "contradicts",
        ],
    }


# ═══════════════════════════════════════════════════════════════════════
# Playground HTML pages
# ═══════════════════════════════════════════════════════════════════════
_CTX_HTML = """\
<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Vectora Context Playground</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg: #0c120a; --surface: #18201a; --surface2: #141a13;
    --text: #dcedd4; --dim: #7a8a6a; --accent: #a3e635; --border: #24301f;
  }
  body { font-family: 'SF Mono', monospace; background: var(--bg); color: var(--text); line-height: 1.6; }
  nav { position: sticky; top: 0; background: var(--bg); padding: 10px 20px;
        border-bottom: 1px solid var(--border); display: flex; gap: 14px; align-items: center; flex-wrap: wrap; }
  .brand { font-size: 18px; font-weight: bold; color: var(--accent); }
  .badge { font-size: 9px; color: var(--accent); background: rgba(163,230,53,0.15);
           padding: 2px 8px; border-radius: 10px; letter-spacing: 0.05em; }
  .links { margin-left: auto; display: flex; gap: 14px; font-size: 11px; }
  .links a { color: var(--dim); text-decoration: none; }
  .links a:hover { color: var(--accent); }
  .layout { display: grid; grid-template-columns: 360px 1fr; min-height: calc(100vh - 50px); }
  .sidebar { background: var(--surface); border-right: 1px solid var(--border); padding: 18px; overflow-y: auto; }
  .main { padding: 18px 24px; overflow-y: auto; }
  .label { font-size: 10px; color: var(--dim); letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 8px; }
  select, input, button { font-family: inherit; font-size: 11px; }
  input[type=text] { width: 100%; background: var(--surface2); color: var(--text);
                     border: 1px solid var(--border); border-radius: 4px; padding: 8px 10px; }
  button.btn { padding: 6px 14px; border-radius: 4px; border: 1px solid var(--accent);
               background: var(--accent); color: var(--bg); cursor: pointer; font-weight: bold; }
  button.btn-alt { padding: 6px 14px; border-radius: 4px; border: 1px solid var(--border);
                   background: transparent; color: var(--dim); cursor: pointer; }
  .doc-btn { text-align: left; background: var(--surface2); color: var(--text);
             border: 1px solid var(--border); border-left: 3px solid var(--border);
             border-radius: 4px; padding: 8px 10px; margin-bottom: 4px; cursor: pointer;
             width: 100%; transition: border-color 0.15s; font-size: 10px; }
  .doc-btn:hover { border-color: var(--accent); }
  .doc-btn.viewed { border-left-color: var(--accent); background: rgba(163,230,53,0.05); }
  .recent-list { background: var(--surface2); border: 1px solid var(--border); border-radius: 4px;
                 padding: 10px; font-size: 10px; margin-top: 8px; min-height: 50px; }
  .recent-item { color: var(--accent); padding: 2px 0; }
  .results-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 14px; }
  .result-col { background: var(--surface); border: 1px solid var(--border); border-radius: 6px; overflow: hidden; }
  .result-col.plain { border-left: 3px solid #a78bfa; }
  .result-col.ctx { border-left: 3px solid var(--accent); }
  .result-header { padding: 10px 14px; border-bottom: 1px solid var(--border); font-weight: bold; font-size: 12px;
                   display: flex; justify-content: space-between; }
  .result-header.plain { color: #a78bfa; }
  .result-header.ctx { color: var(--accent); }
  .result-item { padding: 10px 14px; border-bottom: 1px solid var(--border); font-size: 11px; }
  .result-item:last-child { border-bottom: none; }
  .result-item .id { color: var(--accent); font-weight: bold; font-family: monospace; }
  .result-item .score { color: var(--dim); margin-left: 6px; font-size: 10px; }
  .result-item .text { color: var(--text); margin-top: 4px; line-height: 1.55; }
  .result-item.shifted-up { background: rgba(163,230,53,0.06); }
  .empty { text-align: center; padding: 40px 20px; color: var(--dim); font-size: 12px; }
  @media (max-width: 900px) { .layout { grid-template-columns: 1fr; } .results-grid { grid-template-columns: 1fr; } }
</style></head><body>
<nav>
  <span class="brand">Vectora Context</span><span class="badge">LIVE ENGINE</span>
  <div class="links">
    <a href="/vectora/context">Product</a>
    <a href="/vectora/playground">Retrieval Playground</a>
    <a href="/vectora">Vectora</a>
    <a href="/pep">PEP</a>
  </div>
</nav>
<div class="layout">
  <div class="sidebar">
    <div class="label">1. Build the context</div>
    <div style="font-size:10px;color:var(--dim);margin-bottom:10px;line-height:1.6">
      Click any document below to simulate viewing it. The context tracker records each view; the context vector updates.
    </div>
    <div id="doc-list"></div>
    <div class="label" style="margin-top:18px">Session activity</div>
    <div id="recent" class="recent-list"><span style="color:var(--dim)">no views yet</span></div>
    <button class="btn-alt" onclick="clearSession()" style="margin-top:10px;width:100%">Clear session</button>

    <div class="label" style="margin-top:22px">2. Query</div>
    <input id="query" type="text" placeholder="e.g. merge, embedding, rate limit">
    <div style="margin-top:10px"><button class="btn" onclick="runQuery()" style="width:100%">Compare plain vs contextual</button></div>

    <div class="label" style="margin-top:22px">Sample queries</div>
    <div id="suggested" style="display:flex;flex-direction:column;gap:4px"></div>
  </div>
  <div class="main">
    <h2 style="font-size:16px;color:var(--accent);margin-bottom:10px">Context-modulated retrieval</h2>
    <div style="font-size:11px;color:var(--dim);line-height:1.7;margin-bottom:14px">
      The <b style="color:#a78bfa">left</b> column is plain Vectora retrieval. The <b style="color:var(--accent)">right</b> column reweights results by proximity to your session's context vector. Items highlighted green moved up because of context.
    </div>
    <div id="results"><div class="empty">Build a context and run a query.</div></div>
  </div>
</div>
<script>
const session = 'playground-' + Math.random().toString(36).slice(2, 8);
let sampleDocs = [];
let viewedIds = new Set();

async function init() {
  const r = await fetch('/vectora/playground/sample');
  const data = await r.json();
  sampleDocs = data.documents;
  const list = document.getElementById('doc-list');
  list.innerHTML = sampleDocs.map(d => `<button class="doc-btn" data-id="${d.id}" onclick="recordView('${d.id}')">${d.id}: ${d.text.slice(0, 60)}</button>`).join('');
  const sug = document.getElementById('suggested');
  sug.innerHTML = data.suggested_queries.map(q => `<button class="btn-alt" style="text-align:left;font-size:10px" onclick="document.getElementById('query').value='${q.replace(/'/g, "\\\\'")}';runQuery()">${q}</button>`).join('');
}
async function recordView(docId) {
  await fetch('/vectora/context-playground/record', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({session_id: session, doc_id: docId}),
  });
  viewedIds.add(docId);
  document.querySelectorAll('.doc-btn').forEach(b => {
    if (b.dataset.id === docId) b.classList.add('viewed');
  });
  const list = [...viewedIds].slice(-10);
  document.getElementById('recent').innerHTML = list.length ? list.map(id => `<div class="recent-item">• ${id}</div>`).join('') : '<span style="color:var(--dim)">no views yet</span>';
}
async function clearSession() {
  await fetch('/vectora/context-playground/clear', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({session_id: session}),
  });
  viewedIds.clear();
  document.querySelectorAll('.doc-btn').forEach(b => b.classList.remove('viewed'));
  document.getElementById('recent').innerHTML = '<span style="color:var(--dim)">no views yet</span>';
}
function esc(s) { return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
async function runQuery() {
  const q = document.getElementById('query').value.trim();
  if (!q) return;
  const r = await fetch('/vectora/context-playground/retrieve', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({session_id: session, query: q, k: 8}),
  });
  const data = await r.json();
  const plainOrder = {}; data.plain.forEach((p, i) => plainOrder[p.id] = i);
  function renderList(items, shiftedCheck) {
    return items.map((r, i) => {
      const shifted = shiftedCheck ? (plainOrder[r.id] === undefined || plainOrder[r.id] > i) : false;
      return `<div class="result-item${shifted ? ' shifted-up' : ''}"><div><span style="color:var(--dim)">${i+1}.</span> <span class="id">${esc(r.id)}</span><span class="score">score ${r.score.toFixed(3)}${r.hop_distance > 0 ? ' · hop '+r.hop_distance : ''}</span></div><div class="text">${esc(r.text)}</div></div>`;
    }).join('');
  }
  const html = `<div class="results-grid">
    <div class="result-col plain"><div class="result-header plain"><span>PLAIN</span><span style="color:var(--dim);font-weight:normal;font-size:10px">no context</span></div>${renderList(data.plain, false)}</div>
    <div class="result-col ctx"><div class="result-header ctx"><span>CONTEXTUAL</span><span style="color:var(--dim);font-weight:normal;font-size:10px">${data.session_size} recent views</span></div>${renderList(data.contextual, true)}</div>
  </div>`;
  document.getElementById('results').innerHTML = html;
}
init();
</script></body></html>
"""


_WATCH_HTML = """\
<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Vectora Watch Playground</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg: #14100a; --surface: #1f1a12; --surface2: #1a160e;
    --text: #eee2cb; --dim: #9a8870; --accent: #fbbf24; --border: #2e261a;
  }
  body { font-family: 'SF Mono', monospace; background: var(--bg); color: var(--text); line-height: 1.6; padding: 20px; }
  nav { position: sticky; top: 0; background: var(--bg); padding: 10px 0;
        border-bottom: 1px solid var(--border); display: flex; gap: 14px; align-items: center; flex-wrap: wrap; margin: -20px -20px 20px -20px; padding-left: 20px; padding-right: 20px; }
  .brand { font-size: 18px; font-weight: bold; color: var(--accent); }
  .badge { font-size: 9px; color: var(--accent); background: rgba(251,191,36,0.15);
           padding: 2px 8px; border-radius: 10px; letter-spacing: 0.05em; }
  .links { margin-left: auto; display: flex; gap: 14px; font-size: 11px; }
  .links a { color: var(--dim); text-decoration: none; }
  .links a:hover { color: var(--accent); }
  .container { max-width: 1100px; margin: 0 auto; }
  h2 { font-size: 16px; color: var(--accent); margin-bottom: 10px; }
  .desc { font-size: 11px; color: var(--dim); line-height: 1.7; margin-bottom: 16px; }
  input[type=text] { width: 100%; background: var(--surface2); color: var(--text);
                     border: 1px solid var(--border); border-radius: 4px;
                     padding: 10px 12px; font-family: inherit; font-size: 11px; }
  button { padding: 8px 18px; border-radius: 4px; border: 1px solid var(--accent);
           background: var(--accent); color: var(--bg); font-family: inherit; font-size: 11px; cursor: pointer; font-weight: bold; }
  button.alt { border-color: var(--border); background: transparent; color: var(--dim); font-weight: normal; }
  .controls { display: flex; gap: 8px; align-items: stretch; margin-bottom: 14px; flex-wrap: wrap; }
  .controls input { flex: 1; min-width: 200px; }
  .stream { background: var(--surface); border: 1px solid var(--border); border-radius: 6px;
            padding: 14px; min-height: 200px; max-height: 400px; overflow-y: auto; font-size: 11px; }
  .stream-item { padding: 8px 10px; margin-bottom: 4px; border-radius: 4px;
                 border-left: 3px solid transparent; background: var(--surface2); }
  .stream-item .label { font-size: 9px; letter-spacing: 0.1em; font-weight: bold; margin-left: 8px; }
  .stream-item.normal { border-left-color: #67e8f9; }
  .stream-item.notable { border-left-color: #fbbf24; }
  .stream-item.unusual { border-left-color: #f06292; }
  .stream-item.extreme { border-left-color: #ef4444; background: rgba(239,68,68,0.08); }
  .stream-item .components { font-size: 9px; color: var(--dim); margin-top: 4px; }
  .stats-row { display: flex; gap: 14px; background: var(--surface); border: 1px solid var(--border);
               border-radius: 6px; padding: 10px 14px; margin-bottom: 14px; font-size: 11px; flex-wrap: wrap; }
  .stat .k { color: var(--dim); }
  .stat .v { color: var(--accent); font-weight: bold; }
  .sample-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 14px; }
  .sample-btn { padding: 8px 12px; background: var(--surface2); border: 1px solid var(--border);
                border-radius: 4px; color: var(--text); text-align: left; cursor: pointer; font-size: 10px; }
  .sample-btn:hover { border-color: var(--accent); }
  .sample-btn .kind { font-size: 9px; color: var(--dim); letter-spacing: 0.1em; }
  @media (max-width: 700px) { .sample-grid { grid-template-columns: 1fr; } }
</style></head><body>
<nav>
  <span class="brand">Vectora Watch</span><span class="badge">LIVE ENGINE</span>
  <div class="links">
    <a href="/vectora/watch">Product</a>
    <a href="/vectora/playground">Retrieval Playground</a>
    <a href="/vectora">Vectora</a>
    <a href="/pep">PEP</a>
  </div>
</nav>
<div class="container">
  <h2>Anomaly + novelty scoring on streaming items</h2>
  <p class="desc">Submit items one at a time. Vectora Watch scores each against the corpus's embedding distribution + graph structure + recent history. Residual ≥ 70 is <b style="color:#f06292">unusual</b>; ≥ 85 is <b style="color:#ef4444">extreme</b>. Try a sample below or paste your own.</p>
  <div class="sample-grid" id="samples"></div>
  <div class="controls">
    <input id="text" type="text" placeholder="paste an item to score...">
    <button onclick="scoreItem()">Score</button>
    <button class="alt" onclick="resetStream()">Reset stream</button>
  </div>
  <div id="stats" class="stats-row" style="display:none"></div>
  <div id="stream" class="stream"><div style="color:var(--dim);text-align:center;padding:40px 20px">No items scored yet.</div></div>
</div>
<script>
const SAMPLES = [
  {kind: 'NORMAL', text: 'RAG pipeline rerank component for production LLM apps'},
  {kind: 'NORMAL', text: 'caching strategies with memcached and redis'},
  {kind: 'NORMAL', text: 'embedding dimensions and cosine similarity for semantic search'},
  {kind: 'NORMAL', text: 'prompt engineering patterns for chain of thought'},
  {kind: 'ANOMALOUS', text: 'volcanic eruption tectonic plates lava flow Hawaiian islands basalt'},
  {kind: 'ANOMALOUS', text: 'tyrannosaurus rex fossil jurassic paleontology dinosaur specimen'},
  {kind: 'ANOMALOUS', text: 'baroque violin concerto Vivaldi string ensemble classical music'},
  {kind: 'ANOMALOUS', text: 'peppermint tea brewing temperature steeping time aromatic leaves'},
];
function renderSamples() {
  document.getElementById('samples').innerHTML = SAMPLES.map(s => `<button class="sample-btn" onclick="pick('${s.text.replace(/'/g, "\\\\'")}')"><div class="kind">${s.kind}</div>${s.text}</button>`).join('');
}
function pick(t) { document.getElementById('text').value = t; scoreItem(); }
function esc(s) { return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
async function scoreItem() {
  const text = document.getElementById('text').value.trim();
  if (!text) return;
  const r = await fetch('/vectora/watch-playground/score', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({text, item_id: 'item-' + Date.now()}),
  });
  const data = await r.json();
  const stream = document.getElementById('stream');
  if (stream.firstChild && stream.firstChild.className?.indexOf('stream-item') < 0) stream.innerHTML = '';
  const item = document.createElement('div');
  item.className = 'stream-item ' + data.label;
  const labelCol = {normal:'#67e8f9', notable:'#fbbf24', unusual:'#f06292', extreme:'#ef4444'}[data.label] || '#fff';
  item.innerHTML = `<div><span style="color:${labelCol};font-weight:bold">residual ${data.residual}</span><span class="label" style="color:${labelCol}">${data.label.toUpperCase()}</span><span style="color:var(--text);margin-left:10px">${esc(data.text)}</span></div><div class="components">distance ${data.components.distance} · neighbor ${data.components.neighbor} · novelty ${data.components.novelty}</div>`;
  stream.insertBefore(item, stream.firstChild);
  // Stats
  const stats = document.getElementById('stats');
  stats.style.display = 'flex';
  stats.innerHTML = `<div class="stat"><span class="k">items scored:</span> <span class="v">${data.stats.n}</span></div><div class="stat"><span class="k">mean residual:</span> <span class="v">${data.stats.mean.toFixed(1)}</span></div><div class="stat"><span class="k">max residual:</span> <span class="v">${(data.stats.max || 0).toFixed(1)}</span></div><div class="stat"><span class="k">adaptive threshold:</span> <span class="v">${(data.stats.threshold || 0).toFixed(1)}</span></div>`;
  document.getElementById('text').value = '';
}
function resetStream() {
  document.getElementById('stream').innerHTML = '<div style="color:var(--dim);text-align:center;padding:40px 20px">No items scored yet.</div>';
  document.getElementById('stats').style.display = 'none';
}
renderSamples();
</script></body></html>
"""


_KG_HTML = """\
<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Vectora Graph Playground</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg: #0f0a14; --surface: #1b1224; --surface2: #17101e;
    --text: #e4daf4; --dim: #8a78a0; --accent: #c084fc; --border: #2a1e38;
  }
  body { font-family: 'SF Mono', monospace; background: var(--bg); color: var(--text); line-height: 1.6; }
  nav { position: sticky; top: 0; background: var(--bg); padding: 10px 20px;
        border-bottom: 1px solid var(--border); display: flex; gap: 14px; align-items: center; flex-wrap: wrap; z-index: 10; }
  .brand { font-size: 18px; font-weight: bold; color: var(--accent); }
  .badge { font-size: 9px; color: var(--accent); background: rgba(192,132,252,0.15);
           padding: 2px 8px; border-radius: 10px; letter-spacing: 0.05em; }
  .links { margin-left: auto; display: flex; gap: 14px; font-size: 11px; }
  .links a { color: var(--dim); text-decoration: none; }
  .links a:hover { color: var(--accent); }
  .layout { display: grid; grid-template-columns: 300px 1fr; min-height: calc(100vh - 50px); }
  .sidebar { background: var(--surface); border-right: 1px solid var(--border); padding: 18px; overflow-y: auto; }
  .main { padding: 18px 24px; }
  .label { font-size: 10px; color: var(--dim); letter-spacing: 0.15em; text-transform: uppercase; margin: 14px 0 6px; }
  select, input { width: 100%; background: var(--surface2); color: var(--text);
                  border: 1px solid var(--border); border-radius: 4px; padding: 6px 8px; font-family: inherit; font-size: 11px; }
  button { padding: 6px 14px; border-radius: 4px; border: 1px solid var(--accent);
           background: var(--accent); color: var(--bg); font-family: inherit; font-size: 11px; cursor: pointer; font-weight: bold; }
  button.alt { border-color: var(--border); background: transparent; color: var(--dim); font-weight: normal; }
  canvas { background: var(--surface); border: 1px solid var(--border); border-radius: 6px; display: block; width: 100%; height: 480px; }
  .stats { background: var(--surface); border: 1px solid var(--border); border-radius: 6px;
           padding: 10px 14px; margin-top: 14px; font-size: 10px; color: var(--dim); }
  .stats .v { color: var(--accent); font-weight: bold; }
  .results { background: var(--surface); border: 1px solid var(--border); border-radius: 6px; padding: 14px; margin-top: 14px; font-size: 11px; }
  .result-item { padding: 8px 0; border-bottom: 1px solid var(--border); }
  .result-item:last-child { border-bottom: none; }
  .relation-chain { font-size: 10px; color: var(--accent); margin-top: 2px; }
  @media (max-width: 900px) { .layout { grid-template-columns: 1fr; } }
</style></head><body>
<nav>
  <span class="brand">Vectora Graph</span><span class="badge">LIVE ENGINE</span>
  <div class="links">
    <a href="/vectora/graph">Product</a>
    <a href="/vectora/playground">Retrieval Playground</a>
    <a href="/vectora">Vectora</a>
    <a href="/pep">PEP</a>
  </div>
</nav>
<div class="layout">
  <div class="sidebar">
    <div class="label">Add typed edge</div>
    <select id="edge-source"><option>loading…</option></select>
    <div class="label" style="margin-top:8px">relation</div>
    <select id="edge-relation"></select>
    <div class="label" style="margin-top:8px">target</div>
    <select id="edge-target"></select>
    <div style="display:flex;gap:4px;margin-top:10px">
      <button onclick="addTriple()" style="flex:1">Add triple</button>
    </div>

    <div class="label" style="margin-top:22px">Traverse</div>
    <select id="tr-start"></select>
    <div class="label" style="margin-top:8px">max hops</div>
    <input id="tr-hops" type="number" min="1" max="4" value="2">
    <div style="margin-top:10px"><button onclick="traverse()" style="width:100%">Walk the graph</button></div>

    <div class="label" style="margin-top:22px">Seeded edges</div>
    <div style="font-size:10px;color:var(--dim);line-height:1.6">The demo starts with a handful of curated edges between the sample documents (caching → memory pressure, RAG components, etc.). Add your own to extend.</div>

    <button class="alt" onclick="refreshViz()" style="width:100%;margin-top:14px">Refresh visualization</button>
  </div>
  <div class="main">
    <h2 style="font-size:16px;color:var(--accent);margin-bottom:10px">Knowledge graph</h2>
    <canvas id="graph"></canvas>
    <div id="stats" class="stats"></div>
    <div id="results" class="results" style="display:none"></div>
  </div>
</div>
<script>
let nodes = [], edges = [];
const positions = {};
async function init() {
  const r = await fetch('/vectora/graph-playground/sample');
  const data = await r.json();
  const nodeOptions = data.nodes.map(n => `<option value="${n.id}">${n.id}: ${n.text.slice(0, 36)}</option>`).join('');
  const relOptions = data.relations.map(r => `<option value="${r}">${r}</option>`).join('');
  document.getElementById('edge-source').innerHTML = nodeOptions;
  document.getElementById('edge-target').innerHTML = nodeOptions;
  document.getElementById('edge-relation').innerHTML = relOptions;
  document.getElementById('tr-start').innerHTML = nodeOptions;
  await refreshViz();
}
async function refreshViz() {
  const r = await fetch('/vectora/graph-playground/viz');
  const data = await r.json();
  nodes = data.nodes;
  edges = data.edges;
  layoutNodes();
  drawGraph();
  const stats = data.stats;
  document.getElementById('stats').innerHTML = `typed edges: <span class="v">${stats.typed_edges}</span> · unique relations: <span class="v">${stats.unique_relations}</span> · nodes: <span class="v">${nodes.length}</span>`;
}
function layoutNodes() {
  // Only layout nodes that actually appear in some edge (plus optionally all)
  const inEdges = new Set();
  edges.forEach(e => { inEdges.add(e.source); inEdges.add(e.target); });
  const relevant = nodes.filter(n => inEdges.has(n.id));
  const W = 900, H = 460;
  relevant.forEach((n, i) => {
    const angle = (i / relevant.length) * Math.PI * 2;
    const radius = Math.min(W, H) * 0.38;
    positions[n.id] = { x: W/2 + Math.cos(angle) * radius, y: H/2 + Math.sin(angle) * radius };
  });
}
function drawGraph() {
  const canvas = document.getElementById('graph');
  const ctx = canvas.getContext('2d');
  // Set the backing buffer to match the CSS size for crisp drawing
  const r = canvas.getBoundingClientRect();
  canvas.width = r.width; canvas.height = r.height;
  const W = r.width, H = r.height;
  const sx = W / 900, sy = H / 460;
  ctx.fillStyle = '#0f0a14'; ctx.fillRect(0, 0, W, H);
  // Edges
  edges.forEach(e => {
    const s = positions[e.source], t = positions[e.target];
    if (!s || !t) return;
    ctx.strokeStyle = `rgba(192,132,252,${0.3 + e.confidence * 0.5})`;
    ctx.lineWidth = 1 + e.weight * 0.8;
    ctx.beginPath(); ctx.moveTo(s.x * sx, s.y * sy); ctx.lineTo(t.x * sx, t.y * sy); ctx.stroke();
    ctx.fillStyle = 'rgba(163,230,53,0.75)'; ctx.font = '9px monospace'; ctx.textAlign = 'center';
    ctx.fillText(e.relation, (s.x + t.x) * sx / 2, (s.y + t.y) * sy / 2 - 4);
  });
  // Nodes
  Object.entries(positions).forEach(([id, p]) => {
    const x = p.x * sx, y = p.y * sy;
    ctx.fillStyle = 'rgba(192,132,252,0.5)';
    ctx.beginPath(); ctx.arc(x, y, 18, 0, Math.PI*2); ctx.fill();
    ctx.strokeStyle = 'rgba(192,132,252,0.95)'; ctx.lineWidth = 1.5; ctx.stroke();
    ctx.fillStyle = '#fff'; ctx.font = 'bold 9px monospace'; ctx.textAlign = 'center';
    ctx.fillText(id, x, y + 3);
  });
}
function esc(s) { return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
async function addTriple() {
  const source = document.getElementById('edge-source').value;
  const relation = document.getElementById('edge-relation').value;
  const target = document.getElementById('edge-target').value;
  if (source === target) { alert('source and target must differ'); return; }
  const r = await fetch('/vectora/graph-playground/triple', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({source, relation, target}),
  });
  if (!r.ok) { alert('add failed'); return; }
  await refreshViz();
}
async function traverse() {
  const start = document.getElementById('tr-start').value;
  const hops = parseInt(document.getElementById('tr-hops').value);
  const r = await fetch('/vectora/graph-playground/traverse', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({start, max_hops: hops}),
  });
  const data = await r.json();
  const res = document.getElementById('results');
  res.style.display = 'block';
  if (!data.results.length) { res.innerHTML = `<div style="color:var(--dim)">No reachable neighbors from ${esc(start)} within ${hops} hops.</div>`; return; }
  res.innerHTML = `<div style="color:var(--dim);margin-bottom:6px">Reachable from <b style="color:var(--accent)">${esc(start)}</b> within ${hops} hop(s): <b class="v">${data.results.length}</b></div>` +
    data.results.map(r => {
      const chain = r.relations_to_seed.map(p => `${p[1]} →[${p[0]}]`).join(' ');
      return `<div class="result-item"><div><b style="color:var(--accent)">${esc(r.doc_id)}</b> <span style="color:var(--dim);font-size:10px">weight ${r.total_weight} · hop ${r.hop_distance}</span></div><div class="relation-chain">${esc(chain)}→ ${esc(r.doc_id)}</div><div style="font-size:10px;color:var(--text);margin-top:4px">${esc(r.text)}</div></div>`;
    }).join('');
}
init();
window.addEventListener('resize', drawGraph);
</script></body></html>
"""


@router.get("/vectora/context-playground", response_class=HTMLResponse)
async def ctx_playground_page() -> str:
    return _CTX_HTML


@router.get("/vectora/watch-playground", response_class=HTMLResponse)
async def watch_playground_page() -> str:
    return _WATCH_HTML


@router.get("/vectora/graph-playground", response_class=HTMLResponse)
async def kg_playground_page() -> str:
    return _KG_HTML
