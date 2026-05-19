from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

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


def generate_report(scan_file: str, backtest_file: str, output: str, baseline_file: str | None = None) -> None:
    candidates = read_csv(scan_file)
    summaries = read_csv(backtest_file) if Path(backtest_file).exists() else []
    baseline_rows = read_csv(baseline_file) if baseline_file and Path(baseline_file).exists() else []
    ensure_parent(output)

    lines = ["# Short Term Radar Report", ""]
    lines.extend(_coverage_summary(candidates))
    lines.extend(_mode_summary(candidates))
    lines.extend(_robot_slot_summary(candidates))
    lines.extend(_candidate_section("Top S3 Candidate Entry", [row for row in candidates if row.get("stage") == "S3"]))
    lines.extend(_candidate_section("Top S2 Early Watch", [row for row in candidates if row.get("stage") == "S2"]))
    lines.extend(_candidate_section("Avoid Chasing / S5", [row for row in candidates if row.get("stage") == "S5"]))
    lines.extend(_degraded_summary(candidates))
    lines.extend(_baseline_section(baseline_rows))
    lines.extend(_backtest_section(summaries))
    lines.extend(_freshness_warning(candidates))

    Path(output).write_text("\n".join(lines) + "\n", encoding="utf-8")


def _coverage_summary(candidates: list[dict[str, Any]]) -> list[str]:
    score_ratios = [
        _float(row.get("score_data_coverage_ratio"))
        for row in candidates
        if row.get("score_data_coverage_ratio") not in {None, ""}
    ]
    slot_ratios = [
        _float(row.get("robot_slot_coverage_ratio"))
        for row in candidates
        if row.get("robot_slot_coverage_ratio") not in {None, ""}
    ]
    avg_score_ratio = sum(score_ratios) / len(score_ratios) if score_ratios else 0.0
    avg_slot_ratio = sum(slot_ratios) / len(slot_ratios) if slot_ratios else 0.0
    core_ready = sum(1 for row in candidates if str(row.get("core_data_ready_flag")).lower() in {"true", "1", "yes"})
    return [
        "## Data Coverage Summary",
        "",
        f"- Candidates: {len(candidates)}",
        f"- Average score data coverage ratio: {avg_score_ratio:.4f}",
        f"- Average robot slot coverage ratio: {avg_slot_ratio:.4f}",
        f"- Core data ready: {core_ready}/{len(candidates)}",
        "",
    ]


def _mode_summary(candidates: list[dict[str, Any]]) -> list[str]:
    counts: dict[str, int] = {}
    for row in candidates:
        mode = row.get("mode") or "unknown"
        counts[mode] = counts.get(mode, 0) + 1
    mode_text = ", ".join(f"{mode}: {count}" for mode, count in sorted(counts.items())) or "N/A"
    return [
        "## Radar Mode Summary",
        "",
        f"- Mode distribution: {mode_text}",
        "- Simple mode can scan, backtest, compare baselines, and report, but cannot enter S3 candidate_entry without revenue gating.",
        "",
    ]


def _robot_slot_summary(candidates: list[dict[str, Any]]) -> list[str]:
    statuses = _decode_slot_statuses(candidates[0].get("robot_slot_statuses")) if candidates else {}
    lines = [
        "## Robot Slot Status",
        "",
        "| Slot | Status |",
        "|---|---|",
    ]
    for slot, status in statuses.items():
        lines.append(f"| {_cell(slot)} | {_cell(status)} |")
    if not statuses:
        lines.append("| N/A | N/A |")
    lines.append("")
    return lines


def _candidate_section(title: str, rows: list[dict[str, Any]]) -> list[str]:
    lines = [
        f"## {title}",
        "",
        "| Rank | Symbol | Name | Score | Raw | Adjusted | Cap | Entry Zone | Main Reasons | Risks |",
        "|---:|---|---|---:|---:|---:|---:|---|---|---|",
    ]
    for row in rows[:20]:
        lines.append(
            "| {rank} | {symbol} | {name} | {score} | {raw} | {adjusted} | {cap} | {zone} | {reasons} | {risks} |".format(
                rank=_cell(row.get("rank")),
                symbol=_cell(row.get("symbol")),
                name=_cell(row.get("name")),
                score=_cell(row.get("score_total")),
                raw=_cell(row.get("score_raw_available_norm")),
                adjusted=_cell(row.get("score_coverage_adjusted")),
                cap=_cell(row.get("score_cap")),
                zone=_cell(row.get("entry_zone")),
                reasons=_cell(_decode_list(row.get("reasons", ""))),
                risks=_cell(_decode_list(row.get("risk_flags", ""))),
            )
        )
    if not rows:
        lines.append("|  | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |")
    lines.append("")
    return lines


def _decode_slot_statuses(value: Any) -> dict[str, str]:
    if isinstance(value, dict):
        return {str(key): str(item) for key, item in value.items()}
    if not value:
        return {}
    try:
        parsed = json.loads(str(value))
    except json.JSONDecodeError:
        return {}
    if not isinstance(parsed, dict):
        return {}
    return {str(key): str(item) for key, item in parsed.items()}


def _degraded_summary(candidates: list[dict[str, Any]]) -> list[str]:
    degraded = [row for row in candidates if row.get("degraded_radars")]
    return [
        "## Degraded Radar Summary",
        "",
        f"- Candidates with degraded radar data: {len(degraded)}/{len(candidates)}",
        "- Missing revenue caps candidate entry; active disposition forces S5 avoid_chasing.",
        "",
    ]


def _baseline_section(rows: list[dict[str, Any]]) -> list[str]:
    lines = [
        "## Baseline Comparison",
        "",
        "| Strategy | Hit 3x | Hit 5x | Precision | Avg Forward Max Return | Candidates |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {strategy} | {hit3} | {hit5} | {precision} | {avg} | {count} |".format(
                strategy=_cell(row.get("strategy_name")),
                hit3=_cell(row.get("hit_rate_3x")),
                hit5=_cell(row.get("hit_rate_5x")),
                precision=_cell(row.get("precision_at_n")),
                avg=_cell(row.get("avg_forward_max_return")),
                count=_cell(row.get("num_candidates")),
            )
        )
    if not rows:
        lines.append("| N/A | N/A | N/A | N/A | N/A | N/A |")
    lines.append("")
    return lines


def _backtest_section(rows: list[dict[str, Any]]) -> list[str]:
    lines = ["## Backtest Metrics", ""]
    if rows:
        summary = rows[0]
        lines.extend(
            [
                f"- Horizon: {summary.get('horizon_days', 'N/A')} trading days",
                f"- Top N: {summary.get('top_n', 'N/A')}",
                f"- Hit rate 3x: {summary.get('hit_rate_3x', 'N/A')}",
                f"- Hit rate 5x: {summary.get('hit_rate_5x', 'N/A')}",
                f"- Precision at N: {summary.get('precision_at_n', 'N/A')}",
            ]
        )
    else:
        lines.append("- Backtest file not found or empty.")
    lines.append("")
    return lines


def _freshness_warning(candidates: list[dict[str, Any]]) -> list[str]:
    missing_revenue = sum(1 for row in candidates if "revenue" in str(row.get("degraded_radars") or ""))
    return [
        "## Source Freshness Warning",
        "",
        f"- Revenue degraded candidates: {missing_revenue}/{len(candidates)}",
        "- N/A means the processed table or latest source row was unavailable for the scan date.",
        "",
    ]


def _float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _cell(value: Any) -> str:
    text = "N/A" if value is None or value == "" else str(value)
    return text.replace("|", "\\|").replace("\n", "<br>")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a Markdown radar report.")
    parser.add_argument("--scan-file", required=True)
    parser.add_argument("--backtest-file", required=True)
    parser.add_argument("--baseline-file")
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    generate_report(args.scan_file, args.backtest_file, args.output, args.baseline_file)
    print(f"Wrote report to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
