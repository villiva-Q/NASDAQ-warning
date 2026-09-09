---
title: NUC 网络与端口图
status: draft
date: 2026-08-29
scope: N1 read-only evidence and proposed target
---

# NUC 网络与端口图

## 信任面

```text
Internet（公网/NAT状态未知）
  ├─ Cloudflare edge ← 主机 cloudflared 主动出站 QUIC
  │                    └─ 现有3条脱敏 hostname ingress（研究系统未纳入）
  ├─ Tailscale overlay ← tailscaled UDP 41641 + 动态接口端口
  └─ 上游路由/NAT/ACL：本机证据不足，未知

LAN ── 物理NIC ── br0 ── 主机L3地址
                 └────── vnet1 ── jason-vm（virtio，受保护）

主机 Docker
  ├─ docker0 / bridge（172.17/16，已有容器）
  ├─ polymarket-mvp_default（172.18/16，目前无容器，受保护现状）
  ├─ [目标] value-investing-l1-staging_default（独立私有bridge）
  │    ├─ l1 API/worker
  │    └─ l1 PostgreSQL（仅项目内网）
  └─ [目标] value-investing-l2-staging_default（独立私有bridge）
       ├─ l2 API/worker
       ├─ l2 PostgreSQL（仅项目内网）
       └─ l2 Qdrant（仅项目内网）
```

`br0` 当前 bridge netfilter flags 均为 0，`br_netfilter` 未加载；Docker 使用独立 Linux bridges、IPv4 forwarding 和 nftables `DOCKER*` chains。iptables 前端是 nft backend。UFW、Docker、Tailscale 规则共存于同一 nftables 规则集。任何 Docker/netfilter 变更都必须比较 `br0/vnet1` 状态和 `jason-vm` LAN 连通性，不能假设完全无耦合。

## 当前监听端口（脱敏绑定分类）

### Loopback only

- `25/TCP`：本机 SMTP。
- `5000/TCP`、`8787/TCP`：Python 服务，归属不在本轮改动范围。
- `8384/TCP`：Syncthing GUI/API。
- `11434/TCP`：Docker 中现有模型服务，经 docker-proxy 仅绑定 loopback。
- `12345/TCP`：root SSH session 的 local forward；与半小时重连任务冲突。
- `12346/TCP`：Node 服务；不改。
- `12347/TCP`：SSH local forward；不改。
- `18789/TCP`、`23119/TCP`：OpenClaw 相关 loopback 入口。
- `20241/TCP`：cloudflared 本地 metrics/管理监听。

### LAN / all-interface candidate

- `12662/TCP`、`43382/TCP`：SSH，密钥登录；上游公网可达性未知。
- `3789/TCP`：`opennews-web.service`，root，现有 OpenNews dashboard；不属于研究系统。
- `6611/TCP+UDP`、`6612/TCP+UDP`：sing-box；不改。
- `22000/TCP+UDP`、`21027/UDP`：Syncthing sync/discovery。
- Avahi/mDNS、DHCP client 及若干动态端口：现状保留。
- 停止 Qdrant 曾配置 `6333/TCP` 全接口发布，但容器停止，当前无监听。

### Tailscale

- Tailscale overlay 有专用动态 TCP 监听和 UDP `41641`；研究 MVP 不新增 Tailscale 入口。

### Cloudflare

- cloudflared 主动建立若干动态 QUIC 出站连接；现有 tunnel 有 3 条 hostname ingress。
- 目标研究 Compose 默认不接入现有 tunnel。若未来发布，必须另卡建立独立 ingress、Access 与应用鉴权。

### Public/Internet unknown

- 本机 INPUT/FORWARD 基础策略为 drop，存在 UFW/Tailscale/Docker 规则；但上游 NAT、端口转发、ISP 暴露与 IPv6 路径未从外部测量。
- “全接口监听”只标为 LAN/公网候选，不能据此断言公网开放或关闭。

## 当前 Docker 网络与容器

- `bridge`：默认 bridge，masquerade 与 ICC enabled，host binding 默认 `0.0.0.0`；现有运行容器在此网络。
- `host`、`none`：存在但无容器；研究服务禁止使用 host network。
- `polymarket-mvp_default`：独立 bridge，目前无容器；属于现有环境，不复用、不删除。
- 停止 Qdrant 使用默认 bridge，无 Compose labels、无 links、无 volumes-from；数据 bind 到宿主本地目录。目标研究 Qdrant 不复用这个容器或目录。

## 目标端口方案（提案，未执行）

- L1 PostgreSQL：仅 `value-investing-l1-staging` 网络内 `5432/TCP`，不设置 `ports:`。临时诊断如确有需要，只能另卡批准绑定 `127.0.0.1:<动态批准端口>`。
- L2 PostgreSQL：仅 L2 网络内 `5432/TCP`，不设置 `ports:`。
- L2 Qdrant：仅 L2 网络内 `6333/TCP`、`6334/TCP`，不设置宿主 `ports:`。
- L1/L2 内部 API：仅各自 Compose 网络，不向 LAN/public 发布。
- 可选 operator UI/API：默认无。需要时使用 SSH local forward 到 loopback 端口；必须避开 `12345–12347`、`18789`、`20241`、`23119`，端口逐项批准。
- 第三层 Mac：通过版本化发布快照/manifest 或未来经批准的受控入口交互，不直连数据库、Qdrant 或 Docker socket。

## 目标数据流

```text
SEC/行情/API（HTTPS出站）
  → L1 fetch/normalize（并发1）
  → L1本地NVMe PostgreSQL/对象工作集
  → versioned candidate_manifest + 发布快照
  → L2 ingest/analyse（并发1，证据允许后最多2）
  → L2本地NVMe PostgreSQL + Qdrant
  → Markdown/JSON/CSV/图表/SHA-256清单发布目录
  → Syncthing → Mac（仅发布制品）

本地NVMe逻辑备份/冷文件
  → 独立归档job按需挂载NAS研究子目录
  → .partial → SHA-256/大小核验 → 完成标记/原子发布
  → NAS冷归档
```

禁止流：研究容器 → `/root/.openclaw`、交易目录、`/var/run/docker.sock`、整个 `/mnt/nas`、host PID/IPC/network；Mac/Cloudflare/LAN → PostgreSQL/Qdrant/internal API。

## N3 前网络验证门槛

1. 保存 `nftables` 表/chain/rule count、Docker networks、`br0`/`vnet1`、VM 网卡统计和监听端口基线。
2. 对 Compose `config` 做静态拒绝：`network_mode: host`、`privileged`、未批准 `ports`、Docker socket、受保护目录挂载。
3. 创建每个 project 后立即验证没有意外 host publish，并验证 `jason-vm` LAN 连通/丢包无回归。
4. 若任何步骤加载 `br_netfilter` 或 bridge sysctl 从 0 变化，立即停止并提交差异，不继续试错。

## 2026-08-29 N2-A 后续范围修正（保留原始 N1）

原图中的 L2 project/PostgreSQL/Qdrant 是未来架构占位，不是当前目标状态。当前 NUC-PRE 只允许规划和准备 L1.7；不得据此创建 L2 目录、网络、卷、容器或端口。停止的旧 Qdrant 不复用、不启动。L2 数据流和端口方案须在 H1 与技术选型完成后另行审批。
