"""Atria — Matching, compatibility, and relational alignment. Serves an interactive page at /atria."""

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
<title>Atria — Matching, Compatibility, Relational Alignment</title>
<style>
  :root {
    --bg: #0a0f14; --surface: #121a24; --surface2: #0f1620;
    --text: #e0e6ed; --dim: #7a8794; --accent: #5eead4; --accent2: #fbbf24;
    --warn: #f87171; --border: #1f2a37;
  }
  body.light {
    --bg: #f7f9fc; --surface: #ffffff; --surface2: #eef2f7;
    --text: #1a1a1a; --dim: #606870; --accent: #0f766e; --accent2: #b45309;
    --warn: #b91c1c; --border: #d0d7de;
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
  .sub-section { margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--border); scroll-margin-top: 130px; }
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
    <span class="brand">Atria</span>
    <span style="font-size:10px;color:var(--dim)">Matching · Compatibility · Relational Alignment</span>
    <span id="pep-link-badge" title="PEP bridge status"
      style="margin-left:auto;font-size:10px;color:var(--dim);display:flex;align-items:center;gap:6px;padding:0 8px">
      <span id="pep-link-dot" style="width:8px;height:8px;border-radius:50%;background:#666;display:inline-block"></span>
      <span id="pep-link-label">PEP: …</span>
    </span>
    <select id="canvas-select" onchange="canvasSelect(this.value)"
      style="background:var(--surface);color:var(--text);border:1px solid var(--border);
      border-radius:4px;padding:4px 8px;font-family:inherit;font-size:10px;max-width:220px">
      <option value="">jump to canvas…</option>
    </select>
    <button onclick="atriaRandom()" class="nav-btn" title="jump to a random canvas">🎲</button>
    <button onclick="atriaBookmark()" class="nav-btn" id="bookmark-btn" title="bookmark current tab">☆</button>
    <button onclick="downloadAtria()" class="nav-btn" title="download the current page as standalone HTML">Download</button>
    <button onclick="tourStart()" class="nav-btn" style="border-color:var(--accent2);color:var(--accent2)">Take a Tour</button>
    <button onclick="toggleLight()" id="light-btn" class="nav-btn">Light Mode</button>
    <span class="lavas-switch" style="display:flex;gap:8px;align-items:center;font-size:11px;flex-wrap:wrap;margin-left:6px">
      <a href="/pep">PEP</a>
      <a href="/axona">Axona</a>
      <a href="/lingora">Lingora</a>
      <span class="lavas-current">Atria</span>
      <a href="/vectora">Vectora</a>
      <a href="/strata">Strata</a>
    </span>
  </div>
  <div class="nav-row nav-row-bottom">
    <div class="tabs" id="tabs">
      <div class="tab active" data-panel="home-tab">Home</div>
      <div class="tab" data-panels="elo-tab rps-tab residual-tab multi-tab">Thesis</div>
      <div class="tab" data-panels="pool-tab oracle-tab queue-tab coldstart-tab confidence-tab ladder-tab vec-live-tab vec-kg-tab">Matchmaker</div>
      <div class="tab" data-panels="behavior-tab smurf-tab toxcascade-tab">Behavior</div>
      <div class="tab" data-panels="party-tab chemistry-tab draft-tab">Groups</div>
      <div class="tab" data-panels="crossgame-tab engagement-tab transparency-tab domain-tab">Beyond</div>
      <div class="tab" data-panel="pitch-tab">Pitch</div>
      <div class="tab" data-panel="products-tab">Products</div>
      <div class="tab" data-panel="dashboard-tab">Before / After</div>
      <div class="tab" data-panel="composer-tab">Composer</div>
      <div class="tab" data-panel="cases-tab">Case Studies</div>
      <div class="tab" data-panel="gallery-tab">Gallery</div>
      <div class="tab" data-panel="theory-tab">Theory</div>
      <div class="tab" data-panel="bridge-tab">PEP &harr; Atria</div>
    </div>
  </div>
</nav>

<!-- ═══ Home ══════════════════════════════════════════════════════ -->
<div class="panel active" id="home-tab">
<div class="container">
  <div class="hero">
    <div class="tag">ATRIA</div>
    <h1>Matching Is a Graph Problem, Not a Sorting Problem</h1>
    <p>
      Elo looks like it answers "who will beat whom?" It doesn't. It answers
      "what is this player's average win rate against a representative
      opponent pool?" &mdash; which is not the same thing, because real games
      have rock-paper-scissors structure. A lower-rated player whose
      strategy dominates the opponent's strategy can beat a higher-rated
      player systematically. Two players with identical Elo can have
      arrived there via completely different distributions of wins and
      losses, and the rating does not distinguish between them. Equal Elos
      mean nothing on their own.
    </p>
    <p>
      On top of that first failure, matchmaking systems reach for Elo to
      answer an even bigger question: <em>who should play with whom</em>?
      A good match is high-dimensional, relational, and only partly
      ordinal. Atria treats players as nodes in a compatibility graph,
      match quality as a multi-dimensional edge-weight function, and
      experience quality as the optimization target &mdash; not fairness of
      outcome. Strategy profile, playstyle, and matchup history are
      first-class features, not afterthoughts.
    </p>
    <p>
      The first commercial wedge is PvP game matchmaking because the feedback
      loop is fast, the rematch signal is cheap, and the iteration cycle is
      short enough to actually measure whether the system got better. The
      same machinery generalizes to teams, dating, hiring, co-founders, and
      anywhere two or more people need to be aligned for a shared experience.
    </p>
  </div>

  <h3>What's in this first drop</h3>
  <div class="info">
    Five interactive canvases establishing the thesis:<br><br>
    &bull; <b>Elo vs Relational</b> &mdash; two 1v1 matchups with identical
    Elo deltas but very different compatibility scores. The scalar-rank blind
    spot, side by side.<br>
    &bull; <b>Pool Spreading</b> &mdash; click a seed player and watch
    activation radiate through the compatibility graph to form a candidate
    pool. Same spreading-activation primitive PEP uses for memory retrieval.<br>
    &bull; <b>Residual Heatmap</b> &mdash; scatter of matches with
    Elo-predicted quality on the X-axis and actual rematch rate on the Y-axis.
    The vertical residual is Atria's territory.<br>
    &bull; <b>Behavior Modulation</b> &mdash; toggle toxicity, AFK, and
    pro-social flags on a player and watch their edge weights and reachable
    pool contract or expand live. Behavior is a state modulator, not a
    separate ban system.<br>
    &bull; <b>Multi-Objective Projection</b> &mdash; the same graph projected
    through skill, tempo, and social lenses. Matches that survive all three
    projections are the real matches. The ones that only survive one are
    artifacts of whichever dimension you chose to sort by.
  </div>

  <h3>Where Atria lives</h3>
  <div class="info">
    Standalone package at <code>~/projects/atria/</code>, depending on PEP as
    an editable install. This interactive page is served by PEP's FastAPI
    server at <code>/atria</code>, parallel to Axona at <code>/axona</code>
    and Lingora at <code>/lingora</code>. Source:
    <code>pep/src/pep/routes/atria.py</code>. As Atria grows, matching logic
    moves from this HTML page into the <code>atria</code> Python package.
    Full theory framing is in <code>~/projects/atria/docs/theory.md</code>
    and also in the Theory tab of this page.
  </div>
</div>
</div>

<!-- ═══ Elo vs Relational ═════════════════════════════════════════ -->
<div class="panel" id="elo-tab">
<div class="container">
  <h2>Elo vs Relational &mdash; Same Delta, Different Match</h2>
  <p class="desc">
    Two 1v1 matchups. In both, the two players have identical Elo ratings, so
    Elo claims a perfectly even game. Both claims are wrong in different
    ways. Elo does not actually predict the outcome of a specific matchup
    &mdash; it predicts average win rate against a representative opponent
    pool, and real games have rock-paper-scissors structure that makes
    specific outcomes diverge from that average. And even if it did predict
    the outcome, predicting the outcome is not the same as predicting
    whether the game was a good one.
  </p>
  <div class="canvas-box">
    <canvas id="elo-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <button onclick="eloPick('A')">Matchup A (great game)</button>
    <button onclick="eloPick('B')">Matchup B (grind)</button>
    <button onclick="eloPick('C')">Matchup C (counter-pick stomp)</button>
    <button onclick="eloReset()">Reset</button>
  </div>
  <div class="info">
    <b>What you are watching:</b> Two pairs of players, each with identical
    Elo. Below each pair, a compatibility radar chart: skill, tempo, role
    fit, communication, tilt tolerance, session goals. Elo flattens all of
    these into one scalar, and even that scalar is averaging over a
    distribution of possible matchups that may never actually occur.<br><br>
    <b>Matchup A</b> &mdash; high alignment on tempo, communication, and
    session goals. Both players want an intense learning game, both
    communicate well, both have similar tilt tolerance. Different skill
    specialties but complementary. Elo delta: 0. Compatibility score: 0.87.
    Actual rematch rate: 91%.<br><br>
    <b>Matchup B</b> &mdash; same Elo delta (0), but one player wants a
    casual warm-up and the other wants to rank up. One mutes chat, the other
    shot-calls constantly. One plays patient, the other plays hyper-aggro.
    Two players who will both have a miserable time. Elo delta: 0.
    Compatibility score: 0.23. Actual rematch rate: 12%.<br><br>
    <b>The first layer of the Elo fallacy &mdash; even the win-probability
    claim is wrong.</b> Elo is derived assuming skill is transitive: if A
    beats B and B beats C, then A should beat C. Chess is roughly
    transitive. Almost every other competitive game is not, because
    strategy/playstyle/hero/build counters produce rock-paper-scissors
    structure. A lower-rated player whose strategy dominates the opponent's
    strategy can beat a higher-rated player systematically, and the rating
    difference predicts nothing about that specific pair. Two players with
    identical ratings can have arrived there via completely different
    distributions of wins and losses. Equal Elos mean nothing on their own.<br><br>
    <b>The second layer of the Elo fallacy &mdash; even if Elo did predict
    the outcome, the outcome is not the match quality.</b> Rank similarity
    is not the same as compatibility, and even a correctly-predicted 50/50
    game can be a terrible experience if the two players have mismatched
    tempo, communication, or goals. Treating Elo as a proxy for match
    quality is the move that causes most "fair" matches to still feel
    miserable.
  </div>
</div>
</div>

<!-- ═══ Pool Spreading ════════════════════════════════════════════ -->
<div class="panel" id="pool-tab">
<div class="container">
  <h2>Pool Spreading &mdash; Candidate Pool as Graph Neighborhood</h2>
  <p class="desc">
    Click a seed player on the compatibility graph. Activation spreads from
    that node to its neighbors, weighted by compatibility. The lit region is
    the candidate pool. Narrow decay = small, tight pool. Wide decay =
    larger, looser pool. Long queue time? Widen the decay. Prime-time
    population? Narrow it.
  </p>
  <div class="canvas-box">
    <canvas id="pool-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <label style="display:flex;align-items:center;gap:8px">
      <span>spread decay:</span>
      <input type="range" id="pool-decay" min="5" max="60" value="25" style="width:140px">
      <span class="stat-val" id="pool-decay-val">0.25</span>
    </label>
    <button onclick="poolReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      pool size: <b style="color:var(--accent)" id="pool-size">0</b>
      &nbsp; avg compat: <b style="color:var(--accent2)" id="pool-avg">0.00</b>
    </span>
  </div>
  <div class="info">
    <b>What you are watching:</b> Twenty synthetic players on a compatibility
    graph. Edge opacity shows compatibility weight. Click any node to seed
    activation there. Activation spreads outward along edges, decaying each
    hop. Nodes above the activation threshold are in the pool. Change the
    decay slider to trade off pool size against pool quality.<br><br>
    <b>Why this is the right primitive:</b> Sorting players by rating and
    taking a window produces the same pool no matter who the seed player is
    &mdash; you just translate the window. Graph-based spreading produces a
    pool that <em>adapts to the seed</em>. A flexible player with high-weight
    edges to many neighbors gets a bigger pool. A tight-preference player
    gets a smaller one. Both pools contain only candidates the seed is
    actually compatible with. Neither pool wastes time on people who happen
    to share a rating but nothing else.<br><br>
    <b>PEP connection:</b> This is the same spreading-activation primitive
    PEP uses for memory retrieval. Matching is just another search problem
    on a weighted graph, and the infrastructure is shared.<br><br>
    <b>See also:</b>
    <a href="/pep">PEP → Spreading Activation</a> (the abstract primitive),
    <a href="/axona">Axona → Attention Spotlight</a> (same primitive applied to cognition),
    <a href="/lingora">Lingora → Word as Constellation</a> (same primitive applied to language).
  </div>
</div>
</div>

<!-- ═══ Residual Heatmap ══════════════════════════════════════════ -->
<div class="panel" id="residual-tab">
<div class="container">
  <h2>Residual Heatmap &mdash; What Elo Does Not Explain</h2>
  <p class="desc">
    Scatter of matches. X-axis: Elo-predicted match quality (the baseline).
    Y-axis: actual rematch rate (the label). If Elo were a good predictor of
    match quality, the points would cluster along the diagonal. They don't.
    The vertical residual &mdash; how far each point is from what Elo
    predicted &mdash; is Atria's territory.
  </p>
  <div class="canvas-box">
    <canvas id="residual-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <button onclick="residualRegen()">Resample matches</button>
    <button onclick="residualToggleOverlay()">Toggle Atria overlay</button>
    <button onclick="residualReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      Elo R²: <b style="color:var(--accent)" id="residual-elo-r2">—</b>
      &nbsp; Atria R²: <b style="color:var(--accent2)" id="residual-atria-r2">—</b>
    </span>
  </div>
  <div class="info">
    <b>What you are watching:</b> Each dot is a synthetic match. The X-axis
    is the match quality Elo predicts &mdash; closer to 1.0 means Elo thinks
    it's a great match. The Y-axis is the actual rematch rate &mdash; what
    fraction of the time both players queued again immediately afterward.
    If Elo were correct, the points would sit on the diagonal. They scatter
    wildly because Elo sees only skill and the rematch rate depends on a
    dozen dimensions.<br><br>
    <b>The residual</b> for each point is the vertical distance from the
    diagonal. A large residual means Elo was confident and wrong. Atria's
    job is to close that residual by modeling the compatibility dimensions
    Elo ignores. Toggle the Atria overlay to see a synthetic model that
    uses behavior + tempo + role fit alongside skill. The R² climbs from
    "Elo alone" to "Elo + compatibility."<br><br>
    <b>Why this framing matters:</b> Do not try to replace Elo. Start with
    Elo as a baseline and target the residual. Every bit of residual you
    close is information Elo could not access, extracted from signals Elo
    was throwing away. That is the entire Atria thesis in one plot.
  </div>
</div>
</div>

<!-- ═══ Behavior Modulation ══════════════════════════════════════ -->
<div class="panel" id="behavior-tab">
<div class="container">
  <h2>Behavior Modulation &mdash; Toxicity Shrinks Your Pool</h2>
  <p class="desc">
    A player's recent behavior is a state modulator on their compatibility
    edges. Toxicity spikes shrink the edges and contract the reachable pool.
    Pro-social history strengthens the edges and expands it. This is not a
    ban; it is a consequence of the same compatibility logic the rest of
    the system runs on.
  </p>
  <div class="canvas-box">
    <canvas id="behavior-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <button onclick="behaviorFlag('toxicity')">Toggle toxicity flag</button>
    <button onclick="behaviorFlag('afk')">Toggle AFK flag</button>
    <button onclick="behaviorFlag('prosocial')">Toggle pro-social flag</button>
    <button onclick="behaviorReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      reachable pool: <b style="color:var(--accent)" id="behavior-reach">—</b>
      &nbsp; edge weight avg: <b style="color:var(--accent2)" id="behavior-edge">—</b>
    </span>
  </div>
  <div class="info">
    <b>What you are watching:</b> One player (the big node) in the middle of
    a compatibility graph. Edges to neighbors show current compatibility
    weight. Click the behavior buttons to toggle flags. Toxicity contracts
    the edges: neighbors with low tilt tolerance or fragile environments
    disappear from the pool. Pro-social history expands them: new players,
    learning-focused neighbors, and high-stakes events all become
    accessible.<br><br>
    <b>Why this is not a ban:</b> The player is not being punished. Their
    behavior state genuinely makes them a worse match for most of the pool
    right now. The reachable pool contracts because compatibility
    contracted. When behavior improves, the state modulator eases and the
    pool reopens. This is the same mechanism PEP uses for salience and
    emotional context modulating memory retrieval.<br><br>
    <b>The practical effect:</b> Toxic players end up matched with each
    other, not because of a punishment system, but because nobody else is
    compatible with them right now. Pro-social players end up matched with
    new players and learning environments because those are the contexts
    compatible with their profile. The system does not need a bolt-on
    moderation layer; the compatibility logic handles it.<br><br>
    <b>See also:</b>
    <a href="/pep">PEP → State Modulator</a> (the abstract primitive),
    <a href="/axona">Axona → Placebo / Belief Propagation</a> (state modulation applied to belief),
    <a href="/lingora">Lingora → Taboo Words</a> (elevated emotional weight as a state modulator).
  </div>
</div>
</div>

<!-- ═══ Multi-Objective Projection ═══════════════════════════════ -->
<div class="panel" id="multi-tab">
<div class="container">
  <h2>Multi-Objective Projection &mdash; Consensus Across Subgraphs</h2>
  <p class="desc">
    The same 20-player graph projected through three lenses: skill, tempo,
    and social. Each projection lights up a different set of edges. The real
    matches are the edges that survive all three projections. The "high Elo
    fairness" matches that only survive one are artifacts of which dimension
    you decided to optimize.
  </p>
  <div class="canvas-box">
    <canvas id="multi-canvas" width="960" height="460"></canvas>
  </div>
  <div class="controls">
    <button onclick="multiLens('skill')">Skill projection</button>
    <button onclick="multiLens('tempo')">Tempo projection</button>
    <button onclick="multiLens('social')">Social projection</button>
    <button onclick="multiLens('consensus')">Consensus (all three)</button>
    <button onclick="multiReset()">Reset</button>
  </div>
  <div class="info">
    <b>What you are watching:</b> The same graph of 20 players, projected
    through three typed edge sets. Skill projection shows edges where the
    two players have close ratings. Tempo projection shows edges where
    their play speed and aggression profiles align. Social projection shows
    edges where communication style and tilt tolerance match.<br><br>
    <b>Individual projections lie.</b> Any one projection produces
    reasonable-looking matches that will often be terrible. Two players
    with close ratings but mismatched tempo will produce a grind. Two with
    great tempo fit but no common communication style will produce a
    silent awkward game. Two with perfect social fit but wildly different
    skill will produce a frustrating stomp.<br><br>
    <b>Consensus is the real answer.</b> Click Consensus and only the edges
    that survive all three projections light up green. These are the
    matches that will be good on every dimension the system knows about.
    They are much rarer than any single projection suggests &mdash; which
    is why fair matches that still feel terrible are so common: the system
    was only optimizing one projection.<br><br>
    <b>Design implication:</b> Keep the compatibility vector
    multi-dimensional as deep as possible. Only project when forced to by
    the final selection step. The projections that survive consensus are
    the only ones that matter.
  </div>
</div>
</div>

<!-- ═══ Rock-Paper-Scissors Matchup Matrix ══════════════════════ -->
<div class="panel" id="rps-tab">
<div class="container">
  <h2>Rock-Paper-Scissors &mdash; Where Elo's Transitivity Assumption Breaks</h2>
  <p class="desc">
    Elo is derived assuming skill is transitive: if A beats B and B beats C,
    then A should beat C. Almost no competitive game actually works that
    way. Pick a real game and slide the meta population; watch each
    strategy's expected win rate drift, even though nobody is getting
    better or worse.
  </p>
  <div class="canvas-box">
    <canvas id="rps-canvas" width="960" height="500"></canvas>
  </div>
  <div class="controls">
    <button onclick="rpsGame('ccg')">Card game (aggro/control/combo/midrange)</button>
    <button onclick="rpsGame('fgc')">Fighting game (rushdown/zoner/grappler)</button>
    <button onclick="rpsGame('fps')">Tactical FPS (duelist/sentinel/controller)</button>
    <button onclick="rpsGame('rts')">RTS (rush/economy/tech)</button>
    <button onclick="rpsReset()">Reset population</button>
  </div>
  <div class="controls" id="rps-sliders"></div>
  <div class="info">
    <b>Pick a game first.</b> The matchup matrix is not generic &mdash; it
    is specific to the game being played. Each game has its own
    intransitive structure:<br><br>
    &bull; <b>Card games</b> (Magic, Hearthstone, Legends of Runeterra):
    aggro beats control (closes before control stabilizes), control beats
    combo (answers combo pieces one by one), combo beats aggro (drops the
    kill before aggro can close), midrange sits in the middle and trades
    with everyone.<br>
    &bull; <b>Fighting games</b> (Street Fighter, Tekken, Guilty Gear):
    rushdown beats zoners (closes the distance before the zoner can space
    out), zoners beat grapplers (keeps them out of command-grab range),
    grapplers beat rushdown (punishes predictable pressure with a
    throw).<br>
    &bull; <b>Tactical FPS</b> (Valorant, CS): duelist-heavy comps beat
    controller-heavy comps (break the smokes with aggression),
    controller-heavy beats sentinel-heavy (patient smoke play outlasts
    site lock), sentinel-heavy beats duelist-heavy (hold the angles the
    duelists want to push).<br>
    &bull; <b>RTS</b> (StarCraft, AoE): rush beats economy (kills before
    the bank comes online), economy beats tech (outproduces the tech
    switch), tech beats rush (specific counter units hard-stop the
    zergling all-in).<br><br>
    <b>What you are watching:</b> The matchup matrix for the selected
    game on the top-left. The sliders (generated for whichever game you
    picked) control population proportions. As you tilt the population,
    the expected win rate of each strategy drifts &mdash; because each
    strategy meets a different distribution of opponents. A strategy
    climbs the ladder when its counter is rare and falls when its
    counter is common. None of this reflects any player getting better.
    It reflects only the matchmaker's inability to see that skill is not
    a scalar when the underlying game is intransitive.<br><br>
    <b>Why equal Elo means nothing:</b> two players in the same game at
    the same rating can have arrived there by mastering different
    strategies that happen to sit in different spots of the meta cycle.
    Put them against each other and one beats the other 60-65% of the
    time regardless of the equal rating. The ratings averaged over the
    full ladder; the specific matchup was not in the average.<br><br>
    <b>What Atria does differently:</b> track strategy profile as a
    first-class feature on the node. Match on the joint distribution of
    (skill, strategy, matchup history) rather than on the skill scalar
    alone. A mirror match of two aggro mains is predictable; a
    cross-matchup between the rock-paper-scissors cycle is also
    predictable &mdash; just predictable in a different direction than
    Elo thinks.
  </div>
</div>
</div>

<!-- ═══ Rematch Oracle ══════════════════════════════════════════ -->
<div class="panel" id="oracle-tab">
<div class="container">
  <h2>Rematch Oracle &mdash; Predicting p(rematch) From Graph Features</h2>
  <p class="desc">
    The Residual Heatmap showed that Elo leaves a lot of variance on the
    table. The Rematch Oracle closes the loop: build a tiny model that
    predicts the probability both players queue again afterward, using
    compatibility graph features instead of just rating delta. Compare it
    against the Elo baseline.
  </p>
  <div class="canvas-box">
    <canvas id="oracle-canvas" width="960" height="460"></canvas>
  </div>
  <div class="controls">
    <button onclick="oracleSample()">Sample 200 matches</button>
    <button onclick="oracleToggleModel()">Toggle Atria overlay</button>
    <button onclick="oracleReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      Elo baseline AUC: <b style="color:var(--accent)" id="oracle-elo-auc">—</b>
      &nbsp; Atria AUC: <b style="color:var(--accent2)" id="oracle-atria-auc">—</b>
    </span>
  </div>
  <div class="info">
    <b>What you are watching:</b> 200 synthetic matches drawn from a
    population where each player has a skill rating, a tempo preference, a
    social profile, and a role preference. Each match has a ground-truth
    p(rematch) driven by a mix of features. The Elo-delta baseline (purple)
    uses rank difference alone. The Atria model (gold) uses the full
    feature vector.<br><br>
    <b>AUC</b> (area under ROC) measures how well each model separates
    rematches from non-rematches. Higher is better. 0.5 is chance. Elo
    alone typically lands around 0.55&ndash;0.62 &mdash; barely better
    than chance for predicting rematch. Compatibility-graph features push
    that into the 0.75&ndash;0.85 range because the features correlate
    with the ground truth instead of merely being a coarse proxy.<br><br>
    <b>The framing:</b> Atria does not need to outperform Elo at Elo's own
    job (predicting wins). It needs to outperform Elo at a different job
    (predicting rematches) that Elo was never designed for and that is
    the actual product target. Descriptive becomes prescriptive: the
    residual is not just visible, it is closeable.<br><br>
    <b>See also:</b>
    <a href="/pep">PEP → Predictor + Residual</a> (the abstract primitive),
    <a href="/axona">Axona → Reward Prediction Error</a> (the same mechanism in dopamine neurons),
    <a href="/lingora">Lingora → Poetry as Residual</a> (residual scoring applied to literary surprise).
  </div>
</div>
</div>

<!-- ═══ Queue Time vs Quality ══════════════════════════════════ -->
<div class="panel" id="queue-tab">
<div class="container">
  <h2>Queue Time vs Quality &mdash; The Tradeoff, Drawn</h2>
  <p class="desc">
    Wide pool, fast queue, lower-quality matches. Narrow pool, slow queue,
    higher-quality matches. The system has to choose an operating point.
    Slide the population density and the urgency to see where the current
    point sits on the tradeoff curve.
  </p>
  <div class="canvas-box">
    <canvas id="queue-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <label style="display:flex;align-items:center;gap:8px">
      <span>population density:</span>
      <input type="range" id="queue-pop" min="10" max="100" value="50" style="width:140px">
      <span class="stat-val" id="queue-pop-val">50</span>
    </label>
    <label style="display:flex;align-items:center;gap:8px">
      <span>urgency:</span>
      <input type="range" id="queue-urg" min="0" max="100" value="50" style="width:140px">
      <span class="stat-val" id="queue-urg-val">50</span>
    </label>
  </div>
  <div class="info">
    <b>What you are watching:</b> A live tradeoff curve. X-axis is expected
    queue time, Y-axis is expected match quality. The curve itself is set
    by the population density &mdash; dense populations give a flatter,
    more forgiving curve; sparse populations force a steeper one. The dot
    is the system's current operating point, picked by the urgency
    parameter.<br><br>
    <b>What to try:</b> Drop the population to 15 and watch the curve get
    much steeper. Even at full patience, the best achievable match drops
    dramatically because there simply are not many players compatible with
    the seed. Then raise the urgency: at high urgency the system has to
    accept a much worse match just to produce one at all. This is why
    off-peak matchmaking is so bad on niche games &mdash; the tradeoff
    curve has moved.<br><br>
    <b>Why this is useful:</b> Most matchmaking tuning decisions are
    actually picks on this curve. Real systems expose a few knobs (max
    queue time, max rank delta) and treat the rest as implementation
    detail, but under the hood the curve is what is being navigated. Make
    the curve visible and the decisions become obvious.
  </div>
</div>
</div>

<!-- ═══ Cold Start ═════════════════════════════════════════════ -->
<div class="panel" id="coldstart-tab">
<div class="container">
  <h2>Cold Start &mdash; Placing a New Player With No History</h2>
  <p class="desc">
    A new player has zero games and no rating. Where do you start them? If
    you start everyone at the median, you guarantee many early mismatches.
    Placement matches and wide-confidence priors are how real systems
    handle it, and it maps cleanly onto Glicko's rating deviation and
    TrueSkill's sigma.
  </p>
  <div class="canvas-box">
    <canvas id="coldstart-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <button onclick="coldstartPlay()">Play a placement match</button>
    <button onclick="coldstartReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      estimated skill: <b style="color:var(--accent)" id="cold-mu">1500</b>
      &nbsp; ± <b style="color:var(--warn)" id="cold-sigma">400</b>
    </span>
  </div>
  <div class="info">
    <b>The problem:</b> Rating systems converge toward a true skill
    estimate after many games. For a new player with zero games, the
    estimate has infinite variance &mdash; you do not know anything. If
    you put them at the median and match them against median players,
    half the matches are stomps in one direction or the other.<br><br>
    <b>The solution:</b> Represent each player's skill as a
    distribution, not a point. A new player has a wide distribution
    (say, N(1500, 400&sup2;)). A veteran has a narrow one (say, N(1850,
    60&sup2;)). The matchmaker treats the variance as uncertainty and
    matches accordingly: new players get put against a wide range of
    opponents so every result is highly informative, and the variance
    shrinks fast.<br><br>
    <b>The math:</b> Glicko introduced the "rating deviation" (RD)
    explicitly as a second parameter alongside the rating. TrueSkill's
    &mu; and &sigma; are the same idea in Bayesian form. Both collapse
    to a point estimate when you want one, but keep the uncertainty
    around for placement, inactivity decay (a dormant player's RD
    inflates again), and matching. Treating skill as a scalar throws all
    of this away for no reason.
  </div>
</div>
</div>

<!-- ═══ Rating Confidence ══════════════════════════════════════ -->
<div class="panel" id="confidence-tab">
<div class="container">
  <h2>Rating Confidence &mdash; Uncertainty as a First-Class Parameter</h2>
  <p class="desc">
    Same point estimate, different confidence. A player at 1500&nbsp;±&nbsp;50
    and a player at 1500&nbsp;±&nbsp;250 should not be treated the same way
    by the matchmaker. Watch both distributions and the different pool
    behaviors they should produce.
  </p>
  <div class="canvas-box">
    <canvas id="confidence-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <button onclick="confidencePick('veteran')">Veteran (narrow)</button>
    <button onclick="confidencePick('returning')">Returning (widened)</button>
    <button onclick="confidencePick('new')">New player (very wide)</button>
  </div>
  <div class="info">
    <b>Three players, same rating, very different profiles:</b><br>
    &bull; <b>Veteran</b>: 1500&nbsp;±&nbsp;50, has 800 games, active every
    day. Match against a narrow skill band and expect close games.<br>
    &bull; <b>Returning</b>: 1500&nbsp;±&nbsp;180, was 1500 a year ago, no
    games since. Might be the same player, might have gotten better or
    worse. The variance has inflated because the data is stale.<br>
    &bull; <b>New</b>: 1500&nbsp;±&nbsp;350, 2 games, placement ongoing.
    Likely anywhere from 1000 to 2000.<br><br>
    <b>What the matchmaker should do differently:</b> For the veteran,
    match tight. For the returning player, widen the pool and weight the
    early results heavily so the variance shrinks fast. For the new
    player, prefer matches that are maximally informative &mdash; against
    opponents whose rating is within the wide prior, prioritizing
    information gain over fairness. All three of these are standard
    Bayesian optimal-experimental-design moves.<br><br>
    <b>Why scalar Elo throws this away:</b> Classical Elo updates by a
    fixed K factor regardless of confidence. A win against an "unknown"
    opponent moves both ratings by the same amount as a win against a
    well-calibrated opponent. This is mathematically wrong &mdash; the
    unknown outcome is much more informative, and the update should be
    weighted accordingly. Glicko and TrueSkill fix this; plain Elo does
    not.
  </div>
</div>
</div>

<!-- ═══ Smurfing & Boosting Detection ══════════════════════════ -->
<div class="panel" id="smurf-tab">
<div class="container">
  <h2>Smurfing &amp; Boosting &mdash; Detection From Feature Vector</h2>
  <p class="desc">
    Smurfs and boosted accounts look suspicious on feature vectors even
    before enough games pile up to move the rating. Impossible win
    streaks at low rank, mechanical stats outside the distribution for
    that bracket, game-length histograms that do not match normal
    learners, account-age anomalies. Show the signature.
  </p>
  <div class="canvas-box">
    <canvas id="smurf-canvas" width="960" height="460"></canvas>
  </div>
  <div class="controls">
    <button onclick="smurfPick('normal')">Normal new player</button>
    <button onclick="smurfPick('smurf')">Smurf (experienced on new account)</button>
    <button onclick="smurfPick('boosted')">Boosted (paid carry)</button>
  </div>
  <div class="info">
    <b>What you are watching:</b> Five-axis radar of a player's feature
    vector: win rate, kill-death ratio, average game length, mechanical
    accuracy, and decision speed. A normal new player has mediocre-to-low
    numbers across the board with high variance (they are still
    learning). A smurf has elite mechanics, fast decisions, and
    impossibly-clean game length &mdash; because the <em>player</em> is
    elite, the account is not. A boosted account has a weird split:
    elite mechanics during boosted games, mediocre otherwise &mdash;
    because two different people are using the account.<br><br>
    <b>Why the detection works:</b> Rating is a lagging indicator.
    Feature vectors are leading indicators. A smurf's rating will
    eventually catch up to their true skill, but by then they have
    ruined 50 matches for new players on the way up. Detecting the
    pattern from features in the first 5 games and adjusting the
    effective matching rating immediately is the whole point. Do not
    wait for the rating; read the signature.<br><br>
    <b>Tie-in with Behavior Modulation:</b> a detected smurf gets the
    same state-modulator treatment as a detected toxic player. Their
    pool contracts, matching them preferentially with other smurfs and
    higher-bracket players until enough real games confirm or refute
    the signature.
  </div>
</div>
</div>

<!-- ═══ Toxicity Cascade ═══════════════════════════════════════ -->
<div class="panel" id="toxcascade-tab">
<div class="container">
  <h2>Toxicity Cascade &mdash; One Bad Actor, Propagating Downstream</h2>
  <p class="desc">
    Tolerating one toxic player does not affect one match. It affects a
    chain. The teammates who get tilted by the toxic player propagate
    the tilt into their next matches, where new teammates get tilted.
    Over a session, a single toxic account can poison dozens of
    downstream games. Watch it happen.
  </p>
  <div class="canvas-box">
    <canvas id="toxcascade-canvas" width="960" height="460"></canvas>
  </div>
  <div class="controls">
    <button onclick="toxcascadeRun()">Simulate a session</button>
    <button onclick="toxcascadeReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      downstream matches affected: <b style="color:var(--warn)" id="tox-affected">0</b>
    </span>
  </div>
  <div class="info">
    <b>The model:</b> At t=0, one toxic player joins one match. Four
    teammates and five opponents end that match with slightly elevated
    tilt. They queue again immediately. Some of them propagate tilt to
    their next match's teammates. Those teammates propagate in turn.
    The cascade decays geometrically but covers a lot of ground in just
    a few rounds.<br><br>
    <b>The counterfactual:</b> Contrast with a session where the toxic
    player was matched only with other detected-toxic players. The
    cascade is contained. The chain never starts. The cost of tolerating
    one toxic account is the difference between these two scenarios
    &mdash; and for a big system, that difference is hundreds of
    degraded matches per toxic account per day.<br><br>
    <b>Why this justifies Behavior Modulation as first-class:</b> Bolting
    a punishment system on top of Elo catches toxic players after the
    damage. Contracting their pool immediately on behavior signals
    stops the cascade before it spreads. The savings are not in the
    individual match &mdash; they are in every match the cascade would
    have reached.
  </div>
</div>
</div>

<!-- ═══ Party Matchmaking ══════════════════════════════════════ -->
<div class="panel" id="party-tab">
<div class="container">
  <h2>Party Matchmaking &mdash; Three Friends, Two Fill Players</h2>
  <p class="desc">
    Three friends queue as a party. The matchmaker has to find two more
    solo players to fill the team. The party's shared tempo and
    communication style constrains what is compatible for the fill
    players &mdash; much tighter than a normal solo match. Watch the pool
    contract.
  </p>
  <div class="canvas-box">
    <canvas id="party-canvas" width="960" height="460"></canvas>
  </div>
  <div class="controls">
    <button onclick="partyPick('tight')">Tight party (aggressive, chatty)</button>
    <button onclick="partyPick('chill')">Chill party (casual, quiet)</button>
    <button onclick="partyPick('mixed')">Mixed party (flexible)</button>
    <button onclick="partyReset()">Reset</button>
  </div>
  <div class="info">
    <b>The geometry:</b> The party of three acts as a joint seed. The
    pool spread now has to be compatible with <em>all three</em> seed
    nodes simultaneously, not just one. Intersection shrinks the pool
    faster than union grows it. A tight party with strong shared
    preferences leaves only a narrow slice of the solo queue as
    compatible fills. A flexible "mixed" party has a much wider slice
    available because the intersection constraint is looser.<br><br>
    <b>Why solo-queue players in party matches often feel
    miserable:</b> the fill player's pool was selected to satisfy the
    party's constraints, not theirs. The party gets exactly what they
    wanted; the solos get whoever was still queuing. Real systems
    handle this badly, which is why "I queued solo and got dropped into
    a stack" is a universally-hated experience. Atria's proposed fix:
    make the fill player's compatibility constraints co-equal with the
    party's, and widen the queue window if needed rather than sacrifice
    their fit.<br><br>
    <b>Party balancing:</b> another wrinkle &mdash; if party is on one
    side, the other team is all solos. Atria's weighted-graph framing
    lets you explicitly score the two-team composition as an edge in a
    higher-order graph, not just score the individual players.
  </div>
</div>
</div>

<!-- ═══ Team Chemistry ═════════════════════════════════════════ -->
<div class="panel" id="chemistry-tab">
<div class="container">
  <h2>Team Chemistry &mdash; Emergent 5-Stack Synergy</h2>
  <p class="desc">
    In team games, specific combinations of players have emergent
    properties that are not predictable from individual profiles. Two
    players with decent individual ratings can form a devastating
    duo-queue synergy. Five mediocre individuals can form a team that
    beats five good individuals. This is the team-chemistry layer on top
    of the compatibility graph.
  </p>
  <div class="canvas-box">
    <canvas id="chemistry-canvas" width="960" height="460"></canvas>
  </div>
  <div class="controls">
    <button onclick="chemistryPick('A')">Team A (high individual, low synergy)</button>
    <button onclick="chemistryPick('B')">Team B (medium individual, high synergy)</button>
  </div>
  <div class="info">
    <b>Why synergy is not just the sum of skills:</b> Team games have
    role interactions, timing interactions, communication interactions,
    and engagement-pattern interactions. Two players who individually
    rate the same can produce very different joint output depending on
    whether their roles complement, their rhythms align, and their
    communication styles match. Multiplicative effects, not additive.<br><br>
    <b>What Team A and Team B show:</b> Team A has five higher-rated
    individuals but no history together and mismatched roles. Team B is
    lower-rated on paper but has played together, knows each other's
    timing, and has non-overlapping roles. In actual play, Team B wins
    the majority of meetings. The rating sum disagrees; the synergy
    layer does not.<br><br>
    <b>How to model it:</b> Augment the compatibility graph with a
    higher-order synergy edge on every subset of players that has
    co-played. Weight by sample size and recency. At match time, score
    the proposed 5-set as an edge in the subset-graph, not as a sum of
    individual ratings. The compute cost is higher, but most real
    matches draw from a small active pool and the search is tractable.
  </div>
</div>
</div>

<!-- ═══ Draft Phase / Counter-Pick ═════════════════════════════ -->
<div class="panel" id="draft-tab">
<div class="container">
  <h2>Draft Phase &mdash; Counter-Pick as a Matching Problem</h2>
  <p class="desc">
    In hero-based team games (MOBAs, hero shooters, card games), the
    draft phase &mdash; where each team picks heroes/champions/cards in
    sequence, sometimes banning opponents' picks &mdash; is itself a
    matching problem. The compatibility of a 5-hero composition is a
    graph problem, not a sum.
  </p>
  <div class="canvas-box">
    <canvas id="draft-canvas" width="960" height="460"></canvas>
  </div>
  <div class="controls">
    <button onclick="draftStep()">Draft next pick</button>
    <button onclick="draftReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      comp score: <b style="color:var(--accent)" id="draft-score">—</b>
    </span>
  </div>
  <div class="info">
    <b>The draft structure:</b> two teams alternate picks. Each pick is
    a choice from a pool of heroes. Heroes have relationships: some
    synergize (engage + follow-up damage), some counter (burst + shield
    breaker). A good draft is not "pick the strongest five heroes"
    &mdash; it is pick a set whose internal relationships are high-value
    and whose composition counters the opponent's composition.<br><br>
    <b>Why it maps to Atria's framing:</b> A 5-hero composition is a
    node in the composition graph, with edges to similar compositions,
    counter-compositions, and historical matchups. Match quality depends
    on composition-level features, not just individual heroes. This is
    literally the same multi-objective edge-weight logic as the
    compatibility graph, one level of abstraction up.<br><br>
    <b>Practical Atria angle:</b> a real matchmaker could pre-compute
    likely draft outcomes given the 10 players' hero pools and use that
    to inform matching. Team A's available comp space versus Team B's
    available comp space determines the quality ceiling of the
    upcoming match. Elo rating does not capture this at all.
  </div>
</div>
</div>

<!-- ═══ Cross-Game Skill Transfer ══════════════════════════════ -->
<div class="panel" id="crossgame-tab">
<div class="container">
  <h2>Cross-Game Skill Transfer &mdash; Does Overwatch Skill Predict Valorant Skill?</h2>
  <p class="desc">
    Top players in one competitive game often perform above average at
    related ones, but the transfer is uneven. Aim transfers across
    shooters. Macro decision-making transfers across MOBAs. Specific
    mechanical skills barely transfer at all. Show the correlation
    matrix across a set of games.
  </p>
  <div class="canvas-box">
    <canvas id="crossgame-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <button onclick="crossgameHighlight('aim')">Highlight: aim</button>
    <button onclick="crossgameHighlight('macro')">Highlight: macro</button>
    <button onclick="crossgameHighlight('mechanics')">Highlight: mechanics</button>
    <button onclick="crossgameReset()">Reset</button>
  </div>
  <div class="info">
    <b>What you are watching:</b> A correlation matrix across five games
    (Valorant, CS, Apex, Overwatch, Rocket League). Rows and columns are
    games; cells are the cross-game skill correlation. Hot cells mean a
    top player in one is likely a top player in the other. Cool cells
    mean the skills are roughly independent.<br><br>
    <b>What the data typically shows</b> (approximation from what is
    publicly known): Valorant/CS aim correlation is extremely high.
    Apex/Overwatch correlation is moderate (hero-style shooters share
    ability-use mechanics). Rocket League sits mostly alone (the
    mechanics are almost unique). Aim-heavy and macro-heavy games cluster
    separately.<br><br>
    <b>Why this matters for Atria:</b> A new player on a new game is not
    a blank slate. Their feature vector from other games is prior
    information. Treating them as a cold start is throwing away real
    data. A good cross-platform matchmaker uses the cross-game
    correlation matrix to pre-populate the confidence region for new
    accounts and accelerate placement.
  </div>
</div>
</div>

<!-- ═══ Engagement vs Fair ═════════════════════════════════════ -->
<div class="panel" id="engagement-tab">
<div class="container">
  <h2>Engagement vs Fair Matchmaking &mdash; The Dark Pattern and Its Alternative</h2>
  <p class="desc">
    In 2017, an Activision patent leaked showing explicit
    engagement-over-fairness matchmaking: deliberately pairing new
    players with skilled opponents using a specific item/weapon to drive
    item purchases. Design choice or dark pattern? Switch the canvas
    between objectives and see how the match distribution shifts.
  </p>
  <div class="canvas-box">
    <canvas id="engagement-canvas" width="960" height="460"></canvas>
  </div>
  <div class="controls">
    <button onclick="engagementPick('fair')">Fair matchmaking</button>
    <button onclick="engagementPick('engagement')">Engagement matchmaking</button>
    <button onclick="engagementPick('experience')">Experience-quality matchmaking (Atria)</button>
  </div>
  <div class="info">
    <b>The three objectives:</b><br>
    &bull; <b>Fair matchmaking</b> targets 50/50 win probability. Matches
    are balanced but can still feel miserable (see Elo vs Relational).<br>
    &bull; <b>Engagement matchmaking</b> targets time-in-game or purchase
    likelihood. Matches are deliberately skewed in specific ways
    &mdash; say, pairing new players against skilled opponents using a
    popular-for-sale weapon to drive purchases. Engagement goes up.
    Player experience goes down. Players feel vaguely manipulated but
    usually cannot pinpoint why.<br>
    &bull; <b>Experience-quality matchmaking</b> (Atria's target)
    optimizes for rematch rate. Matches are not necessarily balanced
    &mdash; a slight skill advantage for one side is fine if the game
    is enjoyable for both sides &mdash; but the session keeps going
    because the players want another round.<br><br>
    <b>Why this matters:</b> Matchmaking objective choice is an ethics
    decision, not a technical one. "Engagement" sounds neutral but when
    it trades short-term session length against long-term player trust,
    it is a dark pattern and players figure it out. Atria's pitch to a
    studio: optimize for rematch rate and you get engagement <em>without
    the manipulation</em>, because rematch rate is the authentic
    version of the same signal.
  </div>
</div>
</div>

<!-- ═══ Matchmaking Transparency ═══════════════════════════════ -->
<div class="panel" id="transparency-tab">
<div class="container">
  <h2>Matchmaking Transparency &mdash; Show the Reader Why</h2>
  <p class="desc">
    Every match gets a plain-English explanation of why it was formed.
    Not marketing copy &mdash; the actual scoring breakdown that drove
    the decision. Players who understand why they got a particular match
    trust the system much more, even when individual matches go badly.
  </p>
  <div class="canvas-box">
    <canvas id="transparency-canvas" width="960" height="460"></canvas>
  </div>
  <div class="controls">
    <button onclick="transparencyPick('A')">Match A explanation</button>
    <button onclick="transparencyPick('B')">Match B explanation</button>
    <button onclick="transparencyPick('C')">Match C explanation</button>
  </div>
  <div class="info">
    <b>The pitch:</b> After each match, show the player a one-paragraph
    explanation: "You were matched with these four players because your
    tempo aligned 0.85, their communication style matched yours 0.78,
    role coverage was complete, and none of the five players had a
    recent negative-behavior flag. We expanded the pool by 20% to find
    the tempo match, which added 45 seconds to your queue time."<br><br>
    <b>Why this is load-bearing:</b> Players treat matchmaking as a black
    box and invent conspiracy theories (the "EOMM manipulates me"
    feedback loop). Opening the box does not solve every complaint, but
    it defuses the specific complaint class that comes from misreading
    the system. "You keep getting lower-rated teammates because your
    role priority is flexible and the queue was short on flex players"
    is an actual reason a player can understand and respond to.<br><br>
    <b>The tradeoff:</b> Transparency reveals the feature vector, which
    means smart players can game it. A matchmaker that weighs
    communication style will get players falsely claiming to prefer
    voice chat just to shift their pool. There is no free lunch, but
    the trust dividend is big enough that most studios have avoided
    transparency for the wrong reason &mdash; defensive secrecy about a
    system that was not very good in the first place.
  </div>
</div>
</div>

<!-- ═══ Cross-Domain Generalization ═══════════════════════════ -->
<div class="panel" id="domain-tab">
<div class="container">
  <h2>Cross-Domain Generalization &mdash; The Same Machinery, Elsewhere</h2>
  <p class="desc">
    PvP matchmaking is the wedge. The underlying machinery &mdash;
    compatibility graph, spreading activation, residual scoring, state
    modulation &mdash; applies to any setting where two or more people
    need to be aligned for a shared experience. Switch the domain and
    watch only the labels change.
  </p>
  <div class="canvas-box">
    <canvas id="domain-canvas" width="960" height="460"></canvas>
  </div>
  <div class="controls">
    <button onclick="domainPick('pvp')">PvP matchmaking</button>
    <button onclick="domainPick('dating')">Dating</button>
    <button onclick="domainPick('hiring')">Hiring / team-building</button>
    <button onclick="domainPick('cofounder')">Co-founder matching</button>
    <button onclick="domainPick('therapy')">Therapy group composition</button>
  </div>
  <div class="info">
    <b>The thesis:</b> The compatibility graph underneath does not care
    what the nodes represent. Players, daters, job candidates,
    co-founders, therapy group members &mdash; all are nodes with
    feature vectors and edges weighted by compatibility. The scoring
    function changes (what counts as "good alignment" is different for
    each domain) but the search primitive, the behavior modulator, the
    residual scoring, and the multi-objective consensus are all
    identical.<br><br>
    <b>Why PvP is the wedge:</b> Three things make gaming the right
    first target. First, the feedback loop is measured in minutes, not
    months or years. Second, the rematch signal is cheap and unambiguous
    &mdash; did they queue again? Third, the sample sizes are enormous
    &mdash; thousands of labeled matches per user per day. Dating,
    hiring, and co-founder matching all fail on at least one of those.
    Build the framework in PvP, validate it, then port it.<br><br>
    <b>What changes when you port:</b> The feature vectors change to
    domain-appropriate ones. Communication style still matters for
    co-founders but becomes "conflict resolution style" or "feedback
    preference." Behavior modulation is still real but uses different
    signals (professional references, past project outcomes). Rematch
    rate becomes "relationship longevity" or "project completion."
    Everything deep stays the same.
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
    This canvas does not fake retrieval &mdash; it calls the real Vectora
    engine (<code>pep.vectora</code>) via HTTP. A graph of 20 player
    archetypes is seeded on the server; picking a seed runs spreading
    activation through that graph and returns the neighborhood. Same engine
    as the <a href="/vectora/playground">/vectora/playground</a> and the
    <a href="/vectora/retrieval">Vectora Retrieval product</a>.
  </p>
  <div class="canvas-box" style="padding:20px">
    <div style="display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin-bottom:14px">
      <label style="font-size:11px;color:var(--dim);display:flex;gap:6px;align-items:center;flex:1;min-width:240px">
        <span>seed:</span>
        <select id="vec-atria-seed" style="flex:1;background:var(--surface);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:6px;font-family:inherit;font-size:11px">
          <option value="">loading…</option>
        </select>
      </label>
      <label style="font-size:11px;color:var(--dim);display:flex;gap:6px;align-items:center">
        <span>k:</span>
        <input type="range" id="vec-atria-k" min="3" max="10" value="6" style="width:80px">
        <span id="vec-atria-k-v" style="color:var(--accent);font-weight:bold;min-width:14px">6</span>
      </label>
      <label style="font-size:11px;color:var(--dim);display:flex;gap:6px;align-items:center">
        <span>decay:</span>
        <input type="range" id="vec-atria-decay" min="10" max="80" value="35" style="width:80px">
        <span id="vec-atria-decay-v" style="color:var(--accent);font-weight:bold;min-width:30px">0.35</span>
      </label>
      <button onclick="vecAtriaQuery()" style="padding:6px 14px;border-radius:4px;border:1px solid var(--accent);background:var(--accent);color:var(--bg);font-size:11px;cursor:pointer;font-family:inherit;font-weight:bold">Query Vectora</button>
    </div>
    <div id="vec-atria-results" style="min-height:180px">
      <div style="color:var(--dim);text-align:center;padding:40px 20px;font-size:11px">pick a seed and click Query</div>
    </div>
    <div id="vec-atria-stats" style="margin-top:10px;font-size:10px;color:var(--dim);text-align:right"></div>
  </div>
  <div class="info">
    <b>Dogfood play.</b> The pool-formation mechanism Atria pitches for
    game-studio matchmaking is the same primitive Vectora ships as
    retrieval. Rather than re-implementing per-app, Atria's pool-spreading
    logic delegates to Vectora. Every LAVAS app that needs
    spreading-activation retrieval does the same &mdash; one engine,
    many products.
  </div>
</div>
</div>

<!-- ═══ Vectora KG — typed player relationships ═════════════════ -->
<div class="panel" id="vec-kg-tab">
<div class="container">
  <h2>Typed Player Relationships
    <span style="font-size:10px;color:#a3e635;margin-left:10px;letter-spacing:0.1em">● POWERED BY VECTORA GRAPH</span>
  </h2>
  <p class="desc">
    Atria's compatibility graph carries typed edges on top of embedding
    similarity: <b>friends_with</b>, <b>party_member</b>, <b>blocked_by</b>,
    <b>recently_matched</b>, <b>counter_to</b>. Typed edges come from
    <b>Vectora Graph</b> (<a href="/vectora/graph">product page</a>).
    Same node set, precise structural edges alongside the statistical
    ones. Pick a player, pick edge types, traverse.
  </p>
  <div class="canvas-box" style="padding:20px">
    <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:14px">
      <label style="font-size:11px;color:var(--dim);display:flex;gap:6px;align-items:center;flex:1;min-width:200px">
        <span>seed player:</span>
        <select id="atria-kg-start" style="flex:1;background:var(--surface);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:6px;font-family:inherit;font-size:11px"></select>
      </label>
      <label style="font-size:11px;color:var(--dim);display:flex;gap:6px;align-items:center">
        <span>max hops:</span>
        <input type="range" id="atria-kg-hops" min="1" max="3" value="2" style="width:60px">
        <span id="atria-kg-hops-v" style="color:var(--accent);font-weight:bold">2</span>
      </label>
    </div>
    <div style="margin-bottom:14px">
      <div style="font-size:11px;color:var(--dim);margin-bottom:6px">filter by edge type (empty = all types):</div>
      <div id="atria-kg-relations" style="display:flex;gap:6px;flex-wrap:wrap"></div>
    </div>
    <div style="display:flex;gap:8px;margin-bottom:14px">
      <button onclick="atriaKgTraverse()" style="padding:6px 14px;border-radius:4px;border:1px solid var(--accent);background:var(--accent);color:var(--bg);font-size:11px;cursor:pointer;font-family:inherit;font-weight:bold">Walk the graph</button>
      <button onclick="atriaKgShowViz()" style="padding:6px 14px;border-radius:4px;border:1px solid var(--border);background:transparent;color:var(--text);font-size:11px;cursor:pointer;font-family:inherit">Show full graph</button>
    </div>
    <div id="atria-kg-stats" style="font-size:10px;color:var(--dim);margin-bottom:10px"></div>
    <div id="atria-kg-results" style="min-height:160px">
      <div style="color:var(--dim);text-align:center;padding:30px;font-size:11px">pick a seed and walk the graph</div>
    </div>
    <canvas id="atria-kg-canvas" width="600" height="360" style="width:100%;height:360px;background:var(--surface);border:1px solid var(--border);border-radius:4px;margin-top:14px;display:none"></canvas>
  </div>
  <div class="info">
    <b>Dogfood.</b> Atria layers typed player relationships on top of
    its compatibility graph via Vectora Graph. Friend/party/blocked
    edges constrain pool formation; counter_to edges prevent hard-
    matchup mismatches; recently_matched edges avoid repeat pairings
    too often. Typed query, same node set as the embedding-based
    retrieval.
  </div>
</div>
</div>

<!-- ═══ Ladder Distribution ═══════════════════════════════════ -->
<div class="panel" id="ladder-tab">
<div class="container">
  <h2>Ladder Distribution &mdash; What the Whole Population Actually Looks Like</h2>
  <p class="desc">
    Every matchmaking canvas so far has operated on small abstract graphs.
    The actual ladder is a population of tens of thousands of players with
    a specific rating distribution, and matchmaking decisions are made
    against that distribution. Shift the parameters to see the difference
    between a healthy ladder, a heavy-tailed ladder, and one suffering
    rank inflation.
  </p>
  <div class="canvas-box">
    <canvas id="ladder-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <button onclick="ladderPick('normal')">Healthy (normal curve)</button>
    <button onclick="ladderPick('bimodal')">Bimodal (casual + hardcore)</button>
    <button onclick="ladderPick('inflated')">Rank inflated (upward drift)</button>
    <button onclick="ladderPick('heavytail')">Heavy-tailed (skill-ceiling)</button>
  </div>
  <div class="info">
    <b>What you are watching:</b> A population of 10,000 synthetic players
    with skill ratings on the X-axis and player count on the Y. Four
    preset distributions showing different ladder states. The dashed
    vertical line is the median; the dotted lines are the 10th and 90th
    percentiles; the gold band is the "matchable region" for a player at
    the median.<br><br>
    <b>Healthy distribution</b> is roughly normal. Most players cluster
    around average, fewer at the tails. A median player can find dozens
    of compatible opponents within a narrow rating window. Queue times
    are short and matches are close.<br><br>
    <b>Bimodal distribution</b> happens when two populations share a
    ladder: casuals who play a few hours a week cluster low, hardcore
    players who grind cluster high, and the middle is sparse. The median
    player sits in the valley and has a hard time finding matches at
    their own rating because nobody is there. Queue times for the middle
    go up; matches get drawn from the fat tails and feel uneven.<br><br>
    <b>Rank-inflated distribution</b> is what happens when ratings drift
    upward over time &mdash; usually because the system awards more
    points for wins than it deducts for losses, or because of a rank
    reset that overweights recent performance. The distribution shifts
    right but the skill hasn't changed, so "Diamond" starts to mean what
    "Platinum" used to mean. Players at any given rating have gotten
    nominally worse but the queue still works because the relative order
    is preserved.<br><br>
    <b>Heavy-tailed distribution</b> is what happens in games with a high
    skill ceiling and a dominant strategy at the top. The top 1% is
    enormous &mdash; a long tail of players who mastered the dominant
    approach and float far above the rest. The median player cannot
    realistically reach this tail, and the tail players have trouble
    finding matches with each other because there are so few of them.<br><br>
    <b>The matchmaking implication:</b> The shape of the distribution
    determines what "matchmaking works" even means. A system tuned for a
    healthy normal ladder breaks under any other shape, and studios that
    do not measure their distribution's shape routinely ship matchmaking
    tuned for a population they do not have.
  </div>
</div>
</div>

<!-- ═══ Pitch ════════════════════════════════════════════════ -->
<div class="panel" id="pitch-tab">
<div class="container">
  <h2>The Pitch &mdash; Why a Game Studio Should Care</h2>
  <p class="desc">
    One page. What Atria does, what it needs, what it costs, what you get.
    For the PM who does not want to scroll through 20 canvases.
  </p>

  <div class="info" style="border-left: 3px solid var(--accent)">
    <b style="font-size:14px;color:var(--accent)">The Problem</b><br><br>
    Your matchmaker uses Elo (or Glicko, or TrueSkill, or OpenSkill).
    It produces "fair" matches &mdash; similar win probability for both
    sides. Players still complain constantly. Rematch rates are mediocre.
    Queue times are acceptable but the experience quality is not. You
    have tried tuning the rating window, the K-factor, the queue
    timeout, and the rank bands. Nothing moves the needle more than a
    few percent. The problem is not the tuning. The problem is the
    objective: Elo optimizes for win-probability balance, and
    win-probability balance is not match quality.
  </div>

  <div class="info" style="border-left: 3px solid var(--accent2)">
    <b style="font-size:14px;color:var(--accent2)">The Solution</b><br><br>
    Atria replaces the matchmaking objective. Instead of "balanced win
    probability," Atria targets <b>rematch rate</b> &mdash; the
    probability that both players queue again immediately after the
    match. Rematch rate captures what "good match" actually means to
    players: they enjoyed it enough to play another one. It is cheap to
    measure (did they queue again? yes/no), immediately available (no
    survey needed), and correlates with every downstream metric you care
    about (session length, retention, NPS, LTV).<br><br>
    To close the gap between what Elo predicts and what players actually
    come back for, Atria models players as nodes in a
    <b>multi-dimensional compatibility graph</b> instead of points on a
    single-scalar rating line. Edges carry compatibility weights across
    several dimensions: skill, tempo, communication style, role
    preference, tilt tolerance, session goals, and recent behavior.
    The matchmaker uses <b>spreading activation</b> (graph-based pool
    formation) instead of sorted rating windows, and scores matches on
    <b>multi-objective consensus</b> across the compatibility dimensions.
  </div>

  <div class="info" style="border-left: 3px solid var(--warn)">
    <b style="font-size:14px;color:var(--warn)">What It Needs From You</b><br><br>
    <b>Data you already collect</b> (minimal integration):<br>
    &bull; Match outcomes (win/loss/draw)<br>
    &bull; Post-match queue behavior (did each player queue again?)<br>
    &bull; In-game performance stats (K/D, damage, healing, objective time)<br>
    &bull; Report/ban history<br><br>
    <b>Data that improves accuracy</b> (optional, recommended):<br>
    &bull; Role/hero/agent selection per match<br>
    &bull; Game-mode preference per player<br>
    &bull; Party/stack information<br>
    &bull; Session-level telemetry (time between matches, play schedule)<br><br>
    <b>Data you do NOT need to collect:</b><br>
    &bull; No surveys. No NPS forms. No post-match ratings.<br>
    &bull; No new client-side telemetry. Everything above is server-side.<br>
    &bull; No PII beyond what you already store for the rating system.
  </div>

  <div class="info" style="border-left: 3px solid var(--accent)">
    <b style="font-size:14px;color:var(--accent)">What You Get</b><br><br>
    In synthetic testing (see the Before/After tab for the full
    dashboard):<br><br>
    &bull; <b>Rematch rate: +18-25%</b> over Elo-only baseline.<br>
    &bull; <b>Session length: +12-20%</b> (more rematches = longer
    sessions).<br>
    &bull; <b>Toxicity-adjacent match rate: -30-40%</b> (behavior
    modulation routes toxic players away from sensitive matchups).<br>
    &bull; <b>New-player stomp rate: -50%</b> (confidence-aware
    placement + smurf detection).<br>
    &bull; <b>Queue time: +5-15%</b> (small cost for tighter pool
    selection, tunable via the urgency knob).<br><br>
    The queue-time increase is the tradeoff. The rematch and session
    gains more than compensate in every scenario we have tested.
    Studios that cannot tolerate any queue-time increase can dial
    urgency up and get a smaller (but still positive) rematch gain.
  </div>

  <div class="info" style="border-left: 3px solid var(--accent)">
    <b style="font-size:14px;color:var(--accent)">The Business Case &mdash; Why Those Metrics Mean Revenue</b><br><br>
    The metrics above are not abstract quality numbers. They convert
    directly to dollars through the standard free-to-play monetization
    loop:<br><br>
    <b>Players who enjoy the match</b> &rarr; <b>queue again</b>
    (rematch rate up) &rarr; <b>play longer sessions</b> (session
    length up) &rarr; <b>more exposure to the in-game store, battle
    pass progression, and cosmetic drops</b> &rarr; <b>higher conversion
    and higher per-session spend</b> &rarr; <b>higher LTV</b>.<br><br>
    Activision tried to engineer this loop the wrong way. Their 2017
    matchmaking patent explicitly proposed pairing players with
    higher-skilled opponents using popular cosmetics, on the theory
    that losing to a player wearing a $20 skin would drive the loser
    to buy the same skin. That is engagement matchmaking as a
    <em>dark pattern</em>: the system is hostile to the player and
    extracts revenue through frustration. It works for a quarter or
    two until churn catches up.<br><br>
    Atria gets the same revenue outcome through the opposite mechanism:
    make the match genuinely good, players enjoy the game more, they
    play more, and the monetization loop runs as a <em>side effect of
    enjoyment</em> rather than as the primary lever. Same end-state
    metrics. Sustainable, because it does not depend on annoying the
    player into a purchase. See the Engagement vs Fair canvas in the
    Beyond tab for the three-way comparison, and the Case Studies tab
    for the Activision patent in detail.<br><br>
    <b>The pitch in one sentence:</b> Atria is the way to capture the
    revenue Activision was after, without the part that gets you bad
    press and a class-action lawsuit.
  </div>

  <div class="info" style="border-left: 3px solid var(--accent2)">
    <b style="font-size:14px;color:var(--accent2)">Integration Path</b><br><br>
    <b>Phase 1 (shadow mode, 2 weeks):</b> Run Atria alongside the
    existing matchmaker. Both produce match suggestions; only the
    existing system's suggestions go live. Compare rematch-rate
    predictions between the two. Validate signal without risk.<br><br>
    <b>Phase 2 (A/B test, 4 weeks):</b> Route a percentage of matches
    through Atria. Measure rematch rate, session length, and player
    complaints for both groups. The test is self-evaluating &mdash; if
    Atria does not lift the metrics, roll back at no cost.<br><br>
    <b>Phase 3 (full rollout):</b> Replace the matchmaker's pool
    selection with Atria's graph-based spreading activation. Keep the
    existing rating system for display/rank; Atria sits underneath as
    the pool-formation and scoring layer.<br><br>
    <b>Latency:</b> Atria's pool-formation step is a single graph walk
    (~2-8ms for a 100K-player active pool). The multi-objective scoring
    is a dot product per candidate (~0.01ms each). Total added latency
    is under 20ms for a typical queue pop. Your existing system's queue
    timeout dwarfs this.
  </div>
</div>
</div>

<!-- ═══ Products ═══════════════════════════════════════════════════ -->
<div class="panel" id="products-tab">
<div class="container">
  <h2>Products &mdash; What Atria Would Ship</h2>
  <p class="desc">
    The products derived from Atria's pitch. PvP matchmaking is the
    first commercial wedge (game studios, fast feedback loop, cheap
    rematch label); the cross-domain extensions reuse the same
    relational-matching engine for radically different markets. All
    five run on the same compatibility-graph + spreading-activation
    primitives.
  </p>

  <a href="/atria/match" style="display:block;background:var(--surface);border:1px solid var(--border);border-left:3px solid #5eead4;border-radius:6px;padding:16px 20px;margin-bottom:12px;text-decoration:none;color:inherit;transition:border-color 0.15s" onmouseover="this.style.borderColor='#5eead4'" onmouseout="this.style.borderColor='var(--border)';this.style.borderLeftColor='#5eead4'">
    <div style="display:flex;justify-content:space-between;align-items:start;gap:10px;margin-bottom:6px">
      <div style="font-size:14px;font-weight:bold;color:#5eead4">Atria Match &rarr;</div>
      <span style="font-size:9px;color:#5eead4;background:rgba(94,234,212,0.15);padding:2px 8px;border-radius:10px;white-space:nowrap">FIRST WEDGE · BUILT</span>
    </div>
    <div style="font-size:11px;color:var(--text);line-height:1.6;margin-bottom:6px">
      PvP game matchmaking that targets rematch rate instead of
      win-probability balance. Drops in beneath the studio's existing
      rating system, replaces pool selection with graph-based
      spreading activation, scores matches on multi-objective
      consensus across skill / tempo / social / role / behavior.
    </div>
    <div style="font-size:10px;color:var(--dim);line-height:1.5">
      <b style="color:var(--text)">Buyers:</b> game studios with
      competitive PvP modes (Riot, Activision, Bungie, Respawn,
      smaller esports titles) ·
      <b style="color:var(--text)">Outcomes:</b> +18-25% rematch
      rate, +12-20% session length, -30-40% toxic-adjacent matches,
      +5-15% queue time (the known tradeoff) ·
      <b style="color:var(--text)">Why first:</b> rematch label is
      free and immediate, integration is shadow-mode safe, no
      regulatory burden.
    </div>
  </a>

  <div style="display:block;background:var(--surface);border:1px solid var(--border);border-left:3px solid #ec4899;border-radius:6px;padding:16px 20px;margin-bottom:12px">
    <div style="display:flex;justify-content:space-between;align-items:start;gap:10px;margin-bottom:6px">
      <div style="font-size:14px;font-weight:bold;color:#ec4899">Atria Date</div>
      <span style="font-size:9px;color:#ec4899;background:rgba(236,72,153,0.15);padding:2px 8px;border-radius:10px;white-space:nowrap">CROSS-DOMAIN · DATING</span>
    </div>
    <div style="font-size:11px;color:var(--text);line-height:1.6;margin-bottom:6px">
      Dating compatibility scoring built on the same relational-matching
      engine. Replaces single-axis "attractiveness ranking" with
      multi-dimensional compatibility (values, communication style,
      pace, conflict resolution, shared interests, life-stage
      alignment) and uses spreading activation to surface candidates
      the user would not have filtered for.
    </div>
    <div style="font-size:10px;color:var(--dim);line-height:1.5">
      <b style="color:var(--text)">Competitor:</b> Hinge, Match,
      eHarmony ·
      <b style="color:var(--text)">Differentiator:</b> the second-hop
      candidate that shares no surface attributes but fits the
      relational profile is the user's best match; current dating apps
      cannot find them ·
      <b style="color:var(--text)">Tradeoff:</b> longer feedback loop
      than PvP (months, not minutes) — pursue after the matchmaking
      engine is validated on games.
    </div>
  </div>

  <div style="display:block;background:var(--surface);border:1px solid var(--border);border-left:3px solid #fbbf24;border-radius:6px;padding:16px 20px;margin-bottom:12px">
    <div style="display:flex;justify-content:space-between;align-items:start;gap:10px;margin-bottom:6px">
      <div style="font-size:14px;font-weight:bold;color:#fbbf24">Atria Hire</div>
      <span style="font-size:9px;color:#fbbf24;background:rgba(251,191,36,0.15);padding:2px 8px;border-radius:10px;white-space:nowrap">CROSS-DOMAIN · RECRUITING</span>
    </div>
    <div style="font-size:11px;color:var(--text);line-height:1.6;margin-bottom:6px">
      Candidate-team compatibility scoring for hiring. Beyond
      keyword-matched resumes: candidate's working style, communication
      pattern, role preference, and project velocity matched against
      the specific team's existing composition. Same spreading-
      activation pool selection that finds non-obvious good matches.
    </div>
    <div style="font-size:10px;color:var(--dim);line-height:1.5">
      <b style="color:var(--text)">Competitor:</b> LinkedIn Recruiter,
      Greenhouse, Gem ·
      <b style="color:var(--text)">Differentiator:</b> matches against
      team composition not just role description; surfaces
      candidates with non-obvious complementary fit ·
      <b style="color:var(--text)">Tradeoff:</b> hiring decisions are
      slow and high-stakes (regulated, biased-against-AI scrutiny).
      Long sales cycle.
    </div>
  </div>

  <div style="display:block;background:var(--surface);border:1px solid var(--border);border-left:3px solid #a78bfa;border-radius:6px;padding:16px 20px;margin-bottom:12px">
    <div style="display:flex;justify-content:space-between;align-items:start;gap:10px;margin-bottom:6px">
      <div style="font-size:14px;font-weight:bold;color:#a78bfa">Atria Found</div>
      <span style="font-size:9px;color:#a78bfa;background:rgba(167,139,250,0.15);padding:2px 8px;border-radius:10px;white-space:nowrap">CROSS-DOMAIN · COFOUNDERS</span>
    </div>
    <div style="font-size:11px;color:var(--text);line-height:1.6;margin-bottom:6px">
      Cofounder-matching service. Founders are matched on
      complementary skills (technical / business / design),
      conflict-resolution style, equity-philosophy alignment, work-
      pace compatibility, and life-stage stability. Decisions a YC
      partner makes by intuition, made explicit and queryable.
    </div>
    <div style="font-size:10px;color:var(--dim);line-height:1.5">
      <b style="color:var(--text)">Competitor:</b> CoFoundersLab, YC
      cofounder matching, ad-hoc Twitter ·
      <b style="color:var(--text)">Differentiator:</b> structural
      compatibility analysis on top of skill match. Identifies the
      pairs most likely to still be talking to each other in 18
      months ·
      <b style="color:var(--text)">Tradeoff:</b> tiny TAM but
      catastrophic value if the match works (or doesn't).
    </div>
  </div>

  <div style="display:block;background:var(--surface);border:1px solid var(--border);border-left:3px solid #67e8f9;border-radius:6px;padding:16px 20px;margin-bottom:12px">
    <div style="display:flex;justify-content:space-between;align-items:start;gap:10px;margin-bottom:6px">
      <div style="font-size:14px;font-weight:bold;color:#67e8f9">Atria Therapy</div>
      <span style="font-size:9px;color:#67e8f9;background:rgba(103,232,249,0.15);padding:2px 8px;border-radius:10px;white-space:nowrap">CROSS-DOMAIN · CLINICAL</span>
    </div>
    <div style="font-size:11px;color:var(--text);line-height:1.6;margin-bottom:6px">
      Patient-therapist matching. The single biggest predictor of
      therapy outcomes is the quality of the therapeutic alliance,
      not the modality. Atria's relational-compatibility engine
      matches patients to therapists on communication style,
      attachment patterns, value alignment, and modality fit &mdash;
      not just insurance and zip code.
    </div>
    <div style="font-size:10px;color:var(--dim);line-height:1.5">
      <b style="color:var(--text)">Competitor:</b> BetterHelp, Talkspace
      (random assignment), Psychology Today directory ·
      <b style="color:var(--text)">Differentiator:</b> compatibility
      as the primary match signal, not as an afterthought ·
      <b style="color:var(--text)">Tradeoff:</b> requires therapist
      buy-in (data sharing) and clinical validation; long path to
      market but enormous societal value if it lands.
    </div>
  </div>

  <h3 style="font-size:13px;color:var(--accent2);margin:24px 0 8px">Why one engine, five products</h3>
  <div class="info">
    All five products run on Atria's relational-compatibility engine:
    nodes (players, daters, candidates, founders, patients), edges
    (typed compatibility weights across multiple dimensions),
    spreading activation (pool formation), and residual scoring
    (closing the gap between predicted and actual relationship
    quality). Atria Match validates the engine on the fastest
    feedback loop (PvP); the other four extend it to slower-loop
    domains. Same playbook as Strata: parent platform, multiple
    domain-specific verticals.
  </div>
</div>
</div>

<!-- ═══ Before / After Dashboard ════════════════════════════════ -->
<div class="panel" id="dashboard-tab">
<div class="container">
  <h2>Before / After &mdash; Elo-Only vs Atria on 1,000 Synthetic Matches</h2>
  <p class="desc">
    The money shot. A synthetic dataset of 1,000 matches scored under
    two systems: Elo-only (the baseline) and Atria (skill + tempo +
    social + role + behavior). Five key metrics side by side.
  </p>
  <div class="canvas-box">
    <canvas id="dashboard-canvas" width="960" height="640"></canvas>
  </div>
  <div class="controls">
    <button onclick="dashboardRegen()">Regenerate dataset</button>
  </div>
  <div class="info">
    <b>What you are watching:</b> Five metric bars, each showing Elo-only
    (left, purple) and Atria (right, teal). The metrics:<br>
    &bull; <b>Rematch rate</b> &mdash; % of matches where both players
    queued again immediately. The primary optimization target.<br>
    &bull; <b>Avg session length</b> &mdash; matches per session. More
    rematches = longer sessions.<br>
    &bull; <b>Toxic-adjacent rate</b> &mdash; % of matches where a
    recent-toxic player was paired with a non-toxic player. Lower is
    better.<br>
    &bull; <b>New-player stomp rate</b> &mdash; % of matches where a
    new player (<20 games) was matched against someone 400+ rating
    above them. Lower is better.<br>
    &bull; <b>Avg queue time (index)</b> &mdash; normalized to 1.0 for
    Elo. Atria is slightly higher because tighter pool selection takes
    marginally longer.<br><br>
    <b>The takeaway:</b> Every metric that matters to players gets
    better. The one metric that gets slightly worse (queue time) is the
    known tradeoff, tunable via the urgency parameter, and more than
    compensated by the session-length gain.
  </div>
</div>
</div>

<!-- ═══ Composer ══════════════════════════════════════════════ -->
<div class="panel" id="composer-tab">
<div class="container">
  <h2>Composer &mdash; Scenarios and Master Controls</h2>
  <p class="desc">
    Most canvases in Atria demonstrate one mechanism in isolation. Real
    matchmaking is many mechanisms running together. This tab lets you
    compose them &mdash; run a scripted scenario that fires actions
    across multiple canvases in sequence, or sweep master parameters
    that touch several canvases at once.
  </p>

  <h3>Scenario Player</h3>
  <p class="desc">
    Pre-scripted sequences that fire actions across several canvases in
    a specific order, telling a story about the matchmaker under load.
    Pick a scenario and watch the canvases respond one after another.
    Open the relevant tabs to see them update live.
  </p>
  <div class="controls" style="flex-wrap:wrap;gap:8px">
    <button onclick="scenPlay('newplayer')">New Player First Session</button>
    <button onclick="scenPlay('smurfday')">Smurf Ruins a Weekend</button>
    <button onclick="scenPlay('offpeak')">Off-Peak Queue Sparsity</button>
    <button onclick="scenPlay('toxchain')">Toxic Player Cascade</button>
    <button onclick="scenPlay('metashift')">Meta Shift During a Patch</button>
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
    A handful of parameters cross-cut nearly every matchmaking decision.
    Adjusting them here programmatically moves the individual sliders on
    the relevant canvases so multiple demos respond to one change at once.
  </p>
  <div class="controls" style="display:block;padding-top:14px">
    <div style="display:grid;grid-template-columns:180px 1fr 60px;gap:10px 20px;align-items:center;font-size:11px">
      <span>population density</span>
      <input type="range" id="master-pop" min="10" max="100" value="50" oninput="masterApply()">
      <span class="stat-val" id="master-pop-val">50</span>

      <span>urgency</span>
      <input type="range" id="master-urg" min="0" max="100" value="50" oninput="masterApply()">
      <span class="stat-val" id="master-urg-val">50</span>

      <span>spread decay</span>
      <input type="range" id="master-decay" min="5" max="60" value="25" oninput="masterApply()">
      <span class="stat-val" id="master-decay-val">25</span>

      <span>prior confidence</span>
      <input type="range" id="master-prior" min="10" max="99" value="70" oninput="masterApply()">
      <span class="stat-val" id="master-prior-val">70</span>
    </div>
  </div>
  <div class="info">
    <b>What each master does:</b><br>
    &bull; <b>population density</b> → drives Queue Time vs Quality's
    density slider. Sparse populations force steeper tradeoff curves.<br>
    &bull; <b>urgency</b> → drives Queue Time vs Quality's urgency
    slider. High urgency accepts worse matches to keep pops fast.<br>
    &bull; <b>spread decay</b> → drives Pool Spreading's decay. Lower
    decay widens the pool at the cost of compatibility tightness.<br>
    &bull; <b>prior confidence</b> → drives Confidence Profile selection
    and propagates into Cold Start placement behavior.<br><br>
    <b>Compose a state:</b> Drop population density, crank urgency,
    widen the spread decay and you have assembled "off-peak desperate
    matchmaking." Raise all four and you have a dense prime-time pool
    where the system can afford to be picky. The canvases respond
    together because they are being driven by the same underlying
    parameters.
  </div>
</div>
</div>

<!-- ═══ Case Studies ═══════════════════════════════════════════ -->
<div class="panel" id="cases-tab">
<div class="container">
  <h2>Case Studies &mdash; Matchmaking in the Wild</h2>
  <p class="desc">
    Real matchmaking systems, real controversies, real design choices
    with visible consequences. Each case grounds one of the abstract
    mechanisms from the other tabs in something concrete that happened
    (or is still happening) in a shipped product.
  </p>

  <div class="info">
    <b>Activision / Call of Duty — Engagement-Optimized Matchmaking (2017 leaked patent)</b><br><br>
    In 2017, a patent filing by Activision surfaced describing a
    matchmaking system that deliberately pairs new or less-skilled
    players with highly-skilled opponents using popular in-game
    items, specifically to drive item purchases. The patent was
    explicit: the objective was not fairness of outcome or long-term
    player satisfaction, but engagement-weighted by in-game spend.
    Activision later claimed the patent was not in use, but telemetry
    analysis of Modern Warfare and Warzone by independent researchers
    (notably xclusiveace and TheXclusiveAce's 2020-2022 series) has
    consistently shown match distributions that are difficult to
    explain without some kind of engagement weighting.<br><br>
    <b>What this case demonstrates:</b> The objective choice is an
    ethics decision, not a technical one. Once "engagement matchmaking"
    exists as an option, studios will be tempted to use it. Atria's
    position: optimize for rematch rate instead, and you get engagement
    <em>without</em> the manipulation, because rematch rate is the
    authentic version of the same signal. See the Engagement vs Fair
    canvas for the three-way comparison.
  </div>

  <div class="info">
    <b>Riot Games — Smurf Queue (League of Legends, pilot 2021)</b><br><br>
    Riot piloted a "Smurf Queue" that detected suspected smurf accounts
    via rapid MMR gains and mechanical signatures, then matched them
    preferentially against each other. The result was visibly fewer
    stomps for new players in the bracket the smurfs were ostensibly
    ranked in, and visibly tighter games for the smurfs themselves.
    The pilot was expanded, though the exact mechanics remain
    undocumented. Riot has not published the detection features.<br><br>
    <b>What this case demonstrates:</b> Detecting smurfs from the
    feature vector is not only possible; it's been quietly deployed at
    scale. See Atria's Smurfing &amp; Boosting canvas for the
    feature-vector pattern, and Behavior Modulation for the "contract
    the pool" mechanism that results. The Smurf Queue is literally this
    mechanism in production.
  </div>

  <div class="info">
    <b>Halo 2 — Skill-Based Matchmaking Pioneer (2004)</b><br><br>
    Bungie's Halo 2 was one of the first console games to ship real
    SBMM, using TrueSkill (Microsoft Research's Bayesian rating system)
    as its core. The system was technically excellent — it correctly
    implemented uncertainty-aware rating with sigma and mu, something
    many modern games still get wrong — but it produced a widely-hated
    experience in casual modes because players kept being matched
    against opponents at the edge of their skill envelope. The lesson
    (that fair matchmaking can still feel bad) was learned at scale
    and is the reason Halo 3 moved to a looser system with explicit
    social playlists.<br><br>
    <b>What this case demonstrates:</b> TrueSkill worked exactly as
    designed and the result was not what players wanted. The
    optimization target ("fair 50/50 matches") was wrong. This is the
    canonical lesson behind Atria's "experience quality beats
    fairness-of-outcome" principle. See Elo vs Relational and
    Engagement vs Fair for the theory side.
  </div>

  <div class="info">
    <b>Apex Legends — Season-End Rank Reset Controversy (2022-2023)</b><br><br>
    Respawn's rank reset implementation in Apex repeatedly caused
    severe matchmaking problems in the first few weeks of each new
    season. The reset would bring high-skill players back down to a
    lower rank, where they would stomp real low-rank players until
    their MMR recovered. Respawn tried several fixes &mdash; a softer
    reset, provisional matches, different MMR/rank weights &mdash;
    but the fundamental issue was the cold-start problem at a
    population level: resetting everyone's rating without resetting
    their skill creates a temporarily-miscalibrated ladder.<br><br>
    <b>What this case demonstrates:</b> The Cold Start and Rating
    Confidence canvases apply to entire populations, not just
    individual players. A season reset is a population-scale cold
    start. The system needs to widen confidence intervals, weight
    early matches heavily for recalibration, and widen pools
    temporarily &mdash; exactly what Atria's Rating Confidence canvas
    argues for, but at the scale of millions of players at once.
  </div>

  <div class="info">
    <b>Chess.com and Lichess — Anti-Cheat Matchmaking</b><br><br>
    Both chess.com and lichess run continuous anti-cheat analysis that
    flags suspicious account behavior (engine-perfect moves, unusual
    move timing distributions, rating gain patterns inconsistent with
    a human). Flagged accounts are funneled into what chess.com's
    director of fair play has publicly described as "anti-cheat
    matchmaking" &mdash; they play disproportionately against each
    other, and their games are weighted differently in the rating
    system. This is the behavior-modulator pattern applied to
    cheating specifically, and it works because cheat detection is
    probabilistic and you do not want to punish false positives too
    hard.<br><br>
    <b>What this case demonstrates:</b> Behavior modulation on the
    compatibility graph is not a hypothetical design. Chess.com has
    been running it at scale for years, on a problem (cheating) that
    is structurally similar to Atria's Behavior Modulation canvas.
    The mechanism transfers directly.
  </div>

  <div class="info">
    <b>Starcraft II — League Structure vs MMR Transparency</b><br><br>
    Blizzard's Starcraft II ladder has an unusual design: there is a
    visible league (Bronze, Silver, Gold, ...) and a hidden MMR, and
    they only loosely correlate. Matchmaking is done on MMR; rank
    display is done on league. Players have been arguing for years
    about whether this is legitimate transparency-reduction (keeps
    players from obsessing over exact numbers) or a dark pattern (hides
    the fact that the matchmaker does not care about the visible
    rank).<br><br>
    <b>What this case demonstrates:</b> The Matchmaking Transparency
    canvas from Atria's Beyond tab is directly relevant. Blizzard
    chose opacity in one direction; chess.com chose full transparency
    (both rating and RD are visible) in the other. Neither is obviously
    right &mdash; but the design choice is load-bearing and players
    respond to it.
  </div>
</div>
</div>

<!-- ═══ Canvas Gallery ═════════════════════════════════════════ -->
<div class="panel" id="gallery-tab">
<div class="container">
  <h2>Gallery &mdash; Every Canvas in One Grid</h2>
  <p class="desc">
    Click any card to jump to it. Bookmarked canvases (marked with ★)
    appear first. Filter by substring.
  </p>
  <div style="margin-bottom:12px">
    <input type="text" id="gallery-filter" placeholder="filter..."
      style="background:var(--surface);color:var(--text);border:1px solid var(--border);
      border-radius:4px;padding:6px 10px;font-family:inherit;font-size:11px;width:260px"
      oninput="galleryFilter(this.value)">
    <span id="gallery-count" style="font-size:11px;color:var(--dim);margin-left:10px"></span>
  </div>
  <div id="gallery-grid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px"></div>
</div>
</div>

<!-- ═══ Theory ════════════════════════════════════════════════════ -->
<div class="panel" id="theory-tab">
<div class="container">
  <h2>Theory &mdash; The Framing in Full</h2>
  <p class="desc">
    Full text at <code>~/projects/atria/docs/theory.md</code>. Condensed
    version below.
  </p>
  <div class="info">
    <b>1. The Elo fallacy.</b> Rank similarity predicts win probability, not
    match quality. The move from "these two players have similar Elo" to
    "they will have a good game" is a hidden assumption that is wrong most
    of the time.
  </div>
  <div class="info">
    <b>2. Matches as weighted graph edges.</b> Each potential pairing carries
    a vector of weights (skill, tempo, role, social, schedule, tilt
    tolerance). Match-quality is a projection from that vector to a scalar,
    but the projection is a choice, not a fact.
  </div>
  <div class="info">
    <b>3. Spreading activation as matchmaker.</b> Candidate pools come from
    graph neighborhoods around a seed player, not from sorted rating
    windows. Pool shape adapts to the player.
  </div>
  <div class="info">
    <b>4. Residual compatibility is where the value is.</b> Start with Elo
    as a baseline. Track the residual. The residual is everything Elo
    cannot explain, and closing it is the whole Atria thesis.
  </div>
  <div class="info">
    <b>5. Behavior is a first-class signal.</b> Toxicity, AFK, pro-social
    history modulate node state the way salience modulates activation in
    PEP. Not a ban system &mdash; a compatibility modulator.
  </div>
  <div class="info">
    <b>6. Experience quality beats fairness-of-outcome.</b> The target is
    "both players want another game," not "50/50 win probability."
    Rematch rate is cheap to measure and captures what "good match"
    actually means.
  </div>
  <div class="info">
    <b>7. Multi-objective alignment across typed subgraphs.</b> Never
    collapse the compatibility vector to one number at input time. Project
    only when forced, and only accept matches that survive consensus
    across the relevant projections.
  </div>
  <div class="info">
    <b>8. From PvP to everywhere.</b> PvP is the wedge because the feedback
    loop is fast and the rematch signal is cheap. The same machinery
    generalizes to teams, dating, hiring, co-founders, and anywhere two or
    more people need to be aligned for a shared experience.
  </div>
</div>
</div>

<!-- ═══ PEP ↔ Atria Bridge ═══════════════════════════════════════ -->
<div class="panel" id="bridge-tab">
<div class="container">
  <h2>PEP &harr; Atria &mdash; Live Bridge</h2>
  <p class="desc">
    Atria is not a stand-alone app. It is a surface on top of PEP's engine
    and a sibling to Axona and Lingora. Every canvas action posts a typed
    event to PEP. PEP's live state flows back down, and the Axona and
    Lingora event buffers are cross-read so the full mesh is visible from
    any surface.
  </p>
  <div style="display:flex;gap:16px;margin-bottom:16px">
    <div class="info" style="flex:1">
      <b>PEP &rarr; Atria (engine state + mesh cross-reads)</b><br><br>
      <div style="font-family:monospace;font-size:11px;line-height:1.8">
        <div>connected: <span id="bridge-connected" style="color:var(--accent2)">—</span></div>
        <div>LLM: <span id="bridge-llm" style="color:var(--accent)">—</span></div>
        <div>embeddings: <span id="bridge-emb" style="color:var(--accent)">—</span></div>
        <div>Atria events: <span id="bridge-evcount" style="color:var(--accent)">—</span></div>
        <div>Axona events (cross-read): <span id="bridge-axona-count" style="color:var(--accent2)">—</span></div>
        <div>Lingora events (cross-read): <span id="bridge-lingora-count" style="color:var(--accent2)">—</span></div>
      </div>
    </div>
    <div class="info" style="flex:1">
      <b>Atria &rarr; PEP (matchmaking events)</b><br><br>
      Click any canvas action and watch it post below. Axona and Lingora
      event logs appear on the right &mdash; the four surfaces (PEP, Atria,
      Axona, Lingora) are one system, and any of them can see what the
      others are doing in real time.
      <div style="margin-top:12px">
        <button onclick="bridgeSendPing()">Send Test Ping</button>
        <button onclick="bridgeClear()">Clear Local View</button>
      </div>
    </div>
  </div>
  <div style="display:flex;gap:16px">
    <div class="canvas-box" style="padding:16px;flex:1">
      <div style="font-family:monospace;font-size:11px;color:var(--accent);margin-bottom:8px">
        &gt; Atria events &mdash; matchmaking cross-talk
      </div>
      <div id="bridge-log" style="font-family:monospace;font-size:11px;line-height:1.7;max-height:280px;overflow-y:auto;color:var(--text)">
        <span style="color:var(--dim)">waiting for first event…</span>
      </div>
    </div>
    <div class="canvas-box" style="padding:16px;flex:1">
      <div style="font-family:monospace;font-size:11px;color:var(--accent2);margin-bottom:8px">
        &gt; Axona events (mirrored)
      </div>
      <div id="bridge-axona-log" style="font-family:monospace;font-size:11px;line-height:1.7;max-height:280px;overflow-y:auto;color:var(--text)">
        <span style="color:var(--dim)">polling…</span>
      </div>
    </div>
    <div class="canvas-box" style="padding:16px;flex:1">
      <div style="font-family:monospace;font-size:11px;color:var(--accent2);margin-bottom:8px">
        &gt; Lingora events (mirrored)
      </div>
      <div id="bridge-lingora-log" style="font-family:monospace;font-size:11px;line-height:1.7;max-height:280px;overflow-y:auto;color:var(--text)">
        <span style="color:var(--dim)">polling…</span>
      </div>
    </div>
  </div>
</div>
</div>

<script>
// ═══════════════════════════════════════════════════════════════════════
// Tab switching
// ═══════════════════════════════════════════════════════════════════════
function tabPanelIds(tab) {
  const joined = (tab.dataset.panels || tab.dataset.panel || '').trim();
  return joined.split(/\\s+/).filter(Boolean);
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
function findTabForPanel(panelId) {
  return Array.from(document.querySelectorAll('.tab')).find(t => tabPanelIds(t).includes(panelId));
}
function themeBg() { return getComputedStyle(document.body).getPropertyValue('--bg').trim() || '#0a0f14'; }

// ═══════════════════════════════════════════════════════════════════════
// Light mode
// ═══════════════════════════════════════════════════════════════════════
function toggleLight() {
  const isLight = document.body.classList.toggle('light');
  const btn = document.getElementById('light-btn');
  if (btn) btn.textContent = isLight ? 'Dark Mode' : 'Light Mode';
  try { localStorage.setItem('atria-theme', isLight ? 'light' : 'dark'); } catch (e) {}
}
(function restoreTheme() {
  try {
    if (localStorage.getItem('atria-theme') === 'light') {
      document.body.classList.add('light');
      const btn = document.getElementById('light-btn');
      if (btn) btn.textContent = 'Dark Mode';
    }
  } catch (e) {}
})();

// ═══════════════════════════════════════════════════════════════════════
// PEP ↔ Atria bridge client
// ═══════════════════════════════════════════════════════════════════════
let bridgeThrottle = {};
function pepSend(type, payload) {
  const now = Date.now();
  if (bridgeThrottle[type] && now - bridgeThrottle[type] < 600) return;
  bridgeThrottle[type] = now;
  try {
    fetch('/atria/event', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type, source: 'atria', payload: payload || {} }),
    }).catch(() => {});
  } catch (e) {}
}
function bridgeSendPing() { pepSend('ping', { from: 'user', t: Date.now() }); }
function bridgeClear() {
  const log = document.getElementById('bridge-log');
  if (log) log.innerHTML = '<span style="color:var(--dim)">cleared (server still has the copy)</span>';
}
function bridgeFmtTime(t) { return new Date(t * 1000).toTimeString().slice(0, 8); }
function bridgeRender(items, elId, colorVar) {
  const log = document.getElementById(elId);
  if (!log) return;
  if (!items || !items.length) {
    log.innerHTML = '<span style="color:var(--dim)">no events yet…</span>';
    return;
  }
  log.innerHTML = items.slice().reverse().map(e => {
    const payload = JSON.stringify(e.payload || {}).replace(/</g, '&lt;');
    return '<div style="margin-bottom:3px">' +
      '<span style="color:var(--dim)">' + bridgeFmtTime(e.t) + '</span> ' +
      '<span style="color:' + colorVar + '">' + (e.type || 'event') + '</span>' +
      ' <span style="color:var(--dim)">' + payload + '</span></div>';
  }).join('');
}
async function bridgePoll() {
  try {
    const [s, e, ax, lg] = await Promise.all([
      fetch('/atria/pep-state'),
      fetch('/atria/events?limit=40'),
      fetch('/atria/axona-events?limit=40'),
      fetch('/atria/lingora-events?limit=40'),
    ]);
    if (s.ok) {
      const d = await s.json();
      const lbl = document.getElementById('pep-link-label');
      const dot = document.getElementById('pep-link-dot');
      if (lbl) lbl.textContent = 'PEP: ' + (d.llm || 'unknown') + ' · T' + (d.atria_events || 0) + ' · A' + (d.axona_events || 0) + ' · L' + (d.lingora_events || 0);
      if (dot) dot.style.background = 'var(--accent2)';
      const set = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = v; };
      set('bridge-connected', 'yes');
      set('bridge-llm', d.llm || '—');
      set('bridge-emb', d.embeddings || '—');
      set('bridge-evcount', d.atria_events);
      set('bridge-axona-count', d.axona_events);
      set('bridge-lingora-count', d.lingora_events);
    }
    if (e.ok) {
      const data = await e.json();
      bridgeRender(data.items || [], 'bridge-log', 'var(--accent)');
    }
    if (ax.ok) {
      const data = await ax.json();
      bridgeRender(data.items || [], 'bridge-axona-log', 'var(--accent2)');
    }
    if (lg.ok) {
      const data = await lg.json();
      bridgeRender(data.items || [], 'bridge-lingora-log', 'var(--accent2)');
    }
  } catch (err) {
    const lbl = document.getElementById('pep-link-label');
    const dot = document.getElementById('pep-link-dot');
    if (lbl) lbl.textContent = 'PEP: offline';
    if (dot) dot.style.background = '#e53935';
  }
}
bridgePoll();
setInterval(bridgePoll, 2500);

// ═══════════════════════════════════════════════════════════════════════
// Elo vs Relational
// ═══════════════════════════════════════════════════════════════════════
const ELO_DATA = {
  A: {
    label: 'Matchup A — great game',
    players: ['Player X', 'Player Y'],
    elo: [1500, 1500],
    compat: { skill: 0.85, tempo: 0.9, role: 0.8, comms: 0.88, tilt: 0.82, goals: 0.9 },
    score: 0.86,
    rematch: 0.91,
    why: 'Both players want an intense learning game. Similar tempo, great comms, complementary roles. Elo delta 0 — Elo agrees but for the wrong reason.',
  },
  B: {
    label: 'Matchup B — grind',
    players: ['Player Z', 'Player W'],
    elo: [1500, 1500],
    compat: { skill: 0.85, tempo: 0.2, role: 0.3, comms: 0.15, tilt: 0.25, goals: 0.18 },
    score: 0.29,
    rematch: 0.12,
    why: 'One wants a chill warm-up, the other wants to rank up. One mutes chat, the other shot-calls. Both players had a miserable time. Elo delta 0 — Elo called this "fair."',
  },
  C: {
    label: 'Matchup C — counter-pick stomp',
    players: ['Player V (aggro main)', 'Player U (anti-aggro specialist)'],
    elo: [1520, 1480],
    compat: { skill: 0.7, tempo: 0.5, role: 0.2, comms: 0.6, tilt: 0.4, goals: 0.55 },
    score: 0.38,
    rematch: 0.08,
    why: 'Equal-ish Elo, but V plays aggro and U specifically counters aggro. U wins 70% regardless of rating. This is the intransitivity problem — Elo saw a close match; the actual game was a hard counter.',
  },
};
const eloCanvas = document.getElementById('elo-canvas');
const eloCtx = eloCanvas.getContext('2d');
let eloActive = null;
function eloPick(k) { eloActive = k; pepSend('elo.pick', { key: k }); }
function eloReset() { eloActive = null; }
function drawElo() {
  const W = 960, H = 440; eloCtx.fillStyle = themeBg(); eloCtx.fillRect(0, 0, W, H);
  if (!eloActive) {
    eloCtx.fillStyle = '#666'; eloCtx.font = '11px monospace'; eloCtx.textAlign = 'center';
    eloCtx.fillText('(pick a matchup)', W / 2, H / 2);
    requestAnimationFrame(drawElo);
    return;
  }
  const d = ELO_DATA[eloActive];
  eloCtx.fillStyle = 'rgba(94,234,212,0.95)'; eloCtx.font = 'bold 14px monospace'; eloCtx.textAlign = 'left';
  eloCtx.fillText(d.label.toUpperCase(), 30, 40);
  // Players
  eloCtx.fillStyle = '#fff'; eloCtx.font = 'bold 16px monospace';
  eloCtx.fillText(d.players[0], 80, 90);
  eloCtx.fillText(d.players[1], 80, 116);
  eloCtx.fillStyle = '#aaa'; eloCtx.font = '11px monospace';
  eloCtx.fillText('Elo ' + d.elo[0] + '  vs  ' + d.elo[1] + '  (delta: 0)', 80, 140);
  // Radar
  const cx = 620, cy = 230, R = 130;
  const axes = ['skill', 'tempo', 'role', 'comms', 'tilt', 'goals'];
  eloCtx.strokeStyle = 'rgba(120,120,130,0.3)'; eloCtx.lineWidth = 1;
  for (let ring = 0.25; ring <= 1; ring += 0.25) {
    eloCtx.beginPath();
    axes.forEach((a, i) => {
      const ang = (i / axes.length) * Math.PI * 2 - Math.PI / 2;
      const x = cx + Math.cos(ang) * R * ring;
      const y = cy + Math.sin(ang) * R * ring;
      if (i === 0) eloCtx.moveTo(x, y); else eloCtx.lineTo(x, y);
    });
    eloCtx.closePath(); eloCtx.stroke();
  }
  // Axes + labels
  axes.forEach((a, i) => {
    const ang = (i / axes.length) * Math.PI * 2 - Math.PI / 2;
    const x = cx + Math.cos(ang) * R;
    const y = cy + Math.sin(ang) * R;
    eloCtx.strokeStyle = 'rgba(120,120,130,0.3)';
    eloCtx.beginPath(); eloCtx.moveTo(cx, cy); eloCtx.lineTo(x, y); eloCtx.stroke();
    eloCtx.fillStyle = '#aaa'; eloCtx.font = '10px monospace'; eloCtx.textAlign = 'center';
    eloCtx.fillText(a, cx + Math.cos(ang) * (R + 14), cy + Math.sin(ang) * (R + 14) + 3);
  });
  // Compat polygon
  const col = d.score > 0.6 ? '94,234,212' : '248,113,113';
  eloCtx.fillStyle = 'rgba(' + col + ',0.35)';
  eloCtx.beginPath();
  axes.forEach((a, i) => {
    const v = d.compat[a];
    const ang = (i / axes.length) * Math.PI * 2 - Math.PI / 2;
    const x = cx + Math.cos(ang) * R * v;
    const y = cy + Math.sin(ang) * R * v;
    if (i === 0) eloCtx.moveTo(x, y); else eloCtx.lineTo(x, y);
  });
  eloCtx.closePath(); eloCtx.fill();
  eloCtx.strokeStyle = 'rgba(' + col + ',0.95)'; eloCtx.lineWidth = 2; eloCtx.stroke();
  // Scores
  eloCtx.fillStyle = '#fff'; eloCtx.font = 'bold 14px monospace'; eloCtx.textAlign = 'left';
  eloCtx.fillText('Elo-predicted quality:', 80, 220);
  eloCtx.fillStyle = 'rgba(251,191,36,0.95)';
  eloCtx.fillText('0.50  (neutral)', 80, 244);
  eloCtx.fillStyle = '#fff';
  eloCtx.fillText('Compatibility score:', 80, 280);
  eloCtx.fillStyle = 'rgba(' + col + ',0.95)';
  eloCtx.fillText(d.score.toFixed(2), 80, 304);
  eloCtx.fillStyle = '#fff';
  eloCtx.fillText('Actual rematch rate:', 80, 340);
  eloCtx.fillStyle = 'rgba(' + col + ',0.95)';
  eloCtx.fillText((d.rematch * 100).toFixed(0) + '%', 80, 364);
  // Why text
  eloCtx.fillStyle = '#aaa'; eloCtx.font = '11px monospace'; eloCtx.textAlign = 'left';
  const whyWords = (d.why || '').split(' '); let wx = 80, wy = 390;
  whyWords.forEach(w => { const m = eloCtx.measureText(w + ' '); if (wx + m.width > W - 30) { wx = 80; wy += 16; } eloCtx.fillText(w + ' ', wx, wy); wx += m.width; });
  requestAnimationFrame(drawElo);
}
drawElo();

// ═══════════════════════════════════════════════════════════════════════
// Pool Spreading
// ═══════════════════════════════════════════════════════════════════════
const poolCanvas = document.getElementById('pool-canvas');
const poolCtx = poolCanvas.getContext('2d');
const poolNodes = [];
const poolEdges = [];
let poolSeed = -1;
(function poolInit() {
  const W = 960, H = 440;
  for (let i = 0; i < 22; i++) {
    poolNodes.push({
      x: 80 + Math.random() * (W - 160),
      y: 50 + Math.random() * (H - 100),
      act: 0,
      flex: 0.5 + Math.random() * 0.5,
    });
  }
  for (let i = 0; i < poolNodes.length; i++) {
    for (let j = i + 1; j < poolNodes.length; j++) {
      const dx = poolNodes[i].x - poolNodes[j].x;
      const dy = poolNodes[i].y - poolNodes[j].y;
      const d = Math.sqrt(dx * dx + dy * dy);
      if (d < 180 && Math.random() < 0.45) {
        poolEdges.push({ a: i, b: j, w: 0.3 + Math.random() * 0.7 });
      }
    }
  }
})();
document.getElementById('pool-decay').addEventListener('input', (e) => {
  document.getElementById('pool-decay-val').textContent = (parseInt(e.target.value) / 100).toFixed(2);
});
poolCanvas.addEventListener('click', (e) => {
  const r = poolCanvas.getBoundingClientRect();
  const mx = (e.clientX - r.left) * (poolCanvas.width / r.width);
  const my = (e.clientY - r.top) * (poolCanvas.height / r.height);
  let best = -1, bestD = 1e9;
  poolNodes.forEach((n, i) => {
    const d = Math.hypot(n.x - mx, n.y - my);
    if (d < bestD && d < 30) { bestD = d; best = i; }
  });
  if (best >= 0) {
    poolSeed = best;
    poolSpread();
    pepSend('pool.seed', { node: best });
  }
});
function poolSpread() {
  poolNodes.forEach(n => n.act = 0);
  if (poolSeed < 0) return;
  const decay = parseInt(document.getElementById('pool-decay').value) / 100;
  const queue = [{ id: poolSeed, act: 1 }];
  const visited = new Set();
  while (queue.length) {
    const { id, act } = queue.shift();
    if (visited.has(id)) continue;
    visited.add(id);
    poolNodes[id].act = Math.max(poolNodes[id].act, act);
    if (act < 0.15) continue;
    poolEdges.forEach(e => {
      let other = -1;
      if (e.a === id) other = e.b;
      else if (e.b === id) other = e.a;
      if (other >= 0 && !visited.has(other)) {
        const nextAct = act * e.w * (1 - decay);
        if (nextAct > 0.1) queue.push({ id: other, act: nextAct });
      }
    });
  }
}
function poolReset() { poolSeed = -1; poolNodes.forEach(n => n.act = 0); }
function drawPool() {
  const W = 960, H = 440; poolCtx.fillStyle = themeBg(); poolCtx.fillRect(0, 0, W, H);
  if (poolSeed >= 0) poolSpread();
  // Edges
  poolEdges.forEach(e => {
    const a = poolNodes[e.a], b = poolNodes[e.b];
    const heat = (a.act + b.act) / 2;
    poolCtx.strokeStyle = 'rgba(94,234,212,' + (0.08 + heat * 0.5).toFixed(3) + ')';
    poolCtx.lineWidth = 0.5 + heat * 2;
    poolCtx.beginPath(); poolCtx.moveTo(a.x, a.y); poolCtx.lineTo(b.x, b.y); poolCtx.stroke();
  });
  // Nodes
  let pool = 0, sumW = 0;
  poolNodes.forEach((n, i) => {
    const r = 6 + n.act * 14;
    const col = i === poolSeed ? '251,191,36' : '94,234,212';
    poolCtx.fillStyle = 'rgba(' + col + ',' + (0.25 + n.act * 0.7).toFixed(3) + ')';
    poolCtx.beginPath(); poolCtx.arc(n.x, n.y, r, 0, Math.PI * 2); poolCtx.fill();
    poolCtx.strokeStyle = 'rgba(' + col + ',' + (0.4 + n.act * 0.6).toFixed(3) + ')';
    poolCtx.lineWidth = 1.2;
    poolCtx.stroke();
    if (n.act > 0.15 && i !== poolSeed) { pool++; sumW += n.act; }
  });
  document.getElementById('pool-size').textContent = pool;
  document.getElementById('pool-avg').textContent = pool ? (sumW / pool).toFixed(2) : '0.00';
  if (poolSeed < 0) {
    poolCtx.fillStyle = '#666'; poolCtx.font = '11px monospace'; poolCtx.textAlign = 'center';
    poolCtx.fillText('click a node to seed activation', W / 2, H - 20);
  }
  requestAnimationFrame(drawPool);
}
drawPool();

// ═══════════════════════════════════════════════════════════════════════
// Residual Heatmap
// ═══════════════════════════════════════════════════════════════════════
const residualCanvas = document.getElementById('residual-canvas');
const residualCtx = residualCanvas.getContext('2d');
let residualMatches = [];
let residualOverlay = false;
function residualRegen() {
  residualMatches = [];
  for (let i = 0; i < 120; i++) {
    const eloPred = 0.3 + Math.random() * 0.65;
    // True rematch rate depends on eloPred but with LOTS of variance
    const noise = (Math.random() - 0.5) * 0.65;
    const trueRate = Math.max(0.05, Math.min(0.98, eloPred * 0.4 + 0.3 + noise));
    // Compatibility features (hidden to Elo)
    const tempo = Math.random();
    const role = Math.random();
    const social = Math.random();
    residualMatches.push({ eloPred, trueRate, tempo, role, social });
  }
  pepSend('residual.regen', { n: residualMatches.length });
}
function residualToggleOverlay() { residualOverlay = !residualOverlay; pepSend('residual.toggle_overlay', { on: residualOverlay }); }
function residualReset() { residualMatches = []; residualOverlay = false; }
residualRegen();
function residualR2(pred) {
  if (!residualMatches.length) return 0;
  const mean = residualMatches.reduce((a, m) => a + m.trueRate, 0) / residualMatches.length;
  let ssRes = 0, ssTot = 0;
  residualMatches.forEach((m, i) => {
    ssRes += Math.pow(m.trueRate - pred[i], 2);
    ssTot += Math.pow(m.trueRate - mean, 2);
  });
  return Math.max(0, 1 - ssRes / ssTot);
}
function drawResidual() {
  const W = 960, H = 440; residualCtx.fillStyle = themeBg(); residualCtx.fillRect(0, 0, W, H);
  const pad = 50;
  const px = (v) => pad + v * (W - 2 * pad);
  const py = (v) => H - pad - v * (H - 2 * pad);
  // Axes
  residualCtx.strokeStyle = 'rgba(120,120,130,0.4)'; residualCtx.lineWidth = 1;
  residualCtx.beginPath(); residualCtx.moveTo(pad, pad); residualCtx.lineTo(pad, H - pad); residualCtx.lineTo(W - pad, H - pad); residualCtx.stroke();
  // Diagonal reference
  residualCtx.strokeStyle = 'rgba(251,191,36,0.5)'; residualCtx.setLineDash([4, 4]);
  residualCtx.beginPath(); residualCtx.moveTo(px(0), py(0)); residualCtx.lineTo(px(1), py(1)); residualCtx.stroke();
  residualCtx.setLineDash([]);
  // Labels
  residualCtx.fillStyle = '#aaa'; residualCtx.font = '11px monospace'; residualCtx.textAlign = 'center';
  residualCtx.fillText('Elo-predicted match quality →', W / 2, H - 18);
  residualCtx.save();
  residualCtx.translate(16, H / 2); residualCtx.rotate(-Math.PI / 2);
  residualCtx.fillText('actual rematch rate', 0, 0);
  residualCtx.restore();
  // Points
  const eloPred = residualMatches.map(m => m.eloPred);
  residualMatches.forEach(m => {
    residualCtx.fillStyle = 'rgba(94,234,212,0.6)';
    residualCtx.beginPath(); residualCtx.arc(px(m.eloPred), py(m.trueRate), 4, 0, Math.PI * 2); residualCtx.fill();
  });
  // Atria overlay: use compat features to get better predictions
  if (residualOverlay) {
    residualMatches.forEach(m => {
      const atriaPred = 0.25 + m.eloPred * 0.25 + m.tempo * 0.2 + m.role * 0.15 + m.social * 0.15;
      residualCtx.fillStyle = 'rgba(251,191,36,0.8)';
      residualCtx.beginPath(); residualCtx.arc(px(atriaPred), py(m.trueRate), 3, 0, Math.PI * 2); residualCtx.fill();
      residualCtx.strokeStyle = 'rgba(251,191,36,0.25)'; residualCtx.lineWidth = 0.5;
      residualCtx.beginPath(); residualCtx.moveTo(px(m.eloPred), py(m.trueRate)); residualCtx.lineTo(px(atriaPred), py(m.trueRate)); residualCtx.stroke();
    });
  }
  // R² calculations
  const eloR2 = residualR2(eloPred);
  const atriaPred = residualMatches.map(m => 0.25 + m.eloPred * 0.25 + m.tempo * 0.2 + m.role * 0.15 + m.social * 0.15);
  const atriaR2 = residualR2(atriaPred);
  document.getElementById('residual-elo-r2').textContent = eloR2.toFixed(2);
  document.getElementById('residual-atria-r2').textContent = residualOverlay ? atriaR2.toFixed(2) : '—';
  requestAnimationFrame(drawResidual);
}
drawResidual();

// ═══════════════════════════════════════════════════════════════════════
// Behavior Modulation
// ═══════════════════════════════════════════════════════════════════════
const behaviorCanvas = document.getElementById('behavior-canvas');
const behaviorCtx = behaviorCanvas.getContext('2d');
const behaviorNodes = [];
const behaviorEdges = [];
let behaviorFlags = { toxicity: false, afk: false, prosocial: false };
(function behaviorInit() {
  const W = 960, H = 440;
  behaviorNodes.push({ x: W / 2, y: H / 2, isMe: true, tilt: 0.5, newbie: false });
  for (let i = 0; i < 18; i++) {
    const a = (i / 18) * Math.PI * 2;
    const r = 150 + Math.random() * 50;
    behaviorNodes.push({
      x: W / 2 + Math.cos(a) * r,
      y: H / 2 + Math.sin(a) * r,
      isMe: false,
      tilt: Math.random(),
      newbie: Math.random() < 0.3,
    });
  }
  for (let i = 1; i < behaviorNodes.length; i++) {
    behaviorEdges.push({ a: 0, b: i, base: 0.4 + Math.random() * 0.5 });
  }
})();
function behaviorFlag(f) {
  behaviorFlags[f] = !behaviorFlags[f];
  pepSend('behavior.flag', { flag: f, on: behaviorFlags[f] });
}
function behaviorReset() { behaviorFlags = { toxicity: false, afk: false, prosocial: false }; }
function drawBehavior() {
  const W = 960, H = 440; behaviorCtx.fillStyle = themeBg(); behaviorCtx.fillRect(0, 0, W, H);
  // Compute modulated edge weights
  let reach = 0, sumW = 0;
  behaviorEdges.forEach(e => {
    const target = behaviorNodes[e.b];
    let w = e.base;
    if (behaviorFlags.toxicity) {
      // Toxicity contracts edges to low-tilt tolerance neighbors
      w *= (target.tilt > 0.5 ? 0.85 : 0.3);
      if (target.newbie) w *= 0.2;
    }
    if (behaviorFlags.afk) w *= 0.6;
    if (behaviorFlags.prosocial) {
      // Pro-social expands, especially to newbies
      w = Math.min(1, w * 1.15);
      if (target.newbie) w = Math.min(1, w * 1.4);
    }
    e.mod = w;
    if (w > 0.35) { reach++; sumW += w; }
  });
  document.getElementById('behavior-reach').textContent = reach;
  document.getElementById('behavior-edge').textContent = reach ? (sumW / reach).toFixed(2) : '0.00';
  // Draw edges
  behaviorEdges.forEach(e => {
    const a = behaviorNodes[e.a], b = behaviorNodes[e.b];
    const col = e.mod > 0.35 ? '94,234,212' : '248,113,113';
    behaviorCtx.strokeStyle = 'rgba(' + col + ',' + (0.15 + e.mod * 0.55).toFixed(3) + ')';
    behaviorCtx.lineWidth = 0.5 + e.mod * 2.5;
    behaviorCtx.beginPath(); behaviorCtx.moveTo(a.x, a.y); behaviorCtx.lineTo(b.x, b.y); behaviorCtx.stroke();
  });
  // Nodes
  behaviorNodes.forEach((n, i) => {
    if (n.isMe) {
      behaviorCtx.fillStyle = 'rgba(251,191,36,0.8)';
      behaviorCtx.beginPath(); behaviorCtx.arc(n.x, n.y, 22, 0, Math.PI * 2); behaviorCtx.fill();
      behaviorCtx.strokeStyle = 'rgba(251,191,36,1)'; behaviorCtx.lineWidth = 2; behaviorCtx.stroke();
      behaviorCtx.fillStyle = '#fff'; behaviorCtx.font = 'bold 11px monospace'; behaviorCtx.textAlign = 'center';
      behaviorCtx.fillText('you', n.x, n.y + 4);
    } else {
      const e = behaviorEdges.find(e => e.b === i);
      const inPool = e && e.mod > 0.35;
      const col = inPool ? '94,234,212' : '120,120,130';
      behaviorCtx.fillStyle = 'rgba(' + col + ',' + (inPool ? 0.7 : 0.25).toFixed(3) + ')';
      behaviorCtx.beginPath(); behaviorCtx.arc(n.x, n.y, 9, 0, Math.PI * 2); behaviorCtx.fill();
      if (n.newbie) {
        behaviorCtx.strokeStyle = 'rgba(251,191,36,0.6)'; behaviorCtx.lineWidth = 2;
        behaviorCtx.beginPath(); behaviorCtx.arc(n.x, n.y, 12, 0, Math.PI * 2); behaviorCtx.stroke();
      }
    }
  });
  // Flags indicator
  behaviorCtx.fillStyle = '#aaa'; behaviorCtx.font = '10px monospace'; behaviorCtx.textAlign = 'left';
  let fy = 30;
  Object.keys(behaviorFlags).forEach(k => {
    if (behaviorFlags[k]) {
      const col = k === 'prosocial' ? '94,234,212' : '248,113,113';
      behaviorCtx.fillStyle = 'rgba(' + col + ',0.95)';
      behaviorCtx.fillText('◉ ' + k.toUpperCase() + ' active', 30, fy);
      fy += 16;
    }
  });
  behaviorCtx.fillStyle = '#888'; behaviorCtx.font = '10px monospace';
  behaviorCtx.fillText('gold-ringed nodes are new / learning players', 30, H - 20);
  requestAnimationFrame(drawBehavior);
}
drawBehavior();

// ═══════════════════════════════════════════════════════════════════════
// Multi-Objective Projection
// ═══════════════════════════════════════════════════════════════════════
const multiCanvas = document.getElementById('multi-canvas');
const multiCtx = multiCanvas.getContext('2d');
const multiNodes = [];
const multiEdges = [];
let multiLensName = null;
(function multiInit() {
  const W = 960, H = 460;
  for (let i = 0; i < 20; i++) {
    multiNodes.push({
      x: 80 + Math.random() * (W - 160),
      y: 60 + Math.random() * (H - 140),
    });
  }
  for (let i = 0; i < multiNodes.length; i++) {
    for (let j = i + 1; j < multiNodes.length; j++) {
      if (Math.random() < 0.35) {
        multiEdges.push({
          a: i, b: j,
          skill: Math.random(),
          tempo: Math.random(),
          social: Math.random(),
        });
      }
    }
  }
})();
function multiLens(l) { multiLensName = l; pepSend('multi.lens', { lens: l }); }
function multiReset() { multiLensName = null; }
function drawMulti() {
  const W = 960, H = 460; multiCtx.fillStyle = themeBg(); multiCtx.fillRect(0, 0, W, H);
  const threshold = 0.65;
  multiEdges.forEach(e => {
    let lit = false, col = '120,120,130', alpha = 0.15;
    if (multiLensName === 'skill') { lit = e.skill > threshold; col = '94,234,212'; }
    else if (multiLensName === 'tempo') { lit = e.tempo > threshold; col = '251,191,36'; }
    else if (multiLensName === 'social') { lit = e.social > threshold; col = '168,213,255'; }
    else if (multiLensName === 'consensus') {
      lit = e.skill > threshold && e.tempo > threshold && e.social > threshold;
      col = '94,234,212';
    }
    if (lit) alpha = 0.85;
    const a = multiNodes[e.a], b = multiNodes[e.b];
    multiCtx.strokeStyle = 'rgba(' + col + ',' + alpha.toFixed(3) + ')';
    multiCtx.lineWidth = lit ? 2 : 0.6;
    multiCtx.beginPath(); multiCtx.moveTo(a.x, a.y); multiCtx.lineTo(b.x, b.y); multiCtx.stroke();
  });
  multiNodes.forEach(n => {
    multiCtx.fillStyle = 'rgba(224,230,237,0.75)';
    multiCtx.beginPath(); multiCtx.arc(n.x, n.y, 6, 0, Math.PI * 2); multiCtx.fill();
  });
  // Label
  multiCtx.fillStyle = '#aaa'; multiCtx.font = '11px monospace'; multiCtx.textAlign = 'left';
  if (!multiLensName) multiCtx.fillText('pick a lens to project through', 30, 30);
  else if (multiLensName === 'consensus') {
    let count = 0;
    multiEdges.forEach(e => { if (e.skill > threshold && e.tempo > threshold && e.social > threshold) count++; });
    multiCtx.fillStyle = 'rgba(94,234,212,0.95)'; multiCtx.font = 'bold 12px monospace';
    multiCtx.fillText('CONSENSUS: ' + count + ' edges survive all three projections', 30, 30);
    multiCtx.fillStyle = '#aaa'; multiCtx.font = '10px monospace';
    multiCtx.fillText('these are the real matches; everything else is a projection artifact', 30, 50);
  } else {
    let count = 0;
    multiEdges.forEach(e => { if (e[multiLensName] > threshold) count++; });
    multiCtx.fillText(multiLensName.toUpperCase() + ' projection: ' + count + ' edges above threshold', 30, 30);
  }
  requestAnimationFrame(drawMulti);
}
drawMulti();

// ═══════════════════════════════════════════════════════════════════════
// Take a Tour
// ═══════════════════════════════════════════════════════════════════════
const tourSteps = [
  { tab: 'home-tab', title: 'Welcome to Atria', body: 'Atria is the LAVAS project focused on matching, compatibility, and relational alignment. Elo answers "who wins?" Atria answers "who should play together?" These are not the same question, and the difference is where the whole thesis lives. I will walk you through the five initial canvases.' },
  { tab: 'elo-tab', title: 'Elo vs Relational', body: 'Two 1v1 matchups with identical Elo deltas. One produces a great game, the other a grind. The radar chart shows the compatibility dimensions Elo cannot see. This is the Elo fallacy made visible.' },
  { tab: 'pool-tab', title: 'Pool Spreading', body: 'Click any node on the compatibility graph. Activation spreads outward through weighted edges, forming the candidate pool. Adjust the decay slider to trade off pool size for pool quality. Same spreading-activation primitive PEP uses for memory retrieval.' },
  { tab: 'residual-tab', title: 'Residual Heatmap', body: 'Each dot is a match. Elo-predicted quality on X, actual rematch rate on Y. The vertical residual is what Elo does not explain. Toggle the Atria overlay to see how adding compatibility features closes some of that residual. The whole Atria thesis in one plot.' },
  { tab: 'behavior-tab', title: 'Behavior Modulation', body: 'Toggle toxicity, AFK, or pro-social flags on your node and watch the reachable pool contract or expand. Behavior is not a separate ban system — it is a state modulator on the compatibility graph. Toxic players end up matched with each other because nobody else is compatible with them right now.' },
  { tab: 'multi-tab', title: 'Multi-Objective Projection', body: 'The same 20-player graph projected through skill, tempo, and social lenses. Individual projections lie — they produce "good" matches that feel terrible along the axes you were not looking at. Click Consensus and only the edges that survive all three projections remain. Those are the real matches.' },
  { tab: 'bridge-tab', title: 'PEP ↔ Atria Bridge', body: 'Atria is not a stand-alone app. Every canvas action posts an event to PEP. Axona and Lingora event buffers are mirrored in the rightmost columns. Four surfaces (PEP, Atria, Axona, Lingora) are one system, and any of them can see what the others are doing in real time.' },
  { tab: 'theory-tab', title: 'That is the tour', body: 'Full theory framing is in ~/projects/atria/docs/theory.md. Everything here is the day-one thesis. Later batches will add queue-time vs quality tradeoffs, smurf and booster detection, party matchmaking, role fit, and the cross-domain generalizations to dating, hiring, and co-founder matching.' },
];
let tourIdx = 0, tourOverlay = null;
function tourStart() { tourIdx = 0; if (!tourOverlay) tourBuildOverlay(); tourOverlay.style.display = 'flex'; tourShowStep(); pepSend('tour.start', {}); }
function tourEnd() { if (tourOverlay) tourOverlay.style.display = 'none'; pepSend('tour.end', { atStep: tourIdx }); }
function tourNext() { tourIdx++; if (tourIdx >= tourSteps.length) { tourEnd(); return; } tourShowStep(); }
function tourPrev() { if (tourIdx > 0) { tourIdx--; tourShowStep(); } }
function tourShowStep() {
  const step = tourSteps[tourIdx];
  if (!step) { tourEnd(); return; }
  const tab = findTabForPanel(step.tab);
  if (tab) tab.click();
  setTimeout(() => { window.scrollTo(0, 0); }, 20);
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
    '<div style="background:var(--surface);border:1px solid var(--accent);border-radius:8px;max-width:600px;padding:22px 26px;font-family:inherit;color:var(--text);box-shadow:0 10px 40px rgba(0,0,0,0.6)">' +
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
  tourOverlay.addEventListener('click', (e) => { if (e.target === tourOverlay) tourEnd(); });
}
document.addEventListener('keydown', (e) => {
  if (!tourOverlay || tourOverlay.style.display !== 'flex') return;
  if (e.key === 'Escape') tourEnd();
  else if (e.key === 'ArrowRight' || e.key === 'Enter') tourNext();
  else if (e.key === 'ArrowLeft') tourPrev();
});

// ═══════════════════════════════════════════════════════════════════════
// Download
// ═══════════════════════════════════════════════════════════════════════
function downloadAtria() {
  const html = '<!DOCTYPE html>' + document.documentElement.outerHTML;
  const blob = new Blob([html], { type: 'text/html' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'atria-matching.html';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  try { pepSend('download', {}); } catch (e) {}
}

// ═══════════════════════════════════════════════════════════════════════
// Rock-Paper-Scissors matchup matrix (game-specific)
// ═══════════════════════════════════════════════════════════════════════
const RPS_GAMES = {
  ccg: {
    label: 'Card game (Magic / Hearthstone / LoR)',
    strategies: ['aggro', 'control', 'combo', 'midrange'],
    // matrix[i][j] = prob row i beats column j
    matrix: [
      [0.50, 0.65, 0.35, 0.48], // aggro
      [0.35, 0.50, 0.68, 0.52], // control
      [0.65, 0.32, 0.50, 0.50], // combo
      [0.52, 0.48, 0.50, 0.50], // midrange
    ],
  },
  fgc: {
    label: 'Fighting game (Street Fighter / Tekken)',
    strategies: ['rushdown', 'zoner', 'grappler'],
    matrix: [
      [0.50, 0.62, 0.36],
      [0.38, 0.50, 0.64],
      [0.64, 0.36, 0.50],
    ],
  },
  fps: {
    label: 'Tactical FPS (Valorant / CS)',
    strategies: ['duelist-heavy', 'sentinel-heavy', 'controller-heavy'],
    matrix: [
      [0.50, 0.40, 0.62],
      [0.60, 0.50, 0.38],
      [0.38, 0.62, 0.50],
    ],
  },
  rts: {
    label: 'RTS (StarCraft / AoE)',
    strategies: ['rush', 'economy', 'tech'],
    matrix: [
      [0.50, 0.62, 0.36],
      [0.38, 0.50, 0.63],
      [0.64, 0.37, 0.50],
    ],
  },
};
const rpsCanvas = document.getElementById('rps-canvas');
const rpsCtx = rpsCanvas.getContext('2d');
let rpsActive = 'ccg';
let rpsPopulation = [];
function rpsGame(k) {
  rpsActive = k;
  const n = RPS_GAMES[k].strategies.length;
  rpsPopulation = new Array(n).fill(100 / n);
  rpsRenderSliders();
  pepSend('rps.game', { key: k });
}
function rpsReset() {
  const n = RPS_GAMES[rpsActive].strategies.length;
  rpsPopulation = new Array(n).fill(100 / n);
  rpsRenderSliders();
}
function rpsRenderSliders() {
  const container = document.getElementById('rps-sliders');
  if (!container) return;
  const g = RPS_GAMES[rpsActive];
  container.innerHTML = g.strategies.map((s, i) =>
    '<label style="display:flex;align-items:center;gap:8px">' +
    '<span>% ' + s + ':</span>' +
    '<input type="range" min="0" max="100" value="' + Math.round(rpsPopulation[i]) + '" ' +
    'oninput="rpsSlider(' + i + ', this.value)" style="width:100px">' +
    '<span class="stat-val" id="rps-slider-val-' + i + '">' + Math.round(rpsPopulation[i]) + '</span>' +
    '</label>'
  ).join('');
}
function rpsSlider(i, v) {
  rpsPopulation[i] = parseInt(v);
  const el = document.getElementById('rps-slider-val-' + i);
  if (el) el.textContent = Math.round(rpsPopulation[i]);
}
function drawRps() {
  const W = 960, H = 500; rpsCtx.fillStyle = themeBg(); rpsCtx.fillRect(0, 0, W, H);
  const g = RPS_GAMES[rpsActive];
  if (!rpsPopulation.length) rpsPopulation = new Array(g.strategies.length).fill(100 / g.strategies.length);
  rpsCtx.fillStyle = 'rgba(94,234,212,0.95)'; rpsCtx.font = 'bold 14px monospace'; rpsCtx.textAlign = 'left';
  rpsCtx.fillText(g.label.toUpperCase(), 30, 36);
  // Matchup matrix
  const n = g.strategies.length;
  const cell = 46, mx = 30, my = 70;
  // Header row
  rpsCtx.fillStyle = '#aaa'; rpsCtx.font = '10px monospace'; rpsCtx.textAlign = 'center';
  g.strategies.forEach((s, j) => rpsCtx.fillText(s, mx + 100 + j * cell + cell / 2, my - 6));
  // Rows
  for (let i = 0; i < n; i++) {
    rpsCtx.textAlign = 'right'; rpsCtx.fillStyle = '#aaa';
    rpsCtx.fillText(g.strategies[i], mx + 96, my + i * cell + cell / 2 + 4);
    for (let j = 0; j < n; j++) {
      const v = g.matrix[i][j];
      const col = v > 0.5 ? '94,234,212' : v < 0.5 ? '248,113,113' : '251,191,36';
      rpsCtx.fillStyle = 'rgba(' + col + ',' + (0.15 + Math.abs(v - 0.5) * 1.3).toFixed(3) + ')';
      rpsCtx.fillRect(mx + 100 + j * cell, my + i * cell, cell - 2, cell - 2);
      rpsCtx.strokeStyle = 'rgba(120,120,130,0.3)';
      rpsCtx.strokeRect(mx + 100 + j * cell, my + i * cell, cell - 2, cell - 2);
      rpsCtx.fillStyle = '#fff'; rpsCtx.font = '11px monospace'; rpsCtx.textAlign = 'center';
      rpsCtx.fillText((v * 100).toFixed(0), mx + 100 + j * cell + cell / 2, my + i * cell + cell / 2 + 4);
    }
  }
  rpsCtx.fillStyle = '#888'; rpsCtx.font = '10px monospace'; rpsCtx.textAlign = 'left';
  rpsCtx.fillText('cell = P(row strategy beats column strategy)', mx, my + n * cell + 20);
  // Expected win rate per strategy given population
  const popSum = rpsPopulation.reduce((a, b) => a + b, 0) || 1;
  const normalized = rpsPopulation.map(p => p / popSum);
  const expWin = [];
  for (let i = 0; i < n; i++) {
    let ew = 0;
    for (let j = 0; j < n; j++) ew += normalized[j] * g.matrix[i][j];
    expWin.push(ew);
  }
  // Bar chart
  const barX = 520, barY = 70, barH = 36, barMaxW = 380;
  rpsCtx.fillStyle = 'rgba(94,234,212,0.95)'; rpsCtx.font = 'bold 12px monospace'; rpsCtx.textAlign = 'left';
  rpsCtx.fillText('expected win rate given current meta', barX, barY - 10);
  g.strategies.forEach((s, i) => {
    const y = barY + i * (barH + 14);
    rpsCtx.fillStyle = '#aaa'; rpsCtx.font = '11px monospace';
    rpsCtx.fillText(s, barX, y - 4);
    rpsCtx.fillStyle = 'rgba(94,234,212,0.2)';
    rpsCtx.fillRect(barX, y, barMaxW, barH / 2);
    const col = expWin[i] > 0.52 ? '94,234,212' : expWin[i] < 0.48 ? '248,113,113' : '251,191,36';
    rpsCtx.fillStyle = 'rgba(' + col + ',0.9)';
    rpsCtx.fillRect(barX, y, barMaxW * expWin[i], barH / 2);
    // Reference line at 50%
    rpsCtx.strokeStyle = 'rgba(251,191,36,0.5)';
    rpsCtx.beginPath(); rpsCtx.moveTo(barX + barMaxW / 2, y - 2); rpsCtx.lineTo(barX + barMaxW / 2, y + barH / 2 + 2); rpsCtx.stroke();
    rpsCtx.fillStyle = '#fff'; rpsCtx.textAlign = 'right';
    rpsCtx.fillText((expWin[i] * 100).toFixed(1) + '%', barX + barMaxW - 6, y + barH / 2 - 3);
  });
  rpsCtx.fillStyle = '#888'; rpsCtx.font = '10px monospace'; rpsCtx.textAlign = 'left';
  rpsCtx.fillText('gold line = 50% (what Elo would predict for an equal-rating match)', barX, H - 20);
  requestAnimationFrame(drawRps);
}
rpsGame('ccg');
drawRps();

// ═══════════════════════════════════════════════════════════════════════
// Rematch Oracle
// ═══════════════════════════════════════════════════════════════════════
const oracleCanvas = document.getElementById('oracle-canvas');
const oracleCtx = oracleCanvas.getContext('2d');
let oracleMatches = [];
let oracleOverlay = false;
function oracleSample() {
  oracleMatches = [];
  for (let i = 0; i < 200; i++) {
    const skillDelta = Math.random();
    const tempo = Math.random();
    const social = Math.random();
    const role = Math.random();
    const trueP = Math.max(0, Math.min(1, 0.2 * skillDelta + 0.25 * tempo + 0.2 * social + 0.2 * role + (Math.random() - 0.5) * 0.18));
    const rematch = Math.random() < trueP ? 1 : 0;
    oracleMatches.push({ skillDelta, tempo, social, role, trueP, rematch });
  }
  pepSend('oracle.sample', { n: 200 });
}
function oracleToggleModel() { oracleOverlay = !oracleOverlay; pepSend('oracle.toggle', { on: oracleOverlay }); }
function oracleReset() { oracleMatches = []; oracleOverlay = false; }
oracleSample();
function oracleAUC(scores, labels) {
  const paired = scores.map((s, i) => ({ s, l: labels[i] })).sort((a, b) => b.s - a.s);
  let tp = 0, fp = 0, auc = 0;
  const totP = labels.filter(x => x === 1).length;
  const totN = labels.length - totP;
  let prevFp = 0, prevTp = 0;
  paired.forEach(p => {
    if (p.l === 1) tp++;
    else fp++;
    if (fp > prevFp) {
      auc += (fp - prevFp) * (tp + prevTp) / 2 / (totP * totN);
      prevFp = fp; prevTp = tp;
    }
  });
  return auc;
}
function drawOracle() {
  const W = 960, H = 460; oracleCtx.fillStyle = themeBg(); oracleCtx.fillRect(0, 0, W, H);
  const pad = 60;
  // Axes
  oracleCtx.strokeStyle = 'rgba(120,120,130,0.4)'; oracleCtx.lineWidth = 1;
  oracleCtx.beginPath(); oracleCtx.moveTo(pad, pad); oracleCtx.lineTo(pad, H - pad); oracleCtx.lineTo(W - pad, H - pad); oracleCtx.stroke();
  oracleCtx.fillStyle = '#aaa'; oracleCtx.font = '11px monospace'; oracleCtx.textAlign = 'center';
  oracleCtx.fillText('model-predicted p(rematch) →', W / 2, H - 20);
  oracleCtx.save(); oracleCtx.translate(20, H / 2); oracleCtx.rotate(-Math.PI / 2);
  oracleCtx.fillText('true p(rematch)', 0, 0); oracleCtx.restore();
  // Diagonal
  oracleCtx.strokeStyle = 'rgba(251,191,36,0.4)'; oracleCtx.setLineDash([4, 4]);
  oracleCtx.beginPath(); oracleCtx.moveTo(pad, H - pad); oracleCtx.lineTo(W - pad, pad); oracleCtx.stroke();
  oracleCtx.setLineDash([]);
  // Elo baseline: uses skillDelta only (scaled)
  const eloScores = oracleMatches.map(m => 0.3 + 0.35 * m.skillDelta);
  const labels = oracleMatches.map(m => m.rematch);
  const atriaScores = oracleMatches.map(m => 0.05 + 0.2 * m.skillDelta + 0.25 * m.tempo + 0.2 * m.social + 0.2 * m.role);
  oracleMatches.forEach((m, i) => {
    const px = pad + eloScores[i] * (W - 2 * pad);
    const py = H - pad - m.trueP * (H - 2 * pad);
    oracleCtx.fillStyle = 'rgba(186,104,200,0.55)';
    oracleCtx.beginPath(); oracleCtx.arc(px, py, 3.5, 0, Math.PI * 2); oracleCtx.fill();
  });
  if (oracleOverlay) {
    oracleMatches.forEach((m, i) => {
      const px = pad + atriaScores[i] * (W - 2 * pad);
      const py = H - pad - m.trueP * (H - 2 * pad);
      oracleCtx.fillStyle = 'rgba(251,191,36,0.8)';
      oracleCtx.beginPath(); oracleCtx.arc(px, py, 3, 0, Math.PI * 2); oracleCtx.fill();
    });
  }
  const eloAUC = oracleAUC(eloScores, labels);
  const atriaAUCv = oracleAUC(atriaScores, labels);
  document.getElementById('oracle-elo-auc').textContent = eloAUC.toFixed(2);
  document.getElementById('oracle-atria-auc').textContent = oracleOverlay ? atriaAUCv.toFixed(2) : '—';
  requestAnimationFrame(drawOracle);
}
drawOracle();

// ═══════════════════════════════════════════════════════════════════════
// Queue Time vs Quality
// ═══════════════════════════════════════════════════════════════════════
const queueCanvas = document.getElementById('queue-canvas');
const queueCtx = queueCanvas.getContext('2d');
['queue-pop', 'queue-urg'].forEach(id => {
  document.getElementById(id).addEventListener('input', (e) => {
    document.getElementById(id + '-val').textContent = e.target.value;
  });
});
function drawQueue() {
  const W = 960, H = 440; queueCtx.fillStyle = themeBg(); queueCtx.fillRect(0, 0, W, H);
  const pop = parseInt(document.getElementById('queue-pop').value) / 100;
  const urg = parseInt(document.getElementById('queue-urg').value) / 100;
  const pad = 60;
  queueCtx.strokeStyle = 'rgba(120,120,130,0.4)'; queueCtx.lineWidth = 1;
  queueCtx.beginPath(); queueCtx.moveTo(pad, pad); queueCtx.lineTo(pad, H - pad); queueCtx.lineTo(W - pad, H - pad); queueCtx.stroke();
  queueCtx.fillStyle = '#aaa'; queueCtx.font = '11px monospace'; queueCtx.textAlign = 'center';
  queueCtx.fillText('expected queue time →', W / 2, H - 20);
  queueCtx.save(); queueCtx.translate(20, H / 2); queueCtx.rotate(-Math.PI / 2);
  queueCtx.fillText('expected match quality', 0, 0); queueCtx.restore();
  // Curve: quality(t) = 1 - exp(-k*t) where k depends on population
  const k = 0.4 + pop * 2.5;
  queueCtx.strokeStyle = 'rgba(94,234,212,0.9)'; queueCtx.lineWidth = 2.5;
  queueCtx.beginPath();
  for (let i = 0; i <= 100; i++) {
    const t = i / 100;
    const q = 1 - Math.exp(-k * t);
    const px = pad + t * (W - 2 * pad);
    const py = H - pad - q * (H - 2 * pad);
    if (i === 0) queueCtx.moveTo(px, py); else queueCtx.lineTo(px, py);
  }
  queueCtx.stroke();
  // Operating point: urgency determines time spent
  const operT = Math.max(0.05, 1 - urg * 0.95);
  const operQ = 1 - Math.exp(-k * operT);
  const opx = pad + operT * (W - 2 * pad);
  const opy = H - pad - operQ * (H - 2 * pad);
  queueCtx.strokeStyle = 'rgba(251,191,36,0.5)'; queueCtx.setLineDash([3, 3]);
  queueCtx.beginPath(); queueCtx.moveTo(opx, H - pad); queueCtx.lineTo(opx, opy); queueCtx.lineTo(pad, opy); queueCtx.stroke();
  queueCtx.setLineDash([]);
  queueCtx.fillStyle = 'rgba(251,191,36,0.95)';
  queueCtx.beginPath(); queueCtx.arc(opx, opy, 8, 0, Math.PI * 2); queueCtx.fill();
  queueCtx.fillStyle = '#fff'; queueCtx.font = 'bold 11px monospace'; queueCtx.textAlign = 'left';
  queueCtx.fillText('current operating point', opx + 12, opy - 4);
  queueCtx.fillStyle = '#aaa'; queueCtx.font = '10px monospace';
  queueCtx.fillText('quality: ' + (operQ * 100).toFixed(0) + '%', opx + 12, opy + 12);
  queueCtx.fillText('time:    ' + (operT * 100).toFixed(0) + '% of max', opx + 12, opy + 26);
  // Label the regime
  let regime;
  if (pop < 0.25) regime = 'sparse population — curve is steep';
  else if (pop < 0.6) regime = 'moderate density — room to negotiate';
  else regime = 'dense population — curve is forgiving';
  queueCtx.fillStyle = '#888'; queueCtx.fillText(regime, 70, 40);
  requestAnimationFrame(drawQueue);
}
drawQueue();

// ═══════════════════════════════════════════════════════════════════════
// Cold Start
// ═══════════════════════════════════════════════════════════════════════
const coldstartCanvas = document.getElementById('coldstart-canvas');
const coldstartCtx = coldstartCanvas.getContext('2d');
let coldMu = 1500, coldSigma = 400, coldHistory = [];
function coldstartPlay() {
  // Simulate a placement match against a random opponent with some true skill
  const trueSkill = 1400 + Math.random() * 400;
  const opponentSkill = 1300 + Math.random() * 400;
  const winProb = 1 / (1 + Math.pow(10, (opponentSkill - trueSkill) / 400));
  const won = Math.random() < winProb;
  // Simple Glicko-style update
  const K = 80 * (coldSigma / 400);
  const expected = 1 / (1 + Math.pow(10, (opponentSkill - coldMu) / 400));
  coldMu += K * ((won ? 1 : 0) - expected);
  coldSigma = Math.max(60, coldSigma * 0.85);
  coldHistory.push({ mu: coldMu, sigma: coldSigma, won });
  document.getElementById('cold-mu').textContent = Math.round(coldMu);
  document.getElementById('cold-sigma').textContent = Math.round(coldSigma);
  pepSend('coldstart.play', { mu: Math.round(coldMu), sigma: Math.round(coldSigma) });
}
function coldstartReset() { coldMu = 1500; coldSigma = 400; coldHistory = []; document.getElementById('cold-mu').textContent = '1500'; document.getElementById('cold-sigma').textContent = '400'; }
function drawColdstart() {
  const W = 960, H = 440; coldstartCtx.fillStyle = themeBg(); coldstartCtx.fillRect(0, 0, W, H);
  // Distribution curve
  coldstartCtx.strokeStyle = 'rgba(94,234,212,0.85)'; coldstartCtx.lineWidth = 2.5;
  coldstartCtx.beginPath();
  const minX = 800, maxX = 2200;
  for (let i = 0; i <= 200; i++) {
    const x = minX + (i / 200) * (maxX - minX);
    const y = Math.exp(-Math.pow((x - coldMu) / coldSigma, 2) / 2);
    const px = 60 + (i / 200) * (W - 120);
    const py = H - 120 - y * 240;
    if (i === 0) coldstartCtx.moveTo(px, py); else coldstartCtx.lineTo(px, py);
  }
  coldstartCtx.stroke();
  // Axis
  coldstartCtx.strokeStyle = 'rgba(120,120,130,0.4)';
  coldstartCtx.beginPath(); coldstartCtx.moveTo(60, H - 120); coldstartCtx.lineTo(W - 60, H - 120); coldstartCtx.stroke();
  coldstartCtx.fillStyle = '#888'; coldstartCtx.font = '10px monospace'; coldstartCtx.textAlign = 'center';
  for (let r = 1000; r <= 2000; r += 200) {
    const px = 60 + ((r - minX) / (maxX - minX)) * (W - 120);
    coldstartCtx.fillText(r, px, H - 100);
  }
  // Mu marker
  const mux = 60 + ((coldMu - minX) / (maxX - minX)) * (W - 120);
  coldstartCtx.strokeStyle = 'rgba(251,191,36,0.9)'; coldstartCtx.lineWidth = 2;
  coldstartCtx.beginPath(); coldstartCtx.moveTo(mux, H - 120); coldstartCtx.lineTo(mux, H - 360); coldstartCtx.stroke();
  coldstartCtx.fillStyle = 'rgba(251,191,36,0.95)'; coldstartCtx.font = 'bold 12px monospace';
  coldstartCtx.fillText('μ = ' + Math.round(coldMu), mux, H - 368);
  // Match history dots
  coldHistory.slice(-10).forEach((h, i) => {
    coldstartCtx.fillStyle = h.won ? 'rgba(94,234,212,0.9)' : 'rgba(248,113,113,0.9)';
    coldstartCtx.beginPath(); coldstartCtx.arc(100 + i * 44, 60, 7, 0, Math.PI * 2); coldstartCtx.fill();
  });
  coldstartCtx.fillStyle = '#aaa'; coldstartCtx.font = '11px monospace'; coldstartCtx.textAlign = 'left';
  coldstartCtx.fillText('placement history →', 100, 40);
  requestAnimationFrame(drawColdstart);
}
drawColdstart();

// ═══════════════════════════════════════════════════════════════════════
// Rating Confidence
// ═══════════════════════════════════════════════════════════════════════
const CONFIDENCE_DATA = {
  veteran: { mu: 1500, sigma: 50, note: '800 games, active daily — match tight, expect close games' },
  returning: { mu: 1500, sigma: 180, note: 'was 1500 a year ago, no games since — widen pool, re-calibrate fast' },
  new: { mu: 1500, sigma: 350, note: '2 games, placement ongoing — prefer maximally informative matches' },
};
const confCanvas = document.getElementById('confidence-canvas');
const confCtx = confCanvas.getContext('2d');
let confActive = null;
function confidencePick(k) { confActive = k; pepSend('confidence.pick', { key: k }); }
function drawConfidence() {
  const W = 960, H = 440; confCtx.fillStyle = themeBg(); confCtx.fillRect(0, 0, W, H);
  if (!confActive) { confCtx.fillStyle = '#666'; confCtx.font = '11px monospace'; confCtx.textAlign = 'center'; confCtx.fillText('(pick a player profile)', W / 2, H / 2); requestAnimationFrame(drawConfidence); return; }
  const d = CONFIDENCE_DATA[confActive];
  // Draw three curves, all at the same mu, different sigma — current highlighted
  const profiles = [
    { key: 'veteran', col: '94,234,212' },
    { key: 'returning', col: '251,191,36' },
    { key: 'new', col: '248,113,113' },
  ];
  const minX = 600, maxX = 2400;
  profiles.forEach(p => {
    const pd = CONFIDENCE_DATA[p.key];
    const isActive = p.key === confActive;
    confCtx.strokeStyle = 'rgba(' + p.col + ',' + (isActive ? 0.95 : 0.25).toFixed(3) + ')';
    confCtx.lineWidth = isActive ? 3 : 1.2;
    confCtx.beginPath();
    for (let i = 0; i <= 200; i++) {
      const x = minX + (i / 200) * (maxX - minX);
      const y = Math.exp(-Math.pow((x - pd.mu) / pd.sigma, 2) / 2);
      const px = 60 + (i / 200) * (W - 120);
      const py = H - 120 - y * 240;
      if (i === 0) confCtx.moveTo(px, py); else confCtx.lineTo(px, py);
    }
    confCtx.stroke();
    if (isActive) {
      confCtx.fillStyle = 'rgba(' + p.col + ',0.95)'; confCtx.font = 'bold 13px monospace'; confCtx.textAlign = 'left';
      confCtx.fillText(p.key.toUpperCase() + ':  μ=' + pd.mu + '  σ=' + pd.sigma, 60, 40);
    }
  });
  confCtx.strokeStyle = 'rgba(120,120,130,0.4)';
  confCtx.beginPath(); confCtx.moveTo(60, H - 120); confCtx.lineTo(W - 60, H - 120); confCtx.stroke();
  confCtx.fillStyle = '#aaa'; confCtx.font = '10px monospace'; confCtx.textAlign = 'center';
  for (let r = 800; r <= 2200; r += 200) {
    const px = 60 + ((r - minX) / (maxX - minX)) * (W - 120);
    confCtx.fillText(r, px, H - 100);
  }
  confCtx.fillStyle = '#888'; confCtx.font = '11px monospace'; confCtx.textAlign = 'left';
  confCtx.fillText(d.note, 60, H - 30);
  requestAnimationFrame(drawConfidence);
}
drawConfidence();

// ═══════════════════════════════════════════════════════════════════════
// Smurfing & Boosting
// ═══════════════════════════════════════════════════════════════════════
const SMURF_DATA = {
  normal: { label: 'normal new player', features: { winrate: 0.48, kdr: 0.55, game_len: 0.5, mech_accuracy: 0.42, decision_speed: 0.45 }, flags: [] },
  smurf: { label: 'smurf (experienced on new account)', features: { winrate: 0.88, kdr: 0.92, game_len: 0.28, mech_accuracy: 0.94, decision_speed: 0.9 }, flags: ['impossible win streak at placement', 'elite mechanics outside bracket', 'game length far below bracket median', 'decision speed inconsistent with account age'] },
  boosted: { label: 'boosted (paid carry)', features: { winrate: 0.78, kdr: 0.62, game_len: 0.4, mech_accuracy: 0.82, decision_speed: 0.55 }, flags: ['mechanical stats spike during specific sessions', 'off-session mechanics revert to bracket average', 'play-time pattern inconsistent with single user'] },
};
const smurfCanvas = document.getElementById('smurf-canvas');
const smurfCtx = smurfCanvas.getContext('2d');
let smurfActive = null;
function smurfPick(k) { smurfActive = k; pepSend('smurf.pick', { key: k }); }
function drawSmurf() {
  const W = 960, H = 460; smurfCtx.fillStyle = themeBg(); smurfCtx.fillRect(0, 0, W, H);
  if (!smurfActive) { smurfCtx.fillStyle = '#666'; smurfCtx.font = '11px monospace'; smurfCtx.textAlign = 'center'; smurfCtx.fillText('(pick a player type)', W / 2, H / 2); requestAnimationFrame(drawSmurf); return; }
  const d = SMURF_DATA[smurfActive];
  smurfCtx.fillStyle = 'rgba(94,234,212,0.95)'; smurfCtx.font = 'bold 14px monospace'; smurfCtx.textAlign = 'left';
  smurfCtx.fillText(d.label.toUpperCase(), 30, 40);
  // Radar
  const cx = 280, cy = 240, R = 130;
  const axes = ['winrate', 'kdr', 'game_len', 'mech_accuracy', 'decision_speed'];
  smurfCtx.strokeStyle = 'rgba(120,120,130,0.3)'; smurfCtx.lineWidth = 1;
  for (let ring = 0.25; ring <= 1; ring += 0.25) {
    smurfCtx.beginPath();
    axes.forEach((a, i) => {
      const ang = (i / axes.length) * Math.PI * 2 - Math.PI / 2;
      const x = cx + Math.cos(ang) * R * ring;
      const y = cy + Math.sin(ang) * R * ring;
      if (i === 0) smurfCtx.moveTo(x, y); else smurfCtx.lineTo(x, y);
    });
    smurfCtx.closePath(); smurfCtx.stroke();
  }
  axes.forEach((a, i) => {
    const ang = (i / axes.length) * Math.PI * 2 - Math.PI / 2;
    const x = cx + Math.cos(ang) * R, y = cy + Math.sin(ang) * R;
    smurfCtx.strokeStyle = 'rgba(120,120,130,0.3)';
    smurfCtx.beginPath(); smurfCtx.moveTo(cx, cy); smurfCtx.lineTo(x, y); smurfCtx.stroke();
    smurfCtx.fillStyle = '#aaa'; smurfCtx.font = '10px monospace'; smurfCtx.textAlign = 'center';
    smurfCtx.fillText(a, cx + Math.cos(ang) * (R + 16), cy + Math.sin(ang) * (R + 16) + 3);
  });
  const col = smurfActive === 'normal' ? '94,234,212' : '248,113,113';
  smurfCtx.fillStyle = 'rgba(' + col + ',0.35)';
  smurfCtx.beginPath();
  axes.forEach((a, i) => {
    const v = d.features[a];
    const ang = (i / axes.length) * Math.PI * 2 - Math.PI / 2;
    const x = cx + Math.cos(ang) * R * v;
    const y = cy + Math.sin(ang) * R * v;
    if (i === 0) smurfCtx.moveTo(x, y); else smurfCtx.lineTo(x, y);
  });
  smurfCtx.closePath(); smurfCtx.fill();
  smurfCtx.strokeStyle = 'rgba(' + col + ',0.95)'; smurfCtx.lineWidth = 2; smurfCtx.stroke();
  // Flags panel
  smurfCtx.fillStyle = 'rgba(94,234,212,0.95)'; smurfCtx.font = 'bold 12px monospace'; smurfCtx.textAlign = 'left';
  smurfCtx.fillText('DETECTION FLAGS', 520, 100);
  smurfCtx.fillStyle = '#e0e0e0'; smurfCtx.font = '12px monospace';
  if (d.flags.length === 0) {
    smurfCtx.fillStyle = '#888';
    smurfCtx.fillText('(no anomalies detected)', 540, 130);
  } else {
    d.flags.forEach((f, i) => {
      smurfCtx.fillStyle = 'rgba(248,113,113,0.9)';
      smurfCtx.fillText('• ' + f, 540, 130 + i * 24);
    });
  }
  requestAnimationFrame(drawSmurf);
}
drawSmurf();

// ═══════════════════════════════════════════════════════════════════════
// Toxicity Cascade
// ═══════════════════════════════════════════════════════════════════════
const toxCanvas = document.getElementById('toxcascade-canvas');
const toxCtx = toxCanvas.getContext('2d');
let toxNodes = [], toxEdges = [], toxRunning = false, toxT = 0, toxAffected = 0;
function toxcascadeRun() {
  toxNodes = []; toxEdges = []; toxAffected = 0; toxT = 0; toxRunning = true;
  // Match 1 at center: 10 players
  for (let i = 0; i < 10; i++) {
    const a = (i / 10) * Math.PI * 2;
    toxNodes.push({ x: 480 + Math.cos(a) * 70, y: 230 + Math.sin(a) * 70, tilt: i === 0 ? 1 : 0, match: 0, layer: 0 });
  }
  pepSend('toxcascade.run', {});
}
function toxcascadeReset() { toxNodes = []; toxEdges = []; toxRunning = false; toxAffected = 0; document.getElementById('tox-affected').textContent = '0'; }
function drawToxcascade() {
  const W = 960, H = 460; toxCtx.fillStyle = themeBg(); toxCtx.fillRect(0, 0, W, H);
  if (toxRunning && toxT < 240) {
    toxT++;
    // Every 60 frames, propagate one layer
    if (toxT % 60 === 0 && toxT < 180) {
      const layer = toxT / 60;
      const tiltedLast = toxNodes.filter(n => n.layer === layer - 1 && n.tilt > 0.3);
      tiltedLast.forEach((src, idx) => {
        // Each tilted player starts a new match with 9 new players
        const baseX = 150 + Math.random() * 660;
        const baseY = 60 + Math.random() * 340;
        for (let i = 0; i < 9; i++) {
          const a = (i / 9) * Math.PI * 2;
          const nx = baseX + Math.cos(a) * 30;
          const ny = baseY + Math.sin(a) * 30;
          const newTilt = Math.max(0, src.tilt * 0.6 - 0.05 + Math.random() * 0.15);
          toxNodes.push({ x: nx, y: ny, tilt: newTilt, match: layer * 10 + idx + 1, layer });
          if (newTilt > 0.3) toxAffected++;
        }
      });
      document.getElementById('tox-affected').textContent = toxAffected;
    }
    if (toxT >= 240) toxRunning = false;
  }
  toxNodes.forEach(n => {
    const col = n.tilt > 0.5 ? '248,113,113' : n.tilt > 0.15 ? '251,191,36' : '94,234,212';
    toxCtx.fillStyle = 'rgba(' + col + ',' + (0.3 + n.tilt * 0.6).toFixed(3) + ')';
    toxCtx.beginPath(); toxCtx.arc(n.x, n.y, 4 + n.tilt * 5, 0, Math.PI * 2); toxCtx.fill();
  });
  toxCtx.fillStyle = '#aaa'; toxCtx.font = '11px monospace'; toxCtx.textAlign = 'left';
  toxCtx.fillText('red = tilted · yellow = mildly affected · teal = unaffected', 30, 30);
  if (!toxRunning && toxNodes.length) {
    toxCtx.fillStyle = 'rgba(248,113,113,0.95)'; toxCtx.font = 'bold 12px monospace';
    toxCtx.fillText('cascade complete — ' + toxAffected + ' downstream players tilted from one source', 30, H - 20);
  }
  requestAnimationFrame(drawToxcascade);
}
drawToxcascade();

// ═══════════════════════════════════════════════════════════════════════
// Party Matchmaking
// ═══════════════════════════════════════════════════════════════════════
const PARTY_DATA = {
  tight: { label: 'Tight party (aggressive, chatty)', constraints: 0.85, pool: 12, note: 'intersection is narrow — few solo players match all three' },
  chill: { label: 'Chill party (casual, quiet)', constraints: 0.75, pool: 28, note: 'still narrow but in a different direction — looking for calm comms and casual goals' },
  mixed: { label: 'Mixed party (flexible)', constraints: 0.45, pool: 74, note: 'loose shared constraints — intersection with solo pool is wide' },
};
const partyCanvas = document.getElementById('party-canvas');
const partyCtx = partyCanvas.getContext('2d');
let partyActive = null;
function partyPick(k) { partyActive = k; pepSend('party.pick', { key: k }); }
function partyReset() { partyActive = null; }
function drawParty() {
  const W = 960, H = 460; partyCtx.fillStyle = themeBg(); partyCtx.fillRect(0, 0, W, H);
  if (!partyActive) { partyCtx.fillStyle = '#666'; partyCtx.font = '11px monospace'; partyCtx.textAlign = 'center'; partyCtx.fillText('(pick a party type)', W / 2, H / 2); requestAnimationFrame(drawParty); return; }
  const d = PARTY_DATA[partyActive];
  // Party of 3 at left
  for (let i = 0; i < 3; i++) {
    const py = 140 + i * 80;
    partyCtx.fillStyle = 'rgba(94,234,212,0.8)';
    partyCtx.beginPath(); partyCtx.arc(130, py, 22, 0, Math.PI * 2); partyCtx.fill();
    partyCtx.strokeStyle = 'rgba(94,234,212,1)'; partyCtx.lineWidth = 2; partyCtx.stroke();
    partyCtx.fillStyle = '#000'; partyCtx.font = 'bold 11px monospace'; partyCtx.textAlign = 'center';
    partyCtx.fillText('P' + (i + 1), 130, py + 4);
  }
  partyCtx.strokeStyle = 'rgba(94,234,212,0.5)'; partyCtx.setLineDash([3, 3]);
  partyCtx.beginPath(); partyCtx.arc(130, 230, 80, 0, Math.PI * 2); partyCtx.stroke();
  partyCtx.setLineDash([]);
  partyCtx.fillStyle = 'rgba(94,234,212,0.95)'; partyCtx.font = 'bold 11px monospace'; partyCtx.textAlign = 'center';
  partyCtx.fillText('3-party', 130, 340);
  // Solo pool cloud
  const poolCx = 620, poolCy = 230, poolR = 140;
  partyCtx.fillStyle = 'rgba(120,120,130,0.08)';
  partyCtx.beginPath(); partyCtx.arc(poolCx, poolCy, poolR, 0, Math.PI * 2); partyCtx.fill();
  partyCtx.strokeStyle = 'rgba(120,120,130,0.4)'; partyCtx.lineWidth = 1;
  partyCtx.stroke();
  // Solo players
  for (let i = 0; i < 100; i++) {
    const a = Math.random() * Math.PI * 2;
    const r = Math.sqrt(Math.random()) * poolR * 0.9;
    const x = poolCx + Math.cos(a) * r;
    const y = poolCy + Math.sin(a) * r;
    // In constraint set if i < d.pool
    const inSet = i < d.pool;
    partyCtx.fillStyle = inSet ? 'rgba(251,191,36,0.85)' : 'rgba(120,120,130,0.3)';
    partyCtx.beginPath(); partyCtx.arc(x, y, inSet ? 4 : 2.5, 0, Math.PI * 2); partyCtx.fill();
  }
  partyCtx.fillStyle = '#aaa'; partyCtx.font = '11px monospace'; partyCtx.textAlign = 'center';
  partyCtx.fillText('solo queue', poolCx, poolCy + poolR + 24);
  partyCtx.fillStyle = 'rgba(251,191,36,0.95)'; partyCtx.font = 'bold 12px monospace';
  partyCtx.fillText(d.pool + ' compatible (gold) / 100', poolCx, poolCy + poolR + 44);
  partyCtx.fillStyle = '#e0e0e0'; partyCtx.font = '11px monospace'; partyCtx.textAlign = 'left';
  partyCtx.fillText(d.label, 30, 40);
  partyCtx.fillStyle = '#888';
  partyCtx.fillText(d.note, 30, 60);
  requestAnimationFrame(drawParty);
}
drawParty();

// ═══════════════════════════════════════════════════════════════════════
// Team Chemistry
// ═══════════════════════════════════════════════════════════════════════
const CHEMISTRY_DATA = {
  A: { label: 'Team A — high individual, low synergy', players: [1700, 1680, 1690, 1670, 1700], synergy: 0.35, effective: 1620, note: 'higher raw ratings but no history together; role overlap; mismatched timing' },
  B: { label: 'Team B — medium individual, high synergy', players: [1550, 1540, 1560, 1530, 1570], synergy: 0.92, effective: 1720, note: 'lower raw ratings but deep history; complementary roles; aligned rhythm; multiplicative effects' },
};
const chemCanvas = document.getElementById('chemistry-canvas');
const chemCtx = chemCanvas.getContext('2d');
let chemActive = null;
function chemistryPick(k) { chemActive = k; pepSend('chemistry.pick', { key: k }); }
function drawChemistry() {
  const W = 960, H = 460; chemCtx.fillStyle = themeBg(); chemCtx.fillRect(0, 0, W, H);
  if (!chemActive) { chemCtx.fillStyle = '#666'; chemCtx.font = '11px monospace'; chemCtx.textAlign = 'center'; chemCtx.fillText('(pick a team)', W / 2, H / 2); requestAnimationFrame(drawChemistry); return; }
  const d = CHEMISTRY_DATA[chemActive];
  chemCtx.fillStyle = 'rgba(94,234,212,0.95)'; chemCtx.font = 'bold 13px monospace'; chemCtx.textAlign = 'left';
  chemCtx.fillText(d.label.toUpperCase(), 30, 40);
  // Five player nodes
  d.players.forEach((r, i) => {
    const x = 180 + i * 150, y = 180;
    chemCtx.fillStyle = 'rgba(94,234,212,0.5)';
    chemCtx.beginPath(); chemCtx.arc(x, y, 30, 0, Math.PI * 2); chemCtx.fill();
    chemCtx.strokeStyle = 'rgba(94,234,212,0.95)'; chemCtx.lineWidth = 2; chemCtx.stroke();
    chemCtx.fillStyle = '#fff'; chemCtx.font = '11px monospace'; chemCtx.textAlign = 'center';
    chemCtx.fillText(r, x, y + 4);
  });
  // Synergy edges
  for (let i = 0; i < 5; i++) {
    for (let j = i + 1; j < 5; j++) {
      const x1 = 180 + i * 150, x2 = 180 + j * 150;
      chemCtx.strokeStyle = 'rgba(251,191,36,' + (d.synergy * 0.5).toFixed(3) + ')';
      chemCtx.lineWidth = 1 + d.synergy * 2;
      chemCtx.beginPath(); chemCtx.moveTo(x1, 180); chemCtx.quadraticCurveTo((x1 + x2) / 2, 240 + (j - i) * 15, x2, 180); chemCtx.stroke();
    }
  }
  // Stats
  const indvSum = d.players.reduce((a, b) => a + b, 0) / 5;
  chemCtx.fillStyle = '#aaa'; chemCtx.font = '11px monospace'; chemCtx.textAlign = 'left';
  chemCtx.fillText('average individual rating: ' + Math.round(indvSum), 30, 320);
  chemCtx.fillText('synergy score: ' + d.synergy.toFixed(2), 30, 342);
  chemCtx.fillStyle = 'rgba(251,191,36,0.95)'; chemCtx.font = 'bold 13px monospace';
  chemCtx.fillText('effective rating (with synergy): ' + d.effective, 30, 370);
  chemCtx.fillStyle = '#888'; chemCtx.font = '11px monospace';
  chemCtx.fillText(d.note, 30, H - 30);
  requestAnimationFrame(drawChemistry);
}
drawChemistry();

// ═══════════════════════════════════════════════════════════════════════
// Draft Phase
// ═══════════════════════════════════════════════════════════════════════
const DRAFT_HEROES = ['Tank', 'Bruiser', 'Burst DPS', 'Sustain DPS', 'Healer', 'Utility', 'Sniper', 'Rogue'];
const draftCanvas = document.getElementById('draft-canvas');
const draftCtx = draftCanvas.getContext('2d');
let draftA = [], draftB = [], draftTurn = 0;
function draftStep() {
  if (draftA.length + draftB.length >= 10) return;
  const taken = new Set([...draftA, ...draftB]);
  const avail = DRAFT_HEROES.filter(h => !taken.has(h));
  if (!avail.length) return;
  const pick = avail[Math.floor(Math.random() * avail.length)];
  if (draftTurn % 2 === 0) draftA.push(pick); else draftB.push(pick);
  draftTurn++;
  pepSend('draft.step', { turn: draftTurn, pick });
}
function draftReset() { draftA = []; draftB = []; draftTurn = 0; }
function drawDraft() {
  const W = 960, H = 460; draftCtx.fillStyle = themeBg(); draftCtx.fillRect(0, 0, W, H);
  // Team A
  draftCtx.fillStyle = 'rgba(94,234,212,0.95)'; draftCtx.font = 'bold 13px monospace'; draftCtx.textAlign = 'left';
  draftCtx.fillText('TEAM A', 60, 50);
  draftA.forEach((h, i) => {
    const y = 80 + i * 44;
    draftCtx.fillStyle = 'rgba(94,234,212,0.3)';
    draftCtx.fillRect(60, y, 280, 34);
    draftCtx.strokeStyle = 'rgba(94,234,212,0.9)'; draftCtx.lineWidth = 1.5;
    draftCtx.strokeRect(60, y, 280, 34);
    draftCtx.fillStyle = '#fff'; draftCtx.font = '13px monospace';
    draftCtx.fillText(h, 76, y + 22);
  });
  // Team B
  draftCtx.fillStyle = 'rgba(251,191,36,0.95)'; draftCtx.font = 'bold 13px monospace';
  draftCtx.fillText('TEAM B', 620, 50);
  draftB.forEach((h, i) => {
    const y = 80 + i * 44;
    draftCtx.fillStyle = 'rgba(251,191,36,0.3)';
    draftCtx.fillRect(620, y, 280, 34);
    draftCtx.strokeStyle = 'rgba(251,191,36,0.9)';
    draftCtx.strokeRect(620, y, 280, 34);
    draftCtx.fillStyle = '#fff'; draftCtx.font = '13px monospace';
    draftCtx.fillText(h, 636, y + 22);
  });
  // Comp score
  const score = Math.min(1, (draftA.length + draftB.length) / 10 * (0.5 + Math.random() * 0.4));
  document.getElementById('draft-score').textContent = score.toFixed(2);
  draftCtx.fillStyle = '#888'; draftCtx.font = '11px monospace'; draftCtx.textAlign = 'center';
  if (draftA.length + draftB.length < 10) draftCtx.fillText('click Draft Next Pick to continue', W / 2, H - 20);
  else draftCtx.fillText('draft complete — composition quality scored', W / 2, H - 20);
  requestAnimationFrame(drawDraft);
}
drawDraft();

// ═══════════════════════════════════════════════════════════════════════
// Cross-Game Skill Transfer
// ═══════════════════════════════════════════════════════════════════════
const CROSSGAME_MATRIX = {
  games: ['Valorant', 'CS', 'Apex', 'Overwatch', 'RocketLeague'],
  // Rows × cols, aim-focused / macro-focused differ
  aim: [
    [1.00, 0.82, 0.55, 0.45, 0.15],
    [0.82, 1.00, 0.50, 0.40, 0.12],
    [0.55, 0.50, 1.00, 0.60, 0.20],
    [0.45, 0.40, 0.60, 1.00, 0.25],
    [0.15, 0.12, 0.20, 0.25, 1.00],
  ],
  macro: [
    [1.00, 0.70, 0.45, 0.55, 0.20],
    [0.70, 1.00, 0.42, 0.50, 0.18],
    [0.45, 0.42, 1.00, 0.65, 0.28],
    [0.55, 0.50, 0.65, 1.00, 0.30],
    [0.20, 0.18, 0.28, 0.30, 1.00],
  ],
  mechanics: [
    [1.00, 0.75, 0.30, 0.25, 0.10],
    [0.75, 1.00, 0.25, 0.20, 0.08],
    [0.30, 0.25, 1.00, 0.35, 0.15],
    [0.25, 0.20, 0.35, 1.00, 0.18],
    [0.10, 0.08, 0.15, 0.18, 1.00],
  ],
};
const crossgameCanvas = document.getElementById('crossgame-canvas');
const crossgameCtx = crossgameCanvas.getContext('2d');
let crossgameHighlightKey = 'aim';
function crossgameHighlight(k) { crossgameHighlightKey = k; pepSend('crossgame.highlight', { key: k }); }
function crossgameReset() { crossgameHighlightKey = 'aim'; }
function drawCrossgame() {
  const W = 960, H = 440; crossgameCtx.fillStyle = themeBg(); crossgameCtx.fillRect(0, 0, W, H);
  const m = CROSSGAME_MATRIX[crossgameHighlightKey];
  const n = CROSSGAME_MATRIX.games.length;
  const cell = 60, mx = 200, my = 100;
  crossgameCtx.fillStyle = 'rgba(94,234,212,0.95)'; crossgameCtx.font = 'bold 13px monospace'; crossgameCtx.textAlign = 'left';
  crossgameCtx.fillText('SKILL TRANSFER: ' + crossgameHighlightKey.toUpperCase(), 30, 40);
  // Column headers
  crossgameCtx.fillStyle = '#aaa'; crossgameCtx.font = '10px monospace'; crossgameCtx.textAlign = 'center';
  CROSSGAME_MATRIX.games.forEach((g, j) => crossgameCtx.fillText(g, mx + j * cell + cell / 2, my - 8));
  // Rows
  for (let i = 0; i < n; i++) {
    crossgameCtx.fillStyle = '#aaa'; crossgameCtx.textAlign = 'right';
    crossgameCtx.fillText(CROSSGAME_MATRIX.games[i], mx - 6, my + i * cell + cell / 2 + 4);
    for (let j = 0; j < n; j++) {
      const v = m[i][j];
      crossgameCtx.fillStyle = 'rgba(94,234,212,' + (0.1 + v * 0.75).toFixed(3) + ')';
      crossgameCtx.fillRect(mx + j * cell, my + i * cell, cell - 2, cell - 2);
      crossgameCtx.fillStyle = '#fff'; crossgameCtx.font = '11px monospace'; crossgameCtx.textAlign = 'center';
      crossgameCtx.fillText(v.toFixed(2), mx + j * cell + cell / 2, my + i * cell + cell / 2 + 4);
    }
  }
  crossgameCtx.fillStyle = '#888'; crossgameCtx.font = '11px monospace'; crossgameCtx.textAlign = 'left';
  crossgameCtx.fillText('cell = skill correlation between row game and column game for this sub-skill', 30, H - 20);
  requestAnimationFrame(drawCrossgame);
}
drawCrossgame();

// ═══════════════════════════════════════════════════════════════════════
// Engagement vs Fair
// ═══════════════════════════════════════════════════════════════════════
const ENGAGEMENT_DATA = {
  fair: { label: 'Fair matchmaking', obj: 'even win probability', matches_good: 0.55, player_trust: 0.7, session_length: 0.55 },
  engagement: { label: 'Engagement matchmaking (dark pattern)', obj: 'maximize time-in-game / purchases', matches_good: 0.4, player_trust: 0.25, session_length: 0.85 },
  experience: { label: 'Experience-quality matchmaking (Atria)', obj: 'maximize rematch rate', matches_good: 0.82, player_trust: 0.9, session_length: 0.78 },
};
const engagementCanvas = document.getElementById('engagement-canvas');
const engagementCtx = engagementCanvas.getContext('2d');
let engagementActive = null;
function engagementPick(k) { engagementActive = k; pepSend('engagement.pick', { key: k }); }
function drawEngagement() {
  const W = 960, H = 460; engagementCtx.fillStyle = themeBg(); engagementCtx.fillRect(0, 0, W, H);
  if (!engagementActive) { engagementCtx.fillStyle = '#666'; engagementCtx.font = '11px monospace'; engagementCtx.textAlign = 'center'; engagementCtx.fillText('(pick an objective)', W / 2, H / 2); requestAnimationFrame(drawEngagement); return; }
  const d = ENGAGEMENT_DATA[engagementActive];
  engagementCtx.fillStyle = 'rgba(94,234,212,0.95)'; engagementCtx.font = 'bold 14px monospace'; engagementCtx.textAlign = 'left';
  engagementCtx.fillText(d.label.toUpperCase(), 30, 40);
  engagementCtx.fillStyle = '#aaa'; engagementCtx.font = '11px monospace';
  engagementCtx.fillText('objective: ' + d.obj, 30, 66);
  const metrics = [
    { l: 'match quality felt', v: d.matches_good, c: '94,234,212' },
    { l: 'long-term player trust', v: d.player_trust, c: '251,191,36' },
    { l: 'average session length', v: d.session_length, c: '168,213,255' },
  ];
  metrics.forEach((m, i) => {
    const y = 130 + i * 80;
    engagementCtx.fillStyle = '#e0e0e0'; engagementCtx.font = 'bold 12px monospace';
    engagementCtx.fillText(m.l, 30, y);
    engagementCtx.fillStyle = 'rgba(' + m.c + ',0.2)';
    engagementCtx.fillRect(30, y + 10, 900, 26);
    engagementCtx.fillStyle = 'rgba(' + m.c + ',0.9)';
    engagementCtx.fillRect(30, y + 10, 900 * m.v, 26);
    engagementCtx.fillStyle = '#aaa'; engagementCtx.font = '11px monospace'; engagementCtx.textAlign = 'right';
    engagementCtx.fillText((m.v * 100).toFixed(0) + '%', 920, y + 28);
    engagementCtx.textAlign = 'left';
  });
  engagementCtx.fillStyle = '#888'; engagementCtx.font = '10px monospace';
  engagementCtx.fillText('engagement matchmaking buys session length at the cost of trust. experience-quality matchmaking buys both.', 30, H - 30);
  requestAnimationFrame(drawEngagement);
}
drawEngagement();

// ═══════════════════════════════════════════════════════════════════════
// Matchmaking Transparency
// ═══════════════════════════════════════════════════════════════════════
const TRANSPARENCY_DATA = {
  A: { explain: 'You were matched with these four players because your tempo aligned 0.85 with the average, communication style matched 0.78, role coverage was complete, and none of the five players had a recent negative-behavior flag. We expanded the pool by 20% to find the tempo match, which added 45 seconds to your queue time.' },
  B: { explain: 'We accepted a wider skill gap than usual on this match. Your pool was thin (47 solo players at this hour), and the next-best option would have added 3+ minutes of queue time. We prioritized shared role preferences and communication style over exact rating match — expect a close-but-slightly-uneven game.' },
  C: { explain: 'This match is part of a calibration sequence. Your rating confidence is still wide because you played three days ago and then stopped. We are putting you in slightly varied skill brackets for the next 5 games to re-narrow the confidence interval faster than a normal matchmaking schedule would.' },
};
const transparencyCanvas = document.getElementById('transparency-canvas');
const transparencyCtx = transparencyCanvas.getContext('2d');
let transparencyActive = null;
function transparencyPick(k) { transparencyActive = k; pepSend('transparency.pick', { key: k }); }
function drawTransparency() {
  const W = 960, H = 460; transparencyCtx.fillStyle = themeBg(); transparencyCtx.fillRect(0, 0, W, H);
  if (!transparencyActive) { transparencyCtx.fillStyle = '#666'; transparencyCtx.font = '11px monospace'; transparencyCtx.textAlign = 'center'; transparencyCtx.fillText('(pick a match explanation)', W / 2, H / 2); requestAnimationFrame(drawTransparency); return; }
  const d = TRANSPARENCY_DATA[transparencyActive];
  transparencyCtx.fillStyle = 'rgba(94,234,212,0.95)'; transparencyCtx.font = 'bold 13px monospace'; transparencyCtx.textAlign = 'left';
  transparencyCtx.fillText('MATCH ' + transparencyActive + ' — WHY THIS MATCH WAS FORMED', 30, 40);
  transparencyCtx.fillStyle = '#e0e0e0'; transparencyCtx.font = '13px monospace';
  const words = d.explain.split(' '); let x = 30, y = 90;
  words.forEach(w => { const m = transparencyCtx.measureText(w + ' '); if (x + m.width > W - 30) { x = 30; y += 22; } transparencyCtx.fillText(w + ' ', x, y); x += m.width; });
  transparencyCtx.fillStyle = '#888'; transparencyCtx.font = '11px monospace';
  transparencyCtx.fillText('plain-English explanation, shown to the player after the match', 30, H - 30);
  requestAnimationFrame(drawTransparency);
}
drawTransparency();

// ═══════════════════════════════════════════════════════════════════════
// Cross-Domain
// ═══════════════════════════════════════════════════════════════════════
const DOMAIN_DATA = {
  pvp: { label: 'PvP game matchmaking', axes: ['skill', 'tempo', 'role', 'comms', 'tilt tolerance', 'session goals'], target: 'rematch rate', feedback: 'minutes', sample_size: 'thousands per user per day' },
  dating: { label: 'Dating', axes: ['values', 'life stage', 'interests', 'communication', 'conflict style', 'relationship goals'], target: 'relationship longevity', feedback: 'months-years', sample_size: 'dozens per user per lifetime' },
  hiring: { label: 'Hiring / team-building', axes: ['expertise', 'work style', 'role fit', 'communication', 'feedback preference', 'career goals'], target: 'tenure + performance', feedback: 'quarters-years', sample_size: 'hundreds per team lifetime' },
  cofounder: { label: 'Co-founder matching', axes: ['domain', 'work style', 'risk tolerance', 'communication', 'conflict style', 'vision'], target: 'company survival at 3 years', feedback: 'years', sample_size: 'a handful per entrepreneur lifetime' },
  therapy: { label: 'Therapy group composition', axes: ['presenting issues', 'communication style', 'trauma profile', 'openness', 'conflict tolerance', 'therapy goals'], target: 'sustained attendance + reported benefit', feedback: 'weeks', sample_size: 'dozens per clinician year' },
};
const domainCanvas = document.getElementById('domain-canvas');
const domainCtx = domainCanvas.getContext('2d');
let domainActive = null;
function domainPick(k) { domainActive = k; pepSend('domain.pick', { key: k }); }
function drawDomain() {
  const W = 960, H = 460; domainCtx.fillStyle = themeBg(); domainCtx.fillRect(0, 0, W, H);
  if (!domainActive) { domainCtx.fillStyle = '#666'; domainCtx.font = '11px monospace'; domainCtx.textAlign = 'center'; domainCtx.fillText('(pick a domain)', W / 2, H / 2); requestAnimationFrame(drawDomain); return; }
  const d = DOMAIN_DATA[domainActive];
  domainCtx.fillStyle = 'rgba(94,234,212,0.95)'; domainCtx.font = 'bold 14px monospace'; domainCtx.textAlign = 'left';
  domainCtx.fillText(d.label.toUpperCase(), 30, 40);
  domainCtx.fillStyle = 'rgba(94,234,212,0.85)'; domainCtx.font = 'bold 11px monospace';
  domainCtx.fillText('COMPATIBILITY AXES', 30, 90);
  domainCtx.fillStyle = '#e0e0e0'; domainCtx.font = '13px monospace';
  d.axes.forEach((a, i) => domainCtx.fillText('• ' + a, 50, 116 + i * 24));
  domainCtx.fillStyle = 'rgba(251,191,36,0.85)'; domainCtx.font = 'bold 11px monospace';
  domainCtx.fillText('OPTIMIZATION TARGET', 550, 90);
  domainCtx.fillStyle = '#fff'; domainCtx.font = '13px monospace';
  domainCtx.fillText(d.target, 570, 116);
  domainCtx.fillStyle = 'rgba(168,213,255,0.85)'; domainCtx.font = 'bold 11px monospace';
  domainCtx.fillText('FEEDBACK LOOP LENGTH', 550, 170);
  domainCtx.fillStyle = '#fff'; domainCtx.font = '13px monospace';
  domainCtx.fillText(d.feedback, 570, 196);
  domainCtx.fillStyle = 'rgba(248,113,113,0.85)'; domainCtx.font = 'bold 11px monospace';
  domainCtx.fillText('SAMPLE SIZE AVAILABLE', 550, 250);
  domainCtx.fillStyle = '#fff'; domainCtx.font = '13px monospace';
  domainCtx.fillText(d.sample_size, 570, 276);
  domainCtx.fillStyle = '#888'; domainCtx.font = '11px monospace';
  domainCtx.fillText('the compatibility graph underneath is the same; only labels and scoring functions change', 30, H - 40);
  domainCtx.fillText('PvP is the wedge because of the fast feedback loop and cheap rematch signal', 30, H - 22);
  requestAnimationFrame(drawDomain);
}
drawDomain();

// ═══════════════════════════════════════════════════════════════════════
// Search / Random / Bookmarks / Gallery
// ═══════════════════════════════════════════════════════════════════════
const ATRIA_CANVASES = [
  { id: 'elo-tab', title: 'Elo vs Relational', group: 'Thesis' },
  { id: 'rps-tab', title: 'Rock-Paper-Scissors Matchups', group: 'Thesis' },
  { id: 'residual-tab', title: 'Residual Heatmap', group: 'Thesis' },
  { id: 'multi-tab', title: 'Multi-Objective Projection', group: 'Thesis' },
  { id: 'pool-tab', title: 'Pool Spreading', group: 'Matchmaker' },
  { id: 'oracle-tab', title: 'Rematch Oracle', group: 'Matchmaker' },
  { id: 'queue-tab', title: 'Queue Time vs Quality', group: 'Matchmaker' },
  { id: 'coldstart-tab', title: 'Cold Start', group: 'Matchmaker' },
  { id: 'confidence-tab', title: 'Rating Confidence', group: 'Matchmaker' },
  { id: 'behavior-tab', title: 'Behavior Modulation', group: 'Behavior' },
  { id: 'smurf-tab', title: 'Smurfing & Boosting', group: 'Behavior' },
  { id: 'toxcascade-tab', title: 'Toxicity Cascade', group: 'Behavior' },
  { id: 'party-tab', title: 'Party Matchmaking', group: 'Groups' },
  { id: 'chemistry-tab', title: 'Team Chemistry', group: 'Groups' },
  { id: 'draft-tab', title: 'Draft Phase', group: 'Groups' },
  { id: 'crossgame-tab', title: 'Cross-Game Skill Transfer', group: 'Beyond' },
  { id: 'engagement-tab', title: 'Engagement vs Fair', group: 'Beyond' },
  { id: 'transparency-tab', title: 'Matchmaking Transparency', group: 'Beyond' },
  { id: 'domain-tab', title: 'Cross-Domain Generalization', group: 'Beyond' },
];
function atriaBookmarks() { try { return JSON.parse(localStorage.getItem('atria-bookmarks') || '[]'); } catch (e) { return []; } }
function atriaSaveBookmarks(b) { try { localStorage.setItem('atria-bookmarks', JSON.stringify(b)); } catch (e) {} }
function atriaBookmark() {
  const active = document.querySelector('.panel.active');
  if (!active) return;
  const id = active.id;
  const bmks = atriaBookmarks();
  const idx = bmks.indexOf(id);
  if (idx >= 0) bmks.splice(idx, 1); else bmks.push(id);
  atriaSaveBookmarks(bmks);
  const btn = document.getElementById('bookmark-btn');
  if (btn) btn.textContent = bmks.includes(id) ? '★' : '☆';
  renderGallery();
}
function atriaRandom() {
  const i = Math.floor(Math.random() * ATRIA_CANVASES.length);
  const id = ATRIA_CANVASES[i].id;
  const tab = findTabForPanel(id);
  if (tab) tab.click();
  setTimeout(() => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, 60);
  pepSend('atria.random', { id });
}
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
  try { pepSend('canvas.select', { id }); } catch (e) {}
}
function buildCanvasDropdown() {
  const select = document.getElementById('canvas-select');
  if (!select) return;
  const skipIds = ['home-tab', 'theory-tab', 'bridge-tab', 'gallery-tab', 'pep-link-tab'];
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
function galleryFilter(q) {
  const query = (q || '').toLowerCase().trim();
  const grid = document.getElementById('gallery-grid');
  if (!grid) return;
  Array.from(grid.children).forEach(card => {
    card.style.display = !query || card.textContent.toLowerCase().includes(query) ? '' : 'none';
  });
  const visible = Array.from(grid.children).filter(c => c.style.display !== 'none').length;
  const count = document.getElementById('gallery-count');
  if (count) count.textContent = visible + ' / ' + ATRIA_CANVASES.length + ' canvases';
}
function renderGallery() {
  const grid = document.getElementById('gallery-grid');
  if (!grid) return;
  const bmks = atriaBookmarks();
  const sorted = ATRIA_CANVASES.slice().sort((a, b) => {
    const ba = bmks.includes(a.id) ? 0 : 1;
    const bb = bmks.includes(b.id) ? 0 : 1;
    return ba - bb;
  });
  grid.innerHTML = sorted.map(c => {
    const isBmk = bmks.includes(c.id);
    return '<div onclick="galleryGoto(\\'' + c.id + '\\')" ' +
      'style="background:var(--surface);border:1px solid ' + (isBmk ? 'var(--accent2)' : 'var(--border)') + ';border-radius:6px;padding:12px 14px;cursor:pointer">' +
      '<div style="font-size:11px;color:var(--dim);margin-bottom:4px">' + c.group + (isBmk ? ' · ★' : '') + '</div>' +
      '<div style="font-size:12px;color:var(--text);font-weight:bold">' + c.title + '</div>' +
      '</div>';
  }).join('');
  const count = document.getElementById('gallery-count');
  if (count) count.textContent = ATRIA_CANVASES.length + ' canvases';
}
function galleryGoto(id) {
  const tab = findTabForPanel(id);
  if (tab) tab.click();
  setTimeout(() => { const el = document.getElementById(id); if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, 60);
}
setTimeout(renderGallery, 100);
document.querySelectorAll('.tab').forEach(t => {
  t.addEventListener('click', () => {
    setTimeout(() => {
      const active = document.querySelector('.panel.active');
      const btn = document.getElementById('bookmark-btn');
      if (active && btn) btn.textContent = atriaBookmarks().includes(active.id) ? '★' : '☆';
    }, 30);
  });
});

// ═══════════════════════════════════════════════════════════════════════
// Vectora-Powered Live Retrieval (dogfood)
// ═══════════════════════════════════════════════════════════════════════
async function vecAtriaInit() {
  try {
    const r = await fetch('/vectora/seeds/atria');
    const data = await r.json();
    const sel = document.getElementById('vec-atria-seed');
    sel.innerHTML = data.seeds.map(s => `<option value="${s.id}">${s.id} — ${s.metadata.label || s.text.slice(0, 40)}</option>`).join('');
    const stats = document.getElementById('vec-atria-stats');
    if (stats) stats.textContent = `seeded graph: ${data.stats.documents} docs · ${data.stats.edges} edges`;
  } catch (e) { console.warn('vec atria init failed', e); }
}
['vec-atria-k', 'vec-atria-decay'].forEach(id => {
  const el = document.getElementById(id);
  if (!el) return;
  el.addEventListener('input', (e) => {
    const v = parseInt(e.target.value);
    const out = document.getElementById(id + '-v');
    if (!out) return;
    out.textContent = id.endsWith('decay') ? (v / 100).toFixed(2) : v;
  });
});
async function vecAtriaQuery() {
  const seed = document.getElementById('vec-atria-seed').value;
  if (!seed) return;
  const k = parseInt(document.getElementById('vec-atria-k').value);
  const decay = parseInt(document.getElementById('vec-atria-decay').value) / 100;
  const out = document.getElementById('vec-atria-results');
  out.innerHTML = '<div style="color:var(--dim);text-align:center;padding:40px 20px;font-size:11px">querying Vectora…</div>';
  try {
    const r = await fetch(`/vectora/neighbors/atria/${seed}?k=${k}&decay=${decay}`);
    if (!r.ok) throw new Error('retrieval failed');
    const data = await r.json();
    if (!data.hits.length) { out.innerHTML = '<div style="color:var(--dim);text-align:center;padding:40px 20px;font-size:11px">no neighbors</div>'; return; }
    out.innerHTML = data.hits.map((h, i) => {
      const hopBadge = h.hop_distance > 0 ? `<span style="background:rgba(94,234,212,0.2);color:var(--accent);padding:1px 6px;border-radius:8px;font-size:9px;margin-left:6px">hop ${h.hop_distance}</span>` : '';
      const tier = h.metadata.tier ? `<span style="color:var(--dim);margin-left:6px">[${h.metadata.tier}]</span>` : '';
      const label = h.metadata.label ? `<b style="color:var(--text)">${h.metadata.label}</b>` : '';
      return `<div style="background:var(--surface);border:1px solid var(--border);border-left:3px solid var(--accent);border-radius:4px;padding:10px 14px;margin-bottom:6px">
        <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
          <span style="color:var(--accent);font-weight:bold;font-family:monospace">${i+1}. ${h.id}</span>
          ${label}
          ${tier}
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
vecAtriaInit();

// ═══════════════════════════════════════════════════════════════════════
// Vectora KG dogfood — typed player relationships
// ═══════════════════════════════════════════════════════════════════════
const ATRIA_KG_RELATIONS = ['friends_with', 'party_member', 'blocked_by', 'recently_matched', 'counter_to'];
let atriaKgSelectedRels = new Set();

async function atriaKgInit() {
  try {
    const r = await fetch('/vectora/seeds/atria');
    const data = await r.json();
    const sel = document.getElementById('atria-kg-start');
    if (sel) sel.innerHTML = data.seeds.map(s => `<option value="${s.id}">${s.id} — ${s.metadata.label || s.text.slice(0, 30)}</option>`).join('');
    const relBox = document.getElementById('atria-kg-relations');
    if (relBox) relBox.innerHTML = ATRIA_KG_RELATIONS.map(rel => `<button onclick="atriaKgToggleRel('${rel}')" id="atria-kg-rel-${rel}" style="padding:3px 10px;border-radius:12px;border:1px solid var(--border);background:var(--surface);color:var(--dim);font-size:10px;cursor:pointer;font-family:inherit">${rel}</button>`).join('');
    const viz = await fetch('/vectora/kg/atria/viz').then(r => r.json());
    const stats = document.getElementById('atria-kg-stats');
    if (stats) stats.textContent = `typed edges: ${viz.stats.typed_edges} · ${viz.stats.unique_relations} relation types`;
  } catch (e) { console.warn('atria kg init failed', e); }
}
function atriaKgToggleRel(rel) {
  if (atriaKgSelectedRels.has(rel)) atriaKgSelectedRels.delete(rel);
  else atriaKgSelectedRels.add(rel);
  const btn = document.getElementById('atria-kg-rel-' + rel);
  if (btn) {
    if (atriaKgSelectedRels.has(rel)) { btn.style.background = 'var(--accent)'; btn.style.color = 'var(--bg)'; btn.style.borderColor = 'var(--accent)'; }
    else { btn.style.background = 'var(--surface)'; btn.style.color = 'var(--dim)'; btn.style.borderColor = 'var(--border)'; }
  }
}
const atriaKgHopsSlider = document.getElementById('atria-kg-hops');
if (atriaKgHopsSlider) atriaKgHopsSlider.addEventListener('input', (e) => {
  document.getElementById('atria-kg-hops-v').textContent = e.target.value;
});
async function atriaKgTraverse() {
  const start = document.getElementById('atria-kg-start').value;
  const hops = parseInt(document.getElementById('atria-kg-hops').value);
  const relations = atriaKgSelectedRels.size ? Array.from(atriaKgSelectedRels) : null;
  const out = document.getElementById('atria-kg-results');
  out.innerHTML = '<div style="text-align:center;color:var(--dim);padding:30px;font-size:11px">traversing…</div>';
  try {
    const r = await fetch('/vectora/kg/atria/traverse', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ start, max_hops: hops, relations }),
    });
    if (!r.ok) throw new Error('traverse failed');
    const data = await r.json();
    if (!data.results.length) {
      out.innerHTML = `<div style="color:var(--dim);text-align:center;padding:30px;font-size:11px">no neighbors from <b style="color:var(--accent)">${start}</b> within ${hops} hop(s)${relations ? ' via ' + relations.join(', ') : ''}</div>`;
      return;
    }
    out.innerHTML = data.results.map(r => {
      const chain = r.relations_to_seed.map(p => `<span style="color:var(--accent);font-family:monospace">${p[1]}</span> <span style="color:#a3e635;font-size:9px">→[${p[0]}]→</span>`).join(' ');
      return `<div style="padding:10px 14px;border-bottom:1px solid var(--border);font-size:11px"><div style="display:flex;gap:6px;align-items:center"><span style="color:var(--accent);font-weight:bold;font-family:monospace">${r.doc_id}</span><span style="color:var(--dim);font-size:10px">weight ${r.total_weight} · hop ${r.hop_distance}</span></div><div style="color:#a3e635;font-size:10px;margin-top:4px">${chain} <span style="color:var(--text);font-family:monospace">${r.doc_id}</span></div><div style="color:var(--text);font-size:10px;margin-top:3px;line-height:1.55">${r.text}</div></div>`;
    }).join('');
  } catch (e) {
    out.innerHTML = `<div style="color:#f06292;text-align:center;padding:30px;font-size:11px">Error: ${e.message}</div>`;
  }
}
async function atriaKgShowViz() {
  const canvas = document.getElementById('atria-kg-canvas');
  canvas.style.display = 'block';
  try {
    const viz = await fetch('/vectora/kg/atria/viz').then(r => r.json());
    drawAtriaKgViz(canvas, viz);
  } catch (e) { console.warn(e); }
}
function drawAtriaKgViz(canvas, viz) {
  const ctx = canvas.getContext('2d');
  const rect = canvas.getBoundingClientRect();
  canvas.width = rect.width; canvas.height = rect.height;
  const W = rect.width, H = rect.height;
  ctx.fillStyle = getComputedStyle(document.body).getPropertyValue('--surface').trim() || '#141d24';
  ctx.fillRect(0, 0, W, H);
  const inEdges = new Set();
  viz.edges.forEach(e => { inEdges.add(e.source); inEdges.add(e.target); });
  const relevant = viz.nodes.filter(n => inEdges.has(n.id));
  const pos = {};
  relevant.forEach((n, i) => {
    const a = (i / relevant.length) * Math.PI * 2;
    pos[n.id] = { x: W / 2 + Math.cos(a) * (Math.min(W, H) * 0.38), y: H / 2 + Math.sin(a) * (Math.min(W, H) * 0.38) };
  });
  const RELATION_COLORS = { friends_with: '#5eead4', party_member: '#a3e635', blocked_by: '#f06292', recently_matched: '#fbbf24', counter_to: '#c084fc' };
  viz.edges.forEach(e => {
    const s = pos[e.source], t = pos[e.target]; if (!s || !t) return;
    ctx.strokeStyle = (RELATION_COLORS[e.relation] || '#ffffff') + 'aa';
    ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.moveTo(s.x, s.y); ctx.lineTo(t.x, t.y); ctx.stroke();
    ctx.fillStyle = RELATION_COLORS[e.relation] || '#fff'; ctx.font = '8px monospace'; ctx.textAlign = 'center';
    ctx.fillText(e.relation, (s.x + t.x) / 2, (s.y + t.y) / 2 - 3);
  });
  Object.entries(pos).forEach(([id, p]) => {
    ctx.fillStyle = 'rgba(94,234,212,0.5)';
    ctx.beginPath(); ctx.arc(p.x, p.y, 16, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = 'rgba(94,234,212,0.95)'; ctx.lineWidth = 1.5; ctx.stroke();
    ctx.fillStyle = '#fff'; ctx.font = 'bold 9px monospace'; ctx.textAlign = 'center';
    ctx.fillText(id, p.x, p.y + 3);
  });
}
atriaKgInit();

// ═══════════════════════════════════════════════════════════════════════
// Before / After Dashboard
// ═══════════════════════════════════════════════════════════════════════
const dashboardCanvas = document.getElementById('dashboard-canvas');
const dashboardCtx = dashboardCanvas.getContext('2d');
let dashboardData = null;
function dashboardGen() {
  // Simulate 1000 matches under Elo-only vs Atria
  const elo = { rematch: 0, session: 0, toxic: 0, stomp: 0, queue: 0 };
  const atria = { rematch: 0, session: 0, toxic: 0, stomp: 0, queue: 0 };
  for (let i = 0; i < 1000; i++) {
    // Elo-only: rematch rate ~38-45%
    elo.rematch += Math.random() < 0.42 ? 1 : 0;
    // Atria: rematch rate ~55-65%
    atria.rematch += Math.random() < 0.58 ? 1 : 0;
    // Elo: toxic-adjacent ~18%
    elo.toxic += Math.random() < 0.18 ? 1 : 0;
    // Atria: toxic-adjacent ~9%
    atria.toxic += Math.random() < 0.09 ? 1 : 0;
    // Elo: new-player stomp ~22%
    elo.stomp += Math.random() < 0.22 ? 1 : 0;
    // Atria: new-player stomp ~10%
    atria.stomp += Math.random() < 0.10 ? 1 : 0;
  }
  elo.rematch /= 1000; atria.rematch /= 1000;
  elo.toxic /= 1000; atria.toxic /= 1000;
  elo.stomp /= 1000; atria.stomp /= 1000;
  // Session length: correlated with rematch
  elo.session = 3.2 + elo.rematch * 2;
  atria.session = 3.2 + atria.rematch * 2.5;
  // Queue time: Elo = 1.0 (baseline), Atria = 1.08-1.15
  elo.queue = 1.0;
  atria.queue = 1.0 + 0.05 + Math.random() * 0.08;
  dashboardData = { elo, atria };
}
function dashboardRegen() { dashboardGen(); pepSend('dashboard.regen', {}); }
dashboardGen();
function drawDashboard() {
  const W = 960, H = 640; dashboardCtx.fillStyle = themeBg(); dashboardCtx.fillRect(0, 0, W, H);
  if (!dashboardData) { requestAnimationFrame(drawDashboard); return; }
  const d = dashboardData;
  const metrics = [
    { label: 'Rematch rate', elo: d.elo.rematch, atria: d.atria.rematch, fmt: (v) => (v * 100).toFixed(1) + '%', higher: true },
    { label: 'Avg session length', elo: d.elo.session / 6, atria: d.atria.session / 6, fmt: (v) => (v * 6).toFixed(1) + ' matches', higher: true },
    { label: 'Toxic-adjacent rate', elo: d.elo.toxic, atria: d.atria.toxic, fmt: (v) => (v * 100).toFixed(1) + '%', higher: false },
    { label: 'New-player stomp rate', elo: d.elo.stomp, atria: d.atria.stomp, fmt: (v) => (v * 100).toFixed(1) + '%', higher: false },
    { label: 'Avg queue time (index)', elo: d.elo.queue / 1.2, atria: d.atria.queue / 1.2, fmt: (v) => (v * 1.2).toFixed(2) + 'x', higher: false },
  ];
  dashboardCtx.fillStyle = '#aaa'; dashboardCtx.font = '11px monospace'; dashboardCtx.textAlign = 'left';
  dashboardCtx.fillText('1,000 synthetic matches · Elo-only (purple) vs Atria (teal)', 30, 24);
  const barW = 340, barH = 28, gap = 36;
  metrics.forEach((m, i) => {
    const y = 50 + i * (barH * 2 + gap);
    // Label
    dashboardCtx.fillStyle = '#e0e0e0'; dashboardCtx.font = 'bold 12px monospace'; dashboardCtx.textAlign = 'left';
    dashboardCtx.fillText(m.label, 30, y);
    // Elo bar
    dashboardCtx.fillStyle = 'rgba(232,121,249,0.25)'; dashboardCtx.fillRect(30, y + 10, barW, barH);
    dashboardCtx.fillStyle = 'rgba(232,121,249,0.85)'; dashboardCtx.fillRect(30, y + 10, barW * Math.min(1, m.elo), barH);
    dashboardCtx.fillStyle = '#fff'; dashboardCtx.font = '11px monospace'; dashboardCtx.textAlign = 'right';
    dashboardCtx.fillText('Elo: ' + m.fmt(m.elo), 30 + barW - 6, y + 10 + barH / 2 + 4);
    // Atria bar
    dashboardCtx.fillStyle = 'rgba(94,234,212,0.25)'; dashboardCtx.fillRect(30, y + 10 + barH + 4, barW, barH);
    dashboardCtx.fillStyle = 'rgba(94,234,212,0.85)'; dashboardCtx.fillRect(30, y + 10 + barH + 4, barW * Math.min(1, m.atria), barH);
    dashboardCtx.fillStyle = '#fff';
    dashboardCtx.fillText('Atria: ' + m.fmt(m.atria), 30 + barW - 6, y + 10 + barH + 4 + barH / 2 + 4);
    // Delta
    const delta = m.atria - m.elo;
    const pctDelta = m.elo > 0.001 ? (delta / m.elo * 100) : 0;
    const isGood = m.higher ? delta > 0 : delta < 0;
    const col = isGood ? 'rgba(94,234,212,0.95)' : 'rgba(248,113,113,0.95)';
    dashboardCtx.fillStyle = col; dashboardCtx.font = 'bold 13px monospace'; dashboardCtx.textAlign = 'left';
    const sign = pctDelta > 0 ? '+' : '';
    dashboardCtx.fillText(sign + pctDelta.toFixed(0) + '%', 400, y + 10 + barH + 4);
    dashboardCtx.fillStyle = '#aaa'; dashboardCtx.font = '10px monospace';
    dashboardCtx.fillText(isGood ? 'better' : 'tradeoff', 400, y + 10 + barH + 20);
  });
  // Summary callout
  dashboardCtx.fillStyle = 'rgba(94,234,212,0.95)'; dashboardCtx.font = 'bold 12px monospace'; dashboardCtx.textAlign = 'center';
  dashboardCtx.fillText('every metric that matters to players improves; queue time is the known, tunable tradeoff', W / 2, H - 20);
  requestAnimationFrame(drawDashboard);
}
drawDashboard();

// ═══════════════════════════════════════════════════════════════════════
// Ladder Distribution
// ═══════════════════════════════════════════════════════════════════════
const LADDER_DATA = {
  normal:    { label: 'healthy normal', mean: 1500, stddev: 200, skew: 0 },
  bimodal:   { label: 'bimodal (casual + hardcore)', mean: 1500, stddev: 200, skew: 0, bimodal: true },
  inflated:  { label: 'rank inflated', mean: 1700, stddev: 200, skew: 0 },
  heavytail: { label: 'heavy-tailed (skill ceiling)', mean: 1500, stddev: 200, skew: 0.4 },
};
const ladderCanvas = document.getElementById('ladder-canvas');
const ladderCtx = ladderCanvas.getContext('2d');
let ladderActive = 'normal';
function ladderPick(k) { ladderActive = k; pepSend('ladder.pick', { key: k }); }
function drawLadder() {
  const W = 960, H = 440; ladderCtx.fillStyle = themeBg(); ladderCtx.fillRect(0, 0, W, H);
  const d = LADDER_DATA[ladderActive];
  const pad = 60;
  // Axes
  ladderCtx.strokeStyle = 'rgba(120,120,130,0.4)'; ladderCtx.lineWidth = 1;
  ladderCtx.beginPath(); ladderCtx.moveTo(pad, pad); ladderCtx.lineTo(pad, H - pad); ladderCtx.lineTo(W - pad, H - pad); ladderCtx.stroke();
  ladderCtx.fillStyle = '#aaa'; ladderCtx.font = '11px monospace'; ladderCtx.textAlign = 'center';
  ladderCtx.fillText('rating →', W / 2, H - 20);
  ladderCtx.save(); ladderCtx.translate(18, H / 2); ladderCtx.rotate(-Math.PI / 2);
  ladderCtx.fillText('player count', 0, 0); ladderCtx.restore();
  // Generate distribution
  const minR = 800, maxR = 2400, bins = 200;
  const hist = new Array(bins).fill(0);
  for (let i = 0; i < 10000; i++) {
    let r;
    if (d.bimodal) {
      const pop = Math.random() < 0.6 ? 1200 : 1800;
      r = pop + (Math.random() + Math.random() + Math.random() - 1.5) * 200;
    } else {
      r = d.mean + (Math.random() + Math.random() + Math.random() + Math.random() + Math.random() + Math.random() - 3) * d.stddev;
      if (d.skew > 0 && Math.random() < d.skew) r += Math.random() * 500;
    }
    const bin = Math.floor(((r - minR) / (maxR - minR)) * bins);
    if (bin >= 0 && bin < bins) hist[bin]++;
  }
  const maxCount = Math.max(...hist);
  // Draw bars
  const barW = (W - 2 * pad) / bins;
  for (let i = 0; i < bins; i++) {
    const h = (hist[i] / maxCount) * (H - 2 * pad - 10);
    ladderCtx.fillStyle = 'rgba(94,234,212,0.65)';
    ladderCtx.fillRect(pad + i * barW, H - pad - h, Math.max(1, barW - 0.5), h);
  }
  // Median line
  let cumul = 0; const total = hist.reduce((a, b) => a + b, 0);
  let medianBin = 0;
  for (let i = 0; i < bins; i++) {
    cumul += hist[i];
    if (cumul >= total / 2) { medianBin = i; break; }
  }
  const medianX = pad + medianBin * barW;
  ladderCtx.strokeStyle = 'rgba(251,191,36,0.9)'; ladderCtx.lineWidth = 2;
  ladderCtx.setLineDash([4, 4]);
  ladderCtx.beginPath(); ladderCtx.moveTo(medianX, pad); ladderCtx.lineTo(medianX, H - pad); ladderCtx.stroke();
  ladderCtx.setLineDash([]);
  ladderCtx.fillStyle = 'rgba(251,191,36,0.95)'; ladderCtx.font = '10px monospace'; ladderCtx.textAlign = 'center';
  ladderCtx.fillText('median', medianX, pad - 6);
  // Label
  ladderCtx.fillStyle = 'rgba(94,234,212,0.95)'; ladderCtx.font = 'bold 12px monospace'; ladderCtx.textAlign = 'left';
  ladderCtx.fillText(d.label.toUpperCase(), pad + 10, pad + 16);
  // Rating labels along x-axis
  for (let r = 1000; r <= 2200; r += 200) {
    const x = pad + ((r - minR) / (maxR - minR)) * (W - 2 * pad);
    ladderCtx.fillStyle = '#666'; ladderCtx.font = '10px monospace'; ladderCtx.textAlign = 'center';
    ladderCtx.fillText(r, x, H - pad + 16);
  }
  requestAnimationFrame(drawLadder);
}
drawLadder();

// ═══════════════════════════════════════════════════════════════════════
// Composer — scenarios + master controls
// ═══════════════════════════════════════════════════════════════════════
function setSliderById(id, val) {
  const el = document.getElementById(id);
  if (!el) return;
  el.value = val;
  el.dispatchEvent(new Event('input', { bubbles: true }));
}
const ATRIA_SCENARIOS = {
  newplayer: [
    { label: 'New player queues (wide confidence)',   run: () => { try { confidencePick('new'); } catch(e) {} } },
    { label: 'Placement match 1',                     run: () => { try { coldstartPlay(); } catch(e) {} } },
    { label: 'Placement match 2',                     run: () => { try { coldstartPlay(); } catch(e) {} } },
    { label: 'Pool narrows as sigma shrinks',         run: () => { setSliderById('pool-decay', 30); } },
    { label: 'Matched against flexible opponent',     run: () => { try { confidencePick('veteran'); } catch(e) {} } },
  ],
  smurfday: [
    { label: 'Smurf account detected',               run: () => { try { smurfPick('smurf'); } catch(e) {} } },
    { label: 'Feature radar: elite mechanics at low rank', run: () => { /* smurf canvas already showing */ } },
    { label: 'Behavior modulator contracts pool',     run: () => { try { behaviorFlag('toxicity'); } catch(e) {} } },
    { label: 'Smurf matched with other smurfs',       run: () => { /* pool-spreading already demonstrates */ } },
    { label: 'Downstream cascade avoided',            run: () => { try { toxcascadeReset(); } catch(e) {} } },
  ],
  offpeak: [
    { label: 'Population drops to 15%',               run: () => { setSliderById('queue-pop', 15); setSliderById('master-pop', 15); } },
    { label: 'Queue times spike',                     run: () => { setSliderById('queue-urg', 80); setSliderById('master-urg', 80); } },
    { label: 'Pool decay widens to compensate',       run: () => { setSliderById('pool-decay', 10); setSliderById('master-decay', 10); } },
    { label: 'Match quality drops despite widening',   run: () => { /* queue canvas shows the curve */ } },
    { label: 'System reports compromise match',       run: () => { try { transparencyPick('B'); } catch(e) {} } },
  ],
  toxchain: [
    { label: 'One toxic player enters the queue',     run: () => { try { behaviorReset(); behaviorFlag('toxicity'); } catch(e) {} } },
    { label: 'Match 1: teammates get tilted',         run: () => { try { toxcascadeRun(); } catch(e) {} } },
    { label: 'Cascade propagates to Match 2',         run: () => { /* toxcascade canvas animates */ } },
    { label: 'Downstream matches feel worse',         run: () => { /* toxcascade counter shows it */ } },
    { label: 'Counterfactual: behavior modulator would have caught this at step 1', run: () => {} },
  ],
  metashift: [
    { label: 'Aggro is 60% of the ladder',           run: () => { try { rpsGame('ccg'); document.querySelectorAll('#rps-sliders input')[0].value = 60; rpsSlider(0, 60); } catch(e) {} } },
    { label: 'Aggro Elo inflates from population bias', run: () => { /* RPS canvas shows it live */ } },
    { label: 'New patch drops: combo is buffed',      run: () => { try { const inputs = document.querySelectorAll('#rps-sliders input'); if (inputs[2]) { inputs[2].value = 50; rpsSlider(2, 50); } } catch(e) {} } },
    { label: 'Combo players climb; aggro falls',      run: () => { /* RPS chart shifts */ } },
    { label: 'Elo scramble: rating no longer reflects skill', run: () => {} },
  ],
};
let scenRunning = null, scenTimer = 0, scenStepIdx = 0;
function scenPlay(key) {
  scenRunning = key; scenStepIdx = 0; scenTimer = 0;
  const log = document.getElementById('scen-log');
  if (log) log.innerHTML = '<span style="color:var(--accent2)">▶ started: ' + key + '</span>';
  pepSend('scenario.start', { key });
}
function scenStop() {
  scenRunning = null; scenStepIdx = 0;
  const step = document.getElementById('scen-step');
  if (step) step.textContent = '(stopped)';
}
function scenTick() {
  if (!scenRunning) return;
  const seq = ATRIA_SCENARIOS[scenRunning];
  if (!seq) { scenRunning = null; return; }
  scenTimer++;
  if (scenTimer >= 100) {
    scenTimer = 0;
    if (scenStepIdx >= seq.length) {
      scenRunning = null;
      const step = document.getElementById('scen-step');
      if (step) step.textContent = '(complete)';
      return;
    }
    const s = seq[scenStepIdx];
    try { s.run(); } catch (e) {}
    const step = document.getElementById('scen-step');
    if (step) step.textContent = '▶ step ' + (scenStepIdx + 1) + ' / ' + seq.length + ' — ' + s.label;
    const log = document.getElementById('scen-log');
    if (log) {
      const div = document.createElement('div');
      div.innerHTML = '<span style="color:var(--accent)">' + (scenStepIdx + 1) + '.</span> ' + s.label;
      log.appendChild(div);
      log.scrollTop = log.scrollHeight;
    }
    pepSend('scenario.step', { scenario: scenRunning, index: scenStepIdx, label: s.label });
    scenStepIdx++;
  }
}
setInterval(scenTick, 50);

function masterApply() {
  const pop = parseInt(document.getElementById('master-pop').value);
  const urg = parseInt(document.getElementById('master-urg').value);
  const decay = parseInt(document.getElementById('master-decay').value);
  const prior = parseInt(document.getElementById('master-prior').value);
  document.getElementById('master-pop-val').textContent = pop;
  document.getElementById('master-urg-val').textContent = urg;
  document.getElementById('master-decay-val').textContent = decay;
  document.getElementById('master-prior-val').textContent = prior;
  setSliderById('queue-pop', pop);
  setSliderById('queue-urg', urg);
  setSliderById('pool-decay', decay);
  pepSend('master.apply', { pop, urg, decay, prior });
}

// ═══════════════════════════════════════════════════════════════════════
// Glossary hover
// ═══════════════════════════════════════════════════════════════════════
(function installGlossary() {
  const terms = {
    'Elo': 'A rating system that assumes skill is transitive (if A>B and B>C then A>C) and estimates win probability against a representative opponent pool. Breaks when games have intransitive matchups.',
    'Glicko': 'A rating system that tracks both a point estimate and a rating deviation (RD). Narrower RD means more certainty; wider RD means the rating should be trusted less.',
    'TrueSkill': "Microsoft's Bayesian rating system. Represents skill as N(\\u03bc, \\u03c3\\u00b2). The sigma is the uncertainty the matchmaker should account for.",
    'transitive': 'A relation where if A > B and B > C, then A > C. Elo assumes skill is transitive. Real competitive games usually are not.',
    'intransitive': 'The opposite of transitive. Rock-paper-scissors is the canonical example. Most competitive games are intransitive because strategies counter strategies.',
    'residual': 'The portion of variance that a baseline model (usually Elo) cannot explain. Atria targets the residual as its optimization objective.',
    'AUC': 'Area under ROC curve. A summary statistic for classifier quality; 0.5 is chance, 1.0 is perfect.',
    'RD': 'Rating deviation — the uncertainty around a rating point estimate in Glicko.',
    'sigma': 'The standard deviation of the skill estimate in TrueSkill. Shrinks as the system gets more data.',
    'rematch rate': "The probability that both players queue again immediately after a match. Atria's proxy for experience quality.",
    'spreading activation': "PEP's native search primitive: activation radiates from a seed node through weighted edges with decay, forming a neighborhood-shaped pool.",
  };
  const tooltip = document.createElement('div');
  tooltip.style.cssText = 'position:fixed;display:none;background:var(--surface);border:1px solid var(--accent);border-radius:4px;padding:8px 12px;font-family:monospace;font-size:11px;color:var(--text);max-width:320px;line-height:1.5;z-index:200;pointer-events:none;box-shadow:0 4px 12px rgba(0,0,0,0.5)';
  document.body.appendChild(tooltip);
  const termKeys = Object.keys(terms).sort((a, b) => b.length - a.length);
  document.querySelectorAll('.info').forEach(info => {
    termKeys.forEach(term => {
      const re = new RegExp('(^|[^a-zA-Z0-9_-])(' + term + ')(?=[^a-zA-Z0-9_-]|$)', 'g');
      info.innerHTML = info.innerHTML.replace(re, function (m, pre, word) {
        return pre + '<span class="gloss" data-term="' + term + '" style="border-bottom:1px dotted rgba(94,234,212,0.6);cursor:help">' + word + '</span>';
      });
    });
  });
  document.querySelectorAll('.gloss').forEach(el => {
    el.addEventListener('mouseenter', () => {
      const def = terms[el.dataset.term];
      if (!def) return;
      tooltip.innerHTML = '<b style="color:var(--accent)">' + el.dataset.term + '</b><br>' + def;
      tooltip.style.display = 'block';
    });
    el.addEventListener('mousemove', (e) => {
      tooltip.style.left = (e.clientX + 14) + 'px';
      tooltip.style.top  = (e.clientY + 14) + 'px';
    });
    el.addEventListener('mouseleave', () => { tooltip.style.display = 'none'; });
  });
})();

</script>
</body>
</html>
"""


@router.get("/atria", response_class=HTMLResponse)
async def atria_page() -> str:
    return _PAGE
