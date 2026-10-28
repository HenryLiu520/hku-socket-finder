#!/usr/bin/env bash
# 结构一致性检查：
#   1) 三份 README 的节数 / 图片数 / 代码块数 / 互链必须一致
#   2) 三份 technical 文档的节数 / 代码块数必须一致
#   3) 每份 README 都要链到三份 technical 文档
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 - <<'PY'
import re, sys

def stats(path):
    text = open(path, encoding="utf-8").read()
    return {
        "sections": len(re.findall(r"^## ", text, re.M)),
        "images": len(re.findall(r"!\[", text)),
        "code": text.count("```") // 2,
        "text": text,
    }

fail = False

readmes = ["README.md", "README.zh-CN.md", "README.zh-TW.md"]
docs = ["docs/technical.md", "docs/technical.zh-CN.md", "docs/technical.zh-TW.md"]
deploy = ["docs/deployment.md", "docs/deployment.zh-CN.md", "docs/deployment.zh-TW.md"]

base = stats(readmes[0])
print("README 组")
for f in readmes:
    s = stats(f)
    links = sum(1 for g in readmes if g != f and g in s["text"]) \
            + sum(1 for g in docs if g in s["text"]) \
            + sum(1 for g in deploy if g in s["text"])
    ok = (s["sections"] == base["sections"] and s["images"] == base["images"]
          and s["code"] == base["code"] and links == 8)
    print(("  OK   " if ok else "  FAIL ") + f +
          f"  sections={s['sections']} images={s['images']} code={s['code']} links={links}")
    fail = fail or not ok

dbase = stats(docs[0])
print("technical 组")
for f in docs:
    s = stats(f)
    ok = s["sections"] == dbase["sections"] and s["code"] == dbase["code"]
    print(("  OK   " if ok else "  FAIL ") + f +
          f"  sections={s['sections']} code={s['code']}")
    fail = fail or not ok

dbase2 = stats(deploy[0])
print("deployment 组")
for f in deploy:
    s = stats(f)
    ok = s["sections"] == dbase2["sections"] and s["code"] == dbase2["code"]
    print(("  OK   " if ok else "  FAIL ") + f +
          f"  sections={s['sections']} code={s['code']}")
    fail = fail or not ok

print()
if fail:
    print("结构不一致：先补齐再提交。")
    sys.exit(1)
print(f"一致：README {base['sections']} 节 / {base['images']} 图 / {base['code']} 代码块；"
      f"technical {dbase['sections']} 节 / {dbase['code']} 代码块；"
      f"deployment {dbase2['sections']} 节 / {dbase2['code']} 代码块。")
PY
