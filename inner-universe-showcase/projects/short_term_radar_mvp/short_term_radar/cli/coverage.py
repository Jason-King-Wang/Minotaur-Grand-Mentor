from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
from typing import Any

from short_term_radar.data_sources.config import load_data_source_config
from short_term_radar.data_sources.registry import DATASET_REGISTRY, build_collect_plan
from short_term_radar.data_sources.storage import processed_path, quality_path, read_processed_rows
from short_term_radar.utils.io import write_csv


DATA_COVERAGE_FIELDS = [
    "dataset",
    "processed_table",
    "market",
    "start_date_or_month",
    "end_date_or_month",
    "expected_count",
    "actual_count",
    "coverage_ratio",
    "missing_count",
    "source",
    "generated_at",
]

MISSING_DATES_FIELDS = ["dataset", "market", "missing_date_or_month", "reason", "severity"]

FRESHNESS_FIELDS = [
    "dataset",
    "market",
    "latest_available_date_or_month",
    "expected_latest_date_or_month",
    "lag_days",
    "freshness_status",
    "generated_at",
]

EVENT_DRIVEN_DATASETS = {"material_events", "corporate_actions"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Report processed data coverage.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--write-reports", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    config = load_data_source_config(args.config)
    if args.write_reports and not args.dry_run:
        reports = generate_coverage_reports(config, args.start, args.end)
        coverage_output = quality_path(config, "data_coverage_report.csv")
        missing_output = quality_path(config, "missing_dates_report.csv")
        freshness_output = quality_path(config, "freshness_report.csv")
        write_csv(coverage_output, reports["coverage"], DATA_COVERAGE_FIELDS)
        write_csv(missing_output, reports["missing"], MISSING_DATES_FIELDS)
        write_csv(freshness_output, reports["freshness"], FRESHNESS_FIELDS)
        print(f"Wrote data coverage report to {coverage_output}")
        print(f"Wrote missing dates report to {missing_output}")
        print(f"Wrote freshness report to {freshness_output}")
        return 0

    for name, spec in DATASET_REGISTRY.items():
        path = processed_path(config, name)
        if args.dry_run:
            print(f"[dry-run] {spec.processed_table}: expected range {args.start}..{args.end}, path={path}")
            continue
        rows = read_processed_rows(config, name)
        print(f"{spec.processed_table}: rows={len(rows)} path={path}")
    return 0


def generate_coverage_reports(config: dict[str, Any], start: str, end: str) -> dict[str, list[dict[str, Any]]]:
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    coverage_rows: list[dict[str, Any]] = []
    missing_rows: list[dict[str, Any]] = []
    freshness_rows: list[dict[str, Any]] = []
    trading_dates = _trading_dates_from_prices(config, start, end)

    for name, spec in DATASET_REGISTRY.items():
        rows = read_processed_rows(config, name)
        date_column = _date_column(spec.processed_table)
        markets = sorted({str(row.get("market")) for row in rows if row.get("market")} or set(spec.markets))
        for market in markets:
            market_rows = [row for row in rows if str(row.get("market") or market) == market]
            event_driven = name in EVENT_DRIVEN_DATASETS
            source_missing = name == "surveillance" and not market_rows and not _has_enabled_download_source(config, name, market)
            expected_values = [] if event_driven or source_missing else _expected_values(date_column, start, end, trading_dates)
            actual_values = {
                _date_or_month(row.get(date_column), date_column)
                for row in market_rows
                if _in_coverage_window(_date_or_month(row.get(date_column), date_column), date_column, start, end)
            }
            if expected_values:
                actual_values = {value for value in actual_values if value in expected_values}
            missing_values = [value for value in expected_values if value not in actual_values]
            expected_count = len(expected_values)
            actual_count = len(actual_values)
            coverage_ratio = actual_count / expected_count if expected_count else 1.0
            coverage_rows.append(
                {
                    "dataset": name,
                    "processed_table": spec.processed_table,
                    "market": market,
                    "start_date_or_month": expected_values[0] if expected_values else "",
                    "end_date_or_month": expected_values[-1] if expected_values else "",
                    "expected_count": expected_count,
                    "actual_count": actual_count,
                    "coverage_ratio": round(coverage_ratio, 4),
                    "missing_count": len(missing_values),
                    "source": "source_missing" if source_missing else _source_label(market_rows),
                    "generated_at": generated_at,
                }
            )
            for missing in missing_values:
                missing_rows.append(
                    {
                        "dataset": name,
                        "market": market,
                        "missing_date_or_month": missing,
                        "reason": "processed row not found",
                        "severity": "warning",
                    }
                )
            latest = max(actual_values) if actual_values else ""
            expected_latest = expected_values[-1] if expected_values else end[:10]
            lag_days = _lag_days(latest, expected_latest, date_column)
            freshness_rows.append(
                {
                    "dataset": name,
                    "market": market,
                    "latest_available_date_or_month": latest,
                    "expected_latest_date_or_month": expected_latest,
                    "lag_days": lag_days,
                    "freshness_status": "source_missing" if source_missing else "fresh" if lag_days == 0 else "stale",
                    "generated_at": generated_at,
                }
            )

    return {"coverage": coverage_rows, "missing": missing_rows, "freshness": freshness_rows}


def _date_column(processed_table: str) -> str:
    if processed_table == "monthly_revenue":
        return "revenue_month"
    if processed_table == "material_events":
        return "announce_date"
    if processed_table == "corporate_actions":
        return "action_date"
    if processed_table in {"financial_statement_quarterly"}:
        return "announce_date"
    if processed_table == "insider_holding_monthly":
        return "data_month"
    return "trade_date"


def _expected_values(date_column: str, start: str, end: str, trading_dates: list[str] | None = None) -> list[str]:
    if date_column in {"revenue_month", "data_month"}:
        return _month_values(start, end)
    if trading_dates:
        return trading_dates
    return _weekday_values(start, end)


def _date_values(start: str, end: str) -> list[str]:
    start_date = date.fromisoformat(start[:10])
    end_date = date.fromisoformat(end[:10])
    values: list[str] = []
    current = start_date
    while current <= end_date:
        values.append(current.isoformat())
        current = date.fromordinal(current.toordinal() + 1)
    return values


def _weekday_values(start: str, end: str) -> list[str]:
    return [
        value
        for value in _date_values(start, end)
        if date.fromisoformat(value).weekday() < 5
    ]


def _month_values(start: str, end: str) -> list[str]:
    year = int(start[:4])
    month = int(start[5:7] if "-" in start else start[4:6])
    end_year = int(end[:4])
    end_month = int(end[5:7] if "-" in end else end[4:6])
    values: list[str] = []
    while (year, month) <= (end_year, end_month):
        values.append(f"{year:04d}{month:02d}")
        month += 1
        if month == 13:
            year += 1
            month = 1
    return values


def _date_or_month(value: Any, date_column: str) -> str:
    if value is None:
        return ""
    text = str(value)
    if date_column in {"revenue_month", "data_month"}:
        return text[:7].replace("-", "") if "-" in text[:7] else text[:6]
    return text[:10]


def _in_coverage_window(value: str, date_column: str, start: str, end: str) -> bool:
    if not value:
        return False
    if date_column in {"revenue_month", "data_month"}:
        start_month = start[:7].replace("-", "") if "-" in start[:7] else start[:6]
        end_month = end[:7].replace("-", "") if "-" in end[:7] else end[:6]
        return start_month <= value <= end_month
    return start[:10] <= value <= end[:10]


def _source_label(rows: list[dict[str, Any]]) -> str:
    sources = sorted({str(row.get("source")) for row in rows if row.get("source")})
    return ",".join(sources)


def _lag_days(latest: str, expected: str, date_column: str) -> int:
    if not latest or not expected:
        return 999999
    if date_column in {"revenue_month", "data_month"}:
        latest_date = date(int(latest[:4]), int(latest[4:6]), 1)
        expected_date = date(int(expected[:4]), int(expected[4:6]), 1)
    else:
        latest_date = date.fromisoformat(latest)
        expected_date = date.fromisoformat(expected)
    return max(0, (expected_date - latest_date).days)


def _trading_dates_from_prices(config: dict[str, Any], start: str, end: str) -> list[str]:
    rows = read_processed_rows(config, "prices_daily")
    values = {
        _date_or_month(row.get("trade_date"), "trade_date")
        for row in rows
        if start[:10] <= _date_or_month(row.get("trade_date"), "trade_date") <= end[:10]
    }
    return sorted(value for value in values if value)


def _has_enabled_download_source(config: dict[str, Any], dataset: str, market: str) -> bool:
    try:
        plans = build_collect_plan(config, dataset, market)
    except KeyError:
        return False
    return any(plan.enabled and bool(plan.download_url or plan.url) for plan in plans)


if __name__ == "__main__":
    raise SystemExit(main())
