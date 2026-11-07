"""HTTP APIs + playgrounds for Axona BCI, Clinic, Learn, Wellness."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from pep.axona import bci, clinic, learn, wellness

router = APIRouter()


# ═══ BCI ════════════════════════════════════════════════════════════════
class BCIBody(BaseModel):
    theta_alpha_ratio: float = 0.5
    beta_ratio: float = 0.5
    gamma_ratio: float = 0.3
    frontal_coherence: float = 0.5
    frontal_asymmetry: float = 0.0
    p300_amplitude: float = 0.5


@router.post("/axona/bci-api/interpret")
async def bci_interpret(body: BCIBody) -> dict[str, Any]:
    features = bci.SignalFeatures(**body.model_dump())
    return bci.interpret(features)


@router.get("/axona/bci-api/samples")
async def bci_samples() -> dict[str, Any]:
    return {k: bci.interpret(v) for k, v in bci.SAMPLE_READINGS.items()}


@router.get("/axona/bci/playground", response_class=HTMLResponse)
async def bci_playground() -> str:
    return _state_playground("Axona BCI SDK", "bci", "#ba68c8", "186,104,200",
        "Electrode signal features → cognitive state. Adjust the sliders to simulate raw EEG-style inputs.",
        [("theta_alpha", "Theta/Alpha ratio", 0, 100, 50, "drowsy↔alert"),
         ("beta", "Beta ratio", 0, 100, 50, "relaxed↔focused"),
         ("gamma", "Gamma ratio", 0, 100, 30, "low↔complex processing"),
         ("coherence", "Frontal coherence", 0, 100, 50, "fragmented↔integrated"),
         ("asymmetry", "Frontal asymmetry", -100, 100, 0, "withdrawal↔approach"),
         ("p300", "P300 amplitude", 0, 100, 50, "no surprise↔strong surprise")],
        "bci", [("flow","Flow state"),("fatigued","Fatigued"),("stressed","Stressed"),("relaxed","Relaxed"),("tilt","Tilt")])


# ═══ Clinic ═════════════════════════════════════════════════════════════
class ClinicBody(BaseModel):
    text: str


@router.post("/axona/clinic-api/analyze")
async def clinic_analyze(body: ClinicBody) -> dict[str, Any]:
    return clinic.analyze_session(body.text)


@router.get("/axona/clinic-api/samples")
async def clinic_samples() -> dict[str, Any]:
    return {k: {"text": v, "analysis": clinic.analyze_session(v)} for k, v in clinic.SAMPLE_NOTES.items()}


@router.get("/axona/clinic/playground", response_class=HTMLResponse)
async def clinic_playground() -> str:
    return _clinic_html()


# ═══ Learn ══════════════════════════════════════════════════════════════
_students: dict[str, learn.StudentProfile] = {}


def _get_student(session: str) -> learn.StudentProfile:
    if session not in _students:
        _students[session] = learn.make_student()
    return _students[session]


class LearnActionBody(BaseModel):
    session: str
    concept_id: str
    action: str  # "study" / "test_pass" / "test_fail" / "apply"


@router.post("/axona/learn-api/action")
async def learn_action(body: LearnActionBody) -> dict[str, Any]:
    sp = _get_student(body.session)
    c = sp.concepts.get(body.concept_id)
    if not c:
        return {"error": f"unknown concept: {body.concept_id}"}
    before = c.effective_strength()
    getattr(c, body.action)()
    after = c.effective_strength()
    return {
        "concept": c.name, "action": body.action,
        "strength_before": round(before, 4), "strength_after": round(after, 4),
        "depth": c.encoding_depth(),
        "half_life_hours": round(c.half_life_hours, 1),
        "stats": sp.stats(),
    }


@router.get("/axona/learn-api/concepts")
async def learn_concepts() -> dict[str, Any]:
    return {"concepts": [{"id": c.id, "name": c.name, "topic": c.topic} for c in learn.SAMPLE_CONCEPTS]}


@router.get("/axona/learn/playground", response_class=HTMLResponse)
async def learn_playground() -> str:
    return _learn_html()


# ═══ Wellness ═══════════════════════════════════════════════════════════
class WellnessBody(BaseModel):
    hrv_ms: float = 60
    resting_hr: float = 65
    sleep_hours: float = 7.5
    sleep_quality: float = 0.7
    activity_minutes: int = 30
    stress_events: int = 0
    screen_hours: float = 4
    caffeine_mg: float = 200


@router.post("/axona/wellness-api/report")
async def wellness_report(body: WellnessBody) -> dict[str, Any]:
    reading = wellness.BiometricReading(**body.model_dump())
    return wellness.wellness_report(reading)


@router.get("/axona/wellness-api/samples")
async def wellness_samples() -> dict[str, Any]:
    return {k: wellness.wellness_report(v) for k, v in wellness.SAMPLE_PROFILES.items()}


@router.get("/axona/wellness/playground", response_class=HTMLResponse)
async def wellness_playground() -> str:
    return _state_playground("Axona Wellness", "wellness", "#f06292", "240,98,146",
        "Biometric inputs → cognitive state. Adjust sliders to simulate a day's readings.",
        [("hrv", "HRV (ms)", 20, 100, 60, "stressed↔calm"),
         ("rhr", "Resting HR (bpm)", 45, 100, 65, "fit↔stressed"),
         ("sleep_h", "Sleep hours", 3, 10, 7, ""),
         ("sleep_q", "Sleep quality", 0, 100, 70, "poor↔excellent"),
         ("activity", "Activity (min)", 0, 90, 30, ""),
         ("stress", "Stress events", 0, 8, 0, ""),
         ("screen", "Screen hours", 0, 14, 4, ""),
         ("caffeine", "Caffeine (mg)", 0, 600, 200, "")],
        "wellness", [("well_rested","Well rested"),("sleep_deprived","Sleep deprived"),("active_morning","Active morning"),("burned_out","Burned out"),("weekend_chill","Weekend chill")])


# ═══ Shared state-playground template ═══════════════════════════════════
def _state_playground(title: str, product: str, accent: str, accent_rgb: str,
                       desc: str, sliders: list, api_prefix: str,
                       samples: list[tuple[str, str]]) -> str:
    slider_html = "".join(
        f'<div style="display:grid;grid-template-columns:130px 1fr 40px;gap:8px;align-items:center;margin-bottom:6px;font-size:10px;color:#aaa">'
        f'<span>{label}</span>'
        f'<input type="range" id="s-{sid}" min="{lo}" max="{hi}" value="{default}" oninput="updateSlider()">'
        f'<span id="sv-{sid}" style="color:{accent};font-weight:bold;text-align:right">{default}</span>'
        f'</div>'
        for sid, label, lo, hi, default, hint in sliders
    )
    sample_btns = "".join(
        f'<button onclick="loadSample(\'{key}\')" style="padding:4px 10px;border-radius:12px;border:1px solid #333;background:#1a1a1a;color:#ddd;font-size:10px;cursor:pointer;font-family:inherit">{label}</button>'
        for key, label in samples
    )
    slider_ids = [s[0] for s in sliders]
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} Playground</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'SF Mono', monospace; background: #0d0a14; color: #e0e0e0; line-height: 1.6; padding: 20px; }}
  nav {{ position: sticky; top: 0; background: #0d0a14; padding: 10px 0; border-bottom: 1px solid #2a2236;
        display: flex; gap: 14px; align-items: center; flex-wrap: wrap; margin: -20px -20px 20px; padding: 10px 20px; }}
  .brand {{ font-size: 18px; font-weight: bold; color: {accent}; }}
  .badge {{ font-size: 9px; color: {accent}; background: rgba({accent_rgb},0.15); padding: 2px 8px; border-radius: 10px; }}
  .links {{ margin-left: auto; display: flex; gap: 14px; font-size: 11px; }}
  .links a {{ color: #777; text-decoration: none; }}
  .container {{ max-width: 900px; margin: 0 auto; }}
  h2 {{ font-size: 16px; color: {accent}; margin-bottom: 12px; }}
  button.run {{ padding: 8px 16px; border-radius: 4px; border: 1px solid {accent}; background: {accent};
              color: #0d0a14; font-size: 11px; cursor: pointer; font-family: inherit; font-weight: bold; margin-top: 10px; }}
  .samples {{ display: flex; gap: 6px; flex-wrap: wrap; margin: 10px 0; }}
  .result {{ background: #1a1322; border: 1px solid #2a2236; border-radius: 6px; padding: 16px; margin-top: 14px; }}
  .axis {{ display: flex; gap: 10px; align-items: center; padding: 6px 0; font-size: 11px; }}
  .axis .name {{ min-width: 80px; color: {accent}; font-weight: bold; }}
  .axis .bar {{ flex: 1; height: 10px; background: #17101e; border-radius: 5px; overflow: hidden; }}
  .axis .bar span {{ display: block; height: 100%; border-radius: 5px; }}
  .axis .val {{ min-width: 36px; text-align: right; font-weight: bold; }}
  .alert {{ padding: 8px 12px; margin-top: 6px; border-radius: 4px; font-size: 11px; }}
  .alert.info {{ background: rgba(129,199,132,0.1); border-left: 3px solid #81c784; }}
  .alert.warning {{ background: rgba(255,183,77,0.1); border-left: 3px solid #ffb74d; }}
  .alert.critical {{ background: rgba(240,98,146,0.1); border-left: 3px solid #f06292; }}
</style></head><body>
<nav><span class="brand">{title}</span><span class="badge">LIVE ENGINE</span>
<div class="links"><a href="/axona/{product}">Product</a><a href="/axona">Axona</a><a href="/pep">PEP</a></div></nav>
<div class="container">
<h2>{desc}</h2>
<div class="samples">{sample_btns}</div>
{slider_html}
<button class="run" onclick="runAnalysis()">Analyze</button>
<div id="results"><div style="color:#777;text-align:center;padding:40px;font-size:11px">Adjust sliders and click Analyze.</div></div>
</div>
<script>
const sliderIds = {slider_ids};
const apiPrefix = '{api_prefix}';
function updateSlider() {{
  sliderIds.forEach(id => {{
    const el = document.getElementById('s-' + id);
    const out = document.getElementById('sv-' + id);
    if (el && out) out.textContent = el.value;
  }});
}}
async function loadSample(key) {{
  const r = await fetch('/axona/' + apiPrefix + '-api/samples');
  const data = await r.json();
  const sample = data[key];
  if (!sample) return;
  const features = sample.features || sample.inputs || {{}};
  const mapping = {{{', '.join(f'"{s[0]}": "{s[0]}"' for s in sliders)}}};
  // Try to map API field names to slider IDs
  const featureKeys = Object.keys(features);
  sliderIds.forEach((sid, i) => {{
    if (featureKeys[i] !== undefined) {{
      const el = document.getElementById('s-' + sid);
      if (el) {{
        let val = featureKeys[i] ? features[featureKeys[i]] : 0;
        // Scale to slider range
        const min = parseInt(el.min), max = parseInt(el.max);
        if (Math.abs(val) <= 1 && max > 10) val = val * (max - min) / 2 + (max + min) / 2;
        el.value = Math.round(val);
      }}
    }}
  }});
  updateSlider();
  renderResult(sample);
}}
async function runAnalysis() {{
  const vals = {{}};
  sliderIds.forEach(id => {{
    const el = document.getElementById('s-' + id);
    if (el) vals[id] = parseFloat(el.value);
  }});
  // Map slider IDs to API field names
  const endpoint = apiPrefix === 'bci' ? '/axona/bci-api/interpret' : '/axona/wellness-api/report';
  const body = apiPrefix === 'bci'
    ? {{ theta_alpha_ratio: vals.theta_alpha/100, beta_ratio: vals.beta/100, gamma_ratio: vals.gamma/100,
         frontal_coherence: vals.coherence/100, frontal_asymmetry: (vals.asymmetry || 0)/100, p300_amplitude: vals.p300/100 }}
    : {{ hrv_ms: vals.hrv || 60, resting_hr: vals.rhr || 65, sleep_hours: (vals.sleep_h || 75)/10,
         sleep_quality: (vals.sleep_q || 70)/100, activity_minutes: vals.activity || 30,
         stress_events: vals.stress || 0, screen_hours: vals.screen || 4, caffeine_mg: vals.caffeine || 200 }};
  const r = await fetch(endpoint, {{ method: 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify(body) }});
  const data = await r.json();
  renderResult(data);
}}
function renderResult(data) {{
  const s = data.state;
  const axes = [
    ['novelty', s.novelty, '{accent}'],
    ['coherence', s.coherence, '#67e8f9'],
    ['bandwidth', s.bandwidth, '#ffb74d'],
    ['valence', (s.valence + 1) / 2, s.valence >= 0 ? '#81c784' : '#f06292'],
  ];
  const barsHtml = axes.map(([name, val, col]) =>
    `<div class="axis"><span class="name">${{name}}</span><span class="bar"><span style="width:${{Math.round(val*100)}}%;background:${{col}}"></span></span><span class="val">${{name === 'valence' ? ((val*2-1).toFixed(2)) : val.toFixed(2)}}</span></div>`
  ).join('');
  const alertsHtml = (data.alerts || []).map(a =>
    `<div class="alert ${{a.level}}"><b>${{a.level.toUpperCase()}}:</b> ${{a.message}}<div style="color:#aaa;margin-top:3px;font-size:10px">${{a.recommendation}}</div></div>`
  ).join('');
  document.getElementById('results').innerHTML = `<div class="result">
    <div style="display:flex;justify-content:space-between;margin-bottom:10px"><b style="color:{accent}">Quadrant: ${{s.quadrant}}</b><span style="color:#aaa">Risk: ${{s.risk}}</span></div>
    ${{barsHtml}}
    <div style="margin-top:10px">${{alertsHtml}}</div>
  </div>`;
}}
updateSlider();
</script></body></html>"""


def _clinic_html() -> str:
    samples = "".join(
        f'<button onclick="loadNote(\'{k}\')" style="padding:4px 10px;border-radius:12px;border:1px solid #1f2c34;background:#141d24;color:#dcecec;font-size:10px;cursor:pointer;font-family:inherit">{k}</button>'
        for k in clinic.SAMPLE_NOTES
    )
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Axona Clinic Playground</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'SF Mono', monospace; background: #0a1014; color: #dcecec; line-height: 1.6; padding: 20px; }}
  nav {{ position: sticky; top: 0; background: #0a1014; padding: 10px 0; border-bottom: 1px solid #1f2c34;
        display: flex; gap: 14px; align-items: center; flex-wrap: wrap; margin: -20px -20px 20px; padding: 10px 20px; }}
  .brand {{ font-size: 18px; font-weight: bold; color: #4fc3f7; }}
  .badge {{ font-size: 9px; color: #4fc3f7; background: rgba(79,195,247,0.15); padding: 2px 8px; border-radius: 10px; }}
  .links {{ margin-left: auto; display: flex; gap: 14px; font-size: 11px; }}
  .links a {{ color: #6b8088; text-decoration: none; }}
  .container {{ max-width: 900px; margin: 0 auto; }}
  h2 {{ font-size: 16px; color: #4fc3f7; margin-bottom: 12px; }}
  textarea {{ width: 100%; min-height: 160px; background: #101820; color: #dcecec; border: 1px solid #1f2c34; border-radius: 4px; padding: 12px; font-family: inherit; font-size: 11px; resize: vertical; }}
  button.run {{ padding: 8px 16px; border-radius: 4px; border: 1px solid #4fc3f7; background: #4fc3f7;
              color: #0a1014; font-size: 11px; cursor: pointer; font-family: inherit; font-weight: bold; margin-top: 10px; }}
  .samples {{ display: flex; gap: 6px; flex-wrap: wrap; margin: 10px 0; }}
  .result {{ background: #141d24; border: 1px solid #1f2c34; border-radius: 6px; padding: 16px; margin-top: 14px; }}
  .axis {{ display: flex; gap: 10px; align-items: center; padding: 6px 0; font-size: 11px; }}
  .axis .name {{ min-width: 80px; color: #4fc3f7; font-weight: bold; }}
  .axis .bar {{ flex: 1; height: 10px; background: #101820; border-radius: 5px; overflow: hidden; }}
  .axis .bar span {{ display: block; height: 100%; border-radius: 5px; }}
  .axis .val {{ min-width: 36px; text-align: right; font-weight: bold; }}
  .alert {{ padding: 8px 12px; margin-top: 6px; border-radius: 4px; font-size: 11px; }}
  .alert.info {{ background: rgba(129,199,132,0.1); border-left: 3px solid #81c784; }}
  .alert.warning {{ background: rgba(255,183,77,0.1); border-left: 3px solid #ffb74d; }}
  .alert.critical {{ background: rgba(240,98,146,0.1); border-left: 3px solid #f06292; }}
</style></head><body>
<nav><span class="brand">Axona Clinic</span><span class="badge">LIVE ENGINE</span>
<div class="links"><a href="/axona/clinic">Product</a><a href="/axona">Axona</a><a href="/pep">PEP</a></div></nav>
<div class="container">
<h2>Session transcript → cognitive state mapping</h2>
<p style="font-size:11px;color:#6b8088;margin-bottom:12px">Paste a session note or click a sample. The engine detects keywords that signal novelty, coherence, bandwidth, and valence.</p>
<div class="samples">{samples}</div>
<textarea id="input" placeholder="Paste a session note..."></textarea>
<button class="run" onclick="runClinic()">Analyze session</button>
<div id="results"><div style="color:#6b8088;text-align:center;padding:40px;font-size:11px">Paste or pick a session note.</div></div>
</div>
<script>
const NOTES = {__import__('json').dumps(dict(clinic.SAMPLE_NOTES))};
function loadNote(k) {{ document.getElementById('input').value = NOTES[k] || ''; runClinic(); }}
async function runClinic() {{
  const text = document.getElementById('input').value.trim(); if (!text) return;
  const r = await fetch('/axona/clinic-api/analyze', {{ method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{text}}) }});
  const data = await r.json();
  const s = data.state;
  const axes = [['novelty',s.novelty,'#ba68c8'],['coherence',s.coherence,'#67e8f9'],['bandwidth',s.bandwidth,'#ffb74d'],['valence',(s.valence+1)/2,s.valence>=0?'#81c784':'#f06292']];
  const bars = axes.map(([n,v,c]) => `<div class="axis"><span class="name">${{n}}</span><span class="bar"><span style="width:${{Math.round(v*100)}}%;background:${{c}}"></span></span><span class="val">${{n==='valence'?((v*2-1).toFixed(2)):v.toFixed(2)}}</span></div>`).join('');
  const alerts = (data.alerts||[]).map(a => `<div class="alert ${{a.level}}"><b>${{a.level.toUpperCase()}}:</b> ${{a.message}}<div style="color:#aaa;margin-top:3px;font-size:10px">${{a.recommendation}}</div></div>`).join('');
  document.getElementById('results').innerHTML = `<div class="result"><div style="display:flex;justify-content:space-between;margin-bottom:10px"><b style="color:#4fc3f7">Quadrant: ${{s.quadrant}}</b><span style="color:#6b8088">Risk: ${{s.risk}}</span></div>${{bars}}<div style="margin-top:10px">${{alerts}}</div></div>`;
}}
</script></body></html>"""


def _learn_html() -> str:
    return """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Axona Learn Playground</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'SF Mono', monospace; background: #0a0e16; color: #e0e6ed; line-height: 1.6; }
  nav { position: sticky; top: 0; background: #0a0e16; padding: 10px 20px; border-bottom: 1px solid #2a3140;
        display: flex; gap: 14px; align-items: center; flex-wrap: wrap; }
  .brand { font-size: 18px; font-weight: bold; color: #81c784; }
  .badge { font-size: 9px; color: #81c784; background: rgba(129,199,132,0.15); padding: 2px 8px; border-radius: 10px; }
  .links { margin-left: auto; display: flex; gap: 14px; font-size: 11px; }
  .links a { color: #7a8492; text-decoration: none; }
  .layout { display: grid; grid-template-columns: 320px 1fr; min-height: calc(100vh - 50px); }
  .sidebar { background: #161c28; border-right: 1px solid #2a3140; padding: 18px; overflow-y: auto; }
  .main { padding: 18px 24px; }
  .label { font-size: 10px; color: #7a8492; letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 8px; }
  .concept { background: #0e1420; border: 1px solid #2a3140; border-left: 3px solid #2a3140;
             border-radius: 4px; padding: 10px 14px; margin-bottom: 6px; cursor: pointer; font-size: 11px; }
  .concept:hover { border-color: #81c784; }
  .concept.active { border-left-color: #81c784; background: rgba(129,199,132,0.05); }
  .concept .name { color: #81c784; font-weight: bold; }
  .concept .topic { color: #7a8492; font-size: 9px; }
  .concept .info { display: flex; justify-content: space-between; margin-top: 4px; font-size: 9px; color: #7a8492; }
  button { padding: 6px 14px; border-radius: 4px; font-family: inherit; font-size: 11px; cursor: pointer; }
  button.action { border: 1px solid #81c784; background: #81c784; color: #0a0e16; font-weight: bold; }
  button.test { border: 1px solid #4fc3f7; background: transparent; color: #4fc3f7; }
  button.fail { border: 1px solid #f06292; background: transparent; color: #f06292; }
  button.apply { border: 1px solid #ffb74d; background: transparent; color: #ffb74d; }
  .stats { background: #161c28; border: 1px solid #2a3140; border-radius: 6px; padding: 12px; font-size: 10px; margin-top: 14px; }
  .event { padding: 6px 10px; border-bottom: 1px solid #2a3140; font-size: 10px; }
  @media (max-width: 900px) { .layout { grid-template-columns: 1fr; } }
</style></head><body>
<nav><span class="brand">Axona Learn</span><span class="badge">LIVE ENGINE</span>
<div class="links"><a href="/axona/learn">Product</a><a href="/axona">Axona</a><a href="/pep">PEP</a></div></nav>
<div class="layout">
<div class="sidebar">
  <div class="label">Concepts (10 subjects)</div>
  <div id="concept-list"></div>
  <div id="stats-box" class="stats" style="display:none"></div>
</div>
<div class="main">
  <div id="detail"><div style="color:#7a8492;text-align:center;padding:40px;font-size:12px">Click a concept to study it.</div></div>
  <div class="label" style="margin-top:20px">Events</div>
  <div id="history" style="background:#161c28;border:1px solid #2a3140;border-radius:6px;max-height:300px;overflow-y:auto"><div style="padding:20px;color:#7a8492;text-align:center;font-size:11px">No events yet.</div></div>
</div>
</div>
<script>
const session = 'axlearn-' + Math.random().toString(36).slice(2, 8);
let concepts = [];
let currentId = null;
async function init() {
  const r = await fetch('/axona/learn-api/concepts');
  concepts = (await r.json()).concepts;
  renderList();
}
function renderList() {
  document.getElementById('concept-list').innerHTML = concepts.map(c =>
    `<div class="concept" id="cc-${c.id}" onclick="select('${c.id}')"><div class="name">${c.name}</div><div class="topic">${c.topic}</div><div class="info"><span id="cd-${c.id}">unseen</span><span id="cs-${c.id}">0%</span></div></div>`
  ).join('');
}
function select(id) {
  currentId = id;
  const c = concepts.find(x => x.id === id);
  if (!c) return;
  document.querySelectorAll('.concept').forEach(el => el.classList.remove('active'));
  const el = document.getElementById('cc-' + id);
  if (el) el.classList.add('active');
  document.getElementById('detail').innerHTML = `
    <div style="background:#161c28;border:1px solid #2a3140;border-radius:6px;padding:18px">
      <div style="font-size:16px;color:#81c784;font-weight:bold;margin-bottom:8px">${c.name}</div>
      <div style="font-size:11px;color:#7a8492;margin-bottom:14px">Topic: ${c.topic}</div>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <button class="action" onclick="doAction('${c.id}','study')">Study</button>
        <button class="test" onclick="doAction('${c.id}','test_pass')">Test ✓</button>
        <button class="fail" onclick="doAction('${c.id}','test_fail')">Test ✗</button>
        <button class="apply" onclick="doAction('${c.id}','apply')">Apply in context</button>
      </div>
    </div>`;
}
async function doAction(id, action) {
  const r = await fetch('/axona/learn-api/action', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({session, concept_id:id, action})});
  const d = await r.json();
  addEvent(d); updateStats(d.stats); updateCard(id, d);
}
function addEvent(d) {
  const hist = document.getElementById('history');
  if (hist.querySelector('div[style]')) hist.innerHTML = '';
  const colors = {study:'#81c784', test_pass:'#4fc3f7', test_fail:'#f06292', apply:'#ffb74d'};
  const div = document.createElement('div');
  div.className = 'event';
  div.innerHTML = `<b style="color:${colors[d.action] || '#aaa'}">${d.action}</b> ${d.concept} — strength ${d.strength_before}→${d.strength_after} · half-life ${d.half_life_hours}h · depth: ${d.depth}`;
  hist.insertBefore(div, hist.firstChild);
}
function updateStats(stats) {
  const box = document.getElementById('stats-box');
  box.style.display = 'block';
  box.innerHTML = Object.entries(stats.depths).map(([k,v]) => `<div style="display:flex;justify-content:space-between"><span style="color:#7a8492">${k}</span><span style="color:#81c784;font-weight:bold">${v}</span></div>`).join('') +
    `<div style="display:flex;justify-content:space-between;margin-top:6px;border-top:1px solid #2a3140;padding-top:6px"><span style="color:#7a8492">avg strength</span><span style="color:#81c784;font-weight:bold">${(stats.avg_strength*100).toFixed(0)}%</span></div>`;
}
function updateCard(id, d) {
  const cd = document.getElementById('cd-' + id);
  const cs = document.getElementById('cs-' + id);
  if (cd) cd.textContent = d.depth;
  if (cs) cs.textContent = (d.strength_after * 100).toFixed(0) + '%';
  const cc = document.getElementById('cc-' + id);
  if (cc) cc.classList.add('active');
}
init();
</script></body></html>"""
