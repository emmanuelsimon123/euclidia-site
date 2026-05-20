#!/usr/bin/env python3
"""
Regenerate self-hosted Google Fonts.

Run this only if you change which font weights/styles the site uses,
or if Google ships an updated version of the fonts.

Downloads the latin-subset .woff2 files into fonts/ and prints the
@font-face CSS block to paste into styles.css.
"""

import urllib.request
import re
import os

GOOGLE_URL = (
    "https://fonts.googleapis.com/css2"
    "?family=Playfair+Display:ital,wght@0,400;0,600;0,700;0,900;1,600"
    "&family=DM+Sans:wght@300;400;500;600;700"
    "&display=swap"
)

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def main():
    req = urllib.request.Request(GOOGLE_URL, headers={"User-Agent": UA})
    css = urllib.request.urlopen(req).read().decode("utf-8")

    pattern = re.compile(
        r"/\*\s*([\w-]+)\s*\*/\s*"
        r"@font-face\s*\{"
        r"\s*font-family:\s*'([^']+)';"
        r"\s*font-style:\s*(\w+);"
        r"\s*font-weight:\s*(\d+);"
        r"[^}]*?"
        r"src:\s*url\(([^)]+)\)[^}]*?"
        r"unicode-range:\s*([^;]+);"
        r"\s*\}",
        re.DOTALL,
    )

    os.makedirs("fonts", exist_ok=True)
    blocks = []

    for match in pattern.finditer(css):
        subset, family, style, weight, url, urange = match.groups()
        if subset != "latin":
            continue

        family_slug = family.lower().replace(" ", "-")
        if style == "italic":
            filename = f"{family_slug}-{weight}-italic.woff2"
        else:
            filename = f"{family_slug}-{weight}.woff2"

        print(f"  {family} {weight} {style} -> fonts/{filename}")
        urllib.request.urlretrieve(url, f"fonts/{filename}")

        blocks.append(
            f"@font-face {{ font-family: '{family}'; "
            f"font-style: {style}; font-weight: {weight}; "
            f"font-display: swap; "
            f"src: url('fonts/{filename}') format('woff2'); "
            f"unicode-range: {urange.strip()}; }}"
        )

    print()
    print("Paste these blocks into styles.css, replacing the existing @font-face section:")
    print()
    print("\n".join(blocks))


if __name__ == "__main__":
    main()
