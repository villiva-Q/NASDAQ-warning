# NASDAQ Bubble Radar

一个用于监控 NASDAQ / QQQ 泡沫水平的静态 Dashboard。

目标不是预测某一天见顶，而是把估值、资金、杠杆、投机结构、价格行为压缩成一个可跟踪的预警面板。

## 本地使用

```powershell
python scripts/update_data.py
python -m http.server 8000 -d docs
```

然后打开：

```text
http://localhost:8000
```

## GitHub Pages

本项目已经按 GitHub Pages 静态站点结构准备：

- 页面文件：`docs/index.html`
- 数据快照：`docs/data/dashboard.json`
- 定时更新：`.github/workflows/update-dashboard.yml`

在 GitHub 仓库中开启 Pages，选择 `Deploy from a branch`，目录选择 `main / docs`。

## 模型说明

总分：

```text
Bubble Risk Score = 0.30 Valuation
                  + 0.20 Liquidity
                  + 0.20 Leverage/Derivatives
                  + 0.20 Breadth/Concentration
                  + 0.10 Price Confirmation
```

状态：

- `Green`：正常
- `Yellow`：观察
- `Orange`：降风险
- `Red`：强警戒

## 数据口径

当前 MVP 使用：

- Yahoo Finance chart API：QQQ 日线价格
- FINRA margin statistics：保证金借款、客户现金余额
- 手动/配置项：NDX Forward P/E、P/S、0DTE、资金流等尚未接入稳定免费实时源的指标

没有可靠数据的指标会被标记为 `manual` 或 `unavailable`，不会伪装成实时数据。
