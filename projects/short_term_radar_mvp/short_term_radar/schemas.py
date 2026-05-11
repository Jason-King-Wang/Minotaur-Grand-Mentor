from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ScoreBreakdown:
    score_raw_available_norm: float
    score_coverage_adjusted: float
    score_cap: float
    score_total: float
    score_data_coverage_ratio: float
    robot_slot_coverage_ratio: float
    available_radars: list[str] = field(default_factory=list)
    degraded_radars: list[str] = field(default_factory=list)
    core_data_ready_flag: bool = True

    def to_row(self) -> dict[str, Any]:
        return asdict(self)


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
    score_raw_available_norm: float | None = None
    score_coverage_adjusted: float | None = None
    score_cap: float | None = None
    reasons: list[str] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)
    last_close: float | None = None
    ret_20d: float | None = None
    ret_60d: float | None = None
    volume_z_20: float | None = None
    rs_20d: float | None = None
    rs_60d: float | None = None
    breakout_flag: bool = False
    breakout_120d_flag: bool = False
    volume_expansion_ratio: float | None = None
    ma_alignment_bull_flag: bool = False
    score_data_coverage_ratio: float | None = None
    robot_slot_coverage_ratio: float | None = None
    available_radars: list[str] = field(default_factory=list)
    degraded_radars: list[str] = field(default_factory=list)
    core_data_ready_flag: bool = True
    created_at: str | None = None

    def to_row(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ForwardLabel:
    symbol: str
    trade_date: str
    forward_max_return: float | None
    forward_close_return: float | None
    forward_min_return_from_entry: float | None
    forward_path_max_drawdown: float | None
    hit_3x: bool
    hit_5x: bool

    @property
    def forward_max_drawdown(self) -> float | None:
        return self.forward_min_return_from_entry

    def to_row(self) -> dict[str, Any]:
        row = asdict(self)
        row["forward_max_drawdown"] = self.forward_max_drawdown
        return row
