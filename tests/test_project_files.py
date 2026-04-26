from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_FILES = [
    "README.md",
    "CODEX.md",
    "docs/PROJECT_BRIEF.md",
    "docs/CHARACTER_BIBLE.md",
    "docs/STYLE_GUIDE.md",
    "docs/ASSET_SPEC.md",
    "docs/IMAGE_PROMPTS.md",
    "docs/BLUEPRINT.md",
    "docs/OBS_SETUP.md",
    "docs/LIVE2D_UPGRADE.md",
    "docs/NEXT_ACTIONS.md",
    "assets/reference/README.md",
    "assets/avatar/pngtuber/README.md",
    "overlay/index.html",
    "overlay/app.js",
    "overlay/styles.css",
    "dashboard/index.html",
    "dashboard/dashboard.js",
    "dashboard/dashboard.css",
    "data/avatar-manifest.json",
    "data/project-state.json",
    "data/run-log.json",
    "data/run-log.js",
    "records/README.md",
    "tools/log_event.py",
    "tools/validate_assets.py",
    "tools/build_public_data.py",
    "tests/test_project_files.py",
]


class ProjectFileTests(unittest.TestCase):
    def test_required_files_exist(self) -> None:
        missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
        self.assertEqual(missing, [])

    def test_required_data_files_are_valid_json(self) -> None:
        for path in [
            "data/avatar-manifest.json",
            "data/project-state.json",
            "data/run-log.json",
        ]:
            with self.subTest(path=path):
                json.loads((ROOT / path).read_text(encoding="utf-8"))

    def test_avatar_manifest_shape(self) -> None:
        manifest = json.loads((ROOT / "data/avatar-manifest.json").read_text(encoding="utf-8"))
        required_ids = {asset["id"] for asset in manifest["required_assets"]}
        self.assertEqual(
            required_ids,
            {"idle_closed", "talk_open", "blink_closed", "happy"},
        )

    def test_project_state_shape(self) -> None:
        state = json.loads((ROOT / "data/project-state.json").read_text(encoding="utf-8"))
        for key in [
            "project",
            "version",
            "current_phase",
            "overall_status",
            "completed_tasks",
            "pending_tasks",
            "missing_assets",
            "last_updated",
            "notes",
        ]:
            self.assertIn(key, state)


if __name__ == "__main__":
    unittest.main()

