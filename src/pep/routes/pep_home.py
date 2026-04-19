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
    <button onclick="downloadPep()" class="nav-btn">Download</button>
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
      <div class="tab" data-panel="novelty-tab">Novelty</div>
      <div class="tab" data-panel="modulator-tab">State Modulator</div>
      <div class="tab" data-panel="haze-tab">Opacity + Haze</div>
      <div class="tab" data-panel="mesh-tab">Mesh Dashboard</div>
      <div class="tab" data-panel="combinator-tab">Combinator</div>
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
      maps them onto language. Atria maps them onto matching. Vectora
      maps them onto data retrieval. Strata maps them onto markets. The
      engine is the same.
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

<!-- ═══ Novelty ═════════════════════════════════════════════════ -->
<div class="panel" id="novelty-tab">
<div class="container">
  <h2>Novelty — What PEP Thinks Is Worth Learning From</h2>
  <p class="desc">
    Novelty is not surprise alone. In PEP it's a structured signal compounded
    from three mismatches, gated by the Residual Scorer's threshold, and then
    combined with a forward-looking <em>trajectory</em> score before anything
    reaches memory. Surprising-but-irrelevant does not stick.
  </p>
  <div class="canvas-box">
    <canvas id="novelty-canvas" width="960" height="360"></canvas>
  </div>
  <div class="controls">
    <label style="display:flex;align-items:center;gap:8px">
      <span>entity_mismatch:</span>
      <input type="range" id="nv-em" min="0" max="100" value="60" style="width:100px">
      <span class="stat-val" id="nv-em-v">0.60</span>
    </label>
    <label style="display:flex;align-items:center;gap:8px">
      <span>ambiguity:</span>
      <input type="range" id="nv-am" min="0" max="100" value="35" style="width:100px">
      <span class="stat-val" id="nv-am-v">0.35</span>
    </label>
    <label style="display:flex;align-items:center;gap:8px">
      <span>intent_mismatch:</span>
      <input type="range" id="nv-im" min="0" max="100" value="25" style="width:100px">
      <span class="stat-val" id="nv-im-v">0.25</span>
    </label>
    <label style="display:flex;align-items:center;gap:8px">
      <span>state.novelty (curiosity):</span>
      <input type="range" id="nv-sn" min="0" max="100" value="20" style="width:100px">
      <span class="stat-val" id="nv-sn-v">0.20</span>
    </label>
    <label style="display:flex;align-items:center;gap:8px">
      <span>trajectory score:</span>
      <input type="range" id="nv-tr" min="0" max="100" value="55" style="width:100px">
      <span class="stat-val" id="nv-tr-v">0.55</span>
    </label>
    <button onclick="novEmit(false)">Emit event</button>
    <button onclick="novToggleAuto(this)">Autoplay</button>
    <span style="margin-left:auto;color:var(--dim)">
      stored: <b style="color:var(--accent2)" id="nv-stored">0</b> · seen: <b id="nv-seen">0</b>
    </span>
  </div>
  <div class="info">
    <b>What you are watching.</b> Three mismatches at the input — entities
    the predictor didn't expect (weight 0.5), interpretation ambiguity
    (0.3), intent mismatch (0.2) — weighted-sum into
    <b>novelty_score</b> (<code>core/residuals.py:38</code>). That crosses
    the first gate <code>θ·(1 − 0.4·state.novelty)</code>: high
    state.novelty (curiosity) lowers the bar. If it passes, the signal is
    compounded with a <em>forward-looking</em> trajectory score into
    <code>combined = 0.5·novelty + 0.5·trajectory</code>
    (<code>core/updater.py:382</code>). Only that survives to memory, with
    <b>brightness</b> scaling with <code>combined</code>. Novelty alone is
    not enough. Trajectory alone is not enough. Both gates must open.
    <br><br>
    <b>Why double-gated?</b> A hallucination-prone reward-maximizer chases
    surprise and stores it. PEP insists surprise <em>also</em> be
    future-useful — which is a PTO move: the transformation must leave the
    system in a better state for later turns, not just spike on the
    current one.
  </div>
  <div class="info">
    <b>The five facets of novelty.</b> The math playground's
    <a href="/math#novelty-growth">Novelty &amp; Growth</a> section
    introduces these; the engine implements the first and, via the gate,
    the fifth.<br><br>
    &bull; <b>Residual surprise.</b> <code>|observed − predicted|</code>.
    Large residual = worth storing. <em>This is what the Residual Scorer
    measures directly.</em><br>
    &bull; <b>Rarity.</b> What you rarely see carries more information per
    encounter than what you see often.<br>
    &bull; <b>Structural-hole / link-prediction.</b> A node that bridges
    previously-disconnected clusters scores highest in graph-theoretic
    novelty — bridging is harder than joining a hub.<br>
    &bull; <b>Compression / Kolmogorov.</b> Genuinely new means your
    current knowledge cannot compress it. Incompressible w.r.t. prior =
    truly novel.<br>
    &bull; <b>Adaptability.</b> Novelty that expands what-the-system-can-do
    is worth more than novelty that only changes what-the-system-has-seen.
    <em>This is the PTO link — novelty matters iff it moves capacity, and
    that is exactly what the combined gate enforces.</em>
  </div>
  <div class="info">
    <b>Where this matters in the suite.</b><br>
    &bull; <b>Axona</b> — novelty is one of four cognitive state-space
    dimensions (novelty / coherence / bandwidth / valence), used for
    quadrant detection (<code>pep.axona.core</code>).<br>
    &bull; <b>Vectora Watch</b> — streams items through a
    <code>novelty_component</code> to surface anomalies and new arrivals
    in retrieval streams.<br>
    &bull; <b>Lingora</b> — tracks lexical novelty for vocabulary
    constellation growth.<br>
    &bull; <b>Strata</b> — residual scoring surfaces unusual moves for
    market-regime detection.<br><br>
    <b>See also:</b>
    <a href="/math#novelty-growth">Math &rarr; Novelty &amp; Growth</a>,
    <a href="/axona">Axona &rarr; novelty quadrant</a>,
    <a href="/pto#haze-tab">PTO &rarr; Haze</a>
    (the mirror image: what counts as genuine loss).
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

<!-- ═══ Opacity + Haze ═══════════════════════════════════════════ -->
<div class="panel" id="haze-tab">
<div class="container">
  <h2>Opacity + Haze — The Forgetting Primitive</h2>
  <p class="desc">
    Every node carries an <em>opacity</em> in [0, 1] — its current encoding
    strength. Opacity decays exponentially toward a floor. When it drops
    below the reuse threshold the slot becomes available for overwriting.
    Forgetting is not a defect; it is the mechanism that makes finite
    capacity usable across a lifetime of experience.
  </p>
  <div class="canvas-box">
    <canvas id="haze-canvas" width="960" height="400"></canvas>
  </div>
  <div class="controls">
    <label style="display:flex;align-items:center;gap:8px">
      <span>time elapsed:</span>
      <input type="range" id="hz-time" min="0" max="120" value="0" style="width:140px">
      <span class="stat-val" id="hz-time-val">0 d</span>
    </label>
    <label style="display:flex;align-items:center;gap:8px">
      <span>half-life:</span>
      <input type="range" id="hz-halflife" min="2" max="60" value="14" style="width:100px">
      <span class="stat-val" id="hz-halflife-val">14 d</span>
    </label>
    <label style="display:flex;align-items:center;gap:8px">
      <span>reuse threshold:</span>
      <input type="range" id="hz-thresh" min="5" max="40" value="15" style="width:100px">
      <span class="stat-val" id="hz-thresh-val">0.15</span>
    </label>
    <button onclick="hzReinforce()">reinforce random</button>
    <button onclick="hzReset()">reset</button>
  </div>
  <div class="info">
    <b>What you are watching.</b> Twelve nodes, each encoded at a different
    time in the past with a different baseline strength. The top panel
    shows each node's decay curve over time; the dot marks <em>now</em>
    (the time slider). The bottom panel shows the current opacity state as
    a grid. Dashed red rings mark nodes below the reuse threshold — their
    slots can be reclaimed by new encoding.<br><br>
    <b>Math.</b> Effective opacity =
    <code>max(floor, base · 0.5<sup>(elapsed / half_life)</sup>)</code>.
    Reinforcement resets <code>elapsed</code> to zero and bumps
    <code>base</code> toward 1. Half-life is per-node in the real engine
    (episodic memories have longer half-lives than working memory); here
    it's a single slider for clarity.<br><br>
    <b>Why this is primitive #5 and not a refinement of #4.</b> State
    modulation rescales edge <em>gains</em> at runtime without changing
    what's stored. Haze changes what's <em>stored</em> — it's the only
    primitive that lets slots be reclaimed. Without it the graph is
    monotonically additive and capacity is unbounded, which is both
    biologically wrong and computationally expensive.<br><br>
    <b>Implementation:</b>
    <code>pep.vectora.Document</code> (opacity, encoded_at,
    half_life_seconds, reinforce, is_reusable),
    <code>pep.axona.haze_slope</code> (episodic nodes with reconstruction
    anchors + pre-clinical D_rec → D_irr detection).<br>
    <b>See also:</b>
    <a href="/axona#haze-tab">Axona → Memory Haze</a> (lifespan view with
    reminiscence bump),
    <a href="/lingora">Lingora → Vocabulary Learn</a> (spaced-repetition
    on top of haze),
    <a href="/vectora">Vectora</a> (opacity-gated document retrieval).
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

<!-- ═══ LAVAS Combinator ════════════════════════════════════════ -->
<div class="panel" id="combinator-tab">
<div class="container">
  <h2>LAVAS Combinator &mdash; Apps as Nodes, Ideas as Activation Paths</h2>
  <p class="desc">
    PEP eating its own dogfood. Nodes are primitives, substrates, pains,
    and populations. Edges are "applies to," "addresses," "serves,"
    "composes with." Pick a seed, spread activation, read the top-lit
    nodes across all four types: the combination is a candidate app.
    Short activation paths mean somebody already built it; long paths
    with a plausible chain mean you just invented something.
  </p>
  <div class="controls" style="flex-wrap:wrap;gap:8px;margin-bottom:14px">
    <span style="font-size:11px;color:var(--dim);letter-spacing:0.1em">SEED:</span>
    <select id="comb-seed" style="background:var(--surface);color:var(--text);border:1px solid var(--border);padding:4px 8px;border-radius:4px;font-family:inherit;font-size:12px"></select>
    <button onclick="combGenerate()">Generate</button>
    <button onclick="combRandom()">Random Seed</button>
    <button onclick="combClear()">Clear</button>
    <label style="display:flex;align-items:center;gap:6px;margin-left:8px">
      <span style="font-size:11px;color:var(--dim)">hops:</span>
      <input type="range" id="comb-hops" min="1" max="5" value="3" style="width:80px">
      <span class="stat-val" id="comb-hops-val">3</span>
    </label>
    <label style="display:flex;align-items:center;gap:6px">
      <span style="font-size:11px;color:var(--dim)">decay:</span>
      <input type="range" id="comb-decay" min="30" max="90" value="60" style="width:80px">
      <span class="stat-val" id="comb-decay-val">0.60</span>
    </label>
  </div>
  <div class="canvas-box">
    <canvas id="combinator-canvas" width="960" height="540"></canvas>
  </div>
  <div style="margin-top:14px;display:grid;grid-template-columns:1fr 1fr;gap:14px">
    <div id="comb-output" style="background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:14px 16px;min-height:180px">
      <div style="color:var(--dim);font-size:11px;letter-spacing:0.12em;margin-bottom:8px">CANDIDATE</div>
      <div style="color:var(--dim);font-size:12px;padding:30px 0;text-align:center">pick a seed and hit Generate</div>
    </div>
    <div id="comb-trace" style="background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:14px 16px;min-height:180px">
      <div style="color:var(--dim);font-size:11px;letter-spacing:0.12em;margin-bottom:8px">ACTIVATION TRACE</div>
      <div style="color:var(--dim);font-size:12px;padding:30px 0;text-align:center">&mdash;</div>
    </div>
  </div>
  <div class="info" style="margin-top:14px">
    <b>Node types.</b> <span style="color:#a78bfa">Primitives</span> (top)
    &mdash; the five PEP mechanisms.
    <span style="color:#4fc3f7">Substrates</span> (right) &mdash; what
    the primitives run on (language, people, docs, assets, cognition,
    plus subdomains).
    <span style="color:#f06292">Pains</span> (bottom) &mdash;
    real-world problems someone will pay to solve (drift, decay,
    mismatch, contradiction, regime-break, etc.).
    <span style="color:#81c784">Populations</span> (left) &mdash; who
    the resulting app is for (consumer, enterprise, clinical, creator,
    researcher, educator, trader, regulator).<br><br>
    <b>Reading the output.</b> The candidate panel composes the
    top-lit node from each category into a one-line product sketch:
    <em>apply [primitive] to [substrate] to address [pain] for
    [population]</em>. The activation trace panel shows the top-8 lit
    nodes with their activation values &mdash; this is the explanation
    for why the combinator picked that candidate. Long traces mean the
    primitive reached a substrate far from the seed; those are the
    non-obvious wedges.<br><br>
    <b>Cross-app composition.</b> Substrate nodes have edges to other
    substrates (language &harr; people, language &harr; assets,
    cognition &harr; people, docs &harr; assets, etc.). Those edges are
    the LAVAS-specific moat &mdash; combining two substrates produces a
    cross-app product that a single-substrate competitor can't
    replicate without building all five siblings first. Seed from one
    substrate, watch which other substrate lights up: that pair is a
    cross-app wedge.<br><br>
    <b>What to do with a hit.</b> Short path + familiar combination =
    existing product, skip. Long path + plausible chain = candidate
    vertical under the indicated app, or (if the substrate doesn't
    match any of the five existing apps) candidate new app.
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
    <b>5. Opacity + haze (the forgetting primitive).</b> Every node in
    the graph has an <em>opacity</em> &mdash; its current encoding strength
    in [0, 1] &mdash; that decays over time toward a floor. A node whose
    effective opacity drops below the reuse threshold becomes available
    for overwriting by new encoding. This is the mechanism that makes
    capacity finite and therefore usable: forgetting is not a defect of
    the system, it is the feature that lets the same physical slots
    carry different content at different times. Vivid memories are
    bright; old ones are hazy; the difference is not noise, it is
    reclaimed capacity.<br><br>
    Opacity is node-level state modulation at a slow timescale, so it is
    a refinement of primitive 4, not a separate fifth thing. But it is
    load-bearing enough to call out explicitly. See the
    <a href="#" onclick="document.querySelector('[data-panel=haze-tab]').click();return false">Opacity + Haze</a>
    tab for the live visualization,
    <a href="/axona#haze-tab">Axona &rarr; Memory Haze</a> for the lifespan
    view with reminiscence bump, and <code>pep.vectora.Document</code>
    for the concrete implementation (opacity + encoded_at +
    half_life_seconds + reinforce + is_reusable).
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
    &bull; <b>Vectora</b> treats documents as nodes and embedding/keyword/
    knowledge-graph relations as typed edges; spreading activation drives
    multi-hop retrieval, residual scoring drives anomaly surfacing, and
    state modulation drives context-aware retrieval.<br>
    &bull; <b>Strata</b> treats assets as nodes and correlations as edges;
    spreading activation drives momentum spillover, residual scoring
    drives unusual-move detection, and state modulation drives regime
    awareness. The Equities vertical is shipping at
    <code>~/projects/charlie_project/</code>.
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
function downloadPep() {
  const html = '<!DOCTYPE html>' + document.documentElement.outerHTML;
  const blob = new Blob([html], { type: 'text/html' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'pep-engine.html';
  document.body.appendChild(a); a.click(); document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

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
// Opacity + Haze  (mirrors pep.vectora.Document decay model)
// ═══════════════════════════════════════════════════════════════════════
const hzCanvas = document.getElementById('haze-canvas');
const hzCtx = hzCanvas.getContext('2d');
const HZ_LABELS = [
  'morning coffee', 'first kiss', 'birthday party', 'job interview',
  'final exam', 'concert', 'beach vacation', 'graduation',
  'grandma\u2019s kitchen', 'learning bike', 'grief', 'flow state',
];
const hzNodes = [];
(function hzInit() {
  for (let i = 0; i < HZ_LABELS.length; i++) {
    hzNodes.push({
      label: HZ_LABELS[i],
      encodedDaysAgo: Math.random() * 60,
      base: 0.8 + Math.random() * 0.2,
      floor: 0.02,
      reinforcedAt: null,
    });
  }
})();
function hzTime()     { return parseFloat(document.getElementById('hz-time').value); }
function hzHalfLife() { return parseFloat(document.getElementById('hz-halflife').value); }
function hzThresh()   { return parseFloat(document.getElementById('hz-thresh').value) / 100; }
function hzEffective(n, tNow) {
  const elapsed = Math.max(0, tNow + n.encodedDaysAgo);
  const op = n.base * Math.pow(0.5, elapsed / hzHalfLife());
  return Math.max(n.floor, op);
}
function hzReinforce() {
  const tNow = hzTime();
  const dim = hzNodes.filter(n => hzEffective(n, tNow) < 0.5);
  const pick = (dim.length ? dim : hzNodes)[Math.floor(Math.random() * (dim.length || hzNodes.length))];
  pick.encodedDaysAgo = -tNow;
  pick.base = 1.0;
  pick.reinforcedAt = Date.now();
}
function hzReset() {
  hzNodes.forEach(n => {
    n.encodedDaysAgo = Math.random() * 60;
    n.base = 0.8 + Math.random() * 0.2;
    n.reinforcedAt = null;
  });
  document.getElementById('hz-time').value = 0;
  document.getElementById('hz-time-val').textContent = '0 d';
}
[['hz-time','d'],['hz-halflife','d'],['hz-thresh',null]].forEach(([id,unit]) => {
  const el = document.getElementById(id);
  if (!el) return;
  el.addEventListener('input', (e) => {
    const v = parseFloat(e.target.value);
    const out = document.getElementById(id + '-val');
    if (!out) return;
    out.textContent = unit ? (v + ' ' + unit) : (v / 100).toFixed(2);
  });
});
function drawHaze() {
  const W = 960, H = 400;
  hzCtx.fillStyle = themeBg(); hzCtx.fillRect(0, 0, W, H);
  const tNow = hzTime();
  const hl = hzHalfLife();
  const thresh = hzThresh();
  // ── Top panel: decay curves ────────────────────────────────────────
  const topH = 180, topPadY = 20, topPadX = 60;
  const xMax = 120; // days
  const x2px = t => topPadX + (t / xMax) * (W - topPadX - 20);
  const y2px = op => topPadY + (1 - op) * (topH - topPadY - 10);
  // Axes
  hzCtx.strokeStyle = 'rgba(150,150,150,0.4)'; hzCtx.lineWidth = 1;
  hzCtx.beginPath(); hzCtx.moveTo(topPadX, topPadY); hzCtx.lineTo(topPadX, topH); hzCtx.lineTo(W - 20, topH); hzCtx.stroke();
  // Reuse threshold line
  hzCtx.strokeStyle = 'rgba(248, 113, 113, 0.5)'; hzCtx.setLineDash([4, 4]);
  hzCtx.beginPath(); hzCtx.moveTo(topPadX, y2px(thresh)); hzCtx.lineTo(W - 20, y2px(thresh)); hzCtx.stroke();
  hzCtx.setLineDash([]);
  hzCtx.fillStyle = 'rgba(248, 113, 113, 0.9)'; hzCtx.font = '10px monospace'; hzCtx.textAlign = 'left';
  hzCtx.fillText('reuse threshold = ' + thresh.toFixed(2), W - 180, y2px(thresh) - 4);
  // Axis labels
  hzCtx.fillStyle = '#aaa'; hzCtx.textAlign = 'right';
  hzCtx.fillText('1.0', topPadX - 6, topPadY + 4);
  hzCtx.fillText('0.0', topPadX - 6, topH + 4);
  hzCtx.textAlign = 'center';
  hzCtx.fillText('0', topPadX, topH + 14);
  hzCtx.fillText('60 d', x2px(60), topH + 14);
  hzCtx.fillText('120 d', x2px(120), topH + 14);
  hzCtx.textAlign = 'left';
  hzCtx.fillText('opacity', 8, topPadY + 8);
  hzCtx.fillText('elapsed (days, t=0 at encoding)', W - 220, topH + 14);
  // Curves (plot each node from its encoding up to 120d)
  hzNodes.forEach((n, i) => {
    const hue = (i * 31) % 360;
    hzCtx.strokeStyle = `hsla(${hue}, 65%, 65%, 0.65)`;
    hzCtx.lineWidth = 1.2;
    hzCtx.beginPath();
    for (let t = 0; t <= xMax; t += 2) {
      const op = Math.max(n.floor, n.base * Math.pow(0.5, t / hl));
      const px = x2px(t), py = y2px(op);
      if (t === 0) hzCtx.moveTo(px, py); else hzCtx.lineTo(px, py);
    }
    hzCtx.stroke();
    // Now-dot: shows current opacity at (encodedDaysAgo + tNow)
    const nowElapsed = Math.max(0, tNow + n.encodedDaysAgo);
    if (nowElapsed <= xMax) {
      const op = hzEffective(n, tNow);
      hzCtx.fillStyle = `hsla(${hue}, 70%, 70%, 0.95)`;
      hzCtx.beginPath(); hzCtx.arc(x2px(nowElapsed), y2px(op), 3.5, 0, Math.PI * 2); hzCtx.fill();
    }
  });
  // ── Bottom panel: grid of current state ────────────────────────────
  const gridTop = topH + 40;
  hzCtx.fillStyle = '#aaa'; hzCtx.font = '10px monospace'; hzCtx.textAlign = 'left';
  hzCtx.fillText('current opacity state (dashed red = below reuse threshold, reclaimable)', 20, gridTop - 10);
  let reusable = 0;
  const cols = 6, cellW = (W - 40) / cols, cellH = 80;
  hzNodes.forEach((n, i) => {
    const c = i % cols, r = Math.floor(i / cols);
    const cx = 20 + c * cellW + cellW / 2;
    const cy = gridTop + r * cellH + cellH / 2;
    const op = hzEffective(n, tNow);
    const isReuse = op < thresh;
    if (isReuse) reusable++;
    const radius = 16 + op * 14;
    hzCtx.fillStyle = `rgba(186, 104, 200, ${op.toFixed(3)})`;
    hzCtx.beginPath(); hzCtx.arc(cx, cy, radius, 0, Math.PI * 2); hzCtx.fill();
    if (n.reinforcedAt && Date.now() - n.reinforcedAt < 1200) {
      const age = (Date.now() - n.reinforcedAt) / 1200;
      hzCtx.strokeStyle = `rgba(163, 230, 53, ${(1 - age).toFixed(3)})`;
      hzCtx.lineWidth = 2;
      hzCtx.beginPath(); hzCtx.arc(cx, cy, radius + 6 + age * 16, 0, Math.PI * 2); hzCtx.stroke();
    }
    if (isReuse) {
      hzCtx.strokeStyle = 'rgba(248, 113, 113, 0.85)';
      hzCtx.lineWidth = 1.5; hzCtx.setLineDash([4, 3]);
      hzCtx.beginPath(); hzCtx.arc(cx, cy, radius + 4, 0, Math.PI * 2); hzCtx.stroke();
      hzCtx.setLineDash([]);
    } else {
      hzCtx.strokeStyle = `rgba(186, 104, 200, ${Math.min(1, op + 0.2).toFixed(3)})`;
      hzCtx.lineWidth = 1; hzCtx.beginPath(); hzCtx.arc(cx, cy, radius, 0, Math.PI * 2); hzCtx.stroke();
    }
    hzCtx.fillStyle = `rgba(230, 230, 230, ${Math.max(0.45, op).toFixed(3)})`;
    hzCtx.font = 'bold 10px monospace'; hzCtx.textAlign = 'center';
    hzCtx.fillText(op.toFixed(2), cx, cy + 3);
    hzCtx.fillStyle = `rgba(200, 200, 200, ${Math.max(0.5, op).toFixed(3)})`;
    hzCtx.font = '10px monospace';
    hzCtx.fillText(n.label, cx, cy + radius + 14);
  });
  // Footer
  hzCtx.textAlign = 'left'; hzCtx.fillStyle = '#aaa'; hzCtx.font = '11px monospace';
  hzCtx.fillText(`t = +${tNow.toFixed(0)} d · half-life = ${hl.toFixed(0)} d`, 20, H - 8);
  hzCtx.textAlign = 'right';
  hzCtx.fillStyle = reusable > 0 ? '#f06292' : '#81c784';
  hzCtx.fillText(`${reusable} / ${hzNodes.length} slots reclaimable`, W - 20, H - 8);
  requestAnimationFrame(drawHaze);
}
drawHaze();

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

// ═══════════════════════════════════════════════════════════════════════
// Novelty  (core/residuals.py + core/updater.py mirrored in the browser)
// ═══════════════════════════════════════════════════════════════════════
const novCanvas = document.getElementById('novelty-canvas');
const novCtx = novCanvas.getContext('2d');
const NV_THETA = 0.45;           // core/residuals.py: DEFAULT_STORE_THRESHOLD
const NV_COMBINED_GATE = 0.35;   // core/updater.py: TRAJECTORY_GATE (PTO 2G)
const NV_HISTORY_MAX = 36;
let novHistory = [];
let novAutoHandle = null;
let novSeen = 0, novStored = 0;

function novReadSliders() {
  const em = parseInt(document.getElementById('nv-em').value, 10) / 100;
  const am = parseInt(document.getElementById('nv-am').value, 10) / 100;
  const im = parseInt(document.getElementById('nv-im').value, 10) / 100;
  const sn = parseInt(document.getElementById('nv-sn').value, 10) / 100;
  const tr = parseInt(document.getElementById('nv-tr').value, 10) / 100;
  document.getElementById('nv-em-v').textContent = em.toFixed(2);
  document.getElementById('nv-am-v').textContent = am.toFixed(2);
  document.getElementById('nv-im-v').textContent = im.toFixed(2);
  document.getElementById('nv-sn-v').textContent = sn.toFixed(2);
  document.getElementById('nv-tr-v').textContent = tr.toFixed(2);
  return { em, am, im, sn, tr };
}
function novCompute(em, am, im, sn, tr) {
  const novelty = 0.5 * em + 0.3 * am + 0.2 * im;
  const effTh = NV_THETA * (1 - 0.4 * sn);
  const resPass = novelty >= effTh;
  const combined = 0.5 * novelty + 0.5 * tr;
  const passGate = resPass && combined >= NV_COMBINED_GATE;
  const brightness = passGate ? Math.min(1.0, 0.3 + 0.7 * combined) : 0;
  return { novelty, effTh, resPass, combined, passGate, brightness };
}
function novEmit(noisy) {
  const s = novReadSliders();
  const j = (v) => Math.max(0, Math.min(1, v + (Math.random() - 0.5) * 0.25));
  const sam = noisy
    ? { em: j(s.em), am: j(s.am), im: j(s.im), sn: s.sn, tr: j(s.tr) }
    : s;
  const c = novCompute(sam.em, sam.am, sam.im, sam.sn, sam.tr);
  novHistory.push({ novelty: c.novelty, combined: c.combined, stored: c.passGate, brightness: c.brightness });
  if (novHistory.length > NV_HISTORY_MAX) novHistory.shift();
  novSeen++;
  if (c.passGate) novStored++;
  document.getElementById('nv-seen').textContent = novSeen;
  document.getElementById('nv-stored').textContent = novStored;
}
function novToggleAuto(btn) {
  if (novAutoHandle) {
    clearInterval(novAutoHandle); novAutoHandle = null;
    btn.textContent = 'Autoplay';
  } else {
    novAutoHandle = setInterval(() => novEmit(true), 450);
    btn.textContent = 'Stop';
  }
}

function drawNovelty() {
  const W = 960, H = 360;
  novCtx.fillStyle = themeBg(); novCtx.fillRect(0, 0, W, H);
  const s = novReadSliders();
  const c = novCompute(s.em, s.am, s.im, s.sn, s.tr);

  const accent  = 'rgba(167,139,250,0.92)';
  const accent2 = 'rgba(52,211,153,0.92)';
  const warn    = 'rgba(251,191,36,0.92)';
  const danger  = 'rgba(248,113,113,0.9)';
  const track   = 'rgba(255,255,255,0.07)';
  const dim     = '#888';
  const text    = '#bbb';

  novCtx.font = '11px monospace';
  novCtx.textAlign = 'left';

  // ── Row 1: three input components ─────────────────────────────────
  novCtx.fillStyle = dim;
  novCtx.fillText('1 · residual components', 20, 22);
  const comps = [
    { label: 'entity_mismatch  (×0.5)', val: s.em, color: accent },
    { label: 'ambiguity         (×0.3)', val: s.am, color: warn },
    { label: 'intent_mismatch  (×0.2)', val: s.im, color: accent2 },
  ];
  const r1y = 34, rowH = 16;
  comps.forEach((cc, i) => {
    const y = r1y + i * (rowH + 8);
    novCtx.fillStyle = text; novCtx.fillText(cc.label, 20, y + 12);
    const bx = 230, bw = 280;
    novCtx.fillStyle = track; novCtx.fillRect(bx, y, bw, rowH);
    novCtx.fillStyle = cc.color; novCtx.fillRect(bx, y, bw * cc.val, rowH);
    novCtx.fillStyle = text; novCtx.fillText(cc.val.toFixed(2), bx + bw + 10, y + 12);
  });

  // Σ arrow
  const arrowY = r1y + rowH + 8 + rowH / 2;
  novCtx.strokeStyle = dim; novCtx.lineWidth = 1.5;
  novCtx.beginPath(); novCtx.moveTo(575, arrowY); novCtx.lineTo(612, arrowY); novCtx.stroke();
  novCtx.beginPath(); novCtx.moveTo(607, arrowY - 4); novCtx.lineTo(612, arrowY); novCtx.lineTo(607, arrowY + 4); novCtx.stroke();
  novCtx.fillStyle = dim; novCtx.textAlign = 'center';
  novCtx.fillText('Σ', 593, arrowY - 6);

  // novelty_score bar (right of Σ)
  novCtx.textAlign = 'left';
  const nsx = 620, nsy = arrowY - rowH / 2, nsw = 280, nsh = rowH;
  novCtx.fillStyle = track; novCtx.fillRect(nsx, nsy, nsw, nsh);
  novCtx.fillStyle = c.resPass ? accent2 : danger;
  novCtx.fillRect(nsx, nsy, nsw * c.novelty, nsh);
  // threshold tick
  const tx = nsx + nsw * c.effTh;
  novCtx.strokeStyle = warn; novCtx.lineWidth = 2;
  novCtx.beginPath(); novCtx.moveTo(tx, nsy - 5); novCtx.lineTo(tx, nsy + nsh + 5); novCtx.stroke();
  novCtx.fillStyle = warn; novCtx.font = '10px monospace'; novCtx.textAlign = 'center';
  novCtx.fillText('θ·(1−0.4·sn) = ' + c.effTh.toFixed(2), tx, nsy - 9);
  novCtx.font = '11px monospace'; novCtx.fillStyle = text; novCtx.textAlign = 'left';
  novCtx.fillText(
    'novelty_score = ' + c.novelty.toFixed(2) +
    (c.resPass ? '   ✓ passes residual gate' : '   ✗ below gate — discarded'),
    nsx, nsy + nsh + 22
  );

  // ── Row 2: novelty + trajectory → combined ────────────────────────
  const r2y = 160;
  novCtx.fillStyle = dim; novCtx.fillText('2 · combine with trajectory score (PTO 2G gate)', 20, r2y);
  const splitX = 230, splitW = 280, splitY = r2y + 12;
  // left half: ½·novelty
  novCtx.fillStyle = track; novCtx.fillRect(splitX, splitY, splitW, rowH);
  novCtx.fillStyle = accent;
  novCtx.fillRect(splitX, splitY, (splitW / 2) * c.novelty, rowH);
  // right half: ½·trajectory
  novCtx.fillStyle = warn;
  novCtx.fillRect(splitX + splitW / 2, splitY, (splitW / 2) * s.tr, rowH);
  // divider
  novCtx.strokeStyle = 'rgba(255,255,255,0.15)';
  novCtx.beginPath(); novCtx.moveTo(splitX + splitW / 2, splitY); novCtx.lineTo(splitX + splitW / 2, splitY + rowH); novCtx.stroke();
  novCtx.fillStyle = dim; novCtx.font = '10px monospace'; novCtx.textAlign = 'center';
  novCtx.fillText('½ · novelty', splitX + splitW / 4, splitY - 4);
  novCtx.fillText('½ · trajectory', splitX + 3 * splitW / 4, splitY - 4);

  // Σ arrow again
  novCtx.strokeStyle = dim; novCtx.lineWidth = 1.5;
  const a2y = splitY + rowH / 2;
  novCtx.beginPath(); novCtx.moveTo(575, a2y); novCtx.lineTo(612, a2y); novCtx.stroke();
  novCtx.beginPath(); novCtx.moveTo(607, a2y - 4); novCtx.lineTo(612, a2y); novCtx.lineTo(607, a2y + 4); novCtx.stroke();

  // combined bar
  const cx = 620, cy = splitY, cw = 280;
  novCtx.fillStyle = track; novCtx.fillRect(cx, cy, cw, rowH);
  novCtx.fillStyle = c.passGate ? accent2 : danger;
  novCtx.fillRect(cx, cy, cw * c.combined, rowH);
  const gx = cx + cw * NV_COMBINED_GATE;
  novCtx.strokeStyle = warn; novCtx.lineWidth = 2;
  novCtx.beginPath(); novCtx.moveTo(gx, cy - 5); novCtx.lineTo(gx, cy + rowH + 5); novCtx.stroke();
  novCtx.fillStyle = warn; novCtx.font = '10px monospace'; novCtx.textAlign = 'center';
  novCtx.fillText('combined gate = ' + NV_COMBINED_GATE.toFixed(2), gx, cy - 9);
  novCtx.font = '11px monospace'; novCtx.fillStyle = text; novCtx.textAlign = 'left';
  const verdict = c.passGate
    ? '   ✓ STORE   (brightness ' + c.brightness.toFixed(2) + ')'
    : (c.resPass ? '   ✗ combined too low — discard'
                 : '   ✗ already rejected at residual gate');
  novCtx.fillText('combined = ' + c.combined.toFixed(2) + verdict, cx, cy + rowH + 22);

  // ── Row 3: outcome (memory node) ──────────────────────────────────
  const r3y = 235;
  novCtx.fillStyle = dim; novCtx.fillText('3 · memory persist', 20, r3y);
  // animated disc on the right
  const dx = 830, dy = r3y + 26, dr = 22;
  if (c.passGate) {
    const b = c.brightness;
    novCtx.fillStyle = 'rgba(52,211,153,' + (0.15 + b * 0.65).toFixed(3) + ')';
    novCtx.beginPath(); novCtx.arc(dx, dy, dr, 0, Math.PI * 2); novCtx.fill();
    novCtx.strokeStyle = accent2; novCtx.lineWidth = 2;
    novCtx.stroke();
    novCtx.fillStyle = text; novCtx.textAlign = 'center';
    novCtx.fillText('stored', dx, dy + 3);
    novCtx.fillStyle = dim; novCtx.font = '10px monospace';
    novCtx.fillText('brightness ' + b.toFixed(2), dx, dy + 40);
  } else {
    novCtx.strokeStyle = danger; novCtx.lineWidth = 2;
    novCtx.setLineDash([4, 4]);
    novCtx.beginPath(); novCtx.arc(dx, dy, dr, 0, Math.PI * 2); novCtx.stroke();
    novCtx.setLineDash([]);
    novCtx.fillStyle = dim; novCtx.textAlign = 'center';
    novCtx.fillText('discard', dx, dy + 3);
    novCtx.font = '10px monospace';
    novCtx.fillText('no persist', dx, dy + 40);
  }
  // formula block
  novCtx.textAlign = 'left'; novCtx.font = '11px monospace'; novCtx.fillStyle = text;
  const fx = 230, fy = r3y + 18;
  novCtx.fillText('brightness = min(1.0, 0.3 + 0.7 · combined)', fx, fy);
  novCtx.fillStyle = dim; novCtx.font = '10px monospace';
  novCtx.fillText('core/updater.py:408-410', fx, fy + 18);
  novCtx.fillText('surprising AND future-relevant → bright memory; otherwise dim or dropped.', fx, fy + 34);

  // ── Row 4: event history strip ────────────────────────────────────
  const stripTop = 304, stripH = 40;
  novCtx.fillStyle = dim; novCtx.font = '10px monospace'; novCtx.textAlign = 'left';
  novCtx.fillText('emitted events (last ' + NV_HISTORY_MAX + ')', 20, stripTop - 2);
  novCtx.strokeStyle = 'rgba(255,255,255,0.07)'; novCtx.lineWidth = 1;
  novCtx.beginPath(); novCtx.moveTo(20, stripTop + stripH); novCtx.lineTo(W - 20, stripTop + stripH); novCtx.stroke();
  const col = (W - 40) / NV_HISTORY_MAX;
  novHistory.forEach((ev, i) => {
    const x = 20 + i * col + col / 2;
    // y maps novelty in [0,1] to stripTop..stripTop+stripH
    const y = stripTop + (1 - Math.min(1, ev.novelty)) * stripH;
    novCtx.fillStyle = ev.stored ? 'rgba(52,211,153,0.92)' : 'rgba(136,136,136,0.5)';
    novCtx.beginPath(); novCtx.arc(x, y, ev.stored ? 4.5 : 3.2, 0, Math.PI * 2); novCtx.fill();
  });
  // legend on strip
  novCtx.fillStyle = accent2; novCtx.beginPath(); novCtx.arc(W - 150, stripTop - 6, 4, 0, Math.PI * 2); novCtx.fill();
  novCtx.fillStyle = dim; novCtx.fillText('stored', W - 140, stripTop - 3);
  novCtx.fillStyle = 'rgba(136,136,136,0.5)'; novCtx.beginPath(); novCtx.arc(W - 90, stripTop - 6, 3.2, 0, Math.PI * 2); novCtx.fill();
  novCtx.fillStyle = dim; novCtx.fillText('discarded', W - 80, stripTop - 3);

  requestAnimationFrame(drawNovelty);
}
drawNovelty();

// ═══════════════════════════════════════════════════════════════════════
// LAVAS Combinator — nodes = {primitives, substrates, pains, populations}
//                   edges = applies-to / addresses / serves / composes
//                   mechanic = spreading activation on the meta-graph
// ═══════════════════════════════════════════════════════════════════════
const COMB_NODES = [
  // ── Primitives ──────────────────────────────────────────────────────
  { id: 'graph',    type: 'primitive',  label: 'Graph',     short: 'graph-native',     desc: 'weighted node + edge substrate' },
  { id: 'spread',   type: 'primitive',  label: 'Spread',    short: 'spread-activation', desc: 'radiate from a seed with decay' },
  { id: 'predict',  type: 'primitive',  label: 'Predict',   short: 'predictor+residual', desc: 'forecast vs reality as learning signal' },
  { id: 'modulate', type: 'primitive',  label: 'Modulate',  short: 'state-modulated',  desc: 'slow-timescale runtime gain control' },
  { id: 'haze',     type: 'primitive',  label: 'Haze',      short: 'haze-governed',    desc: 'opacity decay + slot reclamation' },
  // ── Substrates ──────────────────────────────────────────────────────
  { id: 'language',  type: 'substrate', label: 'Language',  desc: 'words, sentences, discourse' },
  { id: 'code',      type: 'substrate', label: 'Code',      desc: 'program text, functions, APIs' },
  { id: 'legal',     type: 'substrate', label: 'Legal',     desc: 'contracts, clauses, case law' },
  { id: 'medical',   type: 'substrate', label: 'Medical',   desc: 'records, literature, protocols' },
  { id: 'people',    type: 'substrate', label: 'People',    desc: 'individuals + compatibility dims' },
  { id: 'teams',     type: 'substrate', label: 'Teams',     desc: 'n-person groups, complementarity' },
  { id: 'mentors',   type: 'substrate', label: 'Mentors',   desc: 'asymmetric relationships' },
  { id: 'docs',      type: 'substrate', label: 'Documents', desc: 'corpus, knowledge base, archive' },
  { id: 'assets',    type: 'substrate', label: 'Assets',    desc: 'securities, commodities, crypto' },
  { id: 'narrative', type: 'substrate', label: 'Narrative', desc: 'news flow, story propagation' },
  { id: 'cognition', type: 'substrate', label: 'Cognition', desc: 'attention, mood, arousal' },
  { id: 'memory',    type: 'substrate', label: 'Memory',    desc: 'episodic traces, engrams' },
  { id: 'organizations', type: 'substrate', label: 'Organizations', desc: 'institutions as graphs' },
  { id: 'creative',  type: 'substrate', label: 'Creative',  desc: 'music, images, prose, poetry' },
  // ── Pains ──────────────────────────────────────────────────────────
  { id: 'drift',            type: 'pain', label: 'Drift',            desc: 'register/persona/voice wandering across time' },
  { id: 'mismatch',         type: 'pain', label: 'Mismatch',         desc: 'compatibility gap nobody models' },
  { id: 'decay',            type: 'pain', label: 'Decay',            desc: 'content / signal / skill going stale' },
  { id: 'contradiction',    type: 'pain', label: 'Contradiction',    desc: 'two sources disagree, nobody flags it' },
  { id: 'permission_leak',  type: 'pain', label: 'Permission Leak',  desc: 'surfaced content shouldn\u2019t have been visible' },
  { id: 'regime_break',     type: 'pain', label: 'Regime Break',     desc: 'correlations / context change, models stale' },
  { id: 'narrative_lag',    type: 'pain', label: 'Narrative Lag',    desc: 'story moves before fundamentals catch up' },
  { id: 'attention_drain',  type: 'pain', label: 'Attention Drain',  desc: 'burnout, fatigue, depletion' },
  { id: 'asymmetry',        type: 'pain', label: 'Asymmetry',        desc: '"A works for B" \u2260 "B works for A"' },
  { id: 'overfit',          type: 'pain', label: 'Overfit',          desc: 'strategies / profiles calcified on old data' },
  { id: 'interference',     type: 'pain', label: 'Interference',     desc: 'signal buried under correlated noise' },
  { id: 'translation_loss', type: 'pain', label: 'Translation Loss', desc: 'pragmatic / cultural meaning flattened' },
  { id: 'trauma',           type: 'pain', label: 'Trauma Persistence', desc: 'haze failing on specific traces (PTSD)' },
  { id: 'surprise_miss',    type: 'pain', label: 'Surprise Miss',    desc: 'anomaly not caught in time' },
  // ── Populations ────────────────────────────────────────────────────
  { id: 'consumer',   type: 'population', label: 'Consumer',   desc: 'B2C, mass market' },
  { id: 'enterprise', type: 'population', label: 'Enterprise', desc: 'B2B, ops + knowledge work' },
  { id: 'clinical',   type: 'population', label: 'Clinical',   desc: 'therapists, doctors, patients' },
  { id: 'creator',    type: 'population', label: 'Creator',    desc: 'writers, artists, filmmakers' },
  { id: 'researcher', type: 'population', label: 'Researcher', desc: 'scientists, academics' },
  { id: 'educator',   type: 'population', label: 'Educator',   desc: 'teachers, tutors, coaches' },
  { id: 'trader',     type: 'population', label: 'Trader',     desc: 'quant, retail, PM, allocator' },
  { id: 'regulator',  type: 'population', label: 'Regulator',  desc: 'compliance, legal, oversight' },
];
const COMB_EDGES = [
  // ── primitive → substrate  (applies to) ─────────────────────────────
  ['graph','people',0.9],['graph','docs',0.85],['graph','assets',0.85],['graph','teams',0.9],['graph','mentors',0.9],['graph','organizations',0.85],['graph','cognition',0.7],['graph','language',0.8],
  ['spread','language',0.9],['spread','cognition',0.95],['spread','narrative',0.95],['spread','memory',0.8],['spread','assets',0.8],['spread','docs',0.85],['spread','people',0.75],
  ['predict','language',0.85],['predict','assets',0.95],['predict','cognition',0.9],['predict','code',0.75],['predict','narrative',0.85],['predict','medical',0.75],
  ['modulate','language',0.9],['modulate','cognition',0.95],['modulate','assets',0.85],['modulate','people',0.8],['modulate','creative',0.8],['modulate','docs',0.75],
  ['haze','docs',0.95],['haze','cognition',0.95],['haze','memory',0.95],['haze','assets',0.8],['haze','organizations',0.85],['haze','mentors',0.75],['haze','people',0.75],
  // ── primitive → pain  (addresses) ───────────────────────────────────
  ['graph','mismatch',0.9],['graph','contradiction',0.7],['graph','asymmetry',0.85],
  ['spread','narrative_lag',0.95],['spread','attention_drain',0.7],['spread','interference',0.7],['spread','surprise_miss',0.75],
  ['predict','surprise_miss',0.95],['predict','regime_break',0.9],['predict','narrative_lag',0.8],['predict','decay',0.6],
  ['modulate','drift',0.95],['modulate','regime_break',0.9],['modulate','permission_leak',0.85],['modulate','translation_loss',0.9],
  ['haze','decay',0.95],['haze','overfit',0.9],['haze','trauma',0.95],['haze','interference',0.8],['haze','contradiction',0.6],
  // ── substrate → population  (serves) ────────────────────────────────
  ['language','consumer',0.85],['language','creator',0.9],['language','educator',0.85],['language','enterprise',0.7],
  ['code','enterprise',0.9],['code','creator',0.7],
  ['legal','enterprise',0.95],['legal','regulator',0.95],
  ['medical','clinical',0.95],['medical','researcher',0.85],
  ['people','consumer',0.95],['people','enterprise',0.85],['people','clinical',0.8],
  ['teams','enterprise',0.95],
  ['mentors','educator',0.9],['mentors','clinical',0.75],['mentors','enterprise',0.7],
  ['docs','enterprise',0.95],['docs','researcher',0.9],['docs','regulator',0.85],['docs','educator',0.75],
  ['assets','trader',0.95],['assets','enterprise',0.7],['assets','regulator',0.75],
  ['narrative','trader',0.9],['narrative','creator',0.85],['narrative','researcher',0.75],
  ['cognition','clinical',0.9],['cognition','consumer',0.85],['cognition','creator',0.8],['cognition','educator',0.8],
  ['memory','clinical',0.85],['memory','educator',0.85],['memory','consumer',0.7],
  ['organizations','enterprise',0.95],['organizations','regulator',0.85],['organizations','researcher',0.7],
  ['creative','creator',0.95],['creative','consumer',0.8],['creative','educator',0.7],
  // ── substrate ↔ substrate  (composes with — the cross-app wedges) ──
  ['language','people',0.7],['language','docs',0.7],['language','assets',0.65],['language','cognition',0.75],['language','creative',0.8],['language','legal',0.7],['language','medical',0.65],
  ['cognition','people',0.7],['cognition','memory',0.85],['cognition','language',0.75],['cognition','creative',0.65],
  ['docs','assets',0.6],['docs','legal',0.75],['docs','medical',0.75],['docs','code',0.7],['docs','organizations',0.7],
  ['people','teams',0.9],['people','mentors',0.9],['people','organizations',0.7],
  ['assets','narrative',0.85],
];
// Build adjacency
const COMB_ADJ = {};
COMB_NODES.forEach(n => { COMB_ADJ[n.id] = []; });
COMB_EDGES.forEach(e => {
  COMB_ADJ[e[0]].push({to: e[1], w: e[2]});
  COMB_ADJ[e[1]].push({to: e[0], w: e[2]});
});
// Lay out nodes: four arcs by type
(function combLayout() {
  const cx = 480, cy = 270, r = 220;
  const byType = {primitive: [], substrate: [], pain: [], population: []};
  COMB_NODES.forEach(n => byType[n.type].push(n));
  // Primitives: top arc, angle from 240° to 300° (top of circle)
  const arcs = {
    primitive:  { start: -Math.PI * 5 / 6,  end: -Math.PI / 6,          rr: r * 0.55 },
    substrate:  { start: -Math.PI / 4,      end: Math.PI / 2 + Math.PI / 6, rr: r * 1.05 },
    pain:       { start: Math.PI / 2 + Math.PI / 6, end: Math.PI + Math.PI / 3, rr: r * 1.05 },
    population: { start: Math.PI + Math.PI / 3, end: 2 * Math.PI - Math.PI / 4, rr: r * 0.75 },
  };
  Object.keys(arcs).forEach(t => {
    const a = arcs[t]; const list = byType[t]; const n = list.length;
    list.forEach((node, i) => {
      const frac = n === 1 ? 0.5 : i / (n - 1);
      const theta = a.start + frac * (a.end - a.start);
      node.x = cx + Math.cos(theta) * a.rr;
      node.y = cy + Math.sin(theta) * a.rr;
    });
  });
})();
// Populate seed dropdown
(function combPopulateSeed() {
  const sel = document.getElementById('comb-seed');
  if (!sel) return;
  const groups = [
    ['Pain points', 'pain'],
    ['Substrates',  'substrate'],
    ['Primitives',  'primitive'],
    ['Populations', 'population'],
  ];
  groups.forEach(([label, t]) => {
    const og = document.createElement('optgroup'); og.label = label;
    COMB_NODES.filter(n => n.type === t).forEach(n => {
      const opt = document.createElement('option');
      opt.value = n.id; opt.textContent = n.label;
      og.appendChild(opt);
    });
    sel.appendChild(og);
  });
  sel.value = 'decay';
})();
['comb-hops', 'comb-decay'].forEach(id => {
  const el = document.getElementById(id);
  if (!el) return;
  el.addEventListener('input', (e) => {
    const v = parseInt(e.target.value, 10);
    const out = document.getElementById(id + '-val');
    if (!out) return;
    out.textContent = id === 'comb-decay' ? (v / 100).toFixed(2) : String(v);
  });
});
let combActivation = {}; let combSeedId = null; let combResult = null;
function combSpread(seedId) {
  const hops = parseInt(document.getElementById('comb-hops').value, 10);
  const decay = parseInt(document.getElementById('comb-decay').value, 10) / 100;
  const act = {}; act[seedId] = 1.0;
  for (let h = 0; h < hops; h++) {
    const next = Object.assign({}, act);
    Object.keys(act).forEach(id => {
      const base = act[id];
      (COMB_ADJ[id] || []).forEach(nb => {
        const contribution = base * nb.w * decay;
        if (!next[nb.to] || next[nb.to] < contribution) next[nb.to] = contribution;
      });
    });
    Object.assign(act, next);
  }
  return act;
}
function combGenerate() {
  combSeedId = document.getElementById('comb-seed').value;
  combActivation = combSpread(combSeedId);
  const byType = {primitive: [], substrate: [], pain: [], population: []};
  COMB_NODES.forEach(n => {
    if (n.id === combSeedId) return;
    byType[n.type].push({n, a: combActivation[n.id] || 0});
  });
  Object.keys(byType).forEach(k => byType[k].sort((a, b) => b.a - a.a));
  // The seed counts for its own category
  const seedNode = COMB_NODES.find(n => n.id === combSeedId);
  const pick = (t) => byType[t][0] ? byType[t][0].n : null;
  const combo = {
    primitive:  seedNode.type === 'primitive'  ? seedNode : pick('primitive'),
    substrate:  seedNode.type === 'substrate'  ? seedNode : pick('substrate'),
    pain:       seedNode.type === 'pain'       ? seedNode : pick('pain'),
    population: seedNode.type === 'population' ? seedNode : pick('population'),
  };
  // Second substrate (the cross-app wedge)
  let second = null;
  if (combo.substrate) {
    second = byType.substrate.find(x => x.n.id !== combo.substrate.id && x.a > 0.15);
    if (second) second = second.n;
  }
  combResult = Object.assign({}, combo, { secondSubstrate: second });
  combRenderOutput();
  pepSend('combinator.generate', { seed: combSeedId });
}
function combRandom() {
  const pool = COMB_NODES.filter(n => n.type === 'pain' || n.type === 'substrate');
  const pick = pool[Math.floor(Math.random() * pool.length)];
  document.getElementById('comb-seed').value = pick.id;
  combGenerate();
}
function combClear() {
  combActivation = {}; combSeedId = null; combResult = null;
  document.getElementById('comb-output').innerHTML = '<div style="color:var(--dim);font-size:11px;letter-spacing:0.12em;margin-bottom:8px">CANDIDATE</div><div style="color:var(--dim);font-size:12px;padding:30px 0;text-align:center">pick a seed and hit Generate</div>';
  document.getElementById('comb-trace').innerHTML = '<div style="color:var(--dim);font-size:11px;letter-spacing:0.12em;margin-bottom:8px">ACTIVATION TRACE</div><div style="color:var(--dim);font-size:12px;padding:30px 0;text-align:center">\u2014</div>';
}
function combEsc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
function combRenderOutput() {
  if (!combResult) return;
  const r = combResult;
  const seedNode = COMB_NODES.find(n => n.id === combSeedId);
  // Generated title
  const subLabel = r.substrate ? r.substrate.label : '\u2014';
  const priShort = r.primitive ? r.primitive.short : '';
  const painLabel = r.pain ? r.pain.label : '';
  const popLabel = r.population ? r.population.label : '';
  const title = `${subLabel} ${painLabel} \u2014 ${r.primitive ? r.primitive.label : ''}`;
  const pitch = r.primitive && r.substrate && r.pain && r.population
    ? `Apply the <b style="color:#a78bfa">${combEsc(priShort)}</b> primitive over <b style="color:#4fc3f7">${combEsc(r.substrate.desc)}</b> to address <b style="color:#f06292">${combEsc(r.pain.desc)}</b>, targeting the <b style="color:#81c784">${combEsc(popLabel)}</b> market (${combEsc(r.population.desc)}).`
    : 'Incomplete activation \u2014 try increasing hops or picking a different seed.';
  const wedge = r.secondSubstrate
    ? `<div style="margin-top:14px;padding:10px 12px;background:rgba(79,195,247,0.08);border-left:3px solid #4fc3f7;border-radius:4px;font-size:12px"><b style="color:#4fc3f7">Cross-app wedge:</b> second substrate <b>${combEsc(r.secondSubstrate.label)}</b> lit strongly. Combining <b>${combEsc(r.substrate.label)}</b> \u00d7 <b>${combEsc(r.secondSubstrate.label)}</b> is the LAVAS-only move \u2014 a single-substrate competitor can\u2019t build this.</div>`
    : '';
  const novelty = (() => {
    // crude novelty: inverse of avg adjacency from seed to each picked node
    const pickedIds = [r.primitive, r.substrate, r.pain, r.population].filter(Boolean).map(x => x.id);
    const acts = pickedIds.map(id => combActivation[id] || 0);
    const avg = acts.reduce((a, b) => a + b, 0) / (acts.length || 1);
    // Lower avg activation means longer-path picks → more novel
    return Math.max(0, Math.min(1, 1 - avg));
  })();
  const novStr = novelty > 0.6 ? `<span style="color:#81c784">novel wedge (${novelty.toFixed(2)})</span>`
                : novelty > 0.35 ? `<span style="color:#f6d35c">moderate novelty (${novelty.toFixed(2)})</span>`
                : `<span style="color:#f06292">obvious combo (${novelty.toFixed(2)})</span>`;
  document.getElementById('comb-output').innerHTML = `
    <div style="color:var(--dim);font-size:11px;letter-spacing:0.12em;margin-bottom:8px">CANDIDATE &middot; seed: ${combEsc(seedNode ? seedNode.label : '')}</div>
    <div style="font-size:17px;font-weight:bold;margin-bottom:4px">${combEsc(title)}</div>
    <div style="font-size:11px;color:var(--dim);margin-bottom:10px">${novStr}</div>
    <div style="font-size:13px;line-height:1.6">${pitch}</div>
    ${wedge}
  `;
  // Trace
  const top = Object.entries(combActivation).sort((a, b) => b[1] - a[1]).slice(0, 10);
  const rows = top.map(([id, a]) => {
    const n = COMB_NODES.find(x => x.id === id);
    if (!n) return '';
    const colorMap = {primitive: '#a78bfa', substrate: '#4fc3f7', pain: '#f06292', population: '#81c784'};
    const col = colorMap[n.type];
    const bar = Math.round(a * 120);
    return `<div style="display:flex;align-items:center;gap:8px;font-size:11px;padding:3px 0">
      <span style="color:${col};min-width:100px">${combEsc(n.label)}</span>
      <span style="color:var(--dim);font-size:10px;min-width:70px">${n.type}</span>
      <span style="background:${col};height:6px;width:${bar}px;border-radius:2px;opacity:0.6"></span>
      <span style="color:var(--dim);font-size:10px">${a.toFixed(3)}</span>
    </div>`;
  }).join('');
  document.getElementById('comb-trace').innerHTML = `
    <div style="color:var(--dim);font-size:11px;letter-spacing:0.12em;margin-bottom:8px">ACTIVATION TRACE &middot; top 10</div>
    ${rows}
  `;
}
const combCanvas = document.getElementById('combinator-canvas');
const combCtx = combCanvas.getContext('2d');
const COMB_TYPE_COLOR = {primitive: '186,139,250', substrate: '79,195,247', pain: '240,98,146', population: '129,199,132'};
combCanvas.addEventListener('click', (ev) => {
  const rect = combCanvas.getBoundingClientRect();
  const mx = (ev.clientX - rect.left) * (combCanvas.width / rect.width);
  const my = (ev.clientY - rect.top) * (combCanvas.height / rect.height);
  let hit = null, best = 20 * 20;
  COMB_NODES.forEach(n => {
    const d2 = (n.x - mx) * (n.x - mx) + (n.y - my) * (n.y - my);
    if (d2 < best) { best = d2; hit = n; }
  });
  if (hit) {
    document.getElementById('comb-seed').value = hit.id;
    combGenerate();
  }
});
function drawCombinator() {
  const W = 960, H = 540;
  combCtx.fillStyle = themeBg(); combCtx.fillRect(0, 0, W, H);
  // Edges
  COMB_EDGES.forEach(e => {
    const a = COMB_NODES.find(n => n.id === e[0]);
    const b = COMB_NODES.find(n => n.id === e[1]);
    if (!a || !b) return;
    const aAct = combActivation[a.id] || 0;
    const bAct = combActivation[b.id] || 0;
    const lit = Math.max(aAct, bAct);
    const alpha = 0.05 + lit * 0.4;
    combCtx.strokeStyle = `rgba(140,150,170,${alpha.toFixed(3)})`;
    combCtx.lineWidth = 0.5 + lit * 1.5;
    combCtx.beginPath(); combCtx.moveTo(a.x, a.y); combCtx.lineTo(b.x, b.y); combCtx.stroke();
  });
  // Nodes
  COMB_NODES.forEach(n => {
    const act = combActivation[n.id] || 0;
    const col = COMB_TYPE_COLOR[n.type];
    const r = 8 + act * 6;
    // Halo if highly activated
    if (act > 0.15) {
      combCtx.fillStyle = `rgba(${col},${(act * 0.25).toFixed(3)})`;
      combCtx.beginPath(); combCtx.arc(n.x, n.y, r + 10, 0, Math.PI * 2); combCtx.fill();
    }
    // Node body
    const alpha = 0.35 + act * 0.6;
    combCtx.fillStyle = `rgba(${col},${alpha.toFixed(3)})`;
    combCtx.beginPath(); combCtx.arc(n.x, n.y, r, 0, Math.PI * 2); combCtx.fill();
    combCtx.strokeStyle = `rgba(${col},0.95)`;
    combCtx.lineWidth = n.id === combSeedId ? 2.2 : 1;
    combCtx.stroke();
    // Label
    const labelAlpha = 0.55 + act * 0.45;
    combCtx.fillStyle = `rgba(220,228,237,${labelAlpha.toFixed(3)})`;
    combCtx.font = n.type === 'primitive' ? 'bold 11px monospace' : '10px monospace';
    combCtx.textAlign = 'center'; combCtx.textBaseline = 'top';
    combCtx.fillText(n.label, n.x, n.y + r + 3);
  });
  // Legend
  combCtx.textAlign = 'left'; combCtx.textBaseline = 'alphabetic';
  combCtx.font = '10px monospace';
  const legend = [['primitive', 'primitive'], ['substrate', 'substrate'], ['pain', 'pain'], ['population', 'population']];
  legend.forEach(([key, lbl], i) => {
    const x = 20 + i * 120, y = H - 16;
    combCtx.fillStyle = `rgba(${COMB_TYPE_COLOR[key]},0.8)`;
    combCtx.beginPath(); combCtx.arc(x, y - 3, 5, 0, Math.PI * 2); combCtx.fill();
    combCtx.fillStyle = '#aaa';
    combCtx.fillText(lbl, x + 10, y);
  });
  // Hint
  combCtx.textAlign = 'right'; combCtx.fillStyle = '#778';
  combCtx.fillText('click any node to seed from there', W - 20, H - 16);
  requestAnimationFrame(drawCombinator);
}
drawCombinator();
</script>
</body>
</html>
"""


@router.get("/pep", response_class=HTMLResponse)
async def pep_home_page() -> str:
    return _PAGE
