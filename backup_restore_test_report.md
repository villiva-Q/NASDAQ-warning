# D3-N5-01 本地备份恢复测试报告（未完成）

- RUN_ID：`20260829T125352Z`
- 结果：**FAIL / STOPPED**
- release SHA：`ff2746f00ed0cb0112e09c3caa09a8354777c745`
- PostgreSQL / pg_dump 版本：16.4

## 源数据库指标

- 数据库：`value_research_n5_source`
- schema 对象数：2
- 表数：1
- 行数：10,000
- 按主键排序的内容校验值：`b358506a6c5b0d253d8f5139ae8b5334`
- 数据库大小：8,802,787 bytes

## 备份状态

- 路径：`/srv/value-investing/backups/l1-staging/n5-drill-20260829T125352Z.dump.partial`
- 大小：218,181 bytes
- SHA-256：`4087bb53709ffc9b6b04c2ed22de98dc63e575dd89a156f4548b78d7314d583b`
- 权限：`0640 root:value-research`
- 状态：`pg_dump` 成功，但 archive-list 校验命令失败，故未发布为正式 `.dump`。

## 恢复与时效指标

- 独立恢复环境：未创建。
- 首次恢复库：未创建。
- 恢复行数/校验值：未产生。
- RPO、备份耗时、恢复耗时：因流程在正式备份发布前停止，不声明成功指标。

## 失败记录

- `pg_restore --list -` 返回：无法打开名为 `-` 的输入文件。
- 未继续 N5-01 后续步骤；源数据库与 `.partial` 按失败证据保留。
- 首次 SQL 命令曾在宿主 shell 解析阶段因引号错误退出，未产生变更；第二次创建源库成功后，度量/备份组合命令提前退出。只读定位确认 10,000 行数据完整，随后单独执行 `pg_dump`。最终在 archive-list 校验处触发正式停止。
- 未输出数据库密码。

等待新的人工批准后从安全重试点继续。

---

## 人工评审后重试

- 复用 RUN_ID `20260829T125352Z`、源库和原 `.partial`；未重新运行 `pg_dump`。
- 原命令把 `-` 作为 filename，失败；修正为 `docker exec -i <container> pg_restore --list < <partial>`，exit 0。
- TOC 非空并包含预期 schema、payload 表、TABLE DATA 与主键；custom-format 可读取。
- `.partial` 重试前后大小均为 218,181 bytes，SHA-256 均为 `4087bb53709ffc9b6b04c2ed22de98dc63e575dd89a156f4548b78d7314d583b`；随后原子发布正式 dump。
- 首次独立恢复使用同一 image digest、无端口、专用 network/volume；恢复命令省略 filename，exit 0。

### 最终逻辑对比

- 源库：schema 对象 2；表 1；行 10,000；checksum `b358506a6c5b0d253d8f5139ae8b5334`；PostgreSQL 16.4。
- 首次恢复库：schema 对象 2；表 1；行 10,000；checksum `b358506a6c5b0d253d8f5139ae8b5334`；PostgreSQL 16.4。
- dump：218,181 bytes；SHA-256 `4087bb53709ffc9b6b04c2ed22de98dc63e575dd89a156f4548b78d7314d583b`。
- 逻辑 RPO：0 次变更。原执行没有持久化精确起止时间；备份与首次恢复均在各自单次 30 秒命令窗口内完成，这是可证明的时间上界。
- pg_dump/pg_restore：16.4。
- 一次额外物理大小相等断言产生假失败；物理大小差异不影响任务要求的逻辑一致性，未重新恢复。

最终结果：**PASS**。临时源库、首次恢复库、NAS 恢复库及临时 Docker 对象已按固定名称和任务标签精确清理。正式 dump 和本地 manifest 保留。未输出数据库密码。
