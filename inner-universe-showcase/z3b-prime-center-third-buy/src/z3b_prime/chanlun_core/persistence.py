from __future__ import annotations

from dataclasses import asdict
from enum import Enum
from typing import Any

from z3b_prime.chanlun_core.models import Center, CenterEvent, TrendUnit


def trend_unit_to_dict(unit: TrendUnit) -> dict[str, Any]:
    return _enum_values(asdict(unit))


def center_to_dict(center: Center) -> dict[str, Any]:
    return _enum_values(asdict(center))


def center_event_to_dict(event: CenterEvent) -> dict[str, Any]:
    return _enum_values(asdict(event))


def _enum_values(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {key: _enum_values(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_enum_values(item) for item in value]
    return value
