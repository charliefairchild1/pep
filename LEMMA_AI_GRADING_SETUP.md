# Lemma × Anthropic — AI grading setup

The grading endpoint (`POST /lemma/api/grade`) calls Claude with vision to read student warmup photos and score each problem against your answer key. Subscription-gated: free tier sees an upgrade CTA, Pro Solo / Pro Multi go through. Every call is logged to `usage_log` for margin tracking.

## 1. Get an Anthropic API key

1. https://console.anthropic.com → sign up
2. **Settings → API Keys → Create key** → copy the `sk-ant-…` value
3. Add a small starting balance ($5 is plenty to test — Haiku grades ~2,000 photos for that)

## 2. Set the env var on Render

Render → your `lemma` service → **Environment → Add Environment Variable**:

- Key: `LEMMA_ANTHROPIC_API_KEY`
- Value: paste your `sk-ant-…` key

Optional second var to control which model grades:

- Key: `LEMMA_GRADE_MODEL`
- Value: `haiku` (default — $0.002/photo, recommended) · or `sonnet` ($0.01/photo, better handwriting) · or `opus` (most expensive)

Save. Render redeploys automatically.

## 3. Test it

1. Sign in as a teacher with at least Pro Solo
2. Go to **📷 AI grade** in the navbar (`/lemma/grade-test`)
3. Pick a class, enter a student name and topic
4. Paste your problem set: `problem | correct answer`, one per line
5. Upload a photo of the student's work (or a screenshot of solved math)
6. Click **Grade this →**

Within ~5 seconds you'll see per-problem ✓/✗, the student's answer as transcribed, AI feedback per problem, an overall note, and the model used.

## How it works

- **Prompt caching** — the grading system prompt is identical every call, so it's marked `cache_control: ephemeral`. After the first call you get ~90% off the input tokens for the system prompt portion.
- **Structured outputs** — `output_config.format` with a JSON schema enforces a strict response shape. No parsing surprises.
- **Margin tracking** — every call logs operation, model, and a cost estimate to `usage_log`. Query it any time to see what each teacher costs you this month.

## Cost-of-goods reference

| Model | Per photo (input + output) | 16 photos/month/student | 75 students/month |
|---|---|---|---|
| Haiku 4.5 | ~$0.002 | ~$0.03/student | ~$2.40 |
| Sonnet 4.6 | ~$0.010 | ~$0.16/student | ~$12 |
| Opus 4.7 | ~$0.05 | ~$0.80/student | ~$60 |

At $15/month Pro Solo with 75 students:
- **Haiku** → ~$12.60 margin (84%)
- **Sonnet** → ~$3 margin (20%)
- **Opus** → loss

Stay on Haiku as default until you have margin data from real classrooms.

## Gating

The endpoint enforces `can_use_ai_grading(teacher_id)`:
- Free tier → 402 + upgrade CTA
- Pro Solo / Pro Multi → allowed
- Over student limit → 402 + overage notice
- Over class limit → 402

Roster sync (Canvas) does not count toward student limit until students actually appear in the roster table.

## Troubleshooting

- **503 "AI grading is not configured"** → `LEMMA_ANTHROPIC_API_KEY` not set in Render env. Re-check spelling and save.
- **402 "AI grading is on Pro Solo and Pro Multi"** → teacher is on free tier. Tell them to upgrade at `/lemma/pricing`.
- **500 "AI grading service error"** → Anthropic API failure. Check `https://status.anthropic.com`. Most resolve themselves within a minute.
- **Photo too large / wrong format** → only JPEG, PNG, WebP, GIF are accepted. Convert with `sips` (Mac) or `convert` (ImageMagick) if needed.
- **Bad grades** → swap to `sonnet` via env var. Sonnet's vision is noticeably better on messy handwriting.
