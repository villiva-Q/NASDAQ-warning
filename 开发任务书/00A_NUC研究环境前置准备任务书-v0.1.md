---
title: NUC研究环境前置准备任务书
version: v0.1
status: 与第一层L1.0—L1.6并行执行；L1.7前必须完成
risk_grade: D3
date: 2026-08-29
handoff_gate: NUC-PRE
---

# NUC研究环境前置准备任务书

> **已被v0.2取代。** 后续N1—N6及NUC-PRE必须使用
> [00A_NUC研究环境前置准备任务书-v0.2.md](./00A_NUC研究环境前置准备任务书-v0.2.md)。
> 本文件仅保留为VM-first历史版本，不再作为执行依据。

## 1. 目标

在不影响NUC现有OpenClaw、Syncthing、cloudflared、sing-box、虚拟机及交易自动化的前提下，建立隔离、可审计、可回滚的价值投资研究staging环境，为第一层L1.7部署做好准备。

本任务不部署第一层应用，只准备运行环境。

## 2. 执行原则

- N0只读核查可以由OpenClaw自动完成；
- N1生成方案和回滚步骤，不修改系统；
- N2及以后涉及防火墙、软件升级、用户、VM、权限和挂载，均为D3，必须逐项人工批准；
- 每个修改项单独执行、验证并记录，不把防火墙、升级、VM和存储合并成一个不可回滚脚本；
- 保留本地控制台或第二SSH会话，防止网络调整锁死；
- 不读取、移动、复制或测试任何交易密钥；
- 不修改或停止 `jason-vm` 和现有自动化，除非另有明确授权；
- 不在本任务中创建自动交易、券商接口或研究应用生产实例。

## 3. 受保护项

```text
现有BTC、Polymarket、Deribit及其他交易任务
jason-vm
OpenClaw生产配置和凭据
Syncthing现有同步库
cloudflared现有隧道
sing-box配置
NAS既有数据
SSH当前可用登录路径
```

任何步骤可能影响上述对象时，停止并提交影响说明。

## 4. N0：只读现状核查

只读采集并脱敏输出：

- CPU、内存、磁盘、温度和近7天负载；
- `jason-vm` 的vCPU、内存、磁盘、网络和实时占用；
- Docker容器、网络、卷和资源使用；
- systemd服务和失败单元；
- 所有TCP/UDP监听及绑定接口；
- nftables/iptables状态；
- SSH有效配置、登录方式和监听；
- cloudflared tunnel、published routes和Access策略引用；
- Syncthing GUI/API和同步端口绑定；
- NAS挂载、剩余空间、快照和权限；
- OpenClaw服务用户、工作目录、systemd路径和失败cron；
- 可升级软件包、保留包和重启需求；
- zram/swap、SSD TRIM和SMART摘要；
- 研究VM可用的私有网段和存储池。

禁止在报告中输出：私钥、token、完整API key、Cookie、密码、Syncthing API key或Cloudflare tunnel token。

交付：`nuc_preflight_inventory_redacted.md` 和原始命令清单。

## 5. N1：变更与回滚计划

基于N0生成：

- 端口和数据流图；
- 防火墙拟议规则，不立即加载；
- 软件升级批次、服务影响和回滚；
- 研究VM资源分配；
- Git远端与部署身份设计；
- NAS专用目录、配额和备份；
- staging/prod网络和数据隔离；
- 每个D3变更的前置检查、执行、验证和恢复步骤。

人工批准N1后才能执行N2—N6。

## 6. N2：安全与维护基线

分项执行：

1. 备份SSH、OpenClaw、Syncthing、cloudflared、sing-box、Docker和libvirt配置；
2. 验证SSH密钥登录和本地控制台恢复；
3. 建立nftables默认拒绝入站方案，只放行已核验服务；
4. 核对cloudflared published routes和Access策略；
5. 确认Syncthing GUI/API保持loopback并有认证；
6. 安排155个待升级包的维护窗口和重启；
7. 修复或隔离连续失败cron；
8. 记录83°C传感器来源并完成受控负载温度测试；
9. 配置8—16 GiB zram作为OOM保护；
10. 确认Fail2ban、auditd、TRIM和时间同步正常。

每项操作前后保存差异和验证结果。防火墙加载后必须从第二会话验证SSH，再关闭原会话。

## 7. N3：独立研究VM

建议初始规格，须根据N0核对后批准：

```text
名称：value-research-vm
vCPU：4
RAM：16 GiB
系统盘：40 GiB
数据盘：160—200 GiB thin provision
网络：NAT/私有网段；默认无公网入站
系统：受支持的Debian稳定版
```

VM内准备：

- 专用非root运行用户和部署用户；
- Docker Engine/Compose或批准的等价容器运行时；
- Git、证书、时间同步和基础诊断工具；
- 只允许DNS、NTP、HTTPS等必要出站；
- PostgreSQL仅容器内网可见；
- staging和production使用不同Compose项目、网络、数据库和卷；
- staging使用fixture或脱敏数据；
- production目录先创建但不部署应用；
- 不挂载交易目录和凭据；
- SSH只允许从NUC宿主或受信管理路径进入。

## 8. N4：Git与固定部署身份

在以下方案中选择一个：

- 私有GitHub/GitLab：Mac推送，研究VM使用只读deploy key拉取；
- NUC bare Git仓库：独立Git用户接收Mac推送，研究VM只读获取；
- 自建Gitea：仅在愿意承担额外服务维护时使用。

必须实现：

- Git远端不在Syncthing目录；
- 部署使用完整commit SHA；
- Mac构建结果不直接复制覆盖NUC工作目录；
- NUC构建 `linux/amd64` 镜像或按固定digest拉取；
- OpenClaw只能调用固定入口：

```text
deploy-staging RELEASE_ID
test-staging RELEASE_ID
promote-release RELEASE_ID
rollback-release RELEASE_ID
deployment-status RELEASE_ID
```

- 固定入口校验release manifest、目标环境、测试报告哈希和审计状态；
- OpenClaw不能把自由文本拼接进shell；
- 同一环境只有一个部署租约；
- 部署身份不能读取交易密钥或修改NUC宿主安全配置。

## 9. N5：目录、NAS和备份

VM热数据：

```text
/srv/value-investing/objects/sha256/
/srv/value-investing/parquet/
/srv/value-investing/exports/
/srv/value-investing/cache/
/srv/value-investing/backups/
```

NAS只挂载专用目录，设置：

- 独立权限和配额；
- 80%容量预警；
- restic或等价加密备份；
- 每日数据库逻辑备份；
- 对象与Parquet增量备份；
- 至少一个不与NUC同时在线的第二备份目标；
- 抽样恢复和完整恢复演练计划。

Syncthing只同步发布目录中的Markdown、JSON和SHA-256清单，不同步数据库、对象、Parquet、WAL、锁、缓存、密钥和容器卷。

## 10. N6：staging空环境验收

在尚未部署第一层应用时验证：

- VM重启后容器运行时正常；
- staging Compose空骨架可启动；
- PostgreSQL端口未暴露LAN；
- Mac/OpenClaw可以用服务身份提交固定部署动作；
- 未知release、错误哈希和错误目标被拒绝；
- staging可以拉取测试提交并构建amd64镜像；
- 健康检查失败能回滚；
- 数据库备份和恢复通过；
- NAS专用目录写入和权限隔离通过；
- VM无法读取交易目录；
- 防火墙、隧道和Syncthing无新增意外暴露；
- CPU、内存、I/O和温度在基准范围内。

## 11. NUC-PRE验收制品

```text
nuc_preflight_inventory_redacted.md
nuc_change_plan.md
nuc_network_and_port_map.md
nuc_firewall_validation.md
nuc_upgrade_and_reboot_report.md
value_research_vm_spec.json
git_and_deploy_identity.md
staging_environment_test_report.md
backup_restore_test_report.md
protected_services_unchanged_report.md
NUC_PRE_acceptance.md
```

`NUC_PRE_acceptance.md`必须明确：

- 哪些配置实际改变；
- 哪些前置项未完成；
- SSH和回滚路径；
- 研究VM资源与网络；
- Git远端和部署身份；
- staging/prod隔离；
- 备份恢复结果；
- 现有交易和其他服务是否保持不变；
- 是否允许启动第一层L1.7 staging部署。

人工确认NUC-PRE后，第一层才可执行L1.7。该确认不授权production部署。
