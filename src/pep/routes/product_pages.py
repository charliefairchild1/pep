"""Product detail pages — one per LAVAS app.

Each page is a focused product surface for one wedge/vertical chosen as the
GTM-first product for its parent app. Live at:
  /lingora/prompt   — Lingora Prompt (prompt engineering toolkit)
  /atria/match      — Atria Match (PvP matchmaking)
  /axona/edge       — Axona Edge (performance + flow optimization)
  /vectora/retrieval — Vectora Retrieval API
  /strata/equities  — Strata Equities (the live shipping vertical)
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


def _product_page(
    *,
    title: str,
    parent_name: str,
    parent_path: str,
    accent: str,
    accent_rgb: str,
    surface_bg: str,
    surface_card: str,
    text_color: str,
    dim_color: str,
    border_color: str,
    tagline: str,
    hero_paragraphs: list[str],
    capabilities: list[tuple[str, str]],
    demo_html: str,
    demo_script: str,
    integration_steps: list[tuple[str, str]],
    pricing_tiers: list[tuple[str, str, str]],
    status_badge: str = "PROPOSED",
) -> str:
    """Render a product detail page from the same template."""
    capability_html = "".join(
        f'<div style="background:{surface_card};border:1px solid {border_color};border-left:3px solid {accent};'
        f'border-radius:6px;padding:14px 18px;margin-bottom:10px">'
        f'<div style="font-size:13px;font-weight:bold;color:{accent};margin-bottom:6px">{name}</div>'
        f'<div style="font-size:11px;color:{text_color};line-height:1.6">{desc}</div>'
        f"</div>"
        for name, desc in capabilities
    )
    integration_html = "".join(
        f'<div style="display:flex;gap:14px;margin-bottom:14px;align-items:start">'
        f'<div style="flex-shrink:0;width:32px;height:32px;border-radius:50%;background:rgba({accent_rgb},0.15);'
        f"color:{accent};display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:13px;"
        f'border:1px solid {accent}">{i + 1}</div>'
        f'<div style="flex:1"><div style="font-size:12px;color:{text_color};font-weight:bold;margin-bottom:3px">'
        f"{step}</div><div style=\"font-size:11px;color:{dim_color};line-height:1.6\">{detail}</div></div>"
        f"</div>"
        for i, (step, detail) in enumerate(integration_steps)
    )
    pricing_html = "".join(
        f'<div style="background:{surface_card};border:1px solid {border_color};border-radius:8px;'
        f'padding:18px 20px;flex:1;min-width:180px">'
        f'<div style="font-size:10px;color:{dim_color};letter-spacing:0.15em;text-transform:uppercase;'
        f'margin-bottom:6px">{tier}</div>'
        f'<div style="font-size:18px;font-weight:bold;color:{accent};margin-bottom:8px">{price}</div>'
        f'<div style="font-size:11px;color:{text_color};line-height:1.6">{features}</div>'
        f"</div>"
        for tier, price, features in pricing_tiers
    )
    hero_p_html = "".join(
        f'<p style="font-size:13px;color:{text_color};line-height:1.8;margin-bottom:10px">{p}</p>'
        for p in hero_paragraphs
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — {parent_name} product</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
         background: {surface_bg}; color: {text_color}; line-height: 1.6; }}
  a {{ color: {accent}; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  nav {{ position: sticky; top: 0; z-index: 50; background: {surface_bg};
        padding: 10px 28px; border-bottom: 1px solid {border_color};
        display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }}
  nav .brand {{ font-size: 18px; font-weight: bold; color: {accent}; letter-spacing: 0.5px; }}
  nav .badge {{ font-size: 9px; color: {accent}; background: rgba({accent_rgb}, 0.15);
                padding: 2px 8px; border-radius: 10px; letter-spacing: 0.05em; }}
  nav .back {{ margin-left: auto; font-size: 11px; color: {dim_color}; }}
  .container {{ max-width: 1000px; margin: 0 auto; padding: 24px 28px; }}
  .hero {{ background: linear-gradient(180deg, {surface_card} 0%, {surface_bg} 100%);
          border: 1px solid {border_color}; border-radius: 10px; padding: 32px 36px;
          margin-bottom: 28px; }}
  .hero .tag {{ font-size: 10px; color: {dim_color}; letter-spacing: 0.25em;
               text-transform: uppercase; margin-bottom: 6px; }}
  .hero h1 {{ font-size: 28px; color: {accent}; margin-bottom: 6px; font-weight: bold;
              letter-spacing: 0.3px; }}
  .hero .tagline {{ font-size: 13px; color: {dim_color}; margin-bottom: 20px; font-style: italic; }}
  h2 {{ font-size: 16px; color: {accent}; margin: 28px 0 12px; }}
  .demo-box {{ background: {surface_card}; border: 1px solid {border_color}; border-radius: 8px;
                padding: 20px; margin-bottom: 24px; }}
  .pricing-row {{ display: flex; gap: 14px; flex-wrap: wrap; margin-bottom: 24px; }}
  button.cta {{ padding: 10px 22px; border-radius: 6px; border: 1px solid {accent};
                background: {accent}; color: {surface_bg}; font-size: 12px; cursor: pointer;
                font-family: inherit; font-weight: bold; letter-spacing: 0.05em; }}
  button.cta-secondary {{ padding: 10px 22px; border-radius: 6px; border: 1px solid {accent};
                background: transparent; color: {accent}; font-size: 12px; cursor: pointer;
                font-family: inherit; font-weight: bold; letter-spacing: 0.05em; margin-left: 10px; }}
  @media (max-width: 700px) {{
    .container {{ padding: 16px; }}
    .hero {{ padding: 22px; }}
    .hero h1 {{ font-size: 22px; }}
  }}
</style>
</head>
<body>
<nav>
  <span class="brand">{title}</span>
  <span class="badge">{status_badge}</span>
  <span style="font-size:10px;color:{dim_color}">a {parent_name} product</span>
  <a href="{parent_path}" class="back">&larr; back to {parent_name}</a>
</nav>

<div class="container">
  <div class="hero">
    <div class="tag">{parent_name.upper()} PRODUCT</div>
    <h1>{title}</h1>
    <div class="tagline">{tagline}</div>
    {hero_p_html}
    <div style="margin-top:18px">
      <button class="cta" onclick="document.getElementById('demo').scrollIntoView({{behavior:'smooth'}})">See the live demo</button>
      <button class="cta-secondary" onclick="document.getElementById('integrate').scrollIntoView({{behavior:'smooth'}})">Integration path</button>
    </div>
  </div>

  <h2>What it does</h2>
  {capability_html}

  <h2 id="demo">Live demo</h2>
  <div class="demo-box">
    {demo_html}
  </div>

  <h2 id="integrate">Integration path</h2>
  {integration_html}

  <h2>Pricing</h2>
  <div class="pricing-row">{pricing_html}</div>

  <div style="margin-top:32px;padding:20px;background:{surface_card};border:1px solid {border_color};border-radius:8px">
    <div style="font-size:11px;color:{dim_color};line-height:1.7">
      <b style="color:{text_color}">{title}</b> is a product of <a href="{parent_path}">{parent_name}</a>,
      part of the LAVAS suite by PEP Labs. Built on PEP (Predictive Encoding and Preparation) primitives.
      For more information, see the {parent_name} app at <a href="{parent_path}">{parent_path}</a>
      or the engine at <a href="/pep">/pep</a>.
    </div>
  </div>
</div>

<script>{demo_script}</script>
</body>
</html>
"""


# ═══════════════════════════════════════════════════════════════════════
# Lingora Prompt
# ═══════════════════════════════════════════════════════════════════════
@router.get("/lingora/prompt", response_class=HTMLResponse)
async def lingora_prompt() -> str:
    return _product_page(
        title="Lingora Prompt",
        parent_name="Lingora",
        parent_path="/lingora",
        accent="#ba68c8",
        accent_rgb="186,104,200",
        surface_bg="#0a0e16",
        surface_card="#161c28",
        text_color="#e0e6ed",
        dim_color="#7a8492",
        border_color="#2a3140",
        tagline="Prompts as linguistic objects, not folk-wisdom incantations.",
        hero_paragraphs=[
            "LLM developers iterate on prompts by trial and error, write 5,000-token system prompts, and hope for the best. Most prompt engineering advice is folklore. Lingora Prompt treats prompts as what they actually are — linguistic objects with structure, meaning layers, and predictable failure modes — and gives developers tools to inspect them.",
            "Paste a prompt, get a structural analysis: which words constrain the model's prediction, which open it up, where attention narrows or widens, suggested compressions, and predicted failure modes. The same primitives Lingora uses for translation and writing analysis, applied to the prompt as input.",
        ],
        capabilities=[
            ("Structural analysis", "Tokenizes the prompt into instruction, context, examples, constraints, and output spec. Highlights which spans constrain output strongly vs weakly."),
            ("Compression suggestions", "Identifies redundant tokens (repeated instructions, throat-clearing, low-information context) with concrete cuts that preserve behavior. Typical 30-50% compression with no quality loss."),
            ("Failure-mode prediction", "Flags structural patterns that historically lead to specific failures: instruction overrides by examples, format-spec collisions, attention dilution from over-long context, conflicting constraints."),
            ("A/B compare", "Side-by-side structural diff between two prompts. Shows what changed and predicts how the change shifts model behavior before you spend tokens testing."),
            ("Cost forecasting", "Token count + estimated API cost per provider (OpenAI, Anthropic, Google, Meta). Suggests cheapest model that meets your structural constraints."),
        ],
        demo_html="""
<div style="display:flex;gap:14px;flex-wrap:wrap">
  <div style="flex:1;min-width:300px">
    <div style="font-size:11px;color:#7a8492;margin-bottom:6px">PASTE A PROMPT</div>
    <textarea id="prompt-input" style="width:100%;height:200px;background:#0a0e16;color:#e0e6ed;border:1px solid #2a3140;border-radius:4px;padding:10px;font-family:inherit;font-size:11px;resize:vertical">You are a helpful assistant. Please be helpful and answer the user's question. Make sure to be accurate and thorough. Always provide complete answers. Do not be unhelpful.

User: What is the capital of France?</textarea>
    <button onclick="analyzePrompt()" style="margin-top:8px;padding:6px 14px;border-radius:4px;border:1px solid #ba68c8;background:#ba68c8;color:#0a0e16;font-size:11px;cursor:pointer;font-family:inherit;font-weight:bold">Analyze</button>
  </div>
  <div style="flex:1;min-width:300px">
    <div style="font-size:11px;color:#7a8492;margin-bottom:6px">STRUCTURAL ANALYSIS</div>
    <div id="prompt-output" style="background:#0a0e16;border:1px solid #2a3140;border-radius:4px;padding:10px;min-height:200px;font-size:11px;line-height:1.7"></div>
  </div>
</div>
        """,
        demo_script="""
function analyzePrompt() {
  const text = document.getElementById('prompt-input').value;
  const tokens = text.split(/\\s+/).filter(Boolean).length;
  const lines = text.split('\\n').length;
  const lower = text.toLowerCase();
  const findings = [];
  if (lower.includes('helpful') && (lower.match(/helpful/g) || []).length > 1) findings.push({ severity: 'medium', text: 'Repeated "helpful" — pick one statement; repetition does not reinforce, it dilutes attention.' });
  if (lower.includes('please')) findings.push({ severity: 'low', text: '"Please" adds tokens, not behavior. Models do not need politeness markers.' });
  if (lower.includes('always') && lower.includes('do not')) findings.push({ severity: 'medium', text: 'Mixed positive ("always") and negative ("do not") instructions. Consolidate into positive form for cleaner constraint.' });
  if (lower.includes('make sure to')) findings.push({ severity: 'low', text: '"Make sure to" is filler; replace with imperative verb directly.' });
  if (lower.includes('thorough') && lower.includes('complete')) findings.push({ severity: 'medium', text: '"Thorough" and "complete" are near-synonyms; pick one.' });
  if (lower.includes('accurate') && lower.includes('thorough')) findings.push({ severity: 'low', text: 'Accuracy and thoroughness can trade off; if you want both, prioritize explicitly.' });
  const compressedTokens = Math.floor(tokens * 0.55);
  const out = document.getElementById('prompt-output');
  out.innerHTML = '<div style="color:#ba68c8;font-weight:bold;margin-bottom:8px">SUMMARY</div>' +
    '<div style="color:#e0e6ed">tokens: <b>' + tokens + '</b> · lines: <b>' + lines + '</b></div>' +
    '<div style="color:#e0e6ed">est. compressed: <b style="color:#a3e635">' + compressedTokens + ' tokens (-' + Math.round((1 - compressedTokens/tokens) * 100) + '%)</b></div>' +
    '<div style="color:#a3e635;font-weight:bold;margin:14px 0 6px">FINDINGS</div>' +
    (findings.length ? findings.map(f => {
      const col = f.severity === 'medium' ? '#fbbf24' : '#67e8f9';
      return '<div style="margin-bottom:6px;color:#e0e6ed"><span style="color:' + col + '">●</span> ' + f.text + '</div>';
    }).join('') : '<div style="color:#7a8492">no obvious issues — prompt looks clean</div>') +
    '<div style="color:#a3e635;font-weight:bold;margin:14px 0 6px">SUGGESTED REWRITE</div>' +
    '<div style="background:#0a0e16;border:1px solid #2a3140;border-radius:3px;padding:8px;color:#e0e6ed;font-size:10px;font-style:italic">Answer the user accurately and concisely.\\n\\nUser: What is the capital of France?</div>';
}
analyzePrompt();
        """,
        integration_steps=[
            ("Drop in the SDK", "pip install lingora-prompt or npm install @lingora/prompt. One-line import in your existing prompt-iteration workflow."),
            ("Paste your prompt", "Pass any prompt string to the analyzer. Returns a structured report with findings, compression suggestions, and predicted failure modes."),
            ("Iterate", "Apply suggested rewrites, re-analyze, ship. The toolkit lets you iterate on prompt structure without spending tokens on the LLM at every step."),
            ("(Optional) CI integration", "Hook the analyzer into CI to flag prompt regressions: anyone who increases token count without adding new constraints gets a warning on PR."),
        ],
        pricing_tiers=[
            ("Free", "$0 / mo", "Web analyzer, up to 100 prompts/mo, no API access. For solo developers."),
            ("Pro", "$29 / mo", "Unlimited web + API access, 10K analyses/mo, A/B compare, CI integration."),
            ("Team", "$199 / mo", "Up to 20 seats, 100K analyses/mo, prompt versioning, team prompt library."),
        ],
        status_badge="WEDGE 4 · GTM FIRST",
    )


# ═══════════════════════════════════════════════════════════════════════
# Atria Match
# ═══════════════════════════════════════════════════════════════════════
@router.get("/atria/match", response_class=HTMLResponse)
async def atria_match() -> str:
    return _product_page(
        title="Atria Match",
        parent_name="Atria",
        parent_path="/atria",
        accent="#5eead4",
        accent_rgb="94,234,212",
        surface_bg="#0a1014",
        surface_card="#141d24",
        text_color="#dcecec",
        dim_color="#6b8088",
        border_color="#1f2c34",
        tagline="Matchmaking that targets rematch rate, not win-probability balance.",
        hero_paragraphs=[
            "Your existing matchmaker uses Elo, Glicko, TrueSkill, or OpenSkill. It produces &quot;fair&quot; matches and players still complain. Rematch rates are mediocre, queue times are acceptable, but the experience quality is not. The problem is not the tuning — the problem is the objective. Win-probability balance is not match quality.",
            "Atria Match drops in beneath your existing rating system, replaces pool selection with graph-based spreading activation, and scores matches on multi-objective consensus across skill, tempo, social, role, and behavior. Every metric that matters to players gets better. The only tradeoff is a small queue-time increase, which is tunable.",
        ],
        capabilities=[
            ("Pool formation via spreading activation", "Replaces sorted rating windows with graph-based candidate pools. Players are nodes; compatibility weights are edges; activation spreads from the seed player. Result: pools shaped by actual fit, not just rank proximity."),
            ("Multi-objective scoring", "Each candidate match scored across skill, tempo, role, communication style, tilt tolerance, and goal alignment. The match with the highest consensus wins, not the closest Elo."),
            ("Behavior modulation", "Recent toxicity, AFK, throwing, and pro-social signals modulate edge weights live. Toxic players get matched with each other; pro-social players surface as good fits for new players."),
            ("Cold-start handling", "Glicko-style uncertainty for new players. Wide initial pools that contract as confidence builds. No more new-player stomp."),
            ("Smurf detection", "Feature-vector anomaly detection on accounts with mechanical signatures inconsistent with their rating. Routes detected smurfs into appropriate pools without bans."),
        ],
        demo_html="""
<div style="display:flex;gap:14px;flex-wrap:wrap">
  <div style="flex:1;min-width:280px">
    <div style="font-size:11px;color:#6b8088;margin-bottom:6px">SCENARIO</div>
    <select id="match-scenario" onchange="renderMatch()" style="width:100%;background:#0a1014;color:#dcecec;border:1px solid #1f2c34;border-radius:4px;padding:8px;font-family:inherit;font-size:11px">
      <option value="0">Veteran player at peak hours</option>
      <option value="1">New player, first session</option>
      <option value="2">Off-peak, sparse pool</option>
      <option value="3">Player with recent toxicity flag</option>
    </select>
    <div id="match-detail" style="margin-top:14px;padding:12px;background:#0a1014;border:1px solid #1f2c34;border-radius:4px;font-size:11px;line-height:1.7;color:#dcecec"></div>
  </div>
  <div style="flex:1;min-width:280px">
    <div style="font-size:11px;color:#6b8088;margin-bottom:6px">METRICS (Elo baseline vs Atria Match)</div>
    <canvas id="match-canvas" width="400" height="280" style="width:100%;background:#0a1014;border:1px solid #1f2c34;border-radius:4px"></canvas>
  </div>
</div>
        """,
        demo_script="""
const MATCH_SCENARIOS = [
  { d: 'Veteran player, prime time. Dense pool, plenty of options. Atria can be picky.', elo: { rematch: 0.42, queue: 12, satisfaction: 0.62 }, atria: { rematch: 0.61, queue: 14, satisfaction: 0.84 } },
  { d: 'New player, first session, wide confidence interval. Atria places into a learning bracket.', elo: { rematch: 0.28, queue: 18, satisfaction: 0.41 }, atria: { rematch: 0.55, queue: 21, satisfaction: 0.78 } },
  { d: 'Off-peak, sparse pool. Atria widens decay to compensate; small quality cost.', elo: { rematch: 0.31, queue: 45, satisfaction: 0.48 }, atria: { rematch: 0.49, queue: 52, satisfaction: 0.71 } },
  { d: 'Player flagged toxic in last 3 matches. Atria modulates pool to skip sensitive teammates.', elo: { rematch: 0.35, queue: 14, satisfaction: 0.52 }, atria: { rematch: 0.58, queue: 16, satisfaction: 0.79 } },
];
function renderMatch() {
  const i = parseInt(document.getElementById('match-scenario').value);
  const s = MATCH_SCENARIOS[i];
  document.getElementById('match-detail').textContent = s.d;
  const c = document.getElementById('match-canvas');
  const ctx = c.getContext('2d');
  ctx.fillStyle = '#0a1014'; ctx.fillRect(0, 0, c.width, c.height);
  const metrics = [
    { label: 'Rematch rate', a: s.elo.rematch, b: s.atria.rematch, fmt: v => (v*100).toFixed(0)+'%', good: v => v > 0 },
    { label: 'Queue (sec)',   a: s.elo.queue/60,   b: s.atria.queue/60,   fmt: v => (v*60).toFixed(0)+'s', good: v => v < 0 },
    { label: 'Satisfaction',  a: s.elo.satisfaction, b: s.atria.satisfaction, fmt: v => (v*100).toFixed(0)+'%', good: v => v > 0 },
  ];
  metrics.forEach((m, j) => {
    const y = 30 + j * 80;
    ctx.fillStyle = '#dcecec'; ctx.font = 'bold 11px monospace'; ctx.fillText(m.label, 10, y);
    ctx.fillStyle = 'rgba(167,139,250,0.25)'; ctx.fillRect(10, y+8, 380, 18);
    ctx.fillStyle = 'rgba(167,139,250,0.85)'; ctx.fillRect(10, y+8, 380*Math.min(1,m.a), 18);
    ctx.fillStyle = '#fff'; ctx.font='10px monospace'; ctx.textAlign='right'; ctx.fillText('Elo: '+m.fmt(m.a), 385, y+21); ctx.textAlign='left';
    ctx.fillStyle = 'rgba(94,234,212,0.25)'; ctx.fillRect(10, y+30, 380, 18);
    ctx.fillStyle = 'rgba(94,234,212,0.85)'; ctx.fillRect(10, y+30, 380*Math.min(1,m.b), 18);
    ctx.fillStyle = '#fff'; ctx.textAlign='right'; ctx.fillText('Atria: '+m.fmt(m.b), 385, y+43); ctx.textAlign='left';
  });
}
renderMatch();
        """,
        integration_steps=[
            ("Phase 1 — Shadow mode (2 weeks)", "Atria runs alongside your existing matchmaker. Both produce match suggestions; only the existing system goes live. Compare predictions. No risk."),
            ("Phase 2 — A/B test (4 weeks)", "Route a percentage of matches through Atria. Measure rematch rate, session length, complaints. Self-evaluating — roll back at no cost if it does not lift metrics."),
            ("Phase 3 — Full rollout", "Replace pool selection with Atria. Keep your existing rating system for display/rank; Atria sits underneath as the pool-formation and scoring layer."),
            ("Latency budget", "Pool formation is a single graph walk (~2-8ms for 100K-player pools). Multi-objective scoring is a dot product per candidate (~0.01ms). Total added latency under 20ms — your queue timeout dwarfs this."),
        ],
        pricing_tiers=[
            ("Indie", "$2K / mo", "Up to 50K MAU, hosted scoring API, standard objectives. For studios with one PvP title."),
            ("Studio", "$15K / mo", "Up to 1M MAU, custom objective tuning, behavior signals, dedicated success engineer."),
            ("Enterprise", "Custom", "Unlimited scale, on-prem or VPC deploy, custom integration, white-label option."),
        ],
        status_badge="FIRST WEDGE · GAME STUDIOS",
    )


# ═══════════════════════════════════════════════════════════════════════
# Axona Edge
# ═══════════════════════════════════════════════════════════════════════
@router.get("/axona/edge", response_class=HTMLResponse)
async def axona_edge() -> str:
    return _product_page(
        title="Axona Edge",
        parent_name="Axona",
        parent_path="/axona",
        accent="#ffb74d",
        accent_rgb="255,183,77",
        surface_bg="#0d0a14",
        surface_card="#1a1322",
        text_color="#e8dee8",
        dim_color="#8a7a8e",
        border_color="#2c2236",
        tagline="Real-time cognitive state monitoring for high-stakes performance.",
        hero_paragraphs=[
            "Surgeons, pilots, athletes, esports pros, and military operators perform at the limit of cognitive bandwidth. When that bandwidth drops below safe thresholds, errors happen — and there is currently no objective real-time signal for &quot;the operator is no longer fit for this task.&quot; Pre-game routines and pre-flight checklists are based on tradition, not measurement.",
            "Axona Edge is the cognitive-state monitoring layer for high-stakes performance. Flow detection, bandwidth tracking, tilt detection, pre-event readiness assessment, and fatigue alerts before errors happen. Already battle-tested in Axona's research canvases on flow state, hyperfocus, attention bandwidth, and inattentional blindness.",
        ],
        capabilities=[
            ("Flow state detection", "Continuous monitoring of the cognitive state space (novelty / coherence / bandwidth / valence). Flags when the operator enters or exits flow with high precision."),
            ("Bandwidth alerts", "Real-time bandwidth gauge. Alerts when free cognitive capacity drops below operator-configured safe thresholds. Pre-event readiness score lets supervisors hold an operator out of high-stakes work when they're depleted."),
            ("Tilt detection (esports)", "Detects emotional state disrupting coherence. Coaches see the moment a player tilts, not after the loss. Replay analysis tied to specific tilt events."),
            ("Fatigue forecasting", "Predicts cognitive depletion 30-60 minutes ahead based on current state-space trajectory. Alerts surgeons during long procedures, pilots on long flights, before errors compound."),
            ("Post-event analysis", "Reconstructs the cognitive state trajectory across the event. Identifies exactly when state degraded, what triggered it, and which interventions would have mattered."),
        ],
        demo_html="""
<div style="display:flex;gap:14px;flex-wrap:wrap">
  <div style="flex:1;min-width:280px">
    <div style="font-size:11px;color:#8a7a8e;margin-bottom:6px">OPERATOR PROFILE</div>
    <select id="edge-op" onchange="renderEdge()" style="width:100%;background:#0d0a14;color:#e8dee8;border:1px solid #2c2236;border-radius:4px;padding:8px;font-family:inherit;font-size:11px">
      <option value="0">Surgeon (3 hours into procedure)</option>
      <option value="1">Esports pro (mid-tournament, on tilt)</option>
      <option value="2">Pilot (8-hour transatlantic, hour 6)</option>
      <option value="3">Athlete (entering flow)</option>
    </select>
    <div id="edge-state" style="margin-top:14px;padding:12px;background:#0d0a14;border:1px solid #2c2236;border-radius:4px;font-size:11px;line-height:1.7;color:#e8dee8"></div>
  </div>
  <div style="flex:1;min-width:280px">
    <div style="font-size:11px;color:#8a7a8e;margin-bottom:6px">COGNITIVE STATE</div>
    <canvas id="edge-canvas" width="400" height="280" style="width:100%;background:#0d0a14;border:1px solid #2c2236;border-radius:4px"></canvas>
  </div>
</div>
        """,
        demo_script="""
const EDGE_OPS = [
  { state: { novelty: 0.20, coherence: 0.55, bandwidth: 0.35, valence: 0.10 }, alert: 'BANDWIDTH WARNING — recommend brief break before next critical step', risk: 'medium' },
  { state: { novelty: 0.85, coherence: 0.25, bandwidth: 0.70, valence: -0.65 }, alert: 'TILT DETECTED — coherence collapsed; coach intervention recommended', risk: 'high' },
  { state: { novelty: 0.10, coherence: 0.65, bandwidth: 0.30, valence: 0.05 }, alert: 'FATIGUE FORECAST — bandwidth declining; auto-pilot recommended for next 30 min', risk: 'medium' },
  { state: { novelty: 0.55, coherence: 0.92, bandwidth: 0.85, valence: 0.85 }, alert: 'FLOW STATE — protect conditions; no intervention', risk: 'low' },
];
function renderEdge() {
  const i = parseInt(document.getElementById('edge-op').value);
  const op = EDGE_OPS[i];
  const c = document.getElementById('edge-canvas');
  const ctx = c.getContext('2d');
  ctx.fillStyle = '#0d0a14'; ctx.fillRect(0, 0, c.width, c.height);
  const axes = [['novelty', '#a3e635'], ['coherence', '#67e8f9'], ['bandwidth', '#ffb74d'], ['valence', '#f06292']];
  axes.forEach((ax, j) => {
    const y = 30 + j * 60;
    ctx.fillStyle = '#dcd6dc'; ctx.font = '11px monospace'; ctx.fillText(ax[0], 10, y);
    ctx.fillStyle = 'rgba(140,140,140,0.2)'; ctx.fillRect(10, y+8, 380, 18);
    const v = op.state[ax[0]];
    if (ax[0] === 'valence') {
      const cx = 10 + 190;
      const w = Math.abs(v) * 190;
      ctx.fillStyle = ax[1] + 'cc';
      ctx.fillRect(v < 0 ? cx - w : cx, y+8, w, 18);
    } else {
      ctx.fillStyle = ax[1] + 'cc'; ctx.fillRect(10, y+8, 380*v, 18);
    }
    ctx.fillStyle = '#fff'; ctx.font = '10px monospace'; ctx.textAlign='right';
    ctx.fillText(v.toFixed(2), 385, y+21); ctx.textAlign='left';
  });
  const cols = { high: '#f06292', medium: '#ffb74d', low: '#a3e635' };
  ctx.fillStyle = cols[op.risk]; ctx.font = 'bold 11px monospace'; ctx.textAlign='center';
  ctx.fillText('RISK: ' + op.risk.toUpperCase(), c.width/2, 270);
  document.getElementById('edge-state').innerHTML = '<b style="color:' + cols[op.risk] + '">' + op.alert + '</b>';
}
renderEdge();
        """,
        integration_steps=[
            ("Sensor integration", "Pulls from existing telemetry: HR/HRV from Apple Watch / Whoop / Polar, EEG from Muse / Neurosity, behavioral from input devices. No new hardware required for most use cases."),
            ("Calibration period (1 week)", "Edge learns the operator's baseline state-space coordinates. Personalized thresholds, not population averages."),
            ("Live deployment", "Continuous monitoring with configurable alert routing — to the operator, to a coach/supervisor, or both. Privacy-first: data stays on-device by default."),
            ("Post-event review", "Optional cloud sync for retrospective analysis. Coaches and operators review state trajectories tied to specific events to learn what conditions produce flow vs collapse."),
        ],
        pricing_tiers=[
            ("Individual", "$49 / mo", "Personal account, 1 device, basic alerts, 30-day history. For solo athletes and pros."),
            ("Team", "$499 / mo", "Up to 25 operators, coach dashboard, team analytics, full history. For sports teams and small clinics."),
            ("Enterprise", "Custom", "Unlimited operators, SSO, on-prem option, custom integrations. For hospitals, airlines, military."),
        ],
        status_badge="WEDGE 4 · GTM FIRST",
    )


# ═══════════════════════════════════════════════════════════════════════
# Vectora Retrieval
# ═══════════════════════════════════════════════════════════════════════
@router.get("/vectora/retrieval", response_class=HTMLResponse)
async def vectora_retrieval() -> str:
    return _product_page(
        title="Vectora Retrieval",
        parent_name="Vectora",
        parent_path="/vectora",
        accent="#38bdf8",
        accent_rgb="56,189,248",
        surface_bg="#0a121a",
        surface_card="#142028",
        text_color="#dce6ed",
        dim_color="#6a808a",
        border_color="#1f3040",
        tagline="Drop-in retrieval API that finds what top-k vector search misses.",
        hero_paragraphs=[
            "Your RAG pipeline uses an embedder + a vector DB + top-k nearest neighbors. You hit a plateau around 60-70% retrieval accuracy on your own eval set, then you start bolting on rerankers and query rewriting. The reranker improves precision but cannot rescue recall — if the answer was not in the top-k, no rerank will find it.",
            "Vectora Retrieval is the layer that finds it. Replaces top-k with graph-based spreading activation, so second-hop results surface automatically. Hybrid keyword + semantic + knowledge-graph edges merged in one query. Sits on top of your existing Pinecone, Weaviate, Qdrant, or pgvector — no migration.",
        ],
        capabilities=[
            ("Spreading-activation retrieval", "Replace top-k with a graph walk that follows weighted edges from the query through the document graph. Second-hop results that share no surface tokens with the query but answer the underlying question surface automatically."),
            ("Hybrid edges", "Same node set, multiple edge types: embedding similarity (broad), keyword exact-match (precise), knowledge-graph relations (typed), co-occurrence (statistical). Activation flows through whichever edges are strong."),
            ("Context-aware modulation", "Recent user activity becomes a state modulator. Same query returns different results when the user is in different contexts. Eliminates the &quot;rephrase to add context&quot; tax users currently pay."),
            ("Anomaly surfacing", "Residual scoring on incoming items. New documents that diverge from the existing pattern get flagged automatically — useful for change detection, research, alerting."),
            ("Drop-in API", "REST + Python/JS SDK. Wraps your existing vector DB. Three-line code change to swap top-k for Vectora retrieval. Backwards compatible: top-k mode preserved as a config flag."),
        ],
        demo_html="""
<div style="font-size:11px;color:#6a808a;margin-bottom:6px">QUERY</div>
<input type="text" id="ret-query" value="caching strategies for a monolith" oninput="renderRet()" style="width:100%;background:#0a121a;color:#dce6ed;border:1px solid #1f3040;border-radius:4px;padding:8px;font-family:inherit;font-size:11px;margin-bottom:14px">
<div style="display:flex;gap:14px;flex-wrap:wrap">
  <div style="flex:1;min-width:260px">
    <div style="font-size:11px;color:#a78bfa;font-weight:bold;margin-bottom:6px">TOP-K (baseline)</div>
    <div id="ret-topk" style="background:#0a121a;border:1px solid #1f3040;border-radius:4px;padding:10px;min-height:200px;font-size:11px;line-height:1.7"></div>
  </div>
  <div style="flex:1;min-width:260px">
    <div style="font-size:11px;color:#38bdf8;font-weight:bold;margin-bottom:6px">VECTORA (with second-hop expansion)</div>
    <div id="ret-vec" style="background:#0a121a;border:1px solid #1f3040;border-radius:4px;padding:10px;min-height:200px;font-size:11px;line-height:1.7"></div>
  </div>
</div>
        """,
        demo_script="""
const RET_QUERIES = {
  'caching': {
    topk: ['Redis caching for Django apps', 'Cache-aside pattern explained', 'Memcached vs Redis performance'],
    vec:  ['Redis caching for Django apps', 'Cache-aside pattern explained', 'Memcached vs Redis performance', '<i style=color:#a3e635>+ Memory pressure when caching too aggressively (2nd hop)</i>', '<i style=color:#a3e635>+ When to split a monolith for cache-locality (2nd hop)</i>', '<i style=color:#a3e635>+ Database query patterns that beat caching (2nd hop)</i>'],
  },
  'rate limit': {
    topk: ['HTTP 429 rate-limit responses', 'Token bucket rate limiting', 'Rate-limit headers spec'],
    vec:  ['HTTP 429 rate-limit responses', 'Token bucket rate limiting', 'Rate-limit headers spec', '<i style=color:#a3e635>+ Backpressure patterns for cascading systems (2nd hop)</i>', '<i style=color:#a3e635>+ Queue depth as a load signal (2nd hop)</i>', '<i style=color:#a3e635>+ Why retries amplify outages (2nd hop)</i>'],
  },
  'embedding': {
    topk: ['Sentence transformers tutorial', 'OpenAI ada-002 dimensions', 'Vector DB comparison'],
    vec:  ['Sentence transformers tutorial', 'OpenAI ada-002 dimensions', 'Vector DB comparison', '<i style=color:#a3e635>+ Curse of dimensionality in embedding space (2nd hop)</i>', '<i style=color:#a3e635>+ Hybrid search: BM25 + vectors merged (2nd hop)</i>', '<i style=color:#a3e635>+ When semantic search hurts more than helps (2nd hop)</i>'],
  },
};
function renderRet() {
  const q = document.getElementById('ret-query').value.toLowerCase();
  let key = 'caching';
  if (q.includes('rate') || q.includes('limit')) key = 'rate limit';
  else if (q.includes('embed') || q.includes('vector')) key = 'embedding';
  const data = RET_QUERIES[key];
  document.getElementById('ret-topk').innerHTML = data.topk.map((r, i) => '<div style="margin-bottom:5px;color:#dce6ed">' + (i+1) + '. ' + r + '</div>').join('');
  document.getElementById('ret-vec').innerHTML = data.vec.map((r, i) => '<div style="margin-bottom:5px;color:#dce6ed">' + (i+1) + '. ' + r + '</div>').join('');
}
renderRet();
        """,
        integration_steps=[
            ("Install the SDK", "pip install vectora or npm install @vectora/client. Configure with your existing vector DB credentials (Pinecone, Weaviate, Qdrant, pgvector — all supported)."),
            ("Index your existing data (no re-embed)", "Vectora reads from your vector DB; the graph layer is built incrementally as queries come in. No re-embedding required, no migration."),
            ("Swap retrieval call", "Replace your top-k call with vectora.retrieve(). Returns the same shape (list of documents with scores) but with second-hop expansion included. Three-line change."),
            ("Tune decay", "One parameter (graph-walk decay) tunes how far Vectora explores. Default works for most cases; tighten for precision-sensitive use cases, loosen for recall-sensitive."),
        ],
        pricing_tiers=[
            ("Hobby", "$0 / mo", "Self-hosted, up to 100K documents, 10K queries/mo. Open source."),
            ("Cloud", "$99 / mo", "Hosted, up to 1M documents, 1M queries/mo, automatic graph maintenance."),
            ("Scale", "Custom", "Unlimited documents and queries, dedicated infrastructure, SLA, on-prem option."),
        ],
        status_badge="CORE PRODUCT",
    )


# ═══════════════════════════════════════════════════════════════════════
# Strata Equities
# ═══════════════════════════════════════════════════════════════════════
@router.get("/strata/equities", response_class=HTMLResponse)
async def strata_equities() -> str:
    return _product_page(
        title="Strata Equities",
        parent_name="Strata",
        parent_path="/strata",
        accent="#e879f9",
        accent_rgb="232,121,249",
        surface_bg="#0c0a14",
        surface_card="#181423",
        text_color="#e8dce8",
        dim_color="#7a708a",
        border_color="#2a2236",
        tagline="AI stock intelligence and paper-trading. Research and simulation only — not financial advice.",
        hero_paragraphs=[
            "Strata Equities is the first shipping vertical of the Strata markets platform. An AI-powered stock intelligence tool that scans for unusual moves, classifies them into 16 archetypes, scores news catalysts with Claude, and runs 294 paper-trading strategies on a leaderboard. Already live at <code>~/projects/charlie_project/</code> as a Next.js + Prisma + Finnhub + Claude application.",
            "The pitch is honest: research and simulation only, no real trades, no financial advice. The value is structural insight — what is happening in the market right now, why it is happening, and which strategies have historically performed under similar conditions. The user makes the trading decisions.",
        ],
        capabilities=[
            ("Unusual Move Scanner", "Continuously scans the watched universe for statistically unusual price/volume moves. Composite score (price percentile 35% + volume 25% + volatility-adjusted 25% + persistence 15%) with Normal / Notable / Unusual / Extreme labels."),
            ("Pattern Classifier", "Classifies each unusual move into one of 16 archetypes — breakout, breakdown, momentum, mean reversion, short squeeze, low float speculation, sector sympathy, pump risk, post-earnings drift, capitulation, gap up/down, exhaustion top/bottom, volume climax."),
            ("News Catalyst Scorer", "Claude-scored multi-dimensional analysis of news headlines tied to flagged stocks. Quality, sentiment, credibility, materiality, hype scores plus a one-line analyst summary. Cost-controlled: only scores stocks with unusualScore ≥ 60."),
            ("294-strategy paper-trading library", "Paper-trade against 294 strategies spanning every major sector and direction. Live leaderboard with annualized return, Sharpe, max drawdown, win rate, trade count. Personalized portfolio recommendations based on recent strategy performance."),
            ("Sector heatmap + watchlist", "Real-time sector rotation visualization. Personal watchlist with custom alerts on price levels, signal triggers, and unusual moves. Daily &quot;Stock of the Day&quot; pick from the highest-conviction signals."),
        ],
        demo_html="""
<div style="font-size:11px;color:#7a708a;margin-bottom:6px">SAMPLE SIGNAL</div>
<select id="eq-signal" onchange="renderEq()" style="width:100%;background:#0c0a14;color:#e8dce8;border:1px solid #2a2236;border-radius:4px;padding:8px;font-family:inherit;font-size:11px;margin-bottom:14px">
  <option value="0">NVDA: +6.2% on 4.1x volume</option>
  <option value="1">SMCI: +18% on 9x volume, low float</option>
  <option value="2">PFE: -5.4% on 3.2x volume, breaking 200d</option>
  <option value="3">SPCE: +42% on 18x volume, no news</option>
</select>
<div id="eq-signal-card" style="background:#0c0a14;border:1px solid #2a2236;border-radius:4px;padding:14px;font-size:11px;line-height:1.7;color:#e8dce8"></div>
        """,
        demo_script="""
const EQ_SIGNALS = [
  { ticker: 'NVDA', label: 'NVDA: +6.2% on 4.1x volume', score: 72, classify: 'BREAKOUT', news: { quality: 88, sentiment: 65 }, summary: 'Earnings beat plus AI capex commentary. High-quality news, confirms breakout. Atria News-Driven and Tech Momentum strategies would enter.' },
  { ticker: 'SMCI', label: 'SMCI: +18% on 9x volume, low float', score: 91, classify: 'PUMP_RISK / LOW_FLOAT_SPECULATION', news: { quality: 22, sentiment: 78 }, summary: 'Large move on small float, no major news. Hype score elevated. PUMP RISK FLAG. Strata recommends avoiding long entries; Hype Fader strategies may take a short.' },
  { ticker: 'PFE', label: 'PFE: -5.4% on 3.2x volume, breaks 200d', score: 79, classify: 'BREAKDOWN', news: { quality: 75, sentiment: -55 }, summary: 'Drug trial failure announcement. Credible source, material news. Healthcare Short and Pharma Short strategies enter; mean-reversion strategies wait.' },
  { ticker: 'SPCE', label: 'SPCE: +42% on 18x volume, no news', score: 96, classify: 'PUMP_RISK', news: { quality: 8, sentiment: 0 }, summary: 'Extreme move with no identifiable catalyst. Likely retail-driven squeeze. PUMP RISK + EXTREME label. All long strategies skip; Squeeze Fader prepares for blow-off top.' },
];
function renderEq() {
  const s = EQ_SIGNALS[parseInt(document.getElementById('eq-signal').value)];
  const scoreCol = s.score >= 85 ? '#f06292' : s.score >= 70 ? '#e879f9' : '#fbbf24';
  document.getElementById('eq-signal-card').innerHTML =
    '<div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:10px">' +
      '<div><div style="font-size:14px;font-weight:bold;color:#e879f9">' + s.ticker + '</div>' +
      '<div style="font-size:11px;color:#7a708a">' + s.label + '</div></div>' +
      '<div style="text-align:right"><div style="font-size:24px;font-weight:bold;color:' + scoreCol + '">' + s.score + '</div>' +
      '<div style="font-size:9px;color:#7a708a;letter-spacing:0.1em">UNUSUAL SCORE</div></div>' +
    '</div>' +
    '<div style="background:rgba(232,121,249,0.1);border-left:3px solid #e879f9;padding:8px 12px;margin:10px 0;font-weight:bold">' + s.classify + '</div>' +
    '<div style="display:flex;gap:14px;margin:10px 0;font-size:10px">' +
      '<div><span style="color:#7a708a">news quality:</span> <b style="color:#e8dce8">' + s.news.quality + '</b></div>' +
      '<div><span style="color:#7a708a">sentiment:</span> <b style="color:' + (s.news.sentiment >= 0 ? '#a3e635' : '#f06292') + '">' + (s.news.sentiment >= 0 ? '+' : '') + s.news.sentiment + '</b></div>' +
    '</div>' +
    '<div style="margin-top:14px;padding-top:14px;border-top:1px solid #2a2236;font-style:italic;color:#a899a8">' + s.summary + '</div>';
}
renderEq();
        """,
        integration_steps=[
            ("Sign in", "Free trial with Google or GitHub OAuth. No credit card required for the basic tier."),
            ("Connect a watchlist", "Import from a CSV or paste tickers. Strata seeds with the S&P 500 + popular small caps by default."),
            ("Configure alerts", "Set thresholds for unusual scores, signal types, sector moves. Email or webhook notifications."),
            ("Paper-trade", "Pick strategies from the 294-strategy library to follow. Strata simulates trades against live data; equity curves and stats update daily."),
        ],
        pricing_tiers=[
            ("Free", "$0 / mo", "Top-100 stocks, daily refresh, 5 strategies, no AI news scoring. For exploration."),
            ("Pro", "$29 / mo", "Full universe, real-time scanning, all 294 strategies, AI news scoring, unlimited watchlists."),
            ("Trader", "$99 / mo", "Custom strategies, backtest engine access, API export, priority support. For active research users."),
        ],
        status_badge="SHIPPING · FIRST VERTICAL",
    )
