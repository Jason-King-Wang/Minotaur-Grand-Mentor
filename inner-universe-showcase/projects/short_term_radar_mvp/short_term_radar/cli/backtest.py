from __future__ import annotations

import argparse

from short_term_radar.backtest.baselines import run_baseline_comparison
from short_term_radar.backtest.simulator import run_backtest, write_backtest_outputs
from short_term_radar.config import load_config


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run short-term radar backtest.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--rebalance", default="monthly", choices=["monthly"])
    parser.add_argument("--top-n", type=int, default=20)
    parser.add_argument("--horizon-days", type=int, default=126)
    parser.add_argument("--target-multiple", type=float, default=3.0)
    parser.add_argument("--include-baselines", action="store_true")
    parser.add_argument("--random-seed", type=int, default=42)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    config = load_config(args.config)
    config.setdefault("backtest", {})["target_multiples"] = [args.target_multiple]
    summary, details = run_backtest(config, args.start, args.end, args.top_n, args.horizon_days)
    if args.include_baselines:
        baseline_rows, baseline_details = run_baseline_comparison(
            config,
            args.start,
            args.end,
            args.top_n,
            args.horizon_days,
            args.random_seed,
        )
        paths = write_backtest_outputs(args.output, summary, details, baseline_rows, baseline_details)
        print(f"Wrote backtest summary to {paths['summary']}")
        print(f"Wrote candidate details to {paths['details']}")
        print(f"Wrote baseline comparison to {paths['baseline']}")
        print(f"Wrote baseline details to {paths['baseline_details']}")
        return 0

    detail_path = write_backtest_outputs(args.output, summary, details)
    print(f"Wrote backtest summary to {args.output}")
    print(f"Wrote candidate details to {detail_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
