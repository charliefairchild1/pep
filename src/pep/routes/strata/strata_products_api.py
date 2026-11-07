"""HTTP APIs + playgrounds for all Strata verticals."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from pep.strata import core, equities, crypto, fx, commodities, predict, bonds

router = APIRouter()

VERTICALS = {
    "equities": {"assets": equities.ASSETS, "label": "Equities", "accent": "#e879f9", "rgb": "232,121,249"},
    "crypto": {"assets": crypto.ASSETS, "label": "Crypto", "accent": "#fbbf24", "rgb": "251,191,36"},
    "fx": {"assets": fx.ASSETS, "label": "FX", "accent": "#67e8f9", "rgb": "103,232,249"},
    "commodities": {"assets": commodities.ASSETS, "label": "Commodities", "accent": "#fb7185", "rgb": "251,113,133"},
    "predict": {"assets": predict.ASSETS, "label": "Prediction Markets", "accent": "#a3e635", "rgb": "163,230,53"},
    "bonds": {"assets": bonds.ASSETS, "label": "Fixed Income", "accent": "#94a3b8", "rgb": "148,163,184"},
}


class ScoreBody(BaseModel):
    asset_id: str
    price_change_pct: float
    relative_volume: float = 1.0
    persistence: float = 0.5
    catalyst: str = ""


@router.post("/strata/{vertical}-api/score")
async def score_move(vertical: str, body: ScoreBody) -> dict[str, Any]:
    if vertical not in VERTICALS:
        raise HTTPException(404, f"unknown vertical: {vertical}")
    signal = core.MoveSignal(
        asset_id=body.asset_id,
        price_change_pct=body.price_change_pct,
        relative_volume=body.relative_volume,
        persistence=body.persistence,
        catalyst=body.catalyst,
    )
    result = core.score_move(signal)
    return {
        "asset_id": result.asset_id,
        "unusual_score": result.unusual_score,
        "label": result.label,
        "classification": result.classification,
        "explanation": result.explanation,
        "components": result.components,
    }


@router.get("/strata/{vertical}-api/assets")
async def get_assets(vertical: str) -> dict[str, Any]:
    if vertical not in VERTICALS:
        raise HTTPException(404, f"unknown vertical: {vertical}")
    v = VERTICALS[vertical]
    return {
        "vertical": vertical,
        "label": v["label"],
        "assets": [
            {"id": a.id, "name": a.name, "sector": a.sector, "description": a.description}
            for a in v["assets"]
        ],
    }


@router.get("/strata/{vertical}/playground", response_class=HTMLResponse)
async def vertical_playground(vertical: str) -> str:
    if vertical not in VERTICALS:
        raise HTTPException(404, f"unknown vertical: {vertical}")
    v = VERTICALS[vertical]
    return _playground(vertical, v["label"], v["accent"], v["rgb"])


def _playground(vertical: str, label: str, accent: str, accent_rgb: str) -> str:
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Strata {label} Playground</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'SF Mono', monospace; background: #0c0a14; color: #e8dce8; line-height: 1.6; padding: 20px; }}
  nav {{ position: sticky; top: 0; background: #0c0a14; padding: 10px 0; border-bottom: 1px solid #2a2236;
        display: flex; gap: 14px; align-items: center; flex-wrap: wrap; margin: -20px -20px 20px; padding: 10px 20px; }}
  .brand {{ font-size: 18px; font-weight: bold; color: {accent}; }}
  .badge {{ font-size: 9px; color: {accent}; background: rgba({accent_rgb},0.15); padding: 2px 8px; border-radius: 10px; }}
  .links {{ margin-left: auto; display: flex; gap: 14px; font-size: 11px; }}
  .links a {{ color: #7a708a; text-decoration: none; }}
  .container {{ max-width: 900px; margin: 0 auto; }}
  h2 {{ font-size: 16px; color: {accent}; margin-bottom: 12px; }}
  .desc {{ font-size: 11px; color: #7a708a; line-height: 1.7; margin-bottom: 16px; }}
  select, input {{ background: #181423; color: #e8dce8; border: 1px solid #2a2236; border-radius: 4px;
                  padding: 8px 10px; font-family: inherit; font-size: 11px; }}
  select {{ min-width: 220px; }}
  button {{ padding: 8px 16px; border-radius: 4px; border: 1px solid {accent}; background: {accent};
           color: #0c0a14; font-size: 11px; cursor: pointer; font-family: inherit; font-weight: bold; }}
  .form {{ display: grid; grid-template-columns: 120px 1fr; gap: 8px 14px; align-items: center;
          font-size: 11px; color: #7a708a; margin-bottom: 14px; }}
  .form input {{ width: 100%; }}
  .result {{ background: #181423; border: 1px solid #2a2236; border-radius: 6px; padding: 16px; margin-top: 14px; }}
  .score-big {{ font-size: 32px; font-weight: bold; text-align: center; margin: 10px 0; }}
  .label-tag {{ display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 10px;
               font-weight: bold; letter-spacing: 0.1em; }}
  .label-tag.normal {{ background: rgba(103,232,249,0.15); color: #67e8f9; }}
  .label-tag.notable {{ background: rgba(251,191,36,0.15); color: #fbbf24; }}
  .label-tag.unusual {{ background: rgba(240,98,146,0.15); color: #f06292; }}
  .label-tag.extreme {{ background: rgba(239,68,68,0.15); color: #ef4444; }}
  .comp {{ display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-top: 12px; }}
  .comp-item {{ font-size: 10px; display: flex; justify-content: space-between; padding: 4px 8px;
               background: #0c0a14; border-radius: 3px; }}
  .comp-item .k {{ color: #7a708a; }}
  .comp-item .v {{ color: {accent}; font-weight: bold; }}
</style></head><body>
<nav><span class="brand">Strata {label}</span><span class="badge">LIVE ENGINE</span>
<div class="links"><a href="/strata/{vertical}">Product</a><a href="/strata">Strata</a><a href="/pep">PEP</a></div></nav>
<div class="container">
<h2>Score a move in the {label} vertical</h2>
<p class="desc">Pick an asset or type your own ID. Enter the move parameters. The engine runs the universal unusual-score formula (35% price + 25% volume + 25% vol-adjusted + 15% persistence) and classifies the move into an archetype.</p>
<div class="form">
  <span>Asset</span><select id="asset"><option>loading…</option></select>
  <span>Price change %</span><input id="pct" type="number" value="5" step="0.5">
  <span>Relative volume</span><input id="rvol" type="number" value="2.5" step="0.5" min="0.1">
  <span>Persistence [0-1]</span><input id="persist" type="number" value="0.6" step="0.1" min="0" max="1">
  <span>Catalyst</span><input id="catalyst" type="text" placeholder="optional news/event description">
</div>
<button onclick="runScore()">Score this move</button>
<div id="results"><div style="color:#7a708a;text-align:center;padding:40px;font-size:11px">Enter a move and click Score.</div></div>
</div>
<script>
async function init() {{
  const r = await fetch('/strata/{vertical}-api/assets');
  const data = await r.json();
  const sel = document.getElementById('asset');
  sel.innerHTML = data.assets.map(a => `<option value="${{a.id}}">${{a.id}} — ${{a.name}} (${{a.sector}})</option>`).join('');
}}
function esc(s) {{ return String(s).replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c])); }}
async function runScore() {{
  const body = {{
    asset_id: document.getElementById('asset').value,
    price_change_pct: parseFloat(document.getElementById('pct').value),
    relative_volume: parseFloat(document.getElementById('rvol').value),
    persistence: parseFloat(document.getElementById('persist').value),
    catalyst: document.getElementById('catalyst').value,
  }};
  const r = await fetch('/strata/{vertical}-api/score', {{
    method: 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify(body),
  }});
  const d = await r.json();
  const labelCol = {{normal:'#67e8f9', notable:'#fbbf24', unusual:'#f06292', extreme:'#ef4444'}}[d.label] || '#fff';
  const comps = Object.entries(d.components).map(([k,v]) =>
    `<div class="comp-item"><span class="k">${{k}}</span><span class="v">${{v.toFixed(1)}}</span></div>`
  ).join('');
  document.getElementById('results').innerHTML = `<div class="result">
    <div style="text-align:center"><span class="label-tag ${{d.label}}">${{d.label.toUpperCase()}}</span></div>
    <div class="score-big" style="color:${{labelCol}}">${{d.unusual_score}}</div>
    <div style="text-align:center;color:{accent};font-weight:bold;margin-bottom:10px">${{d.classification}}</div>
    <div style="font-size:11px;color:#e8dce8;line-height:1.7;margin-bottom:12px">${{esc(d.explanation)}}</div>
    <div class="comp">${{comps}}</div>
  </div>`;
}}
init();
</script></body></html>"""
