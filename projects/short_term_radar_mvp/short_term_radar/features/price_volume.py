from __future__ import annotations

from typing import Any

from short_term_radar.utils.math_utils import clip, mean, pct_change, z_score


def rows_until(rows: list[dict[str, Any]], as_of_date: str) -> list[dict[str, Any]]:
    return [row for row in rows if row["trade_date"] <= as_of_date]


def trailing_return(rows: list[dict[str, Any]], window: int) -> float | None:
    if len(rows) <= window:
        return None
    return pct_change(rows[-1]["close"], rows[-window - 1]["close"])


def moving_average(rows: list[dict[str, Any]], window: int) -> float | None:
    if len(rows) < window:
        return None
    return mean([row["close"] for row in rows[-window:]])


def previous_range_high(rows: list[dict[str, Any]], window: int) -> float | None:
    if len(rows) <= window:
        return None
    highs = [row["high"] for row in rows[-window - 1 : -1] if row["high"] is not None]
    return max(highs) if highs else None


def universe_filters(config: dict[str, Any]) -> dict[str, Any]:
    filters = dict(config.get("universe") or {})
    filters.update(config.get("filters") or {})
    if config.get("universe", {}).get("mode"):
        filters["mode"] = config["universe"]["mode"]
    filters.setdefault("mode", "elastic")
    filters.setdefault("min_trading_days", 120)
    filters.setdefault("min_avg_amount_20d", 10_000_000)
    filters.setdefault("excluded_symbols", [])
    filters.setdefault("included_symbols", [])
    return filters


def symbol_is_excluded(row: dict[str, Any], filters: dict[str, Any]) -> bool:
    name = (row.get("name") or "").upper()
    symbol = str(row.get("symbol") or "").upper()
    if filters.get("exclude_etf") and ("ETF" in name or symbol.startswith("00")):
        return True
    if filters.get("exclude_warrant") and "WARRANT" in name:
        return True
    if filters.get("exclude_full_delivery") and "FULL DELIVERY" in name:
        return True
    return False


def compute_market_returns(
    by_symbol: dict[str, list[dict[str, Any]]], as_of_date: str, market_symbol: str, windows: list[int]
) -> dict[int, float | None]:
    market_rows = rows_until(by_symbol.get(market_symbol, []), as_of_date)
    return {window: trailing_return(market_rows, window) for window in windows}


def compute_price_volume_features(
    by_symbol: dict[str, list[dict[str, Any]]], as_of_date: str, config: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    pv_cfg = config["price_volume"]
    filters = universe_filters(config)
    universe_mode = str(filters.get("mode", "elastic"))
    ma_windows = [int(w) for w in pv_cfg["ma_windows"]]
    rs_windows = [int(w) for w in pv_cfg["rs_windows"]]
    breakout_windows = [int(w) for w in pv_cfg["breakout_windows"]]
    market_returns = compute_market_returns(
        by_symbol, as_of_date, config["data"].get("market_index_symbol", "TAIEX"), rs_windows
    )
    included = {str(item) for item in filters.get("included_symbols") or []}
    excluded = {str(item) for item in filters.get("excluded_symbols") or []}

    result: dict[str, dict[str, Any]] = {}
    for symbol, all_rows in by_symbol.items():
        rows = rows_until(all_rows, as_of_date)
        if len(rows) < int(filters["min_trading_days"]):
            continue
        latest = rows[-1]
        if symbol_is_excluded(latest, filters):
            continue
        if included and symbol not in included:
            continue

        amounts_20 = [row["amount"] for row in rows[-20:] if row.get("amount") is not None]
        avg_amount_20 = mean(amounts_20) or 0.0
        if avg_amount_20 < float(filters["min_avg_amount_20d"]):
            continue
        max_avg_amount = filters.get("max_avg_amount_20d")
        if max_avg_amount is not None and avg_amount_20 > float(max_avg_amount):
            continue
        if universe_mode != "all_market" and filters.get("exclude_market_index_heavyweights", True) and symbol in excluded:
            continue

        close = latest["close"]
        volume = latest.get("volume") or 0.0
        volume_window = int(pv_cfg["volume_z_window"])
        volume_values = [row.get("volume") or 0.0 for row in rows[-volume_window:]]
        volume_ma20 = mean(volume_values) or 0.0
        volume_z_20 = z_score(volume, volume_values)
        volume_ratio = volume / volume_ma20 if volume_ma20 else None
        returns = {window: trailing_return(rows, window) for window in [1, 5, 20, 60, 120]}
        mas = {window: moving_average(rows, window) for window in ma_windows}
        rs = {
            window: (returns.get(window) - market_returns.get(window))
            if returns.get(window) is not None and market_returns.get(window) is not None
            else None
            for window in rs_windows
        }

        breakout_flags: dict[int, bool] = {}
        for window in breakout_windows:
            range_high = previous_range_high(rows, window)
            breakout_flags[window] = bool(range_high is not None and close is not None and close > range_high)

        high = latest.get("high") or close
        low = latest.get("low") or close
        open_price = latest.get("open") or close
        price_range = (high - low) if high is not None and low is not None else 0.0
        upper_shadow_ratio = (
            (high - max(open_price, close)) / price_range
            if price_range and high is not None and open_price is not None and close is not None
            else 0.0
        )

        result[symbol] = {
            "symbol": symbol,
            "name": latest.get("name"),
            "industry": latest.get("industry"),
            "trade_date": latest["trade_date"],
            "universe_mode": universe_mode,
            "excluded_by_universe_flag": False,
            "last_close": close,
            "avg_amount_20": avg_amount_20,
            "market_cap": latest.get("market_cap"),
            "share_capital": latest.get("share_capital"),
            "ret_1d": returns[1],
            "ret_5d": returns[5],
            "ret_20d": returns[20],
            "ret_60d": returns[60],
            "ret_120d": returns[120],
            "volume_ma20": volume_ma20,
            "volume_z_20": volume_z_20,
            "volume_expansion_ratio": volume_ratio,
            "rs_20d": rs.get(20),
            "rs_60d": rs.get(60),
            "breakout_60d_flag": breakout_flags.get(60, False),
            "breakout_120d_flag": breakout_flags.get(120, False),
            "breakout_flag": any(breakout_flags.values()),
            "breakout_with_volume_flag": bool(
                any(breakout_flags.values())
                and volume_ratio is not None
                and float(pv_cfg["breakout_volume_min_ratio"])
                <= volume_ratio
                <= float(pv_cfg["breakout_volume_max_ratio"])
            ),
            "above_ma20_flag": bool(mas.get(20) is not None and close > mas[20]),
            "above_ma60_flag": bool(mas.get(60) is not None and close > mas[60]),
            "ma_alignment_bull_flag": bool(
                close is not None
                and mas.get(20) is not None
                and mas.get(60) is not None
                and mas.get(120) is not None
                and close > mas[20] > mas[60] > mas[120]
            ),
            "upper_shadow_ratio": upper_shadow_ratio,
            "limit_up_like_flag": bool(returns[1] is not None and returns[1] >= 0.09),
            "price_data_source": config.get("data", {}).get("price_data_source", "local_daily_price"),
            "survivorship_bias_warning": "delisted coverage unknown unless the source includes historical delistings",
            "has_delisted_data_flag": None,
            "data_quality_flags": ["market_cap_missing"] if latest.get("market_cap") is None else [],
        }
    return result


def score_price_volume(features: dict[str, Any]) -> float:
    score = 0.0
    if features.get("breakout_120d_flag"):
        score += 25
    elif features.get("breakout_60d_flag"):
        score += 18
    if features.get("breakout_with_volume_flag"):
        score += 20
    ratio = features.get("volume_expansion_ratio")
    if ratio is not None and 1.2 <= ratio <= 3.5:
        score += 15
    if features.get("rs_20d") is not None and features["rs_20d"] > 0:
        score += 12
    if features.get("rs_60d") is not None and features["rs_60d"] > 0:
        score += 10
    if features.get("above_ma20_flag"):
        score += 8
    if features.get("above_ma60_flag"):
        score += 5
    if features.get("ma_alignment_bull_flag"):
        score += 10
    if features.get("upper_shadow_ratio", 0) > 0.45:
        score -= 15
    return clip(score)
