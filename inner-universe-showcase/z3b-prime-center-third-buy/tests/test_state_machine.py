from z3b_prime.reason_codes import EARLY_BULLISH_K_BEFORE_STRUCTURE_COMPLETE
from z3b_prime.strategy.state_machine import State, Z3BPrimeStateMachine


def test_early_bullish_k_before_structure_complete_rejected():
    machine = Z3BPrimeStateMachine()

    assert machine.reject_early_bullish_k() == EARLY_BULLISH_K_BEFORE_STRUCTURE_COMPLETE
    assert machine.reason_log == [EARLY_BULLISH_K_BEFORE_STRUCTURE_COMPLETE]


def test_state_machine_reaches_bullish_k_state_in_order():
    machine = Z3BPrimeStateMachine()
    for state in [
        State.WAIT_1H_UPWARD_LEAVE,
        State.WAIT_1H_STRUCTURE_BREAK,
        State.WAIT_1H_PULLBACK_3BUY,
        State.WAIT_15M_CENTER_A,
        State.WAIT_15M_AB_COMPARE,
        State.WAIT_15M_BA_CENTER,
        State.WAIT_15M_BA_BB_COMPARE,
        State.WAIT_15M_ISOLATED_LOWS,
        State.WAIT_15M_BULLISH_TREND_K,
    ]:
        machine.transition(state)

    assert machine.can_accept_bullish_k()
