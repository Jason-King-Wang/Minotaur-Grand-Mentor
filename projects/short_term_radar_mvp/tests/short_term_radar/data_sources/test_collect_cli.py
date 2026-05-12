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


def test_collect_institutional_trading_official_dry_run(capsys):
    exit_code = main(
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

    assert exit_code == 0
    assert "[dry-run] institutional_trading TWSE 2026-04-30 via official (enabled)" in output
    assert "T86?date=20260430" in output


def test_collect_institutional_trading_official_requires_date():
    with pytest.raises(ValueError, match="requires --date"):
        main(
            [
                "--config",
                "configs/short_term_radar/data_sources.example.yaml",
                "--dataset",
                "institutional_trading",
                "--market",
                "TWSE",
                "--source",
                "official",
            ]
        )
