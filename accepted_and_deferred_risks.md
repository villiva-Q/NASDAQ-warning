---
title: NUC Docker-first 已接受与延期风险
status: effective
date: 2026-08-29
---

# NUC Docker-first 已接受与延期风险

## 硬门槛

- 研究容器禁止 privileged、host network、host PID/IPC、Docker socket、交易目录/密钥、`/root/.openclaw` 和整个 NAS 挂载。
- PostgreSQL、Qdrant、内部 API 不向 LAN 或公网发布；若临时诊断，另卡批准 loopback-only。
- L1/L2 使用独立 Compose project、network、database、volume、directory、credentials；只用版本化 manifest 交接。
- staging/production 完全隔离；本任务不部署 production。
- 部署绑定完整 commit SHA 或 image digest；release 不原地修改；未知目标/哈希/层级必须拒绝。
- N3 前必须有第二管理路径、受保护配置基线、`br0/vnet1/jason-vm` 前后验证方案和已批准的 D3 卡。
- 数据库备份恢复与大型归档复制/哈希/恢复必须在 NUC-PRE 验收前实际通过。
- 任何可归因于变更的 `jason-vm`、交易、SSH、OpenClaw、Syncthing、cloudflared、sing-box 异常都是停止条件。

## 计划处理

- 约 24 小时轻量 CPU/load/I/O/温度基线；第一周低并发运行。七天历史不再作为硬门槛。
- 两个 failed transient systemd units：先由交易 owner 确认“预期业务终态但非零退出”语义，再决定只 reset-failed 还是修改告警映射。
- 四个失败 OpenClaw cron：模型 allowlist 拒绝；由各 owner 单独选择获准模型/修正 alias/停用，不能由研究项目批量修改。
- SSH `12345`：确认半小时重连任务和长期 session 的 owner，从发起端分配唯一端口；不得直接杀唯一管理链。
- Node `3789`：已确认是 `opennews-web.service`，属于现有服务；研究端口避让，不迁移。
- 停止 Qdrant：保留不启动；确认 `/root/qdrant_data` 是否有保留价值后标记 retired。删除容器和数据分别另批。
- 软件更新分用户态与高耦合批次；Docker/kernel/cloudflared/微码及重启必须独立窗口并验证 br0/VM。
- 建立专用研究目录、最小 deploy identity、private Git remote/full-SHA release 和固定入口。
- NAS 研究子目录、80% 容量告警、`.partial`/SHA-256/完成标记、备份恢复和保留策略。

## 用户接受

- OpenClaw 继续以 root 的 systemd user service 运行，本期不迁移。
- Syncthing 继续以 root 运行，本期不迁移；只控制研究发布制品的同步边界。
- 若研究服务不使用 cloudflared 发布，Cloudflare Access 完整策略核验不阻塞 MVP。
- 不等待七天负载历史；采用约 24 小时观察和第一周低并发。
- 2026-08-29 复核时 load average 为 `20.42 / 17.39 / 15.30`，但 12 个逻辑 CPU 实测空闲约 `72%–97%`，I/O wait 通常为 `0%–2%`、短时约 `13%`，内存仍约有 23 GB 可用，且无受保护服务回归。用户确认该现象按非阻断性运行特征处理，不得单独以 load average 偏高为由暂停开发、Git/release 准备或 L1 staging 推进。
- 已启动的 24 小时 timer 继续运行并在到期后汇总，但降级为并行诊断记录，不再是 N3 或 L1 开发的等待门槛。只有出现持续 CPU 饥饿、持续高 I/O wait、内存压力/OOM，或受保护服务可归因回归时，才恢复为停止条件。
- Docker-first 默认部署；不创建新的研究 VM。VM 只在 v0.2 §12 条件触发后另立 D3。
- MVP 不要求立即达到企业级不可变/异地备份，但代码必须有 NUC 外副本，且数据库/大型归档恢复必须通过。

上述接受不取消硬边界，也不授权研究容器访问 root 服务、凭据或交易数据。

## 延期增强

- zram/swap、smartmontools/SMART 持续监控、全盘加密、UPS、电源恢复策略。
- 企业级异地备份、不可变对象锁、完整灾难恢复站点。
- OpenClaw/Syncthing 专用用户迁移与更细粒度 MAC/SELinux 策略。
- 外部网络主动暴露面测试、Cloudflare Access（仅未来发布时升级为硬门槛）、独立研究域名与 WAF。
- 新研究 VM、整机快照与跨主机迁移能力，除非触发 VM 后备条件。
- 清理 Docker 可回收镜像/build cache 和停止 Qdrant；均非 staging 必需且需要单独批准。

## 不得误判为阻塞的项目

- 现有 OpenClaw/Syncthing root 运行。
- Cloudflare Access 未核验但研究服务不经 tunnel 发布。
- 缺少七天 sysstat 历史。
- 24 小时资源观测尚未到期，但已有样本未显示持续资源饥饿或服务回归。
- 停止 Qdrant 尚未删除。
- zram、SMART、磁盘加密、UPS 尚未实施。

若这些项目的实际状态发生变化并触及硬边界（例如研究服务改为 Cloudflare 发布），必须重新分级。

## 2026-08-29 N2-A 后续范围修正（保留原始 N1）

L2 Compose、L2 PostgreSQL、L2 Qdrant 已归入 future/not-deployed；当前 NUC-PRE 只服务 L1.7。旧停止 Qdrant 继续保持停止且不是既定依赖。该修正缩小范围，不取消 L1 的任何硬边界。
