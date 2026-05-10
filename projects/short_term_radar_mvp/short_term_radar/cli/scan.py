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
    parser.add_argument("--universe-mode", choices=["elastic", "all_market", "large_trend"])
    parser.add_argument("--min-coverage", type=float, default=0.0)
    parser.add_argument("--stage", default="")
    parser.add_argument("--include-degraded", default="true", choices=["true", "false"])
    args = parser.parse_args(argv)

    config = load_config(args.config)
    if args.universe_mode:
        config.setdefault("universe", {})["mode"] = args.universe_mode
    stage_filter = {item.strip() for item in args.stage.split(",") if item.strip()} or None
    rows = scan_candidates(
        config,
        args.date,
        args.top,
        min_coverage=args.min_coverage,
        stage_filter=stage_filter,
        include_degraded=args.include_degraded == "true",
    )
    write_csv(args.output, rows, SCAN_FIELDS)
    print(f"Wrote {len(rows)} candidates to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
