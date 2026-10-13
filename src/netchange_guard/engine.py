"""Policy evaluation orchestration."""

from __future__ import annotations

from pathlib import Path

from netchange_guard.backend import AnalysisBackend
from netchange_guard.models import FlowPolicy, PolicyResult, SnapshotResult


def evaluate_snapshot(
    backend: AnalysisBackend,
    snapshot_path: Path,
    snapshot_name: str,
    policies: tuple[FlowPolicy, ...],
) -> SnapshotResult:
    """Load one snapshot and evaluate every policy in declaration order."""

    backend.load_snapshot(snapshot_path, snapshot_name)
    results = tuple(
        PolicyResult(policy=policy, observation=backend.observe(policy, snapshot_name))
        for policy in policies
    )
    return SnapshotResult(name=snapshot_name, results=results)
