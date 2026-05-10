from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

from short_term_radar.utils.io import read_csv_records
from short_term_radar.utils.math_utils import safe_float


def read_table(path: str | Path | None) -> list[dict[str, Any]]:
    if not path:
        return []
    file_path = Path(path)
    if not file_path.exists():
        return []
    if file_path.is_dir():
        rows: list[dict[str, Any]] = []
        for child in sorted([*file_path.rglob("*.csv"), *file_path.rglob("*.parquet"), *file_path.rglob("*.yaml"), *file_path.rglob("*.yml")]):
            rows.extend(read_table(child))
        return rows
    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        return read_csv_records(file_path)
    if suffix == ".parquet":
        try:
            import pandas as pd
        except ImportError as error:
            raise RuntimeError("Reading parquet files requires pandas and pyarrow.") from error
        return pd.read_parquet(file_path).to_dict("records")
    if suffix in {".yaml", ".yml"}:
        loaded = yaml.safe_load(file_path.read_text(encoding="utf-8")) or []
        if isinstance(loaded, dict):
            if isinstance(loaded.get("events"), list):
                return loaded["events"]
            return [loaded]
        if isinstance(loaded, list):
            return loaded
    return []


def first_value(row: dict[str, Any], aliases: list[str]) -> Any:
    if not row:
        return None
    exact = {str(key): key for key in row.keys()}
    lower = {str(key).lower(): key for key in row.keys()}
    for alias in aliases:
        key = exact.get(alias) or lower.get(alias.lower())
        if key is not None:
            value = row.get(key)
            if value not in (None, ""):
                return value
    return None


def text_value(row: dict[str, Any], aliases: list[str]) -> str | None:
    value = first_value(row, aliases)
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def number_value(row: dict[str, Any], aliases: list[str]) -> float | None:
    return safe_float(first_value(row, aliases))


def rate_value(row: dict[str, Any], aliases: list[str]) -> float | None:
    value = number_value(row, aliases)
    if value is None:
        return None
    return value / 100.0 if abs(value) > 3 else value


def date_text(value: Any) -> str | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    text = str(value).strip().replace("/", "-")
    if not text:
        return None
    return text[:10]


def month_text(value: Any) -> str | None:
    text = date_text(value)
    if not text:
        return None
    if len(text) >= 7:
        return text[:7]
    return text


def next_month_release_date(revenue_month: str | None, day: int = 10) -> str | None:
    if not revenue_month:
        return None
    year, month = [int(part) for part in revenue_month[:7].split("-")]
    month += 1
    if month == 13:
        year += 1
        month = 1
    return date(year, month, day).isoformat()
