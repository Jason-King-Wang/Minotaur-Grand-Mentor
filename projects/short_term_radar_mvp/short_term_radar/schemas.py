from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ScoreBreakdown:
    score_raw_available_norm: float
    score_coverage_adjusted: float
    score_cap: float
    score_total: float
    data_coverage_ratio: float
    available_radars: list[str] = field(default_factory=list)
    degraded_radars: list[str] = field(default_factory=list)
    core_data_ready_flag: bool = False

    def to_row(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RadarCandidate:
    rank: int | None
    symbol: str
    name: str | None
    industry: str | None
    trade_date: str
    universe_mode: str
    score_total: float
    score_raw_available_norm: float
    score_coverage_adjusted: float
    score_cap: float
    data_coverage_ratio: float
    available_radars: list[str]
    degraded_radars: list[str]
    core_data_ready_flag: bool
    score_revenue: float | None
    score_expectation_gap: float | None
    expectation_gap_source: str
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
    avg_amount_20: float | None = None
    ret_20d: float | None = None
    ret_60d: float | None = None
    ret_120d: float | None = None
    volume_z_20: float | None = None
    volume_expansion_ratio: float | None = None
    rs_20d: float | None = None
    rs_60d: float | None = None
    breakout_flag: bool = False
    breakout_60d_flag: bool = False
    breakout_120d_flag: bool = False
    rev_1m_yoy: float | None = None
    rev_3m_yoy: float | None = None
    rev_6m_yoy: float | None = None
    rev_3m_vs_12m_acceleration: float | None = None
    latest_revenue_month: str | None = None
    latest_revenue_release_date: str | None = None
    foreign_buy_5d: float | None = None
    investment_trust_buy_5d: float | None = None
    inst_buy_total_20d: float | None = None
    margin_change_20d: float | None = None
    next_catalyst_date: str | None = None
    next_catalyst_category: str | None = None
    excluded_by_universe_flag: bool = False
    market_cap: float | None = None
    share_capital: float | None = None
    data_quality_flags: list[str] = field(default_factory=list)
    survivorship_bias_warning: str | None = None
    has_delisted_data_flag: bool | None = None
    price_data_source: str | None = None
    revenue_data_source: str | None = None
    chip_data_source: str | None = None
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
    hit_2x: bool
    hit_3x: bool
    hit_5x: bool
    time_to_2x_days: int | None = None
    time_to_3x_days: int | None = None
    time_to_5x_days: int | None = None

    def to_row(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def forward_max_drawdown(self) -> float | None:
        return self.forward_path_max_drawdown
