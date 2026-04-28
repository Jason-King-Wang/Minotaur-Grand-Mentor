from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "obsidian_project"


def read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    state = read_json(DATA / "project-state.json", {})
    tasks = read_json(DATA / "task-board.json", {"tasks": []}).get("tasks", [])
    missing = state.get("missing_assets", [])

    write(OUT / "MinotaurGrandMentor_Home.md", f"""# Minotaur Grand Mentor Home

Overall status: `{state.get("overall_status", "unknown")}`

Current phase: `{state.get("current_phase", "unknown")}`

Engineering: `{state.get("engineering_status", "unknown")}`

Documentation: `{state.get("documentation_status", "unknown")}`

Overlay: `{state.get("overlay_status", "unknown")}`

Dashboard: `{state.get("dashboard_status", "unknown")}`

Live2D: `{state.get("live2d_status", "unknown")}`
""")

    write(OUT / "MinotaurGrandMentor_TaskBoard.md", "# Minotaur Grand Mentor Task Board\n\n" + "\n".join(
        f"- [{task.get('status')}] {task.get('id')}: {task.get('title')}" for task in tasks
    ) + "\n")

    write(OUT / "MinotaurGrandMentor_AssetStatus.md", "# Minotaur Grand Mentor Asset Status\n\n" + "\n".join(
        f"- `{item}`" for item in missing
    ) + "\n")

    print("Exported Obsidian project pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

