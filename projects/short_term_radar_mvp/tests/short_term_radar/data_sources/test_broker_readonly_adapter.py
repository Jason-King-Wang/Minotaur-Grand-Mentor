from __future__ import annotations

from short_term_radar.adapters.broker_api_adapter import BrokerApiAdapter


def test_broker_adapter_exposes_no_order_or_account_methods():
    forbidden = {
        "place_order",
        "update_order",
        "cancel_order",
        "account_balance",
        "positions",
        "realized_pnl",
        "unrealized_pnl",
        "settlements",
    }

    adapter_methods = set(dir(BrokerApiAdapter()))

    assert adapter_methods.isdisjoint(forbidden)
