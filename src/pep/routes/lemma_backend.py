"""Lemma classroom backend.

Minimal SQLite-backed multi-teacher, multi-class implementation.
Each teacher creates classes; each class has a 6-char join code; students
join via the code and their progress + bulk-grading submissions are
recorded against (class_code, student_name).

Routes:
  GET  /lemma/start                    — teacher: pick course + class name, create
  GET  /lemma/teacher/{code}           — teacher dashboard (own class)
  GET  /lemma/c/{code}                  — student class page (join screen → math app)
  POST /lemma/api/class/create
  GET  /lemma/api/class/{code}/info
  POST /lemma/api/class/{code}/roster   — add a student
  GET  /lemma/api/class/{code}/roster
  POST /lemma/api/class/{code}/submit   — record a bulk-graded warmup result
  GET  /lemma/api/class/{code}/results  — teacher view of all submissions

The student-facing UI continues to use the existing standalone math app
(at /lemma/math); the class context is injected via a small script that
runs when ?class=CODE&student=NAME is on the URL.
"""

from __future__ import annotations

import json
import os
import random
import secrets
import sqlite3
import string
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse


router = APIRouter()

# ---------------------------------------------------------------------------
# DB setup
# ---------------------------------------------------------------------------

_DB_PATH = Path(__file__).resolve().parent.parent.parent.parent / "data" / "lemma.db"
_DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(_DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def _init_db() -> None:
    with _conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS classes (
            code         TEXT PRIMARY KEY,
            teacher_name TEXT NOT NULL,
            class_name   TEXT NOT NULL,
            course_id    TEXT NOT NULL,
            created_at   TEXT NOT NULL,
            teacher_id   INTEGER,
            announcement TEXT
        );
        CREATE TABLE IF NOT EXISTS students (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            class_code   TEXT NOT NULL,
            name         TEXT NOT NULL,
            joined_at    TEXT NOT NULL,
            UNIQUE(class_code, name)
        );
        CREATE TABLE IF NOT EXISTS submissions (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            class_code   TEXT NOT NULL,
            student_name TEXT NOT NULL,
            warmup_date  TEXT NOT NULL,
            topic        TEXT,
            correct      INTEGER NOT NULL,
            total        INTEGER NOT NULL,
            details      TEXT,
            submitted_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS submissions_class_idx ON submissions(class_code);
        CREATE INDEX IF NOT EXISTS submissions_student_idx ON submissions(class_code, student_name);
        """)
        # Migrations for databases created before a column existed. Each guarded
        # so re-running is a no-op. (The canonical CREATE above already has them
        # for fresh DBs; these cover upgrades-in-place.)
        cols = {r[1] for r in c.execute("PRAGMA table_info(classes)").fetchall()}
        if "teacher_id" not in cols:
            c.execute("ALTER TABLE classes ADD COLUMN teacher_id INTEGER")
        if "announcement" not in cols:
            c.execute("ALTER TABLE classes ADD COLUMN announcement TEXT")


_init_db()


def _new_code(n: int = 6) -> str:
    """Generate a join code that doesn't already exist. 6 chars, no ambiguous."""
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # no 0/O, 1/I
    with _conn() as c:
        for _ in range(50):
            code = "".join(secrets.choice(alphabet) for _ in range(n))
            existing = c.execute("SELECT 1 FROM classes WHERE code = ?", (code,)).fetchone()
            if not existing:
                return code
    raise RuntimeError("Could not allocate unique join code")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------

VALID_COURSES = {
    "pre-algebra", "algebra-1", "geometry", "algebra-2", "precalc",
    "calc-ab", "calc-bc", "stats", "multivar", "linear-alg",
    "diff-eq", "real-analysis", "topology",
}


@router.post("/lemma/api/class/create")
async def create_class(req: Request) -> JSONResponse:
    body = await req.json()
    teacher_name = (body.get("teacher_name") or "").strip()
    class_name = (body.get("class_name") or "").strip()
    course_id = (body.get("course_id") or "").strip()
    # If logged in, prefer the account's display name and link the class to the account.
    teacher_id: int | None = None
    try:
        from pep.routes.lemma_accounts import get_current_teacher  # local import to avoid cycle
        me = get_current_teacher(req)
        if me:
            teacher_id = me["id"]
            if not teacher_name:
                teacher_name = me["display_name"]
            # tier-limit check: free is 1 class, etc.
            try:
                from pep.routes.lemma_billing import can_create_class
                ok, reason = can_create_class(teacher_id)
                if not ok:
                    raise HTTPException(402, reason or "Upgrade required to create another class.")
            except HTTPException:
                raise
            except Exception:  # noqa: BLE001
                pass
    except HTTPException:
        raise
    except Exception:  # noqa: BLE001
        pass
    if not teacher_name or not class_name or not course_id:
        raise HTTPException(400, "teacher_name, class_name, and course_id are required")
    if course_id not in VALID_COURSES:
        raise HTTPException(400, f"unknown course_id: {course_id}")
    if len(teacher_name) > 60 or len(class_name) > 60:
        raise HTTPException(400, "names must be < 60 chars")
    code = _new_code()
    with _conn() as c:
        c.execute(
            "INSERT INTO classes (code, teacher_name, class_name, course_id, created_at, teacher_id) VALUES (?, ?, ?, ?, ?, ?)",
            (code, teacher_name, class_name, course_id, _now(), teacher_id),
        )
    return JSONResponse({"code": code, "class_name": class_name, "teacher_name": teacher_name, "course_id": course_id, "teacher_id": teacher_id})


@router.get("/lemma/api/class/{code}/info")
async def class_info(code: str) -> JSONResponse:
    code = code.upper()
    with _conn() as c:
        row = c.execute("SELECT * FROM classes WHERE code = ?", (code,)).fetchone()
        if not row:
            raise HTTPException(404, "class not found")
        roster_count = c.execute("SELECT COUNT(*) FROM students WHERE class_code = ?", (code,)).fetchone()[0]
        sub_count = c.execute("SELECT COUNT(*) FROM submissions WHERE class_code = ?", (code,)).fetchone()[0]
    keys = row.keys()
    return JSONResponse({
        "code": row["code"], "teacher_name": row["teacher_name"], "class_name": row["class_name"],
        "course_id": row["course_id"], "created_at": row["created_at"],
        "roster_count": roster_count, "submission_count": sub_count,
        "announcement": (row["announcement"] if "announcement" in keys else None) or "",
    })


@router.post("/lemma/api/class/{code}/announcement")
async def set_announcement(code: str, req: Request) -> JSONResponse:
    """Teacher sets a short note shown above students' warmups. Backend-backed
    so it actually reaches students on their own devices (the old localStorage-
    only version never crossed devices)."""
    code = code.upper()
    body = await req.json()
    text = (body.get("text") or "").strip()[:280]
    with _conn() as c:
        cls = c.execute("SELECT 1 FROM classes WHERE code = ?", (code,)).fetchone()
        if not cls:
            raise HTTPException(404, "class not found")
        c.execute("UPDATE classes SET announcement = ? WHERE code = ?", (text, code))
    return JSONResponse({"ok": True, "announcement": text})


@router.post("/lemma/api/class/{code}/roster")
async def add_student(code: str, req: Request) -> JSONResponse:
    code = code.upper()
    body = await req.json()
    name = (body.get("name") or "").strip()
    if not name:
        raise HTTPException(400, "name required")
    if len(name) > 60:
        raise HTTPException(400, "name too long")
    with _conn() as c:
        cls = c.execute("SELECT 1 FROM classes WHERE code = ?", (code,)).fetchone()
        if not cls:
            raise HTTPException(404, "class not found")
        try:
            c.execute(
                "INSERT INTO students (class_code, name, joined_at) VALUES (?, ?, ?)",
                (code, name, _now()),
            )
        except sqlite3.IntegrityError:
            pass  # already joined — that's fine
    return JSONResponse({"ok": True, "name": name})


@router.get("/lemma/api/class/{code}/roster")
async def get_roster(code: str) -> JSONResponse:
    code = code.upper()
    with _conn() as c:
        rows = c.execute("SELECT name, joined_at FROM students WHERE class_code = ? ORDER BY joined_at", (code,)).fetchall()
    return JSONResponse({"students": [{"name": r["name"], "joined_at": r["joined_at"]} for r in rows]})


@router.post("/lemma/api/class/{code}/submit")
async def submit_warmup(code: str, req: Request) -> JSONResponse:
    code = code.upper()
    body = await req.json()
    student_name = (body.get("student_name") or "").strip()
    correct = int(body.get("correct") or 0)
    total = int(body.get("total") or 0)
    topic = (body.get("topic") or "").strip()[:60]
    details = body.get("details") or {}
    warmup_date = body.get("warmup_date") or _now()[:10]
    if not student_name or total <= 0:
        raise HTTPException(400, "student_name and total>0 required")
    with _conn() as c:
        cls = c.execute("SELECT 1 FROM classes WHERE code = ?", (code,)).fetchone()
        if not cls:
            raise HTTPException(404, "class not found")
        c.execute(
            "INSERT INTO submissions (class_code, student_name, warmup_date, topic, correct, total, details, submitted_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (code, student_name, warmup_date, topic, correct, total, json.dumps(details), _now()),
        )
    # auto-push the cumulative grade to Canvas if this class is linked
    canvas_result = None
    try:
        from pep.routes.lemma_canvas import maybe_auto_push_grade
        canvas_result = await maybe_auto_push_grade(code, student_name)
    except Exception:  # noqa: BLE001 — never let a Canvas error break submit
        canvas_result = {"ok": False, "error": "auto_push_exception"}
    return JSONResponse({"ok": True, "canvas": canvas_result})


@router.get("/lemma/api/class/{code}/results")
async def get_results(code: str) -> JSONResponse:
    code = code.upper()
    with _conn() as c:
        rows = c.execute(
            "SELECT student_name, warmup_date, topic, correct, total, submitted_at FROM submissions WHERE class_code = ? ORDER BY submitted_at DESC LIMIT 500",
            (code,),
        ).fetchall()
    submissions = [dict(r) for r in rows]
    # Roll up per-student aggregates
    per_student: dict[str, dict[str, Any]] = {}
    for s in submissions:
        n = s["student_name"]
        if n not in per_student:
            per_student[n] = {"name": n, "warmups": 0, "correct": 0, "total": 0}
        per_student[n]["warmups"] += 1
        per_student[n]["correct"] += s["correct"]
        per_student[n]["total"] += s["total"]
    for s in per_student.values():
        s["accuracy"] = round(100 * s["correct"] / s["total"]) if s["total"] else 0
    aggregates = sorted(per_student.values(), key=lambda x: -x["warmups"])
    return JSONResponse({"submissions": submissions, "aggregates": aggregates})


# ---------------------------------------------------------------------------
# Pages: /lemma/start (teacher create), /lemma/teacher/{code} (dashboard),
# /lemma/c/{code} (student class entry)
# ---------------------------------------------------------------------------

_COURSE_NAMES = {
    "pre-algebra": "Pre-Algebra", "algebra-1": "Algebra 1", "geometry": "Geometry",
    "algebra-2": "Algebra 2", "precalc": "Precalculus",
    "calc-ab": "AP Calculus AB", "calc-bc": "AP Calculus BC", "stats": "AP Statistics",
    "multivar": "Multivariable Calculus", "linear-alg": "Linear Algebra",
    "diff-eq": "Differential Equations", "real-analysis": "Real Analysis", "topology": "Topology",
}


def _shared_css() -> str:
    return r"""
:root{--bg:#0a0d14;--surface:#14181f;--surface2:#0f1318;--text:#e2e6ed;--dim:#7a8092;--accent:#fbbf24;--accent2:#67e8f9;--green:#81c784;--pink:#f06292;--violet:#a78bfa;--border:#1e2430}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Inter,system-ui,sans-serif;background:var(--bg);color:var(--text);line-height:1.6;font-size:15px;min-height:100vh}
a{color:var(--accent2);text-decoration:none}
nav{background:var(--surface2);border-bottom:1px solid var(--border);padding:14px 28px;display:flex;gap:18px;align-items:center;font-size:12px;font-family:'SF Mono',monospace}
nav .brand{color:var(--accent);font-weight:700;font-size:15px}
nav .nav-links{margin-left:auto;display:flex;gap:14px;align-items:center}
.container{max-width:760px;margin:0 auto;padding:48px 24px 80px}
.panel{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:24px;margin-bottom:18px}
h1{font-size:32px;font-weight:800;letter-spacing:-0.01em;margin-bottom:8px}
h2{font-size:20px;font-weight:700;margin-bottom:10px}
h3{font-size:15px;font-weight:700;margin-bottom:8px}
.lede{color:var(--dim);font-size:15px;line-height:1.55;margin-bottom:18px}
.formrow{margin:14px 0}
.formrow label{display:block;font-size:11px;color:var(--dim);font-family:'SF Mono',monospace;letter-spacing:0.06em;text-transform:uppercase;margin-bottom:5px}
.formrow input,.formrow select{width:100%;background:var(--surface2);color:var(--text);border:1px solid var(--border);border-radius:6px;padding:10px 12px;font-size:15px;font-family:inherit}
.btn{display:inline-block;background:var(--accent);color:#0a0d14;border:1px solid var(--accent);border-radius:6px;padding:10px 22px;font-weight:700;font-size:14px;cursor:pointer;font-family:inherit}
.btn:hover{opacity:0.92}
.btn.ghost{background:transparent;color:var(--text);border-color:var(--border)}
.btn.ghost:hover{border-color:var(--accent2);color:var(--accent2)}
.code-display{font-family:'SF Mono',monospace;font-size:48px;font-weight:800;color:var(--accent);letter-spacing:0.15em;text-align:center;padding:18px;background:var(--surface2);border-radius:8px;margin:14px 0}
.share-box{background:var(--surface2);border:1px solid var(--accent2);border-radius:6px;padding:14px 18px;margin:10px 0;display:flex;justify-content:space-between;align-items:center;gap:10px;font-family:'SF Mono',monospace;font-size:13px}
.share-box .url{color:var(--accent2);word-break:break-all;flex:1}
.share-box button{background:var(--accent2);color:#0a0d14;border:none;padding:6px 12px;border-radius:4px;cursor:pointer;font-family:inherit;font-weight:700;font-size:11.5px}
.stat-grid{display:grid;grid-template-columns:repeat(4, 1fr);gap:10px;margin-top:14px}
.stat-card{background:var(--surface2);border:1px solid var(--border);border-radius:6px;padding:12px;text-align:center}
.stat-card .num{font-size:22px;font-weight:800;color:var(--accent);font-family:'SF Mono',monospace}
.stat-card .lbl{font-size:11px;color:var(--dim);font-family:'SF Mono',monospace;text-transform:uppercase;letter-spacing:0.04em;margin-top:4px}
@media (max-width:600px){.stat-grid{grid-template-columns:repeat(2, 1fr)}}
table{width:100%;border-collapse:collapse;font-size:13.5px;margin-top:10px}
th,td{padding:8px 12px;border-bottom:1px solid var(--border);text-align:left}
th{font-family:'SF Mono',monospace;font-size:11px;color:var(--dim);letter-spacing:0.04em;text-transform:uppercase}
.toast{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:var(--surface);border:1px solid var(--accent2);color:var(--text);padding:10px 18px;border-radius:6px;font-family:'SF Mono',monospace;font-size:12.5px;z-index:9999}
"""


_START_PAGE = r"""<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lemma · Start a Class</title>
<style>__CSS__</style></head><body>

<nav>
  <a href="/lemma/teachers" style="color:var(--dim)">← Lemma</a>
  <span class="brand">/lemma</span>
  <span style="color:var(--accent2);font-weight:600">/start</span>
  <span class="nav-links">
    <a href="/lemma/teachers">For educators</a>
  </span>
</nav>

<div class="container">

<h1>Start a class</h1>
<p class="lede">Create a class in 30 seconds. You get a 6-character join code; students enter it on their device and they're in. Their bulk-graded warmups feed your dashboard. All math department teachers can create their own — fully separate, fully private to each class.</p>

<div class="panel" style="border-left:3px solid #0ea5e9;background:linear-gradient(135deg,#0a1929 0%,#0d1f33 100%)">
  <h2 style="color:#7dd3fc;margin-bottom:6px">🔗 Use Canvas? Connect Lemma to it.</h2>
  <p class="lede" style="margin-bottom:12px;color:#94a3b8">Students click a link in Canvas and land in their Lemma class. Warmup grades push back to Canvas automatically. Takes about a minute to set up — just need your Canvas access token.</p>
  <a class="btn" href="/lemma/canvas/setup" style="background:#0ea5e9;color:#fff">Connect Lemma to Canvas →</a>
  <span style="margin-left:14px;color:#64748b;font-size:13px">or create a class below and link it later from the dashboard</span>
</div>

<div class="panel">
  <form onsubmit="event.preventDefault(); createClass();">
    <div class="formrow">
      <label>Your name</label>
      <input type="text" id="teacher" placeholder="e.g. Mr. K" required maxlength="60">
    </div>
    <div class="formrow">
      <label>Class name (period, section, etc.)</label>
      <input type="text" id="class-name" placeholder="e.g. Period 3 AP Calc BC" required maxlength="60">
    </div>
    <div class="formrow">
      <label>Course</label>
      <select id="course-id" required>
        <optgroup label="Foundation">
          <option value="pre-algebra">Pre-Algebra</option>
          <option value="algebra-1">Algebra 1</option>
          <option value="geometry">Geometry</option>
          <option value="algebra-2">Algebra 2</option>
          <option value="precalc">Precalculus</option>
        </optgroup>
        <optgroup label="AP">
          <option value="calc-ab">AP Calculus AB</option>
          <option value="calc-bc" selected>AP Calculus BC</option>
          <option value="stats">AP Statistics</option>
        </optgroup>
        <optgroup label="Post-AP / college">
          <option value="multivar">Multivariable Calculus</option>
          <option value="linear-alg">Linear Algebra</option>
          <option value="diff-eq">Differential Equations</option>
          <option value="real-analysis">Real Analysis</option>
          <option value="topology">Topology</option>
        </optgroup>
      </select>
    </div>
    <button class="btn" type="submit">Create class</button>
  </form>
</div>

<div class="panel" id="result" style="display:none;border-left:3px solid var(--accent)">
  <h2>✓ Class created</h2>
  <div class="code-display" id="code-display"></div>
  <p class="lede" style="margin:8px 0 6px 0;font-weight:700;color:var(--text)">▶ This is the student part — send students HERE (or read them the code above):</p>
  <div class="share-box">
    <span class="url" id="student-url"></span>
    <button onclick="copyText(document.getElementById('student-url').textContent)">📋 copy</button>
  </div>
  <a class="btn" id="preview-student" href="#" target="_blank" style="margin-top:10px;background:var(--accent2,#5cc8ff);color:#0a0d14">👁 Preview what students see ↗</a>
  <p class="lede" style="margin:18px 0 8px 0">Bookmark your own dashboard (where grades land):</p>
  <div class="share-box">
    <span class="url" id="teacher-url"></span>
    <button onclick="copyText(document.getElementById('teacher-url').textContent)">📋 copy</button>
  </div>
  <a class="btn" id="open-dash" href="#" style="margin-top:14px">→ Open my dashboard</a>
</div>

<div class="panel">
  <h2>For the rest of the math department</h2>
  <p class="lede" style="margin-bottom:6px">Each teacher creates their own class from this page. They get their own join code; their dashboard is independent of yours. To share with colleagues:</p>
  <div class="share-box">
    <span class="url" id="start-url"></span>
    <button onclick="copyText(document.getElementById('start-url').textContent)">📋 copy</button>
  </div>
  <p class="lede" style="margin-top:14px;font-size:13.5px">Suggested email to a colleague: <i>"Try Lemma for daily warmups — go to <span id="inline-url"></span>, create your class, send the join code to your students. Each warmup is on paper; the AI grades the photos at end of period."</i></p>
</div>

<div class="toast" id="toast" style="display:none"></div>

<script>
const baseUrl = window.location.origin;
document.getElementById('start-url').textContent = baseUrl + '/lemma/start';
document.getElementById('inline-url').textContent = baseUrl + '/lemma/start';

async function createClass() {
  const teacher = document.getElementById('teacher').value.trim();
  const className = document.getElementById('class-name').value.trim();
  const courseId = document.getElementById('course-id').value;
  if (!teacher || !className || !courseId) return;
  const btn = document.querySelector('form .btn');
  const orig = btn ? btn.textContent : '';
  if (btn) { btn.disabled = true; btn.textContent = 'Creating your class…'; }
  // the free server can take ~30s to wake from sleep — tell the teacher so a
  // slow first response doesn't look broken.
  const slow = setTimeout(() => { if (btn) btn.textContent = 'Waking the server (~30s)…'; }, 2500);
  try {
    const r = await fetch('/lemma/api/class/create', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({teacher_name: teacher, class_name: className, course_id: courseId})
    });
    clearTimeout(slow);
    if (!r.ok) {
      let msg = 'Something went wrong creating the class.';
      try { msg = (await r.json()).detail || msg; } catch (e) {}
      if (r.status === 402) msg += "\n\nYou already have your class — open your dashboard from the link you saved, or sign in at /lemma/teachers to find it.";
      alert(msg);
      return;
    }
    const data = await r.json();
    document.getElementById('code-display').textContent = data.code;
    document.getElementById('student-url').textContent = baseUrl + '/lemma/c/' + data.code;
    document.getElementById('teacher-url').textContent = baseUrl + '/lemma/teacher/' + data.code;
    document.getElementById('open-dash').href = '/lemma/teacher/' + data.code;
    const prev = document.getElementById('preview-student');
    if (prev) prev.href = '/lemma/c/' + data.code;
    document.getElementById('result').style.display = '';
    document.getElementById('result').scrollIntoView({behavior: 'smooth'});
  } catch (e) {
    clearTimeout(slow);
    alert("Couldn't reach the server — it may still be waking up. Wait a few seconds and press Create again.");
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = orig; }
  }
}

function copyText(t) {
  navigator.clipboard.writeText(t).then(() => {
    const tt = document.getElementById('toast');
    tt.textContent = '📋 copied to clipboard';
    tt.style.display = '';
    setTimeout(() => tt.style.display = 'none', 2000);
  });
}
</script>
</body></html>
"""


_TEACHER_PAGE = r"""<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lemma · Teacher Dashboard</title>
<style>__CSS__
.refresh{font-size:11px;color:var(--dim);font-family:'SF Mono',monospace;margin-left:8px;cursor:pointer}
.refresh:hover{color:var(--accent2)}
</style></head><body>

<nav>
  <a href="/lemma/start" style="color:var(--dim)">← New class</a>
  <span class="brand">/lemma</span>
  <span style="color:var(--accent2);font-weight:600">/teacher/__CODE__</span>
  <span class="nav-links">
    <a href="/lemma/c/__CODE__" target="_blank">Student view ↗</a>
    <a href="/lemma/math" target="_blank">Open math app ↗</a>
  </span>
</nav>

<div class="container">

<h1 id="class-title">Loading...</h1>
<p class="lede" id="class-meta"></p>

<div class="panel">
  <h2>Join code</h2>
  <div class="code-display">__CODE__</div>
  <p class="lede" style="margin:8px 0">Share with students:</p>
  <div class="share-box">
    <span class="url" id="share-url"></span>
    <button onclick="copyText(document.getElementById('share-url').textContent)">📋 copy</button>
  </div>
</div>

<div class="panel" id="canvas-panel">
  <h2>🔗 Canvas <span id="canvas-status-pill" style="font-size:12px;font-weight:500;color:var(--dim);font-family:'SF Mono',monospace;margin-left:8px"></span></h2>
  <div id="canvas-content">checking…</div>
</div>

<div class="panel">
  <h2>Class stats <span class="refresh" onclick="loadAll()">↻ refresh</span></h2>
  <div class="stat-grid">
    <div class="stat-card"><div class="num" id="s-roster">—</div><div class="lbl">students joined</div></div>
    <div class="stat-card"><div class="num" id="s-warmups">—</div><div class="lbl">warmups submitted</div></div>
    <div class="stat-card"><div class="num" id="s-accuracy">—</div><div class="lbl">class accuracy</div></div>
    <div class="stat-card"><div class="num" id="s-today">—</div><div class="lbl">submitted today</div></div>
  </div>
  <div id="trend-wrap" style="margin-top:18px"></div>
</div>

<div class="panel">
  <h2>👥 Roster</h2>
  <p class="lede" style="font-size:12.5px">Students who have joined this class. <b>Click any student</b> to see their full history, trend, and weak topics.</p>
  <table id="roster-table"><thead><tr><th>Student</th><th>Joined</th><th>Warmups</th><th>Accuracy</th></tr></thead><tbody id="roster-body"></tbody></table>
</div>

<div class="panel">
  <h2>📝 Recent submissions <button onclick="exportCSV()" style="float:right;font-size:12px;font-weight:600;font-family:inherit;cursor:pointer;background:var(--surface2);color:var(--text);border:1px solid var(--dim);border-radius:6px;padding:5px 11px">⬇ Export CSV</button></h2>
  <p class="lede" style="font-size:12.5px">Most recent 20 graded warmups across the class. Click a row to open that student. Export pulls the full gradebook.</p>
  <table id="subs-table"><thead><tr><th>Student</th><th>Topic</th><th>Score</th><th>When</th></tr></thead><tbody id="subs-body"></tbody></table>
</div>

<div class="panel">
  <h2>🚩 Needs attention</h2>
  <p class="lede" style="font-size:12.5px">Students below 55% class accuracy — worth a check-in.</p>
  <table id="attention-table"><thead><tr><th>Student</th><th>Warmups</th><th>Accuracy</th></tr></thead><tbody id="attention-body"></tbody></table>
</div>

<div class="panel">
  <h2>📊 Hardest topics</h2>
  <p class="lede" style="font-size:12.5px">Class accuracy by topic, weakest first — tells you what's worth reteaching.</p>
  <div id="topic-body"></div>
</div>

<div class="panel">
  <h2>How to run the warmup tomorrow</h2>
  <ol style="margin:10px 0 0 20px;color:var(--text);font-size:14px;line-height:1.85">
    <li>Students paper-write their warmup (the math app at <a href="/lemma/math" target="_blank">/lemma/math</a> generates per-student adaptive sets).</li>
    <li>Collect the papers at end of period.</li>
    <li>Open the <b>👨‍🏫 Teacher dashboard</b> tab in the math app and use <b>📷 bulk warmup grading</b> to upload the photos.</li>
    <li>Click "submit to leaderboard" — results appear on this page (refresh to see them).</li>
  </ol>
  <p class="lede" style="margin-top:12px;font-size:12.5px;font-style:italic">Note: bulk-grading is currently a simulator (random scoring biased toward correct). Real OCR via Claude API is the next build.</p>
</div>

<div class="toast" id="toast" style="display:none"></div>

<div id="student-modal" style="display:none;position:fixed;inset:0;background:rgba(15,23,42,.55);z-index:50;align-items:flex-start;justify-content:center;padding:40px 16px;overflow-y:auto" onclick="if(event.target===this)closeStudent()">
  <div style="background:var(--surface,#fff);max-width:560px;width:100%;border-radius:12px;padding:24px 26px;box-shadow:0 20px 60px rgba(0,0,0,.3)">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px">
      <h2 id="sm-name" style="margin:0">Student</h2>
      <button onclick="closeStudent()" style="background:none;border:none;font-size:26px;line-height:1;color:var(--dim);cursor:pointer">×</button>
    </div>
    <div id="sm-body"></div>
  </div>
</div>

<script>
const CODE = '__CODE__';
let LAST_RESULTS = {submissions:[], aggregates:[]};
document.getElementById('share-url').textContent = window.location.origin + '/lemma/c/' + CODE;

async function loadCanvasStatus() {
  try {
    const r = await fetch('/lemma/api/canvas/link/' + CODE);
    const d = await r.json();
    const pill = document.getElementById('canvas-status-pill');
    const content = document.getElementById('canvas-content');
    if (!d.linked) {
      pill.textContent = 'not connected';
      pill.style.color = '#94a3b8';
      content.innerHTML = `
        <p class="lede" style="font-size:13.5px;margin-bottom:10px">Connect this class to a Canvas course. Students click a link in Canvas and land here; warmup grades push back automatically.</p>
        <a class="btn" href="/lemma/canvas/setup">Connect to Canvas →</a>`;
      return;
    }
    pill.textContent = '✓ connected · ' + (d.canvas_course_name || ('course ' + d.canvas_course_id));
    pill.style.color = '#22c55e';
    const lastPush = d.last_push ? `last grade push: ${d.last_push.ok ? '✓' : '✗'} ${new Date(d.last_push.pushed_at).toLocaleString()}` : 'no grades pushed yet';
    const lemmaUrl = window.location.origin + '/lemma/c/' + CODE;
    content.innerHTML = `
      <div class="stat-grid" style="margin-bottom:14px">
        <div class="stat-card"><div class="num">${d.roster_mapped_count}</div><div class="lbl">canvas-mapped students</div></div>
        <div class="stat-card"><div class="num">${d.total_grades_pushed}</div><div class="lbl">grades pushed total</div></div>
        <div class="stat-card"><div class="num" style="font-size:14px;line-height:1.4">${d.auto_push ? 'on' : 'off'}</div><div class="lbl">auto-push on submit</div></div>
        <div class="stat-card"><div class="num" style="font-size:12.5px;line-height:1.4">${escapeHTML(d.canvas_user_name || '—')}</div><div class="lbl">connected as</div></div>
      </div>
      <p class="lede" style="font-size:12.5px;margin-bottom:8px">Add this URL to a Canvas module (External URL, "Load in new tab"):</p>
      <div class="share-box"><span class="url">${lemmaUrl}</span><button onclick="copyText('${lemmaUrl}')">📋 copy</button></div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:14px">
        <button class="btn" onclick="syncRoster()">↻ Sync roster from Canvas</button>
        <button class="btn" onclick="pushAllGrades()">↗ Push all grades now</button>
        <button class="btn" style="background:transparent;color:var(--dim);border:1px solid var(--dim)" onclick="toggleAutoPush(${d.auto_push?0:1})">${d.auto_push?'Disable':'Enable'} auto-push</button>
        <button class="btn" style="background:transparent;color:#b91c1c;border:1px solid #b91c1c" onclick="unlinkCanvas()">Unlink</button>
      </div>
      <p class="lede" style="font-size:11.5px;margin-top:10px;color:var(--dim)">${lastPush}</p>`;
  } catch (e) {
    document.getElementById('canvas-content').innerHTML = '<p style="color:#b91c1c">Could not check Canvas status: ' + escapeHTML(e.message) + '</p>';
  }
}

async function syncRoster(){
  const r = await fetch('/lemma/api/canvas/sync-roster/' + CODE, {method:'POST'});
  const d = await r.json();
  if(!r.ok){ alert('Sync failed: '+(d.detail||r.status)); return; }
  toast('roster synced: '+d.added+' added, '+d.mapped+' mapped');
  loadAll();
}
async function pushAllGrades(){
  const r = await fetch('/lemma/api/canvas/push-grades/' + CODE, {method:'POST'});
  const d = await r.json();
  if(!r.ok){ alert('Push failed: '+(d.detail||r.status)); return; }
  let msg = 'pushed '+d.pushed+' grade(s)';
  if(d.skipped && d.skipped.length) msg += '; skipped '+d.skipped.length+' (no canvas id)';
  toast(msg);
  loadCanvasStatus();
}
async function toggleAutoPush(v){
  await fetch('/lemma/api/canvas/auto-push/' + CODE, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({auto_push: !!v})});
  loadCanvasStatus();
}
async function unlinkCanvas(){
  if(!confirm('Unlink this class from Canvas? Grades pushed so far will stay in Canvas. The connection can be re-established any time.')) return;
  await fetch('/lemma/api/canvas/link/' + CODE, {method:'DELETE'});
  toast('unlinked');
  loadCanvasStatus();
}
function toast(t){ const tt=document.getElementById('toast'); tt.textContent=t; tt.style.display=''; setTimeout(()=>tt.style.display='none',2500); }
function escapeHTML(s){ return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

async function loadAll() {
  const info = await (await fetch('/lemma/api/class/' + CODE + '/info')).json();
  document.getElementById('class-title').textContent = info.class_name;
  document.getElementById('class-meta').textContent = info.teacher_name + ' · ' + __COURSE_NAMES__[info.course_id] + ' · created ' + new Date(info.created_at).toLocaleDateString();
  loadCanvasStatus();

  const rosterData = await (await fetch('/lemma/api/class/' + CODE + '/roster')).json();
  const resultsData = await (await fetch('/lemma/api/class/' + CODE + '/results')).json();
  LAST_RESULTS = resultsData;
  const aggBy = {};
  resultsData.aggregates.forEach(a => aggBy[a.name] = a);

  document.getElementById('s-roster').textContent = rosterData.students.length;
  document.getElementById('s-warmups').textContent = resultsData.submissions.length;
  const totalC = resultsData.aggregates.reduce((a, b) => a + b.correct, 0);
  const totalT = resultsData.aggregates.reduce((a, b) => a + b.total, 0);
  document.getElementById('s-accuracy').textContent = totalT > 0 ? Math.round(100 * totalC / totalT) + '%' : '—';
  const today = new Date().toISOString().slice(0, 10);
  document.getElementById('s-today').textContent = resultsData.submissions.filter(s => (s.submitted_at || '').slice(0, 10) === today).length;

  const rosterBody = document.getElementById('roster-body');
  if (rosterData.students.length === 0) {
    rosterBody.innerHTML = '<tr><td colspan="4" style="color:var(--dim);text-align:center;padding:18px">no students joined yet — share the link above</td></tr>';
  } else {
    rosterBody.innerHTML = rosterData.students.map(s => {
      const a = aggBy[s.name];
      return `<tr data-student="${escAttr(s.name)}" style="cursor:pointer" title="Open ${escAttr(s.name)}'s detail"><td><b>${s.name}</b></td><td style="color:var(--dim);font-family:'SF Mono',monospace;font-size:11.5px">${new Date(s.joined_at).toLocaleDateString()}</td><td>${a ? a.warmups : 0}</td><td>${a ? a.accuracy + '%' : '—'}</td></tr>`;
    }).join('');
  }

  const subsBody = document.getElementById('subs-body');
  if (resultsData.submissions.length === 0) {
    subsBody.innerHTML = '<tr><td colspan="4" style="color:var(--dim);text-align:center;padding:18px">no warmups submitted yet</td></tr>';
  } else {
    subsBody.innerHTML = resultsData.submissions.slice(0, 20).map(s => {
      const acc = Math.round(100 * s.correct / s.total);
      const color = acc >= 75 ? 'var(--green)' : acc >= 50 ? 'var(--accent)' : 'var(--pink)';
      return `<tr data-student="${escAttr(s.student_name)}" style="cursor:pointer"><td><b>${s.student_name}</b></td><td style="color:var(--dim);font-size:12.5px">${s.topic || '—'}</td><td style="color:${color};font-family:'SF Mono',monospace;font-weight:700">${s.correct}/${s.total} · ${acc}%</td><td style="color:var(--dim);font-family:'SF Mono',monospace;font-size:11.5px">${new Date(s.submitted_at).toLocaleString()}</td></tr>`;
    }).join('');
  }
  renderExtras(resultsData);
}

function renderExtras(resultsData) {
  // Needs attention — students below 55%
  const att = resultsData.aggregates.filter(a => a.total >= 4 && a.accuracy < 55).sort((a, b) => a.accuracy - b.accuracy);
  const ab = document.getElementById('attention-body');
  if (ab) ab.innerHTML = att.length
    ? att.map(a => `<tr data-student="${escAttr(a.name)}" style="cursor:pointer"><td><b>${a.name}</b></td><td>${a.warmups}</td><td style="color:var(--pink);font-family:'SF Mono',monospace;font-weight:700">${a.accuracy}%</td></tr>`).join('')
    : '<tr><td colspan="3" style="color:var(--green);text-align:center;padding:14px">No one below 55% — the class is keeping up. 🎉</td></tr>';
  // Hardest topics — accuracy by topic, weakest first
  const byTopic = {};
  resultsData.submissions.forEach(s => { const t = s.topic || '—'; (byTopic[t] = byTopic[t] || {c: 0, n: 0}); byTopic[t].c += s.correct; byTopic[t].n += s.total; });
  const topics = Object.entries(byTopic).map(([t, v]) => ({t, acc: v.n ? Math.round(100 * v.c / v.n) : 0})).sort((a, b) => a.acc - b.acc);
  const tb = document.getElementById('topic-body');
  if (tb) tb.innerHTML = topics.length
    ? topics.map(o => { const col = o.acc >= 75 ? 'var(--green)' : o.acc >= 55 ? 'var(--accent)' : 'var(--pink)'; return `<div style="display:flex;align-items:center;gap:10px;margin:6px 0"><div style="width:170px;font-size:13px;color:var(--text)">${o.t}</div><div style="flex:1;background:var(--surface2);border-radius:4px;overflow:hidden;height:14px"><div style="width:${o.acc}%;height:100%;background:${col}"></div></div><div style="width:42px;text-align:right;font-family:'SF Mono',monospace;font-size:12px;color:${col}">${o.acc}%</div></div>`; }).join('')
    : '<p class="lede" style="font-size:12.5px">No data yet.</p>';
  renderTrend(resultsData);
}

// ---- escaping + class accuracy-over-time sparkline ----
function escAttr(s){ return String(s||'').replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

function renderTrend(resultsData) {
  const wrap = document.getElementById('trend-wrap');
  if (!wrap) return;
  // class accuracy per warmup_date
  const byDate = {};
  resultsData.submissions.forEach(s => { const d = s.warmup_date || (s.submitted_at||'').slice(0,10); if(!d) return; (byDate[d]=byDate[d]||{c:0,n:0}); byDate[d].c+=s.correct; byDate[d].n+=s.total; });
  const days = Object.keys(byDate).sort();
  if (days.length < 2) { wrap.innerHTML=''; return; }
  const pts = days.map(d => ({d, acc: byDate[d].n ? Math.round(100*byDate[d].c/byDate[d].n) : 0}));
  const W=520, H=90, P=24;
  const x = i => P + i*(W-2*P)/(pts.length-1);
  const y = a => (H-P) - (a/100)*(H-2*P);
  const line = pts.map((p,i)=>`${i?'L':'M'}${x(i).toFixed(1)},${y(p.acc).toFixed(1)}`).join(' ');
  const dots = pts.map((p,i)=>`<circle cx="${x(i).toFixed(1)}" cy="${y(p.acc).toFixed(1)}" r="3" fill="var(--accent)"><title>${p.d}: ${p.acc}%</title></circle>`).join('');
  const first=pts[0].acc, last=pts[pts.length-1].acc, delta=last-first;
  const dcol = delta>=0?'var(--green)':'var(--pink)';
  wrap.innerHTML = `<div style="font-size:12.5px;color:var(--dim);margin-bottom:6px">📈 Class accuracy over time <span style="color:${dcol};font-weight:700">${delta>=0?'+':''}${delta} pts</span> since ${pts[0].d}</div>
    <svg viewBox="0 0 ${W} ${H}" style="width:100%;height:auto;overflow:visible">
      <line x1="${P}" y1="${y(50)}" x2="${W-P}" y2="${y(50)}" stroke="var(--surface2)" stroke-dasharray="3 3"/>
      <path d="${line}" fill="none" stroke="var(--accent)" stroke-width="2"/>
      ${dots}
      <text x="${P-4}" y="${y(100)+4}" text-anchor="end" font-size="9" fill="var(--dim)">100</text>
      <text x="${P-4}" y="${y(0)+4}" text-anchor="end" font-size="9" fill="var(--dim)">0</text>
    </svg>`;
}

// ---- per-student detail modal ----
function studentDetail(name) {
  const subs = LAST_RESULTS.submissions.filter(s => s.student_name === name)
    .sort((a,b)=> (a.warmup_date||a.submitted_at||'').localeCompare(b.warmup_date||b.submitted_at||''));
  const total = subs.reduce((a,s)=>a+s.total,0), correct = subs.reduce((a,s)=>a+s.correct,0);
  const acc = total ? Math.round(100*correct/total) : 0;
  // per-topic
  const byTopic = {};
  subs.forEach(s => { const t=s.topic||'—'; (byTopic[t]=byTopic[t]||{c:0,n:0}); byTopic[t].c+=s.correct; byTopic[t].n+=s.total; });
  const topics = Object.entries(byTopic).map(([t,v])=>({t,acc:v.n?Math.round(100*v.c/v.n):0,n:v.n})).sort((a,b)=>a.acc-b.acc);
  return {subs, total, correct, acc, topics};
}

function openStudent(name) {
  const d = studentDetail(name);
  document.getElementById('sm-name').textContent = name;
  const accCol = d.acc>=75?'var(--green)':d.acc>=55?'var(--accent)':'var(--pink)';
  const rows = d.subs.slice().reverse().slice(0,30).map(s => {
    const a = s.total?Math.round(100*s.correct/s.total):0;
    const col = a>=75?'var(--green)':a>=50?'var(--accent)':'var(--pink)';
    const when = s.warmup_date || (s.submitted_at||'').slice(0,10);
    return `<tr><td style="color:var(--dim);font-family:'SF Mono',monospace;font-size:11.5px">${when}</td><td style="font-size:12.5px">${s.topic||'—'}</td><td style="color:${col};font-family:'SF Mono',monospace;font-weight:700">${s.correct}/${s.total} · ${a}%</td></tr>`;
  }).join('') || '<tr><td colspan="3" style="color:var(--dim);text-align:center;padding:14px">no graded warmups yet</td></tr>';
  const topicRows = d.topics.map(o => { const col=o.acc>=75?'var(--green)':o.acc>=55?'var(--accent)':'var(--pink)'; return `<div style="display:flex;align-items:center;gap:8px;margin:5px 0"><div style="width:150px;font-size:12.5px;color:var(--text)">${o.t}</div><div style="flex:1;background:var(--surface2);border-radius:4px;overflow:hidden;height:12px"><div style="width:${o.acc}%;height:100%;background:${col}"></div></div><div style="width:36px;text-align:right;font-family:'SF Mono',monospace;font-size:11.5px;color:${col}">${o.acc}%</div></div>`; }).join('') || '<p class="lede" style="font-size:12px">No topic data yet.</p>';
  document.getElementById('sm-body').innerHTML = `
    <div class="stat-grid" style="margin:10px 0 16px">
      <div class="stat-card"><div class="num">${d.subs.length}</div><div class="lbl">warmups</div></div>
      <div class="stat-card"><div class="num" style="color:${accCol}">${d.acc}%</div><div class="lbl">accuracy</div></div>
      <div class="stat-card"><div class="num">${d.correct}/${d.total}</div><div class="lbl">problems</div></div>
    </div>
    <h3 style="margin:14px 0 4px;font-size:14px">Weakest topics</h3>
    ${topicRows}
    <h3 style="margin:16px 0 4px;font-size:14px">Warmup history</h3>
    <table style="width:100%"><thead><tr><th>Date</th><th>Topic</th><th>Score</th></tr></thead><tbody>${rows}</tbody></table>`;
  document.getElementById('student-modal').style.display = 'flex';
}
function closeStudent(){ document.getElementById('student-modal').style.display = 'none'; }
document.addEventListener('keydown', e => { if(e.key==='Escape') closeStudent(); });
document.addEventListener('click', e => { const tr = e.target.closest && e.target.closest('tr[data-student]'); if(tr) openStudent(tr.getAttribute('data-student')); });

// ---- CSV export of the full gradebook ----
function exportCSV() {
  const subs = LAST_RESULTS.submissions || [];
  if (!subs.length) { toast('No submissions to export yet.'); return; }
  const esc = v => { const s = String(v==null?'':v); return /[",\n]/.test(s) ? '"'+s.replace(/"/g,'""')+'"' : s; };
  const header = ['student','date','topic','correct','total','accuracy_pct','submitted_at'];
  const lines = [header.join(',')];
  subs.slice().sort((a,b)=> (a.student_name).localeCompare(b.student_name) || (a.warmup_date||'').localeCompare(b.warmup_date||'')).forEach(s => {
    const acc = s.total ? Math.round(100*s.correct/s.total) : 0;
    lines.push([s.student_name, s.warmup_date||(s.submitted_at||'').slice(0,10), s.topic||'', s.correct, s.total, acc, s.submitted_at||''].map(esc).join(','));
  });
  const blob = new Blob([lines.join('\n')], {type:'text/csv'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'lemma-' + CODE + '-gradebook.csv';
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(()=>URL.revokeObjectURL(url), 1000);
  toast('Exported ' + subs.length + ' rows to CSV');
}

function copyText(t) {
  navigator.clipboard.writeText(t).then(() => {
    const tt = document.getElementById('toast');
    tt.textContent = '📋 copied to clipboard';
    tt.style.display = '';
    setTimeout(() => tt.style.display = 'none', 2000);
  });
}

loadAll();
setInterval(loadAll, 15000);
</script>
</body></html>
"""


_STUDENT_PAGE = r"""<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lemma · Join Class</title>
<style>__CSS__</style></head><body>

<nav>
  <span class="brand">/lemma</span>
  <span style="color:var(--accent2);font-weight:600">/c/__CODE__</span>
  <span class="nav-links">
    <a href="/lemma">Lemma home</a>
  </span>
</nav>

<div class="container">

<div class="panel" id="join-panel">
  <h1 id="class-name">Loading...</h1>
  <p class="lede" id="class-meta"></p>

  <div id="known" style="display:none;background:var(--surface2);padding:14px 18px;border-radius:6px;margin:14px 0">
    <p style="font-size:14px;color:var(--text);margin:0">Welcome back, <b style="color:var(--accent)" id="known-name"></b>.</p>
    <div style="display:flex;gap:8px;margin-top:10px;flex-wrap:wrap">
      <button class="btn" onclick="enterAsKnown()">→ Open my warmup</button>
      <button class="btn ghost" onclick="forgetMe()">Not me — switch names</button>
    </div>
  </div>

  <div id="join-form">
    <p class="lede" style="margin-top:14px">Enter your name to join. Use the same name every day — your teacher will see your warmup history under this name.</p>
    <form onsubmit="event.preventDefault(); joinClass();">
      <div class="formrow">
        <label>Your name</label>
        <input type="text" id="name" placeholder="e.g. Alex Rivera" required maxlength="60" autofocus>
      </div>
      <button class="btn" type="submit">Join &amp; open warmup</button>
    </form>
  </div>
</div>

<div class="panel">
  <h3>How this works</h3>
  <p class="lede" style="font-size:13.5px;margin-bottom:0">Each day a 3-problem + 1-FRQ warmup is generated, individually adaptive to your weakest topic. You work it on paper. At the end of class, your teacher photographs the papers and the AI grades them. Your warmup history appears on your teacher's dashboard under the name you enter above.</p>
</div>

<div class="toast" id="toast" style="display:none"></div>

<script>
const CODE = '__CODE__';
const LS_KEY = 'lemma:class:' + CODE;

async function loadInfo() {
  const r = await fetch('/lemma/api/class/' + CODE + '/info');
  if (!r.ok) { document.body.innerHTML = '<div style="padding:48px;text-align:center;color:var(--pink);font-family:monospace">Class not found. Check the join link with your teacher.</div>'; return; }
  const info = await r.json();
  document.getElementById('class-name').textContent = info.class_name;
  document.getElementById('class-meta').textContent = info.teacher_name + ' · ' + __COURSE_NAMES__[info.course_id];
  // Has a saved identity for this class?
  const saved = localStorage.getItem(LS_KEY);
  if (saved) {
    const obj = JSON.parse(saved);
    document.getElementById('known-name').textContent = obj.name;
    document.getElementById('known').style.display = '';
    document.getElementById('join-form').style.display = 'none';
  }
}

async function joinClass() {
  const name = document.getElementById('name').value.trim();
  if (!name) return;
  const r = await fetch('/lemma/api/class/' + CODE + '/roster', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({name})
  });
  if (!r.ok) { alert('Failed: ' + (await r.text())); return; }
  localStorage.setItem(LS_KEY, JSON.stringify({name, joinedAt: Date.now()}));
  enterMath(name);
}

function enterAsKnown() {
  const saved = JSON.parse(localStorage.getItem(LS_KEY));
  enterMath(saved.name);
}

function forgetMe() {
  localStorage.removeItem(LS_KEY);
  location.reload();
}

function enterMath(name) {
  // Redirect into the math app with class context as query params
  window.location.href = '/lemma/math?class=' + CODE + '&student=' + encodeURIComponent(name);
}

loadInfo();
</script>
</body></html>
"""


def _course_names_js() -> str:
    return json.dumps(_COURSE_NAMES, ensure_ascii=False)


@router.get("/lemma/start", response_class=HTMLResponse)
async def lemma_start() -> HTMLResponse:
    page = _START_PAGE.replace("__CSS__", _shared_css())
    return HTMLResponse(page)


@router.get("/lemma/teacher/{code}", response_class=HTMLResponse)
async def lemma_teacher_dashboard(code: str) -> HTMLResponse:
    code = code.upper()
    # Verify class exists; render even if not so user gets a clean error
    with _conn() as c:
        row = c.execute("SELECT 1 FROM classes WHERE code = ?", (code,)).fetchone()
    if not row:
        return HTMLResponse(f"<body style='font-family:sans-serif;padding:40px;text-align:center'><h1>Class not found</h1><p>The code <code>{code}</code> doesn't match any class. <a href='/lemma/start'>Create a new class</a>.</p></body>", status_code=404)
    page = _TEACHER_PAGE.replace("__CSS__", _shared_css()).replace("__CODE__", code).replace("__COURSE_NAMES__", _course_names_js())
    return HTMLResponse(page)


@router.get("/lemma/join", response_class=HTMLResponse)
async def lemma_join_page() -> HTMLResponse:
    page = """<!doctype html><html><head>
<meta charset="utf-8"><title>Join your class — Lemma</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>__CSS__
body{display:flex;align-items:center;justify-content:center;min-height:100vh}
.join-card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:32px 28px;max-width:380px;width:100%;text-align:center}
.join-card h1{font-size:22px;margin:0 0 8px}
.join-card p{color:var(--muted);margin:0 0 22px;font-size:14px}
.join-card input{width:100%;padding:14px 16px;font-size:24px;text-align:center;letter-spacing:6px;text-transform:uppercase;background:var(--surface2);border:2px solid var(--border);border-radius:8px;color:var(--text);font-family:'SF Mono',monospace;font-weight:700;box-sizing:border-box}
.join-card input:focus{outline:none;border-color:var(--accent2)}
.join-card button{width:100%;margin-top:14px;padding:13px;background:var(--accent2);color:#0a0d14;border:none;border-radius:8px;font-weight:700;font-size:15px;cursor:pointer}
.join-card .err{color:#ff7676;font-size:13px;margin-top:10px;min-height:18px}
.join-card .foot{color:var(--muted);font-size:12px;margin-top:18px}
.join-card .foot a{color:var(--accent2)}
</style></head><body>
<div class="join-card">
<h1>Join your class</h1>
<p>Enter the code your teacher gave you.</p>
<form onsubmit="go(event)">
<input id="code" maxlength="8" autocomplete="off" autocapitalize="characters" placeholder="ABC123" autofocus>
<button type="submit">Go →</button>
<div class="err" id="err"></div>
</form>
<div class="foot">Teacher? <a href="/lemma/teachers">Sign in here</a></div>
</div>
<script>
function go(e){
  e.preventDefault();
  const code = document.getElementById('code').value.trim().toUpperCase();
  if(code.length < 4){ document.getElementById('err').textContent = 'Codes are at least 4 characters.'; return; }
  location.href = '/lemma/c/' + encodeURIComponent(code);
}
</script>
</body></html>"""
    return HTMLResponse(page.replace("__CSS__", _shared_css()))


@router.get("/lemma/c/{code}", response_class=HTMLResponse)
async def lemma_class_entry(code: str) -> HTMLResponse:
    code = code.upper()
    with _conn() as c:
        row = c.execute("SELECT 1 FROM classes WHERE code = ?", (code,)).fetchone()
    if not row:
        return HTMLResponse(f"<body style='font-family:sans-serif;padding:40px;text-align:center'><h1>Class not found</h1><p>The code <code>{code}</code> isn't recognized. Ask your teacher for the correct link.</p></body>", status_code=404)
    page = _STUDENT_PAGE.replace("__CSS__", _shared_css()).replace("__CODE__", code).replace("__COURSE_NAMES__", _course_names_js())
    return HTMLResponse(page)


# ---------------------------------------------------------------------------
# Demo seeding — fills a class with a realistic roster + graded warmups so the
# teacher dashboard is alive the moment you open it (for showing the product).
# ---------------------------------------------------------------------------

_DEMO_NAMES = [
    "Alex Rivera", "Maya Chen", "Jordan Brooks", "Priya Patel", "Liam O'Connor",
    "Sofia Garcia", "Noah Kim", "Ava Thompson", "Ethan Nguyen", "Zoe Williams",
    "Diego Morales", "Hannah Cohen", "Marcus Johnson", "Lily Anderson", "Omar Hassan",
    "Grace Park", "Tyler Scott", "Isabella Rossi",
]

_DEMO_TOPICS = {
    "calc-bc": ["Limits & Continuity", "Derivative Rules", "Related Rates", "Optimization",
                "Riemann Sums", "Fundamental Theorem", "Integration by Parts", "Series Convergence",
                "Taylor Series", "Parametric & Polar"],
    "calc-ab": ["Limits", "Derivative Rules", "Chain Rule", "Related Rates", "Optimization",
                "Riemann Sums", "Fundamental Theorem", "Volumes of Revolution"],
    "precalc": ["Function Transformations", "Trig Identities", "Unit Circle", "Logarithms",
                "Polynomial Roots", "Sequences", "Conic Sections", "Vectors"],
    "algebra-1": ["Linear Equations", "Slope & Lines", "Systems", "Inequalities",
                  "Exponents", "Factoring", "Quadratics", "Word Problems"],
    "algebra-2": ["Quadratics", "Complex Numbers", "Polynomials", "Rational Functions",
                  "Exponentials", "Logarithms", "Sequences", "Matrices"],
    "geometry": ["Angles & Lines", "Triangles", "Congruence", "Similarity",
                 "Pythagorean Theorem", "Circles", "Area & Volume", "Coordinate Proofs"],
    "stats": ["Sampling Methods", "Describing Data", "The Normal Model", "Probability",
              "Sampling Distributions", "Confidence Intervals", "Hypothesis Tests", "Regression"],
}
_DEFAULT_TOPICS = ["Warmup Set A", "Warmup Set B", "Warmup Set C", "Warmup Set D", "Review", "Mixed Practice"]


@router.post("/lemma/api/class/{code}/seed")
async def seed_class(code: str, req: Request) -> JSONResponse:
    """Populate a class with a believable roster + ~2 weeks of graded warmups.
    Clears any existing roster/submissions for the code first, so it's a clean
    re-seed every time (intended for demo classes)."""
    code = code.upper()
    try:
        body = await req.json()
    except Exception:
        body = {}
    n_students = max(4, min(len(_DEMO_NAMES), int(body.get("students") or 14)))
    n_days = max(3, min(20, int(body.get("days") or 12)))
    with _conn() as c:
        row = c.execute("SELECT course_id FROM classes WHERE code = ?", (code,)).fetchone()
        if not row:
            raise HTTPException(404, "class not found")
        course_id = row["course_id"]
        c.execute("DELETE FROM students WHERE class_code = ?", (code,))
        c.execute("DELETE FROM submissions WHERE class_code = ?", (code,))
        topics = _DEMO_TOPICS.get(course_id, _DEFAULT_TOPICS)
        rng = random.Random(sum((i + 1) * ord(ch) for i, ch in enumerate(code)))
        names = _DEMO_NAMES[:n_students]
        abilities = {nm: max(0.42, min(0.96, rng.gauss(0.74, 0.13))) for nm in names}
        now = datetime.now(timezone.utc)
        joined = (now - timedelta(days=n_days)).isoformat(timespec="seconds")
        for nm in names:
            c.execute("INSERT INTO students (class_code, name, joined_at) VALUES (?,?,?)", (code, nm, joined))
        sub_rows = []
        for d in range(n_days, -1, -1):  # oldest .. today
            day = now - timedelta(days=d)
            if day.weekday() >= 5:        # skip weekends
                continue
            date_str = day.strftime("%Y-%m-%d")
            topic = topics[(n_days - d) % len(topics)]
            for nm in names:
                if d != 0 and rng.random() > 0.82:      # ~18% absent on past days
                    continue
                if d == 0 and rng.random() > 0.6:        # today: ~60% have submitted so far
                    continue
                total = 4
                abil = abilities[nm] + rng.gauss(0, 0.08)
                correct = sum(1 for _ in range(total) if rng.random() < abil)
                ts = day.replace(hour=8, minute=rng.randint(0, 55), second=0).isoformat(timespec="seconds")
                sub_rows.append((code, nm, date_str, topic, correct, total, "[]", ts))
        c.executemany(
            "INSERT INTO submissions (class_code, student_name, warmup_date, topic, correct, total, details, submitted_at) VALUES (?,?,?,?,?,?,?,?)",
            sub_rows,
        )
    return JSONResponse({"ok": True, "students": len(names), "submissions": len(sub_rows), "course_id": course_id})


_DEMO_PAGE = r"""<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lemma · Live Demo</title>
<style>__CSS__
.big{font-size:18px;padding:15px 32px}
.step{display:flex;gap:14px;align-items:flex-start;margin:12px 0}
.step .n{flex:none;width:26px;height:26px;border-radius:50%;background:var(--accent);color:#0a0d14;font-weight:800;display:flex;align-items:center;justify-content:center;font-family:'SF Mono',monospace;font-size:13px}
.step .t{font-size:14px;color:var(--text)}
.step .t b{color:var(--accent2)}
</style></head><body>

<nav>
  <a href="/lemma" style="color:var(--dim)">← Lemma</a>
  <span class="brand">/lemma</span>
  <span style="color:var(--accent2);font-weight:600">/demo</span>
  <span class="nav-links"><a href="/lemma/start">Start a real class</a></span>
</nav>

<div class="container">

<h1>See Lemma live</h1>
<p class="lede">One click builds a real classroom — a full roster of students and two weeks of graded daily warmups — and drops you straight into the teacher dashboard. Everything you see is the actual product, just pre-filled so there's something to look at.</p>

<div class="panel" style="text-align:center;border-left:3px solid var(--accent)">
  <button class="btn big" id="go" onclick="launch()">▶ Launch a demo classroom</button>
  <p class="lede" id="status" style="margin:14px 0 0 0;display:none"></p>
</div>

<div class="panel">
  <h2>What you're about to see</h2>
  <div class="step"><div class="n">1</div><div class="t"><b>The teacher dashboard</b> — roster, class accuracy, who's submitted today, recent graded warmups, a "needs attention" list, and the hardest topics to reteach.</div></div>
  <div class="step"><div class="n">2</div><div class="t"><b>The join code</b> — students open a link, type their name, and they're in. Try it from the "Student view" link on the dashboard.</div></div>
  <div class="step"><div class="n">3</div><div class="t"><b>The warmup app</b> — adaptive daily problems students work on paper; the teacher bulk-grades the photos and scores flow back to the dashboard live.</div></div>
</div>

<div class="panel">
  <h3>Prefer to start your own?</h3>
  <p class="lede" style="margin-bottom:10px">Make a real class for your own students in about 30 seconds.</p>
  <a class="btn ghost" href="/lemma/start">🎓 Start a real class</a>
</div>

</div>

<script>
async function launch(){
  const btn=document.getElementById('go'), st=document.getElementById('status');
  btn.disabled=true; btn.textContent='Building your classroom…';
  st.style.display=''; st.textContent='Creating the class and seeding two weeks of warmups…';
  try{
    const r=await fetch('/lemma/api/class/create',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({teacher_name:'Demo Teacher',class_name:'Period 3 · AP Calculus BC',course_id:'calc-bc'})});
    if(!r.ok) throw new Error(await r.text());
    const d=await r.json();
    await fetch('/lemma/api/class/'+d.code+'/seed',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({students:14,days:12})});
    window.location.href='/lemma/teacher/'+d.code;
  }catch(e){ st.textContent='Something went wrong — '+e.message; btn.disabled=false; btn.textContent='▶ Launch a demo classroom'; }
}
</script>
</body></html>
"""


@router.get("/lemma/demo", response_class=HTMLResponse)
async def lemma_demo() -> HTMLResponse:
    return HTMLResponse(_DEMO_PAGE.replace("__CSS__", _shared_css()))
