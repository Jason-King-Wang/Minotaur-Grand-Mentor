from __future__ import annotations

import os
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml


DEFAULT_DATA_SOURCE_CONFIG: dict[str, Any] = {
    "data_root": "${TW_RADAR_DATA_ROOT:-data}",
    "existing_daily_price_path": "${TW_EQUITIES_DATA_PATH:-}",
    "fetch": {
        "user_agent": "short-term-radar-mvp/0.2",
        "timeout_seconds": 30,
        "retry_count": 3,
        "sleep_seconds": 1.0,
        "respect_source_rate_limits": True,
    },
    "sources": {
        "twse": {"enabled": True, "open_data_base": "https://data.gov.tw", "datasets": {}},
        "tpex": {"enabled": True, "open_data_base": "https://data.gov.tw", "datasets": {}},
        "twse_eshop": {"enabled": False, "datasets": {}},
        "broker_api": {
            "enabled": False,
            "provider": "shioaji",
            "readonly_only": True,
            "allow_order_methods": False,
        },
    },
}

_ENV_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}")


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def expand_env(value: Any) -> Any:
    if isinstance(value, str):
        return _ENV_PATTERN.sub(lambda match: os.environ.get(match.group(1), match.group(2) or ""), value)
    if isinstance(value, list):
        return [expand_env(item) for item in value]
    if isinstance(value, dict):
        return {key: expand_env(item) for key, item in value.items()}
    return value


def load_data_source_config(path: str | Path | None = None) -> dict[str, Any]:
    loaded: dict[str, Any] = {}
    if path:
        config_path = Path(path)
        if not config_path.exists():
            raise FileNotFoundError(f"Data source config not found: {config_path}")
        loaded = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        if not isinstance(loaded, dict):
            raise ValueError(f"Data source config must be a mapping: {config_path}")
    return expand_env(deep_merge(DEFAULT_DATA_SOURCE_CONFIG, loaded))


def resolve_data_root(config: dict[str, Any]) -> Path:
    return Path(config.get("data_root") or "data")
