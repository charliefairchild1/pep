"""PEP — the engine itself. Interactive teaching page at /pep."""

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
<title>PEP — Predictive Encoding and Preparation</title>
<style>
  :root {
    --bg: #0d0f14; --surface: #1a1f2a; --surface2: #131821;
    --text: #e2e8f0; --dim: #778; --accent: #a78bfa; --accent2: #34d399;
    --warn: #fbbf24; --border: #252b38;
  }
  body.light {
    --bg: #f8f9fb; --surface: #ffffff; --surface2: #eff2f7;
    --text: #1a1a1a; --dim: #555; --accent: #6d28d9; --accent2: #047857;
    --warn: #b45309; --border: #d0d6de;
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
  .brand { font-size: 20px; font-weight: bold; color: var(--accent); letter-spacing: 1px; }
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
          border: 1px solid var(--border); border-radius: 8px; padding: 32px 36px;
          margin-bottom: 24px; }
  .hero h1 { font-size: 24px; color: var(--accent); margin-bottom: 10px; font-weight: bold;
             letter-spacing: 0.5px; }
  .hero p { font-size: 12px; color: var(--text); line-height: 1.8; margin-bottom: 10px; }
  .hero .tag { font-size: 10px; color: var(--dim); letter-spacing: 0.3em;
               text-transform: uppercase; margin-bottom: 6px; }
  .lavas-card { display: block; background: var(--surface); border: 1px solid var(--border);
                border-radius: 6px; padding: 14px 18px; margin-bottom: 8px;
                transition: border-color 0.2s; }
  .lavas-card:hover { border-color: var(--accent); text-decoration: none; }
  .lavas-card .name { font-size: 13px; font-weight: bold; color: var(--accent); }
  .lavas-card .desc { font-size: 11px; color: var(--dim); margin-top: 4px; margin-bottom: 0; }
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
    h1 { font-size: 18px !important; }
    h2 { font-size: 14px; }
    h3 { font-size: 12px; }
    .canvas-box canvas { width: 100% !important; height: auto !important; max-width: 100%; }
    .info { font-size: 11px; line-height: 1.6; }
    .hero { padding: 20px 18px; }
    .lavas-switch { gap: 6px; font-size: 10px; }
    #pep-link-badge { display: none; }
  }
</style>
</head>
<body>
<nav>
  <div class="nav-row nav-row-top">
    <span class="brand">PEP</span>
    <span style="font-size:10px;color:var(--dim)">Predictive Encoding and Preparation · the engine</span>
    <span id="pep-link-badge" style="margin-left:auto;font-size:10px;color:var(--dim);display:flex;align-items:center;gap:6px;padding:0 8px">
      <span id="pep-link-dot" style="width:8px;height:8px;border-radius:50%;background:#666;display:inline-block"></span>
      <span id="pep-link-label">mesh: …</span>
    </span>
    <select id="canvas-select" onchange="canvasSelect(this.value)"
      style="background:var(--surface);color:var(--text);border:1px solid var(--border);
      border-radius:4px;padding:4px 8px;font-family:inherit;font-size:10px;max-width:220px">
      <option value="">jump to canvas…</option>
    </select>
    <button onclick="toggleLight()" id="light-btn" class="nav-btn">Light Mode</button>
    <span class="lavas-switch" style="display:flex;gap:8px;align-items:center;font-size:11px;flex-wrap:wrap">
      <span class="lavas-current">PEP</span>
      <a href="/axona">Axona</a>
      <a href="/lingora">Lingora</a>
      <a href="/atria">Atria</a>
      <a href="/vectora">Vectora</a>
      <a href="/strata">Strata</a>
      <a href="/math" style="opacity:0.7">Math</a>
    </span>
  </div>
  <div class="nav-row nav-row-bottom">
    <div class="tabs" id="tabs">
      <div class="tab active" data-panel="home-tab">Home</div>
      <div class="tab" data-panel="graph-tab">Weighted Graph</div>
      <div class="tab" data-panel="spread-tab">Spreading Activation</div>
      <div class="tab" data-panel="residual-tab">Predictor + Residual</div>
      <div class="tab" data-panel="modulator-tab">State Modulator</div>
      <div class="tab" data-panel="mesh-tab">Mesh Dashboard</div>
      <div class="tab" data-panel="theory-tab">Theory</div>
    </div>
  </div>
</nav>

<!-- ═══ Home ══════════════════════════════════════════════════════ -->
<div class="panel active" id="home-tab">
<div class="container">
  <div class="hero">
    <div class="tag">PEP</div>
    <h1>The Engine the LAVAS Apps Run On</h1>
    <p>
      PEP is a small vocabulary of primitives: weighted graphs, spreading
      activation, predictors with residual scoring, and state modulators.
      Every LAVAS app is a different configuration of those four primitives
      applied to a different domain. Axona maps them onto cognition. Lingora
      maps them onto language. Atria maps them onto matching. Vectora and
      Strata will map them onto data and markets. The engine is the same.
    </p>
    <p>
      This page is PEP's own teaching surface. Each of the four primitives
      gets one compact demo, and the mesh dashboard shows every LAVAS
      sibling talking to PEP in real time. If the siblings feel like
      separate apps, the mesh makes it clear they are not — they are one
      system observed through different lenses.
    </p>
  </div>

  <h3>The four LAVAS siblings</h3>
  <a class="lavas-card" href="/axona">
    <div class="name">Axona → /axona</div>
    <div class="desc">Brain, cognition, and neural interface. ~60 canvases covering memory, attention, prediction, sleep, trauma, language perception, and dozens more. The most mature surface.</div>
  </a>
  <a class="lavas-card" href="/lingora">
    <div class="name">Lingora → /lingora</div>
    <div class="desc">Language as a cognitive technology. ~70 canvases on words, sounds, sentences, speech acts, reading, writing, cross-language, and machines.</div>
  </a>
  <a class="lavas-card" href="/atria">
    <div class="name">Atria → /atria</div>
    <div class="desc">Matching, compatibility, relational alignment. First commercial wedge: PvP matchmaking. ~20 canvases on the Elo fallacy, pool spreading, residual closing, behavior modulation.</div>
  </a>
  <a class="lavas-card" href="/vectora">
    <div class="name">Vectora → /vectora</div>
    <div class="desc">Data organization, pattern analysis, intelligent retrieval. The internal infrastructure layer. ~5 canvases on keyword vs semantic search, embedding spaces, knowledge graphs, anomaly detection.</div>
  </a>
  <a class="lavas-card" href="/strata">
    <div class="name">Strata → /strata</div>
    <div class="desc">Markets, trading signals, financial decision-making. Research sandbox. ~5 canvases on correlation graphs, momentum spreading, earnings residuals, regime modulation, sector rotation.</div>
  </a>

  <h3>Why PEP has its own teaching page</h3>
  <div class="info">
    The three LAVAS apps all teach <em>about</em> PEP — they call PEP's
    primitives by name and demonstrate them in specific domains. For a long
    time PEP itself had no teaching surface, which meant "see the engine"
    was always a reference to some sibling's demo. This page fixes that.
    Each primitive gets a compact canvas here that is neither
    cognition-specific nor language-specific nor matching-specific — just
    the primitive itself, running on synthetic data, labeled with PEP's own
    vocabulary.<br><br>
    When a sibling app says "this is spreading activation applied to X," you
    can click over here and see what spreading activation looks like in the
    abstract. When it says "this canvas closes the residual," you can see
    the residual scorer itself on this page. The four primitive demos are
    the engine's ground truth. Everything else is an application.
  </div>

  <h3>Recent research cut (memory, for future sessions)</h3>
  <div class="info">
    PEP's MemoryStore lives in <code>pep/src/pep/memory/store.py</code>.
    Runs are recorded with their PEPPackets, activation traces, and
    residual scores. A session is a sequence of runs. The store is SQLite
    by default (<code>data/pep.db</code>) and uses simple schema so it can
    be reasoned about without a migration system.<br><br>
    The live FastAPI surface mounts several routes from
    <code>pep/src/pep/main.py</code>: <code>/chat</code>, <code>/debug</code>,
    <code>/ui</code>, <code>/openai/*</code>, <code>/math</code>, <code>/pep</code>
    (this page), <code>/axona</code>, <code>/lingora</code>, <code>/atria</code>,
    and the three bridge endpoints. The bridge cross-reads are symmetric:
    every LAVAS app can see every other LAVAS app's recent events without
    going through PEP's core.
  </div>
</div>
</div>

<!-- ═══ Weighted Graph ═══════════════════════════════════════════ -->
<div class="panel" id="graph-tab">
<div class="container">
  <h2>Weighted Graph — Nodes With Typed Edges</h2>
  <p class="desc">
    The simplest PEP primitive. A set of nodes, each with a feature vector.
    Edges weighted by typed compatibility. Everything downstream — memory,
    matching, language, attention — reduces to operations on structures
    that look like this.
  </p>
  <div class="canvas-box">
    <canvas id="graph-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <button onclick="graphRegen()">Regenerate graph</button>
    <button onclick="graphToggleType()">Toggle edge type (skill ↔ tempo ↔ social)</button>
    <label style="display:flex;align-items:center;gap:8px;margin-left:10px">
      <span>edge threshold:</span>
      <input type="range" id="graph-thresh" min="0" max="100" value="40" style="width:120px">
      <span class="stat-val" id="graph-thresh-val">0.40</span>
    </label>
  </div>
  <div class="info">
    <b>What you are watching:</b> 24 synthetic nodes with multi-dimensional
    feature vectors (skill, tempo, social). Edges are drawn only where the
    compatibility on the currently-displayed dimension exceeds the threshold
    slider. Toggle the edge type to see how the same nodes can form
    completely different graphs depending on which dimension you project
    through.<br><br>
    <b>Why this primitive is load-bearing:</b> Every LAVAS app builds its
    specific graph out of this shape. Axona's attention graph connects
    memory nodes by co-occurrence. Lingora's compatibility graph connects
    words by shared context. Atria's compatibility graph connects players
    by matchup features. The nodes and labels change; the data structure
    does not.<br><br>
    <b>See also:</b>
    <a href="/axona">Axona → Attention Spotlight</a>,
    <a href="/lingora">Lingora → Word as Constellation</a>,
    <a href="/atria">Atria → Multi-Objective Projection</a>.
  </div>
</div>
</div>

<!-- ═══ Spreading Activation ═════════════════════════════════════ -->
<div class="panel" id="spread-tab">
<div class="container">
  <h2>Spreading Activation — The Native Search Primitive</h2>
  <p class="desc">
    Click any node to seed activation. It radiates outward through weighted
    edges with decay, forming a neighborhood-shaped region. This is how
    every LAVAS app turns "who should I consider?" into a graph operation
    instead of a sorting operation.
  </p>
  <div class="canvas-box">
    <canvas id="spread-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <label style="display:flex;align-items:center;gap:8px">
      <span>decay:</span>
      <input type="range" id="spread-decay" min="5" max="60" value="25" style="width:120px">
      <span class="stat-val" id="spread-decay-val">0.25</span>
    </label>
    <button onclick="spreadReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      reached: <b style="color:var(--accent)" id="spread-reached">0</b>
    </span>
  </div>
  <div class="info">
    <b>What you are watching:</b> The same graph from the previous tab.
    Click any node and activation flows outward through the edges,
    attenuating by the decay factor at each hop. Nodes with strong edges to
    the seed become brightly lit. Nodes only loosely connected fade to
    nothing. The "pool" is just the set of nodes above the visibility
    threshold.<br><br>
    <b>Why this beats a sorted window:</b> Sorting by a single feature gives
    the same pool regardless of who the seed is — you just translate the
    window. Graph-based spreading produces a pool that <em>adapts to the
    seed</em>. A node with many high-weight edges reaches a wider pool; a
    node with few reaches a smaller one. Both pools only contain
    candidates the seed is actually compatible with.<br><br>
    <b>See also:</b>
    <a href="/axona">Axona → Attention Spotlight</a>,
    <a href="/lingora">Lingora → Word as Constellation</a>,
    <a href="/atria">Atria → Pool Spreading</a>.
  </div>
</div>
</div>

<!-- ═══ Predictor + Residual ═════════════════════════════════════ -->
<div class="panel" id="residual-tab">
<div class="container">
  <h2>Predictor + Residual Scorer — The Learning Signal</h2>
  <p class="desc">
    A running forecast of the next input, and a scorer for the gap between
    forecast and reality. The residual is the only signal PEP uses for
    learning. When it fires, pathways update; when it stays flat, the
    system assumes its priors are correct and does nothing.
  </p>
  <div class="canvas-box">
    <canvas id="residual-canvas" width="960" height="320"></canvas>
  </div>
  <div class="controls">
    <button onclick="residualShock()">Inject surprise</button>
    <button onclick="residualReset()">Reset</button>
    <label style="display:flex;align-items:center;gap:8px">
      <span>prior stiffness:</span>
      <input type="range" id="residual-prior" min="10" max="99" value="70" style="width:120px">
      <span class="stat-val" id="residual-prior-val">0.70</span>
    </label>
    <span style="margin-left:auto;color:var(--dim)">
      residual spikes: <b style="color:var(--warn)" id="residual-spikes">0</b>
    </span>
  </div>
  <div class="info">
    <b>What you are watching:</b> A synthetic signal (green) and the
    predictor's forecast (purple) running alongside it. Most of the time
    the forecast tracks the signal closely and the residual (orange bars
    at the bottom) is near zero. Click "Inject surprise" and the signal
    jumps; the forecast lags; a spike appears. That spike is the only
    moment the system learns. Outside of spikes, nothing is updated.<br><br>
    <b>Prior stiffness</b> controls how fast the forecast adapts. A stiff
    prior (0.95) holds firm; a loose prior (0.2) chases every fluctuation.
    Stiffer priors reject more noise but miss slower changes; looser
    priors catch changes but update on things that are not really
    signals. There is no single right setting — it depends on the
    signal-to-noise ratio of the domain.<br><br>
    <b>See also:</b>
    <a href="/axona">Axona → Prediction vs Reality</a>,
    <a href="/axona">Axona → Reward Prediction Error</a>,
    <a href="/lingora">Lingora → Sentence Forecast</a>,
    <a href="/lingora">Lingora → Poetry as Residual</a>,
    <a href="/atria">Atria → Residual Heatmap</a>,
    <a href="/atria">Atria → Rematch Oracle</a>.
  </div>
</div>
</div>

<!-- ═══ State Modulator ══════════════════════════════════════════ -->
<div class="panel" id="modulator-tab">
<div class="container">
  <h2>State Modulator — Slow-Timescale Gain Control</h2>
  <p class="desc">
    A slower-moving parameter that rescales the weights and gains the other
    primitives use. Mood, fatigue, context, recent behavior — all get
    represented as state modulators, and all compose into the multiplicative
    factor that sits on every other primitive's output.
  </p>
  <div class="canvas-box">
    <canvas id="modulator-canvas" width="960" height="360"></canvas>
  </div>
  <div class="controls">
    <label style="display:flex;align-items:center;gap:8px">
      <span>mood:</span>
      <input type="range" id="mod-mood" min="0" max="100" value="60" style="width:100px">
      <span class="stat-val" id="mod-mood-val">0.60</span>
    </label>
    <label style="display:flex;align-items:center;gap:8px">
      <span>fatigue:</span>
      <input type="range" id="mod-fatigue" min="0" max="100" value="20" style="width:100px">
      <span class="stat-val" id="mod-fatigue-val">0.20</span>
    </label>
    <label style="display:flex;align-items:center;gap:8px">
      <span>focus:</span>
      <input type="range" id="mod-focus" min="0" max="100" value="70" style="width:100px">
      <span class="stat-val" id="mod-focus-val">0.70</span>
    </label>
  </div>
  <div class="info">
    <b>What you are watching:</b> A fixed underlying graph with fixed
    edge weights. The three sliders modulate the <em>effective</em> gain
    of the edges by multiplicative factors. High mood raises the gain on
    positive-valence edges. High fatigue lowers the gain on
    expensive-to-traverse edges. High focus narrows the gain to a single
    spotlight region.<br><br>
    <b>Why this is separate from weights:</b> Edge weights are learned
    from experience and change slowly (hours, days, weeks). State
    modulators change fast (seconds, minutes) and do not require
    relearning. Decoupling them means the system can respond to
    moment-to-moment context without forgetting what it learned, and it
    can forget what it learned without losing its current state. Slow
    knowledge and fast state are separate degrees of freedom that play
    together at runtime.<br><br>
    <b>See also:</b>
    <a href="/axona">Axona → Placebo / Belief Propagation</a>,
    <a href="/axona">Axona → Cognitive Bandwidth</a>,
    <a href="/lingora">Lingora → Taboo Words</a>,
    <a href="/atria">Atria → Behavior Modulation</a>.
  </div>
</div>
</div>

<!-- ═══ Mesh Dashboard ═══════════════════════════════════════════ -->
<div class="panel" id="mesh-tab">
<div class="container">
  <h2>Mesh Dashboard — Four Surfaces, One System</h2>
  <p class="desc">
    Live status of PEP, Axona, Lingora, and Atria. Each sibling's event
    buffer is polled every 2.5 seconds. Click any event line to jump to
    the canvas that generated it (when possible).
  </p>
  <div style="display:flex;gap:16px;margin-bottom:16px">
    <div class="info" style="flex:1">
      <b>PEP engine state</b><br><br>
      <div style="font-family:monospace;font-size:11px;line-height:1.8">
        <div>LLM: <span id="mesh-llm" style="color:var(--accent)">—</span></div>
        <div>embeddings: <span id="mesh-emb" style="color:var(--accent)">—</span></div>
        <div>recent runs: <span id="mesh-runs" style="color:var(--accent)">—</span></div>
        <div>latest run: <span id="mesh-latest" style="color:var(--dim)">—</span></div>
      </div>
    </div>
    <div class="info" style="flex:1">
      <b>Event counts (last 200 per app)</b><br><br>
      <div style="font-family:monospace;font-size:11px;line-height:1.8">
        <div><span style="color:var(--accent)">Axona</span>: <b id="mesh-count-axona">—</b> events</div>
        <div><span style="color:var(--accent)">Lingora</span>: <b id="mesh-count-lingora">—</b> events</div>
        <div><span style="color:var(--accent)">Atria</span>: <b id="mesh-count-atria">—</b> events</div>
        <div><span style="color:var(--accent)">Vectora</span>: <b id="mesh-count-vectora">—</b> events</div>
        <div><span style="color:var(--accent)">Strata</span>: <b id="mesh-count-strata">—</b> events</div>
      </div>
    </div>
  </div>
  <div style="display:flex;gap:12px;flex-wrap:wrap">
    <div class="canvas-box" style="padding:14px;flex:1;min-width:280px">
      <div style="font-family:monospace;font-size:11px;color:var(--accent);margin-bottom:8px">&gt; Axona events</div>
      <div id="mesh-log-axona" style="font-family:monospace;font-size:11px;line-height:1.7;max-height:240px;overflow-y:auto;color:var(--text)">
        <span style="color:var(--dim)">polling…</span>
      </div>
    </div>
    <div class="canvas-box" style="padding:14px;flex:1;min-width:280px">
      <div style="font-family:monospace;font-size:11px;color:var(--accent2);margin-bottom:8px">&gt; Lingora events</div>
      <div id="mesh-log-lingora" style="font-family:monospace;font-size:11px;line-height:1.7;max-height:240px;overflow-y:auto;color:var(--text)">
        <span style="color:var(--dim)">polling…</span>
      </div>
    </div>
    <div class="canvas-box" style="padding:14px;flex:1;min-width:280px">
      <div style="font-family:monospace;font-size:11px;color:var(--warn);margin-bottom:8px">&gt; Atria events</div>
      <div id="mesh-log-atria" style="font-family:monospace;font-size:11px;line-height:1.7;max-height:240px;overflow-y:auto;color:var(--text)">
        <span style="color:var(--dim)">polling…</span>
      </div>
    </div>
    <div class="canvas-box" style="padding:14px;flex:1;min-width:280px">
      <div style="font-family:monospace;font-size:11px;color:#38bdf8;margin-bottom:8px">&gt; Vectora events</div>
      <div id="mesh-log-vectora" style="font-family:monospace;font-size:11px;line-height:1.7;max-height:240px;overflow-y:auto;color:var(--text)">
        <span style="color:var(--dim)">polling…</span>
      </div>
    </div>
    <div class="canvas-box" style="padding:14px;flex:1;min-width:280px">
      <div style="font-family:monospace;font-size:11px;color:#e879f9;margin-bottom:8px">&gt; Strata events</div>
      <div id="mesh-log-strata" style="font-family:monospace;font-size:11px;line-height:1.7;max-height:240px;overflow-y:auto;color:var(--text)">
        <span style="color:var(--dim)">polling…</span>
      </div>
    </div>
  </div>
  <div class="info">
    <b>How the mesh works:</b> Each LAVAS sibling runs its own bridge
    (<code>{app}_bridge.py</code>) with three kinds of endpoints. An
    event-post endpoint where the sibling's canvases POST typed events; an
    events-read endpoint that returns the ring buffer; and a pep-state
    endpoint that returns PEP's live introspection plus cross-reads of the
    other siblings' buffers. This page polls all five LAVAS siblings in
    parallel and displays the combined picture.<br><br>
    The mesh is what makes the LAVAS suite feel like one system. Every
    sibling can see what every other sibling is doing in real time, and
    this dashboard is the ground truth.
  </div>
</div>
</div>

<!-- ═══ Theory ══════════════════════════════════════════════════ -->
<div class="panel" id="theory-tab">
<div class="container">
  <h2>Theory — The Four Primitives, in Full</h2>
  <p class="desc">
    Condensed framing. Full doc in <code>pep/docs/</code>.
  </p>
  <div class="info">
    <b>1. Weighted graph.</b> A set of nodes with multi-dimensional feature
    vectors, connected by typed edges whose weights come from the
    features. No implicit structure — every relationship is on an edge,
    every feature is on a node, and everything the system "knows" reduces
    to one of these two kinds of annotation.
  </div>
  <div class="info">
    <b>2. Spreading activation.</b> Given a seed node, activation radiates
    through the graph attenuating by edge weight and a tunable decay.
    Neighborhoods are the right shape for search; sorted lists are the
    wrong shape. A specialized decay profile collapses the search to a
    radius-k neighborhood; a looser profile explores further. The whole
    machinery is a single pass over the graph with a budget.
  </div>
  <div class="info">
    <b>3. Predictor + residual scorer.</b> A running forecast of the next
    input given recent context. A scorer for the gap between forecast and
    reality. When the residual is large, the system updates. When it is
    small, the system holds its priors. This is the only place learning
    happens in PEP.
  </div>
  <div class="info">
    <b>4. State modulator.</b> A slow-timescale parameter (mood, fatigue,
    context, recent behavior) that multiplicatively rescales the outputs
    of the other primitives at runtime. Separates slow knowledge (the
    graph) from fast state (the modulators). Allows the same underlying
    graph to produce different behavior under different moment-to-moment
    conditions without retraining anything.
  </div>
  <div class="info">
    <b>How the LAVAS siblings use them.</b><br>
    &bull; <b>Axona</b> uses all four across its cognition canvases. The
    Attention Spotlight is spreading activation; Prediction vs Reality is
    the predictor; Placebo / Behavior Modulation is the state modulator;
    the memory and novelty canvases run on the weighted graph.<br>
    &bull; <b>Lingora</b> treats words as nodes and uses spreading
    activation for word-constellation and listener-reconstruction; the
    predictor for sentence forecasting and poetry residuals; state
    modulators for taboo and register.<br>
    &bull; <b>Atria</b> treats players as nodes, matches as edges, and
    uses spreading activation for pool formation, residual scoring for
    rematch oracle, and state modulation for behavior and confidence.<br>
    &bull; <b>Vectora and Strata</b> (unbuilt) will use the same
    primitives for data retrieval and market signals.
  </div>
  <div class="info">
    <b>The discipline:</b> When building a new LAVAS app, resist the urge
    to invent new primitives. The claim is that these four compose into
    everything the suite needs. Each new app should translate its domain
    into a configuration of the existing four, and the judgment call is
    only about which edges, which decay profile, which modulators, and
    which predictor shape. New primitives are a last resort, and the
    absence of them is what makes the suite cohere.
  </div>
</div>
</div>

<script>
// ═══════════════════════════════════════════════════════════════════════
// Tab switching + canvas dropdown helpers
// ═══════════════════════════════════════════════════════════════════════
function tabPanelIds(tab) {
  const joined = (tab.dataset.panels || tab.dataset.panel || '').trim();
  return joined.split(/\\s+/).filter(Boolean);
}
function findTabForPanel(panelId) {
  return Array.from(document.querySelectorAll('.tab')).find(t => tabPanelIds(t).includes(panelId));
}
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    tab.classList.add('active');
    tabPanelIds(tab).forEach(id => {
      const el = document.getElementById(id);
      if (el) el.classList.add('active');
    });
    window.scrollTo(0, 0);
  });
});
function themeBg() { return getComputedStyle(document.body).getPropertyValue('--bg').trim() || '#0d0f14'; }

function canvasSelect(id) {
  if (!id) return;
  const el = document.getElementById(id);
  if (!el) return;
  let panelId = null;
  if (el.classList && el.classList.contains('panel')) panelId = el.id;
  else {
    const panel = el.closest ? el.closest('.panel') : null;
    if (panel) panelId = panel.id;
  }
  if (panelId) {
    const tab = findTabForPanel(panelId);
    if (tab) tab.click();
  }
  setTimeout(() => {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    const select = document.getElementById('canvas-select');
    if (select) select.value = '';
  }, 60);
}
function buildCanvasDropdown() {
  const select = document.getElementById('canvas-select');
  if (!select) return;
  const tabs = Array.from(document.querySelectorAll('.tab'));
  const skipIds = ['home-tab', 'theory-tab', 'mesh-tab'];
  tabs.forEach(tab => {
    const ids = tabPanelIds(tab);
    if (ids.length === 0) return;
    if (ids.length === 1 && skipIds.includes(ids[0])) return;
    const optgroup = document.createElement('optgroup');
    optgroup.label = tab.textContent.trim();
    ids.forEach(id => {
      const panel = document.getElementById(id);
      if (!panel) return;
      const h2 = panel.querySelector('h2');
      let title = id.replace(/-tab$/, '');
      if (h2) {
        title = h2.textContent.trim();
        const dashIdx = title.indexOf('—');
        if (dashIdx > 0) title = title.slice(0, dashIdx).trim();
      }
      const opt = document.createElement('option');
      opt.value = id;
      opt.textContent = title;
      optgroup.appendChild(opt);
    });
    if (optgroup.children.length > 0) select.appendChild(optgroup);
  });
}
setTimeout(buildCanvasDropdown, 80);

// ═══════════════════════════════════════════════════════════════════════
// Light mode
// ═══════════════════════════════════════════════════════════════════════
function toggleLight() {
  const isLight = document.body.classList.toggle('light');
  const btn = document.getElementById('light-btn');
  if (btn) btn.textContent = isLight ? 'Dark Mode' : 'Light Mode';
  try { localStorage.setItem('pep-theme', isLight ? 'light' : 'dark'); } catch (e) {}
}
(function restoreTheme() {
  try {
    if (localStorage.getItem('pep-theme') === 'light') {
      document.body.classList.add('light');
      const btn = document.getElementById('light-btn');
      if (btn) btn.textContent = 'Dark Mode';
    }
  } catch (e) {}
})();

// ═══════════════════════════════════════════════════════════════════════
// Weighted Graph
// ═══════════════════════════════════════════════════════════════════════
const graphCanvas = document.getElementById('graph-canvas');
const graphCtx = graphCanvas.getContext('2d');
const graphNodes = [];
let graphEdgeType = 'skill';
(function graphInit() {
  const W = 960, H = 440;
  for (let i = 0; i < 24; i++) {
    graphNodes.push({
      x: 60 + Math.random() * (W - 120),
      y: 50 + Math.random() * (H - 100),
      skill: Math.random(),
      tempo: Math.random(),
      social: Math.random(),
    });
  }
})();
document.getElementById('graph-thresh').addEventListener('input', (e) => {
  document.getElementById('graph-thresh-val').textContent = (parseInt(e.target.value) / 100).toFixed(2);
});
function graphRegen() {
  graphNodes.forEach(n => {
    n.skill = Math.random();
    n.tempo = Math.random();
    n.social = Math.random();
  });
}
function graphToggleType() {
  graphEdgeType = graphEdgeType === 'skill' ? 'tempo' : graphEdgeType === 'tempo' ? 'social' : 'skill';
}
function drawGraph() {
  const W = 960, H = 440;
  graphCtx.fillStyle = themeBg(); graphCtx.fillRect(0, 0, W, H);
  const thresh = parseInt(document.getElementById('graph-thresh').value) / 100;
  // Edges
  for (let i = 0; i < graphNodes.length; i++) {
    for (let j = i + 1; j < graphNodes.length; j++) {
      const a = graphNodes[i], b = graphNodes[j];
      const sim = 1 - Math.abs(a[graphEdgeType] - b[graphEdgeType]);
      if (sim < thresh) continue;
      const col = graphEdgeType === 'skill' ? '167,139,250' : graphEdgeType === 'tempo' ? '52,211,153' : '251,191,36';
      graphCtx.strokeStyle = 'rgba(' + col + ',' + (0.15 + sim * 0.5).toFixed(3) + ')';
      graphCtx.lineWidth = 0.5 + sim * 2;
      graphCtx.beginPath(); graphCtx.moveTo(a.x, a.y); graphCtx.lineTo(b.x, b.y); graphCtx.stroke();
    }
  }
  // Nodes
  graphNodes.forEach(n => {
    const r = 6 + n[graphEdgeType] * 8;
    graphCtx.fillStyle = 'rgba(167,139,250,0.75)';
    graphCtx.beginPath(); graphCtx.arc(n.x, n.y, r, 0, Math.PI * 2); graphCtx.fill();
    graphCtx.strokeStyle = 'rgba(167,139,250,1)'; graphCtx.lineWidth = 1.5;
    graphCtx.stroke();
  });
  // Label
  graphCtx.fillStyle = '#aaa'; graphCtx.font = '12px monospace'; graphCtx.textAlign = 'left';
  graphCtx.fillText('edge type: ' + graphEdgeType, 20, 24);
  requestAnimationFrame(drawGraph);
}
drawGraph();

// ═══════════════════════════════════════════════════════════════════════
// Spreading Activation
// ═══════════════════════════════════════════════════════════════════════
const spreadCanvas = document.getElementById('spread-canvas');
const spreadCtx = spreadCanvas.getContext('2d');
const spreadNodes = [];
const spreadEdges = [];
let spreadSeed = -1;
(function spreadInit() {
  const W = 960, H = 440;
  for (let i = 0; i < 24; i++) {
    spreadNodes.push({
      x: 60 + Math.random() * (W - 120),
      y: 50 + Math.random() * (H - 100),
      act: 0,
    });
  }
  for (let i = 0; i < spreadNodes.length; i++) {
    for (let j = i + 1; j < spreadNodes.length; j++) {
      const d = Math.hypot(spreadNodes[i].x - spreadNodes[j].x, spreadNodes[i].y - spreadNodes[j].y);
      if (d < 160 && Math.random() < 0.45) {
        spreadEdges.push({ a: i, b: j, w: 0.3 + Math.random() * 0.7 });
      }
    }
  }
})();
document.getElementById('spread-decay').addEventListener('input', (e) => {
  document.getElementById('spread-decay-val').textContent = (parseInt(e.target.value) / 100).toFixed(2);
});
spreadCanvas.addEventListener('click', (e) => {
  const r = spreadCanvas.getBoundingClientRect();
  const mx = (e.clientX - r.left) * (spreadCanvas.width / r.width);
  const my = (e.clientY - r.top) * (spreadCanvas.height / r.height);
  let best = -1, bestD = 1e9;
  spreadNodes.forEach((n, i) => {
    const d = Math.hypot(n.x - mx, n.y - my);
    if (d < bestD && d < 25) { bestD = d; best = i; }
  });
  if (best >= 0) { spreadSeed = best; spreadRun(); }
});
function spreadRun() {
  spreadNodes.forEach(n => n.act = 0);
  if (spreadSeed < 0) return;
  const decay = parseInt(document.getElementById('spread-decay').value) / 100;
  const queue = [{ id: spreadSeed, act: 1 }];
  const visited = new Set();
  while (queue.length) {
    const { id, act } = queue.shift();
    if (visited.has(id)) continue;
    visited.add(id);
    spreadNodes[id].act = Math.max(spreadNodes[id].act, act);
    if (act < 0.12) continue;
    spreadEdges.forEach(e => {
      let other = -1;
      if (e.a === id) other = e.b;
      else if (e.b === id) other = e.a;
      if (other >= 0 && !visited.has(other)) {
        const nextAct = act * e.w * (1 - decay);
        if (nextAct > 0.08) queue.push({ id: other, act: nextAct });
      }
    });
  }
}
function spreadReset() { spreadSeed = -1; spreadNodes.forEach(n => n.act = 0); }
function drawSpread() {
  const W = 960, H = 440;
  spreadCtx.fillStyle = themeBg(); spreadCtx.fillRect(0, 0, W, H);
  if (spreadSeed >= 0) spreadRun();
  spreadEdges.forEach(e => {
    const a = spreadNodes[e.a], b = spreadNodes[e.b];
    const heat = (a.act + b.act) / 2;
    spreadCtx.strokeStyle = 'rgba(167,139,250,' + (0.08 + heat * 0.5).toFixed(3) + ')';
    spreadCtx.lineWidth = 0.5 + heat * 2;
    spreadCtx.beginPath(); spreadCtx.moveTo(a.x, a.y); spreadCtx.lineTo(b.x, b.y); spreadCtx.stroke();
  });
  let reached = 0;
  spreadNodes.forEach((n, i) => {
    const r = 6 + n.act * 14;
    const col = i === spreadSeed ? '251,191,36' : '167,139,250';
    spreadCtx.fillStyle = 'rgba(' + col + ',' + (0.25 + n.act * 0.7).toFixed(3) + ')';
    spreadCtx.beginPath(); spreadCtx.arc(n.x, n.y, r, 0, Math.PI * 2); spreadCtx.fill();
    spreadCtx.strokeStyle = 'rgba(' + col + ',' + (0.4 + n.act * 0.6).toFixed(3) + ')';
    spreadCtx.lineWidth = 1.2;
    spreadCtx.stroke();
    if (n.act > 0.15 && i !== spreadSeed) reached++;
  });
  document.getElementById('spread-reached').textContent = reached;
  if (spreadSeed < 0) {
    spreadCtx.fillStyle = '#666'; spreadCtx.font = '11px monospace'; spreadCtx.textAlign = 'center';
    spreadCtx.fillText('click any node to seed activation', W / 2, H - 20);
  }
  requestAnimationFrame(drawSpread);
}
drawSpread();

// ═══════════════════════════════════════════════════════════════════════
// Predictor + Residual
// ═══════════════════════════════════════════════════════════════════════
const residualCanvas = document.getElementById('residual-canvas');
const residualCtx = residualCanvas.getContext('2d');
const residualBufLen = 240;
let residualReal = new Array(residualBufLen).fill(0.5);
let residualFcast = new Array(residualBufLen).fill(0.5);
let residualT = 0, residualShockPending = 0, residualSpikes = 0;
document.getElementById('residual-prior').addEventListener('input', (e) => {
  document.getElementById('residual-prior-val').textContent = (parseInt(e.target.value) / 100).toFixed(2);
});
function residualShock() { residualShockPending = 40; }
function residualReset() {
  residualReal = new Array(residualBufLen).fill(0.5);
  residualFcast = new Array(residualBufLen).fill(0.5);
  residualT = 0; residualShockPending = 0; residualSpikes = 0;
  document.getElementById('residual-spikes').textContent = '0';
}
function drawResidual() {
  const W = 960, H = 320;
  residualCtx.fillStyle = themeBg(); residualCtx.fillRect(0, 0, W, H);
  residualT++;
  const slow = Math.sin(residualT * 0.035) * 0.2 + Math.sin(residualT * 0.013) * 0.08;
  let shock = 0;
  if (residualShockPending > 0) {
    shock = (Math.random() - 0.5) * 0.9 * Math.min(1, residualShockPending / 20);
    residualShockPending--;
  }
  const real = Math.max(0.02, Math.min(0.98, 0.5 + slow + (Math.random() - 0.5) * 0.03 + shock));
  const prior = parseInt(document.getElementById('residual-prior').value) / 100;
  const lastFc = residualFcast[residualFcast.length - 1];
  const gain = 1 - prior * 0.93;
  const fc = lastFc + (real - lastFc) * gain;
  residualReal.push(real); residualReal.shift();
  residualFcast.push(fc); residualFcast.shift();
  const resid = Math.abs(real - fc);
  if (resid > 0.1) {
    residualSpikes++;
    document.getElementById('residual-spikes').textContent = residualSpikes;
  }
  // Midline
  residualCtx.strokeStyle = 'rgba(167,139,250,0.12)'; residualCtx.lineWidth = 1;
  residualCtx.setLineDash([4, 4]);
  residualCtx.beginPath(); residualCtx.moveTo(0, H / 2); residualCtx.lineTo(W, H / 2); residualCtx.stroke();
  residualCtx.setLineDash([]);
  const stepX = W / residualBufLen;
  // Residual bars
  for (let i = 0; i < residualBufLen; i++) {
    const r = Math.abs(residualReal[i] - residualFcast[i]);
    if (r < 0.05) continue;
    const bar = Math.min(H * 0.4, r * H * 1.4);
    residualCtx.fillStyle = 'rgba(251,191,36,' + Math.min(0.8, r * 3).toFixed(3) + ')';
    residualCtx.fillRect(i * stepX, H - bar, Math.max(1, stepX), bar);
  }
  // Forecast
  residualCtx.strokeStyle = 'rgba(167,139,250,0.88)'; residualCtx.lineWidth = 2;
  residualCtx.beginPath();
  for (let i = 0; i < residualBufLen; i++) {
    const x = i * stepX, y = H - residualFcast[i] * H;
    if (i === 0) residualCtx.moveTo(x, y); else residualCtx.lineTo(x, y);
  }
  residualCtx.stroke();
  // Real
  residualCtx.strokeStyle = 'rgba(52,211,153,0.95)'; residualCtx.lineWidth = 2;
  residualCtx.beginPath();
  for (let i = 0; i < residualBufLen; i++) {
    const x = i * stepX, y = H - residualReal[i] * H;
    if (i === 0) residualCtx.moveTo(x, y); else residualCtx.lineTo(x, y);
  }
  residualCtx.stroke();
  // Legend
  residualCtx.font = '11px monospace'; residualCtx.textAlign = 'left';
  residualCtx.fillStyle = 'rgba(52,211,153,0.95)'; residualCtx.fillRect(W - 170, 14, 14, 2);
  residualCtx.fillStyle = '#aaa'; residualCtx.fillText('real', W - 150, 18);
  residualCtx.fillStyle = 'rgba(167,139,250,0.9)'; residualCtx.fillRect(W - 170, 30, 14, 2);
  residualCtx.fillStyle = '#aaa'; residualCtx.fillText('forecast', W - 150, 34);
  residualCtx.fillStyle = 'rgba(251,191,36,0.9)'; residualCtx.fillRect(W - 170, 46, 14, 2);
  residualCtx.fillStyle = '#aaa'; residualCtx.fillText('residual', W - 150, 50);
  requestAnimationFrame(drawResidual);
}
drawResidual();

// ═══════════════════════════════════════════════════════════════════════
// State Modulator
// ═══════════════════════════════════════════════════════════════════════
const modCanvas = document.getElementById('modulator-canvas');
const modCtx = modCanvas.getContext('2d');
const modNodes = [];
const modEdges = [];
(function modInit() {
  const W = 960, H = 360;
  for (let i = 0; i < 18; i++) {
    const a = (i / 18) * Math.PI * 2;
    const r = 120 + Math.random() * 30;
    modNodes.push({ x: W / 2 + Math.cos(a) * r, y: H / 2 + Math.sin(a) * r, valence: Math.random() * 2 - 1 });
  }
  for (let i = 0; i < modNodes.length; i++) {
    for (let j = i + 1; j < modNodes.length; j++) {
      if (Math.random() < 0.25) modEdges.push({ a: i, b: j, w: 0.3 + Math.random() * 0.6 });
    }
  }
})();
['mod-mood', 'mod-fatigue', 'mod-focus'].forEach(id => {
  document.getElementById(id).addEventListener('input', (e) => {
    document.getElementById(id + '-val').textContent = (parseInt(e.target.value) / 100).toFixed(2);
  });
});
function drawMod() {
  const W = 960, H = 360;
  modCtx.fillStyle = themeBg(); modCtx.fillRect(0, 0, W, H);
  const mood = parseInt(document.getElementById('mod-mood').value) / 100;
  const fatigue = parseInt(document.getElementById('mod-fatigue').value) / 100;
  const focus = parseInt(document.getElementById('mod-focus').value) / 100;
  // Edges modulated
  modEdges.forEach(e => {
    const a = modNodes[e.a], b = modNodes[e.b];
    const valence = (a.valence + b.valence) / 2;
    // Positive-valence edges boosted by mood, all edges damped by fatigue
    let effW = e.w * (1 + mood * 0.5 * Math.max(0, valence)) * (1 - fatigue * 0.6);
    // Focus narrows: only edges near the "spotlight" node (index 0) survive
    if (focus > 0.5) {
      const distA = Math.hypot(a.x - modNodes[0].x, a.y - modNodes[0].y);
      const distB = Math.hypot(b.x - modNodes[0].x, b.y - modNodes[0].y);
      const dist = Math.min(distA, distB);
      effW *= Math.max(0.1, 1 - (dist / 250) * focus);
    }
    const col = valence > 0 ? '52,211,153' : '251,191,36';
    modCtx.strokeStyle = 'rgba(' + col + ',' + (0.1 + effW * 0.55).toFixed(3) + ')';
    modCtx.lineWidth = 0.5 + effW * 2;
    modCtx.beginPath(); modCtx.moveTo(a.x, a.y); modCtx.lineTo(b.x, b.y); modCtx.stroke();
  });
  modNodes.forEach((n, i) => {
    const col = i === 0 && focus > 0.5 ? '251,191,36' : n.valence > 0 ? '52,211,153' : '167,139,250';
    const r = 7 + Math.abs(n.valence) * 5;
    modCtx.fillStyle = 'rgba(' + col + ',0.7)';
    modCtx.beginPath(); modCtx.arc(n.x, n.y, r, 0, Math.PI * 2); modCtx.fill();
    modCtx.strokeStyle = 'rgba(' + col + ',0.95)'; modCtx.lineWidth = 1.2; modCtx.stroke();
  });
  modCtx.fillStyle = '#aaa'; modCtx.font = '10px monospace'; modCtx.textAlign = 'left';
  modCtx.fillText('green edges = positive valence (boosted by mood)', 20, H - 40);
  modCtx.fillText('gold edges = negative valence (damped by mood)', 20, H - 26);
  modCtx.fillText('all edges damped by fatigue; focus narrows to spotlight node', 20, H - 12);
  requestAnimationFrame(drawMod);
}
drawMod();

// ═══════════════════════════════════════════════════════════════════════
// Mesh Dashboard
// ═══════════════════════════════════════════════════════════════════════
function meshFmtTime(t) { return new Date(t * 1000).toTimeString().slice(0, 8); }
function meshRender(items, elId, colorVar) {
  const log = document.getElementById(elId);
  if (!log) return;
  if (!items || !items.length) {
    log.innerHTML = '<span style="color:var(--dim)">no events yet…</span>';
    return;
  }
  log.innerHTML = items.slice().reverse().slice(0, 30).map(e => {
    const payload = JSON.stringify(e.payload || {}).replace(/</g, '&lt;');
    return '<div style="margin-bottom:3px">' +
      '<span style="color:var(--dim)">' + meshFmtTime(e.t) + '</span> ' +
      '<span style="color:' + colorVar + '">' + (e.type || 'event') + '</span>' +
      ' <span style="color:var(--dim)">' + payload + '</span></div>';
  }).join('');
}
async function meshPoll() {
  try {
    // Use /strata/pep-state as the canonical source since it cross-reads every sibling.
    const [stState, axEvents, lgEvents, atEvents, vcEvents, stEvents] = await Promise.all([
      fetch('/strata/pep-state'),
      fetch('/axona/events?limit=40'),
      fetch('/lingora/events?limit=40'),
      fetch('/atria/events?limit=40'),
      fetch('/vectora/events?limit=40'),
      fetch('/strata/events?limit=40'),
    ]);
    if (stState.ok) {
      const s = await stState.json();
      const lbl = document.getElementById('pep-link-label');
      const dot = document.getElementById('pep-link-dot');
      if (lbl) lbl.textContent = 'mesh: ' + (s.llm || '—') + ' · A' + (s.axona_events || 0) + ' · L' + (s.lingora_events || 0) + ' · T' + (s.atria_events || 0) + ' · V' + (s.vectora_events || 0) + ' · S' + (s.strata_events || 0);
      if (dot) dot.style.background = 'var(--accent2)';
      const set = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = v; };
      set('mesh-llm', s.llm || '—');
      set('mesh-emb', s.embeddings || '—');
      set('mesh-runs', s.runs_recent);
      if (s.latest_run) set('mesh-latest', (s.latest_run.id || '') + ' — ' + (s.latest_run.user_input || '').slice(0, 50));
      set('mesh-count-axona', s.axona_events || 0);
      set('mesh-count-lingora', s.lingora_events || 0);
      set('mesh-count-atria', s.atria_events || 0);
      set('mesh-count-vectora', s.vectora_events || 0);
      set('mesh-count-strata', s.strata_events || 0);
    }
    if (axEvents.ok) meshRender((await axEvents.json()).items || [], 'mesh-log-axona', 'var(--accent)');
    if (lgEvents.ok) meshRender((await lgEvents.json()).items || [], 'mesh-log-lingora', 'var(--accent2)');
    if (atEvents.ok) meshRender((await atEvents.json()).items || [], 'mesh-log-atria', 'var(--warn)');
    if (vcEvents.ok) meshRender((await vcEvents.json()).items || [], 'mesh-log-vectora', '#38bdf8');
    if (stEvents.ok) meshRender((await stEvents.json()).items || [], 'mesh-log-strata', '#e879f9');
  } catch (err) {
    const lbl = document.getElementById('pep-link-label');
    const dot = document.getElementById('pep-link-dot');
    if (lbl) lbl.textContent = 'mesh: offline';
    if (dot) dot.style.background = '#e53935';
  }
}
meshPoll();
setInterval(meshPoll, 2500);

</script>
</body>
</html>
"""


@router.get("/pep", response_class=HTMLResponse)
async def pep_home_page() -> str:
    return _PAGE
