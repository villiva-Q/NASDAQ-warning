# NASDAQ Bubble Radar / 纳斯达克泡沫预警雷达

## English

NASDAQ Bubble Radar is a static dashboard for monitoring bubble pressure in NASDAQ / QQQ.

It is not designed to predict the exact top date. Instead, it combines valuation, liquidity, leverage, derivative speculation, breadth/concentration, and price confirmation into a trackable warning system.

### Live Site

After GitHub Pages is enabled, the dashboard should be available at:

```text
https://villiva-Q.github.io/NASDAQ-warning/
```

### Local Usage

```powershell
python scripts/update_data.py
python -m http.server 8000 -d docs
```

Then open:

```text
http://localhost:8000
```

### Manual Input Update

Some valuation, liquidity, derivative, breadth, and IBKR proxy fields are intentionally configured manually until stable APIs are connected.

To update them:

1. Edit `config/indicators.json`.
2. Update `_meta.manual_inputs_updated_at`.
3. Run:

```powershell
python scripts/update_data.py
```

4. Commit and push the refreshed files:

```powershell
git add config/indicators.json docs/data/dashboard.json
git commit -m "Update manual dashboard inputs"
git push
```

### GitHub Pages

This repository is prepared for GitHub Pages:

- Page: `docs/index.html`
- Data snapshot: `docs/data/dashboard.json`
- Scheduled update workflow: `.github/workflows/update-dashboard.yml`

Enable GitHub Pages in the repository settings:

```text
Settings -> Pages -> Deploy from a branch -> master / docs
```

### Model

The dashboard uses the following weighted score:

```text
Bubble Risk Score = 0.30 Valuation
                  + 0.20 Liquidity
                  + 0.20 Leverage/Derivatives
                  + 0.20 Breadth/Concentration
                  + 0.10 Price Confirmation
```

Risk states:

- `Green`: Normal
- `Yellow`: Watch
- `Orange`: De-risk
- `Red`: High alert

### Data Sources

Current MVP inputs:

- Yahoo Finance chart API: QQQ daily price history
- FINRA margin statistics: margin debt and customer free credit balances
- Yahoo Finance chart API: QQQ/TQQQ daily volume proxy
- Interactive Brokers monthly brokerage metrics: IBKR client margin loan proxy, configured manually
- Manual/configured indicators: NDX Forward P/E, P/S, 0DTE share, fund flow, and other metrics that do not yet have stable free real-time sources

Indicators without a reliable live source are marked as `manual` or `unavailable`. The dashboard does not pretend manual data is real-time.

### Important Note

This tool is a risk-monitoring dashboard, not investment advice and not a precise market-timing engine. Its best use is to detect when NASDAQ moves from "expensive but healthy" into "late-cycle, fragile, and dependent on marginal liquidity."

---

## 中文

NASDAQ Bubble Radar 是一个用于监控 NASDAQ / QQQ 泡沫压力的静态 Dashboard。

它的目标不是预测某一天精确见顶，而是把估值、流动性、杠杆、衍生品投机、市场广度/集中度和价格确认信号整合成一个可持续跟踪的预警系统。

### 在线页面

启用 GitHub Pages 后，Dashboard 预计可通过以下地址访问：

```text
https://villiva-Q.github.io/NASDAQ-warning/
```

### 本地使用

```powershell
python scripts/update_data.py
python -m http.server 8000 -d docs
```

然后打开：

```text
http://localhost:8000
```

### 手动输入更新

部分估值、流动性、衍生品、广度和 IBKR 代理指标，在接入稳定 API 前会作为手动配置项保留。

更新步骤：

1. 编辑 `config/indicators.json`。
2. 更新 `_meta.manual_inputs_updated_at`。
3. 运行：

```powershell
python scripts/update_data.py
```

4. 提交并推送刷新后的文件：

```powershell
git add config/indicators.json docs/data/dashboard.json
git commit -m "Update manual dashboard inputs"
git push
```

### GitHub Pages

本仓库已经按 GitHub Pages 静态站点结构准备：

- 页面文件：`docs/index.html`
- 数据快照：`docs/data/dashboard.json`
- 定时更新工作流：`.github/workflows/update-dashboard.yml`

在 GitHub 仓库设置中开启 Pages：

```text
Settings -> Pages -> Deploy from a branch -> master / docs
```

### 模型说明

Dashboard 使用以下加权总分：

```text
Bubble Risk Score = 0.30 Valuation
                  + 0.20 Liquidity
                  + 0.20 Leverage/Derivatives
                  + 0.20 Breadth/Concentration
                  + 0.10 Price Confirmation
```

风险状态：

- `Green`：正常
- `Yellow`：观察
- `Orange`：降风险
- `Red`：强警戒

### 数据来源

当前 MVP 使用：

- Yahoo Finance chart API：QQQ 日线价格
- FINRA margin statistics：保证金借款和客户现金余额
- Yahoo Finance chart API：QQQ/TQQQ 日频成交量代理
- Interactive Brokers 月度券商指标：IBKR 客户保证金贷款代理，当前以手动配置方式录入
- 手动/配置指标：NDX Forward P/E、P/S、0DTE 占比、资金流等尚未接入稳定免费实时源的指标

没有可靠实时数据源的指标会标记为 `manual` 或 `unavailable`。Dashboard 不会把手动数据伪装成实时数据。

### 重要说明

这个工具是风险监控面板，不是投资建议，也不是精确择时引擎。它最适合用来识别 NASDAQ 是否从“估值高但上涨健康”进入“泡沫晚期、结构脆弱、依赖边际流动性”的状态。
