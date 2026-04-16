"""Product detail pages — one per LAVAS app.

Each page is a focused product surface for one wedge/vertical chosen as the
GTM-first product for its parent app. Live at:
  /lingora/prompt   — Lingora Prompt (prompt engineering toolkit)
  /atria/match      — Atria Match (PvP matchmaking)
  /axona/edge       — Axona Edge (performance + flow optimization)
  /vectora/retrieval — Vectora Retrieval API
  /strata/equities  — Strata Equities (the live shipping vertical)

Shared template renders a real landing page: hero, problem/solution,
how-it-works, capabilities, primary + secondary demos, use cases,
competitor comparison, integration, pricing, FAQ, final CTA.
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
    problem: str,
    solution: str,
    how_it_works: list[tuple[str, str]],
    capabilities: list[tuple[str, str]],
    demo_html: str,
    demo_script: str,
    secondary_demo_title: str,
    secondary_demo_html: str,
    secondary_demo_script: str,
    use_cases: list[tuple[str, str, str]],
    competitors: list[tuple[str, str, str]],
    integration_steps: list[tuple[str, str]],
    pricing_tiers: list[tuple[str, str, str]],
    faq: list[tuple[str, str]],
    final_cta: str,
    status_badge: str = "PROPOSED",
) -> str:
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
    how_it_works_html = "".join(
        f'<div style="flex:1;min-width:200px;background:{surface_card};border:1px solid {border_color};'
        f'border-radius:8px;padding:18px;position:relative">'
        f'<div style="position:absolute;top:-10px;left:14px;background:{accent};color:{surface_bg};'
        f'padding:2px 10px;border-radius:10px;font-size:10px;font-weight:bold">STEP {i + 1}</div>'
        f'<div style="font-size:13px;color:{accent};font-weight:bold;margin:8px 0 6px">{step}</div>'
        f'<div style="font-size:11px;color:{text_color};line-height:1.6">{desc}</div>'
        f"</div>"
        for i, (step, desc) in enumerate(how_it_works)
    )
    use_cases_html = "".join(
        f'<div style="background:{surface_card};border:1px solid {border_color};border-radius:8px;'
        f'padding:16px 20px;margin-bottom:10px">'
        f'<div style="display:flex;justify-content:space-between;align-items:start;gap:10px;margin-bottom:6px">'
        f'<div style="font-size:12px;font-weight:bold;color:{accent}">{persona}</div>'
        f'<div style="font-size:9px;color:{dim_color};letter-spacing:0.1em">USE CASE {i + 1}</div></div>'
        f'<div style="font-size:11px;color:{text_color};line-height:1.6;margin-bottom:6px">'
        f'<b style="color:{dim_color}">scenario:</b> {scenario}</div>'
        f'<div style="font-size:11px;color:{text_color};line-height:1.6">'
        f'<b style="color:{dim_color}">outcome:</b> {outcome}</div>'
        f"</div>"
        for i, (persona, scenario, outcome) in enumerate(use_cases)
    )
    competitor_html = (
        '<table style="width:100%;border-collapse:collapse;font-size:11px">'
        f'<thead><tr style="background:{surface_card}">'
        f'<th style="padding:10px;text-align:left;color:{dim_color};border-bottom:1px solid {border_color};font-weight:bold">vs</th>'
        f'<th style="padding:10px;text-align:left;color:{accent};border-bottom:1px solid {border_color};font-weight:bold">{title}</th>'
        f'<th style="padding:10px;text-align:left;color:{dim_color};border-bottom:1px solid {border_color};font-weight:bold">competitor</th>'
        '</tr></thead><tbody>'
        + "".join(
            f'<tr><td style="padding:10px;vertical-align:top;color:{text_color};font-weight:bold;border-bottom:1px solid {border_color}">{competitor}</td>'
            f'<td style="padding:10px;vertical-align:top;color:{accent};border-bottom:1px solid {border_color};line-height:1.6">{advantage}</td>'
            f'<td style="padding:10px;vertical-align:top;color:{dim_color};border-bottom:1px solid {border_color};line-height:1.6">{them}</td></tr>'
            for competitor, advantage, them in competitors
        )
        + "</tbody></table>"
    )
    faq_html = "".join(
        f'<details style="background:{surface_card};border:1px solid {border_color};border-radius:6px;'
        f'padding:14px 18px;margin-bottom:8px">'
        f'<summary style="font-size:12px;color:{accent};font-weight:bold;cursor:pointer;list-style:none">'
        f'▸ {q}</summary>'
        f'<div style="font-size:11px;color:{text_color};line-height:1.7;margin-top:10px;padding-top:10px;'
        f'border-top:1px solid {border_color}">{a}</div>'
        f"</details>"
        for q, a in faq
    )
    secondary_demo_block = (
        f'<h2 id="demo2">{secondary_demo_title}</h2>'
        f'<div class="demo-box">{secondary_demo_html}</div>'
    ) if secondary_demo_html else ""
    secondary_demo_script_block = secondary_demo_script if secondary_demo_script else ""
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
  nav .nav-links {{ margin-left: auto; display: flex; gap: 14px; align-items: center; font-size: 11px; }}
  nav .nav-links a {{ color: {dim_color}; }}
  nav .nav-links a:hover {{ color: {accent}; }}
  .container {{ max-width: 1000px; margin: 0 auto; padding: 24px 28px; }}
  .hero {{ background: linear-gradient(180deg, {surface_card} 0%, {surface_bg} 100%);
          border: 1px solid {border_color}; border-radius: 10px; padding: 32px 36px;
          margin-bottom: 24px; }}
  .hero .tag {{ font-size: 10px; color: {dim_color}; letter-spacing: 0.25em;
               text-transform: uppercase; margin-bottom: 6px; }}
  .hero h1 {{ font-size: 28px; color: {accent}; margin-bottom: 6px; font-weight: bold;
              letter-spacing: 0.3px; }}
  .hero .tagline {{ font-size: 13px; color: {dim_color}; margin-bottom: 20px; font-style: italic; }}
  .ps-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 28px; }}
  .ps-card {{ background: {surface_card}; border: 1px solid {border_color}; border-radius: 8px; padding: 18px 22px; }}
  .ps-card .label {{ font-size: 10px; letter-spacing: 0.2em; text-transform: uppercase; margin-bottom: 8px; font-weight: bold; }}
  .ps-card .body {{ font-size: 12px; line-height: 1.7; color: {text_color}; }}
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
  .how-grid {{ display: flex; gap: 14px; flex-wrap: wrap; margin: 16px 0 28px; }}
  .final-cta {{ background: linear-gradient(135deg, rgba({accent_rgb}, 0.15) 0%, {surface_card} 100%);
                border: 1px solid {accent}; border-radius: 10px; padding: 28px 32px;
                margin: 32px 0 24px; text-align: center; }}
  .final-cta .headline {{ font-size: 18px; color: {accent}; font-weight: bold; margin-bottom: 8px; }}
  .final-cta .body {{ font-size: 12px; color: {text_color}; line-height: 1.7; margin-bottom: 16px; }}
  details summary {{ outline: none; }}
  details[open] summary {{ color: {accent}; }}
  table {{ background: {surface_card}; border: 1px solid {border_color}; border-radius: 8px; overflow: hidden; }}
  @media (max-width: 700px) {{
    .container {{ padding: 16px; }}
    .hero {{ padding: 22px; }}
    .hero h1 {{ font-size: 22px; }}
    .ps-grid {{ grid-template-columns: 1fr; }}
    nav .nav-links {{ width: 100%; margin-left: 0; }}
  }}
</style>
</head>
<body>
<nav>
  <span class="brand">{title}</span>
  <span class="badge">{status_badge}</span>
  <span style="font-size:10px;color:{dim_color}">a {parent_name} product</span>
  <div class="nav-links">
    <a href="#demo">Demo</a>
    <a href="#use-cases">Use cases</a>
    <a href="#integrate">Integration</a>
    <a href="#pricing">Pricing</a>
    <a href="#faq">FAQ</a>
    <a href="{parent_path}">&larr; {parent_name}</a>
  </div>
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

  <div class="ps-grid">
    <div class="ps-card" style="border-left:3px solid #f06292">
      <div class="label" style="color:#f06292">THE PROBLEM</div>
      <div class="body">{problem}</div>
    </div>
    <div class="ps-card" style="border-left:3px solid {accent}">
      <div class="label" style="color:{accent}">THE FIX</div>
      <div class="body">{solution}</div>
    </div>
  </div>

  <h2>How it works</h2>
  <div class="how-grid">{how_it_works_html}</div>

  <h2>What it does</h2>
  {capability_html}

  <h2 id="demo">Live demo</h2>
  <div class="demo-box">
    {demo_html}
  </div>

  {secondary_demo_block}

  <h2 id="use-cases">Use cases</h2>
  {use_cases_html}

  <h2>How {title} compares</h2>
  {competitor_html}

  <h2 id="integrate">Integration path</h2>
  {integration_html}

  <h2 id="pricing">Pricing</h2>
  <div class="pricing-row">{pricing_html}</div>

  <h2 id="faq">Frequently asked</h2>
  {faq_html}

  <div class="final-cta">
    <div class="headline">{final_cta}</div>
    <div class="body">Built on PEP primitives. Part of the LAVAS suite. Same engine you can inspect at <a href="/pep">/pep</a>.</div>
    <button class="cta">Start free trial</button>
    <button class="cta-secondary">Talk to the team</button>
  </div>

  <div style="margin-top:32px;padding:20px;background:{surface_card};border:1px solid {border_color};border-radius:8px">
    <div style="font-size:11px;color:{dim_color};line-height:1.7">
      <b style="color:{text_color}">{title}</b> is a product of <a href="{parent_path}">{parent_name}</a>,
      part of the LAVAS suite by PEP Labs. Built on PEP (Predictive Encoding and Preparation) primitives.
      For more information, see the {parent_name} app at <a href="{parent_path}">{parent_path}</a>
      or the engine at <a href="/pep">/pep</a>.
    </div>
  </div>
</div>

<script>{demo_script}
{secondary_demo_script_block}
</script>
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
        problem="You ship a prompt. The model behaves weirdly in production. You add &quot;please be careful&quot; and &quot;think step by step&quot; and four more rules. The prompt grows to 5,000 tokens. Nothing improves. You have no theory of why &mdash; just a folk-wisdom belief that more instructions = better output. Token cost climbs; quality plateaus.",
        solution="Treat your prompt as a linguistic object. Tokenize it into instruction / context / examples / constraints / output spec. Score each span on how much it actually constrains the model. Flag redundant instructions, conflicting constraints, and attention-diluting context. Get a compressed rewrite that preserves behavior. Test changes structurally before spending tokens.",
        how_it_works=[
            ("Parse the prompt", "Tokenize the prompt and segment it into recognized roles: instruction, context, few-shot examples, output spec, constraints, persona. Each segment gets its own structural analysis."),
            ("Score constraint strength", "For each segment, estimate how strongly it constrains the model's next-token distribution. Strong constraints (output format, hard rules) anchor behavior; weak ones (politeness, vague exhortations) waste tokens."),
            ("Diagnose failure modes", "Match the prompt against a library of structural antipatterns: instruction overrides by examples, format-spec collisions, attention dilution from over-long context, conflicting constraints. Flag specifically what is likely to break."),
            ("Suggest the rewrite", "Return a compressed version that preserves the strong constraints, drops the weak ones, and resolves conflicts. Typical 30-50% token reduction with no behavior change."),
        ],
        capabilities=[
            ("Structural analysis", "Tokenizes the prompt into instruction, context, examples, constraints, and output spec. Highlights which spans constrain output strongly vs weakly."),
            ("Compression suggestions", "Identifies redundant tokens (repeated instructions, throat-clearing, low-information context) with concrete cuts that preserve behavior. Typical 30-50% compression with no quality loss."),
            ("Failure-mode prediction", "Flags structural patterns that historically lead to specific failures: instruction overrides by examples, format-spec collisions, attention dilution from over-long context, conflicting constraints."),
            ("A/B compare", "Side-by-side structural diff between two prompts. Shows what changed and predicts how the change shifts model behavior before you spend tokens testing."),
            ("Cost forecasting", "Token count + estimated API cost per provider (OpenAI, Anthropic, Google, Meta). Suggests cheapest model that meets your structural constraints."),
            ("Pattern library", "200+ named prompt patterns (chain-of-thought, ReAct, self-consistency, JSON-mode shaping, persona-priming) with structural fingerprints. Recognize what your prompt is doing and suggest established alternatives."),
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
        secondary_demo_title="Cost across providers",
        secondary_demo_html="""
<div style="font-size:11px;color:#7a8492;margin-bottom:10px">Estimated monthly cost based on the prompt above and your daily volume. Lingora Prompt's compressed rewrite cuts cost without changing behavior.</div>
<div style="display:flex;gap:14px;flex-wrap:wrap;align-items:center;margin-bottom:14px">
  <label style="font-size:11px;color:#e0e6ed;display:flex;align-items:center;gap:8px">
    <span>requests/day:</span>
    <input type="range" id="cost-vol" min="100" max="100000" value="10000" step="100" style="width:180px" oninput="updateCost()">
    <span id="cost-vol-val" style="color:#ba68c8;font-weight:bold;min-width:60px">10,000</span>
  </label>
</div>
<table style="width:100%;border-collapse:collapse;font-size:11px;background:#0a0e16;border:1px solid #2a3140;border-radius:4px;overflow:hidden">
  <thead><tr style="background:#161c28">
    <th style="padding:10px;text-align:left;color:#7a8492">Provider · Model</th>
    <th style="padding:10px;text-align:right;color:#a78bfa">Original</th>
    <th style="padding:10px;text-align:right;color:#a3e635">Compressed</th>
    <th style="padding:10px;text-align:right;color:#a3e635">Savings/mo</th>
  </tr></thead>
  <tbody id="cost-table"></tbody>
</table>
        """,
        secondary_demo_script="""
const PROVIDERS = [
  { name: 'OpenAI · GPT-4o', input: 2.50, output: 10.00 },
  { name: 'OpenAI · GPT-4o mini', input: 0.15, output: 0.60 },
  { name: 'Anthropic · Claude Opus 4', input: 15.00, output: 75.00 },
  { name: 'Anthropic · Claude Sonnet 4', input: 3.00, output: 15.00 },
  { name: 'Anthropic · Claude Haiku 4.5', input: 0.25, output: 1.25 },
  { name: 'Google · Gemini 2.5 Pro', input: 1.25, output: 5.00 },
  { name: 'Meta · Llama 3.1 405B', input: 0.90, output: 0.90 },
];
function updateCost() {
  const vol = parseInt(document.getElementById('cost-vol').value);
  document.getElementById('cost-vol-val').textContent = vol.toLocaleString();
  const origTokensIn = 50, compTokensIn = 28, tokensOut = 60;
  const tbody = document.getElementById('cost-table');
  tbody.innerHTML = PROVIDERS.map(p => {
    const origMo = (vol * 30 * (origTokensIn * p.input + tokensOut * p.output) / 1000000);
    const compMo = (vol * 30 * (compTokensIn * p.input + tokensOut * p.output) / 1000000);
    const save = origMo - compMo;
    return '<tr style="border-top:1px solid #2a3140">' +
      '<td style="padding:8px 10px;color:#e0e6ed">' + p.name + '</td>' +
      '<td style="padding:8px 10px;text-align:right;color:#a78bfa">$' + origMo.toFixed(2) + '</td>' +
      '<td style="padding:8px 10px;text-align:right;color:#a3e635">$' + compMo.toFixed(2) + '</td>' +
      '<td style="padding:8px 10px;text-align:right;color:#a3e635;font-weight:bold">$' + save.toFixed(2) + '</td>' +
    '</tr>';
  }).join('');
}
updateCost();
        """,
        use_cases=[
            ("ML platform engineer at a 50-person startup",
             "Inherits a 4,000-token system prompt that 'works' but nobody knows why. Shipping API costs are $18K/month. Cannot iterate on the prompt without breaking production behavior.",
             "Lingora Prompt analyzes the existing prompt, identifies which spans actually constrain behavior, suggests a 1,800-token rewrite that preserves the same outputs. API costs drop to $8K/month. Documented structural analysis lets the team iterate confidently."),
            ("Indie developer building an AI app",
             "Iterating on a customer-support prompt. Each test costs real tokens. Hard to tell why one version performs better than another beyond vibes.",
             "A/B compare in Lingora Prompt shows the structural diff between versions and predicts behavior shifts before any LLM call. Ships better prompts faster, with a 60% reduction in iteration token spend."),
            ("Enterprise AI architect",
             "200+ prompts across 14 services. No structural standard. Each team owner writes prompts differently. No way to audit collectively.",
             "Lingora Prompt's CI integration scans every prompt change in PR. Enforces a structural style guide; flags regressions; surfaces patterns ripe for a shared library. Centralized prompt audit becomes possible without a manual review process."),
            ("LLM researcher running ablation studies",
             "Want to study how prompt structure affects output quality. No good tool for measuring 'how prompty' a prompt is or comparing structural features across hundreds of variants.",
             "Lingora Prompt's API exposes the structural feature vector per prompt. Researcher can correlate structural features with eval scores at scale, publish findings on what structurally distinguishes prompts that work."),
        ],
        competitors=[
            ("Manual prompt iteration (status quo)",
             "Structural analysis: see why a prompt does what it does. A/B compare without spending tokens. Compression with behavior preservation.",
             "Trial and error. Folk-wisdom advice. No structural feedback. Token-spending iterations."),
            ("Prompt management tools (PromptHub, PromptLayer)",
             "Same versioning + analytics, plus structural intelligence. Tells you why one version performs better than another, not just that it does.",
             "Versioning, A/B testing on outputs, eval tracking. Black-box about what structurally differs between variants."),
            ("LLM eval platforms (Braintrust, Langfuse)",
             "Pre-LLM analysis layer. Catches problems at structural level before any expensive eval run.",
             "Post-LLM eval. Tells you what failed. Does not tell you what structurally caused the failure."),
            ("Generic linters (markdown, prose linters)",
             "Designed for prompts specifically. Knows the patterns and antipatterns of LLM instruction.",
             "Generic English advice. Optimizes for prose, not for model behavior."),
        ],
        integration_steps=[
            ("Drop in the SDK", "pip install lingora-prompt or npm install @lingora/prompt. One-line import in your existing prompt-iteration workflow."),
            ("Paste your prompt", "Pass any prompt string to the analyzer. Returns a structured report with findings, compression suggestions, and predicted failure modes."),
            ("Iterate", "Apply suggested rewrites, re-analyze, ship. The toolkit lets you iterate on prompt structure without spending tokens on the LLM at every step."),
            ("(Optional) CI integration", "Hook the analyzer into CI to flag prompt regressions: anyone who increases token count without adding new constraints gets a warning on PR."),
            ("(Optional) Pattern library access", "Subscribe to the curated 200+ pattern library and the structural style guide. Standardize prompt design across your team."),
        ],
        pricing_tiers=[
            ("Free", "$0 / mo", "Web analyzer, up to 100 prompts/mo, no API access. For solo developers."),
            ("Pro", "$29 / mo", "Unlimited web + API access, 10K analyses/mo, A/B compare, CI integration."),
            ("Team", "$199 / mo", "Up to 20 seats, 100K analyses/mo, prompt versioning, team prompt library."),
            ("Enterprise", "Custom", "SSO, audit logs, on-prem option, custom pattern libraries, dedicated success engineer."),
        ],
        faq=[
            ("Does Lingora Prompt call the LLM to analyze prompts?",
             "No. The analysis is purely structural — tokenization, role segmentation, antipattern detection. Zero LLM tokens spent. The whole point is that you can iterate without paying for inference at every step."),
            ("How is this different from just reading good prompt engineering blog posts?",
             "Blog posts give you general advice. Lingora Prompt analyzes your specific prompt and tells you what is wrong with it. Personalized linting beats generic style guides for code; same applies to prompts."),
            ("Will the compressed rewrite preserve my exact output behavior?",
             "Behavior is preserved at the structural level — strong constraints stay strong, weak ones get dropped or consolidated. We recommend regression-testing on your eval set before shipping. The CI integration automates this."),
            ("Does it work for non-English prompts?",
             "Yes. The structural analysis is language-agnostic. Antipattern detection works on any prompt that uses standard LLM instruction conventions. Pattern library is currently English-focused; multilingual library is on the roadmap."),
            ("Can I keep my prompts private?",
             "Yes. Self-hosted deployment available on Pro and above. Free tier sends prompt text to the analysis API but never stores it. Enterprise tier supports VPC deployment and never sends prompt content outside your infrastructure."),
            ("What about agent prompts that change at runtime?",
             "The SDK exposes a runtime analyzer that scores generated prompts in real time. Useful for agent frameworks where the system prompt is composed dynamically — catch regressions before the agent burns tokens on a malformed prompt."),
        ],
        final_cta="Stop spending tokens to debug prompts. Start spending tokens to ship behavior.",
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
        problem="Players quit. Not because of bugs or balance &mdash; because the matches feel bad. Mismatched tempos, mismatched goals, mismatched communication styles. Your Elo says 50/50; the players are mute on voice, AFK by minute three, never queue again. You have tried tuning the rating window, the K-factor, and the queue timeout. Nothing moves session length more than a few percent.",
        solution="Replace the matchmaking objective. Instead of balanced win probability, target <b>rematch rate</b> &mdash; whether both players queue again immediately. Rematch rate captures what &quot;good match&quot; actually means to players, is cheap to measure (no surveys), and correlates with every downstream metric you care about (session length, retention, NPS, LTV). The graph-based engine surfaces compatible opponents your rating-window scan misses.",
        how_it_works=[
            ("Build the compatibility graph", "Players are nodes; edges carry weights across skill, tempo, communication, role preference, tilt tolerance, session goal, and recent behavior. Updates incrementally as matches resolve and behavior signals arrive."),
            ("Spread activation from the seed", "When a player queues, activation radiates from their node through weighted edges with decay. The candidate pool emerges from the graph neighborhood &mdash; not a sorted rating list. Pool shape adapts to the player; it is not a window translation."),
            ("Score on multi-objective consensus", "Each candidate match scored across all objective dimensions with configurable weights. The match with the highest consensus wins, not the closest Elo. Per-studio tuning lets you weight skill more (esports), social more (party games), or experience more (casual)."),
            ("Close the residual loop", "Post-match, the actual rematch outcome updates the predictor. The residual (predicted vs actual rematch) is the learning signal &mdash; the matcher gets better automatically as the playerbase shifts. No manual K-factor tuning."),
        ],
        capabilities=[
            ("Pool formation via spreading activation", "Replaces sorted rating windows with graph-based candidate pools. Players are nodes; compatibility weights are edges; activation spreads from the seed player. Result: pools shaped by actual fit, not just rank proximity."),
            ("Multi-objective scoring", "Each candidate match scored across skill, tempo, role, communication style, tilt tolerance, and goal alignment. The match with the highest consensus wins, not the closest Elo."),
            ("Behavior modulation", "Recent toxicity, AFK, throwing, and pro-social signals modulate edge weights live. Toxic players get matched with each other; pro-social players surface as good fits for new players."),
            ("Cold-start handling", "Glicko-style uncertainty for new players. Wide initial pools that contract as confidence builds. No more new-player stomp."),
            ("Smurf detection", "Feature-vector anomaly detection on accounts with mechanical signatures inconsistent with their rating. Routes detected smurfs into appropriate pools without bans."),
            ("Party-aware pooling", "Treats parties as joint seeds with intersection-constrained pools. No more 5-stack vs 5-solo mismatches; party-friend constraints are part of the optimization, not a fail-fast filter."),
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
        secondary_demo_title="Tune the matchmaker",
        secondary_demo_html="""
<div style="font-size:11px;color:#6b8088;margin-bottom:10px">Adjust the objective weights. Sliders shift how Atria scores candidate matches; the chart shows the effect on rematch rate, average queue time, and toxic-adjacent rate over a 1,000-match simulation.</div>
<div style="display:grid;grid-template-columns:140px 1fr 50px;gap:10px 16px;align-items:center;font-size:11px;margin-bottom:14px">
  <span>skill weight</span>
  <input type="range" id="w-skill" min="0" max="100" value="40" oninput="updateAtriaTune()">
  <span id="w-skill-v" style="color:#5eead4;font-weight:bold">40</span>
  <span>tempo weight</span>
  <input type="range" id="w-tempo" min="0" max="100" value="20" oninput="updateAtriaTune()">
  <span id="w-tempo-v" style="color:#5eead4;font-weight:bold">20</span>
  <span>social weight</span>
  <input type="range" id="w-social" min="0" max="100" value="15" oninput="updateAtriaTune()">
  <span id="w-social-v" style="color:#5eead4;font-weight:bold">15</span>
  <span>behavior weight</span>
  <input type="range" id="w-behav" min="0" max="100" value="25" oninput="updateAtriaTune()">
  <span id="w-behav-v" style="color:#5eead4;font-weight:bold">25</span>
</div>
<canvas id="atria-tune-canvas" width="600" height="220" style="width:100%;background:#0a1014;border:1px solid #1f2c34;border-radius:4px"></canvas>
        """,
        secondary_demo_script="""
function updateAtriaTune() {
  const s = parseInt(document.getElementById('w-skill').value);
  const t = parseInt(document.getElementById('w-tempo').value);
  const so = parseInt(document.getElementById('w-social').value);
  const b = parseInt(document.getElementById('w-behav').value);
  document.getElementById('w-skill-v').textContent = s;
  document.getElementById('w-tempo-v').textContent = t;
  document.getElementById('w-social-v').textContent = so;
  document.getElementById('w-behav-v').textContent = b;
  const total = s + t + so + b;
  const balance = 1 - Math.abs(s - 25) / 100 - Math.abs(t - 25) / 100;
  const rematch = 0.40 + (so + b) / 200 + balance * 0.15;
  const queue = 12 + (b + so) / 8 - s / 10;
  const toxic = Math.max(0.05, 0.20 - b / 250);
  const c = document.getElementById('atria-tune-canvas');
  const ctx = c.getContext('2d');
  ctx.fillStyle = '#0a1014'; ctx.fillRect(0, 0, c.width, c.height);
  const metrics = [
    { label: 'Rematch rate', v: Math.min(1, rematch), fmt: v => (v*100).toFixed(0)+'%', col: '94,234,212' },
    { label: 'Avg queue (s)', v: Math.min(1, queue / 30), fmt: v => (v*30).toFixed(0)+'s', col: '251,191,36' },
    { label: 'Toxic-adjacent', v: Math.min(1, toxic), fmt: v => (v*100).toFixed(1)+'%', col: '248,113,113' },
  ];
  metrics.forEach((m, j) => {
    const y = 30 + j * 60;
    ctx.fillStyle = '#dcecec'; ctx.font = 'bold 11px monospace'; ctx.fillText(m.label, 10, y);
    ctx.fillStyle = 'rgba(' + m.col + ',0.2)'; ctx.fillRect(10, y+8, 580, 22);
    ctx.fillStyle = 'rgba(' + m.col + ',0.85)'; ctx.fillRect(10, y+8, 580*m.v, 22);
    ctx.fillStyle = '#fff'; ctx.font='11px monospace'; ctx.textAlign='right'; ctx.fillText(m.fmt(m.v), 585, y+24); ctx.textAlign='left';
  });
}
updateAtriaTune();
        """,
        use_cases=[
            ("Director of online services at a major studio",
             "Flagship competitive shooter has plateaued at 60% retention week-1. Player surveys consistently call out match quality. Internal tuning has not moved the metric in 6 months. Engagement-matchmaking patent has been floated and rejected for ethics reasons.",
             "Atria Match in shadow mode for 2 weeks confirms a 22% rematch-rate lift. A/B test for 4 weeks ships the engine to a percentage of matches; the test cohort shows +15% week-1 retention and -28% support tickets about matchmaking. Full rollout in 12 weeks."),
            ("Lead designer of a new esports title",
             "Pre-launch. Rating system not yet picked. Founders have read the Activision patent and want to ship something honest. Want a system that works for both the casual entry-level and the competitive top.",
             "Atria Match shipped at launch with two configured objective profiles: casual (heavy social and behavior weights) and ranked (heavy skill and role weights). Same engine, two presets. Players can toggle. Launch metrics outperform comparable titles on rematch rate at 3 months."),
            ("Studio with a chronic toxicity problem in voice chat",
             "Voice chat toxicity has a measurable effect on retention. Reports + bans handle the worst offenders but the gradient (bad teammates, mute-and-go, casual slurs) goes untouched. Player base is split: hardcore wants voice; casual wants out.",
             "Atria Match's behavior modulator routes recent-toxic players preferentially to each other, not to sensitive teammates. Toxic-adjacent match rate drops 35%. Players who mute chat or use friend-only voice get pooled accordingly. Net retention up; reports decline."),
            ("Indie studio with a small but devoted player base",
             "5,000 daily actives. Off-peak queue times are brutal. Players give up after 90 seconds and play something else. Cannot afford to lose them.",
             "Atria Match's urgency dial widens decay automatically when pool density drops. Off-peak matches are looser-fit but still play within 30 seconds. Players come back. Pool grows; the dial tightens automatically as density returns."),
        ],
        competitors=[
            ("Elo / Glicko / TrueSkill",
             "Multi-dimensional graph. Optimizes rematch rate, not win-prob balance. Behavior is a first-class signal. Cold-start uncertainty without separate logic.",
             "Single-scalar rating. Optimizes balanced win probability (which is not match quality). No behavior signal. Cold-start hacked on with K-factor."),
            ("OpenSkill / Bayesian rating systems",
             "Same Bayesian uncertainty plus the multi-dimensional graph and learnable objective. Outputs a rating compatible with your existing display.",
             "Better cold-start than Elo. Still scalar. Same wrong objective."),
            ("Activision-style engagement matchmaking",
             "Same revenue outcome (longer sessions, higher LTV) through actual enjoyment. No dark pattern, no class-action risk.",
             "Patent-flagged. Drives engagement through frustration. Player perception risk; press risk; legal risk."),
            ("In-house custom matchmaker",
             "Off-the-shelf engine, customized to your game's objectives. Lower upfront cost, faster to ship, ongoing improvement from cross-studio learning.",
             "Built by your team. Maintained by your team. Improved on your team's clock. Hard to staff a matchmaking specialist."),
        ],
        integration_steps=[
            ("Phase 1 — Shadow mode (2 weeks)", "Atria runs alongside your existing matchmaker. Both produce match suggestions; only the existing system goes live. Compare predictions. No risk."),
            ("Phase 2 — A/B test (4 weeks)", "Route a percentage of matches through Atria. Measure rematch rate, session length, complaints. Self-evaluating — roll back at no cost if it does not lift metrics."),
            ("Phase 3 — Full rollout", "Replace pool selection with Atria. Keep your existing rating system for display/rank; Atria sits underneath as the pool-formation and scoring layer."),
            ("Latency budget", "Pool formation is a single graph walk (~2-8ms for 100K-player pools). Multi-objective scoring is a dot product per candidate (~0.01ms). Total added latency under 20ms — your queue timeout dwarfs this."),
            ("Continuous tuning", "The objective-weight dashboard lets you re-tune for new game modes, seasonal events, or shifts in player population without code changes."),
        ],
        pricing_tiers=[
            ("Indie", "$2K / mo", "Up to 50K MAU, hosted scoring API, standard objectives. For studios with one PvP title."),
            ("Studio", "$15K / mo", "Up to 1M MAU, custom objective tuning, behavior signals, dedicated success engineer."),
            ("Enterprise", "Custom", "Unlimited scale, on-prem or VPC deploy, custom integration, white-label option."),
        ],
        faq=[
            ("Will Atria Match break our existing rating display?",
             "No. Atria sits beneath your rating system. We use Elo/Glicko/TrueSkill ratings as input to the graph and as one objective dimension. The visible rank players see does not change unless you want it to."),
            ("How much does pool spreading cost in latency?",
             "Pool formation is a single graph walk: 2-8ms for a 100K-player active pool, scales sub-linearly. Multi-objective scoring is a dot product per candidate (~0.01ms). Total added latency is under 20ms, dominated by your existing queue timeout."),
            ("What if my players hate it?",
             "The A/B test phase is exactly designed to catch this. Roll back at any time at no cost. We have not seen a deployment where rematch and session-length metrics declined in test, but the structure is built to surface that fast if it happens."),
            ("How is this different from engagement matchmaking?",
             "Engagement matchmaking optimizes for player frustration that drives in-game purchase. Atria optimizes for player enjoyment that drives session length. Same downstream business outcome (more revenue) through opposite mechanisms. The Activision patent is the dark-pattern version; Atria is the honest version."),
            ("Can we feed in our own behavior signals?",
             "Yes. The behavior modulator takes any signal you can measure: in-game reports, voice-chat sentiment analysis, ping/jitter, AFK rate, throw detection. Studio-specific signals weighted alongside platform defaults."),
            ("How do you handle anti-cheat?",
             "Detected cheaters get routed into a separate pool (similar to chess.com's anti-cheat matchmaking). The smurf detector handles unranked-skill mismatches; explicit cheat-detection signals from your anti-cheat system handle confirmed cases. Both modulate the graph rather than triggering bans."),
        ],
        final_cta="Stop tuning Elo. Start optimizing for rematch.",
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
        problem="Catastrophic errors are caused by cognitive depletion that nobody detected in time. The surgeon at hour 4 of a 6-hour case. The pilot 7 hours into a transatlantic flight. The esports pro on tilt entering a critical match. The pattern is the same: the operator's cognitive state degraded before the error, and no instrument was watching. Heart-rate trackers and pulse oximeters measure the wrong thing.",
        solution="Continuous monitoring of the four-axis cognitive state space (novelty, coherence, bandwidth, valence) with personalized thresholds. Real-time alerts when state degrades; predictive alerts 30-60 minutes before forecast depletion; post-event reconstruction so coaches and supervisors can learn what conditions produce flow vs collapse. The instrument that should have been there.",
        how_it_works=[
            ("Connect existing telemetry", "Edge pulls from sensors the operator already has: HRV from Apple Watch / Whoop / Polar, EEG from Muse / Neurosity, behavioral telemetry from input devices and game/sim/EHR data. No new hardware required for most use cases."),
            ("Calibrate the baseline", "1-week calibration period learns the operator's individual state-space coordinates and thresholds. No population-average defaults; everything personalized to the specific operator's normal."),
            ("Monitor in real time", "Continuous mapping of incoming telemetry into the four-axis state space. Coherence, bandwidth, novelty, and valence updated every few seconds. Alert thresholds fire to the operator, supervisor, or coach per configuration."),
            ("Forecast depletion", "Trajectory analysis predicts cognitive depletion 30-60 minutes ahead based on current state-space velocity. Allows preemptive intervention (break, rotation, hand-off) before bandwidth crosses a safety threshold."),
        ],
        capabilities=[
            ("Flow state detection", "Continuous monitoring of the cognitive state space (novelty / coherence / bandwidth / valence). Flags when the operator enters or exits flow with high precision."),
            ("Bandwidth alerts", "Real-time bandwidth gauge. Alerts when free cognitive capacity drops below operator-configured safe thresholds. Pre-event readiness score lets supervisors hold an operator out of high-stakes work when they're depleted."),
            ("Tilt detection (esports)", "Detects emotional state disrupting coherence. Coaches see the moment a player tilts, not after the loss. Replay analysis tied to specific tilt events."),
            ("Fatigue forecasting", "Predicts cognitive depletion 30-60 minutes ahead based on current state-space trajectory. Alerts surgeons during long procedures, pilots on long flights, before errors compound."),
            ("Post-event analysis", "Reconstructs the cognitive state trajectory across the event. Identifies exactly when state degraded, what triggered it, and which interventions would have mattered."),
            ("Cohort comparisons", "For coaches and supervisors: see the cognitive-state distribution across your team during a match, shift, or training session. Flag operators trending toward depletion before the next high-stakes call."),
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
        secondary_demo_title="Bandwidth trajectory",
        secondary_demo_html="""
<div style="font-size:11px;color:#8a7a8e;margin-bottom:10px">A 4-hour procedure visualized. Bandwidth declines under sustained focus; the trajectory analyzer forecasts depletion 30 minutes ahead and recommends a break before the safety threshold is crossed.</div>
<canvas id="edge-traj-canvas" width="600" height="240" style="width:100%;background:#0d0a14;border:1px solid #2c2236;border-radius:4px"></canvas>
        """,
        secondary_demo_script="""
function drawEdgeTraj() {
  const c = document.getElementById('edge-traj-canvas');
  const ctx = c.getContext('2d');
  const W = c.width, H = c.height;
  ctx.fillStyle = '#0d0a14'; ctx.fillRect(0, 0, W, H);
  // safety threshold at 0.3
  ctx.strokeStyle = 'rgba(248,113,113,0.5)'; ctx.setLineDash([4,4]); ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(40, H * 0.7); ctx.lineTo(W - 20, H * 0.7); ctx.stroke();
  ctx.fillStyle = '#f06292'; ctx.font = '10px monospace'; ctx.fillText('safety threshold (0.30)', 40, H * 0.7 - 4);
  ctx.setLineDash([]);
  // trajectory
  ctx.strokeStyle = '#ffb74d'; ctx.lineWidth = 2;
  ctx.beginPath();
  for (let x = 40; x < W - 20; x++) {
    const t = (x - 40) / (W - 60);
    const y = H * (0.18 + 0.62 * t + 0.04 * Math.sin(t * 8));
    if (x === 40) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  }
  ctx.stroke();
  // forecast extension (dashed)
  ctx.strokeStyle = 'rgba(255,183,77,0.5)'; ctx.setLineDash([3,3]); ctx.lineWidth = 1.5;
  ctx.beginPath();
  for (let x = W - 20; x < W + 60; x++) {
    const t = (x - 40) / (W - 60);
    const y = H * (0.18 + 0.62 * t + 0.04 * Math.sin(t * 8));
    if (x === W - 20) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  }
  ctx.stroke();
  ctx.setLineDash([]);
  // axis labels
  ctx.fillStyle = '#8a7a8e'; ctx.font = '10px monospace'; ctx.textAlign='left';
  ctx.fillText('100% bandwidth', 40, 16);
  ctx.fillText('hour 0', 40, H - 4);
  ctx.fillText('hour 4', W / 2 - 20, H - 4);
  ctx.fillText('forecast →', W - 80, H - 4);
  // alert annotation
  ctx.fillStyle = '#f06292'; ctx.font = 'bold 11px monospace'; ctx.textAlign='center';
  ctx.fillText('⚠ depletion forecast in 28 min — recommend break', W * 0.65, 30);
}
drawEdgeTraj();
        """,
        use_cases=[
            ("Cardiac surgeon performing a CABG",
             "4-6 hour procedure. Bandwidth typically degrades after hour 3. Errors in the back half of long cases are documented in the literature but operationally invisible.",
             "Edge calibrates to the surgeon's individual baseline over a week. During the procedure, bandwidth is monitored continuously. Forecast alerts the supervising attending 30 min before the depletion threshold; team rotation happens preemptively. Reduces late-procedure error rate."),
            ("Pro esports player on a long-form tournament day",
             "Six-match BO3 tournament across 10 hours. Tilt after a critical loss is the dominant performance killer. Coach can see the loss in scoreboard but not the tilt in the player.",
             "Edge detects coherence collapse mid-match. Coach gets an alert with seconds of latency: time-out, tactical reset, breathing protocol. Tilt cascade prevented. Retrospectively, coach reviews state trajectory tied to match events to teach the player triggers."),
            ("Long-haul commercial pilot",
             "8+ hour transatlantic. Two-pilot rotation. Fatigue is governed by hours-of-service rules but those rules are population averages, not personalized.",
             "Edge personalizes the depletion forecast per pilot. The captain sees a private bandwidth gauge and gets recommended hand-off windows aligned to actual cognitive state, not just elapsed hours. Reduces late-flight performance variance."),
            ("Special forces operator",
             "High-stakes mission window. Pre-mission readiness assessment is currently a self-report checklist plus a medic's gut. Operator may push through when not actually fit.",
             "Edge's pre-event readiness score is the objective check. Medic and team lead see the same data. Operator gets pulled when the data says pull, not when the operator admits weakness — which is approximately never."),
        ],
        competitors=[
            ("Whoop / Oura / Apple Watch",
             "Pulls from these sensors as inputs, then maps them into actual cognitive state space, not just physiological proxies. HRV is one signal among many.",
             "Measure heart rate, HRV, sleep duration, recovery score. Useful but indirect. None of them measure cognitive bandwidth directly."),
            ("Self-report checklists (NASA-TLX, Karolinska)",
             "Continuous, objective, real-time. No interrupting the operator to ask &quot;how depleted do you feel?&quot;",
             "Validated instruments but require the operator to stop and self-assess. Subject to demand effects and cannot be done during a procedure."),
            ("Workplace surveillance / productivity trackers",
             "Built for the operator, not against them. Privacy-first by default. Coach/supervisor sees only what the operator authorizes.",
             "Built to monitor employees. Surveillance overtones make adoption hostile and reduce signal quality (operators learn to game them)."),
            ("Coach / supervisor intuition",
             "Augments, does not replace. Coaches still make the call; Edge gives them objective data to base it on. Trains the coach&apos;s pattern recognition over time.",
             "The current standard. Excellent in experienced coaches; absent in junior ones; biased and unmeasurable in everyone."),
        ],
        integration_steps=[
            ("Sensor integration", "Pulls from existing telemetry: HR/HRV from Apple Watch / Whoop / Polar, EEG from Muse / Neurosity, behavioral from input devices. No new hardware required for most use cases."),
            ("Calibration period (1 week)", "Edge learns the operator's baseline state-space coordinates. Personalized thresholds, not population averages."),
            ("Live deployment", "Continuous monitoring with configurable alert routing — to the operator, to a coach/supervisor, or both. Privacy-first: data stays on-device by default."),
            ("Post-event review", "Optional cloud sync for retrospective analysis. Coaches and operators review state trajectories tied to specific events to learn what conditions produce flow vs collapse."),
            ("Team integration", "For coaches and supervisors managing multiple operators, the Cohort dashboard shows aggregate state across the team. Operator-level data only with consent."),
        ],
        pricing_tiers=[
            ("Individual", "$49 / mo", "Personal account, 1 device, basic alerts, 30-day history. For solo athletes and pros."),
            ("Team", "$499 / mo", "Up to 25 operators, coach dashboard, team analytics, full history. For sports teams and small clinics."),
            ("Enterprise", "Custom", "Unlimited operators, SSO, on-prem option, custom integrations. For hospitals, airlines, military."),
        ],
        faq=[
            ("Is Axona Edge a medical device?",
             "No. Edge is performance-monitoring software. It does not diagnose, treat, or prescribe. Clinical-decision-support framing means a much faster regulatory path. We are pursuing FDA clearance for specific use cases (surgery scheduling) on a separate track."),
            ("How accurate is the bandwidth estimate without an EEG?",
             "Multi-sensor fusion (HRV + behavioral + sim/game/EHR telemetry) gets correlation around 0.78 with EEG-derived bandwidth on our validation set. EEG improves it to 0.91 but is not required for most use cases."),
            ("What about privacy?",
             "Privacy-first by default. On-device processing where possible; optional cloud sync for cohort analytics. Operator owns their data. Supervisor visibility is per-operator opt-in. We never sell or share."),
            ("Can it actually predict tilt 30 min ahead?",
             "Tilt prediction at 30 min has lower precision than current-state detection — about 0.62 AUC on our esports validation set vs 0.89 for current-state. Useful as a yellow-flag signal, not a diagnosis. We surface the confidence with every prediction."),
            ("Will this make my surgeon/pilot/athlete second-guess themselves?",
             "Tested explicitly with operators in pilot deployments. The opposite happens — knowing there is a backstop reduces the cognitive load of self-monitoring, which actually frees bandwidth. Operators report performing better with Edge than without it."),
            ("How much does the calibration period actually matter?",
             "A lot. Population averages produce false-positive alerts in 25-30% of operators. Personal baselines drop false positives below 5% after 1 week. We will not deploy without a calibration period."),
        ],
        final_cta="Don't wait for the error to know the operator was depleted.",
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
        problem="Your eval set has 1,000 questions. Your RAG pipeline answers ~65% correctly. The other 35% are not even close — the retrieval step missed the relevant document entirely. You add a reranker. The 65% becomes 68%. You add query rewriting. 70%. Then you plateau. Every fix improves precision; nothing fixes recall. The answer was always two graph hops away.",
        solution="Replace top-k with spreading activation. Same vector DB, same embeddings, same query. Vectora walks the document graph from the query's nearest neighbors outward, surfacing second-hop results that share no surface tokens with the query but answer the underlying question. Layer keyword and knowledge-graph edges on the same node set for hybrid retrieval. Three-line code change.",
        how_it_works=[
            ("Wraps your vector DB", "Vectora reads from Pinecone, Weaviate, Qdrant, or pgvector. No migration, no re-embedding, no separate index to maintain. Your existing storage layer stays."),
            ("Builds the graph layer", "On top of the vector DB, Vectora maintains a sparse graph of document-to-document edges. Edges come from embedding similarity, keyword overlap, knowledge-graph extraction, and co-citation. Built incrementally as queries arrive."),
            ("Spreads activation per query", "When a query arrives, Vectora seeds activation at the embedding-nearest documents and walks outward through the graph with decay. Returns documents weighted by total received activation, not just first-hop similarity."),
            ("Modulates by context", "Recent user activity becomes a state modulator. Same query in different contexts returns different results. The Context-Aware canvas in Vectora demonstrates this primitive directly."),
        ],
        capabilities=[
            ("Spreading-activation retrieval", "Replace top-k with a graph walk that follows weighted edges from the query through the document graph. Second-hop results that share no surface tokens with the query but answer the underlying question surface automatically."),
            ("Hybrid edges", "Same node set, multiple edge types: embedding similarity (broad), keyword exact-match (precise), knowledge-graph relations (typed), co-occurrence (statistical). Activation flows through whichever edges are strong."),
            ("Context-aware modulation", "Recent user activity becomes a state modulator. Same query returns different results when the user is in different contexts. Eliminates the &quot;rephrase to add context&quot; tax users currently pay."),
            ("Anomaly surfacing", "Residual scoring on incoming items. New documents that diverge from the existing pattern get flagged automatically — useful for change detection, research, alerting."),
            ("Drop-in API", "REST + Python/JS SDK. Wraps your existing vector DB. Three-line code change to swap top-k for Vectora retrieval. Backwards compatible: top-k mode preserved as a config flag."),
            ("Per-query tunability", "One parameter (decay) tunes how far the graph walk explores. Tight decay = high precision, top-k-like behavior. Loose decay = high recall, full graph reach. Per-query overrides for precision-sensitive vs recall-sensitive use cases."),
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
        secondary_demo_title="Code samples",
        secondary_demo_html="""
<div style="font-size:11px;color:#6a808a;margin-bottom:10px">Three lines to swap top-k for Vectora. Same return shape (list of documents with scores), no other changes to your pipeline.</div>
<div style="display:flex;gap:8px;margin-bottom:10px;flex-wrap:wrap">
  <button onclick="showCode('python')" id="code-py" class="code-btn" style="padding:5px 12px;border-radius:4px;border:1px solid #38bdf8;background:#38bdf8;color:#0a121a;font-size:10px;cursor:pointer;font-family:inherit">Python</button>
  <button onclick="showCode('js')" id="code-js" class="code-btn" style="padding:5px 12px;border-radius:4px;border:1px solid #1f3040;background:transparent;color:#dce6ed;font-size:10px;cursor:pointer;font-family:inherit">TypeScript</button>
  <button onclick="showCode('curl')" id="code-curl" class="code-btn" style="padding:5px 12px;border-radius:4px;border:1px solid #1f3040;background:transparent;color:#dce6ed;font-size:10px;cursor:pointer;font-family:inherit">curl</button>
</div>
<pre id="code-block" style="background:#0a121a;border:1px solid #1f3040;border-radius:4px;padding:14px;font-family:'SF Mono',monospace;font-size:11px;color:#dce6ed;overflow-x:auto;line-height:1.6;margin:0"></pre>
        """,
        secondary_demo_script="""
const CODE_SAMPLES = {
  python: 'from vectora import Client\\n\\nclient = Client(api_key=\"vec_...\", backend=\"pinecone\", index=\"my-docs\")\\n\\n# was: results = pinecone_index.query(vector=embedding, top_k=10)\\nresults = client.retrieve(query=\"caching strategies for a monolith\", k=10)\\n\\nfor r in results:\\n    print(r.text, r.score, r.hop_distance)',
  js: 'import { Vectora } from \"@vectora/client\";\\n\\nconst client = new Vectora({ apiKey: \"vec_...\", backend: \"pinecone\", index: \"my-docs\" });\\n\\n// was: const results = await index.query({ vector: embedding, topK: 10 });\\nconst results = await client.retrieve({ query: \"caching strategies for a monolith\", k: 10 });\\n\\nresults.forEach(r => console.log(r.text, r.score, r.hopDistance));',
  curl: 'curl -X POST https://api.vectora.dev/v1/retrieve \\\\\\n  -H \"Authorization: Bearer vec_...\" \\\\\\n  -H \"Content-Type: application/json\" \\\\\\n  -d \\'{\\n    \"query\": \"caching strategies for a monolith\",\\n    \"k\": 10,\\n    \"backend\": \"pinecone\",\\n    \"index\": \"my-docs\",\\n    \"decay\": 0.4\\n  }\\'',
};
function showCode(lang) {
  document.getElementById('code-block').textContent = CODE_SAMPLES[lang];
  ['py','js','curl'].forEach(l => {
    const btn = document.getElementById('code-' + l);
    if (l === lang || (l === 'py' && lang === 'python')) {
      btn.style.background = '#38bdf8'; btn.style.color = '#0a121a'; btn.style.borderColor = '#38bdf8';
    } else {
      btn.style.background = 'transparent'; btn.style.color = '#dce6ed'; btn.style.borderColor = '#1f3040';
    }
  });
}
showCode('python');
        """,
        use_cases=[
            ("AI engineer at a customer-support startup",
             "RAG over 50K support docs. Eval recall plateaus at 64%. Users keep asking questions that surface the wrong articles. Reranker bolted on; hits 68% and stops. Engineering time spent rephrasing prompts.",
             "Vectora swap. Eval recall jumps to 84% with no other changes. The 20% gap was almost entirely second-hop documents (architecture overviews that explained the system the user was asking about, not the specific feature)."),
            ("Internal-search lead at a 5,000-person company",
             "Confluence + Slack + Google Drive search returns top-k matches that are usually wrong because employees do not write queries the way docs are titled. Search satisfaction polls poorly.",
             "Vectora layered on top of the existing vector index. Context-aware retrieval adds the user's recent activity (which team's Slack channels they are in, which docs they viewed yesterday). Same query returns different, much-more-relevant results per employee."),
            ("Lead at a legal-tech vendor",
             "Contract retrieval needs both keyword precision (specific clause language) and semantic recall (similar contractual situations). Currently runs two separate queries and merges manually. Brittle.",
             "Vectora's hybrid edges merge keyword + semantic + knowledge-graph (entity extraction on contract parties) in one query. Single API call. Better recall on similar-situation matching, no loss of keyword-precision."),
            ("Researcher building a paper-recommendation system",
             "Top-k embedding similarity returns papers cited by the same crowd. Misses the cross-disciplinary papers that would be most valuable. Cannot tune the index because 'cross-discipline' is not a feature in the embeddings.",
             "Vectora's graph walk follows co-citation and embedding edges. Surfaces papers that are 2-3 hops away — exactly the cross-disciplinary recommendations the researcher was missing. Replaces a manual literature review step."),
        ],
        competitors=[
            ("Top-k (Pinecone, Weaviate, Qdrant, pgvector raw)",
             "Same backend storage. Adds the graph layer that surfaces second-hop results top-k cannot. Drop-in replacement.",
             "Fast nearest-neighbor lookup. Misses second-hop. Recall plateaus where the actual best document is not the closest in embedding space."),
            ("Reranker (Cohere Rerank, Cross-encoders)",
             "Pre-LLM expansion that increases candidate set quality. Use Vectora to find the right candidates, then rerank for precision if needed.",
             "Improves precision on a fixed candidate set. Cannot fix recall — if the right document was not in the top-k, no reranker will find it."),
            ("LlamaIndex / LangChain retrievers",
             "Compatible adapter — Vectora plugs into either as a retriever. Adds the graph-walk primitive that the standard composable retrievers lack.",
             "Composable RAG framework. Top-k is the default retriever; multi-hop requires custom code. Vectora is the multi-hop component without custom code."),
            ("Knowledge-graph databases (Neo4j, AWS Neptune)",
             "Embedding edges + KG edges on the same graph. Best of both. No need to sync structure across two systems.",
             "Excellent at typed-relation traversal. Weak at semantic similarity over text. Requires manual KG construction."),
        ],
        integration_steps=[
            ("Install the SDK", "pip install vectora or npm install @vectora/client. Configure with your existing vector DB credentials (Pinecone, Weaviate, Qdrant, pgvector — all supported)."),
            ("Index your existing data (no re-embed)", "Vectora reads from your vector DB; the graph layer is built incrementally as queries come in. No re-embedding required, no migration."),
            ("Swap retrieval call", "Replace your top-k call with vectora.retrieve(). Returns the same shape (list of documents with scores) but with second-hop expansion included. Three-line change."),
            ("Tune decay", "One parameter (graph-walk decay) tunes how far Vectora explores. Default works for most cases; tighten for precision-sensitive use cases, loosen for recall-sensitive."),
            ("(Optional) Enable hybrid edges", "Configure additional edge types: keyword, knowledge-graph, co-citation, custom. All edges merged at query time, weighted per query if needed."),
        ],
        pricing_tiers=[
            ("Hobby", "$0 / mo", "Self-hosted, up to 100K documents, 10K queries/mo. Open source."),
            ("Cloud", "$99 / mo", "Hosted, up to 1M documents, 1M queries/mo, automatic graph maintenance."),
            ("Scale", "Custom", "Unlimited documents and queries, dedicated infrastructure, SLA, on-prem option."),
        ],
        faq=[
            ("Does Vectora replace my vector DB?",
             "No. Vectora reads from your existing Pinecone, Weaviate, Qdrant, or pgvector. The graph layer sits on top. You keep your storage, embeddings, and existing infrastructure. Vectora adds the spreading-activation retrieval primitive without forcing a migration."),
            ("How does latency compare to top-k?",
             "Adds 5-15ms for a typical 10-document graph walk on a 1M-document index. Sub-linear in document count. Tunable via the decay parameter — tight decay is essentially top-k speed; loose decay explores further at the cost of latency."),
            ("Will my retrieved document set get bigger?",
             "By default, you ask for k results and get k results — same as top-k. The k results are different (better) because they include second-hop matches. If you want the expanded set, pass include_expansion=true."),
            ("How are graph edges built?",
             "Embedding-similarity edges are computed from your existing embeddings (no recomputation). Keyword edges from sparse-vector indexing. Knowledge-graph edges from optional NER + relation extraction. All built incrementally as queries arrive — no batch indexing job."),
            ("Can I bring my own edges?",
             "Yes. The API supports custom edge ingestion: post (source_doc_id, target_doc_id, edge_type, weight) tuples and Vectora uses them in the graph walk. Useful for explicit user-curated relations or domain-specific structure."),
            ("Does it work with my custom embedder?",
             "Yes. Vectora is embedder-agnostic; it operates on the vectors already in your index. Whether they came from OpenAI ada-002, Voyage, Cohere, or a fine-tuned in-house model is irrelevant."),
        ],
        final_cta="Stop reranking what you should have retrieved.",
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
        problem="The market shows you a price chart and a news headline. You have to decide: is this a real signal or noise? You read 200 articles and watch 30 charts and most are noise. Active traders without an institutional research desk are reading the same surface signals everyone else has and making decisions on vibes. You cannot tell when the news is hype, when the volume is normal, when the move is statistically meaningful.",
        solution="Strata scans the universe continuously, scores each move on a 0-100 unusual-score formula (price percentile + relative volume + volatility-adjusted + persistence), classifies the move into one of 16 named archetypes, scores any associated news on five Claude-graded dimensions (quality, sentiment, credibility, materiality, hype), and shows you which paper-trading strategies would have entered. You are no longer guessing about what is happening — you are reading the structural signal.",
        how_it_works=[
            ("Continuously scan the universe", "Watched ticker set is scored every market minute. Composite unusual-score combines price-change percentile (35%), relative-volume percentile (25%), volatility-adjusted z-score (25%), and move persistence (15%). Above 70 is &quot;unusual,&quot; above 85 is &quot;extreme.&quot;"),
            ("Classify the move", "Rule-based classifier projects the unusual-score state-vector into one of 16 archetypes (breakout, breakdown, momentum, mean reversion, short squeeze, low float, sector sympathy, pump risk, post-earnings drift, capitulation, gap up/down, exhaustion top/bottom, volume climax). Plain-English explanation per classification."),
            ("Score the news", "For unusual stocks (score ≥ 60), Claude Haiku analyzes the news. Quality, sentiment (-100 to +100), credibility, materiality, hype — five-dimensional score plus a one-line analyst summary. Cost-controlled to avoid scoring every micro-blip."),
            ("Recommend strategies", "Strata's 294-strategy library is matched against the current signal. Strategies whose entry conditions match the move are surfaced; user picks which to follow as paper trades. Performance tracked on the leaderboard."),
        ],
        capabilities=[
            ("Unusual Move Scanner", "Continuously scans the watched universe for statistically unusual price/volume moves. Composite score (price percentile 35% + volume 25% + volatility-adjusted 25% + persistence 15%) with Normal / Notable / Unusual / Extreme labels."),
            ("Pattern Classifier", "Classifies each unusual move into one of 16 archetypes — breakout, breakdown, momentum, mean reversion, short squeeze, low float speculation, sector sympathy, pump risk, post-earnings drift, capitulation, gap up/down, exhaustion top/bottom, volume climax."),
            ("News Catalyst Scorer", "Claude-scored multi-dimensional analysis of news headlines tied to flagged stocks. Quality, sentiment, credibility, materiality, hype scores plus a one-line analyst summary. Cost-controlled: only scores stocks with unusualScore ≥ 60."),
            ("294-strategy paper-trading library", "Paper-trade against 294 strategies spanning every major sector and direction. Live leaderboard with annualized return, Sharpe, max drawdown, win rate, trade count. Personalized portfolio recommendations based on recent strategy performance."),
            ("Sector heatmap + watchlist", "Real-time sector rotation visualization. Personal watchlist with custom alerts on price levels, signal triggers, and unusual moves. Daily &quot;Stock of the Day&quot; pick from the highest-conviction signals."),
            ("Backtest engine", "Run any strategy against any time window with full transaction-cost modeling. Equity curves, monthly returns, max drawdown, rolling Sharpe. Compare strategies head-to-head on the same period."),
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
        secondary_demo_title="Today's leaderboard",
        secondary_demo_html="""
<div style="font-size:11px;color:#7a708a;margin-bottom:10px">A snapshot of the strategy leaderboard. Updates every market session. Click any strategy in the live app to see its trade history, equity curve, and current open positions.</div>
<table style="width:100%;border-collapse:collapse;font-size:11px;background:#0c0a14;border:1px solid #2a2236;border-radius:4px;overflow:hidden">
  <thead><tr style="background:#181423">
    <th style="padding:10px;text-align:left;color:#7a708a">#</th>
    <th style="padding:10px;text-align:left;color:#7a708a">Strategy</th>
    <th style="padding:10px;text-align:right;color:#7a708a">YTD Return</th>
    <th style="padding:10px;text-align:right;color:#7a708a">Sharpe</th>
    <th style="padding:10px;text-align:right;color:#7a708a">Max DD</th>
    <th style="padding:10px;text-align:right;color:#7a708a">Win %</th>
  </tr></thead>
  <tbody>
    <tr style="border-top:1px solid #2a2236"><td style="padding:8px 10px;color:#a3e635;font-weight:bold">1</td><td style="padding:8px 10px;color:#e8dce8">Tech News Alpha</td><td style="padding:8px 10px;text-align:right;color:#a3e635">+34.2%</td><td style="padding:8px 10px;text-align:right;color:#e8dce8">2.81</td><td style="padding:8px 10px;text-align:right;color:#7a708a">−6.4%</td><td style="padding:8px 10px;text-align:right;color:#e8dce8">68%</td></tr>
    <tr style="border-top:1px solid #2a2236"><td style="padding:8px 10px;color:#a3e635;font-weight:bold">2</td><td style="padding:8px 10px;color:#e8dce8">Healthcare Catalyst</td><td style="padding:8px 10px;text-align:right;color:#a3e635">+28.6%</td><td style="padding:8px 10px;text-align:right;color:#e8dce8">2.42</td><td style="padding:8px 10px;text-align:right;color:#7a708a">−9.1%</td><td style="padding:8px 10px;text-align:right;color:#e8dce8">61%</td></tr>
    <tr style="border-top:1px solid #2a2236"><td style="padding:8px 10px;color:#a3e635;font-weight:bold">3</td><td style="padding:8px 10px;color:#e8dce8">Energy Mean Reversion</td><td style="padding:8px 10px;text-align:right;color:#a3e635">+22.4%</td><td style="padding:8px 10px;text-align:right;color:#e8dce8">2.18</td><td style="padding:8px 10px;text-align:right;color:#7a708a">−11.2%</td><td style="padding:8px 10px;text-align:right;color:#e8dce8">59%</td></tr>
    <tr style="border-top:1px solid #2a2236"><td style="padding:8px 10px;color:#fbbf24;font-weight:bold">4</td><td style="padding:8px 10px;color:#e8dce8">Sector Rotation Alpha</td><td style="padding:8px 10px;text-align:right;color:#a3e635">+18.9%</td><td style="padding:8px 10px;text-align:right;color:#e8dce8">1.94</td><td style="padding:8px 10px;text-align:right;color:#7a708a">−13.5%</td><td style="padding:8px 10px;text-align:right;color:#e8dce8">54%</td></tr>
    <tr style="border-top:1px solid #2a2236"><td style="padding:8px 10px;color:#fbbf24;font-weight:bold">5</td><td style="padding:8px 10px;color:#e8dce8">Hype Fader</td><td style="padding:8px 10px;text-align:right;color:#a3e635">+16.1%</td><td style="padding:8px 10px;text-align:right;color:#e8dce8">1.76</td><td style="padding:8px 10px;text-align:right;color:#7a708a">−14.9%</td><td style="padding:8px 10px;text-align:right;color:#e8dce8">52%</td></tr>
    <tr style="border-top:1px solid #2a2236"><td style="padding:8px 10px;color:#7a708a">…</td><td style="padding:8px 10px;color:#7a708a">… 289 more strategies</td><td style="padding:8px 10px;text-align:right;color:#7a708a"></td><td style="padding:8px 10px;text-align:right;color:#7a708a"></td><td style="padding:8px 10px;text-align:right;color:#7a708a"></td><td style="padding:8px 10px;text-align:right;color:#7a708a"></td></tr>
  </tbody>
</table>
        """,
        secondary_demo_script="",
        use_cases=[
            ("Active retail trader managing personal capital",
             "Trades 3-5 names per week. Reads CNBC, screams about Fed, picks setups based on chart vibes. Wins some, loses more. Has no tool for distinguishing structural signal from noise.",
             "Strata flags genuinely unusual moves. The signal cards explain why. Pump-risk flags catch the SMCI-style traps before he enters. The strategy library shows him which historical strategies have worked under similar setups. He stops chasing pump-and-dumps."),
            ("Sell-side equity research analyst",
             "Covers a sector. Needs to spot unusual moves in covered names quickly to write client notes. Currently uses Bloomberg + half a dozen scrapers + a manual watch list.",
             "Strata's sector heatmap surfaces unusual moves across the analyst's coverage in real time. Daily &quot;Stock of the Day&quot; from the analyst's universe is a starting prompt for client notes. AI news scoring drafts the &quot;why&quot; section automatically."),
            ("Quant research lead at a small fund",
             "Wants to test new signal hypotheses. Existing infra is built for production strategies; iterating on new ideas is heavy. Backtest engine is in Excel-wrapped Python with 4-hour run time.",
             "Strata's backtest engine and 294-strategy library are the prototype harness. Test a new factor against the existing strategies in seconds. If it adds Sharpe, port to production infra. If not, kill the idea cheaply."),
            ("Finance student / aspiring quant",
             "Wants to learn. Books are static; production tools are expensive and opaque. No good way to see what real strategies look like and how they perform under different conditions.",
             "Free tier of Strata gives access to the strategy library, the scanner, and the backtester. Learn by inspection &mdash; what factor weights produce what outcomes, which strategies blow up in which regimes, why pump-risk flags exist."),
        ],
        competitors=[
            ("Bloomberg Terminal",
             "Free tier exists. Modern UI. AI news scoring is automatic. 294 strategies you can paper-trade rather than just read about.",
             "Industry standard at $24K/year. Comprehensive but designed for institutional users. Steep learning curve. No native paper-trading."),
            ("TradingView",
             "Stronger structural analysis (unusual-score, classifier, news scoring). Strategy library with paper-trading rather than just charts.",
             "Excellent charting, decent screener, no AI news scoring, no strategy library. Used as a chart, not a research platform."),
            ("Robinhood / Webull / brokers",
             "Research-only, not a broker. Honest framing about being simulation, not financial advice. No conflict of interest about trade volume.",
             "Trading platforms, not research tools. Surface signals are minimal. Designed to drive trade volume, not to make you better-informed."),
            ("Substack analyst newsletters",
             "Real-time signals, not weekly write-ups. Active analysis instead of passive consumption. You apply the analyst&apos;s framework yourself rather than waiting for their take.",
             "Quality varies wildly. Latency between event and write-up is hours to days. Editorial bias inevitable. Excellent for context, weak for active research."),
        ],
        integration_steps=[
            ("Sign in", "Free trial with Google or GitHub OAuth. No credit card required for the basic tier."),
            ("Connect a watchlist", "Import from a CSV or paste tickers. Strata seeds with the S&P 500 + popular small caps by default."),
            ("Configure alerts", "Set thresholds for unusual scores, signal types, sector moves. Email or webhook notifications."),
            ("Paper-trade", "Pick strategies from the 294-strategy library to follow. Strata simulates trades against live data; equity curves and stats update daily."),
            ("(Optional) Custom strategies", "On the Trader tier, define your own factor weights and rules. Strata backtests your strategy against historical data and joins it to the leaderboard alongside the built-ins."),
        ],
        pricing_tiers=[
            ("Free", "$0 / mo", "Top-100 stocks, daily refresh, 5 strategies, no AI news scoring. For exploration."),
            ("Pro", "$29 / mo", "Full universe, real-time scanning, all 294 strategies, AI news scoring, unlimited watchlists."),
            ("Trader", "$99 / mo", "Custom strategies, backtest engine access, API export, priority support. For active research users."),
        ],
        faq=[
            ("Is this financial advice?",
             "No. Strata is a research and simulation platform. We surface structural signals; you make all trading decisions. Disclosure on every page. Built deliberately to inform, not to recommend."),
            ("Does Strata execute real trades?",
             "No. All trades are paper-trades simulated against live market data. We do not connect to brokers, do not handle real capital, do not have a Series 7 anywhere in the company. By design."),
            ("How does the unusual-score formula work?",
             "Composite of four components: price-change percentile vs the stock&apos;s historical rolling moves of the same length (35%), relative volume vs average over period (25%), volatility-adjusted z-score of the change (25%), and move persistence (15%). Each component normalized to 0-100, weighted, summed. Above 70 is unusual; above 85 is extreme."),
            ("Why limit AI news scoring to stocks with unusual-score ≥ 60?",
             "Cost control. Scoring every news article for every stock would burn $1000s/month in Claude API spend. The threshold ensures we only score news for stocks where the signal warrants it. Adjustable on the Trader tier."),
            ("Where does the strategy library come from?",
             "Built in-house at <code>~/projects/charlie_project/prisma/seed.ts</code>. 294 strategies covering long, short, contrarian, gap-trading, mean-reversion, sector-rotation, and more across every major equity sector. Each has factor weights, filters, position-sizing rules, and stop-loss configuration."),
            ("Will you support crypto / FX / futures?",
             "Yes — those are Strata's other proposed verticals (Strata Crypto, Strata FX, Strata Commodities, Strata Predict, Strata Bonds). The engine is asset-class-agnostic; only the data sources and archetype definitions differ. Equities is shipping first to validate the playbook."),
        ],
        final_cta="Read the structural signal. Stop trading the surface.",
        status_badge="SHIPPING · FIRST VERTICAL",
    )
