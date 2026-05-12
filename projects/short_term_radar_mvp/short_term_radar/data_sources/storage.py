from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import Any

from short_term_radar.data_sources.config import resolve_data_root
from short_term_radar.data_sources.quality import PRIMARY_KEYS
from short_term_radar.data_sources.registry import DATASET_REGISTRY


def data_root(config: dict[str, Any]) -> Path:
    return resolve_data_root(config)


def raw_path(config: dict[str, Any], source: str, dataset: str, date_text: str, suffix: str = "csv") -> Path:
    year, month, day = date_text[:4], date_text[5:7], date_text[8:10]
    return data_root(config) / "raw" / source / dataset / f"yyyy={year}" / f"mm={month}" / f"dd={day}" / f"raw.{suffix}"


def processed_path(config: dict[str, Any], dataset: str) -> Path:
    table = DATASET_REGISTRY.get(dataset).processed_table if dataset in DATASET_REGISTRY else dataset
    return data_root(config) / "processed" / f"{table}.parquet"


def quality_path(config: dict[str, Any], filename: str) -> Path:
    return data_root(config) / "quality" / filename


def sample_path(config: dict[str, Any], filename: str) -> Path:
    return data_root(config) / "samples" / filename


def write_processed_rows(config: dict[str, Any], dataset: str, rows: list[dict[str, Any]]) -> Path:
    path = processed_path(config, dataset)
    path.parent.mkdir(parents=True, exist_ok=True)
    return _write_processed_table(path, rows)


def merge_processed_rows(
    config: dict[str, Any],
    dataset: str,
    new_rows: list[dict[str, Any]],
    mode: str = "upsert",
) -> dict[str, Any]:
    if mode not in {"append", "upsert", "replace"}:
        raise ValueError("mode must be one of: append, upsert, replace")

    path = processed_path(config, dataset)
    table = DATASET_REGISTRY.get(dataset).processed_table if dataset in DATASET_REGISTRY else dataset
    primary_key = PRIMARY_KEYS.get(table)
    if not primary_key:
        raise KeyError(f"No primary key configured for processed table: {table}")

    existing_rows = read_processed_rows(config, dataset)
    merged_rows, inserted, updated, duplicates_removed = _merge_rows(existing_rows, new_rows, primary_key, mode)
    output_path = _write_processed_table(path, merged_rows)
    return {
        "path": str(output_path),
        "existing_rows": len(existing_rows),
        "new_rows": len(new_rows),
        "merged_rows": len(merged_rows),
        "inserted_rows": inserted,
        "updated_rows": updated,
        "duplicate_rows_removed": duplicates_removed,
    }


def read_processed_rows(config: dict[str, Any], dataset: str) -> list[dict[str, Any]]:
    path = processed_path(config, dataset)
    csv_path = path.with_suffix(".csv")
    if path.exists():
        try:
            import pandas as pd

            return pd.read_parquet(path).to_dict(orient="records")
        except Exception:
            if not csv_path.exists():
                raise
    if not csv_path.exists():
        return []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [_coerce_csv_row(row) for row in csv.DictReader(handle)]


def _merge_rows(
    existing_rows: list[dict[str, Any]],
    new_rows: list[dict[str, Any]],
    primary_key: list[str],
    mode: str,
) -> tuple[list[dict[str, Any]], int, int, int]:
    if mode == "replace":
        rows = _dedupe_rows(new_rows, primary_key, prefer_new=True)
        return _sort_rows(rows, primary_key), len(rows), 0, max(0, len(new_rows) - len(rows))

    merged: dict[tuple[Any, ...], dict[str, Any]] = {}
    duplicate_count = 0
    for row in existing_rows:
        key = _row_key(row, primary_key)
        if key in merged:
            duplicate_count += 1
            merged[key] = _choose_row(merged[key], row)
        else:
            merged[key] = dict(row)

    inserted = 0
    updated = 0
    for row in new_rows:
        key = _row_key(row, primary_key)
        if mode == "append":
            if key in merged:
                duplicate_count += 1
                continue
            merged[key] = dict(row)
            inserted += 1
            continue

        if key in merged:
            chosen = _choose_row(merged[key], row, prefer_new_on_tie=True)
            if chosen is not merged[key]:
                merged[key] = dict(chosen)
                updated += 1
            else:
                duplicate_count += 1
        else:
            merged[key] = dict(row)
            inserted += 1

    return _sort_rows(list(merged.values()), primary_key), inserted, updated, duplicate_count


def _dedupe_rows(rows: list[dict[str, Any]], primary_key: list[str], prefer_new: bool = False) -> list[dict[str, Any]]:
    merged: dict[tuple[Any, ...], dict[str, Any]] = {}
    for row in rows:
        key = _row_key(row, primary_key)
        if key not in merged:
            merged[key] = dict(row)
            continue
        merged[key] = dict(row if prefer_new else _choose_row(merged[key], row, prefer_new_on_tie=True))
    return list(merged.values())


def _row_key(row: dict[str, Any], primary_key: list[str]) -> tuple[Any, ...]:
    return tuple(_normalize_key_value(row.get(column)) for column in primary_key)


def _normalize_key_value(value: Any) -> Any:
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return "" if value is None else str(value)


def _choose_row(
    current: dict[str, Any],
    incoming: dict[str, Any],
    prefer_new_on_tie: bool = False,
) -> dict[str, Any]:
    current_ts = str(current.get("fetched_at") or "")
    incoming_ts = str(incoming.get("fetched_at") or "")
    if incoming_ts > current_ts:
        return incoming
    if incoming_ts == current_ts and prefer_new_on_tie:
        return incoming
    return current


def _sort_rows(rows: list[dict[str, Any]], primary_key: list[str]) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda row: _row_key(row, primary_key))


def _write_processed_table(path: Path, rows: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.stem}.tmp{path.suffix}")
    try:
        import pandas as pd

        pd.DataFrame(rows).to_parquet(tmp_path, index=False)
        os.replace(tmp_path, path)
        return path
    except Exception as exc:  # pragma: no cover - exercised only without parquet engine
        if tmp_path.exists():
            tmp_path.unlink()
        fallback = path.with_suffix(".csv")
        _write_csv_fallback(fallback, rows)
        return fallback


def _write_csv_fallback(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        if fieldnames:
            writer.writeheader()
            writer.writerows(rows)


STRING_COLUMNS = {
    "symbol",
    "name",
    "short_name",
    "market",
    "industry",
    "industry_type",
    "source",
    "source_url",
    "fetched_at",
    "revenue_month",
    "data_month",
    "financial_year_quarter",
    "title",
    "description",
    "event_type",
    "rule_clause",
    "note",
    "company_type",
    "raw_market_section",
    "action_type",
    "holiday_name",
    "attention_reason",
    "disposition_condition",
    "disposition_reason",
    "disposition_measure",
    "margin_limit_code",
    "short_limit_code",
    "foreign_registration_country",
    "announce_time",
}


def _coerce_csv_row(row: dict[str, str]) -> dict[str, Any]:
    return {key: _coerce_csv_value(key, value) for key, value in row.items()}


def _coerce_csv_value(column: str, value: str) -> Any:
    if value == "":
        return None
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if column in STRING_COLUMNS or column.endswith("_date"):
        return value
    try:
        number = float(value)
    except ValueError:
        return value
    return int(number) if number.is_integer() else number
