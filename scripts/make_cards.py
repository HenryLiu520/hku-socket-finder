#!/usr/bin/env python3
"""Every card the film needs, in one style: campus photograph, green wash, cream type.

  python3 scripts/make_cards.py out_dir

Writes 3840x2160 stills and two clips under out_dir:
  card-intro.png       title card
  card-members.png     GROUP 21 with the five standing plates
  card-project.png     the socket glyph and the product name
  R21_intro.mp4        3.2 s, fade in from green
  R21_outro.mp4        7.0 s, members 4 s then the project card 3 s

The photograph is 1600x1081, so it is scaled to cover and blurred: it is the room the
type sits in, not the subject. Everything else is drawn on top of it.
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 3840, 2160
FPS = 30

CREAM = (242, 236, 225)
GREEN = (2, 70, 56)
GREEN_DEEP = (1, 40, 32)
GOLD = (180, 151, 100)

BLACK = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHOTO = os.path.join(ROOT, "frontend", "src", "assets", "hku-campus.jpg")

MEMBERS = ["Yiyang Xu", "Haoran Liu", "Chenxi Yu", "Lam Ying Chu", "Deyi Wang"]


def font(path, size):
    try:
        return ImageFont.truetype(path, int(size))
    except OSError:
        return ImageFont.truetype(BOLD, int(size))


def spaced(d, cx, y, text, f, fill, gap):
    total = sum(d.textlength(ch, font=f) for ch in text) + gap * (len(text) - 1)
    x = cx - total / 2
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + gap
    return total


def backdrop():
    """Campus photograph, blurred, under a deep green wash and a vignette."""
    photo = Image.open(PHOTO).convert("RGB")
    scale = max(W / photo.width, H / photo.height)
    photo = photo.resize((round(photo.width * scale), round(photo.height * scale)),
                         Image.LANCZOS)
    left = (photo.width - W) // 2
    top = (photo.height - H) // 3          # keep the sky, crop the ground
    photo = photo.crop((left, top, left + W, top + H)).filter(ImageFilter.GaussianBlur(14))

    wash = Image.new("RGB", (W, H), GREEN)
    img = Image.blend(photo, wash, 0.72)

    img = Image.blend(img, Image.new("RGB", (W, H), (24, 96, 74)), 0.16)

    # a light from the top-left, the way the photograph is lit
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse([-W * 0.2, -H * 0.5, W * 0.8, H * 0.7], fill=70)
    glow = glow.filter(ImageFilter.GaussianBlur(W * 0.07))
    img = Image.composite(Image.new("RGB", (W, H), (14, 82, 64)), img, glow)

    # vignette
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).ellipse([-W * 0.08, -H * 0.1, W * 1.08, H * 1.1], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(W * 0.06))
    img = Image.composite(img, Image.new("RGB", (W, H), GREEN_DEEP), mask)

    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 10], fill=GOLD)
    # a hairline frame, so the card reads as a card
    d.rectangle([70, 70, W - 70, H - 70], outline=(255, 255, 255, 26), width=2)
    return img


def kicker(d, text, y):
    f = font(BOLD, 46)
    spaced(d, W / 2, y, text, f, GOLD, 16)


def plate(img, box, name):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    d.rounded_rectangle([x0, y0 + 10, x1, y1 + 10], radius=40, fill=(0, 34, 27))
    d.rounded_rectangle([x0, y0, x1, y1], radius=40, fill=CREAM)
    d.rounded_rectangle([x0, y0, x1, y1], radius=40, outline=GOLD, width=4)
    d.ellipse([(x0 + x1) / 2 - 11, y0 + 54, (x0 + x1) / 2 + 11, y0 + 76], fill=GOLD)

    parts = name.split()
    f = font(BOLD, 92 if len(parts) < 3 else 80)
    line = f.size * 1.26
    cy = (y0 + y1) / 2 - line * len(parts) / 2 + 10
    for i, part in enumerate(parts):
        d.text(((x0 + x1) / 2 - d.textlength(part, font=f) / 2, cy + i * line),
               part, font=f, fill=GREEN)


def card_intro():
    img = backdrop()
    d = ImageDraw.Draw(img)
    kicker(d, "CCST9003  ·  GROUP R21", H * 0.255)

    f = font(BLACK, 300)
    spaced(d, W / 2, H * 0.36, "SURE SOCKET", f, CREAM, 10)

    d.rectangle([W / 2 - 150, H * 0.585, W / 2 + 150, H * 0.591], fill=GOLD)

    f2 = font(BOLD, 96)
    spaced(d, W / 2, H * 0.625, "KNOW BEFORE YOU SIT", f2, CREAM, 14)

    f3 = font(BOLD, 54)
    spaced(d, W / 2, H * 0.755, "A SOCKET-LEVEL STATUS MAP FOR HKU", f3, (196, 214, 206), 8)
    return img


def card_members():
    img = backdrop()
    d = ImageDraw.Draw(img)
    kicker(d, "CCST9003  ·  GROUP 21", H * 0.13)

    f = font(BLACK, 250)
    spaced(d, W / 2, H * 0.185, "GROUP 21", f, CREAM, 12)

    f2 = font(BOLD, 64)
    spaced(d, W / 2, H * 0.365, "MEMBERS", f2, GOLD, 24)

    n, pw, gap = len(MEMBERS), 540, 66
    total = n * pw + (n - 1) * gap
    x = (W - total) / 2
    for name in MEMBERS:
        plate(img, (x, H * 0.455, x + pw, H * 0.855), name)
        x += pw + gap
    return img


def card_project():
    img = backdrop()
    d = ImageDraw.Draw(img)

    size = 560
    cx, cy = W / 2, H * 0.30
    x0, y0 = cx - size / 2, cy - size / 2
    d.rounded_rectangle([x0, y0, x0 + size, y0 + size], radius=92, fill=CREAM)
    d.rounded_rectangle([x0, y0, x0 + size, y0 + size], radius=92, outline=GOLD, width=5)
    d.rounded_rectangle([cx - 32, cy - 140, cx + 32, cy - 36], radius=14, fill=GREEN)
    d.rounded_rectangle([cx - 132, cy + 28, cx - 38, cy + 86], radius=14, fill=GREEN)
    d.rounded_rectangle([cx + 38, cy + 28, cx + 132, cy + 86], radius=14, fill=GREEN)

    f = font(BLACK, 250)
    spaced(d, W / 2, H * 0.545, "SURE SOCKET", f, CREAM, 8)

    d.rectangle([W / 2 - 130, H * 0.715, W / 2 + 130, H * 0.7205], fill=GOLD)
    f2 = font(BOLD, 80)
    spaced(d, W / 2, H * 0.745, "KNOW BEFORE YOU SIT", f2, GOLD, 12)
    return img


def clip(stills, out, fade=0.5):
    """Join stills of equal length with a short crossfade, then a fade from green."""
    parts, filters = [], []
    for i, (png, secs) in enumerate(stills):
        parts += ["-loop", "1", "-t", str(secs), "-i", png]
        filters.append("[%d:v]fps=%d,format=yuv420p,scale=%d:%d[s%d]" % (i, FPS, W, H, i))
    chain = ";".join(filters)
    if len(stills) == 1:
        chain += ";[s0]copy[v]"
    elif fade <= 0:                      # hard cut keeps the timing exact
        pairs = "".join("[s%d]" % i for i in range(len(stills)))
        chain += ";%sconcat=n=%d:v=1:a=0[v]" % (pairs, len(stills))
    else:
        chain += ";[s0][s1]xfade=transition=fade:duration=%s:offset=%s[v]" % (
            fade, stills[0][1] - fade)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + parts +
                   ["-filter_complex", chain, "-map", "[v]",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], check=True)


def main():
    out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
    os.makedirs(out, exist_ok=True)

    intro = os.path.join(out, "card-intro.png")
    members = os.path.join(out, "card-members.png")
    project = os.path.join(out, "card-project.png")
    card_intro().save(intro)
    card_members().save(members)
    card_project().save(project)
    for p in (intro, members, project):
        print("wrote", p)

    clip([(intro, 3.2)], os.path.join(out, "R21_intro.mp4"))
    clip([(members, 4.0), (project, 3.0)], os.path.join(out, "R21_outro.mp4"), fade=0)
    print("wrote", os.path.join(out, "R21_intro.mp4"))
    print("wrote", os.path.join(out, "R21_outro.mp4"))


if __name__ == "__main__":
    main()
