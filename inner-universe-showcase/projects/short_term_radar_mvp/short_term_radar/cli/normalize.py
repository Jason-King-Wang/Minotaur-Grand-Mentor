from __future__ import annotations

import argparse
from datetime import date

from short_term_radar.data_sources.config import load_data_source_config
from short_term_radar.data_sources.fetchers.local_file_fetcher import LocalFileFetcher
from short_term_radar.data_sources.normalizers.dispatcher import NORMALIZERS, normalize_rows
from short_term_radar.data_sources.quality import validate_rows
from short_term_radar.data_sources.registry import DATASET_REGISTRY, resolve_dataset_names
from short_term_radar.data_sources.storage import merge_processed_rows, processed_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Normalize raw source data into processed tables.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--input", help="Local raw CSV file to normalize.")
    parser.add_argument("--market", default="Unknown")
    parser.add_argument("--source", default="local_file")
    parser.add_argument("--source-url", default="")
    parser.add_argument("--fetched-at")
    parser.add_argument("--as-of")
    parser.add_argument("--mode", default="upsert", choices=["append", "upsert", "replace"])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    config = load_data_source_config(args.config)
    names = resolve_dataset_names(args.dataset)
    for name in names:
        spec = DATASET_REGISTRY[name]
        normalizer_state = "registered" if name in NORMALIZERS else "missing"
        print(f"{'[dry-run] ' if args.dry_run else ''}{name}: normalizer={normalizer_state} output={processed_path(config, name)}")
        if not args.dry_run:
            if not args.input:
                print(f"{name}: no --input path was provided; leaving processed table unchanged.")
                continue
            if len(names) > 1:
                raise ValueError("--input can only be used with one dataset at a time")
            raw_rows = LocalFileFetcher().fetch_csv(args.input, args.source, name).rows
            normalized = normalize_rows(
                name,
                raw_rows,
                args.market,
                args.source,
                args.source_url or args.input,
                args.fetched_at,
            )
            merge_result = merge_processed_rows(config, name, normalized, mode=args.mode)
            output = merge_result["path"]
            report = validate_rows(
                spec.processed_table,
                normalized,
                today=date.fromisoformat(args.as_of) if args.as_of else date.today(),
            )
            print(
                f"{name}: merged {len(normalized)} rows to {output}; "
                f"inserted={merge_result['inserted_rows']} updated={merge_result['updated_rows']} "
                f"quality_ok={report.ok}; issues={len(report.issues)}"
            )
            for issue in report.issues:
                print(f"  {issue.severity}: {issue.check}: {issue.message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
