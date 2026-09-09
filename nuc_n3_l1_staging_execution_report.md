# NUC D3-N3-01 — L1 Docker staging 空环境首次部署执行报告

- 执行日期：2026-08-29（UTC）
- 结果：**成功；L1 staging PostgreSQL 保持运行且 healthy**
- 授权范围：仅 D3-N3-01、L1、staging、指定完整 SHA；未进入 N5/N6/production/L2。

## 1. 固定 release 与 Git 复验

- 完整 commit SHA：`ff2746f00ed0cb0112e09c3caa09a8354777c745`
- Git tree SHA：`3798a7b6c128cdaa5b0271e0accb68f7cde38947`
- `refs/heads/main`：精确等于上述完整 SHA。
- commit object：存在且类型正确；`git fsck --strict` 通过。
- 只读 worktree：HEAD 精确匹配、porcelain status 为空、91 个 tracked files，无未跟踪文件。
- release：`/srv/value-investing/releases/ff2746f00ed0cb0112e09c3caa09a8354777c745/`
- release 验证：91/91 文件的 Git blob 均与指定 tree 相等；无 `.git`、无额外文件；目录 `0555`、普通文件 `0444`，所有者 `value-research:value-research`。
- release 属性：递归设置 ext4 immutable（目录根属性包含 `i`），不可原地修改。
- 精确解除方法（未来独立批准后才可执行）：`chattr -R -i /srv/value-investing/releases/ff2746f00ed0cb0112e09c3caa09a8354777c745/`。

## 2. 证据与 Compose 哈希

- `docs/runbooks/L1_stageA_audit_report.md`：`d88a859f156575ce5c1347e5fe897ee90025a7ddfe075e0b3d6cff0dea481520`
- `docs/runbooks/L1_staging_implementation_summary.md`：`3eaaffc70dea6f98b256a1df1a7b19c7d3fa7340623ee1c5ef5a7824f3bcadf3`
- `docs/runbooks/L1.2_audit_report.md`：`678a5b7cfaf369d71dd84b613d5b71b260b3974cd25648e3bad9c9a24d1f654a`
- `docs/runbooks/L1.2_implementation_summary.md`：`369668857259f0dd837617eca2f9db29626c6caa3ad14120932c1308b94cf029`
- `infra/compose/docker-compose.staging.yml`：`1e96128ae7845b7e18ba7b0b53dc1465af17b8fb86e1109355c9f6eed6c679ab`
- 审计限定如实保留：两份独立审计均无阻塞项并判定通过；其会话中部分动态测试未独立复跑，而是与已哈希的实施报告进行静态交叉验证。

## 3. staging 配置与镜像

- 配置：`/etc/value-investing/staging.env`，`0600 root:root`。
- 文件只含 `POSTGRES_USER`、`POSTGRES_PASSWORD`、`POSTGRES_DB`；密码由 `openssl rand -hex 32` 随机生成。
- 配置未进入 Git、release、镜像、Syncthing 或 manifest；本报告、部署日志及终端记录均未输出密码。
- 镜像 reference：`postgres:16.4-alpine`
- registry digest：`postgres@sha256:5660c2cbfea50c7a9127d17dc4e48543eedd3d7a41a595a2dfa572471e37e64c`
- 实际 image ID：`sha256:5660c2cbfea50c7a9127d17dc4e48543eedd3d7a41a595a2dfa572471e37e64c`，与 manifest 一致。

## 4. approved manifest 与固定入口

- manifest：`/srv/value-investing/manifests/ff2746f00ed0cb0112e09c3caa09a8354777c745.approved.json`
- manifest 权限：`0640 root:value-research`
- manifest SHA-256：`595516eb45a6a88e90ea4ab28070ae0474712763805968c5af91ca2e483cce5b`
- manifest 明确绑定 full SHA、tree SHA、Compose/evidence 哈希、image digest、`layer=L1`、`environment=staging`、固定 project，并设置 `production=false`、`l2=false`。
- 固定入口：`/usr/local/sbin/value-investing-release-entry`，`0750 root:root`
- 固定入口 SHA-256：`ed38adfae27f77ab3ba177824892cf10c3a868eb477bc79190ac3ef14e6529c0`
- 入口使用固定 argv 与非阻塞部署锁，不使用 `eval`；Docker 授权只对上述完整 SHA 生效。

## 5. 部署前静态门禁

结果：**PASS**。

- Compose project 仅为 `value-investing-l1-staging`；仅有 `postgres` 与 `postgres_volume_init`。
- 无 `ports`、host network、privileged、Docker socket、NAS、Syncthing、OpenClaw 或交易目录挂载。
- PostgreSQL 配置用户为 `postgres:postgres`；初始化容器为一次性 root，`cap_drop=ALL`，仅加回 `CHOWN`、`DAC_OVERRIDE`、`FOWNER`，`restart=no`。
- 两服务均配置 CPU、内存、PID、healthcheck、json-file 日志轮换、restart policy 与 stop grace period。
- 专用 bridge network 与专用 named volume 名称正确；无 L2 或 production 对象。
- Compose 解析输出被写入 root-only 临时文件并删除，未输出环境值。

## 6. 实际部署对象与验收

- project：`value-investing-l1-staging`
- PostgreSQL container：`value-investing-l1-staging-postgres-1`，`healthy`
- 初始化 container：`value-investing-l1-staging-postgres_volume_init-1`，`exited/0`，未持续运行
- network：`value-investing-l1-staging-network`，driver=`bridge`，Compose project label 正确
- volume：`value_investing_l1_staging_postgres_data`，driver=`local`，Compose project label 正确
- network/volume 只由本项目两个容器引用；没有与原有容器共享。
- PostgreSQL 运行 UID：`70`（非 root）；Config.User=`postgres:postgres`。
- PostgreSQL：1 CPU、1 GiB、PID 128、`unless-stopped`、stop timeout 60 秒、json-file `10m × 3`、`cap_drop=ALL`。
- init：0.25 CPU、128 MiB、PID 32、`restart=no`、stop timeout 10 秒、json-file `10m × 3`。
- PostgreSQL 仅有 Docker 内部 `5432/tcp`，HostPort 为 null；宿主 `ss` 未发现 5432/54329 TCP/UDP 监听，因此 LAN 无直接数据库入口。
- `deployment-status` 返回指定 SHA、L1、staging、project 与 `healthy`。
- 本轮只启动空 PostgreSQL 和一次性初始化器；未执行 Alembic migration，未部署 worker/API/scheduler/业务任务。

## 7. 负向测试

全部按预期拒绝：

- 短 SHA、branch 名：exit 64
- `L2`、`production`：exit 64
- 额外参数：exit 64
- 不存在的完整 SHA：exit 66
- 持锁并发调用：exit 75
- 部署完成并修正 status 读取后，以上关键负向测试再次执行，仍全部拒绝。

## 8. 受保护对象前后对照

- Docker 对象计数：部署前 container/network/volume=`2/4/0`；部署后=`4/5/1`，增量严格对应本项目两个容器、一个 network、一个 volume。
- `jason-vm`：部署前后均 running。
- SSH、Docker daemon、libvirtd、cloudflared、Syncthing：部署前后均 active。
- OpenClaw Gateway：部署后核验为 active/running；未修改。
- systemd 失败单元仍为 2 个，均为既有交易相关 transient unit；未修改或重启。
- Qdrant：仍为历史停止状态 `Exited (255)`；未启动、修改或删除。
- 24 小时资源 timer：部署时已自行结束，`Result=success`；未等待其完成，也未以此阻塞 N3。
- 未修改 SSH、firewall/netfilter、cloudflared、Syncthing、sing-box、br0、libvirt、现有 Docker 服务或交易任务。

## 9. 实际执行命令族（脱敏）

- Git：`rev-parse`、`cat-file`、`fsck --strict`、`worktree add --detach`、`status --porcelain`、`ls-tree -rz`、`show`、`archive`、`hash-object`。
- 哈希/文件属性：`sha256sum`、`stat`、`find`、`chmod`、`chown`、`chattr -R +i`、`lsattr`。
- 配置：`install -d`、`mktemp`、`openssl rand -hex 32`；敏感值未回显。
- Docker 静态/镜像：`docker compose ... config --format json`、`docker pull postgres:16.4-alpine`、`docker image inspect`。
- 固定入口：`test-staging FULL_SHA L1`、`deploy-staging FULL_SHA L1`、`deployment-status FULL_SHA L1`。
- Docker 验收：`docker ps`、`docker inspect`、`docker exec <postgres> id -u`、`docker network inspect`、`docker volume inspect`。
- 宿主回归：`ss -lntup`、`systemctl is-active/list-units/list-timers/show`、`virsh domstate jason-vm`。

## 10. 异常、修正与回滚

- release 首次预校验因 Git 对非 ASCII 路径默认加引号而产生文件集假不一致；未创建 release/env/Docker 对象。改用 NUL 分隔的 `ls-tree -rz` 后，91 个 blob 全量验证通过。
- 第二次预校验因 zsh 特殊变量名覆盖命令搜索路径而提前退出；仅留下显式临时目录，清理后改用 Bash 与非保留变量名完成。未留下部分 release 或凭据文件。
- 首次 `deployment-status` 因依赖不适用的格式字段误报 `not-created`；仅修正为按固定 Compose labels 获取容器 ID 并读取 health，随后返回 healthy，且负向测试仍通过。数据库与 Docker 拓扑未因修正而改变。
- 如后续经独立人工批准回滚：对固定 project 执行 `docker compose ... down`，**不得使用 `--volumes`**；保留数据库 volume、镜像、release、manifest 和日志。若部署失败，固定入口设计为执行该无卷删除的 down 并撤销该 SHA 的 deploy flags。本次未触发失败回滚。

## 11. 停止声明

D3-N3-01 已完成并在此停止。L1 staging PostgreSQL 保持 healthy；未进入 N5、N6、L2 或 production，未创建研究 VM，未执行迁移、备份恢复或任何应用部署。等待下一次人工评审。
