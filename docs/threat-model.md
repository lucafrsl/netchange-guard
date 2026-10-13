# Threat model

## Assets and trust boundaries

Assets are the integrity of policy decisions, confidentiality of imported configurations, report
accuracy, and CI availability. Untrusted inputs are YAML policy files, configuration snapshots,
container images, and dependency packages. The Batfish service is trusted only to analyze supplied
synthetic data; it is not exposed beyond the local host in the intended lab.

## Threats and mitigations

| Threat | Impact | Mitigation |
|---|---|---|
| Malformed or ambiguous policy | Incorrect approval | Strict schema, safe YAML loader, unknown-key and duplicate rejection |
| Snapshot path containing symlinks | Analyze unintended local data | Reject every symlink beneath a snapshot |
| Missing/unsupported vendor semantics | False confidence | Parse warnings reviewed during verification; limitations documented |
| Committed secrets or production configs | Confidentiality loss | Synthetic fixtures, `.gitignore`, secret-scanning workflow, review guidance |
| Compromised dependency/image | Code execution | Exact Python versions, dependency audit, automated update review; container isolation |
| Stale or falsified report | Incorrect decision | Regenerate in CI; include snapshot name, timestamp, counts, and machine-readable result |
| Denial of service from large inputs | CI exhaustion | Intended for reviewed snapshots; resource limits and size limits are future hardening |

## Residual risks

The Batfish model may not implement a configuration feature or may differ from a device release.
Reports demonstrate declared intent against the supplied model, not runtime state. Container images
are third-party executable content. The Compose setup binds Batfish only to loopback, but it remains
appropriate for a trusted local lab rather than a shared server.
