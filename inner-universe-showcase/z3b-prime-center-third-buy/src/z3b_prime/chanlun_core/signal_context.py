from __future__ import annotations

from enum import Enum

from z3b_prime.chanlun_core.models import Center


class PriceVsCenter(str, Enum):
    ABOVE_CENTER = "above_center"
    BELOW_CENTER = "below_center"
    INSIDE_CENTER = "inside_center"


def classify_price_vs_center(price: float, center: Center) -> PriceVsCenter:
    if price > center.zg:
        return PriceVsCenter.ABOVE_CENTER
    if price < center.zd:
        return PriceVsCenter.BELOW_CENTER
    return PriceVsCenter.INSIDE_CENTER
