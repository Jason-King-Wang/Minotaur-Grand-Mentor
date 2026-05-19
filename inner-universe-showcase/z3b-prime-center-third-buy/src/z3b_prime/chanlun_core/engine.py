from __future__ import annotations

from z3b_prime.chanlun_core.models import (
    Center,
    CenterEvent,
    CenterEventType,
    CenterState,
    Direction,
    TrendUnit,
    UpdateMode,
)


class CenterEngine:
    """Build confirmed centers from confirmed lower-level TrendUnit events."""

    def __init__(
        self,
        symbol: str,
        level: str,
        child_level: str,
        min_units: int = 3,
        update_mode: UpdateMode | str = UpdateMode.FIXED,
    ) -> None:
        if not symbol:
            raise ValueError("symbol is required")
        if not level:
            raise ValueError("level is required")
        if not child_level:
            raise ValueError("child_level is required")
        if min_units < 2:
            raise ValueError("min_units must be >= 2")

        self.symbol = symbol
        self.level = level
        self.child_level = child_level
        self.min_units = min_units
        self.update_mode = UpdateMode(update_mode)
        self.units: list[TrendUnit] = []
        self.active: Center | None = None
        self.completed: list[Center] = []
        self._seen_seqs: set[int] = set()

    @staticmethod
    def calc_overlap(units: list[TrendUnit]) -> tuple[float, float] | None:
        if not units:
            return None
        zd = max(unit.low for unit in units)
        zg = min(unit.high for unit in units)
        return (zd, zg) if zd <= zg else None

    @staticmethod
    def intervals_intersect(low1: float, high1: float, low2: float, high2: float) -> bool:
        return max(low1, low2) <= min(high1, high2)

    @classmethod
    def intersects(cls, unit: TrendUnit, center: Center) -> bool:
        return cls.intervals_intersect(unit.low, unit.high, center.zd, center.zg)

    def on_child_unit(self, unit: TrendUnit) -> list[CenterEvent]:
        self._validate_unit(unit)
        self._seen_seqs.add(unit.seq)
        self.units.append(unit)

        events: list[CenterEvent] = []
        if self.active is not None:
            events.extend(self._update_active_center(unit))
            if events and events[-1].event_type == CenterEventType.EXTENDED:
                return events

        if self.active is None and len(self.units) >= self.min_units:
            event = self._try_start_center(unit)
            if event is not None:
                events.append(event)

        return events

    def _validate_unit(self, unit: TrendUnit) -> None:
        if unit.symbol != self.symbol:
            raise ValueError(f"Expected symbol={self.symbol}, got {unit.symbol}")
        if unit.level != self.child_level:
            raise ValueError(f"Expected child_level={self.child_level}, got {unit.level}")
        if unit.seq in self._seen_seqs:
            raise ValueError(f"Duplicated unit seq: {unit.seq}")
        if self.units and unit.seq <= self.units[-1].seq:
            raise ValueError("TrendUnit seq must be strictly increasing")
        if self.units and unit.confirmed_at < self.units[-1].confirmed_at:
            raise ValueError("confirmed_at must be non-decreasing")

    def _update_active_center(self, unit: TrendUnit) -> list[CenterEvent]:
        active = self.active
        if active is None:
            return []

        if self.intersects(unit, active):
            active.units.append(unit)
            active.end_ts = unit.end_ts
            active.confirmed_at = unit.confirmed_at
            if self.update_mode == UpdateMode.SHRINK:
                active.zd = max(active.zd, unit.low)
                active.zg = min(active.zg, unit.high)
            return [
                CenterEvent(
                    event_type=CenterEventType.EXTENDED,
                    center=active.copy_snapshot(),
                    event_ts=unit.confirmed_at,
                    trigger_unit_seq=unit.seq,
                )
            ]

        if unit.low > active.zg:
            active.break_dir = Direction.UP
        elif unit.high < active.zd:
            active.break_dir = Direction.DOWN

        active.state = CenterState.COMPLETED
        active.confirmed_at = unit.confirmed_at
        snapshot = active.copy_snapshot()
        self.completed.append(snapshot)
        self.active = None
        return [
            CenterEvent(
                event_type=CenterEventType.COMPLETED,
                center=snapshot,
                event_ts=unit.confirmed_at,
                trigger_unit_seq=unit.seq,
            )
        ]

    def _try_start_center(self, unit: TrendUnit) -> CenterEvent | None:
        tail = self.units[-self.min_units :]
        overlap = self.calc_overlap(tail)
        if overlap is None:
            return None

        zd, zg = overlap
        center = Center(
            symbol=self.symbol,
            level=self.level,
            child_level=self.child_level,
            start_ts=tail[0].start_ts,
            end_ts=tail[-1].end_ts,
            zd=zd,
            zg=zg,
            units=list(tail),
            state=CenterState.ACTIVE,
            confirmed_at=unit.confirmed_at,
        )
        self.active = center
        return CenterEvent(
            event_type=CenterEventType.STARTED,
            center=center.copy_snapshot(),
            event_ts=unit.confirmed_at,
            trigger_unit_seq=unit.seq,
        )
