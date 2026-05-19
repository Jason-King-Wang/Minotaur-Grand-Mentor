from z3b_prime.config import strategy_config_from_dict
from z3b_prime.execution.tw_equity import (
    commission,
    decide_quantity,
    sell_tax,
    try_enter_marketable_limit,
)
from z3b_prime.reason_codes import (
    ODD_LOT_QTY_BELOW_ONE_SHARE,
    ODD_LOT_QTY_CAPPED_AT_999,
    ROUND_LOT_QTY_BELOW_ONE_LOT,
    ROUND_LOT_REMAINDER_DROPPED,
)


def round_lot_config():
    return strategy_config_from_dict(
        {
            "execution_profile": "tw_round_lot",
            "quantity": {
                "lot_size_shares": 1000,
                "min_order_quantity_shares": 1000,
                "round_to_lot_size": True,
            },
            "execution": {
                "entry_order_type": "marketable_limit",
                "entry_slippage_bps": 5,
                "max_entry_slippage_bps": 20,
                "stop_slippage_bps": 10,
            },
            "fees_and_taxes": {
                "commission_bps_before_discount": 14.25,
                "commission_discount": 1.0,
                "min_commission_twd": 0,
                "sell_tax_bps": 30.0,
                "sell_tax_bps_day_trade_round_lot": 15.0,
                "apply_day_trade_tax_reduction_if_qualified": True,
            },
        }
    )


def odd_lot_config():
    return strategy_config_from_dict(
        {
            "execution_profile": "tw_odd_lot",
            "quantity": {
                "lot_size_shares": 1,
                "min_order_quantity_shares": 1,
                "max_order_quantity_shares": 999,
                "round_to_lot_size": True,
            },
            "execution": {
                "entry_order_type": "odd_lot_limit",
                "entry_slippage_bps": 10,
                "max_entry_slippage_bps": 30,
            },
            "fees_and_taxes": {
                "commission_bps_before_discount": 14.25,
                "commission_discount": 1.0,
                "min_commission_twd": 0,
                "sell_tax_bps": 30.0,
            },
        }
    )


def test_round_lot_quantity_drops_remainder():
    decision = decide_quantity(raw_quantity_shares=2350, config=round_lot_config())

    assert decision.quantity_shares == 2000
    assert ROUND_LOT_REMAINDER_DROPPED in decision.reason_codes


def test_round_lot_quantity_below_one_lot_rejected():
    decision = decide_quantity(raw_quantity_shares=999, config=round_lot_config())

    assert decision.rejected
    assert ROUND_LOT_QTY_BELOW_ONE_LOT in decision.reason_codes


def test_odd_lot_quantity_below_one_share_rejected():
    decision = decide_quantity(raw_quantity_shares=0.8, config=odd_lot_config())

    assert decision.rejected
    assert ODD_LOT_QTY_BELOW_ONE_SHARE in decision.reason_codes


def test_odd_lot_quantity_caps_at_999():
    decision = decide_quantity(raw_quantity_shares=1200, config=odd_lot_config())

    assert decision.quantity_shares == 999
    assert ODD_LOT_QTY_CAPPED_AT_999 in decision.reason_codes


def test_entry_uses_marketable_limit_with_slippage(make_bars):
    entry_bar = make_bars([(100, 105, 99, 103)], timeframe="15m")[0]
    fill = try_enter_marketable_limit(entry_bar, round_lot_config())

    assert fill.filled
    assert fill.fill_price == 100.05
    assert fill.limit_price == 100.2


def test_tw_fees_and_taxes():
    config = round_lot_config()

    assert commission(100000, config) == 142.5
    assert sell_tax(100000, config, same_day_exit=False) == 300
    assert sell_tax(100000, config, same_day_exit=True) == 150
