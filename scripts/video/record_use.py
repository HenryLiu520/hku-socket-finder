"""Segment A of the demo: how you use it, and one report going in.

  python3 scripts/video/record_use.py /tmp/uA

Beats (about 35 s of screen time; the cut and the narration come later):
  1. home, four buildings, hover a room card
  2. open L1-B
  3. plan appears, hover the socket that has no state yet
  4. scroll to the list so "Last changed" is on screen
  5. scroll back, open that socket, report it as loose
  6. the socket turns orange on the plan
"""
import sys

sys.path.insert(0, "/Users/ran/Documents/课程/CCST9003/项目/socket-finder/scripts/video")
import record as R  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/uA"
R.OUT = OUT

FIND_SOCKET = ("(function(){var g=[...document.querySelectorAll('g.sock')]"
               ".find(function(x){return /0004/.test(x.textContent)});"
               "if(!g) return null; var b=g.getBoundingClientRect();"
               "return {x:b.x+b.width/2,y:b.y+b.height/2};})()")

who = R.login("student2@connect.hku.hk")
rec = R.Recorder(port=9411)
rec.start(who, "/")

try:
    rec.pump(2.6)
    card = rec.rect(".room")
    if card:
        rec.move(card["x"], card["y"] - 40)
    rec.pump(1.4)

    rec.click_selector(".room")
    rec.pump(2.8)

    # plan at the top: hover the unchecked socket
    rec.js("window.scrollTo(0, 0)")
    rec.pump(1.0)
    s = rec.js(FIND_SOCKET)
    if s:
        rec.move(s["x"], s["y"])
    rec.pump(1.6)

    # the list underneath: "last checked" / "last report"
    rec.js("window.scrollTo(0, 250)")
    rec.pump(2.2)

    # back to the plan, open the socket, report it
    rec.js("window.scrollTo(0, 0)")
    rec.pump(0.9)
    rec.js("[...document.querySelectorAll('g.sock')]"
           ".find(function(x){return /0004/.test(x.textContent)})"
           ".dispatchEvent(new MouseEvent('click',{bubbles:true}))")
    rec.pump(1.4)
    rec.js("(function(){var b=[...document.querySelectorAll('.el-dialog button')]"
           ".find(function(x){return /loose/i.test(x.textContent)}); if(b) b.click();})()")
    rec.pump(2.0)
    rec.send("Input.dispatchKeyEvent", type="keyDown", key="Escape", code="Escape", windowsVirtualKeyCode=27)
    rec.send("Input.dispatchKeyEvent", type="keyUp", key="Escape", code="Escape", windowsVirtualKeyCode=27)
    rec.pump(0.8)
    rec.js("window.scrollTo(0, 0)")
    rec.pump(2.6)
finally:
    n = rec.close()

print("frames=%d out=%s" % (n, OUT))
