# Socket Finder 插座查詢

**找一個能充電的座位。** 一個網頁應用，在學生坐下之前就告訴他：這張桌子的電源插座到底能不能用。

[English](README.md) · [简体中文](README.zh-CN.md) · 繁體中文

![房間列表](docs/screens/01-rooms.png)

## 這是什麼

港大 CCST9003 小組項目（第 R21 組）。這個倉庫是**迭代 1**：一個插座，從查到報走完一圈。
打開房間 → 打開插座 → 報它壞了 → 看狀態翻轉。

整個設計的單位是**插座**，不是房間。訂位系統數的是房間和桌子，報修系統數的是故障，
兩者都不知道你這台筆記本到底能不能在這裡充電。

## 介面

| 房間頁 | 維修隊列 |
|---|---|
| ![房間](docs/screens/02-room.png) | ![隊列](docs/screens/03-queue.png) |

## 技術棧

技術棧：

- **後端**：Spring Boot 4.1、Java 21、Spring Data JPA、Flyway、PostgreSQL 17
- **前端**：Vue 3 + Vite + Element Plus，一個應用服務兩個角色
- **鑑權**：電郵 + 密碼（BCrypt），token 存在記憶體裡，每次寫入都檢查角色

## 怎麼跑

需要：Java 21、Maven、Node 18+、本機跑著的 PostgreSQL。

```bash
# 只做一次：建庫（本項目假定 PostgreSQL 在 5433 端口）
createdb -p 5433 -h 127.0.0.1 socketfinder

./scripts/start-all.sh      # 後端 8081，前端 5175
open http://localhost:5175
```

停止用 `./scripts/stop-all.sh`。

## 示範帳號（密碼都是 `demo1234`）

| 電郵 | 角色 | 用途 |
|---|---|---|
| student1@connect.hku.hk | 學生 | 第一個上報的人 |
| student2@connect.hku.hk | 學生 | 第二個上報的人，翻轉狀態必須兩個帳號 |
| estates@hku.hk | 維護人員 | 看維修隊列 |

## 介面

| 方法 | 路徑 | 誰能調 | 做什麼 |
|---|---|---|---|
| POST | `/api/auth/login` | 所有人 | 電郵 + 密碼，回傳 token |
| GET | `/api/auth/demo-accounts` | 所有人 | 三個示範帳號，登入頁用 |
| GET | `/api/buildings` | 所有人 | 樓宇與樓層 |
| GET | `/api/floors/{id}/rooms` | 所有人 | 某層的房間與插座數量 |
| GET | `/api/rooms/{id}` | 所有人 | 房間裡的座位和插座 |
| POST | `/api/sockets/{id}/report` | 學生 | 上報 `WORKING` 或 `BROKEN` |
| POST | `/api/sockets/{id}/repair` | 維護人員 | 標記已修，可寫備註 |
| GET | `/api/maintenance/queue` | 維護人員 | 報壞的插座，壞得最久的排前 |

## 這一版實現了的規則

- **兩個人才翻轉**：24 小時內兩個不同帳號報同一狀態。只報一次會存下來，但介面顯示「未確認」。
- **每帳號每插座每天一次**：再報回傳 HTTP 429。
- **舊的檢查會標舊**：超過 30 天，介面直接標「舊」，不假裝它是新的。
- **只有維護人員能結案**：標記已修後狀態變 `REPAIRED` 並打時間戳，學生看到的就是這個。
- **角色分離由 API 執行**，不是前端把按鈕藏起來。

## 接下來打算做

- 每層一張平面圖，房間從列表變成一張圖。
- 上報可以帶照片；常用的插座狀態變了能收到通知；地下室這種訊號差的地方能離線查看。
- 全校的房間與插座數據，按樓逐棟匯入。
- 學生電郵驗證與自助註冊。
- 網頁版用得夠多之後，再考慮手機端。

每一步的範圍，都在上一輪迭代評審時確定。

## 原型階段的已知限制

- token 存在記憶體裡，後端一重啟所有人都要重新登入。
- 密碼用 BCrypt，但登入介面沒有頻率限制。
- 種子數據是樣本，不是對某一層樓的真實清點。

## 目錄結構

```
backend/   Spring Boot 介面、Flyway 遷移、種子數據、單測
frontend/  Vue 3 應用（一份 build，兩個角色）
scripts/   啟停、測試、端到端
docs/      截圖
```

---

**三份 README 必須同步。** 本項目有英文、簡體中文、繁體中文三份 README，任何改動都要在同一次提交裡三份一起改。
`scripts/check-readmes.sh` 會檢查三份結構是否一致，每次推送前跑。
