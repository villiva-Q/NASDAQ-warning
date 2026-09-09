"""Read existing SEC cache bodies and compare them with the frozen sample parser.

Run with the repository's Python environment and PYTHONPATH=packages:packages/platform.
This is an offline diagnostic, not a replacement parser or a source of screening facts.
Tar members are read in memory; no files are extracted, no database is accessed.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import tarfile
from datetime import datetime
from pathlib import Path

from connectors.sec_edgar import SecSampleParseError, SecSampleScreenParser


def read_bodies(path: Path) -> dict:
    bodies = {}
    with tarfile.open(path) as archive:
        for member in archive.getmembers():
            if not member.isfile() or Path(member.name).name != "body":
                continue
            stream = archive.extractfile(member)
            assert stream is not None
            raw = stream.read()
            document = json.loads(gzip.decompress(raw) if raw.startswith(b"\x1f\x8b") else raw)
            cik = str(document["cik"]).zfill(10)
            endpoint = "companyfacts" if "facts" in document else "submissions"
            if (endpoint, cik) in bodies:
                raise ValueError(f"duplicate source body: {endpoint}/{cik}")
            bodies[endpoint, cik] = (raw, document, member.name)
    return bodies


def diagnose(archive_path: Path, config_path: Path) -> dict:
    config = json.loads(config_path.read_bytes())
    cutoff = datetime.fromisoformat(config["point_in_time_cutoff"].replace("Z", "+00:00"))
    bodies = read_bodies(archive_path)
    parser = SecSampleScreenParser()
    companies = []
    for company in config["companies"]:
        cik = company["cik"]
        responses = {key: bodies[key][0] for key in (("submissions", cik), ("companyfacts", cik))}
        document = bodies["companyfacts", cik][1]
        try:
            filing = parser._filing(bodies["submissions", cik][1], cutoff)
        except SecSampleParseError as error:
            companies.append(
                {
                    "ticker": company["ticker"],
                    "cik": cik,
                    "industry_route": company["industry_route"],
                    "filing": None,
                    "filing_selection_error": str(error),
                    "fields": [],
                    "unmapped_source_candidates": [],
                    "historical_submission_files": bodies["submissions", cik][1]
                    .get("filings", {})
                    .get("files", []),
                    "sources": [
                        {
                            "endpoint": endpoint,
                            "sha256": hashlib.sha256(bodies[endpoint, cik][0]).hexdigest(),
                            "archive_member": bodies[endpoint, cik][2],
                        }
                        for endpoint in ("submissions", "companyfacts")
                    ],
                }
            )
            continue
        fy, fp = parser._filing_fiscal_context(document, filing=filing, cutoff=cutoff)
        filing = {**filing, "fy": fy, "fp": fp}
        parsed = json.loads(parser.parse(responses, cutoff=cutoff))["records"][0]
        selected = {row["metric"]: row for row in parsed["facts"]}
        fields = []
        for namespace, tag, metric, _, unit, context in parser._FACT_TAGS:
            observations = (
                document.get("facts", {})
                .get(namespace, {})
                .get(tag, {})
                .get("units", {})
                .get(unit, [])
            )
            accession_rows = [
                row
                for row in observations
                if row.get("accn") == filing["accessionNumber"]
                and row.get("form") == filing["form"]
                and row.get("filed", "9999") <= cutoff.date().isoformat()
            ]
            period_rows = [
                row
                for row in accession_rows
                if row.get("end") == filing["reportDate"]
                and parser._normalized_fiscal_period(row) == (fy, fp)
            ]
            if metric in selected:
                reason = "selected_by_baseline"
            elif not observations:
                reason = "taxonomy_or_unit_absent_in_archive"
            elif not accession_rows:
                reason = "no_selected_accession_observation"
            elif not period_rows:
                reason = "report_end_or_fiscal_context_mismatch"
            elif all(not isinstance(row.get("frame"), str) for row in period_rows):
                reason = "baseline_requires_frame_but_source_has_none"
            else:
                reason = "baseline_context_filter_rejected"
            fields.append(
                {
                    "metric": metric,
                    "taxonomy": f"{namespace}:{tag}",
                    "unit": unit,
                    "context": context,
                    "reason": reason,
                    "source_pointer": f"/facts/{namespace}/{tag}/units/{unit}",
                    "selected": selected.get(metric),
                    "accession_observations": accession_rows,
                    "report_end_observations": period_rows,
                }
            )
        unmapped = []
        mapped_tags = {(row[0], row[1]) for row in parser._FACT_TAGS}
        for namespace, tags in document.get("facts", {}).items():
            for tag, definition in tags.items():
                if (namespace, tag) in mapped_tags:
                    continue
                if not any(
                    term in tag
                    for term in (
                        "Debt",
                        "Revenue",
                        "SharesOutstanding",
                        "CashAndCashEquivalents",
                        "CashFlowsFromUsedInOperatingActivities",
                        "ProfitLoss",
                        "AdjustedWeightedAverageShares",
                    )
                ):
                    continue
                for unit, observations in definition.get("units", {}).items():
                    rows = [
                        row
                        for row in observations
                        if row.get("accn") == filing["accessionNumber"]
                        and row.get("filed", "9999") <= cutoff.date().isoformat()
                    ]
                    if rows:
                        unmapped.append(
                            {"taxonomy": f"{namespace}:{tag}", "unit": unit, "observations": rows}
                        )
        companies.append(
            {
                "ticker": company["ticker"],
                "cik": cik,
                "industry_route": company["industry_route"],
                "filing": filing,
                "fields": fields,
                "unmapped_source_candidates": unmapped,
                "sources": [
                    {
                        "endpoint": endpoint,
                        "sha256": hashlib.sha256(bodies[endpoint, cik][0]).hexdigest(),
                        "archive_member": bodies[endpoint, cik][2],
                    }
                    for endpoint in ("submissions", "companyfacts")
                ],
            }
        )
    return {
        "diagnostic_only": True,
        "cutoff": config["point_in_time_cutoff"],
        "companies": companies,
    }


if __name__ == "__main__":
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("archive", type=Path)
    args.add_argument("--config", type=Path, default=Path("config/l18_limited_real_sample.v1.json"))
    args.add_argument("--output", type=Path, required=True)
    options = args.parse_args()
    options.output.write_text(
        json.dumps(
            diagnose(options.archive, options.config), ensure_ascii=False, indent=2, sort_keys=True
        )
        + "\n",
        encoding="utf-8",
    )
