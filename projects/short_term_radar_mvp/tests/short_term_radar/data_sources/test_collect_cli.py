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
