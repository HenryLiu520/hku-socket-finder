# Documentation

English · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md)

Everything written about this build lives in this folder. The repository README sells the idea;
these pages are the how and the why.

## Documents

| Document | Other languages | What it covers |
|---|---|---|
| [technical.md](technical.md) | [zh-CN](technical.zh-CN.md) · [zh-TW](technical.zh-TW.md) | How the build is put together: layers, data model, the four rules, endpoints, and what this iteration deliberately leaves out |
| [deployment.md](deployment.md) | [zh-CN](deployment.zh-CN.md) · [zh-TW](deployment.zh-TW.md) | Running it somewhere other than the machine it was written on: services, ports, environment variables, and the checks that prove it came up |
| [screens.md](screens.md) | [zh-CN](screens.zh-CN.md) · [zh-TW](screens.zh-TW.md) | A gallery of every screen, desktop and phone, with one sentence on what you are looking at and how to restore the data behind it |
| [diagrams/](diagrams/) | — | Rendered diagrams: `loop-en.png`, `loop-zh-CN.png`, `loop-zh-TW.png` for the three languages, and the `loop-demo-*.png` frames used in the pitch video |

## Keeping the translations in step

Each document exists three times, once per language, and the three versions of a page carry the
same headings in the same order so a reader can switch language without losing their place. When a
page changes, change all three in the same commit; `scripts/check-readmes.sh` is what notices when
that has not happened.

The root [README](../README.md) is the front door and is not part of this index.
