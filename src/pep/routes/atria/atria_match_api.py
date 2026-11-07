"""HTTP API + playground for Atria Match."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from pep.atria.match import (
    AtriaMatcher,
    BehaviorFlag,
    CommStyle,
    ObjectiveWeights,
    Player,
    SessionGoal,
    run_builtin_eval,
)
from pep.atria.match.baseline import rank_by_elo

router = APIRouter()


# ── Pydantic models ─────────────────────────────────────────────────────
class PlayerBody(BaseModel):
    id: str
    rating: float = 1500.0
    uncertainty: float = 100.0
    tempo: float = Field(0.5, ge=0.0, le=1.0)
    tilt_tolerance: float = Field(0.5, ge=0.0, le=1.0)
    role_pref: str | None = None
    comm_style: str = "reactive"
    session_goal: str = "casual"
    behavior_flags: list[str] = []
    recent_matches: list[str] = []
    friends: list[str] = []
    blocked: list[str] = []


class RankBody(BaseModel):
    seed: PlayerBody
    candidates: list[PlayerBody]
    k: int = 5
    preset: str | None = None   # "ranked" / "casual" / "learning" / "esports"
    weights: dict[str, float] | None = None
    team_mode: bool = True


def _player_from_body(b: PlayerBody) -> Player:
    try:
        comm = CommStyle(b.comm_style)
    except ValueError:
        raise HTTPException(400, f"invalid comm_style: {b.comm_style}")
    try:
        goal = SessionGoal(b.session_goal)
    except ValueError:
        raise HTTPException(400, f"invalid session_goal: {b.session_goal}")
    flags: list[BehaviorFlag] = []
    for f in b.behavior_flags:
        try:
            flags.append(BehaviorFlag(f))
        except ValueError:
            raise HTTPException(400, f"invalid behavior_flag: {f}")
    return Player(
        id=b.id, rating=b.rating, uncertainty=b.uncertainty,
        tempo=b.tempo, tilt_tolerance=b.tilt_tolerance,
        role_pref=b.role_pref, comm_style=comm, session_goal=goal,
        behavior_flags=flags, recent_matches=b.recent_matches,
        friends=b.friends, blocked=b.blocked,
    )


def _serialize_result(r) -> dict[str, Any]:
    return {
        "candidate": {
            "id": r.candidate.id, "rating": r.candidate.rating,
            "tempo": r.candidate.tempo, "tilt_tolerance": r.candidate.tilt_tolerance,
            "comm_style": r.candidate.comm_style.value,
            "session_goal": r.candidate.session_goal.value,
            "behavior_flags": [f.value for f in r.candidate.behavior_flags],
            "role_pref": r.candidate.role_pref,
        },
        "overall_score": r.overall_score,
        "rematch_prob": r.rematch_prob,
        "elo_score": r.elo_score,
        "weakest_dimension": r.weakest_dimension,
        "strongest_dimension": r.strongest_dimension,
        "dimension_scores": {
            "skill": r.dimension_scores.skill,
            "tempo": r.dimension_scores.tempo,
            "communication": r.dimension_scores.communication,
            "role": r.dimension_scores.role,
            "tilt": r.dimension_scores.tilt,
            "goal": r.dimension_scores.goal,
            "behavior": r.dimension_scores.behavior,
        },
    }


@router.post("/atria/match-api/rank")
async def api_rank(body: RankBody) -> dict[str, Any]:
    if len(body.candidates) > 500:
        raise HTTPException(400, "max 500 candidates per request")
    seed = _player_from_body(body.seed)
    candidates = [_player_from_body(c) for c in body.candidates]
    # Build weights
    if body.preset:
        try:
            weights = ObjectiveWeights.preset(body.preset)
        except KeyError:
            raise HTTPException(400, f"unknown preset: {body.preset}")
    elif body.weights:
        weights = ObjectiveWeights(
            skill=body.weights.get("skill", 0.18),
            tempo=body.weights.get("tempo", 0.15),
            communication=body.weights.get("communication", 0.12),
            role=body.weights.get("role", 0.08),
            tilt=body.weights.get("tilt", 0.12),
            goal=body.weights.get("goal", 0.15),
            behavior=body.weights.get("behavior", 0.20),
        )
    else:
        weights = ObjectiveWeights()
    matcher = AtriaMatcher(weights=weights, team_mode=body.team_mode)
    atria = matcher.rank(seed, candidates, k=body.k)
    elo_picks = rank_by_elo(seed, candidates, k=body.k)
    elo_ids = [p.id for p in elo_picks]
    atria_ids = [r.candidate.id for r in atria]
    return {
        "seed_id": seed.id,
        "atria": [_serialize_result(r) for r in atria],
        "elo": [
            {"id": p.id, "rating": p.rating,
             "delta": round(abs(p.rating - seed.rating), 1)}
            for p in elo_picks
        ],
        "overlap": list(set(atria_ids) & set(elo_ids)),
        "only_atria": list(set(atria_ids) - set(elo_ids)),
        "only_elo": list(set(elo_ids) - set(atria_ids)),
        "weights": weights.as_dict(),
    }


@router.get("/atria/match-api/eval")
async def api_eval(n_pairs: int = 500) -> dict[str, Any]:
    n = max(50, min(2000, n_pairs))
    return run_builtin_eval(n_pairs=n)


# ── Playground UI ───────────────────────────────────────────────────────
_PAGE = """\
<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Atria Match Playground — live engine</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg: #0a1014; --surface: #141d24; --surface2: #101820;
    --text: #dcecec; --dim: #6b8088; --accent: #5eead4; --accent2: #a3e635;
    --warn: #fbbf24; --danger: #f06292; --border: #1f2c34;
  }
  body { font-family: 'SF Mono', monospace; background: var(--bg); color: var(--text); line-height: 1.6; }
  a { color: var(--accent); text-decoration: none; }
  a:hover { text-decoration: underline; }
  nav { position: sticky; top: 0; background: var(--bg); padding: 10px 20px;
        border-bottom: 1px solid var(--border); display: flex; gap: 14px;
        align-items: center; flex-wrap: wrap; z-index: 10; }
  .brand { font-size: 18px; font-weight: bold; color: var(--accent); }
  .badge { font-size: 9px; color: var(--accent); background: rgba(94,234,212,0.15);
           padding: 2px 8px; border-radius: 10px; letter-spacing: 0.05em; }
  .links { margin-left: auto; display: flex; gap: 14px; font-size: 11px; }
  .links a { color: var(--dim); }
  .links a:hover { color: var(--accent); }
  .layout { display: grid; grid-template-columns: 340px 1fr; min-height: calc(100vh - 50px); }
  .sidebar { background: var(--surface); border-right: 1px solid var(--border);
             padding: 18px; overflow-y: auto; }
  .main { padding: 18px 24px; overflow-y: auto; }
  .label { font-size: 10px; color: var(--dim); letter-spacing: 0.15em;
           text-transform: uppercase; margin-bottom: 8px; }
  .form-row { display: grid; grid-template-columns: 90px 1fr 38px; gap: 8px;
              align-items: center; margin-bottom: 6px; font-size: 10px; color: var(--dim); }
  select, input { background: var(--surface2); color: var(--text);
                  border: 1px solid var(--border); border-radius: 3px;
                  padding: 4px 8px; font-family: inherit; font-size: 11px; }
  input[type=range] { width: 100%; }
  input[type=number] { width: 70px; }
  button.btn { padding: 7px 14px; border-radius: 4px; border: 1px solid var(--accent);
               background: var(--accent); color: var(--bg); font-size: 11px;
               cursor: pointer; font-family: inherit; font-weight: bold; }
  button.alt { padding: 5px 10px; border-radius: 4px; border: 1px solid var(--border);
               background: transparent; color: var(--dim); font-size: 10px;
               cursor: pointer; font-family: inherit; }
  button.alt:hover { color: var(--text); border-color: var(--accent); }
  button.preset { padding: 4px 10px; border-radius: 12px; font-size: 10px;
                  border: 1px solid var(--border); background: var(--surface2);
                  color: var(--dim); cursor: pointer; font-family: inherit; }
  button.preset.active { background: var(--accent); color: var(--bg); border-color: var(--accent); font-weight: bold; }
  .preset-row { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px; }
  .v { color: var(--accent); font-weight: bold; text-align: right; }
  .compare-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
  .col { background: var(--surface); border: 1px solid var(--border);
         border-radius: 6px; overflow: hidden; }
  .col.atria { border-left: 3px solid var(--accent); }
  .col.elo { border-left: 3px solid #a78bfa; }
  .col-header { padding: 10px 14px; border-bottom: 1px solid var(--border);
                display: flex; justify-content: space-between; align-items: center; font-size: 12px; }
  .col.atria .col-header { color: var(--accent); font-weight: bold; }
  .col.elo .col-header { color: #a78bfa; font-weight: bold; }
  .match { padding: 10px 14px; border-bottom: 1px solid var(--border); font-size: 11px; }
  .match:last-child { border-bottom: none; }
  .match .id { font-weight: bold; color: var(--accent); font-family: monospace; }
  .match.unique { background: rgba(94,234,212,0.06); }
  .match .meta { color: var(--dim); font-size: 10px; margin-top: 3px; }
  .bars { margin-top: 6px; display: grid; grid-template-columns: 1fr 1fr; gap: 3px 10px; }
  .bar { display: flex; align-items: center; gap: 6px; font-size: 9px; color: var(--dim); }
  .bar .bar-fill { flex: 1; height: 6px; background: var(--surface2); border-radius: 3px; overflow: hidden; }
  .bar .bar-fill span { display: block; height: 100%; background: var(--accent); }
  .bar .bar-v { min-width: 24px; color: var(--text); text-align: right; }
  .summary { background: var(--surface); border: 1px solid var(--border);
             border-radius: 6px; padding: 14px 18px; margin-bottom: 14px; font-size: 11px; }
  .empty { text-align: center; padding: 40px 20px; color: var(--dim); font-size: 12px; }
  .eval-row { display: flex; gap: 14px; flex-wrap: wrap; background: var(--surface);
              border: 1px solid var(--accent); border-radius: 6px; padding: 14px 18px;
              margin-bottom: 14px; font-size: 11px; }
  .eval-row .metric { display: flex; gap: 6px; }
  .eval-row .metric .k { color: var(--dim); }
  .eval-row .metric .v { color: var(--accent); font-weight: bold; }
  .eval-row .metric .delta { color: var(--accent2); font-weight: bold; }
  @media (max-width: 900px) { .layout { grid-template-columns: 1fr; } .compare-grid { grid-template-columns: 1fr; } }
</style></head><body>
<nav>
  <span class="brand">Atria Match</span><span class="badge">LIVE ENGINE</span>
  <div class="links">
    <a href="/atria/match">Product</a>
    <a href="/atria">Atria</a>
    <a href="/pep">PEP</a>
  </div>
</nav>
<div class="layout">
  <div class="sidebar">
    <div class="label">1. Seed player</div>
    <div class="form-row"><span>rating</span><input id="seed-rating" type="number" value="1500"></div>
    <div class="form-row"><span>uncertainty</span><input id="seed-unc" type="number" value="100"></div>
    <div class="form-row"><span>tempo</span><input id="seed-tempo" type="range" min="0" max="1" step="0.01" value="0.5" oninput="showSliderVal('seed-tempo')"><span class="v" id="seed-tempo-v">0.50</span></div>
    <div class="form-row"><span>tilt tol</span><input id="seed-tilt" type="range" min="0" max="1" step="0.01" value="0.7" oninput="showSliderVal('seed-tilt')"><span class="v" id="seed-tilt-v">0.70</span></div>
    <div class="form-row"><span>comm</span><select id="seed-comm"><option>vocal</option><option selected>reactive</option><option>text</option><option>muted</option></select></div>
    <div class="form-row"><span>goal</span><select id="seed-goal"><option selected>casual</option><option>learning</option><option>grinding</option><option>competitive</option></select></div>

    <div class="label" style="margin-top:14px">2. Objective preset</div>
    <div class="preset-row">
      <button class="preset" data-preset="default" onclick="setPreset('default')">default</button>
      <button class="preset" data-preset="ranked" onclick="setPreset('ranked')">ranked</button>
      <button class="preset" data-preset="casual" onclick="setPreset('casual')">casual</button>
      <button class="preset" data-preset="learning" onclick="setPreset('learning')">learning</button>
      <button class="preset" data-preset="esports" onclick="setPreset('esports')">esports</button>
    </div>

    <div class="label" style="margin-top:10px">3. Pool size</div>
    <div class="form-row"><span>candidates</span><input id="pool-size" type="range" min="5" max="50" step="5" value="20" oninput="showSliderVal('pool-size', 0)"><span class="v" id="pool-size-v">20</span></div>
    <div class="form-row"><span>k</span><input id="k-size" type="range" min="3" max="10" value="5" oninput="showSliderVal('k-size', 0)"><span class="v" id="k-size-v">5</span></div>

    <div style="margin-top:16px"><button class="btn" onclick="run()" style="width:100%">Rank pool (Atria vs Elo)</button></div>

    <div class="label" style="margin-top:24px">Built-in eval</div>
    <div style="font-size:10px;color:var(--dim);line-height:1.6;margin-bottom:8px">500 synthetic labeled pairs. Measures AUC, precision@5, and the rate at which bad matches are ranked high.</div>
    <button class="alt" onclick="runEval()" style="width:100%">Run eval (500 pairs)</button>
  </div>
  <div class="main">
    <div id="eval-results"></div>
    <div id="content"><div class="empty">Configure the seed and click <b>Rank pool</b>.</div></div>
  </div>
</div>
<script>
let currentPreset = 'default';
function showSliderVal(id, digits=2) {
  const el = document.getElementById(id);
  const out = document.getElementById(id + '-v');
  if (!out) return;
  out.textContent = digits > 0 ? parseFloat(el.value).toFixed(digits) : el.value;
}
function setPreset(p) {
  currentPreset = p;
  document.querySelectorAll('.preset').forEach(b => b.classList.toggle('active', b.dataset.preset === p));
}
setPreset('default');

function esc(s) { return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }

// Random pool generation client-side
function randomPlayer(id) {
  const comms = ['vocal', 'text', 'muted', 'reactive'];
  const goals = ['casual', 'learning', 'grinding', 'competitive'];
  const flags = ['toxic', 'afk', 'throwing', 'leaver'];
  const roles = [null, 'tank', 'dps', 'support', 'flex'];
  const nRaw = Math.random();
  const bf = [];
  if (Math.random() < 0.15) bf.push(flags[Math.floor(Math.random() * flags.length)]);
  if (Math.random() < 0.04) bf.push(flags[Math.floor(Math.random() * flags.length)]);
  return {
    id,
    rating: Math.round(1500 + (nRaw - 0.5) * 600 + (Math.random() - 0.5) * 200),
    uncertainty: Math.max(50, Math.round(100 + (Math.random() - 0.5) * 100)),
    tempo: Math.max(0, Math.min(1, 0.5 + (Math.random() - 0.5))),
    tilt_tolerance: Math.max(0, Math.min(1, 0.5 + (Math.random() - 0.5))),
    comm_style: comms[Math.floor(Math.random() * comms.length)],
    session_goal: goals[Math.floor(Math.random() * goals.length)],
    role_pref: roles[Math.floor(Math.random() * roles.length)],
    behavior_flags: Array.from(new Set(bf)),
  };
}

async function run() {
  const poolSize = parseInt(document.getElementById('pool-size').value);
  const k = parseInt(document.getElementById('k-size').value);
  const seed = {
    id: 'seed',
    rating: parseFloat(document.getElementById('seed-rating').value),
    uncertainty: parseFloat(document.getElementById('seed-unc').value),
    tempo: parseFloat(document.getElementById('seed-tempo').value),
    tilt_tolerance: parseFloat(document.getElementById('seed-tilt').value),
    comm_style: document.getElementById('seed-comm').value,
    session_goal: document.getElementById('seed-goal').value,
  };
  const candidates = Array.from({length: poolSize}, (_, i) => randomPlayer(`c-${String(i).padStart(2, '0')}`));
  const body = { seed, candidates, k };
  if (currentPreset !== 'default') body.preset = currentPreset;
  try {
    const r = await fetch('/atria/match-api/rank', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(body),
    });
    if (!r.ok) throw new Error('rank failed');
    const data = await r.json();
    render(data, candidates);
  } catch (e) {
    document.getElementById('content').innerHTML = `<div class="empty" style="color:var(--danger)">Error: ${esc(e.message)}</div>`;
  }
}

function renderBars(scores) {
  const entries = [
    ['skill', scores.skill], ['tempo', scores.tempo],
    ['comm', scores.communication], ['role', scores.role],
    ['tilt', scores.tilt], ['goal', scores.goal],
    ['behavior', scores.behavior],
  ];
  return '<div class="bars">' + entries.map(([k, v]) =>
    `<div class="bar"><span style="width:50px">${k}</span><span class="bar-fill"><span style="width:${Math.round(v*100)}%"></span></span><span class="bar-v">${v.toFixed(2)}</span></div>`
  ).join('') + '</div>';
}

function render(data, candidates) {
  const candMap = Object.fromEntries(candidates.map(c => [c.id, c]));
  const atriaIds = new Set(data.atria.map(r => r.candidate.id));
  const eloIds = new Set(data.elo.map(p => p.id));

  const atriaHtml = data.atria.map((r, i) => {
    const unique = !eloIds.has(r.candidate.id);
    const c = r.candidate;
    const flags = c.behavior_flags.length ? `<span style="color:var(--danger);margin-left:8px">flags: ${c.behavior_flags.join(', ')}</span>` : '';
    return `<div class="match${unique ? ' unique' : ''}">
      <div><span style="color:var(--dim)">${i+1}.</span> <span class="id">${esc(c.id)}</span>
        <span style="color:var(--dim);margin-left:6px">rating ${c.rating.toFixed(0)}</span>
        <span style="color:var(--accent);font-weight:bold;margin-left:auto;float:right">overall ${r.overall_score.toFixed(3)}</span>
      </div>
      <div class="meta">rematch ${(r.rematch_prob * 100).toFixed(0)}%  ·  tempo ${c.tempo.toFixed(2)}  ·  tilt ${c.tilt_tolerance.toFixed(2)}  ·  ${c.comm_style}  ·  ${c.session_goal}${flags}</div>
      <div class="meta">strongest: <b style="color:var(--accent2)">${r.strongest_dimension}</b>  ·  weakest: <b style="color:var(--warn)">${r.weakest_dimension}</b></div>
      ${renderBars(r.dimension_scores)}
    </div>`;
  }).join('');

  const eloHtml = data.elo.map((p, i) => {
    const unique = !atriaIds.has(p.id);
    const full = candMap[p.id] || {};
    const flags = (full.behavior_flags || []).length ? `<span style="color:var(--danger);margin-left:8px">flags: ${(full.behavior_flags || []).join(', ')}</span>` : '';
    return `<div class="match${unique ? ' unique' : ''}">
      <div><span style="color:var(--dim)">${i+1}.</span> <span class="id" style="color:#a78bfa">${esc(p.id)}</span>
        <span style="color:var(--dim);margin-left:6px">rating ${p.rating.toFixed(0)}</span>
        <span style="color:#a78bfa;font-weight:bold;margin-left:auto;float:right">&Delta; ${p.delta}</span>
      </div>
      <div class="meta">${full.comm_style || '?'}  ·  ${full.session_goal || '?'}  ·  tilt ${(full.tilt_tolerance || 0).toFixed(2)}${flags}</div>
    </div>`;
  }).join('');

  document.getElementById('content').innerHTML = `
    <div class="summary">
      <b style="color:var(--accent)">Atria vs Elo on ${candidates.length}-player pool</b>
      <div style="margin-top:8px;color:var(--dim);line-height:1.7">
        <b style="color:var(--accent)">Overlap:</b> ${data.overlap.length} / ${data.atria.length}  ·
        <b style="color:var(--accent2)">Atria found (Elo missed):</b> ${data.only_atria.length}  ·
        <b style="color:var(--warn)">Elo found (Atria dropped):</b> ${data.only_elo.length}
      </div>
      <div style="margin-top:8px;color:var(--dim);font-size:10px">
        Weights: ${Object.entries(data.weights).map(([k, v]) => `${k} ${v.toFixed(2)}`).join('  ·  ')}
      </div>
    </div>
    <div class="compare-grid">
      <div class="col atria">
        <div class="col-header"><span>ATRIA MATCH (multi-objective)</span><span style="color:var(--dim);font-size:10px;font-weight:normal">${data.atria.length} results</span></div>
        ${atriaHtml}
      </div>
      <div class="col elo">
        <div class="col-header"><span>ELO BASELINE (rating-only)</span><span style="color:var(--dim);font-size:10px;font-weight:normal">${data.elo.length} results</span></div>
        ${eloHtml}
      </div>
    </div>`;
}

async function runEval() {
  const target = document.getElementById('eval-results');
  target.innerHTML = '<div class="eval-row">running 500-pair eval…</div>';
  try {
    const r = await fetch('/atria/match-api/eval?n_pairs=500');
    const d = await r.json();
    target.innerHTML = `<div class="eval-row">
      <div><b style="color:var(--accent)">Eval (${d.n_pairs} pairs):</b></div>
      <div class="metric"><span class="k">AUC:</span> <span class="v">Atria ${d.atria.auc}</span> <span style="color:var(--dim)">vs Elo ${d.elo.auc}</span> <span class="delta">+${d.atria_advantage.auc}</span></div>
      <div class="metric"><span class="k">P@5:</span> <span class="v">Atria ${d.atria.precision_at_5}</span> <span style="color:var(--dim)">vs Elo ${d.elo.precision_at_5}</span></div>
      <div class="metric"><span class="k">bad-match rate:</span> <span class="v">Atria ${d.atria.bad_match_rate}</span> <span style="color:var(--dim)">vs Elo ${d.elo.bad_match_rate}</span></div>
    </div>`;
  } catch (e) {
    target.innerHTML = `<div class="eval-row" style="color:var(--danger)">Eval failed</div>`;
  }
}

['seed-tempo', 'seed-tilt'].forEach(id => showSliderVal(id));
['pool-size', 'k-size'].forEach(id => showSliderVal(id, 0));
</script></body></html>
"""


@router.get("/atria/match/playground", response_class=HTMLResponse)
async def match_playground() -> str:
    return _PAGE
