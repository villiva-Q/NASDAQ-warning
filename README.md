# NASDAQ Bubble Radar / NASDAQ 泡沫预警雷达

NASDAQ Bubble Radar is a static dashboard for monitoring two different NASDAQ / QQQ regimes:

1. **Bubble Risk**: late-cycle top fragility.
2. **Bottom Readiness**: whether a selloff is moving from forced liquidation toward stabilization.

It is not designed to predict exact tops or bottoms. It is a disciplined monitoring tool that combines public data, slow leverage variables, and calibrated historical proxies.

## Obsidian Sync

This repository can be used directly as an Obsidian vault. Open the project root folder in Obsidian, then use Obsidian Sync or your existing vault-sync workflow to sync it across devices.

Recommended entry pages:

- [[00_项目主页]]
- [[跨设备同步说明]]

## Live Site

After GitHub Pages is enabled, the dashboard should be available at:

```text
https://villiva-Q.github.io/NASDAQ-warning/
```

## Local Usage

Install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Update data and start the local dashboard:

```powershell
python scripts/update_data.py
python -m http.server 8000 -d docs
```

Then open:

```text
http://localhost:8000
```

## Model Layers

### 1. Bubble Risk Score

The top-risk layer remains a 0-100 score. It monitors whether NASDAQ is becoming fragile near the top.

Current core score:

```text
Core Daily Score = 0.30 Price Confirmation
                 + 0.25 FINRA Margin Slow Variable
                 + 0.15 QQQ/TQQQ Daily Leverage Proxy
                 + 0.30 AI Fragility Overlay
```

The AI fragility overlay combines three late-cycle inputs:

- AI CapEx cycle: hyperscaler capex growth and acceleration/deceleration, using SEC Companyfacts for Microsoft, Amazon, Alphabet, and Meta as a free quarterly proxy.
- Liquidity drain: bank reserves, TGA, SOFR/RRP spread, and SRF usage, using FRED CSV and New York Fed Markets API sources.
- Options mechanical bid: 0DTE share, call premium proxy, and core call-volume heat. Free Cboe daily statistics are used as a proxy; exact 0DTE share and dealer gamma remain manual or paid-data problems.

Every metric is tagged with refresh frequency, last update, freshness, confidence, and whether it enters the score. Missing fields are excluded from the sub-score denominator; fully missing groups fall back to neutral.

Risk states:

- `Green`: Normal
- `Yellow`: Watch
- `Orange`: De-risk
- `Red`: High alert

### 2. Bottom Readiness Score

The bottom layer is a 0-20 score. It is only meaningful after a real QQQ drawdown.

It asks a different question:

```text
Has forced selling probably cooled enough for staged entry to become reasonable?
```

Public proxy signals include:

- QQQ drawdown zone
- QQQ short-term stabilization
- QQQ RSI oversold rebound
- VIX/VXN easing
- VIX/VIX3M term structure normalization
- Optional VIX9D/VIX3M short-vol term proxy when the free source is available
- Optional SKEW / put-call cooling proxy when the free source is available
- 10Y Treasury yield pressure easing
- BTC risk appetite stabilization
- TQQQ/QQQ volume ratio as a leveraged NASDAQ activity proxy
- QQEW/QQQ equal-weight breadth repair
- QQQ/SPY relative strength
- FINRA margin debt cooling, aligned with a 21-day publication lag

Missing optional free signals are excluded from the score denominator. They are not treated as bearish.

## Bottom Calibration

Run:

```powershell
python scripts/backtest_bottom_framework.py
```

Outputs:

- `docs/nasdaq_bottom_framework_backtest.md`
- `data/nasdaq_bottom_backtest_summary.json`
- `data/nasdaq_bottom_backtest_entries.csv`
- `data/nasdaq_bottom_walk_forward_entries.csv`
- `data/nasdaq_bottom_scored_history.csv`

## Micron Canary

Micron is tracked as an AI-memory canary:

```powershell
python scripts/micron_canary_score.py
```

The score combines MU price heat, profit-cycle heat, demand lock-in, peak-earnings valuation-trap risk, and broader liquidity sensitivity. It is designed to answer a different question than a static P/E ratio:

```text
Is Micron showing the kind of extreme upstream profitability and demand lock-in that often appears near a capex-cycle peak?
```

The dashboard automatically embeds the Micron canary snapshot when `scripts/update_data.py` is run.

The backtest uses QQQ drawdown events and calibrates score thresholds. FINRA margin data is lagged by 21 days to avoid look-ahead bias.

Current practical interpretation:

- `0-7`: Wait; liquidation risk is usually unresolved.
- `8-11`: Observe; small test positions only, if any.
- `12-13`: Watch zone; bottom process may be forming.
- `13+`: Staged-entry zone, but only after a meaningful drawdown and price confirmation.

## Data Sources

Current free sources:

- Yahoo Finance chart API: QQQ, TQQQ, SPY, QQEW, VIX, VIX3M, VXN, TNX, BTC-USD
- Yahoo Finance chart API: MU
- SEC companyfacts API: Micron financial statements
- SEC Companyfacts API: MSFT, AMZN, GOOGL, META hyperscaler CapEx proxy
- FRED CSV: WRESBAL, WTREGEN, SOFR, RRPONTSYAWARD
- New York Fed Markets API: repo / SRF operation results
- Cboe Daily Market Statistics: SPX/SPXW call-put volume proxy
- Yahoo optional symbols when available: VIX9D, SKEW, put/call proxy
- FINRA margin statistics: aggregate margin debt and customer free credit balances
- Manual/configured indicators: valuation, broad derivative speculation, breadth, exact 0DTE stress share, Micron demand-lock-in, and IBKR proxy fields in `config/indicators.json`

Indicators without a reliable source are marked manual or optional. The dashboard does not pretend manual or missing data is real-time.

## Data Quality

The dashboard includes a data quality panel:

- Freshness: each metric is checked against its cadence, such as daily, weekly, monthly, quarterly, or manual.
- Confidence: official sources score highest; Yahoo and Cboe proxies are medium; manual fields score lower and decay when stale.
- Coverage: the panel reports how many metrics are automatic vs manual, and flags stale or low-confidence scored inputs.

## Manual Input Update

Some valuation, liquidity, derivative, breadth, and IBKR proxy fields are intentionally configured manually until stable APIs are connected.

To update them:

1. Edit `config/indicators.json`.
2. Update `_meta.manual_inputs_updated_at`.
3. Run:

```powershell
python scripts/update_data.py
```

4. Commit and push the refreshed files if you are using Git.

## GitHub Pages

This repository is prepared for GitHub Pages:

- Page: `docs/index.html`
- Data snapshot: `docs/data/dashboard.json`
- Scheduled update workflow: `.github/workflows/update-dashboard.yml`

Enable GitHub Pages in the repository settings:

```text
Settings -> Pages -> Deploy from a branch -> master / docs
```

## 中文说明

这个项目是一个双层 NASDAQ / QQQ 监控面板：

1. **泡沫风险**：判断顶部脆弱性是否升高。
2. **底部就绪度**：判断一次下跌是否正在从强制清算转向稳定。

它不是精确预测顶部或底部的工具，而是一个辅助判断框架。顶部模型看估值、价格延伸、FINRA 保证金和 QQQ/TQQQ 杠杆交易代理；底部模型看回撤后是否出现波动率退潮、利率压力缓和、加密风险偏好企稳、杠杆降温、市场广度修复和价格止跌。

底部模型不直接使用付费的 dealer gamma、put wall、CTA flow 数据，而是用公开代理变量替代。FINRA 月度数据会按 21 天发布滞后对齐，避免回测中的未来函数。

重要提醒：这个 dashboard 是研究和风控辅助工具，不是投资建议，也不是自动买卖信号。
