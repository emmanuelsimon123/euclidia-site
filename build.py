#!/usr/bin/env python3
"""
Euclidia site build script.

Reads products.json and generates:

  1. Static product cards injected into shop.html (replaces the JS-rendered
     loading state with real cards Google can index).
  2. One individual lesson page per product at lessons/<slug>.html with
     Product JSON-LD schema, og tags, canonical URL.
  3. An updated sitemap.xml including all lesson pages.

Idempotent: run as often as you like. Called automatically by add_product.py
after a product is added, and by the GitHub Actions workflow before deploy.

Usage:
    python build.py
"""

import json
import os
import re
import sys
from datetime import date

PRODUCTS_FILE = "products.json"
SHOP_FILE = "shop.html"
SITEMAP_FILE = "sitemap.xml"
LESSONS_DIR = "lessons"

# Markers in shop.html that bracket the generated content.
SHOP_CONTAINER_START = "<!-- BUILD:PRODUCTS:START -->"
SHOP_CONTAINER_END = "<!-- BUILD:PRODUCTS:END -->"
SHOP_FILTERS_START = "<!-- BUILD:FILTERS:START -->"
SHOP_FILTERS_END = "<!-- BUILD:FILTERS:END -->"

# Sitemap is fully regenerated each build.
STATIC_PAGES = [
    ("https://euclidiamath.com/", "weekly", "1.0"),
    ("https://euclidiamath.com/shop.html", "weekly", "0.9"),
    ("https://euclidiamath.com/canvas-quiz.html", "weekly", "0.9"),
    ("https://euclidiamath.com/canvas-quiz-guide.html", "monthly", "0.7"),
    ("https://euclidiamath.com/outreach.html", "monthly", "0.8"),
    ("https://euclidiamath.com/generator.html", "monthly", "0.8"),
    ("https://euclidiamath.com/writing-grammar.html", "monthly", "0.8"),
    ("https://euclidiamath.com/about.html", "monthly", "0.7"),
    ("https://euclidiamath.com/privacy.html", "yearly", "0.3"),
    ("https://euclidiamath.com/terms.html", "yearly", "0.3"),
]


def html_escape(text):
    if text is None:
        return ""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    text = re.sub(r"-+", "-", text)
    return text


def product_slug(product):
    """Derive a URL slug for a product. Prefer the thumbnail filename
    if present (since it was already chosen by the author), else slugify
    the title."""
    thumb = product.get("thumbnail", "")
    if thumb:
        base = os.path.splitext(os.path.basename(thumb))[0]
        if base:
            return base
    return slugify(product.get("title", "lesson"))


def parse_price(price_str):
    """Extract a numeric price from strings like '$2.25'. Returns None
    for free products or unparseable strings."""
    if not price_str:
        return None
    m = re.search(r"(\d+\.\d{2})", str(price_str))
    if m:
        return float(m.group(1))
    return None


def grade_label(grade):
    """Render a grade tag. '7' -> 'Grade 7'; '6-8' -> 'Grades 6-8'."""
    grade = str(grade).strip()
    if not grade:
        return ""
    return f"Grades {grade}" if "-" in grade else f"Grade {grade}"


def build_card_html(product, slug):
    """Static product card. Same visual structure as the prior JS-rendered
    version, but title + thumbnail now link to the lesson page."""
    is_free = product.get("is_free") is True or product.get("is_free") == "true"
    title = html_escape(product.get("title", "Lesson Bundle"))
    description = html_escape(product.get("description", ""))
    standard = html_escape(product.get("standard", ""))
    grade = html_escape(product.get("grade", ""))
    price = html_escape(product.get("price", "$2.25"))
    tpt_price = html_escape(product.get("tpt_price", ""))
    buy_url = html_escape(product.get("buy_url", "#"))
    lesson_url = f"lessons/{slug}.html"

    thumb = product.get("thumbnail", "")
    if thumb:
        thumb_html = (
            f'<a href="{lesson_url}" aria-label="View {title}">'
            f'<img src="{html_escape(thumb)}" alt="{title} thumbnail" '
            f'class="product-thumb" loading="lazy">'
            f"</a>"
        )
    else:
        thumb_html = (
            f'<a href="{lesson_url}" aria-label="View {title}" '
            f'class="product-thumb-placeholder">'
            f"<span>Euclidia</span><p>{title}</p>"
            f"</a>"
        )

    if is_free:
        price_html = (
            '<div>'
            '<div class="product-price-main" style="color:#34d399;">FREE</div>'
            '<div class="product-price-note">Print-ready PDF</div>'
            '</div>'
        )
        btn_class = "btn-buy free"
        btn_text = "Download &uarr;"
    else:
        tpt_block = (
            f'<div class="product-price-tpt">{tpt_price}</div>' if tpt_price else ""
        )
        price_html = (
            '<div>'
            f'<div class="product-price-main">{price}</div>'
            f"{tpt_block}"
            '<div class="product-price-note">Print-ready PDF</div>'
            '</div>'
        )
        btn_class = "btn-buy"
        btn_text = "Buy now &uarr;"

    tags_attr = " ".join(product.get("tags", []))
    tag_chips = ""
    if standard:
        tag_chips += f'<span class="product-tag">{standard}</span>'
    if grade:
        tag_chips += f'<span class="product-tag grade">{grade_label(grade)}</span>'

    return (
        f'<div class="product-card" data-tags="{html_escape(tags_attr)}">'
        f"{thumb_html}"
        '<div class="product-body">'
        f'<div class="product-tags">{tag_chips}</div>'
        f'<a href="{lesson_url}" class="product-title-link">'
        f'<div class="product-title">{title}</div>'
        f"</a>"
        f'<div class="product-desc">{description}</div>'
        '<div class="product-includes">'
        "<span>&#128203; Lesson Plan</span>"
        "<span>&#128221; Worksheet</span>"
        "<span>&#9989; Answer Key</span>"
        "</div>"
        "</div>"
        '<div class="product-footer">'
        f"{price_html}"
        f'<a href="{buy_url}" class="{btn_class}" target="_blank" rel="noopener">{btn_text}</a>'
        "</div>"
        "</div>"
    )


def build_filter_buttons(products):
    """Pre-rendered filter buttons. All Resources is always first and active."""
    tags = set()
    for p in products:
        for t in p.get("tags", []):
            t = t.strip()
            if t:
                tags.add(t)
    sorted_tags = sorted(tags)
    buttons = (
        '<button class="filter-btn active" data-filter="all" '
        'onclick="filterProducts(this,\'all\')">All Resources</button>'
    )
    for t in sorted_tags:
        buttons += (
            f'<button class="filter-btn" data-filter="{html_escape(t)}" '
            f"onclick=\"filterProducts(this,'{html_escape(t)}')\">{html_escape(t)}</button>"
        )
    return buttons


def replace_marked_section(source, start_marker, end_marker, replacement):
    pattern = re.compile(
        re.escape(start_marker) + r".*?" + re.escape(end_marker), re.DOTALL
    )
    new_section = f"{start_marker}\n{replacement}\n{end_marker}"
    if pattern.search(source):
        return pattern.sub(new_section, source)
    raise RuntimeError(
        f"Markers not found in source: {start_marker}...{end_marker}. "
        "shop.html may need to be updated to include them."
    )


def update_shop_html(products):
    with open(SHOP_FILE, "r", encoding="utf-8") as f:
        source = f.read()

    cards = "\n".join(build_card_html(p, product_slug(p)) for p in products)
    if products:
        cards_block = f'<div class="product-grid">\n{cards}\n</div>'
    else:
        cards_block = (
            '<div class="empty-state">'
            "<h3>Products coming soon</h3>"
            "<p>Check back shortly. Resources are being added now.</p>"
            "</div>"
        )

    source = replace_marked_section(
        source, SHOP_CONTAINER_START, SHOP_CONTAINER_END, cards_block
    )
    source = replace_marked_section(
        source,
        SHOP_FILTERS_START,
        SHOP_FILTERS_END,
        build_filter_buttons(products),
    )

    with open(SHOP_FILE, "w", encoding="utf-8") as f:
        f.write(source)


LESSON_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | Euclidia</title>
<meta name="description" content="{meta_desc}">
<meta property="og:title" content="{title} | Euclidia">
<meta property="og:description" content="{meta_desc}">
<meta property="og:url" content="https://euclidiamath.com/lessons/{slug}.html">
<meta property="og:type" content="product">
<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="https://euclidiamath.com/lessons/{slug}.html">
<link rel="icon" type="image/svg+xml" href="/images/favicon.svg">
<link rel="stylesheet" href="/styles.css">
<script type="application/ld+json">
{json_ld}
</script>
<style>
main {{ max-width: 980px; margin: 0 auto; padding: 120px 24px 80px; width: 100%; position: relative; z-index: 1; }}
.lesson-eyebrow {{ font-size: 0.8rem; font-weight: 500; color: var(--gold); letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 1rem; }}
.lesson-title {{ font-family: 'Playfair Display', serif; font-size: 2.4rem; font-weight: 700; color: var(--white); line-height: 1.2; margin-bottom: 1rem; }}
.lesson-meta {{ display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 2rem; }}
.lesson-chip {{ font-size: 12px; font-weight: 600; background: var(--gold-pale); border: 1px solid var(--gold-border); color: var(--gold); padding: 4px 12px; border-radius: 6px; }}
.lesson-chip.grade {{ background: rgba(27,58,107,0.3); border-color: rgba(27,58,107,0.5); color: #93b4d4; }}
.gold-rule {{ width: 48px; height: 2px; background: var(--gold); margin-bottom: 2rem; }}
.lesson-grid {{ display: grid; grid-template-columns: 1fr 360px; gap: 40px; align-items: start; }}
.lesson-thumb {{ width: 100%; border-radius: var(--radius-lg); border: 1px solid var(--border); }}
.lesson-desc {{ font-size: 1.05rem; line-height: 1.7; color: var(--text); margin-bottom: 2rem; }}
.lesson-includes {{ background: var(--card-bg); border: 1px solid var(--border); border-radius: var(--radius); padding: 24px; margin-bottom: 2rem; }}
.lesson-includes h3 {{ font-family: 'Playfair Display', serif; font-size: 1.1rem; color: var(--white); margin-bottom: 12px; }}
.lesson-includes ul {{ list-style: none; padding: 0; margin: 0; }}
.lesson-includes li {{ font-size: 0.95rem; color: var(--text); padding: 6px 0; }}
.lesson-buy-card {{ position: sticky; top: 100px; background: var(--card-bg); border: 1px solid var(--gold-border); border-radius: var(--radius-lg); padding: 28px; }}
.lesson-buy-price {{ font-family: 'Playfair Display', serif; font-size: 2.4rem; font-weight: 900; color: var(--gold); line-height: 1; margin-bottom: 4px; }}
.lesson-buy-price.free {{ color: #34d399; }}
.lesson-buy-tpt {{ font-size: 13px; color: var(--text-dim); text-decoration: line-through; margin-bottom: 4px; }}
.lesson-buy-note {{ font-size: 12px; color: var(--text-dim); margin-bottom: 20px; }}
.lesson-buy-btn {{ background: var(--gold); color: var(--navy); padding: 14px 22px; border-radius: 8px; font-size: 15px; font-weight: 700; text-decoration: none; display: block; text-align: center; transition: all 0.2s; }}
.lesson-buy-btn.free {{ background: #34d399; }}
.lesson-buy-btn:hover {{ background: var(--gold-light); transform: translateY(-1px); }}
.lesson-back {{ display: inline-block; margin-top: 3rem; color: var(--gold); text-decoration: none; font-size: 0.95rem; }}
.lesson-back:hover {{ text-decoration: underline; }}
@media (max-width: 768px) {{ .lesson-grid {{ grid-template-columns: 1fr; }} .lesson-title {{ font-size: 1.8rem; }} main {{ padding: 104px 20px 64px; }} .lesson-buy-card {{ position: static; }} }}
</style>
</head>
<body data-page="">

<a href="#main" class="skip-link">Skip to main content</a>

<main id="main">

  <div class="lesson-eyebrow">Lesson Bundle</div>
  <h1 class="lesson-title">{title}</h1>
  <div class="lesson-meta">{chips}</div>
  <div class="gold-rule"></div>

  <div class="lesson-grid">
    <div>
      {thumb_block}
      <div class="lesson-desc">{description}</div>
      <div class="lesson-includes">
        <h3>What's included</h3>
        <ul>
          <li>&#128203; Teacher lesson plan (print-ready PDF)</li>
          <li>&#128221; Scaffolded student worksheet</li>
          <li>&#9989; Detailed answer key with misconception alerts</li>
        </ul>
      </div>
    </div>

    <div>
      <div class="lesson-buy-card">
        {price_block}
        <a href="{buy_url}" class="lesson-buy-btn{btn_modifier}" target="_blank" rel="noopener">{btn_text}</a>
      </div>
    </div>
  </div>

  <a href="/shop.html" class="lesson-back">&larr; Back to all lessons</a>

</main>

<script src="/nav.js"></script>
<script src="/main.js"></script>
</body>
</html>
"""


def build_lesson_page(product):
    slug = product_slug(product)
    title = product.get("title", "Lesson Bundle")
    description = product.get("description", "")
    standard = product.get("standard", "")
    grade = product.get("grade", "")
    price = product.get("price", "$2.25")
    tpt_price = product.get("tpt_price", "")
    buy_url = product.get("buy_url", "#")
    thumb = product.get("thumbnail", "")
    is_free = product.get("is_free") is True or product.get("is_free") == "true"

    # JSON-LD Product schema
    schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": title,
        "description": description,
        "url": f"https://euclidiamath.com/lessons/{slug}.html",
        "brand": {"@type": "Brand", "name": "Euclidia"},
    }
    if thumb:
        schema["image"] = f"https://euclidiamath.com/{thumb}"
    if standard:
        schema["educationalAlignment"] = {
            "@type": "AlignmentObject",
            "alignmentType": "teaches",
            "educationalFramework": "Common Core State Standards",
            "targetName": standard,
        }
    price_value = parse_price(price)
    if is_free:
        schema["offers"] = {
            "@type": "Offer",
            "price": "0.00",
            "priceCurrency": "USD",
            "availability": "https://schema.org/InStock",
            "url": buy_url,
        }
    elif price_value is not None:
        schema["offers"] = {
            "@type": "Offer",
            "price": f"{price_value:.2f}",
            "priceCurrency": "USD",
            "availability": "https://schema.org/InStock",
            "url": buy_url,
        }

    chips = ""
    if standard:
        chips += f'<span class="lesson-chip">{html_escape(standard)}</span>'
    if grade:
        chips += f'<span class="lesson-chip grade">{grade_label(html_escape(grade))}</span>'

    if thumb:
        thumb_block = (
            f'<img src="/{html_escape(thumb)}" alt="{html_escape(title)} thumbnail" '
            'class="lesson-thumb">'
        )
    else:
        thumb_block = ""

    if is_free:
        price_block = (
            '<div class="lesson-buy-price free">FREE</div>'
            '<div class="lesson-buy-note">Print-ready PDF &middot; instant download</div>'
        )
        btn_modifier = " free"
        btn_text = "Download free &rarr;"
    else:
        tpt_block = (
            f'<div class="lesson-buy-tpt">{html_escape(tpt_price)} on TPT</div>'
            if tpt_price
            else ""
        )
        price_block = (
            f'<div class="lesson-buy-price">{html_escape(price)}</div>'
            f"{tpt_block}"
            '<div class="lesson-buy-note">Print-ready PDF &middot; instant download</div>'
        )
        btn_modifier = ""
        btn_text = "Buy on Payhip &rarr;"

    og_image = (
        f"https://euclidiamath.com/{thumb}"
        if thumb
        else "https://euclidiamath.com/images/og-image.png"
    )

    return slug, LESSON_TEMPLATE.format(
        title=html_escape(title),
        slug=slug,
        meta_desc=html_escape(description),
        og_image=html_escape(og_image),
        json_ld=json.dumps(schema, indent=2),
        chips=chips,
        thumb_block=thumb_block,
        description=html_escape(description),
        price_block=price_block,
        buy_url=html_escape(buy_url),
        btn_modifier=btn_modifier,
        btn_text=btn_text,
    )


def write_lesson_pages(products):
    os.makedirs(LESSONS_DIR, exist_ok=True)
    existing = {f for f in os.listdir(LESSONS_DIR) if f.endswith(".html")}
    written = set()
    for product in products:
        slug, html = build_lesson_page(product)
        path = os.path.join(LESSONS_DIR, f"{slug}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        written.add(f"{slug}.html")
        print(f"  wrote {path}")

    # Remove stale lesson pages from deleted products
    for stale in existing - written:
        stale_path = os.path.join(LESSONS_DIR, stale)
        os.remove(stale_path)
        print(f"  removed stale {stale_path}")


def write_sitemap(products):
    today = date.today().isoformat()
    urls = list(STATIC_PAGES)
    for product in products:
        slug = product_slug(product)
        urls.append((f"https://euclidiamath.com/lessons/{slug}.html", "monthly", "0.6"))

    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for loc, changefreq, priority in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{loc}</loc>")
        lines.append(f"    <lastmod>{today}</lastmod>")
        lines.append(f"    <changefreq>{changefreq}</changefreq>")
        lines.append(f"    <priority>{priority}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")

    with open(SITEMAP_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"  wrote {SITEMAP_FILE} ({len(urls)} URLs)")


def main():
    if not os.path.exists(PRODUCTS_FILE):
        print(f"ERROR: {PRODUCTS_FILE} not found")
        sys.exit(1)

    with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
        products = json.load(f)

    print(f"Building site from {len(products)} product(s)...")

    print("Updating shop.html...")
    update_shop_html(products)

    print("Writing lesson pages...")
    write_lesson_pages(products)

    print("Updating sitemap.xml...")
    write_sitemap(products)

    print("Done.")


if __name__ == "__main__":
    main()
