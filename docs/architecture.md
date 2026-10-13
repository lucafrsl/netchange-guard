# Architecture

## Requirements and decisions

NetChange Guard must analyze sanitized configuration snapshots without device credentials, express
intent in a reviewable format, produce repeatable evidence, and fail closed on invalid input. The
implementation is intentionally a small orchestration layer around Batfish rather than a new routing
simulator: protocol semantics remain the responsibility of the mature analysis engine.

The YAML schema is deliberately narrow. Each policy describes one source location, source/destination
IPv4 space, protocol, destination-port set, and expected state. Narrow input reduces ambiguity and
makes review practical. Supporting arbitrary Batfish expressions is out of scope because that would
expose a much larger, harder-to-validate language surface.

## Components and flow

1. `policy_loader` decodes YAML with `safe_load`, checks the document version and rejects unknown
   fields, duplicate IDs, malformed prefixes, and invalid ports.
2. `BatfishBackend` initializes a named network, loads an offline snapshot, and translates each
   policy into `HeaderConstraints` and `PathConstraints`.
3. `engine` evaluates policies independently so a result maps directly to one business invariant.
4. `reporting` emits equivalent JSON and Markdown views.
5. `cli` exposes validation, single-snapshot checks, strict comparison, and the self-testing demo.

## Exit-code contract

| Code | Meaning |
|---:|---|
| 0 | Requested verification succeeded |
| 1 | Input, connection, filesystem, or operational error |
| 2 | Analysis completed and at least one required policy condition failed |

## Alternatives considered

- **Direct packet replay:** valuable for selected examples but cannot cover the complete header space.
- **Custom routing/ACL parser:** rejected because duplicating vendor semantics would create misleading
  confidence and a large maintenance burden.
- **Live device collection:** rejected to keep the project zero-cost, safe, and free of credentials.

## Extension points

The backend protocol allows a different analyzer without changing policy evaluation. Schema versioning
permits future IPv6, transit-node, or failure-scenario fields without silently changing version 1.
