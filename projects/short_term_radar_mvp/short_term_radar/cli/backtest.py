from __future__ import annotations

import argparse

from short_term_radar.backtest.simulator import run_baseline_backtests, run_backtest, write_backtest_outputs
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
    parser.add_argument("--include-baselines", default="true", choices=["true", "false"])
    parser.add_argument("--random-trials", type=int, default=30)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--universe-mode", choices=["elastic", "all_market", "large_trend"])
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    config = load_config(args.config)
    config.setdefault("backtest", {})["target_multiples"] = [args.target_multiple]
    if args.universe_mode:
        config.setdefault("universe", {})["mode"] = args.universe_mode
    summary, details = run_backtest(config, args.start, args.end, args.top_n, args.horizon_days)
    baseline_summaries = None
    baseline_details = None
    if args.include_baselines == "true":
        baseline_summaries, baseline_details = run_baseline_backtests(
            config,
            args.start,
            args.end,
            args.top_n,
            args.horizon_days,
            args.random_trials,
            args.seed,
        )
    paths = write_backtest_outputs(args.output, summary, details, baseline_summaries, baseline_details)
    print(f"Wrote backtest summary to {args.output}")
    print(f"Wrote candidate details to {paths['details']}")
    if "baseline" in paths:
        print(f"Wrote baseline comparison to {paths['baseline']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
