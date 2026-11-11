#!/usr/bin/env python3
"""One-page poster: how the record stays honest (reputation) and why people keep it.

  python3 scripts/make_incentive_poster.py out.pdf

A4 landscape. Chrome prints it, so the type and the SVG line up the same way they
will on paper.
"""
import os
import subprocess
import sys
import tempfile

OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "R21_incentive_poster.pdf")
PNG = OUT.replace(".pdf", ".png")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

HTML = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<style>
  @page { size: A4 landscape; margin: 0; }
  * { box-sizing: border-box; margin: 0; }
  body { width: 297mm; height: 210mm; padding: 12mm 14mm 9mm;
         display: flex; flex-direction: column;
         font: 11pt/1.6 -apple-system, "Helvetica Neue", "PingFang SC", Arial, sans-serif;
         color: #1f2d2a; background: #f7faf8; position: relative; overflow: hidden; }
  .wash { position: absolute; inset: 0; z-index: 0;
          background:
            radial-gradient(120mm 70mm at 8% -8%, rgba(2,70,56,.16), transparent 70%),
            radial-gradient(110mm 70mm at 98% -6%, rgba(180,151,100,.20), transparent 70%);
  }
  .rule { position: absolute; top: 0; left: 0; right: 0; height: 3px; z-index: 2;
          background: linear-gradient(90deg, #024638 0%, #024638 42%, #b49764 100%); }
  header, main, footer { position: relative; z-index: 1; }
  .kicker { font-size: 7.6pt; letter-spacing: 2px; text-transform: uppercase; color: #b49764;
            font-weight: 700; }
  h1 { font-size: 29pt; line-height: 1.12; margin: 3mm 0 1.5mm; color: #024638; letter-spacing: -.4px; }
  h1 em { font-style: normal; color: #b49764; }
  .lede { font-size: 11.4pt; color: #4b5b57; max-width: 190mm; }
  .lede b { color: #024638; }

  main { display: grid; grid-template-columns: 1fr 1fr; gap: 9mm; margin-top: 7mm; flex: 1; min-height: 0; }
  .panel { background: #fff; border: 1px solid #dbe6e1; border-radius: 4mm; padding: 6mm 6.5mm 5mm;
           display: flex; flex-direction: column;
           box-shadow: 0 10mm 20mm -16mm rgba(2,70,56,.55); }
  .panel h2 { font-size: 15pt; color: #024638; letter-spacing: -.2px; }
  .panel .zh { display: block; font-size: 8.6pt; color: #8c9a95; font-weight: 400; margin-top: .6mm; }
  .panel .num { display: inline-block; font-size: 8pt; font-weight: 700; letter-spacing: 1.4px;
                color: #b49764; text-transform: uppercase; margin-bottom: 1.5mm; }
  .diagram { margin: 4mm 0 3mm; }
  ol { list-style: none; padding: 0; margin: 0; }
  .panel ol { margin: auto 0; }
  li { position: relative; padding-left: 6.5mm; margin-bottom: 2.8mm; font-size: 10.2pt; color: #33433f; }
  li::before { content: ""; position: absolute; left: 0; top: 1.6mm; width: 2.6mm; height: 2.6mm;
               border-radius: 50%; border: 1.6px solid #0b6b4f; background: #eaf3ef; }
  li b { color: #024638; }
  .note { font-size: 8.6pt; color: #7b8a85; margin-top: auto; padding-top: 2.5mm;
          border-top: 1px dashed #dbe6e1; }

  footer { margin-top: 5mm; flex: 0 0 auto; display: flex; align-items: center; justify-content: space-between;
           border-top: 1px solid #d7e3de; padding-top: 3.5mm; }
  .loopline { font-size: 9.6pt; color: #024638; }
  .loopline b { color: #b49764; }
  .sig { font-size: 8pt; color: #8c9a95; text-align: right; }
</style></head>
<body>
<div class="wash"></div><div class="rule"></div>

<header>
  <div class="kicker">Socket Finder · Group R21 · CCST9003</div>
  <h1>Keeping the record <em>worth trusting</em></h1>
  <p class="lede">A crowdsourced record only works if two things are true: the people who report are
  <b>judged on how right they were</b>, and the ones who keep reporting <b>get something back</b>.</p>
</header>

<main>
  <section class="panel">
    <div class="num">01 · Reputation</div>
    <h2>Every report is scored after the fact<span class="zh">每条上报都会事后计分</span></h2>

    <svg class="diagram" viewBox="0 0 300 96" width="100%" height="25mm">
      <defs>
        <marker id="a" markerWidth="7" markerHeight="7" refX="5.6" refY="3" orient="auto">
          <path d="M0,0 L6,3 L0,6 z" fill="#9db3ac"/>
        </marker>
      </defs>
      <g font-family="-apple-system, Arial" text-anchor="middle">
        <rect x="0" y="26" width="76" height="44" rx="7" fill="#f2f7f5" stroke="#cfe0db"/>
        <text x="38" y="45" font-size="10" fill="#024638" font-weight="700">Record</text>
        <text x="38" y="58" font-size="8.4" fill="#7b8a85">what was reported</text>

        <rect x="94" y="26" width="76" height="44" rx="7" fill="#f2f7f5" stroke="#cfe0db"/>
        <text x="132" y="45" font-size="10" fill="#024638" font-weight="700">Outcome</text>
        <text x="132" y="58" font-size="8.4" fill="#7b8a85">repair, later reports</text>

        <rect x="188" y="18" width="112" height="60" rx="8" fill="#024638" stroke="#024638"/>
        <text x="244" y="38" font-size="10" fill="#f2ece1" font-weight="700">Score</text>
        <text x="244" y="51" font-size="8.4" fill="#c9d6d1">right: + · wrong: −</text>
        <text x="244" y="63" font-size="8.4" fill="#c9d6d1">weights the next one</text>
      </g>
      <line x1="78" y1="48" x2="90" y2="48" stroke="#9db3ac" stroke-width="1.6" marker-end="url(#a)"/>
      <line x1="172" y1="48" x2="184" y2="48" stroke="#9db3ac" stroke-width="1.6" marker-end="url(#a)"/>
    </svg>

    <ol>
      <li><b>The score comes from the records.</b> A report later confirmed by a repair, or by people
      who checked the same socket, moves the account up. One that turns out wrong moves it down.</li>
      <li><b>The score is what a report is worth.</b> A longer record of being right carries more
      weight in what the next person sees.</li>
      <li><b>It is visible, so it is a judgement.</b> Staff can see who has been reliable; a new
      account starts with nothing to prove.</li>
    </ol>
    <p class="note">The score belongs to the account, never to the socket.</p>
  </section>

  <section class="panel">
    <div class="num">02 · Rewards</div>
    <h2>Enough good updates earns something real<span class="zh">足够数量的正向更新，会得到实际奖励</span></h2>

    <svg class="diagram" viewBox="0 0 300 96" width="100%" height="25mm">
      <g font-family="-apple-system, Arial" text-anchor="middle">
        <circle cx="52" cy="48" r="30" fill="#f2f7f5" stroke="#cfe0db"/>
        <text x="52" y="45" font-size="9.6" fill="#024638" font-weight="700">n updates</text>
        <text x="52" y="57" font-size="8.6" fill="#7b8a85">still holding</text>

        <circle cx="150" cy="48" r="30" fill="#f2f7f5" stroke="#cfe0db"/>
        <text x="150" y="45" font-size="9.6" fill="#024638" font-weight="700">Gift</text>
        <text x="150" y="57" font-size="8.6" fill="#7b8a85">voucher, badge</text>

        <circle cx="248" cy="48" r="30" fill="#024638" stroke="#024638"/>
        <text x="248" y="45" font-size="9.2" fill="#f2ece1" font-weight="700">More</text>
        <text x="248" y="57" font-size="8.2" fill="#c9d6d1">people report</text>
      </g>
      <line x1="84" y1="48" x2="118" y2="48" stroke="#9db3ac" stroke-width="1.6" marker-end="url(#a)"/>
      <line x1="182" y1="48" x2="216" y2="48" stroke="#9db3ac" stroke-width="1.6" marker-end="url(#a)"/>
    </svg>

    <ol>
      <li><b>The trigger is positive information, in volume.</b> Not one tap: enough updates that hold
      up over time.</li>
      <li><b>The reward is small and material.</b> A campus voucher, a badge — worth ten seconds, never
      worth faking.</li>
      <li><b>Rewards follow the same number as reputation,</b> so nobody can farm one without the
      other.</li>
    </ol>
    <p class="note">Small on purpose: coffee money, not a bounty.</p>
  </section>
</main>

<footer>
  <div class="loopline">More accurate reports <b>→</b> higher score <b>→</b> more weight and rewards
  <b>→</b> more people report <b>→</b> the record stays fresh.</div>
  <div class="sig">Every entry carries the date of its last check.</div>
</footer>
</body></html>
"""


def main():
    tmp = os.path.join(tempfile.gettempdir(), "incentive_poster.html")
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(HTML)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    "--print-to-pdf=" + OUT, "file://" + tmp],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--window-size=1122,794", "--force-device-scale-factor=2",
                    "--screenshot=" + PNG, "file://" + tmp],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    print("wrote %s (%.0f KB) and %s" % (OUT, os.path.getsize(OUT) / 1024, PNG))


if __name__ == "__main__":
    main()
