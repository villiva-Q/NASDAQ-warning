# D3-N6-01 L1 staging 空环境综合验收报告

- 执行日期：2026-08-30（UTC）
- 授权范围：仅 L1 staging 空环境；未执行 L2、production、Docker daemon restart 或宿主 reboot。
- 批准 release SHA：`ff2746f00ed0cb0112e09c3caa09a8354777c745`
- 结果：**PARTIAL PASS / GATE BLOCKED**

## 停止、启动与数据持久性

- 在 `value_investing_l1_staging` 中创建一次性数据库 `n6_persistence_20260830t0004z`，写入 `1:D3-N6-01`。
- 使用批准 release 的 Compose 文件和 staging env 对 `value-investing-l1-staging` 执行 `stop` 与 `start`；未执行 `down`，未使用 `--volumes`。
- 停止后容器状态为 `exited`，volume `value_investing_l1_staging_postgres_data` 仍存在。
- 启动后 PostgreSQL 恢复 `healthy`；容器 ID 前后均为 `f13a21240750c33b602f3ee59b5e7080f1260951b5999989ba8ca1a422ee3205`，volume 名前后一致。
- 重启后读回标记 `1:D3-N6-01`，持久性 PASS。验收后已删除一次性数据库，遗留数为 0。

## 端口、network、volume、权限和资源限制

- PostgreSQL 仅声明容器内 `5432/tcp`，HostPort 为 null；宿主未发现 `5432/54329/6333/6334` TCP/UDP 监听。
- network：`value-investing-l1-staging-network`，bridge，Compose project label 正确，验收后仅 PostgreSQL 运行容器连接。
- volume：`value_investing_l1_staging_postgres_data`，local，Compose project label 正确；数据目录 `0700 70:70`。
- PostgreSQL 配置用户 `postgres:postgres`，容器内 UID 70；`privileged=false`、`cap_drop=ALL`、`no-new-privileges=true`，无 host PID、host network 或 Docker socket。
- 限制：1 CPU、1 GiB memory、PID 128、`unless-stopped`；抽样为 CPU 0.03%、memory 19.64 MiB、PID 6。
- 唯一 mount 为上述 PostgreSQL volume 到 `/var/lib/postgresql/data`，无 NAS、交易目录、OpenClaw 目录或 Syncthing 目录。

## 固定入口与负向测试

- `/usr/local/sbin/deployment-status <approved-sha> L1`：rc 0，返回 approved/L1/staging/healthy。
- 错误完整 SHA：rc 66，`FULL_SHA is not present`。
- L2：rc 64，`only layer L1 is allowed`。
- production/额外参数：rc 64，usage 拒绝。
- 入口 SHA-256 仍为 `ed38adfae27f77ab3ba177824892cf10c3a868eb477bc79190ac3ef14e6529c0`；approved manifest SHA-256 仍为 `595516eb45a6a88e90ea4ab28070ae0474712763805968c5af91ca2e483cce5b`。
- **阻塞项**：`test-staging <approved-sha> L1` 返回 rc 68，`refs/heads/main does not equal FULL_SHA`。当前 bare Git `main` 为 `87e9ca72147af7288fff9ab41a976be689067595`，不再等于批准 SHA。未擅自移动 Git ref、批准新 manifest 或部署新 release。

## 结论

L1 空环境的停启、数据持久性、隔离、权限、资源限制和负向拒绝全部通过；但合法批准 SHA 的 `test-staging` 因 `main` ref 漂移失败。D3-N6-01 不能记为全量 PASS。

---

## D3-N6-01R 复验追加（2026-08-30 UTC）

- 原 `PARTIAL PASS / GATE BLOCKED` 结论保留为历史记录。
- 固定入口现依据 manifest 中的 `approved_commit_sha`、`main_sha_at_approval`、evidence/Compose/image digest 和授权字段验证已批准 release，不再要求 target 等于当前 `main`。
- 批准 SHA 在当前 `main=87e9ca72147af7288fff9ab41a976be689067595` 时重跑 `test-staging` rc 0，输出 `main_advanced=true`，未执行 Docker 变更。
- 当前未批准 main、未知 SHA、短 SHA、branch、tag、L2、production 和额外参数全部被拒绝。
- root-only 临时 fixture 对 manifest target、evidence hash、Compose hash、image digest 和可写权限的破坏全部被拒绝，真实 manifest 与 immutable release 未用于破坏测试。
- 已批准历史 SHA 的 rollback target 验证 rc 0，显式返回 `docker_change_performed=false`；并发锁测试返回 rc 75。
- 本轮不重复 stop/start、N5、Docker daemon restart 或宿主 reboot。

**D3-N6-01R 结果：PASS；D3-N6-01 唯一失败项已关闭。**
