---
title: NUC-PRE L1 staging 验收结论
date: 2026-08-30
gate: NUC-PRE
scope: L1 staging only
status: passed
prior_status: blocked
---

# NUC-PRE 验收结论

## 裁决

**NUC-PRE 当前不通过（BLOCKED）；暂不允许启动 L1.7 Docker staging 部署。**

唯一本轮阻塞项是固定入口的正向校验链不再自洽：已批准且正在运行的 SHA 为 `ff2746f00ed0cb0112e09c3caa09a8354777c745`，而 bare Git `refs/heads/main` 已移动到 `87e9ca72147af7288fff9ab41a976be689067595`；因此 `test-staging` 对批准 SHA 返回 rc 68。在重新确定发布基线前，不应移动 ref、不应批准新 manifest，也不应继续 L1.7。

## 已通过项

- L1 Compose 保留 volume 的 stop/start 通过，PostgreSQL 恢复 healthy。
- 一次性数据库标记在重启后可完整读回，验收后已清理。
- 端口、network、volume、运行 UID、capability、no-new-privileges、CPU/memory/PID 限制通过。
- 错误 SHA、L2、production/额外参数均被固定入口拒绝。
- N5 本地 dump SHA-256 为 `4087bb53709ffc9b6b04c2ed22de98dc63e575dd89a156f4548b78d7314d583b`，与 NAS dump 一致。
- N5 64 MiB NAS 制品 SHA-256 为 `3b6a07d0d404fab4e23b6d34bc6696a6a312dd92821332385e5af7c01c421351`；NAS manifest `completed=true`，`n5_01_result=passed`，`nas_restore_result=passed`，恢复逻辑指标与源库一致。
- `jason-vm`、OpenClaw、Syncthing、cloudflared、sing-box、SSH、Docker、libvirt 和既有交易相关失败单元无可归因回归。

## 实际变更与数据边界

- 本轮唯一持久系统操作是 L1 Compose 容器 stop/start；容器、network 和 volume 未重建或删除。
- 一次性数据库已删除，遗留数为 0。N5 本地和 NAS 正式证据按保留规则未删除。
- 热数据仍仅在 NUC 本地 Docker volume；NAS 仅保留研究备份演练制品，未挂载到容器。
- L2 和 production 均未部署，仍为 future/not-deployed。

## 管理、回滚与延期范围

- SSH 管理路径和 Tailscale 备用路径未修改。
- L1 回滚仍须通过固定入口；如停止 Compose，不得使用 `--volumes`。
- 本次授权未包含 Docker daemon restart 或宿主 reboot，两者均未执行；本结论不将其扩张为隐含授权。
- production、L2、自动交易、券商接口和宿主安全配置均不在本轮。

## 解锁条件

1. 人工裁决以已批准 SHA 还是当前 `main` 作为后续 release 基线。
2. 如选择新 `main`，按现有流程对完整 SHA、release、evidence 和 approved manifest 重新验证；不可直接复用旧 manifest。
3. 对裁决后的批准 SHA 重跑 `test-staging` 并取得 rc 0，再重新签发 NUC-PRE PASS。

本文不授权修改 Git ref、部署新 SHA、启动 L1.7 或任何 production 操作。

---

## D3-N6-01R 复验追加（2026-08-30 UTC）

保留上述 D3-N6-01 `BLOCKED` 作为历史裁决。D3-N6-01R 已修正“已批准 release 必须等于当前可变 `main`”的错误绑定，并关闭唯一失败项。

**当前有效结论：PASSED — L1 staging infrastructure ready for future L1.7 release。**

- `test-staging ff2746f00ed0cb0112e09c3caa09a8354777c745 L1` 实际 rc 0，approved manifest、evidence、Compose、image digest 和静态门禁全部通过。
- 输出包含 `current_main_sha=87e9ca72147af7288fff9ab41a976be689067595` 与 `main_advanced=true`；`main` 推进不再撤销已有批准。
- 当前 `main` 无 approved manifest，仍被拒绝；未批准、未部署 `87e9ca72147af7288fff9ab41a976be689067595`。
- 宿主不存在 `/srv/value-investing/current-staging` symlink；这是变更前已有状态。运行容器 Compose config label 无歧义指向 `ff2746f00ed0cb0112e09c3caa09a8354777c745`，本轮未创建或修改指针。
- L1 PostgreSQL 仍为 healthy；container/network/volume 的 ID、名称与数量未变；无宿主 PostgreSQL/Qdrant 端口。
- N5 本地备份、NAS dump、64 MiB 制品、manifest、完成标记和恢复结果仍有效。
- `jason-vm`、OpenClaw、Syncthing、cloudflared、sing-box、SSH、Docker、libvirt 无回归；Qdrant 保持停止；无 L2/production 对象。
- 当前仅为空数据库 L1 staging 环境。L1.7 业务 release 仍需独立完整 SHA、manifest、迁移计划和部署批准。
- 本次通过不授权 production。Docker daemon restart 和宿主 reboot 测试未执行，为明确延期项；L2 为 future/not-deployed。
