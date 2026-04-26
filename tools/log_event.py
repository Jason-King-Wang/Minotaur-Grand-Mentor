from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RECORDS_DIR = ROOT / "records"
RUN_LOG_JSON = DATA_DIR / "run-log.json"
RUN_LOG_JS = DATA_DIR / "run-log.js"
PROJECT_STATE = DATA_DIR / "project-state.json"
TAIPEI = timezone(timedelta(hours=8))


def now_local() -> datetime:
    return datetime.now(TAIPEI)


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "event"


def read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_run_log_js(entries: list[dict]) -> None:
    RUN_LOG_JS.write_text(
        "window.__MINOTAUR_RUN_LOG__ = "
        + json.dumps(entries, ensure_ascii=False, indent=2)
        + ";\n",
        encoding="utf-8",
    )


def unique_record_path(timestamp: datetime, phase: str) -> Path:
    day_dir = RECORDS_DIR / timestamp.strftime("%Y-%m-%d")
    day_dir.mkdir(parents=True, exist_ok=True)
    base_name = f"{timestamp.strftime('%H%M%S')}-{slugify(phase)}"
    candidate = day_dir / f"{base_name}.md"
    counter = 2
    while candidate.exists():
        candidate = day_dir / f"{base_name}-{counter}.md"
        counter += 1
    return candidate


def write_record(path: Path, entry: dict) -> None:
    content = f"""# {entry["phase"]}: {entry["summary"]}

- Time: {entry["timestamp"]}
- Status: {entry["status"]}

## Details

{entry["details"]}

## Next

{entry["next"]}
"""
    path.write_text(content, encoding="utf-8")


def update_project_state(entry: dict) -> None:
    state = read_json(PROJECT_STATE, {})
    state.setdefault("project", "Minotaur Grand Mentor")
    state.setdefault("version", "0.1.0")
    state.setdefault("completed_tasks", [])
    state.setdefault("pending_tasks", [])
    state.setdefault("missing_assets", [])

    state["current_phase"] = entry["phase"]
    state["overall_status"] = f'{entry["phase"]}: {entry["status"]} - {entry["summary"]}'
    state["last_updated"] = entry["timestamp"]
    state["notes"] = entry["next"]

    task_label = f'{entry["phase"]}: {entry["summary"]}'
    if entry["status"].lower() in {"done", "complete", "completed"}:
        if task_label not in state["completed_tasks"]:
            state["completed_tasks"].append(task_label)
        state["pending_tasks"] = [
            task
            for task in state["pending_tasks"]
            if not task.startswith(entry["phase"])
        ]
    else:
        if task_label not in state["pending_tasks"]:
            state["pending_tasks"].append(task_label)

    write_json(PROJECT_STATE, state)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a project record and update public log data.")
    parser.add_argument("--phase", required=True, help="Phase name, e.g. Phase 1.")
    parser.add_argument("--status", required=True, help="Status such as done, pending, or blocked.")
    parser.add_argument("--summary", required=True, help="Short event summary.")
    parser.add_argument("--details", required=True, help="Longer event details.")
    parser.add_argument("--next", required=True, dest="next_step", help="Next action or handoff note.")
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    RECORDS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = now_local()
    record_path = unique_record_path(timestamp, args.phase)
    entry = {
        "timestamp": timestamp.isoformat(timespec="seconds"),
        "phase": args.phase,
        "status": args.status,
        "summary": args.summary,
        "details": args.details,
        "next": args.next_step,
        "record": str(record_path.relative_to(ROOT)).replace("\\", "/"),
    }

    write_record(record_path, entry)
    entries = read_json(RUN_LOG_JSON, [])
    if not isinstance(entries, list):
        entries = []
    entries.append(entry)
    write_json(RUN_LOG_JSON, entries)
    write_run_log_js(entries)
    update_project_state(entry)

    print(f"Logged {entry['phase']} -> {entry['record']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

