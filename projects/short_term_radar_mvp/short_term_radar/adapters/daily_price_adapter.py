from __future__ import annotations

from pathlib import Path
from typing import Any

from short_term_radar.utils.io import read_csv_records
from short_term_radar.utils.math_utils import safe_float


COLUMN_ALIASES = {
    "symbol": ["symbol", "stock_id", "code", "ticker", "證券代號"],
    "name": ["name", "stock_name", "證券名稱", "公司名稱"],
    "industry": ["industry", "sector", "theme_group", "產業別"],
    "trade_date": ["trade_date", "date", "交易日期", "年月日"],
    "open": ["open", "開盤價"],
    "high": ["high", "最高價"],
    "low": ["low", "最低價"],
    "close": ["close", "收盤價"],
    "volume": ["volume", "成交股數", "成交量"],
    "amount": ["amount", "value", "成交金額", "成交值"],
    "market": ["market", "市場別"],
}


class DailyPriceAdapter:
    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.symbol_meta: dict[str, dict[str, str | None]] = {}

    def load(self) -> dict[str, list[dict[str, Any]]]:
        data_path = Path(self.config["data"]["daily_price_path"])
        if not data_path.exists():
            return {}

        self.symbol_meta = self._load_symbol_meta(data_path)
        files = self._data_files(data_path)
        records: list[dict[str, Any]] = []
        for file_path in files:
            records.extend(self._read_file(file_path))

        by_symbol: dict[str, list[dict[str, Any]]] = {}
        for record in records:
            symbol = record.get("symbol")
            trade_date = record.get("trade_date")
            if not symbol or not trade_date or record.get("close") is None:
                continue
            by_symbol.setdefault(symbol, []).append(record)

        for rows in by_symbol.values():
            rows.sort(key=lambda row: row["trade_date"])
        return by_symbol

    def _data_files(self, data_path: Path) -> list[Path]:
        if data_path.is_file():
            return [data_path]
        data_root = data_path / "daily_ohlcv" if (data_path / "daily_ohlcv").exists() else data_path
        return sorted(
            [
                *data_root.rglob("*.csv"),
                *data_root.rglob("*.parquet"),
            ]
        )

    def _load_symbol_meta(self, data_path: Path) -> dict[str, dict[str, str | None]]:
        root = data_path if data_path.is_dir() else data_path.parent
        candidates = [
            root / "reference" / "symbol_master.csv",
            root / "reference" / "symbol_master.parquet",
            root.parent / "reference" / "symbol_master.csv",
            root.parent / "reference" / "symbol_master.parquet",
        ]
        for candidate in candidates:
            if not candidate.exists():
                continue
            rows = self._read_table(candidate)
            meta: dict[str, dict[str, str | None]] = {}
            for row in rows:
                symbol = str(row.get("stock_id") or row.get("symbol") or "").strip()
                if symbol:
                    meta[symbol] = {
                        "name": str(row.get("stock_name") or row.get("name") or "").strip() or None,
                        "industry": str(row.get("industry") or row.get("sector") or "").strip() or None,
                    }
            return meta
        return {}

    def available_trade_dates(self, by_symbol: dict[str, list[dict[str, Any]]]) -> list[str]:
        dates = set()
        for rows in by_symbol.values():
            dates.update(row["trade_date"] for row in rows)
        return sorted(dates)

    def _read_file(self, file_path: Path) -> list[dict[str, Any]]:
        raw_rows = self._read_table(file_path)
        if not raw_rows:
            return []

        sample = raw_rows[0]
        mapping = self._build_mapping(sample)
        return [self._normalize_row(row, mapping) for row in raw_rows]

    def _read_table(self, file_path: Path) -> list[dict[str, Any]]:
        if file_path.suffix.lower() == ".csv":
            return read_csv_records(file_path)
        if file_path.suffix.lower() == ".parquet":
            try:
                import pandas as pd
            except ImportError as error:
                raise RuntimeError(
                    "Reading parquet daily data requires pandas + pyarrow. "
                    "On this machine, run with `py -3.14 -m ...`."
                ) from error
            return pd.read_parquet(file_path).to_dict("records")
        return []

    def _build_mapping(self, sample: dict[str, str]) -> dict[str, str | None]:
        columns = {column.strip(): column for column in sample.keys()}
        lower_columns = {column.lower(): column for column in columns}
        explicit = {
            "symbol": self.config["data"].get("symbol_col"),
            "trade_date": self.config["data"].get("date_col"),
        }

        mapping: dict[str, str | None] = {}
        for target, aliases in COLUMN_ALIASES.items():
            if explicit.get(target) in columns:
                mapping[target] = columns[explicit[target]]
                continue
            found = None
            for alias in aliases:
                found = columns.get(alias) or lower_columns.get(alias.lower())
                if found:
                    break
            mapping[target] = found
        return mapping

    def _normalize_row(self, row: dict[str, str], mapping: dict[str, str | None]) -> dict[str, Any]:
        def text(name: str) -> str | None:
            column = mapping.get(name)
            value = row.get(column, "") if column else ""
            return str(value).strip() or None

        volume = safe_float(text("volume"), 0.0)
        close = safe_float(text("close"))
        amount = safe_float(text("amount"))
        if amount is None and close is not None and volume is not None:
            amount = close * volume

        symbol = text("symbol")
        meta = self.symbol_meta.get(symbol or "", {})
        trade_date = text("trade_date")
        if trade_date and len(trade_date) >= 10:
            trade_date = trade_date[:10]

        return {
            "symbol": symbol,
            "name": text("name") or meta.get("name"),
            "industry": text("industry") or meta.get("industry"),
            "trade_date": trade_date,
            "open": safe_float(text("open")),
            "high": safe_float(text("high")),
            "low": safe_float(text("low")),
            "close": close,
            "volume": volume,
            "amount": amount,
            "market": text("market"),
        }
