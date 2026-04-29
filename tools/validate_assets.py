from __future__ import annotations

import json
import struct
from datetime import datetime, timezone, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
AVATAR_MANIFEST = DATA_DIR / "avatar-manifest.json"
LIVE2D_MANIFEST = DATA_DIR / "live2d-sourcekit-manifest.json"
PROJECT_STATE = DATA_DIR / "project-state.json"
SAME_CANVAS_DIR = ROOT / "assets" / "avatar" / "live2d" / "final" / "layers_png_same_canvas"
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
        return struct.unpack(">II", header[16:24])
    except OSError:
        return None


def update_project_state(missing_assets: list[str], blocked_by_art: list[str]) -> None:
    state = read_json(PROJECT_STATE, {})
    state.setdefault("project", "Minotaur Grand Mentor")
    state.setdefault("version", "0.2.0")
    state.setdefault("completed_tasks", [])
    state.setdefault("pending_tasks", [])
    state.setdefault("blocked_by_rigging", [
        "Live2D Cubism rigging",
        ".moc3 export",
        "VTube Studio test",
    ])
    state["missing_assets"] = missing_assets
    state["blocked_by_art"] = blocked_by_art
    state["last_updated"] = datetime.now(TAIPEI).isoformat(timespec="seconds")
    missing_pngtuber = [item for item in missing_assets if "/pngtuber/" in item.replace("\\", "/")]
    missing_live2d = [item for item in missing_assets if "/live2d/" in item.replace("\\", "/")]

    if missing_pngtuber:
        state["overall_status"] = "ready_waiting_for_art_assets"
        state["current_phase"] = "waiting_for_art"
        state["overlay_status"] = "placeholder_ready"
    elif missing_live2d:
        same_canvas_count = len(list(SAME_CANVAS_DIR.glob("*.png"))) if SAME_CANVAS_DIR.exists() else 0
        if same_canvas_count and all("final_layered_model" in item for item in missing_live2d):
            state["overall_status"] = "same_canvas_layer_pack_built_pending_psd_and_rigging"
            state["current_phase"] = "stage_06_same_canvas_pack_built"
            state["live2d_status"] = "same_canvas_pack_built_pending_visual_review_final_psd_and_moc3_pending"
        else:
            state["overall_status"] = "pngtuber_mvp_ready_waiting_for_live2d_assets"
            state["current_phase"] = "pngtuber_mvp_ready"
            state["live2d_status"] = "spec_ready_waiting_for_art_and_rigging"
        state["overlay_status"] = "pngtuber_assets_ready"
    else:
        state["overall_status"] = "required_art_assets_present"
        state["current_phase"] = "art_assets_present"
        state["overlay_status"] = "pngtuber_assets_ready"
    write_json(PROJECT_STATE, state)


def main() -> int:
    avatar_manifest = read_json(AVATAR_MANIFEST, {})
    live2d_manifest = read_json(LIVE2D_MANIFEST, {})
    missing_assets: list[str] = []
    blocked_by_art: list[str] = []
    size_notes: list[str] = []

    print("PNGTuber required assets:")
    for asset in avatar_manifest.get("required_assets", []):
        path = asset.get("path", "")
        full_path = ROOT / path
        if full_path.exists():
            print(f"[OK] {asset.get('id')} -> {path}")
            if full_path.suffix.lower() == ".png":
                size = png_size(full_path)
                if size and size not in {(2048, 2048), (3000, 3000)}:
                    size_notes.append(f"{path}: {size[0]}x{size[1]}")
        else:
            print(f"[MISSING] {asset.get('id')} -> {path}")
            missing_assets.append(path)

    print("\nPNGTuber optional assets:")
    for asset in avatar_manifest.get("optional_assets", []):
        path = asset.get("path", "")
        full_path = ROOT / path
        status = "OK" if full_path.exists() else "MISSING"
        print(f"[{status}] {asset.get('id')} -> {path}")

    print("\nLive2D required final files:")
    for asset in live2d_manifest.get("required_final_files", []):
        path = asset.get("path", "")
        full_path = ROOT / path
        if full_path.exists():
            print(f"[OK] {asset.get('id')} -> {path}")
        else:
            print(f"[MISSING] {asset.get('id')} -> {path}")
            missing_assets.append(path)

    if any("pngtuber" in item for item in missing_assets):
        blocked_by_art.append("PNGTuber expression PNG files")
    if any("final_front_master" in item for item in missing_assets):
        blocked_by_art.append("Live2D final front master image")
    if any("final_layered_model" in item for item in missing_assets):
        blocked_by_art.append("Live2D final layered PSD")

    if size_notes:
        print("\nSize notes:")
        for note in size_notes:
            print(f"- {note}")

    update_project_state(missing_assets, blocked_by_art)
    state = read_json(PROJECT_STATE, {})
    print(f"\nStatus: {state.get('overall_status', 'ready' if not missing_assets else 'waiting_for_art_assets')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
