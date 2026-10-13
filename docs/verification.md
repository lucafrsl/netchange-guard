# Verification record

Date: **2026-10-13**
Environment: Windows host, Python 3.11.9, Docker Engine 29.8.2
Analyzer: Batfish 2026.08.27.3685, PyBatfish 2026.9.17.3748

This record distinguishes executed checks from workflow definitions. Every result below was observed
locally against the files in version 0.1.0; no production network or cloud resource was involved.

| Check | Command/tool | Observed result |
|---|---|---|
| Policy schema | `netchange-guard validate --policies policies/security.yml` | 4 valid policies |
| Lint | `ruff check src tests` | Passed |
| Formatting | `ruff format --check src tests` | 12 files already formatted |
| Static typing | `mypy src` | No issues in 7 source files |
| Unit tests | `pytest` | 31 passed |
| Coverage gate | pytest-cov | 93.41%; required minimum 90% |
| Dependency audit | `pip-audit --progress-spinner off` | No known vulnerabilities; the local unpublished package is not on PyPI and was skipped |
| Secret scan | Gitleaks 8.30.0 directory scan | 47 deliverable files / 74.79 KB scanned; no leaks found |
| Batfish demo | `netchange-guard demo ...` | Baseline 4/4; candidate 3/4; exactly 1 regression detected |
| Parser integrity | Batfish `fileParseStatus` and `parseWarning` | All 6 configuration files `PASSED`; 0 warnings |
| Compose validation | `docker compose config --quiet` | Passed |

## Observed policy results

| Policy | Baseline | Candidate |
|---|---:|---:|
| `users_no_ssh_to_management` | PASS (denied) | FAIL (allowed) |
| `users_can_reach_internal_https` | PASS (allowed) | PASS (allowed) |
| `dmz_cannot_reach_management` | PASS (denied) | PASS (denied) |
| `dmz_can_reach_internal_api` | PASS (allowed) | PASS (allowed) |

The generated JSON and Markdown evidence is stored under `reports/`.

## Not yet executed

GitHub-hosted workflows cannot be reported as passed until the repository is published and Actions
runs them. Their definitions are present under `.github/workflows/`; this record makes no claim about
an external CI run.
