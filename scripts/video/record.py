#!/usr/bin/env python3
"""Record a real session of the running app with Chrome's screencast, so the pitch
video shows the product rather than slides.

  python3 scripts/video/record.py /tmp/rec

Frames land as frame-00001.jpg ... with a timestamps.json next to them; build.py
turns those into an MP4. Needs the API on :8081 and the web app on :5175.
"""
import json
import os
import subprocess
import sys
import threading
import time
import urllib.request

import websocket  # websocket-client

WEB = os.environ.get("SF_WEB", "http://localhost:5175")
API = os.environ.get("SF_API", "http://127.0.0.1:8081")
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/rec"
W, H = 1280, 800
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def login(email, password="demo1234"):
    req = urllib.request.Request(
        API + "/api/auth/login",
        data=json.dumps({"email": email, "password": password}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


class Recorder:
    def __init__(self, port=9222):
        self.proc = subprocess.Popen(
            [
                CHROME,
                "--headless=new",
                "--remote-debugging-port=%d" % port,
                "--window-size=%d,%d" % (W, H),
                "--hide-scrollbars",
                "--disable-gpu",
                "--no-first-run",
                "--user-data-dir=/tmp/sf-rec-profile",
                "about:blank",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        ws_url = None
        for _ in range(50):
            try:
                with urllib.request.urlopen("http://127.0.0.1:%d/json/list" % port) as r:
                    for t in json.loads(r.read()):
                        if t["type"] == "page":
                            ws_url = t["webSocketDebuggerUrl"]
                            break
            except Exception:
                pass
            if ws_url:
                break
            time.sleep(0.2)
        if not ws_url:
            raise RuntimeError("chrome did not open a debugger")
        self.ws = websocket.create_connection(ws_url, timeout=30)
        self.ID = 0
        self.frames = 0
        self.times = []
        self.stop = False
        self.lock = threading.Lock()
        os.makedirs(OUT, exist_ok=True)
        for f in os.listdir(OUT):
            if f.startswith("frame-"):
                os.remove(os.path.join(OUT, f))

    def send(self, method, **params):
        self.ID += 1
        self.ws.send(json.dumps({"id": self.ID, "method": method, "params": params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == self.ID:
                if "error" in msg:
                    raise RuntimeError("%s: %s" % (method, msg["error"]))
                return msg.get("result", {})
            self._frame(msg)

    def _frame(self, msg):
        if msg.get("method") != "Page.screencastFrame":
            return
        p = msg["params"]
        with self.lock:
            self.frames += 1
            path = os.path.join(OUT, "frame-%05d.jpg" % self.frames)
            with open(path, "wb") as fh:
                import base64

                fh.write(base64.b64decode(p["data"]))
            self.times.append({"frame": self.frames, "t": p["metadata"]["timestamp"]})
        self.ID += 1
        self.ws.send(json.dumps({"id": self.ID, "method": "Page.screencastFrameAck",
                                 "params": {"sessionId": p["sessionId"]}}))

    def pump(self, seconds):
        """Keep reading frames for a while (no command in flight)."""
        end = time.time() + seconds
        self.ws.settimeout(0.2)
        while time.time() < end:
            try:
                msg = json.loads(self.ws.recv())
            except Exception:
                continue
            self._frame(msg)
        self.ws.settimeout(30)

    def js(self, expr):
        r = self.send("Runtime.evaluate", expression=expr, returnByValue=True,
                      awaitPromise=True)
        return r.get("result", {}).get("value")

    def rect(self, selector):
        return self.js(
            "(function(){var e=document.querySelector(%s); if(!e) return null;"
            " var r=e.getBoundingClientRect();"
            " return {x:r.x+r.width/2, y:r.y+r.height/2, w:r.width, h:r.height};})()"
            % json.dumps(selector)
        )

    def move(self, x, y):
        self.send("Input.dispatchMouseEvent", type="mouseMoved", x=x, y=y, buttons=0)
        self.pump(0.35)

    def click(self, x, y):
        self.move(x, y)
        self.send("Input.dispatchMouseEvent", type="mousePressed", x=x, y=y,
                  button="left", buttons=1, clickCount=1)
        self.pump(0.08)
        self.send("Input.dispatchMouseEvent", type="mouseReleased", x=x, y=y,
                  button="left", buttons=0, clickCount=1)
        self.pump(0.9)

    def click_selector(self, selector, hover_only=False):
        r = self.rect(selector)
        if not r:
            raise RuntimeError("no element for " + selector)
        if hover_only:
            self.move(r["x"], r["y"])
        else:
            self.click(r["x"], r["y"])
        return r

    def start(self, session_state, path="/"):
        self.send("Page.enable")
        self.send("Runtime.enable")
        self.send("Emulation.setDeviceMetricsOverride", width=W, height=H,
                  deviceScaleFactor=2, mobile=False)
        self.send("Page.addScriptToEvaluateOnNewDocument",
                  source="localStorage.setItem('sf_token', %s);"
                         "localStorage.setItem('sf_user', %s);"
                         "localStorage.setItem('sf_lang', 'en');"
                         % (json.dumps(session_state["token"]),
                            json.dumps(json.dumps({"displayName": session_state["displayName"],
                                                   "role": session_state["role"],
                                                   "email": session_state["email"]}))))
        self.send("Page.navigate", url=WEB + path)
        self.pump(2.5)
        self.send("Page.startScreencast", format="jpeg", quality=82,
                  maxWidth=W, maxHeight=H, everyNthFrame=1)

    def close(self):
        try:
            self.send("Page.stopScreencast")
        except Exception:
            pass
        with open(os.path.join(OUT, "timestamps.json"), "w") as fh:
            json.dump(self.times, fh)
        self.ws.close()
        self.proc.terminate()
        return self.frames


def main():
    student = login("student2@connect.hku.hk")
    staff = login("estates@hku.hk")
    rec = Recorder()
    rec.start(student)
    try:
        # 1. home: four buildings, rooms sorted by how much is wrong with them
        rec.pump(2.2)
        rec.move(300, 430)
        rec.pump(0.9)
        rec.click_selector(".room")            # L1-B sorts first: one dead, one loose
        rec.pump(2.6)

        # 2. the room: plan first, then the list underneath
        rec.js("window.scrollTo(0, 0)")
        rec.pump(1.4)
        rec.move(390, 440)                     # hover the loose socket on the plan
        rec.pump(1.2)

        # 3. the same screen in the other two languages
        rec.js("[...document.querySelectorAll('.lang')].find(b=>b.textContent.trim()==='繁').click()")
        rec.pump(2.0)
        rec.js("[...document.querySelectorAll('.lang')].find(b=>b.textContent.trim()==='简').click()")
        rec.pump(1.8)
        rec.js("[...document.querySelectorAll('.lang')].find(b=>b.textContent.trim()==='EN').click()")
        rec.pump(1.4)
    finally:
        n = rec.close()
    print("frames:", n)
    print("out:", OUT)


if __name__ == "__main__":
    main()
