# 文档

English · 简体中文 · [繁體中文](README.zh-TW.md)

关于这个版本的所有文字都在这个文件夹里。仓库根目录的 README 讲的是想法；
这里的页面讲的是怎么做、以及为什么这么做。

## 文档一览

| 文档 | 其他语言 | 内容 |
|---|---|---|
| [highlights.md](highlights.md) | [en](highlights.md) · [zh-TW](highlights.zh-TW.md) | 九十秒的导览：问题、单位，以及这个产品围绕的三个瞬间 |
| [loop.md](loop.md) | [en](loop.md) · [zh-TW](loop.zh-TW.md) | 循环一步一步走一遍，五个状态以及什么把插座在它们之间挪动，还有它断掉的三种方式 |
| [trust.md](trust.md) | [en](trust.md) · [zh-TW](trust.zh-TW.md) | 用数字说清证据规则、两条频率限制、分数怎么动，以及已知的限制 |
| [features.md](features.md) | [en](features.md) · [zh-TW](features.zh-TW.md) | 每一个能力一行：它做什么、哪个角色、在哪里看到 |
| [architecture.md](architecture.md) | [en](architecture.md) · [zh-TW](architecture.zh-TW.md) | 三个进程、八张表、一份上报走的路，以及校园规模需要什么 |
| [technical.md](technical.md) | [en](technical.md) · [zh-TW](technical.zh-TW.md) | 这个版本是怎么搭起来的：分层、数据模型、四条规则、接口，以及这一版故意没有做的事 |
| [deployment.md](deployment.md) | [en](deployment.md) · [zh-TW](deployment.zh-TW.md) | 在另一台机器上跑起来：服务、端口、环境变量，以及验证它确实起来的几条检查 |
| [screens.md](screens.md) | [en](screens.md) · [zh-TW](screens.zh-TW.md) | 每个界面的截图合集，桌面和手机都在，每张配一句话说明看到的是什么，以及怎么把背后的数据恢复回去 |
| [diagrams/](diagrams/) | — | 渲染好的图：三种语言各一张 `loop-en.png`、`loop-zh-CN.png`、`loop-zh-TW.png`，另外还有宣传视频里用到的 `loop-demo-*.png` 分帧 |

## 三种语言如何保持一致

每份文档都有三个版本，一种语言一份；同一个页面的三个版本标题相同、顺序相同，
读者切换语言时不会丢失位置。改动一个页面时，请在同一次提交里把三份都改掉；
`scripts/check-readmes.sh` 负责发现没有改全的情况。

根目录的 [README](../README.md) 是门面，不在这个索引里。
