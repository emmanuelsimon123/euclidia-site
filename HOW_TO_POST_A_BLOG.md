# How to post a blog article

No coding needed. Writing a post is the same rhythm as adding a product:
write a file, run one command, push. Everything is free (no CMS, no
subscription). Your writing is plain text, so it stays yours and reads like
you, not like a tool.

---

## The one-time idea

Each post is a single **Markdown** file in the `posts/` folder. Markdown is
just text with a few simple marks for **bold**, headings, and links. Running
`python build.py` turns every post into a real web page (that Google can find)
and updates the blog list automatically.

You never touch HTML. You write; the build makes the page.

---

## Writing a post (about 5 minutes)

**1. Open GitHub Codespaces** (same as adding a product):
github.com/emmanuelsimon123/euclidia-site → green **Code** button →
**Codespaces** tab → open or create one.

**2. Make a new file in the `posts/` folder.** Right-click the `posts` folder
→ **New File**. Name it with the date and a short title, using hyphens and
ending in `.md`, for example:

```
posts/2026-09-03-grading-less-teaching-more.md
```

The file name (minus the date and `.md`) becomes the web address, so keep it
short and readable.

**3. Write the post.** Start with three info lines and a `---`, then your
article:

```
title: Grading less, teaching more
date: 2026-09-03
description: One sentence that shows up on the blog list and in Google search results.
---
Your first paragraph goes here. Just write normally.

## A section heading

Another paragraph. You can make a word **bold** or *italic*, add a
[link like this](https://play.euclidiamath.com), and make a list:

- first point
- second point

> A line like this becomes a nice pulled-out quote.
```

That is the whole format. `title`, `date` (as YYYY-MM-DD), and `description`
are the only required lines.

**4. Build it.** In the Codespaces terminal (Terminal → New Terminal), run:

```
python build.py
```

You'll see `Building blog... wrote blog.html + N post page(s)`. That created
your page at `blog/your-file-name.html` and added it to the blog list.

**5. Publish.** Commit and push (the green **Source Control** panel, or
`git add -A && git commit -m "New post" && git push`). The site updates itself
in about a minute. Your post is live at `euclidiamath.com/blog/<your-file-name>.html`
and linked from `euclidiamath.com/blog.html`.

---

## Good to know

- **No schedule.** Write when you have something to say. One good evergreen
  post a season beats a forced monthly one. An abandoned "monthly" blog looks
  worse than a small handful of strong pieces.
- **Delete or edit the example.** `posts/the-most-dangerous-answer.md` is a
  starter so the blog isn't empty. Keep it, rewrite it, or delete it and
  rebuild. It's yours.
- **To remove a post:** delete its `.md` file from `posts/` and run
  `python build.py` again. The build cleans up the old page for you.
- **Images:** drop the image in the `images/` folder, then in your post write
  `![a short description](images/your-image.png)`.
- **The email signup** on the blog list uses your existing free web3forms
  key, so new subscribers just get emailed to you. No newsletter service, no
  cost. When you're ready to actually send something, you'll already have a
  list building.
- **Markdown cheat sheet:** `# H1`, `## H2`, `**bold**`, `*italic*`,
  `[text](url)`, `- list`, `1. numbered`, `> quote`, `---` for a divider.

The writing is the only real work. Everything else is one command.
