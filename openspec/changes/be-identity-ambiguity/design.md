# Design: be-identity-ambiguity

## 1. Overview

### Purpose
Surface identity problems for a person, deterministically and without acting on them.

### Scope
Two flag kinds, the `ambiguous` status, their events, and one migration.

### Design Principles
Record, do not decide. Derive flags from stored facts inside the transaction that changed them. Pure constants in the domain; SQL in the adapter.

## 2. Context and Constraints

### Current State
`projects.upsert` records `identity_conflict` events and groups checkouts; `refresh_state` derives project state from checkouts.

### Constraints
- Technical: Python 3.12+, `sqlite3`.
- Security and privacy: evidence without paths or URLs.
- Reliability: flag changes commit with the evidence change.
- Compatibility: additive migration; event rows preserved.

### Existing Decisions and Conventions
Stored identity with aliases; index lifecycle and single writer.

### Knowledge References
- `knowledge/concepts/project-identity.md`
- `knowledge/decisions/stored-identity-with-aliases.md`

## 3. Requirements and Traceability

| Requirement or Spec Reference | Design Element | Verification Approach |
|---|---|---|
| Duplicate checkouts are flagged | `_sync_duplicate` | Two clones, moved, removed, same-name tests |
| Conflicting evidence makes identity ambiguous | conflict branch, `_raise` | Conflict, repaired, absence tests |
| Flags are idempotent and audited | `_raise`, `_clear`, unique key | Repeat, reopen, listing tests |
| Existing indexes are migrated | `0003_review_flags.sql` | Schema 2 fixture |

## 4. Architecture and Design

### Architectural Approach
`_raise(project, kind, evidence)` inserts or reopens the flag and writes `flagged` only when the row was absent, cleared, or its evidence changed. `_clear(project, kind)` clears an open flag and writes `resolved`. `sync_duplicates` runs at the end of `store_run`, after absent checkouts are marked, over the projects the run touched and those with an open duplicate flag, so a move inside one run never flags. The conflict branch sets `ambiguous` and raises `identity_unresolved`. A non-conflicting rescan of an `ambiguous` project restores `resolved` (has aliases) or `provisional` and clears the flag. A run that omits the checkout touches nothing, so ambiguity survives absence.

### Components and Responsibilities
| Component | Responsibility | Dependencies |
|---|---|---|
| `vyasa.domain.index` | flag kinds and states | none |
| `migrations/0003_review_flags.sql` | table, events rebuild, derived duplicates | none |
| `vyasa.adapters.sqlite.projects` | derivation, `list_flags` | `sqlite3` |

### Interfaces and Contracts
See `api-contract.md`.

### Key Workflows
Evidence change → refresh state → sync duplicate flag → (conflict) set ambiguous and raise → events.

## 5. Data and State Management

Contract §6. Evidence is stored with sorted keys and sorted aliases so equal evidence compares equal and repeated scans write nothing.

## 6. Error Handling and Resilience

| Failure Scenario | Expected Behavior | Recovery or Mitigation |
|---|---|---|
| Failure mid-transaction | Flag and evidence roll back together | Rerun |
| Migration copy fails | Rolled back; backup remains | Reopen |

## 7. Security and Privacy

Evidence and events hold ids, aliases, and counts. Parameterized SQL.

## 8. Quality Attributes

| Attribute | Requirement or Constraint | Design Response | Verification |
|---|---|---|---|
| Determinism | Same data, same flags | Derived from stored state; sorted evidence | Repeat-scan test |
| Safety | No automatic merge or delete | No such statements | Row-count tests |

## 9. Testing and Verification Strategy

### Behavioral Verification
One test per scenario.

### Test Strategy
Persistence tests on a real file; the migration test builds schema 2 with the real migrations 1 and 2.

### Testability
Run helpers from the existing tests.

### Verification Evidence
`pytest` output; real-workspace double-clone check.

## 10. Implementation and Migration Considerations

### Implementation Order
Migration, duplicate flag, conflict flag, repair, listing.

### Migration and Rollout
Automatic on open, with backup.

### Documentation and Operations
Extend the identity decision; log entry.

## 11. Architecture Decision Checkpoint

- **New ADR required:** No — `knowledge/decisions/stored-identity-with-aliases.md` applies and is extended; see `adr.md`.
