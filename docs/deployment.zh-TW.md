# 部署文件

把它放到別的機器上要怎麼做：會起哪些東西、要配什麼，以及出問題時先看哪裡。

## 部署的是什麼

| 服務 | 映像 | 埠號 | 依賴 |
|---|---|---|---|
| `db` | postgres:17-alpine | 容器內 5432 | 無 |
| `backend` | 由 `backend/` 建置 | 8081 | 等 `db` 健康 |
| `frontend` | 由 `frontend/` 建置（nginx + 打包好的前端） | 8080 → 80 | `backend` |

資料庫**不映射到主機**，外面只能存取 8080 和 8081。

## 需要什麼

- Docker Engine 24 以上 + Compose v2（`docker compose version` 能跑）
- 2 GB 可用磁碟（映像合計約 600 MB）、1 GB 記憶體
- 其他都不用裝。Java、Node、PostgreSQL 都在映像裡。

## 一條命令部署

```bash
git clone https://github.com/HenryLiu520/hku-socket-finder.git
cd hku-socket-finder
docker compose up --build -d
docker compose ps
```

第一次啟動會發生什麼：`db` 起來並通過 `pg_isready` 健康檢查；`backend` 等它就緒後跑 Flyway 遷移（9 張表）並預置三個示範帳號；`frontend` 起 nginx，把 `/api` 轉給後端。

## 確認部署成功

```bash
curl -s http://localhost:8081/api/buildings
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8080
```

然後打開 `http://localhost:8080`，用 `student1@connect.hku.hk` / `demo1234` 登入。要示範「兩報才翻」還需要 `student2`。

## 設定項

| 變數 | 預設值 | 作用 |
|---|---|---|
| `SF_DB_URL` | `jdbc:postgresql://localhost:5433/socketfinder` | JDBC 連線字串；compose 裡指向 `db` 服務 |
| `SF_DB_USER` | 目前系統使用者 | 資料庫使用者 |
| `SF_DB_PASSWORD` | 空 | 資料庫密碼 |
| `SF_BIND` | `127.0.0.1` | 介面監聽位址；容器裡必須是 `0.0.0.0` |
| `SF_PORT` | `8081` | 介面埠號 |
| `SF_CORS_ORIGIN` | `http://localhost:5175` | 唯一允許跨域呼叫介面的來源 |

走 nginx 前端時瀏覽器存取的是同源的 `/api`，CORS 不參與。只有從別的站點直接呼叫介面時才需要改。

不想改倉庫就加一個 `docker-compose.override.yml`：

```yaml
services:
  backend:
    environment:
      SF_CORS_ORIGIN: https://socketfinder.example.com
```

## 資料、備份與重置

資料庫在命名卷 `socketfinder-data` 裡。

```bash
# 備份
docker compose exec -T db pg_dump -U socketfinder socketfinder > backup.sql

# 還原到正在跑的棧
cat backup.sql | docker compose exec -T db psql -U socketfinder -d socketfinder

# 全部重來
docker compose down -v
```

**升級前先備份**。遷移只有前進，沒有回滾腳本。

## 日誌與健康

```bash
docker compose ps                    # 狀態與健康
docker compose logs -f backend       # Spring Boot 輸出、遷移、錯誤
```

沒有 Actuator 健康端點，健康 = `GET /api/buildings` 回 200。

## 起不來的時候

| 現象 | 原因 | 怎麼辦 |
|---|---|---|
| `port is already allocated` | 8080 或 8081 被佔用 | 改埠號映射左邊那個數字 |
| 後端退出、報連線失敗 | 資料庫沒變成健康 | `docker compose logs db`，看卷的權限 |
| nginx 回 502 | 後端沒起來 | `docker compose logs backend`，等首次建置完成 |
| `403 Invalid CORS request` | 從別的來源直接呼叫介面 | 設 `SF_CORS_ORIGIN`，或統一走 nginx |
| 重啟後所有人被登出 | token 存在記憶體裡 | 這一版的已知限制，重新登入即可 |
| 頁面能開、介面 404 | `/api` 代理路徑或後端掛了 | `docker compose ps`，再 `curl localhost:8081/api/buildings` |

## 不用 Docker

```bash
./scripts/start-all.sh      # 資料庫、介面 :8081、前端 :5175
```

`scripts/setup-db.sh` 的規則：設了 `SF_DB_URL` 用現成服務；有 Docker 用 Docker；都沒有的話在 `db/pgdata` 裡建自己的叢集。

純伺服器、沒有 Docker 的話：`mvn -DskipTests package` 打包，用 systemd 跑 `java -jar backend/target/socket-finder-0.1.0.jar`，`frontend/dist` 交給任意靜態伺服器，再把 nginx 的 `/api` 指到 jar 的埠號。

## 面向真實使用者之前

- 換掉預置的示範帳號，補上真正的註冊與身分驗證。
- 把 token 移出記憶體，否則每次部署都會把所有人登出。
- 前面掛 TLS（Caddy 或 nginx），不要把 8081 暴露到公網。
- 資料庫帳密放密鑰管理，不要寫在 compose 檔。
- 按上面的方式做備份計畫，並且**真的還原一次**。
- 先定房間和插座資料從哪來 —— 現在的種子資料只是一層樓的樣本。

## 部署檢查清單

- [ ] `docker compose ps` 三個服務都在跑，`db` 健康
- [ ] `GET /api/buildings` 回 200，有一筆樓宇
- [ ] 能登入，房間列表能出來
- [ ] 兩個帳號能把一個插座翻成壞，維修隊列裡能看到
- [ ] 做過一次備份，並還原進一個臨時庫驗證過
