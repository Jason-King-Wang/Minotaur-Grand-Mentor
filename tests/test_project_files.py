from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_FILES = [
    ".minotaur-project-root",
    "README.md",
    "CODEX.md",
    "SCOPE_LOCK.md",
    "docs/PROJECT_BRIEF.md",
    "docs/CODEX_WORK_BLUEPRINT_FULL.md",
    "docs/CODEX_IMPORT_ASSET_HANDOFF.md",
    "docs/STAGE_06_SAME_CANVAS_BLUEPRINT.md",
    "docs/CHARACTER_BIBLE.md",
    "docs/STYLE_GUIDE.md",
    "docs/SOFTWARE_SETUP.md",
    "docs/BOTTOM_LINES.md",
    "docs/DISCLAIMER.md",
    "docs/BLUEPRINT.md",
    "docs/TASK_BOARD.md",
    "docs/NEXT_ACTIONS.md",
    "docs/ASSET_SPEC.md",
    "docs/IMAGE_PROMPTS.md",
    "docs/PNGTUBER_MVP.md",
    "docs/LIVE2D_UPGRADE.md",
    "docs/LIVE2D_LAYER_SPEC.md",
    "docs/LIVE2D_RIGGER_CHECKLIST.md",
    "docs/OBS_SETUP.md",
    "docs/GITHUB_PAGES_SETUP.md",
    "docs/OBSIDIAN_PROJECT_PAGE.md",
    "docs/ACCEPTANCE_CRITERIA.md",
    "docs/FINAL_HANDOFF.md",
    "assets/reference/README.md",
    "assets/avatar/README.md",
    "assets/avatar/placeholders/README.md",
    "assets/avatar/pngtuber/README.md",
    "assets/avatar/live2d/README.md",
    "assets/avatar/live2d/sourcekit_v0_1/README.md",
    "overlay/index.html",
    "overlay/app.js",
    "overlay/styles.css",
    "dashboard/index.html",
    "dashboard/dashboard.js",
    "dashboard/dashboard.css",
    "data/avatar-manifest.json",
    "data/live2d-sourcekit-manifest.json",
    "data/live2d-component-manifest.json",
    "data/same-canvas-coordinate-map.json",
    "data/stage-06-validation-report.json",
    "data/project-state.json",
    "data/task-board.json",
    "data/run-log.json",
    "data/run-log.js",
    "data/dashboard-data.js",
    "records/README.md",
    "obsidian_project/README.md",
    "obsidian_project/MinotaurGrandMentor_Home.md",
    "obsidian_project/MinotaurGrandMentor_BottomLines.md",
    "obsidian_project/MinotaurGrandMentor_TaskBoard.md",
    "obsidian_project/MinotaurGrandMentor_AssetStatus.md",
    "obsidian_project/MinotaurGrandMentor_NextActions.md",
    "tools/scope_guard.py",
    "tools/log_event.py",
    "tools/validate_assets.py",
    "tools/build_public_data.py",
    "tools/build_same_canvas_pack.py",
    "tools/generate_placeholder_assets.py",
    "tools/export_obsidian_project_pages.py",
    "tools/generate_final_report.py",
    "tests/test_project_files.py",
]


class ProjectFileTests(unittest.TestCase):
    def test_required_files_exist(self) -> None:
        missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
        self.assertEqual(missing, [])

    def test_required_data_files_are_valid_json(self) -> None:
        for path in [
            "data/avatar-manifest.json",
            "data/live2d-sourcekit-manifest.json",
            "data/live2d-component-manifest.json",
            "data/same-canvas-coordinate-map.json",
            "data/stage-06-validation-report.json",
            "data/project-state.json",
            "data/task-board.json",
            "data/run-log.json",
        ]:
            with self.subTest(path=path):
                json.loads((ROOT / path).read_text(encoding="utf-8"))

    def test_scope_lock_content(self) -> None:
        bottom_lines = (ROOT / "docs/BOTTOM_LINES.md").read_text(encoding="utf-8")
        scope_lock = (ROOT / "SCOPE_LOCK.md").read_text(encoding="utf-8")
        self.assertIn("Obsidian", bottom_lines)
        self.assertIn("Codex 只能修改", bottom_lines)
        self.assertIn("Codex may only modify files under this project root", scope_lock)

    def test_avatar_manifest_shape(self) -> None:
        manifest = json.loads((ROOT / "data/avatar-manifest.json").read_text(encoding="utf-8"))
        required_ids = {asset["id"] for asset in manifest["required_assets"]}
        self.assertEqual(
            required_ids,
            {"idle_closed", "talk_open", "blink_closed", "happy"},
        )

    def test_live2d_manifest_shape(self) -> None:
        manifest = json.loads((ROOT / "data/live2d-sourcekit-manifest.json").read_text(encoding="utf-8"))
        required_ids = {asset["id"] for asset in manifest["required_final_files"]}
        self.assertIn("final_layered_psd", required_ids)
        self.assertIn("final_front_master", required_ids)
        self.assertIn("head_base", manifest["required_layers"])

    def test_same_canvas_outputs_exist(self) -> None:
        output_dir = ROOT / "assets/avatar/live2d/final/layers_png_same_canvas"
        outputs = sorted(output_dir.glob("*.png"))
        self.assertGreaterEqual(len(outputs), 30)
        self.assertTrue((output_dir / "head_base.png").exists())
        self.assertTrue((output_dir / "torso_jacket.png").exists())

    def test_project_state_shape(self) -> None:
        state = json.loads((ROOT / "data/project-state.json").read_text(encoding="utf-8"))
        for key in [
            "project",
            "version",
            "mode",
            "current_phase",
            "overall_status",
            "core_goal",
            "scope_lock",
            "engineering_status",
            "documentation_status",
            "overlay_status",
            "dashboard_status",
            "live2d_status",
            "completed_tasks",
            "pending_tasks",
            "missing_assets",
            "blocked_by_art",
            "blocked_by_rigging",
            "last_updated",
            "notes",
        ]:
            self.assertIn(key, state)


if __name__ == "__main__":
    unittest.main()
