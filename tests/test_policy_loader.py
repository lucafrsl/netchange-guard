from __future__ import annotations

from pathlib import Path

import pytest

from netchange_guard.models import ExpectedState
from netchange_guard.policy_loader import load_policies

VALID = """\
version: 1
policies:
  - id: allow_web
    description: Allow HTTPS
    start_location: edge
    source: 10.0.0.0/24
    destination: 10.1.0.10/32
    protocol: tcp
    destination_ports: [443]
    expected: allowed
"""


def write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def test_loads_valid_policy(tmp_path: Path) -> None:
    policies = load_policies(write(tmp_path / "policy.yml", VALID))
    assert len(policies) == 1
    assert policies[0].expected is ExpectedState.ALLOWED


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("- not-a-map", "must be a mapping"),
        ("version: 2\npolicies: []", "Unsupported"),
        ("version: 1\npolicies: []", "non-empty list"),
        ("version: 1\npolicies: [text]", "Each policy"),
        ("version: 1\npolicies: []\nextra: true", "contain only"),
    ],
)
def test_rejects_invalid_documents(tmp_path: Path, text: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        load_policies(write(tmp_path / "policy.yml", text))


def test_rejects_duplicate_ids(tmp_path: Path) -> None:
    duplicate = VALID + VALID.split("policies:\n", maxsplit=1)[1]
    with pytest.raises(ValueError, match="Duplicate policy ids"):
        load_policies(write(tmp_path / "policy.yml", duplicate))


def test_wraps_yaml_and_file_errors(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Cannot read"):
        load_policies(tmp_path / "missing.yml")
    with pytest.raises(ValueError, match="Cannot read"):
        load_policies(write(tmp_path / "bad.yml", "[unterminated"))
