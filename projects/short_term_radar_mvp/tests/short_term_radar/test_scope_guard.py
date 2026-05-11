from __future__ import annotations

from pathlib import Path


def test_short_term_radar_package_lives_under_projects_folder():
    project_root = Path(__file__).resolve().parents[2]
    repo_root = project_root.parents[1]

    assert project_root.name == "short_term_radar_mvp"
    assert project_root.parent.name == "projects"
    assert (project_root / "short_term_radar").is_dir()
    assert not (repo_root / "short_term_radar").exists()
    assert not (repo_root / "configs" / "short_term_radar").exists()
    assert not (repo_root / "SHORT_TERM_RADAR_HANDOFF.md").exists()


def test_repo_root_readme_stays_minotaur_scoped():
    project_root = Path(__file__).resolve().parents[2]
    repo_root = project_root.parents[1]
    readme = (repo_root / "README.md").read_text(encoding="utf-8")

    assert "# Minotaur Grand Mentor" in readme
    assert "projects/short_term_radar_mvp" not in readme


def test_repo_root_gitignore_has_no_radar_project_rules():
    project_root = Path(__file__).resolve().parents[2]
    repo_root = project_root.parents[1]
    gitignore = repo_root / ".gitignore"
    if not gitignore.exists():
        return

    text = gitignore.read_text(encoding="utf-8")
    assert "short_term_radar" not in text
    assert "configs/short_term_radar" not in text
    assert "/data/processed" not in text
