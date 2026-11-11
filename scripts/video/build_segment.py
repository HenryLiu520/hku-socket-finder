#!/usr/bin/env python3
"""Cut the segment I own: how you use it, then the loop, in one file.

  python3 scripts/video/build_segment.py /tmp/uA /tmp/uB /tmp/uC /tmp/R21_segment.mp4

uA = student: buildings, room, plan, list, one report
uB = staff: the queue, close that fault
uC = back in the room, socket closed
then the four-step loop diagram, dissolving from one step to the next

Captions sit at the bottom over the app. Over the diagram they move to the top,
because the diagram has its own note along the bottom edge.
"""
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

USE = sys.argv[1] if len(sys.argv) > 1 else "/tmp/uA"
STAFF = sys.argv[2] if len(sys.argv) > 2 else "/tmp/uB"
AFTER = sys.argv[3] if len(sys.argv) > 3 else "/tmp/uC"
OUT = sys.argv[4] if len(sys.argv) > 4 else "/tmp/R21_segment.mp4"

W, H, FPS = 1280, 800, 30
TITLE, END = 2.4, 3.4
DIAG = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "docs", "diagrams"))
TMP = "/tmp/sfseg"

GREEN, INK, GOLD, MUTED_C = (2, 70, 56), (247, 241, 230), (230, 217, 192), (201, 214, 209)
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
REG = "/System/Library/Fonts/Supplemental/Arial.ttf"

LOOP = [("loop-demo-base.png", 2.2), ("loop-demo-1.png", 4.2), ("loop-demo-2.png", 4.2),
        ("loop-demo-3.png", 4.2), ("loop-demo-4.png", 4.8)]
XFADE = 0.45


def font(path, size):
    return ImageFont.truetype(path, size)


def run(args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def card_png(path, lines):
    img = Image.new("RGB", (W, H), GREEN)
    d = ImageDraw.Draw(img)
    for text, y, f, colour in lines:
        x0, y0, x1, y1 = d.textbbox((0, 0), text, font=f)
        d.text(((W - (x1 - x0)) / 2 - x0, y - (y1 - y0) / 2 - y0), text, font=f, fill=colour)
    img.save(path)


def caption_png(text, path):
    h = 88
    img = Image.new("RGBA", (W, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = font(REG, 28)
    x0, y0, x1, y1 = d.textbbox((0, 0), text, font=f)
    tw, th = x1 - x0, y1 - y0
    bw, bh = tw + 44, th + 24
    bx, by = (W - bw) / 2, (h - bh) / 2
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=10, fill=(8, 30, 25, 205))
    d.text((bx + 22 - x0, by + 12 - y0), text, font=f, fill=(255, 255, 255, 255))
    img.save(path)


def still(png, seconds, path, fade_in=0.0, fade_out=0.0):
    vf = ["scale=%d:%d" % (W, H), "format=yuv420p"]
    if fade_in:
        vf.insert(0, "fade=t=in:st=0:d=%.2f" % fade_in)
    if fade_out:
        vf.insert(0, "fade=t=out:st=%.2f:d=%.2f" % (seconds - fade_out, fade_out))
    run(["ffmpeg", "-y", "-loop", "1", "-i", png, "-t", "%.2f" % seconds, "-r", str(FPS),
         "-vf", ",".join(vf), "-c:v", "libx264", "-preset", "medium", "-crf", "20",
         "-pix_fmt", "yuv420p", path])


def segment(directory, speed, path):
    ts = json.load(open(os.path.join(directory, "timestamps.json")))
    fr = []
    for i, item in enumerate(ts):
        a = item["t"]
        b = ts[i + 1]["t"] if i + 1 < len(ts) else a + 0.6
        fr.append((os.path.join(directory, "frame-%05d.jpg" % item["frame"]),
                   min(3.0, max(0.05, (b - a))) * speed))
    lst = os.path.join(directory, "concat.txt")
    with open(lst, "w") as fh:
        for p, d in fr:
            fh.write("file '%s'\nduration %.3f\n" % (p, d))
        fh.write("file '%s'\n" % fr[-1][0])
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst,
         "-vf", "fps=%d,scale=%d:%d,format=yuv420p" % (FPS, W, H),
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", path])
    return sum(d for _, d in fr)


def loop_section(path):
    """One mp4 for the five diagram frames, dissolved into each other."""
    args = ["ffmpeg", "-y"]
    for name, secs in LOOP:
        args += ["-loop", "1", "-t", "%.2f" % secs, "-i", os.path.join(DIAG, name)]
    chain, last = [], "[0:v]"
    offset = 0.0
    for i in range(1, len(LOOP)):
        offset += LOOP[i - 1][1] - XFADE
        nxt = "[x%d]" % i
        chain.append("%s[%d:v]xfade=transition=fade:duration=%.2f:offset=%.3f%s"
                     % (last, i, XFADE, offset, nxt))
        last = nxt
    total = sum(s for _, s in LOOP) - XFADE * (len(LOOP) - 1)
    chain.append("%sscale=-2:%d:flags=lanczos,pad=%d:%d:(ow-iw)/2:6:color=white,format=yuv420p[v]"
                 % (last, H - 104, W, H))
    args += ["-filter_complex", ";".join(chain), "-map", "[v]", "-t", "%.2f" % total,
             "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "20",
             "-pix_fmt", "yuv420p", path]
    run(args)
    return total


def main():
    os.makedirs(TMP, exist_ok=True)
    t_png, e_png = os.path.join(TMP, "t.png"), os.path.join(TMP, "e.png")
    card_png(t_png, [("Sure Socket", 330, font(BOLD, 76), INK),
                     ("How it works, in one loop", 418, font(REG, 30), GOLD)])
    card_png(e_png, [("One socket, one record.", 336, font(BOLD, 50), INK),
                     ("Students keep it true. Staff close it.", 414, font(REG, 26), GOLD),
                     ("Group R21", 700, font(REG, 18), MUTED_C)])

    t_mp4, e_mp4 = os.path.join(TMP, "t.mp4"), os.path.join(TMP, "e.mp4")
    still(t_png, TITLE, t_mp4, fade_in=0.4)
    still(e_png, END, e_mp4, fade_out=0.6)

    a_mp4, b_mp4, c_mp4 = (os.path.join(TMP, "a.mp4"), os.path.join(TMP, "b.mp4"),
                           os.path.join(TMP, "c.mp4"))
    d_a = segment(USE, 1.45, a_mp4)
    d_b = segment(STAFF, 1.15, b_mp4)
    d_c = segment(AFTER, 1.25, c_mp4)
    lp_mp4 = os.path.join(TMP, "loop.mp4")
    d_l = loop_section(lp_mp4)

    parts = [t_mp4, a_mp4, b_mp4, c_mp4, lp_mp4, e_mp4]
    durs = [TITLE, d_a, d_b, d_c, d_l, END]
    lst = os.path.join(TMP, "all.txt")
    with open(lst, "w") as fh:
        for p in parts:
            fh.write("file '%s'\n" % p)
    base = os.path.join(TMP, "base.mp4")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", base])

    starts, acc = [], 0.0
    for d in durs:
        starts.append(acc)
        acc += d
    a0, b0, c0, l0 = starts[1], starts[2], starts[3], starts[4]
    total = acc

    # (start, text, place)  place: 'bottom' over the app, 'top' over the diagram
    cues = [
        (a0 + 0.4, "Four buildings. Every room.", "bottom"),
        (a0 + 3.4, "Each room says what is wrong.", "bottom"),
        (a0 + 6.4, "Open the room you are in.", "bottom"),
        (a0 + 9.6, "One socket, one number.", "bottom"),
        (a0 + 13.4, "Green works. Orange loose. Red dead.", "bottom"),
        (a0 + 17.2, "And when it was last checked.", "bottom"),
        (a0 + 20.6, "One tap to report.", "bottom"),
        (a0 + 24.2, "Saved for everyone.", "bottom"),
        (b0 + 0.6, "Staff get one queue.", "bottom"),
        (b0 + 3.6, "Close the fault you reported.", "bottom"),
        (c0 + 0.4, "Everyone sees the new state.", "bottom"),
        (l0 + 0.3, "One socket, one record.", "bottom"),
        (l0 + 2.6, "A student reports what they see.", "bottom"),
        (l0 + 6.9, "The record keeps the date.", "bottom"),
        (l0 + 11.2, "Staff repair it, oldest first.", "bottom"),
        (l0 + 15.4, "Everyone sees the new state.", "bottom"),
    ]

    caps = []
    for i, (start, text, place) in enumerate(cues):
        if start > total - 0.8:
            continue
        p = os.path.join(TMP, "cap%02d.png" % i)
        caption_png(text, p)
        nxt = cues[i + 1][0] if i + 1 < len(cues) else total
        end = min(start + 3.2, nxt - 0.12)
        y = 16 if place == "top" else H - 88
        caps.append((p, start, max(end, start + 0.9), y))

    args = ["ffmpeg", "-y", "-i", base]
    for p, _, _, _ in caps:
        args += ["-loop", "1", "-i", p]
    chain, last = [], "[0:v]"
    for i, (_, s, e, y) in enumerate(caps):
        nxt = "[v%d]" % i
        chain.append("%s[%d:v]overlay=0:%d:enable='between(t,%.2f,%.2f)':shortest=0%s"
                     % (last, i + 1, y, s, e, nxt))
        last = nxt
    args += ["-filter_complex", ";".join(chain), "-map", last, "-t", "%.2f" % total,
             "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
             "-movflags", "+faststart", OUT]
    run(args)

    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", OUT], capture_output=True, text=True)
    print("wrote %s  %ss  sections=%s  captions=%d"
          % (OUT, dur.stdout.strip(), ["%.1f" % d for d in durs], len(caps)))


if __name__ == "__main__":
    main()
