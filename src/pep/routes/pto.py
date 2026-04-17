"""PTO — Potential → Transformation → Output. Theory surface at /pto."""

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
<title>PTO — Potential → Transformation → Output</title>
<style>
  :root {
    --bg: #0d0f14; --surface: #1a1f2a; --surface2: #131821;
    --text: #e2e8f0; --dim: #778; --accent: #a78bfa; --accent2: #34d399;
    --warn: #fbbf24; --danger: #f87171; --border: #252b38;
  }
  body.light {
    --bg: #f8f9fb; --surface: #ffffff; --surface2: #eff2f7;
    --text: #1a1a1a; --dim: #555; --accent: #6d28d9; --accent2: #047857;
    --warn: #b45309; --danger: #b91c1c; --border: #d0d6de;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
         background: var(--bg); color: var(--text); transition: background-color 0.2s, color 0.2s; }
  a { color: var(--accent); text-decoration: none; }
  a:hover { text-decoration: underline; }
  nav { position: sticky; top: 0; z-index: 50; background: var(--bg);
        padding: 6px 20px 0 20px; border-bottom: 1px solid var(--border); }
  .nav-row { display: flex; gap: 14px; align-items: center; flex-wrap: wrap; }
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
  h1 { font-size: 22px; color: var(--accent); margin-bottom: 10px; font-weight: bold; letter-spacing: 0.5px; }
  h2 { font-size: 16px; color: var(--accent); margin-bottom: 6px; }
  h3 { font-size: 13px; color: var(--accent2); margin: 20px 0 8px; }
  p { font-size: 12px; color: var(--text); line-height: 1.8; margin-bottom: 12px; }
  .desc { font-size: 11px; color: var(--dim); line-height: 1.7; margin-bottom: 16px; }
  .hero { background: linear-gradient(180deg, var(--surface) 0%, var(--bg) 100%);
          border: 1px solid var(--border); border-radius: 8px; padding: 28px 32px; margin-bottom: 24px; }
  .hero .tag { font-size: 10px; color: var(--dim); letter-spacing: 0.3em;
               text-transform: uppercase; margin-bottom: 6px; }
  .info { font-size: 11px; color: var(--dim); padding: 12px 16px; background: var(--surface);
          border: 1px solid var(--border); border-radius: 6px; margin-bottom: 16px; line-height: 1.75; }
  .info b { color: var(--text); }
  .card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px;
          padding: 14px 18px; margin-bottom: 12px; }
  .card .name { font-size: 13px; font-weight: bold; color: var(--accent); margin-bottom: 4px; }
  .card .desc { margin-bottom: 0; }
  .math { background: var(--surface2); border-left: 2px solid var(--accent);
          padding: 10px 14px; margin: 10px 0; font-size: 12px; color: var(--text); overflow-x: auto; }
  .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
  .two-col ul { list-style: none; padding: 0; }
  .two-col li { font-size: 11px; padding: 4px 0; color: var(--text); }
  .two-col li::before { content: "→ "; color: var(--accent); }
  .col-bad li::before { color: var(--danger); }
  table { width: 100%; border-collapse: collapse; font-size: 11px; margin: 10px 0 16px; }
  th, td { border: 1px solid var(--border); padding: 7px 10px; text-align: left; vertical-align: top; }
  th { background: var(--surface2); color: var(--accent2); font-weight: normal; }
  td:first-child { color: var(--accent); }
  .canvas-box { background: var(--surface); border: 1px solid var(--border);
                border-radius: 8px; padding: 14px; margin-bottom: 14px; }
  canvas { display: block; width: 100%; background: var(--surface2); border-radius: 4px; }
  .controls { display: flex; flex-wrap: wrap; gap: 14px; align-items: center;
              padding: 10px 4px 4px 4px; font-size: 11px; color: var(--dim); }
  .controls label { display: flex; align-items: center; gap: 6px; }
  .controls input[type="range"] { width: 150px; }
  .controls .val { color: var(--accent); font-weight: bold; min-width: 36px; text-align: right; }
  .readout { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 8px; }
  .readout .box { background: var(--surface2); border: 1px solid var(--border);
                  border-radius: 4px; padding: 8px 10px; }
  .readout .lbl { font-size: 10px; color: var(--dim); text-transform: uppercase; letter-spacing: 0.1em; }
  .readout .val2 { font-size: 14px; color: var(--accent); font-weight: bold; margin-top: 2px; }
  .lavas-switch a { color: var(--accent); padding: 2px 4px; border-radius: 3px; }
  .lavas-switch a:hover { background: var(--surface); }
  .lavas-switch .lavas-current { color: var(--text); font-weight: bold; padding: 2px 4px; opacity: 0.7; }
  @media (max-width: 700px) {
    .two-col { grid-template-columns: 1fr; }
    .readout { grid-template-columns: 1fr; }
    .container { padding: 12px; }
    .hero { padding: 20px 18px; }
    h1 { font-size: 17px; }
    .tabs { overflow-x: auto; flex-wrap: nowrap; -webkit-overflow-scrolling: touch; }
    .tab { white-space: nowrap; padding: 6px 8px; font-size: 10px; }
  }
</style>
</head>
<body>
<nav>
  <div class="nav-row nav-row-top">
    <span class="brand">PTO</span>
    <span style="font-size:10px;color:var(--dim)">Potential → Transformation → Output · the theory PEP implements</span>
    <button onclick="toggleLight()" id="light-btn" class="nav-btn" style="margin-left:auto">Light Mode</button>
    <span class="lavas-switch" style="display:flex;gap:8px;align-items:center;font-size:11px;flex-wrap:wrap">
      <a href="/pep">PEP</a>
      <a href="/axona">Axona</a>
      <a href="/lingora">Lingora</a>
      <a href="/atria">Atria</a>
      <a href="/vectora">Vectora</a>
      <a href="/strata">Strata</a>
      <span class="lavas-current">PTO</span>
    </span>
  </div>
  <div class="nav-row nav-row-bottom">
    <div class="tabs">
      <div class="tab active" data-panel="home-tab">Home</div>
      <div class="tab" data-panel="scope-tab">Scope</div>
      <div class="tab" data-panel="axioms-tab">Axioms</div>
      <div class="tab" data-panel="pipeline-tab">P → T → O</div>
      <div class="tab" data-panel="ratio-tab">Ratio form</div>
      <div class="tab" data-panel="dims-tab">Dimensions</div>
      <div class="tab" data-panel="horizon-tab">Trajectory vs reward</div>
      <div class="tab" data-panel="haze-tab">Haze asymmetry</div>
      <div class="tab" data-panel="capacity-tab">Capacity</div>
      <div class="tab" data-panel="pep-tab">In PEP</div>
      <div class="tab" data-panel="objections-tab">Objections</div>
    </div>
  </div>
</nav>

<!-- ═══ Home ═══════════════════════════════════════════════════════════ -->
<div class="panel active" id="home-tab">
<div class="container">
  <div class="hero">
    <div class="tag">PTO</div>
    <h1>Potential → Transformation → Output</h1>
    <p>
      Every system — a star, a cell, a brain, an AI — sits in front of some
      <b>potential</b>: gradients, resources, information, opportunity.
      <b>Transformation</b> is what the system does with it. <b>Output</b> is
      what comes out. PTO is the claim that systems which persist and spread
      are the ones that do this more effectively across time, under
      constraint — and that "effectively" has a specific shape worth naming.
    </p>
    <p>
      The distinguishing move: PTO is <em>not</em> reward-maximization. A
      reward-maximizer says <code>max O</code>. PTO says maximize constructive
      transformation <em>relative to irreversible loss</em>, over a horizon
      long enough for future capacity to count. The best move is the one that
      improves the structure of future moves.
    </p>
    <p style="color:var(--dim);font-size:11px">
      This page is the theory. <a href="/pep">/pep</a> is the engine that
      implements it. The five LAVAS siblings are domain applications.
    </p>
  </div>

  <h3>Is PTO mainly math?</h3>
  <div class="info">
    No. PTO is a systems principle with four layers, and the math is just one
    of them:
    <ol style="margin:8px 0 0 20px;padding:0;font-size:11px;line-height:1.8">
      <li><b>Ontological claim</b> — what kinds of systems persist and spread. (Prose.)</li>
      <li><b>Axiomatic framing</b> — primitive terms and stipulated structure. (See <em>Axioms</em> tab.)</li>
      <li><b>Mathematical optimality</b> — the trajectory functional. (See <em>Ratio</em>, <em>Trajectory</em>, <em>Capacity</em> tabs.)</li>
      <li><b>Engineering design rules</b> — measurable goals and gating questions. (Encoded in every LAVAS sibling.)</li>
    </ol>
    Without layer 1, the axioms are arbitrary. Without layer 4, the math has
    nothing to touch the ground. "PTO is math" is only true of the skeleton.
  </div>

  <h3>The five requirements for any system that wants to claim PTO</h3>
  <div class="card"><div class="name">1 · Coherence</div><div class="desc">Internally consistent as it grows. No silent contradictions.</div></div>
  <div class="card"><div class="name">2 · Relevance</div><div class="desc">Privilege transformations that matter to current goals and future adaptability.</div></div>
  <div class="card"><div class="name">3 · Compression</div><div class="desc">Reduce complexity without erasing what later becomes important.</div></div>
  <div class="card"><div class="name">4 · Recoverability</div><div class="desc">Lost detail should be reconstructable when needed. Forgetting ≠ loss.</div></div>
  <div class="card"><div class="name">5 · Adaptivity</div><div class="desc">Structures should reorganize when new information changes the landscape.</div></div>
</div></div>

<!-- ═══ Scope ════════════════════════════════════════════════════════ -->
<div class="panel" id="scope-tab">
<div class="container">
  <h2>Scope — what PTO claims and does not claim</h2>
  <div class="desc">
    Most systems-theoretic frameworks collapse under their own ambition. PTO
    keeps working by being explicit about what it claims, what it doesn't,
    and where it has no opinion.
  </div>

  <div class="two-col">
    <div>
      <h3 style="color:var(--accent2)">PTO claims</h3>
      <ul>
        <li>Systems differ in how effectively they convert available potential into durable, future-enabling structure.</li>
        <li>This effectiveness is formalizable as a <em>trajectory-level</em> objective, not a per-step reward.</li>
        <li>Systems that score higher on that objective tend to persist longer in their environments.</li>
        <li>The framework is substrate-agnostic: physics, biology, cognition, economics, computation all admit PTO interpretation.</li>
      </ul>
    </div>
    <div class="col-bad">
      <h3 style="color:var(--danger)">PTO does not claim</h3>
      <ul>
        <li>That the universe has intent, purpose, or teleology.</li>
        <li>That all systems are PTO-optimizers — only that persistence correlates with PTO score.</li>
        <li>That PTO-optimal is ethically good. A bioweapon can be PTO-optimal.</li>
        <li>That PTO subsumes thermodynamics, evolution, or control theory. It frames them under a shared objective.</li>
        <li>That horizon H is universal. Each system has its own, measured from behavior.</li>
        <li>That β or H are <em>discovered</em> by systems. They are implicit properties.</li>
      </ul>
    </div>
  </div>

  <h3>When PTO and reward-maximization coincide</h3>
  <div class="info">
    At very short horizons (H → τ_local, the system's local reward window),
    PTO collapses to reward-maximization. This is not a failure of PTO — it
    is a scope clause. PTO makes no claim about sub-τ_local optimization.
    Reward-maximizers are correct when the horizon is short enough;
    PTO-maximizers diverge (and win on persistence) as H grows.
  </div>

  <h3>When PTO is not the right frame at all</h3>
  <div class="info">
    <b>Closed systems in equilibrium.</b> Nothing is being transformed.
    <br>
    <b>Systems with no admissible controls.</b> If u is empty, there are no policies to compare.
    <br>
    <b>Systems where persistence is not the selection criterion.</b> PTO's empirical claim (A7) depends on selection favoring persisters. If the environment actively selects against persistence — a sacrificial process, for example — use a different frame.
  </div>
</div></div>

<!-- ═══ Axioms ═══════════════════════════════════════════════════════ -->
<div class="panel" id="axioms-tab">
<div class="container">
  <h2>Eight axioms</h2>
  <div class="desc">
    Each axiom does independent work; none is a restatement of another.
    Together they characterize the class of systems PTO applies to. They are
    <em>stipulated</em> — they define the frame. Whether real systems
    satisfy them is an empirical question per axiom.
  </div>

  <div class="card">
    <div class="name">A1 · Transformation primacy</div>
    <div class="desc">A system's state change is describable by a rate T acting on available potential P, distinct from both gross activity and net output.</div>
  </div>
  <div class="card">
    <div class="name">A2 · Dissipation floor</div>
    <div class="desc">Every transformation incurs positive total dissipation D > 0. No transformation is free. (Thermodynamic inheritance.)</div>
  </div>
  <div class="card">
    <div class="name">A3 · Asymmetric dissipation</div>
    <div class="desc">D = D_irr + D_rec where D_irr is information-theoretically irreversible and D_rec is recoverable from surrounding state. Only D_irr strictly reduces future capacity. <em>The axiom that distinguishes PTO from ordinary optimization.</em></div>
  </div>
  <div class="card">
    <div class="name">A4 · Capacity exists, non-circularly</div>
    <div class="desc">There exists a scalar C(x,t) measuring future transformability, definable independently of any future value of T. Circular definitions (C := E[∫T]) are rejected. <em>The axiom that keeps PTO from collapsing into empowerment.</em></div>
  </div>
  <div class="card">
    <div class="name">A5 · Constructive decomposition</div>
    <div class="desc">T = α·O + β·(dC/dt) + Σ<sub>k</sub> w<sub>k</sub>·Δq<sub>k</sub>, with α, β, w<sub>k</sub> ≥ 0. Output, capacity-shaping, and per-dimension constructive gains are additive.</div>
  </div>
  <div class="card">
    <div class="name">A6 · Horizon primacy</div>
    <div class="desc">Optimality is defined over H > τ_local. PTO makes no claim about sub-τ_local optimization; at short horizons, PTO and reward-maximization coincide.</div>
  </div>
  <div class="card">
    <div class="name">A7 · Trajectory selection</div>
    <div class="desc">Among admissible policies u(·), persistence favors those maximizing J_H[u] = E[∫<sub>t</sub><sup>t+H</sup>(T − λ·D_irr)dτ | x(t)]. "Favors" is empirical: higher J_H correlates with higher persistence probability across the ensemble.</div>
  </div>
  <div class="card">
    <div class="name">A8 · Domain closure</div>
    <div class="desc">Applies wherever (X, U, f, μ) — state space, admissible controls, dynamics, utility measure — exist. No substrate is privileged. Physical, biological, cognitive, computational systems all qualify.</div>
  </div>

  <h3>Derivable propositions</h3>
  <div class="info">
    From A1–A8:
    <br><br>
    <b>P1.</b> Reward-maximizers are PTO-suboptimal at sufficient horizon. (A5, A6, A7.)
    <br>
    <b>P2.</b> Equal-dissipation accounting is sub-optimal — under-uses haze. (A3, A7.)
    <br>
    <b>P3.</b> Output-only systems (β = 0) collapse to reward-maximization. A degenerate case, not an alternative. (A5.)
    <br>
    <b>P4.</b> Two systems with identical O can have different J_H when their capacity trajectories differ. (A5, A7.)
    <br>
    <b>P5.</b> Horizon miscalibration produces apparent reward-maximization. (A6, A7.)
    <br>
    <b>P6.</b> D_rec can silently migrate to D_irr if reconstruction context is itself hazed. Motivates PEP's drift tracking. (A3.)
    <br>
    <b>P7.</b> Substrate-independence is a corollary of A8.
  </div>

  <h3>Which axioms carry the distinctive weight</h3>
  <div class="info">
    <b>A3 and A4</b> are what make PTO not-RL and not-empowerment. Remove A3
    and you get ordinary control theory with a scalar cost. Remove A4 and
    you get a circular definition that either collapses into empowerment
    (if C = reachable volume) or cannot be computed (if C = E[∫T]).
    A5–A7 operationalize; A3–A4 distinguish.
  </div>
</div></div>

<!-- ═══ Pipeline ═══════════════════════════════════════════════════════ -->
<div class="panel" id="pipeline-tab">
<div class="container">
  <h2>P → T → O — the pipeline</h2>
  <div class="desc">
    The three nouns in the name, each doing real work. <b>P</b>otential enters;
    the system <b>T</b>ransforms it; <b>O</b>utput leaves — but the system is
    also changed. That second effect is what turns PTO from a throughput
    metric into a trajectory claim.
  </div>

  <div class="canvas-box"><canvas id="pipeline-canvas" height="220"></canvas></div>

  <div class="info">
    <b>P (potential)</b> — what is available to transform: gradients,
    resources, signals, opportunity, uncertainty. <br>
    <b>T (transformation)</b> — the rate at which the system does
    constructive work on P. Decomposes into present output plus future
    capacity gain. <br>
    <b>O (output)</b> — the realized immediate effect. What another system
    would see if it watched only the interface.
  </div>

  <h3>Why this shape</h3>
  <p>
    Ordinary models of a system have inputs and outputs. PTO names the middle
    explicitly and insists that the middle is <em>what is being optimized</em>.
    You cannot evaluate a system by its outputs alone, because two systems
    with identical O can have wildly different T — one burning everything
    available, the other building durable structure. The first looks
    productive; the second is what persists.
  </p>
</div></div>

<!-- ═══ Ratio ═════════════════════════════════════════════════════════ -->
<div class="panel" id="ratio-tab">
<div class="container">
  <h2>The ratio form</h2>
  <div class="desc">
    The cleanest one-line statement of PTO. Move the sliders; watch the
    ratio. Notice that raw output going up is not the same as F going up.
  </div>

  <div class="math">
    F(t) = T(t) / D_irr(t) &nbsp;&nbsp; where &nbsp;&nbsp; T = α·O + β·(dC/dt)
  </div>

  <div class="canvas-box">
    <div class="controls">
      <label>α (output weight) <input id="r-alpha" type="range" min="0" max="1" step="0.05" value="0.6"><span class="val" id="r-alpha-v">0.60</span></label>
      <label>β (capacity weight) <input id="r-beta" type="range" min="0" max="1" step="0.05" value="0.4"><span class="val" id="r-beta-v">0.40</span></label>
      <label>O (output rate) <input id="r-O" type="range" min="0" max="10" step="0.1" value="4"><span class="val" id="r-O-v">4.0</span></label>
      <label>dC/dt (capacity gain) <input id="r-dC" type="range" min="-3" max="5" step="0.1" value="1"><span class="val" id="r-dC-v">1.0</span></label>
      <label>D_irr (irreversible loss) <input id="r-D" type="range" min="0.1" max="10" step="0.1" value="2"><span class="val" id="r-D-v">2.0</span></label>
    </div>
    <div class="readout">
      <div class="box"><div class="lbl">T</div><div class="val2" id="r-T">—</div></div>
      <div class="box"><div class="lbl">D_irr</div><div class="val2" id="r-Dout">—</div></div>
      <div class="box"><div class="lbl">F = T / D_irr</div><div class="val2" id="r-F">—</div></div>
    </div>
  </div>

  <div class="info">
    <b>Try this:</b> set O high and dC/dt low — you get big output but mediocre
    F. Now flip it: modest O, strong dC/dt. The system is <em>indexing,
    compressing, learning</em>. Output looks smaller; F is higher; the next
    turn starts from a better state. That is the trajectory claim, reduced to
    two sliders.
  </div>
</div></div>

<!-- ═══ Dimensions ═══════════════════════════════════════════════════ -->
<div class="panel" id="dims-tab">
<div class="container">
  <h2>Constructive vs dissipative</h2>
  <div class="desc">
    T and D are not scalars you read off a gauge; they decompose into named
    dimensions. A transformation is <b>constructive</b> if it moves the left
    column up, <b>dissipative</b> if it moves the right column up. Every
    LAVAS app weights these differently.
  </div>

  <div class="two-col">
    <div>
      <h3 style="color:var(--accent2)">Constructive (feeds T)</h3>
      <ul>
        <li>predictive power</li>
        <li>contextual accuracy</li>
        <li>retrieval precision</li>
        <li>conceptual coherence</li>
        <li>action usefulness</li>
        <li>compression quality</li>
        <li>adaptability to novelty</li>
        <li>preservation of important distinctions</li>
        <li>future learning capacity</li>
      </ul>
    </div>
    <div class="col-bad">
      <h3 style="color:var(--danger)">Dissipative (feeds D_irr)</h3>
      <ul>
        <li>noise</li>
        <li>confusion</li>
        <li>redundancy</li>
        <li>hallucination risk</li>
        <li>contradiction</li>
        <li>brittleness</li>
        <li>retrieval drag</li>
        <li>semantic collapse</li>
        <li>loss of recoverable detail</li>
      </ul>
    </div>
  </div>

  <h3>Weighted decomposition</h3>
  <div class="math">
    T(t) = α·O(t) + β·(dC/dt) + Σ<sub>k</sub> w<sub>k</sub> · Δq<sub>k</sub>(t)
  </div>
  <p>
    Each <code>Δq<sub>k</sub></code> is a per-dimension gain (predictive
    accuracy gained, ambiguity reduced, etc.). The weights <code>w<sub>k</sub></code>
    are what each LAVAS sibling picks for its domain.
  </p>
</div></div>

<!-- ═══ Horizon demo ═══════════════════════════════════════════════════ -->
<div class="panel" id="horizon-tab">
<div class="container">
  <h2>Trajectory vs reward — why horizon matters</h2>
  <div class="desc">
    The single most important distinction in PTO. A reward-maximizer looks at
    the next turn. PTO looks at the next H turns. When H is small enough,
    they agree. When H grows, they diverge — and PTO wins on any metric that
    cares about the system still working in 100 turns.
  </div>

  <div class="canvas-box">
    <div class="controls">
      <label>horizon H <input id="h-range" type="range" min="1" max="80" step="1" value="20"><span class="val" id="h-range-v">20</span></label>
      <label>capacity-investment rate β <input id="h-beta" type="range" min="0" max="1" step="0.05" value="0.5"><span class="val" id="h-beta-v">0.50</span></label>
    </div>
    <canvas id="horizon-canvas" height="260"></canvas>
    <div class="readout">
      <div class="box"><div class="lbl">reward-max total</div><div class="val2" id="h-rm">—</div></div>
      <div class="box"><div class="lbl">PTO total</div><div class="val2" id="h-pto" style="color:var(--accent2)">—</div></div>
      <div class="box"><div class="lbl">PTO advantage</div><div class="val2" id="h-adv" style="color:var(--warn)">—</div></div>
    </div>
  </div>

  <div class="info">
    The reward-max policy burns potential immediately: high O, flat dC/dt,
    output curve tall early and collapsing later. The PTO policy invests
    some fraction β of each turn into dC/dt (indexing, compressing, building
    structure). Its early output is smaller. Around the point where the
    capacity investment matures, its cumulative total crosses reward-max's
    and keeps going.
    <br><br>
    <b>This is why PEP is not a chatbot with better memory.</b> A chatbot
    optimizes per-turn response quality. PEP optimizes the shape of turn
    N+50.
  </div>
</div></div>

<!-- ═══ Haze ═════════════════════════════════════════════════════════ -->
<div class="panel" id="haze-tab">
<div class="container">
  <h2>D_irr vs D_rec — the dissipation asymmetry</h2>
  <div class="desc">
    Ordinary optimization penalizes all cost equally. PTO splits dissipation
    into <b>irreversible</b> (heat, semantic collapse, information-theoretic
    loss) and <b>recoverable</b> (structure temporarily below the reuse
    threshold but reconstructible from context). Only the first is penalized.
  </div>

  <div class="math">
    D(t) = D_irr(t) + D_rec(t) &nbsp;&nbsp;&nbsp; J_H[u] = E[ ∫ (T − λ·D_irr) dτ ]
  </div>

  <p>
    <b>Haze</b> is PEP's engineering name for D_rec. Every node in the memory
    graph has an encoding strength that decays over time; nodes below the
    reuse threshold can be overwritten <em>but the information is still
    reconstructible from neighbors and context until it isn't.</em> Haze
    makes capacity finite without making it fragile.
  </p>

  <p>
    If a system treats all forgetting as loss, it will either hoard
    (infinite storage, retrieval drag goes to the ceiling) or panic-prune
    (irreversible loss of things it will later need). The D_irr / D_rec
    split is how PEP avoids both.
  </p>

  <h3>When does D_rec become D_irr?</h3>
  <p>
    When the reconstruction path is gone. If a node's neighbors are all also
    hazed below threshold, and no external anchor pins the memory, D_rec has
    silently become D_irr. Drift tracking is the honesty layer that catches
    this. Open problem: the formal criterion for the transition is
    unfinished — see <code>docs/pto_math.md</code> §9.
  </p>
</div></div>

<!-- ═══ Capacity ═══════════════════════════════════════════════════════ -->
<div class="panel" id="capacity-tab">
<div class="container">
  <h2>Capacity, defined non-circularly</h2>
  <div class="desc">
    C is the load-bearing term. The tempting definition — "expected future
    T" — is circular: T depends on dC/dt. PTO needs C anchored in something
    that is not itself a transformation rate. Two candidates both work.
  </div>

  <h3>(a) Reachable-utility volume</h3>
  <div class="math">
    C(x, t) = ∫<sub>R<sub>H</sub>(x)</sub> μ(y) dy
  </div>
  <p>
    The measure of useful future states reachable from x under admissible
    controls, weighted by a domain utility μ. This is close to <em>empowerment</em>
    in the Klyubin/Polani sense. Vectora's retrieval graph lives here: what
    queries can I answer well from my current index? is a reachable-utility
    question.
  </p>

  <h3>(b) Predictive mutual information</h3>
  <div class="math">
    C(x, t) = I( past ; future | x(t) )
  </div>
  <p>
    The information the current state retains about the past that is relevant
    to the future. Bialek/Still's <em>predictive information</em>. Lingora
    and Axona live here: how much of what I've seen is doing work in what I'm
    about to predict?
  </p>

  <p style="color:var(--dim);font-size:11px">
    Both are computable (with approximation). Neither is circular. Every
    LAVAS app can pick the one that fits its substrate.
  </p>
</div></div>

<!-- ═══ PEP mapping ══════════════════════════════════════════════════ -->
<div class="panel" id="pep-tab">
<div class="container">
  <h2>PTO mapped onto PEP modules</h2>
  <div class="desc">
    Every module in PEP is doing one of four jobs: (i) measuring T, (ii)
    preserving C, (iii) distinguishing D_irr from D_rec, or (iv) extending
    the optimization horizon H.
  </div>

  <table>
    <thead><tr><th>PEP module</th><th>PTO role</th></tr></thead>
    <tbody>
      <tr><td>Predictor</td><td>produces Δq_pred and Δq_amb. Forecast minus reality is the only learning signal.</td></tr>
      <tr><td>Residual scorer</td><td>decides which events enter dC/dt. Storage budget goes to things that increase <em>future</em> transformation.</td></tr>
      <tr><td>Reactivator (spreading activation)</td><td>pulls C into T. Low-resistance path from current need to useful structure.</td></tr>
      <tr><td>State modulator</td><td>sets domain weights w_k. The affective layer is exactly PTO's view of salience regulation.</td></tr>
      <tr><td>Haze / opacity</td><td>enforces the D_irr / D_rec split. Compression without irreversibility.</td></tr>
      <tr><td>Multi-face memory</td><td>preserves recoverability of C. One object, several reachable interpretations.</td></tr>
      <tr><td>Drift tracking</td><td>honesty about when D_rec has become D_irr.</td></tr>
      <tr><td>Evaluator</td><td>scores J_H[u], not per-turn accuracy. The horizon-extension module.</td></tr>
    </tbody>
  </table>

  <h3>LAVAS specialization</h3>
  <table>
    <thead><tr><th>App</th><th>Dominant dimensions</th><th>Primary C form</th></tr></thead>
    <tbody>
      <tr><td><a href="/vectora">Vectora</a></td><td>Δq_ret, Δq_cmp</td><td>reachable-utility (graph)</td></tr>
      <tr><td><a href="/lingora">Lingora</a></td><td>Δq_cmp, Δq_coh</td><td>predictive info</td></tr>
      <tr><td><a href="/atria">Atria</a></td><td>Δq_pred over compatibility</td><td>reachable-utility (match graph)</td></tr>
      <tr><td><a href="/axona">Axona</a></td><td>Δq_coh, Δq_adp</td><td>state-space volume</td></tr>
      <tr><td><a href="/strata">Strata</a></td><td>Δq_amb, Δq_adp</td><td>reachable-utility (regime space)</td></tr>
    </tbody>
  </table>

  <div class="info">
    For the full formal spine see <code>docs/pto_math.md</code>. For the prose
    statement see <code>docs/pto.md</code>. This page is the bridge between
    them.
  </div>
</div></div>

<!-- ═══ Objections ═══════════════════════════════════════════════════ -->
<div class="panel" id="objections-tab">
<div class="container">
  <h2>Objections and replies</h2>
  <div class="desc">
    Objections that come up about PTO, and the sharpest reply I have for
    each. If the reply is weak, that is marked.
  </div>

  <h3 style="color:var(--danger)">"Capacity C is vague."</h3>
  <p>Only if you decline to pick a definition. The <em>Capacity</em> tab gives two non-circular ones (reachable-utility volume and predictive mutual information). Commit to one per domain and C becomes measurable.</p>

  <h3 style="color:var(--danger)">"β is a free parameter."</h3>
  <p>Yes. It encodes the system's investment policy. Systems don't discover their β; they have it, implicitly, and you can measure it from behavior. A reward-maximizer has β = 0 by revealed behavior.</p>

  <h3 style="color:var(--danger)">"The horizon H is a free parameter."</h3>
  <p>Also yes. It encodes what persistence means for this system. An organism's H is its lifespan; a chat session's is turn count; a trading agent's is the regime-change timescale. Pick wrong and you are not doing PTO — you are doing some other optimization under PTO's name.</p>

  <h3 style="color:var(--danger)">"This is multi-objective RL with a capacity bonus."</h3>
  <p>Closer than thermodynamics or free energy, but no. RL optimizes a fixed reward function. PTO's T includes dC/dt, which itself depends on future T — PTO is about trajectory shape, not climbing a pre-specified reward surface. The D_irr/D_rec asymmetry (A3) is also outside RL's standard framing.</p>

  <h3 style="color:var(--danger)">"Isn't this teleology with equations?"</h3>
  <p>No. PTO does not claim systems <em>try</em> to be PTO-optimal. It claims PTO-optimal systems persist, and persisters dominate the observable ensemble. Same logic as natural selection — descriptive, not teleological.</p>

  <h3 style="color:var(--danger)">"Why call it PTO, not fitness?"</h3>
  <p>Fitness is reproductive success. PTO applies to non-biological systems — data structures, markets, language models — where reproduction is ill-defined but persistence is not.</p>

  <h3 style="color:var(--danger)">"Axioms A3 and A4 carry all the work."</h3>
  <p>Partly true. A3 (dissipation asymmetry) and A4 (non-circular capacity) are what distinguish PTO from ordinary optimization. A5–A7 operationalize; A3–A4 distinguish. This is a feature, not a bug — it tells you what to drop if you want a weaker cousin of PTO.</p>

  <h3 style="color:var(--danger)">"A7 is unfalsifiable — any persister gets labeled PTO-optimal post-hoc."</h3>
  <p style="color:var(--warn)">
    <b>This one is real.</b> The fix: operationalize A7 by (i) pre-registering
    C, β, H <em>before</em> measurement, (ii) computing J_H across an ensemble
    of systems sharing a substrate, (iii) measuring persistence empirically
    (uptime, user retention, benchmark-longevity), (iv) checking the
    pre-registered correlation. The math spine (§14 Open problems) flags this
    as unfinished.
  </p>

  <h3 style="color:var(--danger)">"Why does PEP need PTO? Can't the engine stand alone?"</h3>
  <p>The engine can run without PTO. The <em>design decisions</em> cannot. Why split D into D_irr and D_rec? Why have haze at all? Why evaluate over sessions rather than per-turn? Each answer lives in PTO. Strip PTO out and PEP still works, but every future choice loses its spine.</p>
</div></div>

<script>
// Tabs
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    tab.classList.add('active');
    const id = tab.dataset.panel;
    const el = document.getElementById(id);
    if (el) el.classList.add('active');
    window.scrollTo(0, 0);
  });
});

// Light mode
function toggleLight() {
  const isLight = document.body.classList.toggle('light');
  const btn = document.getElementById('light-btn');
  if (btn) btn.textContent = isLight ? 'Dark Mode' : 'Light Mode';
  try { localStorage.setItem('pto-theme', isLight ? 'light' : 'dark'); } catch (e) {}
  drawPipeline(); drawHorizon();
}
(function restoreTheme() {
  try {
    if (localStorage.getItem('pto-theme') === 'light') {
      document.body.classList.add('light');
      const btn = document.getElementById('light-btn');
      if (btn) btn.textContent = 'Dark Mode';
    }
  } catch (e) {}
})();

function cssVar(name) { return getComputedStyle(document.body).getPropertyValue(name).trim(); }

// ═══ Pipeline diagram ════════════════════════════════════════════════
const pipeCanvas = document.getElementById('pipeline-canvas');
const pipeCtx = pipeCanvas.getContext('2d');
let pipePhase = 0;

function resizeCanvas(c) {
  const dpr = window.devicePixelRatio || 1;
  const w = c.clientWidth;
  const h = parseInt(c.getAttribute('height'), 10) || c.clientHeight;
  c.width = w * dpr; c.height = h * dpr;
  const ctx = c.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  return { w, h, ctx };
}

function drawPipeline() {
  const { w, h, ctx } = resizeCanvas(pipeCanvas);
  ctx.clearRect(0, 0, w, h);
  const accent = cssVar('--accent'), accent2 = cssVar('--accent2'), dim = cssVar('--dim'),
        text = cssVar('--text'), border = cssVar('--border');
  const nodes = [
    { x: w * 0.15, label: 'P', sub: 'potential' },
    { x: w * 0.50, label: 'T', sub: 'transformation' },
    { x: w * 0.85, label: 'O', sub: 'output' },
  ];
  const cy = h * 0.5;
  // edges
  ctx.strokeStyle = border; ctx.lineWidth = 1.5;
  for (let i = 0; i < nodes.length - 1; i++) {
    ctx.beginPath(); ctx.moveTo(nodes[i].x + 30, cy); ctx.lineTo(nodes[i+1].x - 30, cy); ctx.stroke();
  }
  // animated particles along edges
  pipePhase = (pipePhase + 0.012) % 1;
  ctx.fillStyle = accent;
  for (let i = 0; i < nodes.length - 1; i++) {
    for (let k = 0; k < 3; k++) {
      const t = (pipePhase + k / 3) % 1;
      const x = nodes[i].x + 30 + (nodes[i+1].x - 30 - (nodes[i].x + 30)) * t;
      ctx.beginPath(); ctx.arc(x, cy, 2.5, 0, Math.PI * 2); ctx.fill();
    }
  }
  // feedback arc T → (changes system state)
  ctx.strokeStyle = accent2; ctx.lineWidth = 1.5; ctx.setLineDash([4, 4]);
  ctx.beginPath();
  ctx.moveTo(nodes[1].x, cy + 30);
  ctx.bezierCurveTo(nodes[1].x - 40, cy + 80, nodes[1].x - 120, cy + 80, nodes[1].x - 160, cy + 20);
  ctx.stroke();
  ctx.setLineDash([]);
  ctx.fillStyle = accent2; ctx.font = '10px monospace';
  ctx.fillText('dC/dt  (future capacity)', nodes[1].x - 130, cy + 95);
  // nodes
  nodes.forEach(n => {
    ctx.fillStyle = cssVar('--surface2'); ctx.strokeStyle = accent; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.arc(n.x, cy, 30, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
    ctx.fillStyle = accent; ctx.font = 'bold 18px monospace'; ctx.textAlign = 'center';
    ctx.fillText(n.label, n.x, cy + 6);
    ctx.fillStyle = dim; ctx.font = '10px monospace';
    ctx.fillText(n.sub, n.x, cy + 52);
  });
  requestAnimationFrame(drawPipeline);
}
setTimeout(drawPipeline, 50);

// ═══ Ratio sliders ═══════════════════════════════════════════════════
function updateRatio() {
  const a = parseFloat(document.getElementById('r-alpha').value);
  const b = parseFloat(document.getElementById('r-beta').value);
  const O = parseFloat(document.getElementById('r-O').value);
  const dC = parseFloat(document.getElementById('r-dC').value);
  const D = parseFloat(document.getElementById('r-D').value);
  document.getElementById('r-alpha-v').textContent = a.toFixed(2);
  document.getElementById('r-beta-v').textContent = b.toFixed(2);
  document.getElementById('r-O-v').textContent = O.toFixed(1);
  document.getElementById('r-dC-v').textContent = dC.toFixed(1);
  document.getElementById('r-D-v').textContent = D.toFixed(1);
  const T = a * O + b * dC;
  const F = T / Math.max(D, 0.01);
  document.getElementById('r-T').textContent = T.toFixed(2);
  document.getElementById('r-Dout').textContent = D.toFixed(2);
  document.getElementById('r-F').textContent = F.toFixed(2);
}
['r-alpha','r-beta','r-O','r-dC','r-D'].forEach(id => {
  document.getElementById(id).addEventListener('input', updateRatio);
});
updateRatio();

// ═══ Horizon demo ════════════════════════════════════════════════════
const horizonCanvas = document.getElementById('horizon-canvas');
function drawHorizon() {
  const { w, h, ctx } = resizeCanvas(horizonCanvas);
  ctx.clearRect(0, 0, w, h);
  const accent = cssVar('--accent'), accent2 = cssVar('--accent2'),
        dim = cssVar('--dim'), text = cssVar('--text'), border = cssVar('--border'),
        danger = cssVar('--danger');
  const H = parseInt(document.getElementById('h-range').value, 10);
  const beta = parseFloat(document.getElementById('h-beta').value);
  document.getElementById('h-range-v').textContent = H;
  document.getElementById('h-beta-v').textContent = beta.toFixed(2);

  // Simulate two policies over N turns
  const N = 80;
  // Reward-max: always spend, C flat, O = 1 per turn but degrades as potential depletes
  // PTO: spend (1-beta), invest beta into C. Future O grows with C.
  const rm = [], pto = [];
  let P1 = 10, P2 = 10;  // shared potential budget
  let C_rm = 0, C_pto = 0;
  let sum_rm = 0, sum_pto = 0;
  for (let t = 0; t < N; t++) {
    // reward-max
    const o_rm = Math.min(P1, 1.0 + 0.05 * C_rm);
    P1 -= o_rm * 0.4;
    P1 = Math.max(P1, 0.2);
    sum_rm += o_rm;
    rm.push({ t, o: o_rm, cum: sum_rm });
    // PTO
    const spend = 1.0 * (1 - beta);
    const invest = 1.0 * beta;
    const o_pto = Math.min(P2, spend * (1 + 0.22 * C_pto));
    C_pto += invest * (1 - C_pto / 20);  // diminishing returns on capacity
    P2 -= (o_pto + invest * 0.3) * 0.4;
    P2 = Math.max(P2, 0.2);
    sum_pto += o_pto + beta * 0.15 * C_pto;  // β·dC/dt contribution
    pto.push({ t, o: o_pto, cum: sum_pto });
  }
  // layout
  const pad = 30;
  const plotW = w - pad * 2, plotH = h - pad * 2 - 16;
  // axes
  ctx.strokeStyle = border; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(pad, pad); ctx.lineTo(pad, pad + plotH); ctx.lineTo(pad + plotW, pad + plotH); ctx.stroke();
  // scale
  const maxCum = Math.max(sum_rm, sum_pto, 1);
  function px(t) { return pad + (t / (N - 1)) * plotW; }
  function py(v) { return pad + plotH - (v / maxCum) * plotH; }
  // horizon shading
  const xH = px(H);
  ctx.fillStyle = 'rgba(167, 139, 250, 0.06)';
  ctx.fillRect(pad, pad, xH - pad, plotH);
  ctx.strokeStyle = accent; ctx.setLineDash([3, 3]);
  ctx.beginPath(); ctx.moveTo(xH, pad); ctx.lineTo(xH, pad + plotH); ctx.stroke();
  ctx.setLineDash([]);
  ctx.fillStyle = dim; ctx.font = '10px monospace'; ctx.textAlign = 'left';
  ctx.fillText('horizon H', xH + 4, pad + 12);
  // reward-max curve
  ctx.strokeStyle = danger; ctx.lineWidth = 2;
  ctx.beginPath(); rm.forEach((p, i) => { const x = px(p.t), y = py(p.cum); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); }); ctx.stroke();
  // PTO curve
  ctx.strokeStyle = accent2; ctx.lineWidth = 2;
  ctx.beginPath(); pto.forEach((p, i) => { const x = px(p.t), y = py(p.cum); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); }); ctx.stroke();
  // labels
  ctx.fillStyle = danger; ctx.font = '11px monospace'; ctx.textAlign = 'left';
  ctx.fillText('reward-max', pad + 4, pad - 8);
  ctx.fillStyle = accent2; ctx.fillText('PTO', pad + 90, pad - 8);
  ctx.fillStyle = dim; ctx.textAlign = 'right';
  ctx.fillText('turn →', pad + plotW, pad + plotH + 14);
  ctx.textAlign = 'left';
  ctx.fillText('cumulative transformation', pad, pad + plotH + 14);

  // readouts for totals within horizon
  const rm_H = rm[Math.min(H, N) - 1].cum;
  const pto_H = pto[Math.min(H, N) - 1].cum;
  document.getElementById('h-rm').textContent = rm_H.toFixed(1);
  document.getElementById('h-pto').textContent = pto_H.toFixed(1);
  const adv = ((pto_H - rm_H) / Math.max(rm_H, 0.01)) * 100;
  document.getElementById('h-adv').textContent = (adv >= 0 ? '+' : '') + adv.toFixed(0) + '%';
}
['h-range','h-beta'].forEach(id => {
  document.getElementById(id).addEventListener('input', drawHorizon);
});
window.addEventListener('resize', () => { drawHorizon(); });
setTimeout(drawHorizon, 60);
</script>
</body>
</html>
"""


@router.get("/pto", response_class=HTMLResponse)
async def pto_page() -> str:
    return _PAGE
