#!/usr/bin/env python3
"""Just the battery and the warning: no phone frame.

  python3 scripts/make_battery_alert.py out_dir

Bright-on-dark: the backdrop is charcoal rather than black, the battery is outlined
in red with a sliver of charge left, and the alert is a light card with dark text.
Sizes: 1920x1080 and 1080x1920.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
REG = "/System/Library/Fonts/Supplemental/Arial.ttf"

RED = (255, 69, 58)
CARD = (250, 250, 252)
CARD_LINE = (214, 214, 219)
INK = (18, 18, 20)
SUB = (72, 72, 78)
BLUE = (0, 122, 255)


def font(path, size):
    return ImageFont.truetype(path, int(size))


def centre_text(d, text, cx, y, f, fill):
    w = d.textbbox((0, 0), text, font=f)[2]
    d.text((cx - w / 2, y), text, font=f, fill=fill)


def render(W, H, path):
    img = Image.new("RGB", (W, H), (26, 30, 33))
    # a soft light behind the content, so the frame is bright but not flat
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse([W * 0.16, H * 0.10, W * 0.84, H * 0.92], fill=120)
    glow = glow.filter(ImageFilter.GaussianBlur(W * 0.09))
    img = Image.composite(Image.new("RGB", (W, H), (58, 65, 70)), img, glow)
    d = ImageDraw.Draw(img)

    unit = min(W, H) * 0.001                      # everything scales off this
    cx = W / 2

    # battery: body, sliver of charge, nub
    bw, bh = unit * 300, unit * 130
    card_w, card_h = unit * 760, unit * 220
    block = bh + unit * 40 + unit * 150 + unit * 90 + card_h   # battery, 1%, card
    bx, by = cx - bw / 2, (H - block) / 2
    radius = bh * 0.20
    stroke = max(6, int(bh * 0.075))
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=radius, outline=RED, width=stroke)
    inner = stroke + 4
    d.rounded_rectangle([bx + inner, by + inner, bx + inner + max(4, bw * 0.025),
                         by + bh - inner], radius=4, fill=RED)
    nub_w, nub_h = max(8, bw * 0.045), bh * 0.34
    d.rounded_rectangle([bx + bw + unit * 8, by + (bh - nub_h) / 2,
                         bx + bw + unit * 8 + nub_w, by + (bh + nub_h) / 2],
                        radius=nub_w * 0.4, fill=RED)

    f_pct = font(BOLD, unit * 132)
    centre_text(d, "1%", cx, by + bh + unit * 34, f_pct, RED)

    # the alert: light card, dark text, one button
    card_x = cx - card_w / 2
    card_y = by + bh + unit * 280
    d.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h],
                        radius=unit * 26, fill=CARD)
    f_t = font(BOLD, unit * 52)
    f_b = font(REG, unit * 46)
    centre_text(d, "Your phone will shut down", cx, card_y + unit * 34, f_t, INK)
    centre_text(d, "in 30 seconds.", cx, card_y + unit * 104, f_b, SUB)
    div_y = card_y + card_h - unit * 66
    d.line([card_x, div_y, card_x + card_w, div_y], fill=CARD_LINE, width=max(2, int(unit * 2)))
    f_ok = font(BOLD, unit * 50)
    ok_w = d.textbbox((0, 0), "OK", font=f_ok)[2]
    d.text((card_x + card_w / 2 - ok_w / 2, div_y + unit * 12), "OK", font=f_ok, fill=BLUE)

    # gentle vignette, much lighter than before
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).ellipse([-W * 0.10, -H * 0.10, W * 1.10, H * 1.10], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(W * 0.10))
    img = Image.composite(img, Image.new("RGB", (W, H), (8, 9, 10)), mask)

    img.save(path)
    print("wrote", path, img.size)


def main():
    os.makedirs(OUT, exist_ok=True)
    render(1920, 1080, os.path.join(OUT, "battery-alert-landscape.png"))
    render(1080, 1920, os.path.join(OUT, "battery-alert-portrait.png"))


if __name__ == "__main__":
    main()
