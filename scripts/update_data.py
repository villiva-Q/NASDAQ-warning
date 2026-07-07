from __future__ import annotations

import csv
import html
import json
import math
import re
import statistics
import subprocess
import sys
import time
import urllib.parse
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

try:
    from micron_canary_score import build_micron_canary_snapshot
except Exception:  # pragma: no cover
    build_micron_canary_snapshot = None


ROOT = Path(__file__).resolve().parents[1]
DOCS_DATA = ROOT / "docs" / "data"
LOCAL_DATA = ROOT / "data"
CONFIG_PATH = ROOT / "config" / "indicators.json"

YAHOO_CHART = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={range}&interval={interval}&events=history&includeAdjustedClose=true"
FINRA_XLSX = "https://www.finra.org/sites/default/files/2021-03/margin-statistics.xlsx"
FRED_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
NYFED_REPO_SEARCH = "https://markets.newyorkfed.org/api/rp/results/search.json"
CBOE_DAILY_OPTIONS = "https://www.cboe.com/markets/us/options/market-statistics/daily/"
SEC_COMPANYFACTS = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
SEC_USER_AGENT = "mr.q research contact@example.com"

HYPERSCALERS = {
    "MSFT": "0000789019",
    "AMZN": "0001018724",
    "GOOGL": "0001652044",
    "META": "0001326801",
}

CAPEX_CONCEPTS = [
    "PaymentsToAcquirePropertyPlantAndEquipment",
    "PaymentsToAcquireProductiveAssets",
]


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


def fetch_bytes(url: str, timeout: int = 30, headers: dict | None = None) -> bytes:
    request_headers = {"User-Agent": "NASDAQBubbleRadar/1.0"}
    if headers:
        request_headers.update(headers)
    req = urllib.request.Request(url, headers=request_headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read()
    except Exception as first_error:
        cmd = ["curl", "-L", "--max-time", str(timeout), "-s"]
        for key, value in request_headers.items():
            cmd.extend(["-H", f"{key}: {value}"])
        cmd.append(url)
        try:
            result = subprocess.run(cmd, check=True, capture_output=True)
            if result.stdout:
                return result.stdout
        except Exception:
            pass
        raise first_error


def fetch_bytes_with_curl(url: str, timeout: int = 15, headers: dict | None = None) -> bytes:
    request_headers = {"User-Agent": "NASDAQBubbleRadar/1.0"}
    if headers:
        request_headers.update(headers)
    cmd = ["curl", "-L", "--max-time", str(timeout), "-s"]
    for key, value in request_headers.items():
        cmd.extend(["-H", f"{key}: {value}"])
    cmd.append(url)
    result = subprocess.run(cmd, check=True, capture_output=True)
    if not result.stdout:
        raise RuntimeError(f"Empty curl response for {url}")
    return result.stdout


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
    return mark_metric({
        "name": name,
        "value": value,
        "score": score_fn(value, spec["low"], spec["high"]) if value is not None else None,
        "source": spec.get("source", "manual"),
        "range": {"low": spec["low"], "high": spec["high"]},
        "as_of": spec.get("as_of"),
        "note": spec.get("note"),
    }, "manual", False, spec.get("as_of") or load_config().get("_meta", {}).get("manual_inputs_updated_at"))


def parse_as_of(as_of: str | None) -> datetime | None:
    if not as_of:
        return None
    try:
        if len(as_of) == 7:
            return datetime.fromisoformat(f"{as_of}-15").replace(tzinfo=timezone.utc)
        if len(as_of) == 4:
            return datetime.fromisoformat(f"{as_of}-07-01").replace(tzinfo=timezone.utc)
        parsed = datetime.fromisoformat(as_of.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except Exception:
        return None


def cadence_thresholds(cadence: str) -> tuple[int, int]:
    thresholds = {
        "daily": (5, 14),
        "weekly": (10, 28),
        "monthly": (75, 120),
        "quarterly": (135, 220),
        "manual": (45, 120),
        "static": (9999, 9999),
    }
    return thresholds.get(cadence, thresholds["manual"])


def freshness_detail(as_of: str | None, cadence: str) -> dict:
    dt = parse_as_of(as_of)
    if dt is None:
        return {
            "status": "unknown",
            "age_days": None,
            "cadence": cadence,
            "score": 50,
            "fresh_days": None,
            "stale_days": None,
        }
    age_days = max(0, (datetime.now(timezone.utc) - dt).days)
    fresh_days, stale_days = cadence_thresholds(cadence)
    if age_days <= fresh_days:
        status = "fresh"
        score = 100
    elif age_days <= stale_days:
        status = "aging"
        score = 70
    else:
        status = "stale"
        score = 25
    return {
        "status": status,
        "age_days": age_days,
        "cadence": cadence,
        "score": score,
        "fresh_days": fresh_days,
        "stale_days": stale_days,
    }


def freshness_status(as_of: str | None, cadence: str) -> str:
    return freshness_detail(as_of, cadence)["status"]


def source_base_confidence(source: str | None, refresh: str) -> int:
    text = (source or "").lower()
    if "manual" in text or refresh == "manual":
        return 55
    if any(token in text for token in ["federal reserve", "fred", "treasury", "new york fed", "sec companyfacts", "sec xbrl", "finra"]):
        return 95
    if "yahoo" in text:
        return 85
    if "cboe" in text or "occ" in text:
        return 72
    if "auto" in text:
        return 80
    return 60


def confidence_from_score(score: float) -> str:
    if score >= 85:
        return "high"
    if score >= 65:
        return "medium"
    return "low"


def mark_metric(metric: dict, refresh: str, used_in_score: bool, as_of: str | None = None) -> dict:
    if as_of is not None:
        metric["as_of"] = as_of
    cadence = metric.get("cadence") or refresh
    detail = freshness_detail(metric.get("as_of"), cadence)
    confidence_score = source_base_confidence(metric.get("source"), refresh)
    if detail["status"] == "aging":
        confidence_score -= 10
    elif detail["status"] == "stale":
        confidence_score -= 30
    elif detail["status"] == "unknown":
        confidence_score -= 15
    confidence_score = int(clamp(confidence_score, 0, 100))
    metric["refresh"] = refresh
    metric["cadence"] = cadence
    metric["used_in_score"] = used_in_score
    metric["freshness"] = detail["status"]
    metric["freshness_detail"] = detail
    metric["confidence_score"] = confidence_score
    metric["confidence"] = confidence_from_score(confidence_score)
    return metric


def value_to_float(value) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        if math.isnan(float(value)):
            return None
        return float(value)
    text = str(value).strip().replace(",", "")
    if text in {"", ".", "null", "None"}:
        return None
    try:
        return float(text)
    except Exception:
        return None


def fetch_fred_series(series_id: str) -> list[dict]:
    LOCAL_DATA.mkdir(parents=True, exist_ok=True)
    cache = LOCAL_DATA / f"fred-{series_id.lower()}.csv"
    url = FRED_CSV.format(series_id=urllib.parse.quote(series_id, safe=""))
    try:
        raw = fetch_bytes_with_curl(url, timeout=15).decode("utf-8")
        cache.write_text(raw, encoding="utf-8")
    except Exception:
        if not cache.exists():
            raise
        raw = cache.read_text(encoding="utf-8")

    rows = []
    for row in csv.DictReader(raw.splitlines()):
        value = value_to_float(row.get(series_id))
        if value is None:
            continue
        rows.append({"date": row.get("observation_date"), "value": value})
    return rows


def latest_fred_value(series_id: str) -> dict | None:
    rows = fetch_fred_series(series_id)
    return rows[-1] if rows else None


def fetch_json_cached(url: str, cache_name: str, timeout: int = 45, headers: dict | None = None) -> dict:
    LOCAL_DATA.mkdir(parents=True, exist_ok=True)
    cache = LOCAL_DATA / cache_name
    try:
        payload = json.loads(fetch_bytes(url, timeout=timeout, headers=headers).decode("utf-8"))
        cache.write_text(json.dumps(payload), encoding="utf-8")
    except Exception:
        if not cache.exists():
            raise
        payload = json.loads(cache.read_text(encoding="utf-8"))
    return payload


def duration_days(entry: dict) -> int | None:
    try:
        start = datetime.fromisoformat(entry["start"])
        end = datetime.fromisoformat(entry["end"])
    except Exception:
        return None
    return (end - start).days


def choose_sec_concept(companyfacts: dict, concepts: list[str]) -> tuple[str | None, list[dict]]:
    us_gaap = companyfacts.get("facts", {}).get("us-gaap", {})
    best_name = None
    best_entries: list[dict] = []
    best_end = ""
    for concept in concepts:
        entries = us_gaap.get(concept, {}).get("units", {}).get("USD", [])
        if not entries:
            continue
        latest_end = max((entry.get("end", "") for entry in entries), default="")
        if latest_end > best_end:
            best_name = concept
            best_entries = entries
            best_end = latest_end
    return best_name, best_entries


def quarter_label(date_text: str) -> str:
    dt = datetime.fromisoformat(date_text)
    return f"{dt.year}Q{((dt.month - 1) // 3) + 1}"


def quarter_order(fp: str | None) -> int | None:
    return {"Q1": 1, "Q2": 2, "Q3": 3, "FY": 4}.get(fp or "")


def quarterly_cashflow_series(entries: list[dict]) -> list[dict]:
    standalone = {}
    ytd = {}
    annual = {}
    for entry in entries:
        days = duration_days(entry)
        if days is None or entry.get("form") not in {"10-Q", "10-K"}:
            continue
        value = value_to_float(entry.get("val"))
        if value is None:
            continue
        filed_key = entry.get("filed", "")
        if 60 <= days <= 115 and entry.get("fp") != "FY":
            key = (entry.get("start"), entry.get("end"))
            if key not in standalone or filed_key >= standalone[key].get("filed", ""):
                standalone[key] = entry
        elif 150 <= days <= 310 and entry.get("fp") in {"Q2", "Q3"}:
            key = (entry.get("fy"), entry.get("fp"))
            if key not in ytd or filed_key >= ytd[key].get("filed", ""):
                ytd[key] = entry
        elif 330 <= days <= 380 and entry.get("form") == "10-K":
            key = entry.get("fy")
            if key not in annual or filed_key >= annual[key].get("filed", ""):
                annual[key] = entry

    quarters: dict[tuple[str | None, str | None], dict] = {}
    for entry in standalone.values():
        key = (entry.get("start"), entry.get("end"))
        quarters[key] = {
            "start": entry.get("start"),
            "end": entry.get("end"),
            "fy": entry.get("fy"),
            "fp": entry.get("fp"),
            "quarter": quarter_label(entry["end"]),
            "value": float(entry["val"]),
            "filed": entry.get("filed"),
            "form": entry.get("form"),
            "method": "standalone",
        }

    ytd_by_fy = {}
    for (fy, fp), entry in ytd.items():
        ytd_by_fy.setdefault(fy, {})[fp] = entry

    for fy, by_fp in ytd_by_fy.items():
        q1 = next((q for q in quarters.values() if q.get("fy") == fy and q.get("fp") == "Q1"), None)
        q2 = by_fp.get("Q2")
        q3 = by_fp.get("Q3")
        if q2 and q1:
            key = (q1["end"], q2.get("end"))
            if key not in quarters:
                quarters[key] = {
                    "start": q1["end"],
                    "end": q2.get("end"),
                    "fy": fy,
                    "fp": "Q2",
                    "quarter": quarter_label(q2["end"]),
                    "value": float(q2["val"]) - float(q1["value"]),
                    "filed": q2.get("filed"),
                    "form": q2.get("form"),
                    "method": "derived_from_ytd",
                }
        if q3 and q2:
            key = (q2.get("end"), q3.get("end"))
            if key not in quarters:
                quarters[key] = {
                    "start": q2.get("end"),
                    "end": q3.get("end"),
                    "fy": fy,
                    "fp": "Q3",
                    "quarter": quarter_label(q3["end"]),
                    "value": float(q3["val"]) - float(q2["val"]),
                    "filed": q3.get("filed"),
                    "form": q3.get("form"),
                    "method": "derived_from_ytd",
                }
        fy_entry = annual.get(fy)
        if fy_entry and q3:
            key = (q3.get("end"), fy_entry.get("end"))
            if key not in quarters:
                quarters[key] = {
                    "start": q3.get("end"),
                    "end": fy_entry.get("end"),
                    "fy": fy,
                    "fp": "Q4",
                    "quarter": quarter_label(fy_entry["end"]),
                    "value": float(fy_entry["val"]) - float(q3["val"]),
                    "filed": fy_entry.get("filed"),
                    "form": fy_entry.get("form"),
                    "method": "derived_from_annual",
                }

    clean = [row for row in quarters.values() if row["value"] >= 0]
    return sorted(clean, key=lambda row: (row["end"], row.get("filed") or ""))


def fetch_hyperscaler_capex() -> dict:
    companies = {}
    combined: dict[str, dict] = {}
    for symbol, cik in HYPERSCALERS.items():
        payload = fetch_json_cached(
            SEC_COMPANYFACTS.format(cik=cik),
            f"sec-{symbol.lower()}-companyfacts.json",
            timeout=45,
            headers={"User-Agent": SEC_USER_AGENT},
        )
        concept, entries = choose_sec_concept(payload, CAPEX_CONCEPTS)
        series = quarterly_cashflow_series(entries)
        companies[symbol] = {
            "cik": cik,
            "entity": payload.get("entityName"),
            "concept": concept,
            "series": series[-12:],
        }
        for row in series:
            bucket = combined.setdefault(row["quarter"], {"quarter": row["quarter"], "end": row["end"], "total": 0, "companies": {}})
            bucket["total"] += row["value"]
            bucket["end"] = max(bucket["end"], row["end"])
            bucket["companies"][symbol] = row["value"]

    combined_rows = [
        {
            "quarter": row["quarter"],
            "end": row["end"],
            "total_usd": row["total"],
            "total_usd_bn": row["total"] / 1e9,
            "company_count": len(row["companies"]),
            "companies": row["companies"],
        }
        for row in combined.values()
        if len(row["companies"]) >= 3
    ]
    combined_rows = sorted(combined_rows, key=lambda row: row["quarter"])
    complete = [row for row in combined_rows if row["company_count"] == len(HYPERSCALERS)]
    target_rows = complete if len(complete) >= 3 else combined_rows
    latest = target_rows[-1] if target_rows else None
    prev = target_rows[-2] if len(target_rows) >= 2 else None
    prev2 = target_rows[-3] if len(target_rows) >= 3 else None
    qoq_growth = latest["total_usd"] / prev["total_usd"] - 1 if latest and prev and prev["total_usd"] else None
    prev_qoq_growth = prev["total_usd"] / prev2["total_usd"] - 1 if prev and prev2 and prev2["total_usd"] else None
    qoq_delta = qoq_growth - prev_qoq_growth if qoq_growth is not None and prev_qoq_growth is not None else None

    snapshot = {
        "as_of": latest["end"] if latest else None,
        "latest_quarter": latest,
        "qoq_growth": qoq_growth,
        "qoq_delta": qoq_delta,
        "series": combined_rows[-12:],
        "companies": companies,
        "source": "SEC Companyfacts API",
        "note": "Combined reported cash CapEx / productive asset purchases for Microsoft, Amazon, Alphabet, and Meta. This is a hyperscaler CapEx proxy, not pure AI CapEx.",
    }
    (LOCAL_DATA / "hyperscaler_capex.json").write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    return snapshot


def fetch_liquidity_drain_snapshot() -> dict:
    errors = {}

    def safe_fred(series_id: str) -> dict | None:
        try:
            return latest_fred_value(series_id)
        except Exception as exc:
            errors[series_id] = str(exc)
            return None

    reserves = safe_fred("WRESBAL")
    tga = safe_fred("WTREGEN")
    sofr = safe_fred("SOFR")
    rrp_award = safe_fred("RRPONTSYAWARD")

    latest_repo_date = None
    latest_srf = None
    try:
        repo_payload = fetch_json_cached(
            "https://markets.newyorkfed.org/api/rp/repo/all/results/last/20.json",
            "nyfed-repo-last20.json",
            timeout=45,
        )
        operations = repo_payload.get("repo", {}).get("operations", [])
        latest_repo_date = max((op.get("operationDate", "") for op in operations), default=None)
        latest_srf = 0.0
        for op in operations:
            if op.get("operationDate") != latest_repo_date:
                continue
            for detail in op.get("details", []):
                if str(detail.get("securityType", "")).lower() == "srf":
                    latest_srf += float(detail.get("amtAccepted") or 0)
    except Exception as exc:
        errors["NYFED_REPO"] = str(exc)

    spread = None
    spread_as_of = None
    if sofr and rrp_award:
        spread = (sofr["value"] - rrp_award["value"]) * 100
        spread_as_of = min(sofr["date"], rrp_award["date"])

    snapshot = {
        "bank_reserves_usd_tn": reserves["value"] / 1_000_000 if reserves else None,
        "bank_reserves_as_of": reserves["date"] if reserves else None,
        "tga_usd_bn": tga["value"] / 1_000 if tga else None,
        "tga_as_of": tga["date"] if tga else None,
        "sofr_rrp_spread_bp": spread,
        "sofr_rrp_spread_as_of": spread_as_of,
        "srf_usage_usd_bn": latest_srf / 1_000_000_000 if latest_srf is not None else None,
        "srf_usage_as_of": latest_repo_date,
        "source": "FRED CSV and New York Fed Markets API",
        "errors": errors,
    }
    (LOCAL_DATA / "liquidity_drain_sources.json").write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    return snapshot


def parse_cboe_number(value: str) -> float | None:
    return value_to_float(html.unescape(value))


def fetch_cboe_options_snapshot() -> dict:
    LOCAL_DATA.mkdir(parents=True, exist_ok=True)
    cache = LOCAL_DATA / "cboe-options-daily.html"
    try:
        raw = fetch_bytes(CBOE_DAILY_OPTIONS, timeout=45, headers={"User-Agent": "Mozilla/5.0"}).decode("utf-8")
        cache.write_text(raw, encoding="utf-8")
    except Exception:
        if not cache.exists():
            raise
        raw = cache.read_text(encoding="utf-8")

    pattern = re.compile(
        r'<th[^>]*colSpan="4"[^>]*>([^<]+)</th>.*?'
        r'<tr[^>]*><td[^>]*>VOLUME</td><td[^>]*>([^<]+)</td><td[^>]*>([^<]+)</td><td[^>]*>([^<]+)</td></tr>',
        re.S,
    )
    products = {}
    for match in pattern.finditer(raw):
        name = html.unescape(match.group(1)).strip()
        call_volume = parse_cboe_number(match.group(2))
        put_volume = parse_cboe_number(match.group(3))
        total_volume = parse_cboe_number(match.group(4))
        products[name] = {
            "call_volume": call_volume,
            "put_volume": put_volume,
            "total_volume": total_volume,
            "call_share": call_volume / total_volume if call_volume is not None and total_volume else None,
        }

    spx = products.get("SPX + SPXW", {})
    all_products = products.get("SUM OF ALL PRODUCTS", {})
    index_options = products.get("INDEX OPTIONS", {})
    equity_options = products.get("EQUITY OPTIONS", {})
    spx_total = spx.get("total_volume")
    all_total = all_products.get("total_volume")
    index_total = index_options.get("total_volume")
    call_share = spx.get("call_share")
    spx_share = spx_total / all_total if spx_total and all_total else None
    index_call_share = index_options.get("call_share")
    equity_call_share = equity_options.get("call_share")
    call_skew_proxy = None
    if index_call_share is not None and equity_call_share is not None:
        call_skew_proxy = index_call_share - equity_call_share

    snapshot = {
        "as_of": datetime.now(timezone.utc).date().isoformat(),
        "spx_call_share": call_share,
        "spx_total_volume": spx_total,
        "spx_share_of_all_volume": spx_share,
        "index_total_volume": index_total,
        "index_call_share": index_call_share,
        "equity_call_share": equity_call_share,
        "call_skew_proxy": call_skew_proxy,
        "products": products,
        "source": "Cboe Daily Market Statistics page",
        "note": "Free Cboe page proxy. It captures SPX/SPXW call/put volume, not true dealer gamma or exact 0DTE share.",
    }
    (LOCAL_DATA / "cboe_options_daily.json").write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    return snapshot


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


def manual_metric_from_spec(name: str, spec: dict, inverse: bool = False, used_in_score: bool = True) -> dict:
    value = spec.get("value")
    score_fn = score_low_risk if inverse else score_high_risk
    return mark_metric({
        "name": name,
        "value": value,
        "score": score_fn(value, spec["low"], spec["high"]) if value is not None else None,
        "source": spec.get("source", "manual"),
        "range": {"low": spec["low"], "high": spec["high"]},
        "as_of": spec.get("as_of"),
        "note": spec.get("note"),
    }, "manual", used_in_score, spec.get("as_of"))


def auto_metric_from_value(
    name: str,
    value: float | None,
    low: float,
    high: float,
    source: str,
    as_of: str | None,
    note: str,
    inverse: bool = False,
    cadence: str = "daily",
    used_in_score: bool = True,
) -> dict:
    score_fn = score_low_risk if inverse else score_high_risk
    return mark_metric({
        "name": name,
        "value": value,
        "score": score_fn(value, low, high) if value is not None else None,
        "source": source,
        "range": {"low": low, "high": high},
        "as_of": as_of,
        "note": note,
        "cadence": cadence,
    }, cadence, used_in_score, as_of)


def build_ai_capex_metrics(ai_capex_specs: dict) -> tuple[list[dict], dict | None]:
    try:
        capex = fetch_hyperscaler_capex()
        latest_bn = capex.get("latest_quarter", {}).get("total_usd_bn") if capex.get("latest_quarter") else None
        metrics = [
            auto_metric_from_value(
                "Hyperscaler CapEx QoQ Growth",
                capex.get("qoq_growth"),
                ai_capex_specs["hyperscaler_capex_qoq_growth"]["low"],
                ai_capex_specs["hyperscaler_capex_qoq_growth"]["high"],
                "auto: SEC Companyfacts API",
                capex.get("as_of"),
                f"Combined MSFT/AMZN/GOOGL/META cash CapEx proxy. Latest quarter total: {latest_bn:.1f}B USD." if latest_bn else capex.get("note", ""),
                cadence="quarterly",
            ),
            auto_metric_from_value(
                "Hyperscaler CapEx QoQ Delta",
                capex.get("qoq_delta"),
                ai_capex_specs["hyperscaler_capex_qoq_delta"]["low"],
                ai_capex_specs["hyperscaler_capex_qoq_delta"]["high"],
                "auto: SEC Companyfacts API",
                capex.get("as_of"),
                "QoQ growth acceleration/deceleration. Negative acceleration is treated as a late-cycle death-signal candidate.",
                inverse=True,
                cadence="quarterly",
            ),
        ]
        return metrics, capex
    except Exception as exc:
        metrics = [
            manual_metric_from_spec("Hyperscaler CapEx QoQ Growth", ai_capex_specs["hyperscaler_capex_qoq_growth"]),
            manual_metric_from_spec("Hyperscaler CapEx QoQ Delta", ai_capex_specs["hyperscaler_capex_qoq_delta"], inverse=True),
        ]
        for metric in metrics:
            metric["fallback_reason"] = str(exc)
        return metrics, None


def build_liquidity_drain_metrics(liquidity_specs: dict) -> tuple[list[dict], dict | None]:
    try:
        liquidity = fetch_liquidity_drain_snapshot()
        errors = liquidity.get("errors", {})

        def auto_or_manual(key: str, auto_name: str, source: str, as_of_key: str, note: str, inverse: bool = False, cadence: str = "daily") -> dict:
            spec = liquidity_specs[key]
            value = liquidity.get(key)
            as_of = liquidity.get(as_of_key)
            if value is None or as_of is None:
                metric = manual_metric_from_spec(auto_name, spec, inverse=inverse)
                metric["fallback_reason"] = "; ".join(f"{k}: {v}" for k, v in errors.items()) or "Automatic source returned no value."
                return metric
            return auto_metric_from_value(
                auto_name,
                value,
                spec["low"],
                spec["high"],
                source,
                as_of,
                note,
                inverse=inverse,
                cadence=cadence,
            )

        metrics = [
            auto_or_manual(
                "bank_reserves_usd_tn",
                "Bank Reserves",
                "auto: FRED WRESBAL / Federal Reserve H.4.1",
                "bank_reserves_as_of",
                "Reserve balances with Federal Reserve Banks, converted to USD trillions. Lower reserves imply higher liquidity drain risk.",
                inverse=True,
                cadence="weekly",
            ),
            auto_or_manual(
                "tga_usd_bn",
                "Treasury General Account",
                "auto: FRED WTREGEN / Treasury General Account",
                "tga_as_of",
                "Treasury General Account balance, converted to USD billions. Higher TGA can drain private-sector liquidity.",
                cadence="weekly",
            ),
            auto_or_manual(
                "sofr_rrp_spread_bp",
                "SOFR - ON RRP Spread",
                "auto: FRED SOFR minus RRPONTSYAWARD",
                "sofr_rrp_spread_as_of",
                "Positive SOFR minus ON RRP award-rate spread proxies funding stress.",
                cadence="daily",
            ),
            auto_or_manual(
                "srf_usage_usd_bn",
                "Standing Repo Facility Usage",
                "auto: New York Fed Markets API repo operations",
                "srf_usage_as_of",
                "Accepted SRF tranche amount in recent repo operations. Zero is an observed value when no SRF tranche is used.",
                cadence="daily",
            ),
        ]
        return metrics, liquidity
    except Exception as exc:
        metrics = [
            manual_metric_from_spec("Bank Reserves", liquidity_specs["bank_reserves_usd_tn"], inverse=True),
            manual_metric_from_spec("Treasury General Account", liquidity_specs["tga_usd_bn"]),
            manual_metric_from_spec("SOFR - RRP Spread", liquidity_specs["sofr_rrp_spread_bp"]),
            manual_metric_from_spec("Standing Repo Facility Usage", liquidity_specs["srf_usage_usd_bn"]),
        ]
        for metric in metrics:
            metric["fallback_reason"] = str(exc)
        return metrics, None


def build_options_mechanical_metrics(options_specs: dict) -> tuple[list[dict], dict | None]:
    try:
        options = fetch_cboe_options_snapshot()
        core_call_heat = average_available(
            [
                score_high_risk(options.get("spx_call_share"), 0.38, 0.55),
                score_high_risk(options.get("spx_share_of_all_volume"), 0.25, 0.45),
            ],
            fallback=None,
        )
        call_premium_proxy = score_high_risk(options.get("call_skew_proxy"), -0.12, 0.08)
        metrics = [
            manual_metric_from_spec("0DTE Stress Share", options_specs["zero_dte_stress_share"]),
            auto_metric_from_value(
                "Call Premium / Call Skew Proxy",
                options.get("call_skew_proxy"),
                -0.12,
                0.08,
                "auto-proxy: Cboe Daily Market Statistics",
                options.get("as_of"),
                "Index call-share minus equity call-share. This is a free volume proxy, not an IV-skew truth source.",
                cadence="daily",
            ),
            auto_metric_from_value(
                "Core Call Volume Heat",
                core_call_heat / 100 if core_call_heat is not None else None,
                options_specs["core_call_volume_heat"]["low"],
                options_specs["core_call_volume_heat"]["high"],
                "auto-proxy: Cboe Daily Market Statistics",
                options.get("as_of"),
                "Composite of SPX/SPXW call share and SPX/SPXW share of all Cboe option volume.",
                cadence="daily",
            ),
        ]
        if metrics[1]["score"] is None and call_premium_proxy is not None:
            metrics[1]["score"] = call_premium_proxy
        metrics[0]["note"] = (metrics[0].get("note") or "") + " Free precise 0DTE share remains unavailable; kept as manual until a stable source is connected."
        return metrics, options
    except Exception as exc:
        metrics = [
            manual_metric_from_spec("0DTE Stress Share", options_specs["zero_dte_stress_share"]),
            manual_metric_from_spec("Call Premium Inversion", options_specs["call_premium_inversion"]),
            manual_metric_from_spec("Core Call Volume Heat", options_specs["core_call_volume_heat"]),
        ]
        for metric in metrics:
            metric["fallback_reason"] = str(exc)
        return metrics, None


def build_top_fragility_overlay(config: dict) -> dict:
    fragility = config.get("top_fragility", {})

    ai_capex_specs = fragility.get("ai_capex_cycle", {})
    liquidity_specs = fragility.get("liquidity_drain", {})
    options_specs = fragility.get("options_mechanical_bid", {})

    ai_capex_metrics, ai_capex_source = build_ai_capex_metrics(ai_capex_specs)
    liquidity_metrics, liquidity_source = build_liquidity_drain_metrics(liquidity_specs)
    options_metrics, options_source = build_options_mechanical_metrics(options_specs)

    groups = {
        "ai_capex_cycle": ai_capex_metrics,
        "liquidity_drain": liquidity_metrics,
        "options_mechanical_bid": options_metrics,
    }

    group_scores = {
        name: average_available([metric["score"] for metric in metrics])
        for name, metrics in groups.items()
    }
    score = average_available(list(group_scores.values()))

    return {
        "score": round(score, 1),
        "groups": {
            name: {
                "score": round(group_scores[name], 1),
                "metrics": metrics,
            }
            for name, metrics in groups.items()
        },
        "principle": {
            "summary": "AI late-cycle fragility is tracked through hyperscaler capex acceleration, liquidity drain, and options-driven mechanical buying pressure.",
            "use": "Use this overlay to upgrade or downgrade top-risk interpretation when price and leverage signals are already elevated.",
            "limits": "Liquidity and hyperscaler CapEx now use official free sources. Options crowding still uses free proxies; exact 0DTE share and dealer gamma remain manual or paid-data problems.",
        },
        "sources": {
            "ai_capex_cycle": ai_capex_source,
            "liquidity_drain": liquidity_source,
            "options_mechanical_bid": options_source,
        },
    }


def collect_metric_dicts(value) -> list[dict]:
    found = []
    if isinstance(value, dict):
        if "name" in value and "source" in value and "freshness" in value:
            found.append(value)
        for child in value.values():
            found.extend(collect_metric_dicts(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(collect_metric_dicts(child))
    return found


def build_data_quality_snapshot(snapshot: dict) -> dict:
    metrics = collect_metric_dicts(
        {
            "core_metrics": snapshot.get("core_metrics"),
            "context_metrics": snapshot.get("metrics"),
            "top_fragility_overlay": snapshot.get("top_fragility_overlay"),
            "bottom_framework": snapshot.get("bottom_framework"),
            "micron_canary": snapshot.get("micron_canary"),
        }
    )
    total = len(metrics)
    used = [metric for metric in metrics if metric.get("used_in_score")]
    auto = [metric for metric in metrics if metric.get("refresh") != "manual"]
    manual = [metric for metric in metrics if metric.get("refresh") == "manual"]
    freshness_scores = [metric.get("freshness_detail", {}).get("score") for metric in metrics if metric.get("freshness_detail")]
    confidence_scores = [metric.get("confidence_score") for metric in metrics if metric.get("confidence_score") is not None]

    def count_status(name: str) -> int:
        return sum(1 for metric in metrics if metric.get("freshness") == name)

    low_confidence_used = [
        {
            "name": metric.get("name"),
            "source": metric.get("source"),
            "confidence": metric.get("confidence"),
            "confidence_score": metric.get("confidence_score"),
            "freshness": metric.get("freshness"),
            "as_of": metric.get("as_of"),
        }
        for metric in used
        if metric.get("confidence_score", 100) < 65
    ][:12]
    stale_used = [
        {
            "name": metric.get("name"),
            "source": metric.get("source"),
            "freshness": metric.get("freshness"),
            "as_of": metric.get("as_of"),
            "age_days": metric.get("freshness_detail", {}).get("age_days"),
        }
        for metric in used
        if metric.get("freshness") in {"stale", "unknown"}
    ][:12]
    manual_used = [
        {
            "name": metric.get("name"),
            "source": metric.get("source"),
            "as_of": metric.get("as_of"),
            "freshness": metric.get("freshness"),
            "confidence_score": metric.get("confidence_score"),
        }
        for metric in used
        if metric.get("refresh") == "manual"
    ][:12]

    section_breakdown = []
    for section, payload in {
        "core_metrics": snapshot.get("core_metrics"),
        "context_metrics": snapshot.get("metrics"),
        "top_fragility_overlay": snapshot.get("top_fragility_overlay"),
        "bottom_framework": snapshot.get("bottom_framework"),
        "micron_canary": snapshot.get("micron_canary"),
    }.items():
        rows = collect_metric_dicts(payload)
        if not rows:
            continue
        section_breakdown.append(
            {
                "section": section,
                "total": len(rows),
                "auto": sum(1 for row in rows if row.get("refresh") != "manual"),
                "manual": sum(1 for row in rows if row.get("refresh") == "manual"),
                "fresh": sum(1 for row in rows if row.get("freshness") == "fresh"),
                "aging": sum(1 for row in rows if row.get("freshness") == "aging"),
                "stale": sum(1 for row in rows if row.get("freshness") == "stale"),
                "unknown": sum(1 for row in rows if row.get("freshness") == "unknown"),
                "confidence_score": round(average_available([row.get("confidence_score") for row in rows]), 1),
            }
        )

    return {
        "summary": {
            "total_metrics": total,
            "used_metrics": len(used),
            "auto_metrics": len(auto),
            "manual_metrics": len(manual),
            "auto_coverage_pct": round(len(auto) / total * 100, 1) if total else None,
            "freshness_score": round(average_available(freshness_scores), 1),
            "confidence_score": round(average_available(confidence_scores), 1),
            "fresh": count_status("fresh"),
            "aging": count_status("aging"),
            "stale": count_status("stale"),
            "unknown": count_status("unknown"),
        },
        "issues": {
            "stale_or_unknown_used": stale_used,
            "low_confidence_used": low_confidence_used,
            "manual_used": manual_used,
        },
        "section_breakdown": section_breakdown,
        "method": {
            "freshness": "Daily, weekly, monthly, quarterly, and manual fields are scored against different age windows.",
            "confidence": "Official sources score highest; Yahoo and Cboe proxies are medium; manual fields are lower and decay when stale.",
        },
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
    top_fragility_overlay = build_top_fragility_overlay(config)
    micron_canary = None
    if build_micron_canary_snapshot:
        try:
            micron_canary = build_micron_canary_snapshot(
                config,
                top_fragility_overlay["groups"]["liquidity_drain"]["score"],
            )
        except Exception as exc:
            micron_canary = {
                "available": False,
                "error": str(exc),
            }
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
    core_ai_fragility_score = top_fragility_overlay["score"]

    modules = {
        "price_confirmation": core_price_score,
        "finra_margin_slow": core_finra_score,
        "daily_leverage_proxy": core_daily_proxy_score,
        "ai_fragility_overlay": core_ai_fragility_score,
    }
    overall = (
        modules["price_confirmation"] * 0.30
        + modules["finra_margin_slow"] * 0.25
        + modules["daily_leverage_proxy"] * 0.15
        + modules["ai_fragility_overlay"] * 0.30
    )

    warnings = []
    if core_finra_score >= 80:
        warnings.append("FINRA margin leverage is in a historically high zone.")
    if core_daily_proxy_score >= 75:
        warnings.append("QQQ/TQQQ daily leverage proxy is elevated.")
    if core_ai_fragility_score >= 70:
        warnings.append("AI fragility overlay is elevated across capex, liquidity, or option-mechanical signals.")
    liquidity_group = top_fragility_overlay["groups"]["liquidity_drain"]["score"]
    if liquidity_group >= 70:
        warnings.append("Liquidity drain inputs are in a warning zone; watch reserves, TGA, SOFR/RRP, and SRF.")
    capex_group = top_fragility_overlay["groups"]["ai_capex_cycle"]["score"]
    if capex_group >= 70:
        warnings.append("AI capex-cycle inputs suggest late-cycle acceleration or deceleration risk.")
    if price["distance_200dma"] and price["distance_200dma"] > 0.18:
        warnings.append("QQQ is extended above its 200-day moving average.")
    if price["drawdown_from_52w_high"] and price["drawdown_from_52w_high"] < -0.05 and overall > 60:
        warnings.append("Price has pulled back from highs while bubble pressure remains high.")

    snapshot = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "market": "NASDAQ / QQQ",
        "manual_inputs": config.get("_meta", {}),
        "overall_score": round(overall, 1),
        "status": status_for(overall, modules),
        "modules": {k: round(v, 1) for k, v in modules.items()},
        "score_policy": {
            "name": "Core Daily Score",
            "description": "Automatic daily proxies, explicit-frequency slow variables, and the AI fragility overlay enter the top-risk score. Manual overlay fields are labeled and excluded when missing.",
            "weights": {
                "price_confirmation": 0.30,
                "finra_margin_slow": 0.25,
                "daily_leverage_proxy": 0.15,
                "ai_fragility_overlay": 0.30
            }
        },
        "price": price,
        "finra": finra,
        "top_fragility_overlay": top_fragility_overlay,
        "micron_canary": micron_canary,
        "bottom_framework": bottom_framework,
        "core_metrics": {
            "price": [price_metric],
            "finra_margin_slow": [finra_metric] if finra_metric else [],
            "daily_leverage_proxy": daily_proxy_metrics,
            "ai_fragility_overlay": [
                metric
                for group in top_fragility_overlay["groups"].values()
                for metric in group["metrics"]
            ],
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
    snapshot["data_quality"] = build_data_quality_snapshot(snapshot)
    quality = snapshot["data_quality"]["summary"]
    if quality.get("confidence_score") is not None and quality["confidence_score"] < 70:
        warnings.append("Data confidence is below the preferred threshold; inspect manual and proxy inputs before acting.")
    if snapshot["data_quality"]["issues"]["stale_or_unknown_used"]:
        warnings.append("Some scoring inputs are stale or have unknown freshness; check the data quality panel.")
    return snapshot


def main() -> int:
    DOCS_DATA.mkdir(parents=True, exist_ok=True)
    snapshot = build_snapshot()
    (DOCS_DATA / "dashboard.json").write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    if snapshot.get("micron_canary"):
        (LOCAL_DATA / "micron_canary_score.json").write_text(
            json.dumps(snapshot["micron_canary"], indent=2),
            encoding="utf-8",
        )
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
