import csv

from z3b_prime.backtest.engine import backtest_signals
from z3b_prime.config import strategy_config_from_dict
from z3b_prime.output import write_signal_log, write_trade_log
from z3b_prime.strategy.z3b_prime import run_strategy
from z3b_prime.visualization.annotate import write_annotated_svg


def permissive_test_config():
    return strategy_config_from_dict(
        {
            "swing": {"left_bars": 1, "right_bars": 1},
            "center_detection": {
                "min_center_swings": 4,
                "min_center_bars": 3,
                "min_midline_crosses": 1,
            },
            "execution": {"fee_rate": 0, "slippage_bps": 0},
        }
    )


def test_run_strategy_backtest_and_outputs(synthetic_z3b_bars, tmp_path):
    bars_1h, bars_15m = synthetic_z3b_bars
    config = permissive_test_config()

    result = run_strategy("TEST", bars_1h, bars_15m, config)
    trades = backtest_signals(result.signals, bars_15m, config)

    # Z3B-Core v2 starts 15m analysis only after the 1H pullback gate.
    # This legacy synthetic sample creates its 15m terminal structure too early,
    # so the stricter v2 gate should reject it instead of emitting a trade.
    assert len(result.signals) == 0
    assert len(trades) == 0
    assert result.signal_log

    signal_log = tmp_path / "signal_log.csv"
    trade_log = tmp_path / "trade_log.csv"
    write_signal_log(signal_log, result.signal_log, result.signals)
    write_trade_log(trade_log, trades)

    with trade_log.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert rows == []
    assert "NO_1H_PULLBACK_3BUY" in signal_log.read_text(encoding="utf-8-sig")


def test_reason_codes_are_logged_for_rejections(synthetic_z3b_bars):
    bars_1h, bars_15m = synthetic_z3b_bars
    config = strategy_config_from_dict(
        {
            "swing": {"left_bars": 1, "right_bars": 1},
            "center_detection": {
                "min_center_swings": 4,
                "min_center_bars": 3,
                "min_midline_crosses": 1,
            },
        }
    )
    # Remove the later bars that create b-A and bullish confirmation.
    result = run_strategy("TEST", bars_1h, bars_15m[:7], config)

    assert result.signal_log
    assert all(event.reason_code for event in result.signal_log)
