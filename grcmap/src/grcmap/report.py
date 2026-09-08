"""JSON and Markdown report generation.

Every report ends with the same disclaimer sentence, deliberately: this
tool computes coverage/gap indicators from a self-declared control
inventory and reviewer-asserted mappings, not a certification, audit
opinion, or regulatory compliance determination.
"""

from __future__ import annotations

import json
from dataclasses import asdict

from .gaps import summarize
from .models import GapResult

DISCLAIMER = (
    "Coverage findings are readiness indicators computed from a self-declared control "
    "inventory and reviewer-asserted mappings -- they are NOT a certification, audit "
    "opinion, or ISO/PCI/SBP compliance determination."
)


def _table_cell(text: str, max_len: int) -> str:
    """Flatten a value for a single Markdown table cell: collapse
    embedded newlines/whitespace (a raw newline inside a cell breaks
    table rendering) and truncate with an ASCII ellipsis (an unicode
    "..." character mojibakes on a legacy-codepage Windows console).
    """
    flat = " ".join(text.split())
    if len(flat) > max_len:
        flat = flat[: max_len - 3] + "..."
    return flat


def gap_results_to_json(framework_id: str, results: list[GapResult]) -> str:
    payload = {
        "framework": framework_id,
        "disclaimer": DISCLAIMER,
        "summary": summarize(results),
        "requirements": [asdict(r) for r in results],
    }
    return json.dumps(payload, indent=2, default=str)


def gap_results_to_markdown(framework_id: str, framework_title: str, results: list[GapResult]) -> str:
    lines: list[str] = []
    lines.append(f"# Gap Analysis: {framework_title}")
    lines.append("")
    lines.append(f"> {DISCLAIMER}")
    lines.append("")

    summary = summarize(results)
    lines.append("## Summary")
    lines.append("")
    lines.append("| Status | Count |")
    lines.append("|---|---:|")
    for status, count in summary.items():
        lines.append(f"| {status} | {count} |")
    lines.append("")

    lines.append("## Requirements")
    lines.append("")
    lines.append("| ID | Title | Status | Contributing Controls |")
    lines.append("|---|---|---|---|")
    for r in sorted(results, key=lambda r: r.requirement_id):
        controls = ", ".join(r.contributing_controls) if r.contributing_controls else "-"
        title = _table_cell(r.requirement_title, max_len=80)
        note = f" ({_table_cell(r.justification, max_len=120)})" if r.justification else ""
        lines.append(f"| {r.requirement_id} | {title} | {r.status.value}{note} | {controls} |")

    lines.append("")
    return "\n".join(lines)
