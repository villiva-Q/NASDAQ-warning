---
title: NUC N2-B L1 Git 与 release 通道执行报告
status: completed-channel-ready-no-release
risk_grade: D3
date: 2026-08-29
scope: L1 staging only
---

# NUC N2-B L1 Git 与 release 通道执行报告

## 结论

NUC bare Git 与 L1-only 固定 release 入口骨架已建立并通过负向测试。仓库为空，没有已验收 L1 commit SHA、approved manifest 或 release；因此 test/deploy/rollback 明确拒绝，不执行占位部署。未进入 N3。

24 小时资源 timer 继续 active，作为并行诊断，不阻塞本次结果。

## 实际变更

### Bare Git

- `/srv/git/value-investing-system.git`：root:root 0750，本地 NVMe ext4。
- 空 bare repository，HEAD=`refs/heads/main`，ref count=0。
- `receive.denyDeletes=true`、`receive.denyNonFastForwards=true`、`core.sharedRepository=false`。
- 不在 Obsidian、Syncthing 或 NAS；Syncthing folder root 仍为 NAS 上的 Obsidian vault。

### L1 release 通道目录

```text
/srv/value-investing/releases       root:value-research 0755
/srv/value-investing/manifests      root:value-research 0750
/srv/value-investing/locks          root:root           0750
/srv/value-investing/logs/deploy    root:value-research 0750
```

`releases`、`manifests` 均为空。没有创建 L2、production、VM、database 或 Docker object。

### 固定入口

- 主程序：`/usr/local/sbin/value-investing-release-entry`，root:root 0750。
- SHA-256：`77df696b5ba65864242b7ec3807464136b964eadf75f4cff45ce02ab9b5c14cb`。
- 固定入口 symlink：`deployment-status`、`test-staging`、`deploy-staging`、`rollback-staging`。
- 唯一语法：`<entry> FULL_SHA L1`。

实现约束：

- FULL_SHA 必须严格匹配 40 位 hexadecimal；branch、tag、短 SHA 和带 shell 字符文本均拒绝。
- Layer 严格等于 `L1`；L2、production 和额外参数拒绝。
- Python 使用固定 argv 调用 `/usr/bin/git`；无 `eval`、无 shell 拼接、无 Docker 调用。
- test/deploy/rollback 使用 `/srv/value-investing/locks/l1-staging.lock` 非阻塞排他锁。
- approved manifest 必须是 root-owned、不可 group/other write 的 regular file，并同时声明 full SHA、L1、review passed、audit passed。
- 当前 handler 标记为 N2-B disabled；即使未来存在 commit/manifest，本阶段也不执行 staging 动作，必须由后续 D3 启用。
- 日志只记录时间、固定 action、L1、验证后的 SHA、结果和 PID，不记录密钥或任意原始参数。
- release 根目录由 root 管理且应用身份不可原地修改；未来新 release 必须按完整 SHA 新建，完成后运行文件归 `value-research`，不得覆盖既有 release。

## 负向测试结果

```text
短 SHA                       rc=64 rejected
branch main                  rc=64 rejected
tag v1.0.0                   rc=64 rejected
自由文本/shell字符           rc=64 rejected，未执行
L2                           rc=64 rejected
production                   rc=64 rejected
额外参数                     rc=64 rejected
未知40位SHA test             rc=66 commit missing
未知40位SHA deploy           rc=66 commit missing
未知40位SHA rollback         rc=66 commit missing
并发锁占用                   rc=75 lock busy
未知40位SHA status           rc=0，只读报告 commit/manifest/release=false、Docker actions=false
```

测试后 ref count=0、release count=0、manifest count=0。测试日志 12 行，不含秘密。

## 运行身份验证

- `value-research` 仍只有自身组，不在 docker 或 sudo 组。
- 无法读取 bare repo、`/root/.openclaw`、其他现有 workspace 或 Docker socket。
- secrets 目录仍为空；未创建 SSH key、deploy key 或凭据。

## 回归验证

- SSH config mtime 未改变；SSH service 未重启，既有 `43382` 与 `12662` 监听保持。
- 固定入口没有监听 socket；未新增端口。
- Docker 保持 2 containers、4 networks、0 volumes；旧 Qdrant 仍 exited/restart=no。
- `jason-vm` running；Docker、libvirt、cloudflared、Syncthing、OpenClaw gateway 均保持原启动时间和 active/running。
- 24 小时 baseline timer active。
- systemd 仍只有 N0 已知的两个交易 transient failed units，没有新增 failed unit；本任务未处理或触发交易 payload。

## 实际执行命令

```text
install -d（仅批准的 /srv/git 与 /srv/value-investing 路径）
git init --bare --initial-branch=main /srv/git/value-investing-system.git
git --git-dir=... config receive.denyDeletes true
git --git-dir=... config receive.denyNonFastForwards true
git --git-dir=... config core.sharedRepository false
chown/chmod（仅新建 repo、目录和入口）
ln -s value-investing-release-entry /usr/local/sbin/{deployment-status,test-staging,deploy-staging,rollback-staging}
python3 -m py_compile（静态检查；生成的 pycache 随后精确删除）
flock（仅用于锁竞争负向测试）
固定入口负向测试命令
```

只读验证命令包括：`getent`、`findmnt`、`ip`、`ss`、`journalctl`、`systemctl show/is-active/--failed`、`docker ps/network/volume/inspect`、`virsh domstate`、`git symbolic-ref/for-each-ref/fsck`、`id`、`runuser test -r`、`find`、`stat`、`sha256sum`。

## 回滚方法（未执行）

1. 确认 repo ref count、release count、manifest count 仍为 0，且没有 Mac push 正在进行。
2. 精确删除四个入口 symlink 和 `/usr/local/sbin/value-investing-release-entry`。
3. 删除本卡创建的空 `manifests`、`locks`、`logs/deploy`；保留已有 L1 runtime 目录。
4. 精确删除空 bare repo `/srv/git/value-investing-system.git`；若已有任何 commit，必须先取得新的备份/删除批准。
5. `value-research` 身份和 N2-A baseline/snapshot 不属于本卡回滚范围。

## 停止点

N2-B 到此停止。等待 Mac 推送真实 L1 commit，随后另行进行 commit 复验、review/audit manifest 审批与后续 D3；当前不启动 PostgreSQL，不创建 L1 Docker network/volume/container，不进入 N3。
