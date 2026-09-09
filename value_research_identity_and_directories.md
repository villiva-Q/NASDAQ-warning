---
title: value-research 身份与第一层目录
status: completed
date: 2026-08-29
scope: L1 only
---

# value-research 身份与第一层目录

## 身份

- User：`value-research`，system UID 994。
- Group：`value-research`，system GID 992。
- Shell：`/usr/sbin/nologin`。
- Home：`/nonexistent`，未创建 home。
- Supplementary groups：无；不在 docker 或 sudo 组。
- 未创建 SSH key、deploy key、Git remote、wrapper 或 repository。

验证：以该身份执行只读可读性测试，`/root/.openclaw`、`/root/.openclaw/workspace` 和 `/var/run/docker.sock` 均 denied。后两者分别代表现有业务/交易工作区边界与 Docker 控制面；没有读取其内容。

## 目录权限

```text
/srv/value-investing/                    root:root             0755
releases/                                root:value-research   0755
config/                                  root:value-research   0750
config/staging/                          root:value-research   0750
secrets/                                 root:value-research   0750
secrets/staging/                         root:value-research   0750 (empty)
data/                                    value-research:value-research 0750
data/l1/                                 value-research:value-research 0750
objects/                                 value-research:value-research 0750
objects/sha256/                          value-research:value-research 0750
parquet/                                 value-research:value-research 0750
exports/                                 value-research:value-research 0750
cache/                                   value-research:value-research 0750
backups/                                 value-research:value-research 0750
logs/                                    value-research:value-research 0750
baseline/                                root:value-research   0750
```

`admin-snapshots/` 是 D3-N2-01 管理目录，不属于应用运行身份；时间戳快照 root:root 0700。

没有创建 L2 目录。没有向 secrets 写入密钥。没有 NAS bind、Docker volume 或 Syncthing 配置变更。

## 职责说明

- root 管理 releases/config/secrets 和基线采集，运行身份只有必要的读/进入权限。
- `value-research` 可写 L1 data/object/parquet/export/cache/backup/log 工作区。
- 当前 releases 为空；本轮不创建 release 或 deploy wrapper。

## 回滚（未执行）

只有在确认所有目录为空且没有 baseline/snapshot 保留要求时，才能按精确路径删除本轮目录，然后执行 `userdel value-research` 和 `groupdel value-research`。当前快照和基线正在保留，不能直接整体回滚 `/srv/value-investing`。
