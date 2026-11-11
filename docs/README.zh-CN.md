# 文档

[English](README.md) · 简体中文 · [繁體中文](README.zh-TW.md)

关于这个版本的所有文字都在这个文件夹里。仓库根目录的 README 讲的是想法，
这里的页面讲的是怎么做、以及为什么这么做。

## 文档一览

| 文档 | 其他语言 | 内容 |
|---|---|---|
| [technical.md](technical.md) | [zh-CN](technical.zh-CN.md) · [zh-TW](technical.zh-TW.md) | 这个版本是怎么搭起来的：分层、数据模型、四条规则、接口，以及这一版故意没有做的事 |
| [deployment.md](deployment.md) | [zh-CN](deployment.zh-CN.md) · [zh-TW](deployment.zh-TW.md) | 在另一台机器上跑起来：服务、端口、环境变量，以及验证它确实起来的几条检查 |
| [screens.md](screens.md) | [zh-CN](screens.zh-CN.md) · [zh-TW](screens.zh-TW.md) | 每个界面的截图合集，桌面和手机都在，每张配一句话说明看到的是什么，以及怎么把背后的数据恢复回去 |
| [diagrams/](diagrams/) | — | 渲染好的图：三种语言各一张 `loop-en.png`、`loop-zh-CN.png`、`loop-zh-TW.png`，另外还有宣传视频里用到的 `loop-demo-*.png` 分帧 |

## 三种语言如何保持一致

每份文档都有三个版本，一种语言一份；同一个页面的三个版本标题相同、顺序相同，
读者切换语言时不会丢失位置。改动一个页面时，请在同一次提交里把三份都改掉；
`scripts/check-readmes.sh` 负责发现没有改全的情况。

根目录的 [README](../README.md) 是门面，不在这个索引里。
