from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any

NULL_MARKERS = {"", "-", "--", "---", "X", "x", "N/A", "NA", "null", "None", "無"}


def parse_dash_as_null(value: Any) -> Any | None:
    if value is None:
        return None
    text = str(value).strip()
    return None if text in NULL_MARKERS else value


def strip_commas(value: Any) -> str | None:
    value = parse_dash_as_null(value)
    if value is None:
        return None
    return str(value).strip().replace(",", "").replace("，", "")


def safe_float(value: Any, default: float | None = None) -> float | None:
    text = strip_commas(value)
    if text is None:
        return default
    text = text.replace("%", "").replace("％", "")
    try:
        return float(text)
    except ValueError:
        return default


def safe_int(value: Any, default: int | None = None) -> int | None:
    number = safe_float(value)
    return int(number) if number is not None else default


def parse_number_zh_tw(value: Any) -> float | None:
    text = strip_commas(value)
    if text is None:
        return None
    multiplier = 1.0
    if text.endswith("億"):
        multiplier = 100_000_000.0
        text = text[:-1]
    elif text.endswith("萬"):
        multiplier = 10_000.0
        text = text[:-1]
    number = safe_float(text)
    return number * multiplier if number is not None else None


def parse_percent(value: Any) -> float | None:
    return safe_float(value)


def roc_year_to_ad_date(year: int, month: int, day: int) -> date:
    if year < 1911:
        year += 1911
    return date(year, month, day)


def parse_tw_date(value: Any) -> date | None:
    value = parse_dash_as_null(value)
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value

    text = str(value).strip()
    if not text:
        return None
    text = text.replace("民國", "")
    text = text.replace("年", "/").replace("月", "/").replace("日", "")
    text = text.replace(".", "/").replace("-", "/")
    text = re.sub(r"\s+.*$", "", text)

    if re.fullmatch(r"\d{7}", text):
        return roc_year_to_ad_date(int(text[:3]), int(text[3:5]), int(text[5:7]))
    if re.fullmatch(r"\d{8}", text):
        year = int(text[:4])
        if year < 1911:
            return roc_year_to_ad_date(year, int(text[4:6]), int(text[6:8]))
        return date(year, int(text[4:6]), int(text[6:8]))

    parts = [part for part in text.split("/") if part]
    if len(parts) >= 3 and all(part.isdigit() for part in parts[:3]):
        year, month, day = (int(part) for part in parts[:3])
        return roc_year_to_ad_date(year, month, day)

    try:
        return datetime.fromisoformat(str(value)).date()
    except ValueError:
        return None


def parse_tw_month(value: Any) -> str | None:
    value = parse_dash_as_null(value)
    if value is None:
        return None
    text = str(value).strip().replace("年", "/").replace("月", "")
    text = text.replace("-", "/")
    if re.fullmatch(r"\d{5}", text):
        return f"{int(text[:3]) + 1911:04d}{int(text[3:5]):02d}"
    if re.fullmatch(r"\d{6}", text):
        year = int(text[:4])
        if year < 1911:
            year += 1911
        return f"{year:04d}{int(text[4:6]):02d}"
    parts = [part for part in text.split("/") if part]
    if len(parts) >= 2 and all(part.isdigit() for part in parts[:2]):
        year, month = int(parts[0]), int(parts[1])
        if year < 1911:
            year += 1911
        return f"{year:04d}{month:02d}"
    return None


def normalize_symbol(value: Any) -> str:
    value = parse_dash_as_null(value)
    if value is None:
        return ""
    text = str(value).strip().upper()
    match = re.match(r"([0-9A-Z]+)", text)
    return match.group(1) if match else text


def normalize_market(value: Any) -> str:
    text = "" if value is None else str(value).strip().upper()
    if text in {"TWSE", "TSE", "上市", "上市公司"}:
        return "TWSE"
    if text in {"TPEX", "OTC", "TPEx".upper(), "上櫃", "上櫃公司"}:
        return "TPEX"
    if "興櫃" in text or text == "EMERGING":
        return "Emerging"
    return "Unknown"


def normalize_bool_flag(value: Any) -> bool | None:
    value = parse_dash_as_null(value)
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in {"1", "true", "t", "yes", "y", "是", "有"}:
        return True
    if text in {"0", "false", "f", "no", "n", "否", "無"}:
        return False
    return None


def first_value(row: dict[str, Any], *names: str) -> Any:
    for name in names:
        if name in row and parse_dash_as_null(row.get(name)) is not None:
            return row.get(name)
    return None


def iso_date(value: Any) -> str | None:
    parsed = parse_tw_date(value)
    return parsed.isoformat() if parsed else None


def fetched_at_text(fetched_at: Any) -> str:
    if isinstance(fetched_at, datetime):
        return fetched_at.isoformat(timespec="seconds")
    if fetched_at:
        return str(fetched_at)
    return datetime.now().isoformat(timespec="seconds")


def next_month_day_10(revenue_month: str | None) -> str | None:
    if not revenue_month:
        return None
    year, month = int(revenue_month[:4]), int(revenue_month[4:6])
    if month == 12:
        year += 1
        month = 1
    else:
        month += 1
    return date(year, month, 10).isoformat()
