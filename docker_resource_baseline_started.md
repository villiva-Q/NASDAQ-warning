---
title: Docker 宿主资源基线已启动
status: collecting
date: 2026-08-29
interval_seconds: 120
duration_hours: 24
---

# Docker 宿主资源基线已启动

## 状态

- Timer：`value-research-baseline.timer`，enabled、active、waiting。
- Service：`value-research-baseline.service`，oneshot；首个有效样本 exit 0。
- 脚本：`/usr/local/libexec/value-research-baseline-sample`，root:root 0750。
- 输出：`/srv/value-investing/baseline/`，root:value-research 0750；样本 0640。
- 间隔：120 秒。
- 目标截止：2026-08-30 04:59:15 UTC / 2026-08-30 14:59:15 AEST；预计下一个 tick 自动停止，正常最迟约 15:01 AEST。

## 采集范围

- `/proc/loadavg`、`/proc/uptime`、CPU 累计、筛选后的内存字段。
- NVMe `/proc/diskstats`。
- 不含命令参数的 top process 摘要：user、PID、comm、state、CPU%、memory%。
- `docker stats --no-stream`。
- `virsh domstats jason-vm` 的状态、vCPU、balloon、block 和 interface 计数。
- thermal zone 温度；无数据的单个传感器被跳过。

不读取进程环境变量、完整命令行、业务 payload、密钥或 token。

## 保护和停止条件

- service 配置 `CPUQuota=1%`、Nice=10、idle I/O scheduling、NoNewPrivileges 和受限写路径。
- baseline 目录达到 256 MiB、任何有效温度达到 90°C、受保护服务 inactive 或 `jason-vm` 非 running 时，脚本写本地 ALERT 并停止自己的 timer。
- 首个有效样本 CPU 约 338 ms、memory peak 约 12.7 MiB，无 ALERT。

## 首轮异常及修正

第一次自动采样遇到一个 thermal node 返回 `No data available`，service 非零退出且未发布临时样本。脚本随后改为忽略单个无数据节点，删除本轮 `.tmp`，静态校验和重试均成功。未重启或修改任何现有服务。

## 保留与后续

- 原始样本：完成后保留 7 天。
- 脱敏摘要：保留 30 天。
- 本轮未创建自动删除任务；下次人工评审先审阅摘要，再按精确路径批准清理，避免无人复核删除证据。
- 本报告只表示 collection started，不表示 24 小时基线已通过。

## 回滚（未执行）

`systemctl disable --now value-research-baseline.timer` 只停止本观测 timer。确认 service inactive 后，unit、脚本、样本和目录的删除必须另行批准。
