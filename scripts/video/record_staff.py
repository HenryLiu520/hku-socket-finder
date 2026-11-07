"""The two extra segments the pitch demo needs: the staff queue, and the room after
the repair. Split out so each one starts from a clean session instead of switching
accounts in the middle of a recording.

  python3 scripts/video/record_staff.py /tmp/recB staff
  python3 scripts/video/record_staff.py /tmp/recC after
"""
import json
import sys

sys.path.insert(0, "/Users/ran/Documents/课程/CCST9003/项目/socket-finder/scripts/video")
import record as R  # noqa: E402

OUT = sys.argv[1]
MODE = sys.argv[2] if len(sys.argv) > 2 else "staff"

R.OUT = OUT
R.WEB = "http://localhost:5175"

if MODE == "staff":
    who = R.login("estates@hku.hk")
    start = "/maintenance"
else:
    who = R.login("student2@connect.hku.hk")
    start = "/"

rec = R.Recorder()
rec.start(who, start)
try:
    if MODE == "staff":
        rec.pump(2.6)
        rows = rec.js("document.querySelectorAll('tbody tr').length")
        if rows:
            # close the socket that was just reported (0004), not whatever is oldest
            rec.js("(function(){var r=[...document.querySelectorAll('tbody tr')]"
                   ".find(function(x){return /0004/.test(x.textContent)});"
                   "var b=(r||document.querySelector('tbody tr')).querySelector('button'); b.click();})()")
            rec.pump(1.2)
            rec.js("(function(){var b=[...document.querySelectorAll('.el-dialog button')]"
                   ".find(function(x){return /confirm|mark/i.test(x.textContent)}); if(b) b.click();})()")
            rec.pump(2.4)
    else:
        rec.send("Page.navigate", url=R.WEB + "/rooms/2")
        rec.pump(2.4)
        rec.js("window.scrollTo(0, 210)")
        rec.pump(1.4)
finally:
    n = rec.close()

print("mode=%s frames=%d out=%s" % (MODE, n, OUT))
