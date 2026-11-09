# Domain + Google Search Console setup for Lemma

A specific, step-by-step walkthrough. Do these in order; total time ~45 minutes (some of which is waiting for DNS propagation).

---

## Part 1 — Pick + buy a domain

### Names to try (all unlikely to be taken)

Search availability at https://porkbun.com or https://www.cloudflare.com/products/registrar/. Try these in order:

- **`trylemma.com`** — short, clear intent
- **`lemmamath.com`** — explicit about the subject
- **`uselemma.com`** — action-oriented
- **`getlemma.com`** — also action-oriented
- **`lemmagrading.com`** — specific to what you do, good for SEO
- **`lemma.app`** — premium .app TLD (~$15/yr), short and modern
- **`lemma.education`** — pricey (~$50/yr) but very on-brand

**Skip** `lemma.com` and probably `lemma.io` — likely taken or expensive.

### Where to buy

| Registrar | Price/yr (.com) | WHOIS privacy | DNS quality |
|---|---|---|---|
| **Cloudflare Registrar** | ~$10 | Free, automatic | Best |
| **Porkbun** | $9–11 | Free | Good |
| **Namecheap** | $11–15 | Free first year | Fine |

**Recommended: Cloudflare Registrar.** At-cost pricing, free WHOIS privacy, and you get Cloudflare's CDN/DNS automatically — which is good for speed and SEO.

### Steps to buy

1. Sign up at https://cloudflare.com (free account)
2. Click **Add a Site** → enter the domain you want (it'll search availability)
3. If available: **Register** → fill billing info → buy

If you buy elsewhere, you'll need to update your nameservers to point at Cloudflare's nameservers later for the easiest setup.

---

## Part 2 — Point the domain at Render

Render gives your service a URL like `lemma-xxx.onrender.com`. You want `lemma.yourdomain.com` (or `yourdomain.com` directly) to point there.

### In Render

1. Open your service
2. **Settings** → scroll to **Custom Domains** → **Add Custom Domain**
3. Enter `lemma.yourdomain.com` (or `yourdomain.com` for apex)
4. Render shows you the DNS record to add

### In Cloudflare DNS

1. Open your domain in Cloudflare
2. **DNS** in the left nav → **Records** → **Add Record**
3. For a subdomain like `lemma.yourdomain.com`:
   - **Type**: `CNAME`
   - **Name**: `lemma`
   - **Target**: `lemma-xxx.onrender.com` (whatever Render gave you)
   - **Proxy status**: DNS only (gray cloud) — Render handles HTTPS itself
4. For the apex (`yourdomain.com`):
   - Cloudflare supports CNAME flattening — use **CNAME** with **Name** `@` pointing at Render's URL

DNS usually propagates in 1–5 minutes; can take up to 48 hours in rare cases.

5. Back in Render, click **Verify** on the custom domain. Once verified, Render provisions a Let's Encrypt SSL certificate automatically (~2–5 minutes).

### Update `LEMMA_PUBLIC_URL`

In Render → Environment → **edit** `LEMMA_PUBLIC_URL`:
```
LEMMA_PUBLIC_URL=https://lemma.yourdomain.com
```

Save. Render will redeploy automatically. After redeploy:
- All canonical URLs, Open Graph URLs, sitemap entries, email links use your real domain
- Visit `https://lemma.yourdomain.com/sitemap.xml` — confirm it shows the real URLs

---

## Part 3 — Google Search Console

Google needs to know about your site, and needs to verify you own it.

### Sign up

1. Go to https://search.google.com/search-console
2. Log in with a Google account (use a real account you'll keep)

### Add the property

1. Click **Add Property** in the property selector (top-left dropdown)
2. Two property types:
   - **Domain** — verifies the whole domain via a DNS record. Recommended if you bought the domain.
   - **URL prefix** — verifies a specific URL (like `https://lemma.yourdomain.com`). Faster if you just want one subdomain.
3. **Recommended**: **URL prefix** — enter `https://lemma.yourdomain.com` (with the `https://`).

### Verify ownership — the easy way (HTML meta tag)

1. Google offers several verification methods. Pick **HTML tag**.
2. Google gives you a tag like:
   ```html
   <meta name="google-site-verification" content="ABC123_xyz" />
   ```
3. **Copy the `content` value** (`ABC123_xyz` in the example — the part after `content=`).
4. In Render → Environment → **Add Environment Variable**:
   - Key: `LEMMA_GOOGLE_SITE_VERIFICATION`
   - Value: paste the content value (just the string, no quotes)
5. Save. Render redeploys.
6. After redeploy, visit `https://lemma.yourdomain.com/lemma/teachers` → View Source → confirm the `<meta name="google-site-verification" ...>` tag is there.
7. Back in Search Console, click **Verify**. Should succeed instantly.

### Submit your sitemap

1. In Search Console → left nav → **Sitemaps**
2. Enter `sitemap.xml` (relative path, Google fills in the domain)
3. Click **Submit**
4. Google reads it and finds your 7 indexed URLs.

### Request indexing of the most important page

1. In Search Console → top search bar — paste `https://lemma.yourdomain.com/lemma/teachers`
2. Hit Enter → it'll show "URL is not on Google" the first time
3. Click **Request Indexing** → Google will prioritize crawling it

### Wait

- Google takes hours-to-days for initial indexing
- Ranking for "lemma grading app" depends on backlinks + relevance signals. Distinctive queries ("Lemma daily warmup", your domain name) will rank first.
- Check progress in Search Console → **Performance** (will show clicks + impressions over time)

---

## Part 4 — Bing Webmaster Tools (optional but easy)

Bing is small but DuckDuckGo + ChatGPT search both use it under the hood. Same process:

1. https://www.bing.com/webmasters
2. Add site → `https://lemma.yourdomain.com`
3. Verify via meta tag → set env var:
   - `LEMMA_BING_SITE_VERIFICATION` = the content value Bing gives you
4. Submit sitemap

---

## Part 5 — One-time SEO juice

Once the site is live and verified:

### Submit to directories

These index quickly and give you initial backlinks:
- **Common Sense Education** — https://www.commonsense.org/education/ (review for teacher tools, may take days)
- **Class Tech Tips** — https://classtechtips.com/contact/ (Monica Burns sometimes features new tools)
- **Edutopia community** — https://www.edutopia.org/account/register (share use cases)
- **Reddit r/Teachers + r/matheducation** — share when you have a real case study from your teacher

### One backlink that matters

Get your teacher to mention Lemma on:
- His department's web page at the school
- His Twitter/X if he uses it
- Any teacher newsletters

A single inbound link from a `.edu` domain is worth a lot to Google.

### Add structured-data testing

After verification, run https://search.google.com/test/rich-results on `https://lemma.yourdomain.com/lemma/teachers` — confirms your `SoftwareApplication` and `FAQPage` JSON-LD blocks are valid and might be eligible for rich results in search.

---

## Quick checklist

- [ ] Bought domain (Cloudflare/Porkbun)
- [ ] Render service deployed and reachable
- [ ] Custom domain added to Render + DNS record in Cloudflare
- [ ] HTTPS provisioned on Render (automatic)
- [ ] `LEMMA_PUBLIC_URL` env var set to `https://lemma.yourdomain.com`
- [ ] Search Console property added
- [ ] `LEMMA_GOOGLE_SITE_VERIFICATION` env var set, redeploy fired
- [ ] Search Console verification confirmed
- [ ] `sitemap.xml` submitted
- [ ] `/lemma/teachers` requested for indexing
- [ ] (Optional) Bing Webmaster Tools repeated
- [ ] (Optional) Resend SMTP wired up so verification + reset emails actually send

---

## After that

The remaining work is content + backlinks. Things that move SEO over weeks:
- Each piece of unique content on `/lemma/teachers` and any blog posts you add
- Inbound links from real .edu domains
- People searching for your brand name and clicking your result
- Time on page when they land
