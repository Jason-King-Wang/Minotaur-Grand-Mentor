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
    try:
        import pandas as pd

        pd.DataFrame(rows).to_parquet(path, index=False)
    except Exception as exc:  # pragma: no cover - exercised only without parquet engine
        fallback = path.with_suffix(".csv")
        if rows:
            with fallback.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
        raise RuntimeError(f"Failed to write parquet {path}; CSV fallback: {fallback}") from exc
    return path


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
    _atomic_write_parquet(path, merged_rows)
    return {
        "path": str(path),
        "existing_rows": len(existing_rows),
        "new_rows": len(new_rows),
        "merged_rows": len(merged_rows),
        "inserted_rows": inserted,
        "updated_rows": updated,
        "duplicate_rows_removed": duplicates_removed,
    }


def read_processed_rows(config: dict[str, Any], dataset: str) -> list[dict[str, Any]]:
    path = processed_path(config, dataset)
    if not path.exists():
        return []
    import pandas as pd

    return pd.read_parquet(path).to_dict(orient="records")


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


def _atomic_write_parquet(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.stem}.tmp{path.suffix}")
    try:
        import pandas as pd

        pd.DataFrame(rows).to_parquet(tmp_path, index=False)
        os.replace(tmp_path, path)
    except Exception as exc:  # pragma: no cover - exercised only without parquet engine
        if tmp_path.exists():
            tmp_path.unlink()
        fallback = path.with_suffix(".csv")
        if rows:
            with fallback.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
        raise RuntimeError(f"Failed to write parquet {path}; CSV fallback: {fallback}") from exc
