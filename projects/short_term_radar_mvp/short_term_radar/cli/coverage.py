from __future__ import annotations

import argparse

from short_term_radar.data_sources.config import load_data_source_config
from short_term_radar.data_sources.registry import DATASET_REGISTRY
from short_term_radar.data_sources.storage import processed_path, read_processed_rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Report processed data coverage.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    config = load_data_source_config(args.config)
    for name, spec in DATASET_REGISTRY.items():
        path = processed_path(config, name)
        if args.dry_run:
            print(f"[dry-run] {spec.processed_table}: expected range {args.start}..{args.end}, path={path}")
            continue
        rows = read_processed_rows(config, name)
        print(f"{spec.processed_table}: rows={len(rows)} path={path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
