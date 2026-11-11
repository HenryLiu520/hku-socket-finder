#!/usr/bin/env python3
"""Retake the screenshots in docs/screens from the running app.

  python3 scripts/capture_screens.py            # writes docs/screens/{desktop,mobile}

Desktop shots are 1440x900 at 2x, phone shots 390x844 at 2x, both with a real session
injected and the language switcher hidden, so the pictures show the product rather
than the testing controls. The backend must be on :8081 and the dev server on :5175.
"""
import base64
import io
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts", "video"))
import record as R  # noqa: E402

R.WEB = "http://localhost:5175"
SHOTS = os.path.join(ROOT, "docs", "screens")


def grab(rec, path, out_file, settle=2.6):
    rec.send("Page.navigate", url=R.WEB + path)
    rec.pump(settle)
    data = rec.send("Page.captureScreenshot", format="png", fromSurface=True)
    raw = base64.b64decode(data["data"])
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    # 2x capture, downscaled to the width a README actually shows, saved as jpg
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    target = 1440 if img.width > 1600 else 780
    if img.width != target:
        img = img.resize((target, round(img.height * target / img.width)), Image.LANCZOS)
    img.save(out_file, "JPEG", quality=88, optimize=True, progressive=True)
    print("wrote %-52s %6.0f KB" % (os.path.relpath(out_file, ROOT), os.path.getsize(out_file) / 1024))


def session(width, height, who, jobs):
    R.W, R.H = width, height
    rec = R.Recorder(port=9411)
    rec.start(who, "/")
    rec.send("Page.stopScreencast")          # stills, not frames
    for path, out in jobs:
        grab(rec, path, out)
    rec.close()


def main():
    student = R.login("student2@connect.hku.hk")
    staff = R.login("estates@hku.hk")

    session(1440, 900, student, [
        ("/", os.path.join(SHOTS, "desktop", "01-find-a-socket.jpg")),
        ("/rooms/12", os.path.join(SHOTS, "desktop", "02-room-and-plan.jpg")),
        ("/report", os.path.join(SHOTS, "desktop", "03-report-a-fault.jpg")),
    ])
    session(1440, 900, staff, [
        ("/maintenance", os.path.join(SHOTS, "desktop", "04-repair-queue.jpg")),
    ])
    session(390, 844, student, [
        ("/rooms/12", os.path.join(SHOTS, "mobile", "05-phone-room.jpg")),
        ("/report", os.path.join(SHOTS, "mobile", "06-phone-report.jpg")),
    ])


if __name__ == "__main__":
    main()
