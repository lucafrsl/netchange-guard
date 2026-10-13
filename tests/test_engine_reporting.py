from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from netchange_guard.engine import evaluate_snapshot
from netchange_guard.models import (
    ComparisonResult,
    ExpectedState,
    FlowPolicy,
    Observation,
    Protocol,
)
from netchange_guard.reporting import write_comparison_report, write_snapshot_reports


class FakeBackend:
    def __init__(self, reachable: dict[str, bool]) -> None:
        self.reachable = reachable
        self.loaded: tuple[Path, str] | None = None

    def load_snapshot(self, path: Path, name: str) -> None:
        self.loaded = (path, name)

    def observe(self, policy: FlowPolicy, snapshot: str) -> Observation:
        reachable = self.reachable[policy.policy_id]
        return Observation(reachable, int(reachable), "sample" if reachable else None)


def policies() -> tuple[FlowPolicy, ...]:
    return (
        FlowPolicy(
            "allow_web",
            "Allow web",
            "edge",
            "10.0.0.0/24",
            "10.1.0.10/32",
            Protocol.TCP,
            (443,),
            ExpectedState.ALLOWED,
        ),
        FlowPolicy(
            "deny_ssh",
            "Deny SSH",
            "edge",
            "10.0.0.0/24",
            "10.1.0.10/32",
            Protocol.TCP,
            (22,),
            ExpectedState.DENIED,
        ),
    )


def test_evaluate_and_write_reports(tmp_path: Path) -> None:
    backend = FakeBackend({"allow_web": True, "deny_ssh": False})
    result = evaluate_snapshot(backend, tmp_path, "baseline", policies())
    assert backend.loaded == (tmp_path, "baseline")
    assert result.passed and result.passed_count == 2

    instant = datetime(2026, 1, 2, 3, 4, tzinfo=UTC)
    json_path, markdown_path = write_snapshot_reports(result, tmp_path / "reports", instant)
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["summary"] == {"passed": 2, "total": 2}
    assert payload["generated_at"] == "2026-01-02T03:04:00+00:00"
    assert "Policies passed: **2/2**" in markdown_path.read_text(encoding="utf-8")


def test_comparison_identifies_new_regression(tmp_path: Path) -> None:
    baseline = evaluate_snapshot(
        FakeBackend({"allow_web": True, "deny_ssh": False}), tmp_path, "baseline", policies()
    )
    candidate = evaluate_snapshot(
        FakeBackend({"allow_web": True, "deny_ssh": True}), tmp_path, "candidate", policies()
    )
    comparison = ComparisonResult(baseline, candidate)
    assert comparison.regressions == ("deny_ssh",)
    path = write_comparison_report(comparison, tmp_path, datetime(2026, 1, 2, tzinfo=UTC))
    content = path.read_text(encoding="utf-8")
    assert "New regressions: **1**" in content
    assert "`deny_ssh`" in content


def test_comparison_report_handles_no_regressions(tmp_path: Path) -> None:
    result = evaluate_snapshot(
        FakeBackend({"allow_web": True, "deny_ssh": False}), tmp_path, "safe", policies()
    )
    path = write_comparison_report(
        ComparisonResult(result, result), tmp_path, datetime(2026, 1, 2, tzinfo=UTC)
    )
    assert "- None" in path.read_text(encoding="utf-8")
