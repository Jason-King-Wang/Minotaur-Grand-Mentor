from __future__ import annotations

from pathlib import Path

from short_term_radar.config import load_config
from short_term_radar.data_sources.config import load_data_source_config
from short_term_radar.data_sources.registry import build_collect_plan


def test_local_example_has_no_absolute_user_path():
    text = Path("configs/short_term_radar/local.yaml.example").read_text(encoding="utf-8")

    assert "C:/Users/User" not in text
    assert "C:\\Users\\User" not in text


def test_config_expands_tw_radar_data_root(monkeypatch):
    monkeypatch.setenv("TW_RADAR_DATA_ROOT", "X:/radar_data")

    config = load_data_source_config("configs/short_term_radar/local.yaml.example")

    assert config["data_root"] == "X:/radar_data"


def test_config_expands_tw_equities_data_path(monkeypatch):
    monkeypatch.setenv("TW_EQUITIES_DATA_PATH", "X:/tw_equities")

    config = load_config("configs/short_term_radar/default.yaml")

    assert config["data"]["daily_price_path"] == "X:/tw_equities"


def test_data_gov_sources_split_landing_and_download_urls():
    config = load_data_source_config("configs/short_term_radar/data_sources.example.yaml")
    monthly_revenue = config["sources"]["twse"]["datasets"]["monthly_revenue"]

    assert monthly_revenue["landing_url"] == "https://data.gov.tw/dataset/18420"
    assert monthly_revenue["download_url"] == ""
    assert monthly_revenue["api_url"] == "https://openapi.twse.com.tw/v1/opendata/t187ap05_L"


def test_collect_plan_does_not_treat_landing_page_as_download_url():
    config = load_data_source_config("configs/short_term_radar/data_sources.example.yaml")
    plans = build_collect_plan(config, "surveillance", "TPEX")
    tpex_plan = next(plan for plan in plans if plan.source == "tpex")

    assert plans
    assert all(plan.download_url in {None, ""} for plan in plans)
    assert all(plan.url in {None, ""} for plan in plans)
    assert all(plan.api_url in {None, ""} for plan in plans)
    assert "https://data.gov.tw/dataset/11395" in tpex_plan.landing_url
    assert "https://data.gov.tw/dataset/11396" in tpex_plan.landing_url


def test_openapi_source_candidates_are_recorded_for_missing_slots():
    config = load_data_source_config("configs/short_term_radar/data_sources.example.yaml")

    twse = config["sources"]["twse"]["datasets"]
    tpex = config["sources"]["tpex"]["datasets"]

    assert twse["institutional_trading"]["api_url"].endswith("/rwd/zh/fund/T86?date={date}&selectType=ALLBUT0999&response=json")
    assert tpex["institutional_trading"]["api_url"] == "https://www.tpex.org.tw/openapi/v1/tpex_3insti_daily_trading"
    assert twse["margin_short"]["api_url"] == "https://openapi.twse.com.tw/v1/exchangeReport/MI_MARGN"
    assert "https://openapi.twse.com.tw/v1/SBL/TWT96U" in twse["margin_short"]["supplemental_api_urls"]
    assert twse["trading_calendar"]["api_url"] == "https://openapi.twse.com.tw/v1/holidaySchedule/holidaySchedule"
    assert tpex["valuation_daily"]["api_url"] == "https://www.tpex.org.tw/openapi/v1/tpex_mainboard_peratio_analysis"


def test_collect_plan_uses_direct_api_urls_when_configured():
    config = load_data_source_config("configs/short_term_radar/data_sources.example.yaml")
    plans = build_collect_plan(config, "valuation", "TWSE")
    twse_plan = next(plan for plan in plans if plan.source == "twse")

    assert twse_plan.download_url == ""
    assert twse_plan.api_url == "https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_d"
    assert twse_plan.url == twse_plan.api_url
