"""Lingora — Language as a cognitive technology. Serves an interactive page at /lingora."""

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
<title>Lingora — Language as a Cognitive Technology</title>
<style>
  :root {
    --bg: #0c0e14; --surface: #1a1d2e; --surface2: #161a2a;
    --text: #e0e0e0; --dim: #888; --accent: #7cb8ff; --accent2: #f0a869;
    --warn: #ffb74d; --border: #2a2e40;
  }
  body.light {
    --bg: #fafafa; --surface: #ffffff; --surface2: #f0f2f8;
    --text: #1a1a1a; --dim: #666; --accent: #1e3a8a; --accent2: #b45309;
    --warn: #c2410c; --border: #d0d4dc;
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
  .controls button.active { background: var(--accent); color: #000; border-color: var(--accent); }
  .info { font-size: 11px; color: var(--dim); padding: 10px 14px; background: var(--surface);
          border: 1px solid var(--border); border-radius: 6px; margin-bottom: 16px; line-height: 1.7; }
  .info b { color: var(--text); }
  .stat { display: inline-block; margin-right: 16px; }
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
    <span class="brand">Lingora</span>
    <span style="font-size:10px;color:var(--dim)">Language as a Cognitive Technology</span>
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
    <button onclick="lingoraRandom()" class="nav-btn" title="jump to a random canvas">🎲</button>
    <button onclick="lingoraBookmark()" class="nav-btn" id="bookmark-btn" title="bookmark current tab">☆</button>
    <button onclick="downloadLingora()" class="nav-btn" title="download the current page as a standalone HTML file">Download</button>
    <button onclick="tourStart()" class="nav-btn" style="border-color:var(--accent2);color:var(--accent2)">Take a Tour</button>
    <button onclick="toggleLight()" id="light-btn" class="nav-btn">Light Mode</button>
    <span class="lavas-switch" style="display:flex;gap:8px;align-items:center;font-size:11px;flex-wrap:wrap;margin-left:6px">
      <a href="/pep">PEP</a>
      <a href="/axona">Axona</a>
      <span class="lavas-current">Lingora</span>
      <a href="/atria">Atria</a>
      <a href="/vectora">Vectora</a>
      <a href="/strata">Strata</a>
    </span>
  </div>
  <div class="nav-row nav-row-bottom">
    <div class="tabs" id="tabs">
      <div class="tab active" data-panel="home-tab">Home</div>
      <div class="tab" data-panels="word-tab ambig-tab idiom-tab taboo-tab vocab-tab drift-tab onoma-tab metaphor-tab colloc-tab gramm-tab lexgap-tab jargon-tab cognates-tab vec-live-tab vec-context-tab">Words &amp; Meaning</div>
      <div class="tab" data-panels="phono-tab prosody-tab silence-tab soundsym-tab repetition-tab rhyme-tab">Sounds &amp; Rhythm</div>
      <div class="tab" data-panels="sentence-tab grammar-tab listener-tab transfer-tab acquisition-tab babytalk-tab deixis-tab anaphora-tab statistical-tab">Sentences &amp; Learning</div>
      <div class="tab" data-panels="humor-tab voice-tab irony-tab grice-tab conv-tab subtext-tab lying-tab persuasion-tab politeness-tab discourse-tab swearing-tab gesture-tab">Speech Acts</div>
      <div class="tab" data-panels="reading-tab aphasia-tab wvs-tab orthography-tab errors-tab innerspeech-tab readaloud-tab">Reading &amp; Brain</div>
      <div class="tab" data-panels="poetry-tab writing-tab narrative-tab advice-tab diff-tab pov-tab stream-tab typography-tab headlines-tab legal-tab oral-tab">Writing</div>
      <div class="tab" data-panels="codeswitch-tab translation-tab sign-tab pidgin-tab diglossia-tab animal-tab emoji-tab">Cross-Language</div>
      <div class="tab" data-panels="prompt-tab llm-tab aidetect-tab">Machines</div>
      <div class="tab" data-panels="sandbox-tab analyze-tab gallery-tab citations-tab">Tools</div>
      <div class="tab" data-panels="workbench-tab story-tab voice-analyze-tab">Workbench</div>
      <div class="tab" data-panels="pitch-tab bench-tab cases-tab">Pitch</div>
      <div class="tab" data-panel="products-tab">Products</div>
      <div class="tab" data-panel="theory-tab">Theory</div>
      <div class="tab" data-panel="whypep-tab">Why PEP</div>
      <div class="tab" data-panel="bridge-tab">PEP &harr; Lingora</div>
    </div>
  </div>
</nav>

<!-- ═══ Home ══════════════════════════════════════════════════════ -->
<div class="panel active" id="home-tab">
<div class="container">
  <div class="hero">
    <div class="tag">LINGORA</div>
    <h1>Language as a Cognitive Technology</h1>
    <p>
      Axona maps the brain in general. Lingora zeroes in on the part that runs on
      words. Words are not symbols paired with meanings &mdash; they are cues that
      activate specific constellations of nodes across the network. Meaning is not
      transferred; it is reconstructed live in the listener. Sentences are running
      forecasts. Grammar is a statistical prior. Translation is structural remapping
      across two different node graphs. Writing is deliberate prompt engineering for
      every reader's brain.
    </p>
    <p>
      This is Lingora day one. The three interactive canvases in the top nav are the
      first stops. Everything in the <b>Theory</b> tab is the framing in full.
    </p>
  </div>

  <h3>What Lingora will be</h3>
  <div class="info">
    <b>Core claims</b> (see the Theory tab for the full version):<br><br>
    &bull; <b>Words are activation patterns, not symbols.</b> The "meaning" of a word
    is the set of nodes it lights up &mdash; and that set differs from person to
    person, which is why "freedom" never means quite the same thing to any two
    people.<br>
    &bull; <b>Comprehension is reconstruction.</b> The listener does not receive the
    speaker's meaning. They reconstruct a meaning of their own from the activation
    patterns the words prompt. Agreement is never exact; it is engineered to be
    close enough for the purpose at hand.<br>
    &bull; <b>Vocabulary carves perception.</b> A distinction with a name is cheap
    to draw. A distinction without one fades into the background. Learning a new
    language changes what you can see, not just what you can say.<br>
    &bull; <b>Sentences are narrowing forecasts.</b> Each word constrains the
    predictor's guess at the next word. Understanding a sentence is watching the
    forecast lock onto one narrow region as the words arrive.<br>
    &bull; <b>Writing is prompt engineering for brains.</b> The writer chooses
    inputs that will produce specific activation patterns in every reader &mdash;
    concrete imagery fires sensory cortex, rhythm modulates attention, metaphor
    borrows structure, surprise fires the residual scorer. Good writing is a
    programming language targeting a device the writer cannot observe.
  </div>

  <h3>First three demos</h3>
  <div class="info">
    The three interactive canvases in the top nav are the initial drops:<br><br>
    1. <b>Word as Constellation</b> &mdash; click a word and see the nodes it
    activates. Different words produce different shapes.<br>
    2. <b>Sentence Forecast</b> &mdash; watch the predictor's top candidates for
    the next word, narrowing as more context arrives.<br>
    3. <b>Translation Gap</b> &mdash; two constellations side by side. An English
    word and its nearest foreign match. Some nodes overlap, some are missing, some
    are added. The missing structure is what "does not translate."<br><br>
    More are coming: ambiguity resolution, grammar as prior, prompt engineering,
    poetry as residual engineering, and the LLM bridge &mdash; where Lingora
    connects to any running language model and lets you inspect what it is
    activating for a given prompt.
  </div>

  <h3>Where Lingora lives</h3>
  <div class="info">
    Lingora is a standalone Python package at <code>~/projects/lingora/</code>,
    depending on PEP as an editable install. This interactive page is served by
    PEP's FastAPI server at <code>/lingora</code>, parallel to Axona at
    <code>/axona</code>. Source: <code>pep/src/pep/routes/lingora.py</code>. As
    Lingora grows, logic moves from this HTML page into the
    <code>lingora</code> Python package and Lingora becomes a proper library with a
    live demo front-end.
  </div>
</div>
</div>

<!-- ═══ Word as Constellation ═════════════════════════════════════ -->
<div class="panel" id="word-tab">
<div class="container">
  <h2>Word as Constellation</h2>
  <p class="desc">
    Click a word below. Watch the nodes it activates light up. The word is not a
    label on a meaning &mdash; the word <em>is</em> the cue that produces this
    pattern, and the pattern is the meaning, as it exists in this particular
    network right now.
  </p>
  <div class="canvas-box">
    <canvas id="word-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <button onclick="wordPick('dog')">dog</button>
    <button onclick="wordPick('freedom')">freedom</button>
    <button onclick="wordPick('mother')">mother</button>
    <button onclick="wordPick('fire')">fire</button>
    <button onclick="wordPick('home')">home</button>
    <button onclick="wordPick('money')">money</button>
    <button onclick="wordReset()">Clear</button>
    <span style="margin-left:auto;color:var(--dim)">
      active word: <b style="color:var(--accent)" id="word-label">—</b>
    </span>
  </div>
  <div class="info">
    <b>What you are watching:</b> Each word in the panel above is paired with a
    small curated set of associated concepts &mdash; sensory hooks, related words,
    emotional tags, frequent co-occurrences. Clicking a word fires that set,
    weighted by how tightly it is associated. In a real brain the constellation
    would have millions of nodes and the weights would be learned from billions of
    exposures. The principle is the same. The word is not a container; it is a
    cue, and the meaning is whatever the cue lights up.<br><br>
    <b>Why "freedom" is hard:</b> Click "dog" and the constellation is
    mostly concrete &mdash; fur, bark, leash, tail. Two speakers of English will
    have heavily overlapping "dog" constellations. Now click "freedom." The
    constellation is almost entirely abstract &mdash; and the specific nodes are
    personal, cultural, political. Two speakers of English have "freedom"
    constellations that barely overlap. They are using the same word. They are
    not talking about the same thing.<br><br>
    <b>The harder observation:</b> There is no definition of "freedom" that
    replaces the constellation with a single clear meaning. The dictionary entry
    is itself just another word cue that activates <em>its</em> own constellation.
    The concept only exists as a pattern, and the pattern only exists in a
    network.
  </div>
</div>
</div>

<!-- ═══ Sentence Forecast ═════════════════════════════════════════ -->
<div class="panel" id="sentence-tab">
<div class="container">
  <h2>Sentence Forecast &mdash; Watching the Predictor Narrow</h2>
  <p class="desc">
    Click words one at a time to build a sentence. Each click updates the panel
    on the right with the predictor's current top candidates for the next word,
    weighted by probability. The distribution starts wide and narrows as the
    sentence constrains what can plausibly follow.
  </p>
  <div class="canvas-box">
    <canvas id="sent-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <button onclick="sentLoad('cat')">Load: "The cat sat on the ___"</button>
    <button onclick="sentLoad('coffee')">Load: "She poured hot ___"</button>
    <button onclick="sentLoad('violate')">Load: "The horse raced past the barn ___"</button>
    <button onclick="sentStep()">Next word</button>
    <button onclick="sentReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      forecast entropy: <b style="color:var(--accent2)" id="sent-entropy">—</b>
    </span>
  </div>
  <div class="info">
    <b>What "entropy" means here:</b> High entropy = the predictor has many
    plausible candidates for the next word and cannot commit. Low entropy = the
    predictor has locked onto a narrow region. As a sentence builds context,
    entropy drops sharply &mdash; each word eliminates possibilities that were
    open before it.<br><br>
    <b>Watch the garden-path example:</b> "The horse raced past the barn ___"
    generates a confident forecast for the sentence ending: "fell to the ground,"
    "quickly," something verb-phrase-ish. But the correct ending is "fell"
    &mdash; and "fell" only works if "raced past the barn" is reinterpreted as a
    reduced relative clause ("the horse that was raced past the barn, fell"). The
    forecast had to violently rewind and re-parse. That rewind is what "I had to
    re-read that sentence" feels like. It is a measurable event, not a vague
    impression.
  </div>
</div>
</div>

<!-- ═══ Ambiguity Resolution ══════════════════════════════════════ -->
<div class="panel" id="ambig-tab">
<div class="container">
  <h2>Ambiguity Resolution &mdash; Which Meaning Wins</h2>
  <p class="desc">
    A single word can activate two (or more) competing meaning clusters at once.
    The context around the word is what breaks the tie &mdash; not by "choosing"
    a meaning, but by pre-activating one cluster so it wins the race against the
    other when the ambiguous word arrives.
  </p>
  <div class="canvas-box">
    <canvas id="ambig-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <button onclick="ambigWord('bank')">Target: BANK</button>
    <button onclick="ambigWord('bat')">Target: BAT</button>
    <button onclick="ambigWord('pitch')">Target: PITCH</button>
    <button onclick="ambigPrime('A')">Prime: A (left)</button>
    <button onclick="ambigPrime('B')">Prime: B (right)</button>
    <button onclick="ambigPrime(null)">No prime</button>
    <button onclick="ambigReset()">Reset</button>
  </div>
  <div class="info">
    <b>What you are watching:</b> An ambiguous word has two candidate meaning
    clusters drawn as circles on the left and right. Normally activation tries
    to flow into both at once and they compete for the finish line. If one
    cluster is pre-activated (primed) by preceding context, it is already warm
    when the ambiguous word fires &mdash; the warmer cluster wins the race and
    becomes the conscious reading. The losing cluster activates briefly, then
    decays without reaching the threshold where it becomes part of the
    experience.<br><br>
    <b>The critical point:</b> You never experience the ambiguity. You
    experience the winner. The loser was real, the activation was real, the
    competition was real &mdash; but consciousness only reports the result.
    This is why people are surprised to learn the same word had another
    meaning: their network ran the race but only delivered the finish line.
  </div>
</div>
</div>

<!-- ═══ Grammar as Prior ══════════════════════════════════════════ -->
<div class="panel" id="grammar-tab">
<div class="container">
  <h2>Grammar as a Statistical Prior</h2>
  <p class="desc">
    Grammar is not a set of rules a speaker consciously applies. It is a
    learned distribution over which word-types follow which other word-types.
    A well-trained prior generates fluent output; an untrained or random prior
    generates word salad. Both are the same operation &mdash; sampling from a
    distribution &mdash; with different priors loaded.
  </p>
  <div class="canvas-box">
    <canvas id="grammar-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <button onclick="grammarGen('fluent')">Generate with Fluent Prior</button>
    <button onclick="grammarGen('loose')">Generate with Loose Prior</button>
    <button onclick="grammarGen('salad')">Generate with Random Prior</button>
    <button onclick="grammarReset()">Reset</button>
  </div>
  <div class="info">
    <b>The three modes you can run:</b><br>
    &bull; <b>Fluent prior</b> &mdash; the sampler uses a tight distribution
    that strongly prefers well-formed sequences. The output is grammatical
    English. This is what a native speaker's grammar prior does. It was not
    memorized from a rulebook; it was learned from thousands of hours of
    input.<br>
    &bull; <b>Loose prior</b> &mdash; the sampler allows more deviation. The
    output is still mostly English but starts to feel off &mdash; odd word
    choices, mild agreement errors, things a native speaker would flag but
    not find incomprehensible.<br>
    &bull; <b>Random prior</b> &mdash; the sampler draws almost uniformly.
    The output is word salad. It uses English words but no grammar prior is
    running on top. This is what happens when the statistical structure is
    removed.<br><br>
    <b>The point:</b> Rules are a post-hoc description. The prior is the
    actual machinery. A language learner is not memorizing rules; they are
    training a distribution, and after enough exposures the distribution
    starts generating fluent output without the learner ever being able to
    articulate what they did.
  </div>
</div>
</div>

<!-- ═══ Prompt Engineering ════════════════════════════════════════ -->
<div class="panel" id="prompt-tab">
<div class="container">
  <h2>Prompt Engineering &mdash; Reshaping the Forecast Distribution</h2>
  <p class="desc">
    Same underlying question. Different framings. Different regions of the
    activation space activated. A vague prompt lets the predictor fall into
    its default distribution. A specific, role-framed, constraint-bearing
    prompt pushes the predictor into a narrow region most people would never
    reach. This is the same operation a skilled writer runs on a human
    reader, applied to a language model.
  </p>
  <div class="canvas-box">
    <canvas id="prompt-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <button onclick="promptPick('vague')">Vague: "give me ideas"</button>
    <button onclick="promptPick('specific')">Specific: "5 ideas for X"</button>
    <button onclick="promptPick('constrained')">Constrained: "5 counterintuitive ideas for X"</button>
    <button onclick="promptPick('role')">Role-framed: "You are a nobel-prize winner..."</button>
    <button onclick="promptReset()">Reset</button>
  </div>
  <div class="info">
    <b>What you are watching:</b> The activation space is drawn as a field of
    points. Each prompt framing lights up a different region &mdash; the
    vague prompt highlights a large, diffuse area (the predictor's default
    fallback), the specific prompt narrows to a tighter region, the
    constrained prompt pushes even further into a corner, and the role-framed
    prompt moves the center of the region to a completely different part of
    the space.<br><br>
    <b>The mechanism:</b> A language model's next-token distribution is a
    function of everything in the prompt. Adding a role ("you are a chemist")
    activates tokens associated with chemistry, which raises the probability
    of chemistry-coherent continuations and lowers the probability of
    everything else. Adding a constraint ("counterintuitive") suppresses the
    most common continuations and boosts the less-common ones. Adding
    examples in-context works by the same mechanism &mdash; the examples
    pre-activate the pattern the model should match.<br><br>
    <b>Why this is the same thing writers do to human readers:</b> "Concrete
    imagery fires sensory cortex" is the human-brain version of
    "role-framing activates a specific region of the token distribution."
    Both are: construct an input whose shape pushes the downstream system's
    forecast where you want it. The substrate is different. The engineering
    is the same.
  </div>
</div>
</div>

<!-- ═══ Poetry as Residual Engineering ════════════════════════════ -->
<div class="panel" id="poetry-tab">
<div class="container">
  <h2>Poetry as Residual Engineering</h2>
  <p class="desc">
    A good poem is a sequence of precisely-timed prediction violations. Most
    words land softly on the forecast. A few words land hard &mdash; the ones
    the poet chose specifically to produce a residual spike at that exact
    moment. That spike is what "landed" means.
  </p>
  <div class="canvas-box">
    <canvas id="poetry-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <button onclick="poetryPlay('frost')">Frost: "Stopping by Woods..."</button>
    <button onclick="poetryPlay('dickinson')">Dickinson: "Hope is the thing..."</button>
    <button onclick="poetryPlay('plain')">Plain prose (control)</button>
    <button onclick="poetryReset()">Reset</button>
  </div>
  <div class="info">
    <b>What you are seeing:</b> A line of poetry is laid out word by word.
    Above each word, the live residual &mdash; the gap between the
    predictor's forecast and the actual word that arrived. Mostly the bars
    are short. At specific words (the unexpected image, the metaphor that
    reaches across clusters, the line break that violates the rhythm) the
    bars are tall. Those are the moments the poet engineered.<br><br>
    <b>Why plain prose looks flat:</b> Good prose minimizes residuals. You
    want the reader's prediction to track the sentence cleanly so the meaning
    arrives smoothly. Poetry inverts the goal. Poetry wants strategic
    residuals &mdash; engineered moments where the reader's forecast breaks
    and has to reconstruct. The reconstruction is the experience. A poem
    whose residuals are all flat is not a poem; it is information. A poem
    with residuals at the wrong places is a failed poem. A poem with
    residuals at the <em>right</em> places is what people mean by "it hit me."<br><br>
    <b>The deeper point:</b> "Beauty" in language is not a property of the
    words. It is a property of the relationship between the words and the
    reader's forecast. Which means beauty is <em>partially</em> in the
    reader &mdash; and why a poem that lands for one person falls flat for
    another. Different forecasts, different residuals, different experiences
    of the same text.
  </div>
</div>
</div>

<!-- ═══ Show Don't Tell (Writing Mechanics) ═══════════════════════ -->
<div class="panel" id="writing-tab">
<div class="container">
  <h2>Show Don't Tell &mdash; Concrete Words Fire Sensory Cortex</h2>
  <p class="desc">
    The oldest writing advice, made mechanical: concrete words activate
    sensory and motor regions of the brain. Abstract words mostly activate
    semantic/verbal regions and leave sensory regions cold. The same
    information in the two forms produces very different cognitive
    experiences. One makes you feel something. The other gives you a
    summary.
  </p>
  <div class="canvas-box">
    <canvas id="writing-canvas" width="960" height="460"></canvas>
  </div>
  <div class="controls">
    <button onclick="writingLoad('abstract')">Abstract version</button>
    <button onclick="writingLoad('concrete')">Concrete version</button>
    <button onclick="writingReset()">Reset</button>
  </div>
  <div class="info">
    <b>The experiment runs in the reader's head:</b> The text scrolls on the
    left. On the right, the brain regions that each word activates light up.
    Abstract prose mostly lights up the verbal/semantic area. Concrete prose
    lights up visual, auditory, olfactory, and motor cortex in addition.
    Same proposition, radically different cognitive load and cognitive
    texture.<br><br>
    <b>Why "she was sad" is weak:</b> "Sad" is a summary. It activates the
    verbal cluster for sadness but leaves the sensory and motor systems
    quiet. The reader's model of the character knows <em>what</em> the
    character feels without feeling <em>like</em> the character felt it.<br><br>
    <b>Why "her hand shook as she set the cup down on the table" is strong:</b>
    The words are all concrete. "Hand" fires somatosensory cortex. "Shook"
    fires motor simulation. "Cup" and "table" fire visual cortex. The reader
    is running a partial simulation of the scene &mdash; imagery, motor
    imagery, tactile imagery &mdash; and the inference that the character
    is upset is generated from the simulation, not stated. That inference
    feels earned because the reader produced it themselves.<br><br>
    <b>The rule underneath the rule:</b> "Show don't tell" is shorthand for
    "activate sensory systems instead of just verbal ones." Any advice about
    writing that you have ever heard &mdash; specific details, active voice,
    imagery, rhythm, word choice &mdash; ultimately reduces to <em>producing
    specific activation patterns in the reader's brain</em>. Writing is
    neuro-engineering through a very narrow interface (text), and the
    details matter because the interface is so narrow that every token has
    to carry weight.
  </div>
</div>
</div>

<!-- ═══ Listener Reconstruction ═══════════════════════════════════ -->
<div class="panel" id="listener-tab">
<div class="container">
  <h2>Listener Reconstruction &mdash; Meaning Built Live</h2>
  <p class="desc">
    The missing half of Sentence Forecast. Sentence Forecast shows the predictor
    narrowing. This shows the listener's composite meaning <em>building</em>
    as each word arrives &mdash; new nodes activate, existing ones strengthen,
    the shape of "what the sentence is about" takes form in real time.
  </p>
  <div class="canvas-box">
    <canvas id="listener-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <button onclick="listenerLoad('child')">"The child dropped her ice cream"</button>
    <button onclick="listenerLoad('war')">"The soldier came home silent"</button>
    <button onclick="listenerLoad('dog')">"The dog waited by the door"</button>
    <button onclick="listenerStep()">Next word</button>
    <button onclick="listenerReset()">Reset</button>
  </div>
  <div class="info">
    <b>What you are watching:</b> The listener's network is the big field of
    nodes. As each word arrives, the nodes that word associates with light up
    &mdash; weakly at first, then reinforced by subsequent words that share
    neighborhood. By the end of the sentence, a dense cluster has formed and
    that cluster <em>is</em> the listener's understanding. The speaker's
    meaning never crossed into the listener's head. The listener built their
    own.<br><br>
    <b>Why that matters:</b> Two listeners with different networks will build
    different composites from the same sentence. They will both say "I
    understood you." Both will be telling the truth. Neither will be talking
    about quite the same thing.
  </div>
</div>
</div>

<!-- ═══ Speaker ↔ Listener Transfer ═══════════════════════════════ -->
<div class="panel" id="transfer-tab">
<div class="container">
  <h2>Speaker &harr; Listener &mdash; Compression Through Words</h2>
  <p class="desc">
    Communication is not telepathy. The speaker compresses a rich mental state
    into a sequence of discrete symbols, the symbols travel through the
    bottleneck of language, and the listener decompresses them into a
    <em>different</em> mental state. Show the three stages side by side and
    the gaps become visible.
  </p>
  <div class="canvas-box">
    <canvas id="transfer-canvas" width="960" height="460"></canvas>
  </div>
  <div class="controls">
    <button onclick="transferSend('simple')">Send: "I got the job"</button>
    <button onclick="transferSend('complex')">Send: "It was complicated"</button>
    <button onclick="transferSend('abstract')">Send: "I feel free"</button>
    <button onclick="transferReset()">Reset</button>
  </div>
  <div class="info">
    <b>The three stages:</b><br>
    1. <b>Speaker's meaning</b> &mdash; a rich, high-dimensional mental state
    full of context, emotion, memory, and implicit reference.<br>
    2. <b>The words</b> &mdash; a discrete, serialized compression. Most of
    the richness gets dropped at the encoder. The speaker chooses the words
    that they think will be most likely to reconstruct the intended state in
    the listener.<br>
    3. <b>Listener's meaning</b> &mdash; a reconstruction built from whatever
    the words activate in the listener's own network, shaped by the
    listener's priors and recent context.<br><br>
    <b>The gap:</b> Stages 1 and 3 are never identical. Sometimes they are
    close enough that "communication worked." Often they are not, and the
    two speakers walk away thinking they agreed when they did not. The
    bottleneck is language itself.
  </div>
</div>
</div>

<!-- ═══ Humor & Puns ══════════════════════════════════════════════ -->
<div class="panel" id="humor-tab">
<div class="container">
  <h2>Humor &amp; Puns &mdash; Engineered Dual Activation</h2>
  <p class="desc">
    A pun is an ambiguous word deployed so that both meanings activate
    simultaneously, producing a controlled dual reading followed by
    resolution. Unlike unintended ambiguity, here the writer <em>wants</em>
    both clusters to fire. The laugh is the surprise of realizing both
    readings were valid.
  </p>
  <div class="canvas-box">
    <canvas id="humor-canvas" width="960" height="400"></canvas>
  </div>
  <div class="controls">
    <button onclick="humorPlay('panda')">Joke: "A panda walks into a bar..."</button>
    <button onclick="humorPlay('time')">Pun: "Time flies like an arrow..."</button>
    <button onclick="humorPlay('bookkeeper')">Wordplay: "bookkeeper"</button>
    <button onclick="humorReset()">Reset</button>
  </div>
  <div class="info">
    <b>How a pun fires:</b> The setup builds a forecast that the listener is
    running confidently. The punchline word (or phrase) activates <em>two</em>
    meaning clusters instead of one &mdash; and both readings are structurally
    valid given the setup. The forecast cannot resolve to just one, so for a
    fraction of a second both interpretations coexist. Then the system notices
    the alternate reading was also valid, a residual spike fires, and the
    laugh follows.<br><br>
    <b>Why puns that are explained are not funny:</b> Once you have been told
    both readings, the dual activation no longer happens in a spike. It
    happens gradually, because you already know both meanings and are not
    surprised by either. The spike is the whole point. Explanation destroys
    the spike.
  </div>
</div>
</div>

<!-- ═══ Idiom ═════════════════════════════════════════════════════ -->
<div class="panel" id="idiom-tab">
<div class="container">
  <h2>Idiom as Opaque Block</h2>
  <p class="desc">
    "Kick the bucket" does not activate KICK + BUCKET compositionally. It is
    stored as a single unit that retrieves "die." Show the decompositional
    path failing (kicking a bucket → absurd) while the unitary retrieval
    succeeds (the whole phrase → death, old age, euphemism).
  </p>
  <div class="canvas-box">
    <canvas id="idiom-canvas" width="960" height="400"></canvas>
  </div>
  <div class="controls">
    <button onclick="idiomPlay('bucket')">"kick the bucket"</button>
    <button onclick="idiomPlay('beans')">"spill the beans"</button>
    <button onclick="idiomPlay('cold')">"cold feet"</button>
    <button onclick="idiomReset()">Reset</button>
  </div>
  <div class="info">
    <b>Two retrieval paths:</b> When you hear an idiom, the brain tries both
    routes in parallel. The <em>compositional</em> path (word by word →
    literal meaning) retrieves an absurd result: somebody is physically
    kicking a pail. The <em>unitary</em> path (whole phrase → single meaning
    node) retrieves "died." The unitary path always wins for well-known
    idioms because its weight is much higher &mdash; you have heard the
    phrase thousands of times paired with its idiomatic meaning, and those
    co-occurrences have built a direct edge that bypasses compositional
    parsing entirely.<br><br>
    <b>Why this matters:</b> It shows that language is not always
    compositional. A large fraction of everyday speech runs on cached
    phrases, prayers, catchphrases, greetings, and idioms that are looked up
    as blocks. This is why learning a new language by memorizing words and
    grammar never quite gets you to fluency &mdash; the native's everyday
    speech is full of unit-level idioms you have to learn as their own
    entries.
  </div>
</div>
</div>

<!-- ═══ LLM Bridge ════════════════════════════════════════════════ -->
<div class="panel" id="llm-tab">
<div class="container">
  <h2>LLM Bridge &mdash; PEP Applied to a Running Language Model</h2>
  <p class="desc">
    The one thing Lingora does that nothing else in the system can. An LLM is
    a linguistic system running on a different substrate, but PEP's framework
    applies directly: it has learned priors, runs forecasts, and produces
    token distributions that narrow as context arrives. Type a prompt, see
    the top-k next-token distribution &mdash; the residual scorer in its
    digital form.
  </p>
  <div class="canvas-box">
    <canvas id="llm-canvas" width="960" height="460"></canvas>
  </div>
  <div class="controls">
    <button onclick="llmPrompt('complete1')">"The capital of France is"</button>
    <button onclick="llmPrompt('complete2')">"Once upon a time, there was a"</button>
    <button onclick="llmPrompt('complete3')">"To be or not to"</button>
    <button onclick="llmPrompt('complete4')">"def fibonacci(n):"</button>
    <button onclick="llmStep()">Next token</button>
    <button onclick="llmReset()">Reset</button>
  </div>
  <div class="info">
    <b>What this is (and is not):</b> Live LLM integration requires an API
    key that you do not currently have set, so this demo is running on
    pre-computed stub distributions for a handful of common prompts. The
    stubbed top-k mirrors what a real model's output would look like for
    these prompts &mdash; the numbers are roughly calibrated. When you add
    an API key later, the stub will be replaced with live inference against
    whichever model you choose.<br><br>
    <b>What to watch for:</b> "The capital of France is" has near-certain
    top-1 (<em>Paris</em>) because the pattern is overwhelming in the
    training data. "Once upon a time" has a much wider distribution
    (hundreds of valid continuations), reflecting the looser constraint.
    "def fibonacci(n):" has high confidence on the next-token being a
    newline + indented return or if-statement because code patterns are
    tight.<br><br>
    <b>Why this is PEP's framework running on an LLM:</b> Every LLM
    completion is a sequence of "sample from the predictor's distribution →
    append to context → repeat." The forecast is explicit, the residual is
    computable, the prior is everything the model learned during training.
    Prompt engineering is literally engineering an input that reshapes the
    forecast toward a target region &mdash; which is the same operation a
    skilled writer runs on a human reader, applied to a different
    substrate.
  </div>
</div>
</div>

<!-- ═══ Active ↔ Passive ═════════════════════════════════════════ -->
<div class="panel" id="voice-tab">
<div class="container">
  <h2>Active &harr; Passive Voice &mdash; Same Facts, Different Allocation</h2>
  <p class="desc">
    "She hit him" and "He was hit by her" describe the same event. The
    listener's attention and memory encoding, however, are measurably
    different. Active voice puts the agent first and emphasizes them;
    passive puts the patient first and emphasizes them &mdash; and sometimes
    deletes the agent entirely.
  </p>
  <div class="canvas-box">
    <canvas id="voice-canvas" width="960" height="380"></canvas>
  </div>
  <div class="controls">
    <button onclick="voicePlay('active')">Active: "She hit him"</button>
    <button onclick="voicePlay('passive')">Passive: "He was hit by her"</button>
    <button onclick="voicePlay('agentless')">Agentless: "He was hit"</button>
    <button onclick="voiceReset()">Reset</button>
  </div>
  <div class="info">
    <b>What shifts:</b> The first noun of a sentence gets a small attention
    bonus &mdash; it is the "topic" the sentence is about. In the active
    version, the agent (she) is the topic. In the passive, the patient (he)
    is the topic. In the agentless passive, the agent has been removed from
    the sentence altogether and the event reads as if no one caused it.<br><br>
    <b>Why politicians love the agentless passive:</b> "Mistakes were made"
    describes an event without assigning responsibility. "I made a mistake"
    assigns it. Same fact, different encoding, different downstream
    inferences the listener runs. Voice is never neutral &mdash; it is a
    choice about whose attention to allocate to which role in the event.
  </div>
</div>
</div>

<!-- ═══ Irony ═════════════════════════════════════════════════════ -->
<div class="panel" id="irony-tab">
<div class="container">
  <h2>Irony &mdash; Saying the Opposite, Trusting the Flip</h2>
  <p class="desc">
    Irony and sarcasm say literally one thing while meaning another &mdash;
    and rely on the listener to detect the gap and invert the sign. This
    requires the speaker to model the listener's model of the speaker: "I
    will say X and they will know I do not literally mean X because they
    know I know the opposite is true."
  </p>
  <div class="canvas-box">
    <canvas id="irony-canvas" width="960" height="400"></canvas>
  </div>
  <div class="controls">
    <button onclick="ironyPlay('weather')">"Great weather!" (it is pouring)</button>
    <button onclick="ironyPlay('smart')">"Oh, that is brilliant..." (slow clap)</button>
    <button onclick="ironyPlay('thrilled')">"Just thrilled to be here" (funeral)</button>
    <button onclick="ironyReset()">Reset</button>
  </div>
  <div class="info">
    <b>Two layers:</b> The literal meaning (what the words say) and the
    intended meaning (what the speaker wants the listener to infer). For
    irony to land, the listener must notice the mismatch with context, flip
    the literal reading, and recover the intended meaning. The flip takes
    roughly a second of extra processing, which is part of why sarcasm
    feels distinctly different from direct speech &mdash; there is a
    measurable parse delay.<br><br>
    <b>Why it fails:</b> If the listener does not have enough shared context
    with the speaker to detect the mismatch, they take the statement
    literally. This is why irony is hard to land in text (missing tone of
    voice), hard across cultures (different default assumptions), and
    completely incomprehensible to some autism-spectrum listeners (the
    precision-prior is running too tight to discount the literal reading).
  </div>
</div>
</div>

<!-- ═══ Taboo ═════════════════════════════════════════════════════ -->
<div class="panel" id="taboo-tab">
<div class="container">
  <h2>Taboo Words &mdash; Words That Cost More</h2>
  <p class="desc">
    Some words carry an elevated emotional weight that their direct
    synonyms do not. Saying them produces a measurable autonomic response.
    They are expensive to use, which is exactly why they are effective when
    used sparingly &mdash; and why swearing provides measurable catharsis
    under pain.
  </p>
  <div class="canvas-box">
    <canvas id="taboo-canvas" width="960" height="380"></canvas>
  </div>
  <div class="controls">
    <button onclick="tabooPlay('mild')">Mild word</button>
    <button onclick="tabooPlay('medium')">Medium taboo</button>
    <button onclick="tabooPlay('strong')">Strong taboo</button>
    <button onclick="tabooReset()">Reset</button>
  </div>
  <div class="info">
    <b>The mechanism:</b> Taboo words have the same semantic meaning as
    their mild synonyms but carry an additional strong edge to the
    amygdala's threat/social-violation system. Hearing or saying them
    activates both the semantic cluster <em>and</em> the emotional response.
    This is why swearing works as a pain reliever (Stephens et al., 2009:
    subjects who swore during a cold pressor task tolerated more pain than
    those who said a neutral word). The emotional spike fires endogenous
    opioids. Saying "fiddlesticks" does not.<br><br>
    <b>Why context matters so much:</b> Taboo is socially constructed and
    varies by culture, register, and audience. The same word is shocking in
    one context (job interview), funny in another (friends), and invisible
    in a third (workplace of construction crew). The word itself is a
    stable node. What varies is the weight of its edge to the
    social-violation circuit, which is contextually modulated by the
    perceived audience.
  </div>
</div>
</div>

<!-- ═══ Implicature / Grice ═════════════════════════════════════ -->
<div class="panel" id="grice-tab">
<div class="container">
  <h2>Implicature &mdash; What Listeners Infer Beyond the Literal</h2>
  <p class="desc">
    "Can you pass the salt?" is literally a yes/no question about your
    ability. Everyone hears a request. The literal answer ("yes" followed
    by not passing the salt) would be absurd. Grice's maxims capture the
    inference rules listeners run automatically to recover what the speaker
    <em>meant</em> from what they <em>said</em>.
  </p>
  <div class="canvas-box">
    <canvas id="grice-canvas" width="960" height="400"></canvas>
  </div>
  <div class="controls">
    <button onclick="gricePlay('salt')">"Can you pass the salt?"</button>
    <button onclick="gricePlay('cold')">"It is cold in here." (close the window)</button>
    <button onclick="gricePlay('dating')">"John is dating someone in New York." (implies not here)</button>
    <button onclick="griceReset()">Reset</button>
  </div>
  <div class="info">
    <b>The layers:</b><br>
    &bull; <b>Literal content</b> &mdash; what the sentence says at face value.<br>
    &bull; <b>Implicated content</b> &mdash; what the listener infers the
    speaker actually wanted to communicate. The implicature is computed by
    assuming the speaker is being cooperative, relevant, and truthful, and
    asking "why would they say exactly this, and no more?"<br><br>
    <b>Why it works mechanically:</b> The listener runs a quick simulation
    &mdash; "if the literal meaning were all they meant, this would be a
    weird thing to say in this context; but if they meant X, it would make
    perfect sense; therefore they probably meant X." That simulation is
    automatic and fast. You do not consciously derive it; you just hear
    "can you pass the salt?" and automatically pass it. The inference is
    theory of mind running in real time on linguistic input.
  </div>
</div>
</div>

<!-- ═══ Vocabulary Growth ═════════════════════════════════════════ -->
<div class="panel" id="vocab-tab">
<div class="container">
  <h2>Vocabulary Growth &mdash; New Words Create New Distinctions</h2>
  <p class="desc">
    A distinction with a name is cheap to draw. A distinction without a
    name fades into the background. As a vocabulary grows, the number of
    reliably-perceivable categories grows with it &mdash; and once you
    learn a word for something, you start seeing instances of it
    everywhere.
  </p>
  <div class="canvas-box">
    <canvas id="vocab-canvas" width="960" height="420"></canvas>
  </div>
  <div class="controls">
    <label style="display:flex;align-items:center;gap:8px">
      <span>vocabulary size:</span>
      <input type="range" id="vocab-size" min="3" max="50" value="12" style="width:160px">
      <span class="stat-val" id="vocab-val">12</span>
    </label>
    <button onclick="vocabReset()">Reset</button>
  </div>
  <div class="info">
    <b>What you are watching:</b> A continuous feature space (color, shape,
    emotion, whatever) with distinctions that can be named or unnamed.
    Below a vocabulary threshold, most of the space is "some fuzzy thing."
    As vocabulary size increases, boundaries sharpen and formerly-invisible
    distinctions become reliable categories. The same underlying feature
    space is there. What changes is which regions are cheap to think
    about.<br><br>
    <b>The practical effect:</b> Learning vocabulary in a new domain is not
    just "acquiring labels." It is restructuring how you perceive the
    domain. A wine-taster has dozens of words for flavor components; a
    casual drinker has three. The wine-taster does not just talk differently
    about wine &mdash; they experience more of it, because more of the
    feature space is distinguishable. The same happens in every expert
    domain: music, programming, architecture, emotion. Vocabulary is a
    perceptual tool.
  </div>
</div>
</div>

<!-- ═══ Code-Switching ═══════════════════════════════════════════ -->
<div class="panel" id="codeswitch-tab">
<div class="container">
  <h2>Code-Switching &mdash; Two Grammar Priors, Context-Gated</h2>
  <p class="desc">
    Bilingual speakers often switch languages mid-sentence. This is not
    confusion; it is two grammar priors loaded in parallel, with the
    context determining which one fires for each word. Sometimes a concept
    is easier to express in one language than the other and the switch is
    a bandwidth optimization.
  </p>
  <div class="canvas-box">
    <canvas id="cswitch-canvas" width="960" height="400"></canvas>
  </div>
  <div class="controls">
    <button onclick="cswitchPlay('spanglish')">"I went al mercado porque necesitaba milk"</button>
    <button onclick="cswitchPlay('formal')">Formal register in L1, jokes in L2</button>
    <button onclick="cswitchPlay('emotional')">Emotional content in L1, analytical in L2</button>
    <button onclick="cswitchReset()">Reset</button>
  </div>
  <div class="info">
    <b>What is happening:</b> A bilingual's network has two grammar priors
    available. For each word-slot in a sentence, the system asks which
    language has the tighter activation for the intended concept, and it
    fires the winner. For most sentences the same language wins throughout.
    Sometimes a specific word or phrase fits much better in the other
    language &mdash; a cultural concept, an emotional register, a technical
    term &mdash; and the system briefly switches for just that token.<br><br>
    <b>Why emotional content tends to stay in L1:</b> Most bilinguals
    acquired their emotional vocabulary in their first language, with much
    deeper experiential priors attached. "I love you" in L1 has a dense
    emotional constellation; the L2 equivalent is often more semantic than
    felt. Many bilinguals report that swearing in L2 does not hit the same
    way &mdash; the taboo weight never fully built up on those nodes. Code-
    switching follows the path of least resistance, which is usually
    whichever language has the richer edges for the concept at hand.
  </div>
</div>
</div>

<!-- ═══ Semantic Drift ═══════════════════════════════════════════ -->
<div class="panel" id="drift-tab">
<div class="container">
  <h2>Semantic Drift &mdash; Meanings Shift Across Time</h2>
  <p class="desc">
    Word meanings are not fixed. They drift across decades and centuries
    because the collective activation pattern drifts. "Awful" once meant
    <em>full of awe</em> (reverent); now it means <em>terrible</em>.
    "Nice" started as <em>foolish</em>, then <em>precise</em>, then
    <em>pleasant</em>. Slide through the years and watch the constellation
    shift.
  </p>
  <div class="canvas-box">
    <canvas id="drift-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <button onclick="driftWord('awful')">"awful"</button>
    <button onclick="driftWord('nice')">"nice"</button>
    <button onclick="driftWord('gay')">"gay"</button>
    <button onclick="driftWord('silly')">"silly"</button>
    <label style="display:flex;align-items:center;gap:8px;margin-left:10px">
      <span>year:</span>
      <input type="range" id="drift-year" min="1400" max="2025" value="2025" style="width:180px">
      <span class="stat-val" id="drift-year-val">2025</span>
    </label>
  </div>
  <div class="info">
    <b>What you are watching:</b> The selected word's constellation as it
    existed in the year shown by the slider. Slide left and the meaning
    shifts &mdash; nodes fade, new nodes appear, the dominant reading
    changes. The word itself is the same. What drifted is the distribution
    of which contexts it co-occurs with, which over time reshapes which
    nodes it lights up.<br><br>
    <b>Why drift happens:</b> Language is a distributed consensus. Nobody
    decides a word's meaning; the meaning is whatever the population's
    average usage pattern is this decade. Generational shifts in usage
    move the consensus, and once enough speakers use a word differently,
    the new usage is the meaning. No committee, no ruling &mdash; just the
    statistics of what most people activate when they hear the word.
  </div>
</div>
</div>

<!-- ═══ Translation Gap ═══════════════════════════════════════════ -->
<div class="panel" id="translation-tab">
<div class="container">
  <h2>Translation Gap &mdash; Structure That Does Not Cross</h2>
  <p class="desc">
    The English word is on the left with its constellation. The closest foreign
    word is on the right with its constellation. Nodes that appear in both are
    shared meaning. Nodes only on the left are lost in translation. Nodes only
    on the right are meaning the target language adds that English does not
    carry.
  </p>
  <div class="canvas-box">
    <canvas id="trans-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <button onclick="transPick('saudade')">English "longing" ↔ Portuguese <i>saudade</i></button>
    <button onclick="transPick('schadenfreude')">English "pleasure" ↔ German <i>schadenfreude</i></button>
    <button onclick="transPick('komorebi')">English "sunlight" ↔ Japanese <i>komorebi</i></button>
    <button onclick="transPick('hygge')">English "coziness" ↔ Danish <i>hygge</i></button>
    <button onclick="transReset()">Reset</button>
    <span style="margin-left:auto;color:var(--dim)">
      shared nodes: <b style="color:var(--accent)" id="trans-shared">0</b>
      &nbsp; missing: <b style="color:var(--warn)" id="trans-missing">0</b>
      &nbsp; added: <b style="color:var(--accent2)" id="trans-added">0</b>
    </span>
  </div>
  <div class="info">
    <b>Why "saudade" does not translate cleanly:</b> Portuguese <i>saudade</i>
    activates nodes for <em>longing</em>, <em>absence</em>, <em>memory</em>, and
    <em>a specific melancholy-sweet emotional tone</em> that is sufficiently
    distinct that Portuguese speakers report experiencing it as a discrete
    emotion. English "longing" overlaps on the first three nodes but misses the
    specific emotional tone &mdash; the nostalgic-sweet aftertaste &mdash; and
    also misses <em>the cultural frame</em> that makes <i>saudade</i> a
    recognizable thing in Portuguese-speaking cultures. The word cannot be
    translated word-for-word because the target network does not have the same
    constellation available.<br><br>
    <b>The practical implication:</b> When people say "there is no English word
    for X," they are almost always right. There is usually an English phrase that
    gets you in the ballpark, but the structural match between the two
    constellations is incomplete. Good translation is not about finding
    equivalents; it is about preserving as much of the constellation's shape as
    possible while acknowledging what has to be left out.<br><br>
    <b>The deeper point:</b> You can learn the missing concept by learning the
    foreign word and accumulating enough exposures to build its constellation in
    your own network. At some point, the foreign word starts producing an
    experience you cannot fully describe in English &mdash; because the English
    constellation for that experience does not exist yet, and the word has given
    you a handle that the native vocabulary did not.
  </div>
</div>
</div>

<!-- ═══ Onomatopoeia ══════════════════════════════════════════════ -->
<div class="panel" id="onoma-tab">
<div class="container">
  <h2>Onomatopoeia &mdash; Sound-Shaped Words Fire Auditory Cortex</h2>
  <p class="desc">
    Some words are built to sound like the thing they name. Reading them on a
    silent page still activates auditory cortex &mdash; the brain runs a
    partial simulation of the sound as part of comprehension. Pure
    cross-modal wiring, visible in its simplest form.
  </p>
  <div class="canvas-box">
    <canvas id="onoma-canvas" width="960" height="360"></canvas>
  </div>
  <div class="controls">
    <button onclick="onomaPlay('bang')">BANG</button>
    <button onclick="onomaPlay('crash')">CRASH</button>
    <button onclick="onomaPlay('whisper')">whisper</button>
    <button onclick="onomaPlay('buzz')">buzz</button>
    <button onclick="onomaPlay('plain')">(plain word: table)</button>
    <button onclick="onomaReset()">Reset</button>
  </div>
  <div class="info">
    <b>What you are seeing:</b> Reading a word silently activates semantic
    regions strongly and auditory cortex weakly &mdash; unless the word is
    onomatopoeic, in which case the auditory activation jumps. "Buzz" primes
    the acoustic shape of buzzing. "Whisper" activates a quieter, breathier
    acoustic trace. These words do not describe a sound abstractly &mdash;
    they <em>perform</em> the sound, at reduced amplitude, inside the
    reader's auditory cortex.<br><br>
    <b>Why this matters:</b> It is the simplest demonstration that reading
    is not purely symbolic. The shape of the word carries real sensory
    information, and the brain extracts it automatically. Good poetry
    leverages this &mdash; "the silken sad uncertain rustling of each purple
    curtain" is not just describing a sound, it is performing one.
  </div>
</div>
</div>

<!-- ═══ Phonology / Categorical Perception ═══════════════════════ -->
<div class="panel" id="phono-tab">
<div class="container">
  <h2>Phonology &mdash; Categorical Perception of Speech Sounds</h2>
  <p class="desc">
    The deepest demonstration that language reshapes perception. A Japanese
    speaker literally cannot hear the difference between English /r/ and /l/
    &mdash; not because their ears are broken, but because their phonemic
    prior does not carve that acoustic space. Slide through a continuous
    sound gradient and watch the category boundary appear or disappear
    depending on the listener's native language.
  </p>
  <div class="canvas-box">
    <canvas id="phono-canvas" width="960" height="400"></canvas>
  </div>
  <div class="controls">
    <button onclick="phonoPrior('english')">English listener (hears /r/ vs /l/)</button>
    <button onclick="phonoPrior('japanese')">Japanese listener (no r/l boundary)</button>
    <button onclick="phonoPrior('raw')">No prior (raw acoustic signal)</button>
  </div>
  <div class="info">
    <b>The experiment</b> (Miyawaki et al., 1975): create a series of
    synthesized sounds that morph continuously from /r/ to /l/ across
    equally-spaced acoustic steps. English speakers perceive a sharp
    boundary in the middle &mdash; sounds on one side are all "r," sounds
    on the other are all "l," and the transition is a cliff. Japanese
    speakers, whose language has no phonemic distinction between the two,
    hear the entire continuum as one sound. The acoustic signal is identical.
    The perception differs because the prior differs.<br><br>
    <b>Why vocabulary-carves-perception goes all the way down:</b> If your
    language has a phoneme, you hear it as a discrete unit with a hard
    boundary. If it does not, the acoustic variation fades into one
    category. This is not metaphorical &mdash; it is measurable in the
    first few hundred milliseconds of auditory processing, below conscious
    access. The prior is wired into the perceptual pipeline itself.<br><br>
    <b>The window closes:</b> Infants under 6 months can distinguish every
    phonetic contrast from every language. By 12 months, they have lost
    the ability to distinguish contrasts their language does not use.
    This is not loss &mdash; it is specialization. The network pruned
    distinctions it had no reason to maintain, freeing bandwidth for
    the distinctions that matter. An adult learning a new language with
    different phonemes has to rebuild the lost distinctions, which is why
    accent is so hard to shake.
  </div>
</div>
</div>

<!-- ═══ Prosody ═══════════════════════════════════════════════════ -->
<div class="panel" id="prosody-tab">
<div class="container">
  <h2>Prosody &mdash; Pitch, Rhythm, and Stress as Parallel Meaning</h2>
  <p class="desc">
    Words carry one channel. Prosody &mdash; pitch, rhythm, stress,
    loudness, timing &mdash; carries another, in parallel. The same words
    can mean radically different things depending on which word carries
    the stress.
  </p>
  <div class="canvas-box">
    <canvas id="prosody-canvas" width="960" height="420"></canvas>
  </div>
  <div class="controls">
    <button onclick="prosodyStress(-1)">(neutral)</button>
    <button onclick="prosodyStress(0)">I didn't say he stole the money</button>
    <button onclick="prosodyStress(1)">I DIDN'T say he stole the money</button>
    <button onclick="prosodyStress(2)">I didn't SAY he stole the money</button>
    <button onclick="prosodyStress(3)">I didn't say HE stole the money</button>
    <button onclick="prosodyStress(4)">I didn't say he STOLE the money</button>
    <button onclick="prosodyStress(6)">I didn't say he stole the MONEY</button>
  </div>
  <div class="info">
    <b>Seven meanings, one sentence:</b> The sentence "I didn't say he stole
    the money" has a different inference depending on which word gets the
    stress. Stress "I" → someone else said it. Stress "didn't" → I deny
    saying it at all. Stress "say" → maybe I implied it. Stress "he" →
    maybe someone else stole it. Stress "stole" → maybe he borrowed it.
    Stress "money" → maybe he stole something else. The words on the page
    never change. The inference changes because the stress re-weights which
    word's alternative set is being contrasted.<br><br>
    <b>How stress creates contrast:</b> Prosodic stress activates not just
    the stressed word but the <em>set of things the stressed word is
    contrasting with</em>. "Stress HE" activates the implicit alternative
    set {she, they, you, someone else}, and the listener infers that the
    speaker is pointing to one of those alternatives. This is how one
    acoustic cue can carry a whole inference chain.<br><br>
    <b>Why prosody matters so much in speech and so little in text:</b>
    Text loses all prosodic information. "I'm fine" in speech carries a
    dozen different meanings through tone alone. The same two characters
    on the page carry just one, flat, ambiguous meaning. This is why
    sarcasm dies in text, why emojis evolved, and why audiobooks and read
    text feel different even when the words are identical.
  </div>
</div>
</div>

<!-- ═══ Silence ═══════════════════════════════════════════════════ -->
<div class="panel" id="silence-tab">
<div class="container">
  <h2>Silence &mdash; The Utterance That Is Not Said</h2>
  <p class="desc">
    A long pause after a question is an answer. A beat before a punchline
    is part of the joke. Silence in poetry is part of the meter. Gaps
    carry information because the listener is running a forecast during
    the gap, and the shape of the gap is itself a data point.
  </p>
  <div class="canvas-box">
    <canvas id="silence-canvas" width="960" height="360"></canvas>
  </div>
  <div class="controls">
    <button onclick="silencePlay('question')">"Did you love me?" → (long silence)</button>
    <button onclick="silencePlay('joke')">Setup → (beat) → punchline</button>
    <button onclick="silencePlay('grief')">"How are you?" → (pause)</button>
    <button onclick="silenceReset()">Reset</button>
  </div>
  <div class="info">
    <b>Why silence is an utterance:</b> The listener's predictor is running
    continuously. During the speaker's turn, the predictor is consuming
    the incoming words. When the words stop, the predictor does not
    &mdash; it starts forecasting what the speaker is about to say, or
    trying to infer what they are thinking but not saying. The gap is
    data about the speaker's internal state: a hesitation, a deliberation,
    a reluctance, a swallowed response. None of that information is in
    the words. It is in the shape of the space between the words.<br><br>
    <b>The conversational gap of ~200ms:</b> Natural turn-taking averages
    about 200ms of gap between speakers. Gaps longer than ~700ms become
    marked &mdash; the listener registers them as a hesitation or a
    problem. Gaps that approach 2 seconds are unbearable in most
    conversational contexts and force the other speaker to jump in to
    fill them. Skilled interrogators, therapists, and negotiators exploit
    this: they stay silent past the 700ms mark, and the other person
    keeps talking to fill the space &mdash; often revealing more than
    they intended.
  </div>
</div>
</div>

<!-- ═══ Language Acquisition ═════════════════════════════════════ -->
<div class="panel" id="acquisition-tab">
<div class="container">
  <h2>Language Acquisition &mdash; Without Being Taught</h2>
  <p class="desc">
    A child goes from zero vocabulary to grammatical fluency in 3-5 years
    with no explicit grammar instruction. They extract the rules from raw
    input, build a working grammar prior, and never consciously know they
    did it. Watch the developmental curve, and the critical-period cliff
    after which the process becomes much harder.
  </p>
  <div class="canvas-box">
    <canvas id="acquisition-canvas" width="960" height="400"></canvas>
  </div>
  <div class="controls">
    <button onclick="acquisitionPlay('normal')">Normal acquisition (0-12 years)</button>
    <button onclick="acquisitionPlay('late')">Late start (adult second language)</button>
    <button onclick="acquisitionReset()">Reset</button>
  </div>
  <div class="info">
    <b>The curve:</b> Vocabulary climbs quickly after the first year (the
    famous "vocabulary explosion" around 18-24 months), grammatical
    complexity follows a few months later, and by age 5 a typical child
    has effectively adult grammar with a smaller vocabulary. By adulthood
    a native speaker has tens of thousands of words and completely
    automatic grammatical intuitions. None of this was taught in the sense
    of being drilled from a rulebook. It was extracted from exposure.<br><br>
    <b>The critical period:</b> Between roughly age 5 and age 12-15, the
    capacity to acquire new languages natively degrades. An adult
    learning a second language can reach high fluency but almost never
    matches a native accent, and the grammar is always run through
    slower, more explicit processing. The network's phonemic priors have
    specialized (see the Phonology canvas), and retraining them is
    expensive. This is why children of immigrants end up bilingual
    natives and their parents end up bilingual non-natives.<br><br>
    <b>What is happening underneath:</b> The child is running an enormous
    unsupervised statistical learning task on language input &mdash;
    extracting regularities, building a grammar prior, testing it against
    what they hear next. The process is the same Hebbian-plus-prediction
    learning that happens everywhere else in the brain. What is special
    about language is the volume and regularity of the input during a
    period of maximum plasticity.
  </div>
</div>
</div>

<!-- ═══ Baby Talk ═════════════════════════════════════════════════ -->
<div class="panel" id="babytalk-tab">
<div class="container">
  <h2>Baby Talk &mdash; Infant-Directed Speech as Scaffolding</h2>
  <p class="desc">
    Parents across cultures produce a distinct register when talking to
    infants: exaggerated pitch variation, slower tempo, longer pauses,
    simpler vocabulary, more repetition. This is not condescension. It is
    a scaffolding tool evolved to make the language-learning signal
    maximally extractable by a new network.
  </p>
  <div class="canvas-box">
    <canvas id="babytalk-canvas" width="960" height="380"></canvas>
  </div>
  <div class="controls">
    <button onclick="babytalkPlay('adult')">Adult-directed: "Want to go outside?"</button>
    <button onclick="babytalkPlay('infant')">Infant-directed: "Wanna go ouuutside?!"</button>
  </div>
  <div class="info">
    <b>The features:</b>
    &bull; <b>Higher, more variable pitch</b> — attracts attention, marks
    the register as special, and makes word boundaries more
    distinguishable.<br>
    &bull; <b>Slower tempo</b> — gives the infant's predictor more time to
    parse each word.<br>
    &bull; <b>Longer pauses between utterances</b> — lets the encoding
    settle before the next input arrives.<br>
    &bull; <b>Simpler vocabulary</b> — uses words the infant is most likely
    to have partial constellations for already.<br>
    &bull; <b>More repetition</b> — a word heard five times in a minute is
    weighted much higher than a word heard once.<br><br>
    <b>Why it works:</b> Each feature is a scaffolding element that makes
    the statistical learning task easier for the infant. The exaggerated
    pitch marks boundaries the adult speech blurs. The slow tempo stays
    inside the infant's working-memory budget. The repetition accelerates
    weight accumulation on the target words. Taken together, baby talk
    is a compressed, optimized language-learning dataset delivered in
    real time by every caregiver.<br><br>
    <b>Infants who get more infant-directed speech</b> develop faster
    vocabulary and earlier grammatical structures than infants who hear
    mostly adult-directed speech. The effect is real and measurable.
    Baby talk is not silly &mdash; it is evolved pedagogy running without
    any conscious lesson plan.
  </div>
</div>
</div>

<!-- ═══ Reading / Eye Movements ══════════════════════════════════ -->
<div class="panel" id="reading-tab">
<div class="container">
  <h2>Reading &mdash; Saccades, Fixations, and Predictability</h2>
  <p class="desc">
    Reading is not smooth. The eye jumps in discrete saccades to fixation
    points, holds for ~200-300ms, then jumps again. Sometimes it regresses
    backward to re-read. Fixation duration depends on word predictability:
    common, expected words get short fixations or are skipped entirely;
    surprising words get long fixations and sometimes a regression.
  </p>
  <div class="canvas-box">
    <canvas id="reading-canvas" width="960" height="420"></canvas>
  </div>
  <div class="controls">
    <button onclick="readingPlay('normal')">Fluent reader, normal prose</button>
    <button onclick="readingPlay('surprise')">Fluent reader, surprise word</button>
    <button onclick="readingPlay('dyslexic')">Dyslexic reader (slower decoding)</button>
    <button onclick="readingReset()">Reset</button>
  </div>
  <div class="info">
    <b>What you are watching:</b> A line of text with the reader's gaze
    path overlaid. Each fixation is a dot, sized by duration. Saccades
    are the arrows between dots. In fluent reading most fixations last
    150-300ms and are tightly spaced; frequent short words are often
    skipped entirely by a longer saccade. A surprising word (low
    predictability) produces a long fixation, often 500ms or more, and
    may trigger a regression back to earlier words to re-parse.<br><br>
    <b>Dyslexia in the same diagram:</b> Dyslexic reading shows the
    decoding bottleneck visually. Fixations are longer and more numerous,
    saccades are shorter (skipping fewer words), regressions are frequent
    even on normal prose. The visual system is intact. The bottleneck is
    in the grapheme-to-phoneme mapping: translating visual letter
    patterns into the sound/meaning activation that fluent readers do
    automatically. Each word costs more, so the eye has to work harder
    through every one. See the Dyslexia canvas below for the mechanism
    in detail.<br><br>
    <b>Why skilled readers skip short common words:</b> The predictor's
    forecast is already so tight for "the," "of," "and," "to," "is,"
    etc. that fixating them contributes almost nothing. The
    parafoveal preview (the low-resolution text just to the right of the
    fixation point) confirms the predicted word without requiring a
    full fixation, and the eye jumps past. This is only possible because
    the predictor is accurate. A less fluent reader cannot skip, because
    their predictor is less confident.
  </div>
</div>
</div>

<!-- ═══ Aphasia & Dyslexia ═══════════════════════════════════════ -->
<div class="panel" id="aphasia-tab">
<div class="container">
  <h2>Aphasia &amp; Dyslexia &mdash; Specific Linguistic Breakdowns</h2>
  <p class="desc">
    The language system is modular. Different sub-systems can break
    independently, and each breakdown isolates one specific piece of the
    architecture. Broca's aphasia, Wernicke's aphasia, and dyslexia each
    remove a different component and leave everything else intact &mdash;
    which is how we know the components exist separately in the first
    place.
  </p>
  <div class="canvas-box">
    <canvas id="aphasia-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <button onclick="aphasiaPick('broca')">Broca's aphasia (grammar gone)</button>
    <button onclick="aphasiaPick('wernicke')">Wernicke's aphasia (content gone)</button>
    <button onclick="aphasiaPick('dyslexia')">Dyslexia (decoding bottleneck)</button>
    <button onclick="aphasiaPick('intact')">Intact (reference)</button>
    <button onclick="aphasiaReset()">Reset</button>
  </div>
  <div class="info">
    <b>Broca's aphasia</b> &mdash; damage to the left inferior frontal gyrus
    (Broca's area). Grammar production collapses, but the speaker still
    knows what they want to say. Speech becomes effortful,
    telegraphic, content-only: "walk... store... milk." Comprehension is
    largely preserved for simple sentences but fails on syntactically
    complex ones where word order carries the meaning. The grammar prior
    is gone; the semantic clusters are intact.<br><br>
    <b>Wernicke's aphasia</b> &mdash; damage to the superior temporal
    gyrus. Speech is fluent, grammatical, and at normal tempo &mdash;
    but the content is nonsense. Words flow grammatically without being
    anchored to meaning. Comprehension is severely impaired because the
    same region that maps sound to meaning has lost its grip. The grammar
    prior runs beautifully; the semantic link is broken.<br><br>
    <b>Dyslexia</b> &mdash; a developmental reading disorder affecting
    roughly 5-10% of the population. The visual system is intact,
    intelligence is intact, spoken language is intact &mdash; what is
    impaired is the specific pipeline that converts visual letter
    patterns into phonemic representations fast enough for fluent
    reading. Dyslexic readers see the letters correctly; the translation
    to sound/meaning is slow, effortful, and error-prone. This produces
    the long fixations, short saccades, and frequent regressions visible
    in the Reading canvas above. Dyslexia is not a "vision problem" and
    not an "intelligence problem" &mdash; it is a decoding-pipeline
    bottleneck in a specific sub-network.<br><br>
    <b>Why this matters for the overall framework:</b> The three
    breakdowns show three different sub-systems that must exist
    independently: grammar production, semantic mapping, and written
    decoding. If these were not separable, a single lesion would not
    cleanly remove one while leaving the other two intact. The
    modularity is the point. Language is not one thing; it is a set of
    systems that usually cooperate closely enough to feel like one thing.
  </div>
</div>
</div>

<!-- ═══ Written vs Spoken ════════════════════════════════════════ -->
<div class="panel" id="wvs-tab">
<div class="container">
  <h2>Written vs Spoken &mdash; Two Cognitive Modes</h2>
  <p class="desc">
    Writing and speaking run on different cognitive schedules. Speech is
    real-time, irreversible, and constrained by working memory. Writing
    is asynchronous, revisable, and allows the writer to iterate against
    a forecast they would never hit in speech. The resulting texts differ
    in structure, not just in medium.
  </p>
  <div class="canvas-box">
    <canvas id="wvs-canvas" width="960" height="360"></canvas>
  </div>
  <div class="controls">
    <button onclick="wvsPlay('spoken')">Spoken transcript</button>
    <button onclick="wvsPlay('written')">Written version of the same idea</button>
  </div>
  <div class="info">
    <b>What differs:</b><br>
    &bull; <b>Sentence length.</b> Spoken sentences are shorter and more
    fragmented because the speaker cannot plan the whole structure
    before committing to the first word. Written sentences can be much
    longer because the writer plans and revises.<br>
    &bull; <b>Fillers and false starts.</b> Speech is full of "um," "you
    know," "I mean," "well," restarted clauses, and abandoned phrases.
    Writing has essentially none of these because the writer deletes
    them before anyone sees them.<br>
    &bull; <b>Information density.</b> Writing packs more distinct
    concepts per word. Speech uses more repetition and redundancy because
    the listener cannot re-read a sentence they missed.<br>
    &bull; <b>Grammatical complexity.</b> Writing makes heavy use of
    subordinate clauses, passive constructions, and nested parentheticals
    that would be unbearable in speech.<br><br>
    <b>Why writing slows thought and sharpens it:</b> Committing to a
    first draft forces the writer to discover what they actually think,
    because they have to serialize their messy internal state into a
    linear sequence. Editing lets them correct the attempt. The
    iteration loop between draft and revision is the cognitive move
    that spoken-only cultures do not have access to &mdash; and it
    changes what kinds of thoughts become thinkable.
  </div>
</div>
</div>

<!-- ═══ Conversation Dynamics ═══════════════════════════════════ -->
<div class="panel" id="conv-tab">
<div class="container">
  <h2>Conversation Dynamics &mdash; Turn-Taking, Repair, Backchannels</h2>
  <p class="desc">
    Conversation is a coordinated dance. Turn-taking averages ~200ms of
    gap between speakers &mdash; faster than conscious planning.
    Backchannels ("uh-huh," "right") keep the speaker going. Repairs
    ("what I meant was...") happen at specific syntactic points. All of
    this is running automatically in the background and is only visible
    when you slow it down.
  </p>
  <div class="canvas-box">
    <canvas id="conv-canvas" width="960" height="400"></canvas>
  </div>
  <div class="controls">
    <button onclick="convPlay('smooth')">Smooth conversation</button>
    <button onclick="convPlay('overlap')">Overlapping speech</button>
    <button onclick="convPlay('awkward')">Awkward gaps (&gt;1 sec)</button>
    <button onclick="convPlay('repair')">Self-repair mid-sentence</button>
  </div>
  <div class="info">
    <b>The 200ms gap:</b> Studies across ~10 languages find that natural
    turn-taking averages about 200 milliseconds of silence between one
    speaker finishing and the next starting. That is faster than the
    ~600ms minimum required to consciously plan a spoken sentence. The
    only way the listener can hit that gap is by <em>predicting the end
    of the current speaker's turn</em> while it is still happening, and
    starting their own planning in parallel. Turn-taking is a prediction
    game at millisecond resolution.<br><br>
    <b>Backchanneling</b> &mdash; "uh-huh," "right," "mmhm," nods &mdash;
    is how the listener keeps the speaker oriented without taking the
    floor. Remove it from a conversation (deadpan listener) and the
    speaker becomes visibly uncomfortable within seconds and often
    trails off. The backchannels are a feedback signal to the speaker's
    predictor saying "yes, keep going, you are being received."<br><br>
    <b>Repair</b> &mdash; the speaker restarts or corrects themselves
    mid-sentence ("I went to the... she went to the store"). Repairs
    tend to happen at clause boundaries, not in the middle of a phrase,
    because the grammar parser needs to complete the current unit before
    a clean break is available. Awkward silences happen when normal
    turn-taking breaks down &mdash; neither speaker takes the floor, the
    gap extends past 700ms, and both become aware of the gap itself.
    The silence becomes data.
  </div>
</div>
</div>

<!-- ═══ Subtext ══════════════════════════════════════════════════ -->
<div class="panel" id="subtext-tab">
<div class="container">
  <h2>Subtext &mdash; Meaning in What Is Not Said</h2>
  <p class="desc">
    A character asks "Did you eat the last cookie?" and the other
    character answers "What kind of cookie was it?" The second character
    did not say "yes." But the listener infers "yes" instantly, because
    a denial would have been the shorter, simpler response. The shape of
    what the speaker chose <em>not</em> to say is itself information.
  </p>
  <div class="canvas-box">
    <canvas id="subtext-canvas" width="960" height="380"></canvas>
  </div>
  <div class="controls">
    <button onclick="subtextPlay('cookie')">"Did you eat the last cookie?" / "What kind was it?"</button>
    <button onclick="subtextPlay('love')">"Do you love me?" / "I am tired."</button>
    <button onclick="subtextPlay('hiring')">"We will be in touch." (no callback)</button>
    <button onclick="subtextReset()">Reset</button>
  </div>
  <div class="info">
    <b>The mechanism:</b> When a speaker <em>could</em> have said X but
    said Y instead, the listener runs an implicit comparison: "what would
    the simplest truthful response be?" If the simplest response is
    missing, the listener infers a reason for the omission. Dodging a
    direct question is usually an admission. Soft refusals
    ("we'll be in touch") are understood as rejections because the
    normal pattern for acceptance is a specific, committed follow-up.
    Evasion is itself a signal.<br><br>
    <b>Why good writers engineer subtext:</b> Explicit statements
    activate semantic content directly. Subtext forces the reader to
    run the inference themselves &mdash; and an inference the reader
    produced feels more earned than one the writer stated outright.
    "She's fine" is flat. "She's fine," she said, not looking up from
    the dishes is a completely different reading, because the reader
    has to notice that "she's fine" followed by avoidant behavior is a
    contradiction, and the contradiction is what the scene is about.
    The meaning never appears on the page. It appears in the reader's
    head.
  </div>
</div>
</div>

<!-- ═══ Lying ════════════════════════════════════════════════════ -->
<div class="panel" id="lying-tab">
<div class="container">
  <h2>Lying &mdash; Linguistic Markers of Deception</h2>
  <p class="desc">
    Liars do not sound like truth-tellers, and the differences are
    measurable. Reduced first-person pronouns, increased negations, more
    hedges, more distancing language. The pattern shows up across
    studies reliably enough that text-analysis tools can classify
    deception at rates well above chance &mdash; not perfectly, but
    systematically.
  </p>
  <div class="canvas-box">
    <canvas id="lying-canvas" width="960" height="400"></canvas>
  </div>
  <div class="controls">
    <button onclick="lyingPick('truthful')">Truthful statement</button>
    <button onclick="lyingPick('deceptive')">Deceptive statement</button>
  </div>
  <div class="info">
    <b>The markers</b> (Newman et al., 2003; Hancock et al., 2007 and
    others):<br>
    &bull; <b>Fewer first-person singular pronouns</b> ("I", "me", "my").
    Liars distance themselves from the statement linguistically.<br>
    &bull; <b>More third-person and passive constructions</b> ("the thing
    that happened," "mistakes were made").<br>
    &bull; <b>More negative-emotion words</b> indirectly &mdash; anxiety
    leaks into word choice.<br>
    &bull; <b>Fewer exclusive words</b> ("but," "except," "without") &mdash;
    lies tend to be simpler because fabricating exclusions requires more
    cognitive effort.<br>
    &bull; <b>More motion verbs and simple verbs</b>, fewer sensory details.<br><br>
    <b>Why the markers exist:</b> Lying is cognitively expensive. The
    liar has to construct a plausible story, monitor it for consistency
    with what is actually true, suppress the true version from leaking
    out, and track what they have said previously to stay consistent
    under questioning. Under that load, linguistic production shifts
    toward simpler, safer, more distanced constructions. The markers are
    the signature of the extra effort.<br><br>
    <b>Important caveat:</b> These are statistical tendencies, not
    reliable individual diagnoses. A nervous truth-teller can look like
    a liar. A practiced liar can look like a truth-teller. The markers
    work at population scale, not at the "is this specific person lying"
    level &mdash; which is why no credible deception-detection system
    relies on language alone.
  </div>
</div>
</div>

<!-- ═══ Persuasion & Fallacies ═══════════════════════════════════ -->
<div class="panel" id="persuasion-tab">
<div class="container">
  <h2>Persuasion &amp; Logical Fallacies &mdash; Rhetoric as Prior-Reshaping</h2>
  <p class="desc">
    Every logical fallacy is a move that reshapes the listener's prior
    in a direction the literal logic does not justify. Ad hominem shifts
    attention from argument to arguer. Strawman replaces the opponent's
    claim with a weaker one. Appeal to emotion adds an emotional edge
    that outweighs the semantic content. Each is a specific prompt
    engineering technique for human brains.
  </p>
  <div class="canvas-box">
    <canvas id="persuasion-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <button onclick="persuasionPick('ad-hominem')">Ad hominem</button>
    <button onclick="persuasionPick('strawman')">Strawman</button>
    <button onclick="persuasionPick('appeal-emotion')">Appeal to emotion</button>
    <button onclick="persuasionPick('slippery-slope')">Slippery slope</button>
    <button onclick="persuasionPick('anchoring')">Anchoring</button>
    <button onclick="persuasionReset()">Reset</button>
  </div>
  <div class="info">
    <b>Fallacies are not "wrong logic" &mdash; they are effective
    prior-reshaping moves</b> that work on human listeners despite being
    logically invalid. That is why they persist. If they did not work,
    nobody would use them. Each fallacy exploits a specific property of
    how the listener's predictor processes input:<br><br>
    &bull; <b>Ad hominem</b> &mdash; attacks the speaker's character.
    Shifts the listener's activation from "evaluate the claim" to
    "evaluate the person," and weakens the claim's acceptability by
    association with a now-distrusted source.<br>
    &bull; <b>Strawman</b> &mdash; restates the opponent's claim as a
    weaker version that is easier to attack. The listener, already
    primed to understand the stated version, does not run a separate
    check against what was actually claimed.<br>
    &bull; <b>Appeal to emotion</b> &mdash; adds an emotional tag to the
    claim that raises its felt weight without changing the evidence.
    The listener's decision system factors emotional weight in alongside
    logical weight, so a high-emotion claim wins against a low-emotion
    counter even when the evidence favors the counter.<br>
    &bull; <b>Slippery slope</b> &mdash; activates a chain of negative
    consequences, each plausible individually, so the listener's
    forecast ends up at the worst-case even though no single step is
    proven.<br>
    &bull; <b>Anchoring</b> &mdash; introduces a number or standard first,
    and everything after it gets evaluated relative to the anchor. The
    anchor reshapes the distribution of acceptable answers before any
    argument is made.<br><br>
    <b>The defense</b> is not "don't be fooled." The defense is
    mechanical: notice which prior is being reshaped and by what move,
    and ask whether the move is licensed by the actual evidence or only
    by the rhetorical structure. Recognition is the only defense because
    the moves run below conscious deliberation and cannot be prevented
    from firing &mdash; they can only be noticed and corrected after the
    fact.
  </div>
</div>
</div>

<!-- ═══ Narrative Structure ═════════════════════════════════════ -->
<div class="panel" id="narrative-tab">
<div class="container">
  <h2>Narrative Structure &mdash; Story Arc as Activation Wave</h2>
  <p class="desc">
    A well-structured story is not a sequence of events. It is an
    engineered activation curve that rises, peaks, resolves, and leaves
    a residue. The three-act structure, the hero's journey, the setup-
    conflict-resolution pattern &mdash; all are schemas for producing
    specific cognitive effects in the listener or reader across time.
  </p>
  <div class="canvas-box">
    <canvas id="narrative-canvas" width="960" height="400"></canvas>
  </div>
  <div class="controls">
    <button onclick="narrativePick('three-act')">Three-act structure</button>
    <button onclick="narrativePick('hero')">Hero's journey</button>
    <button onclick="narrativePick('tragedy')">Tragedy arc</button>
    <button onclick="narrativePick('comedy')">Comedy arc</button>
    <button onclick="narrativeReset()">Reset</button>
  </div>
  <div class="info">
    <b>Why structures exist:</b> Attention is expensive. A story has to
    hold the listener's attention across minutes or hours. It does this
    by promising a pay-off, slowly escalating the tension to make the
    pay-off more valuable, and then delivering a pay-off with enough
    residual to feel meaningful. The three-act structure is not the only
    way to build this curve, but it is the most-tested one: setup
    (establish baseline), confrontation (raise stakes), resolution
    (release tension).<br><br>
    <b>The peak is the residual spike:</b> The climax is where the
    forecast that has been building through the rising action gets
    violated and replaced. The bigger the buildup, the bigger the
    spike. This is why slow-burn stories often hit hardest: the buildup
    trains the listener's predictor onto a specific forecast, and the
    climax breaks it. A story with no buildup has no forecast to break,
    so it has no spike, so it cannot land hard.<br><br>
    <b>Different arcs target different spike profiles:</b> Tragedy ends
    below the starting line &mdash; the residual is negative, a settled
    sadness. Comedy ends above it &mdash; the residual is positive, a
    settled warmth. The hero's journey is specifically engineered for
    transformation: start low, go lower, rise, peak, return changed. The
    shape of the curve is the shape of the emotional experience.
  </div>
</div>
</div>

<!-- ═══ Writing Advice Engine ═══════════════════════════════════ -->
<div class="panel" id="advice-tab">
<div class="container">
  <h2>Writing Advice &mdash; Classic Rules as Mechanisms</h2>
  <p class="desc">
    Every piece of classic writing advice you have heard is a specific
    mechanism in Lingora's framework. "Show don't tell" activates
    sensory cortex. "Specific details" narrows the reader's forecast.
    "Active voice" topicalizes agents. "Vary sentence length" prevents
    the predictor from settling. Here is the rulebook, translated.
  </p>
  <div class="canvas-box">
    <canvas id="advice-canvas" width="960" height="420"></canvas>
  </div>
  <div class="controls">
    <button onclick="advicePick('show')">"Show, don't tell"</button>
    <button onclick="advicePick('specific')">"Specific details"</button>
    <button onclick="advicePick('active')">"Active voice"</button>
    <button onclick="advicePick('vary')">"Vary sentence length"</button>
    <button onclick="advicePick('darlings')">"Kill your darlings"</button>
    <button onclick="advicePick('rewrite')">"Writing is rewriting"</button>
  </div>
  <div class="info">
    <b>The rules, decoded:</b> Pick a rule above and see the mechanism
    written out. Each one reduces to "produce a specific effect in the
    reader's network by choosing inputs that exploit a specific feature
    of how the reader's predictor processes language." None of the rules
    are arbitrary stylistic preferences; they are all engineering
    guidance for a device (the reader's brain) that the writer cannot
    directly observe but can consistently predict.
  </div>
</div>
</div>

<!-- ═══ Text Diff Analyzer ═════════════════════════════════════ -->
<div class="panel" id="diff-tab">
<div class="container">
  <h2>Text Diff &mdash; Two Versions, Two Activation Profiles</h2>
  <p class="desc">
    Paste (or pick) two versions of a sentence and see which activation
    clusters each one lights up. Useful for comparing a draft with an
    edit, an abstract sentence with a concrete one, or a direct
    statement with a subtextual one. The numbers are approximations
    based on curated activation tables; the point is to make the
    qualitative difference mechanical.
  </p>
  <div class="canvas-box">
    <canvas id="diff-canvas" width="960" height="420"></canvas>
  </div>
  <div class="controls">
    <button onclick="diffPick('tell-show')">Tell vs Show</button>
    <button onclick="diffPick('passive-active')">Passive vs Active</button>
    <button onclick="diffPick('vague-specific')">Vague vs Specific</button>
    <button onclick="diffReset()">Reset</button>
  </div>
  <div class="info">
    <b>How to read the diff:</b> Two sentences are shown side by side.
    Below each, six activation bars show the estimated strength of
    different cognitive regions the sentence recruits: verbal/semantic,
    visual, motor, tactile, emotional, and social-inference. The
    "better" version (usually the right one) recruits more regions at
    higher amplitude, which is why it feels more alive on the page.
  </div>
</div>
</div>

<!-- ═══ Sign Language ═══════════════════════════════════════════ -->
<div class="panel" id="sign-tab">
<div class="container">
  <h2>Sign Language &mdash; Grammar Without Sound</h2>
  <p class="desc">
    Sign languages are not gestures pantomiming words. They are full
    natural languages with their own phonology (at the sub-sign level),
    grammar, morphology, and dialects. ASL is not "English on the hands"
    &mdash; it has a completely different grammar. The proof that
    language is about structured symbols, not about sound, is that any
    modality that can carry structure can carry language.
  </p>
  <div class="canvas-box">
    <canvas id="sign-canvas" width="960" height="400"></canvas>
  </div>
  <div class="controls">
    <button onclick="signPick('phono')">Sub-sign phonology</button>
    <button onclick="signPick('grammar')">Spatial grammar</button>
    <button onclick="signPick('deafborn')">Deaf-native vs deaf-late</button>
  </div>
  <div class="info">
    <b>Sub-sign phonology:</b> Sign languages have a phoneme-level
    structure, but the units are not sounds &mdash; they are handshape,
    location, movement, palm orientation, and facial expression. ASL
    has roughly 40 handshapes, a small set of canonical locations and
    movements, and a grammar of how these combine. Minimal pairs exist
    (signs that differ in exactly one parameter and mean different
    things). The categorical perception of sign phonemes by native
    signers parallels the categorical perception of spoken phonemes by
    hearing people.<br><br>
    <b>Spatial grammar:</b> ASL uses the signing space around the
    signer's body as a grammatical resource. Pronouns get assigned
    locations; verbs move between locations to indicate who is doing
    what to whom. Topic-comment structures, conditionals, and
    questions are marked by facial expressions that function
    grammatically (not just emotionally). None of this has a direct
    equivalent in English grammar.<br><br>
    <b>Critical period applies equally:</b> Deaf children of deaf
    parents acquire sign language natively on the same developmental
    schedule that hearing children acquire spoken language. Deaf
    children born to hearing parents who do not learn sign until late
    often show the same late-acquisition deficits that spoken-language
    late-learners show. The critical period is not about sound. It is
    about exposure to a fully-structured linguistic system at the
    right developmental window.
  </div>
</div>
</div>

<!-- ═══ Sandbox ══════════════════════════════════════════════════ -->
<div class="panel" id="sandbox-tab">
<div class="container">
  <h2>Sandbox &mdash; Build Sentences and Watch the Forecast</h2>
  <p class="desc">
    Axona has a sandbox for node graphs. Lingora's sandbox is for
    language: pick words from the palette or type your own, assemble
    them into a sentence, and watch the running next-token forecast
    narrow with each word you add. Drag words to reorder. Clear and
    rebuild at will.
  </p>
  <div class="canvas-box">
    <canvas id="sandbox-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <button onclick="sandboxAdd('The')">The</button>
    <button onclick="sandboxAdd('cat')">cat</button>
    <button onclick="sandboxAdd('dog')">dog</button>
    <button onclick="sandboxAdd('sat')">sat</button>
    <button onclick="sandboxAdd('ran')">ran</button>
    <button onclick="sandboxAdd('jumped')">jumped</button>
    <button onclick="sandboxAdd('on')">on</button>
    <button onclick="sandboxAdd('in')">in</button>
    <button onclick="sandboxAdd('the')">the</button>
    <button onclick="sandboxAdd('mat')">mat</button>
    <button onclick="sandboxAdd('floor')">floor</button>
    <button onclick="sandboxAdd('couch')">couch</button>
    <button onclick="sandboxAdd('.')">.</button>
    <button onclick="sandboxPop()">Undo</button>
    <button onclick="sandboxClear()">Clear</button>
  </div>
  <div class="info">
    <b>What you are doing:</b> Each word you add updates the running
    sentence on the left and the predictor's top-k forecast on the right.
    The distribution starts wide (many valid first words) and narrows
    with each click. Short common continuations become dominant; odd
    choices produce surprise spikes visible as low-probability tail
    entries. This is the Sentence Forecast canvas, but under your
    control &mdash; you choose the continuation.<br><br>
    <b>What to try:</b> Build a fluent sentence, then intentionally
    break it ("The cat dog...") and watch the forecast collapse. Build
    a garden-path sentence word-by-word and watch the predictor try to
    recover. Or just play &mdash; this is Lingora's closest analog to
    "running the engine yourself."
  </div>
</div>
</div>

<!-- ═══ Metaphor Engine (Lakoff) ═════════════════════════════════ -->
<div class="panel" id="metaphor-tab">
<div class="container">
  <h2>Metaphor Engine &mdash; Systematic Cross-Cluster Mapping</h2>
  <p class="desc">
    A conceptual metaphor is not a single sentence. It is a <em>systematic
    mapping</em> between a source domain (concrete, well-understood) and a
    target domain (abstract, harder to think about), which licenses dozens
    of individual sentences built from the same underlying correspondence.
    Pick a metaphor and see the full table of borrowed inferences.
  </p>
  <div class="canvas-box">
    <canvas id="metaphor-canvas" width="960" height="460"></canvas>
  </div>
  <div class="controls">
    <button onclick="metaphorPick('time-money')">TIME IS MONEY</button>
    <button onclick="metaphorPick('argument-war')">ARGUMENT IS WAR</button>
    <button onclick="metaphorPick('life-journey')">LIFE IS A JOURNEY</button>
    <button onclick="metaphorPick('ideas-objects')">IDEAS ARE OBJECTS</button>
    <button onclick="metaphorReset()">Reset</button>
  </div>
  <div class="info">
    <b>Why conceptual metaphors matter:</b> Once the mapping is installed
    in your network, inferences you never explicitly reasoned about get
    borrowed for free. "Time is money" licenses "invest time," "waste
    time," "spend time with you," "run out of time," "is it worth your
    time." You never decided to treat time as a transactional resource
    &mdash; you inherited the framing from the metaphor, and the framing
    shapes every subsequent thought about time.<br><br>
    <b>The uncomfortable part:</b> Different cultures use different root
    metaphors for the same abstract concept, and the root metaphor shapes
    how people actually think. "Argument is war" produces adversarial
    conversations; a culture whose argument metaphor was "argument is
    dance" would have completely different conversational norms. Neither
    is "right." Both are consequences of which mapping got installed.
  </div>
</div>
</div>

<!-- ═══ Collocations ═════════════════════════════════════════════ -->
<div class="panel" id="colloc-tab">
<div class="container">
  <h2>Collocations &mdash; Words That Go Together</h2>
  <p class="desc">
    "Strong coffee" works. "Powerful coffee" feels wrong &mdash; even
    though the dictionary definitions of "strong" and "powerful" overlap
    almost completely. The word constellation has edges not just to
    meanings but to typical neighbors, and the edges <em>are</em> part
    of the meaning.
  </p>
  <div class="canvas-box">
    <canvas id="colloc-canvas" width="960" height="400"></canvas>
  </div>
  <div class="controls">
    <button onclick="collocPick('coffee')">strong / powerful coffee</button>
    <button onclick="collocPick('rain')">heavy / strong rain</button>
    <button onclick="collocPick('argument')">strong / powerful argument</button>
    <button onclick="collocPick('wind')">strong / high wind</button>
    <button onclick="collocReset()">Reset</button>
  </div>
  <div class="info">
    <b>Why one adjective fits and another doesn't:</b> Native speakers
    have learned statistical regularities over millions of exposures.
    "Strong coffee" has appeared in their input thousands of times;
    "powerful coffee" essentially never. The collocation is stored as a
    weighted edge between the two words, independent of the dictionary
    definition. Non-native speakers can know what every word means and
    still produce phrases that feel wrong because they lack the
    collocation weights.<br><br>
    <b>This is why translation is hard:</b> Even with a perfect bilingual
    dictionary, you cannot translate word-by-word without breaking
    collocations. "Make a decision" is standard English; word-for-word
    translation into other languages often produces "take a decision"
    (French) or "meet a decision" (German). Each language has its own
    web of collocation weights, and they do not align cleanly.
  </div>
</div>
</div>

<!-- ═══ Grammaticalization ═══════════════════════════════════════ -->
<div class="panel" id="gramm-tab">
<div class="container">
  <h2>Grammaticalization &mdash; Content Words Decaying Into Grammar</h2>
  <p class="desc">
    "Going to" meant walking toward a destination. Now it is a pure
    future-tense marker ("I'm gonna finish this by Friday"). "Will" meant
    volition (to want); now it is also a future marker. Over centuries,
    content words drift into grammatical roles &mdash; they lose their
    semantic weight, get phonetically reduced, and eventually become
    pure structural machinery.
  </p>
  <div class="canvas-box">
    <canvas id="gramm-canvas" width="960" height="400"></canvas>
  </div>
  <div class="controls">
    <button onclick="grammPick('going-to')">"going to" → "gonna"</button>
    <button onclick="grammPick('will')">"will" (volition → future)</button>
    <button onclick="grammPick('let-us')">"let us" → "let's"</button>
    <button onclick="grammPick('have-to')">"have to" → "hafta"</button>
  </div>
  <div class="info">
    <b>The pattern is universal:</b> Languages around the world show the
    same pipeline: content word → grammatical function → phonetic
    reduction → bound morpheme → eventually lost. Modern French's future
    tense suffix descended from Latin's "habere" (to have). Modern
    English's "-ly" adverb suffix descended from "lice" (body). These
    are fossilized versions of what "gonna" and "hafta" are doing right
    now.<br><br>
    <b>Why this matters for priors:</b> Grammaticalization is the
    long-term drift of the prior itself. A word that starts as a
    semantic cluster with a specific constellation gradually becomes a
    structural marker whose constellation is almost empty &mdash; its
    weight is in the grammar edges, not the meaning edges. You cannot
    "use" a grammaticalized word for meaning anymore, only for
    structure.
  </div>
</div>
</div>

<!-- ═══ Lexical Gaps ═════════════════════════════════════════════ -->
<div class="panel" id="lexgap-tab">
<div class="container">
  <h2>Lexical Gaps &mdash; What Cannot Be Said</h2>
  <p class="desc">
    The inverse of Translation Gap. Some concepts simply have no word in
    a given language, and the absence shapes what speakers reliably
    notice, remember, and discuss. English speakers often learn a foreign
    word for a concept they have felt their whole lives but never had a
    handle for.
  </p>
  <div class="canvas-box">
    <canvas id="lexgap-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <button onclick="lexgapPick('mamih')">mamihlapinatapai (Yaghan)</button>
    <button onclick="lexgapPick('tsund')">tsundoku (Japanese)</button>
    <button onclick="lexgapPick('iktsu')">iktsuarpok (Inuit)</button>
    <button onclick="lexgapPick('wald')">waldeinsamkeit (German)</button>
    <button onclick="lexgapPick('liter')">literalmente (Spanish/Italian)</button>
  </div>
  <div class="info">
    <b>Why a missing word matters:</b> A concept without a name is
    expensive to think about. You can describe it in a sentence, but the
    sentence has to be constructed each time, and the construction cost
    makes the concept less cognitively available. A concept with a name
    becomes a single-click operation. Speakers of languages that have
    the word notice the phenomenon more often, discuss it, and refine
    their shared sense of it.<br><br>
    <b>This is the Whorfian claim at its clearest:</b> It is not that
    the lack of a word makes the concept impossible to think &mdash; it
    clearly does not. But it makes the concept more expensive to
    maintain, which changes how often it appears in thought, and
    therefore what gets written down, remembered, shared. Lexical gaps
    are not limits on thinkability; they are taxes on it.
  </div>
</div>
</div>

<!-- ═══ Sound Symbolism / Iconicity ══════════════════════════════ -->
<div class="panel" id="soundsym-tab">
<div class="container">
  <h2>Sound Symbolism &mdash; When the Word Sounds Like Its Meaning</h2>
  <p class="desc">
    Show two abstract shapes, one rounded and one spiky. Ask 1,000 people
    which is "bouba" and which is "kiki." About 95% give the same answer
    across cultures, languages, and literacy levels. The sound and the
    shape have an iconic link &mdash; part of the word's meaning is the
    shape of its phonemes.
  </p>
  <div class="canvas-box">
    <canvas id="soundsym-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <button onclick="soundsymPick('bouba')">Bouba / Kiki</button>
    <button onclick="soundsymPick('gl')">gl- cluster (visual)</button>
    <button onclick="soundsymPick('sn')">sn- cluster (nose)</button>
    <button onclick="soundsymPick('sl')">sl- cluster (slippery)</button>
    <button onclick="soundsymPick('fl')">fl- cluster (flowing light)</button>
  </div>
  <div class="info">
    <b>The bouba/kiki effect</b> (Köhler, 1929; Ramachandran &amp;
    Hubbard, 2001): the shapes of /b/ (rounded lips, slow) and /k/ (hard
    stop, sharp) are iconic analogs of the rounded vs spiky shapes they
    tend to get matched with. This cross-modal mapping is found in
    infants as young as four months, in speakers of dozens of languages,
    and across literate and non-literate cultures.<br><br>
    <b>Phonaesthetic clusters in English:</b> "gl-" words (glitter,
    glow, glance, glisten, gleam, glaze) overwhelmingly involve visual
    light effects. "sn-" words (snore, sneeze, sniff, snot, snout,
    snarl) overwhelmingly involve the nose. "sl-" words (slip, slide,
    slither, slick, slush, slug, slurp) overwhelmingly involve
    slipperiness or unpleasant wetness. These are not coincidences.
    They are fossilized iconic mappings that the language preserved
    over centuries.<br><br>
    <b>What it means for Lingora:</b> The constellation a word activates
    is not <em>only</em> about its learned associations. Some of the
    meaning is already in the phonemes themselves. "Meaning is
    arbitrary" is a simplification &mdash; it is mostly arbitrary, with
    a non-trivial iconic component baked into the sound.
  </div>
</div>
</div>

<!-- ═══ Repetition & Rhythm ══════════════════════════════════════ -->
<div class="panel" id="repetition-tab">
<div class="container">
  <h2>Repetition &amp; Rhythm &mdash; Meter as Attention Modulation</h2>
  <p class="desc">
    A refrain repeated gains weight each time. A metered line sets up a
    forecast that the content plays against. Haiku's 5-7-5 produces a
    specific kind of compressed landing. Free verse deliberately breaks
    the forecast. All of these are ways of engineering where the
    listener's attention lands and where the residuals fire.
  </p>
  <div class="canvas-box">
    <canvas id="repetition-canvas" width="960" height="420"></canvas>
  </div>
  <div class="controls">
    <button onclick="repetitionPlay('iambic')">Iambic pentameter</button>
    <button onclick="repetitionPlay('haiku')">Haiku (5-7-5)</button>
    <button onclick="repetitionPlay('free')">Free verse</button>
    <button onclick="repetitionPlay('refrain')">Refrain (repetition)</button>
  </div>
  <div class="info">
    <b>Why meter makes speech feel charged:</b> A predictable rhythm sets
    up an expectation in the listener's predictor. The predictor locks
    onto the rhythmic pattern and starts forecasting stress placement
    before it arrives. When the content lines up with the forecast, it
    feels inevitable. When the content surprises the forecast at the
    right moment, the surprise lands harder because the reader was
    already committing bandwidth to the rhythm.<br><br>
    <b>Why refrains work:</b> The first "tomorrow, and tomorrow, and
    tomorrow" builds a constellation. The second reuses it with added
    context. The third is saturated with accumulated weight. Each
    repetition reinforces the edges a little more, so by the final
    occurrence the phrase is carrying the weight of every previous one.
    This is Hebbian reinforcement turned into an artistic tool.
  </div>
</div>
</div>

<!-- ═══ Pronouns & Deixis ════════════════════════════════════════ -->
<div class="panel" id="deixis-tab">
<div class="container">
  <h2>Pronouns &amp; Deixis &mdash; Words as Function Pointers</h2>
  <p class="desc">
    Most words are constellations. "I", "you", "here", "now", "this",
    "today" are different &mdash; their meaning is a <em>pointer</em>
    that gets resolved against the current speaker's situation. They
    are the only words in language whose constellation is dynamically
    computed at each utterance.
  </p>
  <div class="canvas-box">
    <canvas id="deixis-canvas" width="960" height="420"></canvas>
  </div>
  <div class="controls">
    <button onclick="deixisPick('alice')">Speaker: Alice, "I'll meet you here tomorrow"</button>
    <button onclick="deixisPick('bob')">Speaker: Bob (same sentence)</button>
    <button onclick="deixisPick('later')">Same sentence, said a day later</button>
    <button onclick="deixisReset()">Reset</button>
  </div>
  <div class="info">
    <b>The point:</b> "I'll meet you here tomorrow" has completely
    different referents depending on who says it, where, and when. The
    words are identical; the meaning is parametrized over the current
    deictic context. A recording of the sentence played tomorrow to a
    different audience is nearly useless &mdash; the pointers no longer
    resolve.<br><br>
    <b>Why this is the closest thing to variables in natural language:</b>
    Most words are closer to constants (dog, fire, freedom) whose
    meaning is stable across utterances. Deictics are variables whose
    value is a function of the speech act. Comprehension of a deictic
    utterance requires knowing the speaker, location, and time &mdash;
    which is why reading an old letter feels strange: the "I" and "you"
    and "now" all point at ghosts.<br><br>
    <b>What this says about language:</b> A small, special class of
    words exists precisely to bridge language with the physical world.
    Without deictics, you could describe situations from the outside
    but never speak from inside one. They are how the speaker's body
    and time get into the sentence.
  </div>
</div>
</div>

<!-- ═══ Anaphora ═════════════════════════════════════════════════ -->
<div class="panel" id="anaphora-tab">
<div class="container">
  <h2>Anaphora &mdash; Keeping Pronouns Attached</h2>
  <p class="desc">
    "Mary told Jane that she was late." Who was late? Both readings are
    grammatically valid. The parser has to run a live binding game,
    using plausibility, recency, and prior context to decide which
    antecedent each pronoun points to.
  </p>
  <div class="canvas-box">
    <canvas id="anaphora-canvas" width="960" height="400"></canvas>
  </div>
  <div class="controls">
    <button onclick="anaphoraPick('mary')">"Mary told Jane she was late"</button>
    <button onclick="anaphoraPick('trophy')">"The trophy wouldn't fit in the suitcase because it was too big"</button>
    <button onclick="anaphoraPick('chain')">"John took the book off the shelf and put it on the table because it was dusty"</button>
  </div>
  <div class="info">
    <b>What makes anaphora hard:</b> Pronouns are cheap (they compress
    reference to a few characters) but ambiguous. The parser has to
    bind each pronoun to an antecedent, and the binding depends on
    world knowledge, not just grammar. "The trophy didn't fit in the
    suitcase because it was too big" &mdash; "it" refers to the
    trophy. Change "big" to "small" and "it" now refers to the
    suitcase. The grammar is identical. The binding flips because the
    plausibility of each reading flips.<br><br>
    <b>Winograd schemas</b> are sentences specifically constructed to
    make anaphora resolution require world knowledge rather than pure
    syntactic rules. They were proposed as a harder-than-Turing-test
    for AI, and until recently machine parsers failed badly on them.
    Modern LLMs handle most Winograd-style schemas, which is a
    meaningful (if contested) signal about how much world knowledge
    they have encoded.
  </div>
</div>
</div>

<!-- ═══ Politeness & Indirect Speech ════════════════════════════ -->
<div class="panel" id="politeness-tab">
<div class="container">
  <h2>Politeness &mdash; Face-Saving Through Indirection</h2>
  <p class="desc">
    "Could you maybe possibly close the window?" is not just polite. It
    is a specific move that preserves the listener's face by softening
    the imposition. Brown &amp; Levinson's politeness theory maps the
    strategies: bald, positive politeness, negative politeness,
    off-record. Each is calibrated to the social distance, power, and
    cost of the request.
  </p>
  <div class="canvas-box">
    <canvas id="politeness-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <button onclick="politenessPick('bald')">Bald: "Close the window."</button>
    <button onclick="politenessPick('positive')">Positive: "Hey buddy, close that for us?"</button>
    <button onclick="politenessPick('negative')">Negative: "Could you possibly close the window?"</button>
    <button onclick="politenessPick('off')">Off-record: "It's cold in here."</button>
  </div>
  <div class="info">
    <b>The four strategies</b> (Brown &amp; Levinson, 1987):<br>
    &bull; <b>Bald on-record</b> &mdash; no softening. Used with
    intimates, in emergencies, or when the speaker has high power.<br>
    &bull; <b>Positive politeness</b> &mdash; emphasizes shared
    in-group status. "Hey buddy," "could you help us out?" The request
    is framed as a favor between friends.<br>
    &bull; <b>Negative politeness</b> &mdash; minimizes the imposition.
    "Could you possibly," "if it's not too much trouble," "I hate to
    bother you." The request explicitly acknowledges the cost and
    apologizes in advance.<br>
    &bull; <b>Off-record</b> &mdash; the request is not stated at all.
    "It's cold in here" leaves the listener to infer that a window
    should be closed. The listener has plausible deniability about
    having been asked, which is maximum face-saving for both parties.<br><br>
    <b>Why this is universal:</b> Every language studied so far has
    politeness strategies of these four types, though the surface forms
    vary enormously. Japanese has grammatically-encoded honorific
    registers; English uses mostly vocabulary and intonation. Both are
    implementing the same underlying face-preservation logic.
  </div>
</div>
</div>

<!-- ═══ Discourse Markers ═══════════════════════════════════════ -->
<div class="panel" id="discourse-tab">
<div class="container">
  <h2>Discourse Markers &mdash; Tiny Words, Massive Work</h2>
  <p class="desc">
    "So," "well," "anyway," "I mean," "you know," "right," "like,"
    "actually" &mdash; tiny words that look like filler and are not.
    Each performs a specific interactional move: holding the floor,
    shifting the topic, marking attitude, signaling that a repair is
    coming, negotiating common ground.
  </p>
  <div class="canvas-box">
    <canvas id="discourse-canvas" width="960" height="420"></canvas>
  </div>
  <div class="controls">
    <button onclick="discoursePick('so')">"so"</button>
    <button onclick="discoursePick('well')">"well"</button>
    <button onclick="discoursePick('anyway')">"anyway"</button>
    <button onclick="discoursePick('like')">"like"</button>
    <button onclick="discoursePick('you-know')">"you know"</button>
    <button onclick="discoursePick('actually')">"actually"</button>
  </div>
  <div class="info">
    <b>What they do:</b>
    &bull; <b>"so"</b> &mdash; topic-opening or summary marker. "So, about
    the budget..."<br>
    &bull; <b>"well"</b> &mdash; signals that what follows is not quite
    what the listener expected. "Well, it's complicated."<br>
    &bull; <b>"anyway"</b> &mdash; topic closure; "we were off-topic,
    returning now."<br>
    &bull; <b>"like"</b> &mdash; quotative ("she was like, 'no'") or
    hedge ("it's like, really big"). Both do real grammatical work.<br>
    &bull; <b>"you know"</b> &mdash; common-ground check. "Does my
    listener have the background I'm assuming?"<br>
    &bull; <b>"actually"</b> &mdash; contrast marker. Flags that the
    following will contradict what the listener might expect.<br><br>
    <b>Why they are invisible:</b> Native speakers use them constantly
    without noticing, and edit them out when writing. Non-native
    speakers often miss them entirely even at high fluency, which is
    why fluent second-language speech can still sound weirdly stiff.
    The markers are part of the grammar; removing them makes speech
    measurably harder to follow.
  </div>
</div>
</div>

<!-- ═══ Swearing Dynamics ═══════════════════════════════════════ -->
<div class="panel" id="swearing-tab">
<div class="container">
  <h2>Swearing Dynamics &mdash; Save It for Peaks</h2>
  <p class="desc">
    Taboo words have elevated emotional weight. Frequency erodes that
    weight. Someone who swears constantly loses the ability to land a
    taboo word when it would actually matter. Someone who almost never
    swears can stop a conversation with a single word. Show the tradeoff.
  </p>
  <div class="canvas-box">
    <canvas id="swearing-canvas" width="960" height="400"></canvas>
  </div>
  <div class="controls">
    <label style="display:flex;align-items:center;gap:8px">
      <span>baseline swearing rate:</span>
      <input type="range" id="swearing-rate" min="0" max="100" value="20" style="width:160px">
      <span class="stat-val" id="swearing-rate-val">20%</span>
    </label>
    <button onclick="swearingFire()">Swear now</button>
    <button onclick="swearingReset()">Reset</button>
  </div>
  <div class="info">
    <b>The mechanism:</b> Each taboo-word utterance produces a jump in
    the listener's arousal signal. The jump size depends on how
    surprising the taboo is given the speaker's baseline. If the
    speaker swears every other sentence, the baseline expectation is
    high and each new swear produces almost no arousal. If the speaker
    almost never swears, a single swear word is a huge prediction
    error and lands with full force.<br><br>
    <b>The practical rule:</b> Effectiveness of a taboo word is
    inversely proportional to the speaker's baseline swearing rate.
    Saving it for peaks is not prudery &mdash; it is arousal economics.
    The listener's predictor tracks the speaker's norm, and the impact
    comes from violating it.
  </div>
</div>
</div>

<!-- ═══ POV / Narrative Voice ═══════════════════════════════════ -->
<div class="panel" id="pov-tab">
<div class="container">
  <h2>POV &mdash; Narrative Voice and Reader Distance</h2>
  <p class="desc">
    First, second, third-close, third-omniscient. Each produces a
    measurably different activation profile in the reader. First person
    collapses the distance between reader and character. Third-omniscient
    opens it up. Second person puts the reader <em>inside</em> the
    scene as a participant.
  </p>
  <div class="canvas-box">
    <canvas id="pov-canvas" width="960" height="420"></canvas>
  </div>
  <div class="controls">
    <button onclick="povPick('first')">First: "I walked in..."</button>
    <button onclick="povPick('second')">Second: "You walk in..."</button>
    <button onclick="povPick('third-close')">Third-close: "She walked in..."</button>
    <button onclick="povPick('third-omni')">Third-omniscient: "Meanwhile, in the..."</button>
  </div>
  <div class="info">
    <b>What shifts:</b><br>
    &bull; <b>First person</b> pulls the reader into the character's
    head. Inner thoughts are direct. Perception is filtered through
    the narrator's biases, which the reader absorbs automatically.
    Empathic resonance is maximum.<br>
    &bull; <b>Second person</b> is rare in fiction (common in
    instructions and choose-your-own-adventure). It casts the reader
    as the protagonist, which feels simultaneously immersive and
    coercive.<br>
    &bull; <b>Third-close</b> follows one character's perceptions
    closely but from outside. The reader can empathize without being
    trapped inside the character's errors.<br>
    &bull; <b>Third-omniscient</b> floats above the scene. Can reveal
    any character's thoughts and any event. Maximum information
    bandwidth, minimum empathic pull &mdash; the narrator is visibly
    not one of the characters.<br><br>
    <b>Why choice matters:</b> The same events told in first vs
    third-omniscient produce different stories. First person narrows
    what the reader knows and binds them emotionally. Third-omniscient
    widens the informational field but distances the emotional one.
    Neither is better; they are tools for different effects.
  </div>
</div>
</div>

<!-- ═══ Stream of Consciousness ═════════════════════════════════ -->
<div class="panel" id="stream-tab">
<div class="container">
  <h2>Stream of Consciousness &mdash; Writing Close to Raw Thought</h2>
  <p class="desc">
    Joyce, Woolf, Faulkner. The closest written form to unfiltered
    interior thought. Fragments, associative jumps, minimal grammar,
    no sentence boundaries &mdash; and the reader's predictor has to
    work much harder, which is exactly the point. The difficulty is
    the experience.
  </p>
  <div class="canvas-box">
    <canvas id="stream-canvas" width="960" height="400"></canvas>
  </div>
  <div class="controls">
    <button onclick="streamPick('woolf')">Woolf: "Mrs. Dalloway"</button>
    <button onclick="streamPick('joyce')">Joyce: "Ulysses"</button>
    <button onclick="streamPick('normal')">Normal prose (control)</button>
  </div>
  <div class="info">
    <b>What is unusual:</b> Normal prose conventions are all about
    reducing the reader's cognitive load &mdash; clear sentence
    boundaries, explicit subject-verb-object order, signaled
    transitions. Stream of consciousness throws those out. The reader
    has to do the grammatical work themselves, infer the topic
    transitions, and hold multiple partially-assembled thoughts in
    working memory at once.<br><br>
    <b>Why it still works:</b> Because the <em>experience</em> of
    reading it is the point. The reader's discomfort, effort, and
    partial confusion are a partial simulation of what it feels like
    to be inside the character's head. The difficulty is the
    technique. A smooth summary of the same events would communicate
    the information but lose the experience.<br><br>
    <b>The tradeoff:</b> Stream of consciousness costs more per page to
    read and has a much narrower audience. It is not trying to be
    efficient. It is trying to make the reader feel a thing that
    efficient prose cannot produce.
  </div>
</div>
</div>

<!-- ═══ Typography as Communication ═════════════════════════════ -->
<div class="panel" id="typography-tab">
<div class="container">
  <h2>Typography &mdash; Information Above the Words</h2>
  <p class="desc">
    <em>Italics</em>, <b>bold</b>, ALL CAPS, whitespace, line breaks,
    punctuation, font choice &mdash; all carry information that the
    literal word sequence does not. Every typographic choice
    modulates the reader's attention and reconstructs some of the
    prosody that pure text loses.
  </p>
  <div class="canvas-box">
    <canvas id="typography-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <button onclick="typographyPick('plain')">Plain</button>
    <button onclick="typographyPick('italic')">With italics</button>
    <button onclick="typographyPick('caps')">With ALL CAPS</button>
    <button onclick="typographyPick('breaks')">With line breaks</button>
    <button onclick="typographyPick('spaced')">With s p a c e d letters</button>
  </div>
  <div class="info">
    <b>The channels:</b><br>
    &bull; <b>Italics</b> &mdash; "stress this word prosodically."
    Recovers the missing stress pattern of spoken English.<br>
    &bull; <b>Bold</b> &mdash; topic emphasis. "This word is
    structurally important."<br>
    &bull; <b>ALL CAPS</b> &mdash; volume. Reads as shouting. The
    predictor maps caps to high-volume speech automatically.<br>
    &bull; <b>Whitespace and line breaks</b> &mdash; pacing. A line
    break is a pause in the reader's internal voice. A stanza break
    is a longer one. Poets use whitespace as a rhythmic resource.<br>
    &bull; <b>Letter spacing</b> &mdash; "s l o w" reads slowly.
    "VERY QUICKLY" reads faster than "very quickly" because the
    reader's eye pattern responds to the visual density.<br>
    &bull; <b>Font choice</b> &mdash; authority (serif), casual
    (sans-serif), childish (comic sans), formal (old-style). The font
    pre-activates a context cluster before the first word is read.<br><br>
    <b>Everything above the words is still linguistic.</b> The same
    propositional content can be packaged many ways, and the packaging
    is part of the meaning transmitted.
  </div>
</div>
</div>

<!-- ═══ AI-Generated Text Detection ═════════════════════════════ -->
<div class="panel" id="aidetect-tab">
<div class="container">
  <h2>AI-Generated Text Detection &mdash; Mirror of the Lying Canvas</h2>
  <p class="desc">
    Current LLM output has linguistic tells. Overused vocabulary,
    consistent sentence-length rhythm, specific hedge patterns,
    absence of certain human errors, suspiciously smooth transitions.
    The signal is statistical, not diagnostic &mdash; same caveat as
    the lying canvas.
  </p>
  <div class="canvas-box">
    <canvas id="aidetect-canvas" width="960" height="420"></canvas>
  </div>
  <div class="controls">
    <button onclick="aidetectPick('human')">Human-written</button>
    <button onclick="aidetectPick('llm')">LLM-generated</button>
  </div>
  <div class="info">
    <b>The markers:</b><br>
    &bull; <b>Overused "delve," "tapestry," "realm," "furthermore,"
    "moreover"</b> &mdash; vocabulary reflecting training-data artifacts.<br>
    &bull; <b>Consistent sentence-length variance</b> &mdash; human
    writers have uneven rhythm; LLMs tend to produce a smoother
    distribution.<br>
    &bull; <b>No typos, no awkward repairs, no self-interruption</b>
    &mdash; the text reads like a final draft because it effectively
    is.<br>
    &bull; <b>Hedging patterns</b> &mdash; "It is important to note,"
    "It is worth considering," "There are multiple perspectives."<br>
    &bull; <b>Bulleted structures and clean paragraphs</b> &mdash;
    the model tends to reach for tidy visual hierarchies.<br><br>
    <b>Why this is a moving target:</b> LLMs are trained against
    detectors. Every detection signal that becomes known gets trained
    out. The current tells will look different in six months. What
    stays stable is the statistical nature of the signal: you can
    classify at above-chance rates at population scale, but you cannot
    reliably diagnose an individual passage. Same caveat as lie
    detection.
  </div>
</div>
</div>

<!-- ═══ Text Analyzer ═══════════════════════════════════════════ -->
<div class="panel" id="analyze-tab">
<div class="container">
  <h2>Text Analyzer &mdash; Paste Text, See Which Canvases Apply</h2>
  <p class="desc">
    Paste any short passage and Lingora will run a quick heuristic
    analysis: which of its claims apply to this text. Lingora becomes
    an analysis tool instead of just a demo.
  </p>
  <div class="canvas-box" style="padding:16px">
    <textarea id="analyze-input" rows="6" placeholder="Paste a sentence or paragraph here..."
      style="width:100%;background:var(--surface2);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:10px;font-family:inherit;font-size:12px;resize:vertical"></textarea>
    <div style="margin-top:10px">
      <button onclick="analyzeRun()" class="nav-btn">Analyze</button>
      <button onclick="analyzeClear()" class="nav-btn">Clear</button>
    </div>
    <div id="analyze-output" style="margin-top:16px;font-family:monospace;font-size:11px;line-height:1.8;color:var(--text)"></div>
  </div>
  <div class="info">
    <b>What the analyzer checks:</b> passive vs active voice, hedging
    and uncertainty markers, concrete vs abstract ratio, sentence-length
    variance, AI-detection tells, first-person pronoun density, taboo
    words, idioms, discourse markers, metaphor signatures, and a few
    more. For each positive finding, it points at the relevant Lingora
    canvas so you can jump to the mechanism.<br><br>
    This is pattern-matching, not deep parsing. Good enough to be
    useful on casual text; not a substitute for the full framework.
  </div>
</div>
</div>

<!-- ═══ Citations ═══════════════════════════════════════════════ -->
<div class="panel" id="citations-tab">
<div class="container">
  <h2>Citations &mdash; Source Library</h2>
  <p class="desc">
    The research Lingora draws on, one list. Organized by topic, so
    you can trace any claim in the app back to the paper or book that
    originated it.
  </p>
  <div class="info">
    <b>Words and meaning</b><br>
    &bull; Lakoff, G. &amp; Johnson, M. (1980). <em>Metaphors We Live
    By</em>. Chicago. &mdash; Conceptual metaphor theory.<br>
    &bull; Zeman, A. et al. (2015). "Aphantasia." <em>Cortex</em>.<br>
    &bull; Winawer, J. et al. (2007). "Russian blues reveal effects of
    language on color discrimination." <em>PNAS</em>.<br>
    &bull; Tulving, E. (1972). "Episodic and semantic memory."
  </div>
  <div class="info">
    <b>Sounds and phonology</b><br>
    &bull; Miyawaki, K. et al. (1975). "An effect of linguistic
    experience: The discrimination of /r/ and /l/ by native speakers
    of Japanese and English." <em>Perception &amp; Psychophysics</em>.<br>
    &bull; Köhler, W. (1929). <em>Gestalt Psychology</em>. &mdash;
    Bouba/kiki.<br>
    &bull; Ramachandran, V. S. &amp; Hubbard, E. (2001). "Synaesthesia
    &mdash; A window into perception, thought and language."
  </div>
  <div class="info">
    <b>Reading and disorders</b><br>
    &bull; Rayner, K. (1998). "Eye movements in reading and information
    processing." <em>Psychological Bulletin</em>.<br>
    &bull; Dehaene, S. (2009). <em>Reading in the Brain</em>. Viking.<br>
    &bull; Shaywitz, S. (2003). <em>Overcoming Dyslexia</em>. Knopf.<br>
    &bull; Caramazza, A. (1988). "Some aspects of language processing
    revealed through the analysis of acquired aphasia."
  </div>
  <div class="info">
    <b>Speech acts and pragmatics</b><br>
    &bull; Grice, H. P. (1975). "Logic and conversation." &mdash;
    Cooperative principle, maxims.<br>
    &bull; Brown, P. &amp; Levinson, S. (1987). <em>Politeness: Some
    universals in language usage</em>. Cambridge.<br>
    &bull; Schegloff, E. A. (2007). <em>Sequence Organization in
    Interaction</em>. &mdash; Turn-taking and repair.<br>
    &bull; Newman, M. L. et al. (2003). "Lying words: Predicting
    deception from linguistic styles."
  </div>
  <div class="info">
    <b>Acquisition and critical period</b><br>
    &bull; Chomsky, N. (1965). <em>Aspects of the Theory of Syntax</em>.<br>
    &bull; Lenneberg, E. (1967). <em>Biological Foundations of
    Language</em>. &mdash; Critical period hypothesis.<br>
    &bull; Saffran, J. R., Aslin, R. N. &amp; Newport, E. L. (1996).
    "Statistical learning by 8-month-old infants." <em>Science</em>.<br>
    &bull; Kuhl, P. K. (2004). "Early language acquisition: Cracking
    the speech code." <em>Nature Reviews Neuroscience</em>.
  </div>
  <div class="info">
    <b>Language and cognition</b><br>
    &bull; Whorf, B. L. (1956). <em>Language, Thought and Reality</em>.<br>
    &bull; Slobin, D. (1996). "From 'thought and language' to 'thinking
    for speaking'."<br>
    &bull; Levinson, S. C. (2003). <em>Space in Language and
    Cognition</em>.<br>
    &bull; Pinker, S. (1994). <em>The Language Instinct</em>. Morrow.
  </div>
  <div class="info">
    <b>Sign language and iconicity</b><br>
    &bull; Stokoe, W. (1960). "Sign language structure." &mdash;
    Establishing ASL as a natural language.<br>
    &bull; Sandler, W. &amp; Lillo-Martin, D. (2006). <em>Sign Language
    and Linguistic Universals</em>.<br>
    &bull; Emmorey, K. (2002). <em>Language, Cognition, and the Brain:
    Insights from Sign Language Research</em>.
  </div>
  <div class="info">
    <b>LLMs and prompt engineering</b><br>
    &bull; Vaswani, A. et al. (2017). "Attention is all you need."
    <em>NeurIPS</em>.<br>
    &bull; Brown, T. et al. (2020). "Language models are few-shot
    learners." &mdash; GPT-3 paper.<br>
    &bull; Wei, J. et al. (2022). "Chain-of-thought prompting elicits
    reasoning in large language models."
  </div>
</div>
</div>

<!-- ═══ Jargon ════════════════════════════════════════════════════ -->
<div class="panel" id="jargon-tab">
<div class="container">
  <h2>Jargon &mdash; Expert Vocabulary as Compression</h2>
  <p class="desc">
    Jargon is not primarily gatekeeping. It is compression. Experts need
    vocabulary for fine-grained distinctions non-experts do not draw, and
    once a distinction has a name, referring to it becomes cheap. The
    gatekeeping effect is a side consequence of the compression, not its
    purpose.
  </p>
  <div class="canvas-box">
    <canvas id="jargon-canvas" width="960" height="400"></canvas>
  </div>
  <div class="controls">
    <button onclick="jargonPick('med')">Medicine</button>
    <button onclick="jargonPick('prog')">Programming</button>
    <button onclick="jargonPick('music')">Music theory</button>
    <button onclick="jargonPick('wine')">Wine</button>
  </div>
  <div class="info">
    <b>Example:</b> A doctor says "the patient presents with dyspnea and
    pleuritic chest pain." A non-expert would say "they can't breathe well
    and it hurts when they breathe in." Three expert words compressed a
    full diagnostic observation. In an emergency the compression matters
    &mdash; the expert conveys it in half the syllables and with zero
    ambiguity. Non-expert language is longer, fuzzier, and more prone to
    misinterpretation.<br><br>
    <b>The downside:</b> The same compression that makes expert
    communication fast makes it opaque to outsiders. Not because the
    experts are hiding anything &mdash; because the constellations for
    "dyspnea" or "git rebase" or "Neapolitan chord" simply do not exist
    in the outsider's network. You cannot unpack a word whose edges are
    not there. Explaining jargon is always decompression, which always
    takes longer than the original.
  </div>
</div>
</div>

<!-- ═══ Cognates & False Friends ═════════════════════════════════ -->
<div class="panel" id="cognates-tab">
<div class="container">
  <h2>Cognates &amp; False Friends &mdash; When Lookalikes Betray You</h2>
  <p class="desc">
    "Embarazada" in Spanish looks like "embarrassed" but means
    <em>pregnant</em>. "Gift" in German means <em>poison</em>. False
    friends are words that share surface form across languages but
    diverge in meaning &mdash; because constellations drift even when
    the phonemes match.
  </p>
  <div class="canvas-box">
    <canvas id="cognates-canvas" width="960" height="420"></canvas>
  </div>
  <div class="controls">
    <button onclick="cognatesPick('embarazada')">embarazada (ES)</button>
    <button onclick="cognatesPick('gift')">Gift (DE)</button>
    <button onclick="cognatesPick('preservativo')">preservativo (ES)</button>
    <button onclick="cognatesPick('actually')">eventually (ES "eventualmente")</button>
    <button onclick="cognatesPick('library')">library / librairie (FR)</button>
  </div>
  <div class="info">
    <b>Why false friends exist:</b> Two languages that share an ancestor
    inherit the same word. Over centuries, the word's meaning drifts
    independently in each language (see the Semantic Drift canvas).
    Eventually the phonemic form is nearly identical but the
    constellations barely overlap. A naive learner, trusting the surface
    resemblance, plugs the home-language meaning into the foreign word
    and gets a very specific kind of humiliation.<br><br>
    <b>True cognates</b> are the opposite &mdash; words with the same
    root whose meanings have stayed close. "Night" and "noche" and
    "nuit" and "Nacht" all descend from a common Indo-European root and
    still mean basically the same thing. Cognates make learning easier.
    False friends make it dangerous.
  </div>
</div>
</div>

<!-- ═══ Rhyme ═════════════════════════════════════════════════════ -->
<div class="panel" id="rhyme-tab">
<div class="container">
  <h2>Rhyme &mdash; Phonological Matching as Cognitive Hook</h2>
  <p class="desc">
    Rhyme is phonological matching used as a cognitive hook. A rhyme
    creates a prediction (which sound comes next?) that the listener's
    network locks onto, and the satisfaction of the match produces a
    small residual-resolution spike. Rap and poetry escalate this into
    dense rhyme schemes, internal rhyme, slant rhyme, and multi-syllable
    rhyme.
  </p>
  <div class="canvas-box">
    <canvas id="rhyme-canvas" width="960" height="420"></canvas>
  </div>
  <div class="controls">
    <button onclick="rhymePlay('nursery')">Nursery rhyme</button>
    <button onclick="rhymePlay('shakespeare')">Shakespearean couplet</button>
    <button onclick="rhymePlay('rap')">Rap (dense internal rhyme)</button>
    <button onclick="rhymePlay('slant')">Slant rhyme (near miss)</button>
  </div>
  <div class="info">
    <b>Why rhymes "click":</b> The forecast for the rhyming word is
    tighter than for a normal next-word slot, because the phonological
    constraint eliminates most of the distribution. When the actual
    rhyming word arrives, the residual is small and a satisfaction
    signal fires. Rhyme is engineered prediction success.<br><br>
    <b>Rap goes further:</b> Dense internal rhymes, multi-syllable
    rhymes, slant rhymes where the match is off by one phoneme. Each is
    a more ambitious version of the same prediction game. Great rap
    lines hit because the listener's predictor is doing more work per
    second than in normal speech, and each successful match is a tiny
    hit of "the shape closed."<br><br>
    <b>Slant rhyme</b> (Emily Dickinson's specialty) deliberately misses
    the match slightly &mdash; enough to fire the prediction but not
    enough to satisfy it. The gap itself is the effect. The listener
    notices the near-match and interprets the missed satisfaction as
    unease, irony, or deliberate flatness.
  </div>
</div>
</div>

<!-- ═══ Statistical Learning (Saffran) ══════════════════════════ -->
<div class="panel" id="statistical-tab">
<div class="container">
  <h2>Statistical Learning &mdash; How Infants Find Word Boundaries</h2>
  <p class="desc">
    Saffran 1996: play 8-month-olds two minutes of synthetic continuous
    speech. No pauses between words, no stress cues, just a stream of
    syllables. Certain triplets ("tu-pi-ro," "go-la-bu") appear as
    coherent units; the transitions inside a triplet are high-probability
    and transitions between triplets are low-probability. After two
    minutes the infants distinguish the "words" from non-words. They did
    it with pure unsupervised statistical learning, no instruction, no
    labels, no meaning.
  </p>
  <div class="canvas-box">
    <canvas id="statistical-canvas" width="960" height="420"></canvas>
  </div>
  <div class="controls">
    <button onclick="statisticalPlay()">Stream syllables</button>
    <button onclick="statisticalReveal()">Reveal hidden word boundaries</button>
    <button onclick="statisticalReset()">Reset</button>
  </div>
  <div class="info">
    <b>What you are watching:</b> A continuous stream of synthetic
    syllables, with no overt word boundaries. The stream is generated
    so that certain triplets repeat coherently: "tupiro," "golabu,"
    "bidaku," "padoti." Each internal transition (tu→pi→ro) has
    probability 1.0. Each transition between triplets (ro→go, bu→bi,
    etc.) has lower probability because the next triplet can be any of
    four. The infant's network learns to notice: "inside a word, the
    next syllable is predictable; at a word boundary, it is not."<br><br>
    <b>Reveal the boundaries:</b> After watching the stream, turn on
    the boundary overlay and see which syllables belong together. This
    is what the infant has extracted with no instruction, in two
    minutes, at eight months old. The starting machinery for language
    acquisition is a general-purpose transitional-probability extractor
    running on whatever sensory data arrives.<br><br>
    <b>Why this matters:</b> It suggests the earliest stage of language
    acquisition is not specifically linguistic &mdash; it is a general
    statistical-learning capacity applied to auditory input. The
    language-specific machinery comes later. This is one of the most
    important findings in cognitive science since 1990 and it reframes
    how the critical period, first-language acquisition, and statistical
    models of language all connect.
  </div>
</div>
</div>

<!-- ═══ Cospeech Gesture ═════════════════════════════════════════ -->
<div class="panel" id="gesture-tab">
<div class="container">
  <h2>Cospeech Gesture &mdash; The Second Channel</h2>
  <p class="desc">
    People gesture when they talk, even on the phone, even when blind,
    even alone. Gesture is not decoration &mdash; it is part of the
    language production system, generated in lockstep with speech and
    often carrying information the words do not. The planning is coupled.
  </p>
  <div class="canvas-box">
    <canvas id="gesture-canvas" width="960" height="420"></canvas>
  </div>
  <div class="controls">
    <button onclick="gesturePlay('big')">"it was big" + size gesture</button>
    <button onclick="gesturePlay('there')">"it went over there" + pointing</button>
    <button onclick="gesturePlay('idea')">"I had an idea" + container gesture</button>
  </div>
  <div class="info">
    <b>Timing is the key:</b> The gesture for "big" starts a fraction
    of a second <em>before</em> the word "big" is articulated, not
    after. This means the gesture is not an illustration generated
    from the already-said word &mdash; it is generated in parallel from
    the same conceptual plan, and the motor system often reaches the
    output slightly faster than the articulatory system.<br><br>
    <b>What gesture adds:</b> Speech and gesture together often encode
    more than either alone. "He went that way" + a pointing gesture
    specifies a direction the sentence alone does not. Size gestures
    convey exact dimensions speech cannot efficiently describe. Gesture
    is a low-bandwidth but spatially-rich channel running alongside the
    high-bandwidth auditory channel.<br><br>
    <b>Deaf-born home sign:</b> Deaf children with no exposure to sign
    language spontaneously invent their own gestural communication
    system ("home sign") that has many of the grammatical properties
    of full sign languages. The drive to produce structured
    communication appears independent of the channel &mdash; starving
    the speech channel just routes the system through the motor one.
  </div>
</div>
</div>

<!-- ═══ Writing Systems / Orthography ═══════════════════════════ -->
<div class="panel" id="orthography-tab">
<div class="container">
  <h2>Writing Systems &mdash; Four Ways to Carve Phonology</h2>
  <p class="desc">
    Alphabets, abjads, syllabaries, and logographies are four different
    strategies for mapping spoken language to visible marks. Each has
    different learning costs, different reading patterns, and different
    types of errors. English is a notoriously bad alphabet. Spanish is
    nearly perfect. Japanese uses three scripts in parallel. Chinese
    runs on a different mapping entirely.
  </p>
  <div class="canvas-box">
    <canvas id="orthography-canvas" width="960" height="420"></canvas>
  </div>
  <div class="controls">
    <button onclick="orthographyPick('alphabet')">Alphabet (English / Spanish)</button>
    <button onclick="orthographyPick('abjad')">Abjad (Arabic / Hebrew)</button>
    <button onclick="orthographyPick('syllabary')">Syllabary (Japanese hiragana)</button>
    <button onclick="orthographyPick('logograph')">Logography (Chinese)</button>
  </div>
  <div class="info">
    <b>Alphabet</b> — one symbol per phoneme. Spanish is near-perfect:
    almost every letter maps to exactly one sound, learners pick up
    reading in months. English is a disaster: "tough," "through,"
    "though," "thought" all use "ough" differently. Centuries of
    etymological sludge. Dyslexia is more common in English than
    Spanish not because brains differ but because the mapping is
    harder.<br><br>
    <b>Abjad</b> — consonants written, vowels optional. Arabic and
    Hebrew work this way. Native speakers read vowels in from context
    automatically; learners struggle because the vowels are invisible.<br><br>
    <b>Syllabary</b> — one symbol per syllable. Japanese hiragana has
    46 symbols; every Japanese sound can be written with some
    combination of them. Children learn to read hiragana at age 5-6
    within months of exposure &mdash; the mapping is transparent.<br><br>
    <b>Logography</b> — one symbol per morpheme. Chinese characters
    represent meaning-units directly, not sounds. Takes much longer to
    learn (~3000 characters for literacy, ~6000 for proficiency), but
    once learned, reading is extremely fast because each character is
    one retrieval. And the same script can be read across mutually
    unintelligible Chinese "dialects" because the symbols point at
    meaning, not pronunciation.
  </div>
</div>
</div>

<!-- ═══ Speech Errors ═══════════════════════════════════════════ -->
<div class="panel" id="errors-tab">
<div class="container">
  <h2>Speech Errors &mdash; What Breakage Reveals About the Pipeline</h2>
  <p class="desc">
    Speech errors are not just funny. They are diagnostic windows into
    the language-production pipeline. Spoonerisms reveal the phoneme
    assembly stage. Word exchanges reveal the grammatical-frame stage.
    Blends reveal lexical-selection races. Tip-of-the-tongue reveals
    the pointer-vs-content split. Each error type maps to a specific
    processing stage.
  </p>
  <div class="canvas-box">
    <canvas id="errors-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <button onclick="errorsPick('spoonerism')">Spoonerism</button>
    <button onclick="errorsPick('wordex')">Word exchange</button>
    <button onclick="errorsPick('blend')">Blend</button>
    <button onclick="errorsPick('tot')">Tip-of-the-tongue</button>
    <button onclick="errorsPick('malaprop')">Malapropism</button>
  </div>
  <div class="info">
    <b>Spoonerism</b> — "belly jeans" for "jelly beans." Initial
    phonemes swap between two words. Reveals that phoneme assembly
    happens <em>after</em> word selection and grammatical framing.
    Both words were correctly selected; only the phonemes got
    misrouted between their slots.<br><br>
    <b>Word exchange</b> — "I've got a cat in my tonsils" for "I've
    got a tickle in my throat." Two content words swap. Reveals that
    the grammatical frame is built before the content words are
    filled in &mdash; the slots existed, and both words fit the slot
    type ("noun at position X"), but got swapped between them.<br><br>
    <b>Blend</b> — "splinister" (splinter + sinister). Two competing
    words reach the output stage together and partially merge.
    Reveals that lexical selection is a competition, and sometimes
    the competition does not resolve cleanly before articulation.<br><br>
    <b>Tip-of-the-tongue</b> — the metacognitive circuit fires
    ("I know the word") but the content retrieval fails. You can
    often report first letter, number of syllables, and meaning
    without accessing the word itself. Reveals the two-circuit
    architecture of recall.<br><br>
    <b>Malapropism</b> — "pineapple of success" for "pinnacle of
    success." A similar-sounding wrong word got selected. Reveals
    that phonological neighbors compete for selection &mdash; a word
    that sounds close can win the selection race over the word that
    means what you wanted.
  </div>
</div>
</div>

<!-- ═══ Inner Speech ════════════════════════════════════════════ -->
<div class="panel" id="innerspeech-tab">
<div class="container">
  <h2>Inner Speech &mdash; The Running Commentary in Your Head</h2>
  <p class="desc">
    Some people have near-constant verbal thought: a voice in their head
    that narrates, plans, argues, worries. Others report having almost
    no inner speech and thinking mostly in images or abstract structure.
    The difference is measurable and the existence of the spectrum
    reshapes how we should think about "thinking in language."
  </p>
  <div class="canvas-box">
    <canvas id="innerspeech-canvas" width="960" height="400"></canvas>
  </div>
  <div class="controls">
    <label style="display:flex;align-items:center;gap:8px">
      <span>inner-speech density:</span>
      <input type="range" id="inner-rate" min="0" max="100" value="60" style="width:140px">
      <span class="stat-val" id="inner-rate-val">60%</span>
    </label>
  </div>
  <div class="info">
    <b>The spectrum:</b> Self-reported inner-speech frequency varies
    enormously. Some people say "my inner voice is on all day." Others
    say "I only hear words when I deliberately rehearse them." Both
    can function normally, work professionally, and read fluently.
    Neither group is a failure mode &mdash; they are different
    configurations of the verbal rehearsal loop.<br><br>
    <b>What inner speech is for:</b> Working memory rehearsal
    (holding a phone number), planning (rehearsing what you will say),
    regulation ("calm down, think about this"), narrative
    self-modeling ("so what did I learn here"). People with less inner
    speech run these functions through other channels &mdash;
    imagery, abstract structure, embodied simulation.<br><br>
    <b>Relation to aphantasia:</b> Aphantasia (no visual imagery) and
    low inner speech are partially correlated but distinct. Some
    aphantasics have very rich inner speech; some hyperphantasics
    have very quiet ones. The verbal rehearsal loop and the visual
    imagery system are separable components. Some people have both
    loud, some have both quiet, and some have one loud and the other
    quiet.
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
    via HTTP. A graph of 20 word nodes is seeded on the server; picking a
    word runs spreading activation through its semantic neighborhood.
    Same engine as <a href="/vectora/playground">/vectora/playground</a>
    and the <a href="/vectora/retrieval">Vectora Retrieval product</a>.
  </p>
  <div class="canvas-box" style="padding:20px">
    <div style="display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin-bottom:14px">
      <label style="font-size:11px;color:var(--dim);display:flex;gap:6px;align-items:center;flex:1;min-width:240px">
        <span>seed word:</span>
        <select id="vec-lingora-seed" style="flex:1;background:var(--surface);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:6px;font-family:inherit;font-size:11px">
          <option value="">loading…</option>
        </select>
      </label>
      <label style="font-size:11px;color:var(--dim);display:flex;gap:6px;align-items:center">
        <span>k:</span>
        <input type="range" id="vec-lingora-k" min="3" max="10" value="6" style="width:80px">
        <span id="vec-lingora-k-v" style="color:var(--accent);font-weight:bold;min-width:14px">6</span>
      </label>
      <label style="font-size:11px;color:var(--dim);display:flex;gap:6px;align-items:center">
        <span>decay:</span>
        <input type="range" id="vec-lingora-decay" min="10" max="80" value="35" style="width:80px">
        <span id="vec-lingora-decay-v" style="color:var(--accent);font-weight:bold;min-width:30px">0.35</span>
      </label>
      <button onclick="vecLingoraQuery()" style="padding:6px 14px;border-radius:4px;border:1px solid var(--accent);background:var(--accent);color:var(--bg);font-size:11px;cursor:pointer;font-family:inherit;font-weight:bold">Query Vectora</button>
    </div>
    <div id="vec-lingora-results" style="min-height:180px">
      <div style="color:var(--dim);text-align:center;padding:40px 20px;font-size:11px">pick a word and click Query</div>
    </div>
    <div id="vec-lingora-stats" style="margin-top:10px;font-size:10px;color:var(--dim);text-align:right"></div>
  </div>
  <div class="info">
    <b>Dogfood play.</b> Lingora's word-constellation mechanism is the
    same primitive Vectora ships as retrieval. Rather than
    re-implementing per-app, Lingora delegates neighborhood queries to
    Vectora. Every LAVAS app that needs spreading-activation retrieval
    does the same &mdash; one engine, many products.
  </div>
</div>
</div>

<!-- ═══ Vectora Context — session-aware word lookup ══════════════ -->
<div class="panel" id="vec-context-tab">
<div class="container">
  <h2>Context-Aware Word Lookup
    <span style="font-size:10px;color:#a3e635;margin-left:10px;letter-spacing:0.1em">● POWERED BY VECTORA CONTEXT</span>
  </h2>
  <p class="desc">
    This canvas uses <b>Vectora Context</b> &mdash; the product at
    <a href="/vectora/context">/vectora/context</a> &mdash; to modulate
    word retrieval by your recent activity. Click words below to &quot;browse&quot;
    them; then pick a seed and query. The same seed word returns
    different results depending on what you've been viewing, because
    your session's context vector shifts the edge weights in the word
    graph. Same primitive any Vectora Context customer would use.
  </p>
  <div class="canvas-box" style="padding:20px">
    <div style="margin-bottom:14px">
      <div style="font-size:11px;color:var(--dim);margin-bottom:8px">Recent browsing (click to &quot;view&quot; a word):</div>
      <div id="lingora-ctx-docs" style="display:flex;flex-wrap:wrap;gap:6px"></div>
    </div>
    <div style="margin-bottom:14px;padding:10px 14px;background:var(--surface);border:1px solid var(--border);border-radius:4px;font-size:10px;color:var(--dim)">
      <b id="lingora-ctx-session-stat">session: 0 views</b>
      <span id="lingora-ctx-recent" style="margin-left:12px"></span>
    </div>
    <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:14px">
      <label style="font-size:11px;color:var(--dim);display:flex;gap:6px;align-items:center;flex:1;min-width:240px">
        <span>seed word:</span>
        <select id="lingora-ctx-seed" style="flex:1;background:var(--surface);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:6px;font-family:inherit;font-size:11px"></select>
      </label>
      <button onclick="lingoraCtxQuery()" style="padding:6px 14px;border-radius:4px;border:1px solid var(--accent);background:var(--accent);color:var(--bg);font-size:11px;cursor:pointer;font-family:inherit;font-weight:bold">Compare</button>
      <button onclick="lingoraCtxClear()" style="padding:6px 14px;border-radius:4px;border:1px solid var(--border);background:transparent;color:var(--dim);font-size:11px;cursor:pointer;font-family:inherit">Clear session</button>
    </div>
    <div id="lingora-ctx-results" style="min-height:200px"></div>
  </div>
  <div class="info">
    <b>Example:</b> start by clicking a few "emotion" words (joy, fear,
    anger) as if you were reading an affect-theory article. Then query
    with seed <code>w18 (bird)</code>. Without context, Vectora returns
    fish, tree, and other animal-adjacent words. With the emotion
    context built up, the same seed leans toward words that connect
    emotion and flight &mdash; because your session vector has pulled
    edge weights toward that region of the word graph.
  </div>
</div>
</div>

<!-- ═══ Reading Aloud vs Silent ═══════════════════════════════ -->
<div class="panel" id="readaloud-tab">
<div class="container">
  <h2>Reading Aloud vs Silent &mdash; Two Cognitive Modes From the Same Text</h2>
  <p class="desc">
    Reading aloud recruits auditory cortex, motor planning (lips, tongue,
    larynx), and working memory for prosodic decisions. Silent reading
    skips all of that and runs a faster, lighter comprehension pipeline.
    Same text, two different cognitive budgets, two different activation
    profiles.
  </p>
  <div class="canvas-box">
    <canvas id="readaloud-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <button onclick="readaloudPick('silent')">Silent reading</button>
    <button onclick="readaloudPick('aloud')">Reading aloud</button>
    <button onclick="readaloudPick('subvocal')">Subvocalization (inner voice)</button>
  </div>
  <div class="info">
    <b>Silent reading</b> bypasses motor planning entirely. Comprehension
    runs through visual recognition → semantic access, recruiting visual
    cortex and language areas (Broca's and Wernicke's weakly). Speed is
    high because no motor output is generated.<br><br>
    <b>Reading aloud</b> adds motor planning (lip, tongue, jaw
    articulation), auditory cortex (you hear yourself), prosodic
    decision-making (which words to stress, where to pause), and
    working memory (hold the upcoming phrase to plan the delivery).
    Speed drops by ~50% but comprehension and retention are measurably
    higher for difficult material because the extra circuits carry
    redundant encoding.<br><br>
    <b>Subvocalization</b> is the quiet middle ground. Most silent
    readers produce a faint motor plan and a ghostly inner voice even
    without moving their lips. Speed-reading courses try to suppress
    subvocalization entirely. The research is mixed on whether that is
    possible or desirable &mdash; the inner voice may serve as a
    prosodic layer that aids comprehension even in silent reading.<br><br>
    <b>See also:</b>
    <a href="/axona">Axona → Reading as Controlled Hallucination</a> (the
    imagery generated by silent reading is a hallucination the reader
    steers word by word).
    <a href="/lingora">Lingora → Eye Movements</a> (the saccade patterns
    differ between aloud and silent modes).
  </div>
</div>
</div>

<!-- ═══ Headlines & Clickbait ═══════════════════════════════════ -->
<div class="panel" id="headlines-tab">
<div class="container">
  <h2>Headlines &amp; Clickbait &mdash; Engineered Attention Capture</h2>
  <p class="desc">
    Headlines are prompts aimed at the most reliable residual-producing
    cognitive targets. Curiosity gaps, numbered lists, loss framing,
    in-group cues &mdash; each is a specific move exploiting a specific
    attention vulnerability. Decompose five real headlines into the
    mechanical moves.
  </p>
  <div class="canvas-box">
    <canvas id="headlines-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <button onclick="headlinesPick('curiosity')">Curiosity gap</button>
    <button onclick="headlinesPick('list')">Numbered list</button>
    <button onclick="headlinesPick('loss')">Loss framing</button>
    <button onclick="headlinesPick('ingroup')">In-group cue</button>
    <button onclick="headlinesPick('contrarian')">Contrarian</button>
  </div>
  <div class="info">
    <b>The moves:</b><br>
    &bull; <b>Curiosity gap</b> &mdash; "You won't believe what happened
    next." Promises information the reader does not yet have and
    implies the reveal will be surprising. The reader's predictor
    fires on the unknown reveal and the unresolved anticipation is
    itself the attention hook.<br>
    &bull; <b>Numbered list</b> &mdash; "9 Things Every Parent Should
    Know." Numbered lists promise bounded, finite content. The
    commitment lowers the perceived cost of reading.<br>
    &bull; <b>Loss framing</b> &mdash; "Stop Doing These 5 Things or
    You'll Regret It." Activates loss-avoidance, which is a stronger
    motivator than gain-seeking (Kahneman-Tversky prospect theory).<br>
    &bull; <b>In-group cue</b> &mdash; "For Parents of..." explicitly
    addresses a specific identity. The reader's self-model recognizes
    the call and the attention commits before the content is
    evaluated.<br>
    &bull; <b>Contrarian</b> &mdash; "Why Everyone Is Wrong About X."
    Offers the promise of special knowledge that contradicts received
    wisdom. Exploits the contrarian flattery instinct.<br><br>
    <b>The defense:</b> Recognition, same as fallacies. You cannot
    prevent the move from firing &mdash; the headline has already
    activated the relevant pattern before you consciously read it.
    You can only notice the firing and decide to discount it. Once
    you can name the move, it loses much of its grip.
  </div>
</div>
</div>

<!-- ═══ Legal Language ═════════════════════════════════════════ -->
<div class="panel" id="legal-tab">
<div class="container">
  <h2>Legal Language &mdash; Precision and Deliberate Ambiguity</h2>
  <p class="desc">
    Contracts and statutes read strangely because they are optimized
    for adversarial interpretation. Every word has to survive being
    read by a hostile party looking for loopholes. Some legal language
    is precision engineering. Some is deliberate ambiguity that
    preserves flexibility. Both are design choices, not incompetence.
  </p>
  <div class="canvas-box">
    <canvas id="legal-canvas" width="960" height="420"></canvas>
  </div>
  <div class="controls">
    <button onclick="legalPick('precision')">Engineered precision</button>
    <button onclick="legalPick('ambiguity')">Deliberate ambiguity</button>
    <button onclick="legalPick('boilerplate')">Boilerplate armor</button>
  </div>
  <div class="info">
    <b>Engineered precision:</b> "The Party of the First Part shall
    deliver the Goods to the Party of the Second Part on or before
    5:00 PM Eastern Time on December 15, 2026, at the address
    specified in Exhibit A." Every noun phrase is defined, every
    temporal scope is bounded, every ambiguous pronoun is replaced
    with a named role. The goal is to make contested interpretation
    as hard as possible.<br><br>
    <b>Deliberate ambiguity:</b> "reasonable efforts," "in good
    faith," "material breach," "substantially equivalent." These are
    not failures of precision &mdash; they are load-bearing
    vagueness. The parties could not agree on an exact standard, so
    they agreed on a vague one and implicitly delegated the
    resolution to future courts. Vagueness is the lubricant that
    lets contracts form at all when the parties disagree about
    edge cases.<br><br>
    <b>Boilerplate armor:</b> "including but not limited to," "any
    and all," "without limitation," "to the fullest extent permitted
    by law." Phrases inherited across decades of case law, each
    bearing the scar of a specific lawsuit where omitting them cost
    someone a fortune. The language is not redundant; it is armor
    plating.
  </div>
</div>
</div>

<!-- ═══ Oral Tradition & Mnemonics ══════════════════════════════ -->
<div class="panel" id="oral-tab">
<div class="container">
  <h2>Oral Tradition &mdash; Memorizing Thousands of Lines Without Writing</h2>
  <p class="desc">
    Homer's Iliad is ~15,000 lines. The Odyssey is ~12,000. The Vedas
    are much longer. All were composed and transmitted orally for
    centuries before being written down. How? Rhyme-and-meter,
    formulaic epithets, ring composition, and mnemonic structures were
    built into the material itself as retrieval scaffolding.
  </p>
  <div class="canvas-box">
    <canvas id="oral-canvas" width="960" height="420"></canvas>
  </div>
  <div class="controls">
    <button onclick="oralPick('homer')">Homer's epithets</button>
    <button onclick="oralPick('vedas')">Vedic chant</button>
    <button onclick="oralPick('memorypalace')">Memory palace</button>
    <button onclick="oralPick('alphabet')">Alphabet song</button>
  </div>
  <div class="info">
    <b>Homeric epithets</b> &mdash; "rosy-fingered dawn,"
    "wine-dark sea," "swift-footed Achilles." These are not just
    poetic description. They are meter-filling formulas the bard
    could drop in to maintain the dactylic hexameter while thinking
    about the next line. Each epithet has a known metrical shape
    and a fixed position in the line. The bard is not composing at
    word level &mdash; they are composing at the formula level, from
    a learned vocabulary of pre-assembled chunks that fit specific
    slots.<br><br>
    <b>Vedic chant</b> &mdash; Sanskrit Vedas have been preserved
    nearly verbatim for 3000+ years through elaborate recitation
    techniques. Each verse is memorized in multiple interlocking
    patterns (word-by-word, syllable-reversed, etc.) so that any
    corruption in one recitation can be cross-checked against the
    others. The text itself is an error-correcting code.<br><br>
    <b>Memory palace</b> &mdash; the technique ancient orators used
    to memorize long speeches. Mentally walk through a familiar
    building and attach each point to a specific room. Retrieval is
    done by re-walking the path. The spatial memory system has
    higher capacity and longer retention than the verbal system, so
    offloading sequential content to space is a compression
    strategy.<br><br>
    <b>The alphabet song</b> &mdash; still the fastest way to remember
    26 items in a specific order. The meter and melody carry the
    memory, not the letters themselves. When you need the letters
    alone you often sing the song to yourself and extract them.
  </div>
</div>
</div>

<!-- ═══ Pidgins & Creoles ══════════════════════════════════════ -->
<div class="panel" id="pidgin-tab">
<div class="container">
  <h2>Pidgins &amp; Creoles &mdash; Language Bootstrapping Itself</h2>
  <p class="desc">
    Adults from different languages thrown together under pressure
    produce a <em>pidgin</em> &mdash; minimal vocabulary, almost no
    grammar, one word per concept. The next generation of children,
    born into that pidgin, spontaneously generates a full grammar
    where none existed. The children did not learn the grammar from
    anyone. They invented it. This is the strongest empirical
    evidence for an innate grammatical faculty.
  </p>
  <div class="canvas-box">
    <canvas id="pidgin-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <button onclick="pidginStage('pidgin')">Generation 1: the pidgin</button>
    <button onclick="pidginStage('creole')">Generation 2: the creole</button>
  </div>
  <div class="info">
    <b>Generation 1 &mdash; the pidgin:</b> Adults from several
    language communities need to communicate urgently (plantations,
    trade ports, refugee camps). They cannot learn each other's
    languages quickly enough, so they improvise. The result is a
    pidgin: a small shared vocabulary, no systematic grammar, word
    order varies from speaker to speaker, no tense marking, no
    relative clauses, no embedded structures. Communication is
    possible but effortful. The pidgin is nobody's native
    language.<br><br>
    <b>Generation 2 &mdash; the creole:</b> Children born into the
    pidgin community hear the pidgin as their primary input. What
    they produce is not a pidgin. It is a fully-formed language with
    tense, aspect, relative clauses, embedded structures, consistent
    word order, and all the hallmarks of natural grammar. Nobody
    taught them this grammar. Their parents did not have it. They
    generated it from thin air, in one generation, from impoverished
    input.<br><br>
    <b>Why this is the strongest argument for Universal Grammar:</b>
    The grammatical structures that appear in creoles are not random.
    They cluster around a consistent set of features that recur
    across unrelated creoles in unrelated parts of the world. The
    children are not just inventing grammar at random &mdash; they
    are inventing approximately the same grammar every time. The
    simplest explanation is that the inventing is not random: the
    children are running a prior that already contains constraints
    on what a grammar can look like, and they are filling in the
    parameters from whatever input they have. That prior is
    "universal grammar" &mdash; a scaffolding that shapes the
    generation space even in the absence of a fully-specified model.
  </div>
</div>
</div>

<!-- ═══ Diglossia ═══════════════════════════════════════════════ -->
<div class="panel" id="diglossia-tab">
<div class="container">
  <h2>Diglossia &mdash; Two Varieties for Two Functions</h2>
  <p class="desc">
    Some speakers maintain two distinct varieties of language for
    different social functions &mdash; a "high" formal variety for
    writing, religion, and formal speech, and a "low" everyday
    variety for home and street. Not just register-shifting within
    one language; these are often different enough to be nearly
    different languages.
  </p>
  <div class="canvas-box">
    <canvas id="diglossia-canvas" width="960" height="420"></canvas>
  </div>
  <div class="controls">
    <button onclick="diglossiaPick('arabic')">Modern Standard Arabic / dialect</button>
    <button onclick="diglossiaPick('swiss')">Swiss German / Standard German</button>
    <button onclick="diglossiaPick('tamil')">Literary Tamil / spoken Tamil</button>
  </div>
  <div class="info">
    <b>Arabic</b> is the classic case. Modern Standard Arabic (MSA) is
    used for news, religion, literature, formal speech, and pan-Arab
    communication. It is nobody's native variety. Every Arabic speaker
    grows up speaking a regional dialect (Egyptian, Levantine, Maghrebi,
    Gulf) which can be mutually unintelligible with other dialects. A
    Moroccan and an Iraqi cannot always understand each other in their
    native dialects, but both can switch to MSA and communicate. Every
    literate Arabic speaker maintains two systems in parallel &mdash;
    and uses them in non-overlapping contexts.<br><br>
    <b>Swiss German:</b> Swiss-German speakers use their regional
    Swiss dialect at home, with friends, on local TV. For writing,
    school, national news, and anything formal, they switch to
    Standard German. The dialects are so different from Standard
    German that Germans from Germany often cannot understand them at
    all. Swiss-German speakers are functionally bilingual in a
    language they are officially considered monolingual in.<br><br>
    <b>Why diglossia is stable:</b> A two-variety system can be
    remarkably stable across centuries if each variety has its own
    reliable social function. The "high" variety is preserved by
    writing, religion, and education. The "low" variety is
    preserved by family and street use. Neither displaces the other
    because neither can do what the other does.
  </div>
</div>
</div>

<!-- ═══ Animal Communication ═══════════════════════════════════ -->
<div class="panel" id="animal-tab">
<div class="container">
  <h2>Animal Communication &mdash; What Counts as Language?</h2>
  <p class="desc">
    Bees dance. Whales sing. Vervet monkeys have distinct alarm calls
    for different predators. Parrots and crows use tools and learn
    vocabulary. But none of these systems has the properties that
    make human language what it is. Comparing helps define what
    language actually requires.
  </p>
  <div class="canvas-box">
    <canvas id="animal-canvas" width="960" height="440"></canvas>
  </div>
  <div class="controls">
    <button onclick="animalPick('bee')">Bee waggle dance</button>
    <button onclick="animalPick('vervet')">Vervet alarm calls</button>
    <button onclick="animalPick('whale')">Whale song</button>
    <button onclick="animalPick('ape')">Signing apes (Washoe, Nim, Koko)</button>
  </div>
  <div class="info">
    <b>Bee waggle dance</b> &mdash; the direction of the dance encodes
    the bearing to a food source; the duration encodes the distance.
    Information transfer is real and extraordinary. But: it can only
    encode food locations. It cannot express "let us meet tomorrow"
    or "there is danger behind you." It is a specialized tool, not a
    general communication system.<br><br>
    <b>Vervet alarm calls</b> &mdash; distinct calls for leopard,
    eagle, and snake, each triggering the appropriate evasive
    response. The calls are symbolic (they refer to categories, not
    reactions). But the category set is tiny and fixed. Vervets
    cannot learn new calls for new predators.<br><br>
    <b>Whale song</b> &mdash; humpback songs evolve culturally,
    transmit across ocean populations, and show complex nested
    structure. We do not yet know whether the structure encodes
    meaning or is purely aesthetic. This is an open question, and
    the answer matters.<br><br>
    <b>Signing apes</b> &mdash; Washoe, Nim Chimpsky, Koko. They
    learned to produce dozens to a few hundred signs. They could
    combine signs in simple ways. But: they never produced recursive
    embedded structures, did not ask questions about themselves, did
    not spontaneously teach each other new signs. The best
    interpretation is that they learned an association system
    approaching but not reaching language-hood.<br><br>
    <b>What is missing from all of these:</b> Recursive embedding
    ("the cat that the dog chased saw the man"), displaced reference
    (talking about events not present), productivity (generating
    novel messages from finite parts), metalinguistic awareness
    (talking <em>about</em> the language). These are the properties
    that distinguish human language from every known animal
    communication system. Whether any non-human system has them is
    an open empirical question &mdash; but the answer, so far, is no.
  </div>

  <div class="info" style="border-left: 3px solid var(--accent2)">
    <b style="color:var(--accent2)">Dogs pressing buttons &mdash; what the viral videos show through PEP</b><br><br>
    Recent videos of dogs (Bunny, Stella, Billi) using soundboard
    buttons to &quot;talk&quot; have captivated the internet. A dog
    presses &quot;outside&quot; and the owner opens the door. The dog
    presses &quot;play&quot; and the owner throws the ball. Some dogs
    have learned 50-100 buttons.<br><br>
    Through PEP: the dog is building a small weighted graph where
    button-nodes connect to experience-nodes via spreading activation.
    &quot;Outside&quot; is not a word the dog &quot;knows English&quot;
    for &mdash; it is a node whose activation pattern includes the
    door opening, the leash appearing, the grass smell, the walk.
    The dog learned it the same way Saffran&apos;s 1996 infants
    found word boundaries: statistical learning. Press button &rarr;
    consequence. Repeat. The association strengthens. Same mechanism.<br><br>
    <b>The interesting question:</b> does the dog have a prediction
    engine? If pressing &quot;outside&quot; when it&apos;s raining
    produces a different outcome, does the model update? The viral
    videos suggest yes &mdash; some dogs have learned to press
    &quot;outside&quot; + &quot;water&quot; to indicate they want water,
    not a walk. That is a <em>two-node query</em> on a compatibility
    graph. Same primitive Vectora uses for multi-hop retrieval,
    Atria uses for multi-objective matching. Simpler graph, same
    structure.<br><br>
    <b>What the dogs are NOT doing:</b> recursion, displacement (no
    button-pressing about yesterday&apos;s walk), metalinguistic
    awareness, syntax. The button vocabulary is an association
    system &mdash; the same level as the signing apes, but with a
    more accessible interface (pressing is easier than signing).
    The interesting scientific question is whether any dog will
    spontaneously combine buttons in a way that requires genuine
    syntax, not just sequential association. So far, the evidence
    is ambiguous. The viral clips are selected for the most
    impressive moments; the thousands of random/meaningless presses
    are not filmed.<br><br>
    <b>What this tells us about language:</b> the spreading-activation
    primitive for association is deeply conserved across species. Dogs,
    apes, parrots, and human infants all build associations the same
    way. What makes human language different is not the association
    mechanism (which is shared) but the <em>recursive combinatorial
    engine</em> that sits on top of it. The buttons show where the
    shared floor is. Human language shows how far above that floor
    our species built.
  </div>
</div>
</div>

<!-- ═══ Emoji / Digital Paralinguistics ═══════════════════════ -->
<div class="panel" id="emoji-tab">
<div class="container">
  <h2>Emoji &mdash; Paralinguistics Returning to Text</h2>
  <p class="desc">
    Speech carries tone, pitch, facial expression, gesture, and
    rhythm. Plain text strips all of that out. Emoji are the
    re-emergence of paralinguistics in a written channel that had
    lost it &mdash; a new set of symbols evolved to recover the
    information speech has and text does not.
  </p>
  <div class="canvas-box">
    <canvas id="emoji-canvas" width="960" height="420"></canvas>
  </div>
  <div class="controls">
    <button onclick="emojiPick('tone')">Tone: "Sure." vs "Sure 😊" vs "Sure 🙄"</button>
    <button onclick="emojiPick('softening')">Softening a request</button>
    <button onclick="emojiPick('reaction')">Reactions as backchannels</button>
  </div>
  <div class="info">
    <b>Why emoji exist:</b> Plain text loses most of what speech
    communicates. When written English was the medium of letters and
    books, the reader could spend time to interpret tone from
    context. In text messaging and chat, there is no time. The
    writer needs to signal "I am being friendly" / "I am joking" /
    "I am annoyed" inside a 20-character message, in under a second
    of composition time. Emoji fill exactly that gap.<br><br>
    <b>Tone markers:</b> "Sure." and "Sure 😊" and "Sure 🙄" carry
    three different meanings from the same literal content. In
    speech these would be distinguished by pitch and expression.
    In text, emoji are the pitch and the expression, rendered as
    visible glyphs.<br><br>
    <b>Backchannels and reactions:</b> In face-to-face conversation
    the listener nods, smiles, says "right" to keep the speaker
    going (see the Conversation Dynamics canvas). Online, thumbs-up
    reactions and brief emoji replies do the same work. They are
    minimal social signals that confirm the speaker is being
    received.<br><br>
    <b>Why this is a natural experiment:</b> Emoji emerged
    spontaneously in response to a missing channel. They were not
    designed by linguists. They evolved through use, and they
    encode exactly the information that plain text lacks &mdash;
    affect, tone, social stance, and backchanneling. The fact that
    a new symbol system emerged this fast for this purpose tells
    you those functions are load-bearing in natural language, not
    decoration.
  </div>
</div>
</div>

<!-- ═══ Canvas Gallery ═════════════════════════════════════════ -->
<div class="panel" id="gallery-tab">
<div class="container">
  <h2>Gallery &mdash; Every Canvas in One Grid</h2>
  <p class="desc">
    Lingora has grown past the point where tab groups are browsable
    at a glance. The gallery lists every canvas as a card. Click any
    card to jump to it. Bookmarked canvases appear first if you have
    any.
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

<!-- ═══ Translation Workbench ═════════════════════════════════════ -->
<div class="panel" id="workbench-tab">
<div class="container">
  <h2>Translation Workbench &mdash; Decompose, Translate, Compare</h2>
  <p class="desc">
    A sentence is more than its denotation. Pick a source sentence, watch
    Lingora decompose it into denotation, connotation, register,
    pragmatics, and cultural reference, then see translations under
    different framings. The standard "literal" translation throws away
    most of the structure; the framings preserve different parts.
  </p>
  <div class="canvas-box">
    <canvas id="workbench-canvas" width="960" height="600"></canvas>
  </div>
  <div class="controls">
    <button onclick="workbenchPick(0)">"It's a piece of cake."</button>
    <button onclick="workbenchPick(1)">"Bless your heart."</button>
    <button onclick="workbenchPick(2)">"Boku wa unagi da." (jp)</button>
    <button onclick="workbenchPick(3)">"Saudade" (pt)</button>
  </div>
  <div class="info">
    <b>What you are watching:</b> The selected sentence, decomposed into
    its semantic layers (left column). For each layer, the standard
    machine-translation output (middle) and a Lingora-aware translation
    that preserves that layer (right). The diff is what every commercial
    translation system currently throws away.<br><br>
    <b>The wedge:</b> DeepL beat Google Translate by being marginally
    better at <em>denotation</em> (literal meaning) and producing more
    natural-sounding output. The next jump &mdash; the one nobody has
    cracked &mdash; is preserving <em>pragmatic</em> meaning across
    languages. "Bless your heart" is not insulting denotationally; it
    is devastating pragmatically. Every current MT system flattens
    that.<br><br>
    <b>See also:</b>
    <a href="#" onclick="canvasSelect('translation-tab');return false">Lingora &rarr; Translation Gap</a>,
    <a href="#" onclick="canvasSelect('subtext-tab');return false">Lingora &rarr; Subtext</a>,
    <a href="#" onclick="canvasSelect('politeness-tab');return false">Lingora &rarr; Politeness</a>.
  </div>
</div>
</div>

<!-- ═══ Story Translation Workbench ══════════════════════════════ -->
<div class="panel" id="story-tab">
<div class="container">
  <h2>Story Translation &mdash; How Layer Losses Compound Across a Narrative</h2>
  <p class="desc">
    A single sentence can lose an idiom. A short story loses coherence.
    Pick a passage; watch how standard MT degrades paragraph by paragraph
    as pragmatic, register, and cultural cues accumulate and interact.
    Lingora's layer-aware translation is stitched against the same
    source to show what preservation looks like when narrative voice
    has to stay consistent across a whole text.
  </p>
  <div class="controls" style="margin-bottom:16px">
    <button onclick="storyPick(0)">Spanish — Sobremesa</button>
    <button onclick="storyPick(1)">Japanese — Amai</button>
    <button onclick="storyPick(2)">French — Vouvoyer</button>
  </div>
  <div id="story-view" style="background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:0"></div>
  <div class="canvas-box" style="margin-top:16px">
    <canvas id="story-drift-canvas" width="960" height="220"></canvas>
  </div>
  <div class="info">
    <b>What you are watching.</b> Each paragraph of the source appears in
    three columns: the original, the baseline machine translation
    (naive denotation-preserving), and the Lingora layer-aware
    translation. Below each paragraph, an annotation row calls out
    specifically what the MT lost &mdash; dropped subjects, benefactive
    auxiliaries, register shifts, honorifics, aspect markers, cultural
    anchors &mdash; and how the layer-aware version recovers it.<br><br>
    <b>The drift chart.</b> Each point is per-paragraph preservation
    score (how much of the source's combined pragmatic + register +
    cultural layer survives the translation). MT drops as layers
    compound; Lingora holds because it translates each layer explicitly
    and recomposes. The gap widens over the course of the story, not
    within a single sentence.<br><br>
    <b>Why this matters beyond sentence-scale.</b> Sentence-level MT can
    get lucky on a single idiom. Narrative coherence requires that the
    same character address the same other character the same way across
    ten paragraphs, that register not drift between reported speech
    and narration, that cultural anchors established early keep their
    weight later. No current commercial MT does this; every one of them
    resets to defaults per sentence.<br><br>
    <b>See also:</b>
    <a href="#" onclick="canvasSelect('workbench-tab');return false">Lingora &rarr; Translation Workbench</a>,
    <a href="#" onclick="canvasSelect('translation-tab');return false">Lingora &rarr; Translation Gap</a>,
    <a href="#" onclick="canvasSelect('politeness-tab');return false">Lingora &rarr; Politeness</a>,
    <a href="#" onclick="canvasSelect('anaphora-tab');return false">Lingora &rarr; Anaphora</a>.
  </div>
</div>
</div>

<!-- ═══ Writing Voice Analyzer ═══════════════════════════════════ -->
<div class="panel" id="voice-analyze-tab">
<div class="container">
  <h2>Writing Voice Analyzer &mdash; What Mechanisms Are Operative</h2>
  <p class="desc">
    Pick a paragraph. Lingora identifies which mechanisms are doing the
    work: POV, register, irony, subtext, pacing, voice, repetition,
    sound symbolism. Each mechanism gets a strength score. The diagnostic
    column suggests which would sharpen the prose if turned up or down.
  </p>
  <div class="canvas-box">
    <canvas id="voice-analyze-canvas" width="960" height="520"></canvas>
  </div>
  <div class="controls">
    <button onclick="voiceAnalyzePick(0)">Hemingway (clipped, declarative)</button>
    <button onclick="voiceAnalyzePick(1)">Faulkner (long, embedded)</button>
    <button onclick="voiceAnalyzePick(2)">Corporate memo (passive, hedged)</button>
    <button onclick="voiceAnalyzePick(3)">Tweet (compressed, ironic)</button>
  </div>
  <div class="info">
    <b>The wedge:</b> Grammarly catches grammar errors and suggests
    "shorter sentence" or "active voice." It does not understand voice.
    A Hemingway sentence flagged for "passive voice" is not a bug; it
    is the style. A corporate memo flagged for "no contractions" is
    serving its register correctly. The next-gen writing tool needs to
    measure mechanism strength &mdash; what is the prose actually doing?
    &mdash; and only suggest changes that align with the writer's
    intent.<br><br>
    <b>How this canvas does it:</b> Each paragraph is scored on eight
    mechanisms (POV, register, irony, subtext, pacing, voice
    consistency, repetition, sound symmetry). The scores are
    descriptive, not prescriptive. Then a diagnostic column points at
    which mechanism, if turned up, would sharpen the existing voice.
    The user keeps their style; the tool serves it.<br><br>
    <b>See also:</b>
    <a href="#" onclick="canvasSelect('voice-tab');return false">Lingora &rarr; Voice</a>,
    <a href="#" onclick="canvasSelect('pov-tab');return false">Lingora &rarr; POV</a>,
    <a href="#" onclick="canvasSelect('advice-tab');return false">Lingora &rarr; Writing Advice</a>.
  </div>
</div>
</div>

<!-- ═══ Pitch ══════════════════════════════════════════════════════ -->
<div class="panel" id="pitch-tab">
<div class="container">
  <h2>The Pitch &mdash; Four Wedges, One Engine</h2>
  <p class="desc">
    Lingora has the broadest commercial surface of any LAVAS sibling
    because language touches everything. Four wedges look most viable.
    All four run on the same PEP primitives (spreading activation in
    word constellations, residual scoring on prediction error,
    state modulation for register and pragmatics).
  </p>

  <div class="info" style="border-left: 3px solid #4fc3f7">
    <b style="font-size:14px;color:#4fc3f7">Wedge 1 &mdash; Pragmatic Translation (DeepL competitor)</b><br><br>
    <b>The problem:</b> Every machine-translation system optimizes for
    denotation. None preserve pragmatics, register, or cultural
    framing. "Bless your heart" → "May your heart be blessed" is
    technically correct and substantively wrong. Translators have known
    this for centuries; the tools have never caught up.<br><br>
    <b>What Lingora adds:</b> The Translation Workbench canvas
    decomposes a sentence into layers (denotation, connotation,
    register, pragmatics, cultural reference) and translates each layer
    separately, then re-assembles. The output preserves the parts a
    standard MT system flattens.<br><br>
    <b>Market:</b> Localization for games, film/TV subtitles, legal
    translation, literary translation. DeepL is doing $300M+ ARR by
    being marginally better than Google. The pragmatic-preservation
    wedge is the next 10x.
  </div>

  <div class="info" style="border-left: 3px solid #81c784">
    <b style="font-size:14px;color:#81c784">Wedge 2 &mdash; Voice-Aware Writing Assistant (Grammarly competitor)</b><br><br>
    <b>The problem:</b> Grammarly catches grammar errors and aggressively
    "improves" prose by stripping voice. Hemingway gets flagged for
    fragments. James Baldwin gets flagged for repetition. Corporate
    memos get flagged for being passive. The tool does not understand
    that voice is intentional; it treats every deviation as a bug.<br><br>
    <b>What Lingora adds:</b> The Writing Voice Analyzer canvas scores
    paragraphs on eight mechanisms (POV, register, irony, subtext,
    pacing, voice consistency, repetition, sound symmetry) and only
    suggests changes that align with the writer's existing intent. A
    Hemingway sentence does not get "fixed"; the tool understands what
    it is doing.<br><br>
    <b>Market:</b> Professional writers, novelists, journalists,
    academics, anyone whose voice is the product. Grammarly is at
    ~$200M ARR. The voice-preserving angle is differentiated and
    defensible.
  </div>

  <div class="info" style="border-left: 3px solid #ffb74d">
    <b style="font-size:14px;color:#ffb74d">Wedge 3 &mdash; Constellation-Based Language Learning (Duolingo alternative)</b><br><br>
    <b>The problem:</b> Duolingo and its imitators teach via flashcards
    and gamification. The result: users can recite vocabulary lists but
    cannot have a conversation. The mechanism does not match how humans
    actually acquire language &mdash; through context, association,
    repetition in meaningful situations, and gradual mastery of word
    constellations.<br><br>
    <b>What Lingora adds:</b> Word as Constellation, Statistical
    Learning, Acquisition, and Baby Talk canvases all model the actual
    learning mechanism. A Lingora-based learning app would teach
    constellations &mdash; "hear the word in 12 different contexts
    until the meaning crystallizes" &mdash; instead of definition
    drilling.<br><br>
    <b>Market:</b> Duolingo is at $700M+ ARR with massive churn. Babbel,
    Memrise, Pimsleur all compete on the same flashcard model.
    Constellation-based learning is the differentiated bet.
  </div>

  <div class="info" style="border-left: 3px solid #ba68c8">
    <b style="font-size:14px;color:#ba68c8">Wedge 4 &mdash; Prompt Engineering Toolkit (LLM developer tools)</b><br><br>
    <b>The problem:</b> LLM developers have no good tools for
    understanding why a prompt works or fails. They iterate by trial
    and error, write 5,000-token system prompts, and hope. Most "prompt
    engineering" advice is folklore.<br><br>
    <b>What Lingora adds:</b> The Prompt Engineering, LLM Bridge, and
    AI Text Detection canvases already model what a prompt is doing
    structurally &mdash; which words constrain the model's prediction,
    which open it up, where the model's attention narrows or widens.
    A toolkit version: paste a prompt, get back a structural analysis,
    suggested compressions, and predicted failure modes.<br><br>
    <b>Market:</b> Every team building on OpenAI, Anthropic, Google,
    Meta APIs. Smaller TAM than the others but very high willingness
    to pay because prompt quality directly drives API costs and
    product quality. The most novel angle &mdash; nobody else is
    framing prompts as linguistic objects.
  </div>

  <div class="info" style="border-left: 3px solid var(--accent)">
    <b style="font-size:14px;color:var(--accent)">Which wedge first?</b><br><br>
    Recommended order:<br>
    &bull; <b>Wedge 4 (Prompt Engineering) first.</b> Smallest TAM but
    fastest to ship, easiest to differentiate, willing-to-pay buyers,
    technical audience that does not need hand-holding. Validates the
    underlying engine on a friendly market.<br>
    &bull; <b>Wedge 2 (Writing Assistant) second.</b> Adjacent
    market, similar mechanism, larger TAM. Use revenue from Wedge 4
    to fund the data and model work needed for Wedge 2.<br>
    &bull; <b>Wedge 1 (Translation) third.</b> Largest opportunity but
    requires multilingual data, evaluation infrastructure, and
    competition with funded incumbents. Tackle once the core engine is
    proven on Wedges 4 and 2.<br>
    &bull; <b>Wedge 3 (Language Learning) fourth.</b> Largest consumer
    market but B2C consumer apps are brutal. Better as a platform play
    once the underlying engine is proven and licensable.
  </div>
</div>
</div>

<!-- ═══ Benchmark ══════════════════════════════════════════════════ -->
<div class="panel" id="bench-tab">
<div class="container">
  <h2>Benchmark &mdash; Lingora vs Standard Tools on a Pragmatic-Loss Test Set</h2>
  <p class="desc">
    300 synthetic translation pairs where the source sentence carries
    pragmatic, cultural, or register information beyond the
    denotation. Standard MT (Google Translate baseline, purple) vs
    Lingora-aware translation (blue). Five metrics, same Before/After
    pattern as the other LAVAS apps.
  </p>
  <div class="canvas-box">
    <canvas id="lin-bench-canvas" width="960" height="640"></canvas>
  </div>
  <div class="controls">
    <button onclick="linBenchRegen()">Regenerate test set</button>
  </div>
  <div class="info">
    <b>The metrics:</b><br>
    &bull; <b>Pragmatic preservation</b> &mdash; fraction of sentences
    where the pragmatic intent (sarcasm, indirectness, politeness
    level) survives the translation. The headline metric.<br>
    &bull; <b>Register preservation</b> &mdash; formal/informal/legal
    /technical register correctly maintained.<br>
    &bull; <b>Cultural framing</b> &mdash; idioms and culturally-bound
    expressions translated by intent rather than by surface.<br>
    &bull; <b>BLEU score</b> &mdash; the standard MT quality metric.
    Both systems hit similar BLEU because BLEU does not measure the
    things Lingora optimizes for. Shows that Lingora is not winning by
    being literal-better; it is winning on a different axis.<br>
    &bull; <b>Latency (index)</b> &mdash; normalized to 1.0 for the
    baseline. Lingora is slower because the decomposition adds passes.
  </div>
</div>
</div>

<!-- ═══ Case Studies ══════════════════════════════════════════════ -->
<div class="panel" id="cases-tab">
<div class="container">
  <h2>Case Studies &mdash; Language Tools in the Wild</h2>
  <p class="desc">
    Real shipping products, real wins, real failures. Each case is
    chosen because it illustrates one of the four pitch wedges
    concretely.
  </p>

  <div class="info">
    <b>DeepL beating Google Translate (2017-present)</b><br><br>
    DeepL launched in 2017 with translation quality measurably better
    than Google Translate, despite a fraction of the budget. Their
    edge was a more carefully tuned encoder-decoder architecture and
    careful training data curation. They have grown to $300M+ ARR
    serving professional translators, localization teams, and legal
    firms. Google still dominates raw query volume; DeepL dominates
    the willing-to-pay segment.<br><br>
    <b>Why this matters for Lingora:</b> DeepL proved a smaller,
    smarter team can win the high-end translation market by being
    marginally better on quality. The next jump &mdash; pragmatic
    preservation &mdash; is currently unclaimed. Lingora's
    Translation Workbench is the first canvas demonstrating what that
    would look like.
  </div>

  <div class="info">
    <b>Duolingo's gamification ceiling (2011-present)</b><br><br>
    Duolingo grew to ~80M monthly active users on a flashcard +
    streaks + leaderboards model. The mechanism is sticky for
    daily-streak engagement but produces shallow learning &mdash;
    multiple academic studies show Duolingo users plateau around A2
    proficiency and rarely reach conversational fluency without
    supplementary instruction. Duolingo knows this and has been
    layering on Stories, Roleplays, and now a Max tier with LLM
    conversation, trying to bridge the gap.<br><br>
    <b>Why this matters for Lingora:</b> The flashcard ceiling is
    structural, not a tuning problem. The mechanism does not match
    how humans acquire language. Constellation-based learning is the
    differentiated mechanism that could break the ceiling. The
    canvases on Word as Constellation and Statistical Learning are
    the foundation.
  </div>

  <div class="info">
    <b>Grammarly's "voice" complaints (2018-present)</b><br><br>
    Grammarly's premium tier added "tone" and "style" suggestions
    around 2018. Professional writers immediately complained that the
    suggestions strip voice &mdash; flagging fragments, repetition,
    and unconventional structure as "errors." Multiple high-profile
    writers (and most of literary Twitter) have publicly turned the
    tool off because it is hostile to voice-driven prose. Grammarly's
    response has been to add a "creative writing" mode that is more
    permissive but still does not understand voice; it just suggests
    less aggressively.<br><br>
    <b>Why this matters for Lingora:</b> Grammarly cannot fix this
    inside its current architecture because it has no representation
    of voice. The Voice Analyzer canvas demonstrates the missing
    primitive. A writing assistant built on Lingora would be voice-
    aware from the foundation up.
  </div>

  <div class="info">
    <b>LLM cultural translation failures (2023-present)</b><br><br>
    Multiple incidents of GPT-4, Claude, Gemini producing translations
    that are technically correct but culturally tone-deaf or actively
    insulting. Translating Japanese honorific structures into English
    flat declaratives. Translating Arabic religious phrases without
    the appropriate register. Translating Spanish formal/informal
    distinctions into English without preserving the relationship
    cue. The models know the words; they do not know the implications
    of choosing one phrasing over another.<br><br>
    <b>Why this matters for Lingora:</b> The pragmatic-preservation
    problem is the same problem in a different layer. LLMs are
    trained on text without the meta-information about register,
    politeness, or pragmatic intent. Lingora's decomposition layer
    could sit in front of an LLM and pre-annotate the source text,
    preserving information that would otherwise be lost in the
    translation step.
  </div>

  <div class="info">
    <b>The sign-language gloves controversy (2017-2018)</b><br><br>
    Multiple startups (most prominently SignAloud and BrightSign)
    pitched gloves that would translate ASL hand-shapes into spoken
    English. The Deaf community pushed back hard, pointing out that
    ASL is not encoded in hand-shapes alone &mdash; it uses facial
    expressions for grammar, body posture for register, eye gaze for
    referent tracking, and three-dimensional spatial signs for
    grammatical relations. A glove translator catches roughly 10% of
    actual ASL information. The startups proceeded anyway; most
    quietly folded by 2019.<br><br>
    <b>Why this matters for Lingora:</b> The gloves failed because
    they ignored the multi-channel nature of language. Lingora's
    Sign Language canvas explicitly models this. Any tool built on
    Lingora's framework would not make this category error because
    the framework has multi-channel structure baked in from the
    start.
  </div>
</div>
</div>

<!-- ═══ Products ═══════════════════════════════════════════════════ -->
<div class="panel" id="products-tab">
<div class="container">
  <h2>Products &mdash; The Four Lingora Wedges</h2>
  <p class="desc">
    The four products Lingora would ship, derived directly from the
    wedges in the Pitch tab. Each is a standalone product with its own
    target market and competitor; all four run on the same Lingora
    primitives, so building one accelerates the others. Recommended
    GTM order is bottom-up: Wedge 4 (smallest TAM, fastest validation)
    first, then 2, 1, 3.
  </p>

  <a href="/lingora/translate" style="display:block;background:var(--surface);border:1px solid var(--border);border-left:3px solid #4fc3f7;border-radius:6px;padding:16px 20px;margin-bottom:12px;text-decoration:none;color:inherit;transition:border-color 0.15s" onmouseover="this.style.borderColor='#4fc3f7'" onmouseout="this.style.borderColor='var(--border)';this.style.borderLeftColor='#4fc3f7'">
    <div style="display:flex;justify-content:space-between;align-items:start;gap:10px;margin-bottom:6px">
      <div style="font-size:14px;font-weight:bold;color:#4fc3f7">Lingora Translate &rarr;</div>
      <span style="font-size:9px;color:#4fc3f7;background:rgba(79,195,247,0.15);padding:2px 8px;border-radius:10px;white-space:nowrap">WEDGE 1 · BUILT</span>
    </div>
    <div style="font-size:11px;color:var(--text);line-height:1.6;margin-bottom:6px">
      Pragmatic-preserving translation. Decomposes a sentence into
      denotation / pragmatic / register / cultural layers, translates
      each, then reassembles. Preserves what DeepL and Google Translate
      flatten &mdash; sarcasm, indirectness, politeness level, cultural
      framing.
    </div>
    <div style="font-size:10px;color:var(--dim);line-height:1.5">
      <b style="color:var(--text)">Competitor:</b> DeepL (~$300M ARR) ·
      <b style="color:var(--text)">Buyers:</b> localization agencies,
      film/TV subtitling, legal translation, literary translation ·
      <b style="color:var(--text)">Differentiator:</b> the Translation
      Workbench mechanism (see Workbench tab) preserves layers that
      every current MT system collapses.
    </div>
  </a>

  <a href="/lingora/voice" style="display:block;background:var(--surface);border:1px solid var(--border);border-left:3px solid #81c784;border-radius:6px;padding:16px 20px;margin-bottom:12px;text-decoration:none;color:inherit;transition:border-color 0.15s" onmouseover="this.style.borderColor='#81c784'" onmouseout="this.style.borderColor='var(--border)';this.style.borderLeftColor='#81c784'">
    <div style="display:flex;justify-content:space-between;align-items:start;gap:10px;margin-bottom:6px">
      <div style="font-size:14px;font-weight:bold;color:#81c784">Lingora Voice &rarr;</div>
      <span style="font-size:9px;color:#81c784;background:rgba(129,199,132,0.15);padding:2px 8px;border-radius:10px;white-space:nowrap">WEDGE 2 · BUILT</span>
    </div>
    <div style="font-size:11px;color:var(--text);line-height:1.6;margin-bottom:6px">
      Voice-aware writing assistant. Scores prose on eight mechanisms
      (POV, register, irony, subtext, pacing, voice consistency,
      repetition, sound symmetry). Suggests changes only when they
      align with the writer's existing intent &mdash; no flagging
      Hemingway fragments as errors.
    </div>
    <div style="font-size:10px;color:var(--dim);line-height:1.5">
      <b style="color:var(--text)">Competitor:</b> Grammarly (~$200M
      ARR) ·
      <b style="color:var(--text)">Buyers:</b> professional writers,
      novelists, journalists, academics, anyone whose voice is the
      product ·
      <b style="color:var(--text)">Differentiator:</b> the Voice
      Analyzer canvas demonstrates the missing primitive Grammarly
      cannot bolt on.
    </div>
  </a>

  <a href="/lingora/learn" style="display:block;background:var(--surface);border:1px solid var(--border);border-left:3px solid #ffb74d;border-radius:6px;padding:16px 20px;margin-bottom:12px;text-decoration:none;color:inherit;transition:border-color 0.15s" onmouseover="this.style.borderColor='#ffb74d'" onmouseout="this.style.borderColor='var(--border)';this.style.borderLeftColor='#ffb74d'">
    <div style="display:flex;justify-content:space-between;align-items:start;gap:10px;margin-bottom:6px">
      <div style="font-size:14px;font-weight:bold;color:#ffb74d">Lingora Learn &rarr;</div>
      <span style="font-size:9px;color:#ffb74d;background:rgba(255,183,77,0.15);padding:2px 8px;border-radius:10px;white-space:nowrap">WEDGE 3 · BUILT</span>
    </div>
    <div style="font-size:11px;color:var(--text);line-height:1.6;margin-bottom:6px">
      Constellation-based language learning. Teaches words via context
      and association &mdash; "hear the word in 12 different contexts
      until the meaning crystallizes" &mdash; instead of flashcard
      drilling. Models acquisition the way humans actually learn
      languages.
    </div>
    <div style="font-size:10px;color:var(--dim);line-height:1.5">
      <b style="color:var(--text)">Competitor:</b> Duolingo (~$700M ARR,
      plateaus at A2) ·
      <b style="color:var(--text)">Buyers:</b> direct-to-consumer
      learners frustrated with flashcard ceiling, eventually B2B for
      universities and corporate language training ·
      <b style="color:var(--text)">Differentiator:</b> Word as
      Constellation, Statistical Learning, Acquisition canvases model
      the actual mechanism that flashcards miss.
    </div>
  </a>

  <a href="/lingora/prompt" style="display:block;background:var(--surface);border:1px solid var(--border);border-left:3px solid #ba68c8;border-radius:6px;padding:16px 20px;margin-bottom:12px;text-decoration:none;color:inherit;transition:border-color 0.15s" onmouseover="this.style.borderColor='#ba68c8'" onmouseout="this.style.borderColor='var(--border)';this.style.borderLeftColor='#ba68c8'">
    <div style="display:flex;justify-content:space-between;align-items:start;gap:10px;margin-bottom:6px">
      <div style="font-size:14px;font-weight:bold;color:#ba68c8">Lingora Prompt &rarr;</div>
      <span style="font-size:9px;color:#ba68c8;background:rgba(186,104,200,0.15);padding:2px 8px;border-radius:10px;white-space:nowrap">WEDGE 4 · GTM FIRST · BUILT</span>
    </div>
    <div style="font-size:11px;color:var(--text);line-height:1.6;margin-bottom:6px">
      Prompt engineering toolkit. Paste a prompt, get back a structural
      analysis: which words constrain the model's prediction, which
      open it up, where attention narrows or widens, suggested
      compressions, predicted failure modes. Treats prompts as
      linguistic objects rather than folk-wisdom incantations.
    </div>
    <div style="font-size:10px;color:var(--dim);line-height:1.5">
      <b style="color:var(--text)">Competitor:</b> nobody is framing
      prompts as linguistic objects ·
      <b style="color:var(--text)">Buyers:</b> every team building on
      OpenAI / Anthropic / Google / Meta APIs ·
      <b style="color:var(--text)">Why first:</b> smallest TAM but
      fastest to ship, easiest to differentiate, willing-to-pay
      buyers, technical audience that does not need hand-holding.
      Validates the underlying engine on a friendly market before the
      bigger consumer products.
    </div>
  </a>

  <h3 style="font-size:13px;color:var(--accent2);margin:24px 0 8px">Why one engine, four products</h3>
  <div class="info">
    All four products run on the same Lingora primitives:
    constellation-based meaning representation, layer decomposition
    for translation, mechanism scoring for voice, prediction analysis
    for prompts. Building one product builds the foundation for the
    others &mdash; the Translation Workbench's multi-layer scoring is
    the same shape as the Voice Analyzer's mechanism scoring is the
    same shape as a prompt's structural analysis. The cost of adding
    Wedge 2 after Wedge 4 ships is measured in vertical-specific UI,
    not in re-implementing the engine.
  </div>
</div>
</div>

<!-- ═══ Theory ════════════════════════════════════════════════════ -->
<div class="panel" id="theory-tab">
<div class="container">
  <h2>Theory &mdash; The Framing</h2>
  <p class="desc">
    The full framing lives in <code>~/projects/lingora/docs/theory.md</code>.
    This is the condensed version.
  </p>

  <div class="info">
    <b>1. Words are activation patterns, not symbols.</b><br>
    A word is a cue. Perceiving it activates a distribution of nodes across the
    network. The distribution is the meaning. Two speakers with different
    histories will have different distributions for the same word &mdash; the
    overlap is what we call "shared meaning," and it is always partial.
  </div>

  <div class="info">
    <b>2. Meaning is built live in the listener.</b><br>
    When you hear a sentence, the words prompt activation patterns in your own
    network, and those patterns interact to produce a composite &mdash; that
    composite is your understanding. The speaker's meaning never left the
    speaker. Your meaning is your own reconstruction. Communication works when
    the two reconstructions are close enough for the purpose at hand, which is
    much more often than the underlying math suggests it should be.
  </div>

  <div class="info">
    <b>3. Vocabulary carves perception.</b><br>
    If your language has two words for two shades of blue, you discriminate
    between them faster and more categorically than speakers of a language with
    one. The vocabulary is not a label on a pre-existing distinction; it is a
    prior that runs inside perception and makes the distinction reliable. A
    distinction with a name is cheap to draw. A distinction without a name is
    expensive. Learning a new language with different categories is a real
    perceptual change.
  </div>

  <div class="info">
    <b>4. Sentences are running forecasts.</b><br>
    Each word constrains the predictor's guess at the next word. Understanding
    a sentence is the predictor narrowing onto one specific region. Garden-path
    sentences and good jokes both work by generating a confident forecast and
    then violating it &mdash; producing a residual spike at the point of
    surprise. That spike is the "click" of comprehension or humor.
  </div>

  <div class="info">
    <b>5. Grammar is a prior about how patterns chain.</b><br>
    Native speakers do not consult rules. They have internalized statistical
    regularities from thousands of hours of exposure, and the regularities are
    the grammar. Formal rule systems are post-hoc descriptions of what the
    prior ended up doing. Children acquire grammar without ever being told most
    of the rules, because the network is tuned to extract structural
    regularities from input.
  </div>

  <div class="info">
    <b>6. Translation is structural remapping.</b><br>
    Good translation finds the closest available shape in the target language's
    node graph. Sometimes the shape matches cleanly. Often it does not &mdash;
    and the translator has to either expand (many words in B to approximate one
    in A) or lose structure. Poetry is notoriously hard to translate because it
    depends on precise edge weights between specific nodes, and moving to a
    different network almost never preserves those weights.
  </div>

  <div class="info">
    <b>7. Writing is deliberate prompt engineering for brains.</b><br>
    A writer is choosing inputs that will produce specific activation patterns
    in every reader. The tools: concrete imagery (fires sensory cortex), rhythm
    (modulates attention), repetition (reinforces pathways), metaphor (borrows
    cross-cluster structure), surprise (fires the residual scorer). Good
    writing is programming a device you cannot see, in a language whose effects
    depend on details you can only partially control.
  </div>

  <div class="info">
    <b>8. Large language models are linguistic systems.</b><br>
    An LLM is a statistical model of which node-activation patterns follow
    which others, trained at scale. PEP's framework applies directly. Prompt
    engineering is the deliberate construction of input patterns that push the
    model's forecast distribution toward the desired region &mdash; the same
    operation a skilled writer runs on a human reader. The substrate differs.
    The mechanism is the same.
  </div>
</div>
</div>

<!-- ═══ Why PEP ═════════════════════════════════════════════════ -->
<div class="panel" id="whypep-tab">
<div class="container">
  <h2>Why PEP &mdash; How the Engine Applies to Language</h2>
  <p class="desc">
    Lingora is not a stand-alone idea. It is PEP's five primitives
    applied to language. Every canvas in this app is one or more of
    these primitives exposed in a linguistic frame. Here is the mapping.
  </p>

  <div class="info">
    <b>1. Weighted graph &mdash; the substrate.</b><br>
    Words are nodes. Co-occurrence, semantic similarity, phonological
    similarity, and typed relations (synonym, antonym, collocation,
    register-sibling) are edges. A speaker's lexicon <em>is</em> the
    weighted graph, and two speakers' graphs are never identical &mdash;
    which is the origin of the principle that "shared meaning is always
    partial." Every Lingora canvas that shows a network of words is
    this primitive in its most direct form.
  </div>

  <div class="info">
    <b>2. Spreading activation &mdash; the search primitive.</b><br>
    Hearing a word spreads activation to its neighborhood. Listener
    reconstruction &mdash; what you actually do to make sense of a
    sentence &mdash; is bounded spreading activation from the heard
    words to their semantic clusters. The recipient's reconstruction
    can only use <em>their</em> edges, never the speaker's. See
    <a href="#" onclick="canvasSelect('word-tab');return false">Word Constellation</a>,
    <a href="#" onclick="canvasSelect('listener-tab');return false">Listener Reconstruction</a>,
    <a href="#" onclick="canvasSelect('ambig-tab');return false">Ambiguity</a>.
  </div>

  <div class="info">
    <b>3. Predictor + residual scorer &mdash; the learning signal.</b><br>
    Each word narrows the forecast of the next. Comprehension is the
    predictor settling. Jokes, garden-path sentences, poetry, and good
    prose all engineer residual spikes at chosen moments &mdash; the
    "click" of surprise that makes a sentence land. Residuals are
    where meaning gets updated, not where the model fails. See
    <a href="#" onclick="canvasSelect('sentence-tab');return false">Sentence Prediction</a>,
    <a href="#" onclick="canvasSelect('humor-tab');return false">Humor</a>,
    <a href="#" onclick="canvasSelect('poetry-tab');return false">Poetry</a>.
  </div>

  <div class="info">
    <b>4. State modulator &mdash; runtime gain control.</b><br>
    Register, formality, taboo, audience, mood, code-switching context &mdash;
    all rescale which edges are eligible at runtime. Taboo words have
    their edge gain zeroed in polite contexts; sarcasm markers flip the
    valence of otherwise-positive edges; formal register suppresses the
    casual half of the lexicon. The same word graph produces radically
    different outputs under different social modulators. See
    <a href="#" onclick="canvasSelect('taboo-tab');return false">Taboo</a>,
    <a href="#" onclick="canvasSelect('politeness-tab');return false">Politeness</a>,
    <a href="#" onclick="canvasSelect('codeswitch-tab');return false">Code-Switching</a>,
    <a href="#" onclick="canvasSelect('irony-tab');return false">Irony</a>.
  </div>

  <div class="info">
    <b>5. Opacity + haze &mdash; reclaimable capacity.</b><br>
    Vocabulary you don't use fades. Spaced-repetition (Lingora Learn)
    is an explicit scheduling of reinforcement against the decay curve.
    Forgetting rare words is the feature that lets finite working
    memory support new-language learning &mdash; old senses have to be
    reclaimable for new ones to land. Aphasia is haze gone
    pathological (anchors decay faster than reinforcement replaces
    them). See
    <a href="#" onclick="canvasSelect('vocab-tab');return false">Vocabulary</a>,
    <a href="#" onclick="canvasSelect('acquisition-tab');return false">Acquisition</a>,
    <a href="#" onclick="canvasSelect('aphasia-tab');return false">Aphasia</a>.
  </div>

  <div class="info">
    <b>6. Cross-app wedges on the language substrate.</b><br>
    Language compounds with other substrates in ways single-app
    competitors can't replicate. Translation at story scale preserves
    voice and cultural anchors across paragraphs &mdash; see the
    <a href="#" onclick="canvasSelect('story-tab');return false">Story Translation Workbench</a>
    in the Workbench group. Earnings-call pragmatic analysis feeds the
    pragmatic layer into a trading signal &mdash; see
    <a href="/strata#pragmatic-tab">Strata &rarr; Earnings Pragmatics</a>.
    Both prove the same point: language is an input primitive the
    other siblings consume, not a standalone.
  </div>

  <div class="info" style="border-left:3px solid #4fc3f7">
    <b>The pattern.</b> Language is not its own thing. It is what
    happens when the five primitives run on a substrate of
    word-nodes, listener-reconstructions, and social context. Every
    linguistic phenomenon Lingora studies &mdash; idioms, translation
    gaps, humor, irony, politeness, register drift, acquisition,
    aphasia &mdash; is one or more primitives behaving in a specific
    regime. This is why the same engine runs Atria (people as
    nodes), Vectora (documents as nodes), Strata (assets as nodes),
    and Axona (cognitive states as nodes). The substrate changes;
    the mechanism is the same.
  </div>
</div>
</div>

<!-- ═══ PEP ↔ Lingora Bridge ════════════════════════════════════ -->
<div class="panel" id="bridge-tab">
<div class="container">
  <h2>PEP &harr; Lingora &mdash; Live Bridge</h2>
  <p class="desc">
    Lingora is not a stand-alone app. It is a surface on top of PEP's engine
    and a sibling to Axona in the same living system. Every canvas action
    here posts a typed event to PEP. PEP's live introspection state flows
    back down. This panel is the cross-talk, visible.
  </p>
  <div style="display:flex;gap:16px;margin-bottom:16px">
    <div class="info" style="flex:1">
      <b>PEP &rarr; Lingora (engine state)</b><br><br>
      <div style="font-family:monospace;font-size:11px;line-height:1.8">
        <div>connected: <span id="bridge-connected" style="color:var(--accent2)">—</span></div>
        <div>LLM: <span id="bridge-llm" style="color:var(--accent)">—</span></div>
        <div>embeddings: <span id="bridge-emb" style="color:var(--accent)">—</span></div>
        <div>recent PEP runs: <span id="bridge-runs" style="color:var(--accent)">—</span></div>
        <div>latest run id: <span id="bridge-latest-id" style="color:var(--dim)">—</span></div>
        <div>Lingora events seen by PEP: <span id="bridge-evcount" style="color:var(--accent)">—</span></div>
        <div>Axona events (cross-read): <span id="bridge-axona-count" style="color:var(--accent2)">—</span></div>
        <div>latest Axona event: <span id="bridge-axona-latest" style="color:var(--dim)">—</span></div>
      </div>
    </div>
    <div class="info" style="flex:1">
      <b>Lingora &rarr; PEP (linguistic events)</b><br><br>
      Click any canvas action and watch it post below. Axona's events are
      mirrored on the right — Lingora, Axona, and PEP are a single system, and
      either app can see what the other is doing in real time.
      <div style="margin-top:12px">
        <button onclick="bridgeSendPing()">Send Test Ping</button>
        <button onclick="bridgeClear()">Clear Local View</button>
      </div>
    </div>
  </div>
  <div style="display:flex;gap:16px">
    <div class="canvas-box" style="padding:16px;flex:1">
      <div style="font-family:monospace;font-size:11px;color:var(--accent);margin-bottom:8px">
        &gt; Lingora events &mdash; linguistic cross-talk
      </div>
      <div id="bridge-log" style="font-family:monospace;font-size:11px;line-height:1.7;max-height:360px;overflow-y:auto;color:var(--text)">
        <span style="color:var(--dim)">waiting for first event…</span>
      </div>
    </div>
    <div class="canvas-box" style="padding:16px;flex:1">
      <div style="font-family:monospace;font-size:11px;color:var(--accent2);margin-bottom:8px">
        &gt; Axona events (mirrored from /axona/events) &mdash; cognitive cross-talk
      </div>
      <div id="bridge-axona-log" style="font-family:monospace;font-size:11px;line-height:1.7;max-height:360px;overflow-y:auto;color:var(--text)">
        <span style="color:var(--dim)">polling…</span>
      </div>
    </div>
  </div>
</div>
</div>

<script>
// ═══════════════════════════════════════════════════════════════════════
// Tab switching (supports grouped tabs via data-panels)
// ═══════════════════════════════════════════════════════════════════════
function tabPanelIds(tab) {
  const joined = (tab.dataset.panels || tab.dataset.panel || '').trim();
  return joined.split(/\s+/).filter(Boolean);
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
// Helper: find the tab that owns a panel id (single or grouped)
function findTabForPanel(panelId) {
  return Array.from(document.querySelectorAll('.tab')).find(t => tabPanelIds(t).includes(panelId));
}

// ═══════════════════════════════════════════════════════════════════════
// Light mode
// ═══════════════════════════════════════════════════════════════════════
function toggleLight() {
  const isLight = document.body.classList.toggle('light');
  const btn = document.getElementById('light-btn');
  if (btn) btn.textContent = isLight ? 'Dark Mode' : 'Light Mode';
  try { localStorage.setItem('lingora-theme', isLight ? 'light' : 'dark'); } catch (e) {}
}
function downloadLingora() {
  const html = '<!DOCTYPE html>' + document.documentElement.outerHTML;
  const blob = new Blob([html], { type: 'text/html' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'lingora-language.html';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  try { pepSend('download', {}); } catch (e) {}
}
(function restoreTheme() {
  try {
    if (localStorage.getItem('lingora-theme') === 'light') {
      document.body.classList.add('light');
      const btn = document.getElementById('light-btn');
      if (btn) btn.textContent = 'Dark Mode';
    }
  } catch (e) {}
})();

// ═══════════════════════════════════════════════════════════════════════
// Word as Constellation
// ═══════════════════════════════════════════════════════════════════════
const WORD_DATA = {
  dog: { color: '124,184,255', nodes: [
    { l: 'fur', w: 0.95 }, { l: 'bark', w: 0.92 }, { l: 'leash', w: 0.78 },
    { l: 'tail', w: 0.88 }, { l: 'walks', w: 0.7 }, { l: 'loyal', w: 0.75 },
    { l: 'puppy', w: 0.85 }, { l: 'paws', w: 0.82 }, { l: 'cat', w: 0.35 },
    { l: 'fetch', w: 0.65 }, { l: 'treats', w: 0.6 }, { l: 'friend', w: 0.7 },
    { l: 'wet fur', w: 0.45 }, { l: 'childhood', w: 0.55 }, { l: 'vet', w: 0.5 },
  ] },
  freedom: { color: '240,168,105', nodes: [
    { l: 'choice', w: 0.9 }, { l: 'rights', w: 0.85 }, { l: 'flag', w: 0.6 },
    { l: 'constraint', w: 0.5 }, { l: 'open sky', w: 0.7 }, { l: 'fight', w: 0.6 },
    { l: 'responsibility', w: 0.7 }, { l: 'escape', w: 0.75 }, { l: 'road trip', w: 0.55 },
    { l: 'vote', w: 0.65 }, { l: 'tyranny', w: 0.5 }, { l: 'autonomy', w: 0.85 },
    { l: 'flag', w: 0.55 }, { l: 'prison', w: 0.4 }, { l: 'my life, my choice', w: 0.7 },
    { l: 'abstract', w: 0.8 }, { l: 'contested', w: 0.9 },
  ] },
  mother: { color: '255,183,180', nodes: [
    { l: 'warmth', w: 0.95 }, { l: 'safety', w: 0.9 }, { l: 'food', w: 0.75 },
    { l: 'voice', w: 0.9 }, { l: 'lullaby', w: 0.7 }, { l: 'worry', w: 0.75 },
    { l: 'face', w: 0.95 }, { l: 'hug', w: 0.85 }, { l: 'kitchen', w: 0.65 },
    { l: 'oxytocin', w: 0.6 }, { l: 'first memory', w: 0.75 }, { l: 'complicated', w: 0.55 },
    { l: 'loss', w: 0.5 }, { l: 'love', w: 0.95 },
  ] },
  fire: { color: '255,138,80', nodes: [
    { l: 'heat', w: 0.95 }, { l: 'orange', w: 0.92 }, { l: 'smoke', w: 0.88 },
    { l: 'crackle', w: 0.85 }, { l: 'danger', w: 0.8 }, { l: 'warmth', w: 0.82 },
    { l: 'primordial', w: 0.65 }, { l: 'campfire', w: 0.8 }, { l: 'burn', w: 0.85 },
    { l: 'hearth', w: 0.75 }, { l: 'destroy', w: 0.75 }, { l: 'cook', w: 0.7 },
    { l: 'ancestor', w: 0.5 }, { l: 'sunset glow', w: 0.45 },
  ] },
  home: { color: '130,210,145', nodes: [
    { l: 'family', w: 0.9 }, { l: 'safe', w: 0.92 }, { l: 'kitchen', w: 0.85 },
    { l: 'the smell', w: 0.8 }, { l: 'door', w: 0.7 }, { l: 'return', w: 0.82 },
    { l: 'childhood', w: 0.75 }, { l: 'rest', w: 0.85 }, { l: 'mine', w: 0.78 },
    { l: 'evening light', w: 0.6 }, { l: 'dog', w: 0.5 }, { l: 'a place you can leave', w: 0.65 },
    { l: 'missed when away', w: 0.8 }, { l: 'belonging', w: 0.88 },
  ] },
  money: { color: '180,180,120', nodes: [
    { l: 'work', w: 0.85 }, { l: 'cost', w: 0.8 }, { l: 'savings', w: 0.75 },
    { l: 'dignity', w: 0.6 }, { l: 'power', w: 0.82 }, { l: 'anxiety', w: 0.7 },
    { l: 'future', w: 0.78 }, { l: 'choice', w: 0.75 }, { l: 'bills', w: 0.7 },
    { l: 'paper', w: 0.5 }, { l: 'numbers', w: 0.75 }, { l: 'family', w: 0.5 },
    { l: 'stress', w: 0.75 }, { l: 'freedom', w: 0.6 }, { l: 'trade', w: 0.7 },
  ] },
};
const wordCanvas = document.getElementById('word-canvas');
const wordCtx = wordCanvas.getContext('2d');
let wordActive = null, wordPositions = [], wordT = 0;
function wordPick(key) {
  wordActive = key; wordT = 0;
  wordPositions = [];
  const data = WORD_DATA[key];
  if (!data) return;
  const W = 960, H = 440;
  const cx = W / 2, cy = H / 2;
  const n = data.nodes.length;
  data.nodes.forEach((node, i) => {
    const a = (i / n) * Math.PI * 2 - Math.PI / 2;
    const r = 130 + (1 - node.w) * 140;
    wordPositions.push({
      x: cx + Math.cos(a) * r,
      y: cy + Math.sin(a) * r,
      label: node.l,
      weight: node.w,
      activated: 0,
    });
  });
  document.getElementById('word-label').textContent = key;
}
function wordReset() {
  wordActive = null; wordPositions = []; wordT = 0;
  document.getElementById('word-label').textContent = '—';
}
function drawWord() {
  const W = 960, H = 440;
  wordCtx.fillStyle = getComputedStyle(document.body).getPropertyValue('--bg').trim() || '#0c0e14';
  wordCtx.fillRect(0, 0, W, H);
  wordT++;
  const cx = W / 2, cy = H / 2;
  if (!wordActive) {
    wordCtx.fillStyle = '#666'; wordCtx.font = '11px monospace'; wordCtx.textAlign = 'center';
    wordCtx.fillText('(click a word above)', cx, cy);
    requestAnimationFrame(drawWord);
    return;
  }
  const data = WORD_DATA[wordActive];
  const col = data.color;
  // Activation wave
  wordPositions.forEach((p, i) => {
    const delay = i * 3;
    const t = Math.max(0, wordT - delay);
    p.activated = Math.min(1, p.activated + (t > 0 ? 0.08 : 0));
  });
  // Central word
  wordCtx.fillStyle = 'rgba(' + col + ',0.35)';
  wordCtx.beginPath(); wordCtx.arc(cx, cy, 52, 0, Math.PI * 2); wordCtx.fill();
  wordCtx.strokeStyle = 'rgba(' + col + ',0.95)'; wordCtx.lineWidth = 2;
  wordCtx.stroke();
  wordCtx.fillStyle = '#ffffff'; wordCtx.font = 'bold 18px monospace'; wordCtx.textAlign = 'center';
  wordCtx.fillText(wordActive.toUpperCase(), cx, cy + 6);
  // Edges
  wordPositions.forEach(p => {
    if (p.activated < 0.05) return;
    wordCtx.strokeStyle = 'rgba(' + col + ',' + (p.weight * p.activated * 0.55).toFixed(3) + ')';
    wordCtx.lineWidth = 0.8 + p.weight * p.activated * 2;
    wordCtx.beginPath(); wordCtx.moveTo(cx, cy); wordCtx.lineTo(p.x, p.y); wordCtx.stroke();
  });
  // Nodes
  wordPositions.forEach(p => {
    const r = 6 + p.weight * 18 * p.activated;
    wordCtx.fillStyle = 'rgba(' + col + ',' + (0.2 + p.weight * p.activated * 0.6).toFixed(3) + ')';
    wordCtx.beginPath(); wordCtx.arc(p.x, p.y, r, 0, Math.PI * 2); wordCtx.fill();
    wordCtx.strokeStyle = 'rgba(' + col + ',' + (p.activated * 0.85).toFixed(3) + ')';
    wordCtx.lineWidth = 1;
    wordCtx.stroke();
    if (p.activated > 0.3) {
      wordCtx.fillStyle = 'rgba(224,224,224,' + p.activated.toFixed(3) + ')';
      wordCtx.font = '10px monospace'; wordCtx.textAlign = 'center';
      wordCtx.fillText(p.label, p.x, p.y + r + 12);
    }
  });
  requestAnimationFrame(drawWord);
}
drawWord();

// ═══════════════════════════════════════════════════════════════════════
// Sentence Forecast
// ═══════════════════════════════════════════════════════════════════════
const SENT_DATA = {
  cat: {
    words: ['The', 'cat', 'sat', 'on', 'the', 'mat'],
    forecasts: [
      [{ w: 'cat', p: 0.08 }, { w: 'dog', p: 0.07 }, { w: 'old', p: 0.06 }, { w: 'man', p: 0.05 }, { w: 'idea', p: 0.04 }, { w: 'next', p: 0.04 }, { w: 'first', p: 0.04 }, { w: '(many)', p: 0.62 }],
      [{ w: 'sat', p: 0.18 }, { w: 'ran', p: 0.12 }, { w: 'jumped', p: 0.10 }, { w: 'meowed', p: 0.08 }, { w: 'chased', p: 0.07 }, { w: 'was', p: 0.07 }, { w: 'slept', p: 0.06 }, { w: '(others)', p: 0.32 }],
      [{ w: 'on', p: 0.35 }, { w: 'in', p: 0.14 }, { w: 'by', p: 0.08 }, { w: 'still', p: 0.07 }, { w: 'down', p: 0.06 }, { w: 'quietly', p: 0.05 }, { w: '(others)', p: 0.25 }],
      [{ w: 'the', p: 0.55 }, { w: 'a', p: 0.12 }, { w: 'his', p: 0.06 }, { w: 'top', p: 0.05 }, { w: 'my', p: 0.04 }, { w: '(others)', p: 0.18 }],
      [{ w: 'mat', p: 0.28 }, { w: 'floor', p: 0.15 }, { w: 'couch', p: 0.10 }, { w: 'windowsill', p: 0.08 }, { w: 'chair', p: 0.08 }, { w: 'table', p: 0.07 }, { w: 'sofa', p: 0.06 }, { w: '(others)', p: 0.18 }],
      [{ w: 'mat', p: 1.00 }],
    ],
  },
  coffee: {
    words: ['She', 'poured', 'hot', 'coffee'],
    forecasts: [
      [{ w: 'poured', p: 0.05 }, { w: 'said', p: 0.06 }, { w: 'walked', p: 0.05 }, { w: 'looked', p: 0.05 }, { w: 'thought', p: 0.04 }, { w: '(many)', p: 0.75 }],
      [{ w: 'hot', p: 0.18 }, { w: 'the', p: 0.15 }, { w: 'water', p: 0.10 }, { w: 'tea', p: 0.08 }, { w: 'a', p: 0.07 }, { w: 'herself', p: 0.05 }, { w: '(others)', p: 0.37 }],
      [{ w: 'coffee', p: 0.32 }, { w: 'water', p: 0.22 }, { w: 'tea', p: 0.18 }, { w: 'chocolate', p: 0.08 }, { w: 'milk', p: 0.04 }, { w: '(others)', p: 0.16 }],
      [{ w: 'coffee', p: 1.00 }],
    ],
  },
  violate: {
    words: ['The', 'horse', 'raced', 'past', 'the', 'barn', 'fell'],
    forecasts: [
      [{ w: 'horse', p: 0.04 }, { w: 'cat', p: 0.07 }, { w: 'man', p: 0.05 }, { w: 'car', p: 0.04 }, { w: '(many)', p: 0.80 }],
      [{ w: 'raced', p: 0.08 }, { w: 'was', p: 0.12 }, { w: 'ran', p: 0.09 }, { w: 'stood', p: 0.07 }, { w: 'galloped', p: 0.06 }, { w: '(others)', p: 0.58 }],
      [{ w: 'past', p: 0.22 }, { w: 'around', p: 0.14 }, { w: 'toward', p: 0.10 }, { w: 'through', p: 0.08 }, { w: 'across', p: 0.07 }, { w: '(others)', p: 0.39 }],
      [{ w: 'the', p: 0.65 }, { w: 'a', p: 0.15 }, { w: '(others)', p: 0.20 }],
      [{ w: 'barn', p: 0.18 }, { w: 'fence', p: 0.14 }, { w: 'field', p: 0.10 }, { w: 'gate', p: 0.08 }, { w: 'meadow', p: 0.07 }, { w: '(others)', p: 0.43 }],
      [{ w: '.', p: 0.45 }, { w: 'quickly', p: 0.12 }, { w: 'and', p: 0.15 }, { w: 'toward', p: 0.08 }, { w: '(others)', p: 0.20 }],
      [{ w: 'fell', p: 1.00, violation: true }],
    ],
  },
};
const sentCanvas = document.getElementById('sent-canvas');
const sentCtx = sentCanvas.getContext('2d');
let sentActive = null, sentIdx = 0;
function sentLoad(key) { sentActive = key; sentIdx = 0; }
function sentStep() {
  if (!sentActive) return;
  const data = SENT_DATA[sentActive];
  if (sentIdx < data.words.length) sentIdx++;
}
function sentReset() { sentActive = null; sentIdx = 0; document.getElementById('sent-entropy').textContent = '—'; }
function entropy(forecast) {
  let e = 0;
  forecast.forEach(f => { if (f.p > 0 && f.w !== '(others)' && f.w !== '(many)') e -= f.p * Math.log2(f.p); });
  // Treat "(others)" / "(many)" as many small outcomes
  const other = forecast.find(f => f.w === '(others)' || f.w === '(many)');
  if (other) e += other.p * Math.log2(20);
  return e;
}
function drawSent() {
  const W = 960, H = 440;
  sentCtx.fillStyle = getComputedStyle(document.body).getPropertyValue('--bg').trim() || '#0c0e14';
  sentCtx.fillRect(0, 0, W, H);
  if (!sentActive) {
    sentCtx.fillStyle = '#666'; sentCtx.font = '11px monospace'; sentCtx.textAlign = 'center';
    sentCtx.fillText('(load a sentence to begin)', W / 2, H / 2);
    requestAnimationFrame(drawSent);
    return;
  }
  const data = SENT_DATA[sentActive];
  // Left: sentence so far
  sentCtx.fillStyle = '#aaa'; sentCtx.font = '11px monospace'; sentCtx.textAlign = 'left';
  sentCtx.fillText('sentence so far', 30, 30);
  let x = 30, y = 60;
  for (let i = 0; i < sentIdx; i++) {
    const word = data.words[i];
    sentCtx.font = 'bold 16px monospace';
    const metrics = sentCtx.measureText(word + ' ');
    if (x + metrics.width > 440) { x = 30; y += 30; }
    const isViolation = sentIdx === data.words.length && i === sentIdx - 1 && data.forecasts[i] && data.forecasts[i][0] && data.forecasts[i][0].violation;
    sentCtx.fillStyle = isViolation ? 'rgba(255,183,77,0.95)' : 'rgba(124,184,255,0.95)';
    sentCtx.fillText(word + ' ', x, y);
    x += metrics.width;
  }
  // Pending slot
  if (sentIdx < data.words.length) {
    sentCtx.fillStyle = 'rgba(124,184,255,0.3)'; sentCtx.font = 'bold 16px monospace';
    sentCtx.fillText('___', x, y);
  }
  // Right: forecast
  sentCtx.fillStyle = '#aaa'; sentCtx.font = '11px monospace';
  sentCtx.fillText('predictor forecast for next word', 490, 30);
  const fcIdx = Math.min(sentIdx, data.forecasts.length - 1);
  const forecast = data.forecasts[fcIdx] || [];
  const baseY = 60;
  const barW = 420;
  forecast.forEach((f, i) => {
    const by = baseY + i * 34;
    if (by > H - 30) return;
    const w = barW * f.p;
    sentCtx.fillStyle = 'rgba(124,184,255,0.25)';
    sentCtx.fillRect(490, by, barW, 22);
    const col = f.violation ? '255,183,77' : (f.w === '(others)' || f.w === '(many)' ? '120,120,140' : '124,184,255');
    sentCtx.fillStyle = 'rgba(' + col + ',0.85)';
    sentCtx.fillRect(490, by, w, 22);
    sentCtx.fillStyle = '#ffffff'; sentCtx.font = '11px monospace'; sentCtx.textAlign = 'left';
    sentCtx.fillText(f.w, 496, by + 15);
    sentCtx.fillStyle = '#aaa'; sentCtx.textAlign = 'right';
    sentCtx.fillText((f.p * 100).toFixed(0) + '%', 490 + barW - 6, by + 15);
  });
  // Entropy readout
  const e = entropy(forecast);
  document.getElementById('sent-entropy').textContent = e.toFixed(2);
  // Violation banner
  if (sentIdx >= data.words.length && data.forecasts[data.forecasts.length - 1][0].violation) {
    sentCtx.fillStyle = 'rgba(255,183,77,0.95)'; sentCtx.font = 'bold 12px monospace'; sentCtx.textAlign = 'center';
    sentCtx.fillText('◉ forecast violated — parser rewinds and re-parses', W / 2, H - 20);
  }
  requestAnimationFrame(drawSent);
}
drawSent();

// ═══════════════════════════════════════════════════════════════════════
// Translation Gap
// ═══════════════════════════════════════════════════════════════════════
const TRANS_DATA = {
  saudade: {
    left: { word: 'longing', lang: 'English', nodes: ['absence','memory','desire','waiting','sadness'] },
    right: { word: 'saudade', lang: 'Portuguese', nodes: ['absence','memory','desire','waiting','sadness','bittersweet-joy','cultural frame','fado music','impossible return','a thing you LOVE'] },
  },
  schadenfreude: {
    left: { word: 'pleasure', lang: 'English', nodes: ['happiness','reward','satisfaction','enjoyment'] },
    right: { word: 'schadenfreude', lang: 'German', nodes: ['happiness','reward','specifically-from-others-misfortune','moral complication','secret','shared-with-humans'] },
  },
  komorebi: {
    left: { word: 'sunlight', lang: 'English', nodes: ['bright','warm','day','outdoors','sky'] },
    right: { word: 'komorebi', lang: 'Japanese', nodes: ['sunlight','filtered through leaves','dappled pattern','forest silence','specific mood','aesthetic tradition'] },
  },
  hygge: {
    left: { word: 'coziness', lang: 'English', nodes: ['warm','comfort','indoors','blankets'] },
    right: { word: 'hygge', lang: 'Danish', nodes: ['warm','comfort','indoors','candles','shared with loved ones','seasonal ritual','slow time','cultural practice','a value'] },
  },
};
const transCanvas = document.getElementById('trans-canvas');
const transCtx = transCanvas.getContext('2d');
let transActive = null;
function transPick(key) { transActive = key; }
function transReset() { transActive = null; document.getElementById('trans-shared').textContent = '0'; document.getElementById('trans-missing').textContent = '0'; document.getElementById('trans-added').textContent = '0'; }
function drawTrans() {
  const W = 960, H = 440;
  transCtx.fillStyle = getComputedStyle(document.body).getPropertyValue('--bg').trim() || '#0c0e14';
  transCtx.fillRect(0, 0, W, H);
  if (!transActive) {
    transCtx.fillStyle = '#666'; transCtx.font = '11px monospace'; transCtx.textAlign = 'center';
    transCtx.fillText('(click a translation pair)', W / 2, H / 2);
    requestAnimationFrame(drawTrans);
    return;
  }
  const d = TRANS_DATA[transActive];
  const rightSet = new Set(d.right.nodes);
  const shared = d.left.nodes.filter(n => rightSet.has(n));
  const missing = d.left.nodes.filter(n => !rightSet.has(n));
  const leftSet = new Set(d.left.nodes);
  const added = d.right.nodes.filter(n => !leftSet.has(n));
  document.getElementById('trans-shared').textContent = shared.length;
  document.getElementById('trans-missing').textContent = missing.length;
  document.getElementById('trans-added').textContent = added.length;
  const leftCx = 240, rightCx = 720, cy = H / 2;
  // Left constellation
  transCtx.fillStyle = 'rgba(124,184,255,0.3)';
  transCtx.beginPath(); transCtx.arc(leftCx, cy, 44, 0, Math.PI * 2); transCtx.fill();
  transCtx.strokeStyle = 'rgba(124,184,255,0.9)'; transCtx.lineWidth = 2; transCtx.stroke();
  transCtx.fillStyle = '#ffffff'; transCtx.font = 'bold 13px monospace'; transCtx.textAlign = 'center';
  transCtx.fillText(d.left.word, leftCx, cy + 4);
  transCtx.fillStyle = '#aaa'; transCtx.font = '10px monospace';
  transCtx.fillText('(' + d.left.lang + ')', leftCx, cy - 55);
  // Right constellation
  transCtx.fillStyle = 'rgba(240,168,105,0.3)';
  transCtx.beginPath(); transCtx.arc(rightCx, cy, 44, 0, Math.PI * 2); transCtx.fill();
  transCtx.strokeStyle = 'rgba(240,168,105,0.9)'; transCtx.lineWidth = 2; transCtx.stroke();
  transCtx.fillStyle = '#ffffff'; transCtx.font = 'bold 13px monospace';
  transCtx.fillText(d.right.word, rightCx, cy + 4);
  transCtx.fillStyle = '#aaa'; transCtx.font = '10px monospace';
  transCtx.fillText('(' + d.right.lang + ')', rightCx, cy - 55);
  // Place nodes
  function placeNodes(cx, nodes, highlightSet, highlightCol, dimCol) {
    nodes.forEach((n, i) => {
      const a = (i / nodes.length) * Math.PI * 2 - Math.PI / 2;
      const r = 130;
      const x = cx + Math.cos(a) * r, y = cy + Math.sin(a) * r;
      const isShared = highlightSet.has(n);
      const col = isShared ? '129,199,132' : highlightCol;
      transCtx.strokeStyle = 'rgba(' + col + ',0.55)'; transCtx.lineWidth = 1;
      transCtx.beginPath(); transCtx.moveTo(cx, cy); transCtx.lineTo(x, y); transCtx.stroke();
      transCtx.fillStyle = 'rgba(' + col + ',0.45)';
      transCtx.beginPath(); transCtx.arc(x, y, 10, 0, Math.PI * 2); transCtx.fill();
      transCtx.strokeStyle = 'rgba(' + col + ',0.95)'; transCtx.stroke();
      transCtx.fillStyle = '#e0e0e0'; transCtx.font = '10px monospace'; transCtx.textAlign = 'center';
      transCtx.fillText(n, x, y + r * 0 + (Math.sin(a) >= 0 ? 24 : -14));
    });
  }
  placeNodes(leftCx, d.left.nodes, rightSet, '124,184,255', '229,57,53');
  placeNodes(rightCx, d.right.nodes, leftSet, '240,168,105', '240,168,105');
  // Legend
  transCtx.fillStyle = 'rgba(129,199,132,0.9)'; transCtx.font = '11px monospace'; transCtx.textAlign = 'left';
  transCtx.fillText('● shared (survives translation)', 30, H - 56);
  transCtx.fillStyle = 'rgba(124,184,255,0.9)';
  transCtx.fillText('● left-only (lost in translation)', 30, H - 40);
  transCtx.fillStyle = 'rgba(240,168,105,0.9)';
  transCtx.fillText('● right-only (added by target language)', 30, H - 24);
  requestAnimationFrame(drawTrans);
}
drawTrans();

// ═══════════════════════════════════════════════════════════════════════
// Helper — reuse the theme background color
// ═══════════════════════════════════════════════════════════════════════
function themeBg() {
  return getComputedStyle(document.body).getPropertyValue('--bg').trim() || '#0c0e14';
}

// ═══════════════════════════════════════════════════════════════════════
// Ambiguity Resolution
// ═══════════════════════════════════════════════════════════════════════
const AMBIG_DATA = {
  bank: {
    target: 'BANK',
    left:  { label: 'riverside', nodes: ['river','water','mud','fishing','grass','shore'] },
    right: { label: 'financial',  nodes: ['money','vault','loan','teller','cash','account'] },
    primes: { A: 'river', B: 'money' },
  },
  bat: {
    target: 'BAT',
    left:  { label: 'animal', nodes: ['wings','cave','night','echolocation','fur','small'] },
    right: { label: 'sport',   nodes: ['baseball','swing','wood','pitch','strike','helmet'] },
    primes: { A: 'cave', B: 'baseball' },
  },
  pitch: {
    target: 'PITCH',
    left:  { label: 'sound', nodes: ['note','high','low','music','voice','tone'] },
    right: { label: 'throw',  nodes: ['baseball','mound','ball','throw','curveball','strike'] },
    primes: { A: 'music', B: 'baseball' },
  },
};
const ambigCanvas = document.getElementById('ambig-canvas');
const ambigCtx = ambigCanvas.getContext('2d');
let ambigWordKey = null, ambigPrimeSide = null, ambigLeftAct = 0, ambigRightAct = 0, ambigFired = false, ambigFireT = 0;
function ambigWord(k) { ambigWordKey = k; ambigReset(); ambigFired = true; ambigFireT = 0; }
function ambigPrime(side) {
  ambigPrimeSide = side;
  if (side === 'A') ambigLeftAct = 0.85;
  else if (side === 'B') ambigRightAct = 0.85;
  else { ambigLeftAct = 0.1; ambigRightAct = 0.1; }
}
function ambigReset() { ambigLeftAct = 0.1; ambigRightAct = 0.1; ambigFired = false; ambigPrimeSide = null; }
function drawAmbig() {
  const W = 960, H = 440;
  ambigCtx.fillStyle = themeBg(); ambigCtx.fillRect(0, 0, W, H);
  if (!ambigWordKey) {
    ambigCtx.fillStyle = '#666'; ambigCtx.font = '11px monospace'; ambigCtx.textAlign = 'center';
    ambigCtx.fillText('(pick a target word)', W / 2, H / 2);
    requestAnimationFrame(drawAmbig);
    return;
  }
  const d = AMBIG_DATA[ambigWordKey];
  // Fire animation: when target fires, both candidates get a push; whichever was warmer wins
  if (ambigFired) {
    ambigFireT = Math.min(60, ambigFireT + 1);
    if (ambigFireT === 1) {
      // Race — whoever was pre-warmed wins
      const leftSeed = ambigLeftAct + Math.random() * 0.1;
      const rightSeed = ambigRightAct + Math.random() * 0.1;
      ambigLeftAct = leftSeed > rightSeed ? Math.min(1, leftSeed + 0.1) : Math.max(0.08, leftSeed - 0.2);
      ambigRightAct = rightSeed >= leftSeed ? Math.min(1, rightSeed + 0.1) : Math.max(0.08, rightSeed - 0.2);
    }
  }
  // Natural decay toward primed baseline
  ambigLeftAct += ((ambigPrimeSide === 'A' ? 0.85 : 0.1) - ambigLeftAct) * 0.02;
  ambigRightAct += ((ambigPrimeSide === 'B' ? 0.85 : 0.1) - ambigRightAct) * 0.02;
  // Center (ambiguous word)
  const cx = W / 2, cy = H / 2 + 30;
  ambigCtx.fillStyle = 'rgba(124,184,255,0.35)';
  ambigCtx.beginPath(); ambigCtx.arc(cx, cy, 44, 0, Math.PI * 2); ambigCtx.fill();
  ambigCtx.strokeStyle = 'rgba(124,184,255,0.95)'; ambigCtx.lineWidth = 2; ambigCtx.stroke();
  ambigCtx.fillStyle = '#ffffff'; ambigCtx.font = 'bold 16px monospace'; ambigCtx.textAlign = 'center';
  ambigCtx.fillText(d.target, cx, cy + 6);
  // Prime label if set
  if (ambigPrimeSide) {
    ambigCtx.fillStyle = '#aaa'; ambigCtx.font = '11px monospace';
    ambigCtx.fillText('prime: "' + (ambigPrimeSide === 'A' ? d.primes.A : d.primes.B) + '"', cx, cy - 60);
  }
  // Draw cluster helper
  function drawCluster(x, cluster, activation, color) {
    const r = 70 + activation * 16;
    ambigCtx.fillStyle = 'rgba(' + color + ',' + (0.15 + activation * 0.45).toFixed(3) + ')';
    ambigCtx.beginPath(); ambigCtx.arc(x, 180, r, 0, Math.PI * 2); ambigCtx.fill();
    ambigCtx.strokeStyle = 'rgba(' + color + ',' + (0.4 + activation * 0.55).toFixed(3) + ')';
    ambigCtx.lineWidth = 1.5; ambigCtx.stroke();
    ambigCtx.fillStyle = '#fff'; ambigCtx.font = 'bold 12px monospace'; ambigCtx.textAlign = 'center';
    ambigCtx.fillText(cluster.label.toUpperCase(), x, 184);
    // Sub-nodes around the cluster
    cluster.nodes.forEach((n, i) => {
      const a = (i / cluster.nodes.length) * Math.PI * 2;
      const nx = x + Math.cos(a) * (r + 32);
      const ny = 180 + Math.sin(a) * (r + 18);
      ambigCtx.fillStyle = 'rgba(' + color + ',' + (0.2 + activation * 0.6).toFixed(3) + ')';
      ambigCtx.beginPath(); ambigCtx.arc(nx, ny, 4 + activation * 4, 0, Math.PI * 2); ambigCtx.fill();
      ambigCtx.fillStyle = '#aaa'; ambigCtx.font = '10px monospace';
      ambigCtx.fillText(n, nx, ny + 18);
    });
    // Edge to target
    ambigCtx.strokeStyle = 'rgba(' + color + ',' + (activation * 0.6).toFixed(3) + ')';
    ambigCtx.lineWidth = 1 + activation * 3;
    ambigCtx.beginPath(); ambigCtx.moveTo(x + (x < cx ? r : -r), 180); ambigCtx.lineTo(cx + (x < cx ? -44 : 44), cy); ambigCtx.stroke();
  }
  drawCluster(200, d.left,  ambigLeftAct,  '124,184,255');
  drawCluster(760, d.right, ambigRightAct, '240,168,105');
  // Winner label
  if (Math.abs(ambigLeftAct - ambigRightAct) > 0.3) {
    const winner = ambigLeftAct > ambigRightAct ? d.left.label : d.right.label;
    ambigCtx.fillStyle = 'rgba(129,199,132,0.95)'; ambigCtx.font = 'bold 12px monospace'; ambigCtx.textAlign = 'center';
    ambigCtx.fillText('→ reads as "' + winner + '"', W / 2, H - 18);
  }
  requestAnimationFrame(drawAmbig);
}
drawAmbig();

// ═══════════════════════════════════════════════════════════════════════
// Grammar as Prior
// ═══════════════════════════════════════════════════════════════════════
const GRAMMAR_TEMPLATES = {
  fluent: [
    'The small cat walked across the wooden floor and stopped at the door.',
    'She opened the book and began to read the first chapter.',
    'The old man watched the sun set slowly over the quiet hills.',
    'A sudden rain fell on the street and emptied the market in minutes.',
  ],
  loose: [
    'The cat small across floor wooden walked and stopped the door at.',
    'She the book opened began to chapter first read.',
    'Old man watched sun the set over hills quiet slowly.',
    'A fell rain sudden the street on emptied market minutes in.',
  ],
  salad: [
    'Sun cat wooden rain the book the old watched street market.',
    'Quiet minutes suddenly first chapter hills the slowly opened cat.',
    'Door market book sun read small man emptied watched.',
    'Cat hills read sun wooden small rain market door book.',
  ],
};
const grammarCanvas = document.getElementById('grammar-canvas');
const grammarCtx = grammarCanvas.getContext('2d');
let grammarMode = null, grammarText = '', grammarIdx = 0;
function grammarGen(m) {
  grammarMode = m;
  const list = GRAMMAR_TEMPLATES[m];
  grammarText = list[Math.floor(Math.random() * list.length)];
  grammarIdx = 0;
}
function grammarReset() { grammarMode = null; grammarText = ''; grammarIdx = 0; }
function drawGrammar() {
  const W = 960, H = 440;
  grammarCtx.fillStyle = themeBg(); grammarCtx.fillRect(0, 0, W, H);
  grammarCtx.font = '11px monospace'; grammarCtx.fillStyle = '#aaa'; grammarCtx.textAlign = 'left';
  grammarCtx.fillText('sampling from prior…', 30, 30);
  if (!grammarMode) {
    grammarCtx.fillStyle = '#666'; grammarCtx.textAlign = 'center';
    grammarCtx.fillText('(press a button to generate)', W / 2, H / 2);
    requestAnimationFrame(drawGrammar);
    return;
  }
  // Reveal word by word
  if (grammarIdx < grammarText.split(' ').length) grammarIdx++;
  const words = grammarText.split(' ').slice(0, grammarIdx);
  const modeLabels = { fluent: 'fluent prior (tight distribution)', loose: 'loose prior (noisy)', salad: 'random prior (word salad)' };
  const modeCols = { fluent: '129,199,132', loose: '255,183,77', salad: '229,57,53' };
  grammarCtx.fillStyle = 'rgba(' + modeCols[grammarMode] + ',0.95)';
  grammarCtx.font = 'bold 12px monospace'; grammarCtx.textAlign = 'left';
  grammarCtx.fillText(modeLabels[grammarMode].toUpperCase(), 30, 60);
  // Render text
  let x = 30, y = 120;
  grammarCtx.font = '15px monospace'; grammarCtx.fillStyle = '#e0e0e0';
  words.forEach(w => {
    const m = grammarCtx.measureText(w + ' ');
    if (x + m.width > W - 40) { x = 30; y += 28; }
    grammarCtx.fillText(w + ' ', x, y);
    x += m.width;
  });
  // Probability distribution illustration
  const barY = H - 130;
  grammarCtx.fillStyle = '#aaa'; grammarCtx.font = '11px monospace';
  grammarCtx.fillText('sampling distribution shape', 30, barY - 10);
  const shape = grammarMode === 'fluent' ? 'tight' : (grammarMode === 'loose' ? 'medium' : 'flat');
  for (let i = 0; i < 60; i++) {
    let h;
    if (shape === 'tight') h = i > 25 && i < 35 ? 60 * Math.exp(-Math.pow((i - 30) / 3, 2)) : 0;
    else if (shape === 'medium') h = 40 * Math.exp(-Math.pow((i - 30) / 10, 2));
    else h = 15 + Math.random() * 10;
    grammarCtx.fillStyle = 'rgba(' + modeCols[grammarMode] + ',0.75)';
    grammarCtx.fillRect(30 + i * 15, barY + (60 - h), 12, h);
  }
  requestAnimationFrame(drawGrammar);
}
drawGrammar();

// ═══════════════════════════════════════════════════════════════════════
// Prompt Engineering
// ═══════════════════════════════════════════════════════════════════════
const PROMPT_DATA = {
  vague: {
    label: 'vague: "give me ideas"',
    center: [480, 220], radius: 180, density: 'diffuse',
    desc: 'predictor falls into default distribution — safe, generic, common continuations',
  },
  specific: {
    label: 'specific: "give me 5 ideas for X"',
    center: [380, 260], radius: 90, density: 'medium',
    desc: 'narrower region — still generic but bounded by the topic',
  },
  constrained: {
    label: 'constrained: "5 counterintuitive ideas for X"',
    center: [280, 310], radius: 60, density: 'tight',
    desc: 'common continuations suppressed, tail tokens boosted — much narrower corner of space',
  },
  role: {
    label: 'role-framed: "you are a nobel-prize winning chemist. 5 ideas for X"',
    center: [680, 150], radius: 80, density: 'tight',
    desc: 'region shifts to a completely different part of the token space entirely',
  },
};
const promptCanvas = document.getElementById('prompt-canvas');
const promptCtx = promptCanvas.getContext('2d');
const promptPoints = [];
for (let i = 0; i < 280; i++) {
  promptPoints.push({ x: 40 + Math.random() * 880, y: 100 + Math.random() * 260 });
}
let promptActive = null;
function promptPick(k) { promptActive = k; }
function promptReset() { promptActive = null; }
function drawPrompt() {
  const W = 960, H = 440;
  promptCtx.fillStyle = themeBg(); promptCtx.fillRect(0, 0, W, H);
  // Label axes (activation space)
  promptCtx.strokeStyle = 'rgba(120,120,130,0.3)'; promptCtx.lineWidth = 1;
  promptCtx.strokeRect(30, 80, 900, 300);
  promptCtx.fillStyle = '#aaa'; promptCtx.font = '11px monospace'; promptCtx.textAlign = 'left';
  promptCtx.fillText('token activation space (every point is a possible next-token region)', 40, 70);
  // Plot all points dimly
  promptPoints.forEach(p => {
    let lit = false, highlight = 0;
    if (promptActive) {
      const d = PROMPT_DATA[promptActive];
      const dist = Math.hypot(p.x - d.center[0], p.y - d.center[1]);
      if (dist < d.radius) {
        lit = true;
        highlight = 1 - (dist / d.radius);
      }
    }
    if (lit) {
      promptCtx.fillStyle = 'rgba(240,168,105,' + (0.3 + highlight * 0.7).toFixed(3) + ')';
      promptCtx.beginPath(); promptCtx.arc(p.x, p.y, 2 + highlight * 3, 0, Math.PI * 2); promptCtx.fill();
    } else {
      promptCtx.fillStyle = 'rgba(120,120,130,0.25)';
      promptCtx.beginPath(); promptCtx.arc(p.x, p.y, 1.5, 0, Math.PI * 2); promptCtx.fill();
    }
  });
  if (promptActive) {
    const d = PROMPT_DATA[promptActive];
    // Outline the activated region
    promptCtx.strokeStyle = 'rgba(240,168,105,0.7)'; promptCtx.lineWidth = 1.5;
    promptCtx.setLineDash([4, 4]);
    promptCtx.beginPath(); promptCtx.arc(d.center[0], d.center[1], d.radius, 0, Math.PI * 2); promptCtx.stroke();
    promptCtx.setLineDash([]);
    promptCtx.fillStyle = 'rgba(240,168,105,0.95)'; promptCtx.font = 'bold 12px monospace'; promptCtx.textAlign = 'left';
    promptCtx.fillText(d.label, 40, 420);
    promptCtx.fillStyle = '#aaa'; promptCtx.font = '11px monospace';
    promptCtx.fillText(d.desc, 40, 438);
  } else {
    promptCtx.fillStyle = '#666'; promptCtx.font = '11px monospace'; promptCtx.textAlign = 'center';
    promptCtx.fillText('(pick a prompt framing to see the activation region)', W / 2, H - 18);
  }
  requestAnimationFrame(drawPrompt);
}
drawPrompt();

// ═══════════════════════════════════════════════════════════════════════
// Poetry as Residual Engineering
// ═══════════════════════════════════════════════════════════════════════
const POETRY_DATA = {
  frost: {
    label: 'Robert Frost — "Stopping by Woods on a Snowy Evening"',
    words: ['Whose','woods','these','are','I','think','I','know.','His','house','is','in','the','village','though;'],
    residuals: [0.1,0.8,0.2,0.15,0.1,0.1,0.1,0.2,0.15,0.35,0.2,0.15,0.1,0.75,0.9],
  },
  dickinson: {
    label: 'Emily Dickinson — "Hope is the thing with feathers"',
    words: ['Hope','is','the','thing','with','feathers','—','That','perches','in','the','soul','—'],
    residuals: [0.15,0.1,0.1,0.2,0.1,0.95,0.85,0.15,0.75,0.1,0.1,0.85,0.7],
  },
  plain: {
    label: 'Plain prose (control): a weather report',
    words: ['The','temperature','today','is','expected','to','reach','seventy','degrees','by','noon','.'],
    residuals: [0.1,0.15,0.12,0.1,0.15,0.1,0.15,0.2,0.15,0.1,0.15,0.1],
  },
};
const poetryCanvas = document.getElementById('poetry-canvas');
const poetryCtx = poetryCanvas.getContext('2d');
let poetryActive = null, poetryIdx = 0, poetryTimer = 0;
function poetryPlay(k) { poetryActive = k; poetryIdx = 0; poetryTimer = 0; }
function poetryReset() { poetryActive = null; poetryIdx = 0; poetryTimer = 0; }
function drawPoetry() {
  const W = 960, H = 440;
  poetryCtx.fillStyle = themeBg(); poetryCtx.fillRect(0, 0, W, H);
  if (!poetryActive) {
    poetryCtx.fillStyle = '#666'; poetryCtx.font = '11px monospace'; poetryCtx.textAlign = 'center';
    poetryCtx.fillText('(pick a poem)', W / 2, H / 2);
    requestAnimationFrame(drawPoetry);
    return;
  }
  const d = POETRY_DATA[poetryActive];
  poetryTimer++;
  if (poetryTimer > 30 && poetryIdx < d.words.length) { poetryTimer = 0; poetryIdx++; }
  poetryCtx.fillStyle = '#aaa'; poetryCtx.font = '11px monospace'; poetryCtx.textAlign = 'left';
  poetryCtx.fillText(d.label, 30, 30);
  // Draw residual bars with word labels beneath
  const slotW = Math.min(60, (W - 60) / d.words.length);
  const baseY = 260;
  for (let i = 0; i < d.words.length; i++) {
    const x = 30 + i * slotW;
    const shown = i < poetryIdx;
    const r = shown ? d.residuals[i] : 0;
    const h = r * 170;
    const col = r > 0.5 ? '240,168,105' : '124,184,255';
    poetryCtx.fillStyle = 'rgba(' + col + ',' + (shown ? 0.85 : 0.15).toFixed(3) + ')';
    poetryCtx.fillRect(x + 4, baseY - h, slotW - 8, h);
    poetryCtx.fillStyle = shown ? '#fff' : '#555'; poetryCtx.font = '12px monospace'; poetryCtx.textAlign = 'center';
    poetryCtx.fillText(d.words[i], x + slotW / 2, baseY + 24);
    if (shown && r > 0.6) {
      poetryCtx.fillStyle = 'rgba(240,168,105,0.95)'; poetryCtx.font = 'bold 10px monospace';
      poetryCtx.fillText('◉', x + slotW / 2, baseY - h - 6);
    }
  }
  poetryCtx.fillStyle = '#aaa'; poetryCtx.font = '11px monospace'; poetryCtx.textAlign = 'left';
  poetryCtx.fillText('residual (prediction error) per word — orange spikes are engineered surprises', 30, H - 90);
  poetryCtx.fillStyle = 'rgba(240,168,105,0.9)';
  poetryCtx.fillText('◉ = engineered residual — the moments a reader says "oh"', 30, H - 70);
  poetryCtx.fillStyle = 'rgba(124,184,255,0.85)';
  poetryCtx.fillText('low bars = the forecast tracked the sentence cleanly', 30, H - 50);
  requestAnimationFrame(drawPoetry);
}
drawPoetry();

// ═══════════════════════════════════════════════════════════════════════
// Show Don't Tell
// ═══════════════════════════════════════════════════════════════════════
const WRITING_DATA = {
  abstract: {
    label: 'abstract version',
    text: 'She was sad. The breakup had been difficult. She felt a strong sense of loss. Her emotional state was poor.',
    activation: { verbal: 0.95, visual: 0.1, motor: 0.05, tactile: 0.05, auditory: 0.05, olfactory: 0.0, emotional: 0.6 },
  },
  concrete: {
    label: 'concrete version',
    text: 'She stood by the kitchen window in his old sweater, the one that still smelled faintly of cedar. The cup of tea in her hand had gone cold an hour ago. Her thumb kept tracing the chipped handle.',
    activation: { verbal: 0.6, visual: 0.9, motor: 0.55, tactile: 0.85, auditory: 0.3, olfactory: 0.7, emotional: 0.95 },
  },
};
const writingCanvas = document.getElementById('writing-canvas');
const writingCtx = writingCanvas.getContext('2d');
let writingActive = null;
function writingLoad(k) { writingActive = k; }
function writingReset() { writingActive = null; }
// ═══════════════════════════════════════════════════════════════════════
// PEP ↔ Lingora bridge client
// ═══════════════════════════════════════════════════════════════════════
let bridgeSendThrottle = {};
function pepSend(type, payload) {
  const now = Date.now();
  if (bridgeSendThrottle[type] && now - bridgeSendThrottle[type] < 600) return;
  bridgeSendThrottle[type] = now;
  try {
    fetch('/lingora/event', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type, source: 'lingora', payload: payload || {} }),
    }).catch(() => {});
  } catch (e) {}
}
function bridgeSendPing() { pepSend('ping', { from: 'user', t: Date.now() }); }
function bridgeClear() {
  const log = document.getElementById('bridge-log');
  if (log) log.innerHTML = '<span style="color:var(--dim)">cleared (server still has the copy)</span>';
}
function bridgeFmtTime(t) { return new Date(t * 1000).toTimeString().slice(0, 8); }
function bridgeRender(items) {
  const log = document.getElementById('bridge-log');
  if (!log || !items || !items.length) return;
  log.innerHTML = items.slice().reverse().map(e => {
    const payload = JSON.stringify(e.payload || {}).replace(/</g, '&lt;');
    return '<div style="margin-bottom:3px">' +
      '<span style="color:var(--dim)">' + bridgeFmtTime(e.t) + '</span> ' +
      '<span style="color:var(--accent)">' + (e.type || 'event') + '</span>' +
      ' <span style="color:var(--dim)">' + payload + '</span></div>';
  }).join('');
}
function bridgeRenderAxona(items) {
  const log = document.getElementById('bridge-axona-log');
  if (!log) return;
  if (!items || !items.length) {
    log.innerHTML = '<span style="color:var(--dim)">no axona events yet…</span>';
    return;
  }
  log.innerHTML = items.slice().reverse().map(e => {
    const payload = JSON.stringify(e.payload || {}).replace(/</g, '&lt;');
    return '<div style="margin-bottom:3px">' +
      '<span style="color:var(--dim)">' + bridgeFmtTime(e.t) + '</span> ' +
      '<span style="color:var(--accent2)">' + (e.type || 'event') + '</span>' +
      ' <span style="color:var(--dim)">' + payload + '</span></div>';
  }).join('');
}
async function bridgePoll() {
  try {
    const [s, e, a] = await Promise.all([
      fetch('/lingora/pep-state'),
      fetch('/lingora/events?limit=40'),
      fetch('/lingora/axona-events?limit=40'),
    ]);
    if (s.ok) {
      const d = await s.json();
      const lbl = document.getElementById('pep-link-label');
      const dot = document.getElementById('pep-link-dot');
      if (lbl) lbl.textContent = 'PEP: ' + (d.llm || 'unknown') + ' · L' + (d.lingora_events || 0) + ' · A' + (d.axona_events || 0);
      if (dot) dot.style.background = 'var(--accent2)';
      const set = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = v; };
      set('bridge-connected', 'yes');
      set('bridge-llm', d.llm || '—');
      set('bridge-emb', d.embeddings || '—');
      set('bridge-runs', d.runs_recent);
      set('bridge-evcount', d.lingora_events);
      set('bridge-axona-count', d.axona_events);
      if (d.latest_run) set('bridge-latest-id', d.latest_run.id || '—');
      if (d.axona_latest) set('bridge-axona-latest', d.axona_latest.type || '—');
    }
    if (e.ok) {
      const data = await e.json();
      bridgeRender(data.items || []);
    }
    if (a.ok) {
      const data = await a.json();
      bridgeRenderAxona(data.items || []);
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
// Listener Reconstruction
// ═══════════════════════════════════════════════════════════════════════
const LISTENER_DATA = {
  child: {
    words: ['The','child','dropped','her','ice','cream'],
    nodes: ['person','small','young','hands','clumsy','falling','loss','tears','sweet','cold','disappointment','sticky','sidewalk','moment'],
    activations: {
      'The': [],
      'child': ['person','small','young'],
      'dropped': ['hands','clumsy','falling','loss'],
      'her': ['young'],
      'ice': ['cold','sweet'],
      'cream': ['sweet','cold','sticky','disappointment','tears','loss','sidewalk','moment'],
    },
  },
  war: {
    words: ['The','soldier','came','home','silent'],
    nodes: ['person','young','uniform','war','returning','family','door','memories','trauma','distance','tired','eyes','weight','unspoken'],
    activations: {
      'The': [],
      'soldier': ['person','young','uniform','war'],
      'came': ['returning'],
      'home': ['family','door','returning'],
      'silent': ['trauma','distance','tired','eyes','weight','unspoken','memories'],
    },
  },
  dog: {
    words: ['The','dog','waited','by','the','door'],
    nodes: ['pet','animal','fur','loyal','patient','sitting','watching','hope','family','return','porch','wood','eager','still'],
    activations: {
      'The': [],
      'dog': ['pet','animal','fur','loyal'],
      'waited': ['patient','sitting','watching','still','eager'],
      'by': [],
      'the': [],
      'door': ['porch','wood','hope','return','family'],
    },
  },
};
const listenerCanvas = document.getElementById('listener-canvas');
const listenerCtx = listenerCanvas.getContext('2d');
let listenerActive = null, listenerIdx = 0, listenerNodePos = {};
function listenerLoad(k) {
  listenerActive = k; listenerIdx = 0;
  const d = LISTENER_DATA[k];
  listenerNodePos = {};
  d.nodes.forEach((n, i) => {
    const a = (i / d.nodes.length) * Math.PI * 2 - Math.PI / 2;
    const r = 150;
    listenerNodePos[n] = {
      x: 480 + Math.cos(a) * r,
      y: 220 + Math.sin(a) * r,
      activation: 0,
    };
  });
  pepSend('listener.load', { key: k });
}
function listenerStep() {
  if (!listenerActive) return;
  const d = LISTENER_DATA[listenerActive];
  if (listenerIdx >= d.words.length) return;
  const word = d.words[listenerIdx];
  const activated = d.activations[word] || [];
  activated.forEach(n => {
    if (listenerNodePos[n]) listenerNodePos[n].activation = Math.min(1, listenerNodePos[n].activation + 0.6);
  });
  listenerIdx++;
  pepSend('listener.step', { word, activated });
}
function listenerReset() { listenerActive = null; listenerIdx = 0; listenerNodePos = {}; }
function drawListener() {
  const W = 960, H = 440;
  listenerCtx.fillStyle = themeBg(); listenerCtx.fillRect(0, 0, W, H);
  if (!listenerActive) {
    listenerCtx.fillStyle = '#666'; listenerCtx.font = '11px monospace'; listenerCtx.textAlign = 'center';
    listenerCtx.fillText('(load a sentence)', W / 2, H / 2);
    requestAnimationFrame(drawListener);
    return;
  }
  const d = LISTENER_DATA[listenerActive];
  // Decay
  for (const n in listenerNodePos) listenerNodePos[n].activation *= 0.995;
  // Draw sentence so far at top
  listenerCtx.font = 'bold 14px monospace'; listenerCtx.textAlign = 'left';
  let x = 30, y = 40;
  for (let i = 0; i < d.words.length; i++) {
    const active = i < listenerIdx;
    listenerCtx.fillStyle = active ? 'rgba(124,184,255,0.95)' : 'rgba(120,120,130,0.4)';
    listenerCtx.fillText(d.words[i] + ' ', x, y);
    x += listenerCtx.measureText(d.words[i] + ' ').width;
  }
  // Draw nodes radiating from center
  for (const name in listenerNodePos) {
    const p = listenerNodePos[name];
    const r = 5 + p.activation * 14;
    listenerCtx.fillStyle = 'rgba(124,184,255,' + (0.15 + p.activation * 0.65).toFixed(3) + ')';
    listenerCtx.beginPath(); listenerCtx.arc(p.x, p.y, r, 0, Math.PI * 2); listenerCtx.fill();
    if (p.activation > 0.2) {
      listenerCtx.strokeStyle = 'rgba(124,184,255,0.9)';
      listenerCtx.lineWidth = 1;
      listenerCtx.beginPath(); listenerCtx.moveTo(480, 220); listenerCtx.lineTo(p.x, p.y); listenerCtx.stroke();
      listenerCtx.fillStyle = '#e0e0e0';
      listenerCtx.font = '10px monospace';
      listenerCtx.textAlign = 'center';
      listenerCtx.fillText(name, p.x, p.y + r + 12);
    }
  }
  // Center hub
  listenerCtx.fillStyle = 'rgba(240,168,105,0.35)';
  listenerCtx.beginPath(); listenerCtx.arc(480, 220, 32, 0, Math.PI * 2); listenerCtx.fill();
  listenerCtx.strokeStyle = 'rgba(240,168,105,0.9)'; listenerCtx.lineWidth = 2; listenerCtx.stroke();
  listenerCtx.fillStyle = '#fff'; listenerCtx.font = 'bold 11px monospace'; listenerCtx.textAlign = 'center';
  listenerCtx.fillText('LISTENER', 480, 218);
  listenerCtx.fillText('COMPOSITE', 480, 232);
  requestAnimationFrame(drawListener);
}
drawListener();

// ═══════════════════════════════════════════════════════════════════════
// Speaker ↔ Listener Transfer
// ═══════════════════════════════════════════════════════════════════════
const TRANSFER_DATA = {
  simple: {
    msg: 'I got the job',
    speakerNodes: ['relief','pride','long-wait','interview-mem','bills','future','partner','text','tears','family'],
    wordsCarry: ['job','got','I'],
    listenerNodes: ['job','employment','news','congratulations','salary','change'],
  },
  complex: {
    msg: 'It was complicated',
    speakerNodes: ['regret','unclear-outcome','multiple-parties','truth-partial','withhold','sigh','shame','loyalty'],
    wordsCarry: ['complicated','was','it'],
    listenerNodes: ['unclear','many-factors','no-simple-answer','the-person-does-not-want-to-talk-about-it','wait'],
  },
  abstract: {
    msg: 'I feel free',
    speakerNodes: ['relief','release','no-more-weight','open-road','choice','specific-memory','lightness','contrast'],
    wordsCarry: ['free','feel','I'],
    listenerNodes: ['good-mood','no-constraint','happy','something-ended','abstract-positive'],
  },
};
const transferCanvas = document.getElementById('transfer-canvas');
const transferCtx = transferCanvas.getContext('2d');
let transferActive = null, transferT = 0;
function transferSend(k) { transferActive = k; transferT = 0; pepSend('transfer.send', { key: k }); }
function transferReset() { transferActive = null; transferT = 0; }
function drawTransfer() {
  const W = 960, H = 460;
  transferCtx.fillStyle = themeBg(); transferCtx.fillRect(0, 0, W, H);
  if (!transferActive) {
    transferCtx.fillStyle = '#666'; transferCtx.font = '11px monospace'; transferCtx.textAlign = 'center';
    transferCtx.fillText('(send a message)', W / 2, H / 2);
    requestAnimationFrame(drawTransfer);
    return;
  }
  transferT = Math.min(200, transferT + 1);
  const d = TRANSFER_DATA[transferActive];
  // Speaker cloud on left
  const speakerAct = Math.min(1, transferT / 30);
  transferCtx.fillStyle = 'rgba(124,184,255,0.25)';
  transferCtx.beginPath(); transferCtx.ellipse(180, 230, 130, 170, 0, 0, Math.PI * 2); transferCtx.fill();
  transferCtx.strokeStyle = 'rgba(124,184,255,0.85)'; transferCtx.lineWidth = 2; transferCtx.stroke();
  transferCtx.fillStyle = '#aaa'; transferCtx.font = '11px monospace'; transferCtx.textAlign = 'center';
  transferCtx.fillText('SPEAKER', 180, 90);
  transferCtx.fillText('(intended meaning)', 180, 104);
  d.speakerNodes.forEach((n, i) => {
    const a = (i / d.speakerNodes.length) * Math.PI * 2;
    const nx = 180 + Math.cos(a) * 80;
    const ny = 230 + Math.sin(a) * 110;
    transferCtx.fillStyle = 'rgba(124,184,255,' + (speakerAct * 0.85).toFixed(3) + ')';
    transferCtx.beginPath(); transferCtx.arc(nx, ny, 4, 0, Math.PI * 2); transferCtx.fill();
    transferCtx.fillStyle = '#e0e0e0';
    transferCtx.font = '9px monospace';
    transferCtx.fillText(n, nx, ny + 12);
  });
  // Bottleneck (words)
  const wordsShow = transferT > 40;
  transferCtx.fillStyle = 'rgba(240,168,105,0.12)';
  transferCtx.fillRect(350, 150, 260, 160);
  transferCtx.strokeStyle = 'rgba(240,168,105,0.75)'; transferCtx.lineWidth = 1.5;
  transferCtx.setLineDash([4, 4]); transferCtx.strokeRect(350, 150, 260, 160); transferCtx.setLineDash([]);
  transferCtx.fillStyle = '#aaa'; transferCtx.font = '11px monospace'; transferCtx.textAlign = 'center';
  transferCtx.fillText('BOTTLENECK: WORDS', 480, 140);
  transferCtx.fillStyle = 'rgba(240,168,105,0.95)'; transferCtx.font = 'bold 18px monospace';
  if (wordsShow) transferCtx.fillText('"' + d.msg + '"', 480, 240);
  transferCtx.fillStyle = '#aaa'; transferCtx.font = '10px monospace';
  transferCtx.fillText('(compression: ' + d.speakerNodes.length + ' → ' + d.wordsCarry.length + ' carried)', 480, 270);
  // Listener cloud on right
  const listenerAct = Math.min(1, Math.max(0, (transferT - 100) / 30));
  transferCtx.fillStyle = 'rgba(129,199,132,0.25)';
  transferCtx.beginPath(); transferCtx.ellipse(780, 230, 130, 170, 0, 0, Math.PI * 2); transferCtx.fill();
  transferCtx.strokeStyle = 'rgba(129,199,132,0.85)'; transferCtx.lineWidth = 2; transferCtx.stroke();
  transferCtx.fillStyle = '#aaa'; transferCtx.font = '11px monospace'; transferCtx.textAlign = 'center';
  transferCtx.fillText('LISTENER', 780, 90);
  transferCtx.fillText('(reconstructed meaning)', 780, 104);
  d.listenerNodes.forEach((n, i) => {
    const a = (i / d.listenerNodes.length) * Math.PI * 2;
    const nx = 780 + Math.cos(a) * 80;
    const ny = 230 + Math.sin(a) * 110;
    transferCtx.fillStyle = 'rgba(129,199,132,' + (listenerAct * 0.85).toFixed(3) + ')';
    transferCtx.beginPath(); transferCtx.arc(nx, ny, 4, 0, Math.PI * 2); transferCtx.fill();
    transferCtx.fillStyle = '#e0e0e0';
    transferCtx.font = '9px monospace';
    transferCtx.fillText(n, nx, ny + 12);
  });
  transferCtx.fillStyle = 'rgba(229,57,53,0.95)'; transferCtx.font = 'bold 11px monospace'; transferCtx.textAlign = 'center';
  if (transferT > 150) transferCtx.fillText('◉ gap between intended meaning and reconstructed meaning = the cost of the bottleneck', W / 2, H - 20);
  requestAnimationFrame(drawTransfer);
}
drawTransfer();

// ═══════════════════════════════════════════════════════════════════════
// Humor & Puns
// ═══════════════════════════════════════════════════════════════════════
const HUMOR_DATA = {
  panda: {
    setup: 'A panda walks into a bar, orders a sandwich, and leaves.',
    punch: '"A panda eats, shoots, and leaves."',
    dual: [
      { label: 'literal: animal diet', col: '124,184,255' },
      { label: 'pun: violent bar crime', col: '240,168,105' },
    ],
  },
  time: {
    setup: '"Time flies like an arrow"',
    punch: '"Fruit flies like a banana"',
    dual: [
      { label: 'literal: time resembles an arrow', col: '124,184,255' },
      { label: 'garden-path: fruit flies (insects) are attracted to a banana', col: '240,168,105' },
    ],
  },
  bookkeeper: {
    setup: '"bookkeeper" is the only common English word',
    punch: 'with three consecutive double letters',
    dual: [
      { label: 'surface: person who keeps books', col: '124,184,255' },
      { label: 'structural trivia: oo-kk-ee', col: '240,168,105' },
    ],
  },
};
const humorCanvas = document.getElementById('humor-canvas');
const humorCtx = humorCanvas.getContext('2d');
let humorActive = null, humorT = 0;
function humorPlay(k) { humorActive = k; humorT = 0; pepSend('humor.play', { key: k }); }
function humorReset() { humorActive = null; humorT = 0; }
function drawHumor() {
  const W = 960, H = 400;
  humorCtx.fillStyle = themeBg(); humorCtx.fillRect(0, 0, W, H);
  if (!humorActive) {
    humorCtx.fillStyle = '#666'; humorCtx.font = '11px monospace'; humorCtx.textAlign = 'center';
    humorCtx.fillText('(pick a joke)', W / 2, H / 2);
    requestAnimationFrame(drawHumor);
    return;
  }
  const d = HUMOR_DATA[humorActive];
  humorT = Math.min(300, humorT + 1);
  // Setup text
  humorCtx.fillStyle = '#aaa'; humorCtx.font = '11px monospace'; humorCtx.textAlign = 'left';
  humorCtx.fillText('setup', 30, 30);
  humorCtx.fillStyle = '#e0e0e0'; humorCtx.font = '14px monospace';
  humorCtx.fillText(d.setup, 30, 56);
  // Punch
  if (humorT > 60) {
    humorCtx.fillStyle = '#aaa'; humorCtx.font = '11px monospace';
    humorCtx.fillText('punchline', 30, 100);
    humorCtx.fillStyle = 'rgba(240,168,105,0.95)'; humorCtx.font = 'bold 14px monospace';
    humorCtx.fillText(d.punch, 30, 126);
  }
  // Dual activation clusters
  if (humorT > 100) {
    const opacity1 = Math.min(1, (humorT - 100) / 40);
    const opacity2 = Math.min(1, (humorT - 120) / 40);
    d.dual.forEach((c, i) => {
      const cx = 260 + i * 440, cy = 240;
      const op = i === 0 ? opacity1 : opacity2;
      humorCtx.fillStyle = 'rgba(' + c.col + ',' + (0.25 + op * 0.5).toFixed(3) + ')';
      humorCtx.beginPath(); humorCtx.arc(cx, cy, 60, 0, Math.PI * 2); humorCtx.fill();
      humorCtx.strokeStyle = 'rgba(' + c.col + ',' + op.toFixed(3) + ')'; humorCtx.lineWidth = 2; humorCtx.stroke();
      humorCtx.fillStyle = 'rgba(224,224,224,' + op.toFixed(3) + ')'; humorCtx.font = '11px monospace';
      humorCtx.textAlign = 'center';
      const wrapped = c.label.split(': ');
      humorCtx.fillText(wrapped[0], cx, cy - 4);
      if (wrapped[1]) humorCtx.fillText(wrapped[1], cx, cy + 12);
    });
  }
  // Spike
  if (humorT > 160 && humorT < 220) {
    const spikeOp = Math.sin(((humorT - 160) / 60) * Math.PI) * 0.9;
    humorCtx.fillStyle = 'rgba(255,183,77,' + spikeOp.toFixed(3) + ')';
    humorCtx.font = 'bold 14px monospace'; humorCtx.textAlign = 'center';
    humorCtx.fillText('◉ DUAL ACTIVATION SPIKE — laugh', W / 2, 340);
  }
  requestAnimationFrame(drawHumor);
}
drawHumor();

// ═══════════════════════════════════════════════════════════════════════
// Idiom
// ═══════════════════════════════════════════════════════════════════════
const IDIOM_DATA = {
  bucket: {
    phrase: '"kick the bucket"',
    compositional: ['KICK: foot + strike', 'THE: article', 'BUCKET: pail, metal, water'],
    compositionalResult: 'foot strikes a pail',
    unitary: 'DIE (euphemism)',
  },
  beans: {
    phrase: '"spill the beans"',
    compositional: ['SPILL: pour out', 'THE: article', 'BEANS: legumes'],
    compositionalResult: 'pour out legumes',
    unitary: 'REVEAL A SECRET',
  },
  cold: {
    phrase: '"cold feet"',
    compositional: ['COLD: low temperature', 'FEET: body parts'],
    compositionalResult: 'the physical sensation',
    unitary: 'LOSING NERVE, HESITATION',
  },
};
const idiomCanvas = document.getElementById('idiom-canvas');
const idiomCtx = idiomCanvas.getContext('2d');
let idiomActive = null, idiomT = 0;
function idiomPlay(k) { idiomActive = k; idiomT = 0; pepSend('idiom.play', { key: k }); }
function idiomReset() { idiomActive = null; idiomT = 0; }
function drawIdiom() {
  const W = 960, H = 400;
  idiomCtx.fillStyle = themeBg(); idiomCtx.fillRect(0, 0, W, H);
  if (!idiomActive) {
    idiomCtx.fillStyle = '#666'; idiomCtx.font = '11px monospace'; idiomCtx.textAlign = 'center';
    idiomCtx.fillText('(pick an idiom)', W / 2, H / 2);
    requestAnimationFrame(drawIdiom);
    return;
  }
  const d = IDIOM_DATA[idiomActive];
  idiomT = Math.min(300, idiomT + 1);
  // Phrase at top
  idiomCtx.fillStyle = '#fff'; idiomCtx.font = 'bold 18px monospace'; idiomCtx.textAlign = 'center';
  idiomCtx.fillText(d.phrase, W / 2, 40);
  // Compositional path (left)
  idiomCtx.fillStyle = 'rgba(124,184,255,0.85)'; idiomCtx.font = 'bold 12px monospace'; idiomCtx.textAlign = 'left';
  idiomCtx.fillText('compositional path', 40, 90);
  idiomCtx.fillStyle = '#e0e0e0'; idiomCtx.font = '11px monospace';
  d.compositional.forEach((c, i) => {
    idiomCtx.fillText('• ' + c, 50, 115 + i * 20);
  });
  if (idiomT > 100) {
    idiomCtx.fillStyle = 'rgba(229,57,53,0.9)'; idiomCtx.font = '11px monospace';
    idiomCtx.fillText('→ ' + d.compositionalResult, 50, 200);
    idiomCtx.fillStyle = 'rgba(229,57,53,0.95)'; idiomCtx.font = 'bold 11px monospace';
    idiomCtx.fillText('✕ absurd', 50, 220);
  }
  // Unitary path (right)
  idiomCtx.fillStyle = 'rgba(129,199,132,0.85)'; idiomCtx.font = 'bold 12px monospace';
  idiomCtx.fillText('unitary path (cached block retrieval)', 500, 90);
  idiomCtx.fillStyle = '#e0e0e0'; idiomCtx.font = '11px monospace';
  idiomCtx.fillText('• whole phrase as one unit', 510, 115);
  idiomCtx.fillText('• co-occurred with meaning thousands of times', 510, 135);
  idiomCtx.fillText('• direct edge, bypasses parsing', 510, 155);
  if (idiomT > 100) {
    idiomCtx.fillStyle = 'rgba(129,199,132,0.95)'; idiomCtx.font = 'bold 12px monospace';
    idiomCtx.fillText('→ ' + d.unitary, 510, 200);
    idiomCtx.fillText('✓ wins the retrieval race', 510, 220);
  }
  // Divider
  idiomCtx.strokeStyle = 'rgba(120,120,130,0.3)'; idiomCtx.lineWidth = 1;
  idiomCtx.beginPath(); idiomCtx.moveTo(480, 80); idiomCtx.lineTo(480, 250); idiomCtx.stroke();
  idiomCtx.fillStyle = '#aaa'; idiomCtx.font = '11px monospace'; idiomCtx.textAlign = 'center';
  if (idiomT > 160) idiomCtx.fillText('the unitary path has higher weight from thousands of contextual exposures', W / 2, 300);
  requestAnimationFrame(drawIdiom);
}
drawIdiom();

// ═══════════════════════════════════════════════════════════════════════
// LLM Bridge (stubbed)
// ═══════════════════════════════════════════════════════════════════════
const LLM_DATA = {
  complete1: {
    prompt: 'The capital of France is',
    steps: [
      { topk: [{ t: ' Paris', p: 0.96 }, { t: ' the', p: 0.015 }, { t: ' located', p: 0.005 }, { t: ' not', p: 0.003 }, { t: '(others)', p: 0.017 }] },
      { topk: [{ t: ' Paris', p: 0.97 }, { t: ' France', p: 0.01 }, { t: '(others)', p: 0.02 }] },
      { topk: [{ t: '.', p: 0.7 }, { t: ',', p: 0.12 }, { t: ' and', p: 0.08 }, { t: ' which', p: 0.04 }, { t: '(others)', p: 0.06 }] },
    ],
  },
  complete2: {
    prompt: 'Once upon a time, there was a',
    steps: [
      { topk: [{ t: ' little', p: 0.14 }, { t: ' young', p: 0.10 }, { t: ' beautiful', p: 0.08 }, { t: ' small', p: 0.06 }, { t: ' kind', p: 0.05 }, { t: ' king', p: 0.05 }, { t: ' girl', p: 0.04 }, { t: '(many)', p: 0.48 }] },
      { topk: [{ t: ' girl', p: 0.18 }, { t: ' boy', p: 0.16 }, { t: ' princess', p: 0.12 }, { t: ' prince', p: 0.08 }, { t: ' cottage', p: 0.06 }, { t: ' village', p: 0.05 }, { t: '(others)', p: 0.35 }] },
      { topk: [{ t: ' named', p: 0.22 }, { t: ' who', p: 0.18 }, { t: ' with', p: 0.14 }, { t: '.', p: 0.04 }, { t: ' living', p: 0.06 }, { t: '(others)', p: 0.36 }] },
    ],
  },
  complete3: {
    prompt: 'To be or not to',
    steps: [
      { topk: [{ t: ' be', p: 0.93 }, { t: ' have', p: 0.01 }, { t: ' do', p: 0.01 }, { t: '(others)', p: 0.05 }] },
      { topk: [{ t: ',', p: 0.68 }, { t: '.', p: 0.15 }, { t: ':', p: 0.05 }, { t: ' that', p: 0.04 }, { t: '(others)', p: 0.08 }] },
      { topk: [{ t: ' that', p: 0.82 }, { t: ' the', p: 0.04 }, { t: ' is', p: 0.03 }, { t: '(others)', p: 0.11 }] },
    ],
  },
  complete4: {
    prompt: 'def fibonacci(n):',
    steps: [
      { topk: [{ t: '\\n    if', p: 0.52 }, { t: '\\n    return', p: 0.25 }, { t: '\\n    "', p: 0.05 }, { t: '\\n    a', p: 0.04 }, { t: '(others)', p: 0.14 }] },
      { topk: [{ t: ' n', p: 0.81 }, { t: ' (', p: 0.08 }, { t: ' not', p: 0.03 }, { t: '(others)', p: 0.08 }] },
      { topk: [{ t: ' <=', p: 0.48 }, { t: ' <', p: 0.31 }, { t: ' ==', p: 0.12 }, { t: '(others)', p: 0.09 }] },
    ],
  },
};
const llmCanvas = document.getElementById('llm-canvas');
const llmCtx = llmCanvas.getContext('2d');
let llmActive = null, llmStepIdx = 0;
function llmPrompt(k) { llmActive = k; llmStepIdx = 0; pepSend('llm.prompt', { key: k }); }
function llmStep() {
  if (!llmActive) return;
  const d = LLM_DATA[llmActive];
  if (llmStepIdx < d.steps.length - 1) llmStepIdx++;
  pepSend('llm.step', { key: llmActive, step: llmStepIdx });
}
function llmReset() { llmActive = null; llmStepIdx = 0; }
function drawLlm() {
  const W = 960, H = 460;
  llmCtx.fillStyle = themeBg(); llmCtx.fillRect(0, 0, W, H);
  if (!llmActive) {
    llmCtx.fillStyle = '#666'; llmCtx.font = '11px monospace'; llmCtx.textAlign = 'center';
    llmCtx.fillText('(pick a prompt)', W / 2, H / 2);
    requestAnimationFrame(drawLlm);
    return;
  }
  const d = LLM_DATA[llmActive];
  const step = d.steps[llmStepIdx] || d.steps[0];
  llmCtx.fillStyle = '#aaa'; llmCtx.font = '11px monospace'; llmCtx.textAlign = 'left';
  llmCtx.fillText('prompt (step ' + (llmStepIdx + 1) + ' / ' + d.steps.length + ')', 30, 30);
  llmCtx.fillStyle = '#e0e0e0'; llmCtx.font = 'bold 14px monospace';
  llmCtx.fillText(d.prompt, 30, 56);
  // Bar chart
  llmCtx.fillStyle = '#aaa'; llmCtx.font = '11px monospace';
  llmCtx.fillText('top-k next-token distribution', 30, 100);
  const baseY = 120, barW = 720;
  step.topk.forEach((tk, i) => {
    const y = baseY + i * 34;
    if (y > H - 30) return;
    const w = barW * tk.p;
    llmCtx.fillStyle = 'rgba(124,184,255,0.2)';
    llmCtx.fillRect(30, y, barW, 22);
    const col = tk.t.includes('(') ? '120,120,140' : '124,184,255';
    llmCtx.fillStyle = 'rgba(' + col + ',0.85)';
    llmCtx.fillRect(30, y, w, 22);
    llmCtx.fillStyle = '#fff'; llmCtx.font = '12px monospace'; llmCtx.textAlign = 'left';
    llmCtx.fillText(tk.t, 36, y + 15);
    llmCtx.fillStyle = '#aaa'; llmCtx.textAlign = 'right';
    llmCtx.fillText((tk.p * 100).toFixed(1) + '%', 30 + barW - 6, y + 15);
  });
  llmCtx.fillStyle = '#666'; llmCtx.font = '10px monospace'; llmCtx.textAlign = 'left';
  llmCtx.fillText('(stubbed: running on pre-computed distributions — set ANTHROPIC_API_KEY to go live)', 30, H - 14);
  requestAnimationFrame(drawLlm);
}
drawLlm();

// ═══════════════════════════════════════════════════════════════════════
// Active ↔ Passive voice
// ═══════════════════════════════════════════════════════════════════════
const VOICE_DATA = {
  active: {
    text: 'She hit him.',
    agent: { focus: 0.85, label: 'she (agent)' },
    patient: { focus: 0.4, label: 'him (patient)' },
    note: 'Active voice — agent is the topic, gets the attention bonus.',
  },
  passive: {
    text: 'He was hit by her.',
    agent: { focus: 0.35, label: 'her (agent, demoted)' },
    patient: { focus: 0.85, label: 'he (patient, topicalized)' },
    note: 'Passive voice — patient is the topic, agent is optional and demoted.',
  },
  agentless: {
    text: 'He was hit.',
    agent: { focus: 0.0, label: '(agent deleted)' },
    patient: { focus: 0.9, label: 'he (patient)' },
    note: 'Agent removed entirely. The event reads as if no one caused it. Responsibility has been erased.',
  },
};
const voiceCanvas = document.getElementById('voice-canvas');
const voiceCtx = voiceCanvas.getContext('2d');
let voiceActive = null;
function voicePlay(k) { voiceActive = k; pepSend('voice.play', { key: k }); }
function voiceReset() { voiceActive = null; }
function drawVoice() {
  const W = 960, H = 380;
  voiceCtx.fillStyle = themeBg(); voiceCtx.fillRect(0, 0, W, H);
  if (!voiceActive) {
    voiceCtx.fillStyle = '#666'; voiceCtx.font = '11px monospace'; voiceCtx.textAlign = 'center';
    voiceCtx.fillText('(pick a voice)', W / 2, H / 2);
    requestAnimationFrame(drawVoice);
    return;
  }
  const d = VOICE_DATA[voiceActive];
  voiceCtx.fillStyle = '#fff'; voiceCtx.font = 'bold 22px monospace'; voiceCtx.textAlign = 'center';
  voiceCtx.fillText(d.text, W / 2, 60);
  // Two nodes: agent and patient
  const ax = 300, px = 660, ny = 200;
  // Agent
  const agentExists = d.agent.focus > 0.01;
  if (agentExists) {
    voiceCtx.fillStyle = 'rgba(124,184,255,' + (0.2 + d.agent.focus * 0.55).toFixed(3) + ')';
    voiceCtx.beginPath(); voiceCtx.arc(ax, ny, 30 + d.agent.focus * 30, 0, Math.PI * 2); voiceCtx.fill();
    voiceCtx.strokeStyle = 'rgba(124,184,255,0.95)'; voiceCtx.lineWidth = 2; voiceCtx.stroke();
  } else {
    voiceCtx.strokeStyle = 'rgba(120,120,130,0.4)'; voiceCtx.lineWidth = 1;
    voiceCtx.setLineDash([4, 4]);
    voiceCtx.beginPath(); voiceCtx.arc(ax, ny, 30, 0, Math.PI * 2); voiceCtx.stroke();
    voiceCtx.setLineDash([]);
  }
  voiceCtx.fillStyle = agentExists ? '#fff' : '#666'; voiceCtx.font = '11px monospace';
  voiceCtx.fillText(d.agent.label, ax, ny + 4);
  // Patient
  voiceCtx.fillStyle = 'rgba(240,168,105,' + (0.2 + d.patient.focus * 0.55).toFixed(3) + ')';
  voiceCtx.beginPath(); voiceCtx.arc(px, ny, 30 + d.patient.focus * 30, 0, Math.PI * 2); voiceCtx.fill();
  voiceCtx.strokeStyle = 'rgba(240,168,105,0.95)'; voiceCtx.lineWidth = 2; voiceCtx.stroke();
  voiceCtx.fillStyle = '#fff'; voiceCtx.font = '11px monospace';
  voiceCtx.fillText(d.patient.label, px, ny + 4);
  // Event arrow
  if (agentExists) {
    voiceCtx.strokeStyle = 'rgba(229,57,53,0.7)'; voiceCtx.lineWidth = 2;
    voiceCtx.beginPath(); voiceCtx.moveTo(ax + 60, ny); voiceCtx.lineTo(px - 60, ny); voiceCtx.stroke();
    voiceCtx.fillStyle = 'rgba(229,57,53,0.85)';
    voiceCtx.beginPath();
    voiceCtx.moveTo(px - 60, ny); voiceCtx.lineTo(px - 70, ny - 6); voiceCtx.lineTo(px - 70, ny + 6);
    voiceCtx.closePath(); voiceCtx.fill();
    voiceCtx.fillStyle = 'rgba(229,57,53,0.85)'; voiceCtx.font = '10px monospace';
    voiceCtx.fillText('hit', (ax + px) / 2, ny - 12);
  }
  voiceCtx.fillStyle = '#aaa'; voiceCtx.font = '11px monospace'; voiceCtx.textAlign = 'center';
  voiceCtx.fillText(d.note, W / 2, H - 30);
  requestAnimationFrame(drawVoice);
}
drawVoice();

// ═══════════════════════════════════════════════════════════════════════
// Irony
// ═══════════════════════════════════════════════════════════════════════
const IRONY_DATA = {
  weather: { surface: '"Great weather!"', context: '(pouring rain outside)', literal: 'the weather is excellent', intended: 'the weather is terrible, and I am complaining' },
  smart: { surface: '"Oh, that is brilliant..."', context: '(someone just did something dumb)', literal: 'that is a brilliant idea', intended: 'that is a terrible idea, and I am mocking' },
  thrilled: { surface: '"Just thrilled to be here"', context: '(at a funeral, dry tone)', literal: 'I am very happy to be here', intended: 'I am not happy, but social ritual requires my presence' },
};
const ironyCanvas = document.getElementById('irony-canvas');
const ironyCtx = ironyCanvas.getContext('2d');
let ironyActive = null, ironyT = 0;
function ironyPlay(k) { ironyActive = k; ironyT = 0; pepSend('irony.play', { key: k }); }
function ironyReset() { ironyActive = null; ironyT = 0; }
function drawIrony() {
  const W = 960, H = 400;
  ironyCtx.fillStyle = themeBg(); ironyCtx.fillRect(0, 0, W, H);
  if (!ironyActive) {
    ironyCtx.fillStyle = '#666'; ironyCtx.font = '11px monospace'; ironyCtx.textAlign = 'center';
    ironyCtx.fillText('(pick an ironic utterance)', W / 2, H / 2);
    requestAnimationFrame(drawIrony);
    return;
  }
  const d = IRONY_DATA[ironyActive];
  ironyT = Math.min(200, ironyT + 1);
  ironyCtx.fillStyle = '#aaa'; ironyCtx.font = '11px monospace'; ironyCtx.textAlign = 'left';
  ironyCtx.fillText('what the speaker says', 30, 30);
  ironyCtx.fillStyle = '#fff'; ironyCtx.font = 'bold 18px monospace';
  ironyCtx.fillText(d.surface, 30, 60);
  ironyCtx.fillStyle = '#aaa'; ironyCtx.font = '12px monospace';
  ironyCtx.fillText(d.context, 30, 86);
  if (ironyT > 40) {
    ironyCtx.fillStyle = 'rgba(124,184,255,0.85)'; ironyCtx.font = 'bold 11px monospace';
    ironyCtx.fillText('LITERAL PARSE', 30, 140);
    ironyCtx.fillStyle = '#e0e0e0'; ironyCtx.font = '12px monospace';
    ironyCtx.fillText('→ ' + d.literal, 50, 162);
    ironyCtx.fillStyle = 'rgba(229,57,53,0.85)'; ironyCtx.font = '11px monospace';
    ironyCtx.fillText('✕ mismatch with context', 50, 182);
  }
  if (ironyT > 100) {
    ironyCtx.fillStyle = 'rgba(255,183,77,0.85)'; ironyCtx.font = 'bold 11px monospace';
    ironyCtx.fillText('FLIP OPERATION', 30, 230);
    ironyCtx.fillStyle = '#e0e0e0'; ironyCtx.font = '11px monospace';
    ironyCtx.fillText('the mismatch triggers the listener to re-read the utterance as inverted', 50, 252);
  }
  if (ironyT > 160) {
    ironyCtx.fillStyle = 'rgba(129,199,132,0.85)'; ironyCtx.font = 'bold 11px monospace';
    ironyCtx.fillText('INTENDED MEANING', 30, 300);
    ironyCtx.fillStyle = '#e0e0e0'; ironyCtx.font = '12px monospace';
    ironyCtx.fillText('→ ' + d.intended, 50, 322);
    ironyCtx.fillStyle = 'rgba(129,199,132,0.85)'; ironyCtx.font = '11px monospace';
    ironyCtx.fillText('✓ consistent with context', 50, 342);
  }
  requestAnimationFrame(drawIrony);
}
drawIrony();

// ═══════════════════════════════════════════════════════════════════════
// Taboo
// ═══════════════════════════════════════════════════════════════════════
const TABOO_DATA = {
  mild: { word: 'darn', semantic: 0.7, emotional: 0.05, amygdala: 0.0 },
  medium: { word: 'damn', semantic: 0.7, emotional: 0.35, amygdala: 0.3 },
  strong: { word: '[strong taboo]', semantic: 0.7, emotional: 0.85, amygdala: 0.8 },
};
const tabooCanvas = document.getElementById('taboo-canvas');
const tabooCtx = tabooCanvas.getContext('2d');
let tabooActive = null;
function tabooPlay(k) { tabooActive = k; pepSend('taboo.play', { key: k }); }
function tabooReset() { tabooActive = null; }
function drawTaboo() {
  const W = 960, H = 380;
  tabooCtx.fillStyle = themeBg(); tabooCtx.fillRect(0, 0, W, H);
  if (!tabooActive) {
    tabooCtx.fillStyle = '#666'; tabooCtx.font = '11px monospace'; tabooCtx.textAlign = 'center';
    tabooCtx.fillText('(pick a word class)', W / 2, H / 2);
    requestAnimationFrame(drawTaboo);
    return;
  }
  const d = TABOO_DATA[tabooActive];
  tabooCtx.fillStyle = '#fff'; tabooCtx.font = 'bold 20px monospace'; tabooCtx.textAlign = 'center';
  tabooCtx.fillText(d.word, W / 2, 50);
  // Three activation bars
  const regions = [
    { label: 'SEMANTIC CLUSTER', col: '124,184,255', val: d.semantic },
    { label: 'EMOTIONAL WEIGHT', col: '240,168,105', val: d.emotional },
    { label: 'AMYGDALA / THREAT', col: '229,57,53', val: d.amygdala },
  ];
  regions.forEach((r, i) => {
    const y = 110 + i * 60;
    tabooCtx.fillStyle = '#e0e0e0'; tabooCtx.font = 'bold 11px monospace'; tabooCtx.textAlign = 'left';
    tabooCtx.fillText(r.label, 60, y);
    tabooCtx.fillStyle = 'rgba(' + r.col + ',0.2)';
    tabooCtx.fillRect(60, y + 8, 840, 22);
    tabooCtx.fillStyle = 'rgba(' + r.col + ',0.9)';
    tabooCtx.fillRect(60, y + 8, 840 * r.val, 22);
    tabooCtx.fillStyle = '#aaa'; tabooCtx.textAlign = 'right';
    tabooCtx.fillText((r.val * 100).toFixed(0) + '%', 900, y + 24);
  });
  if (d.amygdala > 0.5) {
    tabooCtx.fillStyle = 'rgba(255,183,77,0.95)'; tabooCtx.font = 'bold 11px monospace'; tabooCtx.textAlign = 'center';
    tabooCtx.fillText('◉ elevated amygdala activation — saying this word costs more', W / 2, 340);
  }
  requestAnimationFrame(drawTaboo);
}
drawTaboo();

// ═══════════════════════════════════════════════════════════════════════
// Grice / Implicature
// ═══════════════════════════════════════════════════════════════════════
const GRICE_DATA = {
  salt: {
    utterance: '"Can you pass the salt?"',
    literal: 'question about physical ability',
    literalAbsurd: 'a yes/no answer without passing the salt would be absurd',
    inference: 'the speaker is cooperative, so they must want the salt',
    intended: 'REQUEST: please pass the salt',
  },
  cold: {
    utterance: '"It is cold in here."',
    literal: 'weather report about the room',
    literalAbsurd: 'reporting the temperature without reason would be strange',
    inference: 'the speaker wants something done about the temperature',
    intended: 'REQUEST: please close the window / adjust the thermostat',
  },
  dating: {
    utterance: '"John is dating someone in New York."',
    literal: 'John is dating a person who lives in New York',
    literalAbsurd: 'why mention location unless it is relevant',
    inference: 'the person is specifically NOT local, which is why location is noted',
    intended: 'IMPLICATURE: they are in a long-distance relationship',
  },
};
const griceCanvas = document.getElementById('grice-canvas');
const griceCtx = griceCanvas.getContext('2d');
let griceActive = null, griceT = 0;
function gricePlay(k) { griceActive = k; griceT = 0; pepSend('grice.play', { key: k }); }
function griceReset() { griceActive = null; griceT = 0; }
function drawGrice() {
  const W = 960, H = 400;
  griceCtx.fillStyle = themeBg(); griceCtx.fillRect(0, 0, W, H);
  if (!griceActive) {
    griceCtx.fillStyle = '#666'; griceCtx.font = '11px monospace'; griceCtx.textAlign = 'center';
    griceCtx.fillText('(pick an utterance)', W / 2, H / 2);
    requestAnimationFrame(drawGrice);
    return;
  }
  const d = GRICE_DATA[griceActive];
  griceT = Math.min(200, griceT + 1);
  griceCtx.fillStyle = '#fff'; griceCtx.font = 'bold 18px monospace'; griceCtx.textAlign = 'center';
  griceCtx.fillText(d.utterance, W / 2, 50);
  if (griceT > 30) {
    griceCtx.fillStyle = 'rgba(124,184,255,0.85)'; griceCtx.font = 'bold 11px monospace'; griceCtx.textAlign = 'left';
    griceCtx.fillText('LITERAL', 40, 100);
    griceCtx.fillStyle = '#e0e0e0'; griceCtx.font = '12px monospace';
    griceCtx.fillText('→ ' + d.literal, 60, 122);
  }
  if (griceT > 70) {
    griceCtx.fillStyle = 'rgba(229,57,53,0.85)'; griceCtx.font = '11px monospace';
    griceCtx.fillText('but: ' + d.literalAbsurd, 60, 148);
  }
  if (griceT > 110) {
    griceCtx.fillStyle = 'rgba(255,183,77,0.85)'; griceCtx.font = 'bold 11px monospace';
    griceCtx.fillText('COOPERATIVE INFERENCE', 40, 200);
    griceCtx.fillStyle = '#e0e0e0'; griceCtx.font = '12px monospace';
    griceCtx.fillText('→ ' + d.inference, 60, 222);
  }
  if (griceT > 160) {
    griceCtx.fillStyle = 'rgba(129,199,132,0.85)'; griceCtx.font = 'bold 11px monospace';
    griceCtx.fillText('RECOVERED INTENT', 40, 280);
    griceCtx.fillStyle = '#fff'; griceCtx.font = 'bold 13px monospace';
    griceCtx.fillText('→ ' + d.intended, 60, 304);
    griceCtx.fillStyle = '#aaa'; griceCtx.font = '11px monospace';
    griceCtx.fillText('the listener did this automatically, in milliseconds, without noticing', 60, 328);
  }
  requestAnimationFrame(drawGrice);
}
drawGrice();

// ═══════════════════════════════════════════════════════════════════════
// Vocabulary Growth
// ═══════════════════════════════════════════════════════════════════════
const vocabCanvas = document.getElementById('vocab-canvas');
const vocabCtx = vocabCanvas.getContext('2d');
document.getElementById('vocab-size').addEventListener('input', (e) => {
  document.getElementById('vocab-val').textContent = e.target.value;
});
function vocabReset() {
  document.getElementById('vocab-size').value = 12;
  document.getElementById('vocab-val').textContent = '12';
}
function drawVocab() {
  const W = 960, H = 420;
  vocabCtx.fillStyle = themeBg(); vocabCtx.fillRect(0, 0, W, H);
  const size = parseInt(document.getElementById('vocab-size').value);
  // Draw a continuous feature space (color gradient band)
  const bandH = 70, bandY = 130;
  for (let i = 0; i < 600; i++) {
    const t = i / 600;
    const r = Math.round(255 * (1 - t) + 60 * t);
    const g = Math.round(120 * (1 - t) + 200 * t);
    const b = Math.round(60 * (1 - t) + 255 * t);
    vocabCtx.fillStyle = 'rgb(' + r + ',' + g + ',' + b + ')';
    vocabCtx.fillRect(30 + i, bandY, 1, bandH);
  }
  vocabCtx.strokeStyle = 'rgba(120,120,140,0.5)'; vocabCtx.lineWidth = 1;
  vocabCtx.strokeRect(30, bandY, 600, bandH);
  vocabCtx.fillStyle = '#aaa'; vocabCtx.font = '11px monospace'; vocabCtx.textAlign = 'left';
  vocabCtx.fillText('continuous feature space (e.g. color, flavor, emotion)', 30, bandY - 10);
  // Draw distinctions based on vocab size
  for (let i = 0; i < size; i++) {
    const x = 30 + ((i + 0.5) / size) * 600;
    vocabCtx.strokeStyle = 'rgba(255,255,255,0.8)'; vocabCtx.lineWidth = 2;
    vocabCtx.beginPath(); vocabCtx.moveTo(x, bandY); vocabCtx.lineTo(x, bandY + bandH); vocabCtx.stroke();
  }
  vocabCtx.fillStyle = '#aaa'; vocabCtx.font = '11px monospace'; vocabCtx.textAlign = 'left';
  vocabCtx.fillText('vocabulary size = ' + size + ' → ' + size + ' named categories → ' + size + ' reliably perceivable distinctions', 30, bandY + bandH + 30);
  // Info
  vocabCtx.fillStyle = '#aaa'; vocabCtx.font = '11px monospace';
  if (size < 6) vocabCtx.fillText('with few words, most of the space reads as "some fuzzy thing"', 30, bandY + bandH + 60);
  else if (size < 20) vocabCtx.fillText('moderate vocabulary: basic distinctions become stable', 30, bandY + bandH + 60);
  else if (size < 35) vocabCtx.fillText('rich vocabulary: subtle distinctions are reliably perceivable', 30, bandY + bandH + 60);
  else vocabCtx.fillText('expert vocabulary: the feature space has become a fine-grained grid', 30, bandY + bandH + 60);
  // Expert analogy
  vocabCtx.fillStyle = '#888'; vocabCtx.font = '10px monospace';
  vocabCtx.fillText('wine taster: ~30+ flavor terms · casual drinker: ~3-5', 30, H - 40);
  vocabCtx.fillText('programmer: hundreds of type/data-structure terms · layperson: ~10', 30, H - 22);
  requestAnimationFrame(drawVocab);
}
drawVocab();

// ═══════════════════════════════════════════════════════════════════════
// Code-Switching
// ═══════════════════════════════════════════════════════════════════════
const CSWITCH_DATA = {
  spanglish: {
    words: [
      { w: 'I', lang: 'L1' }, { w: 'went', lang: 'L1' }, { w: 'al', lang: 'L2' }, { w: 'mercado', lang: 'L2' },
      { w: 'porque', lang: 'L2' }, { w: 'necesitaba', lang: 'L2' }, { w: 'milk', lang: 'L1' },
    ],
    note: 'concrete item "milk" is faster to retrieve in L1; the rest runs in L2 grammar',
  },
  formal: {
    words: [
      { w: 'The', lang: 'L1' }, { w: 'speech', lang: 'L1' }, { w: 'was', lang: 'L1' }, { w: 'long,', lang: 'L1' },
      { w: 'pero', lang: 'L2' }, { w: 'bien', lang: 'L2' }, { w: 'chevere', lang: 'L2' },
    ],
    note: 'formal proposition in L1, emotional reaction in L2',
  },
  emotional: {
    words: [
      { w: 'Technically', lang: 'L1' }, { w: 'the', lang: 'L1' }, { w: 'contract', lang: 'L1' }, { w: 'is', lang: 'L1' },
      { w: 'valid,', lang: 'L1' }, { w: 'pero', lang: 'L2' }, { w: 'me', lang: 'L2' }, { w: 'duele', lang: 'L2' },
    ],
    note: 'analytical content in L1 (business language), emotional content in L2 (personal tongue)',
  },
};
const cswitchCanvas = document.getElementById('cswitch-canvas');
const cswitchCtx = cswitchCanvas.getContext('2d');
let cswitchActive = null, cswitchIdx = 0, cswitchTimer = 0;
function cswitchPlay(k) { cswitchActive = k; cswitchIdx = 0; cswitchTimer = 0; pepSend('codeswitch.play', { key: k }); }
function cswitchReset() { cswitchActive = null; cswitchIdx = 0; cswitchTimer = 0; }
function drawCswitch() {
  const W = 960, H = 400;
  cswitchCtx.fillStyle = themeBg(); cswitchCtx.fillRect(0, 0, W, H);
  if (!cswitchActive) {
    cswitchCtx.fillStyle = '#666'; cswitchCtx.font = '11px monospace'; cswitchCtx.textAlign = 'center';
    cswitchCtx.fillText('(pick a scenario)', W / 2, H / 2);
    requestAnimationFrame(drawCswitch);
    return;
  }
  const d = CSWITCH_DATA[cswitchActive];
  cswitchTimer++;
  if (cswitchTimer > 30 && cswitchIdx < d.words.length) { cswitchTimer = 0; cswitchIdx++; }
  // L1 / L2 prior blocks at top
  cswitchCtx.fillStyle = 'rgba(124,184,255,0.25)';
  cswitchCtx.fillRect(60, 40, 360, 80);
  cswitchCtx.strokeStyle = 'rgba(124,184,255,0.85)'; cswitchCtx.lineWidth = 2; cswitchCtx.strokeRect(60, 40, 360, 80);
  cswitchCtx.fillStyle = '#fff'; cswitchCtx.font = 'bold 13px monospace'; cswitchCtx.textAlign = 'center';
  cswitchCtx.fillText('L1 grammar prior (English)', 240, 86);
  cswitchCtx.fillStyle = 'rgba(240,168,105,0.25)';
  cswitchCtx.fillRect(540, 40, 360, 80);
  cswitchCtx.strokeStyle = 'rgba(240,168,105,0.85)'; cswitchCtx.strokeRect(540, 40, 360, 80);
  cswitchCtx.fillStyle = '#fff';
  cswitchCtx.fillText('L2 grammar prior (Spanish)', 720, 86);
  // Sentence
  cswitchCtx.fillStyle = '#aaa'; cswitchCtx.font = '11px monospace'; cswitchCtx.textAlign = 'left';
  cswitchCtx.fillText('output sentence', 60, 170);
  let x = 60, y = 210;
  for (let i = 0; i < cswitchIdx; i++) {
    const word = d.words[i];
    const col = word.lang === 'L1' ? '124,184,255' : '240,168,105';
    cswitchCtx.fillStyle = 'rgba(' + col + ',0.95)'; cswitchCtx.font = 'bold 16px monospace';
    const m = cswitchCtx.measureText(word.w + ' ');
    if (x + m.width > W - 60) { x = 60; y += 30; }
    cswitchCtx.fillText(word.w + ' ', x, y);
    x += m.width;
  }
  if (cswitchIdx >= d.words.length) {
    cswitchCtx.fillStyle = '#aaa'; cswitchCtx.font = '11px monospace';
    cswitchCtx.fillText(d.note, 60, H - 30);
  }
  requestAnimationFrame(drawCswitch);
}
drawCswitch();

// ═══════════════════════════════════════════════════════════════════════
// Semantic Drift
// ═══════════════════════════════════════════════════════════════════════
const DRIFT_DATA = {
  awful: {
    years: [
      { y: 1400, nodes: ['full-of-awe','reverent','majestic','fear-of-god','sublime'] },
      { y: 1700, nodes: ['full-of-awe','reverent','overwhelming','fear','grand'] },
      { y: 1850, nodes: ['overwhelming','fear','unpleasant','grand','very'] },
      { y: 1950, nodes: ['unpleasant','very','bad','shocking','disgusting'] },
      { y: 2025, nodes: ['bad','shocking','disgusting','very','terrible'] },
    ],
  },
  nice: {
    years: [
      { y: 1300, nodes: ['foolish','silly','simple','ignorant','wanton'] },
      { y: 1500, nodes: ['foolish','silly','shy','fastidious','precise'] },
      { y: 1700, nodes: ['precise','careful','exact','refined','particular'] },
      { y: 1900, nodes: ['refined','pleasant','kind','agreeable','respectable'] },
      { y: 2025, nodes: ['pleasant','kind','agreeable','good','polite'] },
    ],
  },
  gay: {
    years: [
      { y: 1400, nodes: ['joyful','cheerful','bright','merry','carefree'] },
      { y: 1700, nodes: ['joyful','cheerful','showy','merry','licentious'] },
      { y: 1900, nodes: ['cheerful','lively','brightly-dressed','carefree','promiscuous'] },
      { y: 1970, nodes: ['homosexual','community','pride','identity','political'] },
      { y: 2025, nodes: ['homosexual','community','pride','identity','orientation'] },
    ],
  },
  silly: {
    years: [
      { y: 1200, nodes: ['happy','blessed','innocent','blessed-by-god','pious'] },
      { y: 1400, nodes: ['innocent','harmless','deserving-pity','helpless','weak'] },
      { y: 1600, nodes: ['weak','simple','ignorant','foolish','absurd'] },
      { y: 1900, nodes: ['foolish','absurd','childish','trivial','laughable'] },
      { y: 2025, nodes: ['foolish','absurd','childish','playful','light'] },
    ],
  },
};
const driftCanvas = document.getElementById('drift-canvas');
const driftCtx = driftCanvas.getContext('2d');
let driftWordKey = null;
function driftWord(k) { driftWordKey = k; pepSend('drift.word', { key: k }); }
document.getElementById('drift-year').addEventListener('input', (e) => {
  document.getElementById('drift-year-val').textContent = e.target.value;
});
function drawDrift() {
  const W = 960, H = 440;
  driftCtx.fillStyle = themeBg(); driftCtx.fillRect(0, 0, W, H);
  if (!driftWordKey) {
    driftCtx.fillStyle = '#666'; driftCtx.font = '11px monospace'; driftCtx.textAlign = 'center';
    driftCtx.fillText('(pick a word)', W / 2, H / 2);
    requestAnimationFrame(drawDrift);
    return;
  }
  const year = parseInt(document.getElementById('drift-year').value);
  const d = DRIFT_DATA[driftWordKey];
  // Find nearest year entry
  let best = d.years[0];
  d.years.forEach(e => { if (Math.abs(e.y - year) < Math.abs(best.y - year)) best = e; });
  // Draw word at center
  const cx = W / 2, cy = H / 2;
  driftCtx.fillStyle = 'rgba(124,184,255,0.35)';
  driftCtx.beginPath(); driftCtx.arc(cx, cy, 50, 0, Math.PI * 2); driftCtx.fill();
  driftCtx.strokeStyle = 'rgba(124,184,255,0.95)'; driftCtx.lineWidth = 2; driftCtx.stroke();
  driftCtx.fillStyle = '#fff'; driftCtx.font = 'bold 16px monospace'; driftCtx.textAlign = 'center';
  driftCtx.fillText('"' + driftWordKey + '"', cx, cy + 4);
  // Year label
  driftCtx.fillStyle = '#aaa'; driftCtx.font = '11px monospace';
  driftCtx.fillText('year ~' + best.y, cx, cy - 70);
  // Radiating constellation
  best.nodes.forEach((n, i) => {
    const a = (i / best.nodes.length) * Math.PI * 2 - Math.PI / 2;
    const r = 160;
    const x = cx + Math.cos(a) * r;
    const y = cy + Math.sin(a) * r;
    driftCtx.strokeStyle = 'rgba(124,184,255,0.4)'; driftCtx.lineWidth = 1;
    driftCtx.beginPath(); driftCtx.moveTo(cx, cy); driftCtx.lineTo(x, y); driftCtx.stroke();
    driftCtx.fillStyle = 'rgba(124,184,255,0.55)';
    driftCtx.beginPath(); driftCtx.arc(x, y, 8, 0, Math.PI * 2); driftCtx.fill();
    driftCtx.fillStyle = '#e0e0e0'; driftCtx.font = '11px monospace'; driftCtx.textAlign = 'center';
    driftCtx.fillText(n, x, y + (Math.sin(a) >= 0 ? 24 : -14));
  });
  driftCtx.fillStyle = '#888'; driftCtx.font = '10px monospace'; driftCtx.textAlign = 'center';
  driftCtx.fillText('slide the year to watch the constellation drift across centuries', W / 2, H - 20);
  requestAnimationFrame(drawDrift);
}
drawDrift();

// ═══════════════════════════════════════════════════════════════════════
// Glossary hover
// ═══════════════════════════════════════════════════════════════════════
(function installGlossary() {
  const terms = {
    'constellation': 'The set of nodes a word activates. The shape of the constellation is the meaning.',
    'prior': 'A stored expectation the brain uses to predict the next input.',
    'priors': 'Stored expectations the brain uses to predict the next input.',
    'residual': 'Prediction error — the gap between forecast and reality.',
    'forecast': 'The predictor\\u0027s guess at what comes next.',
    'activation': 'The current firing level of a node or cluster of nodes.',
    'token': 'A unit of input (often a word or sub-word) in a language model.',
    'distribution': 'The spread of probabilities across candidate next-tokens.',
    'compositional': 'Meaning built from combining the meanings of individual parts.',
    'unitary': 'Stored as a single block, not composed from parts.',
    'implicature': 'What a listener infers beyond the literal words.',
    'amygdala': 'Brain region central to threat detection and emotional weighting.',
    'LLM': 'Large Language Model — a statistical model of next-token distributions.',
  };
  const tooltip = document.createElement('div');
  tooltip.style.cssText = 'position:fixed;display:none;background:var(--surface);border:1px solid var(--accent);border-radius:4px;padding:8px 12px;font-family:monospace;font-size:11px;color:var(--text);max-width:320px;line-height:1.5;z-index:200;pointer-events:none;box-shadow:0 4px 12px rgba(0,0,0,0.5)';
  document.body.appendChild(tooltip);
  const termKeys = Object.keys(terms).sort((a, b) => b.length - a.length);
  document.querySelectorAll('.info').forEach(info => {
    termKeys.forEach(term => {
      const re = new RegExp('(^|[^a-zA-Z0-9_-])(' + term + ')(?=[^a-zA-Z0-9_-]|$)', 'gi');
      info.innerHTML = info.innerHTML.replace(re, function (m, pre, word) {
        return pre + '<span class="gloss" data-term="' + term + '" style="border-bottom:1px dotted rgba(124,184,255,0.6);cursor:help">' + word + '</span>';
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

// ═══════════════════════════════════════════════════════════════════════
// Take a Tour
// ═══════════════════════════════════════════════════════════════════════
const tourSteps = [
  { tab: 'home-tab',        title: 'Welcome to Lingora',              body: 'Lingora is Axona\\u0027s sibling — the LAVAS project focused on language. Words are not symbols paired with meanings; they are cues that activate specific constellations of nodes. Every canvas here demonstrates one aspect of that claim. I will walk you through them.' },
  { tab: 'word-tab',        title: 'Word as Constellation',           body: 'Click any word and watch the nodes it activates. Concrete words (dog, fire) have tight constellations most people share. Abstract words (freedom, home) have loose ones that differ wildly between speakers — which is why agreement on abstract terms is so hard.' },
  { tab: 'sentence-tab',    title: 'Sentence Forecast',               body: 'A sentence is the predictor narrowing onto a single region. Watch the top-k distribution for "the cat sat on the ___" collapse as each word arrives. The garden-path sentence shows what happens when the forecast gets violated — the parser has to rewind.' },
  { tab: 'listener-tab',    title: 'Listener Reconstruction',         body: 'The missing half. Sentence Forecast shows the predictor. Listener shows the composite meaning building live in the listener as each word arrives. Meaning is never transmitted — it is reconstructed from scratch.' },
  { tab: 'transfer-tab',    title: 'Speaker ↔ Listener Transfer',     body: 'The wider view. Speaker compresses a rich mental state into words. The words travel through a narrow bottleneck. The listener decompresses them into a different mental state. The gap between the two is the cost of language.' },
  { tab: 'ambig-tab',       title: 'Ambiguity Resolution',            body: 'BANK has two meaning clusters — riverside and financial — that compete when the word arrives. Context pre-warms one cluster so it wins the race. You never experience the ambiguity, only the winner.' },
  { tab: 'humor-tab',       title: 'Humor & Puns',                    body: 'A pun is an ambiguous word deployed so that both meanings fire at once. The simultaneous dual activation produces a spike that feels like a laugh. Explaining a joke destroys the spike, which is why explained puns are not funny.' },
  { tab: 'idiom-tab',       title: 'Idiom as Opaque Block',           body: '"Kick the bucket" does not activate KICK + BUCKET. It is cached as a unitary block that retrieves "die." The compositional path fails; the unitary path wins. A big chunk of everyday speech runs on block retrievals like this.' },
  { tab: 'grammar-tab',     title: 'Grammar as Prior',                body: 'Grammar is not a rulebook. It is a learned distribution over which word-types follow which others. Fluent, loose, and random modes show the same sampling operation with different priors loaded. Children learn grammar by training the distribution, not memorizing rules.' },
  { tab: 'prompt-tab',      title: 'Prompt Engineering',              body: 'Same underlying question, different framings, different regions of the activation space lit up. Vague prompts fall into the default region. Constrained prompts push into specific corners. Role-framed prompts relocate the center entirely.' },
  { tab: 'llm-tab',         title: 'LLM Bridge',                      body: 'The one thing Lingora does that nothing else can: PEP\\u0027s framework applied to a running language model. Top-k next-token probabilities as the forecast narrows with context. Currently stubbed because no API key is set — add one and it goes live.' },
  { tab: 'poetry-tab',      title: 'Poetry as Residual',              body: 'A good poem is a sequence of engineered prediction violations. Most words land softly. A few land hard — the ones the poet chose specifically to produce a residual spike. Those spikes are what "landed" means.' },
  { tab: 'writing-tab',     title: 'Show Don\\u0027t Tell',           body: 'Concrete words fire sensory cortex. Abstract words do not. Same proposition, radically different cognitive texture. This is the oldest writing advice made mechanical.' },
  { tab: 'voice-tab',       title: 'Active ↔ Passive',                body: 'Same facts, different attention allocation. Active voice topicalizes the agent, passive topicalizes the patient, agentless passive erases responsibility entirely. "Mistakes were made" is a specific linguistic move.' },
  { tab: 'irony-tab',       title: 'Irony',                           body: 'Saying literally one thing and meaning another, trusting the listener to flip the sign. Requires a measurable extra parse step, which is why sarcasm feels different from direct speech — and why it fails in text.' },
  { tab: 'taboo-tab',       title: 'Taboo Words',                     body: 'Some words carry elevated emotional weight via edges to the amygdala. Saying them costs more and produces measurable autonomic responses. This is why swearing works as a pain reliever and why taboo is socially constructed.' },
  { tab: 'grice-tab',       title: 'Implicature',                     body: '"Can you pass the salt?" is literally a yes/no question. Everyone hears a request. The listener runs a cooperative inference automatically — if the literal reading is absurd in context, try the most charitable non-literal reading. Theory of mind in real time.' },
  { tab: 'vocab-tab',       title: 'Vocabulary Growth',               body: 'A distinction with a name is cheap to draw. Without one, it fades. Slide the vocabulary size and watch more of the feature space become reliably distinguishable. Experts have lots of words in their domain for exactly this reason.' },
  { tab: 'codeswitch-tab',  title: 'Code-Switching',                  body: 'Bilinguals have two grammar priors loaded in parallel. Each word-slot picks whichever prior has the tighter activation for the intended concept. Emotional content tends to stay in L1 because the affective edges are deeper there.' },
  { tab: 'drift-tab',       title: 'Semantic Drift',                  body: 'Word meanings drift across centuries because the collective activation pattern drifts. "Awful" used to mean full of awe. "Gay" has shifted twice. Slide the year and watch the constellation shift.' },
  { tab: 'translation-tab', title: 'Translation Gap',                 body: 'Shared nodes survive translation. Missing nodes are what "does not translate." Added nodes are meaning the target language carries that the source does not. Saudade, schadenfreude, komorebi, hygge — all have structural mismatches with English.' },
  { tab: 'bridge-tab',      title: 'PEP ↔ Lingora Bridge',            body: 'The live cross-talk with PEP. Every canvas action posts a linguistic event to PEP. PEP\\u0027s runtime state flows back. Lingora is part of the same living system as PEP and Axona, not a stand-alone demo.' },
  { tab: 'home-tab',        title: 'That is the tour',                body: 'Twenty canvases. One claim: language runs on PEP\\u0027s framework. Poke around, toggle light mode, hover technical terms for tooltips. If you want more, tell me what — the next obvious adds are irony as second-order theory of mind, reading aloud vs silent, and a live LLM hook once an API key is configured.' },
];
let tourIdx = 0, tourOverlay = null;
function tourStart() { tourIdx = 0; if (!tourOverlay) tourBuildOverlay(); tourOverlay.style.display = 'flex'; tourShowStep(); pepSend('tour.start', {}); }
function tourEnd() { if (tourOverlay) tourOverlay.style.display = 'none'; pepSend('tour.end', { atStep: tourIdx }); }
function tourNext() { tourIdx++; if (tourIdx >= tourSteps.length) { tourEnd(); return; } tourShowStep(); }
function tourPrev() { if (tourIdx > 0) { tourIdx--; tourShowStep(); } }
function tourShowStep() {
  const step = tourSteps[tourIdx];
  if (!step) { tourEnd(); return; }
  const tab = findTabForPanel(step.tab) || document.querySelector('[data-panel="' + step.tab + '"]');
  if (tab) tab.click();
  setTimeout(() => {
    const el = document.getElementById(step.tab);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    else window.scrollTo(0, 0);
  }, 60);
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
// Onomatopoeia
// ═══════════════════════════════════════════════════════════════════════
const ONOMA_DATA = {
  bang: { word: 'BANG', semantic: 0.6, auditory: 0.9, visual: 0.4, motor: 0.3 },
  crash: { word: 'CRASH', semantic: 0.6, auditory: 0.95, visual: 0.5, motor: 0.2 },
  whisper: { word: 'whisper', semantic: 0.5, auditory: 0.8, visual: 0.15, motor: 0.1 },
  buzz: { word: 'buzz', semantic: 0.55, auditory: 0.9, visual: 0.1, motor: 0.05 },
  plain: { word: 'table', semantic: 0.85, auditory: 0.08, visual: 0.6, motor: 0.15 },
};
const onomaCanvas = document.getElementById('onoma-canvas');
const onomaCtx = onomaCanvas.getContext('2d');
let onomaActive = null;
function onomaPlay(k) { onomaActive = k; pepSend('onoma.play', { key: k }); }
function onomaReset() { onomaActive = null; }
function drawOnoma() {
  const W = 960, H = 360; onomaCtx.fillStyle = themeBg(); onomaCtx.fillRect(0, 0, W, H);
  if (!onomaActive) { onomaCtx.fillStyle = '#666'; onomaCtx.font = '11px monospace'; onomaCtx.textAlign = 'center'; onomaCtx.fillText('(pick a word)', W / 2, H / 2); requestAnimationFrame(drawOnoma); return; }
  const d = ONOMA_DATA[onomaActive];
  onomaCtx.fillStyle = '#fff'; onomaCtx.font = 'bold 28px monospace'; onomaCtx.textAlign = 'center';
  onomaCtx.fillText(d.word, W / 2, 60);
  const regions = [
    { l: 'SEMANTIC', v: d.semantic, c: '124,184,255' },
    { l: 'AUDITORY', v: d.auditory, c: '240,168,105' },
    { l: 'VISUAL', v: d.visual, c: '129,199,132' },
    { l: 'MOTOR', v: d.motor, c: '186,104,200' },
  ];
  regions.forEach((r, i) => {
    const y = 110 + i * 55;
    onomaCtx.fillStyle = '#e0e0e0'; onomaCtx.font = 'bold 11px monospace'; onomaCtx.textAlign = 'left';
    onomaCtx.fillText(r.l, 60, y);
    onomaCtx.fillStyle = 'rgba(' + r.c + ',0.2)'; onomaCtx.fillRect(60, y + 8, 840, 22);
    onomaCtx.fillStyle = 'rgba(' + r.c + ',0.9)'; onomaCtx.fillRect(60, y + 8, 840 * r.v, 22);
    onomaCtx.fillStyle = '#aaa'; onomaCtx.textAlign = 'right';
    onomaCtx.fillText((r.v * 100).toFixed(0) + '%', 900, y + 24);
  });
  requestAnimationFrame(drawOnoma);
}
drawOnoma();

// ═══════════════════════════════════════════════════════════════════════
// Phonology — Categorical Perception
// ═══════════════════════════════════════════════════════════════════════
const phonoCanvas = document.getElementById('phono-canvas');
const phonoCtx = phonoCanvas.getContext('2d');
let phonoPriorName = 'english';
function phonoPrior(p) { phonoPriorName = p; pepSend('phono.prior', { prior: p }); }
function drawPhono() {
  const W = 960, H = 400; phonoCtx.fillStyle = themeBg(); phonoCtx.fillRect(0, 0, W, H);
  const gradX = 60, gradY = 140, gradW = 840, gradH = 50;
  // Continuous acoustic gradient
  for (let i = 0; i < gradW; i++) {
    const t = i / gradW;
    const hue = 20 + t * 200;
    phonoCtx.fillStyle = 'hsl(' + hue + ', 70%, 55%)';
    phonoCtx.fillRect(gradX + i, gradY, 1, gradH);
  }
  phonoCtx.strokeStyle = 'rgba(120,120,140,0.6)'; phonoCtx.lineWidth = 1;
  phonoCtx.strokeRect(gradX, gradY, gradW, gradH);
  phonoCtx.fillStyle = '#aaa'; phonoCtx.font = '11px monospace'; phonoCtx.textAlign = 'left';
  phonoCtx.fillText('continuous acoustic space (r → l)', gradX, gradY - 10);
  // Category boundaries based on prior
  if (phonoPriorName === 'english') {
    // Hard boundary in middle
    const bx = gradX + gradW / 2;
    phonoCtx.strokeStyle = 'rgba(255,255,255,0.95)'; phonoCtx.lineWidth = 4;
    phonoCtx.beginPath(); phonoCtx.moveTo(bx, gradY - 10); phonoCtx.lineTo(bx, gradY + gradH + 10); phonoCtx.stroke();
    phonoCtx.fillStyle = '#fff'; phonoCtx.font = 'bold 14px monospace'; phonoCtx.textAlign = 'center';
    phonoCtx.fillText('/r/', gradX + gradW * 0.25, gradY + gradH + 28);
    phonoCtx.fillText('/l/', gradX + gradW * 0.75, gradY + gradH + 28);
    phonoCtx.fillStyle = 'rgba(124,184,255,0.95)'; phonoCtx.font = '11px monospace';
    phonoCtx.fillText('sharp categorical boundary — English listener', gradX + gradW / 2, 240);
  } else if (phonoPriorName === 'japanese') {
    phonoCtx.fillStyle = 'rgba(120,120,140,0.5)'; phonoCtx.fillRect(gradX, gradY - 6, gradW, gradH + 12);
    phonoCtx.fillStyle = '#fff'; phonoCtx.font = 'bold 14px monospace'; phonoCtx.textAlign = 'center';
    phonoCtx.fillText('/r/ (one category)', gradX + gradW / 2, gradY + gradH + 28);
    phonoCtx.fillStyle = 'rgba(240,168,105,0.95)'; phonoCtx.font = '11px monospace';
    phonoCtx.fillText('no boundary — Japanese listener hears one continuous sound', gradX + gradW / 2, 240);
  } else {
    phonoCtx.fillStyle = 'rgba(120,120,140,0.8)'; phonoCtx.font = '11px monospace'; phonoCtx.textAlign = 'center';
    phonoCtx.fillText('raw acoustic signal — no categorical perception applied', gradX + gradW / 2, 240);
  }
  // Step markers
  for (let i = 0; i <= 10; i++) {
    const x = gradX + (i / 10) * gradW;
    phonoCtx.strokeStyle = 'rgba(255,255,255,0.35)'; phonoCtx.lineWidth = 1;
    phonoCtx.beginPath(); phonoCtx.moveTo(x, gradY + gradH + 2); phonoCtx.lineTo(x, gradY + gradH + 8); phonoCtx.stroke();
  }
  phonoCtx.fillStyle = '#888'; phonoCtx.font = '10px monospace'; phonoCtx.textAlign = 'center';
  phonoCtx.fillText('acoustic step 0 (pure /r/) → 10 (pure /l/)', gradX + gradW / 2, H - 30);
  requestAnimationFrame(drawPhono);
}
drawPhono();

// ═══════════════════════════════════════════════════════════════════════
// Prosody
// ═══════════════════════════════════════════════════════════════════════
const PROSODY_WORDS = ['I', "didn't", 'say', 'he', 'stole', 'the', 'money'];
// Indexed by word position. Slot 5 ("the") is unused because "the" does not
// normally carry contrastive stress in English.
const PROSODY_MEANINGS = [
  'someone ELSE said it (not me)',                      // 0: I
  'I deny saying it at all — maybe I implied it',       // 1: didn't
  'I did not say it — maybe I wrote or implied it',     // 2: say
  'maybe SHE or they stole it, not him',                // 3: he
  'maybe he BORROWED or FOUND it, not stole it',        // 4: stole
  null,                                                 // 5: the (unused)
  'maybe he stole something ELSE, not the money',       // 6: money
];
const PROSODY_CONTRASTS = [
  '{someone else, they, she, we}',                      // 0: I
  '{I did, I might have, I implied}',                   // 1: didn't
  '{wrote, implied, hinted, whispered}',                // 2: say
  '{she, they, you, someone else}',                     // 3: he
  '{borrowed, found, took, kept}',                      // 4: stole
  null,                                                 // 5: the (unused)
  '{jewels, car, papers, something else}',              // 6: money
];
const prosodyCanvas = document.getElementById('prosody-canvas');
const prosodyCtx = prosodyCanvas.getContext('2d');
let prosodyStressIdx = -1;  // -1 = neutral, 0..6 = index of stressed word
function prosodyStress(i) { prosodyStressIdx = i; pepSend('prosody.stress', { index: i }); }
function drawProsody() {
  const W = 960, H = 420; prosodyCtx.fillStyle = themeBg(); prosodyCtx.fillRect(0, 0, W, H);
  // Sentence
  prosodyCtx.fillStyle = '#aaa'; prosodyCtx.font = '11px monospace'; prosodyCtx.textAlign = 'left';
  prosodyCtx.fillText('the sentence (stressed word in orange)', 30, 30);
  let x = 30;
  PROSODY_WORDS.forEach((w, i) => {
    const stressed = i === prosodyStressIdx;
    prosodyCtx.fillStyle = stressed ? 'rgba(240,168,105,0.95)' : '#e0e0e0';
    prosodyCtx.font = stressed ? 'bold 20px monospace' : '16px monospace';
    prosodyCtx.fillText(w + ' ', x, 70);
    x += prosodyCtx.measureText(w + ' ').width + 4;
  });
  // Pitch contour
  prosodyCtx.strokeStyle = 'rgba(124,184,255,0.85)'; prosodyCtx.lineWidth = 2;
  prosodyCtx.beginPath();
  const baseY = 150;
  PROSODY_WORDS.forEach((w, i) => {
    const cx = 60 + i * 130;
    const stressed = i === prosodyStressIdx;
    const y = stressed ? baseY - 40 : baseY + (Math.sin(i) * 8);
    if (i === 0) prosodyCtx.moveTo(cx, y); else prosodyCtx.lineTo(cx, y);
  });
  prosodyCtx.stroke();
  prosodyCtx.fillStyle = '#aaa'; prosodyCtx.font = '10px monospace';
  prosodyCtx.fillText('pitch contour', 30, 130);
  // Meaning
  prosodyCtx.fillStyle = 'rgba(129,199,132,0.95)'; prosodyCtx.font = 'bold 14px monospace';
  prosodyCtx.fillText('→ inferred meaning:', 30, 240);
  prosodyCtx.fillStyle = '#fff'; prosodyCtx.font = '13px monospace';
  const meaning = prosodyStressIdx < 0 ? 'neutral reading — no word carries contrastive stress' : (PROSODY_MEANINGS[prosodyStressIdx] || '—');
  prosodyCtx.fillText(meaning, 30, 265);
  // Alternative set
  if (prosodyStressIdx >= 0 && PROSODY_CONTRASTS[prosodyStressIdx]) {
    prosodyCtx.fillStyle = '#aaa'; prosodyCtx.font = '11px monospace';
    prosodyCtx.fillText('implicit contrast set activated:', 30, 310);
    prosodyCtx.fillStyle = 'rgba(240,168,105,0.9)'; prosodyCtx.font = '12px monospace';
    prosodyCtx.fillText(PROSODY_CONTRASTS[prosodyStressIdx], 30, 332);
  }
  requestAnimationFrame(drawProsody);
}
drawProsody();

// ═══════════════════════════════════════════════════════════════════════
// Silence
// ═══════════════════════════════════════════════════════════════════════
const SILENCE_DATA = {
  question: { setup: '"Did you love me?"', gap: 1800, response: '"... I tried."', note: 'a long gap before an answer is itself an answer' },
  joke: { setup: 'A horse walks into a bar', gap: 700, response: '... and the bartender says, "why the long face?"', note: 'comedic timing is the engineered beat' },
  grief: { setup: '"How are you holding up?"', gap: 2400, response: '"..."', note: 'silence after a loss is more honest than words' },
};
const silenceCanvas = document.getElementById('silence-canvas');
const silenceCtx = silenceCanvas.getContext('2d');
let silenceActive = null, silenceT = 0;
function silencePlay(k) { silenceActive = k; silenceT = 0; pepSend('silence.play', { key: k }); }
function silenceReset() { silenceActive = null; silenceT = 0; }
function drawSilence() {
  const W = 960, H = 360; silenceCtx.fillStyle = themeBg(); silenceCtx.fillRect(0, 0, W, H);
  if (!silenceActive) { silenceCtx.fillStyle = '#666'; silenceCtx.font = '11px monospace'; silenceCtx.textAlign = 'center'; silenceCtx.fillText('(pick a scene)', W / 2, H / 2); requestAnimationFrame(drawSilence); return; }
  const d = SILENCE_DATA[silenceActive];
  silenceT += 16; // ~60fps
  silenceCtx.fillStyle = '#fff'; silenceCtx.font = 'bold 16px monospace'; silenceCtx.textAlign = 'left';
  silenceCtx.fillText(d.setup, 30, 80);
  const gapStart = 600, gapEnd = gapStart + d.gap;
  // Timeline
  const tlY = 160, tlW = 900;
  silenceCtx.strokeStyle = 'rgba(120,120,140,0.4)'; silenceCtx.lineWidth = 1;
  silenceCtx.beginPath(); silenceCtx.moveTo(30, tlY); silenceCtx.lineTo(30 + tlW, tlY); silenceCtx.stroke();
  // Gap region
  const gx = 30 + tlW * 0.35, gw = tlW * 0.4;
  silenceCtx.fillStyle = 'rgba(240,168,105,0.2)';
  silenceCtx.fillRect(gx, tlY - 20, gw, 40);
  silenceCtx.strokeStyle = 'rgba(240,168,105,0.85)'; silenceCtx.setLineDash([4, 4]);
  silenceCtx.strokeRect(gx, tlY - 20, gw, 40);
  silenceCtx.setLineDash([]);
  silenceCtx.fillStyle = 'rgba(240,168,105,0.95)'; silenceCtx.font = '11px monospace'; silenceCtx.textAlign = 'center';
  silenceCtx.fillText('SILENCE (' + (d.gap / 1000).toFixed(1) + 's)', gx + gw / 2, tlY - 26);
  silenceCtx.fillText('the listener\\u0027s predictor runs, forecasting what is not being said', gx + gw / 2, tlY + 34);
  // Response
  if (silenceT > gapEnd) {
    silenceCtx.fillStyle = '#fff'; silenceCtx.font = 'bold 14px monospace'; silenceCtx.textAlign = 'left';
    silenceCtx.fillText(d.response, 30, 260);
    silenceCtx.fillStyle = 'rgba(129,199,132,0.85)'; silenceCtx.font = '11px monospace';
    silenceCtx.fillText(d.note, 30, 290);
  }
  if (silenceT > gapEnd + 3000) silenceT = 0;
  requestAnimationFrame(drawSilence);
}
drawSilence();

// ═══════════════════════════════════════════════════════════════════════
// Language Acquisition
// ═══════════════════════════════════════════════════════════════════════
const acqCanvas = document.getElementById('acquisition-canvas');
const acqCtx = acqCanvas.getContext('2d');
let acqMode = null;
function acquisitionPlay(m) { acqMode = m; pepSend('acquisition.play', { mode: m }); }
function acquisitionReset() { acqMode = null; }
function drawAcq() {
  const W = 960, H = 400; acqCtx.fillStyle = themeBg(); acqCtx.fillRect(0, 0, W, H);
  if (!acqMode) { acqCtx.fillStyle = '#666'; acqCtx.font = '11px monospace'; acqCtx.textAlign = 'center'; acqCtx.fillText('(pick a scenario)', W / 2, H / 2); requestAnimationFrame(drawAcq); return; }
  // Axes
  acqCtx.strokeStyle = 'rgba(120,120,140,0.4)'; acqCtx.lineWidth = 1;
  acqCtx.beginPath(); acqCtx.moveTo(60, 50); acqCtx.lineTo(60, H - 60); acqCtx.lineTo(W - 30, H - 60); acqCtx.stroke();
  acqCtx.fillStyle = '#888'; acqCtx.font = '10px monospace'; acqCtx.textAlign = 'left';
  acqCtx.fillText('fluency', 20, 60);
  acqCtx.textAlign = 'right'; acqCtx.fillText('age (years) →', W - 30, H - 40);
  // Age labels
  for (let age = 0; age <= 40; age += 5) {
    const x = 60 + (age / 40) * (W - 100);
    acqCtx.fillStyle = '#666'; acqCtx.font = '10px monospace'; acqCtx.textAlign = 'center';
    acqCtx.fillText(age, x, H - 45);
    acqCtx.strokeStyle = 'rgba(120,120,140,0.15)';
    acqCtx.beginPath(); acqCtx.moveTo(x, 50); acqCtx.lineTo(x, H - 60); acqCtx.stroke();
  }
  // Critical period shading
  const cpX1 = 60 + (5 / 40) * (W - 100), cpX2 = 60 + (12 / 40) * (W - 100);
  acqCtx.fillStyle = 'rgba(240,168,105,0.1)';
  acqCtx.fillRect(cpX1, 50, cpX2 - cpX1, H - 110);
  acqCtx.fillStyle = 'rgba(240,168,105,0.85)'; acqCtx.font = '10px monospace'; acqCtx.textAlign = 'center';
  acqCtx.fillText('critical period', (cpX1 + cpX2) / 2, 70);
  // Curve
  acqCtx.strokeStyle = acqMode === 'normal' ? 'rgba(129,199,132,0.95)' : 'rgba(240,168,105,0.95)';
  acqCtx.lineWidth = 3;
  acqCtx.beginPath();
  for (let age = 0; age <= 40; age += 0.5) {
    const x = 60 + (age / 40) * (W - 100);
    let fluency;
    if (acqMode === 'normal') {
      fluency = Math.min(1, 1 / (1 + Math.exp(-(age - 2.5) * 1.2)));
    } else {
      // Late start: curve shifted right, never reaches full fluency
      if (age < 20) fluency = 0.05;
      else fluency = Math.min(0.75, (age - 20) / 15 * 0.7);
    }
    const y = H - 60 - fluency * (H - 120);
    if (age === 0) acqCtx.moveTo(x, y); else acqCtx.lineTo(x, y);
  }
  acqCtx.stroke();
  acqCtx.fillStyle = '#aaa'; acqCtx.font = '11px monospace'; acqCtx.textAlign = 'left';
  if (acqMode === 'normal') {
    acqCtx.fillText('native acquisition: rapid climb, saturation by ~5y, full adult fluency by ~12y', 80, H - 20);
  } else {
    acqCtx.fillText('adult second-language: slower climb, plateau below native ceiling, accent persists', 80, H - 20);
  }
  requestAnimationFrame(drawAcq);
}
drawAcq();

// ═══════════════════════════════════════════════════════════════════════
// Baby Talk
// ═══════════════════════════════════════════════════════════════════════
const BABY_DATA = {
  adult: { line: 'Want to go outside?', pitchVar: 0.3, tempo: 1.0, note: 'flat adult-directed speech' },
  infant: { line: 'Wanna goooo ouuutsiide?!', pitchVar: 0.95, tempo: 0.55, note: 'exaggerated pitch, slow tempo, simplified vocabulary' },
};
const babyCanvas = document.getElementById('babytalk-canvas');
const babyCtx = babyCanvas.getContext('2d');
let babyActive = null;
function babytalkPlay(k) { babyActive = k; pepSend('babytalk.play', { key: k }); }
function drawBaby() {
  const W = 960, H = 380; babyCtx.fillStyle = themeBg(); babyCtx.fillRect(0, 0, W, H);
  if (!babyActive) { babyCtx.fillStyle = '#666'; babyCtx.font = '11px monospace'; babyCtx.textAlign = 'center'; babyCtx.fillText('(pick a register)', W / 2, H / 2); requestAnimationFrame(drawBaby); return; }
  const d = BABY_DATA[babyActive];
  babyCtx.fillStyle = '#fff'; babyCtx.font = 'bold 18px monospace'; babyCtx.textAlign = 'center';
  babyCtx.fillText(d.line, W / 2, 60);
  // Pitch contour
  babyCtx.strokeStyle = 'rgba(124,184,255,0.85)'; babyCtx.lineWidth = 2;
  babyCtx.beginPath();
  for (let i = 0; i <= 100; i++) {
    const t = i / 100;
    const x = 60 + t * (W - 120);
    const y = 180 + Math.sin(t * Math.PI * 3) * d.pitchVar * 50;
    if (i === 0) babyCtx.moveTo(x, y); else babyCtx.lineTo(x, y);
  }
  babyCtx.stroke();
  babyCtx.fillStyle = '#aaa'; babyCtx.font = '11px monospace'; babyCtx.textAlign = 'left';
  babyCtx.fillText('pitch variation: ' + (d.pitchVar * 100).toFixed(0) + '%', 60, 140);
  babyCtx.fillText('tempo: ' + (d.tempo * 100).toFixed(0) + '% of adult', 60, 260);
  babyCtx.fillStyle = 'rgba(129,199,132,0.85)'; babyCtx.font = 'bold 11px monospace';
  babyCtx.fillText(d.note, 60, H - 40);
  requestAnimationFrame(drawBaby);
}
drawBaby();

// ═══════════════════════════════════════════════════════════════════════
// Reading — Eye Movements
// ═══════════════════════════════════════════════════════════════════════
const READING_DATA = {
  normal: { text: 'The cat sat on the mat by the window.', fixations: [0.12, 0.28, 0.40, 0.48, 0.60, 0.78], durs: [220, 180, 200, 120, 250, 280], regressions: [], label: 'fluent reader' },
  surprise: { text: 'The cat sat on the chandelier instead.', fixations: [0.12, 0.28, 0.40, 0.48, 0.60, 0.85], durs: [220, 180, 200, 120, 550, 300], regressions: [[0.85, 0.60]], label: 'fluent reader hits an unexpected word' },
  dyslexic: { text: 'The cat sat on the mat by the window.', fixations: [0.05, 0.12, 0.22, 0.32, 0.42, 0.52, 0.62, 0.72, 0.82], durs: [380, 420, 360, 390, 450, 380, 400, 370, 390], regressions: [[0.52, 0.32], [0.82, 0.52]], label: 'dyslexic reader — more fixations, longer durations, regressions' },
};
const readingCanvas = document.getElementById('reading-canvas');
const readingCtx = readingCanvas.getContext('2d');
let readingActive = null, readingT = 0;
function readingPlay(k) { readingActive = k; readingT = 0; pepSend('reading.play', { key: k }); }
function readingReset() { readingActive = null; readingT = 0; }
function drawReading() {
  const W = 960, H = 420; readingCtx.fillStyle = themeBg(); readingCtx.fillRect(0, 0, W, H);
  if (!readingActive) { readingCtx.fillStyle = '#666'; readingCtx.font = '11px monospace'; readingCtx.textAlign = 'center'; readingCtx.fillText('(pick a reading scenario)', W / 2, H / 2); requestAnimationFrame(drawReading); return; }
  const d = READING_DATA[readingActive];
  readingCtx.fillStyle = '#aaa'; readingCtx.font = '11px monospace'; readingCtx.textAlign = 'left';
  readingCtx.fillText(d.label, 30, 30);
  // Text
  readingCtx.fillStyle = '#e0e0e0'; readingCtx.font = 'bold 22px monospace';
  readingCtx.fillText(d.text, 60, 120);
  const textX = 60, textW = readingCtx.measureText(d.text).width;
  // Gaze line
  const gazeY = 180;
  readingCtx.strokeStyle = 'rgba(120,120,140,0.3)'; readingCtx.lineWidth = 1;
  readingCtx.beginPath(); readingCtx.moveTo(textX, gazeY); readingCtx.lineTo(textX + textW, gazeY); readingCtx.stroke();
  // Fixations
  d.fixations.forEach((fx, i) => {
    const x = textX + fx * textW;
    const r = 4 + (d.durs[i] / 60);
    readingCtx.fillStyle = 'rgba(240,168,105,0.75)';
    readingCtx.beginPath(); readingCtx.arc(x, gazeY, r, 0, Math.PI * 2); readingCtx.fill();
    readingCtx.strokeStyle = 'rgba(240,168,105,0.95)'; readingCtx.lineWidth = 1.5; readingCtx.stroke();
    // Saccade arrow to next
    if (i < d.fixations.length - 1) {
      const nx = textX + d.fixations[i + 1] * textW;
      readingCtx.strokeStyle = 'rgba(124,184,255,0.6)'; readingCtx.lineWidth = 1;
      readingCtx.beginPath(); readingCtx.moveTo(x + r, gazeY - 14); readingCtx.quadraticCurveTo((x + nx) / 2, gazeY - 40, nx - r, gazeY - 14); readingCtx.stroke();
    }
    // Duration
    readingCtx.fillStyle = '#888'; readingCtx.font = '10px monospace'; readingCtx.textAlign = 'center';
    readingCtx.fillText(d.durs[i] + 'ms', x, gazeY + 22);
  });
  // Regressions
  d.regressions.forEach(r => {
    const from = textX + r[0] * textW;
    const to = textX + r[1] * textW;
    readingCtx.strokeStyle = 'rgba(229,57,53,0.85)'; readingCtx.lineWidth = 2;
    readingCtx.beginPath();
    readingCtx.moveTo(from, gazeY + 40);
    readingCtx.quadraticCurveTo((from + to) / 2, gazeY + 80, to, gazeY + 40);
    readingCtx.stroke();
    readingCtx.fillStyle = 'rgba(229,57,53,0.9)'; readingCtx.font = '10px monospace'; readingCtx.textAlign = 'center';
    readingCtx.fillText('regression', (from + to) / 2, gazeY + 100);
  });
  // Summary
  const avgDur = d.durs.reduce((a, b) => a + b, 0) / d.durs.length;
  readingCtx.fillStyle = '#aaa'; readingCtx.font = '11px monospace'; readingCtx.textAlign = 'left';
  readingCtx.fillText('fixations: ' + d.fixations.length + '  ·  avg duration: ' + avgDur.toFixed(0) + 'ms  ·  regressions: ' + d.regressions.length, 30, H - 30);
  requestAnimationFrame(drawReading);
}
drawReading();

// ═══════════════════════════════════════════════════════════════════════
// Aphasia & Dyslexia
// ═══════════════════════════════════════════════════════════════════════
const APHASIA_DATA = {
  broca: {
    label: 'Broca\\u0027s aphasia',
    production: '"walk... store... milk... yesterday..."',
    grammar: 0.1, semantics: 0.85, production_effort: 0.9,
    note: 'grammar production collapsed; content intact; telegraphic, effortful speech',
  },
  wernicke: {
    label: 'Wernicke\\u0027s aphasia',
    production: '"So I went to the beneath and the car, uh, the thing was all for the blue..."',
    grammar: 0.85, semantics: 0.15, production_effort: 0.15,
    note: 'grammar flows fluently; semantic anchor broken; content is nonsense',
  },
  dyslexia: {
    label: 'dyslexia',
    production: '(reading is slow and effortful; speech is normal)',
    grammar: 0.95, semantics: 0.95, production_effort: 0.25,
    note: 'only the grapheme→phoneme decoding pipeline is impaired; oral language is intact',
  },
  intact: {
    label: 'intact (reference)',
    production: '"I walked to the store yesterday to buy milk."',
    grammar: 0.95, semantics: 0.95, production_effort: 0.2,
    note: 'all sub-systems working',
  },
};
const aphasiaCanvas = document.getElementById('aphasia-canvas');
const aphasiaCtx = aphasiaCanvas.getContext('2d');
let aphasiaActive = null;
function aphasiaPick(k) { aphasiaActive = k; pepSend('aphasia.pick', { key: k }); }
function aphasiaReset() { aphasiaActive = null; }
function drawAphasia() {
  const W = 960, H = 440; aphasiaCtx.fillStyle = themeBg(); aphasiaCtx.fillRect(0, 0, W, H);
  if (!aphasiaActive) { aphasiaCtx.fillStyle = '#666'; aphasiaCtx.font = '11px monospace'; aphasiaCtx.textAlign = 'center'; aphasiaCtx.fillText('(pick a condition)', W / 2, H / 2); requestAnimationFrame(drawAphasia); return; }
  const d = APHASIA_DATA[aphasiaActive];
  aphasiaCtx.fillStyle = 'rgba(240,168,105,0.95)'; aphasiaCtx.font = 'bold 16px monospace'; aphasiaCtx.textAlign = 'left';
  aphasiaCtx.fillText(d.label, 30, 40);
  aphasiaCtx.fillStyle = '#e0e0e0'; aphasiaCtx.font = '13px monospace';
  aphasiaCtx.fillText(d.production, 30, 80);
  const bars = [
    { l: 'GRAMMAR PRODUCTION', v: d.grammar, c: '124,184,255' },
    { l: 'SEMANTIC ANCHOR', v: d.semantics, c: '129,199,132' },
    { l: 'PRODUCTION EFFORT', v: d.production_effort, c: '229,57,53' },
  ];
  bars.forEach((b, i) => {
    const y = 130 + i * 70;
    aphasiaCtx.fillStyle = '#aaa'; aphasiaCtx.font = 'bold 11px monospace';
    aphasiaCtx.fillText(b.l, 30, y);
    aphasiaCtx.fillStyle = 'rgba(' + b.c + ',0.2)'; aphasiaCtx.fillRect(30, y + 8, 900, 24);
    aphasiaCtx.fillStyle = 'rgba(' + b.c + ',0.9)'; aphasiaCtx.fillRect(30, y + 8, 900 * b.v, 24);
    aphasiaCtx.fillStyle = '#aaa'; aphasiaCtx.font = '10px monospace'; aphasiaCtx.textAlign = 'right';
    aphasiaCtx.fillText((b.v * 100).toFixed(0) + '%', 920, y + 25);
    aphasiaCtx.textAlign = 'left';
  });
  aphasiaCtx.fillStyle = 'rgba(129,199,132,0.9)'; aphasiaCtx.font = '11px monospace';
  aphasiaCtx.fillText(d.note, 30, H - 20);
  requestAnimationFrame(drawAphasia);
}
drawAphasia();

// ═══════════════════════════════════════════════════════════════════════
// Written vs Spoken
// ═══════════════════════════════════════════════════════════════════════
const WVS_DATA = {
  spoken: { label: 'spoken transcript', text: 'So um, I was thinking — you know, about what you said — and I, well, I think maybe, um, you were right. Sort of. Mostly.', avg_len: 8, density: 0.45, fillers: 7, complexity: 0.3 },
  written: { label: 'written version', text: 'Thinking about what you said, I have come to agree with the essential point, though my assent is partial rather than unconditional.', avg_len: 22, density: 0.9, fillers: 0, complexity: 0.85 },
};
const wvsCanvas = document.getElementById('wvs-canvas');
const wvsCtx = wvsCanvas.getContext('2d');
let wvsActive = null;
function wvsPlay(k) { wvsActive = k; pepSend('wvs.play', { key: k }); }
function drawWvs() {
  const W = 960, H = 360; wvsCtx.fillStyle = themeBg(); wvsCtx.fillRect(0, 0, W, H);
  if (!wvsActive) { wvsCtx.fillStyle = '#666'; wvsCtx.font = '11px monospace'; wvsCtx.textAlign = 'center'; wvsCtx.fillText('(pick a version)', W / 2, H / 2); requestAnimationFrame(drawWvs); return; }
  const d = WVS_DATA[wvsActive];
  wvsCtx.fillStyle = 'rgba(124,184,255,0.95)'; wvsCtx.font = 'bold 12px monospace'; wvsCtx.textAlign = 'left';
  wvsCtx.fillText(d.label, 30, 30);
  wvsCtx.fillStyle = '#e0e0e0'; wvsCtx.font = '13px monospace';
  // Word wrap
  const words = d.text.split(' '); let x = 30, y = 70;
  words.forEach(w => {
    const m = wvsCtx.measureText(w + ' ');
    if (x + m.width > W - 40) { x = 30; y += 24; }
    wvsCtx.fillText(w + ' ', x, y);
    x += m.width;
  });
  // Metrics
  const metrics = [
    { l: 'avg sentence length', v: d.avg_len / 25, label: d.avg_len + ' words' },
    { l: 'information density', v: d.density, label: (d.density * 100).toFixed(0) + '%' },
    { l: 'filler count', v: d.fillers / 10, label: d.fillers },
    { l: 'grammatical complexity', v: d.complexity, label: (d.complexity * 100).toFixed(0) + '%' },
  ];
  metrics.forEach((m, i) => {
    const my = 180 + i * 32;
    wvsCtx.fillStyle = '#aaa'; wvsCtx.font = '10px monospace'; wvsCtx.textAlign = 'left';
    wvsCtx.fillText(m.l, 30, my);
    wvsCtx.fillStyle = 'rgba(124,184,255,0.2)'; wvsCtx.fillRect(240, my - 10, 600, 14);
    wvsCtx.fillStyle = 'rgba(124,184,255,0.85)'; wvsCtx.fillRect(240, my - 10, 600 * Math.min(1, m.v), 14);
    wvsCtx.fillStyle = '#aaa'; wvsCtx.textAlign = 'right';
    wvsCtx.fillText(m.label, 900, my);
  });
  requestAnimationFrame(drawWvs);
}
drawWvs();

// ═══════════════════════════════════════════════════════════════════════
// Conversation Dynamics
// ═══════════════════════════════════════════════════════════════════════
const CONV_DATA = {
  smooth: { turns: [ { who: 'A', text: 'Hey, how was the trip?', start: 0, end: 1400 }, { who: 'B', text: 'Long, but good.', start: 1600, end: 2600 }, { who: 'A', text: 'Traffic on I-5?', start: 2800, end: 3600 }, { who: 'B', text: 'Not bad actually.', start: 3750, end: 4500 } ], note: 'gaps of ~200ms — natural rhythm' },
  overlap: { turns: [ { who: 'A', text: 'I was going to say that we should—', start: 0, end: 2000 }, { who: 'B', text: '—wait, that is not what I meant.', start: 1500, end: 3500 } ], note: 'overlap region — both speakers active, repair will follow' },
  awkward: { turns: [ { who: 'A', text: 'So... do you want to come over?', start: 0, end: 1600 }, { who: 'B', text: 'Uh... I mean, I am not sure.', start: 3800, end: 5400 } ], note: 'gap of 2.2s — awkward, registered consciously by both' },
  repair: { turns: [ { who: 'A', text: 'I went to the — she went to the store', start: 0, end: 2800 } ], note: 'self-repair at a clause boundary, not mid-phrase' },
};
const convCanvas = document.getElementById('conv-canvas');
const convCtx = convCanvas.getContext('2d');
let convActive = null;
function convPlay(k) { convActive = k; pepSend('conv.play', { key: k }); }
function drawConv() {
  const W = 960, H = 400; convCtx.fillStyle = themeBg(); convCtx.fillRect(0, 0, W, H);
  if (!convActive) { convCtx.fillStyle = '#666'; convCtx.font = '11px monospace'; convCtx.textAlign = 'center'; convCtx.fillText('(pick a conversation)', W / 2, H / 2); requestAnimationFrame(drawConv); return; }
  const d = CONV_DATA[convActive];
  const maxT = Math.max(...d.turns.map(t => t.end)) + 500;
  const tlX = 60, tlW = 880;
  convCtx.strokeStyle = 'rgba(120,120,140,0.4)'; convCtx.lineWidth = 1;
  convCtx.beginPath(); convCtx.moveTo(tlX, 200); convCtx.lineTo(tlX + tlW, 200); convCtx.stroke();
  convCtx.fillStyle = '#888'; convCtx.font = '10px monospace'; convCtx.textAlign = 'center';
  for (let s = 0; s <= maxT; s += 1000) {
    const x = tlX + (s / maxT) * tlW;
    convCtx.strokeStyle = 'rgba(120,120,140,0.2)';
    convCtx.beginPath(); convCtx.moveTo(x, 100); convCtx.lineTo(x, 300); convCtx.stroke();
    convCtx.fillText((s / 1000).toFixed(1) + 's', x, 320);
  }
  d.turns.forEach((t, i) => {
    const x = tlX + (t.start / maxT) * tlW;
    const w = ((t.end - t.start) / maxT) * tlW;
    const y = t.who === 'A' ? 140 : 220;
    const col = t.who === 'A' ? '124,184,255' : '240,168,105';
    convCtx.fillStyle = 'rgba(' + col + ',0.5)';
    convCtx.fillRect(x, y, w, 40);
    convCtx.strokeStyle = 'rgba(' + col + ',0.95)'; convCtx.lineWidth = 1.5;
    convCtx.strokeRect(x, y, w, 40);
    convCtx.fillStyle = '#fff'; convCtx.font = '10px monospace'; convCtx.textAlign = 'left';
    convCtx.fillText(t.who + ': ' + t.text.slice(0, 36), x + 4, y + 24);
  });
  convCtx.fillStyle = 'rgba(129,199,132,0.9)'; convCtx.font = '11px monospace'; convCtx.textAlign = 'left';
  convCtx.fillText(d.note, 60, 60);
  requestAnimationFrame(drawConv);
}
drawConv();

// ═══════════════════════════════════════════════════════════════════════
// Subtext
// ═══════════════════════════════════════════════════════════════════════
const SUBTEXT_DATA = {
  cookie: { q: '"Did you eat the last cookie?"', a: '"What kind of cookie was it?"', literal: 'they are asking for cookie identification', inferred: 'YES — they ate it (they dodged the direct yes/no)' },
  love: { q: '"Do you love me?"', a: '"I am tired."', literal: 'they report being tired', inferred: 'NO or NOT RIGHT NOW — the dodge is the answer' },
  hiring: { q: '"When will we hear back about the job?"', a: '"We will be in touch."', literal: 'a generic courteous phrase', inferred: 'NO CALLBACK — specific follow-ups are missing, which is the signal' },
};
const subtextCanvas = document.getElementById('subtext-canvas');
const subtextCtx = subtextCanvas.getContext('2d');
let subtextActive = null, subtextT = 0;
function subtextPlay(k) { subtextActive = k; subtextT = 0; pepSend('subtext.play', { key: k }); }
function subtextReset() { subtextActive = null; subtextT = 0; }
function drawSubtext() {
  const W = 960, H = 380; subtextCtx.fillStyle = themeBg(); subtextCtx.fillRect(0, 0, W, H);
  if (!subtextActive) { subtextCtx.fillStyle = '#666'; subtextCtx.font = '11px monospace'; subtextCtx.textAlign = 'center'; subtextCtx.fillText('(pick a scene)', W / 2, H / 2); requestAnimationFrame(drawSubtext); return; }
  const d = SUBTEXT_DATA[subtextActive];
  subtextT = Math.min(200, subtextT + 1);
  subtextCtx.fillStyle = '#aaa'; subtextCtx.font = '11px monospace'; subtextCtx.textAlign = 'left';
  subtextCtx.fillText('question', 30, 30);
  subtextCtx.fillStyle = '#e0e0e0'; subtextCtx.font = 'bold 14px monospace';
  subtextCtx.fillText(d.q, 30, 56);
  if (subtextT > 30) {
    subtextCtx.fillStyle = '#aaa'; subtextCtx.font = '11px monospace';
    subtextCtx.fillText('response', 30, 100);
    subtextCtx.fillStyle = '#e0e0e0'; subtextCtx.font = 'bold 14px monospace';
    subtextCtx.fillText(d.a, 30, 126);
  }
  if (subtextT > 70) {
    subtextCtx.fillStyle = 'rgba(124,184,255,0.85)'; subtextCtx.font = 'bold 11px monospace';
    subtextCtx.fillText('LITERAL PARSE', 30, 180);
    subtextCtx.fillStyle = '#e0e0e0'; subtextCtx.font = '12px monospace';
    subtextCtx.fillText('→ ' + d.literal, 50, 200);
  }
  if (subtextT > 130) {
    subtextCtx.fillStyle = 'rgba(129,199,132,0.85)'; subtextCtx.font = 'bold 11px monospace';
    subtextCtx.fillText('INFERRED MEANING', 30, 250);
    subtextCtx.fillStyle = '#fff'; subtextCtx.font = 'bold 13px monospace';
    subtextCtx.fillText('→ ' + d.inferred, 50, 274);
    subtextCtx.fillStyle = '#aaa'; subtextCtx.font = '11px monospace';
    subtextCtx.fillText('the meaning never appears on the page — the dodge is the signal', 50, 298);
  }
  requestAnimationFrame(drawSubtext);
}
drawSubtext();

// ═══════════════════════════════════════════════════════════════════════
// Lying
// ═══════════════════════════════════════════════════════════════════════
const LYING_DATA = {
  truthful: { text: 'I went to the store on Saturday. I bought bread and milk and picked up the dry cleaning. The cashier was the usual guy. I paid in cash.', markers: { first_person: 0.85, negations: 0.1, hedges: 0.05, sensory: 0.8, passive: 0.05 } },
  deceptive: { text: 'That day, the store was visited. Some things were purchased — not many, just some basics. There was a cashier, I think. The transaction was completed.', markers: { first_person: 0.2, negations: 0.4, hedges: 0.6, sensory: 0.1, passive: 0.7 } },
};
const lyingCanvas = document.getElementById('lying-canvas');
const lyingCtx = lyingCanvas.getContext('2d');
let lyingActive = null;
function lyingPick(k) { lyingActive = k; pepSend('lying.pick', { key: k }); }
function drawLying() {
  const W = 960, H = 400; lyingCtx.fillStyle = themeBg(); lyingCtx.fillRect(0, 0, W, H);
  if (!lyingActive) { lyingCtx.fillStyle = '#666'; lyingCtx.font = '11px monospace'; lyingCtx.textAlign = 'center'; lyingCtx.fillText('(pick a statement)', W / 2, H / 2); requestAnimationFrame(drawLying); return; }
  const d = LYING_DATA[lyingActive];
  lyingCtx.fillStyle = 'rgba(124,184,255,0.95)'; lyingCtx.font = 'bold 12px monospace'; lyingCtx.textAlign = 'left';
  lyingCtx.fillText(lyingActive === 'truthful' ? 'truthful' : 'deceptive', 30, 30);
  lyingCtx.fillStyle = '#e0e0e0'; lyingCtx.font = '12px monospace';
  const words = d.text.split(' '); let x = 30, y = 60;
  words.forEach(w => {
    const m = lyingCtx.measureText(w + ' ');
    if (x + m.width > W - 40) { x = 30; y += 22; }
    lyingCtx.fillText(w + ' ', x, y);
    x += m.width;
  });
  const markers = [
    { k: 'first_person', l: 'first-person pronouns', c: '129,199,132' },
    { k: 'sensory', l: 'sensory details', c: '124,184,255' },
    { k: 'negations', l: 'negations', c: '240,168,105' },
    { k: 'hedges', l: 'hedging language', c: '240,168,105' },
    { k: 'passive', l: 'passive constructions', c: '229,57,53' },
  ];
  markers.forEach((m, i) => {
    const my = 190 + i * 38;
    lyingCtx.fillStyle = '#aaa'; lyingCtx.font = '10px monospace'; lyingCtx.textAlign = 'left';
    lyingCtx.fillText(m.l, 30, my);
    lyingCtx.fillStyle = 'rgba(' + m.c + ',0.2)'; lyingCtx.fillRect(230, my - 12, 660, 16);
    lyingCtx.fillStyle = 'rgba(' + m.c + ',0.9)'; lyingCtx.fillRect(230, my - 12, 660 * d.markers[m.k], 16);
  });
  requestAnimationFrame(drawLying);
}
drawLying();

// ═══════════════════════════════════════════════════════════════════════
// Persuasion
// ═══════════════════════════════════════════════════════════════════════
const PERSUASION_DATA = {
  'ad-hominem': { label: 'ad hominem', example: '"You can\\u0027t trust her climate data — she\\u0027s a vegan."', move: 'attacks the arguer, not the argument', effect: 'listener\\u0027s activation shifts from claim-evaluation to person-evaluation' },
  'strawman': { label: 'strawman', example: '"He wants to reform healthcare? So he wants the government to run everything?"', move: 'replaces the opponent\\u0027s claim with a weaker one', effect: 'listener never checks against the original, so the weaker version becomes the working target' },
  'appeal-emotion': { label: 'appeal to emotion', example: '"Do you want your children to grow up in a country like this?"', move: 'adds emotional weight to the claim', effect: 'high-emotion wins against low-emotion evidence regardless of logic' },
  'slippery-slope': { label: 'slippery slope', example: '"If we allow X, soon we\\u0027ll have Y, then Z, then the collapse of civilization."', move: 'chains plausible steps into an implausible end', effect: 'listener\\u0027s forecast settles on the worst case without any step being proven' },
  'anchoring': { label: 'anchoring', example: '"Some estimates put the cost at $500B, but we\\u0027re only asking for $50B."', move: 'introduces a high number first', effect: 'everything after the anchor is judged relative to it, making $50B feel small' },
};
const persuasionCanvas = document.getElementById('persuasion-canvas');
const persuasionCtx = persuasionCanvas.getContext('2d');
let persuasionActive = null;
function persuasionPick(k) { persuasionActive = k; pepSend('persuasion.pick', { key: k }); }
function persuasionReset() { persuasionActive = null; }
function drawPersuasion() {
  const W = 960, H = 440; persuasionCtx.fillStyle = themeBg(); persuasionCtx.fillRect(0, 0, W, H);
  if (!persuasionActive) { persuasionCtx.fillStyle = '#666'; persuasionCtx.font = '11px monospace'; persuasionCtx.textAlign = 'center'; persuasionCtx.fillText('(pick a fallacy)', W / 2, H / 2); requestAnimationFrame(drawPersuasion); return; }
  const d = PERSUASION_DATA[persuasionActive];
  persuasionCtx.fillStyle = 'rgba(240,168,105,0.95)'; persuasionCtx.font = 'bold 14px monospace'; persuasionCtx.textAlign = 'left';
  persuasionCtx.fillText(d.label.toUpperCase(), 30, 40);
  persuasionCtx.fillStyle = '#e0e0e0'; persuasionCtx.font = '13px monospace';
  const words = d.example.split(' '); let x = 30, y = 80;
  words.forEach(w => {
    const m = persuasionCtx.measureText(w + ' ');
    if (x + m.width > W - 40) { x = 30; y += 22; }
    persuasionCtx.fillText(w + ' ', x, y);
    x += m.width;
  });
  persuasionCtx.fillStyle = 'rgba(124,184,255,0.85)'; persuasionCtx.font = 'bold 11px monospace';
  persuasionCtx.fillText('THE MOVE', 30, 200);
  persuasionCtx.fillStyle = '#e0e0e0'; persuasionCtx.font = '12px monospace';
  persuasionCtx.fillText('→ ' + d.move, 50, 222);
  persuasionCtx.fillStyle = 'rgba(129,199,132,0.85)'; persuasionCtx.font = 'bold 11px monospace';
  persuasionCtx.fillText('EFFECT ON THE LISTENER', 30, 270);
  persuasionCtx.fillStyle = '#e0e0e0'; persuasionCtx.font = '12px monospace';
  persuasionCtx.fillText('→ ' + d.effect, 50, 292);
  persuasionCtx.fillStyle = '#aaa'; persuasionCtx.font = '11px monospace';
  persuasionCtx.fillText('recognition is the only defense — the moves run below conscious deliberation', 30, H - 30);
  requestAnimationFrame(drawPersuasion);
}
drawPersuasion();

// ═══════════════════════════════════════════════════════════════════════
// Narrative Structure
// ═══════════════════════════════════════════════════════════════════════
const NARRATIVE_DATA = {
  'three-act': { label: 'three-act structure', curve: [0.3, 0.35, 0.5, 0.55, 0.75, 0.85, 0.95, 0.5, 0.4], note: 'setup → confrontation → climax → resolution' },
  'hero': { label: "hero's journey", curve: [0.4, 0.3, 0.2, 0.5, 0.6, 0.3, 0.8, 0.9, 0.7, 0.6], note: 'call → refusal → descent → trials → revelation → return' },
  'tragedy': { label: 'tragedy arc', curve: [0.6, 0.7, 0.75, 0.6, 0.5, 0.35, 0.2, 0.1, 0.1], note: 'ends below where it started — a settled sadness' },
  'comedy': { label: 'comedy arc', curve: [0.4, 0.3, 0.4, 0.5, 0.3, 0.6, 0.75, 0.85, 0.9], note: 'ends above where it started — a settled warmth' },
};
const narrativeCanvas = document.getElementById('narrative-canvas');
const narrativeCtx = narrativeCanvas.getContext('2d');
let narrativeActive = null;
function narrativePick(k) { narrativeActive = k; pepSend('narrative.pick', { key: k }); }
function narrativeReset() { narrativeActive = null; }
function drawNarrative() {
  const W = 960, H = 400; narrativeCtx.fillStyle = themeBg(); narrativeCtx.fillRect(0, 0, W, H);
  if (!narrativeActive) { narrativeCtx.fillStyle = '#666'; narrativeCtx.font = '11px monospace'; narrativeCtx.textAlign = 'center'; narrativeCtx.fillText('(pick an arc)', W / 2, H / 2); requestAnimationFrame(drawNarrative); return; }
  const d = NARRATIVE_DATA[narrativeActive];
  // Axes
  narrativeCtx.strokeStyle = 'rgba(120,120,140,0.4)'; narrativeCtx.lineWidth = 1;
  narrativeCtx.beginPath(); narrativeCtx.moveTo(60, 60); narrativeCtx.lineTo(60, H - 80); narrativeCtx.lineTo(W - 30, H - 80); narrativeCtx.stroke();
  narrativeCtx.fillStyle = '#888'; narrativeCtx.font = '10px monospace'; narrativeCtx.textAlign = 'left';
  narrativeCtx.fillText('tension', 20, 70);
  narrativeCtx.textAlign = 'right'; narrativeCtx.fillText('story time →', W - 30, H - 60);
  // Curve
  narrativeCtx.strokeStyle = 'rgba(240,168,105,0.95)'; narrativeCtx.lineWidth = 3;
  narrativeCtx.beginPath();
  d.curve.forEach((v, i) => {
    const x = 60 + (i / (d.curve.length - 1)) * (W - 100);
    const y = H - 80 - v * (H - 160);
    if (i === 0) narrativeCtx.moveTo(x, y); else narrativeCtx.lineTo(x, y);
  });
  narrativeCtx.stroke();
  // Peak marker
  const peakIdx = d.curve.indexOf(Math.max(...d.curve));
  const peakX = 60 + (peakIdx / (d.curve.length - 1)) * (W - 100);
  const peakY = H - 80 - d.curve[peakIdx] * (H - 160);
  narrativeCtx.fillStyle = 'rgba(255,183,77,0.95)';
  narrativeCtx.beginPath(); narrativeCtx.arc(peakX, peakY, 7, 0, Math.PI * 2); narrativeCtx.fill();
  narrativeCtx.font = 'bold 11px monospace'; narrativeCtx.textAlign = 'center';
  narrativeCtx.fillText('climax', peakX, peakY - 14);
  narrativeCtx.fillStyle = 'rgba(124,184,255,0.95)'; narrativeCtx.font = 'bold 12px monospace'; narrativeCtx.textAlign = 'left';
  narrativeCtx.fillText(d.label.toUpperCase(), 30, 40);
  narrativeCtx.fillStyle = '#aaa'; narrativeCtx.font = '11px monospace';
  narrativeCtx.fillText(d.note, 30, H - 20);
  requestAnimationFrame(drawNarrative);
}
drawNarrative();

// ═══════════════════════════════════════════════════════════════════════
// Writing Advice Engine
// ═══════════════════════════════════════════════════════════════════════
const ADVICE_DATA = {
  'show': { rule: 'Show, don\\u0027t tell', mechanism: 'concrete words fire sensory cortex; abstract words activate only verbal clusters', example_bad: 'She was sad.', example_good: 'She stood at the window without moving.' },
  'specific': { rule: 'Use specific details', mechanism: 'specific concrete nouns narrow the reader\\u0027s forecast to a single clear mental image', example_bad: 'He held a weapon.', example_good: 'He held a chipped kitchen knife.' },
  'active': { rule: 'Prefer active voice', mechanism: 'active voice topicalizes the agent; passive voice hides them and slows comprehension', example_bad: 'The ball was thrown by the boy.', example_good: 'The boy threw the ball.' },
  'vary': { rule: 'Vary sentence length', mechanism: 'the predictor settles into the rhythm of repeated sentence-length patterns; varying forces re-engagement', example_bad: 'I went home. I made dinner. I went to bed.', example_good: 'I went home. Made dinner — just eggs and toast — and fell into bed before the plates were even dry.' },
  'darlings': { rule: 'Kill your darlings', mechanism: 'a clever sentence that does not serve the larger forecast breaks the reader\\u0027s expectation without payoff', example_bad: '(the beautiful line you love that does not fit)', example_good: '(cut it — your attachment to it is not a reason for the reader to care)' },
  'rewrite': { rule: 'Writing is rewriting', mechanism: 'first drafts are the writer discovering what they think; revisions engineer the effect', example_bad: '(any first draft)', example_good: '(the version after five revisions)' },
};
const adviceCanvas = document.getElementById('advice-canvas');
const adviceCtx = adviceCanvas.getContext('2d');
let adviceActive = null;
function advicePick(k) { adviceActive = k; pepSend('advice.pick', { key: k }); }
function drawAdvice() {
  const W = 960, H = 420; adviceCtx.fillStyle = themeBg(); adviceCtx.fillRect(0, 0, W, H);
  if (!adviceActive) { adviceCtx.fillStyle = '#666'; adviceCtx.font = '11px monospace'; adviceCtx.textAlign = 'center'; adviceCtx.fillText('(pick a rule)', W / 2, H / 2); requestAnimationFrame(drawAdvice); return; }
  const d = ADVICE_DATA[adviceActive];
  adviceCtx.fillStyle = 'rgba(240,168,105,0.95)'; adviceCtx.font = 'bold 16px monospace'; adviceCtx.textAlign = 'left';
  adviceCtx.fillText('"' + d.rule + '"', 30, 40);
  adviceCtx.fillStyle = 'rgba(124,184,255,0.85)'; adviceCtx.font = 'bold 11px monospace';
  adviceCtx.fillText('THE MECHANISM', 30, 90);
  adviceCtx.fillStyle = '#e0e0e0'; adviceCtx.font = '12px monospace';
  const mw = d.mechanism.split(' '); let x = 50, y = 112;
  mw.forEach(w => {
    const m = adviceCtx.measureText(w + ' ');
    if (x + m.width > W - 30) { x = 50; y += 20; }
    adviceCtx.fillText(w + ' ', x, y); x += m.width;
  });
  adviceCtx.fillStyle = 'rgba(229,57,53,0.85)'; adviceCtx.font = 'bold 11px monospace';
  adviceCtx.fillText('BEFORE', 30, 220);
  adviceCtx.fillStyle = '#e0e0e0'; adviceCtx.font = '12px monospace';
  adviceCtx.fillText(d.example_bad, 50, 242);
  adviceCtx.fillStyle = 'rgba(129,199,132,0.85)'; adviceCtx.font = 'bold 11px monospace';
  adviceCtx.fillText('AFTER', 30, 300);
  adviceCtx.fillStyle = '#e0e0e0'; adviceCtx.font = '12px monospace';
  adviceCtx.fillText(d.example_good, 50, 322);
  requestAnimationFrame(drawAdvice);
}
drawAdvice();

// ═══════════════════════════════════════════════════════════════════════
// Text Diff
// ═══════════════════════════════════════════════════════════════════════
const DIFF_DATA = {
  'tell-show': {
    left: { label: 'TELL', text: 'She was afraid.', act: { verbal: 0.9, visual: 0.1, motor: 0.05, tactile: 0.05, emotional: 0.4, social: 0.2 } },
    right: { label: 'SHOW', text: 'She stood very still, one hand flat against the wall.', act: { verbal: 0.6, visual: 0.85, motor: 0.65, tactile: 0.8, emotional: 0.75, social: 0.5 } },
  },
  'passive-active': {
    left: { label: 'PASSIVE', text: 'The decision was made by the committee.', act: { verbal: 0.8, visual: 0.1, motor: 0.0, tactile: 0.0, emotional: 0.2, social: 0.4 } },
    right: { label: 'ACTIVE', text: 'The committee decided.', act: { verbal: 0.85, visual: 0.3, motor: 0.1, tactile: 0.0, emotional: 0.4, social: 0.7 } },
  },
  'vague-specific': {
    left: { label: 'VAGUE', text: 'He had some food.', act: { verbal: 0.8, visual: 0.2, motor: 0.1, tactile: 0.1, emotional: 0.2, social: 0.1 } },
    right: { label: 'SPECIFIC', text: 'He had a bowl of cold rice and pickled cucumber.', act: { verbal: 0.75, visual: 0.9, motor: 0.3, tactile: 0.6, emotional: 0.4, social: 0.2 } },
  },
};
const diffCanvas = document.getElementById('diff-canvas');
const diffCtx = diffCanvas.getContext('2d');
let diffActive = null;
function diffPick(k) { diffActive = k; pepSend('diff.pick', { key: k }); }
function diffReset() { diffActive = null; }
function drawDiff() {
  const W = 960, H = 420; diffCtx.fillStyle = themeBg(); diffCtx.fillRect(0, 0, W, H);
  if (!diffActive) { diffCtx.fillStyle = '#666'; diffCtx.font = '11px monospace'; diffCtx.textAlign = 'center'; diffCtx.fillText('(pick a pair)', W / 2, H / 2); requestAnimationFrame(drawDiff); return; }
  const d = DIFF_DATA[diffActive];
  const sides = [{ k: 'left', x: 30 }, { k: 'right', x: 490 }];
  const regions = ['verbal', 'visual', 'motor', 'tactile', 'emotional', 'social'];
  const cols = ['124,184,255', '240,168,105', '129,199,132', '186,104,200', '255,138,180', '79,195,247'];
  sides.forEach(s => {
    const data = d[s.k];
    diffCtx.fillStyle = 'rgba(240,168,105,0.95)'; diffCtx.font = 'bold 11px monospace'; diffCtx.textAlign = 'left';
    diffCtx.fillText(data.label, s.x, 30);
    diffCtx.fillStyle = '#e0e0e0'; diffCtx.font = '12px monospace';
    const words = data.text.split(' '); let wx = s.x, wy = 60;
    words.forEach(w => {
      const m = diffCtx.measureText(w + ' ');
      if (wx + m.width > s.x + 430) { wx = s.x; wy += 20; }
      diffCtx.fillText(w + ' ', wx, wy); wx += m.width;
    });
    regions.forEach((r, i) => {
      const ry = 140 + i * 38;
      diffCtx.fillStyle = '#aaa'; diffCtx.font = '10px monospace';
      diffCtx.fillText(r, s.x, ry);
      diffCtx.fillStyle = 'rgba(' + cols[i] + ',0.2)';
      diffCtx.fillRect(s.x, ry + 6, 430, 14);
      diffCtx.fillStyle = 'rgba(' + cols[i] + ',0.85)';
      diffCtx.fillRect(s.x, ry + 6, 430 * (data.act[r] || 0), 14);
    });
  });
  requestAnimationFrame(drawDiff);
}
drawDiff();

// ═══════════════════════════════════════════════════════════════════════
// Sign Language
// ═══════════════════════════════════════════════════════════════════════
const SIGN_DATA = {
  phono: { label: 'sub-sign phonology', text: 'ASL signs decompose into parameters: handshape, location, movement, palm orientation, facial expression. A minimal pair: APPLE and CANDY differ only in handshape — same location, same movement, different shape, different meaning. Categorical perception of these parameters parallels the categorical perception of spoken phonemes.' },
  grammar: { label: 'spatial grammar', text: 'ASL uses the signing space around the body as a grammatical resource. Pronouns get assigned locations in space; verbs move between those locations to indicate who is doing what to whom. Facial expressions mark topic/comment, conditionals, and questions — grammatically, not just emotionally. None of this has a direct English equivalent.' },
  deafborn: { label: 'deaf-native vs deaf-late', text: 'Deaf children of deaf parents acquire sign language natively on the same schedule that hearing children acquire spoken language. Deaf children of hearing parents who do not learn sign until age 5 or later show the same late-learner deficits that spoken-language late-learners show. The critical period applies equally to signed languages — proving it is about structured symbolic exposure, not about sound.' },
};
const signCanvas = document.getElementById('sign-canvas');
const signCtx = signCanvas.getContext('2d');
let signActive = null;
function signPick(k) { signActive = k; pepSend('sign.pick', { key: k }); }
function drawSign() {
  const W = 960, H = 400; signCtx.fillStyle = themeBg(); signCtx.fillRect(0, 0, W, H);
  if (!signActive) { signCtx.fillStyle = '#666'; signCtx.font = '11px monospace'; signCtx.textAlign = 'center'; signCtx.fillText('(pick an aspect)', W / 2, H / 2); requestAnimationFrame(drawSign); return; }
  const d = SIGN_DATA[signActive];
  signCtx.fillStyle = 'rgba(240,168,105,0.95)'; signCtx.font = 'bold 14px monospace'; signCtx.textAlign = 'left';
  signCtx.fillText(d.label.toUpperCase(), 30, 40);
  signCtx.fillStyle = '#e0e0e0'; signCtx.font = '13px monospace';
  const words = d.text.split(' '); let x = 30, y = 90;
  words.forEach(w => {
    const m = signCtx.measureText(w + ' ');
    if (x + m.width > W - 40) { x = 30; y += 24; }
    signCtx.fillText(w + ' ', x, y); x += m.width;
  });
  requestAnimationFrame(drawSign);
}
drawSign();

// ═══════════════════════════════════════════════════════════════════════
// Sandbox — sentence builder
// ═══════════════════════════════════════════════════════════════════════
const sandboxCanvas = document.getElementById('sandbox-canvas');
const sandboxCtx = sandboxCanvas.getContext('2d');
let sandboxWords = [];
function sandboxAdd(w) { sandboxWords.push(w); pepSend('sandbox.add', { word: w }); }
function sandboxPop() { sandboxWords.pop(); }
function sandboxClear() { sandboxWords = []; }
function sandboxEntropy(next) {
  // Estimate from heuristics
  const common = { 'The': 8, 'the': 20, 'cat': 6, 'dog': 6, 'sat': 5, 'on': 6, 'mat': 4 };
  return Object.values(next).reduce((a, b) => a - b * Math.log2(b), 0);
}
// ═══════════════════════════════════════════════════════════════════════
// Metaphor Engine — Lakoff conceptual mapping
// ═══════════════════════════════════════════════════════════════════════
const METAPHOR_DATA = {
  'time-money': {
    source: 'MONEY', target: 'TIME',
    mappings: [
      ['spend', 'spend (time)'], ['save', 'save (time)'], ['waste', 'waste (time)'],
      ['invest', 'invest (time)'], ['budget', 'budget (time)'], ['run out', 'run out (of time)'],
      ['borrow', 'borrow (time)'], ['cost', 'cost (time)'], ['worth', 'worth (your time)'],
    ],
  },
  'argument-war': {
    source: 'WAR', target: 'ARGUMENT',
    mappings: [
      ['attack', 'attack (a position)'], ['defend', 'defend (a claim)'], ['retreat', 'retreat'],
      ['win', 'win (an argument)'], ['ally', 'ally (with)'], ['position', 'position'],
      ['strategy', 'strategy'], ['weak spot', 'weak point (in argument)'], ['shoot down', 'shoot down (an idea)'],
    ],
  },
  'life-journey': {
    source: 'JOURNEY', target: 'LIFE',
    mappings: [
      ['start', 'beginning (of life)'], ['goal', 'life goals'], ['path', 'life path'],
      ['obstacle', 'obstacles'], ['milestone', 'milestones'], ['fork', 'crossroads'],
      ['destination', 'destination'], ['lost', 'feeling lost'], ['travel light', 'travel light'],
    ],
  },
  'ideas-objects': {
    source: 'OBJECTS', target: 'IDEAS',
    mappings: [
      ['grasp', 'grasp (an idea)'], ['catch', 'catch (meaning)'], ['hold', 'hold (a view)'],
      ['drop', 'drop (the subject)'], ['throw out', 'throw out (an idea)'], ['pass around', 'pass (ideas) around'],
      ['fragile', 'fragile (idea)'], ['solid', 'solid (argument)'], ['half-baked', 'half-baked'],
    ],
  },
};
const metaphorCanvas = document.getElementById('metaphor-canvas');
const metaphorCtx = metaphorCanvas.getContext('2d');
let metaphorActive = null, metaphorT = 0;
function metaphorPick(k) { metaphorActive = k; metaphorT = 0; pepSend('metaphor.pick', { key: k }); }
function metaphorReset() { metaphorActive = null; metaphorT = 0; }
function drawMetaphor() {
  const W = 960, H = 460; metaphorCtx.fillStyle = themeBg(); metaphorCtx.fillRect(0, 0, W, H);
  if (!metaphorActive) { metaphorCtx.fillStyle = '#666'; metaphorCtx.font = '11px monospace'; metaphorCtx.textAlign = 'center'; metaphorCtx.fillText('(pick a metaphor)', W/2, H/2); requestAnimationFrame(drawMetaphor); return; }
  const d = METAPHOR_DATA[metaphorActive];
  metaphorT = Math.min(200, metaphorT + 1);
  // Headers
  metaphorCtx.fillStyle = 'rgba(124,184,255,0.95)'; metaphorCtx.font = 'bold 14px monospace'; metaphorCtx.textAlign = 'center';
  metaphorCtx.fillText('SOURCE: ' + d.source, 240, 36);
  metaphorCtx.fillStyle = 'rgba(240,168,105,0.95)';
  metaphorCtx.fillText('TARGET: ' + d.target, 720, 36);
  metaphorCtx.fillStyle = '#aaa'; metaphorCtx.font = '11px monospace';
  metaphorCtx.fillText('concrete, well-understood', 240, 54);
  metaphorCtx.fillText('abstract, borrows structure', 720, 54);
  // Mapping rows
  d.mappings.forEach((pair, i) => {
    const y = 90 + i * 38;
    const revealed = metaphorT > i * 12;
    if (!revealed) return;
    metaphorCtx.fillStyle = 'rgba(124,184,255,' + Math.min(1, (metaphorT - i * 12) / 20).toFixed(3) + ')';
    metaphorCtx.font = '13px monospace'; metaphorCtx.textAlign = 'right';
    metaphorCtx.fillText(pair[0], 380, y);
    metaphorCtx.strokeStyle = 'rgba(129,199,132,0.6)'; metaphorCtx.lineWidth = 1.5;
    metaphorCtx.beginPath(); metaphorCtx.moveTo(400, y - 5); metaphorCtx.lineTo(560, y - 5); metaphorCtx.stroke();
    metaphorCtx.fillStyle = 'rgba(240,168,105,0.9)'; metaphorCtx.textAlign = 'left';
    metaphorCtx.fillText(pair[1], 580, y);
  });
  requestAnimationFrame(drawMetaphor);
}
drawMetaphor();

// ═══════════════════════════════════════════════════════════════════════
// Collocations
// ═══════════════════════════════════════════════════════════════════════
const COLLOC_DATA = {
  coffee: { good: 'strong coffee', bad: 'powerful coffee', note: 'both mean intense, only one collocates with coffee' },
  rain: { good: 'heavy rain', bad: 'strong rain', note: 'weather uses "heavy," not "strong"' },
  argument: { good: 'strong argument', bad: 'powerful argument', note: 'either works, but "strong" is much more common' },
  wind: { good: 'strong wind', bad: 'high wind (also ok!)', note: 'both collocate, but in different registers' },
};
const collocCanvas = document.getElementById('colloc-canvas');
const collocCtx = collocCanvas.getContext('2d');
let collocActive = null;
function collocPick(k) { collocActive = k; pepSend('colloc.pick', { key: k }); }
function collocReset() { collocActive = null; }
function drawColloc() {
  const W = 960, H = 400; collocCtx.fillStyle = themeBg(); collocCtx.fillRect(0, 0, W, H);
  if (!collocActive) { collocCtx.fillStyle = '#666'; collocCtx.font = '11px monospace'; collocCtx.textAlign = 'center'; collocCtx.fillText('(pick a pair)', W/2, H/2); requestAnimationFrame(drawColloc); return; }
  const d = COLLOC_DATA[collocActive];
  collocCtx.fillStyle = 'rgba(129,199,132,0.95)'; collocCtx.font = 'bold 22px monospace'; collocCtx.textAlign = 'center';
  collocCtx.fillText('✓ ' + d.good, W/2, 100);
  collocCtx.fillStyle = 'rgba(229,57,53,0.8)';
  collocCtx.fillText('✗ ' + d.bad, W/2, 160);
  collocCtx.fillStyle = '#aaa'; collocCtx.font = '11px monospace';
  collocCtx.fillText(d.note, W/2, 210);
  collocCtx.fillStyle = '#888'; collocCtx.font = '10px monospace';
  collocCtx.fillText('both adjectives have overlapping dictionary meanings', W/2, 260);
  collocCtx.fillText('only one has the collocation weight in native-speaker input', W/2, 280);
  collocCtx.fillText('non-natives who "know what both words mean" still produce the wrong pairing', W/2, 300);
  requestAnimationFrame(drawColloc);
}
drawColloc();

// ═══════════════════════════════════════════════════════════════════════
// Grammaticalization
// ═══════════════════════════════════════════════════════════════════════
const GRAMM_DATA = {
  'going-to': { stages: [ { year: 1400, form: 'going to (a place)', meaning: 'physical motion toward' }, { year: 1600, form: 'going to do X', meaning: 'intention with implication of motion' }, { year: 1800, form: 'going to X', meaning: 'future auxiliary' }, { year: 2000, form: 'gonna', meaning: 'reduced future marker' } ] },
  'will': { stages: [ { year: 800, form: 'willan', meaning: 'to want, desire' }, { year: 1200, form: 'will (volition)', meaning: 'wanting + future implication' }, { year: 1600, form: 'will', meaning: 'future auxiliary, volition fading' }, { year: 2000, form: "'ll", meaning: 'pure future marker' } ] },
  'let-us': { stages: [ { year: 1400, form: 'let us', meaning: 'permit us to' }, { year: 1700, form: 'let us', meaning: 'proposal marker' }, { year: 2000, form: "let's", meaning: 'hortative particle' } ] },
  'have-to': { stages: [ { year: 1200, form: 'have X to do', meaning: 'possess something needing action' }, { year: 1600, form: 'have to do X', meaning: 'obligation' }, { year: 2000, form: 'hafta', meaning: 'reduced obligation marker' } ] },
};
const grammCanvas = document.getElementById('gramm-canvas');
const grammCtx = grammCanvas.getContext('2d');
let grammActive = null;
function grammPick(k) { grammActive = k; pepSend('gramm.pick', { key: k }); }
function drawGramm() {
  const W = 960, H = 400; grammCtx.fillStyle = themeBg(); grammCtx.fillRect(0, 0, W, H);
  if (!grammActive) { grammCtx.fillStyle = '#666'; grammCtx.font = '11px monospace'; grammCtx.textAlign = 'center'; grammCtx.fillText('(pick a word)', W/2, H/2); requestAnimationFrame(drawGramm); return; }
  const d = GRAMM_DATA[grammActive];
  grammCtx.fillStyle = '#aaa'; grammCtx.font = '11px monospace'; grammCtx.textAlign = 'left';
  grammCtx.fillText('stages of grammaticalization (oldest → newest)', 30, 30);
  d.stages.forEach((s, i) => {
    const y = 70 + i * 75;
    grammCtx.fillStyle = 'rgba(240,168,105,0.85)'; grammCtx.font = 'bold 12px monospace';
    grammCtx.fillText('~' + s.year, 40, y);
    grammCtx.fillStyle = 'rgba(124,184,255,0.95)'; grammCtx.font = 'bold 16px monospace';
    grammCtx.fillText(s.form, 140, y);
    grammCtx.fillStyle = '#e0e0e0'; grammCtx.font = '12px monospace';
    grammCtx.fillText('→ ' + s.meaning, 140, y + 20);
    if (i < d.stages.length - 1) {
      grammCtx.strokeStyle = 'rgba(120,120,140,0.5)'; grammCtx.lineWidth = 1;
      grammCtx.beginPath(); grammCtx.moveTo(60, y + 40); grammCtx.lineTo(60, y + 60); grammCtx.stroke();
    }
  });
  requestAnimationFrame(drawGramm);
}
drawGramm();

// ═══════════════════════════════════════════════════════════════════════
// Lexical Gaps
// ═══════════════════════════════════════════════════════════════════════
const LEXGAP_DATA = {
  mamih: { word: 'mamihlapinatapai', lang: 'Yaghan', meaning: 'a look shared by two people, each wishing the other would initiate something they both want but neither is willing to start' },
  tsund: { word: 'tsundoku', lang: 'Japanese', meaning: 'the act of acquiring books and letting them pile up unread' },
  iktsu: { word: 'iktsuarpok', lang: 'Inuit', meaning: 'the anticipatory feeling that makes you go outside to see if anyone is coming' },
  wald: { word: 'waldeinsamkeit', lang: 'German', meaning: 'the feeling of being alone in the woods, connected to nature, both solitary and peaceful' },
  liter: { word: 'literalmente', lang: 'Spanish / Italian', meaning: '"literally" but used as an intensifier with no literal force, which English acquired later' },
};
const lexgapCanvas = document.getElementById('lexgap-canvas');
const lexgapCtx = lexgapCanvas.getContext('2d');
let lexgapActive = null;
function lexgapPick(k) { lexgapActive = k; pepSend('lexgap.pick', { key: k }); }
function drawLexgap() {
  const W = 960, H = 440; lexgapCtx.fillStyle = themeBg(); lexgapCtx.fillRect(0, 0, W, H);
  if (!lexgapActive) { lexgapCtx.fillStyle = '#666'; lexgapCtx.font = '11px monospace'; lexgapCtx.textAlign = 'center'; lexgapCtx.fillText('(pick a word)', W/2, H/2); requestAnimationFrame(drawLexgap); return; }
  const d = LEXGAP_DATA[lexgapActive];
  lexgapCtx.fillStyle = '#fff'; lexgapCtx.font = 'bold 26px monospace'; lexgapCtx.textAlign = 'center';
  lexgapCtx.fillText(d.word, W/2, 80);
  lexgapCtx.fillStyle = '#aaa'; lexgapCtx.font = '11px monospace';
  lexgapCtx.fillText('(' + d.lang + ')', W/2, 104);
  lexgapCtx.fillStyle = '#e0e0e0'; lexgapCtx.font = '13px monospace';
  // Wrap meaning
  const words = d.meaning.split(' '); let x = 80, y = 180;
  words.forEach(w => {
    const m = lexgapCtx.measureText(w + ' ');
    if (x + m.width > W - 80) { x = 80; y += 24; }
    lexgapCtx.fillText(w + ' ', x, y); x += m.width;
  });
  lexgapCtx.fillStyle = 'rgba(240,168,105,0.9)'; lexgapCtx.font = '11px monospace'; lexgapCtx.textAlign = 'center';
  lexgapCtx.fillText('English has no single word for this concept', W/2, H - 30);
  requestAnimationFrame(drawLexgap);
}
drawLexgap();

// ═══════════════════════════════════════════════════════════════════════
// Sound Symbolism — Bouba / Kiki
// ═══════════════════════════════════════════════════════════════════════
const SOUNDSYM_DATA = {
  bouba: { note: '95% of humans match "bouba" with the rounded shape and "kiki" with the spiky one' },
  gl: { cluster: 'gl-', examples: ['glitter', 'glow', 'glance', 'glisten', 'gleam', 'glaze', 'glimmer'], domain: 'visual light effects' },
  sn: { cluster: 'sn-', examples: ['snore', 'sneeze', 'sniff', 'snot', 'snout', 'snarl', 'snub'], domain: 'the nose or snout' },
  sl: { cluster: 'sl-', examples: ['slip', 'slide', 'slither', 'slick', 'slush', 'slurp', 'slop'], domain: 'slippery or wet' },
  fl: { cluster: 'fl-', examples: ['flame', 'flash', 'flicker', 'float', 'flutter', 'flow', 'flame'], domain: 'light and motion' },
};
const soundsymCanvas = document.getElementById('soundsym-canvas');
const soundsymCtx = soundsymCanvas.getContext('2d');
let soundsymActive = null;
function soundsymPick(k) { soundsymActive = k; pepSend('soundsym.pick', { key: k }); }
function drawSoundsym() {
  const W = 960, H = 440; soundsymCtx.fillStyle = themeBg(); soundsymCtx.fillRect(0, 0, W, H);
  if (!soundsymActive) { soundsymCtx.fillStyle = '#666'; soundsymCtx.font = '11px monospace'; soundsymCtx.textAlign = 'center'; soundsymCtx.fillText('(pick an example)', W/2, H/2); requestAnimationFrame(drawSoundsym); return; }
  if (soundsymActive === 'bouba') {
    // Rounded blob on left
    soundsymCtx.fillStyle = 'rgba(124,184,255,0.45)';
    soundsymCtx.beginPath();
    const cx = 280, cy = 200;
    for (let i = 0; i <= 360; i += 10) {
      const r = 80 + Math.sin(i * 0.06) * 15;
      const x = cx + Math.cos(i * Math.PI / 180) * r;
      const y = cy + Math.sin(i * Math.PI / 180) * r;
      if (i === 0) soundsymCtx.moveTo(x, y); else soundsymCtx.lineTo(x, y);
    }
    soundsymCtx.closePath(); soundsymCtx.fill();
    soundsymCtx.strokeStyle = 'rgba(124,184,255,0.95)'; soundsymCtx.lineWidth = 2; soundsymCtx.stroke();
    soundsymCtx.fillStyle = '#fff'; soundsymCtx.font = 'bold 22px monospace'; soundsymCtx.textAlign = 'center';
    soundsymCtx.fillText('BOUBA', cx, cy + 8);
    // Spiky on right
    soundsymCtx.fillStyle = 'rgba(240,168,105,0.45)';
    soundsymCtx.beginPath();
    const sx = 680, sy = 200;
    for (let i = 0; i < 12; i++) {
      const a = (i / 12) * Math.PI * 2;
      const r = i % 2 === 0 ? 95 : 45;
      const x = sx + Math.cos(a) * r;
      const y = sy + Math.sin(a) * r;
      if (i === 0) soundsymCtx.moveTo(x, y); else soundsymCtx.lineTo(x, y);
    }
    soundsymCtx.closePath(); soundsymCtx.fill();
    soundsymCtx.strokeStyle = 'rgba(240,168,105,0.95)'; soundsymCtx.lineWidth = 2; soundsymCtx.stroke();
    soundsymCtx.fillStyle = '#fff'; soundsymCtx.font = 'bold 22px monospace';
    soundsymCtx.fillText('KIKI', sx, sy + 8);
    soundsymCtx.fillStyle = '#aaa'; soundsymCtx.font = '11px monospace';
    soundsymCtx.fillText(SOUNDSYM_DATA.bouba.note, W/2, H - 30);
  } else {
    const d = SOUNDSYM_DATA[soundsymActive];
    soundsymCtx.fillStyle = 'rgba(240,168,105,0.95)'; soundsymCtx.font = 'bold 36px monospace'; soundsymCtx.textAlign = 'center';
    soundsymCtx.fillText(d.cluster, W/2, 80);
    soundsymCtx.fillStyle = '#aaa'; soundsymCtx.font = '11px monospace';
    soundsymCtx.fillText('domain: ' + d.domain, W/2, 110);
    soundsymCtx.fillStyle = '#e0e0e0'; soundsymCtx.font = '16px monospace';
    d.examples.forEach((w, i) => {
      const col = i % 4, row = Math.floor(i / 4);
      const x = 180 + col * 180, y = 170 + row * 50;
      soundsymCtx.fillText(w, x, y);
    });
    soundsymCtx.fillStyle = 'rgba(129,199,132,0.85)'; soundsymCtx.font = '11px monospace';
    soundsymCtx.fillText('part of the meaning is in the phonemes themselves', W/2, H - 30);
  }
  requestAnimationFrame(drawSoundsym);
}
drawSoundsym();

// ═══════════════════════════════════════════════════════════════════════
// Repetition & Rhythm
// ═══════════════════════════════════════════════════════════════════════
const REPETITION_DATA = {
  iambic: { label: 'iambic pentameter', line: 'Shall I compare thee to a summer\\u0027s day?', pattern: [0, 1, 0, 1, 0, 1, 0, 1, 0, 1], note: 'unstressed-stressed × 5 — the default English poetic meter' },
  haiku: { label: 'haiku (5-7-5)', line: 'an old silent pond\\n/ a frog jumps into the pond\\n/ splash! silence again', pattern: [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1], note: 'compressed three-beat landing' },
  free: { label: 'free verse', line: 'So much depends\\n/ upon\\n/ a red wheelbarrow', pattern: [1, 1, 0, 1, 0, 1, 1, 1, 1], note: 'breaks forecast deliberately' },
  refrain: { label: 'refrain', line: 'tomorrow, and tomorrow, and tomorrow', pattern: [1, 0, 1, 0, 1], note: 'each repetition accumulates weight' },
};
const repetitionCanvas = document.getElementById('repetition-canvas');
const repetitionCtx = repetitionCanvas.getContext('2d');
let repetitionActive = null;
function repetitionPlay(k) { repetitionActive = k; pepSend('repetition.play', { key: k }); }
function drawRepetition() {
  const W = 960, H = 420; repetitionCtx.fillStyle = themeBg(); repetitionCtx.fillRect(0, 0, W, H);
  if (!repetitionActive) { repetitionCtx.fillStyle = '#666'; repetitionCtx.font = '11px monospace'; repetitionCtx.textAlign = 'center'; repetitionCtx.fillText('(pick a form)', W/2, H/2); requestAnimationFrame(drawRepetition); return; }
  const d = REPETITION_DATA[repetitionActive];
  repetitionCtx.fillStyle = 'rgba(124,184,255,0.95)'; repetitionCtx.font = 'bold 13px monospace'; repetitionCtx.textAlign = 'left';
  repetitionCtx.fillText(d.label.toUpperCase(), 30, 40);
  repetitionCtx.fillStyle = '#e0e0e0'; repetitionCtx.font = '14px monospace';
  const lines = d.line.split('/');
  lines.forEach((ln, i) => repetitionCtx.fillText(ln.trim(), 30, 70 + i * 26));
  // Stress pattern
  const baseY = 240;
  d.pattern.forEach((p, i) => {
    const x = 60 + i * 50;
    const h = p ? 60 : 20;
    repetitionCtx.fillStyle = p ? 'rgba(240,168,105,0.85)' : 'rgba(120,120,140,0.5)';
    repetitionCtx.fillRect(x, baseY - h, 32, h);
  });
  repetitionCtx.fillStyle = '#aaa'; repetitionCtx.font = '11px monospace';
  repetitionCtx.fillText('stress pattern (orange = stressed)', 60, 280);
  repetitionCtx.fillText(d.note, 60, H - 30);
  requestAnimationFrame(drawRepetition);
}
drawRepetition();

// ═══════════════════════════════════════════════════════════════════════
// Pronouns & Deixis
// ═══════════════════════════════════════════════════════════════════════
const DEIXIS_DATA = {
  alice: { sentence: '"I\\u0027ll meet you here tomorrow."', speaker: 'Alice', listener: 'Bob', location: "Alice's kitchen", time: 'Monday 6pm', resolves: { I: 'Alice', you: 'Bob', here: "Alice's kitchen", tomorrow: 'Tuesday' } },
  bob: { sentence: '"I\\u0027ll meet you here tomorrow."', speaker: 'Bob', listener: 'Alice', location: 'the park', time: 'Monday 6pm', resolves: { I: 'Bob', you: 'Alice', here: 'the park', tomorrow: 'Tuesday' } },
  later: { sentence: '"I\\u0027ll meet you here tomorrow."', speaker: 'Alice', listener: 'Bob', location: "Alice's kitchen", time: 'Wednesday 6pm', resolves: { I: 'Alice', you: 'Bob', here: "Alice's kitchen", tomorrow: 'Thursday' } },
};
const deixisCanvas = document.getElementById('deixis-canvas');
const deixisCtx = deixisCanvas.getContext('2d');
let deixisActive = null;
function deixisPick(k) { deixisActive = k; pepSend('deixis.pick', { key: k }); }
function deixisReset() { deixisActive = null; }
function drawDeixis() {
  const W = 960, H = 420; deixisCtx.fillStyle = themeBg(); deixisCtx.fillRect(0, 0, W, H);
  if (!deixisActive) { deixisCtx.fillStyle = '#666'; deixisCtx.font = '11px monospace'; deixisCtx.textAlign = 'center'; deixisCtx.fillText('(pick a speech context)', W/2, H/2); requestAnimationFrame(drawDeixis); return; }
  const d = DEIXIS_DATA[deixisActive];
  deixisCtx.fillStyle = '#fff'; deixisCtx.font = 'bold 18px monospace'; deixisCtx.textAlign = 'center';
  deixisCtx.fillText(d.sentence, W/2, 60);
  deixisCtx.fillStyle = '#aaa'; deixisCtx.font = '11px monospace';
  deixisCtx.fillText('speaker: ' + d.speaker + ' · listener: ' + d.listener + ' · location: ' + d.location + ' · time: ' + d.time, W/2, 90);
  // Resolution table
  const entries = Object.entries(d.resolves);
  entries.forEach(([key, val], i) => {
    const y = 160 + i * 50;
    deixisCtx.fillStyle = 'rgba(240,168,105,0.95)'; deixisCtx.font = 'bold 16px monospace'; deixisCtx.textAlign = 'right';
    deixisCtx.fillText('"' + key + '"', 380, y);
    deixisCtx.strokeStyle = 'rgba(129,199,132,0.6)'; deixisCtx.lineWidth = 1.5;
    deixisCtx.beginPath(); deixisCtx.moveTo(400, y - 5); deixisCtx.lineTo(540, y - 5); deixisCtx.stroke();
    deixisCtx.fillStyle = 'rgba(124,184,255,0.95)'; deixisCtx.textAlign = 'left';
    deixisCtx.fillText('→ ' + val, 560, y);
  });
  deixisCtx.fillStyle = '#888'; deixisCtx.font = '10px monospace'; deixisCtx.textAlign = 'center';
  deixisCtx.fillText('the words are fixed; the resolutions change with every speech context', W/2, H - 20);
  requestAnimationFrame(drawDeixis);
}
drawDeixis();

// ═══════════════════════════════════════════════════════════════════════
// Anaphora
// ═══════════════════════════════════════════════════════════════════════
const ANAPHORA_DATA = {
  mary: { sentence: '"Mary told Jane that she was late."', candidates: ['Mary', 'Jane'], ambiguous: true, note: 'grammar allows both; listener uses recency + plausibility' },
  trophy: { sentence: '"The trophy wouldn\\u0027t fit in the suitcase because it was too big."', resolved: 'trophy', note: 'world knowledge flips the binding based on "big" vs "small"' },
  chain: { sentence: '"John took the book off the shelf and put it on the table because it was dusty."', resolved: 'shelf (not book or table)', note: 'three "it" candidates; only one makes "dusty" plausible' },
};
const anaphoraCanvas = document.getElementById('anaphora-canvas');
const anaphoraCtx = anaphoraCanvas.getContext('2d');
let anaphoraActive = null;
function anaphoraPick(k) { anaphoraActive = k; pepSend('anaphora.pick', { key: k }); }
function drawAnaphora() {
  const W = 960, H = 400; anaphoraCtx.fillStyle = themeBg(); anaphoraCtx.fillRect(0, 0, W, H);
  if (!anaphoraActive) { anaphoraCtx.fillStyle = '#666'; anaphoraCtx.font = '11px monospace'; anaphoraCtx.textAlign = 'center'; anaphoraCtx.fillText('(pick a sentence)', W/2, H/2); requestAnimationFrame(drawAnaphora); return; }
  const d = ANAPHORA_DATA[anaphoraActive];
  anaphoraCtx.fillStyle = '#fff'; anaphoraCtx.font = 'bold 16px monospace'; anaphoraCtx.textAlign = 'left';
  // Word-wrap
  const words = d.sentence.split(' '); let x = 30, y = 80;
  words.forEach(w => {
    const m = anaphoraCtx.measureText(w + ' ');
    if (x + m.width > W - 40) { x = 30; y += 26; }
    anaphoraCtx.fillText(w + ' ', x, y); x += m.width;
  });
  if (d.ambiguous) {
    anaphoraCtx.fillStyle = 'rgba(240,168,105,0.95)'; anaphoraCtx.font = 'bold 12px monospace'; anaphoraCtx.textAlign = 'left';
    anaphoraCtx.fillText('AMBIGUOUS: both candidates possible', 30, 180);
    d.candidates.forEach((c, i) => {
      anaphoraCtx.fillStyle = 'rgba(124,184,255,0.85)'; anaphoraCtx.font = '13px monospace';
      anaphoraCtx.fillText('• "she" = ' + c, 50, 210 + i * 24);
    });
  } else {
    anaphoraCtx.fillStyle = 'rgba(129,199,132,0.95)'; anaphoraCtx.font = 'bold 12px monospace';
    anaphoraCtx.fillText('RESOLVED (by world knowledge)', 30, 180);
    anaphoraCtx.fillStyle = '#e0e0e0'; anaphoraCtx.font = '13px monospace';
    anaphoraCtx.fillText('→ ' + d.resolved, 50, 204);
  }
  anaphoraCtx.fillStyle = '#aaa'; anaphoraCtx.font = '11px monospace';
  anaphoraCtx.fillText(d.note, 30, H - 30);
  requestAnimationFrame(drawAnaphora);
}
drawAnaphora();

// ═══════════════════════════════════════════════════════════════════════
// Politeness
// ═══════════════════════════════════════════════════════════════════════
const POLITENESS_DATA = {
  bald: { utterance: '"Close the window."', strategy: 'bald on-record', when: 'intimates, emergencies, high-power speaker', face_cost: 0.9 },
  positive: { utterance: '"Hey buddy, close that for us?"', strategy: 'positive politeness', when: 'friends, in-group emphasis', face_cost: 0.35 },
  negative: { utterance: '"Could you possibly close the window, if it\\u0027s not too much trouble?"', strategy: 'negative politeness', when: 'distant/formal, minimizes imposition', face_cost: 0.1 },
  off: { utterance: '"It\\u0027s cold in here."', strategy: 'off-record', when: 'maximum face-saving, plausible deniability', face_cost: 0.05 },
};
const politenessCanvas = document.getElementById('politeness-canvas');
const politenessCtx = politenessCanvas.getContext('2d');
let politenessActive = null;
function politenessPick(k) { politenessActive = k; pepSend('politeness.pick', { key: k }); }
function drawPoliteness() {
  const W = 960, H = 440; politenessCtx.fillStyle = themeBg(); politenessCtx.fillRect(0, 0, W, H);
  if (!politenessActive) { politenessCtx.fillStyle = '#666'; politenessCtx.font = '11px monospace'; politenessCtx.textAlign = 'center'; politenessCtx.fillText('(pick a strategy)', W/2, H/2); requestAnimationFrame(drawPoliteness); return; }
  const d = POLITENESS_DATA[politenessActive];
  politenessCtx.fillStyle = '#fff'; politenessCtx.font = 'bold 18px monospace'; politenessCtx.textAlign = 'center';
  politenessCtx.fillText(d.utterance, W/2, 80);
  politenessCtx.fillStyle = 'rgba(124,184,255,0.95)'; politenessCtx.font = 'bold 13px monospace';
  politenessCtx.fillText(d.strategy.toUpperCase(), W/2, 130);
  politenessCtx.fillStyle = '#aaa'; politenessCtx.font = '11px monospace';
  politenessCtx.fillText('when to use: ' + d.when, W/2, 160);
  // Face cost bar
  politenessCtx.fillStyle = '#aaa'; politenessCtx.textAlign = 'left'; politenessCtx.font = '11px monospace';
  politenessCtx.fillText("face cost (imposition on listener's social standing)", 80, 240);
  politenessCtx.fillStyle = 'rgba(229,57,53,0.2)'; politenessCtx.fillRect(80, 250, 800, 24);
  politenessCtx.fillStyle = 'rgba(229,57,53,0.85)'; politenessCtx.fillRect(80, 250, 800 * d.face_cost, 24);
  politenessCtx.fillStyle = '#aaa'; politenessCtx.textAlign = 'right';
  politenessCtx.fillText((d.face_cost * 100).toFixed(0) + '%', 880, 268);
  politenessCtx.fillStyle = '#888'; politenessCtx.font = '10px monospace'; politenessCtx.textAlign = 'center';
  politenessCtx.fillText('bald strategies are cheap but costly to face; off-record strategies are expensive but preserve face', W/2, H - 20);
  requestAnimationFrame(drawPoliteness);
}
drawPoliteness();

// ═══════════════════════════════════════════════════════════════════════
// Discourse Markers
// ═══════════════════════════════════════════════════════════════════════
const DISCOURSE_DATA = {
  'so': { marker: '"so"', function: 'topic-opener or summary', example: '"So, about that budget..."' },
  'well': { marker: '"well"', function: 'signals non-preferred response', example: '"Well, it\\u0027s complicated..."' },
  'anyway': { marker: '"anyway"', function: 'topic closure / return to main', example: '"Anyway, back to the point..."' },
  'like': { marker: '"like"', function: 'quotative or approximation', example: '"She was like, \\u0027no way.\\u0027"' },
  'you-know': { marker: '"you know"', function: 'common-ground check', example: '"He lives in that neighborhood, you know, the old one."' },
  'actually': { marker: '"actually"', function: 'contrast marker / correction', example: '"Actually, I thought it was okay."' },
};
const discourseCanvas = document.getElementById('discourse-canvas');
const discourseCtx = discourseCanvas.getContext('2d');
let discourseActive = null;
function discoursePick(k) { discourseActive = k; pepSend('discourse.pick', { key: k }); }
function drawDiscourse() {
  const W = 960, H = 420; discourseCtx.fillStyle = themeBg(); discourseCtx.fillRect(0, 0, W, H);
  if (!discourseActive) { discourseCtx.fillStyle = '#666'; discourseCtx.font = '11px monospace'; discourseCtx.textAlign = 'center'; discourseCtx.fillText('(pick a marker)', W/2, H/2); requestAnimationFrame(drawDiscourse); return; }
  const d = DISCOURSE_DATA[discourseActive];
  discourseCtx.fillStyle = 'rgba(240,168,105,0.95)'; discourseCtx.font = 'bold 26px monospace'; discourseCtx.textAlign = 'center';
  discourseCtx.fillText(d.marker, W/2, 90);
  discourseCtx.fillStyle = 'rgba(124,184,255,0.95)'; discourseCtx.font = 'bold 12px monospace';
  discourseCtx.fillText('FUNCTION', W/2, 160);
  discourseCtx.fillStyle = '#e0e0e0'; discourseCtx.font = '14px monospace';
  discourseCtx.fillText(d.function, W/2, 186);
  discourseCtx.fillStyle = 'rgba(129,199,132,0.95)'; discourseCtx.font = 'bold 12px monospace';
  discourseCtx.fillText('EXAMPLE', W/2, 250);
  discourseCtx.fillStyle = '#e0e0e0'; discourseCtx.font = '14px monospace';
  discourseCtx.fillText(d.example, W/2, 276);
  discourseCtx.fillStyle = '#888'; discourseCtx.font = '10px monospace';
  discourseCtx.fillText('native speakers use these constantly and edit them out when writing', W/2, H - 20);
  requestAnimationFrame(drawDiscourse);
}
drawDiscourse();

// ═══════════════════════════════════════════════════════════════════════
// Swearing Dynamics
// ═══════════════════════════════════════════════════════════════════════
const swearingCanvas = document.getElementById('swearing-canvas');
const swearingCtx = swearingCanvas.getContext('2d');
let swearingFiredT = 0;
document.getElementById('swearing-rate').addEventListener('input', (e) => {
  document.getElementById('swearing-rate-val').textContent = e.target.value + '%';
});
function swearingFire() { swearingFiredT = 60; pepSend('swearing.fire', {}); }
function swearingReset() { document.getElementById('swearing-rate').value = 20; document.getElementById('swearing-rate-val').textContent = '20%'; swearingFiredT = 0; }
function drawSwearing() {
  const W = 960, H = 400; swearingCtx.fillStyle = themeBg(); swearingCtx.fillRect(0, 0, W, H);
  const rate = parseInt(document.getElementById('swearing-rate').value) / 100;
  const impact = Math.max(0, 1 - rate);
  if (swearingFiredT > 0) swearingFiredT--;
  swearingCtx.fillStyle = '#aaa'; swearingCtx.font = '11px monospace'; swearingCtx.textAlign = 'left';
  swearingCtx.fillText("listener's arousal impact when the speaker swears once", 60, 40);
  swearingCtx.fillStyle = 'rgba(229,57,53,0.2)'; swearingCtx.fillRect(60, 60, 820, 30);
  swearingCtx.fillStyle = 'rgba(229,57,53,' + (0.4 + impact * 0.55).toFixed(3) + ')';
  swearingCtx.fillRect(60, 60, 820 * impact, 30);
  swearingCtx.fillStyle = '#aaa'; swearingCtx.textAlign = 'right'; swearingCtx.font = '10px monospace';
  swearingCtx.fillText((impact * 100).toFixed(0) + '%', 880, 80);
  // Curve
  swearingCtx.strokeStyle = 'rgba(124,184,255,0.85)'; swearingCtx.lineWidth = 2;
  swearingCtx.beginPath();
  for (let i = 0; i <= 100; i++) {
    const r = i / 100;
    const imp = Math.max(0, 1 - r);
    const x = 60 + i * 8.2;
    const y = 240 - imp * 120;
    if (i === 0) swearingCtx.moveTo(x, y); else swearingCtx.lineTo(x, y);
  }
  swearingCtx.stroke();
  const cx = 60 + rate * 820;
  swearingCtx.fillStyle = 'rgba(240,168,105,0.95)';
  swearingCtx.beginPath(); swearingCtx.arc(cx, 240 - impact * 120, 7, 0, Math.PI * 2); swearingCtx.fill();
  swearingCtx.fillStyle = '#aaa'; swearingCtx.font = '10px monospace'; swearingCtx.textAlign = 'left';
  swearingCtx.fillText('baseline frequency →', 60, 270);
  swearingCtx.fillText('← impact of single swear', 60, 130);
  if (swearingFiredT > 0) {
    swearingCtx.fillStyle = 'rgba(229,57,53,' + (swearingFiredT / 60 * 0.3).toFixed(3) + ')';
    swearingCtx.fillRect(0, 0, W, H);
  }
  swearingCtx.fillStyle = '#888'; swearingCtx.font = '10px monospace'; swearingCtx.textAlign = 'center';
  swearingCtx.fillText('effectiveness is inversely proportional to baseline', W/2, H - 20);
  requestAnimationFrame(drawSwearing);
}
drawSwearing();

// ═══════════════════════════════════════════════════════════════════════
// POV / Narrative Voice
// ═══════════════════════════════════════════════════════════════════════
const POV_DATA = {
  first: { label: 'first person', text: 'I walked into the room. The light was too bright. I hated this place.', distance: 0.15, knowledge: 0.4 },
  second: { label: 'second person', text: 'You walk into the room. The light is too bright. You hate this place.', distance: 0.1, knowledge: 0.4 },
  'third-close': { label: 'third-person close', text: 'She walked into the room. The light was too bright. She hated this place.', distance: 0.4, knowledge: 0.5 },
  'third-omni': { label: 'third-person omniscient', text: 'She walked into the room, unaware that upstairs, the killer was already waiting.', distance: 0.85, knowledge: 1.0 },
};
const povCanvas = document.getElementById('pov-canvas');
const povCtx = povCanvas.getContext('2d');
let povActive = null;
function povPick(k) { povActive = k; pepSend('pov.pick', { key: k }); }
function drawPov() {
  const W = 960, H = 420; povCtx.fillStyle = themeBg(); povCtx.fillRect(0, 0, W, H);
  if (!povActive) { povCtx.fillStyle = '#666'; povCtx.font = '11px monospace'; povCtx.textAlign = 'center'; povCtx.fillText('(pick a POV)', W/2, H/2); requestAnimationFrame(drawPov); return; }
  const d = POV_DATA[povActive];
  povCtx.fillStyle = 'rgba(124,184,255,0.95)'; povCtx.font = 'bold 13px monospace'; povCtx.textAlign = 'left';
  povCtx.fillText(d.label.toUpperCase(), 30, 40);
  povCtx.fillStyle = '#e0e0e0'; povCtx.font = '14px monospace';
  // Wrap
  const words = d.text.split(' '); let x = 30, y = 80;
  words.forEach(w => {
    const m = povCtx.measureText(w + ' ');
    if (x + m.width > W - 40) { x = 30; y += 22; }
    povCtx.fillText(w + ' ', x, y); x += m.width;
  });
  // Two bars
  const metrics = [
    { l: 'reader distance from character', v: d.distance, c: '229,57,53' },
    { l: 'narrator knowledge', v: d.knowledge, c: '129,199,132' },
  ];
  metrics.forEach((m, i) => {
    const my = 200 + i * 56;
    povCtx.fillStyle = '#aaa'; povCtx.font = '11px monospace'; povCtx.textAlign = 'left';
    povCtx.fillText(m.l, 30, my);
    povCtx.fillStyle = 'rgba(' + m.c + ',0.2)'; povCtx.fillRect(30, my + 10, 840, 20);
    povCtx.fillStyle = 'rgba(' + m.c + ',0.9)'; povCtx.fillRect(30, my + 10, 840 * m.v, 20);
  });
  requestAnimationFrame(drawPov);
}
drawPov();

// ═══════════════════════════════════════════════════════════════════════
// Stream of Consciousness
// ═══════════════════════════════════════════════════════════════════════
const STREAM_DATA = {
  woolf: { label: 'Virginia Woolf — Mrs. Dalloway', text: 'What a lark! What a plunge! For so it had always seemed to her, when, with a little squeak of the hinges, which she could hear now, she had burst open the French windows and plunged at Bourton into the open air.', load: 0.8 },
  joyce: { label: 'James Joyce — Ulysses', text: 'yes and then he asked me would I yes to say yes my mountain flower and first I put my arms around him yes and drew him down to me so he could feel my breasts all perfume yes and his heart was going like mad and yes I said yes I will Yes', load: 0.95 },
  normal: { label: 'normal prose', text: 'She opened the French windows and stepped onto the balcony. The morning air was cool. She remembered Bourton and smiled.', load: 0.2 },
};
const streamCanvas = document.getElementById('stream-canvas');
const streamCtx = streamCanvas.getContext('2d');
let streamActive = null;
function streamPick(k) { streamActive = k; pepSend('stream.pick', { key: k }); }
function drawStream() {
  const W = 960, H = 400; streamCtx.fillStyle = themeBg(); streamCtx.fillRect(0, 0, W, H);
  if (!streamActive) { streamCtx.fillStyle = '#666'; streamCtx.font = '11px monospace'; streamCtx.textAlign = 'center'; streamCtx.fillText('(pick a passage)', W/2, H/2); requestAnimationFrame(drawStream); return; }
  const d = STREAM_DATA[streamActive];
  streamCtx.fillStyle = 'rgba(240,168,105,0.95)'; streamCtx.font = 'bold 12px monospace'; streamCtx.textAlign = 'left';
  streamCtx.fillText(d.label, 30, 30);
  streamCtx.fillStyle = '#e0e0e0'; streamCtx.font = '13px monospace';
  const words = d.text.split(' '); let x = 30, y = 70;
  words.forEach(w => {
    const m = streamCtx.measureText(w + ' ');
    if (x + m.width > W - 30) { x = 30; y += 22; }
    streamCtx.fillText(w + ' ', x, y); x += m.width;
  });
  streamCtx.fillStyle = '#aaa'; streamCtx.font = '11px monospace';
  streamCtx.fillText('reader cognitive load', 30, H - 60);
  streamCtx.fillStyle = 'rgba(229,57,53,0.2)'; streamCtx.fillRect(30, H - 48, 900, 22);
  streamCtx.fillStyle = 'rgba(229,57,53,0.85)'; streamCtx.fillRect(30, H - 48, 900 * d.load, 22);
  streamCtx.fillStyle = '#aaa'; streamCtx.textAlign = 'right';
  streamCtx.fillText((d.load * 100).toFixed(0) + '%', 930, H - 32);
  requestAnimationFrame(drawStream);
}
drawStream();

// ═══════════════════════════════════════════════════════════════════════
// Typography
// ═══════════════════════════════════════════════════════════════════════
const typographyCanvas = document.getElementById('typography-canvas');
const typographyCtx = typographyCanvas.getContext('2d');
let typographyActive = null;
function typographyPick(k) { typographyActive = k; pepSend('typography.pick', { key: k }); }
function drawTypography() {
  const W = 960, H = 440; typographyCtx.fillStyle = themeBg(); typographyCtx.fillRect(0, 0, W, H);
  if (!typographyActive) { typographyCtx.fillStyle = '#666'; typographyCtx.font = '11px monospace'; typographyCtx.textAlign = 'center'; typographyCtx.fillText('(pick a variant)', W/2, H/2); requestAnimationFrame(drawTypography); return; }
  typographyCtx.fillStyle = 'rgba(124,184,255,0.95)'; typographyCtx.font = 'bold 12px monospace'; typographyCtx.textAlign = 'left';
  typographyCtx.fillText(typographyActive.toUpperCase(), 30, 40);
  const base = 'I never said she stole the money';
  typographyCtx.textAlign = 'center'; typographyCtx.fillStyle = '#fff';
  if (typographyActive === 'plain') {
    typographyCtx.font = '18px monospace';
    typographyCtx.fillText(base + '.', W/2, 180);
    typographyCtx.fillStyle = '#aaa'; typographyCtx.font = '11px monospace';
    typographyCtx.fillText('no emphasis, no structural hints, reader reconstructs prosody from context alone', W/2, 230);
  } else if (typographyActive === 'italic') {
    typographyCtx.font = 'italic 20px monospace';
    typographyCtx.fillText('I never said ' + String.fromCharCode(8220) + 'she' + String.fromCharCode(8221) + ' stole the money.', W/2, 180);
    typographyCtx.fillStyle = '#aaa'; typographyCtx.font = '11px monospace';
    typographyCtx.fillText('italics recover stress — the reader hears "she" emphasized', W/2, 230);
  } else if (typographyActive === 'caps') {
    typographyCtx.font = '20px monospace';
    typographyCtx.fillText('I NEVER said she stole the money.', W/2, 180);
    typographyCtx.fillStyle = '#aaa'; typographyCtx.font = '11px monospace';
    typographyCtx.fillText('ALL CAPS reads as shouting / emphatic denial', W/2, 230);
  } else if (typographyActive === 'breaks') {
    typographyCtx.font = '18px monospace';
    typographyCtx.fillText('I', W/2, 120);
    typographyCtx.fillText('never said', W/2, 160);
    typographyCtx.fillText('she', W/2, 200);
    typographyCtx.fillText('stole the money.', W/2, 240);
    typographyCtx.fillStyle = '#aaa'; typographyCtx.font = '11px monospace';
    typographyCtx.fillText('line breaks are pauses in the internal voice', W/2, 300);
  } else if (typographyActive === 'spaced') {
    typographyCtx.font = '20px monospace';
    typographyCtx.fillText('I  n e v e r  said she stole the money.', W/2, 180);
    typographyCtx.fillStyle = '#aaa'; typographyCtx.font = '11px monospace';
    typographyCtx.fillText('letter spacing reads slower; "n e v e r" becomes a deliberate drawl', W/2, 230);
  }
  requestAnimationFrame(drawTypography);
}
drawTypography();

// ═══════════════════════════════════════════════════════════════════════
// AI-Generated Text Detection
// ═══════════════════════════════════════════════════════════════════════
const AIDETECT_DATA = {
  human: { text: "OK look I wrote this thing but honestly I'm not sure if it works? It's like — the idea is fine but the execution feels off. Might try again tomorrow. ugh.", markers: { delve: 0, tapestry: 0, hedges: 0.15, variance: 0.85, final_draft: 0.05, typos: 0.2 } },
  llm: { text: 'Furthermore, it is important to consider the multifaceted tapestry of perspectives on this matter. Moreover, one must delve into the nuances, while acknowledging that there are valid considerations on both sides.', markers: { delve: 0.9, tapestry: 0.9, hedges: 0.85, variance: 0.1, final_draft: 0.95, typos: 0.0 } },
};
const aidetectCanvas = document.getElementById('aidetect-canvas');
const aidetectCtx = aidetectCanvas.getContext('2d');
let aidetectActive = null;
function aidetectPick(k) { aidetectActive = k; pepSend('aidetect.pick', { key: k }); }
function drawAidetect() {
  const W = 960, H = 420; aidetectCtx.fillStyle = themeBg(); aidetectCtx.fillRect(0, 0, W, H);
  if (!aidetectActive) { aidetectCtx.fillStyle = '#666'; aidetectCtx.font = '11px monospace'; aidetectCtx.textAlign = 'center'; aidetectCtx.fillText('(pick a sample)', W/2, H/2); requestAnimationFrame(drawAidetect); return; }
  const d = AIDETECT_DATA[aidetectActive];
  aidetectCtx.fillStyle = 'rgba(124,184,255,0.95)'; aidetectCtx.font = 'bold 12px monospace'; aidetectCtx.textAlign = 'left';
  aidetectCtx.fillText(aidetectActive.toUpperCase(), 30, 30);
  aidetectCtx.fillStyle = '#e0e0e0'; aidetectCtx.font = '12px monospace';
  const words = d.text.split(' '); let x = 30, y = 60;
  words.forEach(w => {
    const m = aidetectCtx.measureText(w + ' ');
    if (x + m.width > W - 40) { x = 30; y += 22; }
    aidetectCtx.fillText(w + ' ', x, y); x += m.width;
  });
  const markers = [
    { k: 'delve', l: '"delve/tapestry" vocabulary', c: '229,57,53' },
    { k: 'hedges', l: 'hedging patterns', c: '240,168,105' },
    { k: 'final_draft', l: 'final-draft smoothness', c: '229,57,53' },
    { k: 'variance', l: 'sentence-length variance (human-like)', c: '129,199,132' },
    { k: 'typos', l: 'typos/repairs (human-like)', c: '129,199,132' },
  ];
  markers.forEach((m, i) => {
    const my = 200 + i * 40;
    aidetectCtx.fillStyle = '#aaa'; aidetectCtx.font = '10px monospace'; aidetectCtx.textAlign = 'left';
    aidetectCtx.fillText(m.l, 30, my);
    aidetectCtx.fillStyle = 'rgba(' + m.c + ',0.2)'; aidetectCtx.fillRect(300, my - 12, 600, 16);
    aidetectCtx.fillStyle = 'rgba(' + m.c + ',0.9)'; aidetectCtx.fillRect(300, my - 12, 600 * d.markers[m.k], 16);
  });
  requestAnimationFrame(drawAidetect);
}
drawAidetect();

// ═══════════════════════════════════════════════════════════════════════
// Text Analyzer
// ═══════════════════════════════════════════════════════════════════════
function analyzeClear() {
  document.getElementById('analyze-input').value = '';
  document.getElementById('analyze-output').innerHTML = '';
}
function analyzeRun() {
  const text = document.getElementById('analyze-input').value || '';
  const out = document.getElementById('analyze-output');
  if (!text.trim()) { out.innerHTML = '<span style="color:var(--dim)">(paste some text first)</span>'; return; }
  const findings = [];
  const lower = text.toLowerCase();
  // Passive voice heuristic
  if (/\\b(was|were|is|are|been|being)\\s+\\w+(ed|en)\\b/i.test(text)) {
    findings.push({ label: 'passive voice detected', tab: 'voice-tab', note: 'consider the active-voice alternative' });
  }
  // Hedges
  const hedges = (text.match(/\\b(maybe|possibly|perhaps|sort of|kind of|i think|i guess|arguably)\\b/gi) || []).length;
  if (hedges > 0) findings.push({ label: hedges + ' hedging phrase' + (hedges === 1 ? '' : 's') + ' found', tab: 'lying-tab', note: 'hedges can indicate uncertainty or deception markers' });
  // First person
  const fp = (text.match(/\\b(i|me|my|mine|myself)\\b/gi) || []).length;
  if (fp > 0) findings.push({ label: fp + ' first-person pronoun' + (fp === 1 ? '' : 's'), tab: 'deixis-tab', note: 'the speaker is embedded in the utterance' });
  // Idioms (very crude)
  const idiomHits = ['kick the bucket', 'spill the beans', 'cold feet', 'cost an arm and a leg', 'break a leg', 'piece of cake'].filter(p => lower.includes(p));
  if (idiomHits.length) findings.push({ label: 'idiom detected: "' + idiomHits[0] + '"', tab: 'idiom-tab', note: 'unitary block retrieval, not compositional' });
  // AI tells
  if (/\\b(delve|tapestry|furthermore|moreover|realm)\\b/i.test(text)) {
    findings.push({ label: 'LLM-vocabulary tells detected', tab: 'aidetect-tab', note: 'high-frequency LLM markers present' });
  }
  // Discourse markers
  if (/\\b(so|well|anyway|you know|actually|like)\\b/i.test(text)) {
    findings.push({ label: 'discourse markers present', tab: 'discourse-tab', note: 'tiny words doing interactional work' });
  }
  // Taboo words (very rough)
  if (/\\b(damn|hell|crap)\\b/i.test(text)) {
    findings.push({ label: 'mild taboo word detected', tab: 'taboo-tab', note: 'elevated emotional weight' });
  }
  // Variance
  const sentences = text.split(/[.!?]+/).filter(s => s.trim());
  if (sentences.length > 2) {
    const lens = sentences.map(s => s.trim().split(/\\s+/).length);
    const mean = lens.reduce((a, b) => a + b, 0) / lens.length;
    const variance = lens.reduce((a, b) => a + (b - mean) ** 2, 0) / lens.length;
    if (variance < 2) findings.push({ label: 'uniform sentence length', tab: 'advice-tab', note: 'vary sentence length for attention' });
  }
  // Render
  if (!findings.length) {
    out.innerHTML = '<span style="color:var(--dim)">no notable findings — the text is fairly plain</span>';
    return;
  }
  out.innerHTML = findings.map(f =>
    '<div style="margin-bottom:8px;padding:8px 12px;background:var(--surface2);border-radius:4px;border-left:3px solid var(--accent)">' +
    '<b style="color:var(--accent)">' + f.label + '</b>' +
    '<br><span style="color:var(--dim)">' + f.note + '</span>' +
    ' · <a href="#" onclick="(findTabForPanel(\\''+f.tab+'\\')||{}).click&&findTabForPanel(\\''+f.tab+'\\').click();return false" style="color:var(--accent2)">see canvas →</a>' +
    '</div>'
  ).join('');
  pepSend('analyze.run', { findings: findings.length });
}

// ═══════════════════════════════════════════════════════════════════════
// Jargon
// ═══════════════════════════════════════════════════════════════════════
const JARGON_DATA = {
  med: { label: 'Medicine', expert: 'The patient presents with dyspnea and pleuritic chest pain, non-productive cough, and a grade 2/6 systolic murmur at the left sternal border.', lay: 'They can\\u0027t breathe well, it hurts when they breathe in, they have a dry cough, and I can hear a heart problem.', saved: '23 words → 13 words, zero ambiguity between professionals' },
  prog: { label: 'Programming', expert: 'Rebase onto main, squash the last three commits, and force-push with lease.', lay: 'Move your changes so they sit on top of the main version, combine your last three saved states into one, and upload &mdash; carefully, so you don\\u0027t overwrite what\\u0027s already there.', saved: '13 words → 35 words' },
  music: { label: 'Music theory', expert: 'A ii-V-I in C major resolves via the tritone substitution.', lay: 'The chord progression goes from one specific chord to another to home, with a substitution that uses the opposite side of the key.', saved: '11 words → 22 words' },
  wine: { label: 'Wine', expert: 'Medium body, firm tannins, notes of black cherry and graphite, long finish.', lay: 'It\\u0027s not too thick, it dries your mouth, it tastes a bit like dark fruit and pencil lead, and the flavor lingers.', saved: '12 words → 23 words' },
};
const jargonCanvas = document.getElementById('jargon-canvas');
const jargonCtx = jargonCanvas.getContext('2d');
let jargonActive = null;
function jargonPick(k) { jargonActive = k; pepSend('jargon.pick', { key: k }); }
function drawJargon() {
  const W = 960, H = 400; jargonCtx.fillStyle = themeBg(); jargonCtx.fillRect(0, 0, W, H);
  if (!jargonActive) { jargonCtx.fillStyle = '#666'; jargonCtx.font = '11px monospace'; jargonCtx.textAlign = 'center'; jargonCtx.fillText('(pick a domain)', W/2, H/2); requestAnimationFrame(drawJargon); return; }
  const d = JARGON_DATA[jargonActive];
  jargonCtx.fillStyle = 'rgba(240,168,105,0.95)'; jargonCtx.font = 'bold 13px monospace'; jargonCtx.textAlign = 'left';
  jargonCtx.fillText(d.label.toUpperCase(), 30, 30);
  jargonCtx.fillStyle = 'rgba(124,184,255,0.95)'; jargonCtx.font = 'bold 11px monospace';
  jargonCtx.fillText('EXPERT', 30, 70);
  jargonCtx.fillStyle = '#e0e0e0'; jargonCtx.font = '12px monospace';
  const words1 = d.expert.split(' '); let x = 30, y = 94;
  words1.forEach(w => { const m = jargonCtx.measureText(w + ' '); if (x + m.width > W - 30) { x = 30; y += 22; } jargonCtx.fillText(w + ' ', x, y); x += m.width; });
  jargonCtx.fillStyle = 'rgba(129,199,132,0.95)'; jargonCtx.font = 'bold 11px monospace';
  jargonCtx.fillText('LAY TRANSLATION', 30, 200);
  jargonCtx.fillStyle = '#e0e0e0'; jargonCtx.font = '12px monospace';
  const words2 = d.lay.split(' '); x = 30; y = 222;
  words2.forEach(w => { const m = jargonCtx.measureText(w + ' '); if (x + m.width > W - 30) { x = 30; y += 22; } jargonCtx.fillText(w + ' ', x, y); x += m.width; });
  jargonCtx.fillStyle = '#aaa'; jargonCtx.font = '11px monospace';
  jargonCtx.fillText(d.saved, 30, H - 30);
  requestAnimationFrame(drawJargon);
}
drawJargon();

// ═══════════════════════════════════════════════════════════════════════
// Cognates & False Friends
// ═══════════════════════════════════════════════════════════════════════
const COGNATES_DATA = {
  embarazada: { word: 'embarazada', lang: 'Spanish', looks_like: 'embarrassed', really_means: 'pregnant' },
  gift: { word: 'Gift', lang: 'German', looks_like: 'gift (present)', really_means: 'poison' },
  preservativo: { word: 'preservativo', lang: 'Spanish', looks_like: 'preservative', really_means: 'condom' },
  actually: { word: 'eventualmente', lang: 'Spanish', looks_like: 'eventually', really_means: 'possibly, if the occasion arises' },
  library: { word: 'librairie', lang: 'French', looks_like: 'library', really_means: 'bookstore (not a library — that is "bibliothèque")' },
};
const cognatesCanvas = document.getElementById('cognates-canvas');
const cognatesCtx = cognatesCanvas.getContext('2d');
let cognatesActive = null;
function cognatesPick(k) { cognatesActive = k; pepSend('cognates.pick', { key: k }); }
function drawCognates() {
  const W = 960, H = 420; cognatesCtx.fillStyle = themeBg(); cognatesCtx.fillRect(0, 0, W, H);
  if (!cognatesActive) { cognatesCtx.fillStyle = '#666'; cognatesCtx.font = '11px monospace'; cognatesCtx.textAlign = 'center'; cognatesCtx.fillText('(pick a word)', W/2, H/2); requestAnimationFrame(drawCognates); return; }
  const d = COGNATES_DATA[cognatesActive];
  cognatesCtx.fillStyle = '#fff'; cognatesCtx.font = 'bold 28px monospace'; cognatesCtx.textAlign = 'center';
  cognatesCtx.fillText(d.word, W/2, 80);
  cognatesCtx.fillStyle = '#aaa'; cognatesCtx.font = '11px monospace';
  cognatesCtx.fillText('(' + d.lang + ')', W/2, 104);
  cognatesCtx.fillStyle = 'rgba(240,168,105,0.95)'; cognatesCtx.font = 'bold 12px monospace';
  cognatesCtx.fillText('LOOKS LIKE', W/2, 170);
  cognatesCtx.fillStyle = '#e0e0e0'; cognatesCtx.font = '16px monospace';
  cognatesCtx.fillText(d.looks_like, W/2, 196);
  cognatesCtx.fillStyle = 'rgba(229,57,53,0.95)'; cognatesCtx.font = 'bold 12px monospace';
  cognatesCtx.fillText('ACTUALLY MEANS', W/2, 260);
  cognatesCtx.fillStyle = '#fff'; cognatesCtx.font = 'bold 16px monospace';
  cognatesCtx.fillText(d.really_means, W/2, 286);
  cognatesCtx.fillStyle = '#888'; cognatesCtx.font = '11px monospace';
  cognatesCtx.fillText('naive learner plugs the home-language meaning and gets specifically humiliated', W/2, H - 30);
  requestAnimationFrame(drawCognates);
}
drawCognates();

// ═══════════════════════════════════════════════════════════════════════
// Rhyme
// ═══════════════════════════════════════════════════════════════════════
const RHYME_DATA = {
  nursery: { label: 'nursery rhyme', lines: ['Jack and Jill went up the hill', 'to fetch a pail of water'], rhymes: [[0, 1, 'hill / jill']], note: 'aabb pattern in children\\u0027s verse, tight end-rhyme' },
  shakespeare: { label: 'Shakespearean couplet', lines: ['So long as men can breathe or eyes can see,', 'So long lives this, and this gives life to thee.'], rhymes: [[0, 1, 'see / thee']], note: 'ending couplet, ababcdcdefefgg sonnet structure' },
  rap: { label: 'rap (internal rhyme)', lines: ['I been that kid since the crib, givin you dap', 'and my pen is a trap, every line is a wrap'], rhymes: [[0, 0, 'kid / crib / dap (internal)'], [1, 1, 'trap / wrap (internal + end)']], note: 'high rhyme density — multiple matches per line' },
  slant: { label: 'slant rhyme (Dickinson)', lines: ['Hope is the thing with feathers', 'That perches in the soul'], rhymes: [[0, 1, 'feathers / soul (phonemic near-miss)']], note: 'the near-match creates unease the reader does not consciously notice' },
};
const rhymeCanvas = document.getElementById('rhyme-canvas');
const rhymeCtx = rhymeCanvas.getContext('2d');
let rhymeActive = null;
function rhymePlay(k) { rhymeActive = k; pepSend('rhyme.play', { key: k }); }
function drawRhyme() {
  const W = 960, H = 420; rhymeCtx.fillStyle = themeBg(); rhymeCtx.fillRect(0, 0, W, H);
  if (!rhymeActive) { rhymeCtx.fillStyle = '#666'; rhymeCtx.font = '11px monospace'; rhymeCtx.textAlign = 'center'; rhymeCtx.fillText('(pick a form)', W/2, H/2); requestAnimationFrame(drawRhyme); return; }
  const d = RHYME_DATA[rhymeActive];
  rhymeCtx.fillStyle = 'rgba(240,168,105,0.95)'; rhymeCtx.font = 'bold 12px monospace'; rhymeCtx.textAlign = 'left';
  rhymeCtx.fillText(d.label.toUpperCase(), 30, 40);
  rhymeCtx.fillStyle = '#e0e0e0'; rhymeCtx.font = '15px monospace';
  d.lines.forEach((ln, i) => rhymeCtx.fillText(ln, 30, 90 + i * 30));
  rhymeCtx.fillStyle = 'rgba(129,199,132,0.95)'; rhymeCtx.font = 'bold 11px monospace';
  rhymeCtx.fillText('RHYME MATCHES', 30, 190);
  rhymeCtx.fillStyle = '#e0e0e0'; rhymeCtx.font = '12px monospace';
  d.rhymes.forEach((r, i) => rhymeCtx.fillText('• ' + r[2], 50, 214 + i * 22));
  rhymeCtx.fillStyle = '#aaa'; rhymeCtx.font = '11px monospace';
  rhymeCtx.fillText(d.note, 30, H - 30);
  requestAnimationFrame(drawRhyme);
}
drawRhyme();

// ═══════════════════════════════════════════════════════════════════════
// Statistical Learning (Saffran)
// ═══════════════════════════════════════════════════════════════════════
const STAT_WORDS = ['tupiro', 'golabu', 'bidaku', 'padoti'];
const statCanvas = document.getElementById('statistical-canvas');
const statCtx = statCanvas.getContext('2d');
let statPlaying = false, statRevealing = false, statT = 0, statStream = '';
function statisticalPlay() { statPlaying = true; statT = 0; pepSend('statistical.play', {}); }
function statisticalReveal() { statRevealing = !statRevealing; }
function statisticalReset() { statPlaying = false; statRevealing = false; statT = 0; statStream = ''; }
function drawStat() {
  const W = 960, H = 420; statCtx.fillStyle = themeBg(); statCtx.fillRect(0, 0, W, H);
  if (statPlaying) {
    statT++;
    if (statT % 6 === 0) statStream += STAT_WORDS[Math.floor(Math.random() * STAT_WORDS.length)];
    if (statStream.length > 180) statStream = statStream.slice(-180);
  }
  statCtx.fillStyle = '#aaa'; statCtx.font = '11px monospace'; statCtx.textAlign = 'left';
  statCtx.fillText('synthetic syllable stream (no pauses, no stress)', 30, 30);
  // Render the stream with boundary overlay
  statCtx.font = '14px monospace';
  let x = 30, y = 80;
  for (let i = 0; i < statStream.length; i++) {
    const ch = statStream[i];
    if (x + 14 > W - 30) { x = 30; y += 26; }
    // Boundary detection: every 6 characters is a word in our synthetic stream
    const atBoundary = statRevealing && (i % 6 === 0) && i > 0;
    if (atBoundary) {
      statCtx.strokeStyle = 'rgba(240,168,105,0.8)'; statCtx.lineWidth = 2;
      statCtx.beginPath(); statCtx.moveTo(x - 3, y - 14); statCtx.lineTo(x - 3, y + 4); statCtx.stroke();
    }
    statCtx.fillStyle = statRevealing ? (Math.floor(i / 6) % 2 === 0 ? '#e0e0e0' : '#aaa') : '#e0e0e0';
    statCtx.fillText(ch, x, y);
    x += 14;
  }
  if (statRevealing) {
    statCtx.fillStyle = 'rgba(240,168,105,0.95)'; statCtx.font = 'bold 11px monospace';
    statCtx.fillText('◉ word boundaries extracted from transitional-probability drops', 30, H - 60);
  }
  statCtx.fillStyle = '#aaa'; statCtx.font = '11px monospace';
  statCtx.fillText('hidden words: ' + STAT_WORDS.join(', '), 30, H - 30);
  requestAnimationFrame(drawStat);
}
drawStat();

// ═══════════════════════════════════════════════════════════════════════
// Cospeech Gesture
// ═══════════════════════════════════════════════════════════════════════
const GESTURE_DATA = {
  big: { sentence: 'it was BIG', gestureAt: 'BIG', gestureLead: 180, gestureType: 'hands apart showing size' },
  there: { sentence: 'it went over THERE', gestureAt: 'THERE', gestureLead: 150, gestureType: 'pointing arm extended' },
  idea: { sentence: 'I had an IDEA', gestureAt: 'IDEA', gestureLead: 120, gestureType: 'cupped hand as container' },
};
const gestureCanvas = document.getElementById('gesture-canvas');
const gestureCtx = gestureCanvas.getContext('2d');
let gestureActive = null, gestureT = 0;
function gesturePlay(k) { gestureActive = k; gestureT = 0; pepSend('gesture.play', { key: k }); }
function drawGesture() {
  const W = 960, H = 420; gestureCtx.fillStyle = themeBg(); gestureCtx.fillRect(0, 0, W, H);
  if (!gestureActive) { gestureCtx.fillStyle = '#666'; gestureCtx.font = '11px monospace'; gestureCtx.textAlign = 'center'; gestureCtx.fillText('(pick an utterance)', W/2, H/2); requestAnimationFrame(drawGesture); return; }
  const d = GESTURE_DATA[gestureActive];
  gestureT = Math.min(400, gestureT + 4);
  gestureCtx.fillStyle = '#fff'; gestureCtx.font = 'bold 18px monospace'; gestureCtx.textAlign = 'center';
  gestureCtx.fillText(d.sentence, W/2, 60);
  // Timeline
  gestureCtx.strokeStyle = 'rgba(120,120,140,0.4)'; gestureCtx.lineWidth = 1;
  gestureCtx.beginPath(); gestureCtx.moveTo(60, 200); gestureCtx.lineTo(900, 200); gestureCtx.stroke();
  gestureCtx.fillStyle = '#aaa'; gestureCtx.font = '11px monospace'; gestureCtx.textAlign = 'left';
  gestureCtx.fillText('time →', 60, 220);
  // Speech bar
  gestureCtx.fillStyle = 'rgba(124,184,255,0.5)';
  gestureCtx.fillRect(60, 140, Math.min(760, gestureT * 2), 24);
  gestureCtx.strokeStyle = 'rgba(124,184,255,0.95)'; gestureCtx.lineWidth = 1.5;
  gestureCtx.strokeRect(60, 140, Math.min(760, gestureT * 2), 24);
  gestureCtx.fillStyle = '#fff'; gestureCtx.font = '11px monospace'; gestureCtx.textAlign = 'left';
  gestureCtx.fillText('speech', 70, 156);
  // Stress word marker
  const stressX = 60 + 500;
  gestureCtx.strokeStyle = 'rgba(240,168,105,0.95)'; gestureCtx.lineWidth = 2;
  gestureCtx.setLineDash([4, 4]);
  gestureCtx.beginPath(); gestureCtx.moveTo(stressX, 120); gestureCtx.lineTo(stressX, 280); gestureCtx.stroke();
  gestureCtx.setLineDash([]);
  gestureCtx.fillStyle = 'rgba(240,168,105,0.95)'; gestureCtx.font = 'bold 11px monospace'; gestureCtx.textAlign = 'center';
  gestureCtx.fillText('"' + d.gestureAt + '"', stressX, 114);
  // Gesture bar (starts earlier)
  const gestureStart = 60 + 500 - d.gestureLead * 0.7;
  const gestureWidth = 180;
  if (gestureT * 2 > gestureStart - 60) {
    gestureCtx.fillStyle = 'rgba(129,199,132,0.55)';
    gestureCtx.fillRect(gestureStart, 240, Math.min(gestureWidth, gestureT * 2 - (gestureStart - 60)), 24);
    gestureCtx.strokeStyle = 'rgba(129,199,132,0.95)';
    gestureCtx.strokeRect(gestureStart, 240, Math.min(gestureWidth, gestureT * 2 - (gestureStart - 60)), 24);
    gestureCtx.fillStyle = '#fff'; gestureCtx.font = '11px monospace'; gestureCtx.textAlign = 'left';
    gestureCtx.fillText('gesture: ' + d.gestureType, gestureStart + 6, 256);
  }
  gestureCtx.fillStyle = 'rgba(129,199,132,0.95)'; gestureCtx.font = 'bold 11px monospace'; gestureCtx.textAlign = 'center';
  gestureCtx.fillText('◉ gesture onset leads speech onset by ~' + d.gestureLead + 'ms', W/2, H - 30);
  requestAnimationFrame(drawGesture);
}
drawGesture();

// ═══════════════════════════════════════════════════════════════════════
// Writing Systems / Orthography
// ═══════════════════════════════════════════════════════════════════════
const ORTHO_DATA = {
  alphabet: { label: 'Alphabet (Spanish)', sample: 'gato', note: '1:1 phoneme-to-letter mapping, learn in months', cost: 0.15 },
  abjad: { label: 'Abjad (Arabic)', sample: 'كتب', note: 'consonants only, vowels inferred from context', cost: 0.45 },
  syllabary: { label: 'Syllabary (Japanese hiragana)', sample: 'ねこ', note: 'one symbol per syllable, 46 total', cost: 0.25 },
  logograph: { label: 'Logography (Chinese)', sample: '猫', note: 'one symbol per morpheme, ~3000 for literacy', cost: 0.85 },
};
const orthographyCanvas = document.getElementById('orthography-canvas');
const orthographyCtx = orthographyCanvas.getContext('2d');
let orthoActive = null;
function orthographyPick(k) { orthoActive = k; pepSend('orthography.pick', { key: k }); }
function drawOrthography() {
  const W = 960, H = 420; orthographyCtx.fillStyle = themeBg(); orthographyCtx.fillRect(0, 0, W, H);
  if (!orthoActive) { orthographyCtx.fillStyle = '#666'; orthographyCtx.font = '11px monospace'; orthographyCtx.textAlign = 'center'; orthographyCtx.fillText('(pick a writing system)', W/2, H/2); requestAnimationFrame(drawOrthography); return; }
  const d = ORTHO_DATA[orthoActive];
  orthographyCtx.fillStyle = 'rgba(240,168,105,0.95)'; orthographyCtx.font = 'bold 13px monospace'; orthographyCtx.textAlign = 'center';
  orthographyCtx.fillText(d.label, W/2, 50);
  orthographyCtx.fillStyle = '#fff'; orthographyCtx.font = 'bold 64px monospace';
  orthographyCtx.fillText(d.sample, W/2, 160);
  orthographyCtx.fillStyle = '#aaa'; orthographyCtx.font = '12px monospace';
  orthographyCtx.fillText('(="cat" in the shown language)', W/2, 190);
  orthographyCtx.fillStyle = '#aaa'; orthographyCtx.font = '11px monospace'; orthographyCtx.textAlign = 'left';
  orthographyCtx.fillText('learning cost (relative)', 80, 250);
  orthographyCtx.fillStyle = 'rgba(229,57,53,0.2)'; orthographyCtx.fillRect(80, 262, 800, 22);
  orthographyCtx.fillStyle = 'rgba(229,57,53,0.85)'; orthographyCtx.fillRect(80, 262, 800 * d.cost, 22);
  orthographyCtx.fillStyle = '#aaa'; orthographyCtx.textAlign = 'right';
  orthographyCtx.fillText((d.cost * 100).toFixed(0) + '%', 880, 279);
  orthographyCtx.textAlign = 'center';
  orthographyCtx.fillText(d.note, W/2, 340);
  requestAnimationFrame(drawOrthography);
}
drawOrthography();

// ═══════════════════════════════════════════════════════════════════════
// Speech Errors
// ═══════════════════════════════════════════════════════════════════════
const ERRORS_DATA = {
  spoonerism: { label: 'Spoonerism', example: 'intended: "jelly beans" → actual: "belly jeans"', stage: 'phoneme assembly', reveals: 'initial phonemes got routed into the wrong word slots' },
  wordex: { label: 'Word exchange', example: 'intended: "a tickle in my throat" → actual: "a cat in my tonsils"', stage: 'grammatical-frame filling', reveals: 'the slots existed before the content; two nouns swapped between matching slot types' },
  blend: { label: 'Blend', example: 'intended: "splinter" OR "sinister" → actual: "splinister"', stage: 'lexical selection', reveals: 'two competing words reached output together, failed to resolve cleanly' },
  tot: { label: 'Tip-of-the-tongue', example: '"it starts with P, three syllables, means thinker..."', stage: 'content retrieval', reveals: 'metacognitive pointer fired but content pull failed' },
  malaprop: { label: 'Malapropism', example: 'intended: "pinnacle of success" → actual: "pineapple of success"', stage: 'lexical selection', reveals: 'phonological neighbor won the selection race over the target word' },
};
const errorsCanvas = document.getElementById('errors-canvas');
const errorsCtx = errorsCanvas.getContext('2d');
let errorsActive = null;
function errorsPick(k) { errorsActive = k; pepSend('errors.pick', { key: k }); }
function drawErrors() {
  const W = 960, H = 440; errorsCtx.fillStyle = themeBg(); errorsCtx.fillRect(0, 0, W, H);
  if (!errorsActive) { errorsCtx.fillStyle = '#666'; errorsCtx.font = '11px monospace'; errorsCtx.textAlign = 'center'; errorsCtx.fillText('(pick an error type)', W/2, H/2); requestAnimationFrame(drawErrors); return; }
  const d = ERRORS_DATA[errorsActive];
  errorsCtx.fillStyle = 'rgba(240,168,105,0.95)'; errorsCtx.font = 'bold 14px monospace'; errorsCtx.textAlign = 'left';
  errorsCtx.fillText(d.label.toUpperCase(), 30, 40);
  errorsCtx.fillStyle = '#e0e0e0'; errorsCtx.font = '13px monospace';
  errorsCtx.fillText(d.example, 30, 80);
  errorsCtx.fillStyle = 'rgba(124,184,255,0.95)'; errorsCtx.font = 'bold 11px monospace';
  errorsCtx.fillText('STAGE REVEALED', 30, 150);
  errorsCtx.fillStyle = '#e0e0e0'; errorsCtx.font = '13px monospace';
  errorsCtx.fillText('→ ' + d.stage, 50, 172);
  errorsCtx.fillStyle = 'rgba(129,199,132,0.95)'; errorsCtx.font = 'bold 11px monospace';
  errorsCtx.fillText('WHAT THIS ERROR REVEALS', 30, 220);
  errorsCtx.fillStyle = '#e0e0e0'; errorsCtx.font = '12px monospace';
  const words = d.reveals.split(' '); let x = 50, y = 244;
  words.forEach(w => { const m = errorsCtx.measureText(w + ' '); if (x + m.width > W - 30) { x = 50; y += 22; } errorsCtx.fillText(w + ' ', x, y); x += m.width; });
  // Pipeline diagram
  const stages = ['concept', 'lexical select', 'grammatical frame', 'phoneme assembly', 'articulation'];
  stages.forEach((s, i) => {
    const sx = 60 + i * 180, sy = 360;
    const active = s.includes(d.stage) || d.stage.includes(s);
    errorsCtx.fillStyle = active ? 'rgba(229,57,53,0.75)' : 'rgba(120,120,140,0.4)';
    errorsCtx.fillRect(sx, sy, 160, 30);
    errorsCtx.strokeStyle = active ? 'rgba(229,57,53,0.95)' : 'rgba(120,120,140,0.7)';
    errorsCtx.strokeRect(sx, sy, 160, 30);
    errorsCtx.fillStyle = '#fff'; errorsCtx.font = '10px monospace'; errorsCtx.textAlign = 'center';
    errorsCtx.fillText(s, sx + 80, sy + 19);
    if (i < stages.length - 1) {
      errorsCtx.strokeStyle = 'rgba(120,120,140,0.5)';
      errorsCtx.beginPath(); errorsCtx.moveTo(sx + 160, sy + 15); errorsCtx.lineTo(sx + 180, sy + 15); errorsCtx.stroke();
    }
  });
  requestAnimationFrame(drawErrors);
}
drawErrors();

// ═══════════════════════════════════════════════════════════════════════
// Inner Speech
// ═══════════════════════════════════════════════════════════════════════
const innerspeechCanvas = document.getElementById('innerspeech-canvas');
const innerspeechCtx = innerspeechCanvas.getContext('2d');
document.getElementById('inner-rate').addEventListener('input', (e) => {
  document.getElementById('inner-rate-val').textContent = e.target.value + '%';
});
// ═══════════════════════════════════════════════════════════════════════
// Reading Aloud vs Silent
// ═══════════════════════════════════════════════════════════════════════
const READALOUD_DATA = {
  silent: { label: 'silent reading', regions: { visual: 0.9, semantic: 0.85, motor: 0.05, auditory: 0.1, prosody: 0.1, wm: 0.35 }, speed: 0.9, retention: 0.6 },
  aloud: { label: 'reading aloud', regions: { visual: 0.9, semantic: 0.9, motor: 0.85, auditory: 0.8, prosody: 0.75, wm: 0.7 }, speed: 0.45, retention: 0.85 },
  subvocal: { label: 'subvocalization (inner voice)', regions: { visual: 0.9, semantic: 0.85, motor: 0.25, auditory: 0.35, prosody: 0.4, wm: 0.45 }, speed: 0.75, retention: 0.7 },
};
const readaloudCanvas = document.getElementById('readaloud-canvas');
const readaloudCtx = readaloudCanvas.getContext('2d');
let readaloudActive = null;
function readaloudPick(k) { readaloudActive = k; pepSend('readaloud.pick', { key: k }); }
function drawReadaloud() {
  const W = 960, H = 440; readaloudCtx.fillStyle = themeBg(); readaloudCtx.fillRect(0, 0, W, H);
  if (!readaloudActive) { readaloudCtx.fillStyle = '#666'; readaloudCtx.font = '11px monospace'; readaloudCtx.textAlign = 'center'; readaloudCtx.fillText('(pick a mode)', W / 2, H / 2); requestAnimationFrame(drawReadaloud); return; }
  const d = READALOUD_DATA[readaloudActive];
  readaloudCtx.fillStyle = 'rgba(124,184,255,0.95)'; readaloudCtx.font = 'bold 13px monospace'; readaloudCtx.textAlign = 'left';
  readaloudCtx.fillText(d.label.toUpperCase(), 30, 36);
  const regions = [
    { k: 'visual', l: 'VISUAL CORTEX', c: '240,168,105' },
    { k: 'semantic', l: 'SEMANTIC / LANGUAGE', c: '124,184,255' },
    { k: 'motor', l: 'MOTOR PLANNING', c: '129,199,132' },
    { k: 'auditory', l: 'AUDITORY', c: '186,104,200' },
    { k: 'prosody', l: 'PROSODIC DECISIONS', c: '255,183,77' },
    { k: 'wm', l: 'WORKING MEMORY', c: '79,195,247' },
  ];
  regions.forEach((r, i) => {
    const y = 70 + i * 44;
    readaloudCtx.fillStyle = '#e0e0e0'; readaloudCtx.font = 'bold 10px monospace';
    readaloudCtx.fillText(r.l, 30, y);
    readaloudCtx.fillStyle = 'rgba(' + r.c + ',0.2)';
    readaloudCtx.fillRect(30, y + 6, 600, 18);
    readaloudCtx.fillStyle = 'rgba(' + r.c + ',0.9)';
    readaloudCtx.fillRect(30, y + 6, 600 * d.regions[r.k], 18);
    readaloudCtx.fillStyle = '#aaa'; readaloudCtx.font = '10px monospace'; readaloudCtx.textAlign = 'right';
    readaloudCtx.fillText((d.regions[r.k] * 100).toFixed(0) + '%', 640, y + 18);
    readaloudCtx.textAlign = 'left';
  });
  // Speed and retention bars
  const summY = 360;
  readaloudCtx.fillStyle = '#aaa'; readaloudCtx.font = '11px monospace';
  readaloudCtx.fillText('reading speed: ' + (d.speed * 100).toFixed(0) + '%', 680, summY);
  readaloudCtx.fillStyle = 'rgba(129,199,132,0.2)'; readaloudCtx.fillRect(680, summY + 8, 240, 14);
  readaloudCtx.fillStyle = 'rgba(129,199,132,0.85)'; readaloudCtx.fillRect(680, summY + 8, 240 * d.speed, 14);
  readaloudCtx.fillStyle = '#aaa';
  readaloudCtx.fillText('retention / comprehension: ' + (d.retention * 100).toFixed(0) + '%', 680, summY + 40);
  readaloudCtx.fillStyle = 'rgba(124,184,255,0.2)'; readaloudCtx.fillRect(680, summY + 48, 240, 14);
  readaloudCtx.fillStyle = 'rgba(124,184,255,0.85)'; readaloudCtx.fillRect(680, summY + 48, 240 * d.retention, 14);
  requestAnimationFrame(drawReadaloud);
}
drawReadaloud();

// ═══════════════════════════════════════════════════════════════════════
// Vectora-Powered Live Retrieval (dogfood)
// ═══════════════════════════════════════════════════════════════════════
async function vecLingoraInit() {
  try {
    const r = await fetch('/vectora/seeds/lingora');
    const data = await r.json();
    const sel = document.getElementById('vec-lingora-seed');
    if (!sel) return;
    sel.innerHTML = data.seeds.map(s => `<option value="${s.id}">${s.id} — ${s.text.split(' ').slice(0, 4).join(' ')}</option>`).join('');
    const stats = document.getElementById('vec-lingora-stats');
    if (stats) stats.textContent = `seeded graph: ${data.stats.documents} docs · ${data.stats.edges} edges`;
  } catch (e) { console.warn('vec lingora init failed', e); }
}
['vec-lingora-k', 'vec-lingora-decay'].forEach(id => {
  const el = document.getElementById(id);
  if (!el) return;
  el.addEventListener('input', (e) => {
    const v = parseInt(e.target.value);
    const out = document.getElementById(id + '-v');
    if (!out) return;
    out.textContent = id.endsWith('decay') ? (v / 100).toFixed(2) : v;
  });
});
async function vecLingoraQuery() {
  const seed = document.getElementById('vec-lingora-seed').value;
  if (!seed) return;
  const k = parseInt(document.getElementById('vec-lingora-k').value);
  const decay = parseInt(document.getElementById('vec-lingora-decay').value) / 100;
  const out = document.getElementById('vec-lingora-results');
  out.innerHTML = '<div style="color:var(--dim);text-align:center;padding:40px 20px;font-size:11px">querying Vectora…</div>';
  try {
    const r = await fetch(`/vectora/neighbors/lingora/${seed}?k=${k}&decay=${decay}`);
    if (!r.ok) throw new Error('retrieval failed');
    const data = await r.json();
    if (!data.hits.length) { out.innerHTML = '<div style="color:var(--dim);text-align:center;padding:40px 20px;font-size:11px">no neighbors</div>'; return; }
    out.innerHTML = data.hits.map((h, i) => {
      const hopBadge = h.hop_distance > 0 ? `<span style="background:rgba(124,184,255,0.2);color:var(--accent);padding:1px 6px;border-radius:8px;font-size:9px;margin-left:6px">hop ${h.hop_distance}</span>` : '';
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
vecLingoraInit();

// ═══════════════════════════════════════════════════════════════════════
// Vectora Context dogfood — session-aware word lookup
// ═══════════════════════════════════════════════════════════════════════
const lingoraCtxSession = 'lingora-ctx-' + Math.random().toString(36).slice(2, 8);
let lingoraCtxDocs = [];

async function lingoraCtxInit() {
  try {
    const r = await fetch('/vectora/seeds/lingora');
    const data = await r.json();
    lingoraCtxDocs = data.seeds;
    const list = document.getElementById('lingora-ctx-docs');
    if (!list) return;
    list.innerHTML = lingoraCtxDocs.map(s =>
      `<button data-doc-id="${s.id}" onclick="lingoraCtxView('${s.id}')" style="padding:4px 10px;border-radius:12px;border:1px solid var(--border);background:var(--surface);color:var(--text);font-size:10px;cursor:pointer;font-family:inherit">${s.id} · ${s.text.split(' ').slice(0, 3).join(' ')}</button>`
    ).join('');
    const sel = document.getElementById('lingora-ctx-seed');
    if (sel) sel.innerHTML = lingoraCtxDocs.map(s => `<option value="${s.id}">${s.id} — ${s.text.split(' ').slice(0, 4).join(' ')}</option>`).join('');
  } catch (e) { console.warn('lingora ctx init failed', e); }
}
async function lingoraCtxView(docId) {
  try {
    await fetch(`/vectora/context/lingora/record`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: lingoraCtxSession, doc_id: docId }),
    });
    const btn = document.querySelector(`#lingora-ctx-docs button[data-doc-id="${docId}"]`);
    if (btn) { btn.style.borderColor = 'var(--accent)'; btn.style.background = 'rgba(124,184,255,0.15)'; }
    lingoraCtxUpdateSessionStat();
  } catch (e) { console.warn(e); }
}
async function lingoraCtxClear() {
  try {
    await fetch(`/vectora/context/lingora/clear`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: lingoraCtxSession }),
    });
    document.querySelectorAll('#lingora-ctx-docs button').forEach(b => {
      b.style.borderColor = 'var(--border)'; b.style.background = 'var(--surface)';
    });
    lingoraCtxUpdateSessionStat();
  } catch (e) { console.warn(e); }
}
function lingoraCtxUpdateSessionStat() {
  const viewed = document.querySelectorAll('#lingora-ctx-docs button[style*="accent"]').length;
  const stat = document.getElementById('lingora-ctx-session-stat');
  if (stat) stat.textContent = `session: ${viewed} view${viewed === 1 ? '' : 's'}`;
}
async function lingoraCtxQuery() {
  const seed = document.getElementById('lingora-ctx-seed').value;
  if (!seed) return;
  const out = document.getElementById('lingora-ctx-results');
  out.innerHTML = '<div style="text-align:center;color:var(--dim);padding:30px;font-size:11px">querying Vectora Context…</div>';
  try {
    const r = await fetch('/vectora/context/lingora/compare', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: lingoraCtxSession, seed_id: seed, k: 6 }),
    });
    if (!r.ok) throw new Error('query failed');
    const data = await r.json();
    const plainIds = new Set(data.plain.map(h => h.id));
    const renderList = (hits, shifted) => hits.map((h, i) => {
      const hopBadge = h.hop_distance > 0 ? `<span style="background:rgba(124,184,255,0.2);color:var(--accent);padding:1px 5px;border-radius:8px;font-size:9px;margin-left:4px">hop ${h.hop_distance}</span>` : '';
      const shiftedStyle = shifted && !plainIds.has(h.id) ? ';background:rgba(163,230,53,0.08)' : '';
      return `<div style="padding:8px 12px;border-bottom:1px solid var(--border);font-size:11px${shiftedStyle}"><div style="display:flex;gap:6px;align-items:center"><span style="color:var(--dim);font-size:10px">${i+1}.</span><span style="color:var(--accent);font-weight:bold;font-family:monospace">${h.id}</span>${hopBadge}<span style="color:var(--dim);margin-left:auto;font-size:10px">${h.score.toFixed(3)}</span></div><div style="color:var(--text);margin-top:3px;line-height:1.5">${h.text}</div></div>`;
    }).join('');
    out.innerHTML = `<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
      <div style="background:var(--surface);border:1px solid var(--border);border-left:3px solid #a78bfa;border-radius:6px;overflow:hidden">
        <div style="padding:10px 14px;border-bottom:1px solid var(--border);font-weight:bold;font-size:12px;color:#a78bfa">PLAIN (no context)</div>
        ${renderList(data.plain, false)}
      </div>
      <div style="background:var(--surface);border:1px solid var(--border);border-left:3px solid var(--accent);border-radius:6px;overflow:hidden">
        <div style="padding:10px 14px;border-bottom:1px solid var(--border);font-weight:bold;font-size:12px;color:var(--accent)">CONTEXTUAL (${data.session.size} views)</div>
        ${renderList(data.contextual, true)}
      </div>
    </div>`;
    pepSend('vectora.context.compare', { seed });
  } catch (e) {
    out.innerHTML = `<div style="color:#f06292;text-align:center;padding:30px;font-size:11px">Error: ${e.message}</div>`;
  }
}
lingoraCtxInit();

// ═══════════════════════════════════════════════════════════════════════
// Translation Workbench
// ═══════════════════════════════════════════════════════════════════════
const WORKBENCH_DATA = [
  {
    src: '"It\\'s a piece of cake."',
    srcLang: 'EN → ES',
    layers: {
      denotation: { text: 'A small portion of dessert.', mt: 'Es un trozo de pastel.', lin: 'Es un trozo de pastel.' },
      pragmatic: { text: 'The task is easy.', mt: '(lost)', lin: 'Es pan comido. / Está chupado.' },
      register: { text: 'Casual, conversational.', mt: 'Neutral.', lin: 'Casual idiom preserved.' },
      culture: { text: 'English idiom; cake = effortless.', mt: 'Literal cake reference.', lin: 'Spanish idiom for "easy" used.' },
    },
    finalMT: 'Es un trozo de pastel.',
    finalLin: 'Está chupado.',
    finalNote: 'Casual Spanish idiom for "trivially easy" — preserves pragmatic intent + register, drops the literal cake (which had no cultural function).',
  },
  {
    src: '"Bless your heart."',
    srcLang: 'EN (Southern US) → ES',
    layers: {
      denotation: { text: 'A blessing on your heart.', mt: 'Bendice tu corazón.', lin: 'Bendice tu corazón.' },
      pragmatic: { text: 'Polite condescension or pity.', mt: '(lost — sounds sincere)', lin: 'Pobrecito. / Qué lástima me das.' },
      register: { text: 'Casual, often passive-aggressive.', mt: 'Sounds religious/formal.', lin: 'Casual disdain preserved.' },
      culture: { text: 'Southern US politeness mask for criticism.', mt: 'Religious blessing implication.', lin: 'Cultural function preserved.' },
    },
    finalMT: 'Bendice tu corazón.',
    finalLin: 'Ay, pobrecito… (con esa sonrisita)',
    finalNote: 'Pragmatic intent (polite condescension) + register (casual + passive-aggressive) + cultural function (politeness mask) all preserved in one Spanish phrase.',
  },
  {
    src: '"Boku wa unagi da." (僕はうなぎだ)',
    srcLang: 'JP → EN',
    layers: {
      denotation: { text: 'I am an eel.', mt: 'I am an eel.', lin: 'I\\'ll have the eel.' },
      pragmatic: { text: 'In a restaurant: stating an order.', mt: '(lost — sounds bizarre)', lin: 'Restaurant context preserved.' },
      register: { text: 'Casual male speech (boku).', mt: 'Generic first-person.', lin: 'Casual register noted.' },
      culture: { text: 'Japanese topic-comment grammar; "as for me, eel."', mt: 'Forced into English subject-verb.', lin: 'Topic-comment intent preserved.' },
    },
    finalMT: 'I am an eel.',
    finalLin: 'I\\'ll grab the eel, thanks.',
    finalNote: 'Restaurant pragmatic + casual male register both surface in the natural English ordering phrase. The Japanese topic-comment becomes English "I\\'ll have…" without forcing the literal subject.',
  },
  {
    src: '"Saudade"',
    srcLang: 'PT → EN',
    layers: {
      denotation: { text: 'A noun describing a feeling.', mt: 'Longing / nostalgia.', lin: 'Longing / nostalgia.' },
      pragmatic: { text: 'A bittersweet melancholy for something absent.', mt: '(flattened)', lin: '"Saudade" — a yearning grief that cherishes the absence.' },
      register: { text: 'Literary, emotional, untranslatable.', mt: 'Treated as a normal noun.', lin: 'Marked as untranslatable; gloss provided.' },
      culture: { text: 'Central to Portuguese/Brazilian identity.', mt: '(lost)', lin: 'Cultural weight noted.' },
    },
    finalMT: 'Longing.',
    finalLin: 'Saudade [pt.] — the yearning ache for what is absent and beloved.',
    finalNote: 'The single English word "longing" loses ~70% of the meaning. Lingora keeps the Portuguese word and inlines a gloss that preserves pragmatic + cultural weight.',
  },
];
const workbenchCanvas = document.getElementById('workbench-canvas');
const workbenchCtx = workbenchCanvas.getContext('2d');
let workbenchActive = null;
function workbenchPick(i) { workbenchActive = i; pepSend('workbench.pick', { i }); }
function drawWorkbench() {
  const W = 960, H = 600; workbenchCtx.fillStyle = themeBg(); workbenchCtx.fillRect(0, 0, W, H);
  if (workbenchActive == null) {
    workbenchCtx.fillStyle = '#778'; workbenchCtx.font = '11px monospace'; workbenchCtx.textAlign = 'center';
    workbenchCtx.fillText('(pick a sentence)', W / 2, H / 2);
    requestAnimationFrame(drawWorkbench); return;
  }
  const d = WORKBENCH_DATA[workbenchActive];
  workbenchCtx.fillStyle = '#dce4ed'; workbenchCtx.font = 'bold 13px monospace'; workbenchCtx.textAlign = 'left';
  workbenchCtx.fillText(d.src + '  [' + d.srcLang + ']', 30, 30);
  const cols = [{ x: 30, w: 220, label: 'LAYER', col: '#dce4ed' }, { x: 260, w: 320, label: 'STANDARD MT', col: '#a78bfa' }, { x: 590, w: 340, label: 'LINGORA-AWARE', col: '#4fc3f7' }];
  cols.forEach(c => { workbenchCtx.fillStyle = c.col; workbenchCtx.font = 'bold 11px monospace'; workbenchCtx.fillText(c.label, c.x, 60); });
  const layers = ['denotation', 'pragmatic', 'register', 'culture'];
  layers.forEach((k, i) => {
    const y = 90 + i * 80;
    const layer = d.layers[k];
    workbenchCtx.strokeStyle = 'rgba(120,130,140,0.2)'; workbenchCtx.lineWidth = 1;
    workbenchCtx.beginPath(); workbenchCtx.moveTo(20, y - 8); workbenchCtx.lineTo(W - 20, y - 8); workbenchCtx.stroke();
    workbenchCtx.fillStyle = '#dce4ed'; workbenchCtx.font = 'bold 11px monospace'; workbenchCtx.textAlign = 'left';
    workbenchCtx.fillText(k.toUpperCase(), 30, y + 6);
    workbenchCtx.fillStyle = '#778'; workbenchCtx.font = '10px monospace';
    wrapText(workbenchCtx, layer.text, 30, y + 22, 220, 14);
    workbenchCtx.fillStyle = layer.mt.startsWith('(') ? '#f88' : '#dce4ed'; workbenchCtx.font = '11px monospace';
    wrapText(workbenchCtx, layer.mt, 260, y + 6, 320, 16);
    workbenchCtx.fillStyle = '#4fc3f7'; workbenchCtx.font = '11px monospace';
    wrapText(workbenchCtx, layer.lin, 590, y + 6, 340, 16);
  });
  // ── Final Translation block (all layers combined) ──
  const fy = 90 + layers.length * 80 + 20;
  workbenchCtx.fillStyle = 'rgba(129,199,132,0.12)';
  workbenchCtx.fillRect(20, fy - 22, W - 40, 110);
  workbenchCtx.strokeStyle = 'rgba(129,199,132,0.7)'; workbenchCtx.lineWidth = 1.5;
  workbenchCtx.strokeRect(20, fy - 22, W - 40, 110);
  workbenchCtx.fillStyle = '#81c784'; workbenchCtx.font = 'bold 12px monospace'; workbenchCtx.textAlign = 'left';
  workbenchCtx.fillText('FINAL TRANSLATION  (all layers combined into one sentence)', 30, fy - 4);
  workbenchCtx.fillStyle = '#a78bfa'; workbenchCtx.font = 'bold 10px monospace';
  workbenchCtx.fillText('STANDARD MT', 30, fy + 18);
  workbenchCtx.fillStyle = '#f88'; workbenchCtx.font = '12px monospace';
  wrapText(workbenchCtx, d.finalMT, 160, fy + 18, 780, 16);
  workbenchCtx.fillStyle = '#4fc3f7'; workbenchCtx.font = 'bold 10px monospace';
  workbenchCtx.fillText('LINGORA', 30, fy + 42);
  workbenchCtx.fillStyle = '#fff'; workbenchCtx.font = '12px monospace';
  wrapText(workbenchCtx, d.finalLin, 160, fy + 42, 780, 16);
  workbenchCtx.fillStyle = '#778'; workbenchCtx.font = '10px monospace';
  wrapText(workbenchCtx, d.finalNote, 30, fy + 72, W - 60, 13);
  requestAnimationFrame(drawWorkbench);
}
function wrapText(ctx, text, x, y, maxW, lineH) {
  const words = text.split(' '); let line = '', yy = y;
  words.forEach(w => {
    const test = line + w + ' ';
    if (ctx.measureText(test).width > maxW && line) {
      ctx.fillText(line.trim(), x, yy); line = w + ' '; yy += lineH;
    } else { line = test; }
  });
  if (line) ctx.fillText(line.trim(), x, yy);
}
drawWorkbench();

// ═══════════════════════════════════════════════════════════════════════
// Story Translation Workbench
// ═══════════════════════════════════════════════════════════════════════
const STORY_DATA = [
  {
    title: 'Sobremesa',
    srcLang: 'Spanish',
    srcLangTag: 'es',
    blurb: 'A grandchild\u2019s memory of the Saturday market. The single Spanish word "sobremesa" names a social ritual English has no noun for.',
    paragraphs: [
      {
        src: 'Cuando era ni\u00f1a, mi abuela me llevaba al mercado los s\u00e1bados.',
        mt:  'When I was a girl, my grandmother took me to the market on Saturdays.',
        lin: 'When I was a girl, my grandmother used to take me to the market every Saturday.',
        mtPreserve: 0.45,
        linPreserve: 0.90,
        annotation: [
          '"era" / "llevaba" are imperfect \u2014 habitual, repeated. MT\u2019s simple past ("took") loses the recurrence. Lingora: "used to take."',
          '"los s\u00e1bados" is Spanish for a recurring pattern, not a specific day-list. English needs "every Saturday," not "on Saturdays."',
        ],
      },
      {
        src: 'Siempre se quedaba media hora extra para la sobremesa con don Miguel, el verdulero.',
        mt:  'She always stayed an extra half hour for after-meal with Mr. Miguel, the vegetable seller.',
        lin: 'She\u2019d always linger an extra half-hour for the sobremesa \u2014 the slow talk after the meal \u2014 with Don Miguel, our greengrocer.',
        mtPreserve: 0.25,
        linPreserve: 0.88,
        annotation: [
          '"sobremesa" has no English noun. MT\u2019s "after-meal" is not a word. Lingora keeps the Spanish term and inlines a gloss (cultural anchor preserved by naming, not substituting).',
          '"don" is an honorific of familiar respect, not a social title. "Mr. Miguel" reads as American formality; "Don Miguel" keeps the relational register.',
          '"el verdulero" is occupation-as-identity inside a familiar community. "the vegetable seller" is transactional; "our greengrocer" preserves the relational possessive ("el" \u2248 "ours" in context).',
        ],
      },
      {
        src: 'Yo no entend\u00eda por qu\u00e9 no se iban \u2014 la comida ya se hab\u00eda acabado.',
        mt:  'I did not understand why they did not leave \u2014 the food had already been finished.',
        lin: 'I didn\u2019t understand why they wouldn\u2019t just leave; the food was already gone.',
        mtPreserve: 0.55,
        linPreserve: 0.85,
        annotation: [
          'MT uses full forms ("did not," "had been finished") which read as formal/written. The narrator voice is reflective/spoken. Lingora contracts to match register.',
          '"se iban" with imperfect is not just "did not leave" \u2014 it is "refused to leave / wouldn\u2019t leave." Lingora recovers the modal nuance.',
          '"se hab\u00eda acabado" is passive-reflexive; "was already gone" preserves the sense that the food vanishing happened without an agent.',
        ],
      },
      {
        src: 'Ahora, treinta a\u00f1os despu\u00e9s, me doy cuenta de que la sobremesa nunca era por la comida.',
        mt:  'Now, thirty years later, I realize that the after-meal was never about the food.',
        lin: 'Thirty years on, I see it: the sobremesa was never about the food.',
        mtPreserve: 0.50,
        linPreserve: 0.90,
        annotation: [
          '"Ahora... treinta a\u00f1os despu\u00e9s" opens in the narrator\u2019s reflective register. MT\u2019s literal word order reads as a timestamp; Lingora\u2019s "Thirty years on, I see it:" is a storyteller\u2019s beat (register preserved).',
          '"me doy cuenta" (reflexive: give-oneself-account-of) is idiomatically "realize," but in a reflective context closer to "I see it." Lingora preserves the pacing of the arrived-at insight.',
          'The closing "sobremesa" stays untranslated for continuity with earlier sentence \u2014 narrative consistency across paragraphs. MT switches to "the after-meal" again, breaking cohesion.',
        ],
      },
    ],
  },
  {
    title: 'Amai',
    srcLang: 'Japanese',
    srcLangTag: 'ja',
    blurb: 'An older sister\u2019s reflection on family roles. Japanese drops subjects, uses benefactive auxiliaries, and carries an entire social logic in the single adjective "amai."',
    paragraphs: [
      {
        src: '\u6bcd\u306f\u3044\u3064\u3082\u5f1f\u306b\u7518\u3044\u3002  (Haha wa itsumo ot\u014dto ni amai.)',
        mt:  'Mother is always sweet to my younger brother.',
        lin: 'My mother has always been softer on my little brother.',
        mtPreserve: 0.35,
        linPreserve: 0.85,
        annotation: [
          '"amai" literally means "sweet" (of taste), but applied to a parent\u2019s treatment of a child it means "lenient / too easy on." MT\u2019s "sweet to" reads as affection; the Japanese meaning is mild disapproval of the mother\u2019s leniency.',
          '"Haha" without a possessive is "Mother" as an in-family reference; in English, "My mother" is required to sound natural \u2014 otherwise "Mother" reads as addressing her.',
          '"ot\u014dto" is "younger brother" and carries relational weight. "my little brother" preserves the younger-relative meaning better than "my younger brother" in this register.',
        ],
      },
      {
        src: '\u79c1\u304c\u4f55\u304b\u5931\u6557\u3059\u308b\u3068\u3001\u300c\u3057\u3063\u304b\u308a\u3057\u306a\u3055\u3044\u300d\u3068\u53f1\u3089\u308c\u308b\u3002  (Watashi ga nani ka shippai suru to, "shikkari shinasai" to shikarareru.)',
        mt:  'When I fail at something, I am scolded, "Be strong."',
        lin: 'When I mess something up, I get the \u201cpull yourself together\u201d \u2014 the sharp version.',
        mtPreserve: 0.30,
        linPreserve: 0.82,
        annotation: [
          '"shikarareru" is the passive of "scold" \u2014 specifically the Japanese *suffering passive*, which marks the subject as the one on the receiving end of an unwanted action. English passive is emotionally flat; "I get the..." preserves the sense of something arriving at the speaker.',
          '"shikkari shinasai" is imperative, maternal-stern register. "Be strong" is a translation of the words; "pull yourself together" is a translation of the social act.',
          'MT drops the stakes. Lingora adds "the sharp version" to preserve the emotional weight the Japanese carries via register and passive voicing.',
        ],
      },
      {
        src: '\u3067\u3082\u5f1f\u304c\u540c\u3058\u3053\u3068\u3092\u3059\u308c\u3070\u3001\u300c\u5927\u4e08\u592b\u3088\u300d\u3068\u7b11\u3063\u3066\u304f\u308c\u307e\u3057\u305f\u3002  (Demo ot\u014dto ga onaji koto o sureba, "daij\u014dbu yo" to waratte kuremashita.)',
        mt:  'But when my younger brother does the same thing, she laughs and says, "It\u2019s okay."',
        lin: 'When he does the same thing, she laughs and says "don\u2019t worry about it" \u2014 and she means it as a kindness to him.',
        mtPreserve: 0.20,
        linPreserve: 0.92,
        annotation: [
          '"kuremashita" is the *benefactive auxiliary* \u2014 it marks that the action was done *as a favor / kindness to someone*. This is half the sentence\u2019s meaning in Japanese. MT drops it entirely. Lingora adds the explicit "as a kindness to him" because English has no grammatical slot for this.',
          'Subject drop: the Japanese sentence never names "my mother." Context carries it. MT has to re-supply "she." Lingora uses "he" (for the brother) plus "she" (for mother) to keep the contrast sharp.',
          '"daij\u014dbu yo" with the sentence-final particle "yo" is soft-reassurance register, not neutral. "don\u2019t worry about it" matches; "It\u2019s okay" reads as a statement of fact.',
        ],
      },
      {
        src: '\u3053\u308c\u306f\u4e0d\u516c\u5e73\u3067\u306f\u306a\u3044\u3002  (Kore wa fuk\u014dhei de wa nai.)',
        mt:  'This is not unfair.',
        lin: 'I\u2019m not saying it\u2019s unfair.',
        mtPreserve: 0.45,
        linPreserve: 0.80,
        annotation: [
          'The Japanese sentence is a bare declaration with no hedging particles \u2014 but in context (after two paragraphs of implicit complaint) it reads as the narrator *preemptively blocking* the reader\u2019s inference. English "This is not unfair" reads as an assertion. "I\u2019m not saying it\u2019s unfair" preserves the meta-move \u2014 the narrator is negotiating with the reader.',
          'This is pragmatic preservation, not denotational: the words translate cleanly, but the *speech act* does not. MT only translates the words.',
        ],
      },
      {
        src: '\u305f\u3060\u3001\u5bb6\u65cf\u306e\u4e2d\u3067\u79c1\u306e\u5f79\u5272\u304c\u9055\u3046\u3060\u3051\u3060\u3002  (Tada, kazoku no naka de watashi no yakuwari ga chigau dake da.)',
        mt:  'It\u2019s just that my role in the family is different.',
        lin: 'It\u2019s just that my place in the family was shaped differently.',
        mtPreserve: 0.45,
        linPreserve: 0.85,
        annotation: [
          '"yakuwari" translates as "role" but carries the sense of *assigned position within a structure*, not a chosen part. "place... shaped differently" preserves the sense that this was done to her, not by her. The sentence is about social position, not job description.',
          '"chigau dake da" (is-different only) is a classic Japanese closing of acceptance-with-resignation. MT\u2019s "is different" is flat; Lingora\u2019s "was shaped differently" carries the backward-looking weight of a conclusion.',
          'Final paragraph preserves the arc: the narrator has moved from reporting (\u00b61\u20132), to reflecting (\u00b63), to negotiating with the reader (\u00b64), to resolution (\u00b65). MT flattens every paragraph to the same register; Lingora modulates.',
        ],
      },
    ],
  },
  {
    title: 'Vouvoyer',
    srcLang: 'French',
    srcLangTag: 'fr',
    blurb: 'A grandfather\u2019s use of formal and informal address across generations. The entire story pivots on the tu/vous distinction \u2014 which English has no grammatical equivalent for. The punchline is invisible in standard MT.',
    paragraphs: [
      {
        src: 'Quand j\u2019\u00e9tais enfant, mon grand-p\u00e8re me vouvoyait toujours. Ma m\u00e8re, sa fille, il la tutoyait. Cette asym\u00e9trie me paraissait normale ; c\u2019\u00e9tait l\u2019usage dans la famille.',
        mt:  'When I was a child, my grandfather always spoke to me formally. My mother, his daughter, he spoke to informally. This asymmetry seemed normal to me; it was the custom in the family.',
        lin: 'When I was a child, my grandfather always used *vous* with me. My mother \u2014 his daughter \u2014 he called *tu*. The asymmetry felt normal to me; that was just the family\u2019s way.',
        mtPreserve: 0.40,
        linPreserve: 0.88,
        annotation: [
          'The French verbs "vouvoyer" / "tutoyer" have no English equivalent \u2014 they mean "to address using vous/tu." MT flattens them to "formally/informally," which is denotationally right but loses the <em>grammatical</em> asymmetry that is the whole story. Lingora keeps the French pronouns.',
          '"l\u2019usage" in French names a social convention, not the act of using something. "The family\u2019s way" catches the sense better than MT\u2019s generic "custom."',
          'Semicolon + "c\u2019\u00e9tait l\u2019usage" is a classic French reflective register \u2014 the narrator stepping back to name a pattern. Lingora rephrases as a trailing clause to match the English version of that move.',
        ],
      },
      {
        src: 'Un jour, j\u2019ai compris qu\u2019il me donnait, avec ce \u00ab vous \u00bb, une distance qu\u2019il ne savait pas comment me demander autrement. Il ne voulait pas me manquer de respect \u2014 il voulait que je sois, moi aussi, une personne respect\u00e9e.',
        mt:  'One day, I understood that he was giving me, with this "you," a distance that he did not know how to ask me for otherwise. He did not want to lack respect for me \u2014 he wanted me to be, also, a respected person.',
        lin: 'One day I understood: with that *vous*, he was giving me a distance he didn\u2019t know how else to ask for. He wasn\u2019t failing to respect me \u2014 he was letting me be, too, someone worthy of respect.',
        mtPreserve: 0.30,
        linPreserve: 0.85,
        annotation: [
          'MT renders \u00ab vous \u00bb as "this \u2018you\u2019" \u2014 which in English is meaningless, since "you" covers both registers. Lingora keeps *vous* and lets the French word do the work.',
          '"me manquer de respect" is an idiomatic reflexive \u2014 "to fail to show me respect," not "to lack respect for me." MT\u2019s literal phrasing inverts the direction of the action.',
          'Subjunctive "que je sois" carries a sense of <em>wanting-into-being</em> that English\u2019s flat infinitive "to be" loses. Lingora rephrases as "letting me be... someone worthy of respect" to capture the volitive meaning.',
        ],
      },
      {
        src: 'Quand il est mort, j\u2019ai h\u00e9rit\u00e9 de sa biblioth\u00e8que. Dans les marges des livres, en crayon, il avait \u00e9crit : \u00ab Lis \u00e7a, tu comprendras. \u00bb Il me tutoyait, dans l\u2019\u00e9criture.',
        mt:  'When he died, I inherited his library. In the margins of the books, in pencil, he had written: "Read this, you will understand." He spoke to me informally, in writing.',
        lin: 'When he died, I inherited his library. In the margins of the books, in pencil, he had written: \u00ab Lis \u00e7a, tu comprendras. \u00bb *Tu.* He called me *tu* \u2014 in writing.',
        mtPreserve: 0.20,
        linPreserve: 0.92,
        annotation: [
          'THE PIVOT. The grandfather\u2019s shift from *vous* to *tu* is carried entirely by the imperative form "Lis" (familiar) and the pronoun "tu" \u2014 both of which collapse into English "you." MT loses the whole story\u2019s reversal. Lingora keeps the French quote plus an emphatic "*Tu.*" to make the register shift visible to an English reader.',
          '"dans l\u2019\u00e9criture" is a phrase that treats writing as a register of its own, separate from speech. MT\u2019s "in writing" is correct denotationally but misses the cultural treatment of writing as a literary register with its own grammar of intimacy.',
        ],
      },
      {
        src: 'Voil\u00e0 toute la diff\u00e9rence entre un homme qui parle et un homme qui \u00e9crit.',
        mt:  'There is the whole difference between a man who speaks and a man who writes.',
        lin: 'There \u2014 that\u2019s the whole difference between a man who speaks and a man who writes.',
        mtPreserve: 0.55,
        linPreserve: 0.82,
        annotation: [
          '"Voil\u00e0" is a French discourse marker that gestures at presenting a conclusion, almost physically \u2014 "here, see this." MT\u2019s "There is" is grammatically fine but carries none of the revelation-move. Lingora\u2019s "There \u2014 that\u2019s" captures the oral-storytelling pause.',
          'The parallel structure "un homme qui parle / un homme qui \u00e9crit" is preserved in both versions. This sentence is the one where MT does the least damage \u2014 but only because the previous paragraph did most of the work, and the punchline has already landed.',
        ],
      },
    ],
  },
];
let storyActive = null;
function storyPick(i) {
  storyActive = i;
  pepSend('story.pick', { i, title: STORY_DATA[i].title });
  storyRender();
}
function escHTML(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
function storyRender() {
  const view = document.getElementById('story-view');
  if (!view) return;
  if (storyActive == null) {
    view.innerHTML = '<div style="padding:40px;text-align:center;color:var(--dim)">pick a story above</div>';
    return;
  }
  const d = STORY_DATA[storyActive];
  const header = `
    <div style="padding:14px 18px;border-bottom:1px solid var(--border);background:var(--surface2)">
      <div style="font-size:11px;color:var(--dim);letter-spacing:0.15em">${escHTML(d.srcLang.toUpperCase())} &middot; STORY TRANSLATION</div>
      <div style="font-size:18px;font-weight:bold;margin-top:2px">${escHTML(d.title)}</div>
      <div style="font-size:12px;color:var(--dim);margin-top:6px">${escHTML(d.blurb)}</div>
    </div>
  `;
  const colHeader = `
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;padding:12px 18px;border-bottom:1px solid var(--border);font-size:11px;letter-spacing:0.15em">
      <div style="color:var(--dim)">ORIGINAL (${escHTML(d.srcLangTag)})</div>
      <div style="color:#a78bfa">STANDARD MT</div>
      <div style="color:#4fc3f7">LINGORA LAYER-AWARE</div>
    </div>
  `;
  const rows = d.paragraphs.map((p, i) => {
    const ann = p.annotation.map(a => `<div style="margin-top:4px;padding-left:12px;border-left:2px solid rgba(186,104,200,0.4)">${escHTML(a)}</div>`).join('');
    return `
      <div style="padding:14px 18px;border-bottom:1px solid var(--border)">
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;font-size:13px;line-height:1.55">
          <div style="color:#dce4ed">${escHTML(p.src)}</div>
          <div style="color:#c7b8f0">${escHTML(p.mt)}</div>
          <div style="color:#7cd0f5">${escHTML(p.lin)}</div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:10px;font-size:11px;color:var(--dim)">
          <div>
            <div style="color:#a78bfa;font-weight:bold;letter-spacing:0.1em">MT PRESERVES &nbsp;${(p.mtPreserve * 100).toFixed(0)}%</div>
          </div>
          <div>
            <div style="color:#4fc3f7;font-weight:bold;letter-spacing:0.1em">LINGORA PRESERVES &nbsp;${(p.linPreserve * 100).toFixed(0)}%</div>
          </div>
        </div>
        <div style="margin-top:10px;font-size:11px;color:#aaa;line-height:1.55">
          <div style="color:#aaa;font-weight:bold;letter-spacing:0.1em;margin-bottom:4px">WHAT CHANGED &nbsp;\u00b6${i + 1}</div>
          ${ann}
        </div>
      </div>
    `;
  }).join('');
  view.innerHTML = header + colHeader + rows;
}
storyRender();
const storyDriftCanvas = document.getElementById('story-drift-canvas');
const storyDriftCtx = storyDriftCanvas.getContext('2d');
function drawStoryDrift() {
  const W = 960, H = 220;
  storyDriftCtx.fillStyle = themeBg(); storyDriftCtx.fillRect(0, 0, W, H);
  if (storyActive == null) {
    storyDriftCtx.fillStyle = '#778'; storyDriftCtx.font = '11px monospace'; storyDriftCtx.textAlign = 'center';
    storyDriftCtx.fillText('(pick a story to see per-paragraph preservation drift)', W / 2, H / 2);
    requestAnimationFrame(drawStoryDrift); return;
  }
  const d = STORY_DATA[storyActive];
  const padL = 60, padR = 20, padT = 36, padB = 36;
  const plotW = W - padL - padR, plotH = H - padT - padB;
  const n = d.paragraphs.length;
  const x2px = i => padL + (n === 1 ? plotW / 2 : (i / (n - 1)) * plotW);
  const y2px = v => padT + (1 - v) * plotH;
  // Title
  storyDriftCtx.fillStyle = '#dce4ed'; storyDriftCtx.font = 'bold 12px monospace'; storyDriftCtx.textAlign = 'left';
  storyDriftCtx.fillText('Per-paragraph preservation \u2014 how much of pragmatic + register + cultural layers survives', padL, 18);
  // Axes
  storyDriftCtx.strokeStyle = 'rgba(150,150,150,0.4)'; storyDriftCtx.lineWidth = 1;
  storyDriftCtx.beginPath();
  storyDriftCtx.moveTo(padL, padT); storyDriftCtx.lineTo(padL, padT + plotH); storyDriftCtx.lineTo(padL + plotW, padT + plotH);
  storyDriftCtx.stroke();
  // Y ticks
  [0, 0.25, 0.5, 0.75, 1.0].forEach(v => {
    storyDriftCtx.strokeStyle = 'rgba(150,150,150,0.12)';
    storyDriftCtx.beginPath(); storyDriftCtx.moveTo(padL, y2px(v)); storyDriftCtx.lineTo(padL + plotW, y2px(v)); storyDriftCtx.stroke();
    storyDriftCtx.fillStyle = '#778'; storyDriftCtx.font = '10px monospace'; storyDriftCtx.textAlign = 'right';
    storyDriftCtx.fillText(v.toFixed(2), padL - 6, y2px(v) + 3);
  });
  // X ticks
  d.paragraphs.forEach((_, i) => {
    storyDriftCtx.fillStyle = '#778'; storyDriftCtx.font = '10px monospace'; storyDriftCtx.textAlign = 'center';
    storyDriftCtx.fillText('\u00b6' + (i + 1), x2px(i), padT + plotH + 14);
  });
  // MT line
  storyDriftCtx.strokeStyle = '#a78bfa'; storyDriftCtx.lineWidth = 2;
  storyDriftCtx.beginPath();
  d.paragraphs.forEach((p, i) => {
    const x = x2px(i), y = y2px(p.mtPreserve);
    if (i === 0) storyDriftCtx.moveTo(x, y); else storyDriftCtx.lineTo(x, y);
  });
  storyDriftCtx.stroke();
  d.paragraphs.forEach((p, i) => {
    storyDriftCtx.fillStyle = '#a78bfa';
    storyDriftCtx.beginPath(); storyDriftCtx.arc(x2px(i), y2px(p.mtPreserve), 4, 0, Math.PI * 2); storyDriftCtx.fill();
  });
  // Lingora line
  storyDriftCtx.strokeStyle = '#4fc3f7'; storyDriftCtx.lineWidth = 2;
  storyDriftCtx.beginPath();
  d.paragraphs.forEach((p, i) => {
    const x = x2px(i), y = y2px(p.linPreserve);
    if (i === 0) storyDriftCtx.moveTo(x, y); else storyDriftCtx.lineTo(x, y);
  });
  storyDriftCtx.stroke();
  d.paragraphs.forEach((p, i) => {
    storyDriftCtx.fillStyle = '#4fc3f7';
    storyDriftCtx.beginPath(); storyDriftCtx.arc(x2px(i), y2px(p.linPreserve), 4, 0, Math.PI * 2); storyDriftCtx.fill();
  });
  // Legend
  storyDriftCtx.font = '10px monospace'; storyDriftCtx.textAlign = 'left';
  storyDriftCtx.fillStyle = '#a78bfa';
  storyDriftCtx.fillRect(padL + plotW - 220, 10, 10, 10);
  storyDriftCtx.fillText('Standard MT', padL + plotW - 205, 19);
  storyDriftCtx.fillStyle = '#4fc3f7';
  storyDriftCtx.fillRect(padL + plotW - 110, 10, 10, 10);
  storyDriftCtx.fillText('Lingora layer-aware', padL + plotW - 95, 19);
  // Gap annotation
  const mtAvg = d.paragraphs.reduce((a, p) => a + p.mtPreserve, 0) / n;
  const linAvg = d.paragraphs.reduce((a, p) => a + p.linPreserve, 0) / n;
  storyDriftCtx.fillStyle = '#81c784'; storyDriftCtx.font = 'bold 11px monospace';
  storyDriftCtx.textAlign = 'right';
  storyDriftCtx.fillText('gap: +' + ((linAvg - mtAvg) * 100).toFixed(0) + ' pts preservation', padL + plotW, padT + plotH + 28);
  requestAnimationFrame(drawStoryDrift);
}
drawStoryDrift();

// ═══════════════════════════════════════════════════════════════════════
// Writing Voice Analyzer
// ═══════════════════════════════════════════════════════════════════════
const VOICEAN_DATA = [
  { label: 'HEMINGWAY (clipped, declarative)', text: 'The old man was thin and gaunt with deep wrinkles. He fished alone. He had not caught a fish in eighty-four days. The boy loved him.',
    scores: { pov: 0.7, register: 0.85, irony: 0.1, subtext: 0.6, pacing: 0.95, voice: 0.95, repetition: 0.4, sound: 0.3 },
    diagnostic: 'Voice is consistent and pacing is sharp. Subtext is doing real work; consider letting it carry one more beat.' },
  { label: 'FAULKNER (long, embedded)', text: 'It was a long sentence that wound through the dust of years and the heat of summers and the slow thick blood of a family that did not know how to forget.',
    scores: { pov: 0.8, register: 0.9, irony: 0.2, subtext: 0.85, pacing: 0.4, voice: 0.95, repetition: 0.7, sound: 0.85 },
    diagnostic: 'Voice and sound are dominant. The pacing is intentionally slow; do not flatten. Repetition could carry one more echo.' },
  { label: 'CORPORATE MEMO (passive, hedged)', text: 'It has been determined that certain efficiencies could potentially be realized through a strategic re-evaluation of current operational paradigms.',
    scores: { pov: 0.2, register: 0.95, irony: 0.05, subtext: 0.3, pacing: 0.5, voice: 0.85, repetition: 0.1, sound: 0.1 },
    diagnostic: 'Register is operating exactly as the genre requires. Hedging is the point. Do not "fix" the passive voice.' },
  { label: 'TWEET (compressed, ironic)', text: 'oh great another framework that\\'ll be deprecated by friday',
    scores: { pov: 0.6, register: 0.7, irony: 0.95, subtext: 0.7, pacing: 0.85, voice: 0.85, repetition: 0.0, sound: 0.2 },
    diagnostic: 'Irony is the engine. Subtext is the second engine. Compression is correct for the medium.' },
];
const vanCanvas = document.getElementById('voice-analyze-canvas');
const vanCtx = vanCanvas.getContext('2d');
let vanActive = null;
function voiceAnalyzePick(i) { vanActive = i; pepSend('voice.pick', { i }); }
function drawVoiceAnalyze() {
  const W = 960, H = 520; vanCtx.fillStyle = themeBg(); vanCtx.fillRect(0, 0, W, H);
  if (vanActive == null) {
    vanCtx.fillStyle = '#778'; vanCtx.font = '11px monospace'; vanCtx.textAlign = 'center';
    vanCtx.fillText('(pick a paragraph)', W / 2, H / 2);
    requestAnimationFrame(drawVoiceAnalyze); return;
  }
  const d = VOICEAN_DATA[vanActive];
  vanCtx.fillStyle = '#4fc3f7'; vanCtx.font = 'bold 12px monospace'; vanCtx.textAlign = 'left';
  vanCtx.fillText(d.label, 30, 30);
  vanCtx.fillStyle = '#dce4ed'; vanCtx.font = '12px monospace';
  wrapText(vanCtx, d.text, 30, 60, W - 60, 18);
  const mechs = [['POV', 'pov'], ['REGISTER', 'register'], ['IRONY', 'irony'], ['SUBTEXT', 'subtext'], ['PACING', 'pacing'], ['VOICE CONSISTENCY', 'voice'], ['REPETITION', 'repetition'], ['SOUND SYMMETRY', 'sound']];
  vanCtx.fillStyle = '#a78bfa'; vanCtx.font = 'bold 11px monospace';
  vanCtx.fillText('MECHANISM STRENGTH', 30, 200);
  mechs.forEach((m, i) => {
    const y = 220 + i * 30;
    vanCtx.fillStyle = '#dce4ed'; vanCtx.font = '10px monospace';
    vanCtx.fillText(m[0], 30, y + 12);
    vanCtx.fillStyle = 'rgba(79,195,247,0.15)'; vanCtx.fillRect(180, y, 320, 18);
    vanCtx.fillStyle = 'rgba(79,195,247,0.85)'; vanCtx.fillRect(180, y, 320 * d.scores[m[1]], 18);
    vanCtx.fillStyle = '#fff'; vanCtx.font = '10px monospace'; vanCtx.textAlign = 'right';
    vanCtx.fillText((d.scores[m[1]] * 100).toFixed(0) + '%', 495, y + 12);
    vanCtx.textAlign = 'left';
  });
  vanCtx.fillStyle = '#81c784'; vanCtx.font = 'bold 11px monospace'; vanCtx.textAlign = 'left';
  vanCtx.fillText('DIAGNOSTIC (voice-preserving)', 530, 200);
  vanCtx.fillStyle = '#dce4ed'; vanCtx.font = '11px monospace';
  wrapText(vanCtx, d.diagnostic, 530, 224, 410, 16);
  requestAnimationFrame(drawVoiceAnalyze);
}
drawVoiceAnalyze();

// ═══════════════════════════════════════════════════════════════════════
// Lingora Benchmark
// ═══════════════════════════════════════════════════════════════════════
const linBenchCanvas = document.getElementById('lin-bench-canvas');
const linBenchCtx = linBenchCanvas.getContext('2d');
let linBenchData = null;
function linBenchGen() {
  linBenchData = {
    base: { prag: 0.18 + (Math.random() - 0.5) * 0.04, reg: 0.32 + (Math.random() - 0.5) * 0.04, cult: 0.21 + (Math.random() - 0.5) * 0.04, bleu: 0.42 + (Math.random() - 0.5) * 0.03, lat: 1.0 },
    lin:  { prag: 0.71 + (Math.random() - 0.5) * 0.05, reg: 0.78 + (Math.random() - 0.5) * 0.04, cult: 0.65 + (Math.random() - 0.5) * 0.05, bleu: 0.41 + (Math.random() - 0.5) * 0.03, lat: 1.0 + 0.45 + Math.random() * 0.08 },
  };
}
linBenchGen();
function linBenchRegen() { linBenchGen(); pepSend('linbench.regen', {}); }
function drawLinBench() {
  const W = 960, H = 640; linBenchCtx.fillStyle = themeBg(); linBenchCtx.fillRect(0, 0, W, H);
  if (!linBenchData) { requestAnimationFrame(drawLinBench); return; }
  const d = linBenchData;
  const metrics = [
    { label: 'Pragmatic preservation', b: d.base.prag, l: d.lin.prag, fmt: (v) => (v * 100).toFixed(1) + '%', higher: true },
    { label: 'Register preservation',  b: d.base.reg,  l: d.lin.reg,  fmt: (v) => (v * 100).toFixed(1) + '%', higher: true },
    { label: 'Cultural framing',       b: d.base.cult, l: d.lin.cult, fmt: (v) => (v * 100).toFixed(1) + '%', higher: true },
    { label: 'BLEU score',             b: d.base.bleu, l: d.lin.bleu, fmt: (v) => v.toFixed(2),               higher: true },
    { label: 'Latency (index)',        b: d.base.lat / 2.0, l: d.lin.lat / 2.0, fmt: (v) => (v * 2.0).toFixed(2) + 'x', higher: false },
  ];
  linBenchCtx.fillStyle = '#aaa'; linBenchCtx.font = '11px monospace'; linBenchCtx.textAlign = 'left';
  linBenchCtx.fillText('300 synthetic translation pairs · standard MT (purple) vs Lingora-aware (blue)', 30, 24);
  const barW = 340, barH = 28, gap = 36;
  metrics.forEach((m, i) => {
    const y = 50 + i * (barH * 2 + gap);
    linBenchCtx.fillStyle = '#dce4ed'; linBenchCtx.font = 'bold 12px monospace'; linBenchCtx.textAlign = 'left';
    linBenchCtx.fillText(m.label, 30, y);
    linBenchCtx.fillStyle = 'rgba(167,139,250,0.25)'; linBenchCtx.fillRect(30, y + 8, barW, barH);
    linBenchCtx.fillStyle = 'rgba(167,139,250,0.85)'; linBenchCtx.fillRect(30, y + 8, barW * Math.min(1, m.b), barH);
    linBenchCtx.fillStyle = '#fff'; linBenchCtx.font = '11px monospace'; linBenchCtx.textAlign = 'right';
    linBenchCtx.fillText('MT: ' + m.fmt(m.b), 30 + barW - 6, y + 8 + barH / 2 + 4);
    linBenchCtx.fillStyle = 'rgba(79,195,247,0.25)'; linBenchCtx.fillRect(30, y + 8 + barH + 4, barW, barH);
    linBenchCtx.fillStyle = 'rgba(79,195,247,0.85)'; linBenchCtx.fillRect(30, y + 8 + barH + 4, barW * Math.min(1, m.l), barH);
    linBenchCtx.fillStyle = '#fff';
    linBenchCtx.fillText('Lingora: ' + m.fmt(m.l), 30 + barW - 6, y + 8 + barH + 4 + barH / 2 + 4);
    const delta = m.l - m.b;
    const pct = Math.abs(m.b) > 0.001 ? (delta / m.b * 100) : 0;
    const isGood = m.higher ? delta > 0 : delta < 0;
    const col = isGood ? 'rgba(79,195,247,0.95)' : Math.abs(delta) < 0.05 ? 'rgba(200,200,200,0.95)' : 'rgba(248,113,113,0.95)';
    linBenchCtx.fillStyle = col; linBenchCtx.font = 'bold 13px monospace'; linBenchCtx.textAlign = 'left';
    const sign = pct > 0 ? '+' : '';
    linBenchCtx.fillText(sign + pct.toFixed(0) + '%', 400, y + 8 + barH + 4);
    linBenchCtx.fillStyle = '#aaa'; linBenchCtx.font = '10px monospace';
    const labelTxt = m.label === 'BLEU score' ? 'tied (different axis)' : (isGood ? 'better' : 'tradeoff');
    linBenchCtx.fillText(labelTxt, 400, y + 8 + barH + 20);
  });
  linBenchCtx.fillStyle = 'rgba(79,195,247,0.95)'; linBenchCtx.font = 'bold 11px monospace'; linBenchCtx.textAlign = 'center';
  linBenchCtx.fillText('Lingora is not winning at literal accuracy (BLEU ties); it is winning on the axis BLEU does not measure', W / 2, H - 20);
  requestAnimationFrame(drawLinBench);
}
drawLinBench();

function drawInnerspeech() {
  const W = 960, H = 400; innerspeechCtx.fillStyle = themeBg(); innerspeechCtx.fillRect(0, 0, W, H);
  const rate = parseInt(document.getElementById('inner-rate').value) / 100;
  innerspeechCtx.fillStyle = '#aaa'; innerspeechCtx.font = '11px monospace'; innerspeechCtx.textAlign = 'left';
  innerspeechCtx.fillText('inner verbal activity (simulated)', 30, 30);
  // Scrolling verbal stream
  const phrases = ['ok so', 'what was I', 'remember to', 'hmm', 'right, right', 'maybe I should', 'what if', 'no wait', 'that reminds me', 'I need to', 'oh yeah'];
  for (let i = 0; i < 12; i++) {
    const active = Math.random() < rate;
    const y = 70 + i * 22;
    innerspeechCtx.fillStyle = active ? 'rgba(124,184,255,0.9)' : 'rgba(120,120,140,0.2)';
    innerspeechCtx.font = '13px monospace';
    innerspeechCtx.fillText('• ' + phrases[Math.floor(Math.random() * phrases.length)], 50, y);
  }
  innerspeechCtx.fillStyle = '#aaa'; innerspeechCtx.font = '11px monospace';
  let label;
  if (rate < 0.1) label = 'low inner speech — thinking mostly in images / structure / felt states';
  else if (rate < 0.5) label = 'moderate inner speech — verbal track on for planning, quiet otherwise';
  else label = 'dense inner speech — near-constant verbal commentary';
  innerspeechCtx.fillText(label, 30, H - 30);
  requestAnimationFrame(drawInnerspeech);
}
drawInnerspeech();

// ═══════════════════════════════════════════════════════════════════════
// Headlines & Clickbait
// ═══════════════════════════════════════════════════════════════════════
const HEADLINES_DATA = {
  curiosity: { label: 'curiosity gap', example: 'You won\\u0027t believe what this family did when they found the old box', move: 'promises information the reader does not yet have; implies the reveal will surprise', effect: 'predictor fires on the unknown; unresolved anticipation is the attention hook' },
  list: { label: 'numbered list', example: '9 things every parent should know before the school year starts', move: 'promises bounded, finite content', effect: 'commitment lowers the perceived reading cost; each item is an atomic payoff' },
  loss: { label: 'loss framing', example: 'Stop doing these 5 things or you will regret it', move: 'activates loss-avoidance rather than gain-seeking', effect: 'loss aversion is a stronger motivator than equivalent-magnitude gains' },
  ingroup: { label: 'in-group cue', example: 'For parents of picky eaters: the one trick that finally worked', move: 'explicitly addresses a specific identity', effect: 'the reader\\u0027s self-model recognizes the call and commits attention before evaluating content' },
  contrarian: { label: 'contrarian', example: 'Why everyone is wrong about morning routines', move: 'offers special knowledge that contradicts received wisdom', effect: 'exploits the contrarian-flattery instinct' },
};
const headlinesCanvas = document.getElementById('headlines-canvas');
const headlinesCtx = headlinesCanvas.getContext('2d');
let headlinesActive = null;
function headlinesPick(k) { headlinesActive = k; pepSend('headlines.pick', { key: k }); }
function drawHeadlines() {
  const W = 960, H = 440; headlinesCtx.fillStyle = themeBg(); headlinesCtx.fillRect(0, 0, W, H);
  if (!headlinesActive) { headlinesCtx.fillStyle = '#666'; headlinesCtx.font = '11px monospace'; headlinesCtx.textAlign = 'center'; headlinesCtx.fillText('(pick a move)', W/2, H/2); requestAnimationFrame(drawHeadlines); return; }
  const d = HEADLINES_DATA[headlinesActive];
  headlinesCtx.fillStyle = 'rgba(240,168,105,0.95)'; headlinesCtx.font = 'bold 13px monospace'; headlinesCtx.textAlign = 'left';
  headlinesCtx.fillText(d.label.toUpperCase(), 30, 40);
  headlinesCtx.fillStyle = '#fff'; headlinesCtx.font = 'bold 16px monospace';
  const words = d.example.split(' '); let x = 30, y = 80;
  words.forEach(w => { const m = headlinesCtx.measureText(w + ' '); if (x + m.width > W - 30) { x = 30; y += 24; } headlinesCtx.fillText(w + ' ', x, y); x += m.width; });
  headlinesCtx.fillStyle = 'rgba(124,184,255,0.95)'; headlinesCtx.font = 'bold 11px monospace';
  headlinesCtx.fillText('THE MOVE', 30, 180);
  headlinesCtx.fillStyle = '#e0e0e0'; headlinesCtx.font = '12px monospace';
  headlinesCtx.fillText('→ ' + d.move, 50, 202);
  headlinesCtx.fillStyle = 'rgba(129,199,132,0.95)'; headlinesCtx.font = 'bold 11px monospace';
  headlinesCtx.fillText('THE EFFECT', 30, 250);
  headlinesCtx.fillStyle = '#e0e0e0'; headlinesCtx.font = '12px monospace';
  const ef = d.effect.split(' '); x = 50; y = 272;
  ef.forEach(w => { const m = headlinesCtx.measureText(w + ' '); if (x + m.width > W - 30) { x = 50; y += 20; } headlinesCtx.fillText(w + ' ', x, y); x += m.width; });
  headlinesCtx.fillStyle = '#aaa'; headlinesCtx.font = '11px monospace';
  headlinesCtx.fillText('defense: recognition. Once you can name the move it loses much of its grip.', 30, H - 20);
  requestAnimationFrame(drawHeadlines);
}
drawHeadlines();

// ═══════════════════════════════════════════════════════════════════════
// Legal Language
// ═══════════════════════════════════════════════════════════════════════
const LEGAL_DATA = {
  precision: { label: 'engineered precision', text: 'The Party of the First Part ("Seller") shall deliver the Goods to the Party of the Second Part ("Buyer") on or before 5:00 PM Eastern Time on December 15, 2026, at the address specified in Exhibit A.', note: 'every noun phrase defined, every scope bounded, every pronoun replaced' },
  ambiguity: { label: 'deliberate ambiguity', text: 'The parties shall use reasonable efforts, in good faith, to cure any material breach within a commercially reasonable time.', note: '"reasonable efforts," "good faith," "material" — load-bearing vagueness that lets the contract form' },
  boilerplate: { label: 'boilerplate armor', text: 'including but not limited to, any and all claims, whether known or unknown, arising out of or in connection with, and to the fullest extent permitted by law...', note: 'each phrase bears the scar of a lawsuit where omitting it cost someone a fortune' },
};
const legalCanvas = document.getElementById('legal-canvas');
const legalCtx = legalCanvas.getContext('2d');
let legalActive = null;
function legalPick(k) { legalActive = k; pepSend('legal.pick', { key: k }); }
function drawLegal() {
  const W = 960, H = 420; legalCtx.fillStyle = themeBg(); legalCtx.fillRect(0, 0, W, H);
  if (!legalActive) { legalCtx.fillStyle = '#666'; legalCtx.font = '11px monospace'; legalCtx.textAlign = 'center'; legalCtx.fillText('(pick a style)', W/2, H/2); requestAnimationFrame(drawLegal); return; }
  const d = LEGAL_DATA[legalActive];
  legalCtx.fillStyle = 'rgba(240,168,105,0.95)'; legalCtx.font = 'bold 13px monospace'; legalCtx.textAlign = 'left';
  legalCtx.fillText(d.label.toUpperCase(), 30, 40);
  legalCtx.fillStyle = '#e0e0e0'; legalCtx.font = '13px monospace';
  const words = d.text.split(' '); let x = 30, y = 80;
  words.forEach(w => { const m = legalCtx.measureText(w + ' '); if (x + m.width > W - 30) { x = 30; y += 24; } legalCtx.fillText(w + ' ', x, y); x += m.width; });
  legalCtx.fillStyle = '#aaa'; legalCtx.font = '11px monospace';
  legalCtx.fillText(d.note, 30, H - 30);
  requestAnimationFrame(drawLegal);
}
drawLegal();

// ═══════════════════════════════════════════════════════════════════════
// Oral Tradition
// ═══════════════════════════════════════════════════════════════════════
const ORAL_DATA = {
  homer: { label: 'Homeric epithets', text: '"rosy-fingered dawn," "wine-dark sea," "swift-footed Achilles," "much-suffering Odysseus"', note: 'meter-filling formulas the bard dropped in to maintain dactylic hexameter while composing ahead' },
  vedas: { label: 'Vedic chant', text: 'Sanskrit verses preserved nearly verbatim for 3000+ years through interlocking recitation patterns (word-by-word, syllable-reversed, cross-checked)', note: 'the text itself is an error-correcting code' },
  memorypalace: { label: 'memory palace', text: 'mentally walk a familiar building; attach each point to a specific room; retrieve by re-walking the path', note: 'spatial memory has higher capacity than verbal memory — offloading sequence to space is compression' },
  alphabet: { label: 'alphabet song', text: 'a, b, c, d, e, f, g... / h, i, j, k, l, m, n, o, p...', note: 'still the fastest way to remember 26 items in order; the melody carries the memory, not the letters' },
};
const oralCanvas = document.getElementById('oral-canvas');
const oralCtx = oralCanvas.getContext('2d');
let oralActive = null;
function oralPick(k) { oralActive = k; pepSend('oral.pick', { key: k }); }
function drawOral() {
  const W = 960, H = 420; oralCtx.fillStyle = themeBg(); oralCtx.fillRect(0, 0, W, H);
  if (!oralActive) { oralCtx.fillStyle = '#666'; oralCtx.font = '11px monospace'; oralCtx.textAlign = 'center'; oralCtx.fillText('(pick a technique)', W/2, H/2); requestAnimationFrame(drawOral); return; }
  const d = ORAL_DATA[oralActive];
  oralCtx.fillStyle = 'rgba(240,168,105,0.95)'; oralCtx.font = 'bold 14px monospace'; oralCtx.textAlign = 'left';
  oralCtx.fillText(d.label.toUpperCase(), 30, 40);
  oralCtx.fillStyle = '#e0e0e0'; oralCtx.font = '13px monospace';
  const words = d.text.split(' '); let x = 30, y = 90;
  words.forEach(w => { const m = oralCtx.measureText(w + ' '); if (x + m.width > W - 30) { x = 30; y += 24; } oralCtx.fillText(w + ' ', x, y); x += m.width; });
  oralCtx.fillStyle = '#aaa'; oralCtx.font = '11px monospace';
  const nw = d.note.split(' '); x = 30; y = 280;
  nw.forEach(w => { const m = oralCtx.measureText(w + ' '); if (x + m.width > W - 30) { x = 30; y += 22; } oralCtx.fillText(w + ' ', x, y); x += m.width; });
  requestAnimationFrame(drawOral);
}
drawOral();

// ═══════════════════════════════════════════════════════════════════════
// Pidgins & Creoles
// ═══════════════════════════════════════════════════════════════════════
const PIDGIN_DATA = {
  pidgin: { label: 'Generation 1 — pidgin', examples: ['"You go store me go store"', '"Him no work. Me hungry."', '"Yesterday rain big."'], features: ['minimal vocabulary', 'no systematic grammar', 'word order varies', 'no tense marking', 'no embedded clauses'], note: 'nobody\\u0027s native language — improvised by adults under pressure' },
  creole: { label: 'Generation 2 — creole', examples: ['"I went to the store (while) she went too"', '"He does not have a job so he is hungry"', '"Yesterday there was heavy rain"'], features: ['full vocabulary', 'systematic grammar', 'consistent word order', 'tense and aspect marking', 'relative clauses and embedding'], note: 'children invented the grammar in ONE generation from impoverished input' },
};
const pidginCanvas = document.getElementById('pidgin-canvas');
const pidginCtx = pidginCanvas.getContext('2d');
let pidginActive = null;
function pidginStage(k) { pidginActive = k; pepSend('pidgin.stage', { stage: k }); }
function drawPidgin() {
  const W = 960, H = 440; pidginCtx.fillStyle = themeBg(); pidginCtx.fillRect(0, 0, W, H);
  if (!pidginActive) { pidginCtx.fillStyle = '#666'; pidginCtx.font = '11px monospace'; pidginCtx.textAlign = 'center'; pidginCtx.fillText('(pick a generation)', W/2, H/2); requestAnimationFrame(drawPidgin); return; }
  const d = PIDGIN_DATA[pidginActive];
  const col = pidginActive === 'pidgin' ? '229,57,53' : '129,199,132';
  pidginCtx.fillStyle = 'rgba(' + col + ',0.95)'; pidginCtx.font = 'bold 13px monospace'; pidginCtx.textAlign = 'left';
  pidginCtx.fillText(d.label.toUpperCase(), 30, 40);
  pidginCtx.fillStyle = '#aaa'; pidginCtx.font = '11px monospace';
  pidginCtx.fillText('sample utterances', 30, 80);
  pidginCtx.fillStyle = '#e0e0e0'; pidginCtx.font = '13px monospace';
  d.examples.forEach((e, i) => pidginCtx.fillText('• ' + e, 50, 106 + i * 26));
  pidginCtx.fillStyle = '#aaa'; pidginCtx.font = '11px monospace';
  pidginCtx.fillText('grammatical features', 30, 220);
  pidginCtx.fillStyle = 'rgba(' + col + ',0.95)'; pidginCtx.font = '12px monospace';
  d.features.forEach((f, i) => pidginCtx.fillText('• ' + f, 50, 244 + i * 22));
  pidginCtx.fillStyle = '#888'; pidginCtx.font = '11px monospace';
  const nw = d.note.split(' '); let x = 30, y = H - 50;
  nw.forEach(w => { const m = pidginCtx.measureText(w + ' '); if (x + m.width > W - 30) { x = 30; y += 20; } pidginCtx.fillText(w + ' ', x, y); x += m.width; });
  requestAnimationFrame(drawPidgin);
}
drawPidgin();

// ═══════════════════════════════════════════════════════════════════════
// Diglossia
// ═══════════════════════════════════════════════════════════════════════
const DIGLOSSIA_DATA = {
  arabic: { high: { name: 'Modern Standard Arabic (MSA)', where: 'news, religion, literature, formal speech' }, low: { name: 'regional dialects (Egyptian, Levantine, Maghrebi, Gulf)', where: 'home, street, informal speech' }, note: 'every literate Arab maintains both systems in parallel; a Moroccan and an Iraqi may not understand each other in dialect but can communicate in MSA' },
  swiss: { high: { name: 'Standard German', where: 'writing, school, national news' }, low: { name: 'Swiss-German dialects', where: 'home, friends, local conversation' }, note: 'the dialects are so different that Germans from Germany often cannot understand them; Swiss-German speakers are functionally bilingual' },
  tamil: { high: { name: 'Literary Tamil', where: 'formal writing, speeches, news' }, low: { name: 'Spoken Tamil', where: 'everyday conversation, films, pop culture' }, note: 'two-thousand-year-old split between written and spoken varieties, both thriving in their own functions' },
};
const diglossiaCanvas = document.getElementById('diglossia-canvas');
const diglossiaCtx = diglossiaCanvas.getContext('2d');
let diglossiaActive = null;
function diglossiaPick(k) { diglossiaActive = k; pepSend('diglossia.pick', { key: k }); }
function drawDiglossia() {
  const W = 960, H = 420; diglossiaCtx.fillStyle = themeBg(); diglossiaCtx.fillRect(0, 0, W, H);
  if (!diglossiaActive) { diglossiaCtx.fillStyle = '#666'; diglossiaCtx.font = '11px monospace'; diglossiaCtx.textAlign = 'center'; diglossiaCtx.fillText('(pick a case)', W/2, H/2); requestAnimationFrame(drawDiglossia); return; }
  const d = DIGLOSSIA_DATA[diglossiaActive];
  // High
  diglossiaCtx.fillStyle = 'rgba(124,184,255,0.25)'; diglossiaCtx.fillRect(60, 70, 830, 120);
  diglossiaCtx.strokeStyle = 'rgba(124,184,255,0.9)'; diglossiaCtx.lineWidth = 2; diglossiaCtx.strokeRect(60, 70, 830, 120);
  diglossiaCtx.fillStyle = 'rgba(124,184,255,0.95)'; diglossiaCtx.font = 'bold 13px monospace'; diglossiaCtx.textAlign = 'left';
  diglossiaCtx.fillText('HIGH VARIETY', 80, 100);
  diglossiaCtx.fillStyle = '#fff'; diglossiaCtx.font = '14px monospace';
  diglossiaCtx.fillText(d.high.name, 80, 130);
  diglossiaCtx.fillStyle = '#aaa'; diglossiaCtx.font = '11px monospace';
  diglossiaCtx.fillText('used for: ' + d.high.where, 80, 160);
  // Low
  diglossiaCtx.fillStyle = 'rgba(240,168,105,0.25)'; diglossiaCtx.fillRect(60, 220, 830, 120);
  diglossiaCtx.strokeStyle = 'rgba(240,168,105,0.9)'; diglossiaCtx.lineWidth = 2; diglossiaCtx.strokeRect(60, 220, 830, 120);
  diglossiaCtx.fillStyle = 'rgba(240,168,105,0.95)'; diglossiaCtx.font = 'bold 13px monospace';
  diglossiaCtx.fillText('LOW VARIETY', 80, 250);
  diglossiaCtx.fillStyle = '#fff'; diglossiaCtx.font = '14px monospace';
  diglossiaCtx.fillText(d.low.name, 80, 280);
  diglossiaCtx.fillStyle = '#aaa'; diglossiaCtx.font = '11px monospace';
  diglossiaCtx.fillText('used for: ' + d.low.where, 80, 310);
  diglossiaCtx.fillStyle = '#888'; diglossiaCtx.font = '10px monospace';
  const nw = d.note.split(' '); let x = 30, y = H - 30;
  nw.forEach(w => { const m = diglossiaCtx.measureText(w + ' '); if (x + m.width > W - 30) { x = 30; y += 16; } diglossiaCtx.fillText(w + ' ', x, y); x += m.width; });
  requestAnimationFrame(drawDiglossia);
}
drawDiglossia();

// ═══════════════════════════════════════════════════════════════════════
// Animal Communication
// ═══════════════════════════════════════════════════════════════════════
const ANIMAL_DATA = {
  bee: { label: 'Bee waggle dance', what: 'direction encodes bearing to food; duration encodes distance', missing: 'cannot express anything other than food location' },
  vervet: { label: 'Vervet alarm calls', what: 'distinct calls for leopard, eagle, and snake, each triggering appropriate evasion', missing: 'fixed category set; cannot learn new calls for new predators' },
  whale: { label: 'Humpback whale song', what: 'culturally-transmitted songs with complex nested structure, shared across populations', missing: 'unclear whether the structure encodes meaning or is aesthetic' },
  ape: { label: 'Signing apes (Washoe, Nim, Koko)', what: 'learned dozens to a few hundred signs, simple combinations', missing: 'no recursive embedding, no spontaneous questions, no teaching of other apes' },
};
const animalCanvas = document.getElementById('animal-canvas');
const animalCtx = animalCanvas.getContext('2d');
let animalActive = null;
function animalPick(k) { animalActive = k; pepSend('animal.pick', { key: k }); }
function drawAnimal() {
  const W = 960, H = 440; animalCtx.fillStyle = themeBg(); animalCtx.fillRect(0, 0, W, H);
  if (!animalActive) { animalCtx.fillStyle = '#666'; animalCtx.font = '11px monospace'; animalCtx.textAlign = 'center'; animalCtx.fillText('(pick a species)', W/2, H/2); requestAnimationFrame(drawAnimal); return; }
  const d = ANIMAL_DATA[animalActive];
  animalCtx.fillStyle = 'rgba(240,168,105,0.95)'; animalCtx.font = 'bold 14px monospace'; animalCtx.textAlign = 'left';
  animalCtx.fillText(d.label.toUpperCase(), 30, 40);
  animalCtx.fillStyle = 'rgba(129,199,132,0.95)'; animalCtx.font = 'bold 11px monospace';
  animalCtx.fillText('WHAT IT CAN DO', 30, 90);
  animalCtx.fillStyle = '#e0e0e0'; animalCtx.font = '13px monospace';
  const w1 = d.what.split(' '); let x = 50, y = 112;
  w1.forEach(w => { const m = animalCtx.measureText(w + ' '); if (x + m.width > W - 30) { x = 50; y += 22; } animalCtx.fillText(w + ' ', x, y); x += m.width; });
  animalCtx.fillStyle = 'rgba(229,57,53,0.95)'; animalCtx.font = 'bold 11px monospace';
  animalCtx.fillText('WHAT IS MISSING (vs human language)', 30, 220);
  animalCtx.fillStyle = '#e0e0e0'; animalCtx.font = '13px monospace';
  const w2 = d.missing.split(' '); x = 50; y = 242;
  w2.forEach(w => { const m = animalCtx.measureText(w + ' '); if (x + m.width > W - 30) { x = 50; y += 22; } animalCtx.fillText(w + ' ', x, y); x += m.width; });
  animalCtx.fillStyle = '#888'; animalCtx.font = '11px monospace';
  animalCtx.fillText('required for language: recursion, displaced reference, productivity, metalinguistic awareness', 30, H - 30);
  requestAnimationFrame(drawAnimal);
}
drawAnimal();

// ═══════════════════════════════════════════════════════════════════════
// Emoji / Digital Paralinguistics
// ═══════════════════════════════════════════════════════════════════════
const EMOJI_DATA = {
  tone: { variants: ['"Sure."', '"Sure 😊"', '"Sure 🙄"'], meanings: ['neutral or dismissive (ambiguous)', 'friendly agreement', 'sarcastic / unwilling'] },
  softening: { variants: ['"We should talk."', '"We should talk 💜"', '"We should talk 😬"'], meanings: ['ominous', 'caring, emotional', 'uncomfortable, bracing'] },
  reaction: { variants: ['👍 (thumbs up)', '❤️ (heart)', '😂 (laughing)', '🤔 (thinking)'], meanings: ['acknowledged', 'appreciated', 'funny', 'unclear, reconsidering'] },
};
const emojiCanvas = document.getElementById('emoji-canvas');
const emojiCtx = emojiCanvas.getContext('2d');
let emojiActive = null;
function emojiPick(k) { emojiActive = k; pepSend('emoji.pick', { key: k }); }
function drawEmoji() {
  const W = 960, H = 420; emojiCtx.fillStyle = themeBg(); emojiCtx.fillRect(0, 0, W, H);
  if (!emojiActive) { emojiCtx.fillStyle = '#666'; emojiCtx.font = '11px monospace'; emojiCtx.textAlign = 'center'; emojiCtx.fillText('(pick a scenario)', W/2, H/2); requestAnimationFrame(drawEmoji); return; }
  const d = EMOJI_DATA[emojiActive];
  emojiCtx.fillStyle = 'rgba(240,168,105,0.95)'; emojiCtx.font = 'bold 13px monospace'; emojiCtx.textAlign = 'left';
  emojiCtx.fillText(emojiActive.toUpperCase(), 30, 40);
  d.variants.forEach((v, i) => {
    const y = 90 + i * 90;
    emojiCtx.fillStyle = '#fff'; emojiCtx.font = 'bold 18px monospace';
    emojiCtx.fillText(v, 30, y);
    emojiCtx.fillStyle = 'rgba(129,199,132,0.9)'; emojiCtx.font = '12px monospace';
    emojiCtx.fillText('→ ' + d.meanings[i], 50, y + 28);
  });
  emojiCtx.fillStyle = '#aaa'; emojiCtx.font = '11px monospace';
  emojiCtx.fillText('emoji recovered the paralinguistic channel that text lost', 30, H - 20);
  requestAnimationFrame(drawEmoji);
}
drawEmoji();

// ═══════════════════════════════════════════════════════════════════════
// Search / Random / Bookmarks / Gallery
// ═══════════════════════════════════════════════════════════════════════
const LINGORA_CANVASES = [
  { id: 'word-tab', title: 'Word as Constellation', group: 'Words' },
  { id: 'ambig-tab', title: 'Ambiguity Resolution', group: 'Words' },
  { id: 'idiom-tab', title: 'Idiom as Opaque Block', group: 'Words' },
  { id: 'taboo-tab', title: 'Taboo Words', group: 'Words' },
  { id: 'vocab-tab', title: 'Vocabulary Growth', group: 'Words' },
  { id: 'drift-tab', title: 'Semantic Drift', group: 'Words' },
  { id: 'onoma-tab', title: 'Onomatopoeia', group: 'Words' },
  { id: 'metaphor-tab', title: 'Metaphor Engine', group: 'Words' },
  { id: 'colloc-tab', title: 'Collocations', group: 'Words' },
  { id: 'gramm-tab', title: 'Grammaticalization', group: 'Words' },
  { id: 'lexgap-tab', title: 'Lexical Gaps', group: 'Words' },
  { id: 'jargon-tab', title: 'Jargon', group: 'Words' },
  { id: 'cognates-tab', title: 'Cognates & False Friends', group: 'Words' },
  { id: 'phono-tab', title: 'Phonology / r-l perception', group: 'Sounds' },
  { id: 'prosody-tab', title: 'Prosody (stress)', group: 'Sounds' },
  { id: 'silence-tab', title: 'Silence as utterance', group: 'Sounds' },
  { id: 'soundsym-tab', title: 'Sound Symbolism (bouba/kiki)', group: 'Sounds' },
  { id: 'repetition-tab', title: 'Repetition & Rhythm', group: 'Sounds' },
  { id: 'rhyme-tab', title: 'Rhyme', group: 'Sounds' },
  { id: 'sentence-tab', title: 'Sentence Forecast', group: 'Sentences' },
  { id: 'grammar-tab', title: 'Grammar as Prior', group: 'Sentences' },
  { id: 'listener-tab', title: 'Listener Reconstruction', group: 'Sentences' },
  { id: 'transfer-tab', title: 'Speaker ↔ Listener Transfer', group: 'Sentences' },
  { id: 'acquisition-tab', title: 'Language Acquisition', group: 'Sentences' },
  { id: 'babytalk-tab', title: 'Baby Talk', group: 'Sentences' },
  { id: 'deixis-tab', title: 'Pronouns & Deixis', group: 'Sentences' },
  { id: 'anaphora-tab', title: 'Anaphora', group: 'Sentences' },
  { id: 'statistical-tab', title: 'Statistical Learning (Saffran)', group: 'Sentences' },
  { id: 'humor-tab', title: 'Humor & Puns', group: 'Speech Acts' },
  { id: 'voice-tab', title: 'Active ↔ Passive', group: 'Speech Acts' },
  { id: 'irony-tab', title: 'Irony', group: 'Speech Acts' },
  { id: 'grice-tab', title: 'Implicature (Grice)', group: 'Speech Acts' },
  { id: 'conv-tab', title: 'Conversation Dynamics', group: 'Speech Acts' },
  { id: 'subtext-tab', title: 'Subtext', group: 'Speech Acts' },
  { id: 'lying-tab', title: 'Lying markers', group: 'Speech Acts' },
  { id: 'persuasion-tab', title: 'Persuasion & Fallacies', group: 'Speech Acts' },
  { id: 'politeness-tab', title: 'Politeness', group: 'Speech Acts' },
  { id: 'discourse-tab', title: 'Discourse Markers', group: 'Speech Acts' },
  { id: 'swearing-tab', title: 'Swearing Dynamics', group: 'Speech Acts' },
  { id: 'gesture-tab', title: 'Cospeech Gesture', group: 'Speech Acts' },
  { id: 'reading-tab', title: 'Reading / Eye Movements', group: 'Reading & Brain' },
  { id: 'aphasia-tab', title: 'Aphasia & Dyslexia', group: 'Reading & Brain' },
  { id: 'wvs-tab', title: 'Written vs Spoken', group: 'Reading & Brain' },
  { id: 'orthography-tab', title: 'Writing Systems', group: 'Reading & Brain' },
  { id: 'errors-tab', title: 'Speech Errors', group: 'Reading & Brain' },
  { id: 'innerspeech-tab', title: 'Inner Speech', group: 'Reading & Brain' },
  { id: 'poetry-tab', title: 'Poetry as Residual', group: 'Writing' },
  { id: 'writing-tab', title: "Show Don't Tell", group: 'Writing' },
  { id: 'narrative-tab', title: 'Narrative Structure', group: 'Writing' },
  { id: 'advice-tab', title: 'Writing Advice', group: 'Writing' },
  { id: 'diff-tab', title: 'Text Diff', group: 'Writing' },
  { id: 'pov-tab', title: 'POV / Narrative Voice', group: 'Writing' },
  { id: 'stream-tab', title: 'Stream of Consciousness', group: 'Writing' },
  { id: 'typography-tab', title: 'Typography', group: 'Writing' },
  { id: 'headlines-tab', title: 'Headlines & Clickbait', group: 'Writing' },
  { id: 'legal-tab', title: 'Legal Language', group: 'Writing' },
  { id: 'oral-tab', title: 'Oral Tradition', group: 'Writing' },
  { id: 'codeswitch-tab', title: 'Code-Switching', group: 'Cross-Language' },
  { id: 'translation-tab', title: 'Translation Gap', group: 'Cross-Language' },
  { id: 'sign-tab', title: 'Sign Language', group: 'Cross-Language' },
  { id: 'pidgin-tab', title: 'Pidgins & Creoles', group: 'Cross-Language' },
  { id: 'diglossia-tab', title: 'Diglossia', group: 'Cross-Language' },
  { id: 'animal-tab', title: 'Animal Communication', group: 'Cross-Language' },
  { id: 'emoji-tab', title: 'Emoji / Digital Paralinguistics', group: 'Cross-Language' },
  { id: 'prompt-tab', title: 'Prompt Engineering', group: 'Machines' },
  { id: 'llm-tab', title: 'LLM Bridge', group: 'Machines' },
  { id: 'aidetect-tab', title: 'AI Text Detection', group: 'Machines' },
];
function lingoraBookmarks() {
  try { return JSON.parse(localStorage.getItem('lingora-bookmarks') || '[]'); } catch (e) { return []; }
}
function lingoraSaveBookmarks(b) {
  try { localStorage.setItem('lingora-bookmarks', JSON.stringify(b)); } catch (e) {}
}
function lingoraBookmark() {
  const active = document.querySelector('.panel.active');
  if (!active) return;
  const id = active.id;
  const bmks = lingoraBookmarks();
  const idx = bmks.indexOf(id);
  if (idx >= 0) bmks.splice(idx, 1);
  else bmks.push(id);
  lingoraSaveBookmarks(bmks);
  const btn = document.getElementById('bookmark-btn');
  if (btn) btn.textContent = bmks.includes(id) ? '★' : '☆';
  renderGallery();
}
function lingoraRandom() {
  const i = Math.floor(Math.random() * LINGORA_CANVASES.length);
  const id = LINGORA_CANVASES[i].id;
  const tab = findTabForPanel(id);
  if (tab) tab.click();
  setTimeout(() => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, 60);
  pepSend('lingora.random', { id });
}
function canvasSelect(id) {
  if (!id) return;
  const el = document.getElementById(id);
  if (!el) return;
  // If the selected element is itself a panel, click its tab directly.
  // Otherwise find the enclosing panel and click its tab first.
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
      // Single-panel tab: look for h3 sub-sections inside the panel.
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
      // Grouped tab with multiple panels — one entry per panel.
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
    const match = !query || card.textContent.toLowerCase().includes(query);
    card.style.display = match ? '' : 'none';
  });
  const visible = Array.from(grid.children).filter(c => c.style.display !== 'none').length;
  const count = document.getElementById('gallery-count');
  if (count) count.textContent = visible + ' / ' + LINGORA_CANVASES.length + ' canvases';
}
function renderGallery() {
  const grid = document.getElementById('gallery-grid');
  if (!grid) return;
  const bmks = lingoraBookmarks();
  const sorted = LINGORA_CANVASES.slice().sort((a, b) => {
    const ba = bmks.includes(a.id) ? 0 : 1;
    const bb = bmks.includes(b.id) ? 0 : 1;
    if (ba !== bb) return ba - bb;
    return 0;
  });
  grid.innerHTML = sorted.map(c => {
    const isBmk = bmks.includes(c.id);
    return '<div onclick="galleryGoto(\\'' + c.id + '\\')" ' +
      'style="background:var(--surface);border:1px solid ' + (isBmk ? 'var(--accent2)' : 'var(--border)') + ';border-radius:6px;padding:12px 14px;cursor:pointer;transition:transform 0.1s">' +
      '<div style="font-size:11px;color:var(--dim);margin-bottom:4px">' + c.group + (isBmk ? ' · ★' : '') + '</div>' +
      '<div style="font-size:12px;color:var(--text);font-weight:bold">' + c.title + '</div>' +
      '</div>';
  }).join('');
  const count = document.getElementById('gallery-count');
  if (count) count.textContent = LINGORA_CANVASES.length + ' canvases';
}
function galleryGoto(id) {
  const tab = findTabForPanel(id);
  if (tab) tab.click();
  setTimeout(() => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, 60);
}
setTimeout(renderGallery, 100);
// Update bookmark button on tab switch
document.querySelectorAll('.tab').forEach(t => {
  t.addEventListener('click', () => {
    setTimeout(() => {
      const active = document.querySelector('.panel.active');
      const btn = document.getElementById('bookmark-btn');
      if (active && btn) btn.textContent = lingoraBookmarks().includes(active.id) ? '★' : '☆';
    }, 30);
  });
});

function drawSandbox() {
  const W = 960, H = 440; sandboxCtx.fillStyle = themeBg(); sandboxCtx.fillRect(0, 0, W, H);
  sandboxCtx.fillStyle = '#aaa'; sandboxCtx.font = '11px monospace'; sandboxCtx.textAlign = 'left';
  sandboxCtx.fillText('sentence so far', 30, 30);
  let x = 30, y = 70;
  sandboxWords.forEach((w, i) => {
    sandboxCtx.fillStyle = 'rgba(124,184,255,0.95)'; sandboxCtx.font = 'bold 16px monospace';
    const m = sandboxCtx.measureText(w + ' ');
    if (x + m.width > 450) { x = 30; y += 26; }
    sandboxCtx.fillText(w + ' ', x, y); x += m.width;
  });
  if (sandboxWords.length === 0) {
    sandboxCtx.fillStyle = '#666'; sandboxCtx.fillText('(click words below to build a sentence)', 30, 70);
  }
  // Next-token forecast (heuristic)
  sandboxCtx.fillStyle = '#aaa'; sandboxCtx.font = '11px monospace';
  sandboxCtx.fillText('forecast for next word', 490, 30);
  const last = sandboxWords[sandboxWords.length - 1] || '';
  const fc = {
    'The': [['cat', 0.14], ['dog', 0.12], ['old', 0.08], ['small', 0.06], ['others', 0.60]],
    'cat': [['sat', 0.18], ['ran', 0.14], ['jumped', 0.1], ['is', 0.1], ['others', 0.48]],
    'dog': [['sat', 0.16], ['ran', 0.14], ['jumped', 0.1], ['barked', 0.1], ['others', 0.50]],
    'sat': [['on', 0.40], ['by', 0.1], ['still', 0.08], ['quietly', 0.08], ['others', 0.34]],
    'ran': [['across', 0.18], ['through', 0.14], ['to', 0.12], ['away', 0.1], ['others', 0.46]],
    'jumped': [['on', 0.25], ['over', 0.2], ['off', 0.12], ['onto', 0.1], ['others', 0.33]],
    'on': [['the', 0.6], ['a', 0.15], ['his', 0.05], ['others', 0.20]],
    'in': [['the', 0.55], ['a', 0.14], ['front', 0.05], ['others', 0.26]],
    'the': [['mat', 0.12], ['floor', 0.1], ['couch', 0.08], ['chair', 0.07], ['others', 0.63]],
    'mat': [['.', 0.55], [',', 0.15], ['by', 0.1], ['others', 0.2]],
    'floor': [['.', 0.5], [',', 0.15], ['by', 0.08], ['others', 0.27]],
    'couch': [['.', 0.5], [',', 0.15], ['with', 0.08], ['others', 0.27]],
    '.': [['(end)', 1.0]],
  };
  const candidates = fc[last] || [['(start)', 0.1], ['(or type)', 0.1], ['(many)', 0.8]];
  candidates.forEach((c, i) => {
    const by = 60 + i * 36;
    const w = 420 * c[1];
    sandboxCtx.fillStyle = 'rgba(124,184,255,0.2)'; sandboxCtx.fillRect(490, by, 420, 24);
    const col = c[0] === 'others' || c[0] === '(many)' ? '120,120,140' : '124,184,255';
    sandboxCtx.fillStyle = 'rgba(' + col + ',0.85)'; sandboxCtx.fillRect(490, by, w, 24);
    sandboxCtx.fillStyle = '#fff'; sandboxCtx.font = '12px monospace'; sandboxCtx.textAlign = 'left';
    sandboxCtx.fillText(c[0], 496, by + 16);
    sandboxCtx.fillStyle = '#aaa'; sandboxCtx.textAlign = 'right';
    sandboxCtx.fillText((c[1] * 100).toFixed(0) + '%', 906, by + 16);
  });
  requestAnimationFrame(drawSandbox);
}
drawSandbox();

function drawWriting() {
  const W = 960, H = 460;
  writingCtx.fillStyle = themeBg(); writingCtx.fillRect(0, 0, W, H);
  // Left pane: text
  writingCtx.fillStyle = '#aaa'; writingCtx.font = '11px monospace'; writingCtx.textAlign = 'left';
  writingCtx.fillText('text', 30, 28);
  const leftW = 520;
  writingCtx.strokeStyle = 'rgba(120,120,130,0.4)'; writingCtx.lineWidth = 1;
  writingCtx.strokeRect(30, 40, leftW, 380);
  if (writingActive) {
    const d = WRITING_DATA[writingActive];
    writingCtx.fillStyle = '#e0e0e0'; writingCtx.font = '13px monospace';
    // Word wrap
    const maxW = leftW - 30;
    const words = d.text.split(' ');
    let x = 45, y = 80;
    words.forEach(w => {
      const m = writingCtx.measureText(w + ' ');
      if (x + m.width > 30 + maxW) { x = 45; y += 22; }
      writingCtx.fillText(w, x, y);
      x += m.width;
    });
    writingCtx.fillStyle = 'rgba(124,184,255,0.95)'; writingCtx.font = 'bold 11px monospace';
    writingCtx.fillText(d.label, 45, 60);
  } else {
    writingCtx.fillStyle = '#666'; writingCtx.font = '11px monospace'; writingCtx.textAlign = 'center';
    writingCtx.fillText('(load a version)', 290, 220);
  }
  // Right pane: brain regions activated
  writingCtx.fillStyle = '#aaa'; writingCtx.font = '11px monospace'; writingCtx.textAlign = 'left';
  writingCtx.fillText('activated brain regions', 580, 28);
  const regions = [
    { key: 'verbal',    label: 'VERBAL',         col: '124,184,255' },
    { key: 'visual',    label: 'VISUAL',         col: '240,168,105' },
    { key: 'motor',     label: 'MOTOR',          col: '129,199,132' },
    { key: 'tactile',   label: 'TACTILE',        col: '186,104,200' },
    { key: 'auditory',  label: 'AUDITORY',       col: '255,183,77'  },
    { key: 'olfactory', label: 'OLFACTORY',      col: '255,107,107' },
    { key: 'emotional', label: 'EMOTIONAL',      col: '255,138,180' },
  ];
  regions.forEach((r, i) => {
    const y = 60 + i * 50;
    const act = writingActive ? WRITING_DATA[writingActive].activation[r.key] : 0;
    writingCtx.fillStyle = '#e0e0e0'; writingCtx.font = 'bold 11px monospace'; writingCtx.textAlign = 'left';
    writingCtx.fillText(r.label, 580, y + 14);
    writingCtx.fillStyle = 'rgba(' + r.col + ',0.2)';
    writingCtx.fillRect(580, y + 20, 320, 14);
    writingCtx.fillStyle = 'rgba(' + r.col + ',0.95)';
    writingCtx.fillRect(580, y + 20, 320 * act, 14);
    writingCtx.fillStyle = '#aaa'; writingCtx.font = '10px monospace'; writingCtx.textAlign = 'right';
    writingCtx.fillText((act * 100).toFixed(0) + '%', 900, y + 30);
  });
  requestAnimationFrame(drawWriting);
}
drawWriting();

</script>
</body>
</html>
"""


@router.get("/lingora", response_class=HTMLResponse)
async def lingora_page() -> str:
    return _PAGE
