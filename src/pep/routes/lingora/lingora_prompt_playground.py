"""Standalone playground for Lingora Prompt — paste a prompt, get analysis."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


_PAGE = """\
<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lingora Prompt Playground — live engine</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg: #0a0e16; --surface: #161c28; --surface2: #0e1420;
    --text: #e0e6ed; --dim: #7a8492; --accent: #ba68c8; --accent2: #a3e635;
    --warn: #f59e0b; --danger: #f06292; --border: #2a3140;
  }
  body { font-family: 'SF Mono', monospace; background: var(--bg); color: var(--text); line-height: 1.6; }
  a { color: var(--accent); text-decoration: none; }
  a:hover { text-decoration: underline; }
  nav { position: sticky; top: 0; background: var(--bg); padding: 10px 20px;
        border-bottom: 1px solid var(--border); display: flex; gap: 14px;
        align-items: center; flex-wrap: wrap; z-index: 10; }
  .brand { font-size: 18px; font-weight: bold; color: var(--accent); }
  .badge { font-size: 9px; color: var(--accent); background: rgba(186,104,200,0.15);
           padding: 2px 8px; border-radius: 10px; letter-spacing: 0.05em; }
  .links { margin-left: auto; display: flex; gap: 14px; font-size: 11px; }
  .links a { color: var(--dim); }
  .links a:hover { color: var(--accent); }
  .layout { display: grid; grid-template-columns: 1fr 1fr; min-height: calc(100vh - 50px); }
  .pane { padding: 18px 20px; overflow-y: auto; }
  .pane-left { border-right: 1px solid var(--border); }
  .label { font-size: 10px; color: var(--dim); letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 8px; }
  textarea { width: 100%; background: var(--surface2); color: var(--text);
             border: 1px solid var(--border); border-radius: 4px;
             padding: 12px; font-family: inherit; font-size: 12px; line-height: 1.6;
             resize: vertical; min-height: 260px; }
  textarea:focus { outline: none; border-color: var(--accent); }
  button.btn { padding: 8px 16px; border-radius: 4px; border: 1px solid var(--accent);
               background: var(--accent); color: var(--bg); font-size: 11px;
               cursor: pointer; font-family: inherit; font-weight: bold; }
  button.alt { padding: 8px 16px; border-radius: 4px; border: 1px solid var(--border);
               background: transparent; color: var(--dim); font-size: 11px;
               cursor: pointer; font-family: inherit; }
  button.alt:hover { color: var(--text); border-color: var(--accent); }
  .stats-row { display: flex; gap: 14px; flex-wrap: wrap; background: var(--surface);
               border: 1px solid var(--border); border-radius: 6px;
               padding: 12px 14px; margin-bottom: 14px; font-size: 11px; }
  .stat .k { color: var(--dim); }
  .stat .v { color: var(--accent); font-weight: bold; }
  .section { margin-bottom: 20px; }
  .section h3 { font-size: 12px; color: var(--accent); margin-bottom: 10px;
                letter-spacing: 0.1em; text-transform: uppercase; }
  .finding { background: var(--surface); border: 1px solid var(--border);
             border-left: 3px solid var(--warn); border-radius: 4px;
             padding: 10px 14px; margin-bottom: 8px; font-size: 11px; }
  .finding.low { border-left-color: #67e8f9; }
  .finding.medium { border-left-color: var(--warn); }
  .finding.high { border-left-color: var(--danger); }
  .finding .name { font-weight: bold; }
  .finding.low .name { color: #67e8f9; }
  .finding.medium .name { color: var(--warn); }
  .finding.high .name { color: var(--danger); }
  .finding .msg { color: var(--text); margin-top: 4px; line-height: 1.6; }
  .finding .sug { color: var(--dim); margin-top: 6px; font-style: italic; line-height: 1.6; }
  .rewrite-box { background: var(--surface2); border: 1px solid var(--border);
                 border-radius: 4px; padding: 12px; font-family: 'SF Mono', monospace;
                 font-size: 11px; color: var(--text); white-space: pre-wrap; line-height: 1.7;
                 max-height: 240px; overflow-y: auto; }
  .transforms { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
  .transform { background: rgba(163,230,53,0.1); color: var(--accent2);
               padding: 2px 8px; border-radius: 10px; font-size: 10px;
               border: 1px solid rgba(163,230,53,0.3); }
  table { width: 100%; border-collapse: collapse; background: var(--surface);
          border: 1px solid var(--border); border-radius: 4px; overflow: hidden; font-size: 11px; }
  th, td { padding: 8px 10px; text-align: left; border-bottom: 1px solid var(--border); }
  th { color: var(--dim); letter-spacing: 0.1em; font-size: 10px;
       text-transform: uppercase; font-weight: bold; }
  td.num { text-align: right; font-family: monospace; }
  td.save { color: var(--accent2); font-weight: bold; }
  .samples { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-bottom: 10px; }
  .sample { background: var(--surface); border: 1px solid var(--border);
            border-radius: 4px; padding: 8px 10px; font-size: 10px;
            color: var(--text); cursor: pointer; text-align: left; }
  .sample:hover { border-color: var(--accent); }
  .sample .kind { font-size: 9px; color: var(--dim); letter-spacing: 0.1em;
                  text-transform: uppercase; margin-bottom: 3px; }
  .controls-row { display: flex; gap: 8px; flex-wrap: wrap; align-items: center;
                  margin-top: 10px; margin-bottom: 14px; }
  .controls-row label { font-size: 10px; color: var(--dim); display: flex;
                        align-items: center; gap: 6px; }
  .controls-row input[type=range] { width: 120px; }
  .controls-row .v { color: var(--accent); font-weight: bold; min-width: 40px; text-align: right; }
  .empty-state { text-align: center; padding: 40px 20px; color: var(--dim); font-size: 12px; }
  @media (max-width: 900px) { .layout { grid-template-columns: 1fr; } }
</style></head><body>
<nav>
  <span class="brand">Lingora Prompt</span>
  <span class="badge">LIVE ENGINE</span>
  <div class="links">
    <a href="/lingora/prompt">Product</a>
    <a href="/lingora">Lingora</a>
    <a href="/pep">PEP</a>
  </div>
</nav>
<div class="layout">
  <div class="pane pane-left">
    <div class="label">Your prompt</div>
    <textarea id="input" placeholder="paste a prompt here..."></textarea>
    <div class="controls-row">
      <button class="btn" onclick="analyze()">Analyze</button>
      <button class="alt" onclick="clearInput()">Clear</button>
      <span style="margin-left:auto;font-size:10px;color:var(--dim)" id="input-size">0 chars</span>
    </div>
    <div class="section">
      <div class="label">Sample prompts (click to load)</div>
      <div class="samples" id="samples"></div>
    </div>
    <div class="section">
      <div class="label">Cost assumptions</div>
      <div class="controls-row">
        <label>requests/day:
          <input type="range" id="vol" min="100" max="100000" step="100" value="10000" oninput="onVolChange()">
          <span class="v" id="vol-v">10,000</span>
        </label>
      </div>
    </div>
  </div>
  <div class="pane">
    <div id="results"><div class="empty-state">Paste a prompt and click Analyze.</div></div>
  </div>
</div>
<script>
const SAMPLES = [
  { kind: 'POLITE-VERBOSE', text: `You are a helpful assistant. Please be helpful and answer the user's question.
Please make sure to be accurate and thorough. Always provide complete answers.
Do not be unhelpful. Think step by step.

User: What is the capital of France?` },
  { kind: 'MIXED FRAMING', text: `You are a coding assistant.
Always be thorough. Never skip details. Always explain your reasoning.
Do not be verbose. Make sure to be concise. Never write more than necessary.

User: Explain what a hashmap is.` },
  { kind: 'CONFLICTING FORMAT', text: `Respond in JSON format.
Format: markdown table.
Output should be CSV.

User: List three prime numbers.` },
  { kind: 'CLEAN', text: `Translate the following English sentence to French.

User: The quick brown fox jumps over the lazy dog.` },
];
function esc(s) { return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function renderSamples() {
  document.getElementById('samples').innerHTML = SAMPLES.map((s, i) =>
    `<button class="sample" onclick="loadSample(${i})"><div class="kind">${s.kind}</div>${esc(s.text.slice(0, 80))}...</button>`
  ).join('');
}
function loadSample(i) { document.getElementById('input').value = SAMPLES[i].text; updateInputSize(); analyze(); }
function updateInputSize() {
  const t = document.getElementById('input').value;
  document.getElementById('input-size').textContent = t.length + ' chars';
}
function clearInput() {
  document.getElementById('input').value = '';
  document.getElementById('results').innerHTML = '<div class="empty-state">Paste a prompt and click Analyze.</div>';
  updateInputSize();
}
function onVolChange() {
  const v = parseInt(document.getElementById('vol').value);
  document.getElementById('vol-v').textContent = v.toLocaleString();
}
document.getElementById('input').addEventListener('input', updateInputSize);

async function analyze() {
  const text = document.getElementById('input').value;
  if (!text.trim()) return;
  const res = document.getElementById('results');
  res.innerHTML = '<div class="empty-state">Analyzing...</div>';
  const volume = parseInt(document.getElementById('vol').value);
  try {
    const [anaR, costR] = await Promise.all([
      fetch('/lingora/prompt-api/analyze', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({text, include_rewrite: true}),
      }),
      fetch('/lingora/prompt-api/compare', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({original: text, daily_requests: volume, output_tokens: 100}),
      }),
    ]);
    if (!anaR.ok) throw new Error('analysis failed');
    if (!costR.ok) throw new Error('cost compare failed');
    const a = await anaR.json();
    const c = await costR.json();
    render(a, c, volume);
  } catch (e) {
    res.innerHTML = `<div class="empty-state" style="color:var(--danger)">Error: ${esc(e.message)}</div>`;
  }
}

function render(a, c, volume) {
  const findings = a.findings.length ? a.findings.map(f =>
    `<div class="finding ${f.severity}"><div class="name">${esc(f.name)}</div><div class="msg">${esc(f.message)}</div><div class="sug">→ ${esc(f.suggestion)}</div></div>`
  ).join('') : '<div style="color:var(--dim);font-size:11px">No issues detected.</div>';

  const roles = Object.entries(a.segment_tokens_by_role).map(([r, t]) =>
    `<span style="color:var(--accent)">${esc(r)}</span> <span style="color:var(--dim)">${t}</span>`
  ).join('  ·  ');

  const rewriteHTML = a.rewrite ? `
    <div class="section">
      <h3>Compressed rewrite (${a.rewrite.original_tokens} → ${a.rewrite.compressed_tokens} tokens, −${a.rewrite.token_savings_pct}%)</h3>
      <div class="rewrite-box">${esc(a.rewrite.compressed_text) || '<em>no changes</em>'}</div>
      <div class="transforms">
        ${a.rewrite.transformations_applied.map(t => `<span class="transform">${esc(t)}</span>`).join('')}
      </div>
    </div>` : '';

  const costTable = c.per_provider.length ? `
    <table><thead><tr>
      <th>Provider</th><th style="text-align:right">Original</th><th style="text-align:right">Compressed</th><th style="text-align:right">Annual save</th>
    </tr></thead><tbody>
    ${c.per_provider.map(r => `<tr>
      <td>${esc(r.provider)}</td>
      <td class="num">$${r.original_monthly.toFixed(2)}/mo</td>
      <td class="num">$${r.compressed_monthly.toFixed(2)}/mo</td>
      <td class="num save">$${r.annual_savings_usd.toFixed(2)}</td>
    </tr>`).join('')}
    </tbody></table>` : '';

  document.getElementById('results').innerHTML = `
    <div class="stats-row">
      <div class="stat"><span class="k">tokens:</span> <span class="v">${a.total_tokens}</span></div>
      <div class="stat"><span class="k">words:</span> <span class="v">${a.total_words}</span></div>
      <div class="stat"><span class="k">chars:</span> <span class="v">${a.total_chars}</span></div>
      <div class="stat"><span class="k">segments:</span> <span class="v">${a.segments.length}</span></div>
      <div class="stat"><span class="k">findings:</span> <span class="v">${a.findings.length}</span>
        <span style="color:var(--dim);margin-left:6px">(${a.severity_counts.high}H ${a.severity_counts.medium}M ${a.severity_counts.low}L)</span>
      </div>
      <div class="stat"><span class="k">tokenizer:</span> <span class="v">${esc(a.tokenizer_method)}</span></div>
    </div>
    <div class="section">
      <h3>Tokens by role</h3>
      <div style="font-size:11px">${roles || '<em>no segments</em>'}</div>
    </div>
    <div class="section">
      <h3>Findings (${a.findings.length})</h3>
      ${findings}
    </div>
    ${rewriteHTML}
    <div class="section">
      <h3>Cost @ ${volume.toLocaleString()} req/day</h3>
      ${costTable}
    </div>
  `;
}

renderSamples();
</script></body></html>
"""


@router.get("/lingora/prompt/playground", response_class=HTMLResponse)
async def prompt_playground() -> str:
    return _PAGE
