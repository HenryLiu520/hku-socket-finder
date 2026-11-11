# 文件

[English](README.md) · [简体中文](README.zh-CN.md) · 繁體中文

關於這個版本的所有文字都在這個資料夾裡。倉庫根目錄的 README 講的是想法，
這裡的頁面講的是怎麼做、以及為什麼這麼做。

## 文件一覽

| 文件 | 其他語言 | 內容 |
|---|---|---|
| [highlights.md](highlights.md) | — · — | 九十秒的導覽：問題、單位，以及產品圍著它轉的三個時刻 |
| [loop.md](loop.md) | — · — | 一步一步走這個循環、五種狀態和什麼讓插座在它們之間移動，以及它壞掉的三種方式 |
| [trust.md](trust.md) | — · — | 用數字說的證據規則、兩道速率限制、分數怎麼移動，以及已知限制 |
| [features.md](features.md) | — · — | 每一項能力一列：它做什麼、哪個角色、在哪裡看得到 |
| [architecture.md](architecture.md) | — · — | 三個行程、八張表、一筆上報走的路，以及校園規模會需要什麼 |
| [technical.md](technical.md) | [en](technical.md) · [zh-CN](technical.zh-CN.md) | 這個版本是怎麼組起來的：分層、資料模型、四條規則、介面，以及這一版刻意沒有做的事 |
| [deployment.md](deployment.md) | [en](deployment.md) · [zh-CN](deployment.zh-CN.md) | 在另一台機器上跑起來：服務、連接埠、環境變數，以及驗證它確實起來的幾項檢查 |
| [screens.md](screens.md) | [en](screens.md) · [zh-CN](screens.zh-CN.md) | 每個介面的截圖合集，桌面和手機都在，每張配一句話說明看到的是什麼，以及怎麼把背後的資料還原回去 |
| [diagrams/](diagrams/) | — | 渲染好的圖：三種語言各一張 `loop-en.png`、`loop-zh-CN.png`、`loop-zh-TW.png`，另外還有宣傳影片裡用到的 `loop-demo-*.png` 分幀 |

## 三種語言如何保持一致

每份文件都有三個版本，一種語言一份；同一個頁面的三個版本標題相同、順序相同，
讀者切換語言時不會丟失位置。改動一個頁面時，請在同一次提交裡把三份都改掉；
`scripts/check-readmes.sh` 負責發現沒有改全的情況。

根目錄的 [README](../README.md) 是門面，不在這個索引裡。
