# Sure Socket

**一個學生報告插座壞了，第二個學生確認，職員修好，下一位讀者看到日期。**

<a href="scripts/check-readmes.sh"><img src="https://img.shields.io/badge/structure_check-scripts%2Fcheck--readmes.sh-2f855a?style=flat-square" alt="structure check"></a> <a href="docs/technical.md"><img src="https://img.shields.io/badge/Java-21-informational?style=flat-square" alt="java 21"></a> <img src="https://img.shields.io/badge/licence-coursework-lightgrey?style=flat-square" alt="licence">

[English](README.md) · [简体中文](README.zh-CN.md)

[文件](docs/README.md) · [技術](docs/technical.md) · [部署](docs/deployment.md) · [截圖](docs/screens.md)

![找插座：樓、房間，以及還能用的插座](docs/screens/desktop/01-find-a-socket.jpg)

## 這是什麼

Sure Socket 只在一個問題真正要緊的那一刻回答它：我可不可以在這張桌子為筆記型電腦充電？先選一棟樓，再選一個房間；插座按最後一次已知的狀態上色。

單位是插座，不是房間：一間大致正常的房間，若唯一空著的桌子是壞的，也毫無用處。每個插座都有自己的編號（`CPD-LG01-0001`：樓、房間、序號，永不重用）和自己的歷史。

→ [90 秒導覽](docs/highlights.md)

## 循環

沒有感測，也沒有人手工維護：每一步都給了下一個人動手的理由。

1. 學生打開一個房間，看到每個插座上次的核查。
2. 壞的那個一下就能報告：不需照片、不需留言、不需帳號。
3. 第二個學生表示同意，到那時狀態才改變。
4. 職員按最舊優先取隊列，並逐一標記每個插座已修。
5. 下一個學生看到維修結果和日期，然後再核查一次。

![循環：核查、報告、確認、維修、再核查](docs/diagrams/loop-en.png)

→ [循環如何一步步運作](docs/loop.md)

## 介面

一次建置，兩個角色：學生看到「找插座」和「報告故障」，物業處看到維修隊列。角色不對不會只是把按鈕藏起來；是 API 直接拒絕。

| 一個房間，筆記型電腦 | 報告，手機 |
|---|---|
| ![房間的桌子，每個插座按它的狀態上色](docs/screens/desktop/02-room-and-plan.jpg) | ![手機上的報告表格，每行一個欄位](docs/screens/mobile/06-phone-report.jpg) |

→ [所有介面，桌面與手機](docs/screens.md)

## 為什麼狀態可以信

規則不多，全部在伺服器端執行；只有職員可以關閉一項維修。

- 一個狀態需要在 72 小時內、由最重的三個帳號累積 1.6，並領先 1.5×。
- 帳號權重由 0.5 到 1.5，所以兩個新帳號可以翻轉一個插座，一個就不行。
- 每個插座每天一條報告、每個帳號每天十條，兩者都回傳 HTTP 429。

已知限制：超過 30 天的核查會變舊，權杖存在記憶體裡，登入沒有速率限制。

→ [規則、數字與已知限制](docs/trust.md)

## 執行它

Postgres 17、API 和 Vue 建置一起啟動，結構已遷移，帳號已預置。

```bash
docker compose up --build    # Postgres 17、API、Vue 建置、已預置的帳號
open http://localhost:8080   # 房間選擇頁
docker compose down -v
docker compose logs -f backend
```

`student1@connect.hku.hk` 和 `student2@connect.hku.hk` 的密碼是 `demo1234`（這一對可越過 1.6），`estates@hku.hk` 也一樣。

→ [部署、環境變數與重設](docs/deployment.md)

## 各部分如何湊在一起

- **後端** —— Java 21 上的 Spring Boot、PostgreSQL 17、Flyway；規則是純函數，不用資料庫也能測試。
- **前端** —— Vue 3 與 Vite，一次建置服務兩個角色；房間平面圖是一個 SVG 元件。
- **服務** —— nginx 提供建置檔並代理 `/api`：單一來源，所以 CORS 永不適用。

→ [架構與資料路徑](docs/architecture.md)

## 文件

| 頁面 | 回答甚麼 | 長度 |
|---|---|---|
| [90 秒導覽](docs/highlights.md) | 這是甚麼、寫給誰、看起來怎樣 | 2 分鐘 |
| [循環](docs/loop.md) | 每一步由誰動手，以及甚麼讓插座在狀態之間移動 | 4 分鐘 |
| [為什麼狀態可以信](docs/trust.md) | 以數字說明證據規則、速率限制、已知限制 | 5 分鐘 |
| [功能](docs/features.md) | 每個角色的每項能力，以及在哪裡看到 | 3 分鐘 |
| [架構](docs/architecture.md) | 三個程序、規則，以及一條報告走過的路徑 | 5 分鐘 |
| [截圖](docs/screens.md) | 全部 6 個畫面，桌面與手機 | 1 分鐘 |
| [技術參考](docs/technical.md) | 資料結構、端點、以程式碼表述的規則、下一步 | 12 分鐘 |
| [部署](docs/deployment.md) | Docker、環境變數、備份、重設、故障 | 6 分鐘 |

中文版本：[技術](docs/technical.zh-CN.md) · [技術，繁](docs/technical.zh-TW.md) · [部署](docs/deployment.zh-CN.md) · [部署，繁](docs/deployment.zh-TW.md)。

---

HKU CCST9003 課程作業，第 R21 組；不授權重用。
