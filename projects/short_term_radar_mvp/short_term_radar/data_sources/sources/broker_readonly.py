from __future__ import annotations

ALLOWED_READONLY_METHODS = {
    "kbars",
    "snapshots",
    "ticks",
    "daily_quotes",
    "notice",
    "punish",
    "credit_enquires",
    "short_stock_sources",
    "scanners",
}

FORBIDDEN_ORDER_OR_ACCOUNT_METHODS = {
    "place_order",
    "update_order",
    "cancel_order",
    "account_balance",
    "positions",
    "realized_pnl",
    "unrealized_pnl",
    "settlements",
}
