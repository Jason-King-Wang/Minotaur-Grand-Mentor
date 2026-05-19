from __future__ import annotations

import argparse
import csv
import json
import math
import re
import time
from collections import defaultdict
from dataclasses import asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

from z3b_prime.backtest.engine import simulate_trade
from z3b_prime.config import load_config
from z3b_prime.models import Bar, TradeResult, TradeSignal
from z3b_prime.output import (
    TRADE_LOG_FIELDS,
    calculate_performance_metrics,
    trade_to_row,
    write_performance_report,
)
from z3b_prime.strategy.z3b_prime import run_strategy


DATE_FILE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\.json$")
SYMBOL_RE = re.compile(r"^[1-9]\d{3}$")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Collect historical daily AB preselect symbols and run full repeated-trigger backtests for top symbols."
    )
    parser.add_argument("--ab-workspace", required=True)
    parser.add_argument("--data-root", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--cash", type=float, default=1_000_000)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--progress-every", type=int, default=5)
    parser.add_argument("--reuse-cache", action="store_true")
    args = parser.parse_args()

    start = time.perf_counter()
    ab_workspace = Path(args.ab_workspace)
    data_root = Path(args.data_root)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    config = load_config(args.config)

    all_symbols = collect_ab_preselect_symbols(ab_workspace)
    available = discover_available_symbols(data_root)
    selected = select_symbols(all_symbols, available, args.limit)

    write_csv(output_dir / "all_ab_preselect_symbols.csv", ALL_SYMBOL_FIELDS, all_symbols)
    write_csv(output_dir / "selected_50_symbols.csv", SELECTED_SYMBOL_FIELDS, selected)
    (output_dir / "selected_symbols.txt").write_text(
        "\n".join(row["symbol"] for row in selected) + "\n",
        encoding="utf-8",
    )

    cache_path = output_dir / "symbol_backtest_cache.json"
    cache = read_cache(cache_path) if args.reuse_cache else {}
    trade_cache_path = output_dir / "symbol_trade_cache.json"
    trade_cache = read_cache(trade_cache_path) if args.reuse_cache else {}
    result_rows: list[dict[str, Any]] = []
    trade_rows: list[dict[str, Any]] = []

    for index, symbol_row in enumerate(selected, start=1):
        symbol = symbol_row["symbol"]
        if args.reuse_cache and symbol in cache and cache[symbol].get("status") == "completed":
            cached_trade_rows = trade_cache.get(symbol)
            if cached_trade_rows is not None:
                result_rows.append(cache[symbol])
                trade_rows.extend(cached_trade_rows)
                continue
            if int(cache[symbol].get("trades") or 0) == 0:
                result_rows.append(cache[symbol])
                trade_cache[symbol] = []
                continue

        market = symbol_row["market"]
        symbol_start = time.perf_counter()
        row = {
            **symbol_row,
            "status": "started",
            "signals_total": 0,
            "signals_unique": 0,
            "signals_skipped_overlap": 0,
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0.0,
            "total_pnl": 0.0,
            "profit_factor": 0.0,
            "expectancy": 0.0,
            "cagr": 0.0,
            "mdd": 0.0,
            "sharpe": 0.0,
            "first_entry_time": "",
            "last_exit_time": "",
            "bars_15m": 0,
            "bars_1h": 0,
            "data_start": "",
            "data_end": "",
            "seconds": 0.0,
            "completed_at": "",
            "error": "",
        }
        try:
            bars_15m = load_bars(data_root / "15m" / market / f"{symbol}.parquet", "15m")
            bars_1h = load_bars(data_root / "1h" / market / f"{symbol}.parquet", "1h")
            strategy_result = run_strategy(
                symbol,
                bars_1h,
                bars_15m,
                config,
                stop_after_first_signal=False,
            )
            unique_signals = dedupe_signals(strategy_result.signals)
            trades, skipped_overlap = backtest_sequential_symbol_signals(
                symbol,
                unique_signals,
                bars_15m,
                config,
                args.cash,
            )
            symbol_trade_rows = []
            metrics = calculate_performance_metrics(trades, args.cash)
            wins = sum(1 for trade in trades if trade.pnl > 0)
            losses = len(trades) - wins
            row.update(
                {
                    "status": "completed",
                    "signals_total": len(strategy_result.signals),
                    "signals_unique": len(unique_signals),
                    "signals_skipped_overlap": skipped_overlap,
                    "trades": len(trades),
                    "wins": wins,
                    "losses": losses,
                    "win_rate": wins / len(trades) if trades else 0.0,
                    "total_pnl": sum(trade.pnl for trade in trades),
                    "profit_factor": metrics["profit_factor"],
                    "expectancy": metrics["expectancy"],
                    "cagr": metrics["cagr"],
                    "mdd": metrics["mdd"],
                    "sharpe": metrics["sharpe"],
                    "first_entry_time": min((trade.entry_time for trade in trades), default=""),
                    "last_exit_time": max((trade.exit_time for trade in trades), default=""),
                    "bars_15m": len(bars_15m),
                    "bars_1h": len(bars_1h),
                    "data_start": bars_15m[0].time if bars_15m else "",
                    "data_end": bars_15m[-1].close_time if bars_15m else "",
                    "seconds": round(time.perf_counter() - symbol_start, 3),
                    "completed_at": datetime.now().isoformat(timespec="seconds"),
                }
            )
            for trade in trades:
                trade_row = trade_to_row(trade)
                trade_row["trade_id"] = f"{symbol}-{trade_row['trade_id']}"
                trade_rows.append(trade_row)
                symbol_trade_rows.append(trade_row)
            trade_cache[symbol] = symbol_trade_rows
        except Exception as exc:
            row.update(
                {
                    "status": "error",
                    "error": repr(exc),
                    "seconds": round(time.perf_counter() - symbol_start, 3),
                    "completed_at": datetime.now().isoformat(timespec="seconds"),
                }
            )
        result_rows.append(row)
        cache[symbol] = row
        write_json(cache_path, cache)
        write_json(trade_cache_path, trade_cache)
        if index % args.progress_every == 0 or index == len(selected):
            completed = sum(1 for row in result_rows if row.get("status") == "completed")
            trades_done = sum(int(row.get("trades") or 0) for row in result_rows)
            print(
                f"processed {index}/{len(selected)} selected symbols, completed={completed}, trades={trades_done}",
                flush=True,
            )

    write_json(trade_cache_path, trade_cache)
    write_csv(output_dir / "selected_50_backtest_results.csv", RESULT_FIELDS, result_rows)
    write_csv(output_dir / "selected_50_trade_log.csv", TRADE_LOG_FIELDS, trade_rows)
    trades_for_report = rows_to_trade_results(trade_rows)
    write_performance_report(output_dir / "selected_50_performance_report.md", trades_for_report, args.cash)
    overall_metrics = calculate_performance_metrics(trades_for_report, args.cash)
    run_summary = {
        "run_id": output_dir.name,
        "ab_workspace": str(ab_workspace.resolve()),
        "data_root": str(data_root.resolve()),
        "config": str(Path(args.config).resolve()),
        "selection_policy": "top historical daily AB preselect appearance count, limited to symbols with copied 15m and 1h data",
        "symbols_all_ab": len(all_symbols),
        "symbols_available": sum(1 for row in all_symbols if row["symbol"] in available),
        "symbols_selected": len(selected),
        "symbols_completed": sum(1 for row in result_rows if row.get("status") == "completed"),
        "symbols_error": sum(1 for row in result_rows if row.get("status") == "error"),
        "trades_total": sum(int(row.get("trades") or 0) for row in result_rows),
        "total_pnl": sum(float(row.get("total_pnl") or 0.0) for row in result_rows),
        "overall_metrics": overall_metrics,
        "elapsed_seconds": round(time.perf_counter() - start, 3),
        "output_dir": str(output_dir.resolve()),
    }
    write_json(output_dir / "run_summary.json", run_summary)
    print(json.dumps(run_summary, ensure_ascii=False, indent=2, default=str), flush=True)
    return 0


ALL_SYMBOL_FIELDS = [
    "symbol",
    "stock_name",
    "appearance_count",
    "a_count",
    "b_count",
    "ab_count",
    "first_seen",
    "last_seen",
    "source_dates",
    "source_files",
]
SELECTED_SYMBOL_FIELDS = ["rank", "symbol", "stock_name", "market", *ALL_SYMBOL_FIELDS[2:]]
RESULT_FIELDS = [
    *SELECTED_SYMBOL_FIELDS,
    "status",
    "signals_total",
    "signals_unique",
    "signals_skipped_overlap",
    "trades",
    "wins",
    "losses",
    "win_rate",
    "total_pnl",
    "profit_factor",
    "expectancy",
    "cagr",
    "mdd",
    "sharpe",
    "first_entry_time",
    "last_exit_time",
    "bars_15m",
    "bars_1h",
    "data_start",
    "data_end",
    "seconds",
    "completed_at",
    "error",
]


def collect_ab_preselect_symbols(ab_workspace: Path) -> list[dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}

    preselect_dir = ab_workspace / "data" / "ab_llm_preselect"
    for path in sorted(preselect_dir.glob("*.json")):
        if not DATE_FILE_RE.match(path.name):
            continue
        data = read_json(path)
        trade_date = str(data.get("trade_date") or path.stem)
        add_preselect_list(records, data.get("a_preselect") or [], "A", trade_date, path)
        add_preselect_list(records, data.get("b_preselect") or [], "B", trade_date, path)

    daily_dir = ab_workspace / "data" / "ab_daily_output"
    for path in sorted(daily_dir.glob("*.json")):
        if not DATE_FILE_RE.match(path.name):
            continue
        data = read_json(path)
        trade_date = str(data.get("trade_date") or path.stem)
        for item in data.get("rows") or []:
            tags: list[str] = []
            if item.get("a_flag"):
                tags.append("A")
            if item.get("b_flag"):
                tags.append("B")
            if not tags:
                selection_tag = str(item.get("selection_tag") or "").upper()
                if "A" in selection_tag:
                    tags.append("A")
                if "B" in selection_tag:
                    tags.append("B")
            if not tags:
                tags.append("AB_ROW")
            for tag in tags:
                add_symbol_record(records, item, tag, trade_date, path)

    rows = []
    for symbol, record in records.items():
        source_dates = sorted(record.pop("_source_dates"))
        source_files = sorted(record.pop("_source_files"))
        record["appearance_count"] = len(source_dates)
        record["first_seen"] = source_dates[0] if source_dates else ""
        record["last_seen"] = source_dates[-1] if source_dates else ""
        record["source_dates"] = "|".join(source_dates)
        record["source_files"] = "|".join(source_files)
        rows.append(record)
    rows.sort(key=lambda row: (-int(row["appearance_count"]), row["symbol"]))
    return rows


def add_preselect_list(
    records: dict[str, dict[str, Any]],
    items: list[Any],
    tag: str,
    trade_date: str,
    path: Path,
) -> None:
    for item in items:
        add_symbol_record(records, item, tag, trade_date, path)


def add_symbol_record(
    records: dict[str, dict[str, Any]],
    item: Any,
    tag: str,
    trade_date: str,
    path: Path,
) -> None:
    if not isinstance(item, dict):
        return
    symbol = normalize_symbol(item.get("stock_id") or item.get("symbol") or item.get("code"))
    if symbol is None:
        return
    record = records.setdefault(
        symbol,
        {
            "symbol": symbol,
            "stock_name": "",
            "a_count": 0,
            "b_count": 0,
            "ab_count": 0,
            "_source_dates": set(),
            "_source_files": set(),
        },
    )
    name = str(item.get("stock_name") or item.get("name") or "").strip()
    if name and not record["stock_name"]:
        record["stock_name"] = name
    record["_source_dates"].add(trade_date)
    record["_source_files"].add(str(path.resolve()))
    if tag == "A":
        record["a_count"] += 1
    elif tag == "B":
        record["b_count"] += 1
    if tag == "A" and item.get("b_flag"):
        record["ab_count"] += 1
    elif tag == "B" and item.get("a_flag"):
        record["ab_count"] += 1
    elif str(item.get("selection_tag") or "").upper() == "AB":
        record["ab_count"] += 1


def normalize_symbol(value: Any) -> str | None:
    text = str(value or "").strip()
    match = re.search(r"([1-9]\d{3})", text)
    if not match:
        return None
    symbol = match.group(1)
    return symbol if SYMBOL_RE.match(symbol) else None


def discover_available_symbols(data_root: Path) -> dict[str, str]:
    available: dict[str, str] = {}
    for market in ("TWSE", "TPEX"):
        dir_15m = data_root / "15m" / market
        dir_1h = data_root / "1h" / market
        if not dir_15m.exists() or not dir_1h.exists():
            continue
        for path_15m in sorted(dir_15m.glob("*.parquet")):
            symbol = path_15m.stem
            if SYMBOL_RE.match(symbol) and (dir_1h / path_15m.name).exists():
                available[symbol] = market
    return available


def select_symbols(
    all_symbols: list[dict[str, Any]],
    available: dict[str, str],
    limit: int,
) -> list[dict[str, Any]]:
    rows = [row for row in all_symbols if row["symbol"] in available]
    rows.sort(key=lambda row: (-int(row["appearance_count"]), row["last_seen"], row["symbol"]))
    selected = []
    for rank, row in enumerate(rows[:limit], start=1):
        selected.append({"rank": rank, "market": available[row["symbol"]], **row})
    return selected


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
        bar_time = timestamp.to_pydatetime() if hasattr(timestamp, "to_pydatetime") else timestamp
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


def dedupe_signals(signals: list[TradeSignal]) -> list[TradeSignal]:
    seen = set()
    unique = []
    for signal in sorted(signals, key=lambda item: (item.entry_time, item.signal_time)):
        key = (
            signal.symbol,
            signal.signal_time,
            signal.entry_time,
            round(signal.entry_price, 4),
            round(signal.stop_loss, 4),
            round(signal.take_profit, 4),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(signal)
    return unique


def backtest_sequential_symbol_signals(
    symbol: str,
    signals: list[TradeSignal],
    bars_15m: list[Bar],
    config,
    account_cash: float,
) -> tuple[list[TradeResult], int]:
    trades: list[TradeResult] = []
    skipped_overlap = 0
    last_exit_time = None
    for signal in sorted(signals, key=lambda item: (item.entry_time, item.signal_time)):
        if last_exit_time is not None and signal.entry_time <= last_exit_time:
            skipped_overlap += 1
            continue
        trade = simulate_trade(
            f"T{len(trades) + 1:04d}",
            signal,
            bars_15m,
            config,
            account_cash,
        )
        if trade is None:
            continue
        trades.append(trade)
        last_exit_time = trade.exit_time
    return trades, skipped_overlap


def rows_to_trade_results(rows: list[dict[str, Any]]) -> list[TradeResult]:
    trades = []
    for row in rows:
        metadata = {key: row.get(key, "") for key in TRADE_LOG_FIELDS if key not in TRADE_RESULT_FIELDS}
        trades.append(
            TradeResult(
                trade_id=str(row.get("trade_id", "")),
                strategy_id=str(row.get("strategy_id", "")),
                symbol=str(row.get("symbol", "")),
                entry_time=parse_datetime(row.get("entry_time")),
                entry_price=float_or_zero(row.get("entry_price")),
                stop_loss=float_or_zero(row.get("stop_loss")),
                take_profit=float_or_zero(row.get("take_profit")),
                exit_time=parse_datetime(row.get("exit_time")),
                exit_price=float_or_zero(row.get("exit_price")),
                exit_reason=str(row.get("exit_reason", "")),
                pnl=float_or_zero(row.get("pnl")),
                pnl_pct=float_or_zero(row.get("pnl_pct")),
                rr_planned=float_or_zero(row.get("rr_planned")),
                holding_bars=int(float_or_zero(row.get("holding_bars"))),
                metadata=metadata,
            )
        )
    return trades


TRADE_RESULT_FIELDS = {
    "trade_id",
    "strategy_id",
    "symbol",
    "entry_time",
    "entry_price",
    "stop_loss",
    "take_profit",
    "exit_time",
    "exit_price",
    "exit_reason",
    "pnl",
    "pnl_pct",
    "rr_planned",
    "holding_bars",
}


def parse_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value))


def float_or_zero(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_cache(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    data = read_json(path)
    return data if isinstance(data, dict) else {}


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(format_row(row, fields) for row in rows)


def format_row(row: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    return {field: format_value(row.get(field, "")) for field in fields}


def format_value(value: Any) -> Any:
    if isinstance(value, (datetime,)):
        return value.isoformat(sep=" ")
    if isinstance(value, float) and math.isinf(value):
        return "inf"
    return value


if __name__ == "__main__":
    raise SystemExit(main())
