# Demo video pipeline

Records the running app and cuts a 30 second demo. No screen recorder, no manual
editing: Chrome's own screencast frames are assembled with ffmpeg.

## What it needs

- The app running: API on `:8081`, web on `:5175`, database seeded.
- `python3 -m pip install websocket-client pillow`
- `ffmpeg` with `overlay`, `fade`, `concat` (this build has no drawtext/libass,
  so cards and captions are drawn with Pillow and overlaid as PNGs).

## Three steps

```bash
# 0. a known-good data state
psql -h 127.0.0.1 -p 5433 -U ran -d socketfinder -v ON_ERROR_STOP=1 -f scripts/demo-reset.sql

# 1. record: student segment, staff segment, then the room after the repair
python3 scripts/video/record.py /tmp/rA
python3 scripts/video/record_staff.py /tmp/rB staff
python3 scripts/video/record_staff.py /tmp/rC after

# 2. cut it together (title card, captions, end card)
python3 scripts/video/build.py /tmp/rA /tmp/rB /tmp/rC /tmp/R21_demo.mp4

# 3. optional narration, one generated line per beat
python3 scripts/video/narrate.py /tmp/R21_demo.mp4 /tmp/vo /tmp/R21_demo_vo.mp4
```

## How the recording works

`record.py` starts headless Chrome with `--remote-debugging-port`, injects a real
session into `localStorage` through `Page.addScriptToEvaluateOnNewDocument`,
navigates, then calls `Page.startScreencast`. Frames only arrive when the page
actually changes, and each frame keeps its timestamp, so the cut plays back at the
speed a person saw it. Clicks are real mouse events at element centres.

## What it cannot do

There is no footage of people. The pitch video needs at least two members on
camera for thirty seconds, so those shots have to be filmed on a phone and cut in
after `build.py`; this pipeline only produces the screen part.
