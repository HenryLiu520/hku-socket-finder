#!/usr/bin/env bash
# 三份 README 的结构必须一致：段落数、图片数、互链。任何一项不对就退出码 1。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 - <<'PY'
import re, sys

files = ["README.md", "README.zh-CN.md", "README.zh-TW.md"]
data = {}
fail = False

for f in files:
    text = open(f, encoding="utf-8").read()
    data[f] = {
        "sections": len(re.findall(r"^## ", text, re.M)),
        "images": len(re.findall(r"!\[", text)),
        "code_blocks": text.count("```") // 2,
        "links_to_others": sum(1 for g in files if g != f and g in text),
    }

base = data["README.md"]
for f in files:
    d = data[f]
    ok = (d["sections"] == base["sections"]
          and d["images"] == base["images"]
          and d["code_blocks"] == base["code_blocks"]
          and d["links_to_others"] == 2)
    print(("OK   " if ok else "FAIL ") + f
          + f"  sections={d['sections']} images={d['images']} code={d['code_blocks']} links={d['links_to_others']}")
    fail = fail or not ok

print()
if fail:
    print("三份 README 结构不一致：先补齐再提交。")
    sys.exit(1)
print(f"三份结构一致（{base['sections']} 节 / {base['images']} 张图 / {base['code_blocks']} 段代码）。")
PY
