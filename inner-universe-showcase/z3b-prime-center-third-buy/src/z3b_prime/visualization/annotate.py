from __future__ import annotations

from pathlib import Path

from z3b_prime.models import Bar, TradeResult


def write_annotated_svg(
    path: str | Path,
    bars: list[Bar],
    trade: TradeResult | None,
    *,
    title: str = "Z3B-Prime annotated chart",
) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    if not bars:
        Path(path).write_text(empty_svg(title), encoding="utf-8")
        return

    width = 1200
    height = 640
    margin = 64
    prices = [bar.high for bar in bars] + [bar.low for bar in bars]
    if trade is not None:
        prices += [trade.entry_price, trade.stop_loss, trade.take_profit, trade.exit_price]
    min_price = min(prices)
    max_price = max(prices)
    span = max(max_price - min_price, 1e-9)

    def x_for(index: int) -> float:
        if len(bars) == 1:
            return margin
        return margin + index * ((width - margin * 2) / (len(bars) - 1))

    def y_for(price: float) -> float:
        return height - margin - ((price - min_price) / span) * (height - margin * 2)

    close_points = " ".join(
        f"{x_for(index):.2f},{y_for(bar.close):.2f}" for index, bar in enumerate(bars)
    )
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>text{font-family:Arial,'Noto Sans TC',sans-serif}.axis{stroke:#94a3b8}.line{fill:none;stroke:#0f4c81;stroke-width:2}.entry{stroke:#16a34a}.stop{stroke:#dc2626}.target{stroke:#2563eb}.marker{fill:#0f4c81}.label{fill:#0f172a;font-size:14px}.small{fill:#475569;font-size:12px}</style>",
        f'<rect width="{width}" height="{height}" fill="#f8fbff"/>',
        f'<text x="{margin}" y="34" class="label">{escape(title)}</text>',
        f'<text x="{margin}" y="54" class="small">Generated structure review chart; MACD labels are diagnostic only.</text>',
        f'<line x1="{margin}" y1="{height-margin}" x2="{width-margin}" y2="{height-margin}" class="axis"/>',
        f'<line x1="{margin}" y1="{margin}" x2="{margin}" y2="{height-margin}" class="axis"/>',
        f'<polyline points="{close_points}" class="line"/>',
    ]

    if trade is not None:
        entry_idx = closest_bar_index(bars, trade.entry_time)
        exit_idx = closest_bar_index(bars, trade.exit_time)
        draw_level(parts, margin, width - margin, y_for(trade.entry_price), "entry", f"Entry {trade.entry_price:.2f}")
        draw_level(parts, margin, width - margin, y_for(trade.stop_loss), "stop", f"SL {trade.stop_loss:.2f}")
        draw_level(parts, margin, width - margin, y_for(trade.take_profit), "target", f"TP {trade.take_profit:.2f}")
        parts.append(
            f'<circle cx="{x_for(entry_idx):.2f}" cy="{y_for(trade.entry_price):.2f}" r="5" class="entry" fill="#16a34a"/>'
        )
        parts.append(
            f'<circle cx="{x_for(exit_idx):.2f}" cy="{y_for(trade.exit_price):.2f}" r="5" class="stop" fill="#dc2626"/>'
        )
        parts.append(
            f'<text x="{margin}" y="{height-24}" class="small">Exit: {escape(trade.exit_reason)} | PnL: {trade.pnl:.6f}</text>'
        )
        draw_metadata_labels(parts, trade, margin + 8, 88)

    parts.append("</svg>")
    Path(path).write_text("\n".join(parts), encoding="utf-8")


def draw_level(parts: list[str], x1: float, x2: float, y: float, class_name: str, label: str) -> None:
    parts.append(f'<line x1="{x1}" y1="{y:.2f}" x2="{x2}" y2="{y:.2f}" class="{class_name}" stroke-dasharray="6 6"/>')
    parts.append(f'<text x="{x2 - 140}" y="{y - 6:.2f}" class="small">{escape(label)}</text>')


def draw_metadata_labels(parts: list[str], trade: TradeResult, x: float, y: float) -> None:
    labels = [
        ("1H center", trade.metadata.get("center_1h_macd_diag", "UNKNOWN")),
        ("A center", trade.metadata.get("center_A_macd_diag", "UNKNOWN")),
        ("b-A center", trade.metadata.get("center_bA_macd_diag", "UNKNOWN")),
        ("golden K low", trade.metadata.get("golden_k_low", "")),
        ("A b/a", f'{trade.metadata.get("b_length", "")}/{trade.metadata.get("a_length", "")}'),
        ("b-b/b-a", f'{trade.metadata.get("bb_length", "")}/{trade.metadata.get("ba_length", "")}'),
    ]
    for idx, (name, value) in enumerate(labels):
        parts.append(
            f'<text x="{x}" y="{y + idx * 18}" class="small">{escape(name)}: {escape(str(value))}</text>'
        )


def closest_bar_index(bars: list[Bar], time) -> int:
    return min(range(len(bars)), key=lambda index: abs(bars[index].time - time))


def empty_svg(title: str) -> str:
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="240"><text x="24" y="48">{escape(title)}: no data</text></svg>'


def escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
