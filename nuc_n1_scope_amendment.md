---
title: NUC N1 范围修正
status: effective
date: 2026-08-29
amends: N1 Docker-first plan
preserves_original_n1: true
---

# NUC N1 范围修正

## 修正性质

本文件是 N1 审查后的后续 amendment。原始 N1 文档、结论和形成顺序予以保留；相关文档末尾已追加同日期修正记录，不能把本修正描述为原始 N1 当时结论。

## 当前有效范围

- 当前 NUC-PRE 只服务第一层 L1.7。
- L2 Compose、L2 PostgreSQL、L2 Qdrant 全部为 `future/not-deployed`。
- 不创建任何 L2 目录、网络、卷、容器、数据库或端口。
- 旧停止 Qdrant 不是当前既定依赖，继续保持停止，不启动、不修改、不删除、不复用其数据目录。
- 第二层等待 H1 通过及 L2 技术选型完成后，提交新的独立 D3 审批。

## 本次 N2-A 授权

仅 D3-N2-01、D3-N2-03、D3-N2-06A。未授权 D3-N2-02/04/05、deploy wrapper、Git remote/key/repository、N3—N6、任何 Docker object、研究 VM 或应用部署。

## 已追加修正记录的 N1 文件

- `nuc_docker_change_plan.md`
- `nuc_network_and_port_map.md`
- `git_and_deploy_identity.md`
- `accepted_and_deferred_risks.md`
- `nuc_n1_review_request.md`
- `docker_host_staging_spec.json`（新增 amendments，并将 L2 标为 future/not-deployed；保留 original_n1_preserved 标记）

## 对当前门槛的影响

L1 的隔离、完整 SHA、数据库不外露、禁止 privileged/host network/Docker socket/交易挂载、NVMe/NAS 边界和 `jason-vm` 保护均不变。该修正只缩小交付范围，不降低 L1 硬门槛。
