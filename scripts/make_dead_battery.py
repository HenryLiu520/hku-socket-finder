#!/usr/bin/env python3
"""A dead battery on a phone, on black. Made for the opening shot of the pitch.

  python3 scripts/make_dead_battery.py out_dir

Writes phone-battery-portrait.png (1080x1920) and phone-battery-landscape.png
(1920x1080). Pure Pillow, so it can be regenerated or recoloured later.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
REG = "/System/Library/Fonts/Supplemental/Arial.ttf"

RED = (255, 59, 48)
INK = (232, 236, 238)
DIM = (120, 130, 134)


def rounded(draw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def phone(size, phone_w_ratio=0.62):
    """A dark phone with a black screen and an empty battery, on a black backdrop."""
    W, H = size
    img = Image.new("RGB", (W, H), (4, 5, 6))
    d = ImageDraw.Draw(img)

    # a very soft light behind the phone, so the edges separate from the black
    glow = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(glow)
    pw = int(W * phone_w_ratio)
    ph = int(pw * 2.06)
    if ph > H * 0.88:                      # landscape: shrink the phone so it fits
        ph = int(H * 0.88)
        pw = int(ph / 2.06)
    px = (W - pw) // 2
    py = (H - ph) // 2
    gd.rounded_rectangle([px - 40, py - 40, px + pw + 40, py + ph + 40], radius=120, fill=110)
    glow = glow.filter(ImageFilter.GaussianBlur(55))
    img = Image.composite(Image.new("RGB", (W, H), (26, 31, 33)), img, glow)
    d = ImageDraw.Draw(img)

    # body, then screen, then a rim of light along the top edge
    rounded(d, [px - 10, py - 10, px + pw + 10, py + ph + 10], 74, fill=(16, 18, 19))
    rounded(d, [px, py, px + pw, py + ph], 64, fill=(9, 11, 12), outline=(38, 43, 45), width=3)
    d.arc([px + 26, py + 6, px + pw - 26, py + 120], 200, 340, fill=(54, 60, 62), width=2)
    # rim light down the left edge, as if a window were just out of frame
    d.line([px - 6, py + 90, px - 6, py + ph - 90], fill=(58, 66, 68), width=3)
    # a faint reflection across the screen
    band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    bd.polygon([(px, py + int(ph * 0.30)), (px + pw, py + int(ph * 0.12)),
                (px + pw, py + int(ph * 0.22)), (px, py + int(ph * 0.42))],
               fill=(120, 150, 160, 16))
    img = Image.alpha_composite(img.convert("RGBA"), band).convert("RGB")
    d = ImageDraw.Draw(img)

    # speaker pill
    pill_w, pill_h = int(pw * 0.20), 12
    rounded(d, [W // 2 - pill_w // 2, py + 26, W // 2 + pill_w // 2, py + 26 + pill_h], 6,
            fill=(28, 32, 34))

    # the battery: empty body in red, no fill, with the nub on the right
    bw, bh = int(pw * 0.46), int(pw * 0.20)
    bx, by = W // 2 - bw // 2, int(H * 0.335)
    r = max(6, bh // 6)
    rounded(d, [bx, by, bx + bw, by + bh], r, outline=RED, width=max(4, bh // 9))
    fill_w = max(3, int((bw - 2 * max(4, bh // 9)) * 0.02))
    rounded(d, [bx + max(4, bh // 9) + 1, by + max(4, bh // 9) + 1,
                bx + max(4, bh // 9) + 1 + fill_w,
                by + bh - max(4, bh // 9) - 1], 2, fill=RED)
    nub_w, nub_h = max(6, bw // 22), bh // 3
    rounded(d, [bx + bw + 6, by + (bh - nub_h) // 2, bx + bw + 6 + nub_w,
                by + (bh + nub_h) // 2], 4, fill=RED)

    # 0% under it, and the line the phone says when it dies
    f0 = ImageFont.truetype(BOLD, int(pw * 0.16))
    t0 = "1%"
    tw = d.textbbox((0, 0), t0, font=f0)[2]
    d.text((W // 2 - tw // 2, by + bh + int(pw * 0.10)), t0, font=f0, fill=RED)

    # the system alert a phone throws when the battery is about to die
    card_w, card_h = int(pw * 0.86), int(pw * 0.42)
    cx = W // 2 - card_w // 2
    cy = by + bh + int(pw * 0.36)
    rounded(d, [cx, cy, cx + card_w, cy + card_h], 22, fill=(28, 29, 31),
            outline=(58, 60, 63), width=2)

    f_t = ImageFont.truetype(BOLD, int(pw * 0.062))
    f_b = ImageFont.truetype(REG, int(pw * 0.052))
    t_l1 = "Your phone will shut down"
    t_l2 = "in 30 seconds."
    for i, line in enumerate((t_l1, t_l2)):
        fnt = f_t if i == 0 else f_b
        lw = d.textbbox((0, 0), line, font=fnt)[2]
        d.text((W // 2 - lw // 2, cy + int(card_h * 0.16) + i * int(pw * 0.075)),
               line, font=fnt, fill=INK if i == 0 else (206, 212, 214))

    # divider and the one button, the way a system alert looks
    div_y = cy + int(card_h * 0.66)
    d.line([cx + 2, div_y, cx + card_w - 2, div_y], fill=(58, 60, 63), width=2)
    f_ok = ImageFont.truetype(BOLD, int(pw * 0.056))
    ok = "OK"
    ow = d.textbbox((0, 0), ok, font=f_ok)[2]
    d.text((cx + card_w - ow - int(pw * 0.06), div_y + int(card_h * 0.10)), ok,
           font=f_ok, fill=(10, 132, 255))

    # vignette
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([-W * 0.25, -H * 0.25, W * 1.25, H * 1.25], fill=110)
    mask = mask.filter(ImageFilter.GaussianBlur(160))
    img = Image.composite(img, Image.new("RGB", (W, H), (0, 0, 0)), mask)

    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, size, ratio in [("phone-battery-portrait.png", (1080, 1920), 0.62),
                              ("phone-battery-landscape.png", (1920, 1080), 0.30)]:
        img = phone(size, ratio)
        path = os.path.join(OUT, name)
        img.save(path)
        print("wrote", path, img.size)


if __name__ == "__main__":
    main()
