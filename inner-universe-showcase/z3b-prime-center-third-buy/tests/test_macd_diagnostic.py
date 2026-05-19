from z3b_prime.diagnostics.macd_zero_axis import classify_zero_axis
from z3b_prime.strategy.rules import build_long_signal


def test_macd_zero_axis_diagnostic_does_not_block_trade_by_default(make_bars):
    assert classify_zero_axis([1, 2, 3], [1, 2, 3]) == "BELOW_CURRENT"

    bars = make_bars(
        [
            (110, 116, 108, 115),
            (115, 118, 114, 117),
        ]
    )
    signal = build_long_signal(
        strategy_id="Z3B-Prime",
        symbol="TEST",
        bullish_k=bars[0],
        next_bar=bars[1],
        target_high_1h=130,
        metadata={"macd_level_diag": "BELOW_CURRENT"},
    )

    assert signal.reason_code == "VALID_LONG_SIGNAL"
    assert signal.metadata["macd_level_diag"] == "BELOW_CURRENT"
