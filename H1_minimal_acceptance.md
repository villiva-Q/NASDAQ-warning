# H1 最小验收记录

- 验收时间（UTC）：`2026-09-04T10:50:00Z`
- 裁决：`H1_MINIMAL_ACCEPTED`
- 范围：`L1 / internal staging / research-only`
- 下一状态：`READY_FOR_LIMITED_MULTI_COMPANY_RESEARCH`
- 明确排除：`NOT_FULL_MARKET / NOT_L2 / NOT_L3 / NOT_PRODUCTION / NO_TRADING`

## 一、验收依据

本验收受《内部项目最小防护与工程纪律 v1.0》约束。旧 H1 模板中的多层审批状态链、逐事件哈希链、重复回滚证明和再次独立终审不作为本次内部研究项目的通过条件。本次只判断以下事实：L1 staging 能否运行和恢复、任务与发布是否幂等、PIT 与缺失值语义是否可信、系统是否越过 research-only 边界。

### 当前验收对象

- Git FULL_SHA：`3705e0be9e554b7535aedff524ea552d0a7ab499`
- Git TREE_SHA：`79f8d36c3863de6712cdcd1591ec55872dbd9d28`
- linux/amd64 应用镜像：`sha256:27f80b041443dfe6839c8e897fd474cfb1bd26b5fb6f2dc0617ea199712c54ab`
- release execution：`f362c70e-2336-5741-84d4-a62b7c6ee6a8`
- Alembic revision：`0008_l17_release_identity`
- candidate schema：`candidate_manifest.v0.1`
- candidate schema SHA-256：`8eaf92a769ef80e65633e135e24e5b130d9268915c8194707ead89814b3fa675`
- staging Compose SHA-256：`8c70e670f5896c966f36025665539a4b218f1fa44658c33ed989c66d7ccdfb6f`
- staging 配置 SHA-256：`5abc607306d5e4416d6f9b313ef9c344e7135b3ebcd952cc4fe31aca0fd8193d`

### 主要证据

| 证据 | SHA-256 | 本次采用的事实 |
|---|---|---|
| `l17_nuc_staging_deployment_report.md` | `7aeae4b848d570537274cb8a7a0c9fa5cfef7bb415f25b8788b4a467f475163d` | fixture 全链、发布、失败不发布、幂等、重启/租约恢复、隔离恢复及服务边界通过 |
| `l17_sec_controlled_sample_report.md` | `5a71bd74a322831c39ad25aa1e506f019bc6ccd13074fdb6a20449d3d04135d5` | Apple SEC 受控样本最终成功；采用文件末尾“不可变恢复命名空间修复：最终验收”，此前失败段仅作历史记录 |
| `backup_restore_test_report.md` | `3572135471d0466d1c667a1e0a064c5658484037f78e7efc56f4189a35a18920` | 已有备份恢复能力实证 |
| `protected_services_unchanged_report.md` | `16dc8e72b6469885faec7f32e3a27ebd753f0a7a941335451ff9b97eff404552` | NUC 既有服务未出现可归因回归 |

## 二、最小验收结果

1. **部署身份：通过。** Git commit/tree、应用镜像和 release execution 均有明确身份；NUC 当前运行对象与最终 SEC 验收记录一致。
2. **数据库和服务：通过。** PostgreSQL、control-api、scheduler、worker 均 healthy；数据库为 `0008_l17_release_identity`；API 只绑定 `127.0.0.1:18080`；PostgreSQL 无宿主端口。
3. **fixture 主链：通过。** scheduler/dispatcher、持久队列、worker、exporter、正式发布指针已完成真实链路；同一 occurrence 重放不重复创建 run/job/publication。
4. **SEC 受控样本：通过。** Apple CIK `0000320193` 使用固定 PIT `2024-06-03T13:30:00Z` 和冻结 gzip 原始响应完成真实链路；缓存字节及哈希保持不变。
5. **失败和恢复：通过。** 失败任务不冒充成功且不移动正式指针；历史失败记录未被覆盖；租约恢复和不可变快照恢复得到实证。
6. **数据语义：通过。** market cap、流动性和分析师覆盖度缺失时保持 `unknown`，未填 0、未推测；样本结果为 grade C、三类硬门槛 unknown、`repair_required`，没有用评分覆盖数据不足。
7. **研究边界：通过。** 输出为 `research_only=true`、`production=false`、`publishable=false`；未连接券商、未生成交易指令、未扩大到全市场或第二/第三层。
8. **恢复与资源：通过。** 备份及隔离恢复已有实证；运行未造成 NUC 既有服务可归因回归。

## 三、接受但必须显式保留的限制

1. 真实 SEC 验证目前只有 Apple 单一 CIK，不能代表全市场覆盖、行业覆盖或数据供应稳定性。
2. 真实价格/成交量、公司行动、退市历史和分析师覆盖来源尚未接入；相关字段必须继续为 `unknown`，不得据此产生正式全市场候选。
3. 本次 SEC 样本得到 grade C 和修复队列结果，没有证明真实数据已经足以生成合格候选，也没有证明投资方法有效。
4. SEC 路径当前以文件制品表达门槛、评分和修复结果；验收记录显示对应 `screen_run`、`screen_score`、`hard_gate_evaluation`、`candidate_run` 独立数据库行仍为 0。有限样本阶段可以接受，但扩大到全市场前需要决定这些结果是否必须成为数据库一等记录。
5. 本验收不批准 production、实盘、自动交易、全市场运行或自动进入 L2/L3。

## 四、兼容性和下一阶段边界

- 冻结 `candidate_manifest.v0.1` 的既有字段和语义；后续不得原地删除、重命名或把 unknown 改写为 0/通过。
- 稳定身份使用 `security_id`/CIK，ticker 不作为永久主键。
- 保持 PIT cutoff、原始来源哈希、规则版本、模型版本和 `run_hash` 可追溯。
- 第一层输出只表示“进入进一步研究或修复队列”，不得解释为低估确认、买卖建议、仓位或目标价。
- 下一阶段仅允许有限多公司、跨数据形状的 research-only 样本扩展；任何真实数据源许可选择、评分/估值口径修改、全市场或 L2 启动仍需单独决策。

## 五、裁决

`H1_MINIMAL_ACCEPTED / L1_RESEARCH_STAGING_BASELINE_ACCEPTED / READY_FOR_LIMITED_MULTI_COMPANY_RESEARCH / NOT_FULL_MARKET / NOT_L2 / NOT_PRODUCTION`

本裁决关闭 H1 最小工程验收，不要求再次运行 B 阶段测试、备份恢复或 Claude 终审。下一阶段不得因普通代码、Compose、Docker、测试、迁移或文件范围变化停工请求人工批准。

