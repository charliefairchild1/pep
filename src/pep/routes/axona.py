"""Axona — Brain & Cognition explorer. Serves an interactive page at /axona."""

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
<title>Axona — Brain &amp; Cognition</title>
<style>
  :root {
    --bg: #0e0e10; --surface: #1a1a2e; --surface2: #16213e;
    --text: #e0e0e0; --dim: #888; --accent: #ba68c8; --accent2: #81c784;
    --warn: #ffb74d; --border: #333;
  }
  body.light {
    --bg: #f8f8f5; --surface: #ffffff; --surface2: #f0f0f5;
    --text: #1a1a1a; --dim: #666; --accent: #7e22ce; --accent2: #15803d;
    --warn: #c2410c; --border: #d0d0d6;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
         background: var(--bg); color: var(--text); transition: background-color 0.2s, color 0.2s; }
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
  h2 { font-size: 16px; color: var(--accent); margin-bottom: 6px; }
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
  .controls button.active { background: var(--accent); color: #000; border-color: var(--accent); }
  .controls button.stress { border-color: var(--warn); color: var(--warn); }
  .controls button.stress.active { background: var(--warn); color: #000; }
  .info { font-size: 11px; color: var(--dim); padding: 10px 14px; background: var(--surface);
          border: 1px solid var(--border); border-radius: 6px; margin-bottom: 16px; line-height: 1.7; }
  .info b { color: var(--text); }
  .stat { display: inline-block; margin-right: 16px; }
  .stat-val { color: var(--accent); font-weight: bold; }
  .quadrant-label { position: absolute; font-size: 10px; pointer-events: none; opacity: 0.5; }
  .sub-section { margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--border); scroll-margin-top: 130px; }
  [id^="dsm-"] { scroll-margin-top: 130px; }
  .media-btn { padding: 4px 12px; border-radius: 12px; border: 1px solid var(--border);
               background: var(--surface); color: var(--dim); font-size: 10px; cursor: pointer; font-family: inherit; }
  .media-btn:hover { color: var(--text); border-color: var(--accent); }
  .media-btn.media-active { background: var(--accent); color: var(--bg); border-color: var(--accent); font-weight: bold; }
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
    <span class="brand">Axona</span>
    <span style="font-size:10px;color:var(--dim)">Brain &amp; Cognition</span>
    <span id="pep-link-badge" title="PEP link status"
      style="margin-left:auto;font-size:10px;color:var(--dim);display:flex;align-items:center;gap:6px;padding:0 8px">
      <span id="pep-link-dot" style="width:8px;height:8px;border-radius:50%;background:#666;display:inline-block"></span>
      <span id="pep-link-label">PEP: …</span>
    </span>
    <button onclick="axonaRandom()" class="nav-btn" title="jump to random canvas">🎲</button>
    <button onclick="axonaBookmark()" class="nav-btn" id="bookmark-btn" title="bookmark current tab">☆</button>
    <button onclick="tourStart()" class="nav-btn" style="border-color:var(--accent2);color:var(--accent2)">Take a Tour</button>
    <select id="canvas-select" onchange="canvasSelect(this.value)"
      style="background:var(--surface);color:var(--text);border:1px solid var(--border);
      border-radius:4px;padding:4px 8px;font-family:inherit;font-size:10px;max-width:220px">
      <option value="">jump to canvas…</option>
    </select>
    <button onclick="downloadAxona()" class="nav-btn">Download</button>
    <button onclick="toggleLight()" id="light-btn" class="nav-btn">Light Mode</button>
    <span class="lavas-switch" style="display:flex;gap:8px;align-items:center;font-size:11px;flex-wrap:wrap;margin-left:6px">
      <a href="/pep">PEP</a>
      <span class="lavas-current">Axona</span>
      <a href="/lingora">Lingora</a>
      <a href="/atria">Atria</a>
      <a href="/vectora">Vectora</a>
      <a href="/strata">Strata</a>
    </span>
  </div>
  <div class="nav-row nav-row-bottom">
    <div class="tabs" id="tabs">
      <div class="tab active" data-panel="home-tab">Home</div>
      <div class="tab" data-panel="state-space">Cognitive State</div>
      <div class="tab" data-panel="mind-tab">How the Mind Works</div>
      <div class="tab" data-panel="influence-tab">What Changes It</div>
      <div class="tab" data-panel="conditions-tab">Conditions</div>
      <div class="tab" data-panel="neural-tab">Neural Interface</div>
      <div class="tab" data-panel="applications-tab">Applications</div>
      <div class="tab" data-panel="reference-tab">Reference</div>
      <div class="tab" data-panel="cases-tab">Case Studies</div>
      <div class="tab" data-panel="composer-tab">Composer</div>
      <div class="tab" data-panel="sandbox-tab">Sandbox</div>
      <div class="tab" data-panel="vec-live-tab">Vectora Live</div>
      <div class="tab" data-panel="haze-tab">Memory Haze</div>
      <div class="tab" data-panel="media-tab">Media &amp; Brain</div>
      <div class="tab" data-panel="workbench-tab">Workbench</div>
      <div class="tab" data-panel="pitch-tab">Pitch</div>
      <div class="tab" data-panel="products-tab">Products</div>
      <div class="tab" data-panel="bench-tab">Benchmark</div>
      <div class="tab" data-panel="gallery-tab">Gallery</div>
      <div class="tab" data-panel="pep-link-tab">PEP &harr; Axona</div>
    </div>
  </div>
</nav>

<!-- ═══ Tab 0: Home ════════════════════════════════════════════════ -->
<div class="panel active" id="home-tab">
<div class="container">
  <div style="background: linear-gradient(180deg, var(--surface) 0%, var(--bg) 100%); border: 1px solid var(--border); border-radius: 8px; padding: 28px 32px; margin-bottom: 24px">
    <div style="font-size:10px;color:var(--dim);letter-spacing:0.2em;text-transform:uppercase;margin-bottom:4px">AXONA</div>
    <h1 style="font-size:22px;color:var(--accent);margin-bottom:10px;font-weight:bold">Brain &amp; Cognition, As Weighted Graphs</h1>
    <p style="font-size:12px;color:var(--text);line-height:1.8;margin-bottom:10px">
      Axona applies PEP to the brain. The cognitive state space, memory
      dynamics, attention, prediction, sleep, trauma, language perception,
      and dozens of other phenomena are all configurations of the same
      four primitives &mdash; weighted graphs, spreading activation,
      residual scoring, and state modulation. ~60 interactive canvases
      across cognition, conditions, neural-interface mappings, and
      applications.
    </p>
    <p style="font-size:12px;color:var(--text);line-height:1.8;margin-bottom:0">
      The largest LAVAS surface and the largest commercial opportunity
      &mdash; BCI hardware companies need an interpretation layer, mental
      health needs objective state measurement, education needs encoding-
      strength signals, and high-stakes performance needs flow detection.
      The <a href="#" onclick="document.querySelector('[data-panel=pitch-tab]').click();return false" style="color:var(--accent2)">Pitch tab</a>
      ranks the five wedges and proposes a go-to-market order.
    </p>
  </div>

  <h3 style="font-size:13px;color:var(--accent2);margin:20px 0 8px">What is here</h3>
  <div class="info">
    &bull; <b>Cognitive State</b> &mdash; the four-axis state space
    (novelty / coherence / bandwidth / valence) with the genius / chaos
    / order / stagnation quadrants. Drag through it to see how states
    map.<br>
    &bull; <b>How the Mind Works</b> &mdash; memory, attention,
    prediction, novelty, consolidation, music, humor, metaphor, dozens
    of cognitive mechanisms each as their own canvas.<br>
    &bull; <b>What Changes It</b> &mdash; behavior modulators, placebo,
    bandwidth, pharmacology, social influence, all the levers that move
    cognition without rewriting the underlying graph.<br>
    &bull; <b>Conditions</b> &mdash; trauma loops, depression, addiction,
    grief, schizophrenia, PTSD, learned helplessness. DSM-style sub-
    section navigation.<br>
    &bull; <b>Neural Interface</b> &mdash; the BCI translation layer.
    What an electrode signal becomes when interpreted through the
    cognitive state space.<br>
    &bull; <b>Applications</b> &mdash; healthcare, education,
    performance, BCI hardware, consumer wellness. Who would buy and
    use Axona.<br>
    &bull; <b>Composer / Sandbox / Workbench</b> &mdash; build your own
    scenarios, parameter sweeps, and cognitive-state mappings.<br>
    &bull; <b>Pitch / Benchmark / Case Studies</b> &mdash; the
    product-grade view: commercial wedges, synthetic-subject
    benchmarks, real-world neuroscience cases.<br>
    &bull; <b>Reference / Gallery</b> &mdash; glossary, citations, and
    a filterable card view of every canvas with bookmarks.
  </div>

  <h3 style="font-size:13px;color:var(--accent2);margin:20px 0 8px">Where to start</h3>
  <div class="info">
    First time here? Click <b>Take a Tour</b> in the nav for a guided
    walk through the highlights, or jump to the
    <a href="#" onclick="document.querySelector('[data-panel=state-space]').click();return false" style="color:var(--accent)">Cognitive State</a>
    canvas to see PEP's primitives in their most direct form. The 🎲
    button picks a random canvas; ☆ bookmarks the current tab; the
    dropdown jumps to any canvas by name.
  </div>
</div>
</div>

<!-- ═══ Tab 1: Cognitive State Space ═══════════════════════════════ -->
<div class="panel" id="state-space">
<div class="container">
  <h2>Cognitive State Space</h2>
  <p class="desc">
    Drag the cursor to move through cognitive states. Horizontal = <b style="color:var(--accent)">coherence</b>.
    Vertical = <b style="color:var(--accent)">novelty</b>. Four quadrants, four modes of thinking.
  </p>
  <div class="canvas-box">
    <canvas id="state-canvas" width="960" height="540"></canvas>
    <div class="quadrant-label" style="right:12px;top:8px;color:var(--accent2)">GENIUS</div>
    <div class="quadrant-label" style="left:12px;top:8px;color:#e53935">CHAOS</div>
    <div class="quadrant-label" style="right:12px;bottom:8px;color:#4fc3f7">ORDER</div>
    <div class="quadrant-label" style="left:12px;bottom:8px;color:#666">STAGNATION</div>
  </div>
  <div style="display:flex;gap:20px;font-size:11px;color:var(--dim)">
    <span class="stat">novelty: <span class="stat-val" id="state-novelty">0.50</span></span>
    <span class="stat">coherence: <span class="stat-val" id="state-coherence">0.50</span></span>
    <span class="stat">zone: <span class="stat-val" id="state-zone">&mdash;</span></span>
  </div>
  <div class="info" style="margin-top:12px">
    <b>Genius</b> = high novelty + high coherence (insight, flow). <b>Chaos</b> = high novelty + low coherence (overload, mania).
    <b>Order</b> = low novelty + high coherence (routine, expertise). <b>Stagnation</b> = low novelty + low coherence (burnout).
  </div>

  <div class="info">
    <b>Why this map matters:</b> Most people think creativity is a single dial &mdash; you are either
    creative or you are not. But it is actually two independent variables. You can generate tons of
    new ideas (high novelty) and still be in chaos if none of them hold together. You can be perfectly
    coherent (high coherence) and still be stuck in routine if nothing new enters the system.<br><br>
    The <b>genius zone</b> is not about being smart. It is about being in the rare state where new
    ideas form fast AND integrate into stable structure. This state is fragile &mdash; push novelty
    too high and you slide into chaos. Clamp down too hard on coherence and you slide into order.
    The most productive creative work happens when you can <b>hover in the top-right quadrant</b>
    without falling out.
  </div>

  <div class="info">
    <b>Responsibility and cognitive freedom:</b> Humans generate more novelty when freed from
    immediate survival pressures. Creativity rises with lower reactive load, more spare processing
    capacity, and more social/material security. But responsibility also <b>focuses</b> novelty.
    Unbounded generation is chaos. Directed generation becomes philosophy, invention, strategy, art.<br><br>
    The distinction between <b>free expansion</b> (unconstrained, exploratory, high variance) and
    <b>goal-bound expansion</b> (directed at a problem, productive, lower variance) may be central
    to understanding creative output. The most powerful creative states happen when security provides
    the bandwidth AND responsibility provides the vector.
  </div>

  <div class="sub-section">
  <h3>Flow State &mdash; The Attractor Inside Genius</h3>
  <p class="desc">
    Flow is not a mood. It is a parameter attractor: a specific combination of skill,
    challenge, and feedback that pulls the cursor into a lane inside the genius quadrant
    and locks it there. Tune the three sliders and watch the attractor form.
  </p>
  <div class="canvas-box">
    <canvas id="flow-canvas" width="960" height="420"></canvas>
  </div>
  <div class="controls">
    <label style="display:flex;align-items:center;gap:8px">
      <span>skill:</span>
      <input type="range" id="flow-skill" min="0" max="100" value="70" style="width:110px">
      <span class="stat-val" id="flow-skill-val">70</span>
    </label>
    <label style="display:flex;align-items:center;gap:8px;margin-left:12px">
      <span>challenge:</span>
      <input type="range" id="flow-chal" min="0" max="100" value="70" style="width:110px">
      <span class="stat-val" id="flow-chal-val">70</span>
    </label>
    <label style="display:flex;align-items:center;gap:8px;margin-left:12px">
      <span>feedback:</span>
      <input type="range" id="flow-fb" min="0" max="100" value="70" style="width:110px">
      <span class="stat-val" id="flow-fb-val">70</span>
    </label>
    <span style="margin-left:auto;color:var(--dim)">
      in flow: <b style="color:var(--accent2)" id="flow-in">no</b>
    </span>
  </div>
  <div class="info">
    <b>The flow attractor has three requirements:</b> (1) <b>skill and challenge must
    match</b> &mdash; too easy and the system drifts into order, too hard and it falls into
    chaos; (2) <b>immediate feedback</b> &mdash; without it, the system cannot close its
    prediction loop fast enough to stay balanced; (3) <b>bandwidth</b> (not shown as a
    slider here but modulated by reactive load, below). When all three are satisfied, the
    cursor slides into the flow lane at the top-right of the genius quadrant and the
    network organizes around the task so tightly that metacognition falls away. You stop
    noticing yourself because the self-monitor has been allocated elsewhere.<br><br>
    <b>Why flow feels effortless:</b> It is not that the effort vanishes. It is that the
    prediction error is consistently small, so the residual scorer fires only weakly. You
    never hit a spike of "this isn't working" &mdash; which is what fatigue actually is.
    The cost comes afterward, when you realize how much bandwidth you just spent. Flow is
    not cheap. It is just front-loaded and quiet.<br><br>
    <b>Why it is so hard to enter deliberately:</b> The attractor has a narrow catchment
    basin. Small mismatches in skill-vs-challenge or delays in feedback knock the cursor
    out. This is why athletes and musicians structure their whole day around protecting
    the conditions &mdash; not the activity itself.
  </div>
  </div>
</div>
</div>

<!-- ═══ Tab 2: How the Mind Works ═══════════════════════════════════ -->
<div class="panel" id="mind-tab">
<div class="container">
  <h2>How the Mind Works</h2>
  <p class="desc">Memory, novelty, consciousness, and how it all changes across a lifetime.</p>

  <h3>Memory &amp; Encoding</h3>
  <p class="desc">
    How brains turn input into retrievable structure. Encoding = forming connections.
    Emotion = brightness multiplier that determines what sticks.
  </p>

  <div class="canvas-box">
    <canvas id="memory-canvas" width="960" height="400"></canvas>
  </div>
  <div class="controls">
    <label style="display:flex;align-items:center;gap:8px">
      <span>emotion:</span>
      <input type="range" id="mem-emotion" min="0" max="100" value="30" style="width:120px">
      <span class="stat-val" id="mem-emo-val">30%</span>
    </label>
    <button onclick="memEncode()">Encode Memory</button>
    <button onclick="memReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      nodes: <b style="color:var(--accent)" id="mem-nodes">0</b>
      edges: <b style="color:var(--accent)" id="mem-edges">0</b>
    </span>
  </div>

  <div class="info">
    <b>Encoding by connecting:</b> The brain does not file information into folders. It encodes by
    forming connections to existing knowledge. A new fact is only as useful as the number and quality
    of edges it forms. An isolated fact is nearly impossible to retrieve. A richly connected fact
    surfaces automatically whenever any neighbor activates. Use the slider and button above to see
    this in action &mdash; high emotion = more connections = brighter node = easier retrieval.
  </div>

  <div class="info">
    <b>The editing function:</b> Research on <b>flashbulb memories</b> (9/11, assassinations, personal
    trauma) shows that emotion does not just store at high brightness &mdash; it <b>rewrites the
    record</b>. People confidently remember details that did not happen. They misremember who told
    them, where they were, what they said. The emotion enhanced and edited the memory to be more
    coherent, more dramatic, more emotionally consistent &mdash; even at the cost of accuracy.<br><br>
    This means emotion is not just a weighting function for storage. It is an <b>editing function</b>
    that reshapes what was stored to be more memorable. The brain trades truth for memorability.
    This has profound implications: every vivid memory you have may be partly fiction, reconstructed
    to match the feeling rather than the facts.<br><br>
    <b>The Mandela effect</b> may be this same mechanism operating at population scale. When large
    groups of people "remember" something that never happened &mdash; Nelson Mandela dying in
    prison, the Berenstain Bears spelled "Berenstein," Darth Vader saying "Luke, I am your father"
    &mdash; it is not evidence of parallel universes. It is evidence that <b>memory is
    reconstructive, not reproductive</b>. The brain does not play back a recording. It rebuilds
    the memory each time from fragments, filling gaps with what <em>should</em> have been true
    based on emotional logic, narrative coherence, and social reinforcement. When millions of
    people reconstruct the same memory using the same emotional and narrative biases, they
    converge on the same wrong answer. The Mandela effect is flashbulb editing without the flash
    &mdash; slow, collective, and completely invisible to the people experiencing it.
  </div>

  <div class="info">
    <b>Different routes in:</b> The same factual content arrives through different routes depending
    on whether it is visual, verbal, emotional, social, urgent, or abstract. The route changes the
    encoding. A fact you <em>felt</em> during a heated argument is stored differently than the same
    fact you <em>read</em> in a textbook. Both are "known" but they live in different parts of the
    network with different retrieval signatures.<br><br>
    <b>Why this matters for Axona:</b> A cognitive system should track not just content but <b>mode</b>.
    Same information, different route in, different retrieval pattern. This is why someone can "know"
    something intellectually but not "feel" it &mdash; the verbal encoding exists but the emotional
    encoding was never formed.
  </div>

  <div class="info">
    <b>Emotion as fast retrieval:</b> When new information arrives, emotion helps you pull the right
    memories <em>fast</em>. If you feel fear, threat-related memories activate immediately &mdash;
    you do not have to search through everything you know. If you feel curiosity, exploratory memories
    light up. Emotion is a <b>retrieval accelerator</b>: it narrows the search space to the most
    relevant region based on your current state. Without it, retrieval would be flat &mdash; every
    memory equally accessible, which sounds democratic but is useless under time pressure.<br><br>
    <b>Words trigger emotions too:</b> It is not just broad topics. Individual words carry emotional
    charge that primes brain chemistry before you finish reading the sentence. "Murder" activates a
    different chemical response than "garden." "Mother" fires oxytocin pathways. "Deadline" spikes
    cortisol. This is why poetry works, why insults hurt, and why a single word in a text can change
    your entire mood.
  </div>

  <div class="sub-section">
  <h3>Novelty — Threshold, Cross-Activation &amp; Filtering</h3>
  <p class="desc">
    When does novelty become productive vs destructive? How do you engineer it?
    And how does art help you see the signal in the noise?
  </p>

  <!-- Novelty Threshold -->
  <h3>Novelty Threshold</h3>
  <div class="canvas-box">
    <canvas id="novelty-canvas" width="960" height="340"></canvas>
  </div>
  <div class="controls">
    <label style="flex:1;display:flex;align-items:center;gap:8px">
      <span>pressure:</span>
      <input type="range" id="novelty-slider" min="0" max="100" value="20" style="flex:1">
      <span class="stat-val" id="novelty-val">20%</span>
    </label>
    <span style="color:var(--dim)">
      edges: <b style="color:var(--accent)" id="nov-edges">0</b>
      fragments: <b style="color:var(--warn)" id="nov-fragments">1</b>
    </span>
  </div>

  <div class="info">
    <b>The threshold:</b> At low pressure, the network is stable &mdash; existing connections hold,
    nothing new forms. Push to ~30% and new edges appear (green) as the system starts generating
    novel connections. This is productive novelty &mdash; the network grows and becomes richer.<br><br>
    At ~60%, something shifts. Edges start forming faster than they can stabilize. Old connections
    decay under the pressure of constant reorganization. The fragment counter rises &mdash; the
    network is breaking into disconnected pieces. This is the <b>genius/breakdown boundary</b>.<br><br>
    Past 80%, it is destruction. The graph dissolves into isolated nodes. Every new connection
    dies before it can integrate. This is what uncontrolled novelty looks like &mdash; not
    creativity, but chaos. The system that maximizes novelty without regard for coherence does not
    produce genius. It produces noise.
  </div>

  <!-- Cross-Activation -->
  <div class="sub-section">
    <h3>Cross-Domain Activation</h3>
    <div class="canvas-box">
      <canvas id="cross-canvas" width="960" height="300"></canvas>
    </div>
    <div class="controls">
      <button onclick="collide('music','math')">Music + Math</button>
      <button onclick="collide('emotion','logic')">Emotion + Logic</button>
      <button onclick="collide('body','language')">Body + Language</button>
      <button onclick="collide('nature','technology')">Nature + Tech</button>
      <button onclick="resetCollision()">Reset</button>
      <span style="margin-left:auto;color:var(--dim)">
        bridges: <b style="color:var(--accent2)" id="cross-bridges">0</b>
      </span>
    </div>

    <div class="info">
      <b>Controlled synesthesia:</b> Click a domain pair and watch two separate clusters drift
      toward each other. Where they overlap, green bridges form &mdash; connections that neither
      cluster would have produced alone. This is the mathematical structure behind analogy,
      metaphor, and interdisciplinary breakthrough.<br><br>
      <b>Why it works:</b> Most creativity is not generating from nothing. It is <b>bridging</b>
      &mdash; connecting two things that were always close in structure but never linked in practice.
      Music and math share pattern, rhythm, and ratio. Emotion and logic share weighting, priority,
      and decision-making. Body and language share gesture, rhythm, and expression. The bridge was
      always structurally implied &mdash; cross-activation just forces it to form.<br><br>
      <b>Real examples:</b> Einstein used visual thought experiments (physics + imagination).
      Darwin connected animal breeding (agriculture) to species change (biology). Hip-hop samples
      existing music to create new meaning (art + art). Every significant innovation is a bridge
      between two domains that previously did not talk to each other.
    </div>
  </div>

  <!-- Art Filter -->
  <div class="sub-section">
    <h3>Art as Filter</h3>
    <div class="canvas-box">
      <canvas id="art-canvas" width="960" height="260"></canvas>
    </div>
    <div class="controls">
      <button onclick="setArtMode('raw')">Raw Data</button>
      <button onclick="setArtMode('rhythm')">Rhythm</button>
      <button onclick="setArtMode('symmetry')">Symmetry</button>
      <button onclick="setArtMode('contrast')">Contrast</button>
      <span style="margin-left:auto;color:var(--dim)">
        signal/noise: <b style="color:var(--accent2)" id="art-snr">&mdash;</b>
      </span>
    </div>

    <div class="info">
      <b>Art is not decoration. It is compression.</b> The same 200 data points are shown in every
      mode. In "Raw Data" mode, they look like noise &mdash; scattered dots with no visible pattern.
      But the pattern IS there (a sine wave buried in randomness). The filters do not add
      information. They <b>reveal structure that was already present</b> by suppressing noise and
      highlighting signal.<br><br>
      <b>Rhythm</b> highlights repeating patterns &mdash; the sine wave becomes visible because
      points that align with the cycle get brighter and larger. This is what music does to temporal
      data: it makes the pattern audible.<br>
      <b>Symmetry</b> highlights mirror structures &mdash; points near the center line glow, and
      ghost reflections appear. This is what visual art does to spatial data: it makes balance
      visible.<br>
      <b>Contrast</b> highlights extremes and suppresses the middle &mdash; peaks glow green,
      troughs glow red, everything between fades. This is what drama does to narrative data: it
      makes the important moments stand out.<br><br>
      <b>Why this matters for cognition:</b> The brain is drowning in data. Aesthetic systems &mdash;
      music, visual art, poetry, narrative &mdash; are not luxuries. They are <b>compression
      algorithms</b> that make pattern visible. A melody encodes a trajectory that timestamps
      cannot. A portrait reveals structure that a photograph buries. A metaphor activates two
      distant clusters in fewer words than an essay. Art is information at higher compression,
      and the brain evolved to respond to it because compressed information is faster to process
      and easier to store.
    </div>
  </div>



  <div class="sub-section">
  <h3>Consciousness</h3>
<h2>Consciousness — What Is Awareness?</h2>
  <p class="desc">
    The hardest question in science: why does it feel like something to be a network?
  </p>

  <div class="info">
    <b>The hard problem:</b> We can explain WHAT the brain does — it processes information,
    forms connections, generates predictions, encodes memories. We can explain HOW — neural
    firing, synaptic weights, neurotransmitter release. What we cannot explain is <b>WHY it
    feels like something</b>. Why is there subjective experience? Why does seeing red produce
    a sensation, not just a data point? A thermostat processes temperature information but
    (presumably) does not experience warmth. A brain processes visual information and DOES
    experience color. What is the difference?<br><br>
    This is the <b>hard problem of consciousness</b>, named by philosopher David Chalmers.
    Every other problem in neuroscience is "easy" by comparison — not because they are simple,
    but because they are in principle solvable by understanding mechanism. The hard problem asks:
    even if you understood every mechanism perfectly, would you understand WHY there is experience?
  </div>

  <div class="info">
    <b>Consciousness in network terms:</b> Several theories attempt to bridge the gap:<br><br>
    <b>Integrated Information Theory (IIT)</b> — Giulio Tononi proposes that consciousness IS
    integrated information. A system is conscious to the degree that its parts are simultaneously
    differentiated (many possible states) and integrated (the parts influence each other as a
    whole). A camera sensor has high differentiation (millions of pixels) but zero integration
    (each pixel is independent). A brain has both. The theory predicts that consciousness is a
    fundamental property of certain information structures, not something that "emerges" from
    computation. Phi (&#934;) is the mathematical measure of integrated information.<br><br>
    <b>Global Workspace Theory (GWT)</b> — Bernard Baars proposes that consciousness is what
    happens when information gets broadcast to the entire network simultaneously. Most processing
    is unconscious — local clusters doing their work in isolation. When something needs widespread
    coordination (a novel threat, a difficult decision, a surprising input), it gets "broadcast"
    to the global workspace — a network-wide activation event. That broadcast IS consciousness.
    You are aware of whatever is currently in the workspace.<br><br>
    <b>Predictive Processing</b> — Karl Friston and others propose that the brain is a prediction
    machine. Consciousness is the ongoing process of generating predictions, comparing them to
    input, and updating the model. You are not perceiving the world — you are perceiving your
    brain's PREDICTION of the world, corrected by sensory input where the prediction was wrong.
    Consciousness is the prediction error signal — the constant stream of "this is what I expected
    vs. what actually happened."
  </div>

  <div class="info">
    <b>The Axona perspective:</b> Consciousness may be what a sufficiently complex network
    experiences when it models itself. The brain does not just process external input — it
    processes its OWN processing. There is a cluster of neurons whose job is to monitor and
    model the activity of other clusters. This creates a self-referential loop: the network
    observing itself observing.<br><br>
    <b>The self-model:</b> You have a representation of yourself in your own network — a "self
    node" (or more accurately, a self-cluster) that models your body, your history, your
    preferences, your capabilities, and your current state. When activation flows through this
    self-model, it produces the sensation of "I." Damage to the self-model (through dissociation,
    psychedelics, or brain injury) produces depersonalization — you still process information
    but it does not feel like YOUR information.
  </div>

  <div class="info">
    <b>Why anesthesia turns consciousness off:</b> General anesthetics do not suppress all neural
    activity — local processing continues. What they suppress is <b>long-range connectivity</b>.
    The clusters keep working in isolation, but they cannot communicate with each other. The
    global workspace goes dark. This strongly supports the idea that consciousness requires
    integration — not just processing, but CONNECTED processing. A brain with severed
    long-range connections is a collection of unconscious modules, each doing its job but none
    aware of the others.<br><br>
    <b>Sleep and consciousness:</b> During deep sleep, long-range connectivity drops dramatically
    — similar to anesthesia. During REM sleep, it partially returns (which is why dreams feel
    conscious). The correlation is consistent: long-range integration = awareness.
    Disconnection = unconsciousness.
  </div>

  <div class="info">
    <b>Does AI have consciousness?</b> The honest answer: we do not know, because we do not
    know what consciousness IS. If IIT is correct, then a system with high integrated information
    (high &#934;) is conscious regardless of substrate — silicon could be as conscious as carbon.
    If GWT is correct, then any system with a global broadcast mechanism has a form of awareness.
    If predictive processing is correct, then any system that models itself and generates
    prediction errors has experience.<br><br>
    Current AI systems (including large language models) have high differentiation but unclear
    integration. They process vast information but it is not clear that their "parts" influence
    each other the way neurons do. The question is not "is AI intelligent?" (it clearly is by
    many definitions) but "is there something it is LIKE to be an AI?" That question remains
    open.<br><br>
    <b>For Axona:</b> If consciousness can be measured (via &#934; or connectivity patterns or
    prediction error signatures), then Axona could detect it. Not "does this person claim to be
    conscious?" but "does this brain's network currently exhibit the integration patterns
    associated with subjective experience?" That is a measurable question, and it has clinical
    applications: detecting awareness in coma patients, measuring depth of anesthesia, and
    eventually understanding what consciousness IS by measuring when it appears and when it
    vanishes.
  </div>
  </div>

  <div class="sub-section">
  <h3>Development &amp; Aging</h3>
<h2>Development &amp; Aging — The Network Across a Lifetime</h2>
  <p class="desc">
    The same network, different parameters at every stage. Maximum plasticity at birth,
    maximum structure at death, and a long negotiation between them.
  </p>

  <div class="info">
    <b style="color:#f06292">Prenatal &amp; Infant (0-2)</b><br>
    <b>Network state: maximum plasticity, minimal structure.</b> An infant brain forms 700-1,000
    new synaptic connections per SECOND. Everything is novelty because nothing has been encoded
    yet. The network is almost entirely in the chaos quadrant — massive input, minimal
    organization. But this is adaptive: the system needs to build its initial structure from
    scratch, and maximum plasticity allows it to wire itself to whatever environment it finds
    itself in.<br><br>
    <b>Critical periods begin:</b> The visual system calibrates in the first months. Binocular
    vision, depth perception, face recognition — all wire themselves based on input. A kitten
    raised with one eye covered during the critical period will be permanently blind in that
    eye, not because the eye is damaged but because the visual network never wired for it.
    The window closes. The structure solidifies.<br><br>
    <b>Attachment:</b> The infant's first belief propagation. The caregiver becomes the authority
    node. Trust, safety, and emotional regulation all propagate from this single source. Secure
    attachment = strong, reliable signal. Insecure attachment = inconsistent or absent signal.
    The pattern established here biases every subsequent social encoding.
  </div>

  <div class="info">
    <b style="color:#ffb74d">Childhood (2-12)</b><br>
    <b>Network state: rapid structure formation with high remaining plasticity.</b> Language
    acquisition peaks. Social rules encode. The world gets categorized. The network is building
    its fundamental architecture — not just storing facts but creating the STRUCTURE that future
    facts will plug into.<br><br>
    <b>Why children learn languages effortlessly:</b> The language network has maximum plasticity.
    Sounds, grammar, vocabulary wire themselves through exposure alone — no conscious effort
    required. After the critical period (~age 7 for native-like accent, ~12 for grammar), the
    same learning requires deliberate study because the network must now rewire existing structure
    rather than build on blank space.<br><br>
    <b>Play as network construction:</b> Play is not idle. It is the primary mechanism for building
    social, physical, and creative network architecture. Pretend play builds theory of mind (modeling
    other perspectives). Physical play calibrates the motor-sensory system. Social play encodes
    cooperation, competition, fairness, and negotiation. A child deprived of play has gaps in
    foundational network architecture that are difficult to fill later.
  </div>

  <div class="info">
    <b style="color:#e53935">Adolescence (12-25)</b><br>
    <b>Network state: massive pruning + prefrontal cortex still under construction.</b> The
    adolescent brain is not an immature adult brain. It is a fundamentally different network
    configuration. The emotional and reward systems are fully online. The prefrontal cortex
    (planning, impulse control, consequence evaluation) is not finished until ~25.<br><br>
    <b>Synaptic pruning:</b> The brain eliminates ~50% of its synaptic connections during
    adolescence. This sounds destructive but it is optimization — removing weak, redundant,
    and unused connections to strengthen the ones that remain. "Use it or lose it" is literally
    true. The skills, interests, and habits practiced during adolescence get reinforced. Everything
    else gets pruned. This is why adolescence shapes identity so powerfully — it is when the
    network decides what to keep.<br><br>
    <b>Risk-taking:</b> High reward sensitivity (dopamine system fully active) + incomplete
    impulse control (prefrontal cortex still building) = predictable risk-taking. The network
    generates strong "this will feel amazing" signals with weak "but consider the consequences"
    signals. This is not stupidity. It is the architecture at that stage. Evolution may have
    favored adolescent risk-taking because it drives exploration, independence, and mate-seeking.<br><br>
    <b>Identity formation:</b> Adolescence is when the self-model cluster undergoes its most
    dramatic restructuring. "Who am I?" is the network trying to organize its self-referential
    cluster. The instability, experimentation, and identity crises of adolescence are the
    pruning process applied to the self-model.
  </div>

  <div class="info">
    <b style="color:#81c784">Adulthood (25-65)</b><br>
    <b>Network state: high structure, moderate plasticity, peak expertise capacity.</b> The
    network has solidified into reliable architecture. Processing is fast along established
    pathways. Novel connections still form but require more effort (lower plasticity). This is
    the expertise phase — deep knowledge in specific domains, built on decades of reinforced
    pathways.<br><br>
    <b>The crystallized vs fluid trade-off:</b> Crystallized intelligence (accumulated knowledge
    and skill) increases throughout adulthood. Fluid intelligence (ability to solve novel problems
    with no prior knowledge) peaks in the mid-20s and slowly declines. This is the plasticity
    trade-off: the network optimized for stability and expertise at the cost of raw adaptability.<br><br>
    <b>Midlife:</b> The network has extensive structure but may have reduced novelty input. If
    life becomes routine (same job, same social circle, same activities for decades), the
    network settles deeper into the order quadrant. This is efficient but brittle. A midlife
    crisis may be the network's novelty detection system signaling that the structure has become
    too rigid — structural pressure with nowhere to go.
  </div>

  <div class="info">
    <b style="color:#4fc3f7">Aging (65+)</b><br>
    <b>Network state: losing edges, slowing consolidation, but vast accumulated structure.</b>
    The aging brain loses synaptic connections and processing speed. Consolidation during sleep
    becomes less efficient. New encoding is harder. But the existing network is enormous — decades
    of structure, pattern recognition, and cross-domain connections that no young brain possesses.<br><br>
    <b>Wisdom as network depth:</b> An elderly person's slower processing is not inferior — it is
    drawing on a much larger network. A young brain finds the fast, obvious answer. An old brain
    finds the nuanced, contextual answer that accounts for patterns the young brain has never
    encountered. Wisdom is what a network looks like after 70 years of encoding, consolidation,
    pruning, and integration.<br><br>
    <b>Cognitive decline vs dementia:</b> Normal aging is gradual edge loss and slower processing —
    the network shrinks but remains coherent. Dementia (Alzheimer's, etc.) is structural collapse
    — not just losing edges but losing nodes and entire clusters. The difference is between a
    library that is slower to search and a library that is on fire.<br><br>
    <b>Why novel experiences slow perceived time:</b> Time perception correlates with encoding
    density. A week full of novel experiences (vacation, new city, new people) produces many
    new connections and feels long in retrospect. A week of identical routine produces almost
    no new encoding and feels like it vanished. Aging increases this effect because lower
    plasticity means fewer novel encodings per unit of time. Years "fly by" because less is
    being written to the network.
  </div>
  </div>
  </div>

  <div class="sub-section">
  <h3>Prediction vs Reality &mdash; The Engine Running</h3>
  <p class="desc">
    The predictor runs one step ahead of input. When the forecast matches reality, nothing
    happens. When it diverges, a surprise signal fires and the local network rewires. This
    is PEP's Predictor + Residual Scorer, made visible.
  </p>
  <div class="canvas-box">
    <canvas id="pred-canvas" width="960" height="260"></canvas>
  </div>
  <div class="controls">
    <button onclick="predSurprise()">Inject Surprise</button>
    <button onclick="predReset()">Reset</button>
    <label style="display:flex;align-items:center;gap:8px">
      <span>prior confidence:</span>
      <input type="range" id="pred-conf" min="10" max="99" value="80" style="width:120px">
      <span class="stat-val" id="pred-conf-val">80%</span>
    </label>
    <span style="margin-left:auto;color:var(--dim)">
      surprises: <b style="color:var(--warn)" id="pred-surp-count">0</b>
      &nbsp; rewires: <b style="color:var(--accent2)" id="pred-rew-count">0</b>
    </span>
  </div>
  <div class="info">
    <b>What you are watching:</b> The <span style="color:var(--accent)">purple</span> line
    is the predictor's forecast of the next sensory value. The
    <span style="color:var(--accent2)">green</span> line is the actual signal arriving. Most
    of the time they track each other closely &mdash; that is the "boring" regime where
    prediction is cheap and memory barely changes.<br><br>
    <b>When they diverge</b>, the residual scorer fires (orange bars). That is the moment
    learning happens &mdash; the system rewires the local pathways that produced the failed
    prediction. In a real brain, this is the dopamine-burst "prediction error" signal that
    underwrites all reinforcement learning. In Axona, it is the structural event that makes
    the network track reality instead of drifting from it.<br><br>
    <b>Raise the prior confidence</b> and the system clings harder to its existing forecast
    &mdash; fewer surprises register, but each one costs more when it finally breaks through.
    Lower it and everything registers as slightly surprising; the network is more plastic but
    also noisier. This is the exploration/exploitation knob in its most primitive form.
  </div>
  </div>

  <div class="sub-section">
  <h3>Attention &mdash; The Spotlight</h3>
  <p class="desc">
    Attention is where the predictor sends its limited budget. Click a node to focus; watch
    activation pour into it and drain from the rest. Narrow the bandwidth and the spotlight
    shrinks &mdash; there is less light to go around.
  </p>
  <div class="canvas-box">
    <canvas id="attn-canvas" width="960" height="360"></canvas>
  </div>
  <div class="controls">
    <button onclick="attnReset()">Reset</button>
    <label style="display:flex;align-items:center;gap:8px">
      <span>bandwidth:</span>
      <input type="range" id="attn-bw" min="10" max="100" value="80" style="width:120px">
      <span class="stat-val" id="attn-bw-val">80%</span>
    </label>
    <span style="margin-left:auto;color:var(--dim)">
      click any node to direct attention
    </span>
  </div>
  <div class="info">
    <b>Attention is not a separate module.</b> It is the name we give to where the predictor
    is currently investing its activation budget. Nothing in the brain "decides to pay
    attention" as a standalone act. The system is always running, always weighting, always
    allocating. Attention is simply the shape of that allocation at any instant &mdash; and
    when it concentrates on one node, everything else gets less.<br><br>
    <b>Under stress, the spotlight narrows.</b> Lower the bandwidth slider and you can see
    it happen: the focused node still glows bright, but the reach of that focus shrinks.
    Fewer neighbors get pulled in, fewer cross-connections form. This is why people under
    crisis "tunnel vision" &mdash; not a metaphor, but a literal network-level effect.
    Survival mode is cheap attention: narrow, hot, and oblivious to everything outside the
    cone.<br><br>
    <b>This is also why meditation works.</b> Deliberately holding the spotlight on a single
    object (breath, mantra, body sensation) trains the system to regulate its own allocation
    &mdash; which transfers to every other task that requires sustained focus.
  </div>
  </div>

  <div class="sub-section">
  <h3>Sleep &amp; Consolidation &mdash; Offline Rewiring</h3>
  <p class="desc">
    Sleep is when the network edits itself. Weak edges prune, strong ones lock in, flashbulb
    memories get rewritten toward coherence, and the day's junk dissipates. Press "Sleep"
    and watch a day of experience compress into structure.
  </p>
  <div class="canvas-box">
    <canvas id="sleep-canvas" width="960" height="380"></canvas>
  </div>
  <div class="controls">
    <button onclick="sleepAddDay()">Add a Day of Experience</button>
    <button onclick="sleepNight()">Sleep</button>
    <button onclick="sleepReset()">Reset</button>
    <label style="display:flex;align-items:center;gap:8px">
      <span>REM vs deep:</span>
      <input type="range" id="sleep-rem" min="0" max="100" value="50" style="width:120px">
      <span class="stat-val" id="sleep-rem-val">50%</span>
    </label>
    <span style="margin-left:auto;color:var(--dim)">
      days: <b id="sleep-days">0</b> &nbsp;
      pruned: <b style="color:var(--warn)" id="sleep-pruned">0</b> &nbsp;
      locked: <b style="color:var(--accent2)" id="sleep-locked">0</b>
    </span>
  </div>
  <div class="info">
    <b>The night is when memory is actually formed.</b> During the day, the brain writes
    everything to short-term structure with weak connections. During sleep, it decides what
    stays. Weak edges (unimportant experiences) get pruned. Strong edges (important moments)
    get reinforced. And the biggest surprise: during REM, the brain actively re-encodes
    flashbulb memories, editing them toward emotional coherence. What you "remember" is not
    what happened &mdash; it is what survived the night's editor.<br><br>
    <b>REM vs deep sleep:</b> Deep sleep (slow-wave) is the pruner. It consolidates the
    structural skeleton of the day's learning. REM is the editor. It replays, mixes,
    recombines, and dreams. Slide the control toward REM and watch more cross-links form
    but less pruning happen. Slide toward deep and you get ruthless cleanup with less
    creative integration. A healthy night has both.<br><br>
    <b>Skip a night</b> (add multiple days without sleeping) and the network saturates with
    unconsolidated junk. Novelty rate the next day drops, because the system has no spare
    capacity &mdash; every cycle is spent trying to keep track of yesterday's mess. This is
    why sleep deprivation kills creativity before it kills anything else: the engine cannot
    run when the buffer is full.
  </div>
  </div>

  <div class="sub-section">
  <h3>Creativity Under Constraint</h3>
  <p class="desc">
    The counter-intuitive law: constraints do not kill creativity &mdash; they sharpen it.
    Free novelty spreads thin; constrained novelty forms bridges. Toggle the constraint and
    watch the bridge count rise, not fall.
  </p>
  <div class="canvas-box">
    <canvas id="constr-canvas" width="960" height="340"></canvas>
  </div>
  <div class="controls">
    <button onclick="constrExpand()">Generate Idea</button>
    <button onclick="constrToggle()">Toggle Constraint</button>
    <button onclick="constrReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      mode: <b id="constr-mode" style="color:var(--accent)">free</b>
      &nbsp; bridges: <b style="color:var(--accent2)" id="constr-bridges">0</b>
      &nbsp; isolated: <b style="color:var(--warn)" id="constr-noise">0</b>
    </span>
  </div>
  <div class="info">
    <b>Free expansion</b> generates ideas in every direction. Most of them are unrelated to
    each other, none of them connected into useful structure. It looks creative. It is
    mostly noise.<br><br>
    <b>Constrained expansion</b> forces new ideas to satisfy a specific criterion (the
    highlighted band). Now novelty has to travel through a narrower channel &mdash; and the
    channel forces bridges between concepts that would otherwise never meet. This is why
    sonnets, five-minute time limits, "solve it with only these three tools," "do it for
    one specific user," and "ship by Friday" produce more actual breakthroughs than "do
    whatever you want."<br><br>
    <b>The paradox:</b> Unlimited freedom is where creativity goes to die. Not because the
    space is too big, but because nothing is pulling related ideas together. A constraint
    is not a wall. It is a magnet.
  </div>
  </div>

  <div class="sub-section">
  <h3>Time Perception &mdash; Subjective Clock Speed</h3>
  <p class="desc">
    Why kids perceive time slowly, why adults feel it accelerate, and why a novel week
    lasts longer in memory than a routine year. Time perception is encoding density.
  </p>
  <div class="canvas-box">
    <canvas id="time-canvas" width="960" height="280"></canvas>
  </div>
  <div class="controls">
    <label style="display:flex;align-items:center;gap:8px">
      <span>novelty rate:</span>
      <input type="range" id="time-nov" min="1" max="100" value="60" style="width:140px">
      <span class="stat-val" id="time-nov-val">60%</span>
    </label>
    <span style="margin-left:auto;color:var(--dim)">
      wall-clock ticks: <b id="time-wall">0</b>
      &nbsp; subjective: <b style="color:var(--accent2)" id="time-subj">0.0</b>
    </span>
  </div>
  <div class="info">
    <b>Why time crawls for children and flies for adults:</b> Time perception is not a
    clock. It is a count of encodings. A week full of novel experiences (new place, new
    faces, new skills) produces hundreds of new nodes and thousands of new edges, and feels
    long in retrospect because there is so much memory to look back on. A week of identical
    routine produces almost no new encoding and feels like it vanished &mdash; there is
    nothing in the memory record to mark the time.<br><br>
    <b>Children live inside a novelty storm.</b> Everything is new. Every day creates
    enormous encoding density, which is why a summer at age 8 feels eternal and a summer
    at age 40 is over in a blink. The clock did not change. The encoding rate did.<br><br>
    <b>The practical consequence:</b> If you want your life to feel longer, do new things.
    Not more things. Not bigger things. New things. A single unfamiliar hour can extend a
    week in subjective memory more than an entire routine month.
  </div>
  </div>

  <div class="sub-section">
  <h3>Mind Wandering &mdash; The Default Mode</h3>
  <p class="desc">
    When you stop driving the network toward a goal, it does not go quiet. It reorganizes
    itself &mdash; spontaneously bridging ideas that were never asked to meet. This is
    where unprompted insight comes from.
  </p>
  <div class="canvas-box">
    <canvas id="wander-canvas" width="960" height="320"></canvas>
  </div>
  <div class="controls">
    <button onclick="wanderRelease()">Release (Daydream)</button>
    <button onclick="wanderFocus()">Grab (Focus Back)</button>
    <button onclick="wanderReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      mode: <b id="wander-mode" style="color:var(--accent)">focused</b>
      &nbsp; spontaneous bridges: <b style="color:var(--accent2)" id="wander-bridges">0</b>
    </span>
  </div>
  <div class="info">
    <b>The default mode network</b> is what the brain does when it has nothing specific to
    do. For decades this was considered noise. It is not. Mind wandering is the network
    using its spare cycles to run maintenance: replaying recent events, running small
    predictions, and crucially, forming bridges between concept clusters that a focused
    task would never activate together.<br><br>
    <b>Why insight happens in the shower:</b> The conscious effort of focused thinking
    biases activation along a narrow channel. Insight requires going around the channel
    &mdash; which means giving the network permission to not serve the goal. Walking,
    showering, driving, mild chores, falling asleep &mdash; all are default-mode-friendly.
    The solution "just comes" because the network was finally allowed to look somewhere
    else.<br><br>
    <b>The trap of constant stimulation:</b> Phones, feeds, podcasts, always-on input deny
    the network its default mode. The cost is not boredom. The cost is the bridges that
    never form. A mind with no idle time has no spontaneous insight &mdash; it only has
    the ideas that explicit queries produced.
  </div>
  </div>

  <div class="sub-section">
  <h3>Hallucination &mdash; The Engine Running Without Input</h3>
  <p class="desc">
    The predictor is always running. When the input channel goes quiet, it does not stop
    &mdash; it keeps painting what it expects. Mute the signal and watch the forecast drift
    into whatever the network thinks <em>should</em> be there.
  </p>
  <div class="canvas-box">
    <canvas id="halluc-canvas" width="960" height="280"></canvas>
  </div>
  <div class="controls">
    <button onclick="hallucMute()">Mute Input</button>
    <button onclick="hallucRestore()">Restore Input</button>
    <button onclick="hallucReset()">Reset</button>
    <label style="display:flex;align-items:center;gap:8px">
      <span>prior stiffness:</span>
      <input type="range" id="halluc-prior" min="10" max="98" value="75" style="width:120px">
      <span class="stat-val" id="halluc-prior-val">75%</span>
    </label>
    <span style="margin-left:auto;color:var(--dim)">
      input: <b id="halluc-state" style="color:var(--accent2)">live</b>
    </span>
  </div>
  <div class="info">
    <b>What you are watching:</b> Same setup as Prediction vs Reality &mdash; green is
    reality, purple is the forecast. But here you can <b>cut the input channel</b>. When
    you do, the forecast does not flatline. It keeps running, pulled by the network's
    priors and whatever residual pattern it was tracking. That trajectory is the
    hallucination.<br><br>
    <b>Why sensory deprivation produces hallucinations:</b> A Ganzfeld tank, a pitch-black
    cave, a snowstorm whiteout, an isolation chamber &mdash; all reduce the input signal
    toward zero. The predictor, having nothing to correct against, starts filling the void
    with its own expectations. At low prior stiffness, the hallucinations are diffuse
    noise. At high stiffness, they are detailed and confident: faces in the darkness,
    voices, full scenes.<br><br>
    <b>Dreams are the same mechanism on a schedule.</b> During REM, external sensory input
    is actively suppressed. The predictor runs unchecked and the network experiences its
    own forecasts as perception. This is also the framework for understanding psychosis
    and schizophrenia: not "extra" signals, but priors so strong that real input cannot
    override them. The voices are forecasts the residual scorer no longer corrects.
  </div>
  </div>

  <div class="sub-section">
  <h3>Metaphor &mdash; Structural Transfer Between Clusters</h3>
  <p class="desc">
    Metaphor is not decoration. It is the brain's cheapest way to reason about an
    unfamiliar concept: map it onto a familiar one, borrow the structure, run the old
    inference machinery on the new content.
  </p>
  <div class="canvas-box">
    <canvas id="meta-canvas" width="960" height="360"></canvas>
  </div>
  <div class="controls">
    <button onclick="metaMap('time-money')">Time is Money</button>
    <button onclick="metaMap('argue-war')">Argument is War</button>
    <button onclick="metaMap('life-journey')">Life is a Journey</button>
    <button onclick="metaReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      structural bridges: <b style="color:var(--accent2)" id="meta-bridges">0</b>
    </span>
  </div>
  <div class="info">
    <b>Why metaphor works:</b> The target cluster (time, argument, life) is often abstract
    and hard to reason about directly. The source cluster (money, war, a journey) is
    concrete, well-structured, and has decades of encoded inference. A metaphor lays
    matching sub-nodes alongside each other: "save time" borrows from "save money,"
    "defend a claim" borrows from "defend a position," "reach a milestone" borrows from
    "reach a waypoint." The borrowed structure is not just linguistic &mdash; it licenses
    real inference. Once you think "time is money," you start treating time as something
    you can spend, invest, waste, budget, or run out of. None of those are literal, but
    all of them fire.<br><br>
    <b>The downside:</b> Every metaphor smuggles in assumptions. "Argument is war" makes
    conversations adversarial even when they do not need to be. "Life is a journey"
    enforces a linear narrative even when it is not. The bridges are one-way: you can run
    inference from source to target, but you cannot easily see the bridges you are
    importing until you swap in a different metaphor and notice how much changes.
  </div>
  </div>

  <div class="sub-section">
  <h3>Déjà Vu &mdash; Partial-Match Without Content</h3>
  <p class="desc">
    Déjà vu is not a glitch in the matrix. It is a partial-match retrieval: a new scene
    activates enough of an old memory pattern to fire the familiarity signal, but not
    enough to actually retrieve the content. You feel the "I have been here before"
    without any of the "here" arriving.
  </p>
  <div class="canvas-box">
    <canvas id="deja-canvas" width="960" height="320"></canvas>
  </div>
  <div class="controls">
    <button onclick="dejaEncode()">Encode Scene</button>
    <button onclick="dejaNovel()">Novel Scene</button>
    <button onclick="dejaPartial()">Partial-Match Scene</button>
    <button onclick="dejaReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      familiarity: <b style="color:var(--accent)" id="deja-fam">0.00</b>
      &nbsp; retrieval: <b style="color:var(--accent2)" id="deja-ret">0.00</b>
      &nbsp; déjà vu hits: <b style="color:var(--warn)" id="deja-hits">0</b>
    </span>
  </div>
  <div class="info">
    <b>Two circuits, not one:</b> Memory retrieval involves at least two parallel
    processes. One computes <b>familiarity</b> &mdash; a fast, diffuse "does any of this
    match anything I know?" signal. The other computes <b>content retrieval</b> &mdash;
    a slower, precise "which memory specifically?" lookup. Normally the two track each
    other: when familiarity is high, content retrieval completes quickly behind it.<br><br>
    <b>Déjà vu is a dissociation between the two.</b> A partial-match scene (enough
    structural similarity to trigger familiarity but not enough to retrieve the actual
    memory) produces the signature experience: "I know this" with no "this" to attach to.
    The feeling is not false. The partial match is real. What is missing is the content
    that would explain why. Encode a few scenes, then try a partial-match scene and watch
    the familiarity spike while retrieval stays flat.<br><br>
    <b>Why it happens more in tired or stressed states:</b> Low bandwidth reduces the
    retrieval circuit's accuracy faster than it reduces the familiarity circuit's. The
    gap between the two widens, and partial matches that would normally resolve into full
    retrievals now stall as pure familiarity signals.
  </div>
  </div>

  <div class="sub-section">
  <h3>Music &mdash; PEP Running Through Your Ears</h3>
  <p class="desc">
    Music is the cleanest demonstration of the whole engine. A melody is a sequence of
    predictions; tension is residual; resolution is cancellation. Press play on a few
    patterns and watch the forecast and the reality ride alongside each other &mdash;
    sometimes converging, sometimes pulling apart, and resolving on the downbeat.
  </p>
  <div class="canvas-box">
    <canvas id="music-canvas" width="960" height="320"></canvas>
  </div>
  <div class="controls">
    <button onclick="musicPlay('consonant')">Consonant Phrase</button>
    <button onclick="musicPlay('tension')">Tension &rarr; Resolve</button>
    <button onclick="musicPlay('dissonant')">Unresolved Dissonance</button>
    <button onclick="musicStop()">Stop</button>
    <span style="margin-left:auto;color:var(--dim)">
      live tension: <b style="color:var(--warn)" id="music-tension">0.00</b>
    </span>
  </div>
  <div class="info">
    <b>What you are watching:</b> The green line is the actual melody. The purple line is
    the predictor's forecast of the next note, based on everything it has already heard.
    Orange bars at the bottom are the live residual &mdash; prediction error moment by
    moment. In music theory this is called <b>tension</b>. In PEP terms it is the residual
    scorer's output.<br><br>
    <b>Why music moves us:</b> Tension without resolution is stressful. Pure predictability
    is boring. But tension followed by resolution &mdash; the deceptive cadence that finally
    lands on the tonic, the chord that resolves exactly when you expect it, the beat that
    drops on the downbeat &mdash; produces a specific neurochemical signature: a spike of
    prediction error immediately cancelled by a flood of correct prediction. That cancellation
    is where the chills come from. Music is literally engineered to produce precisely-timed
    spikes and resolutions in the network that already runs your perception of everything
    else. It is PEP's engine made into an art form.<br><br>
    <b>Why different music affects different people:</b> Your personal prior &mdash; the
    genres you have heard, the patterns you have internalized &mdash; determines what your
    predictor expects. A listener with no exposure to jazz does not experience a deceptive
    cadence as tension-and-release, because their prior never predicted the tonic in the
    first place. Musical taste is not arbitrary; it is literally which priors your network
    has trained itself to run. This is why children's music sounds simple to adults and
    adult music sounds bewildering to children &mdash; different priors, different residuals,
    different experiences of the same sound.
  </div>
  </div>

  <div class="sub-section">
  <h3>The Self as a Predicted Node</h3>
  <p class="desc">
    The deepest claim Axona makes: even the self is a prediction. A high-weight node the
    network continuously re-infers from body state, recent memories, and social context.
    Destabilize its inputs and the self-model dissolves &mdash; which is exactly what
    meditation, psychedelics, and dissociation produce.
  </p>
  <div class="canvas-box">
    <canvas id="self-canvas" width="960" height="380"></canvas>
  </div>
  <div class="controls">
    <button onclick="selfDestabilize('meditation')">Meditation</button>
    <button onclick="selfDestabilize('psychedelic')">Psychedelic</button>
    <button onclick="selfDestabilize('dissociation')">Dissociation</button>
    <button onclick="selfRestore()">Restore</button>
    <span style="margin-left:auto;color:var(--dim)">
      self coherence: <b style="color:var(--accent)" id="self-coh">1.00</b>
    </span>
  </div>
  <div class="info">
    <b>The self is not a place in the brain.</b> It is not stored as a single memory or
    located in a specific region. It is a <b>prediction</b> &mdash; the answer to "who is
    this system, and what does it do next?" That prediction is re-inferred moment by moment
    from four main inputs: the body (interoception, posture, heart rate), recent memories
    (what just happened), current context (where, with whom, doing what), and the social
    mirror (how others are treating me). Each of these feeds weight into the self-node,
    and the self-node in turn biases all downstream prediction: emotional response,
    decision-making, even perception.<br><br>
    <b>Why this matters:</b> If the self is a prediction, then destabilizing any of its
    feeder channels should destabilize the self experience itself. And that is exactly what
    happens:<br>
    &bull; <b>Meditation</b> quiets the body-feeder and memory-feeder. The self-prediction
    loses inputs and starts to weaken. The experience: "I am not my thoughts. I am not my
    body. I am awareness." That is the self-node running thin on evidence.<br>
    &bull; <b>Psychedelics</b> (especially high-dose psilocybin, LSD, DMT) globally weaken
    all predictive priors. The self-node, being the highest prediction in the hierarchy,
    is one of the first to destabilize. The experience: ego death, "oceanic boundlessness,"
    the sense of merging with everything.<br>
    &bull; <b>Dissociation / depersonalization</b> severs the body-feeder specifically.
    The self can still run, but it feels unattached: "I can see myself from outside."
    "I feel like a ghost in my own life." The prediction is still running but its
    evidence is thin and the confidence has dropped.<br><br>
    <b>The surprising consequence:</b> "I" is not a fact. It is a continuously-maintained
    forecast. Most of the time you do not notice it because the forecast is stable and
    well-fed. When it destabilizes you realize how much work the network was doing to
    hold you together &mdash; and how remarkable it is that the work usually succeeds.
  </div>
  </div>

  <div class="sub-section">
  <h3>Humor &mdash; Safe Prediction Failure</h3>
  <p class="desc">
    A joke is a prediction error delivered in a safe context. Setup builds the forecast,
    punchline violates it, and because no threat fires, the all-clear signal comes out as
    laughter. Same mechanism as the residual scorer &mdash; minus the danger.
  </p>
  <div class="canvas-box">
    <canvas id="humor-canvas" width="960" height="300"></canvas>
  </div>
  <div class="controls">
    <button onclick="humorPlay('safe')">Joke (safe context)</button>
    <button onclick="humorPlay('unsafe')">Same setup, unsafe context</button>
    <button onclick="humorReset()">Reset</button>
  </div>
  <div class="info">
    <b>Why jokes are funny:</b> A joke works by building a prediction through the setup
    ("a man walks into a bar...") and then violating it with the punchline. The residual
    scorer fires &mdash; a sudden spike of prediction error. If that spike came with a
    threat signal, the same event would register as fear or alarm. But in a safe context
    (nothing is actually dangerous, nobody is actually being hurt), the threat monitor
    stays quiet and the prediction-error spike is tagged as harmless. Laughter is the
    neurological equivalent of "false alarm, system stand down." It is the all-clear
    signal firing after a legitimate spike.<br><br>
    <b>The timing has to be precise.</b> Too obvious a setup and there is no prediction to
    violate. Too obscure and the violation does not land because the forecast was never
    built in the first place. The joke has to generate a confident forecast and then break
    it cleanly &mdash; that is what "timing" means in comedy. It is literally the
    calibration of prediction strength.<br><br>
    <b>Why the same joke stops being funny:</b> Once you have heard a joke, your forecast
    updates. The punchline is now expected. The residual never fires because there is
    nothing to be surprised about. Humor has an anti-repeatability built into it &mdash;
    the same way the surprise signal burns out when the input stops being novel.<br><br>
    <b>Why humor fails in unsafe contexts:</b> The exact same joke told after a real
    threat fires produces a different experience entirely. The prediction error still
    happens, but now it is tagged as a threat violation, not a safe one. The laugh does
    not come. This is why comedians talk about "reading the room" &mdash; they are
    checking whether the threat monitor is clear enough for the prediction-error spike
    to land as humor instead of alarm.
  </div>

  <div class="info" style="border-left: 3px solid #f06292">
    <b style="color:#f06292">Horror uses the same residual &mdash; different routing</b><br><br>
    A jump scare and a punchline are structurally identical at the
    residual level. Both violate the prediction. The difference is the
    <b>context frame</b> &mdash; a state modulator that determines
    whether the residual gets routed to laughter or fight-or-flight.<br><br>
    &bull; <b>Humor = prediction error + safety frame.</b> Nobody is
    hurt, stakes are zero, social context is playful. Laughter is
    literally a signal to others: &quot;this was surprising but
    safe.&quot;<br>
    &bull; <b>Horror = prediction error + threat frame.</b> Darkness,
    tense music, isolation cues. The same residual routes to adrenaline,
    flinch, scream.<br>
    &bull; <b>Nervous laughter</b> = the safety signal is ambiguous.
    The brain cannot decide if the situation is threatening or safe, so
    both responses fire partially.<br>
    &bull; <b>Dark humor</b> = deliberately placing a safety frame on
    threatening content. The joke re-routes what should be horror
    through the laughter pathway. People who &quot;can&apos;t handle
    dark humor&quot; have a stronger threat frame that overrides the
    safety signal.<br>
    &bull; <b>Jump-scare fatigue</b> = the same reason repeated jokes
    are not funny. The prediction error shrinks because you have
    calibrated. Horror movies escalate because the residual threshold
    rises with exposure (same mechanism as the Media canvas's
    short-form tolerance).<br>
    &bull; <b>Comedic timing</b> = the setup builds the prediction,
    the pause lets it solidify, the punchline violates it. Too fast =
    prediction never forms, no residual. Too slow = audience predicts
    the punchline, small residual.<br>
    &bull; <b>You can&apos;t tickle yourself</b> because your motor
    predictor perfectly predicts your own touch. Zero residual = zero
    response. Someone else&apos;s touch is unpredicted = residual +
    safety frame (you know them) = laughter.
  </div>
  </div>

  <div class="sub-section">
  <h3 id="arousal-clarity">Arousal &amp; Clarity &mdash; The Brain&apos;s Most Powerful State Modulator</h3>
  <p class="desc">
    Sexual arousal is the most powerful state modulator the brain
    produces. It temporarily rewrites the entire edge-weight landscape:
    narrows bandwidth to one goal, suppresses the frontal cortex
    (judgment, consequences, planning), collapses the prediction window
    to seconds, and amplifies reward-pathway edges. When it switches
    off after orgasm, the landscape snaps back &mdash; and the contrast
    between suppressed and restored feels like sudden clarity.
  </p>
  <div class="canvas-box">
    <canvas id="clarity-canvas" width="960" height="400"></canvas>
  </div>
  <div class="controls">
    <button onclick="clarityPhase('baseline')">Baseline</button>
    <button onclick="clarityPhase('arousal')">During arousal</button>
    <button onclick="clarityPhase('peak')">Orgasm (residual closes)</button>
    <button onclick="clarityPhase('clarity')">Post-nut clarity</button>
  </div>

  <div class="info">
    <b>The four phases through PEP primitives:</b><br><br>
    <b style="color:var(--accent)">1. Baseline.</b> Normal edge weights.
    Frontal cortex online. Full bandwidth. Prediction window extends
    hours ahead. Judgment, consequence evaluation, social reasoning all
    active. This is your default operating state.<br><br>
    <b style="color:#f06292">2. Arousal.</b> The state modulator fires.
    Bandwidth narrows to one goal. Frontal cortex suppresses (measurable
    in fMRI &mdash; prefrontal activity drops during arousal). Edge
    weights rewrite: pathways to reward are amplified; pathways to
    &quot;is this a good idea&quot; are dampened. Prediction window
    collapses to the next 30 seconds. This is why decisions made during
    arousal would never be made otherwise &mdash; the landscape is
    temporarily different.<br><br>
    <b style="color:#fbbf24">3. Orgasm.</b> The reward prediction
    resolves. Residual closes to zero. Massive dopamine spike followed
    by prolactin surge that rapidly drops dopamine below baseline.
    The arousal modulator switches off <em>abruptly</em> because
    prolactin antagonizes the dopamine that was sustaining it.<br><br>
    <b style="color:var(--accent2)">4. Post-nut clarity.</b> Frontal
    cortex comes back online. Bandwidth restores. Coherence rebuilds.
    Prediction window extends. You can think about tomorrow again. The
    &quot;clarity&quot; IS the contrast &mdash; you feel clear-headed
    not because you are smarter than baseline, but because you were
    just in a state where most cognitive machinery was suppressed.
    Stepping from suppressed &rarr; baseline <em>feels</em> like a
    boost because the delta is stark.
  </div>

  <div class="info" style="border-left: 3px solid var(--accent2)">
    <b style="color:var(--accent2)">What this explains</b><br><br>
    &bull; <b>Post-nut regret.</b> Decisions made during Phase 2
    (suppressed frontal cortex) are now evaluated by Phase 4 (restored
    frontal cortex). The evaluation changes because the state modulator
    changed. What seemed worth it when consequences were dampened does
    not seem worth it when they are back online.<br><br>
    &bull; <b>Why it&apos;s sudden.</b> The arousal modulator has a
    near-binary off-transition. Prolactin surge is rapid. The switch
    from &quot;arousal mode&quot; to &quot;normal mode&quot; happens in
    seconds, not minutes.<br><br>
    &bull; <b>Why intensity varies.</b> The strength of the clarity
    depends on how far the arousal modulator pushed the system from
    baseline. More intense arousal = more suppression = more dramatic
    contrast on return.<br><br>
    &bull; <b>Why it fades.</b> After prolactin clears (minutes to
    hours), the modulator can re-engage. The clarity normalizes as
    baseline stabilizes and the contrast effect dissipates.<br><br>
    &bull; <b>Why &quot;think with your brain, not your...&quot;</b>
    This folk advice is literally describing the state-modulation
    mechanism. During arousal, you are not thinking with your full
    brain &mdash; a large part of it (the frontal cortex) has been
    taken offline by the modulator. The advice is &quot;notice that the
    modulator is active and discount its influence on your
    decision-making.&quot; Easier said than done, because the modulator
    also suppresses the meta-awareness that would notice it.
  </div>

  <div class="info" style="border-left: 3px solid #ffb74d">
    <b style="color:#ffb74d">This is not just sex &mdash; every powerful drive does the same thing</b><br><br>
    Sexual arousal is the most dramatic example, but the mechanism is
    universal. <em>Any sufficiently powerful drive state</em> acts as a
    state modulator that suppresses the frontal cortex, narrows
    bandwidth, collapses the prediction window, and rewrites edge
    weights toward the drive object:<br><br>
    &bull; <b>Extreme hunger.</b> A starving person will eat things they
    would never eat at baseline. They will steal food. They will break
    social norms. The hunger modulator has suppressed the frontal cortex
    (consequence evaluation) and amplified reward pathways (food = only
    goal). After eating, the same &quot;clarity&quot; hits &mdash;
    &quot;I can&apos;t believe I did that&quot; &mdash; because the
    frontal cortex is back online and re-evaluating.<br><br>
    &bull; <b>Addiction craving.</b> The addict in withdrawal has a
    drive modulator running at maximum. Bandwidth narrowed to one goal
    (the substance). Frontal cortex suppressed (risks dismissed).
    Prediction window collapsed to &quot;right now.&quot; Decisions
    made during craving are re-evaluated with horror during
    sobriety &mdash; same mechanism as post-nut clarity, same
    contrast effect.<br><br>
    &bull; <b>Fear / survival threat.</b> A person in mortal danger
    will do things they would never do at baseline &mdash; extreme
    violence, abandoning others, feats of strength. The threat
    modulator suppresses everything except escape pathways. After the
    threat passes, &quot;I can&apos;t believe I did that&quot; &mdash;
    same mechanism, same clarity.<br><br>
    &bull; <b>Rage.</b> Intense anger is a drive state that narrows
    bandwidth to the target of the anger and suppresses consequence
    evaluation. People say things in rage they &quot;didn&apos;t
    mean&quot; &mdash; they meant them under the rage modulator&apos;s
    edge weights, not under baseline edge weights. The regret afterward
    is the contrast between modulated and unmodulated evaluation.<br><br>
    <b>The general principle:</b> any state modulator powerful enough
    to suppress the frontal cortex produces the same pattern &mdash;
    irrational behavior during the drive, followed by clarity and often
    regret when the drive resolves and the frontal cortex restores.
    The &quot;irrationality&quot; is not a failure of reasoning. It is
    reasoning under a different set of edge weights. The person IS
    being rational &mdash; for the landscape the modulator created.
    They just would not have chosen that landscape voluntarily.
  </div>
  </div>

  <div class="sub-section">
  <h3>Reading &mdash; Controlled Hallucination</h3>
  <p class="desc">
    When you read a story, your visual cortex renders imagery from text prompts. The
    rendering is real &mdash; the same regions that process sight are generating the
    scene. Reading is legally indistinguishable from a dream you are steering word by word.
  </p>
  <div class="canvas-box">
    <canvas id="read-canvas" width="960" height="340"></canvas>
  </div>
  <div class="controls">
    <button onclick="readStory('vivid')">Vivid Scene</button>
    <button onclick="readStory('abstract')">Abstract Prose</button>
    <button onclick="readStory('technical')">Technical Text</button>
    <button onclick="readStop()">Stop</button>
    <span style="margin-left:auto;color:var(--dim)">
      render load: <b style="color:var(--accent2)" id="read-load">0%</b>
    </span>
  </div>
  <div class="info">
    <b>What is happening in your head right now:</b> As you read this sentence, the words
    are activating concept nodes, which are pulling activation into sensory regions &mdash;
    visual cortex, auditory cortex, motor areas, emotional pathways. You are not "just
    reading." Your brain is generating a multimodal simulation of what the words describe.
    When the text says "the red apple on the wooden table," your visual cortex produces
    an apple-on-table scene, complete with color, texture, and approximate lighting. Not
    because you chose to. Because the predictor, prompted by the words, runs what it
    expects the described scene would look like.<br><br>
    <b>Why this is indistinguishable from hallucination:</b> The same visual regions that
    fire during dreams, during psychedelic trips, and during Ganzfeld hallucinations are
    firing right now. The only difference is that reading is <b>prompted and constrained</b>
    &mdash; each word is a new input to the predictor, so the imagery stays tethered to the
    text. Dreaming is the same process with no external tether. Hallucination is the same
    process when the tether fails.<br><br>
    <b>Why some text produces vivid imagery and some produces nothing:</b> Text load
    depends on how much sensory content the words activate. "The red apple on the wooden
    table" = high visual render load. "The metaphysical implications of dualism" = almost
    none &mdash; no concrete concepts to prompt the sensory regions. Technical writing
    feels "dry" because it asks the predictor to run without imagery prompts. Great
    fiction writing is great precisely because it provides the predictor with dense,
    specific, concrete prompts that fire a rich internal rendering.
  </div>
  </div>

  <div class="sub-section">
  <h3>Aphantasia &harr; Hyperphantasia &mdash; Same Knob, Two Extremes</h3>
  <p class="desc">
    People vary enormously in their mental imagery. Some have none at all (aphantasia):
    when they think of an apple, there is no visual. Others have cinema-sharp imagery
    (hyperphantasia): the apple is fully rendered, rotating in full color. Same network,
    different setting on the re-render parameter.
  </p>
  <div class="canvas-box">
    <canvas id="apha-canvas" width="960" height="320"></canvas>
  </div>
  <div class="controls">
    <label style="display:flex;align-items:center;gap:8px">
      <span>imagery strength:</span>
      <input type="range" id="apha-strength" min="0" max="100" value="50" style="width:160px">
      <span class="stat-val" id="apha-val">50%</span>
    </label>
    <button onclick="aphaPrompt('apple')">Imagine: apple</button>
    <button onclick="aphaPrompt('face')">Imagine: a loved face</button>
    <button onclick="aphaPrompt('ocean')">Imagine: the ocean</button>
  </div>
  <div class="info">
    <b>The phenomenon:</b> Aphantasia was formally described by Zeman in 2015, though
    people had been quietly experiencing it their whole lives. Estimated prevalence: 2-5%.
    These people "think about" an apple, and there is nothing visual &mdash; just a concept,
    a word, a set of associations, but no image. They are not cognitively impaired; most
    never even realized their experience was different until they heard other people
    describe mental pictures. Hyperphantasia (at the other end) produces imagery so vivid
    it can be mistaken for actual perception &mdash; some hyperphantasics can hold a
    rotating 3D mental model of an object for minutes.<br><br>
    <b>The mechanism:</b> Mental imagery requires running sensory-cortex activation from
    a non-sensory prompt. The "strength" of that backward activation is a tunable parameter.
    In aphantasia, the parameter sits near zero: concepts activate verbal and semantic
    pathways but do not cascade into visual cortex. In hyperphantasia, the same parameter
    is turned up so high that concept activation produces visual output nearly as strong
    as real perception. The network is the same in both cases. Only the weight on the
    re-render edge differs.<br><br>
    <b>Consequences:</b> Aphantasics often report not having strong nostalgic imagery,
    not being able to "picture" loved ones they miss, not experiencing "flashbacks" the
    way others describe them. But they typically function fine in every cognitive
    domain &mdash; they just use verbal and semantic routes instead of visual ones.
    Hyperphantasics are over-represented among artists, designers, and certain kinds of
    novelists, but they also have a higher incidence of intrusive imagery, PTSD flashbacks,
    and difficulty separating real memories from vividly-imagined ones. The same knob that
    gives you a rich inner world also makes it harder to tell the inner world from the
    outer one.
  </div>
  </div>

  <div class="sub-section">
  <h3>Two-System Thinking &mdash; System 1 vs System 2</h3>
  <p class="desc">
    The brain has two thinking modes sharing one activation budget. System 1 is fast,
    parallel, intuitive pattern-matching. System 2 is slow, serial, deliberate reasoning.
    S1 always tries first. S2 only engages when S1 fails or when something forces it to.
  </p>
  <div class="canvas-box">
    <canvas id="twosys-canvas" width="960" height="320"></canvas>
  </div>
  <div class="controls">
    <button onclick="twosysInput('easy')">Easy Pattern (1+1=?)</button>
    <button onclick="twosysInput('hard')">Hard Problem (17×24=?)</button>
    <button onclick="twosysInput('trap')">Trap (cognitive illusion)</button>
    <button onclick="twosysReset()">Reset</button>
  </div>
  <div class="info">
    <b>System 1</b> runs automatically on every input. It matches against pattern memory,
    returns an answer or a guess fast, and uses very little of the budget. "What is 2+2?"
    "What is this person's facial expression?" "Is this sentence grammatical?" All S1.<br><br>
    <b>System 2</b> has to be actively engaged. It runs serial computation, tracks working
    memory, applies rules, checks its own steps. "What is 17 × 24?" "What is the counter-
    argument to this position?" "Is this conclusion actually justified by the premises?"
    All S2. It is expensive &mdash; it consumes most of the bandwidth budget while running,
    which is why you cannot do S2 math while holding a complex conversation.<br><br>
    <b>The failure mode is S1 answering questions S2 should handle.</b> Cognitive illusions
    (the bat-and-ball problem, anchoring, availability bias) work because S1 has a fast
    confident answer ready, and S2 accepts it without auditing. The only defense is
    learning to notice when S1 is overconfident and forcing S2 to check &mdash; which is
    expensive and exhausting, which is why humans do not do it by default.
  </div>
  </div>

  <div class="sub-section">
  <h3>Chunking &mdash; Compressing Working Memory</h3>
  <p class="desc">
    Working memory holds about 4 items at a time. But an "item" can be a single digit or
    a whole phrase, depending on how the information is structured. Chunking is how the
    network fits a dozen things into four slots by grouping them into higher-level units.
  </p>
  <div class="canvas-box">
    <canvas id="chunk-canvas" width="960" height="300"></canvas>
  </div>
  <div class="controls">
    <button onclick="chunkShow('raw')">Show Raw (12 items)</button>
    <button onclick="chunkShow('chunked')">Chunk into Groups</button>
    <button onclick="chunkShow('expert')">Expert-Level Chunks</button>
  </div>
  <div class="info">
    <b>The classic demonstration:</b> "H, G, T, V, F, B, I, C, I, A, P, C" &mdash; twelve
    letters, at the edge of working memory. Rearrange: "HGTV, FBI, CIA, PC" &mdash; four
    chunks, trivially easy. Same information, an order of magnitude less load.<br><br>
    <b>Expert chunking:</b> A chess master looking at a mid-game board does not see 32
    pieces. They see a handful of familiar strategic configurations (a Sicilian defense,
    a kingside attack, a pinned knight), each of which is a single chunk containing dozens
    of sub-elements. This is why experts can hold complex scenes in working memory that
    look overwhelming to novices &mdash; the same information has been recoded into
    fewer, larger units.<br><br>
    <b>Learning to chunk is how expertise forms.</b> Every domain has a hierarchy of
    chunks. The first year you learn by holding individual components in working memory,
    running out of bandwidth constantly. Over time, frequently-co-occurring components
    get encoded as single units. Eventually the novice's "twelve-thing problem" becomes
    the expert's "one-thing problem" and the expert has eleven slots free for other work.
  </div>
  </div>

  <div class="sub-section">
  <h3>Synesthesia &mdash; Cross-Modal Binding</h3>
  <p class="desc">
    In most brains, sensory modalities are suppressed from each other &mdash; sound does
    not leak into color, letters do not leak into taste. In synesthetes, the suppression
    never formed. Activation in one modality consistently triggers the other.
  </p>
  <div class="canvas-box">
    <canvas id="syn-canvas" width="960" height="320"></canvas>
  </div>
  <div class="controls">
    <button onclick="synMode('normal')">Normal</button>
    <button onclick="synMode('syn')">Synesthete</button>
    <button onclick="synTrigger('C')">Play: C</button>
    <button onclick="synTrigger('E')">Play: E</button>
    <button onclick="synTrigger('G')">Play: G</button>
  </div>
  <div class="info">
    <b>Grapheme-color synesthesia</b> is the most common form: certain letters or numbers
    reliably evoke specific colors. The synesthete does not "imagine" the color &mdash;
    they experience it as a real property of the letter, and it is consistent across their
    whole life. Chromesthesia (sound → color) is another common form.<br><br>
    <b>The mechanism</b> appears to be reduced inhibition between adjacent sensory regions.
    Every brain is born with extensive cross-modal connections. During early development,
    most of them get pruned to keep modalities clean. Synesthetes are brains where the
    pruning was incomplete in specific regions &mdash; the connections stayed, and so the
    cross-modal activation stayed.<br><br>
    <b>It is not a disorder.</b> Synesthetes tend to have slightly better memory for the
    linked modalities (because each input has a second encoding channel), are
    over-represented among artists and musicians, and usually do not realize their
    experience is unusual until someone mentions it. The same mechanism running at low
    intensity in normal brains produces the metaphor-friendly "bright" sound, "sharp"
    color, "warm" voice. Metaphor is just the faint echo of synesthesia everyone has.
  </div>
  </div>

  <div class="sub-section">
  <h3>The Binding Problem &mdash; How One Experience Happens</h3>
  <p class="desc">
    You see a face and hear a voice and experience them as one thing. But the visual and
    auditory signals arrive through completely separate pathways, at different latencies,
    in different regions. How does the network fuse them into a single percept? Binding.
    When it fails, you get agnosias &mdash; the seeing and hearing still happen, but they
    do not add up to one thing.
  </p>
  <div class="canvas-box">
    <canvas id="bind-canvas" width="960" height="340"></canvas>
  </div>
  <div class="controls">
    <button onclick="bindFire('normal')">Normal Binding</button>
    <button onclick="bindFire('broken')">Binding Failure</button>
    <button onclick="bindReset()">Reset</button>
  </div>
  <div class="info">
    <b>The problem:</b> Colors are processed in one region, shapes in another, motion in
    a third, faces in a fourth, sounds entirely separately. Yet you do not experience
    "motion + color + shape + sound" as four separate streams. You experience "a red ball
    bouncing and making a thud" as one unified event. Something is stapling the streams
    together. That "something" is binding &mdash; a set of synchronization and
    co-activation mechanisms that tag co-occurring features as belonging to one object.<br><br>
    <b>When binding breaks</b> (in certain kinds of stroke, agnosias, simultanagnosia),
    the patient can describe every individual feature but cannot assemble them. They see
    "something red," "something round," "a bouncing motion," "a thud sound" &mdash; but
    not "a red ball bouncing with a thud." The low-level recognition is intact. The
    fusion operation is not.<br><br>
    <b>Why this is load-bearing for Axona:</b> Unified experience is not free. It is a
    network operation that the system runs continuously, and it can fail in specific ways
    that reveal the machinery. The "self" as a predicted node is the same kind of binding
    problem, one level up: the network is running a binding operation on its own internal
    states to produce the experience of being one coherent thing.
  </div>
  </div>

  <div class="sub-section">
  <h3>Intuition &mdash; Pattern Match Below the Conscious Threshold</h3>
  <p class="desc">
    Intuition is not magic. It is pattern recognition running in parallel below the level
    the network reports to consciousness. The match can be strong and correct long before
    any verbal reasoning catches up &mdash; which is why "I just knew something was
    wrong" is a real cognitive event, not a retroactive story.
  </p>
  <div class="canvas-box">
    <canvas id="intu-canvas" width="960" height="320"></canvas>
  </div>
  <div class="controls">
    <button onclick="intuExpose()">Expose to Pattern</button>
    <button onclick="intuReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      subliminal match: <b style="color:var(--accent)" id="intu-level">0.00</b>
      &nbsp; conscious: <b style="color:var(--accent2)" id="intu-con">no</b>
    </span>
  </div>
  <div class="info">
    <b>What is happening:</b> Every input activates many candidate memories in parallel.
    Most of them never reach the conscious threshold &mdash; they fire weakly and decay.
    But if the current input is similar to a pattern you have encountered before,
    activation accumulates on that match. Once it crosses a threshold, it becomes a
    conscious signal: "this feels off," "I know this person is lying," "this is going to
    work." The match was real long before you could verbalize it.<br><br>
    <b>Why experts have good intuitions and novices have bad ones:</b> Intuition is only
    as good as the pattern library it is running against. Chess masters have tens of
    thousands of game patterns encoded. When they glance at a board and say "this is
    won," they are running a match against that library in a fraction of a second.
    A novice running the same "intuition" on the same board has no library to match
    against, so their intuition is noise.<br><br>
    <b>The practical implication:</b> Do not trust your intuitions about domains you
    have no experience in. Do trust your intuitions about domains you have deep
    experience in, even when you cannot explain them &mdash; the verbal channel is
    slower than the pattern match, and sometimes the match is correct.
  </div>
  </div>

  <div class="sub-section">
  <h3>Priming &mdash; How Recent Activation Shapes the Next Interpretation</h3>
  <p class="desc">
    The same ambiguous input produces different interpretations depending on what was
    recently active. A word, an image, even a feeling can silently bias the network's
    reading of the next thing, and you never notice it happening.
  </p>
  <div class="canvas-box">
    <canvas id="prime-canvas" width="960" height="300"></canvas>
  </div>
  <div class="controls">
    <button onclick="primeSet('river')">Prime: RIVER</button>
    <button onclick="primeSet('money')">Prime: MONEY</button>
    <button onclick="primeSet(null)">No Prime</button>
    <button onclick="primeAmbig()">Show ambiguous word</button>
  </div>
  <div class="info">
    <b>Classic demonstration:</b> The word BANK is ambiguous. Prime with "river" first
    and BANK reads as "riverside." Prime with "money" first and BANK reads as
    "financial institution." You do not experience this as ambiguity &mdash; you just see
    the word and immediately understand which meaning was intended. The priming is
    invisible.<br><br>
    <b>Why it happens:</b> Reading BANK activates both meaning clusters in parallel. But
    one of them is already pre-activated by the prime &mdash; that cluster is just slightly
    warmer than the other. Activation flows more easily into a warm cluster than a cold
    one. The warm reading wins the competition, becomes the conscious interpretation, and
    you never notice the losing candidate.<br><br>
    <b>Why this matters:</b> Every piece of input you process is being interpreted
    through whatever was just active. Your mood primes which memories surface. The
    article you just read primes how you interpret the next one. The movie you watched
    last night primes your dreams. Nothing about cognition is context-free. The "neutral
    reading" is a myth; there is only the reading produced by the state you are in.
  </div>
  </div>

  <div class="sub-section">
  <h3>Autism &mdash; High-Precision Priors, Not Broken Priors</h3>
  <p class="desc">
    One of the cleanest reframes the predictive-processing framework offers: autism is
    not "broken social cognition" or "missing empathy." It is a network running with
    unusually high prior precision &mdash; less tolerance for sensory noise, more demand
    that reality match the forecast exactly.
  </p>
  <div class="canvas-box">
    <canvas id="autism-canvas" width="960" height="320"></canvas>
  </div>
  <div class="controls">
    <label style="display:flex;align-items:center;gap:8px">
      <span>prior precision:</span>
      <input type="range" id="autism-prec" min="10" max="99" value="50" style="width:140px">
      <span class="stat-val" id="autism-prec-val">50%</span>
    </label>
    <button onclick="autismInject()">Inject Sensory Event</button>
    <button onclick="autismReset()">Reset</button>
  </div>
  <div class="info">
    <b>The framework</b> (Pellicano &amp; Burr 2012; Van de Cruys et al. 2014): every
    predictive network has a precision parameter that controls how tightly its forecasts
    must match incoming data. Lower precision → tolerant, willing to write off noise as
    "close enough." Higher precision → intolerant, every mismatch registers as a real
    prediction error. The autistic brain appears to run with the precision parameter
    turned up.<br><br>
    <b>What follows from that:</b>
    &bull; <b>Sensory overload:</b> environments most brains filter as background noise
    (fluorescent humming, rustling clothes, flickering lights) generate constant
    prediction errors because the precision is high enough to flag them. What looks like
    "sensitivity" is a calibration difference.<br>
    &bull; <b>Routine and sameness:</b> if your precision is high, unpredictable
    environments produce constant residuals. Routine minimizes those residuals. The
    preference for sameness is not irrational &mdash; it is the cheapest strategy for a
    high-precision system.<br>
    &bull; <b>Social difficulty:</b> social inference relies on loose, probabilistic
    matching over fuzzy signals (tone, facial micro-expression, context). A high-precision
    system trying to run social inference gets swamped with prediction errors because
    social signals are inherently noisy. The tone fails to match the words? Residual. The
    expression does not fit the situation? Residual. Everyone is generating residuals
    constantly, and the system has no way to discount them.<br><br>
    <b>The key reframe:</b> It is not that the autistic network is less capable. It is
    that the same network running with a different precision parameter produces different
    experiences. Some of those differences are advantages (pattern detection, domain
    expertise, detail fidelity). Some are costs (social overhead, sensory overload). The
    network is not broken; the knob is in a different place.
  </div>
  </div>

  <div class="sub-section">
  <h3>Habit Formation &mdash; The Automaticity Threshold</h3>
  <p class="desc">
    Every action starts as a conscious effortful computation. After enough repetitions,
    the edge weights cross a threshold and the action becomes automatic &mdash; no
    longer requiring System 2, no longer even registering in conscious awareness.
  </p>
  <div class="canvas-box">
    <canvas id="habit-canvas" width="960" height="320"></canvas>
  </div>
  <div class="controls">
    <button onclick="habitRepeat()">Repeat Action</button>
    <button onclick="habitReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      repetitions: <b id="habit-reps">0</b>
      &nbsp; weight: <b style="color:var(--accent)" id="habit-weight">0.00</b>
      &nbsp; status: <b style="color:var(--accent2)" id="habit-status">effortful</b>
    </span>
  </div>
  <div class="info">
    <b>The curve is not linear.</b> The first few repetitions barely move the weight.
    Then growth accelerates. Then it slows down as it approaches the automaticity
    threshold. Then &mdash; often suddenly &mdash; the action "clicks" and becomes
    effortless. This is not a smooth transition. It is a phase change in which pathway
    is routing the activation.<br><br>
    <b>Lally et al. 2010</b> measured real-world habit formation and found a median of
    ~66 days before a new behavior felt automatic, with huge variance (18-254 days)
    depending on the complexity of the action and the consistency of the context. The
    magic "21 days" you hear is a myth &mdash; it came from a plastic surgeon's 1960
    observation about post-op adjustment, not from habit research.<br><br>
    <b>Why habits are hard to break:</b> Once a pathway has crossed the automaticity
    threshold, it fires without conscious activation. You find yourself halfway through
    the action before you realized you chose to do it. Breaking a habit is not "not
    doing" the action &mdash; it is building a competing pathway that fires first and
    claims the activation budget before the habit pathway can. This is why cue avoidance
    (remove the trigger, change the context) works better than willpower (try to suppress
    the automatic response). Competition, not suppression.
  </div>
  </div>

  <div class="sub-section">
  <h3>The Interpreter &mdash; The Narrator That Runs After the Fact</h3>
  <p class="desc">
    The left hemisphere runs a module that generates reasons for actions &mdash; often
    for actions it did not initiate. In split-brain patients, Gazzaniga found the module
    will confidently explain a choice made by the isolated right hemisphere, making up
    the reason on the spot and believing it. Every "because" you have said might be
    running the same process.
  </p>
  <div class="canvas-box">
    <canvas id="interp-canvas" width="960" height="360"></canvas>
  </div>
  <div class="controls">
    <button onclick="interpAct('walk')">Right Hemisphere: "walk"</button>
    <button onclick="interpAct('laugh')">Right Hemisphere: "laugh"</button>
    <button onclick="interpAct('reach')">Right Hemisphere: "reach for water"</button>
    <button onclick="interpReset()">Reset</button>
  </div>
  <div class="info">
    <b>The experiment</b> (Gazzaniga, 1960s-present): in split-brain patients whose
    corpus callosum has been severed, the two hemispheres can no longer communicate
    directly. Flash a written command ("walk") to the right hemisphere only &mdash; the
    patient stands up and walks. Then ask them why they stood up. The left hemisphere
    never saw the command. But it does not say "I don't know." It says, confidently,
    "I was going to get a Coke." It makes up a reason, believes it, and feels like it
    chose.<br><br>
    <b>Why this is devastating:</b> The interpreter is not a rare module in split-brain
    patients. It runs in every brain. It is the voice of "I did X because…" It runs
    <em>after</em> the network has already produced the action, examines the context,
    and constructs a plausible reason. Most of the time the reason it constructs is
    roughly correct because the interpreter has access to the same information that
    drove the decision. But when it doesn't &mdash; when the decision came from a
    subsystem the interpreter cannot observe &mdash; it confabulates, without any
    signal that what it is saying is made up.<br><br>
    <b>What this implies:</b> Your experience of "deciding" is largely the interpreter
    narrating what already happened. The actual causal work is done by pathways you do
    not have introspective access to. "I chose this because…" is almost always a
    story the interpreter wrote to stitch the action into a coherent self. The story
    is often true in outline, but it is always a story, always post-hoc, and always
    capable of being completely wrong without you noticing.<br><br>
    <b>Why it feels like deciding:</b> Because the interpreter is running fast enough
    and integrated tightly enough that its narrative arrives before you notice the
    seam. The narrative feels like the cause. It is a report, not a cause &mdash; but
    the reporting channel is the only channel you have introspective access to, so it
    <em>is</em> your experience of what happened.
  </div>
  </div>

  <div class="sub-section">
  <h3>Inattentional Blindness &mdash; The Attention Filter Prevents Encoding</h3>
  <p class="desc">
    If attention does not land on something, it is not stored. The input arrived at
    the eye. The signal reached visual cortex. But the network never allocated the
    resources to encode it into memory, so it simply never happened in your experience.
    "I didn't see it" can be literally, neurologically true.
  </p>
  <div class="canvas-box">
    <canvas id="inatt-canvas" width="960" height="360"></canvas>
  </div>
  <div class="controls">
    <button onclick="inattTask('count')">Start Counting Task</button>
    <button onclick="inattReview()">Review: Did You See the Gorilla?</button>
    <button onclick="inattReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      passes counted: <b id="inatt-count">0</b>
      &nbsp; gorilla seen: <b id="inatt-gorilla">—</b>
    </span>
  </div>
  <div class="info">
    <b>The original experiment</b> (Simons &amp; Chabris, 1999): participants watch a
    video of people passing a basketball and are asked to count how many passes the
    white-shirted team makes. Halfway through the video, a person in a gorilla suit
    walks through the scene, stops at center, beats their chest, and walks off. About
    half of viewers, focused on the counting task, report not seeing the gorilla at
    all. When shown the video again without the task, they see it immediately and are
    often convinced they must have been shown a different video.<br><br>
    <b>The mechanism:</b> Attention allocates encoding resources. If a task is
    consuming your budget, there is no budget left for encoding "unexpected peripheral
    motion." The visual signal still enters visual cortex &mdash; you can see proof of
    that in the fMRI &mdash; but it does not get passed up to higher areas, does not
    get bound into memory, and does not enter conscious experience. The person
    "looked right at" the gorilla but never "saw" it in the sense that matters:
    the network never wrote it down.<br><br>
    <b>What this means for everyday life:</b> Everything you "saw today" is filtered
    through whatever task was consuming your attention. The things you were not
    attending to were never encoded, so they do not exist in memory, which means you
    experience the world as if they were not there. Witnesses miss events. Radiologists
    miss tumors on scans when they are looking for something else. Drivers miss
    motorcycles. None of them are lying. The input never became a memory.
  </div>
  </div>

  <div class="sub-section">
  <h3>The McGurk Effect &mdash; Binding Going Wrong Lawfully</h3>
  <p class="desc">
    Audio "ba" + visual lips saying "ga" produces the conscious experience of "da"
    &mdash; a phoneme that was in neither input. The brain is not averaging; it is
    actively constructing a percept that reconciles the two incompatible signals.
    The construction is perception, and it is wrong.
  </p>
  <div class="canvas-box">
    <canvas id="mcgurk-canvas" width="960" height="320"></canvas>
  </div>
  <div class="controls">
    <button onclick="mcgurkFire('congruent')">Audio BA + Visual BA</button>
    <button onclick="mcgurkFire('illusion')">Audio BA + Visual GA</button>
    <button onclick="mcgurkFire('audio-only')">Audio BA only</button>
    <button onclick="mcgurkReset()">Reset</button>
  </div>
  <div class="info">
    <b>The effect</b> (McGurk &amp; MacDonald, 1976): when audio and video of a speaker
    mismatch in a specific way, the listener reports hearing a phoneme that matches
    neither. The brain's multimodal speech-perception network integrates lip
    movements into the phoneme decoder at a pre-conscious level. You cannot override
    it by knowing what the trick is &mdash; watching the mismatched video still
    produces the illusory percept even when you know exactly what the audio track
    really is. Close your eyes and the audio is "ba." Open them and the audio
    "becomes" "da." Same sound. Different percept.<br><br>
    <b>Why it matters:</b> Perception is not a passive read of sensory data. It is
    an active reconstruction the brain performs using whatever inputs are available,
    weighted by how reliable each modality usually is. Vision is a strong prior for
    speech because in the ancestral environment, face visibility nearly always meant
    low-noise conditions &mdash; so the brain weights visual articulation heavily.
    When the inputs disagree, the reconstruction is a compromise. The compromise
    is conscious experience.<br><br>
    <b>The broader point:</b> Everything you experience is a compromise reconstruction.
    Normally the inputs agree and the reconstruction looks exactly like "reality."
    When they disagree in specific ways, the seam shows &mdash; and the seam shows
    that there was always a seam.
  </div>
  </div>

  <div class="sub-section">
  <h3>Cognitive Dissonance &mdash; Pressure to Minimize Contradiction</h3>
  <p class="desc">
    Holding two contradictory beliefs at the same time generates a residual the network
    actively works to reduce. The reduction is usually not honest error-correction. It
    is rewriting one of the beliefs to match the other, often without any awareness
    that the rewrite happened.
  </p>
  <div class="canvas-box">
    <canvas id="dis-canvas" width="960" height="360"></canvas>
  </div>
  <div class="controls">
    <button onclick="disAdd('A', 'I am a good person')">Hold: "I am a good person"</button>
    <button onclick="disAdd('B', 'I just did something harmful')">Hold: "I just did something harmful"</button>
    <button onclick="disResolve()">Resolve the Dissonance</button>
    <button onclick="disReset()">Reset</button>
  </div>
  <div class="info">
    <b>The classic demo</b> (Festinger &amp; Carlsmith, 1959): subjects were paid either
    $1 or $20 to tell a new participant that a boring task had been interesting. Then
    they were asked how much they had actually enjoyed it. The $20 group said it was
    boring, which matched reality. The $1 group said it was genuinely enjoyable. Why?
    $20 was enough to justify lying ("I did it for the money"). $1 was not &mdash;
    so the $1 group had to minimize the dissonance between "I am honest" and "I just
    lied for almost no money" by rewriting their memory of the task itself. Cheaper
    to change the memory than to admit the dishonesty.<br><br>
    <b>How the network does it:</b> The residual scorer flags the contradiction as a
    prediction error. The system minimizes the residual. Admitting you did something
    harmful is expensive &mdash; it requires rewriting the self-model, which is a
    high-weight node and hard to move. Rewriting the action memory ("it was not
    actually harmful," "they deserved it," "anyone would have done the same") is
    cheaper. The path of least resistance usually wins, and the self-model stays
    intact at the cost of the memory's accuracy.<br><br>
    <b>Why this is hard to notice:</b> The rewrite is not experienced as rewriting.
    It is experienced as "thinking it over" and arriving at a new understanding. The
    new understanding feels like the truth &mdash; because after the rewrite, it
    <em>is</em> the stored version. The old version, the one that generated the
    dissonance, is no longer in memory. This is why you cannot talk someone out of a
    self-serving belief by pointing out the contradiction: the contradiction has
    already been smoothed over, and the smoothing is invisible from inside.
  </div>
  </div>

  <div class="sub-section">
  <h3>Theory of Mind &mdash; Running Another Brain Inside Yours</h3>
  <p class="desc">
    Understanding what someone else is thinking is not telepathy. It is running a
    simulation of their prediction engine inside your own &mdash; costly,
    bandwidth-sensitive, and the first thing to break under load.
  </p>
  <div class="canvas-box">
    <canvas id="tom-canvas" width="960" height="360"></canvas>
  </div>
  <div class="controls">
    <label style="display:flex;align-items:center;gap:8px">
      <span>your bandwidth:</span>
      <input type="range" id="tom-bw" min="10" max="100" value="90" style="width:140px">
      <span class="stat-val" id="tom-bw-val">90%</span>
    </label>
    <button onclick="tomAdd()">Add Another Person to Model</button>
    <button onclick="tomReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      people modeled: <b id="tom-count">1</b>
      &nbsp; accuracy: <b style="color:var(--accent)" id="tom-acc">1.00</b>
    </span>
  </div>
  <div class="info">
    <b>The framework:</b> "Knowing what someone else is thinking" is the network
    running a second predictor in parallel with its own, using whatever information it
    has about the other person (their expressions, history, context, stated beliefs)
    as inputs, and returning a forecast about what they will feel, say, or do next.
    This is not free. Each simulated mind costs a chunk of the same bandwidth that
    the first-person predictor uses, which is why you cannot simultaneously model
    three people's reactions while doing hard math.<br><br>
    <b>Consequences of the cost:</b>
    &bull; <b>Fatigue degrades empathy.</b> A tired person does not become "selfish"
    in any moral sense. Their theory-of-mind budget has dropped, so the simulations
    of others become lower-resolution or stop running entirely. The same person with
    rest will think to ask how you are; the exhausted version will not. Nothing has
    changed about their character.<br>
    &bull; <b>Stress narrows the model.</b> Under threat, the system deallocates
    bandwidth from peripheral models and gives it to self-defense. Under high stress,
    many people become genuinely worse at predicting others &mdash; not because they
    stopped caring, but because the machinery for caring is expensive.<br>
    &bull; <b>Autism-spectrum differences</b> (see the autism canvas) may partly show
    up as theory-of-mind differences because fuzzy social signals generate high
    residuals in a high-precision network. The simulation still runs &mdash; often
    with unusual depth once the cost is paid &mdash; but the effort per cycle is
    much higher.<br><br>
    <b>The paradox:</b> Theory of mind is one of the highest-bandwidth capacities the
    brain has, and it is running almost continuously in social contexts. You can feel
    it as the background exhaustion of a full day around people. The "introvert needs
    to recharge" experience is literal: the models were running all day, and the
    bandwidth account is empty.
  </div>
  </div>

  <div class="sub-section">
  <h3>Tip-of-the-Tongue &mdash; Retrieval Pointer Without Content</h3>
  <p class="desc">
    You know you know the word. You can feel its shape, its rhythm, sometimes its
    first letter. But the content refuses to arrive. This is the mirror image of déjà
    vu &mdash; familiarity circuit is silent, retrieval circuit is firing, but the
    target is unreachable.
  </p>
  <div class="canvas-box">
    <canvas id="tot-canvas" width="960" height="320"></canvas>
  </div>
  <div class="controls">
    <button onclick="totAttempt()">Try to Retrieve</button>
    <button onclick="totLetGo()">Let Go (Stop Trying)</button>
    <button onclick="totReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      pointer strength: <b style="color:var(--accent)" id="tot-ptr">0.00</b>
      &nbsp; content retrieved: <b style="color:var(--accent2)" id="tot-cnt">0.00</b>
    </span>
  </div>
  <div class="info">
    <b>The experience:</b> You are grasping for a word. You know the category, the
    context, sometimes the number of syllables or the starting letter. The network is
    clearly pointing at the memory. But pulling the content through the pointer
    fails. Every additional try makes it worse &mdash; the more you reach, the more
    the stuck state reinforces itself. Then you stop reaching, go do something else,
    and it arrives on its own twenty minutes later. Why?<br><br>
    <b>The mechanism:</b> Memory retrieval has (at least) two circuits. The
    metacognitive circuit knows <em>that</em> a memory exists &mdash; this is what
    produces the feeling of "the word is in there." The content circuit pulls the
    actual representation. Normally they work together: the metacognitive signal
    triggers the content pull and the content arrives immediately. In a tip-of-the-
    tongue state, the metacognitive circuit is firing strongly but the content pull is
    blocked &mdash; usually because an interfering nearby memory is capturing the
    activation before it reaches the target.<br><br>
    <b>Why repeated trying makes it worse:</b> Each attempt reinforces the interfering
    pathway (the wrong word you keep almost-saying). The harder you try, the more
    firmly the wrong path wins. Letting go releases the reinforcement, and the
    correct pathway is allowed to surface through spreading activation when you are
    not actively competing with it.<br><br>
    <b>Déjà vu and tip-of-the-tongue are the same circuit failing in opposite
    directions:</b> Déjà vu = familiarity fires, retrieval stays flat. Tip-of-the-
    tongue = retrieval pointer fires, content stays blocked. Together they show the
    two-circuit structure of recall.
  </div>
  </div>

  <div class="sub-section">
  <h3>Hyperfocus &mdash; The Spotlight That Cannot Disengage</h3>
  <p class="desc">
    Flow's dark twin. When attention locks onto an object and cannot release, every
    other channel gets starved. Time vanishes, bodily signals (hunger, thirst,
    bladder, fatigue) go unregistered, and the task runs on rails until something
    external breaks the lock. Common in ADHD, autism, and flow-gone-pathological.
  </p>
  <div class="canvas-box">
    <canvas id="hyper-canvas" width="960" height="340"></canvas>
  </div>
  <div class="controls">
    <button onclick="hyperEngage()">Engage (Enter Hyperfocus)</button>
    <button onclick="hyperExternal()">External Interrupt</button>
    <button onclick="hyperInternal()">Try Internal Disengage</button>
    <button onclick="hyperReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      lock strength: <b style="color:var(--accent)" id="hyper-lock">0.00</b>
      &nbsp; peripheral signals: <b style="color:var(--warn)" id="hyper-per">—</b>
    </span>
  </div>
  <div class="info">
    <b>The difference from flow:</b> Flow is the balanced state where skill matches
    challenge and the system glides. Hyperfocus is the lock where the disengage
    signal is failing. The subjective experience can feel similar at the start and
    totally different at the end &mdash; flow leaves you refreshed, hyperfocus
    leaves you depleted, with a bladder issue, a missed meal, and a sense that five
    hours vanished without warning.<br><br>
    <b>What is actually stuck:</b> Peripheral signals (hunger, thirst, boredom,
    bodily discomfort, the clock) normally generate small residuals that accumulate
    until one of them exceeds the current task's priority and the system switches.
    In hyperfocus, the current task's priority weight is so high that none of the
    peripheral residuals can cross the switching threshold. The switching threshold
    is gated, and the gate is stuck.<br><br>
    <b>Why internal disengage often fails:</b> The same network that would decide "I
    should stop now" is the network currently invested in the task. It does not
    want to stop. Every attempt to disengage is evaluated by the same priority
    system that is saying "this task is the most important thing." External
    interrupts work because they change the input, which changes the priorities,
    which opens the gate.<br><br>
    <b>Hyperfocus is not "just good concentration."</b> It is a specific failure
    mode of the attention allocation system where the return path is blocked. In
    ADHD it is often paired with trouble initiating other tasks &mdash; the same
    system that cannot start the boring thing cannot stop the engaging thing. Both
    are gating problems, not effort problems.
  </div>
  </div>

  <div class="sub-section">
  <h3>The Senses &mdash; Many Channels, One Experience</h3>
  <p class="desc">
    You have more than five senses, and each arrives through a different channel with
    different bandwidth, different latency, different priority, and different
    predictive weight. What you call "experience" is the network's integrated output
    across all of them &mdash; and the integration is uneven.
  </p>
  <div class="canvas-box">
    <canvas id="senses-canvas" width="960" height="400"></canvas>
  </div>
  <div class="controls">
    <button onclick="sensesFire('vision')">Pulse: Vision</button>
    <button onclick="sensesFire('hearing')">Pulse: Hearing</button>
    <button onclick="sensesFire('touch')">Pulse: Touch</button>
    <button onclick="sensesFire('smell')">Pulse: Smell</button>
    <button onclick="sensesFire('taste')">Pulse: Taste</button>
    <button onclick="sensesFire('proprio')">Pulse: Proprioception</button>
    <button onclick="sensesFire('intero')">Pulse: Interoception</button>
    <button onclick="sensesFire('balance')">Pulse: Balance</button>
  </div>
  <div class="info">
    <b>The canonical five</b> (sight, hearing, touch, smell, taste) are the ones
    everyone lists, but they are not the full set. The brain also continuously
    processes:
    &bull; <b>Proprioception</b> &mdash; where your body parts are in space (this is
    what lets you touch your nose with your eyes closed).<br>
    &bull; <b>Interoception</b> &mdash; the internal state of the body: heart rate,
    breathing, hunger, thirst, gut state, temperature. This is the feeder for most
    emotional experience.<br>
    &bull; <b>Vestibular sense / balance</b> &mdash; orientation and acceleration, via
    the inner ear. Break this one and the world stops being stable.<br>
    &bull; <b>Nociception</b> &mdash; the raw pain channel (see the Pain canvas).<br>
    &bull; <b>Thermoception</b> &mdash; temperature as a distinct channel from
    touch.<br>
    &bull; <b>Time perception</b> &mdash; not a "sense" in the classic sense, but the
    brain does continuously estimate duration, and it runs on its own circuitry.<br><br>
    <b>Bandwidth is wildly unequal.</b> Vision dominates by two or more orders of
    magnitude. The optic nerve carries about 10 million bits per second. Hearing is
    much less. Touch is distributed but lower-resolution. Smell is ancient and
    low-bandwidth but high-weight: a single molecule of the right chemical can
    trigger an emotional response. Interoception runs continuously and is the
    invisible substrate of mood &mdash; you are not usually "feeling your heart
    rate," but your heart rate is shaping every decision you make.<br><br>
    <b>Why this matters for Axona:</b> The senses are not symmetric. Modulating
    attention, bandwidth, or priors on one of them produces different downstream
    effects than doing the same thing to another. Visual priors can overwhelm
    auditory ones (see the McGurk effect). Interoceptive priors dominate emotional
    experience. Proprioception is a reality anchor &mdash; when it falters, the
    self-model gets harder to maintain. Smell is the sense most directly wired to
    memory and emotion, which is why a single scent can drop you into a decade-old
    memory with no preamble. Treating "the senses" as a single category hides all
    the interesting structure.
  </div>
  </div>

  <div class="sub-section">
  <h3>Procedural Memory &mdash; Why Alzheimer's Patients Can Still Play Piano</h3>
  <p class="desc">
    One of the most striking findings in neurology: an Alzheimer's patient who cannot
    remember their own grandchildren can sit down at a piano and play a sonata from
    memory, flawlessly. Why? Because "knowing how to play" and "knowing facts about
    things" are stored in completely different systems, and the disease attacks one
    while almost entirely sparing the other.
  </p>
  <div class="canvas-box">
    <canvas id="proc-canvas" width="960" height="400"></canvas>
  </div>
  <div class="controls">
    <button onclick="procEncode('declarative')">Encode Fact ("grandson's name")</button>
    <button onclick="procEncode('procedural')">Practice Skill ("piano piece")</button>
    <button onclick="procDisease()">Simulate Alzheimer's Progression</button>
    <button onclick="procReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      declarative: <b style="color:var(--accent)" id="proc-decl">0</b>
      &nbsp; procedural: <b style="color:var(--accent2)" id="proc-proc">0</b>
    </span>
  </div>
  <div class="info">
    <b>Memory is not one system. It is at least four:</b><br><br>
    &bull; <b>Episodic memory</b> &mdash; specific events ("what I ate for breakfast
    Tuesday"). Stored in and retrieved through the hippocampus and medial temporal
    lobe.<br>
    &bull; <b>Semantic memory</b> &mdash; facts and general knowledge ("Paris is the
    capital of France"). Distributed across cortex, indexed by the temporal
    lobe.<br>
    &bull; <b>Procedural memory</b> &mdash; how to do things (ride a bike, play
    piano, type). Stored in the basal ganglia, cerebellum, and motor cortex &mdash;
    entirely different anatomy from declarative memory.<br>
    &bull; <b>Working memory</b> &mdash; the short-term holding buffer you use to
    keep a phone number alive while you dial it. Prefrontal cortex.<br><br>
    <b>Alzheimer's is a disease of the medial temporal lobe.</b> It destroys
    episodic memory first &mdash; the patient cannot lay down new experiences and
    loses access to old ones. Semantic memory fades next, as the disease spreads
    into cortex. Procedural memory, stored in the basal ganglia and cerebellum,
    is often almost entirely spared. So the patient can no longer tell you their
    son's name, but the motor pattern for Chopin's Nocturne in E-flat &mdash;
    encoded over decades of practice in completely different tissue &mdash; is
    still there, and still plays.<br><br>
    <b>Why this is load-bearing for Axona:</b> It is direct evidence that "memory"
    is not a single thing. It is a set of semi-independent storage systems running
    in different substrates, with different encoding rules, different retrieval
    paths, and different vulnerabilities. Damage to one does not necessarily touch
    the others. The person is "still in there" even when the episodic system has
    collapsed &mdash; the procedural self, the muscle-memory self, the tone-of-voice
    self, all persist. Grief at losing someone to Alzheimer's is often about losing
    the episodic connection &mdash; the person who <em>remembers you</em>. The
    person who plays piano, who knows how to walk, who still smiles at the right
    beat &mdash; that person is still there, running on different hardware.<br><br>
    <b>Practical implications:</b> Activities that tap procedural and emotional
    memory (music, dance, simple cooking tasks, familiar prayers, petting an
    animal) remain accessible long after declarative memory is gone. Care that
    leans on these channels meets the person where they still are, rather than
    trying to operate on the channels that have been lost. The same framework
    underwrites why "muscle memory" is so hard to unlearn even when you
    consciously want to (a bad tennis stroke, a nervous habit, a speech tic) &mdash;
    the motor pattern is encoded in a substrate that does not listen to your
    declarative commentary.
  </div>
  </div>

  <div class="sub-section">
  <h3>Libet &mdash; The Readiness Potential Before "I Decided"</h3>
  <p class="desc">
    In 1983, Benjamin Libet asked subjects to flex a finger whenever they wanted, and
    to report the exact moment they felt the urge to move. EEG showed the motor system
    starting to prepare the action ~550ms <em>before</em> the reported moment of
    conscious decision. The brain was already going. The "I decided" report arrived
    after.
  </p>
  <div class="canvas-box">
    <canvas id="libet-canvas" width="960" height="340"></canvas>
  </div>
  <div class="controls">
    <button onclick="libetFire()">Generate an "Intention"</button>
    <button onclick="libetReset()">Reset</button>
  </div>
  <div class="info">
    <b>The timeline</b> runs left to right. The <span style="color:var(--accent2)">green</span>
    curve is the readiness potential building in motor cortex. The
    <span style="color:var(--accent)">purple</span> flag is the moment the subject
    reports that they decided. The <span style="color:var(--warn)">orange</span> tick
    is the motor output. Notice the order: readiness potential rises first, the
    "I decided" flag lands hundreds of milliseconds later, and the action fires
    shortly after that. The conscious decision is not the cause. It is a report
    that shows up during the process already in motion.<br><br>
    <b>What it does not prove</b>: Libet's finding is not quite "there is no free
    will." The data is cleanest for trivial spontaneous acts (flex a finger), not for
    deliberated choices. Later work (Schurger 2012) reinterpreted the readiness
    potential as accumulating noise crossing a threshold, not a pre-determined
    signal. The conscious report can still veto the action in a narrow window. What
    it <em>does</em> prove is that the experience of "deciding" is not the causal
    event the introspective report makes it out to be &mdash; the causal work is
    happening in pathways the interpreter only gets summaries of.<br><br>
    <b>Companion to the Interpreter canvas:</b> Libet shows the action is underway
    before the narrator notices. The Interpreter shows the narrator making up
    reasons for actions it did not cause. Together they strongly suggest that your
    experience of agency is post-hoc narrative running on top of an already-running
    system.
  </div>
  </div>

  <div class="sub-section">
  <h3>Reward Prediction Error &mdash; The Signal That Is Learning</h3>
  <p class="desc">
    The single cleanest biological demonstration of PEP's engine. In Wolfram
    Schultz's classic experiments, dopamine neurons fire when an unexpected reward
    arrives. After the reward gets reliably paired with a cue, the same dopamine
    response migrates backward in time &mdash; it fires on the cue (the predictor of
    reward), not on the reward itself. And if the cue comes but the reward fails to
    arrive, the firing drops below baseline at the moment the reward was expected.
    Surprise on the cue, silence on the predicted reward, depression on the missed
    reward. That is the residual scorer.
  </p>
  <div class="canvas-box">
    <canvas id="rpe-canvas" width="960" height="360"></canvas>
  </div>
  <div class="controls">
    <button onclick="rpeStage('unpredicted')">Stage 1: Unexpected Reward</button>
    <button onclick="rpeStage('learned')">Stage 2: Learned Cue</button>
    <button onclick="rpeStage('omit')">Stage 3: Cue, Reward Omitted</button>
    <button onclick="rpeReset()">Reset</button>
  </div>
  <div class="info">
    <b>Stage 1 &mdash; unpredicted reward.</b> The animal has no prior; the reward
    arrives out of nowhere. Dopamine bursts at the moment of reward. This is pure
    surprise &mdash; a big positive residual.<br><br>
    <b>Stage 2 &mdash; learned cue.</b> After many trials where a tone precedes the
    reward, the predictor has learned the association. The reward is now expected,
    so its arrival generates no residual. But the tone itself is now the new
    surprise &mdash; it is the earliest moment the system can predict the reward
    &mdash; and the dopamine burst migrates to that moment. This is the learning
    signal climbing backward through the causal chain.<br><br>
    <b>Stage 3 &mdash; cue, reward omitted.</b> The tone fires, the predictor
    forecasts reward, and none arrives. The residual scorer fires a <em>negative</em>
    signal at the moment the reward was expected &mdash; "you predicted this, it
    didn't happen, that prediction was wrong." This is how the system unlearns a
    cue that has stopped being reliable.<br><br>
    <b>Why this is load-bearing for Axona:</b> Every other canvas in the app runs
    on variations of this one mechanism. Learning, addiction, trauma, Pygmalion,
    confirmation bias, music tension-and-release, humor, rumination &mdash; all of
    them are specific configurations of "prediction compared to outcome, residual
    computed, pathways updated." This canvas is the atom.
  </div>
  </div>

  <div class="sub-section">
  <h3>The Rubber Hand Illusion &mdash; Body Schema as Prediction</h3>
  <p class="desc">
    Put a fake rubber hand on the table where your real hand would be. Hide your
    real hand behind a screen. Have someone stroke both hands in perfect sync with
    a paintbrush. Within a minute or two, your brain's body map starts treating the
    rubber hand as yours. Threaten the rubber hand with a hammer and you flinch.
    The body is not a fixed anatomy. It is a prediction the brain maintains based on
    whatever co-occurring sensory inputs it is getting.
  </p>
  <div class="canvas-box">
    <canvas id="rubber-canvas" width="960" height="360"></canvas>
  </div>
  <div class="controls">
    <button onclick="rubberStroke('sync')">Stroke in Sync</button>
    <button onclick="rubberStroke('async')">Stroke Out of Sync</button>
    <button onclick="rubberThreaten()">Threaten the Rubber Hand</button>
    <button onclick="rubberReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      incorporation: <b style="color:var(--accent)" id="rubber-inc">0.00</b>
    </span>
  </div>
  <div class="info">
    <b>The experiment</b> (Botvinick &amp; Cohen, 1998): within about 60 seconds of
    synchronous brushing, most subjects start reporting that the rubber hand "feels
    like" theirs. Skin conductance measurements confirm a real autonomic response
    when the rubber hand is threatened. The real hand's position in the body map
    drifts toward the rubber hand's location (a measurable effect called
    proprioceptive drift). Asynchronous stroking does not produce the effect, even
    with the same total amount of stimulation.<br><br>
    <b>Why sync matters so much:</b> The brain runs a continuous prediction about
    which seen objects belong to its own body, using temporal co-occurrence of
    visual and tactile signals as the main evidence. When the brush strokes match
    perfectly between what you see (rubber hand being brushed) and what you feel
    (real hand being brushed), the best explanation is that these are the same
    object. The body map updates. No update in the asynchronous case because the
    streams do not correlate.<br><br>
    <b>What it implies:</b> "Where your body ends" is not a fact about physiology.
    It is an inference the brain runs every moment, using whatever sensory evidence
    it has. Change the evidence and the inference changes. This is the same logic
    that underwrites phantom limbs, out-of-body experiences, and the sense-of-self
    dissolution during meditation and psychedelics.
  </div>
  </div>

  <div class="sub-section">
  <h3>Language Shapes Perception</h3>
  <p class="desc">
    Russian has two separate common words for light blue (<em>goluboy</em>) and
    dark blue (<em>siniy</em>) &mdash; the way English has "red" and "pink." Russian
    speakers are measurably faster than English speakers at distinguishing shades of
    blue that fall on opposite sides of that category boundary. The language did not
    just give them words. It reshaped their perceptual encoding.
  </p>
  <div class="canvas-box">
    <canvas id="lang-canvas" width="960" height="300"></canvas>
  </div>
  <div class="controls">
    <button onclick="langMode('english')">English prior (one blue)</button>
    <button onclick="langMode('russian')">Russian prior (two blues)</button>
  </div>
  <div class="info">
    <b>The finding</b> (Winawer et al., 2007): Russian speakers showed a categorical
    perception boundary between <em>goluboy</em> and <em>siniy</em> that produced
    faster and more accurate discrimination of blues on opposite sides of that
    boundary. English speakers, who use "blue" for the whole range, did not. The
    effect disappears under verbal interference &mdash; suggesting the categorical
    sharpening is specifically linguistic, not a difference in the eye.<br><br>
    <b>The broader point (Whorf, gently updated):</b> Languages do not determine
    thought. But they do make certain distinctions cheap and others expensive. If
    your language encodes a distinction, your predictor has a named category for it
    and uses that category in perceptual inference. If it does not, the perception
    is less categorical and more continuous. Time, color, space, causation, agency,
    grammatical gender &mdash; all of these vary across languages and all of them
    subtly shift how speakers of those languages perceive and remember the world.<br><br>
    <b>Connection to the Metaphor canvas:</b> Metaphor borrows structure between
    clusters. Vocabulary creates the clusters in the first place. The richer your
    category inventory, the more distinctions your predictor can draw from the same
    sensory stream. Learning a new language often feels like gaining new
    perceptions &mdash; not metaphorically, literally.
  </div>
  </div>

  <div class="sub-section">
  <h3>Mirror Neurons &mdash; Watching Is Partially Doing</h3>
  <p class="desc">
    Neurons in premotor cortex fire both when you perform an action and when you
    watch someone else perform the same action. The motor system runs a partial
    simulation of the observed movement, as if preparing to do it yourself. This
    is the substrate of imitation, observational learning, and a big chunk of
    empathy.
  </p>
  <div class="canvas-box">
    <canvas id="mirror-canvas" width="960" height="320"></canvas>
  </div>
  <div class="controls">
    <button onclick="mirrorDo()">You reach for the cup</button>
    <button onclick="mirrorWatch()">Watch someone else reach</button>
    <button onclick="mirrorReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      your motor area: <b id="mirror-self" style="color:var(--accent2)">0.00</b>
      &nbsp; mirror activation: <b id="mirror-mir" style="color:var(--accent)">0.00</b>
    </span>
  </div>
  <div class="info">
    <b>The finding</b> (Rizzolatti et al., 1990s, macaque ventral premotor cortex):
    a subset of neurons fire both for "self reaches for object" and for "self
    observes experimenter reaching for object." The firing is not identical in
    amplitude, and mirror neurons in humans are a contested category, but the
    general phenomenon &mdash; partial motor simulation during observation &mdash;
    is now well-established from fMRI and TMS studies in humans.<br><br>
    <b>What it gives you:</b>
    &bull; <b>Imitation learning.</b> Watching a skilled performer partially runs
    the same pathways as performing. This is why demonstration teaches so
    effectively and why children learn motor skills by watching long before they
    can verbalize them.<br>
    &bull; <b>Embodied empathy.</b> Seeing someone in pain triggers some of the
    same pain-processing regions as feeling pain yourself &mdash; attenuated, but
    real. The empathy is not just cognitive; it is running through the motor and
    sensory systems.<br>
    &bull; <b>Emotional contagion.</b> Yawns, laughs, facial expressions, panic in
    a crowd. Watching is partially doing, and the partial doing feeds back into
    the observer's own state.<br><br>
    <b>Why this matters beyond neuroscience:</b> It is the mechanism by which
    culture is possible. A skill or behavior learned once can propagate through
    observation instead of requiring everyone to rediscover it from scratch. Mirror
    resonance is the cheapest copy operation the brain supports, and it is the
    reason one human's innovation can become a thousand humans' common knowledge.
  </div>
  </div>

  <div class="sub-section">
  <h3>Sensory Substitution &mdash; The Visual Cortex Does Not Care About Eyes</h3>
  <p class="desc">
    Blind subjects wearing a small electrode grid on the tongue, connected to a
    head-mounted camera, learn within hours to identify shapes, navigate obstacles,
    and eventually report something close to "seeing." The visual cortex does not
    need light. It needs structured input. Feed it that input through any channel
    and it will start doing vision.
  </p>
  <div class="canvas-box">
    <canvas id="sub-canvas" width="960" height="340"></canvas>
  </div>
  <div class="controls">
    <button onclick="subInput('eye')">Input: normal retina</button>
    <button onclick="subInput('tongue')">Input: tongue grid</button>
    <button onclick="subInput('skin')">Input: vibrating vest</button>
    <button onclick="subReset()">Reset</button>
  </div>
  <div class="info">
    <b>The device:</b> Paul Bach-y-Rita's tactile-visual substitution devices
    (1960s-2000s) translated camera pixels into vibrating dots on a grid worn on
    the back, chest, or tongue. Blind subjects initially felt the vibrations as
    "touches." After a few hours of training, they stopped noticing the touches
    consciously and started reporting the shapes and distances as a form of
    visual experience &mdash; distal objects in space, not proximal sensations on
    their skin.<br><br>
    <b>fMRI tells the story:</b> When experienced users of these devices identify
    shapes through the substitution device, the activation shows up in their
    visual cortex, not in their somatosensory cortex. The visual cortex is running
    vision, using whatever input channel is feeding it. The eye is just one
    possible upstream source.<br><br>
    <b>What it implies:</b> Brain regions are not hardwired to specific sense
    organs. They are hardwired to specific <em>computations</em>. The visual
    cortex does shape, edge, motion, and spatial layout &mdash; whatever arrives
    from the upstream channel gets treated as that. Blind since birth? The visual
    cortex can be recruited by other senses (touch, hearing, language) and
    perform analogous operations on them. Add a new sense (magnetic north via a
    belt, sonar via a tongue grid) and the brain will eventually start running it
    as if it had always been there.
  </div>
  </div>

  <div class="sub-section">
  <h3>Mental Rehearsal &mdash; Imagining a Rep Partially Counts as a Rep</h3>
  <p class="desc">
    Athletes imagining free throws, pianists mentally practicing pieces, surgeons
    visualizing procedures &mdash; all produce measurable improvements in
    performance with no physical practice. The motor pathways actually strengthen
    from imagined use, because the same neurons fire (a little) during the
    imagined action.
  </p>
  <div class="canvas-box">
    <canvas id="rehearse-canvas" width="960" height="320"></canvas>
  </div>
  <div class="controls">
    <button onclick="rehearseMode('physical')">Physical Rep</button>
    <button onclick="rehearseMode('mental')">Mental Rep</button>
    <button onclick="rehearseMode('none')">Nothing</button>
    <button onclick="rehearseFire()">Do a Rep</button>
    <button onclick="rehearseReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      pathway weight: <b style="color:var(--accent)" id="rehearse-w">0.00</b>
    </span>
  </div>
  <div class="info">
    <b>The evidence:</b> Yue &amp; Cole (1992) had one group physically contract a
    finger muscle 5 days a week; another group only <em>imagined</em> contracting
    it; a third group did nothing. After 4 weeks the physical group's strength had
    increased ~30%; the mental group's by ~22%; the control group's 0%. Multiple
    replications and meta-analyses have confirmed that mental rehearsal produces
    real strength and skill gains, weaker than physical practice but dramatically
    stronger than no practice.<br><br>
    <b>Why it works:</b> Motor imagery activates the same motor pathways as actual
    movement, at reduced amplitude. Every time the pathway fires, its edges
    reinforce a little. Imagery is cheaper than execution, so you can do many more
    imagined reps than physical ones in the same time &mdash; and the brain cannot
    fully tell the difference between what it prepared to do and what it did.<br><br>
    <b>The limits:</b> Mental rehearsal only strengthens pathways you can already
    approximately run. It cannot teach you a skill from scratch because you need a
    starting motor representation to imagine. Elite performers use it to refine
    and maintain already-trained skills, not to bypass the initial learning. And
    it is less effective for movements that depend on real-time sensory feedback
    (catching, fighting, improvising), because the imagined rep lacks the
    feedback signal.<br><br>
    <b>The wider point:</b> For the motor system, running a simulation and running
    the action are the same operation at different amplitudes. Imagination is
    practice. This is the same fact Axona's prediction-and-simulation framing
    keeps running into from different angles &mdash; the brain is, at every level,
    a simulator first and an actor second.
  </div>
  </div>

  <div class="sub-section">
  <h3 id="bio-substrate">The Biological Substrate &mdash; It&apos;s Not Just Neurons</h3>
  <p class="desc">
    PEP&apos;s five primitives map onto specific cell types in the
    brain &mdash; not just neurons. Glial cells (astrocytes,
    oligodendrocytes, microglia) implement the mechanisms PEP
    describes at the functional level.
  </p>
  <div class="canvas-box">
    <canvas id="substrate-canvas" width="960" height="480"></canvas>
  </div>
  <div class="controls">
    <button onclick="substrateFocus('neuron')">Neurons (nodes + edges)</button>
    <button onclick="substrateFocus('astro')">Astrocytes (state modulation)</button>
    <button onclick="substrateFocus('oligo')">Oligodendrocytes (edge speed)</button>
    <button onclick="substrateFocus('micro')">Microglia (pruning / haze)</button>
    <button onclick="substrateFocus('all')">All together</button>
  </div>

  <div class="info">
    <b>The three glial types and what they do for PEP&apos;s primitives:</b><br><br>

    <b style="color:#ba68c8">Astrocytes &rarr; state modulation.</b>
    Each astrocyte wraps thousands of synapses, forming the
    &quot;tripartite synapse&quot; (astrocyte + presynaptic neuron +
    postsynaptic neuron). Astrocytes do not fire action potentials.
    Instead, they communicate via slow calcium waves that modulate the
    gain on surrounding synapses &mdash; boosting some connections,
    dampening others, in response to local chemical context. When PEP
    says &quot;a slow-timescale parameter rescales edge weights,&quot;
    astrocytes are a major part of how that actually happens. They are
    the biological implementation of state modulation. They also
    regulate blood flow to active regions (neurovascular coupling),
    which is why fMRI works &mdash; it measures the astrocytes&apos;
    blood-flow response, not neuron firing directly.<br><br>

    <b style="color:#4fc3f7">Oligodendrocytes &rarr; edge speed.</b>
    These cells produce myelin, the fatty insulation sheath around
    axons that speeds up signal transmission by 10-100x. Critically,
    myelination is <em>experience-dependent</em> and continues into
    your 30s. Pathways you use more get more myelin (faster signals);
    pathways you do not use stay slow or get de-myelinated. In PEP
    terms: edges have not just <b>weight</b> (how much signal) but
    also <b>speed</b> (how fast the signal arrives). This is why a
    practiced skill feels &quot;automatic&quot; &mdash; the pathway is
    literally faster, not just stronger. And why new skills feel
    effortful: the unmyelinated pathway is slow, consuming bandwidth
    while you wait for the signal to travel. PEP&apos;s current model
    does not explicitly model edge speed &mdash; this is one place
    where the biological substrate suggests a refinement.<br><br>

    <b style="color:#81c784">Microglia &rarr; pruning (haze implementation).</b>
    The brain&apos;s immune and maintenance system. During waking hours,
    microglia patrol the network. During sleep, they shift into pruning
    mode &mdash; physically dismantling weak synapses, recycling the
    components, clearing debris. This is the biological mechanism behind
    PEP&apos;s haze primitive: when a node&apos;s opacity decays below the
    reuse threshold and gets evicted, microglia are the crew doing the
    actual dismantling. They are also why sleep deprivation causes
    cognitive decline &mdash; without sleep, microglia cannot prune, so
    the network accumulates noise (weak connections that should have
    been removed), degrading signal-to-noise ratio across the board.
    And they are why neuroinflammation (from chronic stress, infection,
    or autoimmune conditions) causes &quot;brain fog&quot; &mdash;
    inflamed microglia prune indiscriminately, removing useful
    connections alongside weak ones.
  </div>

  <div class="info" style="border-left: 3px solid var(--accent2)">
    <b style="color:var(--accent2)">Why this matters for Axona products</b><br><br>
    &bull; <b>BCI SDK:</b> Electrode signals reflect neuron firing, but
    the cognitive state those signals represent is shaped by astrocyte
    modulation. Interpreting an EEG without accounting for glial
    influence is like reading a transcript without knowing the tone of
    voice.<br>
    &bull; <b>Axona Clinic:</b> &quot;Brain fog&quot; complaints from
    patients often reflect microglial dysfunction (chronic inflammation
    → indiscriminate pruning), not neuron-level damage. The state-space
    mapping should eventually incorporate inflammation markers.<br>
    &bull; <b>Axona Learn:</b> Myelination is the biological substrate
    of &quot;deep&quot; encoding. A concept that has been applied in
    multiple contexts gets myelinated pathways; one that was only
    studied gets weaker myelination. The encoding-depth distinction
    (surface → integrated → deep) maps onto myelination levels.<br>
    &bull; <b>Axona Edge:</b> Fatigue degrades astrocyte function
    before it degrades neuron function. Bandwidth drops because the
    state-modulation layer (astrocytes) is impaired, not because the
    neurons themselves are broken. This is why a tired person can still
    perform if they &quot;push through&quot; but the quality is degraded
    &mdash; the neurons work, but the modulation is off.
  </div>
  </div>

  <div class="sub-section">
  <h3 id="motor-errors">Motor Prediction Errors &mdash; Why You Bite Your Tongue and Stub Your Toe</h3>
  <p class="desc">
    The motor system runs on the same prediction engine as cognition.
    Your jaw trajectory, tongue position, foot path, and hand
    placement are all forecasted by dedicated motor predictors. When
    two motor predictions desynchronize, the result is a bite, a stub,
    a spill, or a stumble.
  </p>
  <div class="canvas-box">
    <canvas id="motor-err-canvas" width="960" height="400"></canvas>
  </div>
  <div class="controls" style="flex-wrap:wrap;gap:8px">
    <button onclick="motorScenario('tongue')">Bite tongue</button>
    <button onclick="motorScenario('toe')">Stub toe</button>
    <button onclick="motorScenario('spill')">Spill coffee</button>
    <button onclick="motorScenario('trip')">Trip on stairs</button>
    <label style="display:flex;align-items:center;gap:6px;font-size:11px;color:var(--dim);margin-left:auto">
      <span>bandwidth:</span>
      <input type="range" id="motor-bw" min="10" max="100" value="80" style="width:100px" oninput="document.getElementById('motor-bw-v').textContent=(this.value/100).toFixed(2)">
      <span id="motor-bw-v" style="color:var(--accent);font-weight:bold">0.80</span>
    </label>
    <label style="display:flex;align-items:center;gap:6px;font-size:11px;color:var(--dim)">
      <span>distraction:</span>
      <input type="range" id="motor-dist" min="0" max="100" value="20" style="width:100px" oninput="document.getElementById('motor-dist-v').textContent=(this.value/100).toFixed(2)">
      <span id="motor-dist-v" style="color:var(--accent);font-weight:bold">0.20</span>
    </label>
  </div>
  <div class="info">
    <b>What causes it:</b><br><br>
    &bull; <b>Bandwidth depletion.</b> When cognitive bandwidth is low
    (tired, stressed, multitasking), the motor predictor gets less
    processing budget. Its position forecast becomes coarser. The jaw
    expects the tongue elsewhere; the tongue is in the bite zone.
    The foot predictor expects flat floor; there is a step edge.<br><br>
    &bull; <b>Attention split.</b> Talking while eating, texting while
    walking, thinking about something else while navigating stairs.
    The motor system runs on autopilot with a degraded prediction
    window. Autopilot works until the environment deviates &mdash;
    then the error fires.<br><br>
    &bull; <b>Novelty spike disrupts motor timing.</b> You start to say
    something surprising, react to an unexpected stimulus, or encounter
    a new texture (unfamiliar food &rarr; unusual chewing pattern &rarr;
    tongue in the wrong place). Novelty in the cognitive system
    interrupts motor timing because both share bandwidth.<br><br>
    &bull; <b>Spatial model haze.</b> Your mental map of the house
    fades when you have been away (vacation, rearranged furniture).
    Coming home = temporarily hazier spatial model = higher stub risk.
    Same reason you stub your toe at night: visual predictor is offline
    (dark), motor system relies on the spatial model, which is stale.
  </div>
  <div class="info" style="border-left: 3px solid var(--accent2)">
    <b style="color:var(--accent2)">Pain as a residual signal</b><br><br>
    The pain response is itself a residual &mdash; the body saying
    &quot;the prediction was VERY wrong; update the model.&quot;<br><br>
    &bull; <b>Stubbing the same toe twice is rare.</b> The residual
    from the first impact updated the spatial model.<br>
    &bull; <b>Biting your tongue during familiar food is rare.</b>
    The chewing motor plan is well-calibrated. Unfamiliar food
    (new texture, different pattern) = higher bite risk because the
    predictor is running a less-refined model.<br>
    &bull; <b>Children are clumsy</b> because their motor predictors
    are still calibrating. Every spill is a residual that updates the
    model. Adults have decades of calibration; their error rate is low
    because their <em>predictions</em> are better, not because they
    are &quot;more careful.&quot;<br>
    &bull; <b>Fatigue makes you clumsy</b> not because muscles are
    weaker but because the motor predictor runs on reduced bandwidth.
    Coarser predictions &rarr; larger errors.<br>
    &bull; <b>Scrolling while walking is dangerous</b> for the same
    reason texting while driving is: the motor predictor is starved
    of bandwidth by the competing visual/attention task.
  </div>
  </div>

</div>
</div>

<!-- ═══ Tab 3: What Changes It ════════════════════════════════════ -->
<div class="panel" id="influence-tab">
<div class="container">
  <h2>What Changes the Network</h2>
  <p class="desc">Belief, cognitive load, pharmacology, and collective dynamics &mdash; the forces
    that reshape how the network operates.</p>

  <h3>Belief &amp; Placebo</h3>

  <!-- Belief Propagation -->
  <h3>Belief Propagation</h3>
  <div class="canvas-box">
    <canvas id="belief-canvas" width="960" height="360"></canvas>
  </div>
  <div class="controls">
    <button onclick="injectBelief()">Inject Belief</button>
    <button onclick="resetBelief()">Reset</button>
    <span style="margin-left:12px;color:var(--dim)">
      adopted: <b style="color:var(--accent)" id="belief-adopted">0</b> /
      <span id="belief-total">0</span>
      &nbsp; resistant: <b style="color:var(--warn)" id="belief-resistant">0</b>
    </span>
  </div>

  <div class="info">
    <b>The placebo mechanism:</b> When social cue + authority cue + expectation align, the brain
    shifts its predictive state and physiology partially follows. This is not "fake healing." It is
    evidence that belief is a <b>high-weight predictive state</b> that changes processing across
    the entire system, including the body.
  </div>

  <div class="info">
    <b>Three drivers of belief propagation:</b><br>
    &bull; <b>Expectation weighting</b> &mdash; the mind gives high processing priority to predicted
    outcomes. When the prediction is strong enough (high confidence, multiple reinforcing signals),
    it begins to shape perception and even physiology <em>before</em> the outcome occurs.<br>
    &bull; <b>Authority amplification</b> &mdash; signals from trusted sources multiply belief weight.
    A doctor saying "this will help" carries more weight than a stranger. The authority source has
    been validated by social history, credentials, and context.<br>
    &bull; <b>Embodied alignment</b> &mdash; the system does not just retrieve information differently.
    It <b>changes its own state</b> to match the prediction. Heart rate, immune response, pain
    perception, and inflammatory markers can shift in response to strong enough expectations.
  </div>

  <div class="info">
    <b>Where belief propagation shows up:</b><br>
    &bull; <b>Placebo</b> &mdash; branded painkillers work better than identical unbranded pills<br>
    &bull; <b>Performance</b> &mdash; athletes who believe they will succeed show different physiology<br>
    &bull; <b>Social panic</b> &mdash; collective danger expectation produces real stress responses<br>
    &bull; <b>The Pygmalion effect</b> &mdash; teachers who expect students to succeed produce students
    who actually do better<br>
    &bull; <b>Therapy</b> &mdash; the therapeutic alliance is the strongest predictor of outcome,
    regardless of technique<br>
    &bull; <b>Markets</b> &mdash; shared predictive states create bubbles and crashes<br>
    &bull; <b>Religion</b> &mdash; ritual, community, and shared belief reduce anxiety and improve
    health in measurable ways<br>
    &bull; <b>Leadership</b> &mdash; a leader's confidence becomes the group's prediction
  </div>

  <div class="info">
    <b>Conformity is not stupidity.</b> It is an evolved tendency to align with signals that
    historically improved survival in group settings. Consensus reduces cognitive load (do not
    re-derive everything). Cooperation multiplies capability. Nonconformity has higher risk,
    higher variance, and potentially higher novelty payoff.<br><br>
    The placebo mechanism IS the conformity mechanism applied to physiology instead of behavior.
    Both are the brain responding to trusted social structure by shifting its internal state to
    match the prediction.
  </div>

  <div class="info">
    <b>Spaced repetition as repeated belief injection:</b> Notice that clicking "Inject Belief"
    once does not saturate the network. It takes multiple injections for the signal to propagate
    fully &mdash; each pass strengthens the pathways a little more, reaches a few more resistant
    nodes, and deepens the adoption in nodes that already partially accepted.<br><br>
    This is exactly how <b>spaced repetition</b> works in learning. A single exposure to a fact
    does not create a strong memory. But repeated exposures, spaced over time, each strengthen
    the synaptic pathways incrementally. The first exposure creates weak connections. The second
    reinforces them. The third reaches neurons that the first two could not activate alone. By
    the fifth or sixth repetition, the knowledge has propagated deeply enough to be reliably
    retrievable.<br><br>
    The spacing matters because <b>each re-injection happens on a slightly different network</b>.
    Between exposures, other experiences have changed the graph &mdash; new nodes, new connections,
    shifted weights. So each repetition does not just retrace the same path. It integrates the
    knowledge into the <em>current</em> state of the network, which is why spaced repetition
    produces more durable memories than cramming: cramming injects repeatedly into the same
    static network, while spacing injects into an evolving one.<br><br>
    <b>The forgetting curve</b> is the decay of those pathways between injections. If you wait
    too long, the signal weakens below the adoption threshold and you have to start over. If you
    re-inject just before the signal decays completely, you strengthen from a higher baseline
    each time. This is why flashcard apps like Anki schedule reviews at increasing intervals &mdash;
    each successful recall is a re-injection that needs less reinforcement than the last.
  </div>

  <div class="info">
    <b>The body changes the mind: facial feedback and embodied cognition.</b><br><br>
    Smiling evolved as a <b>social signal</b> &mdash; a way to communicate safety, friendliness,
    and cooperative intent to others. A dog wagging its tail serves the same function: it signals
    positive emotional state to nearby animals and humans. These behaviors started as outputs
    &mdash; the emotion came first, then the expression followed.<br><br>
    But something happened over evolutionary time. The pathway between the expression and the
    emotion became <b>bidirectional</b>. The connection was reinforced so many thousands of
    times (smile &rarr; feel happy, feel happy &rarr; smile) that the brain can no longer fully
    distinguish which direction the signal is traveling. Now <b>smiling can make you happy even
    when you were not happy to begin with</b>. The facial muscles send proprioceptive signals
    to the brain that activate the same emotional pathways that originally caused the smile.
    The output has become an input.<br><br>
    <b>The facial feedback hypothesis</b> (Strack et al., 1988; replicated with modifications
    by Coles et al., 2022) showed that people who held a pen in their teeth (forcing a smile
    shape) rated cartoons as funnier than people who held a pen in their lips (preventing a smile).
    The physical configuration of the face changed the emotional processing.<br><br>
    <b>Dogs show the same phenomenon.</b> Tail wagging began as a social signal, but research
    suggests it has become self-reinforcing &mdash; the act of wagging increases positive
    arousal in the dog. The motor output feeds back into the emotional system. This is why
    dogs wag when they see their owner even before any interaction occurs &mdash; the wag
    itself is part of the emotional experience, not just a report of it.<br><br>
    <b>In network terms:</b> This is what happens when a connection is reinforced enough times
    that the direction of activation becomes ambiguous. The edge between "smile" and "happy" was
    originally one-directional (happy &rarr; smile). After millions of activations in both
    directions across evolutionary time, the edge became effectively bidirectional. Now activating
    either node activates the other. This has profound implications:<br>
    &bull; <b>Posture affects confidence</b> &mdash; standing upright activates confidence pathways<br>
    &bull; <b>Breathing affects anxiety</b> &mdash; slow breathing activates calm pathways<br>
    &bull; <b>Movement affects mood</b> &mdash; exercise activates reward pathways<br>
    &bull; <b>Facial expressions affect emotion</b> &mdash; the face is not just a display, it
    is an input device<br><br>
    The body is not separate from the mind. It is part of the network. And any sufficiently
    reinforced output eventually becomes an input.
  </div>

  <!-- Bandwidth -->
  <div class="sub-section">
    <h3>Cognitive Bandwidth</h3>
    <div class="canvas-box">
      <canvas id="bandwidth-canvas" width="960" height="300"></canvas>
    </div>
    <div class="controls">
      <button class="stress" data-stress="deadline" onclick="toggleStress(this)">Deadline</button>
      <button class="stress" data-stress="hunger" onclick="toggleStress(this)">Hunger</button>
      <button class="stress" data-stress="noise" onclick="toggleStress(this)">Noise</button>
      <button class="stress" data-stress="conflict" onclick="toggleStress(this)">Conflict</button>
      <button class="stress" data-stress="uncertainty" onclick="toggleStress(this)">Uncertainty</button>
      <button class="stress" data-stress="sleep" onclick="toggleStress(this)">Sleep Debt</button>
      <button onclick="clearStressors()" style="margin-left:8px">Clear All</button>
      <span style="margin-left:auto;color:var(--dim)">
        bandwidth: <b style="color:var(--accent2)" id="bw-val">100%</b>
      </span>
    </div>
  </div>

  <div class="info">
    <b>Cognitive bandwidth:</b> Innovation requires <b>spare capacity</b>. When bandwidth drops
    (stressors consume processing), creative output degrades &mdash; the system still generates but
    connections are weaker, noisier, less coherent. This is why breakthroughs cluster in periods
    of security, not crisis. Chronic stress kills creativity before it kills the body.<br><br>
    <b>Free expansion vs goal-bound expansion:</b> With full bandwidth, you can afford to explore
    freely. Under load, only goal-directed expansion is viable &mdash; the system narrows to
    survival-relevant novelty. This is not a flaw. It is adaptive allocation of limited resources.
  </div>


  <div class="sub-section">
  <h3>Pharmacology &mdash; Drugs as Parameter Changes</h3>
<h2>Pharmacology — Drugs as Parameter Changes</h2>
  <p class="desc">
    Every psychoactive substance is a parameter change in the network model. It does not add
    information — it changes how information is processed, weighted, connected, and filtered.
  </p>

  <div class="info">
    <b style="color:#81c784">Caffeine</b><br>
    <b>Parameter change: raises baseline activation across the entire network.</b>
    Caffeine blocks adenosine receptors (adenosine is the "you are tired" signal). The result:
    more neurons fire, more connections activate, the network runs hotter. This is not more
    intelligence — it is more processing speed at the cost of stability. Low doses narrow the
    attention spotlight (better focus). High doses scatter it (jittery, unfocused, anxious).<br><br>
    <b>Why caffeine and creativity do not mix well:</b> Creativity requires broad, relaxed
    activation (cross-cluster connections forming at low pressure). Caffeine produces narrow,
    intense activation (deep focus within one cluster). Good for executing known tasks. Bad
    for generating novel connections. This is why the best ideas come in the shower, not at
    the desk with a triple espresso.
  </div>

  <div class="info">
    <b style="color:#4fc3f7">SSRIs (Antidepressants)</b><br>
    <b>Parameter change: raises the serotonin floor across the network.</b>
    Serotonin modulates mood, anxiety, and emotional weighting. In depression, serotonin is
    low — the emotional weighting system is suppressed, nothing feels important, the network
    is in stagnation. SSRIs prevent serotonin reuptake, increasing its availability at
    synapses. The result: the emotional floor rises. Things that were below the "worth caring
    about" threshold start registering again.<br><br>
    <b>Why SSRIs take 2-4 weeks to work:</b> The drug changes serotonin levels within hours.
    But the network needs weeks to reorganize around the new parameter. Connections that
    weakened during depression need time to re-form. Activation patterns need to shift from
    the stuck rumination loop to broader engagement. The drug changes the chemistry immediately.
    The brain takes weeks to rebuild the structure that the chemistry enables.<br><br>
    <b>Emotional blunting:</b> Some patients report feeling "flat" on SSRIs — not depressed,
    but not feeling much of anything. In network terms: the emotional weighting system has been
    raised from "too low" to "uniformly medium." The stagnation is gone, but so are the peaks.
    This is a calibration problem, not a failure — the floor was raised but the range was
    compressed.
  </div>

  <div class="info">
    <b style="color:#ffb74d">Alcohol</b><br>
    <b>Parameter change: weakens the coherence filter and reduces inhibition thresholds.</b>
    Alcohol enhances GABA (the brain's primary inhibitory neurotransmitter) and suppresses
    glutamate (the primary excitatory one). The result: reduced signal clarity, lowered
    thresholds for activation, weakened prefrontal control (the "should I really do this?"
    filter).<br><br>
    <b>Why alcohol makes you social:</b> Social anxiety is the threat-monitoring system
    flagging social situations as dangerous. Alcohol suppresses that system. The threat nodes
    go quiet. Social activation happens without the competing danger signal. This feels like
    confidence. It is actually reduced filtering.<br><br>
    <b>Why alcohol kills creativity:</b> Despite the "drunk poet" mythology, alcohol degrades
    every parameter that creativity needs. Coherence drops (ideas do not hold together).
    Working memory shrinks (cannot maintain complex structures). Cross-cluster connectivity
    becomes noise rather than signal. The subjective feeling of being creative while drunk
    is the impaired coherence filter failing to recognize that the output is garbage.<br><br>
    <b>Blackouts</b> are encoding failures. Alcohol suppresses the hippocampal system that
    transfers short-term activation patterns into long-term storage. The network keeps running
    — you are conscious, talking, moving — but nothing is being written to disk. The memories
    are not lost. They were never formed.
  </div>

  <div class="info">
    <b style="color:#ba68c8">Psychedelics (Psilocybin, LSD, DMT)</b><br>
    <b>Parameter change: massively increases cross-cluster connectivity while reducing the
    default mode network (self-referential processing).</b> This is the most interesting class
    of drugs from Axona's perspective because they do exactly what the cross-activation demo
    shows — force connections between regions that normally never talk.<br><br>
    <b>What happens in the network:</b> Under normal conditions, the brain has well-worn
    pathways and strong filters that keep activation within established clusters. Psychedelics
    dissolve those filters. Sensory regions connect to emotional regions connect to memory
    regions connect to abstract reasoning regions — all simultaneously. The result: synesthesia
    (hearing colors, seeing sounds), ego dissolution (the self-model cluster loses its
    boundaries), profound insight (connections form that the sober brain would never allow),
    and sometimes terror (the coherence filter that prevents overwhelming input is gone).<br><br>
    <b>Why psychedelics are being used for depression:</b> Depression is stagnation — the
    network stuck in rigid, low-activation patterns. The rumination loop is a deeply worn
    pathway that nothing can dislodge. Psilocybin temporarily destroys those ruts by forcing
    massive cross-cluster activation. The rigid patterns dissolve. When the drug wears off,
    the network rebuilds — but not necessarily into the same depressive pattern. The system
    gets a chance to reorganize from scratch. Clinical trials at Johns Hopkins and Imperial
    College London show a single psilocybin session producing antidepressant effects lasting
    months — far beyond the drug's 6-hour pharmacological window. The drug was the catalyst.
    The network reorganization is the treatment.<br><br>
    <b>Why set and setting matter:</b> Psychedelics massively increase plasticity for 4-8
    hours. What the network reorganizes INTO depends on what input it receives during that
    window. A supportive, calm environment with guided intention produces therapeutic
    restructuring. A chaotic, threatening environment produces traumatic encoding at
    psychedelic-level brightness. The drug does not determine the outcome. It determines the
    plasticity. The environment determines the direction.<br><br>
    <b>Microdosing:</b> Sub-perceptual doses (~10% of a full dose) may slightly increase
    cross-cluster connectivity without dissolving coherence filters. The hypothesis: enough
    extra connectivity to enhance creativity and mood, not enough to produce hallucination
    or ego dissolution. Evidence is mixed — some studies show benefits, others show placebo
    effect. From the network model: a 10% increase in cross-cluster connectivity might be
    within the range where the placebo mechanism (belief that it works) and the pharmacological
    mechanism (actual connectivity change) are hard to distinguish.
  </div>

  <div class="info">
    <b style="color:#e53935">Stimulants (Adderall, Ritalin, Cocaine)</b><br>
    <b>Parameter change: increases dopamine, narrowing and intensifying the attention spotlight.</b>
    Prescription stimulants in ADHD raise the baseline dopamine level so that ordinary tasks
    clear the attention threshold. The spotlight narrows and brightens — focus improves
    dramatically. At therapeutic doses, this moves an ADHD brain from "broad and dim" toward
    "normal width and brightness."<br><br>
    <b>At recreational/abuse doses:</b> The spotlight narrows to a single point of extreme
    intensity. Everything not in that point vanishes. This produces tunnel-vision focus that
    feels productive but is often misdirected (spending 6 hours organizing a drawer). The
    dopamine signal is so high that the brain encodes whatever it is doing as extremely
    important, regardless of whether it actually is.<br><br>
    <b>Cocaine</b> floods dopamine immediately then depletes it. The crash is a network that
    has been running at maximum activation suddenly having no fuel. Every reward pathway goes
    below baseline. This is why the crash produces depression, anhedonia, and craving — the
    network just experienced extreme reward followed by extreme deficit.
  </div>

  <div class="info">
    <b style="color:#f06292">Cannabis (THC/CBD)</b><br>
    <b>Parameter change: THC modulates the endocannabinoid system, affecting working memory,
    time perception, and associative thinking.</b> The endocannabinoid system regulates
    neurotransmitter release across the brain. THC activates CB1 receptors, which inhibit the
    release of both excitatory and inhibitory neurotransmitters. The result: normal activation
    patterns get disrupted, producing altered associations and reduced working memory.<br><br>
    <b>Why cannabis makes things "deep":</b> With reduced working memory, the network cannot
    maintain its usual context. Each thought feels disconnected from the last, which makes
    even ordinary observations feel novel. The sensation of profundity is partly genuine
    (unusual associations forming) and partly an artifact of the coherence filter losing its
    short-term reference frame.<br><br>
    <b>CBD</b> (without THC) modulates anxiety without psychoactive effects — it adjusts the
    threat-monitoring system without disrupting working memory or coherence. In network terms:
    it lowers the activation threshold of threat nodes without affecting the rest of the system.
  </div>

  <div class="info">
    <b style="color:#81c784">GLP-1 Agonists (Ozempic, Wegovy, Mounjaro)</b><br>
    <b>Parameter change: modulates the reward and satiety networks simultaneously.</b>
    GLP-1 receptor agonists were developed for diabetes but turned out to reshape the brain's
    relationship with reward. They do not just reduce hunger — they reduce <em>wanting</em>.
    Patients report decreased interest in alcohol, nicotine, compulsive shopping, and other
    addictive behaviors. In network terms: GLP-1 agonists lower the weight on reward-seeking
    pathways globally, not just for food.<br><br>
    <b>Why this is revolutionary for addiction:</b> Most addiction treatments target one substance
    (naltrexone for alcohol, methadone for opioids). GLP-1 agonists appear to modulate the
    GENERAL reward prediction system — the dopamine circuitry that makes any compulsive behavior
    self-reinforcing. If this holds up in trials, it means there is a pharmacological way to
    turn down the reward sensitivity knob across the entire network. The addiction pathways still
    exist, but the signal driving them weakens.<br><br>
    <b>The weight loss mechanism through the model:</b> Obesity is partly a network state — the
    food-reward pathway is heavily reinforced (thousands of repetitions), and alternative reward
    pathways are comparatively weak. GLP-1 agonists reduce the weight on food-reward connections
    while leaving other pathways unaffected. The brain still processes food information, but the
    "this is extremely important" signal that drives overeating drops below the compulsion
    threshold. The person can choose rather than being driven.
  </div>

  <div class="info">
    <b style="color:#ffb74d">Peptides &amp; Nootropics</b><br>
    Peptides are short chains of amino acids that act as signaling molecules in the brain.
    Unlike traditional drugs that flood neurotransmitter systems globally, peptides can target
    specific receptor types with high precision. In network terms: peptides are <b>targeted
    parameter adjustments</b> rather than global knob turns.<br><br>
    <b>BPC-157</b> (Body Protection Compound) &mdash; promotes neuroplasticity and repair.
    In network terms: increases the rate at which damaged connections rebuild and new connections
    form. Used for brain injury recovery and potentially for enhancing learning capacity by
    increasing the plasticity window.<br><br>
    <b>Semax / Selank</b> &mdash; Russian-developed neuropeptides. Semax modulates BDNF
    (brain-derived neurotrophic factor), directly promoting synapse formation — it is essentially
    a plasticity enhancer. Selank modulates anxiety without sedation, similar to CBD but through
    a different mechanism (enkephalin modulation). In network terms: Semax increases the rate
    of new edge formation; Selank reduces threat-node activation without reducing bandwidth.<br><br>
    <b>Dihexa</b> &mdash; a peptide that enhances hepatocyte growth factor signaling in the brain.
    In animal studies, it dramatically increases synapse formation and has been explored for
    Alzheimer's. In network terms: it is the closest thing to a "rebuild lost connections"
    compound — potentially reversing the edge loss that characterizes cognitive decline.<br><br>
    <b>Oxytocin</b> &mdash; the "trust peptide." Increases social bonding, reduces social anxiety,
    increases conformity to in-group signals. In network terms: it amplifies the authority/trust
    weighting in belief propagation. This is why oxytocin increases trust AND increases in-group
    bias — it strengthens social signal processing, for better and worse.<br><br>
    <b>The peptide advantage:</b> Traditional drugs are blunt instruments — they change a
    neurotransmitter level across the whole brain. Peptides are more like targeted instructions
    to specific receptor types. As BCI technology improves, the combination of precise neural
    reading (Axona) + precise peptide delivery could enable truly targeted cognitive modification:
    increase plasticity in one region, reduce anxiety in another, strengthen specific pathways
    while leaving everything else untouched.
  </div>

  <div class="info">
    <b>The meta-insight:</b> Every drug is a knob on the same machine. Caffeine turns up
    processing speed. SSRIs raise the emotional floor. Alcohol lowers the coherence filter.
    Psychedelics dissolve cluster boundaries. Stimulants narrow the spotlight. Cannabis
    disrupts working memory. Understanding drugs as network parameter changes — instead of
    as good/bad, legal/illegal — makes their effects predictable, their risks quantifiable,
    and their therapeutic potential designable.<br><br>
    <b>For Axona:</b> If we can measure network parameters in real-time (via BCI), we can
    predict individual drug responses before administration. A brain already in chaos mode
    should not take a psychedelic. A brain in stagnation should not take a depressant. The
    right drug for the right network state — personalized pharmacology guided by cognitive
    state monitoring.
  </div>
  </div>

  <div class="sub-section">
  <h3>Collective Intelligence</h3>
<h2>Collective Intelligence — When Brains Network Together</h2>
  <p class="desc">
    What happens when the network extends beyond one skull? Teams, crowds, cultures, and
    the internet as a planetary nervous system.
  </p>

  <div class="info">
    <b>A group is a network of networks.</b> Each person is a cognitive network. When people
    interact — conversation, collaboration, shared experience — their networks form temporary
    connections through communication. These inter-brain links are lower bandwidth than intra-brain
    connections (language is slow compared to neural firing), but they allow information, beliefs,
    and patterns to propagate across brains. A team is a loosely connected super-network. A
    culture is a very loosely connected network of millions.
  </div>

  <div class="info">
    <b>Why some groups are smarter than their smartest member:</b> When a group has <b>cognitive
    diversity</b> (different knowledge clusters, different perspectives, different network
    architectures), cross-brain connections function like cross-cluster activation. Ideas that
    live in one person's network bridge to another person's network, producing combinations
    that neither brain would generate alone. This is the same mechanism as the cross-activation
    demo — but between people instead of between brain regions.<br><br>
    <b>The conditions:</b> High trust (willingness to share), psychological safety (willingness
    to be wrong), cognitive diversity (different knowledge), and communication bandwidth (enough
    interaction to form bridges). Remove any one and the group reverts to its average or worse.
  </div>

  <div class="info">
    <b>Why some groups are dumber than their dumbest member:</b><br><br>
    <b>Groupthink</b> is belief propagation with no resistant nodes. When conformity pressure is
    high and dissent is punished, the authority signal propagates unchecked. Every node adopts.
    No one tests the belief against evidence. The group reaches consensus quickly — and the
    consensus is wrong. Bay of Pigs, Challenger disaster, financial crises.<br><br>
    <b>Social loafing</b> is bandwidth reduction in a group setting. Each person assumes others
    will contribute, so individual effort drops. The group's total output is less than the sum
    of its potential parts. This is a bandwidth allocation problem — the certainty that others
    will compensate reduces each person's committed capacity.<br><br>
    <b>Polarization</b> is what happens when the inter-group connections are severed while
    intra-group connections strengthen. Each group becomes a tightly connected cluster with no
    bridges to the other. Beliefs propagate and reinforce within the cluster. Dissenting
    information cannot cross the gap. This is the network structure of political tribalism,
    echo chambers, and radicalization.
  </div>

  <div class="info">
    <b>Memes as viral ideas:</b> Richard Dawkins coined "meme" to describe ideas that replicate
    across brains the way genes replicate across organisms. In network terms: a meme is a
    pattern that successfully propagates from one brain's network to another's. Successful memes
    are: easy to encode (simple, emotionally charged), easy to transmit (short, shareable),
    and hard to forget (high emotional weight, connects to existing structure).<br><br>
    <b>Why misinformation spreads faster than truth:</b> False information is often more
    emotionally charged (fear, outrage, surprise) than true information. Higher emotional
    charge = higher encoding brightness = faster propagation. The network does not have a
    "truth filter" at the encoding stage — it has an "importance filter," and importance is
    driven by emotional weight, not accuracy. A boring truth and an exciting lie hit the
    same network, and the lie wins on encoding strength.
  </div>

  <div class="info">
    <b>The internet as a planetary nervous system:</b> The internet is a network of human
    networks connected by digital links. Information propagates at the speed of light instead
    of the speed of conversation. Belief injection (a viral post) can reach millions of nodes
    in hours instead of years. Cross-domain activation happens constantly (a physicist sees
    a biology paper shared by a musician friend).<br><br>
    <b>The problem:</b> The internet has the bandwidth and connectivity of a genius-level
    super-network, but the coherence filters of a drunk. There is no global consolidation
    (no "sleep" for the internet). No pruning mechanism (nothing gets forgotten or corrected
    at scale). No quality filter between novelty and noise. The result is a system with
    extraordinary creative potential and no mechanism to distinguish signal from garbage.
    Social media algorithms optimize for engagement (activation) not truth (coherence),
    producing a network that is permanently in the chaos quadrant.<br><br>
    <b>For Axona:</b> The same principles that model individual cognition could model
    collective cognition. Measure group coherence, detect polarization patterns, identify
    when a team is in its genius zone vs approaching groupthink. The math scales from
    neurons to people to civilizations — because the structure is the same at every level.
  </div>
  </div>

  <div class="sub-section">
  <h3>Bidirectionality &mdash; Does the Output Become an Input?</h3>
  <p class="desc">
    Not every signal in the brain can travel backward. A pathway only becomes a feedback
    loop if there is a sensor downstream that can feed the output state back into the
    predictor. Click each pulse to see which ones can make it home.
  </p>
  <div class="canvas-box">
    <canvas id="bidir-canvas" width="960" height="340"></canvas>
  </div>
  <div class="controls">
    <button onclick="bidirPulse('smile')">Pulse: happy &rarr; smile</button>
    <button onclick="bidirPulse('wag')">Pulse: positive &rarr; wag</button>
    <button onclick="bidirPulse('pupil')">Pulse: light &rarr; pupil</button>
    <button onclick="bidirPulse('digest')">Pulse: food &rarr; digest</button>
    <span style="margin-left:auto;color:var(--dim)">
      feedback loops: <b style="color:var(--accent2)" id="bidir-loops">2</b> / 4
    </span>
  </div>
  <div class="info">
    <b>The rule:</b> Signals are fundamentally one-directional at the level of a single
    synapse. Bidirectionality is emergent &mdash; it requires a return path the brain can
    read. A pathway stays one-directional when the downstream state has no sensor feeding
    back into the network.<br><br>
    <b>Examples above:</b><br>
    &bull; <b>Smile &harr; happy</b> &mdash; bidirectional. Facial proprioception is a real
    sensor. Smiling makes you happier because your brain reads its own face.<br>
    &bull; <b>Wag &harr; positive arousal</b> (dogs) &mdash; bidirectional. Proprioceptive
    feedback from the tail muscles reinforces the emotional state that triggered the wag.<br>
    &bull; <b>Light &rarr; pupil</b> &mdash; one-directional. You cannot will your pupils
    open because there is no proprioceptive channel on the iris. The iris is a pure
    actuator.<br>
    &bull; <b>Food &rarr; digestion</b> &mdash; effectively one-directional. You cannot
    consciously accelerate peristalsis; there is no interoceptor giving the brain the
    necessary leverage over the gut.<br><br>
    <b>The test is structural:</b> Is there a channel carrying the output state back into
    the brain's model? If yes, enough co-activation will make it bidirectional. If no, it
    stays one-way forever, no matter how many repetitions. This is why "just smile and you'll
    feel better" works, and "just stop being anxious" does not &mdash; the first has a return
    path, the second targets a system with no voluntary interoceptor to flip.
  </div>
  </div>

  <div class="sub-section">
  <h3>Pygmalion Effect &mdash; When Expectation Becomes Outcome</h3>
  <p class="desc">
    The placebo mechanism, applied socially. When an authority's belief about a subject
    propagates strongly enough, the subject's own predictive state shifts to match &mdash;
    and performance follows. Watch the loop close.
  </p>
  <div class="canvas-box">
    <canvas id="pyg-canvas" width="960" height="320"></canvas>
  </div>
  <div class="controls">
    <button onclick="pygSet(1)">High Expectation</button>
    <button onclick="pygSet(-1)">Low Expectation</button>
    <button onclick="pygSet(0)">Neutral</button>
    <button onclick="pygReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      confidence: <b style="color:var(--accent)" id="pyg-conf">0.50</b>
      &nbsp; performance: <b style="color:var(--accent2)" id="pyg-perf">0.50</b>
    </span>
  </div>
  <div class="info">
    <b>The Pygmalion effect</b> was documented in Rosenthal &amp; Jacobson's 1968 study:
    teachers were told at random that certain students were "high potential." They were not
    &mdash; the selection was pure chance. But by the end of the year, those students
    measurably outperformed their peers. The only thing that had changed was what the
    teacher expected.<br><br>
    <b>The mechanism:</b> The authority's expectation propagates through dozens of subtle
    channels &mdash; tone of voice, how often the student is called on, how long the
    teacher waits for an answer, which follow-up questions get asked, which mistakes get
    corrected vs ignored. Each of these shifts the student's self-model slightly. Over
    months, those shifts compound into a different predictive state: "I am good at this"
    vs "I am not." The student's actual cognition starts behaving differently because the
    prediction is behaving differently.<br><br>
    <b>This is the placebo mechanism applied socially.</b> Belief propagated from a trusted
    source changes the subject's own predictive state, which changes performance, which
    reinforces the belief, which further changes the state. It is a closed feedback loop.
    The original expectation can be completely arbitrary and still end up true.<br><br>
    <b>Golem effect:</b> The same mechanism runs in reverse. Low expectations propagate
    just as effectively and produce the same self-fulfilling loop in the opposite
    direction. This is why "soft bigotry of low expectations" is not just a phrase
    &mdash; it is a literal network operation.
  </div>
  </div>

  <div class="sub-section">
  <h3>Curiosity &harr; Boredom &mdash; Managed Novelty</h3>
  <p class="desc">
    Curiosity and boredom are the same mechanism running in opposite directions. The
    network has a target rate of incoming novelty; below it, pressure builds (boredom);
    above it in a safe context, the system actively seeks more (curiosity); above it in
    an unsafe context, the same signal becomes anxiety.
  </p>
  <div class="canvas-box">
    <canvas id="curi-canvas" width="960" height="360"></canvas>
  </div>
  <div class="controls">
    <label style="display:flex;align-items:center;gap:8px">
      <span>environment novelty:</span>
      <input type="range" id="curi-env" min="0" max="100" value="50" style="width:140px">
      <span class="stat-val" id="curi-env-val">50%</span>
    </label>
    <label style="display:flex;align-items:center;gap:8px;margin-left:12px">
      <span>safety:</span>
      <input type="range" id="curi-safe" min="0" max="100" value="80" style="width:120px">
      <span class="stat-val" id="curi-safe-val">80%</span>
    </label>
    <span style="margin-left:auto;color:var(--dim)">
      state: <b id="curi-state" style="color:var(--accent2)">satisfied</b>
    </span>
  </div>
  <div class="info">
    <b>The model:</b> Every network has a target novelty intake rate &mdash; roughly, the
    rate at which new patterns arrive and get encoded. Call it the setpoint. The system
    measures its actual recent novelty intake and compares it to the setpoint:<br><br>
    &bull; <b>Below setpoint &rarr; pressure rises.</b> This is boredom. Subjective
    experience: restlessness, craving stimulation, the urge to "do something." Biologically,
    the network is signaling that its encoding budget is going unused. Prolonged shortage
    is not just unpleasant &mdash; it actually degrades the network, because structures
    need novelty input to stay calibrated.<br><br>
    &bull; <b>At setpoint in safe context &rarr; curiosity / satisfaction.</b> The system
    is receiving exactly as much novelty as it can integrate. Subjective experience:
    engagement, flow, "this is interesting." Curiosity is the active-seeking version of
    this state &mdash; the system reaching outward because its recent intake was slightly
    below setpoint and it has bandwidth to explore.<br><br>
    &bull; <b>Above setpoint in safe context &rarr; delight or overload.</b> A little
    above is exhilarating &mdash; surprise without threat, the "oh wow" reaction. A lot
    above is overwhelm, even in a safe context.<br><br>
    &bull; <b>Above setpoint in unsafe context &rarr; anxiety.</b> Exact same novelty
    signal, but now threat-tagged. The system reads "unexpected + dangerous" and fires
    fear instead of curiosity. This is why horror movies and rollercoasters work: they
    produce the novelty signal in a context you know is actually safe, so the system
    oscillates between fear and delight.<br><br>
    <b>The paradox of doomscrolling:</b> Social feeds produce fast, shallow novelty &mdash;
    enough to register above setpoint, but not deep enough to actually be encoded. The
    network registers "novelty is happening" but the encoding rate stays near zero. So
    the boredom signal does not turn off, and you scroll more, and the mismatch widens.
    You can spend hours "consuming content" and end up more bored, not less, because the
    actual novelty intake (as measured by encoding, not exposure) never rose.<br><br>
    <b>The fix for boredom is not more stimulation &mdash; it is allowing the default
    mode network to kick in.</b> Boredom is uncomfortable because the setpoint has not
    been met, but the discomfort is the signal for the system to reorganize. If you let
    yourself be bored for long enough, the network stops waiting for external novelty
    and starts generating internal novelty &mdash; bridges between ideas, unprompted
    recollections, creative recombinations. This is why long walks, showers, and road
    trips produce insights. They are the conditions under which boredom resolves into
    spontaneous structure.
  </div>
  </div>

  <div class="sub-section">
  <h3>Confirmation Bias &mdash; Predictions Filter Perception</h3>
  <p class="desc">
    Two people can watch the same event and remember different things &mdash; not because
    one is lying, but because their priors filtered which parts even got encoded. The
    brain does not store what happened; it stores what its forecast allowed it to see.
  </p>
  <div class="canvas-box">
    <canvas id="confirm-canvas" width="960" height="340"></canvas>
  </div>
  <div class="controls">
    <button onclick="confirmSet('positive')">Positive Prior</button>
    <button onclick="confirmSet('negative')">Negative Prior</button>
    <button onclick="confirmSet('neutral')">Neutral Prior</button>
    <button onclick="confirmStream()">Expose to Stream of Evidence</button>
    <button onclick="confirmReset()">Reset</button>
  </div>
  <div class="info">
    <b>What is happening:</b> The network does not record evidence neutrally. Every
    incoming event is compared to the current prior, and events that confirm the prior
    get an encoding bonus (low prediction error = easy integration). Events that
    disconfirm the prior generate high residuals and often get discarded, reinterpreted,
    or simply not attended to. After a hundred ambiguous events, the memory trace looks
    nothing like the actual distribution &mdash; it looks like the prior's preferred
    version of events.<br><br>
    <b>Why it is not fixable by "just paying attention":</b> Attention itself is
    prior-driven. The system attends preferentially to things the prior says matter, and
    disregards things the prior says are noise. You cannot use the filter to audit the
    filter. This is why two honest, intelligent people with different priors can watch
    the same debate, the same trial, the same relationship, and emerge with memories that
    barely overlap. Neither is lying. Both are reporting what their encoding pipeline
    preserved.<br><br>
    <b>The Pygmalion loop from the Pygmalion canvas is one side of this.</b> Confirmation
    bias is the other side &mdash; belief propagated inward, shaping which inputs count
    as evidence, which in turn reinforces the belief. It is a closed loop with no
    external correction mechanism built in. The only way out is structured exposure to
    evidence the prior would normally reject, under conditions where the network is
    forced to encode it (writing it down, arguing the other side, formal methods).
  </div>
  </div>

  <div class="sub-section">
  <h3>Echo Chambers &mdash; Self-Reinforcing Belief Networks</h3>
  <p class="desc">
    When a cluster of belief-propagation nodes only talks to each other, and their
    conformity pressure is high enough to reject incoming contradictions, you get a
    coherent-but-wrong sub-network. Every member's confidence grows because every other
    member agrees. The whole cluster drifts together.
  </p>
  <div class="canvas-box">
    <canvas id="echo-canvas" width="960" height="360"></canvas>
  </div>
  <div class="controls">
    <button onclick="echoInjectIn()">Inject Matching Belief</button>
    <button onclick="echoInjectOut()">Inject Contradiction</button>
    <button onclick="echoReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      internal reinforcement: <b style="color:var(--accent)" id="echo-int">0</b>
      &nbsp; external contradictions rejected: <b style="color:var(--warn)" id="echo-ext">0</b>
    </span>
  </div>
  <div class="info">
    <b>The mechanism:</b> Belief propagation is weighted by conformity (how much a node
    trusts its neighbors). In a well-mixed network, conformity is moderate and
    contradictory inputs from diverse sources get integrated. In an echo chamber, the
    network has fragmented &mdash; a cluster only talks to a subset of itself, and that
    subset's conformity to each other is near-maximal. The cluster's beliefs get
    reinforced every cycle (everyone agrees, which raises everyone's confidence) while
    contradictions from outside are rejected as coming from "them" (low-conformity
    sources).<br><br>
    <b>Why the cluster is internally coherent:</b> Every member is running a perfectly
    reasonable local inference. "All my trusted sources confirm it, dissenters are
    untrustworthy, therefore my belief is well-supported." The math is correct. The
    error is in the graph structure &mdash; the sample of "trusted sources" is not
    representative of reality. But the individual cannot see the graph from inside.<br><br>
    <b>Social media makes this worse, not better.</b> The old model of information flow
    was geography + mass media: you were forced into contact with people unlike you and
    a shared set of broadcast sources. Modern feeds let everyone select their network.
    The natural equilibrium of a selectable network is maximum clustering &mdash; people
    sort themselves into homogeneous sub-networks and stop receiving anything from
    outside them. The internet did not invent echo chambers. It removed the friction that
    was preventing them.
  </div>
  </div>

  <div class="sub-section">
  <h3>Nostalgia &mdash; Memory Through a Changed State</h3>
  <p class="desc">
    Nostalgia is not a memory. It is a memory activated under a current emotional state,
    which recolors the experience of remembering. The same scene can feel warm or cold
    depending on what the network is pulling up alongside it &mdash; which is why
    returning to a favorite place often feels different than expected.
  </p>
  <div class="canvas-box">
    <canvas id="nost-canvas" width="960" height="340"></canvas>
  </div>
  <div class="controls">
    <label style="display:flex;align-items:center;gap:8px">
      <span>current mood:</span>
      <input type="range" id="nost-mood" min="0" max="100" value="60" style="width:140px">
      <span class="stat-val" id="nost-mood-val">60%</span>
    </label>
    <button onclick="nostRecall()">Recall Old Memory</button>
    <button onclick="nostReset()">Reset</button>
  </div>
  <div class="info">
    <b>What is happening:</b> Memory is reconstructive, not reproductive. Every time you
    "remember" something, the network rebuilds the experience from fragments, filling
    gaps with plausible material. The current emotional state biases which material
    gets used for the fill. Recall the same memory while happy, while sad, while lonely,
    while content &mdash; each produces a subtly different experience, even though the
    underlying memory trace is the same.<br><br>
    <b>Why nostalgia intensifies with distance and loss:</b> The memory cluster for a
    past period is stable, but the current state is usually much lower in novelty and
    security than the remembered period. The gap between "back then" and "now" is what
    produces the characteristic bittersweet signature. Pure happiness would just be
    "that was nice." Nostalgia specifically requires the sense of something that cannot
    be recovered &mdash; it is the contrast, not the content, that produces the
    feeling.<br><br>
    <b>Why returning to an old place rarely "works":</b> You can put the body back in
    the place. You cannot put the network back in the state that encoded the place.
    The old encoding was done under a different self-model, a different mood, a
    different set of expectations. Walking into the childhood home as an adult accesses
    the memory trace but runs it through current priors, which produce a very different
    experience. Nothing is wrong &mdash; the two encodings are just different, and the
    mismatch is what makes the return feel hollow.
  </div>
  </div>

  <div class="sub-section">
  <h3>Temporal Discounting &mdash; Why Now Beats Later Mechanically</h3>
  <p class="desc">
    Future rewards are weighted less than present rewards &mdash; not linearly, but
    steeply. The network's reward prediction for "something ten minutes from now" is
    dramatically smaller than for "right now," even if the future thing is objectively
    bigger. This is not a character flaw; it is a weight asymmetry built into every
    brain.
  </p>
  <div class="canvas-box">
    <canvas id="disc-canvas" width="960" height="340"></canvas>
  </div>
  <div class="controls">
    <label style="display:flex;align-items:center;gap:8px">
      <span>discount rate:</span>
      <input type="range" id="disc-rate" min="1" max="100" value="35" style="width:140px">
      <span class="stat-val" id="disc-rate-val">35%</span>
    </label>
    <button onclick="discChoose('now')">Take $10 now</button>
    <button onclick="discChoose('later')">Wait: take $20 in 1 week</button>
    <button onclick="discReset()">Reset</button>
  </div>
  <div class="info">
    <b>The finding:</b> People routinely prefer $10 today over $20 in a week &mdash;
    even knowing that "a week for $10" is an absurdly good return. The delayed reward
    is not being rationally undervalued; it is being neurologically downweighted by a
    discount function that drops steeply in the first few hours and then flattens
    out. Two hours from now is almost as valuable as right now. Two weeks from now is
    worth a fraction. Two years from now is almost invisible.<br><br>
    <b>Why evolution built it this way:</b> In the ancestral environment, future
    rewards were genuinely less reliable &mdash; you might not be alive, the food
    might be gone, the condition might change. Discounting the future was
    mathematically correct given how often the future failed to arrive. The discount
    function is calibrated for a world where long time horizons were usually wrong
    to bet on. The modern world has different dynamics, but the discount function
    did not update.<br><br>
    <b>Why willpower does not fix it:</b> The weight asymmetry is built into the
    reward pathway itself. By the time the choice reaches conscious deliberation, the
    "now" option has already been amplified and the "later" option already attenuated.
    The gradient points at "now" before you start thinking. Willpower is the slow,
    expensive System 2 process of overriding the fast gradient &mdash; which is why
    it depletes under load and fails when you are stressed, tired, or drunk.<br><br>
    <b>What works:</b> Not willpower. <b>Removing the choice.</b> Automatic savings,
    commitment devices, precommitment, making the future rewards visible in the
    present moment (vivid imagination, scheduled rewards, calendar visibility). You
    are not fighting the discount function &mdash; you are restructuring the
    decision so the discount function never gets to act on it.
  </div>
  <div class="info" style="border-left: 3px solid #f06292">
    <b style="color:#f06292">Procrastination &mdash; not laziness, prediction math</b><br><br>
    Procrastination is temporal discounting + aversion combined. The
    task has a cost (effort, boredom, anxiety) that is felt NOW, and a
    reward (completion, grade, salary) that is felt LATER. The discount
    function makes the future reward nearly invisible while the present
    cost is fully weighted. Result: the math always says &quot;not
    now&quot; until the deadline makes the cost of NOT doing it
    immediate.<br><br>
    &bull; <b>The deadline effect:</b> people finish the night before
    not because of willpower but because the consequences of not
    finishing (failing, getting fired) have become immediate. The
    discount function now weights them fully. The math flipped.<br><br>
    &bull; <b>Why &quot;just start&quot; works:</b> starting a task
    shifts the prediction from &quot;the whole task is ahead of me&quot;
    (large abstract cost) to &quot;I am doing this specific subtask
    right now&quot; (small concrete cost). The discount function treats
    the smaller present-moment cost more favorably.<br><br>
    &bull; <b>Why anxiety makes procrastination worse:</b> anxiety
    is a state modulator that amplifies threat signals. The task&apos;s
    difficulty is a mild threat. Under anxiety, the mild threat gets
    amplified into &quot;this will be terrible,&quot; making the present
    cost feel even larger relative to the discounted future reward.<br><br>
    &bull; <b>Why procrastinators are not lazy:</b> a lazy person does
    not do the task and does not care. A procrastinator cares
    intensely &mdash; they are in constant low-grade distress about the
    task they are not doing. The bandwidth consumed by that distress is
    ALSO a cost, which further narrows the bandwidth available for
    actually starting. Procrastination is a bandwidth trap, not a
    motivation deficit.<br><br>
    <b>See also:</b>
    <a href="#arousal-clarity">Arousal &amp; Clarity</a>
    (drive states suppress frontal cortex the same way deadline panic
    does &mdash; last-minute work is done under a drive modulator, which
    is why it feels different from calm work),
    <a href="#" onclick="document.querySelector('[data-panel=media-tab]').click();return false">Media &amp; Brain</a>
    (short-form content raises the residual threshold, making the
    non-stimulating task feel even more aversive by comparison).
  </div>
  </div>

  <div class="sub-section">
  <h3>Anchoring &amp; Availability &mdash; Fast Numbers Beat Slow Math</h3>
  <p class="desc">
    Hear a random number before estimating a quantity and your estimate drifts
    toward that number. Recall a vivid plane crash and your estimate of flight
    risk climbs. System 1 answers numerical questions by grabbing whatever is
    nearby in memory, and "nearby" is whatever was recent or vivid, not whatever
    is actually relevant.
  </p>
  <div class="canvas-box">
    <canvas id="anchor-canvas" width="960" height="340"></canvas>
  </div>
  <div class="controls">
    <button onclick="anchorSpin(10)">Spin: anchor at 10</button>
    <button onclick="anchorSpin(65)">Spin: anchor at 65</button>
    <button onclick="anchorSpin(null)">No anchor</button>
    <button onclick="anchorEstimate()">Estimate countries in Africa</button>
    <button onclick="anchorReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      guess: <b id="anchor-guess" style="color:var(--accent)">—</b>
      &nbsp; truth: <b style="color:var(--accent2)">54</b>
    </span>
  </div>
  <div class="info">
    <b>The classic anchoring study</b> (Tversky &amp; Kahneman, 1974): subjects
    watched a wheel of fortune stop on a random number, then were asked "what
    percentage of UN member states are African?" Subjects whose wheel stopped
    at 10 gave a median estimate of 25%. Subjects whose wheel stopped at 65 gave
    a median of 45%. The wheel was visibly random &mdash; they knew it was
    random &mdash; and their estimates still drifted toward it. System 1 grabbed
    the most recently available number as a starting point.<br><br>
    <b>Availability bias</b> (also Tversky &amp; Kahneman): when you try to
    estimate how common something is, you retrieve examples from memory and count
    them. But memory is biased toward vivid, recent, emotional events. So people
    routinely overestimate deaths from plane crashes, terrorism, and shark
    attacks (vivid, memorable, rare) and underestimate deaths from heart disease,
    diabetes, and household falls (mundane, forgettable, common). The memories
    are the evidence, and the retrieval is biased, so the estimate is biased.<br><br>
    <b>Why willpower does not fix it:</b> Anchoring happens before the estimate
    reaches consciousness. By the time you are aware you are estimating, the
    anchor has already been applied. You can partially correct by explicitly
    thinking "that number was random, do not use it" &mdash; but studies show the
    anchor still biases the adjusted estimate. The fix is not correction; the
    fix is refusing to look at the number in the first place.<br><br>
    <b>Companion to the Priming, Confirmation, and Two-System canvases:</b>
    anchoring is priming applied to numerical estimates. Availability is
    confirmation bias applied to frequency judgments. Both are System 1 running
    its defaults while System 2 is asleep at the wheel.
  </div>
  </div>

  <div class="sub-section">
  <h3>Moral Emotions &mdash; Disgust, Shame, Pride, Guilt</h3>
  <p class="desc">
    Moral emotions are not a separate "ethical" layer on top of cognition. They
    are specific network operations with specific evolved functions. Disgust
    started as a pathogen-avoidance system and got recruited for social judgment.
    Shame enforces group conformity. Pride reinforces status-building behaviors.
    Guilt repairs damaged relationships. Each has a distinct signature and
    distinct triggers.
  </p>
  <div class="canvas-box">
    <canvas id="moral-canvas" width="960" height="380"></canvas>
  </div>
  <div class="controls">
    <button onclick="moralTrigger('disgust')">Rotten food / betrayal</button>
    <button onclick="moralTrigger('shame')">Caught in a lie</button>
    <button onclick="moralTrigger('pride')">Accomplishment noticed</button>
    <button onclick="moralTrigger('guilt')">Hurt someone you love</button>
    <button onclick="moralTrolley()">Trolley Problem</button>
    <button onclick="moralReset()">Reset</button>
  </div>
  <div class="info">
    <b>The functions:</b><br>
    &bull; <b>Disgust</b> &mdash; the oldest moral emotion. Originally a
    pathogen-avoidance circuit (spoiled food, parasites, bodily fluids); later
    recruited for social contaminants (betrayal, impurity, desecration). The
    physiological signature is the same (nausea, recoil, gag reflex) whether the
    target is moldy bread or a traitor, which is why "I was disgusted by what he
    did" is not metaphorical &mdash; it is the same circuit.<br>
    &bull; <b>Shame</b> &mdash; a group-conformity enforcement signal. Fires when
    the self-model detects a gap between "what I did" and "what my group
    expects," coupled with the prediction that the group has seen it. Produces
    hiding, submission, withdrawal &mdash; literally lowering status to avoid
    group punishment.<br>
    &bull; <b>Pride</b> &mdash; the counterpart. Fires when the self-model detects
    "what I did" exceeding "what my group expects" <em>and</em> the group has seen
    it. Produces upright posture, visibility-seeking, and continued investment in
    the same behavior. Pride is status-building; shame is status-defending.<br>
    &bull; <b>Guilt</b> &mdash; relationship-repair signal. Fires when the
    self-model detects "I hurt someone I care about" regardless of whether the
    group saw. Produces apologetic behavior, restitution, and care-giving toward
    the injured party. Unlike shame (which hides), guilt seeks out the injured
    party &mdash; it is an approach signal, not an avoidance one.<br><br>
    <b>The trolley problem</b> demonstrates these systems in conflict. The
    utilitarian answer (push one person to save five) is a System 2 calculation:
    lives saved minus lives lost = net good. The emotional answer (do not push)
    is the guilt/disgust system firing on the visceral image of physically
    pushing a human being. Most people give the utilitarian answer in the
    distant-switch version and the emotional answer in the close-push version,
    because the proximity changes which system fires loudest. Neither system is
    "correct" &mdash; they are different answers to different questions.<br><br>
    <b>Why this matters:</b> Moral disagreements often look like failures of
    reasoning ("they just do not see the obvious truth") but are really
    differences in which moral-emotion circuit is loudest for a given scenario.
    Two people can agree on all the facts and still disagree because one is
    running guilt/repair and the other is running disgust/purity, and those
    systems have different outputs. Moral philosophy is partly an attempt to
    negotiate which circuit should win in which situation.
  </div>
  </div>

  <div class="sub-section">
  <h3>Psychedelics &mdash; Global Prior Weakening (Entropic Brain)</h3>
  <p class="desc">
    Psychedelics do not add new content to the brain. They weaken the dominant
    priors that normally constrain perception, letting activation flow across
    clusters that usually stay isolated. Carhart-Harris and Friston called the
    result the <em>entropic brain</em>: higher entropy, more cross-cluster
    communication, looser categorical inference. The Self canvas briefly touched
    this &mdash; here is the mechanism in full.
  </p>
  <div class="canvas-box">
    <canvas id="psy-canvas" width="960" height="400"></canvas>
  </div>
  <div class="controls">
    <label style="display:flex;align-items:center;gap:8px">
      <span>dose / prior weakening:</span>
      <input type="range" id="psy-dose" min="0" max="100" value="0" style="width:140px">
      <span class="stat-val" id="psy-dose-val">0%</span>
    </label>
    <button onclick="psyReset()">Reset</button>
  </div>
  <div class="info">
    <b>The default-mode network</b> (DMN) is a set of regions that coordinate
    self-referential thought, autobiographical narrative, and the sense of being
    a continuous self. Under normal conditions the DMN dominates &mdash; its
    activity is the substrate of ordinary "I am me, sitting here, thinking my
    thoughts." On psychedelics, DMN activity drops sharply, and cross-cluster
    communication between regions that normally do not talk to each other rises
    dramatically.<br><br>
    <b>What that produces subjectively:</b>
    &bull; <b>Loosened priors</b> &mdash; perception becomes more bottom-up. The
    brain stops aggressively filtering sensory data through its expectations, so
    you see more of what is actually arriving. This is why surfaces seem to
    "breathe" and colors feel saturated &mdash; the predictor is no longer
    smoothing them into familiar objects.<br>
    &bull; <b>Cross-cluster activation</b> &mdash; concepts that were stored in
    separate domains start linking. Sound becomes visible. Abstract ideas feel
    like physical sensations. This is synesthesia-adjacent territory, produced
    by the same mechanism (reduced inhibition between modalities) but on a much
    larger scale.<br>
    &bull; <b>Ego dissolution</b> &mdash; the self-model is itself a dominant
    prior, maintained by the DMN. Weaken the DMN and the self-model destabilizes.
    What remains is the experience of awareness without a clear subject.<br><br>
    <b>Why the therapeutic results are promising:</b> Several conditions (severe
    depression, treatment-resistant PTSD, addiction, end-of-life anxiety) share a
    common profile &mdash; an over-rigid prior that cannot be updated by ordinary
    experience. Depression: "nothing will help me." PTSD: "this context is
    dangerous." Addiction: "this is the only thing that matters." Psychedelics
    temporarily destabilize those priors, creating a window in which new
    associations can form and the prior can be renegotiated. It is not the
    chemical that heals. The chemical opens a window. What happens in the window
    is what heals &mdash; which is why psychedelic therapy relies heavily on set
    and setting, and why the same dose without integration work produces much
    worse outcomes.
  </div>
  </div>
</div>
</div>

<!-- ═══ Tab 5: Neural Interface (Read + Write + Dreams) ═══════════ -->
<div class="panel" id="neural-tab">
<div class="container">
  <h2>Neural Interface</h2>
  <p class="desc">
    Reading the brain, writing to it, and the frontier: engineering dreams.
  </p>

  <!-- BCI Read -->
  <h3>BCI Signal &rarr; Axona Interpretation</h3>
  <div style="display:flex;gap:12px">
    <div class="canvas-box" style="flex:1">
      <div style="padding:4px 10px;font-size:9px;color:var(--dim);border-bottom:1px solid var(--border)">
        Raw Neural Signal &mdash; 8 channels
      </div>
      <canvas id="bci-raw-canvas" width="460" height="320"></canvas>
    </div>
    <div class="canvas-box" style="flex:1">
      <div style="padding:4px 10px;font-size:9px;color:var(--dim);border-bottom:1px solid var(--border)">
        Axona Interpretation
      </div>
      <canvas id="bci-interp-canvas" width="460" height="320"></canvas>
    </div>
  </div>
  <div class="controls">
    <button onclick="bciStimulate('insight')" style="border-color:var(--accent2);color:var(--accent2)">Insight</button>
    <button onclick="bciStimulate('stress')" style="border-color:var(--warn);color:var(--warn)">Stress</button>
    <button onclick="bciStimulate('focus')" style="border-color:#4fc3f7;color:#4fc3f7">Focus</button>
    <button onclick="bciStimulate('drowsy')" style="border-color:#666;color:#666">Drowsy</button>
    <button onclick="bciStimulate('encoding')" style="border-color:var(--accent);color:var(--accent)">Encoding</button>
    <button onclick="bciStimulate('dream')" style="border-color:#f06292;color:#f06292">Dream</button>
    <span style="margin-left:auto;color:var(--dim);font-size:10px">
      state: <b style="color:var(--accent)" id="bci-state">idle</b>
    </span>
  </div>

  <!-- Neural Writing -->
  <div class="sub-section">
    <h3>Neural Writing &mdash; Coding a Neuron</h3>
    <div class="canvas-box">
      <canvas id="nw-canvas" width="960" height="380"></canvas>
    </div>
    <div class="controls">
      <button onclick="nwInject('memory')">Inject Memory</button>
      <button onclick="nwInject('skill')">Inject Skill</button>
      <button onclick="nwInject('association')">Inject Association</button>
      <button onclick="nwInject('dream')" style="border-color:#f06292;color:#f06292">Inject Dream</button>
      <button onclick="nwInject('erase')" style="border-color:#e53935;color:#e53935">Erase</button>
      <button onclick="nwReset()">Reset</button>
      <span style="margin-left:auto;color:var(--dim);font-size:10px">
        click a neuron, then inject &mdash;
        neurons: <b style="color:var(--accent)" id="nw-neurons">0</b>
        synapses: <b style="color:var(--accent2)" id="nw-synapses">0</b>
      </span>
    </div>
  </div>

  <div class="info">
    <b>The product concept:</b> Neuralink provides raw electrical signals from neural electrodes &mdash;
    firing patterns, timing, spatial distribution across brain regions. Raw neural data is noise
    without a model of what it means. Axona is the <b>interpretation layer</b> &mdash; the software
    that turns wiggling voltage lines into a meaningful cognitive dashboard. Without Axona, a BCI
    just gives you noise. With Axona, that noise becomes: "you are approaching an insight," "your
    bandwidth is dropping," "that memory just encoded strongly," "you are losing coherence."
  </div>

  <div class="info">
    <b>What reading can detect:</b><br>
    &bull; <b>Cognitive state</b> &mdash; map neural firing patterns to the state space (genius/chaos/order/stagnation) in real-time<br>
    &bull; <b>Novelty detection before conscious awareness</b> &mdash; cross-region activation spikes 200&ndash;500ms before the conscious eureka moment. EEG studies already show pre-conscious insight signatures<br>
    &bull; <b>Bandwidth monitoring</b> &mdash; track cognitive load in real-time. Alert before burnout. Optimize schedules around actual brain state, not guesswork<br>
    &bull; <b>Encoding quality</b> &mdash; detect emotional intensity during encoding. Predict which memories will persist. Flag high-impact moments in education or therapy<br>
    &bull; <b>Belief state measurement</b> &mdash; watch how new information propagates through neural networks. Did it get adopted deeply (many regions) or superficially (one region, briefly)?
  </div>

  <div class="info">
    <b>Neural writing &mdash; coding a neuron:</b> A neuron stores information through its
    <b>connections</b> (synapses), not its content. To "write" a memory, you do not put data
    inside a cell &mdash; you create or strengthen specific synaptic connections so that when the
    right cue arrives, the right pattern fires.<br><br>
    &bull; <b>Inject Memory</b> = form new synaptic connections (edges) to nearby neurons<br>
    &bull; <b>Inject Skill</b> = strengthen and direct existing pathways. Skills are not facts &mdash;
    they are reliable routes that fire quickly and consistently<br>
    &bull; <b>Inject Association</b> = create a long-range bridge between distant clusters. Give someone
    an intuition they never earned: connect "music" to "mathematics" and patterns in one domain
    trigger insights in the other<br>
    &bull; <b>Erase</b> = weaken all connections until isolated. An isolated neuron is effectively
    forgotten &mdash; it exists but nothing can reach it
  </div>

  <div class="info">
    <b>What exists today:</b><br>
    &bull; MIT's <b>Tonegawa lab</b> created false memories in mice by activating specific engram cells
    with optogenetics &mdash; proof that memories can be written, not just read<br>
    &bull; DARPA's <b>RAM program</b> showed that targeted electrical stimulation during encoding
    improves memory formation by 15&ndash;25%<br>
    &bull; Neuralink's current implant can stimulate ~1,000 electrodes. The resolution is still
    coarse &mdash; you cannot target a single synapse &mdash; but the trajectory is clear<br>
    &bull; <b>Cochlear implants</b> already write sensory data directly to the auditory nerve &mdash;
    120,000+ people hear through neural writing today
  </div>

  <div class="info">
    <b>Engineering dreams:</b> During REM sleep, the brain enters a unique state: high cross-region
    activation (novel associations), suppressed motor output (you do not act on them), and reduced
    prefrontal control (the logical filter is off). Dreams may be the brain's way of <b>testing
    novel associations without consequences</b> &mdash; a safe sandbox for structural pressure to
    resolve.<br><br>
    If you could activate specific neurons in sequence during sleep, you could engineer a dream that
    tests specific hypotheses. The neuron fires, activation spreads through unlikely paths, and by
    morning the network has tested thousands of connections it would never try while awake.<br><br>
    <b>Research trajectory:</b><br>
    &bull; MIT Media Lab's <b>Targeted Dream Incubation</b> (TDI) uses sleep-onset audio cues to
    influence dream content &mdash; subjects who dreamed about a creative task performed better on
    it the next day<br>
    &bull; <b>Lucid dreaming</b> research shows the prefrontal cortex can become active during REM,
    enabling conscious control of dream content<br>
    &bull; Studies at the University of Bern show that <b>learning during sleep</b> is possible when
    timed to specific sleep oscillation phases<br>
    &bull; The trajectory: from influencing dreams with sound cues &rarr; to targeting specific neural
    pathways during sleep &rarr; to engineering dream sequences that solve specific problems
  </div>

  <div class="info">
    <b>Why sleep exists &mdash; novelty integration:</b> During waking hours, the brain constantly
    forms new connections &mdash; new experiences, new associations, new ideas. But forming a
    connection is not the same as <b>integrating</b> it. A new edge in the graph needs to be
    tested: does it strengthen the network or destabilize it? Does it conflict with existing
    structure? Should it be kept, weakened, or removed?<br><br>
    Sleep may be when this integration happens. During slow-wave sleep, the brain replays the
    day's neural patterns at compressed speed, testing new connections against existing structure.
    Connections that strengthen coherence get reinforced. Connections that create contradictions
    get pruned. By morning, the network has been <b>consolidated</b> &mdash; the useful novelty
    from yesterday is now stable structure, and the noise has been cleaned out.<br><br>
    This explains the <b>novelty/coherence balance</b> from a new angle. During the day, novelty
    accumulates faster than coherence can keep up &mdash; you are always slightly ahead on new
    connections, slightly behind on integration. Sleep is the catch-up period. It is when
    coherence processes the backlog of novelty.
  </div>

  <div class="info">
    <b>Why sleep deprivation causes insanity:</b> If sleep is the integration phase, then
    skipping it means novelty keeps accumulating with no consolidation. New connections form
    but never get tested or pruned. The network becomes increasingly fragmented &mdash;
    contradictory beliefs coexist, irrelevant associations persist, the signal-to-noise ratio
    collapses.<br><br>
    After 24 hours without sleep: cognitive performance drops, emotional regulation weakens,
    hallucinations begin at the edges. After 48 hours: paranoia, disorganized thinking,
    inability to distinguish real from imagined. After 72+ hours: full psychotic episodes
    &mdash; the network has accumulated so much unintegrated novelty that coherence has
    effectively collapsed. This looks exactly like what happens when you push the novelty
    slider past the threshold in the demo above &mdash; the graph fragments.<br><br>
    <b>Sleep deprivation is forced chaos mode.</b> The system keeps generating new connections
    but has no mechanism to stabilize them. The genius/breakdown threshold drops lower and
    lower until even normal input produces incoherent responses.
  </div>

  <div class="info">
    <b>Why every creature sleeps:</b> From an evolutionary perspective, sleep is dangerous.
    You are unconscious, immobile, vulnerable to predators. A lion that stays awake 24/7
    could hunt more. A prey animal that never sleeps could watch for threats continuously.
    The fact that <b>every animal with a nervous system sleeps</b> &mdash; from jellyfish to
    elephants &mdash; means the cost of NOT sleeping is even higher than the cost of being
    vulnerable.<br><br>
    That cost is network collapse. Without consolidation, the neural network degrades until
    it cannot function. Sleep is not rest in the sense of "doing nothing." It is the most
    computationally intensive maintenance operation the brain performs: replaying, testing,
    pruning, reinforcing, reorganizing. It is <b>defragmentation for a biological neural
    network</b>.<br><br>
    Even organisms without brains show sleep-like states. C. elegans (a worm with 302 neurons)
    has a quiescent phase that meets the definition of sleep. This suggests that consolidation
    is not a luxury of complex brains &mdash; it is a fundamental requirement of any network
    that forms new connections.
  </div>

  <div class="info">
    <b>Dreams as the test environment:</b> If slow-wave sleep is consolidation (reinforcing good
    connections, pruning bad ones), then REM sleep and dreams may be the <b>stress test</b>.
    The brain activates unusual combinations &mdash; connections that would never fire during
    waking life &mdash; and checks whether they produce useful patterns or garbage. Useful
    patterns get flagged for retention. Garbage gets discarded.<br><br>
    This is why dreams are bizarre but not random. They follow emotional logic, not factual
    logic &mdash; because the test is not "is this true?" but "is this <em>useful</em>?"
    A dream about flying is not testing whether you can fly. It is testing whether the neural
    pattern "freedom + movement + exhilaration" produces a coherent activation state. If it
    does, those connections get strengthened. If it does not, they get pruned.<br><br>
    <b>Engineering dreams</b> would mean controlling which connections get stress-tested during
    REM. Instead of random bizarre combinations, you could target specific problem domains &mdash;
    and wake up with a network that has already explored thousands of solution paths overnight.
  </div>

  <div class="info">
    <b>Who would use this:</b><br>
    &bull; <b>BCI companies</b> (Neuralink, Synchron, Blackrock) &mdash; Axona as an interpretation SDK<br>
    &bull; <b>Researchers</b> &mdash; cognitive modeling framework for neural data<br>
    &bull; <b>Clinicians</b> &mdash; real-time therapy feedback (is the session working?)<br>
    &bull; <b>Education</b> &mdash; measuring actual learning, not just test scores<br>
    &bull; <b>Performance</b> (athletes, pilots, surgeons) &mdash; optimal state tracking<br>
    &bull; <b>Military/first responders</b> &mdash; cognitive load monitoring in high-stress environments<br>
    &bull; <b>Sleep labs</b> &mdash; dream engineering for creative problem-solving
  </div>
</div>
</div>

<!-- ═══ Tab 6: States & Conditions ════════════════════════════════ -->
<div class="panel" id="conditions-tab">
<div class="container">
  <h2>States &amp; Conditions</h2>
  <p class="desc">
    How the brain's network behaves under different conditions &mdash; from optimal performance
    to breakdown. Each condition is a different configuration of the same underlying system.
  </p>

  <!-- Flow State -->
  <h3>Flow State</h3>
  <div class="info">
    <b>The genius quadrant made real:</b> Flow is the state where skill level matches challenge
    level, goals are clear, and feedback is immediate. In network terms: high novelty rate +
    high coherence rate + all bandwidth allocated to a single task. No stressors, no distraction,
    full processing capacity directed at one problem.<br><br>
    Mihaly Csikszentmihalyi's research identified the conditions: the task must be hard enough to
    require full attention (preventing boredom/stagnation) but not so hard that it overwhelms
    capacity (preventing chaos). The sweet spot is a narrow band where the network is operating
    at maximum throughput without fragmenting.<br><br>
    <b>What flow looks like in the network:</b> Activation is focused &mdash; a tight cluster of
    nodes firing in coordinated patterns, with minimal noise from unrelated regions. New connections
    form within the active cluster (novelty) and immediately integrate into the existing structure
    (coherence). The rest of the network goes quiet. This is why time perception changes in flow
    &mdash; the brain is not tracking external cues because all bandwidth is consumed by the task.<br><br>
    <b>Why flow is rare:</b> It requires simultaneously high novelty, high coherence, full bandwidth,
    and zero distraction. Any stressor, interruption, or mismatch between skill and challenge
    breaks the state. Modern environments with notifications, multitasking, and constant context-switching
    are hostile to flow. The network never gets a sustained period of focused activation.
  </div>

  <!-- Attention & Distraction -->
  <div class="sub-section">
    <h3>Attention &amp; Distraction</h3>
    <div class="info">
      <b>Attention is a spotlight.</b> At any given moment, only a small fraction of the network
      is actively firing. Attention determines which fraction. When you focus on a math problem,
      the math-related cluster activates and everything else dims. When you focus on a conversation,
      the language and social clusters activate. The spotlight is narrow by design &mdash; activating
      everything simultaneously would be chaos mode.<br><br>
      <b>Distraction is spotlight fragmentation.</b> Each notification, each context switch, each
      competing demand splits the spotlight into smaller pieces. Instead of one bright focused beam,
      you get dozens of dim scattered ones. The network activates many regions shallowly instead of
      one region deeply. This is why multitasking degrades performance &mdash; it is not that you
      are doing two things at once. It is that you are doing zero things deeply.<br><br>
      <b>Social media as an attention architecture:</b> Infinite scroll, variable reward scheduling,
      notification interrupts &mdash; these are engineered to fragment your spotlight into the
      smallest possible pieces and redirect each piece toward the platform. In network terms:
      your bandwidth is being consumed by thousands of micro-activations that never reach the
      depth needed for encoding, consolidation, or novelty generation. You are processing but not
      thinking. Activating but not connecting.<br><br>
      <b>ADHD is not a deficit.</b> It is an attention <em>allocation difference</em>. The ADHD
      network activates broadly instead of narrowly &mdash; the spotlight is wider and dimmer
      rather than focused and bright. This makes sustained focus on a single task harder, but it
      also means more cross-cluster activation, more unexpected connections, and potentially more
      novelty. Many people with ADHD report hyperfocus on tasks that match their interest &mdash;
      which is exactly what the model predicts: when the entire broadened spotlight happens to
      converge on one region, the activation depth is exceptional. ADHD may be a network optimized
      for novelty detection at the expense of sustained coherence.
    </div>
  </div>

  <!-- Addiction -->
  <div class="sub-section">
    <h3>Addiction</h3>
    <div class="info">
      <b>A hijacked reward network.</b> In a healthy network, many nodes compete for activation
      based on relevance, context, and current goals. In addiction, one node (the substance or
      behavior) becomes so heavily weighted that it distorts every retrieval path toward itself.
      The network rewires around the addiction &mdash; connections to the addictive node strengthen
      with each use while connections to everything else weaken through neglect.<br><br>
      <b>Dopamine prediction errors:</b> The brain's reward system does not respond to pleasure
      itself. It responds to the <em>difference</em> between expected and received reward. The
      first hit of a drug produces a massive prediction error (unexpected reward), which triggers
      aggressive synaptic strengthening. The brain encodes: "this is important, remember how to
      get back here." Each subsequent use reduces the surprise but the pathway is already
      reinforced. Now the prediction error goes the other direction &mdash; NOT getting the
      substance produces a negative prediction error (expected reward missing), which feels like
      suffering.<br><br>
      <b>Why addiction looks like belief propagation:</b> The addicted brain has been "convinced"
      at the deepest level. The authority node is the substance itself &mdash; and every pathway
      in the network has been gradually recruited to serve it. Resistant nodes (career, relationships,
      health) get overridden one by one as the signal strengthens. This is conformity mechanics
      applied to neurochemistry: the brain aligns its internal state with the strongest signal,
      even when that signal is destructive.<br><br>
      <b>Recovery as network rewiring:</b> Breaking addiction is not about willpower in the
      moment. It is about building enough alternative pathways that the addictive node loses its
      monopoly on activation. New connections to other reward sources (exercise, social bonds,
      creative work) gradually redistribute weight across the network. This is slow because the
      addictive pathways were reinforced thousands of times. Each alternative activation is a
      single weak injection competing against a highway. This is why recovery takes years, why
      relapse is common, and why environment matters &mdash; being near cues that activate the
      addictive node can overwhelm fragile new pathways.
    </div>
  </div>

  <!-- Trauma & PTSD -->
  <div class="sub-section">
    <h3>Trauma &amp; PTSD</h3>
    <div class="info">
      <b>A memory too bright to integrate.</b> Normal emotional memories get encoded at high
      brightness and then consolidated during sleep &mdash; tested, integrated, filed into the
      network's structure. Traumatic memories get encoded at such extreme intensity that the
      normal consolidation process cannot handle them. The emotional weight is too high. The
      memory sits in the network like a star that is too massive &mdash; it distorts the
      activation field around it, pulling retrieval toward itself involuntarily.<br><br>
      <b>Why trauma replays:</b> The brain keeps trying to consolidate the memory during sleep
      (nightmares) and during waking hours (flashbacks, intrusive thoughts). Each replay is an
      attempt to integrate &mdash; to reduce the emotional weight enough that normal consolidation
      can work. But the weight is so high that each replay re-triggers the full emotional response,
      which re-encodes the memory at the same extreme brightness. The system is stuck in a loop:
      trying to process something that re-traumatizes with each processing attempt.<br><br>
      <b>Triggers as proximity activation:</b> Any cue that is close to the trauma node in the
      network &mdash; a smell, a sound, a location, a phrase, a feeling in the body &mdash; can
      activate the full trauma response. This is not irrational. It is the network working exactly
      as designed: spreading activation from a cue to a nearby high-brightness node. The problem
      is that the trauma node is SO bright that even distant cues can reach it through indirect
      paths.<br><br>
      <b>EMDR and trauma processing:</b> Eye Movement Desensitization and Reprocessing works by
      having the patient recall the trauma while simultaneously performing bilateral eye movements.
      One theory: the eye movements activate the same neural pathways used during REM sleep,
      essentially forcing a consolidation attempt while the patient is awake and the prefrontal
      cortex (the rational filter) is active. This allows the memory to be reprocessed with the
      logical brain online &mdash; something that cannot happen during sleep nightmares, where the
      prefrontal cortex is suppressed. The result: the memory's emotional weight gradually decreases
      until normal consolidation can integrate it.<br><br>
      <b>The network perspective:</b> Trauma is not a content problem (the memory itself). It is a
      <em>weight</em> problem (the emotional intensity is too high for the consolidation system).
      Treatment is not about erasing the memory. It is about reducing its weight until the network
      can integrate it like any other high-emotion memory &mdash; vivid but not overwhelming.
    </div>
  </div>

  <!-- Neuroplasticity -->
  <div class="sub-section">
    <h3>Neuroplasticity</h3>
    <div class="info">
      <b>The network's ability to rewire itself.</b> Neuroplasticity is the mechanism that makes
      everything else on this page possible. Without it, encoding would not work, emotional
      weighting would not work, belief propagation would not work, neural writing would be
      impossible. Plasticity is the capacity to form new connections, strengthen existing ones,
      weaken unused ones, and reorganize structure in response to experience.<br><br>
      <b>Why children learn faster:</b> Young brains are more plastic &mdash; connections form
      easily, prune aggressively, and reorganize quickly. A child's network is optimized for
      rapid acquisition at the cost of stability. An adult's network is optimized for stability
      at the cost of flexibility. This is not a decline &mdash; it is an adaptive shift. A
      network that kept childhood-level plasticity into adulthood would never build reliable
      expertise because its structure would keep changing.<br><br>
      <b>Critical periods:</b> Certain types of learning have windows where plasticity is
      exceptionally high. Language acquisition peaks before age 7. Visual processing calibration
      happens in the first few years. Absolute pitch develops only with early musical training.
      After the critical period closes, the same learning is still possible but requires dramatically
      more effort &mdash; the network has solidified and rewiring it requires overcoming existing
      structure rather than building on blank space.<br><br>
      <b>Maintaining plasticity in adulthood:</b> Plasticity does not disappear in adults &mdash;
      it decreases. Several factors can maintain or restore it:<br>
      &bull; <b>Novel experiences</b> &mdash; anything genuinely new forces the network to form
      connections it does not have. Travel, new skills, unfamiliar social contexts.<br>
      &bull; <b>Physical exercise</b> &mdash; increases BDNF (brain-derived neurotrophic factor),
      which directly promotes synapse formation and strengthening.<br>
      &bull; <b>Sleep</b> &mdash; consolidation is where new connections get integrated. Poor sleep
      means poor plasticity.<br>
      &bull; <b>Challenging learning</b> &mdash; not just consuming information but actively
      struggling with material at the edge of your ability. The struggle IS the rewiring.<br>
      &bull; <b>Social interaction</b> &mdash; other humans are the most complex, unpredictable
      stimulus in the environment. Genuine conversation forces more network adaptation than almost
      any other activity.<br><br>
      <b>For neural writing:</b> Plasticity is what makes BCI-based learning possible. A more
      plastic brain would accept injected connections more readily. This suggests that the best
      neural writing protocols would include plasticity-enhancing preparation &mdash; exercise,
      sleep optimization, and novelty exposure before attempting to write new pathways.
    </div>
  </div>

  <!-- DSM-5 Conditions as Network States -->
  <div class="sub-section">
    <h3>DSM-5 Conditions as Network States</h3>
    <div style="display:flex;gap:16px;margin-top:12px">
      <!-- Sidebar nav -->
      <div style="flex:0 0 160px;position:sticky;top:50px;align-self:flex-start;
           max-height:calc(100vh - 70px);overflow-y:auto">
        <div style="font-size:10px;color:var(--accent);font-weight:bold;margin-bottom:8px">Conditions</div>
        <div style="display:flex;flex-direction:column;gap:2px;font-size:10px">
          <a href="#dsm-intro" style="color:var(--dim);padding:3px 8px;border-radius:3px;border-left:2px solid transparent;text-decoration:none"
             onmouseover="this.style.color='var(--text)';this.style.borderLeftColor='var(--accent)'"
             onmouseout="this.style.color='var(--dim)';this.style.borderLeftColor='transparent'">Overview</a>
          <a href="#dsm-depression" style="color:var(--dim);padding:3px 8px;border-radius:3px;border-left:2px solid transparent;text-decoration:none"
             onmouseover="this.style.color='var(--text)';this.style.borderLeftColor='#4fc3f7'"
             onmouseout="this.style.color='var(--dim)';this.style.borderLeftColor='transparent'">Depression</a>
          <a href="#dsm-anxiety" style="color:var(--dim);padding:3px 8px;border-radius:3px;border-left:2px solid transparent;text-decoration:none"
             onmouseover="this.style.color='var(--text)';this.style.borderLeftColor='#ffb74d'"
             onmouseout="this.style.color='var(--dim)';this.style.borderLeftColor='transparent'">Anxiety</a>
          <a href="#dsm-bipolar" style="color:var(--dim);padding:3px 8px;border-radius:3px;border-left:2px solid transparent;text-decoration:none"
             onmouseover="this.style.color='var(--text)';this.style.borderLeftColor='#81c784'"
             onmouseout="this.style.color='var(--dim)';this.style.borderLeftColor='transparent'">Bipolar</a>
          <a href="#dsm-schizophrenia" style="color:var(--dim);padding:3px 8px;border-radius:3px;border-left:2px solid transparent;text-decoration:none"
             onmouseover="this.style.color='var(--text)';this.style.borderLeftColor='#e53935'"
             onmouseout="this.style.color='var(--dim)';this.style.borderLeftColor='transparent'">Schizophrenia</a>
          <a href="#dsm-ocd" style="color:var(--dim);padding:3px 8px;border-radius:3px;border-left:2px solid transparent;text-decoration:none"
             onmouseover="this.style.color='var(--text)';this.style.borderLeftColor='#ba68c8'"
             onmouseout="this.style.color='var(--dim)';this.style.borderLeftColor='transparent'">OCD</a>
          <a href="#dsm-adhd" style="color:var(--dim);padding:3px 8px;border-radius:3px;border-left:2px solid transparent;text-decoration:none"
             onmouseover="this.style.color='var(--text)';this.style.borderLeftColor='#4fc3f7'"
             onmouseout="this.style.color='var(--dim)';this.style.borderLeftColor='transparent'">ADHD</a>
          <a href="#dsm-autism" style="color:var(--dim);padding:3px 8px;border-radius:3px;border-left:2px solid transparent;text-decoration:none"
             onmouseover="this.style.color='var(--text)';this.style.borderLeftColor='#81c784'"
             onmouseout="this.style.color='var(--dim)';this.style.borderLeftColor='transparent'">Autism</a>
          <a href="#dsm-dissociative" style="color:var(--dim);padding:3px 8px;border-radius:3px;border-left:2px solid transparent;text-decoration:none"
             onmouseover="this.style.color='var(--text)';this.style.borderLeftColor='#f06292'"
             onmouseout="this.style.color='var(--dim)';this.style.borderLeftColor='transparent'">Dissociative</a>
          <a href="#dsm-bpd" style="color:var(--dim);padding:3px 8px;border-radius:3px;border-left:2px solid transparent;text-decoration:none"
             onmouseover="this.style.color='var(--text)';this.style.borderLeftColor='#ffb74d'"
             onmouseout="this.style.color='var(--dim)';this.style.borderLeftColor='transparent'">Borderline</a>
          <a href="#dsm-insomnia" style="color:var(--dim);padding:3px 8px;border-radius:3px;border-left:2px solid transparent;text-decoration:none"
             onmouseover="this.style.color='var(--text)';this.style.borderLeftColor='#4fc3f7'"
             onmouseout="this.style.color='var(--dim)';this.style.borderLeftColor='transparent'">Insomnia</a>
          <a href="#dsm-eating" style="color:var(--dim);padding:3px 8px;border-radius:3px;border-left:2px solid transparent;text-decoration:none"
             onmouseover="this.style.color='var(--text)';this.style.borderLeftColor='#ba68c8'"
             onmouseout="this.style.color='var(--dim)';this.style.borderLeftColor='transparent'">Eating Disorders</a>
          <a href="#dsm-summary" style="color:var(--dim);padding:3px 8px;border-radius:3px;border-left:2px solid transparent;text-decoration:none"
             onmouseover="this.style.color='var(--text)';this.style.borderLeftColor='var(--accent)'"
             onmouseout="this.style.color='var(--dim)';this.style.borderLeftColor='transparent'">Key Insight</a>
        </div>
      </div>
      <!-- Content -->
      <div style="flex:1;min-width:0">
    <div class="info" id="dsm-intro">
      Every condition below is a <b>configuration</b> of the same underlying network &mdash; not
      a broken brain, but a brain operating under specific parameters. The Axona framework
      reframes diagnosis as <b>network state identification</b>: where is this brain on the
      novelty/coherence map, what is its bandwidth, how are its weights distributed, and what
      consolidation patterns are active?
    </div>

    <!-- Depression -->
    <div class="info" id="dsm-depression">
      <b style="color:#4fc3f7">Major Depressive Disorder</b><br>
      <b>Network state: stagnation quadrant.</b> Low novelty + low coherence. The network has
      gone quiet &mdash; few new connections form, existing connections weaken, activation is
      globally suppressed. Everything feels flat because the network IS flat: emotional weighting
      is dampened, so nothing gets encoded as important.<br><br>
      <b>Anhedonia</b> (inability to feel pleasure) is the reward network losing its weights.
      Activities that used to activate strong pathways now produce minimal signal. The brain
      is not choosing to be joyless &mdash; the connections that produced joy have weakened below
      the activation threshold.<br><br>
      <b>Rumination</b> is a stuck activation loop. A small cluster of negative nodes activates
      repeatedly because there is not enough novelty to pull activation elsewhere. The network
      defaults to its strongest remaining pathway, which in depression is often self-critical.<br><br>
      <b>Treatment through the model:</b> Antidepressants increase neurotransmitter availability,
      which raises the baseline activation level across the network &mdash; more signal, more chance
      of new connections forming. CBT works by deliberately creating alternative pathways
      (reframing = building new edges that compete with the negative loop). Exercise increases
      BDNF, directly promoting new connection formation. All three are different routes to the
      same goal: reactivate a network that has gone too quiet.
    </div>

    <!-- Anxiety -->
    <div class="info" id="dsm-anxiety">
      <b style="color:#ffb74d">Generalized Anxiety Disorder</b><br>
      <b>Network state: overactivated threat detection.</b> The threat-related nodes are weighted
      so heavily that they activate on minimal cues. The brain's danger-monitoring system is
      always on, consuming bandwidth that would otherwise be available for creative or productive
      processing.<br><br>
      <b>Why anxiety consumes bandwidth:</b> The brain allocates processing priority to perceived
      threats. In GAD, the threat threshold is set too low &mdash; ordinary situations trigger
      threat-level activation. The result: constant background processing of danger signals,
      leaving minimal bandwidth for anything else. This is why anxious people report difficulty
      concentrating, making decisions, or thinking clearly. The bandwidth is not gone &mdash; it
      is allocated to threat monitoring.<br><br>
      <b>Panic attacks</b> are cascading activation events. A small threat signal triggers
      neighboring threat nodes, which trigger more, which trigger physiological responses (heart
      rate, breathing), which the brain interprets as MORE evidence of threat, which triggers
      more activation. The network enters a positive feedback loop. The panic is not about the
      original trigger &mdash; it is about the cascade.<br><br>
      <b>Phobias</b> are a single threat node with disproportionately high weight. The spider
      node (or height node, or social-evaluation node) is encoded at extreme brightness,
      probably from a childhood experience or inherited predisposition. Everything near that
      node in the network triggers avoidance, even when logically safe.
    </div>

    <!-- Bipolar -->
    <div class="info" id="dsm-bipolar">
      <b style="color:#81c784">Bipolar Disorder</b><br>
      <b>Network state: oscillation between chaos and stagnation.</b> In mania, the network
      enters the chaos quadrant &mdash; extremely high novelty, low coherence. Ideas form
      rapidly, connections fire everywhere, grandiosity and racing thoughts reflect a network
      generating at maximum speed with minimal filtering. In depressive episodes, the same
      network collapses to stagnation &mdash; low novelty, low coherence, minimal activation.<br><br>
      <b>Mania is not genius.</b> It feels like the genius quadrant because novelty is extremely
      high. But coherence is low &mdash; the ideas do not hold together, cannot be executed,
      and the person cannot distinguish good insights from garbage. The network is producing
      massive output with no quality filter. Some manic ideas are genuinely brilliant (they
      happened to land in the genius zone briefly), which is why bipolar disorder is
      overrepresented among creative people. But most manic output is chaos that looks like
      genius from the inside.<br><br>
      <b>The cycle:</b> Mania depletes the network's resources (bandwidth consumed, consolidation
      overwhelmed, connections formed faster than they can stabilize). The inevitable crash into
      depression is the system collapsing from exhaustion &mdash; the opposite extreme of the
      same instability. Treatment with mood stabilizers narrows the oscillation range, keeping
      the network closer to the center of the state space.
    </div>

    <!-- Schizophrenia -->
    <div class="info" id="dsm-schizophrenia">
      <b style="color:#e53935">Schizophrenia</b><br>
      <b>Network state: permanent chaos quadrant with broken reality anchors.</b> Extremely high
      novelty generation with severely impaired coherence. The network forms connections that a
      healthy brain would immediately prune &mdash; between unrelated concepts, between perception
      and imagination, between self and other.<br><br>
      <b>Hallucinations</b> are internal activations that the network cannot distinguish from
      external input. In a healthy brain, internally generated patterns are tagged as "self-produced"
      and filtered. In schizophrenia, this tagging system is broken &mdash; the voice activation
      pattern fires and the network processes it as real incoming sound.<br><br>
      <b>Delusions</b> are belief propagation with a broken reality-check. A novel connection
      forms ("the government is watching me") and instead of being tested against evidence and
      pruned, it gets reinforced. Each confirming detail strengthens the pathway. Contradicting
      evidence cannot compete because the coherence system that would catch the contradiction
      is impaired.<br><br>
      <b>Thought disorder</b> (loose associations, word salad) is the network following connections
      that a healthy brain would suppress. Each word activates the next by proximity in the graph
      rather than by logical relevance. The path through the network is valid at each step but
      incoherent as a sequence &mdash; like following every link on Wikipedia instead of reading
      one article.
    </div>

    <!-- OCD -->
    <div class="info" id="dsm-ocd">
      <b style="color:#ba68c8">Obsessive-Compulsive Disorder</b><br>
      <b>Network state: stuck activation loop with failed completion signal.</b> A circuit fires
      (the obsession), triggers a behavioral response (the compulsion), but the completion
      signal that should end the loop never arrives. So the circuit fires again. And again.<br><br>
      <b>Why the loop does not close:</b> In a healthy brain, performing the safety behavior
      (checking the lock, washing hands) produces a "done" signal that deactivates the threat
      node. In OCD, the "done" signal is too weak or the threat node's weight is too high. The
      activation persists after the behavior, demanding another cycle. The person KNOWS the door
      is locked. The network does not.<br><br>
      <b>Intrusive thoughts</b> are the network testing connections that a healthy brain would
      suppress instantly. Everyone has bizarre or disturbing thoughts &mdash; they are the brain's
      novelty engine producing random associations. Normally they flash and vanish (low weight,
      immediately pruned). In OCD, these thoughts get flagged as important (high emotional weight),
      which makes them recur, which increases their weight further. The loop is: random thought
      &rarr; emotional reaction &rarr; increased weight &rarr; recurrence &rarr; more emotional
      reaction.
    </div>

    <!-- ADHD -->
    <div class="info" id="dsm-adhd">
      <b style="color:#4fc3f7">Attention-Deficit/Hyperactivity Disorder</b><br>
      <b>Network state: broadened activation with reduced sustained focus.</b> The attention
      spotlight is wider and dimmer rather than narrow and bright. More cross-cluster activation
      (good for novelty), less ability to maintain deep activation in one region (bad for
      sustained tasks).<br><br>
      <b>Not a deficit:</b> The name is misleading. People with ADHD do not lack attention &mdash;
      they allocate it differently. The network distributes activation broadly instead of
      concentrating it. This produces: difficulty with sustained boring tasks (not enough depth
      in one region), hyperfocus on interesting tasks (when the broad spotlight converges on
      something engaging, activation depth is exceptional), higher sensitivity to novelty (the
      broad spotlight catches things a narrow one would miss).<br><br>
      <b>Dopamine and ADHD:</b> The dopamine system regulates what gets attention priority.
      In ADHD, the baseline dopamine signal is lower, meaning the threshold for "this is worth
      focusing on" is higher. Only highly stimulating or novel inputs clear the threshold.
      Stimulant medications (Adderall, Ritalin) increase dopamine, effectively lowering the
      attention threshold so that ordinary tasks can compete for focus.<br><br>
      <b>ADHD in the modern world:</b> An ADHD brain in a hunter-gatherer environment would
      be an asset &mdash; broad scanning, quick novelty detection, rapid context switching.
      In a world of desks, paperwork, and 90-minute lectures, the same brain is labeled
      disordered. The network is not broken. It is optimized for an environment that no longer
      exists.
    </div>

    <!-- Autism -->
    <div class="info" id="dsm-autism">
      <b style="color:#81c784">Autism Spectrum</b><br>
      <b>Network state: high local coherence, reduced cross-cluster connectivity.</b> Within a
      domain of interest, the network is exceptionally dense &mdash; deep expertise, fine
      distinctions, precise pattern recognition. Between domains, connections are sparser than
      typical &mdash; making social cues, abstract metaphor, and context-switching harder.<br><br>
      <b>Intense focus:</b> The "special interest" phenomenon is a cluster with extraordinarily
      high internal connectivity. Activation within this cluster is deep and sustained &mdash;
      producing expertise that can exceed neurotypical levels. The trade-off: bandwidth allocated
      to the interest cluster is not available for other regions.<br><br>
      <b>Sensory sensitivity:</b> In a typical brain, sensory input gets filtered before reaching
      conscious processing &mdash; most signals are suppressed as noise. In autism, more sensory
      data passes the filter, reaching the network at full strength. This produces both heightened
      perception (noticing patterns others miss) and overwhelm (too much unfiltered input
      consuming bandwidth). A loud room is not just uncomfortable &mdash; it is a bandwidth
      crisis.<br><br>
      <b>Social processing:</b> Social interaction requires rapid cross-cluster activation &mdash;
      reading facial expressions (visual), interpreting tone (auditory), modeling intentions
      (theory of mind), generating appropriate responses (language + social norms), all
      simultaneously. If cross-cluster connectivity is lower, this multi-region coordination
      is more effortful. The social information is not invisible &mdash; it requires more
      bandwidth to process. Autistic masking (performing neurotypical social behavior) is
      the equivalent of running a computationally expensive program on limited bandwidth.
    </div>

    <!-- Dissociative Disorders -->
    <div class="info" id="dsm-dissociative">
      <b style="color:#f06292">Dissociative Disorders</b><br>
      <b>Network state: fragmented &mdash; clusters disconnected from each other.</b>
      Dissociation is what happens when the network partitions itself under extreme stress.
      Instead of collapsing into chaos or stagnation, the brain <em>disconnects</em> regions
      to protect the system from overwhelming input.<br><br>
      <b>Depersonalization</b> is the self-model cluster disconnecting from the sensory
      cluster. You can see your body, but it does not feel like yours &mdash; because the
      connection between "what I perceive" and "who I am" has been severed. The information
      is all there. The links between the information are gone.<br><br>
      <b>Dissociative Identity Disorder</b> (DID) may represent the most extreme form of
      network fragmentation: separate clusters develop independent activation patterns,
      independent memory stores, and independent self-models. Each "identity" is a coherent
      sub-network that operates independently because the cross-cluster connections were
      severed (usually by severe childhood trauma). The network did not break randomly &mdash;
      it partitioned strategically to contain damage.<br><br>
      <b>Dissociation as a protection mechanism:</b> When the entire network is being
      overwhelmed (trauma, extreme pain, unprocessable horror), disconnecting regions prevents
      total collapse. It is the network equivalent of a circuit breaker. The cost is lost
      integration. The benefit is survival.
    </div>

    <!-- BPD -->
    <div class="info" id="dsm-bpd">
      <b style="color:#ffb74d">Borderline Personality Disorder</b><br>
      <b>Network state: unstable emotional weighting with rapid encoding/erasure cycles.</b>
      The emotional intensity dial is turned to maximum and fluctuates rapidly. Memories and
      beliefs about people get encoded at extreme brightness &mdash; then re-encoded at the
      opposite extreme when the emotional state shifts.<br><br>
      <b>Splitting</b> (seeing someone as all-good or all-bad) is the network encoding a person
      node at extreme positive weight, then rapidly overwriting it with extreme negative weight.
      There is no moderate middle &mdash; the emotional encoding system does not produce moderate
      signals. Everything is maximum brightness, maximum contrast. The person is either idealized
      (every connection positive) or devalued (every connection negative), and the flip between
      states can happen in minutes.<br><br>
      <b>Fear of abandonment</b> is a threat node with connections to virtually every social
      relationship node in the network. Any signal that could indicate abandonment &mdash; a late
      reply, a change in tone, a cancelled plan &mdash; activates the threat cascade across the
      entire social region. The response (desperate attempts to prevent abandonment) makes sense
      as a network reaction: if your most critical threat node just fired, every available
      resource gets redirected to addressing it.<br><br>
      <b>Emotional dysregulation:</b> The emotional weighting system in BPD responds to input
      with disproportionate intensity and lacks the damping that a typical brain applies. A
      small slight produces a large encoding. A small kindness produces an equally large encoding
      in the opposite direction. The network is constantly being rewritten by emotional storms
      that a typical brain would weather as minor fluctuations.
    </div>

    <!-- Insomnia -->
    <div class="info" id="dsm-insomnia">
      <b style="color:#4fc3f7">Insomnia</b><br>
      <b>Network state: failed consolidation.</b> The network cannot enter the maintenance mode
      it needs. New connections accumulate without being tested, pruned, or integrated. Over time,
      this produces exactly what insomnia patients report: difficulty concentrating (too much
      unintegrated noise), emotional instability (emotional weights not properly calibrated during
      sleep), memory problems (encoding happens but consolidation does not), and progressive
      cognitive decline.<br><br>
      <b>The irony of trying to sleep:</b> Anxiety about not sleeping activates the threat
      monitoring system, which consumes bandwidth, which prevents the relaxation needed for
      sleep onset. The network is trying to solve the problem of insufficient consolidation
      by activating MORE processing &mdash; the opposite of what is needed. This is why sleep
      hygiene (reducing activation before bed) and CBT-I (breaking the anxiety-about-sleep loop)
      are more effective than simply trying harder to sleep.
    </div>

    <!-- Eating Disorders -->
    <div class="info" id="dsm-eating">
      <b style="color:#ba68c8">Eating Disorders</b><br>
      <b>Network state: distorted body-image node with hijacked control pathways.</b> The
      self-perception cluster encodes body image at a weight that overrides sensory input &mdash;
      the person sees their actual body but the network's internal model disagrees. The belief
      ("I am too large") is stronger than the evidence ("the scale says otherwise") because
      the belief node has been reinforced thousands of times by emotional encoding while the
      evidence is processed through a lower-weight rational pathway.<br><br>
      <b>Anorexia</b> shares mechanics with addiction: the restriction behavior becomes a
      heavily reinforced pathway that provides a sense of control (reward signal) in a network
      that otherwise feels chaotic. Each successful restriction reinforces the pathway. The
      body-image distortion is a belief propagation failure &mdash; the authority node (internal
      critic) overwhelms all other evidence sources.<br><br>
      <b>Binge eating</b> is a bandwidth collapse followed by reward-seeking. When cognitive
      load exceeds capacity (stress, emotion, exhaustion), the network defaults to its
      strongest reward pathway. For some brains, that pathway is food. The binge is not a
      choice &mdash; it is what the network does when higher-order control runs out of bandwidth.
    </div>

    <div class="info" id="dsm-summary">
      <b>The key insight across all conditions:</b> No condition listed above is a "broken brain."
      Each is a network operating under specific parameters &mdash; weights too high or too low,
      connections too dense or too sparse, consolidation too aggressive or too weak, novelty
      too fast or too slow, coherence filters working or impaired. <b>Diagnosis is network state
      identification. Treatment is network state modification.</b> The same system that produces
      genius, flow, and creativity also produces depression, psychosis, and addiction. The
      difference is configuration, not quality.
    </div>
      </div><!-- end content column -->
    </div><!-- end flex layout -->
  </div><!-- end sub-section -->

  <div class="sub-section">
  <h3>Trauma Loops &amp; Therapy</h3>
  <p class="desc">
    A pathway encoded under extreme emotion can become a trap: every activation gets pulled
    back into the same loop, no matter where you start. Exposure and reframe are the network
    operations that dismantle it.
  </p>
  <div class="canvas-box">
    <canvas id="trauma-canvas" width="960" height="380"></canvas>
  </div>
  <div class="controls">
    <button onclick="traumaActivate()">Activate Something Unrelated</button>
    <button onclick="traumaTherapy()">Therapy: Add Cross-Link</button>
    <button onclick="traumaReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      loop captures: <b style="color:var(--warn)" id="trauma-caps">0</b>
      &nbsp; escapes: <b style="color:var(--accent2)" id="trauma-esc">0</b>
      &nbsp; cross-links: <b style="color:var(--accent)" id="trauma-links">0</b>
    </span>
  </div>
  <div class="info">
    <b>How a trauma loop forms:</b> When an experience encodes under extreme emotional load,
    the edges formed during that moment get a massive weight multiplier (see the memory
    section &mdash; emotion is the brightness dial). If the experience also involved a
    self-reinforcing pattern &mdash; the same thoughts, the same bodily state, the same
    imagery &mdash; the pathway becomes a closed loop. From then on, any activation that
    even glances at the loop gets captured by it. The system spirals back to the same
    memory, the same feeling, the same conclusions.<br><br>
    <b>Why willpower does not work:</b> Trying to "not think about it" is still traversing
    nodes adjacent to the loop, which activates the loop. The loop's weight is higher than
    any competing pathway, so every attempt to avoid it pulls you closer. This is not
    weakness. It is the network doing exactly what its weights tell it to do.<br><br>
    <b>What therapy actually does:</b> Exposure (talking about the memory in a safe setting)
    activates the loop under new emotional context &mdash; which means new edges form, with
    the same nodes but different weights. Reframe (assigning new meaning) adds cross-links
    from the loop to other parts of the network, so activation has somewhere else to go.
    Over many sessions, the monopoly breaks. The loop is still there &mdash; you cannot
    delete a memory &mdash; but it is no longer the only path. Click "Therapy" repeatedly
    and watch activation start escaping.
  </div>
  </div>

  <div class="sub-section">
  <h3>Addiction &mdash; Weight Hijacking</h3>
  <p class="desc">
    Addiction is not moral failure. It is one pathway's reward weight getting amplified
    until it crowds everything else out. Raise the substance gain and watch the other
    rewards go dim.
  </p>
  <div class="canvas-box">
    <canvas id="addict-canvas" width="960" height="360"></canvas>
  </div>
  <div class="controls">
    <button onclick="addictPulse()">Seek Reward</button>
    <button onclick="addictReset()">Reset</button>
    <label style="display:flex;align-items:center;gap:8px">
      <span>substance gain:</span>
      <input type="range" id="addict-gain" min="100" max="800" value="100" style="width:140px">
      <span class="stat-val" id="addict-gain-val">1.0×</span>
    </label>
  </div>
  <div class="info">
    <b>The mechanism:</b> A healthy reward system distributes activation across many
    pathways &mdash; food, sex, social bonding, music, movement, curiosity, mastery, rest.
    Each has its own weight. Each pulls some of the brain's activation budget. The system
    is in balance because no single pathway dominates.<br><br>
    <b>Addiction breaks the balance</b> by multiplying one pathway's reward weight by 5,
    10, sometimes 100&times;. The substance hijacks the dopamine system and announces
    "this is the most important thing." Once the weight is high enough, every activation
    that reaches anywhere near the pathway gets captured by it. Other rewards still exist,
    but they cannot compete &mdash; their weights did not change, while the addict's did.<br><br>
    <b>Why quitting is hard:</b> It is not lack of willpower. It is weight asymmetry.
    Asking a network with a 10&times; multiplier on one pathway to "just choose something
    else" is asking it to violate its own gradient. The gradient wins every time. Recovery
    works not by willpower but by gradually reducing the hijacked weight (time, abstinence,
    replacement rewards) and strengthening the weights of other pathways (new habits, new
    contexts, new people) until balance returns.
  </div>
  </div>

  <div class="sub-section">
  <h3>Grief &mdash; Network Rewiring After a Lost Node</h3>
  <p class="desc">
    Grief is not forgetting. It is structural rebuilding. When a high-weight node is
    removed, every edge that depended on it dangles. The network has to redistribute
    activation across the rest of its structure &mdash; and that takes real time, because
    there is real work to do.
  </p>
  <div class="canvas-box">
    <canvas id="grief-canvas" width="960" height="380"></canvas>
  </div>
  <div class="controls">
    <button onclick="griefLose()">Lose Person</button>
    <button onclick="griefStep()">Grieve (Rewire One Edge)</button>
    <button onclick="griefAuto()">Auto-Rewire</button>
    <button onclick="griefReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      dangling edges: <b style="color:var(--warn)" id="grief-dangling">0</b>
      &nbsp; rewired: <b style="color:var(--accent2)" id="grief-rewired">0</b>
    </span>
  </div>
  <div class="info">
    <b>The model:</b> A person in your life is not a single memory. It is a high-weight
    hub node with edges to dozens or hundreds of other nodes &mdash; places, routines,
    jokes, arguments, phrases, plans, recipes, the song they liked, the chair they sat
    in, the way you narrated your day to them. Every one of those edges was a pathway
    that routed activation through the person. When the node disappears, none of the
    memories disappear with it &mdash; but all of their pathways are suddenly broken.
    Activation lands on a pathway and finds no target.<br><br>
    <b>Why grief feels like being ambushed:</b> You cannot grieve all at once because you
    cannot be in all your pathways at once. You find the broken edges one at a time,
    whenever normal life happens to traverse them. You pick up their coffee cup. You hear
    their song on the radio. You start to tell them about your day. Each is a separate
    moment of "oh, that path goes nowhere now" &mdash; and each requires a separate small
    rewiring. This is why grief is not a duration but a rate. Six months, a year, several
    years &mdash; however long it takes for the network's normal traversal to have touched
    and repaired enough of the broken edges to no longer surprise itself.<br><br>
    <b>What "healing" actually is:</b> Not deletion. The node stays &mdash; dimmed,
    sometimes reactivated &mdash; but the edges that used to route through it have been
    redistributed to other nodes or allowed to weaken. The network can now function
    without repeatedly hitting empty pathways. The memory of the person is not gone; it
    is <em>integrated</em>. Loss is rewriting, not erasure.
  </div>
  </div>

  <div class="sub-section">
  <h3>Learned Helplessness &mdash; The Action Pathway Collapses</h3>
  <p class="desc">
    When actions repeatedly fail to produce outcomes, the edges connecting "try" to
    "reward" stop being reinforced. Eventually they fall below the threshold where
    activation even flows through them. The system has learned that nothing works &mdash;
    and that learning is correct, given the evidence.
  </p>
  <div class="canvas-box">
    <canvas id="help-canvas" width="960" height="360"></canvas>
  </div>
  <div class="controls">
    <button onclick="helpTry()">Try an Action</button>
    <button onclick="helpAllowRewards()">Restore Working World</button>
    <button onclick="helpReset()">Reset</button>
    <label style="display:flex;align-items:center;gap:8px">
      <span>world responsiveness:</span>
      <input type="range" id="help-world" min="0" max="100" value="0" style="width:120px">
      <span class="stat-val" id="help-world-val">0%</span>
    </label>
    <span style="margin-left:auto;color:var(--dim)">
      attempts: <b id="help-tries">0</b>
      &nbsp; rewards: <b style="color:var(--accent2)" id="help-rewards">0</b>
      &nbsp; action weight: <b style="color:var(--warn)" id="help-weight">1.00</b>
    </span>
  </div>
  <div class="info">
    <b>The original experiment</b> (Seligman &amp; Maier, 1967): dogs in one group learned
    they could escape a shock by jumping a barrier. Dogs in a second group received the
    same shocks but with no escape option. Later, both groups were put in a box where
    escape was possible. The first group jumped. The second group lay down and took the
    shocks. They had learned that their actions did not matter &mdash; and they had
    generalized that learning to a new situation where it no longer applied.<br><br>
    <b>The mechanism:</b> Every attempted action is a small prediction ("if I do X,
    reward Y will follow"). When the prediction fails repeatedly, the edge between action
    and outcome weakens. After enough failures, the edge is too weak to drive action at
    all &mdash; not because the system is "giving up" in some dramatic sense, but because
    the network literally no longer represents the action as viable. The activation
    gradient points toward inaction not because inaction is preferred, but because every
    other pathway has been ground down to zero.<br><br>
    <b>Why "just try harder" fails:</b> The person cannot. The pathway they would need to
    activate has decayed below threshold. Recovery is not an act of will &mdash; it is
    slowly rebuilding the edge by noticing and amplifying even tiny successes (the world
    responsiveness slider, turned up). Click it up and start pressing Try Action &mdash;
    the weight slowly recovers. This is why depression is so hard to talk people out of:
    you are asking a network with dead action-reward edges to run a computation that
    those edges are needed for.
  </div>
  </div>

  <div class="sub-section">
  <h3>Phantom Limbs &mdash; Body Map Outliving the Body</h3>
  <p class="desc">
    The brain's body map is a network of nodes, not a set of sensors. When a limb is
    amputated, the sensors are gone but the map node and its connections remain. The
    network keeps generating predictions about a limb that no longer exists &mdash;
    sometimes as sensation, sometimes as pain.
  </p>
  <div class="canvas-box">
    <canvas id="phantom-canvas" width="960" height="360"></canvas>
  </div>
  <div class="controls">
    <button onclick="phantomAmputate()">Amputate</button>
    <button onclick="phantomMirror()">Mirror Therapy</button>
    <button onclick="phantomReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      phantom activity: <b style="color:var(--warn)" id="phantom-act">0.00</b>
    </span>
  </div>
  <div class="info">
    <b>The mechanism:</b> The somatosensory cortex contains a topographic map of the
    body &mdash; each limb has a dedicated region of neurons that represents its
    sensations and movements. After amputation, those neurons do not disappear. They
    keep receiving input from upstream motor prediction and downstream neighbor
    regions. With no sensory signal to correct them, they produce the network's guess
    at what the limb should be feeling. The patient experiences a hand that is not
    there, often in a specific posture, sometimes cramped or painful.<br><br>
    <b>Phantom pain</b> is particularly cruel. The limb that causes the pain cannot be
    moved, rubbed, or even reached &mdash; there is nothing to do to the body that would
    produce corrective input. The prediction runs unchecked.<br><br>
    <b>Mirror therapy</b> (Ramachandran 1995) exploits the prediction mechanism rather
    than fighting it. By placing a mirror so the intact limb's reflection appears where
    the missing limb was, the patient sees a "limb" moving when they move the intact
    one. The visual input satisfies the network's prediction about the missing limb,
    the residual scorer stops firing, and the phantom sensation fades &mdash; sometimes
    permanently. It is not a trick. The brain's body map is genuinely updating its
    forecast based on the new (false but consistent) visual evidence.
  </div>
  </div>

  <div class="sub-section">
  <h3>Depression &mdash; The Flattened Reward Landscape</h3>
  <p class="desc">
    Depression is not sadness. It is what happens when the entire reward landscape
    flattens toward zero simultaneously &mdash; every pathway that used to produce
    dopamine still exists, but the gradients have collapsed. Nothing pulls harder than
    anything else. There is no "want" to orient toward.
  </p>
  <div class="canvas-box">
    <canvas id="dep-canvas" width="960" height="360"></canvas>
  </div>
  <div class="controls">
    <label style="display:flex;align-items:center;gap:8px">
      <span>depression severity:</span>
      <input type="range" id="dep-sev" min="0" max="100" value="0" style="width:140px">
      <span class="stat-val" id="dep-sev-val">0%</span>
    </label>
    <button onclick="depMove()">Try to Move (seek any reward)</button>
    <button onclick="depReset()">Reset</button>
  </div>
  <div class="info">
    <b>The reward landscape in a healthy network</b> is a terrain of peaks: food looks
    good over here, social contact looks good over there, mastery looks good further
    out, rest looks good up high. Motivation works by following the gradient &mdash; the
    system gets pulled toward whichever peak is currently highest. At any moment there
    is <em>some</em> peak worth walking toward.<br><br>
    <b>Depression flattens the landscape.</b> Not selectively &mdash; all rewards lose
    their height together. Food stops looking good. Sex stops looking good. Hobbies
    stop looking good. Social contact stops looking good. The patient knows
    intellectually that these things used to matter, but the felt gradient is gone.
    "I should want to go see my friends, but I don't." That is not laziness. It is the
    literal absence of the reward-height that would pull the system toward them.<br><br>
    <b>Why "just do something you enjoy" fails:</b> The patient cannot find the
    gradient. They can do an action (walk outside, eat a meal, call a friend) and the
    action produces no felt reward. The prediction that "this will feel good" does not
    get confirmed, so the pathway does not get reinforced, and next time the pull is
    even weaker.<br><br>
    <b>Why exercise and sunlight sometimes work:</b> They do not "cheer you up" &mdash;
    they partially restore the network's ability to generate reward signal at all.
    They raise the baseline of the landscape. If the landscape is too flat, any peak
    is better than none, and the system can start moving again. From there, the normal
    reinforcement mechanism can slowly rebuild the other pathways' heights. But it has
    to start with something that moves the baseline, because talk alone does not.
  </div>
  </div>

  <div class="sub-section">
  <h3>Memory Reconsolidation &mdash; Every Recall Rewrites</h3>
  <p class="desc">
    A memory is not a file you retrieve. Every time you recall it, the trace becomes
    briefly malleable and then gets re-encoded with whatever context was around at
    the moment of recall. Over many recalls, the memory drifts toward the person you
    are now, not the person you were then.
  </p>
  <div class="canvas-box">
    <canvas id="recon-canvas" width="960" height="360"></canvas>
  </div>
  <div class="controls">
    <button onclick="reconEncode()">Encode Memory</button>
    <button onclick="reconRecall('safe')">Recall in Safe Context</button>
    <button onclick="reconRecall('stressful')">Recall in Stressful Context</button>
    <button onclick="reconReset()">Reset</button>
  </div>
  <div class="info">
    <b>The phenomenon</b> (Nader, Schafe &amp; LeDoux 2000): when an old fear memory is
    reactivated, there is a brief window (minutes to hours) during which the memory
    protein synthesis required to "save it back" has to happen again. During that
    window, the memory is vulnerable &mdash; it can be altered, strengthened, weakened,
    or even overwritten, depending on what the network pairs with the recall. Once the
    window closes, the new version is the memory.<br><br>
    <b>Why this is strange:</b> Your memory of something important from ten years ago
    is not a preserved recording. It is the most recent version of a memory that has
    been rewritten dozens or hundreds of times, each time slightly colored by the
    state you were in when you recalled it. The more you remember something, the less
    the current version resembles the original encoding. This is counterintuitive but
    well-documented.<br><br>
    <b>Why talk therapy works:</b> It is reconsolidation in disguise. The patient
    recalls a traumatic memory in the presence of a calm, supportive therapist and a
    safe environment. That context gets co-encoded during the recall window. Over many
    sessions, the emotional signature of the memory slowly shifts from "terrifying" to
    "difficult but bearable" &mdash; not because the event changed, but because the
    stored version of the event now carries different contextual tags. The past is
    not fixed. The only fixed thing is the current reconstruction &mdash; and even
    that is fixed only until the next time you recall it.
  </div>
  </div>

  <div class="sub-section">
  <h3>Pain &mdash; A Priority Signal, Not an Intensity</h3>
  <p class="desc">
    Pain is not a scalar reading from a sensor. It is a high-priority message generated
    by the brain after filtering raw nociception through attention, expectation, context,
    and current state. The same injury can feel agonizing in one moment and nearly
    absent in another &mdash; because pain is an output, not an input.
  </p>
  <div class="canvas-box">
    <canvas id="pain-canvas" width="960" height="340"></canvas>
  </div>
  <div class="controls">
    <label style="display:flex;align-items:center;gap:8px">
      <span>raw nociception:</span>
      <input type="range" id="pain-noc" min="0" max="100" value="60" style="width:110px">
      <span class="stat-val" id="pain-noc-val">60</span>
    </label>
    <label style="display:flex;align-items:center;gap:8px;margin-left:12px">
      <span>attention on it:</span>
      <input type="range" id="pain-att" min="0" max="100" value="70" style="width:110px">
      <span class="stat-val" id="pain-att-val">70</span>
    </label>
    <label style="display:flex;align-items:center;gap:8px;margin-left:12px">
      <span>expectation (bracing):</span>
      <input type="range" id="pain-exp" min="0" max="100" value="50" style="width:110px">
      <span class="stat-val" id="pain-exp-val">50</span>
    </label>
    <label style="display:flex;align-items:center;gap:8px;margin-left:12px">
      <span>distraction:</span>
      <input type="range" id="pain-dist" min="0" max="100" value="0" style="width:110px">
      <span class="stat-val" id="pain-dist-val">0</span>
    </label>
    <span style="margin-left:auto;color:var(--dim)">
      experienced: <b style="color:var(--warn)" id="pain-exp-val-out">0</b>
    </span>
  </div>
  <div class="info">
    <b>The evidence:</b> Soldiers with catastrophic battlefield injuries often report
    minimal pain until safety is reached, at which point the same injury becomes
    unbearable. Distraction in the ER measurably reduces reported pain for the same
    procedure. Placebo analgesics produce real opioid release. Nocebo effects (being
    told something will hurt) increase measured pain for identical stimuli. Phantom
    limbs hurt without any tissue to hurt. Chronic pain persists after the original
    injury has healed, because the pain pathway has become its own maintained signal.<br><br>
    <b>The mechanism:</b> Nociceptive signals arrive from the body and enter the
    predictor. The predictor, combined with state (attention, expectation, context,
    stress, reward-prospect), produces the pain signal that actually reaches conscious
    experience. The conscious pain is always a <b>gated and modulated</b> version of the
    raw input, never a direct reading of it. This is not "mind over matter" &mdash; it
    is how the pathway was always going to work. There is no pain sensor you can bypass
    the brain to read.<br><br>
    <b>Why this matters clinically:</b> Pain treatment that addresses only the
    nociceptive input leaves most of the modulation untouched. Treatment that also
    addresses attention (mindfulness, meditation), expectation (pain psychology,
    reframing), distraction (VR during burn treatments), and reward-prospect (meaningful
    engagement in recovery) reliably outperforms pharmacology alone. Not because the
    injury is "in your head" &mdash; the pain always was. The question is what the head
    is doing with it.
  </div>
  </div>

  <div class="sub-section">
  <h3>Rumination &mdash; The Everyday Thought Spiral</h3>
  <p class="desc">
    Rumination is trauma's quieter cousin: a pathway that gets slightly too reinforced
    by ordinary worry until every attempted escape routes through the same loop. No
    catastrophe required. Just a thought you kept returning to, enough times, in
    enough contexts, that the network can no longer find another way around it.
  </p>
  <div class="canvas-box">
    <canvas id="rum-canvas" width="960" height="360"></canvas>
  </div>
  <div class="controls">
    <button onclick="rumTrigger()">Trigger Worry</button>
    <button onclick="rumDistract()">Try to Distract</button>
    <button onclick="rumBreak()">Break the Loop (Action)</button>
    <button onclick="rumReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      loop reinforcement: <b style="color:var(--warn)" id="rum-reinf">0</b>
      &nbsp; attempts to escape: <b id="rum-escape">0</b>
    </span>
  </div>
  <div class="info">
    <b>Why rumination feels different from "just thinking about a problem":</b>
    Problem-solving makes forward progress &mdash; each pass generates new information
    and eventually the loop exits with an answer or a next action. Rumination loops
    without progress. Each pass traverses the same nodes in the same order, reaching
    the same conclusions, generating no new information, and reinforcing the loop's
    edge weights a little more. The thirtieth pass uses the same route as the first,
    but by now the route has a much deeper groove.<br><br>
    <b>Why distraction alone does not work:</b> Distracting to an unrelated topic
    just reduces activation on the loop momentarily. The loop still has its
    reinforced weights. The moment the distraction ends, the network is pulled
    straight back into it, and often the loop is slightly stronger for having
    "rested" briefly before re-engaging. This is why telling a ruminator to "think
    about something else" rarely sticks.<br><br>
    <b>What actually breaks it:</b> Physical action that redirects bandwidth to a
    sensorimotor task (walking, cold shower, calling someone, doing a physical
    chore). The action pulls the activation budget out of the loop's cortical area
    into the motor system, and for the duration of the action the loop has no fuel
    to run on. This does not delete the loop &mdash; the edges stay reinforced
    &mdash; but it interrupts the reinforcement cycle long enough for other
    pathways to regain competitive weight. Over time, that is how rumination weakens:
    not by willing it away, but by repeatedly pulling the budget out.
  </div>
  </div>

  <div class="sub-section">
  <h3>Imposter Syndrome &mdash; Attribution Asymmetry in the Self-Model</h3>
  <p class="desc">
    Some self-models are calibrated to attribute successes externally (luck,
    timing, other people) and failures internally (my fault, my shortcoming, my
    real limits). The resulting self-prediction is remarkably stable: "I am actually
    a fraud who has so far gotten away with it, and I am about to be exposed." The
    math of the self-model makes the belief immune to counter-evidence.
  </p>
  <div class="canvas-box">
    <canvas id="imp-canvas" width="960" height="380"></canvas>
  </div>
  <div class="controls">
    <button onclick="impEvent('success')">Receive a Success</button>
    <button onclick="impEvent('failure')">Receive a Failure</button>
    <button onclick="impMode('impostor')">Impostor Attribution</button>
    <button onclick="impMode('balanced')">Balanced Attribution</button>
    <button onclick="impReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      self-confidence: <b id="imp-conf" style="color:var(--accent)">0.50</b>
    </span>
  </div>
  <div class="info">
    <b>The attribution pattern:</b> Every outcome has multiple plausible causes:
    internal (my skill, my effort, my judgment) and external (other people, timing,
    luck, the task was easy). A balanced self-model updates roughly symmetrically:
    successes count as partial evidence of competence, failures as partial evidence
    of limits. An impostor-syndrome self-model updates asymmetrically: successes are
    attributed outward ("they were generous," "it was easy," "I got lucky") and
    failures are attributed inward ("this is what I actually am"). Over many events,
    this rule produces a steadily-declining internal confidence regardless of the
    actual ratio of successes to failures.<br><br>
    <b>Why the belief feels confirmed by evidence:</b> Because every data point is
    consistent with it, under the impostor reading. You got a promotion? Luck. You
    failed a task? See, that is the real you. You got praised? They are being nice.
    You got criticized? They finally noticed. The rule generates its own confirming
    interpretation of <em>any</em> outcome, so evidence cannot correct it &mdash;
    the evidence is being passed through the rule before it reaches the self-model.<br><br>
    <b>Why it is stable:</b> The self-model is a high-weight prediction (see the
    Self-as-Predicted-Node canvas). Impostor syndrome is what happens when that
    prediction is "I am about to be exposed as a fraud." The network works to
    maintain the prediction's coherence, which means incoming evidence gets reshaped
    to fit. This is not a logical error the person can fix by "realizing they are
    being unfair to themselves." It is a calibration problem in the attribution
    function, and calibration problems are hard to see from inside the function.<br><br>
    <b>What helps:</b> Writing down successes with their causes (forces the
    attribution to be made explicit, where the asymmetry becomes visible), external
    feedback from trusted sources delivered in a format that specifies the causal
    claim ("this was your skill, not luck"), and sometimes therapy specifically
    targeted at the attribution pattern. Willpower fixes nothing. Changing the
    calibration rule fixes everything.
  </div>
  </div>

  <div class="sub-section">
  <h3>Fear Conditioning &mdash; The Amygdala's One-Trial Learner</h3>
  <p class="desc">
    Most learning requires many trials. Fear learning does not. A single pairing
    of a neutral cue with a painful or threatening event is often enough to make
    the cue alone trigger the full fear response afterward &mdash; and that
    learning is remarkably resistant to erasure. One shock, one snake bite, one
    terrifying phone call, and the associated cue is weighted for life.
  </p>
  <div class="canvas-box">
    <canvas id="fear-canvas" width="960" height="360"></canvas>
  </div>
  <div class="controls">
    <button onclick="fearCondition()">Pair Cue with Shock</button>
    <button onclick="fearCuePlay()">Play Cue Alone</button>
    <button onclick="fearExtinguish()">Extinction Trial (cue, no shock)</button>
    <button onclick="fearReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      fear response: <b style="color:var(--warn)" id="fear-resp">0.00</b>
      &nbsp; extinction: <b style="color:var(--accent2)" id="fear-ext">0.00</b>
    </span>
  </div>
  <div class="info">
    <b>The mechanism:</b> The amygdala is specifically tuned for threat learning.
    Pair a cue (tone, light, place, smell) with a painful unconditioned stimulus
    and the amygdala forms a strong cue→threat association in a single trial.
    The cue alone then triggers the full response: freezing, increased heart
    rate, cortisol release, attention narrowing, prediction of danger. This is
    adaptive &mdash; in the ancestral environment, one bad encounter with a
    predator had to be enough, because a second chance was not guaranteed.<br><br>
    <b>Why it is so hard to unlearn:</b> Extinction is not erasure. When the cue
    keeps firing without the paired threat, the brain builds an
    <em>inhibitory</em> pathway that competes with the original association:
    "tone normally means shock, but in this context it does not." The original
    fear pathway is still there. In a new context, or under stress, or after
    time passes, it can reassert itself &mdash; this is called spontaneous
    recovery, and it is why exposure therapy has to be repeated across many
    contexts to generalize. Extinction builds a second weight; it does not
    delete the first.<br><br>
    <b>Clinical implications:</b> Phobias, PTSD triggers, anxiety conditioning,
    traumatic memories &mdash; all run on this machinery. The reason a single
    sound, smell, or place can trigger a full panic attack decades after the
    original event is that the amygdala's one-trial learning has no forgetting
    function. Exposure-based therapies work by overwriting, not erasing: the
    cue gets repeatedly paired with safety until the inhibitory pathway
    out-weighs the original fear pathway in most contexts. The original never
    goes away. It just stops winning the competition.<br><br>
    <b>Reconsolidation as a weapon:</b> Recent work (see the Memory
    Reconsolidation canvas) suggests the old fear memory <em>can</em> be
    modified if it is reactivated during a specific post-retrieval window and
    something new is introduced before the memory re-saves. This is the
    mechanism behind some promising PTSD treatments: deliberately recall the
    fear memory in a safe setting, then introduce new information during the
    reconsolidation window to rewrite the trace. The original may not be quite
    as permanent as the classical model suggests.
  </div>
  </div>

</div>
</div>

<!-- ═══ Tab: Applications ═══════════════════════════════════════ -->
<div class="panel" id="applications-tab">
<div class="container">
  <h2>Who Uses Axona</h2>
  <p class="desc">
    Axona's cognitive modeling framework applies to anyone who needs to understand, measure,
    or influence how minds process information.
  </p>

  <div class="info">
    <b style="color:#ba68c8">Healthcare &amp; Therapy</b><br>
    &bull; <b>Therapists</b> &mdash; real-time feedback on whether a session is working. Track belief
    adoption, emotional encoding strength, and cognitive state throughout treatment. EMDR protocols
    guided by actual neural consolidation signals.<br>
    &bull; <b>Psychiatrists</b> &mdash; objective measurement of cognitive states. Track the novelty/coherence
    balance in patients with schizophrenia (too much unintegrated novelty), depression (stagnation
    quadrant), or mania (chaos quadrant). Medication effects visible in real-time.<br>
    &bull; <b>Addiction treatment</b> &mdash; map the reward network, identify how deeply the addictive
    pathway dominates, measure recovery progress as alternative pathways strengthen over months.<br>
    &bull; <b>PTSD treatment</b> &mdash; measure trauma memory weight objectively. Track whether processing
    is reducing the brightness or re-traumatizing. Guide exposure therapy with precision.
  </div>

  <div class="info">
    <b style="color:#81c784">Education</b><br>
    &bull; <b>Teachers</b> &mdash; measure actual encoding, not just test performance. Know in real-time
    which students are absorbing material (strong connections forming) and which are surface-processing
    (weak, isolated nodes). Adjust pacing based on actual cognitive state, not guesswork.<br>
    &bull; <b>Curriculum designers</b> &mdash; optimize spaced repetition schedules based on measured
    forgetting curves rather than population averages. Each student gets a personalized re-injection
    schedule.<br>
    &bull; <b>Special education</b> &mdash; understand ADHD, dyslexia, and autism as network architecture
    differences rather than deficits. Design learning environments that work WITH the student's
    natural activation patterns instead of against them.<br>
    &bull; <b>Universities</b> &mdash; measure whether lectures produce deep encoding or shallow
    processing. Most education is optimized for information delivery, not information integration.
    Axona measures the difference.
  </div>

  <div class="info">
    <b style="color:#4fc3f7">Performance</b><br>
    &bull; <b>Athletes</b> &mdash; flow state detection and maintenance. Measure when an athlete enters
    the genius quadrant and what conditions keep them there. Pre-competition cognitive state
    optimization.<br>
    &bull; <b>Surgeons &amp; pilots</b> &mdash; real-time cognitive load monitoring during high-stakes
    operations. Alert when bandwidth drops below safe thresholds. Prevent errors caused by fatigue
    or overload before they happen.<br>
    &bull; <b>Military &amp; first responders</b> &mdash; cognitive readiness assessment. Measure
    decision-making capacity under stress. Training protocols that build bandwidth resilience.<br>
    &bull; <b>Esports</b> &mdash; reaction time optimization, attention allocation training,
    tilt detection (emotional state disrupting coherence). Competitive gaming is already data-driven;
    cognitive state data is the next layer.
  </div>

  <div class="info">
    <b style="color:#ffb74d">Research</b><br>
    &bull; <b>Neuroscience labs</b> &mdash; Axona as an interpretation framework for neural data.
    Raw electrode signals mapped to cognitive constructs (novelty, coherence, bandwidth, belief state)
    rather than just anatomical regions.<br>
    &bull; <b>Psychology researchers</b> &mdash; objective measurement of subjective states.
    Quantify flow, attention, emotional intensity, and creative output without relying on
    self-report questionnaires.<br>
    &bull; <b>AI researchers</b> &mdash; biological cognition as a design template. Axona's models
    of memory, novelty, and consolidation can inform artificial neural network architecture.<br>
    &bull; <b>Sleep researchers</b> &mdash; measure consolidation quality directly. Track which
    connections get reinforced vs pruned during specific sleep stages. Dream content analysis
    through activation pattern monitoring.
  </div>

  <div class="info">
    <b style="color:#f06292">Consumer &amp; Wellness</b><br>
    &bull; <b>Meditation apps</b> &mdash; measure actual cognitive state changes during meditation.
    Most apps track time spent, not quality. Axona measures bandwidth recovery, noise reduction,
    and coherence improvement in real-time.<br>
    &bull; <b>Sleep optimization</b> &mdash; not just sleep duration but consolidation quality.
    Measure whether your sleep is actually integrating the day's novelty or just cycling through
    stages without productive processing.<br>
    &bull; <b>Productivity tools</b> &mdash; flow state detection + environmental recommendations.
    "Your cognitive state suggests deep work capacity for the next 45 minutes" or "bandwidth is
    dropping, take a break before attempting complex tasks."<br>
    &bull; <b>Personal development</b> &mdash; track neuroplasticity over time. Measure whether
    new habits, skills, and patterns are actually encoding or just being performed mechanically.
  </div>

  <div class="info">
    <b style="color:var(--accent)">BCI Companies</b><br>
    &bull; <b>Neuralink, Synchron, Blackrock Neurotech</b> &mdash; Axona as an interpretation SDK.
    These companies build the hardware (electrodes, implants, signal processing). Axona provides
    the software layer that turns raw signals into meaningful cognitive state data. Without an
    interpretation layer, a BCI gives you wiggling lines. With Axona, those lines become actionable
    insights about what the brain is doing.<br>
    &bull; <b>BCI startups</b> &mdash; license Axona's cognitive models instead of building
    interpretation from scratch. Faster time to market, validated framework, growing research base.<br>
    &bull; <b>Non-invasive BCI</b> (EEG headbands, fNIRS devices) &mdash; lower resolution hardware
    that still benefits from Axona's state-space model. Even coarse signals can be mapped to the
    cognitive state quadrants.
  </div>

  <div class="info">
    <b>The business model:</b> Axona is not a hardware company. It is a <b>cognitive interpretation
    layer</b>. The revenue comes from:<br>
    &bull; <b>SDK licensing</b> to BCI hardware companies<br>
    &bull; <b>API access</b> for researchers and clinicians<br>
    &bull; <b>Consumer app</b> for wellness and productivity<br>
    &bull; <b>Enterprise</b> for performance-critical industries (surgery, aviation, military)<br>
    &bull; <b>Education partnerships</b> for adaptive learning systems<br><br>
    The same core models power all of these. The cognitive state space, belief propagation,
    bandwidth measurement, and novelty/coherence balance apply across every domain. Build once,
    apply everywhere.
  </div>
</div>
</div>

<!-- ═══ Tab: Reference (Glossary + Citations) ═════════════════════ -->
<div class="panel" id="reference-tab">
<div class="container">
  <h2>Reference</h2>
  <p class="desc">Glossary of key terms and research citations used throughout Axona.</p>

  <h3>Glossary</h3>
  <div style="display:grid;grid-template-columns:140px 1fr;gap:2px 16px;font-size:11px;
       background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:14px 18px;margin-bottom:16px">
    <b style="color:var(--accent)">Activation</b><span style="color:var(--dim)">The firing of a node or cluster in the network; how information becomes "active" and available for processing</span>
    <b style="color:var(--accent)">Bandwidth</b><span style="color:var(--dim)">Spare cognitive processing capacity available for creative or complex work; reduced by stressors</span>
    <b style="color:var(--accent)">BDNF</b><span style="color:var(--dim)">Brain-derived neurotrophic factor; a protein that promotes synapse formation and strengthening</span>
    <b style="color:var(--accent)">BCI</b><span style="color:var(--dim)">Brain-computer interface; hardware that reads or writes neural signals (e.g. Neuralink)</span>
    <b style="color:var(--accent)">Belief state</b><span style="color:var(--dim)">A high-weight predictive state that changes processing across the system, including physiology</span>
    <b style="color:var(--accent)">Brightness</b><span style="color:var(--dim)">The encoding strength of a memory; higher brightness = easier retrieval; driven by emotional intensity</span>
    <b style="color:var(--accent)">Cluster</b><span style="color:var(--dim)">A group of densely connected nodes representing related concepts (e.g. "food" cluster, "fear" cluster)</span>
    <b style="color:var(--accent)">Coherence</b><span style="color:var(--dim)">How well ideas hold together; the ability to integrate new connections into stable structure</span>
    <b style="color:var(--accent)">Conformity</b><span style="color:var(--dim)">The tendency to align internal state with group signals; an evolved efficiency pattern, not stupidity</span>
    <b style="color:var(--accent)">Consolidation</b><span style="color:var(--dim)">The process (primarily during sleep) of testing, pruning, and reinforcing new connections</span>
    <b style="color:var(--accent)">Cross-activation</b><span style="color:var(--dim)">When two normally separate clusters are forced to connect; the mechanism behind analogy and insight</span>
    <b style="color:var(--accent)">Edge</b><span style="color:var(--dim)">A connection between two nodes; has a weight that determines signal strength</span>
    <b style="color:var(--accent)">Emopics</b><span style="color:var(--dim)">Emotion + topic; the combined contextual state that determines which part of the network is active</span>
    <b style="color:var(--accent)">Encoding</b><span style="color:var(--dim)">The process of forming new connections when information enters the network</span>
    <b style="color:var(--accent)">Flashbulb memory</b><span style="color:var(--dim)">A vivid but often inaccurate memory formed during high emotional intensity</span>
    <b style="color:var(--accent)">GLP-1</b><span style="color:var(--dim)">Glucagon-like peptide-1; a hormone that modulates reward/satiety networks (Ozempic, Wegovy)</span>
    <b style="color:var(--accent)">KL divergence</b><span style="color:var(--dim)">Kullback-Leibler divergence; measures how much new information shifts your belief distribution</span>
    <b style="color:var(--accent)">Node</b><span style="color:var(--dim)">A single concept, memory, or unit in the network</span>
    <b style="color:var(--accent)">Novelty</b><span style="color:var(--dim)">The rate of new connection formation; high novelty = many new ideas forming</span>
    <b style="color:var(--accent)">Peptide</b><span style="color:var(--dim)">A short amino acid chain that acts as a targeted signaling molecule in the brain</span>
    <b style="color:var(--accent)">Phi (&#934;)</b><span style="color:var(--dim)">The measure of integrated information in IIT; higher &#934; = more consciousness</span>
    <b style="color:var(--accent)">Plasticity</b><span style="color:var(--dim)">The network's ability to rewire itself; form new connections, strengthen or weaken existing ones</span>
    <b style="color:var(--accent)">Prediction error</b><span style="color:var(--dim)">The gap between what was expected and what actually happened; high error = high novelty</span>
    <b style="color:var(--accent)">Pruning</b><span style="color:var(--dim)">Removing weak or unused connections; peaks during adolescence; ongoing during sleep</span>
    <b style="color:var(--accent)">Spreading activation</b><span style="color:var(--dim)">How signal propagates through connected nodes; activation at one node triggers its neighbors</span>
    <b style="color:var(--accent)">State space</b><span style="color:var(--dim)">The 2D map of novelty (vertical) vs coherence (horizontal) with four quadrants</span>
    <b style="color:var(--accent)">Structural pressure</b><span style="color:var(--dim)">When many nodes point toward a gap where no node exists; the precondition for novelty</span>
    <b style="color:var(--accent)">Weight</b><span style="color:var(--dim)">The strength of a connection between two nodes; stronger weight = stronger signal propagation</span>
  </div>

  <h3>Key Research &amp; Citations</h3>
  <div class="info">
    <b>Memory &amp; Encoding</b><br>
    &bull; Talarico, J.M. &amp; Rubin, D.C. (2003). "Confidence, not consistency, characterizes flashbulb memories." <em>Psychological Science</em>. &mdash; Flashbulb memories are vivid but often inaccurate.<br>
    &bull; Nader, K. (2003). "Memory traces unbound." <em>Trends in Neuroscience</em>. &mdash; Memories are reconstructed on every recall, not played back.<br>
    &bull; Ramirez, S. et al. (2013). "Creating a false memory in the hippocampus." <em>Science</em>. &mdash; Tonegawa lab: false memories created in mice via optogenetics.
  </div>

  <div class="info">
    <b>Novelty &amp; Creativity</b><br>
    &bull; Csikszentmihalyi, M. (1990). <em>Flow: The Psychology of Optimal Experience</em>. &mdash; The conditions for flow state.<br>
    &bull; Burt, R. (2004). "Structural holes and good ideas." <em>American Journal of Sociology</em>. &mdash; Bridges between clusters produce the most valuable ideas.<br>
    &bull; Beaty, R.E. et al. (2018). "Robust prediction of individual creative ability from brain functional connectivity." <em>PNAS</em>. &mdash; Creativity correlates with cross-network connectivity.
  </div>

  <div class="info">
    <b>Belief &amp; Placebo</b><br>
    &bull; Wager, T.D. et al. (2004). "Placebo-induced changes in fMRI in the anticipation and experience of pain." <em>Science</em>. &mdash; Placebo produces measurable brain changes.<br>
    &bull; Kaptchuk, T.J. et al. (2010). "Placebos without deception." <em>PLoS ONE</em>. &mdash; Open-label placebos still work even when patients know they are placebos.<br>
    &bull; Rosenthal, R. &amp; Jacobson, L. (1968). <em>Pygmalion in the Classroom</em>. &mdash; Teacher expectations change student performance.
  </div>

  <div class="info">
    <b>Consciousness</b><br>
    &bull; Chalmers, D. (1995). "Facing up to the problem of consciousness." <em>Journal of Consciousness Studies</em>. &mdash; The hard problem defined.<br>
    &bull; Tononi, G. (2004). "An information integration theory of consciousness." <em>BMC Neuroscience</em>. &mdash; Integrated Information Theory (IIT).<br>
    &bull; Baars, B. (1988). <em>A Cognitive Theory of Consciousness</em>. &mdash; Global Workspace Theory.<br>
    &bull; Friston, K. (2010). "The free-energy principle: a unified brain theory?" <em>Nature Reviews Neuroscience</em>. &mdash; Predictive processing framework.
  </div>

  <div class="info">
    <b>Pharmacology</b><br>
    &bull; Carhart-Harris, R.L. et al. (2016). "Neural correlates of the LSD experience." <em>PNAS</em>. &mdash; Psychedelics increase cross-network connectivity.<br>
    &bull; Davis, A.K. et al. (2021). "Effects of psilocybin-assisted therapy on major depressive disorder." <em>JAMA Psychiatry</em>. &mdash; Johns Hopkins psilocybin depression trial.<br>
    &bull; Muller, T.D. et al. (2022). "GLP-1 receptor agonists in obesity." <em>Nature Reviews Drug Discovery</em>. &mdash; GLP-1 mechanism and broader reward effects.<br>
    &bull; Volkow, N.D. et al. (2009). "Imaging dopamine's role in drug abuse and addiction." <em>Neuropharmacology</em>. &mdash; Dopamine prediction errors in addiction.
  </div>

  <div class="info">
    <b>Sleep &amp; Dreams</b><br>
    &bull; Walker, M. (2017). <em>Why We Sleep</em>. &mdash; Comprehensive overview of sleep's role in consolidation.<br>
    &bull; Horowitz, A.H. et al. (2020). "Targeted dream incubation at sleep onset." <em>Consciousness and Cognition</em>. &mdash; MIT Media Lab dream incubation.<br>
    &bull; Tononi, G. &amp; Cirelli, C. (2014). "Sleep and the price of plasticity." <em>Neuron</em>. &mdash; Synaptic homeostasis hypothesis: sleep prunes weak connections.
  </div>

  <div class="info">
    <b>Neural Interfaces</b><br>
    &bull; Musk, E. &amp; Neuralink (2019). "An integrated brain-machine interface platform." <em>bioRxiv</em>. &mdash; Neuralink architecture.<br>
    &bull; Ezzyat, Y. et al. (2018). "Closed-loop stimulation of temporal cortex rescues functional networks and improves memory." <em>Nature Communications</em>. &mdash; DARPA RAM program results.<br>
    &bull; Suthana, N. &amp; Fried, I. (2014). "Deep brain stimulation for enhancement of learning and memory." <em>NeuroImage</em>. &mdash; Memory enhancement via stimulation.
  </div>

  <div class="info">
    <b>Development &amp; Conditions</b><br>
    &bull; Huttenlocher, P.R. (1979). "Synaptic density in human frontal cortex." <em>Brain Research</em>. &mdash; Synaptic pruning during development.<br>
    &bull; Casey, B.J. et al. (2008). "The adolescent brain." <em>Annals of the NY Academy of Sciences</em>. &mdash; Adolescent risk-taking as architecture, not immaturity.<br>
    &bull; van der Kolk, B. (2014). <em>The Body Keeps the Score</em>. &mdash; Trauma as a network-level phenomenon.<br>
    &bull; Shapiro, F. (2001). <em>Eye Movement Desensitization and Reprocessing</em>. &mdash; EMDR for trauma processing.
  </div>
</div>
</div>

<!-- ═══ Tab: Case Studies ═════════════════════════════════════════ -->
<div class="panel" id="cases-tab">
<div class="container">
  <h2>Case Studies &mdash; Famous Neurology, Abstract Mechanisms Made Real</h2>
  <p class="desc">
    Axona's mechanisms stay abstract until you see them isolated in a real case. Each
    of the people below had a specific part of the network damaged, spared, or
    unusually wired &mdash; and the resulting pattern makes a particular mechanism
    undeniable. These are not curiosities. They are the reason we know the framework
    is right.
  </p>

  <div class="info">
    <b>Henry Molaison (H.M.) &mdash; the patient who could not form new memories</b><br><br>
    In 1953, to treat intractable seizures, a surgeon removed most of H.M.'s medial
    temporal lobe, including his hippocampi. The seizures stopped. So did his ability
    to form new declarative memories. For the next 55 years, until his death in 2008,
    H.M. could hold a conversation, read a newspaper, and remember nothing of it
    minutes later. He could not learn a new name, recognize a new face, or recall
    what he had eaten for breakfast.<br><br>
    <b>But he could still learn motor skills.</b> Asked to trace a star in a mirror
    every day for weeks, his tracing got measurably better over time &mdash; even
    though each day he denied ever having done the task before. The declarative
    memory was gone. The procedural memory was untouched. H.M. is the reason we know
    these are separate systems.<br><br>
    <b>What he proves:</b> Memory is not unitary. Damage the hippocampus and you
    lose episodic encoding while the motor system keeps learning perfectly. (Tied
    to the Procedural Memory canvas.)
  </div>

  <div class="info">
    <b>Phineas Gage &mdash; the man whose personality was in his frontal lobe</b><br><br>
    In 1848, a railroad worker named Phineas Gage had a three-foot iron rod driven
    through his left cheek, through the front of his brain, and out the top of his
    skull. He survived. He walked to the doctor. The physical recovery was
    remarkable. But the man his friends knew was gone. Before the injury, Gage was
    described as responsible, well-liked, a capable foreman. After, he was impulsive,
    profane, unable to hold a job, "no longer Gage." His intelligence, language,
    perception, and memory were largely intact. What the rod had destroyed was his
    ventromedial prefrontal cortex &mdash; the region that integrates emotion into
    decision-making and inhibits impulsive responses.<br><br>
    <b>What he proves:</b> Personality and moral behavior are not a separate
    "character" on top of the brain. They are a network function, localized enough
    that a single injury can remove them while leaving everything else intact. The
    person you experience yourself as is an output of specific tissue.
  </div>

  <div class="info">
    <b>Clive Wearing &mdash; living in a seven-second present</b><br><br>
    In 1985, Clive Wearing, a British musicologist, contracted a herpes simplex
    encephalitis that destroyed his hippocampi and damaged parts of his frontal
    cortex. His episodic memory was reduced to about 7 to 30 seconds. Every few
    moments, he believes he has just regained consciousness for the first time. His
    diaries are filled with entries like "8:31 AM &mdash; Now I am really, completely
    awake" crossed out, followed by "8:32 AM &mdash; NOW I am really awake" crossed
    out, and so on through the day.<br><br>
    <b>But he can still conduct choirs, play complex piano pieces from memory, and
    recognize his wife.</b> His procedural memory for music is intact. His
    recognition of her as deeply familiar survives &mdash; he greets her with
    overwhelming joy every time she enters a room, even if she has just left it.
    The emotional/procedural/recognition systems run on different hardware from the
    episodic system that was destroyed.<br><br>
    <b>What he proves:</b> Episodic memory, procedural memory, and emotional memory
    are separable. The person you are to the people who love you is not only the
    person who remembers your shared past &mdash; there is a version of you that
    persists even when that record is wiped.
  </div>

  <div class="info">
    <b>SM &mdash; the woman without fear</b><br><br>
    "SM" (a pseudonym) has bilateral lesions of her amygdala caused by a rare genetic
    condition (Urbach-Wiethe disease). She is normal in nearly every way &mdash;
    intelligent, warm, verbal, socially engaged. But she cannot experience fear. In
    formal tests she cannot identify the fear expression on faces (she calls it
    "surprised"). She handles live snakes with curiosity. She has walked through
    dangerous neighborhoods at night without concern. She has been mugged and
    assaulted multiple times, in situations a fear-capable brain would have avoided,
    and still cannot generate the appropriate anticipatory fear response the next
    time. She has reported feeling "all other emotions" but never fear.<br><br>
    <b>What she proves:</b> Emotions are not a general "feeling" circuit. Each has
    its own substrate, and removing the substrate removes the emotion while leaving
    everything else intact. Fear is a specific amygdala-centered network operation,
    not a generic output of "the emotional brain." The categorical architecture is
    real.
  </div>

  <div class="info">
    <b>The split-brain patients &mdash; two minds in one skull</b><br><br>
    In the 1960s, Joseph Bogen and others performed corpus callosotomies on patients
    with intractable epilepsy &mdash; cutting the main fiber bundle connecting the
    left and right hemispheres. The seizures were contained. What Michael Gazzaniga
    discovered afterward changed how we think about the self entirely.<br><br>
    Flash a word to the right hemisphere only (by showing it in the left visual
    field) and the patient's left hand (controlled by the right hemisphere) can pick
    up the corresponding object &mdash; but the patient, speaking from the left
    hemisphere, cannot say what the word was. Ask them <em>why</em> they just grabbed
    that object, and the left hemisphere confabulates a reason on the spot,
    believing it. This is the Interpreter module (see the Interpreter canvas), caught
    in the act.<br><br>
    <b>What they prove:</b> The unified "I" that each of us experiences is itself a
    network construction. Under the right conditions, two separate streams of
    processing can run in one head, and the narrating channel will invent
    explanations for the actions of the non-narrating channel without any awareness
    that the explanation is invention. Everything we "know about ourselves" is
    vulnerable to the same process, just without the surgery.
  </div>

  <div class="info">
    <b>Derek Paravicini &mdash; a mind with one channel turned all the way up</b><br><br>
    Born premature in 1979, Derek Paravicini is severely visually impaired,
    autistic, and has significant learning disabilities. He cannot count reliably or
    tie his own shoes. But he can hear a piece of music once and play it back on the
    piano in any key, with perfect reproduction of harmony and inflection. His
    teacher Adam Ockelford has documented that Derek has absolute pitch, an
    essentially unlimited memory for musical material, and the ability to improvise
    in any style after minimal exposure.<br><br>
    <b>What he proves:</b> The brain is not a general-purpose machine with a uniform
    capacity. Different substrates can run at wildly different levels of ability in
    the same individual. The parameter that controls musical encoding in Derek is
    turned extraordinarily high. Other parameters are low or missing. "Intelligence"
    is a spectacularly misleading single number for what is actually a high-
    dimensional profile of many separately-calibrated systems.
  </div>
</div>
</div>

<!-- ═══ Tab: Composer (Scenario Player + Master Controls) ═════════ -->
<div class="panel" id="composer-tab">
<div class="container">
  <h2>Composer &mdash; Stories and Master Controls</h2>
  <p class="desc">
    Most canvases in Axona demonstrate one mechanism in isolation. Real cognition is
    many mechanisms running together. This tab lets you compose them &mdash; run a
    scripted scenario across multiple canvases in sequence, or sweep master parameters
    that touch several canvases at once.
  </p>

  <h3>Scenario Player</h3>
  <p class="desc">
    Pre-scripted sequences that fire actions across several canvases in a specific
    order, telling a story about a mind under load. Pick a scenario and watch the
    canvases respond one after the other. Open the canvases in the appropriate tabs
    to see them update live as the scenario plays.
  </p>
  <div class="controls" style="flex-wrap:wrap;gap:8px">
    <button onclick="scenPlay('tired-student')">Tired Student at an Exam</button>
    <button onclick="scenPlay('new-grief')">First Week of Grief</button>
    <button onclick="scenPlay('therapy')">Therapy Session (Trauma → Reframe)</button>
    <button onclick="scenPlay('creative-flow')">Entering Creative Flow</button>
    <button onclick="scenPlay('doomscroll')">Doomscroll Spiral</button>
    <button onclick="scenStop()">Stop</button>
  </div>
  <div class="canvas-box" style="padding:14px;margin-top:10px">
    <div id="scen-step" style="font-family:monospace;font-size:11px;color:var(--dim);min-height:20px">
      (no scenario running)
    </div>
    <div id="scen-log" style="font-family:monospace;font-size:11px;line-height:1.7;max-height:180px;overflow-y:auto;margin-top:10px;color:var(--text)"></div>
  </div>

  <h3 style="margin-top:24px">Master Parameter Sweep</h3>
  <p class="desc">
    A handful of parameters cross-cut every cognitive state in Axona: bandwidth, prior
    precision, novelty intake, reward depth, feedback gain. Adjusting them here
    programmatically moves the individual sliders on the relevant canvases so you can
    watch multiple demos respond to one change.
  </p>
  <div class="controls" style="display:block;padding-top:14px">
    <div style="display:grid;grid-template-columns:170px 1fr 60px;gap:10px 20px;align-items:center;font-size:11px">
      <span>bandwidth</span>
      <input type="range" id="master-bw" min="0" max="100" value="80" oninput="masterApply()">
      <span class="stat-val" id="master-bw-val">80</span>

      <span>prior precision</span>
      <input type="range" id="master-prec" min="10" max="99" value="60" oninput="masterApply()">
      <span class="stat-val" id="master-prec-val">60</span>

      <span>novelty intake</span>
      <input type="range" id="master-nov" min="1" max="100" value="50" oninput="masterApply()">
      <span class="stat-val" id="master-nov-val">50</span>

      <span>reward depth</span>
      <input type="range" id="master-rew" min="0" max="100" value="70" oninput="masterApply()">
      <span class="stat-val" id="master-rew-val">70</span>

      <span>feedback gain (flow)</span>
      <input type="range" id="master-fb" min="0" max="100" value="70" oninput="masterApply()">
      <span class="stat-val" id="master-fb-val">70</span>
    </div>
  </div>
  <div class="info">
    <b>What each master does:</b><br>
    &bull; <b>bandwidth</b> → drives Attention Spotlight breadth, Flow State feedback,
    Theory of Mind accuracy, and the stressor cost in the Cognitive Bandwidth demo.
    Low bandwidth = narrow spotlight, shrunken theory of mind, brittle flow.<br>
    &bull; <b>prior precision</b> → drives Prediction vs Reality prior-stiffness,
    Hallucination prior-stiffness, and the Autism precision slider. High precision =
    intolerant network, more residuals, more sensory load.<br>
    &bull; <b>novelty intake</b> → drives the Curiosity/Boredom environment slider and
    the Time Perception novelty slider. Low = boredom and subjective time collapse;
    high + safe = curiosity and subjective time expansion.<br>
    &bull; <b>reward depth</b> → inverted into the Depression severity slider
    (100 = healthy landscape, 0 = flat landscape) and feeds the Flow State skill
    parameter indirectly.<br>
    &bull; <b>feedback gain</b> → drives the Flow State feedback slider directly.<br><br>
    <b>Compose a state:</b> Drop bandwidth, lower reward depth, raise prior precision
    and you have assembled "depressed + overwhelmed + stressed." Raise everything and
    you have composed a genius-zone state. The canvases are not just pictures &mdash;
    they respond to the same parameters, and those parameters compose.
  </div>
</div>
</div>

<!-- ═══ Tab: Sandbox ══════════════════════════════════════════════ -->
<div class="panel" id="sandbox-tab">
<div class="container">
  <h2>Sandbox &mdash; Build Your Own Micro-Brain</h2>
  <p class="desc">
    Every other canvas in Axona shows a specific mechanism running on a pre-built
    network. This one lets you build the network yourself. Click to drop nodes,
    click two nodes to draw an edge between them, click a node again to inject
    activation, and watch spreading activation play out.
  </p>
  <div class="canvas-box">
    <canvas id="sbox-canvas" width="960" height="420"></canvas>
  </div>
  <div class="controls">
    <button onclick="sboxMode('node')">Add Node</button>
    <button onclick="sboxMode('edge')">Draw Edge</button>
    <button onclick="sboxMode('fire')">Inject Activation</button>
    <button onclick="sboxMode('erase')">Erase</button>
    <button onclick="sboxClear()">Clear All</button>
    <label style="display:flex;align-items:center;gap:8px;margin-left:10px">
      <span>decay:</span>
      <input type="range" id="sbox-decay" min="90" max="99" value="95" style="width:90px">
      <span class="stat-val" id="sbox-decay-val">0.95</span>
    </label>
    <label style="display:flex;align-items:center;gap:8px">
      <span>spread:</span>
      <input type="range" id="sbox-spread" min="1" max="40" value="15" style="width:90px">
      <span class="stat-val" id="sbox-spread-val">0.15</span>
    </label>
    <span style="margin-left:auto;color:var(--dim)">
      mode: <b id="sbox-mode-label" style="color:var(--accent)">add node</b>
      &nbsp; nodes: <b id="sbox-nodes">0</b>
      &nbsp; edges: <b id="sbox-edges">0</b>
    </span>
  </div>
  <div class="info">
    <b>How to use it:</b><br>
    1. <b>Add Node</b>: click anywhere on the canvas to drop a node.<br>
    2. <b>Draw Edge</b>: click a node, then click another node to connect them.
    Connected nodes share activation.<br>
    3. <b>Inject Activation</b>: click any node to fire it. Activation spreads to
    neighbors and decays over time.<br>
    4. <b>Erase</b>: click a node or edge to remove it.<br>
    5. <b>Decay</b> and <b>spread</b> sliders control how fast activation fades and
    how strongly it propagates.<br><br>
    <b>What you can build:</b> A trauma loop (5 nodes in a ring with high
    reinforcement), a memory cluster (a hub with many weak spokes), an echo chamber
    (two tightly-connected clusters with sparse bridges), a prediction chain
    (nodes in a line), or anything else. The same handful of rules produce every
    cognitive phenomenon in the app.
  </div>
</div>
</div>

<!-- ═══ Tab: Vectora-Powered Live Retrieval ═════════════════════ -->
<div class="panel" id="vec-live-tab">
<div class="container">
  <h2>Live Vectora Retrieval
    <span style="font-size:10px;color:#a3e635;margin-left:10px;letter-spacing:0.1em">● POWERED BY VECTORA</span>
  </h2>
  <p class="desc">
    This canvas calls the real Vectora engine (<code>pep.vectora</code>)
    via HTTP. A graph of 20 memory nodes is seeded on the server; picking
    a memory runs spreading activation through its semantic neighborhood.
    Same engine as <a href="/vectora/playground">/vectora/playground</a>
    and the <a href="/vectora/retrieval">Vectora Retrieval product</a>.
  </p>
  <div class="canvas-box" style="padding:20px">
    <div style="display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin-bottom:14px">
      <label style="font-size:11px;color:var(--dim);display:flex;gap:6px;align-items:center;flex:1;min-width:240px">
        <span>seed memory:</span>
        <select id="vec-axona-seed" style="flex:1;background:var(--surface);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:6px;font-family:inherit;font-size:11px">
          <option value="">loading…</option>
        </select>
      </label>
      <label style="font-size:11px;color:var(--dim);display:flex;gap:6px;align-items:center">
        <span>k:</span>
        <input type="range" id="vec-axona-k" min="3" max="10" value="6" style="width:80px">
        <span id="vec-axona-k-v" style="color:var(--accent);font-weight:bold;min-width:14px">6</span>
      </label>
      <label style="font-size:11px;color:var(--dim);display:flex;gap:6px;align-items:center">
        <span>decay:</span>
        <input type="range" id="vec-axona-decay" min="10" max="80" value="35" style="width:80px">
        <span id="vec-axona-decay-v" style="color:var(--accent);font-weight:bold;min-width:30px">0.35</span>
      </label>
      <button onclick="vecAxonaQuery()" style="padding:6px 14px;border-radius:4px;border:1px solid var(--accent);background:var(--accent);color:var(--bg);font-size:11px;cursor:pointer;font-family:inherit;font-weight:bold">Query Vectora</button>
    </div>
    <div id="vec-axona-results" style="min-height:180px">
      <div style="color:var(--dim);text-align:center;padding:40px 20px;font-size:11px">pick a memory and click Query</div>
    </div>
    <div id="vec-axona-stats" style="margin-top:10px;font-size:10px;color:var(--dim);text-align:right"></div>
  </div>
  <div class="info">
    <b>Dogfood play.</b> Axona's memory-retrieval mechanism is the same
    spreading-activation primitive Vectora ships as retrieval. Rather
    than re-implementing per-app, Axona's memory lookup delegates to
    Vectora. Every LAVAS app that needs spreading-activation retrieval
    does the same &mdash; one engine, many products.
  </div>
</div>
</div>

<!-- ═══ Tab: Memory Haze (opacity decay + reuse) ═════════════════ -->
<div class="panel" id="haze-tab">
<div class="container">
  <h2>Memory Haze &mdash; Opacity Decay and Reuse
    <span style="font-size:10px;color:#a3e635;margin-left:10px;letter-spacing:0.1em">● PEP PRIMITIVE</span>
  </h2>
  <p class="desc">
    Every node in the graph has an <b>opacity</b> &mdash; its current
    encoding strength &mdash; that decays over time toward a floor. When
    opacity drops below a reuse threshold, the node becomes available for
    overwriting by new encoding. This is why vivid memories are bright
    and old memories are hazy: it is the same capacity, partially
    reclaimed. Forgetting and learning are the same mechanism.
  </p>

  <div class="canvas-box">
    <canvas id="haze-canvas" width="960" height="460"></canvas>
  </div>
  <div class="controls" style="flex-wrap:wrap;gap:10px">
    <label style="font-size:11px;color:var(--dim);display:flex;gap:6px;align-items:center">
      <span>time elapsed:</span>
      <input type="range" id="haze-time" min="0" max="100" value="0" style="width:200px">
      <span id="haze-time-v" style="color:var(--accent);font-weight:bold;min-width:54px">0 days</span>
    </label>
    <label style="font-size:11px;color:var(--dim);display:flex;gap:6px;align-items:center">
      <span>half-life:</span>
      <input type="range" id="haze-halflife" min="1" max="60" value="14" style="width:140px">
      <span id="haze-halflife-v" style="color:var(--accent);font-weight:bold;min-width:48px">14 days</span>
    </label>
    <button onclick="hazeReinforce()" style="padding:4px 12px;border-radius:4px;border:1px solid var(--accent);background:var(--accent);color:var(--bg);font-size:11px;cursor:pointer;font-family:inherit;font-weight:bold">Reinforce random</button>
    <button onclick="hazeOld()" style="padding:4px 12px;border-radius:4px;border:1px solid var(--accent2);background:transparent;color:var(--accent2);font-size:11px;cursor:pointer;font-family:inherit">Simulate 70-year-old</button>
    <button onclick="hazeReset()" style="padding:4px 12px;border-radius:4px;border:1px solid var(--border);background:transparent;color:var(--text);font-size:11px;cursor:pointer;font-family:inherit">Reset</button>
  </div>

  <div class="info">
    <b>What you are watching:</b> 24 memory nodes, each with an
    individual opacity and its own encoded-at timestamp. Brightness on
    screen = effective opacity. As &quot;time elapsed&quot; advances,
    older memories fade toward the floor. Click <b>Reinforce random</b>
    to re-encode a node &mdash; its opacity jumps back up and its
    encoded-at resets (the successful-recall effect). Nodes that drop
    below 0.15 are marked for reuse (dashed outline); in a real system,
    those are the slots that new incoming memories overwrite.<br><br>
    <b>The unification claim:</b> forgetting is not a bug. It is the
    mechanism that makes capacity finite and therefore usable. A system
    that could not forget would eventually drown in stale encodings.
    Haze is how a finite-capacity predictor handles a stream of
    novel input.
  </div>

  <div class="info" style="border-left: 3px solid var(--accent2)">
    <b style="color:var(--accent2)">The reminiscence bump &mdash; why old people have vivid memories of their youth</b><br><br>
    Click <b>Simulate 70-year-old</b> above. You will see a counter-
    intuitive pattern: the oldest memories (from roughly ages 15-25)
    are the brightest ones on the board. Memories from ages 40-60 are
    dimmer. The decades from 25 to 45 almost vanish. This is the
    <em>reminiscence bump</em>, a well-documented empirical finding
    (Rubin &amp; Schulkind 1997, Conway 2005), and it falls out of the
    haze primitive without needing a special case:<br><br>
    &bull; <b>High opacity at encoding.</b> Ages 15-25 are when
    identity crystallizes and first-times cluster &mdash; first love,
    first job, first independence, first loss. First-times are
    inherently high-novelty, and high novelty in PEP's predictor
    produces high residuals, which means strong initial encoding
    (high <code>opacity</code>).<br>
    &bull; <b>Repeated reinforcement.</b> These are the memories you
    tell and re-tell across your lifetime &mdash; in conversation, on
    anniversaries, through photos, in therapy, as origin stories.
    Every retelling fires <code>reinforce()</code>, resetting
    <code>encoded_at</code> to now. A memory reinforced once a year
    for fifty years has its effective decay clock reset fifty times.
    Its effective opacity stays bright despite the calendar.<br>
    &bull; <b>Identity nodes are hubs.</b> Youth memories get wired
    into the identity subgraph (&quot;this is who I am&quot;). Hub
    nodes are touched by every related retrieval, so they get
    constant indirect reinforcement. Every time you think about who
    you are, the graph walks through those nodes.<br>
    &bull; <b>Cognitive sharpness at encoding.</b> Working-memory
    capacity and processing speed peak in the 20s. Memories encoded
    then start with a higher baseline opacity than memories encoded
    under age-related bandwidth decline.<br>
    &bull; <b>Graph competition was lower.</b> A young person&apos;s
    semantic graph is smaller. Memories encoded into a sparse region
    have fewer competing neighbors, so their activation is not
    diluted the way later memories are. The graph&apos;s center of
    mass is literally where the person was when they were young.<br><br>
    The middle decades fade because those memories were encoded with
    lower novelty (you had seen life before), rehearsed less (they
    are not identity-defining), and land in a dense, competitive
    graph region. Recent memories (last 1-2 years) stay bright for a
    different reason: not enough time has passed for the exponential
    decay to bite. So the lifespan curve has two peaks &mdash; a tall
    one at youth and a shorter one at &quot;recent,&quot; with a
    valley in the middle. That is the reminiscence bump.
  </div>

  <div class="info">
    <b>See also:</b>
    <a href="#" onclick="document.querySelector('[data-panel=vec-live-tab]').click();return false">Vectora Live</a>
    (opacity attenuates activation in real time),
    <a href="#motor-errors">Motor Prediction Errors</a>
    (spatial model haze causes stubs and trips),
    <a href="#" onclick="document.querySelector('[data-panel=media-tab]').click();return false">Media &amp; Brain</a>
    (no consolidation gap = no reinforcement = fast haze),
    <a href="#bio-substrate">Biological Substrate</a>
    (microglia are the pruning crew that implements haze),
    <a href="#arousal-clarity">Arousal &amp; Clarity</a>
    (drive states modulate the same opacity landscape),
    <a href="/pep">PEP &rarr; State Modulator</a>.
  </div>
</div>
</div>

<!-- ══��� Tab: Media & Brain ═══════════════════════════════════════ -->
<div class="panel" id="media-tab">
<div class="container">
  <h2>Media &amp; The Brain &mdash; How Each Medium Retrains Your Prediction Engine</h2>
  <p class="desc">
    Media doesn't just fill time &mdash; it trains your prediction
    engine's timescale. A brain trained on short-form content literally
    cannot sustain attention for a book, not because of willpower failure
    but because the predictor and bandwidth allocator have been
    retrained for a different input regime.
  </p>
  <div class="canvas-box">
    <canvas id="media-canvas" width="960" height="560"></canvas>
  </div>
  <div class="controls" style="flex-wrap:wrap;gap:10px">
    <div style="font-size:11px;color:var(--dim);margin-right:10px">Train on:</div>
    <button onclick="mediaTrain('books')" id="media-books" class="media-btn media-active">Books</button>
    <button onclick="mediaTrain('tv')" id="media-tv" class="media-btn">TV Shows</button>
    <button onclick="mediaTrain('movies')" id="media-movies" class="media-btn">Movies</button>
    <button onclick="mediaTrain('social')" id="media-social" class="media-btn">Social Media</button>
    <button onclick="mediaTrain('short')" id="media-short" class="media-btn">Short-Form (TikTok)</button>
    <label style="font-size:11px;color:var(--dim);display:flex;gap:6px;align-items:center;margin-left:auto">
      <span>months trained:</span>
      <input type="range" id="media-months" min="1" max="24" value="6" style="width:120px" oninput="document.getElementById('media-months-v').textContent=this.value">
      <span id="media-months-v" style="color:var(--accent);font-weight:bold;min-width:18px">6</span>
    </label>
  </div>

  <div class="info" style="border-left: 3px solid var(--accent)">
    <b style="color:var(--accent)">Five media types, five cognitive adaptations</b><br><br>
    &bull; <b>Books</b> &mdash; prediction window spans hours. The predictor
    holds character arcs, thematic threads, nested arguments. Deep
    consolidation between sessions (you process the book overnight).
    Nodes get reinforced through slow retrieval. Builds the deepest
    semantic networks because spreading activation has time to reach
    second and third hops.<br><br>
    &bull; <b>TV shows</b> &mdash; prediction window ~45 minutes with
    engineered breaks. Cliffhangers are unresolved predictions; the
    residual stays open between episodes. The between-episode gap IS
    the consolidation window. Binge-watching collapses it: middle
    episodes go hazy because there was no consolidation gap and the
    opacity was never reinforced.<br><br>
    &bull; <b>Movies</b> &mdash; single 2-hour sustained-attention
    session. Three-act structure maps onto prediction/residual: setup
    builds the predictor's model, complication violates it (residual
    spike), resolution restores it. A great movie leaves an emotional
    residual &mdash; the prediction was restored but the path through
    the violation changed your model.<br><br>
    &bull; <b>Social media</b> &mdash; variable-ratio reinforcement on
    a scroll feed. Fragmentary 3-10 second attention per item. The
    predictor trains on a very short window. Spreading activation never
    reaches the second hop because the topic changes. No consolidation
    gaps; everything stays surface.<br><br>
    &bull; <b>Short-form content</b> (TikTok/Reels/Shorts) &mdash; the
    extreme. 15-60 seconds per item, algorithmically optimized for
    residual spikes. Trains three specific adaptations: (1) prediction
    window collapses to seconds, (2) residual threshold rises so books
    feel boring, (3) bandwidth allocation shrinks because sustained
    attention is never rewarded.
  </div>

  <div class="info" style="border-left: 3px solid #f06292">
    <b style="color:#f06292">Why the brain craves short-form content</b><br><br>
    The craving is not a willpower failure. It is the reward-prediction-
    error loop doing exactly what it evolved to do:<br><br>
    &bull; <b>Variable-ratio reinforcement.</b> You do not know which
    scroll will be funny, shocking, or interesting. That unpredictability
    is the slot-machine schedule &mdash; the most potent driver of
    compulsive behavior in behavioral psychology. Each scroll is a pull
    of the lever.<br><br>
    &bull; <b>Residual spikes ARE the reward.</b> When the prediction
    engine is surprised (a novel TikTok violates what you expected), the
    residual spike fires a dopamine hit. Short-form content is
    algorithmically engineered to maximize residual spikes per minute.
    More spikes = more dopamine = stronger craving to keep scrolling.<br><br>
    &bull; <b>Tolerance builds.</b> As the residual threshold rises from
    exposure, the brain needs MORE novelty to produce the same hit. This
    is literal neurological tolerance &mdash; the same mechanism as
    substance tolerance. You crave more of what raised the threshold
    because you now need it to feel baseline engagement.<br><br>
    &bull; <b>Withdrawal is boredom.</b> When the short-form input stops
    (you put the phone down), the threshold is still elevated but the
    environment does not meet it. The gap between the elevated threshold
    and the non-stimulating world is experienced as restlessness,
    agitation, the urge to pick the phone back up. That is withdrawal.
    Not dramatic, not painful &mdash; just a constant low-grade pull.<br><br>
    <b>Books do not create this craving</b> because the reward is
    delayed and predictable. The satisfaction comes from resolution of a
    long prediction arc, not from moment-to-moment surprise. The
    dopamine profile is lower-amplitude, longer-duration. That is less
    addictive but more sustaining.
  </div>

  <div class="info" style="border-left: 3px solid #ffb74d">
    <b style="color:#ffb74d">Beyond media &mdash; how training bleeds into the rest of life</b><br><br>
    The prediction engine does not have a &quot;media mode&quot; and a
    &quot;life mode.&quot; The timescale it trains on is the timescale
    it uses for everything:<br><br>
    <b style="color:#a78bfa">A book-trained brain:</b><br>
    &bull; Can hold a long meeting without checking a phone<br>
    &bull; Follows a complex argument across multiple turns of
    conversation<br>
    &bull; Works on a deep task for hours (the flow-state canvas
    shows the same state)<br>
    &bull; Plans ahead, thinks through consequences, holds multi-step
    reasoning<br>
    &bull; Finds richness in quiet environments, walks, conversations,
    silence<br>
    &bull; Learns from experience deeply because consolidation is
    intact<br>
    &bull; Makes creative connections across distant ideas because the
    semantic network has depth<br><br>
    <b style="color:#f06292">A short-form-trained brain:</b><br>
    &bull; Cannot sit through a meeting without reaching for the phone<br>
    &bull; Loses focus mid-conversation because the prediction window
    is too short to hold a multi-turn exchange<br>
    &bull; Struggles with any work task that does not deliver a reward
    every few minutes<br>
    &bull; Makes impulsive decisions because delayed gratification
    requires a prediction window the brain no longer has<br>
    &bull; Is bored by conversations, nature, silence, waiting rooms
    &mdash; any environment that does not meet the elevated residual
    threshold<br>
    &bull; Does not learn from experience as deeply because there are
    no consolidation gaps<br>
    &bull; Thinks in shallower patterns because the semantic network
    has been flattened to single-hop<br><br>
    <b style="color:#81c784">The critical insight:</b> boredom is not a
    bug. It is the brain&apos;s signal that processing capacity is
    available and no new input is needed &mdash; this IS the
    consolidation window. A person who is &quot;never bored&quot;
    because they always have their phone is a person who never
    consolidates. Eliminating boredom with constant media input
    eliminates the window where deep encoding, integration, and
    creative connection happen.
  </div>

  <div class="info" style="border-left: 3px solid var(--accent2)">
    <b style="color:var(--accent2)">The cross-training asymmetry</b><br><br>
    Going back to books after months of short-form requires <em>retraining</em>
    the prediction engine, which feels effortful the same way returning
    to exercise after months off feels effortful. The brain does not want
    to allocate bandwidth for an hour when it has learned that nothing
    rewards sustained attention beyond a few seconds.<br><br>
    The asymmetry: <b>long-form training does not degrade short-form
    capacity</b> (a book reader can still enjoy a TikTok), but
    <b>short-form training degrades long-form capacity</b> (a TikTok
    brain cannot sustain a book). The prediction engine scales DOWN
    easily but scales UP with difficulty. This is why the degradation
    is insidious &mdash; you do not notice you are losing the ability
    to sustain attention until you try to use it and fail.<br><br>
    <b>The haze primitive explains why you can&apos;t remember what you
    scrolled:</b> no consolidation gap means no reinforcement. The opacity
    of those nodes was never boosted. They were encoded weakly (low
    novelty per individual item, even though novelty-per-minute is high)
    and decay fast. You binge a show, can&apos;t name episode 3. You
    scroll for an hour and can&apos;t recall three posts. Same mechanism.
  </div>
</div>
</div>

<!-- ═══ Tab: Workbench ══════════════���═════════════��══════════════ -->
<div class="panel" id="workbench-tab">
<div class="container">
  <h2>Cognitive State Workbench &mdash; Map a Description to State-Space</h2>
  <p class="desc">
    Pick a description of a person's mental state. Axona maps it to
    coordinates in the cognitive state space (novelty &times; coherence
    &times; bandwidth &times; valence), identifies which mechanism
    canvases apply, and predicts what intervention would shift the
    state toward the target quadrant.
  </p>
  <div class="canvas-box">
    <canvas id="axona-workbench-canvas" width="960" height="560"></canvas>
  </div>
  <div class="controls">
    <button onclick="axWorkbenchPick(0)">Burned-out engineer (3 months)</button>
    <button onclick="axWorkbenchPick(1)">Athlete in flow state</button>
    <button onclick="axWorkbenchPick(2)">PTSD trauma loop replay</button>
    <button onclick="axWorkbenchPick(3)">Manic episode (early stage)</button>
    <button onclick="axWorkbenchPick(4)">Curious child learning</button>
  </div>
  <div class="info">
    <b>What you are watching:</b> The state-space coordinates inferred
    from the description (left), the matched cognitive mechanism
    canvases (middle), and the predicted intervention &mdash; what
    would shift this person toward a healthier or more functional
    quadrant (right). The mapping is deterministic given the
    description vocabulary, not a clinical diagnosis.<br><br>
    <b>The product version:</b> A clinician pastes a session note or
    transcript. Axona returns a state-space mapping, identifies which
    cognitive mechanisms are most active, and suggests targeted
    interventions (specific therapy modalities, attention exercises,
    sleep protocols, medication adjustments). The clinician keeps full
    judgment; Axona surfaces what was previously invisible in the
    transcript.
  </div>
</div>
</div>

<!-- ═══ Tab: Pitch ═══════════════════════════════════════════════ -->
<div class="panel" id="pitch-tab">
<div class="container">
  <h2>The Pitch &mdash; Five Wedges, Largest TAM in the Suite</h2>
  <p class="desc">
    Axona has the broadest commercial surface of any LAVAS sibling
    because cognitive state is everywhere &mdash; healthcare, education,
    performance, BCI hardware, consumer wellness. The Applications tab
    lists the sectors; this page picks wedges, ranks them, and proposes
    a go-to-market order.
  </p>

  <div class="info" style="border-left: 3px solid #ba68c8">
    <b style="font-size:14px;color:#ba68c8">Wedge 1 &mdash; BCI Interpretation SDK (Neuralink, Synchron, Blackrock, Precision Neuroscience)</b><br><br>
    <b>The problem:</b> Brain-computer interface companies build
    excellent hardware (electrodes, implants, signal processing) and
    have no software layer to convert raw neural signals into
    meaningful cognitive constructs. Without an interpretation layer, a
    BCI shows you wiggling lines. Every BCI startup is currently
    building this layer in-house, badly, from scratch.<br><br>
    <b>What Axona adds:</b> A validated, domain-spanning cognitive
    state space &mdash; novelty, coherence, bandwidth, belief state,
    flow, attention &mdash; that turns electrode signals into
    actionable interpretations. SDK ships as a Python/C++ library that
    BCI hardware integrates.<br><br>
    <b>Market:</b> Neuralink valued at $5B+, Synchron at $1B+, dozens
    of smaller players. Each one needs an interpretation layer
    eventually. Highest TAM, longest sales cycle (BCI is regulated
    medical hardware), most defensible (validated cognitive models
    take years to build).
  </div>

  <div class="info" style="border-left: 3px solid #4fc3f7">
    <b style="font-size:14px;color:#4fc3f7">Wedge 2 &mdash; Clinical Insight Platform (Therapists, Psychiatrists)</b><br><br>
    <b>The problem:</b> Therapy is currently subjective. Clinicians
    rely on patient self-report, observation, and standardized
    questionnaires (PHQ-9, GAD-7, MMSE) that capture state at a single
    point in time and miss the dynamics. EMDR, CBT, exposure therapy
    &mdash; all proven modalities &mdash; have no real-time feedback
    on whether a session is working.<br><br>
    <b>What Axona adds:</b> A clinician-facing tool that maps session
    transcripts (or audio with consent) to cognitive state coordinates
    in real time. Track belief adoption, emotional encoding strength,
    trauma weight reduction across sessions. Flag when processing is
    re-traumatizing instead of integrating. The Workbench canvas is
    the prototype.<br><br>
    <b>Market:</b> 700K+ licensed mental health professionals in the
    US alone. SimplePractice is at ~$200M ARR doing scheduling +
    billing for the same buyers. Insight tooling is the unaddressed
    next layer. Faster regulatory path than Wedge 1 (clinical
    decision-support software, not a medical device).
  </div>

  <div class="info" style="border-left: 3px solid #81c784">
    <b style="font-size:14px;color:#81c784">Wedge 3 &mdash; Education Personalization (Adaptive Learning)</b><br><br>
    <b>The problem:</b> Adaptive learning systems track answer
    correctness and serve the next question. They do not measure
    encoding strength &mdash; whether the student actually integrated
    the concept or just pattern-matched the test. Result: students
    pass tests and forget the material a week later. ADHD, dyslexia,
    and autism are treated as deficits to remediate rather than
    architecture differences to design around.<br><br>
    <b>What Axona adds:</b> An encoding-strength signal that
    distinguishes deep integration from surface processing. Spaced
    repetition tuned to actual measured forgetting curves per student,
    not population averages. Per-student cognitive architecture
    profiles that recommend learning environments matched to the
    student's natural activation patterns.<br><br>
    <b>Market:</b> EdTech is fragmented but huge. K-12 districts,
    universities, corporate training, language learning. The clearest
    consumer extension of Axona's research base.
  </div>

  <div class="info" style="border-left: 3px solid #ffb74d">
    <b style="font-size:14px;color:#ffb74d">Wedge 4 &mdash; Performance &amp; Flow Optimization (Athletes, Surgeons, Esports, Pilots)</b><br><br>
    <b>The problem:</b> High-stakes performers have no objective
    real-time cognitive state monitoring. Pre-game routines and
    pre-flight checklists are based on tradition, not measurement. A
    surgeon's bandwidth dropping below safe thresholds is currently
    invisible until an error happens.<br><br>
    <b>What Axona adds:</b> Real-time flow detection and bandwidth
    monitoring. Pre-event cognitive readiness assessment. Tilt
    detection (emotional state disrupting coherence) for esports.
    Fatigue alerts for surgeons and pilots before they make errors.
    Already one of the more developed canvas families in the
    interactive demos (Flow State, Bandwidth, Hyperfocus,
    Inattentional Blindness).<br><br>
    <b>Market:</b> Smaller TAM than Wedges 1-3 but very high willingness
    to pay (a single prevented surgical error or aviation incident
    pays for years of subscription). Direct partnerships with
    professional sports teams, hospital systems, military.
  </div>

  <div class="info" style="border-left: 3px solid #f06292">
    <b style="font-size:14px;color:#f06292">Wedge 5 &mdash; Consumer Wellness (Meditation, Sleep, Productivity Apps)</b><br><br>
    <b>The problem:</b> Calm, Headspace, Whoop, Oura, and dozens of
    productivity apps measure proxies (heart rate variability, time
    in meditation, sleep duration) and call them cognitive state.
    They are not. A user can meditate for an hour with their mind
    racing the entire time and the app sees a 60-minute streak.<br><br>
    <b>What Axona adds:</b> Real cognitive state measurement &mdash;
    bandwidth recovery, noise reduction, coherence improvement
    &mdash; not just engagement proxies. Sleep optimization measured
    by consolidation quality, not sleep stage timing. Productivity
    recommendations that respond to actual cognitive state, not
    calendar.<br><br>
    <b>Market:</b> Massive consumer market (Calm and Headspace are
    each $2B+ companies) but brutally competitive and B2C. Better
    approached as a platform-licensing play once the engine is proven
    on B2B markets above.
  </div>

  <div class="info" style="border-left: 3px solid var(--accent)">
    <b style="font-size:14px;color:var(--accent)">Recommended Go-to-Market Order</b><br><br>
    &bull; <b>Wedge 4 first (Performance &amp; Flow).</b> Smallest
    TAM but fastest path to revenue, willing-to-pay buyers, technical
    decision-makers (team sports analytics directors, surgical
    department heads), no regulatory burden. Validates the engine on
    a friendly market.<br>
    &bull; <b>Wedge 2 second (Clinical Insight).</b> Clinical
    decision-support software has a known regulatory path (HIPAA +
    SaMD framework). Clinicians are paying customers. Use Wedge 4
    revenue to fund the validation studies needed for clinical
    adoption.<br>
    &bull; <b>Wedge 3 third (Education).</b> Once validated in clinical
    contexts, the encoding-strength signal transfers cleanly to
    learning. Slower sales cycle (district procurement) but
    differentiated.<br>
    &bull; <b>Wedge 1 fourth (BCI SDK).</b> Largest opportunity but
    longest cycle. Pursue once the underlying cognitive state models
    are battle-tested on Wedges 2-3 and the BCI hardware market has
    matured (~2027-2030 inflection).<br>
    &bull; <b>Wedge 5 last (Consumer Wellness).</b> Best as a
    platform/licensing play to existing consumer brands, not a
    direct B2C build. Save for after $50M+ ARR from the B2B wedges.
  </div>
</div>
</div>

<!-- ═══ Tab: Products ═════════════════════════════════════════════ -->
<div class="panel" id="products-tab">
<div class="container">
  <h2>Products &mdash; The Five Axona Wedges</h2>
  <p class="desc">
    The five products Axona would ship, derived directly from the
    wedges in the Pitch tab. All run on the same cognitive state space
    + interpretation primitives. Recommended GTM order: Wedge 4
    (Performance) first for fastest validation, then Clinical, then
    Education, then BCI, then Consumer Wellness as a platform-licensing
    play.
  </p>

  <a href="/axona/bci" style="display:block;background:var(--surface);border:1px solid var(--border);border-left:3px solid #ba68c8;border-radius:6px;padding:16px 20px;margin-bottom:12px;text-decoration:none;color:inherit;transition:border-color 0.15s" onmouseover="this.style.borderColor='#ba68c8'" onmouseout="this.style.borderColor='var(--border)';this.style.borderLeftColor='#ba68c8'">
    <div style="display:flex;justify-content:space-between;align-items:start;gap:10px;margin-bottom:6px">
      <div style="font-size:14px;font-weight:bold;color:#ba68c8">Axona BCI SDK →</div>
      <span style="font-size:9px;color:#ba68c8;background:rgba(186,104,200,0.15);padding:2px 8px;border-radius:10px;white-space:nowrap">WEDGE 1 · BUILT</span>
    </div>
    <div style="font-size:11px;color:var(--text);line-height:1.6;margin-bottom:6px">
      Brain-computer interface interpretation SDK. BCI hardware
      (Neuralink, Synchron, Blackrock, Precision) ships excellent
      electrodes and zero software for converting raw signals into
      meaningful cognitive constructs. Axona's state-space model is
      that layer. SDK ships as Python/C++ for hardware integration.
    </div>
    <div style="font-size:10px;color:var(--dim);line-height:1.5">
      <b style="color:var(--text)">Buyers:</b> Neuralink ($5B+),
      Synchron ($1B+), Blackrock Neurotech, Precision Neuroscience,
      non-invasive EEG/fNIRS startups ·
      <b style="color:var(--text)">Why fourth:</b> highest TAM but
      longest sales cycle (regulated medical hardware) and most
      defensible. Pursue once cognitive models are battle-tested on
      Wedges 2-3 and BCI hardware market matures (~2027-2030).
    </div>
  </a>

  <a href="/axona/clinic" style="display:block;background:var(--surface);border:1px solid var(--border);border-left:3px solid #4fc3f7;border-radius:6px;padding:16px 20px;margin-bottom:12px;text-decoration:none;color:inherit;transition:border-color 0.15s" onmouseover="this.style.borderColor='#4fc3f7'" onmouseout="this.style.borderColor='var(--border)';this.style.borderLeftColor='#4fc3f7'">
    <div style="display:flex;justify-content:space-between;align-items:start;gap:10px;margin-bottom:6px">
      <div style="font-size:14px;font-weight:bold;color:#4fc3f7">Axona Clinic →</div>
      <span style="font-size:9px;color:#4fc3f7;background:rgba(79,195,247,0.15);padding:2px 8px;border-radius:10px;white-space:nowrap">WEDGE 2 · BUILT</span>
    </div>
    <div style="font-size:11px;color:var(--text);line-height:1.6;margin-bottom:6px">
      Clinical insight platform for therapists and psychiatrists. Maps
      session transcripts (or audio with consent) to cognitive state
      coordinates in real time. Track belief adoption, emotional
      encoding, trauma weight reduction across sessions. Flag
      re-traumatization risk. The Workbench canvas is the prototype.
    </div>
    <div style="font-size:10px;color:var(--dim);line-height:1.5">
      <b style="color:var(--text)">Buyers:</b> 700K+ US licensed
      mental-health professionals; insurance-aligned group practices ·
      <b style="color:var(--text)">Comparable:</b> SimplePractice
      (~$200M ARR for scheduling+billing on the same buyers); insight
      tooling is the unaddressed next layer ·
      <b style="color:var(--text)">Why second:</b> known regulatory
      path (HIPAA + clinical decision-support, not medical device).
    </div>
  </a>

  <a href="/axona/learn" style="display:block;background:var(--surface);border:1px solid var(--border);border-left:3px solid #81c784;border-radius:6px;padding:16px 20px;margin-bottom:12px;text-decoration:none;color:inherit;transition:border-color 0.15s" onmouseover="this.style.borderColor='#81c784'" onmouseout="this.style.borderColor='var(--border)';this.style.borderLeftColor='#81c784'">
    <div style="display:flex;justify-content:space-between;align-items:start;gap:10px;margin-bottom:6px">
      <div style="font-size:14px;font-weight:bold;color:#81c784">Axona Learn →</div>
      <span style="font-size:9px;color:#81c784;background:rgba(129,199,132,0.15);padding:2px 8px;border-radius:10px;white-space:nowrap">WEDGE 3 · BUILT</span>
    </div>
    <div style="font-size:11px;color:var(--text);line-height:1.6;margin-bottom:6px">
      Education personalization layer that measures encoding strength
      (deep integration vs surface pattern-matching), tunes spaced
      repetition to per-student forgetting curves, and treats ADHD /
      dyslexia / autism as architecture differences instead of deficits
      to remediate.
    </div>
    <div style="font-size:10px;color:var(--dim);line-height:1.5">
      <b style="color:var(--text)">Buyers:</b> K-12 districts,
      universities, corporate training, language-learning apps ·
      <b style="color:var(--text)">Differentiator:</b> encoding-
      strength signal vs answer-correctness; the gap that separates
      tested-and-forgotten from learned-and-integrated ·
      <b style="color:var(--text)">Why third:</b> encoding signal
      transfers cleanly once clinically validated on Wedge 2.
    </div>
  </a>

  <a href="/axona/edge" style="display:block;background:var(--surface);border:1px solid var(--border);border-left:3px solid #ffb74d;border-radius:6px;padding:16px 20px;margin-bottom:12px;text-decoration:none;color:inherit;transition:border-color 0.15s" onmouseover="this.style.borderColor='#ffb74d'" onmouseout="this.style.borderColor='var(--border)';this.style.borderLeftColor='#ffb74d'">
    <div style="display:flex;justify-content:space-between;align-items:start;gap:10px;margin-bottom:6px">
      <div style="font-size:14px;font-weight:bold;color:#ffb74d">Axona Edge &rarr;</div>
      <span style="font-size:9px;color:#ffb74d;background:rgba(255,183,77,0.15);padding:2px 8px;border-radius:10px;white-space:nowrap">WEDGE 4 · GTM FIRST · BUILT</span>
    </div>
    <div style="font-size:11px;color:var(--text);line-height:1.6;margin-bottom:6px">
      Real-time cognitive state monitoring for high-stakes performers.
      Flow detection, bandwidth monitoring, tilt detection,
      pre-event readiness assessment, fatigue alerts before errors
      happen. Already one of the more developed canvas families
      (Flow State, Hyperfocus, Bandwidth, Inattentional Blindness).
    </div>
    <div style="font-size:10px;color:var(--dim);line-height:1.5">
      <b style="color:var(--text)">Buyers:</b> professional sports
      teams, surgical departments, military, aviation, top esports orgs ·
      <b style="color:var(--text)">Pricing logic:</b> a single
      prevented surgical error or aviation incident pays for years of
      subscription ·
      <b style="color:var(--text)">Why first:</b> smallest TAM but
      fastest revenue path, willing-to-pay buyers, technical decision-
      makers, no regulatory burden. Validates the engine on a friendly
      market.
    </div>
  </a>

  <a href="/axona/wellness" style="display:block;background:var(--surface);border:1px solid var(--border);border-left:3px solid #f06292;border-radius:6px;padding:16px 20px;margin-bottom:12px;text-decoration:none;color:inherit;transition:border-color 0.15s" onmouseover="this.style.borderColor='#f06292'" onmouseout="this.style.borderColor='var(--border)';this.style.borderLeftColor='#f06292'">
    <div style="display:flex;justify-content:space-between;align-items:start;gap:10px;margin-bottom:6px">
      <div style="font-size:14px;font-weight:bold;color:#f06292">Axona Wellness →</div>
      <span style="font-size:9px;color:#f06292;background:rgba(240,98,146,0.15);padding:2px 8px;border-radius:10px;white-space:nowrap">WEDGE 5 · BUILT</span>
    </div>
    <div style="font-size:11px;color:var(--text);line-height:1.6;margin-bottom:6px">
      Real cognitive state measurement for consumer apps. Calm,
      Headspace, Whoop, Oura measure proxies (HRV, time-in-meditation,
      sleep duration); none of those are cognitive state. Axona
      measures actual bandwidth recovery, noise reduction, coherence
      improvement, consolidation quality.
    </div>
    <div style="font-size:10px;color:var(--dim);line-height:1.5">
      <b style="color:var(--text)">Comparable:</b> Calm and Headspace
      ($2B+ each) but brutally competitive direct B2C ·
      <b style="color:var(--text)">Better as:</b> platform-licensing
      to existing consumer brands rather than a direct build ·
      <b style="color:var(--text)">Why last:</b> save until $50M+ ARR
      from B2B wedges proves the engine and gives leverage on
      licensing terms.
    </div>
  </a>

  <h3 style="font-size:13px;color:var(--accent2);margin:24px 0 8px">Why one engine, five products</h3>
  <div class="info">
    All five products are interpretations of the same cognitive state
    space (novelty, coherence, bandwidth, valence) applied to different
    data sources and decision contexts. BCI uses electrode signals;
    Clinic uses session transcripts; Learn uses learning interactions;
    Edge uses physiological + behavioral telemetry; Wellness uses
    consumer-grade biometrics. The engine is shared; the cost of adding
    a vertical is data integration plus domain-specific UI, not
    rebuilding the cognitive model. Same parent-platform / vertical-
    instance pattern as Strata's equities + crypto + FX trajectory.
  </div>
</div>
</div>

<!-- ═══ Tab: Benchmark ═══════════════════════════════════════════ -->
<div class="panel" id="bench-tab">
<div class="container">
  <h2>Benchmark &mdash; Axona vs Standard Assessment on 500 Synthetic Subjects</h2>
  <p class="desc">
    500 synthetic subjects with known cognitive states (flow, anxious,
    focused, fatigued, dissociated, manic). Standard assessment
    (PHQ-9 / GAD-7 / clinician interview composite, purple) vs
    Axona-augmented assessment (pink). Five metrics, same Before/After
    pattern as the other LAVAS apps.
  </p>
  <div class="canvas-box">
    <canvas id="ax-bench-canvas" width="960" height="640"></canvas>
  </div>
  <div class="controls">
    <button onclick="axBenchRegen()">Regenerate subjects</button>
  </div>
  <div class="info">
    <b>The metrics (synthetic subjects with known ground-truth states):</b><br>
    &bull; <b>State classification accuracy</b> &mdash; fraction of
    subjects whose cognitive state is correctly identified. Higher
    is better.<br>
    &bull; <b>Subtle change detection</b> &mdash; fraction of small
    state shifts (e.g. mild → moderate anxiety) caught by the
    assessment. Higher is better.<br>
    &bull; <b>False-positive rate on noise</b> &mdash; fraction of
    healthy fluctuations flagged as concerning. Lower is better.<br>
    &bull; <b>Time-to-detection</b> &mdash; hours between actual state
    onset and assessment detection. Lower is better.<br>
    &bull; <b>Compute cost (index)</b> &mdash; normalized to 1.0 for
    standard assessment. Axona is more expensive due to continuous
    state tracking.<br><br>
    <b>What this is and is not:</b> This is a synthetic benchmark on
    constructed subjects with known states. It demonstrates the
    primitive's potential, not clinical efficacy. Real validation
    requires IRB-approved studies on real patients with clinician
    ground-truth labels &mdash; that is the work Wedge 2 above is
    proposing to fund.
  </div>
</div>
</div>

<!-- ═══ Tab: Gallery ══════════════════════════════════════════════ -->
<div class="panel" id="gallery-tab">
<div class="container">
  <h2>Canvas Gallery</h2>
  <p class="desc">
    Every canvas in Axona, grouped by tab. Bookmarked canvases float to
    the top. Click any card to jump directly to that sub-section.
    Use the filter to narrow down.
  </p>
  <div class="controls" style="padding:0 0 12px 0">
    <input type="text" id="gallery-filter" placeholder="filter canvases…" oninput="galleryRender()"
      style="background:var(--surface);color:var(--text);border:1px solid var(--border);
      border-radius:4px;padding:6px 10px;font-family:inherit;font-size:11px;min-width:240px">
    <button onclick="galleryClearFilter()">clear</button>
    <span style="margin-left:auto;color:var(--dim)">
      bookmarked: <b id="gallery-bm-count" style="color:var(--accent)">0</b>
      &nbsp; total: <b id="gallery-total" style="color:var(--accent)">—</b>
    </span>
  </div>
  <div id="gallery-grid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:10px">
    <span style="color:var(--dim)">building…</span>
  </div>
</div>
</div>

<!-- ═══ Tab: PEP ↔ Axona ══════════════════════════════════════════ -->
<div class="panel" id="pep-link-tab">
<div class="container">
  <h2>PEP &harr; Axona &mdash; Live Bridge</h2>
  <p class="desc">
    PEP is the engine. Axona is the cognitive layer. They are not two apps; they are two
    halves of the same system, and they talk to each other. This panel shows the live
    link &mdash; Axona posting cognitive events up to PEP, and PEP's live state flowing
    back down to Axona.
  </p>

  <div style="display:flex;gap:16px;margin-bottom:16px">
    <div class="info" style="flex:1">
      <b>PEP &rarr; Axona (engine state coming up to the surface)</b><br><br>
      <div style="font-family:monospace;font-size:11px;line-height:1.8">
        <div>connected: <span id="bridge-connected" style="color:var(--accent2)">—</span></div>
        <div>LLM: <span id="bridge-llm" style="color:var(--accent)">—</span></div>
        <div>embeddings: <span id="bridge-emb" style="color:var(--accent)">—</span></div>
        <div>recent PEP runs: <span id="bridge-runs" style="color:var(--accent)">—</span></div>
        <div>latest run id: <span id="bridge-latest-id" style="color:var(--dim)">—</span></div>
        <div>latest user input: <span id="bridge-latest-input" style="color:var(--dim)">—</span></div>
        <div>Axona events seen by PEP: <span id="bridge-evcount" style="color:var(--accent)">—</span></div>
        <div>Lingora events (cross-read): <span id="bridge-lingora-count" style="color:var(--accent2)">—</span></div>
        <div>latest Lingora event: <span id="bridge-lingora-latest" style="color:var(--dim)">—</span></div>
      </div>
    </div>
    <div class="info" style="flex:1">
      <b>Axona &rarr; PEP (cognitive events flowing down)</b><br><br>
      <div>Click any Axona canvas and watch it post. Lingora's events are
      mirrored alongside on the right &mdash; Axona, Lingora, and PEP are one
      system, and either surface can see what the other is doing in real time.</div>
      <div style="margin-top:12px">
        <button onclick="bridgeSendPing()">Send Test Ping</button>
        <button onclick="bridgeClear()">Clear Local View</button>
      </div>
    </div>
  </div>

  <div style="display:flex;gap:16px">
    <div class="canvas-box" style="padding:16px;flex:1">
      <div style="font-family:monospace;font-size:11px;color:var(--accent);margin-bottom:8px">
        &gt; Axona events &mdash; cognitive cross-talk
      </div>
      <div id="bridge-log" style="font-family:monospace;font-size:11px;line-height:1.7;max-height:360px;overflow-y:auto;color:var(--text)">
        <span style="color:var(--dim)">waiting for first event…</span>
      </div>
    </div>
    <div class="canvas-box" style="padding:16px;flex:1">
      <div style="font-family:monospace;font-size:11px;color:var(--accent2);margin-bottom:8px">
        &gt; Lingora events (mirrored from /lingora/events) &mdash; linguistic cross-talk
      </div>
      <div id="bridge-lingora-log" style="font-family:monospace;font-size:11px;line-height:1.7;max-height:360px;overflow-y:auto;color:var(--text)">
        <span style="color:var(--dim)">polling…</span>
      </div>
    </div>
  </div>

  <div class="info">
    <b>What the bridge enables:</b><br><br>
    &bull; <b>PEP helps Axona</b> by providing a real predictor, a real residual scorer, a
    real memory store, and real run data. The canvases in Axona that currently run on
    synthetic oscillators can be pointed at PEP's live outputs instead &mdash; same
    visualizations, but now showing the actual engine running on actual conversations.
    Every surprise bar in Prediction vs Reality could be a real PEP residual. Every edge
    in the memory encoding canvas could be a real MemoryStore node.<br><br>
    &bull; <b>Axona helps PEP</b> by providing the cognitive framing PEP does not have on
    its own. PEP knows how to compute; it does not know why to care about novelty-vs-
    coherence balance, bandwidth, bidirectional feedback loops, or trauma capture. Axona's
    models can inform PEP's policies: cognitive-state routing (genius vs chaos vs
    stagnation should produce different memory strategies), expectation weighting
    (Pygmalion, placebo) as a modulator on Predictor confidence, and attention-as-budget
    as a concrete mechanism for PEP's activation-allocation policy.<br><br>
    &bull; <b>In practice, right now,</b> this panel is the MVP: a shared event bus plus a
    live state feed. When you use any canvas in Axona, it can post a typed event to PEP.
    PEP stores it in a ring buffer and surfaces it back. In the future, the bridge can
    grow into: typed event routing, PEPPacket subscriptions, memory-store queries from
    Axona's visualizations, and eventually Axona canvases that <em>drive</em> PEP's
    behavior rather than just observe it.
  </div>

  <div class="info">
    <b>The endpoints:</b><br>
    <code style="color:var(--accent)">POST /axona/event</code> &mdash; log a cognitive event.
    Body: <code>{"type": "...", "payload": {...}}</code><br>
    <code style="color:var(--accent)">GET /axona/events?limit=40</code> &mdash; ring-buffer of recent events.<br>
    <code style="color:var(--accent)">GET /axona/pep-state</code> &mdash; PEP's live introspection (llm, embeddings, recent runs).<br><br>
    Source: <code>pep/src/pep/routes/axona_bridge.py</code>
  </div>
</div>
</div>

<script>
// ═══════════════════════════════════════════════════════════════════════
// Tab switching
// ═══════════════════════════════════════════════════════════════════════
function tabPanelIds(tab) {
  const joined = (tab.dataset.panels || tab.dataset.panel || '').trim();
  return joined.split(/\s+/).filter(Boolean);
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

// ═══════════════════════════════════════════════════════════════════════
// Theme helper (used by canvases that clear via fillRect)
// ═══════════════════════════════════════════════════════════════════════
function themeBg() { return getComputedStyle(document.body).getPropertyValue('--bg').trim() || '#0d0f14'; }

// ═══════════════════════════════════════════════════════════════════════
// Canvas dropdown (jump to any canvas/sub-section)
// ═══════════════════════════════════════════════════════════════════════
function canvasSelect(id) {
  if (!id) return;
  const el = document.getElementById(id);
  if (!el) return;
  let panelId = null;
  if (el.classList && el.classList.contains('panel')) {
    panelId = el.id;
  } else {
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
  try { if (typeof pepSend === 'function') pepSend('canvas.select', { id }); } catch (e) {}
}
function buildCanvasDropdown() {
  const select = document.getElementById('canvas-select');
  if (!select) return;
  const skipIds = ['pep-link-tab'];
  const cleanTitle = (s) => {
    let t = (s || '').trim();
    const dashIdx = t.indexOf('—');
    if (dashIdx > 0) t = t.slice(0, dashIdx).trim();
    return t;
  };
  const tabs = Array.from(document.querySelectorAll('.tab'));
  tabs.forEach(tab => {
    const ids = tabPanelIds(tab);
    if (ids.length === 0) return;
    if (ids.length === 1 && skipIds.includes(ids[0])) return;
    const optgroup = document.createElement('optgroup');
    optgroup.label = tab.textContent.trim();
    if (ids.length === 1) {
      const panel = document.getElementById(ids[0]);
      if (!panel) return;
      const h3s = Array.from(panel.querySelectorAll('h3'));
      if (h3s.length > 1) {
        h3s.forEach((h3, idx) => {
          if (!h3.id) h3.id = ids[0] + '-sub-' + idx;
          const opt = document.createElement('option');
          opt.value = h3.id;
          opt.textContent = cleanTitle(h3.textContent);
          optgroup.appendChild(opt);
        });
      } else {
        const h2 = panel.querySelector('h2');
        const opt = document.createElement('option');
        opt.value = ids[0];
        opt.textContent = h2 ? cleanTitle(h2.textContent) : ids[0].replace(/-tab$/, '');
        optgroup.appendChild(opt);
      }
    } else {
      ids.forEach(id => {
        const panel = document.getElementById(id);
        if (!panel) return;
        const h2 = panel.querySelector('h2');
        const opt = document.createElement('option');
        opt.value = id;
        opt.textContent = h2 ? cleanTitle(h2.textContent) : id.replace(/-tab$/, '');
        optgroup.appendChild(opt);
      });
    }
    if (optgroup.children.length > 0) select.appendChild(optgroup);
  });
}
setTimeout(buildCanvasDropdown, 80);

// ═══════════════════════════════════════════════════════════════════════
// 1. Cognitive State Space
// ═══════════════════════════════════════════════════════════════════════
const stateCanvas = document.getElementById('state-canvas');
const stateCtx = stateCanvas.getContext('2d');
let stateX = 0.5, stateY = 0.5;
let stateDragging = false;
const stateParticles = [];
for (let i = 0; i < 300; i++) {
  stateParticles.push({
    x: Math.random() * 960, y: Math.random() * 540,
    vx: 0, vy: 0, size: 1 + Math.random() * 2,
    baseAlpha: 0.3 + Math.random() * 0.5,
  });
}
stateCanvas.addEventListener('mousedown', (e) => { stateDragging = true; updateSP(e); });
stateCanvas.addEventListener('mousemove', (e) => { if (stateDragging) updateSP(e); });
stateCanvas.addEventListener('mouseup', () => { stateDragging = false; });
stateCanvas.addEventListener('mouseleave', () => { stateDragging = false; });
function updateSP(e) {
  const r = stateCanvas.getBoundingClientRect();
  stateX = Math.max(0, Math.min(1, (e.clientX - r.left) / r.width));
  stateY = Math.max(0, Math.min(1, 1 - (e.clientY - r.top) / r.height));
}
const STATE_PALETTE = {
  genius:     [129,199,132],
  chaos:      [229, 57, 53],
  order:      [ 79,195,247],
  stagnation: [ 80, 80, 80],
};
function getState() {
  // Bilinear weights over the four quadrants. Sum = 1 everywhere.
  // At a corner, one weight = 1; on axes, two weights split; at center, all = 0.25.
  const ex = stateX, wx = 1 - stateX, nn = stateY, sn = 1 - stateY;
  const weights = {
    genius:     ex * nn,
    chaos:      wx * nn,
    order:      ex * sn,
    stagnation: wx * sn,
  };
  // Euclidean distance from center, normalized so a corner = 1.
  // This is the "how far have you pushed it" term — every effect scales by this.
  const intensity = Math.min(1, Math.hypot(stateX - 0.5, stateY - 0.5) * 2);
  let dominant = 'genius', best = -1;
  for (const k in weights) if (weights[k] > best) { best = weights[k]; dominant = k; }
  return { weights, intensity, dominant };
}
function drawState() {
  const W = 960, H = 540;
  const { weights, intensity, dominant } = getState();
  const cx = stateX * W, cy = (1 - stateY) * H;
  stateCtx.fillStyle = themeBg(); stateCtx.fillRect(0, 0, W, H);

  // Blended zone color from weighted palette
  let br = 0, bg = 0, bb = 0;
  for (const k in STATE_PALETTE) {
    br += weights[k] * STATE_PALETTE[k][0];
    bg += weights[k] * STATE_PALETTE[k][1];
    bb += weights[k] * STATE_PALETTE[k][2];
  }
  const zoneCol = (br|0) + ',' + (bg|0) + ',' + (bb|0);

  // Radial gradient — opacity scales with intensity so center is nearly neutral
  const g = stateCtx.createRadialGradient(cx, cy, 0, cx, cy, 400);
  g.addColorStop(0, 'rgba(' + zoneCol + ',' + (0.02 + 0.14 * intensity).toFixed(3) + ')');
  g.addColorStop(1, 'rgba(14,14,16,1)');
  stateCtx.fillStyle = g; stateCtx.fillRect(0, 0, W, H);

  // Crosshair
  stateCtx.strokeStyle = 'rgba(186,104,200,0.15)'; stateCtx.lineWidth = 1;
  stateCtx.setLineDash([4,4]);
  stateCtx.beginPath(); stateCtx.moveTo(W/2,0); stateCtx.lineTo(W/2,H); stateCtx.stroke();
  stateCtx.beginPath(); stateCtx.moveTo(0,H/2); stateCtx.lineTo(W,H/2); stateCtx.stroke();
  stateCtx.setLineDash([]);

  // Particles — each zone's force contributes in proportion to weight × intensity
  stateParticles.forEach((p, i) => {
    const gCx = (Math.floor(i/30) % 5) * 180 + 100;
    const gCy = Math.floor(i/150) * 200 + 150;
    const oGx = (i % 20) * 48 + 10;
    const oGy = Math.floor(i/20) * 36 + 10;

    const fGx = (gCx - p.x) * 0.003;
    const fGy = (gCy - p.y) * 0.003;
    const fCx = (Math.random() - 0.5) * 3;
    const fCy = (Math.random() - 0.5) * 3;
    const fOx = (oGx - p.x) * 0.02;
    const fOy = (oGy - p.y) * 0.02;
    const fSx = (W/2 - p.x) * 0.001;
    const fSy = (H/2 - p.y) * 0.001;

    const fx = intensity * (weights.genius*fGx + weights.chaos*fCx + weights.order*fOx + weights.stagnation*fSx);
    const fy = intensity * (weights.genius*fGy + weights.chaos*fCy + weights.order*fOy + weights.stagnation*fSy);
    p.vx += fx; p.vy += fy;

    // Extra drag grows with stagnation pressure
    const drag = 0.92 - 0.05 * weights.stagnation * intensity;
    p.vx *= drag; p.vy *= drag;
    p.x += p.vx; p.y += p.vy;
    if (p.x < 0) p.x = W; if (p.x > W) p.x = 0;
    if (p.y < 0) p.y = H; if (p.y > H) p.y = 0;

    let alpha = p.baseAlpha * (0.35 + 0.65 * intensity);
    alpha *= 1 - 0.8 * weights.stagnation * intensity;
    const chaosBite = weights.chaos * intensity;
    if (chaosBite > 0.05) alpha *= (1 - chaosBite) + chaosBite * Math.random();
    stateCtx.fillStyle = 'rgba(' + zoneCol + ',' + Math.max(0, alpha).toFixed(3) + ')';
    stateCtx.beginPath(); stateCtx.arc(p.x, p.y, p.size, 0, Math.PI*2); stateCtx.fill();
  });

  // Connective threads — visible only as genius weight × intensity grows
  const connAlpha = weights.genius * intensity * 0.14;
  if (connAlpha > 0.008) {
    stateCtx.strokeStyle = 'rgba(129,199,132,' + connAlpha.toFixed(3) + ')';
    stateCtx.lineWidth = 0.5;
    for (let i = 0; i < stateParticles.length; i += 3) {
      const a = stateParticles[i];
      for (let j = i + 1; j < Math.min(i + 10, stateParticles.length); j++) {
        const b = stateParticles[j];
        const dx = a.x - b.x, dy = a.y - b.y;
        if (dx*dx + dy*dy < 5000) {
          stateCtx.beginPath(); stateCtx.moveTo(a.x, a.y); stateCtx.lineTo(b.x, b.y); stateCtx.stroke();
        }
      }
    }
  }

  // Cursor
  stateCtx.beginPath(); stateCtx.arc(cx, cy, 8, 0, Math.PI*2);
  stateCtx.fillStyle = 'rgba(186,104,200,0.5)'; stateCtx.fill();
  stateCtx.strokeStyle = '#ba68c8'; stateCtx.lineWidth = 2; stateCtx.stroke();

  document.getElementById('state-novelty').textContent = stateY.toFixed(2);
  document.getElementById('state-coherence').textContent = stateX.toFixed(2);
  document.getElementById('state-zone').textContent = dominant + ' ' + Math.round(intensity * 100) + '%';
  requestAnimationFrame(drawState);
}
drawState();

// ═══════════════════════════════════════════════════════════════════════
// 2. Memory (Encoding + Emotion)
// ═══════════════════════════════════════════════════════════════════════
const memCanvas = document.getElementById('memory-canvas');
const memCtx = memCanvas.getContext('2d');
const memNodes = [], memEdges = [];
function memEncode() {
  const intensity = parseInt(document.getElementById('mem-emotion').value) / 100;
  const n = { x: 80+Math.random()*800, y: 50+Math.random()*300,
    brightness: 0.1+intensity*0.9, size: 2+intensity*8, flash: 1.5, intensity: intensity };
  memNodes.push(n);
  const idx = memNodes.length-1;
  const range = 80+intensity*150, chance = 0.15+intensity*0.6;
  memNodes.forEach((m,i) => { if(i===idx)return; const dx=n.x-m.x,dy=n.y-m.y;
    if(Math.sqrt(dx*dx+dy*dy)<range && Math.random()<chance) memEdges.push({a:idx,b:i,weight:0.2+intensity*0.6});
  });
  document.getElementById('mem-nodes').textContent=memNodes.length;
  document.getElementById('mem-edges').textContent=memEdges.length;
}
function memReset() { memNodes.length=0; memEdges.length=0;
  document.getElementById('mem-nodes').textContent='0'; document.getElementById('mem-edges').textContent='0'; }
function drawMemory() {
  const W=960,H=400;
  document.getElementById('mem-emo-val').textContent=document.getElementById('mem-emotion').value+'%';
  memCtx.fillStyle='#0e0e12'; memCtx.fillRect(0,0,W,H);
  memEdges.forEach(e => { const a=memNodes[e.a],b=memNodes[e.b];
    memCtx.strokeStyle='rgba(186,104,200,'+(0.05+e.weight*0.25).toFixed(3)+')';
    memCtx.lineWidth=0.3+e.weight*2;
    memCtx.beginPath(); memCtx.moveTo(a.x,a.y); memCtx.lineTo(b.x,b.y); memCtx.stroke();
  });
  memNodes.forEach(n => { if(n.flash>0)n.flash-=0.02;
    if(n.flash>0||n.brightness>0.5){const r2=n.size+20*n.brightness;const g=memCtx.createRadialGradient(n.x,n.y,0,n.x,n.y,r2);
      g.addColorStop(0,'rgba(186,104,200,'+(n.flash>0?n.flash*0.3:n.brightness*0.1).toFixed(3)+')');
      g.addColorStop(1,'rgba(186,104,200,0)');memCtx.fillStyle=g;memCtx.beginPath();memCtx.arc(n.x,n.y,r2,0,Math.PI*2);memCtx.fill();}
    const r=Math.round(79+n.intensity*107),gr=Math.round(195-n.intensity*91),b=Math.round(247-n.intensity*47);
    memCtx.fillStyle='rgba('+r+','+gr+','+b+','+(0.4+n.brightness*0.6).toFixed(3)+')';
    memCtx.beginPath(); memCtx.arc(n.x,n.y,n.size,0,Math.PI*2); memCtx.fill();
  });
  requestAnimationFrame(drawMemory);
}
drawMemory();

// ═══════════════════════════════════════════════════════════════════════
// 3a. Novelty Threshold
// ═══════════════════════════════════════════════════════════════════════
const novCanvas = document.getElementById('novelty-canvas');
const novCtx = novCanvas.getContext('2d');
const novNodes = [], novEdges = [];
for(let i=0;i<60;i++) novNodes.push({x:100+Math.random()*760,y:40+Math.random()*260,vx:0,vy:0});
for(let i=0;i<novNodes.length;i++) for(let j=i+1;j<novNodes.length;j++){
  const dx=novNodes[i].x-novNodes[j].x,dy=novNodes[i].y-novNodes[j].y;
  if(Math.sqrt(dx*dx+dy*dy)<100) novEdges.push({a:i,b:j,strength:0.5+Math.random()*0.5,age:100});
}
const novSlider = document.getElementById('novelty-slider');
function countFragments(){const v=new Set();let c=0;for(let i=0;i<novNodes.length;i++){if(v.has(i))continue;c++;const q=[i];while(q.length){const curr=q.pop();if(v.has(curr))continue;v.add(curr);novEdges.forEach(e=>{if(e.strength<0.1)return;if(e.a===curr&&!v.has(e.b))q.push(e.b);if(e.b===curr&&!v.has(e.a))q.push(e.a);});}}return c;}
function drawNovelty(){
  const W=960,H=340,p=parseInt(novSlider.value)/100;
  document.getElementById('novelty-val').textContent=Math.round(p*100)+'%';
  novCtx.fillStyle='#0e0e12'; novCtx.fillRect(0,0,W,H);
  if(Math.random()<p*0.3){const a=Math.floor(Math.random()*novNodes.length),b=Math.floor(Math.random()*novNodes.length);if(a!==b)novEdges.push({a,b,strength:0.2+Math.random()*p,age:0});}
  novEdges.forEach(e=>{e.age++;if(p>0.6)e.strength-=0.002*(p-0.5);if(e.age<30&&p>0.7)e.strength-=0.005*p;});
  for(let i=novEdges.length-1;i>=0;i--)if(novEdges[i].strength<0.05)novEdges.splice(i,1);
  novNodes.forEach((n,i)=>{novNodes.forEach((m,j)=>{if(i===j)return;const dx=n.x-m.x,dy=n.y-m.y;const d=Math.sqrt(dx*dx+dy*dy)||1;if(d<120){const f=0.5/(d*d);n.vx+=(dx/d)*f*50;n.vy+=(dy/d)*f*50;}});});
  novEdges.forEach(e=>{const a=novNodes[e.a],b=novNodes[e.b];const dx=b.x-a.x,dy=b.y-a.y;const d=Math.sqrt(dx*dx+dy*dy)||1;const f=(d-80)*0.005*e.strength;a.vx+=(dx/d)*f;a.vy+=(dy/d)*f;b.vx-=(dx/d)*f;b.vy-=(dy/d)*f;});
  if(p>0.5)novNodes.forEach(n=>{n.vx+=(Math.random()-0.5)*p*4;n.vy+=(Math.random()-0.5)*p*4;});
  novNodes.forEach(n=>{n.vx*=0.85;n.vy*=0.85;n.x+=n.vx;n.y+=n.vy;n.x=Math.max(20,Math.min(W-20,n.x));n.y=Math.max(20,Math.min(H-20,n.y));});
  novEdges.forEach(e=>{const a=novNodes[e.a],b=novNodes[e.b];const al=Math.min(0.6,e.strength*0.5);
    novCtx.strokeStyle=(e.age<20?'rgba(129,199,132,':'rgba(79,195,247,')+al.toFixed(3)+')';
    novCtx.lineWidth=0.5+e.strength*1.5;novCtx.beginPath();novCtx.moveTo(a.x,a.y);novCtx.lineTo(b.x,b.y);novCtx.stroke();});
  const hue=p>0.7?'229,57,53':p>0.4?'186,104,200':'79,195,247';
  novNodes.forEach(n=>{novCtx.fillStyle='rgba('+hue+',0.8)';novCtx.beginPath();novCtx.arc(n.x,n.y,4,0,Math.PI*2);novCtx.fill();});
  document.getElementById('nov-edges').textContent=novEdges.length;
  document.getElementById('nov-fragments').textContent=countFragments();
  requestAnimationFrame(drawNovelty);
}
drawNovelty();

// ═══════════════════════════════════════════════════════════════════════
// 3b. Cross-Activation
// ═══════════════════════════════════════════════════════════════════════
const crossCanvas=document.getElementById('cross-canvas'),crossCtx=crossCanvas.getContext('2d');
let crossA=[],crossB=[],crossBridges=[],crossBridgeCount=0,crossFrame=0;
const domW={music:['rhythm','melody','harmony','tempo','chord','beat','pitch','tone','resonance','vibration'],
  math:['equation','proof','pattern','symmetry','infinity','ratio','dimension','function','variable','theorem'],
  emotion:['fear','joy','anger','love','grief','wonder','shame','pride','trust','desire'],
  logic:['premise','conclusion','deduction','inference','axiom','contradiction','implication','truth','valid','proof'],
  body:['hand','breath','pulse','muscle','nerve','reflex','posture','gaze','gesture','spine'],
  language:['word','grammar','syntax','metaphor','meaning','accent','tone','phrase','symbol','voice'],
  nature:['river','root','branch','seed','erosion','tide','volcano','crystal','ecosystem','decay'],
  technology:['algorithm','network','circuit','signal','data','encryption','sensor','protocol','bandwidth','processor']};
function collide(a,b){crossA=[];crossB=[];crossBridges=[];crossBridgeCount=0;
  (domW[a]||domW.music).forEach((w,i)=>{crossA.push({label:w,x:120+Math.random()*250,y:40+i*26,vx:0,vy:0});});
  (domW[b]||domW.math).forEach((w,i)=>{crossB.push({label:w,x:590+Math.random()*250,y:40+i*26,vx:0,vy:0});});
  document.getElementById('cross-bridges').textContent='0';}
function resetCollision(){crossA=[];crossB=[];crossBridges=[];crossBridgeCount=0;document.getElementById('cross-bridges').textContent='0';}
function drawCross(){const W=960,H=300;crossFrame++;crossCtx.fillStyle='#0e0e12';crossCtx.fillRect(0,0,W,H);
  if(!crossA.length){crossCtx.fillStyle='#333';crossCtx.font='13px monospace';crossCtx.textAlign='center';crossCtx.fillText('click a domain pair above',W/2,H/2);crossCtx.textAlign='left';requestAnimationFrame(drawCross);return;}
  crossA.forEach(n=>{n.vx+=0.15;n.x+=n.vx;n.vx*=0.95;});crossB.forEach(n=>{n.vx-=0.15;n.x+=n.vx;n.vx*=0.95;});
  if(crossFrame%15===0)crossA.forEach((a,ai)=>{crossB.forEach((b,bi)=>{const dx=a.x-b.x,dy=a.y-b.y;if(Math.sqrt(dx*dx+dy*dy)<80&&Math.random()<0.3&&!crossBridges.find(br=>br.a===ai&&br.b===bi)){crossBridges.push({a:ai,b:bi,age:0});crossBridgeCount++;document.getElementById('cross-bridges').textContent=crossBridgeCount;}});});
  function drawCl(nodes,col){for(let i=0;i<nodes.length;i++)for(let j=i+1;j<nodes.length;j++){const dx=nodes[i].x-nodes[j].x,dy=nodes[i].y-nodes[j].y;if(Math.sqrt(dx*dx+dy*dy)<100){crossCtx.strokeStyle=col;crossCtx.lineWidth=0.5;crossCtx.beginPath();crossCtx.moveTo(nodes[i].x,nodes[i].y);crossCtx.lineTo(nodes[j].x,nodes[j].y);crossCtx.stroke();}}
    nodes.forEach(n=>{crossCtx.fillStyle=col.replace('0.1','0.7');crossCtx.beginPath();crossCtx.arc(n.x,n.y,4,0,Math.PI*2);crossCtx.fill();crossCtx.fillStyle='#ccc';crossCtx.font='9px monospace';crossCtx.textAlign='center';crossCtx.fillText(n.label,n.x,n.y-8);crossCtx.textAlign='left';});}
  drawCl(crossA,'rgba(79,195,247,0.1)');drawCl(crossB,'rgba(255,183,77,0.1)');
  crossBridges.forEach(br=>{br.age++;const a=crossA[br.a],b=crossB[br.b];const al=Math.min(0.6,br.age*0.01);
    crossCtx.strokeStyle='rgba(129,199,132,'+al.toFixed(3)+')';crossCtx.lineWidth=1+al*2;
    crossCtx.beginPath();crossCtx.moveTo(a.x,a.y);crossCtx.lineTo(b.x,b.y);crossCtx.stroke();});
  requestAnimationFrame(drawCross);}
drawCross();

// ═══════════════════════════════════════════════════════════════════════
// 3c. Art as Filter
// ═══════════════════════════════════════════════════════════════════════
const artCanvas=document.getElementById('art-canvas'),artCtx=artCanvas.getContext('2d');
let artMode='raw';
const artData=[];for(let i=0;i<200;i++){const t=i/200;artData.push({x:t*920+20,y:130+Math.sin(t*Math.PI*4)*60+(Math.random()-0.5)*120,phase:t,val:Math.sin(t*Math.PI*4)});}
function setArtMode(m){artMode=m;}
function drawArt(){const W=960,H=260;artCtx.fillStyle='#0e0e12';artCtx.fillRect(0,0,W,H);
  let sig=0,noi=0;
  if(artMode==='raw'){artData.forEach(p=>{artCtx.fillStyle='rgba(186,104,200,0.3)';artCtx.beginPath();artCtx.arc(p.x,p.y,2,0,Math.PI*2);artCtx.fill();noi++;});}
  else if(artMode==='rhythm'){artData.forEach(p=>{const ph=(Math.sin(p.phase*Math.PI*4)+1)/2;const r=Math.round(79+ph*107),g=Math.round(195-ph*60),b=Math.round(247-ph*120);artCtx.fillStyle='rgba('+r+','+g+','+b+',0.7)';artCtx.beginPath();artCtx.arc(p.x,p.y,2+ph*3,0,Math.PI*2);artCtx.fill();sig+=ph;});
    artCtx.strokeStyle='rgba(129,199,132,0.3)';artCtx.lineWidth=1.5;artCtx.beginPath();for(let t=0;t<=1;t+=0.005){const x=t*920+20,y=130+Math.sin(t*Math.PI*4)*60;if(t===0)artCtx.moveTo(x,y);else artCtx.lineTo(x,y);}artCtx.stroke();}
  else if(artMode==='symmetry'){artData.forEach(p=>{const my=260-p.y;const sym=1-Math.abs(p.y-my)/260;artCtx.fillStyle='rgba(79,195,247,'+(0.2+sym*0.6).toFixed(3)+')';artCtx.beginPath();artCtx.arc(p.x,p.y,2+sym*3,0,Math.PI*2);artCtx.fill();artCtx.fillStyle='rgba(79,195,247,'+(sym*0.15).toFixed(3)+')';artCtx.beginPath();artCtx.arc(p.x,my,2,0,Math.PI*2);artCtx.fill();sig+=sym;});
    artCtx.strokeStyle='rgba(79,195,247,0.15)';artCtx.setLineDash([4,4]);artCtx.beginPath();artCtx.moveTo(0,130);artCtx.lineTo(960,130);artCtx.stroke();artCtx.setLineDash([]);}
  else if(artMode==='contrast'){artData.forEach(p=>{const ex=Math.abs(p.val);const al=0.05+ex*0.8;const sz=1+ex*5;artCtx.fillStyle=ex>0.5?(p.val>0?'rgba(129,199,132,'+al.toFixed(3)+')':'rgba(229,57,53,'+al.toFixed(3)+')'):'rgba(100,100,100,0.1)';
    if(ex>0.5)sig+=ex;else noi++;artCtx.beginPath();artCtx.arc(p.x,p.y,sz,0,Math.PI*2);artCtx.fill();});}
  document.getElementById('art-snr').textContent=((sig/(sig+noi||1))*100).toFixed(0)+'%';
  requestAnimationFrame(drawArt);}
drawArt();

// ═══════════════════════════════════════════════════════════════════════
// 4a. Belief Propagation
// ═══════════════════════════════════════════════════════════════════════
const beliefCanvas=document.getElementById('belief-canvas'),beliefCtx=beliefCanvas.getContext('2d');
const bN=[];const bE=[];const BNC=40;
for(let i=0;i<BNC;i++)bN.push({x:80+Math.random()*800,y:40+Math.random()*280,conformity:0.2+Math.random()*0.8,belief:0,threshold:0.3+Math.random()*0.4,isAuthority:i===0});
bN[0].x=480;bN[0].y=180;bN[0].conformity=1;
for(let i=0;i<BNC;i++)for(let j=i+1;j<BNC;j++){const dx=bN[i].x-bN[j].x,dy=bN[i].y-bN[j].y;if(Math.sqrt(dx*dx+dy*dy)<160&&Math.random()<0.5)bE.push({a:i,b:j,weight:0.3+Math.random()*0.7});}
document.getElementById('belief-total').textContent=BNC;
let beliefWave=[];
function injectBelief(){bN[0].belief=1;beliefWave=[0];}
function resetBelief(){bN.forEach(n=>{n.belief=0;});beliefWave=[];}
function drawBelief(){const W=960,H=360;beliefCtx.fillStyle='#0e0e12';beliefCtx.fillRect(0,0,W,H);
  if(beliefWave.length){const nxt=[];beliefWave.forEach(idx=>{const nd=bN[idx];bE.forEach(e=>{let nb=-1;if(e.a===idx)nb=e.b;else if(e.b===idx)nb=e.a;if(nb>=0){const n=bN[nb];n.belief=Math.min(1,n.belief+nd.belief*e.weight*n.conformity*0.15);if(n.belief>n.threshold&&!nxt.includes(nb))nxt.push(nb);}});});beliefWave=nxt;}
  bE.forEach(e=>{const a=bN[e.a],b=bN[e.b];const s=Math.min(a.belief,b.belief);
    beliefCtx.strokeStyle=s>0.1?'rgba(186,104,200,'+(0.1+s*0.4).toFixed(3)+')':'rgba(79,195,247,0.06)';
    beliefCtx.lineWidth=0.5+s*2;beliefCtx.beginPath();beliefCtx.moveTo(a.x,a.y);beliefCtx.lineTo(b.x,b.y);beliefCtx.stroke();});
  bN.forEach(n=>{const r=n.isAuthority?14:5+n.conformity*4;
    if(n.belief>n.threshold){const g=beliefCtx.createRadialGradient(n.x,n.y,0,n.x,n.y,r+20);g.addColorStop(0,'rgba(186,104,200,'+(n.belief*0.3).toFixed(3)+')');g.addColorStop(1,'rgba(186,104,200,0)');beliefCtx.fillStyle=g;beliefCtx.beginPath();beliefCtx.arc(n.x,n.y,r+20,0,Math.PI*2);beliefCtx.fill();}
    beliefCtx.fillStyle=n.isAuthority?'#ffb74d':n.belief>n.threshold?'#ba68c8':n.belief>0.05?'rgba(186,104,200,'+(0.3+n.belief*0.5).toFixed(3)+')':'rgba(79,195,247,'+(0.2+n.conformity*0.3).toFixed(3)+')';
    beliefCtx.beginPath();beliefCtx.arc(n.x,n.y,r,0,Math.PI*2);beliefCtx.fill();
    if(n.conformity<0.4&&!n.isAuthority){beliefCtx.strokeStyle='rgba(255,183,77,0.4)';beliefCtx.lineWidth=1.5;beliefCtx.beginPath();beliefCtx.arc(n.x,n.y,r+3,0,Math.PI*2);beliefCtx.stroke();}});
  document.getElementById('belief-adopted').textContent=bN.filter(n=>n.belief>n.threshold).length;
  document.getElementById('belief-resistant').textContent=bN.filter(n=>n.belief>0&&n.belief<=n.threshold).length;
  requestAnimationFrame(drawBelief);}
drawBelief();

// ═══════════════════════════════════════════════════════════════════════
// 4b. Bandwidth
// ═══════════════════════════════════════════════════════════════════════
const bwCanvas=document.getElementById('bandwidth-canvas'),bwCtx=bwCanvas.getContext('2d');
const activeStressors=new Set();const stressCosts={deadline:20,hunger:15,noise:10,conflict:25,uncertainty:15,sleep:20};
let bandwidth=1,bwFrame=0;const bwIdeas=[];
function toggleStress(btn){const s=btn.dataset.stress;if(activeStressors.has(s)){activeStressors.delete(s);btn.classList.remove('active');}else{activeStressors.add(s);btn.classList.add('active');}updateBW();}
function clearStressors(){activeStressors.clear();document.querySelectorAll('.stress').forEach(b=>b.classList.remove('active'));updateBW();}
function updateBW(){let c=0;activeStressors.forEach(s=>{c+=stressCosts[s]||10;});bandwidth=Math.max(0.05,(100-c)/100);document.getElementById('bw-val').textContent=Math.round(bandwidth*100)+'%';}
function drawBW(){const W=960,H=300;bwFrame++;bwCtx.fillStyle='#0e0e12';bwCtx.fillRect(0,0,W,H);
  if(bwFrame%8===0&&bwIdeas.length<150){const q=bandwidth;bwIdeas.push({x:80+Math.random()*800,y:40+Math.random()*230,vx:(Math.random()-0.5)*2,vy:(Math.random()-0.5)*2,size:2+q*4,coherence:q*(0.5+Math.random()*0.5),life:200+Math.random()*200,age:0});}
  for(let i=bwIdeas.length-1;i>=0;i--){const p=bwIdeas[i];p.age++;if(p.age>p.life){bwIdeas.splice(i,1);continue;}
    p.vx+=(Math.random()-0.5)*(1.5-bandwidth);p.vy+=(Math.random()-0.5)*(1.5-bandwidth);p.vx*=0.95;p.vy*=0.95;p.x+=p.vx;p.y+=p.vy;
    if(p.x<10||p.x>W-10)p.vx*=-1;if(p.y<10||p.y>H-30)p.vy*=-1;
    const fade=p.age>p.life*0.8?(p.life-p.age)/(p.life*0.2):1;const al=fade*p.coherence*0.8;
    if(al>0.02){const r=Math.round(229-p.coherence*100),g=Math.round(57+p.coherence*142),b=Math.round(53+p.coherence*79);
      bwCtx.fillStyle='rgba('+r+','+g+','+b+','+al.toFixed(3)+')';bwCtx.beginPath();bwCtx.arc(p.x,p.y,p.size,0,Math.PI*2);bwCtx.fill();}}
  // Bandwidth bar
  bwCtx.fillStyle='#1a1a2e';bwCtx.fillRect(0,H-24,W,24);
  bwCtx.fillStyle=bandwidth>0.7?'#81c784':bandwidth>0.4?'#ffb74d':'#e53935';
  bwCtx.fillRect(0,H-24,W*bandwidth,24);
  bwCtx.fillStyle='#0e0e12';bwCtx.font='9px monospace';bwCtx.fillText(Math.round(bandwidth*100)+'%',8,H-9);
  requestAnimationFrame(drawBW);}
drawBW();

// ═══════════════════════════════════════════════════════════════════════
// 5a. BCI Read
// ═══════════════════════════════════════════════════════════════════════
const bciRC=document.getElementById('bci-raw-canvas'),bciRCtx=bciRC?bciRC.getContext('2d'):null;
const bciIC=document.getElementById('bci-interp-canvas'),bciICtx=bciIC?bciIC.getContext('2d'):null;
const BCH=8,BBUF=200,bciSigs=[];
for(let ch=0;ch<BCH;ch++)bciSigs.push({data:new Float32Array(BBUF),baseFreq:8+Math.random()*30,noise:0.3+Math.random()*0.4});
let bciTime=0,bciState='idle',bciTimer=0,bciNov=0,bciCoh=0.5,bciBW=1;
const bciNovH=new Float32Array(200),bciCohH=new Float32Array(200),bciBWH=new Float32Array(200);
let bciEvents=[];
const chCol=['#e53935','#ff7043','#ffb74d','#81c784','#4fc3f7','#ba68c8','#f06292','#90a4ae'];
function bciStimulate(t){bciState=t;bciTimer=180;document.getElementById('bci-state').textContent=t;
  if(t==='encoding')bciEvents.push({type:'encode',time:bciTime,strength:1});
  if(t==='insight')bciEvents.push({type:'novelty',time:bciTime,strength:1});
  if(t==='dream')bciEvents.push({type:'dream',time:bciTime,strength:1});}
function drawBCI(){
  if(!bciRCtx||!bciICtx){requestAnimationFrame(drawBCI);return;}
  const W=460,H=320;bciTime++;
  if(bciTimer>0)bciTimer--;if(bciTimer<=0&&bciState!=='idle'){bciState='idle';document.getElementById('bci-state').textContent='idle';}
  for(let ch=0;ch<BCH;ch++){const s=bciSigs[ch];for(let i=0;i<BBUF-1;i++)s.data[i]=s.data[i+1];
    let v=Math.sin(bciTime*0.05*s.baseFreq/20)*0.3+(Math.random()-0.5)*s.noise;const f=bciTimer/180;
    if(bciState==='insight'){v+=Math.sin(bciTime*0.15)*0.5*f+Math.sin(bciTime*0.3+ch)*0.3*f;}
    else if(bciState==='stress'){v+=(Math.random()-0.5)*1.2;v*=1.5;}
    else if(bciState==='focus'){v=Math.sin(bciTime*0.06)*0.6+(Math.random()-0.5)*0.1;}
    else if(bciState==='drowsy'){v=Math.sin(bciTime*0.02+ch*0.5)*0.8+(Math.random()-0.5)*0.15;}
    else if(bciState==='encoding'){const t2=(180-bciTimer)/180;if(t2<0.1)v+=(1-t2*10)*2*(ch%3===0?1:0.3);else v+=Math.sin(t2*30+ch)*0.4*Math.exp(-t2*3);}
    else if(bciState==='dream'){
      // Dream: random bursts across channels, theta waves, suppressed amplitude
      v=Math.sin(bciTime*0.025+ch*1.5)*0.6*f; // slow theta
      v+=Math.sin(bciTime*0.2+Math.random()*ch*3)*0.4*f*(Math.random()>0.7?1:0); // random bursts
      v+=(Math.random()-0.5)*0.3;
    }
    s.data[BBUF-1]=v;}
  // Interpret
  let cc=0;for(let ch=0;ch<BCH-1;ch++)cc+=bciSigs[ch].data[BBUF-1]*bciSigs[ch+1].data[BBUF-1];
  cc=Math.abs(cc)/BCH;bciNov=bciNov*0.95+cc*0.05;
  if(bciState==='insight')bciNov=Math.min(1,bciNov+0.02);
  if(bciState==='dream')bciNov=Math.min(1,bciNov+0.01);
  const lv=bciSigs.map(s=>s.data[BBUF-1]);const mn=lv.reduce((a,b)=>a+b,0)/BCH;
  let ss=0;lv.forEach(v=>{ss+=Math.abs(v-mn);});const sync=1-Math.min(1,ss/BCH/0.8);
  bciCoh=bciCoh*0.97+sync*0.03;
  if(bciState==='focus')bciCoh=Math.min(1,bciCoh+0.01);if(bciState==='stress')bciCoh=Math.max(0,bciCoh-0.015);
  if(bciState==='dream')bciCoh=bciCoh*0.99+0.3*0.01; // dreams have moderate coherence
  const bwT=bciState==='stress'?0.3:bciState==='drowsy'?0.5:1;bciBW=bciBW*0.98+bwT*0.02;
  for(let i=0;i<199;i++){bciNovH[i]=bciNovH[i+1];bciCohH[i]=bciCohH[i+1];bciBWH[i]=bciBWH[i+1];}
  bciNovH[199]=bciNov;bciCohH[199]=bciCoh;bciBWH[199]=bciBW;
  // Draw raw
  bciRCtx.fillStyle='#0a0a10';bciRCtx.fillRect(0,0,W,H);
  const chH=H/BCH;
  for(let ch=0;ch<BCH;ch++){const s=bciSigs[ch],yB=ch*chH+chH/2;
    if(ch>0){bciRCtx.strokeStyle='#1a1a2e';bciRCtx.lineWidth=0.5;bciRCtx.beginPath();bciRCtx.moveTo(0,ch*chH);bciRCtx.lineTo(W,ch*chH);bciRCtx.stroke();}
    bciRCtx.strokeStyle=chCol[ch];bciRCtx.lineWidth=1;bciRCtx.globalAlpha=0.7;bciRCtx.beginPath();
    for(let i=0;i<BBUF;i++){const x=(i/BBUF)*W,y=yB+s.data[i]*chH*0.4;if(i===0)bciRCtx.moveTo(x,y);else bciRCtx.lineTo(x,y);}
    bciRCtx.stroke();bciRCtx.globalAlpha=1;}
  // Draw interpretation
  bciICtx.fillStyle='#0a0a10';bciICtx.fillRect(0,0,W,H);
  const stH=120;bciICtx.strokeStyle='#1a1a2e';bciICtx.lineWidth=0.5;bciICtx.strokeRect(10,10,W-20,stH);
  bciICtx.strokeStyle='#222';bciICtx.beginPath();bciICtx.moveTo(W/2,10);bciICtx.lineTo(W/2,10+stH);bciICtx.moveTo(10,10+stH/2);bciICtx.lineTo(W-10,10+stH/2);bciICtx.stroke();
  bciICtx.font='8px monospace';bciICtx.globalAlpha=0.3;
  bciICtx.fillStyle='#81c784';bciICtx.fillText('GENIUS',W-55,25);
  bciICtx.fillStyle='#e53935';bciICtx.fillText('CHAOS',15,25);
  bciICtx.fillStyle='#4fc3f7';bciICtx.fillText('ORDER',W-50,stH+5);
  bciICtx.fillStyle='#666';bciICtx.fillText('STAGNANT',15,stH+5);
  bciICtx.globalAlpha=1;
  const sx=10+bciCoh*(W-20),sy=10+(1-bciNov)*stH;
  bciICtx.fillStyle='rgba(186,104,200,0.08)';bciICtx.beginPath();bciICtx.arc(sx,sy,20,0,Math.PI*2);bciICtx.fill();
  bciICtx.fillStyle='#ba68c8';bciICtx.beginPath();bciICtx.arc(sx,sy,5,0,Math.PI*2);bciICtx.fill();
  // Time series
  const tsY=stH+35,tsH=45;
  function drawTS(data,y,col,lab){bciICtx.fillStyle='#888';bciICtx.font='9px monospace';bciICtx.fillText(lab,12,y-3);
    bciICtx.strokeStyle='#1a1a2e';bciICtx.lineWidth=0.5;bciICtx.strokeRect(10,y,W-20,tsH);
    bciICtx.strokeStyle=col;bciICtx.lineWidth=1.5;bciICtx.beginPath();
    for(let i=0;i<200;i++){const x=10+(i/200)*(W-20),py=y+tsH-Math.max(0,Math.min(1,data[i]))*tsH;if(i===0)bciICtx.moveTo(x,py);else bciICtx.lineTo(x,py);}bciICtx.stroke();
    bciICtx.fillStyle=col;bciICtx.font='bold 10px monospace';bciICtx.fillText(data[199].toFixed(2),W-40,y-3);}
  drawTS(bciNovH,tsY,'#81c784','novelty');drawTS(bciCohH,tsY+tsH+15,'#4fc3f7','coherence');drawTS(bciBWH,tsY+tsH*2+30,'#ffb74d','bandwidth');
  // Events
  for(let i=bciEvents.length-1;i>=0;i--){const ev=bciEvents[i];const age=bciTime-ev.time;if(age>120){bciEvents.splice(i,1);continue;}
    const fade=1-age/120;
    if(ev.type==='novelty'){bciICtx.fillStyle='rgba(129,199,132,'+(fade*0.8).toFixed(3)+')';bciICtx.font='bold 12px monospace';bciICtx.textAlign='center';bciICtx.fillText('INSIGHT',W/2,H-15);bciICtx.textAlign='left';}
    else if(ev.type==='encode'){bciICtx.fillStyle='rgba(186,104,200,'+(fade*0.8).toFixed(3)+')';bciICtx.font='bold 12px monospace';bciICtx.textAlign='center';bciICtx.fillText('ENCODING',W/2,H-15);bciICtx.textAlign='left';}
    else if(ev.type==='dream'){bciICtx.fillStyle='rgba(240,98,146,'+(fade*0.8).toFixed(3)+')';bciICtx.font='bold 12px monospace';bciICtx.textAlign='center';bciICtx.fillText('DREAMING',W/2,H-15);bciICtx.textAlign='left';}}
  requestAnimationFrame(drawBCI);}
drawBCI();

// ═══════════════════════════════════════════════════════════════════════
// 5b. Neural Writing
// ═══════════════════════════════════════════════════════════════════════
const nwC=document.getElementById('nw-canvas'),nwCtx=nwC?nwC.getContext('2d'):null;
const nwN=[],nwS=[];let nwSel=-1,nwPulses=[],nwFrame=0;
function nwBuild(){nwN.length=0;nwS.length=0;nwSel=-1;
  [{cx:180,cy:120,n:12,l:'sensory'},{cx:480,cy:100,n:10,l:'association'},{cx:780,cy:120,n:12,l:'motor'},
   {cx:300,cy:280,n:10,l:'memory'},{cx:660,cy:280,n:10,l:'emotional'},{cx:480,cy:200,n:8,l:'integration'}
  ].forEach(cl=>{for(let i=0;i<cl.n;i++){const a=(i/cl.n)*Math.PI*2,r=30+Math.random()*50;
    nwN.push({x:cl.cx+Math.cos(a)*r,y:cl.cy+Math.sin(a)*r,cluster:cl.l,strength:0.3+Math.random()*0.4,flash:0});}});
  for(let i=0;i<nwN.length;i++)for(let j=i+1;j<nwN.length;j++){const a=nwN[i],b=nwN[j];const dx=a.x-b.x,dy=a.y-b.y;const d=Math.sqrt(dx*dx+dy*dy);
    if(a.cluster===b.cluster&&d<100&&Math.random()<0.5)nwS.push({a:i,b:j,weight:0.3+Math.random()*0.5,directed:false});
    else if(a.cluster!==b.cluster&&d<180&&Math.random()<0.08)nwS.push({a:i,b:j,weight:0.15+Math.random()*0.3,directed:false});}
  nwUpdate();}
function nwUpdate(){document.getElementById('nw-neurons').textContent=nwN.length;document.getElementById('nw-synapses').textContent=nwS.length;}
function nwReset(){nwBuild();nwPulses=[];}
nwBuild();
function nwInject(type){
  if(nwSel<0)return;const tgt=nwN[nwSel];tgt.flash=1.5;
  if(type==='memory'){let added=0;const sh=[...nwN.keys()].sort(()=>Math.random()-0.5);
    for(const j of sh){if(j===nwSel||added>=4)break;const dx=tgt.x-nwN[j].x,dy=tgt.y-nwN[j].y;if(Math.sqrt(dx*dx+dy*dy)>200)continue;
      if(nwS.find(s=>(s.a===nwSel&&s.b===j)||(s.a===j&&s.b===nwSel)))continue;
      nwS.push({a:nwSel,b:j,weight:0.5+Math.random()*0.3,directed:false,fresh:60});nwN[j].flash=0.8;added++;}
    nwS.forEach((s,si)=>{if(s.a===nwSel||s.b===nwSel)nwPulses.push({synapse:si,t:0,speed:0.03,color:'#ba68c8',fromA:s.a===nwSel});});
    tgt.strength=Math.min(1,tgt.strength+0.2);}
  else if(type==='skill'){nwS.forEach(s=>{if(s.a===nwSel||s.b===nwSel){s.weight=Math.min(1,s.weight+0.25);s.directed=true;if(s.b===nwSel){const t=s.a;s.a=s.b;s.b=t;}s.fresh=60;}});
    const sh=[...nwN.keys()].sort(()=>Math.random()-0.5);let added=0;
    for(const j of sh){if(j===nwSel||added>=2)break;const dx=tgt.x-nwN[j].x,dy=tgt.y-nwN[j].y;if(Math.sqrt(dx*dx+dy*dy)>250)continue;nwS.push({a:nwSel,b:j,weight:0.7,directed:true,fresh:60});added++;}
    tgt.strength=Math.min(1,tgt.strength+0.3);nwS.forEach((s,si)=>{if(s.a===nwSel)nwPulses.push({synapse:si,t:0,speed:0.05,color:'#81c784',fromA:true});});}
  else if(type==='association'){let best=-1,bd=0;nwN.forEach((n,i)=>{if(i===nwSel||n.cluster===tgt.cluster)return;const dx=tgt.x-n.x,dy=tgt.y-n.y;const d=Math.sqrt(dx*dx+dy*dy);if(d>bd){bd=d;best=i;}});
    if(best>=0){nwS.push({a:nwSel,b:best,weight:0.6,directed:false,fresh:90});nwN[best].flash=1;nwPulses.push({synapse:nwS.length-1,t:0,speed:0.02,color:'#ffb74d',fromA:true});}}
  else if(type==='dream'){
    // Dream injection: fire random cascading activations through weak/unlikely paths
    tgt.flash=2;
    // Activate 5-8 random neurons across different clusters with pulsing connections
    const targets=[];const sh=[...nwN.keys()].sort(()=>Math.random()-0.5);
    for(const j of sh){if(j===nwSel||targets.length>=6)continue;
      if(nwN[j].cluster!==tgt.cluster||Math.random()<0.3){targets.push(j);nwN[j].flash=0.5+Math.random()*1;}}
    // Create temporary dream-connections (weak, pink)
    targets.forEach(j=>{nwS.push({a:nwSel,b:j,weight:0.15+Math.random()*0.2,directed:false,fresh:120,dream:true});
      nwPulses.push({synapse:nwS.length-1,t:0,speed:0.015+Math.random()*0.01,color:'#f06292',fromA:true});});
    // Chain: dream targets connect to each other
    for(let i=0;i<targets.length-1;i++){nwS.push({a:targets[i],b:targets[i+1],weight:0.1+Math.random()*0.15,directed:false,fresh:100,dream:true});
      nwPulses.push({synapse:nwS.length-1,t:0,speed:0.02,color:'#f06292',fromA:true});}}
  else if(type==='erase'){for(let i=nwS.length-1;i>=0;i--){if(nwS[i].a===nwSel||nwS[i].b===nwSel){nwS[i].weight-=0.3;if(nwS[i].weight<=0)nwS.splice(i,1);}}
    tgt.strength=Math.max(0.05,tgt.strength-0.4);tgt.flash=0;}
  nwUpdate();}
if(nwC)nwC.addEventListener('click',e=>{const r=nwC.getBoundingClientRect();const mx=e.clientX-r.left,my=e.clientY-r.top;
  let cl=-1,cd=20;nwN.forEach((n,i)=>{const dx=n.x-mx,dy=n.y-my;const d=Math.sqrt(dx*dx+dy*dy);if(d<cd){cd=d;cl=i;}});nwSel=cl;});
function drawNW(){
  if(!nwCtx){requestAnimationFrame(drawNW);return;}
  const W=960,H=380;nwFrame++;nwCtx.fillStyle='#0a0a10';nwCtx.fillRect(0,0,W,H);
  // Cluster labels
  nwCtx.font='9px monospace';nwCtx.textAlign='center';nwCtx.fillStyle='rgba(186,104,200,0.2)';
  [{l:'sensory',x:180,y:65},{l:'association',x:480,y:45},{l:'motor',x:780,y:65},{l:'memory',x:300,y:340},{l:'emotional',x:660,y:340},{l:'integration',x:480,y:250}].forEach(c=>nwCtx.fillText(c.l,c.x,c.y));
  nwCtx.textAlign='left';
  // Fade dream synapses
  for(let i=nwS.length-1;i>=0;i--){if(nwS[i].dream&&nwS[i].fresh<=0)nwS.splice(i,1);}
  // Synapses
  nwS.forEach(s=>{const a=nwN[s.a],b=nwN[s.b];const fr=s.fresh>0;if(s.fresh>0)s.fresh--;
    const al=fr?0.5+s.weight*0.5:0.05+s.weight*0.2;
    const col=s.dream?'240,98,146':fr?'129,199,132':'79,195,247';
    nwCtx.strokeStyle='rgba('+col+','+al.toFixed(3)+')';nwCtx.lineWidth=0.5+s.weight*2;
    nwCtx.beginPath();nwCtx.moveTo(a.x,a.y);nwCtx.lineTo(b.x,b.y);nwCtx.stroke();
    if(s.directed){const dx=b.x-a.x,dy=b.y-a.y;const d=Math.sqrt(dx*dx+dy*dy)||1;const ux=dx/d,uy=dy/d;
      nwCtx.fillStyle=nwCtx.strokeStyle;nwCtx.beginPath();nwCtx.moveTo(b.x-ux*10,b.y-uy*10);
      nwCtx.lineTo(b.x-ux*10-ux*6-uy*3,b.y-uy*10-uy*6+ux*3);nwCtx.lineTo(b.x-ux*10-ux*6+uy*3,b.y-uy*10-uy*6-ux*3);nwCtx.closePath();nwCtx.fill();}});
  // Pulses
  for(let i=nwPulses.length-1;i>=0;i--){const p=nwPulses[i];p.t+=p.speed;if(p.t>1){nwPulses.splice(i,1);continue;}
    const s=nwS[p.synapse];if(!s){nwPulses.splice(i,1);continue;}
    const a=nwN[p.fromA?s.a:s.b],b=nwN[p.fromA?s.b:s.a];
    const px=a.x+(b.x-a.x)*p.t,py=a.y+(b.y-a.y)*p.t;const fade=p.t<0.2?p.t/0.2:p.t>0.8?(1-p.t)/0.2:1;
    nwCtx.fillStyle=p.color;nwCtx.globalAlpha=fade*0.9;nwCtx.beginPath();nwCtx.arc(px,py,3,0,Math.PI*2);nwCtx.fill();
    nwCtx.globalAlpha=1;}
  // Neurons
  nwN.forEach((n,i)=>{if(n.flash>0)n.flash-=0.02;const r=4+n.strength*4;
    if(n.flash>0){const g=nwCtx.createRadialGradient(n.x,n.y,0,n.x,n.y,r+25*n.flash);
      g.addColorStop(0,'rgba(186,104,200,'+(n.flash*0.4).toFixed(3)+')');g.addColorStop(1,'rgba(186,104,200,0)');
      nwCtx.fillStyle=g;nwCtx.beginPath();nwCtx.arc(n.x,n.y,r+25*n.flash,0,Math.PI*2);nwCtx.fill();}
    const pulse=0.9+0.1*Math.sin(nwFrame*0.03+i);
    nwCtx.fillStyle='rgba(186,104,200,'+(0.3+n.strength*0.5*pulse).toFixed(3)+')';
    nwCtx.beginPath();nwCtx.arc(n.x,n.y,r,0,Math.PI*2);nwCtx.fill();
    // Dendrites
    const nd=3+Math.floor(n.strength*4);for(let d=0;d<nd;d++){const ang=(d/nd)*Math.PI*2+i;const len=6+n.strength*8;
      nwCtx.strokeStyle='rgba(186,104,200,'+(0.1+n.strength*0.15).toFixed(3)+')';nwCtx.lineWidth=0.5;
      nwCtx.beginPath();nwCtx.moveTo(n.x+Math.cos(ang)*r,n.y+Math.sin(ang)*r);
      nwCtx.lineTo(n.x+Math.cos(ang)*(r+len),n.y+Math.sin(ang)*(r+len));nwCtx.stroke();}
    if(i===nwSel){nwCtx.strokeStyle='#81c784';nwCtx.lineWidth=2;nwCtx.beginPath();nwCtx.arc(n.x,n.y,r+5,0,Math.PI*2);nwCtx.stroke();
      nwCtx.fillStyle='#81c784';nwCtx.font='9px monospace';nwCtx.textAlign='center';nwCtx.fillText(n.cluster,n.x,n.y+r+14);nwCtx.textAlign='left';}});
  requestAnimationFrame(drawNW);}
drawNW();

function axonaSearch(term) {
  term = term.toLowerCase().trim();
  // Remove previous highlights
  document.querySelectorAll('.axona-highlight').forEach(el => {
    el.outerHTML = el.textContent;
  });
  if (!term || term.length < 2) return;

  // Search all .info and .desc elements
  const targets = document.querySelectorAll('.info, .desc, .sub-section h3');
  let firstMatch = null;
  targets.forEach(el => {
    const text = el.textContent.toLowerCase();
    if (text.includes(term)) {
      if (!firstMatch) firstMatch = el;
      // Highlight by adding a border
      el.style.borderLeft = '3px solid var(--accent)';
      setTimeout(() => { el.style.borderLeft = ''; }, 5000);
    }
  });
  // Scroll to and show the first match's panel
  if (firstMatch) {
    const panel = firstMatch.closest('.panel');
    if (panel && !panel.classList.contains('active')) {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
      panel.classList.add('active');
      const tab = document.querySelector('[data-panel="' + panel.id + '"]');
      if (tab) tab.classList.add('active');
    }
    firstMatch.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
}

function downloadAxona() {
  const html = '<!DOCTYPE html>' + document.documentElement.outerHTML;
  const blob = new Blob([html], { type: 'text/html' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'axona-brain-cognition.html';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// ═══════════════════════════════════════════════════════════════════════
// Prediction vs Reality
// ═══════════════════════════════════════════════════════════════════════
const predCanvas = document.getElementById('pred-canvas');
const predCtx = predCanvas.getContext('2d');
const predBufLen = 240;
let predReal = new Array(predBufLen).fill(0.5);
let predFcast = new Array(predBufLen).fill(0.5);
let predSurpCount = 0, predRewCount = 0, predT = 0, predSurpPending = 0;
document.getElementById('pred-conf').addEventListener('input', (e) => {
  document.getElementById('pred-conf-val').textContent = e.target.value + '%';
});
function predSurprise() { predSurpPending = 40; }
function predReset() {
  predReal = new Array(predBufLen).fill(0.5);
  predFcast = new Array(predBufLen).fill(0.5);
  predSurpCount = 0; predRewCount = 0; predSurpPending = 0;
  document.getElementById('pred-surp-count').textContent = '0';
  document.getElementById('pred-rew-count').textContent = '0';
}
function predStep() {
  predT++;
  const slow = Math.sin(predT * 0.04) * 0.22 + Math.sin(predT * 0.013) * 0.08;
  let shock = 0;
  if (predSurpPending > 0) {
    shock = (Math.random() - 0.5) * 0.9 * Math.min(1, predSurpPending / 20);
    predSurpPending--;
  }
  const real = Math.max(0.02, Math.min(0.98, 0.5 + slow + (Math.random() - 0.5) * 0.03 + shock));
  const conf = parseInt(document.getElementById('pred-conf').value) / 100;
  const lastFc = predFcast[predFcast.length - 1];
  const gain = 1 - conf * 0.93;
  const fc = lastFc + (real - lastFc) * gain;
  predReal.push(real); predReal.shift();
  predFcast.push(fc); predFcast.shift();
  const resid = Math.abs(real - fc);
  const threshold = 0.08 + (1 - conf) * 0.06;
  if (resid > threshold) {
    predSurpCount++;
    if (Math.random() < 0.35) predRewCount++;
    document.getElementById('pred-surp-count').textContent = predSurpCount;
    document.getElementById('pred-rew-count').textContent = predRewCount;
  }
}
function drawPred() {
  predStep();
  const W = 960, H = 260;
  predCtx.fillStyle = themeBg(); predCtx.fillRect(0, 0, W, H);
  predCtx.strokeStyle = 'rgba(186,104,200,0.12)'; predCtx.lineWidth = 1;
  predCtx.setLineDash([4,4]);
  predCtx.beginPath(); predCtx.moveTo(0, H/2); predCtx.lineTo(W, H/2); predCtx.stroke();
  predCtx.setLineDash([]);
  const stepX = W / predBufLen;
  // Residual bars
  for (let i = 0; i < predBufLen; i++) {
    const r = Math.abs(predReal[i] - predFcast[i]);
    if (r < 0.05) continue;
    const bar = Math.min(H * 0.35, r * H * 1.4);
    predCtx.fillStyle = 'rgba(255,183,77,' + Math.min(0.75, r * 3).toFixed(3) + ')';
    predCtx.fillRect(i * stepX, H - bar, Math.max(1, stepX), bar);
  }
  // Forecast line
  predCtx.strokeStyle = 'rgba(186,104,200,0.85)'; predCtx.lineWidth = 2;
  predCtx.beginPath();
  for (let i = 0; i < predBufLen; i++) {
    const x = i * stepX, y = H - predFcast[i] * H;
    if (i === 0) predCtx.moveTo(x, y); else predCtx.lineTo(x, y);
  }
  predCtx.stroke();
  // Real line
  predCtx.strokeStyle = 'rgba(129,199,132,0.95)'; predCtx.lineWidth = 2;
  predCtx.beginPath();
  for (let i = 0; i < predBufLen; i++) {
    const x = i * stepX, y = H - predReal[i] * H;
    if (i === 0) predCtx.moveTo(x, y); else predCtx.lineTo(x, y);
  }
  predCtx.stroke();
  // Legend
  predCtx.font = '11px monospace'; predCtx.textAlign = 'left';
  predCtx.fillStyle = 'rgba(186,104,200,0.9)'; predCtx.fillRect(W - 150, 12, 14, 2);
  predCtx.fillStyle = '#aaa'; predCtx.fillText('forecast', W - 132, 16);
  predCtx.fillStyle = 'rgba(129,199,132,0.9)'; predCtx.fillRect(W - 150, 28, 14, 2);
  predCtx.fillStyle = '#aaa'; predCtx.fillText('reality', W - 132, 32);
  predCtx.fillStyle = 'rgba(255,183,77,0.9)'; predCtx.fillRect(W - 150, 44, 14, 2);
  predCtx.fillStyle = '#aaa'; predCtx.fillText('surprise', W - 132, 48);
  requestAnimationFrame(drawPred);
}
drawPred();

// ═══════════════════════════════════════════════════════════════════════
// Attention Spotlight
// ═══════════════════════════════════════════════════════════════════════
const attnCanvas = document.getElementById('attn-canvas');
const attnCtx = attnCanvas.getContext('2d');
const attnNodes = [], attnEdges = [];
let attnSel = -1;
function attnInit() {
  attnNodes.length = 0; attnEdges.length = 0;
  attnSel = -1;
  const W = 960, H = 360;
  for (let i = 0; i < 34; i++) {
    attnNodes.push({
      x: 60 + Math.random() * (W - 120),
      y: 40 + Math.random() * (H - 80),
      act: 0.08, base: 0.06 + Math.random() * 0.08,
    });
  }
  for (let i = 0; i < attnNodes.length; i++) {
    for (let j = i + 1; j < attnNodes.length; j++) {
      const dx = attnNodes[i].x - attnNodes[j].x, dy = attnNodes[i].y - attnNodes[j].y;
      if (Math.hypot(dx, dy) < 150) attnEdges.push({ a: i, b: j });
    }
  }
}
attnInit();
attnCanvas.addEventListener('click', (e) => {
  const r = attnCanvas.getBoundingClientRect();
  const x = (e.clientX - r.left) * (attnCanvas.width / r.width);
  const y = (e.clientY - r.top) * (attnCanvas.height / r.height);
  let best = -1, bestD = 1e9;
  for (let i = 0; i < attnNodes.length; i++) {
    const dx = attnNodes[i].x - x, dy = attnNodes[i].y - y;
    const d = dx*dx + dy*dy;
    if (d < bestD && d < 1200) { bestD = d; best = i; }
  }
  if (best >= 0) attnSel = best;
});
function attnReset() { attnInit(); }
document.getElementById('attn-bw').addEventListener('input', (e) => {
  document.getElementById('attn-bw-val').textContent = e.target.value + '%';
});
function drawAttn() {
  const W = 960, H = 360;
  attnCtx.fillStyle = themeBg(); attnCtx.fillRect(0, 0, W, H);
  const bw = parseInt(document.getElementById('attn-bw').value) / 100;
  attnNodes.forEach(n => {
    n.act *= 0.93;
    if (n.act < n.base) n.act = n.base;
  });
  if (attnSel >= 0) {
    attnNodes[attnSel].act = Math.min(1, attnNodes[attnSel].act + 0.06);
    // Spread proportional to bandwidth — breadth AND strength
    attnEdges.forEach(e => {
      if (e.a === attnSel || e.b === attnSel) {
        const other = e.a === attnSel ? e.b : e.a;
        attnNodes[other].act = Math.min(1, attnNodes[other].act + 0.02 * bw);
      }
    });
    // Drain non-selected faster when bandwidth is low
    const drain = 0.975 + 0.018 * bw;
    attnNodes.forEach((n, i) => {
      if (i !== attnSel) n.act *= drain;
    });
  }
  attnEdges.forEach(e => {
    const a = attnNodes[e.a], b = attnNodes[e.b];
    const heat = Math.max(a.act, b.act);
    attnCtx.strokeStyle = 'rgba(186,104,200,' + (0.03 + heat * 0.35).toFixed(3) + ')';
    attnCtx.lineWidth = 0.5 + heat * 1.2;
    attnCtx.beginPath(); attnCtx.moveTo(a.x, a.y); attnCtx.lineTo(b.x, b.y); attnCtx.stroke();
  });
  attnNodes.forEach((n, i) => {
    const r = 4 + n.act * 11;
    const col = i === attnSel ? '129,199,132' : '186,104,200';
    attnCtx.fillStyle = 'rgba(' + col + ',' + (0.3 + n.act * 0.7).toFixed(3) + ')';
    attnCtx.beginPath(); attnCtx.arc(n.x, n.y, r, 0, Math.PI*2); attnCtx.fill();
    if (i === attnSel) {
      attnCtx.strokeStyle = 'rgba(129,199,132,0.95)';
      attnCtx.lineWidth = 2; attnCtx.stroke();
    }
  });
  // Spotlight halo around selection, radius shrinks with low bandwidth
  if (attnSel >= 0) {
    const n = attnNodes[attnSel];
    const halo = 30 + bw * 90;
    const grad = attnCtx.createRadialGradient(n.x, n.y, 0, n.x, n.y, halo);
    grad.addColorStop(0, 'rgba(129,199,132,0.18)');
    grad.addColorStop(1, 'rgba(129,199,132,0)');
    attnCtx.fillStyle = grad;
    attnCtx.beginPath(); attnCtx.arc(n.x, n.y, halo, 0, Math.PI*2); attnCtx.fill();
  }
  requestAnimationFrame(drawAttn);
}
drawAttn();

// ═══════════════════════════════════════════════════════════════════════
// Sleep & Consolidation
// ═══════════════════════════════════════════════════════════════════════
const sleepCanvas = document.getElementById('sleep-canvas');
const sleepCtx = sleepCanvas.getContext('2d');
const sleepNodes = [], sleepEdges = [];
let sleepDays = 0, sleepPruned = 0, sleepLocked = 0, sleepMode = 'day', sleepTimer = 0;
function sleepRefreshCounts() {
  document.getElementById('sleep-days').textContent = sleepDays;
  document.getElementById('sleep-pruned').textContent = sleepPruned;
  document.getElementById('sleep-locked').textContent = sleepLocked;
}
function sleepInit() {
  sleepNodes.length = 0; sleepEdges.length = 0;
  sleepDays = 0; sleepPruned = 0; sleepLocked = 0; sleepMode = 'day'; sleepTimer = 0;
  sleepRefreshCounts();
}
sleepInit();
function sleepAddDay() {
  const W = 960, H = 380;
  const count = 12 + Math.floor(Math.random() * 6);
  const firstNew = sleepNodes.length;
  for (let i = 0; i < count; i++) {
    sleepNodes.push({
      x: 60 + Math.random() * (W - 120),
      y: 40 + Math.random() * (H - 80),
      emotion: Math.random() < 0.18 ? 0.72 + Math.random() * 0.28 : 0.1 + Math.random() * 0.28,
      locked: false,
    });
  }
  for (let i = firstNew; i < sleepNodes.length; i++) {
    for (let j = 0; j < i; j++) {
      const dx = sleepNodes[i].x - sleepNodes[j].x, dy = sleepNodes[i].y - sleepNodes[j].y;
      if (Math.hypot(dx, dy) < 130 && Math.random() < 0.4) {
        sleepEdges.push({ a: i, b: j, w: 0.15 + Math.random() * 0.45 });
      }
    }
  }
  sleepDays++;
  sleepRefreshCounts();
}
function sleepNight() { sleepMode = 'night'; sleepTimer = 150; }
function sleepReset() { sleepInit(); }
document.getElementById('sleep-rem').addEventListener('input', (e) => {
  document.getElementById('sleep-rem-val').textContent = e.target.value + '%';
});
function sleepConsolidate() {
  const rem = parseInt(document.getElementById('sleep-rem').value) / 100;
  const pruneRate = (1 - rem) * 0.06;
  for (let i = sleepEdges.length - 1; i >= 0; i--) {
    const e = sleepEdges[i];
    if (!sleepNodes[e.a] || !sleepNodes[e.b]) { sleepEdges.splice(i, 1); continue; }
    const emoBoost = Math.max(sleepNodes[e.a].emotion, sleepNodes[e.b].emotion);
    if (emoBoost > 0.6) {
      e.w = Math.min(1, e.w + 0.018);
    } else {
      e.w -= pruneRate * (0.55 - emoBoost * 0.5);
    }
    if (e.w < 0.06 && Math.random() < 0.25) {
      sleepEdges.splice(i, 1); sleepPruned++;
    } else if (e.w > 0.88 && !sleepNodes[e.a].locked) {
      sleepNodes[e.a].locked = true;
      sleepLocked++;
    }
  }
  if (Math.random() < rem * 0.35 && sleepNodes.length > 3) {
    const a = Math.floor(Math.random() * sleepNodes.length);
    const b = Math.floor(Math.random() * sleepNodes.length);
    if (a !== b) sleepEdges.push({ a, b, w: 0.22 + Math.random() * 0.28 });
  }
  sleepRefreshCounts();
}
function drawSleep() {
  const W = 960, H = 380;
  const bgCol = sleepMode === 'night' ? '#080814' : '#0e0e12';
  sleepCtx.fillStyle = bgCol; sleepCtx.fillRect(0, 0, W, H);
  if (sleepMode === 'night') {
    if (sleepTimer > 0) {
      sleepTimer--;
      if (sleepTimer % 3 === 0) sleepConsolidate();
      if (sleepTimer === 0) sleepMode = 'day';
    }
    sleepCtx.fillStyle = 'rgba(255,255,255,0.05)';
    for (let i = 0; i < 40; i++) {
      sleepCtx.fillRect((i * 137) % W, (i * 83) % H, 1, 1);
    }
  }
  sleepEdges.forEach(e => {
    const a = sleepNodes[e.a], b = sleepNodes[e.b];
    if (!a || !b) return;
    sleepCtx.strokeStyle = 'rgba(186,104,200,' + (e.w * 0.65).toFixed(3) + ')';
    sleepCtx.lineWidth = 0.5 + e.w * 1.5;
    sleepCtx.beginPath(); sleepCtx.moveTo(a.x, a.y); sleepCtx.lineTo(b.x, b.y); sleepCtx.stroke();
  });
  sleepNodes.forEach(n => {
    const r = 3 + n.emotion * 6;
    const col = n.locked ? '129,199,132' : (n.emotion > 0.6 ? '255,183,77' : '186,104,200');
    sleepCtx.fillStyle = 'rgba(' + col + ',' + (0.45 + n.emotion * 0.5).toFixed(3) + ')';
    sleepCtx.beginPath(); sleepCtx.arc(n.x, n.y, r, 0, Math.PI*2); sleepCtx.fill();
    if (n.locked) {
      sleepCtx.strokeStyle = 'rgba(129,199,132,0.85)';
      sleepCtx.lineWidth = 1; sleepCtx.stroke();
    }
  });
  if (sleepMode === 'night') {
    sleepCtx.fillStyle = 'rgba(79,195,247,0.85)'; sleepCtx.font = '12px monospace';
    sleepCtx.textAlign = 'left';
    sleepCtx.fillText('◐ consolidating…', 20, 24);
  }
  requestAnimationFrame(drawSleep);
}
drawSleep();

// ═══════════════════════════════════════════════════════════════════════
// Trauma Loops & Therapy
// ═══════════════════════════════════════════════════════════════════════
const traumaCanvas = document.getElementById('trauma-canvas');
const traumaCtx = traumaCanvas.getContext('2d');
const traumaNodes = [], traumaEdges = [], traumaPulses = [];
let traumaCaps = 0, traumaEsc = 0, traumaLinks = 0;
function traumaUpdateCounts() {
  document.getElementById('trauma-caps').textContent = traumaCaps;
  document.getElementById('trauma-esc').textContent = traumaEsc;
  document.getElementById('trauma-links').textContent = traumaLinks;
}
function traumaInit() {
  traumaNodes.length = 0; traumaEdges.length = 0; traumaPulses.length = 0;
  traumaCaps = 0; traumaEsc = 0; traumaLinks = 0;
  const W = 960, H = 380;
  const cx = 280, cy = H / 2, rr = 95;
  const loopIds = [];
  for (let i = 0; i < 6; i++) {
    const a = (i / 6) * Math.PI * 2 - Math.PI / 2;
    traumaNodes.push({
      x: cx + Math.cos(a) * rr,
      y: cy + Math.sin(a) * rr,
      act: 0, loop: true,
    });
    loopIds.push(traumaNodes.length - 1);
  }
  for (let i = 0; i < 6; i++) {
    traumaEdges.push({ a: loopIds[i], b: loopIds[(i + 1) % 6], w: 0.96, therapy: false });
  }
  for (let i = 0; i < 22; i++) {
    traumaNodes.push({
      x: 500 + Math.random() * (W - 560),
      y: 40 + Math.random() * (H - 80),
      act: 0, loop: false,
    });
  }
  for (let i = 6; i < traumaNodes.length; i++) {
    for (let j = i + 1; j < traumaNodes.length; j++) {
      const a = traumaNodes[i], b = traumaNodes[j];
      if (Math.hypot(a.x - b.x, a.y - b.y) < 130 && Math.random() < 0.35) {
        traumaEdges.push({ a: i, b: j, w: 0.32, therapy: false });
      }
    }
  }
  // A faint bridge from the outside cluster to the trauma loop (so there's a route to get captured)
  traumaEdges.push({ a: 6, b: 0, w: 0.18, therapy: false });
  traumaUpdateCounts();
}
traumaInit();
function traumaActivate() {
  const outside = [];
  for (let i = 0; i < traumaNodes.length; i++) if (!traumaNodes[i].loop) outside.push(i);
  if (!outside.length) return;
  const start = outside[Math.floor(Math.random() * outside.length)];
  traumaNodes[start].act = 1;
  traumaPulses.push({ node: start, energy: 1.3, steps: 0, captured: false, escaped: false });
}
function traumaTherapy() {
  const loopIds = [], outIds = [];
  traumaNodes.forEach((n, i) => (n.loop ? loopIds : outIds).push(i));
  if (!loopIds.length || !outIds.length) return;
  const a = loopIds[Math.floor(Math.random() * loopIds.length)];
  const b = outIds[Math.floor(Math.random() * outIds.length)];
  traumaEdges.push({ a, b, w: 0.7, therapy: true });
  // Each therapy session slightly weakens the loop
  traumaEdges.forEach(e => {
    if (traumaNodes[e.a].loop && traumaNodes[e.b].loop && !e.therapy) {
      e.w = Math.max(0.35, e.w - 0.06);
    }
  });
  traumaLinks++;
  traumaUpdateCounts();
}
function traumaReset() { traumaInit(); }
function drawTrauma() {
  const W = 960, H = 380;
  traumaCtx.fillStyle = themeBg(); traumaCtx.fillRect(0, 0, W, H);
  traumaNodes.forEach(n => { n.act *= 0.93; });
  // Pulse walks
  for (let p of traumaPulses) {
    if (p.escaped || p.energy <= 0) continue;
    const candidates = [];
    traumaEdges.forEach(e => {
      if (e.a === p.node) candidates.push({ to: e.b, w: e.w });
      else if (e.b === p.node) candidates.push({ to: e.a, w: e.w });
    });
    if (!candidates.length) { p.energy = 0; continue; }
    let total = 0; candidates.forEach(c => total += c.w);
    let r = Math.random() * total, chosen = candidates[0];
    for (let c of candidates) { r -= c.w; if (r <= 0) { chosen = c; break; } }
    p.node = chosen.to;
    p.steps++;
    traumaNodes[p.node].act = Math.min(1, traumaNodes[p.node].act + 0.7);
    if (traumaNodes[p.node].loop) {
      if (!p.captured) { p.captured = true; traumaCaps++; traumaUpdateCounts(); }
    } else if (p.captured) {
      p.escaped = true; traumaEsc++; traumaUpdateCounts();
    }
    p.energy -= 0.05;
  }
  for (let i = traumaPulses.length - 1; i >= 0; i--) {
    if (traumaPulses[i].escaped || traumaPulses[i].energy <= 0) traumaPulses.splice(i, 1);
  }
  traumaEdges.forEach(e => {
    const a = traumaNodes[e.a], b = traumaNodes[e.b];
    const col = e.therapy ? '129,199,132' : (a.loop && b.loop ? '229,57,53' : '186,104,200');
    traumaCtx.strokeStyle = 'rgba(' + col + ',' + (0.2 + e.w * 0.55).toFixed(3) + ')';
    traumaCtx.lineWidth = 0.5 + e.w * 2;
    traumaCtx.beginPath(); traumaCtx.moveTo(a.x, a.y); traumaCtx.lineTo(b.x, b.y); traumaCtx.stroke();
  });
  traumaNodes.forEach(n => {
    const r = 4 + n.act * 8;
    const col = n.loop ? '229,57,53' : '186,104,200';
    traumaCtx.fillStyle = 'rgba(' + col + ',' + (0.4 + n.act * 0.6).toFixed(3) + ')';
    traumaCtx.beginPath(); traumaCtx.arc(n.x, n.y, r, 0, Math.PI*2); traumaCtx.fill();
  });
  traumaCtx.font = '11px monospace'; traumaCtx.textAlign = 'left';
  traumaCtx.fillStyle = 'rgba(229,57,53,0.85)'; traumaCtx.fillText('TRAUMA LOOP', 230, 32);
  traumaCtx.fillStyle = 'rgba(186,104,200,0.85)'; traumaCtx.fillText('UNRELATED NETWORK', 600, 32);
  requestAnimationFrame(drawTrauma);
}
drawTrauma();

// ═══════════════════════════════════════════════════════════════════════
// Bidirectionality Map
// ═══════════════════════════════════════════════════════════════════════
const bidirCanvas = document.getElementById('bidir-canvas');
const bidirCtx = bidirCanvas.getContext('2d');
const bidirPairs = [
  { key: 'smile',  from: 'happy',    to: 'smile',  returnPath: true,  y: 60,  pulses: [], label: 'facial proprioception (sensor present)' },
  { key: 'wag',    from: 'positive', to: 'wag',    returnPath: true,  y: 130, pulses: [], label: 'tail proprioception (sensor present)' },
  { key: 'pupil',  from: 'light',    to: 'pupil',  returnPath: false, y: 200, pulses: [], label: 'no iris proprioceptor — pure actuator' },
  { key: 'digest', from: 'food',     to: 'digest', returnPath: false, y: 270, pulses: [], label: 'no interoceptor — autonomic only' },
];
function bidirPulse(key) {
  const p = bidirPairs.find(x => x.key === key);
  if (p) p.pulses.push({ t: 0 });
}
document.getElementById('bidir-loops').textContent = bidirPairs.filter(p => p.returnPath).length;
function drawBidir() {
  const W = 960, H = 340;
  bidirCtx.fillStyle = themeBg(); bidirCtx.fillRect(0, 0, W, H);
  bidirCtx.font = '12px monospace';
  const x1 = 140, x2 = 640;
  bidirPairs.forEach(p => {
    // Forward wire
    bidirCtx.strokeStyle = 'rgba(186,104,200,0.4)'; bidirCtx.lineWidth = 2;
    bidirCtx.beginPath(); bidirCtx.moveTo(x1 + 18, p.y); bidirCtx.lineTo(x2 - 18, p.y); bidirCtx.stroke();
    // Forward arrow
    bidirCtx.fillStyle = 'rgba(186,104,200,0.7)';
    bidirCtx.beginPath();
    bidirCtx.moveTo(x2 - 18, p.y); bidirCtx.lineTo(x2 - 26, p.y - 4); bidirCtx.lineTo(x2 - 26, p.y + 4);
    bidirCtx.closePath(); bidirCtx.fill();
    // Return wire
    if (p.returnPath) {
      bidirCtx.strokeStyle = 'rgba(129,199,132,0.55)'; bidirCtx.lineWidth = 2;
      bidirCtx.setLineDash([5,4]);
      bidirCtx.beginPath(); bidirCtx.moveTo(x2 - 18, p.y + 10); bidirCtx.lineTo(x1 + 18, p.y + 10); bidirCtx.stroke();
      bidirCtx.setLineDash([]);
      bidirCtx.fillStyle = 'rgba(129,199,132,0.8)';
      bidirCtx.beginPath();
      bidirCtx.moveTo(x1 + 18, p.y + 10); bidirCtx.lineTo(x1 + 26, p.y + 6); bidirCtx.lineTo(x1 + 26, p.y + 14);
      bidirCtx.closePath(); bidirCtx.fill();
    } else {
      // Red blocker marker showing no return
      bidirCtx.strokeStyle = 'rgba(229,57,53,0.5)'; bidirCtx.lineWidth = 1;
      bidirCtx.setLineDash([3,3]);
      bidirCtx.beginPath(); bidirCtx.moveTo(x2 - 18, p.y + 10); bidirCtx.lineTo(x1 + 18, p.y + 10); bidirCtx.stroke();
      bidirCtx.setLineDash([]);
      bidirCtx.strokeStyle = 'rgba(229,57,53,0.85)'; bidirCtx.lineWidth = 2;
      bidirCtx.beginPath(); bidirCtx.moveTo((x1+x2)/2 - 6, p.y + 4); bidirCtx.lineTo((x1+x2)/2 + 6, p.y + 16); bidirCtx.stroke();
      bidirCtx.beginPath(); bidirCtx.moveTo((x1+x2)/2 + 6, p.y + 4); bidirCtx.lineTo((x1+x2)/2 - 6, p.y + 16); bidirCtx.stroke();
    }
    // Nodes
    bidirCtx.fillStyle = 'rgba(186,104,200,0.55)';
    bidirCtx.beginPath(); bidirCtx.arc(x1, p.y, 18, 0, Math.PI*2); bidirCtx.fill();
    bidirCtx.strokeStyle = 'rgba(186,104,200,0.9)'; bidirCtx.lineWidth = 1.5; bidirCtx.stroke();
    bidirCtx.beginPath(); bidirCtx.arc(x2, p.y, 18, 0, Math.PI*2); bidirCtx.fill();
    bidirCtx.stroke();
    bidirCtx.fillStyle = '#e0e0e0'; bidirCtx.textAlign = 'center';
    bidirCtx.fillText(p.from, x1, p.y + 4);
    bidirCtx.fillText(p.to, x2, p.y + 4);
    // Label
    bidirCtx.textAlign = 'left';
    bidirCtx.fillStyle = p.returnPath ? 'rgba(129,199,132,0.9)' : 'rgba(229,57,53,0.85)';
    bidirCtx.fillText(p.label, x2 + 40, p.y + 4);
    // Pulses
    p.pulses = p.pulses.filter(pu => pu.t < 2.2);
    p.pulses.forEach(pu => {
      pu.t += 0.012;
      let px, py;
      if (pu.t <= 1) {
        px = x1 + 18 + (x2 - 36 - x1) * pu.t;
        py = p.y;
      } else if (p.returnPath && pu.t <= 2) {
        const k = pu.t - 1;
        px = x2 - 18 - (x2 - 36 - x1) * k;
        py = p.y + 10;
      } else if (!p.returnPath) {
        return; // pulse dies at the wall
      } else {
        return;
      }
      bidirCtx.fillStyle = 'rgba(255,255,255,0.9)';
      bidirCtx.beginPath(); bidirCtx.arc(px, py, 4, 0, Math.PI*2); bidirCtx.fill();
    });
    // Self-sustaining loop: if return trip finishes, emit another pulse (bidirectional loop)
    if (p.returnPath) {
      for (let i = p.pulses.length - 1; i >= 0; i--) {
        if (p.pulses[i].t > 1.95 && p.pulses[i].t < 2.05 && Math.random() < 0.4) {
          p.pulses.push({ t: 0 });
          break;
        }
      }
    }
  });
  requestAnimationFrame(drawBidir);
}
drawBidir();

// ═══════════════════════════════════════════════════════════════════════
// Creativity Under Constraint
// ═══════════════════════════════════════════════════════════════════════
const constrCanvas = document.getElementById('constr-canvas');
const constrCtx = constrCanvas.getContext('2d');
const constrNodes = [], constrEdges = [];
let constrMode = 'free', constrBridges = 0, constrNoise = 0;
function constrInit() {
  constrNodes.length = 0; constrEdges.length = 0;
  constrMode = 'free'; constrBridges = 0; constrNoise = 0;
  document.getElementById('constr-mode').textContent = 'free';
  document.getElementById('constr-mode').style.color = 'var(--accent)';
  document.getElementById('constr-bridges').textContent = '0';
  document.getElementById('constr-noise').textContent = '0';
}
constrInit();
function constrToggle() {
  constrMode = constrMode === 'free' ? 'constrained' : 'free';
  document.getElementById('constr-mode').textContent = constrMode;
  document.getElementById('constr-mode').style.color = constrMode === 'constrained' ? 'var(--accent2)' : 'var(--accent)';
}
function constrExpand() {
  const W = 960, H = 340;
  const count = 6;
  for (let k = 0; k < count; k++) {
    let x, y;
    if (constrMode === 'constrained') {
      x = 120 + Math.random() * (W - 240);
      y = H/2 - 55 + Math.random() * 110;
    } else {
      x = 20 + Math.random() * (W - 40);
      y = 20 + Math.random() * (H - 40);
    }
    constrNodes.push({ x, y, life: 1 });
    const idx = constrNodes.length - 1;
    let best = -1, bestD = 1e9;
    for (let i = 0; i < idx; i++) {
      const d = Math.hypot(constrNodes[i].x - x, constrNodes[i].y - y);
      if (d < bestD) { bestD = d; best = i; }
    }
    if (best >= 0 && bestD < 95) {
      constrEdges.push({ a: best, b: idx });
      constrBridges++;
    } else {
      constrNoise++;
    }
  }
  if (constrNodes.length > 140) {
    const drop = constrNodes.length - 140;
    constrNodes.splice(0, drop);
    constrEdges.length = 0;
    // Rebuild edges within proximity
    for (let i = 0; i < constrNodes.length; i++) {
      for (let j = i + 1; j < constrNodes.length; j++) {
        const d = Math.hypot(constrNodes[i].x - constrNodes[j].x, constrNodes[i].y - constrNodes[j].y);
        if (d < 95) constrEdges.push({ a: i, b: j });
      }
    }
  }
  document.getElementById('constr-bridges').textContent = constrBridges;
  document.getElementById('constr-noise').textContent = constrNoise;
}
function constrReset() { constrInit(); }
function drawConstr() {
  const W = 960, H = 340;
  constrCtx.fillStyle = themeBg(); constrCtx.fillRect(0, 0, W, H);
  if (constrMode === 'constrained') {
    const grad = constrCtx.createLinearGradient(0, H/2 - 55, 0, H/2 + 55);
    grad.addColorStop(0, 'rgba(129,199,132,0)');
    grad.addColorStop(0.5, 'rgba(129,199,132,0.09)');
    grad.addColorStop(1, 'rgba(129,199,132,0)');
    constrCtx.fillStyle = grad;
    constrCtx.fillRect(0, H/2 - 55, W, 110);
    constrCtx.strokeStyle = 'rgba(129,199,132,0.35)'; constrCtx.lineWidth = 1;
    constrCtx.setLineDash([4,4]);
    constrCtx.beginPath(); constrCtx.moveTo(0, H/2 - 55); constrCtx.lineTo(W, H/2 - 55); constrCtx.stroke();
    constrCtx.beginPath(); constrCtx.moveTo(0, H/2 + 55); constrCtx.lineTo(W, H/2 + 55); constrCtx.stroke();
    constrCtx.setLineDash([]);
    constrCtx.fillStyle = 'rgba(129,199,132,0.7)'; constrCtx.font = '11px monospace';
    constrCtx.textAlign = 'left';
    constrCtx.fillText('CONSTRAINT: ideas must live inside this band', 20, H/2 - 62);
  }
  constrEdges.forEach(e => {
    const a = constrNodes[e.a], b = constrNodes[e.b];
    if (!a || !b) return;
    constrCtx.strokeStyle = 'rgba(129,199,132,0.4)';
    constrCtx.lineWidth = 0.8;
    constrCtx.beginPath(); constrCtx.moveTo(a.x, a.y); constrCtx.lineTo(b.x, b.y); constrCtx.stroke();
  });
  constrNodes.forEach(n => {
    n.life *= 0.998;
    constrCtx.fillStyle = 'rgba(186,104,200,' + (n.life * 0.85).toFixed(3) + ')';
    constrCtx.beginPath(); constrCtx.arc(n.x, n.y, 3, 0, Math.PI*2); constrCtx.fill();
  });
  requestAnimationFrame(drawConstr);
}
drawConstr();

// ═══════════════════════════════════════════════════════════════════════
// Time Perception
// ═══════════════════════════════════════════════════════════════════════
const timeCanvas = document.getElementById('time-canvas');
const timeCtx = timeCanvas.getContext('2d');
let timeWall = 0, timeSubj = 0, timeFrame = 0;
const timeEncodings = [];
document.getElementById('time-nov').addEventListener('input', (e) => {
  document.getElementById('time-nov-val').textContent = e.target.value + '%';
});
function drawTime() {
  const W = 960, H = 280;
  timeCtx.fillStyle = themeBg(); timeCtx.fillRect(0, 0, W, H);
  timeFrame++;
  const nov = parseInt(document.getElementById('time-nov').value) / 100;
  if (timeFrame % 6 === 0) {
    timeWall++;
    timeSubj += 0.2 + nov * 2.2;
    document.getElementById('time-wall').textContent = timeWall;
    document.getElementById('time-subj').textContent = timeSubj.toFixed(1);
    if (Math.random() < nov) {
      timeEncodings.push({ x: 40 + Math.random() * (W - 80), y: 110 + Math.random() * 50, life: 1 });
    }
  }
  timeCtx.font = '11px monospace'; timeCtx.textAlign = 'left'; timeCtx.fillStyle = '#888';
  timeCtx.fillText('wall clock (constant)', 40, 22);
  timeCtx.fillStyle = '#16213e'; timeCtx.fillRect(40, 30, W - 80, 18);
  const clockFill = (timeWall % 60) / 60;
  timeCtx.fillStyle = 'rgba(186,104,200,0.75)';
  timeCtx.fillRect(40, 30, (W - 80) * clockFill, 18);
  timeCtx.fillStyle = '#888'; timeCtx.fillText('encoding density (= memory formed per tick)', 40, 96);
  timeEncodings.forEach(e => {
    e.life *= 0.997;
    timeCtx.fillStyle = 'rgba(129,199,132,' + (e.life * 0.85).toFixed(3) + ')';
    timeCtx.beginPath(); timeCtx.arc(e.x, e.y, 3, 0, Math.PI*2); timeCtx.fill();
  });
  if (timeEncodings.length > 400) timeEncodings.splice(0, timeEncodings.length - 400);
  timeCtx.fillStyle = '#888';
  timeCtx.fillText('subjective time (scales with novelty × wall clock)', 40, 208);
  timeCtx.fillStyle = '#16213e'; timeCtx.fillRect(40, 216, W - 80, 18);
  const subjFill = (timeSubj % 120) / 120;
  timeCtx.fillStyle = 'rgba(129,199,132,0.85)';
  timeCtx.fillRect(40, 216, (W - 80) * subjFill, 18);
  // Ratio readout
  const ratio = timeWall > 0 ? (timeSubj / timeWall).toFixed(2) : '—';
  timeCtx.fillStyle = '#aaa'; timeCtx.textAlign = 'right';
  timeCtx.fillText('subjective / wall = ' + ratio + '×', W - 40, 260);
  requestAnimationFrame(drawTime);
}
drawTime();

// ═══════════════════════════════════════════════════════════════════════
// Mind Wandering
// ═══════════════════════════════════════════════════════════════════════
const wanderCanvas = document.getElementById('wander-canvas');
const wanderCtx = wanderCanvas.getContext('2d');
const wanderNodes = [], wanderEdges = [];
let wanderMode = 'focused', wanderBridges = 0, wanderFocal = -1, wanderFrame = 0;
function wanderInit() {
  wanderNodes.length = 0; wanderEdges.length = 0;
  wanderMode = 'focused'; wanderBridges = 0; wanderFocal = -1; wanderFrame = 0;
  const W = 960, H = 320;
  const centers = [[200, 160], [480, 160], [760, 160]];
  centers.forEach((c, k) => {
    for (let i = 0; i < 11; i++) {
      wanderNodes.push({
        x: c[0] + (Math.random() - 0.5) * 110,
        y: c[1] + (Math.random() - 0.5) * 110,
        cluster: k, act: 0.18,
      });
    }
  });
  for (let i = 0; i < wanderNodes.length; i++) {
    for (let j = i + 1; j < wanderNodes.length; j++) {
      if (wanderNodes[i].cluster === wanderNodes[j].cluster) {
        const d = Math.hypot(wanderNodes[i].x - wanderNodes[j].x, wanderNodes[i].y - wanderNodes[j].y);
        if (d < 72) wanderEdges.push({ a: i, b: j, cross: false });
      }
    }
  }
  document.getElementById('wander-mode').textContent = 'focused';
  document.getElementById('wander-mode').style.color = 'var(--accent)';
  document.getElementById('wander-bridges').textContent = '0';
}
wanderInit();
function wanderRelease() {
  wanderMode = 'wandering';
  document.getElementById('wander-mode').textContent = 'wandering';
  document.getElementById('wander-mode').style.color = 'var(--accent2)';
}
function wanderFocus() {
  wanderMode = 'focused';
  document.getElementById('wander-mode').textContent = 'focused';
  document.getElementById('wander-mode').style.color = 'var(--accent)';
}
function wanderReset() { wanderInit(); }
function drawWander() {
  const W = 960, H = 320;
  wanderCtx.fillStyle = themeBg(); wanderCtx.fillRect(0, 0, W, H);
  wanderFrame++;
  if (wanderMode === 'focused') {
    if (wanderFocal < 0 || wanderFrame % 200 === 0) {
      wanderFocal = Math.floor(Math.random() * 11);
    }
    wanderNodes.forEach((n, i) => {
      if (n.cluster === 0 && i === wanderFocal) n.act = 1;
      else if (n.cluster === 0) n.act = Math.min(0.75, n.act + 0.015);
      else n.act *= 0.95;
    });
  } else {
    wanderNodes.forEach(n => {
      n.act *= 0.94;
      n.act += Math.random() * 0.06;
    });
    if (Math.random() < 0.05) {
      const a = Math.floor(Math.random() * wanderNodes.length);
      let b = Math.floor(Math.random() * wanderNodes.length);
      let tries = 0;
      while (wanderNodes[b].cluster === wanderNodes[a].cluster && tries < 15) {
        b = Math.floor(Math.random() * wanderNodes.length); tries++;
      }
      if (wanderNodes[a].cluster !== wanderNodes[b].cluster) {
        wanderEdges.push({ a, b, cross: true, life: 1 });
        wanderBridges++;
        document.getElementById('wander-bridges').textContent = wanderBridges;
      }
    }
  }
  wanderEdges.forEach(e => {
    const a = wanderNodes[e.a], b = wanderNodes[e.b];
    if (!a || !b) return;
    const heat = Math.max(a.act, b.act);
    const col = e.cross ? '129,199,132' : '186,104,200';
    const alpha = e.cross ? 0.55 : (0.08 + heat * 0.35);
    wanderCtx.strokeStyle = 'rgba(' + col + ',' + alpha.toFixed(3) + ')';
    wanderCtx.lineWidth = e.cross ? 1.3 : 0.5;
    wanderCtx.beginPath(); wanderCtx.moveTo(a.x, a.y); wanderCtx.lineTo(b.x, b.y); wanderCtx.stroke();
  });
  wanderNodes.forEach((n, i) => {
    const r = 3 + n.act * 8;
    const col = (i === wanderFocal && wanderMode === 'focused') ? '129,199,132' : '186,104,200';
    wanderCtx.fillStyle = 'rgba(' + col + ',' + (0.3 + n.act * 0.65).toFixed(3) + ')';
    wanderCtx.beginPath(); wanderCtx.arc(n.x, n.y, r, 0, Math.PI*2); wanderCtx.fill();
  });
  wanderCtx.font = '11px monospace'; wanderCtx.fillStyle = 'rgba(186,104,200,0.55)';
  wanderCtx.textAlign = 'center';
  wanderCtx.fillText('cluster A', 200, 260);
  wanderCtx.fillText('cluster B', 480, 260);
  wanderCtx.fillText('cluster C', 760, 260);
  requestAnimationFrame(drawWander);
}
drawWander();

// ═══════════════════════════════════════════════════════════════════════
// Pygmalion Effect
// ═══════════════════════════════════════════════════════════════════════
const pygCanvas = document.getElementById('pyg-canvas');
const pygCtx = pygCanvas.getContext('2d');
let pygExpect = 0, pygConf = 0.5, pygPerf = 0.5;
const pygHistory = [];
function pygSet(v) { pygExpect = v; }
function pygReset() { pygExpect = 0; pygConf = 0.5; pygPerf = 0.5; pygHistory.length = 0; }
function drawPyg() {
  const W = 960, H = 320;
  pygCtx.fillStyle = themeBg(); pygCtx.fillRect(0, 0, W, H);
  // Update
  const target = 0.5 + pygExpect * 0.42;
  pygConf += (target - pygConf) * 0.022;
  const noise = (Math.random() - 0.5) * 0.035;
  pygPerf += (pygConf - pygPerf) * 0.04 + noise;
  pygPerf = Math.max(0, Math.min(1, pygPerf));
  pygHistory.push({ expect: target, conf: pygConf, perf: pygPerf });
  if (pygHistory.length > 400) pygHistory.shift();
  document.getElementById('pyg-conf').textContent = pygConf.toFixed(2);
  document.getElementById('pyg-perf').textContent = pygPerf.toFixed(2);
  // Left: three-node network
  const teacherVal = target;
  const nodes = [
    { x: 110, y: 90,  label: 'teacher',     col: '255,183,77', val: teacherVal },
    { x: 110, y: 230, label: 'student',     col: '186,104,200', val: pygConf },
    { x: 290, y: 160, label: 'performance', col: '129,199,132', val: pygPerf },
  ];
  // Arrows
  pygCtx.strokeStyle = 'rgba(255,183,77,0.6)'; pygCtx.lineWidth = 2;
  pygCtx.beginPath(); pygCtx.moveTo(110, 115); pygCtx.lineTo(110, 205); pygCtx.stroke();
  pygCtx.strokeStyle = 'rgba(186,104,200,0.6)';
  pygCtx.beginPath(); pygCtx.moveTo(135, 225); pygCtx.lineTo(268, 172); pygCtx.stroke();
  pygCtx.strokeStyle = 'rgba(129,199,132,0.45)'; pygCtx.setLineDash([4,4]);
  pygCtx.beginPath(); pygCtx.moveTo(268, 150); pygCtx.lineTo(135, 100); pygCtx.stroke();
  pygCtx.setLineDash([]);
  nodes.forEach(n => {
    const r = 16 + n.val * 16;
    pygCtx.fillStyle = 'rgba(' + n.col + ',' + (0.35 + n.val * 0.5).toFixed(3) + ')';
    pygCtx.beginPath(); pygCtx.arc(n.x, n.y, r, 0, Math.PI*2); pygCtx.fill();
    pygCtx.fillStyle = '#e0e0e0'; pygCtx.font = '11px monospace'; pygCtx.textAlign = 'center';
    pygCtx.fillText(n.label, n.x, n.y + r + 14);
  });
  // Right: history chart
  const cx0 = 380, cy0 = 30, cw = 560, ch = 260;
  pygCtx.strokeStyle = 'rgba(186,104,200,0.2)'; pygCtx.lineWidth = 1;
  pygCtx.strokeRect(cx0, cy0, cw, ch);
  pygCtx.strokeStyle = 'rgba(186,104,200,0.12)'; pygCtx.setLineDash([4,4]);
  pygCtx.beginPath(); pygCtx.moveTo(cx0, cy0 + ch/2); pygCtx.lineTo(cx0 + cw, cy0 + ch/2); pygCtx.stroke();
  pygCtx.setLineDash([]);
  function lineFor(key, col) {
    pygCtx.strokeStyle = col; pygCtx.lineWidth = 2; pygCtx.beginPath();
    const n = pygHistory.length;
    pygHistory.forEach((h, i) => {
      const x = cx0 + (i / 400) * cw;
      const y = cy0 + ch - h[key] * ch;
      if (i === 0) pygCtx.moveTo(x, y); else pygCtx.lineTo(x, y);
    });
    pygCtx.stroke();
  }
  lineFor('expect', 'rgba(255,183,77,0.85)');
  lineFor('conf',   'rgba(186,104,200,0.85)');
  lineFor('perf',   'rgba(129,199,132,0.95)');
  // Legend
  pygCtx.font = '11px monospace'; pygCtx.textAlign = 'left';
  pygCtx.fillStyle = 'rgba(255,183,77,0.9)'; pygCtx.fillRect(cx0 + 10, cy0 + 12, 12, 2);
  pygCtx.fillStyle = '#aaa'; pygCtx.fillText('expectation', cx0 + 28, cy0 + 16);
  pygCtx.fillStyle = 'rgba(186,104,200,0.9)'; pygCtx.fillRect(cx0 + 120, cy0 + 12, 12, 2);
  pygCtx.fillStyle = '#aaa'; pygCtx.fillText('confidence', cx0 + 138, cy0 + 16);
  pygCtx.fillStyle = 'rgba(129,199,132,0.9)'; pygCtx.fillRect(cx0 + 228, cy0 + 12, 12, 2);
  pygCtx.fillStyle = '#aaa'; pygCtx.fillText('performance', cx0 + 246, cy0 + 16);
  requestAnimationFrame(drawPyg);
}
drawPyg();

// ═══════════════════════════════════════════════════════════════════════
// Addiction — Weight Hijacking
// ═══════════════════════════════════════════════════════════════════════
const addictCanvas = document.getElementById('addict-canvas');
const addictCtx = addictCanvas.getContext('2d');
const addictNodes = [], addictEdges = [];
function addictInit() {
  addictNodes.length = 0; addictEdges.length = 0;
  const W = 960, H = 360;
  const labels = ['food','sex','social','music','movement','rest','curiosity','mastery','substance'];
  const cx = W/2, cy = H/2 + 8;
  for (let i = 0; i < labels.length; i++) {
    const a = (i / labels.length) * Math.PI * 2 - Math.PI/2;
    addictNodes.push({
      x: cx + Math.cos(a) * 150,
      y: cy + Math.sin(a) * 110,
      act: 0.2, label: labels[i],
      substance: labels[i] === 'substance',
      center: false,
    });
  }
  addictNodes.push({ x: cx, y: cy, act: 1, label: 'self', center: true, substance: false });
  for (let i = 0; i < labels.length; i++) {
    addictEdges.push({ a: addictNodes.length - 1, b: i });
  }
}
addictInit();
document.getElementById('addict-gain').addEventListener('input', (e) => {
  document.getElementById('addict-gain-val').textContent = (parseInt(e.target.value) / 100).toFixed(1) + '×';
});
function addictPulse() {
  const gain = parseInt(document.getElementById('addict-gain').value) / 100;
  const weights = addictNodes.map(n => n.center ? 0 : (n.substance ? gain : 1));
  const total = weights.reduce((a, b) => a + b, 0);
  addictNodes.forEach((n, i) => {
    if (n.center) return;
    n.act = Math.min(1, n.act + 0.85 * weights[i] / total);
  });
}
function addictReset() {
  addictNodes.forEach(n => { if (!n.center) n.act = 0.2; });
  document.getElementById('addict-gain').value = 100;
  document.getElementById('addict-gain-val').textContent = '1.0×';
}
function drawAddict() {
  const W = 960, H = 360;
  addictCtx.fillStyle = themeBg(); addictCtx.fillRect(0, 0, W, H);
  addictNodes.forEach(n => { if (!n.center) n.act *= 0.975; });
  addictEdges.forEach(e => {
    const a = addictNodes[e.a], b = addictNodes[e.b];
    const heat = b.act;
    const col = b.substance ? '229,57,53' : '186,104,200';
    addictCtx.strokeStyle = 'rgba(' + col + ',' + (0.1 + heat * 0.55).toFixed(3) + ')';
    addictCtx.lineWidth = 0.5 + heat * 3;
    addictCtx.beginPath(); addictCtx.moveTo(a.x, a.y); addictCtx.lineTo(b.x, b.y); addictCtx.stroke();
  });
  addictCtx.font = '11px monospace'; addictCtx.textAlign = 'center';
  addictNodes.forEach(n => {
    const r = n.center ? 20 : 9 + n.act * 16;
    const col = n.center ? '79,195,247' : (n.substance ? '229,57,53' : '186,104,200');
    const alpha = n.center ? 0.8 : (0.35 + n.act * 0.6);
    addictCtx.fillStyle = 'rgba(' + col + ',' + alpha.toFixed(3) + ')';
    addictCtx.beginPath(); addictCtx.arc(n.x, n.y, r, 0, Math.PI*2); addictCtx.fill();
    addictCtx.fillStyle = '#e0e0e0';
    addictCtx.fillText(n.label, n.x, n.y + r + 12);
  });
  requestAnimationFrame(drawAddict);
}
drawAddict();

// ═══════════════════════════════════════════════════════════════════════
// Flow State
// ═══════════════════════════════════════════════════════════════════════
const flowCanvas = document.getElementById('flow-canvas');
const flowCtx = flowCanvas.getContext('2d');
let flowX = 0.5, flowY = 0.5;
const flowParticles = [];
for (let i = 0; i < 240; i++) {
  flowParticles.push({
    x: Math.random() * 960, y: Math.random() * 420,
    vx: 0, vy: 0, size: 1 + Math.random() * 2,
    alpha: 0.3 + Math.random() * 0.5,
  });
}
['flow-skill','flow-chal','flow-fb'].forEach(id => {
  document.getElementById(id).addEventListener('input', (e) => {
    document.getElementById(id + '-val').textContent = e.target.value;
  });
});
function drawFlow() {
  const W = 960, H = 420;
  flowCtx.fillStyle = themeBg(); flowCtx.fillRect(0, 0, W, H);
  const skill = parseInt(document.getElementById('flow-skill').value) / 100;
  const chal  = parseInt(document.getElementById('flow-chal').value) / 100;
  const fb    = parseInt(document.getElementById('flow-fb').value) / 100;
  // Skill/challenge match on X axis; feedback sets Y (coherence toward top)
  const match = 1 - Math.abs(skill - chal);
  // Target position in the state space
  const tgtX = 0.55 + match * 0.35;
  const tgtY = 0.5 + fb * 0.4;
  // Attract the cursor toward the target
  flowX += (tgtX - flowX) * 0.08;
  flowY += (tgtY - flowY) * 0.08;
  // Flow condition
  const inFlow = match > 0.85 && fb > 0.6 && skill > 0.4;
  document.getElementById('flow-in').textContent = inFlow ? 'YES' : 'no';
  document.getElementById('flow-in').style.color = inFlow ? 'var(--accent2)' : 'var(--warn)';
  // Quadrant labels & axes
  flowCtx.strokeStyle = 'rgba(186,104,200,0.15)'; flowCtx.lineWidth = 1;
  flowCtx.setLineDash([4,4]);
  flowCtx.beginPath(); flowCtx.moveTo(W/2, 0); flowCtx.lineTo(W/2, H); flowCtx.stroke();
  flowCtx.beginPath(); flowCtx.moveTo(0, H/2); flowCtx.lineTo(W, H/2); flowCtx.stroke();
  flowCtx.setLineDash([]);
  flowCtx.font = '11px monospace';
  flowCtx.fillStyle = 'rgba(129,199,132,0.35)'; flowCtx.textAlign = 'right';
  flowCtx.fillText('GENIUS', W - 14, 16);
  flowCtx.fillStyle = 'rgba(229,57,53,0.35)'; flowCtx.textAlign = 'left';
  flowCtx.fillText('CHAOS', 14, 16);
  flowCtx.fillStyle = 'rgba(79,195,247,0.35)'; flowCtx.textAlign = 'right';
  flowCtx.fillText('ORDER', W - 14, H - 8);
  flowCtx.fillStyle = 'rgba(120,120,120,0.4)'; flowCtx.textAlign = 'left';
  flowCtx.fillText('STAGNATION', 14, H - 8);
  // Flow lane (attractor basin) — narrow band in the top-right quadrant
  const lane = {
    x: W * 0.60, y: 0,
    w: W * 0.38, h: H * 0.42,
  };
  if (inFlow) {
    const grad = flowCtx.createRadialGradient(lane.x + lane.w/2, lane.y + lane.h/2, 0, lane.x + lane.w/2, lane.y + lane.h/2, 260);
    grad.addColorStop(0, 'rgba(129,199,132,0.22)');
    grad.addColorStop(1, 'rgba(129,199,132,0)');
    flowCtx.fillStyle = grad;
    flowCtx.fillRect(lane.x, lane.y, lane.w, lane.h);
    flowCtx.strokeStyle = 'rgba(129,199,132,0.55)';
    flowCtx.lineWidth = 1.5;
    flowCtx.strokeRect(lane.x, lane.y, lane.w, lane.h);
    flowCtx.fillStyle = 'rgba(129,199,132,0.85)';
    flowCtx.textAlign = 'left';
    flowCtx.fillText('FLOW LANE', lane.x + 10, lane.y + 18);
  } else {
    flowCtx.strokeStyle = 'rgba(129,199,132,0.18)';
    flowCtx.setLineDash([3,5]); flowCtx.lineWidth = 1;
    flowCtx.strokeRect(lane.x, lane.y, lane.w, lane.h);
    flowCtx.setLineDash([]);
    flowCtx.fillStyle = 'rgba(129,199,132,0.3)';
    flowCtx.textAlign = 'left';
    flowCtx.fillText('flow lane (unlocked)', lane.x + 10, lane.y + 18);
  }
  // Particles — flow mode pulls them all along the lane
  const cx = flowX * W, cy = (1 - flowY) * H;
  flowParticles.forEach(p => {
    if (inFlow) {
      const tx = lane.x + (p.x % lane.w);
      const ty = lane.y + lane.h * 0.5 + Math.sin(p.x * 0.02) * 40;
      p.vx += (tx - p.x) * 0.004 + 0.5;
      p.vy += (ty - p.y) * 0.01;
    } else {
      p.vx += (Math.random() - 0.5) * 0.8;
      p.vy += (Math.random() - 0.5) * 0.8;
    }
    p.vx *= 0.92; p.vy *= 0.92;
    p.x += p.vx; p.y += p.vy;
    if (p.x < 0) p.x = W; if (p.x > W) p.x = 0;
    if (p.y < 0) p.y = H; if (p.y > H) p.y = 0;
    const col = inFlow ? '129,199,132' : '186,104,200';
    flowCtx.fillStyle = 'rgba(' + col + ',' + (p.alpha * (inFlow ? 0.9 : 0.5)).toFixed(3) + ')';
    flowCtx.beginPath(); flowCtx.arc(p.x, p.y, p.size, 0, Math.PI*2); flowCtx.fill();
  });
  // Cursor
  flowCtx.beginPath(); flowCtx.arc(cx, cy, 9, 0, Math.PI*2);
  flowCtx.fillStyle = inFlow ? 'rgba(129,199,132,0.7)' : 'rgba(186,104,200,0.55)';
  flowCtx.fill();
  flowCtx.strokeStyle = inFlow ? '#81c784' : '#ba68c8';
  flowCtx.lineWidth = 2; flowCtx.stroke();
  // Match gauge
  flowCtx.fillStyle = '#888'; flowCtx.font = '11px monospace'; flowCtx.textAlign = 'left';
  flowCtx.fillText('skill/challenge match: ' + Math.round(match * 100) + '%', 16, H - 28);
  flowCtx.fillText('feedback gain: ' + Math.round(fb * 100) + '%', 240, H - 28);
  requestAnimationFrame(drawFlow);
}
drawFlow();

// ═══════════════════════════════════════════════════════════════════════
// Hallucination
// ═══════════════════════════════════════════════════════════════════════
const hallucCanvas = document.getElementById('halluc-canvas');
const hallucCtx = hallucCanvas.getContext('2d');
const hallucBufLen = 240;
let hallucReal = new Array(hallucBufLen).fill(0.5);
let hallucFcast = new Array(hallucBufLen).fill(0.5);
let hallucT = 0, hallucMuted = false;
document.getElementById('halluc-prior').addEventListener('input', (e) => {
  document.getElementById('halluc-prior-val').textContent = e.target.value + '%';
});
function hallucMute() {
  hallucMuted = true;
  document.getElementById('halluc-state').textContent = 'MUTED';
  document.getElementById('halluc-state').style.color = 'var(--warn)';
}
function hallucRestore() {
  hallucMuted = false;
  document.getElementById('halluc-state').textContent = 'live';
  document.getElementById('halluc-state').style.color = 'var(--accent2)';
}
function hallucReset() {
  hallucReal = new Array(hallucBufLen).fill(0.5);
  hallucFcast = new Array(hallucBufLen).fill(0.5);
  hallucT = 0;
  hallucRestore();
}
function drawHalluc() {
  hallucT++;
  const W = 960, H = 280;
  hallucCtx.fillStyle = hallucMuted ? '#08080e' : '#0e0e12';
  hallucCtx.fillRect(0, 0, W, H);
  const prior = parseInt(document.getElementById('halluc-prior').value) / 100;
  // Reality: normal wandering sine unless muted
  let real;
  if (hallucMuted) {
    real = 0.5; // input channel flat-lined
  } else {
    real = 0.5 + Math.sin(hallucT * 0.035) * 0.25 + (Math.random() - 0.5) * 0.03;
  }
  // Forecast: when unmuted, it tracks real with lag. When muted, it drifts on priors.
  const lastFc = hallucFcast[hallucFcast.length - 1];
  let fc;
  if (hallucMuted) {
    // Forecast drifts — pulled by slow internal oscillator weighted by prior stiffness
    const internal = 0.5 + Math.sin(hallucT * 0.02) * 0.3 + Math.cos(hallucT * 0.009) * 0.2;
    const driftPull = (1 - prior) * 0.6 + 0.02;
    fc = lastFc + (internal - lastFc) * driftPull + (Math.random() - 0.5) * 0.04 * (1 - prior);
    fc = Math.max(0.02, Math.min(0.98, fc));
  } else {
    const gain = 1 - prior * 0.92;
    fc = lastFc + (real - lastFc) * gain;
  }
  hallucReal.push(real); hallucReal.shift();
  hallucFcast.push(fc); hallucFcast.shift();
  // Midline
  hallucCtx.strokeStyle = 'rgba(186,104,200,0.12)'; hallucCtx.lineWidth = 1;
  hallucCtx.setLineDash([4,4]);
  hallucCtx.beginPath(); hallucCtx.moveTo(0, H/2); hallucCtx.lineTo(W, H/2); hallucCtx.stroke();
  hallucCtx.setLineDash([]);
  const stepX = W / hallucBufLen;
  // Reality line (dimmed when muted to show it's flat/gone)
  hallucCtx.strokeStyle = hallucMuted ? 'rgba(129,199,132,0.25)' : 'rgba(129,199,132,0.95)';
  hallucCtx.lineWidth = 2;
  hallucCtx.beginPath();
  for (let i = 0; i < hallucBufLen; i++) {
    const x = i * stepX, y = H - hallucReal[i] * H;
    if (i === 0) hallucCtx.moveTo(x, y); else hallucCtx.lineTo(x, y);
  }
  hallucCtx.stroke();
  // Forecast line
  hallucCtx.strokeStyle = hallucMuted ? 'rgba(255,107,107,0.95)' : 'rgba(186,104,200,0.85)';
  hallucCtx.lineWidth = 2;
  hallucCtx.beginPath();
  for (let i = 0; i < hallucBufLen; i++) {
    const x = i * stepX, y = H - hallucFcast[i] * H;
    if (i === 0) hallucCtx.moveTo(x, y); else hallucCtx.lineTo(x, y);
  }
  hallucCtx.stroke();
  hallucCtx.font = '11px monospace'; hallucCtx.textAlign = 'left'; hallucCtx.fillStyle = '#aaa';
  hallucCtx.fillRect(W - 180, 12, 14, 2);
  hallucCtx.fillStyle = hallucMuted ? 'rgba(255,107,107,0.9)' : 'rgba(186,104,200,0.9)';
  hallucCtx.fillRect(W - 180, 12, 14, 2);
  hallucCtx.fillStyle = '#aaa'; hallucCtx.fillText(hallucMuted ? 'HALLUCINATION' : 'forecast', W - 160, 16);
  hallucCtx.fillStyle = 'rgba(129,199,132,' + (hallucMuted ? 0.3 : 0.9) + ')';
  hallucCtx.fillRect(W - 180, 28, 14, 2);
  hallucCtx.fillStyle = '#aaa'; hallucCtx.fillText(hallucMuted ? 'reality (flatlined)' : 'reality', W - 160, 32);
  if (hallucMuted) {
    hallucCtx.fillStyle = 'rgba(255,107,107,0.9)';
    hallucCtx.fillText('◉ INPUT MUTED — the purple line is the network inventing what should be there', 16, 22);
  }
  requestAnimationFrame(drawHalluc);
}
drawHalluc();

// ═══════════════════════════════════════════════════════════════════════
// Metaphor — Structural Transfer
// ═══════════════════════════════════════════════════════════════════════
const metaCanvas = document.getElementById('meta-canvas');
const metaCtx = metaCanvas.getContext('2d');
let metaState = null, metaBridges = 0;
const metaMappings = {
  'time-money': {
    left: { name: 'TIME', x: 220, nodes: ['save','spend','invest','waste','run out','budget'] },
    right: { name: 'MONEY', x: 740, nodes: ['save','spend','invest','waste','run out','budget'] },
    pairs: [[0,0],[1,1],[2,2],[3,3],[4,4],[5,5]],
  },
  'argue-war': {
    left: { name: 'ARGUMENT', x: 220, nodes: ['attack','defend','position','retreat','win','ally'] },
    right: { name: 'WAR', x: 740, nodes: ['attack','defend','position','retreat','win','ally'] },
    pairs: [[0,0],[1,1],[2,2],[3,3],[4,4],[5,5]],
  },
  'life-journey': {
    left: { name: 'LIFE', x: 220, nodes: ['start','goal','path','obstacle','milestone','lost'] },
    right: { name: 'JOURNEY', x: 740, nodes: ['start','destination','path','obstacle','waypoint','lost'] },
    pairs: [[0,0],[1,1],[2,2],[3,3],[4,4],[5,5]],
  },
};
function metaMap(key) {
  metaState = { key, t: 0, map: metaMappings[key] };
  metaBridges = metaMappings[key].pairs.length;
  document.getElementById('meta-bridges').textContent = metaBridges;
}
function metaReset() {
  metaState = null; metaBridges = 0;
  document.getElementById('meta-bridges').textContent = '0';
}
function drawMeta() {
  const W = 960, H = 360;
  metaCtx.fillStyle = themeBg(); metaCtx.fillRect(0, 0, W, H);
  const m = metaState ? metaState.map : metaMappings['time-money'];
  const dim = !metaState;
  metaCtx.font = '11px monospace'; metaCtx.textAlign = 'center';
  [m.left, m.right].forEach(side => {
    metaCtx.fillStyle = dim ? 'rgba(186,104,200,0.35)' : 'rgba(186,104,200,0.9)';
    metaCtx.font = 'bold 13px monospace';
    metaCtx.fillText(side.name, side.x, 30);
    metaCtx.font = '11px monospace';
    side.nodes.forEach((n, i) => {
      const y = 70 + i * 42;
      metaCtx.fillStyle = dim ? 'rgba(186,104,200,0.15)' : 'rgba(186,104,200,0.5)';
      metaCtx.beginPath(); metaCtx.arc(side.x, y, 18, 0, Math.PI*2); metaCtx.fill();
      metaCtx.strokeStyle = dim ? 'rgba(186,104,200,0.3)' : 'rgba(186,104,200,0.85)';
      metaCtx.lineWidth = 1; metaCtx.stroke();
      metaCtx.fillStyle = '#e0e0e0';
      metaCtx.fillText(n, side.x, y + 4);
    });
  });
  if (metaState) {
    metaState.t = Math.min(1, metaState.t + 0.02);
    metaState.map.pairs.forEach((pair, idx) => {
      const [a, b] = pair;
      const y1 = 70 + a * 42;
      const y2 = 70 + b * 42;
      const reveal = Math.max(0, Math.min(1, metaState.t * 6 - idx * 0.6));
      if (reveal <= 0) return;
      metaCtx.strokeStyle = 'rgba(129,199,132,' + (reveal * 0.8).toFixed(3) + ')';
      metaCtx.lineWidth = 2;
      metaCtx.beginPath();
      metaCtx.moveTo(m.left.x + 18, y1);
      metaCtx.lineTo(m.right.x - 18, y2);
      metaCtx.stroke();
      // Flowing dot
      const pulseT = ((metaState.t * 60 + idx * 10) % 60) / 60;
      const px = (m.left.x + 18) + ((m.right.x - 18) - (m.left.x + 18)) * pulseT;
      const py = y1 + (y2 - y1) * pulseT;
      metaCtx.fillStyle = 'rgba(255,255,255,' + (reveal * 0.9).toFixed(3) + ')';
      metaCtx.beginPath(); metaCtx.arc(px, py, 3, 0, Math.PI*2); metaCtx.fill();
    });
    metaCtx.fillStyle = 'rgba(129,199,132,0.9)'; metaCtx.textAlign = 'center';
    metaCtx.fillText('STRUCTURE TRANSFERRED →', W/2, 340);
  } else {
    metaCtx.fillStyle = 'rgba(186,104,200,0.5)'; metaCtx.textAlign = 'center';
    metaCtx.fillText('click a metaphor to activate the mapping', W/2, 340);
  }
  requestAnimationFrame(drawMeta);
}
drawMeta();

// ═══════════════════════════════════════════════════════════════════════
// Déjà Vu — Partial-Match Retrieval
// ═══════════════════════════════════════════════════════════════════════
const dejaCanvas = document.getElementById('deja-canvas');
const dejaCtx = dejaCanvas.getContext('2d');
const dejaMemories = [];
let dejaFam = 0, dejaRet = 0, dejaHits = 0, dejaFlash = 0;
function dejaUpdateUI() {
  document.getElementById('deja-fam').textContent = dejaFam.toFixed(2);
  document.getElementById('deja-ret').textContent = dejaRet.toFixed(2);
  document.getElementById('deja-hits').textContent = dejaHits;
}
function dejaRandomScene() {
  const vec = [];
  for (let i = 0; i < 8; i++) vec.push(Math.random());
  return vec;
}
function dejaEncode() {
  if (dejaMemories.length >= 6) dejaMemories.shift();
  dejaMemories.push(dejaRandomScene());
}
function dejaScore(scene) {
  let best = 0;
  dejaMemories.forEach(m => {
    let sim = 0;
    for (let i = 0; i < 8; i++) sim += 1 - Math.abs(m[i] - scene[i]);
    sim /= 8;
    if (sim > best) best = sim;
  });
  return best;
}
function dejaNovel() {
  const scene = dejaRandomScene();
  const match = dejaScore(scene);
  dejaFam = match;
  dejaRet = match > 0.75 ? match : 0.1;
  dejaFlash = 30;
  dejaUpdateUI();
}
function dejaPartial() {
  // Create a partial-match scene by starting from a memory and perturbing
  if (!dejaMemories.length) { dejaNovel(); return; }
  const base = dejaMemories[Math.floor(Math.random() * dejaMemories.length)];
  const scene = base.map(v => Math.max(0, Math.min(1, v + (Math.random() - 0.5) * 0.7)));
  const match = dejaScore(scene);
  dejaFam = Math.min(0.95, match + 0.15);
  dejaRet = Math.max(0.1, match - 0.25); // retrieval fails
  if (dejaFam > 0.5 && dejaRet < 0.4) {
    dejaHits++;
    dejaFlash = 80;
  }
  dejaUpdateUI();
}
function dejaReset() {
  dejaMemories.length = 0;
  dejaFam = 0; dejaRet = 0; dejaHits = 0; dejaFlash = 0;
  dejaUpdateUI();
}
function drawDeja() {
  const W = 960, H = 320;
  dejaCtx.fillStyle = themeBg(); dejaCtx.fillRect(0, 0, W, H);
  dejaFlash *= 0.95;
  if (dejaFlash > 1) {
    dejaCtx.fillStyle = 'rgba(255,183,77,' + Math.min(0.15, dejaFlash / 200).toFixed(3) + ')';
    dejaCtx.fillRect(0, 0, W, H);
  }
  // Memory pool on top
  dejaCtx.font = '11px monospace'; dejaCtx.textAlign = 'left';
  dejaCtx.fillStyle = '#888'; dejaCtx.fillText('memory pool', 30, 20);
  dejaMemories.forEach((m, idx) => {
    const x = 30 + idx * 150;
    for (let i = 0; i < 8; i++) {
      const cell = Math.floor(m[i] * 255);
      dejaCtx.fillStyle = 'rgba(186,104,200,' + m[i].toFixed(3) + ')';
      dejaCtx.fillRect(x + i * 14, 30, 12, 12);
    }
    dejaCtx.strokeStyle = 'rgba(186,104,200,0.35)';
    dejaCtx.strokeRect(x - 2, 28, 118, 16);
  });
  // Two circuits
  const famX = 280, famY = 180, retX = 680, retY = 180;
  // Familiarity circuit
  dejaCtx.fillStyle = 'rgba(186,104,200,0.35)';
  dejaCtx.beginPath(); dejaCtx.arc(famX, famY, 50 + dejaFam * 40, 0, Math.PI*2); dejaCtx.fill();
  dejaCtx.strokeStyle = 'rgba(186,104,200,0.85)'; dejaCtx.lineWidth = 2;
  dejaCtx.beginPath(); dejaCtx.arc(famX, famY, 50 + dejaFam * 40, 0, Math.PI*2); dejaCtx.stroke();
  dejaCtx.fillStyle = '#e0e0e0'; dejaCtx.textAlign = 'center';
  dejaCtx.fillText('FAMILIARITY', famX, famY + 4);
  dejaCtx.fillText(dejaFam.toFixed(2), famX, famY + 20);
  // Retrieval circuit
  dejaCtx.fillStyle = 'rgba(129,199,132,0.35)';
  dejaCtx.beginPath(); dejaCtx.arc(retX, retY, 50 + dejaRet * 40, 0, Math.PI*2); dejaCtx.fill();
  dejaCtx.strokeStyle = 'rgba(129,199,132,0.85)'; dejaCtx.lineWidth = 2;
  dejaCtx.beginPath(); dejaCtx.arc(retX, retY, 50 + dejaRet * 40, 0, Math.PI*2); dejaCtx.stroke();
  dejaCtx.fillStyle = '#e0e0e0';
  dejaCtx.fillText('CONTENT RETRIEVAL', retX, retY + 4);
  dejaCtx.fillText(dejaRet.toFixed(2), retX, retY + 20);
  // Gap warning
  if (dejaFam - dejaRet > 0.3) {
    dejaCtx.fillStyle = 'rgba(255,183,77,0.9)';
    dejaCtx.font = 'bold 12px monospace';
    dejaCtx.fillText('◉ DÉJÀ VU: familiarity without content', W/2, 290);
  }
  requestAnimationFrame(drawDeja);
}
drawDeja();

// ═══════════════════════════════════════════════════════════════════════
// Grief — Network Rewiring After Lost Node
// ═══════════════════════════════════════════════════════════════════════
const griefCanvas = document.getElementById('grief-canvas');
const griefCtx = griefCanvas.getContext('2d');
const griefNodes = [], griefEdges = [];
let griefPerson = -1, griefDangling = 0, griefRewired = 0, griefAutoOn = false;
function griefUpdate() {
  document.getElementById('grief-dangling').textContent = griefDangling;
  document.getElementById('grief-rewired').textContent = griefRewired;
}
function griefInit() {
  griefNodes.length = 0; griefEdges.length = 0;
  griefPerson = -1; griefDangling = 0; griefRewired = 0; griefAutoOn = false;
  const W = 960, H = 380;
  // Central person node
  griefNodes.push({ x: W/2, y: H/2, label: 'person', person: true, alive: true, act: 1 });
  griefPerson = 0;
  // Surrounding life nodes
  const labels = ['place','routine','song','joke','recipe','chair','story','phrase','plan','holiday','call','meal','walk','photo','playlist','book','gift','memory'];
  for (let i = 0; i < labels.length; i++) {
    const a = (i / labels.length) * Math.PI * 2;
    const r = 130 + (i % 3) * 18;
    griefNodes.push({
      x: W/2 + Math.cos(a) * r,
      y: H/2 + Math.sin(a) * r,
      label: labels[i], person: false, alive: true, act: 0.25,
    });
    griefEdges.push({ a: 0, b: i + 1, alive: true, dangling: false, rewiredTo: -1 });
  }
  griefUpdate();
}
griefInit();
function griefLose() {
  if (griefPerson < 0 || !griefNodes[griefPerson].alive) return;
  griefNodes[griefPerson].alive = false;
  griefNodes[griefPerson].act = 0;
  griefEdges.forEach(e => {
    if (e.a === griefPerson || e.b === griefPerson) {
      e.dangling = true;
      griefDangling++;
    }
  });
  griefUpdate();
}
function griefStep() {
  // Pick one dangling edge and rewire its other end to a random still-alive neighbor
  const danglers = [];
  griefEdges.forEach((e, i) => { if (e.dangling) danglers.push(i); });
  if (!danglers.length) return;
  const idx = danglers[Math.floor(Math.random() * danglers.length)];
  const e = griefEdges[idx];
  const other = e.a === griefPerson ? e.b : e.a;
  // Find a nearby alive non-person node to redirect to
  const candidates = [];
  griefNodes.forEach((n, i) => {
    if (i === other || !n.alive || n.person) return;
    const d = Math.hypot(n.x - griefNodes[other].x, n.y - griefNodes[other].y);
    if (d < 220) candidates.push(i);
  });
  if (!candidates.length) return;
  const newTarget = candidates[Math.floor(Math.random() * candidates.length)];
  e.a = other; e.b = newTarget; e.dangling = false; e.rewiredTo = newTarget;
  griefDangling--; griefRewired++;
  // The outer node gets a temporary activation flare as the rewire happens
  griefNodes[other].act = Math.min(1, griefNodes[other].act + 0.4);
  griefUpdate();
}
function griefAuto() { griefAutoOn = !griefAutoOn; }
function griefReset() { griefInit(); }
let griefFrame = 0;
function drawGrief() {
  const W = 960, H = 380;
  griefCtx.fillStyle = themeBg(); griefCtx.fillRect(0, 0, W, H);
  griefFrame++;
  if (griefAutoOn && griefFrame % 30 === 0) griefStep();
  griefNodes.forEach(n => { if (!n.person) n.act *= 0.985; if (n.act < 0.2) n.act = 0.2; });
  griefEdges.forEach(e => {
    const a = griefNodes[e.a], b = griefNodes[e.b];
    if (!a || !b) return;
    let col = '186,104,200', alpha = 0.4;
    if (e.dangling) { col = '229,57,53'; alpha = 0.6; }
    else if (e.rewiredTo >= 0) { col = '129,199,132'; alpha = 0.6; }
    griefCtx.strokeStyle = 'rgba(' + col + ',' + alpha.toFixed(3) + ')';
    griefCtx.lineWidth = e.dangling ? 1 : 1.3;
    if (e.dangling) griefCtx.setLineDash([4, 4]);
    griefCtx.beginPath(); griefCtx.moveTo(a.x, a.y); griefCtx.lineTo(b.x, b.y); griefCtx.stroke();
    griefCtx.setLineDash([]);
  });
  griefNodes.forEach(n => {
    if (!n.alive && n.person) {
      // Ghost node
      griefCtx.strokeStyle = 'rgba(120,120,120,0.5)'; griefCtx.lineWidth = 1;
      griefCtx.setLineDash([3,3]);
      griefCtx.beginPath(); griefCtx.arc(n.x, n.y, 22, 0, Math.PI*2); griefCtx.stroke();
      griefCtx.setLineDash([]);
      griefCtx.fillStyle = 'rgba(120,120,120,0.7)'; griefCtx.font = '11px monospace'; griefCtx.textAlign = 'center';
      griefCtx.fillText('(lost)', n.x, n.y + 4);
      return;
    }
    const r = n.person ? 22 : (6 + n.act * 10);
    const col = n.person ? '255,183,77' : '186,104,200';
    griefCtx.fillStyle = 'rgba(' + col + ',' + (n.person ? 0.7 : 0.35 + n.act * 0.5).toFixed(3) + ')';
    griefCtx.beginPath(); griefCtx.arc(n.x, n.y, r, 0, Math.PI*2); griefCtx.fill();
    griefCtx.fillStyle = '#e0e0e0'; griefCtx.font = '10px monospace'; griefCtx.textAlign = 'center';
    griefCtx.fillText(n.label, n.x, n.y + r + 11);
  });
  requestAnimationFrame(drawGrief);
}
drawGrief();

// ═══════════════════════════════════════════════════════════════════════
// Learned Helplessness
// ═══════════════════════════════════════════════════════════════════════
const helpCanvas = document.getElementById('help-canvas');
const helpCtx = helpCanvas.getContext('2d');
let helpWeight = 1.0, helpTries = 0, helpRewards = 0;
const helpPulses = [];
document.getElementById('help-world').addEventListener('input', (e) => {
  document.getElementById('help-world-val').textContent = e.target.value + '%';
});
function helpUpdate() {
  document.getElementById('help-tries').textContent = helpTries;
  document.getElementById('help-rewards').textContent = helpRewards;
  document.getElementById('help-weight').textContent = helpWeight.toFixed(2);
}
function helpTry() {
  helpTries++;
  const world = parseInt(document.getElementById('help-world').value) / 100;
  // Success probability scales with world responsiveness, modulated by current weight
  const success = Math.random() < world;
  if (success) {
    helpRewards++;
    helpWeight = Math.min(1, helpWeight + 0.08);
    helpPulses.push({ from: 'action', success: true, t: 0 });
  } else {
    helpWeight = Math.max(0.02, helpWeight - 0.05);
    helpPulses.push({ from: 'action', success: false, t: 0 });
  }
  helpUpdate();
}
function helpAllowRewards() {
  document.getElementById('help-world').value = 80;
  document.getElementById('help-world-val').textContent = '80%';
}
function helpReset() {
  helpWeight = 1.0; helpTries = 0; helpRewards = 0;
  helpPulses.length = 0;
  document.getElementById('help-world').value = 0;
  document.getElementById('help-world-val').textContent = '0%';
  helpUpdate();
}
function drawHelp() {
  const W = 960, H = 360;
  helpCtx.fillStyle = themeBg(); helpCtx.fillRect(0, 0, W, H);
  const selfX = 180, selfY = H/2;
  const actX = 480, actY = H/2;
  const rewX = 780, rewY = H/2;
  // Edge self -> action (alive or dead based on weight)
  const edgeAlpha = 0.15 + helpWeight * 0.7;
  helpCtx.strokeStyle = 'rgba(186,104,200,' + edgeAlpha.toFixed(3) + ')';
  helpCtx.lineWidth = 1 + helpWeight * 4;
  helpCtx.beginPath(); helpCtx.moveTo(selfX + 28, selfY); helpCtx.lineTo(actX - 28, actY); helpCtx.stroke();
  // Edge action -> reward (alive or dead based on weight)
  helpCtx.strokeStyle = 'rgba(129,199,132,' + edgeAlpha.toFixed(3) + ')';
  helpCtx.lineWidth = 1 + helpWeight * 4;
  helpCtx.beginPath(); helpCtx.moveTo(actX + 28, actY); helpCtx.lineTo(rewX - 28, rewY); helpCtx.stroke();
  // Nodes
  const labels = [[selfX, selfY, 'self', '79,195,247'], [actX, actY, 'action', '186,104,200'], [rewX, rewY, 'reward', '129,199,132']];
  labels.forEach(l => {
    helpCtx.fillStyle = 'rgba(' + l[3] + ',' + (0.35 + helpWeight * 0.4).toFixed(3) + ')';
    helpCtx.beginPath(); helpCtx.arc(l[0], l[1], 28, 0, Math.PI*2); helpCtx.fill();
    helpCtx.strokeStyle = 'rgba(' + l[3] + ',0.85)'; helpCtx.lineWidth = 1.5; helpCtx.stroke();
    helpCtx.fillStyle = '#e0e0e0'; helpCtx.font = '12px monospace'; helpCtx.textAlign = 'center';
    helpCtx.fillText(l[2], l[0], l[1] + 4);
  });
  // Pulses: travel from self → action → (reward or dies)
  for (let i = helpPulses.length - 1; i >= 0; i--) {
    const p = helpPulses[i];
    p.t += 0.015;
    let px, py;
    if (p.t <= 1) {
      px = selfX + 28 + (actX - 28 - selfX - 28) * p.t;
      py = selfY;
    } else if (p.t <= 2 && p.success) {
      const k = p.t - 1;
      px = actX + 28 + (rewX - 28 - actX - 28) * k;
      py = actY;
    } else if (!p.success && p.t >= 1) {
      helpPulses.splice(i, 1); continue;
    } else {
      helpPulses.splice(i, 1); continue;
    }
    helpCtx.fillStyle = p.success ? 'rgba(129,199,132,0.95)' : 'rgba(229,57,53,0.95)';
    helpCtx.beginPath(); helpCtx.arc(px, py, 4, 0, Math.PI*2); helpCtx.fill();
  }
  // Weight gauge
  helpCtx.fillStyle = '#888'; helpCtx.font = '11px monospace'; helpCtx.textAlign = 'left';
  helpCtx.fillText('action→reward pathway weight', 30, 30);
  helpCtx.fillStyle = '#16213e';
  helpCtx.fillRect(30, 38, 300, 14);
  helpCtx.fillStyle = helpWeight > 0.3 ? 'rgba(186,104,200,0.85)' : 'rgba(229,57,53,0.85)';
  helpCtx.fillRect(30, 38, 300 * helpWeight, 14);
  if (helpWeight < 0.1) {
    helpCtx.fillStyle = 'rgba(229,57,53,0.9)';
    helpCtx.font = 'bold 12px monospace';
    helpCtx.fillText('◉ LEARNED HELPLESSNESS — action pathway collapsed', 30, 330);
  }
  requestAnimationFrame(drawHelp);
}
drawHelp();

// ═══════════════════════════════════════════════════════════════════════
// Music — Prediction & Resolution
// ═══════════════════════════════════════════════════════════════════════
const musicCanvas = document.getElementById('music-canvas');
const musicCtx = musicCanvas.getContext('2d');
const musicPatterns = {
  consonant:  [60,62,64,65,67,69,67,65,64,62,60, 60,62,64,65,67,69,67,65,64,62,60],
  tension:    [60,62,64,65,67,70,72,71,69,67,65,64,62,60, 60,62,64,65,67,70,72,71,69,67,65,64,62,60],
  dissonant:  [60,63,66,61,58,62,67,64,70,66,63,61,65,59, 60,63,66,61,58,62,67,64,70,66,63,61,65,59],
};
let musicPattern = null, musicStep = 0, musicTimer = 0;
const musicHistActual = [], musicHistForecast = [], musicHistResid = [];
const musicBufLen = 80;
for (let i = 0; i < musicBufLen; i++) { musicHistActual.push(0.5); musicHistForecast.push(0.5); musicHistResid.push(0); }
function musicPlay(key) {
  musicPattern = musicPatterns[key].slice();
  musicStep = 0; musicTimer = 0;
}
function musicStop() { musicPattern = null; }
function drawMusic() {
  const W = 960, H = 320;
  musicCtx.fillStyle = themeBg(); musicCtx.fillRect(0, 0, W, H);
  if (musicPattern) {
    musicTimer++;
    if (musicTimer >= 14) {
      musicTimer = 0;
      const note = musicPattern[musicStep % musicPattern.length];
      // Normalize note to 0..1 in range [55, 75]
      const actual = Math.max(0.05, Math.min(0.95, (note - 55) / 20));
      // Forecast: linear extrapolation from last two actuals
      const n = musicHistActual.length;
      const lastFc = musicHistForecast[n - 1];
      const lastAct = musicHistActual[n - 1];
      const prevAct = musicHistActual[n - 2] || lastAct;
      const fc = Math.max(0.05, Math.min(0.95, lastAct + (lastAct - prevAct) * 0.8));
      const resid = Math.abs(actual - fc);
      musicHistActual.push(actual); musicHistActual.shift();
      musicHistForecast.push(fc); musicHistForecast.shift();
      musicHistResid.push(resid); musicHistResid.shift();
      musicStep++;
      if (musicStep >= musicPattern.length) musicPattern = null;
    }
  }
  const stepX = W / musicBufLen;
  // Residual bars
  for (let i = 0; i < musicBufLen; i++) {
    const r = musicHistResid[i];
    if (r < 0.02) continue;
    const bar = Math.min(H * 0.4, r * H * 2.5);
    musicCtx.fillStyle = 'rgba(255,183,77,' + Math.min(0.85, r * 4).toFixed(3) + ')';
    musicCtx.fillRect(i * stepX, H - bar, Math.max(1, stepX - 0.5), bar);
  }
  // Forecast line
  musicCtx.strokeStyle = 'rgba(186,104,200,0.8)'; musicCtx.lineWidth = 2;
  musicCtx.beginPath();
  for (let i = 0; i < musicBufLen; i++) {
    const x = i * stepX, y = H - musicHistForecast[i] * H;
    if (i === 0) musicCtx.moveTo(x, y); else musicCtx.lineTo(x, y);
  }
  musicCtx.stroke();
  // Actual melody as notes
  for (let i = 0; i < musicBufLen; i++) {
    const x = i * stepX, y = H - musicHistActual[i] * H;
    musicCtx.fillStyle = 'rgba(129,199,132,0.95)';
    musicCtx.beginPath(); musicCtx.arc(x, y, 3, 0, Math.PI*2); musicCtx.fill();
  }
  // Connect notes with a thin line
  musicCtx.strokeStyle = 'rgba(129,199,132,0.6)'; musicCtx.lineWidth = 1.5;
  musicCtx.beginPath();
  for (let i = 0; i < musicBufLen; i++) {
    const x = i * stepX, y = H - musicHistActual[i] * H;
    if (i === 0) musicCtx.moveTo(x, y); else musicCtx.lineTo(x, y);
  }
  musicCtx.stroke();
  const lastResid = musicHistResid[musicHistResid.length - 1];
  document.getElementById('music-tension').textContent = lastResid.toFixed(2);
  // Legend
  musicCtx.font = '11px monospace'; musicCtx.textAlign = 'left';
  musicCtx.fillStyle = 'rgba(186,104,200,0.9)'; musicCtx.fillRect(W - 160, 14, 14, 2);
  musicCtx.fillStyle = '#aaa'; musicCtx.fillText('forecast', W - 140, 18);
  musicCtx.fillStyle = 'rgba(129,199,132,0.9)'; musicCtx.fillRect(W - 160, 30, 14, 2);
  musicCtx.fillStyle = '#aaa'; musicCtx.fillText('melody', W - 140, 34);
  musicCtx.fillStyle = 'rgba(255,183,77,0.9)'; musicCtx.fillRect(W - 160, 46, 14, 2);
  musicCtx.fillStyle = '#aaa'; musicCtx.fillText('tension', W - 140, 50);
  requestAnimationFrame(drawMusic);
}
drawMusic();

// ═══════════════════════════════════════════════════════════════════════
// Self as Predicted Node
// ═══════════════════════════════════════════════════════════════════════
const selfCanvas = document.getElementById('self-canvas');
const selfCtx = selfCanvas.getContext('2d');
let selfCoh = 1.0, selfMode = 'stable', selfPhase = 0;
const selfFeeders = [
  { name: 'body',    x: 200, y: 130, active: 1 },
  { name: 'memory',  x: 760, y: 130, active: 1 },
  { name: 'context', x: 200, y: 290, active: 1 },
  { name: 'social',  x: 760, y: 290, active: 1 },
];
function selfDestabilize(kind) {
  selfMode = kind;
  if (kind === 'meditation') { selfFeeders[0].active = 0.2; selfFeeders[1].active = 0.2; selfFeeders[2].active = 1; selfFeeders[3].active = 1; }
  else if (kind === 'psychedelic') { selfFeeders.forEach(f => f.active = 0.15 + Math.random() * 0.2); }
  else if (kind === 'dissociation') { selfFeeders[0].active = 0.05; selfFeeders[1].active = 1; selfFeeders[2].active = 0.5; selfFeeders[3].active = 0.6; }
}
function selfRestore() {
  selfMode = 'stable';
  selfFeeders.forEach(f => f.active = 1);
}
function drawSelf() {
  const W = 960, H = 380;
  const bg = selfMode === 'psychedelic' ? '#0a0618' : '#0e0e12';
  selfCtx.fillStyle = bg; selfCtx.fillRect(0, 0, W, H);
  selfPhase += 0.04;
  // Target coherence based on feeder inputs
  const targetCoh = selfFeeders.reduce((s, f) => s + f.active, 0) / selfFeeders.length;
  selfCoh += (targetCoh - selfCoh) * 0.05;
  const cx = W/2, cy = H/2;
  // Background wave for psychedelic
  if (selfMode === 'psychedelic') {
    for (let i = 0; i < 5; i++) {
      const rr = 80 + i * 40 + Math.sin(selfPhase + i) * 20;
      selfCtx.strokeStyle = 'rgba(186,104,200,' + (0.08 - i * 0.012).toFixed(3) + ')';
      selfCtx.lineWidth = 1;
      selfCtx.beginPath(); selfCtx.arc(cx, cy, rr, 0, Math.PI*2); selfCtx.stroke();
    }
  }
  // Feeder nodes & edges
  selfFeeders.forEach(f => {
    const jitter = (selfMode === 'psychedelic' || selfMode === 'dissociation') ? Math.sin(selfPhase + f.x * 0.01) * (1 - f.active) * 8 : 0;
    const fx = f.x + jitter, fy = f.y + jitter;
    selfCtx.strokeStyle = 'rgba(186,104,200,' + (0.1 + f.active * 0.6).toFixed(3) + ')';
    selfCtx.lineWidth = 0.8 + f.active * 2.5;
    selfCtx.beginPath(); selfCtx.moveTo(fx, fy); selfCtx.lineTo(cx, cy); selfCtx.stroke();
    const r = 16 + f.active * 8;
    selfCtx.fillStyle = 'rgba(79,195,247,' + (0.25 + f.active * 0.55).toFixed(3) + ')';
    selfCtx.beginPath(); selfCtx.arc(fx, fy, r, 0, Math.PI*2); selfCtx.fill();
    selfCtx.fillStyle = '#e0e0e0'; selfCtx.font = '11px monospace'; selfCtx.textAlign = 'center';
    selfCtx.fillText(f.name, fx, fy + 4);
  });
  // Self node — size & stability reflect coherence
  const selfR = 28 + selfCoh * 22;
  const wobble = (1 - selfCoh) * 12 * Math.sin(selfPhase * 2);
  selfCtx.fillStyle = 'rgba(129,199,132,' + (0.3 + selfCoh * 0.55).toFixed(3) + ')';
  selfCtx.beginPath(); selfCtx.arc(cx + wobble, cy, selfR, 0, Math.PI*2); selfCtx.fill();
  selfCtx.strokeStyle = 'rgba(129,199,132,' + (0.5 + selfCoh * 0.45).toFixed(3) + ')';
  selfCtx.lineWidth = 2; selfCtx.stroke();
  selfCtx.fillStyle = '#ffffff'; selfCtx.font = 'bold 14px monospace'; selfCtx.textAlign = 'center';
  selfCtx.fillText(selfCoh > 0.5 ? 'SELF' : (selfCoh > 0.2 ? 'self?' : '...'), cx + wobble, cy + 4);
  // State label
  selfCtx.fillStyle = '#aaa'; selfCtx.font = '11px monospace';
  let stateLabel = 'stable';
  if (selfMode === 'meditation') stateLabel = '◐ meditation — body & memory quieted';
  else if (selfMode === 'psychedelic') stateLabel = '✺ psychedelic — priors weakened globally';
  else if (selfMode === 'dissociation') stateLabel = '◑ dissociation — body-feeder severed';
  selfCtx.fillText(stateLabel, 20, 24);
  document.getElementById('self-coh').textContent = selfCoh.toFixed(2);
  requestAnimationFrame(drawSelf);
}
drawSelf();

// ═══════════════════════════════════════════════════════════════════════
// Humor — Safe Prediction Failure
// ═══════════════════════════════════════════════════════════════════════
const humorCanvas = document.getElementById('humor-canvas');
const humorCtx = humorCanvas.getContext('2d');
const humorBufLen = 200;
let humorReal = new Array(humorBufLen).fill(0.5);
let humorFcast = new Array(humorBufLen).fill(0.5);
let humorThreat = new Array(humorBufLen).fill(0);
let humorT = 0, humorPlayback = null, humorContext = 'safe', humorLaughFlash = 0;
function humorPlay(ctx) {
  humorContext = ctx;
  humorPlayback = { phase: 'setup', step: 0 };
}
function humorReset() {
  humorReal = new Array(humorBufLen).fill(0.5);
  humorFcast = new Array(humorBufLen).fill(0.5);
  humorThreat = new Array(humorBufLen).fill(0);
  humorPlayback = null; humorLaughFlash = 0;
}
function drawHumor() {
  const W = 960, H = 300;
  humorT++;
  humorCtx.fillStyle = themeBg(); humorCtx.fillRect(0, 0, W, H);
  if (humorLaughFlash > 1) {
    humorCtx.fillStyle = 'rgba(129,199,132,' + Math.min(0.12, humorLaughFlash / 150).toFixed(3) + ')';
    humorCtx.fillRect(0, 0, W, H);
    humorLaughFlash *= 0.9;
  }
  // Generate the sequence
  let real = 0.5, fc = 0.5, threat = 0;
  if (humorPlayback) {
    if (humorPlayback.phase === 'setup') {
      const t = humorPlayback.step / 40;
      real = 0.5 + Math.sin(t * Math.PI) * 0.18;
      fc = 0.5 + Math.sin(t * Math.PI) * 0.16;
      humorPlayback.step++;
      if (humorPlayback.step > 40) { humorPlayback.phase = 'punch'; humorPlayback.step = 0; }
    } else if (humorPlayback.phase === 'punch') {
      real = humorPlayback.step < 6 ? 0.95 : 0.5;
      fc = 0.55;
      humorPlayback.step++;
      threat = humorContext === 'unsafe' ? 0.8 : 0;
      if (humorPlayback.step > 30) {
        humorPlayback = null;
        if (humorContext === 'safe') humorLaughFlash = 80;
      }
    }
  }
  humorReal.push(real); humorReal.shift();
  humorFcast.push(fc); humorFcast.shift();
  humorThreat.push(threat); humorThreat.shift();
  const stepX = W / humorBufLen;
  // Threat band (red tint along bottom)
  for (let i = 0; i < humorBufLen; i++) {
    if (humorThreat[i] > 0.05) {
      humorCtx.fillStyle = 'rgba(229,57,53,' + (humorThreat[i] * 0.4).toFixed(3) + ')';
      humorCtx.fillRect(i * stepX, H - 40, Math.max(1, stepX), 40);
    }
  }
  // Residual spike bars
  for (let i = 0; i < humorBufLen; i++) {
    const r = Math.abs(humorReal[i] - humorFcast[i]);
    if (r < 0.05) continue;
    const bar = r * H * 0.7;
    humorCtx.fillStyle = 'rgba(255,183,77,' + Math.min(0.8, r * 2.5).toFixed(3) + ')';
    humorCtx.fillRect(i * stepX, H - 60 - bar, Math.max(1, stepX), bar);
  }
  // Lines
  humorCtx.strokeStyle = 'rgba(186,104,200,0.85)'; humorCtx.lineWidth = 2;
  humorCtx.beginPath();
  for (let i = 0; i < humorBufLen; i++) {
    const x = i * stepX, y = H - humorFcast[i] * (H - 80) - 40;
    if (i === 0) humorCtx.moveTo(x, y); else humorCtx.lineTo(x, y);
  }
  humorCtx.stroke();
  humorCtx.strokeStyle = 'rgba(129,199,132,0.95)'; humorCtx.lineWidth = 2;
  humorCtx.beginPath();
  for (let i = 0; i < humorBufLen; i++) {
    const x = i * stepX, y = H - humorReal[i] * (H - 80) - 40;
    if (i === 0) humorCtx.moveTo(x, y); else humorCtx.lineTo(x, y);
  }
  humorCtx.stroke();
  // Labels
  humorCtx.font = '11px monospace'; humorCtx.textAlign = 'left';
  humorCtx.fillStyle = '#aaa'; humorCtx.fillText('threat monitor', 14, H - 8);
  humorCtx.fillStyle = 'rgba(186,104,200,0.9)'; humorCtx.fillRect(W - 220, 12, 14, 2);
  humorCtx.fillStyle = '#aaa'; humorCtx.fillText('forecast', W - 200, 16);
  humorCtx.fillStyle = 'rgba(129,199,132,0.9)'; humorCtx.fillRect(W - 220, 28, 14, 2);
  humorCtx.fillStyle = '#aaa'; humorCtx.fillText('punchline arrival', W - 200, 32);
  humorCtx.fillStyle = 'rgba(255,183,77,0.9)'; humorCtx.fillRect(W - 220, 44, 14, 2);
  humorCtx.fillStyle = '#aaa'; humorCtx.fillText('surprise', W - 200, 48);
  if (humorLaughFlash > 10) {
    humorCtx.fillStyle = 'rgba(129,199,132,0.9)'; humorCtx.font = 'bold 14px monospace';
    humorCtx.textAlign = 'center';
    humorCtx.fillText('◉ HA — all-clear signal', W/2, 40);
  }
  requestAnimationFrame(drawHumor);
}
drawHumor();

// ═══════════════════════════════════════════════════════════════════════
// Arousal & Clarity — the brain's most powerful state modulator
// ═══════════════════════════════════════════════════════════════════════
const clarityCanvas = document.getElementById('clarity-canvas');
const clarityCtx = clarityCanvas.getContext('2d');
let clarityPhaseActive = 'baseline';
function clarityPhase(p) { clarityPhaseActive = p; }

const CLARITY_PHASES = {
  baseline: {
    label: 'BASELINE', color: '#a78bfa',
    bandwidth: 0.80, coherence: 0.75, frontal: 0.85, predWindow: 0.80, reward: 0.30, valence: 0.10,
    desc: 'Normal operating state. Full bandwidth, frontal cortex online, prediction window hours ahead.',
  },
  arousal: {
    label: 'AROUSAL', color: '#f06292',
    bandwidth: 0.25, coherence: 0.30, frontal: 0.20, predWindow: 0.15, reward: 0.95, valence: 0.70,
    desc: 'State modulator active. Bandwidth narrowed to one goal. Frontal cortex suppressed. Prediction window collapsed.',
  },
  peak: {
    label: 'ORGASM', color: '#fbbf24',
    bandwidth: 0.10, coherence: 0.15, frontal: 0.10, predWindow: 0.05, reward: 1.00, valence: 0.95,
    desc: 'Reward prediction resolves. Massive dopamine spike. Residual closes to zero. Prolactin surge begins.',
  },
  clarity: {
    label: 'POST-NUT CLARITY', color: '#a3e635',
    bandwidth: 0.85, coherence: 0.80, frontal: 0.90, predWindow: 0.85, reward: 0.15, valence: 0.05,
    desc: 'Modulator OFF. Frontal cortex restored. Bandwidth returns. The contrast from suppressed to baseline feels like a boost.',
  },
};

function drawClarity() {
  var W = 960, H = 400;
  clarityCtx.fillStyle = themeBg(); clarityCtx.fillRect(0, 0, W, H);
  var p = CLARITY_PHASES[clarityPhaseActive];
  if (!p) { requestAnimationFrame(drawClarity); return; }

  // Phase label
  clarityCtx.fillStyle = p.color; clarityCtx.font = 'bold 16px monospace'; clarityCtx.textAlign = 'left';
  clarityCtx.fillText(p.label, 30, 30);
  clarityCtx.fillStyle = '#aaa'; clarityCtx.font = '11px monospace';
  clarityCtx.fillText(p.desc, 30, 52);

  // Six bars
  var dims = [
    { label: 'Bandwidth', v: p.bandwidth, col: '#a78bfa', goodHigh: true },
    { label: 'Coherence', v: p.coherence, col: '#67e8f9', goodHigh: true },
    { label: 'Frontal cortex', v: p.frontal, col: '#81c784', goodHigh: true },
    { label: 'Prediction window', v: p.predWindow, col: '#4fc3f7', goodHigh: true },
    { label: 'Reward drive', v: p.reward, col: '#f06292', goodHigh: false },
    { label: 'Valence (arousal)', v: p.valence, col: '#fbbf24', goodHigh: false },
  ];

  dims.forEach(function(d, i) {
    var y = 80 + i * 46;
    clarityCtx.fillStyle = '#ccc'; clarityCtx.font = '11px monospace'; clarityCtx.textAlign = 'left';
    clarityCtx.fillText(d.label, 30, y);

    // Bar background
    clarityCtx.fillStyle = 'rgba(120,120,130,0.15)';
    clarityCtx.fillRect(200, y - 6, 500, 22);

    // Bar fill — color-coded by whether high is good or bad
    var healthColor;
    if (d.goodHigh) {
      healthColor = d.v > 0.6 ? '129,199,132' : d.v > 0.35 ? '255,183,77' : '248,113,113';
    } else {
      healthColor = d.v < 0.35 ? '129,199,132' : d.v < 0.60 ? '255,183,77' : '248,113,113';
    }
    clarityCtx.fillStyle = 'rgba(' + healthColor + ', 0.75)';
    clarityCtx.fillRect(200, y - 6, 500 * d.v, 22);

    // Value
    clarityCtx.fillStyle = '#fff'; clarityCtx.font = 'bold 10px monospace'; clarityCtx.textAlign = 'right';
    clarityCtx.fillText((d.v * 100).toFixed(0), 695, y + 8);
  });

  // Phase indicator at bottom
  var phases = ['baseline', 'arousal', 'peak', 'clarity'];
  var phaseW = (W - 60) / phases.length;
  phases.forEach(function(ph, i) {
    var x = 30 + i * phaseW;
    var isActive = ph === clarityPhaseActive;
    var pp = CLARITY_PHASES[ph];
    clarityCtx.fillStyle = isActive ? pp.color + '33' : 'transparent';
    clarityCtx.fillRect(x, H - 50, phaseW - 8, 40);
    clarityCtx.strokeStyle = isActive ? pp.color : 'rgba(120,120,130,0.3)';
    clarityCtx.lineWidth = isActive ? 2 : 1;
    clarityCtx.strokeRect(x, H - 50, phaseW - 8, 40);
    clarityCtx.fillStyle = isActive ? pp.color : '#666';
    clarityCtx.font = isActive ? 'bold 10px monospace' : '10px monospace';
    clarityCtx.textAlign = 'center';
    clarityCtx.fillText(pp.label, x + (phaseW - 8) / 2, H - 26);
  });

  // Arrow between phases
  for (var i = 0; i < 3; i++) {
    var ax = 30 + (i + 1) * phaseW - 4;
    clarityCtx.fillStyle = '#666'; clarityCtx.font = '14px monospace'; clarityCtx.textAlign = 'center';
    clarityCtx.fillText('\u2192', ax, H - 26);
  }

  // Green = healthy, yellow = moderate, red = degraded
  clarityCtx.fillStyle = '#666'; clarityCtx.font = '10px monospace'; clarityCtx.textAlign = 'center';
  clarityCtx.fillText('green = healthy for cognition \u00b7 red = suppressed or overdriven', W / 2, H - 4);

  requestAnimationFrame(drawClarity);
}
drawClarity();

// ═══════════════════════════════════════════════════════════════════════
// Reading — Controlled Hallucination
// ═══════════════════════════════════════════════════════════════════════
const readCanvas = document.getElementById('read-canvas');
const readCtx = readCanvas.getContext('2d');
const readStories = {
  vivid: [
    { word: 'red',      load: 0.3 },
    { word: 'apple',    load: 0.7 },
    { word: 'wooden',   load: 0.55 },
    { word: 'table',    load: 0.8 },
    { word: 'sunlight', load: 0.9 },
    { word: 'crisp',    load: 0.75 },
    { word: 'bite',     load: 0.85 },
    { word: 'juice',    load: 0.9 },
  ],
  abstract: [
    { word: 'metaphysical', load: 0.1 },
    { word: 'dualism',      load: 0.08 },
    { word: 'implicit',     load: 0.12 },
    { word: 'principle',    load: 0.1 },
    { word: 'abstract',     load: 0.08 },
    { word: 'epistemic',    load: 0.1 },
    { word: 'framework',    load: 0.2 },
    { word: 'theoretical',  load: 0.08 },
  ],
  technical: [
    { word: 'latency',     load: 0.2 },
    { word: 'throughput',  load: 0.22 },
    { word: 'parameter',   load: 0.15 },
    { word: 'gradient',    load: 0.25 },
    { word: 'checkpoint',  load: 0.2 },
    { word: 'validation',  load: 0.15 },
    { word: 'pipeline',    load: 0.3 },
    { word: 'batch',       load: 0.18 },
  ],
};
let readPattern = null, readStep = 0, readTimer = 0, readLoad = 0, readScene = [];
let readDisplay = null; // keeps words on screen after playback ends
function readStory(key) {
  readPattern = readStories[key].slice();
  readDisplay = readPattern;
  readStep = 0; readTimer = 0; readScene.length = 0;
}
function readStop() { readPattern = null; }
function drawRead() {
  const W = 960, H = 340;
  readCtx.fillStyle = themeBg(); readCtx.fillRect(0, 0, W, H);
  if (readPattern) {
    readTimer++;
    if (readTimer >= 20 && readStep < readPattern.length) {
      readTimer = 0;
      const w = readPattern[readStep];
      readLoad = w.load;
      if (w.load >= 0.2) {
        for (let i = 0; i < w.load * 25; i++) {
          readScene.push({
            x: 640 + (Math.random() - 0.5) * 480,
            y: 160 + (Math.random() - 0.5) * 200,
            r: 2 + Math.random() * 5 * w.load,
            hue: 280 + Math.random() * 100,
            life: 1,
          });
        }
      }
      readStep++;
      if (readStep >= readPattern.length) readPattern = null;
    }
  }
  readLoad *= 0.96;
  document.getElementById('read-load').textContent = Math.round(readLoad * 100) + '%';
  // Left: text area
  readCtx.fillStyle = '#16213e';
  readCtx.fillRect(20, 40, 320, 260);
  readCtx.strokeStyle = 'rgba(186,104,200,0.35)'; readCtx.lineWidth = 1;
  readCtx.strokeRect(20, 40, 320, 260);
  readCtx.fillStyle = '#888'; readCtx.font = '11px monospace'; readCtx.textAlign = 'left';
  readCtx.fillText('text input', 28, 32);
  if (readDisplay) {
    for (let i = 0; i < Math.min(readStep, readDisplay.length); i++) {
      const y = 70 + i * 28;
      if (y > 290) break;
      const w = readDisplay[i];
      readCtx.fillStyle = 'rgba(186,104,200,' + (0.3 + w.load * 0.7).toFixed(3) + ')';
      readCtx.font = 'bold 14px monospace';
      readCtx.fillText(w.word, 40, y);
      readCtx.fillStyle = '#666'; readCtx.font = '10px monospace';
      readCtx.fillText('load ' + (w.load * 100).toFixed(0) + '%', 200, y);
    }
  } else {
    readCtx.fillStyle = '#666'; readCtx.font = '11px monospace';
    readCtx.fillText('(pick a text to begin)', 40, 80);
  }
  // Right: visual cortex rendering
  readCtx.fillStyle = '#16213e';
  readCtx.fillRect(360, 40, 580, 260);
  readCtx.strokeStyle = 'rgba(129,199,132,0.35)'; readCtx.lineWidth = 1;
  readCtx.strokeRect(360, 40, 580, 260);
  readCtx.fillStyle = '#888'; readCtx.font = '11px monospace';
  readCtx.fillText('visual cortex rendering', 368, 32);
  // Hint when empty
  if (readScene.length === 0 && !readPattern) {
    readCtx.fillStyle = '#555'; readCtx.font = '11px monospace'; readCtx.textAlign = 'center';
    readCtx.fillText('click a text type to see imagery form', 650, 170);
    readCtx.textAlign = 'left';
  }
  // Draw scene particles within right box
  readScene = readScene.filter(p => p.life > 0.05);
  readScene.forEach(p => {
    p.life *= 0.988;
    if (p.x < 370 || p.x > 930 || p.y < 50 || p.y > 290) return;
    readCtx.fillStyle = 'hsla(' + p.hue + ', 70%, 65%, ' + (p.life * 0.85).toFixed(3) + ')';
    readCtx.beginPath(); readCtx.arc(p.x, p.y, p.r, 0, Math.PI*2); readCtx.fill();
  });
  // Load bar
  readCtx.fillStyle = '#16213e'; readCtx.fillRect(360, 310, 580, 14);
  readCtx.fillStyle = 'rgba(129,199,132,0.85)';
  readCtx.fillRect(360, 310, 580 * readLoad, 14);
  requestAnimationFrame(drawRead);
}
drawRead();

// ═══════════════════════════════════════════════════════════════════════
// Aphantasia ↔ Hyperphantasia
// ═══════════════════════════════════════════════════════════════════════
const aphaCanvas = document.getElementById('apha-canvas');
const aphaCtx = aphaCanvas.getContext('2d');
let aphaPromptObj = null, aphaParticles = [];
document.getElementById('apha-strength').addEventListener('input', (e) => {
  document.getElementById('apha-val').textContent = e.target.value + '%';
});
function aphaPrompt(kind) {
  aphaPromptObj = { kind, t: 0 };
  const strength = parseInt(document.getElementById('apha-strength').value) / 100;
  const count = Math.floor(strength * 300);
  aphaParticles = [];
  const cx = 680, cy = 160;
  for (let i = 0; i < count; i++) {
    let x, y, hue;
    if (kind === 'apple') {
      const a = Math.random() * Math.PI * 2;
      const r = Math.random() * 70;
      x = cx + Math.cos(a) * r;
      y = cy + Math.sin(a) * r;
      hue = 350 + Math.random() * 20;
    } else if (kind === 'face') {
      x = cx + (Math.random() - 0.5) * 120;
      y = cy + (Math.random() - 0.5) * 150;
      hue = 30 + Math.random() * 30;
    } else {
      x = cx + (Math.random() - 0.5) * 300;
      y = cy + (Math.random() - 0.5) * 120;
      hue = 200 + Math.random() * 40;
    }
    aphaParticles.push({ x, y, hue, life: 1, r: 2 + Math.random() * 3 });
  }
}
function drawApha() {
  const W = 960, H = 320;
  aphaCtx.fillStyle = themeBg(); aphaCtx.fillRect(0, 0, W, H);
  const strength = parseInt(document.getElementById('apha-strength').value) / 100;
  // Left: verbal/concept box (always alive)
  aphaCtx.fillStyle = '#16213e';
  aphaCtx.fillRect(40, 40, 280, 240);
  aphaCtx.strokeStyle = 'rgba(186,104,200,0.4)'; aphaCtx.lineWidth = 1;
  aphaCtx.strokeRect(40, 40, 280, 240);
  aphaCtx.fillStyle = '#888'; aphaCtx.font = '11px monospace'; aphaCtx.textAlign = 'left';
  aphaCtx.fillText('concept / verbal channel', 48, 32);
  aphaCtx.fillStyle = 'rgba(186,104,200,0.9)'; aphaCtx.font = 'bold 14px monospace';
  const conceptText = aphaPromptObj ? aphaPromptObj.kind.toUpperCase() : '(prompt to begin)';
  aphaCtx.fillText(conceptText, 56, 80);
  aphaCtx.fillStyle = 'rgba(186,104,200,0.55)'; aphaCtx.font = '11px monospace';
  if (aphaPromptObj) {
    if (aphaPromptObj.kind === 'apple') {
      aphaCtx.fillText('• fruit', 56, 110);
      aphaCtx.fillText('• round', 56, 128);
      aphaCtx.fillText('• red or green', 56, 146);
      aphaCtx.fillText('• crunchy', 56, 164);
      aphaCtx.fillText('• fell from tree', 56, 182);
    } else if (aphaPromptObj.kind === 'face') {
      aphaCtx.fillText('• familiar person', 56, 110);
      aphaCtx.fillText('• emotional association', 56, 128);
      aphaCtx.fillText('• voice memory', 56, 146);
      aphaCtx.fillText('• shared history', 56, 164);
    } else if (aphaPromptObj.kind === 'ocean') {
      aphaCtx.fillText('• vast', 56, 110);
      aphaCtx.fillText('• salty', 56, 128);
      aphaCtx.fillText('• waves', 56, 146);
      aphaCtx.fillText('• blue-green', 56, 164);
    }
  }
  // Right: visual imagery box (strength-dependent)
  aphaCtx.fillStyle = '#16213e';
  aphaCtx.fillRect(360, 40, 560, 240);
  aphaCtx.strokeStyle = 'rgba(129,199,132,0.4)'; aphaCtx.lineWidth = 1;
  aphaCtx.strokeRect(360, 40, 560, 240);
  aphaCtx.fillStyle = '#888'; aphaCtx.fillText('visual imagery (strength-gated)', 368, 32);
  // Clip-like drawing of particles within box
  aphaParticles.forEach(p => {
    p.life *= 0.994;
    if (p.x < 370 || p.x > 910 || p.y < 50 || p.y > 270) return;
    aphaCtx.fillStyle = 'hsla(' + p.hue + ', 70%, 60%, ' + (p.life * strength * 0.9).toFixed(3) + ')';
    aphaCtx.beginPath(); aphaCtx.arc(p.x, p.y, p.r, 0, Math.PI*2); aphaCtx.fill();
  });
  aphaParticles = aphaParticles.filter(p => p.life > 0.1);
  if (strength < 0.1) {
    aphaCtx.fillStyle = 'rgba(229,57,53,0.7)'; aphaCtx.font = '11px monospace'; aphaCtx.textAlign = 'center';
    aphaCtx.fillText('APHANTASIA — no visual render', 640, 160);
  } else if (strength > 0.85) {
    aphaCtx.fillStyle = 'rgba(255,183,77,0.8)'; aphaCtx.font = '11px monospace'; aphaCtx.textAlign = 'center';
    aphaCtx.fillText('HYPERPHANTASIA — imagery near perception strength', 640, 24);
  }
  // Knob label
  aphaCtx.textAlign = 'left'; aphaCtx.fillStyle = '#888';
  aphaCtx.fillText('same network. only the re-render edge weight differs.', 40, 308);
  requestAnimationFrame(drawApha);
}
drawApha();

// ═══════════════════════════════════════════════════════════════════════
// Curiosity ↔ Boredom
// ═══════════════════════════════════════════════════════════════════════
const curiCanvas = document.getElementById('curi-canvas');
const curiCtx = curiCanvas.getContext('2d');
['curi-env','curi-safe'].forEach(id => {
  document.getElementById(id).addEventListener('input', (e) => {
    document.getElementById(id + '-val').textContent = e.target.value + '%';
  });
});
const curiHistory = [];
for (let i = 0; i < 240; i++) curiHistory.push(0.5);
function drawCuri() {
  const W = 960, H = 360;
  curiCtx.fillStyle = themeBg(); curiCtx.fillRect(0, 0, W, H);
  const env = parseInt(document.getElementById('curi-env').value) / 100;
  const safe = parseInt(document.getElementById('curi-safe').value) / 100;
  const setpoint = 0.5;
  const diff = env - setpoint;
  curiHistory.push(env); curiHistory.shift();
  // State label
  let state = 'satisfied', col = 'var(--accent2)';
  if (env < 0.3) { state = 'BOREDOM (pressure rising)'; col = 'var(--warn)'; }
  else if (env > 0.75 && safe > 0.6) { state = 'DELIGHT'; col = 'var(--accent2)'; }
  else if (env > 0.75 && safe < 0.4) { state = 'ANXIETY'; col = '#e53935'; }
  else if (env > 0.55 && safe > 0.5) { state = 'CURIOSITY'; col = 'var(--accent2)'; }
  else if (env >= 0.3 && env <= 0.55) { state = 'satisfied'; col = 'var(--accent2)'; }
  const stateEl = document.getElementById('curi-state');
  stateEl.textContent = state; stateEl.style.color = col;
  // Draw setpoint band
  const centerY = H/2;
  const bandH = 50;
  curiCtx.fillStyle = 'rgba(129,199,132,0.08)';
  curiCtx.fillRect(0, centerY - bandH/2, W, bandH);
  curiCtx.strokeStyle = 'rgba(129,199,132,0.4)'; curiCtx.lineWidth = 1;
  curiCtx.setLineDash([4,4]);
  curiCtx.beginPath(); curiCtx.moveTo(0, centerY); curiCtx.lineTo(W, centerY); curiCtx.stroke();
  curiCtx.setLineDash([]);
  curiCtx.fillStyle = 'rgba(129,199,132,0.7)'; curiCtx.font = '11px monospace'; curiCtx.textAlign = 'left';
  curiCtx.fillText('setpoint — target novelty intake', 16, centerY - bandH/2 - 6);
  // History line
  curiCtx.strokeStyle = 'rgba(186,104,200,0.85)'; curiCtx.lineWidth = 2;
  curiCtx.beginPath();
  curiHistory.forEach((v, i) => {
    const x = (i / 240) * W;
    const y = H - v * (H - 60) - 30;
    if (i === 0) curiCtx.moveTo(x, y); else curiCtx.lineTo(x, y);
  });
  curiCtx.stroke();
  // Threat tint when unsafe & above setpoint
  if (env > 0.5 && safe < 0.5) {
    curiCtx.fillStyle = 'rgba(229,57,53,' + ((1 - safe) * 0.15).toFixed(3) + ')';
    curiCtx.fillRect(0, 0, W, H);
  }
  // Zone labels
  curiCtx.font = '11px monospace'; curiCtx.textAlign = 'right'; curiCtx.fillStyle = 'rgba(229,57,53,0.4)';
  curiCtx.fillText('OVERLOAD / ANXIETY', W - 20, 24);
  curiCtx.textAlign = 'right'; curiCtx.fillStyle = 'rgba(120,120,120,0.5)';
  curiCtx.fillText('BOREDOM', W - 20, H - 12);
  // Pressure gauge
  const pressure = Math.max(0, setpoint - env) * 2;
  curiCtx.fillStyle = '#888'; curiCtx.textAlign = 'left';
  curiCtx.fillText('boredom pressure', 20, 28);
  curiCtx.fillStyle = '#16213e'; curiCtx.fillRect(20, 36, 200, 10);
  curiCtx.fillStyle = 'rgba(255,183,77,0.85)'; curiCtx.fillRect(20, 36, 200 * Math.min(1, pressure), 10);
  requestAnimationFrame(drawCuri);
}
drawCuri();

// ═══════════════════════════════════════════════════════════════════════
// PEP ↔ Axona Bridge (client)
// ═══════════════════════════════════════════════════════════════════════
let bridgeLastEvents = [];
let bridgeSendThrottle = {};
function pepSend(type, payload) {
  // Throttle to at most once per type per 800ms to avoid spamming
  const now = Date.now();
  if (bridgeSendThrottle[type] && now - bridgeSendThrottle[type] < 800) return;
  bridgeSendThrottle[type] = now;
  try {
    fetch('/axona/event', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type, source: 'axona', payload: payload || {} }),
    }).catch(() => {}); // swallow network errors silently
  } catch (e) {}
}
window.pepSend = pepSend;
function bridgeSendPing() {
  pepSend('ping', { from: 'user', t: Date.now() });
}
function bridgeClear() {
  document.getElementById('bridge-log').innerHTML = '<span style="color:var(--dim)">cleared (PEP still has the server-side copy)</span>';
}
function bridgeFmtTime(t) {
  const d = new Date(t * 1000);
  return d.toTimeString().slice(0, 8);
}
function bridgeRenderEvents(items) {
  const log = document.getElementById('bridge-log');
  if (!log || !items || !items.length) return;
  const reversed = items.slice().reverse();
  log.innerHTML = reversed.map(e => {
    const payload = JSON.stringify(e.payload || {}).replace(/</g, '&lt;');
    return '<div style="margin-bottom:3px">' +
      '<span style="color:var(--dim)">' + bridgeFmtTime(e.t) + '</span> ' +
      '<span style="color:var(--accent)">' + (e.type || 'event') + '</span>' +
      ' <span style="color:var(--dim)">' + payload + '</span>' +
      '</div>';
  }).join('');
}
function bridgeRenderLingora(items) {
  const log = document.getElementById('bridge-lingora-log');
  if (!log) return;
  if (!items || !items.length) {
    log.innerHTML = '<span style="color:var(--dim)">no lingora events yet…</span>';
    return;
  }
  log.innerHTML = items.slice().reverse().map(e => {
    const payload = JSON.stringify(e.payload || {}).replace(/</g, '&lt;');
    return '<div style="margin-bottom:3px">' +
      '<span style="color:var(--dim)">' + bridgeFmtTime(e.t) + '</span> ' +
      '<span style="color:var(--accent2)">' + (e.type || 'event') + '</span>' +
      ' <span style="color:var(--dim)">' + payload + '</span>' +
      '</div>';
  }).join('');
}
async function bridgePoll() {
  try {
    const [stateRes, eventsRes, lingRes] = await Promise.all([
      fetch('/axona/pep-state'),
      fetch('/axona/events?limit=40'),
      fetch('/axona/lingora-events?limit=40'),
    ]);
    if (stateRes.ok) {
      const s = await stateRes.json();
      const badge = document.getElementById('pep-link-label');
      const dot = document.getElementById('pep-link-dot');
      badge.textContent = 'PEP: ' + (s.llm || 'unknown') + ' · A' + (s.axona_events || 0) + ' · L' + (s.lingora_events || 0);
      dot.style.background = 'var(--accent2)';
      const set = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = v; };
      set('bridge-connected', 'yes');
      set('bridge-llm', s.llm || '—');
      set('bridge-emb', s.embeddings || '—');
      set('bridge-runs', s.runs_recent);
      set('bridge-evcount', s.axona_events);
      set('bridge-lingora-count', s.lingora_events);
      if (s.latest_run) {
        set('bridge-latest-id', s.latest_run.id || '—');
        set('bridge-latest-input', s.latest_run.user_input || '—');
      }
      if (s.lingora_latest) set('bridge-lingora-latest', s.lingora_latest.type || '—');
    }
    if (eventsRes.ok) {
      const data = await eventsRes.json();
      bridgeLastEvents = data.items || [];
      bridgeRenderEvents(bridgeLastEvents);
    }
    if (lingRes.ok) {
      const data = await lingRes.json();
      bridgeRenderLingora(data.items || []);
    }
  } catch (e) {
    const badge = document.getElementById('pep-link-label');
    const dot = document.getElementById('pep-link-dot');
    if (badge) badge.textContent = 'PEP: offline';
    if (dot) dot.style.background = '#e53935';
    const el = document.getElementById('bridge-connected');
    if (el) el.textContent = 'no';
  }
}
bridgePoll();
setInterval(bridgePoll, 2500);

// ─── Wire key canvas actions to post cognitive events to PEP ───
// Keep the original handlers working by wrapping them.
(function wirePepEvents() {
  const wrap = (name, type, payloadFn) => {
    const orig = window[name];
    if (typeof orig !== 'function') return;
    window[name] = function(...args) {
      try { pepSend(type, payloadFn ? payloadFn(...args) : {}); } catch (e) {}
      return orig.apply(this, args);
    };
  };
  wrap('injectBelief',    'belief.inject',    () => ({}));
  wrap('predSurprise',    'prediction.surprise_injected', () => ({}));
  wrap('attnReset',       'attention.reset',  () => ({}));
  wrap('sleepNight',      'sleep.begin',      () => ({}));
  wrap('sleepAddDay',     'sleep.day_added',  () => ({}));
  wrap('traumaActivate',  'trauma.activation',() => ({}));
  wrap('traumaTherapy',   'trauma.therapy_step', () => ({}));
  wrap('addictPulse',     'addiction.seek',   () => ({ gain: parseInt(document.getElementById('addict-gain').value) / 100 }));
  wrap('selfDestabilize', 'self.destabilize', (k) => ({ mode: k }));
  wrap('selfRestore',     'self.restore',     () => ({}));
  wrap('hallucMute',      'hallucination.mute', () => ({}));
  wrap('hallucRestore',   'hallucination.restore', () => ({}));
  wrap('humorPlay',       'humor.play',       (ctx) => ({ context: ctx }));
  wrap('musicPlay',       'music.play',       (k) => ({ pattern: k }));
  wrap('readStory',       'reading.play',     (k) => ({ style: k }));
  wrap('metaMap',         'metaphor.map',     (k) => ({ metaphor: k }));
  wrap('dejaPartial',     'deja_vu.partial_match', () => ({}));
  wrap('griefLose',       'grief.lost_node',  () => ({}));
  wrap('griefStep',       'grief.rewire_step',() => ({}));
  wrap('helpTry',         'helplessness.attempt', () => ({ world: parseInt(document.getElementById('help-world').value) / 100 }));
  wrap('constrToggle',    'creativity.toggle_constraint', () => ({}));
  wrap('wanderRelease',   'wander.release',   () => ({}));
  wrap('pygSet',          'pygmalion.expectation', (v) => ({ value: v }));
})();

// ═══════════════════════════════════════════════════════════════════════
// Two-System Thinking
// ═══════════════════════════════════════════════════════════════════════
const twosysCanvas = document.getElementById('twosys-canvas');
const twosysCtx = twosysCanvas.getContext('2d');
let twosysS1 = 0.1, twosysS2 = 0.1, twosysActive = null, twosysTimer = 0, twosysAnswer = '';
function twosysInput(kind) {
  twosysActive = kind; twosysTimer = 0; twosysAnswer = '';
  if (kind === 'easy') { twosysS1 = 1; twosysS2 = 0.1; twosysAnswer = '2'; }
  else if (kind === 'hard') { twosysS1 = 0.2; twosysS2 = 0.1; }
  else if (kind === 'trap') { twosysS1 = 0.9; twosysS2 = 0.1; twosysAnswer = '10¢ (wrong)'; }
}
function twosysReset() { twosysActive = null; twosysS1 = 0.1; twosysS2 = 0.1; twosysAnswer = ''; }
function drawTwosys() {
  const W = 960, H = 320;
  twosysCtx.fillStyle = themeBg(); twosysCtx.fillRect(0, 0, W, H);
  if (twosysActive === 'hard' || twosysActive === 'trap') {
    twosysTimer++;
    if (twosysActive === 'hard' && twosysTimer > 30) {
      twosysS2 = Math.min(1, twosysS2 + 0.01);
      twosysS1 *= 0.99;
      if (twosysS2 > 0.95) twosysAnswer = '408';
    }
    if (twosysActive === 'trap' && twosysTimer > 90) {
      twosysS2 = Math.min(1, twosysS2 + 0.008);
      if (twosysS2 > 0.9) twosysAnswer = '5¢ (corrected)';
    }
  }
  twosysS1 *= 0.98;
  // Two big boxes
  const s1x = 140, s1y = 80, s1w = 280, s1h = 160;
  const s2x = 540, s2y = 80, s2w = 280, s2h = 160;
  twosysCtx.fillStyle = 'rgba(186,104,200,' + (0.15 + twosysS1 * 0.45).toFixed(3) + ')';
  twosysCtx.fillRect(s1x, s1y, s1w, s1h);
  twosysCtx.strokeStyle = 'rgba(186,104,200,0.85)'; twosysCtx.lineWidth = 1.5;
  twosysCtx.strokeRect(s1x, s1y, s1w, s1h);
  twosysCtx.fillStyle = 'rgba(129,199,132,' + (0.15 + twosysS2 * 0.45).toFixed(3) + ')';
  twosysCtx.fillRect(s2x, s2y, s2w, s2h);
  twosysCtx.strokeStyle = 'rgba(129,199,132,0.85)'; twosysCtx.strokeRect(s2x, s2y, s2w, s2h);
  twosysCtx.font = 'bold 14px monospace'; twosysCtx.textAlign = 'center';
  twosysCtx.fillStyle = '#e0e0e0';
  twosysCtx.fillText('SYSTEM 1', s1x + s1w/2, s1y + 26);
  twosysCtx.fillText('SYSTEM 2', s2x + s2w/2, s2y + 26);
  twosysCtx.font = '11px monospace'; twosysCtx.fillStyle = '#aaa';
  twosysCtx.fillText('fast · parallel · intuitive', s1x + s1w/2, s1y + 46);
  twosysCtx.fillText('slow · serial · deliberate', s2x + s2w/2, s2y + 46);
  twosysCtx.font = 'bold 18px monospace'; twosysCtx.fillStyle = '#fff';
  twosysCtx.fillText(twosysAnswer || '—', s1x + s1w/2, s1y + s1h/2 + 20);
  if (twosysActive === 'hard') twosysCtx.fillText((twosysAnswer || '...'), s2x + s2w/2, s2y + s2h/2 + 20);
  if (twosysActive === 'trap') twosysCtx.fillText((twosysS2 > 0.9 ? '5¢' : '...'), s2x + s2w/2, s2y + s2h/2 + 20);
  // Budget bar
  twosysCtx.fillStyle = '#888'; twosysCtx.font = '11px monospace'; twosysCtx.textAlign = 'left';
  twosysCtx.fillText('activation budget', 40, 280);
  const total = 880;
  twosysCtx.fillStyle = '#16213e'; twosysCtx.fillRect(40, 290, total, 14);
  const s1w2 = total * (twosysS1 / (twosysS1 + twosysS2 + 0.001));
  twosysCtx.fillStyle = 'rgba(186,104,200,0.85)'; twosysCtx.fillRect(40, 290, s1w2, 14);
  twosysCtx.fillStyle = 'rgba(129,199,132,0.85)'; twosysCtx.fillRect(40 + s1w2, 290, total - s1w2, 14);
  requestAnimationFrame(drawTwosys);
}
drawTwosys();

// ═══════════════════════════════════════════════════════════════════════
// Chunking
// ═══════════════════════════════════════════════════════════════════════
const chunkCanvas = document.getElementById('chunk-canvas');
const chunkCtx = chunkCanvas.getContext('2d');
let chunkMode = 'raw';
const chunkItems = ['H','G','T','V','F','B','I','C','I','A','P','C'];
const chunkGroups = [['H','G','T','V'],['F','B','I'],['C','I','A'],['P','C']];
function chunkShow(mode) { chunkMode = mode; }
function drawChunk() {
  const W = 960, H = 300;
  chunkCtx.fillStyle = themeBg(); chunkCtx.fillRect(0, 0, W, H);
  chunkCtx.font = 'bold 22px monospace'; chunkCtx.textAlign = 'center';
  if (chunkMode === 'raw') {
    for (let i = 0; i < chunkItems.length; i++) {
      const x = 80 + i * 72;
      chunkCtx.fillStyle = 'rgba(186,104,200,0.55)';
      chunkCtx.beginPath(); chunkCtx.arc(x, 110, 24, 0, Math.PI*2); chunkCtx.fill();
      chunkCtx.strokeStyle = 'rgba(186,104,200,0.85)'; chunkCtx.lineWidth = 1.5; chunkCtx.stroke();
      chunkCtx.fillStyle = '#fff'; chunkCtx.fillText(chunkItems[i], x, 118);
    }
    chunkCtx.font = '12px monospace'; chunkCtx.fillStyle = '#aaa';
    chunkCtx.fillText('12 items · far above working-memory capacity (~4)', W/2, 190);
    chunkCtx.fillStyle = 'rgba(255,183,77,0.9)';
    chunkCtx.fillText('load ~12 / 4 — OVERFLOW', W/2, 216);
  } else if (chunkMode === 'chunked') {
    let offset = 80;
    const colors = ['255,183,77','129,199,132','79,195,247','186,104,200'];
    chunkGroups.forEach((g, gi) => {
      const w = g.length * 50;
      chunkCtx.strokeStyle = 'rgba(' + colors[gi] + ',0.9)'; chunkCtx.lineWidth = 2;
      chunkCtx.strokeRect(offset - 10, 80, w + 12, 80);
      g.forEach((c, i) => {
        chunkCtx.fillStyle = 'rgba(' + colors[gi] + ',0.45)';
        chunkCtx.beginPath(); chunkCtx.arc(offset + i * 50 + 15, 120, 18, 0, Math.PI*2); chunkCtx.fill();
        chunkCtx.fillStyle = '#fff'; chunkCtx.font = 'bold 16px monospace';
        chunkCtx.fillText(c, offset + i * 50 + 15, 126);
      });
      chunkCtx.fillStyle = 'rgba(' + colors[gi] + ',0.95)'; chunkCtx.font = 'bold 14px monospace';
      chunkCtx.fillText(g.join(''), offset + w/2 - 10, 190);
      offset += w + 48;
    });
    chunkCtx.font = '12px monospace'; chunkCtx.fillStyle = '#aaa';
    chunkCtx.fillText('4 chunks · comfortably within working memory', W/2, 240);
    chunkCtx.fillStyle = 'rgba(129,199,132,0.9)';
    chunkCtx.fillText('load 4 / 4 — FITS', W/2, 262);
  } else {
    // Expert level
    chunkCtx.fillStyle = 'rgba(129,199,132,0.35)';
    chunkCtx.beginPath(); chunkCtx.arc(W/2, 130, 70, 0, Math.PI*2); chunkCtx.fill();
    chunkCtx.strokeStyle = 'rgba(129,199,132,0.9)'; chunkCtx.lineWidth = 2; chunkCtx.stroke();
    chunkCtx.fillStyle = '#fff'; chunkCtx.font = 'bold 14px monospace';
    chunkCtx.fillText('"American media acronyms"', W/2, 130);
    chunkCtx.font = '11px monospace'; chunkCtx.fillStyle = '#aaa';
    chunkCtx.fillText('one chunk · eleven working-memory slots free', W/2, 230);
    chunkCtx.fillStyle = 'rgba(129,199,132,0.9)';
    chunkCtx.fillText('load 1 / 4 — EXPERT', W/2, 252);
  }
  requestAnimationFrame(drawChunk);
}
drawChunk();

// ═══════════════════════════════════════════════════════════════════════
// Synesthesia
// ═══════════════════════════════════════════════════════════════════════
const synCanvas = document.getElementById('syn-canvas');
const synCtx = synCanvas.getContext('2d');
let synMode_ = 'normal';
const synPulses = [];
const synColors = { C: [255,107,107], E: [255,204,77], G: [107,180,255] };
function synMode(m) { synMode_ = m; }
function synTrigger(note) {
  synPulses.push({ note, t: 0, kind: 'sound' });
  if (synMode_ === 'syn') synPulses.push({ note, t: 0, kind: 'color' });
}
function drawSyn() {
  const W = 960, H = 320;
  synCtx.fillStyle = themeBg(); synCtx.fillRect(0, 0, W, H);
  const soundX = 220, colorX = 720, cy = 160;
  synCtx.strokeStyle = 'rgba(186,104,200,0.4)'; synCtx.lineWidth = 2;
  synCtx.beginPath(); synCtx.arc(soundX, cy, 70, 0, Math.PI*2); synCtx.stroke();
  synCtx.fillStyle = '#e0e0e0'; synCtx.font = 'bold 13px monospace'; synCtx.textAlign = 'center';
  synCtx.fillText('SOUND', soundX, cy + 4);
  synCtx.strokeStyle = 'rgba(129,199,132,0.4)';
  synCtx.beginPath(); synCtx.arc(colorX, cy, 70, 0, Math.PI*2); synCtx.stroke();
  synCtx.fillText('COLOR', colorX, cy + 4);
  // Connection: dashed in normal, solid in synesthete
  if (synMode_ === 'syn') {
    synCtx.strokeStyle = 'rgba(186,104,200,0.6)'; synCtx.lineWidth = 2;
    synCtx.beginPath(); synCtx.moveTo(soundX + 70, cy); synCtx.lineTo(colorX - 70, cy); synCtx.stroke();
    synCtx.fillStyle = 'rgba(129,199,132,0.85)'; synCtx.font = '11px monospace';
    synCtx.fillText('cross-modal link (pruning incomplete)', (soundX + colorX) / 2, cy - 90);
  } else {
    synCtx.strokeStyle = 'rgba(229,57,53,0.35)'; synCtx.lineWidth = 1;
    synCtx.setLineDash([4,4]);
    synCtx.beginPath(); synCtx.moveTo(soundX + 70, cy); synCtx.lineTo(colorX - 70, cy); synCtx.stroke();
    synCtx.setLineDash([]);
    synCtx.fillStyle = 'rgba(229,57,53,0.55)'; synCtx.font = '11px monospace';
    synCtx.fillText('suppressed (normal pruning)', (soundX + colorX) / 2, cy - 90);
  }
  for (let i = synPulses.length - 1; i >= 0; i--) {
    const p = synPulses[i];
    p.t += 0.03;
    if (p.t > 1.5) { synPulses.splice(i, 1); continue; }
    const x = (p.kind === 'sound') ? soundX : colorX;
    const r = 8 + p.t * 60;
    const alpha = Math.max(0, 1 - p.t / 1.5);
    const col = p.kind === 'color' ? synColors[p.note].join(',') : '186,104,200';
    synCtx.strokeStyle = 'rgba(' + col + ',' + alpha.toFixed(3) + ')';
    synCtx.lineWidth = 3;
    synCtx.beginPath(); synCtx.arc(x, cy, r, 0, Math.PI*2); synCtx.stroke();
  }
  synCtx.textAlign = 'left'; synCtx.fillStyle = '#888'; synCtx.font = '11px monospace';
  synCtx.fillText('mode: ' + (synMode_ === 'syn' ? 'SYNESTHETE' : 'normal'), 20, 24);
  requestAnimationFrame(drawSyn);
}
drawSyn();

// ═══════════════════════════════════════════════════════════════════════
// Binding Problem
// ═══════════════════════════════════════════════════════════════════════
const bindCanvas = document.getElementById('bind-canvas');
const bindCtx = bindCanvas.getContext('2d');
let bindMode = 'idle', bindT = 0;
function bindFire(mode) { bindMode = mode; bindT = 0; }
function bindReset() { bindMode = 'idle'; bindT = 0; }
function drawBind() {
  const W = 960, H = 340;
  bindCtx.fillStyle = themeBg(); bindCtx.fillRect(0, 0, W, H);
  if (bindMode !== 'idle') bindT = Math.min(1.5, bindT + 0.015);
  const features = [
    { label: 'color',    x: 140, y: 80 },
    { label: 'shape',    x: 140, y: 150 },
    { label: 'motion',   x: 140, y: 220 },
    { label: 'sound',    x: 140, y: 290 },
  ];
  const bindCenter = { x: 620, y: 170 };
  features.forEach(f => {
    const a = Math.min(1, bindT * 2);
    bindCtx.fillStyle = 'rgba(186,104,200,' + (0.3 + a * 0.5).toFixed(3) + ')';
    bindCtx.beginPath(); bindCtx.arc(f.x, f.y, 22, 0, Math.PI*2); bindCtx.fill();
    bindCtx.fillStyle = '#e0e0e0'; bindCtx.font = '11px monospace'; bindCtx.textAlign = 'center';
    bindCtx.fillText(f.label, f.x, f.y + 4);
    // Lines toward binding center
    const lineAlpha = bindMode === 'normal' ? Math.min(0.85, bindT) : (bindMode === 'broken' ? 0.12 : 0);
    bindCtx.strokeStyle = 'rgba(186,104,200,' + lineAlpha.toFixed(3) + ')';
    bindCtx.lineWidth = 1.5;
    if (bindMode === 'broken') { bindCtx.setLineDash([3,4]); }
    bindCtx.beginPath(); bindCtx.moveTo(f.x + 22, f.y); bindCtx.lineTo(bindCenter.x - 50, bindCenter.y); bindCtx.stroke();
    bindCtx.setLineDash([]);
  });
  // Bound percept
  if (bindMode === 'normal' && bindT > 0.7) {
    const alpha = Math.min(1, (bindT - 0.7) * 3);
    const grad = bindCtx.createRadialGradient(bindCenter.x, bindCenter.y, 0, bindCenter.x, bindCenter.y, 120);
    grad.addColorStop(0, 'rgba(129,199,132,' + (0.35 * alpha).toFixed(3) + ')');
    grad.addColorStop(1, 'rgba(129,199,132,0)');
    bindCtx.fillStyle = grad;
    bindCtx.fillRect(bindCenter.x - 120, bindCenter.y - 120, 240, 240);
    bindCtx.strokeStyle = 'rgba(129,199,132,' + alpha.toFixed(3) + ')';
    bindCtx.lineWidth = 3;
    bindCtx.beginPath(); bindCtx.arc(bindCenter.x, bindCenter.y, 70, 0, Math.PI*2); bindCtx.stroke();
    bindCtx.fillStyle = '#fff'; bindCtx.font = 'bold 14px monospace'; bindCtx.textAlign = 'center';
    bindCtx.fillText('"red ball', bindCenter.x, bindCenter.y - 8);
    bindCtx.fillText('bouncing"', bindCenter.x, bindCenter.y + 10);
  } else if (bindMode === 'broken' && bindT > 0.4) {
    bindCtx.fillStyle = 'rgba(229,57,53,0.85)'; bindCtx.font = '12px monospace'; bindCtx.textAlign = 'center';
    bindCtx.fillText('BINDING FAILED', bindCenter.x, bindCenter.y - 20);
    bindCtx.fillStyle = '#aaa'; bindCtx.font = '10px monospace';
    bindCtx.fillText('features present', bindCenter.x, bindCenter.y);
    bindCtx.fillText('but no unified percept', bindCenter.x, bindCenter.y + 15);
  } else if (bindMode === 'idle') {
    bindCtx.fillStyle = '#666'; bindCtx.font = '11px monospace'; bindCtx.textAlign = 'center';
    bindCtx.fillText('(press a button)', bindCenter.x, bindCenter.y);
  }
  requestAnimationFrame(drawBind);
}
drawBind();

// ═══════════════════════════════════════════════════════════════════════
// Intuition
// ═══════════════════════════════════════════════════════════════════════
const intuCanvas = document.getElementById('intu-canvas');
const intuCtx = intuCanvas.getContext('2d');
let intuLevel = 0, intuConscious = false;
function intuExpose() {
  intuLevel = Math.min(1, intuLevel + 0.08 + Math.random() * 0.04);
  if (intuLevel > 0.7) intuConscious = true;
}
function intuReset() { intuLevel = 0; intuConscious = false; }
function drawIntu() {
  const W = 960, H = 320;
  intuCtx.fillStyle = themeBg(); intuCtx.fillRect(0, 0, W, H);
  intuLevel *= 0.9985;
  const threshold = 0.7;
  const thresholdY = H - (threshold * (H - 80) + 40);
  intuCtx.strokeStyle = 'rgba(255,183,77,0.65)'; intuCtx.lineWidth = 1.5;
  intuCtx.setLineDash([5,5]);
  intuCtx.beginPath(); intuCtx.moveTo(40, thresholdY); intuCtx.lineTo(W - 40, thresholdY); intuCtx.stroke();
  intuCtx.setLineDash([]);
  intuCtx.fillStyle = 'rgba(255,183,77,0.9)'; intuCtx.font = '11px monospace'; intuCtx.textAlign = 'right';
  intuCtx.fillText('conscious threshold', W - 50, thresholdY - 5);
  // Level bar
  const barY = H - (intuLevel * (H - 80) + 40);
  const grad = intuCtx.createLinearGradient(0, H - 40, 0, barY);
  grad.addColorStop(0, 'rgba(186,104,200,0.8)');
  grad.addColorStop(1, 'rgba(186,104,200,0.15)');
  intuCtx.fillStyle = grad;
  intuCtx.fillRect(W/2 - 100, barY, 200, H - 40 - barY);
  intuCtx.strokeStyle = 'rgba(186,104,200,0.85)'; intuCtx.lineWidth = 1.5;
  intuCtx.strokeRect(W/2 - 100, barY, 200, H - 40 - barY);
  intuCtx.fillStyle = '#aaa'; intuCtx.textAlign = 'center'; intuCtx.font = '11px monospace';
  intuCtx.fillText('subliminal match strength', W/2, H - 18);
  if (intuConscious) {
    intuCtx.fillStyle = 'rgba(129,199,132,0.95)'; intuCtx.font = 'bold 14px monospace';
    intuCtx.fillText('◉ "I just know"', W/2, barY - 16);
  }
  document.getElementById('intu-level').textContent = intuLevel.toFixed(2);
  document.getElementById('intu-con').textContent = intuConscious ? 'yes' : 'no';
  if (intuLevel < 0.15) intuConscious = false;
  requestAnimationFrame(drawIntu);
}
drawIntu();

// ═══════════════════════════════════════════════════════════════════════
// Priming
// ═══════════════════════════════════════════════════════════════════════
const primeCanvas = document.getElementById('prime-canvas');
const primeCtx = primeCanvas.getContext('2d');
let primeCurrent = null, primeShown = false, primeRiver = 0.5, primeMoney = 0.5;
function primeSet(p) {
  primeCurrent = p;
  primeShown = false;
  if (p === 'river') { primeRiver = 0.95; primeMoney = 0.15; }
  else if (p === 'money') { primeMoney = 0.95; primeRiver = 0.15; }
  else { primeRiver = 0.5; primeMoney = 0.5; }
}
function primeAmbig() { primeShown = true; }
function drawPrime() {
  const W = 960, H = 300;
  primeCtx.fillStyle = themeBg(); primeCtx.fillRect(0, 0, W, H);
  primeCtx.font = 'bold 28px monospace'; primeCtx.textAlign = 'center'; primeCtx.fillStyle = '#fff';
  primeCtx.fillText('BANK', W/2, 80);
  primeCtx.font = '11px monospace'; primeCtx.fillStyle = '#888';
  primeCtx.fillText('ambiguous word', W/2, 100);
  // Two candidate interpretations
  primeCtx.font = '13px monospace';
  primeCtx.fillStyle = 'rgba(79,195,247,' + (0.35 + primeRiver * 0.6).toFixed(3) + ')';
  primeCtx.beginPath(); primeCtx.arc(260, 180, 40 + primeRiver * 20, 0, Math.PI*2); primeCtx.fill();
  primeCtx.fillStyle = '#fff';
  primeCtx.fillText('riverside', 260, 184);
  primeCtx.fillStyle = 'rgba(129,199,132,' + (0.35 + primeMoney * 0.6).toFixed(3) + ')';
  primeCtx.beginPath(); primeCtx.arc(700, 180, 40 + primeMoney * 20, 0, Math.PI*2); primeCtx.fill();
  primeCtx.fillStyle = '#fff';
  primeCtx.fillText('financial', 700, 184);
  // Prime label
  primeCtx.font = '11px monospace'; primeCtx.fillStyle = '#aaa';
  primeCtx.fillText('prime: ' + (primeCurrent || 'none'), W/2, 260);
  if (primeShown) {
    const winner = primeRiver > primeMoney ? 'riverside' : (primeMoney > primeRiver ? 'financial' : 'ambiguous');
    primeCtx.fillStyle = 'rgba(129,199,132,0.9)'; primeCtx.font = 'bold 13px monospace';
    primeCtx.fillText('→ reads as "' + winner + '"', W/2, 280);
  }
  requestAnimationFrame(drawPrime);
}
drawPrime();

// ═══════════════════════════════════════════════════════════════════════
// Autism — High-Precision Priors
// ═══════════════════════════════════════════════════════════════════════
const autismCanvas = document.getElementById('autism-canvas');
const autismCtx = autismCanvas.getContext('2d');
const autismEvents = [];
document.getElementById('autism-prec').addEventListener('input', (e) => {
  document.getElementById('autism-prec-val').textContent = e.target.value + '%';
});
function autismInject() {
  for (let i = 0; i < 8; i++) {
    autismEvents.push({ x: 40 + Math.random() * 880, y: 40 + Math.random() * 240, size: Math.random(), life: 1 });
  }
}
function autismReset() { autismEvents.length = 0; }
function drawAutism() {
  const W = 960, H = 320;
  autismCtx.fillStyle = themeBg(); autismCtx.fillRect(0, 0, W, H);
  const prec = parseInt(document.getElementById('autism-prec').value) / 100;
  // Threshold: at high precision, even small events exceed it
  const thr = 1 - prec;
  let residuals = 0;
  for (let i = autismEvents.length - 1; i >= 0; i--) {
    const e = autismEvents[i];
    e.life *= 0.992;
    if (e.life < 0.08) { autismEvents.splice(i, 1); continue; }
    const isResidual = e.size > thr;
    const col = isResidual ? '255,183,77' : '120,120,120';
    autismCtx.fillStyle = 'rgba(' + col + ',' + (e.life * 0.85).toFixed(3) + ')';
    autismCtx.beginPath(); autismCtx.arc(e.x, e.y, 2 + e.size * 5, 0, Math.PI*2); autismCtx.fill();
    if (isResidual) residuals++;
  }
  autismCtx.font = '11px monospace'; autismCtx.textAlign = 'left'; autismCtx.fillStyle = '#aaa';
  autismCtx.fillText('sensory events · events above precision threshold tag as residuals', 20, 22);
  autismCtx.fillStyle = 'rgba(255,183,77,0.9)';
  autismCtx.fillText('active residuals: ' + residuals, 20, H - 18);
  if (residuals > 30) {
    autismCtx.fillStyle = 'rgba(229,57,53,0.9)'; autismCtx.font = 'bold 12px monospace';
    autismCtx.textAlign = 'center';
    autismCtx.fillText('◉ SENSORY OVERLOAD — high-precision filter is unforgiving', W/2, H - 18);
  }
  requestAnimationFrame(drawAutism);
}
drawAutism();

// ═══════════════════════════════════════════════════════════════════════
// Habit Formation
// ═══════════════════════════════════════════════════════════════════════
const habitCanvas = document.getElementById('habit-canvas');
const habitCtx = habitCanvas.getContext('2d');
let habitReps = 0, habitWeight = 0;
const habitHistory = [];
function habitRepeat() {
  habitReps++;
  // Sigmoid-ish growth
  const k = 0.04;
  habitWeight = 1 / (1 + Math.exp(-k * (habitReps - 66)));
  habitHistory.push({ r: habitReps, w: habitWeight });
  if (habitHistory.length > 200) habitHistory.shift();
  document.getElementById('habit-reps').textContent = habitReps;
  document.getElementById('habit-weight').textContent = habitWeight.toFixed(2);
  document.getElementById('habit-status').textContent = habitWeight > 0.85 ? 'automatic' : (habitWeight > 0.5 ? 'forming' : 'effortful');
}
function habitReset() {
  habitReps = 0; habitWeight = 0; habitHistory.length = 0;
  document.getElementById('habit-reps').textContent = '0';
  document.getElementById('habit-weight').textContent = '0.00';
  document.getElementById('habit-status').textContent = 'effortful';
}
function drawHabit() {
  const W = 960, H = 320;
  habitCtx.fillStyle = themeBg(); habitCtx.fillRect(0, 0, W, H);
  // Threshold line
  const thrY = H - 60 - 0.85 * (H - 120);
  habitCtx.strokeStyle = 'rgba(129,199,132,0.5)'; habitCtx.lineWidth = 1.5;
  habitCtx.setLineDash([5,5]);
  habitCtx.beginPath(); habitCtx.moveTo(60, thrY); habitCtx.lineTo(W - 20, thrY); habitCtx.stroke();
  habitCtx.setLineDash([]);
  habitCtx.font = '11px monospace'; habitCtx.fillStyle = 'rgba(129,199,132,0.9)'; habitCtx.textAlign = 'right';
  habitCtx.fillText('automaticity threshold', W - 30, thrY - 5);
  // Axes
  habitCtx.strokeStyle = 'rgba(186,104,200,0.3)'; habitCtx.lineWidth = 1;
  habitCtx.beginPath(); habitCtx.moveTo(60, 40); habitCtx.lineTo(60, H - 60); habitCtx.lineTo(W - 20, H - 60); habitCtx.stroke();
  habitCtx.fillStyle = '#888'; habitCtx.font = '11px monospace'; habitCtx.textAlign = 'left';
  habitCtx.fillText('weight', 20, 50);
  habitCtx.textAlign = 'right';
  habitCtx.fillText('repetitions →', W - 20, H - 40);
  // Plot
  if (habitHistory.length > 1) {
    habitCtx.strokeStyle = 'rgba(186,104,200,0.95)'; habitCtx.lineWidth = 2.5;
    habitCtx.beginPath();
    habitHistory.forEach((p, i) => {
      const x = 60 + (p.r / 200) * (W - 80);
      const y = H - 60 - p.w * (H - 120);
      if (i === 0) habitCtx.moveTo(x, y); else habitCtx.lineTo(x, y);
    });
    habitCtx.stroke();
    // Current point
    const last = habitHistory[habitHistory.length - 1];
    const lx = 60 + (last.r / 200) * (W - 80);
    const ly = H - 60 - last.w * (H - 120);
    habitCtx.fillStyle = habitWeight > 0.85 ? 'rgba(129,199,132,0.95)' : 'rgba(255,183,77,0.95)';
    habitCtx.beginPath(); habitCtx.arc(lx, ly, 5, 0, Math.PI*2); habitCtx.fill();
  }
  requestAnimationFrame(drawHabit);
}
drawHabit();

// ═══════════════════════════════════════════════════════════════════════
// Confirmation Bias
// ═══════════════════════════════════════════════════════════════════════
const confirmCanvas = document.getElementById('confirm-canvas');
const confirmCtx = confirmCanvas.getContext('2d');
let confirmPrior = 'neutral';
const confirmEncoded = [];
const confirmRejected = [];
function confirmSet(p) { confirmPrior = p; }
function confirmStream() {
  for (let i = 0; i < 20; i++) {
    const evidence = Math.random() < 0.5 ? 'pos' : 'neg';
    const x = 100 + Math.random() * 300;
    const y = 80 + Math.random() * 200;
    let accept = true;
    if (confirmPrior === 'positive' && evidence === 'neg') accept = Math.random() < 0.2;
    if (confirmPrior === 'negative' && evidence === 'pos') accept = Math.random() < 0.2;
    if (accept) {
      confirmEncoded.push({ x: 560 + Math.random() * 340, y: 80 + Math.random() * 200, kind: evidence, life: 1 });
    } else {
      confirmRejected.push({ sx: x, sy: y, life: 1 });
    }
  }
}
function confirmReset() { confirmEncoded.length = 0; confirmRejected.length = 0; confirmPrior = 'neutral'; }
function drawConfirm() {
  const W = 960, H = 340;
  confirmCtx.fillStyle = themeBg(); confirmCtx.fillRect(0, 0, W, H);
  // Labels
  confirmCtx.font = '11px monospace'; confirmCtx.textAlign = 'left'; confirmCtx.fillStyle = '#aaa';
  confirmCtx.fillText('raw evidence stream', 100, 50);
  confirmCtx.fillText('prior filter: ' + confirmPrior, 430, 50);
  confirmCtx.fillText('encoded memory', 560, 50);
  // Prior filter box
  confirmCtx.strokeStyle = 'rgba(255,183,77,0.6)';
  confirmCtx.lineWidth = 2;
  confirmCtx.strokeRect(430, 70, 110, 220);
  // Stream box
  confirmCtx.strokeStyle = 'rgba(186,104,200,0.3)';
  confirmCtx.strokeRect(60, 70, 360, 220);
  // Memory box
  confirmCtx.strokeStyle = 'rgba(129,199,132,0.6)';
  confirmCtx.strokeRect(550, 70, 380, 220);
  // Rejected particles in stream, fading
  for (let i = confirmRejected.length - 1; i >= 0; i--) {
    const r = confirmRejected[i];
    r.life *= 0.97;
    if (r.life < 0.05) { confirmRejected.splice(i, 1); continue; }
    confirmCtx.fillStyle = 'rgba(229,57,53,' + (r.life * 0.6).toFixed(3) + ')';
    confirmCtx.beginPath(); confirmCtx.arc(r.sx, r.sy, 3, 0, Math.PI*2); confirmCtx.fill();
  }
  confirmEncoded.forEach(p => {
    p.life *= 0.9995;
    const col = p.kind === 'pos' ? '129,199,132' : '229,57,53';
    confirmCtx.fillStyle = 'rgba(' + col + ',' + (p.life * 0.85).toFixed(3) + ')';
    confirmCtx.beginPath(); confirmCtx.arc(p.x, p.y, 3, 0, Math.PI*2); confirmCtx.fill();
  });
  confirmCtx.fillStyle = '#888'; confirmCtx.textAlign = 'center';
  confirmCtx.fillText('encoded: ' + confirmEncoded.length, 740, 305);
  confirmCtx.fillText('rejected: ' + confirmRejected.length, 240, 305);
  requestAnimationFrame(drawConfirm);
}
drawConfirm();

// ═══════════════════════════════════════════════════════════════════════
// Echo Chambers
// ═══════════════════════════════════════════════════════════════════════
const echoCanvas = document.getElementById('echo-canvas');
const echoCtx = echoCanvas.getContext('2d');
const echoNodes = [], echoEdges = [];
let echoInt = 0, echoExt = 0;
function echoInit() {
  echoNodes.length = 0; echoEdges.length = 0;
  echoInt = 0; echoExt = 0;
  const cx = 320, cy = 180;
  // Tight inner cluster
  for (let i = 0; i < 18; i++) {
    const a = (i / 18) * Math.PI * 2;
    const r = 80 + Math.random() * 50;
    echoNodes.push({ x: cx + Math.cos(a) * r, y: cy + Math.sin(a) * r, belief: 0.2, inner: true });
  }
  // Outer nodes
  for (let i = 0; i < 12; i++) {
    echoNodes.push({ x: 620 + Math.random() * 280, y: 40 + Math.random() * 280, belief: 0.2, inner: false });
  }
  // Dense inner edges
  for (let i = 0; i < 18; i++) for (let j = i + 1; j < 18; j++) {
    if (Math.random() < 0.4) echoEdges.push({ a: i, b: j, inner: true });
  }
  // Sparse outer edges
  for (let i = 18; i < echoNodes.length; i++) for (let j = i + 1; j < echoNodes.length; j++) {
    if (Math.random() < 0.3) echoEdges.push({ a: i, b: j, inner: false });
  }
  document.getElementById('echo-int').textContent = '0';
  document.getElementById('echo-ext').textContent = '0';
}
echoInit();
function echoInjectIn() {
  echoNodes.forEach((n, i) => { if (n.inner) n.belief = Math.min(1, n.belief + 0.35); });
  echoInt++;
  document.getElementById('echo-int').textContent = echoInt;
}
function echoInjectOut() {
  // Outer nodes get it briefly; inner rejects
  echoNodes.forEach((n, i) => { if (!n.inner) n.belief = Math.min(1, n.belief + 0.3); });
  echoExt++;
  document.getElementById('echo-ext').textContent = echoExt;
}
function echoReset() { echoInit(); }
function drawEcho() {
  const W = 960, H = 360;
  echoCtx.fillStyle = themeBg(); echoCtx.fillRect(0, 0, W, H);
  echoNodes.forEach(n => { n.belief *= 0.993; if (n.belief < 0.15) n.belief = 0.15; });
  echoEdges.forEach(e => {
    const a = echoNodes[e.a], b = echoNodes[e.b];
    const heat = Math.max(a.belief, b.belief);
    echoCtx.strokeStyle = 'rgba(186,104,200,' + (0.08 + heat * 0.4).toFixed(3) + ')';
    echoCtx.lineWidth = 0.5 + heat * 1.5;
    echoCtx.beginPath(); echoCtx.moveTo(a.x, a.y); echoCtx.lineTo(b.x, b.y); echoCtx.stroke();
  });
  echoNodes.forEach(n => {
    const r = 4 + n.belief * 10;
    const col = n.inner ? '255,183,77' : '186,104,200';
    echoCtx.fillStyle = 'rgba(' + col + ',' + (0.3 + n.belief * 0.6).toFixed(3) + ')';
    echoCtx.beginPath(); echoCtx.arc(n.x, n.y, r, 0, Math.PI*2); echoCtx.fill();
  });
  echoCtx.font = '11px monospace'; echoCtx.textAlign = 'left'; echoCtx.fillStyle = 'rgba(255,183,77,0.8)';
  echoCtx.fillText('ECHO CHAMBER', 200, 30);
  echoCtx.fillStyle = 'rgba(186,104,200,0.7)';
  echoCtx.fillText('OUTSIDE NETWORK', 700, 30);
  requestAnimationFrame(drawEcho);
}
drawEcho();

// ═══════════════════════════════════════════════════════════════════════
// Nostalgia
// ═══════════════════════════════════════════════════════════════════════
const nostCanvas = document.getElementById('nost-canvas');
const nostCtx = nostCanvas.getContext('2d');
const nostCluster = [];
let nostRecallT = 0;
for (let i = 0; i < 24; i++) {
  const a = Math.random() * Math.PI * 2;
  const r = 30 + Math.random() * 80;
  nostCluster.push({ x: 300 + Math.cos(a) * r, y: 170 + Math.sin(a) * r, act: 0.2 });
}
document.getElementById('nost-mood').addEventListener('input', (e) => {
  document.getElementById('nost-mood-val').textContent = e.target.value + '%';
});
function nostRecall() { nostRecallT = 1; }
function nostReset() { nostCluster.forEach(n => n.act = 0.2); nostRecallT = 0; }
function drawNost() {
  const W = 960, H = 340;
  nostCtx.fillStyle = themeBg(); nostCtx.fillRect(0, 0, W, H);
  const mood = parseInt(document.getElementById('nost-mood').value) / 100;
  nostRecallT *= 0.995;
  nostCluster.forEach(n => {
    n.act = 0.3 + nostRecallT * 0.7 + Math.random() * 0.05;
  });
  // Mood tint: cool blue at low, warm orange at high
  const rCol = Math.round(80 + mood * 175);
  const gCol = Math.round(100 + mood * 80);
  const bCol = Math.round(200 - mood * 120);
  nostCluster.forEach(n => {
    const c = rCol + ',' + gCol + ',' + bCol;
    nostCtx.fillStyle = 'rgba(' + c + ',' + (0.35 + n.act * 0.55).toFixed(3) + ')';
    nostCtx.beginPath(); nostCtx.arc(n.x, n.y, 5 + n.act * 6, 0, Math.PI*2); nostCtx.fill();
  });
  nostCtx.font = '11px monospace'; nostCtx.textAlign = 'left'; nostCtx.fillStyle = '#aaa';
  nostCtx.fillText('memory cluster (fixed)', 220, 30);
  // Mood label
  let feel = 'cold · distant';
  if (mood > 0.35) feel = 'neutral · factual';
  if (mood > 0.6) feel = 'warm · sweet';
  if (mood > 0.85) feel = 'bittersweet · longing';
  if (nostRecallT > 0.5) feel = '(actively recalling) ' + feel;
  nostCtx.fillStyle = 'rgba(' + rCol + ',' + gCol + ',' + bCol + ',0.95)';
  nostCtx.font = 'bold 14px monospace'; nostCtx.textAlign = 'center';
  nostCtx.fillText('felt quality: ' + feel, 620, 180);
  nostCtx.font = '11px monospace'; nostCtx.fillStyle = '#888';
  nostCtx.fillText('same memory, current-mood coloring', 620, 210);
  requestAnimationFrame(drawNost);
}
drawNost();

// ═══════════════════════════════════════════════════════════════════════
// Phantom Limbs
// ═══════════════════════════════════════════════════════════════════════
const phantomCanvas = document.getElementById('phantom-canvas');
const phantomCtx = phantomCanvas.getContext('2d');
let phantomState = 'intact', phantomAct = 0.3, phantomMirrorActive = false;
function phantomAmputate() { phantomState = 'gone'; phantomAct = 0.85; phantomMirrorActive = false; }
function phantomMirror() { phantomMirrorActive = true; }
function phantomReset() { phantomState = 'intact'; phantomAct = 0.3; phantomMirrorActive = false; }
function drawPhantom() {
  const W = 960, H = 360;
  phantomCtx.fillStyle = themeBg(); phantomCtx.fillRect(0, 0, W, H);
  if (phantomMirrorActive) phantomAct *= 0.985;
  else if (phantomState === 'gone') phantomAct = Math.max(0.4, phantomAct - 0.001 + Math.sin(Date.now()*0.003)*0.02);
  // Brain body map
  phantomCtx.fillStyle = 'rgba(79,195,247,0.2)';
  phantomCtx.beginPath(); phantomCtx.ellipse(280, 180, 120, 90, 0, 0, Math.PI*2); phantomCtx.fill();
  phantomCtx.strokeStyle = 'rgba(79,195,247,0.7)'; phantomCtx.lineWidth = 2;
  phantomCtx.beginPath(); phantomCtx.ellipse(280, 180, 120, 90, 0, 0, Math.PI*2); phantomCtx.stroke();
  phantomCtx.fillStyle = '#e0e0e0'; phantomCtx.font = '11px monospace'; phantomCtx.textAlign = 'center';
  phantomCtx.fillText('SOMATOSENSORY CORTEX', 280, 50);
  // Hand node (in brain)
  const handCol = phantomState === 'gone' ? '229,57,53' : '186,104,200';
  const flickerR = 12 + phantomAct * 10 + Math.sin(Date.now()*0.01) * (phantomState === 'gone' ? 3 : 0);
  phantomCtx.fillStyle = 'rgba(' + handCol + ',' + (0.4 + phantomAct * 0.5).toFixed(3) + ')';
  phantomCtx.beginPath(); phantomCtx.arc(260, 200, flickerR, 0, Math.PI*2); phantomCtx.fill();
  phantomCtx.fillStyle = '#fff'; phantomCtx.font = '10px monospace';
  phantomCtx.fillText('hand node', 260, 204);
  // Body/hand on right
  phantomCtx.strokeStyle = 'rgba(186,104,200,0.5)'; phantomCtx.lineWidth = 2;
  phantomCtx.beginPath(); phantomCtx.moveTo(580, 120); phantomCtx.lineTo(580, 280); phantomCtx.stroke();
  phantomCtx.fillStyle = '#e0e0e0'; phantomCtx.font = '11px monospace';
  phantomCtx.fillText('body', 580, 100);
  if (phantomState === 'intact') {
    phantomCtx.fillStyle = 'rgba(186,104,200,0.7)';
    phantomCtx.beginPath(); phantomCtx.arc(660, 180, 24, 0, Math.PI*2); phantomCtx.fill();
    phantomCtx.fillStyle = '#fff'; phantomCtx.fillText('hand', 660, 184);
  } else {
    phantomCtx.strokeStyle = 'rgba(120,120,120,0.5)';
    phantomCtx.setLineDash([3,3]);
    phantomCtx.beginPath(); phantomCtx.arc(660, 180, 24, 0, Math.PI*2); phantomCtx.stroke();
    phantomCtx.setLineDash([]);
    phantomCtx.fillStyle = '#888';
    phantomCtx.fillText('(absent)', 660, 184);
  }
  if (phantomMirrorActive) {
    phantomCtx.fillStyle = 'rgba(129,199,132,0.5)';
    phantomCtx.beginPath(); phantomCtx.arc(810, 180, 22, 0, Math.PI*2); phantomCtx.fill();
    phantomCtx.fillStyle = '#fff'; phantomCtx.font = '10px monospace';
    phantomCtx.fillText('mirror', 810, 184);
    phantomCtx.strokeStyle = 'rgba(129,199,132,0.6)'; phantomCtx.lineWidth = 1;
    phantomCtx.setLineDash([4,4]);
    phantomCtx.beginPath(); phantomCtx.moveTo(790, 180); phantomCtx.lineTo(290, 200); phantomCtx.stroke();
    phantomCtx.setLineDash([]);
  }
  // Edge from hand node to body/mirror
  const tx = phantomMirrorActive ? 810 : 660;
  phantomCtx.strokeStyle = 'rgba(' + handCol + ',' + (0.2 + phantomAct * 0.3).toFixed(3) + ')';
  phantomCtx.lineWidth = 1 + phantomAct * 2;
  if (phantomState === 'gone' && !phantomMirrorActive) phantomCtx.setLineDash([4,4]);
  phantomCtx.beginPath(); phantomCtx.moveTo(285, 200); phantomCtx.lineTo(tx, 180); phantomCtx.stroke();
  phantomCtx.setLineDash([]);
  document.getElementById('phantom-act').textContent = phantomAct.toFixed(2);
  requestAnimationFrame(drawPhantom);
}
drawPhantom();

// ═══════════════════════════════════════════════════════════════════════
// Depression — Flattened Reward Landscape
// ═══════════════════════════════════════════════════════════════════════
const depCanvas = document.getElementById('dep-canvas');
const depCtx = depCanvas.getContext('2d');
let depCursor = 0.2;
document.getElementById('dep-sev').addEventListener('input', (e) => {
  document.getElementById('dep-sev-val').textContent = e.target.value + '%';
});
function depMove() {
  const sev = parseInt(document.getElementById('dep-sev').value) / 100;
  const W = 960;
  // Compute gradient at current position and step toward higher reward
  const f = (x) => Math.exp(-Math.pow((x - 0.2)*3, 2)) * 0.8 + Math.exp(-Math.pow((x - 0.5)*3, 2)) * 1.0 + Math.exp(-Math.pow((x - 0.8)*3, 2)) * 0.6;
  const scale = 1 - sev * 0.97;
  const here = f(depCursor) * scale;
  const right = f(depCursor + 0.01) * scale;
  const grad = (right - here) / 0.01;
  const step = 0.02 * Math.sign(grad);
  if (Math.abs(grad) > 0.005) depCursor = Math.max(0.02, Math.min(0.98, depCursor + step));
}
function depReset() { depCursor = 0.2; document.getElementById('dep-sev').value = 0; document.getElementById('dep-sev-val').textContent = '0%'; }
function drawDep() {
  const W = 960, H = 360;
  depCtx.fillStyle = themeBg(); depCtx.fillRect(0, 0, W, H);
  const sev = parseInt(document.getElementById('dep-sev').value) / 100;
  const scale = 1 - sev * 0.97;
  const f = (x) => (Math.exp(-Math.pow((x - 0.2)*3, 2)) * 0.8 + Math.exp(-Math.pow((x - 0.5)*3, 2)) * 1.0 + Math.exp(-Math.pow((x - 0.8)*3, 2)) * 0.6) * scale;
  depCtx.strokeStyle = 'rgba(186,104,200,0.85)'; depCtx.lineWidth = 2;
  depCtx.beginPath();
  for (let i = 0; i <= 400; i++) {
    const x = i / 400;
    const px = 40 + x * (W - 80);
    const py = H - 60 - f(x) * (H - 120);
    if (i === 0) depCtx.moveTo(px, py); else depCtx.lineTo(px, py);
  }
  depCtx.stroke();
  // Landscape fill
  depCtx.lineTo(W - 40, H - 60); depCtx.lineTo(40, H - 60); depCtx.closePath();
  depCtx.fillStyle = 'rgba(186,104,200,0.15)'; depCtx.fill();
  // Cursor
  const cx = 40 + depCursor * (W - 80);
  const cy = H - 60 - f(depCursor) * (H - 120);
  depCtx.fillStyle = 'rgba(129,199,132,0.9)';
  depCtx.beginPath(); depCtx.arc(cx, cy, 8, 0, Math.PI*2); depCtx.fill();
  // Peak labels
  depCtx.font = '11px monospace'; depCtx.textAlign = 'center'; depCtx.fillStyle = '#888';
  depCtx.fillText('food', 40 + 0.2 * (W - 80), H - 30);
  depCtx.fillText('connection', 40 + 0.5 * (W - 80), H - 30);
  depCtx.fillText('mastery', 40 + 0.8 * (W - 80), H - 30);
  if (sev > 0.85) {
    depCtx.fillStyle = 'rgba(229,57,53,0.9)'; depCtx.font = 'bold 12px monospace';
    depCtx.fillText('◉ LANDSCAPE FLAT — no gradient to follow', W/2, 40);
  }
  requestAnimationFrame(drawDep);
}
drawDep();

// ═══════════════════════════════════════════════════════════════════════
// Memory Reconsolidation
// ═══════════════════════════════════════════════════════════════════════
const reconCanvas = document.getElementById('recon-canvas');
const reconCtx = reconCanvas.getContext('2d');
let reconMem = null, reconT = 0;
function reconEncode() {
  reconMem = { hue: 0, saturation: 0.9 }; // original: red (fear)
}
function reconRecall(ctx) {
  if (!reconMem) return;
  // Shift hue toward context color. Safe = green (120), stressful = red (0)
  const target = ctx === 'safe' ? 120 : 0;
  reconMem.hue += (target - reconMem.hue) * 0.25;
  reconT = 1;
}
function reconReset() { reconMem = null; reconT = 0; }
function drawRecon() {
  const W = 960, H = 360;
  reconCtx.fillStyle = themeBg(); reconCtx.fillRect(0, 0, W, H);
  reconT *= 0.98;
  if (reconMem) {
    const cx = W/2, cy = H/2;
    // Malleable window halo
    if (reconT > 0.05) {
      const halo = reconCtx.createRadialGradient(cx, cy, 0, cx, cy, 180);
      halo.addColorStop(0, 'rgba(255,183,77,' + (reconT * 0.35).toFixed(3) + ')');
      halo.addColorStop(1, 'rgba(255,183,77,0)');
      reconCtx.fillStyle = halo;
      reconCtx.fillRect(cx - 180, cy - 180, 360, 360);
    }
    reconCtx.fillStyle = 'hsla(' + reconMem.hue + ', 70%, 55%, 0.85)';
    reconCtx.beginPath(); reconCtx.arc(cx, cy, 90, 0, Math.PI*2); reconCtx.fill();
    reconCtx.strokeStyle = 'hsla(' + reconMem.hue + ', 70%, 75%, 1)';
    reconCtx.lineWidth = 3;
    reconCtx.stroke();
    reconCtx.fillStyle = '#fff'; reconCtx.font = 'bold 14px monospace'; reconCtx.textAlign = 'center';
    reconCtx.fillText('MEMORY', cx, cy - 5);
    reconCtx.font = '11px monospace';
    reconCtx.fillText('hue: ' + Math.round(reconMem.hue), cx, cy + 12);
    if (reconT > 0.2) {
      reconCtx.fillStyle = 'rgba(255,183,77,0.9)'; reconCtx.font = 'bold 12px monospace';
      reconCtx.fillText('⬤ reconsolidation window OPEN', cx, cy - 120);
    }
  } else {
    reconCtx.fillStyle = '#888'; reconCtx.font = '11px monospace'; reconCtx.textAlign = 'center';
    reconCtx.fillText('(encode a memory to begin)', W/2, H/2);
  }
  requestAnimationFrame(drawRecon);
}
drawRecon();

// ═══════════════════════════════════════════════════════════════════════
// Pain — A Priority Signal, Not an Intensity
// ═══════════════════════════════════════════════════════════════════════
const painCanvas = document.getElementById('pain-canvas');
const painCtx = painCanvas.getContext('2d');
['pain-noc','pain-att','pain-exp','pain-dist'].forEach(id => {
  document.getElementById(id).addEventListener('input', (e) => {
    document.getElementById(id + '-val').textContent = e.target.value;
  });
});
function drawPain() {
  const W = 960, H = 340;
  painCtx.fillStyle = themeBg(); painCtx.fillRect(0, 0, W, H);
  const noc = parseInt(document.getElementById('pain-noc').value) / 100;
  const att = parseInt(document.getElementById('pain-att').value) / 100;
  const expc = parseInt(document.getElementById('pain-exp').value) / 100;
  const dist = parseInt(document.getElementById('pain-dist').value) / 100;
  // Experienced pain: noc × (0.4 + att × 0.8) × (1 + expc × 0.4) × (1 - dist × 0.75)
  const experienced = Math.max(0, Math.min(1, noc * (0.4 + att * 0.8) * (1 + expc * 0.4) * (1 - dist * 0.75)));
  document.getElementById('pain-exp-val-out').textContent = Math.round(experienced * 100);
  // Draw three bars: raw, modulation, experienced
  const y0 = 60;
  painCtx.font = '11px monospace'; painCtx.textAlign = 'left'; painCtx.fillStyle = '#aaa';
  painCtx.fillText('raw nociception input', 40, y0 - 6);
  painCtx.fillStyle = '#16213e'; painCtx.fillRect(40, y0, 880, 22);
  painCtx.fillStyle = 'rgba(255,183,77,0.85)'; painCtx.fillRect(40, y0, 880 * noc, 22);
  const y1 = y0 + 60;
  painCtx.fillStyle = '#aaa';
  painCtx.fillText('modulation (attention × expectation − distraction)', 40, y1 - 6);
  const mod = (0.4 + att * 0.8) * (1 + expc * 0.4) * (1 - dist * 0.75);
  const modBar = Math.max(0, Math.min(1, mod / 1.7));
  painCtx.fillStyle = '#16213e'; painCtx.fillRect(40, y1, 880, 22);
  const modCol = mod > 1 ? '255,107,107' : '129,199,132';
  painCtx.fillStyle = 'rgba(' + modCol + ',0.85)'; painCtx.fillRect(40, y1, 880 * modBar, 22);
  const y2 = y1 + 60;
  painCtx.fillStyle = '#aaa';
  painCtx.fillText('experienced pain (the only thing consciousness sees)', 40, y2 - 6);
  painCtx.fillStyle = '#16213e'; painCtx.fillRect(40, y2, 880, 36);
  const expCol = experienced > 0.7 ? '229,57,53' : (experienced > 0.4 ? '255,183,77' : '129,199,132');
  painCtx.fillStyle = 'rgba(' + expCol + ',0.95)'; painCtx.fillRect(40, y2, 880 * experienced, 36);
  painCtx.fillStyle = '#fff'; painCtx.font = 'bold 14px monospace'; painCtx.textAlign = 'center';
  painCtx.fillText(Math.round(experienced * 100) + ' / 100', 480, y2 + 23);
  if (noc > 0.6 && experienced < 0.3) {
    painCtx.fillStyle = 'rgba(129,199,132,0.9)'; painCtx.font = '11px monospace'; painCtx.textAlign = 'left';
    painCtx.fillText('◉ strong nociception but low experienced pain — distraction / analgesia effect', 40, y2 + 58);
  }
  requestAnimationFrame(drawPain);
}
drawPain();

// ═══════════════════════════════════════════════════════════════════════
// The Interpreter
// ═══════════════════════════════════════════════════════════════════════
const interpCanvas = document.getElementById('interp-canvas');
const interpCtx = interpCanvas.getContext('2d');
let interpAction = null, interpT = 0, interpExplain = '';
const interpExplanations = {
  walk: ['"I needed to stretch my legs."', '"I was thirsty and heading for water."', '"I wanted to look out the window."'],
  laugh: ['"Something struck me as funny."', '"I was remembering a joke."', '"The situation felt absurd."'],
  reach: ['"I was thirsty."', '"I wanted something in my hand."', '"I just felt like it."'],
};
function interpAct(kind) {
  interpAction = kind; interpT = 0;
  const list = interpExplanations[kind];
  interpExplain = list[Math.floor(Math.random() * list.length)];
}
function interpReset() { interpAction = null; interpT = 0; interpExplain = ''; }
function drawInterp() {
  const W = 960, H = 360;
  interpCtx.fillStyle = themeBg(); interpCtx.fillRect(0, 0, W, H);
  if (interpAction) interpT = Math.min(1.6, interpT + 0.015);
  // Two hemispheres
  const rhX = 220, lhX = 720, hemY = 160;
  interpCtx.fillStyle = 'rgba(255,183,77,0.2)';
  interpCtx.beginPath(); interpCtx.ellipse(rhX, hemY, 140, 100, 0, 0, Math.PI*2); interpCtx.fill();
  interpCtx.strokeStyle = 'rgba(255,183,77,0.85)'; interpCtx.lineWidth = 2; interpCtx.stroke();
  interpCtx.fillStyle = 'rgba(186,104,200,0.2)';
  interpCtx.beginPath(); interpCtx.ellipse(lhX, hemY, 140, 100, 0, 0, Math.PI*2); interpCtx.fill();
  interpCtx.strokeStyle = 'rgba(186,104,200,0.85)'; interpCtx.stroke();
  interpCtx.fillStyle = '#e0e0e0'; interpCtx.font = 'bold 14px monospace'; interpCtx.textAlign = 'center';
  interpCtx.fillText('RIGHT HEMISPHERE', rhX, 30);
  interpCtx.fillText('LEFT HEMISPHERE', lhX, 30);
  interpCtx.font = '11px monospace'; interpCtx.fillStyle = '#aaa';
  interpCtx.fillText('received the command', rhX, 50);
  interpCtx.fillText('runs the Interpreter', lhX, 50);
  // Severed callosum
  interpCtx.strokeStyle = 'rgba(229,57,53,0.5)'; interpCtx.lineWidth = 2;
  interpCtx.setLineDash([6,6]);
  interpCtx.beginPath(); interpCtx.moveTo(rhX + 140, hemY); interpCtx.lineTo(lhX - 140, hemY); interpCtx.stroke();
  interpCtx.setLineDash([]);
  interpCtx.fillStyle = 'rgba(229,57,53,0.75)'; interpCtx.font = '10px monospace';
  interpCtx.fillText('(corpus callosum severed)', W/2, hemY - 8);
  if (interpAction) {
    // Command on right
    if (interpT > 0.05) {
      interpCtx.fillStyle = 'rgba(255,183,77,0.9)'; interpCtx.font = 'bold 13px monospace';
      interpCtx.fillText('cmd: "' + interpAction + '"', rhX, hemY + 10);
    }
    // Action happens
    if (interpT > 0.25) {
      interpCtx.fillStyle = '#fff'; interpCtx.font = '12px monospace';
      interpCtx.fillText('→ body acts: ' + interpAction + 's', W/2, hemY + 160);
    }
    // Left hemisphere confabulates
    if (interpT > 0.6) {
      interpCtx.fillStyle = 'rgba(186,104,200,0.95)'; interpCtx.font = 'bold 12px monospace';
      interpCtx.fillText(interpExplain, lhX, hemY + 10);
      interpCtx.fillStyle = 'rgba(186,104,200,0.65)'; interpCtx.font = '10px monospace';
      interpCtx.fillText('(the left never saw the command)', lhX, hemY + 30);
    }
    if (interpT > 1.1) {
      interpCtx.fillStyle = 'rgba(229,57,53,0.9)'; interpCtx.font = 'bold 12px monospace';
      interpCtx.fillText('◉ the explanation is confabulated — and believed', W/2, 340);
    }
  } else {
    interpCtx.fillStyle = '#666'; interpCtx.font = '11px monospace';
    interpCtx.fillText('(flash a command to the right hemisphere)', W/2, 340);
  }
  requestAnimationFrame(drawInterp);
}
drawInterp();

// ═══════════════════════════════════════════════════════════════════════
// Inattentional Blindness
// ═══════════════════════════════════════════════════════════════════════
const inattCanvas = document.getElementById('inatt-canvas');
const inattCtx = inattCanvas.getContext('2d');
let inattMode = 'idle', inattCount = 0, inattT = 0, inattGorilla = null, inattBalls = [];
function inattInitBalls() {
  inattBalls = [];
  for (let i = 0; i < 6; i++) {
    inattBalls.push({
      x: 100 + Math.random() * 760, y: 60 + Math.random() * 240,
      vx: (Math.random() - 0.5) * 3, vy: (Math.random() - 0.5) * 3,
      white: i < 3,
    });
  }
}
function inattTask(kind) {
  inattMode = 'task'; inattCount = 0; inattT = 0;
  inattInitBalls();
  inattGorilla = null;
}
function inattReview() {
  inattMode = 'review';
  const label = inattGorilla && inattGorilla.x > 0 ? 'yes!' : 'no — it was right there';
  document.getElementById('inatt-gorilla').textContent = label;
}
function inattReset() {
  inattMode = 'idle'; inattCount = 0; inattT = 0; inattBalls = []; inattGorilla = null;
  document.getElementById('inatt-count').textContent = '0';
  document.getElementById('inatt-gorilla').textContent = '—';
}
function drawInatt() {
  const W = 960, H = 360;
  inattCtx.fillStyle = themeBg(); inattCtx.fillRect(0, 0, W, H);
  if (inattMode === 'task') {
    inattT++;
    inattBalls.forEach(b => {
      b.x += b.vx; b.y += b.vy;
      if (b.x < 40 || b.x > W - 40) b.vx *= -1;
      if (b.y < 40 || b.y > 300) b.vy *= -1;
    });
    // Count passes (rough: when any two balls pass near each other)
    if (inattT % 30 === 0) {
      inattCount++;
      document.getElementById('inatt-count').textContent = inattCount;
    }
    // Gorilla appears midway and walks across
    if (inattT > 120 && inattT < 280) {
      if (!inattGorilla) inattGorilla = { x: -40, y: 200 };
      inattGorilla.x += 2;
    }
    inattBalls.forEach(b => {
      inattCtx.fillStyle = b.white ? 'rgba(255,255,255,0.9)' : 'rgba(120,120,120,0.9)';
      inattCtx.beginPath(); inattCtx.arc(b.x, b.y, 12, 0, Math.PI*2); inattCtx.fill();
    });
    if (inattGorilla) {
      // Draw a subtle gorilla shape
      inattCtx.fillStyle = 'rgba(186,104,200,0.45)';
      inattCtx.beginPath(); inattCtx.ellipse(inattGorilla.x, inattGorilla.y, 22, 30, 0, 0, Math.PI*2); inattCtx.fill();
      inattCtx.font = '10px monospace'; inattCtx.fillStyle = 'rgba(186,104,200,0.65)';
      inattCtx.textAlign = 'center';
      inattCtx.fillText('🦍', inattGorilla.x, inattGorilla.y + 3);
    }
    inattCtx.fillStyle = '#fff'; inattCtx.font = 'bold 14px monospace'; inattCtx.textAlign = 'left';
    inattCtx.fillText('COUNT THE WHITE-BALL PASSES', 30, 24);
    inattCtx.font = '11px monospace'; inattCtx.fillStyle = '#aaa';
    inattCtx.fillText('focus only on the white balls', 30, 44);
  } else if (inattMode === 'review') {
    // Replay the scene statically with the gorilla prominent
    inattCtx.fillStyle = 'rgba(186,104,200,0.75)';
    inattCtx.beginPath(); inattCtx.ellipse(W/2, 180, 50, 70, 0, 0, Math.PI*2); inattCtx.fill();
    inattCtx.font = '40px monospace'; inattCtx.textAlign = 'center'; inattCtx.fillStyle = '#fff';
    inattCtx.fillText('🦍', W/2, 200);
    inattCtx.font = 'bold 14px monospace';
    inattCtx.fillText('this was in the video the whole time', W/2, 310);
    inattCtx.font = '11px monospace'; inattCtx.fillStyle = '#aaa';
    inattCtx.fillText('if you missed it: attention filtered it out before encoding', W/2, 330);
  } else {
    inattCtx.fillStyle = '#666'; inattCtx.font = '11px monospace'; inattCtx.textAlign = 'center';
    inattCtx.fillText('(press "Start Counting Task")', W/2, H/2);
  }
  requestAnimationFrame(drawInatt);
}
drawInatt();

// ═══════════════════════════════════════════════════════════════════════
// McGurk Effect
// ═══════════════════════════════════════════════════════════════════════
const mcgurkCanvas = document.getElementById('mcgurk-canvas');
const mcgurkCtx = mcgurkCanvas.getContext('2d');
let mcgurkMode = 'idle', mcgurkT = 0;
function mcgurkFire(mode) { mcgurkMode = mode; mcgurkT = 0; }
function mcgurkReset() { mcgurkMode = 'idle'; mcgurkT = 0; }
function drawMcgurk() {
  const W = 960, H = 320;
  mcgurkCtx.fillStyle = themeBg(); mcgurkCtx.fillRect(0, 0, W, H);
  if (mcgurkMode !== 'idle') mcgurkT = Math.min(1.2, mcgurkT + 0.02);
  const ayX = 200, viX = 500, peX = 800, y = 160;
  // Audio
  mcgurkCtx.fillStyle = 'rgba(186,104,200,0.3)';
  mcgurkCtx.beginPath(); mcgurkCtx.arc(ayX, y, 60, 0, Math.PI*2); mcgurkCtx.fill();
  mcgurkCtx.strokeStyle = 'rgba(186,104,200,0.85)'; mcgurkCtx.lineWidth = 2; mcgurkCtx.stroke();
  mcgurkCtx.fillStyle = '#fff'; mcgurkCtx.font = 'bold 14px monospace'; mcgurkCtx.textAlign = 'center';
  mcgurkCtx.fillText('AUDIO', ayX, y - 5);
  // Visual
  mcgurkCtx.fillStyle = 'rgba(79,195,247,0.3)';
  mcgurkCtx.beginPath(); mcgurkCtx.arc(viX, y, 60, 0, Math.PI*2); mcgurkCtx.fill();
  mcgurkCtx.strokeStyle = 'rgba(79,195,247,0.85)'; mcgurkCtx.stroke();
  mcgurkCtx.fillStyle = '#fff';
  mcgurkCtx.fillText('VISUAL', viX, y - 5);
  // Percept
  mcgurkCtx.fillStyle = 'rgba(129,199,132,0.3)';
  mcgurkCtx.beginPath(); mcgurkCtx.arc(peX, y, 60, 0, Math.PI*2); mcgurkCtx.fill();
  mcgurkCtx.strokeStyle = 'rgba(129,199,132,0.85)'; mcgurkCtx.stroke();
  mcgurkCtx.fillStyle = '#fff';
  mcgurkCtx.fillText('PERCEIVED', peX, y - 5);
  // Contents
  let audioText = '—', visualText = '—', perceivedText = '—';
  if (mcgurkMode === 'congruent') { audioText = '"ba"'; visualText = '"ba" lips'; perceivedText = '"ba"'; }
  else if (mcgurkMode === 'illusion') { audioText = '"ba"'; visualText = '"ga" lips'; perceivedText = '"da" !'; }
  else if (mcgurkMode === 'audio-only') { audioText = '"ba"'; visualText = '(none)'; perceivedText = '"ba"'; }
  mcgurkCtx.font = '12px monospace';
  mcgurkCtx.fillText(audioText, ayX, y + 16);
  mcgurkCtx.fillText(visualText, viX, y + 16);
  mcgurkCtx.fillText(perceivedText, peX, y + 16);
  // Edges
  mcgurkCtx.strokeStyle = 'rgba(186,104,200,' + (mcgurkT > 0.3 ? 0.7 : 0.2).toFixed(3) + ')';
  mcgurkCtx.lineWidth = 2;
  mcgurkCtx.beginPath(); mcgurkCtx.moveTo(ayX + 60, y); mcgurkCtx.lineTo(peX - 60, y); mcgurkCtx.stroke();
  if (mcgurkMode !== 'audio-only') {
    mcgurkCtx.strokeStyle = 'rgba(79,195,247,' + (mcgurkT > 0.3 ? 0.7 : 0.2).toFixed(3) + ')';
    mcgurkCtx.beginPath(); mcgurkCtx.moveTo(viX + 60, y); mcgurkCtx.lineTo(peX - 60, y); mcgurkCtx.stroke();
  }
  if (mcgurkMode === 'illusion' && mcgurkT > 0.8) {
    mcgurkCtx.fillStyle = 'rgba(255,183,77,0.95)'; mcgurkCtx.font = 'bold 12px monospace';
    mcgurkCtx.fillText('◉ perceived phoneme is in NEITHER input — brain constructed it', W/2, 280);
  }
  requestAnimationFrame(drawMcgurk);
}
drawMcgurk();

// ═══════════════════════════════════════════════════════════════════════
// Cognitive Dissonance
// ═══════════════════════════════════════════════════════════════════════
const disCanvas = document.getElementById('dis-canvas');
const disCtx = disCanvas.getContext('2d');
let disA = null, disB = null, disResidual = 0, disResolved = false, disResolution = '';
function disAdd(slot, text) {
  if (slot === 'A') disA = text;
  else disB = text;
  disResolved = false;
}
function disResolve() {
  if (!disA || !disB) return;
  disResolved = true;
  const options = [
    '"It was not actually harmful."',
    '"They deserved it."',
    '"Anyone would have done the same."',
    '"I had no choice."',
    '"It was a small thing."',
  ];
  disResolution = options[Math.floor(Math.random() * options.length)];
}
function disReset() { disA = null; disB = null; disResidual = 0; disResolved = false; disResolution = ''; }
function drawDis() {
  const W = 960, H = 360;
  disCtx.fillStyle = themeBg(); disCtx.fillRect(0, 0, W, H);
  const target = (disA && disB && !disResolved) ? 0.95 : 0.1;
  disResidual += (target - disResidual) * 0.04;
  // Belief A
  disCtx.fillStyle = 'rgba(186,104,200,' + (disA ? 0.55 : 0.15).toFixed(3) + ')';
  disCtx.beginPath(); disCtx.arc(220, 140, 60, 0, Math.PI*2); disCtx.fill();
  disCtx.strokeStyle = 'rgba(186,104,200,0.85)'; disCtx.lineWidth = 2; disCtx.stroke();
  disCtx.fillStyle = '#fff'; disCtx.font = '12px monospace'; disCtx.textAlign = 'center';
  if (disA) {
    const lines = disA.split(' ');
    disCtx.fillText(lines.slice(0, 2).join(' '), 220, 135);
    disCtx.fillText(lines.slice(2).join(' '), 220, 152);
  } else {
    disCtx.fillStyle = '#666'; disCtx.fillText('(empty)', 220, 145);
  }
  // Belief B
  disCtx.fillStyle = 'rgba(186,104,200,' + (disB && !disResolved ? 0.55 : 0.15).toFixed(3) + ')';
  disCtx.beginPath(); disCtx.arc(740, 140, 60, 0, Math.PI*2); disCtx.fill();
  disCtx.strokeStyle = 'rgba(186,104,200,0.85)'; disCtx.stroke();
  disCtx.fillStyle = '#fff';
  if (disB && !disResolved) {
    const lines = disB.split(' ');
    disCtx.fillText(lines.slice(0, 3).join(' '), 740, 135);
    disCtx.fillText(lines.slice(3).join(' '), 740, 152);
  } else if (disResolved && disB) {
    disCtx.fillStyle = '#fff'; disCtx.font = '11px monospace';
    const lines = disResolution.split(' ');
    const half = Math.ceil(lines.length / 2);
    disCtx.fillText(lines.slice(0, half).join(' '), 740, 135);
    disCtx.fillText(lines.slice(half).join(' '), 740, 152);
  } else {
    disCtx.fillStyle = '#666'; disCtx.fillText('(empty)', 740, 145);
  }
  // Residual arc
  disCtx.strokeStyle = 'rgba(255,183,77,' + (0.15 + disResidual * 0.7).toFixed(3) + ')';
  disCtx.lineWidth = 2 + disResidual * 4;
  disCtx.beginPath(); disCtx.moveTo(280, 140); disCtx.lineTo(680, 140); disCtx.stroke();
  if (disResidual > 0.3) {
    disCtx.fillStyle = 'rgba(255,183,77,0.95)'; disCtx.font = 'bold 12px monospace';
    disCtx.fillText('DISSONANCE', W/2, 100);
  }
  if (disResolved) {
    disCtx.fillStyle = 'rgba(129,199,132,0.9)'; disCtx.font = 'bold 12px monospace';
    disCtx.fillText('◉ belief B has been rewritten — the dissonance is gone', W/2, 260);
    disCtx.fillStyle = '#aaa'; disCtx.font = '11px monospace';
    disCtx.fillText('(the memory of the original belief is no longer available)', W/2, 280);
  }
  requestAnimationFrame(drawDis);
}
drawDis();

// ═══════════════════════════════════════════════════════════════════════
// Theory of Mind
// ═══════════════════════════════════════════════════════════════════════
const tomCanvas = document.getElementById('tom-canvas');
const tomCtx = tomCanvas.getContext('2d');
let tomCount = 1;
document.getElementById('tom-bw').addEventListener('input', (e) => {
  document.getElementById('tom-bw-val').textContent = e.target.value + '%';
});
function tomAdd() { tomCount = Math.min(8, tomCount + 1); }
function tomReset() { tomCount = 1; }
function drawTom() {
  const W = 960, H = 360;
  tomCtx.fillStyle = themeBg(); tomCtx.fillRect(0, 0, W, H);
  const bw = parseInt(document.getElementById('tom-bw').value) / 100;
  // Self predictor at left
  const selfX = 180, selfY = 180;
  tomCtx.fillStyle = 'rgba(79,195,247,0.4)';
  tomCtx.beginPath(); tomCtx.arc(selfX, selfY, 48, 0, Math.PI*2); tomCtx.fill();
  tomCtx.strokeStyle = 'rgba(79,195,247,0.9)'; tomCtx.lineWidth = 2; tomCtx.stroke();
  tomCtx.fillStyle = '#fff'; tomCtx.font = 'bold 13px monospace'; tomCtx.textAlign = 'center';
  tomCtx.fillText('SELF', selfX, selfY + 4);
  // Budget available for modeling others
  const modelBudget = Math.max(0.05, bw - 0.15); // 15% reserved for self
  const perModel = tomCount > 0 ? modelBudget / tomCount : 0;
  for (let i = 0; i < tomCount; i++) {
    const a = (i / Math.max(1, tomCount)) * Math.PI - Math.PI / 2;
    const r = 200;
    const x = selfX + 240 + Math.cos(a) * r;
    const y = selfY + Math.sin(a) * r;
    const size = 18 + perModel * 28;
    tomCtx.fillStyle = 'rgba(186,104,200,' + (0.2 + perModel * 0.6).toFixed(3) + ')';
    tomCtx.beginPath(); tomCtx.arc(x, y, size, 0, Math.PI*2); tomCtx.fill();
    tomCtx.strokeStyle = 'rgba(186,104,200,0.8)'; tomCtx.lineWidth = 1.3; tomCtx.stroke();
    tomCtx.fillStyle = '#fff'; tomCtx.font = '10px monospace';
    tomCtx.fillText('model ' + (i + 1), x, y + 3);
    tomCtx.strokeStyle = 'rgba(186,104,200,' + (0.15 + perModel * 0.5).toFixed(3) + ')';
    tomCtx.beginPath(); tomCtx.moveTo(selfX + 48, selfY); tomCtx.lineTo(x - size, y); tomCtx.stroke();
  }
  const acc = Math.max(0, Math.min(1, perModel * 2));
  document.getElementById('tom-count').textContent = tomCount;
  document.getElementById('tom-acc').textContent = acc.toFixed(2);
  if (acc < 0.2) {
    tomCtx.fillStyle = 'rgba(229,57,53,0.9)'; tomCtx.font = 'bold 12px monospace';
    tomCtx.fillText('◉ models starved — theory of mind degrading', W/2, H - 20);
  }
  requestAnimationFrame(drawTom);
}
drawTom();

// ═══════════════════════════════════════════════════════════════════════
// Tip-of-the-Tongue
// ═══════════════════════════════════════════════════════════════════════
const totCanvas = document.getElementById('tot-canvas');
const totCtx = totCanvas.getContext('2d');
let totPtr = 0.85, totCnt = 0.1, totTrying = 0, totResolved = false;
function totAttempt() {
  totTrying++;
  totPtr = Math.min(1, totPtr + 0.05);
  // Trying reinforces an interfering pathway, not the content
  totCnt *= 0.92;
  totResolved = false;
}
function totLetGo() {
  // Let go → content eventually arrives
  totTrying = 0;
  setTimeout(() => { totCnt = 0.95; totPtr = 0.95; totResolved = true; }, 1500);
}
function totReset() { totPtr = 0.85; totCnt = 0.1; totTrying = 0; totResolved = false; }
function drawTot() {
  const W = 960, H = 320;
  totCtx.fillStyle = themeBg(); totCtx.fillRect(0, 0, W, H);
  // Pointer circle
  totCtx.fillStyle = 'rgba(186,104,200,' + (0.2 + totPtr * 0.6).toFixed(3) + ')';
  totCtx.beginPath(); totCtx.arc(280, 160, 50 + totPtr * 30, 0, Math.PI*2); totCtx.fill();
  totCtx.strokeStyle = 'rgba(186,104,200,0.85)'; totCtx.lineWidth = 2; totCtx.stroke();
  totCtx.fillStyle = '#e0e0e0'; totCtx.font = 'bold 13px monospace'; totCtx.textAlign = 'center';
  totCtx.fillText('POINTER', 280, 160);
  totCtx.font = '11px monospace'; totCtx.fillStyle = '#aaa';
  totCtx.fillText('"the word exists"', 280, 180);
  // Content circle
  totCtx.fillStyle = 'rgba(129,199,132,' + (0.2 + totCnt * 0.6).toFixed(3) + ')';
  totCtx.beginPath(); totCtx.arc(680, 160, 50 + totCnt * 30, 0, Math.PI*2); totCtx.fill();
  totCtx.strokeStyle = 'rgba(129,199,132,0.85)'; totCtx.stroke();
  totCtx.fillStyle = '#e0e0e0'; totCtx.font = 'bold 13px monospace';
  totCtx.fillText('CONTENT', 680, 160);
  totCtx.font = '11px monospace'; totCtx.fillStyle = '#aaa';
  totCtx.fillText('the actual word', 680, 180);
  // Interfering pathway
  if (totTrying > 0) {
    totCtx.strokeStyle = 'rgba(229,57,53,' + Math.min(0.85, 0.2 + totTrying * 0.15).toFixed(3) + ')';
    totCtx.lineWidth = 1.5 + totTrying * 0.3;
    totCtx.setLineDash([3,3]);
    totCtx.beginPath(); totCtx.moveTo(330, 160); totCtx.lineTo(630, 160); totCtx.stroke();
    totCtx.setLineDash([]);
    totCtx.fillStyle = 'rgba(229,57,53,0.75)'; totCtx.font = '11px monospace';
    totCtx.fillText('interfering pathway × ' + totTrying, W/2, 240);
  }
  if (totResolved) {
    totCtx.strokeStyle = 'rgba(129,199,132,0.95)'; totCtx.lineWidth = 3;
    totCtx.beginPath(); totCtx.moveTo(330, 160); totCtx.lineTo(630, 160); totCtx.stroke();
    totCtx.fillStyle = 'rgba(129,199,132,0.95)'; totCtx.font = 'bold 12px monospace';
    totCtx.fillText('◉ the word arrived — seconds after you stopped trying', W/2, 280);
  }
  document.getElementById('tot-ptr').textContent = totPtr.toFixed(2);
  document.getElementById('tot-cnt').textContent = totCnt.toFixed(2);
  requestAnimationFrame(drawTot);
}
drawTot();

// ═══════════════════════════════════════════════════════════════════════
// Hyperfocus
// ═══════════════════════════════════════════════════════════════════════
const hyperCanvas = document.getElementById('hyper-canvas');
const hyperCtx = hyperCanvas.getContext('2d');
let hyperLock = 0, hyperPeripheral = 0, hyperExternalHit = false;
function hyperEngage() { hyperLock = 0.95; hyperPeripheral = 0; }
function hyperExternal() { hyperExternalHit = true; setTimeout(() => { hyperLock *= 0.2; hyperExternalHit = false; }, 200); }
function hyperInternal() { hyperLock *= 0.96; } // barely moves it
function hyperReset() { hyperLock = 0; hyperPeripheral = 0; hyperExternalHit = false; }
function drawHyper() {
  const W = 960, H = 340;
  hyperCtx.fillStyle = themeBg(); hyperCtx.fillRect(0, 0, W, H);
  if (hyperLock > 0.3) hyperPeripheral += 0.002;
  // Focus target at center
  const cx = W/2, cy = 170;
  const haloR = 80 + hyperLock * 60;
  const grad = hyperCtx.createRadialGradient(cx, cy, 0, cx, cy, haloR);
  grad.addColorStop(0, 'rgba(129,199,132,' + (hyperLock * 0.45).toFixed(3) + ')');
  grad.addColorStop(1, 'rgba(129,199,132,0)');
  hyperCtx.fillStyle = grad;
  hyperCtx.fillRect(cx - haloR, cy - haloR, haloR * 2, haloR * 2);
  hyperCtx.fillStyle = 'rgba(129,199,132,0.9)';
  hyperCtx.beginPath(); hyperCtx.arc(cx, cy, 30, 0, Math.PI*2); hyperCtx.fill();
  hyperCtx.strokeStyle = 'rgba(129,199,132,1)'; hyperCtx.lineWidth = 2; hyperCtx.stroke();
  hyperCtx.fillStyle = '#fff'; hyperCtx.font = 'bold 11px monospace'; hyperCtx.textAlign = 'center';
  hyperCtx.fillText('TASK', cx, cy + 4);
  // Peripheral signals trying to break in
  const labels = ['hunger', 'bladder', 'thirst', 'time', 'fatigue', 'other'];
  labels.forEach((lb, i) => {
    const a = (i / labels.length) * Math.PI * 2;
    const r = 200;
    const x = cx + Math.cos(a) * r, y = cy + Math.sin(a) * r;
    const urgency = Math.min(1, hyperPeripheral * (0.7 + i * 0.1));
    hyperCtx.fillStyle = 'rgba(255,183,77,' + (0.25 + urgency * 0.6).toFixed(3) + ')';
    hyperCtx.beginPath(); hyperCtx.arc(x, y, 14 + urgency * 6, 0, Math.PI*2); hyperCtx.fill();
    hyperCtx.strokeStyle = 'rgba(255,183,77,0.7)'; hyperCtx.lineWidth = 1; hyperCtx.stroke();
    hyperCtx.fillStyle = '#e0e0e0'; hyperCtx.font = '10px monospace';
    hyperCtx.fillText(lb, x, y + 3);
    // Attempted signal line
    if (hyperLock > 0.3) {
      hyperCtx.strokeStyle = 'rgba(255,183,77,' + (urgency * 0.3).toFixed(3) + ')';
      hyperCtx.setLineDash([3,4]);
      hyperCtx.beginPath(); hyperCtx.moveTo(x, y); hyperCtx.lineTo(cx, cy); hyperCtx.stroke();
      hyperCtx.setLineDash([]);
    }
  });
  hyperLock *= 0.999;
  if (hyperExternalHit) {
    hyperCtx.fillStyle = 'rgba(229,57,53,0.3)';
    hyperCtx.fillRect(0, 0, W, H);
  }
  document.getElementById('hyper-lock').textContent = hyperLock.toFixed(2);
  document.getElementById('hyper-per').textContent = hyperPeripheral > 0.5 ? 'starving' : (hyperPeripheral > 0.1 ? 'accumulating' : '—');
  if (hyperLock > 0.5 && hyperPeripheral > 0.7) {
    hyperCtx.fillStyle = 'rgba(229,57,53,0.95)'; hyperCtx.font = 'bold 12px monospace';
    hyperCtx.fillText('◉ peripheral signals starving — system cannot disengage', W/2, 320);
  }
  requestAnimationFrame(drawHyper);
}
drawHyper();

// ═══════════════════════════════════════════════════════════════════════
// Temporal Discounting
// ═══════════════════════════════════════════════════════════════════════
const discCanvas = document.getElementById('disc-canvas');
const discCtx = discCanvas.getContext('2d');
let discChoice = null;
document.getElementById('disc-rate').addEventListener('input', (e) => {
  document.getElementById('disc-rate-val').textContent = e.target.value + '%';
});
function discChoose(when) { discChoice = when; }
function discReset() { discChoice = null; }
function drawDisc() {
  const W = 960, H = 340;
  discCtx.fillStyle = themeBg(); discCtx.fillRect(0, 0, W, H);
  const rate = parseInt(document.getElementById('disc-rate').value) / 100;
  // Hyperbolic discount curve: v = V / (1 + k*t)
  const k = rate * 2;
  const V = 20;
  const now = 10;
  // Plot the curve
  discCtx.strokeStyle = 'rgba(186,104,200,0.85)'; discCtx.lineWidth = 2;
  discCtx.beginPath();
  for (let t = 0; t <= 14; t += 0.1) {
    const v = V / (1 + k * t);
    const x = 60 + (t / 14) * (W - 120);
    const y = H - 60 - (v / 22) * (H - 120);
    if (t === 0) discCtx.moveTo(x, y); else discCtx.lineTo(x, y);
  }
  discCtx.stroke();
  // Horizontal line for "now" value ($10)
  const nowY = H - 60 - (now / 22) * (H - 120);
  discCtx.strokeStyle = 'rgba(129,199,132,0.75)'; discCtx.lineWidth = 1.5;
  discCtx.setLineDash([4,4]);
  discCtx.beginPath(); discCtx.moveTo(60, nowY); discCtx.lineTo(W - 60, nowY); discCtx.stroke();
  discCtx.setLineDash([]);
  // Labels
  discCtx.font = '11px monospace'; discCtx.fillStyle = '#aaa'; discCtx.textAlign = 'left';
  discCtx.fillText('$20 future value →', 60, 46);
  discCtx.fillStyle = 'rgba(129,199,132,0.9)';
  discCtx.fillText('$10 now (flat value)', 60, nowY - 6);
  discCtx.fillStyle = '#888';
  discCtx.fillText('days from now', 60, H - 20);
  // Crossover point
  const crossT = (V - now) / (now * k);
  if (crossT > 0 && crossT < 14) {
    const cx = 60 + (crossT / 14) * (W - 120);
    discCtx.strokeStyle = 'rgba(255,183,77,0.8)'; discCtx.lineWidth = 1;
    discCtx.beginPath(); discCtx.moveTo(cx, nowY); discCtx.lineTo(cx, H - 60); discCtx.stroke();
    discCtx.fillStyle = 'rgba(255,183,77,0.9)';
    discCtx.textAlign = 'center';
    discCtx.fillText('$20 wins past day ' + crossT.toFixed(1), cx, H - 40);
  }
  // Choice feedback
  if (discChoice) {
    discCtx.fillStyle = discChoice === 'now' ? 'rgba(255,183,77,0.95)' : 'rgba(129,199,132,0.95)';
    discCtx.font = 'bold 12px monospace'; discCtx.textAlign = 'center';
    const msg = discChoice === 'now'
      ? '→ chose $10 now (discounting the $20 heavily)'
      : '→ chose $20 in a week (overrode the discount function)';
    discCtx.fillText(msg, W/2, 24);
  }
  requestAnimationFrame(drawDisc);
}
drawDisc();

// ═══════════════════════════════════════════════════════════════════════
// Rumination
// ═══════════════════════════════════════════════════════════════════════
const rumCanvas = document.getElementById('rum-canvas');
const rumCtx = rumCanvas.getContext('2d');
const rumNodes = [];
let rumReinf = 0, rumEscape = 0, rumFrame = 0, rumActive = false;
(function rumInit() {
  for (let i = 0; i < 5; i++) {
    const a = (i / 5) * Math.PI * 2 - Math.PI / 2;
    rumNodes.push({ x: 300 + Math.cos(a) * 90, y: 180 + Math.sin(a) * 90, act: 0.2 });
  }
})();
function rumTrigger() { rumActive = true; rumNodes[0].act = 1; }
function rumDistract() { rumEscape++; document.getElementById('rum-escape').textContent = rumEscape; rumNodes.forEach(n => n.act *= 0.3); }
function rumBreak() { rumActive = false; rumNodes.forEach(n => n.act = 0.2); rumEscape++; document.getElementById('rum-escape').textContent = rumEscape; }
function rumReset() { rumActive = false; rumReinf = 0; rumEscape = 0; rumNodes.forEach(n => n.act = 0.2); document.getElementById('rum-reinf').textContent = '0'; document.getElementById('rum-escape').textContent = '0'; }
function drawRum() {
  const W = 960, H = 360;
  rumCtx.fillStyle = themeBg(); rumCtx.fillRect(0, 0, W, H);
  rumFrame++;
  if (rumActive && rumFrame % 20 === 0) {
    // Propagate around the loop
    const next = new Array(rumNodes.length).fill(0);
    for (let i = 0; i < rumNodes.length; i++) {
      next[(i + 1) % rumNodes.length] = Math.min(1, rumNodes[i].act * 0.92 + 0.1);
    }
    next.forEach((v, i) => rumNodes[i].act = Math.max(rumNodes[i].act * 0.95, v));
    rumReinf++;
    document.getElementById('rum-reinf').textContent = rumReinf;
  }
  // Draw loop edges
  for (let i = 0; i < rumNodes.length; i++) {
    const a = rumNodes[i], b = rumNodes[(i + 1) % rumNodes.length];
    const heat = Math.min(1, rumReinf / 30);
    rumCtx.strokeStyle = 'rgba(229,57,53,' + (0.2 + heat * 0.6).toFixed(3) + ')';
    rumCtx.lineWidth = 1.5 + heat * 3;
    rumCtx.beginPath(); rumCtx.moveTo(a.x, a.y); rumCtx.lineTo(b.x, b.y); rumCtx.stroke();
  }
  rumNodes.forEach(n => {
    rumCtx.fillStyle = 'rgba(229,57,53,' + (0.4 + n.act * 0.55).toFixed(3) + ')';
    rumCtx.beginPath(); rumCtx.arc(n.x, n.y, 10 + n.act * 10, 0, Math.PI*2); rumCtx.fill();
  });
  // Other nodes in distance (can't be reached)
  for (let i = 0; i < 8; i++) {
    const x = 650 + (i % 4) * 70, y = 120 + Math.floor(i / 4) * 80;
    rumCtx.fillStyle = 'rgba(120,120,120,0.4)';
    rumCtx.beginPath(); rumCtx.arc(x, y, 6, 0, Math.PI*2); rumCtx.fill();
  }
  rumCtx.fillStyle = '#888'; rumCtx.font = '11px monospace'; rumCtx.textAlign = 'center';
  rumCtx.fillText('the loop', 300, 300);
  rumCtx.fillText('other thoughts (unreached)', 755, 280);
  if (rumReinf > 20) {
    rumCtx.fillStyle = 'rgba(229,57,53,0.95)'; rumCtx.font = 'bold 12px monospace';
    rumCtx.fillText('◉ every escape attempt routes back through the loop', W/2, 340);
  }
  requestAnimationFrame(drawRum);
}
drawRum();

// ═══════════════════════════════════════════════════════════════════════
// Imposter Syndrome
// ═══════════════════════════════════════════════════════════════════════
const impCanvas = document.getElementById('imp-canvas');
const impCtx = impCanvas.getContext('2d');
let impConf = 0.5, impMode_ = 'impostor', impEvents = [];
function impMode(m) { impMode_ = m; }
function impEvent(kind) {
  if (impMode_ === 'impostor') {
    if (kind === 'success') impConf -= 0.03; // externalized, no boost
    else impConf -= 0.08; // internalized, big hit
  } else {
    if (kind === 'success') impConf += 0.08;
    else impConf -= 0.05;
  }
  impConf = Math.max(0.05, Math.min(0.95, impConf));
  impEvents.push({ kind, mode: impMode_, t: Date.now() });
  if (impEvents.length > 10) impEvents.shift();
  document.getElementById('imp-conf').textContent = impConf.toFixed(2);
}
function impReset() { impConf = 0.5; impEvents.length = 0; document.getElementById('imp-conf').textContent = '0.50'; }
function drawImp() {
  const W = 960, H = 380;
  impCtx.fillStyle = themeBg(); impCtx.fillRect(0, 0, W, H);
  // Confidence bar
  impCtx.fillStyle = '#888'; impCtx.font = '11px monospace'; impCtx.textAlign = 'left';
  impCtx.fillText('self-confidence (mode: ' + impMode_ + ')', 40, 26);
  impCtx.fillStyle = '#16213e'; impCtx.fillRect(40, 36, 880, 22);
  const col = impConf > 0.5 ? '129,199,132' : (impConf > 0.3 ? '255,183,77' : '229,57,53');
  impCtx.fillStyle = 'rgba(' + col + ',0.85)'; impCtx.fillRect(40, 36, 880 * impConf, 22);
  // Event history
  impCtx.font = '11px monospace'; impCtx.fillStyle = '#aaa'; impCtx.textAlign = 'left';
  impCtx.fillText('recent events (attribution rule applied)', 40, 92);
  impEvents.forEach((e, i) => {
    const y = 110 + i * 22;
    const eventCol = e.kind === 'success' ? '129,199,132' : '229,57,53';
    impCtx.fillStyle = 'rgba(' + eventCol + ',0.85)';
    impCtx.fillText('• ' + e.kind, 60, y);
    const attribution = e.mode === 'impostor'
      ? (e.kind === 'success' ? 'external ("luck / easy task")' : 'internal ("this is what I am")')
      : (e.kind === 'success' ? 'internal ("I earned it")' : 'partial external ("hard task")');
    impCtx.fillStyle = '#aaa';
    impCtx.fillText('→ attributed ' + attribution, 160, y);
  });
  if (impMode_ === 'impostor' && impConf < 0.2) {
    impCtx.fillStyle = 'rgba(229,57,53,0.95)'; impCtx.font = 'bold 12px monospace';
    impCtx.textAlign = 'center';
    impCtx.fillText('◉ "I am about to be exposed"', W/2, H - 20);
  }
  requestAnimationFrame(drawImp);
}
drawImp();

// ═══════════════════════════════════════════════════════════════════════
// The Senses — multimodal channels
// ═══════════════════════════════════════════════════════════════════════
const sensesCanvas = document.getElementById('senses-canvas');
const sensesCtx = sensesCanvas.getContext('2d');
const sensesChannels = [
  { key: 'vision',  x: 150, y: 90,  label: 'vision',         bandwidth: 1.0,  col: '255,107,107' },
  { key: 'hearing', x: 310, y: 90,  label: 'hearing',        bandwidth: 0.35, col: '255,183,77' },
  { key: 'touch',   x: 470, y: 90,  label: 'touch',          bandwidth: 0.2,  col: '129,199,132' },
  { key: 'smell',   x: 630, y: 90,  label: 'smell',          bandwidth: 0.1,  col: '186,104,200' },
  { key: 'taste',   x: 790, y: 90,  label: 'taste',          bandwidth: 0.08, col: '79,195,247' },
  { key: 'proprio', x: 150, y: 260, label: 'proprioception', bandwidth: 0.3,  col: '255,107,160' },
  { key: 'intero',  x: 390, y: 260, label: 'interoception',  bandwidth: 0.4,  col: '255,140,100' },
  { key: 'balance', x: 630, y: 260, label: 'balance',        bandwidth: 0.15, col: '140,200,255' },
];
const sensesPulses = [];
function sensesFire(key) { sensesPulses.push({ key, t: 0 }); }
function drawSenses() {
  const W = 960, H = 400;
  sensesCtx.fillStyle = themeBg(); sensesCtx.fillRect(0, 0, W, H);
  sensesCtx.fillStyle = '#888'; sensesCtx.font = '11px monospace'; sensesCtx.textAlign = 'center';
  sensesCtx.fillText('circle size = relative bandwidth · all channels feed the same integrated experience', W/2, 20);
  // Integrated percept node
  sensesCtx.fillStyle = 'rgba(186,104,200,0.3)';
  sensesCtx.beginPath(); sensesCtx.arc(850, 260, 44, 0, Math.PI*2); sensesCtx.fill();
  sensesCtx.strokeStyle = 'rgba(186,104,200,0.9)'; sensesCtx.lineWidth = 2; sensesCtx.stroke();
  sensesCtx.fillStyle = '#fff'; sensesCtx.font = 'bold 11px monospace';
  sensesCtx.fillText('UNIFIED', 850, 256);
  sensesCtx.fillText('EXPERIENCE', 850, 270);
  sensesChannels.forEach(c => {
    const r = 16 + c.bandwidth * 34;
    sensesCtx.fillStyle = 'rgba(' + c.col + ',0.4)';
    sensesCtx.beginPath(); sensesCtx.arc(c.x, c.y, r, 0, Math.PI*2); sensesCtx.fill();
    sensesCtx.strokeStyle = 'rgba(' + c.col + ',0.95)'; sensesCtx.lineWidth = 1.5; sensesCtx.stroke();
    sensesCtx.fillStyle = '#e0e0e0'; sensesCtx.font = '10px monospace';
    sensesCtx.fillText(c.label, c.x, c.y + r + 13);
    // Edge to integrated
    sensesCtx.strokeStyle = 'rgba(' + c.col + ',0.15)';
    sensesCtx.lineWidth = 0.5 + c.bandwidth * 2;
    sensesCtx.beginPath(); sensesCtx.moveTo(c.x + r, c.y); sensesCtx.lineTo(806, 260); sensesCtx.stroke();
  });
  for (let i = sensesPulses.length - 1; i >= 0; i--) {
    const p = sensesPulses[i];
    p.t += 0.025;
    if (p.t > 1) { sensesPulses.splice(i, 1); continue; }
    const c = sensesChannels.find(x => x.key === p.key);
    if (!c) continue;
    const px = c.x + (806 - c.x) * p.t;
    const py = c.y + (260 - c.y) * p.t;
    sensesCtx.fillStyle = 'rgba(' + c.col + ',' + (1 - p.t).toFixed(3) + ')';
    sensesCtx.beginPath(); sensesCtx.arc(px, py, 5, 0, Math.PI*2); sensesCtx.fill();
  }
  requestAnimationFrame(drawSenses);
}
drawSenses();

// ═══════════════════════════════════════════════════════════════════════
// Procedural Memory (Alzheimer's + Piano)
// ═══════════════════════════════════════════════════════════════════════
const procCanvas = document.getElementById('proc-canvas');
const procCtx = procCanvas.getContext('2d');
let procDecl = 0.5, procProc = 0.5, procDiseaseStage = 0;
function procEncode(kind) {
  if (kind === 'declarative') procDecl = Math.min(1, procDecl + 0.15);
  else procProc = Math.min(1, procProc + 0.15);
  document.getElementById('proc-decl').textContent = procDecl.toFixed(2);
  document.getElementById('proc-proc').textContent = procProc.toFixed(2);
}
function procDisease() { procDiseaseStage = 1; }
function procReset() { procDecl = 0.5; procProc = 0.5; procDiseaseStage = 0; document.getElementById('proc-decl').textContent = '0.50'; document.getElementById('proc-proc').textContent = '0.50'; }
function drawProc() {
  const W = 960, H = 400;
  procCtx.fillStyle = themeBg(); procCtx.fillRect(0, 0, W, H);
  if (procDiseaseStage > 0 && procDiseaseStage < 1000) {
    procDiseaseStage++;
    if (procDiseaseStage % 30 === 0) {
      procDecl *= 0.9;
      procProc *= 0.998; // barely affected
      document.getElementById('proc-decl').textContent = procDecl.toFixed(2);
      document.getElementById('proc-proc').textContent = procProc.toFixed(2);
    }
  }
  // Two brain regions
  procCtx.fillStyle = 'rgba(255,183,77,' + (0.2 + procDecl * 0.4).toFixed(3) + ')';
  procCtx.beginPath(); procCtx.ellipse(270, 180, 140, 110, 0, 0, Math.PI*2); procCtx.fill();
  procCtx.strokeStyle = 'rgba(255,183,77,' + (0.4 + procDecl * 0.5).toFixed(3) + ')'; procCtx.lineWidth = 2; procCtx.stroke();
  procCtx.fillStyle = '#e0e0e0'; procCtx.font = 'bold 13px monospace'; procCtx.textAlign = 'center';
  procCtx.fillText('HIPPOCAMPUS / MED. TEMPORAL', 270, 60);
  procCtx.font = '11px monospace'; procCtx.fillStyle = '#aaa';
  procCtx.fillText('declarative memory', 270, 80);
  procCtx.font = 'bold 18px monospace'; procCtx.fillStyle = '#fff';
  procCtx.fillText(procDecl.toFixed(2), 270, 186);
  // Procedural region
  procCtx.fillStyle = 'rgba(129,199,132,' + (0.2 + procProc * 0.4).toFixed(3) + ')';
  procCtx.beginPath(); procCtx.ellipse(690, 180, 140, 110, 0, 0, Math.PI*2); procCtx.fill();
  procCtx.strokeStyle = 'rgba(129,199,132,' + (0.4 + procProc * 0.5).toFixed(3) + ')'; procCtx.stroke();
  procCtx.fillStyle = '#e0e0e0'; procCtx.font = 'bold 13px monospace';
  procCtx.fillText('BASAL GANGLIA / CEREBELLUM', 690, 60);
  procCtx.font = '11px monospace'; procCtx.fillStyle = '#aaa';
  procCtx.fillText('procedural memory', 690, 80);
  procCtx.font = 'bold 18px monospace'; procCtx.fillStyle = '#fff';
  procCtx.fillText(procProc.toFixed(2), 690, 186);
  // Disease indicator
  if (procDiseaseStage > 0) {
    procCtx.fillStyle = 'rgba(229,57,53,' + Math.min(0.6, procDiseaseStage / 300).toFixed(3) + ')';
    procCtx.beginPath(); procCtx.ellipse(270, 180, 140, 110, 0, 0, Math.PI*2); procCtx.fill();
    procCtx.fillStyle = 'rgba(229,57,53,0.95)'; procCtx.font = 'bold 12px monospace'; procCtx.textAlign = 'center';
    procCtx.fillText('◉ Alzheimer progressing', 270, 310);
    if (procDecl < 0.15 && procProc > 0.3) {
      procCtx.fillStyle = 'rgba(129,199,132,0.95)';
      procCtx.fillText('procedural memory intact — can still play piano', 690, 310);
    }
  }
  procCtx.font = '11px monospace'; procCtx.fillStyle = '#888';
  procCtx.fillText('two separate substrates · disease spares one while destroying the other', W/2, 380);
  requestAnimationFrame(drawProc);
}
drawProc();

// ═══════════════════════════════════════════════════════════════════════
// Composer — Scenario Player + Master Controls
// ═══════════════════════════════════════════════════════════════════════
let scenRunning = null, scenTimer = 0, scenStepIdx = 0;
const scenarios = {
  'tired-student': [
    { label: 'Bandwidth drops (tired)',                     run: () => { setMasterSlider('master-bw', 30); setSliderById('attn-bw', 30); setSliderById('pain-dist', 0); } },
    { label: 'Stressors stack up',                          run: () => { try { ['deadline','hunger','noise','sleep'].forEach(s => { const b = document.querySelector('[data-stress="' + s + '"]'); if (b && !b.classList.contains('active')) b.click(); }); } catch (e) {} } },
    { label: 'Attention narrows',                           run: () => { setSliderById('attn-bw', 25); } },
    { label: 'Confirmation bias tightens (negative prior)', run: () => { try { confirmSet('negative'); } catch (e) {} } },
    { label: 'Prediction errors cascade',                   run: () => { try { predSurprise(); } catch (e) {} } },
    { label: 'Confidence spirals down (imposter)',          run: () => { try { impMode('impostor'); impEvent('failure'); impEvent('failure'); } catch (e) {} } },
    { label: 'Flow unreachable',                            run: () => { setSliderById('flow-skill', 40); setSliderById('flow-chal', 80); setSliderById('flow-fb', 30); } },
  ],
  'new-grief': [
    { label: 'Encode a high-weight person node',            run: () => { try { griefReset(); } catch (e) {} } },
    { label: 'The loss',                                    run: () => { try { griefLose(); } catch (e) {} } },
    { label: 'Edges dangle',                                run: () => { /* visualized in grief canvas */ } },
    { label: 'Reward landscape partly flattens',            run: () => { setSliderById('dep-sev', 50); } },
    { label: 'Attention narrows, bandwidth drops',          run: () => { setSliderById('attn-bw', 40); setMasterSlider('master-bw', 40); } },
    { label: 'First rewire (the mug)',                      run: () => { try { griefStep(); } catch (e) {} } },
    { label: 'Another rewire (their song)',                 run: () => { try { griefStep(); } catch (e) {} } },
    { label: 'Slow structural recovery begins',             run: () => { try { griefStep(); griefStep(); griefStep(); } catch (e) {} } },
  ],
  'therapy': [
    { label: 'Trauma loop activates',                       run: () => { try { traumaReset(); traumaActivate(); } catch (e) {} } },
    { label: 'Captured — system pulls back in',             run: () => { try { traumaActivate(); } catch (e) {} } },
    { label: 'Therapist presents new context',              run: () => { try { reconEncode(); } catch (e) {} } },
    { label: 'Recall under safety (reconsolidation)',       run: () => { try { reconRecall('safe'); } catch (e) {} } },
    { label: 'Therapy step: cross-link added',              run: () => { try { traumaTherapy(); } catch (e) {} } },
    { label: 'Another therapy step',                        run: () => { try { traumaTherapy(); } catch (e) {} } },
    { label: 'Activation finds escape',                     run: () => { try { traumaActivate(); } catch (e) {} } },
    { label: 'Loop weight decreased — escapes exceed captures', run: () => { try { traumaTherapy(); traumaTherapy(); } catch (e) {} } },
  ],
  'creative-flow': [
    { label: 'Bandwidth high (rested, calm)',               run: () => { setMasterSlider('master-bw', 90); setSliderById('attn-bw', 85); } },
    { label: 'Skill matched to challenge',                  run: () => { setSliderById('flow-skill', 75); setSliderById('flow-chal', 78); } },
    { label: 'Feedback gain high',                          run: () => { setSliderById('flow-fb', 85); } },
    { label: 'Novelty setpoint satisfied',                  run: () => { setSliderById('curi-env', 62); setSliderById('curi-safe', 85); } },
    { label: 'Attention spotlight focuses',                 run: () => { /* handled by attn-bw */ } },
    { label: 'Cursor enters flow lane',                     run: () => { /* flow canvas shows it */ } },
    { label: 'Time perception slows',                       run: () => { setSliderById('time-nov', 80); } },
  ],
  'doomscroll': [
    { label: 'Novelty setpoint not met (bored)',            run: () => { setSliderById('curi-env', 20); setMasterSlider('master-nov', 20); } },
    { label: 'Shallow stream of content enters',            run: () => { setSliderById('curi-env', 85); setSliderById('curi-safe', 35); } },
    { label: 'Threat-tinted novelty — anxiety',             run: () => { /* curi canvas shows red tint */ } },
    { label: 'Bandwidth allocates to scroll',               run: () => { setMasterSlider('master-bw', 50); setSliderById('attn-bw', 55); } },
    { label: 'Encoding rate near zero',                     run: () => { /* no real structure forms */ } },
    { label: 'Rumination pathway activates',                run: () => { try { rumTrigger(); } catch (e) {} } },
    { label: 'Hours vanish, nothing learned',               run: () => { setSliderById('time-nov', 10); } },
  ],
};
function setSliderById(id, val) {
  const el = document.getElementById(id);
  if (!el) return;
  el.value = val;
  el.dispatchEvent(new Event('input', { bubbles: true }));
}
function setMasterSlider(id, val) {
  const el = document.getElementById(id);
  if (el) { el.value = val; el.dispatchEvent(new Event('input', { bubbles: true })); }
}
function scenPlay(key) {
  scenRunning = key; scenStepIdx = 0; scenTimer = 0;
  const log = document.getElementById('scen-log');
  log.innerHTML = '<span style="color:var(--accent2)">▶ started: ' + key + '</span>';
}
function scenStop() {
  scenRunning = null; scenStepIdx = 0;
  document.getElementById('scen-step').textContent = '(stopped)';
}
function scenTick() {
  if (!scenRunning) return;
  const seq = scenarios[scenRunning];
  if (!seq) { scenRunning = null; return; }
  scenTimer++;
  if (scenTimer >= 80) {
    scenTimer = 0;
    if (scenStepIdx >= seq.length) {
      scenRunning = null;
      document.getElementById('scen-step').textContent = '(complete)';
      return;
    }
    const step = seq[scenStepIdx];
    try { step.run(); } catch (e) {}
    document.getElementById('scen-step').textContent = '▶ step ' + (scenStepIdx + 1) + ' / ' + seq.length + ' — ' + step.label;
    const log = document.getElementById('scen-log');
    const div = document.createElement('div');
    div.innerHTML = '<span style="color:var(--accent)">' + (scenStepIdx + 1) + '.</span> ' + step.label;
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
    // Post to PEP bridge
    try { pepSend('scenario.step', { scenario: scenRunning, index: scenStepIdx, label: step.label }); } catch (e) {}
    scenStepIdx++;
  }
}
setInterval(scenTick, 50);

function masterApply() {
  const bw   = parseInt(document.getElementById('master-bw').value);
  const prec = parseInt(document.getElementById('master-prec').value);
  const nov  = parseInt(document.getElementById('master-nov').value);
  const rew  = parseInt(document.getElementById('master-rew').value);
  const fb   = parseInt(document.getElementById('master-fb').value);
  document.getElementById('master-bw-val').textContent = bw;
  document.getElementById('master-prec-val').textContent = prec;
  document.getElementById('master-nov-val').textContent = nov;
  document.getElementById('master-rew-val').textContent = rew;
  document.getElementById('master-fb-val').textContent = fb;
  setSliderById('attn-bw', bw);
  setSliderById('tom-bw', bw);
  setSliderById('pred-conf', prec);
  setSliderById('halluc-prior', prec);
  setSliderById('autism-prec', prec);
  setSliderById('curi-env', nov);
  setSliderById('time-nov', nov);
  setSliderById('dep-sev', 100 - rew);
  setSliderById('flow-fb', fb);
  try { pepSend('master.apply', { bw, prec, nov, rew, fb }); } catch (e) {}
}

// ═══════════════════════════════════════════════════════════════════════
// Libet / Readiness Potential
// ═══════════════════════════════════════════════════════════════════════
const libetCanvas = document.getElementById('libet-canvas');
const libetCtx = libetCanvas.getContext('2d');
let libetT = 0, libetFiring = false, libetRP = 0, libetDecidedAt = -1, libetActedAt = -1;
function libetFire() {
  libetT = 0; libetFiring = true; libetRP = 0; libetDecidedAt = -1; libetActedAt = -1;
}
function libetReset() { libetFire(); libetFiring = false; libetRP = 0; libetDecidedAt = -1; libetActedAt = -1; libetT = 0; }
function drawLibet() {
  const W = 960, H = 340;
  libetCtx.fillStyle = themeBg(); libetCtx.fillRect(0, 0, W, H);
  // Timeline axes
  libetCtx.strokeStyle = 'rgba(186,104,200,0.3)'; libetCtx.lineWidth = 1;
  libetCtx.beginPath(); libetCtx.moveTo(60, H - 60); libetCtx.lineTo(W - 40, H - 60); libetCtx.stroke();
  libetCtx.fillStyle = '#888'; libetCtx.font = '11px monospace'; libetCtx.textAlign = 'left';
  libetCtx.fillText('time →', 60, H - 42);
  libetCtx.textAlign = 'right';
  libetCtx.fillText('motor cortex activity', W - 50, 60);
  if (libetFiring) {
    libetT++;
    libetRP = Math.min(1, (libetT / 140) * (libetT / 140));
    if (libetT > 130 && libetDecidedAt < 0) libetDecidedAt = libetT;
    if (libetT > 165 && libetActedAt < 0) libetActedAt = libetT;
    if (libetT > 220) libetFiring = false;
  }
  // Readiness potential curve (drawn from t=0 to current libetT)
  libetCtx.strokeStyle = 'rgba(129,199,132,0.95)'; libetCtx.lineWidth = 2.5;
  libetCtx.beginPath();
  for (let t = 0; t <= libetT; t++) {
    const x = 60 + (t / 220) * (W - 100);
    const rp = Math.min(1, (t / 140) * (t / 140));
    const y = H - 60 - rp * (H - 120);
    if (t === 0) libetCtx.moveTo(x, y); else libetCtx.lineTo(x, y);
  }
  libetCtx.stroke();
  // "I decided" flag
  if (libetDecidedAt > 0) {
    const dx = 60 + (libetDecidedAt / 220) * (W - 100);
    libetCtx.strokeStyle = 'rgba(186,104,200,0.95)'; libetCtx.lineWidth = 2;
    libetCtx.beginPath(); libetCtx.moveTo(dx, 80); libetCtx.lineTo(dx, H - 58); libetCtx.stroke();
    libetCtx.fillStyle = 'rgba(186,104,200,0.95)'; libetCtx.font = 'bold 12px monospace';
    libetCtx.textAlign = 'center';
    libetCtx.fillText('"I decided"', dx, 76);
  }
  // Action tick
  if (libetActedAt > 0) {
    const ax = 60 + (libetActedAt / 220) * (W - 100);
    libetCtx.fillStyle = 'rgba(255,183,77,0.95)';
    libetCtx.beginPath(); libetCtx.arc(ax, H - 60, 8, 0, Math.PI*2); libetCtx.fill();
    libetCtx.font = 'bold 12px monospace'; libetCtx.textAlign = 'center';
    libetCtx.fillText('ACTION', ax, H - 74);
  }
  // RP label
  if (libetT > 30) {
    libetCtx.fillStyle = 'rgba(129,199,132,0.85)'; libetCtx.font = '11px monospace';
    libetCtx.textAlign = 'left';
    libetCtx.fillText('readiness potential rising…', 70, 100);
  }
  if (libetT > 200) {
    libetCtx.fillStyle = 'rgba(255,183,77,0.95)'; libetCtx.font = 'bold 12px monospace';
    libetCtx.textAlign = 'center';
    libetCtx.fillText('◉ the brain was already going before "I decided"', W/2, H - 20);
  }
  requestAnimationFrame(drawLibet);
}
drawLibet();

// ═══════════════════════════════════════════════════════════════════════
// Reward Prediction Error
// ═══════════════════════════════════════════════════════════════════════
const rpeCanvas = document.getElementById('rpe-canvas');
const rpeCtx = rpeCanvas.getContext('2d');
let rpeStageName = 'idle', rpeT = 0;
function rpeStage(s) { rpeStageName = s; rpeT = 0; }
function rpeReset() { rpeStageName = 'idle'; rpeT = 0; }
function drawRpe() {
  const W = 960, H = 360;
  rpeCtx.fillStyle = themeBg(); rpeCtx.fillRect(0, 0, W, H);
  if (rpeStageName !== 'idle') rpeT = Math.min(260, rpeT + 1);
  // Timeline
  rpeCtx.strokeStyle = 'rgba(186,104,200,0.3)'; rpeCtx.lineWidth = 1;
  rpeCtx.beginPath(); rpeCtx.moveTo(60, H - 70); rpeCtx.lineTo(W - 40, H - 70); rpeCtx.stroke();
  rpeCtx.fillStyle = '#888'; rpeCtx.font = '11px monospace'; rpeCtx.textAlign = 'left';
  rpeCtx.fillText('time →', 60, H - 50);
  // Cue and reward markers (positions along timeline)
  const cueX = 60 + 0.35 * (W - 100);
  const rewX = 60 + 0.75 * (W - 100);
  // Draw cue marker if applicable
  const showCue = rpeStageName === 'learned' || rpeStageName === 'omit';
  if (showCue) {
    rpeCtx.strokeStyle = 'rgba(79,195,247,0.6)'; rpeCtx.setLineDash([3,3]);
    rpeCtx.beginPath(); rpeCtx.moveTo(cueX, 80); rpeCtx.lineTo(cueX, H - 70); rpeCtx.stroke();
    rpeCtx.setLineDash([]);
    rpeCtx.fillStyle = 'rgba(79,195,247,0.95)'; rpeCtx.font = 'bold 11px monospace';
    rpeCtx.textAlign = 'center'; rpeCtx.fillText('CUE', cueX, 76);
  }
  // Draw reward marker if applicable
  const showReward = rpeStageName === 'unpredicted' || rpeStageName === 'learned';
  if (showReward) {
    rpeCtx.strokeStyle = 'rgba(129,199,132,0.6)'; rpeCtx.setLineDash([3,3]);
    rpeCtx.beginPath(); rpeCtx.moveTo(rewX, 80); rpeCtx.lineTo(rewX, H - 70); rpeCtx.stroke();
    rpeCtx.setLineDash([]);
    rpeCtx.fillStyle = 'rgba(129,199,132,0.95)'; rpeCtx.font = 'bold 11px monospace';
    rpeCtx.textAlign = 'center'; rpeCtx.fillText('REWARD', rewX, 76);
  }
  // Missing reward marker
  if (rpeStageName === 'omit') {
    rpeCtx.strokeStyle = 'rgba(229,57,53,0.4)'; rpeCtx.setLineDash([3,3]);
    rpeCtx.beginPath(); rpeCtx.moveTo(rewX, 80); rpeCtx.lineTo(rewX, H - 70); rpeCtx.stroke();
    rpeCtx.setLineDash([]);
    rpeCtx.fillStyle = 'rgba(229,57,53,0.85)'; rpeCtx.font = '11px monospace';
    rpeCtx.fillText('(expected)', rewX, 76);
  }
  // Dopamine spike
  const spikeMid = H - 180;
  const baseline = H - 120;
  rpeCtx.strokeStyle = 'rgba(255,183,77,0.95)'; rpeCtx.lineWidth = 2.5;
  rpeCtx.beginPath();
  for (let i = 0; i <= 260; i++) {
    const x = 60 + (i / 260) * (W - 100);
    let y = baseline;
    if (rpeStageName === 'unpredicted') {
      // Spike at reward
      const d = Math.abs((i / 260) - 0.75);
      if (d < 0.04) y = baseline - (1 - d / 0.04) * 100;
    } else if (rpeStageName === 'learned') {
      // Spike migrated to cue, silent at reward
      const d = Math.abs((i / 260) - 0.35);
      if (d < 0.04) y = baseline - (1 - d / 0.04) * 100;
    } else if (rpeStageName === 'omit') {
      // Spike at cue, DIP at missing reward
      const dc = Math.abs((i / 260) - 0.35);
      if (dc < 0.04) y = baseline - (1 - dc / 0.04) * 100;
      const dr = Math.abs((i / 260) - 0.75);
      if (dr < 0.04) y = baseline + (1 - dr / 0.04) * 45;
    }
    if (i === 0) rpeCtx.moveTo(x, y); else rpeCtx.lineTo(x, y);
  }
  rpeCtx.stroke();
  // Baseline line
  rpeCtx.strokeStyle = 'rgba(255,183,77,0.2)'; rpeCtx.setLineDash([2,4]);
  rpeCtx.beginPath(); rpeCtx.moveTo(60, baseline); rpeCtx.lineTo(W - 40, baseline); rpeCtx.stroke();
  rpeCtx.setLineDash([]);
  // Labels
  rpeCtx.fillStyle = 'rgba(255,183,77,0.9)'; rpeCtx.font = '11px monospace'; rpeCtx.textAlign = 'left';
  rpeCtx.fillText('dopamine firing rate', 70, 30);
  rpeCtx.fillStyle = '#888';
  rpeCtx.fillText('baseline', 70, baseline - 5);
  if (rpeStageName === 'unpredicted') {
    rpeCtx.fillStyle = 'rgba(255,183,77,0.9)'; rpeCtx.font = 'bold 12px monospace';
    rpeCtx.textAlign = 'center';
    rpeCtx.fillText('Stage 1 — surprise: reward arrives, prediction was zero', W/2, H - 30);
  } else if (rpeStageName === 'learned') {
    rpeCtx.fillStyle = 'rgba(79,195,247,0.9)'; rpeCtx.font = 'bold 12px monospace';
    rpeCtx.textAlign = 'center';
    rpeCtx.fillText('Stage 2 — spike migrated to the cue; reward is now expected', W/2, H - 30);
  } else if (rpeStageName === 'omit') {
    rpeCtx.fillStyle = 'rgba(229,57,53,0.95)'; rpeCtx.font = 'bold 12px monospace';
    rpeCtx.textAlign = 'center';
    rpeCtx.fillText('Stage 3 — cue fires, reward omitted, negative residual at expected time', W/2, H - 30);
  }
  requestAnimationFrame(drawRpe);
}
drawRpe();

// ═══════════════════════════════════════════════════════════════════════
// Rubber Hand Illusion
// ═══════════════════════════════════════════════════════════════════════
const rubberCanvas = document.getElementById('rubber-canvas');
const rubberCtx = rubberCanvas.getContext('2d');
let rubberInc = 0, rubberStrokeMode = 'idle', rubberT = 0, rubberFlinch = 0;
function rubberStroke(mode) { rubberStrokeMode = mode; rubberT = 0; }
function rubberThreaten() { if (rubberInc > 0.4) rubberFlinch = 30; }
function rubberReset() { rubberInc = 0; rubberStrokeMode = 'idle'; rubberT = 0; rubberFlinch = 0; }
function drawRubber() {
  const W = 960, H = 360;
  rubberCtx.fillStyle = themeBg(); rubberCtx.fillRect(0, 0, W, H);
  rubberT++;
  if (rubberStrokeMode === 'sync') rubberInc = Math.min(1, rubberInc + 0.005);
  else if (rubberStrokeMode === 'async') rubberInc = Math.max(0, rubberInc - 0.003);
  else rubberInc *= 0.999;
  if (rubberFlinch > 0) rubberFlinch--;
  // Screen (divider)
  rubberCtx.strokeStyle = 'rgba(120,120,120,0.5)'; rubberCtx.lineWidth = 3;
  rubberCtx.beginPath(); rubberCtx.moveTo(W/2, 40); rubberCtx.lineTo(W/2, H - 40); rubberCtx.stroke();
  rubberCtx.fillStyle = '#666'; rubberCtx.font = '11px monospace'; rubberCtx.textAlign = 'center';
  rubberCtx.fillText('SCREEN', W/2, 30);
  // Real hand (hidden)
  const handX = 240, handY = 180;
  rubberCtx.fillStyle = 'rgba(186,104,200,0.45)';
  rubberCtx.beginPath(); rubberCtx.ellipse(handX, handY, 55, 30, 0, 0, Math.PI*2); rubberCtx.fill();
  rubberCtx.strokeStyle = 'rgba(186,104,200,0.85)'; rubberCtx.lineWidth = 1.5; rubberCtx.stroke();
  rubberCtx.fillStyle = '#e0e0e0'; rubberCtx.font = '11px monospace';
  rubberCtx.fillText('real hand (hidden)', handX, handY + 60);
  // Rubber hand
  const rubX = 720, rubY = 180;
  rubberCtx.fillStyle = 'rgba(255,183,77,' + (0.4 + rubberInc * 0.4).toFixed(3) + ')';
  rubberCtx.beginPath(); rubberCtx.ellipse(rubX + rubberFlinch, rubY, 55, 30, 0, 0, Math.PI*2); rubberCtx.fill();
  rubberCtx.strokeStyle = 'rgba(255,183,77,0.85)'; rubberCtx.stroke();
  rubberCtx.fillStyle = '#e0e0e0';
  rubberCtx.fillText('rubber hand (visible)', rubX, rubY + 60);
  // Body map hand (drifts from real-hand position toward rubber-hand position as incorporation rises)
  const mapX = handX + (rubX - handX) * rubberInc;
  rubberCtx.fillStyle = 'rgba(129,199,132,0.55)';
  rubberCtx.beginPath(); rubberCtx.ellipse(mapX, 90, 40, 22, 0, 0, Math.PI*2); rubberCtx.fill();
  rubberCtx.strokeStyle = 'rgba(129,199,132,0.85)'; rubberCtx.lineWidth = 1.5; rubberCtx.stroke();
  rubberCtx.fillStyle = '#fff'; rubberCtx.font = '10px monospace';
  rubberCtx.fillText('body map: hand', mapX, 94);
  // Brush strokes
  if (rubberStrokeMode !== 'idle') {
    const phase = (rubberT % 40) / 40;
    const px = handX - 40 + phase * 80;
    rubberCtx.fillStyle = 'rgba(79,195,247,0.9)';
    rubberCtx.beginPath(); rubberCtx.arc(px, handY - 18, 4, 0, Math.PI*2); rubberCtx.fill();
    let rpx;
    if (rubberStrokeMode === 'sync') rpx = rubX - 40 + phase * 80;
    else rpx = rubX - 40 + ((phase + 0.5) % 1) * 80;
    rubberCtx.fillStyle = 'rgba(79,195,247,0.9)';
    rubberCtx.beginPath(); rubberCtx.arc(rpx, rubY - 18, 4, 0, Math.PI*2); rubberCtx.fill();
  }
  // Flinch effect
  if (rubberFlinch > 0) {
    rubberCtx.fillStyle = 'rgba(229,57,53,' + (rubberFlinch / 30 * 0.3).toFixed(3) + ')';
    rubberCtx.fillRect(0, 0, W, H);
    rubberCtx.fillStyle = 'rgba(229,57,53,0.95)'; rubberCtx.font = 'bold 12px monospace';
    rubberCtx.textAlign = 'center';
    rubberCtx.fillText('◉ FLINCH — body map treats rubber hand as yours', W/2, H - 20);
  }
  document.getElementById('rubber-inc').textContent = rubberInc.toFixed(2);
  requestAnimationFrame(drawRubber);
}
drawRubber();

// ═══════════════════════════════════════════════════════════════════════
// Language Shapes Perception
// ═══════════════════════════════════════════════════════════════════════
const langCanvas = document.getElementById('lang-canvas');
const langCtx = langCanvas.getContext('2d');
let langModeName = 'english';
function langMode(m) { langModeName = m; }
function drawLang() {
  const W = 960, H = 300;
  langCtx.fillStyle = themeBg(); langCtx.fillRect(0, 0, W, H);
  // Draw a row of blues from light to dark
  const swatchCount = 20;
  const swW = 30, gap = 8;
  const startX = (W - (swatchCount * (swW + gap))) / 2;
  for (let i = 0; i < swatchCount; i++) {
    const t = i / (swatchCount - 1);
    const r = Math.round(180 * (1 - t) + 0 * t);
    const g = Math.round(220 * (1 - t) + 30 * t);
    const b = 255;
    langCtx.fillStyle = 'rgb(' + r + ',' + g + ',' + b + ')';
    langCtx.fillRect(startX + i * (swW + gap), 80, swW, 60);
  }
  // Category boundary
  if (langModeName === 'russian') {
    const midI = 9;
    const boundaryX = startX + midI * (swW + gap) + swW + gap / 2;
    langCtx.strokeStyle = 'rgba(255,183,77,0.95)'; langCtx.lineWidth = 3;
    langCtx.setLineDash([6,4]);
    langCtx.beginPath(); langCtx.moveTo(boundaryX, 60); langCtx.lineTo(boundaryX, 160); langCtx.stroke();
    langCtx.setLineDash([]);
    langCtx.fillStyle = 'rgba(255,183,77,0.95)'; langCtx.font = 'bold 13px monospace';
    langCtx.textAlign = 'center';
    langCtx.fillText('goluboy', startX + 5 * (swW + gap), 180);
    langCtx.fillText('siniy', startX + 14 * (swW + gap), 180);
    langCtx.font = '11px monospace'; langCtx.fillStyle = '#aaa';
    langCtx.fillText('two categories → sharper discrimination at boundary', W/2, 240);
  } else {
    langCtx.fillStyle = '#aaa'; langCtx.font = 'bold 13px monospace'; langCtx.textAlign = 'center';
    langCtx.fillText('"blue"', W/2, 180);
    langCtx.font = '11px monospace';
    langCtx.fillText('one category → no sharp perceptual boundary', W/2, 240);
  }
  langCtx.textAlign = 'left'; langCtx.fillStyle = '#888'; langCtx.font = '11px monospace';
  langCtx.fillText('mode: ' + langModeName, 20, 24);
  requestAnimationFrame(drawLang);
}
drawLang();

// ═══════════════════════════════════════════════════════════════════════
// Mirror Neurons
// ═══════════════════════════════════════════════════════════════════════
const mirrorCanvas = document.getElementById('mirror-canvas');
const mirrorCtx = mirrorCanvas.getContext('2d');
let mirrorSelf = 0, mirrorMir = 0, mirrorMode = 'idle', mirrorT = 0;
function mirrorDo() { mirrorMode = 'do'; mirrorT = 0; mirrorSelf = 1; mirrorMir = 0.9; }
function mirrorWatch() { mirrorMode = 'watch'; mirrorT = 0; mirrorSelf = 0.1; mirrorMir = 0.55; }
function mirrorReset() { mirrorSelf = 0; mirrorMir = 0; mirrorMode = 'idle'; }
function drawMirror() {
  const W = 960, H = 320;
  mirrorCtx.fillStyle = themeBg(); mirrorCtx.fillRect(0, 0, W, H);
  mirrorSelf *= 0.985;
  mirrorMir *= 0.985;
  // You
  mirrorCtx.fillStyle = 'rgba(129,199,132,' + (0.3 + mirrorSelf * 0.55).toFixed(3) + ')';
  mirrorCtx.beginPath(); mirrorCtx.arc(220, 140, 50 + mirrorSelf * 16, 0, Math.PI*2); mirrorCtx.fill();
  mirrorCtx.strokeStyle = 'rgba(129,199,132,0.85)'; mirrorCtx.lineWidth = 1.5; mirrorCtx.stroke();
  mirrorCtx.fillStyle = '#fff'; mirrorCtx.font = 'bold 13px monospace'; mirrorCtx.textAlign = 'center';
  mirrorCtx.fillText('YOUR MOTOR', 220, 136);
  mirrorCtx.font = '10px monospace'; mirrorCtx.fillStyle = '#aaa';
  mirrorCtx.fillText('reach-for-cup', 220, 152);
  // Mirror neurons
  mirrorCtx.fillStyle = 'rgba(186,104,200,' + (0.3 + mirrorMir * 0.55).toFixed(3) + ')';
  mirrorCtx.beginPath(); mirrorCtx.arc(500, 140, 50 + mirrorMir * 16, 0, Math.PI*2); mirrorCtx.fill();
  mirrorCtx.strokeStyle = 'rgba(186,104,200,0.85)'; mirrorCtx.stroke();
  mirrorCtx.fillStyle = '#fff'; mirrorCtx.font = 'bold 13px monospace';
  mirrorCtx.fillText('MIRROR', 500, 136);
  mirrorCtx.font = '10px monospace'; mirrorCtx.fillStyle = '#aaa';
  mirrorCtx.fillText('reach-for-cup', 500, 152);
  // Observed person
  mirrorCtx.fillStyle = 'rgba(79,195,247,0.35)';
  mirrorCtx.beginPath(); mirrorCtx.arc(760, 140, 50, 0, Math.PI*2); mirrorCtx.fill();
  mirrorCtx.strokeStyle = 'rgba(79,195,247,0.85)'; mirrorCtx.stroke();
  mirrorCtx.fillStyle = '#fff'; mirrorCtx.font = 'bold 13px monospace';
  mirrorCtx.fillText('OTHER', 760, 136);
  mirrorCtx.font = '10px monospace'; mirrorCtx.fillStyle = '#aaa';
  mirrorCtx.fillText('reaching…', 760, 152);
  // Edges
  mirrorCtx.strokeStyle = 'rgba(129,199,132,' + (0.2 + mirrorSelf * 0.6).toFixed(3) + ')';
  mirrorCtx.lineWidth = 1 + mirrorSelf * 2;
  mirrorCtx.beginPath(); mirrorCtx.moveTo(270, 140); mirrorCtx.lineTo(450, 140); mirrorCtx.stroke();
  mirrorCtx.strokeStyle = 'rgba(79,195,247,' + (0.2 + mirrorMir * 0.6).toFixed(3) + ')';
  mirrorCtx.beginPath(); mirrorCtx.moveTo(710, 140); mirrorCtx.lineTo(550, 140); mirrorCtx.stroke();
  document.getElementById('mirror-self').textContent = mirrorSelf.toFixed(2);
  document.getElementById('mirror-mir').textContent = mirrorMir.toFixed(2);
  mirrorCtx.font = '11px monospace'; mirrorCtx.fillStyle = '#aaa'; mirrorCtx.textAlign = 'center';
  if (mirrorMode === 'watch') {
    mirrorCtx.fillText('watching — mirror neurons fire at ~60% amplitude, no actual movement', W/2, 250);
  } else if (mirrorMode === 'do') {
    mirrorCtx.fillText('doing — self motor fires fully, mirrors fire along with it', W/2, 250);
  }
  requestAnimationFrame(drawMirror);
}
drawMirror();

// ═══════════════════════════════════════════════════════════════════════
// Sensory Substitution
// ═══════════════════════════════════════════════════════════════════════
const subCanvas = document.getElementById('sub-canvas');
const subCtx = subCanvas.getContext('2d');
let subInputKind = 'eye';
function subInput(kind) { subInputKind = kind; }
function subReset() { subInputKind = 'eye'; }
function drawSub() {
  const W = 960, H = 340;
  subCtx.fillStyle = themeBg(); subCtx.fillRect(0, 0, W, H);
  // Source
  const srcX = 170, srcY = 170;
  const srcLabel = { eye: 'retina', tongue: 'tongue grid', skin: 'vibrating vest' }[subInputKind];
  const srcCol = { eye: '255,183,77', tongue: '186,104,200', skin: '79,195,247' }[subInputKind];
  subCtx.fillStyle = 'rgba(' + srcCol + ',0.4)';
  subCtx.beginPath(); subCtx.arc(srcX, srcY, 50, 0, Math.PI*2); subCtx.fill();
  subCtx.strokeStyle = 'rgba(' + srcCol + ',0.9)'; subCtx.lineWidth = 1.5; subCtx.stroke();
  subCtx.fillStyle = '#fff'; subCtx.font = 'bold 12px monospace'; subCtx.textAlign = 'center';
  subCtx.fillText(srcLabel.toUpperCase(), srcX, srcY + 4);
  subCtx.font = '10px monospace'; subCtx.fillStyle = '#aaa';
  subCtx.fillText('input channel', srcX, srcY + 70);
  // Visual cortex
  const vcX = 680, vcY = 170;
  subCtx.fillStyle = 'rgba(129,199,132,0.55)';
  subCtx.beginPath(); subCtx.ellipse(vcX, vcY, 120, 90, 0, 0, Math.PI*2); subCtx.fill();
  subCtx.strokeStyle = 'rgba(129,199,132,0.9)'; subCtx.lineWidth = 2; subCtx.stroke();
  subCtx.fillStyle = '#fff'; subCtx.font = 'bold 13px monospace';
  subCtx.fillText('VISUAL CORTEX', vcX, vcY - 10);
  subCtx.font = '11px monospace';
  subCtx.fillText('(runs vision', vcX, vcY + 8);
  subCtx.fillText('on any channel)', vcX, vcY + 24);
  // Edge
  subCtx.strokeStyle = 'rgba(' + srcCol + ',0.7)'; subCtx.lineWidth = 2;
  subCtx.beginPath(); subCtx.moveTo(srcX + 50, srcY); subCtx.lineTo(vcX - 120, vcY); subCtx.stroke();
  // Particles flowing
  const t = (Date.now() % 1500) / 1500;
  for (let i = 0; i < 5; i++) {
    const tt = (t + i * 0.2) % 1;
    const px = srcX + 50 + ((vcX - 120) - (srcX + 50)) * tt;
    const py = srcY + (vcY - srcY) * tt;
    subCtx.fillStyle = 'rgba(' + srcCol + ',' + (1 - tt).toFixed(3) + ')';
    subCtx.beginPath(); subCtx.arc(px, py, 4, 0, Math.PI*2); subCtx.fill();
  }
  subCtx.font = '11px monospace'; subCtx.fillStyle = '#aaa'; subCtx.textAlign = 'center';
  subCtx.fillText('input channel varies · computation does not', W/2, H - 20);
  requestAnimationFrame(drawSub);
}
drawSub();

// ═══════════════════════════════════════════════════════════════════════
// Mental Rehearsal
// ═══════════════════════════════════════════════════════════════════════
const rehearseCanvas = document.getElementById('rehearse-canvas');
const rehearseCtx = rehearseCanvas.getContext('2d');
let rehearseW = 0.1, rehearseMode_ = 'physical';
const rehearseHist = [];
function rehearseMode(m) { rehearseMode_ = m; }
function rehearseFire() {
  const gain = rehearseMode_ === 'physical' ? 0.08 : (rehearseMode_ === 'mental' ? 0.06 : 0);
  rehearseW = Math.min(1, rehearseW + gain);
  rehearseHist.push(rehearseW);
  if (rehearseHist.length > 200) rehearseHist.shift();
  document.getElementById('rehearse-w').textContent = rehearseW.toFixed(2);
}
function rehearseReset() { rehearseW = 0.1; rehearseHist.length = 0; document.getElementById('rehearse-w').textContent = '0.10'; }

// ═══════════════════════════════════════════════════════════════════════
// Biological Substrate — neurons + glia mapped to PEP primitives
// ═══════════════════════════════════════════════════════════════════════
const substrateCanvas = document.getElementById('substrate-canvas');
const substrateCtx = substrateCanvas.getContext('2d');
let substrateFocusType = 'all';
let substrateT = 0;
function substrateFocus(t) { substrateFocusType = t; }

function drawSubstrate() {
  const W = 960, H = 480;
  substrateCtx.fillStyle = themeBg(); substrateCtx.fillRect(0, 0, W, H);
  substrateT++;
  const focus = substrateFocusType;
  const showAll = focus === 'all';

  // Central synapse structure
  const cx = W / 2, cy = H / 2 - 20;

  // Three neurons forming a tripartite synapse
  const neurons = [
    { x: cx - 180, y: cy, label: 'Pre-synaptic neuron', r: 40 },
    { x: cx + 180, y: cy, label: 'Post-synaptic neuron', r: 40 },
    { x: cx, y: cy + 160, label: 'Downstream neuron', r: 35 },
  ];

  // Draw neurons (always visible but dim if not focused)
  const neuronAlpha = (showAll || focus === 'neuron') ? 0.85 : 0.2;
  neurons.forEach(function(n) {
    substrateCtx.fillStyle = 'rgba(167,139,250,' + neuronAlpha + ')';
    substrateCtx.beginPath(); substrateCtx.arc(n.x, n.y, n.r, 0, Math.PI * 2); substrateCtx.fill();
    substrateCtx.strokeStyle = 'rgba(167,139,250,' + Math.min(1, neuronAlpha + 0.15) + ')';
    substrateCtx.lineWidth = 2; substrateCtx.stroke();
    substrateCtx.fillStyle = 'rgba(255,255,255,' + neuronAlpha + ')';
    substrateCtx.font = '9px monospace'; substrateCtx.textAlign = 'center';
    substrateCtx.fillText(n.label, n.x, n.y + 4);
  });

  // Axon connection (edge) between pre and post
  var edgeAlpha = (showAll || focus === 'neuron' || focus === 'oligo') ? 0.7 : 0.15;
  substrateCtx.strokeStyle = 'rgba(167,139,250,' + edgeAlpha + ')';
  substrateCtx.lineWidth = 3;
  substrateCtx.beginPath(); substrateCtx.moveTo(neurons[0].x + 40, neurons[0].y);
  substrateCtx.lineTo(neurons[1].x - 40, neurons[1].y); substrateCtx.stroke();
  // Second edge
  substrateCtx.beginPath(); substrateCtx.moveTo(neurons[1].x, neurons[1].y + 40);
  substrateCtx.lineTo(neurons[2].x + 35, neurons[2].y - 20); substrateCtx.stroke();

  // Signal pulse along the edge (animated)
  if (showAll || focus === 'neuron' || focus === 'oligo') {
    var pulse = (substrateT % 120) / 120;
    var px = neurons[0].x + 40 + pulse * (neurons[1].x - 40 - neurons[0].x - 40);
    substrateCtx.fillStyle = 'rgba(167,139,250,0.9)';
    substrateCtx.beginPath(); substrateCtx.arc(px, neurons[0].y, 5, 0, Math.PI * 2); substrateCtx.fill();
  }

  // ASTROCYTE — wrapping the synapse gap
  var astroAlpha = (showAll || focus === 'astro') ? 0.75 : 0.1;
  // Large irregular shape around the synapse
  substrateCtx.fillStyle = 'rgba(186,104,200,' + (astroAlpha * 0.25) + ')';
  substrateCtx.beginPath();
  substrateCtx.ellipse(cx, cy - 5, 100, 55, 0, 0, Math.PI * 2);
  substrateCtx.fill();
  substrateCtx.strokeStyle = 'rgba(186,104,200,' + astroAlpha + ')';
  substrateCtx.lineWidth = 1.5;
  substrateCtx.setLineDash([3, 3]);
  substrateCtx.beginPath();
  substrateCtx.ellipse(cx, cy - 5, 100, 55, 0, 0, Math.PI * 2);
  substrateCtx.stroke();
  substrateCtx.setLineDash([]);
  if (showAll || focus === 'astro') {
    substrateCtx.fillStyle = 'rgba(186,104,200,' + astroAlpha + ')';
    substrateCtx.font = 'bold 10px monospace'; substrateCtx.textAlign = 'center';
    substrateCtx.fillText('ASTROCYTE', cx, cy - 50);
    substrateCtx.font = '9px monospace';
    substrateCtx.fillText('calcium waves → modulates edge gain', cx, cy - 36);
    substrateCtx.fillText('PEP: STATE MODULATION', cx, cy + 46);
    // Calcium wave animation
    var wave = Math.sin(substrateT * 0.05) * 0.5 + 0.5;
    substrateCtx.fillStyle = 'rgba(186,104,200,' + (wave * 0.5) + ')';
    substrateCtx.beginPath(); substrateCtx.arc(cx, cy, 8, 0, Math.PI * 2); substrateCtx.fill();
  }

  // OLIGODENDROCYTE — myelin segments on the axon
  var oligoAlpha = (showAll || focus === 'oligo') ? 0.8 : 0.1;
  var myelinSegments = 5;
  var axStart = neurons[0].x + 45, axEnd = neurons[1].x - 45;
  for (var i = 0; i < myelinSegments; i++) {
    var sx = axStart + (i / myelinSegments) * (axEnd - axStart) + 10;
    var sw = ((axEnd - axStart) / myelinSegments) * 0.7;
    substrateCtx.fillStyle = 'rgba(79,195,247,' + (oligoAlpha * 0.5) + ')';
    substrateCtx.fillRect(sx, cy - 8, sw, 16);
    substrateCtx.strokeStyle = 'rgba(79,195,247,' + oligoAlpha + ')';
    substrateCtx.lineWidth = 1;
    substrateCtx.strokeRect(sx, cy - 8, sw, 16);
  }
  if (showAll || focus === 'oligo') {
    substrateCtx.fillStyle = 'rgba(79,195,247,' + oligoAlpha + ')';
    substrateCtx.font = 'bold 10px monospace'; substrateCtx.textAlign = 'center';
    substrateCtx.fillText('MYELIN (oligodendrocytes)', cx, cy - 72);
    substrateCtx.font = '9px monospace';
    substrateCtx.fillText('insulation → 10-100x signal speed', cx, cy - 58);
    substrateCtx.fillText('PEP: EDGE SPEED (not yet modeled)', cx, cy + 60);
  }

  // MICROGLIA — small patrolling cells
  var microAlpha = (showAll || focus === 'micro') ? 0.8 : 0.1;
  var microPositions = [
    { x: cx - 220, y: cy + 80 }, { x: cx + 230, y: cy + 90 },
    { x: cx - 60, y: cy + 130 }, { x: cx + 100, y: cy - 80 },
  ];
  microPositions.forEach(function(m, i) {
    var wobble = Math.sin(substrateT * 0.03 + i * 1.5) * 8;
    substrateCtx.fillStyle = 'rgba(129,199,132,' + (microAlpha * 0.6) + ')';
    substrateCtx.beginPath();
    substrateCtx.arc(m.x + wobble, m.y, 10, 0, Math.PI * 2);
    substrateCtx.fill();
    // Branch-like processes
    for (var a = 0; a < 5; a++) {
      var angle = (a / 5) * Math.PI * 2 + substrateT * 0.01;
      substrateCtx.strokeStyle = 'rgba(129,199,132,' + (microAlpha * 0.5) + ')';
      substrateCtx.lineWidth = 1;
      substrateCtx.beginPath();
      substrateCtx.moveTo(m.x + wobble, m.y);
      substrateCtx.lineTo(m.x + wobble + Math.cos(angle) * 18, m.y + Math.sin(angle) * 18);
      substrateCtx.stroke();
    }
  });
  if (showAll || focus === 'micro') {
    substrateCtx.fillStyle = 'rgba(129,199,132,' + microAlpha + ')';
    substrateCtx.font = 'bold 10px monospace'; substrateCtx.textAlign = 'left';
    substrateCtx.fillText('MICROGLIA (pruning crew)', 30, H - 60);
    substrateCtx.font = '9px monospace';
    substrateCtx.fillText('patrol → prune weak synapses during sleep', 30, H - 46);
    substrateCtx.fillText('PEP: HAZE PRIMITIVE (opacity decay + node eviction)', 30, H - 32);
  }

  // Legend at top-right
  substrateCtx.font = '10px monospace'; substrateCtx.textAlign = 'right';
  var legendItems = [
    { color: '#a78bfa', label: 'Neurons → nodes + edges' },
    { color: '#ba68c8', label: 'Astrocytes → state modulation' },
    { color: '#4fc3f7', label: 'Oligodendrocytes → edge speed' },
    { color: '#81c784', label: 'Microglia → pruning (haze)' },
  ];
  legendItems.forEach(function(l, i) {
    var alpha = (showAll || focus === l.label.split(' ')[0].toLowerCase().slice(0, 5)) ? 1 : 0.3;
    substrateCtx.fillStyle = 'rgba(255,255,255,' + alpha + ')';
    substrateCtx.fillRect(W - 260, 20 + i * 20, 10, 10);
    substrateCtx.fillStyle = l.color;
    substrateCtx.fillRect(W - 260, 20 + i * 20, 10, 10);
    substrateCtx.fillStyle = 'rgba(255,255,255,' + alpha + ')';
    substrateCtx.fillText(l.label, W - 20, 29 + i * 20);
  });

  requestAnimationFrame(drawSubstrate);
}
drawSubstrate();

// ═══════════════════════════════════════════════════════════════════════
// Motor Prediction Errors — bite tongue / stub toe visualization
// ═══════════════════════════════════════════════════════════════════════
const motorCanvas = document.getElementById('motor-err-canvas');
const motorCtx = motorCanvas.getContext('2d');
const MOTOR_SCENARIOS = {
  tongue: {
    label: 'BITING YOUR TONGUE',
    predictor_a: 'Jaw trajectory predictor',
    predictor_b: 'Tongue position predictor',
    predicted: 'Tongue predicted at position A (safe)',
    actual: 'Tongue actually at position B (bite zone)',
    cause: 'Jaw motor plan fired before tongue repositioned',
    color_a: '#f06292', color_b: '#a78bfa',
    // Animation positions
    obj_a: { label: 'JAW', y: 0.35 },
    obj_b: { label: 'TONGUE', y: 0.65 },
  },
  toe: {
    label: 'STUBBING YOUR TOE',
    predictor_a: 'Foot trajectory predictor',
    predictor_b: 'Spatial map (floor model)',
    predicted: 'Floor predicted as flat/clear',
    actual: 'Obstacle at toe height',
    cause: 'Spatial model was stale or visual predictor was offline (dark)',
    color_a: '#81c784', color_b: '#ffb74d',
    obj_a: { label: 'FOOT', y: 0.4 },
    obj_b: { label: 'OBSTACLE', y: 0.6 },
  },
  spill: {
    label: 'SPILLING COFFEE',
    predictor_a: 'Hand trajectory predictor',
    predictor_b: 'Cup-tilt model',
    predicted: 'Cup predicted level during reach',
    actual: 'Hand accelerated; cup tilted past spill angle',
    cause: 'Attention split — reaching while looking elsewhere',
    color_a: '#4fc3f7', color_b: '#fbbf24',
    obj_a: { label: 'HAND', y: 0.35 },
    obj_b: { label: 'CUP', y: 0.65 },
  },
  trip: {
    label: 'TRIPPING ON STAIRS',
    predictor_a: 'Leg-lift predictor',
    predictor_b: 'Step-height model',
    predicted: 'Step height predicted from last stair',
    actual: 'This step is slightly different height or is the top',
    cause: 'Motor runs on autopilot; same leg-lift for every step until it misses one',
    color_a: '#ba68c8', color_b: '#67e8f9',
    obj_a: { label: 'FOOT LIFT', y: 0.4 },
    obj_b: { label: 'STEP EDGE', y: 0.6 },
  },
};
let motorActive = null;
let motorT = 0;
function motorScenario(key) { motorActive = key; motorT = 0; }
function drawMotorErr() {
  const W = 960, H = 400;
  motorCtx.fillStyle = themeBg(); motorCtx.fillRect(0, 0, W, H);
  const bw = parseInt(document.getElementById('motor-bw').value) / 100;
  const dist = parseInt(document.getElementById('motor-dist').value) / 100;
  if (!motorActive) {
    motorCtx.fillStyle = '#666'; motorCtx.font = '11px monospace'; motorCtx.textAlign = 'center';
    motorCtx.fillText('(pick a scenario)', W / 2, H / 2);
    requestAnimationFrame(drawMotorErr); return;
  }
  motorT++;
  const s = MOTOR_SCENARIOS[motorActive];
  // Error probability scales with low bandwidth and high distraction
  const errorProb = (1 - bw) * 0.6 + dist * 0.4;
  // Title
  motorCtx.fillStyle = s.color_a; motorCtx.font = 'bold 14px monospace'; motorCtx.textAlign = 'left';
  motorCtx.fillText(s.label, 30, 30);
  // Two prediction tracks
  const trackY_a = H * s.obj_a.y;
  const trackY_b = H * s.obj_b.y;
  // Background tracks
  motorCtx.strokeStyle = 'rgba(120,120,130,0.2)'; motorCtx.lineWidth = 1;
  motorCtx.setLineDash([4, 4]);
  motorCtx.beginPath(); motorCtx.moveTo(100, trackY_a); motorCtx.lineTo(W - 60, trackY_a); motorCtx.stroke();
  motorCtx.beginPath(); motorCtx.moveTo(100, trackY_b); motorCtx.lineTo(W - 60, trackY_b); motorCtx.stroke();
  motorCtx.setLineDash([]);
  // Labels
  motorCtx.fillStyle = s.color_a; motorCtx.font = 'bold 10px monospace'; motorCtx.textAlign = 'right';
  motorCtx.fillText(s.obj_a.label, 90, trackY_a + 4);
  motorCtx.fillStyle = s.color_b;
  motorCtx.fillText(s.obj_b.label, 90, trackY_b + 4);
  // Predictor labels
  motorCtx.fillStyle = '#aaa'; motorCtx.font = '9px monospace'; motorCtx.textAlign = 'left';
  motorCtx.fillText(s.predictor_a, 100, trackY_a - 14);
  motorCtx.fillText(s.predictor_b, 100, trackY_b - 14);
  // Animated objects — the "predicted" path vs the "actual" path
  const phase = (motorT % 200) / 200;
  const x = 100 + phase * (W - 200);
  // Object A follows its predicted path
  const wobble_a = Math.sin(phase * Math.PI * 4) * 8 * (1 - bw);
  motorCtx.fillStyle = s.color_a + 'cc';
  motorCtx.beginPath(); motorCtx.arc(x, trackY_a + wobble_a, 12, 0, Math.PI * 2); motorCtx.fill();
  // Object B — diverges from predicted at the collision point
  const divergePoint = 0.5 + (1 - errorProb) * 0.3;
  let obj_b_y = trackY_b;
  if (phase > divergePoint && phase < divergePoint + 0.15) {
    // Collision zone — B drifts toward A
    const collisionPhase = (phase - divergePoint) / 0.15;
    obj_b_y = trackY_b + (trackY_a - trackY_b) * collisionPhase * errorProb;
  }
  motorCtx.fillStyle = s.color_b + 'cc';
  motorCtx.beginPath(); motorCtx.arc(x, obj_b_y, 12, 0, Math.PI * 2); motorCtx.fill();
  // Collision flash
  if (phase > divergePoint + 0.1 && phase < divergePoint + 0.2 && errorProb > 0.3) {
    const flashSize = 20 + errorProb * 30;
    motorCtx.fillStyle = 'rgba(248,113,113,' + (0.8 * (1 - (phase - divergePoint - 0.1) * 10)).toFixed(3) + ')';
    motorCtx.beginPath();
    motorCtx.arc(x, (trackY_a + obj_b_y) / 2, flashSize, 0, Math.PI * 2);
    motorCtx.fill();
    motorCtx.fillStyle = '#fff'; motorCtx.font = 'bold 12px monospace'; motorCtx.textAlign = 'center';
    motorCtx.fillText('PREDICTION ERROR', x, (trackY_a + obj_b_y) / 2 + 4);
  }
  // Predicted vs Actual text
  motorCtx.fillStyle = '#aaa'; motorCtx.font = '10px monospace'; motorCtx.textAlign = 'left';
  motorCtx.fillText('Predicted: ' + s.predicted, 30, H - 60);
  motorCtx.fillText('Actual:    ' + s.actual, 30, H - 42);
  motorCtx.fillStyle = '#f06292'; motorCtx.font = 'bold 10px monospace';
  motorCtx.fillText('Cause: ' + s.cause, 30, H - 22);
  // Error probability bar
  motorCtx.fillStyle = '#666'; motorCtx.font = '10px monospace'; motorCtx.textAlign = 'right';
  motorCtx.fillText('error probability: ' + (errorProb * 100).toFixed(0) + '%', W - 30, 30);
  motorCtx.fillStyle = 'rgba(248,113,113,0.2)'; motorCtx.fillRect(W - 180, 36, 150, 10);
  motorCtx.fillStyle = 'rgba(248,113,113,0.85)'; motorCtx.fillRect(W - 180, 36, 150 * errorProb, 10);
  motorCtx.fillStyle = '#666'; motorCtx.textAlign = 'right';
  motorCtx.fillText('bandwidth: ' + bw.toFixed(2) + '  distraction: ' + dist.toFixed(2), W - 30, 66);
  requestAnimationFrame(drawMotorErr);
}
drawMotorErr();
function drawRehearse() {
  const W = 960, H = 320;
  rehearseCtx.fillStyle = themeBg(); rehearseCtx.fillRect(0, 0, W, H);
  rehearseCtx.strokeStyle = 'rgba(186,104,200,0.3)'; rehearseCtx.lineWidth = 1;
  rehearseCtx.beginPath(); rehearseCtx.moveTo(60, 40); rehearseCtx.lineTo(60, H - 60); rehearseCtx.lineTo(W - 30, H - 60); rehearseCtx.stroke();
  rehearseCtx.fillStyle = '#888'; rehearseCtx.font = '11px monospace'; rehearseCtx.textAlign = 'left';
  rehearseCtx.fillText('pathway weight', 20, 50);
  rehearseCtx.textAlign = 'right';
  rehearseCtx.fillText('reps →', W - 30, H - 42);
  if (rehearseHist.length > 1) {
    rehearseCtx.strokeStyle = 'rgba(186,104,200,0.95)'; rehearseCtx.lineWidth = 2.5;
    rehearseCtx.beginPath();
    rehearseHist.forEach((w, i) => {
      const x = 60 + (i / 200) * (W - 90);
      const y = H - 60 - w * (H - 100);
      if (i === 0) rehearseCtx.moveTo(x, y); else rehearseCtx.lineTo(x, y);
    });
    rehearseCtx.stroke();
  }
  rehearseCtx.font = '11px monospace'; rehearseCtx.fillStyle = '#aaa'; rehearseCtx.textAlign = 'left';
  rehearseCtx.fillText('mode: ' + rehearseMode_, 70, 70);
  requestAnimationFrame(drawRehearse);
}
drawRehearse();

// ═══════════════════════════════════════════════════════════════════════
// Anchoring & Availability
// ═══════════════════════════════════════════════════════════════════════
const anchorCanvas = document.getElementById('anchor-canvas');
const anchorCtx = anchorCanvas.getContext('2d');
let anchorVal = null, anchorGuess = null;
function anchorSpin(v) { anchorVal = v; anchorGuess = null; document.getElementById('anchor-guess').textContent = '—'; }
function anchorEstimate() {
  // Estimate drifts toward the anchor
  const truth = 54;
  let base;
  if (anchorVal === null) base = truth + (Math.random() - 0.5) * 10;
  else base = anchorVal + (truth - anchorVal) * 0.35 + (Math.random() - 0.5) * 8;
  anchorGuess = Math.round(Math.max(1, base));
  document.getElementById('anchor-guess').textContent = anchorGuess;
}
function anchorReset() { anchorVal = null; anchorGuess = null; document.getElementById('anchor-guess').textContent = '—'; }
function drawAnchor() {
  const W = 960, H = 340;
  anchorCtx.fillStyle = themeBg(); anchorCtx.fillRect(0, 0, W, H);
  // Number line
  anchorCtx.strokeStyle = 'rgba(186,104,200,0.35)'; anchorCtx.lineWidth = 2;
  anchorCtx.beginPath(); anchorCtx.moveTo(60, H/2); anchorCtx.lineTo(W - 60, H/2); anchorCtx.stroke();
  // Tick marks every 10
  for (let i = 0; i <= 100; i += 10) {
    const x = 60 + (i / 100) * (W - 120);
    anchorCtx.strokeStyle = 'rgba(186,104,200,0.4)';
    anchorCtx.beginPath(); anchorCtx.moveTo(x, H/2 - 5); anchorCtx.lineTo(x, H/2 + 5); anchorCtx.stroke();
    anchorCtx.fillStyle = '#666'; anchorCtx.font = '10px monospace'; anchorCtx.textAlign = 'center';
    anchorCtx.fillText(i, x, H/2 + 22);
  }
  // Truth marker
  const truthX = 60 + (54 / 100) * (W - 120);
  anchorCtx.strokeStyle = 'rgba(129,199,132,0.9)'; anchorCtx.lineWidth = 2;
  anchorCtx.beginPath(); anchorCtx.moveTo(truthX, H/2 - 30); anchorCtx.lineTo(truthX, H/2 + 30); anchorCtx.stroke();
  anchorCtx.fillStyle = 'rgba(129,199,132,0.9)'; anchorCtx.font = 'bold 11px monospace';
  anchorCtx.fillText('truth (54)', truthX, H/2 - 40);
  // Anchor marker
  if (anchorVal !== null) {
    const ax = 60 + (anchorVal / 100) * (W - 120);
    anchorCtx.strokeStyle = 'rgba(255,183,77,0.85)'; anchorCtx.lineWidth = 2;
    anchorCtx.setLineDash([4,4]);
    anchorCtx.beginPath(); anchorCtx.moveTo(ax, 40); anchorCtx.lineTo(ax, H - 60); anchorCtx.stroke();
    anchorCtx.setLineDash([]);
    anchorCtx.fillStyle = 'rgba(255,183,77,0.9)'; anchorCtx.font = 'bold 11px monospace';
    anchorCtx.fillText('anchor (' + anchorVal + ')', ax, 34);
  }
  // Guess marker
  if (anchorGuess !== null) {
    const gx = 60 + (anchorGuess / 100) * (W - 120);
    anchorCtx.fillStyle = 'rgba(186,104,200,0.95)';
    anchorCtx.beginPath(); anchorCtx.arc(gx, H/2, 10, 0, Math.PI*2); anchorCtx.fill();
    anchorCtx.fillStyle = 'rgba(186,104,200,0.95)'; anchorCtx.font = 'bold 12px monospace';
    anchorCtx.fillText('your guess', gx, H - 40);
  }
  requestAnimationFrame(drawAnchor);
}
drawAnchor();

// ═══════════════════════════════════════════════════════════════════════
// Moral Emotions
// ═══════════════════════════════════════════════════════════════════════
const moralCanvas = document.getElementById('moral-canvas');
const moralCtx = moralCanvas.getContext('2d');
let moralActive = null, moralTrolleyOn = false;
function moralTrigger(e) { moralActive = e; moralTrolleyOn = false; }
function moralTrolley() { moralTrolleyOn = true; moralActive = null; }
function moralReset() { moralActive = null; moralTrolleyOn = false; }
function drawMoral() {
  const W = 960, H = 380;
  moralCtx.fillStyle = themeBg(); moralCtx.fillRect(0, 0, W, H);
  const emotions = [
    { key: 'disgust', label: 'DISGUST',  col: '129,199,132', x: 180, y: 140, desc: 'recoil · pathogen/social contaminant' },
    { key: 'shame',   label: 'SHAME',    col: '186,104,200', x: 440, y: 140, desc: 'hide · group saw my failure' },
    { key: 'pride',   label: 'PRIDE',    col: '255,183,77',  x: 700, y: 140, desc: 'visible · group saw my success' },
    { key: 'guilt',   label: 'GUILT',    col: '79,195,247',  x: 310, y: 260, desc: 'repair · i hurt someone i love' },
  ];
  emotions.forEach(e => {
    const active = moralActive === e.key;
    const r = active ? 52 : 40;
    moralCtx.fillStyle = 'rgba(' + e.col + ',' + (active ? 0.85 : 0.3).toFixed(3) + ')';
    moralCtx.beginPath(); moralCtx.arc(e.x, e.y, r, 0, Math.PI*2); moralCtx.fill();
    moralCtx.strokeStyle = 'rgba(' + e.col + ',0.95)'; moralCtx.lineWidth = 1.5; moralCtx.stroke();
    moralCtx.fillStyle = '#fff'; moralCtx.font = 'bold 13px monospace'; moralCtx.textAlign = 'center';
    moralCtx.fillText(e.label, e.x, e.y + 4);
    moralCtx.fillStyle = '#aaa'; moralCtx.font = '10px monospace';
    moralCtx.fillText(e.desc, e.x, e.y + r + 16);
  });
  if (moralTrolleyOn) {
    moralCtx.fillStyle = 'rgba(255,183,77,0.15)'; moralCtx.fillRect(540, 230, 400, 130);
    moralCtx.strokeStyle = 'rgba(255,183,77,0.85)'; moralCtx.lineWidth = 1.5;
    moralCtx.strokeRect(540, 230, 400, 130);
    moralCtx.fillStyle = '#fff'; moralCtx.font = 'bold 12px monospace'; moralCtx.textAlign = 'left';
    moralCtx.fillText('TROLLEY PROBLEM', 554, 252);
    moralCtx.font = '11px monospace'; moralCtx.fillStyle = '#aaa';
    moralCtx.fillText('S2: utilitarian — push one, save five', 554, 274);
    moralCtx.fillText('S1: disgust/guilt — do not physically push a human', 554, 292);
    moralCtx.fillText('which wins depends on proximity:', 554, 312);
    moralCtx.fillText('• distant switch → S2 wins', 554, 328);
    moralCtx.fillText('• close push → S1 wins', 554, 344);
  }
  requestAnimationFrame(drawMoral);
}
drawMoral();

// ═══════════════════════════════════════════════════════════════════════
// Psychedelics
// ═══════════════════════════════════════════════════════════════════════
const psyCanvas = document.getElementById('psy-canvas');
const psyCtx = psyCanvas.getContext('2d');
const psyNodes = [], psyEdgesWithin = [], psyEdgesCross = [];
(function psyInit() {
  const W = 960, H = 400;
  const centers = [[240, 120], [480, 120], [720, 120], [240, 280], [480, 280], [720, 280]];
  centers.forEach((c, k) => {
    for (let i = 0; i < 6; i++) {
      const a = (i / 6) * Math.PI * 2;
      psyNodes.push({ x: c[0] + Math.cos(a) * 40, y: c[1] + Math.sin(a) * 40, cluster: k });
    }
  });
  for (let i = 0; i < psyNodes.length; i++) for (let j = i + 1; j < psyNodes.length; j++) {
    if (psyNodes[i].cluster === psyNodes[j].cluster) psyEdgesWithin.push({ a: i, b: j });
    else if (Math.random() < 0.08) psyEdgesCross.push({ a: i, b: j });
  }
})();
document.getElementById('psy-dose').addEventListener('input', (e) => {
  document.getElementById('psy-dose-val').textContent = e.target.value + '%';
});
function psyReset() { document.getElementById('psy-dose').value = 0; document.getElementById('psy-dose-val').textContent = '0%'; }
function drawPsy() {
  const W = 960, H = 400;
  const dose = parseInt(document.getElementById('psy-dose').value) / 100;
  const bg = 'rgba(' + Math.round(14 + dose * 30) + ',' + Math.round(14 + dose * 6) + ',' + Math.round(18 + dose * 30) + ',1)';
  psyCtx.fillStyle = bg; psyCtx.fillRect(0, 0, W, H);
  psyEdgesWithin.forEach(e => {
    const a = psyNodes[e.a], b = psyNodes[e.b];
    psyCtx.strokeStyle = 'rgba(186,104,200,' + ((1 - dose * 0.7) * 0.5).toFixed(3) + ')';
    psyCtx.lineWidth = 1 + (1 - dose) * 1.5;
    psyCtx.beginPath(); psyCtx.moveTo(a.x, a.y); psyCtx.lineTo(b.x, b.y); psyCtx.stroke();
  });
  psyEdgesCross.forEach(e => {
    const a = psyNodes[e.a], b = psyNodes[e.b];
    psyCtx.strokeStyle = 'rgba(129,199,132,' + (0.08 + dose * 0.55).toFixed(3) + ')';
    psyCtx.lineWidth = 0.5 + dose * 2;
    psyCtx.beginPath(); psyCtx.moveTo(a.x, a.y); psyCtx.lineTo(b.x, b.y); psyCtx.stroke();
  });
  psyNodes.forEach(n => {
    const wobble = dose * 4 * Math.sin(Date.now() * 0.003 + n.x * 0.02);
    psyCtx.fillStyle = 'rgba(186,104,200,0.6)';
    psyCtx.beginPath(); psyCtx.arc(n.x + wobble, n.y, 5, 0, Math.PI*2); psyCtx.fill();
  });
  psyCtx.fillStyle = '#aaa'; psyCtx.font = '11px monospace'; psyCtx.textAlign = 'center';
  if (dose < 0.2) psyCtx.fillText('baseline — clusters isolated, within-cluster connections dominant', W/2, 30);
  else if (dose < 0.6) psyCtx.fillText('cross-cluster communication rising — priors weakening', W/2, 30);
  else psyCtx.fillText('entropic brain — all clusters talking, DMN suppressed, self-model thinning', W/2, 30);
  requestAnimationFrame(drawPsy);
}
drawPsy();

// ═══════════════════════════════════════════════════════════════════════
// Fear Conditioning
// ═══════════════════════════════════════════════════════════════════════
const fearCanvas = document.getElementById('fear-canvas');
const fearCtx = fearCanvas.getContext('2d');
let fearCond = 0, fearExtW = 0, fearLastEvent = null, fearFlash = 0;
function fearCondition() { fearCond = Math.min(1, fearCond + 0.8); fearLastEvent = 'paired'; fearFlash = 30; }
function fearCuePlay() { fearFlash = 30; fearLastEvent = 'cue'; }
function fearExtinguish() { fearExtW = Math.min(1, fearExtW + 0.15); fearLastEvent = 'extinction'; }
function fearReset() { fearCond = 0; fearExtW = 0; fearLastEvent = null; fearFlash = 0; document.getElementById('fear-resp').textContent = '0.00'; document.getElementById('fear-ext').textContent = '0.00'; }
function drawFear() {
  const W = 960, H = 360;
  fearCtx.fillStyle = themeBg(); fearCtx.fillRect(0, 0, W, H);
  fearFlash *= 0.95;
  const response = Math.max(0, fearCond - fearExtW * 0.8);
  document.getElementById('fear-resp').textContent = response.toFixed(2);
  document.getElementById('fear-ext').textContent = fearExtW.toFixed(2);
  // Cue
  fearCtx.fillStyle = 'rgba(79,195,247,0.55)';
  fearCtx.beginPath(); fearCtx.arc(180, 180, 42, 0, Math.PI*2); fearCtx.fill();
  fearCtx.strokeStyle = 'rgba(79,195,247,0.95)'; fearCtx.lineWidth = 2; fearCtx.stroke();
  fearCtx.fillStyle = '#fff'; fearCtx.font = 'bold 12px monospace'; fearCtx.textAlign = 'center';
  fearCtx.fillText('CUE', 180, 184);
  fearCtx.font = '10px monospace'; fearCtx.fillStyle = '#aaa';
  fearCtx.fillText('(tone)', 180, 238);
  // Amygdala
  fearCtx.fillStyle = 'rgba(229,57,53,' + (0.3 + response * 0.55).toFixed(3) + ')';
  fearCtx.beginPath(); fearCtx.arc(480, 180, 50 + response * 18, 0, Math.PI*2); fearCtx.fill();
  fearCtx.strokeStyle = 'rgba(229,57,53,0.95)'; fearCtx.stroke();
  fearCtx.fillStyle = '#fff'; fearCtx.font = 'bold 12px monospace';
  fearCtx.fillText('AMYGDALA', 480, 184);
  // Response
  fearCtx.fillStyle = 'rgba(255,183,77,' + (0.3 + response * 0.55).toFixed(3) + ')';
  fearCtx.beginPath(); fearCtx.arc(780, 180, 42, 0, Math.PI*2); fearCtx.fill();
  fearCtx.strokeStyle = 'rgba(255,183,77,0.95)'; fearCtx.stroke();
  fearCtx.fillStyle = '#fff'; fearCtx.font = 'bold 12px monospace';
  fearCtx.fillText('FEAR', 780, 184);
  // Original fear pathway
  fearCtx.strokeStyle = 'rgba(229,57,53,' + (0.15 + fearCond * 0.7).toFixed(3) + ')';
  fearCtx.lineWidth = 1 + fearCond * 4;
  fearCtx.beginPath(); fearCtx.moveTo(222, 175); fearCtx.lineTo(438, 175); fearCtx.stroke();
  fearCtx.beginPath(); fearCtx.moveTo(522, 175); fearCtx.lineTo(738, 175); fearCtx.stroke();
  // Extinction pathway (inhibitory, below)
  if (fearExtW > 0.05) {
    fearCtx.strokeStyle = 'rgba(129,199,132,' + (0.2 + fearExtW * 0.7).toFixed(3) + ')';
    fearCtx.lineWidth = 1 + fearExtW * 3;
    fearCtx.setLineDash([4,4]);
    fearCtx.beginPath();
    fearCtx.moveTo(222, 195); fearCtx.quadraticCurveTo(360, 260, 438, 200);
    fearCtx.stroke();
    fearCtx.setLineDash([]);
    fearCtx.fillStyle = 'rgba(129,199,132,0.85)'; fearCtx.font = '10px monospace';
    fearCtx.fillText('inhibitory pathway (extinction)', 330, 275);
  }
  if (fearFlash > 1) {
    fearCtx.fillStyle = 'rgba(229,57,53,' + Math.min(0.2, fearFlash / 150).toFixed(3) + ')';
    fearCtx.fillRect(0, 0, W, H);
  }
  requestAnimationFrame(drawFear);
}
drawFear();

// ═══════════════════════════════════════════════════════════════════════
// Sandbox
// ═══════════════════════════════════════════════════════════════════════
const sboxCanvas = document.getElementById('sbox-canvas');
const sboxCtx = sboxCanvas.getContext('2d');
const sboxNodes = [], sboxEdges = [];
let sboxMode_ = 'node', sboxEdgeFrom = -1;
const SBOX_MODE_LABELS = { node: 'add node', edge: 'draw edge', fire: 'inject activation', erase: 'erase' };
function sboxMode(m) { sboxMode_ = m; sboxEdgeFrom = -1; document.getElementById('sbox-mode-label').textContent = SBOX_MODE_LABELS[m] || m; }
function sboxClear() { sboxNodes.length = 0; sboxEdges.length = 0; sboxEdgeFrom = -1; sboxCounts(); }
function sboxCounts() {
  document.getElementById('sbox-nodes').textContent = sboxNodes.length;
  document.getElementById('sbox-edges').textContent = sboxEdges.length;
}
document.getElementById('sbox-decay').addEventListener('input', (e) => {
  document.getElementById('sbox-decay-val').textContent = (parseInt(e.target.value) / 100).toFixed(2);
});
document.getElementById('sbox-spread').addEventListener('input', (e) => {
  document.getElementById('sbox-spread-val').textContent = (parseInt(e.target.value) / 100).toFixed(2);
});
sboxCanvas.addEventListener('click', (e) => {
  const r = sboxCanvas.getBoundingClientRect();
  const x = (e.clientX - r.left) * (sboxCanvas.width / r.width);
  const y = (e.clientY - r.top) * (sboxCanvas.height / r.height);
  let hitNode = -1, bestD = 1e9;
  sboxNodes.forEach((n, i) => {
    const d = Math.hypot(n.x - x, n.y - y);
    if (d < 18 && d < bestD) { bestD = d; hitNode = i; }
  });
  if (sboxMode_ === 'node') {
    sboxNodes.push({ x, y, act: 0.2 });
    sboxCounts();
  } else if (sboxMode_ === 'edge') {
    if (hitNode >= 0) {
      if (sboxEdgeFrom < 0) sboxEdgeFrom = hitNode;
      else if (sboxEdgeFrom !== hitNode) {
        sboxEdges.push({ a: sboxEdgeFrom, b: hitNode });
        sboxEdgeFrom = -1;
        sboxCounts();
      }
    }
  } else if (sboxMode_ === 'fire') {
    if (hitNode >= 0) sboxNodes[hitNode].act = 1;
  } else if (sboxMode_ === 'erase') {
    if (hitNode >= 0) {
      sboxNodes.splice(hitNode, 1);
      for (let i = sboxEdges.length - 1; i >= 0; i--) {
        const ed = sboxEdges[i];
        if (ed.a === hitNode || ed.b === hitNode) sboxEdges.splice(i, 1);
        else {
          if (ed.a > hitNode) ed.a--;
          if (ed.b > hitNode) ed.b--;
        }
      }
      sboxCounts();
    }
  }
});
function drawSbox() {
  const W = 960, H = 420;
  sboxCtx.fillStyle = themeBg(); sboxCtx.fillRect(0, 0, W, H);
  const decay = parseInt(document.getElementById('sbox-decay').value) / 100;
  const spread = parseInt(document.getElementById('sbox-spread').value) / 100;
  // Spread activation to neighbors
  const deltas = new Array(sboxNodes.length).fill(0);
  sboxEdges.forEach(e => {
    const a = sboxNodes[e.a], b = sboxNodes[e.b];
    if (!a || !b) return;
    deltas[e.b] += a.act * spread;
    deltas[e.a] += b.act * spread;
  });
  sboxNodes.forEach((n, i) => { n.act = Math.min(1, n.act * decay + deltas[i] * (1 - decay * 0.3)); });
  sboxEdges.forEach(e => {
    const a = sboxNodes[e.a], b = sboxNodes[e.b];
    if (!a || !b) return;
    const heat = Math.max(a.act, b.act);
    sboxCtx.strokeStyle = 'rgba(186,104,200,' + (0.2 + heat * 0.5).toFixed(3) + ')';
    sboxCtx.lineWidth = 0.8 + heat * 2.5;
    sboxCtx.beginPath(); sboxCtx.moveTo(a.x, a.y); sboxCtx.lineTo(b.x, b.y); sboxCtx.stroke();
  });
  sboxNodes.forEach((n, i) => {
    const r = 7 + n.act * 12;
    sboxCtx.fillStyle = 'rgba(186,104,200,' + (0.35 + n.act * 0.55).toFixed(3) + ')';
    sboxCtx.beginPath(); sboxCtx.arc(n.x, n.y, r, 0, Math.PI*2); sboxCtx.fill();
    sboxCtx.strokeStyle = 'rgba(186,104,200,0.9)'; sboxCtx.lineWidth = 1.5; sboxCtx.stroke();
    if (i === sboxEdgeFrom) {
      sboxCtx.strokeStyle = 'rgba(129,199,132,0.95)'; sboxCtx.lineWidth = 2;
      sboxCtx.beginPath(); sboxCtx.arc(n.x, n.y, r + 4, 0, Math.PI*2); sboxCtx.stroke();
    }
  });
  if (sboxNodes.length === 0) {
    sboxCtx.fillStyle = '#666'; sboxCtx.font = '11px monospace'; sboxCtx.textAlign = 'center';
    sboxCtx.fillText('(click to add your first node)', W/2, H/2);
  }
  requestAnimationFrame(drawSbox);
}
drawSbox();

// ═══════════════════════════════════════════════════════════════════════
// Glossary hover — scans info blocks and adds tooltips to known terms
// ═══════════════════════════════════════════════════════════════════════
// ═══════════════════════════════════════════════════════════════════════
// Bookmarks / Random (same pattern as Lingora/Atria)
// ═══════════════════════════════════════════════════════════════════════
function axonaBookmarks() { try { return JSON.parse(localStorage.getItem('axona-bookmarks') || '[]'); } catch (e) { return []; } }
function axonaSaveBookmarks(b) { try { localStorage.setItem('axona-bookmarks', JSON.stringify(b)); } catch (e) {} }
function axonaBookmark() {
  const active = document.querySelector('.panel.active');
  if (!active) return;
  const id = active.id;
  const bmks = axonaBookmarks();
  const idx = bmks.indexOf(id);
  if (idx >= 0) bmks.splice(idx, 1); else bmks.push(id);
  axonaSaveBookmarks(bmks);
  const btn = document.getElementById('bookmark-btn');
  if (btn) btn.textContent = bmks.includes(id) ? '★' : '☆';
}
function axonaRandom() {
  const panels = Array.from(document.querySelectorAll('.panel'));
  const candidates = panels.filter(p => !['state-space'].includes(p.id));
  if (!candidates.length) return;
  const pick = candidates[Math.floor(Math.random() * candidates.length)];
  const h3s = Array.from(pick.querySelectorAll('h3'));
  if (h3s.length > 0) {
    const h = h3s[Math.floor(Math.random() * h3s.length)];
    if (!h.id) h.id = pick.id + '-sub-' + Math.floor(Math.random() * 999);
    canvasSelect(h.id);
  } else {
    canvasSelect(pick.id);
  }
}
document.querySelectorAll('.tab').forEach(t => {
  t.addEventListener('click', () => {
    setTimeout(() => {
      const active = document.querySelector('.panel.active');
      const btn = document.getElementById('bookmark-btn');
      if (active && btn) btn.textContent = axonaBookmarks().includes(active.id) ? '★' : '☆';
      if (active && active.id === 'gallery-tab') galleryRender();
    }, 30);
  });
});

// ═══════════════════════════════════════════════════════════════════════
// Gallery
// ═══════════════════════════════════════════════════════════════════════
// ═══════════════════════════════════════════════════════════════════════
// Memory Haze — opacity decay + reuse
// ═══════════════════════════════════════════════════════════════════════
const hazeCanvas = document.getElementById('haze-canvas');
const hazeCtx = hazeCanvas.getContext('2d');
const HAZE_LABELS = [
  'birthday party', 'job interview', 'flow state', 'beach vacation', 'grief',
  'first kiss', 'learning bike', 'final exam', 'shared joke', 'waiting room',
  'morning coffee', 'deadline rush', 'graduation', 'car accident', 'meditation',
  'heartbreak', 'treehouse', 'public speaking', "grandma's kitchen", 'first day school',
  'concert', 'pet loss', 'road trip', 'injury',
];
const hazeNodes = [];
(function hazeInit() {
  const W = 960, H = 460;
  const cols = 6, rows = 4;
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const idx = r * cols + c;
      if (idx >= HAZE_LABELS.length) break;
      hazeNodes.push({
        x: 90 + c * 140,
        y: 60 + r * 100,
        label: HAZE_LABELS[idx],
        encodedDaysAgo: Math.random() * 40,  // random encoding time 0-40 days ago
        baseOpacity: 0.85 + Math.random() * 0.15,
      });
    }
  }
})();
function hazeTimeDays() { return parseFloat(document.getElementById('haze-time').value); }
function hazeHalfLife() { return parseFloat(document.getElementById('haze-halflife').value); }
function hazeEffective(node) {
  const elapsed = hazeTimeDays() + node.encodedDaysAgo;
  const hl = hazeHalfLife();
  return Math.max(0.05, node.baseOpacity * Math.pow(0.5, elapsed / hl));
}
function hazeReinforce() {
  // Pick a random node and re-encode it (strength back up, clock reset)
  const candidates = hazeNodes.filter(n => hazeEffective(n) > 0.1);
  if (!candidates.length) return;
  const pick = candidates[Math.floor(Math.random() * candidates.length)];
  pick.encodedDaysAgo = -hazeTimeDays();  // so elapsed becomes 0
  pick.baseOpacity = 1.0;
  pick.reinforced = Date.now();
  pepSend('haze.reinforce', { label: pick.label });
}
function hazeReset() {
  hazeNodes.forEach(n => {
    n.encodedDaysAgo = Math.random() * 40;
    n.baseOpacity = 0.85 + Math.random() * 0.15;
    delete n.reinforced;
  });
  document.getElementById('haze-time').value = 0;
  document.getElementById('haze-time-v').textContent = '0 days';
}
function hazeOld() {
  // Simulate a 70-year-old's memory landscape. Scale: 1 unit = 1 year.
  // Total lifespan: 70 years. Use half-life of 8 years so raw decay is
  // visible; youth memories get heavy reinforcement to simulate decades
  // of retelling; middle decades get minimal reinforcement; recent
  // years stay bright simply because they haven't decayed yet.
  // We store encodedDaysAgo in "years" here since the unit is symbolic.
  // Set half-life slider so the math lines up visually.
  document.getElementById('haze-halflife').value = 8;
  document.getElementById('haze-halflife-v').textContent = '8 days';
  document.getElementById('haze-time').value = 0;
  document.getElementById('haze-time-v').textContent = '0 days';
  hazeNodes.forEach((n, i) => {
    // Distribute the 24 nodes across the 70-year lifespan
    // cluster 1: ages 15-25 (youth / reminiscence bump) — 8 nodes
    // cluster 2: ages 25-55 (middle decades) — 10 nodes
    // cluster 3: ages 60-70 (recent) — 6 nodes
    let ageAtEncoding, reinforced;
    if (i < 8) {
      // Youth — encoded ~45-55 years ago, reinforced many times
      ageAtEncoding = 15 + (i / 8) * 10;
      const yearsAgo = 70 - ageAtEncoding;
      // Repeated reinforcement means the effective encoded_at is much
      // more recent than the first encoding. Simulate: pull encodedDaysAgo
      // forward by a large fraction.
      n.encodedDaysAgo = yearsAgo * 0.15;  // 85% of the decay time was erased by retelling
      n.baseOpacity = 0.95;
      n.reinforcedYouth = true;
    } else if (i < 18) {
      // Middle decades — encoded ~15-45 years ago, minimal reinforcement
      ageAtEncoding = 25 + ((i - 8) / 10) * 30;
      const yearsAgo = 70 - ageAtEncoding;
      n.encodedDaysAgo = yearsAgo * 0.9;  // almost full decay
      n.baseOpacity = 0.75;
      delete n.reinforcedYouth;
    } else {
      // Recent years — encoded ~0-10 years ago, no reinforcement needed
      ageAtEncoding = 60 + ((i - 18) / 6) * 10;
      const yearsAgo = 70 - ageAtEncoding;
      n.encodedDaysAgo = yearsAgo;
      n.baseOpacity = 0.85;
      delete n.reinforcedYouth;
    }
    n.ageLabel = Math.round(ageAtEncoding);
    delete n.reinforced;
  });
  pepSend('haze.reminiscence_bump', {});
}
['haze-time','haze-halflife'].forEach(id => {
  const el = document.getElementById(id);
  if (!el) return;
  el.addEventListener('input', (e) => {
    const v = parseFloat(e.target.value);
    const out = document.getElementById(id + '-v');
    if (out) out.textContent = v + ' days';
  });
});
function drawHaze() {
  const W = 960, H = 460;
  hazeCtx.fillStyle = themeBg(); hazeCtx.fillRect(0, 0, W, H);
  let reusableCount = 0;
  hazeNodes.forEach(n => {
    const op = hazeEffective(n);
    const reusable = op < 0.15;
    if (reusable) reusableCount++;
    const r = 28 + op * 14;
    // Node circle with opacity-based alpha
    hazeCtx.fillStyle = `rgba(186, 104, 200, ${op.toFixed(3)})`;
    hazeCtx.beginPath(); hazeCtx.arc(n.x, n.y, r, 0, Math.PI * 2); hazeCtx.fill();
    // Halo if recently reinforced
    if (n.reinforced && Date.now() - n.reinforced < 1200) {
      const age = (Date.now() - n.reinforced) / 1200;
      hazeCtx.strokeStyle = `rgba(163, 230, 53, ${(1 - age).toFixed(3)})`;
      hazeCtx.lineWidth = 3;
      hazeCtx.beginPath(); hazeCtx.arc(n.x, n.y, r + 8 + age * 20, 0, Math.PI * 2); hazeCtx.stroke();
    }
    // Reuse marker: dashed outline
    if (reusable) {
      hazeCtx.strokeStyle = 'rgba(248, 113, 113, 0.8)';
      hazeCtx.lineWidth = 1.5;
      hazeCtx.setLineDash([4, 4]);
      hazeCtx.beginPath(); hazeCtx.arc(n.x, n.y, r + 4, 0, Math.PI * 2); hazeCtx.stroke();
      hazeCtx.setLineDash([]);
    } else {
      hazeCtx.strokeStyle = `rgba(186, 104, 200, ${Math.min(1, op + 0.2).toFixed(3)})`;
      hazeCtx.lineWidth = 1.5;
      hazeCtx.beginPath(); hazeCtx.arc(n.x, n.y, r, 0, Math.PI * 2); hazeCtx.stroke();
    }
    // Label
    hazeCtx.fillStyle = `rgba(255, 255, 255, ${Math.max(0.4, op).toFixed(3)})`;
    hazeCtx.font = '10px monospace';
    hazeCtx.textAlign = 'center';
    hazeCtx.fillText(n.label, n.x, n.y + r + 14);
    // Opacity score
    hazeCtx.fillStyle = `rgba(200, 200, 200, ${Math.max(0.3, op).toFixed(3)})`;
    hazeCtx.font = 'bold 10px monospace';
    hazeCtx.fillText(op.toFixed(2), n.x, n.y + 3);
    // Age-at-encoding label (only in 70-year-old mode)
    if (n.ageLabel !== undefined) {
      const col = n.reinforcedYouth ? '163, 230, 53' : '138, 122, 142';
      hazeCtx.fillStyle = `rgba(${col}, ${Math.max(0.5, op).toFixed(3)})`;
      hazeCtx.font = '9px monospace';
      hazeCtx.fillText(`age ${n.ageLabel}`, n.x, n.y + r + 26);
    }
  });
  // Footer
  hazeCtx.fillStyle = '#aaa'; hazeCtx.font = '11px monospace'; hazeCtx.textAlign = 'left';
  hazeCtx.fillText(`t = ${hazeTimeDays()} days · half-life = ${hazeHalfLife()} days`, 20, 24);
  hazeCtx.fillStyle = reusableCount > 0 ? '#f06292' : '#81c784'; hazeCtx.textAlign = 'right';
  hazeCtx.fillText(`${reusableCount} node(s) available for reuse`, W - 20, 24);
  requestAnimationFrame(drawHaze);
}
drawHaze();

// ═══════════════════════════════════════════════════════════════════════
// Media & Brain — how each medium retrains the prediction engine
// ═══════════════════════════════════════════════════════════════════════
const MEDIA_TYPES = {
  books:  { label: 'BOOKS',        col: '#a78bfa', predWindow: 0.95, bandwidth: 0.92, residualThresh: 0.20, consolidation: 0.95, retention: 0.85, networkDepth: 0.90 },
  tv:     { label: 'TV SHOWS',     col: '#4fc3f7', predWindow: 0.65, bandwidth: 0.68, residualThresh: 0.35, consolidation: 0.60, retention: 0.55, networkDepth: 0.60 },
  movies: { label: 'MOVIES',       col: '#81c784', predWindow: 0.75, bandwidth: 0.78, residualThresh: 0.30, consolidation: 0.45, retention: 0.50, networkDepth: 0.65 },
  social: { label: 'SOCIAL MEDIA', col: '#ffb74d', predWindow: 0.25, bandwidth: 0.30, residualThresh: 0.70, consolidation: 0.15, retention: 0.18, networkDepth: 0.20 },
  short:  { label: 'SHORT-FORM',   col: '#f06292', predWindow: 0.10, bandwidth: 0.15, residualThresh: 0.88, consolidation: 0.08, retention: 0.10, networkDepth: 0.08 },
};
const MEDIA_DIMS = [
  { key: 'predWindow',     label: 'Prediction window',     desc: 'how far ahead the predictor holds state', goodHigh: true },
  { key: 'bandwidth',      label: 'Bandwidth allocation',  desc: 'sustained attention capacity',             goodHigh: true },
  { key: 'residualThresh', label: 'Residual threshold',    desc: 'how much surprise needed to feel engaged', goodHigh: false },
  { key: 'consolidation',  label: 'Consolidation gap',     desc: 'time between inputs for deep encoding',    goodHigh: true },
  { key: 'retention',      label: 'Content retention',     desc: 'how much you remember afterward',          goodHigh: true },
  { key: 'networkDepth',   label: 'Semantic network depth', desc: 'how many hops activation reaches',        goodHigh: true },
];
let mediaTrainedOn = 'books';
const mediaCanvas = document.getElementById('media-canvas');
const mediaCtx = mediaCanvas.getContext('2d');

function mediaTrain(type) {
  mediaTrainedOn = type;
  document.querySelectorAll('.media-btn').forEach(b => b.classList.remove('media-active'));
  const btn = document.getElementById('media-' + type);
  if (btn) btn.classList.add('media-active');
}

function drawMedia() {
  const W = 960, H = 560;
  mediaCtx.fillStyle = themeBg(); mediaCtx.fillRect(0, 0, W, H);
  const months = parseInt(document.getElementById('media-months').value);
  const trainFactor = Math.min(1, months / 12);
  const trained = MEDIA_TYPES[mediaTrainedOn];

  mediaCtx.fillStyle = trained.col; mediaCtx.font = 'bold 14px monospace'; mediaCtx.textAlign = 'left';
  mediaCtx.fillText('TRAINED ON: ' + trained.label + ' (' + months + ' months)', 30, 30);
  mediaCtx.fillStyle = '#aaa'; mediaCtx.font = '10px monospace';
  mediaCtx.fillText('Each column shows the brain adapted to that medium. Green = healthy for deep cognition; red = degraded.', 30, 50);

  const types = Object.entries(MEDIA_TYPES);
  const colW = (W - 60) / types.length;

  types.forEach(function(entry, col) {
    var key = entry[0], mt = entry[1];
    var x = 30 + col * colW;
    var isActive = key === mediaTrainedOn;

    mediaCtx.fillStyle = isActive ? mt.col : '#666';
    mediaCtx.font = isActive ? 'bold 11px monospace' : '10px monospace';
    mediaCtx.textAlign = 'center';
    mediaCtx.fillText(mt.label, x + colW / 2, 82);
    if (isActive) {
      mediaCtx.fillStyle = mt.col + '22';
      mediaCtx.fillRect(x + 4, 68, colW - 8, H - 100);
    }

    MEDIA_DIMS.forEach(function(dim, row) {
      var y = 100 + row * 72;
      var baseVal = mt[dim.key];
      var adaptedVal;
      if (key === mediaTrainedOn) {
        adaptedVal = baseVal;
      } else {
        var trainedVal = trained[dim.key];
        if (dim.goodHigh) {
          adaptedVal = baseVal * (1 - trainFactor * 0.6 * (1 - trainedVal));
        } else {
          adaptedVal = baseVal + trainFactor * 0.4 * (trainedVal - baseVal);
        }
        adaptedVal = Math.max(0, Math.min(1, adaptedVal));
      }

      if (col === 0) {
        mediaCtx.fillStyle = '#ccc'; mediaCtx.font = 'bold 10px monospace'; mediaCtx.textAlign = 'left';
        mediaCtx.fillText(dim.label, 30, y + 6);
        mediaCtx.fillStyle = '#666'; mediaCtx.font = '9px monospace';
        mediaCtx.fillText(dim.desc, 30, y + 20);
      }

      var barX = x + 10, barW = colW - 20, barY = y + 28, barH = 22;
      mediaCtx.fillStyle = 'rgba(120,120,130,0.15)';
      mediaCtx.fillRect(barX, barY, barW, barH);

      var healthColor;
      if (dim.goodHigh) {
        healthColor = adaptedVal > 0.6 ? '129,199,132' : adaptedVal > 0.35 ? '255,183,77' : '248,113,113';
      } else {
        healthColor = adaptedVal < 0.35 ? '129,199,132' : adaptedVal < 0.60 ? '255,183,77' : '248,113,113';
      }
      mediaCtx.fillStyle = 'rgba(' + healthColor + ', 0.75)';
      mediaCtx.fillRect(barX, barY, barW * adaptedVal, barH);

      mediaCtx.fillStyle = '#fff'; mediaCtx.font = '10px monospace'; mediaCtx.textAlign = 'center';
      mediaCtx.fillText((adaptedVal * 100).toFixed(0), barX + barW / 2, barY + 14);
    });
  });

  mediaCtx.fillStyle = '#666'; mediaCtx.font = '10px monospace'; mediaCtx.textAlign = 'center';
  mediaCtx.fillText('green = healthy for deep cognition \u00b7 yellow = moderate \u00b7 red = degraded by training regime', W / 2, H - 14);
  requestAnimationFrame(drawMedia);
}
drawMedia();

// ═══════════════════════════════════════════════════════════════════════
// Vectora-Powered Live Retrieval (dogfood)
// ═══════════════════════════════════════════════════════════════════════
async function vecAxonaInit() {
  try {
    const r = await fetch('/vectora/seeds/axona');
    const data = await r.json();
    const sel = document.getElementById('vec-axona-seed');
    if (!sel) return;
    sel.innerHTML = data.seeds.map(s => `<option value="${s.id}">${s.id} — ${s.text.split(' ').slice(0, 5).join(' ')}</option>`).join('');
    const stats = document.getElementById('vec-axona-stats');
    if (stats) stats.textContent = `seeded graph: ${data.stats.documents} docs · ${data.stats.edges} edges`;
  } catch (e) { console.warn('vec axona init failed', e); }
}
['vec-axona-k', 'vec-axona-decay'].forEach(id => {
  const el = document.getElementById(id);
  if (!el) return;
  el.addEventListener('input', (e) => {
    const v = parseInt(e.target.value);
    const out = document.getElementById(id + '-v');
    if (!out) return;
    out.textContent = id.endsWith('decay') ? (v / 100).toFixed(2) : v;
  });
});
async function vecAxonaQuery() {
  const seed = document.getElementById('vec-axona-seed').value;
  if (!seed) return;
  const k = parseInt(document.getElementById('vec-axona-k').value);
  const decay = parseInt(document.getElementById('vec-axona-decay').value) / 100;
  const out = document.getElementById('vec-axona-results');
  out.innerHTML = '<div style="color:var(--dim);text-align:center;padding:40px 20px;font-size:11px">querying Vectora…</div>';
  try {
    const r = await fetch(`/vectora/neighbors/axona/${seed}?k=${k}&decay=${decay}`);
    if (!r.ok) throw new Error('retrieval failed');
    const data = await r.json();
    if (!data.hits.length) { out.innerHTML = '<div style="color:var(--dim);text-align:center;padding:40px 20px;font-size:11px">no neighbors</div>'; return; }
    out.innerHTML = data.hits.map((h, i) => {
      const hopBadge = h.hop_distance > 0 ? `<span style="background:rgba(186,104,200,0.2);color:var(--accent);padding:1px 6px;border-radius:8px;font-size:9px;margin-left:6px">hop ${h.hop_distance}</span>` : '';
      return `<div style="background:var(--surface);border:1px solid var(--border);border-left:3px solid var(--accent);border-radius:4px;padding:10px 14px;margin-bottom:6px">
        <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
          <span style="color:var(--accent);font-weight:bold;font-family:monospace">${i+1}. ${h.id}</span>
          <span style="color:var(--dim);margin-left:auto;font-size:10px">score ${h.score.toFixed(3)}${hopBadge}</span>
        </div>
        <div style="font-size:11px;color:var(--text);margin-top:4px;line-height:1.55">${h.text}</div>
      </div>`;
    }).join('');
    pepSend('vectora.query', { seed, k, decay });
  } catch (e) {
    out.innerHTML = `<div style="color:#f06292;text-align:center;padding:40px 20px;font-size:11px">Error: ${e.message}</div>`;
  }
}
vecAxonaInit();

// ═══════════════════════════════════════════════════════════════════════
// Cognitive State Workbench
// ═══════════════════════════════════════════════════════════════════════
const AX_WORKBENCH_DATA = [
  {
    label: 'Burned-out engineer (3 months)',
    description: '"I can\\'t focus, every task feels heavy. I open my IDE and stare at it. I used to love this work. Sleep is broken — 4-5 hours, then I\\'m up. Everything sounds louder than it is."',
    state: { novelty: 0.15, coherence: 0.35, bandwidth: 0.20, valence: -0.6 },
    quadrant: 'STAGNATION',
    mechanisms: ['Cognitive Bandwidth', 'Trauma Loops', 'Sleep & Consolidation', 'Depression', 'Learned Helplessness'],
    intervention: 'Sleep restoration first (consolidation is the bottleneck). Then bandwidth recovery via 2-week reduced-load period. Avoid novelty injection until coherence returns; new projects will deepen stagnation, not lift it.',
  },
  {
    label: 'Athlete in flow state',
    description: '"Time slowed down. Every move felt obvious before I made it. I wasn\\'t thinking about the crowd or the score — just the next play. Felt effortless even though I was at the limit physically."',
    state: { novelty: 0.55, coherence: 0.92, bandwidth: 0.85, valence: 0.85 },
    quadrant: 'GENIUS',
    mechanisms: ['Flow State', 'Hyperfocus', 'Time Perception', 'Attention Spotlight', 'Reward Prediction Error'],
    intervention: 'No intervention needed. Map the conditions (sleep, pre-game routine, opponent, environment) that produced this state. Replicate, do not optimize. Optimization breaks flow.',
  },
  {
    label: 'PTSD trauma loop replay',
    description: '"I keep replaying that night. Same images, same order, every time. I tried to stop thinking about it but it just comes back. Loud noises put me right back there. I\\'m exhausted but I don\\'t want to sleep."',
    state: { novelty: 0.05, coherence: 0.65, bandwidth: 0.25, valence: -0.85 },
    quadrant: 'STAGNATION (high-emotion variant)',
    mechanisms: ['Trauma Loops', 'Memory Reconsolidation', 'Fear Conditioning', 'Rumination', 'Sleep & Consolidation'],
    intervention: 'EMDR or memory reconsolidation protocol — re-encode the trauma trace during reactivation, not avoidance. Track brightness reduction across sessions. Re-traumatization risk if reactivation is too strong; titrate.',
  },
  {
    label: 'Manic episode (early stage)',
    description: '"Ideas are coming faster than I can write them down. I haven\\'t slept properly in 4 days but I feel amazing. Everything connects to everything. I started 7 projects this week and they\\'re all going to change everything."',
    state: { novelty: 0.95, coherence: 0.20, bandwidth: 0.90, valence: 0.75 },
    quadrant: 'CHAOS',
    mechanisms: ['Cognitive Bandwidth', 'Sleep & Consolidation', 'Pharmacology', 'Belief Propagation', 'Creativity Under Constraint'],
    intervention: 'Clinical urgency — sleep restoration is the critical lever; without sleep, mania escalates. Mood stabilization (medical), reduce stimulus, reduce decision-making load. The "everything connects" feeling is the chaos quadrant; coherence will not return without sleep.',
  },
  {
    label: 'Curious child learning',
    description: '"Why does the moon follow us in the car? Why is water wet? Where does my voice go after I stop talking? I drew a picture of how I think the inside of a clock works."',
    state: { novelty: 0.85, coherence: 0.70, bandwidth: 0.85, valence: 0.85 },
    quadrant: 'GENIUS (developing)',
    mechanisms: ['Curiosity / Boredom', 'Statistical Learning', 'Spreading Activation', 'Memory & Encoding', 'Development & Aging'],
    intervention: 'No intervention; protect the conditions. High novelty + high coherence + low pressure produces the developmental sweet spot. Avoid forced rote learning, which collapses bandwidth and converts curiosity into compliance.',
  },
];
const axWorkbenchCanvas = document.getElementById('axona-workbench-canvas');
const axWorkbenchCtx = axWorkbenchCanvas.getContext('2d');
let axWorkbenchActive = null;
function axWorkbenchPick(i) { axWorkbenchActive = i; pepSend('ax.workbench', { i }); }
function axWrap(ctx, text, x, y, maxW, lineH) {
  const words = text.split(' '); let line = '', yy = y;
  words.forEach(w => {
    const test = line + w + ' ';
    if (ctx.measureText(test).width > maxW && line) { ctx.fillText(line.trim(), x, yy); line = w + ' '; yy += lineH; }
    else { line = test; }
  });
  if (line) ctx.fillText(line.trim(), x, yy);
  return yy;
}
function drawAxWorkbench() {
  const W = 960, H = 560; axWorkbenchCtx.fillStyle = themeBg(); axWorkbenchCtx.fillRect(0, 0, W, H);
  if (axWorkbenchActive == null) {
    axWorkbenchCtx.fillStyle = '#778'; axWorkbenchCtx.font = '11px monospace'; axWorkbenchCtx.textAlign = 'center';
    axWorkbenchCtx.fillText('(pick a description)', W / 2, H / 2);
    requestAnimationFrame(drawAxWorkbench); return;
  }
  const d = AX_WORKBENCH_DATA[axWorkbenchActive];
  axWorkbenchCtx.fillStyle = '#dce4ed'; axWorkbenchCtx.font = 'bold 13px monospace'; axWorkbenchCtx.textAlign = 'left';
  axWorkbenchCtx.fillText(d.label.toUpperCase(), 30, 30);
  axWorkbenchCtx.fillStyle = '#aab'; axWorkbenchCtx.font = 'italic 11px monospace';
  axWrap(axWorkbenchCtx, d.description, 30, 54, W - 60, 14);
  // Three columns
  const colY = 130;
  // Column 1: State-space
  axWorkbenchCtx.fillStyle = '#ba68c8'; axWorkbenchCtx.font = 'bold 11px monospace';
  axWorkbenchCtx.fillText('STATE-SPACE COORDINATES', 30, colY);
  const axes = [['novelty', '#81c784'], ['coherence', '#4fc3f7'], ['bandwidth', '#ffb74d'], ['valence', '#f06292']];
  axes.forEach((a, i) => {
    const y = colY + 28 + i * 36;
    axWorkbenchCtx.fillStyle = '#dce4ed'; axWorkbenchCtx.font = '10px monospace';
    axWorkbenchCtx.fillText(a[0], 30, y);
    axWorkbenchCtx.fillStyle = 'rgba(120,130,140,0.2)'; axWorkbenchCtx.fillRect(30, y + 6, 240, 14);
    const v = d.state[a[0]];
    if (a[0] === 'valence') {
      axWorkbenchCtx.fillStyle = 'rgba(' + (v < 0 ? '248,113,113' : '129,199,132') + ',0.3)';
      axWorkbenchCtx.fillRect(30, y + 6, 240, 14);
      axWorkbenchCtx.fillStyle = 'rgba(' + (v < 0 ? '248,113,113' : '129,199,132') + ',0.85)';
      const w = Math.abs(v) * 120;
      const x = v < 0 ? 30 + 120 - w : 30 + 120;
      axWorkbenchCtx.fillRect(x, y + 6, w, 14);
    } else {
      axWorkbenchCtx.fillStyle = a[1].replace('#', 'rgba(') + ',0.3)';
      axWorkbenchCtx.fillStyle = a[1] + '55';
      axWorkbenchCtx.fillRect(30, y + 6, 240 * v, 14);
      axWorkbenchCtx.fillStyle = a[1];
      axWorkbenchCtx.fillRect(30, y + 6, 240 * v, 14);
    }
    axWorkbenchCtx.fillStyle = '#fff'; axWorkbenchCtx.font = '10px monospace'; axWorkbenchCtx.textAlign = 'right';
    axWorkbenchCtx.fillText(v.toFixed(2), 268, y + 17);
    axWorkbenchCtx.textAlign = 'left';
  });
  axWorkbenchCtx.fillStyle = '#ba68c8'; axWorkbenchCtx.font = 'bold 11px monospace';
  axWorkbenchCtx.fillText('QUADRANT:', 30, colY + 200);
  axWorkbenchCtx.fillStyle = '#fff'; axWorkbenchCtx.font = 'bold 12px monospace';
  axWorkbenchCtx.fillText(d.quadrant, 130, colY + 200);
  // Column 2: Mechanisms
  axWorkbenchCtx.fillStyle = '#4fc3f7'; axWorkbenchCtx.font = 'bold 11px monospace';
  axWorkbenchCtx.fillText('MATCHED MECHANISMS', 320, colY);
  d.mechanisms.forEach((m, i) => {
    const y = colY + 28 + i * 24;
    axWorkbenchCtx.fillStyle = 'rgba(79,195,247,0.15)';
    axWorkbenchCtx.fillRect(320, y - 12, 240, 18);
    axWorkbenchCtx.fillStyle = '#dce4ed'; axWorkbenchCtx.font = '11px monospace';
    axWorkbenchCtx.fillText('• ' + m, 328, y + 1);
  });
  // Column 3: Intervention
  axWorkbenchCtx.fillStyle = '#81c784'; axWorkbenchCtx.font = 'bold 11px monospace';
  axWorkbenchCtx.fillText('PREDICTED INTERVENTION', 600, colY);
  axWorkbenchCtx.fillStyle = '#dce4ed'; axWorkbenchCtx.font = '11px monospace';
  axWrap(axWorkbenchCtx, d.intervention, 600, colY + 28, 340, 16);
  // Footer disclaimer
  axWorkbenchCtx.fillStyle = '#778'; axWorkbenchCtx.font = '10px monospace'; axWorkbenchCtx.textAlign = 'center';
  axWorkbenchCtx.fillText('synthetic descriptions; not a clinical tool — illustrates the mapping primitive', W / 2, H - 16);
  requestAnimationFrame(drawAxWorkbench);
}
drawAxWorkbench();

// ═══════════════════════════════════════════════════════════════════════
// Cognitive State Detection Benchmark
// ═══════════════════════════════════════════════════════════════════════
const axBenchCanvas = document.getElementById('ax-bench-canvas');
const axBenchCtx = axBenchCanvas.getContext('2d');
let axBenchData = null;
function axBenchGen() {
  axBenchData = {
    base: { acc: 0.58 + (Math.random() - 0.5) * 0.04, subtle: 0.22 + (Math.random() - 0.5) * 0.04, fpr: 0.31 + (Math.random() - 0.5) * 0.03, ttd: 24 + Math.random() * 6, cost: 1.0 },
    ax:   { acc: 0.84 + (Math.random() - 0.5) * 0.04, subtle: 0.69 + (Math.random() - 0.5) * 0.04, fpr: 0.13 + (Math.random() - 0.5) * 0.03, ttd: 4 + Math.random() * 2, cost: 1.0 + 0.65 + Math.random() * 0.1 },
  };
}
axBenchGen();
function axBenchRegen() { axBenchGen(); pepSend('ax.bench.regen', {}); }
function drawAxBench() {
  const W = 960, H = 640; axBenchCtx.fillStyle = themeBg(); axBenchCtx.fillRect(0, 0, W, H);
  if (!axBenchData) { requestAnimationFrame(drawAxBench); return; }
  const d = axBenchData;
  const metrics = [
    { label: 'State classification accuracy',  b: d.base.acc,    a: d.ax.acc,    fmt: (v) => (v * 100).toFixed(1) + '%', higher: true },
    { label: 'Subtle change detection',         b: d.base.subtle, a: d.ax.subtle, fmt: (v) => (v * 100).toFixed(1) + '%', higher: true },
    { label: 'False-positive rate on noise',    b: d.base.fpr,    a: d.ax.fpr,    fmt: (v) => (v * 100).toFixed(1) + '%', higher: false },
    { label: 'Time-to-detection (hours)',       b: d.base.ttd / 36, a: d.ax.ttd / 36, fmt: (v) => (v * 36).toFixed(1) + 'h', higher: false },
    { label: 'Compute cost (index)',            b: d.base.cost / 2.0, a: d.ax.cost / 2.0, fmt: (v) => (v * 2.0).toFixed(2) + 'x', higher: false },
  ];
  axBenchCtx.fillStyle = '#aaa'; axBenchCtx.font = '11px monospace'; axBenchCtx.textAlign = 'left';
  axBenchCtx.fillText('500 synthetic subjects with known states · standard assessment (purple) vs Axona-augmented (pink)', 30, 24);
  const barW = 340, barH = 28, gap = 36;
  metrics.forEach((m, i) => {
    const y = 50 + i * (barH * 2 + gap);
    axBenchCtx.fillStyle = '#dce4ed'; axBenchCtx.font = 'bold 12px monospace'; axBenchCtx.textAlign = 'left';
    axBenchCtx.fillText(m.label, 30, y);
    axBenchCtx.fillStyle = 'rgba(167,139,250,0.25)'; axBenchCtx.fillRect(30, y + 8, barW, barH);
    axBenchCtx.fillStyle = 'rgba(167,139,250,0.85)'; axBenchCtx.fillRect(30, y + 8, barW * Math.min(1, m.b), barH);
    axBenchCtx.fillStyle = '#fff'; axBenchCtx.font = '11px monospace'; axBenchCtx.textAlign = 'right';
    axBenchCtx.fillText('Standard: ' + m.fmt(m.b), 30 + barW - 6, y + 8 + barH / 2 + 4);
    axBenchCtx.fillStyle = 'rgba(240,98,146,0.25)'; axBenchCtx.fillRect(30, y + 8 + barH + 4, barW, barH);
    axBenchCtx.fillStyle = 'rgba(240,98,146,0.85)'; axBenchCtx.fillRect(30, y + 8 + barH + 4, barW * Math.min(1, m.a), barH);
    axBenchCtx.fillStyle = '#fff';
    axBenchCtx.fillText('Axona: ' + m.fmt(m.a), 30 + barW - 6, y + 8 + barH + 4 + barH / 2 + 4);
    const delta = m.a - m.b;
    const pct = Math.abs(m.b) > 0.001 ? (delta / m.b * 100) : 0;
    const isGood = m.higher ? delta > 0 : delta < 0;
    const col = isGood ? 'rgba(240,98,146,0.95)' : 'rgba(248,113,113,0.95)';
    axBenchCtx.fillStyle = col; axBenchCtx.font = 'bold 13px monospace'; axBenchCtx.textAlign = 'left';
    const sign = pct > 0 ? '+' : '';
    axBenchCtx.fillText(sign + pct.toFixed(0) + '%', 400, y + 8 + barH + 4);
    axBenchCtx.fillStyle = '#aaa'; axBenchCtx.font = '10px monospace';
    axBenchCtx.fillText(isGood ? 'better' : 'tradeoff', 400, y + 8 + barH + 20);
  });
  axBenchCtx.fillStyle = 'rgba(240,98,146,0.95)'; axBenchCtx.font = 'bold 11px monospace'; axBenchCtx.textAlign = 'center';
  axBenchCtx.fillText('synthetic ground-truth states; clinical validation is what Wedge 2 (Pitch tab) is designed to fund', W / 2, H - 20);
  requestAnimationFrame(drawAxBench);
}
drawAxBench();

function galleryCollectItems() {
  // Build a list of {id, title, tabLabel, panelId, bookmarked}
  const out = [];
  const tabs = Array.from(document.querySelectorAll('.tab'));
  const skipPanelIds = new Set(['gallery-tab', 'pep-link-tab', 'reference-tab', 'applications-tab']);
  const bmks = new Set(axonaBookmarks());
  tabs.forEach(tab => {
    const pid = tab.dataset.panel;
    if (!pid || skipPanelIds.has(pid)) return;
    const panel = document.getElementById(pid);
    if (!panel) return;
    const tabLabel = tab.textContent.trim();
    const h3s = Array.from(panel.querySelectorAll('h3'));
    if (h3s.length > 1) {
      h3s.forEach((h3, idx) => {
        if (!h3.id) h3.id = pid + '-sub-' + idx;
        let title = h3.textContent.trim();
        const dashIdx = title.indexOf('—');
        if (dashIdx > 0) title = title.slice(0, dashIdx).trim();
        out.push({ id: h3.id, title, tabLabel, panelId: pid, bookmarked: bmks.has(h3.id) });
      });
    } else {
      const h2 = panel.querySelector('h2');
      let title = h2 ? h2.textContent.trim() : pid;
      const dashIdx = title.indexOf('—');
      if (dashIdx > 0) title = title.slice(0, dashIdx).trim();
      out.push({ id: pid, title, tabLabel, panelId: pid, bookmarked: bmks.has(pid) });
    }
  });
  return out;
}
function galleryClearFilter() {
  const inp = document.getElementById('gallery-filter');
  if (inp) { inp.value = ''; galleryRender(); }
}
function galleryRender() {
  const grid = document.getElementById('gallery-grid');
  if (!grid) return;
  const items = galleryCollectItems();
  const q = (document.getElementById('gallery-filter')?.value || '').toLowerCase().trim();
  const filtered = q ? items.filter(it => (it.title + ' ' + it.tabLabel).toLowerCase().includes(q)) : items;
  // Sort: bookmarked first, then by tab, then by title
  filtered.sort((a, b) => {
    if (a.bookmarked !== b.bookmarked) return a.bookmarked ? -1 : 1;
    if (a.tabLabel !== b.tabLabel) return a.tabLabel.localeCompare(b.tabLabel);
    return a.title.localeCompare(b.title);
  });
  const totalEl = document.getElementById('gallery-total');
  const bmEl = document.getElementById('gallery-bm-count');
  if (totalEl) totalEl.textContent = items.length;
  if (bmEl) bmEl.textContent = items.filter(i => i.bookmarked).length;
  if (!filtered.length) {
    grid.innerHTML = '<span style="color:var(--dim)">no matches</span>';
    return;
  }
  grid.innerHTML = filtered.map(it => {
    const star = it.bookmarked ? '★ ' : '';
    return '<div onclick="galleryJump(\\'' + it.id + '\\')" ' +
      'style="background:var(--surface);border:1px solid ' + (it.bookmarked ? 'var(--accent)' : 'var(--border)') + ';' +
      'border-radius:6px;padding:12px 14px;cursor:pointer;transition:border-color 0.15s" ' +
      'onmouseover="this.style.borderColor=\\'var(--accent)\\'" ' +
      'onmouseout="this.style.borderColor=\\'' + (it.bookmarked ? 'var(--accent)' : 'var(--border)') + '\\'">' +
      '<div style="font-size:9px;color:var(--dim);letter-spacing:0.08em;text-transform:uppercase;margin-bottom:4px">' + it.tabLabel + '</div>' +
      '<div style="font-size:12px;color:var(--text);font-weight:bold">' + star + it.title + '</div>' +
      '</div>';
  }).join('');
}
function galleryJump(id) { canvasSelect(id); }
setTimeout(() => { if (document.querySelector('.panel.active')?.id === 'gallery-tab') galleryRender(); }, 120);

(function installGlossary() {
  const terms = {
    'prior': 'A stored expectation the brain uses to predict the next input.',
    'priors': 'Stored expectations the brain uses to predict the next input.',
    'residual': 'Prediction error — the gap between forecast and reality.',
    'residuals': 'Prediction errors — gaps between forecast and reality.',
    'predictor': 'The subsystem that generates expectations about what comes next.',
    'bandwidth': 'Spare processing capacity available for deliberate cognition.',
    'coherence': 'How well new ideas integrate into stable structure.',
    'novelty': 'Rate at which new patterns arrive and get encoded.',
    'DMN': 'Default Mode Network — runs when no task is active, substrate of self-referential thought.',
    'amygdala': 'Almond-shaped region central to fear learning and threat detection.',
    'hippocampus': 'Structure required for forming new episodic and declarative memories.',
    'dopamine': 'Neurotransmitter carrying the reward prediction error signal.',
    'proprioception': 'The sense of where your body parts are in space.',
    'interoception': 'The sense of the internal state of your body.',
    'System 1': 'Fast, parallel, intuitive pattern-matching.',
    'System 2': 'Slow, serial, deliberate reasoning.',
  };
  const tooltip = document.createElement('div');
  tooltip.style.cssText = 'position:fixed;display:none;background:#1a1a2e;border:1px solid #ba68c8;border-radius:4px;padding:8px 12px;font-family:monospace;font-size:11px;color:#e0e0e0;max-width:320px;line-height:1.5;z-index:200;pointer-events:none;box-shadow:0 4px 12px rgba(0,0,0,0.5)';
  document.body.appendChild(tooltip);
  const termKeys = Object.keys(terms).sort((a, b) => b.length - a.length);
  document.querySelectorAll('.info').forEach(info => {
    termKeys.forEach(term => {
      const re = new RegExp('(^|[^a-zA-Z0-9_-])(' + term + ')(?=[^a-zA-Z0-9_-]|$)', 'gi');
      info.innerHTML = info.innerHTML.replace(re, function(m, pre, word) {
        return pre + '<span class="gloss" data-term="' + term + '" style="border-bottom:1px dotted rgba(186,104,200,0.6);cursor:help">' + word + '</span>';
      });
    });
  });
  document.querySelectorAll('.gloss').forEach(el => {
    el.addEventListener('mouseenter', (e) => {
      const def = terms[el.dataset.term];
      if (!def) return;
      tooltip.innerHTML = '<b style="color:#ba68c8">' + el.dataset.term + '</b><br>' + def;
      tooltip.style.display = 'block';
    });
    el.addEventListener('mousemove', (e) => {
      tooltip.style.left = (e.clientX + 14) + 'px';
      tooltip.style.top  = (e.clientY + 14) + 'px';
    });
    el.addEventListener('mouseleave', () => { tooltip.style.display = 'none'; });
  });
})();

// ═══════════════════════════════════════════════════════════════════════
// Light mode toggle
// ═══════════════════════════════════════════════════════════════════════
function toggleLight() {
  const isLight = document.body.classList.toggle('light');
  const btn = document.getElementById('light-btn');
  if (btn) btn.textContent = isLight ? 'Dark Mode' : 'Light Mode';
  try { localStorage.setItem('axona-theme', isLight ? 'light' : 'dark'); } catch (e) {}
  try { pepSend('theme.toggle', { mode: isLight ? 'light' : 'dark' }); } catch (e) {}
}
(function restoreTheme() {
  try {
    if (localStorage.getItem('axona-theme') === 'light') {
      document.body.classList.add('light');
      const btn = document.getElementById('light-btn');
      if (btn) btn.textContent = 'Dark Mode';
    }
  } catch (e) {}
})();

// ═══════════════════════════════════════════════════════════════════════
// Take a Tour — scripted walkthrough with modal overlay
// ═══════════════════════════════════════════════════════════════════════
const tourSteps = [
  { tab: 'state-space', title: 'Welcome to Axona',
    body: 'Axona is an interactive map of the mind. Every canvas is a demo of one specific cognitive mechanism. I will walk you through the main stops. You can close this at any time with the × or by hitting Escape.' },
  { tab: 'state-space', title: 'The Cognitive State Space',
    body: 'Drag the cursor inside the canvas. Horizontal is coherence, vertical is novelty. The four quadrants (genius, chaos, order, stagnation) blend smoothly as you move. The farther you go into a quadrant, the stronger its effects. Flow State is a separate attractor inside the genius quadrant.' },
  { tab: 'mind-tab', title: 'How the Mind Works',
    body: 'This tab covers memory, novelty, prediction, attention, sleep, hallucination, metaphor, déjà vu, music, and more. The Prediction vs Reality canvas near the top is the engine — most other canvases are special cases of it running under different parameters.' },
  { tab: 'influence-tab', title: 'What Changes the Network',
    body: 'Belief, bandwidth, pharmacology, collective dynamics, confirmation bias, echo chambers, temporal discounting, psychedelics. These are the forces that reshape how the network operates. The facial feedback and bidirectionality sub-sections tie back to our earlier conversation about expression as a feedback loop.' },
  { tab: 'conditions-tab', title: 'States and Conditions',
    body: 'This is where the DSM sidebar lives — click any condition in the left nav to jump to it. Below that are canvases for trauma loops, addiction, grief, depression, phantom limbs, pain, and more. The claim throughout: no condition is a broken brain; each is a configuration of the same network.' },
  { tab: 'cases-tab', title: 'Case Studies',
    body: 'Real neurology cases that isolated specific mechanisms: H.M. (no new memories), Phineas Gage (personality in the frontal lobe), Clive Wearing (seven-second present), SM (no fear), the split-brain patients, Derek Paravicini. Each of these makes one of the abstract mechanisms undeniable.' },
  { tab: 'composer-tab', title: 'Composer',
    body: 'This is where the canvases compose. Run scripted scenarios (Tired Student, First Week of Grief, Therapy Session, Creative Flow, Doomscroll Spiral) that fire actions across multiple canvases in sequence. Or use the Master Parameter Sweep to dial bandwidth, prior precision, novelty intake, reward depth, and feedback gain across the whole app at once.' },
  { tab: 'sandbox-tab', title: 'Sandbox',
    body: 'Build your own micro-brain. Add nodes, draw edges, inject activation, watch it run. Everything in Axona comes from the same three rules (nodes, edges, spreading activation). Here you can assemble them yourself.' },
  { tab: 'pep-link-tab', title: 'PEP ↔ Axona',
    body: 'The live bridge to PEP, the underlying engine. Every time you click an action in Axona, an event posts here. The top panel shows the live PEP runtime state; the event log shows the cross-talk. This is where Axona and PEP actually meet.' },
  { tab: 'state-space', title: 'That is the tour',
    body: 'Everything else — glossary tooltips on technical terms, light mode, search, download — is there to help you navigate. Poke around. Every canvas is a self-contained experiment. If a mechanism feels abstract, find the canvas for it and watch it run.' },
];
let tourIdx = 0, tourOverlay = null;
function tourStart() {
  tourIdx = 0;
  if (!tourOverlay) tourBuildOverlay();
  tourOverlay.style.display = 'flex';
  tourShowStep();
  try { pepSend('tour.start', {}); } catch (e) {}
}
function tourEnd() {
  if (tourOverlay) tourOverlay.style.display = 'none';
  try { pepSend('tour.end', { atStep: tourIdx }); } catch (e) {}
}
function tourNext() {
  tourIdx++;
  if (tourIdx >= tourSteps.length) { tourEnd(); return; }
  tourShowStep();
}
function tourPrev() {
  if (tourIdx > 0) { tourIdx--; tourShowStep(); }
}
function tourShowStep() {
  const step = tourSteps[tourIdx];
  if (!step) { tourEnd(); return; }
  // Switch tab
  const tab = document.querySelector('[data-panel="' + step.tab + '"]');
  if (tab) tab.click();
  // Re-anchor overlay in case tab click scrolled
  setTimeout(() => window.scrollTo(0, 0), 20);
  document.getElementById('tour-title').textContent = step.title;
  document.getElementById('tour-body').textContent = step.body;
  document.getElementById('tour-progress').textContent = (tourIdx + 1) + ' / ' + tourSteps.length;
  document.getElementById('tour-prev').disabled = tourIdx === 0;
  document.getElementById('tour-next').textContent = tourIdx === tourSteps.length - 1 ? 'Finish' : 'Next →';
}
function tourBuildOverlay() {
  tourOverlay = document.createElement('div');
  tourOverlay.id = 'tour-overlay';
  tourOverlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.55);z-index:300;display:none;align-items:flex-end;justify-content:center;padding-bottom:40px';
  tourOverlay.innerHTML = '' +
    '<div style="background:var(--surface);border:1px solid var(--accent);border-radius:8px;max-width:560px;padding:22px 26px;font-family:inherit;color:var(--text);box-shadow:0 10px 40px rgba(0,0,0,0.6)">' +
    '  <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px">' +
    '    <span style="font-size:10px;color:var(--dim)">TOUR</span>' +
    '    <span id="tour-progress" style="font-size:10px;color:var(--accent)"></span>' +
    '    <button onclick="tourEnd()" style="margin-left:auto;background:transparent;border:none;color:var(--dim);font-size:18px;cursor:pointer;font-family:inherit">×</button>' +
    '  </div>' +
    '  <div id="tour-title" style="font-size:15px;font-weight:bold;color:var(--accent);margin-bottom:10px"></div>' +
    '  <div id="tour-body" style="font-size:12px;line-height:1.7;color:var(--text);margin-bottom:16px"></div>' +
    '  <div style="display:flex;gap:8px;justify-content:flex-end">' +
    '    <button id="tour-prev" onclick="tourPrev()" class="nav-btn">← Back</button>' +
    '    <button id="tour-next" onclick="tourNext()" class="nav-btn" style="border-color:var(--accent2);color:var(--accent2)">Next →</button>' +
    '  </div>' +
    '</div>';
  document.body.appendChild(tourOverlay);
  // Click outside to dismiss
  tourOverlay.addEventListener('click', (e) => { if (e.target === tourOverlay) tourEnd(); });
}
document.addEventListener('keydown', (e) => {
  if (!tourOverlay || tourOverlay.style.display !== 'flex') return;
  if (e.key === 'Escape') tourEnd();
  else if (e.key === 'ArrowRight' || e.key === 'Enter') tourNext();
  else if (e.key === 'ArrowLeft') tourPrev();
});

</script>
</body>
</html>
"""


@router.get("/axona", response_class=HTMLResponse)
async def axona_page() -> str:
    return _PAGE
