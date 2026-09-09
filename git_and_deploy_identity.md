---
title: Git 与固定部署身份方案
status: draft
risk_grade: D3
date: 2026-08-29
---

# Git 与固定部署身份方案

本轮未创建 remote、repository、user、key 或 deploy entrypoint。

## 方案 A：私有 Git 远端

流程：Mac 向私有 GitHub/GitLab 推送；NUC 专用 deploy identity 使用只读 deploy key 拉取；NUC 按指定完整 commit SHA 构建 linux/amd64 镜像，或按固定 digest 拉取制品。

优点：代码天然有 NUC 外副本；审计、分支保护、review 和 key 吊销成熟；Mac 与 NUC 不需要直接保持在线。缺点：依赖第三方服务和外网；要管理组织/仓库权限；私有源代码和元数据离开本地网络。

适用：接受私有云远端、希望最低自建维护成本，并且可建立最小只读 deploy key。

## 方案 B：NUC bare Git

流程：NUC 上独立 Git 用户托管 bare repo；Mac 通过受限 SSH push；部署身份从 bare repo 只读 materialize 指定 commit 到 release 目录。

优点：代码和元数据留在本地；无第三方 Git 服务依赖；网络路径可控。缺点：NUC 同时成为运行端和 Git 主存储，必须另做 NUC 外备份；新增 SSH principal/authorized-key command 与仓库运维；误配置可能扩大宿主 SSH 面。

适用：明确要求本地优先、愿意维护独立 Git 身份与备份，并能避免复用 root SSH。

## 推荐

推荐方案 A：私有 Git 远端 + NUC 单仓库只读 deploy key。理由是代码必须存在 NUC 之外的副本，且不应为了 MVP 在宿主新增一个 SSH 写入面。deploy key 只授予目标仓库 read，不能复用个人 key，不能进入 Syncthing、镜像、日志或 OpenClaw prompt。

若用户不接受第三方托管，则选择方案 B；此时 bare repo、工作树和备份均不得位于 Obsidian/Syncthing，同步库不能作为 Git transport。

## 缺失决策

1. 远端类型：私有 GitHub/GitLab，或 NUC bare Git。
2. 仓库拆分：单仓库含 L1/L2，还是分别仓库；推荐初期单仓库、独立 Compose/project/release manifest。
3. 构建：NUC 本机构建，或可信 CI 构建并按 digest 拉取；MVP 推荐 NUC 本地按 full SHA 构建以减少 registry 前置。
4. deploy identity 名称、UID/GID、shell/no-shell、凭据保管和轮换周期。
5. release 保留数量、磁盘配额、数据库 migration 的向后兼容窗口。
6. 谁可批准 L1/L2 release、谁可执行 rollback、紧急回滚是否双人确认。

## 固定部署模型

```text
Mac: git push <private-remote> <reviewed-commit>
  → 人工选择 40-hex full commit SHA
  → NUC deploy fetch（只读）
  → 验证 commit object、签名/审批、manifest、测试报告哈希
  → 创建 /srv/value-investing/releases/<full_sha>/（不可原地修改）
  → 生成/验证固定镜像 tag 或 digest
  → test-staging <full_sha> <L1|L2>
  → deploy-staging <full_sha> <L1|L2>
  → 原子切换 current-staging release pointer
  → 健康和受保护服务验证
```

允许的固定入口仅为：

```text
deploy-staging FULL_COMMIT_SHA LAYER
test-staging FULL_COMMIT_SHA LAYER
rollback-staging FULL_COMMIT_SHA LAYER
deployment-status FULL_COMMIT_SHA LAYER
archive-research-data ARCHIVE_MANIFEST_ID
```

入口必须：

- FULL_COMMIT_SHA 精确匹配 40 个十六进制字符，并由 `git cat-file -e <sha>^{commit}` 验证存在；禁止 branch、tag、短 SHA 或自由文本替代。
- LAYER 只允许枚举 `L1`/`L2`；环境只允许 staging；production 必须拒绝。
- 验证 release manifest、镜像 digest、Compose project、测试报告哈希和目标目录均与 SHA 绑定。
- 同一 Compose project 同时只有一个部署租约；超时后需人工确认，不自动抢锁。
- 不把用户输入拼接到 shell；使用固定 argv 和 allowlist；日志不含 secrets。
- 不给 OpenClaw 任意 shell、Docker socket 或 Git 写权限。现有 OpenClaw root 是接受风险，但不是扩大授权。

## 回滚 release

每次成功部署记录 `previous_full_sha`、Compose config digest、image digest、数据库 schema version、备份 ID 与验证结果。回滚只允许切换到清单内的完整 SHA：

1. 验证目标 release 完整、镜像存在、schema 兼容。
2. 若需数据恢复，先停止写入并按单独批准的数据库恢复卡执行。
3. 原子切换 `current-staging` 到上一 release。
4. 启动精确 Compose project，完成 healthcheck 与受保护服务检查。
5. 回滚失败立即停止；不得退回 branch head 或现场修改 release。

## D3 批准拆分

- D3-GIT-01：选择远端与仓库布局。
- D3-GIT-02：创建部署身份和只读 key/受限 SSH command。
- D3-GIT-03：创建 release 目录、manifest schema 与固定入口。
- D3-GIT-04：首次 full-SHA fetch/build/test。
- D3-GIT-05：首次受控部署与回滚演练。

每张卡独立批准；批准远端不等于授权创建用户、key、部署或 production。

## 2026-08-29 N2-A 后续范围修正（保留原始 N1）

当前固定部署身份和 Git 决策只服务 L1.7 staging。文中的 L2 release/入口是 future 设计占位，不在本轮或当前 NUC-PRE 创建。L2 须等待 H1 通过和技术选型后另批。
