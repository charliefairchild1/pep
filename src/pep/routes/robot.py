"""/robot — the buildable blueprint for an embodied PEP mind.

Renders the ROBOT_BLUEPRINT.md document into a clean, dark, printable HTML
page with a sticky tier-switcher for the parts list. The canonical source is
ROBOT_BLUEPRINT.md at the repo root.
"""
import os

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, PlainTextResponse

router = APIRouter()
_DIST = os.path.join(os.path.dirname(__file__), "..", "..", "..", "dist")
_BLUEPRINT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ROBOT_BLUEPRINT.md")


def _read_blueprint() -> str:
    try:
        with open(_BLUEPRINT, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return "# Blueprint missing\n\nROBOT_BLUEPRINT.md not found."


@router.get("/robot.md", response_class=PlainTextResponse)
async def robot_md() -> PlainTextResponse:
    return PlainTextResponse(_read_blueprint(), media_type="text/markdown; charset=utf-8")


@router.get("/robot/model", response_class=HTMLResponse)
async def robot_model() -> HTMLResponse:
    path = os.path.join(_DIST, "robot_model.html")
    try:
        return HTMLResponse(open(path, encoding="utf-8").read())
    except OSError:
        return HTMLResponse("<h1>Robot Model</h1><p>robot_model.html not found in dist/.</p>")


@router.get("/robot", response_class=HTMLResponse)
async def robot() -> HTMLResponse:
    md = _read_blueprint()
    # client-side markdown render via marked.js; keeps the route trivial and the
    # source single-sourced.
    page = f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>A Robot With A Self And A Seeming — blueprint</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#06080d;color:#d7dde7;font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;line-height:1.62;font-size:15px}}
.wrap{{max-width:880px;margin:0 auto;padding:24px 18px 80px}}
.top{{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;border-bottom:1px solid #18202d;padding-bottom:10px;margin-bottom:18px}}
.top h1{{font-size:22px;font-weight:650}}
.top h1 .s{{color:#5c6675;font-weight:400;font-size:14px;margin-left:6px}}
.nav a{{color:#7b8696;text-decoration:none;font-size:13px;margin-right:13px}}
.nav a:hover{{color:#5bb6c8}}
.actions{{margin-left:auto;display:flex;gap:8px}}
.actions a{{font-size:12px;color:#94a0b0;background:#0a0e15;border:1px solid #1a2230;border-radius:6px;padding:5px 9px;text-decoration:none}}
.actions a:hover{{border-color:#3f718a;color:#8fd4e6}}

article{{font-size:14.5px}}
article h1{{font-size:26px;font-weight:680;margin:14px 0 14px;color:#e8eef6;letter-spacing:-.005em}}
article h2{{font-size:18.5px;font-weight:650;margin:30px 0 10px;color:#cfd6e0;border-bottom:1px solid #18202d;padding-bottom:5px}}
article h3{{font-size:15.5px;font-weight:650;margin:22px 0 8px;color:#bcc6d4;font-family:ui-monospace,monospace;letter-spacing:.01em}}
article p{{margin:9px 0 11px;color:#cfd6e0}}
article strong{{color:#e6ecf2;font-weight:650}}
article em{{color:#caa15a;font-style:italic}}
article ul,article ol{{margin:9px 0 13px 22px;color:#cfd6e0}}
article ul li,article ol li{{margin:5px 0}}
article a{{color:#5bb6c8;text-decoration:none;border-bottom:1px dotted #2f5d6e}}
article a:hover{{color:#7fd0e2}}
article code{{background:#0a0e15;border:1px solid #18202d;border-radius:3px;padding:1px 5px;font-size:12.5px;color:#caa15a;font-family:ui-monospace,monospace}}
article pre{{background:#04060a;border:1px solid #141c28;border-radius:8px;padding:14px 16px;overflow-x:auto;margin:12px 0;font-size:12px;line-height:1.55}}
article pre code{{background:transparent;border:none;padding:0;color:#aac4ce;font-size:12px}}
article blockquote{{border-left:3px solid #5bb6c8;padding:6px 14px;margin:12px 0;background:#0a0e15;border-radius:0 6px 6px 0;color:#94a0b0}}

article table{{width:100%;border-collapse:collapse;margin:12px 0;font-size:13.5px;background:#0a0e15;border:1px solid #141c28;border-radius:8px;overflow:hidden}}
article th{{background:#0e1622;color:#5bb6c8;text-align:left;padding:9px 12px;font-weight:600;font-size:12.5px;letter-spacing:.04em;border-bottom:1px solid #18202d}}
article td{{padding:8px 12px;border-bottom:1px solid #10161f;color:#cfd6e0;vertical-align:top}}
article tr:last-child td{{border-bottom:none}}
article td:nth-child(3){{font-family:ui-monospace,monospace;color:#caa15a;white-space:nowrap}}
article hr{{border:none;border-top:1px solid #18202d;margin:24px 0}}

@media print {{
  body{{background:#fff;color:#222}}
  article p,article li{{color:#333}}
  article strong{{color:#000}}
  .nav,.actions,.printhide{{display:none}}
  article pre{{background:#f5f5f5;border-color:#ccc}}
  article pre code{{color:#222}}
  article code{{background:#f5f5f5;border-color:#ccc;color:#9a6100}}
  article table{{background:#fff;border-color:#ccc}}
  article th{{background:#eee;color:#000;border-color:#ccc}}
  article td{{color:#222;border-color:#eee}}
  article td:nth-child(3){{color:#7a4d00}}
  article h2{{border-color:#ddd}}
  article blockquote{{background:#f8f8f8;color:#444}}
}}
</style></head>
<body><div class="wrap">

<div class="top">
  <h1>A Robot With A Self And A Seeming <span class="s">— buildable blueprint</span></h1>
  <div class="nav"><a href="/everything">← everything</a><a href="/robot/model">3D model</a><a href="/axona/mind">try the mind</a><a href="/axona/origin">origin</a><a href="/axona/seeming">seeming</a><a href="/pep">pep</a></div>
  <div class="actions printhide">
    <a href="/robot.md" download="ROBOT_BLUEPRINT.md">↓ .md</a>
    <a href="javascript:window.print()">⎙ print</a>
  </div>
</div>

<article id="doc"></article>

</div>

<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script>
const SRC = {md!r};
document.getElementById('doc').innerHTML = marked.parse(SRC, {{breaks:false, gfm:true}});
</script>
</body></html>"""
    return HTMLResponse(page)
