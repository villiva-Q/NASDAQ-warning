# D3-N6-01R 已批准 release 门禁修正与 NUC-PRE 复验报告

- 执行日期：2026-08-30（UTC）
- 批准 SHA：`ff2746f00ed0cb0112e09c3caa09a8354777c745`
- 当前 main：`87e9ca72147af7288fff9ab41a976be689067595`
- 结果：**PASS**

## 1. 根因与修正语义

原固定入口在已批准 release 的日常 `test-staging/deploy-staging` 路径中强制 `target SHA == 当前 refs/heads/main`。`main` 推进后，这会错误撤销不可变 release 的既有批准，并阻断历史 rollback target。

修正后，日常路径验证完整 target SHA、commit object、root-owned/非 group-other 可写 manifest、`approved_commit_sha`、`main_sha_at_approval`、批准时间、evidence、Compose、image digest、L1/staging/project 边界与 Docker 授权字段。当前 `main` 仅作为 `current_main_sha/main_advanced` 状态输出。新 release 仍必须在批准动作时确认 candidate 等于当时 main；本次未创建新批准。

## 2. 变更前快照与回滚包

- root-only 目录：`/srv/value-investing/backups/config/n6-release-gate-20260830T001900Z`，目录 `0700 root:root`，文件均 `0600 root:root`。
- 4 个入口别名和共享脚本变更前 SHA-256：`ed38adfae27f77ab3ba177824892cf10c3a868eb477bc79190ac3ef14e6529c0`。
- manifest 变更前 SHA-256：`595516eb45a6a88e90ea4ab28070ae0474712763805968c5af91ca2e483cce5b`。
- 快照记录 current main、实际部署 SHA、Docker IDs/数量、端口与受保护服务状态，不包含数据库密码。

## 3. 变更后哈希与 manifest schema

- `test-staging`、`deploy-staging`、`rollback-staging`、`deployment-status` 和共享脚本变更后 SHA-256：`7a64639145bfa61f46c4a358691789940eb0934ba902d6ac4c7c4f4f91a84448`。
- approved manifest 变更后 SHA-256：`35e3deecdaf2cf551282a98d1728dc46d84b20d37ce2f9d70fee2dc00c7ddea1`。
- schema `1.1 -> 1.2`；新增 `approved_commit_sha`、`main_sha_at_approval`、`approved_at`、`evidence_hashes`、`compose_sha256`、`image_digest`。
- 上述值均与既有 `full_sha/main_ref_sha/created_utc`、evidence records、compose record 和 image record 一致；未改变证据内容、Compose hash、image digest、层级、环境或部署授权。

## 4. 15 项正向/负向测试与并发锁

1. 已批准 SHA `test-staging`：rc 0，PASS。
2. 当前未批准 main：rc 67，拒绝。
3. 未知 40 位 SHA：rc 66，拒绝。
4. 短 SHA：rc 64，拒绝。
5. branch：rc 64，拒绝。
6. tag：rc 64，拒绝。
7. L2：rc 64，拒绝。
8. production：rc 64，拒绝。
9. 额外参数：rc 64，拒绝。
10. manifest target SHA 不一致 fixture：`manifest_gate_failed`。
11. evidence 哈希错误 fixture：`evidence_hash_mismatch`。
12. Compose 哈希错误 fixture：`evidence_hash_mismatch`。
13. image digest 错误 fixture：`local_image_digest_mismatch`。
14. group 可写 manifest fixture：`manifest_ownership_or_mode_invalid`。
15. 历史已批准 SHA rollback target 验证：rc 0，`docker_change_performed=false`。

额外并发锁测试：rc 75，`L1 staging deployment lock is held`。所有破坏测试仅使用 root-only `/tmp` fixture，测试后删除；未修改真实 manifest 为错误值，未修改 immutable release。

## 5. N6 唯一失败项实际输出

命令：

```text
/usr/local/sbin/test-staging ff2746f00ed0cb0112e09c3caa09a8354777c745 L1
```

实际 rc：`0`

实际输出：

```json
{"current_main_sha":"87e9ca72147af7288fff9ab41a976be689067595","environment":"staging","full_sha":"ff2746f00ed0cb0112e09c3caa09a8354777c745","image_digest":"verified","layer":"L1","main_advanced":true,"static_gate":"passed","status":"validation-passed"}
```

## 6. 指针、Docker 和受保护服务前后对照

- current main 前后均为 `87e9ca72147af7288fff9ab41a976be689067595`；批准 SHA 前后均为 `ff2746f00ed0cb0112e09c3caa09a8354777c745`。
- `/srv/value-investing/current-staging` symlink 变更前后均不存在；运行 PostgreSQL 的 Compose config label 前后均指向批准 SHA。
- container/network/volume 前后均为 `4/5/1`；PostgreSQL container ID、network ID 和 volume 未变，仍 healthy；无宿主数据库端口。
- N5 本地/NAS dump SHA-256 仍同为 `4087bb53709ffc9b6b04c2ed22de98dc63e575dd89a156f4548b78d7314d583b`；64 MiB 制品 SHA-256 仍为 `3b6a07d0d404fab4e23b6d34bc6696a6a312dd92821332385e5af7c01c421351`；N5-01/NAS restore 仍 passed。
- `jason-vm`、OpenClaw、Syncthing、cloudflared、sing-box、SSH、Docker、libvirt 前后一致；Qdrant 保持 exited；无 L2/production 对象。

## 7. 回滚方法

如后续需回滚本轮修正，使用上述 root-only 快照中的 `value-investing-release-entry.before` 和 `ff2746f.approved.before.json` 原子恢复到原路径，恢复权限为入口 `0750 root:root`、manifest `0640 root:value-research`，然后复核变更前两个 SHA-256。回滚不需也不得移动 main、修改 release/evidence、重建 Docker 对象或修改数据库。

## 8. 最终结论与停止声明

**PASSED — L1 staging infrastructure ready for future L1.7 release.**

当前仅为空数据库 staging 环境。L1.7 仍需独立完整 SHA、manifest、迁移计划和部署批准。本次通过不授权 production；Docker daemon restart 和宿主 reboot 未执行且明确延期；L2 为 future/not-deployed。

本轮未修改 Git 仓库内容或移动 main，**未批准或部署 `87e9ca72147af7288fff9ab41a976be689067595`**，未修改 current-staging，未执行 Docker/Compose 变更，未重启 Docker 或宿主，未修改 SSH、firewall、network、libvirt 或既有服务，未输出数据库密码。完成后在此停止，不进入 L1.7 或 production。
