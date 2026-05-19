from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


SwingKind = Literal["high", "low"]
Direction = Literal["down", "up"]
CenterState = Literal["active", "completed"]
CenterBreakDir = Literal["down", "up"]
MacdLevelDiag = Literal[
    "BELOW_CURRENT",
    "CURRENT_LIKE",
    "ABOVE_CURRENT_LIKE",
    "UNKNOWN",
]


@dataclass(frozen=True)
class Bar:
    symbol: str
    timeframe: str
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0
    close_time: datetime | None = None

    def __post_init__(self) -> None:
        if self.close_time is None:
            object.__setattr__(self, "close_time", self.time)


@dataclass(frozen=True)
class SwingPoint:
    symbol: str
    timeframe: str
    time: datetime
    confirmed_time: datetime
    kind: SwingKind
    price: float
    bar_index: int


@dataclass
class Center:
    id: str
    symbol: str
    timeframe: str
    start_time: datetime
    end_time: datetime
    upper: float
    lower: float
    mid: float
    range: float
    duration_bars: int
    score: float
    start_index: int
    end_index: int
    macd_level_diag: MacdLevelDiag = "UNKNOWN"
    confirmed_time: datetime | None = None
    overlap_upper: float | None = None
    overlap_lower: float | None = None
    box_high: float | None = None
    box_low: float | None = None
    member_leg_count: int = 0
    state: CenterState = "active"
    break_dir: CenterBreakDir | None = None
    completed_time: datetime | None = None
    source_type: str = "swing_simplified"
    extension_count: int = 0
    midline_crosses: int = 0


@dataclass(frozen=True)
class Leg:
    name: str
    start_time: datetime
    end_time: datetime
    start_price: float
    end_price: float
    direction: Direction
    length: float
    start_index: int | None = None
    end_index: int | None = None
    confirmed_time: datetime | None = None


@dataclass
class TradeSignal:
    strategy_id: str
    symbol: str
    signal_time: datetime
    entry_time: datetime
    entry_price: float
    stop_loss: float
    take_profit: float
    rr: float
    reason_code: str
    metadata: dict = field(default_factory=dict)


@dataclass
class SignalEvent:
    strategy_id: str
    symbol: str
    time: datetime
    state: str
    reason_code: str
    message: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class TradeResult:
    trade_id: str
    strategy_id: str
    symbol: str
    entry_time: datetime
    entry_price: float
    stop_loss: float
    take_profit: float
    exit_time: datetime
    exit_price: float
    exit_reason: str
    pnl: float
    pnl_pct: float
    rr_planned: float
    holding_bars: int
    metadata: dict = field(default_factory=dict)
