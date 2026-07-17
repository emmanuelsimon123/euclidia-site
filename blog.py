"""
Euclidia blog builder — zero dependencies (Python stdlib only), zero cost.

You write each post as a Markdown file in posts/.  Running the site build
(python build.py) turns every posts/*.md into a styled static HTML page under
blog/, rebuilds the blog index (blog.html), and adds them to the sitemap.

  posts/my-post.md   ->   blog/my-post.html   (+ a card on blog.html)

Static HTML is deliberate: it is what search engines actually read, which is
the whole point of a blog (be found when a teacher searches a math/teaching
question).  No CMS, no JavaScript rendering, no monthly fee.

A post file looks like this:

    title: Making Math Class Actually Fun
    date: 2026-08-15
    description: One sentence for the index card and Google.
    ---
    Your post, written in Markdown.

    ## A heading

    A paragraph with **bold**, *italic*, a [link](https://example.com),
    and a list:

    - point one
    - point two

Supported Markdown: # ## ### headings, **bold**, *italic*, `code`,
[links](url), ![images](src), - and 1. lists, > quotes, ``` code blocks,
and --- horizontal rules.  That covers everything a teaching post needs.
"""
import os
import re
import html
from datetime import date

POSTS_DIR = "posts"
BLOG_DIR = "blog"
BLOG_INDEX = "blog.html"

# reuse the founder's existing free web3forms key (same one the old waitlist
# used) so email signups cost nothing and just email him each subscriber
WEB3FORMS_KEY = "c8ebcae4-1442-4218-82d6-7b482f62f42a"


# ------------------------------------------------------------------ markdown
def _inline(text):
    """Inline Markdown -> HTML on already-HTML-escaped text.

    Order matters: pull code / images / links out into placeholders first so
    bold/italic can't mangle a URL that contains * or _, then restore them."""
    stash = []

    def _stash(html_fragment):
        stash.append(html_fragment)
        return f"\x00{len(stash) - 1}\x00"

    # inline code `...`
    text = re.sub(r"`([^`]+)`", lambda m: _stash(f"<code>{m.group(1)}</code>"), text)
    # images ![alt](src)
    text = re.sub(
        r"!\[([^\]]*)\]\(([^)\s]+)\)",
        lambda m: _stash(f'<img src="{m.group(2)}" alt="{m.group(1)}" loading="lazy">'),
        text,
    )
    # links [text](url) — bold/italic inside the link text is applied after restore,
    # so keep the raw text here and format the whole string below
    text = re.sub(
        r"\[([^\]]+)\]\(([^)\s]+)\)",
        lambda m: _stash(f'<a href="{m.group(2)}">{m.group(1)}</a>'),
        text,
    )
    # bold then italic (bold first so ** is not eaten by the single-* rule)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__([^_]+)__", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"(?<!\w)_([^_]+)_(?!\w)", r"<em>\1</em>", text)

    for i, frag in enumerate(stash):
        text = text.replace(f"\x00{i}\x00", frag)
    return text


def md_to_html(md):
    """Minimal, safe block-level Markdown -> HTML (stdlib only)."""
    lines = md.replace("\r\n", "\n").split("\n")
    out = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()

        # blank line
        if not stripped:
            i += 1
            continue

        # fenced code block ```
        if stripped.startswith("```"):
            i += 1
            code = []
            while i < n and not lines[i].strip().startswith("```"):
                code.append(html.escape(lines[i]))
                i += 1
            i += 1  # skip closing fence
            out.append("<pre><code>" + "\n".join(code) + "</code></pre>")
            continue

        # horizontal rule
        if re.fullmatch(r"(-{3,}|\*{3,})", stripped):
            out.append("<hr>")
            i += 1
            continue

        # heading
        m = re.match(r"(#{1,4})\s+(.*)", stripped)
        if m:
            level = len(m.group(1))
            out.append(f"<h{level}>{_inline(html.escape(m.group(2).strip()))}</h{level}>")
            i += 1
            continue

        # blockquote (consecutive > lines)
        if stripped.startswith(">"):
            quote = []
            while i < n and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip()[1:].strip())
                i += 1
            body = _inline(html.escape(" ".join(quote)))
            out.append(f"<blockquote><p>{body}</p></blockquote>")
            continue

        # unordered list
        if re.match(r"[-*]\s+", stripped):
            items = []
            while i < n and re.match(r"[-*]\s+", lines[i].strip()):
                items.append(re.sub(r"^[-*]\s+", "", lines[i].strip()))
                i += 1
            lis = "".join(f"<li>{_inline(html.escape(it))}</li>" for it in items)
            out.append(f"<ul>{lis}</ul>")
            continue

        # ordered list
        if re.match(r"\d+\.\s+", stripped):
            items = []
            while i < n and re.match(r"\d+\.\s+", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                i += 1
            lis = "".join(f"<li>{_inline(html.escape(it))}</li>" for it in items)
            out.append(f"<ol>{lis}</ol>")
            continue

        # paragraph (gather until blank line or a block starter)
        para = []
        while i < n and lines[i].strip() and not re.match(
            r"(#{1,4}\s|[-*]\s|\d+\.\s|>|```|-{3,}$|\*{3,}$)", lines[i].strip()
        ):
            para.append(lines[i].strip())
            i += 1
        out.append(f"<p>{_inline(html.escape(' '.join(para)))}</p>")

    return "\n".join(out)


# ------------------------------------------------------------------ post model
def parse_post(path):
    """Read a posts/*.md file -> dict(title, date, description, slug, html, words)."""
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    meta = {"title": "", "date": "", "description": ""}
    body = raw
    if "\n---" in raw or raw.lstrip().startswith(("title:", "date:", "description:")):
        # split frontmatter (key: value lines) at the first line that is only ---
        parts = re.split(r"(?m)^---\s*$", raw, maxsplit=1)
        if len(parts) == 2:
            head, body = parts
            for line in head.strip().split("\n"):
                if ":" in line:
                    k, _, v = line.partition(":")
                    if k.strip() in meta:
                        meta[k.strip()] = v.strip()
    slug = os.path.splitext(os.path.basename(path))[0].lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    words = len(re.findall(r"\w+", body))
    return {
        "title": meta["title"] or slug.replace("-", " ").title(),
        "date": meta["date"],
        "description": meta["description"],
        "slug": slug,
        "html": md_to_html(body.strip()),
        "words": words,
        "read_min": max(1, round(words / 200)),
    }


def _pretty_date(iso):
    try:
        y, m, d = (int(x) for x in iso.split("-"))
        months = ["", "January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        return f"{months[m]} {d}, {y}"
    except Exception:
        return iso or ""


# ------------------------------------------------------------------ templates
def _head(title, description, canonical, jsonld):
    desc = html.escape(description or "Notes on teaching math, from a teacher building tools for teachers.")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="article">
<meta property="og:image" content="https://euclidiamath.com/images/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{canonical}">
<link rel="icon" type="image/svg+xml" href="images/favicon.svg">
<link rel="stylesheet" href="styles.css">
<noscript><style>.reveal{{opacity:1!important;transform:none!important;}}</style></noscript>
<style>
  .blog-wrap {{ max-width:760px; margin:0 auto; padding:120px 20px 80px; }}
  .blog-back {{ display:inline-block; color:var(--text-dim); text-decoration:none; font-size:14px; margin-bottom:28px; }}
  .blog-back:hover {{ color:var(--gold); }}
  .blog-eyebrow {{ color:var(--gold); font-size:13px; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; }}
  .post-title {{ font-family:'Playfair Display',serif; color:var(--white); font-size:40px; line-height:1.2; margin:14px 0 10px; }}
  .post-meta {{ color:var(--text-dim); font-size:14px; margin-bottom:36px; }}
  .post-body {{ color:var(--text); font-size:17px; line-height:1.75; }}
  .post-body h2 {{ font-family:'Playfair Display',serif; color:var(--white); font-size:27px; margin:40px 0 12px; }}
  .post-body h3 {{ color:var(--text-bright); font-size:21px; margin:30px 0 10px; }}
  .post-body p {{ margin:0 0 20px; }}
  .post-body a {{ color:var(--gold-light); text-decoration:underline; }}
  .post-body ul, .post-body ol {{ margin:0 0 20px; padding-left:24px; }}
  .post-body li {{ margin:6px 0; }}
  .post-body blockquote {{ border-left:3px solid var(--gold-border); margin:24px 0; padding:4px 18px; color:var(--text-bright); font-style:italic; }}
  .post-body img {{ max-width:100%; height:auto; border-radius:12px; margin:24px 0; }}
  .post-body pre {{ background:var(--navy-card); border:1px solid var(--border-gold); border-radius:10px; padding:16px; overflow-x:auto; }}
  .post-body code {{ font-family:ui-monospace,monospace; font-size:0.92em; }}
  .post-body hr {{ border:0; border-top:1px solid var(--border-gold); margin:36px 0; }}
  .blog-cards {{ display:grid; gap:22px; margin-top:36px; }}
  .blog-card {{ background:var(--card-bg); border:1px solid var(--border-gold); border-radius:var(--radius-lg); padding:26px 28px; }}
  .blog-card h2 {{ font-family:'Playfair Display',serif; color:var(--white); font-size:24px; margin:6px 0 8px; line-height:1.25; }}
  .blog-card p {{ color:var(--text); font-size:15px; line-height:1.7; margin:0 0 14px; }}
  .blog-card .card-date {{ color:var(--text-dim); font-size:13px; }}
  .blog-card a.read {{ color:var(--gold-light); font-weight:700; text-decoration:none; font-size:14px; }}
  .blog-card a.read:hover {{ text-decoration:underline; }}
  .blog-empty {{ color:var(--text-dim); }}
  .signup {{ background:var(--card-bg); border:1px solid var(--border-gold); border-radius:var(--radius-lg); padding:28px; margin-top:44px; text-align:center; }}
  .signup h3 {{ font-family:'Playfair Display',serif; color:var(--white); font-size:22px; margin:0 0 6px; }}
  .signup p {{ color:var(--text); font-size:14.5px; margin:0 0 16px; }}
  .signup form {{ display:flex; gap:10px; max-width:420px; margin:0 auto; flex-wrap:wrap; justify-content:center; }}
  .signup input[type=email] {{ flex:1; min-width:220px; background:rgba(255,255,255,0.07); border:1px solid rgba(255,255,255,0.15); border-radius:9px; padding:12px 16px; color:var(--white); font:inherit; font-size:15px; }}
  .signup button {{ background:var(--gold); color:var(--navy); border:0; border-radius:9px; padding:12px 24px; font:inherit; font-weight:700; cursor:pointer; }}
  .signup button:hover {{ background:var(--gold-light); }}
  .post-foot {{ margin-top:48px; padding-top:28px; border-top:1px solid var(--border-gold); color:var(--text); }}
  .post-foot a {{ color:var(--gold-light); }}
</style>
<script type="application/ld+json">
{jsonld}
</script>
</head>
<body data-page="blog">
<a href="#main" class="skip-link">Skip to main content</a>
<main id="main">"""


_TAIL = """</main>
<script src="nav.js"></script>
<script src="main.js"></script>
</body>
</html>"""


def _signup_html():
    return f"""    <div class="signup reveal">
      <h3>Occasional teaching notes</h3>
      <p>No schedule, no spam. Just the odd note on making math land, sent when there's something worth saying.</p>
      <form action="https://api.web3forms.com/submit" method="POST">
        <input type="hidden" name="access_key" value="{WEB3FORMS_KEY}">
        <input type="hidden" name="subject" value="Euclidia Teaching Notes signup">
        <input type="checkbox" name="botcheck" style="display:none;" tabindex="-1" autocomplete="off" aria-hidden="true">
        <label class="sr-only" for="notes-email">Email address</label>
        <input type="email" id="notes-email" name="email" placeholder="your@email.com" required>
        <button type="submit">Keep me posted</button>
      </form>
    </div>"""


def render_post(post):
    canonical = f"https://euclidiamath.com/{BLOG_DIR}/{post['slug']}.html"
    jsonld = (
        '{\n  "@context": "https://schema.org",\n  "@type": "BlogPosting",\n'
        f'  "headline": {_json(post["title"])},\n'
        f'  "description": {_json(post["description"])},\n'
        f'  "datePublished": {_json(post["date"])},\n'
        f'  "url": {_json(canonical)},\n'
        '  "author": { "@type": "Person", "name": "Euclidia (a teacher)" },\n'
        '  "publisher": { "@type": "Organization", "name": "Euclidia" }\n}'
    )
    head = _head(f"{post['title']} · Euclidia", post["description"], canonical, jsonld)
    meta = _pretty_date(post["date"])
    if meta:
        meta += f" &middot; {post['read_min']} min read"
    return f"""{head}
  <article class="blog-wrap reveal">
    <a href="/blog.html" class="blog-back">&larr; All notes</a>
    <div class="blog-eyebrow">Teaching notes</div>
    <h1 class="post-title">{html.escape(post['title'])}</h1>
    <div class="post-meta">{meta}</div>
    <div class="post-body">
{post['html']}
    </div>
    <div class="post-foot">
      <p>Written by a working math teacher building <a href="/index.html">Euclidia</a>. If a game your class actually asks for (that grades itself into your gradebook) sounds useful, <a href="https://play.euclidiamath.com">try it free</a>.</p>
    </div>
  </article>
{_TAIL}"""


def render_index(posts):
    canonical = "https://euclidiamath.com/blog.html"
    jsonld = (
        '{\n  "@context": "https://schema.org",\n  "@type": "Blog",\n'
        '  "name": "Euclidia Teaching Notes",\n'
        f'  "url": {_json(canonical)},\n'
        '  "description": "Notes on teaching math, assessment, and engagement, from a teacher building tools for teachers."\n}'
    )
    head = _head(
        "Teaching Notes · Euclidia",
        "Notes on teaching math, assessment, and engagement, from a teacher building tools for teachers.",
        canonical, jsonld,
    )
    if posts:
        cards = "\n".join(
            f"""      <article class="blog-card">
        <span class="card-date">{_pretty_date(p['date'])}</span>
        <h2>{html.escape(p['title'])}</h2>
        <p>{html.escape(p['description'])}</p>
        <a class="read" href="/{BLOG_DIR}/{p['slug']}.html">Read &rarr;</a>
      </article>"""
            for p in posts
        )
        body = f'    <div class="blog-cards reveal">\n{cards}\n    </div>'
    else:
        body = '    <p class="blog-empty">No notes yet. Check back soon.</p>'
    return f"""{head}
  <div class="blog-wrap">
    <a href="/index.html" class="blog-back">&larr; euclidiamath.com</a>
    <div class="blog-eyebrow">Teaching notes</div>
    <h1 class="post-title">Notes from the classroom</h1>
    <div class="post-meta">Math, assessment, and engagement. Written by a teacher, between classes.</div>
{body}
{_signup_html()}
  </div>
{_TAIL}"""


def _json(s):
    """Minimal JSON string encode for the JSON-LD blocks."""
    return '"' + (s or "").replace("\\", "\\\\").replace('"', '\\"') + '"'


# ------------------------------------------------------------------ build
def build_blog():
    """Build blog/<slug>.html for every posts/*.md + the blog.html index.
    Returns the list of (url, changefreq, priority) tuples for the sitemap."""
    os.makedirs(BLOG_DIR, exist_ok=True)
    posts = []
    if os.path.isdir(POSTS_DIR):
        for fn in os.listdir(POSTS_DIR):
            if fn.endswith(".md") and not fn.startswith("_"):
                posts.append(parse_post(os.path.join(POSTS_DIR, fn)))
    posts.sort(key=lambda p: p["date"], reverse=True)

    # remove stale generated pages for posts that no longer exist
    live = {f"{p['slug']}.html" for p in posts}
    for fn in os.listdir(BLOG_DIR):
        if fn.endswith(".html") and fn not in live:
            os.remove(os.path.join(BLOG_DIR, fn))

    for p in posts:
        with open(os.path.join(BLOG_DIR, f"{p['slug']}.html"), "w", encoding="utf-8") as f:
            f.write(render_post(p))
    with open(BLOG_INDEX, "w", encoding="utf-8") as f:
        f.write(render_index(posts))

    print(f"  wrote {BLOG_INDEX} + {len(posts)} post page(s)")
    urls = [("https://euclidiamath.com/blog.html", "weekly", "0.7")]
    urls += [(f"https://euclidiamath.com/{BLOG_DIR}/{p['slug']}.html", "monthly", "0.6") for p in posts]
    return urls


if __name__ == "__main__":
    build_blog()
