# Socket Finder 插座查询

**找一个能充电的座位。** 一个网页应用，在学生坐下之前就告诉他：这张桌子的电源插座到底能不能用。

[English](README.md) · 简体中文 · [繁體中文](README.zh-TW.md)

![房间列表](docs/screens/01-rooms.png)

## 这是什么

港大 CCST9003 小组项目（第 R21 组）。这个仓库是**迭代 1**：一个插座，从查到报走完一圈。
打开房间 → 打开插座 → 报它坏了 → 看状态翻转。

整个设计的单位是**插座**，不是房间。订位系统数的是房间和桌子，报修系统数的是故障，
两者都不知道你这台笔记本到底能不能在这里充电。

## 界面

| 房间页 | 维修队列 |
|---|---|
| ![房间](docs/screens/02-room.png) | ![队列](docs/screens/03-queue.png) |

## 技术栈

技术栈：

- **后端**：Spring Boot 4.1、Java 21、Spring Data JPA、Flyway、PostgreSQL 17
- **前端**：Vue 3 + Vite + Element Plus，一个应用服务两个角色
- **鉴权**：邮箱 + 密码（BCrypt），token 存在内存里，每次写入都校验角色

## 怎么跑

需要：Java 21、Maven、Node 18+、本机跑着的 PostgreSQL。

```bash
# 只做一次：建库（本项目假定 PostgreSQL 在 5433 端口）
createdb -p 5433 -h 127.0.0.1 socketfinder

./scripts/start-all.sh      # 后端 8081，前端 5175
open http://localhost:5175
```

停止用 `./scripts/stop-all.sh`。

## 演示账号（密码都是 `demo1234`）

| 邮箱 | 角色 | 用途 |
|---|---|---|
| student1@connect.hku.hk | 学生 | 第一个上报的人 |
| student2@connect.hku.hk | 学生 | 第二个上报的人，翻转状态必须两个账号 |
| estates@hku.hk | 维护人员 | 看维修队列 |

## 接口

| 方法 | 路径 | 谁能调 | 做什么 |
|---|---|---|---|
| POST | `/api/auth/login` | 所有人 | 邮箱 + 密码，返回 token |
| GET | `/api/auth/demo-accounts` | 所有人 | 三个演示账号，登录页用 |
| GET | `/api/buildings` | 所有人 | 楼宇与楼层 |
| GET | `/api/floors/{id}/rooms` | 所有人 | 某层的房间与插座数量 |
| GET | `/api/rooms/{id}` | 所有人 | 房间里的座位和插座 |
| POST | `/api/sockets/{id}/report` | 学生 | 上报 `WORKING` 或 `BROKEN` |
| POST | `/api/sockets/{id}/repair` | 维护人员 | 标记已修，可写备注 |
| GET | `/api/maintenance/queue` | 维护人员 | 报坏的插座，按坏得最久排前 |

## 这一版实现了的规则

- **两个人才翻转**：24 小时内两个不同账号报同一状态。只报一次会存下来，但界面显示「未确认」。
- **每账号每插座每天一次**：再报返回 HTTP 429。
- **旧的核查会标旧**：超过 30 天，界面直接标「旧」，不假装它是新的。
- **只有维护人员能结案**：标记已修后状态变 `REPAIRED` 并打时间戳，学生看到的就是这个。
- **角色分离由 API 执行**，不是前端把按钮藏起来。

## 接下来打算做

- 每层一张平面图，房间从列表变成一张图。
- 上报可以带照片；常用的插座状态变了能收到通知；地下室这种信号差的地方能离线查看。
- 全校的房间与插座数据，按楼逐栋导入。
- 学生邮箱验证与自助注册。
- 网页版用得够多之后，再考虑手机端。

每一步的范围，都在上一轮迭代评审时确定。

## 原型阶段的已知限制

- token 存在内存里，后端一重启所有人都要重新登录。
- 密码用 BCrypt，但登录接口没有频率限制。
- 种子数据是样例，不是对某一层楼的真实清点。

## 目录结构

```
backend/   Spring Boot 接口、Flyway 迁移、种子数据、单测
frontend/  Vue 3 应用（一份 build，两个角色）
scripts/   启停、测试、端到端
docs/      截图
```

---

**三份 README 必须同步。** 本项目有英文、简体中文、繁体中文三份 README，任何改动都要在同一次提交里三份一起改。
`scripts/check-readmes.sh` 会检查三份结构是否一致，每次推送前跑。
