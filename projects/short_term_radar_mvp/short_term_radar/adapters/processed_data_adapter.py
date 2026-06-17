from __future__ import annotations

from pathlib import Path
from typing import Any


class ProcessedDataAdapter:
    def __init__(self, config: dict[str, Any]):
        self.config = config

    @property
    def processed_dir(self) -> Path:
        data_cfg = self.config.get("data") or {}
        if data_cfg.get("processed_data_path"):
            return Path(data_cfg["processed_data_path"])
        data_root = self.config.get("data_root") or data_cfg.get("data_root") or "data"
        return Path(data_root) / "processed"

    def table_path(self, table_name: str) -> Path:
        return self.processed_dir / f"{table_name}.parquet"

    def table_exists(self, table_name: str) -> bool:
        parquet_path = self.table_path(table_name)
        return parquet_path.exists() or parquet_path.with_suffix(".csv").exists()

    def load_table(self, table_name: str) -> list[dict[str, Any]]:
        parquet_path = self.table_path(table_name)
        csv_path = parquet_path.with_suffix(".csv")
        if parquet_path.exists():
            import pandas as pd

            return pd.read_parquet(parquet_path).to_dict(orient="records")
        if csv_path.exists():
            import csv

            with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
                return list(csv.DictReader(handle))
        return []
