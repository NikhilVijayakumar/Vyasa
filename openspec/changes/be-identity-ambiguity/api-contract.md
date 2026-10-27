# Interface and Data Contract: be-identity-ambiguity

- **OpenSpec Change ID:** `be-identity-ambiguity`
- **Proposing team:** be (backend team)
- **Related proposal:** `proposal.md`
- **Related specifications:** `specs/`
- **Related design:** `design.md`

## 1. Purpose

Fixes the review-flag table, its lifecycle, and the read function. No MCP tool, CLI command, or sync exchange is involved yet.

## 2. Scope

In: migration `0003`, `vyasa.adapters.sqlite.projects`, `vyasa.domain.index`. Out: MCP, CLI, Sheets, provider calls (not affected); `store_run` is unchanged.

## 3. Interface Surface

| Operation | Kind | Access | Input | Success output | Errors |
|---|---|---|---|---|---|
| `store_run(...)` | Python function | Writes | unchanged | unchanged | as before |
| `list_flags(connection, state="open")` | Python function | Read | `open`, `cleared`, or `None` for all | rows: project id, kind, state, evidence (JSON text), raised and cleared times, ordered by project id then kind | none |
| `list_projects(...)` | Python function | Read | unchanged | `identity_status` may now be `ambiguous` | none |

## 4. Error Model

No new error codes. Flags are data.

## 5. Trust Boundary

Inputs are trusted candidate fields. Evidence holds project ids, alias values, and counts only; no path, no URL. All SQL is parameterized. Flags are generated local state; reviewer decisions are not stored here.

## 6. Data Model

`review_flags`: `flag_id` INTEGER PK; `project_id` FK; `kind` (`duplicate_checkout`, `identity_unresolved`); `state` (`open`, `cleared`); `evidence` JSON text; `raised_at`; `cleared_at` (NULL while open); `run_id` FK (the run that last changed it, NULL when set by a migration). UNIQUE (`project_id`, `kind`).

`identity_events.kind` gains `flagged` and `resolved`; `detail` is `{"flag": "<kind>"}`.

Evidence: `duplicate_checkout` is `{"rule": "same_remote_identity", "aliases": [...sorted], "active_checkouts": n}`; `identity_unresolved` is `{"alias": a, "alias_owner": id, "path_project": id}`.

Invariants: a project has an open `duplicate_checkout` flag iff it has more than one active checkout; an open `identity_unresolved` flag iff its status is `ambiguous`; flags are never deleted; flag changes happen in the transaction that changed the evidence.

## 7. Migration and Compatibility

`0003_review_flags.sql`: create `review_flags`; rebuild `identity_events` with the wider CHECK, copying all rows with their ids; derive duplicate flags from current checkouts. Existing conflict events are not turned into flags: the cause (alias and path disagreement) is only visible at scan time, so the next scan raises them. Backup precedes it (runner).

## 8. Traceability

| Requirement | Operation / table |
|---|---|
| Duplicate checkouts are flagged | `review_flags`, derivation after checkout changes |
| Conflicting evidence makes identity ambiguous | `projects.identity_status`, `identity_unresolved` |
| Flags are idempotent and audited | unique key, `identity_events` |
| Existing indexes are migrated | `0003_review_flags.sql` |

## 9. Open Contract Questions

- [ ] Whether flags need a reviewer note field (Q15, `be-review-candidates`).
