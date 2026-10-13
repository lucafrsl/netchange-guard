"""Deterministic JSON and human-readable Markdown reports."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from netchange_guard.models import ComparisonResult, SnapshotResult


def _result_payload(result: SnapshotResult) -> dict[str, Any]:
    return {
        "snapshot": result.name,
        "passed": result.passed,
        "summary": {"passed": result.passed_count, "total": len(result.results)},
        "policies": [
            {
                "id": item.policy.policy_id,
                "description": item.policy.description,
                "expected": item.policy.expected.value,
                "observed": item.observed.value,
                "passed": item.passed,
                "evidence": asdict(item.observation),
            }
            for item in result.results
        ],
    }


def write_snapshot_reports(
    result: SnapshotResult, output_dir: Path, generated_at: datetime | None = None
) -> tuple[Path, Path]:
    """Write matching JSON and Markdown reports and return their paths."""

    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = (generated_at or datetime.now(UTC)).astimezone(UTC).isoformat()
    payload = _result_payload(result)
    payload["generated_at"] = timestamp
    json_path = output_dir / f"{result.name}.json"
    markdown_path = output_dir / f"{result.name}.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    status = "PASS" if result.passed else "FAIL"
    lines = [
        f"# NetChange Guard report: {result.name}",
        "",
        f"- Generated (UTC): `{timestamp}`",
        f"- Result: **{status}**",
        f"- Policies passed: **{result.passed_count}/{len(result.results)}**",
        "",
        "| Policy | Expected | Observed | Result | Evidence |",
        "|---|---:|---:|---:|---:|",
    ]
    for item in result.results:
        lines.append(
            f"| `{item.policy.policy_id}` | {item.policy.expected.value} | "
            f"{item.observed.value} | {'PASS' if item.passed else 'FAIL'} | "
            f"{item.observation.evidence_count} |"
        )
    lines.extend(["", "## Policy details", ""])
    for item in result.results:
        lines.extend(
            [
                f"### {item.policy.policy_id}",
                "",
                item.policy.description,
                "",
                f"Observed: **{item.observed.value}**; expected: **{item.policy.expected.value}**.",
                "",
            ]
        )
    markdown_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, markdown_path


def write_comparison_report(
    comparison: ComparisonResult, output_dir: Path, generated_at: datetime | None = None
) -> Path:
    """Write a concise regression-focused Markdown comparison."""

    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = (generated_at or datetime.now(UTC)).astimezone(UTC).isoformat()
    regressions = comparison.regressions
    lines = [
        "# NetChange Guard comparison",
        "",
        f"- Generated (UTC): `{timestamp}`",
        f"- Baseline: **{'PASS' if comparison.baseline.passed else 'FAIL'}**",
        f"- Candidate: **{'PASS' if comparison.candidate.passed else 'FAIL'}**",
        f"- New regressions: **{len(regressions)}**",
        "",
        "## Regressions",
        "",
    ]
    if regressions:
        lines.extend(f"- `{policy_id}`" for policy_id in regressions)
    else:
        lines.append("- None")
    path = output_dir / "comparison.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
