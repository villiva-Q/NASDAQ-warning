from __future__ import annotations

import csv
import json
import math
import statistics
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

try:
    import pandas as pd
except Exception:  # pragma: no cover
    pd = None

try:
    from backtest_bottom_framework import add_scores, build_dataset, choose_threshold, evaluate_thresholds, find_drawdown_events, walk_forward_calibration
except Exception:  # pragma: no cover
    add_scores = None
    build_dataset = None
    choose_threshold = None
    evaluate_thresholds = None
    find_drawdown_events = None
    walk_forward_calibration = None


ROOT = Path(__file__).resolve().parents[1]
DOCS_DATA = ROOT / "docs" / "data"
LOCAL_DATA = ROOT / "data"
CONFIG_PATH = ROOT / "config" / "indicators.json"

YAHOO_CHART = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={range}&interval={interval}&events=history&includeAdjustedClose=true"
FINRA_XLSX = "https://www.finra.org/sites/default/files/2021-03/margin-statistics.xlsx"


def clamp(value: float, low: float = 0, high: float = 100) -> float:
    return max(low, min(high, value))


def score_high_risk(value: float | None, low: float, high: float) -> float | None:
    if value is None or math.isnan(value):
        return None
    if high == low:
        return None
    return clamp((value - low) / (high - low) * 100)


def score_low_risk(value: float | None, low: float, high: float) -> float | None:
    raw = score_high_risk(value, low, high)
    if raw is None:
        return None
    return 100 - raw


def average_available(values: list[float | None], fallback: float = 50) -> float:
    clean = [v for v in values if v is not None and not math.isnan(v)]
    if not clean:
        return fallback
    return sum(clean) / len(clean)


def fetch_bytes(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "NASDAQBubbleRadar/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()


def load_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def fetch_yahoo(symbol: str = "QQQ", range_: str = "2y", interval: str = "1d") -> dict:
    url = YAHOO_CHART.format(symbol=symbol, range=range_, interval=interval)
    payload = json.loads(fetch_bytes(url).decode("utf-8"))
    result = payload["chart"]["result"][0]
    quote = result["indicators"]["quote"][0]
    adj = result["indicators"]["adjclose"][0]["adjclose"]
    rows = []
    for idx, ts in enumerate(result["timestamp"]):
        close = adj[idx] if adj[idx] is not None else quote["close"][idx]
        if close is None:
            continue
        rows.append(
            {
                "date": datetime.fromtimestamp(ts, tz=timezone.utc).date().isoformat(),
                "close": float(close),
                "volume": quote["volume"][idx],
            }
        )
    return {"symbol": symbol, "rows": rows}


def load_or_fetch_qqq() -> dict:
    cache = LOCAL_DATA / "yahoo-qqq.json"
    try:
        data = fetch_yahoo("QQQ", "2y", "1d")
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return data
    except Exception:
        if cache.exists():
            raw = json.loads(cache.read_text(encoding="utf-8"))
            if "chart" in raw:
                result = raw["chart"]["result"][0]
                quote = result["indicators"]["quote"][0]
                adj = result["indicators"]["adjclose"][0]["adjclose"]
                rows = []
                for idx, ts in enumerate(result["timestamp"]):
                    close = adj[idx] if adj[idx] is not None else quote["close"][idx]
                    if close is not None:
                        rows.append(
                            {
                                "date": datetime.fromtimestamp(ts, tz=timezone.utc).date().isoformat(),
                                "close": float(close),
                                "volume": quote["volume"][idx],
                            }
                        )
                return {"symbol": "QQQ", "rows": rows}
            return raw
        raise


def load_or_fetch_symbol(symbol: str, range_: str = "2y", interval: str = "1d") -> dict:
    cache = LOCAL_DATA / f"yahoo-{symbol.lower()}.json"
    try:
        data = fetch_yahoo(symbol, range_, interval)
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return data
    except Exception:
        if cache.exists():
            return json.loads(cache.read_text(encoding="utf-8"))
        raise


def compute_price_metrics(rows: list[dict]) -> dict:
    closes = [float(r["close"]) for r in rows]
    latest = closes[-1]

    def sma(n: int) -> float | None:
        if len(closes) < n:
            return None
        return sum(closes[-n:]) / n

    def ret(n: int) -> float | None:
        if len(closes) <= n:
            return None
        return latest / closes[-n - 1] - 1

    sma50 = sma(50)
    sma200 = sma(200)
    high252 = max(closes[-252:]) if len(closes) >= 252 else max(closes)
    low252 = min(closes[-252:]) if len(closes) >= 252 else min(closes)
    dd_high = latest / high252 - 1
    distance_200 = latest / sma200 - 1 if sma200 else None
    distance_50 = latest / sma50 - 1 if sma50 else None
    acceleration = (ret(63) or 0) - (ret(126) or 0) / 2

    price_scores = [
        score_high_risk(distance_200, -0.05, 0.30),
        score_high_risk(ret(63), -0.08, 0.25),
        score_high_risk(acceleration, -0.06, 0.16),
        score_low_risk(dd_high, -0.15, 0.0),
    ]

    return {
        "latest": latest,
        "latest_date": rows[-1]["date"],
        "sma50": sma50,
        "sma200": sma200,
        "return_1m": ret(21),
        "return_3m": ret(63),
        "return_6m": ret(126),
        "distance_50dma": distance_50,
        "distance_200dma": distance_200,
        "drawdown_from_52w_high": dd_high,
        "range_52w": {"low": low252, "high": high252},
        "score": average_available(price_scores),
    }


def load_or_fetch_finra() -> dict | None:
    if pd is None:
        return None
    xlsx = LOCAL_DATA / "finra-margin-statistics.xlsx"
    try:
        xlsx.write_bytes(fetch_bytes(FINRA_XLSX, timeout=45))
    except Exception:
        if not xlsx.exists():
            return None

    df = pd.read_excel(xlsx)
    df.columns = ["month", "debit", "free_cash", "free_margin"]
    df = df.dropna(subset=["month", "debit"]).sort_values("month")
    latest = df.iloc[-1]
    debit = float(latest["debit"])
    free_cash = float(latest["free_cash"])
    free_margin = float(latest["free_margin"]) if not math.isnan(float(latest["free_margin"])) else None
    ratio_cash = debit / free_cash if free_cash else None
    ratio_total = debit / (free_cash + free_margin) if free_margin else None

    debt_values = [float(v) for v in df["debit"].dropna()]
    ratio_cash_values = [
        float(r["debit"]) / float(r["free_cash"])
        for _, r in df.dropna(subset=["debit", "free_cash"]).iterrows()
        if float(r["free_cash"]) != 0
    ]
    debt_percentile = sum(1 for v in debt_values if v <= debit) / len(debt_values) * 100
    ratio_percentile = sum(1 for v in ratio_cash_values if v <= ratio_cash) / len(ratio_cash_values) * 100

    return {
        "month": str(latest["month"])[:7],
        "margin_debt": debit,
        "free_cash": free_cash,
        "free_margin": free_margin,
        "debit_to_free_cash": ratio_cash,
        "debit_to_total_free_credit": ratio_total,
        "margin_debt_percentile": debt_percentile,
        "debit_to_free_cash_percentile": ratio_percentile,
        "score": average_available([debt_percentile, ratio_percentile]),
    }


def build_manual_metric(name: str, spec: dict, inverse: bool = False) -> dict:
    value = spec.get("value")
    score_fn = score_low_risk if inverse else score_high_risk
    return {
        "name": name,
        "value": value,
        "score": score_fn(value, spec["low"], spec["high"]) if value is not None else None,
        "source": spec.get("source", "manual"),
        "range": {"low": spec["low"], "high": spec["high"]},
        "as_of": spec.get("as_of"),
        "note": spec.get("note"),
        "refresh": "manual",
        "used_in_score": False,
        "freshness": freshness_status(spec.get("as_of") or load_config().get("_meta", {}).get("manual_inputs_updated_at"), "manual"),
    }


def freshness_status(as_of: str | None, cadence: str) -> str:
    if not as_of:
        return "unknown"
    try:
        if len(as_of) == 7:
            dt = datetime.fromisoformat(f"{as_of}-15").replace(tzinfo=timezone.utc)
        else:
            dt = datetime.fromisoformat(as_of).replace(tzinfo=timezone.utc)
    except Exception:
        return "unknown"
    age_days = (datetime.now(timezone.utc) - dt).days
    if cadence == "daily":
        return "fresh" if age_days <= 3 else "stale"
    if cadence == "monthly":
        return "fresh" if age_days <= 75 else "stale"
    if cadence == "manual":
        return "fresh" if age_days <= 30 else "stale"
    return "unknown"


def mark_metric(metric: dict, refresh: str, used_in_score: bool, as_of: str | None = None) -> dict:
    metric["refresh"] = refresh
    metric["used_in_score"] = used_in_score
    if as_of is not None:
        metric["as_of"] = as_of
    metric["freshness"] = freshness_status(metric.get("as_of"), refresh)
    return metric


def percentile(values: list[float], latest: float) -> float | None:
    clean = [v for v in values if v is not None and not math.isnan(v)]
    if not clean:
        return None
    return sum(1 for v in clean if v <= latest) / len(clean) * 100


def compute_daily_proxy_metrics(qqq_rows: list[dict], tqqq_rows: list[dict]) -> tuple[list[dict], float]:
    qqq_volumes = [float(row["volume"]) for row in qqq_rows if row.get("volume")]
    tqqq_volumes = [float(row["volume"]) for row in tqqq_rows if row.get("volume")]
    paired = list(zip(qqq_rows[-min(len(qqq_rows), len(tqqq_rows)) :], tqqq_rows[-min(len(qqq_rows), len(tqqq_rows)) :]))
    volume_ratios = [
        float(trow["volume"]) / float(qrow["volume"])
        for qrow, trow in paired
        if qrow.get("volume") and trow.get("volume") and float(qrow["volume"]) != 0
    ]

    latest_qqq_volume = qqq_volumes[-1] if qqq_volumes else None
    latest_tqqq_volume = tqqq_volumes[-1] if tqqq_volumes else None
    latest_ratio = volume_ratios[-1] if volume_ratios else None

    qqq_volume_score = percentile(qqq_volumes[-252:], latest_qqq_volume) if latest_qqq_volume else None
    tqqq_volume_score = percentile(tqqq_volumes[-252:], latest_tqqq_volume) if latest_tqqq_volume else None
    tqqq_ratio_score = percentile(volume_ratios[-252:], latest_ratio) if latest_ratio else None
    proxy_score = average_available([qqq_volume_score, tqqq_volume_score, tqqq_ratio_score])

    metrics = [
        mark_metric({
            "name": "QQQ Volume Percentile",
            "value": latest_qqq_volume,
            "score": qqq_volume_score,
            "source": "auto: Yahoo Finance chart API",
            "range": {"low": "1Y low volume", "high": "1Y high volume"},
            "as_of": qqq_rows[-1]["date"] if qqq_rows else None,
            "note": "Daily QQQ volume percentile over the last 252 trading days.",
        }, "daily", True),
        mark_metric({
            "name": "TQQQ Volume Percentile",
            "value": latest_tqqq_volume,
            "score": tqqq_volume_score,
            "source": "auto: Yahoo Finance chart API",
            "range": {"low": "1Y low volume", "high": "1Y high volume"},
            "as_of": tqqq_rows[-1]["date"] if tqqq_rows else None,
            "note": "Daily TQQQ volume percentile over the last 252 trading days.",
        }, "daily", True),
        mark_metric({
            "name": "TQQQ / QQQ Volume Ratio",
            "value": latest_ratio,
            "score": tqqq_ratio_score,
            "source": "auto: Yahoo Finance chart API",
            "range": {"low": "1Y low ratio", "high": "1Y high ratio"},
            "as_of": tqqq_rows[-1]["date"] if tqqq_rows else None,
            "note": "Leveraged ETF activity proxy relative to QQQ volume.",
        }, "daily", True),
    ]
    return metrics, proxy_score


def status_for(score: float, modules: dict) -> str:
    high_modules = sum(1 for value in modules.values() if value >= 70)
    if score >= 75 and high_modules >= 3:
        return "Red"
    if score >= 60:
        return "Orange"
    if score >= 40:
        return "Yellow"
    return "Green"


def bottom_status_for(score: float, drawdown: float | None) -> str:
    if drawdown is None or drawdown > -0.04:
        return "No setup"
    if score >= 15:
        return "Confirmed"
    if score >= 14:
        return "Entry zone"
    if score >= 12:
        return "Watch"
    return "Wait"


def bottom_metric(name: str, value, score, source: str, note: str, as_of: str | None) -> dict:
    return {
        "name": name,
        "value": None if value is None or (isinstance(value, float) and math.isnan(value)) else value,
        "score": None if score is None or (isinstance(score, float) and math.isnan(score)) else round(float(score), 2),
        "source": source,
        "note": note,
        "as_of": as_of,
        "refresh": "daily",
        "used_in_score": True,
        "freshness": freshness_status(as_of, "daily") if as_of else "unknown",
    }


def build_bottom_framework_snapshot() -> dict | None:
    if not all([add_scores, build_dataset, find_drawdown_events, evaluate_thresholds]):
        return None
    try:
        scored = add_scores(build_dataset("10y")).dropna(subset=["qqq_drawdown", "bottom_score"])
    except Exception as exc:
        return {
            "available": False,
            "error": str(exc),
        }

    events = find_drawdown_events(scored)
    summary, _ = evaluate_thresholds(scored, events)
    wf = walk_forward_calibration(scored, events) if walk_forward_calibration else pd.DataFrame()
    latest = scored.iloc[-1]
    latest_date = scored.index[-1].isoformat()

    best_threshold = choose_threshold(summary) if choose_threshold else None
    if best_threshold is None:
        best_threshold = 13

    signal_specs = [
        ("Drawdown Zone", "qqq_drawdown", "s_drawdown_zone", "QQQ", "Scores whether the pullback is large enough to matter."),
        ("Price Stabilizing", "qqq_ret_5d", "s_price_stabilizing", "QQQ", "Looks for short-term stabilization after the drawdown."),
        ("Oversold Rebound", "qqq_rsi14", "s_oversold_rebound", "QQQ", "Checks whether oversold pressure is starting to reverse."),
        ("Volatility Easing", "vix_change_5d", "s_vol_easing", "Yahoo: ^VIX, ^VXN", "VIX/VXN easing means forced hedging pressure may be cooling."),
        ("VIX Term Structure", "vix_ratio_3m", "s_vol_term", "Yahoo: ^VIX, ^VIX3M", "Contango recovery is a panic-normalization proxy."),
        ("Short Vol Term", "vix9d_ratio_3m", "s_short_vol_term", "Yahoo: ^VIX9D, ^VIX3M", "VIX9D/VIX3M adds a shorter panic gauge when free data is available."),
        ("Options Skew Cooling", "skew_change_5d", "s_options_skew_cooling", "Yahoo: ^SKEW, ^CPC", "Free proxy for put/call and tail-hedge pressure cooling."),
        ("Rate Easing", "tnx_change_5d", "s_rate_easing", "Yahoo: ^TNX", "Checks whether rate pressure stopped worsening."),
        ("Crypto Stable", "btc_ret_5d", "s_crypto_stable", "Yahoo: BTC-USD", "BTC stabilization proxies high-beta risk appetite."),
        ("Leveraged ETF Cooling", "tqqq_qqq_volume_ratio", "s_leverage_cooling", "Yahoo: TQQQ/QQQ", "TQQQ/QQQ volume ratio proxies leveraged NASDAQ activity."),
        ("Breadth Recovering", "qqew_rel_qqq_10d", "s_breadth_recovering", "Yahoo: QQEW/QQQ", "Equal-weight relative strength proxies internal repair."),
        ("Tech Relative Strength", "qqq_rel_spy_5d", "s_tech_relative", "Yahoo: QQQ/SPY", "Checks whether NASDAQ leadership is returning."),
        ("FINRA Margin Cooling", "finra_margin_3m", "s_finra_margin_cooling", "FINRA margin statistics", "Monthly margin debt is lagged 21 days to avoid look-ahead bias."),
    ]
    signals = [
        bottom_metric(name, latest.get(value_col), latest.get(score_col), source, note, latest_date)
        for name, value_col, score_col, source, note in signal_specs
    ]

    wf_valid = wf[wf["triggered"] & wf["fwd_21d"].notna()].copy() if wf is not None and not wf.empty else pd.DataFrame()
    return {
        "available": True,
        "as_of": latest_date,
        "score": round(float(latest["bottom_score"]), 1),
        "score_pct": round(float(latest["bottom_score_pct"]), 1),
        "status": bottom_status_for(float(latest["bottom_score"]), float(latest["qqq_drawdown"])),
        "qqq": {
            "close": round(float(latest["qqq_close"]), 2),
            "drawdown_from_52w_high": float(latest["qqq_drawdown"]),
            "forward_21d": None if math.isnan(float(latest["qqq_fwd_21d"])) else float(latest["qqq_fwd_21d"]),
            "forward_63d": None if math.isnan(float(latest["qqq_fwd_63d"])) else float(latest["qqq_fwd_63d"]),
        },
        "calibration": {
            "history_start": scored.index.min().isoformat(),
            "history_end": scored.index.max().isoformat(),
            "event_count": len(events),
            "best_threshold": best_threshold,
            "threshold_summary": summary.to_dict(orient="records"),
            "walk_forward": {
                "tested_events": int(len(wf)) if wf is not None else 0,
                "triggered_events": int(wf["triggered"].sum()) if wf is not None and not wf.empty else 0,
                "avg_fwd_21d": float(wf_valid["fwd_21d"].mean()) if not wf_valid.empty else None,
                "hit_rate_21d": float((wf_valid["fwd_21d"] > 0).mean()) if not wf_valid.empty else None,
                "avg_fwd_63d": float(wf_valid["fwd_63d"].mean()) if not wf_valid.empty and wf_valid["fwd_63d"].notna().any() else None,
                "hit_rate_63d": float((wf_valid["fwd_63d"] > 0).mean()) if not wf_valid.empty and wf_valid["fwd_63d"].notna().any() else None,
            },
        },
        "signals": signals,
        "principle": {
            "summary": "Bottom readiness rises when a meaningful QQQ drawdown is followed by volatility normalization, rate pressure easing, risk appetite stabilization, leverage cooling, breadth repair, and price stabilization.",
            "use": "Use as a staged-entry confirmation tool after a drawdown, not as an exact low predictor.",
            "limits": "Dealer gamma, put wall, and CTA flow are represented by public proxies unless paid data is connected.",
        },
    }


def build_snapshot() -> dict:
    config = load_config()
    qqq = load_or_fetch_qqq()
    tqqq = load_or_fetch_symbol("TQQQ", "2y", "1d")
    price = compute_price_metrics(qqq["rows"])
    finra = load_or_fetch_finra()
    bottom_framework = build_bottom_framework_snapshot()

    valuation_metrics = [
        build_manual_metric("NDX Forward P/E", config["valuation"]["ndx_forward_pe"]),
        build_manual_metric("NDX Price/Sales", config["valuation"]["ndx_price_sales"]),
        build_manual_metric("Equity Risk Premium", config["valuation"]["equity_risk_premium"], inverse=True),
    ]
    liquidity_metrics = [
        build_manual_metric("QQQ 4W Flow", config["liquidity"]["qqq_flow_4w_usd_bn"], inverse=True),
        build_manual_metric("Fed Liquidity 4W Change", config["liquidity"]["fed_liquidity_4w_change_usd_bn"], inverse=True),
        build_manual_metric("Credit Spread Trend", config["liquidity"]["credit_spread_trend"]),
    ]
    derivatives_metrics = [
        build_manual_metric("0DTE Share", config["derivatives"]["zero_dte_share"]),
        build_manual_metric("Put/Call Heat", config["derivatives"]["put_call_heat"]),
    ]
    ibkr_metrics = [
        build_manual_metric("IBKR Client Margin Loan", config["leverage_proxies"]["ibkr_client_margin_loan_usd_bn"]),
        build_manual_metric("IBKR Margin Loan YoY", config["leverage_proxies"]["ibkr_margin_loan_yoy_pct"]),
        build_manual_metric("IBKR Margin Loan MoM", config["leverage_proxies"]["ibkr_margin_loan_mom_pct"]),
    ]
    daily_proxy_metrics, daily_proxy_score = compute_daily_proxy_metrics(qqq["rows"], tqqq["rows"])
    breadth_metrics = [
        build_manual_metric("Equal Weight Relative 6M", config["breadth"]["equal_weight_relative_6m"], inverse=True),
        build_manual_metric("Mega-cap Concentration", config["breadth"]["mega_cap_concentration"]),
    ]

    price_metric = mark_metric({
        "name": "QQQ Price Confirmation",
        "value": price["latest"],
        "score": price["score"],
        "source": "auto: Yahoo Finance chart API",
        "range": {"low": "low risk", "high": "high risk"},
        "as_of": price["latest_date"],
        "note": "Composite of distance from 200DMA, 3M return, acceleration, and drawdown from 52-week high.",
    }, "daily", True)

    finra_metric = None
    if finra:
        finra_metric = mark_metric({
            "name": "FINRA Margin Leverage",
            "value": finra["debit_to_free_cash"],
            "score": finra["score"],
            "source": "auto-check: FINRA margin statistics",
            "range": {"low": "historical low", "high": "historical high"},
            "as_of": finra["month"],
            "note": "Authoritative aggregate margin data. Monthly and lagged; used as a slow structural risk variable.",
        }, "monthly", True)

    core_price_score = price_metric["score"]
    core_finra_score = finra_metric["score"] if finra_metric and finra_metric["freshness"] != "stale" else 50
    core_daily_proxy_score = daily_proxy_score

    modules = {
        "price_confirmation": core_price_score,
        "finra_margin_slow": core_finra_score,
        "daily_leverage_proxy": core_daily_proxy_score,
    }
    overall = (
        modules["price_confirmation"] * 0.40
        + modules["finra_margin_slow"] * 0.35
        + modules["daily_leverage_proxy"] * 0.25
    )

    warnings = []
    if core_finra_score >= 80:
        warnings.append("FINRA margin leverage is in a historically high zone.")
    if core_daily_proxy_score >= 75:
        warnings.append("QQQ/TQQQ daily leverage proxy is elevated.")
    if price["distance_200dma"] and price["distance_200dma"] > 0.18:
        warnings.append("QQQ is extended above its 200-day moving average.")
    if price["drawdown_from_52w_high"] and price["drawdown_from_52w_high"] < -0.05 and overall > 60:
        warnings.append("Price has pulled back from highs while bubble pressure remains high.")

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "market": "NASDAQ / QQQ",
        "manual_inputs": config.get("_meta", {}),
        "overall_score": round(overall, 1),
        "status": status_for(overall, modules),
        "modules": {k: round(v, 1) for k, v in modules.items()},
        "score_policy": {
            "name": "Core Daily Score",
            "description": "Only automatic daily proxies and explicit-frequency slow variables enter the score. Manual inputs are context only.",
            "weights": {
                "price_confirmation": 0.40,
                "finra_margin_slow": 0.35,
                "daily_leverage_proxy": 0.25
            }
        },
        "price": price,
        "finra": finra,
        "bottom_framework": bottom_framework,
        "core_metrics": {
            "price": [price_metric],
            "finra_margin_slow": [finra_metric] if finra_metric else [],
            "daily_leverage_proxy": daily_proxy_metrics,
        },
        "metrics": {
            "valuation": valuation_metrics,
            "liquidity": liquidity_metrics,
            "derivatives": derivatives_metrics,
            "ibkr_leverage_proxy": ibkr_metrics,
            "breadth": breadth_metrics,
        },
        "warnings": warnings,
        "history": qqq["rows"][-260:],
        "notes": [
            "This dashboard is a risk monitor, not a precise top predictor.",
            "Manual indicators can be updated in config/indicators.json until a reliable API source is added.",
        ],
    }


def main() -> int:
    DOCS_DATA.mkdir(parents=True, exist_ok=True)
    snapshot = build_snapshot()
    (DOCS_DATA / "dashboard.json").write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    (DOCS_DATA / "dashboard-inline.js").write_text(
        "window.DASHBOARD_DATA = "
        + json.dumps(snapshot, ensure_ascii=False)
        + ";\n",
        encoding="utf-8",
    )
    print(f"Updated docs/data/dashboard.json at {snapshot['generated_at']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
