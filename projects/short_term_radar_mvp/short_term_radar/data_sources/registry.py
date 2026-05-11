from __future__ import annotations

from dataclasses import dataclass

from short_term_radar.data_sources.base import CollectorPlan
from short_term_radar.data_sources.quality import DATASET_SCHEMAS, PRIMARY_KEYS


@dataclass(frozen=True)
class DatasetSpec:
    name: str
    processed_table: str
    priority: str
    markets: tuple[str, ...]
    sources: tuple[str, ...]
    description: str

    @property
    def schema(self) -> list[str]:
        return DATASET_SCHEMAS[self.processed_table]

    @property
    def primary_key(self) -> list[str]:
        return PRIMARY_KEYS[self.processed_table]


DATASET_REGISTRY: dict[str, DatasetSpec] = {
    "symbol_master": DatasetSpec(
        "symbol_master",
        "symbol_master",
        "P0",
        ("TWSE", "TPEX"),
        ("twse", "tpex"),
        "Company universe, industry, capital, listing metadata.",
    ),
    "prices_daily": DatasetSpec(
        "prices_daily",
        "prices_daily",
        "P0",
        ("TWSE", "TPEX"),
        ("twse", "tpex", "broker_api"),
        "Daily OHLCV incremental source.",
    ),
    "monthly_revenue": DatasetSpec(
        "monthly_revenue",
        "monthly_revenue",
        "P0",
        ("TWSE", "TPEX"),
        ("twse", "tpex"),
        "Monthly revenue with announce-date gating.",
    ),
    "institutional_trading": DatasetSpec(
        "institutional_trading",
        "institutional_trading_daily",
        "P0",
        ("TWSE", "TPEX"),
        ("twse", "tpex", "twse_eshop"),
        "Three major institutional investors daily buy/sell.",
    ),
    "margin_short": DatasetSpec(
        "margin_short",
        "margin_short_daily",
        "P0",
        ("TWSE", "TPEX"),
        ("twse", "tpex", "twse_eshop", "broker_api"),
        "Margin, short and securities borrowing risk data.",
    ),
    "surveillance": DatasetSpec(
        "surveillance",
        "surveillance_daily",
        "P0",
        ("TWSE", "TPEX"),
        ("twse_eshop", "tpex", "broker_api"),
        "Attention and disposition stocks.",
    ),
    "corporate_actions": DatasetSpec(
        "corporate_actions",
        "corporate_actions",
        "P0",
        ("TWSE", "TPEX"),
        ("twse", "tpex"),
        "Ex-right, ex-dividend and capital events.",
    ),
    "material_events": DatasetSpec(
        "material_events",
        "material_events",
        "P0",
        ("TWSE", "TPEX"),
        ("twse", "tpex"),
        "Material event announcements and catalyst classification.",
    ),
    "financial_statement": DatasetSpec(
        "financial_statement",
        "financial_statement_quarterly",
        "P1",
        ("TWSE", "TPEX"),
        ("twse", "tpex"),
        "Quarterly financial statements.",
    ),
    "insider_holding": DatasetSpec(
        "insider_holding",
        "insider_holding_monthly",
        "P1",
        ("TWSE", "TPEX"),
        ("twse", "tpex"),
        "Insider holdings and pledge risk.",
    ),
    "valuation": DatasetSpec(
        "valuation",
        "valuation_daily",
        "P1",
        ("TWSE", "TPEX"),
        ("twse", "tpex"),
        "PE, PB, dividend yield and market-cap proxy.",
    ),
}


ALIASES = {
    "all": "all",
    "institutional_trading_daily": "institutional_trading",
    "margin_short_daily": "margin_short",
    "financial_statement_quarterly": "financial_statement",
    "valuation_daily": "valuation",
}


def resolve_dataset_names(dataset: str) -> list[str]:
    normalized = ALIASES.get(dataset, dataset)
    if normalized == "all":
        return list(DATASET_REGISTRY)
    if normalized not in DATASET_REGISTRY:
        raise KeyError(f"Unknown dataset: {dataset}")
    return [normalized]


def build_collect_plan(config: dict, dataset: str, market: str = "all") -> list[CollectorPlan]:
    plans: list[CollectorPlan] = []
    for name in resolve_dataset_names(dataset):
        spec = DATASET_REGISTRY[name]
        markets = spec.markets if market.lower() == "all" else (market.upper(),)
        for source in spec.sources:
            source_cfg = (config.get("sources") or {}).get(source, {})
            enabled = bool(source_cfg.get("enabled", False))
            for item_market in markets:
                if not _source_supports_market(source, item_market):
                    continue
                dataset_cfg = _dataset_config(source_cfg, name, spec.processed_table, source)
                landing_url = (dataset_cfg or {}).get("landing_url") or (dataset_cfg or {}).get("url")
                download_url = (dataset_cfg or {}).get("download_url")
                plans.append(
                    CollectorPlan(
                        dataset=name,
                        market=item_market,
                        source=source,
                        url=download_url,
                        enabled=enabled,
                        note=None if enabled else "source disabled or registry-only",
                        landing_url=landing_url,
                        download_url=download_url,
                    )
                )
    return plans


def _dataset_config(source_cfg: dict, name: str, processed_table: str, source: str) -> dict:
    datasets = source_cfg.get("datasets") or {}
    if name == "surveillance" and source == "tpex":
        return _merged_endpoint_config(datasets, ("attention", "disposition"))
    return datasets.get(name) or datasets.get(processed_table) or {}


def _merged_endpoint_config(datasets: dict, names: tuple[str, ...]) -> dict:
    landing_urls = [str(datasets[name].get("landing_url")) for name in names if datasets.get(name, {}).get("landing_url")]
    download_urls = [str(datasets[name].get("download_url")) for name in names if datasets.get(name, {}).get("download_url")]
    return {
        "landing_url": " | ".join(landing_urls),
        "download_url": " | ".join(download_urls),
    }


def _source_supports_market(source: str, market: str) -> bool:
    if source == "twse":
        return market == "TWSE"
    if source == "tpex":
        return market == "TPEX"
    if source == "twse_eshop":
        return market == "TWSE"
    return True
