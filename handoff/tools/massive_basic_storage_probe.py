"""Bounded, owner-authorized Basic API/storage evaluation; independent of production."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
import zipfile

API = "https://api.massive.com"
SECRET = Path("/srv/cargoq/.market-data-secrets/massive_api_key")


def stamp():
    return datetime.now(timezone.utc).isoformat()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def analyze(entries, root):
    output = []
    for entry in entries:
        body = (root / entry["file"]).read_bytes()
        if hashlib.sha256(body).hexdigest() != entry["sha256"]:
            raise ValueError("snapshot_integrity_mismatch")
        obj = json.loads(body)
        rows = obj.get("results", []) if isinstance(obj, dict) else []
        rows = [rows] if isinstance(rows, dict) else rows
        if not isinstance(rows, list):
            raise ValueError("results_shape_invalid")
        item = {"label": entry["label"], "http_status": entry["http_status"], "rows": len(rows)}
        if entry["kind"] == "bars" and rows:
            times = [r["t"] for r in rows]
            required = {"o", "h", "l", "c", "v", "t"}
            item.update({
                "first_date": datetime.fromtimestamp(min(times)/1000, timezone.utc).date().isoformat(),
                "last_date": datetime.fromtimestamp(max(times)/1000, timezone.utc).date().isoformat(),
                "adjusted": obj.get("adjusted"),
                "unique_timestamps": len(times) == len(set(times)),
                "ordered_timestamps": times == sorted(times),
                "required_fields_present": all(required <= r.keys() for r in rows),
                "ohlcv_valid": all(0 < r["l"] <= min(r["o"], r["c"]) <= max(r["o"], r["c"]) <= r["h"] and r["v"] >= 0 for r in rows),
                "close_average": sum(r["c"] for r in rows) / len(rows),
            })
        elif entry["kind"] == "grouped" and rows:
            symbols=[r.get("T") for r in rows]
            item.update({"adjusted":obj.get("adjusted"),"unique_symbols":len(symbols)==len(set(symbols)),
                         "selected_symbols_present":{s:s in symbols for s in ("AAPL","KO","PARA","BRK.B","GOOG","GOOGL")},
                         "required_fields_present":all({"T","o","h","l","c","v","t"} <= r.keys() for r in rows)})
        elif entry["kind"] == "identity" and rows:
            r = rows[0]
            item["identity"] = {k:r.get(k) for k in ("ticker", "cik", "composite_figi", "share_class_figi", "primary_exchange", "type", "currency_name")}
        elif entry["kind"] in ("splits", "dividends") and rows:
            name = "execution_date" if entry["kind"] == "splits" else "ex_dividend_date"
            dates = [r[name] for r in rows if r.get(name)]
            item.update({"first_event_date": min(dates) if dates else None, "last_event_date": max(dates) if dates else None,
                         "unique_ids": len({r.get("id") for r in rows}) == len(rows)})
        output.append(item)
    return output


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def collect(root, grouped_only=False):
    root.mkdir(parents=True, exist_ok=False)
    (root / "raw").mkdir()
    key = SECRET.read_text().strip()
    if not key or not key.isascii() or any(c.isspace() or ord(c)<33 or ord(c)>126 for c in key):
        raise ValueError("credential_format_invalid")
    opener = urllib.request.build_opener(NoRedirect())
    jobs = []
    for ticker, day, start in [("AAPL","2024-11-01","2024-10-31"),("KO","2024-11-15","2024-11-14"),
                               ("PARA","2024-11-15","2024-11-14"),("BRK.B","2024-11-01","2024-10-31"),
                               ("GOOG","2024-11-01","2024-10-31"),("GOOGL","2024-11-01","2024-10-31")]:
        jobs += [(ticker+"_identity", "identity", f"/v3/reference/tickers/{ticker}?date={day}"),
                 (ticker+"_bars", "bars", f"/v2/aggs/ticker/{ticker}/range/1/day/{start}/{day}?adjusted=false&sort=asc&limit=100")]
    jobs += [
        ("AAPL_two_year_bars", "bars", "/v2/aggs/ticker/AAPL/range/1/day/2024-09-09/2026-09-04?adjusted=false&sort=asc&limit=50000"),
        ("AAPL_outside_window_bars", "bars", "/v2/aggs/ticker/AAPL/range/1/day/2024-08-01/2024-08-02?adjusted=false&sort=asc&limit=100"),
        ("AAPL_outside_window_identity", "identity", "/v3/reference/tickers/AAPL?date=2024-08-01"),
        ("AAPL_splits", "splits", "/stocks/v1/splits?ticker=AAPL&limit=100"),
        ("AAPL_dividends_page1", "dividends", "/stocks/v1/dividends?ticker=AAPL&limit=20&sort=ex_dividend_date.asc"),
    ]
    if grouped_only:
        jobs=[("market_daily_20241101","grouped","/v2/aggs/grouped/locale/us/market/stocks/2024-11-01?adjusted=false&include_otc=false")]
    entries = []
    last_start = 0.0
    begun = stamp()
    page_urls = set()
    while jobs:
        if len(entries) >= 25:
            raise ValueError("bounded_request_budget_exceeded")
        label, kind, path = jobs.pop(0)
        target = urllib.parse.urlsplit(path if path.startswith("https://") else API+path)
        if target.scheme != "https" or target.netloc != "api.massive.com":
            raise ValueError("unexpected_pagination_origin")
        query = [(k,v) for k,v in urllib.parse.parse_qsl(target.query) if k.lower() != "apikey"]
        url = urllib.parse.urlunsplit((target.scheme,target.netloc,target.path,urllib.parse.urlencode(query),""))
        delay = 13-(time.monotonic()-last_start)
        if delay>0:
            time.sleep(delay)
        started = stamp()
        last_start = time.monotonic()
        req = urllib.request.Request(url, headers={"Authorization":"Bearer "+key,"User-Agent":"cargoq-basic-storage-evaluation/1.0"})
        try:
            response = opener.open(req, timeout=25)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            code = response.code
            body = response.read(10_000_001)
        if len(body)>10_000_000 or key.encode() in body:
            raise ValueError("response_not_safe_to_store")
        # This output directory is an owner-only evaluation archive, outside Git.
        file = f"raw/{len(entries)+1:02d}_{label}.json"
        (root/file).write_bytes(body)
        obj = json.loads(body)
        if not isinstance(obj,dict):
            raise ValueError("response_shape_invalid")
        next_url = obj.get("next_url")
        entry = {"label":label,"kind":kind,"source_url":url,"started_at":started,"fetched_at":stamp(),
                 "http_status":code,"api_status":obj.get("status") if obj.get("status") in ("OK","ERROR","NOT_AUTHORIZED","DELAYED") else "other",
                 "file":file,"sha256":hashlib.sha256(body).hexdigest(),"bytes":len(body),"has_next_page":bool(next_url)}
        entries.append(entry)
        save(root/"manifest.json", {"begun_at":begun,"updated_at":stamp(),"entries":entries})
        count = len(obj.get("results",[])) if isinstance(obj.get("results"),list) else 1 if isinstance(obj.get("results"),dict) else 0
        print(json.dumps({"label":label,"http_status":code,"rows":count,"has_next_page":bool(next_url)}),flush=True)
        if next_url and 200<=code<300:
            if next_url in page_urls:
                raise ValueError("pagination_cycle")
            page_urls.add(next_url)
            jobs.append((label.split("_page")[0]+f"_page{len(page_urls)+1}",kind,next_url))
    derived = analyze(entries,root)
    save(root/"derived_report.json",derived)
    with zipfile.ZipFile(root/"backup.zip","w",compression=zipfile.ZIP_DEFLATED) as z:
        for file in [root/"manifest.json",root/"derived_report.json",*sorted((root/"raw").iterdir())]:
            z.write(file,file.relative_to(root))
    save(root/"collection_summary.json",{"completed_at":stamp(),"request_count":len(entries),
         "http_200_count":sum(x["http_status"]==200 for x in entries),"raw_bytes":sum(x["bytes"] for x in entries),
         "storage_root":str(root),"license_status":"provider_reply_pending","long_elapsed_time_tested":False})
    print("COLLECTION_COMPLETE "+str(root),flush=True)


def verify(root):
    # Called in a fresh process with an isolated network namespace. Never reads SECRET.
    isolated = False
    try:
        with socket.create_connection(("1.1.1.1",443),timeout=1):
            pass
    except OSError:
        isolated = True
    manifest=json.loads((root/"manifest.json").read_text())
    expected=json.loads((root/"derived_report.json").read_text())
    actual=analyze(manifest["entries"],root)
    if actual!=expected:
        raise ValueError("offline_result_mismatch")
    restored=Path(tempfile.mkdtemp(prefix="restored-",dir=root))
    with zipfile.ZipFile(root/"backup.zip") as z:
        z.extractall(restored)
    if analyze(manifest["entries"],restored)!=expected:
        raise ValueError("restored_result_mismatch")
    # Alter only the disposable restored copy, proving bad input is detected.
    first=restored/manifest["entries"][0]["file"]
    first.write_bytes(first.read_bytes()+b" ")
    caught=False
    try:
        analyze(manifest["entries"],restored)
    except ValueError as error:
        caught=str(error)=="snapshot_integrity_mismatch"
    result={"verified_at":stamp(),"fresh_process_replay_equal":actual==expected,
            "network_unavailable":isolated,"secret_read":False,"backup_restore_equal":True,
            "corrupt_copy_detected":caught,"original_archive_preserved":True,
            "long_elapsed_time_tested":False}
    save(root/"offline_verification.json",result)
    print(json.dumps(result),flush=True)
    if not isolated or not caught:
        raise ValueError("verification_incomplete")


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("mode",choices=("collect","collect-grouped","verify"))
    parser.add_argument("root",type=Path)
    args=parser.parse_args()
    os.umask(0o077)
    try:
        if args.mode=="verify":
            verify(args.root)
        else:
            collect(args.root,grouped_only=args.mode=="collect-grouped")
    except Exception as error:
        print(json.dumps({"error_type":type(error).__name__}),flush=True)
        raise SystemExit(1)
