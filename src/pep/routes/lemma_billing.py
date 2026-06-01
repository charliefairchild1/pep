"""Lemma billing — tiered subscriptions, Stripe Checkout, usage tracking.

Pricing tiers live in TIERS below — change a number in one place and the
pricing page, dashboard, and Stripe metadata all stay consistent.

Stripe is gated by env vars. Without LEMMA_STRIPE_SECRET_KEY set, the
billing pages render but checkout is disabled with a clear message. The
moment you create a Stripe account and paste keys, checkout starts working.

Env vars:
  LEMMA_STRIPE_SECRET_KEY      sk_live_... or sk_test_... — main API key
  LEMMA_STRIPE_WEBHOOK_SECRET  whsec_... — verifies incoming webhook events
  LEMMA_STRIPE_PRICE_SOLO      price_... — Stripe Price ID for Solo tier
  LEMMA_STRIPE_PRICE_MULTI     price_... — Stripe Price ID for Multi tier
  LEMMA_GENERATE_MODEL         haiku | sonnet (default: haiku)
  LEMMA_GRADE_MODEL            haiku | sonnet (default: haiku)
"""
from __future__ import annotations

import json
import os
import secrets as _secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any

import stripe
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from pep.routes.lemma_backend import _conn, _now
from pep.routes.lemma_accounts import get_current_teacher, _navbar, _seo_head, _BASE_STYLE, _LOGOUT_SCRIPT, _public_base


router = APIRouter()


# ---------------------------------------------------------------------------
# Pricing — single source of truth
# ---------------------------------------------------------------------------

TRIAL_DAYS = 14  # auto-given to every new signup; uses Pro Solo features

TIERS: dict[str, dict[str, Any]] = {
    "free": {
        "name": "Free",
        "price_monthly_usd": 0,
        "max_classes": 1,
        "max_students": 25,
        "ai_grading": False,
        "ai_generation": False,
        "canvas": True,
        "blurb": "Try Lemma. Manual grading, one class, up to 25 students. Free forever.",
    },
    "solo": {
        "name": "Pro Solo",
        "price_monthly_usd": 15,
        "max_classes": 3,
        "max_students": 75,
        "ai_grading": True,
        "ai_generation": True,
        "canvas": True,
        "blurb": "For one teacher with up to 3 periods. AI photo grading + adaptive practice included.",
    },
    "multi": {
        "name": "Pro Multi",
        "price_monthly_usd": 30,
        "max_classes": 8,
        "max_students": 200,
        "ai_grading": True,
        "ai_generation": True,
        "canvas": True,
        "blurb": "For teachers with bigger loads or department-wide rollouts. 8 classes, 200 students.",
    },
}
OVERAGE_USD_PER_STUDENT_MONTH = 0.20


def get_tier(plan: str) -> dict[str, Any]:
    return TIERS.get(plan, TIERS["free"])


# Approximate per-call cost in USD (used for our internal cost-projection
# display, not billed to teachers). Update if Anthropic pricing changes.
COST_PER_CALL_USD = {
    ("generate", "haiku"):  0.003,
    ("generate", "sonnet"): 0.017,
    ("grade",    "haiku"):  0.002,
    ("grade",    "sonnet"): 0.010,
}


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

def _init_billing_db() -> None:
    with _conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            teacher_id              INTEGER PRIMARY KEY,
            plan                    TEXT NOT NULL DEFAULT 'free',
            status                  TEXT NOT NULL DEFAULT 'active',
            stripe_customer_id      TEXT,
            stripe_subscription_id  TEXT,
            current_period_start    TEXT,
            current_period_end      TEXT,
            cancel_at_period_end    INTEGER NOT NULL DEFAULT 0,
            updated_at              TEXT NOT NULL,
            FOREIGN KEY (teacher_id) REFERENCES teachers(id)
        );
        CREATE TABLE IF NOT EXISTS usage_log (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id    INTEGER NOT NULL,
            class_code    TEXT,
            operation     TEXT NOT NULL,
            model         TEXT NOT NULL,
            count         INTEGER NOT NULL DEFAULT 1,
            cost_usd      REAL,
            ts            TEXT NOT NULL,
            FOREIGN KEY (teacher_id) REFERENCES teachers(id)
        );
        CREATE INDEX IF NOT EXISTS usage_teacher_idx ON usage_log(teacher_id);
        CREATE INDEX IF NOT EXISTS usage_ts_idx ON usage_log(ts);
        """)


_init_billing_db()


# ---------------------------------------------------------------------------
# Stripe init
# ---------------------------------------------------------------------------

def _stripe_configured() -> bool:
    return bool(os.environ.get("LEMMA_STRIPE_SECRET_KEY"))


def _stripe_init() -> bool:
    key = os.environ.get("LEMMA_STRIPE_SECRET_KEY", "").strip()
    if not key:
        return False
    stripe.api_key = key
    return True


def _stripe_price_id(plan: str) -> str | None:
    if plan == "solo":
        return os.environ.get("LEMMA_STRIPE_PRICE_SOLO", "").strip() or None
    if plan == "multi":
        return os.environ.get("LEMMA_STRIPE_PRICE_MULTI", "").strip() or None
    return None


# ---------------------------------------------------------------------------
# Subscription state helpers
# ---------------------------------------------------------------------------

def get_subscription(teacher_id: int) -> dict[str, Any]:
    with _conn() as c:
        row = c.execute(
            "SELECT * FROM subscriptions WHERE teacher_id = ?", (teacher_id,)
        ).fetchone()
        if row:
            return dict(row)
        c.execute(
            "INSERT INTO subscriptions (teacher_id, plan, status, updated_at) VALUES (?, 'free', 'active', ?)",
            (teacher_id, _now()),
        )
        return {"teacher_id": teacher_id, "plan": "free", "status": "active",
                "stripe_customer_id": None, "stripe_subscription_id": None,
                "current_period_start": None, "current_period_end": None,
                "cancel_at_period_end": 0, "updated_at": _now()}


def update_subscription(teacher_id: int, **fields: Any) -> None:
    keys = ["plan", "status", "stripe_customer_id", "stripe_subscription_id",
            "current_period_start", "current_period_end", "cancel_at_period_end"]
    cols = [k for k in keys if k in fields]
    if not cols:
        return
    values = [fields[k] for k in cols]
    set_clause = ", ".join(f"{k} = ?" for k in cols) + ", updated_at = ?"
    with _conn() as c:
        existing = c.execute("SELECT 1 FROM subscriptions WHERE teacher_id = ?", (teacher_id,)).fetchone()
        if existing:
            c.execute(
                f"UPDATE subscriptions SET {set_clause} WHERE teacher_id = ?",
                (*values, _now(), teacher_id),
            )
        else:
            cols_all = ["teacher_id"] + cols + ["updated_at"]
            placeholders = ", ".join("?" for _ in cols_all)
            c.execute(
                f"INSERT INTO subscriptions ({', '.join(cols_all)}) VALUES ({placeholders})",
                (teacher_id, *values, _now()),
            )


def get_total_students(teacher_id: int) -> int:
    with _conn() as c:
        return c.execute(
            """SELECT COUNT(*) FROM students s
               JOIN classes c ON s.class_code = c.code
               WHERE c.teacher_id = ?""",
            (teacher_id,),
        ).fetchone()[0]


def get_total_classes(teacher_id: int) -> int:
    with _conn() as c:
        return c.execute(
            "SELECT COUNT(*) FROM classes WHERE teacher_id = ?",
            (teacher_id,),
        ).fetchone()[0]


# ---------------------------------------------------------------------------
# Feature gates
# ---------------------------------------------------------------------------

def is_trial_active(sub: dict[str, Any]) -> bool:
    if sub.get("status") != "trialing":
        return False
    end = sub.get("current_period_end") or ""
    return bool(end) and end > _now()


def can_use_ai_grading(teacher_id: int) -> tuple[bool, str | None]:
    """Returns (allowed, reason_if_not). Reason is shown to the teacher."""
    sub = get_subscription(teacher_id)
    # If trial has expired, demote to free automatically
    if sub.get("status") == "trialing" and not is_trial_active(sub):
        update_subscription(teacher_id, plan="free", status="active")
        sub = get_subscription(teacher_id)
    tier = get_tier(sub["plan"])
    if sub["status"] not in ("active", "trialing"):
        return False, f"Your subscription is {sub['status']}. Reactivate to use AI grading."
    if not tier["ai_grading"]:
        return False, f"AI grading is on Pro Solo and Pro Multi. Upgrade to enable it."
    students = get_total_students(teacher_id)
    if students > tier["max_students"]:
        return False, (
            f"You have {students} students; {tier['name']} includes up to {tier['max_students']}. "
            f"Upgrade or accept overage charges (${OVERAGE_USD_PER_STUDENT_MONTH:.2f}/student over the limit)."
        )
    classes = get_total_classes(teacher_id)
    if classes > tier["max_classes"]:
        return False, f"You have {classes} classes; {tier['name']} includes up to {tier['max_classes']}."
    return True, None


def can_create_class(teacher_id: int) -> tuple[bool, str | None]:
    sub = get_subscription(teacher_id)
    tier = get_tier(sub["plan"])
    classes = get_total_classes(teacher_id)
    if classes >= tier["max_classes"]:
        return False, (
            f"{tier['name']} includes up to {tier['max_classes']} class"
            f"{'es' if tier['max_classes']!=1 else ''}. Upgrade to add more."
        )
    return True, None


def can_add_student(teacher_id: int) -> tuple[bool, str | None]:
    sub = get_subscription(teacher_id)
    tier = get_tier(sub["plan"])
    students = get_total_students(teacher_id)
    if students >= tier["max_students"]:
        if sub["plan"] == "free":
            return False, f"Free tier holds up to {tier['max_students']} students. Upgrade to Pro Solo for 75."
        # paid tiers can go over — overage charges apply
    return True, None


# ---------------------------------------------------------------------------
# Usage tracking
# ---------------------------------------------------------------------------

def log_usage(teacher_id: int, operation: str, model: str, count: int = 1, class_code: str | None = None) -> None:
    cost = COST_PER_CALL_USD.get((operation, model), 0.0) * count
    with _conn() as c:
        c.execute(
            "INSERT INTO usage_log (teacher_id, class_code, operation, model, count, cost_usd, ts) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (teacher_id, class_code, operation, model, count, cost, _now()),
        )


def get_usage_this_month(teacher_id: int) -> dict[str, Any]:
    month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat(timespec="seconds")
    with _conn() as c:
        rows = c.execute(
            "SELECT operation, model, SUM(count) AS calls, SUM(cost_usd) AS cost "
            "FROM usage_log WHERE teacher_id = ? AND ts >= ? "
            "GROUP BY operation, model",
            (teacher_id, month_start),
        ).fetchall()
    total_calls = 0
    total_cost = 0.0
    by_op: dict[str, dict[str, float]] = {}
    for r in rows:
        total_calls += int(r["calls"] or 0)
        total_cost += float(r["cost"] or 0)
        by_op.setdefault(r["operation"], {"calls": 0, "cost": 0.0})
        by_op[r["operation"]]["calls"] += int(r["calls"] or 0)
        by_op[r["operation"]]["cost"] += float(r["cost"] or 0)
    return {"total_calls": total_calls, "total_cost_usd": round(total_cost, 4), "by_operation": by_op}


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------

@router.get("/lemma/api/billing/me")
async def billing_me(req: Request) -> JSONResponse:
    me = get_current_teacher(req)
    if not me:
        raise HTTPException(401, "not signed in")
    sub = get_subscription(me["id"])
    tier = get_tier(sub["plan"])
    classes = get_total_classes(me["id"])
    students = get_total_students(me["id"])
    return JSONResponse({
        "plan": sub["plan"],
        "plan_name": tier["name"],
        "status": sub["status"],
        "tier": tier,
        "limits": {"max_classes": tier["max_classes"], "max_students": tier["max_students"]},
        "usage": {"classes": classes, "students": students},
        "overage_price_per_student": OVERAGE_USD_PER_STUDENT_MONTH,
        "stripe_configured": _stripe_configured(),
        "current_period_end": sub.get("current_period_end"),
        "cancel_at_period_end": bool(sub.get("cancel_at_period_end")),
        "ai_usage_this_month": get_usage_this_month(me["id"]),
    })


@router.post("/lemma/api/billing/checkout")
async def billing_checkout(req: Request) -> JSONResponse:
    me = get_current_teacher(req)
    if not me:
        raise HTTPException(401, "not signed in")
    if not _stripe_init():
        raise HTTPException(503, "billing is not configured on this server. Tell the admin to set LEMMA_STRIPE_SECRET_KEY.")
    body = await req.json()
    plan = (body.get("plan") or "").strip().lower()
    if plan not in ("solo", "multi"):
        raise HTTPException(400, "plan must be 'solo' or 'multi'")
    price_id = _stripe_price_id(plan)
    if not price_id:
        raise HTTPException(503, f"No Stripe Price ID configured for {plan}. Set LEMMA_STRIPE_PRICE_{plan.upper()}.")
    sub = get_subscription(me["id"])
    base = _public_base(req)
    try:
        customer_id = sub.get("stripe_customer_id")
        if not customer_id:
            customer = stripe.Customer.create(
                email=me["email"],
                name=me["display_name"],
                metadata={"lemma_teacher_id": str(me["id"])},
            )
            customer_id = customer.id
            update_subscription(me["id"], stripe_customer_id=customer_id)
        session = stripe.checkout.Session.create(
            mode="subscription",
            customer=customer_id,
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=f"{base}/lemma/me?upgrade=success",
            cancel_url=f"{base}/lemma/pricing?upgrade=cancel",
            metadata={"lemma_teacher_id": str(me["id"]), "lemma_plan": plan},
            allow_promotion_codes=True,
        )
        return JSONResponse({"ok": True, "url": session.url})
    except stripe.StripeError as e:
        raise HTTPException(500, f"Stripe error: {str(e)[:200]}")


@router.post("/lemma/api/billing/portal")
async def billing_portal(req: Request) -> JSONResponse:
    me = get_current_teacher(req)
    if not me:
        raise HTTPException(401, "not signed in")
    if not _stripe_init():
        raise HTTPException(503, "billing not configured")
    sub = get_subscription(me["id"])
    if not sub.get("stripe_customer_id"):
        raise HTTPException(400, "no Stripe customer record. Upgrade first.")
    base = _public_base(req)
    try:
        session = stripe.billing_portal.Session.create(
            customer=sub["stripe_customer_id"],
            return_url=f"{base}/lemma/account",
        )
        return JSONResponse({"ok": True, "url": session.url})
    except stripe.StripeError as e:
        raise HTTPException(500, f"Stripe error: {str(e)[:200]}")


@router.post("/lemma/api/billing/webhook")
async def billing_webhook(req: Request) -> JSONResponse:
    if not _stripe_init():
        raise HTTPException(503, "billing not configured")
    secret = os.environ.get("LEMMA_STRIPE_WEBHOOK_SECRET", "").strip()
    if not secret:
        raise HTTPException(503, "webhook secret not configured")
    payload = await req.body()
    sig_header = req.headers.get("stripe-signature", "")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, secret)
    except (stripe.SignatureVerificationError, ValueError):
        raise HTTPException(400, "invalid signature")
    et = event["type"]
    data = event["data"]["object"]

    def _find_teacher_id_from_customer(customer_id: str) -> int | None:
        with _conn() as c:
            r = c.execute(
                "SELECT teacher_id FROM subscriptions WHERE stripe_customer_id = ?",
                (customer_id,),
            ).fetchone()
            return int(r["teacher_id"]) if r else None

    if et == "checkout.session.completed":
        meta = data.get("metadata") or {}
        tid = int(meta.get("lemma_teacher_id") or 0)
        plan = (meta.get("lemma_plan") or "solo").lower()
        sub_id = data.get("subscription")
        if tid:
            update_subscription(tid, plan=plan, status="active", stripe_subscription_id=sub_id)
    elif et in ("customer.subscription.updated", "customer.subscription.created"):
        tid = _find_teacher_id_from_customer(data.get("customer", ""))
        if tid:
            items = data.get("items", {}).get("data", [])
            price_id = items[0]["price"]["id"] if items else None
            plan = "free"
            if price_id == os.environ.get("LEMMA_STRIPE_PRICE_SOLO", ""):
                plan = "solo"
            elif price_id == os.environ.get("LEMMA_STRIPE_PRICE_MULTI", ""):
                plan = "multi"
            update_subscription(
                tid, plan=plan, status=data.get("status", "active"),
                stripe_subscription_id=data.get("id"),
                current_period_start=str(data.get("current_period_start") or ""),
                current_period_end=str(data.get("current_period_end") or ""),
                cancel_at_period_end=1 if data.get("cancel_at_period_end") else 0,
            )
    elif et == "customer.subscription.deleted":
        tid = _find_teacher_id_from_customer(data.get("customer", ""))
        if tid:
            update_subscription(tid, plan="free", status="canceled", stripe_subscription_id=None)
    return JSONResponse({"received": True, "type": et})


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

def _tier_card(plan_key: str, current_plan: str, stripe_ready: bool) -> str:
    tier = TIERS[plan_key]
    is_current = plan_key == current_plan
    is_free = plan_key == "free"
    button = ""
    if is_current:
        button = '<button class="btn ghost" disabled style="width:100%">Your current plan</button>'
    elif is_free:
        button = '<a class="btn ghost" href="/lemma/signup" style="display:block;text-align:center;text-decoration:none">Sign up free</a>'
    elif stripe_ready:
        button = f'<button class="btn" onclick="upgrade(\'{plan_key}\')" style="width:100%">Upgrade to {tier["name"]} →</button>'
    else:
        button = '<button class="btn ghost" disabled style="width:100%" title="Stripe not configured yet">Coming soon</button>'
    features = []
    features.append(f'<li>{tier["max_classes"]} class{"es" if tier["max_classes"] != 1 else ""}</li>')
    features.append(f'<li>{tier["max_students"]} students</li>')
    features.append(f'<li>{"✓" if tier["ai_grading"] else "—"} AI photo grading</li>')
    features.append(f'<li>{"✓" if tier["ai_generation"] else "—"} Adaptive practice (AI-generated)</li>')
    features.append(f'<li>{"✓" if tier["canvas"] else "—"} Canvas LMS integration</li>')
    features.append("<li>Manual grading + dashboards</li>")
    return f'''
    <div class="card" style="display:flex;flex-direction:column;{'border-color:#0ea5e9;box-shadow:0 0 0 2px #0ea5e9 inset' if is_current else ''}">
      <h2>{tier["name"]}</h2>
      <div style="font-size:32px;font-weight:700;color:#0f172a;margin:8px 0">
        ${tier["price_monthly_usd"]}<span style="font-size:14px;color:#64748b;font-weight:400">/month</span>
      </div>
      <p class="muted" style="font-size:13.5px">{tier["blurb"]}</p>
      <ul style="margin:14px 0 18px 18px;color:#334155;font-size:13.5px;line-height:1.85">
        {''.join(features)}
      </ul>
      <div style="margin-top:auto">{button}</div>
    </div>'''


@router.get("/lemma/pricing", response_class=HTMLResponse)
async def lemma_pricing_page(req: Request) -> HTMLResponse:
    me = get_current_teacher(req)
    nav = _navbar(bool(me), me["display_name"] if me else None)
    current_plan = "free"
    if me:
        current_plan = get_subscription(me["id"])["plan"]
    stripe_ready = _stripe_configured() and bool(_stripe_price_id("solo")) and bool(_stripe_price_id("multi"))
    head = _seo_head(
        req,
        title="Pricing · Lemma — Free + Pro plans for math teachers",
        description=(
            f"Lemma pricing — Free for manual grading. Pro Solo ${TIERS['solo']['price_monthly_usd']}/mo "
            f"for 3 classes with AI photo grading. Pro Multi ${TIERS['multi']['price_monthly_usd']}/mo "
            "for 8 classes. Overage at $0.20/student over your tier limit. No credit card to start."
        ),
        path="/lemma/pricing",
    )
    cards = "".join([_tier_card(p, current_plan, stripe_ready) for p in ("free", "solo", "multi")])
    not_configured_banner = ""
    if not stripe_ready:
        not_configured_banner = '''
        <div class="card" style="background:#fef3c7;border-color:#fde68a">
          <h3 style="color:#92400e">⚙️ Billing not yet configured on this server</h3>
          <p style="color:#78350f;font-size:13.5px;margin-top:6px">
            Upgrade buttons are inactive until Stripe environment variables are set on the server.
            Free tier works fully right now.
          </p>
        </div>'''
    page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
{head}
<style>{_BASE_STYLE}</style></head><body>
<div class="wrap">
{nav}
<header class="hero" style="padding:32px 0 12px;text-align:center">
  <h1>Pricing</h1>
  <p class="lead" style="max-width:680px;margin:8px auto 0">
    Free to start. AI grading and adaptive practice are on the Pro tiers — because the AI calls cost
    real money on our end. No credit card to sign up.
  </p>
</header>

{not_configured_banner}

<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px;margin-top:18px">
  {cards}
</div>

<div class="card" style="margin-top:18px">
  <h2>Going over your tier limit</h2>
  <p class="muted" style="font-size:13.5px">
    On the Pro tiers, you can exceed your tier's student limit — you'll just be charged
    <b>${OVERAGE_USD_PER_STUDENT_MONTH:.2f} per student per month</b> over the included count. No surprise cutoffs.
    The Free tier is hard-capped at {TIERS['free']['max_students']} students.
  </p>
</div>

<div class="card">
  <h2>Why is grading paid?</h2>
  <p class="muted" style="font-size:13.5px">
    AI grading calls a vision model (Anthropic Claude) on every photo. Each call costs money on our
    side. The Pro price covers those calls plus a small margin to keep Lemma running and improving.
    Manual grading uses no AI and stays free forever.
  </p>
</div>

<div class="card">
  <h2>Frequently asked</h2>
  <h3 style="margin-top:10px">Can I switch tiers?</h3>
  <p class="muted">Yes — upgrade or downgrade any time from the billing portal. Changes prorate.</p>
  <h3 style="margin-top:10px">Can I cancel?</h3>
  <p class="muted">Yes. Cancel from the billing portal. You stay on Pro until end of period; then auto-downgrade to Free.</p>
  <h3 style="margin-top:10px">Do you offer a free trial?</h3>
  <p class="muted">The Free tier never expires. If you want a Pro trial, contact us via the in-app help link.</p>
  <h3 style="margin-top:10px">School / district pricing?</h3>
  <p class="muted">Coming soon. For now, each teacher signs up individually.</p>
</div>

<p style="text-align:center;color:#94a3b8;font-size:13px;margin-top:24px">
  <a href="/lemma/teachers">← back to home</a>
</p>

</div>
<script>
{_LOGOUT_SCRIPT}
async function upgrade(plan){{
  const r = await fetch('/lemma/api/billing/checkout', {{
    method:'POST', headers:{{'Content-Type':'application/json'}},
    body: JSON.stringify({{plan}}),
  }});
  const d = await r.json();
  if(!r.ok){{ alert(d.detail || 'Upgrade failed.'); return; }}
  if(d.url) location.href = d.url;
}}
</script>
</body></html>"""
    return HTMLResponse(page)


@router.get("/lemma/upgrade", response_class=HTMLResponse)
async def lemma_upgrade_redirect() -> RedirectResponse:
    return RedirectResponse("/lemma/pricing", status_code=302)


# ---------------------------------------------------------------------------
# Admin override — flip a teacher's plan with a secret token.
# Use this to bypass Stripe for testing. Set LEMMA_ADMIN_SECRET in Render env.
# ---------------------------------------------------------------------------

@router.post("/lemma/api/admin/set-plan")
async def admin_set_plan(req: Request) -> JSONResponse:
    body = await req.json()
    secret = (body.get("secret") or "").strip()
    expected = (os.environ.get("LEMMA_ADMIN_SECRET") or "").strip()
    if not expected:
        raise HTTPException(503, "admin endpoint disabled (no LEMMA_ADMIN_SECRET set)")
    if not _secrets.compare_digest(secret, expected):
        raise HTTPException(403, "forbidden")
    email = (body.get("email") or "").strip().lower()
    plan = (body.get("plan") or "").strip().lower()
    if plan not in ("free", "solo", "multi"):
        raise HTTPException(400, "plan must be 'free', 'solo', or 'multi'")
    if not email:
        raise HTTPException(400, "email required")
    with _conn() as c:
        t = c.execute("SELECT id FROM teachers WHERE email = ?", (email,)).fetchone()
        if not t:
            raise HTTPException(404, f"no teacher account for {email}")
    update_subscription(t["id"], plan=plan, status="active")
    return JSONResponse({"ok": True, "email": email, "plan": plan})
