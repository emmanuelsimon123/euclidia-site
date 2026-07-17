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

> **The command word: `python` vs `py`.** In **GitHub Codespaces** (the cloud
> editor) the command is **`python`**. On **your own Windows computer** (VS
> Code terminal), type **`py`** instead — so `py new_post.py` and
> `py build.py`. Windows doesn't answer to `python` unless you install it;
> `py` is already there. Everything below uses `python`; swap in `py` if
> you're on your own machine.

**1. Open GitHub Codespaces** (same as adding a product):
github.com/emmanuelsimon123/euclidia-site → green **Code** button →
**Codespaces** tab → open or create one.

**2. Run the helper.** In the terminal (Terminal → New Terminal), run:

```
python new_post.py
```

It asks you three quick things and makes the file for you:

```
Post title: Grading less, teaching more
Date (press enter for today):
One-line description (shows on the blog list + in Google): A quick take on cutting grading time.

✓ Created posts/grading-less-teaching-more.md
```

No setup lines to type, no formatting to remember. The title, date, and
description are already filled in.

**3. Write your article.** Open the file it made
(`posts/<your-title>.md`) and replace the starter text with your post. Write
normally. A few optional marks:

- `## A heading` makes a section heading
- `**bold**` and `*italic*`
- `[words to show](https://the-link.com)` makes a link
- a line starting with `-` makes a bullet; `>` makes a pulled-out quote

That's it. Anything you don't use, just ignore.

**4. Build it.** Back in the terminal:

```
python build.py
```

You'll see `Building blog... wrote blog.html + N post page(s)`. That turned
your post into a real web page and added it to the blog list.

**5. Publish.** Commit and push (the green **Source Control** panel, or
`git add -A && git commit -m "New post" && git push`). The site updates itself
in about a minute. Your post is live at `euclidiamath.com/blog/<your-title>.html`
and linked from `euclidiamath.com/blog.html`.

*(Prefer to skip the helper and just make the file yourself? You can — a post
is a plain `.md` file in `posts/` with three lines at the top: `title:`,
`date:` as YYYY-MM-DD, `description:`, then a `---`, then your article. The
helper just fills those in for you.)*

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
