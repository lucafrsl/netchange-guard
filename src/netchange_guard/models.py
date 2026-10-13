"""Validated domain models for policy-driven network checks."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from ipaddress import ip_network
from typing import Any


class ExpectedState(StrEnum):
    """Reachability state required by a policy."""

    ALLOWED = "allowed"
    DENIED = "denied"


class Protocol(StrEnum):
    """Supported IP protocols."""

    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"


_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{2,63}$")
_LOCATION_PATTERN = re.compile(r"^[A-Za-z0-9_@.()[\]/,:*+?-]{1,128}$")


@dataclass(frozen=True, slots=True)
class FlowPolicy:
    """One business intent expressed as a constrained packet flow."""

    policy_id: str
    description: str
    start_location: str
    source: str
    destination: str
    protocol: Protocol
    destination_ports: tuple[int, ...]
    expected: ExpectedState

    def __post_init__(self) -> None:
        if not _ID_PATTERN.fullmatch(self.policy_id):
            raise ValueError(f"Invalid policy id: {self.policy_id!r}")
        if not self.description.strip():
            raise ValueError(f"Policy {self.policy_id}: description cannot be empty")
        if not _LOCATION_PATTERN.fullmatch(self.start_location):
            raise ValueError(f"Policy {self.policy_id}: invalid start_location")
        for field_name, value in (("source", self.source), ("destination", self.destination)):
            try:
                ip_network(value, strict=False)
            except ValueError as exc:
                raise ValueError(
                    f"Policy {self.policy_id}: invalid {field_name} {value!r}"
                ) from exc
        if self.protocol in {Protocol.TCP, Protocol.UDP} and not self.destination_ports:
            raise ValueError(f"Policy {self.policy_id}: TCP/UDP requires destination_ports")
        if self.protocol is Protocol.ICMP and self.destination_ports:
            raise ValueError(f"Policy {self.policy_id}: ICMP cannot specify destination_ports")
        if any(port < 1 or port > 65535 for port in self.destination_ports):
            raise ValueError(f"Policy {self.policy_id}: port must be between 1 and 65535")
        if len(set(self.destination_ports)) != len(self.destination_ports):
            raise ValueError(f"Policy {self.policy_id}: duplicate destination port")

    @classmethod
    def from_mapping(cls, raw: dict[str, Any]) -> FlowPolicy:
        """Build and validate a policy from decoded YAML."""

        required = {
            "id",
            "description",
            "start_location",
            "source",
            "destination",
            "protocol",
            "destination_ports",
            "expected",
        }
        unknown = set(raw) - required
        missing = required - set(raw)
        if missing:
            raise ValueError(f"Missing policy keys: {', '.join(sorted(missing))}")
        if unknown:
            raise ValueError(f"Unknown policy keys: {', '.join(sorted(unknown))}")
        ports = raw["destination_ports"]
        if not isinstance(ports, list) or any(not isinstance(port, int) for port in ports):
            raise ValueError("destination_ports must be a list of integers")
        return cls(
            policy_id=str(raw["id"]),
            description=str(raw["description"]),
            start_location=str(raw["start_location"]),
            source=str(raw["source"]),
            destination=str(raw["destination"]),
            protocol=Protocol(str(raw["protocol"]).lower()),
            destination_ports=tuple(ports),
            expected=ExpectedState(str(raw["expected"]).lower()),
        )


@dataclass(frozen=True, slots=True)
class Observation:
    """Reachability returned by an analysis backend."""

    reachable: bool
    evidence_count: int
    sample: str | None = None


@dataclass(frozen=True, slots=True)
class PolicyResult:
    """Evaluation outcome for a policy in one snapshot."""

    policy: FlowPolicy
    observation: Observation

    @property
    def passed(self) -> bool:
        expected_reachable = self.policy.expected is ExpectedState.ALLOWED
        return self.observation.reachable is expected_reachable

    @property
    def observed(self) -> ExpectedState:
        return ExpectedState.ALLOWED if self.observation.reachable else ExpectedState.DENIED


@dataclass(frozen=True, slots=True)
class SnapshotResult:
    """All policy results for a named snapshot."""

    name: str
    results: tuple[PolicyResult, ...]

    @property
    def passed(self) -> bool:
        return all(result.passed for result in self.results)

    @property
    def passed_count(self) -> int:
        return sum(result.passed for result in self.results)


@dataclass(frozen=True, slots=True)
class ComparisonResult:
    """Baseline and candidate results plus newly introduced failures."""

    baseline: SnapshotResult
    candidate: SnapshotResult

    @property
    def regressions(self) -> tuple[str, ...]:
        baseline_by_id = {item.policy.policy_id: item for item in self.baseline.results}
        return tuple(
            item.policy.policy_id
            for item in self.candidate.results
            if not item.passed and baseline_by_id[item.policy.policy_id].passed
        )
