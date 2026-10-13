# Contributing

Use only synthetic or fully sanitized network data. Never open a pull request containing credentials,
production configurations, internal addresses, customer names, or other confidential information.

1. Create a focused branch and describe the behavior being changed.
2. Add or update tests before changing a policy outcome.
3. Run `ruff check src tests`, `ruff format --check src tests`, `mypy src`, `pytest`, and `pip-audit`.
4. For analyzer changes, run the full Batfish demo and inspect parsing warnings and generated reports.
5. Keep `README.md` and `README.it.md`, and all paired documentation, semantically aligned.

Report security issues privately as described in `SECURITY.md` rather than opening a public issue.
