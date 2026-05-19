from __future__ import annotations

from z3b_prime import reason_codes
from z3b_prime.backtest.broker import stop_take_exit_reason
from z3b_prime.config import StrategyConfig
from z3b_prime.execution.tw_equity import (
    calculate_raw_quantity,
    commission,
    decide_quantity,
    sell_tax,
    try_enter_marketable_limit,
)
from z3b_prime.models import Bar, TradeResult, TradeSignal


def backtest_signals(
    signals: list[TradeSignal],
    bars_15m: list[Bar],
    config: StrategyConfig,
    account_cash: float = 1_000_000,
) -> list[TradeResult]:
    trades: list[TradeResult] = []
    for idx, signal in enumerate(signals, start=1):
        trade = simulate_trade(f"T{idx:04d}", signal, bars_15m, config, account_cash)
        if trade is not None:
            trades.append(trade)
    return trades


def simulate_trade(
    trade_id: str,
    signal: TradeSignal,
    bars_15m: list[Bar],
    config: StrategyConfig,
    account_cash: float = 1_000_000,
) -> TradeResult | None:
    entry_index = next(
        (idx for idx, bar in enumerate(bars_15m) if bar.time == signal.entry_time),
        None,
    )
    if entry_index is None:
        return None

    entry_bar = bars_15m[entry_index]
    entry_fill = try_enter_marketable_limit(entry_bar, config)
    if not entry_fill.filled:
        return None

    raw_qty = calculate_raw_quantity(
        account_cash=account_cash,
        entry_price=entry_fill.fill_price,
        stop_loss=signal.stop_loss,
        config=config,
    )
    quantity = decide_quantity(
        raw_quantity_shares=raw_qty,
        config=config,
        entry_bar=entry_bar,
    )
    if quantity.rejected:
        return None

    exit_bar = bars_15m[-1]
    exit_price = exit_bar.close
    exit_reason = reason_codes.END_OF_DATA
    holding_bars = 0

    for holding_bars, bar in enumerate(bars_15m[entry_index:], start=1):
        reason = stop_take_exit_reason(bar, signal.stop_loss, signal.take_profit)
        if reason is None:
            continue
        exit_bar = bar
        exit_reason = reason
        if "STOP" in reason:
            exit_price = signal.stop_loss * (1 - config.execution.stop_slippage_bps / 10000)
        else:
            exit_price = signal.take_profit
        break

    entry_value = entry_fill.fill_price * quantity.quantity_shares
    exit_value = exit_price * quantity.quantity_shares
    commission_buy = commission(entry_value, config)
    commission_sell = commission(exit_value, config)
    tax = sell_tax(
        exit_value,
        config,
        same_day_exit=entry_bar.time.date() == exit_bar.time.date(),
    )
    total_costs = commission_buy + commission_sell + tax
    pnl = exit_value - entry_value - total_costs
    pnl_pct = pnl / entry_value if entry_value else 0

    return TradeResult(
        trade_id=trade_id,
        strategy_id=signal.strategy_id,
        symbol=signal.symbol,
        entry_time=signal.entry_time,
        entry_price=entry_fill.fill_price,
        stop_loss=signal.stop_loss,
        take_profit=signal.take_profit,
        exit_time=exit_bar.close_time,
        exit_price=exit_price,
        exit_reason=exit_reason,
        pnl=pnl,
        pnl_pct=pnl_pct,
        rr_planned=signal.rr,
        holding_bars=holding_bars,
        metadata={
            **signal.metadata,
            "quantity_shares": quantity.quantity_shares,
            "raw_quantity_shares": raw_qty,
            "quantity_reason_codes": "|".join(quantity.reason_codes),
            "execution_profile": config.execution_profile,
            "entry_order_type": config.execution.entry_order_type,
            "entry_limit_price": entry_fill.limit_price,
            "entry_slippage_bps": config.execution.entry_slippage_bps,
            "max_entry_slippage_bps": config.execution.max_entry_slippage_bps,
            "stop_slippage_bps": config.execution.stop_slippage_bps,
            "gross_entry_value": entry_value,
            "gross_exit_value": exit_value,
            "commission_buy": commission_buy,
            "commission_sell": commission_sell,
            "sell_tax": tax,
            "total_costs": total_costs,
        },
    )
