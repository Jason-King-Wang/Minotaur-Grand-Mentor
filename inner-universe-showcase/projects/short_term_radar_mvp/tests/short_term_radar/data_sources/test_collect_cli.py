from __future__ import annotations

import pytest

from short_term_radar.cli.collect import main


def test_collect_write_raw_is_not_silently_ignored():
    with pytest.raises(ValueError, match="write-raw"):
        main(
            [
                "--config",
                "configs/short_term_radar/local.yaml.example",
                "--dataset",
                "prices_daily",
                "--write-raw",
            ]
        )


def test_official_institutional_dry_run_prints_direct_endpoint(capsys):
    result = main(
        [
            "--config",
            "configs/short_term_radar/data_sources.example.yaml",
            "--dataset",
            "institutional_trading",
            "--market",
            "TWSE",
            "--date",
            "2026-04-30",
            "--source",
            "official",
            "--dry-run",
        ]
    )

    output = capsys.readouterr().out

    assert result == 0
    assert "institutional_trading TWSE twse_t86 via official date=2026-04-30" in output
    assert "https://openapi.twse.com.tw/v1/exchangeReport/T86" in output


def test_official_institutional_range_errors_explicitly():
    with pytest.raises(ValueError, match="range collect not implemented"):
        main(
            [
                "--config",
                "configs/short_term_radar/data_sources.example.yaml",
                "--dataset",
                "institutional_trading",
                "--market",
                "all",
                "--start",
                "2021-01-01",
                "--end",
                "2026-05-11",
                "--source",
                "official",
                "--normalize",
            ]
        )
