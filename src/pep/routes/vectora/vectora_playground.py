"""Vectora playground — live developer console backed by the real engine.

  GET  /vectora/playground  — the playground UI
  POST /vectora/playground/retrieve  — run a retrieval against a corpus
  GET  /vectora/playground/sample  — load a curated sample corpus

The retrieval actually runs the Vectora engine (pep.vectora), not a fake demo.
Paste your own documents or use the sample corpus; the graph is built in-memory
per request. For larger corpora, use the Vectora SDK directly — this endpoint
is rate-limited and capped at 50 documents per call.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from pep.vectora import Document, RetrievalMode, VectoraRetriever
from pep.vectora.demo import SAMPLE_CORPUS

router = APIRouter()

MAX_DOCS = 50
MAX_QUERY_LEN = 500


class DocInput(BaseModel):
    id: str
    text: str


class RetrieveRequest(BaseModel):
    documents: list[DocInput]
    query: str
    k: int = 8
    decay: float = 0.4


@router.post("/vectora/playground/retrieve")
async def playground_retrieve(req: RetrieveRequest) -> dict[str, Any]:
    if len(req.documents) > MAX_DOCS:
        raise HTTPException(400, f"max {MAX_DOCS} documents per request")
    if len(req.query) > MAX_QUERY_LEN:
        raise HTTPException(400, f"query too long (max {MAX_QUERY_LEN} chars)")
    if not req.documents:
        raise HTTPException(400, "no documents provided")

    retriever = VectoraRetriever()
    retriever.add_documents([Document(id=d.id, text=d.text) for d in req.documents])
    stats = retriever.build_graph()
    topk = retriever.retrieve(req.query, k=req.k, mode=RetrievalMode.TOPK, decay=req.decay)
    vec = retriever.retrieve(req.query, k=req.k, mode=RetrievalMode.VECTORA, decay=req.decay)

    def serialize(results):
        return [
            {
                "id": r.doc.id,
                "text": r.doc.text,
                "score": round(r.score, 4),
                "hop_distance": r.hop_distance,
                "breakdown": {k: round(v, 4) for k, v in r.score_breakdown.items()},
            }
            for r in results
        ]

    topk_ids = {r.doc.id for r in topk}
    vec_added = [r for r in vec if r.doc.id not in topk_ids]
    return {
        "query": req.query,
        "stats": stats,
        "topk": serialize(topk),
        "vectora": serialize(vec),
        "vectora_added": serialize(vec_added),
    }


@router.get("/vectora/playground/sample")
async def playground_sample() -> dict[str, Any]:
    return {
        "documents": [{"id": d.id, "text": d.text} for d in SAMPLE_CORPUS],
        "suggested_queries": [
            "caching strategies for a monolith",
            "rate limiting and load shedding",
            "embedding-based document search",
            "reducing LLM inference cost",
        ],
    }


_PAGE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Vectora Playground — live retrieval</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg: #0a121a; --surface: #142028; --surface2: #0f181f;
    --text: #dce6ed; --dim: #6a808a; --accent: #38bdf8; --accent2: #a3e635;
    --warn: #f59e0b; --border: #1f3040;
  }
  body { font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
         background: var(--bg); color: var(--text); line-height: 1.6; }
  a { color: var(--accent); text-decoration: none; }
  a:hover { text-decoration: underline; }
  nav { position: sticky; top: 0; z-index: 50; background: var(--bg);
        padding: 10px 20px; border-bottom: 1px solid var(--border);
        display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }
  .brand { font-size: 18px; font-weight: bold; color: var(--accent); letter-spacing: 0.5px; }
  .badge { font-size: 9px; color: var(--accent); background: rgba(56,189,248,0.15);
           padding: 2px 8px; border-radius: 10px; letter-spacing: 0.05em; }
  .nav-links { margin-left: auto; display: flex; gap: 14px; font-size: 11px; }
  .nav-links a { color: var(--dim); }
  .nav-links a:hover { color: var(--accent); }

  .layout { display: grid; grid-template-columns: 360px 1fr; min-height: calc(100vh - 50px); }
  .sidebar { background: var(--surface); border-right: 1px solid var(--border);
             padding: 18px; overflow-y: auto; }
  .main { padding: 18px 24px; overflow-y: auto; }
  .section-label { font-size: 10px; color: var(--dim); letter-spacing: 0.15em;
                   text-transform: uppercase; margin-bottom: 8px; }
  textarea, input {
    width: 100%; background: var(--surface2); color: var(--text);
    border: 1px solid var(--border); border-radius: 4px;
    padding: 8px 10px; font-family: inherit; font-size: 11px; line-height: 1.6;
  }
  textarea:focus, input:focus { outline: none; border-color: var(--accent); }
  button.btn {
    padding: 6px 14px; border-radius: 4px; border: 1px solid var(--accent);
    background: var(--accent); color: var(--bg); font-size: 11px; cursor: pointer;
    font-family: inherit; font-weight: bold;
  }
  button.btn-secondary {
    padding: 6px 14px; border-radius: 4px; border: 1px solid var(--border);
    background: transparent; color: var(--dim); font-size: 11px; cursor: pointer;
    font-family: inherit;
  }
  button.btn-secondary:hover { color: var(--text); border-color: var(--accent); }
  button:disabled { opacity: 0.5; cursor: not-allowed; }

  .slider-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; font-size: 11px; }
  .slider-row span:first-child { min-width: 60px; color: var(--dim); }
  .slider-row input[type=range] { flex: 1; }
  .slider-row .val { color: var(--accent); font-weight: bold; min-width: 34px; text-align: right; }

  .stats-row { display: flex; gap: 14px; flex-wrap: wrap; padding: 10px 14px;
               background: var(--surface); border: 1px solid var(--border); border-radius: 6px;
               margin-bottom: 14px; font-size: 11px; }
  .stat { display: flex; gap: 6px; }
  .stat .k { color: var(--dim); }
  .stat .v { color: var(--accent); font-weight: bold; }

  .results-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
  .result-column { background: var(--surface); border: 1px solid var(--border); border-radius: 6px; overflow: hidden; }
  .result-column.vectora { border-left: 3px solid var(--accent); }
  .result-column.topk { border-left: 3px solid #a78bfa; }
  .result-header { padding: 10px 14px; border-bottom: 1px solid var(--border); font-weight: bold; font-size: 12px;
                   display: flex; justify-content: space-between; align-items: center; }
  .result-header .topk-h { color: #a78bfa; }
  .result-header .vec-h { color: var(--accent); }
  .result-item { padding: 10px 14px; border-bottom: 1px solid var(--border); font-size: 11px; }
  .result-item:last-child { border-bottom: none; }
  .result-item .id { color: var(--accent); font-weight: bold; display: inline-block; min-width: 80px; }
  .result-item .score { color: var(--dim); margin-left: 6px; }
  .result-item .hop { display: inline-block; background: rgba(163,230,53,0.15);
                      color: var(--accent2); padding: 1px 6px; border-radius: 8px;
                      font-size: 9px; margin-left: 6px; }
  .result-item .text { color: var(--text); margin-top: 4px; line-height: 1.55; }
  .result-item.added { background: rgba(163,230,53,0.06); }

  .added-callout { background: rgba(163,230,53,0.1); border: 1px solid rgba(163,230,53,0.3);
                   border-radius: 6px; padding: 14px 16px; margin: 14px 0; }
  .added-callout .title { color: var(--accent2); font-weight: bold; font-size: 12px; margin-bottom: 8px; }
  .added-callout .item { font-size: 11px; color: var(--text); margin-bottom: 4px; }
  .added-callout .item .id { color: var(--accent2); font-weight: bold; }

  .empty-state { text-align: center; padding: 40px 20px; color: var(--dim); }
  .empty-state .icon { font-size: 28px; margin-bottom: 10px; }

  .loading { opacity: 0.5; pointer-events: none; }

  pre { background: var(--surface2); border: 1px solid var(--border); border-radius: 4px;
        padding: 12px; font-size: 11px; overflow-x: auto; color: var(--text); margin: 10px 0; }

  @media (max-width: 900px) {
    .layout { grid-template-columns: 1fr; }
    .sidebar { border-right: none; border-bottom: 1px solid var(--border); }
    .results-grid { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>
<nav>
  <span class="brand">Vectora Playground</span>
  <span class="badge">LIVE ENGINE</span>
  <div class="nav-links">
    <a href="/vectora/retrieval">Product</a>
    <a href="/vectora">Vectora app</a>
    <a href="/pep">PEP</a>
  </div>
</nav>

<div class="layout">
  <div class="sidebar">
    <div class="section-label">1. Corpus</div>
    <div style="display:flex;gap:6px;margin-bottom:8px">
      <button class="btn-secondary" onclick="loadSample()">Load sample</button>
      <button class="btn-secondary" onclick="clearCorpus()">Clear</button>
      <span id="doc-count" style="margin-left:auto;color:var(--dim);font-size:10px;align-self:center"></span>
    </div>
    <textarea id="corpus" rows="14" placeholder="Paste one document per line, id: text
example:
cache-1: Redis caching strategies for Django applications
cache-2: Cache-aside pattern explained..."></textarea>

    <div class="section-label" style="margin-top:14px">2. Query</div>
    <input id="query" type="text" placeholder="Ask a question of the corpus…">

    <div class="section-label" style="margin-top:14px">3. Parameters</div>
    <div class="slider-row">
      <span>k results</span>
      <input type="range" id="k" min="3" max="20" value="8" oninput="document.getElementById('k-v').textContent=this.value">
      <span class="val" id="k-v">8</span>
    </div>
    <div class="slider-row">
      <span>decay</span>
      <input type="range" id="decay" min="10" max="90" value="40" oninput="document.getElementById('decay-v').textContent=(this.value/100).toFixed(2)">
      <span class="val" id="decay-v">0.40</span>
    </div>

    <div style="margin-top:18px;display:flex;gap:8px">
      <button class="btn" onclick="runRetrieval()" id="run-btn">Run retrieval</button>
    </div>

    <div class="section-label" style="margin-top:22px">Suggested queries</div>
    <div id="suggestions" style="display:flex;flex-direction:column;gap:6px"></div>

    <div class="section-label" style="margin-top:22px">About</div>
    <div style="font-size:10px;color:var(--dim);line-height:1.7">
      This playground runs the real Vectora engine
      (<code>pep.vectora</code>) in-process. Your corpus is embedded with a
      local TF-IDF embedder, a document graph is built, and two retrievers
      run side by side: top-k nearest by similarity, and Vectora's
      spreading-activation graph walk. No data leaves the server.
    </div>
  </div>

  <div class="main">
    <div id="stats-row" class="stats-row" style="display:none"></div>
    <div id="results">
      <div class="empty-state">
        <div class="icon">▸</div>
        <div style="font-size:13px;margin-bottom:6px">Load a corpus and run a query to see the comparison.</div>
        <div style="font-size:11px">Click <b>Load sample</b> to use the curated demo corpus, or paste your own documents in the sidebar.</div>
      </div>
    </div>
  </div>
</div>

<script>
function parseCorpus() {
  const raw = document.getElementById('corpus').value;
  const docs = [];
  const seen = new Set();
  for (const line of raw.split('\\n')) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    const colonIdx = trimmed.indexOf(':');
    if (colonIdx < 1) continue;
    const id = trimmed.slice(0, colonIdx).trim();
    const text = trimmed.slice(colonIdx + 1).trim();
    if (!id || !text) continue;
    if (seen.has(id)) continue;
    seen.add(id);
    docs.push({ id, text });
  }
  return docs;
}
function updateDocCount() {
  const docs = parseCorpus();
  document.getElementById('doc-count').textContent = docs.length ? docs.length + ' docs' : '';
}
document.getElementById('corpus').addEventListener('input', updateDocCount);

async function loadSample() {
  const r = await fetch('/vectora/playground/sample');
  const data = await r.json();
  const lines = data.documents.map(d => d.id + ': ' + d.text).join('\\n');
  document.getElementById('corpus').value = lines;
  updateDocCount();
  const sug = document.getElementById('suggestions');
  sug.innerHTML = data.suggested_queries.map(q =>
    '<button class="btn-secondary" style="text-align:left;font-size:10px" onclick="document.getElementById(\\'query\\').value=\\'' + q.replace(/'/g, "\\\\'") + '\\';runRetrieval()">' + q + '</button>'
  ).join('');
  if (!document.getElementById('query').value) {
    document.getElementById('query').value = data.suggested_queries[0];
  }
}
function clearCorpus() {
  document.getElementById('corpus').value = '';
  document.getElementById('query').value = '';
  document.getElementById('results').innerHTML = '<div class="empty-state"><div class="icon">▸</div><div style="font-size:13px">Corpus cleared.</div></div>';
  document.getElementById('stats-row').style.display = 'none';
  document.getElementById('suggestions').innerHTML = '';
  updateDocCount();
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function renderResults(data) {
  const statsEl = document.getElementById('stats-row');
  statsEl.style.display = 'flex';
  statsEl.innerHTML =
    '<div class="stat"><span class="k">docs:</span><span class="v">' + data.stats.nodes + '</span></div>' +
    '<div class="stat"><span class="k">embedding edges:</span><span class="v">' + data.stats.embedding_edges + '</span></div>' +
    '<div class="stat"><span class="k">keyword edges:</span><span class="v">' + data.stats.keyword_edges + '</span></div>' +
    '<div class="stat"><span class="k">total edges:</span><span class="v">' + data.stats.total_edges + '</span></div>' +
    '<div class="stat" style="margin-left:auto"><span class="k">query:</span><span class="v">"' + escapeHtml(data.query) + '"</span></div>';

  const topkIds = new Set(data.topk.map(r => r.id));
  const vecIds = new Set(data.vectora.map(r => r.id));

  function renderList(results, mode) {
    if (!results.length) return '<div class="result-item"><em style="color:var(--dim)">no results</em></div>';
    return results.map((r, i) => {
      const isAdded = mode === 'vectora' && !topkIds.has(r.id);
      const hopBadge = r.hop_distance > 0 ? '<span class="hop">hop ' + r.hop_distance + '</span>' : '';
      return '<div class="result-item' + (isAdded ? ' added' : '') + '">' +
        '<div><span style="color:var(--dim)">' + (i+1) + '.</span> ' +
        '<span class="id">' + escapeHtml(r.id) + '</span>' +
        '<span class="score">score ' + r.score.toFixed(3) + '</span>' +
        hopBadge + '</div>' +
        '<div class="text">' + escapeHtml(r.text) + '</div>' +
      '</div>';
    }).join('');
  }

  let html = '<div class="results-grid">';
  html += '<div class="result-column topk"><div class="result-header"><span class="topk-h">TOP-K (baseline)</span><span style="color:var(--dim);font-weight:normal;font-size:10px">' + data.topk.length + ' results</span></div>' + renderList(data.topk, 'topk') + '</div>';
  html += '<div class="result-column vectora"><div class="result-header"><span class="vec-h">VECTORA (spreading activation)</span><span style="color:var(--dim);font-weight:normal;font-size:10px">' + data.vectora.length + ' results</span></div>' + renderList(data.vectora, 'vectora') + '</div>';
  html += '</div>';

  if (data.vectora_added.length) {
    html += '<div class="added-callout"><div class="title">Vectora surfaced ' + data.vectora_added.length + ' document(s) top-k missed</div>';
    html += data.vectora_added.map(r =>
      '<div class="item"><span class="id">' + escapeHtml(r.id) + '</span>' +
      (r.hop_distance > 0 ? ' <span style="color:var(--accent2);font-size:9px">[hop ' + r.hop_distance + ']</span>' : '') +
      ' — ' + escapeHtml(r.text) + '</div>'
    ).join('');
    html += '</div>';
  }

  document.getElementById('results').innerHTML = html;
}

async function runRetrieval() {
  const docs = parseCorpus();
  const query = document.getElementById('query').value.trim();
  if (!docs.length) { alert('Load or paste a corpus first'); return; }
  if (!query) { alert('Enter a query'); return; }
  const k = parseInt(document.getElementById('k').value);
  const decay = parseInt(document.getElementById('decay').value) / 100;
  const btn = document.getElementById('run-btn');
  btn.disabled = true; btn.textContent = 'Running…';
  document.getElementById('results').classList.add('loading');
  try {
    const r = await fetch('/vectora/playground/retrieve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ documents: docs, query, k, decay }),
    });
    if (!r.ok) {
      const err = await r.json().catch(() => ({ detail: 'request failed' }));
      throw new Error(err.detail || 'retrieval failed');
    }
    const data = await r.json();
    renderResults(data);
  } catch (e) {
    document.getElementById('results').innerHTML = '<div class="empty-state"><div style="color:#f06292">Error: ' + escapeHtml(e.message) + '</div></div>';
  } finally {
    btn.disabled = false; btn.textContent = 'Run retrieval';
    document.getElementById('results').classList.remove('loading');
  }
}
</script>
</body>
</html>
"""


@router.get("/vectora/playground", response_class=HTMLResponse)
async def playground_page() -> str:
    return _PAGE
