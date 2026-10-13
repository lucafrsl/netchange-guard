from __future__ import annotations

import pytest

from netchange_guard.models import ExpectedState, FlowPolicy, Observation, PolicyResult, Protocol


def make_policy(**overrides: object) -> FlowPolicy:
    values: dict[str, object] = {
        "policy_id": "allow_web",
        "description": "Allow web traffic",
        "start_location": "edge",
        "source": "10.0.0.0/24",
        "destination": "10.1.0.10/32",
        "protocol": Protocol.TCP,
        "destination_ports": (443,),
        "expected": ExpectedState.ALLOWED,
    }
    values.update(overrides)
    return FlowPolicy(**values)  # type: ignore[arg-type]


def test_result_passes_when_observation_matches() -> None:
    result = PolicyResult(make_policy(), Observation(True, 1, "flow"))
    assert result.passed
    assert result.observed is ExpectedState.ALLOWED


def test_denied_result_passes_when_no_flow_is_found() -> None:
    result = PolicyResult(make_policy(expected=ExpectedState.DENIED), Observation(False, 0))
    assert result.passed
    assert result.observed is ExpectedState.DENIED


@pytest.mark.parametrize(
    ("override", "message"),
    [
        ({"policy_id": "BAD"}, "Invalid policy id"),
        ({"description": " "}, "description cannot be empty"),
        ({"start_location": "bad location"}, "invalid start_location"),
        ({"source": "invalid"}, "invalid source"),
        ({"destination": "invalid"}, "invalid destination"),
        ({"destination_ports": ()}, "requires destination_ports"),
        ({"destination_ports": (0,)}, "between 1 and 65535"),
        ({"destination_ports": (443, 443)}, "duplicate destination port"),
        (
            {"protocol": Protocol.ICMP, "destination_ports": (443,)},
            "ICMP cannot specify",
        ),
    ],
)
def test_policy_rejects_invalid_values(override: dict[str, object], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        make_policy(**override)


def test_from_mapping_rejects_unknown_and_missing_keys() -> None:
    with pytest.raises(ValueError, match="Missing policy keys"):
        FlowPolicy.from_mapping({"id": "some_id"})
    raw = {
        "id": "some_id",
        "description": "test",
        "start_location": "edge",
        "source": "10.0.0.0/24",
        "destination": "10.1.0.0/24",
        "protocol": "tcp",
        "destination_ports": [443],
        "expected": "allowed",
        "extra": True,
    }
    with pytest.raises(ValueError, match="Unknown policy keys"):
        FlowPolicy.from_mapping(raw)


def test_from_mapping_requires_integer_port_list() -> None:
    raw = {
        "id": "some_id",
        "description": "test",
        "start_location": "edge",
        "source": "10.0.0.0/24",
        "destination": "10.1.0.0/24",
        "protocol": "tcp",
        "destination_ports": "443",
        "expected": "allowed",
    }
    with pytest.raises(ValueError, match="list of integers"):
        FlowPolicy.from_mapping(raw)
