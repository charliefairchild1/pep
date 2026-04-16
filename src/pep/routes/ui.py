"""HTML chat + dashboard UI served directly by FastAPI. No extra dependencies."""

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
<title>PEP</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
  :root {
    --bg: #0e0e10; --surface: #1a1a2e; --surface2: #16213e;
    --text: #e0e0e0; --dim: #888; --accent: #4fc3f7; --accent2: #81c784;
    --warn: #ffb74d; --border: #333;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
         background: var(--bg); color: var(--text); height: 100vh;
         display: flex; flex-direction: column; }
  header { padding: 12px 20px; border-bottom: 1px solid var(--border);
           display: flex; align-items: center; gap: 16px; }
  header h1 { font-size: 16px; color: var(--accent); }
  header span { font-size: 12px; color: var(--dim); }
  .tabs { display: flex; border-bottom: 1px solid var(--border); }
  .tab { padding: 8px 20px; font-size: 13px; color: var(--dim);
         cursor: pointer; border-bottom: 2px solid transparent; }
  .tab.active { color: var(--accent); border-bottom-color: var(--accent); }
  .panels { flex: 1; overflow: hidden; display: flex; flex-direction: column; }
  .panel { display: none; flex: 1; overflow: auto; flex-direction: column; }
  .panel.active { display: flex; }

  /* Chat */
  #chat-messages { flex: 1; overflow-y: auto; padding: 16px 20px; }
  #demo-runner { background: linear-gradient(180deg, var(--surface2), var(--surface));
                 border: 1px solid var(--accent2); border-radius: 8px;
                 padding: 14px 18px; margin-bottom: 16px; max-width: 900px; }
  #demo-runner h3 { color: var(--accent2); font-size: 14px; margin-bottom: 6px; }
  #demo-runner .demo-controls { display: flex; gap: 8px; align-items: center;
                                 margin-top: 10px; flex-wrap: wrap; }
  #demo-scenario { background: var(--surface); color: var(--text);
                    border: 1px solid var(--border); border-radius: 4px;
                    padding: 6px 10px; font-family: inherit; font-size: 12px;
                    flex: 1; min-width: 200px; }
  #demo-runner button { background: var(--accent2); color: #000; border: none;
                         border-radius: 6px; padding: 8px 16px; font-family: inherit;
                         font-size: 12px; cursor: pointer; font-weight: bold; }
  #demo-runner button.secondary { background: var(--surface); color: var(--accent);
                                   border: 1px solid var(--accent); }
  #demo-runner button.danger { background: var(--surface); color: var(--warn);
                                border: 1px solid var(--warn); }
  #demo-runner button:disabled { opacity: 0.4; cursor: not-allowed; }
  #demo-runner .speed { font-size: 11px; color: var(--dim);
                        display: flex; align-items: center; gap: 6px; }
  #demo-runner .speed select { background: var(--surface); color: var(--text);
                                border: 1px solid var(--border); border-radius: 4px;
                                padding: 4px 8px; font-family: inherit; font-size: 11px; }
  #demo-summary { font-size: 12px; color: var(--dim); margin-top: 8px;
                  line-height: 1.5; font-style: italic; }
  #demo-progress { font-size: 11px; color: var(--accent); margin-top: 6px;
                   font-weight: bold; min-height: 14px; }
  #demo-moral { font-size: 12px; color: var(--accent2); margin-top: 8px;
                padding: 8px 12px; background: var(--surface2);
                border-left: 3px solid var(--accent2); border-radius: 4px;
                display: none; }
  #demo-moral.show { display: block; }
  .step-note { font-size: 10px; color: var(--dim); font-style: italic;
                margin: 4px 0 8px; }
  #welcome-card { background: var(--surface2); border: 1px solid var(--accent);
                  border-radius: 8px; padding: 16px 20px; margin-bottom: 16px;
                  position: relative; max-width: 900px; }
  #welcome-card h3 { color: var(--accent); font-size: 14px; margin-bottom: 8px; }
  #welcome-card h4 { color: var(--accent2); font-size: 12px; margin: 12px 0 6px; }
  #welcome-card p { font-size: 12px; line-height: 1.6; color: var(--text); margin-bottom: 8px; }
  #welcome-card ol { font-size: 12px; line-height: 1.7; padding-left: 20px; color: var(--text); }
  #welcome-card em { color: var(--accent2); font-style: normal; }
  #welcome-card .dismiss { position: absolute; top: 8px; right: 12px;
                           background: none; border: none; color: var(--dim);
                           font-size: 18px; cursor: pointer; }
  #welcome-card .dismiss:hover { color: var(--accent); }
  .msg { margin-bottom: 16px; max-width: 900px; }
  .msg.compare { max-width: 100%; }
  .compare-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 4px; }
  .compare-col { background: var(--surface); border: 1px solid var(--border);
                 border-radius: 6px; padding: 10px 14px; }
  .compare-col.raw { border-left: 3px solid var(--warn); }
  .compare-col.pep { border-left: 3px solid var(--accent2); }
  .compare-col .col-label { font-size: 10px; font-weight: bold; text-transform: uppercase;
                            margin-bottom: 6px; letter-spacing: 0.5px; }
  .compare-col.raw .col-label { color: var(--warn); }
  .compare-col.pep .col-label { color: var(--accent2); }
  .compare-col .col-body { font-size: 13px; line-height: 1.5; white-space: pre-wrap;
                           word-break: break-word; }
  .compare-toggle { font-size: 11px; color: var(--dim); display: flex;
                    align-items: center; gap: 6px; cursor: pointer; user-select: none; }
  .compare-toggle input { cursor: pointer; }
  .compare-toggle:hover { color: var(--accent); }
  .msg .role { font-size: 11px; font-weight: bold; margin-bottom: 2px; }
  .msg .role.user { color: var(--accent); }
  .msg .role.assistant { color: var(--accent2); }
  .msg .body { font-size: 13px; line-height: 1.5; white-space: pre-wrap; word-break: break-word; }
  .msg .trace-toggle { font-size: 11px; color: var(--dim); cursor: pointer;
                        margin-top: 4px; user-select: none; }
  .msg .trace-toggle:hover { color: var(--accent); }
  .msg .trace { display: none; margin-top: 6px; padding: 8px 12px;
                background: var(--surface2); border-radius: 6px;
                font-size: 11px; color: var(--dim); line-height: 1.6;
                max-height: 400px; overflow-y: auto; }
  .msg .trace.open { display: block; }
  .msg .trace .label { color: var(--accent); }
  .msg .trace .warn { color: var(--warn); }
  #chat-input-bar { padding: 12px 20px; border-top: 1px solid var(--border);
                     display: flex; gap: 8px; }
  #chat-input { flex: 1; background: var(--surface); color: var(--text);
                border: 1px solid var(--border); border-radius: 6px;
                padding: 10px 14px; font-family: inherit; font-size: 13px;
                outline: none; resize: none; }
  #chat-input:focus { border-color: var(--accent); }
  #send-btn { background: var(--accent); color: #000; border: none;
              border-radius: 6px; padding: 10px 20px; font-family: inherit;
              font-size: 13px; cursor: pointer; font-weight: bold; }
  #send-btn:disabled { opacity: 0.4; cursor: not-allowed; }
  #session-id { background: var(--surface); color: var(--text);
                border: 1px solid var(--border); border-radius: 4px;
                padding: 4px 8px; font-family: inherit; font-size: 11px;
                width: 120px; }
  #setup-link { color: var(--warn); cursor: pointer; text-decoration: underline;
                font-size: 11px; margin-left: 8px; }
  #setup-link:hover { color: var(--accent); }
  #setup-modal { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
                 background: rgba(0,0,0,0.7); z-index: 100; align-items: center;
                 justify-content: center; }
  #setup-modal.open { display: flex; }
  #setup-modal .modal-body { background: var(--surface2); border: 1px solid var(--accent);
                              border-radius: 8px; padding: 24px; max-width: 500px; }
  #setup-modal h2 { color: var(--accent); font-size: 16px; margin-bottom: 12px; }
  #setup-modal p { font-size: 12px; line-height: 1.6; margin-bottom: 12px; color: var(--text); }
  #setup-modal pre { background: var(--bg); padding: 12px; border-radius: 6px;
                     font-size: 12px; line-height: 1.6; color: var(--accent2); margin: 8px 0; }
  #setup-modal button { background: var(--accent); color: #000; border: none;
                        border-radius: 6px; padding: 8px 18px; font-family: inherit;
                        font-size: 12px; cursor: pointer; font-weight: bold; margin-top: 8px; }

  /* Dialogue */
  .dlg-turn { margin-bottom: 12px; padding: 10px 14px; border-radius: 6px;
              max-width: 80%; }
  .dlg-turn.agent-0 { background: var(--surface2); border-left: 3px solid #4fc3f7;
                       margin-right: auto; }
  .dlg-turn.agent-1 { background: var(--surface); border-right: 3px solid #81c784;
                       margin-left: auto; }
  .dlg-turn.agent-2 { background: var(--surface2); border-left: 3px solid #ffb74d;
                       margin-right: auto; margin-left: 8%; }
  .dlg-turn.agent-3 { background: var(--surface); border-right: 3px solid #ba68c8;
                       margin-left: auto; margin-right: 8%; }
  .dlg-turn.agent-4 { background: var(--surface2); border-left: 3px solid #f06292;
                       margin-right: auto; margin-left: 16%; }
  .dlg-turn .dlg-name { font-size: 10px; font-weight: bold; text-transform: uppercase;
                        letter-spacing: 0.5px; margin-bottom: 4px; }
  .dlg-turn.agent-0 .dlg-name { color: #4fc3f7; }
  .dlg-turn.agent-1 .dlg-name { color: #81c784; }
  .dlg-turn.agent-2 .dlg-name { color: #ffb74d; }
  .dlg-turn.agent-3 .dlg-name { color: #ba68c8; }
  .dlg-turn.agent-4 .dlg-name { color: #f06292; }
  .dlg-turn .dlg-text { font-size: 13px; line-height: 1.5; white-space: pre-wrap;
                        word-break: break-word; color: var(--text); }
  .dlg-turn .dlg-meta { font-size: 10px; color: var(--dim); margin-top: 6px; }
  .dlg-opening { padding: 10px 14px; background: var(--surface);
                  border: 1px dashed var(--border); border-radius: 6px;
                  margin-bottom: 16px; font-size: 12px; color: var(--dim); }
  .dlg-opening b { color: var(--text); }

  /* Sky View */
  .memory-card { background: var(--surface); border: 1px solid var(--border);
                 border-radius: 6px; padding: 12px 16px; margin: 8px 20px; }
  .memory-card .title { font-size: 12px; color: var(--accent); margin-bottom: 4px; }
  .memory-card .meta { font-size: 11px; color: var(--dim); margin-bottom: 4px; }
  .memory-card .content { font-size: 12px; color: var(--text); white-space: pre-wrap; }
  .memory-card .bar { display: inline-block; color: var(--accent2); letter-spacing: -2px; }
  .stat { display: inline-block; margin-right: 16px; font-size: 13px; color: var(--dim); }
  .stat b { color: var(--accent); font-size: 18px; }

  #sky-panel { display: none; flex-direction: column; }
  #sky-panel.active { display: flex; }
  #sky-toolbar { display: flex; align-items: center; gap: 16px;
                  padding: 10px 20px; border-bottom: 1px solid var(--border);
                  background: var(--bg); }
  #sky-toolbar .stat-inline { font-size: 12px; color: var(--dim); }
  #sky-toolbar .stat-inline b { color: var(--accent); font-size: 14px; }
  #sky-toolbar .legend { display: flex; gap: 14px; font-size: 11px; color: var(--dim); margin-left: auto; }
  #sky-toolbar .legend-dot { display: inline-block; width: 10px; height: 10px;
                              border-radius: 50%; margin-right: 4px; vertical-align: middle; }
  #sky-toolbar button { background: var(--surface); color: var(--accent);
                         border: 1px solid var(--accent); border-radius: 4px;
                         padding: 4px 12px; font-family: inherit; font-size: 11px;
                         cursor: pointer; }
  #sky-stage { position: relative; flex: 1; overflow: hidden; background: var(--bg); }
  #sky-canvas { display: block; cursor: grab; }
  #sky-canvas:active { cursor: grabbing; }
  #sky-tooltip { position: absolute; pointer-events: none; background: var(--surface2);
                  border: 1px solid var(--accent); border-radius: 6px;
                  padding: 8px 12px; font-size: 11px; color: var(--text);
                  max-width: 320px; line-height: 1.4; z-index: 10;
                  display: none; box-shadow: 0 4px 12px rgba(0,0,0,0.5); }
  #sky-tooltip.show { display: block; }
  #sky-tooltip .tip-id { color: var(--accent); font-weight: bold; margin-bottom: 4px; }
  #sky-tooltip .tip-meta { color: var(--dim); margin-bottom: 4px; font-size: 10px; }
  #sky-detail { position: absolute; top: 0; right: 0; width: 320px; bottom: 0;
                 background: var(--surface); border-left: 1px solid var(--border);
                 padding: 16px; overflow-y: auto; display: none; z-index: 5; }
  #sky-detail.show { display: block; }
  #sky-detail .close { float: right; background: none; border: none; color: var(--dim);
                       font-size: 18px; cursor: pointer; }
  #sky-detail .close:hover { color: var(--accent); }
  #sky-detail h3 { color: var(--accent); font-size: 13px; margin-bottom: 8px;
                    word-break: break-all; }
  #sky-detail .field { font-size: 11px; color: var(--dim); margin-bottom: 8px; }
  #sky-detail .field b { color: var(--text); }
  #sky-detail .core { font-size: 12px; color: var(--text); white-space: pre-wrap;
                       background: var(--bg); padding: 8px 10px; border-radius: 4px;
                       margin: 8px 0; max-height: 240px; overflow-y: auto; }
  #sky-detail .face { font-size: 11px; color: var(--text); margin-top: 6px;
                       padding: 6px 10px; background: var(--bg); border-radius: 4px;
                       border-left: 2px solid var(--accent2); }
  #sky-detail .face .face-name { color: var(--accent2); font-weight: bold;
                                   font-size: 10px; text-transform: uppercase; }

  /* Runs */
  .run-item { padding: 8px 20px; border-bottom: 1px solid var(--border);
              cursor: pointer; font-size: 12px; }
  .run-item:hover { background: var(--surface); }
  .run-detail { padding: 16px 20px; }
  .run-detail pre { background: var(--surface2); padding: 10px; border-radius: 6px;
                    font-size: 11px; overflow-x: auto; max-height: 500px; }
</style>
</head>
<body>

<header>
  <h1>PEP</h1>
  <span>Predictive Encoding and Preparation</span>
  <span style="margin-left:auto" id="health-status">...</span>
</header>

<div class="tabs">
  <div class="tab active" data-panel="chat-panel">Chat</div>
  <div class="tab" data-panel="sky-panel">Sky View</div>
  <div class="tab" data-panel="dialogue-panel">Dialogue</div>
  <div class="tab" data-panel="dictionary-panel">Dictionary</div>
  <div class="tab" data-panel="categories-panel">Categories</div>
  <div class="tab" data-panel="analysis-panel">Analysis</div>
  <div class="tab" data-panel="runs-panel">Runs</div>
  <div class="tab" data-panel="ingest-panel">Ingest</div>
  <div class="tab" data-panel="bench-panel">Benchmarks</div>
</div>

<div class="panels">

  <!-- Chat Panel -->
  <div class="panel active" id="chat-panel">
    <div id="chat-messages">

      <div id="demo-runner">
        <h3>▶ Demo Runner — press Start, watch what PEP does</h3>
        <p style="font-size:12px;color:var(--dim);line-height:1.5">
          A scripted bot will send PEP a sequence of messages so you can sit back
          and watch the conversation unfold. The <b>Compare with raw AI</b> toggle
          turns on automatically — every turn shows two answers side by side.
        </p>

        <div class="demo-controls">
          <select id="demo-scenario"></select>
          <button id="demo-start" onclick="startDemo()">Start</button>
          <button id="demo-stop" class="secondary" onclick="stopDemo()" disabled>Stop</button>
          <button id="demo-reset" class="danger" onclick="resetDemoMemory()">Reset memory</button>
          <span class="speed">
            speed:
            <select id="demo-speed">
              <option value="2500">slow</option>
              <option value="1200" selected>normal</option>
              <option value="400">fast</option>
            </select>
          </span>
        </div>

        <div id="demo-summary"></div>
        <div id="demo-progress"></div>
        <div id="demo-moral"></div>
      </div>

      <div id="welcome-card">
        <button class="dismiss" onclick="dismissWelcome()" title="dismiss">×</button>
        <h3>What is this?</h3>
        <p><b>PEP</b> is a memory and context layer that sits on top of a base AI.
        As you chat, PEP <em>remembers everything</em>, <em>links related ideas</em>,
        and <em>feeds the right context back into the AI</em> on every turn.
        The base AI does the reasoning; PEP makes sure it has the right information to reason with.</p>

        <h4>Try this (3 turns):</h4>
        <ol>
          <li>Turn on <b>Compare with raw AI</b> below.</li>
          <li>Tell PEP: <em>"I'm working on a project called PEP."</em></li>
          <li>Then: <em>"PEP stands for Predictive Encoding and Preparation."</em></li>
          <li>Then ask: <em>"What does my project do?"</em></li>
        </ol>
        <p>The <b>Raw AI</b> column will say "I don't have context."
        The <b>PEP</b> column will remember and answer — because earlier turns are now in its memory.
        Click <em>"trace"</em> below the PEP answer to see exactly which memories were activated.</p>
      </div>
    </div>
    <div id="chat-input-bar" style="flex-direction:column;align-items:stretch;gap:8px">
      <label class="compare-toggle">
        <input type="checkbox" id="compare-toggle"> Compare with raw AI (side-by-side)
      </label>
      <div style="display:flex;gap:8px">
        <input id="session-id" value="default" placeholder="session" title="Session ID">
        <textarea id="chat-input" rows="1" placeholder="Send a message to PEP..."></textarea>
        <button id="send-btn">Send</button>
      </div>
    </div>
  </div>

  <!-- Setup Modal -->
  <div id="setup-modal">
    <div class="modal-body">
      <h2>Set up a free local AI</h2>
      <p>PEP is currently running with a stub LLM (canned responses). To make the demo
      actually work, install <b>Ollama</b> — it runs a small AI model locally on your
      Mac. Free, no API costs.</p>
      <pre>brew install ollama
brew services start ollama
ollama pull llama3.2:3b</pre>
      <p>The model is about 2GB. After it downloads, refresh this page.
      The status bar will show <b>llm: ollama</b> and PEP will start giving real answers.</p>
      <button onclick="document.getElementById('setup-modal').classList.remove('open')">Got it</button>
    </div>
  </div>

  <!-- Sky View Panel -->
  <div class="panel" id="sky-panel">
    <div id="sky-toolbar">
      <span class="stat-inline"><b id="sky-count">0</b> memories</span>
      <span class="stat-inline"><b id="sky-link-count">0</b> links</span>
      <span class="stat-inline"><b id="sky-bright">0</b> bright</span>
      <button onclick="resetSkyView()">Refit</button>
      <button onclick="loadSky()">Refresh</button>
      <span class="legend">
        <span><span class="legend-dot" style="background:#4fc3f7"></span>conversation</span>
        <span><span class="legend-dot" style="background:#81c784"></span>summary</span>
        <span><span class="legend-dot" style="background:#ffb74d"></span>document</span>
        <span><span class="legend-dot" style="background:#ba68c8"></span>fact / abstraction</span>
      </span>
    </div>
    <div id="sky-stage">
      <canvas id="sky-canvas"></canvas>
      <div id="sky-tooltip"></div>
      <div id="sky-detail">
        <button class="close" onclick="closeSkyDetail()">×</button>
        <div id="sky-detail-content"></div>
      </div>
    </div>
  </div>

  <!-- Dialogue Panel -->
  <div class="panel" id="dialogue-panel">
    <div style="padding:16px 20px;max-width:1200px">
      <h2 style="font-size:16px;color:var(--accent2);margin-bottom:6px">
        Two PEP instances talking to each other
      </h2>
      <p style="font-size:12px;color:var(--dim);line-height:1.6;margin-bottom:14px">
        Two PEP-equipped agents converse for a fixed number of turns. Each agent has
        its own memory store, its own state vector, and its own persona. They take
        turns: A speaks, B receives the message via PEP's full overlay loop and stores
        it in B's memory, then B speaks, etc. After the dialogue runs, you can inspect
        each agent's memory and categories — they should look <em>different</em>,
        because each one stored the conversation from its own perspective.
      </p>

      <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:8px">
        <select id="dlg-personas" style="background:var(--surface);color:var(--text);
          border:1px solid var(--border);border-radius:4px;padding:6px 10px;font-family:inherit;font-size:12px;flex:1;min-width:240px">
        </select>
        <input id="dlg-turns" type="number" min="2" max="500" value="30"
          style="background:var(--surface);color:var(--text);border:1px solid var(--border);
          border-radius:4px;padding:6px 10px;font-family:inherit;font-size:12px;width:80px"
          title="max turns (ignored when auto-continue is on)">
        <label class="compare-toggle" style="white-space:nowrap">
          <input type="checkbox" id="dlg-auto"> auto-continue (run until Stop)
        </label>
      </div>
      <div style="display:flex;gap:8px;margin-bottom:8px">
        <input id="dlg-topic" placeholder="topic (optional — meta-context, not a message)"
          value="how memory shapes thinking"
          style="flex:1;background:var(--surface);color:var(--text);border:1px solid var(--border);
          border-radius:4px;padding:6px 10px;font-family:inherit;font-size:12px"
          title="Both agents see this in their system prompt as 'You are discussing: ...'. Steers them to stay on subject across many turns.">
      </div>
      <div style="display:flex;gap:8px;margin-bottom:8px">
        <input id="dlg-opening" placeholder="opening line (the first message)"
          value="So — where do you want to start?"
          style="flex:1;background:var(--surface);color:var(--text);border:1px solid var(--border);
          border-radius:4px;padding:6px 10px;font-family:inherit;font-size:12px">
      </div>
      <div style="display:flex;gap:8px;margin-bottom:14px;align-items:center;flex-wrap:wrap">
        <button onclick="startDialogue()" id="dlg-start"
          style="background:var(--accent2);color:#000;border:none;border-radius:6px;
          padding:8px 18px;font-family:inherit;font-size:13px;cursor:pointer;font-weight:bold">Start</button>
        <button onclick="stopDialogue()" id="dlg-stop" disabled
          style="background:var(--surface);color:var(--accent);border:1px solid var(--accent);
          border-radius:6px;padding:8px 18px;font-family:inherit;font-size:13px;cursor:pointer">Stop</button>
        <button onclick="resetDialogue()" id="dlg-reset"
          style="background:var(--surface);color:var(--warn);border:1px solid var(--warn);
          border-radius:6px;padding:8px 18px;font-family:inherit;font-size:13px;cursor:pointer">Reset agents</button>
        <button onclick="saveDialogueTranscript()" id="dlg-save" disabled
          style="background:var(--surface);color:var(--accent2);border:1px solid var(--accent2);
          border-radius:6px;padding:8px 18px;font-family:inherit;font-size:13px;cursor:pointer">Save transcript</button>
        <span id="dlg-status" style="font-size:11px;color:var(--dim)"></span>
      </div>

      <div id="dlg-personas-display" style="font-size:11px;color:var(--dim);
        margin-bottom:12px;padding:10px 14px;background:var(--surface);
        border-radius:4px;line-height:1.6"></div>

      <div id="dlg-transcript"></div>

      <!-- State coupling chart (live, populated as turns stream) -->
      <div id="dlg-state-chart" style="display:none;margin-top:20px;
        background:var(--surface);border:1px solid var(--border);border-radius:6px;
        padding:14px 18px">
        <h3 style="font-size:13px;color:var(--accent2);margin-bottom:6px">
          State coupling — both agents over time
        </h3>
        <p style="font-size:11px;color:var(--dim);line-height:1.5;margin-bottom:8px">
          Each agent's state vector across turns. <span style="color:var(--accent)">Alice cyan</span>,
          <span style="color:var(--accent2)">Bob green</span>. If the two lines move together,
          the agents' processing modes are coupling — one's urgency raises the other's, etc.
          That's the §8.8 question made visible.
        </p>
        <div id="dlg-state-grid"
          style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px"></div>
      </div>

      <!-- Per-agent coherence panel (visible after dialogue runs) -->
      <div id="dlg-coherence-panel" style="display:none;margin-top:20px;
        background:var(--surface2);border:1px solid var(--accent2);border-radius:6px;
        padding:14px 18px">
        <h3 style="font-size:13px;color:var(--accent2);margin-bottom:6px">
          Per-agent vs combined coherence
        </h3>
        <p style="font-size:11px;color:var(--dim);line-height:1.5;margin-bottom:10px">
          Run the multi-scale coherence experiment three times: once on Alice's memory,
          once on Bob's, once on the union. Different numbers mean the joint memory has
          different structure than either agent alone — answering §8.8 of the research note.
          Run consolidation first if you want categories to exist.
        </p>
        <div style="display:flex;gap:8px;margin-bottom:10px">
          <input id="dlg-coherence-query" placeholder="query (e.g. memory)"
            style="background:var(--surface);color:var(--text);border:1px solid var(--border);
            border-radius:4px;padding:6px 10px;font-family:inherit;font-size:12px;flex:1">
          <button onclick="runDialogueCoherence()"
            style="background:var(--accent2);color:#000;border:none;border-radius:6px;
            padding:6px 16px;font-family:inherit;font-size:12px;cursor:pointer;font-weight:bold">Compare</button>
        </div>
        <div id="dlg-coherence-results"></div>
      </div>
    </div>
  </div>

  <!-- Dictionary Panel -->
  <div class="panel" id="dictionary-panel">
    <div style="padding:16px 20px;max-width:1200px">
      <h2 style="font-size:16px;color:var(--accent2);margin-bottom:6px">
        Dictionary — paste a dictionary, see word connections
      </h2>
      <p style="font-size:12px;color:var(--dim);line-height:1.6;margin-bottom:14px">
        A dictionary is a graph of words linked by their definitions. Paste one or two
        dictionaries below (one per language). Each headword becomes a memory; words
        appearing in each other's definitions become linked. The result is a navigable
        word graph you can compare across languages.
      </p>
      <p style="font-size:11px;color:var(--dim);line-height:1.5;margin-bottom:14px;
                background:var(--surface);padding:8px 12px;border-radius:4px">
        Format: one entry per line as <code>word: definition</code> (or <code>word - definition</code>,
        or tab-separated). Empty lines and lines starting with <code>#</code> are skipped.
      </p>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
        <!-- Dictionary A -->
        <div>
          <h3 style="font-size:13px;color:var(--accent);margin-bottom:6px">Language A</h3>
          <div style="display:flex;gap:6px;margin-bottom:6px">
            <input id="dict-a-language" value="english" placeholder="language name"
              style="background:var(--surface);color:var(--text);border:1px solid var(--border);
              border-radius:4px;padding:6px 10px;font-family:inherit;font-size:12px;flex:1">
          </div>
          <textarea id="dict-a-text" rows="14"
            placeholder="memory: a stored representation of past experience used to inform present decisions
prediction: an inference about a future state based on a model of the present
context: the surrounding information that gives meaning to a fact
inference: the process of drawing a conclusion from premises
model: a structured representation that captures regularities in some domain"
            style="width:100%;background:var(--surface);color:var(--text);border:1px solid var(--border);
            border-radius:4px;padding:8px 10px;font-family:'SF Mono','Consolas',monospace;font-size:11px;
            resize:vertical;line-height:1.5"></textarea>
          <button onclick="ingestDictionary('a')" id="dict-a-btn"
            style="background:var(--accent);color:#000;border:none;border-radius:4px;
            padding:6px 14px;font-family:inherit;font-size:12px;cursor:pointer;
            font-weight:bold;margin-top:6px">Ingest A</button>
          <span id="dict-a-status" style="font-size:11px;color:var(--dim);margin-left:8px"></span>
        </div>

        <!-- Dictionary B -->
        <div>
          <h3 style="font-size:13px;color:var(--accent2);margin-bottom:6px">Language B</h3>
          <div style="display:flex;gap:6px;margin-bottom:6px">
            <input id="dict-b-language" value="spanish" placeholder="language name"
              style="background:var(--surface);color:var(--text);border:1px solid var(--border);
              border-radius:4px;padding:6px 10px;font-family:inherit;font-size:12px;flex:1">
          </div>
          <textarea id="dict-b-text" rows="14"
            placeholder="memoria: una representación almacenada de experiencias pasadas usada para informar decisiones presentes
predicción: una inferencia sobre un estado futuro basada en un modelo del presente
contexto: la información circundante que da significado a un hecho
inferencia: el proceso de extraer una conclusión a partir de premisas
modelo: una representación estructurada que captura regularidades en algún dominio"
            style="width:100%;background:var(--surface);color:var(--text);border:1px solid var(--border);
            border-radius:4px;padding:8px 10px;font-family:'SF Mono','Consolas',monospace;font-size:11px;
            resize:vertical;line-height:1.5"></textarea>
          <button onclick="ingestDictionary('b')" id="dict-b-btn"
            style="background:var(--accent2);color:#000;border:none;border-radius:4px;
            padding:6px 14px;font-family:inherit;font-size:12px;cursor:pointer;
            font-weight:bold;margin-top:6px">Ingest B</button>
          <span id="dict-b-status" style="font-size:11px;color:var(--dim);margin-left:8px"></span>
        </div>
      </div>

      <div style="margin-top:16px;display:flex;gap:8px;align-items:center;flex-wrap:wrap">
        <button onclick="compareDictionaries()" id="dict-compare-btn"
          style="background:var(--surface);color:var(--accent2);border:1px solid var(--accent2);
          border-radius:6px;padding:8px 18px;font-family:inherit;font-size:13px;cursor:pointer;
          font-weight:bold">Compare A vs B</button>
        <button onclick="viewDictionaryInSky('a')"
          style="background:var(--surface);color:var(--accent);border:1px solid var(--accent);
          border-radius:6px;padding:8px 18px;font-family:inherit;font-size:12px;cursor:pointer">View A in Sky</button>
        <button onclick="viewDictionaryInSky('b')"
          style="background:var(--surface);color:var(--accent2);border:1px solid var(--accent2);
          border-radius:6px;padding:8px 18px;font-family:inherit;font-size:12px;cursor:pointer">View B in Sky</button>
        <button onclick="resetDictionaries()"
          style="background:var(--surface);color:var(--warn);border:1px solid var(--warn);
          border-radius:6px;padding:8px 18px;font-family:inherit;font-size:12px;cursor:pointer">Reset both</button>
      </div>

      <div id="dict-comparison" style="margin-top:16px"></div>
    </div>
  </div>

  <!-- Categories Panel -->
  <div class="panel" id="categories-panel">
    <div style="padding:16px 20px">
      <div style="display:flex;gap:12px;align-items:center;margin-bottom:16px">
        <h2 style="font-size:16px;color:var(--accent)">Categories (Folds)</h2>
        <button onclick="runConsolidate()" style="background:var(--surface);color:var(--accent);
          border:1px solid var(--accent);border-radius:6px;padding:6px 14px;font-family:inherit;
          font-size:12px;cursor:pointer">Run Consolidation</button>
        <span id="consolidate-status" style="font-size:11px;color:var(--dim)"></span>
      </div>

      <div style="background:var(--surface2);border:1px solid var(--accent2);border-radius:6px;
                  padding:12px 16px;margin-bottom:16px;max-width:900px">
        <h3 style="font-size:13px;color:var(--accent2);margin-bottom:6px">Multi-scale coherence</h3>
        <p style="font-size:11px;color:var(--dim);line-height:1.5;margin-bottom:10px">
          Score every memory against a query (fine scale), aggregate per category (coarse scale),
          then compute the Spearman rank correlation between the two. High ρ = the category structure
          preserves what's actually relevant. Low ρ = categorization is decoupled from relevance.
          Workflow: <em>run a demo → run consolidation → test a query that matches the demo's topic</em>.
        </p>
        <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
          <input id="coherence-query" placeholder="query (e.g. neural network)"
            style="background:var(--surface);color:var(--text);border:1px solid var(--border);
            border-radius:4px;padding:6px 10px;font-family:inherit;font-size:12px;flex:1;min-width:240px">
          <button onclick="runCoherence()" style="background:var(--accent2);color:#000;border:none;
            border-radius:6px;padding:6px 16px;font-family:inherit;font-size:12px;cursor:pointer;
            font-weight:bold">Test coherence</button>
        </div>
        <pre id="coherence-output" style="background:var(--bg);padding:10px 14px;border-radius:4px;
          font-size:11px;color:var(--text);margin-top:10px;white-space:pre-wrap;
          max-height:480px;overflow-y:auto;display:none;line-height:1.5"></pre>
      </div>

      <div id="categories-list"></div>
    </div>
  </div>

  <!-- Analysis Panel — research-y experiments against the live store -->
  <div class="panel" id="analysis-panel">
    <div style="padding:16px 20px;max-width:900px">
      <h2 style="font-size:16px;color:var(--accent2);margin-bottom:6px">
        Analysis — research findings against the live store
      </h2>
      <p style="font-size:12px;color:var(--dim);line-height:1.6;margin-bottom:14px">
        Closes open questions from the research note (<code>docs/research_note.md</code> §8).
        These analyses run against your actual memory store, so they update as you use PEP.
      </p>

      <!-- §8.1: Trajectory score validation -->
      <div style="background:var(--surface2);border:1px solid var(--accent2);border-radius:6px;
                  padding:14px 18px;margin-bottom:16px">
        <h3 style="font-size:14px;color:var(--accent2);margin-bottom:6px">
          §8.1 — Does the trajectory score predict reactivation?
        </h3>
        <p style="font-size:11px;color:var(--dim);line-height:1.5;margin-bottom:10px">
          Every memory has a <code>trajectory_at_storage</code> value the Updater computed
          (the system's prediction of "will this matter for future turns?") and an
          <code>activation_count</code> (how often the Reactivator actually pulled it).
          Spearman ρ between the two tells you whether the prediction is doing real work
          or just adding noise to the storage gate.
        </p>
        <button onclick="loadTrajectoryAnalysis()" id="traj-load"
          style="background:var(--accent2);color:#000;border:none;border-radius:6px;
          padding:6px 16px;font-family:inherit;font-size:12px;cursor:pointer;font-weight:bold">Run analysis</button>
        <button onclick="loadTrajectoryComparison()" id="traj-compare"
          style="background:var(--surface);color:var(--accent2);border:1px solid var(--accent2);
          border-radius:6px;padding:6px 16px;font-family:inherit;font-size:12px;cursor:pointer;
          margin-left:6px">Compare LLM vs heuristic</button>
        <span id="traj-status" style="font-size:11px;color:var(--dim);margin-left:10px"></span>
        <div id="traj-headline" style="display:none;margin-top:14px"></div>
        <div id="traj-scatter-wrap" style="display:none;margin-top:12px;
          background:var(--bg);padding:10px;border-radius:4px">
          <svg id="traj-scatter" width="100%" height="360" viewBox="0 0 600 360"
            preserveAspectRatio="xMidYMid meet"></svg>
        </div>
        <div id="traj-tables" style="display:none;margin-top:12px"></div>
      </div>
    </div>
  </div>

  <!-- Runs Panel -->
  <div class="panel" id="runs-panel">
    <div id="runs-list"></div>
    <div id="run-detail" class="run-detail" style="display:none"></div>
  </div>

  <!-- Benchmarks Panel -->
  <div class="panel" id="bench-panel">
    <div style="padding:16px 20px;max-width:1100px">
      <h2 style="font-size:16px;color:var(--accent);margin-bottom:8px">Benchmarks</h2>
      <p style="font-size:12px;color:var(--dim);margin-bottom:12px">
        Run a benchmark across all three policies (recent_window, semantic_topk, pep_full)
        and compare them side by side. Each benchmark uses its own seeded memory store
        — your real PEP data is untouched.
      </p>
      <div style="display:flex;gap:8px;margin-bottom:12px;align-items:center;flex-wrap:wrap">
        <select id="bench-name" style="background:var(--surface);color:var(--text);
          border:1px solid var(--border);border-radius:4px;padding:6px 10px;font-family:inherit;font-size:12px">
          <option value="ambiguity">ambiguity</option>
          <option value="long_horizon_recall">long_horizon_recall</option>
          <option value="distractor_resistance">distractor_resistance</option>
          <option value="state_dependent_retrieval">state_dependent_retrieval</option>
        </select>
        <select id="bench-policy" style="background:var(--surface);color:var(--text);
          border:1px solid var(--border);border-radius:4px;padding:6px 10px;font-family:inherit;font-size:12px">
          <option value="all">all policies</option>
          <option value="recent_window">recent_window only</option>
          <option value="semantic_topk">semantic_topk only</option>
          <option value="pep_full">pep_full only</option>
        </select>
        <button onclick="runBench()" style="background:var(--accent);color:#000;border:none;
          border-radius:6px;padding:8px 18px;font-family:inherit;font-size:13px;cursor:pointer;
          font-weight:bold">Run</button>
        <span id="bench-status" style="font-size:11px;color:var(--dim)"></span>
      </div>
      <div id="bench-results"></div>
    </div>
  </div>

  <!-- Ingest Panel -->
  <div class="panel" id="ingest-panel">
    <div style="padding:16px 20px;max-width:800px">
      <h2 style="font-size:16px;color:var(--accent);margin-bottom:8px">Ingest Text</h2>
      <p style="font-size:12px;color:var(--dim);margin-bottom:12px">
        Paste text below. PEP will split it by blank lines and store each paragraph
        as a separate memory. These memories become retrievable in future chat turns.
      </p>
      <textarea id="ingest-text" rows="12" style="width:100%;background:var(--surface);
        color:var(--text);border:1px solid var(--border);border-radius:6px;padding:10px 14px;
        font-family:inherit;font-size:13px;resize:vertical" placeholder="Paste text here..."></textarea>
      <div style="display:flex;gap:8px;margin-top:8px;align-items:center">
        <input id="ingest-session" value="default" placeholder="session id"
          style="background:var(--surface);color:var(--text);border:1px solid var(--border);
          border-radius:4px;padding:6px 10px;font-family:inherit;font-size:12px;width:140px">
        <button onclick="doIngest()" style="background:var(--accent);color:#000;border:none;
          border-radius:6px;padding:8px 18px;font-family:inherit;font-size:13px;cursor:pointer;
          font-weight:bold">Ingest</button>
        <span id="ingest-status" style="font-size:12px;color:var(--dim)"></span>
      </div>
    </div>
  </div>

</div>

<script>
// Tabs
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById(tab.dataset.panel).classList.add('active');
    if (tab.dataset.panel === 'sky-panel') loadSky();
    if (tab.dataset.panel === 'dialogue-panel') loadDialoguePersonas();
    if (tab.dataset.panel === 'categories-panel') loadCategories();
    if (tab.dataset.panel === 'runs-panel') loadRuns();
  });
});

// Health
fetch('/health').then(r=>r.json()).then(d=>{
  const status = document.getElementById('health-status');
  status.textContent = `llm: ${d.llm} | embeddings: ${d.embeddings}`;
  if (d.llm === 'stub') {
    const link = document.createElement('span');
    link.id = 'setup-link';
    link.textContent = 'set up real AI →';
    link.onclick = () => document.getElementById('setup-modal').classList.add('open');
    status.appendChild(link);
  }
});

// Welcome card dismissal (persisted in localStorage)
function dismissWelcome() {
  document.getElementById('welcome-card').style.display = 'none';
  try { localStorage.setItem('pep_welcome_dismissed', '1'); } catch(e) {}
}
if (localStorage.getItem('pep_welcome_dismissed') === '1') {
  const wc = document.getElementById('welcome-card');
  if (wc) wc.style.display = 'none';
}

// Chat
const msgs = document.getElementById('chat-messages');
const input = document.getElementById('chat-input');
const btn = document.getElementById('send-btn');
const sessionInput = document.getElementById('session-id');

input.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMsg(); }
});
btn.addEventListener('click', sendMsg);

// Auto-resize textarea
input.addEventListener('input', () => {
  input.style.height = 'auto';
  input.style.height = Math.min(input.scrollHeight, 120) + 'px';
});

async function sendMsg() {
  const text = input.value.trim();
  if (!text) return;
  input.value = ''; input.style.height = 'auto';
  btn.disabled = true;

  appendMsg('user', text);

  const compare = document.getElementById('compare-toggle').checked;

  try {
    if (compare) {
      const res = await fetch('/chat/compare', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({text, session_id: sessionInput.value})
      });
      const data = await res.json();
      appendCompareMsg(data);
    } else {
      // Streaming path: use /chat/stream + SSE so text appears live
      await streamMsg(text);
    }
  } catch(e) {
    appendMsg('assistant', '[error: ' + e.message + ']');
  }
  btn.disabled = false;
  input.focus();
}

async function streamMsg(text) {
  // Create the assistant message div upfront so chunks have somewhere to land
  const div = document.createElement('div');
  div.className = 'msg';
  div.innerHTML = `<div class="role assistant">assistant</div><div class="body"></div>`;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;

  const bodyEl = div.querySelector('.body');
  let bodyText = '';
  let finalData = null;

  const res = await fetch('/chat/stream', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({text, session_id: sessionInput.value})
  });

  if (!res.ok || !res.body) {
    bodyEl.textContent = '[stream failed: HTTP ' + res.status + ']';
    return;
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  // SSE parser: events are separated by blank lines
  while (true) {
    const {done, value} = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, {stream: true});

    let idx;
    while ((idx = buffer.indexOf('\\n\\n')) >= 0) {
      const block = buffer.slice(0, idx);
      buffer = buffer.slice(idx + 2);

      // Parse: each block has 'event: name' and 'data: json' lines
      let eventName = 'message';
      let dataLine = '';
      block.split('\\n').forEach(line => {
        if (line.startsWith('event: ')) eventName = line.slice(7).trim();
        else if (line.startsWith('data: ')) dataLine += line.slice(6);
      });
      if (!dataLine) continue;

      let payload;
      try { payload = JSON.parse(dataLine); }
      catch(e) { continue; }

      if (eventName === 'chunk') {
        bodyText += payload.text || '';
        bodyEl.textContent = bodyText;
        msgs.scrollTop = msgs.scrollHeight;
      } else if (eventName === 'trace_pre') {
        // Could show the activated memories before the LLM speaks; for now we
        // just remember the packet and use the final 'done' for the trace.
      } else if (eventName === 'done') {
        finalData = payload;
      } else if (eventName === 'error') {
        bodyEl.textContent += '\\n[stream error: ' + (payload.message || '?') + ']';
      }
    }
  }

  // After the stream closes, attach the trace expander
  if (finalData && finalData.packet) {
    const fakeChatData = {
      response: finalData.response || bodyText,
      packet: finalData.packet,
      state_after: finalData.state_after,
    };
    const traceBlock = renderTraceBlock(fakeChatData);
    div.appendChild(traceBlock);
  }
}

function appendCompareMsg(data) {
  const div = document.createElement('div');
  div.className = 'msg compare';
  const rawText = (data.raw && data.raw.response) || '(no raw response)';
  const pepText = (data.pep && data.pep.response) || '(no pep response)';

  // Build the trace block for the PEP side using the existing renderer
  const pepData = data.pep || {};
  const tracePayload = {
    response: pepText,
    packet: pepData.packet,
    state_after: pepData.state_after,
  };

  div.innerHTML = `
    <div class="role assistant">assistant (compare)</div>
    <div class="compare-grid">
      <div class="compare-col raw">
        <div class="col-label">Raw AI (no memory)</div>
        <div class="col-body">${esc(rawText)}</div>
      </div>
      <div class="compare-col pep">
        <div class="col-label">PEP + AI (with memory)</div>
        <div class="col-body">${esc(pepText)}</div>
        <div id="pep-trace-slot"></div>
      </div>
    </div>
  `;
  msgs.appendChild(div);

  // Inject the existing trace renderer into the PEP column
  if (pepData.packet) {
    const traceDiv = renderTraceBlock(pepData);
    div.querySelector('#pep-trace-slot').appendChild(traceDiv);
  }
  msgs.scrollTop = msgs.scrollHeight;
}

function renderTraceBlock(data) {
  // Reuses the same trace markup as appendMsg(), extracted so compare mode can call it.
  const wrap = document.createElement('div');
  if (!data.packet) return wrap;
  const p = data.packet;
  const t = p.activation_trace || {};
  const r = p.residual || {};
  const m = p.metrics || {};
  const totalTime = Object.values(m).reduce((a,b)=>a+b, 0).toFixed(3);

  let traceHtml = '';
  traceHtml += `<span class="label">intent:</span> ${p.interpreted?.task_type || '?'} | `;
  traceHtml += `<span class="label">topic:</span> ${p.interpreted?.topic || '?'}\\n`;
  traceHtml += `<span class="label">memories:</span> ${(p.selected_memories||[]).length} | `;
  traceHtml += `<span class="label">novelty:</span> ${(r.novelty_score||0).toFixed(2)} | `;
  traceHtml += `<span class="label">trajectory:</span> ${(r.trajectory_score||0.5).toFixed(2)} | `;
  traceHtml += `<span class="label">stored:</span> ${r.should_store ? 'yes' : 'no'}\\n`;

  if ((t.activated||[]).length) {
    traceHtml += `\\n<span class="label">activated:</span>\\n`;
    (t.activated||[]).forEach(a => {
      const c = a.constellation_id != null ? ` [constellation #${a.constellation_id}]` : '';
      traceHtml += `  ${a.memory_id} score=${a.score.toFixed(3)} face=${a.face_used}${c}\\n`;
    });
  }
  if ((t.constellations||[]).length) {
    traceHtml += `\\n<span class="label">constellations:</span>\\n`;
    (t.constellations||[]).forEach(c => {
      traceHtml += `  #${c.id}: ${c.member_ids.length} members, cohesion=${c.cohesion.toFixed(2)}\\n`;
    });
  }
  if (t.fallback_to_strategic_search) {
    traceHtml += `\\n<span class="warn">strategic fallback: ${t.fallback_reason||''}</span>\\n`;
  }
  traceHtml += `\\n<span class="label">timing:</span> ${totalTime}s`;

  wrap.innerHTML =
    `<div class="trace-toggle" onclick="this.nextElementSibling.classList.toggle('open')">` +
    `trace (${(p.selected_memories||[]).length} memories, ${totalTime}s)</div>` +
    `<div class="trace">${traceHtml}</div>`;
  return wrap;
}

function appendMsg(role, text, data) {
  const div = document.createElement('div');
  div.className = 'msg';
  let html = `<div class="role ${role}">${role}</div><div class="body">${esc(text)}</div>`;
  if (data && data.packet) {
    const p = data.packet;
    const t = p.activation_trace || {};
    const r = p.residual || {};
    const m = p.metrics || {};
    const totalTime = Object.values(m).reduce((a,b)=>a+b, 0).toFixed(3);
    let traceHtml = '';
    traceHtml += `<span class="label">intent:</span> ${p.interpreted?.task_type || '?'} | `;
    traceHtml += `<span class="label">topic:</span> ${p.interpreted?.topic || '?'}\\n`;
    traceHtml += `<span class="label">memories:</span> ${(p.selected_memories||[]).length} | `;
    traceHtml += `<span class="label">novelty:</span> ${(r.novelty_score||0).toFixed(2)} | `;
    traceHtml += `<span class="label">trajectory:</span> ${(r.trajectory_score||0.5).toFixed(2)} | `;
    traceHtml += `<span class="label">stored:</span> ${r.should_store ? 'yes' : 'no'}\\n`;

    if ((t.activated||[]).length) {
      traceHtml += `\\n<span class="label">activated:</span>\\n`;
      (t.activated||[]).forEach(a => {
        const c = a.constellation_id != null ? ` [constellation #${a.constellation_id}]` : '';
        traceHtml += `  ${a.memory_id} score=${a.score.toFixed(3)} face=${a.face_used}${c}\\n`;
      });
    }
    if ((t.constellations||[]).length) {
      traceHtml += `\\n<span class="label">constellations:</span>\\n`;
      (t.constellations||[]).forEach(c => {
        traceHtml += `  #${c.id}: ${c.member_ids.length} members, cohesion=${c.cohesion.toFixed(2)}\\n`;
      });
    }
    if ((t.resolved_terms||[]).length) {
      traceHtml += `\\n<span class="label">sense disambiguation:</span>\\n`;
      (t.resolved_terms||[]).forEach(rt => {
        const chosen = rt.chosen_sense ? rt.chosen_sense.sense_label : '?';
        traceHtml += `  ${rt.term}: chose "${chosen}" (ambiguity=${rt.ambiguity_score.toFixed(2)})\\n`;
      });
    }
    if (t.fallback_to_strategic_search) {
      traceHtml += `\\n<span class="warn">strategic fallback: ${t.fallback_reason||''}</span>\\n`;
    }

    const stateAfter = data.state_after || {};
    traceHtml += `\\n<span class="label">state:</span> `;
    ['urgency','uncertainty','novelty','conflict','exploration'].forEach(k => {
      traceHtml += `${k}=${(stateAfter[k]||0).toFixed(2)} `;
    });
    traceHtml += `\\n<span class="label">timing:</span> ${totalTime}s`;

    html += `<div class="trace-toggle" onclick="this.nextElementSibling.classList.toggle('open')">` +
            `trace (${(p.selected_memories||[]).length} memories, ${totalTime}s)</div>`;
    html += `<div class="trace">${traceHtml}</div>`;
  }
  div.innerHTML = html;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
}

function esc(s) { const d=document.createElement('div'); d.textContent=s; return d.innerHTML; }

// Sky View — force-directed visual graph
// NOTE: do not reference `d3` at script load time. The CDN may not be ready
// (or may be unreachable entirely) when this script first parses; touching
// `d3.anything` here would throw ReferenceError and kill the WHOLE script
// block — including the tab click handler. Keep d3 references inside functions.
let skyState = {
  simulation: null,
  nodes: [],
  links: [],
  transform: null,  // populated lazily inside initSkyCanvas
  hovered: null,
  selected: null,
};

const SKY_COLORS = {
  conversation: '#4fc3f7',
  summary: '#81c784',
  document: '#ffb74d',
  fact: '#ba68c8',
  abstraction: '#ba68c8',
};

async function loadSky() {
  // Graceful degradation if D3 didn't load (CDN unreachable, offline, etc.)
  if (typeof d3 === 'undefined') {
    const stage = document.getElementById('sky-stage');
    if (stage) {
      stage.innerHTML = '<div style="padding:32px;color:var(--warn);font-size:13px;line-height:1.6">' +
        'D3.js failed to load (CDN unreachable?). The Sky View needs D3 for the force-directed graph. ' +
        'Try refreshing, or check your network connection.' +
        '</div>';
    }
    return;
  }
  const res = await fetch('/memories');
  const mems = await res.json();

  // Build nodes + links
  const nodes = mems.map(m => ({
    id: m.id,
    brightness: m.brightness || 0.5,
    drift: m.drift_score || 0,
    activation_count: m.activation_count || 0,
    core: m.core || '',
    tags: m.tags || [],
    faces: m.faces || {},
    source_type: m.source_type || 'conversation',
    links_out: m.links || [],
  }));
  const idSet = new Set(nodes.map(n => n.id));
  const links = [];
  nodes.forEach(n => {
    n.links_out.forEach(l => {
      if (idSet.has(l.to_id) && l.to_id !== n.id) {
        links.push({source: n.id, target: l.to_id, weight: l.weight || 0.5});
      }
    });
  });

  document.getElementById('sky-count').textContent = nodes.length;
  document.getElementById('sky-link-count').textContent = links.length;
  document.getElementById('sky-bright').textContent =
    nodes.filter(n => n.brightness >= 0.7).length;

  skyState.nodes = nodes;
  skyState.links = links;

  initSkyCanvas();
}

function initSkyCanvas() {
  // Lazy-init the d3 zoom identity now that we know d3 is loaded
  if (skyState.transform === null) {
    skyState.transform = d3.zoomIdentity;
  }

  const stage = document.getElementById('sky-stage');
  const canvas = document.getElementById('sky-canvas');
  const ctx = canvas.getContext('2d');

  // Resize to fit container
  function resize() {
    const dpr = window.devicePixelRatio || 1;
    const rect = stage.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    canvas.style.width = rect.width + 'px';
    canvas.style.height = rect.height + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  resize();
  window.addEventListener('resize', resize);

  const width = canvas.clientWidth;
  const height = canvas.clientHeight;

  // Stop any prior simulation
  if (skyState.simulation) skyState.simulation.stop();

  // Force simulation
  skyState.simulation = d3.forceSimulation(skyState.nodes)
    .force('link', d3.forceLink(skyState.links)
      .id(d => d.id)
      .distance(d => 60 + (1 - (d.weight || 0.5)) * 40)
      .strength(d => 0.4 * (d.weight || 0.5)))
    .force('charge', d3.forceManyBody().strength(-80))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collide', d3.forceCollide(d => 6 + d.brightness * 18))
    .alphaDecay(0.04);

  skyState.simulation.on('tick', draw);

  // Pan + zoom via D3
  const d3canvas = d3.select(canvas);
  d3canvas.call(d3.zoom()
    .scaleExtent([0.2, 5])
    .on('zoom', (event) => {
      skyState.transform = event.transform;
      draw();
    })
  );

  // Mouse interactions
  canvas.onmousemove = (event) => {
    const node = nodeAtEvent(event);
    skyState.hovered = node;
    if (node) {
      showTooltip(node, event);
    } else {
      hideTooltip();
    }
    draw();
  };
  canvas.onmouseleave = () => {
    skyState.hovered = null;
    hideTooltip();
    draw();
  };
  canvas.onclick = (event) => {
    const node = nodeAtEvent(event);
    if (node) {
      skyState.selected = node;
      showSkyDetail(node);
    }
  };

  function draw() {
    const w = canvas.clientWidth, h = canvas.clientHeight;
    ctx.save();
    ctx.fillStyle = '#0e0e10';
    ctx.fillRect(0, 0, w, h);
    ctx.translate(skyState.transform.x, skyState.transform.y);
    ctx.scale(skyState.transform.k, skyState.transform.k);

    // Draw links first so they're under the nodes
    ctx.lineCap = 'round';
    skyState.links.forEach(l => {
      const opacity = 0.15 + (l.weight || 0.5) * 0.35;
      ctx.strokeStyle = `rgba(79, 195, 247, ${opacity})`;
      ctx.lineWidth = 0.5 + (l.weight || 0.5) * 1.5;
      ctx.beginPath();
      ctx.moveTo(l.source.x, l.source.y);
      ctx.lineTo(l.target.x, l.target.y);
      ctx.stroke();
    });

    // Draw nodes
    skyState.nodes.forEach(n => {
      const r = 4 + n.brightness * 16;
      const color = SKY_COLORS[n.source_type] || '#4fc3f7';

      // Halo (subtle outer glow)
      const haloR = r + 3 + n.brightness * 4;
      const grad = ctx.createRadialGradient(n.x, n.y, r * 0.5, n.x, n.y, haloR);
      grad.addColorStop(0, color + 'aa');
      grad.addColorStop(1, color + '00');
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(n.x, n.y, haloR, 0, Math.PI * 2);
      ctx.fill();

      // Core star
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(n.x, n.y, r, 0, Math.PI * 2);
      ctx.fill();

      // Highlight ring if hovered or selected
      if (skyState.hovered === n || skyState.selected === n) {
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 2 / skyState.transform.k;
        ctx.beginPath();
        ctx.arc(n.x, n.y, r + 3, 0, Math.PI * 2);
        ctx.stroke();
      }
    });

    ctx.restore();
  }

  function nodeAtEvent(event) {
    const rect = canvas.getBoundingClientRect();
    const x = (event.clientX - rect.left - skyState.transform.x) / skyState.transform.k;
    const y = (event.clientY - rect.top - skyState.transform.y) / skyState.transform.k;
    // Find the closest node within its radius
    let best = null;
    let bestDist = Infinity;
    skyState.nodes.forEach(n => {
      const r = 4 + n.brightness * 16;
      const dx = n.x - x, dy = n.y - y;
      const dist = Math.sqrt(dx*dx + dy*dy);
      if (dist < r + 4 && dist < bestDist) {
        best = n;
        bestDist = dist;
      }
    });
    return best;
  }
}

function showTooltip(node, event) {
  const tip = document.getElementById('sky-tooltip');
  const tags = (node.tags || []).slice(0, 6).join(', ');
  tip.innerHTML = `
    <div class="tip-id">${esc(node.id)}</div>
    <div class="tip-meta">
      brightness ${node.brightness.toFixed(2)} ·
      activated ${node.activation_count}× ·
      drift ${node.drift.toFixed(2)} ·
      ${node.source_type}
    </div>
    <div>${esc(node.core.slice(0, 180))}</div>
    ${tags ? `<div class="tip-meta" style="margin-top:6px">tags: ${esc(tags)}</div>` : ''}
  `;
  // Position next to cursor, but keep on screen
  const stage = document.getElementById('sky-stage').getBoundingClientRect();
  const x = event.clientX - stage.left + 14;
  const y = event.clientY - stage.top + 14;
  tip.style.left = Math.min(x, stage.width - 340) + 'px';
  tip.style.top = Math.min(y, stage.height - 160) + 'px';
  tip.classList.add('show');
}

function hideTooltip() {
  document.getElementById('sky-tooltip').classList.remove('show');
}

function showSkyDetail(node) {
  const det = document.getElementById('sky-detail');
  const content = document.getElementById('sky-detail-content');
  const faces = node.faces || {};
  const faceHtml = Object.keys(faces).map(name => {
    return `<div class="face"><div class="face-name">${name}</div>${esc(faces[name].slice(0, 280))}</div>`;
  }).join('');
  content.innerHTML = `
    <h3>${esc(node.id)}</h3>
    <div class="field"><b>brightness:</b> ${node.brightness.toFixed(3)}</div>
    <div class="field"><b>drift:</b> ${node.drift.toFixed(3)} ·
      <b>activated:</b> ${node.activation_count}× ·
      <b>links:</b> ${(node.links_out||[]).length}</div>
    <div class="field"><b>source:</b> ${node.source_type}</div>
    <div class="field"><b>tags:</b> ${esc((node.tags||[]).join(', '))}</div>
    <div class="core">${esc(node.core)}</div>
    ${faceHtml ? '<div class="field"><b>faces:</b></div>' + faceHtml : ''}
  `;
  det.classList.add('show');
}

function closeSkyDetail() {
  document.getElementById('sky-detail').classList.remove('show');
  skyState.selected = null;
}

function resetSkyView() {
  if (typeof d3 === 'undefined') return;
  // Reheat the simulation and recenter
  if (skyState.simulation) {
    const canvas = document.getElementById('sky-canvas');
    const w = canvas.clientWidth, h = canvas.clientHeight;
    skyState.simulation.force('center', d3.forceCenter(w / 2, h / 2));
    skyState.simulation.alpha(0.8).restart();
    skyState.transform = d3.zoomIdentity;
    d3.select(canvas).call(d3.zoom().transform, d3.zoomIdentity);
  }
}

// Dictionary tab — paste a dictionary, see word connections, compare languages
async function ingestDictionary(which) {
  const lang = document.getElementById(`dict-${which}-language`).value.trim() || 'unknown';
  const text = document.getElementById(`dict-${which}-text`).value;
  const status = document.getElementById(`dict-${which}-status`);
  if (!text.trim()) { status.textContent = 'no text'; return; }
  status.textContent = 'ingesting...';
  document.getElementById(`dict-${which}-btn`).disabled = true;
  try {
    const res = await fetch('/dictionary/ingest', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        text,
        language: lang,
        session_id: `dictionary:${lang}`,
      }),
    });
    const data = await res.json();
    status.textContent = `✓ ${data.ingested} entries, ${data.links_created} links` +
      (data.notes ? ` (${data.notes})` : '');
  } catch(e) {
    status.textContent = 'error: ' + e.message;
  }
  document.getElementById(`dict-${which}-btn`).disabled = false;
}

async function compareDictionaries() {
  const langA = document.getElementById('dict-a-language').value.trim() || 'english';
  const langB = document.getElementById('dict-b-language').value.trim() || 'spanish';
  const out = document.getElementById('dict-comparison');
  out.innerHTML = '<div style="color:var(--dim);font-size:11px;padding:10px">comparing...</div>';
  try {
    const res = await fetch(
      '/dictionary/compare?session_a=' + encodeURIComponent(`dictionary:${langA}`) +
      '&session_b=' + encodeURIComponent(`dictionary:${langB}`)
    );
    const data = await res.json();
    renderDictionaryComparison(data, langA, langB);
  } catch(e) {
    out.innerHTML = '<div style="color:var(--warn)">error: ' + esc(e.message) + '</div>';
  }
}

function renderDictionaryComparison(data, langA, langB) {
  const out = document.getElementById('dict-comparison');
  let html = '';
  // Top stats
  html += '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:14px">';
  html += `<div style="background:var(--surface);padding:10px 14px;border-radius:6px;border-left:3px solid var(--accent)">` +
          `<div style="font-size:10px;color:var(--dim);text-transform:uppercase">${esc(langA)}</div>` +
          `<div style="font-size:24px;color:var(--accent);font-weight:bold">${data.size_a}</div>` +
          `<div style="font-size:10px;color:var(--dim)">entries</div></div>`;
  html += `<div style="background:var(--surface);padding:10px 14px;border-radius:6px;border-left:3px solid var(--accent2)">` +
          `<div style="font-size:10px;color:var(--dim);text-transform:uppercase">${esc(langB)}</div>` +
          `<div style="font-size:24px;color:var(--accent2);font-weight:bold">${data.size_b}</div>` +
          `<div style="font-size:10px;color:var(--dim)">entries</div></div>`;
  html += `<div style="background:var(--surface);padding:10px 14px;border-radius:6px;border-left:3px solid var(--warn)">` +
          `<div style="font-size:10px;color:var(--dim);text-transform:uppercase">Shared headwords</div>` +
          `<div style="font-size:24px;color:var(--warn);font-weight:bold">${data.n_shared}</div>` +
          `<div style="font-size:10px;color:var(--dim)">literal matches</div></div>`;
  html += '</div>';

  // Shared headwords list
  if ((data.shared_headwords || []).length > 0) {
    html += '<div style="background:var(--surface);padding:10px 14px;border-radius:6px;margin-bottom:14px">';
    html += '<div style="font-size:11px;color:var(--accent);font-weight:bold;margin-bottom:6px">Headwords present in both:</div>';
    html += '<div style="font-size:11px;color:var(--text);font-family:monospace">' +
            data.shared_headwords.slice(0, 30).map(esc).join(' · ') + '</div>';
    html += '</div>';
  }

  // Structural divergence on shared words
  if ((data.structural_divergence || []).length > 0) {
    html += '<div style="background:var(--surface2);padding:12px 16px;border-radius:6px;margin-bottom:14px">';
    html += '<div style="font-size:12px;color:var(--accent2);font-weight:bold;margin-bottom:6px">Structural divergence (most divergent first)</div>';
    html += '<div style="font-size:10px;color:var(--dim);margin-bottom:8px">For words that appear in both languages, how much do their tag neighborhoods differ? Low Jaccard = the same word has very different connections in each language.</div>';
    html += '<table style="width:100%;font-size:11px;border-collapse:collapse">';
    html += '<tr style="color:var(--dim);border-bottom:1px solid var(--border)">' +
            '<th style="text-align:left;padding:4px 6px">word</th>' +
            '<th style="text-align:right;padding:4px 6px">jaccard</th>' +
            `<th style="text-align:left;padding:4px 6px;color:var(--accent)">${esc(langA)} only</th>` +
            `<th style="text-align:left;padding:4px 6px;color:var(--accent2)">${esc(langB)} only</th>` +
            '</tr>';
    data.structural_divergence.slice(0, 12).forEach(d => {
      html += '<tr style="border-bottom:1px solid #222">' +
              `<td style="padding:4px 6px;color:var(--text);font-weight:bold">${esc(d.word)}</td>` +
              `<td style="padding:4px 6px;text-align:right">${d.tag_jaccard.toFixed(2)}</td>` +
              `<td style="padding:4px 6px;color:var(--accent);font-family:monospace">${esc((d.tags_a_only || []).join(' '))}</td>` +
              `<td style="padding:4px 6px;color:var(--accent2);font-family:monospace">${esc((d.tags_b_only || []).join(' '))}</td>` +
              '</tr>';
    });
    html += '</table></div>';
  }

  // Cross-definition matches
  if ((data.cross_definition_matches || []).length > 0) {
    html += '<div style="background:var(--surface2);padding:12px 16px;border-radius:6px;margin-bottom:14px">';
    html += '<div style="font-size:12px;color:var(--accent2);font-weight:bold;margin-bottom:6px">Cross-definition matches (likely translations)</div>';
    html += '<div style="font-size:10px;color:var(--dim);margin-bottom:8px">Words whose definitions share content even though the headwords differ. Strong matches are likely translations of each other.</div>';
    html += '<table style="width:100%;font-size:11px;border-collapse:collapse">';
    html += '<tr style="color:var(--dim);border-bottom:1px solid var(--border)">' +
            `<th style="text-align:left;padding:4px 6px;color:var(--accent)">${esc(langA)}</th>` +
            `<th style="text-align:left;padding:4px 6px;color:var(--accent2)">${esc(langB)}</th>` +
            '<th style="text-align:right;padding:4px 6px">jaccard</th>' +
            '</tr>';
    data.cross_definition_matches.slice(0, 12).forEach(m => {
      html += '<tr style="border-bottom:1px solid #222">' +
              `<td style="padding:4px 6px;color:var(--accent);font-weight:bold">${esc(m.word_a)}</td>` +
              `<td style="padding:4px 6px;color:var(--accent2);font-weight:bold">${esc(m.word_b)}</td>` +
              `<td style="padding:4px 6px;text-align:right">${m.tag_jaccard.toFixed(2)}</td>` +
              '</tr>';
    });
    html += '</table></div>';
  }

  if (!data.shared_headwords?.length && !data.cross_definition_matches?.length) {
    html += '<div style="color:var(--dim);font-size:12px;padding:14px;background:var(--surface);border-radius:4px">' +
            'No matches found. Make sure both dictionaries are ingested and have overlapping content.</div>';
  }

  out.innerHTML = html;
}

function viewDictionaryInSky(which) {
  const lang = document.getElementById(`dict-${which}-language`).value.trim() || 'english';
  // Switch to Sky View tab and trigger a load
  document.querySelector('.tab[data-panel="sky-panel"]').click();
  // The Sky View doesn't currently filter by session in its UI, but
  // its loadSky() shows everything; we just trust that the user can spot
  // the recently-added cluster. Future improvement: add a session filter.
  alert(`Sky View now shows all memories. Look for the dense cluster of '${lang}' dictionary entries (they share the '${lang}' tag).`);
}

async function resetDictionaries() {
  const langA = document.getElementById('dict-a-language').value.trim() || 'english';
  const langB = document.getElementById('dict-b-language').value.trim() || 'spanish';
  try {
    await fetch(`/sessions/dictionary:${encodeURIComponent(langA)}/clear`, {method: 'POST'});
    await fetch(`/sessions/dictionary:${encodeURIComponent(langB)}/clear`, {method: 'POST'});
    document.getElementById('dict-a-status').textContent = 'cleared';
    document.getElementById('dict-b-status').textContent = 'cleared';
    document.getElementById('dict-comparison').innerHTML = '';
  } catch(e) {
    document.getElementById('dict-a-status').textContent = 'error: ' + e.message;
  }
}

// Analysis: §8.1 follow-up — compare LLM vs heuristic scorers side by side
async function loadTrajectoryComparison() {
  const status = document.getElementById('traj-status');
  status.textContent = 'comparing...';
  document.getElementById('traj-compare').disabled = true;
  try {
    const res = await fetch('/trajectory-compare');
    if (!res.ok) {
      status.textContent = 'error: HTTP ' + res.status;
      return;
    }
    const data = await res.json();
    renderTrajectoryComparison(data);
    const llmN = data.llm.n_memories_with_trajectory;
    const heuN = data.heuristic.n_memories_with_trajectory;
    status.textContent = `done — llm: ${llmN}, heuristic: ${heuN}`;
  } catch(e) {
    status.textContent = 'error: ' + e.message;
  }
  document.getElementById('traj-compare').disabled = false;
}

function renderTrajectoryComparison(data) {
  const headline = document.getElementById('traj-headline');
  const tables = document.getElementById('traj-tables');
  document.getElementById('traj-scatter-wrap').style.display = 'none';

  const reports = [
    {label: 'LLM-driven', key: 'llm', report: data.llm},
    {label: 'Heuristic', key: 'heuristic', report: data.heuristic},
    {label: 'All', key: 'all', report: data.all},
  ];

  let html = '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px">';
  reports.forEach(({label, report}) => {
    const rho = report.correlation || 0;
    let color = 'var(--accent2)';
    if (Math.abs(rho) < 0.2) color = 'var(--warn)';
    else if (rho < 0) color = '#f06292';

    html += '<div style="background:var(--bg);padding:12px 14px;border-radius:6px;border:1px solid var(--border)">';
    html += '<div style="font-size:11px;color:var(--dim);text-transform:uppercase;letter-spacing:0.5px">' + label + '</div>';
    html += '<div style="font-size:24px;color:' + color + ';font-weight:bold;line-height:1.1;margin-top:4px">' +
            (rho >= 0 ? '+' : '') + rho.toFixed(3) + '</div>';
    html += '<div style="font-size:10px;color:var(--dim);margin-top:6px">Spearman ρ</div>';
    html += '<div style="font-size:11px;color:var(--text);margin-top:8px">' +
            'n = <b>' + report.n_memories_with_trajectory + '</b><br>' +
            'mean pred = <b>' + report.mean_trajectory.toFixed(2) + '</b><br>' +
            'mean actual = <b>' + report.mean_activation_count.toFixed(2) + '</b>' +
            '</div>';
    if (report.notes) {
      html += '<div style="font-size:10px;color:var(--dim);margin-top:8px;font-style:italic">' +
              esc(report.notes) + '</div>';
    }
    html += '</div>';
  });
  html += '</div>';

  // Verdict
  const llmRho = data.llm.correlation || 0;
  const heuRho = data.heuristic.correlation || 0;
  const llmN = data.llm.n_memories_with_trajectory;
  const heuN = data.heuristic.n_memories_with_trajectory;
  let verdict = '';
  if (llmN < 5 && heuN < 5) {
    verdict = 'Not enough data yet on either side. Run a longer dialogue.';
  } else if (llmN < 5) {
    verdict = 'Not enough LLM-scored memories yet. Restart the server with PEP_OLLAMA_SUPPORT_CALLS=1 and run a dialogue.';
  } else if (heuN < 5) {
    verdict = 'Not enough heuristic-scored memories. (Most existing memories should be heuristic — odd that there are none.)';
  } else if (Math.abs(llmRho) > Math.abs(heuRho) + 0.1) {
    verdict = 'LLM-driven trajectory scoring correlates meaningfully better with actual reactivation than the heuristic. The §8.1 finding is partially reversed: the heuristic is the limitation, not the design.';
  } else if (Math.abs(heuRho) > Math.abs(llmRho) + 0.1) {
    verdict = 'Heuristic actually does better than the LLM. Suggests trajectory scoring is fundamentally hard to do at storage time, regardless of how smart the scorer is.';
  } else {
    verdict = 'No meaningful difference between LLM and heuristic. The §8.1 finding holds: trajectory scoring as currently formulated is not doing predictive work, regardless of which scorer runs.';
  }
  html += '<div style="margin-top:14px;padding:10px 14px;background:var(--surface2);border-radius:4px;font-size:12px;color:var(--text);line-height:1.5">';
  html += '<b style="color:var(--accent2)">Verdict:</b> ' + esc(verdict);
  html += '</div>';

  headline.style.display = 'block';
  headline.innerHTML = html;
  tables.style.display = 'none';
}

// Analysis: trajectory score validation (§8.1)
async function loadTrajectoryAnalysis() {
  const status = document.getElementById('traj-status');
  status.textContent = 'running...';
  document.getElementById('traj-load').disabled = true;
  try {
    const res = await fetch('/trajectory-validate');
    if (!res.ok) {
      status.textContent = 'error: HTTP ' + res.status;
      return;
    }
    const data = await res.json();
    renderTrajectoryAnalysis(data);
    status.textContent = 'done — ' + data.n_memories_with_trajectory + ' memories analyzed';
  } catch(e) {
    status.textContent = 'error: ' + e.message;
  }
  document.getElementById('traj-load').disabled = false;
}

function renderTrajectoryAnalysis(data) {
  // Headline ρ
  const headline = document.getElementById('traj-headline');
  const rho = data.correlation || 0;
  let interpretation;
  if (rho > 0.5) interpretation = 'strong positive: trajectory predicts reactivation well';
  else if (rho > 0.2) interpretation = 'mild positive: some predictive power';
  else if (rho > -0.2) interpretation = 'essentially uncorrelated: trajectory is not doing predictive work';
  else if (rho > -0.5) interpretation = 'mild negative: predicts the opposite of reality';
  else interpretation = 'strong negative: alarming — actively wrong';

  let rhoColor = 'var(--accent2)';
  if (Math.abs(rho) < 0.2) rhoColor = 'var(--warn)';
  else if (rho < 0) rhoColor = '#f06292';

  headline.style.display = 'block';
  headline.innerHTML =
    '<div style="font-size:11px;color:var(--dim)">Spearman ρ (predicted vs actual)</div>' +
    '<div style="font-size:32px;color:' + rhoColor + ';font-weight:bold;line-height:1.1">' +
    (rho >= 0 ? '+' : '') + rho.toFixed(3) + '</div>' +
    '<div style="font-size:11px;color:var(--dim);margin-top:2px">' + interpretation + '</div>' +
    '<div style="font-size:11px;color:var(--dim);margin-top:8px">' +
    'mean predicted: <b style="color:var(--text)">' + (data.mean_trajectory||0).toFixed(2) + '</b> · ' +
    'mean actual: <b style="color:var(--text)">' + (data.mean_activation_count||0).toFixed(2) + '</b> · ' +
    'n: <b style="color:var(--text)">' + data.correlation_n + '</b>' +
    '</div>';

  // Scatter plot
  if (typeof d3 === 'undefined') return;
  const wrap = document.getElementById('traj-scatter-wrap');
  wrap.style.display = 'block';
  const svg = document.getElementById('traj-scatter');
  svg.innerHTML = '';

  // Build the dataset by joining top_predicted and top_actually_used (the
  // /trajectory-validate endpoint doesn't return all points; it only sends
  // the headline numbers + top-5 lists). For a richer scatter we hit
  // /memories and use future_use.trajectory_at_storage + activation_count.
  fetch('/memories').then(r => r.json()).then(memories => {
    const points = [];
    memories.forEach(m => {
      const fu = m.future_use || {};
      const pred = fu.trajectory_at_storage;
      if (pred === undefined || pred === null) return;
      points.push({
        id: m.id,
        x: parseFloat(pred),
        y: m.activation_count || 0,
        source: m.source_type || 'conversation',
      });
    });
    drawTrajectoryScatter(svg, points, data);
  });

  // Top tables
  const tables = document.getElementById('traj-tables');
  tables.style.display = 'block';
  let html = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">';
  html += renderTrajectoryTable('Top 5 by predicted trajectory', data.top_predicted || []);
  html += renderTrajectoryTable('Top 5 by actual activation', data.top_actually_used || []);
  html += '</div>';
  tables.innerHTML = html;
}

function renderTrajectoryTable(title, rows) {
  let h = '<div style="background:var(--bg);padding:10px 14px;border-radius:4px">';
  h += '<div style="font-size:11px;color:var(--accent2);font-weight:bold;margin-bottom:6px">' + title + '</div>';
  h += '<table style="width:100%;font-size:11px">';
  h += '<tr style="color:var(--dim)"><th style="text-align:left;padding:2px 4px">id</th>' +
       '<th style="text-align:right;padding:2px 4px">pred</th>' +
       '<th style="text-align:right;padding:2px 4px">actual</th></tr>';
  rows.forEach(r => {
    h += '<tr style="border-top:1px solid var(--border)">' +
         '<td style="padding:2px 4px;color:var(--text);font-family:monospace">' + r.id + '</td>' +
         '<td style="padding:2px 4px;text-align:right">' + (r.predicted_trajectory || 0).toFixed(2) + '</td>' +
         '<td style="padding:2px 4px;text-align:right">' + r.actual_count + '</td>' +
         '</tr>';
  });
  h += '</table></div>';
  return h;
}

function drawTrajectoryScatter(svg, points, summary) {
  while (svg.firstChild) svg.removeChild(svg.firstChild);
  if (points.length === 0) return;

  const W = 600, H = 360;
  const margin = {top: 20, right: 20, bottom: 50, left: 60};
  const innerW = W - margin.left - margin.right;
  const innerH = H - margin.top - margin.bottom;

  const maxY = Math.max(1, ...points.map(p => p.y));
  const xScale = d3.scaleLinear().domain([0, 1]).range([margin.left, margin.left + innerW]);
  const yScale = d3.scaleLinear().domain([0, maxY * 1.05]).range([margin.top + innerH, margin.top]);

  // Axes
  const axisStyle = (el) => {
    el.setAttribute('stroke', '#555');
    el.setAttribute('stroke-width', '1');
  };
  // X axis
  const xAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
  xAxis.setAttribute('x1', margin.left);
  xAxis.setAttribute('y1', margin.top + innerH);
  xAxis.setAttribute('x2', margin.left + innerW);
  xAxis.setAttribute('y2', margin.top + innerH);
  axisStyle(xAxis);
  svg.appendChild(xAxis);
  // Y axis
  const yAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
  yAxis.setAttribute('x1', margin.left);
  yAxis.setAttribute('y1', margin.top);
  yAxis.setAttribute('x2', margin.left);
  yAxis.setAttribute('y2', margin.top + innerH);
  axisStyle(yAxis);
  svg.appendChild(yAxis);

  // X tick labels (0, 0.25, 0.5, 0.75, 1.0)
  [0, 0.25, 0.5, 0.75, 1.0].forEach(v => {
    const t = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    t.setAttribute('x', xScale(v));
    t.setAttribute('y', margin.top + innerH + 16);
    t.setAttribute('text-anchor', 'middle');
    t.setAttribute('fill', '#888');
    t.setAttribute('font-size', '10');
    t.setAttribute('font-family', 'monospace');
    t.textContent = v.toFixed(2);
    svg.appendChild(t);
  });
  // Y tick labels
  const yTicks = [0, Math.round(maxY * 0.25), Math.round(maxY * 0.5), Math.round(maxY * 0.75), maxY];
  yTicks.forEach(v => {
    const t = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    t.setAttribute('x', margin.left - 8);
    t.setAttribute('y', yScale(v) + 3);
    t.setAttribute('text-anchor', 'end');
    t.setAttribute('fill', '#888');
    t.setAttribute('font-size', '10');
    t.setAttribute('font-family', 'monospace');
    t.textContent = v;
    svg.appendChild(t);
  });

  // Axis labels
  const xLabel = document.createElementNS('http://www.w3.org/2000/svg', 'text');
  xLabel.setAttribute('x', margin.left + innerW / 2);
  xLabel.setAttribute('y', H - 10);
  xLabel.setAttribute('text-anchor', 'middle');
  xLabel.setAttribute('fill', '#888');
  xLabel.setAttribute('font-size', '11');
  xLabel.textContent = 'predicted trajectory_at_storage →';
  svg.appendChild(xLabel);

  const yLabel = document.createElementNS('http://www.w3.org/2000/svg', 'text');
  yLabel.setAttribute('x', -(margin.top + innerH / 2));
  yLabel.setAttribute('y', 16);
  yLabel.setAttribute('text-anchor', 'middle');
  yLabel.setAttribute('fill', '#888');
  yLabel.setAttribute('font-size', '11');
  yLabel.setAttribute('transform', 'rotate(-90)');
  yLabel.textContent = 'actual activation_count →';
  svg.appendChild(yLabel);

  // Diagonal "perfect prediction" reference line (for visual reference only,
  // mapping x∈[0,1] linearly to y∈[0,maxY])
  const ref = document.createElementNS('http://www.w3.org/2000/svg', 'line');
  ref.setAttribute('x1', xScale(0));
  ref.setAttribute('y1', yScale(0));
  ref.setAttribute('x2', xScale(1));
  ref.setAttribute('y2', yScale(maxY));
  ref.setAttribute('stroke', '#444');
  ref.setAttribute('stroke-dasharray', '4,4');
  ref.setAttribute('stroke-width', '1');
  svg.appendChild(ref);

  // Points
  const colorBySource = {
    conversation: '#4fc3f7',
    summary: '#81c784',
    document: '#ffb74d',
    fact: '#ba68c8',
    abstraction: '#ba68c8',
  };
  // Add small random jitter so overlapping points are visible
  points.forEach(p => {
    const c = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    c.setAttribute('cx', xScale(p.x) + (Math.random() - 0.5) * 4);
    c.setAttribute('cy', yScale(p.y) + (Math.random() - 0.5) * 2);
    c.setAttribute('r', '3');
    c.setAttribute('fill', colorBySource[p.source] || '#4fc3f7');
    c.setAttribute('fill-opacity', '0.55');
    c.setAttribute('stroke', 'none');
    const title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
    title.textContent = p.id + ' — pred=' + p.x.toFixed(2) + ', actual=' + p.y;
    c.appendChild(title);
    svg.appendChild(c);
  });

  // Annotation: ρ in the corner
  const annot = document.createElementNS('http://www.w3.org/2000/svg', 'text');
  annot.setAttribute('x', margin.left + innerW - 10);
  annot.setAttribute('y', margin.top + 14);
  annot.setAttribute('text-anchor', 'end');
  annot.setAttribute('fill', summary.correlation > 0.2 ? '#81c784' :
                              summary.correlation < -0.2 ? '#f06292' : '#ffb74d');
  annot.setAttribute('font-size', '13');
  annot.setAttribute('font-weight', 'bold');
  annot.setAttribute('font-family', 'monospace');
  annot.textContent = 'ρ = ' + (summary.correlation >= 0 ? '+' : '') + summary.correlation.toFixed(3);
  svg.appendChild(annot);

  const sub = document.createElementNS('http://www.w3.org/2000/svg', 'text');
  sub.setAttribute('x', margin.left + innerW - 10);
  sub.setAttribute('y', margin.top + 28);
  sub.setAttribute('text-anchor', 'end');
  sub.setAttribute('fill', '#888');
  sub.setAttribute('font-size', '10');
  sub.setAttribute('font-family', 'monospace');
  sub.textContent = 'n = ' + points.length + ' memories';
  svg.appendChild(sub);
}

// Demo Runner
const DEMO_SESSION = 'demo';
let demoRunning = false;
let demoStopRequested = false;
let demoScenarios = [];

async function loadDemoList() {
  try {
    const res = await fetch('/demos');
    demoScenarios = await res.json();
    const sel = document.getElementById('demo-scenario');
    sel.innerHTML = '';
    demoScenarios.forEach(s => {
      const opt = document.createElement('option');
      opt.value = s.id;
      opt.textContent = `${s.title} (${s.step_count} turns)`;
      sel.appendChild(opt);
    });
    updateDemoSummary();
    sel.addEventListener('change', updateDemoSummary);
  } catch(e) {
    console.error('failed to load demos', e);
  }
}

function updateDemoSummary() {
  const id = document.getElementById('demo-scenario').value;
  const s = demoScenarios.find(x => x.id === id);
  document.getElementById('demo-summary').textContent = s ? s.summary : '';
  document.getElementById('demo-moral').classList.remove('show');
}

async function startDemo() {
  if (demoRunning) return;
  const id = document.getElementById('demo-scenario').value;
  if (!id) return;

  // Force-enable compare mode and switch to the demo session
  document.getElementById('compare-toggle').checked = true;
  document.getElementById('session-id').value = DEMO_SESSION;

  // Hide the welcome card so the demo has the screen
  const wc = document.getElementById('welcome-card');
  if (wc) wc.style.display = 'none';

  // Clear previous chat output
  const msgs = document.getElementById('chat-messages');
  // Keep the demo runner panel, remove everything below it
  Array.from(msgs.querySelectorAll('.msg')).forEach(el => el.remove());

  // Fetch the full scenario
  let scenario;
  try {
    const res = await fetch('/demos/' + id);
    scenario = await res.json();
  } catch(e) {
    document.getElementById('demo-progress').textContent = 'failed to load scenario';
    return;
  }

  demoRunning = true;
  demoStopRequested = false;
  document.getElementById('demo-start').disabled = true;
  document.getElementById('demo-stop').disabled = false;
  document.getElementById('demo-moral').classList.remove('show');

  const speed = parseInt(document.getElementById('demo-speed').value, 10);
  const steps = scenario.steps || [];
  let stoppedEarly = false;

  for (let i = 0; i < steps.length; i++) {
    if (demoStopRequested) { stoppedEarly = true; break; }
    document.getElementById('demo-progress').textContent =
      `▶ step ${i+1} of ${steps.length}`;

    const step = steps[i];
    appendMsg('user', step.text);
    if (step.note) {
      const noteEl = document.createElement('div');
      noteEl.className = 'step-note';
      noteEl.textContent = '↳ ' + step.note;
      msgs.lastElementChild.appendChild(noteEl);
    }

    try {
      const res = await fetch('/chat/compare', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({text: step.text, session_id: DEMO_SESSION})
      });
      const data = await res.json();
      appendCompareMsg(data);
    } catch(e) {
      appendMsg('assistant', '[demo error: ' + e.message + ']');
      break;
    }

    // Pause between turns so the user can read
    if (i < steps.length - 1) {
      await sleep(speed);
    }
  }

  demoRunning = false;
  document.getElementById('demo-start').disabled = false;
  document.getElementById('demo-stop').disabled = true;
  document.getElementById('demo-progress').textContent =
    stoppedEarly ? 'stopped' : `✓ done (${steps.length} turns)`;

  if (!stoppedEarly && scenario.moral) {
    const moralEl = document.getElementById('demo-moral');
    moralEl.innerHTML = '<b>What just happened:</b> ' + esc(scenario.moral);
    moralEl.classList.add('show');
  }
}

function stopDemo() {
  if (!demoRunning) return;
  demoStopRequested = true;
  document.getElementById('demo-progress').textContent = 'stopping...';
}

async function resetDemoMemory() {
  if (demoRunning) return;
  try {
    const res = await fetch('/sessions/' + DEMO_SESSION + '/clear', {method: 'POST'});
    const data = await res.json();
    document.getElementById('demo-progress').textContent =
      `cleared demo memory (${data.memories_deleted} memories, ${data.runs_deleted} runs)`;
    // Wipe the on-screen chat too
    Array.from(document.getElementById('chat-messages').querySelectorAll('.msg')).forEach(el => el.remove());
    document.getElementById('demo-moral').classList.remove('show');
  } catch(e) {
    document.getElementById('demo-progress').textContent = 'reset failed: ' + e.message;
  }
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// Boot the demo list on page load
loadDemoList();

// ─── Keyboard shortcuts ─────────────────────────────────────────────────
// 1-7: switch tabs (only when no input is focused)
// Cmd/Ctrl+Enter: send chat / start demo / start dialogue depending on tab
// Esc: stop running things (demo or dialogue)
// ?: show shortcut help overlay
const TAB_ORDER = ['chat-panel', 'sky-panel', 'dialogue-panel', 'dictionary-panel',
                   'categories-panel', 'analysis-panel', 'runs-panel', 'ingest-panel', 'bench-panel'];

function isTypingTarget(el) {
  if (!el) return false;
  const tag = (el.tagName || '').toLowerCase();
  return tag === 'input' || tag === 'textarea' || tag === 'select' || el.isContentEditable;
}

document.addEventListener('keydown', (e) => {
  // ? — help overlay (works even when typing if shift is held)
  if (e.key === '?' && !isTypingTarget(e.target)) {
    e.preventDefault();
    toggleShortcutHelp();
    return;
  }

  // Esc — stop running things
  if (e.key === 'Escape') {
    if (dlgRunning) { stopDialogue(); return; }
    if (typeof demoRunning !== 'undefined' && demoRunning) { stopDemo(); return; }
    // Also close any open overlays
    document.getElementById('setup-modal').classList.remove('open');
    const help = document.getElementById('shortcut-help');
    if (help) help.style.display = 'none';
    return;
  }

  // Cmd/Ctrl+Enter — context-sensitive submit
  if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
    e.preventDefault();
    const activePanel = document.querySelector('.panel.active');
    if (!activePanel) return;
    const panelId = activePanel.id;
    if (panelId === 'chat-panel') {
      sendMsg();
    } else if (panelId === 'dialogue-panel') {
      if (!dlgRunning) startDialogue();
    } else if (panelId === 'ingest-panel') {
      doIngest();
    } else if (panelId === 'bench-panel') {
      runBench();
    }
    return;
  }

  // 1-7 — switch tabs (only when not typing in an input)
  if (!isTypingTarget(e.target) && !e.metaKey && !e.ctrlKey && !e.altKey) {
    const idx = parseInt(e.key, 10);
    if (idx >= 1 && idx <= TAB_ORDER.length) {
      const targetPanelId = TAB_ORDER[idx - 1];
      const targetTab = document.querySelector(`.tab[data-panel="${targetPanelId}"]`);
      if (targetTab) {
        e.preventDefault();
        targetTab.click();
      }
    }
  }
});

function toggleShortcutHelp() {
  let help = document.getElementById('shortcut-help');
  if (!help) {
    help = document.createElement('div');
    help.id = 'shortcut-help';
    help.style.cssText =
      'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);' +
      'background:var(--surface2);border:1px solid var(--accent);border-radius:8px;' +
      'padding:24px 30px;font-size:13px;line-height:1.8;color:var(--text);' +
      'z-index:200;box-shadow:0 8px 32px rgba(0,0,0,0.6);min-width:340px';
    help.innerHTML =
      '<h2 style="color:var(--accent);font-size:14px;margin-bottom:12px">Keyboard shortcuts</h2>' +
      '<table style="font-size:12px">' +
      '<tr><td style="padding:3px 12px 3px 0"><kbd style="background:var(--bg);padding:2px 6px;border-radius:3px;border:1px solid var(--border)">1</kbd>–<kbd style="background:var(--bg);padding:2px 6px;border-radius:3px;border:1px solid var(--border)">7</kbd></td><td>Switch tabs</td></tr>' +
      '<tr><td style="padding:3px 12px 3px 0"><kbd style="background:var(--bg);padding:2px 6px;border-radius:3px;border:1px solid var(--border)">⌘</kbd>+<kbd style="background:var(--bg);padding:2px 6px;border-radius:3px;border:1px solid var(--border)">↵</kbd></td><td>Send / Start (context-aware)</td></tr>' +
      '<tr><td style="padding:3px 12px 3px 0"><kbd style="background:var(--bg);padding:2px 6px;border-radius:3px;border:1px solid var(--border)">Esc</kbd></td><td>Stop running demo or dialogue</td></tr>' +
      '<tr><td style="padding:3px 12px 3px 0"><kbd style="background:var(--bg);padding:2px 6px;border-radius:3px;border:1px solid var(--border)">?</kbd></td><td>Toggle this help</td></tr>' +
      '</table>' +
      '<div style="margin-top:12px;font-size:10px;color:var(--dim)">' +
      'Tab order: Chat · Sky View · Dialogue · Categories · Runs · Ingest · Benchmarks' +
      '</div>' +
      '<button onclick="document.getElementById(\\'shortcut-help\\').style.display=\\'none\\'" ' +
      'style="margin-top:14px;background:var(--accent);color:#000;border:none;border-radius:4px;' +
      'padding:6px 16px;font-family:inherit;font-size:12px;cursor:pointer;font-weight:bold">close (Esc)</button>';
    document.body.appendChild(help);
  }
  help.style.display = (help.style.display === 'none' || !help.style.display) ? 'block' : 'none';
}

// Dialogue — N PEP instances talking to each other (round-robin)
let dlgPersonas = {};
let dlgRunning = false;
let dlgController = null;       // AbortController for the in-flight fetch
let dlgTranscript = [];         // turns collected for save
let dlgMeta = {};               // opening, personas, etc. for save
// State coupling history: per agent name, an array of {turn, ...state vars}
let dlgStateHistory = {};       // populated dynamically based on selected persona set
let dlgAgentNames = [];         // ['Alice', 'Bob', ...] for the active dialogue
let dlgAgentIndex = {};         // {name: index} for color lookup

const STATE_VARS = ['urgency', 'uncertainty', 'novelty', 'conflict', 'exploration', 'stability_need'];
const AGENT_COLORS = ['#4fc3f7', '#81c784', '#ffb74d', '#ba68c8', '#f06292'];

async function loadDialoguePersonas() {
  if (Object.keys(dlgPersonas).length > 0) return;  // already loaded
  try {
    const res = await fetch('/dialogue/personas');
    dlgPersonas = await res.json();
    const sel = document.getElementById('dlg-personas');
    sel.innerHTML = '';
    Object.keys(dlgPersonas).forEach(name => {
      const set = dlgPersonas[name];
      const opt = document.createElement('option');
      opt.value = name;
      opt.textContent = name + ' (' + set.count + ' agent' + (set.count > 1 ? 's' : '') + ')';
      sel.appendChild(opt);
    });
    sel.addEventListener('change', updateDlgPersonaDisplay);
    updateDlgPersonaDisplay();
  } catch(e) {
    document.getElementById('dlg-status').textContent = 'failed to load personas: ' + e.message;
  }
}

function updateDlgPersonaDisplay() {
  const sel = document.getElementById('dlg-personas');
  const choice = sel.value;
  const display = document.getElementById('dlg-personas-display');
  if (!choice || !dlgPersonas[choice]) { display.innerHTML = ''; return; }
  const set = dlgPersonas[choice];
  const lines = (set.agents || []).map((a, i) => {
    const color = AGENT_COLORS[i] || '#888';
    return `<b style="color:${color}">${esc(a.name)}:</b> ${esc(a.persona)}`;
  });
  display.innerHTML = lines.join('<br>');
}

async function startDialogue() {
  if (dlgRunning) return;
  const personas = document.getElementById('dlg-personas').value;
  const turns = parseInt(document.getElementById('dlg-turns').value, 10) || 30;
  const opening = document.getElementById('dlg-opening').value.trim() || 'Hello';
  const topic = document.getElementById('dlg-topic').value.trim();
  const autoContinue = document.getElementById('dlg-auto').checked;

  const transcript = document.getElementById('dlg-transcript');
  transcript.innerHTML = '';
  dlgTranscript = [];
  dlgMeta = {opening, personas, turns, started: new Date().toISOString()};

  // Set up agent name list and per-agent state history based on the persona set
  const set = dlgPersonas[personas] || {};
  dlgAgentNames = (set.agents || []).map(a => a.name);
  dlgAgentIndex = {};
  dlgStateHistory = {};
  dlgAgentNames.forEach((name, i) => {
    dlgAgentIndex[name] = i;
    dlgStateHistory[name] = [];
  });

  // Hide chart until first turn arrives
  document.getElementById('dlg-state-chart').style.display = 'none';
  document.getElementById('dlg-state-grid').innerHTML = '';

  // Show the opening line
  const openingDiv = document.createElement('div');
  openingDiv.className = 'dlg-opening';
  openingDiv.innerHTML = '<b>opening:</b> ' + esc(opening);
  transcript.appendChild(openingDiv);

  dlgRunning = true;
  document.getElementById('dlg-start').disabled = true;
  document.getElementById('dlg-stop').disabled = false;
  document.getElementById('dlg-save').disabled = true;
  document.getElementById('dlg-status').textContent =
    'running... (each turn takes a few seconds with local model)';

  dlgController = new AbortController();
  try {
    const res = await fetch('/dialogue/stream', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({opening, topic, turns, personas, fresh: true, auto_continue: autoContinue}),
      signal: dlgController.signal,
    });
    if (!res.ok || !res.body) {
      document.getElementById('dlg-status').textContent = 'request failed: HTTP ' + res.status;
      dlgRunning = false;
      document.getElementById('dlg-start').disabled = false;
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const {done, value} = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, {stream: true});

      let idx;
      while ((idx = buffer.indexOf('\\n\\n')) >= 0) {
        const block = buffer.slice(0, idx);
        buffer = buffer.slice(idx + 2);

        let eventName = 'message';
        let dataLine = '';
        block.split('\\n').forEach(line => {
          if (line.startsWith('event: ')) eventName = line.slice(7).trim();
          else if (line.startsWith('data: ')) dataLine += line.slice(6);
        });
        if (!dataLine) continue;

        let payload;
        try { payload = JSON.parse(dataLine); }
        catch(e) { continue; }

        if (eventName === 'turn') {
          dlgTranscript.push(payload);
          renderDlgTurn(payload);
        } else if (eventName === 'observation') {
          // Multi-agent: listener observed the speaker's message; record
          // their state for the coupling chart
          recordObservationState(payload);
        } else if (eventName === 'opening') {
          // Already rendered above
        } else if (eventName === 'done') {
          document.getElementById('dlg-status').textContent =
            '✓ done (' + payload.total_turns + ' turns). Sky View shows both agents\\' memories.';
          document.getElementById('dlg-coherence-panel').style.display = 'block';
        } else if (eventName === 'stopped') {
          document.getElementById('dlg-status').textContent =
            'stopped after ' + payload.completed_turns + ' turns';
          document.getElementById('dlg-coherence-panel').style.display = 'block';
        } else if (eventName === 'error') {
          document.getElementById('dlg-status').textContent =
            'error: ' + (payload.message || '?');
        }
      }
    }
  } catch(e) {
    if (e.name === 'AbortError') {
      document.getElementById('dlg-status').textContent =
        'stopped (' + dlgTranscript.length + ' turns completed)';
    } else {
      document.getElementById('dlg-status').textContent = 'error: ' + e.message;
    }
  }

  dlgRunning = false;
  dlgController = null;
  document.getElementById('dlg-start').disabled = false;
  document.getElementById('dlg-stop').disabled = true;
  document.getElementById('dlg-save').disabled = dlgTranscript.length === 0;
}

async function stopDialogue() {
  if (!dlgRunning) return;
  document.getElementById('dlg-status').textContent = 'stopping...';
  // Tell the server to stop emitting after the current turn
  try { await fetch('/dialogue/stop', {method: 'POST'}); } catch(e) {}
  // Then abort the in-flight fetch so the JS loop exits
  if (dlgController) { try { dlgController.abort(); } catch(e) {} }
}

function saveDialogueTranscript() {
  if (dlgTranscript.length === 0) return;
  const lines = [];
  lines.push('# PEP Dialogue Transcript');
  lines.push('');
  lines.push('- **Personas:** `' + (dlgMeta.personas || '?') + '`');
  lines.push('- **Started:** ' + (dlgMeta.started || ''));
  lines.push('- **Turns completed:** ' + dlgTranscript.length);
  lines.push('');
  lines.push('**Opening:** ' + (dlgMeta.opening || ''));
  lines.push('');
  lines.push('---');
  lines.push('');
  dlgTranscript.forEach((t, i) => {
    lines.push('## Turn ' + (i+1) + ' — ' + (t.speaker || '?'));
    lines.push('');
    lines.push(t.message || '');
    lines.push('');
    const s = t.state_after || {};
    const stateBits = ['urgency','uncertainty','novelty','conflict','exploration','stability_need']
      .map(k => k + '=' + (s[k] || 0).toFixed(2)).join(' · ');
    lines.push('> _state:_ ' + stateBits);
    lines.push('> _memories: ' + (t.memories_after || 0) +
               '_ · _activated: ' + ((t.activated_memory_ids || []).length) + '_');
    lines.push('');
  });
  const md = lines.join('\\n');
  const blob = new Blob([md], {type: 'text/markdown'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'pep_dialogue_' + (dlgMeta.personas || 'session') + '_' +
    new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-') + '.md';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

async function runDialogueCoherence() {
  const query = document.getElementById('dlg-coherence-query').value.trim();
  const out = document.getElementById('dlg-coherence-results');
  if (!query) { out.textContent = 'enter a query first'; return; }
  out.innerHTML = '<div style="color:var(--dim);font-size:11px">running...</div>';
  try {
    const res = await fetch('/dialogue/coherence?query=' + encodeURIComponent(query));
    if (!res.ok) {
      out.innerHTML = '<div style="color:var(--warn)">error: ' + res.status + '</div>';
      return;
    }
    const data = await res.json();
    let html = '<table style="width:100%;border-collapse:collapse;font-size:12px">';
    html += '<tr style="border-bottom:1px solid var(--border)">' +
            '<th style="text-align:left;padding:6px 8px;color:var(--dim)">scope</th>' +
            '<th style="text-align:right;padding:6px 8px;color:var(--dim)">memories</th>' +
            '<th style="text-align:right;padding:6px 8px;color:var(--dim)">categories</th>' +
            '<th style="text-align:right;padding:6px 8px;color:var(--dim)">in cats</th>' +
            '<th style="text-align:right;padding:6px 8px;color:var(--accent2)">ρ (mean)</th>' +
            '<th style="text-align:right;padding:6px 8px;color:var(--accent2)">ρ (max)</th>' +
            '</tr>';
    const order = ['dialogue:Alice', 'dialogue:Bob', '_combined'];
    const labels = {'dialogue:Alice':'Alice', 'dialogue:Bob':'Bob', '_combined':'Combined'};
    order.forEach(key => {
      const r = data[key];
      if (!r) return;
      html += '<tr style="border-bottom:1px solid #222">' +
              '<td style="padding:6px 8px;color:var(--text);font-weight:bold">' + labels[key] + '</td>' +
              '<td style="padding:6px 8px;text-align:right">' + r.n_memories + '</td>' +
              '<td style="padding:6px 8px;text-align:right">' + r.n_categories + '</td>' +
              '<td style="padding:6px 8px;text-align:right">' + r.n_memories_in_categories + '</td>' +
              '<td style="padding:6px 8px;text-align:right;color:var(--accent2)">' + r.coherence_mean.toFixed(3) + '</td>' +
              '<td style="padding:6px 8px;text-align:right;color:var(--accent2)">' + r.coherence_max.toFixed(3) + '</td>' +
              '</tr>';
    });
    html += '</table>';
    html += '<div style="margin-top:8px;font-size:10px;color:var(--dim)">';
    html += 'If the Combined ρ is higher than either agent alone, the joint memory has more coherent structure than the parts. ';
    html += 'If lower, the agents are organizing their memory in incompatible ways.';
    html += '</div>';
    out.innerHTML = html;
  } catch(e) {
    out.innerHTML = '<div style="color:var(--warn)">error: ' + e.message + '</div>';
  }
}

function renderDlgTurn(payload) {
  const transcript = document.getElementById('dlg-transcript');
  const div = document.createElement('div');
  const speaker = payload.speaker || '?';
  const agentIdx = dlgAgentIndex[speaker] !== undefined ? dlgAgentIndex[speaker] : 0;
  div.className = 'dlg-turn agent-' + agentIdx;

  const state = payload.state_after || {};
  const stateLine =
    'urgency=' + (state.urgency||0).toFixed(2) + ' ' +
    'uncertainty=' + (state.uncertainty||0).toFixed(2) + ' ' +
    'novelty=' + (state.novelty||0).toFixed(2) + ' ' +
    'exploration=' + (state.exploration||0).toFixed(2);

  div.innerHTML =
    '<div class="dlg-name">' + esc(speaker) + '</div>' +
    '<div class="dlg-text">' + esc(payload.message || '') + '</div>' +
    '<div class="dlg-meta">' +
      'memories: ' + (payload.memories_after||0) + ' | ' +
      'activated: ' + ((payload.activated_memory_ids||[]).length) + ' | ' +
      stateLine +
    '</div>';
  transcript.appendChild(div);
  transcript.scrollIntoView({behavior: 'smooth', block: 'end'});

  // Record state for the coupling chart
  if (speaker && dlgStateHistory[speaker] !== undefined) {
    const stateRecord = {turn: dlgStateHistory[speaker].length};
    STATE_VARS.forEach(v => { stateRecord[v] = state[v] || 0; });
    dlgStateHistory[speaker].push(stateRecord);
    renderStateCouplingChart();
  }
}

function recordObservationState(payload) {
  // observation events also carry state_after, so observers' state vectors
  // grow alongside speakers' — that's how the coupling chart shows the
  // listening agents.
  const observer = payload.observer;
  if (!observer || dlgStateHistory[observer] === undefined) return;
  const state = payload.state_after || {};
  const stateRecord = {turn: dlgStateHistory[observer].length};
  STATE_VARS.forEach(v => { stateRecord[v] = state[v] || 0; });
  dlgStateHistory[observer].push(stateRecord);
  renderStateCouplingChart();
}

function renderStateCouplingChart() {
  if (typeof d3 === 'undefined') return;
  const chartContainer = document.getElementById('dlg-state-chart');
  const grid = document.getElementById('dlg-state-grid');
  // Need at least one data point across all agents before showing
  const totalPoints = dlgAgentNames.reduce(
    (sum, name) => sum + (dlgStateHistory[name] || []).length, 0);
  if (totalPoints === 0) return;
  chartContainer.style.display = 'block';

  // Build/refresh the 6 small subplots — one per state variable
  STATE_VARS.forEach((varName) => {
    let cell = document.getElementById('dlg-chart-' + varName);
    if (!cell) {
      cell = document.createElement('div');
      cell.id = 'dlg-chart-' + varName;
      cell.style.cssText = 'background:var(--bg);border-radius:4px;padding:6px 8px';
      cell.innerHTML =
        '<div style="font-size:10px;color:var(--dim);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:2px">' +
        varName + '</div>' +
        '<svg width="100%" height="60" viewBox="0 0 200 60" preserveAspectRatio="none"></svg>';
      grid.appendChild(cell);
    }

    const svg = cell.querySelector('svg');
    svg.innerHTML = '';

    const maxLen = Math.max(
      ...dlgAgentNames.map(name => (dlgStateHistory[name] || []).length),
      1,
    );
    const xScale = d3.scaleLinear().domain([0, Math.max(maxLen - 1, 1)]).range([4, 196]);
    const yScale = d3.scaleLinear().domain([0, 1]).range([56, 4]);

    // Background grid line at y=0.5
    const half = yScale(0.5);
    const gridLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    gridLine.setAttribute('x1', 0);
    gridLine.setAttribute('y1', half);
    gridLine.setAttribute('x2', 200);
    gridLine.setAttribute('y2', half);
    gridLine.setAttribute('stroke', '#333');
    gridLine.setAttribute('stroke-dasharray', '2,2');
    svg.appendChild(gridLine);

    const lineGen = d3.line()
      .x(d => xScale(d.turn))
      .y(d => yScale(d[varName]))
      .curve(d3.curveMonotoneX);

    // Draw a line per agent
    dlgAgentNames.forEach((name, idx) => {
      const data = dlgStateHistory[name] || [];
      const color = AGENT_COLORS[idx] || '#888';
      if (data.length > 1) {
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', lineGen(data));
        path.setAttribute('stroke', color);
        path.setAttribute('stroke-width', '1.5');
        path.setAttribute('fill', 'none');
        svg.appendChild(path);
      }
      if (data.length >= 1) {
        const last = data[data.length - 1];
        const dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        dot.setAttribute('cx', xScale(last.turn));
        dot.setAttribute('cy', yScale(last[varName]));
        dot.setAttribute('r', '2.5');
        dot.setAttribute('fill', color);
        svg.appendChild(dot);
      }
    });
  });
}

async function resetDialogue() {
  if (dlgRunning) return;
  document.getElementById('dlg-status').textContent = 'clearing...';
  try {
    await fetch('/sessions/dialogue:Alice/clear', {method: 'POST'});
    await fetch('/sessions/dialogue:Bob/clear', {method: 'POST'});
    document.getElementById('dlg-transcript').innerHTML = '';
    document.getElementById('dlg-status').textContent = 'cleared both agents';
  } catch(e) {
    document.getElementById('dlg-status').textContent = 'clear failed: ' + e.message;
  }
}

// Categories
async function loadCategories() {
  const res = await fetch('/categories');
  const cats = await res.json();
  const container = document.getElementById('categories-list');
  if (cats.length === 0) {
    container.innerHTML = '<div style="color:var(--dim);font-size:13px;padding:12px 0">' +
      'No categories yet. Chat some more and click "Run Consolidation" to discover them.</div>';
    return;
  }
  container.innerHTML = '';
  cats.forEach(c => {
    const tags = (c.top_tags || []).join(', ');
    const card = document.createElement('div');
    card.className = 'memory-card';
    card.style.cursor = 'pointer';
    card.innerHTML = `
      <div class="title">${c.name} <span style="color:var(--dim);font-weight:normal">(${c.id})</span></div>
      <div class="meta">${c.member_count} members | avg brightness: ${(c.avg_brightness||0).toFixed(2)}${c.parent_id ? ' | parent: '+c.parent_id : ''}</div>
      <div class="meta">tags: ${tags}</div>
      <div class="content">${esc(c.description || '')}</div>
    `;
    card.addEventListener('click', async () => {
      const full = await fetch('/categories/' + c.id).then(x=>x.json());
      const members = full.members || [];
      let detail = `<h3 style="color:var(--accent);font-size:14px;margin:12px 0">${c.name} — ${members.length} members</h3>`;
      members.slice(0, 20).forEach(m => {
        detail += `<div class="memory-card"><div class="title">${m.id}</div>` +
          `<div class="meta">brightness: ${m.brightness.toFixed(2)} | tags: ${(m.tags||[]).join(', ')}</div>` +
          `<div class="content">${esc(m.core.slice(0, 200))}</div></div>`;
      });
      container.innerHTML = '<div style="cursor:pointer;color:var(--accent);font-size:12px;margin-bottom:8px" ' +
        'onclick="loadCategories()">← back to all categories</div>' + detail;
    });
    container.appendChild(card);
  });
}

async function runConsolidate() {
  const status = document.getElementById('consolidate-status');
  status.textContent = 'running...';
  try {
    const res = await fetch('/consolidate', {method:'POST'});
    const data = await res.json();
    const parts = Object.entries(data).map(([k,v]) => `${k}: ${v}`);
    status.textContent = parts.join(' | ');
    loadCategories();
  } catch(e) {
    status.textContent = 'error: ' + e.message;
  }
}

async function runCoherence() {
  const query = document.getElementById('coherence-query').value.trim();
  const out = document.getElementById('coherence-output');
  if (!query) { out.textContent = 'enter a query first'; out.style.display = 'block'; return; }
  out.textContent = 'running...';
  out.style.display = 'block';
  try {
    const res = await fetch('/coherence?query=' + encodeURIComponent(query));
    if (!res.ok) {
      const err = await res.text();
      out.textContent = 'error: ' + err;
      return;
    }
    const data = await res.json();
    out.textContent = data.text || JSON.stringify(data, null, 2);
  } catch(e) {
    out.textContent = 'error: ' + e.message;
  }
}

// Ingest
async function runBench() {
  const benchmark = document.getElementById('bench-name').value;
  const policy = document.getElementById('bench-policy').value;
  const status = document.getElementById('bench-status');
  const results = document.getElementById('bench-results');
  status.textContent = 'running... (this may take a few seconds)';
  results.innerHTML = '';
  try {
    const res = await fetch('/bench', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({benchmark, policy})
    });
    const data = await res.json();
    status.textContent = 'done';
    renderBenchResults(data, benchmark);
  } catch(e) {
    status.textContent = 'error: ' + e.message;
  }
}

function renderBenchResults(data, benchmark) {
  const container = document.getElementById('bench-results');
  const comp = data.comparison;
  const policies = Object.keys(comp);
  if (policies.length === 0) {
    container.innerHTML = '<div style="color:var(--dim)">no results</div>';
    return;
  }
  // Collect all metric names
  const metrics = new Set();
  policies.forEach(p => Object.keys(comp[p]).forEach(m => metrics.add(m)));
  const metricList = Array.from(metrics).sort();

  // Find best per metric (higher = better for most; lower for latency)
  const lowerIsBetter = new Set(['latency_mean_s','latency_p95_s','strategic_fallback_rate','avg_memories_activated']);
  const best = {};
  metricList.forEach(m => {
    let bestVal = null, bestPolicy = null;
    policies.forEach(p => {
      const v = comp[p][m];
      if (v == null) return;
      if (bestVal === null) { bestVal = v; bestPolicy = p; return; }
      if (lowerIsBetter.has(m) ? v < bestVal : v > bestVal) {
        bestVal = v; bestPolicy = p;
      }
    });
    best[m] = bestPolicy;
  });

  let html = `<h3 style="color:var(--accent2);font-size:14px;margin-bottom:8px">Benchmark: ${benchmark}</h3>`;
  html += '<table style="width:100%;border-collapse:collapse;font-size:12px">';
  html += '<tr style="border-bottom:1px solid var(--border)">';
  html += '<th style="text-align:left;padding:8px;color:var(--dim)">metric</th>';
  policies.forEach(p => {
    html += `<th style="text-align:right;padding:8px;color:var(--accent)">${p}</th>`;
  });
  html += '</tr>';
  metricList.forEach(m => {
    html += `<tr style="border-bottom:1px solid #222"><td style="padding:6px 8px;color:var(--dim)">${m}</td>`;
    policies.forEach(p => {
      const v = comp[p][m];
      const isBest = best[m] === p;
      const style = isBest ? 'color:var(--accent2);font-weight:bold' : 'color:var(--text)';
      html += `<td style="text-align:right;padding:6px 8px;${style}">${v != null ? v.toFixed(4) : '—'}</td>`;
    });
    html += '</tr>';
  });
  html += '</table>';
  html += `<div style="margin-top:8px;font-size:10px;color:var(--dim)">` +
    `Green = best for that metric. Lower is better for: latency_mean_s, latency_p95_s, strategic_fallback_rate, avg_memories_activated.</div>`;
  container.innerHTML = html;
}

async function doIngest() {
  const text = document.getElementById('ingest-text').value.trim();
  const session = document.getElementById('ingest-session').value.trim() || 'default';
  const status = document.getElementById('ingest-status');
  if (!text) { status.textContent = 'no text to ingest'; return; }
  status.textContent = 'ingesting...';
  try {
    const res = await fetch('/ingest', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({text, session_id: session})
    });
    const data = await res.json();
    status.textContent = `ingested ${data.ingested} memories into session "${data.session_id}"`;
    document.getElementById('ingest-text').value = '';
  } catch(e) {
    status.textContent = 'error: ' + e.message;
  }
}

// Runs
async function loadRuns() {
  const res = await fetch('/runs');
  const runs = await res.json();
  const list = document.getElementById('runs-list');
  const detail = document.getElementById('run-detail');
  list.innerHTML = '';
  detail.style.display = 'none';
  runs.forEach(r => {
    const item = document.createElement('div');
    item.className = 'run-item';
    item.textContent = `${r.id.slice(0,16)}... | ${r.user_input.slice(0,80)}`;
    item.addEventListener('click', async () => {
      const full = await fetch('/runs/' + r.id).then(x=>x.json());
      detail.style.display = 'block';
      detail.innerHTML = `<pre>${esc(JSON.stringify(full, null, 2))}</pre>`;
    });
    list.appendChild(item);
  });
}
</script>
</body>
</html>
"""


@router.get("/ui", response_class=HTMLResponse)
async def ui_page() -> str:
    return _PAGE
