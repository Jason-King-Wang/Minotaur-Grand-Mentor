from __future__ import annotations

import argparse

from short_term_radar.data_sources.config import load_data_source_config
from short_term_radar.data_sources.local_backfill import (
    backfill_prices_daily_from_existing,
    backfill_symbol_master_from_existing,
)
from short_term_radar.data_sources.registry import build_collect_plan


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
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    config = load_data_source_config(args.config)
    plans = build_collect_plan(config, args.dataset, args.market)

    if args.dry_run:
        for plan in plans:
            status = "enabled" if plan.enabled else "disabled"
            print(f"[dry-run] {plan.dataset} {plan.market} via {plan.source} ({status}) {plan.url or ''}".rstrip())
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


if __name__ == "__main__":
    raise SystemExit(main())
