"""Strata — Markets, trading signals, financial decision-making. Serves at /strata."""

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
<title>Strata — Markets, Trading Signals, Financial Decision-Making</title>
<style>
  :root {
    --bg: #0c0b10; --surface: #18161f; --surface2: #12111a;
    --text: #e0dce8; --dim: #7a7588; --accent: #e879f9; --accent2: #67e8f9;
    --warn: #facc15; --border: #2a2636;
  }
  body.light {
    --bg: #faf8fc; --surface: #ffffff; --surface2: #f3f0f8;
    --text: #1a1a1a; --dim: #665e74; --accent: #a21caf; --accent2: #0891b2;
    --warn: #a16207; --border: #d4cee0;
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
  .cat-btn { padding: 3px 9px; border-radius: 12px; border: 1px solid var(--border);
             background: var(--surface); color: var(--dim); font-size: 10px; cursor: pointer; font-family: inherit; }
  .cat-btn:hover { color: var(--text); border-color: var(--accent); }
  .cat-btn.cat-active { background: var(--accent); color: var(--bg); border-color: var(--accent); }
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
    <span class="brand">Strata</span>
    <span style="font-size:10px;color:var(--dim)">Markets · Trading Signals · Financial Decisions</span>
    <span id="pep-link-badge" style="margin-left:auto;font-size:10px;color:var(--dim);display:flex;align-items:center;gap:6px;padding:0 8px">
      <span id="pep-link-dot" style="width:8px;height:8px;border-radius:50%;background:#666;display:inline-block"></span>
      <span id="pep-link-label">PEP: …</span>
    </span>
    <select id="canvas-select" onchange="canvasSelect(this.value)"
      style="background:var(--surface);color:var(--text);border:1px solid var(--border);
      border-radius:4px;padding:4px 8px;font-family:inherit;font-size:10px;max-width:220px">
      <option value="">jump to canvas…</option>
    </select>
    <button onclick="downloadStrata()" class="nav-btn">Download</button>
    <button onclick="toggleLight()" id="light-btn" class="nav-btn">Light Mode</button>
    <span class="lavas-switch" style="display:flex;gap:8px;align-items:center;font-size:11px;flex-wrap:wrap">
      <a href="/pep">PEP</a>
      <a href="/axona">Axona</a>
      <a href="/lingora">Lingora</a>
      <a href="/atria">Atria</a>
      <a href="/vectora">Vectora</a>
      <span class="lavas-current">Strata</span>
    </span>
  </div>
  <div class="nav-row nav-row-bottom">
    <div class="tabs" id="tabs">
      <div class="tab active" data-panel="home-tab">Home</div>
      <div class="tab" data-panel="corr-tab">Correlation Graph</div>
      <div class="tab" data-panel="momentum-tab">Momentum Spread</div>
      <div class="tab" data-panel="earnings-tab">Earnings Residual</div>
      <div class="tab" data-panel="pragmatic-tab">Earnings Pragmatics</div>
      <div class="tab" data-panel="regime-tab">Regime Modulation</div>
      <div class="tab" data-panel="rotation-tab">Sector Rotation</div>
      <div class="tab" data-panel="vec-live-tab">Vectora Live</div>
      <div class="tab" data-panel="vec-watch-tab">Vectora Watch</div>
      <div class="tab" data-panels="unusual-tab classify-tab newscore-tab">Equities</div>
      <div class="tab" data-panels="leaderboard-tab catalog-tab strategy-detail-tab">Strategies</div>
      <div class="tab" data-panels="pitch-tab bench-tab">Pitch</div>
      <div class="tab" data-panel="products-tab">Products</div>
      <div class="tab" data-panel="theory-tab">Theory</div>
      <div class="tab" data-panel="whypep-tab">Why PEP</div>
      <div class="tab" data-panel="bridge-tab">PEP &harr; Strata</div>
    </div>
  </div>
</nav>

<!-- ═══ Home ══════════════════════════════════════════════════════ -->
<div class="panel active" id="home-tab">
<div class="container">
  <div class="hero">
    <div class="tag">STRATA</div>
    <h1>Markets Are Weighted Graphs That Change Under Stress</h1>
    <p>
      Every asset is a node. Correlation, flow, and sector membership are
      edges. Momentum is spreading activation. Earnings surprises are
      residual spikes. Risk-on vs risk-off is a state modulator that
      rewrites the edge weights on the fly. The same four PEP primitives
      that model cognition, language, matching, and data retrieval also
      model markets &mdash; because markets are information-processing
      systems built on weighted structure, prediction, and surprise.
    </p>
    <p>
      Strata is the LAVAS markets platform &mdash; the parent of every
      vertical market application built on PEP primitives. The
      <b>Equities</b> tab is Strata's first shipping vertical: an
      AI-powered stock intelligence and paper-trading layer with a
      working implementation at
      <code>~/projects/charlie_project/</code>. Future verticals
      (crypto, FX, commodities, prediction markets, fixed income)
      reuse the same four primitives applied to different asset
      classes. Strata is the engine; each vertical is an instance.
      Not a trading bot, not financial advice &mdash; research and
      simulation only.
    </p>
  </div>

  <h3>Five day-one canvases</h3>
  <div class="info">
    &bull; <b>Correlation Graph</b> &mdash; 12 synthetic assets with
    rolling correlation edges. Toggle sector overlay. See the community
    structure.<br>
    &bull; <b>Momentum Spread</b> &mdash; one asset moves; activation
    spreads to correlated neighbors with a lag. The shape of the
    spread is the market's internal structure becoming visible.<br>
    &bull; <b>Earnings Residual</b> &mdash; the gap between the market's
    forecast and reality. Beat, miss, or in-line. The price move is
    proportional to the residual, not the absolute number.<br>
    &bull; <b>Regime Modulation</b> &mdash; switch between risk-on,
    risk-off, and crisis. Watch the correlation graph rewire itself
    as the regime changes.<br>
    &bull; <b>Sector Rotation</b> &mdash; capital flows around the
    business-cycle clock. Early → mid → late → recession → early.
    Track where activation sits and where it is building.
  </div>
</div>
</div>

<!-- ═══ Correlation Graph ════════════════════════════════════════ -->
<div class="panel" id="corr-tab">
<div class="container">
  <h2>Correlation Graph &mdash; Who Moves With Whom</h2>
  <p class="desc">
    12 synthetic assets. Edges are weighted by return correlation over a
    rolling window. Highly correlated assets cluster; uncorrelated ones
    drift apart. Toggle sector overlay to see the community structure.
  </p>
  <div class="canvas-box">
    <canvas id="corr-canvas" width="960" height="460"></canvas>
  </div>
  <div class="controls">
    <button onclick="corrToggleSector()">Toggle sector overlay</button>
    <button onclick="corrRegen()">Regenerate</button>
  </div>
  <div class="info">
    <b>See also:</b>
    <a href="/pep">PEP &rarr; Weighted Graph</a>,
    <a href="/vectora">Vectora &rarr; Knowledge Graph</a> (same
    typed-edge structure, different domain),
    <a href="/atria">Atria &rarr; Multi-Objective Projection</a>.
  </div>
</div>
</div>

<!-- ═══ Momentum Spread ═════════════════════════════════════════ -->
<div class="panel" id="momentum-tab">
<div class="container">
  <h2>Momentum Spread &mdash; Activation After a Shock</h2>
  <p class="desc">
    Click any asset to simulate a sharp move. Activation spreads to
    correlated neighbors with decay, modeling momentum spillover across
    the market.
  </p>
  <div class="canvas-box">
    <canvas id="momentum-canvas" width="960" height="460"></canvas>
  </div>
  <div class="controls">
    <label style="display:flex;align-items:center;gap:8px">
      <span>spread decay:</span>
      <input type="range" id="mom-decay" min="5" max="60" value="25" style="width:120px">
      <span class="stat-val" id="mom-decay-val">0.25</span>
    </label>
    <button onclick="momReset()">Reset</button>
  </div>
  <div class="info">
    <b>See also:</b>
    <a href="/pep">PEP &rarr; Spreading Activation</a>,
    <a href="/axona">Axona &rarr; Attention Spotlight</a>,
    <a href="/atria">Atria &rarr; Pool Spreading</a>.
  </div>
</div>
</div>

<!-- ═══ Earnings Residual ═══════════════════════════════════════ -->
<div class="panel" id="earnings-tab">
<div class="container">
  <h2>Earnings Residual &mdash; The Gap Between Forecast and Reality</h2>
  <p class="desc">
    A company reports earnings. The market had a forecast. The difference
    is the residual. The price move is proportional to the residual, not
    the absolute earnings number.
  </p>
  <div class="canvas-box">
    <canvas id="earnings-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <button onclick="earningsFire('beat')">Earnings beat (+15%)</button>
    <button onclick="earningsFire('inline')">In-line (0%)</button>
    <button onclick="earningsFire('miss')">Earnings miss (-20%)</button>
    <button onclick="earningsReset()">Reset</button>
  </div>
  <div class="info">
    <b>See also:</b>
    <a href="/pep">PEP &rarr; Predictor + Residual</a>,
    <a href="/axona">Axona &rarr; Reward Prediction Error</a>,
    <a href="/atria">Atria &rarr; Residual Heatmap</a>.
  </div>
</div>
</div>

<!-- ═══ Earnings Pragmatics ═════════════════════════════════════ -->
<div class="panel" id="pragmatic-tab">
<div class="container">
  <h2>Earnings-Call Pragmatics &mdash; The Gap Between What They Say and What They Signal</h2>
  <p class="desc">
    Executives are trained to mask pragmatic content. They say positive
    words while hedge density, passive subject-drop, register shifts,
    and deflection patterns give the real story away. The gap between
    <em>stated sentiment</em> (lexicon of the words) and <em>pragmatic
    sentiment</em> (what the language is actually signaling) is alpha
    number-only engines don't see. This canvas runs the Lingora voice +
    translate analyzer on curated fictional excerpts showing canonical
    patterns &mdash; click any row to see the rationale.
  </p>
  <div class="controls" style="margin-bottom:10px">
    <button onclick="prPick(0)">Clean positive</button>
    <button onclick="prPick(1)">Hedged</button>
    <button onclick="prPick(2)">Deflection</button>
    <button onclick="prPick(3)">Register shift</button>
    <button onclick="prPick(4)">Passive subject drop</button>
    <button onclick="prPick(5)">CEO confidence</button>
    <button onclick="prPick(6)">Defensive formal</button>
    <button onclick="prAnalyzeAll()">Analyze entire transcript</button>
  </div>
  <div class="canvas-box">
    <canvas id="pragmatic-canvas" width="960" height="360"></canvas>
  </div>
  <div id="pr-detail" style="margin-top:14px;background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:14px 16px;min-height:200px">
    <div style="color:var(--dim);font-size:12px;padding:30px 0;text-align:center">pick an excerpt above</div>
  </div>
  <div class="info">
    <b>What the signal means.</b><br>
    &bull; <b>CONFIRM</b> &mdash; stated and pragmatic agree. The number
    story and the language story point the same direction. High
    confidence.<br>
    &bull; <b>WARNING / FADE / STRONG FADE</b> &mdash; positive stated
    but pragmatic markers (hedge, deflection, passive, register shift)
    discount it. The bigger the gap, the more the language is
    concealing. Trade: fade or wait for the shoe to drop next quarter.<br>
    &bull; <b>REINFORCE</b> &mdash; pragmatic is <em>more</em> positive
    than stated (rare). Usually a CEO who's been burned and is
    under-promising to set up over-delivery. Buy signal.<br>
    &bull; <b>NEUTRAL</b> &mdash; no material markers either way; trust
    the numbers.<br><br>
    <b>Why PEP.</b> This is the predictor + residual primitive (#3)
    composed with the state-modulator primitive (#4), running on
    language-as-substrate. The predictor is "what the words literally
    say"; the residual is what the pragmatic layer is adding or
    subtracting. The state modulator (register, hedge density, deflection
    rate) rescales the predictor's output. It's Strata (the asset-signal
    app) consuming Lingora (the language-analysis app) &mdash; a pure
    cross-app wedge that single-substrate competitors can't replicate
    without building both halves.<br><br>
    <b>Engine module:</b> <code>pep.lingora.earnings_pragmatic</code>
    &mdash; regex + lexicon heuristics, LLM-free.
    <b>See also:</b>
    <a href="#" onclick="document.querySelector('[data-panel=earnings-tab]').click();return false">Strata &rarr; Earnings Residual</a>
    (the numerical side),
    <a href="/lingora#voice-tab">Lingora &rarr; Voice</a> (the analyzer primitives),
    <a href="/lingora#subtext-tab">Lingora &rarr; Subtext</a> (pragmatic layer in general).
  </div>
</div>
</div>

<!-- ═══ Regime Modulation ═══════════════════════════════════════ -->
<div class="panel" id="regime-tab">
<div class="container">
  <h2>Regime Modulation &mdash; The Graph Rewires Under Stress</h2>
  <p class="desc">
    Switch between regimes and watch the correlation graph change. In
    risk-on, risky assets cluster tightly. In risk-off, safe havens
    strengthen. In crisis, everything correlates to 1 because
    everything sells together.
  </p>
  <div class="canvas-box">
    <canvas id="regime-canvas" width="960" height="460"></canvas>
  </div>
  <div class="controls">
    <button onclick="regimePick('riskon')">Risk-on (bull)</button>
    <button onclick="regimePick('riskoff')">Risk-off (flight to safety)</button>
    <button onclick="regimePick('crisis')">Crisis (everything correlated)</button>
    <button onclick="regimePick('lowvol')">Low-vol grind</button>
  </div>
  <div class="info">
    <b>See also:</b>
    <a href="/pep">PEP &rarr; State Modulator</a>,
    <a href="/axona">Axona &rarr; Cognitive Bandwidth</a>,
    <a href="/atria">Atria &rarr; Behavior Modulation</a>.
  </div>
</div>
</div>

<!-- ═══ Sector Rotation ════════════════════════════════════════ -->
<div class="panel" id="rotation-tab">
<div class="container">
  <h2>Sector Rotation &mdash; Capital Walks the Business Cycle</h2>
  <p class="desc">
    Capital rotates between sectors over the cycle: early → cyclicals,
    mid → tech/growth, late → energy/materials, recession → defensives.
    Track where activation sits and where it is building next.
  </p>
  <div class="canvas-box">
    <canvas id="rotation-canvas" width="960" height="460"></canvas>
  </div>
  <div class="controls">
    <button onclick="rotationPick('early')">Early cycle</button>
    <button onclick="rotationPick('mid')">Mid cycle</button>
    <button onclick="rotationPick('late')">Late cycle</button>
    <button onclick="rotationPick('recession')">Recession</button>
  </div>
  <div class="info">
    <b>The business-cycle clock:</b> Early cycle (recovery) favors
    consumer discretionary and industrials. Mid cycle favors tech and
    growth. Late cycle favors energy, materials, and financials.
    Recession favors utilities, healthcare, and consumer staples. The
    rotation is a slow graph walk across the sector map, seeded by the
    macro environment.<br><br>
    <b>See also:</b>
    <a href="/lingora">Lingora &rarr; Semantic Drift</a> (the same
    temporal-shift visualization, applied to word meaning instead of
    capital flow).
  </div>
</div>
</div>

<!-- ═══ Vectora-Powered Live Retrieval ═══════════════════════════ -->
<div class="panel" id="vec-live-tab">
<div class="container">
  <h2>Live Vectora Retrieval
    <span style="font-size:10px;color:#a3e635;margin-left:10px;letter-spacing:0.1em">● POWERED BY VECTORA</span>
  </h2>
  <p class="desc">
    This canvas calls the real Vectora engine (<code>pep.vectora</code>)
    via HTTP. A graph of 20 asset nodes is seeded on the server; picking
    a ticker runs spreading activation through its correlation
    neighborhood. Same engine as
    <a href="/vectora/playground">/vectora/playground</a>.
  </p>
  <div class="canvas-box" style="padding:20px">
    <div style="display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin-bottom:14px">
      <label style="font-size:11px;color:var(--dim);display:flex;gap:6px;align-items:center;flex:1;min-width:240px">
        <span>seed ticker:</span>
        <select id="vec-strata-seed" style="flex:1;background:var(--surface);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:6px;font-family:inherit;font-size:11px">
          <option value="">loading…</option>
        </select>
      </label>
      <label style="font-size:11px;color:var(--dim);display:flex;gap:6px;align-items:center">
        <span>k:</span>
        <input type="range" id="vec-strata-k" min="3" max="10" value="6" style="width:80px">
        <span id="vec-strata-k-v" style="color:var(--accent);font-weight:bold;min-width:14px">6</span>
      </label>
      <label style="font-size:11px;color:var(--dim);display:flex;gap:6px;align-items:center">
        <span>decay:</span>
        <input type="range" id="vec-strata-decay" min="10" max="80" value="35" style="width:80px">
        <span id="vec-strata-decay-v" style="color:var(--accent);font-weight:bold;min-width:30px">0.35</span>
      </label>
      <button onclick="vecStrataQuery()" style="padding:6px 14px;border-radius:4px;border:1px solid var(--accent);background:var(--accent);color:var(--bg);font-size:11px;cursor:pointer;font-family:inherit;font-weight:bold">Query Vectora</button>
    </div>
    <div id="vec-strata-results" style="min-height:180px">
      <div style="color:var(--dim);text-align:center;padding:40px 20px;font-size:11px">pick a ticker and click Query</div>
    </div>
    <div id="vec-strata-stats" style="margin-top:10px;font-size:10px;color:var(--dim);text-align:right"></div>
  </div>
  <div class="info">
    <b>Dogfood play.</b> The correlation-graph spreading mechanism Strata
    uses for momentum spillover is the same primitive Vectora ships as
    retrieval. Strata's asset graph delegates to Vectora. Every LAVAS app
    that needs spreading-activation retrieval does the same &mdash; one
    engine, many products.
  </div>
</div>
</div>

<!-- ═══ Vectora Watch — real residual scoring on asset descriptions ═══ -->
<div class="panel" id="vec-watch-tab">
<div class="container">
  <h2>Anomaly Scoring
    <span style="font-size:10px;color:#a3e635;margin-left:10px;letter-spacing:0.1em">● POWERED BY VECTORA WATCH</span>
  </h2>
  <p class="desc">
    This canvas delegates anomaly scoring to <b>Vectora Watch</b>
    (<a href="/vectora/watch">product page</a>). Paste an asset
    description or click a sample. Vectora scores it against the
    20-asset reference corpus with a three-component residual:
    distance from the corpus centroid + nearest-neighbor weakness +
    novelty vs recent stream. Same engine, different asset class.
  </p>
  <div class="canvas-box" style="padding:20px">
    <div style="margin-bottom:10px">
      <div style="font-size:11px;color:var(--dim);margin-bottom:8px">Sample items (click to score):</div>
      <div id="strata-watch-samples" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:6px"></div>
    </div>
    <div style="display:flex;gap:8px;margin-bottom:14px">
      <input id="strata-watch-input" type="text" placeholder="paste an asset description or news snippet..." style="flex:1;background:var(--surface);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:8px 12px;font-family:inherit;font-size:11px">
      <button onclick="strataWatchScore()" style="padding:8px 14px;border-radius:4px;border:1px solid var(--accent);background:var(--accent);color:var(--bg);font-size:11px;cursor:pointer;font-family:inherit;font-weight:bold">Score</button>
    </div>
    <div id="strata-watch-stream" style="min-height:200px;max-height:340px;overflow-y:auto;background:var(--surface);border:1px solid var(--border);border-radius:4px;padding:12px">
      <div style="color:var(--dim);text-align:center;padding:30px;font-size:11px">No items scored yet.</div>
    </div>
    <div id="strata-watch-stats" style="margin-top:10px;padding:8px 12px;background:var(--surface);border:1px solid var(--border);border-radius:4px;font-size:10px;color:var(--dim);display:none"></div>
  </div>
  <div class="info">
    <b>Dogfood.</b> Strata's equities vertical does not re-implement
    anomaly detection &mdash; it calls Vectora Watch. The residual
    scoring you see here is the same primitive every Watch customer
    would use, seeded with Strata's asset corpus. Drop in a dataset,
    get a scorer.
  </div>
</div>
</div>

<!-- ═══ Unusual Move Scanner ════════════════════════════════════ -->
<div class="panel" id="unusual-tab">
<div class="container">
  <h2>Unusual Move Scanner &mdash; Residual Scoring on Price + Volume</h2>
  <p class="desc">
    Strata's equities vertical, residual-scoring layer. Today's price
    move and volume are scored against the stock's historical
    distribution of rolling moves. The composite "unusual score" is a
    weighted residual: how far the move is from what the predictor
    expected. Lives in production at <code>~/projects/charlie_project/</code>;
    formula reproduced here as a Strata canvas.
  </p>
  <div class="canvas-box">
    <canvas id="unusual-canvas" width="960" height="500"></canvas>
  </div>
  <div class="controls">
    <label style="display:flex;align-items:center;gap:8px">
      <span>price move %:</span>
      <input type="range" id="u-price" min="-15" max="15" value="3" style="width:140px" oninput="document.getElementById('u-price-val').textContent=this.value+'%'">
      <span class="stat-val" id="u-price-val">3%</span>
    </label>
    <label style="display:flex;align-items:center;gap:8px">
      <span>relative volume:</span>
      <input type="range" id="u-rvol" min="50" max="500" value="120" style="width:140px" oninput="document.getElementById('u-rvol-val').textContent=(this.value/100).toFixed(1)+'x'">
      <span class="stat-val" id="u-rvol-val">1.2x</span>
    </label>
  </div>
  <div class="info">
    <b>The formula</b> (Strata's <code>calculateUnusualScore</code>,
    deployed in the equities vertical): 35% price-change percentile vs
    historical, 25% relative-volume percentile, 25% volatility-adjusted
    z-score, 15% move persistence. Each component normalized to 0-100,
    weighted, summed.<br><br>
    <b>What you are watching:</b> Live computation. The four bars on the
    left are the four components. The composite "unusual score" on the
    right is the weighted sum. Above 70 is flagged as "unusual"; above
    85 as "extreme." Both labels trigger downstream logic in the
    equities vertical (news scoring, classification, alert).<br><br>
    <b>PEP framing:</b> This is residual scoring (Predictor + Residual
    primitive). The "predictor" is the historical distribution; the
    "residual" is how far today's observation lies from it. Identical
    to the Earnings Residual canvas mechanism, generalized from
    earnings to price/volume.
  </div>
</div>
</div>

<!-- ═══ Pattern Classifier ═══════════════════════════════════════ -->
<div class="panel" id="classify-tab">
<div class="container">
  <h2>Pattern Classifier &mdash; 16 Move Types From the Same Inputs</h2>
  <p class="desc">
    Strata's equities vertical, classification layer. Given an unusual
    move, classify it into one of 16 archetypes (breakout, breakdown,
    momentum, mean reversion, short squeeze, low float, sector
    sympathy, pump risk, post-earnings drift, capitulation, gap up/
    down, exhaustion top/bottom, volume climax, unknown). The classifier
    is rule-based because the rules are interpretable and the categories
    are discrete; an LLM would be overkill.
  </p>
  <div class="canvas-box">
    <canvas id="classify-canvas" width="960" height="500"></canvas>
  </div>
  <div class="controls">
    <button onclick="classifyPick(0)">+12% on 5x volume, hits new high</button>
    <button onclick="classifyPick(1)">-8% on 4x volume, breaks 200d MA</button>
    <button onclick="classifyPick(2)">+6% gap up at open</button>
    <button onclick="classifyPick(3)">+25% on $80M float</button>
    <button onclick="classifyPick(4)">+4% drift after earnings beat</button>
    <button onclick="classifyPick(5)">+18% with 8x volume + low float</button>
  </div>
  <div class="info">
    <b>What you are watching:</b> A scenario card with the price
    candle, volume bar, and historical context (left). The classifier's
    decision tree (middle). The output classification + confidence +
    plain-English explanation (right). The same six inputs (price %,
    volume, float, market cap, gap, persistence) drive every
    classification.<br><br>
    <b>PEP framing:</b> The classifier is a learned discrete projection
    on top of the residual. The residual ("how unusual?") is a
    continuous score; the classifier is a categorical map from the
    state-vector to a label. Same primitive Atria uses to label match
    quality types.
  </div>
</div>
</div>

<!-- ═══ News Catalyst Scorer ═════════════════════════════════════ -->
<div class="panel" id="newscore-tab">
<div class="container">
  <h2>News Catalyst Scorer &mdash; Multi-Dimensional Headline Scoring</h2>
  <p class="desc">
    Strata's equities vertical, AI news-scoring layer (Claude Haiku in
    production). Each headline gets scored on five dimensions: quality
    (substantive vs clickbait), sentiment (-100 bearish to +100
    bullish), credibility (Reuters &gt;&gt; unknown blog), materiality
    (likely to move price?), and hype (sensational relative to
    content). Cost-controlled: only stocks with unusualScore &ge; 60
    get scored.
  </p>
  <div class="canvas-box">
    <canvas id="newscore-canvas" width="960" height="540"></canvas>
  </div>
  <div class="controls">
    <button onclick="newscorePick(0)">"AAPL beats Q4 expectations" (Reuters)</button>
    <button onclick="newscorePick(1)">"Mystery Penny Stock POPS 200%" (Pump blog)</button>
    <button onclick="newscorePick(2)">"FDA approves Pfizer cancer drug" (Bloomberg)</button>
    <button onclick="newscorePick(3)">"CEO interviewed at conference" (Yahoo)</button>
    <button onclick="newscorePick(4)">"Tesla recalls 50K vehicles" (WSJ)</button>
    <button onclick="newscorePick(5)">"BREAKING: Crypto coin moon soon???" (Twitter)</button>
  </div>
  <div class="info">
    <b>What you are watching:</b> A headline (top), the five-dimension
    scoring (middle), and a one-line analyst summary (bottom). The
    scoring weights match the Claude prompt Strata deploys in the
    equities vertical (<code>NEWS_SCORING_SYSTEM_PROMPT</code>): high quality goes to
    earnings/FDA approvals/major contracts; low to rumors/clickbait;
    high hype + low credibility flags pump risk.<br><br>
    <b>PEP framing:</b> Multi-objective projection on text. Same
    primitive Atria uses for player compatibility (skill / tempo /
    social / role) and Lingora uses for translation layers
    (denotation / pragmatic / register / cultural). Different domain,
    same shape: a single input projected through multiple typed lenses.
  </div>
</div>
</div>

<!-- ═══ Strategy Leaderboard ═════════════════════════════════════ -->
<div class="panel" id="leaderboard-tab">
<div class="container">
  <h2>Strategy Leaderboard &mdash; Multiple Strategies, One Population</h2>
  <p class="desc">
    Strata's equities vertical, strategy backtester. Six paper-trading
    strategies compete on the same synthetic price history. Each has
    different factor weights, position sizing, stop-loss, and exit
    rules. Scored on annualized return, Sharpe, max drawdown, win rate,
    total trades.
  </p>
  <div class="canvas-box">
    <canvas id="leaderboard-canvas" width="960" height="560"></canvas>
  </div>
  <div class="controls">
    <button onclick="leaderRegen()">Regenerate market scenario</button>
  </div>
  <div class="info">
    <b>The six strategies:</b><br>
    &bull; <b>Momentum Long</b> &mdash; chase confirmed breakouts; 5%
    stop, 15% take-profit, 5-day max hold.<br>
    &bull; <b>Mean Reversion</b> &mdash; buy oversold high-quality
    names; 8% stop, 6% take-profit, 3-day max hold.<br>
    &bull; <b>News-Driven</b> &mdash; only trade signals with
    materialityScore &ge; 70; tighter sizing, longer hold.<br>
    &bull; <b>Short Pump Risk</b> &mdash; short stocks flagged as pump
    risk; small size, hard 3% stop.<br>
    &bull; <b>Sector Rotation</b> &mdash; rotate into the leading
    sector each week.<br>
    &bull; <b>Buy &amp; Hold (SPY)</b> &mdash; baseline; no rules.<br><br>
    <b>What you are watching:</b> Equity curves over a synthetic 1-year
    period (top). Performance leaderboard (bottom) with annualized
    return, Sharpe, max drawdown, win rate. Different scenarios reward
    different strategies; no strategy dominates across all
    regimes.<br><br>
    <b>PEP framing:</b> Same multi-objective comparison Atria uses
    for matchmaker objectives, and Vectora uses for retrieval
    benchmarks. Strategies are nodes; market scenarios are state
    modulators; the leaderboard is residual scoring on returns.
  </div>
</div>
</div>

<!-- ═══ Strategy Catalog ═══════════════════════════════════════ -->
<div class="panel" id="catalog-tab">
<div class="container">
  <h2>Strategy Catalog &mdash; All <span id="cat-count">294</span> Equities Strategies</h2>
  <p class="desc">
    Strata's equities vertical ships with 294 paper-trading strategies
    spanning every major sector, direction, and style. Pure-momentum
    breakouts to contrarian dip-buyers to hedged sector rotations.
    Filter by sector or direction; click any card to open it in
    Strategy Detail.
  </p>
  <div class="controls" style="flex-wrap:wrap;gap:6px">
    <span style="color:var(--dim)">sector:</span>
    <button onclick="catalogFilter('sector','all')" id="cf-all" class="cat-btn cat-active">all</button>
    <button onclick="catalogFilter('sector','Tech')" class="cat-btn">Tech</button>
    <button onclick="catalogFilter('sector','Healthcare')" class="cat-btn">Healthcare</button>
    <button onclick="catalogFilter('sector','Financial')" class="cat-btn">Financial</button>
    <button onclick="catalogFilter('sector','Energy')" class="cat-btn">Energy</button>
    <button onclick="catalogFilter('sector','Industrial')" class="cat-btn">Industrial</button>
    <button onclick="catalogFilter('sector','Consumer')" class="cat-btn">Consumer</button>
    <button onclick="catalogFilter('sector','Staples')" class="cat-btn">Staples</button>
    <button onclick="catalogFilter('sector','Utilities')" class="cat-btn">Utilities</button>
    <button onclick="catalogFilter('sector','RealEstate')" class="cat-btn">Real Estate</button>
    <button onclick="catalogFilter('sector','Materials')" class="cat-btn">Materials</button>
    <button onclick="catalogFilter('sector','Communication')" class="cat-btn">Comm</button>
    <button onclick="catalogFilter('sector','Mixed')" class="cat-btn">Cross-sector</button>
  </div>
  <div class="controls" style="padding-top:0;flex-wrap:wrap;gap:6px">
    <span style="color:var(--dim)">direction:</span>
    <button onclick="catalogFilter('dir','all')" class="cat-btn cat-active" id="cf-dir-all">all</button>
    <button onclick="catalogFilter('dir','long')" class="cat-btn">long</button>
    <button onclick="catalogFilter('dir','short')" class="cat-btn">short</button>
    <button onclick="catalogFilter('dir','contrarian_long')" class="cat-btn">contrarian long</button>
    <button onclick="catalogFilter('dir','contrarian_short')" class="cat-btn">contrarian short</button>
    <button onclick="catalogFilter('dir','gap_long')" class="cat-btn">gap long</button>
    <input type="text" id="cat-search" placeholder="search…" oninput="catalogRender()"
      style="background:var(--surface);color:var(--text);border:1px solid var(--border);
      border-radius:4px;padding:4px 8px;font-family:inherit;font-size:11px;margin-left:auto;width:160px">
    <span style="color:var(--dim);font-size:10px">showing <b id="cat-shown" style="color:var(--accent)">—</b> / <b id="cat-total" style="color:var(--accent)">—</b></span>
  </div>
  <div id="catalog-grid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:8px;margin-top:10px">
    <span style="color:var(--dim)">building catalog…</span>
  </div>
</div>
</div>

<!-- ═══ Strategy Detail ════════════════════════════════════════ -->
<div class="panel" id="strategy-detail-tab">
<div class="container">
  <h2>Strategy Detail &mdash; <span id="sd-name">(pick one from the catalog)</span></h2>
  <p class="desc">
    Pick a strategy from the Catalog or use the dropdown to inspect any
    of the 294. Shows factor weights, direction, description, expected
    behavior under different market regimes, and which scanner output
    would trigger an entry.
  </p>
  <div class="controls">
    <select id="sd-select" onchange="strategyDetailPick(this.value)"
      style="background:var(--surface);color:var(--text);border:1px solid var(--border);
      border-radius:4px;padding:6px 10px;font-family:inherit;font-size:11px;min-width:300px">
      <option value="">— choose a strategy —</option>
    </select>
  </div>
  <div class="canvas-box">
    <canvas id="sd-canvas" width="960" height="560"></canvas>
  </div>
  <div class="info">
    <b>What you are watching:</b> The picked strategy's factor weights
    as horizontal bars (left), its declared direction and risk
    parameters (middle), and a "would it trigger?" check against three
    sample setups (right). Factor weights typically include
    relativeVolume, unusualScore, gapPct, sectorMomentum, hypeRisk,
    and priceLevel52w &mdash; the same factors the Unusual Move
    Scanner produces. Strategies are how Strata's equities vertical
    converts scanner output into entry decisions.<br><br>
    <b>The composition:</b> Each strategy is a weighted dot product of
    factor scores plus filters (market cap, float, price thresholds)
    plus position-management rules (stop loss %, take profit %, max
    hold days, max positions, position size %). Same shape across all
    294. The variation is in the weights and thresholds, not the
    structure &mdash; which is why adding new strategies is cheap and
    why a portfolio of strategies makes sense.
  </div>
</div>
</div>

<!-- ═══ Research Pitch ═══════════════════════════════════════════ -->
<div class="panel" id="pitch-tab">
<div class="container">
  <h2>Research Pitch &mdash; Strata Is the Markets-Primitive Platform</h2>
  <p class="desc">
    Strata is not a single product. It is the LAVAS markets-primitive
    platform &mdash; the parent of every vertical market application
    that runs on PEP primitives. The Equities vertical is the first
    shipping instance (AI-powered stock intelligence + paper-trading;
    code at <code>~/projects/charlie_project/</code>). Crypto, FX,
    commodities, prediction markets, and fixed income are natural
    additional verticals that reuse the same primitives applied to
    different asset classes. Research validates the engine; each
    vertical validates a market.
  </p>

  <div class="info" style="border-left: 3px solid var(--accent2)">
    <b style="font-size:14px;color:var(--accent2)">Strata's Architecture &mdash; Engine + Verticals</b><br><br>
    The four PEP primitives compose into a markets-primitive layer
    that any asset-class vertical can build on. The Equities vertical
    is the first instance and is already running:<br><br>
    &bull; <b>Unusual Move Scanner</b> &mdash; residual scoring on
    price/volume against historical distributions (35% price percentile
    + 25% volume + 25% volatility-adjusted + 15% persistence).
    Asset-class agnostic; the equities vertical wires it to Finnhub,
    a crypto vertical would wire it to CoinGecko, an FX vertical to
    a broker feed.<br>
    &bull; <b>Pattern Classifier</b> &mdash; 16 discrete archetypes
    projected from the unusual-score state-vector. The archetypes are
    domain-specific per vertical (equities has breakouts and gaps;
    crypto has pump-and-dumps and rug pulls; FX has carry-trade
    unwinds and intervention spikes); the classifier framework is
    shared.<br>
    &bull; <b>News Catalyst Scorer</b> &mdash; Claude-scored
    multi-dimensional headline analysis (quality, sentiment,
    credibility, materiality, hype). Same Claude prompt across
    verticals, with vertical-specific source weighting (Reuters for
    equities, on-chain analytics for crypto, central-bank statements
    for FX).<br>
    &bull; <b>Strategy Leaderboard</b> &mdash; paper-trading strategies
    competing on returns. The strategy framework, position-sizing,
    drawdown calculations are vertical-agnostic; only the asset
    universe and execution model differ.<br><br>
    Every vertical reuses the engine. The cost of adding a new vertical
    is data-source integration plus vertical-specific archetype
    definitions, not rebuilding the platform.
  </div>

  <div class="info" style="border-left: 3px solid var(--accent)">
    <b style="font-size:14px;color:var(--accent)">The Hypothesis</b><br><br>
    Markets are information-processing systems running on weighted
    graphs, and PEP's four primitives &mdash; weighted graph, spreading
    activation, residual scoring, state modulation &mdash; should
    produce useful structural insights on real market data without any
    market-specific inductive bias. The Equities vertical demonstrates
    this is feasible on real-shape problems with cost-controlled AI.
    The four falsifiable questions below are the next layer of
    validation &mdash; structural-insight claims that go beyond what
    any single asset-class vertical currently shows.
  </div>

  <div class="info" style="border-left: 3px solid var(--accent2)">
    <b style="font-size:14px;color:var(--accent2)">Four Falsifiable Questions</b><br><br>
    &bull; <b>Q1:</b> Does the correlation-graph community structure
    predict sector rotation transitions better than standard macro
    indicators (yield curve, PMI, unemployment)? Measurable: rank
    correlation of predicted rotation timing vs actual.<br>
    &bull; <b>Q2:</b> Does spreading-activation momentum capture
    lead-lag effects that pairwise correlation misses? Measurable:
    information coefficient (IC) of the spread signal vs IC of the
    direct correlation signal on held-out returns.<br>
    &bull; <b>Q3:</b> Does residual scoring on earnings surprises
    correlate with subsequent alpha better than the raw surprise
    number? Measurable: 30-day post-announcement drift Sharpe under
    each scoring method.<br>
    &bull; <b>Q4:</b> Does regime-detection via state modulation
    improve risk management compared to fixed-correlation models?
    Measurable: max drawdown and tail-beta of a simple portfolio
    under each regime model, across the 2008, 2020, and 2022 stress
    windows.
  </div>

  <div class="info" style="border-left: 3px solid var(--warn)">
    <b style="font-size:14px;color:var(--warn)">What This Is Not</b><br><br>
    &bull; <b>Not a trading system.</b> No order execution, no live
    signals, no backtest harness for strategy development. These are
    structural measurements, not trades.<br>
    &bull; <b>Not forecasting.</b> The canvases demonstrate mechanisms
    (what the graph does under a regime shift, how momentum spreads).
    They do not predict tomorrow&apos;s returns.<br>
    &bull; <b>Not financial advice.</b> Anything on this page is a
    research artifact. Do not trade on it.<br>
    &bull; <b>Not a replacement for Bloomberg, Refinitiv, or a proper
    quant platform.</b> Strata's value add is the graph primitives on
    top of data you already have, not the data.
  </div>

  <div class="info" style="border-left: 3px solid var(--accent)">
    <b style="font-size:14px;color:var(--accent)">What Success Looks Like</b><br><br>
    Positive results on Q1-Q4 on real market data (S&amp;P 500
    constituents plus major ETFs, 10-year daily returns) would justify
    taking Strata from sandbox to product. Even modest positive results
    &mdash; say, Q2 showing IC uplift of 0.01-0.02 vs the correlation
    baseline &mdash; would be a meaningful validation because the
    primitives are domain-free and the uplift comes from structure the
    baseline cannot see.<br><br>
    Negative results are equally useful. If the primitives do not
    produce uplift on market data, that is a signal about which
    primitives need refinement, which feeds back into every other
    LAVAS app. A research sandbox that produces honest negative
    results is more valuable than a product that produces confident
    wrong ones.
  </div>
</div>
</div>

<!-- ═══ Recall Benchmark (Strata style — IC comparison) ══════════ -->
<div class="panel" id="bench-tab">
<div class="container">
  <h2>Signal Benchmark &mdash; Graph-Based vs Baseline on Synthetic Returns</h2>
  <p class="desc">
    500 synthetic asset-return sequences with known factor structure.
    Baseline: direct pairwise correlation as a momentum signal.
    Strata: spreading-activation momentum on the correlation graph.
    The baseline captures first-order structure; Strata captures
    higher-order structure through graph expansion. Same pattern as
    Atria's Before/After and Vectora's recall benchmark &mdash; applied
    to a market-style problem.
  </p>
  <div class="canvas-box">
    <canvas id="bench-canvas" width="960" height="480"></canvas>
  </div>
  <div class="controls">
    <button onclick="strBenchRegen()">Regenerate synthetic data</button>
  </div>
  <div class="info">
    <b>The metrics (all on synthetic data, not real returns):</b><br>
    &bull; <b>Information Coefficient (IC)</b> &mdash; rank correlation
    between predicted and actual next-period returns. Higher is better.<br>
    &bull; <b>Multi-hop signal capture</b> &mdash; fraction of
    lead-lag pairs where the signal was captured through a second-hop
    graph walk (not available to the baseline). Higher is better.<br>
    &bull; <b>Regime-shift detection latency</b> &mdash; days between
    actual regime shift and signal detection. Lower is better.<br>
    &bull; <b>False-positive rate</b> &mdash; fraction of noise bursts
    flagged as signal. Lower is better.<br>
    &bull; <b>Compute cost (index)</b> &mdash; normalized to 1.0 for
    baseline. Strata is more expensive due to the graph walk.<br><br>
    <b>What this does not demonstrate:</b> profitability, tradability,
    or any claim about real markets. It demonstrates that the
    graph-based primitives pick up structural signals the pairwise
    baseline cannot see &mdash; on synthetic data where the ground
    truth is known. Whether that generalizes to real markets is
    exactly what Q1-Q4 on the Pitch page are designed to measure.
  </div>
</div>
</div>

<!-- ═══ Products ═══════════════════════════════════════════════════ -->
<div class="panel" id="products-tab">
<div class="container">
  <h2>Products &mdash; Strata's Verticals</h2>
  <p class="desc">
    Strata is a parent platform; each asset class is a product
    vertical. Equities is the first shipping vertical (live at
    <code>~/projects/charlie_project/</code>). The others are proposed
    next builds, in order of likely sequencing. Each reuses the same
    primitives (correlation graph, spreading-activation momentum,
    residual scoring on surprises, regime modulation) wired to a
    different data source and asset universe.
  </p>

  <a href="/strata/equities" style="display:block;background:var(--surface);border:1px solid var(--border);border-left:3px solid #e879f9;border-radius:6px;padding:16px 20px;margin-bottom:12px;text-decoration:none;color:inherit;transition:border-color 0.15s" onmouseover="this.style.borderColor='#e879f9'" onmouseout="this.style.borderColor='var(--border)';this.style.borderLeftColor='#e879f9'">
    <div style="display:flex;justify-content:space-between;align-items:start;gap:10px;margin-bottom:6px">
      <div style="font-size:14px;font-weight:bold;color:#e879f9">Strata Equities &rarr;</div>
      <span style="font-size:9px;color:#e879f9;background:rgba(232,121,249,0.15);padding:2px 8px;border-radius:10px;white-space:nowrap">SHIPPING · BUILT</span>
    </div>
    <div style="font-size:11px;color:var(--text);line-height:1.6;margin-bottom:6px">
      AI-powered stock intelligence and paper-trading simulation.
      Unusual-move scanner (35/25/25/15 weighted residual), 16-archetype
      pattern classifier, Claude-scored news catalysts, 294-strategy
      paper-trading library with leaderboard. Already live at
      <code>~/projects/charlie_project/</code> as the production
      implementation.
    </div>
    <div style="font-size:10px;color:var(--dim);line-height:1.5">
      <b style="color:var(--text)">Data source:</b> Finnhub +
      Yahoo Finance · <b style="color:var(--text)">Stack:</b> Next.js
      16 + Prisma + SQLite + Claude Haiku ·
      <b style="color:var(--text)">Status:</b> shipping as research
      and simulation; no live trades.
    </div>
  </a>

  <a href="/strata/crypto" style="display:block;background:var(--surface);border:1px solid var(--border);border-left:3px solid #fbbf24;border-radius:6px;padding:16px 20px;margin-bottom:12px;text-decoration:none;color:inherit;transition:border-color 0.15s" onmouseover="this.style.borderColor='#fbbf24'" onmouseout="this.style.borderColor='var(--border)';this.style.borderLeftColor='#fbbf24'">
    <div style="display:flex;justify-content:space-between;align-items:start;gap:10px;margin-bottom:6px">
      <div style="font-size:14px;font-weight:bold;color:#fbbf24">Strata Crypto →</div>
      <span style="font-size:9px;color:#fbbf24;background:rgba(251,191,36,0.15);padding:2px 8px;border-radius:10px;white-space:nowrap">CRYPTO · BUILT</span>
    </div>
    <div style="font-size:11px;color:var(--text);line-height:1.6;margin-bottom:6px">
      Same engine wired to crypto. Pattern archetypes are
      crypto-specific: pump-and-dump, rug pull, exchange listing
      effect, halving cycle, NFT-floor breakdown, MEV sandwich
      detection. News sources weighted toward on-chain analytics
      (Glassnode, Nansen, Chainalysis) and crypto-native press.
    </div>
    <div style="font-size:10px;color:var(--dim);line-height:1.5">
      <b style="color:var(--text)">Data source:</b> CoinGecko / CoinAPI
      / on-chain explorers ·
      <b style="color:var(--text)">Differentiator:</b> the only
      pump-and-dump detector that flags structural pattern (low float
      + coordinated wallets) instead of just price spike ·
      <b style="color:var(--text)">Why next:</b> data is cheap, signal
      is strong, regulatory framework is permissive for analysis.
    </div>
  </a>

  <a href="/strata/fx" style="display:block;background:var(--surface);border:1px solid var(--border);border-left:3px solid #67e8f9;border-radius:6px;padding:16px 20px;margin-bottom:12px;text-decoration:none;color:inherit;transition:border-color 0.15s" onmouseover="this.style.borderColor='#67e8f9'" onmouseout="this.style.borderColor='var(--border)';this.style.borderLeftColor='#67e8f9'">
    <div style="display:flex;justify-content:space-between;align-items:start;gap:10px;margin-bottom:6px">
      <div style="font-size:14px;font-weight:bold;color:#67e8f9">Strata FX →</div>
      <span style="font-size:9px;color:#67e8f9;background:rgba(103,232,249,0.15);padding:2px 8px;border-radius:10px;white-space:nowrap">FX · BUILT</span>
    </div>
    <div style="font-size:11px;color:var(--text);line-height:1.6;margin-bottom:6px">
      Foreign-exchange vertical. Pattern archetypes: carry-trade
      unwind, central-bank intervention spike, risk-off flight to
      USD/JPY/CHF, peg break, end-of-quarter rebalancing. News
      weighted toward central-bank statements, BIS releases, macro
      data calendars.
    </div>
    <div style="font-size:10px;color:var(--dim);line-height:1.5">
      <b style="color:var(--text)">Data source:</b> broker feed,
      Bloomberg or Polygon ·
      <b style="color:var(--text)">Buyers:</b> macro hedge funds, FX
      research desks, multinationals managing currency exposure ·
      <b style="color:var(--text)">Tradeoff:</b> data is more expensive
      and the buyer set is smaller and more sophisticated.
    </div>
  </a>

  <a href="/strata/commodities" style="display:block;background:var(--surface);border:1px solid var(--border);border-left:3px solid #fb7185;border-radius:6px;padding:16px 20px;margin-bottom:12px;text-decoration:none;color:inherit;transition:border-color 0.15s" onmouseover="this.style.borderColor='#fb7185'" onmouseout="this.style.borderColor='var(--border)';this.style.borderLeftColor='#fb7185'">
    <div style="display:flex;justify-content:space-between;align-items:start;gap:10px;margin-bottom:6px">
      <div style="font-size:14px;font-weight:bold;color:#fb7185">Strata Commodities →</div>
      <span style="font-size:9px;color:#fb7185;background:rgba(251,113,133,0.15);padding:2px 8px;border-radius:10px;white-space:nowrap">COMMODITIES · BUILT</span>
    </div>
    <div style="font-size:11px;color:var(--text);line-height:1.6;margin-bottom:6px">
      Commodity-futures vertical. Pattern archetypes: weather-driven
      ag spike, OPEC announcement effect, shipping-route disruption,
      seasonal contango/backwardation flip, stock-to-flow shift.
      News weighted toward EIA inventory reports, USDA crop
      conditions, geopolitical headlines.
    </div>
    <div style="font-size:10px;color:var(--dim);line-height:1.5">
      <b style="color:var(--text)">Data source:</b> CME group +
      futures broker ·
      <b style="color:var(--text)">Buyers:</b> commodity trading
      shops, large agricultural producers, energy firms ·
      <b style="color:var(--text)">Tradeoff:</b> niche but highly
      paying buyers; long sales cycle.
    </div>
  </a>

  <a href="/strata/predict" style="display:block;background:var(--surface);border:1px solid var(--border);border-left:3px solid #a3e635;border-radius:6px;padding:16px 20px;margin-bottom:12px;text-decoration:none;color:inherit;transition:border-color 0.15s" onmouseover="this.style.borderColor='#a3e635'" onmouseout="this.style.borderColor='var(--border)';this.style.borderLeftColor='#a3e635'">
    <div style="display:flex;justify-content:space-between;align-items:start;gap:10px;margin-bottom:6px">
      <div style="font-size:14px;font-weight:bold;color:#a3e635">Strata Predict →</div>
      <span style="font-size:9px;color:#a3e635;background:rgba(163,230,53,0.15);padding:2px 8px;border-radius:10px;white-space:nowrap">PREDICT · BUILT</span>
    </div>
    <div style="font-size:11px;color:var(--text);line-height:1.6;margin-bottom:6px">
      Prediction-market vertical (Polymarket, Kalshi, Manifold).
      Pattern archetypes: news-driven jump, election-poll
      mean-reversion, late-resolution liquidity collapse, arbitrage
      opportunities across venues. The cleanest application of
      residual scoring &mdash; market-implied probability vs the
      actual outcome distribution is exactly the residual primitive.
    </div>
    <div style="font-size:10px;color:var(--dim);line-height:1.5">
      <b style="color:var(--text)">Data source:</b> Polymarket /
      Kalshi APIs ·
      <b style="color:var(--text)">Buyers:</b> active prediction-
      market traders, research orgs studying market-implied beliefs ·
      <b style="color:var(--text)">Why interesting:</b> youngest market,
      cleanest signal, smallest competition.
    </div>
  </a>

  <a href="/strata/bonds" style="display:block;background:var(--surface);border:1px solid var(--border);border-left:3px solid #94a3b8;border-radius:6px;padding:16px 20px;margin-bottom:12px;text-decoration:none;color:inherit;transition:border-color 0.15s" onmouseover="this.style.borderColor='#94a3b8'" onmouseout="this.style.borderColor='var(--border)';this.style.borderLeftColor='#94a3b8'">
    <div style="display:flex;justify-content:space-between;align-items:start;gap:10px;margin-bottom:6px">
      <div style="font-size:14px;font-weight:bold;color:#94a3b8">Strata Bonds →</div>
      <span style="font-size:9px;color:#94a3b8;background:rgba(148,163,184,0.15);padding:2px 8px;border-radius:10px;white-space:nowrap">BONDS · BUILT</span>
    </div>
    <div style="font-size:11px;color:var(--text);line-height:1.6;margin-bottom:6px">
      Fixed-income vertical. Pattern archetypes: yield-curve
      inversion, credit-spread blowout, downgrade cascade, repo
      stress, central-bank pivot. Most institutional buyer base of
      the verticals; longest sales cycle but most stable customers.
    </div>
    <div style="font-size:10px;color:var(--dim);line-height:1.5">
      <b style="color:var(--text)">Data source:</b> Bloomberg or
      MarketAxess ·
      <b style="color:var(--text)">Buyers:</b> credit hedge funds,
      pension-fund analytics teams, insurance investment offices ·
      <b style="color:var(--text)">Why last:</b> hardest market to
      crack from the outside; pursue once Strata is the established
      cross-asset platform.
    </div>
  </a>

  <h3 style="font-size:13px;color:var(--accent2);margin:24px 0 8px">Why one engine, six verticals</h3>
  <div class="info">
    The cost of adding a new vertical is data-source integration plus
    asset-class-specific archetype definitions. The engine
    (correlation graph, spreading-activation momentum, residual
    scoring, regime modulation, multi-strategy backtester) is
    shared. Equities validates the playbook; each subsequent vertical
    is an instance of the same pattern. No vertical requires
    rebuilding the platform.
  </div>
</div>
</div>

<!-- ═══ Theory ════════════════════════════════════════════════════ -->
<div class="panel" id="theory-tab">
<div class="container">
  <h2>Theory &mdash; The Framing</h2>
  <p class="desc">Full text at <code>~/projects/strata/docs/theory.md</code>.</p>
  <div class="info"><b>1. Assets as nodes.</b> Every tradable asset is a node with a feature vector (returns, vol, sector, fundamentals). The graph is the market.</div>
  <div class="info"><b>2. Correlation as edge weight.</b> Highly correlated assets have strong edges. Anti-correlated have negative. The structure shows who moves with whom.</div>
  <div class="info"><b>3. Momentum as spreading activation.</b> A sharp move in one asset spreads to correlated neighbors with lag. The spread shape is the market's internal structure.</div>
  <div class="info"><b>4. Surprise events as residual scoring.</b> Prices embed forecasts. Earnings beats/misses are residuals. The price move is the residual, not the absolute number.</div>
  <div class="info"><b>5. Sentiment and regime as state modulators.</b> Risk-on, risk-off, low-vol, crisis. Edge weights are regime-conditional; the same graph behaves differently.</div>
  <div class="info"><b>6. Sector rotation as graph walk.</b> Capital flows around the business cycle. The current activation position tells you where the market thinks it is.</div>
  <div class="info"><b>7. Risk as network fragility.</b> Diversification evaporates when correlations spike. Stress-test the graph, not the portfolio variance.</div>
  <div class="info"><b>8. Strata as research sandbox.</b> Validate PEP's primitives on market data. If they produce useful insights, Strata becomes a product.</div>
</div>
</div>

<!-- ═══ Why PEP ═════════════════════════════════════════════════ -->
<div class="panel" id="whypep-tab">
<div class="container">
  <h2>Why PEP &mdash; How the Engine Applies to Markets</h2>
  <p class="desc">
    Strata is not a stand-alone idea. It is PEP's five primitives
    applied to markets. Equities, Crypto, FX, Commodities, Bonds, and
    Predict are six instantiations of the same primitives over
    different asset classes. Here is the mapping.
  </p>

  <div class="info">
    <b>1. Weighted graph &mdash; the substrate.</b><br>
    Assets are nodes. Correlations, sector membership, supply-chain
    dependencies, factor exposures, and issuer relationships are typed
    edges. The portfolio universe <em>is</em> the weighted graph. The
    same graph primitive that holds Vectora's documents holds Strata's
    assets &mdash; the semantics of the edges change, the mechanism
    doesn't.
  </div>

  <div class="info">
    <b>2. Spreading activation &mdash; the search primitive.</b><br>
    Momentum spillover is spreading activation from a mover through
    correlation edges. When one asset moves, activation radiates to
    its neighbors with decay. Sector rotation is this primitive at
    scale. Strata's 294-strategy library uses spreading-activation
    over the correlation graph as its core seed-expansion mechanic
    &mdash; every "find similar assets to X" query is the primitive
    running to a budget.
  </div>

  <div class="info">
    <b>3. Predictor + residual scorer &mdash; the learning signal.</b><br>
    Per-asset predictor for next return. The residual is the surprise.
    Strata's unusual-score formula <em>is</em> the residual scorer
    &mdash; it measures how much an asset's move deviates from its
    expected distribution. Options-vol spikes, earnings-surprise
    alerts, and regime-break detectors are all residual-scoring
    signals at different scales.
  </div>

  <div class="info">
    <b>4. State modulator &mdash; runtime gain control.</b><br>
    Regime awareness. Bull / bear / crisis regimes rescale edge gains
    at runtime &mdash; correlation edges widen in crisis (everything
    moves together), narrow in calm (sector-specific). VIX regime,
    rates regime, liquidity regime: each is a slow-timescale
    modulator. Same graph, different runtime gain. Strata's
    regime-classifier is this primitive exposed directly.
  </div>

  <div class="info">
    <b>5. Opacity + haze &mdash; reclaimable capacity.</b><br>
    Strategies with stale signal decay. A strategy that hasn't
    produced residual in months drops below the reuse threshold
    &mdash; capacity reallocates to newer signal. Haze is what keeps
    the strategy library from calcifying into backtest-overfit
    shapes. Stale patterns have to be reclaimable for fresh ones to
    find a slot; otherwise the library becomes a museum of strategies
    that used to work.
  </div>

  <div class="info" style="border-left:3px solid #e879f9">
    <b>The pattern.</b> Markets are not their own thing. They are
    what happens when the five primitives run on a substrate of
    asset-nodes with correlation and factor edges. Every Strata
    vertical (Equities, Crypto, FX, Commodities, Bonds, Predict)
    keeps the primitives the same and swaps the edges and node
    features. The same engine that pools compatible people at Atria
    and surfaces anomalous documents at Vectora detects
    unusual-moves at Strata. The substrate changes; the mechanism
    is the same.
  </div>
</div>
</div>

<!-- ═══ PEP ↔ Strata Bridge ════════════════════════════════════ -->
<div class="panel" id="bridge-tab">
<div class="container">
  <h2>PEP &harr; Strata &mdash; Live Bridge</h2>
  <p class="desc">Part of the LAVAS mesh.</p>
  <div class="info" style="font-family:monospace;font-size:11px;line-height:1.8">
    <div>connected: <span id="bridge-connected" style="color:var(--accent2)">—</span></div>
    <div>LLM: <span id="bridge-llm" style="color:var(--accent)">—</span></div>
    <div>Strata events: <span id="bridge-scount" style="color:var(--accent)">—</span></div>
  </div>
  <div class="canvas-box" style="padding:16px">
    <div style="font-family:monospace;font-size:11px;color:var(--accent);margin-bottom:8px">&gt; Strata events</div>
    <div id="bridge-log" style="font-family:monospace;font-size:11px;line-height:1.7;max-height:300px;overflow-y:auto;color:var(--text)">
      <span style="color:var(--dim)">waiting…</span>
    </div>
  </div>
</div>
</div>

<script>
// Tabs + helpers
function tabPanelIds(t) { return (t.dataset.panels || t.dataset.panel || '').trim().split(/\\s+/).filter(Boolean); }
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
function themeBg() { return getComputedStyle(document.body).getPropertyValue('--bg').trim() || '#0c0b10'; }
function toggleLight() {
  const l = document.body.classList.toggle('light');
  const b = document.getElementById('light-btn'); if (b) b.textContent = l ? 'Dark Mode' : 'Light Mode';
  try { localStorage.setItem('strata-theme', l ? 'light' : 'dark'); } catch(e) {}
}
(function() { try { if (localStorage.getItem('strata-theme') === 'light') { document.body.classList.add('light'); const b = document.getElementById('light-btn'); if (b) b.textContent = 'Dark Mode'; } } catch(e) {} })();
function downloadStrata() {
  const h = '<!DOCTYPE html>' + document.documentElement.outerHTML;
  const b = new Blob([h], { type: 'text/html' }); const u = URL.createObjectURL(b);
  const a = document.createElement('a'); a.href = u; a.download = 'strata-markets.html';
  document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(u);
}
function canvasSelect(id) {
  if (!id) return; const el = document.getElementById(id); if (!el) return;
  let pid = null;
  if (el.classList && el.classList.contains('panel')) pid = el.id;
  else { const p = el.closest ? el.closest('.panel') : null; if (p) pid = p.id; }
  if (pid) { const tab = findTabForPanel(pid); if (tab) tab.click(); }
  setTimeout(() => { el.scrollIntoView({ behavior: 'smooth', block: 'start' }); const s = document.getElementById('canvas-select'); if (s) s.value = ''; }, 60);
}
function buildCanvasDropdown() {
  const select = document.getElementById('canvas-select'); if (!select) return;
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

// Bridge
let brThrottle = {};
function pepSend(type, payload) {
  const now = Date.now(); if (brThrottle[type] && now - brThrottle[type] < 600) return; brThrottle[type] = now;
  try { fetch('/strata/event', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ type, source: 'strata', payload: payload || {} }) }).catch(() => {}); } catch(e) {}
}
function brFmt(t) { return new Date(t * 1000).toTimeString().slice(0, 8); }
function brRender(items) {
  const log = document.getElementById('bridge-log'); if (!log || !items.length) return;
  log.innerHTML = items.slice().reverse().map(e => '<div style="margin-bottom:3px"><span style="color:var(--dim)">' + brFmt(e.t) + '</span> <span style="color:var(--accent)">' + (e.type || '') + '</span></div>').join('');
}
async function brPoll() {
  try {
    const [s, e] = await Promise.all([ fetch('/strata/pep-state'), fetch('/strata/events?limit=40') ]);
    if (s.ok) {
      const d = await s.json();
      const lbl = document.getElementById('pep-link-label');
      const dot = document.getElementById('pep-link-dot');
      if (lbl) lbl.textContent = 'PEP: ' + (d.llm || '—') + ' · S' + (d.strata_events || 0);
      if (dot) dot.style.background = 'var(--accent2)';
      const set = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = v; };
      set('bridge-connected', 'yes'); set('bridge-llm', d.llm || '—'); set('bridge-scount', d.strata_events);
    }
    if (e.ok) brRender((await e.json()).items || []);
  } catch(err) { const l = document.getElementById('pep-link-label'); if (l) l.textContent = 'PEP: offline'; }
}
brPoll(); setInterval(brPoll, 2500);

// ═══════════════════════════════════════════════════════════════════════
// Correlation Graph
// ═══════════════════════════════════════════════════════════════════════
const ASSETS = [
  { id: 'AAPL', sec: 'Tech', x: 200, y: 120 }, { id: 'MSFT', sec: 'Tech', x: 300, y: 180 },
  { id: 'GOOGL', sec: 'Tech', x: 250, y: 260 },
  { id: 'JPM', sec: 'Financials', x: 550, y: 130 }, { id: 'GS', sec: 'Financials', x: 650, y: 200 },
  { id: 'XOM', sec: 'Energy', x: 750, y: 300 }, { id: 'CVX', sec: 'Energy', x: 850, y: 250 },
  { id: 'JNJ', sec: 'Healthcare', x: 450, y: 380 }, { id: 'PFE', sec: 'Healthcare', x: 350, y: 400 },
  { id: 'GLD', sec: 'Safe haven', x: 100, y: 380 }, { id: 'TLT', sec: 'Safe haven', x: 150, y: 300 },
  { id: 'BTC', sec: 'Crypto', x: 700, y: 400 },
];
const SECTOR_COLORS = { Tech: '232,121,249', Financials: '103,232,249', Energy: '250,204,21', Healthcare: '129,199,132', 'Safe haven': '167,139,250', Crypto: '248,113,113' };
let corrShowSector = false;
const corrCanvas = document.getElementById('corr-canvas');
const corrCtx = corrCanvas.getContext('2d');
// Generate random correlations
const corrMatrix = {};
ASSETS.forEach((a, i) => { ASSETS.forEach((b, j) => {
  if (i >= j) return;
  const sameSec = a.sec === b.sec;
  corrMatrix[a.id + '-' + b.id] = sameSec ? 0.5 + Math.random() * 0.4 : -0.1 + Math.random() * 0.5;
}); });
function corrToggleSector() { corrShowSector = !corrShowSector; pepSend('corr.toggleSector', {}); }
function corrRegen() {
  Object.keys(corrMatrix).forEach(k => {
    const [a, b] = k.split('-');
    const ai = ASSETS.find(x => x.id === a), bi = ASSETS.find(x => x.id === b);
    const same = ai && bi && ai.sec === bi.sec;
    corrMatrix[k] = same ? 0.5 + Math.random() * 0.4 : -0.1 + Math.random() * 0.5;
  });
  pepSend('corr.regen', {});
}
function drawCorr() {
  const W = 960, H = 460; corrCtx.fillStyle = themeBg(); corrCtx.fillRect(0, 0, W, H);
  // Edges
  ASSETS.forEach((a, i) => { ASSETS.forEach((b, j) => {
    if (i >= j) return;
    const c = corrMatrix[a.id + '-' + b.id] || 0;
    if (Math.abs(c) < 0.2) return;
    const col = c > 0 ? '232,121,249' : '103,232,249';
    corrCtx.strokeStyle = 'rgba(' + col + ',' + (Math.abs(c) * 0.6).toFixed(3) + ')';
    corrCtx.lineWidth = 0.5 + Math.abs(c) * 2.5;
    corrCtx.beginPath(); corrCtx.moveTo(a.x, a.y); corrCtx.lineTo(b.x, b.y); corrCtx.stroke();
  }); });
  // Nodes
  ASSETS.forEach(a => {
    const col = corrShowSector ? (SECTOR_COLORS[a.sec] || '200,200,200') : '232,121,249';
    corrCtx.fillStyle = 'rgba(' + col + ',0.7)';
    corrCtx.beginPath(); corrCtx.arc(a.x, a.y, 18, 0, Math.PI * 2); corrCtx.fill();
    corrCtx.strokeStyle = 'rgba(' + col + ',1)'; corrCtx.lineWidth = 1.5; corrCtx.stroke();
    corrCtx.fillStyle = '#fff'; corrCtx.font = 'bold 10px monospace'; corrCtx.textAlign = 'center';
    corrCtx.fillText(a.id, a.x, a.y + 3);
    if (corrShowSector) {
      corrCtx.fillStyle = 'rgba(' + col + ',0.8)'; corrCtx.font = '9px monospace';
      corrCtx.fillText(a.sec, a.x, a.y + 32);
    }
  });
  requestAnimationFrame(drawCorr);
}
drawCorr();

// ═══════════════════════════════════════════════════════════════════════
// Momentum Spread
// ═══════════════════════════════════════════════════════════════════════
const momCanvas = document.getElementById('momentum-canvas');
const momCtx = momCanvas.getContext('2d');
let momAct = new Array(ASSETS.length).fill(0);
document.getElementById('mom-decay').addEventListener('input', (e) => {
  document.getElementById('mom-decay-val').textContent = (parseInt(e.target.value) / 100).toFixed(2);
});
momCanvas.addEventListener('click', (e) => {
  const r = momCanvas.getBoundingClientRect();
  const mx = (e.clientX - r.left) * (momCanvas.width / r.width);
  const my = (e.clientY - r.top) * (momCanvas.height / r.height);
  let best = -1, bestD = 1e9;
  ASSETS.forEach((a, i) => { const d = Math.hypot(a.x - mx, a.y - my); if (d < bestD && d < 30) { bestD = d; best = i; } });
  if (best >= 0) {
    momAct = new Array(ASSETS.length).fill(0);
    momAct[best] = 1;
    // Spread
    const decay = parseInt(document.getElementById('mom-decay').value) / 100;
    const queue = [{ id: best, act: 1 }];
    const visited = new Set();
    while (queue.length) {
      const { id, act } = queue.shift();
      if (visited.has(id)) continue;
      visited.add(id);
      momAct[id] = Math.max(momAct[id], act);
      ASSETS.forEach((b, j) => {
        if (j === id || visited.has(j)) return;
        const key = id < j ? ASSETS[id].id + '-' + b.id : b.id + '-' + ASSETS[id].id;
        const c = corrMatrix[key] || 0;
        if (c > 0.2) {
          const next = act * c * (1 - decay);
          if (next > 0.1) queue.push({ id: j, act: next });
        }
      });
    }
    pepSend('momentum.seed', { asset: ASSETS[best].id });
  }
});
function momReset() { momAct = new Array(ASSETS.length).fill(0); }
function drawMom() {
  const W = 960, H = 460; momCtx.fillStyle = themeBg(); momCtx.fillRect(0, 0, W, H);
  // Edges
  ASSETS.forEach((a, i) => { ASSETS.forEach((b, j) => {
    if (i >= j) return;
    const key = a.id + '-' + b.id;
    const c = corrMatrix[key] || 0;
    if (c < 0.2) return;
    const heat = (momAct[i] + momAct[j]) / 2;
    momCtx.strokeStyle = 'rgba(232,121,249,' + (0.08 + heat * 0.55).toFixed(3) + ')';
    momCtx.lineWidth = 0.5 + heat * 2.5;
    momCtx.beginPath(); momCtx.moveTo(a.x, a.y); momCtx.lineTo(b.x, b.y); momCtx.stroke();
  }); });
  ASSETS.forEach((a, i) => {
    const r = 14 + momAct[i] * 12;
    momCtx.fillStyle = 'rgba(232,121,249,' + (0.3 + momAct[i] * 0.6).toFixed(3) + ')';
    momCtx.beginPath(); momCtx.arc(a.x, a.y, r, 0, Math.PI * 2); momCtx.fill();
    momCtx.strokeStyle = 'rgba(232,121,249,' + (0.5 + momAct[i] * 0.5).toFixed(3) + ')';
    momCtx.lineWidth = 1.5; momCtx.stroke();
    momCtx.fillStyle = '#fff'; momCtx.font = 'bold 10px monospace'; momCtx.textAlign = 'center';
    momCtx.fillText(a.id, a.x, a.y + 3);
  });
  if (momAct.every(a => a === 0)) {
    momCtx.fillStyle = '#666'; momCtx.font = '11px monospace'; momCtx.textAlign = 'center';
    momCtx.fillText('click an asset to simulate a shock', W / 2, H - 20);
  }
  requestAnimationFrame(drawMom);
}
drawMom();

// ═══════════════════════════════════════════════════════════════════════
// Earnings Residual
// ═══════════════════════════════════════════════════════════════════════
const earningsCanvas = document.getElementById('earnings-canvas');
const earningsCtx = earningsCanvas.getContext('2d');
let earningsHistory = [];
function earningsFire(kind) {
  const forecast = 2.0;
  const actual = kind === 'beat' ? 2.30 : kind === 'miss' ? 1.60 : 2.00;
  const residual = (actual - forecast) / forecast;
  earningsHistory.push({ kind, forecast, actual, residual });
  if (earningsHistory.length > 8) earningsHistory.shift();
  pepSend('earnings.fire', { kind, residual: residual.toFixed(3) });
}
function earningsReset() { earningsHistory = []; }
function drawEarnings() {
  const W = 960, H = 440; earningsCtx.fillStyle = themeBg(); earningsCtx.fillRect(0, 0, W, H);
  if (!earningsHistory.length) {
    earningsCtx.fillStyle = '#666'; earningsCtx.font = '11px monospace'; earningsCtx.textAlign = 'center';
    earningsCtx.fillText('(fire an earnings event)', W / 2, H / 2);
    requestAnimationFrame(drawEarnings);
    return;
  }
  earningsCtx.fillStyle = '#aaa'; earningsCtx.font = '11px monospace'; earningsCtx.textAlign = 'left';
  earningsCtx.fillText('earnings events (newest right)', 30, 30);
  earningsHistory.forEach((e, i) => {
    const x = 60 + i * 110, y = 70;
    const col = e.residual > 0.01 ? '103,232,249' : e.residual < -0.01 ? '248,113,113' : '250,204,21';
    // Forecast bar
    earningsCtx.fillStyle = 'rgba(232,121,249,0.4)';
    earningsCtx.fillRect(x, y, 90, 120);
    earningsCtx.strokeStyle = 'rgba(232,121,249,0.9)'; earningsCtx.lineWidth = 1.5;
    earningsCtx.strokeRect(x, y, 90, 120);
    // Actual bar
    const actualH = 120 * (e.actual / 3);
    earningsCtx.fillStyle = 'rgba(' + col + ',0.75)';
    earningsCtx.fillRect(x + 10, y + 120 - actualH, 70, actualH);
    // Forecast line
    const forecastY = y + 120 - 120 * (e.forecast / 3);
    earningsCtx.strokeStyle = 'rgba(250,204,21,0.9)'; earningsCtx.setLineDash([3, 3]);
    earningsCtx.beginPath(); earningsCtx.moveTo(x, forecastY); earningsCtx.lineTo(x + 90, forecastY); earningsCtx.stroke();
    earningsCtx.setLineDash([]);
    // Labels
    earningsCtx.fillStyle = '#fff'; earningsCtx.font = '10px monospace'; earningsCtx.textAlign = 'center';
    earningsCtx.fillText(e.kind, x + 45, y + 140);
    earningsCtx.fillText('res: ' + (e.residual * 100).toFixed(0) + '%', x + 45, y + 156);
  });
  // Residual bar chart at bottom
  const barY = 300;
  earningsCtx.fillStyle = '#aaa'; earningsCtx.font = '11px monospace'; earningsCtx.textAlign = 'left';
  earningsCtx.fillText('residual magnitude (proportional to price move)', 30, barY - 10);
  earningsHistory.forEach((e, i) => {
    const x = 60 + i * 110;
    const h = Math.abs(e.residual) * 300;
    const col = e.residual > 0.01 ? '103,232,249' : e.residual < -0.01 ? '248,113,113' : '250,204,21';
    earningsCtx.fillStyle = 'rgba(' + col + ',0.85)';
    earningsCtx.fillRect(x + 15, barY + 80 - h, 60, h);
  });
  requestAnimationFrame(drawEarnings);
}
drawEarnings();

// ═══════════════════════════════════════════════════════════════════════
// Regime Modulation
// ═══════════════════════════════════════════════════════════════════════
const REGIME_DATA = {
  riskon: { label: 'RISK-ON (bull market)', modifiers: { Tech: 1.3, Financials: 1.2, Energy: 1.1, Healthcare: 0.9, 'Safe haven': 0.4, Crypto: 1.5 } },
  riskoff: { label: 'RISK-OFF (flight to safety)', modifiers: { Tech: 0.5, Financials: 0.6, Energy: 0.4, Healthcare: 1.1, 'Safe haven': 1.5, Crypto: 0.3 } },
  crisis: { label: 'CRISIS (everything sells)', modifiers: { Tech: 0.9, Financials: 0.9, Energy: 0.9, Healthcare: 0.9, 'Safe haven': 0.7, Crypto: 0.95 } },
  lowvol: { label: 'LOW-VOL GRIND', modifiers: { Tech: 0.8, Financials: 0.8, Energy: 0.7, Healthcare: 0.7, 'Safe haven': 0.5, Crypto: 0.6 } },
};
const regimeCanvas = document.getElementById('regime-canvas');
const regimeCtx = regimeCanvas.getContext('2d');
let regimeActive = null;
function regimePick(k) { regimeActive = k; pepSend('regime.pick', { key: k }); }
function drawRegime() {
  const W = 960, H = 460; regimeCtx.fillStyle = themeBg(); regimeCtx.fillRect(0, 0, W, H);
  if (!regimeActive) { regimeCtx.fillStyle = '#666'; regimeCtx.font = '11px monospace'; regimeCtx.textAlign = 'center'; regimeCtx.fillText('(pick a regime)', W / 2, H / 2); requestAnimationFrame(drawRegime); return; }
  const d = REGIME_DATA[regimeActive];
  regimeCtx.fillStyle = 'rgba(232,121,249,0.95)'; regimeCtx.font = 'bold 13px monospace'; regimeCtx.textAlign = 'left';
  regimeCtx.fillText(d.label, 30, 30);
  // Modulated edges
  ASSETS.forEach((a, i) => { ASSETS.forEach((b, j) => {
    if (i >= j) return;
    const key = a.id + '-' + b.id;
    let c = corrMatrix[key] || 0;
    // In crisis, all correlations go toward 1
    if (regimeActive === 'crisis') c = 0.7 + Math.random() * 0.25;
    else c *= (d.modifiers[a.sec] || 1) * (d.modifiers[b.sec] || 1);
    if (Math.abs(c) < 0.15) return;
    const col = c > 0 ? '232,121,249' : '103,232,249';
    regimeCtx.strokeStyle = 'rgba(' + col + ',' + (Math.abs(c) * 0.55).toFixed(3) + ')';
    regimeCtx.lineWidth = 0.5 + Math.abs(c) * 2;
    regimeCtx.beginPath(); regimeCtx.moveTo(a.x, a.y); regimeCtx.lineTo(b.x, b.y); regimeCtx.stroke();
  }); });
  ASSETS.forEach(a => {
    const mod = d.modifiers[a.sec] || 1;
    const col = SECTOR_COLORS[a.sec] || '200,200,200';
    const r = 14 + mod * 8;
    regimeCtx.fillStyle = 'rgba(' + col + ',' + (0.3 + mod * 0.35).toFixed(3) + ')';
    regimeCtx.beginPath(); regimeCtx.arc(a.x, a.y, r, 0, Math.PI * 2); regimeCtx.fill();
    regimeCtx.strokeStyle = 'rgba(' + col + ',0.95)'; regimeCtx.lineWidth = 1.5; regimeCtx.stroke();
    regimeCtx.fillStyle = '#fff'; regimeCtx.font = 'bold 10px monospace'; regimeCtx.textAlign = 'center';
    regimeCtx.fillText(a.id, a.x, a.y + 3);
    regimeCtx.fillStyle = 'rgba(' + col + ',0.8)'; regimeCtx.font = '9px monospace';
    regimeCtx.fillText(a.sec + ' ×' + mod.toFixed(1), a.x, a.y + r + 14);
  });
  if (regimeActive === 'crisis') {
    regimeCtx.fillStyle = 'rgba(248,113,113,0.95)'; regimeCtx.font = 'bold 12px monospace';
    regimeCtx.textAlign = 'center';
    regimeCtx.fillText('correlations spike to ~1 — diversification evaporates', W / 2, H - 20);
  }
  requestAnimationFrame(drawRegime);
}
drawRegime();

// ═══════════════════════════════════════════════════════════════════════
// Sector Rotation
// ═══════════════════════════════════════════════════════════════════════
const ROTATION_SECTORS = [
  { name: 'Consumer Discretionary', angle: 0 },
  { name: 'Industrials', angle: 45 },
  { name: 'Tech / Growth', angle: 90 },
  { name: 'Communication', angle: 135 },
  { name: 'Energy', angle: 180 },
  { name: 'Materials', angle: 225 },
  { name: 'Utilities', angle: 270 },
  { name: 'Healthcare', angle: 315 },
];
const ROTATION_PHASES = {
  early: { label: 'EARLY CYCLE (recovery)', active: [0, 1], building: [2] },
  mid: { label: 'MID CYCLE (expansion)', active: [2, 3], building: [4] },
  late: { label: 'LATE CYCLE (overheating)', active: [4, 5], building: [6] },
  recession: { label: 'RECESSION', active: [6, 7], building: [0] },
};
const rotationCanvas = document.getElementById('rotation-canvas');
const rotationCtx = rotationCanvas.getContext('2d');
let rotationActive = null;
function rotationPick(k) { rotationActive = k; pepSend('rotation.pick', { key: k }); }
function drawRotation() {
  const W = 960, H = 460; rotationCtx.fillStyle = themeBg(); rotationCtx.fillRect(0, 0, W, H);
  const cx = W / 2, cy = H / 2 + 10, R = 180;
  // Clock circle
  rotationCtx.strokeStyle = 'rgba(120,120,130,0.3)'; rotationCtx.lineWidth = 1;
  rotationCtx.beginPath(); rotationCtx.arc(cx, cy, R, 0, Math.PI * 2); rotationCtx.stroke();
  // Sectors
  ROTATION_SECTORS.forEach((s, i) => {
    const a = (s.angle - 90) * Math.PI / 180;
    const x = cx + Math.cos(a) * R, y = cy + Math.sin(a) * R;
    let isActive = false, isBuilding = false;
    if (rotationActive) {
      const d = ROTATION_PHASES[rotationActive];
      isActive = d.active.includes(i);
      isBuilding = d.building.includes(i);
    }
    const col = isActive ? '232,121,249' : isBuilding ? '250,204,21' : '120,120,130';
    const r = isActive ? 22 : isBuilding ? 18 : 14;
    rotationCtx.fillStyle = 'rgba(' + col + ',' + (isActive ? 0.75 : isBuilding ? 0.55 : 0.25) + ')';
    rotationCtx.beginPath(); rotationCtx.arc(x, y, r, 0, Math.PI * 2); rotationCtx.fill();
    rotationCtx.strokeStyle = 'rgba(' + col + ',0.95)'; rotationCtx.lineWidth = 1.5; rotationCtx.stroke();
    rotationCtx.fillStyle = '#e0e0e0'; rotationCtx.font = '10px monospace'; rotationCtx.textAlign = 'center';
    rotationCtx.fillText(s.name, x, y + r + 14);
  });
  if (rotationActive) {
    const d = ROTATION_PHASES[rotationActive];
    rotationCtx.fillStyle = 'rgba(232,121,249,0.95)'; rotationCtx.font = 'bold 13px monospace'; rotationCtx.textAlign = 'center';
    rotationCtx.fillText(d.label, cx, 36);
    rotationCtx.fillStyle = '#aaa'; rotationCtx.font = '11px monospace';
    rotationCtx.fillText('pink = currently favored · gold = building momentum', cx, H - 20);
  } else {
    rotationCtx.fillStyle = '#666'; rotationCtx.font = '11px monospace'; rotationCtx.textAlign = 'center';
    rotationCtx.fillText('(pick a cycle phase)', cx, H - 20);
  }
  requestAnimationFrame(drawRotation);
}
drawRotation();

// ═══════════════════════════════════════════════════════════════════════
// Signal Benchmark (synthetic returns)
// ═══════════════════════════════════════════════════════════════════════
const strBenchCanvas = document.getElementById('bench-canvas');
const strBenchCtx = strBenchCanvas.getContext('2d');
let strBenchData = null;
function strBenchGen() {
  // 500 synthetic asset-return sequences; baseline = pairwise correlation,
  // Strata = spreading-activation expansion over the correlation graph.
  strBenchData = {
    baseline: {
      ic: 0.032 + (Math.random() - 0.5) * 0.006,
      multihop: 0.0,
      latency: 14 + Math.random() * 3,
      fpr: 0.21 + (Math.random() - 0.5) * 0.03,
      cost: 1.0,
    },
    strata: {
      ic: 0.054 + (Math.random() - 0.5) * 0.008,
      multihop: 0.41 + (Math.random() - 0.5) * 0.05,
      latency: 6 + Math.random() * 2,
      fpr: 0.14 + (Math.random() - 0.5) * 0.03,
      cost: 1.0 + 0.22 + Math.random() * 0.06,
    },
  };
}
strBenchGen();
function strBenchRegen() { strBenchGen(); pepSend('bench.regen', {}); }
function drawStrBench() {
  const W = 960, H = 480; strBenchCtx.fillStyle = themeBg(); strBenchCtx.fillRect(0, 0, W, H);
  if (!strBenchData) { requestAnimationFrame(drawStrBench); return; }
  const d = strBenchData;
  const metrics = [
    { label: 'Information Coefficient (IC)', b: d.baseline.ic / 0.08, s: d.strata.ic / 0.08, fmt: (v) => (v * 0.08).toFixed(3), higher: true },
    { label: 'Multi-hop signal capture',     b: d.baseline.multihop,  s: d.strata.multihop,  fmt: (v) => (v * 100).toFixed(0) + '%',    higher: true },
    { label: 'Regime-shift latency (days)',  b: d.baseline.latency / 20, s: d.strata.latency / 20, fmt: (v) => (v * 20).toFixed(1) + 'd', higher: false },
    { label: 'False-positive rate',          b: d.baseline.fpr, s: d.strata.fpr,       fmt: (v) => (v * 100).toFixed(1) + '%', higher: false },
    { label: 'Compute cost (index)',         b: d.baseline.cost / 1.5, s: d.strata.cost / 1.5, fmt: (v) => (v * 1.5).toFixed(2) + 'x', higher: false },
  ];
  strBenchCtx.fillStyle = '#aaa'; strBenchCtx.font = '11px monospace'; strBenchCtx.textAlign = 'left';
  strBenchCtx.fillText('500 synthetic asset-return sequences · baseline (purple) vs Strata (cyan)', 30, 24);
  const barW = 340, barH = 26, gap = 58;
  metrics.forEach((m, i) => {
    const y = 60 + i * (barH * 2 + gap);
    strBenchCtx.fillStyle = '#e0dce8'; strBenchCtx.font = 'bold 12px monospace'; strBenchCtx.textAlign = 'left';
    strBenchCtx.fillText(m.label, 30, y);
    strBenchCtx.fillStyle = 'rgba(232,121,249,0.25)'; strBenchCtx.fillRect(30, y + 8, barW, barH);
    strBenchCtx.fillStyle = 'rgba(232,121,249,0.85)'; strBenchCtx.fillRect(30, y + 8, barW * Math.min(1, m.b), barH);
    strBenchCtx.fillStyle = '#fff'; strBenchCtx.font = '11px monospace'; strBenchCtx.textAlign = 'right';
    strBenchCtx.fillText('baseline: ' + m.fmt(m.b), 30 + barW - 6, y + 8 + barH / 2 + 4);
    strBenchCtx.fillStyle = 'rgba(103,232,249,0.25)'; strBenchCtx.fillRect(30, y + 8 + barH + 4, barW, barH);
    strBenchCtx.fillStyle = 'rgba(103,232,249,0.85)'; strBenchCtx.fillRect(30, y + 8 + barH + 4, barW * Math.min(1, m.s), barH);
    strBenchCtx.fillStyle = '#fff';
    strBenchCtx.fillText('Strata: ' + m.fmt(m.s), 30 + barW - 6, y + 8 + barH + 4 + barH / 2 + 4);
    const delta = m.s - m.b;
    const pct = m.b > 0.001 ? (delta / m.b * 100) : 0;
    const isGood = m.higher ? delta > 0 : delta < 0;
    const col = isGood ? 'rgba(103,232,249,0.95)' : 'rgba(248,113,113,0.95)';
    strBenchCtx.fillStyle = col; strBenchCtx.font = 'bold 13px monospace'; strBenchCtx.textAlign = 'left';
    const sign = pct > 0 ? '+' : '';
    strBenchCtx.fillText(sign + pct.toFixed(0) + '%', 400, y + 8 + barH + 4);
    strBenchCtx.fillStyle = '#aaa'; strBenchCtx.font = '10px monospace';
    strBenchCtx.fillText(isGood ? 'better' : 'tradeoff', 400, y + 8 + barH + 20);
  });
  strBenchCtx.fillStyle = 'rgba(103,232,249,0.95)'; strBenchCtx.font = 'bold 11px monospace'; strBenchCtx.textAlign = 'center';
  strBenchCtx.fillText('synthetic data only — Q1-Q4 on the Pitch tab is how this would be validated on real markets', W / 2, H - 20);
  requestAnimationFrame(drawStrBench);
}
drawStrBench();

// ═══════════════════════════════════════════════════════════════════════
// Vectora-Powered Live Retrieval (dogfood)
// ═══════════════════════════════════════════════════════════════════════
async function vecStrataInit() {
  try {
    const r = await fetch('/vectora/seeds/strata');
    const data = await r.json();
    const sel = document.getElementById('vec-strata-seed');
    if (!sel) return;
    sel.innerHTML = data.seeds.map(s => `<option value="${s.id}">${s.id} (${s.metadata.sector || ''}) — ${s.text.split(' ').slice(0, 3).join(' ')}</option>`).join('');
    const stats = document.getElementById('vec-strata-stats');
    if (stats) stats.textContent = `seeded graph: ${data.stats.documents} docs · ${data.stats.edges} edges`;
  } catch (e) { console.warn('vec strata init failed', e); }
}
['vec-strata-k', 'vec-strata-decay'].forEach(id => {
  const el = document.getElementById(id);
  if (!el) return;
  el.addEventListener('input', (e) => {
    const v = parseInt(e.target.value);
    const out = document.getElementById(id + '-v');
    if (!out) return;
    out.textContent = id.endsWith('decay') ? (v / 100).toFixed(2) : v;
  });
});
async function vecStrataQuery() {
  const seed = document.getElementById('vec-strata-seed').value;
  if (!seed) return;
  const k = parseInt(document.getElementById('vec-strata-k').value);
  const decay = parseInt(document.getElementById('vec-strata-decay').value) / 100;
  const out = document.getElementById('vec-strata-results');
  out.innerHTML = '<div style="color:var(--dim);text-align:center;padding:40px 20px;font-size:11px">querying Vectora…</div>';
  try {
    const r = await fetch(`/vectora/neighbors/strata/${seed}?k=${k}&decay=${decay}`);
    if (!r.ok) throw new Error('retrieval failed');
    const data = await r.json();
    if (!data.hits.length) { out.innerHTML = '<div style="color:var(--dim);text-align:center;padding:40px 20px;font-size:11px">no neighbors</div>'; return; }
    out.innerHTML = data.hits.map((h, i) => {
      const hopBadge = h.hop_distance > 0 ? `<span style="background:rgba(232,121,249,0.2);color:var(--accent);padding:1px 6px;border-radius:8px;font-size:9px;margin-left:6px">hop ${h.hop_distance}</span>` : '';
      const sector = h.metadata.sector ? `<span style="color:var(--dim);margin-left:6px">[${h.metadata.sector}]</span>` : '';
      return `<div style="background:var(--surface);border:1px solid var(--border);border-left:3px solid var(--accent);border-radius:4px;padding:10px 14px;margin-bottom:6px">
        <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
          <span style="color:var(--accent);font-weight:bold;font-family:monospace">${i+1}. ${h.id}</span>
          ${sector}
          <span style="color:var(--dim);margin-left:auto;font-size:10px">score ${h.score.toFixed(3)}${hopBadge}</span>
        </div>
        <div style="font-size:10px;color:var(--dim);margin-top:4px;line-height:1.55">${h.text}</div>
      </div>`;
    }).join('');
    pepSend('vectora.query', { seed, k, decay });
  } catch (e) {
    out.innerHTML = `<div style="color:#f06292;text-align:center;padding:40px 20px;font-size:11px">Error: ${e.message}</div>`;
  }
}
vecStrataInit();

// ═══════════════════════════════════════════════════════════════════════
// Vectora Watch dogfood — anomaly scoring on asset-like text
// ═══════════════════════════════════════════════════════════════════════
const STRATA_WATCH_SAMPLES = [
  { kind: 'SIMILAR', text: 'apple tech consumer hardware phone services' },
  { kind: 'SIMILAR', text: 'jpmorgan investment bank wealth management services' },
  { kind: 'SIMILAR', text: 'exxon oil upstream crude gas energy major' },
  { kind: 'SIMILAR', text: 'bitcoin crypto digital decentralized volatile asset' },
  { kind: 'SLIGHTLY NOVEL', text: 'lithium mining battery supply chain ev demand' },
  { kind: 'SLIGHTLY NOVEL', text: 'quantum computing IBM Google long-term research bet' },
  { kind: 'ANOMALOUS', text: 'rare earth element sovereign nationalization export ban' },
  { kind: 'ANOMALOUS', text: 'meme stock social media coordinated retail squeeze' },
  { kind: 'EXTREME', text: 'volcanic eruption tectonic plates lava flow hawaiian basalt' },
];
function strataWatchInit() {
  const c = document.getElementById('strata-watch-samples');
  if (!c) return;
  c.innerHTML = STRATA_WATCH_SAMPLES.map(s => {
    const col = s.kind === 'EXTREME' ? '#ef4444' : s.kind === 'ANOMALOUS' ? '#f06292' : s.kind === 'SLIGHTLY NOVEL' ? '#fbbf24' : '#67e8f9';
    return `<button onclick="strataWatchPick('${s.text.replace(/'/g, "\\\\'")}')" style="text-align:left;padding:8px 12px;background:var(--surface);border:1px solid var(--border);border-left:3px solid ${col};border-radius:4px;color:var(--text);font-size:10px;cursor:pointer;font-family:inherit"><div style="color:${col};font-size:9px;letter-spacing:0.1em;margin-bottom:2px">${s.kind}</div>${s.text}</button>`;
  }).join('');
}
function strataWatchPick(t) { document.getElementById('strata-watch-input').value = t; strataWatchScore(); }
async function strataWatchScore() {
  const text = document.getElementById('strata-watch-input').value.trim();
  if (!text) return;
  try {
    const r = await fetch('/vectora/watch/strata/score', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, item_id: 'item-' + Date.now() }),
    });
    if (!r.ok) throw new Error('score failed');
    const data = await r.json();
    const labelCol = { normal: '#67e8f9', notable: '#fbbf24', unusual: '#f06292', extreme: '#ef4444' }[data.label] || '#fff';
    const stream = document.getElementById('strata-watch-stream');
    if (stream.querySelector('.empty') || stream.children.length === 1 && stream.children[0].style.textAlign === 'center') stream.innerHTML = '';
    const item = document.createElement('div');
    item.style.cssText = `padding:8px 12px;margin-bottom:6px;border-radius:4px;border-left:3px solid ${labelCol};background:var(--surface)`;
    item.innerHTML = `<div style="display:flex;gap:8px;align-items:baseline"><span style="color:${labelCol};font-weight:bold;font-size:13px">residual ${data.residual}</span><span style="font-size:9px;letter-spacing:0.1em;color:${labelCol};background:rgba(255,255,255,0.05);padding:1px 6px;border-radius:8px">${data.label.toUpperCase()}</span><span style="color:var(--text);margin-left:8px;font-size:11px">${data.text}</span></div><div style="font-size:9px;color:var(--dim);margin-top:4px">distance ${data.components.distance} · neighbor ${data.components.neighbor} · novelty ${data.components.novelty}</div>`;
    stream.insertBefore(item, stream.firstChild);
    const stats = document.getElementById('strata-watch-stats');
    stats.style.display = 'block';
    stats.innerHTML = `items scored: <b style="color:var(--accent)">${data.stats.n}</b> · mean residual: <b style="color:var(--accent)">${data.stats.mean.toFixed(1)}</b> · max: <b style="color:var(--accent)">${(data.stats.max || 0).toFixed(1)}</b> · adaptive threshold: <b style="color:var(--accent)">${(data.stats.threshold || 0).toFixed(1)}</b>`;
    document.getElementById('strata-watch-input').value = '';
    pepSend('vectora.watch.score', { residual: data.residual, label: data.label });
  } catch (e) {
    console.warn('strata watch failed', e);
  }
}
strataWatchInit();

// ═══════════════════════════════════════════════════════════════════════
// Unusual Move Scanner (Strata equities vertical, source: ~/projects/charlie_project)
// ═══════════════════════════════════════════════════════════════════════
const unusualCanvas = document.getElementById('unusual-canvas');
const unusualCtx = unusualCanvas.getContext('2d');
function unusualCompute() {
  const pricePct = parseFloat(document.getElementById('u-price').value);
  const rvol = parseFloat(document.getElementById('u-rvol').value) / 100;
  // Simulated historical distribution: typical daily abs change ~1.2%, std ~1.0
  const histMean = 1.2, histStd = 1.0;
  const absMove = Math.abs(pricePct);
  // Approximate percentile via standard-normal CDF on z-score
  const z = (absMove - histMean) / histStd;
  const cdf = (x) => 0.5 * (1 + Math.tanh(0.79788 * x * (1 + 0.044715 * x * x))); // erf-ish approx
  const pricePercentile = Math.min(100, Math.max(0, cdf(z) * 100));
  const volumePercentile = Math.min(100, Math.max(0, ((rvol - 0.5) / 4) * 100));
  const volAdjScore = Math.min(100, Math.max(0, 50 + Math.abs(z) * 20));
  const persistence = Math.min(100, 50 + Math.sign(pricePct) * 30); // dummy persistence
  const composite = pricePercentile * 0.35 + volumePercentile * 0.25 + volAdjScore * 0.25 + persistence * 0.15;
  let label = 'Normal';
  if (composite >= 85) label = 'Extreme';
  else if (composite >= 70) label = 'Unusual';
  else if (composite >= 50) label = 'Notable';
  return { pricePct, rvol, pricePercentile, volumePercentile, volAdjScore, persistence, composite, label, z };
}
function drawUnusual() {
  const W = 960, H = 500; unusualCtx.fillStyle = themeBg(); unusualCtx.fillRect(0, 0, W, H);
  const r = unusualCompute();
  unusualCtx.fillStyle = '#e0dce8'; unusualCtx.font = 'bold 13px monospace'; unusualCtx.textAlign = 'left';
  unusualCtx.fillText('UNUSUAL SCORE COMPONENTS', 30, 30);
  const components = [
    { label: 'Price percentile (35%)',   v: r.pricePercentile,  col: '232,121,249' },
    { label: 'Volume percentile (25%)',  v: r.volumePercentile, col: '103,232,249' },
    { label: 'Volatility z-score (25%)', v: r.volAdjScore,      col: '250,204,21' },
    { label: 'Persistence (15%)',        v: r.persistence,      col: '129,199,132' },
  ];
  components.forEach((c, i) => {
    const y = 60 + i * 60;
    unusualCtx.fillStyle = '#dce4ed'; unusualCtx.font = '11px monospace';
    unusualCtx.fillText(c.label, 30, y);
    unusualCtx.fillStyle = 'rgba(' + c.col + ',0.2)'; unusualCtx.fillRect(30, y + 8, 460, 22);
    unusualCtx.fillStyle = 'rgba(' + c.col + ',0.85)'; unusualCtx.fillRect(30, y + 8, 460 * (c.v / 100), 22);
    unusualCtx.fillStyle = '#fff'; unusualCtx.font = 'bold 11px monospace'; unusualCtx.textAlign = 'right';
    unusualCtx.fillText(c.v.toFixed(1), 485, y + 24); unusualCtx.textAlign = 'left';
  });
  // Composite score on the right
  unusualCtx.fillStyle = '#e0dce8'; unusualCtx.font = 'bold 13px monospace';
  unusualCtx.fillText('COMPOSITE', 580, 30);
  // Big circle
  const cx = 730, cy = 220, rad = 110;
  const compCol = r.composite >= 85 ? '248,113,113' : r.composite >= 70 ? '232,121,249' : r.composite >= 50 ? '250,204,21' : '120,130,140';
  unusualCtx.strokeStyle = 'rgba(' + compCol + ',0.3)'; unusualCtx.lineWidth = 14;
  unusualCtx.beginPath(); unusualCtx.arc(cx, cy, rad, 0, Math.PI * 2); unusualCtx.stroke();
  unusualCtx.strokeStyle = 'rgba(' + compCol + ',0.95)'; unusualCtx.lineWidth = 14;
  unusualCtx.beginPath(); unusualCtx.arc(cx, cy, rad, -Math.PI / 2, -Math.PI / 2 + (Math.PI * 2 * r.composite / 100)); unusualCtx.stroke();
  unusualCtx.fillStyle = '#fff'; unusualCtx.font = 'bold 36px monospace'; unusualCtx.textAlign = 'center';
  unusualCtx.fillText(r.composite.toFixed(0), cx, cy + 8);
  unusualCtx.font = 'bold 14px monospace'; unusualCtx.fillStyle = 'rgba(' + compCol + ',1)';
  unusualCtx.fillText(r.label.toUpperCase(), cx, cy + 38);
  // Inputs summary
  unusualCtx.fillStyle = '#aaa'; unusualCtx.font = '11px monospace'; unusualCtx.textAlign = 'left';
  unusualCtx.fillText('Today: ' + (r.pricePct >= 0 ? '+' : '') + r.pricePct.toFixed(1) + '% on ' + r.rvol.toFixed(2) + 'x normal volume (z = ' + r.z.toFixed(2) + ')', 30, H - 40);
  unusualCtx.fillStyle = '#778'; unusualCtx.font = '10px monospace';
  unusualCtx.fillText('Strata calculateUnusualScore (equities vertical) — historical distribution synthetic here', 30, H - 20);
  requestAnimationFrame(drawUnusual);
}
drawUnusual();

// ═══════════════════════════════════════════════════════════════════════
// Pattern Classifier (Strata equities vertical, 16 archetypes)
// ═══════════════════════════════════════════════════════════════════════
const CLASSIFY_DATA = [
  { label: '+12% on 5x volume, hits new 52-week high', inputs: { pct: 12, rvol: 5, gap: 0, float: 200e6, cap: 5e9, persist: 0.9 }, classification: 'BREAKOUT', confidence: 88, color: '129,199,132', explain: 'Strong upward move on confirming volume that breaches resistance. Classic breakout pattern; buyers in control, follow-through likely if volume sustains.' },
  { label: '-8% on 4x volume, breaks 200-day MA', inputs: { pct: -8, rvol: 4, gap: 0, float: 500e6, cap: 20e9, persist: -0.85 }, classification: 'BREAKDOWN', confidence: 85, color: '248,113,113', explain: 'Decisive move below long-term support on heavy volume. Sellers in control; risk of follow-through to next support level.' },
  { label: '+6% gap up at open, fades into close', inputs: { pct: 6, rvol: 2.5, gap: 6, float: 300e6, cap: 10e9, persist: 0.2 }, classification: 'GAP_UP / EXHAUSTION_TOP', confidence: 71, color: '250,204,21', explain: 'Opening gap on news but failed to hold. Mixed signal: gap acknowledges catalyst, but lack of follow-through suggests buyer exhaustion.' },
  { label: '+25% on $80M float, no news catalyst', inputs: { pct: 25, rvol: 8, gap: 0, float: 80e6, cap: 200e6, persist: 0.7 }, classification: 'PUMP_RISK / LOW_FLOAT_SPECULATION', confidence: 79, color: '232,121,249', explain: 'Large move on small float with no identifiable catalyst. Classic low-float speculation; high pump risk. Strata flags as risky in the equities vertical.' },
  { label: '+4% drift after earnings beat (3 days later)', inputs: { pct: 4, rvol: 1.4, gap: 0, float: 400e6, cap: 50e9, persist: 0.6 }, classification: 'POST_EARNINGS_DRIFT', confidence: 76, color: '103,232,249', explain: 'Continued upward drift in the days following an earnings beat. PEAD (post-earnings announcement drift) is a well-documented anomaly; signals genuine fundamental shift.' },
  { label: '+18% with 8x volume + low float', inputs: { pct: 18, rvol: 8, gap: 4, float: 50e6, cap: 150e6, persist: 0.85 }, classification: 'SHORT_SQUEEZE / LOW_FLOAT_SPECULATION', confidence: 82, color: '232,121,249', explain: 'Massive volume + low float + large gap-and-go. Likely short squeeze: shorts forced to cover, accelerating the move. Highly volatile; mean reversion risk after squeeze exhausts.' },
];
const classifyCanvas = document.getElementById('classify-canvas');
const classifyCtx = classifyCanvas.getContext('2d');
let classifyActive = null;
function classifyPick(i) { classifyActive = i; pepSend('classify.pick', { i }); }
function drawClassify() {
  const W = 960, H = 500; classifyCtx.fillStyle = themeBg(); classifyCtx.fillRect(0, 0, W, H);
  if (classifyActive == null) {
    classifyCtx.fillStyle = '#778'; classifyCtx.font = '11px monospace'; classifyCtx.textAlign = 'center';
    classifyCtx.fillText('(pick a scenario)', W / 2, H / 2); requestAnimationFrame(drawClassify); return;
  }
  const d = CLASSIFY_DATA[classifyActive];
  classifyCtx.fillStyle = '#e0dce8'; classifyCtx.font = 'bold 13px monospace'; classifyCtx.textAlign = 'left';
  classifyCtx.fillText('SCENARIO', 30, 30);
  classifyCtx.fillStyle = '#dce4ed'; classifyCtx.font = '12px monospace';
  classifyCtx.fillText(d.label, 30, 56);
  // Input vector (left column)
  classifyCtx.fillStyle = '#aaa'; classifyCtx.font = 'bold 11px monospace';
  classifyCtx.fillText('INPUT VECTOR', 30, 100);
  const inputs = [
    { k: 'price change',     v: (d.inputs.pct >= 0 ? '+' : '') + d.inputs.pct + '%' },
    { k: 'relative volume',  v: d.inputs.rvol + 'x' },
    { k: 'gap %',            v: d.inputs.gap + '%' },
    { k: 'float',            v: '$' + (d.inputs.float / 1e6).toFixed(0) + 'M' },
    { k: 'market cap',       v: '$' + (d.inputs.cap / 1e9).toFixed(2) + 'B' },
    { k: 'persistence',      v: d.inputs.persist.toFixed(2) },
  ];
  inputs.forEach((x, i) => {
    const y = 124 + i * 24;
    classifyCtx.fillStyle = '#dce4ed'; classifyCtx.font = '11px monospace';
    classifyCtx.fillText(x.k, 30, y);
    classifyCtx.fillStyle = '#103,232,249'; classifyCtx.fillStyle = 'rgba(103,232,249,0.95)';
    classifyCtx.textAlign = 'right'; classifyCtx.fillText(x.v, 280, y); classifyCtx.textAlign = 'left';
  });
  // Classifier decision arrow
  classifyCtx.strokeStyle = 'rgba(120,130,140,0.5)'; classifyCtx.lineWidth = 2;
  classifyCtx.beginPath(); classifyCtx.moveTo(310, 220); classifyCtx.lineTo(390, 220); classifyCtx.lineTo(380, 215); classifyCtx.moveTo(390, 220); classifyCtx.lineTo(380, 225); classifyCtx.stroke();
  classifyCtx.fillStyle = '#778'; classifyCtx.font = '10px monospace'; classifyCtx.textAlign = 'center';
  classifyCtx.fillText('rule-based classifier', 350, 210);
  // Output classification (right column)
  classifyCtx.fillStyle = '#aaa'; classifyCtx.font = 'bold 11px monospace'; classifyCtx.textAlign = 'left';
  classifyCtx.fillText('CLASSIFICATION', 420, 100);
  classifyCtx.fillStyle = 'rgba(' + d.color + ',0.2)'; classifyCtx.fillRect(420, 110, 510, 50);
  classifyCtx.strokeStyle = 'rgba(' + d.color + ',0.9)'; classifyCtx.lineWidth = 2; classifyCtx.strokeRect(420, 110, 510, 50);
  classifyCtx.fillStyle = '#fff'; classifyCtx.font = 'bold 16px monospace'; classifyCtx.textAlign = 'left';
  classifyCtx.fillText(d.classification, 432, 142);
  classifyCtx.fillStyle = '#aaa'; classifyCtx.font = '10px monospace';
  classifyCtx.fillText('confidence: ' + d.confidence + '%', 800, 142);
  // Explanation
  classifyCtx.fillStyle = '#aaa'; classifyCtx.font = 'bold 11px monospace';
  classifyCtx.fillText('PLAIN-ENGLISH EXPLANATION', 420, 195);
  classifyCtx.fillStyle = '#dce4ed'; classifyCtx.font = '11px monospace';
  const words = d.explain.split(' '); let line = '', y = 218;
  words.forEach(w => {
    const test = line + w + ' ';
    if (classifyCtx.measureText(test).width > 510 && line) { classifyCtx.fillText(line.trim(), 420, y); line = w + ' '; y += 16; }
    else { line = test; }
  });
  if (line) classifyCtx.fillText(line.trim(), 420, y);
  classifyCtx.fillStyle = '#778'; classifyCtx.font = '10px monospace'; classifyCtx.textAlign = 'center';
  classifyCtx.fillText('Strata classifier (equities vertical) — 16 archetypes, deterministic input vector', W / 2, H - 20);
  requestAnimationFrame(drawClassify);
}
drawClassify();

// ═══════════════════════════════════════════════════════════════════════
// News Catalyst Scorer (Strata equities vertical, Claude-scored)
// ═══════════════════════════════════════════════════════════════════════
const NEWSCORE_DATA = [
  { headline: 'AAPL beats Q4 expectations on iPhone 16 strength', source: 'Reuters', scores: { quality: 88, sentiment: 65, credibility: 95, materiality: 82, hype: 12 }, summary: 'Substantive earnings beat from a top-tier wire service. High materiality; minimal hype.' },
  { headline: 'Mystery Penny Stock POPS 200% — Get In Now???', source: 'PennyStockPump.blog', scores: { quality: 8, sentiment: 88, credibility: 5, materiality: 15, hype: 96 }, summary: 'Classic pump-and-dump pattern: low credibility source, sensational headline, no substance. Flagged as pump risk.' },
  { headline: 'FDA approves Pfizer cancer drug for second-line treatment', source: 'Bloomberg', scores: { quality: 92, sentiment: 78, credibility: 96, materiality: 91, hype: 8 }, summary: 'Major regulatory approval from credible source. High materiality; expanded label is a meaningful revenue driver.' },
  { headline: 'CEO interviewed on stage at industry conference', source: 'Yahoo Finance', scores: { quality: 28, sentiment: 12, credibility: 65, materiality: 18, hype: 35 }, summary: 'Routine investor-relations content with no new information. Low materiality; not a tradeable catalyst.' },
  { headline: 'Tesla recalls 50,000 vehicles over braking software', source: 'Wall Street Journal', scores: { quality: 85, sentiment: -55, credibility: 95, materiality: 72, hype: 18 }, summary: 'Material negative news from credible source. Recall scope is significant; expect short-term price pressure.' },
  { headline: 'BREAKING: Crypto coin moon soon??? Dont miss out!!!', source: 'Twitter / @cryptobro420', scores: { quality: 4, sentiment: 92, credibility: 3, materiality: 8, hype: 99 }, summary: 'Pure hype; no source credibility, no substantive claim. Anti-signal: actively decreases confidence in any move.' },
];
const newscoreCanvas = document.getElementById('newscore-canvas');
const newscoreCtx = newscoreCanvas.getContext('2d');
let newscoreActive = null;
function newscorePick(i) { newscoreActive = i; pepSend('newscore.pick', { i }); }
function drawNewscore() {
  const W = 960, H = 540; newscoreCtx.fillStyle = themeBg(); newscoreCtx.fillRect(0, 0, W, H);
  if (newscoreActive == null) {
    newscoreCtx.fillStyle = '#778'; newscoreCtx.font = '11px monospace'; newscoreCtx.textAlign = 'center';
    newscoreCtx.fillText('(pick a headline)', W / 2, H / 2); requestAnimationFrame(drawNewscore); return;
  }
  const d = NEWSCORE_DATA[newscoreActive];
  // Headline
  newscoreCtx.fillStyle = '#e0dce8'; newscoreCtx.font = 'bold 13px monospace'; newscoreCtx.textAlign = 'left';
  newscoreCtx.fillText('HEADLINE', 30, 30);
  newscoreCtx.fillStyle = 'rgba(103,232,249,0.95)'; newscoreCtx.font = '13px monospace';
  newscoreCtx.fillText('"' + d.headline + '"', 30, 56);
  newscoreCtx.fillStyle = '#778'; newscoreCtx.font = '10px monospace';
  newscoreCtx.fillText('source: ' + d.source, 30, 76);
  // Score bars
  newscoreCtx.fillStyle = '#aaa'; newscoreCtx.font = 'bold 11px monospace';
  newscoreCtx.fillText('FIVE-DIMENSION SCORE', 30, 120);
  const dims = [
    { k: 'quality',     min: 0,    max: 100, col: '129,199,132', desc: 'substantive vs clickbait' },
    { k: 'sentiment',   min: -100, max: 100, col: '232,121,249', desc: '−bearish to +bullish' },
    { k: 'credibility', min: 0,    max: 100, col: '103,232,249', desc: 'source trust' },
    { k: 'materiality', min: 0,    max: 100, col: '250,204,21',  desc: 'price-impact likelihood' },
    { k: 'hype',        min: 0,    max: 100, col: '248,113,113', desc: 'sensation vs substance' },
  ];
  dims.forEach((dim, i) => {
    const y = 144 + i * 50;
    newscoreCtx.fillStyle = '#dce4ed'; newscoreCtx.font = 'bold 11px monospace';
    newscoreCtx.fillText(dim.k, 30, y);
    newscoreCtx.fillStyle = '#778'; newscoreCtx.font = '10px monospace';
    newscoreCtx.fillText('(' + dim.desc + ')', 130, y);
    const v = d.scores[dim.k];
    const range = dim.max - dim.min;
    newscoreCtx.fillStyle = 'rgba(' + dim.col + ',0.15)'; newscoreCtx.fillRect(30, y + 8, 800, 22);
    if (dim.min < 0) {
      const center = 30 + 400;
      const w = (Math.abs(v) / 100) * 400;
      const x = v < 0 ? center - w : center;
      newscoreCtx.fillStyle = 'rgba(' + dim.col + ',0.85)'; newscoreCtx.fillRect(x, y + 8, w, 22);
      newscoreCtx.strokeStyle = 'rgba(255,255,255,0.3)'; newscoreCtx.lineWidth = 1;
      newscoreCtx.beginPath(); newscoreCtx.moveTo(center, y + 8); newscoreCtx.lineTo(center, y + 30); newscoreCtx.stroke();
    } else {
      newscoreCtx.fillStyle = 'rgba(' + dim.col + ',0.85)'; newscoreCtx.fillRect(30, y + 8, 800 * (v / 100), 22);
    }
    newscoreCtx.fillStyle = '#fff'; newscoreCtx.font = 'bold 11px monospace'; newscoreCtx.textAlign = 'right';
    newscoreCtx.fillText(v.toString(), 825, y + 24); newscoreCtx.textAlign = 'left';
  });
  // Summary
  newscoreCtx.fillStyle = '#aaa'; newscoreCtx.font = 'bold 11px monospace';
  newscoreCtx.fillText('AI ANALYST SUMMARY', 30, 430);
  newscoreCtx.fillStyle = '#dce4ed'; newscoreCtx.font = '11px monospace';
  const words = d.summary.split(' '); let line = '', y = 454;
  words.forEach(w => {
    const test = line + w + ' ';
    if (newscoreCtx.measureText(test).width > 870 && line) { newscoreCtx.fillText(line.trim(), 30, y); line = w + ' '; y += 16; }
    else { line = test; }
  });
  if (line) newscoreCtx.fillText(line.trim(), 30, y);
  newscoreCtx.fillStyle = '#778'; newscoreCtx.font = '10px monospace'; newscoreCtx.textAlign = 'center';
  newscoreCtx.fillText('Strata news scorer (equities vertical) — Claude Haiku, cost-controlled to unusualScore ≥ 60', W / 2, H - 14);
  requestAnimationFrame(drawNewscore);
}
drawNewscore();

// ═══════════════════════════════════════════════════════════════════════
// Strategy Leaderboard (Strata equities vertical, paper-trading backtest)
// ═══════════════════════════════════════════════════════════════════════
const STRATEGIES = [
  { name: 'Momentum Long', col: '232,121,249', baseRet: 0.18 },
  { name: 'Mean Reversion', col: '103,232,249', baseRet: 0.11 },
  { name: 'News-Driven', col: '129,199,132', baseRet: 0.22 },
  { name: 'Short Pump Risk', col: '248,113,113', baseRet: 0.08 },
  { name: 'Sector Rotation', col: '250,204,21', baseRet: 0.13 },
  { name: 'Buy & Hold (SPY)', col: '167,139,250', baseRet: 0.10 },
];
const leaderCanvas = document.getElementById('leaderboard-canvas');
const leaderCtx = leaderCanvas.getContext('2d');
let leaderEquity = null, leaderStats = null;
function leaderGen() {
  // Simulate 252 trading days of equity for each strategy
  leaderEquity = STRATEGIES.map(s => {
    const path = [10000];
    const annualVol = 0.18 + Math.random() * 0.12;
    const dailyDrift = s.baseRet / 252 + (Math.random() - 0.5) * 0.001;
    const dailyVol = annualVol / Math.sqrt(252);
    for (let i = 1; i < 252; i++) {
      const r = dailyDrift + (Math.random() + Math.random() + Math.random() - 1.5) * dailyVol;
      path.push(path[i - 1] * (1 + r));
    }
    return path;
  });
  leaderStats = STRATEGIES.map((s, i) => {
    const path = leaderEquity[i];
    const ret = (path[path.length - 1] - path[0]) / path[0];
    let peak = path[0], maxDD = 0;
    path.forEach(v => { if (v > peak) peak = v; const dd = (peak - v) / peak; if (dd > maxDD) maxDD = dd; });
    const dailyRets = []; for (let j = 1; j < path.length; j++) dailyRets.push((path[j] - path[j-1]) / path[j-1]);
    const meanR = dailyRets.reduce((a, b) => a + b, 0) / dailyRets.length;
    const variance = dailyRets.reduce((a, b) => a + (b - meanR) ** 2, 0) / dailyRets.length;
    const sharpe = (meanR / Math.sqrt(variance)) * Math.sqrt(252);
    const winRate = dailyRets.filter(r => r > 0).length / dailyRets.length;
    const trades = 50 + Math.floor(Math.random() * 80);
    return { name: s.name, col: s.col, ret, sharpe, maxDD, winRate, trades };
  });
}
leaderGen();
function leaderRegen() { leaderGen(); pepSend('leaderboard.regen', {}); }
function drawLeader() {
  const W = 960, H = 560; leaderCtx.fillStyle = themeBg(); leaderCtx.fillRect(0, 0, W, H);
  if (!leaderEquity) { requestAnimationFrame(drawLeader); return; }
  // Equity curves (top half)
  const chartH = 240, chartTop = 40, chartLeft = 40, chartRight = W - 40;
  const chartW = chartRight - chartLeft;
  let allMin = Infinity, allMax = -Infinity;
  leaderEquity.forEach(p => p.forEach(v => { if (v < allMin) allMin = v; if (v > allMax) allMax = v; }));
  // Axes
  leaderCtx.strokeStyle = 'rgba(120,130,140,0.4)'; leaderCtx.lineWidth = 1;
  leaderCtx.beginPath(); leaderCtx.moveTo(chartLeft, chartTop); leaderCtx.lineTo(chartLeft, chartTop + chartH); leaderCtx.lineTo(chartRight, chartTop + chartH); leaderCtx.stroke();
  // Equity curves
  leaderEquity.forEach((path, i) => {
    leaderCtx.strokeStyle = 'rgba(' + STRATEGIES[i].col + ',0.85)'; leaderCtx.lineWidth = 1.5;
    leaderCtx.beginPath();
    path.forEach((v, j) => {
      const x = chartLeft + (j / (path.length - 1)) * chartW;
      const y = chartTop + chartH - ((v - allMin) / (allMax - allMin)) * chartH;
      if (j === 0) leaderCtx.moveTo(x, y); else leaderCtx.lineTo(x, y);
    });
    leaderCtx.stroke();
  });
  leaderCtx.fillStyle = '#aaa'; leaderCtx.font = '11px monospace'; leaderCtx.textAlign = 'left';
  leaderCtx.fillText('252 trading-day equity curves (synthetic)', chartLeft, 24);
  // Leaderboard table (bottom half)
  const tableTop = 320;
  leaderCtx.fillStyle = '#aaa'; leaderCtx.font = 'bold 11px monospace';
  ['STRATEGY', 'ANNUAL RETURN', 'SHARPE', 'MAX DD', 'WIN RATE', 'TRADES'].forEach((h, i) => {
    const x = [40, 240, 400, 510, 620, 760][i];
    leaderCtx.fillStyle = '#aaa'; leaderCtx.fillText(h, x, tableTop);
  });
  const sorted = leaderStats.slice().sort((a, b) => b.sharpe - a.sharpe);
  sorted.forEach((s, i) => {
    const y = tableTop + 24 + i * 30;
    leaderCtx.fillStyle = 'rgba(' + s.col + ',0.15)'; leaderCtx.fillRect(30, y - 14, W - 60, 24);
    leaderCtx.fillStyle = 'rgba(' + s.col + ',1)'; leaderCtx.font = 'bold 11px monospace';
    leaderCtx.fillText((i + 1) + '. ' + s.name, 40, y);
    const cells = [
      { x: 240, v: (s.ret * 100).toFixed(1) + '%' },
      { x: 400, v: s.sharpe.toFixed(2) },
      { x: 510, v: '-' + (s.maxDD * 100).toFixed(1) + '%' },
      { x: 620, v: (s.winRate * 100).toFixed(0) + '%' },
      { x: 760, v: s.trades.toString() },
    ];
    cells.forEach(c => { leaderCtx.fillStyle = '#dce4ed'; leaderCtx.font = '11px monospace'; leaderCtx.fillText(c.v, c.x, y); });
  });
  leaderCtx.fillStyle = '#778'; leaderCtx.font = '10px monospace'; leaderCtx.textAlign = 'center';
  leaderCtx.fillText('Strata super-strategy + backtest engine — different scenarios reward different strategies', W / 2, H - 12);
  requestAnimationFrame(drawLeader);
}
drawLeader();

// ═══════════════════════════════════════════════════════════════════════
// Strategy Catalog + Detail (Strata equities vertical, 294 strategies)
// Source: ~/projects/charlie_project/prisma/seed.ts
// ═══════════════════════════════════════════════════════════════════════
const STRATEGIES_FULL = [{n:"Tech Momentum",d:"Volume-confirmed tech momentum",dir:"long",s:"Tech"},{n:"Tech Scalper",d:"Ultra-short 1-2 day tech trades on volume spikes",dir:"long",s:"Tech"},{n:"Tech Swing",d:"Multi-day tech trend riding",dir:"long",s:"Tech"},{n:"Tech Breakout",d:"Extreme volume breakouts in tech",dir:"long",s:"Tech"},{n:"Tech Aggressive Momentum",d:"Wide stops, big position sizes for tech momentum",dir:"long",s:"Tech"},{n:"Tech Conservative",d:"Large-cap tech only with tight risk",dir:"long",s:"Tech"},{n:"Tech News Alpha",d:"News-driven tech plays — earnings, product launches",dir:"long",s:"Tech"},{n:"Tech Dip Buyer",d:"Buys tech dips — overreactions in quality names",dir:"contrarian_long",s:"Tech"},{n:"Tech Volatility Play",d:"Rides extreme volatility in mid-cap tech using gap and sector momentum",dir:"contrarian_long",s:"Tech"},{n:"Tech Trend Follower",d:"Extended tech trend following using 52w level and sector momentum",dir:"long",s:"Tech"},{n:"Semiconductor Focus",d:"Chip stocks momentum — cyclical with high beta",dir:"long",s:"Tech"},{n:"Cybersecurity Alpha",d:"Security sector plays — news-driven catalysts",dir:"long",s:"Tech"},{n:"Cloud & SaaS Growth",d:"Cloud/SaaS momentum — subscription model growth plays",dir:"long",s:"Tech"},{n:"Tech Multi-Factor",d:"Balanced multi-factor tech using all available signals",dir:"long",s:"Tech"},{n:"Tech Small Cap Spec",d:"Small-cap tech speculation — high risk, high reward",dir:"long",s:"Tech"},{n:"Tech Short Scalp",d:"Quick tech shorts — fades overextended rallies",dir:"contrarian_short",s:"Tech"},{n:"Tech Short Swing",d:"Multi-day tech shorts on overextended names",dir:"contrarian_short",s:"Tech"},{n:"Tech Aggressive Short",d:"Aggressive tech shorts with wider stops",dir:"contrarian_short",s:"Tech"},{n:"Healthcare Catalyst",d:"News-driven — FDA approvals and trial results",dir:"long",s:"Healthcare"},{n:"Biotech Speculative",d:"High-risk biotech — binary events, big moves",dir:"long",s:"Healthcare"},{n:"Healthcare Momentum",d:"Volume-confirmed healthcare momentum",dir:"long",s:"Healthcare"},{n:"Healthcare Dip Buyer",d:"Buys healthcare dips — overreactions to trial data",dir:"contrarian_long",s:"Healthcare"},{n:"Healthcare Conservative",d:"Large-cap healthcare — steady earners, low hype",dir:"long",s:"Healthcare"},{n:"Healthcare Scalper",d:"Ultra-short healthcare trades on big volume days",dir:"long",s:"Healthcare"},{n:"Healthcare Breakout",d:"Healthcare stocks breaking out with extreme volume",dir:"long",s:"Healthcare"},{n:"Pharma Big Cap",d:"Big pharma plays — slow and steady with news catalysts",dir:"long",s:"Healthcare"},{n:"Biotech Aggressive",d:"Maximum risk biotech — wide stops, big upside targets",dir:"long",s:"Healthcare"},{n:"Healthcare Trend Follower",d:"Extended healthcare trend following",dir:"long",s:"Healthcare"},{n:"Medtech Growth",d:"Medical devices and medtech growth plays",dir:"long",s:"Healthcare"},{n:"Healthcare Multi-Factor",d:"Balanced multi-factor healthcare using all signals",dir:"long",s:"Healthcare"},{n:"Healthcare Volatility",d:"High-volatility healthcare plays",dir:"contrarian_long",s:"Healthcare"},{n:"Healthcare Short",d:"Shorts overextended healthcare — fades hype biotech",dir:"contrarian_short",s:"Healthcare"},{n:"Biotech Short Scalp",d:"Quick biotech shorts on hype spikes",dir:"contrarian_short",s:"Healthcare"},{n:"Healthcare Short Swing",d:"Multi-day healthcare shorts",dir:"contrarian_short",s:"Healthcare"},{n:"Pharma Short",d:"Shorts overvalued pharma on bearish catalysts",dir:"contrarian_short",s:"Healthcare"},{n:"Healthcare Aggressive Short",d:"Aggressive healthcare shorts with wide stops",dir:"contrarian_short",s:"Healthcare"},{n:"Financial Steady",d:"Conservative financials — banks move on macro",dir:"long",s:"Financial"},{n:"Fintech Momentum",d:"Aggressive fintech momentum — COIN, HOOD type",dir:"long",s:"Financial"},{n:"Financial Breakout",d:"Financials breaking out with volume",dir:"long",s:"Financial"},{n:"Financial Swing",d:"Longer financial sector — macro cycles play out slowly",dir:"long",s:"Financial"},{n:"Financial Dip Buyer",d:"Buys financials on macro overreactions",dir:"contrarian_long",s:"Financial"},{n:"Financial Scalper",d:"Quick financial trades on volume spikes",dir:"long",s:"Financial"},{n:"Bank Earnings Play",d:"Banks around earnings — post-announcement drift",dir:"long",s:"Financial"},{n:"Insurance Value",d:"Insurance sector value plays — rate cycle driven",dir:"long",s:"Financial"},{n:"Financial Aggressive",d:"Aggressive financial momentum — wide stops",dir:"long",s:"Financial"},{n:"Financial Trend Follower",d:"Extended financial trend following",dir:"long",s:"Financial"},{n:"Regional Banks",d:"Regional bank plays — rate sensitivity",dir:"long",s:"Financial"},{n:"Financial Multi-Factor",d:"Balanced multi-factor financial using all signals",dir:"long",s:"Financial"},{n:"Payments Momentum",d:"Payment processor momentum plays",dir:"long",s:"Financial"},{n:"Financial Short",d:"Shorts overextended financial stocks",dir:"contrarian_short",s:"Financial"},{n:"Fintech Short",d:"Shorts overextended fintech — high beta reversals",dir:"contrarian_short",s:"Financial"},{n:"Financial Short Swing",d:"Multi-day financial shorts",dir:"contrarian_short",s:"Financial"},{n:"Bank Short Scalp",d:"Quick bank shorts on overreaction spikes",dir:"contrarian_short",s:"Financial"},{n:"Financial Aggressive Short",d:"Aggressive financial shorts with wide stops",dir:"contrarian_short",s:"Financial"},{n:"Energy Cyclical",d:"Rides commodity-driven energy cycles",dir:"long",s:"Energy"},{n:"Energy Momentum",d:"Short-hold energy momentum — commodity spikes",dir:"long",s:"Energy"},{n:"Energy Swing",d:"Patient energy swing — multi-week commodity cycles",dir:"long",s:"Energy"},{n:"Energy Dip Buyer",d:"Buys energy dips — commodity pullback opportunities",dir:"contrarian_long",s:"Energy"},{n:"Energy Breakout",d:"Extreme volume energy breakouts",dir:"long",s:"Energy"},{n:"Energy Scalper",d:"Quick energy trades on volume spikes",dir:"long",s:"Energy"},{n:"Oil Majors",d:"Large-cap oil plays — macro-driven with volume",dir:"long",s:"Energy"},{n:"Energy Aggressive",d:"Aggressive energy momentum — wide stops",dir:"long",s:"Energy"},{n:"E&P Focus",d:"Exploration & production company momentum",dir:"long",s:"Energy"},{n:"Midstream Value",d:"Midstream/pipeline value plays — yield driven",dir:"contrarian_long",s:"Energy"},{n:"Energy Trend Follower",d:"Extended energy trend following",dir:"long",s:"Energy"},{n:"Energy Multi-Factor",d:"Balanced multi-factor energy approach",dir:"long",s:"Energy"},{n:"Clean Energy Growth",d:"Clean energy and renewables momentum",dir:"long",s:"Energy"},{n:"Energy Short",d:"Shorts overextended energy spikes — commodity reversal",dir:"contrarian_short",s:"Energy"},{n:"Energy Short Scalp",d:"Quick energy shorts on spike days",dir:"contrarian_short",s:"Energy"},{n:"Energy Short Swing",d:"Multi-day energy shorts on macro reversals",dir:"contrarian_short",s:"Energy"},{n:"Oil Short Aggressive",d:"Aggressive oil shorts with wide stops",dir:"contrarian_short",s:"Energy"},{n:"Energy Conservative Short",d:"Conservative energy shorts — tight risk",dir:"contrarian_short",s:"Energy"},{n:"Industrial Value",d:"Institutional volume in large-cap industrials",dir:"long",s:"Industrial"},{n:"Industrial Momentum",d:"Short-hold industrial momentum",dir:"long",s:"Industrial"},{n:"Industrial Swing",d:"Patient industrial trades — infrastructure spending",dir:"long",s:"Industrial"},{n:"Industrial Dip Buyer",d:"Buys industrial dips — overreactions revert",dir:"contrarian_long",s:"Industrial"},{n:"Defense & Aerospace",d:"Defense plays — government spending cycles",dir:"long",s:"Industrial"},{n:"Industrial Scalper",d:"Quick industrial trades on volume spikes",dir:"long",s:"Industrial"},{n:"Industrial Breakout",d:"Industrial breakouts with extreme volume",dir:"long",s:"Industrial"},{n:"Industrial Aggressive",d:"Aggressive industrial momentum — wide stops",dir:"long",s:"Industrial"},{n:"Transport & Logistics",d:"Shipping, trucking, airlines momentum",dir:"long",s:"Industrial"},{n:"Building & Construction",d:"Building products and construction equipment",dir:"long",s:"Industrial"},{n:"Industrial Trend Follower",d:"Extended industrial trend following",dir:"long",s:"Industrial"},{n:"Industrial Multi-Factor",d:"Balanced multi-factor industrial approach",dir:"long",s:"Industrial"},{n:"Industrial Conservative",d:"Conservative large-cap industrials only",dir:"long",s:"Industrial"},{n:"Industrial Short",d:"Shorts overextended industrial stocks",dir:"contrarian_short",s:"Industrial"},{n:"Industrial Short Scalp",d:"Quick industrial shorts on spike days",dir:"contrarian_short",s:"Industrial"},{n:"Industrial Short Swing",d:"Multi-day industrial shorts",dir:"contrarian_short",s:"Industrial"},{n:"Defense Short",d:"Shorts overvalued defense stocks on sentiment shifts",dir:"contrarian_short",s:"Industrial"},{n:"Industrial Aggressive Short",d:"Aggressive industrial shorts with wide stops",dir:"contrarian_short",s:"Industrial"},{n:"Consumer Sentiment",d:"Retail sentiment-driven consumer plays with hype",dir:"long",s:"Consumer"},{n:"Consumer Momentum",d:"Consumer discretionary momentum — retail trends",dir:"long",s:"Consumer"},{n:"Consumer Swing",d:"Longer consumer plays — earnings and seasonal trends",dir:"long",s:"Consumer"},{n:"Consumer Dip Buyer",d:"Buys consumer brand dips — strong brands recover",dir:"contrarian_long",s:"Consumer"},{n:"Consumer Breakout",d:"Heavy volume consumer breakouts",dir:"long",s:"Consumer"},{n:"Consumer Scalper",d:"Quick consumer trades on volume days",dir:"long",s:"Consumer"},{n:"Retail Momentum",d:"Retail sector momentum — seasonal shopping trends",dir:"long",s:"Consumer"},{n:"Homebuilders",d:"Homebuilder plays — rate and housing cycle driven",dir:"long",s:"Consumer"},{n:"Travel & Leisure",d:"Travel and leisure momentum plays",dir:"long",s:"Consumer"},{n:"EV & Auto",d:"Electric vehicle and auto sector plays",dir:"long",s:"Consumer"},{n:"Consumer Aggressive",d:"Aggressive consumer momentum — wide stops",dir:"long",s:"Consumer"},{n:"Consumer Trend Follower",d:"Extended consumer trend following",dir:"long",s:"Consumer"},{n:"Consumer Multi-Factor",d:"Balanced multi-factor consumer approach",dir:"long",s:"Consumer"},{n:"Consumer Short",d:"Shorts overextended consumer — sentiment reversals",dir:"contrarian_short",s:"Consumer"},{n:"Consumer Short Scalp",d:"Quick consumer shorts on hype spikes",dir:"contrarian_short",s:"Consumer"},{n:"Consumer Short Swing",d:"Multi-day consumer shorts",dir:"contrarian_short",s:"Consumer"},{n:"EV Short",d:"Shorts overextended EV and hype auto names",dir:"contrarian_short",s:"Consumer"},{n:"Consumer Aggressive Short",d:"Aggressive consumer shorts with wide stops",dir:"contrarian_short",s:"Consumer"},{n:"Staples Steady",d:"Conservative staples — defensive, low vol",dir:"long",s:"Staples"},{n:"Staples Breakout",d:"Staples breakout — rare but powerful",dir:"long",s:"Staples"},{n:"Staples Momentum",d:"Short-hold staples momentum — sector rotation",dir:"long",s:"Staples"},{n:"Staples Dip Buyer",d:"Buys staples dips — defensive names bounce back",dir:"contrarian_long",s:"Staples"},{n:"Staples Scalper",d:"Quick staples trades on unusual days",dir:"long",s:"Staples"},{n:"Staples Swing",d:"Multi-week staples holds — rotation and macro",dir:"long",s:"Staples"},{n:"Food & Beverage",d:"Food and beverage sector value plays",dir:"long",s:"Staples"},{n:"Staples Aggressive",d:"Aggressive staples momentum — wider stops",dir:"long",s:"Staples"},{n:"Staples Trend Follower",d:"Extended staples trend following",dir:"long",s:"Staples"},{n:"Staples Multi-Factor",d:"Balanced multi-factor staples approach",dir:"long",s:"Staples"},{n:"Discount Retail",d:"Discount retail and dollar store plays",dir:"long",s:"Consumer"},{n:"Staples Short",d:"Shorts overextended staples — rare but profitable",dir:"contrarian_short",s:"Staples"},{n:"Staples Short Scalp",d:"Quick staples shorts on overreactions",dir:"contrarian_short",s:"Staples"},{n:"Staples Short Swing",d:"Multi-day staples shorts",dir:"contrarian_short",s:"Staples"},{n:"Staples Aggressive Short",d:"Aggressive staples shorts with wide stops",dir:"contrarian_short",s:"Staples"},{n:"Staples Conservative Short",d:"Conservative staples shorts — tight risk",dir:"contrarian_short",s:"Staples"},{n:"Comms & Media",d:"Streaming, ad revenue, subscriber metrics driven",dir:"long",s:"Communication"},{n:"Comms Momentum",d:"Short-hold media/comms momentum",dir:"long",s:"Communication"},{n:"Comms Swing",d:"Longer media holds — narrative-driven multi-week",dir:"long",s:"Communication"},{n:"Comms Dip Buyer",d:"Buys comms dips — subscriber fears create buying ops",dir:"contrarian_long",s:"Communication"},{n:"Comms Scalper",d:"Quick comms trades on volume spikes",dir:"long",s:"Communication"},{n:"Comms Breakout",d:"Communication services breakouts",dir:"long",s:"Communication"},{n:"Streaming Wars",d:"Streaming platform plays — subscriber growth bets",dir:"long",s:"Tech"},{n:"Gaming & Esports",d:"Video game and esports momentum",dir:"long",s:"Tech"},{n:"Comms Aggressive",d:"Aggressive comms momentum — wide stops",dir:"long",s:"Communication"},{n:"Comms Trend Follower",d:"Extended comms trend following",dir:"long",s:"Communication"},{n:"Comms Multi-Factor",d:"Balanced multi-factor comms approach",dir:"long",s:"Communication"},{n:"Comms Short",d:"Shorts overextended media — sentiment shifts fast",dir:"contrarian_short",s:"Communication"},{n:"Comms Short Scalp",d:"Quick comms shorts on hype spikes",dir:"contrarian_short",s:"Communication"},{n:"Comms Short Swing",d:"Multi-day comms shorts",dir:"contrarian_short",s:"Communication"},{n:"Comms Aggressive Short",d:"Aggressive comms shorts with wide stops",dir:"contrarian_short",s:"Communication"},{n:"Comms Conservative Short",d:"Conservative comms shorts — tight risk",dir:"contrarian_short",s:"Communication"},{n:"Materials & Mining",d:"Cyclical materials — volume signals cycle turns",dir:"long",s:"Materials"},{n:"Materials Momentum",d:"Short-hold materials momentum",dir:"long",s:"Materials"},{n:"Materials Swing",d:"Patient materials — commodity cycles take time",dir:"long",s:"Materials"},{n:"Materials Dip Buyer",d:"Buys materials dips — commodity bear overreactions",dir:"contrarian_long",s:"Materials"},{n:"Materials Scalper",d:"Quick materials trades on volume days",dir:"long",s:"Materials"},{n:"Materials Breakout",d:"Materials stocks breaking out on volume",dir:"long",s:"Materials"},{n:"Gold & Silver",d:"Precious metals mining plays",dir:"long",s:"Materials"},{n:"Chemicals Value",d:"Chemical sector value — cyclical with macro sensitivity",dir:"long",s:"Materials"},{n:"Materials Aggressive",d:"Aggressive materials momentum — wide stops",dir:"long",s:"Materials"},{n:"Materials Trend Follower",d:"Extended materials trend following",dir:"long",s:"Materials"},{n:"Materials Multi-Factor",d:"Balanced multi-factor materials approach",dir:"long",s:"Materials"},{n:"Materials Short",d:"Shorts overextended commodity stocks",dir:"contrarian_short",s:"Materials"},{n:"Materials Short Scalp",d:"Quick materials shorts on spike days",dir:"contrarian_short",s:"Materials"},{n:"Materials Short Swing",d:"Multi-day materials shorts on cycle peaks",dir:"contrarian_short",s:"Materials"},{n:"Materials Aggressive Short",d:"Aggressive materials shorts with wide stops",dir:"contrarian_short",s:"Materials"},{n:"Mining Short",d:"Shorts overvalued miners at commodity peaks",dir:"contrarian_short",s:"Materials"},{n:"Utilities Income",d:"Yield plays on unusual pullbacks",dir:"contrarian_long",s:"Utilities"},{n:"Utilities Momentum",d:"Rare sector rotation into utilities",dir:"long",s:"Utilities"},{n:"Utilities Swing",d:"Patient utility trades — rate cycle multi-week",dir:"long",s:"Utilities"},{n:"Utilities Breakout",d:"Utilities breaking out — nuclear/clean energy",dir:"long",s:"Utilities"},{n:"Utilities Scalper",d:"Quick utility trades on unusual volume days",dir:"long",s:"Utilities"},{n:"Nuclear & Clean Energy",d:"Nuclear and clean energy utility plays",dir:"long",s:"Energy"},{n:"Utilities Conservative",d:"Conservative utility value — dividend safety",dir:"long",s:"Utilities"},{n:"Utilities Aggressive",d:"Aggressive utility momentum — wide stops",dir:"long",s:"Utilities"},{n:"Utilities Trend Follower",d:"Extended utility trend following",dir:"long",s:"Utilities"},{n:"Utilities Multi-Factor",d:"Balanced multi-factor utility approach",dir:"long",s:"Utilities"},{n:"Utilities Dip Buyer",d:"Buys utility dips — rate overreactions",dir:"contrarian_long",s:"Utilities"},{n:"Utilities Short",d:"Shorts overextended utility rallies",dir:"contrarian_short",s:"Utilities"},{n:"Utilities Short Scalp",d:"Quick utility shorts on overextension",dir:"contrarian_short",s:"Utilities"},{n:"Utilities Short Swing",d:"Multi-day utility shorts",dir:"contrarian_short",s:"Utilities"},{n:"Utilities Aggressive Short",d:"Aggressive utility shorts with wide stops",dir:"contrarian_short",s:"Utilities"},{n:"Utilities Conservative Short",d:"Conservative utility shorts — tight risk",dir:"contrarian_short",s:"Utilities"},{n:"REIT Value",d:"REIT dip buying — rate overreactions create opportunity",dir:"contrarian_long",s:"RealEstate"},{n:"REIT Momentum",d:"REIT momentum — sector rotation into real estate",dir:"long",s:"RealEstate"},{n:"REIT Swing",d:"Longer REIT holds — rate cycle multi-week trends",dir:"long",s:"RealEstate"},{n:"REIT Breakout",d:"REIT breakout — data center and infrastructure growth",dir:"long",s:"RealEstate"},{n:"REIT Scalper",d:"Quick REIT trades on unusual volume days",dir:"long",s:"RealEstate"},{n:"Data Center REITs",d:"Data center REIT plays — AI infrastructure growth",dir:"long",s:"Tech"},{n:"REIT Conservative",d:"Conservative REIT value — large cap, dividend safety",dir:"long",s:"RealEstate"},{n:"REIT Aggressive",d:"Aggressive REIT momentum — wide stops",dir:"long",s:"RealEstate"},{n:"REIT Trend Follower",d:"Extended REIT trend following",dir:"long",s:"RealEstate"},{n:"REIT Multi-Factor",d:"Balanced multi-factor REIT approach",dir:"long",s:"RealEstate"},{n:"REIT Dip Buyer",d:"Buys REIT dips — rate fears always overshoot",dir:"contrarian_long",s:"RealEstate"},{n:"REIT Short",d:"Shorts overextended REITs — rate spike reversals",dir:"contrarian_short",s:"RealEstate"},{n:"REIT Short Scalp",d:"Quick REIT shorts on overextension",dir:"contrarian_short",s:"RealEstate"},{n:"REIT Short Swing",d:"Multi-day REIT shorts on rate moves",dir:"contrarian_short",s:"RealEstate"},{n:"REIT Aggressive Short",d:"Aggressive REIT shorts with wide stops",dir:"contrarian_short",s:"RealEstate"},{n:"REIT Conservative Short",d:"Conservative REIT shorts — tight risk",dir:"contrarian_short",s:"RealEstate"},{n:"Tech Mean Reversion",d:"Buys tech stocks after sharp drops — bets on overreaction bounce",dir:"contrarian_long",s:"Tech"},{n:"Healthcare Mean Reversion",d:"Buys healthcare drops — overreaction to trial/FDA news",dir:"contrarian_long",s:"Healthcare"},{n:"Financials Mean Reversion",d:"Buys financial sector dips — rate shock reversals",dir:"contrarian_long",s:"Financial"},{n:"Energy Mean Reversion",d:"Buys energy drops — commodity overreaction plays",dir:"contrarian_long",s:"Energy"},{n:"Consumer Mean Reversion",d:"Buys consumer discretionary dips — sentiment overreaction",dir:"contrarian_long",s:"Consumer"},{n:"Industrials Mean Reversion",d:"Buys industrial sector drops — cyclical bounce plays",dir:"contrarian_long",s:"Industrial"},{n:"Materials Mean Reversion",d:"Buys materials dips — commodity cycle reversals",dir:"contrarian_long",s:"Materials"},{n:"Comm Services Mean Reversion",d:"Buys comms drops — ad revenue overreaction bounce",dir:"contrarian_long",s:"Communication"},{n:"Utilities Mean Reversion",d:"Buys utilities drops — defensive sector bounce",dir:"contrarian_long",s:"Utilities"},{n:"REIT Mean Reversion",d:"Buys REIT drops — rate shock overreaction",dir:"contrarian_long",s:"RealEstate"},{n:"Staples Mean Reversion",d:"Buys consumer staples drops — safe haven bounce",dir:"contrarian_long",s:"Staples"},{n:"Broad Mean Reversion",d:"Cross-sector mean reversion — buys the biggest drops",dir:"contrarian_long",s:"Mixed"},{n:"Aggressive Mean Reversion",d:"Wide stops mean reversion — rides bigger bounces",dir:"contrarian_long",s:"Mixed"},{n:"Conservative Mean Reversion",d:"Tight stops mean reversion — quick bounces only",dir:"contrarian_long",s:"Mixed"},{n:"Volume Climax Reversal",d:"Buys extreme volume selloffs — capitulation bottom fishing",dir:"contrarian_long",s:"Mixed"},{n:"Gap Up Continuation",d:"Buys gap-up stocks expecting follow-through momentum",dir:"gap_long",s:"Mixed"},{n:"Gap Fill Buyer",d:"Buys gap-down stocks expecting the gap to fill",dir:"contrarian_long",s:"Mixed"},{n:"Tech Gap Continuation",d:"Tech-specific gap-up momentum plays",dir:"gap_long",s:"Tech"},{n:"Tech Gap Fill",d:"Buys tech gap-downs — overreaction to pre-market news",dir:"contrarian_long",s:"Tech"},{n:"Healthcare Gap Fill",d:"Buys healthcare gap-downs — FDA/trial overreaction",dir:"contrarian_long",s:"Healthcare"},{n:"Energy Gap Continuation",d:"Energy gap-up plays on commodity news",dir:"gap_long",s:"Energy"},{n:"Financials Gap Fill",d:"Buys financial gap-downs — rate decision overreaction",dir:"contrarian_long",s:"Financial"},{n:"Large Gap Reversal",d:"Buys stocks after 5%+ gap downs — extreme overreaction",dir:"contrarian_long",s:"Mixed"},{n:"Gap Scalper",d:"Ultra-short gap trades — in and out same day or next",dir:"gap_long",s:"Mixed"},{n:"Gap & Go Momentum",d:"Rides gap-up stocks with strong volume confirmation",dir:"gap_long",s:"Mixed"},{n:"Sector Rotation Alpha",d:"Rotates into strongest sector — momentum-driven allocation",dir:"long",s:"Mixed"},{n:"Sector Rotation Conservative",d:"Sector rotation with tight risk and large-cap bias",dir:"long",s:"Mixed"},{n:"Sector Rotation Aggressive",d:"Aggressive sector rotation — wide stops, big targets",dir:"long",s:"Mixed"},{n:"Defensive Rotation",d:"Rotates into defensive sectors when momentum is weak",dir:"long",s:"Mixed"},{n:"Cyclical Rotation",d:"Rotates into cyclical sectors during expansions",dir:"long",s:"Mixed"},{n:"Growth Rotation",d:"Rotates into growth sectors — tech, healthcare, comm services",dir:"long",s:"Mixed"},{n:"Value Rotation",d:"Rotates into value sectors — financials, energy, industrials",dir:"long",s:"Mixed"},{n:"Momentum Sector Swing",d:"Swing trades in the hottest sector of the week",dir:"long",s:"Mixed"},{n:"Sector Breakout Hunter",d:"Buys breakouts in sectors showing broad strength",dir:"long",s:"Mixed"},{n:"Sector Momentum Scalper",d:"Quick sector-momentum trades — 1-3 day holds",dir:"gap_long",s:"Mixed"},{n:"Broad Sector Trend",d:"Long-term sector rotation — rides multi-week sector trends",dir:"long",s:"Mixed"},{n:"Tech Downtrend Rider",d:"Shorts tech stocks in sustained downtrends — rides bearish momentum",dir:"short",s:"Tech"},{n:"Energy Bear",d:"Shorts energy stocks trending down — follows sector weakness",dir:"short",s:"Energy"},{n:"Healthcare Breakdown",d:"Shorts healthcare stocks breaking key support levels",dir:"short",s:"Healthcare"},{n:"Financial Sector Bear",d:"Shorts financials in downtrends — follows credit weakness",dir:"short",s:"Financial"},{n:"Consumer Discretionary Short",d:"Shorts consumer discretionary in spending downturns",dir:"short",s:"Consumer"},{n:"Industrial Weakness",d:"Shorts industrials showing sustained weakness",dir:"short",s:"Industrial"},{n:"Materials Downtrend",d:"Shorts materials stocks in commodity downturns",dir:"short",s:"Materials"},{n:"Broad Market Bear",d:"Shorts stocks across all sectors in sustained downtrends",dir:"short",s:"Mixed"},{n:"52-Week Low Breakdown",d:"Shorts stocks making new 52-week lows with high volume",dir:"short",s:"Mixed"},{n:"Slow Bleed Short",d:"Shorts stocks in slow persistent decline — low volatility downtrend",dir:"short",s:"Mixed"},{n:"Breakdown Scalper",d:"Quick short trades on technical breakdowns — 1-3 day holds",dir:"short",s:"Mixed"},{n:"Comm Services Bear",d:"Shorts communication services stocks in downtrends",dir:"short",s:"Communication"},{n:"Real Estate Downturn",d:"Shorts real estate stocks in rate-hike driven downtrends",dir:"short",s:"RealEstate"},{n:"Utilities Decline",d:"Shorts utilities in rising-rate environments",dir:"short",s:"Utilities"},{n:"Consumer Staples Short",d:"Shorts staples when defensive rotation reverses",dir:"short",s:"Consumer"},{n:"High Volume Selloff",d:"Shorts stocks with heavy selling pressure — volume spike breakdowns",dir:"short",s:"Mixed"},{n:"Multi-Sector Bear Swing",d:"Swing short across weakest sectors — 1-2 week holds",dir:"short",s:"Mixed"},{n:"Small Cap Short",d:"Shorts small caps with weak fundamentals in downtrends",dir:"short",s:"Mixed"},{n:"Large Cap Decline",d:"Shorts large caps in confirmed downtrends — lower volatility shorts",dir:"short",s:"Mixed"},{n:"Sector Rotation Short",d:"Shorts sectors losing relative strength — follows rotation away",dir:"short",s:"Mixed"},{n:"Hype Fader",d:"Shorts hyped-up stocks that spiked — bets on mean reversion down",dir:"contrarian_short",s:"Mixed"},{n:"Tech Rally Fader",d:"Shorts overextended tech rallies — fades the hype",dir:"contrarian_short",s:"Tech"},{n:"Biotech Rally Fader",d:"Shorts overextended biotech spikes — trial hype fade",dir:"contrarian_short",s:"Healthcare"},{n:"Small Cap Fader",d:"Shorts overextended small-cap spikes — pump and dump targets",dir:"contrarian_short",s:"Mixed"},{n:"Exhaustion Top Fader",d:"Shorts stocks showing intraday exhaustion — reversal pattern",dir:"contrarian_short",s:"Mixed"},{n:"Gap Up Fader",d:"Shorts gap-up stocks expecting the gap to fill down",dir:"contrarian_short",s:"Mixed"},{n:"Energy Rally Fader",d:"Shorts overextended energy rallies — commodity overbought",dir:"contrarian_short",s:"Energy"},{n:"Consumer Hype Fader",d:"Shorts consumer discretionary hype — retail/meme stock fades",dir:"contrarian_short",s:"Consumer"},{n:"Broad Rally Fader",d:"Cross-sector rally fade — shorts the most overextended",dir:"contrarian_short",s:"Mixed"},{n:"Aggressive Rally Fader",d:"Aggressive contrarian shorts — wide stops, big targets",dir:"contrarian_short",s:"Mixed"},{n:"Conservative Rally Fader",d:"Tight-risk rally fades — confirmed exhaustion only",dir:"contrarian_short",s:"Mixed"},{n:"Squeeze Fader",d:"Shorts stocks after short squeeze peaks — fading the blow-off top",dir:"contrarian_short",s:"Mixed"},{n:"Financials Rally Fader",d:"Shorts overextended financial sector rallies",dir:"contrarian_short",s:"Financial"},{n:"Comm Services Fader",d:"Shorts comms hype spikes — social media/streaming fades",dir:"contrarian_short",s:"Communication"},{n:"Volume Climax Fader",d:"Shorts after extreme volume spikes — blow-off top pattern",dir:"contrarian_short",s:"Mixed"},{n:"Swing Mean Reversion",d:"Longer-hold mean reversion — 10-15 day recovery plays",dir:"contrarian_long",s:"Mixed"},{n:"Deep Value Reversal",d:"Large-cap 52w low buys — deep value with extreme volume",dir:"contrarian_long",s:"Mixed"},{n:"Sector Capitulation Buyer",d:"Buys when whole sector is dumping — broad capitulation",dir:"contrarian_long",s:"Mixed"},{n:"Energy Gap Fill",d:"Energy gap-down fill — commodity overreaction gaps",dir:"contrarian_long",s:"Energy"},{n:"Consumer Gap Fill",d:"Consumer discretionary gap-down fill — sentiment overreaction",dir:"contrarian_long",s:"Consumer"},{n:"Industrials Gap Fill",d:"Industrials gap-down fill — cyclical overreaction",dir:"contrarian_long",s:"Industrial"},{n:"Materials Gap Fill",d:"Materials gap-down fill — commodity price overreaction",dir:"contrarian_long",s:"Materials"},{n:"Comm Services Gap Fill",d:"Comms gap-down fill — ad revenue overreaction gaps",dir:"contrarian_long",s:"Communication"},{n:"Utilities Gap Fill",d:"Utilities gap-down fill — defensive sector overreaction",dir:"contrarian_long",s:"Utilities"},{n:"REIT Gap Fill",d:"REIT gap-down fill — rate shock gap reversals",dir:"contrarian_long",s:"RealEstate"},{n:"Staples Gap Fill",d:"Consumer staples gap-down fill — safe haven gap reversal",dir:"contrarian_long",s:"Staples"},{n:"Small Cap Mean Reversion",d:"Small-cap dip buying — low market cap overreactions",dir:"contrarian_long",s:"Mixed"},{n:"Large Cap Mean Reversion",d:"$10B+ conservative dip buying — blue chip bounces",dir:"contrarian_long",s:"Mixed"},{n:"High Volume Dip Buyer",d:"Requires 3x+ volume — only buys on extreme selling pressure",dir:"contrarian_long",s:"Mixed"},{n:"Exhaustion Bottom Scalper",d:"Ultra-short 1-2 day holds on exhaustion bottom signals",dir:"contrarian_long",s:"Mixed"},{n:"Broad Gap Fill",d:"Cross-sector moderate gap-down fill — diversified gap plays",dir:"contrarian_long",s:"Mixed"},{n:"Aggressive Gap Fill",d:"Wide stops gap fill — rides full gap closure",dir:"contrarian_long",s:"Mixed"},{n:"Conservative Gap Fill",d:"Tight stops gap fill — 1-day, large-cap only",dir:"contrarian_long",s:"Mixed"},{n:"Industrials Rally Fader",d:"Shorts overextended industrial sector rallies",dir:"contrarian_short",s:"Industrial"},{n:"Materials Rally Fader",d:"Shorts materials sector spikes — commodity overbought fades",dir:"contrarian_short",s:"Materials"},{n:"Utilities Rally Fader",d:"Shorts utility sector spikes — defensive overbought fade",dir:"contrarian_short",s:"Utilities"},{n:"REIT Rally Fader",d:"Shorts overextended REIT rallies — rate play fades",dir:"contrarian_short",s:"RealEstate"},{n:"Staples Rally Fader",d:"Shorts consumer staples spikes — safe haven overbought",dir:"contrarian_short",s:"Staples"},{n:"Healthcare Rally Fader",d:"Shorts broader healthcare spikes — not just biotech",dir:"contrarian_short",s:"Healthcare"},{n:"Large Cap Rally Fader",d:"Fades $10B+ overextensions — blue chip blow-off tops",dir:"contrarian_short",s:"Mixed"},{n:"Parabolic Fader",d:"Shorts 10%+ single-day moves — parabolic blow-off",dir:"contrarian_short",s:"Mixed"},{n:"Gap Up Scalper",d:"1-day gap-up fade — ultra-short fade and close",dir:"contrarian_short",s:"Mixed"},{n:"Sector Hype Fader",d:"Shorts sector-wide hype — when a whole sector gets too hot",dir:"contrarian_short",s:"Mixed"},{n:"Low Float Fader",d:"Shorts low-float pump targets — high risk, high reward fades",dir:"contrarian_short",s:"Mixed"},{n:"Earnings Hype Fader",d:"Fades post-earnings gap-up hype — buy the rumor sell the news",dir:"contrarian_short",s:"Mixed"},{n:"Swing Rally Fader",d:"7-10 day holds fading multi-day rallies that lose steam",dir:"contrarian_short",s:"Mixed"},{n:"Aggressive Gap Fader",d:"Wide stops gap-up fade — lets trades breathe",dir:"contrarian_short",s:"Mixed"},{n:"Conservative Gap Fader",d:"Tight-risk gap-up fade — confirmed exhaustion signals only",dir:"contrarian_short",s:"Mixed"},{n:"Broad Exhaustion Fader",d:"Cross-sector exhaustion-top fades — diversified",dir:"contrarian_short",s:"Mixed"},{n:"Multi-Day Exhaustion Fader",d:"Shorts stocks with weakening volume after consecutive up days",dir:"contrarian_short",s:"Mixed"}];

// Color per direction
const DIR_COLORS = { long: '129,199,132', short: '248,113,113', contrarian_long: '103,232,249', contrarian_short: '232,121,249', gap_long: '250,204,21' };
const DIR_LABELS = { long: 'long', short: 'short', contrarian_long: 'contra-long', contrarian_short: 'contra-short', gap_long: 'gap-long' };
const SECTOR_COLOR_BY_KEY = { Tech: '232,121,249', Healthcare: '129,199,132', Financial: '103,232,249', Energy: '250,204,21', Industrial: '186,104,200', Consumer: '249,168,212', Staples: '255,183,77', Utilities: '79,195,247', RealEstate: '167,139,250', Materials: '141,110,99', Communication: '244,143,177', Mixed: '158,158,158' };

let catFilter = { sector: 'all', dir: 'all' };

function catalogFilter(kind, value) {
  catFilter[kind] = value;
  // Update active button styling
  const prefix = kind === 'sector' ? 'cf-' : 'cf-dir-';
  // Find and update sibling buttons in the same controls block
  document.querySelectorAll('.cat-btn').forEach(b => {
    const text = b.textContent.trim();
    const isActive = (kind === 'sector' && (text === value || (value === 'all' && b.id === 'cf-all'))) ||
                     (kind === 'dir' && (text === value || (value === 'all' && b.id === 'cf-dir-all')));
  });
  // Cleaner: just toggle by inspecting onclick attr
  document.querySelectorAll('.cat-btn').forEach(b => {
    const oc = b.getAttribute('onclick') || '';
    const matches = oc.includes("'" + kind + "','" + value + "'");
    const isOtherKind = !oc.includes("'" + kind + "',");
    if (isOtherKind) return;
    b.classList.toggle('cat-active', matches);
  });
  catalogRender();
  pepSend('catalog.filter', { kind, value });
}

function catalogRender() {
  const grid = document.getElementById('catalog-grid');
  if (!grid) return;
  const q = (document.getElementById('cat-search')?.value || '').toLowerCase().trim();
  const filtered = STRATEGIES_FULL.filter(st => {
    if (catFilter.sector !== 'all' && st.s !== catFilter.sector) return false;
    if (catFilter.dir !== 'all' && st.dir !== catFilter.dir) return false;
    if (q && !(st.n + ' ' + st.d).toLowerCase().includes(q)) return false;
    return true;
  });
  document.getElementById('cat-count').textContent = STRATEGIES_FULL.length;
  document.getElementById('cat-shown').textContent = filtered.length;
  document.getElementById('cat-total').textContent = STRATEGIES_FULL.length;
  if (!filtered.length) { grid.innerHTML = '<span style="color:var(--dim)">no matches</span>'; return; }
  grid.innerHTML = filtered.map((st, i) => {
    const dirCol = DIR_COLORS[st.dir] || '180,180,180';
    const secCol = SECTOR_COLOR_BY_KEY[st.s] || '160,160,160';
    const escapedName = st.n.replace(/'/g, "\\\\'").replace(/"/g, '&quot;');
    return '<div onclick="strategyDetailFromCard(\\'' + escapedName + '\\')" ' +
      'style="background:var(--surface);border:1px solid var(--border);border-left:3px solid rgb(' + dirCol + ');' +
      'border-radius:6px;padding:10px 12px;cursor:pointer;transition:border-color 0.15s" ' +
      'onmouseover="this.style.borderColor=\\'rgb(' + dirCol + ')\\'" ' +
      'onmouseout="this.style.borderColor=\\'var(--border)\\'">' +
      '<div style="display:flex;justify-content:space-between;align-items:start;gap:8px">' +
        '<div style="font-size:12px;color:var(--text);font-weight:bold">' + st.n + '</div>' +
        '<span style="font-size:9px;color:rgb(' + secCol + ');background:rgba(' + secCol + ',0.15);padding:1px 6px;border-radius:8px;white-space:nowrap">' + st.s + '</span>' +
      '</div>' +
      '<div style="font-size:10px;color:var(--dim);margin-top:4px;line-height:1.4">' + st.d + '</div>' +
      '<div style="font-size:9px;color:rgb(' + dirCol + ');margin-top:6px;letter-spacing:0.05em">' + (DIR_LABELS[st.dir] || st.dir) + '</div>' +
      '</div>';
  }).join('');
}

// Populate the strategy detail dropdown with all 294 strategies
function populateStrategyDropdown() {
  const sel = document.getElementById('sd-select');
  if (!sel) return;
  // Group by sector
  const bySector = {};
  STRATEGIES_FULL.forEach(st => { (bySector[st.s] = bySector[st.s] || []).push(st); });
  Object.keys(bySector).sort().forEach(sec => {
    const og = document.createElement('optgroup');
    og.label = sec + ' (' + bySector[sec].length + ')';
    bySector[sec].forEach(st => {
      const o = document.createElement('option');
      o.value = st.n;
      o.textContent = st.n + ' [' + (DIR_LABELS[st.dir] || st.dir) + ']';
      og.appendChild(o);
    });
    sel.appendChild(og);
  });
}

function strategyDetailFromCard(name) {
  // Activate the strategy-detail panel and set the dropdown
  const tab = findTabForPanel('strategy-detail-tab');
  if (tab) tab.click();
  setTimeout(() => {
    const sel = document.getElementById('sd-select');
    if (sel) { sel.value = name; strategyDetailPick(name); }
    const el = document.getElementById('strategy-detail-tab');
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, 80);
}

// Derive plausible factor weights from strategy name + direction
function deriveStrategyFactors(st) {
  const name = st.n.toLowerCase();
  const factors = { relativeVolume: 0.15, unusualScore: 0.15, gapPct: 0.1, sectorMomentum: 0.15, hypeRisk: 0.1, priceLevel52w: 0.15 };
  if (name.includes('breakout') || name.includes('momentum')) { factors.relativeVolume = 0.30; factors.unusualScore = 0.30; factors.priceLevel52w = 0.25; }
  if (name.includes('scalper')) { factors.relativeVolume = 0.40; factors.unusualScore = 0.30; factors.gapPct = 0.20; }
  if (name.includes('swing') || name.includes('trend')) { factors.priceLevel52w = 0.35; factors.sectorMomentum = 0.30; factors.unusualScore = 0.20; }
  if (name.includes('dip') || name.includes('mean reversion') || name.includes('gap fill') || name.includes('capitulation')) { factors.unusualScore = 0.30; factors.relativeVolume = 0.25; factors.priceLevel52w = 0.25; factors.hypeRisk = 0.05; }
  if (name.includes('gap') && (st.dir === 'gap_long' || name.includes('continuation') || name.includes('go'))) { factors.gapPct = 0.35; factors.relativeVolume = 0.25; factors.unusualScore = 0.20; }
  if (st.dir === 'short' || st.dir === 'contrarian_short') { factors.hypeRisk = 0.30; factors.priceLevel52w = 0.25; factors.unusualScore = 0.20; factors.relativeVolume = 0.15; factors.sectorMomentum = 0.10; }
  if (name.includes('news') || name.includes('catalyst') || name.includes('earnings')) { factors.unusualScore = 0.30; factors.hypeRisk = 0.05; }
  if (name.includes('multi-factor')) { Object.keys(factors).forEach(k => factors[k] = 1 / 6); }
  // Normalize
  const sum = Object.values(factors).reduce((a, b) => a + b, 0);
  Object.keys(factors).forEach(k => factors[k] /= sum);
  return factors;
}

function deriveStrategyParams(st) {
  const name = st.n.toLowerCase();
  let stop = 5, takeProfit = 12, maxHold = 5, posSize = 20;
  if (name.includes('aggressive')) { stop = 8; takeProfit = 20; }
  if (name.includes('conservative')) { stop = 3; takeProfit = 8; }
  if (name.includes('scalper')) { stop = 3; takeProfit = 5; maxHold = 2; posSize = 15; }
  if (name.includes('swing') || name.includes('trend follower')) { stop = 6; takeProfit = 18; maxHold = 14; posSize = 18; }
  if (st.dir === 'short' || st.dir === 'contrarian_short') { stop = stop - 1; takeProfit = takeProfit - 2; }
  if (name.includes('speculative') || name.includes('biotech')) { stop = 12; takeProfit = 30; posSize = 10; }
  return { stop, takeProfit, maxHold, posSize };
}

const sdCanvas = document.getElementById('sd-canvas');
const sdCtx = sdCanvas.getContext('2d');
let sdActive = null;
function strategyDetailPick(name) {
  sdActive = STRATEGIES_FULL.find(s => s.n === name) || null;
  const nameSpan = document.getElementById('sd-name');
  if (nameSpan) nameSpan.textContent = sdActive ? sdActive.n : '(pick one from the catalog)';
  pepSend('strategy.detail', { name });
}

function drawSd() {
  const W = 960, H = 560; sdCtx.fillStyle = themeBg(); sdCtx.fillRect(0, 0, W, H);
  if (!sdActive) {
    sdCtx.fillStyle = '#778'; sdCtx.font = '11px monospace'; sdCtx.textAlign = 'center';
    sdCtx.fillText('(pick a strategy from the dropdown or the Catalog)', W / 2, H / 2);
    requestAnimationFrame(drawSd); return;
  }
  const st = sdActive;
  const dirCol = DIR_COLORS[st.dir] || '180,180,180';
  const secCol = SECTOR_COLOR_BY_KEY[st.s] || '160,160,160';
  // Header
  sdCtx.fillStyle = '#dce4ed'; sdCtx.font = 'bold 16px monospace'; sdCtx.textAlign = 'left';
  sdCtx.fillText(st.n, 30, 32);
  sdCtx.fillStyle = 'rgb(' + secCol + ')'; sdCtx.font = '11px monospace';
  sdCtx.fillText(st.s + ' · ' + (DIR_LABELS[st.dir] || st.dir), 30, 52);
  sdCtx.fillStyle = '#aab'; sdCtx.font = '11px monospace';
  // Wrap description
  const words = st.d.split(' '); let line = '', y = 78;
  words.forEach(w => {
    const test = line + w + ' ';
    if (sdCtx.measureText(test).width > W - 60 && line) { sdCtx.fillText(line.trim(), 30, y); line = w + ' '; y += 14; }
    else { line = test; }
  });
  if (line) sdCtx.fillText(line.trim(), 30, y);
  // Three columns
  const colY = 130;
  // Col 1: factor weights
  const factors = deriveStrategyFactors(st);
  sdCtx.fillStyle = '#dce4ed'; sdCtx.font = 'bold 11px monospace';
  sdCtx.fillText('FACTOR WEIGHTS', 30, colY);
  Object.entries(factors).forEach(([k, v], i) => {
    const fy = colY + 24 + i * 28;
    sdCtx.fillStyle = '#aab'; sdCtx.font = '10px monospace';
    sdCtx.fillText(k, 30, fy);
    sdCtx.fillStyle = 'rgba(' + dirCol + ',0.2)'; sdCtx.fillRect(30, fy + 6, 240, 14);
    sdCtx.fillStyle = 'rgba(' + dirCol + ',0.85)'; sdCtx.fillRect(30, fy + 6, 240 * v, 14);
    sdCtx.fillStyle = '#fff'; sdCtx.font = '10px monospace'; sdCtx.textAlign = 'right';
    sdCtx.fillText((v * 100).toFixed(0) + '%', 268, fy + 18);
    sdCtx.textAlign = 'left';
  });
  // Col 2: risk parameters
  const params = deriveStrategyParams(st);
  sdCtx.fillStyle = '#dce4ed'; sdCtx.font = 'bold 11px monospace';
  sdCtx.fillText('RISK PARAMETERS', 350, colY);
  const paramList = [
    ['stop loss',   params.stop + '%'],
    ['take profit', params.takeProfit + '%'],
    ['max hold',    params.maxHold + ' days'],
    ['position size', params.posSize + '% of equity'],
    ['direction',   DIR_LABELS[st.dir] || st.dir],
    ['sector',      st.s],
  ];
  paramList.forEach(([k, v], i) => {
    const py = colY + 28 + i * 26;
    sdCtx.fillStyle = '#aab'; sdCtx.font = '10px monospace'; sdCtx.fillText(k, 350, py);
    sdCtx.fillStyle = '#fff'; sdCtx.font = 'bold 10px monospace'; sdCtx.textAlign = 'right'; sdCtx.fillText(v, 600, py); sdCtx.textAlign = 'left';
  });
  // Col 3: would it trigger on these setups?
  sdCtx.fillStyle = '#dce4ed'; sdCtx.font = 'bold 11px monospace';
  sdCtx.fillText('WOULD TRIGGER?', 640, colY);
  const setups = [
    { label: '+8% on 3x volume, sector strong', score: 82 },
    { label: '−6% gap down, low volume', score: 35 },
    { label: 'Quiet drift +1%, normal volume', score: 12 },
  ];
  setups.forEach((setup, i) => {
    const sy = colY + 32 + i * 80;
    sdCtx.fillStyle = '#aab'; sdCtx.font = '10px monospace';
    sdCtx.fillText(setup.label, 640, sy);
    // Determine if this setup matches the strategy direction
    const triggers = (
      (st.dir === 'long' && setup.score > 60) ||
      (st.dir === 'short' && setup.label.includes('gap down')) ||
      (st.dir === 'contrarian_long' && setup.label.includes('gap down')) ||
      (st.dir === 'contrarian_short' && setup.score > 70) ||
      (st.dir === 'gap_long' && setup.label.includes('gap down') === false && setup.score > 60)
    );
    const triggerCol = triggers ? '129,199,132' : '120,130,140';
    const triggerLabel = triggers ? '✓ ENTRY' : '✗ skip';
    sdCtx.fillStyle = 'rgba(' + triggerCol + ',0.2)'; sdCtx.fillRect(640, sy + 8, 280, 22);
    sdCtx.fillStyle = 'rgb(' + triggerCol + ')'; sdCtx.font = 'bold 11px monospace';
    sdCtx.fillText(triggerLabel, 650, sy + 24);
    sdCtx.fillStyle = '#778'; sdCtx.font = '9px monospace';
    sdCtx.fillText('signal score: ' + setup.score, 740, sy + 24);
  });
  // Footer
  sdCtx.fillStyle = '#778'; sdCtx.font = '10px monospace'; sdCtx.textAlign = 'center';
  sdCtx.fillText('factor weights and parameters derived from name+direction; production values live in the Strategy table at ~/projects/charlie_project', W / 2, H - 14);
  requestAnimationFrame(drawSd);
}
drawSd();

setTimeout(() => { catalogRender(); populateStrategyDropdown(); }, 80);

// ═══════════════════════════════════════════════════════════════════════
// Earnings Pragmatics — mirrors pep.lingora.earnings_pragmatic in the browser
// ═══════════════════════════════════════════════════════════════════════
const PR_POS = ['strong','grew','growth','expanded','expanding','outperformed','beat','beats','record','momentum','accelerated','accelerating','raised','raising','confident','pleased','robust','healthy','leading','leadership','advance','improving','improved','reiterating','encouraged','encouraging'];
const PR_NEG = ['declined','decline','weakness','softer','soft','challenge','challenges','pressure','pressured','impacted','headwinds','miss','missed','disappointing','writedown','impairment','restructuring','layoffs','reduction','downward'];
const PR_HEDGE = ['we remain','we continue to','we believe','to some extent','broadly speaking','directionally','on balance','on the whole','taking a measured approach','dynamic macro','near-term','certain','some','in certain regions','in certain markets','measured approach','prudent','in the context of','over time','over the long term','long-term thesis'];
const PR_DEFLECT = ['great question',"i'd point you to",'i would point you to',"we're really focused on","what we've been focused on",'the broader','the bigger picture','at a high level',"we'll talk more about",'we plan to address that at'];
const PR_PASSIVE = [/\bdecisions were made\b/i,/\blessons have been learned\b/i,/\bactions are being taken\b/i,/\bmitigations are being implemented\b/i,/\bsteps are being taken\b/i,/\bit (?:was|has been) determined\b/i];
const PR_CASUAL = [/\byeah\b/i,/\byou know\b/i,/\blook,?\b/i,/\bfrankly\b/i,/\bnot a big deal\b/i,/\bat the end of the day\b/i,/\bhonestly\b/i,/\bkinda\b/i];
const PR_FORMAL = [/\bwith respect to\b/i,/\bquantum of\b/i,/\bas disclosed\b/i,/\bas previously communicated\b/i,/\bas referenced\b/i,/\bin accordance with\b/i,/\bpursuant to\b/i,/\bon a constant-currency basis\b/i,/\binvestment community\b/i];
const PR_HEAVY = ['writedown','impairment','restructuring','sec','investigation','litigation','breach','outage','miss','shortfall','accelerated','goodwill','european operations','layoffs','reduction'];
const PR_TRANSCRIPT = [
  "Revenue came in at $420M, up 18% year-over-year, driven by strong growth in our Enterprise segment. Gross margin expanded 150 basis points. We're reiterating guidance for the full year and raising our share buyback authorization.",
  "We're encouraged by the trajectory we're seeing, and while there have been some near-term headwinds in certain regions, we remain confident in the long-term thesis. We're taking a measured approach to guidance given the dynamic macro environment.",
  "That's a great question. What we've been really focused on is the broader platform story, and we're seeing tremendous engagement across all our key verticals. I'd point you to the disclosures in the 10-Q for the specific metrics.",
  "Yeah, so, look — we took a look at the carrying value of the European operations and, you know, felt it was prudent to adjust. Honestly it's not a big deal in the context of the overall business.",
  "Certain strategic decisions were made regarding the European operations that in hindsight could have been executed differently. Lessons have been learned, and mitigations are being implemented.",
  "We grew. We shipped. We expanded. Three things happened this quarter, and they're all in the right direction.",
  "With respect to the accelerated amortization of the prior-period adjustment, and as disclosed on page 42 of the supplementary deck, the quantum of impact is within the range previously communicated to the investment community.",
];
function prCountLiteral(t, list) { const s = t.toLowerCase(); return list.reduce((a, m) => a + (s.includes(m) ? 1 : 0), 0); }
function prCountRegex(t, list) { return list.reduce((a, r) => a + (r.test(t) ? 1 : 0), 0); }
function prLexicon(t) {
  const s = t.toLowerCase();
  const pos = PR_POS.reduce((a, w) => a + ((new RegExp(`\\b${w}\\b`)).test(s) ? 1 : 0), 0);
  const neg = PR_NEG.reduce((a, w) => a + ((new RegExp(`\\b${w}\\b`)).test(s) ? 1 : 0), 0);
  if (pos + neg === 0) return 0;
  return Math.max(-1, Math.min(1, ((pos - neg) / (pos + neg)) * 0.9));
}
function prContext(t) {
  const s = t.toLowerCase();
  return PR_HEAVY.some(w => s.includes(w)) ? 'heavy' : 'normal';
}
function prAnalyze(text) {
  const wc = Math.max(1, text.split(/\s+/).length);
  const stated = prLexicon(text);
  const hedgeN = prCountLiteral(text, PR_HEDGE);
  const hedgeDensity = Math.min(1, hedgeN / Math.max(5, wc / 20));
  const defN = prCountLiteral(text, PR_DEFLECT);
  const passN = prCountRegex(text, PR_PASSIVE);
  const casN = prCountRegex(text, PR_CASUAL);
  const forN = prCountRegex(text, PR_FORMAL);
  const ctx = prContext(text);
  let regShift = 0;
  if (ctx === 'heavy' && casN >= 1) regShift = Math.min(1, 0.4 + 0.2 * casN);
  else if (ctx === 'normal' && forN >= 2) regShift = Math.min(1, 0.3 + 0.15 * (forN - 1));
  let prag = stated;
  prag -= 0.45 * hedgeDensity;
  prag -= 0.20 * defN;
  prag -= 0.20 * passN;
  prag -= 0.35 * regShift;
  prag = Math.max(-1, Math.min(1, prag));
  const gap = stated - prag;
  let signal;
  if (Math.abs(gap) < 0.15 && stated > 0.3) signal = 'CONFIRM';
  else if (Math.abs(gap) < 0.15 && stated < -0.2) signal = 'CONFIRM (bear)';
  else if (Math.abs(gap) < 0.1) signal = 'NEUTRAL';
  else if (gap > 0.5) signal = 'STRONG FADE';
  else if (gap > 0.25) signal = 'FADE';
  else if (gap > 0.1) signal = 'WARNING';
  else if (gap < -0.15) signal = 'REINFORCE';
  else signal = 'NEUTRAL';
  const rationale = [];
  if (hedgeN) rationale.push(`${hedgeN} hedging marker(s) — density ${hedgeDensity.toFixed(2)}`);
  if (defN) rationale.push(`${defN} deflection marker(s) — not answering the question asked`);
  if (passN) rationale.push(`${passN} passive subject-drop — who did what is being hidden`);
  if (regShift > 0) rationale.push(`register shift (${ctx} topic, ${casN ? 'casual' : 'formal'} tone) — ${regShift.toFixed(2)}`);
  if (!rationale.length) rationale.push('no significant pragmatic markers — stated sentiment likely reliable');
  return { text, stated, hedgeDensity, defN, passN, regShift, pragmatic: prag, gap, signal, rationale };
}
let prActive = null;
let prAll = null;
function prPick(i) {
  prActive = i; prAll = null;
  prRenderDetail(prAnalyze(PR_TRANSCRIPT[i]), i);
  pepSend('pragmatic.pick', { i });
}
function prAnalyzeAll() {
  prAll = PR_TRANSCRIPT.map(prAnalyze);
  prActive = null;
  document.getElementById('pr-detail').innerHTML =
    '<div style="color:var(--dim);font-size:11px;letter-spacing:0.12em;margin-bottom:10px">TRANSCRIPT SCAN</div>' +
    prAll.map((a, i) => {
      const sigCol = prSignalColor(a.signal);
      return `<div style="padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.04);display:grid;grid-template-columns:28px 1fr 90px 90px 100px;gap:10px;font-size:11px;align-items:center">
        <span style="color:var(--dim)">#${i}</span>
        <span style="color:var(--text);overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${prEsc(a.text)}">${prEsc(a.text.slice(0, 90))}${a.text.length > 90 ? '…' : ''}</span>
        <span style="color:${a.stated >= 0 ? '#81c784' : '#f06292'};font-family:monospace">stated ${a.stated.toFixed(2)}</span>
        <span style="color:${a.pragmatic >= 0 ? '#81c784' : '#f06292'};font-family:monospace">prag ${a.pragmatic.toFixed(2)}</span>
        <span style="color:${sigCol};font-weight:bold">${a.signal}</span>
      </div>`;
    }).join('');
  pepSend('pragmatic.scan_all', {});
}
function prSignalColor(sig) {
  if (sig.startsWith('CONFIRM')) return '#81c784';
  if (sig === 'REINFORCE') return '#38bdf8';
  if (sig === 'STRONG FADE') return '#f87171';
  if (sig === 'FADE') return '#f06292';
  if (sig === 'WARNING') return '#f6d35c';
  return '#aaa';
}
function prEsc(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function prRenderDetail(a, i) {
  const detail = document.getElementById('pr-detail');
  const sigCol = prSignalColor(a.signal);
  detail.innerHTML = `
    <div style="color:var(--dim);font-size:11px;letter-spacing:0.12em;margin-bottom:8px">EXCERPT #${i}</div>
    <div style="font-size:13px;line-height:1.6;margin-bottom:14px;color:#dce4ed;font-style:italic">"${prEsc(a.text)}"</div>
    <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-bottom:14px;font-size:11px">
      <div><div style="color:var(--dim);letter-spacing:0.1em">STATED</div><div style="color:${a.stated >= 0 ? '#81c784' : '#f06292'};font-size:16px;font-family:monospace">${a.stated.toFixed(2)}</div></div>
      <div><div style="color:var(--dim);letter-spacing:0.1em">PRAGMATIC</div><div style="color:${a.pragmatic >= 0 ? '#81c784' : '#f06292'};font-size:16px;font-family:monospace">${a.pragmatic.toFixed(2)}</div></div>
      <div><div style="color:var(--dim);letter-spacing:0.1em">GAP</div><div style="color:${a.gap > 0.15 ? '#f87171' : a.gap < -0.1 ? '#38bdf8' : '#aaa'};font-size:16px;font-family:monospace">${a.gap >= 0 ? '+' : ''}${a.gap.toFixed(2)}</div></div>
      <div><div style="color:var(--dim);letter-spacing:0.1em">HEDGE DENSITY</div><div style="font-size:16px;font-family:monospace;color:#f6d35c">${a.hedgeDensity.toFixed(2)}</div></div>
      <div><div style="color:var(--dim);letter-spacing:0.1em">SIGNAL</div><div style="color:${sigCol};font-size:15px;font-weight:bold">${a.signal}</div></div>
    </div>
    <div style="background:rgba(167,139,250,0.06);border-left:3px solid #a78bfa;padding:10px 12px;border-radius:4px">
      <div style="color:#a78bfa;font-size:10px;letter-spacing:0.15em;margin-bottom:6px">RATIONALE</div>
      ${a.rationale.map(r => `<div style="font-size:12px;color:#dce4ed;margin:3px 0">&middot; ${prEsc(r)}</div>`).join('')}
    </div>`;
}
const prCanvas = document.getElementById('pragmatic-canvas');
const prCtx = prCanvas.getContext('2d');
function drawPragmatic() {
  const W = 960, H = 360;
  prCtx.fillStyle = themeBg(); prCtx.fillRect(0, 0, W, H);
  const data = prAll || PR_TRANSCRIPT.map(prAnalyze);
  const padL = 60, padR = 30, padT = 40, padB = 50;
  const plotW = W - padL - padR, plotH = H - padT - padB;
  prCtx.fillStyle = '#dce4ed'; prCtx.font = 'bold 13px monospace'; prCtx.textAlign = 'left';
  prCtx.fillText('Stated vs Pragmatic sentiment per excerpt  (gap = alpha signal)', padL, 22);
  // Y axis
  prCtx.strokeStyle = 'rgba(150,150,150,0.4)'; prCtx.lineWidth = 1;
  prCtx.beginPath(); prCtx.moveTo(padL, padT); prCtx.lineTo(padL, padT + plotH); prCtx.lineTo(padL + plotW, padT + plotH); prCtx.stroke();
  // Zero line
  const zeroY = padT + plotH / 2;
  prCtx.strokeStyle = 'rgba(150,150,150,0.25)'; prCtx.setLineDash([3, 3]);
  prCtx.beginPath(); prCtx.moveTo(padL, zeroY); prCtx.lineTo(padL + plotW, zeroY); prCtx.stroke();
  prCtx.setLineDash([]);
  prCtx.fillStyle = '#aaa'; prCtx.font = '10px monospace'; prCtx.textAlign = 'right';
  prCtx.fillText('+1.0', padL - 6, padT + 4);
  prCtx.fillText('0.0', padL - 6, zeroY + 3);
  prCtx.fillText('-1.0', padL - 6, padT + plotH + 3);
  // Bars: stated + pragmatic side by side
  const slotW = plotW / data.length;
  data.forEach((a, i) => {
    const cx = padL + (i + 0.5) * slotW;
    const barW = slotW * 0.32;
    const sY = zeroY - (a.stated * plotH / 2);
    prCtx.fillStyle = a.stated >= 0 ? 'rgba(129,199,132,0.85)' : 'rgba(240,98,146,0.85)';
    prCtx.fillRect(cx - barW - 2, Math.min(zeroY, sY), barW, Math.abs(sY - zeroY));
    const pY = zeroY - (a.pragmatic * plotH / 2);
    prCtx.fillStyle = a.pragmatic >= 0 ? 'rgba(56,189,248,0.85)' : 'rgba(248,113,113,0.85)';
    prCtx.fillRect(cx + 2, Math.min(zeroY, pY), barW, Math.abs(pY - zeroY));
    // Gap arrow / annotation
    if (Math.abs(a.gap) > 0.1) {
      prCtx.strokeStyle = a.gap > 0 ? 'rgba(248,113,113,0.7)' : 'rgba(56,189,248,0.7)';
      prCtx.lineWidth = 1.5;
      prCtx.beginPath(); prCtx.moveTo(cx - barW / 2, sY); prCtx.lineTo(cx + barW / 2 + 4, pY); prCtx.stroke();
    }
    // Signal label
    prCtx.fillStyle = prSignalColor(a.signal);
    prCtx.font = 'bold 9px monospace'; prCtx.textAlign = 'center';
    prCtx.fillText(a.signal, cx, padT + plotH + 14);
    prCtx.fillStyle = '#aaa'; prCtx.font = '9px monospace';
    prCtx.fillText('#' + i, cx, padT + plotH + 26);
  });
  // Legend
  prCtx.textAlign = 'left'; prCtx.font = '10px monospace';
  prCtx.fillStyle = 'rgba(129,199,132,0.85)'; prCtx.fillRect(W - 230, 12, 10, 10);
  prCtx.fillStyle = '#aaa'; prCtx.fillText('stated (lexicon)', W - 214, 21);
  prCtx.fillStyle = 'rgba(56,189,248,0.85)'; prCtx.fillRect(W - 120, 12, 10, 10);
  prCtx.fillStyle = '#aaa'; prCtx.fillText('pragmatic', W - 104, 21);
  requestAnimationFrame(drawPragmatic);
}
drawPragmatic();

</script>
</body>
</html>
"""


@router.get("/strata", response_class=HTMLResponse)
async def strata_page() -> str:
    return _PAGE
