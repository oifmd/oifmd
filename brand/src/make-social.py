#!/usr/bin/env python3
"""Build the 1280x640 social card GitHub uses for link previews.

GitHub's social preview is 2:1, not the 3:1 of a profile header, so this
is its own composition rather than a crop: wordmark, tagline, and the
column motif reduced to a strip along the foot.

    python3 brand/src/make-social.py
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

CHAR, AMBER, BG = (45, 45, 45), (224, 160, 60), (249, 245, 234)
MUTE = (107, 101, 87)
BOLD = "/usr/share/fonts/adwaita-mono-fonts/AdwaitaMono-Bold.ttf"
REG = "/usr/share/fonts/adwaita-mono-fonts/AdwaitaMono-Regular.ttf"
out = Path(__file__).resolve().parent.parent

W, H = 2560, 1280                      # 2x, downscaled for crisp text
im = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(im)

f_mark = ImageFont.truetype(BOLD, 260)
f_md = ImageFont.truetype(BOLD, 110)
f_tag = ImageFont.truetype(REG, 74)

# wordmark, left-aligned with a generous margin
x0, y0 = 190, 300
b1 = d.textbbox((0, 0), "oif", font=f_mark)
d.text((x0 - b1[0], y0 - b1[1]), "oif", font=f_mark, fill=CHAR)
b2 = d.textbbox((0, 0), ".md", font=f_md)
d.text((x0 + (b1[2] - b1[0]) - b2[0], y0 + (b1[3] - b1[1]) - (b2[3] - b2[1]) - b2[1]),
       ".md", font=f_md, fill=AMBER)

# tagline over two lines, so neither runs long
for i, line in enumerate(["Issues and review comments as files,",
                          "in any git repository, about anything in it."]):
    d.text((x0, 700 + i * 100), line, font=f_tag, fill=MUTE)

# the column motif as a foot strip: four bands, one sheet amber
strip_y, strip_h = 1010, 200
for i in range(4):
    bx = 190 + i * 545
    d.line([(bx + 500, strip_y), (bx + 500, strip_y + strip_h)], fill=(226, 220, 203), width=4)
    sw, sh = 110, 140
    sx, sy = bx + 40 + (i % 2) * 60, strip_y + 30
    fill = AMBER if i == 2 else None
    d.rounded_rectangle([sx, sy, sx + sw, sy + sh], radius=8, outline=CHAR, width=9, fill=fill)

im.resize((1280, 640), Image.LANCZOS).save(out / "oif-social-1280x640.png", optimize=True)
print(f"wrote {out / 'oif-social-1280x640.png'}")
