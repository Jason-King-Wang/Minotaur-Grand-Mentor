from __future__ import annotations

from datetime import date, timedelta

from short_term_radar.config import DEFAULT_CONFIG, deep_merge
from short_term_radar.features.price_volume import compute_price_volume_features


def _rows(symbol: str, closes: list[float], volumes: list[float] | None = None):
    start = date(2025, 1, 1)
    volumes = volumes or [1000.0] * len(closes)
    rows = []
    for index, close in enumerate(closes):
        rows.append(
            {
                "symbol": symbol,
                "name": symbol,
                "industry": "AI",
                "trade_date": (start + timedelta(days=index)).isoformat(),
                "open": close * 0.98,
                "high": close,
                "low": close * 0.95,
                "close": close,
                "volume": volumes[index],
                "amount": close * volumes[index],
                "market": "TWSE",
            }
        )
    return rows


def _config():
    return deep_merge(
        DEFAULT_CONFIG,
        {
            "filters": {"min_trading_days": 30, "min_avg_amount_20d": 1},
            "data": {"market_index_symbol": "TAIEX"},
        },
    )


def test_price_volume_features_ma_rs_breakout_and_volume_z():
    market = _rows("TAIEX", [100 + i * 0.1 for i in range(130)])
    stock = _rows("1234", [10 + i * 0.05 for i in range(129)] + [25], [1000] * 129 + [2500])
    as_of = stock[-1]["trade_date"]

    features = compute_price_volume_features({"TAIEX": market, "1234": stock}, as_of, _config())["1234"]

    assert features["above_ma20_flag"] is True
    assert features["breakout_60d_flag"] is True
    assert features["breakout_with_volume_flag"] is True
    assert features["volume_z_20"] is not None
    assert features["rs_20d"] is not None
