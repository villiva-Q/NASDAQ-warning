# D3-N6-01 NUC 现有服务无回归报告

- 执行日期：2026-08-30（UTC）
- 结果：**PASS；未见可归因于 L1 Compose stop/start 的回归**

## 前后一致性

- Docker container/network/volume 数量前后均为 `4/5/1`；增量为 0。
- `jason-vm` 保持 `running`。
- SSH、Docker、libvirtd、cloudflared 保持 active。
- OpenClaw Gateway 的 root user service 保持 active，gateway 进程存在。
- `syncthing@root.service` 保持 active/running。
- sing-box 未由同名 systemd unit 托管，但既有 `/srv/NoWallConf/run/sing-box` 进程保持运行。
- 历史停止的 `qdrant` 仍为 `Exited (255)`，未启动、修改或删除。
- systemd 失败单元前后均为既有 2 个：`ord-20260828-01-exec.service`、`ord-20260828-01-normal-skip-watch.service`。
- 未修改 SSH、Docker daemon、firewall/netfilter、br0、libvirt、cloudflared、Syncthing、sing-box、OpenClaw 或交易任务配置。

## 结论

受保护 VM、网络和既有服务状态与 N5 收尾证据一致，未发现本次变更引入的新失败、端口暴露或 Docker 对象遗留。

---

## D3-N6-01R 复验追加（2026-08-30 UTC）

- 本轮仅修改 L1 固定入口共享逻辑和 `ff2746f...` approved manifest；未执行 Compose、Docker daemon、宿主、SSH、firewall、network 或 libvirt 变更。
- Docker container/network/volume 前后均为 `4/5/1`；PostgreSQL container ID `f13a21240750...`、network ID `64be24111ce5...` 和 volume 未变，PostgreSQL 保持 healthy。
- `jason-vm=running`；SSH、Docker、libvirtd、cloudflared、`syncthing@root`、OpenClaw user gateway 保持 active；sing-box 进程保持 running。
- Qdrant 保持 exited；已有两个 `ord-20260828-01-*` failed unit 数量和名称未变。
- 无宿主 `5432/54329/6333/6334` 监听；无 L2 或 production container/network/volume。
- 未批准或部署 `87e9ca72147af7288fff9ab41a976be689067595`，未输出数据库密码。

**D3-N6-01R 受保护服务回归结果：PASS。**
