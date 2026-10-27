# Design: be-identity-create-and-rescan

## 1. Overview

### Purpose
Make a project's identity independent of its path, so renames and moves keep one project.

### Scope
Matching, aliases, events, derived project state, and one migration. Not review flags, not root-commit identity.

### Design Principles
Create once, never recompute. Prefer recording over deciding: conflicts become events. Pure rules stay in the domain; SQL stays in the adapter.

## 2. Context and Constraints

### Current State
`projects.upsert` matches by `path_key` and writes the project state from its single checkout. `Candidate.remote.identity` is available and credential-free.

### Constraints
- Technical: Python 3.12+, `sqlite3`.
- Security and privacy: no Git execution; no URL or path in aliases or events.
- Performance and reliability: one transaction per project, as now.
- Compatibility: additive migration; `store_run` unchanged.

### Existing Decisions and Conventions
Stored identity with aliases; remote identity normalization; index lifecycle and single writer.

### Knowledge References
- `knowledge/concepts/project-identity.md`
- `knowledge/decisions/stored-identity-with-aliases.md`
- `knowledge/decisions/remote-identity-normalization.md`

## 3. Requirements and Traceability

| Requirement or Spec Reference | Design Element | Verification Approach |
|---|---|---|
| Identity is created once | `_create_project` | Persistence tests |
| Found by alias, then path | `_match` | Rescan, move, provisional-move tests |
| Later evidence becomes an alias | `_add_alias` | Remote added, renamed, removed tests |
| Conflicting evidence is preserved | conflict branch in `upsert` | Conflict test |
| Identity changes are recorded | `_event` | Event content test |
| Existing indexes are migrated | `0002_identity.sql` | Fixture index at schema 1 |

## 4. Architecture and Design

### Architectural Approach
Inside the per-project transaction, `upsert` reads the checkout by `path_key` and the alias by remote identity. The decision table is in the contract. After any checkout change a project's `state` is recomputed from its checkouts (`_refresh_state`), which `mark_absent` and `mark_inaccessible` also call, so one missing checkout does not hide an active one.

### Components and Responsibilities
| Component | Responsibility | Dependencies |
|---|---|---|
| `vyasa.domain.index` | identity status, source, and event constants | none |
| `migrations/0002_identity.sql` | columns, tables, backfill | none |
| `vyasa.adapters.sqlite.projects` | matching, aliases, events, derived state | `sqlite3` |
| `vyasa.application.indexing.store` | counts only | adapter |

### Interfaces and Contracts
See `api-contract.md`.

### Key Workflows
Candidate → alias lookup → path lookup → create / attach / update / conflict → refresh state → event if the mapping changed.

## 5. Data and State Management

Contract §6. Events are written only when the mapping changes, so an unchanged rescan adds none. The migration runs in the existing one-transaction runner.

## 6. Error Handling and Resilience

| Failure Scenario | Expected Behavior | Recovery or Mitigation |
|---|---|---|
| Failure inside a project's transaction | That project rolls back; the run is interrupted | Rerun |
| Alias and path disagree | Event only | Review in the ambiguity change |
| Migration backfill hits a duplicate remote | First checkout wins | Ambiguity change |

## 7. Security and Privacy

Aliases and events carry only the normalized identity. Paths remain in `checkouts`. Parameterized SQL.

## 8. Quality Attributes

| Attribute | Requirement or Constraint | Design Response | Verification |
|---|---|---|---|
| Stability | Identifier never changes | Created once; no update path | Tests compare ids across scenarios |
| Auditability | Mapping changes recorded | Event per change | Event tests |
| Integrity | Nothing deleted | No delete statements | Row-count tests |

## 9. Testing and Verification Strategy

### Behavioral Verification
One test per scenario.

### Test Strategy
Persistence tests on a real file; the migration test builds a schema 1 database by applying only `0001` and inserting rows.

### Testability
Clock and ids are injected where needed; run ids come from the test runs.

### Verification Evidence
`pytest` output, a real-workspace rescan with a simulated rename.

## 10. Implementation and Migration Considerations

### Implementation Order
Migration, create with identity, rediscovery, later evidence, conflict, derived state.

### Migration and Rollout
Automatic on open, with backup.

### Documentation and Operations
Update the decision; log entry.

## 11. Architecture Decision Checkpoint

- **New ADR required:** No — `knowledge/decisions/stored-identity-with-aliases.md` applies and is extended; see `adr.md`.
