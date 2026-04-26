from __future__ import annotations

import json
import struct
from datetime import datetime, timezone, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
MANIFEST = DATA_DIR / "avatar-manifest.json"
PROJECT_STATE = DATA_DIR / "project-state.json"
TAIPEI = timezone(timedelta(hours=8))


def read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def png_size(path: Path) -> tuple[int, int] | None:
    try:
        with path.open("rb") as file:
            header = file.read(24)
        if len(header) < 24 or not header.startswith(b"\x89PNG\r\n\x1a\n"):
            return None
        width, height = struct.unpack(">II", header[16:24])
        return width, height
    except OSError:
        return None


def asset_rows(manifest: dict) -> list[dict]:
    return list(manifest.get("required_assets", [])) + list(manifest.get("optional_assets", []))


def update_project_state(missing_required: list[str]) -> None:
    state = read_json(PROJECT_STATE, {})
    state.setdefault("project", "Minotaur Grand Mentor")
    state.setdefault("version", "0.1.0")
    state.setdefault("completed_tasks", [])
    state.setdefault("pending_tasks", [])
    state["missing_assets"] = missing_required
    state["last_updated"] = datetime.now(TAIPEI).isoformat(timespec="seconds")
    if missing_required:
        state["overall_status"] = f"Assets pending: {len(missing_required)} required PNGTuber files missing"
    else:
        state["overall_status"] = "Required PNGTuber assets present"
    write_json(PROJECT_STATE, state)


def main() -> int:
    manifest = read_json(MANIFEST, {})
    if not manifest:
        print("Missing or invalid data/avatar-manifest.json")
        update_project_state([])
        return 0

    missing_required: list[str] = []
    missing_optional: list[str] = []
    size_notes: list[str] = []

    for asset in asset_rows(manifest):
        rel_path = asset.get("path", "")
        file_path = ROOT / rel_path
        exists = file_path.exists()
        if not exists and asset.get("required"):
            missing_required.append(rel_path)
        elif not exists:
            missing_optional.append(rel_path)
        elif file_path.suffix.lower() == ".png":
            size = png_size(file_path)
            if size is None:
                size_notes.append(f"{rel_path}: PNG dimensions unreadable")
            else:
                width, height = size
                if (width, height) not in {(2048, 2048), (3000, 3000)}:
                    size_notes.append(f"{rel_path}: {width}x{height}, expected 2048x2048 or 3000x3000")

    update_project_state(missing_required)

    print("Asset validation report")
    print("=======================")
    if missing_required:
        print("Missing required assets:")
        for item in missing_required:
            print(f"- {item}")
    else:
        print("All required assets are present.")

    if missing_optional:
        print("\nMissing optional assets:")
        for item in missing_optional:
            print(f"- {item}")

    if size_notes:
        print("\nSize notes:")
        for item in size_notes:
            print(f"- {item}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

