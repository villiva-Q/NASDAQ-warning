# NUC 价值投资研究环境 N0 只读前置核查（脱敏）

- 核查时间：2026-08-29 13:03–13:06 AEST
- 范围：NUC 宿主机、`jason-vm`、Docker、网络与相关基础服务
- 执行权限：root；全程仅执行读取/枚举命令
- 脱敏：主机名、序列号、UUID、IP/MAC、隧道凭据路径、域名及身份信息不在本报告中披露
- 结论：硬件余量足以规划 `value-research-vm`，但在 N1 前应先解释高负载、处理失败单元/cron、确认防火墙实际实现，并完成 NAS 恢复演练与 Cloudflare Access 策略核验。

## 1. 宿主机资源、温度与负载

- Debian 13.2，Linux 6.12.57；Intel Core i7-9850H，6 核/12 线程，VT-x 可用。
- 内存 62 GiB：已用约 8 GiB、可用约 54 GiB；无 swap，未发现 zram。
- NVMe 2 TB（可用约 1.6–1.7 TiB，根分区约 6% 使用）；EFI 正常挂载。
- 温度传感器读数约 27.8°C、32°C、41°C，当前无过温迹象。
- 采样时 load average 约 9.36/10.54/11.24（此前一次为 10.81/10.89/11.37），相对 12 线程偏高。进程状态采样未见 D 状态，主要为大量 idle 内核线程；瞬时 top 进程不能解释全部 load。
- 近 7 天：未安装/未启用 sysstat 历史数据，journal 中也无 systemd-sysstat 记录，故无法可靠给出 7 天曲线或峰值。

## 2. `jason-vm`

- 运行中、自动启动；KVM、host-passthrough CPU、AppArmor enforcing。
- 2 vCPU、4 GiB RAM；guest balloon 报告约 3.69 GiB unused、约 1.91 GiB QEMU RSS。
- 2 秒采样 CPU 增量约 0.085 CPU 秒，约等于 4.25% 单核或 2.1% 的 2-vCPU 配额。
- 单个 qcow2 系统盘：逻辑 20 GiB；virsh allocation 约 2.43 GiB（domstats 曾报约 16.5 GiB allocation，统计口径不一致，N1 前需复核）。
- 网络：单 virtio 网卡桥接宿主 `br0`，等同接入宿主 LAN；累计收/发约 421/273 MiB，0 errors、0 drops。
- 未发现独立私有隔离网络正在供其使用。

## 3. Docker

- Docker 运行正常，cgroup v2/systemd driver，overlayfs；2 个容器（1 运行、1 停止），7 个镜像。
- 运行容器 `remarkable-translategemma`：CPU 0.00%，内存约 52.5 MiB/16 GiB，端口仅映射到 loopback `127.0.0.1:11434`。
- 停止容器 `qdrant`：已停止约 5 个月；配置曾发布 6333/TCP 到全接口，但停止状态当前无监听。
- 网络：`bridge`、`host`、`none`、一个项目 bridge；无 overlay 网络。
- Docker 命名卷为 0。镜像约 10.73 GB，其中约 8.56 GB 可回收；build cache 约 535.5 MB。N0 未清理。

## 4. systemd、失败单元与 OpenClaw cron

- 核查时核心服务（SSH、cloudflared、Syncthing、OpenClaw gateway、Docker/libvirt、时间同步）处于运行状态。
- system scope 有 2 个失败单元：`ord-20260828-01-exec.service`、`ord-20260828-01-normal-skip-watch.service`。
- OpenClaw cron 明确失败：`btc-status-only-shadow...`（12 次）、`wp7-oos-backfill-hour...`（12 次）、`daily-archive-auto-run`（91 次）、`memory-incremental-in...`（1 次）。另有一项 M14 job 正在运行。
- 系统错误日志显示 SSH 每约 30 分钟尝试绑定 loopback `12345` 失败（端口已占用），形成持续噪声，需确认对应自动化任务。

## 5. TCP/UDP 监听端口（脱敏接口分类）

TCP：

- 全接口/LAN 可达候选：SSH `12662,43382`；Node `3789`；sing-box `6611,6612`；Syncthing sync `22000`。
- loopback：SMTP `25`、Python `5000,8787`、Syncthing GUI/API `8384`、Docker proxy `11434`、SSH 转发 `12345,12347`、Node `12346`、OpenClaw `18789,23119`、cloudflared metrics/local `20241`。
- Tailscale 接口：一个动态 TCP 端口（具体地址已脱敏）。

UDP：

- Tailscale `41641`；DHCP client `68`；mDNS/Avahi `5353` 及动态端口；Syncthing `22000,21027` 及动态端口；sing-box `6611,6612`；cloudflared 若干动态 QUIC 端口。
- 端口“监听”不等同于公网暴露；公网/NAT/上游 ACL 未在本机侧确认。

## 6. nftables / iptables

- `nft` 与 `iptables` 命令均不可用，因此无法读取规则集。
- 这不能证明“没有防火墙”：Docker、libvirt 或其他组件可能通过内核 netfilter/backend 管理规则。N1 前需确认实际 backend、包来源及上游网关策略；本次未安装工具。

## 7. SSH 有效配置与登录方式

- 监听全接口 TCP `12662` 与 `43382`。
- `PasswordAuthentication no`、`KbdInteractiveAuthentication no`、`PubkeyAuthentication yes`。
- `PermitRootLogin without-password`：root 可使用密钥登录；未发现强制 MFA。
- `AllowTcpForwarding yes`、`GatewayPorts no`、`X11Forwarding yes`、PAM 开启、`MaxAuthTries 6`。
- 风险：双 SSH 端口和 root 密钥登录需确认是否均为有意；反复的 `12345` 转发冲突需定位。

## 8. cloudflared tunnels、published routes 与 Access

- `cloudflared` system service 运行中；单个命名 tunnel 显示 4 条边缘连接，跨墨尔本/悉尼 POP。
- 配置中发现 3 条 hostname ingress，最终 fallback 为 HTTP 404；具体域名和源站已脱敏。
- 当前版本 2026.1.2，CLI 提示可升级至 2026.8.2；本次未升级。
- Cloudflare Access 策略不存于本机 tunnel ingress 文件，且未调用带账户 API 的策略查询；应用、identity provider、allow/deny、MFA 与 session duration 均“未验证”。

## 9. Syncthing

- 以 root 身份通过 `syncthing@root.service` 运行。
- GUI/API 仅绑定 `127.0.0.1:8384`；API key 未读取/未输出。
- 同步监听为 `default`：TCP/UDP `22000` 对全接口，local discovery UDP `21027` 对全接口；global discovery、local discovery、relay、NAT 均启用。
- 风险：以 root 运行扩大文件访问半径；N1 应基于现有目录所有权评估是否迁移到专用用户（不得贸然改动）。

## 10. NAS

- CIFS 3.0 挂载于 `/mnt/nas`，约 15 TiB，总用量约 11 TiB（74%），可用约 3.9 TiB；挂载为 `rw`、`soft`，本地呈现 `root:root 0755`。
- 本机可见权限意味着 root 可读写；普通用户的写权限需按实际 uid/gid 与 ACL 另测。本次未创建测试文件，以遵守只读要求。
- 浅层目录枚举未发现明显 snapshot/recycle 入口；NAS 设备端快照、复制、版本保留、不可变备份及恢复点均未验证。
- `soft` CIFS 在超时/网络抖动时可能向应用返回 I/O 错误，不宜把数据库活动文件直接放在该挂载上。

## 11. OpenClaw

- 以 root 的 systemd user service 运行：`/root/.config/systemd/user/openclaw-gateway.service`。
- 工作目录 `/root`；程序位于 `/root/.nvm/versions/node/v24.18.1/lib/node_modules/openclaw/`；配置 `/root/.openclaw/openclaw.json`。
- gateway 2026.7.1-2，绑定 loopback `127.0.0.1/[::1]:18789`，探测正常。
- 状态检查提示 service PATH 含版本管理器路径、配置“out of date or non-standard”；仅记录建议，未运行 repair。

## 12. 待升级、保留包和重启需求

- `apt list --upgradable` 共 156 项，包含 kernel、glibc、OpenSSH、OpenSSL、Chromium、Docker、containerd、cloudflared、Intel microcode 等安全/核心组件。
- held packages：0。
- `/var/run/reboot-required` 不存在；但计划升级 kernel/microcode 后通常需要安排重启窗口。

## 13. zram/swap、TRIM、SMART、时间同步

- 无 swap、未发现 zram。当前内存余量大，但突发内存耗尽时没有交换缓冲。
- `fstrim.timer` enabled/active，下一次计划 2026-08-31。
- `smartctl` 不可用，NVMe SMART 健康、寿命、介质错误、unsafe shutdown 未验证；本次未安装 smartmontools。
- `systemd-timesyncd` enabled/active，系统时钟已同步；RTC 使用 UTC，时区 Australia/Melbourne。

## 14. `value-research-vm` 可用资源、存储池与私有网络

- 宿主理论空闲：约 10 vCPU 线程未静态分配给现有 VM、约 54 GiB available RAM、约 1.71 TiB libvirt `images` 池可用。
- 保守 N1 初始建议：4 vCPU、16 GiB RAM、120–200 GiB qcow2；保留宿主至少 4 线程与 24 GiB RAM，并先解释当前高 load。
- `images` 池 active/autostart，容量约 1.79 TiB、已分配约 84 GiB、可用约 1.71 TiB。
- libvirt `default` NAT 网络存在但 inactive、非 autostart（192.168.122.0/24 信息不应视为已部署）；现有 `jason-vm` 走 `br0` LAN bridge。
- N1 应新建专用、私有、默认拒绝入站的 libvirt NAT 网络，并明确是否允许经宿主/NAS/Internet 出站；本次未创建或启动。

## 风险与待确认事项

1. **高**：156 个待升级包含 kernel、OpenSSL/OpenSSH、Docker/cloudflared；需维护窗口、兼容性验证与回滚方案。
2. **高**：Cloudflare Access 策略未验证，不能仅凭 tunnel 在线就断言发布入口受身份策略保护。
3. **高**：NAS 快照与真实恢复能力未验证；“有快照”不等于“可恢复”。
4. **中高**：当前 load 约 9–11，缺少 7 天历史，需先定位再承诺 VM 资源。
5. **中高**：`nft`/`iptables` 用户态工具不可用，本机规则集与公网暴露状态未知。
6. **中**：SSH 双端口、root 密钥登录、TCP forwarding/X11 forwarding 开启；确认业务依赖后再收敛。
7. **中**：失败 systemd 单元、4 个失败 OpenClaw cron，以及持续 SSH 端口转发冲突。
8. **中**：Syncthing 以 root 运行且同步端口全接口监听；需确认节点信任边界。
9. **中**：无 swap/zram、SMART 未验证；NVMe/内存异常时韧性和预警不足。
10. **中**：CIFS 使用 `soft`；数据库、向量库和事务性工作目录应优先放本地 NVMe，NAS 用于备份/归档。
11. **待确认**：NUC 磁盘加密、UPS、电源恢复策略、上游路由器端口转发、异地备份、NAS ACL/配额。

## 建议的 N1 变更计划（仅计划，未执行）

1. 建立变更窗口与回滚点：导出 libvirt/OpenClaw/Docker/网络配置，确认 NAS 快照与一次抽样恢复。
2. 补齐只读可观测性：经批准安装/启用 sysstat 与 smartmontools，记录 7 天 CPU/load/I/O、SMART baseline；调查当前高 load。
3. 处理失败项：逐项确认 2 个 failed units、4 个失败 cron、SSH `12345` 冲突的 owner 和业务影响。
4. 安全更新分批演练：先安全库与用户态，再 Docker/cloudflared，最后 kernel/microcode；每批验证 SSH、tunnel、Syncthing、OpenClaw、Docker、libvirt，并预留重启/回滚。
5. 核验访问面：从可信 LAN 和外部网络分别验证 SSH、Cloudflare Access、Syncthing；确认 netfilter backend 和上游 NAT/ACL 后再制定最小端口策略。
6. 创建专用 libvirt 私有 NAT 网络；默认拒绝来自 LAN 的入站，仅允许必要 DNS/NTP/HTTPS 出站，NAS 访问单独授权。
7. 创建 `value-research-vm`：初始 4 vCPU/16 GiB/120–200 GiB qcow2，本地 NVMe 放 OS/数据库，NAS 仅放加密备份和研究归档；设置资源上限与 autostart 策略。
8. VM 内按最小权限部署研究栈，固定依赖、记录数据源许可和密钥管理方式；不得把 API key 写入镜像、日志或仓库。
9. 做验收与恢复演练：性能基线、断网/重启、VM 备份还原、NAS 文件恢复、Cloudflare/SSH 紧急访问路径。

## 实际执行的只读命令清单

以下为实际执行的命令族（管道中的 `sed/rg/head/wc` 仅用于筛选或脱敏）；未执行任何状态变更命令：

```text
id
uname -a
cat /etc/os-release
command -v {virsh,docker,nft,iptables,cloudflared,syncthing,openclaw,smartctl,sensors,zramctl,apt}
hostnamectl
uptime
last reboot -F | head -n 3                 # 命令不存在
lscpu
free -h
swapon --show --bytes                      # 命令不存在
zramctl                                    # 命令不存在
lsblk -e7 -o ...
df -hT -x tmpfs -x devtmpfs
df -i -x tmpfs -x devtmpfs
sensors                                    # 命令不存在/无输出
读取 /sys/class/thermal/thermal_zone*/temp
cat /proc/loadavg
sar -q / journalctl -u systemd-sysstat     # sysstat 不可用
systemctl status fstrim.timer
systemctl status systemd-timesyncd chrony ntpsec
timedatectl
virsh list --all
virsh dominfo/domblklist/domiflist/domstats/dumpxml jason-vm
virsh domblkinfo jason-vm vda
virsh cpu-stats jason-vm --total（两次，间隔 2 秒）
virsh pool-list/pool-info/vol-list
virsh net-list/net-info/net-dumpxml
docker info
docker ps -a
docker stats --no-stream
docker network ls
docker volume ls
docker system df [-v]
systemctl --failed
systemctl --user --failed
systemctl list-units/list-unit-files/list-timers
systemctl status/show（SSH、cloudflared、Syncthing、OpenClaw）
systemctl --user status/show openclaw openclaw-gateway
journalctl --since '7 days ago' --priority=err -n 200
ss -H -lntup
ip -br link
ip -br addr
ip route
nft list ruleset                            # 命令不可用
iptables -S / iptables -t nat -S            # 命令不可用
/usr/sbin/sshd -T
cloudflared tunnel list
cloudflared tunnel info villiva              # 名称不匹配，无 tunnel 结果
find /etc/cloudflared /root/.cloudflared ... # 仅文件名
筛选读取 /etc/cloudflared/config.yml 的 tunnel/credentials-file/hostname/service 行并脱敏
find Syncthing config.xml
筛选读取 Syncthing address/listen/discovery/relay/NAT 配置（未读取 API key）
findmnt -T /mnt/nas
stat /mnt/nas
浅层查找 NAS snapshot/recycle 目录（无写入测试）
ps -eo ... --sort=-pcpu
ps 状态分类统计
openclaw gateway status --deep
openclaw cron list
apt list --upgradable
apt-mark showhold
检查 /var/run/reboot-required 是否存在
systemctl status smartmontools smartd
smartctl -H -A /dev/nvme0n1                # 命令不可用
```

## 停止点

N0 报告至此结束。未执行 N1，未安装、升级、重启、停止服务或修改任何系统、网络、虚拟化、容器及 OpenClaw 配置。
