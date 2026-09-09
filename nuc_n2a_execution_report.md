---
title: NUC N2-A 最低宿主准备执行报告
status: completed-awaiting-24h-baseline
risk_grade: D3
date: 2026-08-29
scope: D3-N2-01, D3-N2-03, D3-N2-06A only
---

# NUC N2-A 最低宿主准备执行报告

## 结论

只执行了获批的 D3-N2-01、D3-N2-03、D3-N2-06A。没有进入 N3。受保护配置快照已建立；24 小时观测 timer 已启动并产生首个有效样本；`value-research` 系统身份和 L1 专用目录已创建并通过隔离检查。

## 实际变更

1. 创建 system group/user `value-research`：自动分配 UID 994、GID 992，shell `/usr/sbin/nologin`，home `/nonexistent`，无 home 目录。
2. 创建 `/srv/value-investing/` 下获批的 L1 目录；没有 L2 目录。
3. 创建 root-only 快照 `/srv/value-investing/admin-snapshots/20260829T045749Z/`，root:root 0700；106 个文件，约 0.9 MB。
4. 创建只读采样脚本 `/usr/local/libexec/value-research-baseline-sample`（root:root 0750）。
5. 创建并启用 `value-research-baseline.service` 与 `.timer`；120 秒间隔，24 小时阈值后自动停止采样。
6. 在 N1 文档末尾追加后续 scope amendment，并更新 draft JSON 的 amendment/L2 future 状态；没有伪装成原始 N1 结论。

## 实际执行命令

下列为本轮实际执行的变更命令或命令族；尖括号未用于实际执行：

```text
/usr/sbin/groupadd --system value-research
/usr/sbin/useradd --system --gid value-research --home-dir /nonexistent --no-create-home --shell /usr/sbin/nologin value-research
/usr/bin/install -d -o ... -g ... -m ... /srv/value-investing/<approved-paths>
cp -a <approved-existing-config> /srv/value-investing/admin-snapshots/20260829T045749Z/config/<category>/
将只读状态命令输出重定向到 snapshot/status/
sha256sum 生成 snapshot/MANIFEST.sha256
find/stat 生成 snapshot/FILES.tsv
chmod -R go-rwx /srv/value-investing/admin-snapshots/20260829T045749Z
chmod/chown 观测脚本、unit 和 baseline metadata
systemctl daemon-reload
systemctl enable --now value-research-baseline.timer
systemctl reset-failed value-research-baseline.service
systemctl start value-research-baseline.service
```

用于前置/验证的只读命令包括：`getent`、`findmnt`、`loginctl`、`ss`、`tailscale status`、`systemctl is-active/is-enabled/status/show/list-timers/cat`、`id`、`runuser ... test -r`、`find`、`stat`、`sha256sum`、`docker inspect`、`virsh domstate`、`systemd-analyze verify`、`sh -n`、`jq`、`rg`。

首次不带绝对路径的 `groupadd` 因 shell PATH 不含 `/usr/sbin` 而在第一步失败，未产生变更；随后使用绝对路径成功。观测首轮因一个温度节点返回 `No data available` 失败，未发布 `.tmp`；脚本改为跳过单个无数据传感器，删除该临时文件并重试成功。该异常没有影响其他服务。

## 验证结果

- SSH 两个既有监听正常；Tailscale backend online 且有 online peer，第二管理路径只读验证通过。物理本地控制台未远程实测。
- `value-research` 只属于自身组，不在 docker/sudo 组。
- `value-research` 无法读取 `/root/.openclaw`、`/root/.openclaw/workspace` 或 `/var/run/docker.sock`。
- `secrets/staging` 为空，没有写入真实密钥。
- Qdrant 保持 `exited`、`restart=no`；`jason-vm` 保持 running。
- SSH、Docker、libvirt、cloudflared、Syncthing 均保持 active。
- 首个有效样本成功：service exit 0，CPU 约 338 ms、memory peak 约 12.7 MiB；timer active/waiting。
- 未创建任何 Docker project/container/network/volume/image，未创建研究 VM，未启动或修改旧 Qdrant。

## timer 完成时间

- 观测阈值：2026-08-30 04:59:15 UTC，即 2026-08-30 14:59:15 AEST。
- timer 每 120 秒检查一次，预计在阈值后的第一个 tick 自动停止；正常情况下最迟约 15:01 AEST 形成摘要。
- 原始样本保留策略为完成后 7 天，脱敏摘要 30 天。为避免未经复核的自动删除，本轮未创建清理 timer；下次人工评审确认摘要后执行保留期清理卡。

## 回滚方法（未执行）

1. 观测：`systemctl disable --now value-research-baseline.timer`，确认 service inactive；删除新建 unit/script 和 baseline 文件需另行人工确认，再 `daemon-reload`。
2. 身份/目录：仅在确认目录无业务数据时，删除本轮目录，再 `userdel value-research`、`groupdel value-research`；含数据时禁止直接删除。
3. 快照：30 天后或 NUC-PRE 完成后，逐个确认精确时间戳目录再删除；快照 parent 不应整体递归删除。
4. N1 amendment：保留审计记录，不建议删除；若范围再变化，追加新 amendment。

## 停止点

N2-A 到此停止。等待 24 小时基线完成和下一次人工评审；未执行其他 N2 卡或 N3—N6。

## 2026-08-29 用户后续裁决（不追溯改写执行时停止点）

用户已根据后续实测确认：当前 load average 偏高不代表 CPU 持续繁忙，现有 CPU、I/O 和内存余量足以继续项目。已启动的 24 小时 timer 保留为并行诊断记录，但不再作为后续开发、Git/release 准备或 L1 staging 的等待门槛。后续工作可在低并发和既有最低隔离边界下直接推进；仅当出现持续资源饥饿、OOM 或受保护服务可归因回归时停止。
