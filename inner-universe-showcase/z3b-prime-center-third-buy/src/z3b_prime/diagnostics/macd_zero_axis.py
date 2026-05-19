from __future__ import annotations

from z3b_prime.models import MacdLevelDiag


def touches_zero(values: list[float]) -> bool:
    if not values:
        return False
    return min(values) <= 0 <= max(values)


def zero_cross_count(values: list[float]) -> int:
    signs = []
    for value in values:
        if value > 0:
            signs.append(1)
        elif value < 0:
            signs.append(-1)
        else:
            signs.append(0)

    compact = [sign for sign in signs if sign != 0]
    return sum(1 for prev, curr in zip(compact, compact[1:]) if prev != curr)


def classify_zero_axis(dif: list[float], dea: list[float]) -> MacdLevelDiag:
    dif_touch = touches_zero(dif)
    dea_touch = touches_zero(dea)
    dif_crosses = zero_cross_count(dif)
    dea_crosses = zero_cross_count(dea)

    if not dif_touch and not dea_touch:
        return "BELOW_CURRENT"
    if dif_crosses >= 2 and dea_crosses >= 2:
        return "ABOVE_CURRENT_LIKE"
    if dif_touch and dea_touch:
        return "CURRENT_LIKE"
    return "UNKNOWN"
