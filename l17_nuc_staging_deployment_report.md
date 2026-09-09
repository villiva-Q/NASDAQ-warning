# D3-L1.7-NUC-STAGING-01 部署报告

- 状态：`NUC_L1_STAGING_ACCEPTED / READY_FOR_SEC_CONTROLLED_SAMPLE / NOT_H1_APPROVED`
- 执行日期：2026-09-03
- 范围：仅 L1 staging；未连接 production、真实 SEC、交易系统、L2 或 L3。

## 部署身份与备份

- 最终部署 FULL_SHA：`e69cb611da183c3685ebdc0f598666f67b804d2d`
- Git tree：`b8a077ea4544f57194f5a79b51ef65c7b6afaf2c`
- NUC 应用镜像 ID：`sha256:f8a7a4879001b05b27b75731f6976f9d3d65b46b30d6a4d44a9ce4037e5b2746`（linux/amd64）
- PostgreSQL 镜像 ID：`sha256:5660c2cbfea50c7a9127d17dc4e48543eedd3d7a41a595a2dfa572471e37e64c`（`postgres:16.4-alpine`）
- 迁移前备份 ID：`l17-predeploy-20260903T101416Z`；901 bytes；SHA-256 `9dc658109340c06da0e8e3d99c5f0e5dc9c3b5f45697fac533181b355d5f3bd1`；`pg_restore --list` 验证可读。
- 数据库从 `base` 成功迁移并保持在 `0008_l17_release_identity`。

## 服务与网络

- PostgreSQL、control-api、scheduler、worker 均为 healthy。
- control API：NUC 本机 `http://127.0.0.1:18080/health` 返回 HTTP 200；宿主映射仅为 `127.0.0.1:18080->8080/tcp`。
- control API 同时接入 internal `l1_staging` 与独立 `l1_api_ingress`；PostgreSQL、scheduler、worker 只接入 internal 网络。
- PostgreSQL 无宿主 published port；未启动 `sec-sample`。

## fixture 完整链与正式发布

- 原首次执行源码：`70cdcec720b922ab1d8d19777267191bfc399a38`；其 EXDEV 隐藏快照由修复镜像直接 reconciliation，没有重建任务。
- occurrence ID：`d1373b3a-9f31-4bc5-b6d2-0c5b9bf58bc5`
- run ID：`5bae41c0-fd2b-4179-9567-6cfc6a026daa`
- job ID：`f6ced921-998a-445e-848c-0234c07356cc`
- release execution ID：`ecab89bd-e401-544f-8b07-a2bd32844e82`
- 终态：run/job 均 succeeded；publication 为 published。
- 候选数量：1。
- 正式报告：`/var/lib/value-investing/l1/formal-reports/snapshots/5bae41c0-fd2b-4179-9567-6cfc6a026daa-6d6fa35988bbee1e725179733aa8521b86c760c55136528df274a820979bf9c2/`
- 正式发布指针：`active_weekly_formal.json`；数据库指针为 `5bae41c0-fd2b-4179-9567-6cfc6a026daa:6d6fa35988bbee1e725179733aa8521b86c760c55136528df274a820979bf9c2`。
- 数据库 run/job/release identity 与正式报告一致。当前部署 release execution 为 `b6a22046-a83f-5f7f-8624-58acef3ad0f2`，绑定最终修复 FULL_SHA 与镜像。

## 幂等、失败与重启

- 同一 occurrence 重放前后 occurrence/run/job/pointer 计数保持 `1/1/1/1`，ID 与正式指针完全不变。
- 可恢复失败用例：run `6c67ec34-0fc8-4b00-9e63-b970fdd6152f` 为 failed、publication 为 not_published；job `df99defa-a3e9-4bc3-b000-74c64fbb73a6` 为 dead_letter；正式指针未移动。fixture 随后恢复为 golden 输入。
- restart/租约恢复：预置 1 秒租约的 run `5bea363a-40af-4e0b-b75f-ca81fe032818`、job `289e87fe-bd63-40b3-9a46-48627e9a0d6f` 在 control-api/scheduler/worker stop/start 后恢复为 succeeded；`restart_recovery` fact 数量为 1；正式指针保持不变，API 恢复 HTTP 200。

## 隔离恢复

- 部署前备份恢复至独立 internal 网络、一次性容器和一次性卷，确认 revision=`base`、public 表数量为 0，与迁移前空库状态一致。
- 同一隔离对象重建数据库后，以流式当前 dump 验证 0008 数据。主库与恢复库快照均为 `0008_l17_release_identity:3 runs:3 jobs:2 release executions:1 pointer`。
- 代表性原 run、job、release execution 与 published pointer 均存在且各为 1 条。
- 验证后仅清理本轮一次性恢复容器、网络、卷和临时 secret；主卷、WAL、正式报告与历史备份未删除。

## 资源、既有服务与限制

- 短时资源：PostgreSQL约 32 MiB/1 GiB，control-api约 40 MiB/512 MiB，scheduler约 45 MiB/512 MiB，worker约 41 MiB/4 GiB；无 OOM 或持续满载。
- jason-vm、OpenClaw Gateway、Syncthing、cloudflared、sing-box 正常；Qdrant 保持停止。
- 已知限制：本轮只使用 `source_class=fixture`；未运行真实 SEC、未启动 `sec-sample`、未进入 H1，未启动第二层或第三层。
