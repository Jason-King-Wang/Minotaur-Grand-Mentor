from __future__ import annotations

from short_term_radar.adapters.broker_api_adapter import BrokerApiAdapter


def test_broker_adapter_exposes_no_order_methods():
    adapter = BrokerApiAdapter()

    for forbidden in ["place_order", "update_order", "cancel_order", "buy", "sell", "order", "trade", "position", "account", "balance", "settlement"]:
        assert not hasattr(adapter, forbidden)
