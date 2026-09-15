#!/usr/bin/env python3
"""Regenerate the OIF avatar at every size from the wordmark.

The mark is `oif` in charcoal with `.md` half-height in amber, sized so
the pair occupies a fixed fraction of the canvas width. Sizing by width
rather than by point size is what keeps it inside a circular crop, which
is how X, GitHub and most platforms display an avatar.

    python3 src/make-avatar.py
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

CHAR = (45, 45, 45)        # charcoal
AMBER = (224, 160, 60)     # muted amber
BG = (249, 245, 234)       # warm off-white
FONT = "/usr/share/fonts/adwaita-mono-fonts/AdwaitaMono-Bold.ttf"

MASTER = 1600
WIDTH_FRAC = 0.68          # share of canvas width the whole mark occupies
MD_RATIO = 0.42            # ".md" size relative to "oif"
SIZES = (1024, 512, 400, 192, 180, 32)

out = Path(__file__).resolve().parent.parent


def fit_font_size() -> int:
    """Largest size where 'oif' + '.md' fits WIDTH_FRAC of the canvas."""
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    lo, hi, target = 10, int(MASTER * 0.6), MASTER * WIDTH_FRAC
    while lo < hi:
        mid = (lo + hi + 1) // 2
        fb = ImageFont.truetype(FONT, mid)
        fs = ImageFont.truetype(FONT, max(8, int(mid * MD_RATIO)))
        w = probe.textbbox((0, 0), "oif", font=fb)[2] + probe.textbbox((0, 0), ".md", font=fs)[2]
        lo, hi = (mid, hi) if w <= target else (lo, mid - 1)
    return lo


def render(size: int) -> Image.Image:
    fb = ImageFont.truetype(FONT, size)
    fs = ImageFont.truetype(FONT, max(8, int(size * MD_RATIO)))
    im = Image.new("RGB", (MASTER, MASTER), BG)
    d = ImageDraw.Draw(im)
    b1 = d.textbbox((0, 0), "oif", font=fb); w1, h1 = b1[2] - b1[0], b1[3] - b1[1]
    b2 = d.textbbox((0, 0), ".md", font=fs); w2, h2 = b2[2] - b2[0], b2[3] - b2[1]
    x, y = (MASTER - (w1 + w2)) // 2, (MASTER - h1) // 2
    d.text((x - b1[0], y - b1[1]), "oif", font=fb, fill=CHAR)
    d.text((x + w1 - b2[0], y + h1 - h2 - b2[1]), ".md", font=fs, fill=AMBER)
    return im


def circle_preview(im: Image.Image, n: int) -> Image.Image:
    """What a platform actually shows: the square masked to a circle."""
    a = im.resize((n, n), Image.LANCZOS)
    mask = Image.new("L", (n, n), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, n - 1, n - 1), fill=255)
    c = Image.new("RGB", (n, n), (255, 255, 255))
    c.paste(a, (0, 0), mask)
    return c


if __name__ == "__main__":
    master = render(fit_font_size())
    master.save(out / "src" / "oif-avatar-master-1600.png", optimize=True)
    for n in SIZES:
        master.resize((n, n), Image.LANCZOS).save(out / f"oif-avatar-{n}.png", optimize=True)
    circle_preview(master, 400).save(out / "oif-avatar-400-circle-preview.png", optimize=True)
    print(f"wrote master + {len(SIZES)} sizes to {out}")
