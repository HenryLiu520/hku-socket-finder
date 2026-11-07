#!/usr/bin/env python3
"""The loop used in the demo video: four steps, no second-confirmation card.

Draws five PNGs into docs/diagrams/: the plain figure and one per step, where the
step in question is in the accent colour and the rest are greyed out. The video
cross-fades between them, which is enough to read as "the loop moves on".

  python3 scripts/video/loop_demo.py
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "diagrams")

INK = "#1f2328"
MUTED = "#6b7280"
LINE = "#111111"
CARD = "#fbfbfa"
ACCENT = "#0b6b4f"
DIM_CARD = "#f3f3f1"
DIM_LINE = "#cfcfca"
DIM_TEXT = "#a9a9a4"

NODES = [
    ("A student reports\nwhat they see", "(one tap)"),
    ("Staff see it\nin one queue", "(oldest fault first)"),
    ("They repair it\nand mark it done", "(only they can)"),
    ("The record updates\nfor everyone", "(the loop starts again)"),
]

CENTRE_TOP = "Every entry carries"
CENTRE_MAIN = "the date of\nits last check"
CENTRE_SUB = "so an old check looks old,\nand a fresh one is worth trusting"
LOOP_NOTE = ("The next student sees the new state. If it is wrong again,\n"
             "they report it, and the loop turns once more.")

BOXES = [
    (30, 84, 70, 98),
    (72, 43, 99, 57),
    (30, 16, 70, 30),
    (1, 43, 28, 57),
]


def draw(active, path):
    fig, ax = plt.subplots(figsize=(8.6, 7.2), dpi=220)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 104)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    def txt(x, y, s, size=10, color=INK, weight="normal", ls=1.6):
        ax.text(x, y, s, fontsize=size, color=color, fontweight=weight,
                ha="center", va="center", linespacing=ls, zorder=6)

    def card(i, x0, y0, x1, y1, title, sub, num):
        on = active is None or active == i
        edge = ACCENT if (active is not None and on) else (LINE if active is None else DIM_LINE)
        face = CARD if on else DIM_CARD
        width = 2.0 if (active is not None and on) else 1.1
        ax.add_patch(FancyBboxPatch((x0 + 0.7, y0 - 0.7), x1 - x0, y1 - y0,
                                    boxstyle="round,pad=0.55,rounding_size=2.0",
                                    linewidth=0, facecolor="#e9e9e6", zorder=1))
        ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0,
                                    boxstyle="round,pad=0.55,rounding_size=2.0",
                                    linewidth=width, edgecolor=edge, facecolor=face, zorder=3))
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        tcol = INK if on else DIM_TEXT
        scol = (ACCENT if on else MUTED) if active is not None else MUTED
        txt(cx, cy + 2.6, f"{num}   {title}", 9.6, tcol, "bold")
        txt(cx, cy - 4.8, sub, 8.0, scol if on else DIM_TEXT)

    def arrow(p1, p2, hot):
        ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", connectionstyle="arc3,rad=0",
                                     mutation_scale=14,
                                     linewidth=1.6 if hot else 1.0,
                                     color=ACCENT if hot else (LINE if active is None else DIM_LINE),
                                     shrinkA=6, shrinkB=6, zorder=2))

    for i, (x0, y0, x1, y1) in enumerate(BOXES, start=1):
        card(i, x0, y0, x1, y1, NODES[i - 1][0], NODES[i - 1][1], i)

    hot_map = {
        1: (True, False, False, False),    # 1 -> 2
        2: (False, True, False, False),    # 2 -> 3
        3: (False, False, True, False),    # 3 -> 4
        4: (False, False, False, True),    # 4 -> 1
    }
    hot = hot_map.get(active, (False, False, False, False))
    arrow((68.2, 83.6), (73.4, 57.6), hot[0])
    arrow((73.2, 42.6), (68.2, 30.4), hot[1])
    arrow((31.8, 29.6), (26.6, 42.6), hot[2])
    arrow((26.8, 57.6), (31.8, 83.6), hot[3])

    txt(50, 66, CENTRE_TOP, 9.2, MUTED)
    txt(50, 58.5, CENTRE_MAIN, 10.8, INK, "bold", ls=1.4)
    txt(50, 49.2, CENTRE_SUB, 8.4, MUTED, ls=1.7)

    ax.add_patch(FancyBboxPatch((16, 1.5), 68, 12.0,
                                boxstyle="round,pad=0.55,rounding_size=1.8",
                                linewidth=1.0, edgecolor=LINE, facecolor="#f4f4f2",
                                linestyle=(0, (4, 3)), zorder=3))
    txt(50, 7.5, LOOP_NOTE, 8.2, INK, ls=1.9)
    arrow((50, 13.5), (50, 17.4), active == 4)

    fig.savefig(path, facecolor="white", bbox_inches="tight")
    plt.close(fig)


def main():
    os.makedirs(OUT, exist_ok=True)
    draw(None, os.path.join(OUT, "loop-demo-base.png"))
    for i in range(1, 5):
        draw(i, os.path.join(OUT, "loop-demo-%d.png" % i))
    print("wrote loop-demo-base.png and loop-demo-1..4.png into", OUT)


if __name__ == "__main__":
    main()
