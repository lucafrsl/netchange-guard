# NetChange Guard report: candidate

- Generated (UTC): `2026-10-13T07:34:42.547865+00:00`
- Result: **FAIL**
- Policies passed: **3/4**

| Policy | Expected | Observed | Result | Evidence |
|---|---:|---:|---:|---:|
| `users_no_ssh_to_management` | denied | allowed | FAIL | 1 |
| `users_can_reach_internal_https` | allowed | allowed | PASS | 1 |
| `dmz_cannot_reach_management` | denied | denied | PASS | 0 |
| `dmz_can_reach_internal_api` | allowed | allowed | PASS | 1 |

## Policy details

### users_no_ssh_to_management

User workstations must not open SSH sessions to the management segment.

Observed: **allowed**; expected: **denied**.

### users_can_reach_internal_https

User workstations must reach the internal application over HTTPS.

Observed: **allowed**; expected: **allowed**.

### dmz_cannot_reach_management

DMZ workloads must not reach any management host over SSH.

Observed: **denied**; expected: **denied**.

### dmz_can_reach_internal_api

DMZ workloads may call the internal application only on its API port.

Observed: **allowed**; expected: **allowed**.
