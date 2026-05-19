import pytest

from z3b_prime.backtest.broker import stop_take_exit_reason
from z3b_prime.models import Leg
from z3b_prime.reason_codes import (
    AMBIGUOUS_BAR_STOP_FIRST,
    INVALID_RISK_ENTRY_LE_STOP,
    INVALID_TARGET_LE_ENTRY,
)
from z3b_prime.strategy.rules import (
    a_b_direct_entry_allowed_v1_1,
    a_b_goes_to_bA_path,
    bA_is_smaller_than_A,
    bb_low_holds_ba_low,
    bb_less_than_ba,
    build_long_signal,
    has_upward_leave,
    is_bullish_trend_k,
    isolated_lows_hold,
    pullback_holds_center_upper,
)


def leg(name, length):
    return Leg(
        name=name,
        start_time=None,
        end_time=None,
        start_price=100,
        end_price=100 - length,
        direction="down",
        length=length,
    )


def test_1h_upward_leave_requires_close_above_center_upper(make_bars, center):
    center_1h = center(upper=110, lower=100)
    below, above = make_bars([(108, 111, 105, 110), (110, 113, 109, 111)])

    assert not has_upward_leave(below, center_1h)
    assert has_upward_leave(above, center_1h)


def test_1h_pullback_low_must_not_break_center_upper(make_bars, center):
    center_1h = center(upper=110, lower=100)
    hold, break_ = make_bars([(112, 115, 110, 113), (112, 115, 109.9, 113)])

    assert pullback_holds_center_upper(hold, center_1h)
    assert not pullback_holds_center_upper(break_, center_1h)


def test_ab_compare_b_greater_a_goes_to_bA_path():
    assert a_b_goes_to_bA_path(leg("a", 10), leg("b", 12))


def test_ab_compare_b_less_a_no_longer_allows_direct_path():
    assert not a_b_direct_entry_allowed_v1_1(leg("a", 12), leg("b", 8))


def test_bA_must_be_smaller_than_A(center):
    assert bA_is_smaller_than_A(
        center("A", 120, 100, start_index=0, end_index=10),
        center("bA", 110, 100, start_index=6, end_index=10),
    )
    assert not bA_is_smaller_than_A(
        center("A", 110, 100, start_index=0, end_index=10),
        center("bA", 120, 100, start_index=6, end_index=10),
    )


def test_bb_less_than_ba_allows_next_confirmation_state():
    assert bb_less_than_ba(leg("b-a", 10), leg("b-b", 8))
    assert not bb_less_than_ba(leg("b-a", 10), leg("b-b", 10))


def test_bb_low_must_not_break_ba_low():
    assert bb_low_holds_ba_low(leg("b-a", 10), leg("b-b", 8))
    assert not bb_low_holds_ba_low(leg("b-a", 10), leg("b-b", 12))


def test_second_low_must_not_break_first_low(swing):
    assert isolated_lows_hold(swing("low", 100, 1), swing("low", 101, 3))
    assert not isolated_lows_hold(swing("low", 100, 1), swing("low", 99, 3))


def test_bullish_trend_k_body_threshold(make_bars, center):
    small, strong = make_bars([(100, 103, 99, 102), (100, 106, 99, 105)])
    center_bA = center("bA", 120, 100)

    assert not is_bullish_trend_k(small, center_bA)
    assert is_bullish_trend_k(strong, center_bA)


def test_stop_loss_is_bullish_k_low(make_bars):
    bullish_k, next_bar = make_bars([(100, 106, 99, 105), (106, 108, 105, 107)])

    signal = build_long_signal(
        strategy_id="Z3B-Prime",
        symbol="TEST",
        bullish_k=bullish_k,
        next_bar=next_bar,
        target_high_1h=130,
    )

    assert signal.stop_loss == 99


def test_take_profit_is_1h_target_high(make_bars):
    bullish_k, next_bar = make_bars([(100, 106, 99, 105), (106, 108, 105, 107)])

    signal = build_long_signal(
        strategy_id="Z3B-Prime",
        symbol="TEST",
        bullish_k=bullish_k,
        next_bar=next_bar,
        target_high_1h=130,
    )

    assert signal.take_profit == 130


def test_entry_uses_next_15m_open(make_bars):
    bullish_k, next_bar = make_bars([(100, 106, 99, 105), (106, 108, 105, 107)])

    signal = build_long_signal(
        strategy_id="Z3B-Prime",
        symbol="TEST",
        bullish_k=bullish_k,
        next_bar=next_bar,
        target_high_1h=130,
    )

    assert signal.entry_price == next_bar.open


def test_invalid_risk_and_target_reason_codes(make_bars):
    bullish_k, next_bar = make_bars([(100, 106, 105, 105), (104, 108, 103, 107)])
    with pytest.raises(ValueError, match=INVALID_RISK_ENTRY_LE_STOP):
        build_long_signal(
            strategy_id="Z3B-Prime",
            symbol="TEST",
            bullish_k=bullish_k,
            next_bar=next_bar,
            target_high_1h=130,
        )

    bullish_k, next_bar = make_bars([(100, 106, 99, 105), (106, 108, 105, 107)])
    with pytest.raises(ValueError, match=INVALID_TARGET_LE_ENTRY):
        build_long_signal(
            strategy_id="Z3B-Prime",
            symbol="TEST",
            bullish_k=bullish_k,
            next_bar=next_bar,
            target_high_1h=105,
        )


def test_ambiguous_bar_stop_first(make_bars):
    bar = make_bars([(100, 125, 95, 110)])[0]

    assert stop_take_exit_reason(bar, stop_loss=98, take_profit=120) == AMBIGUOUS_BAR_STOP_FIRST
