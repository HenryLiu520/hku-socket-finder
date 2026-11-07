#!/usr/bin/env python3
"""Render the pitch-video plan as a bilingual A4 PDF.

  python3 scripts/make_pitch_plan_pdf.py out.pdf

Chrome does the layout (it is the only renderer here with good CJK), so the file is
built as HTML with token placeholders and printed with --print-to-pdf. No % formatting,
because the stylesheet is full of percent signs.
"""
import os
import subprocess
import sys
import tempfile

OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "R21_pitch_plan_bilingual.pdf")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

REQ = [
    ("L1 overview, group project slide",
     "Design and present an <b>innovative</b> project on a new computing service or futuristic "
     "application. Submission is a <b>3-min pitch video</b>. Grading: 10% individual presentation "
     "+ 30% group video.",
     "要求设计并展示一个<b>创新</b>项目（新的计算服务或未来应用）；提交物是 <b>3 分钟 pitch 影片</b>；"
     "计分 10% 个人 presentation + 30% 小组影片。"),
    ("Moodle, video entry",
     "3 minutes, due 29 Nov 23:59, <code>30 secs show up (of at least 2 members) any time in the "
     "3 mins video</code>, one copy per group.",
     "3 分钟，11 月 29 日 23:59 截止，<code>30 secs show up (of at least 2 members) any time in the "
     "3 mins video</code>，每组交一份。"),
    ("Neither document",
     "No required business, ethics or team section. Those belong to the exec document and the "
     "presentation.",
     "<b>没有</b>要求商业 / 伦理 / 团队段落 —— 那些属于 exec 文档和 presentation。"),
]

TIMELINE = [
    ("0:00-0:15", "A student sits, plugs in, nothing. He tries the next socket, nothing again.",
     "学生坐下插电，没反应；换一支，还是没反应。"),
    ("0:15-0:30", "A friend walks over, taps his shoulder, shows his phone.",
     "朋友走过来拍拍肩，把手机递给他看。"),
    ("0:30-0:45", "On the phone: four buildings, one room, a plan of numbered sockets, one green "
     "desk. They get up and walk.",
     "手机上是四栋楼、一间房、带编号的插座平面图，有一支是绿的。两人起身走过去。"),
    ("0:45-1:00", "He sits at that desk, plugs in, the laptop charges. He looks up and nods. "
     "Cut to the screen.",
     "他在那个位置坐下插电，笔电亮了，抬头点头。切到屏幕。"),
    ("1:00-2:04", "Screen demo, already cut: 1:04, English subtitles.",
     "系统演示，已剪好：1 分 04 秒，英文字幕。"),
    ("2:04-2:35", "Talking to camera: why people keep the record honest — a score from reports "
     "that turned out right, and how that score weights one report.",
     "对镜头讲激励机制：报得准会累积信誉分，分数决定一次上报的权重。"),
    ("2:35-3:00", "One line of value, then the end card.", "一句价值 + 片尾卡。"),
]

DEMO = [
    ("0:00", "Title card.", "片头卡。"),
    ("0:02", "Four buildings, rooms sorted by what is wrong with them.", "四栋楼，房间按坏多少排序。"),
    ("0:08", "Opening one room.", "点进一间房。"),
    ("0:12", "The floor plan: every socket has a four-digit number.", "平面图：每支插座一个四位数编号。"),
    ("0:17", "Green works, orange loose, red dead; the list gives the last check date.",
     "绿=可用、橙=松动、红=没电；列表给上次核查日期。"),
    ("0:23", "Reporting one socket; it turns orange on the spot.", "上报一支插座，当场变橙。"),
    ("0:32", "The staff queue with that socket in it.", "维护队列里能看到这一支。"),
    ("0:36", "Closing it; the room shows the new state.", "标修好；房间页显示新状态。"),
    ("0:43", "The four-step loop, one step at a time.", "四步闭环图，一步一高亮。"),
    ("1:01", "End card.", "片尾卡。"),
]

INCENTIVE = [
    ("Why keep reporting: a score built from reports that turned out right; a higher score makes "
     "one report count for more.",
     "报得准会累积信誉分；分数高，一次上报的权重更大。"),
    ("The ten-a-day cap is the floor: no score buys unlimited reports.",
     "每天十次是地板：积分再高也不能刷。"),
    ("Rewards hang off the same number: badges, and a visible record of what you have kept accurate.",
     "奖励挂在同一个分数上：徽章，以及一份「你维护过什么」的可见记录。"),
    ("One line: first make the record worth trusting, then make keeping it worth someone's time.",
     "一句话：先让记录值得信，再让维护它值得花时间。"),
]

SHOOT = [
    ("Chi Wah L1, early morning or late evening, same clothes for every setup.",
     "慧卿 L1，早上或傍晚人少时；各场次同一套衣服。"),
    ("Phone, landscape, 1080p, tripod or window sill. Keep the walking shot steady.",
     "手机横屏 1080p，三脚架或靠窗台；走路那镜头要稳。"),
    ("0:30-0:45 needs a real phone screen: film the phone itself showing the room plan.",
     "0:30–0:45 需要一段真实手机屏幕：实拍手机显示的平面图。"),
    ("Copyright-free music under -20 dB. Export <code>R21_pitch.mp4</code>, H.264.",
     "无版权音乐压到 −20 dB 以下；导出 <code>R21_pitch.mp4</code>，H.264。"),
]


def tr(first, en, zh, cls="l"):
    return '<tr><td class="%s">%s</td><td>%s</td><td class="zh">%s</td></tr>' % (cls, first, en, zh)


def table2(items):
    return "\n".join('<tr><td>%s</td><td class="zh2">%s</td></tr>' % (en, zh) for en, zh in items)


def table(items, first_is_time=True):
    rows = []
    for item in items:
        if len(item) == 3:
            first, en, zh = item
        else:
            en, zh = item
            first = "·"
        rows.append(tr(first, en, zh, "t" if first_is_time else "l"))
    return "\n".join(rows)


TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<style>
  @page { size: A4; margin: 15mm 13mm 13mm; }
  * { box-sizing: border-box; }
  body { font: 9.5pt/1.5 -apple-system, "Helvetica Neue", "PingFang SC", Arial, sans-serif;
         color: #1f2d2a; margin: 0; }
  header { border-bottom: 2px solid #024638; padding-bottom: 7px; margin-bottom: 12px; }
  .kicker { font-size: 8.2pt; letter-spacing: 1.4px; text-transform: uppercase; color: #b49764;
            font-weight: 700; }
  h1 { font-size: 18.5pt; margin: 4px 0 2px; color: #024638; letter-spacing: -.3px; }
  h1 .zh { font-weight: 400; font-size: 12pt; color: #6b7b77; }
  .sub { font-size: 8.8pt; color: #6b7b77; }
  h2 { font-size: 11.2pt; color: #024638; margin: 14px 0 5px; }
  h2 .zh { font-weight: 400; color: #6b7b77; font-size: 9.4pt; }
  table { width: 100%; border-collapse: collapse; margin-bottom: 4px; }
  th { text-align: left; font-size: 8.4pt; text-transform: uppercase; letter-spacing: .6px;
       color: #6b7b77; border-bottom: 1px solid #cfe0db; padding: 4px 6px; font-weight: 700; }
  td { vertical-align: top; padding: 4.6px 6px; border-bottom: 1px solid #eef2f0; }
  td.t { white-space: nowrap; font-weight: 700; color: #024638; width: 14%; }
  td.l { width: 24%; font-weight: 650; color: #024638; }
  td.zh { width: 32%; color: #33433f; border-left: 1px solid #f2f6f4; }
  td.zh2 { width: 42%; color: #33433f; border-left: 1px solid #f2f6f4; }
  code { font-family: ui-monospace, Menlo, monospace; font-size: 8.4pt; background: #f1f6f3;
         padding: 1px 3px; border-radius: 3px; }
  .note { font-size: 8.7pt; color: #6b7b77; margin: 3px 0 10px; }
  footer { margin-top: 14px; border-top: 1px solid #cfe0db; padding-top: 5px;
           font-size: 8.2pt; color: #6b7b77; }
</style></head>
<body>
<header>
  <div class="kicker">CCST9003 · Group R21 · Socket Finder</div>
  <h1>Pitch video plan <span class="zh">影片方案</span></h1>
  <div class="sub">3:00 target · all English on screen · bilingual document for review</div>
</header>

<h2>What the course asks for <span class="zh">课程要求</span></h2>
<table><thead><tr><th>Source</th><th>Requirement</th><th>中文</th></tr></thead>
<tbody>
{{REQ}}
</tbody></table>
<p class="note">The 30-second on-camera rule is a floor, not a target, so the acted opening now
carries the first minute. <span class="zh">30 秒出镜是下限不是目标，所以开场演绎拉到一分钟。</span></p>

<h2>Timeline <span class="zh">时间轴</span></h2>
<table><thead><tr><th>Time</th><th>English</th><th>中文</th></tr></thead>
<tbody>{{TIMELINE}}</tbody></table>

<h2>The screen demo, already recorded <span class="zh">系统演示（已剪好）</span></h2>
<table><thead><tr><th>Time</th><th>English</th><th>中文</th></tr></thead>
<tbody>{{DEMO}}</tbody></table>

<h2>Incentives, 2:04-2:35 <span class="zh">激励机制</span></h2>
<table><thead><tr><th>English</th><th>中文</th></tr></thead>
<tbody>{{INCENTIVE}}</tbody></table>

<h2>Shoot notes <span class="zh">拍摄注意</span></h2>
<table><thead><tr><th>English</th><th>中文</th></tr></thead>
<tbody>{{SHOOT}}</tbody></table>

<footer>Socket Finder · Group R21 · CCST9003 · plan for the 3-minute pitch video, due 29 Nov 23:59</footer>
</body></html>
"""


def main():
    html = (TEMPLATE
            .replace("{{REQ}}", "\n".join(tr(a, b, c) for a, b, c in REQ))
            .replace("{{TIMELINE}}", table(TIMELINE))
            .replace("{{DEMO}}", table(DEMO))
            .replace("{{INCENTIVE}}", table2(INCENTIVE))
            .replace("{{SHOOT}}", table2(SHOOT)))
    tmp = os.path.join(tempfile.gettempdir(), "pitch_plan.html")
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(html)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    "--print-to-pdf=" + OUT, "file://" + tmp],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    print("wrote %s (%.1f KB)" % (OUT, os.path.getsize(OUT) / 1024))


if __name__ == "__main__":
    main()
