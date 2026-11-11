#!/usr/bin/env python3
"""Compose the demo video from the three recorded segments.

  python3 scripts/video/build.py /tmp/rA /tmp/rB /tmp/rC /tmp/R21_demo.mp4

rA = student: buildings, a room, the two other languages
rB = staff: the queue, close the oldest fault
rC = back in the room, the fault now closed

Cards and captions are drawn with Pillow: the ffmpeg here has no drawtext and no
libass. Caption images are looped so an overlay can stay on screen for its window.
"""
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

SEG = [sys.argv[1] if len(sys.argv) > 1 else "/tmp/rA",
       sys.argv[2] if len(sys.argv) > 2 else "/tmp/rB",
       sys.argv[3] if len(sys.argv) > 3 else "/tmp/rC"]
OUT = sys.argv[4] if len(sys.argv) > 4 else "/tmp/R21_demo.mp4"

W, H = 1280, 800
FPS = 30
TITLE, END = 3.2, 3.8

GREEN = (2, 70, 56)
INK = (247, 241, 230)
GOLD = (230, 217, 192)
MUTED = (201, 214, 209)

BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
REG = "/System/Library/Fonts/Supplemental/Arial.ttf"
TMP = "/tmp/sfvideo"


def font(path, size):
    return ImageFont.truetype(path, size)


def centre(draw, text, y, f, fill):
    x0, y0, x1, y1 = draw.textbbox((0, 0), text, font=f)
    draw.text(((W - (x1 - x0)) / 2 - x0, y - (y1 - y0) / 2 - y0), text, font=f, fill=fill)


def card(path, lines):
    img = Image.new("RGB", (W, H), GREEN)
    d = ImageDraw.Draw(img)
    for text, y, f, colour in lines:
        centre(d, text, y, f, colour)
    img.save(path)


def title_image(path):
    card(path, [("Sure Socket", 330, font(BOLD, 78), INK),
                ("Know before you sit down", 420, font(REG, 30), GOLD),
                ("CCST9003  ·  Group R21  ·  HKU", 730, font(REG, 19), MUTED)])


def end_image(path):
    card(path, [("One socket, one record.", 330, font(BOLD, 52), INK),
                ("Students keep it true. Staff act on it.", 410, font(REG, 26), GOLD),
                ("github.com/HenryLiu520/sure-socket", 720, font(REG, 18), MUTED)])


def caption_image(text, path):
    h = 96
    img = Image.new("RGBA", (W, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = font(REG, 28)
    x0, y0, x1, y1 = d.textbbox((0, 0), text, font=f)
    tw, th = x1 - x0, y1 - y0
    pad_x, pad_y = 22, 12
    bw, bh = tw + pad_x * 2, th + pad_y * 2
    bx, by = (W - bw) / 2, (h - bh) / 2
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=10, fill=(8, 30, 25, 195))
    d.text((bx + pad_x - x0, by + pad_y - y0), text, font=f, fill=(255, 255, 255, 255))
    img.save(path)


def run(args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def still(png, seconds, path, fade_in=False, fade_out=False):
    vf = ["scale=%d:%d" % (W, H), "format=yuv420p"]
    if fade_in:
        vf.insert(0, "fade=t=in:st=0:d=0.45")
    if fade_out:
        vf.insert(0, "fade=t=out:st=%.2f:d=0.6" % (seconds - 0.6))
    run(["ffmpeg", "-y", "-loop", "1", "-i", png, "-t", "%.2f" % seconds, "-r", str(FPS),
         "-vf", ",".join(vf), "-c:v", "libx264", "-preset", "medium", "-crf", "20",
         "-pix_fmt", "yuv420p", path])


def segment(directory, path):
    ts = json.load(open(os.path.join(directory, "timestamps.json")))
    fr = []
    for i, item in enumerate(ts):
        a = item["t"]
        b = ts[i + 1]["t"] if i + 1 < len(ts) else a + 0.6
        fr.append((os.path.join(directory, "frame-%05d.jpg" % item["frame"]),
                   max(0.04, min(3.0, b - a))))
    lst = os.path.join(directory, "concat.txt")
    with open(lst, "w") as fh:
        for p, d in fr:
            fh.write("file '%s'\nduration %.3f\n" % (p, d))
        fh.write("file '%s'\n" % fr[-1][0])
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst,
         "-vf", "fps=%d,scale=%d:%d,format=yuv420p" % (FPS, W, H),
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", path])
    return sum(d for _, d in fr)


def main():
    os.makedirs(TMP, exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)

    t_png, e_png = os.path.join(TMP, "title.png"), os.path.join(TMP, "end.png")
    title_image(t_png)
    end_image(e_png)
    t_mp4, e_mp4 = os.path.join(TMP, "t.mp4"), os.path.join(TMP, "e.mp4")
    still(t_png, TITLE, t_mp4, fade_in=True)
    still(e_png, END, e_mp4, fade_out=True)

    bodies = [os.path.join(TMP, "a.mp4"), os.path.join(TMP, "b.mp4"), os.path.join(TMP, "c.mp4")]
    durs = [segment(d, p) for d, p in zip(SEG, bodies)]
    a_end = durs[0]
    b_end = a_end + durs[1]

    cues = [
        (0.5, 2.8, "Four buildings. Rooms are sorted by what is wrong."),
        (3.6, 2.6, "Open the room you are sitting in."),
        (6.4, 2.8, "Every socket, on a plan and in a list."),
        (9.4, 2.6, "The same screen, in Chinese."),
        (a_end + 0.5, 2.6, "Staff get one queue, oldest fault first."),
        (a_end + 3.0, 2.6, "Close the oldest fault."),
        (b_end + 0.4, 2.8, "Back in the room: the socket is closed."),
        (b_end + 3.0, 3.0, "One socket, one record. That is the loop."),
    ]

    caps = []
    for i, (start, dur, text) in enumerate(cues):
        p = os.path.join(TMP, "cap%d.png" % i)
        caption_image(text, p)
        caps.append((p, start + TITLE, start + TITLE + dur))

    lst = os.path.join(TMP, "all.txt")
    with open(lst, "w") as fh:
        for p in [t_mp4] + bodies + [e_mp4]:
            fh.write("file '%s'\n" % p)
    base = os.path.join(TMP, "base.mp4")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", base])

    args = ["ffmpeg", "-y", "-i", base]
    for p, _, _ in caps:
        args += ["-loop", "1", "-i", p]
    chain, last = [], "[0:v]"
    for i, (_, start, end) in enumerate(caps):
        nxt = "[v%d]" % i
        chain.append("%s[%d:v]overlay=0:%d:enable='between(t,%.2f,%.2f)':shortest=0%s"
                     % (last, i + 1, H - 96, start, end, nxt))
        last = nxt
    args += ["-filter_complex", ";".join(chain), "-map", last, "-t", "%.2f" % (TITLE + sum(durs) + END),
             "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
             "-movflags", "+faststart", OUT]
    run(args)

    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", OUT], capture_output=True, text=True)
    print("wrote %s  %ss  segments=%s  captions=%d"
          % (OUT, dur.stdout.strip(), ["%.1f" % d for d in durs], len(caps)))


if __name__ == "__main__":
    main()
