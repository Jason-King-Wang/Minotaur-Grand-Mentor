from __future__ import annotations

from typing import Any

from short_term_radar.data_sources.normalizers.common import (
    fetched_at_text,
    first_value,
    iso_date,
    normalize_market,
    normalize_symbol,
    parse_number_zh_tw,
)


def normalize_institutional_trading_rows(
    rows: list[dict[str, Any]],
    market: str,
    source: str,
    source_url: str,
    fetched_at: Any = None,
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for row in rows:
        foreign_buy = parse_number_zh_tw(first_value(row, "外陸資買進股數", "外資買進", "foreign_buy"))
        foreign_sell = parse_number_zh_tw(first_value(row, "外陸資賣出股數", "外資賣出", "foreign_sell"))
        investment_buy = parse_number_zh_tw(first_value(row, "投信買進股數", "投信買進", "investment_trust_buy"))
        investment_sell = parse_number_zh_tw(first_value(row, "投信賣出股數", "投信賣出", "investment_trust_sell"))
        dealer_buy = parse_number_zh_tw(first_value(row, "自營商買進股數", "自營商買進", "dealer_buy"))
        dealer_sell = parse_number_zh_tw(first_value(row, "自營商賣出股數", "自營商賣出", "dealer_sell"))
        normalized.append(
            {
                "trade_date": iso_date(first_value(row, "日期", "資料日期", "trade_date")),
                "market": normalize_market(first_value(row, "市場", "market") or market),
                "symbol": normalize_symbol(first_value(row, "證券代號", "股票代號", "代號", "symbol")),
                "name": first_value(row, "證券名稱", "名稱", "name"),
                "foreign_buy": foreign_buy,
                "foreign_sell": foreign_sell,
                "foreign_net": parse_number_zh_tw(first_value(row, "外資及陸資淨買股數", "外陸資買賣超股數", "foreign_net"))
                or _net(foreign_buy, foreign_sell),
                "investment_trust_buy": investment_buy,
                "investment_trust_sell": investment_sell,
                "investment_trust_net": parse_number_zh_tw(
                    first_value(row, "投信淨買股數", "投信買賣超股數", "investment_trust_net")
                )
                or _net(investment_buy, investment_sell),
                "dealer_buy": dealer_buy,
                "dealer_sell": dealer_sell,
                "dealer_net": parse_number_zh_tw(first_value(row, "自營商淨買股數", "自營商買賣超股數", "dealer_net"))
                or _net(dealer_buy, dealer_sell),
                "dealer_self_buy": parse_number_zh_tw(first_value(row, "自營商自行買賣買進", "dealer_self_buy")),
                "dealer_self_sell": parse_number_zh_tw(first_value(row, "自營商自行買賣賣出", "dealer_self_sell")),
                "dealer_self_net": parse_number_zh_tw(first_value(row, "自營商自行買賣買賣超", "dealer_self_net")),
                "dealer_hedge_buy": parse_number_zh_tw(first_value(row, "自營商避險買進", "dealer_hedge_buy")),
                "dealer_hedge_sell": parse_number_zh_tw(first_value(row, "自營商避險賣出", "dealer_hedge_sell")),
                "dealer_hedge_net": parse_number_zh_tw(first_value(row, "自營商避險買賣超", "dealer_hedge_net")),
                "total_institutional_net": parse_number_zh_tw(
                    first_value(row, "三大法人買賣超股數合計", "三大法人買賣超", "total_institutional_net")
                ),
                "source": source,
                "source_url": source_url,
                "fetched_at": fetched_at_text(fetched_at),
            }
        )
    for row in normalized:
        if row["total_institutional_net"] is None:
            row["total_institutional_net"] = sum(
                value or 0.0 for value in [row["foreign_net"], row["investment_trust_net"], row["dealer_net"]]
            )
    return [row for row in normalized if row["trade_date"] and row["symbol"]]


def _net(buy: float | None, sell: float | None) -> float | None:
    if buy is None or sell is None:
        return None
    return buy - sell
