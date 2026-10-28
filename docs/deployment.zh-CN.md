# 部署文档

把它放到别的机器上要怎么做：会起哪些东西、要配什么、以及出问题时先看哪里。

## 部署的是什么

| 服务 | 镜像 | 端口 | 依赖 |
|---|---|---|---|
| `db` | postgres:17-alpine | 容器内 5432 | 无 |
| `backend` | 由 `backend/` 构建 | 8081 | 等 `db` 健康 |
| `frontend` | 由 `frontend/` 构建（nginx + 打包好的前端） | 8080 → 80 | `backend` |

数据库**不映射到宿主机**，外面只能访问 8080 和 8081。

## 需要什么

- Docker Engine 24 以上 + Compose v2（`docker compose version` 能跑）
- 2 GB 空余磁盘（镜像加起来约 600 MB）、1 GB 内存
- 其它都不用装。Java、Node、PostgreSQL 都在镜像里。

## 一条命令部署

```bash
git clone https://github.com/HenryLiu520/hku-socket-finder.git
cd hku-socket-finder
docker compose up --build -d
docker compose ps
```

第一次启动会发生什么：`db` 起来并通过 `pg_isready` 健康检查；`backend` 等它就绪后跑 Flyway 迁移（9 张表）并预置三个演示账号；`frontend` 起 nginx，把 `/api` 转给后端。

## 确认部署成功

```bash
curl -s http://localhost:8081/api/buildings
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8080
```

然后打开 `http://localhost:8080`，用 `student1@connect.hku.hk` / `demo1234` 登录。要演示「两报才翻」还需要 `student2`。

## 配置项

| 变量 | 默认值 | 作用 |
|---|---|---|
| `SF_DB_URL` | `jdbc:postgresql://localhost:5433/socketfinder` | JDBC 连接串；compose 里指向 `db` 服务 |
| `SF_DB_USER` | 当前系统用户 | 数据库用户 |
| `SF_DB_PASSWORD` | 空 | 数据库密码 |
| `SF_BIND` | `127.0.0.1` | 接口监听地址；容器里必须是 `0.0.0.0` |
| `SF_PORT` | `8081` | 接口端口 |
| `SF_CORS_ORIGIN` | `http://localhost:5175` | 唯一允许跨域调接口的来源 |

走 nginx 前端时浏览器访问的是同源的 `/api`，CORS 根本不参与。只有你从别的站点直接调接口时才需要改。

不想改仓库就加一个 `docker-compose.override.yml`：

```yaml
services:
  backend:
    environment:
      SF_CORS_ORIGIN: https://socketfinder.example.com
```

## 数据、备份与重置

数据库在命名卷 `socketfinder-data` 里。

```bash
# 备份
docker compose exec -T db pg_dump -U socketfinder socketfinder > backup.sql

# 恢复到一个正在跑的栈
cat backup.sql | docker compose exec -T db psql -U socketfinder -d socketfinder

# 全部重来
docker compose down -v
```

**升级前先备份**。迁移只有前进，没有回滚脚本。

## 日志与健康

```bash
docker compose ps                    # 状态与健康
docker compose logs -f backend       # Spring Boot 输出、迁移、报错
```

没有 Actuator 健康端点，健康 = `GET /api/buildings` 返回 200。

## 起不来的时候

| 现象 | 原因 | 怎么办 |
|---|---|---|
| `port is already allocated` | 8080 或 8081 被占 | 改端口映射左边那个数 |
| 后端退出、报连接失败 | 数据库没变成健康 | `docker compose logs db`，看卷权限 |
| nginx 返回 502 | 后端没起来 | `docker compose logs backend`，等首次构建完成 |
| `403 Invalid CORS request` | 从别的源直接调接口 | 设 `SF_CORS_ORIGIN`，或统一走 nginx |
| 重启后所有人被登出 | token 存在内存里 | 这一版的已知限制，重新登录即可 |
| 页面能开、接口 404 | `/api` 代理路径或后端挂了 | `docker compose ps`，再 `curl localhost:8081/api/buildings` |

## 不用 Docker

```bash
./scripts/start-all.sh      # 数据库、接口 :8081、前端 :5175
```

`scripts/setup-db.sh` 的规则：设了 `SF_DB_URL` 用现成服务；有 Docker 用 Docker；都没有就在 `db/pgdata` 里建自己的集群。

纯服务器、没有 Docker 的话：`mvn -DskipTests package` 打包，用 systemd 跑 `java -jar backend/target/socket-finder-0.1.0.jar`，`frontend/dist` 交给任意静态服务器，再把 nginx 的 `/api` 指到 jar 的端口。

## 面向真实用户之前

- 换掉预置的演示账号，补上真正的注册与身份校验。
- 把 token 挪出内存，否则每次部署都会把所有人登出。
- 前面挂 TLS（Caddy 或 nginx），不要把 8081 暴露到公网。
- 数据库账号密码放密钥管理里，不要写在 compose 文件。
- 按上面的方式做备份计划，并且**真的恢复一次**。
- 先定房间和插座数据从哪来 —— 现在的种子数据只是一层楼的样例。

## 部署检查清单

- [ ] `docker compose ps` 三个服务都在跑，`db` 健康
- [ ] `GET /api/buildings` 返回 200，有一条楼宇
- [ ] 能登录，房间列表能出来
- [ ] 两个账号能把一个插座翻成坏，维修队列里能看到
- [ ] 做过一次备份，并恢复进一个临时库验证过
