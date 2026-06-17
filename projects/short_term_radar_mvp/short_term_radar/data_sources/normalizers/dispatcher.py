from __future__ import annotations

from typing import Any, Callable

from short_term_radar.data_sources.normalizers.corporate_actions import normalize_corporate_action_rows
from short_term_radar.data_sources.normalizers.financials import normalize_financial_statement_rows
from short_term_radar.data_sources.normalizers.insider_holding import normalize_insider_holding_rows
from short_term_radar.data_sources.normalizers.institutional_trading import normalize_institutional_trading_rows
from short_term_radar.data_sources.normalizers.margin_short import normalize_margin_short_rows
from short_term_radar.data_sources.normalizers.material_events import normalize_material_event_rows
from short_term_radar.data_sources.normalizers.monthly_revenue import normalize_monthly_revenue_rows
from short_term_radar.data_sources.normalizers.prices_daily import normalize_prices_daily_rows
from short_term_radar.data_sources.normalizers.surveillance import normalize_surveillance_rows
from short_term_radar.data_sources.normalizers.symbol_master import normalize_symbol_master_rows
from short_term_radar.data_sources.normalizers.valuation import normalize_valuation_rows

Normalizer = Callable[[list[dict[str, Any]], str, str, str, Any], list[dict[str, Any]]]

NORMALIZERS: dict[str, Normalizer] = {
    "symbol_master": normalize_symbol_master_rows,
    "prices_daily": normalize_prices_daily_rows,
    "monthly_revenue": normalize_monthly_revenue_rows,
    "institutional_trading": normalize_institutional_trading_rows,
    "margin_short": normalize_margin_short_rows,
    "surveillance": normalize_surveillance_rows,
    "corporate_actions": normalize_corporate_action_rows,
    "material_events": normalize_material_event_rows,
    "financial_statement": normalize_financial_statement_rows,
    "insider_holding": normalize_insider_holding_rows,
    "valuation": normalize_valuation_rows,
}


def normalize_rows(
    dataset: str,
    rows: list[dict[str, Any]],
    market: str,
    source: str,
    source_url: str,
    fetched_at: Any = None,
) -> list[dict[str, Any]]:
    if dataset not in NORMALIZERS:
        raise KeyError(f"No normalizer registered for dataset: {dataset}")
    return NORMALIZERS[dataset](rows, market, source, source_url, fetched_at)
