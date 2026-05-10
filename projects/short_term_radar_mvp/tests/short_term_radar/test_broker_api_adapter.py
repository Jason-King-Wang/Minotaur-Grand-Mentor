from __future__ import annotations

from types import SimpleNamespace

from short_term_radar.adapters.broker_api_adapter import BrokerApiAdapter


class FakeContracts:
    def __init__(self):
        self.TSE001 = object()

    def get(self, key, default=None):
        return getattr(self, key, default)


class FakeApi:
    def __init__(self):
        self.Contracts = SimpleNamespace(Indexs=SimpleNamespace(TSE=FakeContracts()))
        self.called = []

    def kbars(self, contract, start, end):
        self.called.append((contract, start, end))
        return {
            "ts": ["2026-04-29", "2026-04-30"],
            "Open": [100, 101],
            "High": [102, 103],
            "Low": [99, 100],
            "Close": [101, 102],
            "Volume": [1000, 1200],
            "Amount": [101000, 122400],
        }


def test_broker_adapter_fetches_index_kbars_read_only():
    api = FakeApi()
    adapter = BrokerApiAdapter()

    rows = adapter.fetch_index_daily_prices(api, "2026-04-29", "2026-04-30")

    assert adapter.read_only is True
    assert api.called
    assert rows[0]["symbol"] == "TAIEX"
    assert rows[0]["trade_date"] == "2026-04-29"
    assert rows[1]["close"] == 102
