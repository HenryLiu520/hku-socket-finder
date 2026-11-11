# Sure Socket

**一名学生上报一个坏插座，第二名学生确认，维修人员修复，下一位读者看到日期。**

<a href="scripts/check-readmes.sh"><img src="https://img.shields.io/badge/structure_check-scripts%2Fcheck--readmes.sh-2f855a?style=flat-square" alt="structure check"></a> <a href="docs/technical.md"><img src="https://img.shields.io/badge/Java-21-informational?style=flat-square" alt="java 21"></a> <img src="https://img.shields.io/badge/licence-coursework-lightgrey?style=flat-square" alt="licence">

简体中文 · [English](README.md) · [繁體中文](README.zh-TW.md)

[文档](docs/README.md) · [技术说明](docs/technical.md) · [部署](docs/deployment.md) · [界面](docs/screens.md)

![找插座：楼栋、房间和可用的插座](docs/screens/desktop/01-find-a-socket.jpg)

## 这是什么

Sure Socket 在一个问题最要紧的那一刻回答它：我能在这张桌子上给笔记本充电吗？先选楼栋，再选房间；插座按它们最后一次已知的状态上色。

单位是插座，不是房间：一个大体上都好的房间，在你面前那张空桌子是坏的时候毫无用处。每个插座都有自己的编号（`CPD-LG01-0001`：楼栋、房间、序号，永不复用）和自己的历史。

→ [90 秒导览](docs/highlights.md)

## 循环

没有任何东西被传感器感知，也没有任何东西靠手工维护：每一步都为下一个人带来回报。

1. 一名学生打开房间，看到每个插座最后一次核查的结果。
2. 坏的那个点一下就上报：不用照片，不用留言，不用账号。
3. 第二名学生表示同意，这时状态才改变。
4. 维修人员按从旧到新的顺序接单，把每个插座标记为已修复。
5. 下一名学生看到这次修复和它的日期，再核查一次。

![循环：核查、上报、确认、修复、再核查](docs/diagrams/loop-en.png)

→ [循环如何一步步运转](docs/loop.md)

## 界面

一套构建，两个角色：学生看到*找插座*和*上报故障*，物业办公室看到维修队列。角色不对不会隐藏按钮；是 API 拒绝。

| 一个房间，笔记本 | 上报，手机 |
|---|---|
| ![房间里的桌子，每个插座按它的状态上色](docs/screens/desktop/02-room-and-plan.jpg) | ![手机上的上报表单，每行一个字段](docs/screens/mobile/06-phone-report.jpg) |

→ [所有界面，桌面与手机](docs/screens.md)

## 为什么状态值得信任

规则很少，由服务端强制执行；只有维修人员可以关闭一次修复。

- 一个状态需要在 72 小时内、来自三个最重账号的 1.6，并且领先 1.5×。
- 账号权重为 0.5 到 1.5，所以两个新账号可以翻转一个插座，一个不行。
- 每个插座每天一条上报，每个账号每天十条，两者都返回 HTTP 429。

已知限制：超过 30 天的核查会过期，令牌存在内存里，登录没有限流。

→ [规则、数字和已知限制](docs/trust.md)

## 运行

Postgres 17、API 和 Vue 构建一起启动，数据库结构已迁移，账号已写入种子数据。

```bash
docker compose up --build    # Postgres 17、API、Vue 构建、预置账号
open http://localhost:8080   # 房间选择页
docker compose down -v
docker compose logs -f backend
```

`student1@connect.hku.hk` 和 `student2@connect.hku.hk` 的密码是 `demo1234`（这一对可以凑够 1.6），`estates@hku.hk` 也是。

→ [部署、环境变量和重置](docs/deployment.md)

## 各部分如何拼在一起

- **后端** — Java 21 上的 Spring Boot，PostgreSQL 17，Flyway；规则是纯函数，不用数据库就能测试。
- **前端** — Vue 3 和 Vite，一套构建同时服务两个角色；房间平面图是一个 SVG 组件。
- **对外服务** — nginx 提供构建产物并代理 `/api`：同一个源，所以 CORS 从不生效。

→ [架构与数据路径](docs/architecture.md)

## 文档

| 页面 | 回答的问题 | 长度 |
|---|---|---|
| [90 秒导览](docs/highlights.md) | 这是什么、给谁用、长什么样 | 2 分钟 |
| [循环](docs/loop.md) | 每一步由谁行动，什么让插座在状态之间移动 | 4 分钟 |
| [为什么状态值得信任](docs/trust.md) | 用数字说明的证据规则、限流、已知限制 | 5 分钟 |
| [功能](docs/features.md) | 按角色列出的每一项能力，以及在哪里能看到 | 3 分钟 |
| [架构](docs/architecture.md) | 三个进程、规则，以及一条上报经过的路径 | 5 分钟 |
| [界面](docs/screens.md) | 全部 6 个界面，桌面与手机 | 1 分钟 |
| [技术参考](docs/technical.md) | 数据库结构、端点、以代码写成的规则、下一步 | 12 分钟 |
| [部署](docs/deployment.md) | Docker、环境变量、备份、重置、故障 | 6 分钟 |

中文版本：[技术说明](docs/technical.zh-CN.md) · [技术说明，繁](docs/technical.zh-TW.md) · [部署](docs/deployment.zh-CN.md) · [部署，繁](docs/deployment.zh-TW.md)。

---

HKU CCST9003 课程作业，第 R21 组；不授权重复使用。
