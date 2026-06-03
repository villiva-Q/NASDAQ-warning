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
    }


def status_for(score: float, modules: dict) -> str:
    high_modules = sum(1 for value in modules.values() if value >= 70)
    if score >= 75 and high_modules >= 3:
        return "Red"
    if score >= 60:
        return "Orange"
    if score >= 40:
        return "Yellow"
    return "Green"


def build_snapshot() -> dict:
    config = load_config()
    qqq = load_or_fetch_qqq()
    price = compute_price_metrics(qqq["rows"])
    finra = load_or_fetch_finra()

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
    breadth_metrics = [
        build_manual_metric("Equal Weight Relative 6M", config["breadth"]["equal_weight_relative_6m"], inverse=True),
        build_manual_metric("Mega-cap Concentration", config["breadth"]["mega_cap_concentration"]),
    ]

    valuation_score = average_available([m["score"] for m in valuation_metrics])
    liquidity_score = average_available([m["score"] for m in liquidity_metrics], fallback=50)
    leverage_score = finra["score"] if finra else 50
    derivatives_score = average_available([m["score"] for m in derivatives_metrics])
    breadth_score = average_available([m["score"] for m in breadth_metrics])
    leverage_derivatives_score = 0.65 * leverage_score + 0.35 * derivatives_score

    modules = {
        "valuation": valuation_score,
        "liquidity": liquidity_score,
        "leverage_derivatives": leverage_derivatives_score,
        "breadth_concentration": breadth_score,
        "price_confirmation": price["score"],
    }
    overall = (
        modules["valuation"] * 0.30
        + modules["liquidity"] * 0.20
        + modules["leverage_derivatives"] * 0.20
        + modules["breadth_concentration"] * 0.20
        + modules["price_confirmation"] * 0.10
    )

    warnings = []
    if valuation_score >= 75:
        warnings.append("NASDAQ valuation pressure is elevated.")
    if leverage_score >= 80:
        warnings.append("FINRA margin leverage is in a historically high zone.")
    if breadth_score >= 70:
        warnings.append("Breadth/concentration signals suggest narrowing leadership.")
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
        "price": price,
        "finra": finra,
        "metrics": {
            "valuation": valuation_metrics,
            "liquidity": liquidity_metrics,
            "derivatives": derivatives_metrics,
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
    print(f"Updated docs/data/dashboard.json at {snapshot['generated_at']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
