from __future__ import annotations

import json
import math
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REPORT_DIR = ROOT / "docs"
YAHOO_CHART = (
    "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    "?range={range}&interval=1d&events=history&includeAdjustedClose=true"
)


SYMBOLS = {
    "qqq": "QQQ",
    "tqqq": "TQQQ",
    "qqew": "QQEW",
    "spy": "SPY",
    "vix": "^VIX",
    "vix9d": "^VIX9D",
    "vix3m": "^VIX3M",
    "vxn": "^VXN",
    "skew": "^SKEW",
    "cpc": "^CPC",
    "tnx": "^TNX",
    "btc": "BTC-USD",
}


def fetch_json(url: str, timeout: int = 45) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "NASDAQBottomBacktest/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_yahoo(symbol: str, range_: str = "10y") -> pd.DataFrame:
    encoded = urllib.parse.quote(symbol, safe="")
    cache = DATA_DIR / f"yahoo-{symbol.lower().replace('^', '')}-{range_}.json"
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    url = YAHOO_CHART.format(symbol=encoded, range=range_)
    try:
        payload = fetch_json(url)
        cache.write_text(json.dumps(payload), encoding="utf-8")
    except Exception:
        if not cache.exists():
            return pd.DataFrame(columns=["close", "volume"])
        payload = json.loads(cache.read_text(encoding="utf-8"))

    result = payload["chart"].get("result", [None])[0]
    if not result:
        return pd.DataFrame(columns=["close", "volume"])
    quote = result["indicators"]["quote"][0]
    adj = result["indicators"].get("adjclose", [{}])[0].get("adjclose")
    rows = []
    for idx, ts in enumerate(result.get("timestamp", [])):
        close = adj[idx] if adj and adj[idx] is not None else quote["close"][idx]
        if close is None:
            continue
        rows.append(
            {
                "date": datetime.fromtimestamp(ts, tz=timezone.utc).date(),
                "close": float(close),
                "volume": float(quote["volume"][idx] or 0),
            }
        )
    df = pd.DataFrame(rows).drop_duplicates("date").set_index("date").sort_index()
    df.index = pd.to_datetime(df.index).astype("datetime64[ns]")
    return df


def load_finra_history() -> pd.DataFrame:
    xlsx = DATA_DIR / "finra-margin-statistics.xlsx"
    if not xlsx.exists():
        return pd.DataFrame()
    df = pd.read_excel(xlsx)
    df.columns = ["month", "debit", "free_cash", "free_margin"]
    df = df.dropna(subset=["month", "debit"]).copy()
    df["month"] = pd.to_datetime(df["month"]).dt.to_period("M").dt.to_timestamp("M")
    df = df.sort_values("month")
    df["debit"] = df["debit"].astype(float)
    df["free_cash"] = df["free_cash"].astype(float)
    df["free_margin"] = df["free_margin"].astype(float)
    df["debit_to_free_cash"] = df["debit"] / df["free_cash"].replace(0, np.nan)
    df["margin_debt_pct_lookback"] = df["debit"].expanding().rank(pct=True)
    df["margin_ratio_pct_lookback"] = df["debit_to_free_cash"].expanding().rank(pct=True)
    df["margin_mom"] = df["debit"].pct_change()
    df["margin_3m"] = df["debit"].pct_change(3)
    # FINRA usually publishes around the third week after month-end. Use a
    # conservative 21-day lag so the backtest does not peek at future data.
    df["available_date"] = (df["month"] + pd.Timedelta(days=21)).astype("datetime64[ns]")
    return df.set_index("available_date")


def rsi(series: pd.Series, window: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(window).mean()
    loss = (-delta.clip(upper=0)).rolling(window).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def score_bool(condition: pd.Series | bool) -> pd.Series | int:
    if isinstance(condition, pd.Series):
        return condition.fillna(False).astype(int) * 2
    return 2 if condition else 0


def score_three(full: pd.Series, partial: pd.Series) -> pd.Series:
    return pd.Series(np.where(full.fillna(False), 2, np.where(partial.fillna(False), 1, 0)), index=full.index)


def build_dataset(range_: str = "10y") -> pd.DataFrame:
    frames = {}
    qqq_trading_dates = None
    for name, symbol in SYMBOLS.items():
        df = fetch_yahoo(symbol, range_)
        if name == "qqq":
            qqq_trading_dates = df.index
        frames[f"{name}_close"] = df["close"]
        frames[f"{name}_volume"] = df["volume"]

    data = pd.DataFrame(frames).sort_index()
    data = data.ffill()
    data = data.loc[qqq_trading_dates]
    data = data[data["qqq_close"].notna()]

    qqq = data["qqq_close"]
    data["qqq_ret_1d"] = qqq.pct_change()
    data["qqq_ret_5d"] = qqq.pct_change(5)
    data["qqq_ret_21d"] = qqq.pct_change(21)
    data["qqq_fwd_21d"] = qqq.shift(-21) / qqq - 1
    data["qqq_fwd_63d"] = qqq.shift(-63) / qqq - 1
    data["qqq_sma5"] = qqq.rolling(5).mean()
    data["qqq_sma10"] = qqq.rolling(10).mean()
    data["qqq_sma20"] = qqq.rolling(20).mean()
    data["qqq_sma50"] = qqq.rolling(50).mean()
    data["qqq_sma200"] = qqq.rolling(200).mean()
    data["qqq_high252"] = qqq.rolling(252).max()
    data["qqq_drawdown"] = qqq / data["qqq_high252"] - 1
    data["qqq_rsi14"] = rsi(qqq)
    data["realized_vol_10d"] = data["qqq_ret_1d"].rolling(10).std() * math.sqrt(252)
    data["realized_vol_5d"] = data["qqq_ret_1d"].rolling(5).std() * math.sqrt(252)

    data["vix_ratio_3m"] = data["vix_close"] / data["vix3m_close"]
    data["vix9d_ratio_3m"] = data["vix9d_close"] / data["vix3m_close"]
    data["vix_change_5d"] = data["vix_close"].diff(5)
    data["vxn_change_5d"] = data["vxn_close"].diff(5)
    data["skew_change_5d"] = data["skew_close"].diff(5)
    data["cpc_change_5d"] = data["cpc_close"].diff(5)
    data["tnx_change_5d"] = data["tnx_close"].diff(5)
    data["btc_ret_5d"] = data["btc_close"].pct_change(5)
    data["btc_above_5d_low"] = data["btc_close"] / data["btc_close"].rolling(5).min() - 1
    data["tqqq_qqq_volume_ratio"] = data["tqqq_volume"] / data["qqq_volume"].replace(0, np.nan)
    data["tqqq_ratio_pct_252"] = data["tqqq_qqq_volume_ratio"].rolling(252).rank(pct=True)
    data["qqew_rel_qqq_10d"] = (data["qqew_close"] / data["qqq_close"]).pct_change(10)
    data["qqq_rel_spy_5d"] = (data["qqq_close"] / data["spy_close"]).pct_change(5)

    finra = load_finra_history()
    if not finra.empty:
        merged = pd.merge_asof(
            data.reset_index().sort_values("date"),
            finra.reset_index().sort_values("available_date"),
            left_on="date",
            right_on="available_date",
            direction="backward",
        ).set_index("date")
        for col in [
            "debit",
            "debit_to_free_cash",
            "margin_debt_pct_lookback",
            "margin_ratio_pct_lookback",
            "margin_mom",
            "margin_3m",
        ]:
            data[f"finra_{col}"] = merged[col]
    else:
        data["finra_margin_debt_pct_lookback"] = np.nan
        data["finra_margin_ratio_pct_lookback"] = np.nan
        data["finra_margin_mom"] = np.nan
        data["finra_margin_3m"] = np.nan
    return data


def add_scores(data: pd.DataFrame) -> pd.DataFrame:
    df = data.copy()

    # 0-2 for each signal. This is a bottom-readiness score, not a top-risk score.
    df["s_drawdown_zone"] = score_three(df["qqq_drawdown"] <= -0.10, df["qqq_drawdown"] <= -0.06)
    df["s_price_stabilizing"] = score_three(
        (df["qqq_close"] > df["qqq_sma10"]) & (df["qqq_ret_5d"] > 0),
        (df["qqq_close"] > df["qqq_sma5"]) | (df["qqq_ret_5d"] > -0.01),
    )
    df["s_oversold_rebound"] = score_three(
        (df["qqq_rsi14"].shift(5).rolling(5).min() < 30) & (df["qqq_rsi14"] > 35),
        df["qqq_rsi14"] < 40,
    )
    df["s_vol_easing"] = score_three(
        (df["vix_change_5d"] < 0) & (df["vxn_change_5d"] < 0),
        (df["vix_change_5d"] < 0) | (df["vxn_change_5d"] < 0),
    )
    df["s_vol_term"] = score_three(df["vix_ratio_3m"] < 0.95, df["vix_ratio_3m"] < 1.00)
    df["s_short_vol_term"] = score_three(df["vix9d_ratio_3m"] < 0.92, df["vix9d_ratio_3m"] < 0.98)
    df.loc[df["vix9d_ratio_3m"].isna(), "s_short_vol_term"] = np.nan
    df["s_options_skew_cooling"] = score_three(
        (df["skew_change_5d"] < 0) & (df["cpc_change_5d"] < 0),
        (df["skew_change_5d"] < 0) | (df["cpc_change_5d"] < 0),
    )
    df.loc[df[["skew_change_5d", "cpc_change_5d"]].isna().all(axis=1), "s_options_skew_cooling"] = np.nan
    df["s_rate_easing"] = score_three(df["tnx_change_5d"] <= -0.05, df["tnx_change_5d"] <= 0.02)
    df["s_crypto_stable"] = score_three(
        (df["btc_ret_5d"] > 0) & (df["btc_above_5d_low"] > 0.03),
        (df["btc_ret_5d"] > -0.03) | (df["btc_above_5d_low"] > 0.01),
    )
    df["s_leverage_cooling"] = score_three(
        (df["tqqq_ratio_pct_252"].shift(1) > 0.80)
        & (df["tqqq_qqq_volume_ratio"] < df["tqqq_qqq_volume_ratio"].rolling(5).mean()),
        df["tqqq_ratio_pct_252"] > 0.70,
    )
    df["s_breadth_recovering"] = score_three(df["qqew_rel_qqq_10d"] > 0.01, df["qqew_rel_qqq_10d"] > -0.005)
    df["s_tech_relative"] = score_three(df["qqq_rel_spy_5d"] > 0.005, df["qqq_rel_spy_5d"] > -0.005)
    df["s_finra_margin_cooling"] = score_three(
        (df["finra_margin_debt_pct_lookback"] > 0.75) & (df["finra_margin_3m"] < 0),
        (df["finra_margin_debt_pct_lookback"] > 0.75) & (df["finra_margin_mom"] <= 0.01),
    )
    df.loc[df["finra_margin_debt_pct_lookback"].isna(), "s_finra_margin_cooling"] = np.nan

    score_cols = [c for c in df.columns if c.startswith("s_")]
    available_score_max = df[score_cols].notna().sum(axis=1) * 2
    df["bottom_score_raw"] = df[score_cols].sum(axis=1, skipna=True)
    df["bottom_score"] = df["bottom_score_raw"] / available_score_max.replace(0, np.nan) * 20
    df["bottom_score_pct"] = df["bottom_score"] / 20 * 100
    df["bottom_score_available_signals"] = df[score_cols].notna().sum(axis=1)
    return df


@dataclass
class Event:
    event_id: int
    start: pd.Timestamp
    end: pd.Timestamp
    low_date: pd.Timestamp
    low_drawdown: float


def find_drawdown_events(df: pd.DataFrame, min_drawdown: float = -0.06, recovered_to: float = -0.02) -> list[Event]:
    events = []
    in_event = False
    start = None
    last_event_end_idx = -1
    dates = list(df.index)
    for i, date in enumerate(dates):
        dd = df.at[date, "qqq_drawdown"]
        if not in_event and dd <= min_drawdown and i - last_event_end_idx > 10:
            in_event = True
            start = date
        elif in_event and dd >= recovered_to:
            end = date
            window = df.loc[start:end]
            low_date = window["qqq_drawdown"].idxmin()
            events.append(Event(len(events) + 1, start, end, low_date, float(window.at[low_date, "qqq_drawdown"])))
            in_event = False
            last_event_end_idx = i
    if in_event and start is not None:
        end = dates[-1]
        window = df.loc[start:end]
        low_date = window["qqq_drawdown"].idxmin()
        events.append(Event(len(events) + 1, start, end, low_date, float(window.at[low_date, "qqq_drawdown"])))
    return events


def evaluate_thresholds(df: pd.DataFrame, events: list[Event], thresholds: range = range(8, 18)) -> tuple[pd.DataFrame, pd.DataFrame]:
    event_rows = []
    threshold_rows = []

    for threshold in thresholds:
        entries = []
        for event in events:
            window = df.loc[event.start:event.end].copy()
            candidates = window[window["bottom_score"] >= threshold]
            if candidates.empty:
                entries.append(
                    {
                        "event_id": event.event_id,
                        "threshold": threshold,
                        "entry_date": None,
                        "triggered": False,
                        "low_date": event.low_date.isoformat(),
                        "days_from_low": None,
                        "entry_drawdown": None,
                        "low_drawdown": event.low_drawdown,
                        "fwd_21d": None,
                        "fwd_63d": None,
                    }
                )
                continue
            entry_date = candidates.index[0]
            entry = df.loc[entry_date]
            entries.append(
                {
                    "event_id": event.event_id,
                    "threshold": threshold,
                    "entry_date": entry_date.isoformat(),
                    "triggered": True,
                    "low_date": event.low_date.isoformat(),
                    "days_from_low": int((entry_date - event.low_date).days),
                    "entry_drawdown": float(entry["qqq_drawdown"]),
                    "low_drawdown": event.low_drawdown,
                    "fwd_21d": float(entry["qqq_fwd_21d"]) if not math.isnan(entry["qqq_fwd_21d"]) else None,
                    "fwd_63d": float(entry["qqq_fwd_63d"]) if not math.isnan(entry["qqq_fwd_63d"]) else None,
                }
            )
        entry_df = pd.DataFrame(entries)
        valid = entry_df[entry_df["triggered"] & entry_df["fwd_21d"].notna()].copy()
        threshold_rows.append(
            {
                "threshold": threshold,
                "triggered_events": int(entry_df["triggered"].sum()),
                "events": len(events),
                "avg_days_from_low": float(valid["days_from_low"].mean()) if not valid.empty else None,
                "median_days_from_low": float(valid["days_from_low"].median()) if not valid.empty else None,
                "avg_fwd_21d": float(valid["fwd_21d"].mean()) if not valid.empty else None,
                "hit_rate_21d": float((valid["fwd_21d"] > 0).mean()) if not valid.empty else None,
                "avg_fwd_63d": float(valid["fwd_63d"].mean()) if valid["fwd_63d"].notna().any() else None,
                "hit_rate_63d": float((valid["fwd_63d"] > 0).mean()) if valid["fwd_63d"].notna().any() else None,
            }
        )
        event_rows.extend(entries)

    return pd.DataFrame(threshold_rows), pd.DataFrame(event_rows)


def choose_threshold(summary: pd.DataFrame) -> int | None:
    best = summary.dropna(subset=["avg_fwd_21d"]).copy()
    if best.empty:
        return None
    best["coverage"] = best["triggered_events"] / best["events"].replace(0, np.nan)
    practical = best[best["coverage"] >= 0.50].copy()
    if practical.empty:
        practical = best
    practical["rank_score"] = (
        practical["avg_fwd_21d"] * 100
        + practical["hit_rate_21d"] * 8
        + practical["avg_fwd_63d"].fillna(0) * 20
        + practical["coverage"] * 5
        - practical["avg_days_from_low"].abs() * 0.03
    )
    return int(practical.sort_values("rank_score", ascending=False).iloc[0]["threshold"])


def walk_forward_calibration(df: pd.DataFrame, events: list[Event], thresholds: range = range(8, 18)) -> pd.DataFrame:
    rows = []
    for idx in range(4, len(events)):
        train_events = events[:idx]
        test_event = events[idx]
        train_summary, _ = evaluate_thresholds(df, train_events, thresholds)
        threshold = choose_threshold(train_summary)
        if threshold is None:
            continue
        _, test_entries = evaluate_thresholds(df, [test_event], range(threshold, threshold + 1))
        row = test_entries.iloc[0].to_dict()
        row["trained_on_events"] = idx
        row["walk_forward_threshold"] = threshold
        rows.append(row)
    return pd.DataFrame(rows)


def fmt_pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value * 100:.1f}%"


def fmt_num(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.1f}"


def write_report(df: pd.DataFrame, events: list[Event], summary: pd.DataFrame, event_entries: pd.DataFrame) -> dict:
    best_threshold = choose_threshold(summary)
    best_row = summary[summary["threshold"] == best_threshold].iloc[0].to_dict() if best_threshold else {}
    wf = walk_forward_calibration(df, events)
    wf_valid = wf[wf["triggered"] & wf["fwd_21d"].notna()].copy() if not wf.empty else pd.DataFrame()

    summary_path = DATA_DIR / "nasdaq_bottom_backtest_summary.json"
    entries_path = DATA_DIR / "nasdaq_bottom_backtest_entries.csv"
    wf_path = DATA_DIR / "nasdaq_bottom_walk_forward_entries.csv"
    scored_path = DATA_DIR / "nasdaq_bottom_scored_history.csv"
    report_path = REPORT_DIR / "nasdaq_bottom_framework_backtest.md"

    event_entries.to_csv(entries_path, index=False)
    wf.to_csv(wf_path, index=False)
    df.reset_index().rename(columns={"index": "date"}).to_csv(scored_path, index=False)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "history_start": df.index.min().isoformat(),
        "history_end": df.index.max().isoformat(),
        "event_count": len(events),
        "best_threshold": int(best_row.get("threshold")) if best_row else None,
        "walk_forward": {
            "tested_events": int(len(wf)),
            "triggered_events": int(wf["triggered"].sum()) if not wf.empty else 0,
            "avg_fwd_21d": float(wf_valid["fwd_21d"].mean()) if not wf_valid.empty else None,
            "hit_rate_21d": float((wf_valid["fwd_21d"] > 0).mean()) if not wf_valid.empty else None,
            "avg_fwd_63d": float(wf_valid["fwd_63d"].mean()) if not wf_valid.empty and wf_valid["fwd_63d"].notna().any() else None,
            "hit_rate_63d": float((wf_valid["fwd_63d"] > 0).mean()) if not wf_valid.empty and wf_valid["fwd_63d"].notna().any() else None,
        },
        "threshold_summary": summary.to_dict(orient="records"),
        "events": [
            {
                "event_id": e.event_id,
                "start": e.start.isoformat(),
                "end": e.end.isoformat(),
                "low_date": e.low_date.isoformat(),
                "low_drawdown": e.low_drawdown,
            }
            for e in events
        ],
        "files": {
            "entries_csv": str(entries_path),
            "walk_forward_csv": str(wf_path),
            "scored_history_csv": str(scored_path),
            "report_md": str(report_path),
        },
    }
    summary_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# NASDAQ Bottom Framework Backtest",
        "",
        f"Generated: {payload['generated_at']}",
        f"History: {payload['history_start']} to {payload['history_end']}",
        f"Proxy: QQQ. Drawdown events: {len(events)}.",
        "",
        "## Method",
        "",
        "The score is a 0-20 bottom-readiness score. It is not a prediction of the exact low.",
        "It uses public proxies for the framework: QQQ price damage/stabilization, VIX/VIX3M term structure, VXN/VIX easing, TNX rate pressure, BTC risk appetite, TQQQ/QQQ volume leverage, QQEW/QQQ breadth, and QQQ/SPY relative strength.",
        "",
        "Private or paid indicators such as dealer GEX, gamma flip, put wall, and CTA flow are not directly backtested here. They are represented by price, volatility, trend, and volume proxies. FINRA margin data is aligned with a 21-day publication lag to avoid look-ahead bias.",
        "",
        "## Threshold Calibration",
        "",
        "| Threshold | Triggered Events | Avg Days From Low | 21D Avg | 21D Hit | 63D Avg | 63D Hit |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            "| {threshold:.0f} | {triggered_events:.0f}/{events:.0f} | {days} | {f21} | {h21} | {f63} | {h63} |".format(
                threshold=row["threshold"],
                triggered_events=row["triggered_events"],
                events=row["events"],
                days=fmt_num(row["avg_days_from_low"]),
                f21=fmt_pct(row["avg_fwd_21d"]),
                h21=fmt_pct(row["hit_rate_21d"]),
                f63=fmt_pct(row["avg_fwd_63d"]),
                h63=fmt_pct(row["hit_rate_63d"]),
            )
        )

    lines.extend(
        [
            "",
            "## Walk-Forward Check",
            "",
            "For each event after the first four, the threshold is selected from prior events only, then applied to the next event.",
            "",
            f"Tested events: {payload['walk_forward']['tested_events']}. Triggered: {payload['walk_forward']['triggered_events']}.",
            f"21D average return: {fmt_pct(payload['walk_forward']['avg_fwd_21d'])}. 21D hit rate: {fmt_pct(payload['walk_forward']['hit_rate_21d'])}.",
            f"63D average return: {fmt_pct(payload['walk_forward']['avg_fwd_63d'])}. 63D hit rate: {fmt_pct(payload['walk_forward']['hit_rate_63d'])}.",
        ]
    )

    lines.extend(
        [
            "",
            "## Event Lows",
            "",
            "| Event | Start | Low Date | End | Low Drawdown |",
            "|---:|---|---|---|---:|",
        ]
    )
    for event in events:
        lines.append(
            f"| {event.event_id} | {event.start.isoformat()} | {event.low_date.isoformat()} | {event.end.isoformat()} | {fmt_pct(event.low_drawdown)} |"
        )

    if best_row:
        lines.extend(
            [
                "",
                "## Suggested Calibration",
                "",
                f"The best simple threshold in this run is `{int(best_row['threshold'])}` out of 20.",
                "",
                "Practical interpretation:",
                "",
                "- Below 8: liquidation risk is usually still unresolved.",
                "- 8-11: watch zone or very small test position.",
                "- 12-14: bottom process is often forming; staged entry becomes reasonable.",
                "- 15+: confirmation is stronger, but entries tend to arrive later and may miss early rebounds.",
                "",
                "Use the threshold with event context. A high score during a shallow pullback is less meaningful than a high score after a 6%+ QQQ drawdown.",
            ]
        )

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    df = add_scores(build_dataset("10y"))
    df = df.dropna(subset=["qqq_drawdown", "bottom_score"])
    events = find_drawdown_events(df)
    summary, event_entries = evaluate_thresholds(df, events)
    payload = write_report(df, events, summary, event_entries)
    print(json.dumps({
        "report": payload["files"]["report_md"],
        "summary": payload["files"],
        "best_threshold": payload["best_threshold"],
        "event_count": payload["event_count"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
