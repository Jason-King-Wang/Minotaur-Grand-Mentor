from __future__ import annotations

import csv
import json
from dataclasses import asdict
from datetime import datetime
from math import sqrt
from pathlib import Path
from typing import Any

from z3b_prime.models import SignalEvent, TradeResult, TradeSignal


TRADE_LOG_FIELDS = [
    "trade_id",
    "strategy_id",
    "symbol",
    "entry_time",
    "entry_price",
    "entry_limit_price",
    "entry_order_type",
    "execution_profile",
    "quantity_shares",
    "raw_quantity_shares",
    "quantity_reason_codes",
    "stop_loss",
    "take_profit",
    "exit_time",
    "exit_price",
    "exit_reason",
    "pnl",
    "pnl_pct",
    "rr_planned",
    "holding_bars",
    "entry_path",
    "gross_entry_value",
    "gross_exit_value",
    "commission_buy",
    "commission_sell",
    "sell_tax",
    "total_costs",
    "entry_slippage_bps",
    "max_entry_slippage_bps",
    "stop_slippage_bps",
    "center_1h_start",
    "center_1h_end",
    "center_1h_upper",
    "center_1h_lower",
    "center_1h_box_high",
    "center_1h_box_low",
    "center_1h_score",
    "center_1h_macd_diag",
    "center_A_15m_start",
    "center_A_15m_end",
    "center_A_upper",
    "center_A_lower",
    "center_A_box_high",
    "center_A_box_low",
    "center_A_score",
    "center_A_macd_diag",
    "a_length",
    "b_length",
    "center_bA_15m_start",
    "center_bA_15m_end",
    "center_bA_upper",
    "center_bA_lower",
    "center_bA_score",
    "center_bA_macd_diag",
    "ba_length",
    "bb_length",
    "iso_low_1",
    "iso_low_2",
    "local_resistance",
    "golden_k_time",
    "golden_k_open",
    "golden_k_high",
    "golden_k_low",
    "golden_k_close",
    "bullish_k_time",
    "bullish_k_low",
]


SIGNAL_LOG_FIELDS = [
    "strategy_id",
    "symbol",
    "time",
    "state",
    "reason_code",
    "message",
    "metadata_json",
]


def write_trade_log(path: str | Path, trades: list[TradeResult]) -> None:
    rows = [trade_to_row(trade) for trade in trades]
    write_csv(path, TRADE_LOG_FIELDS, rows)


def write_signal_log(
    path: str | Path,
    events: list[SignalEvent],
    signals: list[TradeSignal],
) -> None:
    rows = [event_to_row(event) for event in events]
    for signal in signals:
        rows.append(
            {
                "strategy_id": signal.strategy_id,
                "symbol": signal.symbol,
                "time": signal.signal_time,
                "state": "SIGNAL",
                "reason_code": signal.reason_code,
                "message": "long signal emitted",
                "metadata_json": json.dumps(signal.metadata, ensure_ascii=False, default=str),
            }
        )
    write_csv(path, SIGNAL_LOG_FIELDS, rows)


def calculate_performance_metrics(
    trades: list[TradeResult],
    initial_cash: float = 1_000_000,
) -> dict[str, float]:
    ordered = sorted(trades, key=lambda trade: trade.exit_time)
    total_pnl = sum(trade.pnl for trade in ordered)
    gross_profit = sum(trade.pnl for trade in ordered if trade.pnl > 0)
    gross_loss = -sum(trade.pnl for trade in ordered if trade.pnl < 0)
    final_equity = initial_cash + total_pnl
    total_return = final_equity / initial_cash - 1 if initial_cash else 0.0

    if ordered:
        start = min(trade.entry_time for trade in ordered)
        end = max(trade.exit_time for trade in ordered)
        years = max((end - start).total_seconds() / (365.25 * 24 * 3600), 1 / 365.25)
    else:
        years = 0.0
    cagr = (final_equity / initial_cash) ** (1 / years) - 1 if years and final_equity > 0 else 0.0

    equity = initial_cash
    peak = initial_cash
    max_drawdown = 0.0
    for trade in ordered:
        equity += trade.pnl
        peak = max(peak, equity)
        drawdown = equity / peak - 1 if peak else 0.0
        max_drawdown = min(max_drawdown, drawdown)

    trade_returns = [trade.pnl / initial_cash for trade in ordered if initial_cash]
    if len(trade_returns) >= 2:
        mean_ret = sum(trade_returns) / len(trade_returns)
        variance = sum((ret - mean_ret) ** 2 for ret in trade_returns) / (len(trade_returns) - 1)
        trades_per_year = len(trade_returns) / years if years else 0.0
        sharpe = mean_ret / sqrt(variance) * sqrt(trades_per_year) if variance > 0 and trades_per_year > 0 else 0.0
    else:
        sharpe = 0.0

    profit_factor = gross_profit / gross_loss if gross_loss > 0 else (float("inf") if gross_profit > 0 else 0.0)
    expectancy = sum(trade.pnl_pct for trade in ordered) / len(ordered) if ordered else 0.0
    wins = sum(1 for trade in ordered if trade.pnl > 0)
    return {
        "initial_cash": initial_cash,
        "final_equity": final_equity,
        "total_pnl": total_pnl,
        "total_return": total_return,
        "cagr": cagr,
        "mdd": max_drawdown,
        "sharpe": sharpe,
        "profit_factor": profit_factor,
        "expectancy": expectancy,
        "trades": float(len(ordered)),
        "wins": float(wins),
        "win_rate": wins / len(ordered) if ordered else 0.0,
    }


def write_performance_report(
    path: str | Path,
    trades: list[TradeResult],
    initial_cash: float = 1_000_000,
) -> None:
    metrics = calculate_performance_metrics(trades, initial_cash)
    total_pnl = metrics["total_pnl"]
    wins = int(metrics["wins"])
    win_rate = metrics["win_rate"]
    lines = [
        "# Z3B-Prime Backtest Report",
        "",
        "## Five Core Metrics",
        "",
        "| 指標 | English | 數值 | 解讀 |",
        "|---|---|---:|---|",
        f"| 年化報酬率 | CAGR / Annualized Return | {metrics['cagr']:.2%} | 長期資金成長效率 |",
        f"| 最大回撤 | MDD / Maximum Drawdown | {metrics['mdd']:.2%} | 最慘下跌幅度 |",
        f"| 夏普率 | Sharpe Ratio | {metrics['sharpe']:.2f} | 報酬穩定度 |",
        f"| 獲利因子 | Profit Factor | {format_ratio(metrics['profit_factor'])} | 總獲利能否覆蓋總虧損 |",
        f"| 每筆交易期望值 | Expectancy | {metrics['expectancy']:.2%} | 平均每次交易期望 |",
        "",
        "## Detailed Stats",
        "",
        f"- Trades: {len(trades)}",
        f"- Wins: {wins}",
        f"- Win rate: {win_rate:.2%}",
        f"- Total PnL: {total_pnl:.6f}",
        f"- Initial Cash: {initial_cash:.2f}",
        f"- Final Equity: {metrics['final_equity']:.2f}",
        "",
        "This report is for rule quantification and historical backtest review only. It is not investment advice and does not guarantee returns.",
    ]
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def format_ratio(value: float) -> str:
    return "inf" if value == float("inf") else f"{value:.2f}"


def trade_to_row(trade: TradeResult) -> dict[str, Any]:
    base = asdict(trade)
    metadata = base.pop("metadata") or {}
    row = {**base, **metadata}
    return {field: format_value(row.get(field, "")) for field in TRADE_LOG_FIELDS}


def event_to_row(event: SignalEvent) -> dict[str, Any]:
    return {
        "strategy_id": event.strategy_id,
        "symbol": event.symbol,
        "time": event.time,
        "state": event.state,
        "reason_code": event.reason_code,
        "message": event.message,
        "metadata_json": json.dumps(event.metadata, ensure_ascii=False, default=str),
    }


def write_csv(path: str | Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def format_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat(sep=" ")
    return value
