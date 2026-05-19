from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from z3b_prime.backtest.engine import backtest_signals
from z3b_prime.config import load_config
from z3b_prime.data.loader import load_ohlcv_csv
from z3b_prime.data.resample import resample_to_1h
from z3b_prime.output import write_performance_report, write_signal_log, write_trade_log
from z3b_prime.strategy.z3b_prime import run_strategy
from z3b_prime.visualization.annotate import write_annotated_svg


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Z3B-Prime backtest.")
    parser.add_argument("--bars-15m", required=True, help="15m OHLCV CSV path")
    parser.add_argument("--bars-1h", help="1H OHLCV CSV path; resampled from 15m if omitted")
    parser.add_argument("--config", default="config/config.example.yaml")
    parser.add_argument("--symbol", help="Override symbol")
    parser.add_argument("--output", help="Output directory")
    parser.add_argument("--cash", type=float, default=1_000_000, help="Starting cash for position sizing")
    parser.add_argument("--no-annotate", action="store_true", help="Skip annotated SVG output")
    args = parser.parse_args(argv)

    config = load_config(args.config)
    bars_15m = load_ohlcv_csv(args.bars_15m, symbol=args.symbol, timeframe="15m")
    bars_1h = (
        load_ohlcv_csv(args.bars_1h, symbol=args.symbol, timeframe="1h")
        if args.bars_1h
        else resample_to_1h(bars_15m)
    )
    if not bars_15m:
        raise SystemExit("15m CSV has no rows")
    symbol = args.symbol or bars_15m[0].symbol

    result = run_strategy(symbol, bars_1h, bars_15m, config)
    trades = backtest_signals(result.signals, bars_15m, config, account_cash=args.cash)

    output_dir = Path(args.output or default_output_dir())
    output_dir.mkdir(parents=True, exist_ok=True)
    write_signal_log(output_dir / "signal_log.csv", result.signal_log, result.signals)
    write_trade_log(output_dir / "trade_log.csv", trades)
    write_performance_report(output_dir / "performance_report.md", trades)
    if not args.no_annotate:
        write_annotated_svg(
            output_dir / "annotated_chart.svg",
            bars_15m,
            trades[0] if trades else None,
        )

    print(f"signals={len(result.signals)} trades={len(trades)} output={output_dir}")
    return 0


def default_output_dir() -> str:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"reports/z3b_prime/{stamp}"


if __name__ == "__main__":
    raise SystemExit(main())
