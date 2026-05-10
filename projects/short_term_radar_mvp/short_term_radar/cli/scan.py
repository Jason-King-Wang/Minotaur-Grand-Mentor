from __future__ import annotations

import argparse

from short_term_radar.config import load_config
from short_term_radar.pipeline import SCAN_FIELDS, scan_candidates
from short_term_radar.utils.io import write_csv


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run daily short-term radar scan.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--top", type=int, default=50)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    config = load_config(args.config)
    rows = scan_candidates(config, args.date, args.top)
    write_csv(args.output, rows, SCAN_FIELDS)
    print(f"Wrote {len(rows)} candidates to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
