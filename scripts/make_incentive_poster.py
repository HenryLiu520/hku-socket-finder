#!/usr/bin/env python3
"""One slide: Reputation on the left, Rewards on the right, nothing else.

  python3 scripts/make_incentive_poster.py out.pdf

Built to be filmed: 16:9, very large type, no small print, no Chinese. The words are
the two points as stated, with the earlier headings demoted to subtitles.
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
  @page { size: 16in 9in; margin: 0; }
  * { box-sizing: border-box; margin: 0; }
  html, body { width: 1920px; height: 1080px; }
  body { padding: 54px 62px 48px; background: #f7faf8; color: #1f2d2a;
         font-family: -apple-system, "Helvetica Neue", Arial, sans-serif;
         display: flex; flex-direction: column; position: relative; overflow: hidden; }
  .wash { position: absolute; inset: 0; z-index: 0;
          background:
            radial-gradient(900px 520px at 4% -12%, rgba(2,70,56,.20), transparent 70%),
            radial-gradient(820px 520px at 102% -10%, rgba(180,151,100,.26), transparent 70%); }
  .rule { position: absolute; top: 0; left: 0; right: 0; height: 8px; z-index: 2;
          background: linear-gradient(90deg, #024638 0%, #024638 40%, #b49764 100%); }
  header, main { position: relative; z-index: 1; }

  .kicker { font-size: 26px; letter-spacing: 6px; text-transform: uppercase; color: #a8875a;
            font-weight: 700; }

  main { display: grid; grid-template-columns: 1fr 1fr; gap: 46px; margin-top: 40px;
         flex: 1; min-height: 0; }
  .panel { background: #fff; border: 2px solid #d5e3dd; border-radius: 26px;
           padding: 46px 50px 44px; display: flex; flex-direction: column; justify-content: center;
           box-shadow: 0 40px 70px -50px rgba(2,70,56,.75); }

  h2 { font-size: 118px; line-height: 1; color: #024638; letter-spacing: -2.4px; }
  .sub { margin-top: 22px; font-size: 44px; line-height: 1.3; color: #47605a; font-weight: 500; }

  .diagram { margin: 52px 0 26px; }
  ol { list-style: none; padding: 0; margin: 6px 0 0; }
  li { position: relative; padding-left: 50px; margin-bottom: 32px; font-size: 48px;
       font-weight: 700; color: #024638; line-height: 1.25; }
  li:last-child { margin-bottom: 0; }
  li::before { content: ""; position: absolute; left: 0; top: 15px; width: 20px; height: 20px;
               border-radius: 50%; background: #0b6b4f; }
</style></head>
<body>
<div class="wash"></div><div class="rule"></div>

<header>
  <div class="kicker">Sure Socket · Group R21</div>
</header>

<main>
  <section class="panel">
    <h2>Reputation</h2>
    <p class="sub">Every report is scored, after the fact.</p>

    <svg class="diagram" viewBox="0 0 620 120" width="100%" height="190">
      <defs>
        <marker id="a" markerWidth="7" markerHeight="7" refX="5.4" refY="3" orient="auto">
          <path d="M0,0 L6,3 L0,6 z" fill="#9db3ac"/>
        </marker>
      </defs>
      <g font-family="-apple-system, Arial" text-anchor="middle" font-weight="700">
        <rect x="0" y="26" width="176" height="68" rx="14" fill="#f2f7f5" stroke="#cfe0db" stroke-width="1.5"/>
        <text x="88" y="68" font-size="26" fill="#024638">Uploads</text>

        <rect x="222" y="26" width="176" height="68" rx="14" fill="#f2f7f5" stroke="#cfe0db" stroke-width="1.5"/>
        <text x="310" y="68" font-size="26" fill="#024638">Score</text>

        <rect x="444" y="16" width="176" height="88" rx="16" fill="#024638"/>
        <text x="532" y="70" font-size="27" fill="#f4efe6">Evaluation</text>
      </g>
      <line x1="180" y1="60" x2="216" y2="60" stroke="#9db3ac" stroke-width="2.4" marker-end="url(#a)"/>
      <line x1="402" y1="60" x2="438" y2="60" stroke="#9db3ac" stroke-width="2.4" marker-end="url(#a)"/>
    </svg>

    <ol>
      <li>Computed from the records</li>
      <li>Decides the evaluation</li>
    </ol>
  </section>

  <section class="panel">
    <h2>Rewards</h2>
    <p class="sub">Enough good updates earns something real.</p>

    <svg class="diagram" viewBox="0 0 620 120" width="100%" height="190">
      <g font-family="-apple-system, Arial" text-anchor="middle" font-weight="700">
        <circle cx="88" cy="60" r="58" fill="#f2f7f5" stroke="#cfe0db" stroke-width="1.5"/>
        <text x="88" y="68" font-size="25" fill="#024638">Updates</text>

        <circle cx="310" cy="60" r="58" fill="#f2f7f5" stroke="#cfe0db" stroke-width="1.5"/>
        <text x="310" y="68" font-size="26" fill="#024638">Gift</text>

        <circle cx="532" cy="60" r="58" fill="#024638"/>
        <text x="532" y="68" font-size="26" fill="#f4efe6">Loop</text>
      </g>
      <line x1="150" y1="60" x2="246" y2="60" stroke="#9db3ac" stroke-width="2.4" marker-end="url(#a)"/>
      <line x1="372" y1="60" x2="468" y2="60" stroke="#9db3ac" stroke-width="2.4" marker-end="url(#a)"/>
    </svg>

    <ol>
      <li>Enough updates earn a gift</li>
      <li>The loop turns virtuous</li>
    </ol>
  </section>
</main>
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
                    "--window-size=1920,1080", "--force-device-scale-factor=2",
                    "--screenshot=" + PNG, "file://" + tmp],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    print("wrote %s (%.0f KB) and %s" % (OUT, os.path.getsize(OUT) / 1024, PNG))


if __name__ == "__main__":
    main()
