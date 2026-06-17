from __future__ import annotations

from datetime import date, timedelta

from short_term_radar.config import DEFAULT_CONFIG, deep_merge
from short_term_radar.features.price_volume import compute_price_volume_features


def _rows(symbol: str, closes: list[float]):
    start = date(2025, 1, 1)
    return [
        {
            "symbol": symbol,
            "name": symbol,
            "industry": "AI",
            "trade_date": (start + timedelta(days=index)).isoformat(),
            "open": close,
            "high": close,
            "low": close,
            "close": close,
            "volume": 1000,
            "amount": close * 1000,
            "market": "TWSE",
        }
        for index, close in enumerate(closes)
    ]


def test_features_do_not_change_when_future_rows_are_added():
    cfg = deep_merge(
        DEFAULT_CONFIG,
        {"filters": {"min_trading_days": 30, "min_avg_amount_20d": 1}},
    )
    stock_until_t = _rows("1234", [10 + i * 0.1 for i in range(80)])
    market_until_t = _rows("TAIEX", [100 + i * 0.1 for i in range(80)])
    as_of = stock_until_t[-1]["trade_date"]
    future_start = date.fromisoformat(as_of) + timedelta(days=1)
    stock_future = []
    market_future = []
    for index, close in enumerate([500, 600, 700]):
        trade_date = (future_start + timedelta(days=index)).isoformat()
        stock_future.append({**stock_until_t[-1], "trade_date": trade_date, "close": close, "high": close})
        market_future.append({**market_until_t[-1], "trade_date": trade_date, "close": close, "high": close})
    stock_with_future = stock_until_t + stock_future
    market_with_future = market_until_t + market_future

    before = compute_price_volume_features({"1234": stock_until_t, "TAIEX": market_until_t}, as_of, cfg)["1234"]
    after = compute_price_volume_features({"1234": stock_with_future, "TAIEX": market_with_future}, as_of, cfg)["1234"]

    assert after["ret_20d"] == before["ret_20d"]
    assert after["breakout_flag"] == before["breakout_flag"]
    assert after["last_close"] == before["last_close"]
