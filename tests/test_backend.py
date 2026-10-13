from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from netchange_guard.backend import BatfishBackend
from netchange_guard.models import ExpectedState, FlowPolicy, Protocol


class Row:
    def get(self, key: str, default: str) -> str:
        return "example-flow" if key == "Flow" else default


class Indexer:
    def __getitem__(self, index: int) -> Row:
        assert index == 0
        return Row()


class Frame:
    def __init__(self, empty: bool) -> None:
        self.empty = empty
        self.index = [] if empty else [0, 1]
        self.iloc = Indexer()


class Answer:
    def __init__(self, empty: bool) -> None:
        self.empty = empty

    def frame(self) -> Frame:
        return Frame(self.empty)


class Question:
    def __init__(self, session: FakeSession) -> None:
        self.session = session

    def answer(self, *, snapshot: str) -> Answer:
        self.session.answer_snapshot = snapshot
        return Answer(self.session.empty)


class Questions:
    def __init__(self, session: FakeSession) -> None:
        self.session = session

    def reachability(self, **kwargs: Any) -> Question:
        self.session.query = kwargs
        return Question(self.session)


class FakeSession:
    latest: FakeSession | None = None

    def __init__(self, *, host: str) -> None:
        self.host = host
        self.network = ""
        self.empty = False
        self.query: dict[str, Any] = {}
        self.answer_snapshot = ""
        self.snapshots: list[tuple[str, str, bool]] = []
        self.q = Questions(self)
        FakeSession.latest = self

    def set_network(self, network: str) -> None:
        self.network = network

    def init_snapshot(self, path: str, *, name: str, overwrite: bool) -> None:
        self.snapshots.append((path, name, overwrite))


def policy() -> FlowPolicy:
    return FlowPolicy(
        "allow_web",
        "Allow HTTPS",
        "edge",
        "10.0.0.0/24",
        "10.1.0.10/32",
        Protocol.TCP,
        (443,),
        ExpectedState.ALLOWED,
    )


def backend(monkeypatch: pytest.MonkeyPatch) -> BatfishBackend:
    monkeypatch.setattr("pybatfish.client.session.Session", FakeSession)
    return BatfishBackend("batfish.local", "test-network")


def test_load_snapshot_and_observe_reachable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    analyzer = backend(monkeypatch)
    configs = tmp_path / "configs"
    configs.mkdir()
    (configs / "router.cfg").write_text("hostname router", encoding="utf-8")
    analyzer.load_snapshot(tmp_path, "baseline")
    session = FakeSession.latest
    assert session is not None
    assert session.host == "batfish.local" and session.network == "test-network"
    assert session.snapshots == [(str(tmp_path), "baseline", True)]

    observation = analyzer.observe(policy(), "baseline")
    assert observation.reachable and observation.evidence_count == 2
    assert observation.sample == "example-flow"
    assert session.answer_snapshot == "baseline"
    assert session.query["actions"] == "SUCCESS"


def test_observe_unreachable(monkeypatch: pytest.MonkeyPatch) -> None:
    analyzer = backend(monkeypatch)
    session = FakeSession.latest
    assert session is not None
    session.empty = True
    assert not analyzer.observe(policy(), "candidate").reachable


def test_rejects_invalid_snapshot(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    analyzer = backend(monkeypatch)
    with pytest.raises(ValueError, match="Invalid Batfish snapshot"):
        analyzer.load_snapshot(tmp_path, "bad")
