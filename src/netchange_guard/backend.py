"""Analysis backend abstraction and Batfish implementation."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol as TypingProtocol

from netchange_guard.models import FlowPolicy, Observation


class AnalysisBackend(TypingProtocol):
    """Minimal interface required by the policy evaluator."""

    def load_snapshot(self, path: Path, name: str) -> None:
        """Load a snapshot for later queries."""

    def observe(self, policy: FlowPolicy, snapshot: str) -> Observation:
        """Evaluate whether any matching flow succeeds."""


class BatfishBackend:
    """Run symbolic reachability queries against a Batfish service."""

    def __init__(self, host: str, network: str) -> None:
        from pybatfish.client.session import Session

        self._session = Session(host=host)
        self._session.set_network(network)

    def load_snapshot(self, path: Path, name: str) -> None:
        configs = path / "configs"
        if not path.is_dir() or not configs.is_dir() or not any(configs.iterdir()):
            raise ValueError(f"Invalid Batfish snapshot (missing non-empty configs/): {path}")
        if any(item.is_symlink() for item in path.rglob("*")):
            raise ValueError(f"Snapshot must not contain symbolic links: {path}")
        self._session.init_snapshot(str(path), name=name, overwrite=True)

    def observe(self, policy: FlowPolicy, snapshot: str) -> Observation:
        from pybatfish.datamodel import HeaderConstraints, PathConstraints

        ports = ",".join(str(port) for port in policy.destination_ports) or None
        headers = HeaderConstraints(
            srcIps=policy.source,
            dstIps=policy.destination,
            ipProtocols=[policy.protocol.value.upper()],
            dstPorts=ports,
        )
        answer = self._session.q.reachability(  # type: ignore[attr-defined]
            pathConstraints=PathConstraints(startLocation=policy.start_location),
            headers=headers,
            actions="SUCCESS",
            maxTraces=3,
        ).answer(snapshot=snapshot)
        frame = answer.frame()
        if frame.empty:
            return Observation(reachable=False, evidence_count=0)
        sample = str(frame.iloc[0].get("Flow", "matching flow"))
        return Observation(
            reachable=True,
            evidence_count=len(frame.index),
            sample=sample[:500],
        )
