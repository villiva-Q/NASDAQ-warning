from __future__ import annotations

import json
import math
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
CONFIG_PATH = ROOT / "config" / "indicators.json"

MU_CIK = "0000723125"
SEC_COMPANYFACTS = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{MU_CIK}.json"
YAHOO_CHART = (
    "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    "?range={range}&interval=1d&events=history&includeAdjustedClose=true"
)


def clamp(value: float, low: float = 0, high: float = 100) -> float:
    return max(low, min(high, value))


def score_high_risk(value: float | None, low: float, high: float) -> float | None:
    if value is None or math.isnan(value) or high == low:
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


def fetch_json(url: str, timeout: int = 30, user_agent: str = "NASDAQBubbleRadar/1.0") -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def fetch_yahoo_rows(symbol: str = "MU", range_: str = "2y") -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    cache = DATA_DIR / f"yahoo-{symbol.lower()}-{range_}.json"
    encoded = urllib.parse.quote(symbol, safe="")
    url = YAHOO_CHART.format(symbol=encoded, range=range_)
    try:
        payload = fetch_json(url, user_agent="Mozilla/5.0")
        cache.write_text(json.dumps(payload), encoding="utf-8")
    except Exception:
        if not cache.exists():
            raise
        payload = json.loads(cache.read_text(encoding="utf-8"))

    result = payload["chart"]["result"][0]
    quote = result["indicators"]["quote"][0]
    adj = result["indicators"].get("adjclose", [{}])[0].get("adjclose")
    rows = []
    for idx, ts in enumerate(result.get("timestamp", [])):
        close = adj[idx] if adj and adj[idx] is not None else quote["close"][idx]
        if close is None:
            continue
        rows.append(
            {
                "date": datetime.fromtimestamp(ts, tz=timezone.utc).date().isoformat(),
                "close": float(close),
                "volume": float(quote["volume"][idx] or 0),
            }
        )
    return {"symbol": symbol, "rows": rows}


def compute_price_heat(rows: list[dict]) -> tuple[dict, float]:
    closes = [float(row["close"]) for row in rows]
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
    drawdown = latest / high252 - 1
    distance_50 = latest / sma50 - 1 if sma50 else None
    distance_200 = latest / sma200 - 1 if sma200 else None
    score = average_available(
        [
            score_high_risk(ret(63), -0.10, 1.20),
            score_high_risk(distance_200, -0.10, 1.00),
            score_low_risk(drawdown, -0.45, 0),
            score_high_risk(ret(21), -0.15, 0.45),
        ]
    )

    return (
        {
            "latest": latest,
            "latest_date": rows[-1]["date"],
            "return_1m": ret(21),
            "return_3m": ret(63),
            "distance_50dma": distance_50,
            "distance_200dma": distance_200,
            "drawdown_from_52w_high": drawdown,
            "range_52w": {"high": high252},
        },
        score,
    )


def fetch_companyfacts() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    cache = DATA_DIR / "sec-mu-companyfacts.json"
    try:
        payload = fetch_json(SEC_COMPANYFACTS, timeout=45, user_agent="mr.q research contact@example.com")
        cache.write_text(json.dumps(payload), encoding="utf-8")
    except Exception:
        if not cache.exists():
            raise
        payload = json.loads(cache.read_text(encoding="utf-8"))
    return payload


def fact_entries(companyfacts: dict, concepts: list[str], unit: str) -> list[dict]:
    us_gaap = companyfacts.get("facts", {}).get("us-gaap", {})
    for concept in concepts:
        units = us_gaap.get(concept, {}).get("units", {})
        if unit in units:
            return units[unit]
    return []


def duration_days(entry: dict) -> int | None:
    try:
        start = datetime.fromisoformat(entry["start"])
        end = datetime.fromisoformat(entry["end"])
    except Exception:
        return None
    return (end - start).days


def latest_quarter(entries: list[dict]) -> dict | None:
    quarters = []
    for entry in entries:
        days = duration_days(entry)
        if days is None or days < 60 or days > 115:
            continue
        if entry.get("form") not in {"10-Q", "10-K"}:
            continue
        if entry.get("fp") == "FY":
            continue
        quarters.append(entry)
    if not quarters:
        return None
    return sorted(quarters, key=lambda x: (x.get("end", ""), x.get("filed", "")))[-1]


def quarterly_series(entries: list[dict]) -> list[dict]:
    by_period = {}
    for entry in entries:
        days = duration_days(entry)
        if days is None or days < 60 or days > 115:
            continue
        if entry.get("form") not in {"10-Q", "10-K"} or entry.get("fp") == "FY":
            continue
        key = (entry.get("start"), entry.get("end"))
        current = by_period.get(key)
        if current is None or entry.get("filed", "") >= current.get("filed", ""):
            by_period[key] = entry
    return sorted(by_period.values(), key=lambda x: x.get("end", ""))


def latest_annual(entries: list[dict], fy: int | None = None) -> dict | None:
    annuals = []
    for entry in entries:
        days = duration_days(entry)
        if days is None or days < 330 or days > 380:
            continue
        if entry.get("form") != "10-K" or entry.get("fp") != "FY":
            continue
        if fy is not None and entry.get("fy") != fy:
            continue
        annuals.append(entry)
    if not annuals:
        return None
    return sorted(annuals, key=lambda x: (x.get("fy", 0), x.get("end", ""), x.get("filed", "")))[-1]


def latest_ytd(entries: list[dict]) -> dict | None:
    ytds = []
    for entry in entries:
        days = duration_days(entry)
        if days is None or days < 150 or days > 310:
            continue
        if entry.get("form") != "10-Q" or entry.get("fp") not in {"Q2", "Q3"}:
            continue
        ytds.append(entry)
    if not ytds:
        return None
    return sorted(ytds, key=lambda x: (x.get("fy", 0), x.get("end", ""), x.get("filed", "")))[-1]


def matching_ytd(entries: list[dict], fy: int, fp: str) -> dict | None:
    matches = []
    for entry in entries:
        days = duration_days(entry)
        if days is None or days < 150 or days > 310:
            continue
        if entry.get("form") == "10-Q" and entry.get("fy") == fy and entry.get("fp") == fp:
            matches.append(entry)
    if not matches:
        return None
    return sorted(matches, key=lambda x: (x.get("end", ""), x.get("filed", "")))[-1]


def ttm_value(entries: list[dict]) -> float | None:
    ytd = latest_ytd(entries)
    if ytd:
        fy = int(ytd["fy"])
        fp = ytd["fp"]
        annual_prev = latest_annual(entries, fy - 1)
        ytd_prev = matching_ytd(entries, fy - 1, fp)
        if annual_prev and ytd_prev:
            return float(annual_prev["val"]) + float(ytd["val"]) - float(ytd_prev["val"])

    annual = latest_annual(entries)
    if annual:
        return float(annual["val"])
    return None


def growth(latest: float | None, previous: float | None) -> float | None:
    if latest is None or previous is None or previous == 0:
        return None
    return latest / previous - 1


def metric(name: str, value, score, source: str, note: str, as_of: str | None, refresh: str = "auto") -> dict:
    return {
        "name": name,
        "value": value,
        "score": None if score is None or (isinstance(score, float) and math.isnan(score)) else round(float(score), 1),
        "source": source,
        "note": note,
        "as_of": as_of,
        "refresh": refresh,
        "used_in_score": True,
    }


def manual_metric(name: str, spec: dict) -> dict:
    value = spec.get("value")
    return metric(
        name,
        value,
        score_high_risk(value, spec["low"], spec["high"]) if value is not None else None,
        spec.get("source", "manual"),
        spec.get("note", ""),
        spec.get("as_of"),
        "manual",
    )


def status_for(score: float) -> str:
    if score >= 75:
        return "Fragile"
    if score >= 55:
        return "Hot"
    if score >= 35:
        return "Watch"
    return "Normal"


def build_micron_canary_snapshot(config: dict | None = None, liquidity_sensitivity_score: float | None = None) -> dict:
    if config is None:
        config = load_config()

    yahoo = fetch_yahoo_rows("MU", "2y")
    price, price_score = compute_price_heat(yahoo["rows"])
    facts = fetch_companyfacts()

    revenue_entries = fact_entries(facts, ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"], "USD")
    gross_profit_entries = fact_entries(facts, ["GrossProfit"], "USD")
    net_income_entries = fact_entries(facts, ["NetIncomeLoss"], "USD")
    eps_entries = fact_entries(facts, ["EarningsPerShareDiluted"], "USD/shares")

    revenue_q = quarterly_series(revenue_entries)
    gross_profit_q = quarterly_series(gross_profit_entries)
    eps_q = quarterly_series(eps_entries)

    latest_revenue = revenue_q[-1] if revenue_q else None
    prev_revenue = revenue_q[-2] if len(revenue_q) >= 2 else None
    latest_gross_profit = gross_profit_q[-1] if gross_profit_q else None
    prev_gross_profit = gross_profit_q[-2] if len(gross_profit_q) >= 2 else None
    latest_eps = eps_q[-1] if eps_q else None
    prev_eps = eps_q[-2] if len(eps_q) >= 2 else None

    latest_revenue_value = float(latest_revenue["val"]) if latest_revenue else None
    prev_revenue_value = float(prev_revenue["val"]) if prev_revenue else None
    latest_gross_profit_value = float(latest_gross_profit["val"]) if latest_gross_profit else None
    prev_gross_profit_value = float(prev_gross_profit["val"]) if prev_gross_profit else None
    latest_eps_value = float(latest_eps["val"]) if latest_eps else None
    prev_eps_value = float(prev_eps["val"]) if prev_eps else None

    latest_gross_margin = (
        latest_gross_profit_value / latest_revenue_value
        if latest_gross_profit_value is not None and latest_revenue_value
        else None
    )
    prev_gross_margin = (
        prev_gross_profit_value / prev_revenue_value
        if prev_gross_profit_value is not None and prev_revenue_value
        else None
    )
    revenue_qoq = growth(latest_revenue_value, prev_revenue_value)
    eps_qoq = growth(latest_eps_value, prev_eps_value)
    gross_margin_delta = (
        latest_gross_margin - prev_gross_margin
        if latest_gross_margin is not None and prev_gross_margin is not None
        else None
    )

    ttm_eps = ttm_value(eps_entries)
    ttm_revenue = ttm_value(revenue_entries)
    ttm_net_income = ttm_value(net_income_entries)
    trailing_pe = price["latest"] / ttm_eps if ttm_eps and ttm_eps > 0 else None

    profit_cycle_metrics = [
        metric(
            "Latest Gross Margin",
            latest_gross_margin,
            score_high_risk(latest_gross_margin, 0.35, 0.85),
            "auto: SEC companyfacts",
            "Gross profit divided by revenue for the latest standalone quarter.",
            latest_revenue.get("end") if latest_revenue else None,
        ),
        metric(
            "Revenue QoQ Growth",
            revenue_qoq,
            score_high_risk(revenue_qoq, -0.10, 0.80),
            "auto: SEC companyfacts",
            "Standalone quarterly revenue growth. Extreme growth signals capex-chain heat.",
            latest_revenue.get("end") if latest_revenue else None,
        ),
        metric(
            "Diluted EPS QoQ Growth",
            eps_qoq,
            score_high_risk(eps_qoq, -0.20, 1.50),
            "auto: SEC companyfacts",
            "Standalone quarterly GAAP diluted EPS growth.",
            latest_eps.get("end") if latest_eps else None,
        ),
        metric(
            "Gross Margin QoQ Delta",
            gross_margin_delta,
            score_high_risk(gross_margin_delta, -0.05, 0.20),
            "auto: SEC companyfacts",
            "Quarterly gross-margin acceleration. A rollover from extreme levels is a canary warning.",
            latest_revenue.get("end") if latest_revenue else None,
        ),
    ]
    profit_cycle_score = average_available([item["score"] for item in profit_cycle_metrics])

    micron_config = config.get("micron_canary", {})
    demand_lockin_metrics = [
        manual_metric("HBM Supply Tightness", micron_config["hbm_supply_tightness"]),
        manual_metric("Take-or-Pay Intensity", micron_config["take_or_pay_intensity"]),
        manual_metric("Customer Prepayment Intensity", micron_config["customer_prepayment_intensity"]),
    ]
    demand_lockin_score = average_available([item["score"] for item in demand_lockin_metrics])

    peak_trap_metrics = [
        metric(
            "Trailing GAAP P/E",
            trailing_pe,
            score_low_risk(trailing_pe, 8, 35) if latest_gross_margin and latest_gross_margin >= 0.55 else score_high_risk(trailing_pe, 8, 35),
            "auto: Yahoo Finance + SEC companyfacts",
            "Low P/E becomes risky when it is paired with extreme margins and EPS surge, because it may reflect peak earnings.",
            price["latest_date"],
        ),
        metric(
            "TTM Diluted EPS",
            ttm_eps,
            score_high_risk(ttm_eps, 0, 45),
            "auto: SEC companyfacts",
            "TTM GAAP diluted EPS estimated from latest annual plus YTD bridge.",
            latest_eps.get("end") if latest_eps else None,
        ),
        metric(
            "Peak Margin Confirmation",
            latest_gross_margin,
            score_high_risk(latest_gross_margin, 0.45, 0.85),
            "auto: SEC companyfacts",
            "Extreme gross margin confirms that valuation is being measured on unusually strong profits.",
            latest_revenue.get("end") if latest_revenue else None,
        ),
    ]
    peak_trap_score = average_available([item["score"] for item in peak_trap_metrics])

    price_metrics = [
        metric(
            "MU 3M Return",
            price["return_3m"],
            score_high_risk(price["return_3m"], -0.10, 1.20),
            "auto: Yahoo Finance chart API",
            "Three-month momentum heat.",
            price["latest_date"],
        ),
        metric(
            "Distance From 200DMA",
            price["distance_200dma"],
            score_high_risk(price["distance_200dma"], -0.10, 1.00),
            "auto: Yahoo Finance chart API",
            "Price extension above long trend.",
            price["latest_date"],
        ),
        metric(
            "Drawdown From 52W High",
            price["drawdown_from_52w_high"],
            score_low_risk(price["drawdown_from_52w_high"], -0.45, 0),
            "auto: Yahoo Finance chart API",
            "Near-high prices leave less margin for disappointment.",
            price["latest_date"],
        ),
        metric(
            "MU 1M Return",
            price["return_1m"],
            score_high_risk(price["return_1m"], -0.15, 0.45),
            "auto: Yahoo Finance chart API",
            "Short-term acceleration heat.",
            price["latest_date"],
        ),
    ]

    liquidity_score = 50 if liquidity_sensitivity_score is None else liquidity_sensitivity_score
    liquidity_metrics = [
        metric(
            "Market Liquidity Sensitivity",
            liquidity_score,
            liquidity_score,
            "dashboard: liquidity drain overlay",
            "High-beta AI canaries become more fragile when the broader liquidity-drain overlay rises.",
            price["latest_date"],
        )
    ]

    groups = {
        "price_heat": {
            "score": round(price_score, 1),
            "metrics": price_metrics,
        },
        "profit_cycle_heat": {
            "score": round(profit_cycle_score, 1),
            "metrics": profit_cycle_metrics,
        },
        "demand_lockin_heat": {
            "score": round(demand_lockin_score, 1),
            "metrics": demand_lockin_metrics,
        },
        "peak_earnings_trap": {
            "score": round(peak_trap_score, 1),
            "metrics": peak_trap_metrics,
        },
        "liquidity_sensitivity": {
            "score": round(liquidity_score, 1),
            "metrics": liquidity_metrics,
        },
    }

    score = (
        groups["price_heat"]["score"] * 0.30
        + groups["profit_cycle_heat"]["score"] * 0.25
        + groups["demand_lockin_heat"]["score"] * 0.20
        + groups["peak_earnings_trap"]["score"] * 0.15
        + groups["liquidity_sensitivity"]["score"] * 0.10
    )

    warnings = []
    if groups["profit_cycle_heat"]["score"] >= 75 and groups["peak_earnings_trap"]["score"] >= 65:
        warnings.append("Micron profits look extreme enough that low P/E may be a peak-earnings trap.")
    if groups["demand_lockin_heat"]["score"] >= 75:
        warnings.append("Manual supply-chain inputs imply high demand lock-in and customer urgency.")
    if price["drawdown_from_52w_high"] is not None and price["drawdown_from_52w_high"] < -0.15:
        warnings.append("MU has started to draw down materially from its 52-week high.")

    return {
        "available": True,
        "as_of": price["latest_date"],
        "score": round(score, 1),
        "status": status_for(score),
        "symbol": "MU",
        "price": price,
        "fundamentals": {
            "latest_quarter_end": latest_revenue.get("end") if latest_revenue else None,
            "latest_revenue": latest_revenue_value,
            "latest_gross_profit": latest_gross_profit_value,
            "latest_gross_margin": latest_gross_margin,
            "latest_diluted_eps": latest_eps_value,
            "revenue_qoq": revenue_qoq,
            "eps_qoq": eps_qoq,
            "gross_margin_delta": gross_margin_delta,
            "ttm_revenue": ttm_revenue,
            "ttm_net_income": ttm_net_income,
            "ttm_diluted_eps": ttm_eps,
            "trailing_pe": trailing_pe,
        },
        "weights": {
            "price_heat": 0.30,
            "profit_cycle_heat": 0.25,
            "demand_lockin_heat": 0.20,
            "peak_earnings_trap": 0.15,
            "liquidity_sensitivity": 0.10,
        },
        "groups": groups,
        "warnings": warnings,
        "principle": {
            "summary": "Micron is treated as an AI-memory canary: low static P/E is not automatically safe when gross margin, EPS, and demand lock-in are extreme.",
            "use": "Watch for divergence: MU price near highs and profits extreme, while cloud capex QoQ growth or memory gross margin acceleration rolls over.",
            "limits": "Demand lock-in inputs are manual until a stable contract/deposit dataset is connected.",
        },
    }


def main() -> int:
    payload = build_micron_canary_snapshot()
    out = DATA_DIR / "micron_canary_score.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"file": str(out), "score": payload["score"], "status": payload["status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
