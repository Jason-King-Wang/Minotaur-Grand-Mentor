from __future__ import annotations

from typing import Any

from short_term_radar.adapters.daily_price_adapter import DailyPriceAdapter


def load_daily_prices(config: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    return DailyPriceAdapter(config).load()
