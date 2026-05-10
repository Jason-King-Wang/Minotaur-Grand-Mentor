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


def _section_table(rows: list[dict[str, str]], title: str, limit: int = 20) -> list[str]:
    lines = [
        f"## {title}",
        "",
        "| Rank | Symbol | Name | Score | Coverage | Stage | Entry Zone | Core Ready | Main Reasons | Risks |",
        "|---:|---|---|---:|---:|---|---|---|---|---|",
    ]
    for row in rows[:limit]:
        lines.append(
            "| {rank} | {symbol} | {name} | {score} | {coverage} | {stage} | {zone} | {core} | {reasons} | {risks} |".format(
                rank=row.get("rank", ""),
                symbol=row.get("symbol", ""),
                name=row.get("name", ""),
                score=row.get("score_total", ""),
                coverage=row.get("data_coverage_ratio", ""),
                stage=row.get("stage", ""),
                zone=row.get("entry_zone", ""),
                core=row.get("core_data_ready_flag", ""),
                reasons=_decode_list(row.get("reasons", "")),
                risks=_decode_list(row.get("risk_flags", "")),
            )
        )
    return lines


def generate_report(
    scan_file: str,
    backtest_file: str,
    output: str,
    baseline_file: str | None = None,
    max_candidates: int = 50,
    show_degraded: bool = True,
) -> None:
    candidates = read_csv(scan_file)
    summaries = read_csv(backtest_file) if Path(backtest_file).exists() else []
    baselines = read_csv(baseline_file) if baseline_file and Path(baseline_file).exists() else []
    ensure_parent(output)

    s3 = [row for row in candidates if row.get("stage") == "S3"]
    s2 = [row for row in candidates if row.get("stage") == "S2"]
    s5 = [row for row in candidates if row.get("stage") == "S5"]
    degraded = [row for row in candidates if row.get("degraded_radars") not in ("", "[]")]

    lines = [
        "# Short Term Radar Report",
        "",
        "## Summary",
        "",
        f"- Scan date: {Path(scan_file).stem.replace('scan_', '')}",
        f"- Universe mode: {candidates[0].get('universe_mode') if candidates else ''}",
        f"- Data coverage summary: {len(degraded)} degraded / {len(candidates)} candidates",
        f"- Core data ready count: {sum(1 for row in candidates if row.get('core_data_ready_flag') in ('1', 'True', 'true'))}",
        f"- S3 candidate count: {len(s3)}",
        f"- S5 avoid count: {len(s5)}",
        "",
    ]
    lines.extend(_section_table(candidates, "Top Candidates", max_candidates))
    lines.extend([""])
    lines.extend(_section_table(s3, "S3 Candidate Entry", max_candidates))
    lines.extend([""])
    lines.extend(_section_table(s2, "S2 Early Watch", max_candidates))
    lines.extend([""])
    lines.extend(_section_table(s5, "S5 Avoid Chasing", max_candidates))

    lines.extend(["", "## Theme Groups", ""])
    lines.append("- Theme metrics are embedded in scan rows when industry/theme peer groups are available.")

    lines.extend(["", "## Backtest Summary", ""])
    if summaries:
        summary = summaries[0]
        for key in [
            "strategy_name",
            "horizon_days",
            "top_n",
            "hit_rate_2x",
            "hit_rate_3x",
            "hit_rate_5x",
            "avg_forward_max_return",
            "avg_forward_close_return",
            "avg_forward_path_max_drawdown",
            "precision_at_n",
        ]:
            lines.append(f"- {key}: {summary.get(key)}")
    else:
        lines.append("- Backtest file not found or empty.")

    lines.extend(["", "## Baseline Comparison", ""])
    if baselines:
        lines.extend(
            [
                "| Strategy | Candidates | Hit 2x | Hit 3x | Hit 5x | Avg Max Return | Avg Close Return | Avg Path DD | Precision |",
                "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for row in baselines:
            lines.append(
                f"| {row.get('strategy_name')} | {row.get('num_candidates')} | {row.get('hit_rate_2x')} | {row.get('hit_rate_3x')} | {row.get('hit_rate_5x')} | {row.get('avg_forward_max_return')} | {row.get('avg_forward_close_return')} | {row.get('avg_forward_path_max_drawdown')} | {row.get('precision_at_n')} |"
            )
    else:
        lines.append("- Baseline comparison file not supplied.")

    lines.extend(["", "## Data Degradation Notes", ""])
    if show_degraded:
        lines.append("- Missing revenue, chip, or catalyst data caps score_total and blocks S3 when revenue is missing.")
        lines.append("- expectation_gap_source remains price_only unless external news/social/analyst coverage is provided.")
    else:
        lines.append("- Degraded rows hidden by report option.")

    lines.extend(["", "## Backtest Limitations", ""])
    lines.append("- Survivorship bias depends on whether the source includes delisted securities.")
    lines.append("- Revenue release-date accuracy depends on the optional revenue source.")
    lines.append("- Chip and catalyst fields degrade when optional local files are absent.")

    lines.extend(["", "## Disclaimer", ""])
    lines.append("Research and education only; this is not investment advice.")

    Path(output).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a Markdown radar report.")
    parser.add_argument("--scan-file", required=True)
    parser.add_argument("--backtest-file", required=True)
    parser.add_argument("--baseline-file")
    parser.add_argument("--max-candidates", type=int, default=50)
    parser.add_argument("--show-degraded", default="true", choices=["true", "false"])
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    generate_report(
        args.scan_file,
        args.backtest_file,
        args.output,
        args.baseline_file,
        args.max_candidates,
        args.show_degraded == "true",
    )
    print(f"Wrote report to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
