from __future__ import annotations

import argparse
import json
from pathlib import Path

from short_term_radar.utils.io import ensure_parent, read_csv


def _decode_list(value: str) -> str:
    if not value:
        return ""
    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return "<br>".join(str(item) for item in parsed)
    except json.JSONDecodeError:
        pass
    return value


def generate_report(scan_file: str, backtest_file: str, output: str) -> None:
    candidates = read_csv(scan_file)
    summaries = read_csv(backtest_file) if Path(backtest_file).exists() else []
    ensure_parent(output)

    lines = [
        "# Short Term Radar Report",
        "",
        "## 今日 Top Candidates",
        "",
        "| Rank | Symbol | Name | Score | Stage | Entry Zone | Main Reasons | Risks |",
        "|---:|---|---|---:|---|---|---|---|",
    ]

    for row in candidates[:50]:
        lines.append(
            "| {rank} | {symbol} | {name} | {score} | {stage} | {zone} | {reasons} | {risks} |".format(
                rank=row.get("rank", ""),
                symbol=row.get("symbol", ""),
                name=row.get("name", ""),
                score=row.get("score_total", ""),
                stage=row.get("stage", ""),
                zone=row.get("entry_zone", ""),
                reasons=_decode_list(row.get("reasons", "")),
                risks=_decode_list(row.get("risk_flags", "")),
            )
        )

    lines.extend(["", "## Backtest Summary", ""])
    if summaries:
        summary = summaries[0]
        lines.extend(
            [
                f"- Horizon: {summary.get('horizon_days')} trading days",
                f"- Top N: {summary.get('top_n')}",
                f"- Hit rate 3x: {summary.get('hit_rate_3x')}",
                f"- Hit rate 5x: {summary.get('hit_rate_5x')}",
                f"- Precision at N: {summary.get('precision_at_n')}",
            ]
        )
    else:
        lines.append("- Backtest file not found or empty.")

    lines.extend(["", "## Data Degradation", ""])
    degradation_count = sum(1 for row in candidates if "缺資料" in row.get("risk_flags", ""))
    lines.append(f"- Candidates with degraded radar data: {degradation_count}/{len(candidates)}")
    lines.append("- revenue/chip/catalyst adapters are placeholders in this MVP unless external data is added.")

    Path(output).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a Markdown radar report.")
    parser.add_argument("--scan-file", required=True)
    parser.add_argument("--backtest-file", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    generate_report(args.scan_file, args.backtest_file, args.output)
    print(f"Wrote report to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
