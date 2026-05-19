from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
TAIPEI = timezone(timedelta(hours=8))


def read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def write_js(path: Path, variable: str, value) -> None:
    path.write_text(
        f"window.{variable} = "
        + json.dumps(value, ensure_ascii=False, indent=2)
        + ";\n",
        encoding="utf-8",
    )


def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    project_state = read_json(DATA_DIR / "project-state.json", {})
    task_board = read_json(DATA_DIR / "task-board.json", {"columns": {}, "tasks": []})
    avatar_manifest = read_json(DATA_DIR / "avatar-manifest.json", {})
    live2d_manifest = read_json(DATA_DIR / "live2d-sourcekit-manifest.json", {})
    live2d_component_manifest = read_json(DATA_DIR / "live2d-component-manifest.json", {})
    stage_06_validation = read_json(DATA_DIR / "stage-06-validation-report.json", {})
    run_log = read_json(DATA_DIR / "run-log.json", [])
    if not isinstance(run_log, list):
        run_log = []

    write_js(DATA_DIR / "run-log.js", "__MINOTAUR_RUN_LOG__", run_log)
    write_js(
        DATA_DIR / "dashboard-data.js",
        "__MINOTAUR_DASHBOARD_DATA__",
        {
            "projectState": project_state,
            "taskBoard": task_board,
            "avatarManifest": avatar_manifest,
            "live2dManifest": live2d_manifest,
            "live2dComponentManifest": live2d_component_manifest,
            "stage06Validation": stage_06_validation,
            "runLog": run_log,
            "generatedAt": datetime.now(TAIPEI).isoformat(timespec="seconds"),
        },
    )
    print("Built data/run-log.js and data/dashboard-data.js")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
