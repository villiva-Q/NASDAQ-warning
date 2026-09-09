# Massive Basic 首次接口测试与 C5 续接

> 后续用户已确认邮件发出，并明确批准 Basic 真实数据落盘、本地保存与研究重放测试。以 [扩展测试指令](2026-09-08_Basic研究能力与本地保存扩展测试.md) 为准；下文“仅内存测试”的限制是首次测试时的历史范围。

测试完成时间：2026-09-08 10:49 UTC。测试从 NUC 以 cargoq 身份执行，退出码 0。账户方案由用户说明为 Basic，本次未另查账户套餐信息。

## 凭据

用户已在仓库外配置 `/srv/cargoq/.market-data-secrets/massive_api_key`。实测 cargoq 可读，文件权限 0600。密钥只由进程读取，通过官方 Authorization Bearer 头发送至 api.massive.com；没有把值输出到聊天、命令参数或仓库。

## 实测结果

四次请求串行，间隔 13 秒，每次超时 25 秒，无重试。响应仅在内存解析，输出接口状态、字段名称、条数和分页标志，没有保存原始行情响应或价格值。

| 接口 | 请求参数 | HTTP / API 状态 | 实际结果 |
|---|---|---|---|
| `/v3/reference/tickers/AAPL` | `date=2024-11-01` | 200 / OK | 1 个对象，含 cik、composite_figi、share_class_figi、primary_exchange、currency_name、type 等字段 |
| `/v2/aggs/ticker/AAPL/range/1/day/2024-10-31/2024-11-01` | `adjusted=false&sort=asc&limit=10` | 200 / OK | 2 行，响应 adjusted=false；字段 c、h、l、n、o、t、v、vw |
| `/stocks/v1/splits` | `ticker=AAPL&limit=100` | 200 / OK | 5 行，字段 adjustment_type、execution_date、historical_adjustment_factor、id、split_from、split_to、ticker |
| `/stocks/v1/dividends` | `ticker=AAPL&limit=100` | 200 / OK | 57 行，含 cash_amount、currency、declaration_date、distribution_type、ex_dividend_date、frequency、historical_adjustment_factor、id、pay_date、record_date、split_adjusted_cash_amount、ticker |

四次响应均未出现 next_url。本次未核验公司行动的具体日期覆盖，不据此宣称全历史完整；未请求 KO 或 PARA；未触发限速错误，不构成限速错误处理测试。未验证生产数据库采用、报告导出或离线重放，不构成 C5 验收。

## 新的工作边界

用户表示自行发邮件咨询用途、保存限制、必要时的最低费用，同时希望使用 Basic 做测试；随后提供了凭据配置完成结果。当前没有收到邮件发送回执或提供方许可答复。不得将本次测试写成长期保存/衍生研究许可已确认。

现已证明真实请求可通，无须继续使用“Massive 未配置凭据、未发请求”作为当前阻塞。可以推进 Basic 接口接入、字段解析、错误处理、SEC 身份接线及相关定向测试。等待许可答复期间，真实接口验证以短时内存解析和技术诊断摘要为限；原始数据长期留存、持续研究使用、生产采用与离线重放许可仍待确认。不要自动订阅或采购，也不要替用户发送邮件。

现有真实 adapter 尚待实现，不能用本摘要或合成数据代替最终真实采用正例。对于必须保存真实响应才能完成的环节，列出具体待执行动作，收到用途确认后执行；不围绕同一未变化许可问题循环派发分析，也不要宣称 C5 完成。

## 已查明的历史语义

[官方身份文档](https://massive.com/docs/rest/stocks/tickers/ticker-overview)明确 date 对 SEC 派生信息使用报告期，示例中 2019-06-29 查询会纳入 2019-07-31 才提交的申报。故不能把 date 当作所有字段的公开时间；涉及 SEC 派生字段时用 SEC 提交/公开时间独立校验。不能将该局限泛化为所有身份字段必然无效。

继续区分当前取得的历史重建与当时留存快照；保持原固定 cutoff、旧 strict 契约及 PARA 负例，不填写未知公开/修订时间。HTTP 200 与字段存在只证明接口可用，不证明身份匹配正确或已达到历史证据规则。

鉴权方式依据：[官方 REST Quickstart](https://massive.com/docs/rest/quickstart)。免费入口依据：[官方免费访问说明](https://massive.com/knowledge-base/article/how-quickly-can-i-access-massives-market-date)。
