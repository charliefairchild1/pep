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
  /* LAVAS switcher + mobile responsive */
  .lavas-switch a { color: var(--accent); text-decoration: none; padding: 2px 4px; border-radius: 3px; }
  .lavas-switch a:hover { background: var(--surface); }
  .lavas-switch .lavas-current { color: var(--text); font-weight: bold; padding: 2px 4px; opacity: 0.7; }
  @media (max-width: 700px) {
    nav { padding: 4px 8px 0 8px; }
    .nav-row { flex-wrap: wrap; gap: 6px; }
    .nav-row-top { padding-bottom: 4px; }
    .brand { font-size: 14px; }
    .tabs { overflow-x: auto; flex-wrap: nowrap; -webkit-overflow-scrolling: touch; max-width: 100%; }
    .tabs::-webkit-scrollbar { height: 3px; }
    .tab { white-space: nowrap; padding: 6px 8px; font-size: 10px; }
    .nav-btn { padding: 4px 8px; font-size: 10px; }
    .container { padding: 12px; max-width: 100%; }
    h2 { font-size: 14px; }
    h3 { font-size: 12px; }
    .canvas-box canvas { width: 100% !important; height: auto !important; max-width: 100%; }
    .info { font-size: 11px; line-height: 1.6; }
    .lavas-switch { gap: 6px; font-size: 10px; }
    #pep-link-badge { display: none; }
  }
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
    <span class="lavas-switch" style="display:flex;gap:8px;align-items:center;font-size:11px;flex-wrap:wrap">
      <a href="/pep">PEP</a>
      <a href="/axona">Axona</a>
      <a href="/lingora">Lingora</a>
      <a href="/atria">Atria</a>
      <span class="lavas-current">Vectora</span>
      <a href="/strata">Strata</a>
    </span>
  </div>
  <div class="nav-row nav-row-bottom">
    <div class="tabs" id="tabs">
      <div class="tab active" data-panel="home-tab">Home</div>
      <div class="tab" data-panels="keyword-tab embed-tab rerank-tab multihop-tab context-tab">Retrieval</div>
      <div class="tab" data-panels="kg-tab anomaly-tab orgopacity-tab">Structure</div>
      <div class="tab" data-panel="rag-tab">Pipeline</div>
      <div class="tab" data-panels="pitch-tab bench-tab">Pitch</div>
      <div class="tab" data-panel="products-tab">Products</div>
      <div class="tab" data-panel="theory-tab">Theory</div>
      <div class="tab" data-panel="whypep-tab">Why PEP</div>
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
      Vectora is the internal infrastructure layer and four LAVAS
      siblings already consume it in production &mdash; <b>Axona</b>'s
      memory retrieval, <b>Atria</b>'s player-pool formation,
      <b>Lingora</b>'s word constellations, and <b>Strata</b>'s
      correlation-graph momentum all delegate neighborhood queries to
      the same Vectora engine via HTTP. Each app has a <b>&quot;Live
      Vectora Retrieval&quot;</b> canvas that calls the real API. See the
      <a href="/vectora/retrieval">Vectora Retrieval product page</a>
      for the full rundown and a live playground.
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

<!-- ═══ Organizational Opacity ═════════════════════════════════════ -->
<div class="panel" id="orgopacity-tab">
<div class="container">
  <h2>Organizational Opacity &mdash; Haze Applied to Institutional Knowledge</h2>
  <p class="desc">
    Every company has a long tail of docs, wikis, and runbooks nobody
    reads anymore but nobody can confidently delete. Apply PEP's haze
    primitive to the corpus: each doc carries opacity + last-access +
    half-life + incoming-references. Below the reuse threshold, a doc is
    safe to archive &mdash; <em>unless</em> it's load-bearing for other
    live content. This canvas runs the full audit on a simulated
    140-doc org corpus; swap the adapter for a real corpus and the same
    code works.
  </p>
  <div class="controls" style="flex-wrap:wrap">
    <label style="display:flex;align-items:center;gap:8px">
      <span>time forward:</span>
      <input type="range" id="oo-time" min="0" max="180" value="0" style="width:140px">
      <span class="stat-val" id="oo-time-val">0 d</span>
    </label>
    <label style="display:flex;align-items:center;gap:8px">
      <span>reuse threshold:</span>
      <input type="range" id="oo-thresh" min="5" max="30" value="12" style="width:100px">
      <span class="stat-val" id="oo-thresh-val">0.12</span>
    </label>
    <button onclick="ooReinforceRandom()">reinforce random 5 docs</button>
    <button onclick="ooReset()">reset corpus</button>
  </div>
  <div class="canvas-box">
    <canvas id="orgopacity-canvas" width="960" height="340"></canvas>
  </div>
  <div style="margin-top:14px;display:grid;grid-template-columns:1fr 1fr;gap:14px">
    <div id="oo-archive" style="background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:14px 16px;min-height:220px">
      <div style="color:#81c784;font-size:11px;letter-spacing:0.12em;margin-bottom:8px">ARCHIVE CANDIDATES &mdash; safe to move to cold storage</div>
      <div style="color:var(--dim);font-size:12px">&mdash;</div>
    </div>
    <div id="oo-stale" style="background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:14px 16px;min-height:220px">
      <div style="color:#f06292;font-size:11px;letter-spacing:0.12em;margin-bottom:8px">LOAD-BEARING STALE &mdash; don't archive, reinforce</div>
      <div style="color:var(--dim);font-size:12px">&mdash;</div>
    </div>
  </div>
  <div class="info">
    <b>What a CKO / platform ops / KM lead gets out of this.</b><br>
    &bull; <b>"What % of your knowledge is below reuse threshold?"</b>
    Answer at top of canvas, updating as you slide time forward.<br>
    &bull; <b>"What should we archive?"</b> The green panel &mdash; ranked
    by lowest opacity, not load-bearing, not regulated.<br>
    &bull; <b>"What's load-bearing but decaying?"</b> The pink panel.
    These are the docs other live content depends on, but nobody's
    reinforcing. This is where the <em>real</em> org risk is &mdash; not
    in what you archive but in what's quietly becoming inaccessible.<br>
    &bull; <b>"What's our decay velocity?"</b> Bottom line of the canvas:
    how many docs/week are crossing the reuse threshold. A high number
    means your corpus is accelerating its turnover; a low number means
    it's crystallized and ready for a sweep.<br><br>
    <b>Why PEP.</b> This is the haze primitive (#5) at institutional
    scale. Same opacity + half-life + reinforce model that
    <code>pep.vectora.Document</code> uses per-retrieval, just applied
    to the corpus as a whole and surfaced as operational signals.
    <code>pep.vectora.org_opacity</code> is the engine module.<br><br>
    <b>See also:</b>
    <a href="#" onclick="canvasSelect('anomaly-tab');return false">Vectora &rarr; Anomaly</a>,
    <a href="#" onclick="canvasSelect('whypep-tab');return false">Why PEP</a>,
    <a href="/axona#haze-tab">Axona &rarr; Memory Haze</a> (same
    primitive, episodic-memory substrate).
  </div>
</div>
</div>

<!-- ═══ RAG Pipeline ═══════════════════════════════════════════════ -->
<div class="panel" id="rag-tab">
<div class="container">
  <h2>RAG Pipeline &mdash; Retrieve, Augment, Generate</h2>
  <p class="desc">
    Retrieval-Augmented Generation: a query → retrieve relevant chunks →
    feed them to a generator with the query. Click "Run query" to step
    through the pipeline. Each stage shows what moves through.
  </p>
  <div class="canvas-box">
    <canvas id="rag-canvas" width="960" height="480"></canvas>
  </div>
  <div class="controls">
    <button onclick="ragRun('climate')">Query: "why is climate change speeding up"</button>
    <button onclick="ragRun('insulin')">Query: "how does insulin resistance develop"</button>
    <button onclick="ragRun('rome')">Query: "what ended the Roman Empire"</button>
    <button onclick="ragReset()">Reset</button>
  </div>
  <div class="info">
    <b>The pipeline in four stages:</b><br><br>
    &bull; <b>Stage 1 &mdash; query embedding.</b> The query is encoded
    into a vector. This is a one-shot call to the embedder and costs
    almost nothing.<br>
    &bull; <b>Stage 2 &mdash; retrieval.</b> The query vector finds its
    nearest neighbors in the document index. Typical k is 5 to 50. The
    quality of this step is where most RAG systems succeed or fail; a
    weak embedder or a badly-chunked corpus kills recall here.<br>
    &bull; <b>Stage 3 &mdash; augmentation.</b> The retrieved chunks
    are packed into the prompt, usually with the query at the bottom.
    Token budget is the hard constraint &mdash; you can only fit so
    many chunks, and you want the best ones first (which is why
    reranking matters; see the Hybrid Reranker canvas).<br>
    &bull; <b>Stage 4 &mdash; generation.</b> The LLM generates an
    answer grounded in the retrieved context. The output quality is
    bounded above by the retrieval quality; generating from bad
    context produces confident nonsense.<br><br>
    <b>Where Vectora fits:</b> Stage 2 is the spreading-activation
    primitive. Vectora replaces top-k vector search with graph-based
    activation spread, which naturally surfaces second-hop results the
    vector index would miss. See the Multi-Hop Retrieval canvas.<br><br>
    <b>See also:</b>
    <a href="/pep">PEP &rarr; Spreading Activation</a>,
    <a href="/vectora">Vectora &rarr; Hybrid Reranker</a>.
  </div>
</div>
</div>

<!-- ═══ Hybrid Reranker ════════════════════════════════════════════ -->
<div class="panel" id="rerank-tab">
<div class="container">
  <h2>Hybrid Reranker &mdash; Keyword + Semantic, Then Rerank</h2>
  <p class="desc">
    Keyword retrieval has perfect precision for exact matches. Semantic
    retrieval has broader recall for related meanings. A hybrid system
    merges both candidate sets and reranks them. Adjust the weights to
    see the ranking change.
  </p>
  <div class="canvas-box">
    <canvas id="rerank-canvas" width="960" height="480"></canvas>
  </div>
  <div class="controls">
    <label style="display:flex;align-items:center;gap:8px">
      <span>keyword weight:</span>
      <input type="range" id="rerank-kw" min="0" max="100" value="40" style="width:120px">
      <span class="stat-val" id="rerank-kw-val">0.40</span>
    </label>
    <label style="display:flex;align-items:center;gap:8px">
      <span>semantic weight:</span>
      <input type="range" id="rerank-sem" min="0" max="100" value="60" style="width:120px">
      <span class="stat-val" id="rerank-sem-val">0.60</span>
    </label>
    <button onclick="rerankRegen()">Regenerate candidates</button>
  </div>
  <div class="info">
    <b>What you are watching:</b> Two candidate lists (keyword on the
    left, semantic on the right) merged into a single ranked list on
    the bottom. Each document's final score is a weighted sum: kw_score
    × kw_weight + sem_score × sem_weight. Adjust the sliders to see
    which documents rise or fall.<br><br>
    <b>Why both:</b> Pure keyword misses semantic neighbors ("car" does
    not match "automobile"). Pure semantic misses exact-string queries
    ("error code E47" should return documents mentioning E47, not
    everything vaguely about errors). Hybrid retrieval catches both
    failure modes. Production systems (ColBERT, SPLADE, dense+sparse
    fusion) almost universally use some variant of this pattern.<br><br>
    <b>The reranker vs the retriever:</b> Retrieval casts a wide net
    (get 50-100 candidates fast). Reranking is a more expensive scoring
    pass on a smaller set (top 20) that can use more accurate but
    slower models. The canvas simplifies this to a weighted linear
    score, but the same structure holds with cross-encoders or LLM-based
    rerankers.
  </div>
</div>
</div>

<!-- ═══ Multi-Hop Retrieval ════════════════════════════════════════ -->
<div class="panel" id="multihop-tab">
<div class="container">
  <h2>Multi-Hop Retrieval &mdash; The Second-Hop Advantage</h2>
  <p class="desc">
    A query directly retrieves its nearest neighbors (first hop). Those
    neighbors have their own neighbors (second hop). Documents at the
    second hop are often the most useful &mdash; they answer the
    question the user did not know to ask. Click through the hops to
    see what vector search misses.
  </p>
  <div class="canvas-box">
    <canvas id="multihop-canvas" width="960" height="480"></canvas>
  </div>
  <div class="controls">
    <button onclick="multihopStep(0)">Query only</button>
    <button onclick="multihopStep(1)">+ first hop (vector top-k)</button>
    <button onclick="multihopStep(2)">+ second hop (graph spread)</button>
    <button onclick="multihopStep(3)">+ third hop</button>
    <button onclick="multihopReset()">Reset</button>
  </div>
  <div class="info">
    <b>What you are watching:</b> A document graph where edges come
    from embedding similarity. The query lights up the closest documents
    (first hop). Those documents have their own neighbors (second hop).
    A vanilla vector-search retriever stops at first hop and returns
    those top-k documents. Graph-based retrieval keeps going &mdash;
    often the second-hop items are the most valuable, because they
    share a conceptual link with the first hop that the raw query
    vector never encoded.<br><br>
    <b>Concrete example:</b> Query "caching strategies for a monolith."
    First hop: documents about caching. Second hop: documents about
    memory pressure, about database query patterns, about when to
    split a monolith. The user did not ask about those, but they are
    the most useful results because they reframe the problem.<br><br>
    <b>The tradeoff:</b> More hops means bigger candidate sets, which
    means more ranking work and more noise. Decay controls how far the
    activation travels before it fades out &mdash; same decay parameter
    as PEP's core spreading activation.<br><br>
    <b>See also:</b>
    <a href="/pep">PEP &rarr; Spreading Activation</a>,
    <a href="/atria">Atria &rarr; Pool Spreading</a>,
    <a href="/axona">Axona &rarr; Attention Spotlight</a>.
  </div>
</div>
</div>

<!-- ═══ Pitch ══════════════════════════════════════════════════════ -->
<div class="panel" id="pitch-tab">
<div class="container">
  <h2>The Pitch &mdash; Why Build Vectora Instead of Buying a Vector DB</h2>
  <p class="desc">
    Vectora is infrastructure. The question is not "vector DB yes/no"
    &mdash; it is "which retrieval layer?" This page makes the case
    for the graph-based, context-aware, residual-scoring approach over
    the default top-k-vector approach.
  </p>

  <div class="info" style="border-left: 3px solid var(--accent)">
    <b style="font-size:14px;color:var(--accent)">The Default Stack</b><br><br>
    A modern RAG system usually looks like this: an embedder (OpenAI
    ada-002, Cohere embed, Voyage, or a local model) generates vectors.
    A vector DB (Pinecone, Weaviate, Qdrant, pgvector) stores them. At
    query time: embed the query, do top-k nearest neighbors, feed
    results to an LLM. Most teams ship this, hit plateaus at 60-70%
    retrieval accuracy on their own eval set, and start bolting on
    reranking and query rewriting.
  </div>

  <div class="info" style="border-left: 3px solid var(--accent2)">
    <b style="font-size:14px;color:var(--accent2)">What Breaks</b><br><br>
    &bull; <b>Top-k misses second-hop context.</b> The item that would
    have answered the question was two graph hops away; top-k only saw
    one. Users report "the answer is obvious, why didn't it find that?"<br>
    &bull; <b>No context-awareness.</b> The same query returns the same
    results regardless of what the user was just looking at. Users
    rephrase queries to carry context the retriever should have
    inferred.<br>
    &bull; <b>Novelty has no home.</b> New documents that break existing
    patterns are treated the same as documents that confirm them. No
    anomaly surfacing.<br>
    &bull; <b>Reranking is a band-aid.</b> Reranking improves precision
    but cannot rescue recall. If the item was not in the top-k, no
    rerank will find it.
  </div>

  <div class="info" style="border-left: 3px solid var(--warn)">
    <b style="font-size:14px;color:var(--warn)">What Vectora Adds</b><br><br>
    &bull; <b>Graph-based spreading activation</b> for retrieval.
    Second-hop items surface automatically. The Multi-Hop canvas
    demonstrates the mechanism concretely.<br>
    &bull; <b>Hybrid keyword + semantic + knowledge-graph edges.</b>
    Same node set, multiple edge types, activation flows through all
    of them. Precision from the structured side, recall from the
    statistical side.<br>
    &bull; <b>Context as a state modulator.</b> Recent activity boosts
    edges in the relevant region and dampens others. The Context-
    Dependent Retrieval canvas shows this.<br>
    &bull; <b>Residual scoring for novelty.</b> New items that break the
    existing pattern get flagged automatically. Useful for change
    detection, research, and anomaly-aware retrieval.<br>
    &bull; <b>Same primitive as every other LAVAS app.</b> If your team
    builds on PEP, Vectora gives you retrieval for free &mdash; it is
    the same engine that drives Axona's memory, Atria's matchmaking,
    and Strata's correlation graph.
  </div>

  <div class="info" style="border-left: 3px solid var(--accent)">
    <b style="font-size:14px;color:var(--accent)">Integration Path</b><br><br>
    Vectora is <b>not</b> a replacement for Pinecone or pgvector. It is
    a retrieval layer that sits on top of them. The vector DB stores
    the embeddings; Vectora layers graph edges, knowledge-graph edges,
    context modulation, and residual scoring on top. You keep your
    existing infrastructure and gain the spreading-activation, multi-hop,
    context-aware layer above it.<br><br>
    <b>Phase 1:</b> Shadow queries. Run Vectora alongside existing
    retrieval. Measure recall on your eval set with and without the
    graph expansion.<br>
    <b>Phase 2:</b> A/B test. Route a percentage of queries through
    Vectora's retrieval. Measure answer quality (user thumbs-up rate,
    time-to-answer).<br>
    <b>Phase 3:</b> Full rollout. Vectora is the retrieval API; the
    vector DB is storage underneath.
  </div>
</div>
</div>

<!-- ═══ Recall Benchmark ════════════════════════════════════════════ -->
<div class="panel" id="bench-tab">
<div class="container">
  <h2>Recall Benchmark &mdash; Top-K vs Vectora on a Synthetic Eval Set</h2>
  <p class="desc">
    Five metrics on 500 synthetic queries. Top-k vector search (baseline,
    purple) vs Vectora (graph-based, lime). The pattern is consistent:
    Vectora wins on recall and multi-hop relevance; both are comparable
    on precision; Vectora pays a small latency tax for the extra
    expansion.
  </p>
  <div class="canvas-box">
    <canvas id="bench-canvas" width="960" height="480"></canvas>
  </div>
  <div class="controls">
    <button onclick="benchRegen()">Regenerate eval set</button>
  </div>
  <div class="info">
    <b>The metrics:</b><br>
    &bull; <b>Recall@10</b> &mdash; fraction of relevant documents in
    the top-10 results. Higher is better.<br>
    &bull; <b>Multi-hop relevance</b> &mdash; fraction of queries where
    the best answer was a second-hop item. Shows the graph-expansion
    advantage directly.<br>
    &bull; <b>Precision@5</b> &mdash; fraction of top-5 that are actually
    relevant. Higher is better. Vectora and top-k tie here because
    hybrid ranking pushes quality up on both sides.<br>
    &bull; <b>Context-aware uplift</b> &mdash; rate at which
    context-modulated retrieval beats fixed retrieval. Top-k cannot
    even measure this because it does not use context.<br>
    &bull; <b>Latency (index)</b> &mdash; normalized to 1.0 for top-k.
    Vectora's graph walk adds a small constant per query. Tunable via
    the hop depth.
  </div>
</div>
</div>

<!-- ═══ Products ═══════════════════════════════════════════════════ -->
<div class="panel" id="products-tab">
<div class="container">
  <h2>Products &mdash; Vectora's Retrieval Surface</h2>
  <p class="desc">
    Vectora ships as a layered retrieval system rather than a single
    product. Four products carved out of the same engine, each
    addressing a distinct buyer and use case. All sit on top of an
    existing vector DB (Pinecone, Weaviate, Qdrant, pgvector) rather
    than replacing it.
  </p>

  <a href="/vectora/retrieval" style="display:block;background:var(--surface);border:1px solid var(--border);border-left:3px solid #38bdf8;border-radius:6px;padding:16px 20px;margin-bottom:12px;text-decoration:none;color:inherit;transition:border-color 0.15s" onmouseover="this.style.borderColor='#38bdf8'" onmouseout="this.style.borderColor='var(--border)';this.style.borderLeftColor='#38bdf8'">
    <div style="display:flex;justify-content:space-between;align-items:start;gap:10px;margin-bottom:6px">
      <div style="font-size:14px;font-weight:bold;color:#38bdf8">Vectora Retrieval &rarr;</div>
      <span style="font-size:9px;color:#38bdf8;background:rgba(56,189,248,0.15);padding:2px 8px;border-radius:10px;white-space:nowrap">CORE PRODUCT · BUILT</span>
    </div>
    <div style="font-size:11px;color:var(--text);line-height:1.6;margin-bottom:6px">
      Drop-in retrieval API that wraps an existing vector DB. Replaces
      top-k nearest neighbors with graph-based spreading activation,
      surfacing second-hop results that vector search misses. Hybrid
      keyword + semantic + knowledge-graph edges merged and re-ranked.
    </div>
    <div style="font-size:10px;color:var(--dim);line-height:1.5">
      <b style="color:var(--text)">Buyers:</b> RAG-pipeline teams,
      enterprise search, knowledge-management products ·
      <b style="color:var(--text)">Differentiator:</b> the second-hop
      result that answers the question the user could not have asked ·
      <b style="color:var(--text)">Integration:</b> sits on top of
      Pinecone/Weaviate/pgvector; doesn't replace storage.
    </div>
  </a>

  <a href="/vectora/context" style="display:block;background:var(--surface);border:1px solid var(--border);border-left:3px solid #a3e635;border-radius:6px;padding:16px 20px;margin-bottom:12px;text-decoration:none;color:inherit;transition:border-color 0.15s" onmouseover="this.style.borderColor='#a3e635'" onmouseout="this.style.borderColor='var(--border)';this.style.borderLeftColor='#a3e635'">
    <div style="display:flex;justify-content:space-between;align-items:start;gap:10px;margin-bottom:6px">
      <div style="font-size:14px;font-weight:bold;color:#a3e635">Vectora Context &rarr;</div>
      <span style="font-size:9px;color:#a3e635;background:rgba(163,230,53,0.15);padding:2px 8px;border-radius:10px;white-space:nowrap">SDK · CONTEXT-AWARE</span>
    </div>
    <div style="font-size:11px;color:var(--text);line-height:1.6;margin-bottom:6px">
      Context-aware personalization layer for LLM apps. Recent user
      activity becomes a state modulator on the retrieval graph;
      identical queries return different results depending on what the
      user was just looking at. Eliminates the "rephrase to add
      context" tax users currently pay.
    </div>
    <div style="font-size:10px;color:var(--dim);line-height:1.5">
      <b style="color:var(--text)">Buyers:</b> consumer LLM products
      (chat assistants, search), agent platforms, IDE assistants ·
      <b style="color:var(--text)">Comparable:</b> Cursor's project-
      context retrieval, but generalized and pluggable ·
      <b style="color:var(--text)">Differentiator:</b> context as a
      first-class state modulator, not a prompt-stuffing hack.
    </div>
  </a>

  <a href="/vectora/watch" style="display:block;background:var(--surface);border:1px solid var(--border);border-left:3px solid #fbbf24;border-radius:6px;padding:16px 20px;margin-bottom:12px;text-decoration:none;color:inherit;transition:border-color 0.15s" onmouseover="this.style.borderColor='#fbbf24'" onmouseout="this.style.borderColor='var(--border)';this.style.borderLeftColor='#fbbf24'">
    <div style="display:flex;justify-content:space-between;align-items:start;gap:10px;margin-bottom:6px">
      <div style="font-size:14px;font-weight:bold;color:#fbbf24">Vectora Watch &rarr;</div>
      <span style="font-size:9px;color:#fbbf24;background:rgba(251,191,36,0.15);padding:2px 8px;border-radius:10px;white-space:nowrap">ANOMALY · NOVELTY · BUILT</span>
    </div>
    <div style="font-size:11px;color:var(--text);line-height:1.6;margin-bottom:6px">
      Anomaly and novelty surfacing for streaming data. Residual
      scoring on incoming items against the existing pattern; flags
      items that diverge as either anomalies (alerting) or genuine
      novelty (research / discovery). Context-sensitive: what is
      anomalous shifts as the data shifts.
    </div>
    <div style="font-size:10px;color:var(--dim);line-height:1.5">
      <b style="color:var(--text)">Buyers:</b> security/observability
      teams, research orgs scanning literature, content-moderation
      teams, change-detection use cases ·
      <b style="color:var(--text)">Differentiator:</b> context-sensitive
      threshold instead of fixed-rule outlier detection ·
      <b style="color:var(--text)">Same primitive:</b> Strata's
      Unusual Move Scanner is this product applied to equities.
    </div>
  </a>

  <a href="/vectora/graph" style="display:block;background:var(--surface);border:1px solid var(--border);border-left:3px solid #c084fc;border-radius:6px;padding:16px 20px;margin-bottom:12px;text-decoration:none;color:inherit;transition:border-color 0.15s" onmouseover="this.style.borderColor='#c084fc'" onmouseout="this.style.borderColor='var(--border)';this.style.borderLeftColor='#c084fc'">
    <div style="display:flex;justify-content:space-between;align-items:start;gap:10px;margin-bottom:6px">
      <div style="font-size:14px;font-weight:bold;color:#c084fc">Vectora Graph &rarr;</div>
      <span style="font-size:9px;color:#c084fc;background:rgba(192,132,252,0.15);padding:2px 8px;border-radius:10px;white-space:nowrap">KG BUILDER · BUILT</span>
    </div>
    <div style="font-size:11px;color:var(--text);line-height:1.6;margin-bottom:6px">
      Hybrid knowledge-graph builder. Layers explicit entity-relation
      structure on top of embedding-derived similarity edges. Same
      node set, two edge types: precise structure from extraction,
      broad coverage from embeddings. The Knowledge Graph canvas is
      the prototype.
    </div>
    <div style="font-size:10px;color:var(--dim);line-height:1.5">
      <b style="color:var(--text)">Buyers:</b> enterprises with
      structured + unstructured data overlap (legal, healthcare,
      research) ·
      <b style="color:var(--text)">Comparable:</b> Neo4j + LlamaIndex
      separately; Vectora unifies them ·
      <b style="color:var(--text)">Differentiator:</b> single graph,
      typed edges, queryable by either path simultaneously.
    </div>
  </a>

  <h3 style="font-size:13px;color:var(--accent2);margin:24px 0 8px">Why one engine, four products</h3>
  <div class="info">
    All four sit on the same Vectora primitives: nodes (documents,
    entities, items), typed edges (semantic similarity, knowledge
    relations, co-occurrence, context), spreading activation
    (retrieval), residual scoring (novelty/anomaly), state modulation
    (context). Each product surfaces a different combination of those
    primitives. The Retrieval API is the foundation; the others are
    specializations layered on top. Building Vectora Retrieval first
    builds the substrate for all the others.
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

<!-- ═══ Why PEP ═════════════════════════════════════════════════ -->
<div class="panel" id="whypep-tab">
<div class="container">
  <h2>Why PEP &mdash; How the Engine Applies to Retrieval</h2>
  <p class="desc">
    Vectora is not a stand-alone idea. It is PEP's five primitives
    applied to data organization and retrieval. Vectora is also the
    engine the other LAVAS siblings dogfood &mdash; every Axona,
    Lingora, Atria, and Strata retrieval call ultimately lands here.
    Here is the mapping.
  </p>

  <div class="info">
    <b>1. Weighted graph &mdash; the substrate.</b><br>
    Documents (or chunks) are nodes. Embedding similarity, keyword
    overlap, knowledge-graph relations, citation links, authorship, and
    metadata are typed edges. The knowledge base <em>is</em> the graph.
    Vectora's dogfood layer is what exposes this graph over HTTP so
    every sibling app can treat its own domain-specific corpus as a
    PEP graph without reimplementing the primitive.
  </div>

  <div class="info">
    <b>2. Spreading activation &mdash; the search primitive.</b><br>
    Retrieval is spreading activation from a query seed through typed
    edges with decay. BM25, embedding search, and knowledge-graph walks
    are all shapes of this same primitive; multi-hop retrieval is the
    primitive running to a larger budget. The reranker is activation
    concentrating after the first wave. "Hybrid search" is not a
    separate algorithm; it's spreading activation over multiple edge
    types simultaneously with a single budget.
  </div>

  <div class="info">
    <b>3. Predictor + residual scorer &mdash; the learning signal.</b><br>
    Vectora Watch is the predictor-plus-residual applied to a corpus.
    The predictor forecasts "expected content for this context";
    residuals flag documents that deviate. Anomaly surfacing, drift
    detection, and unusual-content alerts are residual scoring at
    corpus scale. The same primitive that drives Strata's
    unusual-move detector drives Vectora's unusual-document detector.
  </div>

  <div class="info">
    <b>4. State modulator &mdash; runtime gain control.</b><br>
    Session context and user intent rescale retrieval. Same query,
    different conversation history, different documents surface.
    Recency weights, relevance priors, per-user affinity, and
    domain-mode toggles are all runtime modulators on the same
    underlying graph. Vectora Context is this primitive exposed as a
    product &mdash; it's the session-modulator for retrieval.
  </div>

  <div class="info">
    <b>5. Opacity + haze &mdash; reclaimable capacity.</b><br>
    Every document has opacity in [0, 1]. Reinforced retrievals push
    opacity up; unretrieved documents decay. Below the reuse threshold
    a document becomes eligible for eviction. Finite index,
    reclaimable slots &mdash; the only way a knowledge base can grow
    forever without retrieval cost growing with it. This is why
    <code>pep.vectora.Document</code> carries opacity, encoded_at,
    half_life_seconds, reinforce(), and is_reusable() as
    first-class fields.
  </div>

  <div class="info" style="border-left:3px solid #38bdf8">
    <b>The pattern.</b> Retrieval is not its own thing. It is what
    happens when the five primitives run on a substrate of
    document-nodes with typed edges. Vectora is the cleanest
    expression of PEP because it sits at the base of the stack:
    every sibling's domain problem (cognition, language, matching,
    markets) reduces, at some step, to "find the relevant nodes in
    the graph." That step is Vectora. Which means PEP's engine
    primitives are not an abstraction layered over retrieval &mdash;
    retrieval is one of their direct specializations.
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
// ═══════════════════════════════════════════════════════════════════════
// RAG Pipeline
// ═══════════════════════════════════════════════════════════════════════
const RAG_DATA = {
  climate: {
    query: 'why is climate change speeding up',
    chunks: [
      'Ice-albedo feedback: melting ice reduces reflectivity, amplifying warming.',
      'Permafrost thaw releases methane, a potent greenhouse gas.',
      'Ocean heat capacity is saturating; heat now spills into the atmosphere.',
      'Aerosol cooling (dimming) has weakened as air quality has improved.',
    ],
    answer: 'Climate change is accelerating because of compounding feedbacks: ice-albedo, permafrost methane release, ocean heat saturation, and reduced aerosol cooling. Each stacks on the others.',
  },
  insulin: {
    query: 'how does insulin resistance develop',
    chunks: [
      'Chronic caloric surplus expands adipose tissue beyond its buffering capacity.',
      'Ectopic fat deposits in liver and muscle interfere with insulin signaling.',
      'Inflammation from visceral fat impairs insulin receptor function.',
      'Mitochondrial dysfunction reduces oxidative capacity in muscle.',
    ],
    answer: 'Insulin resistance develops when chronic overfeeding overwhelms adipose buffering, deposits ectopic fat, triggers inflammation, and impairs mitochondrial function. Each step makes insulin less effective.',
  },
  rome: {
    query: 'what ended the Roman Empire',
    chunks: [
      'Economic decline: currency debasement, inflation, and tax base erosion.',
      'Military overextension across hostile frontiers.',
      'Migration pressure from Germanic and Hunnic peoples.',
      'Administrative split into Eastern and Western empires in 285 CE.',
    ],
    answer: 'No single cause. Economic decline, military overextension, migration pressure, and administrative fragmentation compounded over centuries. The Western empire fell in 476 CE; the Eastern lasted until 1453.',
  },
};
const ragCanvas = document.getElementById('rag-canvas');
const ragCtx = ragCanvas.getContext('2d');
let ragActive = null, ragStage = 0, ragTimer = 0;
function ragRun(k) { ragActive = k; ragStage = 0; ragTimer = 0; pepSend('rag.run', { query: k }); }
function ragReset() { ragActive = null; ragStage = 0; }
function drawRag() {
  const W = 960, H = 480; ragCtx.fillStyle = themeBg(); ragCtx.fillRect(0, 0, W, H);
  if (!ragActive) { ragCtx.fillStyle = '#666'; ragCtx.font = '11px monospace'; ragCtx.textAlign = 'center'; ragCtx.fillText('(pick a query)', W / 2, H / 2); requestAnimationFrame(drawRag); return; }
  ragTimer++;
  if (ragTimer > 60 && ragStage < 4) { ragStage++; ragTimer = 0; }
  const d = RAG_DATA[ragActive];
  const stages = ['1. EMBED QUERY', '2. RETRIEVE', '3. AUGMENT PROMPT', '4. GENERATE'];
  // Stage boxes
  stages.forEach((s, i) => {
    const x = 40 + i * 228, y = 40, w = 210, h = 50;
    const active = i < ragStage;
    ragCtx.fillStyle = active ? 'rgba(56,189,248,0.25)' : 'rgba(100,100,110,0.15)';
    ragCtx.fillRect(x, y, w, h);
    ragCtx.strokeStyle = active ? 'rgba(56,189,248,0.9)' : 'rgba(100,100,110,0.4)';
    ragCtx.lineWidth = active ? 2 : 1;
    ragCtx.strokeRect(x, y, w, h);
    ragCtx.fillStyle = active ? '#fff' : '#6a7a8a'; ragCtx.font = 'bold 11px monospace'; ragCtx.textAlign = 'center';
    ragCtx.fillText(s, x + w / 2, y + 20);
    ragCtx.font = '10px monospace';
    if (i < 3 && i < stages.length - 1) {
      ragCtx.fillStyle = active ? 'rgba(56,189,248,0.8)' : 'rgba(100,100,110,0.3)';
      ragCtx.beginPath(); ragCtx.moveTo(x + w + 2, y + h / 2); ragCtx.lineTo(x + w + 14, y + h / 2);
      ragCtx.stroke();
    }
  });
  // Query
  if (ragStage >= 1) {
    ragCtx.fillStyle = 'rgba(163,230,53,0.9)'; ragCtx.font = 'bold 12px monospace'; ragCtx.textAlign = 'left';
    ragCtx.fillText('query: "' + d.query + '"', 40, 130);
  }
  // Retrieved chunks
  if (ragStage >= 2) {
    ragCtx.fillStyle = 'rgba(56,189,248,0.9)'; ragCtx.font = 'bold 11px monospace';
    ragCtx.fillText('retrieved chunks (top-k from graph-expanded retrieval):', 40, 160);
    d.chunks.forEach((c, i) => {
      ragCtx.fillStyle = '#dce4ed'; ragCtx.font = '11px monospace';
      ragCtx.fillText('• ' + c, 60, 184 + i * 22);
    });
  }
  // Generated answer
  if (ragStage >= 4) {
    ragCtx.fillStyle = 'rgba(245,158,11,0.9)'; ragCtx.font = 'bold 11px monospace';
    ragCtx.fillText('generated answer (grounded in retrieved context):', 40, 310);
    ragCtx.fillStyle = '#e0dce8'; ragCtx.font = '11px monospace';
    const words = d.answer.split(' '); let wx = 60, wy = 334;
    words.forEach(w => { const m = ragCtx.measureText(w + ' '); if (wx + m.width > W - 30) { wx = 60; wy += 18; } ragCtx.fillText(w + ' ', wx, wy); wx += m.width; });
  }
  requestAnimationFrame(drawRag);
}
drawRag();

// ═══════════════════════════════════════════════════════════════════════
// Hybrid Reranker
// ═══════════════════════════════════════════════════════════════════════
const RERANK_DOCS = [
  { title: 'Merging strategies in distributed systems', kw: 0.95, sem: 0.85 },
  { title: 'Git merge vs rebase: a practical guide', kw: 0.90, sem: 0.60 },
  { title: 'Database MERGE INTO syntax reference', kw: 0.75, sem: 0.50 },
  { title: 'How pandas.merge joins DataFrames', kw: 0.65, sem: 0.78 },
  { title: 'Three-way merge algorithm explained', kw: 0.55, sem: 0.82 },
  { title: 'Conflict resolution in collaborative editors', kw: 0.30, sem: 0.75 },
  { title: 'Consensus protocols and quorum merging', kw: 0.25, sem: 0.65 },
  { title: 'Merging sorted arrays efficiently', kw: 0.80, sem: 0.40 },
];
const rerankCanvas = document.getElementById('rerank-canvas');
const rerankCtx = rerankCanvas.getContext('2d');
['rerank-kw', 'rerank-sem'].forEach(id => {
  document.getElementById(id).addEventListener('input', (e) => {
    document.getElementById(id + '-val').textContent = (parseInt(e.target.value) / 100).toFixed(2);
  });
});
function rerankRegen() {
  RERANK_DOCS.forEach(d => { d.kw = Math.max(0, Math.min(1, d.kw + (Math.random() - 0.5) * 0.3)); d.sem = Math.max(0, Math.min(1, d.sem + (Math.random() - 0.5) * 0.3)); });
  pepSend('rerank.regen', {});
}
function drawRerank() {
  const W = 960, H = 480; rerankCtx.fillStyle = themeBg(); rerankCtx.fillRect(0, 0, W, H);
  const kw = parseInt(document.getElementById('rerank-kw').value) / 100;
  const sem = parseInt(document.getElementById('rerank-sem').value) / 100;
  const totalW = kw + sem;
  const ranked = RERANK_DOCS.map(d => ({ ...d, score: totalW > 0 ? (d.kw * kw + d.sem * sem) / totalW : 0 }))
    .sort((a, b) => b.score - a.score);
  // Two columns
  rerankCtx.fillStyle = 'rgba(56,189,248,0.95)'; rerankCtx.font = 'bold 12px monospace'; rerankCtx.textAlign = 'left';
  rerankCtx.fillText('KEYWORD (by kw score)', 40, 30);
  rerankCtx.fillStyle = 'rgba(163,230,53,0.95)';
  rerankCtx.fillText('SEMANTIC (by sem score)', 340, 30);
  rerankCtx.fillStyle = 'rgba(245,158,11,0.95)';
  rerankCtx.fillText('MERGED & RERANKED (by weighted sum)', 640, 30);
  const kwSorted = [...RERANK_DOCS].sort((a, b) => b.kw - a.kw);
  const semSorted = [...RERANK_DOCS].sort((a, b) => b.sem - a.sem);
  kwSorted.forEach((d, i) => {
    rerankCtx.fillStyle = '#dce4ed'; rerankCtx.font = '10px monospace';
    rerankCtx.fillText((i + 1) + '. ' + d.title.slice(0, 32), 40, 60 + i * 22);
    rerankCtx.fillStyle = 'rgba(56,189,248,0.7)';
    rerankCtx.fillText(d.kw.toFixed(2), 290, 60 + i * 22);
  });
  semSorted.forEach((d, i) => {
    rerankCtx.fillStyle = '#dce4ed'; rerankCtx.font = '10px monospace';
    rerankCtx.fillText((i + 1) + '. ' + d.title.slice(0, 32), 340, 60 + i * 22);
    rerankCtx.fillStyle = 'rgba(163,230,53,0.7)';
    rerankCtx.fillText(d.sem.toFixed(2), 590, 60 + i * 22);
  });
  ranked.forEach((d, i) => {
    rerankCtx.fillStyle = '#fff'; rerankCtx.font = 'bold 10px monospace';
    rerankCtx.fillText((i + 1) + '. ' + d.title.slice(0, 32), 640, 60 + i * 22);
    rerankCtx.fillStyle = 'rgba(245,158,11,0.85)';
    rerankCtx.fillText(d.score.toFixed(2), 900, 60 + i * 22);
  });
  requestAnimationFrame(drawRerank);
}
drawRerank();

// ═══════════════════════════════════════════════════════════════════════
// Multi-Hop Retrieval
// ═══════════════════════════════════════════════════════════════════════
const multihopCanvas = document.getElementById('multihop-canvas');
const multihopCtx = multihopCanvas.getContext('2d');
const MULTIHOP_NODES = [];
const MULTIHOP_EDGES = [];
(function multihopInit() {
  const center = { x: 480, y: 240, kind: 'query', label: 'QUERY' };
  MULTIHOP_NODES.push(center);
  // First hop — 5 nodes close
  const firstCount = 5;
  for (let i = 0; i < firstCount; i++) {
    const a = (i / firstCount) * Math.PI * 2;
    const n = { x: center.x + Math.cos(a) * 110, y: center.y + Math.sin(a) * 90, kind: 'hop1', label: 'H1-' + i };
    MULTIHOP_NODES.push(n);
    MULTIHOP_EDGES.push({ a: 0, b: MULTIHOP_NODES.length - 1, kind: 'hop1' });
  }
  // Second hop — 10 nodes further out
  for (let i = 1; i <= firstCount; i++) {
    for (let j = 0; j < 2; j++) {
      const parent = MULTIHOP_NODES[i];
      const a = Math.atan2(parent.y - center.y, parent.x - center.x) + (j - 0.5) * 0.8;
      const n = { x: parent.x + Math.cos(a) * 110, y: parent.y + Math.sin(a) * 90, kind: 'hop2', label: 'H2-' + i + '.' + j };
      MULTIHOP_NODES.push(n);
      MULTIHOP_EDGES.push({ a: i, b: MULTIHOP_NODES.length - 1, kind: 'hop2' });
    }
  }
  // Third hop — a few sparser
  for (let i = 6; i < 16; i += 2) {
    const parent = MULTIHOP_NODES[i];
    const a = Math.atan2(parent.y - center.y, parent.x - center.x);
    const n = { x: parent.x + Math.cos(a) * 90, y: parent.y + Math.sin(a) * 70, kind: 'hop3', label: 'H3' };
    MULTIHOP_NODES.push(n);
    MULTIHOP_EDGES.push({ a: i, b: MULTIHOP_NODES.length - 1, kind: 'hop3' });
  }
})();
let multihopLevel = 0;
function multihopStep(n) { multihopLevel = n; pepSend('multihop.step', { level: n }); }
function multihopReset() { multihopLevel = 0; }
function drawMultihop() {
  const W = 960, H = 480; multihopCtx.fillStyle = themeBg(); multihopCtx.fillRect(0, 0, W, H);
  const showHop = (k) => (k === 'query') || (k === 'hop1' && multihopLevel >= 1) || (k === 'hop2' && multihopLevel >= 2) || (k === 'hop3' && multihopLevel >= 3);
  MULTIHOP_EDGES.forEach(e => {
    if (!(showHop(MULTIHOP_NODES[e.a].kind) && showHop(MULTIHOP_NODES[e.b].kind))) return;
    const a = MULTIHOP_NODES[e.a], b = MULTIHOP_NODES[e.b];
    const col = e.kind === 'hop1' ? '56,189,248' : e.kind === 'hop2' ? '163,230,53' : '245,158,11';
    multihopCtx.strokeStyle = 'rgba(' + col + ',0.5)'; multihopCtx.lineWidth = 1.5;
    multihopCtx.beginPath(); multihopCtx.moveTo(a.x, a.y); multihopCtx.lineTo(b.x, b.y); multihopCtx.stroke();
  });
  MULTIHOP_NODES.forEach(n => {
    if (!showHop(n.kind)) return;
    const col = n.kind === 'query' ? '255,255,255' : n.kind === 'hop1' ? '56,189,248' : n.kind === 'hop2' ? '163,230,53' : '245,158,11';
    const r = n.kind === 'query' ? 16 : n.kind === 'hop1' ? 10 : n.kind === 'hop2' ? 8 : 6;
    multihopCtx.fillStyle = 'rgba(' + col + ',0.7)';
    multihopCtx.beginPath(); multihopCtx.arc(n.x, n.y, r, 0, Math.PI * 2); multihopCtx.fill();
    multihopCtx.strokeStyle = 'rgba(' + col + ',1)'; multihopCtx.lineWidth = 1.5; multihopCtx.stroke();
    if (n.kind === 'query') {
      multihopCtx.fillStyle = '#000'; multihopCtx.font = 'bold 10px monospace'; multihopCtx.textAlign = 'center';
      multihopCtx.fillText('Q', n.x, n.y + 3);
    }
  });
  // Legend / counts
  const hop1Count = MULTIHOP_NODES.filter(n => n.kind === 'hop1').length;
  const hop2Count = MULTIHOP_NODES.filter(n => n.kind === 'hop2').length;
  const hop3Count = MULTIHOP_NODES.filter(n => n.kind === 'hop3').length;
  multihopCtx.font = '11px monospace'; multihopCtx.textAlign = 'left';
  multihopCtx.fillStyle = 'rgba(56,189,248,0.9)';
  multihopCtx.fillText('first hop (vector top-k): ' + (multihopLevel >= 1 ? hop1Count : 0) + ' docs', 30, 30);
  multihopCtx.fillStyle = 'rgba(163,230,53,0.9)';
  multihopCtx.fillText('second hop (graph spread): ' + (multihopLevel >= 2 ? hop2Count : 0) + ' docs', 30, 50);
  multihopCtx.fillStyle = 'rgba(245,158,11,0.9)';
  multihopCtx.fillText('third hop: ' + (multihopLevel >= 3 ? hop3Count : 0) + ' docs', 30, 70);
  multihopCtx.fillStyle = '#6a7a8a'; multihopCtx.font = '10px monospace';
  multihopCtx.fillText('top-k stops at first hop; Vectora keeps going', 30, H - 20);
  requestAnimationFrame(drawMultihop);
}
drawMultihop();

// ═══════════════════════════════════════════════════════════════════════
// Recall Benchmark
// ═══════════════════════════════════════════════════════════════════════
const benchCanvas = document.getElementById('bench-canvas');
const benchCtx = benchCanvas.getContext('2d');
let benchData = null;
function benchGen() {
  // Simulate 500 queries under top-k vs Vectora
  benchData = {
    topk:   { recall: 0.62 + (Math.random() - 0.5) * 0.03, multihop: 0.18 + (Math.random() - 0.5) * 0.04, precision: 0.71 + (Math.random() - 0.5) * 0.03, context: 0, latency: 1.0 },
    vectora:{ recall: 0.84 + (Math.random() - 0.5) * 0.03, multihop: 0.62 + (Math.random() - 0.5) * 0.04, precision: 0.73 + (Math.random() - 0.5) * 0.03, context: 0.31 + (Math.random() - 0.5) * 0.04, latency: 1.0 + 0.12 + Math.random() * 0.05 },
  };
}
benchGen();
function benchRegen() { benchGen(); pepSend('bench.regen', {}); }
function drawBench() {
  const W = 960, H = 480; benchCtx.fillStyle = themeBg(); benchCtx.fillRect(0, 0, W, H);
  if (!benchData) { requestAnimationFrame(drawBench); return; }
  const d = benchData;
  const metrics = [
    { label: 'Recall@10', tk: d.topk.recall, vc: d.vectora.recall, fmt: (v) => (v * 100).toFixed(1) + '%', higher: true },
    { label: 'Multi-hop relevance', tk: d.topk.multihop, vc: d.vectora.multihop, fmt: (v) => (v * 100).toFixed(1) + '%', higher: true },
    { label: 'Precision@5', tk: d.topk.precision, vc: d.vectora.precision, fmt: (v) => (v * 100).toFixed(1) + '%', higher: true },
    { label: 'Context-aware uplift', tk: d.topk.context, vc: d.vectora.context, fmt: (v) => (v * 100).toFixed(1) + '%', higher: true },
    { label: 'Latency (index)', tk: d.topk.latency / 1.5, vc: d.vectora.latency / 1.5, fmt: (v) => (v * 1.5).toFixed(2) + 'x', higher: false },
  ];
  benchCtx.fillStyle = '#aaa'; benchCtx.font = '11px monospace'; benchCtx.textAlign = 'left';
  benchCtx.fillText('500 synthetic queries · top-k (purple) vs Vectora (lime)', 30, 24);
  const barW = 340, barH = 26, gap = 58;
  metrics.forEach((m, i) => {
    const y = 60 + i * (barH * 2 + gap);
    benchCtx.fillStyle = '#e0e0e0'; benchCtx.font = 'bold 12px monospace'; benchCtx.textAlign = 'left';
    benchCtx.fillText(m.label, 30, y);
    benchCtx.fillStyle = 'rgba(168,85,247,0.25)'; benchCtx.fillRect(30, y + 8, barW, barH);
    benchCtx.fillStyle = 'rgba(168,85,247,0.85)'; benchCtx.fillRect(30, y + 8, barW * Math.min(1, m.tk), barH);
    benchCtx.fillStyle = '#fff'; benchCtx.font = '11px monospace'; benchCtx.textAlign = 'right';
    benchCtx.fillText('top-k: ' + m.fmt(m.tk), 30 + barW - 6, y + 8 + barH / 2 + 4);
    benchCtx.fillStyle = 'rgba(163,230,53,0.25)'; benchCtx.fillRect(30, y + 8 + barH + 4, barW, barH);
    benchCtx.fillStyle = 'rgba(163,230,53,0.85)'; benchCtx.fillRect(30, y + 8 + barH + 4, barW * Math.min(1, m.vc), barH);
    benchCtx.fillStyle = '#fff';
    benchCtx.fillText('Vectora: ' + m.fmt(m.vc), 30 + barW - 6, y + 8 + barH + 4 + barH / 2 + 4);
    const delta = m.vc - m.tk;
    const pct = m.tk > 0.001 ? (delta / m.tk * 100) : 0;
    const isGood = m.higher ? delta > 0 : delta < 0;
    const col = isGood ? 'rgba(163,230,53,0.95)' : 'rgba(248,113,113,0.95)';
    benchCtx.fillStyle = col; benchCtx.font = 'bold 13px monospace'; benchCtx.textAlign = 'left';
    const sign = pct > 0 ? '+' : '';
    benchCtx.fillText(sign + pct.toFixed(0) + '%', 400, y + 8 + barH + 4);
    benchCtx.fillStyle = '#aaa'; benchCtx.font = '10px monospace';
    benchCtx.fillText(isGood ? 'better' : 'tradeoff', 400, y + 8 + barH + 20);
  });
  benchCtx.fillStyle = 'rgba(163,230,53,0.95)'; benchCtx.font = 'bold 12px monospace'; benchCtx.textAlign = 'center';
  benchCtx.fillText('recall and multi-hop gains; small latency tax on the graph walk', W / 2, H - 20);
  requestAnimationFrame(drawBench);
}
drawBench();

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

// ═══════════════════════════════════════════════════════════════════════
// Organizational Opacity — mirrors pep.vectora.org_opacity in the browser
// ═══════════════════════════════════════════════════════════════════════
const OO_TEAMS = ['platform','eng','product','design','ops','hr','legal','finance'];
const OO_STEMS = ['Runbook: ','RFC #','Spec: ','Memo — ','Q-plan ','Playbook: ','Retro — ','Design doc: ','Proposal: ','Policy: ','Guide: ','Strategy memo — ','Onboarding: ','Architecture — ','Review: '];
const OO_TOPICS = ['service migration','deploy safety','data retention','compensation bands','vendor onboarding','incident response','feature flags','privacy review','growth plan','metrics dashboard','hiring loop','security audit','design system','customer interview','tech debt','content moderation','api versioning','capacity planning'];
function ooExp(mean, rng) { return -Math.log(1 - rng()) * mean; }
let ooRngState = 42;
function ooRng() { ooRngState = (ooRngState * 1664525 + 1013904223) % 4294967296; return ooRngState / 4294967296; }
let ooDocs = [];
function ooBuildCorpus(n) {
  ooRngState = 42;
  const docs = [];
  for (let i = 0; i < n; i++) {
    const team = OO_TEAMS[Math.floor(ooRng() * OO_TEAMS.length)];
    const stem = OO_STEMS[Math.floor(ooRng() * OO_STEMS.length)];
    const topic = OO_TOPICS[Math.floor(ooRng() * OO_TOPICS.length)];
    const mix = ooRng();
    let age;
    if (mix < 0.4) age = ooExp(40, ooRng);
    else if (mix < 0.8) age = ooExp(180, ooRng);
    else age = ooExp(720, ooRng);
    age = Math.min(age, 4 * 365);
    const base = 0.6 + ooRng() * 0.4;
    const isLoadBearing = ooRng() < 0.12;
    const refs = isLoadBearing ? 3 + Math.floor(ooRng() * 12) : 0;
    const criticality = 0.2 + ooRng() * 0.7;
    const regulated = ooRng() < 0.08;
    const halfLife = [60, 90, 120, 180][Math.floor(ooRng() * 4)];
    docs.push({
      id: 'doc-' + String(i).padStart(4, '0'),
      title: stem + topic + ' (' + team + ')',
      team, opacity: base, encodedDaysAgo: age,
      halfLife, refs, criticality, regulated,
    });
  }
  return docs;
}
function ooEffective(d, tElapsed) {
  const total = Math.max(0, d.encodedDaysAgo + tElapsed);
  const decayed = d.opacity * Math.pow(0.5, total / d.halfLife);
  return Math.max(0.02, decayed);
}
function ooLoadBearing(d) { return d.refs >= 3 || d.criticality >= 0.7 || d.regulated; }
function ooTime()   { return parseFloat(document.getElementById('oo-time').value); }
function ooThresh() { return parseFloat(document.getElementById('oo-thresh').value) / 100; }
function ooReport() {
  const t = ooTime(), th = ooThresh();
  const hist = new Array(10).fill(0);
  let reusable = 0;
  const arch = [], stale = [];
  const byTeam = {};
  ooDocs.forEach(d => {
    const op = ooEffective(d, t);
    hist[Math.min(9, Math.floor(op * 10))]++;
    const te = byTeam[d.team] || (byTeam[d.team] = { total: 0, reusable: 0 });
    te.total++;
    if (op < th) {
      reusable++; te.reusable++;
      if (ooLoadBearing(d)) stale.push({ d, op }); else arch.push({ d, op });
    }
  });
  let willCross = 0;
  ooDocs.forEach(d => {
    const cur = ooEffective(d, t);
    if (cur >= th && cur < 2 * th && ooEffective(d, t + 14) < th) willCross++;
  });
  const velocity = willCross / 14 * 7;
  arch.sort((a, b) => a.op - b.op);
  stale.sort((a, b) => (b.d.refs - a.d.refs) || (a.op - b.op));
  return { hist, reusable, arch, stale, byTeam, total: ooDocs.length, velocity };
}
function ooReinforceRandom() {
  for (let i = 0; i < 5; i++) {
    const idx = Math.floor(Math.random() * ooDocs.length);
    const d = ooDocs[idx];
    const op = ooEffective(d, ooTime());
    d.opacity = Math.min(1, op + 0.5);
    d.encodedDaysAgo = -ooTime();
  }
  pepSend('orgopacity.reinforce', {});
}
function ooReset() {
  ooDocs = ooBuildCorpus(140);
  document.getElementById('oo-time').value = 0;
  document.getElementById('oo-time-val').textContent = '0 d';
}
['oo-time','oo-thresh'].forEach(id => {
  const el = document.getElementById(id); if (!el) return;
  el.addEventListener('input', (e) => {
    const v = parseFloat(e.target.value);
    const out = document.getElementById(id + '-val');
    if (!out) return;
    out.textContent = id === 'oo-thresh' ? (v / 100).toFixed(2) : v + ' d';
  });
});
ooDocs = ooBuildCorpus(140);
const ooCanvas = document.getElementById('orgopacity-canvas');
const ooCtx = ooCanvas.getContext('2d');
function ooEsc(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function ooRenderLists(rep) {
  const archPanel = document.getElementById('oo-archive');
  const stalePanel = document.getElementById('oo-stale');
  const archRows = rep.arch.slice(0, 10).map(x =>
    `<div style="display:flex;gap:10px;align-items:center;padding:4px 0;font-size:11px;border-bottom:1px solid rgba(255,255,255,0.04)"><span style="color:#81c784;min-width:44px;font-family:monospace">${x.op.toFixed(3)}</span><span style="color:var(--text);flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${ooEsc(x.d.title)}</span></div>`
  ).join('');
  archPanel.innerHTML = `<div style="color:#81c784;font-size:11px;letter-spacing:0.12em;margin-bottom:8px">ARCHIVE CANDIDATES &middot; ${rep.arch.length} total &middot; showing top 10</div>${archRows || '<div style="color:var(--dim);font-size:12px;padding:30px 0;text-align:center">nothing below threshold yet</div>'}`;
  const staleRows = rep.stale.slice(0, 10).map(x =>
    `<div style="display:flex;gap:10px;align-items:center;padding:4px 0;font-size:11px;border-bottom:1px solid rgba(255,255,255,0.04)"><span style="color:#f06292;min-width:44px;font-family:monospace">${x.op.toFixed(3)}</span><span style="color:var(--dim);min-width:34px;font-size:10px">${x.d.refs}ref</span><span style="color:var(--text);flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${ooEsc(x.d.title)}${x.d.regulated ? ' <span style=\"color:#e879f9;font-size:9px\">REG</span>' : ''}</span></div>`
  ).join('');
  stalePanel.innerHTML = `<div style="color:#f06292;font-size:11px;letter-spacing:0.12em;margin-bottom:8px">LOAD-BEARING STALE &middot; ${rep.stale.length} total &middot; showing top 10</div>${staleRows || '<div style="color:var(--dim);font-size:12px;padding:30px 0;text-align:center">no load-bearing docs are decayed (good)</div>'}`;
}
function drawOrgOpacity() {
  const W = 960, H = 340;
  ooCtx.fillStyle = themeBg(); ooCtx.fillRect(0, 0, W, H);
  const rep = ooReport();
  const padL = 60, padR = 20, padT = 48, padB = 60;
  const plotW = W - padL - padR, plotH = H - padT - padB;
  const maxCount = Math.max(1, ...rep.hist);
  // Bars
  rep.hist.forEach((c, i) => {
    const bw = plotW / 10;
    const bh = (c / maxCount) * plotH;
    const x = padL + i * bw + bw * 0.1;
    const y = padT + plotH - bh;
    const w = bw * 0.8;
    const bucketMid = (i + 0.5) / 10;
    const inReuse = bucketMid < ooThresh();
    ooCtx.fillStyle = inReuse ? 'rgba(240,98,146,0.85)' : `rgba(79,195,247,${(0.3 + bucketMid * 0.5).toFixed(3)})`;
    ooCtx.fillRect(x, y, w, bh);
    ooCtx.fillStyle = '#aaa'; ooCtx.font = '10px monospace'; ooCtx.textAlign = 'center';
    if (c > 0) ooCtx.fillText(String(c), x + w / 2, y - 4);
    ooCtx.fillText(((i) / 10).toFixed(1) + '-' + ((i + 1) / 10).toFixed(1), x + w / 2, padT + plotH + 14);
  });
  // Threshold line
  const thX = padL + (ooThresh() * 10) * (plotW / 10);
  ooCtx.strokeStyle = 'rgba(248, 113, 113, 0.7)'; ooCtx.setLineDash([4, 4]);
  ooCtx.lineWidth = 1.5;
  ooCtx.beginPath(); ooCtx.moveTo(thX, padT); ooCtx.lineTo(thX, padT + plotH); ooCtx.stroke();
  ooCtx.setLineDash([]);
  ooCtx.fillStyle = '#f87171'; ooCtx.font = 'bold 10px monospace'; ooCtx.textAlign = 'left';
  ooCtx.fillText('← reuse threshold', thX + 6, padT + 10);
  // Title row: reusable % + velocity
  const pct = rep.total ? (100 * rep.reusable / rep.total).toFixed(1) : '0.0';
  ooCtx.fillStyle = '#dce4ed'; ooCtx.font = 'bold 13px monospace'; ooCtx.textAlign = 'left';
  ooCtx.fillText(`${rep.reusable} of ${rep.total} docs below threshold  (${pct}% reclaimable)`, padL, 22);
  ooCtx.fillStyle = '#aaa'; ooCtx.font = '11px monospace'; ooCtx.textAlign = 'right';
  ooCtx.fillText(`decay velocity: ${rep.velocity.toFixed(1)} docs/week crossing threshold`, W - 20, 22);
  // Axis labels
  ooCtx.fillStyle = '#aaa'; ooCtx.font = '10px monospace'; ooCtx.textAlign = 'left';
  ooCtx.fillText('doc count', 20, padT + 4);
  ooCtx.textAlign = 'center';
  ooCtx.fillText('opacity bucket', padL + plotW / 2, H - 8);
  ooRenderLists(rep);
  requestAnimationFrame(drawOrgOpacity);
}
drawOrgOpacity();

</script>
</body>
</html>
"""


@router.get("/vectora", response_class=HTMLResponse)
async def vectora_page() -> str:
    return _PAGE
