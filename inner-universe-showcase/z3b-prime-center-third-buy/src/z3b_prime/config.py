from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class SwingConfig:
    left_bars: int = 2
    right_bars: int = 2


@dataclass(frozen=True)
class CenterDetectionConfig:
    min_center_swings: int = 4
    min_center_bars: int = 5
    min_midline_crosses: int = 2
    use_edges: str = "wick_extreme"


@dataclass(frozen=True)
class MacdConfig:
    fast: int = 12
    slow: int = 26
    signal: int = 9


@dataclass(frozen=True)
class EntryConfirmationConfig:
    bullish_k_body_ratio_of_ba_range: float = 0.25
    bullish_k_requires_close_gt_open: bool = True
    bullish_k_min_body_range_ratio: float = 0.60
    bullish_k_max_upper_wick_ratio: float = 0.20
    bullish_k_min_close_position: float = 0.75
    bullish_k_require_close_above_local_resistance: bool = True
    bullish_k_max_bars_after_low2: int = 8


@dataclass(frozen=True)
class QuantityConfig:
    lot_size_shares: int = 1
    min_order_quantity_shares: int = 1
    max_order_quantity_shares: int | None = None
    round_to_lot_size: bool = True
    allow_odd_lot_remainder: bool = False
    cap_qty_at_999: bool = False
    allow_round_lot_conversion: bool = False


@dataclass(frozen=True)
class ExecutionConfig:
    entry_order_type: str = "marketable_limit"
    allow_pure_market_order: bool = False
    entry_order_timeout_bars: int = 1
    entry_slippage_bps: float = 0.0
    max_entry_slippage_bps: float = 0.0
    stop_slippage_bps: float = 0.0
    ambiguous_bar_policy: str = "stop_first"
    chase_if_not_filled: bool = False
    odd_lot_fill_model: str = ""
    odd_lot_requires_intraday_odd_lot_volume: bool = False
    proxy_fill_allowed_if_odd_lot_volume_missing: bool = False


@dataclass(frozen=True)
class PositionSizingConfig:
    method: str = "risk_percent"
    risk_per_trade_pct: float = 0.005
    max_cash_per_trade_pct: float = 0.2
    min_order_value_twd: float = 0.0


@dataclass(frozen=True)
class LiquidityFilterConfig:
    enabled: bool = False
    min_avg_volume_20_shares: int = 0
    max_order_participation_pct: float = 1.0
    require_nonzero_volume_on_entry_bar: bool = False
    reduce_qty_if_exceeds_volume_cap: bool = True
    require_odd_lot_volume_if_available: bool = False


@dataclass(frozen=True)
class FeesAndTaxesConfig:
    commission_bps_before_discount: float = 0.0
    commission_discount: float = 1.0
    min_commission_twd: float = 0.0
    sell_tax_bps: float = 0.0
    sell_tax_bps_day_trade_round_lot: float | None = None
    apply_day_trade_tax_reduction_if_qualified: bool = False
    odd_lot_uses_day_trade_tax_reduction: bool = False


@dataclass(frozen=True)
class RiskAnchorConfig:
    stop_loss_source: str = "golden_k_low"
    forbid_bullish_k_low_as_stop: bool = True


@dataclass(frozen=True)
class StrategyConfig:
    strategy_id: str = "Z3B-Prime"
    execution_profile: str = "generic"
    swing: SwingConfig = SwingConfig()
    center_detection: CenterDetectionConfig = CenterDetectionConfig()
    macd: MacdConfig = MacdConfig()
    entry_confirmation: EntryConfirmationConfig = EntryConfirmationConfig()
    macd_hard_filter: bool = False
    fee_rate: float = 0.0005
    slippage_bps: float = 0.0
    ambiguous_bar_policy: str = "stop_first"
    quantity: QuantityConfig = QuantityConfig()
    execution: ExecutionConfig = ExecutionConfig()
    position_sizing: PositionSizingConfig = PositionSizingConfig()
    liquidity_filter: LiquidityFilterConfig = LiquidityFilterConfig()
    fees_and_taxes: FeesAndTaxesConfig = FeesAndTaxesConfig()
    risk_anchor: RiskAnchorConfig = RiskAnchorConfig()


def load_config(path: str | Path) -> StrategyConfig:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return strategy_config_from_dict(data)


def strategy_config_from_dict(data: dict[str, Any]) -> StrategyConfig:
    diag = data.get("center_level_diagnostic") or {}
    execution = ExecutionConfig(
        **known_fields(ExecutionConfig, data.get("execution") or {})
    )
    return StrategyConfig(
        strategy_id=data.get("strategy_id", "Z3B-Prime"),
        execution_profile=data.get("execution_profile", "generic"),
        swing=SwingConfig(**known_fields(SwingConfig, data.get("swing") or {})),
        center_detection=CenterDetectionConfig(
            **known_fields(CenterDetectionConfig, data.get("center_detection") or {})
        ),
        macd=MacdConfig(**known_fields(MacdConfig, data.get("macd") or {})),
        entry_confirmation=EntryConfirmationConfig(
            **known_fields(
                EntryConfirmationConfig, data.get("entry_confirmation") or {}
            )
        ),
        macd_hard_filter=bool(diag.get("hard_filter", False)),
        fee_rate=float((data.get("execution") or {}).get("fee_rate", 0.0005)),
        slippage_bps=float((data.get("execution") or {}).get("slippage_bps", 0.0)),
        ambiguous_bar_policy=execution.ambiguous_bar_policy,
        quantity=QuantityConfig(
            **known_fields(QuantityConfig, data.get("quantity") or {})
        ),
        execution=execution,
        position_sizing=PositionSizingConfig(
            **known_fields(PositionSizingConfig, data.get("position_sizing") or {})
        ),
        liquidity_filter=LiquidityFilterConfig(
            **known_fields(LiquidityFilterConfig, data.get("liquidity_filter") or {})
        ),
        fees_and_taxes=FeesAndTaxesConfig(
            **known_fields(FeesAndTaxesConfig, data.get("fees_and_taxes") or {})
        ),
        risk_anchor=RiskAnchorConfig(
            **known_fields(RiskAnchorConfig, data.get("risk_anchor") or {})
        ),
    )


def known_fields(cls, values: dict[str, Any]) -> dict[str, Any]:
    allowed = set(cls.__dataclass_fields__.keys())
    return {key: value for key, value in values.items() if key in allowed}
