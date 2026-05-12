from __future__ import annotations

import pytest

from short_term_radar.data_sources.fetchers.broker_readonly_fetcher import BrokerReadonlyFetcher
from short_term_radar.data_sources.sources.broker_readonly import BrokerReadonlySource


class _Contract:
    def __init__(self, code: str, name: str, exchange: str, margin_balance: int, short_balance: int):
        self.code = code
        self.name = name
        self.exchange = exchange
        self.margin_trading_balance = margin_balance
        self.short_selling_balance = short_balance


class _Stocks:
    TSE = {"2330": _Contract("2330", "台積電", "TSE", 1200, 300)}
    OTC = {"6488": _Contract("6488", "環球晶", "OTC", 800, 120)}


class _Contracts:
    Stocks = _Stocks()


class _FakeApi:
    Contracts = _Contracts()

    def notice(self):
        return [
            {
                "code": "2330",
                "name": "台積電",
                "date": "2026-05-11",
                "market": "TWSE",
                "reason": "注意交易資訊",
                "close": "1000",
            }
        ]

    def punish(self):
        return [
            {
                "code": "6488",
                "name": "環球晶",
                "announce_date": "2026-05-11",
                "market": "TPEX",
                "start_date": "2026-05-10",
                "end_date": "2026-05-20",
                "reason": "處置說明",
                "measure": "撮合間隔調整",
            }
        ]

    def credit_enquires(self, contracts):
        return [
            {
                "code": getattr(contract, "code", ""),
                "margin_trading_balance": getattr(contract, "margin_trading_balance", None),
                "short_selling_balance": getattr(contract, "short_selling_balance", None),
            }
            for contract in contracts
        ]

    def short_stock_sources(self, contracts):
        return [{"code": getattr(contract, "code", ""), "quantity": 5000} for contract in contracts]

    def place_order(self, *_args, **_kwargs):  # pragma: no cover - must never be called
        raise AssertionError("read-only source must not call place_order")


def test_broker_readonly_source_normalizes_notice_and_punish_rows():
    rows = BrokerReadonlySource(api=_FakeApi()).collect_surveillance_daily("2026-05-11")

    notice = next(row for row in rows if row["symbol"] == "2330")
    punish = next(row for row in rows if row["symbol"] == "6488")

    assert notice["attention_flag"] is True
    assert notice["disposition_flag"] is False
    assert notice["attention_reason"] == "注意交易資訊"
    assert punish["attention_flag"] is False
    assert punish["disposition_flag"] is True
    assert punish["disposition_start"] == "2026-05-10"
    assert punish["disposition_end"] == "2026-05-20"


def test_broker_readonly_source_normalizes_margin_short_rows():
    rows = BrokerReadonlySource(api=_FakeApi()).collect_margin_short_daily(
        ["2330", "6488"],
        "2026-05-11",
    )

    twse = next(row for row in rows if row["symbol"] == "2330")
    tpex = next(row for row in rows if row["symbol"] == "6488")

    assert twse["market"] == "TWSE"
    assert twse["margin_balance"] == 1200
    assert twse["short_balance"] == 300
    assert twse["sbl_balance"] == 5000
    assert tpex["market"] == "TPEX"
    assert tpex["margin_balance"] == 800


def test_broker_readonly_source_requires_external_api_object():
    with pytest.raises(ValueError, match="externally managed"):
        BrokerReadonlySource().collect_surveillance_daily("2026-05-11")


def test_strict_api_surface_can_still_reject_forbidden_methods():
    fetcher = BrokerReadonlyFetcher({"strict_api_surface": True})

    with pytest.raises(AttributeError, match="forbidden"):
        fetcher.fetch_surveillance_daily(_FakeApi(), "2026-05-11")
