"""Command-line interface for NetChange Guard."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from netchange_guard.backend import BatfishBackend
from netchange_guard.engine import evaluate_snapshot
from netchange_guard.models import ComparisonResult
from netchange_guard.policy_loader import load_policies
from netchange_guard.reporting import write_comparison_report, write_snapshot_reports


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="netchange-guard",
        description="Validate network changes against explicit reachability policies.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate", help="validate a policy YAML file")
    validate.add_argument("--policies", type=Path, required=True)

    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument("--policies", type=Path, required=True)
    shared.add_argument("--batfish-host", default="localhost")
    shared.add_argument("--network", default="netchange-guard")
    shared.add_argument("--report-dir", type=Path, default=Path("reports"))

    check = subparsers.add_parser("check", parents=[shared], help="evaluate one snapshot")
    check.add_argument("--snapshot", type=Path, required=True)
    check.add_argument("--name", required=True)

    compare = subparsers.add_parser("compare", parents=[shared], help="compare two snapshots")
    compare.add_argument("--baseline", type=Path, required=True)
    compare.add_argument("--candidate", type=Path, required=True)

    demo = subparsers.add_parser(
        "demo",
        parents=[shared],
        help="prove the baseline passes and the fixture regression is caught",
    )
    demo.add_argument("--baseline", type=Path, default=Path("snapshots/baseline"))
    demo.add_argument("--candidate", type=Path, default=Path("snapshots/candidate"))
    return parser


def _evaluate_pair(args: argparse.Namespace) -> ComparisonResult:
    policies = load_policies(args.policies)
    backend = BatfishBackend(host=args.batfish_host, network=args.network)
    baseline = evaluate_snapshot(backend, args.baseline, "baseline", policies)
    candidate = evaluate_snapshot(backend, args.candidate, "candidate", policies)
    write_snapshot_reports(baseline, args.report_dir)
    write_snapshot_reports(candidate, args.report_dir)
    comparison = ComparisonResult(baseline=baseline, candidate=candidate)
    write_comparison_report(comparison, args.report_dir)
    return comparison


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""

    args = _parser().parse_args(argv)
    try:
        if args.command == "validate":
            policies = load_policies(args.policies)
            print(f"Valid policy file: {len(policies)} policies")
            return 0
        if args.command == "check":
            policies = load_policies(args.policies)
            backend = BatfishBackend(host=args.batfish_host, network=args.network)
            result = evaluate_snapshot(backend, args.snapshot, args.name, policies)
            write_snapshot_reports(result, args.report_dir)
            print(f"{result.name}: {result.passed_count}/{len(result.results)} policies passed")
            return 0 if result.passed else 2

        comparison = _evaluate_pair(args)
        print(
            f"baseline={comparison.baseline.passed_count}/{len(comparison.baseline.results)} "
            f"candidate={comparison.candidate.passed_count}/{len(comparison.candidate.results)} "
            f"regressions={len(comparison.regressions)}"
        )
        if args.command == "demo":
            return 0 if comparison.baseline.passed and len(comparison.regressions) == 1 else 2
        return 0 if comparison.baseline.passed and comparison.candidate.passed else 2
    except (ConnectionError, OSError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
