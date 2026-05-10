from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any
import os
import re

import yaml


ENV_PATTERN = re.compile(r"^\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-(.*))?\}$")


DEFAULT_CONFIG: dict[str, Any] = {
    "data": {
        "daily_price_path": "${TW_EQUITIES_DATA_PATH}",
        "monthly_revenue_path": "${TW_MONTHLY_REVENUE_PATH:-}",
        "chip_data_path": "${TW_CHIP_DATA_PATH:-}",
        "catalyst_path": "${TW_CATALYST_PATH:-}",
        "daily_price_format": "auto",
        "symbol_col": "symbol",
        "date_col": "trade_date",
        "market_index_symbol": "TAIEX",
        "market_index_contract_candidates": ["TSE.TSE001", "TSE001", "TAIEX"],
        "use_broker_api": False,
        "broker_api_profile": "default",
        "price_data_source": "local_daily_price",
        "revenue_data_source": "optional_local_file",
        "chip_data_source": "optional_local_file",
    },
    "filters": {
        "min_trading_days": 120,
        "min_avg_amount_20d": 10_000_000,
        "exclude_full_delivery": True,
        "exclude_etf": True,
        "exclude_warrant": True,
    },
    "universe": {
        "mode": "elastic",
        "min_trading_days": 120,
        "min_avg_amount_20d": 10_000_000,
        "max_avg_amount_20d": None,
        "exclude_etf": True,
        "exclude_warrant": True,
        "exclude_full_delivery": True,
        "exclude_large_cap": True,
        "max_market_cap": None,
        "max_share_capital": None,
        "exclude_market_index_heavyweights": True,
        "excluded_symbols": ["2330", "2317", "2454", "2308", "2412", "6505", "2881", "2882", "1301", "1303"],
        "included_symbols": [],
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
    "catalyst": {
        "catalyst_path": "${TW_CATALYST_PATH:-}",
        "lookahead_days": 126,
        "near_term_days": 45,
    },
    "backtest": {
        "start": "2020-01-01",
        "end": "2025-01-01",
        "rebalance": "monthly",
        "top_n": 20,
        "horizon_days": 126,
        "target_multiples": [2, 3, 5],
        "include_baselines": True,
        "random_trials": 30,
        "seed": 42,
    },
    "theme_mapping": {},
    "manual_catalysts": {},
}


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def expand_env(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: expand_env(item) for key, item in value.items()}
    if isinstance(value, list):
        return [expand_env(item) for item in value]
    if not isinstance(value, str):
        return value
    match = ENV_PATTERN.match(value)
    if not match:
        return value
    name, default = match.group(1), match.group(2)
    if name in os.environ:
        return os.environ[name]
    if default is not None:
        return default or None
    raise KeyError(f"Required environment variable is not set: {name}")


def _backward_compatible_universe(config: dict[str, Any]) -> dict[str, Any]:
    filters = config.get("filters") or {}
    universe = config.setdefault("universe", {})
    for key, value in filters.items():
        universe.setdefault(key, value)
    return config


def load_config(config_path: str | Path | None) -> dict[str, Any]:
    if not config_path:
        return _backward_compatible_universe(expand_env(deepcopy(DEFAULT_CONFIG)))

    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")

    loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Config must be a mapping: {path}")
    merged = deep_merge(DEFAULT_CONFIG, loaded)
    return _backward_compatible_universe(expand_env(merged))
