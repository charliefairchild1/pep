"""Lemma ↔ Canvas LMS integration.

Token-based integration that works today (no LTI 1.3 OIDC dance needed).

The teacher:
  1. Generates a Canvas access token in their Canvas profile settings
  2. Pastes it into /lemma/canvas/setup along with their Canvas base URL
  3. Picks one of their Canvas courses to link to a Lemma class
  4. Adds the Lemma class URL as a Module item (External URL) in Canvas

Then:
  - Lemma can pull the roster from Canvas (sync-roster)
  - Lemma can push warmup grades back to Canvas (push-grades), either on
    demand or automatically on every submission

We store the Canvas access token in SQLite per linked Lemma class. The token
never leaves the server.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse

from pep.routes.lemma_backend import _DB_PATH, _conn, _now


router = APIRouter()


# ---------------------------------------------------------------------------
# Schema additions — idempotent
# ---------------------------------------------------------------------------

def _init_canvas_db() -> None:
    with _conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS canvas_links (
            class_code            TEXT PRIMARY KEY,
            canvas_base_url       TEXT NOT NULL,
            access_token          TEXT NOT NULL,
            canvas_course_id      TEXT NOT NULL,
            canvas_course_name    TEXT,
            canvas_assignment_id  TEXT,
            canvas_user_name      TEXT,
            auto_push             INTEGER NOT NULL DEFAULT 1,
            created_at            TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS canvas_student_map (
            class_code         TEXT NOT NULL,
            lemma_student_name TEXT NOT NULL,
            canvas_user_id     TEXT NOT NULL,
            canvas_user_name   TEXT,
            PRIMARY KEY (class_code, lemma_student_name)
        );
        CREATE TABLE IF NOT EXISTS canvas_grade_log (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            class_code   TEXT NOT NULL,
            student_name TEXT NOT NULL,
            score        REAL NOT NULL,
            pushed_at    TEXT NOT NULL,
            ok           INTEGER NOT NULL,
            error        TEXT
        );
        CREATE INDEX IF NOT EXISTS canvas_grade_log_class_idx
            ON canvas_grade_log(class_code);
        """)


_init_canvas_db()


# ---------------------------------------------------------------------------
# Canvas API helpers
# ---------------------------------------------------------------------------

def _normalize_base(url: str) -> str:
    u = (url or "").strip()
    if not u:
        raise HTTPException(400, "Canvas URL required")
    if not u.startswith(("http://", "https://")):
        u = "https://" + u
    return u.rstrip("/")


async def _cget(base: str, token: str, path: str, params: dict | None = None) -> Any:
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        r = await client.get(f"{base}{path}", headers=headers, params=params)
        if r.status_code == 401:
            raise HTTPException(401, "Canvas rejected the token. Generate a new one in Canvas → Account → Settings → New Access Token.")
        if r.status_code >= 400:
            raise HTTPException(r.status_code, f"Canvas API error: {r.text[:200]}")
        return r.json()


async def _cpost(base: str, token: str, path: str, data: dict) -> Any:
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        r = await client.post(f"{base}{path}", headers=headers, data=data)
        if r.status_code >= 400:
            raise HTTPException(r.status_code, f"Canvas API error: {r.text[:200]}")
        return r.json()


async def _cput(base: str, token: str, path: str, data: dict) -> Any:
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        r = await client.put(f"{base}{path}", headers=headers, data=data)
        if r.status_code >= 400:
            raise HTTPException(r.status_code, f"Canvas API error: {r.text[:200]}")
        return r.json()


# ---------------------------------------------------------------------------
# Public API endpoints
# ---------------------------------------------------------------------------

@router.post("/lemma/api/canvas/validate")
async def canvas_validate(req: Request) -> JSONResponse:
    """Teacher pastes their Canvas URL + token. We verify and return their courses."""
    body = await req.json()
    base = _normalize_base(body.get("canvas_url") or "")
    token = (body.get("token") or "").strip()
    if not token:
        raise HTTPException(400, "Canvas access token required")
    # who are they?
    me = await _cget(base, token, "/api/v1/users/self/profile")
    # list their teacher courses (active enrollments only)
    courses = await _cget(base, token, "/api/v1/courses", params={
        "enrollment_type": "teacher",
        "enrollment_state": "active",
        "per_page": "100",
    })
    return JSONResponse({
        "ok": True,
        "user_name": me.get("name") or me.get("short_name") or "Teacher",
        "user_id": me.get("id"),
        "canvas_url": base,
        "courses": [
            {
                "id": str(c["id"]),
                "name": c.get("name") or c.get("course_code") or f"Course {c['id']}",
                "course_code": c.get("course_code"),
            }
            for c in courses if c.get("id")
        ],
    })


@router.post("/lemma/api/canvas/link/{code}")
async def canvas_link(code: str, req: Request) -> JSONResponse:
    """Link a Lemma class to a Canvas course; create the assignment in Canvas."""
    code = code.upper()
    body = await req.json()
    base = _normalize_base(body.get("canvas_url") or "")
    token = (body.get("token") or "").strip()
    course_id = str(body.get("canvas_course_id") or "").strip()
    course_name = (body.get("canvas_course_name") or "").strip()
    user_name = (body.get("user_name") or "").strip() or None
    if not token or not course_id:
        raise HTTPException(400, "token and canvas_course_id required")
    # verify the class exists
    with _conn() as c:
        row = c.execute("SELECT class_name FROM classes WHERE code = ?", (code,)).fetchone()
        if not row:
            raise HTTPException(404, "Lemma class not found")
        class_name = row["class_name"]
    # create or reuse a Canvas assignment for grade pushing
    assignment_name = f"Lemma Warmups — {class_name}"
    existing = await _cget(base, token, f"/api/v1/courses/{course_id}/assignments", params={
        "search_term": "Lemma Warmups",
        "per_page": "20",
    })
    assignment_id = None
    for a in (existing or []):
        if (a.get("name") or "").startswith("Lemma Warmups"):
            assignment_id = str(a["id"])
            break
    if not assignment_id:
        created = await _cpost(base, token, f"/api/v1/courses/{course_id}/assignments", {
            "assignment[name]": assignment_name,
            "assignment[points_possible]": "100",
            "assignment[grading_type]": "percent",
            "assignment[submission_types][]": "none",
            "assignment[published]": "true",
            "assignment[description]": (
                "Daily warmups in Lemma — grades push back here automatically. "
                f"Students enter at /lemma/c/{code}"
            ),
        })
        assignment_id = str(created.get("id") or "")
    # save link
    with _conn() as c:
        c.execute(
            "INSERT OR REPLACE INTO canvas_links "
            "(class_code, canvas_base_url, access_token, canvas_course_id, canvas_course_name, canvas_assignment_id, canvas_user_name, auto_push, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)",
            (code, base, token, course_id, course_name, assignment_id, user_name, _now()),
        )
    return JSONResponse({
        "ok": True,
        "class_code": code,
        "canvas_course_id": course_id,
        "canvas_assignment_id": assignment_id,
        "canvas_course_name": course_name,
    })


@router.get("/lemma/api/canvas/link/{code}")
async def canvas_link_status(code: str) -> JSONResponse:
    code = code.upper()
    with _conn() as c:
        row = c.execute(
            "SELECT canvas_base_url, canvas_course_id, canvas_course_name, canvas_assignment_id, canvas_user_name, auto_push, created_at "
            "FROM canvas_links WHERE class_code = ?",
            (code,),
        ).fetchone()
        if not row:
            return JSONResponse({"linked": False})
        last = c.execute(
            "SELECT pushed_at, ok, error FROM canvas_grade_log WHERE class_code = ? ORDER BY id DESC LIMIT 1",
            (code,),
        ).fetchone()
        total_pushed = c.execute(
            "SELECT COUNT(*) FROM canvas_grade_log WHERE class_code = ? AND ok = 1",
            (code,),
        ).fetchone()[0]
        roster_mapped = c.execute(
            "SELECT COUNT(*) FROM canvas_student_map WHERE class_code = ?",
            (code,),
        ).fetchone()[0]
    return JSONResponse({
        "linked": True,
        "canvas_url": row["canvas_base_url"],
        "canvas_course_id": row["canvas_course_id"],
        "canvas_course_name": row["canvas_course_name"],
        "canvas_assignment_id": row["canvas_assignment_id"],
        "canvas_user_name": row["canvas_user_name"],
        "auto_push": bool(row["auto_push"]),
        "linked_at": row["created_at"],
        "last_push": dict(last) if last else None,
        "total_grades_pushed": total_pushed,
        "roster_mapped_count": roster_mapped,
    })


@router.delete("/lemma/api/canvas/link/{code}")
async def canvas_unlink(code: str) -> JSONResponse:
    code = code.upper()
    with _conn() as c:
        c.execute("DELETE FROM canvas_links WHERE class_code = ?", (code,))
        c.execute("DELETE FROM canvas_student_map WHERE class_code = ?", (code,))
    return JSONResponse({"ok": True})


@router.post("/lemma/api/canvas/sync-roster/{code}")
async def canvas_sync_roster(code: str) -> JSONResponse:
    """Pull the Canvas course's roster + add each student to the Lemma class."""
    code = code.upper()
    link = _get_link(code)
    if not link:
        raise HTTPException(404, "Class is not linked to Canvas. Set up the link first.")
    base = link["canvas_base_url"]
    token = link["access_token"]
    course_id = link["canvas_course_id"]
    # paginate through users with student role
    students: list[dict[str, Any]] = []
    page = 1
    while page < 10:
        chunk = await _cget(base, token, f"/api/v1/courses/{course_id}/users", params={
            "enrollment_type[]": "student",
            "per_page": "100",
            "page": str(page),
        })
        if not chunk:
            break
        students.extend(chunk)
        if len(chunk) < 100:
            break
        page += 1
    added = 0
    mapped = 0
    with _conn() as c:
        for s in students:
            name = (s.get("name") or s.get("short_name") or "").strip()
            uid = str(s.get("id") or "").strip()
            if not name or not uid:
                continue
            try:
                c.execute(
                    "INSERT INTO students (class_code, name, joined_at) VALUES (?, ?, ?)",
                    (code, name, _now()),
                )
                added += 1
            except sqlite3.IntegrityError:
                pass
            c.execute(
                "INSERT OR REPLACE INTO canvas_student_map "
                "(class_code, lemma_student_name, canvas_user_id, canvas_user_name) "
                "VALUES (?, ?, ?, ?)",
                (code, name, uid, name),
            )
            mapped += 1
    return JSONResponse({"ok": True, "added": added, "mapped": mapped, "total_in_canvas": len(students)})


@router.post("/lemma/api/canvas/push-grades/{code}")
async def canvas_push_grades(code: str) -> JSONResponse:
    """Push aggregate accuracy (0–100) per student to the linked Canvas assignment."""
    code = code.upper()
    link = _get_link(code)
    if not link:
        raise HTTPException(404, "Class is not linked to Canvas.")
    if not link["canvas_assignment_id"]:
        raise HTTPException(400, "No Canvas assignment id is stored. Re-link the class.")
    base = link["canvas_base_url"]
    token = link["access_token"]
    course_id = link["canvas_course_id"]
    assignment_id = link["canvas_assignment_id"]
    # roll up per-student
    with _conn() as c:
        rows = c.execute(
            "SELECT student_name, SUM(correct) AS c, SUM(total) AS t "
            "FROM submissions WHERE class_code = ? GROUP BY student_name",
            (code,),
        ).fetchall()
        student_to_uid = dict(c.execute(
            "SELECT lemma_student_name, canvas_user_id FROM canvas_student_map WHERE class_code = ?",
            (code,),
        ).fetchall())
    pushed = 0
    skipped: list[str] = []
    errors: list[dict[str, str]] = []
    for r in rows:
        name = r["student_name"]
        total = int(r["t"] or 0)
        if total <= 0:
            continue
        score = round(100 * int(r["c"] or 0) / total, 1)
        uid = student_to_uid.get(name)
        if not uid:
            skipped.append(name)
            _log_grade(code, name, score, ok=False, error="no_canvas_user_id")
            continue
        try:
            await _cput(
                base, token,
                f"/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions/{uid}",
                {"submission[posted_grade]": f"{score}%"},
            )
            _log_grade(code, name, score, ok=True)
            pushed += 1
        except HTTPException as e:
            err = e.detail if isinstance(e.detail, str) else str(e.detail)
            errors.append({"student": name, "error": err})
            _log_grade(code, name, score, ok=False, error=err)
    return JSONResponse({"ok": True, "pushed": pushed, "skipped": skipped, "errors": errors, "total_students": len(rows)})


@router.post("/lemma/api/canvas/auto-push/{code}")
async def canvas_set_auto_push(code: str, req: Request) -> JSONResponse:
    code = code.upper()
    body = await req.json()
    auto = 1 if body.get("auto_push") else 0
    with _conn() as c:
        r = c.execute("UPDATE canvas_links SET auto_push = ? WHERE class_code = ?", (auto, code))
    return JSONResponse({"ok": True, "auto_push": bool(auto)})


# ---------------------------------------------------------------------------
# Helpers used by lemma_backend on every submit (auto-push hook)
# ---------------------------------------------------------------------------

def _get_link(code: str) -> dict[str, Any] | None:
    with _conn() as c:
        row = c.execute("SELECT * FROM canvas_links WHERE class_code = ?", (code,)).fetchone()
        return dict(row) if row else None


def _log_grade(code: str, student: str, score: float, ok: bool, error: str | None = None) -> None:
    with _conn() as c:
        c.execute(
            "INSERT INTO canvas_grade_log (class_code, student_name, score, pushed_at, ok, error) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (code, student, score, _now(), 1 if ok else 0, error),
        )


async def maybe_auto_push_grade(code: str, student_name: str) -> dict[str, Any] | None:
    """Called from /lemma/api/class/{code}/submit. Returns push result or None.

    Pushes the student's cumulative accuracy for the linked assignment.
    Silently no-ops if there's no link or auto_push is off.
    """
    link = _get_link(code)
    if not link or not link.get("auto_push") or not link.get("canvas_assignment_id"):
        return None
    with _conn() as c:
        r = c.execute(
            "SELECT SUM(correct) AS c, SUM(total) AS t "
            "FROM submissions WHERE class_code = ? AND student_name = ?",
            (code, student_name),
        ).fetchone()
        uid_row = c.execute(
            "SELECT canvas_user_id FROM canvas_student_map WHERE class_code = ? AND lemma_student_name = ?",
            (code, student_name),
        ).fetchone()
    if not uid_row:
        _log_grade(code, student_name, 0.0, ok=False, error="no_canvas_user_id")
        return {"ok": False, "reason": "no_canvas_user_id"}
    total = int(r["t"] or 0) if r else 0
    if total <= 0:
        return None
    score = round(100 * int(r["c"] or 0) / total, 1)
    try:
        await _cput(
            link["canvas_base_url"], link["access_token"],
            f"/api/v1/courses/{link['canvas_course_id']}/assignments/{link['canvas_assignment_id']}/submissions/{uid_row['canvas_user_id']}",
            {"submission[posted_grade]": f"{score}%"},
        )
        _log_grade(code, student_name, score, ok=True)
        return {"ok": True, "score": score}
    except HTTPException as e:
        err = e.detail if isinstance(e.detail, str) else str(e.detail)
        _log_grade(code, student_name, score, ok=False, error=err)
        return {"ok": False, "error": err}


# ---------------------------------------------------------------------------
# UI pages
# ---------------------------------------------------------------------------

_SETUP_PAGE = r"""<!DOCTYPE html><html><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Connect Lemma to Canvas</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#f8fafc;color:#1e293b;font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;line-height:1.55;padding:30px 16px}
.wrap{max-width:720px;margin:0 auto}
h1{font-size:26px;font-weight:650;margin-bottom:8px;color:#0f172a}
h1 span{color:#dc2626}
.lead{color:#64748b;margin-bottom:20px;font-size:14.5px}
.card{background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:22px 24px;margin-bottom:16px;box-shadow:0 1px 2px rgba(0,0,0,0.03)}
.card h2{font-size:17px;font-weight:650;margin-bottom:5px;color:#0f172a}
.card .sub{color:#64748b;font-size:13px;margin-bottom:14px}
.field{margin-bottom:12px}
.field label{display:block;font-size:13px;font-weight:600;color:#475569;margin-bottom:4px}
.field input{width:100%;padding:9px 12px;border:1px solid #cbd5e1;border-radius:7px;font:inherit;font-size:14px;background:#fff}
.field input:focus{outline:none;border-color:#0ea5e9;box-shadow:0 0 0 3px rgba(14,165,233,0.12)}
.help{font-size:12px;color:#64748b;margin-top:3px;line-height:1.5}
.help code{background:#f1f5f9;padding:1px 5px;border-radius:3px;font-size:11.5px;color:#0f172a}
.btn{font:inherit;font-size:14px;background:#0ea5e9;color:#fff;border:none;border-radius:7px;padding:9px 18px;cursor:pointer;font-weight:600}
.btn:hover{background:#0284c7}
.btn:disabled{opacity:0.6;cursor:not-allowed}
.btn.ghost{background:#fff;color:#0ea5e9;border:1px solid #0ea5e9}
.btn.ghost:hover{background:#f0f9ff}
.alert{background:#fef2f2;border:1px solid #fecaca;color:#991b1b;padding:11px 13px;border-radius:7px;font-size:13.5px;margin-top:12px}
.alert.ok{background:#f0fdf4;border-color:#bbf7d0;color:#166534}
.courses{display:flex;flex-direction:column;gap:8px;margin-top:14px;max-height:380px;overflow-y:auto}
.course{background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:12px 14px;cursor:pointer;transition:border-color 0.15s,background 0.15s}
.course:hover{border-color:#0ea5e9;background:#f0f9ff}
.course.sel{border-color:#0ea5e9;background:#e0f2fe;box-shadow:0 0 0 2px rgba(14,165,233,0.2) inset}
.course .nm{font-weight:600;color:#0f172a;font-size:14px}
.course .cd{color:#64748b;font-size:12px;margin-top:2px}
.classChoice{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:16px}
.classChoice .opt{background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:14px 16px}
.classChoice .opt h3{font-size:14px;font-weight:650;color:#0f172a;margin-bottom:6px}
.classChoice .opt p{font-size:12.5px;color:#64748b;margin-bottom:10px}
.hide{display:none}
.nav-back{color:#64748b;text-decoration:none;font-size:13px;margin-bottom:14px;display:inline-block}
.nav-back:hover{color:#0ea5e9}
.steps{counter-reset:s;margin-bottom:20px}
.step{counter-increment:s;display:flex;gap:14px;padding:10px 0}
.step::before{content:counter(s);background:#0ea5e9;color:#fff;width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px;flex-shrink:0}
.step .stxt{font-size:13.5px;color:#334155;line-height:1.55}
.step .stxt b{color:#0f172a}
.step a{color:#0284c7;text-decoration:none}.step a:hover{text-decoration:underline}
</style></head><body>
<div class="wrap">
  <a href="/lemma/start" class="nav-back">← back to start</a>

  <h1>Connect Lemma to Canvas <span>·</span> <span style="color:#0ea5e9">step 1</span></h1>
  <p class="lead">After this, your students click a link in Canvas and land in Lemma in the right class. Their warmup grades push back to Canvas automatically.</p>

  <div class="card">
    <h2>How to get your Canvas access token</h2>
    <div class="steps">
      <div class="step"><div class="stxt">In Canvas, click your profile picture (top-left) → <b>Account</b> → <b>Settings</b>.</div></div>
      <div class="step"><div class="stxt">Scroll down to <b>Approved Integrations</b>. Click <b>+ New Access Token</b>.</div></div>
      <div class="step"><div class="stxt">Give it any purpose name (e.g. <code>Lemma</code>). Leave the expiry blank. Click <b>Generate Token</b>.</div></div>
      <div class="step"><div class="stxt">Copy the token string. <b>It only shows once</b> — Canvas won't let you see it again.</div></div>
    </div>
    <p style="font-size:12.5px;color:#64748b">The token lets Lemma act in Canvas on your behalf — read your roster, post grades. It never leaves this server; you can delete it any time by unlinking the class.</p>
  </div>

  <div class="card">
    <h2>Enter your Canvas info</h2>
    <div class="sub">Lemma will validate your token and list your active courses.</div>
    <div class="field">
      <label>Your Canvas URL</label>
      <input id="canvasUrl" type="text" placeholder="https://canvas.instructure.com" autocomplete="off">
      <div class="help">The address you log into. For a school it might be <code>https://[yourschool].instructure.com</code>.</div>
    </div>
    <div class="field">
      <label>Access token</label>
      <input id="canvasToken" type="password" placeholder="paste the token you just generated" autocomplete="off">
      <div class="help">Stored only on this server. Never sent to anyone else.</div>
    </div>
    <button id="validateBtn" class="btn">Validate & continue →</button>
    <div id="validateMsg"></div>
  </div>

  <div id="courseSection" class="card hide">
    <h2>Pick the Canvas course to connect</h2>
    <div class="sub" id="whoami"></div>
    <div class="courses" id="coursesList"></div>
  </div>

  <div id="classChoice" class="card hide">
    <h2>Use this Lemma class</h2>
    <div class="sub" id="chosenCourse"></div>
    <div class="classChoice">
      <div class="opt">
        <h3>Create a new Lemma class</h3>
        <p>Recommended. Picks AP Calc BC by default. You can change the subject later.</p>
        <button id="createBtn" class="btn">Create + link →</button>
      </div>
      <div class="opt">
        <h3>Link an existing class</h3>
        <p>Use your 6-character join code if you already have a Lemma class running.</p>
        <input id="existingCode" type="text" placeholder="join code" maxlength="6" style="width:100%;padding:8px 11px;border:1px solid #cbd5e1;border-radius:6px;text-transform:uppercase;font-family:ui-monospace,monospace;font-size:14px;margin-bottom:8px">
        <button id="linkExistingBtn" class="btn ghost">Link this code →</button>
      </div>
    </div>
    <div id="linkMsg"></div>
  </div>

  <div id="doneCard" class="card hide" style="border-color:#bbf7d0;background:#f0fdf4">
    <h2 style="color:#166534">✓ Connected.</h2>
    <p style="margin-bottom:14px;color:#166534;font-size:14px">Your Lemma class is linked to Canvas. Now add the Lemma class link to a Canvas module so your students can click in.</p>
    <div id="doneInfo"></div>
    <a id="dashLink" class="btn" style="display:inline-block;text-decoration:none;margin-top:14px" href="#">Open the teacher dashboard →</a>
  </div>
</div>

<script>
let canvasUrl = '', canvasToken = '', courses = [], picked = null, userName = '';

document.getElementById('validateBtn').addEventListener('click', async (e)=>{
  e.target.disabled = true;
  document.getElementById('validateMsg').innerHTML = '';
  canvasUrl = document.getElementById('canvasUrl').value.trim();
  canvasToken = document.getElementById('canvasToken').value.trim();
  if(!canvasUrl || !canvasToken){
    document.getElementById('validateMsg').innerHTML = '<div class="alert">Both the Canvas URL and an access token are required.</div>';
    e.target.disabled = false;
    return;
  }
  try {
    const r = await fetch('/lemma/api/canvas/validate', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({canvas_url: canvasUrl, token: canvasToken}),
    });
    const data = await r.json();
    if(!r.ok){
      document.getElementById('validateMsg').innerHTML = '<div class="alert">' + escapeHTML(data.detail || 'Validation failed.') + '</div>';
      e.target.disabled = false;
      return;
    }
    canvasUrl = data.canvas_url;
    courses = data.courses || [];
    userName = data.user_name;
    document.getElementById('whoami').innerHTML = `Signed in as <b>${escapeHTML(userName)}</b>. Pick the course this Lemma class belongs to.`;
    document.getElementById('validateMsg').innerHTML = '<div class="alert ok">Connected as ' + escapeHTML(userName) + ' — ' + courses.length + ' active course(s).</div>';
    renderCourses();
    document.getElementById('courseSection').classList.remove('hide');
    document.getElementById('courseSection').scrollIntoView({behavior:'smooth',block:'start'});
  } catch(err){
    document.getElementById('validateMsg').innerHTML = '<div class="alert">Network error: ' + escapeHTML(err.message) + '</div>';
  } finally {
    e.target.disabled = false;
  }
});

function renderCourses(){
  if(!courses.length){
    document.getElementById('coursesList').innerHTML = '<div class="alert">No active teacher-courses found. Are you teaching this term?</div>';
    return;
  }
  document.getElementById('coursesList').innerHTML = courses.map(c => `
    <div class="course" data-id="${c.id}">
      <div class="nm">${escapeHTML(c.name)}</div>
      ${c.course_code ? '<div class="cd">' + escapeHTML(c.course_code) + '</div>' : ''}
    </div>`).join('');
  for(const el of document.querySelectorAll('.course')){
    el.addEventListener('click', ()=>pickCourse(el.dataset.id));
  }
}

function pickCourse(id){
  picked = courses.find(c => c.id === id);
  if(!picked) return;
  for(const el of document.querySelectorAll('.course')){
    el.classList.toggle('sel', el.dataset.id === id);
  }
  document.getElementById('chosenCourse').innerHTML = `Linking <b>${escapeHTML(picked.name)}</b>.`;
  document.getElementById('classChoice').classList.remove('hide');
  document.getElementById('classChoice').scrollIntoView({behavior:'smooth',block:'start'});
}

document.getElementById('createBtn').addEventListener('click', async (e)=>{
  if(!picked) return;
  e.target.disabled = true;
  try {
    const cr = await fetch('/lemma/api/class/create', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        teacher_name: userName || 'Teacher',
        class_name: picked.name,
        course_id: 'calc-bc',
      }),
    });
    const cls = await cr.json();
    if(!cr.ok) throw new Error(cls.detail || 'Could not create Lemma class');
    await linkAndFinish(cls.code);
  } catch(err){
    document.getElementById('linkMsg').innerHTML = '<div class="alert">' + escapeHTML(err.message) + '</div>';
  } finally {
    e.target.disabled = false;
  }
});

document.getElementById('linkExistingBtn').addEventListener('click', async (e)=>{
  if(!picked) return;
  const code = document.getElementById('existingCode').value.trim().toUpperCase();
  if(code.length !== 6){
    document.getElementById('linkMsg').innerHTML = '<div class="alert">Join code must be 6 characters.</div>';
    return;
  }
  e.target.disabled = true;
  try { await linkAndFinish(code); }
  catch(err){
    document.getElementById('linkMsg').innerHTML = '<div class="alert">' + escapeHTML(err.message) + '</div>';
  } finally { e.target.disabled = false; }
});

async function linkAndFinish(code){
  const r = await fetch('/lemma/api/canvas/link/' + code, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      canvas_url: canvasUrl,
      token: canvasToken,
      canvas_course_id: picked.id,
      canvas_course_name: picked.name,
      user_name: userName,
    }),
  });
  const data = await r.json();
  if(!r.ok) throw new Error(data.detail || 'Linking failed.');
  // sync roster too (in the background)
  fetch('/lemma/api/canvas/sync-roster/' + code, {method:'POST'}).catch(()=>{});
  showDone(code);
}

function showDone(code){
  const lemmaUrl = location.origin + '/lemma/c/' + code;
  document.getElementById('doneInfo').innerHTML = `
    <div style="background:#fff;border:1px solid #bbf7d0;border-radius:8px;padding:13px 15px;font-size:13.5px;line-height:1.65">
      <b style="color:#166534">Add this URL to a Canvas module:</b><br>
      <code style="background:#f0fdf4;padding:5px 9px;border-radius:5px;display:inline-block;margin-top:6px;color:#166534;font-size:13px;word-break:break-all">${lemmaUrl}</code><br>
      <div style="margin-top:10px;color:#15803d">In Canvas → Modules → + → External URL → paste above. Check "Load in new tab."</div>
    </div>
    <div style="margin-top:10px;padding:11px 13px;background:#fefce8;border:1px solid #fde68a;border-radius:7px;color:#854d0e;font-size:13px">
      <b>Grades push automatically</b> on every warmup submission. Manage the link from the teacher dashboard.
    </div>`;
  document.getElementById('dashLink').href = '/lemma/teacher/' + code;
  document.getElementById('classChoice').classList.add('hide');
  document.getElementById('doneCard').classList.remove('hide');
  document.getElementById('doneCard').scrollIntoView({behavior:'smooth',block:'start'});
}

function escapeHTML(s){ return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
</script>
</body></html>"""


@router.get("/lemma/canvas/setup", response_class=HTMLResponse)
async def lemma_canvas_setup() -> HTMLResponse:
    return HTMLResponse(_SETUP_PAGE)


@router.get("/lemma/canvas", response_class=HTMLResponse)
async def lemma_canvas_redirect() -> HTMLResponse:
    return HTMLResponse('<meta http-equiv="refresh" content="0; url=/lemma/canvas/setup">')
