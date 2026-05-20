# Euclidia Site — Your Action Items

This is the consolidated list of things that need you (a human) rather than code edits, ranked by how much damage they prevent if you actually do them.

All items are **free** — no paid tools needed.

---

## HIGH IMPACT (do these soon)

### 1. Submit sitemap.xml to Google Search Console

I just created `sitemap.xml`. Google can find it on its own eventually, but submitting directly tells Google to crawl all 7 pages immediately and starts indexing them within hours instead of weeks. This is the single biggest discoverability action you can take.

**Steps:**
1. Go to https://search.google.com/search-console
2. Sign in with the Google account that owns euclidiamath.com
3. If you haven't added the property: click "Add property" → enter `https://euclidiamath.com` → verify via DNS or HTML file (use DNS, it's permanent)
4. Once verified, in the left sidebar click **Sitemaps**
5. In the "Add a new sitemap" field, type: `sitemap.xml`
6. Click **Submit**

You'll get a green "Success" status. Within 24-48 hours, Search Console will start showing which pages are being crawled and indexed.

While you're in Search Console, also click **Request indexing** for `https://euclidiamath.com/` — that's a one-shot "look at this now" signal.

### 2. Set up UptimeRobot monitor for the marketing site

You already have UptimeRobot configured for the SaaS app. Adding a monitor for the marketing site is a 2-minute addition.

**Steps:**
1. Log into https://uptimerobot.com
2. Click "Add New Monitor"
3. Monitor type: **HTTPS**, URL: `https://euclidiamath.com/`, interval: 5 minutes
4. Under "Alert Contacts to Notify", select your existing email contact (the same one you set up for the SaaS app)
5. Click **Create Monitor**

Now if the site ever goes down, you get an email immediately rather than finding out from a user.

### 3. Optimize your product thumbnail images

Your product images in `/images/` are currently 500-560 KB each. That's roughly 10x the optimized size. Compressing them gives faster page loads and lower bandwidth usage. No quality loss visible to the eye.

**Steps:**
1. Go to https://squoosh.app (free, runs in your browser, no upload to a server)
2. For each image in `/images/`:
   - Drag the image into Squoosh
   - On the right side, pick **WebP** format (or stick with PNG if you prefer)
   - Slide the quality to ~75
   - Click **Download**
3. Replace the original file in `/images/` with the compressed version
4. Update `products.json` to reference the new filenames if you changed extensions (e.g., `.png` → `.webp`)
5. Commit + push

Expect roughly 80-90% file size reduction.

### 4. Get one real teacher testimonial

Zero social proof is your biggest credibility gap. One real testimonial is worth more than every line of marketing copy on the site.

**Steps:**
1. Look at your Payhip sales (or TPT store reviews) and pick a teacher who left a positive comment or otherwise seemed happy
2. Email them: "Hey, I noticed you bought [X] — would you be willing to share a sentence about your experience for the homepage? Just your first name and what you teach (e.g., 'Sarah, 8th grade math, Texas') is enough"
3. Once they reply, ask me to add a "What Teachers Say" section to the homepage with their quote

If you don't have any past buyers to ask, send a free lesson bundle to a teacher friend in exchange for honest feedback you can quote.

---

## MEDIUM IMPACT (worth doing within a month or two)

### 5. Pick a free mailing list provider and set up a welcome email

Right now your three waitlist forms collect emails and dump them in your inbox with no follow-up. The retention problem from the evaluation. Fixing it gives you a real audience to talk to.

**Free options (pick one):**
- **Buttondown** (https://buttondown.com) — free up to 100 subscribers, simplest UI, my recommendation for getting started
- **MailerLite** (https://mailerlite.com) — free up to 1,000 subscribers, more features
- **ConvertKit** (https://convertkit.com) — free up to 10,000 subscribers, most powerful

**Steps once you've picked one:**
1. Sign up
2. Create a single welcome email that delivers a free lesson PDF or just thanks them and sets expectations ("You'll hear from me about once a month with a free lesson and any new launches")
3. Replace the web3forms action URL on your three waitlist forms with the mailing list provider's form endpoint (each one provides this in their settings)
4. Ask me to make the swap when you're ready

Once that's wired, you have an actual audience instead of cold leads in your inbox.

### 6. Grow the lesson catalog

The shop has 3 products. That's the inventory crisis from the evaluation. Until this is fixed, the shop will lose to TPT or any competitor on selection alone.

**Suggested approach:**
- Pick ONE Common Core strand (e.g., 8.EE.C) and saturate it — create lessons for every standard in that strand (8.EE.C.7a, 8.EE.C.7b, 8.EE.C.8a, 8.EE.C.8b, 8.EE.C.8c, etc.)
- Goal: get to 15-20 products in the next 3 months
- Becoming THE source for one strand is more valuable than scattered single lessons across many strands

The script (`python add_product.py`) makes adding each new product about 5 minutes once you have the lesson PDF + thumbnail + Payhip link ready.

### 7. Decide what to do with "Coming Soon" labels

The Generator and Outreach are both labeled "Coming Soon" on the homepage. Outreach should be flippable to live the moment Google verification clears (we're days/weeks away).

**Once Outreach is verified:**
- Ask me to flip the "Coming Soon" status to live on the homepage card
- Update the Outreach page to remove the waitlist form and replace it with a live "Sign in" CTA pointing to https://outreach.euclidiamath.com

**The Generator:**
- If you're months away from building it, consider de-emphasizing it on the homepage — it dilutes attention from the products you can actually sell
- Or commit to a launch date and start building

---

## LOW IMPACT BUT WORTH KNOWING

### 8. Self-host Google Fonts

Right now `styles.css` loads Playfair Display and DM Sans from Google's CDN. This adds latency and gives Google a tracking signal on every visitor. Self-hosting fixes both.

**Steps:**
1. Go to https://gwfh.mranftl.com/fonts (Google Webfonts Helper)
2. Search for "Playfair Display" → pick the weights you use (400, 600, 700, 900 + italic 600)
3. Download as .woff2 files, drop into a new `/fonts/` folder in the repo
4. Replace the Google Fonts `@import` line in styles.css with `@font-face` declarations pointing to the local files
5. Repeat for DM Sans

If you want me to do this conversion when you're ready, ask.

### 9. Consider a deploy safety gate

Right now any push to `main` immediately goes live. A single broken commit kills the site.

**Optional fix:** switch to a PR-based workflow:
1. Settings → Branches → Add rule: protect `main`, require PR before merging
2. From then on, you push to a branch, open a PR, review the diff, then merge to deploy

This adds 30 seconds per change but gives you a chance to catch obvious mistakes.

### 10. Optional: light mode toggle

Your dark theme is on-brand but the teacher audience tends to prefer light interfaces. Adding a light mode toggle would broaden comfort without changing brand identity.

This is a couple hours of CSS work. Ask if you want me to add it.

---

## LATER (when the site grows)

These don't matter much at current scale but will matter once you have 10+ lessons and growing traffic.

- **Individual product pages**: each lesson gets its own URL like `/lessons/laws-of-exponents.html`. Better for SEO and shareability than the current shop.html-with-JS-cards setup.
- **Pre-render shop products into shop.html** at deploy time so the products are in the initial HTML (better SEO than JS-rendered).
- **Move nav and footer from JS-injected to static HTML** in each page. Better SEO. Cost is duplication across 7 files.
- **Start a blog** with content like "5 ways to teach systems of equations" or "Common Core 8.EE strand breakdown." Content marketing drives organic traffic that's not brand-specific. Probably the highest-leverage long-term move once basics are in place.
- **Test the site on mobile** end-to-end. You may discover issues.

---

## Summary

If you only do four things from this list, do **1, 2, 3, and 4** above (Submit sitemap, UptimeRobot monitor, optimize images, get a testimonial). Together those address the largest fraction of the evaluation's damage ranking and they're all under 30 minutes apiece.
