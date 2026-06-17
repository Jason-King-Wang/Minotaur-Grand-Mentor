from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DatasetRequest:
    dataset: str
    market: str = "all"
    date: str | None = None
    month: str | None = None
    start: str | None = None
    end: str | None = None
    start_month: str | None = None
    end_month: str | None = None
    dry_run: bool = False


@dataclass(frozen=True)
class FetchResult:
    source: str
    dataset: str
    url: str | None
    rows: list[dict[str, Any]] = field(default_factory=list)
    raw_text: str | None = None
    degraded: bool = False
    message: str | None = None


@dataclass(frozen=True)
class CollectorPlan:
    dataset: str
    market: str
    source: str
    url: str | None
    enabled: bool
    note: str | None = None


class DataSourceError(RuntimeError):
    pass
