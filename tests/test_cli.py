from __future__ import annotations

from pathlib import Path

import pytest

from netchange_guard import cli
from netchange_guard.models import (
    ComparisonResult,
    ExpectedState,
    FlowPolicy,
    Observation,
    PolicyResult,
    Protocol,
    SnapshotResult,
)


def policy_file() -> Path:
    return Path(__file__).parents[1] / "policies" / "security.yml"


def snapshot(name: str, passed: bool) -> SnapshotResult:
    policy = FlowPolicy(
        "deny_ssh",
        "Deny SSH",
        "edge",
        "10.0.0.0/24",
        "10.1.0.10/32",
        Protocol.TCP,
        (22,),
        ExpectedState.DENIED,
    )
    return SnapshotResult(name, (PolicyResult(policy, Observation(not passed, 1)),))


def test_validate_command(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["validate", "--policies", str(policy_file())]) == 0
    assert "4 policies" in capsys.readouterr().out


def test_validate_command_reports_errors(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert cli.main(["validate", "--policies", str(tmp_path / "missing")]) == 1
    assert "error:" in capsys.readouterr().err


def test_demo_requires_one_caught_regression(monkeypatch: pytest.MonkeyPatch) -> None:
    comparison = ComparisonResult(snapshot("baseline", True), snapshot("candidate", False))
    monkeypatch.setattr(cli, "_evaluate_pair", lambda _args: comparison)
    args = ["demo", "--policies", str(policy_file())]
    assert cli.main(args) == 0


def test_compare_fails_on_candidate_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    comparison = ComparisonResult(snapshot("baseline", True), snapshot("candidate", False))
    monkeypatch.setattr(cli, "_evaluate_pair", lambda _args: comparison)
    args = [
        "compare",
        "--policies",
        str(policy_file()),
        "--baseline",
        "baseline",
        "--candidate",
        "candidate",
    ]
    assert cli.main(args) == 2
