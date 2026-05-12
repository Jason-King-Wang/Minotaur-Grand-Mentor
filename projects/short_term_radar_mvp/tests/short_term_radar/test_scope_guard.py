from __future__ import annotations

from pathlib import Path


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _embedded_repo_root(project_root: Path) -> Path | None:
    if project_root.parent.name == "projects":
        return project_root.parents[1]
    assert not (project_root.parent / ".minotaur-project-root").exists(), (
        "short_term_radar_mvp must live under projects/ inside the Minotaur repo, "
        "or be moved out as a standalone project."
    )
    return None


def test_short_term_radar_project_layout_is_self_contained():
    project_root = Path(__file__).resolve().parents[2]
    repo_root = _embedded_repo_root(project_root)

    assert project_root.name == "short_term_radar_mvp"
    assert (project_root / "short_term_radar").is_dir()
    assert (project_root / "short_term_radar" / "__init__.py").is_file()
    assert (project_root / "configs" / "short_term_radar" / "default.yaml").is_file()
    assert (project_root / "tests" / "short_term_radar").is_dir()

    if repo_root is None:
        return

    assert not (repo_root / "short_term_radar").exists()
    assert not (repo_root / "configs" / "short_term_radar").exists()
    assert not (repo_root / "tests" / "short_term_radar").exists()
    assert not (repo_root / "reports" / "short_term_radar").exists()
    assert not (repo_root / "SHORT_TERM_RADAR_HANDOFF.md").exists()
    assert not (repo_root / "pytest.ini").exists()


def test_repo_root_readme_stays_minotaur_scoped():
    project_root = _project_root()
    repo_root = _embedded_repo_root(project_root)
    if repo_root is None:
        readme = (project_root / "README.md").read_text(encoding="utf-8")
        assert "# Short Term Radar MVP" in readme
        return

    readme = (repo_root / "README.md").read_text(encoding="utf-8")

    assert "# Minotaur Grand Mentor" in readme
    assert "projects/short_term_radar_mvp" not in readme


def test_repo_root_gitignore_has_no_radar_project_rules():
    project_root = _project_root()
    repo_root = _embedded_repo_root(project_root)
    if repo_root is None:
        return

    gitignore = repo_root / ".gitignore"
    if not gitignore.exists():
        return

    text = gitignore.read_text(encoding="utf-8")
    assert "short_term_radar" not in text
    assert "configs/short_term_radar" not in text
    assert "/data/processed" not in text


def test_repo_root_data_has_no_short_term_radar_artifacts():
    project_root = _project_root()
    repo_root = _embedded_repo_root(project_root)
    if repo_root is None:
        return

    root_data = repo_root / "data"
    if not root_data.exists():
        return

    radar_data_files = {
        "prices_daily.parquet",
        "symbol_master.parquet",
        "monthly_revenue.parquet",
        "institutional_trading_daily.parquet",
        "margin_short_daily.parquet",
        "surveillance_daily.parquet",
        "material_events.parquet",
        "corporate_actions.parquet",
        "financial_statement_quarterly.parquet",
        "valuation_daily.parquet",
    }
    root_data_paths = [path.relative_to(root_data) for path in root_data.rglob("*")]

    assert not any("short_term_radar" in str(path).replace("\\", "/") for path in root_data_paths)
    assert not any(path.name in radar_data_files for path in root_data_paths)
