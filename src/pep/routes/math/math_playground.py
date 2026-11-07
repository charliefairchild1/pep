"""Interactive math playground for PEP.

A standalone page at /math that lets you explore the mathematical concepts
behind PEP: graph theory, weighted networks, spreading activation, relevance
scoring, power/effect, and the idea lifecycle. Everything is client-side
(D3.js + vanilla JS) — no backend calls, no Ollama, no memory store needed.

This doubles as a "love of math" class project: open it in a browser, build
a graph, watch activation spread, adjust the scoring formula with sliders,
measure power and effect, merge/split/create/forget ideas.
"""

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
<title>PEP Math Playground</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
  :root {
    --bg: #0e0e10; --surface: #1a1a2e; --surface2: #16213e;
    --text: #e0e0e0; --dim: #888; --accent: #4fc3f7; --accent2: #81c784;
    --warn: #ffb74d; --border: #333;
    --canvas-bg: #0e0e12;
  }
  [data-theme="light"] {
    --bg: #f5f5f5; --surface: #ffffff; --surface2: #eee;
    --text: #1a1a1a; --dim: #666; --accent: #0277bd; --accent2: #2e7d32;
    --warn: #e65100; --border: #ccc;
    --canvas-bg: #f0f0f5;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
         background: var(--bg); color: var(--text); }
  a { color: var(--accent); text-decoration: none; }
  a:hover { text-decoration: underline; }

  /* Top nav */
  nav { position: sticky; top: 0; z-index: 50; background: var(--bg);
        border-bottom: none; padding: 8px 20px;
        display: flex; gap: 20px; align-items: center; margin: 0;
        height: 36px; }
  nav .brand { font-size: 16px; font-weight: bold; color: var(--accent); }
  nav a { font-size: 12px; color: var(--dim); }
  nav a:hover { color: var(--accent); }

  /* Tab panels */
  .tab-panel { display: none; }
  .tab-panel.active { display: block; }
  /* Sections within a tab panel scroll together */
  .section { max-width: 1100px; margin: 0 auto; padding: 20px 20px; }
  .section h2 { font-size: 18px; color: var(--accent2); margin-bottom: 8px; }
  .section .subtitle { font-size: 12px; color: var(--dim); line-height: 1.6;
                        margin-bottom: 16px; max-width: 700px; }
  .section .formula { font-family: 'SF Mono', monospace; font-size: 13px;
                       background: var(--surface2); padding: 10px 16px;
                       border-radius: 6px; color: var(--accent2);
                       margin: 12px 0; display: inline-block; }
  .section .explain { background: var(--surface); border-radius: 6px;
                       padding: 14px 18px; margin: 16px 0; line-height: 1.7;
                       font-size: 12px; color: var(--text); border-left: 3px solid var(--accent2); }
  .section .explain b { color: var(--accent2); }

  /* Tab bar — sticky, flush directly under the nav */
  .math-tabs { display: flex; border-bottom: 1px solid var(--border);
               background: var(--bg); padding: 0 20px; gap: 0; overflow-x: auto;
               position: sticky; top: 36px; z-index: 40; margin: 0; }
  .math-tab { padding: 8px 18px; font-size: 12px; color: var(--dim);
              cursor: pointer; border-bottom: 2px solid transparent;
              white-space: nowrap; }
  .math-tab:hover { color: var(--accent); }
  .math-tab.active { color: var(--accent2); border-bottom-color: var(--accent2); }

  /* Canvas area */
  .canvas-wrap { position: relative; background: var(--surface);
                  border: 1px solid var(--border); border-radius: 8px;
                  overflow: hidden; }
  canvas { display: block; cursor: crosshair; }

  /* Controls */
  .controls { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0;
              align-items: center; }
  .controls button { background: var(--surface); color: var(--accent);
                      border: 1px solid var(--accent); border-radius: 4px;
                      padding: 6px 14px; font-family: inherit; font-size: 11px;
                      cursor: pointer; }
  .controls button:hover { background: var(--accent); color: #000; }
  .controls button.active { background: var(--accent); color: #000; }
  .controls button.danger { border-color: var(--warn); color: var(--warn); }
  .controls button.danger:hover { background: var(--warn); color: #000; }
  .controls label { font-size: 11px; color: var(--dim); display: flex;
                    align-items: center; gap: 6px; }
  .controls input[type=range] { width: 100px; }
  .controls .value { font-size: 11px; color: var(--accent); min-width: 30px; }

  /* Side panel */
  .side-panel { background: var(--surface2); border: 1px solid var(--border);
                 border-radius: 6px; padding: 12px 16px; margin-top: 12px;
                 max-height: 300px; overflow-y: auto; }
  .side-panel h3 { font-size: 12px; color: var(--accent); margin-bottom: 8px; }
  .side-panel .row { font-size: 11px; padding: 3px 0; border-bottom: 1px solid #222;
                      display: flex; justify-content: space-between; }
  .side-panel .row .name { color: var(--text); }
  .side-panel .row .score { color: var(--accent2); font-weight: bold; }

  /* Wiki links */
  .explain a, .subtitle a { color: var(--accent); text-decoration: none;
    border-bottom: 1px dashed rgba(79,195,247,0.4); }
  .explain a:hover, .subtitle a:hover { border-bottom-style: solid;
    border-bottom-color: var(--accent); }

  /* Separator */
  hr { border: none; border-top: 1px solid var(--border); margin: 40px 0; }

  /* Tooltip */
  #tooltip { position: absolute; pointer-events: none; background: var(--surface2);
              border: 1px solid var(--accent); border-radius: 6px;
              padding: 8px 12px; font-size: 11px; z-index: 100;
              display: none; max-width: 280px; line-height: 1.5; }
  #tooltip.show { display: block; }

  /* Tour overlay */
  #tour-overlay { position: fixed; top:0; left:0; width:100%; height:100%;
    background: rgba(0,0,0,0.6); z-index: 200; display: none; }
  #tour-overlay.active { display: block; }
  #tour-box { position: fixed; z-index: 201; background: var(--surface2);
    border: 2px solid var(--accent); border-radius: 10px; padding: 16px 20px;
    max-width: 340px; font-size: 13px; line-height: 1.6; color: var(--text);
    box-shadow: 0 8px 32px rgba(0,0,0,0.5); }
  #tour-box .tour-title { font-size: 14px; font-weight: bold; color: var(--accent);
    margin-bottom: 6px; }
  #tour-box .tour-step { font-size: 10px; color: var(--dim); margin-bottom: 8px; }
  #tour-box .tour-btns { display: flex; gap: 8px; margin-top: 12px; }
  #tour-box .tour-btns button { padding: 5px 14px; border-radius: 4px; border: 1px solid var(--border);
    background: var(--surface); color: var(--text); font-size: 11px; cursor: pointer; }
  #tour-box .tour-btns button.primary { background: var(--accent); color: #000; border: none; font-weight: bold; }
  #tour-highlight { position: fixed; z-index: 199; border: 2px solid var(--accent);
    border-radius: 8px; box-shadow: 0 0 0 9999px rgba(0,0,0,0.55);
    pointer-events: none; transition: all 0.4s ease; display: none; }

  /* Loading overlay */
  #loading-overlay { position: fixed; top:0; left:0; width:100%; height:100%;
    background: var(--bg); z-index: 300; display: flex; flex-direction: column;
    align-items: center; justify-content: center; transition: opacity 0.5s; }
  #loading-overlay.done { opacity: 0; pointer-events: none; }
  #loading-overlay .spinner { width: 32px; height: 32px; border: 3px solid var(--border);
    border-top-color: var(--accent); border-radius: 50%; animation: spin 0.8s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }

  /* Mobile responsiveness */
  @media (max-width: 768px) {
    nav { flex-wrap: wrap; gap: 8px; padding: 6px 12px; }
    .brand { font-size: 14px; }
    .math-tabs { gap: 0; }
    .math-tab { padding: 6px 8px; font-size: 10px; }
    .section { padding: 12px 10px; }
    .controls { flex-wrap: wrap; gap: 4px; }
    .controls button, .controls select, .controls input { font-size: 10px; padding: 4px 6px; }
    .explain { padding: 10px 12px; font-size: 11px; }
    .formula { font-size: 11px; padding: 10px; }
    #compare-panel { grid-template-columns: 1fr !important; }
    #vec-ranking { display: none; }
  }
</style>
</head>
<body>

<div id="loading-overlay">
  <div class="spinner"></div>
  <div style="margin-top:14px;font-size:12px;color:var(--dim)">Building concept network...</div>
</div>

<nav>
  <span class="brand">PEP Math Playground</span>
  <span style="font-size:10px;color:var(--dim);margin-left:8px">PEP — Predictive Encoding &amp; Preparation</span>
  <button onclick="startTour()" style="margin-left:auto;padding:4px 12px;border-radius:4px;
    border:1px solid var(--accent);background:transparent;color:var(--accent);
    font-size:11px;cursor:pointer;font-family:inherit">Take a Tour</button>
  <button onclick="downloadPage()" style="padding:4px 12px;border-radius:4px;
    border:1px solid var(--accent2);background:transparent;color:var(--accent2);
    font-size:11px;cursor:pointer;font-family:inherit;margin-left:6px">Download HTML</button>
  <button onclick="toggleTheme()" id="theme-btn" style="padding:4px 12px;border-radius:4px;
    border:1px solid var(--border);background:transparent;color:var(--dim);
    font-size:11px;cursor:pointer;font-family:inherit;margin-left:6px">Light</button>
  <a href="/pep" style="font-size:11px;color:var(--accent);margin-left:10px;text-decoration:none;border:1px solid var(--accent);border-radius:4px;padding:4px 12px">PEP Engine &rarr;</a>
</nav>
<div class="math-tabs" id="math-tabs">
  <div class="math-tab active" data-section="network-tab">The Network</div>
  <div class="math-tab" data-section="vectors-tab">Vectors &amp; Distance</div>
  <div class="math-tab" data-section="prediction-tab">Prediction &amp; Probability</div>
  <div class="math-tab" data-section="emotion-tab">Emopics</div>
  <div class="math-tab" data-section="flow-tab">Flow &amp; Optimization</div>
  <div class="math-tab" data-section="applications">Applications</div>
</div>

<!-- ─── Section 1: Graph Builder ──────────────────────────────────── -->
<div class="tab-panel active" id="network-tab">
<div class="section" id="graph-builder">
  <h2>Graph Builder</h2>
  <p class="subtitle">
    Build a network of concepts. <b>Click the canvas</b> to add a node.
    <b>Drag from one node to another</b> to create a weighted edge.
    <b>Click an edge</b> to adjust its weight. This is <a href="https://en.wikipedia.org/wiki/Graph_theory" target="_blank"><b>graph theory</b></a> —
    the mathematical study of relationships between things.
  </p>
  <div class="controls">
    <button onclick="addNodePrompt()" id="btn-add">+ Add node</button>
    <button onclick="clearGraph()" class="danger">Clear all</button>
    <button onclick="loadPreset()" id="btn-preset">Load example</button>
    <button onclick="saveGraph()">Save</button>
    <button onclick="loadGraph()">Load</button>
    <button onclick="startGrowing()" id="btn-grow" style="background:var(--accent2);color:#000;border:none">Start growing</button>
    <button onclick="stopGrowing()" id="btn-stop-grow" disabled style="border-color:var(--warn);color:var(--warn)">Stop</button>
    <select id="emopic-select" onchange="emopicGraph(this.value)"
      style="background:var(--surface);color:var(--text);border:1px solid var(--accent);
      border-radius:4px;padding:4px 10px;font-family:inherit;font-size:11px;cursor:pointer">
      <option value="">emopics...</option>
      <option value="fear">Fear</option>
      <option value="joy">Joy</option>
      <option value="food">Food</option>
      <option value="music">Music</option>
      <option value="war">War</option>
      <option value="love">Love</option>
      <option value="nature">Nature</option>
      <option value="tech">Technology</option>
      <option value="body">Body</option>
      <option value="science">Science</option>
      <option value="time">Time</option>
      <option value="place">Place</option>
      <option value="language">Language</option>
      <option value="abstract">Abstract</option>
    </select>
    <input type="text" id="node-search" placeholder="search nodes..."
      style="background:var(--surface);color:var(--text);border:1px solid var(--border);
      border-radius:4px;padding:4px 8px;font-family:inherit;font-size:11px;width:120px;margin-left:auto"
      oninput="searchNode(this.value)">
    <span style="font-size:10px;color:var(--dim)" id="graph-stats">
      0 nodes, 0 edges
    </span>
  </div>
  <div style="display:flex;gap:10px">
    <div class="canvas-wrap" style="position:relative;flex:1">
      <canvas id="graph-canvas" width="960" height="640"></canvas>
      <div style="position:absolute;bottom:10px;right:10px;display:flex;flex-direction:column;gap:4px;z-index:10">
        <button onclick="zoomIn()" style="width:28px;height:28px;border-radius:4px;border:1px solid var(--border);
          background:var(--surface);color:var(--text);font-size:16px;cursor:pointer;padding:0;line-height:28px">+</button>
        <button onclick="zoomOut()" style="width:28px;height:28px;border-radius:4px;border:1px solid var(--border);
          background:var(--surface);color:var(--text);font-size:16px;cursor:pointer;padding:0;line-height:28px">&minus;</button>
        <button onclick="zoomFit()" style="width:28px;height:28px;border-radius:4px;border:1px solid var(--border);
          background:var(--surface);color:var(--dim);font-size:9px;cursor:pointer;padding:0;line-height:28px">fit</button>
        <button onclick="screenshotGraph()" title="Save as image" style="width:28px;height:28px;border-radius:4px;border:1px solid var(--border);
          background:var(--surface);color:var(--dim);font-size:12px;cursor:pointer;padding:0;line-height:28px">&#128247;</button>
        <button onclick="toggleFullscreen()" id="btn-fullscreen" title="Fullscreen" style="width:28px;height:28px;border-radius:4px;border:1px solid var(--border);
          background:var(--surface);color:var(--dim);font-size:12px;cursor:pointer;padding:0;line-height:28px">&#9974;</button>
      </div>
      <div id="tooltip"></div>
    </div>
    <div id="grow-panel" style="width:220px;background:var(--surface);border:1px solid var(--border);
         border-radius:6px;padding:10px;display:none;overflow-y:auto;max-height:640px">
      <div style="font-size:11px;color:var(--accent2);font-weight:bold;margin-bottom:6px">
        Growing <span id="grow-timer" style="color:var(--dim);font-weight:normal">0:00</span>
      </div>
      <div style="font-size:10px;color:var(--dim);margin-bottom:8px">
        <span id="grow-count">0</span> new concepts
      </div>
      <div id="grow-list" style="font-size:10px;line-height:1.6"></div>
    </div>
  </div>

  <!-- Side-by-side comparison panel (hidden until two nodes are shift-clicked) -->
  <div id="compare-panel" style="display:none;margin:10px 0;padding:14px 18px;background:var(--surface);
       border:1px solid var(--accent);border-radius:8px">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
      <span style="font-size:12px;color:var(--accent);font-weight:bold">Node Comparison</span>
      <button onclick="clearComparison()" style="padding:2px 10px;border-radius:4px;border:1px solid var(--border);
        background:var(--surface);color:var(--dim);font-size:10px;cursor:pointer">Clear</button>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;font-size:11px" id="compare-content"></div>
    <div style="font-size:10px;color:var(--dim);margin-top:8px">
      <b>Shift+click</b> any two nodes to compare them
    </div>
  </div>

  <div class="explain">
    <b>What you are looking at:</b> This is a <a href="https://en.wikipedia.org/wiki/Graph_(discrete_mathematics)#Weighted_graph" target="_blank"><b>weighted graph</b></a> — one of the most
    important structures in mathematics. Each circle (node) represents a concept or word.
    Each line (edge) represents a relationship between two concepts, with a <b>weight</b>
    that measures how strong that relationship is. Thicker, brighter lines mean stronger
    connections.
  </div>
  <div class="explain">
    <b>Why this matters for PEP:</b> PEP treats all information — memories, ideas, words,
    facts — as nodes in a weighted graph. When you ask PEP a question, it does not search
    a list. It <b>activates a region</b> of this graph and follows the strongest connections
    outward. The shape of the graph determines what gets retrieved. That is why structure
    matters more than size: a well-connected graph with good weights beats a giant pile of
    unrelated data.
  </div>
  <div class="explain">
    <b>Try this:</b> Click a node to activate it (you will see it glow and the activation
    spreads). Hold Alt/Cmd and drag from one node to another to create a new connection.
    Click an edge to change its weight. <b>Shift+click two nodes</b> to compare them
    side by side — see their definitions, connections, power scores, and shared neighbors.
    Right-click a node to set it as the scoring query.
    Use the <b>Zoom</b> buttons or scroll to zoom in/out. <b>Fit all</b> shows the whole graph.
  </div>
</div>

<!-- ─── Section 2: Spreading Activation ───────────────────────────── -->
<div class="section" id="spreading">
  <h2><a href="https://en.wikipedia.org/wiki/Spreading_activation" target="_blank" style="color:inherit;text-decoration:none;border-bottom:1px dashed var(--dim)">Spreading Activation</a></h2>
  <p class="subtitle">
    Click any node to <b>activate</b> it. Watch the activation spread through the
    network — bright at the center, dimming as it travels across edges. This is how
    PEP retrieves memories: not by searching everything, but by <b>lighting up the
    switchboard</b> and seeing what glows.
  </p>
  <div class="formula" id="spread-formula">
    A<sub>neighbor</sub> = A<sub>source</sub> &times; decay<sup>hop</sup> &times; weight
  </div>
  <div class="controls">
    <label>decay <input type="range" id="decay-slider" min="0.1" max="1.0" step="0.05" value="0.5">
      <span class="value" id="decay-val">0.50</span></label>
    <label>hops <input type="range" id="hops-slider" min="1" max="5" step="1" value="2">
      <span class="value" id="hops-val">2</span></label>
    <button onclick="resetActivation()">Reset glow</button>
    <span style="margin-left:auto;font-size:10px;color:var(--dim)" id="spread-status"></span>
  </div>

  <div class="explain">
    <b>What is happening:</b> When you click a node, it "fires" with full activation (1.0).
    On the next beat, every node connected to it receives activation equal to
    <b>source activation &times; decay<sup>hop</sup> &times; edge weight</b>. On the beat after
    that, those newly-lit nodes spread to THEIR neighbors at an even lower level. The result
    is a wave of decreasing brightness rippling outward through the network.
  </div>
  <div class="explain">
    <b>Why this matters:</b> This is how PEP retrieves memories. Instead of searching
    everything equally (like a database query), PEP lights up the most relevant region and
    lets activation flow to nearby concepts. Nodes that are strongly connected to the query
    glow bright; distant or weakly connected nodes stay dark. When a cluster of nodes all
    light up together, that is a <b>constellation</b> — a coherent group of ideas that belong
    together in this context.
  </div>
  <div class="explain">
    <b>The math:</b> This is related to <a href="https://en.wikipedia.org/wiki/Diffusion_process" target="_blank"><b>diffusion on graphs</b></a>, <a href="https://en.wikipedia.org/wiki/Random_walk" target="_blank"><b>random walks</b></a>,
    and <b>eigenvector centrality</b> (the math behind Google's original PageRank algorithm).
    The decay parameter controls how far influence travels. Low decay = local retrieval. High
    decay = broad, associative recall. The sweet spot depends on the question.
  </div>
</div>

<!-- ─── Section 3: Relevance Scoring ──────────────────────────────── -->
<div class="section" id="scoring">
  <h2>Relevance Scoring</h2>
  <p class="subtitle">
    Select a node as the <b>query</b> (right-click it). Every other node gets scored by
    the formula below. Drag the <b>weight sliders</b> and watch the rankings update
    in real time. This is <b>optimization</b> — finding the best answers under
    changing priorities.
  </p>
  <div class="formula">
    R(x) = w<sub>1</sub>&middot;connection + w<sub>2</sub>&middot;brightness +
    w<sub>3</sub>&middot;proximity + &alpha;&middot;E(x) + &beta;&middot;P(x)
  </div>
  <div class="controls" id="weight-sliders">
    <label>connection <input type="range" min="0" max="1" step="0.05" value="0.4" data-w="connection">
      <span class="value">0.40</span></label>
    <label>brightness <input type="range" min="0" max="1" step="0.05" value="0.25" data-w="brightness">
      <span class="value">0.25</span></label>
    <label>proximity <input type="range" min="0" max="1" step="0.05" value="0.15" data-w="proximity">
      <span class="value">0.15</span></label>
    <label>&alpha; (effect) <input type="range" min="0" max="1" step="0.05" value="0.1" data-w="effect">
      <span class="value">0.10</span></label>
    <label>&beta; (power) <input type="range" min="0" max="1" step="0.05" value="0.1" data-w="power">
      <span class="value">0.10</span></label>
  </div>
  <div class="side-panel" id="ranking-panel">
    <h3>Rankings (select a query node by right-clicking)</h3>
    <div id="ranking-list"></div>
  </div>

  <div class="explain">
    <b>What is happening:</b> When you right-click a node to make it the "query," every
    other node gets a <b>relevance score</b> computed from the formula above. The ranking
    panel shows them sorted from most to least relevant. Drag the weight sliders and watch
    the rankings change in real time — the same graph produces different answers depending
    on what you prioritize.
  </div>
  <div class="explain">
    <b>Why this matters:</b> This is <a href="https://en.wikipedia.org/wiki/Optimization_problem" target="_blank"><b>optimization under constraints</b></a> — one of the
    deepest ideas in mathematics. There is no single "right" answer to "what is relevant."
    It depends on your weights: how much do you value direct connection vs. brightness vs.
    proximity vs. influence? Different settings give different truths. PEP uses this exact
    formula (with more components) to decide which memories to surface on every turn.
  </div>
</div>

<!-- ─── Section 4: Power & Effect ─────────────────────────────────── -->
<div class="section" id="power-effect">
  <h2>Power &amp; Effect</h2>
  <p class="subtitle">
    <b>Effect</b> is how much change a node causes in its neighborhood.
    <b>Power</b> is the capacity to produce that effect across the whole network.
    Math is not only about counting connections — it is about measuring
    <b>influence</b>.
  </p>
  <div class="formula">
    E(n) = &Sigma; w<sub>i</sub> &middot; &Delta;<sub>i</sub>
    &nbsp;&nbsp;&nbsp;
    P(n) = &Sigma; E(neighbor) &middot; w<sub>link</sub>
  </div>
  <div class="side-panel" id="power-panel">
    <h3>Nodes ranked by power</h3>
    <div id="power-list"></div>
  </div>

  <div class="explain">
    <b>What is happening:</b> <b>Effect E(n)</b> measures how much direct influence a node
    has — the sum of all its edge weights. A node connected to many things with strong weights
    has high effect. <b>Power P(n)</b> goes one step deeper: it measures how much influence
    a node has <em>through</em> its neighbors. A node connected to other high-effect nodes
    has high power, even if its own direct connections are modest.
  </div>
  <div class="explain">
    <b>Why this matters:</b> Math is not only about counting connections. It is about measuring
    <b>influence</b>. Some words — like "love," "power," "time," "truth" — are not just
    popular. They actively reshape how you think about everything connected to them. That is
    what power means in a network: the capacity to change the structure around you. PEP uses
    power and effect to decide which memories are not just relevant but <b>transformative</b>.
  </div>
</div>

<!-- ─── Section 5: Idea Lifecycle ─────────────────────────────────── -->
<div class="section" id="lifecycle">
  <h2>Idea Lifecycle</h2>
  <p class="subtitle">
    Ideas are not static. They <b>merge</b> into larger concepts, <b>split</b> into
    finer distinctions, <b>emerge</b> from patterns, and <b>fade</b> when no longer
    useful. Math can describe not just storage but <b>transformation</b>.
  </p>
  <div class="controls">
    <button onclick="mergeSelected()">Merge selected</button>
    <button onclick="splitSelected()">Split selected</button>
    <button onclick="createNovelNode()">Create (novelty)</button>
    <button onclick="forgetSelected()" class="danger">Forget selected</button>
    <span style="font-size:10px;color:var(--dim);margin-left:8px" id="lifecycle-status">
      shift+click to select multiple nodes
    </span>
  </div>

  <div class="explain">
    <b>What is happening:</b> Ideas do not stay frozen. <b>Merge</b> combines two concepts
    into a more abstract one (like combining "fear" and "danger" into "threat"). <b>Split</b>
    breaks a broad concept into finer distinctions (like splitting "animal" into "predator"
    and "prey"). <b>Create</b> detects where the graph has an "unfinished edge" and suggests
    a new concept that would complete the pattern — this is <b>novelty prediction</b>, the
    system reaching beyond what it currently knows. <b>Forget</b> lets nodes fade and die
    when they are no longer useful.
  </div>
  <div class="explain">
    <b>Why this matters:</b> A truly intelligent memory system does not just store and
    retrieve. It <b>transforms</b>. Ideas merge into higher abstractions. Vague concepts
    split into precise distinctions. New ideas emerge from the structure of existing ones.
    And forgetting — far from being failure — is an optimization: it removes clutter so the
    important connections become easier to find. Math can describe all four of these
    transformations as operations on a weighted graph.
  </div>
</div>

<!-- ─── Section: Novelty & Growth ──────────────────────────────── -->
<div class="section" id="novelty-growth">
  <h2>How Ideas Grow: Novelty Prediction</h2>
  <p class="subtitle">
    The most interesting part of PEP: the network can <b>predict concepts that
    do not exist yet</b> by detecting the unfinished edges of structure.
  </p>

  <div class="explain">
    <b>The core idea:</b> If many nodes in a graph point toward a region where no
    node exists, something is probably missing. Think of seeing most of a constellation
    and guessing the position of the missing star. The system does not need to know
    the answer in advance — the <b>shape of the gap</b> reveals what should fill it.
    This is novelty prediction: reaching beyond current knowledge by analyzing the
    structure of what is already known.
  </div>

  <div class="explain">
    <b>Try it now:</b> Click the <b style="color:var(--accent2)">Start growing</b>
    button above. The graph will begin to grow on its own — every few seconds, PEP
    analyzes the network, finds the area with the most "structural pressure" (nodes
    with strong connections that lead nowhere), and proposes a new concept to fill
    the gap. Watch the network expand and notice where new nodes appear: usually at
    the boundaries between clusters, where two domains are close but unconnected.
    That is where novel ideas live — not deep inside what you already know, but at
    the edges between different kinds of knowledge.
  </div>

  <div class="explain">
    <b>Why this matters:</b> A lot of what humans call "creativity" may actually be
    this: detecting the <b>unfinished edges</b> in your mental graph and filling them
    with something that completes the pattern. An analogy is a bridge between two
    otherwise-separated clusters. A breakthrough is a node that suddenly connects many
    unrelated regions. A good question is one that points at exactly where the graph
    has a gap. PEP tries to formalize this: creativity is not random. It is
    <b>structurally implied novelty</b>.
  </div>

  <div class="explain">
    <b>What novelty feels like:</b> When a new idea forms in your mind, it does not
    feel like computation. It feels like an <b>explosion</b> — the eureka moment, the
    3am insight, the thought that hits you in the shower. But what is actually happening
    is that your brain's network just completed a structural gap. Two clusters that were
    close but unconnected suddenly link up. Activation floods through paths that did not
    exist a moment ago. The rush of excitement you feel IS the signal that a high-pressure
    edge just resolved. The idea was structurally implied before you became conscious of it.
    Your brain computed it; the "aha" was just the moment it surfaced.
  </div>

  <div class="explain">
    <b>Geniuses describing their brains exploding:</b> History's greatest thinkers
    have described exactly this process — often without knowing the math behind it.<br><br>
    <b><a href="https://en.wikipedia.org/wiki/Nikola_Tesla" target="_blank">Nikola Tesla</a></b>
    described inventions arriving fully formed as visions — complete machines appearing
    in his mind before he ever built them. His network had so much structural pressure
    that the solutions were inevitable.<br><br>
    <b><a href="https://en.wikipedia.org/wiki/Albert_Einstein" target="_blank">Einstein</a></b>
    called it "combinatory play" — ideas from different domains crashing into each other
    to produce something neither domain contained alone. That is two clusters bridging.<br><br>
    <b><a href="https://en.wikipedia.org/wiki/Wolfgang_Amadeus_Mozart" target="_blank">Mozart</a></b>
    described entire compositions arriving "all at once," as if he could see the whole
    piece simultaneously. The network resolved so completely that the output felt instant.<br><br>
    <b><a href="https://en.wikipedia.org/wiki/Ada_Lovelace" target="_blank">Ada Lovelace</a></b>
    saw connections between mathematics and music that nobody else did. She was bridging
    clusters that her contemporaries kept separate — and that bridge became the foundation
    of computer science.<br><br>
    <b><a href="https://en.wikipedia.org/wiki/Srinivasa_Ramanujan" target="_blank">Ramanujan</a></b>
    said his theorems came to him in dreams. His subconscious was computing structural
    pressure while he slept, and the results surfaced as fully formed mathematical truths.<br><br>
    These are not mystical experiences. They are descriptions of a network with massive
    structural pressure suddenly resolving. The ideas were <b>structurally implied</b>
    before the person became conscious of them.
  </div>

  <div class="explain">
    <b>Free will and novelty:</b> If ideas emerge from structural pressure in a network,
    do you really <b>choose</b> your ideas? Or do they choose you?<br><br>
    The graph does not generate randomly — it follows the structure. But the structure
    itself was built by your experiences, your attention, your choices about what to learn
    and what to ignore. So novelty is not fully free (it is constrained by what you already
    know) and not fully determined (the exact resolution is unpredictable even to you).<br><br>
    This suggests something profound: <b>free will might be the ability to build the
    structure that produces the ideas you could not have predicted.</b> You do not control
    the eureka moment directly. But you control what you feed into the network — what you
    read, who you talk to, what problems you sit with, what clusters you build. The
    breakthrough is a consequence of the structure you chose to construct. In that sense,
    creativity is not something you do in the moment. It is something you prepared for
    across your entire life.
  </div>

  <div class="explain">
    <b>Why "brain exploding" is literally accurate:</b> When a new node connects two
    previously separate clusters, activation can now flow between them for the first time.
    If both clusters are large — say 200 nodes each — the number of newly accessible paths
    is not 200 + 200. It is closer to 200 &times; 200 = <b>40,000 new connections</b> that
    did not exist a moment ago. This is a <a href="https://en.wikipedia.org/wiki/Combinatorial_explosion"
    target="_blank">combinatorial explosion</a>. A single new idea does not just add one
    fact — it <b>reorganizes everything</b>. Memories that were dormant suddenly become
    relevant. Questions you could not even formulate before now have obvious answers.
    The "explosion" metaphor is not poetic. It is structurally accurate: one bridge
    between two large clusters activates thousands of paths that did not exist a moment ago.
    That is what insight feels like — and that is exactly what you see when you click
    "Start growing" and watch a new node light up the graph.
  </div>

  <div class="explain">
    <b>How the growth algorithm works:</b> For each node, PEP computes a "pressure score"
    — how much influence the node has relative to how many of its potential connections
    actually exist. High influence + few outgoing paths = high pressure = something is
    missing nearby. The new node is placed near the highest-pressure node and connected
    to it and its neighbors. Over time, this fills gaps, bridges clusters, and grows the
    network the way ideas grow in a mind: not randomly, but by completing patterns.
  </div>

  <div class="formula">
    pressure(n) = E(n) / max(1, degree(n)) &mdash; high effect + low degree = unfinished edge
  </div>

  <div class="explain">
    <b>The math of novelty goes deep.</b> The pressure formula above is a heuristic — a
    fast approximation. But novelty prediction draws on several real branches of mathematics,
    each capturing a different aspect of what it means for something to be "new."
  </div>

  <div class="explain">
    <b>1. <a href="https://en.wikipedia.org/wiki/Link_prediction" target="_blank">Link prediction</a>
    — which edges should exist but don't?</b><br><br>
    Given an incomplete graph, which connections are missing? This is a studied problem in
    graph theory. One classic method is the <b>Common Neighbors</b> score: if nodes A and B
    share many neighbors but are not connected, the missing edge between them is likely real.
    The more shared neighbors, the higher the score.
  </div>

  <div class="formula">
    score(A, B) = | neighbors(A) &cap; neighbors(B) |
  </div>

  <div class="explain">
    More sophisticated methods include the <b>Jaccard coefficient</b> (shared neighbors
    divided by total neighbors) and the <b><a href="https://en.wikipedia.org/wiki/Adamic%E2%80%93Adar_index"
    target="_blank">Adamic-Adar index</a></b> (which weights rare shared neighbors more heavily —
    if two nodes share a neighbor that has very few connections, that is a stronger signal
    than sharing a highly-connected hub). In PEP, novelty prediction is essentially link
    prediction: finding where the graph has structural gaps that imply missing concepts.
  </div>

  <div class="formula">
    Adamic-Adar(A, B) = &Sigma;<sub>z &isin; neighbors(A) &cap; neighbors(B)</sub> 1 / log(degree(z))
  </div>

  <div class="explain">
    <b>2. <a href="https://en.wikipedia.org/wiki/Betweenness_centrality" target="_blank">
    Betweenness centrality</a> and structural holes — where the bridges are.</b><br><br>
    Sociologist <a href="https://en.wikipedia.org/wiki/Ronald_Stuart_Burt" target="_blank">Ron Burt</a>
    showed that the most valuable position in a network is not the most connected node — it is the
    <b>bridge between otherwise disconnected groups</b>. He called these gaps "structural holes."
    The person (or idea) that bridges a structural hole gets access to non-redundant information
    from both sides. Mathematically, <b>betweenness centrality</b> counts how many shortest
    paths between all pairs of nodes pass through a given node. High betweenness = you are
    a bridge. In PEP, a novel concept that fills a structural hole would have the highest
    betweenness centrality of any newly added node.
  </div>

  <div class="formula">
    C<sub>B</sub>(v) = &Sigma;<sub>s &ne; v &ne; t</sub> &sigma;<sub>st</sub>(v) / &sigma;<sub>st</sub>
    &mdash; fraction of shortest paths through v
  </div>

  <div class="explain">
    <b>3. <a href="https://en.wikipedia.org/wiki/Kullback%E2%80%93Leibler_divergence"
    target="_blank">Bayesian surprise</a> — how much did this change your beliefs?</b><br><br>
    When new information arrives, your beliefs shift. The mathematical measure of how much
    they shifted is the <b>KL divergence</b> (Kullback-Leibler divergence) between your
    prior beliefs and your posterior beliefs after seeing the new data. High KL divergence
    means the new information fundamentally changed what you think is true. Low KL divergence
    means it was roughly what you expected. This is a rigorous definition of surprise: not
    just "I didn't see that coming" but "my entire probability distribution just changed shape."
    PEP uses this principle: when new input causes a large shift in which memories are
    considered relevant, that input has high novelty and should be stored at high brightness.
  </div>

  <div class="formula">
    D<sub>KL</sub>(posterior || prior) = &Sigma; posterior(x) &middot; log( posterior(x) / prior(x) )
  </div>

  <div class="explain">
    <b>4. Prediction error (residuals) — the gap between expected and actual.</b><br><br>
    The simplest and most powerful measure of novelty: <b>what did you predict, and how
    wrong were you?</b> In PEP, the Predictor module generates expectations about what
    kind of input is coming next. The Residual Scorer then measures the gap between that
    prediction and what actually arrived. A large residual means the input was surprising —
    it carried information the system did not already have. A small residual means it was
    predictable — compress it or skip it. This is the same principle behind
    <a href="https://en.wikipedia.org/wiki/Predictive_coding" target="_blank">predictive coding</a>
    in neuroscience: the brain constantly predicts its own inputs, and only the
    <b>prediction errors</b> get propagated upward for attention and storage.
  </div>

  <div class="formula">
    residual = | observed - predicted | &mdash; large residual = high novelty = store it
  </div>

  <div class="explain">
    <b>5. <a href="https://en.wikipedia.org/wiki/Kolmogorov_complexity" target="_blank">
    Kolmogorov complexity</a> — can you compress it using what you already know?</b><br><br>
    The deepest mathematical definition of novelty: something is genuinely new if it
    <b>cannot be compressed</b> using your existing patterns. If you can describe the new
    information as a combination of things you already know, it is not truly novel — it is
    a rearrangement. But if the shortest description of the new information is as long as the
    information itself, it is <b>incompressible</b> — fundamentally new, not reducible to
    prior knowledge. This is the theoretical limit on novelty: the boundary between what your
    current network can represent and what it cannot. In practice, PEP approximates this
    through tag overlap and semantic distance — if a new input cannot be described by
    existing tags and has no close neighbors in embedding space, it has high Kolmogorov-like
    novelty.
  </div>

  <div class="formula">
    K(x) = length of shortest program that produces x &mdash; incompressible = truly novel
  </div>

  <div class="explain">
    <b>Why all five matter together:</b> Each captures a different facet of novelty.
    Link prediction finds <em>where</em> something is missing. Betweenness centrality
    measures <em>how valuable</em> a bridge would be. Bayesian surprise measures <em>how
    much it changes your beliefs</em>. Prediction error measures <em>how unexpected</em>
    it was. Kolmogorov complexity measures <em>how fundamentally irreducible</em> it is.
    A truly novel idea scores high on all five: it fills a structural gap, bridges
    disconnected clusters, shifts beliefs, defies prediction, and cannot be compressed
    into what was already known. That is what makes it feel like an explosion.
  </div>
</div>

<!-- ─── Section: Learn More (Videos) ──────────────────────────────── -->
<div class="section" id="learn-more">
  <h2>Learn More</h2>
  <p class="subtitle">
    These videos explain the mathematical concepts behind PEP in more depth.
  </p>

  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px">
    <div style="background:var(--surface);border-radius:8px;padding:12px;border:1px solid var(--border)">
      <a href="https://www.youtube.com/watch?v=aircAruvnKk" target="_blank" style="display:block;position:relative;border-radius:6px;overflow:hidden"><img src="https://img.youtube.com/vi/aircAruvnKk/hqdefault.jpg" style="width:100%;display:block;border-radius:6px" loading="lazy"><div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:48px;height:48px;background:rgba(0,0,0,0.7);border-radius:50%;display:flex;align-items:center;justify-content:center"><div style="width:0;height:0;border-top:10px solid transparent;border-bottom:10px solid transparent;border-left:18px solid #fff;margin-left:4px"></div></div></a>
      <div style="font-size:10px;color:var(--dim);margin-top:6px;line-height:1.3">But what is a neural network?</div>
    </div>
    <div style="background:var(--surface);border-radius:8px;padding:12px;border:1px solid var(--border)">
      <a href="https://www.youtube.com/watch?v=W18FDEA1jRQ" target="_blank" style="display:block;position:relative;border-radius:6px;overflow:hidden"><img src="https://img.youtube.com/vi/W18FDEA1jRQ/hqdefault.jpg" style="width:100%;display:block;border-radius:6px" loading="lazy"><div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:48px;height:48px;background:rgba(0,0,0,0.7);border-radius:50%;display:flex;align-items:center;justify-content:center"><div style="width:0;height:0;border-top:10px solid transparent;border-bottom:10px solid transparent;border-left:18px solid #fff;margin-left:4px"></div></div></a>
      <div style="font-size:10px;color:var(--dim);margin-top:6px;line-height:1.3">The Seven Bridges of Königsberg</div>
    </div>
    <div style="background:var(--surface);border-radius:8px;padding:12px;border:1px solid var(--border)">
      <a href="https://www.youtube.com/watch?v=cWNEl4HE2OE" target="_blank" style="display:block;position:relative;border-radius:6px;overflow:hidden"><img src="https://img.youtube.com/vi/cWNEl4HE2OE/hqdefault.jpg" style="width:100%;display:block;border-radius:6px" loading="lazy"><div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:48px;height:48px;background:rgba(0,0,0,0.7);border-radius:50%;display:flex;align-items:center;justify-content:center"><div style="width:0;height:0;border-top:10px solid transparent;border-bottom:10px solid transparent;border-left:18px solid #fff;margin-left:4px"></div></div></a>
      <div style="font-size:10px;color:var(--dim);margin-top:6px;line-height:1.3">Graph Search Algorithms in 100 Seconds</div>
    </div>
    <div style="background:var(--surface);border-radius:8px;padding:12px;border:1px solid var(--border)">
      <a href="https://www.youtube.com/watch?v=hBpetDxIEMU" target="_blank" style="display:block;position:relative;border-radius:6px;overflow:hidden"><img src="https://img.youtube.com/vi/hBpetDxIEMU/hqdefault.jpg" style="width:100%;display:block;border-radius:6px" loading="lazy"><div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:48px;height:48px;background:rgba(0,0,0,0.7);border-radius:50%;display:flex;align-items:center;justify-content:center"><div style="width:0;height:0;border-top:10px solid transparent;border-bottom:10px solid transparent;border-left:18px solid #fff;margin-left:4px"></div></div></a>
      <div style="font-size:10px;color:var(--dim);margin-top:6px;line-height:1.3">The Stuff of Thought — Steven Pinker</div>
    </div>
  </div>
</div>

</div><!-- end network-tab -->

<!-- ═══ Tab 2: Vectors & Distance ═══════════════════════════════════ -->
<div class="tab-panel" id="vectors-tab">
<div class="section">
  <h2>Vectors &amp; Distance</h2>
  <p class="subtitle">
    How meaning lives in mathematical space. Every word, concept, and memory can be
    represented as a point in a high-dimensional space — and the <b>distance</b> between
    two points tells you how similar they are.
  </p>

  <div style="margin:12px 0 20px">
    <p style="font-size:11px;color:var(--dim);margin-bottom:10px">
      Each dot is a word positioned by two dimensions: <b>concrete ↔ abstract</b> (horizontal)
      and <b>negative ↔ positive</b> (vertical). <b>Click two words</b> to see the distance
      and cosine similarity between them.
    </p>
    <div style="display:flex;gap:10px">
      <div class="canvas-wrap" style="flex:1">
        <canvas id="vector-canvas" width="800" height="400" style="cursor:pointer;width:100%;display:block"></canvas>
      </div>
      <div id="vec-ranking" style="flex:0 0 260px;background:var(--surface);border:1px solid var(--border);
           border-radius:6px;padding:10px;overflow-y:auto;max-height:400px">
        <div style="font-size:11px;color:var(--accent);font-weight:bold;margin-bottom:6px">
          Most Connected Words
        </div>
        <div id="vec-rank-list" style="font-size:10px;line-height:1.8"></div>
      </div>
    </div>
    <div id="vector-info" style="margin-top:8px;font-size:12px;color:var(--dim);min-height:20px">
      click any two words to compare
    </div>
  </div>

  <div class="explain">
    <b>What is a <a href="https://en.wikipedia.org/wiki/Vector_(mathematics_and_physics)" target="_blank" style="color:var(--accent)">vector</a>?</b> A vector has both <b>magnitude</b> (how strong) and
    <b>direction</b> (which way). In everyday math, a vector might describe motion:
    "3 miles north." In PEP, a vector describes <b>meaning</b>: a concept is a point
    in a space where every dimension represents some feature of that concept. The word
    "dog" might score high on dimensions like "animal," "domestic," "loyal" and low on
    "abstract," "liquid," "mathematical." That pattern of scores IS the vector.
  </div>

  <div class="formula">
    distance(A, B) = 1 - cos(&theta;) = 1 - (A &middot; B) / (|A| &times; |B|)
  </div>

  <div class="explain">
    <b>Why distance matters:</b> If "dog" and "wolf" have similar vectors (they share
    many features), their distance is small. If "dog" and "calculus" have very different
    vectors, their distance is large. This lets us turn the vague human intuition of
    "these things are related" into a <b>precise, computable number</b>. That number
    is what PEP uses when it decides which memories are semantically closest to your query.
  </div>

  <div class="explain">
    <a href="https://en.wikipedia.org/wiki/Cosine_similarity" target="_blank"><b>Cosine similarity:</b></a> The standard way to measure closeness between two vectors
    is not Euclidean distance (straight-line) but <b>cosine similarity</b> — the angle
    between them. Two vectors pointing in the same direction have cosine similarity = 1
    (perfectly aligned). Two pointing in opposite directions have cosine = -1. Two at
    right angles have cosine = 0 (completely unrelated). This works better than straight
    distance because it ignores magnitude and focuses on <b>direction of meaning</b>.
  </div>

  <div class="explain">
    <b>The deep insight:</b> Meaning is not a label. It is a <b>position in a space</b>.
    When you learn a new word, you are placing a new point in your mental space. When
    your understanding shifts, that point <b>moves</b>. When two ideas are confused,
    their vectors are too close together. When an analogy works, it means two vectors
    from different domains point in the same direction. Math makes all of this precise.
  </div>

  <div class="explain">
    <b>Puns prove vectors are real:</b> A pun works because one word sits near
    <b>two different clusters</b> in meaning-space simultaneously. "I used to be a banker
    but I lost interest" works because "interest" has a vector near both {finance, money, bank}
    AND {curiosity, attention, boredom}. The humor comes from the brain being forced to
    activate two distant regions at once — the collision is the joke. This is not just
    wordplay. It is <b>evidence that meaning has spatial structure</b>. If words were just
    labels with no geometry, puns would not exist. The fact that they do means meaning
    occupies a space where some words genuinely sit at the intersection of unrelated
    neighborhoods. That is exactly what a vector model predicts.
  </div>

  <div class="explain">
    <b>In PEP:</b> Every memory has an embedding vector (currently 1024 dimensions).
    When you ask a question, PEP embeds your question into the same space and finds the
    memories whose vectors point in the closest direction. That is semantic retrieval —
    not matching keywords, but matching <b>meaning geometry</b>.
  </div>

  <div class="explain">
    <b>Thought as motion:</b> A conversation is not just a sequence of statements. It is
    a <a href="https://en.wikipedia.org/wiki/Trajectory" target="_blank"><b>trajectory through vector space</b></a>. Each turn moves the active meaning-point
    in some direction. Some directions are small refinements; others are large jumps to
    a new region. PEP tracks this trajectory through its State Modulator — the urgency,
    novelty, and exploration dimensions are themselves a vector that changes with every turn.
  </div>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px">
    <div style="background:var(--surface);border-radius:8px;padding:12px;border:1px solid var(--border)">
      <a href="https://www.youtube.com/watch?v=fNk_zzaMoSs" target="_blank" style="display:block;position:relative;border-radius:6px;overflow:hidden"><img src="https://img.youtube.com/vi/fNk_zzaMoSs/hqdefault.jpg" style="width:100%;display:block;border-radius:6px" loading="lazy"><div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:48px;height:48px;background:rgba(0,0,0,0.7);border-radius:50%;display:flex;align-items:center;justify-content:center"><div style="width:0;height:0;border-top:10px solid transparent;border-bottom:10px solid transparent;border-left:18px solid #fff;margin-left:4px"></div></div></a>
      <div style="font-size:10px;color:var(--dim);margin-top:6px;line-height:1.3">Vectors — Essence of Linear Algebra</div>
    </div>
    <div style="background:var(--surface);border-radius:8px;padding:12px;border:1px solid var(--border)">
      <a href="https://www.youtube.com/watch?v=LyGKycYT2v0" target="_blank" style="display:block;position:relative;border-radius:6px;overflow:hidden"><img src="https://img.youtube.com/vi/LyGKycYT2v0/hqdefault.jpg" style="width:100%;display:block;border-radius:6px" loading="lazy"><div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:48px;height:48px;background:rgba(0,0,0,0.7);border-radius:50%;display:flex;align-items:center;justify-content:center"><div style="width:0;height:0;border-top:10px solid transparent;border-bottom:10px solid transparent;border-left:18px solid #fff;margin-left:4px"></div></div></a>
      <div style="font-size:10px;color:var(--dim);margin-top:6px;line-height:1.3">Dot Products and Duality</div>
    </div>
    <div style="background:var(--surface);border-radius:8px;padding:12px;border:1px solid var(--border)">
      <a href="https://www.youtube.com/watch?v=kYB8IZa5AuE" target="_blank" style="display:block;position:relative;border-radius:6px;overflow:hidden"><img src="https://img.youtube.com/vi/kYB8IZa5AuE/hqdefault.jpg" style="width:100%;display:block;border-radius:6px" loading="lazy"><div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:48px;height:48px;background:rgba(0,0,0,0.7);border-radius:50%;display:flex;align-items:center;justify-content:center"><div style="width:0;height:0;border-top:10px solid transparent;border-bottom:10px solid transparent;border-left:18px solid #fff;margin-left:4px"></div></div></a>
      <div style="font-size:10px;color:var(--dim);margin-top:6px;line-height:1.3">Linear Transformations and Matrices</div>
    </div>
    <div style="background:var(--surface);border-radius:8px;padding:12px;border:1px solid var(--border)">
      <a href="https://www.youtube.com/watch?v=zjMuIxRvygQ" target="_blank" style="display:block;position:relative;border-radius:6px;overflow:hidden"><img src="https://img.youtube.com/vi/zjMuIxRvygQ/hqdefault.jpg" style="width:100%;display:block;border-radius:6px" loading="lazy"><div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:48px;height:48px;background:rgba(0,0,0,0.7);border-radius:50%;display:flex;align-items:center;justify-content:center"><div style="width:0;height:0;border-top:10px solid transparent;border-bottom:10px solid transparent;border-left:18px solid #fff;margin-left:4px"></div></div></a>
      <div style="font-size:10px;color:var(--dim);margin-top:6px;line-height:1.3">Quaternions and 3D Rotation</div>
    </div>
  </div>
</div>
</div><!-- end vectors-tab -->

<!-- ═══ Tab 3: Prediction & Probability ═════════════════════════════ -->
<div class="tab-panel" id="prediction-tab">
<div class="section">
  <h2>Prediction &amp; Probability</h2>
  <p class="subtitle">
    How PEP anticipates what will matter before it happens. Prediction is not
    guessing — it is <b>structured estimation</b> based on patterns in the network.
  </p>

  <div class="formula">
    P(A | B) = P(B | A) &times; P(A) / P(B)
  </div>

  <div class="explain">
    <a href="https://en.wikipedia.org/wiki/Bayes%27_theorem" target="_blank"><b>Bayes' theorem</b></a> says: the probability of A given B depends on
    how often B happens when A is true, how common A is in general, and
    how common B is in general. In PEP, this is how beliefs get updated: when new
    information arrives, the system adjusts which memories are likely relevant.
  </div>

  <!-- Interactive: Bayes Calculator — right after the explanation -->
  <div style="margin:12px 0 24px">
    <h3 style="font-size:14px;color:#f06292;margin-bottom:10px">Interactive: Bayes' Theorem Calculator</h3>
    <p style="font-size:11px;color:var(--dim);margin-bottom:12px">
      Drag the sliders to see how <b>P(A|B)</b> changes. This is how PEP updates its
      beliefs about which memories are relevant when new evidence arrives.
    </p>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px">
      <div>
        <div class="controls" style="flex-direction:column;align-items:stretch">
          <label style="margin-bottom:8px">P(A) — prior belief
            <input type="range" id="bayes-pa" min="0.01" max="0.99" step="0.01" value="0.3" style="width:100%">
            <span class="value" id="bayes-pa-val">0.30</span></label>
          <label style="margin-bottom:8px">P(B|A) — likelihood
            <input type="range" id="bayes-pba" min="0.01" max="0.99" step="0.01" value="0.8" style="width:100%">
            <span class="value" id="bayes-pba-val">0.80</span></label>
          <label style="margin-bottom:8px">P(B) — evidence
            <input type="range" id="bayes-pb" min="0.01" max="0.99" step="0.01" value="0.4" style="width:100%">
            <span class="value" id="bayes-pb-val">0.40</span></label>
        </div>
      </div>
      <div style="display:flex;flex-direction:column;justify-content:center;align-items:center">
        <div style="font-size:11px;color:var(--dim);margin-bottom:4px">P(A|B) = P(B|A) &times; P(A) / P(B)</div>
        <div id="bayes-result" style="font-size:48px;font-weight:bold;color:#f06292">0.60</div>

        <div style="width:250px;margin-top:12px">
          <div style="display:flex;justify-content:space-between;font-size:9px;color:var(--dim);margin-bottom:2px">
            <span>prior P(A)</span><span>posterior P(A|B)</span>
          </div>
          <div style="position:relative;height:20px;background:var(--bg);border-radius:10px;
               border:1px solid var(--border);overflow:hidden">
            <div id="bayes-prior-bar" style="position:absolute;left:0;top:0;height:100%;
                 background:rgba(79,195,247,0.4);transition:width 0.3s;border-radius:10px"></div>
            <div id="bayes-fill" style="position:absolute;left:0;top:0;height:100%;
                 background:linear-gradient(90deg,#4fc3f7,#f06292);transition:width 0.3s;
                 border-radius:10px;opacity:0.8"></div>
          </div>
          <div style="display:flex;justify-content:space-between;font-size:9px;margin-top:2px">
            <span style="color:#4fc3f7" id="bayes-prior-label">0.30</span>
            <span style="color:#f06292" id="bayes-post-label">0.60</span>
          </div>
        </div>

        <div id="bayes-verdict" style="font-size:11px;color:var(--dim);margin-top:10px;text-align:center;max-width:250px"></div>
      </div>
    </div>
  </div>

  <div class="formula">
    Information(event) = -log<sub>2</sub> P(event)
  </div>

  <div class="explain">
    <a href="https://en.wikipedia.org/wiki/Information_content" target="_blank"><b>Shannon's insight:</b></a> The amount of information in a message is the negative log
    of its probability. A coin flip (50/50) carries 1 bit. A certain event carries 0 bits.
    A rare event carries many bits. PEP uses this: unexpected things get stored,
    predictable things get compressed. <b>Intelligence is partly allocating attention
    proportional to surprise.</b>
  </div>

  <!-- Interactive: Surprise Meter — right after Shannon's explanation -->
  <div style="margin:12px 0 24px">
    <h3 style="font-size:14px;color:#f06292;margin-bottom:10px">Interactive: Surprise Meter</h3>
    <p style="font-size:11px;color:var(--dim);margin-bottom:10px">
      Type any English word and press Enter. You will see its <b>real definition</b> and how
      <b>predictable</b> it is. Common words like "the" or "I" appear constantly — your brain
      barely notices them. Rare words like "quixotic" are surprising — your brain pays attention
      and is more likely to remember them. <b>This is how PEP decides what to store:</b>
      predictable = compress, surprising = remember.
    </p>
    <div style="display:flex;gap:12px;align-items:flex-start;flex-wrap:wrap">
      <div style="min-width:220px">
        <input type="text" id="surprise-word" placeholder="type a word and press enter..."
          style="background:var(--surface);color:var(--text);border:1px solid var(--border);
          border-radius:4px;padding:8px 12px;font-family:inherit;font-size:13px;width:100%;box-sizing:border-box">
        <div id="surprise-status" style="font-size:9px;color:var(--dim);margin-top:4px;min-height:14px"></div>
      </div>
      <div style="flex:1;min-width:250px">
        <div style="display:flex;justify-content:space-between;font-size:9px;color:var(--dim);margin-bottom:2px">
          <span>predictable (brain skips)</span><span>surprising (brain stores)</span>
        </div>
        <div style="position:relative;height:24px;background:var(--bg);border-radius:12px;
             border:1px solid var(--border);overflow:hidden">
          <div id="surprise-bar" style="position:absolute;left:0;top:0;height:100%;width:0%;
               background:linear-gradient(90deg,#81c784,#ffd54f,#f06292);transition:width 0.4s;
               border-radius:12px"></div>
        </div>
        <div style="display:flex;justify-content:space-between;margin-top:3px">
          <span id="surprise-label" style="font-size:11px;color:var(--dim)"></span>
          <span id="surprise-rank" style="font-size:10px;color:var(--dim)"></span>
        </div>
      </div>
    </div>
    <div id="surprise-def" style="margin-top:10px;padding:10px 14px;background:var(--surface);
         border:1px solid var(--border);border-radius:6px;font-size:12px;color:var(--text);
         display:none;line-height:1.6">
    </div>
    <div id="surprise-explain" style="font-size:10px;color:var(--dim);margin-top:8px;min-height:16px"></div>
  </div>

  <div class="explain">
    <a href="https://en.wikipedia.org/wiki/Information_theory" target="_blank"><b>Novelty as surprise:</b></a> PEP's Residual Scorer measures how <b>unexpected</b>
    your input was. High surprise = high novelty = worth storing. Low surprise = filler = skip.
  </div>

  <div class="explain">
    <b>Predicting the missing node:</b> PEP detects where the network has "unfinished edges"
    and estimates what concept <em>should</em> exist there. This is like seeing most of a
    constellation and guessing the missing star. A lot of what humans call "creativity" may
    be exactly this: detecting the shape of what is missing from the shape of what is present.
  </div>

  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px">
    <div style="background:var(--surface);border-radius:8px;padding:12px;border:1px solid var(--border)">
      <a href="https://www.youtube.com/watch?v=HZGCoVF3YvM" target="_blank" style="display:block;position:relative;border-radius:6px;overflow:hidden"><img src="https://img.youtube.com/vi/HZGCoVF3YvM/hqdefault.jpg" style="width:100%;display:block;border-radius:6px" loading="lazy"><div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:48px;height:48px;background:rgba(0,0,0,0.7);border-radius:50%;display:flex;align-items:center;justify-content:center"><div style="width:0;height:0;border-top:10px solid transparent;border-bottom:10px solid transparent;border-left:18px solid #fff;margin-left:4px"></div></div></a>
      <div style="font-size:10px;color:var(--dim);margin-top:6px;line-height:1.3">Bayes Theorem — The Geometry of Changing Beliefs</div>
    </div>
    <div style="background:var(--surface);border-radius:8px;padding:12px;border:1px solid var(--border)">
      <a href="https://www.youtube.com/watch?v=bPFNxD3Yg6U" target="_blank" style="display:block;position:relative;border-radius:6px;overflow:hidden"><img src="https://img.youtube.com/vi/bPFNxD3Yg6U/hqdefault.jpg" style="width:100%;display:block;border-radius:6px" loading="lazy"><div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:48px;height:48px;background:rgba(0,0,0,0.7);border-radius:50%;display:flex;align-items:center;justify-content:center"><div style="width:0;height:0;border-top:10px solid transparent;border-bottom:10px solid transparent;border-left:18px solid #fff;margin-left:4px"></div></div></a>
      <div style="font-size:10px;color:var(--dim);margin-top:6px;line-height:1.3">The Shape of Data: Distributions</div>
    </div>
    <div style="background:var(--surface);border-radius:8px;padding:12px;border:1px solid var(--border)">
      <a href="https://www.youtube.com/watch?v=iSNsgj1OCLA" target="_blank" style="display:block;position:relative;border-radius:6px;overflow:hidden"><img src="https://img.youtube.com/vi/iSNsgj1OCLA/hqdefault.jpg" style="width:100%;display:block;border-radius:6px" loading="lazy"><div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:48px;height:48px;background:rgba(0,0,0,0.7);border-radius:50%;display:flex;align-items:center;justify-content:center"><div style="width:0;height:0;border-top:10px solid transparent;border-bottom:10px solid transparent;border-left:18px solid #fff;margin-left:4px"></div></div></a>
      <div style="font-size:10px;color:var(--dim);margin-top:6px;line-height:1.3">The Riddle That Seems Impossible</div>
    </div>
    <div style="background:var(--surface);border-radius:8px;padding:12px;border:1px solid var(--border)">
      <a href="https://www.youtube.com/watch?v=sbbYntt5CJk" target="_blank" style="display:block;position:relative;border-radius:6px;overflow:hidden"><img src="https://img.youtube.com/vi/sbbYntt5CJk/hqdefault.jpg" style="width:100%;display:block;border-radius:6px" loading="lazy"><div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:48px;height:48px;background:rgba(0,0,0,0.7);border-radius:50%;display:flex;align-items:center;justify-content:center"><div style="width:0;height:0;border-top:10px solid transparent;border-bottom:10px solid transparent;border-left:18px solid #fff;margin-left:4px"></div></div></a>
      <div style="font-size:10px;color:var(--dim);margin-top:6px;line-height:1.3">Statistics and Probability Full Course</div>
    </div>
  </div>
</div>
</div><!-- end prediction-tab -->

<!-- ═══ Tab: Emotion & Memory ════════════════════════════════════════ -->
<div class="tab-panel" id="emotion-tab">
<div class="section">
  <h2>Emopics — Emotion + Topic as a Weighting Layer</h2>
  <p class="subtitle">
    Emotion is not noise on top of thinking. And topic is not just "subject matter."
    Together — <b>emopics</b> — they form the contextual state that determines which
    part of your memory network is lit up at any given moment.
  </p>

  <div class="explain">
    <b>Why emotion matters for information:</b> When you experience something with strong
    emotion — fear, love, surprise, excitement — your brain does not store it the same way
    it stores a random Tuesday afternoon. Emotional intensity acts like a <b>brightness
    multiplier</b> on the memory. The stronger the emotion, the brighter the node glows,
    the more connections it forms, and the easier it is to retrieve later. This is not a bug
    in human cognition. It is a feature: the system prioritizes what <em>mattered</em> over
    what merely <em>happened</em>.
  </div>

  <div class="explain">
    <b>The 9/11 example:</b> Most people who were alive on September 11, 2001 can tell you
    exactly where they were, what they were doing, who told them, and how they felt when they
    heard the news. But almost nobody can tell you what they did on September 10. The events
    of the 10th were perfectly normal — and therefore stored at low brightness. The events of
    the 11th were emotionally overwhelming — and therefore burned into memory at maximum
    intensity. The information itself is similar (a day of events), but the <b>emotional weight</b>
    made one permanently retrievable and the other essentially forgotten. That is emotion
    functioning as a storage and retrieval operator, not as a distraction from thought.<br><br>
    But here is the deeper twist: research on <a href="https://en.wikipedia.org/wiki/Flashbulb_memory"
    target="_blank"><b>flashbulb memories</b></a> shows that many of those vivid 9/11 memories
    are <b>wrong</b>. People confidently remember details that did not happen — they misremember
    who told them, where they were, what they said. The emotion did not just store the memory
    at high brightness — it <b>enhanced and edited</b> the memory to make it more coherent,
    more dramatic, more emotionally consistent. The brain rewrites the record to match the
    feeling. This means emotion is not just a weighting function for storage. It is also an
    <b>editing function</b> that reshapes what was stored to be more memorable, even at the
    cost of accuracy. The memory becomes more retrievable precisely because it was made more
    emotional — even if parts of it are now fiction.
  </div>

  <div class="formula">
    memory_strength = base_encoding &times; emotional_intensity &times; repetition
  </div>

  <div class="explain">
    <b>Enjoying a good book:</b> The same principle explains why you remember a novel you
    loved far better than a textbook you endured. Emotional engagement — curiosity, suspense,
    attachment to characters, surprise at a plot twist — continuously adjusts the weights on
    what you are reading. Each emotionally charged scene creates a brighter node with stronger
    connections. A boring textbook, no matter how factual, encodes at low brightness because
    the emotional signal is flat. The information is technically "received" but it is stored
    so dimly that retrieval is slow, fragile, and unreliable. <b>Engagement is not separate
    from learning. Engagement IS the weighting function that determines what gets learned.</b>
  </div>

  <div class="explain">
    <b>How this works in the network:</b> Imagine the concept graph on the Network tab.
    When you click a node, activation spreads outward. Now imagine that some nodes glow
    <b>much brighter</b> than others — not because they have more connections, but because
    they were encoded with strong emotion. Those bright nodes act like beacons: when a
    nearby cue arrives, the emotional nodes activate faster and more strongly than their
    neutral neighbors. That is exactly what happens in human memory: an emotional memory
    does not just exist in the network — it <b>distorts the activation field around it</b>,
    pulling retrieval toward itself.
  </div>

  <div class="explain">
    <b>Emotion as fast retrieval:</b> When new information arrives, emotion helps you
    pull the right memories <em>fast</em>. If you feel fear, threat-related memories
    activate immediately — you do not have to search through everything you know. If you
    feel curiosity, exploratory memories light up. If you feel nostalgia, past experiences
    surface. Emotion is not just about storage. It is a <b>retrieval accelerator</b>: it
    narrows the search space to the most relevant region of your memory based on your
    current state. Without this, retrieval would be flat — every memory equally accessible,
    which sounds democratic but is actually useless under time pressure.
  </div>

  <div class="explain">
    <b>In PEP:</b> PEP models this with the <b>State Modulator</b> — a vector of six
    values (urgency, uncertainty, novelty, conflict, exploration, stability) that changes
    on every turn. These are not emotions in the human chemical sense, but they serve the
    same mathematical function: they <b>change the weights</b> on every retrieval, every
    storage decision, and every scoring formula. High urgency narrows the search. High
    exploration widens it. High novelty lowers the storage threshold so surprising things
    get kept. This is the functional equivalent of emotion applied to an information system.
  </div>

  <div class="explain">
    <b>Why this means emotion is not opposed to intelligence:</b> People often treat
    emotion and reason as opposites. But from a mathematical perspective, emotion is one
    of the mechanisms that makes <em>rapid, context-sensitive intelligence possible</em>.
    A system that treats all information equally — no weighting, no urgency, no salience — is
    not more rational. It is just slower. Emotion is what lets a system instantly prioritize
    the right information in the right situation. Removing it does not make you smarter.
    It makes you an archive with no sense of what matters.
  </div>

  <div class="explain">
    <b>It is not just emotion — it is also topic. Call it emopics.</b><br><br>
    Here is the key insight: <b>topics activate emotions</b>. When someone mentions food,
    that topic primes a region of your network — but it also triggers endogenous compounds
    in your brain: <a href="https://en.wikipedia.org/wiki/Dopamine" target="_blank">dopamine</a> (anticipation), maybe <a href="https://en.wikipedia.org/wiki/Cortisol" target="_blank">cortisol</a> (if you are hungry), <a href="https://en.wikipedia.org/wiki/Serotonin" target="_blank">serotonin</a>
    (comfort food memories). When someone mentions war, the topic activates a completely
    different chemical cocktail: adrenaline, cortisol, heightened alertness. <b>The emotions
    ARE the <a href="https://en.wikipedia.org/wiki/Endogeny_(biology)" target="_blank">endogenous</a> compounds</b> — dopamine, serotonin, cortisol, <a href="https://en.wikipedia.org/wiki/Oxytocin" target="_blank">oxytocin</a>, <a href="https://en.wikipedia.org/wiki/Endorphins" target="_blank">endorphins</a>,
    <a href="https://en.wikipedia.org/wiki/Norepinephrine" target="_blank">norepinephrine</a> — and topics are what trigger them.<br><br>
    This is why we call it <b>emopics (emotion + topic)</b>: the topic provides the
    <b>region</b> of the network that lights up, and the emotion — the actual chemical
    response — provides the <b>intensity</b> of the activation. Fear while discussing war
    activates different nodes than fear while discussing a medical diagnosis, even though
    the chemical signature is similar. The topic selects which memories are candidates;
    the emotion determines how strongly they activate and how deeply they get stored.<br><br>
    It is not just broad topics either — <b>individual words trigger emotions</b>. The word
    "murder" activates a different chemical response than the word "garden," even outside
    of any larger topic. The word "mother" fires oxytocin pathways. The word "deadline"
    spikes cortisol. Words are not neutral labels — each one carries an emotional charge
    that primes your brain chemistry before you even finish reading the sentence. This is
    why poetry works, why insults hurt, and why a single word in a text message can change
    your entire mood. The word IS a micro-topic that triggers a micro-emotion.<br><br>
    This pairing is not optional. A topic without emotion is flat information — you process
    it but it does not stick. An emotion without a topic is free-floating anxiety or
    excitement with nothing to attach to. <b>Together they create a precise spotlight</b>
    on exactly the right memories at exactly the right intensity.
  </div>

  <div class="explain">
    <b>The deeper principle:</b> The more strongly a piece of information triggers
    endogenous compounds — the more it alters your chemical state — the more heavily it
    gets weighted in storage and retrieval. This is not a flaw in human cognition. It is
    the system working correctly: things that change your body chemistry are usually things
    that matter for survival, action, or identity. PEP formalizes this: memory brightness,
    state modulation, trajectory scoring, and per-turn decay are all mechanisms that make
    information behave the way it behaves in biological systems with real neurochemistry —
    even though PEP itself does not have chemistry. It uses both the emotional state
    (urgency, novelty, conflict) AND the topical state (what tags and concepts are active)
    to weight every retrieval.
  </div>

  <div class="formula">
    retrieval_score = relevance &times; emopic_match &times; brightness &times; recency
  </div>

  <div style="margin:20px 0 24px">
    <h3 style="font-size:14px;color:var(--warn);margin-bottom:10px">Interactive: Emopic Spotlight</h3>
    <p style="font-size:11px;color:var(--dim);margin-bottom:10px">
      Click an emopic below and watch which region of a small concept network lights up.
      The <b>topic</b> selects the region. The <b>emotion</b> (the endogenous chemical response)
      determines how brightly it glows. Same network, different spotlight.
    </p>
    <div class="controls" style="margin-bottom:10px">
      <button onclick="emopicActivate('fear')" style="background:#e53935;color:#fff;border:none">Fear</button>
      <button onclick="emopicActivate('joy')" style="background:#43a047;color:#fff;border:none">Joy</button>
      <button onclick="emopicActivate('food')" style="background:#ff8f00;color:#fff;border:none">Food</button>
      <button onclick="emopicActivate('music')" style="background:#8e24aa;color:#fff;border:none">Music</button>
      <button onclick="emopicActivate('war')" style="background:#455a64;color:#fff;border:none">War</button>
      <button onclick="emopicActivate('love')" style="background:#d81b60;color:#fff;border:none">Love</button>
      <button onclick="emopicActivate('science')" style="background:#00897b;color:#fff;border:none">Science</button>
      <button onclick="emopicReset()">Reset</button>
    </div>
    <div class="canvas-wrap">
      <canvas id="emopic-canvas" width="800" height="320" style="width:100%;display:block"></canvas>
    </div>
  </div>

  <div class="explain">
    <b>A concrete example:</b> Imagine two memories stored in PEP. Memory A: "the user
    mentioned they are afraid of public speaking." Memory B: "the user mentioned they like
    pizza." Both are facts. But if the current conversation turns to a job interview, Memory A
    should activate immediately — it is emotionally loaded, relevant to the stakes, and
    connected to fear, anxiety, and preparation. Memory B should stay dim. The difference
    is not that one is "more true" than the other. The difference is that one has higher
    <b>emotional salience in this context</b>. PEP's state-weighted retrieval handles exactly
    this: the urgency/anxiety state boosts fear-related memories and suppresses neutral ones.
  </div>

  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px">
    <div style="background:var(--surface);border-radius:8px;padding:12px;border:1px solid var(--border)">
      <a href="https://www.youtube.com/watch?v=lEXBxijQREo" target="_blank" style="display:block;position:relative;border-radius:6px;overflow:hidden"><img src="https://img.youtube.com/vi/lEXBxijQREo/hqdefault.jpg" style="width:100%;display:block;border-radius:6px" loading="lazy"><div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:48px;height:48px;background:rgba(0,0,0,0.7);border-radius:50%;display:flex;align-items:center;justify-content:center"><div style="width:0;height:0;border-top:10px solid transparent;border-bottom:10px solid transparent;border-left:18px solid #fff;margin-left:4px"></div></div></a>
      <div style="font-size:10px;color:var(--dim);margin-top:6px;line-height:1.3">How Sugar Affects the Brain</div>
    </div>
    <div style="background:var(--surface);border-radius:8px;padding:12px;border:1px solid var(--border)">
      <a href="https://www.youtube.com/watch?v=16W7c0mb-rE" target="_blank" style="display:block;position:relative;border-radius:6px;overflow:hidden"><img src="https://img.youtube.com/vi/16W7c0mb-rE/hqdefault.jpg" style="width:100%;display:block;border-radius:6px" loading="lazy"><div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:48px;height:48px;background:rgba(0,0,0,0.7);border-radius:50%;display:flex;align-items:center;justify-content:center"><div style="width:0;height:0;border-top:10px solid transparent;border-bottom:10px solid transparent;border-left:18px solid #fff;margin-left:4px"></div></div></a>
      <div style="font-size:10px;color:var(--dim);margin-top:6px;line-height:1.3">Emergence — How Stupid Things Become Smart</div>
    </div>
    <div style="background:var(--surface);border-radius:8px;padding:12px;border:1px solid var(--border)">
      <a href="https://www.youtube.com/watch?v=t-_VPRCtiUg" target="_blank" style="display:block;position:relative;border-radius:6px;overflow:hidden"><img src="https://img.youtube.com/vi/t-_VPRCtiUg/hqdefault.jpg" style="width:100%;display:block;border-radius:6px" loading="lazy"><div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:48px;height:48px;background:rgba(0,0,0,0.7);border-radius:50%;display:flex;align-items:center;justify-content:center"><div style="width:0;height:0;border-top:10px solid transparent;border-bottom:10px solid transparent;border-left:18px solid #fff;margin-left:4px"></div></div></a>
      <div style="font-size:10px;color:var(--dim);margin-top:6px;line-height:1.3">The Surprising Secret of Synchronization</div>
    </div>
    <div style="background:var(--surface);border-radius:8px;padding:12px;border:1px solid var(--border)">
      <a href="https://www.youtube.com/watch?v=lyu7v7nWzfo" target="_blank" style="display:block;position:relative;border-radius:6px;overflow:hidden"><img src="https://img.youtube.com/vi/lyu7v7nWzfo/hqdefault.jpg" style="width:100%;display:block;border-radius:6px" loading="lazy"><div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:48px;height:48px;background:rgba(0,0,0,0.7);border-radius:50%;display:flex;align-items:center;justify-content:center"><div style="width:0;height:0;border-top:10px solid transparent;border-bottom:10px solid transparent;border-left:18px solid #fff;margin-left:4px"></div></div></a>
      <div style="font-size:10px;color:var(--dim);margin-top:6px;line-height:1.3">Your Brain Hallucinates Your Conscious Reality</div>
    </div>
  </div>
</div>
</div><!-- end emotion-tab -->

<!-- ═══ Tab 4: Flow & Optimization ══════════════════════════════════ -->
<div class="tab-panel" id="flow-tab">
<div class="section">
  <h2>Flow &amp; Optimization</h2>
  <p class="subtitle">
    The PTO principle: systems are favored when they maximize <b>constructive
    transformation</b> relative to <b>total dissipation</b>. In plain language:
    do as much useful work as possible with as little waste as possible.
  </p>

  <div class="explain">
    <b>Three teachers of flow:</b> PEP draws inspiration from three natural flow systems,
    each of which teaches a different layer of intelligence:<br><br>
    <b>Subways</b> teach <b>routing under pressure</b> — how a system handles bottlenecks,
    transfers, delays, and rerouting. In PEP, this means information should find efficient
    paths through the network without clogging everything.<br><br>
    <b>Rivers</b> teach <b>emergent flow</b> — how paths of least resistance form naturally,
    branch, merge, erode old routes, and adapt to terrain. Memory should flow toward
    relevance, pool in stable basins, and flood when a topic becomes suddenly important.<br><br>
    <b>The brain</b> teaches <b>dynamic salience</b> — some paths strengthen with use, others
    fade, and the whole system reorganizes based on emotion, repetition, threat, reward,
    and novelty. This is what PEP's State Modulator and per-turn decay are trying to capture.
  </div>

  <div class="formula">
    Efficiency = constructive transformation / total dissipation
  </div>

  <div class="explain">
    <b>PTO — Principle of Transformative Optimality:</b> PEP is built on a theory called PTO.
    The core claim: a good system converts input into useful, adaptive, future-enabling
    structure while minimizing waste and self-damage. This is not just "be efficient" —
    it is deeper. The best move is not always the one with the biggest immediate payoff.
    It is the one that <b>improves the structure of future moves</b>. PTO cares about
    trajectory quality, not local reward.
  </div>

  <div class="explain">
    <b>What counts as constructive:</b> A transformation is constructive if it increases
    predictive power, retrieval precision, conceptual coherence, adaptability to novelty,
    or future learning capacity. A transformation is <b>dissipative</b> if it increases
    noise, confusion, redundancy, contradiction, or brittleness. PEP's design choices
    are judged by this ratio.
  </div>

  <div class="explain">
    <b>Optimization is everywhere:</b> The scoring formula is an optimization problem
    (find the most relevant memory under weighted constraints). Memory storage is an
    optimization problem (store what improves future turns, not just what happened).
    Forgetting is an optimization (reduce clutter so the important things stand out).
    Even category formation is optimization (group things to make the graph more
    navigable without losing resolution).
  </div>

  <div class="explain">
    <b>The emotion analogy:</b> Biological emotions are not just feelings. They are
    <b>weighting functions</b> that change which information gets prioritized. Fear
    narrows attention to threats. Curiosity broadens search to novelty. Joy reinforces
    what worked. In PEP, the State Modulator plays this role: urgency, uncertainty,
    novelty, conflict, exploration, and stability are not emotions, but they serve the
    same mathematical function — they <b>change the weights</b> on every retrieval,
    every storage decision, and every scoring formula, dynamically, on every turn.
  </div>

  <div class="explain">
    <b>The deep principle:</b> Intelligence is not just having information. It is
    <b>structuring</b> information so that the right parts become active at the right
    time. A subway system is not intelligent because it has many stations. It is useful
    because the routes, connections, and schedules are organized so people can get where
    they need to go. PEP tries to do the same for knowledge: not just store everything,
    but arrange it so the right memory surfaces at the right moment with minimal waste.
  </div>

  <div style="margin:20px 0 24px">
    <h3 style="font-size:14px;color:var(--accent2);margin-bottom:10px">Interactive: Information Flow</h3>
    <p style="font-size:11px;color:var(--dim);margin-bottom:12px">
      Watch information (glowing dots) flow through channels of different widths.
      Wide channels = low resistance = efficient flow. Narrow channels = bottleneck = waste.
      This is the PTO principle made visible.
    </p>
    <div class="canvas-wrap">
      <canvas id="flow-canvas" width="800" height="300" style="width:100%;display:block"></canvas>
    </div>
    <div style="margin-top:8px;display:flex;gap:16px;font-size:11px;color:var(--dim)">
      <span>PTO ratio: <b style="color:var(--accent2)" id="pto-ratio">—</b></span>
      <span>constructive: <b style="color:var(--accent)" id="pto-construct">—</b></span>
      <span>dissipated: <b style="color:var(--warn)" id="pto-dissipate">—</b></span>
    </div>
  </div>

  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px">
    <div style="background:var(--surface);border-radius:8px;padding:12px;border:1px solid var(--border)">
      <a href="https://www.youtube.com/watch?v=gB9n2gHsHN4" target="_blank" style="display:block;position:relative;border-radius:6px;overflow:hidden"><img src="https://img.youtube.com/vi/gB9n2gHsHN4/hqdefault.jpg" style="width:100%;display:block;border-radius:6px" loading="lazy"><div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:48px;height:48px;background:rgba(0,0,0,0.7);border-radius:50%;display:flex;align-items:center;justify-content:center"><div style="width:0;height:0;border-top:10px solid transparent;border-bottom:10px solid transparent;border-left:18px solid #fff;margin-left:4px"></div></div></a>
      <div style="font-size:10px;color:var(--dim);margin-top:6px;line-height:1.3">Fractals Are Typically Not Self-Similar</div>
    </div>
    <div style="background:var(--surface);border-radius:8px;padding:12px;border:1px solid var(--border)">
      <a href="https://www.youtube.com/watch?v=kkGeOWYOFoA" target="_blank" style="display:block;position:relative;border-radius:6px;overflow:hidden"><img src="https://img.youtube.com/vi/kkGeOWYOFoA/hqdefault.jpg" style="width:100%;display:block;border-radius:6px" loading="lazy"><div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:48px;height:48px;background:rgba(0,0,0,0.7);border-radius:50%;display:flex;align-items:center;justify-content:center"><div style="width:0;height:0;border-top:10px solid transparent;border-bottom:10px solid transparent;border-left:18px solid #fff;margin-left:4px"></div></div></a>
      <div style="font-size:10px;color:var(--dim);margin-top:6px;line-height:1.3">Nature by Numbers</div>
    </div>
    <div style="background:var(--surface);border-radius:8px;padding:12px;border:1px solid var(--border)">
      <a href="https://www.youtube.com/watch?v=ovJcsL7vyrk" target="_blank" style="display:block;position:relative;border-radius:6px;overflow:hidden"><img src="https://img.youtube.com/vi/ovJcsL7vyrk/hqdefault.jpg" style="width:100%;display:block;border-radius:6px" loading="lazy"><div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:48px;height:48px;background:rgba(0,0,0,0.7);border-radius:50%;display:flex;align-items:center;justify-content:center"><div style="width:0;height:0;border-top:10px solid transparent;border-bottom:10px solid transparent;border-left:18px solid #fff;margin-left:4px"></div></div></a>
      <div style="font-size:10px;color:var(--dim);margin-top:6px;line-height:1.3">The Logistic Map</div>
    </div>
    <div style="background:var(--surface);border-radius:8px;padding:12px;border:1px solid var(--border)">
      <a href="https://www.youtube.com/watch?v=r6sGWTCMz2k" target="_blank" style="display:block;position:relative;border-radius:6px;overflow:hidden"><img src="https://img.youtube.com/vi/r6sGWTCMz2k/hqdefault.jpg" style="width:100%;display:block;border-radius:6px" loading="lazy"><div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:48px;height:48px;background:rgba(0,0,0,0.7);border-radius:50%;display:flex;align-items:center;justify-content:center"><div style="width:0;height:0;border-top:10px solid transparent;border-bottom:10px solid transparent;border-left:18px solid #fff;margin-left:4px"></div></div></a>
      <div style="font-size:10px;color:var(--dim);margin-top:6px;line-height:1.3">But what is a Fourier series?</div>
    </div>
  </div>
</div>
</div><!-- end flow-tab -->

<!-- ═══ Tab 5: Applications ═════════════════════════════════════════ -->
<div class="tab-panel" id="applications">
<div class="section">
  <h2>Where PEP Applies</h2>
  <p class="subtitle">
    PEP is a general mathematical framework for structuring, weighting, and
    retrieving information. That means it applies anywhere relationships,
    patterns, and context matter — which turns out to be almost everywhere.
  </p>

  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;margin-top:20px">

    <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;
                padding:18px 20px;border-left:3px solid #4fc3f7">
      <h3 style="font-size:14px;color:#4fc3f7;margin-bottom:8px">Language &amp; Linguistics</h3>
      <p style="font-size:12px;color:var(--text);line-height:1.6;margin-bottom:8px">
        Languages are weighted networks of words, meanings, and sounds that evolve over time.
        PEP can track how words connect, drift in meaning, branch across dialects, and
        reorganize when a language changes. A word is not a definition — it is a node in a
        living graph of relationships.
      </p>
      <p style="font-size:11px;color:var(--dim);line-height:1.5">
        <b>Applications:</b> language progression tracking, etymology visualization,
        semantic drift detection, multilingual comparison, language learning systems
        that adapt to how you actually acquire meaning — not just how many flashcards
        you clicked.
      </p>
      <p style="font-size:10px;margin-top:6px">
        <a href="/lingora" style="color:#4fc3f7">Explore Lingora &rarr;</a>
      </p>
      <canvas id="app-lang-canvas" width="260" height="80" style="width:100%;margin-top:8px;border-radius:4px;cursor:pointer"></canvas>
    </div>

    <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;
                padding:18px 20px;border-left:3px solid #81c784">
      <h3 style="font-size:14px;color:#81c784;margin-bottom:8px">Skill-Based Matchmaking</h3>
      <p style="font-size:12px;color:var(--text);line-height:1.6;margin-bottom:8px">
        Current matchmaking in games reduces a player to one number (MMR/Elo). Real skill
        is multi-dimensional: aggression, patience, mechanical speed, strategic depth,
        tilt tendency, clutch factor. PEP can model each player as a weighted profile and
        match not just by rank, but by compatibility, playstyle, and predicted experience
        quality.
      </p>
      <p style="font-size:11px;color:var(--dim);line-height:1.5">
        <b>Applications:</b> PvP game matchmaking that optimizes for enjoyment (not just
        statistical fairness), team formation, toxicity prediction, behavior-aware
        lobbies, coaching alignment, ranked duo recommendations.
      </p>
      <p style="font-size:10px;margin-top:6px">
        <a href="/atria" style="color:#81c784">Explore Atria &rarr;</a>
      </p>
      <canvas id="app-match-canvas" width="260" height="80" style="width:100%;margin-top:8px;border-radius:4px;cursor:pointer"></canvas>
    </div>

    <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;
                padding:18px 20px;border-left:3px solid #ffb74d">
      <h3 style="font-size:14px;color:#ffb74d;margin-bottom:8px">Data &amp; Pattern Intelligence</h3>
      <p style="font-size:12px;color:var(--text);line-height:1.6;margin-bottom:8px">
        Information is not a pile. It has structure, weight, context, and direction.
        PEP treats data as a relational network where relevance changes dynamically —
        what matters depends on what you are looking for. That makes retrieval sharper,
        storage more efficient, and pattern detection more meaningful.
      </p>
      <p style="font-size:11px;color:var(--dim);line-height:1.5">
        <b>Applications:</b> intelligent retrieval systems, semantic search, knowledge
        graphs, recommendation engines, anomaly detection, any system where "more data"
        is not the answer but "better organized data" is.
      </p>
      <canvas id="app-data-canvas" width="260" height="80" style="width:100%;margin-top:8px;border-radius:4px;cursor:pointer"></canvas>
    </div>

    <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;
                padding:18px 20px;border-left:3px solid #ba68c8">
      <h3 style="font-size:14px;color:#ba68c8;margin-bottom:8px">Brain &amp; Cognition — <span style="font-weight:normal;font-size:12px">Axona</span></h3>
      <p style="font-size:12px;color:var(--text);line-height:1.6;margin-bottom:8px">
        The brain is a dynamic weighted network. Memories strengthen with use, weaken
        without it, merge into abstractions, and reconstruct on every recall. PEP
        models these same principles computationally: spreading activation, salience
        weighting, drift tracking, and reconsolidation.
      </p>
      <p style="font-size:11px;color:var(--dim);line-height:1.5">
        <b>Applications:</b> cognitive modeling, the genius/breakdown threshold,
        belief as a predictive state (placebo mechanism), cognitive bandwidth,
        conformity as adaptive neural strategy, creativity modeling.
      </p>
      <p style="font-size:10px;margin-top:6px">
        <a href="/axona" style="color:#ba68c8">Explore Axona &rarr;</a>
      </p>
      <canvas id="app-brain-canvas" width="260" height="80" style="width:100%;margin-top:8px;border-radius:4px;cursor:pointer"></canvas>
    </div>

    <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;
                padding:18px 20px;border-left:3px solid #f06292">
      <h3 style="font-size:14px;color:#f06292;margin-bottom:8px">Markets &amp; Trading</h3>
      <p style="font-size:12px;color:var(--text);line-height:1.6;margin-bottom:8px">
        Markets are flow systems with resistance, friction, amplification, and
        dissipation. PEP can weight signals by novelty, detect unusual movement
        patterns, and model how information propagates through sectors. The same
        math that tracks spreading activation in a concept network can track
        spreading momentum in a market.
      </p>
      <p style="font-size:11px;color:var(--dim);line-height:1.5">
        <b>Applications:</b> signal analysis, unusual activity detection, sentiment
        weighting, paper-trading strategy engines, sector comparison, portfolio
        optimization under uncertainty.
      </p>
      <canvas id="app-market-canvas" width="260" height="80" style="width:100%;margin-top:8px;border-radius:4px;cursor:pointer"></canvas>
    </div>

    <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;
                padding:18px 20px;border-left:3px solid var(--text)">
      <h3 style="font-size:14px;color:var(--text);margin-bottom:8px">And Many More</h3>
      <p style="font-size:12px;color:var(--text);line-height:1.6;margin-bottom:8px">
        The math behind PEP — graph theory, weighted networks, optimization,
        spreading activation, power/effect, and the idea lifecycle — applies
        anywhere information has relationships and context matters.
      </p>
      <p style="font-size:11px;color:var(--dim);line-height:1.5">
        <b>Other domains:</b> education systems that track real understanding (not just
        test scores), transportation networks (subway routing, traffic flow), social
        network analysis, scientific literature mapping, music recommendation by
        structural similarity, city planning, ecological modeling, creative writing
        tools, and any field where the question is not "what exists?" but "what
        connects, what matters, and what emerges?"
      </p>
    </div>

  </div>

  <div style="margin-top:28px;padding:16px 20px;background:var(--surface2);
              border-radius:8px;border:1px solid var(--accent)">
    <p style="font-size:13px;color:var(--text);line-height:1.7;margin:0">
      <b style="color:var(--accent)">The core insight:</b> PEP is not tied to one domain.
      It is a mathematical framework for how information is <b>stored</b>, <b>connected</b>,
      <b>weighted</b>, <b>retrieved</b>, and <b>transformed</b>. The same principles that
      describe how a word connects to other words also describe how a player connects to
      a team, how a memory connects to an emotion, how a signal connects to a market move,
      and how an idea connects to the ideas that came before it.
    </p>
    <p style="font-size:12px;color:var(--dim);line-height:1.6;margin-top:10px;margin-bottom:0">
      That universality is what makes math powerful. It reveals that underneath the
      surface differences of things, there are deep similarities in structure.
    </p>
  </div>
</div>

</div><!-- end section -->
</div><!-- end applications tab-panel -->

<!-- About section — always visible at the bottom -->
<div style="max-width:1100px;margin:40px auto 20px;padding:20px;text-align:center;
     border-top:1px solid var(--border)">
  <p style="font-size:12px;color:var(--dim);line-height:1.7;max-width:700px;margin:0 auto">
    <b style="color:var(--accent)">PEP Math Playground</b> — an interactive exploration of the
    mathematics behind <b>Predictive Encoding &amp; Preparation</b> (PEP), a framework for
    structuring, weighting, and retrieving information using graph theory, spreading activation,
    weighted scoring, and the Principle of Transformative Optimality (PTO). Built as a demonstration
    that math describes relationships, influence, and transformation — not just arithmetic.
  </p>
  <p style="font-size:10px;color:var(--dim);margin-top:10px">
    Keyboard shortcuts: <code style="background:var(--surface);padding:1px 5px;border-radius:3px">/</code> search
    &nbsp; <code style="background:var(--surface);padding:1px 5px;border-radius:3px">G</code> grow
    &nbsp; <code style="background:var(--surface);padding:1px 5px;border-radius:3px">Esc</code> clear
    &nbsp; <code style="background:var(--surface);padding:1px 5px;border-radius:3px">Shift+click</code> compare
  </p>
</div>
<div style="height:20px"></div>

<script>
// ═══════════════════════════════════════════════════════════════════════
// Theme color cache — avoids getComputedStyle in hot animation loops
// ═══════════════════════════════════════════════════════════════════════
const _tc = { canvasBg: '#0e0e12', surface: '#1a1a2e', accent: '#4fc3f7', dim: '#888' };
function refreshThemeColors() {
  const s = getComputedStyle(document.documentElement);
  _tc.canvasBg = s.getPropertyValue('--canvas-bg').trim() || '#0e0e12';
  _tc.surface = s.getPropertyValue('--surface').trim() || '#1a1a2e';
  _tc.accent = s.getPropertyValue('--accent').trim() || '#4fc3f7';
  _tc.dim = s.getPropertyValue('--dim').trim() || '#888';
}
refreshThemeColors();

// ═══════════════════════════════════════════════════════════════════════
// Tab switching — targets .tab-panel divs, not .section divs
// ═══════════════════════════════════════════════════════════════════════
document.querySelectorAll('.math-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.math-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    tab.classList.add('active');
    const target = document.getElementById(tab.dataset.section);
    if (target) target.classList.add('active');
    window.scrollTo(0, 0);
    // Trigger canvas redraws for tabs that have visuals (they have zero
    // dimensions when hidden so the initial draw produces nothing)
    setTimeout(() => {
      if (tab.dataset.section === 'vectors-tab') drawVectorSpace();
      if (tab.dataset.section === 'prediction-tab') updateBayes();
      if (tab.dataset.section === 'emotion-tab') drawEmopic();
      if (tab.dataset.section === 'flow-tab') { flowConstructive=0; flowDissipated=0; drawFlow(); }
    }, 100);
  });
});

// ═══════════════════════════════════════════════════════════════════════
// Graph state
// ═══════════════════════════════════════════════════════════════════════
let nodes = [];        // {id, label, x, y, brightness, activation, selected, vx, vy}
let edges = [];        // {source, target, weight, directed}
let nextId = 1;
let queryNodeId = null;
let hoveredNode = null; // tracked for label-on-hover
let dragging = null;   // node being dragged
let dragEdge = null;   // {from: nodeId, x, y} while creating an edge
let simulation = null;

const canvas = document.getElementById('graph-canvas');
const ctx = canvas.getContext('2d');
let zoomTransform = {x: 0, y: 0, k: 1};  // pan + zoom state

function resizeCanvas() {
  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.parentElement.getBoundingClientRect();
  canvas.width = rect.width * dpr;
  canvas.height = 640 * dpr;
  canvas.style.width = rect.width + 'px';
  canvas.style.height = '640px';
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
}
resizeCanvas();
window.addEventListener('resize', () => { resizeCanvas(); });

// D3 zoom on the canvas — stored as a variable so the zoom buttons can use it.
let zoomBehavior = null;
if (typeof d3 !== 'undefined') {
  zoomBehavior = d3.zoom()
    .scaleExtent([0.15, 4])
    .filter((event) => {
      if (event.type === 'wheel') return true;
      const rect = canvas.getBoundingClientRect();
      const sx = event.clientX - rect.left;
      const sy = event.clientY - rect.top;
      return !nodeAt(sx, sy);
    })
    .on('zoom', (event) => {
      zoomTransform = event.transform;
    });
  d3.select(canvas).call(zoomBehavior);
}

function zoomIn() {
  if (!zoomBehavior) return;
  d3.select(canvas).transition().duration(300).call(zoomBehavior.scaleBy, 1.4);
}
function zoomOut() {
  if (!zoomBehavior) return;
  d3.select(canvas).transition().duration(300).call(zoomBehavior.scaleBy, 0.7);
}
function zoomFit() {
  if (typeof d3 === 'undefined' || nodes.length === 0) return;
  const W = canvas.clientWidth, H = canvas.clientHeight;
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
  nodes.forEach(n => {
    if (n.x < minX) minX = n.x; if (n.x > maxX) maxX = n.x;
    if (n.y < minY) minY = n.y; if (n.y > maxY) maxY = n.y;
  });
  const pad = 40;
  const gw = (maxX - minX) || 1, gh = (maxY - minY) || 1;
  const scale = Math.min((W - pad*2) / gw, (H - pad*2) / gh, 2);
  const cx = (minX + maxX) / 2, cy = (minY + maxY) / 2;
  const tx = W/2 - cx * scale, ty = H/2 - cy * scale;
  const t = d3.zoomIdentity.translate(tx, ty).scale(scale);
  if (zoomBehavior) d3.select(canvas).transition().duration(500).call(zoomBehavior.transform, t);
  zoomTransform = t;
}

// Convert screen coords to graph coords (accounting for zoom)
function screenToGraph(sx, sy) {
  return [(sx - zoomTransform.x) / zoomTransform.k,
          (sy - zoomTransform.y) / zoomTransform.k];
}

// ═══════════════════════════════════════════════════════════════════════
// Node / edge creation
// ═══════════════════════════════════════════════════════════════════════
// ═══════════════════════════════════════════════════════════════════════
// Definitions — shown on hover. Key words get hand-written definitions;
// the rest get auto-generated descriptions from their cluster + neighbors.
// ═══════════════════════════════════════════════════════════════════════
const DEFINITIONS = {
  // People
  person:'a human being considered individually',man:'an adult male human',woman:'an adult female human',
  child:'a young human being',baby:'a very young child',family:'a group of related people',
  friend:'someone you trust and enjoy being with',mother:'a female parent',father:'a male parent',
  brother:'a male sibling',sister:'a female sibling',neighbor:'someone who lives nearby',
  stranger:'a person you do not know',crowd:'a large group of people gathered together',
  group:'a number of people or things together',boy:'a young male',girl:'a young female',
  elder:'an older person, often respected for wisdom',youth:'the period of being young',
  husband:'a married man',wife:'a married woman',daughter:'a female child',son:'a male child',
  // Body
  hand:'the body part used to grasp and manipulate',eye:'the organ of sight',
  head:'the upper part of the body containing the brain',heart:'the organ that pumps blood; the center of emotion',
  face:'the front of the head; how you present yourself',mouth:'the opening used for eating and speaking',
  foot:'the base of the leg used for standing and walking',arm:'the upper limb of the body',
  skin:'the outer covering of the body',blood:'the red fluid circulating through the body',
  bone:'the hard tissue forming the skeleton',brain:'the organ of thought and control',
  voice:'sound produced by the vocal cords for speech',hair:'threadlike strands growing from the skin',
  finger:'one of the digits of the hand',body:'the physical structure of a person',
  tooth:'a hard structure in the mouth used for biting',ear:'the organ of hearing',
  chest:'the front of the upper body',shoulder:'the joint connecting arm to body',
  knee:'the joint in the middle of the leg',back:'the rear surface of the body',
  neck:'the part connecting head to body',stomach:'the organ where food is digested',
  muscle:'tissue that contracts to produce movement',nerve:'a fiber that transmits signals in the body',
  breath:'air taken into and expelled from the lungs',lung:'the organ used for breathing',
  // Nature
  water:'a clear liquid essential for all life',sun:'the star at the center of our solar system',
  earth:'the planet we live on; also soil or ground',tree:'a large plant with a trunk and branches',
  fire:'the phenomenon of combustion producing heat and light',air:'the invisible mixture of gases we breathe',
  river:'a large natural stream of flowing water',ocean:'the vast body of salt water covering most of earth',
  mountain:'a large natural elevation of the earth',stone:'a small piece of rock',
  flower:'the reproductive part of a plant, often colorful',leaf:'a flat green part of a plant that captures sunlight',
  root:'the underground part of a plant that absorbs water',seed:'the embryo of a new plant',
  forest:'a large area densely covered with trees',grass:'short green plants covering the ground',
  sand:'tiny grains of rock found on beaches and deserts',wave:'a moving ridge on the surface of water',
  island:'land completely surrounded by water',valley:'a low area between hills or mountains',
  desert:'a dry barren area with little rainfall',lake:'a body of still water surrounded by land',
  soil:'the upper layer of earth where plants grow',coral:'marine organisms that build reef structures',
  vine:'a climbing or trailing plant',mushroom:'a fungus with a cap and stem',
  // Sky
  sky:'the expanse of air above the earth',star:'a luminous point in the night sky; a distant sun',
  moon:'the natural satellite orbiting the earth',cloud:'a visible mass of water droplets in the sky',
  rain:'water falling from clouds as droplets',wind:'moving air caused by pressure differences',
  snow:'frozen water crystals falling from the sky',storm:'a violent atmospheric disturbance',
  thunder:'the sound caused by lightning',lightning:'a sudden electrical discharge in the atmosphere',
  rainbow:'an arc of colors caused by light refracting through water',dawn:'the first light of day',
  dusk:'the darker part of twilight as night approaches',shadow:'a dark shape cast by blocking light',
  light:'what makes things visible; also understanding',dark:'the absence of light',
  fog:'thick low-lying cloud that reduces visibility',frost:'a thin layer of ice on surfaces',
  horizon:'the line where earth and sky appear to meet',comet:'an icy body that develops a tail near the sun',
  eclipse:'when one celestial body blocks the light of another',meteor:'a streak of light from space debris burning up',
  sunrise:'the moment the sun appears above the horizon',sunset:'the moment the sun disappears below the horizon',
  twilight:'the soft light after sunset or before sunrise',
  // Time
  time:'the ongoing sequence of events from past to future',day:'the period of light between sunrise and sunset',
  night:'the period of darkness between sunset and sunrise',year:'the time it takes earth to orbit the sun',
  morning:'the early part of the day',evening:'the later part of the day before night',
  hour:'a unit of time equal to sixty minutes',moment:'a very brief period of time',
  past:'the time that has already happened',future:'the time that has not yet happened',
  now:'the present moment',season:'one of the four divisions of the year',
  spring:'the season of new growth after winter',summer:'the warmest season of the year',
  autumn:'the season when leaves fall',winter:'the coldest season of the year',
  age:'the length of time something has existed',century:'a period of one hundred years',
  clock:'a device for measuring and showing time',forever:'for all future time; without end',
  instant:'an extremely short period of time',change:'to become different; the only constant',
  begin:'to start; the first part of something',end:'to finish; the final part of something',
  death:'the permanent end of life',birth:'the moment of coming into existence',
  grow:'to increase in size, number, or strength',decay:'to gradually deteriorate or decompose',
  // Place
  home:'a place of belonging and safety',city:'a large settlement of people',
  road:'a wide path for traveling',world:'the earth and all its inhabitants',
  land:'the solid surface of the earth',country:'a nation with its own government',
  village:'a small settlement smaller than a town',door:'a movable barrier at an entrance',
  room:'an enclosed space within a building',wall:'a vertical structure dividing or enclosing space',
  floor:'the lower surface of a room',bridge:'a structure connecting two separated places',
  garden:'a cultivated area for growing plants',field:'an open area of land',
  street:'a paved road in a town or city',tower:'a tall narrow building or structure',
  church:'a building for religious worship',market:'a place where goods are bought and sold',
  castle:'a large fortified building',harbor:'a sheltered area of water for ships',
  cave:'a natural underground chamber',path:'a narrow way for walking',
  border:'the edge or boundary of something',corner:'the point where two edges meet',
  center:'the middle point of something',edge:'the outer boundary of something',
  window:'an opening in a wall for light and air',roof:'the top covering of a building',
  // Communication
  word:'a unit of language carrying meaning',speak:'to produce words with the voice',
  story:'a narrative of events, real or imagined',name:'a word that identifies a specific person or thing',
  book:'a written work bound together',write:'to form letters and words on a surface',
  read:'to interpret written text',language:'a structured system of communication',
  letter:'a written symbol representing a sound',sign:'something that indicates or represents',
  message:'information sent from one person to another',lie:'a false statement made to deceive',
  secret:'something kept hidden from others',promise:'a commitment to do something',
  silence:'the absence of sound',listen:'to pay attention to sound',
  shout:'to speak very loudly',whisper:'to speak very softly',
  argue:'to present reasons for or against something',explain:'to make something clear and understandable',
  translate:'to express in another language',grammar:'the rules governing language structure',
  phrase:'a small group of words forming a unit',meaning:'what something signifies or represents',
  symbol:'something that stands for something else',text:'written or printed words',
  // Mind
  think:'to use the mind to form ideas',know:'to be aware of through experience or learning',
  feel:'to experience an emotion or sensation',love:'deep affection and care for something',
  fear:'an emotional response to perceived danger',dream:'images during sleep; also an aspiration',
  idea:'a thought or concept formed in the mind',memory:'the ability to store and recall past experience',
  hope:'expectation and desire for something to happen',wish:'a desire for something to be true',
  believe:'to accept something as true',understand:'to grasp the meaning of something',
  imagine:'to form mental images of things not present',wonder:'a feeling of amazement; also to question',
  doubt:'a feeling of uncertainty',reason:'the power of logical thinking',
  thought:'a product of thinking',mind:'the seat of consciousness and thought',
  conscious:'aware of your own existence and surroundings',attention:'focused mental engagement',
  focus:'concentrated attention on something',forget:'to fail to remember',
  recall:'to bring back to mind',insight:'a deep understanding of something',
  intuition:'understanding without conscious reasoning',curiosity:'a desire to know or learn',
  confusion:'inability to think clearly; lack of understanding',
  // Action
  make:'to bring into existence or produce',give:'to transfer to someone else',
  take:'to get hold of something',move:'to change position or location',
  work:'to exert effort toward a purpose',play:'to engage in activity for enjoyment',
  find:'to discover something',run:'to move quickly on foot',
  walk:'to move at a regular pace on foot',stand:'to be in an upright position',
  sit:'to rest with weight on the buttocks',hold:'to keep in your grasp',
  break:'to separate into pieces',build:'to construct by putting parts together',
  open:'to move so as to allow access',close:'to move so as to block access',
  pull:'to draw toward yourself',push:'to press away from yourself',
  carry:'to transport from one place to another',throw:'to propel through the air',
  catch:'to seize something in motion',fight:'to struggle against with force',
  sleep:'a state of rest with reduced consciousness',wake:'to stop sleeping; to become alert',
  climb:'to move upward using hands and feet',swim:'to move through water',
  fly:'to move through the air',dig:'to break up and move earth',
  search:'to look carefully to find something',hide:'to put out of sight',
  share:'to give a portion to others',choose:'to select from alternatives',
  create:'to bring something new into existence',destroy:'to end the existence of something',
  // Society
  power:'the ability to influence or cause change',money:'a medium of exchange representing value',
  king:'a male ruler of a kingdom',law:'a system of rules governing behavior',
  war:'armed conflict between groups',peace:'the absence of conflict',
  freedom:'the state of being free from constraint',justice:'fairness in how people are treated',
  people:'human beings collectively',leader:'a person who guides or directs others',
  army:'an organized military force',trade:'the exchange of goods and services',
  tax:'money paid to a government',vote:'a formal expression of choice',
  right:'a moral or legal entitlement',rule:'an authoritative regulation',
  prison:'a place of confinement for criminals',court:'a place where justice is administered',
  government:'the system that controls a state',citizen:'a member of a state or nation',
  revolution:'a fundamental change in political power',wealth:'an abundance of valuable resources',
  poverty:'the state of being extremely poor',class:'a social division based on status',
  nation:'a large group of people sharing culture and territory',politics:'activities related to governing',
  empire:'a group of nations ruled by one authority',
  // Food
  food:'any substance consumed for nutritional support',bread:'a staple food made from flour and water',
  meat:'the flesh of animals used as food',milk:'a white liquid produced by mammals',
  salt:'a mineral used to season and preserve food',sugar:'a sweet substance from plants',
  fruit:'the seed-bearing part of a plant, often sweet',grain:'the seeds of cereal plants',
  cook:'to prepare food by heating',eat:'to consume food',
  drink:'to take liquid into the mouth',hunger:'a strong need for food',
  taste:'the sensation of flavor',egg:'an oval body laid by birds containing offspring',
  rice:'a cereal grain and staple food for much of the world',wine:'an alcoholic drink made from fermented grapes',
  honey:'a sweet substance made by bees',spice:'a substance used to flavor food',
  feast:'a large celebratory meal',harvest:'the gathering of crops',
  farm:'land used for growing crops or raising animals',apple:'a round fruit with red or green skin',
  cheese:'a food made from pressed milk curds',oil:'a viscous liquid used in cooking',
  soup:'a liquid food made by boiling ingredients',
  // Knowledge
  learn:'to gain knowledge through study or experience',teach:'to give knowledge to someone',
  school:'a place of education',question:'a request for information',
  answer:'a response to a question',math:'the science of number, quantity, and space',
  science:'systematic study through observation and experiment',number:'a mathematical value used for counting',
  pattern:'a repeated arrangement revealing structure',test:'an assessment of knowledge or ability',
  student:'a person who is learning',theory:'a system of ideas explaining something',
  fact:'something known to be true',proof:'evidence establishing truth',
  study:'to apply the mind to learning',logic:'reasoning according to strict principles',
  experiment:'a test to discover something unknown',discovery:'finding something for the first time',
  research:'systematic investigation to establish facts',measure:'to determine the size or amount of something',
  calculate:'to determine by mathematical methods',equation:'a statement that two expressions are equal',
  formula:'a mathematical rule expressed in symbols',geometry:'the math of shapes and spatial relationships',
  algebra:'the math of symbols and rules for manipulating them',infinity:'without limit; endlessly large',
  zero:'the number representing nothing; the additive identity',
  // Art
  music:'organized sound in patterns of rhythm and pitch',song:'a musical composition with words',
  dance:'rhythmic movement of the body',art:'the expression of creative imagination',
  color:'the property of light as seen by the eye',paint:'to apply color to a surface to create images',
  draw:'to produce a picture with lines',beauty:'a quality that gives pleasure to the senses',
  shape:'the external form of something',form:'the visible structure of something',
  rhythm:'a repeated pattern of movement or sound',sound:'vibrations that travel through air and are heard',
  image:'a visual representation',picture:'a painting, drawing, or photograph',
  poem:'a piece of writing with rhythm and imagery',stage:'a raised platform for performance',
  film:'a series of moving images telling a story',craft:'skill in making things by hand',
  sculpture:'a three-dimensional work of art',melody:'a sequence of musical notes forming a tune',
  harmony:'the combination of simultaneous musical notes',design:'a plan or arrangement of elements',
  style:'a distinctive way of doing something',expression:'conveying thoughts or feelings',
  inspire:'to fill with creative motivation',
  // Animal
  animal:'a living creature that moves and feeds',dog:'a domesticated carnivore kept as a pet',
  cat:'a small domesticated feline',bird:'a warm-blooded creature with feathers and wings',
  horse:'a large animal used for riding and transport',cow:'a large domesticated animal raised for milk and meat',
  sheep:'a woolly domesticated animal',wolf:'a wild predator related to dogs',
  snake:'a limbless reptile',bear:'a large heavy mammal',
  lion:'a large wild cat; the king of beasts',mouse:'a small rodent',
  deer:'a hoofed animal with antlers',eagle:'a large bird of prey',
  whale:'the largest marine mammal',ant:'a tiny social insect',
  bee:'a flying insect that makes honey',spider:'an eight-legged creature that spins webs',
  elephant:'the largest land animal',tiger:'a large striped wild cat',
  fox:'a small cunning wild canine',rabbit:'a small long-eared burrowing mammal',
  frog:'an amphibian that leaps and croaks',shark:'a large predatory fish',
  dolphin:'an intelligent marine mammal',crow:'a large black intelligent bird',
  owl:'a nocturnal bird of prey',bat:'a flying mammal active at night',
  // Emotion
  joy:'a feeling of great happiness',anger:'a strong feeling of displeasure and hostility',
  sadness:'a feeling of sorrow or grief',surprise:'an unexpected event or feeling',
  trust:'firm belief in the reliability of someone',disgust:'a strong feeling of revulsion',
  shame:'a painful feeling of humiliation',pride:'satisfaction in your own achievements',
  guilt:'a feeling of responsibility for wrongdoing',jealousy:'resentment of someone else having something',
  courage:'the ability to face fear and difficulty',patience:'the capacity to endure delay without frustration',
  kindness:'the quality of being friendly and generous',hate:'intense dislike or hostility',
  desire:'a strong feeling of wanting something',pain:'physical suffering or mental distress',
  comfort:'a state of ease and freedom from pain',loneliness:'sadness from being alone',
  gratitude:'thankfulness and appreciation',empathy:'understanding and sharing another person feelings',
  anxiety:'a feeling of worry about the future',calm:'a state of peacefulness and quiet',
  excitement:'a feeling of eager enthusiasm',grief:'intense sorrow especially from loss',
  nostalgia:'a sentimental longing for the past',awe:'a feeling of wonder and reverence',
  // Technology
  machine:'a device that performs a task mechanically',tool:'an instrument used to do work',
  wheel:'a circular device that rotates on an axle',engine:'a machine that converts energy into motion',
  computer:'a device that processes information by following instructions',
  network:'a group of interconnected things or people',system:'a set of connected parts forming a whole',
  device:'an object made for a particular purpose',wire:'a thin flexible strand of metal',
  signal:'a sign conveying information or instruction',digital:'using discrete values, usually 0 and 1',
  electric:'powered by or relating to electricity',energy:'the capacity to do work',
  battery:'a device that stores electrical energy',program:'a set of instructions for a computer',
  algorithm:'a step-by-step procedure for solving a problem',artificial:'made by humans rather than nature',
  intelligence:'the ability to learn, reason, and solve problems',process:'a series of steps toward a result',
  software:'programs and data that run on a computer',hardware:'the physical components of a computer',
  internet:'a global network connecting millions of computers',server:'a computer that provides data to other computers',
  screen:'a display surface for showing information',robot:'a machine that can perform tasks automatically',
  // Abstract
  truth:'what corresponds to reality',good:'morally right or beneficial',
  evil:'profoundly immoral and harmful',real:'actually existing, not imagined',
  possible:'able to happen or be done',order:'a meaningful arrangement of things',
  chaos:'complete disorder and unpredictability',balance:'equal distribution of weight or importance',
  structure:'the way parts are organized into a whole',whole:'complete, entire, not divided',
  part:'a piece of something larger',cause:'what produces an effect',
  effect:'a result produced by a cause',relation:'a connection between two things',
  value:'the worth or importance of something',purpose:'the reason something exists',
  identity:'what makes something itself and not something else',self:'your own being and consciousness',
  other:'something different or separate',same:'identical, not different',
  different:'not the same',constant:'unchanging over time',
  code:'a system of symbols for representing information',data:'facts collected for analysis',model:'a simplified representation of something complex',
};

// Cluster-specific fallback definitions — much better than generic placeholder
const CLUSTER_DEFS = {
  people: 'a person, role, or relationship in human life',
  body: 'a part, organ, or sensation of the human body',
  nature: 'an element, plant, or feature of the natural world',
  sky: 'a phenomenon of the sky, weather, or atmosphere',
  time: 'a period, moment, or concept related to the passage of time',
  place: 'a location, building, or physical space',
  communication: 'a form, tool, or act of human communication',
  mind: 'a mental state, cognitive process, or psychological capacity',
  action: 'a physical action, movement, or activity',
  society: 'an institution, system, or aspect of social organization',
  food: 'a food, ingredient, drink, or aspect of eating and cooking',
  knowledge: 'a concept in science, mathematics, or formal study',
  art: 'an art form, creative medium, or expressive technique',
  animal: 'a species or type of living creature',
  emotion: 'an emotional state, feeling, or psychological response',
  technology: 'a technology, device, system, or digital concept',
  abstract: 'an abstract idea, philosophical concept, or logical relation',
  clothing: 'a garment, fabric, accessory, or fashion item',
  transport: 'a vehicle, route, or aspect of travel and movement',
  material: 'a physical material, substance, or raw element',
  health: 'a medical condition, body function, or health practice',
  sports: 'a sport, game, competition, or athletic concept',
  weather: 'a weather pattern, climate condition, or atmospheric event',
  space: 'a celestial body, cosmic force, or space exploration concept',
  music_detail: 'a musical term, genre, instrument, or production technique',
  geography: 'a geographical feature, landform, or terrain type',
  home_life: 'a household item, room, appliance, or domestic tool',
  mythology: 'a mythological figure, creature, place, or concept from ancient stories',
  work: 'a profession, workplace role, or aspect of employment and career',
  relationship: 'a dynamic, quality, or event in human relationships and social bonds',
};

// Lazy-loaded definitions from the Free Dictionary API.
// Fetched once per word on first hover, then cached.
const _apiDefCache = {};
let _apiFetching = {};

function fetchDefinition(word) {
  if (_apiDefCache[word] || _apiFetching[word]) return;
  _apiFetching[word] = true;
  fetch('https://api.dictionaryapi.dev/api/v2/entries/en/' + encodeURIComponent(word))
    .then(function(r) { return r.ok ? r.json() : Promise.reject(r.status); })
    .then(function(data) {
      const entry = data[0];
      const meanings = entry.meanings || [];
      if (meanings.length > 0 && meanings[0].definitions && meanings[0].definitions.length > 0) {
        _apiDefCache[word] = meanings[0].definitions[0].definition;
      } else {
        _apiDefCache[word] = null;  // mark as "tried, no result"
      }
      delete _apiFetching[word];
    })
    .catch(function() {
      _apiDefCache[word] = null;  // mark as tried so we don't retry forever
      delete _apiFetching[word];
    });
}

function getDefinition(node) {
  if (node._definition) return node._definition;
  if (DEFINITIONS[node.label]) return DEFINITIONS[node.label];
  // Check API cache (null means "tried but no result")
  if (_apiDefCache[node.label]) return _apiDefCache[node.label];
  if (_apiDefCache[node.label] === undefined) {
    // Not yet fetched — trigger async fetch, show cluster fallback for now
    fetchDefinition(node.label);
  }
  // Cluster fallback (always available instantly)
  if (node._cluster && CLUSTER_DEFS[node._cluster]) {
    return CLUSTER_DEFS[node._cluster];
  }
  return node.label;
}

function startBatch() { _batchMode = true; }
function endBatch() {
  _batchMode = false;
  rebuildSimulation();
  updateStats();
}

function addNode(label, x, y) {
  const n = {
    id: nextId++, label: label || 'node',
    x: x || canvas.clientWidth / 2 + (Math.random() - 0.5) * 100,
    y: y || canvas.clientHeight / 2 + (Math.random() - 0.5) * 100,
    brightness: 0.5 + Math.random() * 0.3,
    activation: 0, selected: false, vx: 0, vy: 0,
  };
  nodes.push(n);
  if (!_batchMode) {
    rebuildSimulation();
    updateStats();
  }
  return n;
}

let _batchMode = false;  // skip expensive updates during bulk loading

function addEdge(sourceId, targetId, weight, directed) {
  if (sourceId === targetId) return;
  // Skip duplicate check in batch mode (too slow with 6000+ edges)
  if (!_batchMode) {
    if (edges.find(e => (e.source === sourceId && e.target === targetId) ||
                         (!directed && e.source === targetId && e.target === sourceId))) return;
  }
  edges.push({source: sourceId, target: targetId, weight: weight || 0.5, directed: !!directed});
  if (!_batchMode) {
    rebuildSimulation();
    updateStats();
  }
}

function removeNode(id) {
  nodes = nodes.filter(n => n.id !== id);
  edges = edges.filter(e => e.source !== id && e.target !== id);
  if (queryNodeId === id) queryNodeId = null;
  rebuildSimulation();
  updateStats();
}

function addNodePrompt() {
  const label = prompt('Node label (word or concept):');
  if (!label) return;
  const trimmed = label.trim().toLowerCase();
  const definition = prompt('Definition (what does "' + trimmed + '" mean?):');
  const newNode = addNode(trimmed);
  if (definition && definition.trim()) {
    newNode._definition = definition.trim();
    // Auto-connect: find existing nodes whose labels appear in the definition
    // or whose definitions share words with this one
    const defWords = new Set(definition.toLowerCase().split(/[^a-zA-Z]+/).filter(w => w.length > 2));
    let connected = 0;
    nodes.forEach(n => {
      if (n === newNode || connected >= 4) return;
      // Connect if the definition mentions an existing node's label
      if (defWords.has(n.label)) {
        addEdge(newNode.id, n.id, 0.4 + Math.random() * 0.3);
        connected++;
        return;
      }
      // Or if the existing node's definition shares words with this one
      const existingDef = getDefinition(n);
      if (existingDef) {
        const existingWords = new Set(existingDef.toLowerCase().split(/[^a-zA-Z]+/).filter(w => w.length > 2));
        let overlap = 0;
        defWords.forEach(w => { if (existingWords.has(w)) overlap++; });
        if (overlap >= 2) {
          addEdge(newNode.id, n.id, 0.2 + overlap * 0.1);
          connected++;
        }
      }
    });
  }
}

let _searchTerm = '';
function searchNode(term) {
  _searchTerm = term.toLowerCase().trim();
  if (!_searchTerm) { nodes.forEach(n => { n._searchMatch = false; }); return; }
  let found = null;
  nodes.forEach(n => {
    n._searchMatch = n.label.toLowerCase().includes(_searchTerm);
    if (n._searchMatch && !found) found = n;
  });
  // Zoom to the first match
  if (found && typeof d3 !== 'undefined') {
    const scale = 1.5;
    const canvas = document.getElementById('graph-canvas');
    const tx = canvas.clientWidth / 2 - found.x * scale;
    const ty = canvas.clientHeight / 2 - found.y * scale;
    zoomTransform = { x: tx, y: ty, k: scale };
    if (zoomBehavior) {
      d3.select(canvas).call(zoomBehavior.transform,
        d3.zoomIdentity.translate(tx, ty).scale(scale));
    }
  }
}

function updateComparison() {
  const selected = nodes.filter(n => n.selected);
  const panel = document.getElementById('compare-panel');
  const content = document.getElementById('compare-content');
  if (selected.length < 2) { panel.style.display = 'none'; return; }
  // Use the first two selected
  const a = selected[0], b = selected[1];
  panel.style.display = 'block';

  function nodeInfo(n) {
    const def = getDefinition(n);
    const conns = edges.filter(e => e.source === n.id || e.target === n.id);
    const neighborIds = new Set();
    conns.forEach(e => {
      if (e.source === n.id) neighborIds.add(e.target);
      if (e.target === n.id) neighborIds.add(e.source);
    });
    const neighbors = nodes.filter(nd => neighborIds.has(nd.id)).map(nd => nd.label);
    return { def: def, connections: conns.length, effect: (n._effect || 0).toFixed(2),
             power: (n._power || 0).toFixed(2), neighbors: neighbors };
  }

  const infoA = nodeInfo(a), infoB = nodeInfo(b);
  // Shared neighbors
  const setA = new Set(infoA.neighbors), setB = new Set(infoB.neighbors);
  const shared = infoA.neighbors.filter(n => setB.has(n));

  function col(n, info) {
    return '<div>' +
      '<div style="font-size:14px;font-weight:bold;color:var(--accent);margin-bottom:6px">' + n.label + '</div>' +
      '<div style="color:var(--text);margin-bottom:6px">' + info.def + '</div>' +
      '<div style="color:var(--dim)">connections: <b style="color:var(--text)">' + info.connections + '</b></div>' +
      '<div style="color:var(--dim)">effect: <b style="color:var(--text)">' + info.effect + '</b></div>' +
      '<div style="color:var(--dim)">power: <b style="color:var(--text)">' + info.power + '</b></div>' +
      '<div style="color:var(--dim);margin-top:4px">neighbors: ' +
        info.neighbors.slice(0, 8).map(function(w) {
          return setA.has(w) && setB.has(w)
            ? '<b style="color:var(--accent2)">' + w + '</b>'
            : '<span>' + w + '</span>';
        }).join(', ') +
        (info.neighbors.length > 8 ? ' +' + (info.neighbors.length - 8) + ' more' : '') +
      '</div>' +
    '</div>';
  }

  content.innerHTML = col(a, infoA) + col(b, infoB);
  if (shared.length > 0) {
    content.innerHTML += '<div style="grid-column:span 2;color:var(--accent2);font-size:10px;margin-top:4px">' +
      '<b>' + shared.length + ' shared neighbors:</b> ' + shared.slice(0, 12).join(', ') +
      (shared.length > 12 ? ' +' + (shared.length - 12) + ' more' : '') + '</div>';
  }
}

function clearComparison() {
  nodes.forEach(n => { n.selected = false; });
  document.getElementById('compare-panel').style.display = 'none';
  draw();
}

function clearGraph() {
  nodes = []; edges = []; nextId = 1; queryNodeId = null;
  if (simulation) simulation.stop();
  updateStats(); draw();
}

function saveGraph() {
  const data = {
    nodes: nodes.map(n => ({
      id: n.id, label: n.label, x: n.x, y: n.y,
      brightness: n.brightness, _definition: n._definition || null,
    })),
    edges: edges.map(e => ({
      source: e.source, target: e.target, weight: e.weight, directed: e.directed,
    })),
    nextId: nextId,
  };
  const json = JSON.stringify(data);
  // Save to localStorage
  try { localStorage.setItem('pep_graph', json); } catch(e) {}
  // Also download as file
  const blob = new Blob([json], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'pep-graph.json';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function loadGraph() {
  // Try localStorage first, then offer file upload
  const stored = localStorage.getItem('pep_graph');
  if (stored) {
    const use = confirm('Found a saved graph in browser storage. Load it?\\n\\nClick Cancel to load from a file instead.');
    if (use) { _applyGraphData(JSON.parse(stored)); return; }
  }
  // File picker
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = '.json';
  input.onchange = function(e) {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function(ev) {
      try {
        const data = JSON.parse(ev.target.result);
        _applyGraphData(data);
      } catch(err) { alert('Could not parse file: ' + err.message); }
    };
    reader.readAsText(file);
  };
  input.click();
}

function _applyGraphData(data) {
  nodes = []; edges = [];
  startBatch();
  (data.nodes || []).forEach(n => {
    const node = addNode(n.label, n.x, n.y);
    node.id = n.id;
    node.brightness = n.brightness || 0.5;
    if (n._definition) node._definition = n._definition;
  });
  nextId = data.nextId || (nodes.length + 1);
  (data.edges || []).forEach(e => {
    addEdge(e.source, e.target, e.weight, e.directed);
  });
  endBatch();
  setTimeout(zoomFit, 300);
}

function updateStats() {
  document.getElementById('graph-stats').textContent =
    nodes.length + ' nodes, ' + edges.length + ' edges';
  computePowerEffect();
  computeRankings();
}

// ═══════════════════════════════════════════════════════════════════════
// Force simulation
// ═══════════════════════════════════════════════════════════════════════
function rebuildSimulation() {
  if (typeof d3 === 'undefined') return;
  if (simulation) simulation.stop();

  // For large graphs (1000+), skip force simulation entirely — it's O(N²)
  // per tick and freezes the browser. The ring layout is already good.
  if (nodes.length > 800) {
    simulation = null;
    return;
  }

  const simEdges = edges.map(e => ({
    source: nodes.find(n => n.id === e.source),
    target: nodes.find(n => n.id === e.target),
    weight: e.weight,
  })).filter(e => e.source && e.target);

  simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(simEdges).strength(e => 0.15 * (e.weight || 0.5)).distance(60))
    .force('charge', d3.forceManyBody().strength(-80).distanceMax(400))
    .force('center', d3.forceCenter(canvas.clientWidth / 2, canvas.clientHeight / 2))
    .force('collide', d3.forceCollide(12))
    .alphaDecay(0.015)
    .on('tick', draw);
}

// ═══════════════════════════════════════════════════════════════════════
// Background stars (subtle field that makes the canvas feel alive)
// ═══════════════════════════════════════════════════════════════════════
const bgStars = Array.from({length: 80}, () => ({
  x: Math.random(), y: Math.random(),
  r: 0.3 + Math.random() * 1.2,
  a: 0.1 + Math.random() * 0.25,
  twinkleSpeed: 0.5 + Math.random() * 2,
}));

// ═══════════════════════════════════════════════════════════════════════
// Particle system (flowing dots along edges during activation spread)
// ═══════════════════════════════════════════════════════════════════════
let particles = [];
function spawnParticles(srcNode, tgtNode, weight) {
  const count = Math.round(3 + weight * 5);
  for (let i = 0; i < count; i++) {
    particles.push({
      sx: srcNode.x, sy: srcNode.y,
      tx: tgtNode.x, ty: tgtNode.y,
      t: -i * 0.12,  // stagger start
      speed: 0.015 + Math.random() * 0.01,
      size: 1 + weight * 2,
      alpha: 0.5 + weight * 0.4,
    });
  }
}
function updateParticles() {
  particles = particles.filter(p => {
    p.t += p.speed;
    return p.t < 1.1;
  });
}

// ═══════════════════════════════════════════════════════════════════════
// Color helpers
// ═══════════════════════════════════════════════════════════════════════
function activationColor(activation) {
  // cold blue → cyan → warm yellow → orange as activation rises
  if (activation < 0.01) return null;
  const t = Math.min(1, activation);
  const r = Math.round(79 + t * 176);   // 79 → 255
  const g = Math.round(195 - t * 12);   // 195 → 183
  const b = Math.round(247 - t * 170);  // 247 → 77
  return {r, g, b};
}

// ═══════════════════════════════════════════════════════════════════════
// Animation loop (replaces static draw)
// ═══════════════════════════════════════════════════════════════════════
let animFrame = 0;
let lastTime = performance.now();

function animate(now) {
  requestAnimationFrame(animate);
  const dt = (now - lastTime) / 1000;
  lastTime = now;
  animFrame++;
  updateParticles();
  draw();
}

function draw() {
  const W = canvas.clientWidth, H = canvas.clientHeight;

  // Background (drawn without transform)
  ctx.fillStyle = _tc.canvasBg;
  ctx.fillRect(0, 0, W, H);

  const time = animFrame * 0.02;
  bgStars.forEach(s => {
    const twinkle = 0.5 + 0.5 * Math.sin(time * s.twinkleSpeed);
    ctx.fillStyle = 'rgba(79,195,247,' + (s.a * twinkle).toFixed(3) + ')';
    ctx.beginPath();
    ctx.arc(s.x * W, s.y * H, s.r, 0, Math.PI * 2);
    ctx.fill();
  });

  // Apply zoom transform for all graph elements
  ctx.save();
  ctx.translate(zoomTransform.x, zoomTransform.y);
  ctx.scale(zoomTransform.k, zoomTransform.k);

  // Edges — for large graphs, build a lookup map once instead of find() per edge
  const nodeMap = {};
  if (nodes.length > 500) { nodes.forEach(n => { nodeMap[n.id] = n; }); }

  edges.forEach(e => {
    const src = nodes.length > 500 ? nodeMap[e.source] : nodes.find(n => n.id === e.source);
    const tgt = nodes.length > 500 ? nodeMap[e.target] : nodes.find(n => n.id === e.target);
    if (!src || !tgt) return;

    // Wireframe edges — visible enough to see the network structure
    const avgAct = ((src.activation || 0) + (tgt.activation || 0)) / 2;
    const edgeAlpha = 0.12 + e.weight * 0.25 + avgAct * 0.5;

    ctx.strokeStyle = 'rgba(79,195,247,' + Math.min(0.8, edgeAlpha).toFixed(3) + ')';
    ctx.lineWidth = 0.5 + e.weight * 1.5 + avgAct * 2;
    ctx.beginPath();
    ctx.moveTo(src.x, src.y);
    ctx.lineTo(tgt.x, tgt.y);
    ctx.stroke();

    // Arrowhead for directed edges
    if (e.directed) {
      const tgtR = 5 + (tgt.brightness || 0.5) * 4 + 4;
      const ddx = tgt.x - src.x, ddy = tgt.y - src.y;
      const dist = Math.sqrt(ddx*ddx + ddy*ddy) || 1;
      const ux = ddx/dist, uy = ddy/dist;
      const tipX = tgt.x - ux * tgtR, tipY = tgt.y - uy * tgtR;
      const arrowSize = 4 + e.weight * 3;
      ctx.fillStyle = ctx.strokeStyle;
      ctx.beginPath();
      ctx.moveTo(tipX, tipY);
      ctx.lineTo(tipX - ux*arrowSize - uy*arrowSize*0.5, tipY - uy*arrowSize + ux*arrowSize*0.5);
      ctx.lineTo(tipX - ux*arrowSize + uy*arrowSize*0.5, tipY - uy*arrowSize - ux*arrowSize*0.5);
      ctx.closePath();
      ctx.fill();
    }

  });

  // Particles flowing along edges
  particles.forEach(p => {
    if (p.t < 0 || p.t > 1) return;
    const x = p.sx + (p.tx - p.sx) * p.t;
    const y = p.sy + (p.ty - p.sy) * p.t;
    const fade = p.t < 0.2 ? p.t / 0.2 : p.t > 0.8 ? (1 - p.t) / 0.2 : 1;
    ctx.fillStyle = 'rgba(255,183,77,' + (p.alpha * fade).toFixed(3) + ')';
    ctx.beginPath();
    ctx.arc(x, y, p.size, 0, Math.PI * 2);
    ctx.fill();
  });

  // Drag-edge preview
  if (dragEdge) {
    const src = nodes.find(n => n.id === dragEdge.from);
    if (src) {
      ctx.strokeStyle = 'rgba(129,199,132,0.5)';
      ctx.lineWidth = 2;
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.moveTo(src.x, src.y);
      ctx.lineTo(dragEdge.x, dragEdge.y);
      ctx.stroke();
      ctx.setLineDash([]);
    }
  }

  // Nodes — fast rendering for 2000+ nodes. No radial gradients (too slow).
  // Simple filled circles with color coding.
  const largeGraph = nodes.length > 500;

  nodes.forEach(n => {
    const baseR = largeGraph ? (1.5 + n.brightness * 1.5) : (2.5 + n.brightness * 2);
    const isHovered = n === hoveredNode;
    const isSpecial = n.selected || n.id === queryNodeId || isHovered;
    const drawR = isSpecial ? baseR + 2 : baseR;

    // Activation glow — simple circle, no gradient
    if (n.activation > 0.05) {
      const ac = activationColor(n.activation);
      if (ac) {
        ctx.fillStyle = 'rgba(' + ac.r + ',' + ac.g + ',' + ac.b + ',' + (n.activation * 0.3).toFixed(3) + ')';
        ctx.beginPath();
        ctx.arc(n.x, n.y, drawR + 6 + n.activation * 10, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    // Core dot
    let coreColor;
    if (n.selected) coreColor = '#81c784';
    else if (n.id === queryNodeId) coreColor = '#ffb74d';
    else if (n.activation > 0.3) {
      const ac = activationColor(n.activation);
      coreColor = ac ? 'rgb(' + ac.r + ',' + ac.g + ',' + ac.b + ')' : '#4fc3f7';
    } else {
      coreColor = isHovered ? '#ffffff' : '#4fc3f7';
    }

    ctx.fillStyle = coreColor;
    ctx.globalAlpha = 0.5 + n.brightness * 0.5;
    ctx.beginPath();
    ctx.arc(n.x, n.y, drawR, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalAlpha = 1;

    // Search highlight ring
    if (n._searchMatch) {
      ctx.strokeStyle = '#ffd54f';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(n.x, n.y, drawR + 4, 0, Math.PI * 2);
      ctx.stroke();
    }

    // Hover ring
    if (isSpecial) {
      ctx.strokeStyle = isHovered ? '#fff' : n.selected ? '#81c784' : '#ffb74d';
      ctx.lineWidth = 1.5 / zoomTransform.k;
      ctx.beginPath();
      ctx.arc(n.x, n.y, drawR + 3, 0, Math.PI * 2);
      ctx.stroke();
    }

    // Label — ONLY on hover
    if (isHovered || n.selected || n.id === queryNodeId) {
      const fontSize = Math.max(8, 10 / Math.sqrt(zoomTransform.k));
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold ' + fontSize + 'px monospace';
      ctx.textAlign = 'center';
      ctx.fillText(n.label, n.x, n.y - drawR - 5);
    }
  });

  ctx.restore();  // pop the zoom transform
}

// Start the animation loop
requestAnimationFrame(animate);

// ═══════════════════════════════════════════════════════════════════════
// Mouse interactions
// ═══════════════════════════════════════════════════════════════════════
function nodeAt(sx, sy) {
  const [x, y] = screenToGraph(sx, sy);
  for (let i = nodes.length - 1; i >= 0; i--) {
    const n = nodes[i];
    const r = (5 + n.brightness * 4) + 4;
    if ((n.x - x) ** 2 + (n.y - y) ** 2 < (r + 4) ** 2) return n;
  }
  return null;
}

function edgeAt(sx, sy) {
  const [x, y] = screenToGraph(sx, sy);
  const threshold = 36 / (zoomTransform.k * zoomTransform.k);
  for (const e of edges) {
    const src = nodes.find(n => n.id === e.source);
    const tgt = nodes.find(n => n.id === e.target);
    if (!src || !tgt) continue;
    const dx = tgt.x - src.x, dy = tgt.y - src.y;
    const len = Math.sqrt(dx*dx + dy*dy) || 1;
    const t = Math.max(0, Math.min(1, ((x - src.x)*dx + (y - src.y)*dy) / (len*len)));
    const px = src.x + t*dx, py = src.y + t*dy;
    if ((px - x)**2 + (py - y)**2 < threshold) return e;
  }
  return null;
}

canvas.addEventListener('mousedown', (ev) => {
  const rect = canvas.getBoundingClientRect();
  const x = ev.clientX - rect.left, y = ev.clientY - rect.top;
  const n = nodeAt(x, y);

  if (ev.shiftKey && n) {
    // Shift+click = toggle selection (for lifecycle + comparison)
    n.selected = !n.selected;
    updateComparison();
    draw();
    return;
  }

  if (n) {
    if (ev.altKey || ev.metaKey) {
      // Alt/Cmd+click = start creating an edge
      dragEdge = {from: n.id, x, y};
    } else {
      // Normal click = drag node + activate (spreading)
      dragging = n;
      activateNode(n.id);
    }
  } else {
    // Clicked on empty space — check for edge
    const e = edgeAt(x, y);
    if (e) {
      const newW = prompt('Edge weight (0.0 - 1.0):', e.weight.toFixed(2));
      if (newW !== null) {
        e.weight = Math.max(0, Math.min(1, parseFloat(newW) || 0.5));
        updateStats();
        draw();
      }
    }
  }
});

canvas.addEventListener('mousemove', (ev) => {
  const rect = canvas.getBoundingClientRect();
  const x = ev.clientX - rect.left, y = ev.clientY - rect.top;
  if (dragging) {
    const [gx, gy] = screenToGraph(x, y);
    dragging.x = gx; dragging.y = gy;
    dragging.fx = gx; dragging.fy = gy;
    if (simulation) simulation.alpha(0.3).restart();
  }
  if (dragEdge) {
    const [gx, gy] = screenToGraph(x, y);
    dragEdge.x = gx; dragEdge.y = gy;
  }
  // Tooltip
  const n = nodeAt(x, y);
  const tip = document.getElementById('tooltip');
  hoveredNode = n;  // track for label rendering
  if (n) {
    const def = getDefinition(n);
    tip.innerHTML =
      '<b style="color:var(--accent);font-size:13px">' + n.label + '</b><br>' +
      '<span style="color:var(--text);line-height:1.5">' + def + '</span><br>' +
      '<span style="color:var(--dim);font-size:9px;margin-top:4px;display:inline-block">' +
      'brightness ' + n.brightness.toFixed(2) +
      ' · effect ' + (n._effect || 0).toFixed(2) +
      ' · power ' + (n._power || 0).toFixed(2) +
      (n.activation > 0.01 ? ' · activation ' + n.activation.toFixed(2) : '') +
      '</span>';
    const wrapRect = canvas.parentElement.getBoundingClientRect();
    tip.style.left = (ev.clientX - wrapRect.left + 14) + 'px';
    tip.style.top = (ev.clientY - wrapRect.top + 14) + 'px';
    tip.classList.add('show');
  } else {
    tip.classList.remove('show');
  }
});

canvas.addEventListener('mouseup', (ev) => {
  if (dragging) {
    delete dragging.fx; delete dragging.fy;
    dragging = null;
  }
  if (dragEdge) {
    const rect = canvas.getBoundingClientRect();
    const x = ev.clientX - rect.left, y = ev.clientY - rect.top;
    const target = nodeAt(x, y);
    if (target && target.id !== dragEdge.from) {
      const w = prompt('Edge weight (0.0 - 1.0):', '0.5');
      addEdge(dragEdge.from, target.id, parseFloat(w) || 0.5);
    }
    dragEdge = null;
    draw();
  }
});

canvas.addEventListener('contextmenu', (ev) => {
  ev.preventDefault();
  const rect = canvas.getBoundingClientRect();
  const n = nodeAt(ev.clientX - rect.left, ev.clientY - rect.top);
  if (n) {
    queryNodeId = n.id;
    computeRankings();
    draw();
  }
});

// ═══════════════════════════════════════════════════════════════════════
// Spreading Activation (Section 2)
// ═══════════════════════════════════════════════════════════════════════
function activateNode(nodeId) {
  resetActivation();
  const decay = parseFloat(document.getElementById('decay-slider').value);
  const maxHops = parseInt(document.getElementById('hops-slider').value);

  const node = nodes.find(n => n.id === nodeId);
  if (!node) return;
  node.activation = 1.0;

  let frontier = [{id: nodeId, activation: 1.0}];
  const visited = new Set([nodeId]);

  let hop = 0;
  function spreadStep() {
    if (hop >= maxHops || frontier.length === 0) {
      document.getElementById('spread-status').textContent =
        'done (' + hop + ' hops, decay=' + decay.toFixed(2) + ')';
      return;
    }
    hop++;
    const next = [];
    frontier.forEach(({id, activation}) => {
      const srcNode = nodes.find(n => n.id === id);
      edges.forEach(e => {
        let neighborId = null;
        if (e.source === id) neighborId = e.target;
        else if (e.target === id) neighborId = e.source;
        if (!neighborId || visited.has(neighborId)) return;
        visited.add(neighborId);
        const contrib = activation * (decay ** hop) * e.weight;
        const neighbor = nodes.find(n => n.id === neighborId);
        if (neighbor) {
          neighbor.activation = Math.max(neighbor.activation, contrib);
          next.push({id: neighborId, activation: contrib});
          // Spawn flowing particles along this edge
          if (srcNode) spawnParticles(srcNode, neighbor, e.weight);
        }
      });
    });
    frontier = next;
    document.getElementById('spread-status').textContent =
      'hop ' + hop + '/' + maxHops + ' (' + next.length + ' nodes lit)';
    setTimeout(spreadStep, 500);
  }
  draw();
  setTimeout(spreadStep, 300);
}

function resetActivation() {
  nodes.forEach(n => n.activation = 0);
  document.getElementById('spread-status').textContent = '';
  draw();
}

document.getElementById('decay-slider').oninput = function() {
  document.getElementById('decay-val').textContent = parseFloat(this.value).toFixed(2);
};
document.getElementById('hops-slider').oninput = function() {
  document.getElementById('hops-val').textContent = this.value;
};

// ═══════════════════════════════════════════════════════════════════════
// Relevance Scoring (Section 3)
// ═══════════════════════════════════════════════════════════════════════
function getWeights() {
  const w = {};
  document.querySelectorAll('#weight-sliders input[type=range]').forEach(sl => {
    const key = sl.dataset.w;
    w[key] = parseFloat(sl.value);
    sl.nextElementSibling.textContent = parseFloat(sl.value).toFixed(2);
  });
  return w;
}

document.querySelectorAll('#weight-sliders input[type=range]').forEach(sl => {
  sl.oninput = () => { getWeights(); computeRankings(); };
});

function computeRankings() {
  if (!queryNodeId) return;
  const w = getWeights();
  const qNode = nodes.find(n => n.id === queryNodeId);
  if (!qNode) return;

  const scored = nodes.filter(n => n.id !== queryNodeId).map(n => {
    // connection: does this node share an edge with the query?
    const edge = edges.find(e =>
      (e.source === queryNodeId && e.target === n.id) ||
      (e.target === queryNodeId && e.source === n.id));
    const connection = edge ? edge.weight : 0;

    // proximity: shortest-path hops (BFS, max 5)
    const proximity = 1 / (1 + shortestPath(queryNodeId, n.id));

    const score =
      w.connection * connection +
      w.brightness * n.brightness +
      w.proximity * proximity +
      w.effect * (n._effect || 0) +
      w.power * (n._power || 0);

    return {node: n, score, connection, proximity};
  });

  scored.sort((a, b) => b.score - a.score);

  const list = document.getElementById('ranking-list');
  list.innerHTML = scored.map((s, i) =>
    '<div class="row">' +
    '<span class="name">' + (i+1) + '. ' + s.node.label + '</span>' +
    '<span class="score">' + s.score.toFixed(3) + '</span>' +
    '</div>'
  ).join('');
}

function shortestPath(fromId, toId) {
  const visited = new Set([fromId]);
  let frontier = [fromId];
  let hops = 0;
  while (frontier.length > 0 && hops < 6) {
    hops++;
    const next = [];
    frontier.forEach(id => {
      edges.forEach(e => {
        let neighbor = null;
        if (e.source === id) neighbor = e.target;
        else if (e.target === id) neighbor = e.source;
        if (neighbor && !visited.has(neighbor)) {
          if (neighbor === toId) return;
          visited.add(neighbor);
          next.push(neighbor);
        }
      });
    });
    if (visited.has(toId)) return hops;
    frontier = next;
  }
  return visited.has(toId) ? hops : 99;
}

// ═══════════════════════════════════════════════════════════════════════
// Power & Effect (Section 4)
// ═══════════════════════════════════════════════════════════════════════
function computePowerEffect() {
  // Effect: sum of edge weights to neighbors
  nodes.forEach(n => {
    let effect = 0;
    edges.forEach(e => {
      if (e.source === n.id || e.target === n.id) {
        effect += e.weight;
      }
    });
    n._effect = effect;
  });

  // Power: sum of (neighbor effect * edge weight) — one-step recursive influence
  nodes.forEach(n => {
    let power = 0;
    edges.forEach(e => {
      let neighborId = null;
      if (e.source === n.id) neighborId = e.target;
      else if (e.target === n.id) neighborId = e.source;
      if (neighborId) {
        const neighbor = nodes.find(nn => nn.id === neighborId);
        if (neighbor) power += (neighbor._effect || 0) * e.weight;
      }
    });
    n._power = power;
  });

  // Render the power ranking
  const sorted = [...nodes].sort((a, b) => (b._power || 0) - (a._power || 0));
  const list = document.getElementById('power-list');
  list.innerHTML = sorted.map((n, i) =>
    '<div class="row">' +
    '<span class="name">' + (i+1) + '. ' + n.label +
    ' <span style="color:var(--dim)">(E=' + (n._effect||0).toFixed(2) +
    ')</span></span>' +
    '<span class="score">P=' + (n._power||0).toFixed(2) + '</span>' +
    '</div>'
  ).join('');
}

// ═══════════════════════════════════════════════════════════════════════
// Idea Lifecycle (Section 5)
// ═══════════════════════════════════════════════════════════════════════
function getSelected() { return nodes.filter(n => n.selected); }

function mergeSelected() {
  const sel = getSelected();
  if (sel.length < 2) { alert('Select 2+ nodes (shift+click) to merge.'); return; }
  const label = prompt('Merged concept name:', sel.map(n => n.label).join('+'));
  if (!label) return;
  const cx = sel.reduce((s, n) => s + n.x, 0) / sel.length;
  const cy = sel.reduce((s, n) => s + n.y, 0) / sel.length;
  const maxB = Math.max(...sel.map(n => n.brightness));
  const merged = addNode(label, cx, cy);
  merged.brightness = Math.min(1, maxB + 0.1);
  // Transfer edges from merged nodes to the new node
  const selIds = new Set(sel.map(n => n.id));
  edges.forEach(e => {
    if (selIds.has(e.source) && !selIds.has(e.target)) addEdge(merged.id, e.target, e.weight);
    if (selIds.has(e.target) && !selIds.has(e.source)) addEdge(merged.id, e.source, e.weight);
  });
  sel.forEach(n => removeNode(n.id));
  document.getElementById('lifecycle-status').textContent = 'merged ' + sel.length + ' nodes into "' + label + '"';
  draw();
}

function splitSelected() {
  const sel = getSelected();
  if (sel.length !== 1) { alert('Select exactly 1 node to split.'); return; }
  const orig = sel[0];
  const name1 = prompt('First sub-concept:', orig.label + ' (part A)');
  if (!name1) return;
  const name2 = prompt('Second sub-concept:', orig.label + ' (part B)');
  if (!name2) return;
  const n1 = addNode(name1, orig.x - 30, orig.y);
  const n2 = addNode(name2, orig.x + 30, orig.y);
  n1.brightness = orig.brightness * 0.8;
  n2.brightness = orig.brightness * 0.8;
  addEdge(n1.id, n2.id, 0.6);
  // Transfer edges
  edges.filter(e => e.source === orig.id || e.target === orig.id).forEach(e => {
    const other = e.source === orig.id ? e.target : e.source;
    if (other !== n1.id && other !== n2.id) {
      addEdge(n1.id, other, e.weight * 0.7);
      addEdge(n2.id, other, e.weight * 0.7);
    }
  });
  removeNode(orig.id);
  document.getElementById('lifecycle-status').textContent = 'split "' + orig.label + '" into "' + name1 + '" and "' + name2 + '"';
  draw();
}

function createNovelNode() {
  // Find the node with the most unbalanced connections (high effect but
  // few edges on one side) — a heuristic for "unfinished edge"
  if (nodes.length < 2) { alert('Need at least 2 nodes.'); return; }
  let best = null, bestScore = -1;
  nodes.forEach(n => {
    const degree = edges.filter(e => e.source === n.id || e.target === n.id).length;
    const score = (n._effect || 0) / Math.max(1, degree);
    if (score > bestScore) { bestScore = score; best = n; }
  });
  if (!best) return;
  const label = prompt(
    'The graph suggests a new concept near "' + best.label + '". Name it:',
    best.label + '-related'
  );
  if (!label) return;
  const nn = addNode(label, best.x + 60, best.y + (Math.random() - 0.5) * 60);
  nn.brightness = 0.4;
  addEdge(nn.id, best.id, 0.5);
  document.getElementById('lifecycle-status').textContent =
    'created "' + label + '" (predicted near "' + best.label + '")';
  draw();
}

function forgetSelected() {
  const sel = getSelected();
  if (sel.length === 0) { alert('Select nodes to forget (shift+click).'); return; }
  // Scatter burst particles from each dying node
  sel.forEach(n => {
    for (let i = 0; i < 12; i++) {
      const angle = (i / 12) * Math.PI * 2 + Math.random() * 0.3;
      const dist = 40 + Math.random() * 60;
      particles.push({
        sx: n.x, sy: n.y,
        tx: n.x + Math.cos(angle) * dist,
        ty: n.y + Math.sin(angle) * dist,
        t: 0, speed: 0.02 + Math.random() * 0.01,
        size: 1.5 + Math.random() * 2,
        alpha: 0.7,
      });
    }
  });
  // Animate fade
  let steps = 0;
  function fadeStep() {
    steps++;
    sel.forEach(n => {
      n.brightness = Math.max(0, n.brightness - 0.12);
      edges.forEach(e => {
        if (e.source === n.id || e.target === n.id) {
          e.weight = Math.max(0, e.weight - 0.12);
        }
      });
    });
    if (steps < 6) {
      setTimeout(fadeStep, 180);
    } else {
      sel.forEach(n => removeNode(n.id));
      document.getElementById('lifecycle-status').textContent =
        'forgot ' + sel.length + ' node(s)';
    }
  }
  fadeStep();
}

// ═══════════════════════════════════════════════════════════════════════
// Preset
// ═══════════════════════════════════════════════════════════════════════
function loadPreset() {
  clearGraph();
  buildConceptNetwork();
  // Auto-fit after the simulation settles
  setTimeout(zoomFit, 2000);
}

function buildConceptNetwork() {
  startBatch();  // disable per-edge updates until everything is built
  // ═════════════════════════════════════════════════════════════════════
  // Concept network — ~2000 common English words in 27 clusters, laid out
  // in a ring. The force simulation pulls connected words together so
  // natural semantic clusters emerge on their own.
  // ═════════════════════════════════════════════════════════════════════

  const clusters = [
    {name:'people', angle:0.0, words:['person','man','woman','child','baby','family','friend','mother','father','brother','sister','neighbor','stranger','crowd','group','boy','girl','elder','youth','husband','wife','daughter','son','uncle','aunt','cousin','grandparent','twin','orphan','hero','villain','teacher','doctor','nurse','soldier','merchant','farmer','priest','judge','thief','beggar','slave','master','servant','warrior','scholar','fool','genius','leader','follower','citizen','immigrant','refugee','ancestor','descendant','widow','bride','groom','partner','rival','ally','enemy','victim','witness','guest','host','passenger','patient','prisoner','volunteer','guardian','orphan','infant','teenager','adult']},
    {name:'body', angle:0.3, words:['hand','eye','head','heart','face','mouth','foot','arm','skin','blood','bone','brain','voice','hair','finger','body','tooth','ear','chest','shoulder','knee','back','neck','stomach','muscle','nerve','breath','lung','tongue','lip','nose','jaw','skull','rib','spine','wrist','ankle','elbow','thumb','palm','fist','vein','organ','cell','tissue','wound','scar','sweat','tear','smile','frown','pulse','heartbeat','reflex','posture','gesture','gaze','blink','yawn','cough','sneeze','shiver','tremble']},
    {name:'nature', angle:0.6, words:['water','sun','earth','tree','fire','air','river','ocean','mountain','stone','flower','leaf','root','seed','forest','grass','sand','wave','island','valley','desert','lake','soil','coral','vine','mushroom','moss','fern','oak','pine','rose','thorn','petal','branch','trunk','bark','cliff','canyon','waterfall','stream','creek','pond','marsh','swamp','glacier','volcano','earthquake','flood','drought','tide','current','reef','jungle','meadow','prairie','tundra','savanna','oasis','geyser','crystal','mineral','fossil','pebble','boulder','mud','clay','ash','lava','erosion']},
    {name:'sky', angle:0.9, words:['sky','star','moon','cloud','rain','wind','snow','storm','thunder','lightning','rainbow','dawn','dusk','shadow','light','dark','fog','frost','horizon','comet','eclipse','meteor','sunrise','sunset','twilight','aurora','constellation','galaxy','nebula','orbit','atmosphere','breeze','gust','tornado','hurricane','blizzard','hail','dew','mist','haze','sleet','drought','humidity','temperature','pressure','climate','weather','season','solstice','equinox','moonlight','starlight','daylight','shade','glow','beam','ray','sparkle','glitter','flash','flicker']},
    {name:'time', angle:1.2, words:['time','day','night','year','morning','evening','hour','moment','past','future','now','season','spring','summer','autumn','winter','age','century','clock','forever','instant','change','begin','end','death','birth','grow','decay','dawn','dusk','midnight','noon','week','month','decade','millennium','era','epoch','history','present','tomorrow','yesterday','soon','late','early','always','never','often','once','twice','daily','annual','eternal','temporary','brief','long','sudden','gradual','rhythm','cycle','deadline','schedule','memory','anniversary','tradition','generation','lifetime','youth','aging','renewal','pause','wait','hurry','delay','rush']},
    {name:'place', angle:1.5, words:['home','city','road','world','land','country','village','door','room','wall','floor','bridge','garden','field','street','tower','church','market','castle','harbor','cave','path','border','corner','center','edge','window','roof','stairs','gate','fence','yard','park','square','alley','tunnel','basement','attic','balcony','porch','hall','corridor','arch','pillar','dome','monument','temple','mosque','palace','cottage','cabin','tent','shelter','barn','warehouse','factory','hospital','school','library','museum','theater','stadium','airport','station','port','dock','pier','lighthouse','fountain','well','mill','mine','quarry','ruin','tomb','grave','cemetery']},
    {name:'communication', angle:1.8, words:['word','speak','story','name','book','write','read','language','letter','sign','message','lie','secret','promise','silence','listen','shout','whisper','argue','explain','translate','grammar','phrase','meaning','symbol','code','text','speech','lecture','debate','conversation','dialogue','monologue','joke','rumor','gossip','news','report','headline','essay','novel','poem','chapter','verse','quote','slang','accent','dialect','tone','volume','pitch','echo','voice','song','chant','prayer','curse','compliment','insult','greeting','farewell','apology','confession','announcement','broadcast','publish','print','type','spell','punctuate','edit','censor','interpret']},
    {name:'mind', angle:2.1, words:['think','know','feel','love','fear','dream','idea','memory','hope','wish','believe','understand','imagine','wonder','doubt','reason','thought','mind','conscious','attention','focus','forget','recall','insight','intuition','curiosity','confusion','logic','wisdom','knowledge','ignorance','genius','madness','sanity','perception','awareness','instinct','habit','obsession','phobia','delusion','hallucination','meditation','concentration','distraction','boredom','interest','fascination','epiphany','revelation','realization','comprehension','misunderstanding','prejudice','bias','assumption','hypothesis','conclusion','decision','judgment','opinion','belief','conviction','skepticism','certainty','ambiguity','paradox','dilemma','puzzle','riddle','mystery','solution','problem']},
    {name:'action', angle:2.4, words:['make','give','take','move','work','play','find','run','walk','stand','sit','hold','break','build','open','close','pull','push','carry','throw','catch','fight','sleep','wake','climb','swim','fly','dig','search','hide','share','choose','create','destroy','lift','drop','pour','fill','empty','cut','tear','fold','bend','stretch','twist','spin','roll','slide','jump','leap','crawl','kneel','bow','wave','point','grab','release','squeeze','shake','stir','mix','scrub','polish','carve','weave','sew','plant','water','prune','harvest','hunt','fish','cook','bake','roast','boil','freeze','melt','burn','explode','collapse','repair','fix']},
    {name:'society', angle:2.7, words:['power','money','king','law','war','peace','freedom','justice','people','leader','army','trade','tax','vote','right','rule','prison','court','government','citizen','revolution','wealth','poverty','class','nation','border','politics','democracy','empire','republic','monarchy','dictatorship','constitution','treaty','alliance','colony','independence','protest','riot','strike','election','campaign','congress','senate','mayor','governor','president','ambassador','diplomat','spy','police','judge','lawyer','jury','trial','verdict','sentence','crime','punishment','fine','pardon','corruption','bribery','propaganda','censorship','reform','policy','budget','debt','inflation','recession','economy','currency','stock','bond','investment','profit','loss','bankruptcy']},
    {name:'food', angle:3.0, words:['food','bread','meat','milk','salt','sugar','fruit','grain','cook','eat','drink','hunger','taste','egg','rice','wine','honey','spice','feast','harvest','farm','apple','cheese','oil','soup','butter','cream','flour','dough','cake','pie','cookie','candy','chocolate','pepper','garlic','onion','tomato','potato','carrot','corn','bean','nut','grape','lemon','orange','banana','peach','cherry','berry','melon','lettuce','spinach','mushroom','olive','tea','coffee','juice','beer','vinegar','sauce','stew','salad','sandwich','toast','cereal','yogurt','bacon','sausage','chicken','beef','pork','lamb','shrimp','lobster','crab','salmon','tuna']},
    {name:'knowledge', angle:3.3, words:['learn','teach','school','question','answer','math','science','number','pattern','test','student','theory','fact','proof','study','logic','experiment','discovery','research','data','measure','calculate','equation','formula','geometry','algebra','infinity','zero','statistics','probability','variable','function','graph','matrix','vector','dimension','symmetry','theorem','axiom','hypothesis','method','analysis','synthesis','abstract','concrete','concept','principle','law','rule','definition','classification','category','species','genus','element','compound','molecule','atom','particle','quantum','wave','frequency','amplitude','velocity','acceleration','gravity','magnetism','electricity','radiation','entropy','evolution','mutation','genetics','chromosome','protein','enzyme','bacteria','virus','cell','organism','ecosystem']},
    {name:'art', angle:3.6, words:['music','song','dance','art','color','paint','draw','beauty','shape','form','rhythm','sound','image','picture','poem','stage','film','craft','sculpture','melody','harmony','design','style','expression','inspire','create','canvas','brush','palette','sketch','portrait','landscape','abstract','gallery','exhibit','museum','performance','concert','opera','ballet','theater','drama','comedy','tragedy','actor','director','writer','composer','musician','singer','drummer','guitar','piano','violin','flute','trumpet','drum','orchestra','choir','lyric','verse','rhyme','metaphor','symbol','mural','mosaic','pottery','ceramic','textile','embroidery','photography','cinema','animation','architecture','calligraphy','graffiti','tattoo','costume','mask']},
    {name:'animal', angle:3.9, words:['animal','dog','cat','bird','horse','cow','sheep','wolf','snake','bear','lion','mouse','deer','eagle','whale','ant','bee','spider','elephant','tiger','fox','rabbit','frog','shark','dolphin','crow','owl','bat','monkey','gorilla','chimpanzee','giraffe','zebra','hippo','rhino','crocodile','turtle','lizard','chameleon','parrot','penguin','flamingo','swan','duck','chicken','rooster','goose','pigeon','sparrow','hawk','falcon','vulture','peacock','butterfly','moth','beetle','dragonfly','mosquito','fly','worm','snail','slug','octopus','squid','jellyfish','starfish','crab','lobster','clam','oyster','coral','salmon','trout','goldfish','ray','eel','seal','walrus','otter','beaver','squirrel','raccoon','skunk','porcupine','moose','elk','buffalo','camel','donkey']},
    {name:'emotion', angle:4.2, words:['joy','anger','sadness','surprise','trust','disgust','shame','pride','guilt','jealousy','courage','patience','kindness','hate','desire','pain','comfort','loneliness','gratitude','empathy','anxiety','calm','wonder','excitement','grief','nostalgia','awe','hope','despair','relief','regret','envy','contempt','admiration','affection','tenderness','passion','lust','devotion','obsession','indifference','apathy','boredom','frustration','irritation','rage','fury','terror','horror','dread','panic','shock','confusion','embarrassment','humiliation','satisfaction','contentment','bliss','ecstasy','serenity','melancholy','sorrow','anguish','heartbreak','betrayal','forgiveness','mercy','compassion','sympathy','pity','respect','reverence','worship','faith','doubt','certainty','confusion']},
    {name:'technology', angle:4.5, words:['machine','tool','wheel','engine','computer','network','system','device','wire','signal','code','data','screen','robot','digital','electric','energy','battery','program','algorithm','model','artificial','intelligence','process','software','hardware','internet','server','database','cloud','encryption','password','virus','firewall','router','bandwidth','pixel','resolution','sensor','chip','circuit','transistor','semiconductor','laser','fiber','satellite','antenna','radar','sonar','drone','rocket','telescope','microscope','lens','camera','microphone','speaker','printer','scanner','keyboard','monitor','processor','memory','storage','download','upload','stream','wireless','bluetooth','GPS','app','website','browser','email','social','media','virtual','reality','simulation','automation','robotics','nanotechnology','biotechnology','blockchain','cryptocurrency']},
    {name:'abstract', angle:4.8, words:['truth','beauty','good','evil','real','possible','nothing','everything','order','chaos','balance','structure','whole','part','cause','effect','relation','meaning','value','purpose','identity','self','other','same','different','constant','infinite','finite','absolute','relative','universal','particular','general','specific','simple','complex','visible','invisible','known','unknown','certain','uncertain','necessary','contingent','actual','potential','essence','existence','being','becoming','substance','form','matter','energy','space','dimension','boundary','limit','freedom','constraint','unity','diversity','harmony','conflict','paradox','contradiction','analogy','metaphor','symbol','sign','pattern','structure','hierarchy','network','flow','resistance','transformation','emergence','entropy','information','signal','noise','symmetry','asymmetry']},
    {name:'clothing', angle:5.1, words:['shirt','pants','dress','shoe','hat','coat','jacket','glove','sock','belt','tie','scarf','skirt','blouse','sweater','vest','robe','gown','uniform','suit','boot','sandal','slipper','heel','lace','button','zipper','pocket','collar','sleeve','hem','fabric','cotton','silk','wool','leather','denim','velvet','linen','nylon','thread','needle','stitch','tailor','fashion','trend','style','accessory','jewelry','ring','necklace','bracelet','earring','crown','mask','veil','apron','cape','shawl','umbrella']},
    {name:'transport', angle:5.4, words:['car','bus','train','plane','ship','boat','bicycle','motorcycle','truck','van','taxi','subway','ferry','helicopter','rocket','wagon','carriage','sled','raft','canoe','kayak','yacht','cruise','engine','wheel','brake','steering','fuel','gasoline','diesel','electric','highway','freeway','intersection','traffic','parking','garage','runway','terminal','platform','track','rail','bridge','tunnel','toll','speed','acceleration','collision','crash','journey','trip','voyage','commute','route','destination','departure','arrival','passport','ticket','luggage','cargo']},
    {name:'material', angle:5.7, words:['wood','metal','glass','plastic','paper','stone','brick','concrete','steel','iron','copper','gold','silver','bronze','aluminum','tin','lead','mercury','diamond','ruby','emerald','sapphire','pearl','ivory','marble','granite','slate','clay','ceramic','porcelain','rubber','foam','wax','glue','paint','ink','dye','oil','gas','liquid','solid','powder','dust','smoke','steam','ice','crystal','fiber','wire','rope','chain','nail','screw','bolt','beam','plank','sheet','tube','pipe','rod','bar']},
    {name:'health', angle:6.0, words:['health','sick','disease','medicine','doctor','nurse','hospital','surgery','wound','pain','fever','cough','infection','virus','bacteria','vaccine','antibiotic','pill','injection','diagnosis','symptom','treatment','cure','recovery','therapy','exercise','diet','nutrition','vitamin','protein','calorie','weight','muscle','bone','blood','heart','lung','kidney','liver','stomach','intestine','nerve','brain','skin','immune','allergy','asthma','diabetes','cancer','stroke','headache','nausea','fatigue','insomnia','stress','anxiety','depression','addiction','disability','blindness','deafness']},
    {name:'sports', angle:0.15, words:['game','team','player','coach','referee','score','goal','point','win','lose','draw','match','tournament','league','champion','trophy','medal','record','athlete','sprint','marathon','relay','hurdle','jump','throw','kick','punch','tackle','dribble','pass','shoot','defend','attack','strategy','tactic','formation','foul','penalty','overtime','halftime','stadium','arena','court','field','track','pool','ring','net','ball','bat','racket','glove','helmet','whistle','clock','timer','crowd','cheer','rival','underdog','comeback','upset','streak','training','practice','warmup','stretch','endurance','stamina','agility','reflex','skill','talent','draft','transfer','retire','legend','rookie','captain','bench','substitute']},
    {name:'weather', angle:0.45, words:['sunny','cloudy','rainy','windy','stormy','calm','clear','overcast','humid','dry','hot','cold','warm','cool','freezing','boiling','mild','harsh','gentle','fierce','tropical','arctic','arid','temperate','monsoon','cyclone','typhoon','drought','flood','wildfire','avalanche','landslide','earthquake','tsunami','eruption','erosion','pollution','smog','ozone','carbon','greenhouse','warming','cooling','forecast','barometer','thermometer','satellite','radar','warning','alert','shelter','evacuate','disaster','emergency','rescue','survive','rebuild','adapt','resilient','vulnerable','exposed','protected']},
    {name:'space', angle:0.75, words:['universe','cosmos','galaxy','star','planet','moon','sun','orbit','gravity','light','space','vacuum','asteroid','comet','meteor','nebula','quasar','pulsar','blackhole','supernova','constellation','satellite','rocket','astronaut','telescope','observatory','launch','mission','rover','probe','station','module','capsule','crater','atmosphere','solar','lunar','martian','alien','extraterrestrial','dimension','wormhole','singularity','expansion','bigbang','darkmatter','darkenergy','radiation','spectrum','wavelength','frequency','redshift','parallax','lightyear','parsec','fusion','fission','plasma','antimatter','particle','photon','neutron','electron','proton','quantum','relativity','spacetime','entropy','infinity','multiverse','simulation','origin','fate','collapse','horizon']},
    {name:'music_detail', angle:1.05, words:['note','chord','scale','key','tempo','beat','measure','rest','sharp','flat','major','minor','octave','pitch','tone','tune','melody','harmony','rhythm','bass','treble','alto','soprano','tenor','baritone','ensemble','solo','duet','trio','quartet','symphony','concerto','sonata','overture','prelude','fugue','waltz','march','blues','jazz','rock','pop','classical','folk','country','rap','hiphop','electronic','reggae','soul','gospel','punk','metal','indie','acoustic','studio','album','single','track','remix','cover','sample','loop','verse','chorus','bridge','hook','riff','groove','improvise','compose','arrange','conduct','perform','record','mix','master','amplify','distort']},
    {name:'geography', angle:1.35, words:['continent','ocean','sea','lake','river','mountain','valley','plain','plateau','peninsula','island','archipelago','cape','bay','gulf','strait','delta','basin','canyon','cliff','coast','shore','beach','reef','glacier','volcano','desert','forest','jungle','tundra','savanna','prairie','steppe','marsh','swamp','oasis','equator','tropic','arctic','antarctic','hemisphere','latitude','longitude','altitude','elevation','terrain','landscape','erosion','sediment','fossil','mineral','ore','soil','clay','sand','gravel','limestone','granite','basalt','quartz','crystal','cave','gorge','waterfall','spring','geyser','hotspring','permafrost','iceberg','fjord','atoll','lagoon','estuary','tributary','watershed','ridge','summit','peak','slope','terrace']},
    {name:'home_life', angle:1.65, words:['kitchen','bedroom','bathroom','living','dining','furniture','table','chair','sofa','bed','desk','shelf','drawer','cabinet','closet','lamp','candle','mirror','curtain','carpet','rug','pillow','blanket','towel','soap','shampoo','toothbrush','comb','razor','laundry','iron','vacuum','broom','mop','bucket','trash','recycle','dish','plate','bowl','cup','glass','fork','knife','spoon','pot','pan','oven','stove','fridge','microwave','toaster','blender','kettle','sink','faucet','drain','pipe','heater','thermostat','switch','outlet','plug','cord','bulb','battery','remote','television','radio','telephone','clock','alarm','key','lock','doorbell','mailbox','garage','driveway','lawn','sprinkler','hose','rake','shovel','hammer','screwdriver','wrench','tape','glue','scissors','string']},
    {name:'mythology', angle:1.95, words:['myth','legend','oracle','prophecy','ritual','sacrifice','temple','altar','idol','curse','blessing','demon','angel','ghost','spirit','phantom','dragon','phoenix','unicorn','griffin','minotaur','centaur','mermaid','werewolf','vampire','zombie','goblin','troll','fairy','elf','dwarf','giant','titan','god','goddess','hero','quest','fate','destiny','doom','underworld','heaven','hell','paradise','purgatory','resurrection','immortal','mortal','sacred','profane','relic','amulet','talisman','enchantment','sorcery','witchcraft','alchemy','potion','spell','incantation','charm','hex','omen','vision','apparition','labyrinth','riddle','sirens','cyclops','chimera','hydra','kraken','cerberus','olympus','valhalla','eden','atlantis','avalon','excalibur','grail','pandora','prometheus','icarus','odyssey','genesis','apocalypse','rapture','karma','reincarnation','nirvana']},
    {name:'work', angle:2.25, words:['job','career','salary','wage','boss','employee','manager','office','meeting','deadline','project','task','skill','resume','interview','promotion','raise','resign','retire','hire','fire','intern','apprentice','mentor','colleague','client','customer','contract','negotiation','profit','revenue','startup','entrepreneur','investor','budget','expense','invoice','receipt','audit','tax','insurance','pension','union','strike','shift','overtime','commute','freelance','consultant','executive','CEO','accountant','engineer','designer','programmer','mechanic','plumber','electrician','carpenter','chef','pilot','surgeon','architect','janitor','receptionist','cashier','waiter','bartender','librarian','journalist','photographer','translator','therapist','veterinarian','pharmacist','dentist','paramedic','firefighter','detective','attorney','professor','researcher','scientist','astronaut']},
    {name:'relationship', angle:2.55, words:['trust','loyalty','betrayal','honesty','deception','bond','connection','intimacy','distance','attraction','rejection','commitment','breakup','divorce','marriage','engagement','romance','flirtation','crush','obsession','jealousy','fidelity','infidelity','forgiveness','resentment','gratitude','respect','disrespect','boundary','compromise','conflict','reconciliation','apology','acceptance','vulnerability','dependence','independence','codependence','attachment','detachment','empathy','neglect','abuse','nurture','support','abandonment','reunion','separation','communication','silence','argument','understanding','misunderstanding','expectation','disappointment','admiration','contempt','affection','indifference','companionship','solitude','belonging','alienation','inheritance','legacy','tradition','generation','ancestry','kinship','adoption','custody','guardian','godparent','soulmate','nemesis','mentor','protege','confidant','acquaintance','stranger','neighbor','community','tribe','clan']},
  ];

  const nodeById = {};

  // Lay out clusters in a grid pattern — each cluster gets a rectangular
  // region, words scattered inside it. Much better than a circle for 2000+ nodes.
  const cols = Math.ceil(Math.sqrt(clusters.length));
  const rows = Math.ceil(clusters.length / cols);
  const cellW = 280, cellH = 220;
  const startX = 50, startY = 50;

  clusters.forEach((cl, ci) => {
    const col = ci % cols;
    const row = Math.floor(ci / cols);
    const regionCx = startX + col * cellW + cellW / 2;
    const regionCy = startY + row * cellH + cellH / 2;
    const n = cl.words.length;

    cl.words.forEach((word, i) => {
      // Scatter within the cluster region
      const angle = (i / n) * Math.PI * 2 + Math.random() * 0.3;
      const r = 20 + Math.random() * Math.min(cellW, cellH) * 0.35;
      const px = regionCx + Math.cos(angle) * r + (Math.random() - 0.5) * 20;
      const py = regionCy + Math.sin(angle) * r + (Math.random() - 0.5) * 20;
      const node = addNode(word, px, py);
      node.brightness = 0.3 + Math.random() * 0.4;
      node._cluster = cl.name;
      nodeById[word] = node;
    });
  });

  // Boost key concept nodes
  ['love','power','time','life','truth','math','mind','dream','freedom','world','beauty','pattern','memory'].forEach(w => {
    if (nodeById[w]) nodeById[w].brightness = 0.85;
  });

  // Intra-cluster edges: circular chain + skip connections + random links.
  // Every node gets at least 3 edges so nothing floats disconnected.
  clusters.forEach(cl => {
    const n = cl.words.length;
    for (let i = 0; i < n; i++) {
      const a = nodeById[cl.words[i]];
      if (!a) continue;
      // Circular chain: connect to next (wraps around)
      const b1 = nodeById[cl.words[(i + 1) % n]];
      if (b1) addEdge(a.id, b1.id, 0.4 + Math.random() * 0.3);
      // Skip-one neighbor (wraps around)
      const b2 = nodeById[cl.words[(i + 2) % n]];
      if (b2) addEdge(a.id, b2.id, 0.25 + Math.random() * 0.25);
      // Two random within cluster for density
      for (let r = 0; r < 2; r++) {
        const ri = Math.floor(Math.random() * n);
        if (ri !== i && ri !== (i+1)%n && ri !== (i+2)%n) {
          const b = nodeById[cl.words[ri]];
          if (b) addEdge(a.id, b.id, 0.15 + Math.random() * 0.3);
        }
      }
    }
  });

  // Safety: ensure every node has at least 2 edges. If any node is under-connected,
  // link it to the nearest other node in the same cluster.
  nodes.forEach(n => {
    const degree = edges.filter(e => e.source === n.id || e.target === n.id).length;
    if (degree < 2 && n._cluster) {
      const sameCluster = nodes.filter(nn => nn._cluster === n._cluster && nn.id !== n.id);
      sameCluster.sort((a, b) => {
        const da = (a.x-n.x)**2 + (a.y-n.y)**2;
        const db = (b.x-n.x)**2 + (b.y-n.y)**2;
        return da - db;
      });
      for (let k = 0; k < Math.min(3, sameCluster.length); k++) {
        addEdge(n.id, sameCluster[k].id, 0.3 + Math.random() * 0.3);
      }
    }
  });

  // Cross-cluster bridges (hand-selected for semantic meaning)
  const bridges = [
    // body ↔ mind/emotion
    ['heart','love',0.9],['heart','feel',0.7],['head','think',0.8],['brain','mind',0.9],
    ['brain','memory',0.8],['eye','see',0.5],['voice','speak',0.8],['pain','body',0.5],
    // people ↔ society
    ['person','power',0.5],['family','home',0.7],['leader','king',0.7],['group','army',0.5],
    ['friend','trust',0.6],['stranger','fear',0.4],['child','school',0.6],['mother','love',0.6],
    // nature ↔ time/sky
    ['sun','day',0.8],['moon','night',0.8],['river','life',0.5],['tree','life',0.5],
    ['flower','beauty',0.6],['seed','grow',0.5],['ocean','wave',0.8],['mountain','earth',0.7],
    // mind ↔ knowledge
    ['think','learn',0.7],['know','truth',0.8],['idea','pattern',0.6],['reason','logic',0.8],
    ['wonder','question',0.6],['believe','truth',0.5],['doubt','question',0.5],['imagine','dream',0.7],
    // mind ↔ emotion
    ['feel','joy',0.7],['feel','anger',0.6],['feel','sadness',0.6],['love','desire',0.6],
    ['fear','courage',0.5],['hope','dream',0.6],['hate','anger',0.7],['trust','friend',0.6],
    // action ↔ various
    ['work','money',0.7],['build','home',0.6],['fight','war',0.7],['run','fear',0.4],
    ['walk','road',0.6],['play','music',0.5],['sleep','dream',0.7],['cook','food',0.8],
    ['write','book',0.8],['read','learn',0.7],['draw','art',0.7],
    // communication ↔ mind
    ['word','think',0.7],['story','life',0.5],['story','memory',0.5],['language','mind',0.5],
    ['book','learn',0.7],['silence','peace',0.5],['secret','truth',0.4],['promise','trust',0.6],
    // society ↔ emotion
    ['freedom','dream',0.5],['justice','truth',0.6],['war','fear',0.6],['peace','comfort',0.5],
    ['prison','fear',0.5],['power','desire',0.4],['money','desire',0.4],
    // food ↔ life
    ['food','life',0.5],['hunger','fear',0.4],['water','life',0.7],['wine','joy',0.3],
    // art ↔ emotion
    ['music','feel',0.6],['beauty','love',0.5],['dance','joy',0.5],['poem','love',0.4],
    ['color','light',0.5],['rhythm','heart',0.4],['sound','voice',0.6],
    // animal ↔ nature
    ['animal','earth',0.5],['bird','sky',0.6],['fish','water',0.7],['wolf','forest',0.5],
    ['eagle','mountain',0.4],['whale','ocean',0.6],['bee','flower',0.6],['dog','home',0.5],
    // sky ↔ emotion
    ['star','dream',0.4],['storm','anger',0.4],['rainbow','hope',0.5],['dawn','hope',0.5],
    ['shadow','fear',0.4],['light','truth',0.5],['dark','fear',0.5],
    // knowledge ↔ power
    ['math','pattern',0.8],['science','truth',0.6],['proof','truth',0.7],
    ['theory','idea',0.6],['experiment','find',0.5],['number','money',0.3],
    // time ↔ life
    ['life','love',0.6],['age','time',0.8],['moment','now',0.9],['past','memory',0.7],
    ['future','hope',0.6],['spring','life',0.5],['winter','death',0.3],
    // meta bridges (the really interesting cross-domain ones)
    ['pattern','beauty',0.4],['math','music',0.4],['fire','power',0.4],
    ['name','person',0.7],['mind','brain',0.9],['story','truth',0.5],
    ['world','people',0.6],['freedom','fight',0.4],['patience','time',0.4],
    // clothing bridges
    ['shirt','body',0.4],['fashion','beauty',0.5],['uniform','soldier',0.6],
    ['crown','king',0.7],['mask','hide',0.5],['silk','luxury',0.3],
    ['thread','needle',0.8],['fabric','weave',0.6],['shoe','walk',0.5],
    // transport bridges
    ['car','road',0.7],['train','track',0.7],['plane','fly',0.7],
    ['ship','ocean',0.6],['bicycle','wheel',0.6],['rocket','space',0.5],
    ['journey','life',0.4],['destination','purpose',0.4],['crash','fear',0.4],
    ['bridge','connect',0.4],['speed','time',0.4],['fuel','energy',0.7],
    // material bridges
    ['gold','money',0.6],['diamond','beauty',0.5],['steel','strong',0.4],
    ['glass','window',0.6],['paper','book',0.6],['wood','tree',0.7],
    ['stone','mountain',0.5],['iron','tool',0.5],['crystal','light',0.4],
    ['ice','cold',0.7],['fire','heat',0.5],['dust','decay',0.4],
    // health bridges
    ['doctor','heal',0.5],['medicine','science',0.5],['pain','body',0.6],
    ['fever','fire',0.3],['exercise','move',0.6],['diet','food',0.7],
    ['stress','anxiety',0.7],['depression','sadness',0.7],['brain','mind',0.9],
    ['heart','love',0.7],['blood','life',0.5],['wound','pain',0.7],
    ['cure','hope',0.5],['virus','fear',0.4],['sleep','rest',0.6],
    // expanded people bridges
    ['hero','courage',0.7],['villain','evil',0.6],['teacher','learn',0.8],
    ['doctor','health',0.8],['soldier','war',0.7],['farmer','harvest',0.7],
    ['judge','justice',0.7],['thief','crime',0.6],['genius','idea',0.6],
    ['slave','freedom',0.5],['warrior','fight',0.7],['scholar','knowledge',0.7],
    // expanded knowledge bridges
    ['gravity','earth',0.6],['evolution','change',0.6],['atom','small',0.4],
    ['cell','life',0.5],['ecosystem','nature',0.6],['probability','chance',0.5],
    ['statistics','data',0.7],['variable','change',0.5],['function','math',0.6],
    ['theorem','proof',0.8],['wavelength','light',0.5],['frequency','sound',0.5],
    // technology bridges
    ['computer','brain',0.5],['network','system',0.7],['algorithm','pattern',0.7],
    ['data','knowledge',0.5],['machine','work',0.5],['signal','message',0.5],
    ['model','idea',0.6],['intelligence','mind',0.7],['code','language',0.5],
    ['energy','power',0.6],['process','think',0.4],['digital','number',0.5],
    ['internet','world',0.4],['robot','machine',0.8],['software','code',0.7],
    ['screen','eye',0.4],['artificial','create',0.4],
    // abstract bridges
    ['order','pattern',0.6],['chaos','storm',0.4],['balance','justice',0.5],
    ['structure','build',0.5],['cause','reason',0.6],['effect','change',0.6],
    ['meaning','word',0.7],['value','money',0.4],['value','truth',0.4],
    ['purpose','life',0.5],['identity','name',0.6],['self','mind',0.6],
    ['whole','part',0.8],['nothing','zero',0.6],['everything','world',0.5],
    ['real','truth',0.6],['possible','dream',0.5],['different','change',0.5],
    // more time bridges
    ['birth','baby',0.8],['death','life',0.7],['grow','child',0.6],
    ['decay','forget',0.5],['begin','create',0.5],['end','death',0.6],
    ['change','move',0.5],['forever','love',0.3],
    // more body bridges
    ['breath','air',0.7],['lung','breath',0.8],['nerve','feel',0.6],
    ['muscle','move',0.6],['stomach','hunger',0.7],['chest','heart',0.7],
    // more place bridges
    ['castle','king',0.6],['harbor','ocean',0.6],['cave','dark',0.5],
    ['window','light',0.5],['border','freedom',0.4],['path','road',0.8],
    ['edge','border',0.5],['center','power',0.4],
    // more people bridges
    ['husband','wife',0.9],['daughter','son',0.8],['youth','child',0.6],
    ['mother','child',0.9],['father','son',0.7],
    // more emotion bridges
    ['loneliness','stranger',0.4],['nostalgia','memory',0.7],['awe','beauty',0.6],
    ['anxiety','future',0.5],['calm','peace',0.7],['grief','death',0.7],
    ['gratitude','give',0.5],['empathy','feel',0.6],['excitement','play',0.4],
    // more knowledge bridges
    ['infinity','forever',0.4],['geometry','shape',0.7],['algebra','equation',0.8],
    ['formula','equation',0.8],['discovery','find',0.7],['research','question',0.6],
    ['measure','number',0.7],['calculate','math',0.7],['zero','nothing',0.7],
  ];

  bridges.forEach(([a, b, w]) => {
    const na = nodeById[a], nb = nodeById[b];
    if (na && nb) addEdge(na.id, nb.id, w);
  });

  endBatch();  // now run simulation + stats once
}

// ═══════════════════════════════════════════════════════════════════════
// Emopic Graph — light up regions of the main graph by emotion/topic
// ═══════════════════════════════════════════════════════════════════════
const EMOPIC_CLUSTERS = {
  fear:     ['emotion', 'mind'],
  joy:      ['emotion', 'art'],
  food:     ['food'],
  music:    ['art'],
  war:      ['society'],
  love:     ['emotion', 'people'],
  nature:   ['nature', 'sky', 'animal'],
  tech:     ['technology'],
  body:     ['body', 'health'],
  science:  ['knowledge'],
  time:     ['time'],
  place:    ['place', 'transport'],
  language: ['communication'],
  abstract: ['abstract'],
};

function emopicGraph(emopic) {
  // Empty selection = reset
  if (!emopic) { resetActivation(); return; }
  // Reset all activations first
  nodes.forEach(n => n.activation = 0);

  const targetClusters = new Set(EMOPIC_CLUSTERS[emopic] || []);
  const activated = [];

  // Light up all nodes in the target clusters
  nodes.forEach(n => {
    if (n._cluster && targetClusters.has(n._cluster)) {
      n.activation = 0.8 + Math.random() * 0.2;
      activated.push(n);
    }
  });

  // Spread to direct neighbors of activated nodes (one hop, weaker)
  const activatedIds = new Set(activated.map(n => n.id));
  activated.forEach(src => {
    edges.forEach(e => {
      let neighborId = null;
      if (e.source === src.id) neighborId = e.target;
      else if (e.target === src.id) neighborId = e.source;
      if (neighborId && !activatedIds.has(neighborId)) {
        const neighbor = nodes.find(nn => nn.id === neighborId);
        if (neighbor && neighbor.activation < 0.3) {
          neighbor.activation = 0.15 + e.weight * 0.2;
        }
      }
    });
  });

  // Spawn particles from a few random activated nodes to their neighbors
  const sample = activated.slice(0, 8);
  sample.forEach(src => {
    edges.forEach(e => {
      let tgt = null;
      if (e.source === src.id) tgt = nodes.find(n => n.id === e.target);
      else if (e.target === src.id) tgt = nodes.find(n => n.id === e.source);
      if (tgt && Math.random() < 0.3) spawnParticles(src, tgt, e.weight);
    });
  });
}

// ═══════════════════════════════════════════════════════════════════════
// Auto-grow (novelty prediction running continuously)
// ═══════════════════════════════════════════════════════════════════════
let growInterval = null;
let growTimerInterval = null;
let growCount = 0;
let growStartTime = null;

function startGrowing() {
  if (growInterval) return;
  document.getElementById('btn-grow').disabled = true;
  document.getElementById('btn-stop-grow').disabled = false;
  document.getElementById('grow-panel').style.display = 'block';
  document.getElementById('grow-list').innerHTML = '';
  growCount = 0;
  growStartTime = Date.now();

  // Timer update
  growTimerInterval = setInterval(() => {
    const elapsed = Math.floor((Date.now() - growStartTime) / 1000);
    const min = Math.floor(elapsed / 60);
    const sec = String(elapsed % 60).padStart(2, '0');
    document.getElementById('grow-timer').textContent = min + ':' + sec;
  }, 1000);

  growInterval = setInterval(growOneNode, 1500);
}

function stopGrowing() {
  if (growInterval) { clearInterval(growInterval); growInterval = null; }
  if (growTimerInterval) { clearInterval(growTimerInterval); growTimerInterval = null; }
  document.getElementById('btn-grow').disabled = false;
  document.getElementById('btn-stop-grow').disabled = true;
}

function growOneNode() {
  if (nodes.length === 0) { stopGrowing(); return; }
  if (nodes.length > 5000) { stopGrowing(); return; }  // safety cap

  // Find a high-pressure node using sampling (avoids O(N*E) scan)
  // Sample up to 50 random nodes and pick the best among them
  const sampleSize = Math.min(50, nodes.length);
  const sampled = [];
  const used = new Set();
  while (sampled.length < sampleSize) {
    const idx = Math.floor(Math.random() * nodes.length);
    if (!used.has(idx)) { used.add(idx); sampled.push(nodes[idx]); }
  }
  let bestNode = null, bestPressure = -1;
  sampled.forEach(n => {
    let degree = 0;
    for (let i = 0; i < edges.length; i++) {
      if (edges[i].source === n.id || edges[i].target === n.id) degree++;
    }
    const effect = n._effect || 0;
    const pressure = effect / Math.max(1, degree * 0.7);
    if (pressure > bestPressure) {
      bestPressure = pressure;
      bestNode = n;
    }
  });

  if (!bestNode) { stopGrowing(); return; }

  // Find the neighbors of the best node to name the new concept
  const neighborIds = new Set();
  edges.forEach(e => {
    if (e.source === bestNode.id) neighborIds.add(e.target);
    if (e.target === bestNode.id) neighborIds.add(e.source);
  });
  const neighbors = nodes.filter(n => neighborIds.has(n.id));

  // Name: blend parent + neighbor into a single portmanteau word (no spaces, no dashes)
  growCount++;
  let newLabel;
  const neighbor = neighbors.length > 0
    ? neighbors[Math.floor(Math.random() * neighbors.length)]
    : null;

  function blendWords(a, b) {
    // Take the first part of a and last part of b to make a portmanteau
    const cutA = Math.max(2, Math.ceil(a.length * 0.55));
    const cutB = Math.max(2, Math.floor(b.length * 0.45));
    return a.slice(0, cutA) + b.slice(b.length - cutB);
  }

  if (neighbor) {
    const a = bestNode.label.toLowerCase().replace(/[^a-z]/g, '');
    const b = neighbor.label.toLowerCase().replace(/[^a-z]/g, '');
    // Several blend strategies, pick one randomly
    const blends = [
      blendWords(a, b),
      blendWords(b, a),
      a.slice(0, Math.ceil(a.length * 0.6)) + b.slice(Math.floor(b.length * 0.5)),
      b.slice(0, 3) + a.slice(1),
    ];
    newLabel = blends[Math.floor(Math.random() * blends.length)];
    // Avoid duplicates
    let attempts = 0;
    while (nodes.find(n => n.label === newLabel) && attempts < 15) {
      newLabel = blends[Math.floor(Math.random() * blends.length)];
      if (attempts > 8) newLabel = newLabel + String.fromCharCode(97 + (growCount % 26));
      attempts++;
    }
  } else {
    newLabel = bestNode.label.toLowerCase().replace(/[^a-z]/g, '') + String.fromCharCode(97 + (growCount % 26));
  }

  // Place near the best node with some offset
  const angle = Math.random() * Math.PI * 2;
  const dist = 40 + Math.random() * 30;
  _batchMode = true;  // avoid expensive updateStats per operation
  const newNode = addNode(newLabel,
    bestNode.x + Math.cos(angle) * dist,
    bestNode.y + Math.sin(angle) * dist,
  );
  newNode.brightness = 0.35 + Math.random() * 0.2;
  newNode.activation = 0.8;  // flash on creation

  // Generate a real definition by synthesizing the parent meanings.
  // Not a meta-description of how it was created — an actual definition
  // of what the concept represents.
  const parentDef = (DEFINITIONS[bestNode.label] || bestNode.label).split(';')[0].split('.')[0];
  let bridgeWord = bestNode.label;
  let bridgeDef = parentDef;
  if (neighbors.length > 0) {
    const rn = neighbors[Math.floor(Math.random() * neighbors.length)];
    bridgeWord = rn.label;
    bridgeDef = (DEFINITIONS[rn.label] || rn.label).split(';')[0].split('.')[0];
  }
  // Synthesize a definition that reads like a real dictionary entry.
  // The word is a blend of parent + neighbor, so the definition should
  // explain it as the meeting point of both meanings.
  const a = bestNode.label, b = bridgeWord;
  const ad = parentDef, bd = bridgeDef;
  // Build a definition that sounds like the hand-written ones:
  // short, concrete, describes what the thing IS.
  // e.g. "the organ of sight" not "vision as it relates to perception"
  const templates = [
    ad + ' that involves ' + b,
    bd + ' directed at ' + a,
    ad + ' caused by ' + b,
    'the ' + b + ' form of ' + ad,
    bd + ' within ' + a,
    'a ' + a + ' that produces ' + bd,
    ad + ' used for ' + b,
    'the result of ' + a + ' meeting ' + b,
    bd + ' specific to ' + a,
    'a response to ' + a + ' involving ' + bd,
    ad + ' during ' + b,
    'the ' + a + ' version of ' + bd,
  ];
  newNode._definition = templates[Math.floor(Math.random() * templates.length)];

  // Connect to the best node + 1-2 random neighbors
  addEdge(newNode.id, bestNode.id, 0.4 + Math.random() * 0.3);
  if (neighbors.length > 0) {
    const rn = neighbors[Math.floor(Math.random() * neighbors.length)];
    addEdge(newNode.id, rn.id, 0.2 + Math.random() * 0.3);
  }
  if (neighbors.length > 1) {
    const rn2 = neighbors[Math.floor(Math.random() * neighbors.length)];
    if (rn2.id !== newNode.id) {
      addEdge(newNode.id, rn2.id, 0.15 + Math.random() * 0.2);
    }
  }

  _batchMode = false;  // re-enable normal mode
  // Just update the stats text cheaply (skip full computePowerEffect)
  document.getElementById('graph-stats').textContent =
    nodes.length + ' nodes, ' + edges.length + ' edges';

  // Spawn particles from the parent to the new node (visual birth effect)
  spawnParticles(bestNode, newNode, 0.8);

  // Fade the activation over a second
  setTimeout(() => { if (newNode) newNode.activation *= 0.3; }, 1000);
  setTimeout(() => { if (newNode) newNode.activation = 0; }, 2000);

  // Update the side panel
  document.getElementById('grow-count').textContent = growCount;
  const list = document.getElementById('grow-list');
  const entry = document.createElement('div');
  entry.style.cssText = 'padding:4px 0;border-bottom:1px solid #222';
  entry.innerHTML =
    '<b style="color:var(--accent)">' + newNode.label + '</b><br>' +
    '<span style="color:var(--dim)">' + getDefinition(newNode) + '</span>';
  list.prepend(entry);  // newest on top
}

// ═══════════════════════════════════════════════════════════════════════
// Vector Space interactive (Vectors & Distance tab)
// ═══════════════════════════════════════════════════════════════════════
const vecCanvas = document.getElementById('vector-canvas');
const vecCtx = vecCanvas ? vecCanvas.getContext('2d') : null;
const vecWords = [
  // concrete + positive (top-right quadrant)
  {label:'dog', x:0.74, y:0.68}, {label:'cat', x:0.70, y:0.62},
  {label:'home', x:0.72, y:0.76}, {label:'flower', x:0.82, y:0.78},
  {label:'bread', x:0.86, y:0.65}, {label:'sun', x:0.90, y:0.82},
  {label:'tree', x:0.84, y:0.58}, {label:'baby', x:0.66, y:0.80},
  {label:'garden', x:0.78, y:0.72}, {label:'cake', x:0.88, y:0.70},
  {label:'puppy', x:0.76, y:0.74}, {label:'rainbow', x:0.80, y:0.85},
  // concrete + negative (bottom-right quadrant)
  {label:'fire', x:0.82, y:0.32}, {label:'stone', x:0.90, y:0.40},
  {label:'war', x:0.74, y:0.10}, {label:'weapon', x:0.80, y:0.16},
  {label:'prison', x:0.72, y:0.24}, {label:'storm', x:0.88, y:0.20},
  {label:'blood', x:0.78, y:0.14}, {label:'snake', x:0.84, y:0.35},
  {label:'crash', x:0.86, y:0.12}, {label:'wound', x:0.76, y:0.28},
  {label:'chain', x:0.70, y:0.18}, {label:'thorn', x:0.92, y:0.30},
  // abstract + positive (top-left quadrant)
  {label:'love', x:0.28, y:0.90}, {label:'joy', x:0.36, y:0.84},
  {label:'beauty', x:0.22, y:0.86}, {label:'hope', x:0.18, y:0.78},
  {label:'peace', x:0.30, y:0.82}, {label:'dream', x:0.20, y:0.74},
  {label:'music', x:0.34, y:0.76}, {label:'truth', x:0.12, y:0.72},
  {label:'freedom', x:0.26, y:0.92}, {label:'courage', x:0.16, y:0.84},
  {label:'wisdom', x:0.10, y:0.80}, {label:'grace', x:0.24, y:0.88},
  // abstract + negative (bottom-left quadrant)
  {label:'fear', x:0.28, y:0.18}, {label:'hate', x:0.34, y:0.10},
  {label:'pain', x:0.38, y:0.22}, {label:'doubt', x:0.20, y:0.30},
  {label:'chaos', x:0.12, y:0.14}, {label:'nothing', x:0.08, y:0.24},
  {label:'death', x:0.24, y:0.08}, {label:'guilt', x:0.30, y:0.26},
  {label:'dread', x:0.16, y:0.12}, {label:'grief', x:0.22, y:0.20},
  {label:'rage', x:0.32, y:0.14}, {label:'despair', x:0.10, y:0.18},
  // center — ambiguous, multi-meaning words (where puns live)
  {label:'power', x:0.46, y:0.36}, {label:'interest', x:0.50, y:0.50},
  {label:'mind', x:0.38, y:0.56}, {label:'change', x:0.56, y:0.44},
  {label:'time', x:0.48, y:0.62}, {label:'light', x:0.58, y:0.66},
  {label:'dark', x:0.44, y:0.30}, {label:'balance', x:0.52, y:0.54},
  {label:'idea', x:0.24, y:0.60}, {label:'memory', x:0.42, y:0.58},
  {label:'silence', x:0.32, y:0.42}, {label:'water', x:0.68, y:0.50},
  {label:'road', x:0.62, y:0.48}, {label:'math', x:0.14, y:0.56},
  {label:'play', x:0.54, y:0.60}, {label:'bank', x:0.60, y:0.42},
  {label:'spring', x:0.56, y:0.56}, {label:'current', x:0.64, y:0.38},
  {label:'wave', x:0.66, y:0.54}, {label:'drive', x:0.58, y:0.36},
  {label:'class', x:0.42, y:0.44}, {label:'match', x:0.48, y:0.40},
  {label:'run', x:0.60, y:0.52}, {label:'scale', x:0.40, y:0.48},
];
let vecSelected = [];

function drawVectorSpace() {
  if (!vecCtx) return;
  const W = 800, H = 400;
  const dpr = window.devicePixelRatio || 1;
  vecCanvas.width = W * dpr; vecCanvas.height = H * dpr;
  vecCanvas.style.width = W + 'px'; vecCanvas.style.height = H + 'px';
  vecCtx.setTransform(dpr, 0, 0, dpr, 0, 0);

  // Margins for axis labels
  const margin = {left: 60, right: 20, top: 20, bottom: 50};
  const plotW = W - margin.left - margin.right;
  const plotH = H - margin.top - margin.bottom;

  vecCtx.fillStyle = _tc.canvasBg;
  vecCtx.fillRect(0, 0, W, H);

  // Plot area background
  vecCtx.fillStyle = _tc.surface;
  vecCtx.fillRect(margin.left, margin.top, plotW, plotH);

  // Grid lines
  vecCtx.strokeStyle = '#1a1a2e'; vecCtx.lineWidth = 0.5;
  for (let i = 0; i <= 10; i++) {
    const gx = margin.left + (i/10) * plotW;
    const gy = margin.top + (i/10) * plotH;
    vecCtx.beginPath(); vecCtx.moveTo(gx, margin.top); vecCtx.lineTo(gx, margin.top + plotH); vecCtx.stroke();
    vecCtx.beginPath(); vecCtx.moveTo(margin.left, gy); vecCtx.lineTo(margin.left + plotW, gy); vecCtx.stroke();
  }

  // Center crosshair (where abstract/concrete and positive/negative meet)
  vecCtx.strokeStyle = '#333'; vecCtx.lineWidth = 1;
  const cx = margin.left + plotW * 0.5, cy = margin.top + plotH * 0.5;
  vecCtx.beginPath(); vecCtx.moveTo(cx, margin.top); vecCtx.lineTo(cx, margin.top + plotH); vecCtx.stroke();
  vecCtx.beginPath(); vecCtx.moveTo(margin.left, cy); vecCtx.lineTo(margin.left + plotW, cy); vecCtx.stroke();

  // X-axis (bottom)
  vecCtx.strokeStyle = '#555'; vecCtx.lineWidth = 1.5;
  vecCtx.beginPath(); vecCtx.moveTo(margin.left, margin.top + plotH); vecCtx.lineTo(margin.left + plotW, margin.top + plotH); vecCtx.stroke();
  // Y-axis (left)
  vecCtx.beginPath(); vecCtx.moveTo(margin.left, margin.top); vecCtx.lineTo(margin.left, margin.top + plotH); vecCtx.stroke();

  // X-axis arrow
  vecCtx.beginPath();
  vecCtx.moveTo(margin.left + plotW, margin.top + plotH);
  vecCtx.lineTo(margin.left + plotW - 8, margin.top + plotH - 4);
  vecCtx.moveTo(margin.left + plotW, margin.top + plotH);
  vecCtx.lineTo(margin.left + plotW - 8, margin.top + plotH + 4);
  vecCtx.stroke();
  // Y-axis arrow
  vecCtx.beginPath();
  vecCtx.moveTo(margin.left, margin.top);
  vecCtx.lineTo(margin.left - 4, margin.top + 8);
  vecCtx.moveTo(margin.left, margin.top);
  vecCtx.lineTo(margin.left + 4, margin.top + 8);
  vecCtx.stroke();

  // X-axis labels
  vecCtx.fillStyle = '#888'; vecCtx.font = '11px monospace'; vecCtx.textAlign = 'center';
  vecCtx.fillText('abstract', margin.left + plotW * 0.15, H - 10);
  vecCtx.fillText('concrete', margin.left + plotW * 0.85, H - 10);
  vecCtx.fillStyle = '#4fc3f7';
  vecCtx.fillText('concrete ←→ abstract', margin.left + plotW * 0.5, H - 10);

  // Y-axis labels
  vecCtx.fillStyle = '#888';
  vecCtx.save(); vecCtx.translate(16, margin.top + plotH * 0.85); vecCtx.rotate(-Math.PI/2);
  vecCtx.fillText('negative', 0, 0); vecCtx.restore();
  vecCtx.save(); vecCtx.translate(16, margin.top + plotH * 0.15); vecCtx.rotate(-Math.PI/2);
  vecCtx.fillText('positive', 0, 0); vecCtx.restore();
  vecCtx.fillStyle = '#81c784';
  vecCtx.save(); vecCtx.translate(16, margin.top + plotH * 0.5); vecCtx.rotate(-Math.PI/2);
  vecCtx.fillText('negative ←→ positive', 0, 0); vecCtx.restore();

  // Tick marks on axes
  vecCtx.fillStyle = '#555'; vecCtx.font = '9px monospace'; vecCtx.textAlign = 'center';
  for (let i = 0; i <= 10; i += 2) {
    const val = (i/10).toFixed(1);
    const gx = margin.left + (i/10) * plotW;
    const gy = margin.top + plotH - (i/10) * plotH;
    // X ticks
    vecCtx.beginPath(); vecCtx.moveTo(gx, margin.top + plotH); vecCtx.lineTo(gx, margin.top + plotH + 5); vecCtx.strokeStyle = '#555'; vecCtx.stroke();
    vecCtx.fillText(val, gx, margin.top + plotH + 16);
    // Y ticks
    vecCtx.beginPath(); vecCtx.moveTo(margin.left - 5, gy); vecCtx.lineTo(margin.left, gy); vecCtx.stroke();
    vecCtx.textAlign = 'right';
    vecCtx.fillText(val, margin.left - 8, gy + 3);
    vecCtx.textAlign = 'center';
  }

  // Helper: convert data coords (0-1) to pixel coords
  function toPixel(dx, dy) {
    return [margin.left + dx * plotW, margin.top + (1 - dy) * plotH];
  }

  // Distance line between selected pair
  if (vecSelected.length === 2) {
    const a = vecSelected[0], b = vecSelected[1];
    const [ax, ay] = toPixel(a.x, a.y);
    const [bx, by] = toPixel(b.x, b.y);
    vecCtx.strokeStyle = 'rgba(255,183,77,0.7)'; vecCtx.lineWidth = 2;
    vecCtx.setLineDash([5,4]);
    vecCtx.beginPath(); vecCtx.moveTo(ax, ay); vecCtx.lineTo(bx, by); vecCtx.stroke();
    vecCtx.setLineDash([]);
    const dist = Math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2);
    vecCtx.fillStyle = '#ffb74d'; vecCtx.font = 'bold 12px monospace';
    vecCtx.textAlign = 'center';
    vecCtx.fillText('d = ' + dist.toFixed(3), (ax+bx)/2, (ay+by)/2 - 10);
  }

  // Words as dots — all labeled so the space isn't empty
  vecWords.forEach(w => {
    const [px, py] = toPixel(w.x, w.y);
    const isSel = vecSelected.includes(w);

    // Glow for selected
    if (isSel) {
      const grad = vecCtx.createRadialGradient(px, py, 2, px, py, 16);
      grad.addColorStop(0, 'rgba(255,183,77,0.5)');
      grad.addColorStop(1, 'rgba(255,183,77,0)');
      vecCtx.fillStyle = grad;
      vecCtx.beginPath(); vecCtx.arc(px, py, 16, 0, Math.PI*2); vecCtx.fill();
    }

    vecCtx.fillStyle = isSel ? '#ffb74d' : '#4fc3f7';
    vecCtx.beginPath(); vecCtx.arc(px, py, isSel ? 5 : 3.5, 0, Math.PI*2); vecCtx.fill();
    vecCtx.fillStyle = isSel ? '#fff' : '#aaa'; vecCtx.font = '9px monospace';
    vecCtx.textAlign = 'center';
    vecCtx.fillText(w.label, px, py - 8);
  });
}

if (vecCanvas) {
  vecCanvas.addEventListener('click', (ev) => {
    const rect = vecCanvas.getBoundingClientRect();
    const mx = (ev.clientX - rect.left) * (800 / rect.width);
    const my = (ev.clientY - rect.top) * (500 / rect.height);
    // Convert mouse pixel to data coords using same margins as draw
    const margin = {left: 60, right: 20, top: 20, bottom: 50};
    const plotW = 800 - margin.left - margin.right;
    const plotH = 500 - margin.top - margin.bottom;
    let closest = null, closestDist = Infinity;
    vecWords.forEach(w => {
      const px = margin.left + w.x * plotW;
      const py = margin.top + (1 - w.y) * plotH;
      const dx = px - mx, dy = py - my;
      const d = Math.sqrt(dx*dx + dy*dy);
      if (d < closestDist && d < 25) { closestDist = d; closest = w; }
    });
    if (closest) {
      if (vecSelected.includes(closest)) {
        vecSelected = vecSelected.filter(w => w !== closest);
      } else {
        vecSelected.push(closest);
        if (vecSelected.length > 2) vecSelected.shift();
      }
    }
    drawVectorSpace();
    if (vecSelected.length === 2) {
      const a = vecSelected[0], b = vecSelected[1];
      const dist = Math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2);
      const dot = a.x*b.x + a.y*b.y;
      const magA = Math.sqrt(a.x*a.x+a.y*a.y), magB = Math.sqrt(b.x*b.x+b.y*b.y);
      const cosine = dot / (magA * magB || 1);
      document.getElementById('vector-info').innerHTML =
        '<b style="color:#ffb74d">' + a.label + '</b> ↔ <b style="color:#ffb74d">' + b.label + '</b>: ' +
        'distance = <b>' + dist.toFixed(3) + '</b>, ' +
        'cosine similarity = <b>' + cosine.toFixed(3) + '</b>';
    } else {
      document.getElementById('vector-info').textContent = 'click two words to compare';
    }
  });
  setTimeout(drawVectorSpace, 100);

  // Populate the "most connected" ranking — rank by how many close neighbors each word has
  const rankList = document.getElementById('vec-rank-list');
  if (rankList) {
    const threshold = 0.25; // distance threshold for "close"
    const scored = vecWords.map(w => {
      let closeCount = 0;
      let totalDist = 0;
      vecWords.forEach(other => {
        if (other === w) return;
        const dx = w.x - other.x, dy = w.y - other.y;
        const dist = Math.sqrt(dx*dx + dy*dy);
        if (dist < threshold) { closeCount++; totalDist += dist; }
      });
      return { label: w.label, close: closeCount, avgDist: closeCount ? totalDist / closeCount : 1 };
    });
    scored.sort((a, b) => b.close - a.close || a.avgDist - b.avgDist);
    rankList.innerHTML = scored.map((s, i) =>
      '<div style="display:flex;justify-content:space-between;padding:2px 0;' +
      'border-bottom:1px solid #222">' +
      '<span style="color:var(--text)">' + (i+1) + '. ' + s.label + '</span>' +
      '<span style="color:var(--accent)">' + s.close + '</span></div>'
    ).join('');
  }
}

// ═══════════════════════════════════════════════════════════════════════
// Bayes Calculator (Prediction & Probability tab)
// ═══════════════════════════════════════════════════════════════════════
function updateBayes() {
  const pa = parseFloat(document.getElementById('bayes-pa').value);
  const pba = parseFloat(document.getElementById('bayes-pba').value);
  const pb = parseFloat(document.getElementById('bayes-pb').value);
  document.getElementById('bayes-pa-val').textContent = pa.toFixed(2);
  document.getElementById('bayes-pba-val').textContent = pba.toFixed(2);
  document.getElementById('bayes-pb-val').textContent = pb.toFixed(2);
  const pab = (pba * pa) / pb;
  const clamped = Math.min(1, Math.max(0, pab));
  document.getElementById('bayes-result').textContent = clamped.toFixed(3);
  document.getElementById('bayes-fill').style.width = (clamped * 100) + '%';
  document.getElementById('bayes-prior-bar').style.width = (pa * 100) + '%';
  document.getElementById('bayes-prior-label').textContent = pa.toFixed(2);
  document.getElementById('bayes-post-label').textContent = clamped.toFixed(2);
  if (pab > 1) {
    document.getElementById('bayes-result').style.color = 'var(--warn)';
  } else {
    document.getElementById('bayes-result').style.color = '#f06292';
  }
  // Verdict: how much did the evidence shift our belief?
  const shift = clamped - pa;
  const verdict = document.getElementById('bayes-verdict');
  if (Math.abs(shift) < 0.05) {
    verdict.textContent = 'The evidence barely changed your belief.';
    verdict.style.color = 'var(--dim)';
  } else if (shift > 0.3) {
    verdict.textContent = 'Strong update — the evidence dramatically increased your belief.';
    verdict.style.color = '#f06292';
  } else if (shift > 0.1) {
    verdict.textContent = 'Moderate update — the evidence meaningfully increased your belief.';
    verdict.style.color = 'var(--accent2)';
  } else if (shift > 0) {
    verdict.textContent = 'Mild update — slightly more likely after seeing the evidence.';
    verdict.style.color = 'var(--accent)';
  } else if (shift < -0.3) {
    verdict.textContent = 'Strong update — the evidence dramatically decreased your belief.';
    verdict.style.color = 'var(--warn)';
  } else {
    verdict.textContent = 'Negative update — the evidence made it less likely.';
    verdict.style.color = 'var(--warn)';
  }
}
['bayes-pa','bayes-pba','bayes-pb'].forEach(id => {
  const el = document.getElementById(id);
  if (el) el.addEventListener('input', updateBayes);
});
setTimeout(updateBayes, 100);

// ═══════════════════════════════════════════════════════════════════════
// Surprise Meter (Prediction & Probability tab)
// ═══════════════════════════════════════════════════════════════════════
// Top 500 English words by frequency rank (based on corpus data).
// Rank 1 = most common. Used to estimate how "surprising" a word is.
const WORD_RANKS = {};
[
  'the','be','to','of','and','a','in','that','have','i','it','for','not','on','with',
  'he','as','you','do','at','this','but','his','by','from','they','we','her','she','or',
  'an','will','my','one','all','would','there','their','what','so','up','out','if','about',
  'who','get','which','go','me','when','make','can','like','time','no','just','him','know',
  'take','people','into','year','your','good','some','could','them','see','other','than',
  'then','now','look','only','come','its','over','think','also','back','after','use','two',
  'how','our','work','first','well','way','even','new','want','because','any','these','give',
  'day','most','us','is','was','are','were','been','being','has','had','did','does','am',
  'say','said','go','went','gone','got','see','saw','seen','come','came','think','thought',
  'tell','told','find','found','give','gave','may','might','must','should','shall','need',
  'man','woman','child','world','life','hand','part','place','case','week','point','fact',
  'group','number','night','room','water','money','story','young','old','home','head','long',
  'body','school','book','eye','word','food','house','door','car','city','tree','name','game',
  'idea','light','run','love','war','fire','power','music','fear','hope','death','king','god',
  'earth','air','mind','heart','blood','dream','pain','truth','art','end','set','own','put',
  'ask','try','call','keep','let','begin','seem','help','show','hear','play','move','live',
  'believe','hold','bring','happen','write','sit','stand','lose','pay','meet','include',
  'continue','learn','change','lead','understand','watch','follow','stop','create','speak',
  'read','allow','add','spend','grow','open','walk','win','offer','remember','consider',
  'appear','buy','wait','serve','die','send','expect','build','stay','fall','cut','reach',
  'kill','remain','suggest','raise','pass','sell','require','report','decide','pull',
  'develop','carry','break','receive','agree','support','hit','produce','eat','cover',
  'catch','draw','choose','cause','wear','quite','probably','already','enough','rather',
  'almost','often','always','never','still','ever','much','more','very','too','here','there',
  'where','why','when','how','what','which','again','once','soon','before','after','while',
  'since','until','between','through','during','against','without','within','along','each',
  'every','both','few','many','several','some','any','no','such','another','other',
  'great','big','small','little','large','high','low','right','left','early','late',
  'important','different','possible','last','next','sure','real','true','best','better',
  'hard','whole','free','full','clear','dark','white','black','red','green','blue',
  'strong','special','happy','kind','able','bad','close','cold','hot','open','short',
  'simple','single','wrong','away','off','back','down','far','fast','together','alone',
  'country','family','person','friend','mother','father','brother','sister','daughter','son',
  'husband','wife','company','government','program','question','problem','system','reason',
  'line','side','area','turn','form','face','order','level','course','position','road',
  'table','court','market','ground','town','morning','today','information','service',
  'sense','experience','interest','business','education','research','girl','boy','baby',
  'music','movie','picture','state','office','church','river','street','field','student',
  'teacher','doctor','paper','law','moment','history','health','month','south','north',
  'east','west','class','cost','age','land','car','bed','wall','window','ball','act',
  'animal','dog','cat','fish','bird','horse','tree','flower','sun','moon','star','rain',
  'snow','wind','sea','lake','mountain','sky','stone','wood','glass','iron','gold','silver',
  'price','horse','ship','boat','brain','memory','thought','soul','spirit','science',
  'nature','energy','force','matter','space','math','circle','square','language','speech',
  'noise','sound','song','voice','color','shape','size','weight','speed','distance',
].forEach(function(w, i) { if (!WORD_RANKS[w]) WORD_RANKS[w] = i + 1; });

let _surpriseTimeout = null;
(function() {
  const input = document.getElementById('surprise-word');
  if (!input) return;

  function lookupWord(w) {
    const bar = document.getElementById('surprise-bar');
    const label = document.getElementById('surprise-label');
    const rankEl = document.getElementById('surprise-rank');
    const defBox = document.getElementById('surprise-def');
    const explain = document.getElementById('surprise-explain');
    const status = document.getElementById('surprise-status');

    if (!w) {
      bar.style.width = '0%';
      label.textContent = '';
      rankEl.textContent = '';
      defBox.style.display = 'none';
      explain.textContent = '';
      status.textContent = '';
      return;
    }

    // Frequency-based surprise (0-100 scale)
    const rank = WORD_RANKS[w];
    let surprise, freqNote;
    if (rank) {
      // Top 500 words: rank 1 = 0% surprise, rank 500 = ~60% surprise
      surprise = Math.min(60, (rank / 500) * 60);
      if (rank <= 20) freqNote = 'extremely common (top 20 in English)';
      else if (rank <= 50) freqNote = 'very common (top 50)';
      else if (rank <= 150) freqNote = 'common (top 150)';
      else if (rank <= 300) freqNote = 'fairly common (top 300)';
      else freqNote = 'moderately common (top 500)';
    } else {
      // Not in top 500 — surprise depends on whether the dictionary knows it
      surprise = 70; // start high, adjust after API call
      freqNote = 'not in the 500 most common words';
    }

    bar.style.width = surprise + '%';
    rankEl.textContent = rank ? 'frequency rank: #' + rank : freqNote;

    if (surprise < 15) {
      label.textContent = 'your brain barely notices this word';
      label.style.color = '#81c784';
    } else if (surprise < 35) {
      label.textContent = 'common — low surprise';
      label.style.color = '#81c784';
    } else if (surprise < 55) {
      label.textContent = 'moderate — some surprise';
      label.style.color = '#ffd54f';
    } else {
      label.textContent = 'uncommon — high surprise';
      label.style.color = '#f06292';
    }

    // Fetch real definition from Free Dictionary API
    status.textContent = 'looking up...';
    defBox.style.display = 'none';

    fetch('https://api.dictionaryapi.dev/api/v2/entries/en/' + encodeURIComponent(w))
      .then(function(r) { return r.ok ? r.json() : Promise.reject(r.status); })
      .then(function(data) {
        status.textContent = '';
        const entry = data[0];
        let html = '<b style="color:var(--accent);font-size:14px">' + entry.word + '</b>';
        if (entry.phonetic) html += ' <span style="color:var(--dim)">' + entry.phonetic + '</span>';
        html += '<br>';
        // Show up to 3 meanings
        const meanings = entry.meanings || [];
        meanings.slice(0, 3).forEach(function(m) {
          html += '<span style="color:#f06292;font-size:10px;font-style:italic">' + m.partOfSpeech + '</span> ';
          const defs = m.definitions || [];
          defs.slice(0, 2).forEach(function(d, i) {
            html += '<span style="color:var(--text)">' + (i + 1) + '. ' + d.definition + '</span>';
            if (d.example) html += ' <span style="color:var(--dim);font-size:10px">"' + d.example + '"</span>';
            html += '<br>';
          });
        });
        defBox.innerHTML = html;
        defBox.style.display = 'block';

        // If it is a real but uncommon word, bump surprise higher
        if (!rank) {
          // Check if it has many meanings (more meanings = more common in practice)
          const totalDefs = meanings.reduce(function(s, m) { return s + (m.definitions||[]).length; }, 0);
          if (totalDefs > 4) { surprise = 55; freqNote = 'real word, used in several contexts'; }
          else if (totalDefs > 2) { surprise = 65; freqNote = 'real word, moderately specialized'; }
          else { surprise = 78; freqNote = 'real but uncommon word'; }
          bar.style.width = surprise + '%';
          rankEl.textContent = freqNote;
          label.textContent = surprise > 70 ? 'uncommon — high surprise' : 'not everyday — notable';
          label.style.color = surprise > 70 ? '#f06292' : '#ffd54f';
        }

        // PEP explanation
        if (surprise < 25) {
          explain.textContent = 'PEP would compress this — "' + w + '" is so predictable that it carries almost no new information. Your brain processes it automatically.';
        } else if (surprise < 50) {
          explain.textContent = 'PEP would note this — "' + w + '" carries moderate information. Common enough to expect, but specific enough to matter in context.';
        } else if (surprise < 70) {
          explain.textContent = 'PEP would store this — "' + w + '" is specific enough to be meaningful. When something is this uncommon, it often signals a topic shift or new idea.';
        } else {
          explain.textContent = 'PEP would flag this as novel — "' + w + '" is rare enough that encountering it is genuinely surprising. High surprise = high information = worth remembering.';
        }
      })
      .catch(function(err) {
        status.textContent = '';
        if (err === 404) {
          defBox.innerHTML = '<span style="color:var(--warn)">Not found in dictionary.</span> This could be a typo, a very specialized term, or a made-up word.';
          defBox.style.display = 'block';
          bar.style.width = '95%';
          label.textContent = 'unknown word — maximum surprise';
          label.style.color = '#f06292';
          rankEl.textContent = 'not in any standard dictionary';
          explain.textContent = 'PEP would absolutely store this — if a word is not even in the dictionary, encountering it is maximally surprising. This is how new concepts enter the network.';
        } else {
          status.textContent = 'could not reach dictionary (offline?)';
        }
      });
  }

  input.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
      const w = this.value.trim().toLowerCase().replace(/[^a-z]/g, '');
      lookupWord(w);
    }
  });
  // Also trigger after a pause in typing
  input.addEventListener('input', function() {
    clearTimeout(_surpriseTimeout);
    const w = this.value.trim().toLowerCase().replace(/[^a-z]/g, '');
    if (!w) { lookupWord(''); return; }
    _surpriseTimeout = setTimeout(function() { lookupWord(w); }, 800);
  });
})();

// ═══════════════════════════════════════════════════════════════════════
// Flow Network (Flow & Optimization tab)
// ═══════════════════════════════════════════════════════════════════════
const flowCanvas = document.getElementById('flow-canvas');
const flowCtx = flowCanvas ? flowCanvas.getContext('2d') : null;
let flowParticles = [];
let flowConstructive = 0, flowDissipated = 0;

// Define a branching pipe network
const flowPipes = [
  {x1:0.05,y1:0.5, x2:0.25,y2:0.5, width:20, label:'input'},
  {x1:0.25,y1:0.5, x2:0.45,y2:0.25, width:14, label:'branch A'},
  {x1:0.25,y1:0.5, x2:0.45,y2:0.75, width:8, label:'branch B'},
  {x1:0.45,y1:0.25, x2:0.65,y2:0.25, width:14, label:'main path'},
  {x1:0.45,y1:0.75, x2:0.65,y2:0.75, width:4, label:'narrow'},
  {x1:0.65,y1:0.25, x2:0.85,y2:0.5, width:12, label:'merge'},
  {x1:0.65,y1:0.75, x2:0.85,y2:0.5, width:4, label:'trickle'},
  {x1:0.85,y1:0.5, x2:0.97,y2:0.5, width:16, label:'output'},
];

function spawnFlowParticle() {
  flowParticles.push({
    pipe: 0, t: 0, speed: 0.008 + Math.random()*0.004,
    size: 2, alive: true, path: [0],
  });
}

function updateFlow() {
  // Spawn new particles
  if (Math.random() < 0.15) spawnFlowParticle();

  flowParticles.forEach(p => {
    if (!p.alive) return;
    p.t += p.speed;
    if (p.t >= 1) {
      const pipe = flowPipes[p.pipe];
      // Find next pipe(s) starting from this pipe's end
      const nextPipes = [];
      flowPipes.forEach((fp, i) => {
        if (i !== p.pipe && Math.abs(fp.x1 - pipe.x2) < 0.02 && Math.abs(fp.y1 - pipe.y2) < 0.02) {
          nextPipes.push(i);
        }
      });
      if (nextPipes.length > 0) {
        // Choose randomly weighted by pipe width
        const totalW = nextPipes.reduce((s, i) => s + flowPipes[i].width, 0);
        let r = Math.random() * totalW;
        for (const i of nextPipes) {
          r -= flowPipes[i].width;
          if (r <= 0) { p.pipe = i; p.t = 0; p.path.push(i); break; }
        }
      } else {
        // Reached the end
        p.alive = false;
        // Was it the wide path or narrow path?
        if (p.path.includes(1) || p.path.includes(3)) {
          flowConstructive++;
        } else {
          flowDissipated++;
        }
      }
    }
  });
  flowParticles = flowParticles.filter(p => p.alive);
}

function drawFlow() {
  if (!flowCtx) return;
  const W = 800, H = 300;
  const dpr = window.devicePixelRatio || 1;
  flowCanvas.width = W * dpr; flowCanvas.height = H * dpr;
  flowCanvas.style.width = W + 'px'; flowCanvas.style.height = H + 'px';
  flowCtx.setTransform(dpr, 0, 0, dpr, 0, 0);

  flowCtx.fillStyle = _tc.canvasBg;
  flowCtx.fillRect(0, 0, W, H);

  // Draw pipes
  flowPipes.forEach(pipe => {
    flowCtx.strokeStyle = 'rgba(79,195,247,0.3)';
    flowCtx.lineWidth = pipe.width;
    flowCtx.lineCap = 'round';
    flowCtx.beginPath();
    flowCtx.moveTo(pipe.x1*W, pipe.y1*H);
    flowCtx.lineTo(pipe.x2*W, pipe.y2*H);
    flowCtx.stroke();
  });

  // Draw particles
  flowParticles.forEach(p => {
    if (!p.alive || p.t < 0) return;
    const pipe = flowPipes[p.pipe];
    const x = pipe.x1 + (pipe.x2 - pipe.x1) * p.t;
    const y = pipe.y1 + (pipe.y2 - pipe.y1) * p.t;
    const isWide = pipe.width > 8;
    flowCtx.fillStyle = isWide ? 'rgba(129,199,132,0.8)' : 'rgba(255,183,77,0.6)';
    flowCtx.beginPath();
    flowCtx.arc(x*W, y*H, p.size + (isWide ? 1 : 0), 0, Math.PI*2);
    flowCtx.fill();
  });

  // Labels
  flowCtx.fillStyle = '#555'; flowCtx.font = '9px monospace'; flowCtx.textAlign = 'center';
  flowCtx.fillText('source', 0.05*W, 0.5*H - 18);
  flowCtx.fillText('wide path', 0.55*W, 0.25*H - 14);
  flowCtx.fillText('narrow path', 0.55*W, 0.75*H + 18);
  flowCtx.fillText('output', 0.95*W, 0.5*H - 18);

  // Update PTO stats
  const total = flowConstructive + flowDissipated || 1;
  document.getElementById('pto-ratio').textContent =
    (flowConstructive / total).toFixed(2);
  document.getElementById('pto-construct').textContent = flowConstructive;
  document.getElementById('pto-dissipate').textContent = flowDissipated;
}

// Flow animation loop
if (flowCanvas) {
  setInterval(() => { updateFlow(); drawFlow(); }, 50);
}

// ═══════════════════════════════════════════════════════════════════════
// Emopic Spotlight interactive (Emopics tab)
// ═══════════════════════════════════════════════════════════════════════
const emopicNodes = [
  {label:'danger',x:80,y:60,groups:['fear','war']},
  {label:'escape',x:130,y:40,groups:['fear']},
  {label:'dark',x:60,y:100,groups:['fear']},
  {label:'scream',x:110,y:90,groups:['fear']},
  {label:'laugh',x:300,y:50,groups:['joy','love']},
  {label:'smile',x:340,y:80,groups:['joy']},
  {label:'play',x:270,y:70,groups:['joy','music']},
  {label:'celebrate',x:320,y:110,groups:['joy','food']},
  {label:'bread',x:500,y:60,groups:['food']},
  {label:'taste',x:540,y:90,groups:['food']},
  {label:'cook',x:480,y:100,groups:['food']},
  {label:'hunger',x:520,y:40,groups:['food','fear']},
  {label:'song',x:180,y:200,groups:['music','love']},
  {label:'rhythm',x:220,y:230,groups:['music']},
  {label:'melody',x:160,y:240,groups:['music']},
  {label:'dance',x:200,y:180,groups:['music','joy']},
  {label:'battle',x:650,y:60,groups:['war']},
  {label:'soldier',x:690,y:90,groups:['war']},
  {label:'weapon',x:670,y:130,groups:['war','fear']},
  {label:'peace',x:620,y:100,groups:['war','love']},
  {label:'heart',x:400,y:200,groups:['love']},
  {label:'kiss',x:430,y:230,groups:['love']},
  {label:'together',x:370,y:220,groups:['love','joy']},
  {label:'tender',x:410,y:250,groups:['love','music']},
  {label:'discover',x:560,y:200,groups:['science']},
  {label:'theory',x:600,y:230,groups:['science']},
  {label:'proof',x:580,y:260,groups:['science']},
  {label:'question',x:540,y:240,groups:['science','fear']},
  {label:'memory',x:350,y:160,groups:['love','fear','science']},
  {label:'think',x:400,y:140,groups:['science','fear']},
];

const emopicEdges = [
  [0,1],[0,2],[0,3],[1,3],
  [4,5],[4,6],[5,7],[6,7],
  [8,9],[8,10],[9,10],[8,11],
  [12,13],[12,14],[13,15],[12,15],
  [16,17],[17,18],[16,19],[18,19],
  [20,21],[20,22],[21,23],[22,23],
  [24,25],[25,26],[24,27],[26,27],
  [28,20],[28,0],[28,24],[29,28],[29,27],[29,0],
  [11,0],[15,6],[19,20],[7,10],[12,20],
];

const emopicColors = {
  fear:'#e53935', joy:'#43a047', food:'#ff8f00',
  music:'#8e24aa', war:'#455a64', love:'#d81b60', science:'#00897b',
};
let activeEmopic = null;

function emopicActivate(group) { activeEmopic = group; drawEmopic(); }
function emopicReset() { activeEmopic = null; drawEmopic(); }

function drawEmopic() {
  const c = document.getElementById('emopic-canvas');
  if (!c) return;
  const ctx2 = c.getContext('2d');
  // Use fixed dimensions — clientWidth is 0 when tab is hidden
  const W = 800, H = 320;
  c.width = W; c.height = H;

  ctx2.fillStyle = _tc.canvasBg;
  ctx2.fillRect(0, 0, W, H);

  // Edges
  emopicEdges.forEach(([ai, bi]) => {
    const a = emopicNodes[ai], b = emopicNodes[bi];
    const aLit = activeEmopic && a.groups.includes(activeEmopic);
    const bLit = activeEmopic && b.groups.includes(activeEmopic);
    const lit = aLit && bLit;
    ctx2.strokeStyle = lit ? 'rgba(255,255,255,0.3)' : 'rgba(79,195,247,0.08)';
    ctx2.lineWidth = lit ? 1.5 : 0.5;
    ctx2.beginPath(); ctx2.moveTo(a.x, a.y); ctx2.lineTo(b.x, b.y); ctx2.stroke();
  });

  // Nodes
  emopicNodes.forEach(n => {
    const isLit = activeEmopic && n.groups.includes(activeEmopic);
    const color = isLit ? (emopicColors[activeEmopic] || '#fff') : '#4fc3f7';
    const r = isLit ? 6 : 3;
    const alpha = isLit ? 1.0 : 0.25;

    if (isLit) {
      const grad = ctx2.createRadialGradient(n.x, n.y, r*0.3, n.x, n.y, r+12);
      grad.addColorStop(0, color + 'cc');
      grad.addColorStop(1, color + '00');
      ctx2.fillStyle = grad;
      ctx2.beginPath(); ctx2.arc(n.x, n.y, r+12, 0, Math.PI*2); ctx2.fill();
    }

    ctx2.fillStyle = color;
    ctx2.globalAlpha = alpha;
    ctx2.beginPath(); ctx2.arc(n.x, n.y, r, 0, Math.PI*2); ctx2.fill();
    ctx2.globalAlpha = 1;

    if (isLit) {
      ctx2.fillStyle = '#fff';
      ctx2.font = '10px monospace';
      ctx2.textAlign = 'center';
      ctx2.fillText(n.label, n.x, n.y - r - 6);
    }
  });

  // Label the active emopic
  if (activeEmopic) {
    ctx2.fillStyle = emopicColors[activeEmopic] || '#fff';
    ctx2.font = 'bold 14px monospace';
    ctx2.textAlign = 'left';
    ctx2.fillText(activeEmopic.toUpperCase(), 15, 25);
    const litCount = emopicNodes.filter(n => n.groups.includes(activeEmopic)).length;
    ctx2.font = '10px monospace';
    ctx2.fillStyle = '#888';
    ctx2.fillText(litCount + ' nodes activated', 15, 40);
  }
}

// Start with the preset loaded
loadPreset();
// Auto-fit after a moment so the full graph is visible
setTimeout(zoomFit, 500);
// Dismiss loading overlay
setTimeout(() => {
  const overlay = document.getElementById('loading-overlay');
  if (overlay) { overlay.classList.add('done'); setTimeout(() => overlay.remove(), 600); }
}, 800);

// ═══════════════════════════════════════════════════════════════════════
// Keyboard shortcuts
// ═══════════════════════════════════════════════════════════════════════
document.addEventListener('keydown', (e) => {
  // Don't trigger when typing in an input
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
  if (e.key === 'Escape') { clearComparison(); resetActivation(); }
  if (e.key === '/' || e.key === 'f' && !e.metaKey && !e.ctrlKey) {
    e.preventDefault();
    document.getElementById('node-search').focus();
  }
  if (e.key === 'g' || e.key === 'G') {
    if (growInterval) stopGrowing(); else startGrowing();
  }
});

// ═══════════════════════════════════════════════════════════════════════
// Guided Tour
// ═══════════════════════════════════════════════════════════════════════
const TOUR_STEPS = [
  {
    target: '#graph-canvas',
    title: 'The Concept Network',
    text: 'This is a graph of 2000+ English words connected by meaning. Each dot is a word. Each line is a relationship. Hover over any node to see its definition.',
    tab: 'network-tab',
  },
  {
    target: '#node-search',
    title: 'Search',
    text: 'Type any word here to find it in the network. Matching nodes light up yellow and the view zooms to the first match.',
    tab: 'network-tab',
  },
  {
    target: '#btn-grow',
    title: 'Watch It Grow',
    text: 'Click "Start growing" and the network will create brand new words by blending existing concepts. Each new word gets a name, a definition, and connections — this is novelty prediction in action.',
    tab: 'network-tab',
  },
  {
    target: '#emopic-select',
    title: 'Emopics',
    text: 'Select an emotion or topic here to see how it changes which nodes are activated. "Fear" lights up threat-related words. "Food" lights up taste and hunger. This is how context shapes retrieval.',
    tab: 'network-tab',
  },
  {
    target: '[data-section="vectors-tab"]',
    title: 'Vectors & Distance',
    text: 'This tab shows how words live in a mathematical space. Click two words to see the cosine similarity between them. Close words = similar meaning.',
    tab: 'vectors-tab',
  },
  {
    target: '[data-section="prediction-tab"]',
    title: 'Prediction & Probability',
    text: 'Play with Bayes\\'s theorem using sliders, and type any word into the Surprise Meter to see its real dictionary definition and how predictable it is. Common words = low surprise. Rare words = high surprise.',
    tab: 'prediction-tab',
  },
  {
    target: '[data-section="emotion-tab"]',
    title: 'Emopics',
    text: 'Topics trigger emotions — the actual endogenous compounds in your brain. This tab explains how emotion and topic together determine what gets stored and what gets forgotten.',
    tab: 'emotion-tab',
  },
  {
    target: '[data-section="flow-tab"]',
    title: 'Flow & Optimization',
    text: 'Watch information flow through channels. Wide channels = efficient. Narrow channels = waste. This visualizes the PTO principle: maximize constructive transformation, minimize dissipation.',
    tab: 'flow-tab',
  },
];

let tourStep = -1;
const tourOverlay = document.createElement('div');
tourOverlay.id = 'tour-overlay';
document.body.appendChild(tourOverlay);

const tourHighlight = document.createElement('div');
tourHighlight.id = 'tour-highlight';
document.body.appendChild(tourHighlight);

const tourBox = document.createElement('div');
tourBox.id = 'tour-box';
tourBox.style.display = 'none';
document.body.appendChild(tourBox);

tourOverlay.addEventListener('click', endTour);

function startTour() {
  tourStep = -1;
  tourOverlay.classList.add('active');
  nextTourStep();
}

function endTour() {
  tourOverlay.classList.remove('active');
  tourBox.style.display = 'none';
  tourHighlight.style.display = 'none';
  tourStep = -1;
}

function nextTourStep() {
  tourStep++;
  if (tourStep >= TOUR_STEPS.length) { endTour(); return; }
  showTourStep(TOUR_STEPS[tourStep]);
}

function prevTourStep() {
  tourStep = Math.max(0, tourStep - 1);
  showTourStep(TOUR_STEPS[tourStep]);
}

function showTourStep(step) {
  // Switch to the right tab if needed
  if (step.tab) {
    const tabEl = document.querySelector('[data-section="' + step.tab + '"]');
    if (tabEl) tabEl.click();
  }

  setTimeout(() => {
    const el = document.querySelector(step.target);
    if (!el) { nextTourStep(); return; }

    const rect = el.getBoundingClientRect();
    const pad = 6;

    // Position highlight
    tourHighlight.style.display = 'block';
    tourHighlight.style.left = (rect.left - pad) + 'px';
    tourHighlight.style.top = (rect.top - pad) + 'px';
    tourHighlight.style.width = (rect.width + pad * 2) + 'px';
    tourHighlight.style.height = (rect.height + pad * 2) + 'px';

    // Position tour box
    tourBox.style.display = 'block';
    let boxTop = rect.bottom + 16;
    let boxLeft = Math.max(16, rect.left);
    // If it would go off-screen bottom, put it above
    if (boxTop + 200 > window.innerHeight) {
      boxTop = Math.max(16, rect.top - 200);
    }
    if (boxLeft + 360 > window.innerWidth) {
      boxLeft = window.innerWidth - 376;
    }
    tourBox.style.top = boxTop + 'px';
    tourBox.style.left = boxLeft + 'px';

    tourBox.innerHTML =
      '<div class="tour-step">Step ' + (tourStep + 1) + ' of ' + TOUR_STEPS.length + '</div>' +
      '<div class="tour-title">' + step.title + '</div>' +
      '<div>' + step.text + '</div>' +
      '<div class="tour-btns">' +
        (tourStep > 0 ? '<button onclick="prevTourStep()">Back</button>' : '') +
        (tourStep < TOUR_STEPS.length - 1
          ? '<button class="primary" onclick="nextTourStep()">Next</button>'
          : '<button class="primary" onclick="endTour()">Finish</button>') +
        '<button onclick="endTour()">Skip</button>' +
      '</div>';
  }, 200);
}

// ═══════════════════════════════════════════════════════════════════════
// Application card mini-demos
// ═══════════════════════════════════════════════════════════════════════
(function() {
  function miniGraph(canvasId, wordPairs, color) {
    const c = document.getElementById(canvasId);
    if (!c) return;
    const ctx = c.getContext('2d');
    const W = c.width, H = c.height;
    const pts = wordPairs.map((w, i) => ({
      label: w, x: 30 + (i % 5) * (W - 60) / 4, y: 20 + Math.floor(i / 5) * 40,
      vx: (Math.random() - 0.5) * 0.3, vy: (Math.random() - 0.5) * 0.3,
    }));
    const links = [];
    for (let i = 0; i < pts.length; i++) {
      for (let j = i + 1; j < pts.length; j++) {
        if (Math.random() < 0.35) links.push([i, j]);
      }
    }
    let frame = 0;
    function draw() {
      frame++;
      ctx.fillStyle = _tc.surface;
      ctx.fillRect(0, 0, W, H);
      // Animate nodes gently
      pts.forEach(p => {
        p.x += p.vx; p.y += p.vy;
        if (p.x < 20 || p.x > W - 20) p.vx *= -1;
        if (p.y < 12 || p.y > H - 12) p.vy *= -1;
      });
      // Edges
      links.forEach(([i, j]) => {
        ctx.strokeStyle = color + '33';
        ctx.lineWidth = 0.5;
        ctx.beginPath();
        ctx.moveTo(pts[i].x, pts[i].y);
        ctx.lineTo(pts[j].x, pts[j].y);
        ctx.stroke();
      });
      // Nodes
      pts.forEach((p, i) => {
        const pulse = 0.5 + 0.5 * Math.sin(frame * 0.03 + i);
        ctx.fillStyle = color;
        ctx.globalAlpha = 0.4 + pulse * 0.4;
        ctx.beginPath();
        ctx.arc(p.x, p.y, 3, 0, Math.PI * 2);
        ctx.fill();
        ctx.globalAlpha = 0.6;
        ctx.font = '8px monospace';
        ctx.fillText(p.label, p.x + 5, p.y + 3);
        ctx.globalAlpha = 1;
      });
      if (animating) requestAnimationFrame(draw);
    }
    let animating = false;
    const observer = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && !animating) { animating = true; draw(); }
      else if (!entries[0].isIntersecting) { animating = false; }
    }, { threshold: 0.1 });
    observer.observe(c);
  }

  miniGraph('app-lang-canvas',
    ['hello','hola','bonjour','ciao','hallo','ola','merhaba','salut','ahoj','hej'],
    '#4fc3f7');
  miniGraph('app-match-canvas',
    ['aggro','patient','fast','strategic','clutch','tilt','sniper','rusher','support','flex'],
    '#81c784');
  miniGraph('app-data-canvas',
    ['query','index','cluster','rank','weight','embed','retrieve','link','score','filter'],
    '#ffb74d');
  miniGraph('app-brain-canvas',
    ['neuron','synapse','cortex','memory','recall','decay','encode','prime','inhibit','fire'],
    '#ba68c8');
  miniGraph('app-market-canvas',
    ['signal','momentum','volume','spread','hedge','sector','trend','spike','dip','flow'],
    '#f06292');
})();

// ═══════════════════════════════════════════════════════════════════════
// Theme toggle (dark/light)
// ═══════════════════════════════════════════════════════════════════════
function toggleTheme() {
  const html = document.documentElement;
  const isLight = html.getAttribute('data-theme') === 'light';
  if (isLight) {
    html.removeAttribute('data-theme');
    document.getElementById('theme-btn').textContent = 'Light';
    try { localStorage.setItem('pep_theme', 'dark'); } catch(e) {}
  } else {
    html.setAttribute('data-theme', 'light');
    document.getElementById('theme-btn').textContent = 'Dark';
    try { localStorage.setItem('pep_theme', 'light'); } catch(e) {}
  }
  // Refresh cached colors and redraw all canvases
  refreshThemeColors();
  draw();
  drawVectorSpace();
  drawEmopic();
}
// Restore saved preference
(function() {
  try {
    if (localStorage.getItem('pep_theme') === 'light') {
      document.documentElement.setAttribute('data-theme', 'light');
      document.getElementById('theme-btn').textContent = 'Dark';
      refreshThemeColors();
    }
  } catch(e) {}
})();

// ═══════════════════════════════════════════════════════════════════════
// Screenshot graph as PNG
// ═══════════════════════════════════════════════════════════════════════
function screenshotGraph() {
  const c = document.getElementById('graph-canvas');
  if (!c) return;
  const url = c.toDataURL('image/png');
  const a = document.createElement('a');
  a.href = url;
  a.download = 'pep-graph.png';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

// ═══════════════════════════════════════════════════════════════════════
// Fullscreen mode for the graph canvas
// ═══════════════════════════════════════════════════════════════════════
function toggleFullscreen() {
  const wrap = document.querySelector('#graph-builder .canvas-wrap');
  if (!wrap) return;
  if (document.fullscreenElement) {
    document.exitFullscreen();
  } else {
    wrap.requestFullscreen().then(() => {
      const c = document.getElementById('graph-canvas');
      // Make the wrap fill the screen
      wrap.style.width = '100vw';
      wrap.style.height = '100vh';
      wrap.style.maxWidth = 'none';
      wrap.style.maxHeight = 'none';
      wrap.style.border = 'none';
      wrap.style.borderRadius = '0';
      // Make canvas match
      c.width = window.innerWidth;
      c.height = window.innerHeight;
      c.style.width = '100%';
      c.style.height = '100%';
      setTimeout(zoomFit, 300);
    }).catch(() => {});
  }
}
document.addEventListener('fullscreenchange', () => {
  if (!document.fullscreenElement) {
    const wrap = document.querySelector('#graph-builder .canvas-wrap');
    const c = document.getElementById('graph-canvas');
    // Restore wrap styles
    if (wrap) {
      wrap.style.width = '';
      wrap.style.height = '';
      wrap.style.maxWidth = '';
      wrap.style.maxHeight = '';
      wrap.style.border = '';
      wrap.style.borderRadius = '';
    }
    c.style.width = '';
    c.style.height = '';
    c.width = 960;
    c.height = 640;
    setTimeout(zoomFit, 100);
  }
});

// ═══════════════════════════════════════════════════════════════════════
// Download as standalone HTML
// ═══════════════════════════════════════════════════════════════════════
function downloadPage() {
  // Grab the full page HTML as-is (it's already self-contained with inline CSS/JS)
  const html = '<!DOCTYPE html>' + document.documentElement.outerHTML;
  const blob = new Blob([html], { type: 'text/html' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'pep-math-playground.html';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
</script>
</body>
</html>
"""


@router.get("/math", response_class=HTMLResponse)
async def math_playground() -> str:
    return _PAGE
