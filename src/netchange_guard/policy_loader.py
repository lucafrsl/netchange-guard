"""Safe loading and validation of YAML policy files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from netchange_guard.models import FlowPolicy


def load_policies(path: Path) -> tuple[FlowPolicy, ...]:
    """Load a versioned policy file and reject malformed or ambiguous content."""

    try:
        raw: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ValueError(f"Cannot read policy file {path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValueError("Policy document must be a mapping")
    if set(raw) != {"version", "policies"}:
        raise ValueError("Policy document must contain only 'version' and 'policies'")
    if raw["version"] != 1:
        raise ValueError(f"Unsupported policy schema version: {raw['version']!r}")
    entries = raw["policies"]
    if not isinstance(entries, list) or not entries:
        raise ValueError("'policies' must be a non-empty list")
    if any(not isinstance(entry, dict) for entry in entries):
        raise ValueError("Each policy must be a mapping")
    policies = tuple(FlowPolicy.from_mapping(entry) for entry in entries)
    ids = [policy.policy_id for policy in policies]
    duplicates = sorted({policy_id for policy_id in ids if ids.count(policy_id) > 1})
    if duplicates:
        raise ValueError(f"Duplicate policy ids: {', '.join(duplicates)}")
    return policies
