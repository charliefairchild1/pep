"""Unified LAVAS landing page at /. Shows the full suite as one product family."""

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
<title>LAVAS — Five Products, One Engine</title>
<style>
  :root {
    --bg: #0a0c12; --surface: #14181f; --surface2: #0f1318;
    --text: #e2e6ed; --dim: #6a7588; --accent: #a78bfa;
    --border: #1e2430;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
         background: var(--bg); color: var(--text); line-height: 1.6; }
  a { color: var(--accent); text-decoration: none; }
  a:hover { text-decoration: underline; }
  .container { max-width: 1100px; margin: 0 auto; padding: 40px 28px; }
  .hero { text-align: center; padding: 60px 20px 40px; }
  .hero .tag { font-size: 11px; color: var(--dim); letter-spacing: 0.3em;
               text-transform: uppercase; margin-bottom: 10px; }
  .hero h1 { font-size: 32px; color: var(--accent); margin-bottom: 12px;
             font-weight: bold; letter-spacing: 0.5px; }
  .hero p { font-size: 14px; color: var(--text); max-width: 700px;
            margin: 0 auto; line-height: 1.8; }
  .primitives { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap;
                margin: 30px auto 50px; max-width: 800px; }
  .primitive { background: var(--surface); border: 1px solid var(--border);
               border-radius: 6px; padding: 10px 16px; font-size: 11px;
               color: var(--dim); }
  .primitive b { color: var(--accent); }
  .apps { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 16px; margin-bottom: 40px; }
  .app-card { display: block; background: var(--surface); border: 1px solid var(--border);
              border-radius: 10px; padding: 24px 28px; text-decoration: none;
              color: inherit; transition: border-color 0.2s, transform 0.15s; }
  .app-card:hover { border-color: var(--accent); transform: translateY(-2px); text-decoration: none; }
  .app-card .name { font-size: 18px; font-weight: bold; margin-bottom: 4px; }
  .app-card .tagline { font-size: 11px; color: var(--dim); margin-bottom: 10px; }
  .app-card .products { font-size: 10px; color: var(--dim); line-height: 1.7; }
  .app-card .products b { color: var(--text); }
  .app-card .count { font-size: 9px; color: var(--dim); letter-spacing: 0.1em;
                     text-transform: uppercase; margin-top: 10px; }
  .engine { text-align: center; background: var(--surface); border: 1px solid var(--border);
            border-radius: 10px; padding: 28px 32px; margin-bottom: 40px; }
  .engine h2 { font-size: 16px; color: var(--accent); margin-bottom: 8px; }
  .engine p { font-size: 12px; color: var(--dim); max-width: 700px; margin: 0 auto; line-height: 1.8; }
  .engine a { display: inline-block; margin-top: 14px; padding: 8px 20px;
              border: 1px solid var(--accent); border-radius: 6px;
              font-size: 11px; font-weight: bold; }
  .footer { text-align: center; font-size: 10px; color: var(--dim); padding: 20px 0; }
  @media (max-width: 700px) {
    .hero h1 { font-size: 24px; }
    .container { padding: 20px 16px; }
    .apps { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>
<div class="container">
  <div class="hero">
    <div class="tag">PEP Labs</div>
    <h1>Five Products, One Engine</h1>
    <p>
      LAVAS is a suite of products built on PEP (Predictive Encoding and
      Preparation). Five primitives &mdash; weighted graphs, spreading
      activation, residual scoring, state modulation, and opacity-based
      haze &mdash; compose into cognition, language, matching, data
      retrieval, and markets. Same engine, different surfaces.
    </p>
  </div>

  <div class="primitives">
    <div class="primitive"><b>1.</b> Weighted graph</div>
    <div class="primitive"><b>2.</b> Spreading activation</div>
    <div class="primitive"><b>3.</b> Predictor + residual</div>
    <div class="primitive"><b>4.</b> State modulation</div>
    <div class="primitive"><b>5.</b> Opacity / haze</div>
  </div>

  <div class="apps">
    <a class="app-card" href="/axona" style="border-left: 3px solid #ba68c8">
      <div class="name" style="color:#ba68c8">Axona</div>
      <div class="tagline">Brain &amp; Cognition</div>
      <div class="products">
        <b>Products:</b> Edge (performance), BCI SDK, Clinic (session analysis),
        Learn (encoding strength), Wellness (biometrics)<br>
        <b>Canvases:</b> ~60 interactive demos on memory, attention, sleep,
        trauma, media effects, motor prediction, biological substrate
      </div>
      <div class="count">5 products &bull; ~60 canvases &bull; real engine</div>
    </a>

    <a class="app-card" href="/lingora" style="border-left: 3px solid #4fc3f7">
      <div class="name" style="color:#4fc3f7">Lingora</div>
      <div class="tagline">Language as a Cognitive Technology</div>
      <div class="products">
        <b>Products:</b> Prompt (structural analysis), Translate (pragmatic
        preservation), Voice (8-mechanism scoring), Learn (constellation
        vocabulary)<br>
        <b>Canvases:</b> ~70 on words, sounds, sentences, speech acts, writing
      </div>
      <div class="count">4 products &bull; ~70 canvases &bull; real engine</div>
    </a>

    <a class="app-card" href="/atria" style="border-left: 3px solid #5eead4">
      <div class="name" style="color:#5eead4">Atria</div>
      <div class="tagline">Matching &amp; Relational Alignment</div>
      <div class="products">
        <b>Products:</b> Match (PvP matchmaking, AUC 0.977 vs Elo 0.655),
        Date, Hire, Found (cofounders), Therapy<br>
        <b>Canvases:</b> ~20 on compatibility, pool spreading, behavior
        modulation, cross-domain matching
      </div>
      <div class="count">5 products &bull; ~20 canvases &bull; real engine</div>
    </a>

    <a class="app-card" href="/vectora" style="border-left: 3px solid #38bdf8">
      <div class="name" style="color:#38bdf8">Vectora</div>
      <div class="tagline">Data Organization &amp; Intelligent Retrieval</div>
      <div class="products">
        <b>Products:</b> Retrieval API (graph-based), Context (session-aware),
        Watch (anomaly scoring), Graph (knowledge graph builder)<br>
        <b>Dogfooded:</b> powers retrieval across all LAVAS siblings
      </div>
      <div class="count">4 products &bull; 10 canvases &bull; real engine &bull; dogfooded</div>
    </a>

    <a class="app-card" href="/strata" style="border-left: 3px solid #e879f9">
      <div class="name" style="color:#e879f9">Strata</div>
      <div class="tagline">Markets &amp; Trading Signals</div>
      <div class="products">
        <b>Verticals:</b> Equities (shipping, 294 strategies), Crypto, FX,
        Commodities, Prediction Markets, Fixed Income<br>
        <b>Source:</b> StockIntel absorbed as the Equities vertical
      </div>
      <div class="count">6 verticals &bull; canvases + strategies &bull; real engine</div>
    </a>
  </div>

  <div class="engine">
    <h2>The Engine</h2>
    <p>
      PEP is the engine every LAVAS product runs on. Four interactive
      primitive demos, a live mesh dashboard polling all five siblings,
      and the theory that ties everything together. If you want to
      understand what the products are built on, start here.
    </p>
    <a href="/pep">Open PEP Engine &rarr;</a>
  </div>

  <div class="footer">
    PEP Labs LLC &mdash; LAVAS Suite &mdash; 19 products &bull; 372+ tests &bull; same engine
    &mdash; <a href="/math">Math Playground</a>
  </div>
</div>
</body>
</html>
"""


@router.get("/", response_class=HTMLResponse)
async def landing() -> str:
    return _PAGE
