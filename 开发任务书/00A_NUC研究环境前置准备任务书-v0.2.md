---
title: NUC研究环境前置准备任务书
version: v0.2
status: N0已完成；N1待执行；与第一层L1.0—L1.6并行，L1.7前必须完成
risk_grade: D3
date: 2026-08-29
handoff_gate: NUC-PRE
deployment_decision: Docker-first, VM-optional
supersedes: 00A_NUC研究环境前置准备任务书-v0.1.md
---

# NUC研究环境前置准备任务书

## 1. 目标与架构裁决

在不影响NUC现有OpenClaw、Syncthing、cloudflared、sing-box、Docker、`jason-vm`及交易自动化的前提下，直接在NUC宿主的Docker环境中建立隔离、可审计、可回滚的价值投资研究staging环境，为第一层L1.7部署做好准备。

本版本作出以下裁决：

- MVP默认直接使用宿主Docker，不创建 `value-research-vm`；
- 第一层与第二层是独立应用，使用不同Compose项目、网络、数据库和卷；
- 第三层继续运行在Mac，只向NUC提交受控任务或读取发布快照；
- PostgreSQL、任务状态、热数据和运行缓存放NUC本地NVMe；
- 大型原始文件、Parquet冷数据、备份和历史归档可存放NAS；
- VM保留为后备隔离路线，只有满足§12触发条件并另行批准D3任务书时才启用。

本任务不部署第一层或第二层production实例，只准备Docker staging环境。

## 2. 执行原则

- N0只读核查可以由OpenClaw自动完成；本版本承接已经落盘的 `nuc_preflight_inventory_redacted.md`；
- N1只生成Docker部署、维护和回滚计划，不修改系统；
- N2及以后涉及软件升级、用户、权限、目录、Docker网络、挂载和服务配置，均为D3，必须逐项人工批准；
- 每个修改项单独执行、验证并记录，不把升级、网络、目录和部署合并成一个不可回滚脚本；
- 保留本地控制台或第二SSH会话，防止网络或Docker维护造成远程失联；
- 不读取、移动、复制或测试任何交易密钥；
- 不修改或停止 `jason-vm` 和现有自动化，除非另有明确授权；
- 现有Syncthing和OpenClaw以root体系运行，作为用户已接受风险记录，不在MVP中强制迁移；
- 若研究系统不经cloudflared对外发布，Cloudflare Access完整核验不作为MVP阻塞项；
- 不以企业级安全加固为目标，但必须保护研究数据完整性、部署可复现性和同机既有服务的可用性；
- 不创建自动交易、券商接口或研究应用production实例。

## 3. 受保护项与最低硬边界

### 3.1 受保护项

```text
现有BTC、Polymarket、Deribit及其他交易任务
jason-vm及其桥接网络
OpenClaw生产配置和凭据
Syncthing现有同步库
cloudflared现有隧道
sing-box配置
NAS既有数据
SSH当前可用登录路径
现有Docker容器和镜像依赖
```

任何步骤可能影响上述对象时，停止并提交影响说明。

### 3.2 最低硬边界

以下边界不得以“私人设备”或“研究用途”为由取消：

- 研究容器不得挂载交易目录、交易密钥、OpenClaw私有目录或Docker socket；
- 不使用 `privileged`、`network_mode: host`、宿主PID/IPC命名空间；
- PostgreSQL、Qdrant和内部任务API不得直接暴露到LAN或公网；
- staging与production使用不同Compose项目、网络、数据库、卷、目录和凭据；
- 部署必须绑定完整Git commit SHA或镜像digest；
- 数据库备份恢复和大型归档文件校验必须实际通过；
- 未知路径、未知release、错误哈希和错误目标必须拒绝；
- 不得让研究部署影响 `jason-vm`、交易任务或NUC现有远程访问路径。

## 4. N0：只读现状核查

N0已经完成，交付文件为 `nuc_preflight_inventory_redacted.md`。N0确认：

- 宿主CPU、内存和NVMe空间足以运行Docker研究staging；
- 现有 `jason-vm` 为2 vCPU、4 GiB内存，使用 `br0` 桥接网络；
- Docker已经运行，现有容器和网络必须保留；
- 宿主采样load average约9—11，但瞬时进程与VM采样不能完整解释；
- 宿主缺少可直接读取netfilter规则的用户态工具；
- NAS通过CIFS `soft` 挂载，不适合承载数据库活动文件；
- OpenClaw与Syncthing现有root运行方式由用户接受，不作为本期迁移目标；
- Cloudflare Access策略尚未验证，仅在研究服务计划通过现有隧道发布时升级为阻塞项。

N0状态为“有条件通过”：允许启动N1计划，不授权任何系统变更。

## 5. N1：Docker变更与回滚计划

基于N0生成以下只读计划制品：

- 现有服务、容器、端口、桥接网络、Docker网络和数据流图；
- 识别Node `3789`、失败systemd单元、失败OpenClaw cron和SSH转发冲突的归属；
- 读取并记录停止状态Qdrant的restart policy、bind mount、依赖和废弃判定，不删除；
- Docker与libvirt/netfilter兼容性检查方案，重点防止Docker变更影响 `br0` 和 `jason-vm`；
- 24小时轻量CPU/load/I/O观测方案，以及第一周低并发运行计划；
- 软件升级批次、服务影响、验证和回滚步骤；
- Docker研究目录、运行身份、Compose项目和资源预算；
- Git远端、deploy key、release目录和固定部署入口；
- 本地NVMe热数据、NAS冷归档和备份恢复设计；
- staging与production隔离设计；
- 每个D3变更的前置检查、执行、验证和恢复步骤；
- 明确接受、延期和关闭的风险，不以未闭环风险自动阻塞全部工程。

人工批准N1中的具体变更卡后，才能逐项执行N2—N6。批准N1不等于一次性授权所有宿主修改。

## 6. N2：最低宿主维护基线

按独立变更卡分项执行：

1. 备份SSH、OpenClaw、Syncthing、cloudflared、sing-box、Docker、libvirt和网络配置；
2. 验证SSH密钥登录、本地控制台或第二管理路径可用；
3. 确认Docker、libvirt与实际netfilter backend，验证Docker重启不会切断 `jason-vm` 桥接网络；
4. 识别高负载、未知监听、失败单元和失败cron的归属；只处理确认会影响研究系统或持续消耗资源的项目；
5. 经依赖核验后，将废弃Qdrant标记为retired；删除容器另行批准，不作为staging阻塞项；
6. 安排软件升级维护窗口。允许按“用户态组件”和“内核/微码/Docker/cloudflared＋重启”两个批次执行；
7. 建立约24小时轻量负载观测。七天历史不再是创建staging环境的硬门槛；
8. 创建研究专用目录和必要的运行/部署身份，不改变现有root服务身份；
9. 确认Fail2ban、auditd、TRIM和时间同步保持正常；
10. zram、SMART工具、磁盘加密、UPS和企业级异地备份作为增强项记录，不作为当前MVP硬门槛。

若研究系统不通过cloudflared发布，不新增或修改tunnel。若未来需要远程Web入口，必须先新增独立的Access与应用鉴权变更卡。

每项操作前后保存差异和验证结果。涉及Docker、网络或SSH时，必须验证 `jason-vm`、OpenClaw、Syncthing和既有交易任务仍正常。

## 7. N3：宿主Docker研究staging环境

### 7.1 目录

建议宿主目录：

```text
/srv/value-investing/
  releases/<full_commit_sha>/
  current-staging -> releases/<full_commit_sha>/
  config/staging/
  secrets/staging/
  data/l1/
  data/l2/
  objects/sha256/
  parquet/
  exports/
  cache/
  backups/
  logs/
```

production目录可以预留，但不得在本任务中部署production服务。密钥目录不得进入Git、Syncthing、镜像或日志。

### 7.2 Compose边界

```text
第一层staging：value-investing-l1-staging
第二层staging：value-investing-l2-staging
production：独立项目名、网络、数据库和卷；本任务不启动
```

- 第一层和第二层通过版本化 `candidate_manifest` 交接，不直接共享内部数据库表；
- 每个项目使用独立Compose network、PostgreSQL实例或明确隔离的数据域及独立volume；
- PostgreSQL默认只存在于Compose内网；确需宿主诊断时只绑定 `127.0.0.1`；
- 容器不得绑定未审批的宿主端口；
- 容器不得访问 `/root/.openclaw`、交易目录、`/var/run/docker.sock` 或整个 `/mnt/nas`；
- 只有归档任务可以按需挂载NAS上的研究专用目录；
- 镜像固定版本或digest，禁止长期使用漂移的 `latest`；
- 服务必须有healthcheck、结构化日志、正常停止超时和明确restart policy。

### 7.3 初始资源预算

NUC研究系统初始总预算：

```text
CPU：最多4个逻辑CPU的并发预算
内存：16 GiB目标预算，硬上限不超过24 GiB
第一层任务并发：1
第二层公司分析并发：1—2
PostgreSQL、热数据和缓存：本地NVMe
大型冷数据和归档：NAS研究专用目录
```

Docker资源限制写入Compose或运行配置，不能只写在文档中。第一周低并发运行并记录CPU、内存、I/O、温度和对既有服务的影响；根据证据调整，不因初始load未知而阻塞空环境创建。

## 8. N4：Git与固定部署身份

在以下方案中选择一个：

- 私有GitHub/GitLab：Mac推送，NUC部署身份使用只读deploy key拉取；
- NUC bare Git仓库：独立Git用户接收Mac推送，部署身份只读获取；
- 自建Gitea：仅在愿意承担额外服务维护时使用。

必须实现：

- Git远端、bare仓库和工作树均不位于Syncthing目录；
- 部署使用完整commit SHA；
- Mac构建结果不直接复制覆盖NUC当前运行目录；
- NUC按指定提交构建 `linux/amd64` 镜像，或按固定digest拉取；
- release目录不可原地修改，通过受控链接或release指针切换；
- OpenClaw只能调用固定入口：

```text
deploy-staging RELEASE_ID LAYER
test-staging RELEASE_ID LAYER
rollback-staging RELEASE_ID LAYER
deployment-status RELEASE_ID LAYER
archive-research-data ARCHIVE_MANIFEST_ID
```

- 固定入口校验release manifest、目标环境、层级、测试报告哈希和审计状态；
- OpenClaw不能把自由文本拼接进shell；
- 同一Compose项目同一时间只有一个部署租约；
- 部署流程不得读取交易密钥或修改NUC宿主SSH、网络、防火墙和libvirt配置；
- 不向部署容器或研究容器挂载Docker socket。

现有OpenClaw以root运行属于已接受现状，但这不授权研究任务执行任意宿主命令。固定入口用于保证发布可复现和防止误操作，而非追求企业级权限模型。

## 9. N5：本地存储、NAS归档和备份

### 9.1 本地NVMe热数据

以下内容保存在NUC本地：

```text
PostgreSQL数据目录与WAL
任务队列、租约、锁和运行状态
当前使用的对象和Parquet工作集
模型与API运行缓存
当前release和最近回滚release
最近一次可用数据库逻辑备份
```

### 9.2 NAS冷数据与备份

NAS只使用研究专用目录，适合保存：

- SEC原始财报和其他可重新验证的大型原始文件；
- 历史行情、Parquet冷分区和长期回放数据；
- 发布报告、对象清单和长期审计制品；
- 数据库逻辑备份和配置备份；
- 已退出本地工作集的历史release制品。

大型文件归档采用：

```text
写入临时文件
→ 计算并核对SHA-256与大小
→ 原子重命名或发布完成标记
→ 记录archive manifest
→ 校验通过后才能按保留策略删除本地源文件
```

因当前CIFS使用 `soft`，数据库、WAL、锁、容器卷和事务性工作目录不得放在NAS。写入失败必须可重试，不能把部分文件标记为归档成功。

MVP不要求立即建立企业级不可变或异地备份，但必须完成：

- Git代码存在NUC之外的副本；
- 一次数据库逻辑备份和恢复；
- 一次大型归档文件复制、校验和恢复；
- 明确保留周期、NAS 80%容量预警和失败告警；
- 明确哪些原始数据可重新下载，哪些数据不可再获取。

Syncthing只同步发布目录中的Markdown、JSON、CSV、图表和SHA-256清单，不同步数据库、对象工作集、Parquet工作集、WAL、锁、缓存、密钥和容器卷。

## 10. N6：Docker staging空环境验收

在尚未部署第一层业务功能时验证：

- 宿主重启或Docker重启后，现有服务和 `jason-vm` 保持正常；
- 两个staging Compose空骨架可分别启动、停止和重启；
- Compose项目、网络、数据库、卷和目录互相隔离；
- PostgreSQL、Qdrant和内部API没有LAN或公网监听；
- Mac/OpenClaw可以用固定部署身份提交受控部署动作；
- 未知release、错误哈希、错误层级和错误目标被拒绝；
- staging可以拉取测试提交并构建 `linux/amd64` 镜像；
- 健康检查失败可以回滚到前一个release；
- 数据库备份和恢复通过；
- NAS研究专用目录归档、校验和恢复通过；
- 研究容器无法读取交易目录、OpenClaw私有目录和Docker socket；
- CPU、内存、I/O和温度在设定预算内；
- `jason-vm`、OpenClaw、Syncthing、cloudflared、sing-box和交易任务无可归因于本次变更的异常；
- Syncthing没有新增数据库、WAL、锁、密钥或容器卷同步项。

## 11. NUC-PRE验收制品

```text
nuc_preflight_inventory_redacted.md
nuc_docker_change_plan.md
nuc_network_and_port_map.md
nuc_netfilter_and_bridge_compatibility.md
nuc_upgrade_and_reboot_report.md（如本期实际执行升级）
docker_host_staging_spec.json
docker_resource_baseline.md
git_and_deploy_identity.md
staging_environment_test_report.md
backup_restore_test_report.md
protected_services_unchanged_report.md
accepted_and_deferred_risks.md
NUC_PRE_acceptance.md
```

`NUC_PRE_acceptance.md`必须明确：

- 哪些配置实际改变；
- 哪些前置项未完成、延期或由用户接受风险；
- SSH和回滚路径；
- Docker Compose项目、资源预算、网络、端口和卷；
- Git远端、release和部署身份；
- staging与production隔离；
- 本地NVMe与NAS的数据边界；
- 备份、归档校验和恢复结果；
- 现有VM、交易和其他服务是否保持不变；
- 是否允许启动第一层L1.7 Docker staging部署。

人工确认NUC-PRE后，第一层才可执行L1.7。该确认不授权production部署。

## 12. VM后备路线触发条件

Docker-first不是永久禁止VM。出现以下任一情况时，暂停扩容并提交独立D3 VM方案：

- OpenClaw或模型需要持续执行未经审计的任意代码；
- 系统新增公网上传、第三方插件或不可信二进制执行能力；
- Docker资源竞争持续影响 `jason-vm`、交易任务或宿主稳定性；
- 需要与宿主不同的内核、系统库或升级周期；
- 需要整机快照、快速迁移或比容器更强的故障隔离；
- 经实际事件证明现有容器边界不足。

触发条件成立不等于自动创建VM。必须另行确定VM资源、网络、存储、迁移、回滚和对 `br0` 的影响，并获得人工批准。

## 13. 本次v0.2变更日志

- 默认运行载体由独立 `value-research-vm` 改为NUC宿主Docker；
- VM从强制前置改为条件触发的后备路线；
- 现有OpenClaw和Syncthing root运行方式记录为用户接受风险，不要求MVP迁移；
- Cloudflare Access核验改为仅在研究服务使用隧道发布时的硬门槛；
- 七天负载历史改为约24小时观测加第一周低并发运行，不阻塞空环境创建；
- 第一、二层使用独立Compose项目、网络、数据库和卷；
- 热数据固定在NUC本地NVMe，大型冷数据和备份允许归档NAS；
- 增加CIFS `soft` 场景下的临时文件、SHA-256校验和完成标记要求；
- 保留数据库不外露、禁止特权容器、禁止Docker socket、禁止挂载交易目录等最低硬边界；
- 重写N3—N6和NUC-PRE制品，使验收对象从研究VM变为宿主Docker staging。
