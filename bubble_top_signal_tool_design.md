# 泡沫顶部信号捕捉工具设计

日期：2026-05-27

## 1. 工具目标

目标不是预测某一天见顶，而是提前识别市场从“高估但健康上涨”进入“泡沫晚期、边际资金不足、去杠杆风险上升”的状态。

核心输出：

1. 泡沫温度：估值是否处在历史极端区。
2. 资金承接：新增资金是否还能支撑估值继续扩张。
3. 杠杆脆弱性：上涨是否越来越依赖借钱和短线交易。
4. 顶部行为：价格是否出现加速、背离、放量滞涨或反转。
5. 决策状态：正常、观察、降风险、强警戒。

一句话定义：

`Bubble Top Signal = 高估值 + 边际资金衰减 + 杠杆/投机升高 + 价格顶部行为`

## 2. 总体架构

工具分五个信号簇：

| 信号簇 | 作用 | 权重建议 |
| --- | --- | ---: |
| Valuation 估值压力 | 判断泡沫高度 | 25% |
| Liquidity 资金增量 | 判断新增买盘是否变弱 | 25% |
| Leverage 杠杆压力 | 判断强制卖出风险 | 20% |
| Speculation 投机结构 | 判断短线化和脆弱性 | 15% |
| Price Action 顶部行为 | 判断是否开始转弱 | 15% |

最终得分：

`Bubble Risk Score = 0.25V + 0.25Lq + 0.20Lv + 0.15S + 0.15P`

每个子模块打 0-100 分。分数越高，泡沫顶部风险越高。

## 3. 信号簇设计

### 3.1 Valuation 估值压力

目的：判断价格相对基本面是否过度。

建议指标：

| 指标 | 说明 | 信号方向 |
| --- | --- | --- |
| Shiller CAPE | 长周期市盈率 | 越高越危险 |
| Forward P/E | 未来 12 个月预期市盈率 | 越高越危险 |
| Buffett Indicator | 美国总市值/GDP | 越高越危险 |
| Price/Sales | 尤其适合科技股泡沫 | 越高越危险 |
| Equity Risk Premium | 盈利收益率 - 10Y Treasury | 越低越危险 |

评分方式：

用历史百分位打分。比如 CAPE 位于历史 95 分位，则该指标得 95 分。

估值模块得分：

`V = average(percentile(CAPE), percentile(Forward PE), percentile(Buffett), percentile(P/S), inverse_percentile(ERP))`

解释：

估值高本身不是顶部信号，只是泡沫燃料。估值模块高分只能说明“未来长期收益差、市场对坏消息敏感”，不能单独触发强警戒。

### 3.2 Liquidity 资金增量

目的：判断边际资金是否还能继续推高估值。

建议指标：

| 指标 | 说明 | 信号方向 |
| --- | --- | --- |
| Equity Fund Flow | 股票基金/ETF 净流入 | 流入放缓或转负危险 |
| Money Market Fund Assets | 货币基金资金池 | 若股市涨而货基不流出，承接不足 |
| Corporate Buybacks | 企业回购金额 | 回购放缓危险 |
| Fed Liquidity Proxy | Fed balance sheet - TGA - RRP | 流动性下降危险 |
| Credit Spread | HY OAS / IG OAS | 利差走阔危险 |
| Foreign Capital Flow | 海外资金流入美股/美债 | 股市依赖外资时尤其重要 |

核心不是看绝对流入，而是看“估值扩张需要的资金”与“实际新增资金”的差距。

建议构造：

`Funding Gap = Market Cap Change - Net Equity Flow - Buybacks - Margin Debt Change`

简化版：

`Funding Stress = percentile(3M Market Cap Growth - 3M Net Flow Proxy)`

解释：

如果市值继续快速膨胀，但可见新增资金没有同步增加，说明上涨更多来自估值重定价和杠杆，而非稳定现金买盘。

### 3.3 Leverage 杠杆压力

目的：判断市场上涨是否越来越依赖借贷。

建议指标：

| 指标 | 说明 | 信号方向 |
| --- | --- | --- |
| FINRA Margin Debt | 保证金借款余额 | 越高越危险 |
| Margin Debt YoY | 保证金同比增速 | 快速上升危险 |
| Debit / Free Credit | 保证金借款 / 客户现金余额 | 越高越危险 |
| Leveraged ETF AUM | TQQQ/UPRO 等杠杆 ETF 规模 | 越高越危险 |
| Prime Brokerage Leverage | 对冲基金融资杠杆 | 越高越危险 |

关键组合信号：

`Leverage Late-Cycle Signal = Margin Debt Percentile > 90 AND Debit/FreeCredit Percentile > 90 AND Price Momentum > 0`

解释：

杠杆只有在上涨末期才最危险。熊市底部的高杠杆和牛市加速期的高杠杆意义不同，所以必须和价格趋势、估值一起看。

### 3.4 Speculation 投机结构

目的：判断市场参与者是否越来越短线化、彩票化。

建议指标：

| 指标 | 说明 | 信号方向 |
| --- | --- | --- |
| 0DTE Share | SPX/QQQ/NDX 0DTE 成交占比 | 越高越危险 |
| Options Put/Call | 期权看涨情绪 | Call 过热危险 |
| Single Stock Option Volume | 个股期权成交 | 越高越危险 |
| IPO First-Day Return | IPO 首日涨幅 | 越高越危险 |
| Meme/High Beta Basket | 高 beta/亏损科技股表现 | 过强危险 |
| Retail Trading Share | 散户交易占比 | 过高危险 |

关键组合信号：

`Speculation Exhaustion = 0DTE high + call volume high + high-beta underperforms index`

解释：

投机高涨不等于马上跌。更危险的是：投机指标仍高，但高 beta 股票开始跑输，说明边际投机资金已经推不动最敏感资产。

### 3.5 Price Action 顶部行为

目的：从价格本身确认顶部风险是否开始兑现。

建议指标：

| 指标 | 说明 | 信号方向 |
| --- | --- | --- |
| 12M Momentum | 长趋势是否仍向上 | 向上但过热 |
| 3M Acceleration | 短期是否加速上涨 | 过快危险 |
| Breadth Divergence | 指数创新高但成分股参与度下降 | 危险 |
| New Highs - New Lows | 创新高数量减弱 | 危险 |
| Equal Weight / Cap Weight | 等权指数跑输市值加权 | 集中度风险 |
| Volatility Divergence | 指数新高但 VIX/Skew 不再下降 | 危险 |
| Failed Breakout | 创新高后快速跌回 | 高危 |

关键确认信号：

`Top Confirmation = Valuation high + Liquidity weakening + Breadth divergence + Failed breakout`

解释：

价格模块不应过早触发风险。它更像最后确认器，用于把“泡沫高温”升级成“顶部可能正在发生”。

## 4. 告警分层

建议输出四档：

| 等级 | 总分 | 状态 | 决策含义 |
| --- | ---: | --- | --- |
| Green | 0-39 | 正常 | 估值或资金没有明显系统性风险 |
| Yellow | 40-59 | 观察 | 市场偏热，开始跟踪资金和广度 |
| Orange | 60-74 | 降风险 | 泡沫晚期概率上升，减少杠杆和集中仓位 |
| Red | 75-100 | 强警戒 | 顶部脆弱性高，准备对冲/止盈/降低 beta |

强警戒触发条件不只看总分，还要满足至少三个模块高危：

`Red Trigger = Total Score > 75 AND count(module_score > 70) >= 3`

防止单一估值指标过高导致过早报警。

## 5. 顶部信号组合

### 5.1 早期泡沫信号

`Valuation > 80 AND Price Momentum > 70`

含义：市场贵，而且还在强势上涨。不是卖出信号，是风险观察信号。

### 5.2 泡沫晚期信号

`Valuation > 85 AND Leverage > 75 AND Speculation > 75`

含义：上涨越来越依赖杠杆和投机。应减少杠杆、降低单一主题集中度。

### 5.3 顶部脆弱信号

`Valuation > 85 AND Liquidity < 40 AND Price Breadth < 40`

含义：估值高，但资金和市场广度转弱。顶部风险明显上升。

### 5.4 顶部确认信号

`Bubble Risk Score > 75 AND Failed Breakout = True AND Credit Spread widening`

含义：价格行为开始验证泡沫压力。进入强警戒。

### 5.5 崩盘前高危信号

`Leverage high AND Liquidity falling AND Volatility rising AND Index below 50DMA`

含义：从“高估泡沫”进入“去杠杆可能启动”。

## 6. 工具输出格式

建议每日或每周生成一份信号卡：

```text
Bubble Top Radar
Date: 2026-05-27
Market: NDX / QQQ / S&P 500

Overall Score: 72 / 100
Status: Orange - 降风险

Module Scores:
Valuation: 91
Liquidity: 48
Leverage: 82
Speculation: 77
Price Action: 61

Key Warnings:
- Valuation is in historical extreme zone.
- Margin leverage is above 90th percentile.
- 0DTE / option speculation remains elevated.
- Breadth is weakening while index remains near high.

Decision Notes:
- Do not add leverage.
- Reduce high-beta concentration.
- Consider staged hedges if price fails new highs.
- Upgrade to Red if index loses 50DMA with credit spread widening.
```

## 7. 数据频率

| 数据 | 频率 | 用途 |
| --- | --- | --- |
| 指数价格、广度、波动率 | 日频 | 顶部确认 |
| 期权成交、0DTE、Put/Call | 日频/周频 | 投机结构 |
| ETF/基金流入 | 周频 | 资金增量 |
| FINRA margin debt | 月频 | 杠杆压力 |
| GDP/巴菲特指标/CAPE | 月频/季频 | 估值压力 |
| 回购、海外流入 | 月频/季频 | 资金承接 |

工具不需要所有数据同频。做法是：

1. 高频价格信号每日更新。
2. 月度/季度宏观和杠杆信号在新数据发布后锁定。
3. 最终分数使用最近可得数据。

## 8. 设计原则

### 8.1 不用单点预测

不输出“某点必崩”，只输出风险状态和触发条件。

### 8.2 强制使用组合信号

至少需要估值、资金/杠杆、价格行为三类信号共同确认，才升级为强警戒。

### 8.3 区分泡沫和顶部

泡沫可以持续很久。顶部信号必须包含边际资金变弱或价格行为转弱。

### 8.4 指标全部百分位化

不同指标单位不同，全部转换成历史百分位，减少口径冲突。

### 8.5 输出可执行动作

每个等级对应决策动作，而不是只给分数。

## 9. 最小可行版本

如果先做 MVP，只需要 12 个指标：

| 模块 | MVP 指标 |
| --- | --- |
| 估值 | CAPE、Forward P/E、Buffett Indicator |
| 资金 | ETF/fund flow、Fed liquidity proxy、HY credit spread |
| 杠杆 | FINRA margin debt、Debit/free credit |
| 投机 | 0DTE share、Put/Call ratio |
| 价格 | 200DMA distance、Breadth divergence |

MVP 输出：

1. 总分。
2. 五个模块分。
3. 四档状态。
4. 最近触发/解除的信号。
5. 决策建议。

## 10. 推荐决策规则

| 状态 | 仓位动作 | 风控动作 |
| --- | --- | --- |
| Green | 正常配置 | 正常再平衡 |
| Yellow | 不追高 | 监控广度和资金流 |
| Orange | 降低杠杆、降低高 beta | 分批止盈、建立轻度保护 |
| Red | 明显降低风险暴露 | 对冲、严格止损、避免补跌中加杠杆 |

注意：该工具不直接替代投资决策。它的最佳用途是提前提醒“继续上涨的代价变高，失败后的下跌速度会变快”。
