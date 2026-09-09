# NUC D3-N5-01 / D3-N5-02 执行报告（失败停止）

- RUN_ID：`20260829T125352Z`
- release SHA：`ff2746f00ed0cb0112e09c3caa09a8354777c745`
- PostgreSQL image digest：`postgres@sha256:5660c2cbfea50c7a9127d17dc4e48543eedd3d7a41a595a2dfa572471e37e64c`
- 最终状态：**D3-N5-01 未完成，已按失败停止条件停止；D3-N5-02 未开始。**

## 前置检查

- L1 staging PostgreSQL：healthy；manifest、release SHA 与运行镜像一致。
- 宿主 PostgreSQL 监听端口：0。
- 主 network：`value-investing-l1-staging-network`；主 volume：`value_investing_l1_staging_postgres_data`。
- 三个临时数据库名和三个临时 Docker 对象执行前均不存在。
- 本地 NVMe 可用空间：1,773,710,827,520 bytes。
- NAS：CIFS 3.0、`rw`，使用率 74%，可用 4,169,064,226,816 bytes；挂载身份和地址已脱敏。
- 执行前 Docker container/network/volume 数：`4/5/1`。

## 已执行变更

- 创建专用源数据库 `value_research_n5_source`。
- 创建 schema `n5_drill` 与表 `n5_drill.payload`，写入 10,000 行确定性数据。
- `pg_dump` 已产生 `/srv/value-investing/backups/l1-staging/n5-drill-20260829T125352Z.dump.partial`。
- `.partial`：218,181 bytes，SHA-256 `4087bb53709ffc9b6b04c2ed22de98dc63e575dd89a156f4548b78d7314d583b`，权限 `0640 root:value-research`。

## 失败点与停止状态

- 失败命令族：`docker exec -i <staging-postgres> pg_restore --list - < .partial`
- 错误：`pg_restore: error: could not open input file "-": No such file or directory`
- 原因：该 `pg_restore` 调用将 `-` 解释为文件名，未从 stdin 校验 archive。
- `pg_dump` 本身已成功；失败发生在正式发布前的 archive-list 校验。
- `.partial` 未原子改名为正式 dump；未创建本地正式 manifest。
- 未创建恢复 container/network/volume；未写 NAS；未创建完成标记。
- 按任务书“任一步失败立即停止后续步骤”，本轮未用修正命令继续。

## 保留对象与安全重试点

- 保留源数据库 `value_research_n5_source`，供核查。
- 保留上述 `.partial`，供核查；它不被视为正式备份。
- 安全重试点：经再次人工批准后，先验证源库指标未变，再使用容器可访问的临时副本或明确支持 stdin 的校验方式执行 `pg_restore --list`；验证通过后才可发布正式 dump。不得覆盖本 RUN_ID 文件。

## 回归检查

- 主 L1 staging PostgreSQL：healthy；宿主新增 PostgreSQL 监听端口：0。
- 临时恢复 container/network/volume：无。
- `jason-vm` running；OpenClaw、Syncthing、cloudflared active。
- Qdrant 仍为 exited。
- 主 staging network、volume、release、approved manifest 未修改。
- 未执行 Alembic、L2、N6、production、Docker daemon/SSH/firewall/libvirt 变更。
- 未读取、记录或输出数据库密码。

## 实际执行命令族

- 前置：`docker ps/inspect/network inspect/volume inspect`、`ss`、`df`、`findmnt`、`virsh domstate`、`systemctl is-active`。
- 数据库：容器内 `createdb`、`psql`、`pg_dump`、`pg_restore --list`。
- 文件验证：`stat`、`sha256sum`、权限检查。

等待人工评审；本报告不构成继续 N5 或进入 N6 的授权。

---

## 人工评审后重试（2026-08-29）

### 重试授权与检查点

- 复用 RUN_ID `20260829T125352Z`，未生成新编号。
- 复用 `value_research_n5_source` 和原 `.partial`；未重新创建源库，未重新执行 `pg_dump`。
- 重试前源库指标仍为：schema 对象 2、表 1、行 10,000、内容校验值 `b358506a6c5b0d253d8f5139ae8b5334`、PostgreSQL 16.4。
- 原 `.partial` 大小仍为 218,181 bytes，SHA-256 仍为 `4087bb53709ffc9b6b04c2ed22de98dc63e575dd89a156f4548b78d7314d583b`。
- 主 staging healthy；无恢复 Docker 遗留对象；NAS 无本 RUN_ID 正式文件，使用率 74%。

### 原错误与修正

- 原错误形式：`docker exec -i <container> pg_restore --list - < <partial>`；exit 非 0，`-` 被解释为 filename。
- 修正形式：`docker exec -i <container> pg_restore --list < <partial>`；真实 exit code 0。
- TOC 非空，archive 为 PostgreSQL custom format，包含 `SCHEMA n5_drill`、`TABLE n5_drill payload`、`TABLE DATA` 和主键 constraint。
- 初次 TOC 自动断言因 schema 行包含 owner 占位列 `-` 而假阴性；`pg_restore` 本身已成功。调整为匹配实际 TOC 字段后通过，期间未改动 dump。
- 正式发布前后大小与 SHA-256 完全一致；原子发布为 `/srv/value-investing/backups/l1-staging/n5-drill-20260829T125352Z.dump`。
- 本地 dump manifest：`/srv/value-investing/backups/l1-staging/n5-drill-20260829T125352Z.manifest.json`；SHA-256 `d545e5fc11af93eeb0335dfc226058f6f5985a3cda556ca38d391dfdbe81876e`。

### N5-01 最终结果：PASS

- 独立对象曾创建：container `value-investing-n5-restore`、network `value-investing-n5-restore-network`、volume `value_investing_n5_restore_data`，均带 `D3-N5-01` 与 RUN_ID 标签。
- 使用与 staging manifest 相同的 image digest；无宿主端口、无主 staging network/volume、NAS 或禁用路径挂载。
- 恢复 PostgreSQL PID 1 UID 为 70；容器 healthy；限制为 1 CPU、1 GiB、PID 128、json-file `10m × 3`、no-new-privileges。
- `value_research_n5_restore` 恢复命令从 stdin 读取 dump，未传 `-` filename，exit 0。
- 源库/首次恢复库逻辑指标完全一致：`2 / 1 / 10000 / b358506a6c5b0d253d8f5139ae8b5334 / PostgreSQL 16.4`。
- 源/恢复物理数据库大小分别为 8,802,787 / 8,737,251 bytes；物理占用不是原任务逻辑一致性门禁。组合验收曾因额外要求物理大小相等而提前退出；只读定位确认所有规定逻辑指标一致，因此未重做恢复。
- RPO：测试数据完成后无新提交，逻辑 RPO 为 0 次变更；原首次执行未保留精确时间戳，备份及首次恢复耗时只能诚实记录为各自在单次 30 秒命令窗口内完成，不能伪造更精确数值。
- 工具版本：pg_dump/pg_restore/PostgreSQL 16.4。

### N5-02 最终结果：PASS

- NAS 目录：`/mnt/nas/value-investing-research/l1-staging/backup-drill/`；CIFS 3.0、`rw`，完成后使用率 74%。
- dump 三方 SHA-256（本地/NAS/回读）：均为 `4087bb53709ffc9b6b04c2ed22de98dc63e575dd89a156f4548b78d7314d583b`；大小均为 218,181 bytes。
- 64 MiB 确定性文件三方 SHA-256：均为 `3b6a07d0d404fab4e23b6d34bc6696a6a312dd92821332385e5af7c01c421351`；大小均为 67,108,864 bytes。
- 两个文件均经 NAS 同目录 `.partial`、大小/哈希校验和原子 rename 发布。
- NAS 回读 dump 恢复至 `value_research_n5_nas_restore`，exit 0；开始/完成时间均为 `2026-08-29T13:06:08Z`（墙钟分辨率 1 秒，耗时不足 1 秒）。
- NAS 恢复逻辑指标：`2 / 1 / 10000 / b358506a6c5b0d253d8f5139ae8b5334 / PostgreSQL 16.4`，与源库一致。
- NAS manifest：`manifest-20260829T125352Z.json`，`completed=true`，SHA-256 `b90d8b1dc29e214050063b4976dc4a47e07c26509b6ff68b0e80ced7ec0b57c4`。
- 完成标记：`COMPLETED-20260829T125352Z`，SHA-256 `bb0d95b3a405afd280c52d2ccebd2708b20c891f748413bdada7d3edb8fd15ef`。

### 清理、保留与回归

- 已精确删除三个临时数据库、带标签的临时 container/network/volume、临时 env、restore-check 目录和本地 64 MiB 源文件。
- Docker 数量恢复为 container/network/volume=`4/5/1`；无 N5 临时对象遗留。
- 保留：本地正式 dump 与本地 manifest；NAS 正式 dump、64 MiB 归档、manifest、完成标记；三份 Obsidian 报告。
- 本地正式 dump 至少保留 7 天；NAS 演练制品保留至 N6 验收完成，删除需独立批准。
- L1 staging PostgreSQL 仍 healthy，无宿主数据库监听；主 network/volume/release/approved manifest 未变。
- `jason-vm` running；SSH、Docker、libvirtd、OpenClaw、Syncthing、cloudflared active；失败单元仍为既有 2 个；Qdrant 仍 exited。
- Syncthing 配置的同步根仅为 Obsidian vault；数据库 dump、volume、临时 env 和恢复目录均不在同步根内。
- 未执行 Alembic、L2、N6、production、Docker daemon、SSH、firewall、br0 或 libvirt 变更。
- 全程未记录或输出数据库密码。

人工评审后重试最终完成 N5-01 与 N5-02，并在此停止；不进入 N6。
