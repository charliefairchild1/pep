"""Lemma AI grading — Anthropic vision-based grading of math warmup photos.

Gated behind subscription tier (`can_use_ai_grading`). Logs every call to
`usage_log` for margin tracking. Defaults to Haiku 4.5 for cost; flip via
`LEMMA_GRADE_MODEL` env var.

Env vars:
  LEMMA_ANTHROPIC_API_KEY  Anthropic API key. Required for AI grading to work.
                            Without it, the endpoint returns 503.
  LEMMA_GRADE_MODEL        haiku (default) | sonnet | opus

Prompt caching: the system prompt is identical across every grading call,
so we mark it with `cache_control: {"type": "ephemeral"}` to get ~90%
discount on cached input tokens after the first call.
"""
from __future__ import annotations

import base64
import json
import os
from typing import Any

import anthropic
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse

from pep.routes.lemma_accounts import get_current_teacher, _BASE_STYLE, _navbar, _seo_head, _LOGOUT_SCRIPT
from pep.routes.lemma_billing import can_use_ai_grading, log_usage
from pep.routes.lemma_backend import _conn, _now


router = APIRouter()


# ---------------------------------------------------------------------------
# Model selection
# ---------------------------------------------------------------------------

_MODEL_ALIASES = {
    "haiku": "claude-haiku-4-5",
    "sonnet": "claude-sonnet-4-6",
    "opus": "claude-opus-4-7",
}


def _resolve_model(env_var: str, default: str = "haiku") -> tuple[str, str]:
    """Returns (model_id, short_alias). Short alias is used for usage logging."""
    raw = (os.environ.get(env_var) or default).strip().lower()
    if raw in _MODEL_ALIASES:
        return _MODEL_ALIASES[raw], raw
    # If a raw model ID was set, log it under the alias that matches
    if raw.startswith("claude-haiku"):
        return raw, "haiku"
    if raw.startswith("claude-sonnet"):
        return raw, "sonnet"
    if raw.startswith("claude-opus"):
        return raw, "opus"
    return _MODEL_ALIASES[default], default


def _grade_model() -> tuple[str, str]:
    return _resolve_model("LEMMA_GRADE_MODEL", "haiku")


def _anthropic_client() -> anthropic.Anthropic:
    key = (os.environ.get("LEMMA_ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY") or "").strip()
    if not key:
        raise HTTPException(503, "AI grading is not configured on this server. Tell the admin to set LEMMA_ANTHROPIC_API_KEY.")
    return anthropic.Anthropic(api_key=key)


# ---------------------------------------------------------------------------
# Grading prompt — designed for caching
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """You are an experienced math teacher grading a student's daily warmup. The student wrote their answers on paper; you are looking at a photo of that paper.

You will be given:
- The list of problems the student was asked to solve, with the correct answer for each
- A photo of the student's work

For each problem, decide whether the student's final answer matches the correct answer (or is mathematically equivalent — e.g. 0.5 and 1/2 are the same, "2x+1" and "1+2x" are the same).

Be generous with formatting (the student is on paper, in a hurry). Be strict about correctness — if the answer is wrong or unclear, mark it wrong.

If a problem is left blank, unreadable, or skipped, mark it wrong and note that in `feedback`.

Return a JSON object with the exact structure shown in the user message. Each problem's feedback should be one short sentence the teacher can show to the student."""


def _grade_response_schema(num_problems: int) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "results": {
                "type": "array",
                "minItems": num_problems,
                "maxItems": num_problems,
                "items": {
                    "type": "object",
                    "properties": {
                        "problem_number": {"type": "integer"},
                        "is_correct": {"type": "boolean"},
                        "student_answer_shown": {"type": "string", "description": "What the student wrote (best transcription); empty string if blank/unreadable."},
                        "feedback": {"type": "string", "description": "One short sentence."},
                    },
                    "required": ["problem_number", "is_correct", "student_answer_shown", "feedback"],
                    "additionalProperties": False,
                },
            },
            "overall_notes": {"type": "string", "description": "One sentence the teacher might say to the student about the warmup as a whole."},
        },
        "required": ["results", "overall_notes"],
        "additionalProperties": False,
    }


def _grade_with_claude(
    image_base64: str,
    image_media_type: str,
    problems: list[dict[str, str]],
    topic: str,
) -> dict[str, Any]:
    """Calls Claude vision to grade one student's warmup. Returns parsed JSON.

    `problems` is a list like:
        [{"number": 1, "prompt": "Find dy/dx for y = sin(x)", "correct_answer": "cos(x)"}, ...]
    """
    client = _anthropic_client()
    model_id, _ = _grade_model()
    problems_block = "\n".join(
        f"Problem {p['number']}: {p['prompt']}\nCorrect answer: {p['correct_answer']}"
        for p in problems
    )
    user_text = (
        f"Topic: {topic or '(unspecified)'}\n\n"
        f"PROBLEMS:\n{problems_block}\n\n"
        "Look at the photo and grade each problem. Return JSON with this shape:\n"
        "{\n"
        '  "results": [{"problem_number": int, "is_correct": bool, "student_answer_shown": str, "feedback": str}, ...],\n'
        '  "overall_notes": str\n'
        "}"
    )
    response = client.messages.create(
        model=model_id,
        max_tokens=4096,
        system=[{
            "type": "text",
            "text": _SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": image_media_type, "data": image_base64},
                },
                {"type": "text", "text": user_text},
            ],
        }],
        output_config={
            "format": {
                "type": "json_schema",
                "schema": _grade_response_schema(len(problems)),
            },
        },
    )
    text = next((b.text for b in response.content if b.type == "text"), "")
    if not text:
        raise HTTPException(500, "AI grading returned no content.")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        raise HTTPException(500, "AI grading returned invalid JSON.")
    # Attach usage so caller can log it
    parsed["_usage"] = {
        "input_tokens": getattr(response.usage, "input_tokens", 0),
        "output_tokens": getattr(response.usage, "output_tokens", 0),
        "cache_creation_input_tokens": getattr(response.usage, "cache_creation_input_tokens", 0),
        "cache_read_input_tokens": getattr(response.usage, "cache_read_input_tokens", 0),
    }
    return parsed


# ---------------------------------------------------------------------------
# API endpoint
# ---------------------------------------------------------------------------

@router.post("/lemma/api/grade")
async def grade_warmup(req: Request) -> JSONResponse:
    me = get_current_teacher(req)
    if not me:
        raise HTTPException(401, "not signed in")
    body = await req.json()
    class_code = (body.get("class_code") or "").strip().upper()
    student_name = (body.get("student_name") or "").strip()
    topic = (body.get("topic") or "").strip()[:80]
    image_b64 = body.get("image_base64") or ""
    image_media_type = (body.get("image_media_type") or "image/jpeg").strip()
    problems = body.get("problems") or []
    warmup_date = body.get("warmup_date") or _now()[:10]
    if not class_code or not student_name or not image_b64 or not problems:
        raise HTTPException(400, "class_code, student_name, image_base64, and problems are required")
    if not isinstance(problems, list) or len(problems) < 1 or len(problems) > 20:
        raise HTTPException(400, "problems must be a list with 1–20 entries")
    if image_media_type not in ("image/jpeg", "image/png", "image/webp", "image/gif"):
        raise HTTPException(400, f"unsupported image media type: {image_media_type}")
    # Verify the teacher owns this class
    with _conn() as c:
        cls = c.execute("SELECT teacher_id FROM classes WHERE code = ?", (class_code,)).fetchone()
        if not cls:
            raise HTTPException(404, "class not found")
        if cls["teacher_id"] and cls["teacher_id"] != me["id"]:
            raise HTTPException(403, "that class belongs to a different teacher account")
    # Gate on plan
    ok, reason = can_use_ai_grading(me["id"])
    if not ok:
        raise HTTPException(402, reason or "AI grading not available on your plan.")

    # Call Claude
    try:
        parsed = _grade_with_claude(image_b64, image_media_type, problems, topic)
    except HTTPException:
        raise
    except anthropic.APIStatusError as e:
        raise HTTPException(e.status_code or 500, f"AI grading service error: {str(e)[:200]}")
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"AI grading failed: {str(e)[:200]}")

    # Log usage
    _, model_alias = _grade_model()
    log_usage(me["id"], operation="grade", model=model_alias, count=1, class_code=class_code)

    # Roll up score + record submission
    results = parsed.get("results", [])
    correct = sum(1 for r in results if r.get("is_correct"))
    total = len(results)
    details = {
        "ai_results": results,
        "overall_notes": parsed.get("overall_notes", ""),
        "model": model_alias,
        "usage": parsed.get("_usage"),
    }
    with _conn() as c:
        c.execute(
            "INSERT INTO submissions (class_code, student_name, warmup_date, topic, correct, total, details, submitted_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (class_code, student_name, warmup_date, topic, correct, total, json.dumps(details), _now()),
        )

    # Optional auto-push to Canvas
    try:
        from pep.routes.lemma_canvas import maybe_auto_push_grade
        await maybe_auto_push_grade(class_code, student_name)
    except Exception:  # noqa: BLE001
        pass

    return JSONResponse({
        "ok": True,
        "score": correct,
        "total": total,
        "accuracy_percent": round(100 * correct / total) if total else 0,
        "results": results,
        "overall_notes": parsed.get("overall_notes", ""),
        "model_used": model_alias,
    })


# ---------------------------------------------------------------------------
# Test page — teacher uploads a photo + a few problems to sanity-check AI
# ---------------------------------------------------------------------------

@router.get("/lemma/grade-test", response_class=HTMLResponse)
async def grade_test_page(req: Request) -> HTMLResponse:
    me = get_current_teacher(req)
    if not me:
        return HTMLResponse('<meta http-equiv="refresh" content="0; url=/lemma/login">')
    nav = _navbar(True, me["display_name"])
    head = _seo_head(
        req,
        title="AI grading test · Lemma",
        description="Test the AI grading by uploading a photo of a math warmup.",
        path="/lemma/grade-test",
    )
    page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
{head}
<meta name="robots" content="noindex">
<style>{_BASE_STYLE}
.dropzone{{border:2px dashed #cbd5e1;border-radius:10px;padding:30px;text-align:center;color:#64748b;cursor:pointer;background:#f8fafc}}
.dropzone:hover{{border-color:#0ea5e9;color:#0284c7}}
.dropzone img{{max-width:100%;max-height:300px;display:block;margin:0 auto}}
textarea{{width:100%;padding:9px 12px;border:1px solid #cbd5e1;border-radius:7px;font:inherit;font-size:13.5px;font-family:ui-monospace,'SF Mono',monospace;background:#fff}}
.result{{background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:14px 16px;margin-top:14px}}
.result h4{{font-size:14.5px;font-weight:600;margin-bottom:6px;color:#0f172a}}
.problem-row{{padding:9px 11px;border-bottom:1px solid #f1f5f9}}
.problem-row:last-child{{border-bottom:none}}
.problem-row .mark{{display:inline-block;width:22px;height:22px;border-radius:50%;text-align:center;line-height:22px;font-weight:700;font-size:13px;margin-right:8px}}
.problem-row .mark.ok{{background:#dcfce7;color:#15803d}}
.problem-row .mark.no{{background:#fee2e2;color:#b91c1c}}
</style></head><body>
<div class="wrap">
{nav}
<h1>AI grading test</h1>
<p class="lead">Upload a photo and a few problems. We'll grade it with the AI right now.</p>

<div class="card">
  <h2>1. Pick a class</h2>
  <div class="field">
    <label>Your class</label>
    <select id="classCode" style="width:100%;padding:9px 12px;border:1px solid #cbd5e1;border-radius:7px;font:inherit;font-size:14px;background:#fff"><option>loading…</option></select>
  </div>
  <div class="field">
    <label>Student name</label>
    <input id="studentName" type="text" placeholder="e.g. Mr. K (you), or a real student name">
  </div>
  <div class="field">
    <label>Topic (optional)</label>
    <input id="topic" type="text" placeholder="e.g. Derivatives — chain rule">
  </div>
</div>

<div class="card">
  <h2>2. Define the problems + correct answers</h2>
  <p class="muted" style="font-size:13px;margin-bottom:8px">One per line. Format: <code>problem | correct answer</code></p>
  <textarea id="problemsText" rows="6" placeholder="d/dx of sin(x) | cos(x)
2 + 2 | 4
solve x^2 = 9 | x = ±3"></textarea>
</div>

<div class="card">
  <h2>3. Photo of student work</h2>
  <input id="fileInput" type="file" accept="image/jpeg,image/png,image/webp" style="display:none">
  <div class="dropzone" id="dropzone" onclick="document.getElementById('fileInput').click()">
    <div id="dropzoneText">📷 Click to choose a photo (or drop here)</div>
    <img id="preview" style="display:none">
  </div>
</div>

<div style="display:flex;gap:10px;align-items:center;margin-top:14px">
  <button class="btn" id="gradeBtn">Grade this →</button>
  <span class="muted" id="status"></span>
</div>

<div id="results"></div>

</div>
<script>
{_LOGOUT_SCRIPT}
let imageBase64 = null, imageMedia = null;

async function loadClasses(){{
  const r = await fetch('/lemma/api/account/me');
  const d = await r.json();
  const sel = document.getElementById('classCode');
  if(!d.classes || !d.classes.length){{
    sel.innerHTML = '<option value="">(no classes yet — create one first)</option>';
    return;
  }}
  sel.innerHTML = d.classes.map(c => `<option value="${{c.code}}">${{c.class_name}} (${{c.code}})</option>`).join('');
}}
loadClasses();

document.getElementById('fileInput').addEventListener('change', e=>{{
  const f = e.target.files && e.target.files[0]; if(!f) return;
  imageMedia = f.type;
  const reader = new FileReader();
  reader.onload = ()=> {{
    const dataUrl = reader.result;
    imageBase64 = dataUrl.split(',')[1];
    document.getElementById('preview').src = dataUrl;
    document.getElementById('preview').style.display = 'block';
    document.getElementById('dropzoneText').style.display = 'none';
  }};
  reader.readAsDataURL(f);
}});

const dz = document.getElementById('dropzone');
['dragenter','dragover'].forEach(e => dz.addEventListener(e, ev=>{{ev.preventDefault(); dz.style.background='#e0f2fe';}}));
['dragleave','drop'].forEach(e => dz.addEventListener(e, ev=>{{ev.preventDefault(); dz.style.background='#f8fafc';}}));
dz.addEventListener('drop', ev=>{{
  const f = ev.dataTransfer.files && ev.dataTransfer.files[0];
  if(f){{ document.getElementById('fileInput').files = ev.dataTransfer.files; document.getElementById('fileInput').dispatchEvent(new Event('change')); }}
}});

document.getElementById('gradeBtn').addEventListener('click', async ()=>{{
  const code = document.getElementById('classCode').value;
  const name = document.getElementById('studentName').value.trim();
  const topic = document.getElementById('topic').value.trim();
  const probsRaw = document.getElementById('problemsText').value;
  if(!code || !name || !imageBase64 || !probsRaw.trim()){{
    alert('Need class, student name, problems, and a photo.');
    return;
  }}
  const problems = probsRaw.split(/\\n/).map(s=>s.trim()).filter(Boolean).map((line, i)=>{{
    const parts = line.split('|').map(p=>p.trim());
    return {{number: i+1, prompt: parts[0] || '', correct_answer: (parts[1] || '').trim()}};
  }});
  const status = document.getElementById('status');
  status.textContent = 'Grading…';
  document.getElementById('gradeBtn').disabled = true;
  try {{
    const r = await fetch('/lemma/api/grade', {{
      method:'POST', headers:{{'Content-Type':'application/json'}},
      body: JSON.stringify({{class_code: code, student_name: name, topic, image_base64: imageBase64, image_media_type: imageMedia, problems}}),
    }});
    const d = await r.json();
    if(!r.ok){{ status.textContent = ''; alert(d.detail || 'Grading failed.'); return; }}
    status.textContent = `Graded with ${{d.model_used}}: ${{d.score}}/${{d.total}} (${{d.accuracy_percent}}%)`;
    const out = document.getElementById('results');
    let h = `<div class="result"><h4>${{d.score}}/${{d.total}} · ${{d.accuracy_percent}}%</h4>`;
    h += '<p class="muted" style="font-style:italic">' + escapeHTML(d.overall_notes || '') + '</p>';
    for(const r of d.results){{
      h += `<div class="problem-row"><span class="mark ${{r.is_correct?'ok':'no'}}">${{r.is_correct?'✓':'✗'}}</span>
        <b>Problem ${{r.problem_number}}</b> · student wrote: <code>${{escapeHTML(r.student_answer_shown || '(blank)')}}</code><br>
        <span class="muted" style="font-size:12.5px;margin-left:30px">${{escapeHTML(r.feedback)}}</span></div>`;
    }}
    h += '</div>';
    out.innerHTML = h;
  }} catch(err){{
    status.textContent = '';
    alert('Network error: ' + err.message);
  }} finally {{
    document.getElementById('gradeBtn').disabled = false;
  }}
}});

function escapeHTML(s){{ return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }}
</script>
</body></html>"""
    return HTMLResponse(page)
