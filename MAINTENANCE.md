# Euclidia Site — Maintenance Guide (for humans)

Last updated: 2026-05-19

This is the human-readable operations guide for the marketing site at euclidiamath.com. For the SaaS app (Euclidia Outreach), see the separate `gradebook_outreach` repo.

---

## What this site is, in one sentence

A static marketing + commerce site for the Euclidia brand, deployed via GitHub Pages, selling math lesson bundles (via Payhip) and marketing two upcoming products (the Generator and Euclidia Outreach).

---

## The 60-second mental model

- **Pure static site** — no build step, no server, no database
- **GitHub Pages** auto-deploys on push to main
- **Pages**: index, shop, generator, outreach, about, privacy, terms (7 total)
- **Shared parts** injected via JavaScript (nav.js handles the top nav + footer)
- **Product catalog** lives in `products.json` and is rendered client-side on shop.html
- **Form submissions** go to web3forms (free third-party form forwarder)
- **Payments** handled by Payhip (lesson bundles) and Stripe (eventually for Outreach subscriptions)

---

## Common task: add a new lesson product

The fastest path is the included Python script that does git push for you.

1. Open the project in GitHub Codespaces (or any environment with Python + git)
2. Make sure you have a Payhip link and a thumbnail image ready
3. Run: `python add_product.py`
4. Answer the questions one at a time
5. The script updates `products.json`, runs `build.py` (which regenerates the static shop, individual lesson pages, and sitemap), and pushes everything to GitHub
6. The product is live on the shop page within ~60 seconds (GitHub Pages deploy)

Full step-by-step is in `HOW_TO_ADD_PRODUCTS.md`.

---

## How the shop is built

The shop is a static site, but the product cards on `shop.html` and the
individual lesson pages under `lessons/` are **generated** from
`products.json` by `build.py`. This gives Google fully-rendered HTML
to index (instead of JS-rendered cards that crawlers see less reliably).

When you change `products.json` directly (instead of running
`add_product.py`), you must run `python build.py` afterward so the static
HTML reflects the new catalog. The GitHub Actions workflow also runs
`build.py` on every push as a safety net.

`build.py` is idempotent — running it twice in a row produces the same
output, and it removes lesson pages for products that no longer exist.

---

## Common task: deploy a manual change

GitHub Pages auto-deploys on every push to `main`. There's no separate deploy step. Just:

```bash
git add path/to/file.html
git commit -m "What changed"
git push
```

Wait ~60 seconds and check euclidiamath.com.

There is **no staging environment**. Every push to main goes straight to live. If you want a safety net, create a pull request first, review the diff, then merge.

---

## Where everything lives

**Pages (one HTML file per route):**
- `index.html` — homepage
- `shop.html` — lesson bundles catalog (renders products.json client-side)
- `generator.html` — Generator product page (currently "Coming Soon")
- `outreach.html` — Euclidia Outreach product page
- `about.html` — story + FAQ
- `privacy.html` — privacy policy
- `terms.html` — terms of service

**Shared assets:**
- `styles.css` — site-wide design system (colors, typography, components)
- `nav.js` — injects the top nav and footer into every page
- `main.js` — scroll reveal animation + nav background on scroll
- `fonts/` — self-hosted Playfair Display and DM Sans (.woff2 files, latin subset). Regenerate with `python regenerate_fonts.py` if you change which weights the site uses.

**SEO assets (recently added):**
- `robots.txt` — tells crawlers to index everything
- `sitemap.xml` — lists all 7 pages with priority + change frequency
- JSON-LD structured data is embedded in each page's `<head>` (Organization, WebSite, SoftwareApplication, FAQPage, etc.)

**Product catalog:**
- `products.json` — single source of truth for what's in the shop
- `images/` — product thumbnails and the favicon
- `add_product.py` — interactive script that adds a new product to products.json

**Deploy:**
- `.github/workflows/static.yml` — GitHub Pages auto-deploy on push to main
- `.github/workflows/claude.yml` — Claude Code action triggered by @claude mentions in issues
- `wrangler.jsonc` — Cloudflare Workers config (alternative deploy target; unclear if currently used. Safe to ignore unless you've actively switched to CF Workers.)

---

## Monthly health check

A 5-minute monthly routine. Habit-stack onto something you already do monthly.

1. Visit https://euclidiamath.com → page loads fast?
2. Click through all nav links → no broken pages?
3. Click "Browse Lessons" → products load on shop page?
4. Click a Payhip "Buy Now" link → Payhip product page loads?
5. Try submitting a waitlist email on the homepage → check your inbox for a forwarded copy from web3forms?
6. View page on a phone → mobile nav (hamburger) works?

If anything fails, the most common causes are: a broken commit, a Payhip link that changed, or a web3forms outage.

---

## Things that will break in predictable ways

- **A broken commit** kills the live site immediately (no staging gate)
- **web3forms outage** silently breaks all 3 waitlist forms (you won't be notified)
- **Payhip link changes** create broken "Buy Now" buttons on shop products. Re-check after any Payhip dashboard activity.
- **Domain (euclidiamath.com) renewal failure** = full site down. Set a calendar reminder.
- **GitHub Pages outage** = full site down. Rare.
- **Google Fonts CDN issues** = fonts fall back to system defaults. Visual change but not a break.

---

## What NOT to do without thinking carefully

- Do **not** delete `nav.js` or `main.js` — they're injected into every page
- Do **not** mess with `_products/` (it's been removed; if you re-create it, nothing references it)
- Do **not** push experimental changes directly to main without testing — there's no rollback besides a force-revert
- Do **not** add em-dashes to any copy. This is a hard brand rule (em-dashes are an AI tell)
- Do **not** check `wrangler.jsonc` into deploy unless you've intentionally switched to Cloudflare Workers — it's currently dormant config

---

## Settings up monitoring (recommended)

The site has no uptime monitoring right now. To set one up free:

1. Log into UptimeRobot (https://uptimerobot.com)
2. Click "Add New Monitor"
3. Type: HTTPS, URL: `https://euclidiamath.com/`, interval: 5 minutes
4. Add your email under "Alert Contacts to Notify"
5. Save

You'll get an email if the site is ever down. Free.

---

## When products break

The shop page reads `products.json` via client-side fetch and renders cards. If something looks wrong:

- **Product shows but with no thumbnail**: filename mismatch between `products.json` and `images/`. Check capitalization.
- **Product missing entirely**: check `products.json` syntax — a stray comma or unmatched quote breaks the whole file.
- **"Buy Now" button leads to 404**: Payhip URL is wrong or the Payhip product was deleted.
- **All products gone, error message showing**: `products.json` failed to load. Check the file exists and is valid JSON.

To validate `products.json` is well-formed, paste its contents into https://jsonlint.com.

---

## Where to ask for help

- For GitHub Pages deploy issues → GitHub repo Actions tab → check the latest workflow run
- For Payhip issues → Payhip dashboard
- For web3forms issues → https://web3forms.com (status page)
- For everything else → euclidiamath@gmail.com (you)
