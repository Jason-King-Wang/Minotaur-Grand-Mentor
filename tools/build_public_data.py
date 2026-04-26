from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RUN_LOG_JSON = DATA_DIR / "run-log.json"
RUN_LOG_JS = DATA_DIR / "run-log.js"


def read_run_log() -> list[dict]:
    if not RUN_LOG_JSON.exists():
        return []
    data = json.loads(RUN_LOG_JSON.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("data/run-log.json must contain a JSON array")
    return data


def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    entries = read_run_log()
    RUN_LOG_JS.write_text(
        "window.__MINOTAUR_RUN_LOG__ = "
        + json.dumps(entries, ensure_ascii=False, indent=2)
        + ";\n",
        encoding="utf-8",
    )
    print("Built data/run-log.js")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

