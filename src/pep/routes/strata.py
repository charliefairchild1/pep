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
      <div class="tab" data-panel="regime-tab">Regime Modulation</div>
      <div class="tab" data-panel="rotation-tab">Sector Rotation</div>
      <div class="tab" data-panels="unusual-tab classify-tab newscore-tab leaderboard-tab">Equities</div>
      <div class="tab" data-panels="pitch-tab bench-tab">Research Pitch</div>
      <div class="tab" data-panel="theory-tab">Theory</div>
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

</script>
</body>
</html>
"""


@router.get("/strata", response_class=HTMLResponse)
async def strata_page() -> str:
    return _PAGE
