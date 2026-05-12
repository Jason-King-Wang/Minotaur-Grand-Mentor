from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from short_term_radar.data_sources.base import FetchResult


MOPS_MONTHLY_REVENUE_BASE = "https://mopsov.twse.com.tw/nas/t21"


@dataclass(frozen=True)
class MonthlyRevenueUrl:
    market: str
    revenue_month: str
    company_type: str
    url: str


class MopsMonthlyRevenueFetcher:
    def __init__(self, config: dict[str, Any] | None = None):
        fetch_cfg = (config or {}).get("fetch") or {}
        self.user_agent = fetch_cfg.get("user_agent", "short-term-radar-mvp/0.2")
        self.timeout = int(fetch_cfg.get("timeout_seconds", 30))

    def build_url(self, market: str, revenue_month: str, company_type: str = "local") -> MonthlyRevenueUrl:
        normalized_market = market.upper()
        normalized_month = normalize_revenue_month(revenue_month)
        roc_year = int(normalized_month[:4]) - 1911
        month = int(normalized_month[4:6])
        market_code = "sii" if normalized_market == "TWSE" else "otc"
        type_code = "1" if company_type == "foreign" else "0"
        url = f"{MOPS_MONTHLY_REVENUE_BASE}/{market_code}/t21sc03_{roc_year}_{month}_{type_code}.html"
        return MonthlyRevenueUrl(normalized_market, normalized_month, company_type, url)

    def fetch_month(self, market: str, revenue_month: str, company_type: str = "local") -> FetchResult:
        request_info = self.build_url(market, revenue_month, company_type)
        try:
            request = Request(request_info.url, headers={"User-Agent": self.user_agent})
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read()
                encoding = response.headers.get_content_charset()
                text = _decode_mops(raw, encoding)
        except URLError as exc:
            return FetchResult("mops", "monthly_revenue", request_info.url, degraded=True, message=str(exc))

        rows = parse_mops_monthly_revenue_html(
            text,
            request_info.market,
            request_info.revenue_month,
            request_info.company_type,
        )
        return FetchResult("mops", "monthly_revenue", request_info.url, rows=rows, raw_text=text)


def iter_revenue_months(start_month: str, end_month: str) -> list[str]:
    start = normalize_revenue_month(start_month)
    end = normalize_revenue_month(end_month)
    year = int(start[:4])
    month = int(start[4:6])
    end_pair = (int(end[:4]), int(end[4:6]))
    months: list[str] = []
    while (year, month) <= end_pair:
        months.append(f"{year:04d}{month:02d}")
        month += 1
        if month == 13:
            year += 1
            month = 1
    return months


def normalize_revenue_month(value: str) -> str:
    compact = str(value).strip().replace("-", "").replace("/", "")
    if len(compact) == 5 and compact[:3].isdigit():
        return f"{int(compact[:3]) + 1911:04d}{int(compact[3:]):02d}"
    if len(compact) >= 6:
        return f"{int(compact[:4]):04d}{int(compact[4:6]):02d}"
    raise ValueError(f"Bad revenue month: {value}")


def parse_mops_monthly_revenue_html(
    html_text: str,
    market: str,
    revenue_month: str,
    company_type: str,
) -> list[dict[str, Any]]:
    parser = _TableParser()
    parser.feed(html_text)
    rows: list[dict[str, Any]] = []
    for table in parser.tables:
        if not table:
            continue
        header_index = _find_header_index(table)
        if header_index is None:
            continue
        headers = table[header_index]
        for raw_row in table[header_index + 1 :]:
            if len(raw_row) < 3:
                continue
            row = _row_from_cells(headers, raw_row, revenue_month)
            if row.get("symbol") and str(row["symbol"]).isdigit():
                row["market"] = market
                row["company_type"] = company_type
                row["raw_market_section"] = f"{market}_{company_type}"
                row["announce_date_inferred"] = True
                rows.append(row)
    return rows


def _decode_mops(raw: bytes, encoding: str | None) -> str:
    candidates = [encoding, "big5", "cp950", "utf-8"]
    for candidate in [item for item in candidates if item]:
        try:
            return raw.decode(candidate)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def _find_header_index(table: list[list[str]]) -> int | None:
    for index, row in enumerate(table):
        joined = " ".join(row).lower()
        if "symbol" in joined and "revenue" in joined:
            return index
        if "公司代號" in joined and ("營業收入" in joined or "營收" in joined):
            return index
    return 0 if len(table) > 1 else None


def _row_from_cells(headers: list[str], cells: list[str], revenue_month: str) -> dict[str, Any]:
    by_header = {header.strip().lower(): cells[index].strip() for index, header in enumerate(headers) if index < len(cells)}
    if any(key in by_header for key in ["symbol", "revenue_current"]):
        row = {
            "revenue_month": by_header.get("revenue_month") or revenue_month,
            "symbol": by_header.get("symbol"),
            "name": by_header.get("name"),
            "industry": by_header.get("industry"),
            "revenue_current": by_header.get("revenue_current"),
            "revenue_previous_month": by_header.get("revenue_previous_month"),
            "revenue_last_year_same_month": by_header.get("revenue_last_year_same_month"),
            "revenue_mom_pct": by_header.get("revenue_mom_pct"),
            "revenue_yoy_pct": by_header.get("revenue_yoy_pct"),
            "cumulative_revenue_current": by_header.get("cumulative_revenue_current"),
            "cumulative_revenue_last_year": by_header.get("cumulative_revenue_last_year"),
            "cumulative_yoy_pct": by_header.get("cumulative_yoy_pct"),
            "note": by_header.get("note"),
        }
        return row

    values = list(cells)
    if _looks_like_month(values[0]):
        ordered = values
    else:
        ordered = [revenue_month, *values]
    ordered.extend([""] * max(0, 13 - len(ordered)))
    keys = [
        "revenue_month",
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
    ]
    return dict(zip(keys, ordered[: len(keys)]))


def _looks_like_month(value: str) -> bool:
    compact = str(value).strip().replace("/", "").replace("-", "")
    return len(compact) in {5, 6} and compact.isdigit()


class _TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables: list[list[list[str]]] = []
        self._table: list[list[str]] | None = None
        self._row: list[str] | None = None
        self._cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag == "table":
            self._table = []
        elif tag == "tr" and self._table is not None:
            self._row = []
        elif tag in {"td", "th"} and self._row is not None:
            self._cell = []

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            self._cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"td", "th"} and self._row is not None and self._cell is not None:
            self._row.append(" ".join(part.strip() for part in self._cell if part.strip()))
            self._cell = None
        elif tag == "tr" and self._table is not None and self._row is not None:
            if any(cell for cell in self._row):
                self._table.append(self._row)
            self._row = None
        elif tag == "table" and self._table is not None:
            self.tables.append(self._table)
            self._table = None
