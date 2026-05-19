from __future__ import annotations


def ema(values: list[float], period: int) -> list[float]:
    if period <= 0:
        raise ValueError("period must be positive")
    if not values:
        return []

    alpha = 2 / (period + 1)
    out = [float(values[0])]
    for value in values[1:]:
        out.append((float(value) * alpha) + (out[-1] * (1 - alpha)))
    return out


def macd(
    closes: list[float],
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> list[dict[str, float]]:
    fast_ema = ema(closes, fast)
    slow_ema = ema(closes, slow)
    dif = [fast_value - slow_value for fast_value, slow_value in zip(fast_ema, slow_ema)]
    dea = ema(dif, signal)
    return [
        {"dif": dif_value, "dea": dea_value, "hist": dif_value - dea_value}
        for dif_value, dea_value in zip(dif, dea)
    ]
