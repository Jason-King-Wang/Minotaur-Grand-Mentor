from __future__ import annotations

from dataclasses import dataclass, field
from math import floor

from z3b_prime import reason_codes
from z3b_prime.config import StrategyConfig
from z3b_prime.models import Bar


@dataclass(frozen=True)
class QuantityDecision:
    quantity_shares: int
    raw_quantity_shares: float
    reason_codes: list[str] = field(default_factory=list)
    rejected: bool = False


@dataclass(frozen=True)
class EntryFill:
    filled: bool
    fill_price: float = 0.0
    limit_price: float = 0.0
    reason_code: str = ""


def decide_quantity(
    *,
    raw_quantity_shares: float,
    config: StrategyConfig,
    entry_bar: Bar | None = None,
) -> QuantityDecision:
    quantity_config = config.quantity
    reasons: list[str] = []

    if config.execution_profile == "tw_odd_lot" and raw_quantity_shares < 1:
        return QuantityDecision(
            0,
            raw_quantity_shares,
            [reason_codes.ODD_LOT_QTY_BELOW_ONE_SHARE],
            True,
        )

    lot_size = max(1, quantity_config.lot_size_shares)
    quantity = floor(raw_quantity_shares)
    if quantity_config.round_to_lot_size:
        rounded = floor(quantity / lot_size) * lot_size
        if rounded < quantity:
            if config.execution_profile == "tw_round_lot":
                reasons.append(reason_codes.ROUND_LOT_REMAINDER_DROPPED)
            quantity = rounded

    if (
        quantity_config.max_order_quantity_shares is not None
        and quantity > quantity_config.max_order_quantity_shares
    ):
        quantity = quantity_config.max_order_quantity_shares
        if config.execution_profile == "tw_odd_lot":
            reasons.append(reason_codes.ODD_LOT_QTY_CAPPED_AT_999)

    if config.liquidity_filter.enabled and entry_bar is not None:
        if config.liquidity_filter.require_nonzero_volume_on_entry_bar and entry_bar.volume <= 0:
            code = (
                reason_codes.ODD_LOT_ENTRY_BAR_ZERO_VOLUME
                if config.execution_profile == "tw_odd_lot"
                else reason_codes.ENTRY_BAR_ZERO_VOLUME
            )
            return QuantityDecision(0, raw_quantity_shares, reasons + [code], True)
        volume_cap = floor(entry_bar.volume * config.liquidity_filter.max_order_participation_pct)
        if volume_cap > 0 and quantity > volume_cap:
            if config.liquidity_filter.reduce_qty_if_exceeds_volume_cap:
                quantity = volume_cap
                reasons.append(reason_codes.ORDER_QTY_REDUCED_BY_VOLUME_CAP)

    minimum = quantity_config.min_order_quantity_shares
    if quantity < minimum:
        code = (
            reason_codes.ROUND_LOT_QTY_BELOW_ONE_LOT
            if config.execution_profile == "tw_round_lot"
            else reason_codes.ORDER_QTY_BELOW_MINIMUM
        )
        if config.execution_profile == "tw_odd_lot":
            code = reason_codes.ODD_LOT_QTY_BELOW_ONE_SHARE
        return QuantityDecision(0, raw_quantity_shares, reasons + [code], True)

    return QuantityDecision(quantity, raw_quantity_shares, reasons, False)


def calculate_raw_quantity(
    *,
    account_cash: float,
    entry_price: float,
    stop_loss: float,
    config: StrategyConfig,
) -> float:
    risk_per_share = max(entry_price - stop_loss, 0)
    if risk_per_share <= 0:
        return 0
    risk_budget = account_cash * config.position_sizing.risk_per_trade_pct
    cash_cap = account_cash * config.position_sizing.max_cash_per_trade_pct
    return min(risk_budget / risk_per_share, cash_cap / entry_price)


def try_enter_marketable_limit(entry_bar: Bar, config: StrategyConfig) -> EntryFill:
    if config.execution_profile == "tw_odd_lot" and config.execution.entry_order_type != "odd_lot_limit":
        return EntryFill(False, reason_code=reason_codes.ODD_LOT_LIMIT_ONLY)
    limit_price = entry_bar.open * (1 + config.execution.max_entry_slippage_bps / 10000)
    fill_price = entry_bar.open * (1 + config.execution.entry_slippage_bps / 10000)
    if fill_price > limit_price:
        return EntryFill(False, limit_price=limit_price, reason_code=reason_codes.MARKETABLE_LIMIT_NOT_FILLED)
    return EntryFill(True, fill_price=fill_price, limit_price=limit_price)


def commission(value: float, config: StrategyConfig) -> float:
    fees = config.fees_and_taxes
    bps = fees.commission_bps_before_discount * fees.commission_discount
    fee = value * bps / 10000
    return max(fee, fees.min_commission_twd)


def sell_tax(value: float, config: StrategyConfig, *, same_day_exit: bool = False) -> float:
    fees = config.fees_and_taxes
    sell_tax_bps = fees.sell_tax_bps
    if (
        same_day_exit
        and config.execution_profile == "tw_round_lot"
        and fees.apply_day_trade_tax_reduction_if_qualified
        and fees.sell_tax_bps_day_trade_round_lot is not None
    ):
        sell_tax_bps = fees.sell_tax_bps_day_trade_round_lot
    return value * sell_tax_bps / 10000
