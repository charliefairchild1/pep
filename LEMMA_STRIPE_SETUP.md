# Lemma × Stripe — setup guide

You ship Lemma with pricing infrastructure already wired. To turn on
real payments, you need a Stripe account and four environment variables.
Total time: ~20 minutes.

## 1. Create a Stripe account

1. Go to https://stripe.com → **Start now**
2. Use your real email / business name. Stripe asks for tax info before
   you can take live payments, but you can use test mode immediately.
3. After signup you'll land on the Stripe **Dashboard**. Top-right toggle:
   leave it on **Test mode** until you're ready for real money.

## 2. Create two Products + Prices

In Stripe → **Products** → **+ Create product**:

**Product 1: Lemma Pro Solo**
- Name: `Lemma Pro Solo`
- Description: `For one teacher with up to 3 classes and 75 students. AI photo grading and adaptive practice included.`
- Pricing:
  - **Recurring**
  - **$15.00 USD / month**
- **Save product**
- After save, **copy the Price ID** (looks like `price_1ABC...`) — you'll need it as `LEMMA_STRIPE_PRICE_SOLO`

**Product 2: Lemma Pro Multi**
- Name: `Lemma Pro Multi`
- Description: `For teachers with up to 8 classes and 200 students. AI photo grading and adaptive practice included.`
- Pricing:
  - **Recurring**
  - **$30.00 USD / month**
- **Save product**
- Copy this Price ID — `LEMMA_STRIPE_PRICE_MULTI`

(Skip the overage charge for now. It's simpler to bill overages manually for the first few teachers, then build metered billing later when you have volume.)

## 3. Get your API keys

In Stripe → **Developers** → **API keys**:
- **Secret key** (`sk_test_...` in test mode, `sk_live_...` in live mode) — copy this. It's `LEMMA_STRIPE_SECRET_KEY`. Treat it like a password — never commit it to GitHub.

## 4. Set up the webhook

In Stripe → **Developers** → **Webhooks** → **+ Add endpoint**:
- **Endpoint URL**: `https://lemma-2b0h.onrender.com/lemma/api/billing/webhook` (or your custom domain when you have one)
- **Events to send**: click **+ Select events** and add:
  - `checkout.session.completed`
  - `customer.subscription.created`
  - `customer.subscription.updated`
  - `customer.subscription.deleted`
- Save the endpoint
- Click the new endpoint, scroll to **Signing secret** → **Reveal** → copy. It's `LEMMA_STRIPE_WEBHOOK_SECRET` (looks like `whsec_...`)

## 5. Set the env vars in Render

In Render → your `lemma` service → **Environment** → add these four:

```
LEMMA_STRIPE_SECRET_KEY=sk_test_...            (from step 3)
LEMMA_STRIPE_WEBHOOK_SECRET=whsec_...          (from step 4)
LEMMA_STRIPE_PRICE_SOLO=price_...              (from step 2, Solo)
LEMMA_STRIPE_PRICE_MULTI=price_...             (from step 2, Multi)
```

Save → Render redeploys automatically (~30 seconds).

## 6. Test it

1. Open `https://lemma-2b0h.onrender.com/lemma/pricing` — the "Coming soon" banner should be gone
2. Sign up as a test teacher
3. Click **Upgrade to Pro Solo →** — you land on a Stripe Checkout page
4. Use test card `4242 4242 4242 4242`, any future date, any 3-digit CVC
5. Complete payment — you're redirected back to `/lemma/me?upgrade=success`
6. The dashboard shows your plan as **Pro Solo**
7. In Stripe → **Customers** — verify a new customer record exists
8. In Stripe → **Webhooks** → click your endpoint → **Recent events** — see the events that fired and that they returned 200

If anything fails:
- Render logs: search for `Stripe error` or `webhook`
- Stripe → **Logs** (top right) — shows every API request you made and its response

## 7. Going live

When you're ready to take real money:

1. Stripe Dashboard top-right toggle: **Test mode** → **Live mode**
2. Activate the account — Stripe asks for tax info, business address, bank account for payouts
3. Re-create the two products + prices in live mode (Stripe doesn't carry test mode products to live)
4. Re-create the webhook endpoint in live mode
5. Generate new live API keys
6. Update the four env vars in Render with the live versions:
   - `sk_live_...` instead of `sk_test_...`
   - `whsec_...` (new live signing secret)
   - `price_...` (new live Price IDs)
7. Redeploy

That's it. The same code path handles both test and live — only the keys change.

## Costs

Stripe takes **2.9% + $0.30 per successful charge**. For a $15/mo Solo
subscription: Stripe takes $0.74, you net $14.26. For a $30 Multi: Stripe
takes $1.17, you net $28.83.

## Where pricing lives in code

If you want to change prices, **don't** change them in Stripe alone —
the Lemma pricing page reads from a constant in
`src/pep/routes/lemma_billing.py` called `TIERS`. Change the dollar
amount there to match whatever you set in Stripe.

```python
TIERS = {
    "solo": {..., "price_monthly_usd": 15, ...},
    "multi": {..., "price_monthly_usd": 30, ...},
}
OVERAGE_USD_PER_STUDENT_MONTH = 0.20
```

Push to GitHub → Render auto-deploys. Pricing page reflects the new
numbers within a minute.
