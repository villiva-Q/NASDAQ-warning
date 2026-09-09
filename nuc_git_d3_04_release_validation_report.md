---
title: NUC D3-GIT-04 首次完整 SHA 与 release 通道验证报告
status: completed-no-deploy
risk_grade: D3
date: 2026-08-29
layer: L1
full_sha: 1844fa61b34b95ba3f17fb332bff7ff45a5fc59b
---

# NUC D3-GIT-04 首次完整 SHA 与 release 通道验证报告

## 结论

D3-GIT-04 已通过：bare repo 的 `refs/heads/main`、commit object 和批准 SHA 精确一致；Git object/tree、临时 worktree 洁净性、三份证据及 approved manifest 已验证；`test-staging FULL_SHA L1` 通过且明确 `docker_actions_enabled=false`；release 已只读、immutable 物化。

没有执行 `deploy-staging`，没有启动 Docker/PostgreSQL，没有创建 network、volume、container、L2、production 或研究 VM，未进入 N3。24 小时 timer 继续并行运行。

## Git 与工作树完整性

```text
refs/heads/main = 1844fa61b34b95ba3f17fb332bff7ff45a5fc59b
commit object    = 1844fa61b34b95ba3f17fb332bff7ff45a5fc59b
tree object      = 0c2a9e0f3719d973f7961ed58f6be1087a2c1430
object type      = commit
tracked files    = 62
tracked bytes    = 347,510
symlinks         = 0
```

- `git fsck --full --strict --no-dangling` 通过。
- 临时 detached worktree HEAD 精确匹配 full SHA。
- `git status --porcelain=v2 --untracked-files=all` 为 0 行；index/worktree diff 均为空。
- 临时 worktree 已用 `git worktree remove --force` 清理并 prune；bare repo 只保留自身 worktree 记录。
- 跟踪文件名扫描唯一命中 `.env.example`；内容是明确的本地开发占位说明，真实 `.env` 未入库。未发现 key/pem/dump/database 文件名。

## 证据核验与 SHA-256

```text
docs/runbooks/L1.0_test_report.md
99fe49168f091b0ae2db7cd8ce8525bb4526e214cba4872b88696c98b433e237

docs/runbooks/backup_restore_drill.md
aceaa1271d4d3ff999abf41ceecac38ebd56f63f98931d8d736b573c0ea26d25

docs/runbooks/L1.0_audit_report.md
78084c92924219b6f00f4645bee0dfbe5688278bb9f485912459354a423834d3
```

测试报告结论为 L1.0 复验通过；备份恢复演练结论为通过。独立审计结论是“通过（有保留）”、无阻塞项：静态审计全部通过，但该审计会话未独立动态复跑 pytest、migration、容器属性及备份恢复，相关动态结论依赖已单独哈希的执行报告。manifest 如实保留该 qualification，没有写成无保留通过。

## Approved manifest

- 文件：`/srv/value-investing/manifests/1844fa61b34b95ba3f17fb332bff7ff45a5fc59b.approved.json`
- 所有权/权限：root:value-research 0640。
- SHA-256：`b82447d0abbb571685542dff7c28e0f0162967c104e69fc9b4a2ba7771235945`。
- 绑定：full commit SHA、main ref、tree SHA、上述三份 evidence SHA-256、review passed、audit passed-with-reservation。
- 明确为 false：Docker authorization、deploy-staging authorization、PostgreSQL、network/volume、production。

固定入口现会从该 commit 重新读取三份 Git blob 并计算 SHA-256，必须与 manifest 完全一致；manifest 必须为 root-owned regular file，且 group/other 不可写。

## `test-staging` 结果

最终执行：

```text
/usr/local/sbin/test-staging 1844fa61b34b95ba3f17fb332bff7ff45a5fc59b L1
rc=0
status=validation-passed-no-deploy
commit_exists=true
approved_manifest=true
evidence_hashes_verified=true
main_ref_matches=true
docker_actions_enabled=false
```

首次执行曾返回 rc=67：入口误用 40 位 commit SHA 正则校验 64 位 SHA-256 evidence digest。该问题只导致安全拒绝，未产生 release 或 Docker 动作。新增独立 64 位 digest 正则后静态校验及重试通过。

物化后 `deployment-status` 的布尔字段正确但沿用旧标签 `channel-ready-no-release`；已只修正标签为 `release-materialized-no-deploy`，执行权限未改变。

## Release 物化与不可变性

- 路径：`/srv/value-investing/releases/1844fa61b34b95ba3f17fb332bff7ff45a5fc59b/`
- 物化：从固定 commit 执行 `git archive` 到同文件系统临时目录；逐一比较全部 62 个 materialized file 的 `git hash-object` 与 tree blob object；文件集合差异=0；随后原子 rename。
- 规模：62 files、27 directories、347,510 bytes。
- 所有权：全部 `value-research:value-research`。
- 模式：目录及 Git executable 为 0555，普通文件 0444；可写项=0。
- ext4 属性：全部 89 个文件/目录均具有 immutable `i`；缺失数=0。
- 运行用户写入负向测试返回 `Operation not permitted`；证据文件哈希保持不变。
- Release 没有 `.git`、额外 metadata 或 untracked file；release 只包含该 commit 的 tree。

若以后要删除或替换，只能创建新 full-SHA release；不得解除 immutable 后原地修改本 release。

## 负向测试

```text
正确 SHA / L1 test       rc=0 validation passed, no deploy
错误40位 SHA / L1 test   rc=66 commit missing
正确 SHA / L2 test       rc=64 rejected
正确 SHA / production    rc=64 rejected
release 原地写入          rc=2 Operation not permitted
```

未调用 `deploy-staging`。此前 N2-B 对 branch、tag、短 SHA、额外参数、自由文本与锁竞争的拒绝规则仍保留；本次没有放宽。

## 宿主回归检查

- Docker：2 containers、4 networks、0 volumes，与 N2-B 相同；没有 L1 Docker 名称。
- PostgreSQL：无 `5432/54329` 新监听。
- 新 release entry listeners：0；未新增端口。
- Qdrant：exited、restart=no。
- `jason-vm`：running。
- SSH、Docker、libvirt、cloudflared、Syncthing、OpenClaw gateway：active。
- systemd failed units 仍为 N0 已知的 2 个 transient 交易单元，没有新增失败单元。
- L2 paths：0。
- baseline timer：active；检查时已有 76 个样本，未等待完成。

## 实际变更命令

```text
git rev-parse/cat-file/fsck/ls-tree/worktree add/status/diff/worktree remove/prune
sha256sum（3份 evidence、manifest、release evidence、入口）
apply_patch 创建 approved manifest并修改固定入口的纯验证逻辑
chown/chmod manifest
/usr/local/sbin/test-staging FULL_SHA L1
git archive --format=tar FULL_SHA | tar -xf - -C <same-filesystem-temp>
逐文件 git hash-object 对照 tree blob
chmod/chown release；mv 临时目录到 full-SHA 目录
chattr -R +i 精确 release
runuser value-research 写入负向测试
deployment-status 与错误SHA/L2/production负向测试
```

只读回归命令包括 `docker ps/network/volume/inspect`、`virsh domstate`、`systemctl is-active/--failed`、`ss`、`find`、`stat`、`lsattr`。

## 回滚方法（未执行）

1. 确认没有 N3/Docker/deploy 使用该 release。
2. 精确执行 `chattr -R -i` 解除该 full-SHA release 的 immutable 属性。
3. 将 release 移到 root-only quarantine；核对后删除必须另获批准，不能直接覆盖或递归处理 releases 根目录。
4. 移走该 SHA 的 approved manifest；保留本报告和哈希审计记录。
5. 将固定入口恢复为 N2-B 的 test handler disabled 逻辑；deploy/rollback 当前本就保持 disabled。

## 停止点

D3-GIT-04 到此停止。当前 release 仅为已验证只读源码树；不表示 staging 已部署。等待下一次人工批准后才能进入任何 Docker/PostgreSQL/network/volume 操作。
