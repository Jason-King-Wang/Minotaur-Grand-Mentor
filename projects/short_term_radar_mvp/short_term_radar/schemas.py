from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class RadarCandidate:
    symbol: str
    name: str | None
    industry: str | None
    trade_date: str
    score_total: float
    score_revenue: float | None
    score_expectation_gap: float | None
    score_price_volume: float | None
    score_theme_group: float | None
    score_chip: float | None
    score_catalyst: float | None
    risk_penalty: float
    stage: str
    entry_zone: str
    reasons: list[str] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)
    last_close: float | None = None
    ret_20d: float | None = None
    ret_60d: float | None = None
    volume_z_20: float | None = None
    rs_20d: float | None = None
    rs_60d: float | None = None
    breakout_flag: bool = False
    created_at: str | None = None

    def to_row(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ForwardLabel:
    symbol: str
    trade_date: str
    forward_max_return: float | None
    forward_close_return: float | None
    forward_max_drawdown: float | None
    hit_3x: bool
    hit_5x: bool

    def to_row(self) -> dict[str, Any]:
        return asdict(self)
