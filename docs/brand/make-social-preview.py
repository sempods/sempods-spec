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
MARK = 288  # the mark's rendered edge, whatever coordinate system it is drawn in

# The mark's body is lifted out rather than the file embedded, so there is one source for the
# shape — an `<img>` would need a second copy on disk. Its `viewBox` comes with it: the current
# mark is 24×24, the replacement `README.md` promises need not be, and a body placed under a
# scale factor chosen for 24 units would silently render at the wrong size or crop. Nesting an
# `<svg>` that carries the source coordinate system lets the mark scale itself.
mark = (HERE / "sempods-mark.svg").read_text()
glyph = re.sub(r"^.*?<svg[^>]*>|</svg>\s*$", "", mark, flags=re.S).strip()

view_box = re.search(r'viewBox="([^"]+)"', mark)
if not view_box:
    raise SystemExit("error: sempods-mark.svg has no viewBox — cannot place it without guessing.")

card = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}"
     viewBox="0 0 {WIDTH} {HEIGHT}">
  <rect width="{WIDTH}" height="{HEIGHT}" fill="{BACKGROUND}"/>
  <svg x="496" y="116" width="{MARK}" height="{MARK}" viewBox="{view_box.group(1)}"
       fill="{FOREGROUND}" color="{FOREGROUND}">{glyph}</svg>
  <text x="640" y="486" font-family="Helvetica,Arial,sans-serif" font-size="62"
        fill="{FOREGROUND}" text-anchor="middle" letter-spacing="1">sempods</text>
  <text x="640" y="532" font-family="Helvetica,Arial,sans-serif" font-size="25"
        fill="{MUTED}" text-anchor="middle">your data belongs to you</text>
</svg>"""

out = HERE / "sempods-social-preview.png"
cairosvg.svg2png(bytestring=card.encode(), write_to=str(out),
                 output_width=WIDTH, output_height=HEIGHT)
print(f"wrote {out.relative_to(HERE.parent.parent)} ({out.stat().st_size} bytes)")
