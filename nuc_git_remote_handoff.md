---
title: NUC Git remote 交接
status: ready-for-first-L1-push
date: 2026-08-29
scope: Mac and Co-op handoff
---

# NUC Git remote 交接

## Mac 端准确命令

在 Mac 的 `value-investing-system` 工作仓库根目录执行：

```bash
git remote add nuc ssh://root@192.168.50.232:43382/srv/git/value-investing-system.git
git push nuc main
```

该命令复用已验证的 `root` SSH 管理路径、NUC LAN 地址和现有端口 43382；本次未修改 sshd、authorized keys、监听端口、防火墙或公网暴露。

若本地已经存在名为 `nuc` 的 remote，不要重复 add 或自行覆盖；先执行 `git remote get-url nuc`，将结果交给人工复核。

## 推送前检查

```bash
git status --short
git branch --show-current
git rev-parse --verify HEAD
git rev-parse HEAD
git remote -v
```

应确认当前 branch 是 `main`，工作树状态符合提交意图，并记录 `git rev-parse HEAD` 返回的 40 位 full SHA。不要推送 secrets、`.env`、数据库、WAL、交易数据、OpenClaw 配置或 NAS 工作集。

## 推送后只读状态检查

```bash
FULL_SHA=$(git rev-parse HEAD)
ssh -p 43382 root@192.168.50.232 /usr/local/sbin/deployment-status "$FULL_SHA" L1
```

第一次 push 后预期：`commit_exists=true`，但在 review/audit manifest 尚未批准前，`approved_manifest=false`、`docker_actions_enabled=false`。这不是错误，而是当前停止门。

不要执行 test/deploy/rollback 来绕过该门。它们会明确拒绝没有通过复验和审计的 SHA；当前 N2-B handler 也未启用 Docker action。

## 固定入口契约

```text
deployment-status FULL_SHA L1
test-staging FULL_SHA L1
deploy-staging FULL_SHA L1
rollback-staging FULL_SHA L1
```

远程非交互调用应使用 `/usr/local/sbin/<entry>` 的绝对路径，避免依赖 SSH 会话 PATH。

只允许 40 位 hexadecimal full SHA 和层级 L1。禁止 branch、tag、短 SHA、L2、production、额外参数及自由文本 shell。Co-op 应把 full SHA 作为结构化字段传递，不拼接 shell。

## 数据与传输边界

- Bare repo：`/srv/git/value-investing-system.git`，本地 NVMe。
- Release：`/srv/value-investing/releases/<full_sha>/`，尚未创建。
- Manifest：`/srv/value-investing/manifests/<full_sha>.approved.json`，尚未创建。
- Git 不经 Syncthing、Obsidian 或 NAS 传输。
- 当前只有 L1；L2/production/future VM 均未部署。

## 下一次人工评审所需证据

1. Mac 推送的 full commit SHA。
2. Bare repo 中该 commit 可读取，tree 不含 secrets/大文件误入。
3. L1 tests、依赖锁定、license/security review 与 audit 结果。
4. 拟批准的 root-owned manifest 内容和 SHA-256。
5. N3 前精确 Compose config；不得含 privileged、host network、Docker socket、交易/OpenClaw/NAS 整体挂载或 LAN 数据库端口。

只有新 D3 明确批准后，才能启用 test/deploy handler 或创建任何 Docker object。
