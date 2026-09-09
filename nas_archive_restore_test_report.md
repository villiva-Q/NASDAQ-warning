# D3-N5-02 NAS 冷归档恢复测试报告（未执行）

- RUN_ID：`20260829T125352Z`
- 结果：**NOT STARTED**
- 原因：D3-N5-01 未完整通过，按硬前置门禁禁止进入 N5-02。

## NAS 前置状态

- 目标：`/mnt/nas/value-investing-research/l1-staging/backup-drill/`
- 协议：CIFS 3.0，挂载为 `rw`。
- 执行前使用率：74%；可用空间：4,169,064,226,816 bytes。
- 没有为本 RUN_ID 创建 NAS dump、大型测试文件、manifest 或完成标记。
- 没有创建本地 64 MiB 测试源文件或 restore-check 目录。
- 没有创建 `value_research_n5_nas_restore` 数据库。

## 哈希与恢复结果

- 源/归档/恢复三方哈希：未产生。
- NAS 恢复数据库行数和内容校验值：未产生。
- NAS 既有文件未修改或删除。
- 未向任何容器挂载 NAS。

## 停止声明

N5-02 未执行，未创建完成标记，未进入 N6。需先重新批准并完整通过 N5-01，才能再次评估 NAS 归档演练。未记录或输出任何数据库密码。

---

## 人工评审后重试

- 复用 RUN_ID：`20260829T125352Z`。
- N5-01 重试通过后进入 N5-02；NAS 使用率执行前后均为 74%。
- NAS 协议：CIFS 3.0，`rw`；没有把 NAS 挂入容器。

### 三方文件验证

- dump 大小：218,181 bytes；本地源/NAS 正式归档/本地回读 SHA-256 均为 `4087bb53709ffc9b6b04c2ed22de98dc63e575dd89a156f4548b78d7314d583b`。
- 64 MiB 确定性文件大小：67,108,864 bytes；三方 SHA-256 均为 `3b6a07d0d404fab4e23b6d34bc6696a6a312dd92821332385e5af7c01c421351`。
- 两个归档均先写 NAS 同目录 `.partial`，通过大小和 SHA-256 校验后原子改名。

### NAS 回读数据库恢复

- 回读 dump 恢复至 `value_research_n5_nas_restore`，`pg_restore` exit 0。
- 开始/完成：`2026-08-29T13:06:08Z` / `2026-08-29T13:06:08Z`；墙钟分辨率为 1 秒，耗时不足 1 秒。
- schema 对象 2；表 1；行 10,000；checksum `b358506a6c5b0d253d8f5139ae8b5334`；PostgreSQL 16.4，与源库一致。
- 正式 manifest：`manifest-20260829T125352Z.json`，`completed=true`，SHA-256 `b90d8b1dc29e214050063b4976dc4a47e07c26509b6ff68b0e80ced7ec0b57c4`。
- 完成标记：`COMPLETED-20260829T125352Z`，SHA-256 `bb0d95b3a405afd280c52d2ccebd2708b20c891f748413bdada7d3edb8fd15ef`。

### 清理与保留

- 已删除本地 restore-check、64 MiB 源文件、三个临时数据库和临时 Docker container/network/volume/env。
- 保留 NAS 正式 dump、64 MiB 归档、正式 manifest 与完成标记，直至 N6 验收完成；后续删除需独立批准。
- 未修改或删除其他 NAS 文件；未执行 N6；未输出数据库密码。

最终结果：**PASS**。
