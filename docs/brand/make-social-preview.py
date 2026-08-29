#!/usr/bin/env python3
"""Render `sempods-social-preview.png` from the mark beside it.

GitHub's social preview — the card a shared repository link renders as — is a raster image at a
fixed size, and it has no API: each repository takes it through Settings → General. So the file is
committed rather than generated on demand, and this script is how it is regenerated when the mark
changes. Which it will: `README.md` says the current one is transitional.

    pip install cairosvg && python3 docs/brand/make-social-preview.py

Colours are the app icon's, so the three assets stay one family. The wording is the website's
first line; if that changes, this follows rather than inventing a second tagline.
"""

import re
from pathlib import Path

import cairosvg

HERE = Path(__file__).parent
WIDTH, HEIGHT = 1280, 640  # what GitHub recommends; it crops smaller in some surfaces
BACKGROUND, FOREGROUND, MUTED = "#111111", "#ffffff", "#9a9a9a"

# The mark is a 24×24 glyph drawn in `currentColor`. Lifting its body out rather than embedding
# the whole file keeps one source for the shape — an `<img>` would need a second copy on disk.
mark = (HERE / "sempods-mark.svg").read_text()
glyph = re.sub(r"^.*?<svg[^>]*>|</svg>\s*$", "", mark, flags=re.S).strip()

card = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}"
     viewBox="0 0 {WIDTH} {HEIGHT}">
  <rect width="{WIDTH}" height="{HEIGHT}" fill="{BACKGROUND}"/>
  <g transform="translate(496,116) scale(12)" fill="{FOREGROUND}" color="{FOREGROUND}">{glyph}</g>
  <text x="640" y="486" font-family="Helvetica,Arial,sans-serif" font-size="62"
        fill="{FOREGROUND}" text-anchor="middle" letter-spacing="1">sempods</text>
  <text x="640" y="532" font-family="Helvetica,Arial,sans-serif" font-size="25"
        fill="{MUTED}" text-anchor="middle">your data belongs to you</text>
</svg>"""

out = HERE / "sempods-social-preview.png"
cairosvg.svg2png(bytestring=card.encode(), write_to=str(out),
                 output_width=WIDTH, output_height=HEIGHT)
print(f"wrote {out.relative_to(HERE.parent.parent)} ({out.stat().st_size} bytes)")
