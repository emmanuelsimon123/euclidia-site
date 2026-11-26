#!/usr/bin/env python3
"""
Curriculum pages: every Euclidia TPT listing, organized course > unit > lesson.

Reads data/catalog.json (built in the lesson-plan-generator repo by
course_plans/website_catalog/build_catalog.py from the live TPT store) and writes:

  curriculum/<course>.html            one page per full-year course
  curriculum/<course>/unit-<n>.html   one page per unit, every lesson with its links
  curriculum/catalog.json             compact list for the filter on shop.html

Every Buy link goes to the TPT listing (lessons are sold only on TPT).
Called by build.py. Zero dependencies.
"""

import html
import json
import os
from urllib.parse import urlencode

DATA_FILE = os.path.join("data", "catalog.json")
OUT_DIR = "curriculum"
SITE = "https://euclidiamath.com"

KIND_LABEL = {
    "notes": "Guided Notes",
    "worksheet": "Worksheet",
    "pair": "Notes + Worksheet",
    "bundle": "Bundle",
    "unit_test": "Unit Test",
    "full_year": "Full Year",
    "guide": "Pacing Guide",
    "sub_plans": "Sub Plans",
    "bell_ringers": "Bell Ringers",
    "exam": "Exam",
    "other": "Resource",
}


# Grade levels, as the listings are tagged on TPT (high school listings are tagged 9th to 12th as one group)
COURSE_GRADES = {
    "grade6": ["6th grade"],
    "grade7": ["7th grade"],
    "grade8": ["8th grade"],
    "prealgebra": ["7th grade", "8th grade"],
}
GRADE_LABEL = {"grade6": "6th grade", "grade7": "7th grade", "grade8": "8th grade", "prealgebra": "7th and 8th grade"}
GRADE_BAND = {"grade6": "middle", "grade7": "middle", "grade8": "middle", "prealgebra": "middle"}


def esc(text):
    return html.escape(str(text), quote=True)


def tpt_link(item, place):
    """TPT URL with tracking tags so TPT's traffic report shows website clicks."""
    q = urlencode({"utm_source": "euclidiamath", "utm_medium": "website", "utm_campaign": place})
    return f"{item['url']}?{q}"


def price_text(item):
    p = item.get("price")
    if p is None:
        return ""
    return "Free" if p == 0 else f"${p:,.2f}"


def head(title, desc, path, extra_ld=None):
    ld = ""
    if extra_ld:
        ld = '<script type="application/ld+json">\n' + json.dumps(extra_ld, ensure_ascii=False, indent=1) + "\n</script>"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)} | Euclidia</title>
<meta name="description" content="{esc(desc)}">
<meta property="og:title" content="{esc(title)} | Euclidia">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{SITE}/{path}">
<meta property="og:type" content="website">
<link rel="canonical" href="{SITE}/{path}">
<link rel="icon" type="image/svg+xml" href="/images/favicon.svg">
<link rel="stylesheet" href="/styles.css">
<link rel="stylesheet" href="/curriculum.css">
{ld}
</head>
<body data-page="shop">
<a href="#main" class="skip-link">Skip to main content</a>
<main id="main" class="cur-main">
"""


FOOT = """
</main>
<script src="/nav.js"></script>
<script src="/main.js"></script>
</body>
</html>
"""


def buy_button(item, label, place, cls="cur-btn"):
    if not item:
        return ""
    pt = price_text(item)
    return (f'<a class="{cls}" href="{esc(tpt_link(item, place))}" target="_blank" rel="noopener">'
            f'{esc(label)}<span>{esc(pt)}</span></a>')


def course_path(course):
    return f"curriculum/{course['slug']}.html"


def unit_path(course, unit):
    return f"curriculum/{course['slug']}/unit-{unit['num']}.html"


def unit_lessons(u):
    return u.get("lesson_count", len(u["lessons"]))


def lesson_count(course):
    return sum(unit_lessons(u) for u in course["units"])


def unit_href(course, u):
    ref = u.get("ref")
    if ref:
        return f"/curriculum/{ref['course_slug']}/unit-{ref['unit']}.html"
    return f"/{unit_path(course, u)}"


def is_topic_group(course):
    return course.get("full_year") is None and not any(u.get("test") for u in course["units"])


def course_page(course):
    n = lesson_count(course)
    nu = len(course["units"])
    fy = course.get("full_year")
    guide = next((x for x in course["extras"] if x["kind"] == "guide"), None)
    topics = is_topic_group(course)
    if topics:
        lead = (f"{n} lessons in {nu} groups. Each lesson has two parts: Guided Notes with Teacher Notes, "
                f"and a Worksheet with a worked answer key.")
    else:
        lead = (f"{n} lessons in {nu} units. Each lesson has two parts: Guided Notes with Teacher Notes, "
                f"and a Worksheet with a worked answer key. Every unit ends with a review and a unit test.")
        if any(u.get("ref") for u in course["units"]):
            lead += " Units 2 to 11 are the same units as in 7th and 8th grade, so their links open those pages."
    desc = f"{course['name']}: {lead}"
    ld = {"@context": "https://schema.org", "@type": "ItemList", "name": f"{course['name']} units",
          "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": f"Unit {u['num']}: {u['name']}",
                               "url": SITE + unit_href(course, u)} for i, u in enumerate(course["units"])]}
    title = (f"{course['name']} Lessons: Guided Notes and Worksheets" if topics
             else f"{course['name']} Curriculum: {n} Lessons, Unit Tests")
    out = [head(title, desc, course_path(course), ld)]
    out.append(f'<p class="cur-eyebrow"><a href="/shop.html">All courses</a> / {esc(course["name"])}</p>')
    out.append(f'<h1 class="cur-title">{esc(course["name"])}</h1>')
    out.append(f'<p class="cur-lead">{esc(lead)}</p>')
    out.append('<div class="cur-buybar">')
    if fy:
        lp = fy.get("list_price")
        save = f' <em>(${lp:,.0f} if bought one by one)</em>' if lp and fy.get("price") and lp > fy["price"] else ""
        out.append(f'<div class="cur-buycard"><h2>The whole year</h2><p>All {n} lessons, every unit review and test, '
                   f'and the pacing guide.{save}</p>{buy_button(fy, "Full year on TPT", "course-" + course["slug"], "cur-btn cur-btn-gold")}</div>')
    if guide:
        out.append(f'<div class="cur-buycard"><h2>Pacing guide</h2><p>The year at a glance, unit by unit and day by day.</p>'
                   f'{buy_button(guide, "Free on TPT", "course-" + course["slug"])}</div>')
    out.append("</div>")
    out.append(f'<h2 class="cur-h2">{"Topics" if topics else "Units"}</h2><ol class="cur-units">')
    for u in course["units"]:
        ub = u.get("bundle")
        label = "" if topics else f"Unit {u['num']}"
        meta = f"{unit_lessons(u)} lessons"
        if u.get("ref"):
            meta += f" · {u['ref']['course_name']} Unit {u['ref']['unit']}"
        elif u.get("note"):
            meta += f" · {u['note']}"
        out.append(f'<li class="cur-unit"><a class="cur-unit-link" href="{unit_href(course, u)}">'
                   f'<span class="cur-unit-num">{esc(label)}</span><span class="cur-unit-name">{esc(u["name"])}</span>'
                   f'<span class="cur-unit-meta">{esc(meta)}</span></a>'
                   f'{buy_button(ub, "Unit bundle", "course-" + course["slug"], "cur-btn cur-btn-small") if ub else ""}</li>')
    out.append("</ol>")
    extras = [x for x in course["extras"] if x["kind"] != "guide"]
    if extras:
        out.append(f'<h2 class="cur-h2">More for {esc(course["name"])}</h2>')
        out.append(extras_list(extras, "course-" + course["slug"]))
    out.append(FOOT)
    return "".join(out)


def extras_list(items, place):
    groups = {}
    for x in items:
        groups.setdefault(KIND_LABEL.get(x["kind"], "Resource"), []).append(x)
    out = ['<div class="cur-extras">']
    for label in sorted(groups):
        out.append(f'<details class="cur-group"><summary>{esc(label)} <span>({len(groups[label])})</span></summary><ul>')
        for x in groups[label]:
            out.append(f'<li><a href="{esc(tpt_link(x, place))}" target="_blank" rel="noopener">{esc(x["title"])}</a>'
                       f'<span class="cur-price">{esc(price_text(x))}</span></li>')
        out.append("</ul></details>")
    out.append("</div>")
    return "".join(out)


def unit_page(course, unit, prev_u, next_u):
    place = f"{course['slug']}-unit-{unit['num']}"
    n = len(unit["lessons"])
    desc = (f"{course['name']} Unit {unit['num']}: {unit['name']}. {n} lessons, each with Guided Notes and a "
            f"Worksheet with answer key, plus a unit review and test.")
    items = []
    for l in unit["lessons"]:
        for x in (l["notes"], l["worksheet"], l["pair"]):
            if x:
                items.append(x)
    ld = {"@context": "https://schema.org", "@type": "ItemList", "name": f"{course['name']} Unit {unit['num']}: {unit['name']}",
          "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": l["name"]}
                              for i, l in enumerate(unit["lessons"])]}
    topics = is_topic_group(course)
    h1 = f"{course['name']}: {unit['name']}" if topics else f"Unit {unit['num']}: {unit['name']}"
    crumb = unit["name"] if topics else f"Unit {unit['num']}"
    out = [head(f"{course['name']} Unit {unit['num']}: {unit['name']}" if not topics else h1, desc, unit_path(course, unit), ld)]
    out.append(f'<p class="cur-eyebrow"><a href="/shop.html">All courses</a> / '
               f'<a href="/{course_path(course)}">{esc(course["name"])}</a> / {esc(crumb)}</p>')
    out.append(f'<h1 class="cur-title">{esc(h1)}</h1>')
    choice = "Buy one part, or both parts together." if topics or not unit.get("bundle") else \
        "Buy one part, both parts together, or the whole unit."
    note = f" A {unit['note']}." if unit.get("note") else ""
    out.append(f'<p class="cur-lead">{n} lessons.{esc(note)} Each lesson has Guided Notes with Teacher Notes and a Worksheet '
               f'with a worked answer key. {choice}</p>')
    cards = []
    if unit.get("bundle"):
        cards.append(f'<div class="cur-buycard"><h2>The whole unit</h2><p>All {n} lessons with the unit review and test.</p>'
                     f'{buy_button(unit["bundle"], "Unit bundle on TPT", place, "cur-btn cur-btn-gold")}</div>')
    if unit.get("test"):
        cards.append(f'<div class="cur-buycard"><h2>Unit review and test</h2><p>A review and a test with answer keys.</p>'
                     f'{buy_button(unit["test"], "Review and test", place)}</div>')
    for b in unit.get("bundles", []):
        cards.append(f'<div class="cur-buycard"><h2>Bundle</h2><p>{esc(b["title"])}</p>'
                     f'{buy_button(b, "Bundle on TPT", place)}</div>')
    if cards:
        out.append('<div class="cur-buybar">' + "".join(cards) + "</div>")
    out.append('<h2 class="cur-h2">Lessons</h2><ol class="cur-lessons">')
    for l in unit["lessons"]:
        out.append(f'<li class="cur-lesson"><div class="cur-lesson-name"><span class="cur-lesson-num">{esc(l["num"])}</span>'
                   f'{esc(l["name"])}</div><div class="cur-lesson-buy">'
                   f'{buy_button(l["notes"], "Guided Notes", place, "cur-btn cur-btn-small")}'
                   f'{buy_button(l["worksheet"], "Worksheet", place, "cur-btn cur-btn-small")}'
                   f'{buy_button(l["pair"], "Both", place, "cur-btn cur-btn-small cur-btn-gold")}</div></li>')
    out.append("</ol>")
    nav = ['<div class="cur-pager" role="navigation" aria-label="Units">']
    if prev_u:
        nav.append(f'<a href="{unit_href(course, prev_u)}">&larr; {esc(prev_u["name"])}</a>')
    nav.append(f'<a href="/{course_path(course)}">All of {esc(course["name"])}</a>')
    if next_u:
        nav.append(f'<a href="{unit_href(course, next_u)}">{esc(next_u["name"])} &rarr;</a>')
    nav.append("</div>")
    out.append("".join(nav))
    out.append(FOOT)
    return "".join(out)


def write_shop_cards(cat, shop="shop.html"):
    start, end = "<!-- BUILD:COURSES:START -->", "<!-- BUILD:COURSES:END -->"
    with open(shop, encoding="utf-8") as f:
        src = f.read()
    if start not in src or end not in src:
        print("  shop.html has no course markers; skipping cards")
        return
    cards = []
    for band, title in (("middle", "Middle school: 6th, 7th and 8th grade"), ("high", "High school: 9th to 12th grade")):
        cards.append(f'<h3 class="cur-band">{esc(title)}</h3><div class="cur-courses">')
        for c in cat["courses"]:
            if (GRADE_BAND.get(c["key"]) or "high") != band:
                continue
            n = lesson_count(c)
            fy = c.get("full_year")
            price = f"Full year {price_text(fy)} on TPT" if fy else "Single lessons and bundles"
            what = (f"{n} lessons, {len(c['units'])} units" if not is_topic_group(c) else f"{n} lessons")
            cards.append(f'<a class="cur-course" href="/{course_path(c)}"><span class="cur-course-grade">'
                         f'{esc(GRADE_LABEL.get(c["key"], "High school"))}</span><h3>{esc(c["name"])}</h3>'
                         f'<p>{esc(what)}</p><p>{esc(price)}</p><span class="cur-course-go">See every lesson &rarr;</span></a>')
        cards.append("</div>")
    i, j = src.index(start) + len(start), src.index(end)
    src = src[:i] + "\n" + "".join(cards) + "\n" + src[j:]
    with open(shop, "w", encoding="utf-8") as f:
        f.write(src)


def filter_rows(cat):
    rows, seen = [], set()

    def add(x, course, unit=None, lesson=None):
        if not x or x["id"] in seen:
            return
        seen.add(x["id"])
        rows.append({"t": x["title"], "u": tpt_link(x, "shop-filter"), "p": price_text(x), "k": x["kind"],
                     "c": course, "n": unit, "g": grades})

    for c in cat["courses"]:
        grades = COURSE_GRADES.get(c["key"], ["High school"])
        add(c.get("full_year"), c["name"])
        for u in c["units"]:
            add(u.get("bundle"), c["name"], u["num"])
            add(u.get("test"), c["name"], u["num"])
            for b in u.get("bundles", []):
                add(b, c["name"])
            for l in u["lessons"]:
                for x in (l["notes"], l["worksheet"], l["pair"]):
                    add(x, c["name"], u["num"])
        for x in c["extras"]:
            add(x, c["name"])
    names = {"prealgebra": "Pre-Algebra", "hs_extra": "High School", "other": "Other"}
    grades = ["High school"]
    for k, items in cat.get("more", {}).items():
        for x in items:
            add(x, names.get(k, k))
    return rows


def build():
    """Write every curriculum page; return sitemap entries."""
    if not os.path.exists(DATA_FILE):
        print(f"  {DATA_FILE} not found; skipping curriculum pages")
        return []
    with open(DATA_FILE, encoding="utf-8") as f:
        cat = json.load(f)
    urls = []
    os.makedirs(OUT_DIR, exist_ok=True)
    for course in cat["courses"]:
        os.makedirs(os.path.join(OUT_DIR, course["slug"]), exist_ok=True)
        with open(course_path(course), "w", encoding="utf-8") as f:
            f.write(course_page(course))
        urls.append((f"{SITE}/{course_path(course)}", "weekly", "0.8"))
        units = course["units"]
        for i, u in enumerate(units):
            if u.get("ref"):
                continue  # Pre-Algebra units 2 to 11 are 7th and 8th grade units: link, no copy
            with open(unit_path(course, u), "w", encoding="utf-8") as f:
                f.write(unit_page(course, u, units[i - 1] if i else None, units[i + 1] if i + 1 < len(units) else None))
            urls.append((f"{SITE}/{unit_path(course, u)}", "weekly", "0.7"))
    write_shop_cards(cat)
    rows = filter_rows(cat)
    with open(os.path.join(OUT_DIR, "catalog.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, separators=(",", ":"))
    print(f"  wrote {len(cat['courses'])} course pages, {len(urls) - len(cat['courses'])} unit pages, "
          f"{len(rows)} catalog rows")
    return urls


if __name__ == "__main__":
    build()
