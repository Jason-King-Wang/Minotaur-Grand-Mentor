from __future__ import annotations

import csv
from pathlib import Path

from short_term_radar.data_sources.base import FetchResult


class LocalFileFetcher:
    def fetch_csv(self, path: str | Path, source: str, dataset: str) -> FetchResult:
        file_path = Path(path)
        if not file_path.exists():
            return FetchResult(source, dataset, str(file_path), degraded=True, message="local file not found")
        with file_path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        return FetchResult(source, dataset, str(file_path), rows=rows)
