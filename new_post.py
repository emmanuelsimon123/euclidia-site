#!/usr/bin/env python3
"""
Euclidia - New Blog Post
========================
Run this in GitHub Codespaces (or locally) to start a new blog post.

Usage:
    python new_post.py

It asks you a few quick questions, then creates the post file for you with
everything set up. You just open the file and write your article. No setup
lines to type, no formatting to remember up front.

After you've written it:
    python build.py     (turns your post into a real web page)
    then commit + push   (it goes live in about a minute)
"""

import os
import re
import sys
from datetime import date

# make the ✓/→ output safe on any console (Windows cp1252, etc.)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

GREEN = "\033[92m"
GOLD = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

POSTS_DIR = "posts"


def print_header():
    print(f"\n{GOLD}{BOLD}{'=' * 50}{RESET}")
    print(f"{GOLD}{BOLD}   EUCLIDIA - New Blog Post{RESET}")
    print(f"{GOLD}{BOLD}{'=' * 50}{RESET}\n")


def print_success(msg):
    print(f"{GREEN}✓ {msg}{RESET}")


def print_error(msg):
    print(f"{RED}✗ {msg}{RESET}")


def print_info(msg):
    print(f"{BLUE}→ {msg}{RESET}")


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    text = re.sub(r"-+", "-", text)
    return text or "post"


def ask(question, required=True, default=None):
    prompt = f"{BOLD}{question}{RESET}"
    prompt += f" [{default}]: " if default else ": "
    while True:
        answer = input(prompt).strip()
        if not answer and default is not None:
            return default
        if answer or not required:
            return answer
        print_error("This one's needed. Give it a try.")


# The body the file starts with - a friendly runway he types over.
STARTER_BODY = """Write your post here. Delete this line and start typing.

A few marks you can use (ignore any you don't need):

## A section heading

**bold words**, *italic words*, and [a link like this](https://play.euclidiamath.com).

- a bullet point
- another bullet point

> A line starting with a greater-than sign becomes a nice pulled-out quote.

That's everything. Just write like normal; the marks above are optional.
"""


def main():
    print_header()

    if not os.path.isdir(POSTS_DIR):
        os.makedirs(POSTS_DIR)

    title = ask("Post title")
    today = date.today().isoformat()
    post_date = ask("Date (press enter for today)", required=False, default=today)
    description = ask("One-line description (shows on the blog list + in Google)")

    slug = slugify(title)
    path = os.path.join(POSTS_DIR, f"{slug}.md")

    if os.path.exists(path):
        print()
        print_error(f"A post file already exists at {path}")
        choice = ask("Overwrite it? (yes/no)", required=False, default="no").lower()
        if not choice.startswith("y"):
            print_info("Nothing changed. Run again with a different title, or edit the existing file.")
            return

    content = (
        f"title: {title}\n"
        f"date: {post_date}\n"
        f"description: {description}\n"
        f"---\n"
        f"{STARTER_BODY}"
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print()
    print_success(f"Created {path}")
    print()
    print_info("Next steps:")
    print(f"   1. Open {BOLD}{path}{RESET} and write your article (replace the starter text).")
    print(f"   2. Run {BOLD}python build.py{RESET} to turn it into a web page.")
    print(f"   3. Commit + push. It goes live at {BOLD}euclidiamath.com/blog/{slug}.html{RESET} in about a minute.")
    print()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled. Nothing changed.")
        sys.exit(0)
