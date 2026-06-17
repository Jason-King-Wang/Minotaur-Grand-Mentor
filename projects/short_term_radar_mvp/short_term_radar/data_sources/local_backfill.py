from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from short_term_radar.data_sources.fetchers.local_file_fetcher import LocalFileFetcher
from short_term_radar.data_sources.normalizers.symbol_master import normalize_symbol_master_rows
from short_term_radar.data_sources.storage import processed_path


def existing_daily_price_root(config: dict[str, Any]) -> Path | None:
    raw_path = config.get("existing_daily_price_path") or config.get("data", {}).get("daily_price_path")
    if not raw_path:
        return None
    path = Path(raw_path)
    return path if path.exists() else None


def backfill_symbol_master_from_existing(config: dict[str, Any]) -> tuple[Path, int]:
    root = existing_daily_price_root(config)
    if root is None:
        raise FileNotFoundError("existing_daily_price_path is not configured or does not exist")
    source_file = root / "reference" / "symbol_master.csv"
    if not source_file.exists():
        raise FileNotFoundError(f"symbol master not found: {source_file}")

    rows = LocalFileFetcher().fetch_csv(source_file, "local_existing_cache", "symbol_master").rows
    normalized = normalize_symbol_master_rows(
        rows,
        "Unknown",
        "local_existing_cache",
        str(source_file),
        datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )
    return _write_dataframe(config, "symbol_master", normalized), len(normalized)


def backfill_prices_daily_from_existing(
    config: dict[str, Any],
    start: str | None = None,
    end: str | None = None,
    market: str = "all",
) -> tuple[Path, int]:
    root = existing_daily_price_root(config)
    if root is None:
        raise FileNotFoundError("existing_daily_price_path is not configured or does not exist")

    import pandas as pd

    frames = []
    markets = ["TWSE", "TPEX"] if market.lower() == "all" else [market.upper()]
    symbol_lookup = _load_symbol_lookup(root)
    fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for item_market in markets:
        market_dir = root / "daily_ohlcv" / item_market
        if not market_dir.exists():
            continue
        for parquet_path in market_dir.glob("*.parquet"):
            df = pd.read_parquet(parquet_path)
            if df.empty:
                continue
            df = df.rename(
                columns={
                    "date": "trade_date",
                    "stock_id": "symbol",
                    "stock_name": "name",
                    "trades": "transactions",
                }
            )
            df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.date.astype(str)
            if start:
                df = df[df["trade_date"] >= start]
            if end:
                df = df[df["trade_date"] <= end]
            if df.empty:
                continue
            df["symbol"] = df["symbol"].astype(str)
            df["market"] = df.get("market", item_market)
            df["name"] = df["symbol"].map(lambda symbol: symbol_lookup.get(symbol, {}).get("name"))
            df["source_url"] = str(parquet_path)
            df["fetched_at"] = fetched_at
            if "downloaded_at" in df.columns:
                df["fetched_at"] = df["downloaded_at"].astype(str)
            for column in ["change", "issued_shares", "next_limit_up", "next_limit_down"]:
                if column not in df.columns:
                    df[column] = None
            if "amount" not in df.columns:
                df["amount"] = None
            if "transactions" not in df.columns:
                df["transactions"] = None
            df["source"] = df.get("source", "local_existing_cache")
            frames.append(
                df[
                    [
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
                    ]
                ]
            )

    if not frames:
        return _write_dataframe(config, "prices_daily", []), 0
    combined = pd.concat(frames, ignore_index=True)
    combined = combined.drop_duplicates(subset=["trade_date", "market", "symbol"]).sort_values(
        ["trade_date", "market", "symbol"]
    )
    output = processed_path(config, "prices_daily")
    output.parent.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(output, index=False)
    return output, len(combined)


def _load_symbol_lookup(root: Path) -> dict[str, dict[str, str]]:
    source_file = root / "reference" / "symbol_master.csv"
    if not source_file.exists():
        return {}
    rows = LocalFileFetcher().fetch_csv(source_file, "local_existing_cache", "symbol_master").rows
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        symbol = str(row.get("stock_id") or row.get("symbol") or "")
        if symbol:
            result[symbol] = {"name": row.get("stock_name") or row.get("name") or ""}
    return result


def _write_dataframe(config: dict[str, Any], dataset: str, rows: list[dict[str, Any]]) -> Path:
    output = processed_path(config, dataset)
    output.parent.mkdir(parents=True, exist_ok=True)
    import pandas as pd

    pd.DataFrame(rows).to_parquet(output, index=False)
    return output
