from __future__ import annotations

from collections import defaultdict

from z3b_prime.chanlun_core.engine import CenterEngine
from z3b_prime.chanlun_core.models import CenterEvent, TrendUnit


class MultiLevelCenterRouter:
    """Route confirmed TrendUnit events to center engines by child level."""

    def __init__(self, engines: list[CenterEngine]) -> None:
        self.engines_by_child_level: dict[str, list[CenterEngine]] = defaultdict(list)
        for engine in engines:
            self.engines_by_child_level[engine.child_level].append(engine)

    def on_trend_unit_confirmed(self, unit: TrendUnit) -> list[CenterEvent]:
        events: list[CenterEvent] = []
        for engine in self.engines_by_child_level.get(unit.level, []):
            events.extend(engine.on_child_unit(unit))
        return events
