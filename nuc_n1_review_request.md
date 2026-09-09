---
title: NUC N1 人工评审请求
status: draft-awaiting-user-approval
risk_grade: D3
date: 2026-08-29
next_gate: N2
---

# NUC N1 人工评审请求

本文件请求逐项审批，不表示任何变更已执行或已通过。N1 只完成计划与只读证据。

## 只读证据摘要

- `3789` 已归属 `opennews-web.service`，root/always restart，现状保护、目标端口避让。
- 两个 failed units 是交易自动化 transient one-shot，非研究服务；非零退出分别对应已最终化不重试、跳过未确认告警。
- 四个失败 OpenClaw cron 均因模型不在当前 allowlist，被 preflight 拒绝，业务任务未启动。
- `12345` 由长期 root SSH local-forward session 占用；另一个半小时任务持续争用，发起端 owner 尚待确认。
- 停止 Qdrant：restart=no、default bridge、本地 bind mount、无 Compose/依赖 labels；不启动、不删除、不复用。
- iptables 使用 nft backend；UFW/Docker/Tailscale 共用 nftables。`br_netfilter` 未加载，`br0` bridge netfilter flags 为 0；`jason-vm` 的 `vnet1` 直接加入 `br0`。

## 进入 N2 的逐项审批

请按卡号分别批准、拒绝或要求修改：

1. **D3-N2-01（必需）**：受保护配置快照与第二管理路径验证。需决定快照路径、秘密处理、保留期和窗口。
2. **D3-N2-02A（可延期，不阻塞空环境）**：两个 transient failed unit 的 owner 确认与告警语义；禁止改变交易结果。
3. **D3-N2-02B（可延期，不阻塞空环境）**：四个 OpenClaw cron 分别修正 allowlist/model 或停用。
4. **D3-N2-02C（计划处理；若影响唯一管理链则先阻塞）**：确认 SSH `12345` 发起端，分配唯一端口并优雅轮换旧 session。
5. **D3-N2-03（N3 前必需启动）**：约 24 小时轻量基线；批准采样脚本、60 秒或更长间隔、本地路径和保留期。无需等七天。
6. **D3-N2-04（可延期但记录风险）**：批准的用户态安全更新包清单与窗口。
7. **D3-N2-05（可延期至 N3 前后独立窗口）**：kernel/microcode/Docker/cloudflared 更新与宿主重启；需要本地控制台和 `jason-vm` 回归测试。
8. **D3-N2-06（N3 前必需）**：研究目录与 deploy identity；需决定用户名/UID/GID、权限和固定入口的宿主执行机制。
9. **D3-GIT-01（N3 前必需）**：选择私有 Git 远端（推荐）或 NUC bare Git。
10. **D3-GIT-02/03（N3 前必需）**：只读 deploy key/身份、release 目录、manifest 和固定入口；仍不得部署 production。
11. **D3-N3-01（执行 N3 时必需）**：分别创建 L1/L2 staging 空骨架、network 和 volume；两个 project 单独批准。
12. **D3-N3-02（空环境验收后）**：首次 L1 staging release，完整 SHA、并发 1。
13. **D3-N3-03（空环境验收后）**：首次 L2 staging release，初始并发 1，升至 2 需新证据/批准。
14. **D3-N5-01（NUC-PRE 前必需）**：数据库逻辑备份恢复演练。
15. **D3-N5-02（NUC-PRE 前必需）**：NAS 研究子目录、冷归档哈希与恢复演练；本轮未向 NAS 写测试文件。
16. **D3-N6-01（NUC-PRE 前必需）**：staging 空环境验收。Docker restart 和宿主 reboot 必须另行明确勾选，不能隐含授权。

## 执行 N3 Docker staging 前真正必需

- D3-N2-01：受保护基线和第二管理路径。
- D3-N2-03：24 小时观测已启动，且初始证据没有显示应立即停止；创建空环境不必等满七天。
- D3-N2-06：研究目录/身份边界获批。
- D3-GIT-01/02/03：Git 方案、full-SHA release 与固定部署入口获批；若 N3 只创建完全空的 Compose 骨架，remote/key 的实际创建可与首次 release 前衔接，但设计必须先批准。
- `docker_host_staging_spec.json` 和两套 Compose 静态 config 经审查，确认无 host/privileged/socket/交易目录/LAN 端口。
- `br0/vnet1/jason-vm`、nftables、Docker network 和监听端口的前后验证步骤就绪。
- 每个 N3 project/network/volume 的精确名称和回滚命令获批。

## 可延期

- 修复交易 transient unit 的显示状态，只要 owner 确认不消耗资源且不影响研究部署。
- 四个 OpenClaw cron 的模型 allowlist 修复，只要它们不是 N3 部署入口。
- 停止 Qdrant 的 retired/delete；研究项目不得复用它。
- 用户态及高耦合升级；延期必须记录 156 个待升级包的版本风险。若 Docker 现版本满足 Compose spec，可先建空环境，升级另窗处理。
- Cloudflare Access（研究服务不通过 tunnel 发布时）。
- OpenClaw/Syncthing root 迁移、zram、SMART、磁盘加密、UPS、企业级异地/不可变备份、新研究 VM。

## 请求用户补齐的决策

1. Git：批准“私有 Git 远端 + 单仓库只读 deploy key”推荐方案，还是选择 NUC bare Git？
2. 研究宿主身份：是否批准新增专用 system user/group，且不加入 docker group？
3. 固定入口：由 root-owned、参数 allowlist 的 wrapper 代理最小 Docker Compose 动作，还是采用另一种最小权限机制？
4. 24 小时观测：采样间隔、保留期和本地目录是否接受建议值？
5. N2 顺序：是否先批准 N2-01、N2-03、N2-06 和 Git 设计，其余故障/升级卡延期？
6. Docker/宿主重启：当前不授权；未来是否接受在 N6 另开维护窗测试？

## 停止声明

N1 到此停止。只有用户逐项批准相应 D3 卡后才能进入 N2；任何笼统的“批准 N1”不视为授权全部宿主修改、Docker 变更、网络变更、重启或部署。

## 2026-08-29 N2-A 审批结果与范围修正

后续审批仅授权 D3-N2-01、D3-N2-03 和 D3-N2-06A；不授权其他 N2 或 N3—N6。当前 NUC-PRE 只服务 L1.7，原文所有 L2 卡均转为 future/not-deployed，等待 H1 与 L2 技术选型后重新审批。本节为后续记录，不表示原始 N1 已执行。
