from __future__ import annotations

import argparse
import csv
import json
import re
import time
from datetime import timedelta
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

from z3b_prime.backtest.engine import backtest_signals
from z3b_prime.config import load_config
from z3b_prime.models import Bar
from z3b_prime.output import (
    TRADE_LOG_FIELDS,
    calculate_performance_metrics,
    trade_to_row,
    write_performance_report,
)
from z3b_prime.strategy.z3b_prime import run_strategy


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Z3B-Prime over intraday parquet universe.")
    parser.add_argument("--data-root", default=r"D:\market-data\tw-intraday")
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--cash", type=float, default=1_000_000)
    parser.add_argument(
        "--symbol-pattern",
        default=r"^[1-9][0-9]{3}$",
        help="Default keeps 4-digit non-ETF-like Taiwan equity symbols.",
    )
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--progress-every", type=int, default=50)
    args = parser.parse_args()

    data_root = Path(args.data_root)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    symbol_re = re.compile(args.symbol_pattern)
    config = load_config(args.config)

    pairs = discover_pairs(data_root, symbol_re)
    if args.limit > 0:
        pairs = pairs[: args.limit]

    start = time.perf_counter()
    trades = []
    trade_rows: list[dict[str, Any]] = []
    symbol_rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for index, (market, symbol, bars_15m_path, bars_1h_path) in enumerate(pairs, start=1):
        symbol_start = time.perf_counter()
        try:
            bars_15m = load_bars(bars_15m_path, "15m")
            bars_1h = load_bars(bars_1h_path, "1h")
            result = run_strategy(symbol, bars_1h, bars_15m, config)
            symbol_trades = backtest_signals(
                result.signals,
                bars_15m,
                config,
                account_cash=args.cash,
            )
            trades.extend(symbol_trades)
            for trade in symbol_trades:
                row = trade_to_row(trade)
                row["trade_id"] = f"{symbol}-{row['trade_id']}"
                trade_rows.append(row)
            symbol_rows.append(
                {
                    "market": market,
                    "symbol": symbol,
                    "status": "ok",
                    "bars_15m": len(bars_15m),
                    "bars_1h": len(bars_1h),
                    "start": bars_15m[0].time if bars_15m else "",
                    "end": bars_15m[-1].time if bars_15m else "",
                    "signals": len(result.signals),
                    "signal_events": len(result.signal_log),
                    "trades": len(symbol_trades),
                    "wins": sum(1 for trade in symbol_trades if trade.pnl > 0),
                    "losses": sum(1 for trade in symbol_trades if trade.pnl <= 0),
                    "pnl": sum(trade.pnl for trade in symbol_trades),
                    "seconds": round(time.perf_counter() - symbol_start, 3),
                }
            )
        except Exception as exc:  # Keep the universe run moving and report failures.
            errors.append({"market": market, "symbol": symbol, "error": repr(exc)})
            symbol_rows.append(
                {
                    "market": market,
                    "symbol": symbol,
                    "status": "error",
                    "signals": 0,
                    "signal_events": 0,
                    "trades": 0,
                    "wins": 0,
                    "losses": 0,
                    "pnl": 0.0,
                    "seconds": round(time.perf_counter() - symbol_start, 3),
                    "error": repr(exc),
                }
            )
        if index % args.progress_every == 0 or index == len(pairs):
            signals_total = sum(int(row.get("signals") or 0) for row in symbol_rows)
            print(
                f"processed {index}/{len(pairs)} symbols, "
                f"signals={signals_total}, trades={len(trades)}, errors={len(errors)}",
                flush=True,
            )

    write_csv(output_dir / "trade_log_all.csv", TRADE_LOG_FIELDS, trade_rows)
    write_csv(
        output_dir / "symbol_summary.csv",
        [
            "market",
            "symbol",
            "status",
            "bars_15m",
            "bars_1h",
            "start",
            "end",
            "signals",
            "signal_events",
            "trades",
            "wins",
            "losses",
            "pnl",
            "seconds",
            "error",
        ],
        symbol_rows,
    )
    write_performance_report(output_dir / "performance_report.md", trades, args.cash)
    metrics = calculate_performance_metrics(trades, args.cash)
    (output_dir / "five_core_metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )

    wins = sum(1 for trade in trades if trade.pnl > 0)
    summary = {
        "run_id": output_dir.name,
        "scope": "all paired intraday parquet files matching symbol pattern",
        "symbol_pattern": args.symbol_pattern,
        "config": str(Path(args.config).resolve()),
        "data_root": str(data_root.resolve()),
        "symbols_total": len(pairs),
        "symbols_ok": sum(1 for row in symbol_rows if row.get("status") == "ok"),
        "symbols_error": len(errors),
        "signals_total": sum(int(row.get("signals") or 0) for row in symbol_rows),
        "signal_events_total": sum(int(row.get("signal_events") or 0) for row in symbol_rows),
        "trades_total": len(trades),
        "wins": wins,
        "losses": len(trades) - wins,
        "win_rate": wins / len(trades) if trades else 0,
        "total_pnl": sum(trade.pnl for trade in trades),
        "five_core_metrics": metrics,
        "elapsed_seconds": round(time.perf_counter() - start, 3),
        "output_dir": str(output_dir.resolve()),
    }
    (output_dir / "run_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    if errors:
        (output_dir / "errors.json").write_text(
            json.dumps(errors, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    return 0


def discover_pairs(data_root: Path, symbol_re: re.Pattern[str]) -> list[tuple[str, str, Path, Path]]:
    pairs: list[tuple[str, str, Path, Path]] = []
    for market in ("TWSE", "TPEX"):
        dir_15m = data_root / "15m" / market
        dir_1h = data_root / "1h" / market
        if not dir_15m.exists() or not dir_1h.exists():
            continue
        for path_15m in sorted(dir_15m.glob("*.parquet")):
            symbol = path_15m.stem
            if not symbol_re.match(symbol):
                continue
            path_1h = dir_1h / path_15m.name
            if path_1h.exists():
                pairs.append((market, symbol, path_15m, path_1h))
    return pairs


def load_bars(path: Path, timeframe: str) -> list[Bar]:
    table = pq.read_table(
        path,
        columns=["timestamp", "symbol", "open", "high", "low", "close", "volume"],
    )
    data = table.to_pydict()
    delta = timedelta(minutes=15) if timeframe == "15m" else timedelta(hours=1)
    bars: list[Bar] = []
    for timestamp, symbol, open_, high, low, close, volume in zip(
        data["timestamp"],
        data["symbol"],
        data["open"],
        data["high"],
        data["low"],
        data["close"],
        data["volume"],
    ):
        bar_time = to_datetime(timestamp)
        bars.append(
            Bar(
                symbol=str(symbol),
                timeframe=timeframe,
                time=bar_time,
                close_time=bar_time + delta,
                open=float(open_),
                high=float(high),
                low=float(low),
                close=float(close),
                volume=float(volume or 0),
            )
        )
    return bars


def to_datetime(value):
    return value.to_pydatetime() if hasattr(value, "to_pydatetime") else value


def write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(main())
