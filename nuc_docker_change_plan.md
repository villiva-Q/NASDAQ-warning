---
title: NUC Docker-first N1 变更与回滚计划
status: draft
risk_grade: D3
date: 2026-08-29
scope: N1 plan only
---

# NUC Docker-first N1 变更与回滚计划

## 边界与只读复核结论

本文件只提出 N2—N6 的候选命令，不授权执行。默认架构为宿主 Docker-first、VM-optional；不创建研究 VM，不改 `jason-vm`、交易自动化或现有远程访问。

- `*:3789`：`opennews-web.service`，root，enabled，`Restart=always`，工作目录位于 OpenClaw workspace，读取独立 `.env`；现有业务，受保护。
- 失败 systemd 单元：均为 `/run/systemd/transient` 下的交易自动化 one-shot。`...exec` 返回 3 表示订单已最终化且不重试；`...normal-skip-watch` 返回 2 表示跳过状态未获确认而告警。不是研究环境服务。
- 四个失败 OpenClaw cron：均在 cron preflight 被当前模型 allowlist 拒绝，业务 payload 未运行；不应为研究 staging 擅自修改。
- SSH `12345`：现有 root SSH session 已占用 loopback 端口约 9 天；另一个半小时重连任务持续请求同一端口。归属仍需用户确认远端发起端，不能直接终止 session。
- Qdrant：停止；`restart=no`；默认 Docker bridge；宿主 `6333` 配置为全接口发布但当前未监听；唯一 bind mount 为本地 `/root/qdrant_data` 到容器存储；无 links、volumes-from 或 Compose/依赖 labels；镜像声明 v1.17.0。删除不是 staging 前置。
- netfilter：`iptables` 使用 nft backend；UFW、Docker、Tailscale 共享 nftables 规则集，IPv4/IPv6 INPUT 与 FORWARD 基础策略为 drop。Docker 建有 `DOCKER*` chains并启用 IPv4 forwarding。
- `br_netfilter` 当前未加载，`br0` 的 `nf_call_iptables/ip6tables/arptables` 均为 0；物理 NIC 和 `jason-vm` 的 `vnet1` 直接挂到 `br0`。因此当前 Docker bridge 过滤与 `br0` 二层转发相对解耦；任何 Docker/netfilter 重启或模块加载仍须做 `jason-vm` 连通性前后对照。

## D3-N2-01 受保护配置快照与管理路径验证

- 目的：在任何宿主变更前建立只读基线、可审计差异和恢复材料。
- 依赖：用户指定维护窗口；确认本地控制台或第二 SSH 会话可用；确认备份目的地和保留期。
- 影响对象：SSH、Docker、libvirt、br0、OpenClaw、Syncthing、cloudflared、sing-box 的配置副本；不修改源配置。
- 前置检查：目标目录不在 Syncthing；可用空间足够；备份不包含私钥、token 或 API key，或使用批准的加密容器。
- 拟执行命令（提案，未执行）：`install -d -m 0700 /srv/value-investing/admin-snapshots/<timestamp>`；使用 `cp --archive`/`systemctl cat`/`docker inspect`/`virsh dumpxml` 分项导出；`sha256sum` 生成清单。
- 验证：清单可读；敏感文件权限 0600；抽样恢复到临时离线位置并比较哈希；SSH 第二路径保持在线。
- 回滚：删除本次新建的快照目录；源配置未改变，无服务回滚。
- 停止条件：缺少第二管理路径、快照包含未获批准的秘密、目标路径落入同步目录、NAS 不稳定。
- 所需人工批准：批准快照范围、存放位置、加密/保留策略和维护时间。

## D3-N2-02 归属确认与故障噪声处置

- 目的：只处理会影响 staging 或持续浪费资源的已确认故障，不触碰交易语义。
- 依赖：交易任务 owner 对两个 transient 单元退出码作书面确认；OpenClaw cron owner 选择允许模型或停用；SSH 客户端 owner 确认 `12345` 用途。
- 影响对象：两个 failed transient units、四个 OpenClaw cron、一个长期 SSH session/半小时重连任务。
- 前置检查：再次读取最新状态和最近三次运行；确认没有订单执行中、归档任务进行中或唯一管理链依赖该 tunnel。
- 拟执行命令（提案，未执行）：对确认是终态的 transient unit 使用 `systemctl reset-failed <exact-unit>`；对每个 cron 单独 `openclaw cron edit <id> ...` 或 `disable`；对 SSH 冲突从发起端调整唯一 local-forward 端口并优雅结束旧 session。
- 验证：交易结果哈希/终态不变；cron 下一次 dry-run/单次批准运行成功；`12345` 只由一个预期进程监听且不再出现冲突日志。
- 回滚：恢复原 cron 声明；恢复原 SSH forward 配置并重新建立旧链路；failed 标记本身无需恢复。
- 停止条件：任何交易状态不明确、cron 修改会改变业务行为、SSH 链路是唯一管理路径、owner 未确认。
- 所需人工批准：每个 unit/cron/SSH forward 分别批准；不得打包授权。

## D3-N2-03 约 24 小时轻量资源基线

- 目的：解释 load 与 I/O，确定 4 CPU/16 GiB 初始预算不会伤害既有服务。
- 依赖：选择无需安装新包的观测脚本；采样输出放本地 NVMe，禁止写 NAS 测试文件。
- 影响对象：只新增小型日志/报告；预计开销极低。
- 前置检查：脚本仅调用 `/proc`、`ps`、`docker stats --no-stream`、`virsh domstats`、`df`、温度 sysfs；间隔至少 60 秒。
- 拟执行命令（提案，未执行）：创建受限 systemd timer 或 `systemd-run` 采样任务；输出到 `/srv/value-investing/baseline/`；24 小时后生成峰值/P95。
- 验证：采样连续、无秘密、总开销和文件大小在批准阈值内；记录 CPU/load/memory/I/O/温度及 `jason-vm` 状态。
- 回滚：停用并删除本次 timer/service 与日志；保留已批准的最终摘要。
- 停止条件：采样本身 CPU 持续超过 1%、磁盘异常增长、load/温度/既有服务明显恶化。
- 所需人工批准：批准脚本、频率、路径、保留期。七天历史不是阻塞项。

## D3-N2-04 用户态安全更新批次

- 目的：先更新低耦合用户态安全组件，降低一次性维护风险。
- 依赖：D3-N2-01；锁定准确包清单；排除 Docker、containerd、cloudflared、kernel、microcode、SSH（若远程链路风险未解决）。
- 影响对象：批准清单内的软件包；可能触发库使用进程需后续重启。
- 前置检查：`apt-get --simulate upgrade <packages>`；保存版本、依赖和磁盘空间；确认交易窗口为空。
- 拟执行命令（提案，未执行）：`apt-get update`；`apt-get install --only-upgrade <approved-userland-packages>`；不得使用无清单的全量 upgrade。
- 验证：`dpkg --audit`、关键服务健康、SSH/OpenClaw/Syncthing/交易任务/VM 状态和监听基线一致。
- 回滚：按快照记录回装上一版本；若仓库不保留旧包则使用预下载缓存；必要时恢复配置。
- 停止条件：模拟将删除包、改变网络栈、触发未计划服务重启、旧包不可获得、验证失败。
- 所需人工批准：最终包名/版本清单和窗口。

## D3-N2-05 内核、微码、Docker、cloudflared 与计划重启批次

- 目的：处理高耦合更新，并以 `jason-vm`/br0 可靠性为硬验收。
- 依赖：D3-N2-01、N2-03；本地控制台；明确停机窗口；Qdrant 保持停止；交易任务暂停窗口需单独批准。
- 影响对象：宿主内核、微码、Docker/containerd、cloudflared、所有容器连接、nftables/bridge 行为、宿主重启。
- 前置检查：锁定版本；导出 nftables 摘要、Docker networks、`br0`/`vnet1`、VM 和端口基线；准备上一内核启动项。
- 拟执行命令（提案，未执行）：只升级批准的精确包；按序验证 Docker/cloudflared；最后由人工执行一次计划重启。
- 验证：启动到目标内核；Docker/UFW/Tailscale chains 存在；`br_netfilter` 与 bridge sysctl 未发生未批准漂移；`jason-vm` LAN 连通、无 drop；既有容器与全部受保护服务正常。
- 回滚：从上一内核启动；回装上一 Docker/cloudflared；恢复 nftables/config 快照；不得通过重置 br0 试错。
- 停止条件：无控制台、上一内核不可用、Docker 模拟迁移数据格式不可逆、VM 连通性下降、SSH/tunnel 中断。
- 所需人工批准：包清单、服务重启顺序、宿主重启和回滚负责人分别批准。

## D3-N2-06 研究目录与非交互部署身份

- 目的：建立与 OpenClaw/交易目录隔离的宿主边界。
- 依赖：Git 方案已选；UID/GID、目录树、secret provider 已批准。
- 影响对象：新增专用用户/组、`/srv/value-investing` 目录和最小权限。
- 前置检查：名称/UID 不冲突；路径不在 Syncthing；不继承 `/root` 或交易目录权限。
- 拟执行命令（提案，未执行）：`useradd --system ...`、`install -d -o <user> -g <group> -m <mode> ...`；禁止加入 `docker` 组，部署动作通过固定受控入口完成。
- 验证：专用身份不能读取 `/root/.openclaw`、交易目录、Docker socket；应用目录可按职责读写；secrets 0700/0600。
- 回滚：删除仅本卡创建且为空的目录/身份；保留审计清单；若已有数据则先人工迁移批准。
- 停止条件：权限测试可读受保护路径、需要 docker 组/任意 sudo、目录与现有项目冲突。
- 所需人工批准：用户名、UID/GID、目录所有权、sudo/fixed-entry 设计。

## D3-N3-01 Compose 网络、卷与空骨架

- 目的：创建 L1/L2 完全独立的 staging 空环境，不部署业务功能。
- 依赖：N2-01、N2-03、N2-06；`docker_host_staging_spec.json` 审批；N2-05 可延期，但若延期需记录版本风险。
- 影响对象：新增两个 Compose project、各自 bridge network、PostgreSQL volume/必要应用 volume；不碰现有 networks/containers。
- 前置检查：project/network/volume 名称不冲突；无 host/privileged/socket/交易挂载；端口默认不发布。
- 拟执行命令（提案，未执行）：`docker compose -p value-investing-l1-staging config --quiet`；同理 L2；批准后 `up -d` 空骨架。
- 验证：两个项目互不可见；数据库与内部 API 仅 Compose 内网；资源总限制不超过 4 CPU、16 GiB 目标、24 GiB 硬上限；`jason-vm`/br0 与既有服务前后无变化。
- 回滚：按 project 精确 `docker compose ... down`；默认保留数据卷，删除卷须另卡批准。
- 停止条件：Compose 解析出 host network、privileged、Docker socket、LAN 端口、未固定镜像或跨项目共享数据库/卷。
- 所需人工批准：两个项目分别批准；网络/卷创建清单逐项批准。

## D3-N3-02 第一层 staging 最小部署

- 目的：按第一层并发 1 部署 L1 staging，不部署 production。
- 依赖：N3-01、N4-01；完整 commit SHA、测试报告哈希、候选 manifest schema。
- 影响对象：仅 `value-investing-l1-staging` 的容器/网络/卷和本地 NVMe L1 数据。
- 前置检查：镜像 tag/digest 固定；CPU/memory/pids/healthcheck/restart policy 完整；不挂 NAS，除独立归档 job 经批准只访问研究子目录。
- 拟执行命令（提案，未执行）：固定入口 `deploy-staging <full_sha> L1`，内部仅允许 `docker compose -p value-investing-l1-staging ...`。
- 验证：并发=1；无 LAN/public 监听；健康检查通过；candidate manifest 版本化；预算和受保护服务正常。
- 回滚：`rollback-staging <previous_full_sha> L1`；数据库 schema 变更必须有向后兼容/恢复点。
- 停止条件：未知 SHA、healthcheck 失败、资源越限、受保护服务异常、需访问交易或 OpenClaw 目录。
- 所需人工批准：release SHA、镜像 digest、迁移计划和第一次部署窗口。

## D3-N3-03 第二层 staging 最小部署

- 目的：按公司分析并发 1 起步、最多 2，部署独立 L2 staging。
- 依赖：N3-01、N4-01；只通过版本化 candidate manifest 接收 L1 输入。
- 影响对象：仅 `value-investing-l2-staging` 的容器/网络/卷和本地 NVMe L2 数据。
- 前置检查：不得直连 L1 数据库；独立 PostgreSQL/Qdrant 数据域；内部服务不发布 LAN 端口。
- 拟执行命令（提案，未执行）：固定入口 `deploy-staging <full_sha> L2`。
- 验证：默认并发=1，证据允许后才升到 2；L1 停止不破坏 L2 数据一致性；资源总预算合规。
- 回滚：`rollback-staging <previous_full_sha> L2`；恢复独立数据库备份。
- 停止条件：跨层共享数据库表/卷、Qdrant/API 向 LAN 发布、总预算越限、`jason-vm` 或交易任务受影响。
- 所需人工批准：release、并发从 1 到 2、数据库/Qdrant 版本分别批准。

## D3-N4-01 Git 远端、release 与固定部署入口

- 目的：实现完整 SHA、不可原地修改 release 和可回滚部署。
- 依赖：在私有 Git 远端与 NUC bare Git 中做出决策；N2-06。
- 影响对象：新增 Git remote/仓库、只读部署身份、release 目录和固定入口；本轮均未创建。
- 前置检查：仓库不在 Syncthing；deploy identity 无 shell 或最小 shell；入口拒绝自由文本、错误层级和未知目标。
- 拟执行命令（提案，未执行）：创建远端/只读 key 或 bare repo；`git fetch`；`git cat-file -e <full_sha>^{commit}`；创建新 release；原子切换 `current-staging`。
- 验证：只能部署完整 SHA；构建为 linux/amd64；同 project 单租约；旧 release 可一键切回；日志不含秘密。
- 回滚：撤销 current-staging 指针、恢复上一 Compose release；吊销本次 key；保留审计记录。
- 停止条件：必须给 OpenClaw 任意 shell、仓库/工作树位于同步目录、使用 branch/latest 作为唯一标识、key 有写权限却无业务需要。
- 所需人工批准：Git 方案、remote、部署身份、key 权限、固定入口实现。

## D3-N5-01 本地数据库备份恢复

- 目的：证明 PostgreSQL 逻辑备份可恢复，不依赖 NAS 活动存储。
- 依赖：N3 空骨架；独立临时恢复数据库/volume；测试数据集。
- 影响对象：staging 数据库和新增备份文件；不碰 production/交易数据库。
- 前置检查：备份目标在本地 NVMe；版本兼容；可用空间；凭据不出日志。
- 拟执行命令（提案，未执行）：容器内 `pg_dump` 到本地受限目录；计算 SHA-256；恢复到独立临时实例；执行一致性查询。
- 验证：schema/行数/关键校验一致；记录 RPO/RTO、工具版本、哈希。
- 回滚：删除独立临时恢复实例；保留经批准的最近一次可用备份。
- 停止条件：备份写到 NAS、恢复覆盖原库、凭据出现在命令行/日志、哈希不一致。
- 所需人工批准：测试库、备份路径、保留期、临时 volume 删除。

## D3-N5-02 NAS 冷归档与恢复演练

- 目的：验证大型冷文件的临时写入、哈希、完成标记和恢复流程。
- 依赖：NAS 研究专用目录与 ACL 已批准；容量告警阈值 80%；准备非敏感测试制品。
- 影响对象：仅批准的 NAS 研究子目录；不挂整个 `/mnt/nas` 给常驻容器。
- 前置检查：CIFS 在线；不使用数据库/WAL/锁；测试对象可删除；明确重试语义。
- 拟执行命令（提案，未执行）：写 `.partial`、`sha256sum`、核对大小、同目录原子改名/完成标记、manifest；从 NAS 恢复到本地临时路径并复核。
- 验证：源/归档/恢复哈希一致；中断不会生成成功标记；达到 80% 有告警。
- 回滚：删除本卡测试制品和 manifest（需单独批准）；不删除任何既有 NAS 文件。
- 停止条件：NAS 抖动、非研究目录、哈希/大小不一致、必须挂整个 NAS、容量超过阈值。
- 所需人工批准：NAS 子目录、ACL、测试文件、清理动作和保留策略。

## D3-N6-01 Docker staging 空环境验收

- 目的：证明 N3 空环境隔离、可回滚且不影响受保护服务。
- 依赖：N3-01、N4-01、N5-01、N5-02；验收清单与维护窗口。
- 影响对象：两个 staging project；可能包含经批准的 Docker 重启测试，宿主重启另行批准。
- 前置检查：保存端口、nftables、Docker networks、br0/vnet1、VM/交易/OpenClaw 状态基线；本地控制台可用。
- 拟执行命令（提案，未执行）：逐项目 start/stop/restart；固定入口负向测试；备份恢复；若单独批准，再测试 Docker restart 和宿主 reboot。
- 验证：项目/网络/DB/卷隔离；无 LAN/public DB/Qdrant/API；拒绝错误 release；资源预算合规；`jason-vm`、交易任务和全部受保护服务无回归。
- 回滚：逐项目回到上一 release 或 down；恢复配置快照；必要时上一内核启动；不得修改 br0 试错。
- 停止条件：任何受保护服务异常、管理路径不稳定、数据恢复失败、端口意外暴露、netfilter/bridge 漂移。
- 所需人工批准：每个测试步骤；Docker restart 与宿主 reboot 必须独立明确批准。

## N2 前真正硬门槛

- 用户逐卡批准；第二管理路径；受保护配置基线；确认 `jason-vm`/br0 前后验证方法。
- N3 前还必须完成：研究目录/身份设计、Compose spec、Git/release 决策、24 小时观测至少启动并确认无异常；无需等待七天。
- 可延期：清理停止 Qdrant、迁移 root OpenClaw/Syncthing、Cloudflare Access（若不发布）、zram/SMART/磁盘加密/UPS/异地不可变备份、全量系统升级（须记录版本风险）。

## 2026-08-29 N2-A 后续范围修正（保留原始 N1）

本节是原始 N1 审查后的显式 amendment，不追溯改写上述计划形成时的结论：当前 NUC-PRE 只服务第一层 L1.7。L2 Compose、L2 PostgreSQL、L2 Qdrant 及 D3-N3-03 全部转为 `future/not-deployed`，不创建任何 L2 目录、网络、卷或容器。旧停止 Qdrant 不是当前依赖并继续保持停止。第二层环境须等待 H1 通过、L2 技术选型完成并取得新的 D3 批准。
