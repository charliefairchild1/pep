"""HTTP APIs for Lingora Translate, Voice, and Learn."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from pep.lingora import translate, voice, learn

router = APIRouter()


# ═══ Translate ══════════════════════════════════════════════════════════
class TranslateBody(BaseModel):
    text: str
    target_lang: str = "es"


@router.post("/lingora/translate-api/analyze")
async def translate_analyze(body: TranslateBody) -> dict[str, Any]:
    r = translate.translate(body.text, body.target_lang)
    return {
        "source": r.source,
        "source_lang": r.source_lang,
        "target_lang": r.target_lang,
        "mt_output": r.mt_output,
        "lingora_output": r.lingora_output,
        "mt_overall_preservation": r.mt_overall_preservation,
        "lingora_overall_preservation": r.lingora_overall_preservation,
        "explanation": r.explanation,
        "layers": [
            {"layer": l.layer.value, "description": l.description,
             "mt_preserves": l.mt_preserves, "lingora_preserves": l.lingora_preserves}
            for l in r.layers
        ],
    }


@router.get("/lingora/translate/playground", response_class=HTMLResponse)
async def translate_playground() -> str:
    return _translate_html()


# ═══ Voice ══════════════════════════════════════════════════════════════
class VoiceBody(BaseModel):
    text: str


@router.post("/lingora/voice-api/analyze")
async def voice_analyze(body: VoiceBody) -> dict[str, Any]:
    r = voice.analyze_voice(body.text)
    return {
        "total_words": r.total_words,
        "total_sentences": r.total_sentences,
        "voice_signature": r.voice_signature,
        "overall_voice_strength": r.overall_voice_strength,
        "mechanisms": [
            {"name": m.name, "value": m.value, "description": m.description}
            for m in r.mechanisms
        ],
        "diagnostics": [
            {"mechanism": d.mechanism, "suggestion": d.suggestion, "priority": d.priority}
            for d in r.diagnostics
        ],
    }


@router.get("/lingora/voice/playground", response_class=HTMLResponse)
async def voice_playground() -> str:
    return _voice_html()


# ═══ Learn ══════════════════════════════════════════════════════════════
_learners: dict[str, learn.LearnerProfile] = {}


def _get_learner(session: str) -> learn.LearnerProfile:
    if session not in _learners:
        _learners[session] = learn.make_learner()
    return _learners[session]


class LearnStudyBody(BaseModel):
    session: str
    word: str


class LearnRecallBody(BaseModel):
    session: str
    word: str
    success: bool


@router.post("/lingora/learn-api/study")
async def learn_study(body: LearnStudyBody) -> dict[str, Any]:
    lp = _get_learner(body.session)
    sess = lp.study_word(body.word)
    if not sess:
        return {"error": f"unknown word: {body.word}"}
    return {
        "word": sess.word, "action": sess.action,
        "strength_before": sess.strength_before, "strength_after": sess.strength_after,
        "half_life_before": sess.half_life_before, "half_life_after": sess.half_life_after,
        "depth": sess.depth, "stats": lp.stats(),
    }


@router.post("/lingora/learn-api/recall")
async def learn_recall(body: LearnRecallBody) -> dict[str, Any]:
    lp = _get_learner(body.session)
    sess = lp.recall(body.word, body.success)
    if not sess:
        return {"error": f"unknown word: {body.word}"}
    return {
        "word": sess.word, "action": sess.action,
        "strength_before": sess.strength_before, "strength_after": sess.strength_after,
        "half_life_before": sess.half_life_before, "half_life_after": sess.half_life_after,
        "depth": sess.depth, "stats": lp.stats(),
    }


@router.get("/lingora/learn-api/next-review/{session}")
async def learn_next(session: str, k: int = 5) -> dict[str, Any]:
    lp = _get_learner(session)
    words = lp.next_review(k)
    return {
        "words": [
            {"word": w.word, "definition": w.definition, "strength": round(w.effective_strength(), 4),
             "depth": w.acquisition_depth, "times_seen": w.times_seen}
            for w in words
        ],
        "stats": lp.stats(),
    }


@router.get("/lingora/learn-api/vocabulary")
async def learn_vocabulary() -> dict[str, Any]:
    return {
        "words": [
            {"word": w.word, "definition": w.definition,
             "contexts": w.contexts, "associations": w.associations}
            for w in learn.SAMPLE_VOCABULARY
        ]
    }


@router.get("/lingora/learn/playground", response_class=HTMLResponse)
async def learn_playground() -> str:
    return _learn_html()


# ═══ Playground HTML ════════════════════════════════════════════════════

def _translate_html() -> str:
    return """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lingora Translate Playground</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  :root { --bg: #0a0e16; --surface: #161c28; --text: #e0e6ed; --dim: #7a8492; --accent: #4fc3f7; --border: #2a3140; }
  body { font-family: 'SF Mono', monospace; background: var(--bg); color: var(--text); line-height: 1.6; padding: 20px; }
  nav { position: sticky; top: 0; background: var(--bg); padding: 10px 0; border-bottom: 1px solid var(--border);
        display: flex; gap: 14px; align-items: center; flex-wrap: wrap; margin: -20px -20px 20px; padding: 10px 20px; }
  .brand { font-size: 18px; font-weight: bold; color: var(--accent); }
  .badge { font-size: 9px; color: var(--accent); background: rgba(79,195,247,0.15); padding: 2px 8px; border-radius: 10px; }
  .links { margin-left: auto; display: flex; gap: 14px; font-size: 11px; }
  .links a { color: var(--dim); text-decoration: none; }
  .container { max-width: 900px; margin: 0 auto; }
  h2 { font-size: 16px; color: var(--accent); margin-bottom: 12px; }
  .desc { font-size: 11px; color: var(--dim); line-height: 1.7; margin-bottom: 16px; }
  input { width: 100%; background: #0e1420; color: var(--text); border: 1px solid var(--border); border-radius: 4px; padding: 10px; font-family: inherit; font-size: 12px; }
  button { padding: 8px 16px; border-radius: 4px; border: 1px solid var(--accent); background: var(--accent); color: var(--bg); font-size: 11px; cursor: pointer; font-family: inherit; font-weight: bold; }
  .samples { display: flex; gap: 6px; flex-wrap: wrap; margin: 10px 0; }
  .sample { padding: 4px 10px; border-radius: 12px; border: 1px solid var(--border); background: var(--surface); color: var(--text); font-size: 10px; cursor: pointer; font-family: inherit; }
  .sample:hover { border-color: var(--accent); }
  .result { background: var(--surface); border: 1px solid var(--border); border-radius: 6px; padding: 16px; margin-top: 14px; }
  .layer { display: grid; grid-template-columns: 100px 1fr 1fr; gap: 10px; padding: 8px 0; border-bottom: 1px solid var(--border); font-size: 11px; }
  .layer:last-child { border-bottom: none; }
  .layer .name { color: var(--accent); font-weight: bold; }
  .bar { height: 8px; border-radius: 4px; }
  .compare { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 14px; }
  .compare-col { background: #0e1420; border: 1px solid var(--border); border-radius: 6px; padding: 14px; }
  .compare-col h3 { font-size: 11px; margin-bottom: 8px; }
  .compare-col.mt h3 { color: #a78bfa; }
  .compare-col.lin h3 { color: var(--accent); }
  .compare-col .text { font-size: 12px; line-height: 1.7; }
  @media (max-width: 700px) { .compare { grid-template-columns: 1fr; } }
</style></head><body>
<nav><span class="brand">Lingora Translate</span><span class="badge">LIVE ENGINE</span>
<div class="links"><a href="/lingora/translate">Product</a><a href="/lingora">Lingora</a><a href="/pep">PEP</a></div></nav>
<div class="container">
<h2>Pragmatic-preserving translation</h2>
<p class="desc">Type or pick a sentence. The engine decomposes it into four semantic layers, scores how much each layer survives standard MT vs Lingora-aware translation.</p>
<input id="input" placeholder="Type a sentence with pragmatic content...">
<div class="samples" id="samples"></div>
<button onclick="run()" style="margin-top:8px">Analyze</button>
<div id="results"></div>
</div>
<script>
const SAMPLES = ["It's a piece of cake", "Bless your heart", "Break a leg", "Yeah right", "That's just wonderful", "Under the weather", "Spill the beans"];
document.getElementById('samples').innerHTML = SAMPLES.map((s, i) => `<button class="sample" onclick="pick(${i})">${s}</button>`).join('');
function pick(i) { document.getElementById('input').value = SAMPLES[i]; run(); }
function esc(s) { return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
async function run() {
  const text = document.getElementById('input').value.trim(); if (!text) return;
  const r = await fetch('/lingora/translate-api/analyze', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({text}) });
  const d = await r.json();
  const layers = d.layers.map(l => `<div class="layer"><div class="name">${l.layer}</div><div><div style="font-size:10px;color:var(--dim);margin-bottom:3px">MT: ${(l.mt_preserves*100).toFixed(0)}%</div><div class="bar" style="width:${l.mt_preserves*100}%;background:rgba(167,139,250,0.7)"></div></div><div><div style="font-size:10px;color:var(--dim);margin-bottom:3px">Lingora: ${(l.lingora_preserves*100).toFixed(0)}%</div><div class="bar" style="width:${l.lingora_preserves*100}%;background:rgba(79,195,247,0.7)"></div></div></div>`).join('');
  document.getElementById('results').innerHTML = `
    <div class="result"><div style="font-size:11px;color:var(--dim);margin-bottom:10px">Layer preservation (purple = standard MT, blue = Lingora):</div><div style="display:grid;grid-template-columns:100px 1fr 1fr;gap:10px;padding-bottom:6px;font-size:10px;color:var(--dim)"><span>Layer</span><span>Standard MT</span><span>Lingora-aware</span></div>${layers}
    <div style="margin-top:12px;font-size:11px;color:var(--dim)">Overall: MT preserves <b style="color:#a78bfa">${(d.mt_overall_preservation*100).toFixed(0)}%</b> · Lingora preserves <b style="color:var(--accent)">${(d.lingora_overall_preservation*100).toFixed(0)}%</b></div></div>
    <div class="compare"><div class="compare-col mt"><h3>STANDARD MT</h3><div class="text">${esc(d.mt_output)}</div></div><div class="compare-col lin"><h3>LINGORA-AWARE</h3><div class="text">${esc(d.lingora_output)}</div></div></div>
    <div style="margin-top:12px;padding:12px;background:var(--surface);border:1px solid var(--border);border-radius:6px;font-size:11px;color:var(--text);line-height:1.7"><b style="color:var(--accent)">Why:</b> ${esc(d.explanation)}</div>`;
}
</script></body></html>"""


def _voice_html() -> str:
    return """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lingora Voice Playground</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  :root { --bg: #0a0e16; --surface: #161c28; --text: #e0e6ed; --dim: #7a8492; --accent: #81c784; --border: #2a3140; }
  body { font-family: 'SF Mono', monospace; background: var(--bg); color: var(--text); line-height: 1.6; padding: 20px; }
  nav { position: sticky; top: 0; background: var(--bg); padding: 10px 0; border-bottom: 1px solid var(--border);
        display: flex; gap: 14px; align-items: center; flex-wrap: wrap; margin: -20px -20px 20px; padding: 10px 20px; }
  .brand { font-size: 18px; font-weight: bold; color: var(--accent); }
  .badge { font-size: 9px; color: var(--accent); background: rgba(129,199,132,0.15); padding: 2px 8px; border-radius: 10px; }
  .links { margin-left: auto; display: flex; gap: 14px; font-size: 11px; }
  .links a { color: var(--dim); text-decoration: none; }
  .container { max-width: 900px; margin: 0 auto; }
  h2 { font-size: 16px; color: var(--accent); margin-bottom: 12px; }
  textarea { width: 100%; min-height: 160px; background: #0e1420; color: var(--text); border: 1px solid var(--border); border-radius: 4px; padding: 12px; font-family: inherit; font-size: 12px; resize: vertical; }
  button { padding: 8px 16px; border-radius: 4px; border: 1px solid var(--accent); background: var(--accent); color: var(--bg); font-size: 11px; cursor: pointer; font-family: inherit; font-weight: bold; }
  button.sample { padding: 6px 12px; border-radius: 4px; border: 1px solid var(--border); background: var(--surface); color: var(--text); font-size: 10px; cursor: pointer; }
  button.sample:hover { border-color: var(--accent); }
  .result { background: var(--surface); border: 1px solid var(--border); border-radius: 6px; padding: 16px; margin-top: 14px; }
  .mech { display: flex; gap: 10px; align-items: center; padding: 6px 0; font-size: 11px; }
  .mech .name { min-width: 130px; color: var(--accent); font-weight: bold; }
  .mech .bar-bg { flex: 1; height: 10px; background: #0e1420; border-radius: 5px; overflow: hidden; }
  .mech .bar-fill { height: 100%; border-radius: 5px; }
  .mech .val { min-width: 30px; text-align: right; color: var(--text); font-weight: bold; }
  .mech .desc { font-size: 9px; color: var(--dim); min-width: 180px; }
  .diag { background: #0e1420; border: 1px solid var(--border); border-left: 3px solid var(--accent); border-radius: 4px; padding: 10px 14px; margin-top: 8px; font-size: 11px; }
  .diag .mech-name { color: var(--accent); font-weight: bold; font-size: 10px; }
  .diag .sug { color: var(--text); margin-top: 4px; line-height: 1.6; }
</style></head><body>
<nav><span class="brand">Lingora Voice</span><span class="badge">LIVE ENGINE</span>
<div class="links"><a href="/lingora/voice">Product</a><a href="/lingora">Lingora</a><a href="/pep">PEP</a></div></nav>
<div class="container">
<h2>Voice-aware writing analysis</h2>
<p style="font-size:11px;color:var(--dim);margin-bottom:12px">Paste a paragraph. The engine scores 8 voice mechanisms and generates voice-preserving suggestions — not "fix your grammar" but "here's what your style is doing and how to sharpen it."</p>
<div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px" id="samples"></div>
<textarea id="input" placeholder="Paste a paragraph..."></textarea>
<button onclick="run()" style="margin-top:8px">Analyze voice</button>
<div id="results"></div>
</div>
<script>
const SAMPLES = [
  {label: 'Hemingway', text: 'The old man was thin and gaunt with deep wrinkles. He fished alone. He had not caught a fish in eighty-four days. The boy loved him.'},
  {label: 'Faulkner', text: 'It was a long sentence that wound through the dust of years and the heat of summers and the slow thick blood of a family that did not know how to forget.'},
  {label: 'Corporate', text: 'It has been determined that certain efficiencies could potentially be realized through a strategic re-evaluation of current operational paradigms.'},
  {label: 'Tweet', text: "oh great another framework that'll be deprecated by friday"},
];
document.getElementById('samples').innerHTML = SAMPLES.map(s => `<button class="sample" onclick="pick('${s.label}')">${s.label}</button>`).join('');
function pick(label) { const s = SAMPLES.find(x => x.label === label); if (s) { document.getElementById('input').value = s.text; run(); } }
function esc(s) { return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
const MECH_COLORS = { pov: '#a78bfa', register: '#4fc3f7', irony: '#f06292', subtext: '#fbbf24', pacing: '#81c784', voice_consistency: '#67e8f9', repetition: '#ffb74d', sound_symmetry: '#ec4899' };
async function run() {
  const text = document.getElementById('input').value.trim(); if (!text) return;
  const r = await fetch('/lingora/voice-api/analyze', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({text}) });
  const d = await r.json();
  const mechs = d.mechanisms.map(m => {
    const col = MECH_COLORS[m.name] || '#81c784';
    return `<div class="mech"><span class="name">${m.name}</span><span class="bar-bg"><span class="bar-fill" style="width:${Math.round(m.value*100)}%;background:${col}"></span></span><span class="val">${(m.value*100).toFixed(0)}</span><span class="desc">${esc(m.description)}</span></div>`;
  }).join('');
  const diags = d.diagnostics.map(d => `<div class="diag"><div class="mech-name">${d.mechanism} (${d.priority})</div><div class="sug">${esc(d.suggestion)}</div></div>`).join('');
  document.getElementById('results').innerHTML = `
    <div class="result">
      <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:12px"><div style="font-size:13px;color:var(--accent);font-weight:bold">Voice signature: ${esc(d.voice_signature)}</div><div style="font-size:11px;color:var(--dim)">${d.total_words} words · ${d.total_sentences} sentences · strength ${(d.overall_voice_strength*100).toFixed(0)}%</div></div>
      ${mechs}
    </div>
    <div style="margin-top:14px"><div style="font-size:11px;color:var(--accent);font-weight:bold;margin-bottom:8px">Voice-preserving diagnostics</div>${diags}</div>`;
}
</script></body></html>"""


def _learn_html() -> str:
    return """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lingora Learn Playground</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  :root { --bg: #0e0a16; --surface: #1a1228; --text: #e8daf4; --dim: #8a78a0; --accent: #ffb74d; --border: #2a1e38; }
  body { font-family: 'SF Mono', monospace; background: var(--bg); color: var(--text); line-height: 1.6; }
  nav { position: sticky; top: 0; background: var(--bg); padding: 10px 20px; border-bottom: 1px solid var(--border);
        display: flex; gap: 14px; align-items: center; flex-wrap: wrap; }
  .brand { font-size: 18px; font-weight: bold; color: var(--accent); }
  .badge { font-size: 9px; color: var(--accent); background: rgba(255,183,77,0.15); padding: 2px 8px; border-radius: 10px; }
  .links { margin-left: auto; display: flex; gap: 14px; font-size: 11px; }
  .links a { color: var(--dim); text-decoration: none; }
  .layout { display: grid; grid-template-columns: 340px 1fr; min-height: calc(100vh - 50px); }
  .sidebar { background: var(--surface); border-right: 1px solid var(--border); padding: 18px; overflow-y: auto; }
  .main { padding: 18px 24px; overflow-y: auto; }
  .label { font-size: 10px; color: var(--dim); letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 8px; }
  .word-card { background: #17101e; border: 1px solid var(--border); border-left: 3px solid var(--border);
               border-radius: 4px; padding: 10px 14px; margin-bottom: 6px; cursor: pointer; font-size: 11px; }
  .word-card:hover { border-color: var(--accent); }
  .word-card.studied { border-left-color: var(--accent); }
  .word-card .word { color: var(--accent); font-weight: bold; font-size: 12px; }
  .word-card .def { color: var(--dim); font-size: 10px; margin-top: 2px; }
  .word-card .strength { float: right; font-size: 10px; }
  button { padding: 6px 14px; border-radius: 4px; border: 1px solid var(--accent); background: var(--accent);
           color: var(--bg); font-size: 11px; cursor: pointer; font-family: inherit; font-weight: bold; }
  button.alt { border-color: var(--border); background: transparent; color: var(--dim); font-weight: normal; }
  .detail { background: var(--surface); border: 1px solid var(--border); border-radius: 6px; padding: 18px; margin-bottom: 14px; }
  .contexts { list-style: none; }
  .contexts li { padding: 6px 0; border-bottom: 1px solid var(--border); font-size: 11px; font-style: italic; color: var(--dim); }
  .contexts li:last-child { border-bottom: none; }
  .assoc { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 8px; }
  .assoc span { background: rgba(255,183,77,0.1); border: 1px solid rgba(255,183,77,0.3); color: var(--accent);
                padding: 2px 8px; border-radius: 10px; font-size: 10px; }
  .stats { background: var(--surface); border: 1px solid var(--border); border-radius: 6px; padding: 14px; font-size: 11px; margin-bottom: 14px; }
  .stats .row { display: flex; justify-content: space-between; padding: 3px 0; }
  .stats .k { color: var(--dim); }
  .stats .v { color: var(--accent); font-weight: bold; }
  .event { padding: 8px 12px; border-bottom: 1px solid var(--border); font-size: 10px; }
  .event .action { font-weight: bold; }
  .event.study .action { color: var(--accent); }
  .event.recall_success .action { color: #81c784; }
  .event.recall_failure .action { color: #f06292; }
  .empty { text-align: center; padding: 40px 20px; color: var(--dim); font-size: 12px; }
  @media (max-width: 900px) { .layout { grid-template-columns: 1fr; } }
</style></head><body>
<nav><span class="brand">Lingora Learn</span><span class="badge">LIVE ENGINE</span>
<div class="links"><a href="/lingora/learn">Product</a><a href="/lingora">Lingora</a><a href="/pep">PEP</a></div></nav>
<div class="layout">
<div class="sidebar">
  <div class="label">Vocabulary (10 untranslatable words)</div>
  <div id="word-list"></div>
  <div id="stats-box" class="stats" style="margin-top:14px;display:none"></div>
</div>
<div class="main">
  <div id="detail"><div class="empty">Click a word to study it.</div></div>
  <div class="label" style="margin-top:20px">Study history</div>
  <div id="history" style="background:var(--surface);border:1px solid var(--border);border-radius:6px;max-height:300px;overflow-y:auto"><div style="padding:20px;color:var(--dim);text-align:center;font-size:11px">No study events yet.</div></div>
</div>
</div>
<script>
const session = 'learn-' + Math.random().toString(36).slice(2, 8);
let vocab = [];
let currentWord = null;
function esc(s) { return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
async function init() {
  const r = await fetch('/lingora/learn-api/vocabulary');
  vocab = (await r.json()).words;
  renderWordList();
}
function renderWordList() {
  document.getElementById('word-list').innerHTML = vocab.map(w =>
    `<div class="word-card" id="wc-${w.word}" onclick="selectWord('${w.word}')"><span class="strength" id="ws-${w.word}">unseen</span><div class="word">${esc(w.word)}</div><div class="def">${esc(w.definition.slice(0, 50))}</div></div>`
  ).join('');
}
function selectWord(word) {
  currentWord = word;
  const w = vocab.find(v => v.word === word);
  if (!w) return;
  const ctx = w.contexts.map(c => `<li>${esc(c)}</li>`).join('');
  const assoc = w.associations.map(a => `<span>${esc(a)}</span>`).join('');
  document.getElementById('detail').innerHTML = `
    <div class="detail">
      <div style="font-size:18px;color:var(--accent);font-weight:bold;margin-bottom:6px">${esc(w.word)}</div>
      <div style="font-size:12px;color:var(--text);margin-bottom:12px;line-height:1.7">${esc(w.definition)}</div>
      <div class="label">Example contexts (the constellation)</div>
      <ul class="contexts">${ctx}</ul>
      <div class="label" style="margin-top:12px">Semantic associations</div>
      <div class="assoc">${assoc}</div>
      <div style="display:flex;gap:8px;margin-top:16px">
        <button onclick="doStudy('${word}')">Study this word</button>
        <button onclick="doRecall('${word}', true)" class="alt" style="border-color:#81c784;color:#81c784">I recalled it ✓</button>
        <button onclick="doRecall('${word}', false)" class="alt" style="border-color:#f06292;color:#f06292">I forgot ✗</button>
      </div>
    </div>`;
}
async function doStudy(word) {
  const r = await fetch('/lingora/learn-api/study', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({session, word}) });
  const d = await r.json();
  addEvent(d); updateStats(d.stats); updateCard(word, d);
}
async function doRecall(word, success) {
  const r = await fetch('/lingora/learn-api/recall', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({session, word, success}) });
  const d = await r.json();
  addEvent(d); updateStats(d.stats); updateCard(word, d);
}
function addEvent(d) {
  const hist = document.getElementById('history');
  if (hist.querySelector('.empty')) hist.innerHTML = '';
  const cls = d.action;
  const div = document.createElement('div');
  div.className = 'event ' + cls;
  div.innerHTML = `<span class="action">${d.action}</span> <b>${esc(d.word)}</b> — strength ${d.strength_before} → ${d.strength_after} · half-life ${d.half_life_before}h → ${d.half_life_after}h · depth: ${d.depth}`;
  hist.insertBefore(div, hist.firstChild);
}
function updateStats(stats) {
  const box = document.getElementById('stats-box');
  box.style.display = 'block';
  box.innerHTML = `<div class="row"><span class="k">studied:</span><span class="v">${stats.total_study_events}</span></div>
    <div class="row"><span class="k">avg strength:</span><span class="v">${(stats.avg_strength * 100).toFixed(0)}%</span></div>
    <div class="row"><span class="k">deep:</span><span class="v">${stats.depths.deep}</span></div>
    <div class="row"><span class="k">moderate:</span><span class="v">${stats.depths.moderate}</span></div>
    <div class="row"><span class="k">shallow:</span><span class="v">${stats.depths.shallow}</span></div>
    <div class="row"><span class="k">fading:</span><span class="v">${stats.depths.fading}</span></div>
    <div class="row"><span class="k">unseen:</span><span class="v">${stats.depths.unseen}</span></div>`;
}
function updateCard(word, d) {
  const card = document.getElementById('wc-' + word);
  if (card) card.classList.add('studied');
  const ws = document.getElementById('ws-' + word);
  if (ws) ws.textContent = d.depth + ' (' + (d.strength_after * 100).toFixed(0) + '%)';
}
init();
</script></body></html>"""
