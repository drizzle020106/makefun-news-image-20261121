#!/usr/bin/env python3
"""Draw entry.png: one image summing up the world news of Saturday 21 November 2026.

Layout: dark-navy page, big WORLD NEWS header with the date in gold, then a
2x3 grid of six stories. Each cell has a hand-drawn pictogram, a short
headline and a one-line caption. All drawing is done with Pillow only.
"""
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

NAVY = (10, 26, 46)
CELL = (18, 44, 71)
CELL_EDGE = (42, 74, 104)
GOLD = (232, 184, 75)
WHITE = (245, 247, 250)
GREY = (201, 214, 227)
RED = (214, 72, 60)
BLUE = (70, 130, 200)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_rocket(d, cx, cy, s):
    # A missile climbing to the upper right, with a burst at its nose.
    body = [(cx - 6 * s, cy + 14 * s), (cx + 2 * s, cy - 12 * s),
            (cx + 10 * s, cy - 8 * s), (cx + 2 * s, cy + 18 * s)]
    d.polygon(body, fill=GOLD)
    d.polygon([(cx + 2 * s, cy - 12 * s), (cx + 12 * s, cy - 16 * s),
               (cx + 10 * s, cy - 8 * s)], fill=RED)
    d.polygon([(cx - 6 * s, cy + 14 * s), (cx - 12 * s, cy + 20 * s),
               (cx - 2 * s, cy + 20 * s)], fill=GOLD)
    d.polygon([(cx + 2 * s, cy + 18 * s), (cx + 8 * s, cy + 24 * s),
               (cx + 6 * s, cy + 16 * s)], fill=GOLD)
    # exhaust flame
    d.polygon([(cx - 8 * s, cy + 22 * s), (cx - 14 * s, cy + 34 * s),
               (cx - 2 * s, cy + 26 * s)], fill=RED)
    # burst star at the nose
    bx, by = cx + 20 * s, cy - 22 * s
    for dx, dy in [(0, -8), (6, -6), (8, 0), (6, 6), (0, 8), (-6, 6), (-8, 0), (-6, -6)]:
        d.line([bx, by, bx + dx * s, by + dy * s], fill=WHITE, width=2)


def draw_chart(d, cx, cy, s):
    # Axes and a falling market line ending in a down arrow.
    d.line([cx - 34 * s, cy + 24 * s, cx + 34 * s, cy + 24 * s], fill=GREY, width=3)
    d.line([cx - 34 * s, cy + 24 * s, cx - 34 * s, cy - 28 * s], fill=GREY, width=3)
    pts = [(cx - 30 * s, cy - 18 * s), (cx - 14 * s, cy - 8 * s),
           (cx - 2 * s, cy - 16 * s), (cx + 12 * s, cy + 2 * s),
           (cx + 26 * s, cy + 18 * s)]
    d.line(pts, fill=RED, width=4, joint="curve")
    d.polygon([(cx + 26 * s, cy + 18 * s), (cx + 18 * s, cy + 14 * s),
               (cx + 24 * s, cy + 28 * s)], fill=RED)


def draw_flags(d, cx, cy, s):
    # Two small flags side by side: UK (red cross) and EU (stars on blue).
    d.rectangle([cx - 36 * s, cy - 18 * s, cx - 4 * s, cy + 18 * s],
                outline=WHITE, width=2)
    d.line([cx - 36 * s, cy, cx - 4 * s, cy], fill=RED, width=4)
    d.line([cx - 20 * s, cy - 18 * s, cx - 20 * s, cy + 18 * s], fill=RED, width=4)
    d.rectangle([cx + 4 * s, cy - 18 * s, cx + 36 * s, cy + 18 * s],
                fill=BLUE, outline=WHITE, width=2)
    for k in range(8):
        import math
        a = math.pi * 2 * k / 8 - math.pi / 2
        d.ellipse([cx + 20 * s + 10 * s * math.cos(a) - 2,
                   cy + 10 * s * math.sin(a) - 2,
                   cx + 20 * s + 10 * s * math.cos(a) + 2,
                   cy + 10 * s * math.sin(a) + 2], fill=GOLD)


def draw_shield(d, cx, cy, s):
    # A shield stopping an incoming missile.
    d.polygon([(cx - 22 * s, cy - 20 * s), (cx + 22 * s, cy - 20 * s),
               (cx + 22 * s, cy + 2 * s), (cx, cy + 24 * s),
               (cx - 22 * s, cy + 2 * s)], outline=GOLD, width=3)
    d.line([cx - 8 * s, cy - 8 * s, cx + 8 * s, cy - 8 * s], fill=WHITE, width=3)
    d.line([cx, cy - 14 * s, cx, cy + 8 * s], fill=WHITE, width=3)
    d.polygon([(cx + 26 * s, cy - 30 * s), (cx + 34 * s, cy - 26 * s),
               (cx + 28 * s, cy - 20 * s)], fill=RED)
    d.line([cx + 30 * s, cy - 24 * s, cx + 20 * s, cy - 14 * s], fill=RED, width=3)


def draw_quake(d, cx, cy, s):
    # Seismograph zigzag above cracked ground.
    pts = [(cx - 36 * s, cy - 6 * s), (cx - 24 * s, cy - 6 * s),
           (cx - 18 * s, cy - 22 * s), (cx - 10 * s, cy + 10 * s),
           (cx - 2 * s, cy - 14 * s), (cx + 8 * s, cy + 8 * s),
           (cx + 16 * s, cy - 6 * s), (cx + 36 * s, cy - 6 * s)]
    d.line(pts, fill=GOLD, width=3, joint="curve")
    d.line([cx - 36 * s, cy + 20 * s, cx - 10 * s, cy + 20 * s], fill=GREY, width=3)
    d.line([cx - 10 * s, cy + 20 * s, cx - 2 * s, cy + 30 * s], fill=GREY, width=3)
    d.line([cx - 2 * s, cy + 30 * s, cx + 6 * s, cy + 20 * s], fill=GREY, width=3)
    d.line([cx + 6 * s, cy + 20 * s, cx + 36 * s, cy + 20 * s], fill=GREY, width=3)


def draw_controller(d, cx, cy, s):
    # A game controller with a dollar coin above it.
    d.rounded_rectangle([cx - 34 * s, cy - 12 * s, cx + 34 * s, cy + 20 * s],
                        radius=12, outline=WHITE, width=3)
    d.line([cx - 24 * s, cy + 2 * s, cx - 12 * s, cy + 2 * s], fill=GOLD, width=4)
    d.line([cx - 18 * s, cy - 4 * s, cx - 18 * s, cy + 8 * s], fill=GOLD, width=4)
    for dx, dy in [(14, -4), (22, 4), (14, 10), (6, 4)]:
        d.ellipse([cx + dx * s - 3, cy + dy * s - 3,
                   cx + dx * s + 3, cy + dy * s + 3], fill=RED)
    d.ellipse([cx - 5, cy - 34 * s, cx + 15, cy - 14 * s],
              outline=GOLD, width=3)
    d.text((cx + 5, cy - 34 * s), "$", font=font(FONT_BOLD, 18),
           fill=GOLD, anchor="mm")


STORIES = [
    ("RUSSIAN MISSILES LAND IN POLAND",
     "400 drones, 110 missiles hit Ukraine; two land in Poland",
     draw_rocket),
    ("AI SELL-OFF HITS WALL STREET",
     "S&P 500 and Dow enter correction; Nasdaq erases its 2026 gains",
     draw_chart),
    ("UK AND EU SIGN POST-BREXIT DEAL",
     "Three pacts on food, carbon and youth mobility signed in Brussels",
     draw_flags),
    ("HOUTHI MISSILES TARGET RIYADH",
     "Saudi Arabia intercepts three ballistic missiles early on Saturday",
     draw_shield),
    ("6.8 QUAKE SHAKES PERU",
     "Tremor in the Andes felt in Lima; streets fill, no major damage",
     draw_quake),
    ("GTA VI SMASHES SALES RECORD",
     "$3.8bn on day one \u2014 the biggest entertainment launch ever",
     draw_controller),
]


def main():
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)

    # Header
    title_f = font(FONT_BOLD, 66)
    d.text((W // 2, 52), "WORLD NEWS", font=title_f, fill=WHITE, anchor="mm")
    d.line([W // 2 - 210, 96, W // 2 + 210, 96], fill=GOLD, width=3)
    date_f = font(FONT_BOLD, 34)
    d.text((W // 2, 128), "Saturday 21 November 2026", font=date_f,
           fill=GOLD, anchor="mm")

    # Grid geometry
    margin, gutter = 24, 20
    top, bottom = 168, 1000
    col_w = (W - 2 * margin - gutter) // 2
    row_h = (bottom - top - 2 * 16) // 3

    head_f = font(FONT_BOLD, 30)
    cap_f = font(FONT_REG, 22)

    for i, (headline, caption, icon) in enumerate(STORIES):
        r, c = divmod(i, 2)
        x0 = margin + c * (col_w + gutter)
        y0 = top + r * (row_h + 16)
        x1, y1 = x0 + col_w, y0 + row_h
        d.rounded_rectangle([x0, y0, x1, y1], radius=14, fill=CELL,
                            outline=CELL_EDGE, width=2)

        # Pictogram, centred near the top of the cell.
        icon(d, (x0 + x1) // 2, y0 + 52, 1.0)

        # Headline, up to two centred lines.
        lines = wrap(d, headline, head_f, col_w - 36)
        hy = y0 + 108
        for line in lines[:2]:
            d.text(((x0 + x1) // 2, hy), line, font=head_f, fill=WHITE,
                   anchor="mm")
            hy += 36

        # Caption, up to two centred lines.
        cap_lines = wrap(d, caption, cap_f, col_w - 36)
        cy = hy + 12
        for line in cap_lines[:2]:
            d.text(((x0 + x1) // 2, cy), line, font=cap_f, fill=GREY,
                   anchor="mm")
            cy += 28

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG")
    print("saved", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
