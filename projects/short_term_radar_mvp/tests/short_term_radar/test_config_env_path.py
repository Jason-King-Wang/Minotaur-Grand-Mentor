from __future__ import annotations

from short_term_radar.config import load_config


def test_config_expands_env_paths_and_optional_defaults(tmp_path, monkeypatch):
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        """
data:
  daily_price_path: "${TW_EQUITIES_DATA_PATH}"
  monthly_revenue_path: "${OPTIONAL_PATH:-}"
""",
        encoding="utf-8",
    )
    monkeypatch.setenv("TW_EQUITIES_DATA_PATH", "C:/data/tw")
    monkeypatch.delenv("OPTIONAL_PATH", raising=False)

    config = load_config(config_file)

    assert config["data"]["daily_price_path"] == "C:/data/tw"
    assert config["data"]["monthly_revenue_path"] is None
