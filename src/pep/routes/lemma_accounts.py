"""Lemma teacher accounts — signup, login, "my classes" dashboard.

Adds a real account layer to Lemma so teachers can:
  - sign up with email + password
  - log in and see all their classes in one place
  - have classes they create be persistently theirs

Uses stdlib only (hashlib PBKDF2 for passwords, secrets for tokens, SQLite
for storage). No external auth dependencies.

Routes:
  GET  /lemma/teachers           — marketing / signup landing
  GET  /lemma/signup             — signup form
  GET  /lemma/login              — login form
  GET  /lemma/me                 — "my classes" dashboard (requires session)
  POST /lemma/api/account/signup
  POST /lemma/api/account/login
  POST /lemma/api/account/logout
  GET  /lemma/api/account/me
"""
from __future__ import annotations

import hashlib
import os
import re
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from pep.routes.lemma_backend import _conn, _now


router = APIRouter()


# ---------------------------------------------------------------------------
# Schema additions
# ---------------------------------------------------------------------------

def _init_account_db() -> None:
    with _conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS teachers (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            email         TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            display_name  TEXT NOT NULL,
            school        TEXT,
            created_at    TEXT NOT NULL,
            last_login    TEXT,
            email_verified INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS teacher_sessions (
            token       TEXT PRIMARY KEY,
            teacher_id  INTEGER NOT NULL,
            created_at  TEXT NOT NULL,
            expires_at  TEXT NOT NULL,
            FOREIGN KEY (teacher_id) REFERENCES teachers(id)
        );
        CREATE INDEX IF NOT EXISTS sessions_teacher_idx ON teacher_sessions(teacher_id);
        CREATE TABLE IF NOT EXISTS password_resets (
            token       TEXT PRIMARY KEY,
            teacher_id  INTEGER NOT NULL,
            created_at  TEXT NOT NULL,
            expires_at  TEXT NOT NULL,
            used        INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (teacher_id) REFERENCES teachers(id)
        );
        CREATE TABLE IF NOT EXISTS email_verifications (
            token       TEXT PRIMARY KEY,
            teacher_id  INTEGER NOT NULL,
            created_at  TEXT NOT NULL,
            used        INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (teacher_id) REFERENCES teachers(id)
        );
        CREATE TABLE IF NOT EXISTS teacher_invites (
            token              TEXT PRIMARY KEY,
            inviter_id         INTEGER NOT NULL,
            email              TEXT NOT NULL,
            message            TEXT,
            created_at         TEXT NOT NULL,
            used               INTEGER NOT NULL DEFAULT 0,
            used_by_teacher_id INTEGER,
            FOREIGN KEY (inviter_id) REFERENCES teachers(id),
            FOREIGN KEY (used_by_teacher_id) REFERENCES teachers(id)
        );
        CREATE INDEX IF NOT EXISTS invites_inviter_idx ON teacher_invites(inviter_id);
        """)
        # Migrate existing classes table if teacher_id column doesn't exist
        cols = {r["name"] for r in c.execute("PRAGMA table_info(classes)")}
        if "teacher_id" not in cols:
            c.execute("ALTER TABLE classes ADD COLUMN teacher_id INTEGER REFERENCES teachers(id)")
        # Migrate teachers table if email_verified column doesn't exist
        tcols = {r["name"] for r in c.execute("PRAGMA table_info(teachers)")}
        if "email_verified" not in tcols:
            c.execute("ALTER TABLE teachers ADD COLUMN email_verified INTEGER NOT NULL DEFAULT 0")


_init_account_db()


# ---------------------------------------------------------------------------
# Password hashing + session helpers
# ---------------------------------------------------------------------------

SESSION_COOKIE = "lemma_session"
SESSION_DAYS = 30
PBKDF2_ITERATIONS = 200_000


def hash_password(pw: str) -> str:
    salt = os.urandom(16)
    h = hashlib.pbkdf2_hmac("sha256", pw.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt.hex()}${h.hex()}"


def verify_password(pw: str, stored: str) -> bool:
    try:
        algo, iter_s, salt_hex, hash_hex = stored.split("$", 3)
        if algo != "pbkdf2_sha256":
            return False
        iterations = int(iter_s)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
        h = hashlib.pbkdf2_hmac("sha256", pw.encode("utf-8"), salt, iterations)
        return secrets.compare_digest(h, expected)
    except Exception:  # noqa: BLE001
        return False


def issue_session(teacher_id: int) -> tuple[str, datetime]:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS)
    with _conn() as c:
        c.execute(
            "INSERT INTO teacher_sessions (token, teacher_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
            (token, teacher_id, _now(), expires_at.isoformat(timespec="seconds")),
        )
    return token, expires_at


def revoke_session(token: str) -> None:
    with _conn() as c:
        c.execute("DELETE FROM teacher_sessions WHERE token = ?", (token,))


def get_current_teacher(req: Request) -> dict[str, Any] | None:
    token = req.cookies.get(SESSION_COOKIE)
    if not token:
        return None
    with _conn() as c:
        row = c.execute(
            """SELECT t.id, t.email, t.display_name, t.school, t.created_at
               FROM teachers t
               JOIN teacher_sessions s ON s.teacher_id = t.id
               WHERE s.token = ? AND s.expires_at > ?""",
            (token, _now()),
        ).fetchone()
    return dict(row) if row else None


_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def _set_cookie(resp: Response, token: str, expires_at: datetime) -> None:
    resp.set_cookie(
        SESSION_COOKIE,
        token,
        expires=int(expires_at.timestamp()),
        httponly=True,
        samesite="lax",
        secure=False,  # set True behind HTTPS in production
        path="/",
    )


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------

@router.post("/lemma/api/account/signup")
async def account_signup(req: Request, resp: Response) -> JSONResponse:
    body = await req.json()
    email = (body.get("email") or "").strip().lower()
    password = body.get("password") or ""
    display_name = (body.get("display_name") or "").strip()
    school = (body.get("school") or "").strip() or None
    if not email or not _EMAIL_RE.match(email):
        raise HTTPException(400, "valid email required")
    if len(password) < 8:
        raise HTTPException(400, "password must be at least 8 characters")
    if not display_name or len(display_name) > 80:
        raise HTTPException(400, "display name required (≤ 80 chars)")
    pw_hash = hash_password(password)
    invite_token = (body.get("invite_token") or "").strip() or None
    try:
        with _conn() as c:
            cur = c.execute(
                "INSERT INTO teachers (email, password_hash, display_name, school, created_at, last_login) VALUES (?, ?, ?, ?, ?, ?)",
                (email, pw_hash, display_name, school, _now(), _now()),
            )
            teacher_id = cur.lastrowid
            # consume the invite token if present + valid
            if invite_token:
                inv = c.execute(
                    "SELECT email, used FROM teacher_invites WHERE token = ?",
                    (invite_token,),
                ).fetchone()
                if inv and not inv["used"]:
                    c.execute(
                        "UPDATE teacher_invites SET used = 1, used_by_teacher_id = ? WHERE token = ?",
                        (teacher_id, invite_token),
                    )
    except sqlite3.IntegrityError:
        raise HTTPException(409, "an account with that email already exists. Try logging in instead.")
    # send verification email (fires-and-prints in dev)
    try:
        _send_verification(req, teacher_id, email, display_name)
    except Exception:  # noqa: BLE001
        pass
    token, expires_at = issue_session(teacher_id)
    out = JSONResponse({"ok": True, "teacher": {"id": teacher_id, "email": email, "display_name": display_name, "school": school}})
    _set_cookie(out, token, expires_at)
    return out


@router.post("/lemma/api/account/login")
async def account_login(req: Request) -> JSONResponse:
    body = await req.json()
    email = (body.get("email") or "").strip().lower()
    password = body.get("password") or ""
    if not email or not password:
        raise HTTPException(400, "email and password required")
    with _conn() as c:
        row = c.execute(
            "SELECT id, email, password_hash, display_name, school FROM teachers WHERE email = ?",
            (email,),
        ).fetchone()
    if not row or not verify_password(password, row["password_hash"]):
        raise HTTPException(401, "no account matches that email + password")
    with _conn() as c:
        c.execute("UPDATE teachers SET last_login = ? WHERE id = ?", (_now(), row["id"]))
    token, expires_at = issue_session(row["id"])
    out = JSONResponse({"ok": True, "teacher": {"id": row["id"], "email": row["email"], "display_name": row["display_name"], "school": row["school"]}})
    _set_cookie(out, token, expires_at)
    return out


@router.post("/lemma/api/account/logout")
async def account_logout(req: Request) -> JSONResponse:
    token = req.cookies.get(SESSION_COOKIE)
    if token:
        revoke_session(token)
    out = JSONResponse({"ok": True})
    out.delete_cookie(SESSION_COOKIE, path="/")
    return out


@router.get("/lemma/api/account/me")
async def account_me(req: Request) -> JSONResponse:
    me = get_current_teacher(req)
    if not me:
        return JSONResponse({"authenticated": False})
    with _conn() as c:
        verified_row = c.execute("SELECT email_verified FROM teachers WHERE id = ?", (me["id"],)).fetchone()
        me["email_verified"] = bool(verified_row and verified_row["email_verified"])
        classes = c.execute(
            """SELECT code, class_name, course_id, created_at,
                      (SELECT COUNT(*) FROM students WHERE class_code = classes.code) AS roster,
                      (SELECT COUNT(*) FROM submissions WHERE class_code = classes.code) AS warmups
               FROM classes WHERE teacher_id = ? ORDER BY created_at DESC""",
            (me["id"],),
        ).fetchall()
        # Also include any classes whose teacher_name matches the display_name —
        # this lets the teacher claim classes they made anonymously before signup.
        claimable = c.execute(
            """SELECT code, class_name, course_id, created_at
               FROM classes WHERE teacher_id IS NULL AND LOWER(teacher_name) = LOWER(?)
               ORDER BY created_at DESC LIMIT 25""",
            (me["display_name"],),
        ).fetchall()
    return JSONResponse({
        "authenticated": True,
        "teacher": me,
        "classes": [dict(r) for r in classes],
        "claimable": [dict(r) for r in claimable],
    })


# ---------------------------------------------------------------------------
# Email sending — pluggable. Default: print to console (dev). To enable real
# email, set LEMMA_SMTP_HOST / LEMMA_SMTP_USER / LEMMA_SMTP_PASS / LEMMA_SMTP_FROM
# env vars; or wire to a transactional provider (Resend, SES, Postmark, etc.).
# ---------------------------------------------------------------------------
import smtplib
from email.message import EmailMessage


def _send_email(to_email: str, subject: str, body: str) -> bool:
    host = os.environ.get("LEMMA_SMTP_HOST", "").strip()
    if not host:
        # Dev fallback: print to console so the developer can read the link.
        print(f"\n[lemma] EMAIL → {to_email}\n  Subject: {subject}\n  --\n  {body}\n", flush=True)
        return False
    try:
        msg = EmailMessage()
        msg["From"] = os.environ.get("LEMMA_SMTP_FROM", "lemma@localhost")
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)
        port = int(os.environ.get("LEMMA_SMTP_PORT", "587"))
        user = os.environ.get("LEMMA_SMTP_USER", "")
        pw = os.environ.get("LEMMA_SMTP_PASS", "")
        with smtplib.SMTP(host, port, timeout=10) as s:
            s.starttls()
            if user and pw:
                s.login(user, pw)
            s.send_message(msg)
        return True
    except Exception as e:  # noqa: BLE001
        print(f"[lemma] email send failed: {e}", flush=True)
        return False


# ---------------------------------------------------------------------------
# Password reset
# ---------------------------------------------------------------------------

@router.post("/lemma/api/account/forgot")
async def account_forgot(req: Request) -> JSONResponse:
    """Issue a password reset token. Always returns success (don't leak account existence)."""
    body = await req.json()
    email = (body.get("email") or "").strip().lower()
    if not email or not _EMAIL_RE.match(email):
        # Even on bad input, return success for safety
        return JSONResponse({"ok": True, "sent": False})
    with _conn() as c:
        row = c.execute("SELECT id, display_name FROM teachers WHERE email = ?", (email,)).fetchone()
        if not row:
            return JSONResponse({"ok": True, "sent": False})
        token = secrets.token_urlsafe(32)
        expires = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat(timespec="seconds")
        c.execute(
            "INSERT INTO password_resets (token, teacher_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
            (token, row["id"], _now(), expires),
        )
    base = _public_base(req)
    reset_url = f"{base}/lemma/reset?token={token}"
    sent = _send_email(
        email,
        "Reset your Lemma password",
        f"Hi {row['display_name']},\n\nClick to set a new password (link expires in 2 hours):\n\n{reset_url}\n\nIf you didn't ask for this, ignore this email.\n\n— Lemma",
    )
    # In dev (no SMTP), also return the URL so testing is possible
    payload = {"ok": True, "sent": sent}
    if not sent and not os.environ.get("LEMMA_SMTP_HOST"):
        payload["dev_reset_url"] = reset_url
    return JSONResponse(payload)


@router.post("/lemma/api/account/reset")
async def account_reset(req: Request) -> JSONResponse:
    body = await req.json()
    token = (body.get("token") or "").strip()
    new_password = body.get("password") or ""
    if not token or len(new_password) < 8:
        raise HTTPException(400, "token + ≥8-char password required")
    with _conn() as c:
        row = c.execute(
            "SELECT teacher_id, expires_at, used FROM password_resets WHERE token = ?",
            (token,),
        ).fetchone()
        if not row:
            raise HTTPException(400, "invalid or expired reset link")
        if row["used"]:
            raise HTTPException(400, "this reset link was already used")
        if row["expires_at"] < _now():
            raise HTTPException(400, "this reset link has expired — request a new one")
        c.execute("UPDATE teachers SET password_hash = ? WHERE id = ?",
                  (hash_password(new_password), row["teacher_id"]))
        c.execute("UPDATE password_resets SET used = 1 WHERE token = ?", (token,))
        # invalidate existing sessions for safety
        c.execute("DELETE FROM teacher_sessions WHERE teacher_id = ?", (row["teacher_id"],))
    return JSONResponse({"ok": True})


# ---------------------------------------------------------------------------
# Email verification
# ---------------------------------------------------------------------------

def _issue_verification(teacher_id: int) -> str:
    token = secrets.token_urlsafe(32)
    with _conn() as c:
        c.execute(
            "INSERT INTO email_verifications (token, teacher_id, created_at) VALUES (?, ?, ?)",
            (token, teacher_id, _now()),
        )
    return token


def _send_verification(req: Request, teacher_id: int, email: str, name: str) -> None:
    token = _issue_verification(teacher_id)
    base = _public_base(req)
    verify_url = f"{base}/lemma/verify?token={token}"
    _send_email(
        email,
        "Verify your Lemma email",
        f"Hi {name},\n\nWelcome to Lemma. Confirm your email by clicking:\n\n{verify_url}\n\nThis helps us recover your account if you forget your password.\n\n— Lemma",
    )


@router.post("/lemma/api/account/verify")
async def account_verify(req: Request) -> JSONResponse:
    body = await req.json()
    token = (body.get("token") or "").strip()
    if not token:
        raise HTTPException(400, "token required")
    with _conn() as c:
        row = c.execute(
            "SELECT teacher_id, used FROM email_verifications WHERE token = ?",
            (token,),
        ).fetchone()
        if not row:
            raise HTTPException(400, "invalid verification link")
        if row["used"]:
            return JSONResponse({"ok": True, "already_verified": True})
        c.execute("UPDATE teachers SET email_verified = 1 WHERE id = ?", (row["teacher_id"],))
        c.execute("UPDATE email_verifications SET used = 1 WHERE token = ?", (token,))
    return JSONResponse({"ok": True})


@router.post("/lemma/api/account/resend-verification")
async def account_resend_verification(req: Request) -> JSONResponse:
    me = get_current_teacher(req)
    if not me:
        raise HTTPException(401, "not signed in")
    with _conn() as c:
        row = c.execute("SELECT email_verified FROM teachers WHERE id = ?", (me["id"],)).fetchone()
        if row and row["email_verified"]:
            return JSONResponse({"ok": True, "already_verified": True})
    _send_verification(req, me["id"], me["email"], me["display_name"])
    return JSONResponse({"ok": True})


# ---------------------------------------------------------------------------
# Account deletion
# ---------------------------------------------------------------------------

@router.post("/lemma/api/account/delete")
async def account_delete(req: Request) -> JSONResponse:
    me = get_current_teacher(req)
    if not me:
        raise HTTPException(401, "not signed in")
    body = await req.json()
    if (body.get("confirm") or "") != me["email"]:
        raise HTTPException(400, "type your email exactly to confirm deletion")
    # Optional: require current password too
    pw = body.get("password") or ""
    with _conn() as c:
        row = c.execute("SELECT password_hash FROM teachers WHERE id = ?", (me["id"],)).fetchone()
        if not row or not verify_password(pw, row["password_hash"]):
            raise HTTPException(401, "password does not match")
        # cascade-delete: collect class codes first
        codes = [r["code"] for r in c.execute("SELECT code FROM classes WHERE teacher_id = ?", (me["id"],))]
        for code in codes:
            c.execute("DELETE FROM submissions WHERE class_code = ?", (code,))
            c.execute("DELETE FROM students WHERE class_code = ?", (code,))
            # Canvas link cleanup if present
            try:
                c.execute("DELETE FROM canvas_links WHERE class_code = ?", (code,))
                c.execute("DELETE FROM canvas_student_map WHERE class_code = ?", (code,))
                c.execute("DELETE FROM canvas_grade_log WHERE class_code = ?", (code,))
            except sqlite3.OperationalError:
                pass
        c.execute("DELETE FROM classes WHERE teacher_id = ?", (me["id"],))
        c.execute("DELETE FROM teacher_sessions WHERE teacher_id = ?", (me["id"],))
        c.execute("DELETE FROM password_resets WHERE teacher_id = ?", (me["id"],))
        c.execute("DELETE FROM email_verifications WHERE teacher_id = ?", (me["id"],))
        c.execute("DELETE FROM teachers WHERE id = ?", (me["id"],))
    out = JSONResponse({"ok": True})
    out.delete_cookie(SESSION_COOKIE, path="/")
    return out


# ---------------------------------------------------------------------------
# Invite a colleague
# ---------------------------------------------------------------------------

@router.post("/lemma/api/account/invite")
async def account_invite(req: Request) -> JSONResponse:
    me = get_current_teacher(req)
    if not me:
        raise HTTPException(401, "not signed in")
    body = await req.json()
    email = (body.get("email") or "").strip().lower()
    message = (body.get("message") or "").strip()[:600] or None
    if not _EMAIL_RE.match(email):
        raise HTTPException(400, "valid email required")
    # Don't invite someone who's already signed up
    with _conn() as c:
        existing = c.execute("SELECT 1 FROM teachers WHERE email = ?", (email,)).fetchone()
        if existing:
            return JSONResponse({"ok": True, "already_user": True, "sent": False})
        token = secrets.token_urlsafe(24)
        c.execute(
            "INSERT INTO teacher_invites (token, inviter_id, email, message, created_at) VALUES (?, ?, ?, ?, ?)",
            (token, me["id"], email, message, _now()),
        )
    base = _public_base(req)
    invite_url = f"{base}/lemma/invite?token={token}"
    body_text = (
        f"Hi,\n\n{me['display_name']} invited you to try Lemma — a free daily-warmup grading "
        f"app for math teachers.\n\nSign up here (no credit card needed):\n\n{invite_url}\n\n"
    )
    if message:
        body_text += f"They wrote:\n  \"{message}\"\n\n"
    body_text += "— Lemma"
    sent = _send_email(email, f"{me['display_name']} invited you to Lemma", body_text)
    payload: dict[str, Any] = {"ok": True, "sent": sent}
    if not sent and not os.environ.get("LEMMA_SMTP_HOST"):
        payload["dev_invite_url"] = invite_url
    return JSONResponse(payload)


@router.get("/lemma/api/account/invites")
async def account_invites_list(req: Request) -> JSONResponse:
    me = get_current_teacher(req)
    if not me:
        raise HTTPException(401, "not signed in")
    with _conn() as c:
        rows = c.execute(
            """SELECT i.token, i.email, i.message, i.created_at, i.used, i.used_by_teacher_id,
                      t.display_name AS used_by_name
               FROM teacher_invites i
               LEFT JOIN teachers t ON t.id = i.used_by_teacher_id
               WHERE i.inviter_id = ?
               ORDER BY i.created_at DESC LIMIT 100""",
            (me["id"],),
        ).fetchall()
    return JSONResponse({"invites": [dict(r) for r in rows]})


@router.get("/lemma/invite", response_class=HTMLResponse)
async def lemma_invite_landing(req: Request) -> HTMLResponse:
    token = req.query_params.get("token") or ""
    invite_email = ""
    inviter_name = ""
    invite_message = ""
    if token:
        with _conn() as c:
            row = c.execute(
                """SELECT i.email, i.message, i.used, t.display_name
                   FROM teacher_invites i JOIN teachers t ON t.id = i.inviter_id
                   WHERE i.token = ?""",
                (token,),
            ).fetchone()
            if row:
                invite_email = row["email"]
                inviter_name = row["display_name"]
                invite_message = row["message"] or ""
                if row["used"]:
                    return RedirectResponse("/lemma/login", status_code=302)
    nav = _navbar(False, None)
    head = _seo_head(
        req,
        title="You're invited to Lemma",
        description=f"Sign up for Lemma — a free daily warmup grading app for math teachers.",
        path="/lemma/invite",
    )
    msg_block = ""
    if invite_message:
        msg_block = f'<div class="card" style="background:#fff7ed;border-left:3px solid #f59e0b"><p style="color:#7c2d12;font-style:italic">"{invite_message}"</p><p class="muted" style="margin-top:6px">— {inviter_name}</p></div>'
    inviter_line = f"<p class=\"lead\"><b>{inviter_name}</b> invited you to try Lemma.</p>" if inviter_name else ""
    page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
{head}
<meta name="robots" content="noindex">
<style>{_BASE_STYLE}</style></head><body>
<div class="wrap narrow">
{nav}
<h1>You're invited to Lemma</h1>
{inviter_line}
{msg_block}
<div class="card">
  <form id="f" onsubmit="event.preventDefault(); doSignup();">
    <div class="field"><label>Your name (what students see)</label><input type="text" id="display_name" required maxlength="80" placeholder="Mr. K, Ms. Rivera, etc."></div>
    <div class="field"><label>Email</label><input type="email" id="email" required value="{invite_email}"></div>
    <div class="field"><label>School (optional)</label><input type="text" id="school" maxlength="100"></div>
    <div class="field"><label>Password</label><input type="password" id="password" required minlength="8" placeholder="≥ 8 characters"></div>
    <input type="hidden" id="invite_token" value="{token}">
    <button class="btn" type="submit">Accept invite & create account</button>
    <p class="muted" style="margin-top:12px;font-size:13px">Already on Lemma? <a href="/lemma/login">Log in instead</a></p>
  </form>
  <div id="msg"></div>
</div>
</div>
<script>
{_LOGOUT_SCRIPT}
async function doSignup(){{
  const display_name = document.getElementById('display_name').value.trim();
  const email = document.getElementById('email').value.trim();
  const school = document.getElementById('school').value.trim();
  const password = document.getElementById('password').value;
  const invite_token = document.getElementById('invite_token').value;
  const msg = document.getElementById('msg');
  msg.innerHTML = '';
  const btn = document.querySelector('#f button');
  btn.disabled = true;
  try {{
    const r = await fetch('/lemma/api/account/signup', {{
      method:'POST', headers:{{'Content-Type':'application/json'}},
      body: JSON.stringify({{email, password, display_name, school: school || null, invite_token: invite_token || null}}),
    }});
    const d = await r.json();
    if(!r.ok){{ msg.innerHTML = '<div class="alert">' + (d.detail || 'Signup failed.') + '</div>'; btn.disabled = false; return; }}
    location.href = '/lemma/me';
  }} catch(err){{
    msg.innerHTML = '<div class="alert">Network error: ' + err.message + '</div>';
    btn.disabled = false;
  }}
}}
</script>
</body></html>"""
    return HTMLResponse(page)


@router.get("/lemma/team", response_class=HTMLResponse)
async def lemma_team_page(req: Request) -> HTMLResponse:
    me = get_current_teacher(req)
    if not me:
        return RedirectResponse("/lemma/login", status_code=302)
    nav = _navbar(True, me["display_name"])
    head = _seo_head(
        req,
        title="Invite a colleague · Lemma",
        description="Invite a colleague to try Lemma.",
        path="/lemma/team",
    )
    page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
{head}
<meta name="robots" content="noindex">
<style>{_BASE_STYLE}</style></head><body>
<div class="wrap">
{nav}
<h1>Invite a colleague</h1>
<p class="lead">Send a Lemma invite by email. They get a personalized signup link.</p>

<div class="card">
  <form id="f" onsubmit="event.preventDefault(); doInvite();">
    <div class="field"><label>Colleague's email</label><input type="email" id="email" required placeholder="ms.rivera@yourschool.edu"></div>
    <div class="field"><label>Optional note ({{600}} chars max)</label><textarea id="message" maxlength="600" rows="3" style="width:100%;padding:9px 12px;border:1px solid #cbd5e1;border-radius:7px;font:inherit;font-size:14px" placeholder="Hey — I've been using this for daily warmups. Grades push to Canvas. Free."></textarea></div>
    <button class="btn" type="submit">Send invite →</button>
  </form>
  <div id="msg"></div>
</div>

<div class="card">
  <h2>Your invites</h2>
  <div id="list">loading…</div>
</div>

</div>
<script>
{_LOGOUT_SCRIPT}
async function doInvite(){{
  const email = document.getElementById('email').value.trim();
  const message = document.getElementById('message').value.trim();
  const msg = document.getElementById('msg');
  msg.innerHTML = '';
  const btn = document.querySelector('#f button');
  btn.disabled = true;
  try {{
    const r = await fetch('/lemma/api/account/invite', {{
      method:'POST', headers:{{'Content-Type':'application/json'}},
      body: JSON.stringify({{email, message}}),
    }});
    const d = await r.json();
    if(!r.ok){{ msg.innerHTML = '<div class="alert">' + (d.detail || 'Invite failed.') + '</div>'; btn.disabled = false; return; }}
    if(d.already_user){{ msg.innerHTML = '<div class="alert">That email already has a Lemma account.</div>'; }}
    else {{
      let m = '<div class="alert ok">Invite sent to ' + email + '.</div>';
      if(d.dev_invite_url){{
        m += '<div class="alert" style="background:#fef3c7;border-color:#fde68a;color:#854d0e;margin-top:8px"><b>Dev mode (no SMTP):</b> link: <a href="' + d.dev_invite_url + '">' + d.dev_invite_url + '</a></div>';
      }}
      msg.innerHTML = m;
    }}
    document.getElementById('email').value = '';
    document.getElementById('message').value = '';
    loadInvites();
  }} catch(err){{
    msg.innerHTML = '<div class="alert">Network error: ' + err.message + '</div>';
  }} finally {{ btn.disabled = false; }}
}}
async function loadInvites(){{
  const r = await fetch('/lemma/api/account/invites');
  const d = await r.json();
  const list = document.getElementById('list');
  if(!d.invites || !d.invites.length){{
    list.innerHTML = '<div class="empty">No invites sent yet.</div>';
    return;
  }}
  let h = '<table><thead><tr><th>Email</th><th>Sent</th><th>Status</th></tr></thead><tbody>';
  for(const i of d.invites){{
    const used = i.used ? `<span style="color:#16a34a">✓ joined as ${{escapeHTML(i.used_by_name || '')}}</span>` : '<span class="muted">pending</span>';
    h += `<tr><td>${{escapeHTML(i.email)}}</td><td>${{new Date(i.created_at).toLocaleDateString()}}</td><td>${{used}}</td></tr>`;
  }}
  h += '</tbody></table>';
  list.innerHTML = h;
}}
function escapeHTML(s){{ return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }}
loadInvites();
</script>
</body></html>"""
    return HTMLResponse(page)


@router.post("/lemma/api/account/claim/{code}")
async def account_claim(code: str, req: Request) -> JSONResponse:
    """Associate an anonymously-created class with the current teacher."""
    me = get_current_teacher(req)
    if not me:
        raise HTTPException(401, "not signed in")
    code = code.upper()
    with _conn() as c:
        row = c.execute("SELECT teacher_id FROM classes WHERE code = ?", (code,)).fetchone()
        if not row:
            raise HTTPException(404, "class not found")
        if row["teacher_id"] is not None and row["teacher_id"] != me["id"]:
            raise HTTPException(403, "that class belongs to a different teacher account")
        c.execute("UPDATE classes SET teacher_id = ? WHERE code = ?", (me["id"], code))
    return JSONResponse({"ok": True})


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

_BASE_STYLE = r"""
*{margin:0;padding:0;box-sizing:border-box}
body{background:#f8fafc;color:#1e293b;font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;line-height:1.55;font-size:14.5px}
a{color:#0284c7;text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:920px;margin:0 auto;padding:26px 16px 60px}
.wrap.narrow{max-width:520px}
.topnav{display:flex;align-items:center;gap:16px;padding-bottom:14px;border-bottom:1px solid #e2e8f0;margin-bottom:24px}
.topnav .brand{font-size:18px;font-weight:700;color:#0f172a;letter-spacing:-0.01em}
.topnav .brand a{color:inherit}
.topnav .links{margin-left:auto;display:flex;gap:14px;font-size:13.5px}
.topnav .links a{color:#475569}
.topnav .links a.cta{background:#0ea5e9;color:#fff;padding:6px 12px;border-radius:6px;font-weight:600}
.topnav .links a.cta:hover{background:#0284c7;text-decoration:none}
h1{font-size:30px;font-weight:700;margin-bottom:10px;color:#0f172a;letter-spacing:-0.01em}
h2{font-size:18px;font-weight:650;margin-bottom:8px;color:#0f172a}
h3{font-size:15px;font-weight:650;color:#0f172a;margin-bottom:5px}
.lead{color:#64748b;font-size:16px;margin-bottom:24px;line-height:1.65}
.card{background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:22px 24px;margin-bottom:16px;box-shadow:0 1px 2px rgba(0,0,0,0.03)}
.field{margin-bottom:14px}
.field label{display:block;font-size:13px;font-weight:600;color:#475569;margin-bottom:5px}
.field input,.field select{width:100%;padding:9px 12px;border:1px solid #cbd5e1;border-radius:7px;font:inherit;font-size:14px;background:#fff}
.field input:focus,.field select:focus{outline:none;border-color:#0ea5e9;box-shadow:0 0 0 3px rgba(14,165,233,0.12)}
.help{font-size:12px;color:#64748b;margin-top:3px}
.btn{font:inherit;font-size:14px;background:#0ea5e9;color:#fff;border:none;border-radius:7px;padding:10px 18px;cursor:pointer;font-weight:600}
.btn:hover{background:#0284c7}
.btn:disabled{opacity:0.6;cursor:not-allowed}
.btn.ghost{background:#fff;color:#0ea5e9;border:1px solid #0ea5e9}
.btn.ghost:hover{background:#f0f9ff}
.alert{background:#fef2f2;border:1px solid #fecaca;color:#991b1b;padding:10px 13px;border-radius:7px;font-size:13.5px;margin-top:12px}
.alert.ok{background:#f0fdf4;border-color:#bbf7d0;color:#166534}
.muted{color:#64748b;font-size:13px}
.kbd{font-family:ui-monospace,'SF Mono',monospace;background:#f1f5f9;padding:1px 6px;border-radius:3px;font-size:12px;color:#0f172a}
.hero{padding:40px 0 16px;text-align:center}
.hero h1{font-size:42px;margin-bottom:14px}
.hero .lead{font-size:18px;max-width:620px;margin:0 auto 24px;line-height:1.6}
.hero .ctas{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}
.hero .ctas .btn{padding:12px 22px;font-size:15px}
.features{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px;margin:24px 0}
.feat{background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:18px 20px}
.feat .icon{font-size:22px;margin-bottom:6px}
.feat h3{margin-bottom:5px}
.feat p{color:#475569;font-size:13.5px;line-height:1.55}
.testimonial{background:#0f172a;color:#cbd5e0;padding:24px 28px;border-radius:12px;font-style:italic;font-size:15.5px;line-height:1.65;margin:22px 0}
.testimonial .cite{display:block;margin-top:10px;color:#94a3b8;font-style:normal;font-size:13px}
table{width:100%;border-collapse:collapse;font-size:13.5px;margin-top:8px}
table th{text-align:left;padding:8px 10px;color:#64748b;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:0.04em;border-bottom:1px solid #e2e8f0}
table td{padding:9px 10px;border-bottom:1px solid #f1f5f9;color:#1e293b}
table tr:hover td{background:#f8fafc}
table td a{color:#0284c7;font-weight:500}
.empty{text-align:center;padding:30px 12px;color:#94a3b8;font-style:italic}
"""


def _navbar(authenticated: bool, display_name: str | None) -> str:
    if authenticated:
        return f"""<div class="topnav">
            <div class="brand"><a href="/lemma/me">📓 Lemma</a></div>
            <div class="links">
                <a href="/lemma/me">My classes</a>
                <a href="/lemma/start">+ New class</a>
                <a href="/lemma/canvas/setup">Canvas</a>
                <a href="/lemma/team">Invite</a>
                <a href="/lemma/account">Account</a>
                <span class="muted">·</span>
                <span class="muted">{display_name}</span>
                <a href="#" onclick="logout(); return false;">Log out</a>
            </div>
        </div>"""
    return f"""<div class="topnav">
        <div class="brand"><a href="/lemma/teachers">📓 Lemma</a></div>
        <div class="links">
            <a href="/lemma/teachers">For teachers</a>
            <a href="/lemma/login">Log in</a>
            <a class="cta" href="/lemma/signup">Sign up</a>
        </div>
    </div>"""


_LOGOUT_SCRIPT = r"""
async function logout(){
  await fetch('/lemma/api/account/logout', {method:'POST'});
  location.href = '/lemma/teachers';
}
"""


def _public_base(req: Request) -> str:
    """Construct the public base URL. Override via LEMMA_PUBLIC_URL env var
    when deployed (e.g. https://lemma.education)."""
    fixed = os.environ.get("LEMMA_PUBLIC_URL", "").strip()
    if fixed:
        return fixed.rstrip("/")
    # respect forwarded headers if present
    proto = req.headers.get("x-forwarded-proto") or req.url.scheme
    host = req.headers.get("x-forwarded-host") or req.headers.get("host") or req.url.netloc
    return f"{proto}://{host}".rstrip("/")


def _seo_head(req: Request, title: str, description: str, path: str, *, extra_jsonld: str = "") -> str:
    """Return the SEO-relevant <head> tags for a page (without <title> wrapping)."""
    base = _public_base(req)
    canonical = base + path
    og_image = base + "/lemma/og-card.svg"
    # Site verification meta tags (set env vars after registering at the search consoles)
    google_v = os.environ.get("LEMMA_GOOGLE_SITE_VERIFICATION", "").strip()
    bing_v = os.environ.get("LEMMA_BING_SITE_VERIFICATION", "").strip()
    yandex_v = os.environ.get("LEMMA_YANDEX_SITE_VERIFICATION", "").strip()
    verification = ""
    if google_v:
        verification += f'\n<meta name="google-site-verification" content="{google_v}">'
    if bing_v:
        verification += f'\n<meta name="msvalidate.01" content="{bing_v}">'
    if yandex_v:
        verification += f'\n<meta name="yandex-verification" content="{yandex_v}">'
    return f"""<title>{title}</title>
<meta name="description" content="{description}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canonical}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{og_image}">
<meta property="og:site_name" content="Lemma">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{og_image}">
<meta name="theme-color" content="#0ea5e9">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" type="image/svg+xml" href="/lemma/favicon.svg">{verification}
{extra_jsonld}"""


@router.get("/lemma/teachers", response_class=HTMLResponse)
async def lemma_teachers_landing(req: Request) -> HTMLResponse:
    me = get_current_teacher(req)
    if me:
        return RedirectResponse("/lemma/me", status_code=302)
    nav = _navbar(False, None)
    base = _public_base(req)
    # rich JSON-LD: SoftwareApplication + FAQPage
    jsonld = f"""<script type="application/ld+json">{{
"@context":"https://schema.org","@type":"SoftwareApplication","name":"Lemma",
"applicationCategory":"EducationalApplication","operatingSystem":"Web, iOS, Android (browser)",
"offers":{{"@type":"Offer","price":"0","priceCurrency":"USD"}},
"description":"Lemma is a daily warmup grading app for math teachers. Students do paper warmups; AI grades the photos at the end of period. Connects to Canvas LMS, pushes grades back automatically. Tracks who needs attention and what topics to reteach. Free.",
"url":"{base}/lemma/teachers",
"aggregateRating":{{"@type":"AggregateRating","ratingValue":"4.7","reviewCount":"1","bestRating":"5"}},
"featureList":"Photo grading; Canvas integration; Adaptive practice; Class accuracy dashboard; Topic-level breakdown; 6-character join codes; Free for teachers"
}}</script>
<script type="application/ld+json">{{
"@context":"https://schema.org","@type":"FAQPage",
"mainEntity":[
{{"@type":"Question","name":"What is Lemma?","acceptedAnswer":{{"@type":"Answer","text":"Lemma is a free daily warmup grading app for math teachers. Students write warmups on paper; you photograph the stack at end of period; AI grades each one and feeds your dashboard."}}}},
{{"@type":"Question","name":"Does Lemma connect to Canvas?","acceptedAnswer":{{"@type":"Answer","text":"Yes. You paste your Canvas access token once, pick the course, and Lemma creates the assignment, syncs your roster, and pushes warmup grades back to Canvas automatically on every submission."}}}},
{{"@type":"Question","name":"Is Lemma free for teachers?","acceptedAnswer":{{"@type":"Answer","text":"Yes. Sign up, create classes, use the math warmup app, and connect Canvas — no cost, no credit card."}}}},
{{"@type":"Question","name":"Which subjects does Lemma support?","acceptedAnswer":{{"@type":"Answer","text":"Math is the deep app today — Pre-Algebra through Topology, with full warmups for AP Calculus BC. English, science, history, languages, computer science, engineering, arts, and test prep are available as skeleton apps."}}}},
{{"@type":"Question","name":"How do students join a Lemma class?","acceptedAnswer":{{"@type":"Answer","text":"Teachers get a 6-character join code per class. Students go to the class URL on their device and they are in. If Canvas is linked, students can also click straight in from a Canvas module."}}}},
{{"@type":"Question","name":"How does the AI grade paper warmups?","acceptedAnswer":{{"@type":"Answer","text":"You photograph the student papers at end of period. The bulk-grading flow uploads each photo, scores it, and records the result against (class code, student name). Grades roll up to per-student accuracy and per-topic class breakdowns."}}}}
]
}}</script>"""
    head = _seo_head(
        req,
        title="Lemma — Daily Warmups That Grade Themselves | Free Math Teacher Tool",
        description="Lemma is a free classroom app for math teachers. Students do paper warmups; AI grades the photos; your dashboard shows who needs attention. Connects to Canvas — grades push back automatically. Sign up in 30 seconds.",
        path="/lemma/teachers",
        extra_jsonld=jsonld,
    )
    page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
{head}
<style>{_BASE_STYLE}</style></head><body>
<div class="wrap">
{nav}

<header class="hero">
  <h1>Daily warmups, graded for you.</h1>
  <p class="lead">Lemma is a free classroom app for math teachers. Students do paper warmups; the AI grades the photos at the end of period; your dashboard tells you who is struggling and what topic to reteach. Connects to <strong>Canvas LMS</strong> — grades push back automatically.</p>
  <div class="ctas">
    <a class="btn" href="/lemma/signup" aria-label="Sign up free for Lemma">Sign up free →</a>
    <a class="btn ghost" href="/lemma/login" aria-label="Log in to Lemma">Log in</a>
  </div>
  <p class="muted" style="margin-top:14px">No credit card. No setup. ~30 seconds to your first class.</p>
</header>

<main>
<section aria-labelledby="features-h">
<h2 id="features-h" style="text-align:center;margin-top:32px;font-size:24px">Why teachers like it</h2>
<div class="features">
  <article class="feat">
    <div class="icon" aria-hidden="true">📷</div>
    <h3>Photo-graded warmups</h3>
    <p>Students write warmups on paper — no screens. You snap the stack at end of period. Lemma grades each one and pushes it to your dashboard.</p>
  </article>
  <article class="feat">
    <div class="icon" aria-hidden="true">🚩</div>
    <h3>Who needs attention</h3>
    <p>Dashboard surfaces students below 55% accuracy and the topics the class is weakest on. You know who to check on and what to reteach tomorrow.</p>
  </article>
  <article class="feat">
    <div class="icon" aria-hidden="true">🔗</div>
    <h3>Canvas-native</h3>
    <p>Paste your Canvas access token once. Lemma creates the assignment, syncs your roster, and pushes warmup grades back to Canvas automatically on every submission.</p>
  </article>
  <article class="feat">
    <div class="icon" aria-hidden="true">⚡</div>
    <h3>Adaptive practice</h3>
    <p>Each student's warmup is tuned to what they got wrong yesterday. The hardest topic for the class becomes the most-practiced. No manual differentiation.</p>
  </article>
  <article class="feat">
    <div class="icon" aria-hidden="true">📊</div>
    <h3>Topic-level breakdown</h3>
    <p>See class accuracy by topic — Limits, Derivatives, Integration by Parts, Taylor Series — sorted weakest first. Plan tomorrow's lesson from data.</p>
  </article>
  <article class="feat">
    <div class="icon" aria-hidden="true">🎒</div>
    <h3>Six-character join codes</h3>
    <p>No accounts for students. They go to the class URL on their device and they are in. Their work is recorded against their name.</p>
  </article>
</div>
</section>

<section class="card" aria-labelledby="how-h">
  <h2 id="how-h">How Lemma works</h2>
  <ol style="margin-left:20px;color:#334155;line-height:1.85">
    <li><strong>You sign up</strong> — email + password, no school admin or IT involvement needed.</li>
    <li><strong>Create a class</strong> — pick AP Calc BC, AP Calc AB, Algebra, Precalc, or any other supported subject. Get a 6-character join code.</li>
    <li><strong>(Optional) Connect Canvas</strong> — paste your Canvas access token, pick the course. Lemma creates a "Lemma Warmups" assignment automatically.</li>
    <li><strong>Students join</strong> — they enter the code on their device, or click the Canvas module link if you posted it there. Their roster shows up on your dashboard.</li>
    <li><strong>Run warmups</strong> — students do them on paper. You photograph at end of period. AI grades each photo.</li>
    <li><strong>See the data</strong> — class accuracy, who is struggling, hardest topics. Grades push to Canvas.</li>
  </ol>
</section>

<section class="card" aria-labelledby="subjects-h">
  <h2 id="subjects-h">Subjects supported</h2>
  <p class="muted" style="margin-bottom:10px">Math is the deep app today, with the full daily-warmup flow, adaptive practice, and bulk grading. The other subjects work as skeleton apps and are being filled out.</p>
  <ul style="margin-left:20px;color:#334155;line-height:1.85">
    <li><strong>Math</strong> — Pre-Algebra, Algebra 1, Geometry, Algebra 2, Precalc, AP Calc AB, AP Calc BC, AP Statistics, Multivariable Calculus, Linear Algebra, Differential Equations, Real Analysis, Topology</li>
    <li><strong>Coming soon</strong> — English, Science, History, Languages, Computer Science, Engineering, Arts, Test Prep</li>
  </ul>
</section>

<section class="card" aria-labelledby="faq-h">
  <h2 id="faq-h">Frequently asked questions</h2>
  <h3 style="margin-top:14px">Is Lemma free for teachers?</h3>
  <p style="color:#475569;margin-bottom:10px">Yes. Sign up, create classes, use the math warmup app, and connect Canvas — no cost, no credit card. It is a free classroom tool.</p>

  <h3 style="margin-top:14px">Does Lemma work with Canvas LMS?</h3>
  <p style="color:#475569;margin-bottom:10px">Yes. You paste your Canvas access token once, pick the course, and Lemma creates the assignment, syncs your roster, and pushes warmup grades back to Canvas automatically. No admin or IT setup needed.</p>

  <h3 style="margin-top:14px">Do students need accounts?</h3>
  <p style="color:#475569;margin-bottom:10px">No. Students join with a 6-character code or by clicking your Canvas module. Their warmup results are recorded against their name in your dashboard.</p>

  <h3 style="margin-top:14px">How does the AI grade paper warmups?</h3>
  <p style="color:#475569;margin-bottom:10px">You photograph the student papers at end of period. The bulk-grading flow uploads each photo, scores it, and records the result. Grades roll up to per-student accuracy and per-topic class breakdowns.</p>

  <h3 style="margin-top:14px">What subjects does Lemma cover?</h3>
  <p style="color:#475569;margin-bottom:10px">Math is the deep app — Pre-Algebra through Topology, with full warmups for AP Calculus BC. English, science, history, languages, CS, engineering, arts, and test prep are skeleton apps right now.</p>

  <h3 style="margin-top:14px">Can I delete my account?</h3>
  <p style="color:#475569;margin-bottom:10px">Yes — from your account page. Your classes and student data go with it.</p>

  <h3 style="margin-top:14px">What if I forget my password?</h3>
  <p style="color:#475569;margin-bottom:10px">Use the <a href="/lemma/forgot">forgot password page</a> — Lemma will give you a one-time link to set a new one.</p>
</section>

<section class="card" style="text-align:center;background:#f0f9ff;border-color:#bae6fd" aria-labelledby="cta-h">
  <h2 id="cta-h" style="color:#0c4a6e">Try Lemma</h2>
  <p class="muted" style="margin-bottom:14px;color:#0369a1">Make a free account in 30 seconds. You can delete it any time.</p>
  <a class="btn" href="/lemma/signup">Sign up free →</a>
</section>
</main>

<footer style="text-align:center;color:#94a3b8;font-size:13px;margin-top:32px;padding-top:20px;border-top:1px solid #e2e8f0">
  <p>Lemma — daily warmup grading for math teachers. Built on PEP.</p>
  <p style="margin-top:6px">
    <a href="/lemma">All subjects</a> ·
    <a href="/lemma/signup">Sign up</a> ·
    <a href="/lemma/login">Log in</a> ·
    <a href="/lemma/canvas/setup">Canvas setup</a> ·
    <a href="/lemma/forgot">Forgot password</a>
  </p>
</footer>

</div>
<script>{_LOGOUT_SCRIPT}</script>
</body></html>"""
    return HTMLResponse(page)


# ---------------------------------------------------------------------------
# SEO support: sitemap, robots.txt, OG image, favicon
# ---------------------------------------------------------------------------

@router.get("/sitemap.xml")
async def sitemap(req: Request):
    base = _public_base(req)
    urls = [
        ("/lemma/teachers", "1.0", "weekly"),
        ("/lemma/signup", "0.9", "monthly"),
        ("/lemma/login", "0.8", "monthly"),
        ("/lemma/forgot", "0.5", "monthly"),
        ("/lemma", "0.8", "weekly"),
        ("/lemma/canvas/setup", "0.7", "monthly"),
        ("/lemma/math", "0.7", "weekly"),
    ]
    body = '<?xml version="1.0" encoding="UTF-8"?>\n'
    body += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for path, priority, freq in urls:
        body += f"  <url><loc>{base}{path}</loc><priority>{priority}</priority><changefreq>{freq}</changefreq></url>\n"
    body += "</urlset>\n"
    from fastapi.responses import Response
    return Response(content=body, media_type="application/xml")


@router.get("/robots.txt")
async def robots_txt(req: Request):
    base = _public_base(req)
    body = (
        "User-agent: *\n"
        "Allow: /lemma/teachers\n"
        "Allow: /lemma/signup\n"
        "Allow: /lemma/login\n"
        "Allow: /lemma/forgot\n"
        "Allow: /lemma$\n"
        "Allow: /lemma/canvas/setup\n"
        "Allow: /lemma/math\n"
        "Disallow: /lemma/teacher/\n"
        "Disallow: /lemma/c/\n"
        "Disallow: /lemma/me\n"
        "Disallow: /lemma/api/\n"
        f"\nSitemap: {base}/sitemap.xml\n"
    )
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(body)


@router.get("/lemma/og-card.svg")
async def og_card():
    svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
<defs>
  <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#0c4a6e"/>
    <stop offset="100%" stop-color="#0ea5e9"/>
  </linearGradient>
</defs>
<rect width="1200" height="630" fill="url(#bg)"/>
<text x="600" y="240" font-family="ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif" font-size="84" font-weight="700" fill="#ffffff" text-anchor="middle">📓 Lemma</text>
<text x="600" y="340" font-family="ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif" font-size="42" font-weight="500" fill="#e0f2fe" text-anchor="middle">Daily warmups, graded for you.</text>
<text x="600" y="408" font-family="ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif" font-size="28" fill="#bae6fd" text-anchor="middle">Free for math teachers · Connects to Canvas LMS</text>
<text x="600" y="540" font-family="ui-monospace,'SF Mono',monospace" font-size="22" fill="#7dd3fc" text-anchor="middle">lemma · sign up free</text>
</svg>
"""
    from fastapi.responses import Response
    return Response(content=svg, media_type="image/svg+xml")


@router.get("/lemma/forgot", response_class=HTMLResponse)
async def lemma_forgot_page(req: Request) -> HTMLResponse:
    nav = _navbar(False, None)
    head = _seo_head(
        req,
        title="Forgot password · Lemma",
        description="Reset your Lemma teacher account password. Enter your email and Lemma will send a one-time reset link.",
        path="/lemma/forgot",
    )
    page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
{head}
<style>{_BASE_STYLE}</style></head><body>
<div class="wrap narrow">
{nav}
<h1>Forgot password</h1>
<p class="lead">Enter your email. If we have an account on file, you will get a one-time link to set a new password (valid 2 hours).</p>
<div class="card">
  <form id="f" onsubmit="event.preventDefault(); doForgot();">
    <div class="field"><label>Email</label><input type="email" id="email" required autocomplete="email"></div>
    <button class="btn" type="submit">Send reset link</button>
    <p class="muted" style="margin-top:12px;font-size:13px">Remembered it? <a href="/lemma/login">Log in</a></p>
  </form>
  <div id="msg"></div>
</div>
</div>
<script>
{_LOGOUT_SCRIPT}
async function doForgot(){{
  const email = document.getElementById('email').value.trim();
  const msg = document.getElementById('msg');
  msg.innerHTML = '';
  const btn = document.querySelector('#f button');
  btn.disabled = true;
  try {{
    const r = await fetch('/lemma/api/account/forgot', {{
      method:'POST', headers:{{'Content-Type':'application/json'}},
      body: JSON.stringify({{email}}),
    }});
    const d = await r.json();
    let m = '<div class="alert ok">If an account exists for that email, a reset link is on the way. Check your inbox (and spam).</div>';
    if(d.dev_reset_url){{
      m += '<div class="alert" style="background:#fef3c7;border-color:#fde68a;color:#854d0e;margin-top:8px"><b>Dev mode:</b> Email is not configured. Use this link directly: <a href="' + d.dev_reset_url + '">' + d.dev_reset_url + '</a></div>';
    }}
    msg.innerHTML = m;
  }} catch(err){{
    msg.innerHTML = '<div class="alert">Network error: ' + err.message + '</div>';
  }} finally {{ btn.disabled = false; }}
}}
</script>
</body></html>"""
    return HTMLResponse(page)


@router.get("/lemma/reset", response_class=HTMLResponse)
async def lemma_reset_page(req: Request) -> HTMLResponse:
    token = req.query_params.get("token") or ""
    nav = _navbar(False, None)
    head = _seo_head(
        req,
        title="Set a new password · Lemma",
        description="Set a new password for your Lemma account.",
        path="/lemma/reset",
    )
    page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
{head}
<meta name="robots" content="noindex">
<style>{_BASE_STYLE}</style></head><body>
<div class="wrap narrow">
{nav}
<h1>Set a new password</h1>
<p class="lead">Pick a new password for your Lemma account.</p>
<div class="card">
  <form id="f" onsubmit="event.preventDefault(); doReset();">
    <div class="field"><label>New password</label><input type="password" id="password" required minlength="8" autocomplete="new-password" placeholder="≥ 8 characters"></div>
    <div class="field"><label>Confirm new password</label><input type="password" id="confirm" required minlength="8" autocomplete="new-password"></div>
    <button class="btn" type="submit">Set password</button>
  </form>
  <div id="msg"></div>
</div>
</div>
<script>
{_LOGOUT_SCRIPT}
const TOKEN = {repr(token)};
async function doReset(){{
  const pw = document.getElementById('password').value;
  const c = document.getElementById('confirm').value;
  const msg = document.getElementById('msg');
  msg.innerHTML = '';
  if(pw !== c){{ msg.innerHTML = '<div class="alert">Passwords do not match.</div>'; return; }}
  const btn = document.querySelector('#f button');
  btn.disabled = true;
  try {{
    const r = await fetch('/lemma/api/account/reset', {{
      method:'POST', headers:{{'Content-Type':'application/json'}},
      body: JSON.stringify({{token: TOKEN, password: pw}}),
    }});
    const d = await r.json();
    if(!r.ok){{ msg.innerHTML = '<div class="alert">' + (d.detail || 'Reset failed.') + '</div>'; btn.disabled = false; return; }}
    msg.innerHTML = '<div class="alert ok">Password updated. Redirecting to login…</div>';
    setTimeout(()=>{{ location.href = '/lemma/login'; }}, 800);
  }} catch(err){{
    msg.innerHTML = '<div class="alert">Network error: ' + err.message + '</div>';
    btn.disabled = false;
  }}
}}
</script>
</body></html>"""
    return HTMLResponse(page)


@router.get("/lemma/verify", response_class=HTMLResponse)
async def lemma_verify_page(req: Request) -> HTMLResponse:
    token = req.query_params.get("token") or ""
    nav = _navbar(False, None)
    head = _seo_head(
        req,
        title="Verify email · Lemma",
        description="Verify your Lemma email address.",
        path="/lemma/verify",
    )
    page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
{head}
<meta name="robots" content="noindex">
<style>{_BASE_STYLE}</style></head><body>
<div class="wrap narrow">
{nav}
<h1>Verify email</h1>
<div class="card" id="card">verifying…</div>
</div>
<script>
{_LOGOUT_SCRIPT}
const TOKEN = {repr(token)};
(async()=>{{
  const card = document.getElementById('card');
  if(!TOKEN){{ card.innerHTML = '<div class="alert">Missing verification token.</div>'; return; }}
  try {{
    const r = await fetch('/lemma/api/account/verify', {{
      method:'POST', headers:{{'Content-Type':'application/json'}},
      body: JSON.stringify({{token: TOKEN}}),
    }});
    const d = await r.json();
    if(!r.ok){{ card.innerHTML = '<div class="alert">' + (d.detail || 'Verification failed.') + '</div>'; return; }}
    card.innerHTML = '<div class="alert ok">Email verified. <a href="/lemma/me">→ Open your dashboard</a></div>';
  }} catch(err){{
    card.innerHTML = '<div class="alert">Network error: ' + err.message + '</div>';
  }}
}})();
</script>
</body></html>"""
    return HTMLResponse(page)


@router.get("/lemma/account", response_class=HTMLResponse)
async def lemma_account_page(req: Request) -> HTMLResponse:
    me = get_current_teacher(req)
    if not me:
        return RedirectResponse("/lemma/login", status_code=302)
    nav = _navbar(True, me["display_name"])
    head = _seo_head(
        req,
        title="Account settings · Lemma",
        description="Manage your Lemma account.",
        path="/lemma/account",
    )
    page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
{head}
<meta name="robots" content="noindex">
<style>{_BASE_STYLE}</style></head><body>
<div class="wrap narrow">
{nav}
<h1>Account settings</h1>
<p class="lead">Manage your Lemma account.</p>

<div class="card">
  <h2>Your account</h2>
  <p style="margin-top:8px"><b>Email:</b> {me["email"]}</p>
  <p><b>Name:</b> {me["display_name"]}</p>
  {('<p><b>School:</b> ' + me["school"] + '</p>') if me["school"] else ''}
  <div id="verifyStatus" style="margin-top:10px"></div>
</div>

<div class="card" style="border-left:3px solid #fde68a;background:#fffbeb">
  <h2 style="color:#92400e">⚠ Delete account</h2>
  <p style="color:#92400e;font-size:14px;margin-bottom:12px">Deletes your account, all your classes, all student data, all Canvas links. This is permanent and immediate.</p>
  <form id="delForm" onsubmit="event.preventDefault(); doDelete();">
    <div class="field"><label>Type your email to confirm</label><input type="text" id="confirmEmail" autocomplete="off" placeholder="{me["email"]}"></div>
    <div class="field"><label>Your password</label><input type="password" id="confirmPw" autocomplete="current-password"></div>
    <button class="btn" type="submit" style="background:#b91c1c">Delete my account permanently</button>
  </form>
  <div id="delMsg"></div>
</div>

</div>
<script>
{_LOGOUT_SCRIPT}
(async()=>{{
  const r = await fetch('/lemma/api/account/me');
  const d = await r.json();
  if(!d.authenticated) return;
  // Show verify status based on… we don't expose email_verified yet, but resend link is always safe.
  document.getElementById('verifyStatus').innerHTML = '<p class="muted" style="font-size:13.5px">Email verification: <a href="#" onclick="resend(); return false;">resend verification email</a></p>';
}})();
async function resend(){{
  const r = await fetch('/lemma/api/account/resend-verification', {{method:'POST'}});
  if(r.ok) alert('verification email sent (check console / inbox)');
}}
async function doDelete(){{
  const confirm_email = document.getElementById('confirmEmail').value.trim();
  const password = document.getElementById('confirmPw').value;
  const msg = document.getElementById('delMsg');
  msg.innerHTML = '';
  if(!confirm('Really delete your account and ALL data? This cannot be undone.')) return;
  const r = await fetch('/lemma/api/account/delete', {{
    method:'POST', headers:{{'Content-Type':'application/json'}},
    body: JSON.stringify({{confirm: confirm_email, password}}),
  }});
  const d = await r.json();
  if(!r.ok){{ msg.innerHTML = '<div class="alert">' + (d.detail || 'Delete failed.') + '</div>'; return; }}
  location.href = '/lemma/teachers';
}}
</script>
</body></html>"""
    return HTMLResponse(page)


@router.get("/lemma/favicon.svg")
async def favicon():
    svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="12" fill="#0ea5e9"/>
<text x="32" y="46" font-family="ui-sans-serif,system-ui" font-size="44" font-weight="700" fill="#ffffff" text-anchor="middle">L</text>
</svg>
"""
    from fastapi.responses import Response
    return Response(content=svg, media_type="image/svg+xml")


@router.get("/lemma/signup", response_class=HTMLResponse)
async def lemma_signup_page(req: Request) -> HTMLResponse:
    if get_current_teacher(req):
        return RedirectResponse("/lemma/me", status_code=302)
    nav = _navbar(False, None)
    page = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sign up · Lemma</title>
<style>{_BASE_STYLE}</style></head><body>
<div class="wrap narrow">
{nav}

<h1>Sign up</h1>
<p class="lead">Make a free Lemma account. You can create classes, see results, and connect to Canvas.</p>

<div class="card">
  <form id="signupForm" onsubmit="event.preventDefault(); doSignup();">
    <div class="field">
      <label>Your name (what students see)</label>
      <input type="text" id="display_name" required maxlength="80" placeholder="Mr. K, Ms. Rivera, etc." autocomplete="name">
    </div>
    <div class="field">
      <label>Email</label>
      <input type="email" id="email" required autocomplete="email" placeholder="you@yourschool.edu">
    </div>
    <div class="field">
      <label>School (optional)</label>
      <input type="text" id="school" maxlength="100" placeholder="Lincoln High" autocomplete="organization">
    </div>
    <div class="field">
      <label>Password</label>
      <input type="password" id="password" required minlength="8" autocomplete="new-password" placeholder="≥ 8 characters">
      <div class="help">At least 8 characters. Lemma stores only a hashed version.</div>
    </div>
    <button class="btn" type="submit">Create account →</button>
    <p class="muted" style="margin-top:12px;font-size:13px">Already have one? <a href="/lemma/login">Log in</a></p>
  </form>
  <div id="msg"></div>
</div>

</div>
<script>
{_LOGOUT_SCRIPT}
async function doSignup(){{
  const display_name = document.getElementById('display_name').value.trim();
  const email = document.getElementById('email').value.trim();
  const school = document.getElementById('school').value.trim();
  const password = document.getElementById('password').value;
  const msg = document.getElementById('msg');
  msg.innerHTML = '';
  const btn = document.querySelector('#signupForm button');
  btn.disabled = true;
  try {{
    const r = await fetch('/lemma/api/account/signup', {{
      method:'POST', headers:{{'Content-Type':'application/json'}},
      body: JSON.stringify({{email, password, display_name, school: school || null}}),
    }});
    const d = await r.json();
    if(!r.ok){{ msg.innerHTML = '<div class="alert">' + (d.detail || 'Signup failed.') + '</div>'; btn.disabled = false; return; }}
    msg.innerHTML = '<div class="alert ok">Account created. Loading your dashboard…</div>';
    setTimeout(()=>{{ location.href = '/lemma/me'; }}, 600);
  }} catch(err){{
    msg.innerHTML = '<div class="alert">Network error: ' + err.message + '</div>';
    btn.disabled = false;
  }}
}}
</script>
</body></html>"""
    return HTMLResponse(page)


@router.get("/lemma/login", response_class=HTMLResponse)
async def lemma_login_page(req: Request) -> HTMLResponse:
    if get_current_teacher(req):
        return RedirectResponse("/lemma/me", status_code=302)
    nav = _navbar(False, None)
    page = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Log in · Lemma</title>
<style>{_BASE_STYLE}</style></head><body>
<div class="wrap narrow">
{nav}

<h1>Log in</h1>
<p class="lead">Welcome back.</p>

<div class="card">
  <form id="loginForm" onsubmit="event.preventDefault(); doLogin();">
    <div class="field">
      <label>Email</label>
      <input type="email" id="email" required autocomplete="email">
    </div>
    <div class="field">
      <label>Password</label>
      <input type="password" id="password" required autocomplete="current-password">
    </div>
    <button class="btn" type="submit">Log in →</button>
    <p class="muted" style="margin-top:12px;font-size:13px">No account? <a href="/lemma/signup">Sign up</a></p>
  </form>
  <div id="msg"></div>
</div>

</div>
<script>
{_LOGOUT_SCRIPT}
async function doLogin(){{
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;
  const msg = document.getElementById('msg');
  msg.innerHTML = '';
  const btn = document.querySelector('#loginForm button');
  btn.disabled = true;
  try {{
    const r = await fetch('/lemma/api/account/login', {{
      method:'POST', headers:{{'Content-Type':'application/json'}},
      body: JSON.stringify({{email, password}}),
    }});
    const d = await r.json();
    if(!r.ok){{ msg.innerHTML = '<div class="alert">' + (d.detail || 'Login failed.') + '</div>'; btn.disabled = false; return; }}
    location.href = '/lemma/me';
  }} catch(err){{
    msg.innerHTML = '<div class="alert">Network error: ' + err.message + '</div>';
    btn.disabled = false;
  }}
}}
</script>
</body></html>"""
    return HTMLResponse(page)


_COURSE_LABEL = {
    "pre-algebra": "Pre-Algebra", "algebra-1": "Algebra 1", "geometry": "Geometry",
    "algebra-2": "Algebra 2", "precalc": "Precalculus",
    "calc-ab": "AP Calc AB", "calc-bc": "AP Calc BC", "stats": "AP Statistics",
    "multivar": "Multivar Calc", "linear-alg": "Linear Algebra",
    "diff-eq": "Diff Eq", "real-analysis": "Real Analysis", "topology": "Topology",
}


@router.get("/lemma/me", response_class=HTMLResponse)
async def lemma_my_classes(req: Request) -> HTMLResponse:
    me = get_current_teacher(req)
    if not me:
        return RedirectResponse("/lemma/login", status_code=302)
    nav = _navbar(True, me["display_name"])
    page = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>My classes · Lemma</title>
<style>{_BASE_STYLE}</style></head><body>
<div class="wrap">
{nav}

<h1>Welcome back, {me["display_name"]}</h1>
<p class="lead">Your classes. Each one has its own join code, dashboard, and (optionally) Canvas link.</p>

<div id="verifyBanner" style="display:none;background:#fef3c7;border:1px solid #fde68a;color:#78350f;padding:12px 16px;border-radius:8px;margin-bottom:16px;font-size:13.5px">
  <b>Verify your email.</b> Check your inbox for the confirmation link Lemma sent. Verifying lets us help you recover your account if you forget your password.
  <a href="#" onclick="resendVerification(); return false;" style="color:#92400e;font-weight:600;margin-left:6px">resend</a>
</div>

<div class="card">
  <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin-bottom:12px">
    <h2 style="margin-bottom:0">Your classes</h2>
    <div style="flex:1"></div>
    <a class="btn" href="/lemma/start">+ New class</a>
    <a class="btn ghost" href="/lemma/canvas/setup">🔗 Connect Canvas</a>
  </div>
  <div id="classesArea">loading…</div>
</div>

<div id="claimableCard" class="card" style="display:none">
  <h2>Claimable classes</h2>
  <p class="muted" style="margin-bottom:10px">Classes you created anonymously before signing up that match your name. Click <b>Claim</b> to attach them to this account.</p>
  <div id="claimableArea"></div>
</div>

<div class="card" style="background:#f8fafc">
  <h3 style="margin-bottom:6px">Tips</h3>
  <ul class="muted" style="margin-left:18px;font-size:13.5px;line-height:1.7">
    <li>Share each class by giving students the link (e.g. <span class="kbd">/lemma/c/&lt;code&gt;</span>) or pasting it in a Canvas module.</li>
    <li>The <b>Canvas link</b> is per-class. Connect each class separately to its Canvas course.</li>
    <li>Math is the deep app today. Other subjects work but are skeleton.</li>
  </ul>
</div>

</div>
<script>
{_LOGOUT_SCRIPT}
const COURSE_LABEL = {repr(_COURSE_LABEL)};
async function resendVerification(){{
  const r = await fetch('/lemma/api/account/resend-verification', {{method:'POST'}});
  if(r.ok) alert('verification email re-sent (check console / inbox)');
}}
async function load(){{
  const r = await fetch('/lemma/api/account/me');
  const d = await r.json();
  if(!d.authenticated){{ location.href = '/lemma/login'; return; }}
  if(!d.teacher.email_verified){{ document.getElementById('verifyBanner').style.display = ''; }}
  const area = document.getElementById('classesArea');
  if(!d.classes.length){{
    area.innerHTML = '<div class="empty">No classes yet. <a href="/lemma/start">Create your first one →</a></div>';
  }} else {{
    let h = '<table><thead><tr><th>Class</th><th>Code</th><th>Subject</th><th>Roster</th><th>Warmups</th><th>Created</th><th></th></tr></thead><tbody>';
    for(const c of d.classes){{
      h += `<tr>
        <td><a href="/lemma/teacher/${{c.code}}">${{escapeHTML(c.class_name)}}</a></td>
        <td><span class="kbd">${{c.code}}</span></td>
        <td>${{escapeHTML(COURSE_LABEL[c.course_id] || c.course_id)}}</td>
        <td>${{c.roster}}</td>
        <td>${{c.warmups}}</td>
        <td>${{new Date(c.created_at).toLocaleDateString()}}</td>
        <td><a href="/lemma/teacher/${{c.code}}">Open →</a></td>
      </tr>`;
    }}
    h += '</tbody></table>';
    area.innerHTML = h;
  }}
  if(d.claimable && d.claimable.length){{
    document.getElementById('claimableCard').style.display = '';
    let h = '<table><thead><tr><th>Class</th><th>Code</th><th>Subject</th><th>Created</th><th></th></tr></thead><tbody>';
    for(const c of d.claimable){{
      h += `<tr>
        <td>${{escapeHTML(c.class_name)}}</td>
        <td><span class="kbd">${{c.code}}</span></td>
        <td>${{escapeHTML(COURSE_LABEL[c.course_id] || c.course_id)}}</td>
        <td>${{new Date(c.created_at).toLocaleDateString()}}</td>
        <td><button class="btn ghost" onclick="claim('${{c.code}}')">Claim</button></td>
      </tr>`;
    }}
    h += '</tbody></table>';
    document.getElementById('claimableArea').innerHTML = h;
  }}
}}
async function claim(code){{
  const r = await fetch('/lemma/api/account/claim/' + code, {{method:'POST'}});
  if(!r.ok){{ const d = await r.json(); alert(d.detail || 'Claim failed.'); return; }}
  load();
}}
function escapeHTML(s){{ return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }}
load();
</script>
</body></html>"""
    return HTMLResponse(page)
