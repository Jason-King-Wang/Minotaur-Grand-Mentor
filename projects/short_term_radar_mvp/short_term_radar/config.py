from __future__ import annotations

from copy import deepcopy
import os
from pathlib import Path
import re
from typing import Any

import yaml


DEFAULT_CONFIG: dict[str, Any] = {
    "data": {
        "daily_price_path": "data/tw_stock_daily",
        "daily_price_format": "auto",
        "symbol_col": "symbol",
        "date_col": "trade_date",
        "market_index_symbol": "TAIEX",
        "use_broker_api": False,
        "broker_api_profile": "default",
    },
    "filters": {
        "min_trading_days": 120,
        "min_avg_amount_20d": 10_000_000,
        "exclude_full_delivery": True,
        "exclude_etf": True,
        "exclude_warrant": True,
    },
    "scoring": {
        "weights": {
            "revenue": 0.25,
            "expectation_gap": 0.20,
            "price_volume": 0.20,
            "theme_group": 0.15,
            "chip": 0.10,
            "catalyst": 0.10,
        },
        "risk_penalty_max": 40,
    },
    "price_volume": {
        "ma_windows": [5, 20, 60, 120, 240],
        "rs_windows": [20, 60],
        "breakout_windows": [60, 120],
        "volume_z_window": 20,
        "breakout_volume_min_ratio": 1.5,
        "breakout_volume_max_ratio": 3.5,
    },
    "expectation_gap": {
        "early_ret_20d_max": 0.35,
        "early_ret_60d_max": 0.80,
        "overheated_ret_20d": 0.80,
        "overheated_ret_60d": 1.50,
        "overheated_volume_z": 4.0,
    },
    "backtest": {
        "start": "2020-01-01",
        "end": "2025-01-01",
        "rebalance": "monthly",
        "top_n": 20,
        "horizon_days": 126,
        "target_multiples": [3, 5],
    },
    "theme_mapping": {},
    "manual_catalysts": {},
}


ENV_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-(.*?))?\}")


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(config_path: str | Path | None) -> dict[str, Any]:
    if not config_path:
        return deepcopy(DEFAULT_CONFIG)

    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")

    loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Config must be a mapping: {path}")
    return expand_env_values(deep_merge(DEFAULT_CONFIG, loaded))


def expand_env_values(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: expand_env_values(item) for key, item in value.items()}
    if isinstance(value, list):
        return [expand_env_values(item) for item in value]
    if not isinstance(value, str):
        return value

    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        default = match.group(2)
        if name in os.environ:
            return os.environ[name]
        return default if default is not None else match.group(0)

    expanded = ENV_PATTERN.sub(replace, value)
    return None if expanded == "" else expanded
