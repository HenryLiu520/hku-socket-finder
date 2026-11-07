#!/usr/bin/env python3
"""Put the narration on the demo video.

  python3 scripts/video/narrate.py /tmp/R21_demo.mp4 /tmp/vo out.mp4

The eight lines were generated separately so each one could be nudged to its beat;
the offsets below mirror the cues in build.py (title card = 3.2 s, then the three
recorded segments).
"""
import os
import subprocess
import sys

SRC = sys.argv[1] if len(sys.argv) > 1 else "/tmp/R21_demo.mp4"
VO = sys.argv[2] if len(sys.argv) > 2 else "/tmp/vo"
OUT = sys.argv[3] if len(sys.argv) > 3 else "/tmp/R21_demo_vo.mp4"

TITLE = 3.2
A, B = 13.2, 5.8

OFFSETS = [
    (1, TITLE + 0.5),
    (2, TITLE + 3.6),
    (3, TITLE + 6.4),
    (4, TITLE + 9.4),
    (5, TITLE + A + 0.5),
    (6, TITLE + A + 3.0),
    (7, TITLE + A + B + 0.4),
    (8, TITLE + A + B + 3.0),
]


def main():
    args = ["ffmpeg", "-y", "-i", SRC]
    for n, _ in OFFSETS:
        args += ["-i", os.path.join(VO, "%d.mp3" % n)]

    parts = []
    for i, (n, at) in enumerate(OFFSETS, start=1):
        ms = int(at * 1000)
        parts.append("[%d:a]adelay=%d|%d,volume=1.0[a%d]" % (i, ms, ms, i))
    mix_inputs = "".join("[a%d]" % i for i in range(1, len(OFFSETS) + 1))
    chain = ";".join(parts) + (";%samix=inputs=%d:normalize=0,highpass=f=90,"
                               "afade=t=out:st=%d:d=1.2[a]"
                               % (mix_inputs, len(OFFSETS), 27))

    args += ["-filter_complex", chain, "-map", "0:v", "-map", "[a]",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ac", "2",
             "-movflags", "+faststart", OUT]
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                            "format=duration:stream=codec_type", "-of", "default=nw=1", OUT],
                           capture_output=True, text=True)
    print(probe.stdout.strip())
    print("wrote", OUT)


if __name__ == "__main__":
    main()
