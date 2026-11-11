#!/usr/bin/env python3
"""The two closing cards, 3840x2160, plus a 7-second cut of them.

  python3 scripts/make_end_cards.py out_dir

Card one: GROUP 21 with the five names on standing plates. Card two: the project
name and a socket glyph. Four seconds then three.
Every card is drawn twice: on chroma green for keying, and on the brand backdrop for
use as it is. ffmpeg glues each pair into a clip.
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 3840, 2160
FPS = 30
FIRST, SECOND = 4.0, 3.0

CREAM = (242, 236, 225)
DEEP = (2, 70, 56)
GOLD = (180, 151, 100)
CHROMA = (0, 177, 64)
WASH = (11, 46, 39)

BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
BLACK = "/System/Library/Fonts/Supplemental/Arial Black.ttf"

MEMBERS = ["Yiyang Xu", "Haoran Liu", "Chenxi Yu", "Lam Ying Chu", "Deyi Wang"]


def font(path, size):
    try:
        return ImageFont.truetype(path, int(size))
    except OSError:
        return ImageFont.truetype(BOLD, int(size))


def spaced(d, xy, text, f, fill, gap):
    """Draw text with extra tracking, centred on xy[0]."""
    total = sum(d.textlength(ch, font=f) for ch in text) + gap * (len(text) - 1)
    x = xy[0] - total / 2
    for ch in text:
        d.text((x, xy[1]), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + gap
    return total


def backdrop(mode):
    img = Image.new("RGB", (W, H), CHROMA if mode == "key" else WASH)
    if mode == "brand":
        glow = Image.new("L", (W, H), 0)
        gd = ImageDraw.Draw(glow)
        gd.ellipse([-W * 0.25, -H * 0.55, W * 0.85, H * 0.75], fill=95)
        gd.ellipse([W * 0.45, H * 0.45, W * 1.3, H * 1.5], fill=70)
        glow = glow.filter(ImageFilter.GaussianBlur(W * 0.06))
        img = Image.composite(Image.new("RGB", (W, H), (18, 66, 52)), img, glow)
        # a thin gold rule along the top, brand only
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, W, 12], fill=GOLD)
    return img


def plate(img, box, name, radius=44):
    """A standing name plate: cream face, deep green type, gold hairline."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    d.rounded_rectangle([x0 + 10, y0 + 14, x1 + 10, y1 + 14], radius=radius, fill=(0, 120, 46)
                        if img.getpixel((5, 5)) == CHROMA else (0, 34, 27))
    d.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=CREAM)
    d.rounded_rectangle([x0, y0, x1, y1], radius=radius, outline=GOLD, width=5)

    parts = name.split()
    f = font(BOLD, 96 if len(parts) < 3 else 84)
    line_h = f.size * 1.28
    total = line_h * len(parts)
    cy = (y0 + y1) / 2 - total / 2
    for i, part in enumerate(parts):
        tw = d.textlength(part, font=f)
        d.text(((x0 + x1) / 2 - tw / 2, cy + i * line_h), part, font=f, fill=DEEP)

    # a gold pin at the top, the same mark the app uses for a socket
    d.ellipse([(x0 + x1) / 2 - 13, y0 + 56, (x0 + x1) / 2 + 13, y0 + 82], fill=GOLD)


def card_one(mode):
    img = backdrop(mode)
    d = ImageDraw.Draw(img)

    f_group = font(BLACK, 286)
    spaced(d, (W / 2, H * 0.13), "GROUP 21", f_group, CREAM, 16)
    f_mem = font(BOLD, 76)
    spaced(d, (W / 2, H * 0.335), "MEMBERS", f_mem, GOLD, 30)

    n = len(MEMBERS)
    pw, gap = 560, 70
    total = n * pw + (n - 1) * gap
    x = (W - total) / 2
    top, bottom = H * 0.425, H * 0.875
    for name in MEMBERS:
        plate(img, (x, top, x + pw, bottom), name)
        x += pw + gap
    return img


def card_two(mode):
    img = backdrop(mode)
    d = ImageDraw.Draw(img)

    # the socket glyph: faceplate with three holes, a plug lead leaving the top
    size = 600
    cx, cy = W / 2, H * 0.35
    x0, y0 = cx - size / 2, cy - size / 2

    if mode == "brand":                      # never halo the chroma plate
        glow = Image.new("L", (W, H), 0)
        ImageDraw.Draw(glow).ellipse([cx - size, cy - size, cx + size, cy + size], fill=90)
        glow = glow.filter(ImageFilter.GaussianBlur(120))
        img = Image.composite(Image.new("RGB", (W, H), (26, 84, 66)), img, glow)
        d = ImageDraw.Draw(img)
    d.rounded_rectangle([x0, y0, x0 + size, y0 + size], radius=96, fill=CREAM)
    d.rounded_rectangle([x0, y0, x0 + size, y0 + size], radius=96, outline=GOLD, width=6)
    hole = DEEP
    d.rounded_rectangle([cx - 34, cy - 150, cx + 34, cy - 40], radius=16, fill=hole)   # earth
    d.rounded_rectangle([cx - 140, cy + 30, cx - 40, cy + 92], radius=16, fill=hole)   # neutral
    d.rounded_rectangle([cx + 40, cy + 30, cx + 140, cy + 92], radius=16, fill=hole)   # live


    f_name = font(BLACK, 230)
    spaced(d, (W / 2, H * 0.60), "SOCKET FINDER", f_name, CREAM, 8)
    f_tag = font(BOLD, 96)
    spaced(d, (W / 2, H * 0.78), "KNOW BEFORE YOU SIT", f_tag, GOLD, 18)
    return img


def clip(png_a, png_b, out):
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-loop", "1", "-t", str(FIRST), "-i", png_a,
           "-loop", "1", "-t", str(SECOND), "-i", png_b,
           "-filter_complex",
           "[0:v]fps=%d,format=yuv420p[a];[1:v]fps=%d,format=yuv420p[b];[a][b]concat=n=2:v=1:a=0[v]"
           % (FPS, FPS),
           "-map", "[v]", "-c:v", "libx264", "-preset", "medium", "-crf", "16",
           "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    print("wrote", out)


def main():
    out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
    os.makedirs(out, exist_ok=True)
    paths = {}
    for mode in ("key", "brand"):
        for i, fn in ((1, card_one), (2, card_two)):
            p = os.path.join(out, "endcard-%s-%d.png" % (mode, i))
            fn(mode).save(p)
            paths[(mode, i)] = p
            print("wrote", p)
    clip(paths[("key", 1)], paths[("key", 2)], os.path.join(out, "R21_end_card_key.mp4"))
    clip(paths[("brand", 1)], paths[("brand", 2)], os.path.join(out, "R21_end_card_brand.mp4"))


if __name__ == "__main__":
    main()
