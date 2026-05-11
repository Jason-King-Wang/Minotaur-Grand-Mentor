from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from short_term_radar.data_sources.normalizers.common import parse_tw_date


DATASET_SCHEMAS: dict[str, list[str]] = {
    "symbol_master": [
        "symbol",
        "name",
        "short_name",
        "market",
        "industry",
        "listing_date",
        "established_date",
        "paid_in_capital",
        "issued_shares",
        "par_value",
        "foreign_registration_country",
        "is_ky",
        "is_etf",
        "is_warrant",
        "is_etn",
        "is_tdr",
        "is_common_stock",
        "is_full_delivery",
        "is_attention",
        "is_disposition",
        "source",
        "source_url",
        "fetched_at",
    ],
    "prices_daily": [
        "trade_date",
        "market",
        "symbol",
        "name",
        "open",
        "high",
        "low",
        "close",
        "change",
        "volume",
        "amount",
        "transactions",
        "issued_shares",
        "next_limit_up",
        "next_limit_down",
        "source",
        "source_url",
        "fetched_at",
    ],
    "monthly_revenue": [
        "revenue_month",
        "announce_date",
        "market",
        "symbol",
        "name",
        "industry",
        "revenue_current",
        "revenue_previous_month",
        "revenue_last_year_same_month",
        "revenue_mom_pct",
        "revenue_yoy_pct",
        "cumulative_revenue_current",
        "cumulative_revenue_last_year",
        "cumulative_yoy_pct",
        "note",
        "announce_date_inferred",
        "company_type",
        "raw_market_section",
        "source",
        "source_url",
        "fetched_at",
    ],
    "institutional_trading_daily": [
        "trade_date",
        "market",
        "symbol",
        "name",
        "foreign_buy",
        "foreign_sell",
        "foreign_net",
        "investment_trust_buy",
        "investment_trust_sell",
        "investment_trust_net",
        "dealer_buy",
        "dealer_sell",
        "dealer_net",
        "dealer_self_buy",
        "dealer_self_sell",
        "dealer_self_net",
        "dealer_hedge_buy",
        "dealer_hedge_sell",
        "dealer_hedge_net",
        "total_institutional_net",
        "source",
        "source_url",
        "fetched_at",
    ],
    "margin_short_daily": [
        "trade_date",
        "market",
        "symbol",
        "name",
        "margin_buy",
        "margin_sell",
        "margin_redeem",
        "margin_balance",
        "margin_balance_prev",
        "short_sell",
        "short_cover",
        "short_redeem",
        "short_balance",
        "short_balance_prev",
        "short_margin_ratio",
        "sbl_short_sell_volume",
        "sbl_balance",
        "sbl_short_sell_balance",
        "margin_limit_code",
        "short_limit_code",
        "source",
        "source_url",
        "fetched_at",
    ],
    "surveillance_daily": [
        "trade_date",
        "market",
        "symbol",
        "name",
        "attention_flag",
        "attention_reason",
        "attention_close",
        "attention_pe",
        "disposition_flag",
        "disposition_start",
        "disposition_end",
        "disposition_condition",
        "disposition_reason",
        "disposition_measure",
        "attention_count_recent",
        "source",
        "source_url",
        "fetched_at",
    ],
    "corporate_actions": [
        "action_date",
        "market",
        "symbol",
        "name",
        "action_type",
        "cash_dividend",
        "stock_dividend_ratio",
        "capital_increase_ratio",
        "subscription_price",
        "reference_price",
        "previous_close",
        "right_value",
        "interest_value",
        "source",
        "source_url",
        "fetched_at",
    ],
    "material_events": [
        "announce_date",
        "announce_time",
        "market",
        "symbol",
        "name",
        "title",
        "rule_clause",
        "event_date",
        "description",
        "event_type",
        "catalyst_score",
        "risk_score",
        "source",
        "source_url",
        "fetched_at",
    ],
    "financial_statement_quarterly": [
        "year",
        "quarter",
        "market",
        "symbol",
        "name",
        "industry_type",
        "announce_date",
        "revenue",
        "cost",
        "gross_profit",
        "gross_margin",
        "operating_expense",
        "operating_profit",
        "operating_margin",
        "pretax_income",
        "net_income",
        "eps",
        "source",
        "source_url",
        "fetched_at",
    ],
    "insider_holding_monthly": [
        "data_month",
        "market",
        "symbol",
        "name",
        "title",
        "insider_name",
        "shares_at_election",
        "current_holding",
        "pledged_shares",
        "pledge_ratio",
        "related_party_holding",
        "related_party_pledged_shares",
        "related_party_pledge_ratio",
        "source",
        "source_url",
        "fetched_at",
    ],
    "valuation_daily": [
        "trade_date",
        "market",
        "symbol",
        "name",
        "close",
        "pe",
        "pb",
        "dividend_yield",
        "dividend_per_share",
        "financial_year_quarter",
        "market_cap",
        "source",
        "source_url",
        "fetched_at",
    ],
}

PRIMARY_KEYS: dict[str, list[str]] = {
    "symbol_master": ["market", "symbol"],
    "prices_daily": ["trade_date", "market", "symbol"],
    "monthly_revenue": ["revenue_month", "market", "symbol"],
    "institutional_trading_daily": ["trade_date", "market", "symbol"],
    "margin_short_daily": ["trade_date", "market", "symbol"],
    "surveillance_daily": ["trade_date", "market", "symbol", "attention_flag", "disposition_flag"],
    "corporate_actions": ["action_date", "market", "symbol", "action_type"],
    "material_events": ["announce_date", "announce_time", "market", "symbol", "title"],
    "financial_statement_quarterly": ["year", "quarter", "market", "symbol"],
    "insider_holding_monthly": ["data_month", "market", "symbol", "title", "insider_name"],
    "valuation_daily": ["trade_date", "market", "symbol"],
}

DATE_COLUMNS = {
    "trade_date",
    "announce_date",
    "action_date",
    "event_date",
    "listing_date",
    "established_date",
    "disposition_start",
    "disposition_end",
}

VALID_MARKETS = {"TWSE", "TPEX", "Emerging", "Unknown", "INDEX"}


@dataclass(frozen=True)
class QualityIssue:
    dataset: str
    check: str
    severity: str
    message: str


@dataclass(frozen=True)
class QualityReport:
    dataset: str
    row_count: int
    issues: list[QualityIssue]

    @property
    def ok(self) -> bool:
        return not any(issue.severity == "error" for issue in self.issues)


def validate_rows(
    dataset: str,
    rows: list[dict[str, Any]],
    today: date | None = None,
    allow_future_dates: bool = False,
) -> QualityReport:
    if dataset not in DATASET_SCHEMAS:
        raise KeyError(f"Unknown processed table: {dataset}")

    today = today or date.today()
    schema = DATASET_SCHEMAS[dataset]
    pk = PRIMARY_KEYS[dataset]
    issues: list[QualityIssue] = []

    missing_columns = [column for column in schema if rows and column not in rows[0]]
    if missing_columns:
        issues.append(
            QualityIssue(dataset, "schema columns exist", "error", f"Missing columns: {missing_columns}")
        )

    seen: set[tuple[Any, ...]] = set()
    duplicate_count = 0
    for index, row in enumerate(rows):
        key = tuple(row.get(column) for column in pk)
        if key in seen:
            duplicate_count += 1
        else:
            seen.add(key)

        if "symbol" in schema and not row.get("symbol"):
            issues.append(QualityIssue(dataset, "symbol not null", "error", f"Row {index} has blank symbol"))
        if "market" in schema and row.get("market") not in VALID_MARKETS:
            issues.append(
                QualityIssue(dataset, "market valid", "error", f"Row {index} has invalid market {row.get('market')}")
            )
        if "source" in schema and not row.get("source"):
            issues.append(QualityIssue(dataset, "source not null", "error", f"Row {index} has blank source"))
        if "source_url" in schema and not row.get("source_url"):
            issues.append(QualityIssue(dataset, "source_url not null", "warning", f"Row {index} has blank URL"))
        if "fetched_at" in schema and not row.get("fetched_at"):
            issues.append(QualityIssue(dataset, "fetched_at not null", "error", f"Row {index} has blank fetched_at"))

        for column in DATE_COLUMNS.intersection(row):
            parsed = parse_tw_date(row.get(column))
            if row.get(column) and parsed is None:
                issues.append(QualityIssue(dataset, "date parse success", "error", f"Row {index} bad {column}"))
            if parsed and parsed > today and not allow_future_dates:
                issues.append(
                    QualityIssue(dataset, "no unexpected future date", "error", f"Row {index} future {column}")
                )

    if duplicate_count:
        issues.append(
            QualityIssue(
                dataset,
                "primary key uniqueness",
                "error",
                f"Found {duplicate_count} duplicate primary-key rows for {pk}",
            )
        )

    if not rows:
        issues.append(QualityIssue(dataset, "row count", "warning", "No processed rows available"))

    return QualityReport(dataset, len(rows), issues)
