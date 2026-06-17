from __future__ import annotations

import argparse
from datetime import date

from short_term_radar.data_sources.config import load_data_source_config
from short_term_radar.data_sources.quality import validate_rows
from short_term_radar.data_sources.registry import DATASET_REGISTRY, resolve_dataset_names
from short_term_radar.data_sources.storage import read_processed_rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate processed radar data tables.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--as-of")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    config = load_data_source_config(args.config)
    today = date.fromisoformat(args.as_of) if args.as_of else date.today()

    for name in resolve_dataset_names(args.dataset):
        spec = DATASET_REGISTRY[name]
        if args.dry_run:
            print(f"[dry-run] {spec.processed_table}: columns={len(spec.schema)} primary_key={spec.primary_key}")
            continue
        rows = read_processed_rows(config, name)
        report = validate_rows(spec.processed_table, rows, today=today)
        print(f"{spec.processed_table}: rows={report.row_count} ok={report.ok} issues={len(report.issues)}")
        for issue in report.issues:
            print(f"  {issue.severity}: {issue.check}: {issue.message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
