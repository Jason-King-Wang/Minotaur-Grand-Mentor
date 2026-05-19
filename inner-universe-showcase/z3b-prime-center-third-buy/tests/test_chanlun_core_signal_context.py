from z3b_prime.chanlun_core import Center, PriceVsCenter, classify_price_vs_center


def center() -> Center:
    return Center(
        symbol="2330",
        level="1h",
        child_level="15m",
        start_ts=1000,
        end_ts=3000,
        zd=98,
        zg=102,
        confirmed_at=3060,
    )


def test_classify_price_vs_center():
    zhongshu = center()

    assert classify_price_vs_center(103, zhongshu) == PriceVsCenter.ABOVE_CENTER
    assert classify_price_vs_center(97, zhongshu) == PriceVsCenter.BELOW_CENTER
    assert classify_price_vs_center(100, zhongshu) == PriceVsCenter.INSIDE_CENTER
    assert classify_price_vs_center(98, zhongshu) == PriceVsCenter.INSIDE_CENTER
    assert classify_price_vs_center(102, zhongshu) == PriceVsCenter.INSIDE_CENTER
