from __future__ import annotations

import argparse
from pathlib import Path


MARKER = ".minotaur-project-root"


def find_root(start: Path) -> Path | None:
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / MARKER).exists():
            return candidate
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Minotaur Grand Mentor project scope.")
    parser.add_argument("paths", nargs="*", help="Optional paths to validate.")
    args = parser.parse_args()

    root = find_root(Path.cwd())
    if root is None:
        print(f"Missing {MARKER}; refusing to continue.")
        return 1

    for raw_path in args.paths:
        path = Path(raw_path)
        resolved = (Path.cwd() / path).resolve() if not path.is_absolute() else path.resolve()
        try:
            resolved.relative_to(root)
        except ValueError:
            print(f"Out of scope: {resolved}")
            return 1

    print(f"Scope OK: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

