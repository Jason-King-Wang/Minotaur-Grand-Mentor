from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from short_term_radar.data_sources.config import resolve_data_root
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


def read_processed_rows(config: dict[str, Any], dataset: str) -> list[dict[str, Any]]:
    path = processed_path(config, dataset)
    if not path.exists():
        return []
    import pandas as pd

    return pd.read_parquet(path).to_dict(orient="records")
