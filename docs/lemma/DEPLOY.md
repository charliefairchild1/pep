# Deploying Lemma

This is a one-page guide to getting Lemma on a public URL so Google can index it and your teacher can use it.

Total time on the easy path: **~40 minutes**. Total ongoing cost: **$0–$5/month** for hosting + **~$12/year** for a domain.

---

## Step 1 — Pick a host

| Host | Free tier? | Best for |
|---|---|---|
| **Render** | Yes (with cold starts after 15 min idle) | Easiest. Git-push deploys. |
| **Fly.io** | Yes (3 small VMs free) | Always-on free, more control |
| **Railway** | No (~$5/mo always-on) | If you hate config, just want it to work |

Pick **Render** if you've never deployed before. Steps below assume Render.

---

## Step 2 — Prepare the repo

Lemma lives inside the PEP project. From `~/projects/pep/`:

**Procfile** (one line, tells Render how to start):
```
web: uvicorn pep.main:app --host 0.0.0.0 --port $PORT
```

**Or Dockerfile** (if you want full control — Fly uses this):
```Dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN uv sync --frozen --no-dev
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD uv run uvicorn pep.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

**Push to GitHub** if not already there:
```bash
cd ~/projects/pep
git add Procfile Dockerfile
git commit -m "deploy: Procfile + Dockerfile for Render/Fly"
git push
```

---

## Step 3 — Deploy on Render

1. Sign up at https://render.com (use GitHub auth)
2. **New +** → **Web Service** → pick your `pep` repo
3. Settings:
   - **Name**: `lemma` (or whatever)
   - **Runtime**: Python (or Docker, if using the Dockerfile)
   - **Build command**: `uv sync --frozen --no-dev` (or leave default if Docker)
   - **Start command**: `uv run uvicorn pep.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free
4. **Environment** tab → add these:
   - `LEMMA_PUBLIC_URL` = `https://lemma-XXX.onrender.com` (Render gives you this URL after first deploy — come back and set it then)
   - `PYTHONUNBUFFERED` = `1` (so logs appear immediately)
5. Click **Create Web Service**. First deploy takes 3–5 minutes.

After it's live, **visit** `https://lemma-XXX.onrender.com/lemma/teachers` — you should see the marketing page with your Render URL in the canonical tags.

---

## Step 4 — Buy a domain (optional but recommended)

A short, memorable domain ("lemmamath.com", "trylemma.com", "uselemma.com") is much better for SEO and word-of-mouth than `lemma-xxx.onrender.com`.

- **Cloudflare Registrar** — at-cost pricing (~$10/yr for `.com`)
- **Porkbun** — $9–11/yr `.com`, includes WHOIS privacy
- **Namecheap** — common, slightly more expensive

After buying, in your registrar's DNS settings:
- Add a **CNAME** record:
  - `lemma` → `lemma-XXX.onrender.com`
- Or for the apex (`@`):
  - Use Cloudflare for free apex CNAME flattening, or use the host's instructions

In Render → **Custom Domains** → add `lemma.yourdomain.com`. Render handles HTTPS automatically.

Then **update the env var**:
- `LEMMA_PUBLIC_URL` = `https://lemma.yourdomain.com`

This makes every canonical URL, Open Graph URL, sitemap entry, and email link use your real domain.

---

## Step 5 — Set up email (so verification + password reset work)

Use **Resend** — easiest pluggable transactional email.

1. Sign up at https://resend.com (free tier: 100 emails/day)
2. Add your domain — Resend gives you DNS records to add (SPF/DKIM/DMARC). Add them in your registrar.
3. Get an API key from the Resend dashboard
4. In Render env, add:
   - `LEMMA_SMTP_HOST` = `smtp.resend.com`
   - `LEMMA_SMTP_PORT` = `587`
   - `LEMMA_SMTP_USER` = `resend`
   - `LEMMA_SMTP_PASS` = `re_YourApiKeyHere`
   - `LEMMA_SMTP_FROM` = `Lemma <hello@lemma.yourdomain.com>`

If you skip this step, signup verification and password reset emails are printed to the Render logs instead — works for testing but real users can't recover their accounts.

---

## Step 6 — Submit to Google Search Console

1. Go to https://search.google.com/search-console
2. **Add property** → pick **URL prefix** → enter `https://lemma.yourdomain.com`
3. Verify ownership — easiest is the HTML meta tag method:
   - Google gives you a `<meta>` tag
   - Add it to the `<head>` of `/lemma/teachers` (we already have the SEO helper — easiest is to paste it into `_seo_head` in `lemma_accounts.py`)
4. **Sitemaps** in the left nav → submit `https://lemma.yourdomain.com/sitemap.xml`
5. **URL Inspection** → enter `https://lemma.yourdomain.com/lemma/teachers` → **Request Indexing**

Google will crawl within a few hours. Ranking for "lemma grading app" takes days–weeks; ranking for distinctive terms ("Lemma daily warmup", your domain name, etc.) can happen within days.

---

## Step 7 — Ongoing

- **HTTPS** — Render does this automatically. Don't worry about it.
- **Backups** — Lemma uses SQLite at `data/lemma.db`. On Render's free tier, the disk is ephemeral — **set up a persistent disk** ($1/month) and mount it at `/app/data`, or migrate to Postgres if you have any real users.
- **Logs** — Render's dashboard has them. Search for "EMAIL" to find what verification/reset emails would have been sent.
- **Updates** — `git push` → Render re-deploys automatically.

---

## Common pitfalls

- **Forgot to set `LEMMA_PUBLIC_URL`** — canonical URLs and sitemap will still show `http://localhost:8000`. Google won't index.
- **HTTPS-only cookies** — flip `secure=True` on the session cookie once on HTTPS (line in `lemma_accounts.py: _set_cookie`).
- **SQLite on ephemeral disk** — Render's free tier wipes the disk on each restart. Add the $1/mo persistent disk if you have any real teachers using it.
- **Slow first request** — Render free tier sleeps after 15 min idle; first request after wake takes ~30 sec. Not ideal for SEO. Upgrade to Starter ($7/mo) for always-on.

---

## After deploying

- Visit `https://lemma.yourdomain.com/lemma/teachers` — confirm SEO meta tags use the real domain
- Search Google for `site:lemma.yourdomain.com` after a few days — should show the indexed pages
- Tell your teacher the URL
- Tell colleagues — invite them via the **/lemma/team** page (in-app invite link)
