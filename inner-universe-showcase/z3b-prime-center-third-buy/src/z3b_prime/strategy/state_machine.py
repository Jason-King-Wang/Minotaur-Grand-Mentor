from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from z3b_prime import reason_codes


class State(str, Enum):
    WAIT_1H_CENTER = "WAIT_1H_CENTER"
    WAIT_1H_UPWARD_LEAVE = "WAIT_1H_UPWARD_LEAVE"
    WAIT_1H_STRUCTURE_BREAK = "WAIT_1H_STRUCTURE_BREAK"
    WAIT_1H_PULLBACK_3BUY = "WAIT_1H_PULLBACK_3BUY"
    WAIT_15M_CENTER_A = "WAIT_15M_CENTER_A"
    WAIT_15M_AB_COMPARE = "WAIT_15M_AB_COMPARE"
    WAIT_15M_BA_CENTER = "WAIT_15M_BA_CENTER"
    WAIT_15M_BA_BB_COMPARE = "WAIT_15M_BA_BB_COMPARE"
    WAIT_15M_ISOLATED_LOWS = "WAIT_15M_ISOLATED_LOWS"
    WAIT_15M_ISOLATED_LOWS_AND_GOLDEN_K = "WAIT_15M_ISOLATED_LOWS_AND_GOLDEN_K"
    WAIT_15M_BULLISH_TREND_K = "WAIT_15M_BULLISH_TREND_K"
    IN_POSITION = "IN_POSITION"


ALLOWED_TRANSITIONS = {
    State.WAIT_1H_CENTER: {State.WAIT_1H_UPWARD_LEAVE},
    State.WAIT_1H_UPWARD_LEAVE: {State.WAIT_1H_STRUCTURE_BREAK},
    State.WAIT_1H_STRUCTURE_BREAK: {State.WAIT_1H_PULLBACK_3BUY},
    State.WAIT_1H_PULLBACK_3BUY: {State.WAIT_15M_CENTER_A},
    State.WAIT_15M_CENTER_A: {State.WAIT_15M_AB_COMPARE},
    State.WAIT_15M_AB_COMPARE: {State.WAIT_15M_BA_CENTER},
    State.WAIT_15M_BA_CENTER: {State.WAIT_15M_BA_BB_COMPARE},
    State.WAIT_15M_BA_BB_COMPARE: {
        State.WAIT_15M_ISOLATED_LOWS,
        State.WAIT_15M_ISOLATED_LOWS_AND_GOLDEN_K,
    },
    State.WAIT_15M_ISOLATED_LOWS: {State.WAIT_15M_BULLISH_TREND_K},
    State.WAIT_15M_ISOLATED_LOWS_AND_GOLDEN_K: {State.WAIT_15M_BULLISH_TREND_K},
    State.WAIT_15M_BULLISH_TREND_K: {State.IN_POSITION},
}


@dataclass
class Z3BPrimeStateMachine:
    state: State = State.WAIT_1H_CENTER
    reason_log: list[str] = field(default_factory=list)

    def transition(self, new_state: State) -> None:
        allowed = ALLOWED_TRANSITIONS.get(self.state, set())
        if new_state not in allowed:
            raise ValueError(f"invalid transition: {self.state} -> {new_state}")
        self.state = new_state

    def reset(self) -> None:
        self.state = State.WAIT_1H_CENTER

    def can_accept_bullish_k(self) -> bool:
        return self.state == State.WAIT_15M_BULLISH_TREND_K

    def reject_early_bullish_k(self) -> str | None:
        if self.can_accept_bullish_k():
            return None
        self.reason_log.append(reason_codes.EARLY_BULLISH_K_BEFORE_STRUCTURE_COMPLETE)
        return reason_codes.EARLY_BULLISH_K_BEFORE_STRUCTURE_COMPLETE
