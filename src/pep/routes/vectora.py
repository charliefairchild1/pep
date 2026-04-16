"""Vectora — Data organization, pattern analysis, intelligent retrieval. Serves at /vectora."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

_PAGE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Vectora — Data Organization, Pattern Analysis, Intelligent Retrieval</title>
<style>
  :root {
    --bg: #0b0e14; --surface: #141a24; --surface2: #0f141e;
    --text: #dce4ed; --dim: #6a7a8a; --accent: #38bdf8; --accent2: #a3e635;
    --warn: #f59e0b; --border: #1c2535;
  }
  body.light {
    --bg: #f6f9fc; --surface: #ffffff; --surface2: #ebf0f7;
    --text: #1a1a1a; --dim: #556; --accent: #0369a1; --accent2: #4d7c0f;
    --warn: #b45309; --border: #cdd5de;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
         background: var(--bg); color: var(--text);
         transition: background-color 0.2s, color 0.2s; }
  a { color: var(--accent); text-decoration: none; }
  a:hover { text-decoration: underline; }
  nav { position: sticky; top: 0; z-index: 50; background: var(--bg);
        padding: 6px 20px 0 20px; border-bottom: 1px solid var(--border); }
  .nav-row { display: flex; gap: 14px; align-items: center; }
  .nav-row-top { padding-bottom: 6px; border-bottom: 1px solid var(--border); }
  .nav-row-bottom { padding: 4px 0; }
  .nav-btn { padding: 4px 12px; border-radius: 4px; border: 1px solid var(--accent);
             background: transparent; color: var(--accent); font-size: 11px; cursor: pointer;
             font-family: inherit; }
  .nav-btn:hover { background: var(--surface); }
  .brand { font-size: 18px; font-weight: bold; color: var(--accent); }
  .tabs { display: flex; gap: 0; flex-wrap: wrap; }
  .tab { padding: 6px 14px; font-size: 11px; cursor: pointer; color: var(--dim);
         border-bottom: 2px solid transparent; transition: all 0.2s; }
  .tab:hover { color: var(--text); }
  .tab.active { color: var(--accent); border-bottom-color: var(--accent); }
  .panel { display: none; }
  .panel.active { display: block; }
  .container { max-width: 1000px; margin: 0 auto; padding: 20px; }
  h2 { font-size: 16px; color: var(--accent); margin-bottom: 6px; scroll-margin-top: 130px; }
  h3 { font-size: 13px; color: var(--accent2); margin: 20px 0 8px; scroll-margin-top: 130px; }
  .desc { font-size: 11px; color: var(--dim); line-height: 1.6; margin-bottom: 16px; }
  .canvas-box { position: relative; background: var(--surface); border: 1px solid var(--border);
                 border-radius: 8px; overflow: hidden; margin-bottom: 12px; }
  .controls { display: flex; flex-wrap: wrap; gap: 6px; align-items: center;
              padding: 8px 12px; font-size: 11px; }
  .controls button { padding: 4px 12px; border-radius: 4px; border: 1px solid var(--border);
                     background: var(--surface); color: var(--text); font-size: 11px;
                     cursor: pointer; font-family: inherit; }
  .controls button:hover { border-color: var(--accent); }
  .info { font-size: 11px; color: var(--dim); padding: 10px 14px; background: var(--surface);
          border: 1px solid var(--border); border-radius: 6px; margin-bottom: 16px; line-height: 1.7; }
  .info b { color: var(--text); }
  .stat-val { color: var(--accent); font-weight: bold; }
  .hero { background: linear-gradient(180deg, var(--surface) 0%, var(--bg) 100%);
          border: 1px solid var(--border); border-radius: 8px; padding: 28px 32px;
          margin-bottom: 24px; }
  .hero h1 { font-size: 22px; color: var(--accent); margin-bottom: 8px; font-weight: bold; }
  .hero p { font-size: 12px; color: var(--text); line-height: 1.8; margin-bottom: 8px; }
  .hero .tag { font-size: 10px; color: var(--dim); letter-spacing: 0.2em;
               text-transform: uppercase; margin-bottom: 4px; }
</style>
</head>
<body>
<nav>
  <div class="nav-row nav-row-top">
    <span class="brand">Vectora</span>
    <span style="font-size:10px;color:var(--dim)">Data Organization · Pattern Analysis · Intelligent Retrieval</span>
    <span id="pep-link-badge" style="margin-left:auto;font-size:10px;color:var(--dim);display:flex;align-items:center;gap:6px;padding:0 8px">
      <span id="pep-link-dot" style="width:8px;height:8px;border-radius:50%;background:#666;display:inline-block"></span>
      <span id="pep-link-label">PEP: …</span>
    </span>
    <select id="canvas-select" onchange="canvasSelect(this.value)"
      style="background:var(--surface);color:var(--text);border:1px solid var(--border);
      border-radius:4px;padding:4px 8px;font-family:inherit;font-size:10px;max-width:220px">
      <option value="">jump to canvas…</option>
    </select>
    <button onclick="downloadVectora()" class="nav-btn">Download</button>
    <button onclick="toggleLight()" id="light-btn" class="nav-btn">Light Mode</button>
    <a href="/pep" style="font-size:11px">&larr; PEP</a>
    <a href="/axona" style="font-size:11px">Axona</a>
    <a href="/lingora" style="font-size:11px">Lingora</a>
    <a href="/atria" style="font-size:11px">Atria</a>
  </div>
  <div class="nav-row nav-row-bottom">
    <div class="tabs" id="tabs">
      <div class="tab active" data-panel="home-tab">Home</div>
      <div class="tab" data-panel="keyword-tab">Keyword vs Semantic</div>
      <div class="tab" data-panel="embed-tab">Embedding Space</div>
      <div class="tab" data-panel="kg-tab">Knowledge Graph</div>
      <div class="tab" data-panel="anomaly-tab">Anomaly Detection</div>
      <div class="tab" data-panel="context-tab">Context-Dependent Retrieval</div>
      <div class="tab" data-panel="theory-tab">Theory</div>
      <div class="tab" data-panel="bridge-tab">PEP &harr; Vectora</div>
    </div>
  </div>
</nav>

<!-- ═══ Home ══════════════════════════════════════════════════════ -->
<div class="panel active" id="home-tab">
<div class="container">
  <div class="hero">
    <div class="tag">VECTORA</div>
    <h1>Find What You Did Not Know to Ask For</h1>
    <p>
      Keyword search finds what you already know exists. Vectora finds
      what you need but could not have named &mdash; because the item
      that answers your question is connected to your query through two
      hops of meaning, not through a shared string. Items are nodes in a
      weighted graph. Retrieval is spreading activation. Novelty is
      residual scoring. Context modulates the whole thing so the same
      query gives different answers when you need different answers.
    </p>
    <p>
      Vectora is the internal infrastructure layer. The other LAVAS
      siblings (Axona, Lingora, Atria) will consume it. PvP matchmaking
      needs to retrieve player profiles. Cognitive modeling needs to
      retrieve memories. Language processing needs to retrieve word
      constellations. All of them need the same primitive &mdash;
      Vectora builds it once.
    </p>
  </div>

  <h3>What is here so far</h3>
  <div class="info">
    Five interactive canvases establishing the thesis:<br><br>
    &bull; <b>Keyword vs Semantic</b> &mdash; same query, two retrieval
    methods, dramatically different results. Shows why keyword search
    misses most of the value.<br>
    &bull; <b>Embedding Space</b> &mdash; documents as points in a
    high-dimensional space projected to 2D. Cluster structure, distance
    as meaning, and the nearest-neighbor illusion.<br>
    &bull; <b>Knowledge Graph</b> &mdash; entities with typed
    relationships. Click to traverse. Spreading activation finds paths
    keyword search cannot.<br>
    &bull; <b>Anomaly Detection</b> &mdash; the residual scorer applied
    to data patterns. Expected items produce low residuals; unexpected
    items spike.<br>
    &bull; <b>Context-Dependent Retrieval</b> &mdash; the same query
    returns different results depending on the user's recent context.
    State modulation on the retrieval graph.<br><br>
    Full theory framing is in <code>~/projects/vectora/docs/theory.md</code>
    and the Theory tab.
  </div>
</div>
</div>

<!-- ═══ Keyword vs Semantic ═══════════════════════════════════════ -->
<div class="panel" id="keyword-tab">
<div class="container">
  <h2>Keyword vs Semantic Search</h2>
  <p class="desc">
    Type "bank" and keyword search returns every document containing the
    string "bank." Semantic search returns documents about financial
    institutions, riverbanks, blood banks, or all three &mdash; depending
    on the query's embedding vector and what is close to it in the space.
  </p>
  <div class="canvas-box">
    <canvas id="keyword-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <button onclick="searchPick('jaguar')">Query: "jaguar"</button>
    <button onclick="searchPick('python')">Query: "python"</button>
    <button onclick="searchPick('cell')">Query: "cell"</button>
    <button onclick="searchReset()">Reset</button>
  </div>
  <div class="info">
    <b>What you are watching:</b> A query with multiple possible
    meanings. On the left, keyword results &mdash; every document
    containing the query string, regardless of meaning. On the right,
    semantic results &mdash; documents whose embeddings are close to
    the query's embedding, clustered by meaning. The semantic side
    naturally separates the animal "jaguar" from the car "Jaguar"
    from the guitar brand, because each meaning lives in a different
    part of the embedding space.<br><br>
    <b>Why this matters:</b> Keyword search has perfect recall for
    exact matches and zero recall for everything else. Semantic search
    has softer recall &mdash; it can miss an exact match if the
    embedding is noisy &mdash; but it finds related items that share
    no keywords with the query. The combination of both is stronger
    than either alone. This is what modern RAG pipelines do: keyword
    retrieval + vector retrieval, merged and re-ranked.<br><br>
    <b>See also:</b>
    <a href="/pep">PEP &rarr; Spreading Activation</a>,
    <a href="/lingora">Lingora &rarr; Word as Constellation</a>.
  </div>
</div>
</div>

<!-- ═══ Embedding Space ═══════════════════════════════════════════ -->
<div class="panel" id="embed-tab">
<div class="container">
  <h2>Embedding Space &mdash; Documents as Points in Meaning</h2>
  <p class="desc">
    Every document is a point in a high-dimensional space. Items with
    similar meaning cluster together. Items with different meaning are
    far apart. Click a cluster to see what binds it.
  </p>
  <div class="canvas-box">
    <canvas id="embed-canvas" width="960" height="460"></canvas>
  </div>
  <div class="controls">
    <button onclick="embedRegen()">Regenerate</button>
    <button onclick="embedToggleLabels()">Toggle labels</button>
  </div>
  <div class="info">
    <b>What you are watching:</b> 80 synthetic "documents" projected
    from a 768-dimensional embedding space down to 2D (via synthetic
    PCA). The color bands are clusters &mdash; groups of documents
    whose embeddings are mutually close. The distances on screen
    approximate the distances in the full space: items near each
    other on screen are semantically similar; items far apart are
    semantically different.<br><br>
    <b>The nearest-neighbor illusion:</b> In very high dimensions, many
    items are equidistant from a query. The "nearest neighbor" is only
    slightly closer than the 10th or 50th nearest. This is why
    embedding-based retrieval needs careful threshold tuning &mdash;
    the margin between "relevant" and "not relevant" in the distance
    metric can be razor-thin.<br><br>
    <b>See also:</b>
    <a href="/pep">PEP &rarr; Weighted Graph</a> (the graph derived
    from these distances),
    <a href="/lingora">Lingora &rarr; Word as Constellation</a>
    (words as vectors with meaning components).
  </div>
</div>
</div>

<!-- ═══ Knowledge Graph ═══════════════════════════════════════════ -->
<div class="panel" id="kg-tab">
<div class="container">
  <h2>Knowledge Graph &mdash; Entities and Typed Relationships</h2>
  <p class="desc">
    Entities (people, places, concepts) connected by named relationships
    ("born in," "wrote," "part of"). Click any node to highlight its
    neighborhood. This is PEP's weighted graph with typed edges,
    applied to structured knowledge.
  </p>
  <div class="canvas-box">
    <canvas id="kg-canvas" width="960" height="460"></canvas>
  </div>
  <div class="controls">
    <button onclick="kgPick('einstein')">Einstein subgraph</button>
    <button onclick="kgPick('python')">Python ecosystem</button>
    <button onclick="kgPick('music')">Music genre tree</button>
    <button onclick="kgReset()">Reset</button>
  </div>
  <div class="info">
    <b>Knowledge graph vs embedding graph:</b> Both are weighted
    graphs. The difference is how edges are derived. Embedding edges
    come from vector similarity &mdash; cheap, broad, noisy. Knowledge
    edges come from explicit extraction &mdash; expensive, precise,
    sparse. Layering both gives you broad reach (embedding) with
    precise structure (knowledge). Vectora supports both on the
    same node set.<br><br>
    <b>See also:</b>
    <a href="/pep">PEP &rarr; Weighted Graph</a>,
    <a href="/atria">Atria &rarr; Multi-Objective Projection</a>
    (the same multi-typed-edge structure applied to matchmaking).
  </div>
</div>
</div>

<!-- ═══ Anomaly Detection ═════════════════════════════════════════ -->
<div class="panel" id="anomaly-tab">
<div class="container">
  <h2>Anomaly Detection &mdash; The Residual Scorer on Data</h2>
  <p class="desc">
    The predictor models what the data "usually looks like." A new item
    that matches the pattern produces a low residual. An item that
    diverges &mdash; a measurement that is too high, a document about
    a topic nobody has covered, a code change in an unusual file &mdash;
    produces a high residual and gets flagged.
  </p>
  <div class="canvas-box">
    <canvas id="anomaly-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <button onclick="anomalyInject('normal')">Inject normal item</button>
    <button onclick="anomalyInject('anomaly')">Inject anomaly</button>
    <button onclick="anomalyReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      items: <b id="anomaly-count" style="color:var(--accent)">0</b>
      &nbsp; anomalies flagged: <b id="anomaly-flagged" style="color:var(--warn)">0</b>
    </span>
  </div>
  <div class="info">
    <b>What you are watching:</b> A stream of data items. Normal items
    (blue) land within the expected distribution. Anomalies (gold)
    land outside it. The residual bar on the right shows the gap
    between where the predictor expected each item to be and where it
    actually landed. High residuals get flagged automatically.<br><br>
    <b>Why this is not just outlier detection:</b> Classical outlier
    detection uses a fixed model of "normal." Vectora's residual
    scorer is context-sensitive &mdash; the predictor updates as data
    arrives, so what counts as anomalous shifts over time. An item
    that was anomalous yesterday might be normal today because the
    pattern changed. The scorer tracks this automatically.<br><br>
    <b>See also:</b>
    <a href="/pep">PEP &rarr; Predictor + Residual</a>,
    <a href="/atria">Atria &rarr; Residual Heatmap</a>,
    <a href="/axona">Axona &rarr; Prediction vs Reality</a>.
  </div>
</div>
</div>

<!-- ═══ Context-Dependent Retrieval ═══════════════════════════════ -->
<div class="panel" id="context-tab">
<div class="container">
  <h2>Context-Dependent Retrieval &mdash; Same Query, Different Context</h2>
  <p class="desc">
    The same query returns different results depending on what you have
    been looking at recently. A developer searching "merge" while
    reading git docs gets version-control results. The same developer
    searching "merge" while reading about data pipelines gets ETL
    results. Context is a state modulator on the retrieval graph.
  </p>
  <div class="canvas-box">
    <canvas id="context-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <button onclick="contextSet('git')">Context: git / version control</button>
    <button onclick="contextSet('data')">Context: data pipelines / ETL</button>
    <button onclick="contextSet('none')">No context</button>
    <button onclick="contextSearch()">Search: "merge"</button>
  </div>
  <div class="info">
    <b>What you are watching:</b> A fixed document graph. The query
    "merge" has multiple meaning clusters. With no context, both
    clusters light up equally. After setting a context (git or data
    pipelines), recent-context modulation boosts edges near the
    context region and dampens the other. The same query now produces
    a focused result set without the user having to disambiguate.<br><br>
    <b>Why this is useful:</b> Users should not have to specify their
    intent in every query. If they have been reading git docs for the
    last ten minutes, "merge" obviously means "git merge." Making
    them type "git merge" instead of "merge" is making them do work
    the system should do. Context-sensitive retrieval lets short,
    ambiguous queries produce precise results because the context is
    doing half the disambiguation.<br><br>
    <b>See also:</b>
    <a href="/pep">PEP &rarr; State Modulator</a>,
    <a href="/lingora">Lingora &rarr; Ambiguity Resolution</a>
    (the same mechanism applied to word meaning).
  </div>
</div>
</div>

<!-- ═══ Theory ════════════════════════════════════════════════════ -->
<div class="panel" id="theory-tab">
<div class="container">
  <h2>Theory &mdash; The Framing in Full</h2>
  <p class="desc">
    Full text at <code>~/projects/vectora/docs/theory.md</code>.
    Condensed version below.
  </p>
  <div class="info">
    <b>1. The filing-cabinet fallacy.</b> Real retrieval is not "go to
    the folder I already know about." It is "I have a vague question
    and the system figures out which items are relevant."
  </div>
  <div class="info">
    <b>2. Items as nodes in a weighted graph.</b> Documents, records,
    images, code — each is a node with a feature vector. Edges come
    from content similarity, shared metadata, co-occurrence, or
    explicit links.
  </div>
  <div class="info">
    <b>3. Retrieval as spreading activation.</b> Seed at query-matching
    nodes, spread through weighted edges. The expansion surfaces items
    the user would not have found through any keyword.
  </div>
  <div class="info">
    <b>4. Embedding spaces.</b> High-dimensional vectors where distance
    approximates semantic similarity. The graph is computed from these
    distances.
  </div>
  <div class="info">
    <b>5. Knowledge graphs.</b> Entities with typed relationships.
    Precise but expensive. Layering with embeddings gives the best of
    both.
  </div>
  <div class="info">
    <b>6. Anomaly as residual scoring.</b> New items scored against the
    predictor. High residuals are flagged as novel or anomalous.
  </div>
  <div class="info">
    <b>7. Context-dependent retrieval.</b> Recent activity modulates
    edge weights so the same query gives different answers under
    different contexts.
  </div>
  <div class="info">
    <b>8. Vectora as infrastructure.</b> The internal layer the other
    LAVAS siblings consume. Build the retrieval primitive once; let
    every sibling call it.
  </div>
</div>
</div>

<!-- ═══ PEP ↔ Vectora Bridge ════════════════════════════════════ -->
<div class="panel" id="bridge-tab">
<div class="container">
  <h2>PEP &harr; Vectora &mdash; Live Bridge</h2>
  <p class="desc">
    Vectora is part of the LAVAS mesh. Every canvas action posts to PEP.
    Axona, Lingora, and Atria event buffers are mirrored here.
  </p>
  <div style="display:flex;gap:16px;margin-bottom:16px">
    <div class="info" style="flex:1">
      <b>PEP state + mesh</b><br><br>
      <div style="font-family:monospace;font-size:11px;line-height:1.8">
        <div>connected: <span id="bridge-connected" style="color:var(--accent2)">—</span></div>
        <div>LLM: <span id="bridge-llm" style="color:var(--accent)">—</span></div>
        <div>Vectora events: <span id="bridge-vcount" style="color:var(--accent)">—</span></div>
        <div>Axona: <span id="bridge-acount" style="color:var(--accent)">—</span>
          · Lingora: <span id="bridge-lcount" style="color:var(--accent)">—</span>
          · Atria: <span id="bridge-tcount" style="color:var(--accent)">—</span></div>
      </div>
    </div>
    <div class="info" style="flex:1">
      <b>Vectora &rarr; PEP</b><br><br>
      <button onclick="bridgePing()">Send Test Ping</button>
    </div>
  </div>
  <div class="canvas-box" style="padding:16px">
    <div style="font-family:monospace;font-size:11px;color:var(--accent);margin-bottom:8px">
      &gt; Vectora events
    </div>
    <div id="bridge-log" style="font-family:monospace;font-size:11px;line-height:1.7;max-height:300px;overflow-y:auto;color:var(--text)">
      <span style="color:var(--dim)">waiting…</span>
    </div>
  </div>
</div>
</div>

<script>
// ═══════════════════════════════════════════════════════════════════════
// Tab switching + helpers
// ═══════════════════════════════════════════════════════════════════════
function tabPanelIds(tab) { return (tab.dataset.panels || tab.dataset.panel || '').trim().split(/\\s+/).filter(Boolean); }
function findTabForPanel(id) { return Array.from(document.querySelectorAll('.tab')).find(t => tabPanelIds(t).includes(id)); }
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    tab.classList.add('active');
    tabPanelIds(tab).forEach(id => { const el = document.getElementById(id); if (el) el.classList.add('active'); });
    window.scrollTo(0, 0);
  });
});
function themeBg() { return getComputedStyle(document.body).getPropertyValue('--bg').trim() || '#0b0e14'; }
function toggleLight() {
  const isLight = document.body.classList.toggle('light');
  const btn = document.getElementById('light-btn');
  if (btn) btn.textContent = isLight ? 'Dark Mode' : 'Light Mode';
  try { localStorage.setItem('vectora-theme', isLight ? 'light' : 'dark'); } catch (e) {}
}
(function() { try { if (localStorage.getItem('vectora-theme') === 'light') { document.body.classList.add('light'); const b = document.getElementById('light-btn'); if (b) b.textContent = 'Dark Mode'; } } catch(e) {} })();
function downloadVectora() {
  const h = '<!DOCTYPE html>' + document.documentElement.outerHTML;
  const b = new Blob([h], { type: 'text/html' });
  const u = URL.createObjectURL(b);
  const a = document.createElement('a'); a.href = u; a.download = 'vectora-data.html';
  document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(u);
}
function canvasSelect(id) {
  if (!id) return;
  const el = document.getElementById(id);
  if (!el) return;
  let pid = null;
  if (el.classList && el.classList.contains('panel')) pid = el.id;
  else { const p = el.closest ? el.closest('.panel') : null; if (p) pid = p.id; }
  if (pid) { const tab = findTabForPanel(pid); if (tab) tab.click(); }
  setTimeout(() => { el.scrollIntoView({ behavior: 'smooth', block: 'start' }); const s = document.getElementById('canvas-select'); if (s) s.value = ''; }, 60);
}
function buildCanvasDropdown() {
  const select = document.getElementById('canvas-select');
  if (!select) return;
  const skip = ['home-tab', 'theory-tab', 'bridge-tab'];
  document.querySelectorAll('.tab').forEach(tab => {
    const ids = tabPanelIds(tab);
    if (!ids.length || (ids.length === 1 && skip.includes(ids[0]))) return;
    const og = document.createElement('optgroup'); og.label = tab.textContent.trim();
    ids.forEach(id => {
      const p = document.getElementById(id); if (!p) return;
      const h = p.querySelector('h2'); let t = id.replace(/-tab$/, '');
      if (h) { t = h.textContent.trim(); const d = t.indexOf('—'); if (d > 0) t = t.slice(0, d).trim(); }
      const o = document.createElement('option'); o.value = id; o.textContent = t; og.appendChild(o);
    });
    if (og.children.length) select.appendChild(og);
  });
}
setTimeout(buildCanvasDropdown, 80);

// ═══════════════════════════════════════════════════════════════════════
// Bridge
// ═══════════════════════════════════════════════════════════════════════
let bridgeThrottle = {};
function pepSend(type, payload) {
  const now = Date.now(); if (bridgeThrottle[type] && now - bridgeThrottle[type] < 600) return; bridgeThrottle[type] = now;
  try { fetch('/vectora/event', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ type, source: 'vectora', payload: payload || {} }) }).catch(() => {}); } catch (e) {}
}
function bridgePing() { pepSend('ping', { from: 'user', t: Date.now() }); }
function bridgeFmt(t) { return new Date(t * 1000).toTimeString().slice(0, 8); }
function bridgeRender(items) {
  const log = document.getElementById('bridge-log'); if (!log || !items.length) return;
  log.innerHTML = items.slice().reverse().map(e => '<div style="margin-bottom:3px"><span style="color:var(--dim)">' + bridgeFmt(e.t) + '</span> <span style="color:var(--accent)">' + (e.type || '') + '</span></div>').join('');
}
async function bridgePoll() {
  try {
    const [s, e] = await Promise.all([ fetch('/vectora/pep-state'), fetch('/vectora/events?limit=40') ]);
    if (s.ok) {
      const d = await s.json();
      const set = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = v; };
      const lbl = document.getElementById('pep-link-label');
      const dot = document.getElementById('pep-link-dot');
      if (lbl) lbl.textContent = 'PEP: ' + (d.llm || '—') + ' · V' + (d.vectora_events || 0);
      if (dot) dot.style.background = 'var(--accent2)';
      set('bridge-connected', 'yes'); set('bridge-llm', d.llm || '—');
      set('bridge-vcount', d.vectora_events); set('bridge-acount', d.axona_events);
      set('bridge-lcount', d.lingora_events); set('bridge-tcount', d.atria_events);
    }
    if (e.ok) bridgeRender((await e.json()).items || []);
  } catch (err) {
    const lbl = document.getElementById('pep-link-label');
    if (lbl) lbl.textContent = 'PEP: offline';
  }
}
bridgePoll(); setInterval(bridgePoll, 2500);

// ═══════════════════════════════════════════════════════════════════════
// Keyword vs Semantic
// ═══════════════════════════════════════════════════════════════════════
const SEARCH_DATA = {
  jaguar: {
    keyword: ['Jaguar XF review (car)', 'Jaguar habitat map (animal)', 'Fender Jaguar setup guide (guitar)', 'Jacksonville Jaguars roster (sports)', 'Jaguar Wright discography (music)'],
    semantic: { animal: ['Jaguar habitat', 'Big cats of the Americas', 'Endangered species list'], car: ['Jaguar XF review', 'Luxury sedan comparison', 'British automotive brands'], guitar: ['Fender Jaguar setup', 'Short-scale guitars', 'Surf rock gear'] },
  },
  python: {
    keyword: ['Python 3.12 release notes', 'Burmese python habitat', 'Monty Python sketch list', 'Python bootcamp syllabus', 'Reticulated python size record'],
    semantic: { programming: ['Python 3.12 release', 'Type hints guide', 'FastAPI tutorial', 'pip dependency resolver'], animal: ['Burmese python habitat', 'Large constrictor snakes', 'Reptile care guide'], comedy: ['Monty Python sketch list', 'British comedy history', 'Dead parrot origins'] },
  },
  cell: {
    keyword: ['Cell biology textbook', 'Cell phone comparison', 'Prison cell standards', 'Excel cell formatting', 'Fuel cell technology'],
    semantic: { biology: ['Cell biology', 'Mitosis and meiosis', 'Organelle function', 'Stem cell research'], technology: ['Cell phone comparison', 'Battery cell chemistry', 'Fuel cell vehicles'], computing: ['Excel cell formatting', 'Spreadsheet formulas', 'Notebook cell (Jupyter)'] },
  },
};
const keywordCanvas = document.getElementById('keyword-canvas');
const keywordCtx = keywordCanvas.getContext('2d');
let searchActive = null;
function searchPick(k) { searchActive = k; pepSend('search.pick', { key: k }); }
function searchReset() { searchActive = null; }
function drawSearch() {
  const W = 960, H = 440; keywordCtx.fillStyle = themeBg(); keywordCtx.fillRect(0, 0, W, H);
  if (!searchActive) { keywordCtx.fillStyle = '#666'; keywordCtx.font = '11px monospace'; keywordCtx.textAlign = 'center'; keywordCtx.fillText('(pick a query)', W / 2, H / 2); requestAnimationFrame(drawSearch); return; }
  const d = SEARCH_DATA[searchActive];
  // Left: keyword results
  keywordCtx.fillStyle = 'rgba(56,189,248,0.95)'; keywordCtx.font = 'bold 12px monospace'; keywordCtx.textAlign = 'left';
  keywordCtx.fillText('KEYWORD RESULTS for "' + searchActive + '"', 30, 30);
  keywordCtx.fillStyle = '#dce4ed'; keywordCtx.font = '12px monospace';
  d.keyword.forEach((r, i) => keywordCtx.fillText('• ' + r, 40, 60 + i * 24));
  keywordCtx.fillStyle = '#6a7a8a'; keywordCtx.font = '10px monospace';
  keywordCtx.fillText('all contain the string — no disambiguation', 40, 60 + d.keyword.length * 24 + 14);
  // Right: semantic results
  keywordCtx.fillStyle = 'rgba(163,230,53,0.95)'; keywordCtx.font = 'bold 12px monospace';
  keywordCtx.fillText('SEMANTIC RESULTS for "' + searchActive + '"', 500, 30);
  let y = 60;
  const cols = { 0: '56,189,248', 1: '163,230,53', 2: '245,158,11' };
  Object.entries(d.semantic).forEach(([cluster, items], ci) => {
    keywordCtx.fillStyle = 'rgba(' + (cols[ci] || '200,200,200') + ',0.85)'; keywordCtx.font = 'bold 11px monospace';
    keywordCtx.fillText(cluster.toUpperCase(), 510, y); y += 20;
    keywordCtx.fillStyle = '#dce4ed'; keywordCtx.font = '11px monospace';
    items.forEach(r => { keywordCtx.fillText('• ' + r, 520, y); y += 20; });
    y += 10;
  });
  keywordCtx.fillStyle = '#6a7a8a'; keywordCtx.font = '10px monospace';
  keywordCtx.fillText('clustered by meaning — disambiguation is automatic', 510, H - 20);
  requestAnimationFrame(drawSearch);
}
drawSearch();

// ═══════════════════════════════════════════════════════════════════════
// Embedding Space
// ═══════════════════════════════════════════════════════════════════════
const embedCanvas = document.getElementById('embed-canvas');
const embedCtx = embedCanvas.getContext('2d');
let embedPoints = [], embedLabels = true;
function embedGen() {
  embedPoints = [];
  const clusters = [
    { cx: 200, cy: 160, r: 80, col: '56,189,248', label: 'science' },
    { cx: 500, cy: 300, r: 70, col: '163,230,53', label: 'cooking' },
    { cx: 760, cy: 180, r: 90, col: '245,158,11', label: 'sports' },
    { cx: 400, cy: 120, r: 60, col: '168,85,247', label: 'music' },
  ];
  clusters.forEach(c => {
    for (let i = 0; i < 20; i++) {
      const a = Math.random() * Math.PI * 2;
      const r = Math.sqrt(Math.random()) * c.r;
      embedPoints.push({ x: c.cx + Math.cos(a) * r, y: c.cy + Math.sin(a) * r, col: c.col, label: c.label });
    }
  });
}
embedGen();
function embedRegen() { embedGen(); }
function embedToggleLabels() { embedLabels = !embedLabels; }
function drawEmbed() {
  const W = 960, H = 460; embedCtx.fillStyle = themeBg(); embedCtx.fillRect(0, 0, W, H);
  embedPoints.forEach(p => {
    embedCtx.fillStyle = 'rgba(' + p.col + ',0.65)';
    embedCtx.beginPath(); embedCtx.arc(p.x, p.y, 5, 0, Math.PI * 2); embedCtx.fill();
    if (embedLabels) {
      embedCtx.fillStyle = 'rgba(' + p.col + ',0.5)'; embedCtx.font = '9px monospace'; embedCtx.textAlign = 'center';
      embedCtx.fillText(p.label, p.x, p.y + 14);
    }
  });
  embedCtx.fillStyle = '#6a7a8a'; embedCtx.font = '11px monospace'; embedCtx.textAlign = 'left';
  embedCtx.fillText('2D projection of a synthetic 768-dim embedding space · 80 documents · 4 clusters', 30, H - 16);
  requestAnimationFrame(drawEmbed);
}
drawEmbed();

// ═══════════════════════════════════════════════════════════════════════
// Knowledge Graph
// ═══════════════════════════════════════════════════════════════════════
const KG_DATA = {
  einstein: {
    nodes: [ { id: 'einstein', l: 'Einstein', x: 480, y: 230 }, { id: 'ulm', l: 'Ulm', x: 280, y: 130 }, { id: 'relativity', l: 'Relativity', x: 680, y: 130 }, { id: 'photoelectric', l: 'Photoelectric', x: 680, y: 330 }, { id: 'nobel', l: 'Nobel Prize', x: 480, y: 380 }, { id: 'physics', l: 'Physics', x: 280, y: 330 } ],
    edges: [ { a: 'einstein', b: 'ulm', l: 'born in' }, { a: 'einstein', b: 'relativity', l: 'developed' }, { a: 'einstein', b: 'photoelectric', l: 'explained' }, { a: 'einstein', b: 'nobel', l: 'won' }, { a: 'relativity', b: 'physics', l: 'part of' }, { a: 'photoelectric', b: 'physics', l: 'part of' } ],
  },
  python: {
    nodes: [ { id: 'python', l: 'Python', x: 480, y: 230 }, { id: 'fastapi', l: 'FastAPI', x: 280, y: 130 }, { id: 'django', l: 'Django', x: 680, y: 130 }, { id: 'numpy', l: 'NumPy', x: 280, y: 330 }, { id: 'pytorch', l: 'PyTorch', x: 680, y: 330 }, { id: 'pip', l: 'pip', x: 480, y: 380 } ],
    edges: [ { a: 'python', b: 'fastapi', l: 'framework' }, { a: 'python', b: 'django', l: 'framework' }, { a: 'python', b: 'numpy', l: 'library' }, { a: 'python', b: 'pytorch', l: 'library' }, { a: 'python', b: 'pip', l: 'package manager' }, { a: 'numpy', b: 'pytorch', l: 'depends on' } ],
  },
  music: {
    nodes: [ { id: 'music', l: 'Music', x: 480, y: 130 }, { id: 'rock', l: 'Rock', x: 280, y: 230 }, { id: 'jazz', l: 'Jazz', x: 680, y: 230 }, { id: 'blues', l: 'Blues', x: 480, y: 330 }, { id: 'punk', l: 'Punk', x: 180, y: 330 }, { id: 'hiphop', l: 'Hip-Hop', x: 780, y: 330 } ],
    edges: [ { a: 'music', b: 'rock', l: 'genre' }, { a: 'music', b: 'jazz', l: 'genre' }, { a: 'rock', b: 'blues', l: 'evolved from' }, { a: 'jazz', b: 'blues', l: 'evolved from' }, { a: 'rock', b: 'punk', l: 'spawned' }, { a: 'jazz', b: 'hiphop', l: 'influenced' } ],
  },
};
const kgCanvas = document.getElementById('kg-canvas');
const kgCtx = kgCanvas.getContext('2d');
let kgActive = null;
function kgPick(k) { kgActive = k; pepSend('kg.pick', { key: k }); }
function kgReset() { kgActive = null; }
function drawKg() {
  const W = 960, H = 460; kgCtx.fillStyle = themeBg(); kgCtx.fillRect(0, 0, W, H);
  if (!kgActive) { kgCtx.fillStyle = '#666'; kgCtx.font = '11px monospace'; kgCtx.textAlign = 'center'; kgCtx.fillText('(pick a subgraph)', W / 2, H / 2); requestAnimationFrame(drawKg); return; }
  const d = KG_DATA[kgActive];
  const nodeMap = {}; d.nodes.forEach(n => nodeMap[n.id] = n);
  d.edges.forEach(e => {
    const a = nodeMap[e.a], b = nodeMap[e.b];
    kgCtx.strokeStyle = 'rgba(56,189,248,0.5)'; kgCtx.lineWidth = 2;
    kgCtx.beginPath(); kgCtx.moveTo(a.x, a.y); kgCtx.lineTo(b.x, b.y); kgCtx.stroke();
    kgCtx.fillStyle = 'rgba(163,230,53,0.85)'; kgCtx.font = '10px monospace'; kgCtx.textAlign = 'center';
    kgCtx.fillText(e.l, (a.x + b.x) / 2, (a.y + b.y) / 2 - 6);
  });
  d.nodes.forEach(n => {
    kgCtx.fillStyle = 'rgba(56,189,248,0.55)';
    kgCtx.beginPath(); kgCtx.arc(n.x, n.y, 24, 0, Math.PI * 2); kgCtx.fill();
    kgCtx.strokeStyle = 'rgba(56,189,248,0.95)'; kgCtx.lineWidth = 2; kgCtx.stroke();
    kgCtx.fillStyle = '#fff'; kgCtx.font = 'bold 11px monospace'; kgCtx.textAlign = 'center';
    kgCtx.fillText(n.l, n.x, n.y + 4);
  });
  requestAnimationFrame(drawKg);
}
drawKg();

// ═══════════════════════════════════════════════════════════════════════
// Anomaly Detection
// ═══════════════════════════════════════════════════════════════════════
const anomalyCanvas = document.getElementById('anomaly-canvas');
const anomalyCtx = anomalyCanvas.getContext('2d');
const anomalyItems = [];
let anomalyCount = 0, anomalyFlagged = 0;
function anomalyInject(kind) {
  const x = 60 + Math.random() * 840;
  let y, isAnomaly = false;
  if (kind === 'anomaly') {
    y = 60 + Math.random() * 120; isAnomaly = true; anomalyFlagged++;
  } else {
    y = 250 + (Math.random() - 0.5) * 80;
  }
  anomalyItems.push({ x, y, isAnomaly, life: 1 });
  anomalyCount++;
  document.getElementById('anomaly-count').textContent = anomalyCount;
  document.getElementById('anomaly-flagged').textContent = anomalyFlagged;
  pepSend('anomaly.inject', { kind });
}
function anomalyReset() { anomalyItems.length = 0; anomalyCount = 0; anomalyFlagged = 0; document.getElementById('anomaly-count').textContent = '0'; document.getElementById('anomaly-flagged').textContent = '0'; }
function drawAnomaly() {
  const W = 960, H = 440; anomalyCtx.fillStyle = themeBg(); anomalyCtx.fillRect(0, 0, W, H);
  // Expected band
  anomalyCtx.fillStyle = 'rgba(56,189,248,0.08)';
  anomalyCtx.fillRect(60, 210, 840, 80);
  anomalyCtx.strokeStyle = 'rgba(56,189,248,0.35)'; anomalyCtx.setLineDash([4, 4]);
  anomalyCtx.beginPath(); anomalyCtx.moveTo(60, 250); anomalyCtx.lineTo(900, 250); anomalyCtx.stroke();
  anomalyCtx.setLineDash([]);
  anomalyCtx.fillStyle = '#6a7a8a'; anomalyCtx.font = '10px monospace'; anomalyCtx.textAlign = 'left';
  anomalyCtx.fillText('expected range', 64, 206);
  anomalyItems.forEach(p => {
    p.life *= 0.998;
    const col = p.isAnomaly ? '245,158,11' : '56,189,248';
    anomalyCtx.fillStyle = 'rgba(' + col + ',' + (p.life * 0.85).toFixed(3) + ')';
    anomalyCtx.beginPath(); anomalyCtx.arc(p.x, p.y, p.isAnomaly ? 7 : 4, 0, Math.PI * 2); anomalyCtx.fill();
    if (p.isAnomaly) {
      anomalyCtx.strokeStyle = 'rgba(245,158,11,0.9)'; anomalyCtx.lineWidth = 1.5; anomalyCtx.stroke();
    }
  });
  // Residual bar on the right
  if (anomalyItems.length) {
    const last = anomalyItems[anomalyItems.length - 1];
    const resid = Math.abs(last.y - 250) / 200;
    anomalyCtx.fillStyle = '#6a7a8a'; anomalyCtx.font = '10px monospace'; anomalyCtx.textAlign = 'center';
    anomalyCtx.fillText('residual', 930, 160);
    anomalyCtx.fillStyle = 'rgba(245,158,11,0.2)'; anomalyCtx.fillRect(916, 170, 28, 200);
    anomalyCtx.fillStyle = 'rgba(245,158,11,0.85)'; anomalyCtx.fillRect(916, 370 - resid * 200, 28, resid * 200);
  }
  requestAnimationFrame(drawAnomaly);
}
drawAnomaly();

// ═══════════════════════════════════════════════════════════════════════
// Context-Dependent Retrieval
// ═══════════════════════════════════════════════════════════════════════
const CONTEXT_DATA = {
  git: { label: 'git / version control', results: ['git merge --no-ff', 'resolving merge conflicts', 'merge vs rebase', 'pull request merge strategies', 'branch protection rules'] },
  data: { label: 'data pipelines / ETL', results: ['merge join in Spark', 'MERGE INTO (SQL)', 'merging DataFrames in pandas', 'CDC merge patterns', 'data deduplication after merge'] },
  none: { label: '(no context)', results: ['git merge --no-ff', 'merge join in Spark', 'corporate merger news', 'mail merge tutorial', 'merge sort algorithm'] },
};
const contextCanvas = document.getElementById('context-canvas');
const contextCtx = contextCanvas.getContext('2d');
let contextMode = null, contextSearched = false;
function contextSet(k) { contextMode = k; contextSearched = false; pepSend('context.set', { key: k }); }
function contextSearch() { contextSearched = true; pepSend('context.search', { context: contextMode }); }
function drawContext() {
  const W = 960, H = 440; contextCtx.fillStyle = themeBg(); contextCtx.fillRect(0, 0, W, H);
  contextCtx.fillStyle = '#dce4ed'; contextCtx.font = 'bold 18px monospace'; contextCtx.textAlign = 'center';
  contextCtx.fillText('Query: "merge"', W / 2, 50);
  if (contextMode) {
    contextCtx.fillStyle = 'rgba(163,230,53,0.85)'; contextCtx.font = '11px monospace';
    contextCtx.fillText('context: ' + CONTEXT_DATA[contextMode].label, W / 2, 76);
  }
  if (contextSearched && contextMode) {
    const d = CONTEXT_DATA[contextMode];
    contextCtx.fillStyle = 'rgba(56,189,248,0.95)'; contextCtx.font = 'bold 12px monospace'; contextCtx.textAlign = 'left';
    contextCtx.fillText('RESULTS (context-modulated)', 80, 130);
    contextCtx.fillStyle = '#dce4ed'; contextCtx.font = '13px monospace';
    d.results.forEach((r, i) => contextCtx.fillText('• ' + r, 100, 160 + i * 28));
    if (contextMode !== 'none') {
      contextCtx.fillStyle = '#6a7a8a'; contextCtx.font = '11px monospace';
      contextCtx.fillText('context boosted ' + d.label + ' edges; other meanings dampened', 80, 160 + d.results.length * 28 + 20);
    }
  } else if (!contextSearched) {
    contextCtx.fillStyle = '#666'; contextCtx.font = '11px monospace'; contextCtx.textAlign = 'center';
    contextCtx.fillText('set a context, then click Search', W / 2, H / 2);
  }
  requestAnimationFrame(drawContext);
}
drawContext();

</script>
</body>
</html>
"""


@router.get("/vectora", response_class=HTMLResponse)
async def vectora_page() -> str:
    return _PAGE
