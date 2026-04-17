"""HTTP API + playground endpoints for Atria Date, Hire, Found, Therapy.

Each product has a /rank endpoint and a /playground page, using the same
shape as the Atria Match API. The GenericMatcher in pep.atria.core
handles the ranking; each product supplies its own dimensions + seed data.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from pep.atria import date, found, hire, therapy
from pep.atria.core import GenericMatcher, RankResult

router = APIRouter()


# ── Cached matchers ─────────────────────────────────────────────────────
@lru_cache(maxsize=4)
def _date_matcher() -> GenericMatcher:
    return date.make_matcher()


@lru_cache(maxsize=4)
def _hire_matcher() -> GenericMatcher:
    return hire.make_matcher()


@lru_cache(maxsize=4)
def _found_matcher() -> GenericMatcher:
    return found.make_matcher()


@lru_cache(maxsize=4)
def _therapy_matcher() -> GenericMatcher:
    return therapy.make_matcher()


def _serialize(results: list[RankResult]) -> list[dict[str, Any]]:
    return [
        {
            "id": r.candidate_id,
            "overall": r.overall,
            "reengagement_prob": r.reengagement_prob,
            "dim_scores": r.dim_scores,
            "strongest": r.strongest,
            "weakest": r.weakest,
            "metadata": r.metadata,
        }
        for r in results
    ]


# ═══════════════════════════════════════════════════════════════════════
# Date
# ═══════════════════════════════════════════════════════════════════════
@router.get("/atria/date-api/rank/{seed_id}")
async def date_rank(seed_id: str, k: int = 6) -> dict[str, Any]:
    seed = next((p for p in date.SEED_PROFILES if p.id == seed_id), None)
    if seed is None:
        raise HTTPException(404, f"unknown seed: {seed_id}")
    candidates = [p for p in date.SEED_PROFILES if p.id != seed_id]
    results = _date_matcher().rank(seed, candidates, k=k)
    return {"seed": seed_id, "results": _serialize(results), "weights": date.DEFAULT_WEIGHTS}


@router.get("/atria/date-api/seeds")
async def date_seeds() -> dict[str, Any]:
    return {"seeds": [
        {
            "id": p.id,
            "label": p.metadata.get("label", p.id),
            "values": p.values,
            "warmth": p.warmth,
            "attachment": p.attachment,
            "conflict_style": p.conflict_style,
            "interests": p.interests,
            "life_stage": p.life_stage,
            "age": p.age,
        }
        for p in date.SEED_PROFILES
    ]}


@router.get("/atria/date/playground", response_class=HTMLResponse)
async def date_playground() -> str:
    return _date_playground()


# ═══════════════════════════════════════════════════════════════════════
# Hire
# ═══════════════════════════════════════════════════════════════════════
@router.get("/atria/hire-api/rank/{candidate_id}")
async def hire_rank(candidate_id: str, k: int = 8) -> dict[str, Any]:
    """Score one candidate against the seeded team."""
    cand = next((c for c in hire.SEED_CANDIDATES if c.id == candidate_id), None)
    if cand is None:
        raise HTTPException(404, f"unknown candidate: {candidate_id}")
    ds = _hire_matcher().score_pair(hire.SEED_TEAM, cand)
    ov = _hire_matcher().overall(ds)
    rp = _hire_matcher().reengagement(ov)
    return {
        "candidate": candidate_id,
        "team": hire.SEED_TEAM.id,
        "overall": round(ov, 4),
        "reengagement": rp,
        "dim_scores": {k: round(v, 4) for k, v in ds.items()},
    }


@router.get("/atria/hire-api/rank-all")
async def hire_rank_all(k: int = 8) -> dict[str, Any]:
    results = _hire_matcher().rank(hire.SEED_TEAM, hire.SEED_CANDIDATES, k=k)
    return {
        "team": {"id": hire.SEED_TEAM.id, "label": hire.SEED_TEAM.metadata.get("label", ""), "skills_needed": hire.SEED_TEAM.skills_needed},
        "results": _serialize(results),
        "weights": hire.DEFAULT_WEIGHTS,
    }


@router.get("/atria/hire-api/seeds")
async def hire_seeds() -> dict[str, Any]:
    return {
        "team": {"id": hire.SEED_TEAM.id, "skills_needed": hire.SEED_TEAM.skills_needed, "culture": hire.SEED_TEAM.culture},
        "candidates": [{"id": c.id, "label": c.metadata.get("label", c.id), "skills": c.skills} for c in hire.SEED_CANDIDATES],
    }


@router.get("/atria/hire/playground", response_class=HTMLResponse)
async def hire_playground() -> str:
    return _playground("Atria Hire", "hire", "#fbbf24", "251,191,36")


# ═══════════════════════════════════════════════════════════════════════
# Found
# ═══════════════════════════════════════════════════════════════════════
@router.get("/atria/found-api/rank/{seed_id}")
async def found_rank(seed_id: str, k: int = 6) -> dict[str, Any]:
    seed = next((p for p in found.SEED_PROFILES if p.id == seed_id), None)
    if seed is None:
        raise HTTPException(404, f"unknown seed: {seed_id}")
    candidates = [p for p in found.SEED_PROFILES if p.id != seed_id]
    results = _found_matcher().rank(seed, candidates, k=k)
    return {"seed": seed_id, "results": _serialize(results), "weights": found.DEFAULT_WEIGHTS}


@router.get("/atria/found-api/seeds")
async def found_seeds() -> dict[str, Any]:
    return {"seeds": [{"id": p.id, "label": p.metadata.get("label", p.id)} for p in found.SEED_PROFILES]}


@router.get("/atria/found/playground", response_class=HTMLResponse)
async def found_playground() -> str:
    return _playground("Atria Found", "found", "#a78bfa", "167,139,250")


# ═══════════════════════════════════════════════════════════════════════
# Therapy
# ═══════════════════════════════════════════════════════════════════════
@router.get("/atria/therapy-api/rank")
async def therapy_rank(k: int = 6) -> dict[str, Any]:
    results = _therapy_matcher().rank(therapy.SEED_PATIENT, therapy.SEED_THERAPISTS, k=k)
    return {
        "patient": {"id": therapy.SEED_PATIENT.id, "label": therapy.SEED_PATIENT.metadata.get("label", "")},
        "results": _serialize(results),
        "weights": therapy.DEFAULT_WEIGHTS,
    }


@router.get("/atria/therapy-api/seeds")
async def therapy_seeds() -> dict[str, Any]:
    return {
        "patient": {"id": therapy.SEED_PATIENT.id, "label": therapy.SEED_PATIENT.metadata.get("label", "")},
        "therapists": [{"id": t.id, "label": t.metadata.get("label", t.id)} for t in therapy.SEED_THERAPISTS],
    }


@router.get("/atria/therapy/playground", response_class=HTMLResponse)
async def therapy_playground() -> str:
    return _playground("Atria Therapy", "therapy", "#67e8f9", "103,232,249")


# ═══════════════════════════════════════════════════════════════════════
# Shared playground template
# ═══════════════════════════════════════════════════════════════════════
def _date_playground() -> str:
    return """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Atria Date Playground — live engine</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  :root { --bg: #100a10; --surface: #1c1220; --surface2: #170e1a;
           --text: #eddce8; --dim: #8a6a80; --accent: #ec4899; --accent2: #a3e635; --border: #2e1a2a; }
  body { font-family: 'SF Mono', monospace; background: var(--bg); color: var(--text); line-height: 1.6; }
  a { color: var(--accent); text-decoration: none; }
  a:hover { text-decoration: underline; }
  nav { position: sticky; top: 0; background: var(--bg); padding: 10px 20px;
        border-bottom: 1px solid var(--border); display: flex; gap: 14px;
        align-items: center; flex-wrap: wrap; z-index: 10; }
  .brand { font-size: 18px; font-weight: bold; color: var(--accent); }
  .badge { font-size: 9px; color: var(--accent); background: rgba(236,72,153,0.15);
           padding: 2px 8px; border-radius: 10px; letter-spacing: 0.05em; }
  .links { margin-left: auto; display: flex; gap: 14px; font-size: 11px; }
  .links a { color: var(--dim); }
  .links a:hover { color: var(--accent); }
  .layout { display: grid; grid-template-columns: 380px 1fr; min-height: calc(100vh - 50px); }
  .sidebar { background: var(--surface); border-right: 1px solid var(--border); padding: 18px; overflow-y: auto; }
  .main { padding: 18px 24px; overflow-y: auto; }
  .label { font-size: 10px; color: var(--dim); letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 8px; }
  select { width: 100%; background: var(--surface2); color: var(--text); border: 1px solid var(--border);
           border-radius: 4px; padding: 8px 10px; font-family: inherit; font-size: 11px; }
  button.btn { padding: 8px 16px; border-radius: 4px; border: 1px solid var(--accent);
               background: var(--accent); color: var(--bg); font-size: 11px;
               cursor: pointer; font-family: inherit; font-weight: bold; width: 100%; margin-top: 14px; }
  .profile-card { background: var(--surface2); border: 1px solid var(--border); border-radius: 6px;
                  padding: 14px; margin-top: 12px; font-size: 11px; }
  .profile-card .attr { display: flex; justify-content: space-between; padding: 4px 0;
                        border-bottom: 1px solid var(--border); }
  .profile-card .attr:last-child { border-bottom: none; }
  .profile-card .attr .k { color: var(--dim); }
  .profile-card .attr .v { color: var(--text); font-weight: bold; }
  .dim-legend { background: var(--surface2); border: 1px solid var(--border); border-radius: 6px;
                padding: 12px 14px; margin-top: 14px; font-size: 10px; line-height: 1.8; }
  .dim-legend b { color: var(--accent); }
  .dim-legend .desc { color: var(--dim); }
  .result { background: var(--surface); border: 1px solid var(--border); border-left: 3px solid var(--accent);
            border-radius: 6px; padding: 14px 18px; margin-bottom: 10px; }
  .result .header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px; }
  .result .id { color: var(--accent); font-weight: bold; font-family: monospace; font-size: 13px; }
  .result .label-text { color: var(--text); font-size: 11px; margin-left: 6px; }
  .result .overall { color: var(--accent); font-weight: bold; font-size: 16px; }
  .result .dims { display: grid; grid-template-columns: 1fr 1fr; gap: 4px 16px; font-size: 10px; margin-top: 6px; }
  .result .dim { display: flex; gap: 8px; align-items: center; }
  .result .dim .name { color: var(--dim); min-width: 70px; }
  .result .dim .bar-bg { flex: 1; height: 8px; background: var(--surface2); border-radius: 4px; overflow: hidden; }
  .result .dim .bar-fill { height: 100%; border-radius: 4px; }
  .result .dim .val { color: var(--text); min-width: 30px; text-align: right; font-weight: bold; }
  .result .meta { font-size: 10px; color: var(--dim); margin-top: 8px; }
  .empty { text-align: center; padding: 40px 20px; color: var(--dim); font-size: 12px; }
  @media (max-width: 900px) { .layout { grid-template-columns: 1fr; } }
</style></head><body>
<nav>
  <span class="brand">Atria Date</span><span class="badge">LIVE ENGINE</span>
  <div class="links">
    <a href="/atria/date">Product page</a>
    <a href="/atria/match/playground">Match Playground</a>
    <a href="/atria">Atria</a>
    <a href="/pep">PEP</a>
  </div>
</nav>
<div class="layout">
  <div class="sidebar">
    <div class="label">1. Pick your profile</div>
    <select id="seed-select" onchange="showProfile()"><option>loading…</option></select>
    <div id="profile-view" class="profile-card" style="display:none"></div>
    <button class="btn" onclick="runRank()">Find matches</button>

    <div class="label" style="margin-top:22px">What the dimensions mean</div>
    <div class="dim-legend">
      <div><b>values</b> <span class="desc">— overlap of core life values (family, adventure, career, independence, community, creativity). Higher = more shared values.</span></div>
      <div><b>warmth</b> <span class="desc">— emotional expressiveness match. 0 = reserved, 1 = very warm. Similar warmth levels feel natural; large gaps feel overwhelming or cold.</span></div>
      <div><b>attachment</b> <span class="desc">— attachment style compatibility. Secure (0.5) pairs well with everything. Avoidant + anxious is the hardest combination. Based on attachment theory.</span></div>
      <div><b>conflict</b> <span class="desc">— how you handle disagreements. Compromise + compromise = best. Confronting + avoidant = worst. Based on Gottman's research.</span></div>
      <div><b>interests</b> <span class="desc">— shared hobbies and activities. At least 1 shared interest is needed for a baseline score; 3+ approaches maximum.</span></div>
      <div><b>life_stage</b> <span class="desc">— where you are in life (student / early-career / established / retired). Adjacent stages are compatible; 2+ gaps cause friction.</span></div>
    </div>
  </div>
  <div class="main">
    <h2 style="font-size:16px;color:var(--accent);margin-bottom:12px">Your matches</h2>
    <div id="results"><div class="empty">Pick a profile and click <b>Find matches</b>.</div></div>
  </div>
</div>
<script>
let allSeeds = [];
async function init() {
  const r = await fetch('/atria/date-api/seeds');
  const data = await r.json();
  allSeeds = data.seeds;
  const sel = document.getElementById('seed-select');
  sel.innerHTML = allSeeds.map(s => `<option value="${s.id}">${s.id} — ${s.label}</option>`).join('');
  showProfile();
}
function showProfile() {
  const id = document.getElementById('seed-select').value;
  const p = allSeeds.find(s => s.id === id);
  const view = document.getElementById('profile-view');
  if (!p) { view.style.display = 'none'; return; }
  view.style.display = 'block';
  const attachLabels = { '0': 'avoidant', '0.5': 'secure', '1': 'anxious' };
  const attachLabel = p.attachment <= 0.25 ? 'avoidant' : p.attachment >= 0.65 ? 'anxious' : 'secure';
  view.innerHTML = `
    <div class="attr"><span class="k">age</span><span class="v">${p.age}</span></div>
    <div class="attr"><span class="k">values</span><span class="v">${p.values.join(', ')}</span></div>
    <div class="attr"><span class="k">warmth</span><span class="v">${p.warmth.toFixed(2)} (${p.warmth > 0.6 ? 'warm' : p.warmth < 0.4 ? 'reserved' : 'moderate'})</span></div>
    <div class="attr"><span class="k">attachment</span><span class="v">${p.attachment.toFixed(2)} (${attachLabel})</span></div>
    <div class="attr"><span class="k">conflict style</span><span class="v">${p.conflict_style}</span></div>
    <div class="attr"><span class="k">interests</span><span class="v">${p.interests.join(', ')}</span></div>
    <div class="attr"><span class="k">life stage</span><span class="v">${p.life_stage}</span></div>
  `;
}
function esc(s) { return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
const DIM_COLORS = {
  values: '#ec4899', warmth: '#f59e0b', attachment: '#a78bfa',
  conflict: '#67e8f9', interests: '#a3e635', life_stage: '#f06292',
};
async function runRank() {
  const seed = document.getElementById('seed-select').value;
  const r = await fetch(`/atria/date-api/rank/${seed}?k=8`);
  const data = await r.json();
  const out = document.getElementById('results');
  if (!data.results.length) { out.innerHTML = '<div class="empty">No matches.</div>'; return; }
  out.innerHTML = data.results.map((r, i) => {
    const label = r.metadata?.label ? `<span class="label-text">${esc(r.metadata.label)}</span>` : '';
    const dims = Object.entries(r.dim_scores).map(([k, v]) => {
      const col = DIM_COLORS[k] || '#ec4899';
      return `<div class="dim"><span class="name">${k}</span><span class="bar-bg"><span class="bar-fill" style="width:${Math.round(v*100)}%;background:${col}"></span></span><span class="val">${(v*100).toFixed(0)}</span></div>`;
    }).join('');
    return `<div class="result">
      <div class="header">
        <div><span style="color:var(--dim)">${i+1}.</span> <span class="id">${esc(r.id)}</span>${label}</div>
        <div class="overall">${(r.overall * 100).toFixed(0)}%</div>
      </div>
      <div style="font-size:11px;color:var(--accent);margin-bottom:6px">re-engagement: <b>${(r.reengagement_prob * 100).toFixed(0)}%</b> predicted</div>
      <div class="dims">${dims}</div>
      <div class="meta">strongest: <b style="color:var(--accent2)">${r.strongest}</b> · weakest: <b style="color:#fbbf24">${r.weakest}</b></div>
    </div>`;
  }).join('');
}
init();
</script></body></html>"""


def _playground(title: str, product: str, accent: str, accent_rgb: str) -> str:
    """Generate a playground page for one Atria product."""
    # Determine which API shape to use
    is_hire = product == "hire"
    is_therapy = product == "therapy"
    seed_api = f"/atria/{product}-api/seeds"
    rank_api = (
        f"/atria/{product}-api/rank-all" if is_hire
        else f"/atria/{product}-api/rank" if is_therapy
        else f"/atria/{product}-api/rank/"
    )
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} Playground — live engine</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{ --bg: #0a0e14; --surface: #141a22; --surface2: #0f141c;
           --text: #dce4ed; --dim: #6a7a8a; --accent: {accent}; --border: #1f2c34; }}
  body {{ font-family: 'SF Mono', monospace; background: var(--bg); color: var(--text); line-height: 1.6; padding: 20px; }}
  nav {{ position: sticky; top: 0; background: var(--bg); padding: 10px 0;
        border-bottom: 1px solid var(--border); display: flex; gap: 14px;
        align-items: center; flex-wrap: wrap; margin: -20px -20px 20px; padding: 10px 20px; z-index: 10; }}
  .brand {{ font-size: 18px; font-weight: bold; color: var(--accent); }}
  .badge {{ font-size: 9px; color: var(--accent); background: rgba({accent_rgb}, 0.15);
           padding: 2px 8px; border-radius: 10px; letter-spacing: 0.05em; }}
  .links {{ margin-left: auto; display: flex; gap: 14px; font-size: 11px; }}
  .links a {{ color: var(--dim); text-decoration: none; }}
  .links a:hover {{ color: var(--accent); }}
  .container {{ max-width: 900px; margin: 0 auto; }}
  h2 {{ font-size: 16px; color: var(--accent); margin-bottom: 12px; }}
  .desc {{ font-size: 11px; color: var(--dim); line-height: 1.7; margin-bottom: 16px; }}
  select {{ background: var(--surface2); color: var(--text); border: 1px solid var(--border);
           border-radius: 4px; padding: 6px 10px; font-family: inherit; font-size: 11px; min-width: 240px; }}
  button {{ padding: 7px 14px; border-radius: 4px; border: 1px solid var(--accent);
           background: var(--accent); color: var(--bg); font-size: 11px;
           cursor: pointer; font-family: inherit; font-weight: bold; }}
  .controls {{ display: flex; gap: 10px; flex-wrap: wrap; align-items: center; margin-bottom: 16px; }}
  .result {{ background: var(--surface); border: 1px solid var(--border); border-left: 3px solid var(--accent);
            border-radius: 6px; padding: 14px 18px; margin-bottom: 10px; }}
  .result .rank {{ color: var(--dim); font-size: 10px; }}
  .result .id {{ color: var(--accent); font-weight: bold; font-family: monospace; font-size: 12px; }}
  .result .label {{ color: var(--text); font-size: 11px; margin-left: 6px; }}
  .result .scores {{ font-size: 10px; color: var(--dim); margin-top: 6px; line-height: 1.8; }}
  .result .overall {{ color: var(--accent); font-weight: bold; font-size: 14px; float: right; }}
  .result .bar {{ display: inline-block; height: 6px; border-radius: 3px; margin-left: 4px; vertical-align: middle; }}
  .empty {{ text-align: center; padding: 40px; color: var(--dim); font-size: 12px; }}
  @media (max-width: 700px) {{ .container {{ padding: 10px; }} }}
</style></head><body>
<nav>
  <span class="brand">{title}</span><span class="badge">LIVE ENGINE</span>
  <div class="links">
    <a href="/atria/{product}">Product</a>
    <a href="/atria/match/playground">Match Playground</a>
    <a href="/atria">Atria</a>
    <a href="/pep">PEP</a>
  </div>
</nav>
<div class="container">
  <h2>{title} — multi-dimensional compatibility ranking</h2>
  <p class="desc">Pick a seed {'(patient profile is fixed)' if is_therapy else '(team is fixed)' if is_hire else 'from the dropdown'}. The engine scores {'all candidates against the team' if is_hire else 'all therapists against the patient' if is_therapy else 'every other profile against it'} across {'6' if not is_hire else '6'} dimensions, returns the ranking with per-dimension breakdowns.</p>
  <div class="controls">
    {'<span style="font-size:11px;color:var(--dim)">seed: fixed patient profile</span>' if is_therapy else '<span style="font-size:11px;color:var(--dim)">seed: fixed team (needs ML + data-eng + security)</span>' if is_hire else '<select id="seed-select"><option>loading…</option></select>'}
    <button onclick="runRank()">Rank</button>
  </div>
  <div id="results"><div class="empty">Click Rank to see results.</div></div>
</div>
<script>
const product = '{product}';
const isHire = {'true' if is_hire else 'false'};
const isTherapy = {'true' if is_therapy else 'false'};
async function init() {{
  if (isHire || isTherapy) return;
  const r = await fetch('{seed_api}');
  const data = await r.json();
  const seeds = data.seeds;
  const sel = document.getElementById('seed-select');
  if (!sel) return;
  sel.innerHTML = seeds.map(s => `<option value="${{s.id}}">${{s.id}} — ${{s.label}}</option>`).join('');
}}
function esc(s) {{ return String(s).replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c])); }}
function bar(v) {{ return `<span class="bar" style="width:${{Math.round(v * 80)}}px;background:rgba({accent_rgb}, ${{0.4 + v * 0.6}})"></span>`; }}
async function runRank() {{
  let url = '{rank_api}';
  if (!isHire && !isTherapy) {{
    const sel = document.getElementById('seed-select');
    url += sel.value + '?k=8';
  }} else {{
    url += '?k=8';
  }}
  try {{
    const r = await fetch(url);
    if (!r.ok) throw new Error('rank failed');
    const data = await r.json();
    const results = data.results;
    const html = results.map((r, i) => {{
      const dims = Object.entries(r.dim_scores).map(([k, v]) =>
        `<b style="color:var(--text)">${{k}}</b> ${{v.toFixed(2)}} ${{bar(v)}}`
      ).join('&nbsp;&nbsp;');
      const label = r.metadata?.label ? `<span class="label">${{esc(r.metadata.label)}}</span>` : '';
      return `<div class="result">
        <div><span class="overall">${{(r.overall * 100).toFixed(0)}}% · re-engage ${{(r.reengagement_prob * 100).toFixed(0)}}%</span>
        <span class="rank">#${{i + 1}}</span> <span class="id">${{esc(r.id)}}</span>${{label}}</div>
        <div class="scores">${{dims}}</div>
        <div class="scores" style="margin-top:4px">strongest: <b style="color:rgba({accent_rgb}, 1)">${{r.strongest}}</b> · weakest: <b style="color:var(--dim)">${{r.weakest}}</b></div>
      </div>`;
    }}).join('');
    document.getElementById('results').innerHTML = html || '<div class="empty">No results.</div>';
  }} catch (e) {{
    document.getElementById('results').innerHTML = `<div class="empty" style="color:#f06292">Error: ${{esc(e.message)}}</div>`;
  }}
}}
init();
</script></body></html>"""
