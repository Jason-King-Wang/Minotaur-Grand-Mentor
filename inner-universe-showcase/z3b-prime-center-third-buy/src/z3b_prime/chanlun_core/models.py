from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Direction(str, Enum):
    UP = "up"
    DOWN = "down"


class CenterState(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"


class CenterEventType(str, Enum):
    STARTED = "center_started"
    EXTENDED = "center_extended"
    COMPLETED = "center_completed"


class UpdateMode(str, Enum):
    FIXED = "fixed"
    SHRINK = "shrink"


@dataclass(frozen=True)
class TrendUnit:
    """A confirmed lower-level trend unit available only at confirmed_at."""

    symbol: str
    level: str
    seq: int
    start_ts: int
    end_ts: int
    direction: Direction
    low: float
    high: float
    confirmed_at: int

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("symbol is required")
        if not self.level:
            raise ValueError("level is required")
        if self.seq < 0:
            raise ValueError("seq must be non-negative")
        if self.start_ts > self.end_ts:
            raise ValueError("start_ts must be <= end_ts")
        if self.confirmed_at < self.end_ts:
            raise ValueError("confirmed_at must be >= end_ts to avoid look-ahead")
        if self.low > self.high:
            raise ValueError("low must be <= high")


@dataclass
class Center:
    symbol: str
    level: str
    child_level: str
    start_ts: int
    end_ts: int
    zd: float
    zg: float
    units: list[TrendUnit] = field(default_factory=list)
    state: CenterState = CenterState.ACTIVE
    confirmed_at: int = 0
    break_dir: Direction | None = None

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("symbol is required")
        if not self.level:
            raise ValueError("level is required")
        if not self.child_level:
            raise ValueError("child_level is required")
        if self.start_ts > self.end_ts:
            raise ValueError("start_ts must be <= end_ts")
        if self.zd > self.zg:
            raise ValueError("zd must be <= zg")
        if self.confirmed_at and self.confirmed_at < self.end_ts:
            raise ValueError("confirmed_at must be >= end_ts")

    def copy_snapshot(self) -> Center:
        return Center(
            symbol=self.symbol,
            level=self.level,
            child_level=self.child_level,
            start_ts=self.start_ts,
            end_ts=self.end_ts,
            zd=self.zd,
            zg=self.zg,
            units=list(self.units),
            state=self.state,
            confirmed_at=self.confirmed_at,
            break_dir=self.break_dir,
        )


@dataclass(frozen=True)
class CenterEvent:
    event_type: CenterEventType
    center: Center
    event_ts: int
    trigger_unit_seq: int

    def __post_init__(self) -> None:
        if self.event_ts < self.center.confirmed_at:
            raise ValueError("event_ts must be >= center.confirmed_at")
        if self.trigger_unit_seq < 0:
            raise ValueError("trigger_unit_seq must be non-negative")
