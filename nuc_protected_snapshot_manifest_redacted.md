---
title: NUC 受保护快照脱敏清单
status: completed
date: 2026-08-29
retention_days: 30
---

# NUC 受保护快照脱敏清单

## 快照根

- 本地路径：`/srv/value-investing/admin-snapshots/20260829T045749Z/`
- 所有权/权限：root:root 0700
- 文件数：106
- 大小：894,859 bytes
- `MANIFEST.sha256` 自身 SHA-256：`9ae627b51f3a40dabf4f83d4a95698463fe871eeda061971056c787e0a983704`
- 保留：暂定 30 天；NUC-PRE 完成前不自动删除。

配置分类：SSH、network/UFW/nftables、Docker、libvirt、OpenClaw、Syncthing、cloudflared、sing-box。分类下可能含秘密；只保存在 root-only 本地目录，不在本报告列出敏感文件名或内容。

## 可公开记录的文件名、权限与哈希

```text
MANIFEST.sha256 | root:root 0600 | 9ae627b51f3a40dabf4f83d4a95698463fe871eeda061971056c787e0a983704
FILES.tsv | root:root 0600 | 1c4930b3228b6077e3c78f979d6b986a278e5eb4b00f2c7bd74931ecf7e68f9e
status/ssh-effective.txt | root:root 0600 | f406038dcd6b7a6d77dd31243e78bd3daf844a4de4809053c87dd5ffa5de1548
status/nft-ruleset.txt | root:root 0600 | 9f2c6810d4b3f36a06f0645d0d65dc2d2f2c41bb41f757c8e545ffb868c6f400
status/docker-info.txt | root:root 0600 | 81b15639af1ecb5cc4597e9891eda8f1c42e246c7188c0121b4e5526dd79aab1
status/jason-vm.xml | root:root 0600 | 7a770b9336db876fb770b47d1a7eab02a5da765a6b5a94a12d4ba4deda41067d
status/openclaw-status.txt | root:root 0600 | 46365dca44087058d80d75a00d794fd1e78f9bd8e4d2fd7f828af3d87250d3fa
```

其他敏感配置的逐文件权限和 SHA-256 位于内部 `FILES.tsv`/`MANIFEST.sha256`，受快照根 0700 保护。本 Obsidian 文件不包含 token、key、域名、IP 或身份内容。

## 采集方式

配置使用 `cp -a` 分类别复制。状态来自只读的 `sshd -T`、`ss`、`ip`、`nft list ruleset`、Docker info/ps/network/volume、精简 Qdrant inspect、virsh、systemd unit/status、OpenClaw status、Syncthing system、cloudflared tunnel list 和 Tailscale status。没有修改源配置或服务。

## 恢复边界

快照是恢复材料，不授权直接覆盖在线配置。任何恢复必须先比较差异、确认第二管理路径并按对象单独批准；禁止一次性整目录覆盖 `/etc` 或 `/root`。
