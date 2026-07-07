# NASDAQ Bottom Framework Backtest

Generated: 2026-07-07T02:42:37+00:00
History: 2017-07-06T00:00:00 to 2026-07-06T00:00:00
Proxy: QQQ. Drawdown events: 19.

## Method

The score is a 0-20 bottom-readiness score. It is not a prediction of the exact low.
It uses public proxies for the framework: QQQ price damage/stabilization, VIX/VIX3M term structure, VXN/VIX easing, TNX rate pressure, BTC risk appetite, TQQQ/QQQ volume leverage, QQEW/QQQ breadth, and QQQ/SPY relative strength.

Private or paid indicators such as dealer GEX, gamma flip, put wall, and CTA flow are not directly backtested here. They are represented by price, volatility, trend, and volume proxies. FINRA margin data is aligned with a 21-day publication lag to avoid look-ahead bias.

## Threshold Calibration

| Threshold | Triggered Events | Avg Days From Low | 21D Avg | 21D Hit | 63D Avg | 63D Hit |
|---:|---:|---:|---:|---:|---:|---:|
| 8 | 19/19 | -26.0 | 0.8% | 55.6% | 6.8% | 88.9% |
| 9 | 19/19 | -24.6 | 0.5% | 50.0% | 6.6% | 88.9% |
| 10 | 19/19 | -23.0 | 0.9% | 50.0% | 6.9% | 88.9% |
| 11 | 18/19 | -19.1 | 3.6% | 58.8% | 8.6% | 76.5% |
| 12 | 16/19 | -17.9 | 3.2% | 68.8% | 7.7% | 81.2% |
| 13 | 12/19 | -20.6 | 4.7% | 83.3% | 10.2% | 75.0% |
| 14 | 4/19 | -69.0 | 1.2% | 50.0% | 9.3% | 75.0% |
| 15 | 3/19 | -63.3 | -1.7% | 33.3% | 9.3% | 66.7% |
| 16 | 2/19 | -72.0 | 0.9% | 50.0% | 8.2% | 50.0% |
| 17 | 1/19 | 71.0 | 9.2% | 100.0% | 13.7% | 100.0% |

## Walk-Forward Check

For each event after the first four, the threshold is selected from prior events only, then applied to the next event.

Tested events: 15. Triggered: 9.
21D average return: 3.9%. 21D hit rate: 77.8%.
63D average return: 9.2%. 63D hit rate: 66.7%.

## Event Lows

| Event | Start | Low Date | End | Low Drawdown |
|---:|---|---|---|---:|
| 1 | 2018-02-05T00:00:00 | 2018-02-08T00:00:00 | 2018-02-23T00:00:00 | -10.2% |
| 2 | 2018-03-22T00:00:00 | 2018-04-02T00:00:00 | 2018-06-01T00:00:00 | -10.5% |
| 3 | 2018-10-10T00:00:00 | 2018-12-24T00:00:00 | 2019-03-21T00:00:00 | -22.8% |
| 4 | 2019-05-13T00:00:00 | 2019-06-03T00:00:00 | 2019-06-20T00:00:00 | -11.0% |
| 5 | 2019-08-05T00:00:00 | 2019-08-05T00:00:00 | 2019-09-05T00:00:00 | -7.5% |
| 6 | 2020-02-24T00:00:00 | 2020-03-16T00:00:00 | 2020-05-29T00:00:00 | -28.6% |
| 7 | 2020-09-04T00:00:00 | 2020-09-23T00:00:00 | 2020-11-27T00:00:00 | -12.7% |
| 8 | 2021-02-25T00:00:00 | 2021-03-08T00:00:00 | 2021-04-05T00:00:00 | -10.9% |
| 9 | 2021-05-12T00:00:00 | 2021-05-12T00:00:00 | 2021-06-04T00:00:00 | -7.3% |
| 10 | 2021-09-30T00:00:00 | 2021-10-04T00:00:00 | 2021-10-19T00:00:00 | -7.6% |
| 11 | 2022-01-13T00:00:00 | 2022-11-03T00:00:00 | 2023-05-10T00:00:00 | -35.1% |
| 12 | 2023-08-16T00:00:00 | 2023-08-18T00:00:00 | 2023-09-05T00:00:00 | -7.2% |
| 13 | 2023-09-21T00:00:00 | 2023-10-26T00:00:00 | 2023-11-10T00:00:00 | -10.8% |
| 14 | 2024-04-19T00:00:00 | 2024-04-19T00:00:00 | 2024-05-06T00:00:00 | -7.1% |
| 15 | 2024-07-24T00:00:00 | 2024-08-07T00:00:00 | 2024-10-09T00:00:00 | -13.6% |
| 16 | 2025-02-27T00:00:00 | 2025-04-08T00:00:00 | 2025-06-04T00:00:00 | -22.8% |
| 17 | 2025-11-18T00:00:00 | 2025-11-20T00:00:00 | 2025-12-03T00:00:00 | -7.9% |
| 18 | 2026-03-13T00:00:00 | 2026-03-30T00:00:00 | 2026-04-14T00:00:00 | -12.0% |
| 19 | 2026-06-10T00:00:00 | 2026-06-10T00:00:00 | 2026-06-15T00:00:00 | -7.0% |

## Suggested Calibration

The best simple threshold in this run is `13` out of 20.

Practical interpretation:

- Below 8: liquidation risk is usually still unresolved.
- 8-11: watch zone or very small test position.
- 12-14: bottom process is often forming; staged entry becomes reasonable.
- 15+: confirmation is stronger, but entries tend to arrive later and may miss early rebounds.

Use the threshold with event context. A high score during a shallow pullback is less meaningful than a high score after a 6%+ QQQ drawdown.
