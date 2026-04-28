from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "docs" / "FINAL_HANDOFF.md"


def read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def main() -> int:
    state = read_json(DATA / "project-state.json", {})
    missing = state.get("missing_assets", [])
    blocked_art = state.get("blocked_by_art", [])
    blocked_rigging = state.get("blocked_by_rigging", [])
    content = f"""# Final Handoff

## Completed

- Scope lock and Obsidian protection.
- Documentation, dashboard, overlay, records, validation, placeholder, and Live2D specification tooling.
- Public fallback data for static dashboard use.

## Current Status

- Overall: `{state.get("overall_status", "unknown")}`
- Current phase: `{state.get("current_phase", "unknown")}`
- Engineering: `{state.get("engineering_status", "unknown")}`
- Documentation: `{state.get("documentation_status", "unknown")}`
- Overlay: `{state.get("overlay_status", "unknown")}`
- Dashboard: `{state.get("dashboard_status", "unknown")}`
- Live2D: `{state.get("live2d_status", "unknown")}`

## Missing Assets

{chr(10).join(f"- `{item}`" for item in missing) or "- None"}

## Blocked By Art

{chr(10).join(f"- {item}" for item in blocked_art) or "- None"}

## Blocked By Rigging

{chr(10).join(f"- {item}" for item in blocked_rigging) or "- None"}

## Commands

```powershell
python tools\\validate_assets.py
python tools\\build_public_data.py
python tests\\test_project_files.py
```

## Final Note

本內容僅供研究、教育與娛樂用途，不構成投資建議。
"""
    OUT.write_text(content, encoding="utf-8")
    print(f"Generated {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

