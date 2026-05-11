from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from short_term_radar.data_sources.config import load_data_source_config
from short_term_radar.data_sources.local_backfill import (
    backfill_prices_daily_from_existing,
    backfill_symbol_master_from_existing,
)
from short_term_radar.data_sources.quality import validate_rows
from short_term_radar.data_sources.registry import build_collect_plan
from short_term_radar.data_sources.sources.monthly_revenue_official import MonthlyRevenueOfficialSource
from short_term_radar.data_sources.sources.surveillance_official import SurveillanceOfficialSource
from short_term_radar.data_sources.storage import data_root, merge_processed_rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect short-term radar source data.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--market", default="all")
    parser.add_argument("--date")
    parser.add_argument("--month")
    parser.add_argument("--start")
    parser.add_argument("--end")
    parser.add_argument("--start-month")
    parser.add_argument("--end-month")
    parser.add_argument("--source", default="registry")
    parser.add_argument("--write-raw", action="store_true")
    parser.add_argument("--normalize", action="store_true")
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--rate-limit-seconds", type=float)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    config = load_data_source_config(args.config)
    if args.dataset == "monthly_revenue" and args.source == "official":
        return _collect_monthly_revenue_official(config, args)
    if args.dataset == "surveillance" and args.source == "official":
        return _collect_surveillance_official(config, args)
    if args.write_raw:
        raise ValueError("--write-raw is only implemented for monthly_revenue --source official.")

    plans = build_collect_plan(config, args.dataset, args.market)

    if args.dry_run:
        for plan in plans:
            status = "enabled" if plan.enabled else "disabled"
            landing = f" landing={plan.landing_url}" if plan.landing_url else ""
            download = f" download={plan.download_url}" if plan.download_url else " download=<not configured>"
            api = f" api={plan.api_url}" if plan.api_url else " api=<not configured>"
            print(f"[dry-run] {plan.dataset} {plan.market} via {plan.source} ({status}){landing}{download}{api}")
        print(f"[dry-run] data_root={config.get('data_root')}")
        return 0

    if args.dataset == "symbol_master":
        output, count = backfill_symbol_master_from_existing(config)
        print(f"Wrote {count} symbol_master rows to {output}")
        return 0

    if args.dataset == "prices_daily":
        output, count = backfill_prices_daily_from_existing(config, args.start or args.date, args.end or args.date, args.market)
        print(f"Wrote {count} prices_daily rows to {output}")
        return 0

    for plan in plans:
        if not plan.enabled:
            print(f"Skipped {plan.dataset} {plan.market} via {plan.source}: {plan.note}")
            continue
        print(
            f"Collector interface ready for {plan.dataset} {plan.market} via {plan.source}; "
            "live fetch endpoint is intentionally not executed by default."
        )
    return 0


def _collect_monthly_revenue_official(config: dict, args: argparse.Namespace) -> int:
    start_month = args.start_month or args.month
    end_month = args.end_month or args.month or start_month
    if not start_month or not end_month:
        raise ValueError("monthly_revenue official collect requires --month or --start-month/--end-month")

    source = MonthlyRevenueOfficialSource(config)
    requests = source.build_requests(args.market, start_month, end_month)
    if args.dry_run:
        for request in requests:
            print(
                "[dry-run] monthly_revenue "
                f"{request.market} {request.company_type} {request.revenue_month} via official_mops {request.url}"
            )
        print(f"[dry-run] data_root={config.get('data_root')}")
        return 0

    result = source.collect(args.market, start_month, end_month)
    if result.degraded:
        for message in result.degraded:
            print(f"source unavailable: {message}")
    print(f"Fetched {len(result.rows)} monthly_revenue rows from {len(result.requests)} official MOPS requests.")

    if args.write_raw:
        written = _write_monthly_revenue_raw_documents(config, result.raw_documents)
        print(f"Wrote {len(written)} raw monthly_revenue documents.")

    if args.normalize:
        merge_result = merge_processed_rows(config, "monthly_revenue", result.rows, mode="upsert")
        print(
            f"Merged monthly_revenue rows to {merge_result['path']}; "
            f"inserted={merge_result['inserted_rows']} updated={merge_result['updated_rows']}"
        )

    if args.validate:
        report = validate_rows("monthly_revenue", result.rows, today=date.today(), allow_future_dates=True)
        print(f"monthly_revenue quality_ok={report.ok}; issues={len(report.issues)}")
        for issue in report.issues:
            print(f"  {issue.severity}: {issue.check}: {issue.message}")
    return 0


def _write_monthly_revenue_raw_documents(config: dict, raw_documents: list[dict[str, str]]) -> list[Path]:
    outputs: list[Path] = []
    for document in raw_documents:
        output = (
            data_root(config)
            / "raw"
            / "official_mops"
            / "monthly_revenue"
            / f"revenue_month={document['revenue_month']}"
            / f"market={document['market']}"
            / f"company_type={document['company_type']}"
            / "raw.html"
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(document["raw_text"], encoding="utf-8")
        outputs.append(output)
    return outputs


def _collect_surveillance_official(config: dict, args: argparse.Namespace) -> int:
    if args.write_raw:
        raise ValueError("--write-raw is not supported for surveillance until a direct download_url is configured.")

    source = SurveillanceOfficialSource(config)
    requests = source.build_requests(args.market)
    if args.dry_run:
        for request in requests:
            status = "enabled" if request.enabled else "disabled"
            landing = f" landing={request.landing_url}" if request.landing_url else ""
            download = f" download={request.download_url}" if request.download_url else " download=<not configured>"
            print(f"[dry-run] surveillance {request.market} {request.kind} via official ({status}){landing}{download}")
            if request.note:
                print(f"[dry-run] note: {request.note}")
        print(f"[dry-run] data_root={config.get('data_root')}")
        return 0

    rows, degraded = source.collect(args.market)
    for message in degraded:
        print(f"source unavailable: {message}")
    print(f"Fetched {len(rows)} surveillance rows from official sources.")
    if args.normalize:
        merge_result = merge_processed_rows(config, "surveillance", rows, mode="upsert")
        print(
            f"Merged surveillance rows to {merge_result['path']}; "
            f"inserted={merge_result['inserted_rows']} updated={merge_result['updated_rows']}"
        )
    if args.validate:
        report = validate_rows("surveillance_daily", rows, today=date.today(), allow_future_dates=True)
        print(f"surveillance quality_ok={report.ok}; issues={len(report.issues)}")
        for issue in report.issues:
            print(f"  {issue.severity}: {issue.check}: {issue.message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
