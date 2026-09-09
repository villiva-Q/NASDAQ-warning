# L1.7 Apple SEC 受控小样本报告

- 状态：`FUNCTIONAL_DEFECT / SEC_CONTROLLED_SAMPLE_NOT_COMPLETED`
- FULL_SHA：`ae6a578e354e970817da0c9acaad9ffaf29a28e5`
- TREE_SHA：`b75dc21ddfc467d93454cc9afb459927be7271c8`
- 父提交：`e52cf314b463ab95bbdec4a4c124dc17b8a12dbd`
- 标题：`fix: close SEC sample market and parser v2 contracts`
- NUC 应用镜像：`sha256:675498d72cb90192cd3b4e5031d17a2b22721c38bc457d37258046381a167446`（linux/amd64）
- release_execution：`13e5b184-ae25-50df-8411-68573d13a028`，记录的 FULL_SHA/TREE_SHA/镜像均与上述一致。
- CIK：`0000320193`；PIT cutoff：`2024-06-03T13:30:00Z`。

## prepare 与冻结输入

- `sec-prepare` 命中既有缓存并将完全匹配的 run_spec 从 v1 原子升级为 `l1.7.sec-screen-parser.v2`。
- submissions gzip SHA-256：`6bd4d7ea9c930c0504837ee5d40ae1ddcdfd119e3223f52f15718e6571a46174`。
- companyfacts gzip SHA-256：`f0ffb4c2bc0c18b0f3cd96ebe91fd9d36a08aa1c0f4a692d61428b1e94bb721a`。
- 准备前后缓存字节哈希不变，未重新访问 SEC。
- v1 run_hash：`80382b3b96fca0104091f8b64672ecb51a98469ce9e785cb70dfc8a46aed8952`。
- v2 run_hash：`86a78c074201c59567efc4a86dd97efcebe4d08f22eeef5ae2ef9892fbf0515d`；与 v1 不同。

## 首个可复现代码缺陷

- 失败命令：`docker compose --env-file /srv/value-investing/runtime/l1-staging-ae6a578e354e970817da0c9acaad9ffaf29a28e5/compose.env -f /srv/value-investing/releases/ae6a578e354e970817da0c9acaad9ffaf29a28e5/infra/compose/docker-compose.staging.yml --profile sec-sample run --rm --no-deps sec-sample`。
- 新 v2 control_run：`29e367ce-fe7e-4b85-96e4-de825afcc6b8`，状态 `requested`，input_snapshot_hash 为上述 v2 run_hash，未产生 screen_run/candidate_run/result。
- 新 v2 job：`ebdf487f-aa52-4da1-b589-b03c2d8de617`，三次尝试后 `dead_letter`，last_error=`b3b_worker_failure`。
- 根因：`ControlRunServiceAdapter.create()` 为 SEC 创建的队列 payload 只有 `kind/run_hash/source_class` 三个键；常驻 B3b worker 会抢先领取它，并调用只接受 weekly-formal 14 字段 payload 的 `validate_queue_job_payload()`。
- 只读最小复现抛出：`workflow.dispatcher.DispatchError: queue payload fields are not closed`；输入形状为 `['kind', 'run_hash', 'source_class']`。
- 因作业被常驻 worker 先行 dead-letter，SEC runner 无法取得其精确 lease，实际 PIT→标准化→门槛→等级→评分→候选链路没有执行；按自动回流规则未继续重放。

## 旧记录保留与现场

- 旧 v1 control_run：`9e1f50f5-f5d7-4b57-a2c0-f49bff52c267`，状态仍为 `requested`，input_snapshot_hash=`80382b...8952`。
- 旧 v1 job：`4b4e266d-cd5d-4cb8-8687-feae5ca08e59`，仍为 `dead_letter`、attempt_count=3、last_error=`b3b_worker_failure`；未删除或改写。
- SEC 作业总数 2，均为 dead_letter；SEC 成功 run/result 为 0。
- PostgreSQL、control-api、scheduler、worker 均 healthy；数据库 revision `0008_l17_release_identity`。
- API health HTTP 200，仅监听 `127.0.0.1:18080`；PostgreSQL 无宿主 published port。
- 未移动正式发布指针，未运行其他公司，未进入全市场、L2、L3 或 production。

## 结论

`FUNCTIONAL_DEFECT / SEC_CONTROLLED_SAMPLE_NOT_COMPLETED / NOT_FULL_MARKET / NOT_PRODUCTION`

需要回派 Codex 修复 SEC 专属作业与常驻 B3b worker 的队列消费隔离/路由，使 SEC runner 能取得并完成其自有 job；随后从本 FULL_SHA 的现场重新部署复验。

---

## 2026-09-04 路由修复提交复验

- 状态：`FUNCTIONAL_DEFECT / SEC_CONTROLLED_SAMPLE_NOT_COMPLETED`。
- 核验并部署：FULL_SHA `7a1cb518aeb1a98edd9b48b82056b0dae043b7c9`，TREE_SHA `045be024cbaf976059baf58e1ad7ae34e8d40687`，父提交 `ae6a578e354e970817da0c9acaad9ffaf29a28e5`，标题 `fix(sec): route controlled sample queue jobs`。
- 新 linux/amd64 镜像：`sha256:107d5364fd65a6536062c8ef064d668d1daf18b8a211855692e220b373bf3cb3`；release context identity：`bf297e20-eea5-50cb-800d-08e8d3148b53`。因首个 SEC 命令在首次 release-bound 事务前失败，数据库尚未追加该 release_execution（计数 0）。
- 仅重建 control-api/scheduler/worker；PostgreSQL 容器、数据卷与 revision `0008_l17_release_identity` 保持不变；未执行迁移、备份恢复或 fixture 验收。
- `sec-prepare` 成功且缓存未变：companyfacts `f0ffb4c2bc0c18b0f3cd96ebe91fd9d36a08aa1c0f4a692d61428b1e94bb721a`，submissions `6bd4d7ea9c930c0504837ee5d40ae1ddcdfd119e3223f52f15718e6571a46174`；两份 gzip 均通过解压校验。run_spec SHA-256 `f51a2ab863122b0baaded953ab03419f1e2f25efd72f67af54a2b7dd0ae73682`，仍为 parser v2、PIT `2024-06-03T13:30:00Z`、run_hash `86a78c074201c59567efc4a86dd97efcebe4d08f22eeef5ae2ef9892fbf0515d`。
- 失败命令：`docker compose --env-file /srv/value-investing/runtime/l1-staging-7a1cb518aeb1a98edd9b48b82056b0dae043b7c9/compose.env -f /srv/value-investing/releases/7a1cb518aeb1a98edd9b48b82056b0dae043b7c9/infra/compose/docker-compose.staging.yml --profile sec-sample run --rm --no-deps sec-sample`。
- 首个异常：`RuntimeError: L1.6 queue did not lease the control run job`，发生于 `SecSampleRunner._run -> lifecycle.mark_running`。实际 SEC payload 仍为严格三字段：`kind/run_hash/source_class`。
- 恢复记录未创建：执行前后总计均为 control_run=5、job_queue=5、screen_run=0、screen_score=0、hard_gate_evaluation=0、candidate_run=0。v1 run/job `9e1f50f5-f5d7-4b57-a2c0-f49bff52c267` / `4b4e266d-cd5d-4cb8-8687-feae5ca08e59` 与首次 v2 run/job `29e367ce-fe7e-4b85-96e4-de825afcc6b8` / `ebdf487f-aa52-4da1-b589-b03c2d8de617` 均原样保持 requested/dead_letter、attempt_count=3、原 payload/hash/error 不变。
- 现场健康：PostgreSQL、control-api、scheduler、worker 均 healthy；API HTTP 200 且仅监听 `127.0.0.1:18080`；正式发布指针计数仍为 1，未移动。
- 按自动回流规则，在首个可复现代码缺陷处停止；未执行第二次重放，未扩大到其他公司、全市场、L2、L3 或 production。

结论：`FUNCTIONAL_DEFECT / SEC_CONTROLLED_SAMPLE_NOT_COMPLETED / NOT_FULL_MARKET / NOT_PRODUCTION`。

---

## 2026-09-04 租约竞态修复提交复验

- 状态：`FUNCTIONAL_DEFECT / SEC_CONTROLLED_SAMPLE_NOT_COMPLETED`。
- 裸仓库只读核验通过：FULL_SHA `1078e271e837ca9f4e71fc29ada4360f7fb8177f`，TREE_SHA `a2265ab86645fe2a809a662c4f08f1257187da5e`，父提交 `7a1cb518aeb1a98edd9b48b82056b0dae043b7c9`，标题 `fix(sec): converge controlled sample queue ownership`。
- 构建并部署的 linux/amd64 镜像：`sha256:76c8b6544bf5177d5d78d4db2c5c1ac01f3797b732a8b7e6cbcc77f8da1197cf`；release context identity：`0046898f-0868-52d6-8b6a-944e48902171`。首次SEC命令在创建release-bound事务前失败，因此数据库中该 release_execution 计数仍为0。
- 仅强制重建 control-api、scheduler、worker；PostgreSQL容器 `2c73c2c51c81b99028db3f3d291d9a577e0212d58e8fb4ca375f02860c71b1c2` 保持运行，未执行迁移、卷替换、备份恢复或fixture验收。
- `sec-prepare` 成功；run_spec SHA-256 `f51a2ab863122b0baaded953ab03419f1e2f25efd72f67af54a2b7dd0ae73682`，parser仍为 `l1.7.sec-screen-parser.v2`，PIT cutoff仍为 `2024-06-03T13:30:00Z`，v2 run_hash仍为 `86a78c074201c59567efc4a86dd97efcebe4d08f22eeef5ae2ef9892fbf0515d`。v1 run_hash为 `80382b3b96fca0104091f8b64672ecb51a98469ce9e785cb70dfc8a46aed8952`。
- 缓存保持：companyfacts大小271819、SHA-256 `f0ffb4c2bc0c18b0f3cd96ebe91fd9d36a08aa1c0f4a692d61428b1e94bb721a`；submissions大小28459、SHA-256 `6bd4d7ea9c930c0504837ee5d40ae1ddcdfd119e3223f52f15718e6571a46174`；两份gzip解压校验通过，未出现缓存缺失或损坏证据。
- 失败命令：`docker compose --env-file /srv/value-investing/runtime/l1-staging-1078e271e837ca9f4e71fc29ada4360f7fb8177f/compose.env -f /srv/value-investing/releases/1078e271e837ca9f4e71fc29ada4360f7fb8177f/infra/compose/docker-compose.staging.yml --profile sec-sample run --rm --no-deps sec-sample`，稳定退出码78。
- 首个异常：`apps.screener.production_runtime.TrustedRuntimeUnavailable: trusted staging configuration hash is unavailable`；底层为 `FileNotFoundError: /run/secrets/l1_staging_config_sha256`。新代码 `_build_sec_sample_runner()` 调用 `_runtime_config()`，但Compose的 `sec-sample` 服务只挂载 `l1_postgres_dsn`，未挂载 `l1_staging_config_sha256`，也未挂载 `/etc/value-investing/staging/l1.toml`。
- 失败发生在队列创建/争抢之前：实际SEC payload未生成；预期严格形状仍为 `kind/run_hash/source_class`，lease owner为空，状态时间线为“命令启动 → runtime组装失败 → exit 78”，没有新run/job或状态变化。
- 执行前后SEC计数均为 control_run=2、job_queue=2、screen_run=0、screen_score=0、hard_gate_evaluation=0、candidate_run=0。旧v1 run/job `9e1f50f5-f5d7-4b57-a2c0-f49bff52c267` / `4b4e266d-cd5d-4cb8-8687-feae5ca08e59` 与旧v2 run/job `29e367ce-fe7e-4b85-96e4-de825afcc6b8` / `ebdf487f-aa52-4da1-b589-b03c2d8de617` 仍保持原主键、requested/dead_letter、attempt_count=3、payload/hash/error，未删除、重置、改写或重新入队。
- 健康现场：PostgreSQL、control-api、scheduler、worker均healthy；数据库 `0008_l17_release_identity`；API HTTP 200且只监听 `127.0.0.1:18080`，PostgreSQL无宿主监听端口。
- 按缺陷自动回流纪律停止：未执行第二次重放，未验证成功screen/result及市场unknown链路，未扩大到其他公司、全市场、L2、L3或production；未修改代码、Compose或基础设施配置。

结论：`FUNCTIONAL_DEFECT / SEC_CONTROLLED_SAMPLE_NOT_COMPLETED / NOT_FULL_MARKET / NOT_PRODUCTION`。需回派Codex为 `sec-sample` 补齐与 `_runtime_config()` 一致的只读配置与配置哈希挂载（并保持现有严格边界），再从本现场继续复验。

---

## 2026-09-04 可信挂载修复提交复验

- 状态：`FUNCTIONAL_DEFECT / SEC_CONTROLLED_SAMPLE_NOT_COMPLETED / NOT_FULL_MARKET / NOT_PRODUCTION`。
- 裸仓库只读核验通过：FULL_SHA `7c5e5ae9d608df12f5731829be5d9f2834220839`，TREE_SHA `3a2acb03dab2647fe1aa244f6249ac7b1f0c6217`，父提交 `1078e271e837ca9f4e71fc29ada4360f7fb8177f`，标题 `fix(staging): mount trusted config for SEC sample`；变更仅 `infra/compose/docker-compose.staging.yml` 与 `tests/test_staging_compose.py`，两文件 SHA-256 分别为 `8c70e670f5896c966f36025665539a4b218f1fa44658c33ed989c66d7ccdfb6f` / `a7838df70af1bc604118c75a4d35221f3763467e3329bc533bb41fd98f1ec711`。
- 新 linux/amd64 镜像：`sha256:b177e31a5fdaf75ae70f507b9408449458a3f3d185f0611ff9de6b888347691e`；release context identity：`3c66cca7-7d87-55ec-8a06-8057841729c9`。仅重建 control-api/scheduler/worker，PostgreSQL 容器与数据卷保留；未执行迁移、备份恢复或 fixture 验收。首个 SEC 命令在新 release-bound 事务落库前失败，该 `release_execution` 行计数为 0。
- 实际 env-file 展开 Compose 核验：`sec-sample` 仅连接 `l1_staging`；配置 `/etc/value-investing/staging/l1.toml` 为 uid/gid 10001、mode 0444；配置哈希 `/run/secrets/l1_staging_config_sha256` 为 uid/gid 10001、mode 0400；PostgreSQL 无宿主发布端口，control-api 仅 `127.0.0.1:18080->8080`。
- 同 release/Compose 只读挂载检查：`docker compose ... --profile sec-sample run --rm --no-deps --entrypoint test sec-sample -r /run/secrets/l1_staging_config_sha256` 退出 0；对 `/etc/value-investing/staging/l1.toml` 同样检查退出 0；未读取文件内容。
- `sec-prepare` 成功；run_spec 前后 SHA-256 均为 `f51a2ab863122b0baaded953ab03419f1e2f25efd72f67af54a2b7dd0ae73682`，parser 仍为 `l1.7.sec-screen-parser.v2`，CIK `0000320193`，PIT cutoff `2024-06-03T13:30:00Z`，v2 run_hash `86a78c074201c59567efc4a86dd97efcebe4d08f22eeef5ae2ef9892fbf0515d`，与v1 `80382b3b96fca0104091f8b64672ecb51a98469ce9e785cb70dfc8a46aed8952` 不同。
- 缓存前后不变：companyfacts 271819 bytes，SHA-256 `f0ffb4c2bc0c18b0f3cd96ebe91fd9d36a08aa1c0f4a692d61428b1e94bb721a`；submissions 28459 bytes，SHA-256 `6bd4d7ea9c930c0504837ee5d40ae1ddcdfd119e3223f52f15718e6571a46174`；两份 gzip 均通过 `gzip -t`，无缓存缺失或损坏证据。
- 失败命令：`docker compose --env-file /srv/value-investing/runtime/l1-staging-7c5e5ae9d608df12f5731829be5d9f2834220839/compose.env -f /srv/value-investing/releases/7c5e5ae9d608df12f5731829be5d9f2834220839/infra/compose/docker-compose.staging.yml --profile sec-sample run --rm --no-deps sec-sample`，退出码 70。
- 首个可复现缺陷：`SecSampleQueueExecutionError: SEC controlled-sample queue job is dead-lettered`。`ControlRunServiceAdapter.create()` 只在已有 run 状态为 `FAILED` 时进入 SEC 确定性恢复；现场 v2 run `29e367ce-fe7e-4b85-96e4-de825afcc6b8` 实际状态为 `requested`，其 job `ebdf487f-aa52-4da1-b589-b03c2d8de617` 为 `dead_letter`，因而返回旧 run，随后在权威 run/job 收敛检查中立即拒绝。
- 关键输入形状仍为严格三字段 `kind/run_hash/source_class`。lease owner 为空；时间线为“19:29:19 +10:00 命令启动 → 复用 requested/dead_letter 旧绑定 → exit 70”，未创建恢复 run/job，也未进入 worker lease/PIT/标准化/门槛/评分链。
- 历史保留：v1 run/job `9e1f50f5-f5d7-4b57-a2c0-f49bff52c267` / `4b4e266d-cd5d-4cb8-8687-feae5ca08e59`，v2 run/job `29e367ce-fe7e-4b85-96e4-de825afcc6b8` / `ebdf487f-aa52-4da1-b589-b03c2d8de617`，两组均保持 run=`requested`、job=`dead_letter`、attempt_count=3、lease_owner=NULL、last_error=`b3b_worker_failure`，主键、payload/payload_hash 和时间戳未改。
- 首次前后全局计数相同：control_run=5，job_queue=5，screen_run=0，screen_score=0，hard_gate_evaluation=0，candidate_run=0，data_repair_queue=0，schedule_occurrence=3，published_run_pointer=1。无恢复 run/job/screen/result/occurrence 主键；既有 occurrence 主键为 `d1373b3a-9f31-4bc5-b6d2-0c5b9bf58bc5`、`ce5ecd24-5d54-4615-8422-3cbc90de2327`、`66b08f88-2f1b-470d-a1a8-050c4dd1410a`；正式发布指针仍指向 control_run `5bae41c0-fd2b-4179-9567-6cfc6a026daa`，未移动。
- 现场健康：PostgreSQL、control-api、scheduler、worker 均 healthy；数据库 `0008_l17_release_identity`；API 仅绑定 `127.0.0.1:18080`，PostgreSQL 无宿主发布端口。
- 依缺陷自动回流纪律立即停止：未执行第二次重放，未修改代码，未扩大到其他公司、全市场、H1 实盘批准、L2、L3 或 production。

结论：`FUNCTIONAL_DEFECT / SEC_CONTROLLED_SAMPLE_NOT_COMPLETED / NOT_FULL_MARKET / NOT_PRODUCTION`。需回派 Codex 修复确定性恢复对“run 仍 requested 但其严格 SEC job 已 dead_letter”的受控历史形状的识别，且不改写旧 run/job。

---

## 2026-09-04 恢复资格修复提交复验

- 状态：`FUNCTIONAL_DEFECT / SEC_CONTROLLED_SAMPLE_NOT_COMPLETED / NOT_FULL_MARKET / NOT_PRODUCTION`。
- 裸仓库身份通过：FULL_SHA `adc130ab8b04ee7b6e5d2a9b68a7c6d2d218887e`，TREE_SHA `e7c34cea3973a29e31d95d93ea7ee3017f6ca7e2`，父提交 `7c5e5ae9d608df12f5731829be5d9f2834220839`，标题 `fix(sec): recover requested dead-letter sample`；提交仅修改 `apps/screener/runtime.py`、`tests/test_l17_sec_dispatch_contracts.py`。
- 构建并部署 linux/amd64 镜像 `sha256:4157c88ecc79a6578c1a0e44d79cef519b5e97fd4a460be8e64a6fb5fd340670`；release identity `5074d556-d5c1-5e82-855e-1d631697d58c` 已落库且绑定上述 SHA/TREE/镜像。仅重建 control-api/scheduler/worker，PostgreSQL 容器和数据卷保持原位；未执行迁移、备份恢复或 fixture 验收。
- 实际 env-file 展开：sec-sample 只连接 `l1_staging`；`/run/secrets/l1_staging_config_sha256` 为 uid/gid 10001、mode 0400，`/etc/value-investing/staging/l1.toml` 为 uid/gid 10001、mode 0444；两项 `test -r` 均 exit 0；PostgreSQL 无宿主端口，control-api 仅 `127.0.0.1:18080->8080`。
- `sec-prepare` 命中冻结缓存并 exit 0；run_spec SHA-256 前后均为 `f51a2ab863122b0baaded953ab03419f1e2f25efd72f67af54a2b7dd0ae73682`，parser `l1.7.sec-screen-parser.v2`，CIK `0000320193`，PIT `2024-06-03T13:30:00Z`，v2 run_hash `86a78c074201c59567efc4a86dd97efcebe4d08f22eeef5ae2ef9892fbf0515d`，与 v1 `80382b3b96fca0104091f8b64672ecb51a98469ce9e785cb70dfc8a46aed8952` 不同。submissions 为 28459 bytes / `6bd4d7ea9c930c0504837ee5d40ae1ddcdfd119e3223f52f15718e6571a46174`；companyfacts 为 271819 bytes / `f0ffb4c2bc0c18b0f3cd96ebe91fd9d36a08aa1c0f4a692d61428b1e94bb721a`；前后哈希相同且 gzip 校验 exit 0，无重新访问 SEC 的证据。
- 首次正式命令：`docker compose --env-file /srv/value-investing/runtime/l1-staging-7c5e5ae9d608df12f5731829be5d9f2834220839/compose.env -f /srv/value-investing/releases/adc130ab8b04ee7b6e5d2a9b68a7c6d2d218887e/infra/compose/docker-compose.staging.yml --profile sec-sample run --rm --no-deps sec-sample`。恢复身份只创建一次：control_run `a83ddbed-dcd2-4957-a509-d60401461009`，job `f92b7b3e-ccdf-4d84-92f4-9a49d94bc916`；payload 严格且仅含 `kind/run_hash/source_class`，payload_hash `9fcaf56f961586fb992586e12fb56f41ce4bcde2eec1cee9aa88f8f2709222f1`。
- 首个新缺陷：恢复 job 被 `l1.7_b3b_worker` 取得后，run 时间线为 requested 09:50:33.099664Z → queued 09:50:33.138733Z → running 09:50:33.140986Z → failed 09:50:35.062207Z；job 三次尝试后 dead_letter，`last_error=b3b_worker_failure`，最终 lease_owner=NULL。确定性触发条件是结果卷中已存在同一 v2 run_hash、但绑定旧 v2 run `29e367ce-fe7e-4b85-96e4-de825afcc6b8` 的 `_SUCCESS` 快照；新恢复运行走到 `NonReleaseSnapshotWriter.stage()` 时命中不可覆盖边界，异常类型/关键错误为 `FileExistsError: B2 result snapshots are immutable and cannot be overwritten`。应用仅持久化通用 `b3b_worker_failure`，未保留底层 traceback。
- 历史未改：v1 `9e1f50f5-f5d7-4b57-a2c0-f49bff52c267` / `4b4e266d-cd5d-4cb8-8687-feae5ca08e59` 与旧 v2 `29e367ce-fe7e-4b85-96e4-de825afcc6b8` / `ebdf487f-aa52-4da1-b589-b03c2d8de617` 仍为 requested/dead_letter、attempt_count=3、lease_owner=NULL、原严格 payload/hash/error 不变。
- 首次前→后全局计数：control_run 5→6，job_queue 5→6，release_execution 4→5；screen_run 0→0、screen_score 0→0、hard_gate_evaluation 0→0、candidate_run 0→0、data_repair_queue 0→0、schedule_occurrence 3→3、published_run_pointer 1→1。未生成新 screen/result/occurrence 主键；正式指针仍指向 control_run `5bae41c0-fd2b-4179-9567-6cfc6a026daa`。按首缺陷停止，未执行第二次重放，也未据此宣称本次完成市场 unknown 链路验收。
- 健康现场：PostgreSQL、control-api、scheduler、worker 均 healthy；API health HTTP 200；数据库 `0008_l17_release_identity`；API 仅 loopback 18080，PostgreSQL 无宿主发布端口。

结论：`FUNCTIONAL_DEFECT / SEC_CONTROLLED_SAMPLE_NOT_COMPLETED / NOT_FULL_MARKET / NOT_PRODUCTION`。需要 Codex 处理“同 run_hash 已有绑定旧失败 run 的可见非发布快照”与新恢复身份之间的闭合恢复语义；不得覆盖旧快照或历史数据库记录。

## 2026-09-04 不可变恢复命名空间修复：最终验收

- 裸仓库只读核验通过：FULL_SHA `3705e0be9e554b7535aedff524ea552d0a7ab499`，TREE_SHA `79f8d36c3863de6712cdcd1591ec55872dbd9d28`，父提交 `adc130ab8b04ee7b6e5d2a9b68a7c6d2d218887e`，标题 `fix(sec): namespace immutable recovery snapshots`；提交文件严格为 `apps/screener/runtime.py`、`apps/screener/sec_sample_runner.py`、`packages/platform/l1_platform/control_runs.py`、`tests/test_l17_sec_dispatch_contracts.py`。
- 物化 release `/srv/value-investing/releases/3705e0be9e554b7535aedff524ea552d0a7ab499`，构建并部署 linux/amd64 镜像 `sha256:27f80b041443dfe6839c8e897fd474cfb1bd26b5fb6f2dc0617ea199712c54ab`；release_execution / release identity 为 `f362c70e-2336-5741-84d4-a62b7c6ee6a8`。仅更新应用容器，PostgreSQL 与数据卷保留；未执行迁移往返、备份恢复或 fixture 验收。
- 实际 env-file 展开：`sec-sample` 仅连接 `l1_staging`；`l1_staging_config_sha256` 映射 `/run/secrets/l1_staging_config_sha256`（uid/gid 10001、mode 0400），`l1_staging_runtime_config` 映射 `/etc/value-investing/staging/l1.toml`（uid/gid 10001、mode 0444）；以同一 release/Compose 和 `/usr/bin/test -r` 检查两项均 exit 0。control-api 仅 `127.0.0.1:18080->8080`；PostgreSQL 无宿主发布端口。
- `sec-prepare` exit 0，固定 CIK `0000320193`、PIT cutoff `2024-06-03T13:30:00Z`、parser `l1.7.sec-screen-parser.v2`；run_spec SHA-256 保持 `f51a2ab863122b0baaded953ab03419f1e2f25efd72f67af54a2b7dd0ae73682`。submissions 为 28459 bytes / `6bd4d7ea9c930c0504837ee5d40ae1ddcdfd119e3223f52f15718e6571a46174`，companyfacts 为 271819 bytes / `f0ffb4c2bc0c18b0f3cd96ebe91fd9d36a08aa1c0f4a692d61428b1e94bb721a`；前后压缩字节哈希相同且 gzip 校验通过，无缓存缺失、损坏或重新访问 SEC 的证据。
- v1 run_hash `80382b3b96fca0104091f8b64672ecb51a98469ce9e785cb70dfc8a46aed8952`；v2 与全部恢复尝试的输入 run_hash `86a78c074201c59567efc4a86dd97efcebe4d08f22eeef5ae2ef9892fbf0515d`，两者不同。历史保持：v1 run/job `9e1f50f5-f5d7-4b57-a2c0-f49bff52c267` / `4b4e266d-cd5d-4cb8-8687-feae5ca08e59`（requested/dead_letter）；原 v2 run/job `29e367ce-fe7e-4b85-96e4-de825afcc6b8` / `ebdf487f-aa52-4da1-b589-b03c2d8de617`（requested/dead_letter）；第一代恢复 run/job `a83ddbed-dcd2-4957-a509-d60401461009` / `f92b7b3e-ccdf-4d84-92f4-9a49d94bc916`（failed/dead_letter）。三组旧主键、状态、严格 payload、时间和历史内容均未改变，最终 lease_owner 均为 NULL。
- 旧 v2 根快照 `/var/lib/docker/volumes/value_investing_l1_staging_sec_sample_result/_data/86a78c074201c59567efc4a86dd97efcebe4d08f22eeef5ae2ef9892fbf0515d`（含 `_SUCCESS`、`SHA256SUMS` 及五个 JSON 制品）在首次执行前后清单与逐文件 SHA-256 完全一致（`old-root-before.sha256` 与 `old-root-after.sha256` cmp=0）。成功恢复使用确定性非碰撞命名空间 `/var/lib/docker/volumes/value_investing_l1_staging_sec_sample_result/_data/721e1b973f2ff3a92247e06a9965b654a2f92ca9762baf2958cabbf8a92ab58c`，未覆盖旧根；其 `_SUCCESS` SHA-256 为 `b10fac4de298e89726d1cc1361eed02b2727309569c28e1578f485c823407ac3`，`SHA256SUMS` SHA-256 为 `7e13f33f30a27898b25532ecd0bbaba31eaec9dbb5f3915941a1dc7375373477`。
- 首次正式 `sec-sample` 通过持久化队列、dispatcher、`PersistentQueueWorker.run_exact` 和 `SecSampleRunner.run_bound` 完成。并发常驻 worker 收敛为唯一第二代恢复 run `fafbe5fe-e7d5-4d75-a8e5-c3ce794a0445` / job `5e552b79-d284-4ade-af59-f37a32dcb09d`；严格 payload 仅 `kind=l1.7.b2`、上述 v2 `run_hash`、`source_class=sec_controlled_sample`。时间线：requested `10:28:22.247419Z` → queued `10:28:22.278513Z` → running `10:28:22.281568Z` → succeeded `10:28:22.550594Z`；job attempt_count=1，最终 lease_owner=NULL、last_error=NULL。
- 成功制品 run_id 同上述恢复 control_run，manifest `l15-b2-86a78c074201c595`；数据库 screen_run/screen_score/hard_gate_evaluation/candidate_run 均无独立行，因此没有对应数据库主键。制品真实记录 L1.3 `l1.3.v1`、L1.4 `l1.4.0` 双模型与 L1.5 规则链；Apple `security_id=8e7110c8-a95b-4eb5-bb9d-8fe442f346fb`，data_grade=C，survival/data/accounting 均 unknown，disposition=repair_required，score=rank=NULL，candidate_count=0、repair_queue_count=1。market_cap/liquidity/analyst_coverage 均 unknown；估值字段为 NULL/insufficient_verify，无 0 或推测值。SEC raw 契约由 v2 parser 保持为 market_snapshot 仅 `as_of` 与 `source=unavailable`，未出现五个禁止市场字段。
- 执行前→首次后计数：control_run 6→7，job_queue 6→7，release_execution 5→6；screen_run 0→0、screen_score 0→0、hard_gate_evaluation 0→0、candidate_run 0→0、data_repair_queue 0→0、occurrence 3→3、formal publication 1→1。occurrence 主键仍为 `d1373b3a-9f31-4bc5-b6d2-0c5b9bf58bc5`、`ce5ecd24-5d54-4615-8422-3cbc90de2327`、`66b08f88-2f1b-470d-a1a8-050c4dd1410a`；正式发布指针仍指向 `5bae41c0-fd2b-4179-9567-6cfc6a026daa`。
- 使用完全相同 run_spec 再次执行同一正式命令后，数据库快照 `db-after-first.json` 与 `db-after-replay.json` cmp=0，成功命名空间逐文件哈希清单 cmp=0，run_spec/两份缓存/旧根均不变；计数仍为 control_run=7、job_queue=7、screen_run=0、screen_score=0、hard_gate_evaluation=0、candidate_run=0、data_repair_queue=0、occurrence=3、formal publication=1、release_execution=6。没有新增 run/job/result/occurrence/publication。
- 结果边界：`research_only=true`、`production=false`、`publishable=false`、coverage=`not_full_market`、publication_status=`staging/not_published`；fixture/全市场正式发布指针未移动。PostgreSQL、control-api、scheduler、worker 全部 healthy；数据库仍为 `0008_l17_release_identity`；control-api HTTP health 正常且仅 loopback 18080，PostgreSQL 无宿主端口。

最终结论：`SEC_CONTROLLED_SAMPLE_ACCEPTED / READY_FOR_H1_MINIMAL_REVIEW / NOT_FULL_MARKET / NOT_PRODUCTION`。
