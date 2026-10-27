# Design: be-review-candidates

## 1. Overview

### Purpose
Make flags explainable and let a reviewer record a judgment that stays on this machine.

### Scope
Catalogue, decision table, candidate view. Not obsolete rules, not any sync.

### Design Principles
Human-owned state is separate from scan-owned state. Explain with data, not prose assembled at query time. Never act on a decision.

## 2. Context and Constraints

### Current State
`review_flags` is written only by scans. `list_flags` returns raw rows.

### Constraints
- Technical: Python 3.12+, `sqlite3`.
- Security and privacy: local only; bounded note; parameterized SQL.
- Compatibility: additive migration.

### Existing Decisions and Conventions
Review decisions stay local; stored identity with aliases.

### Knowledge References
- `knowledge/decisions/review-decisions-stay-local.md`
- `knowledge/concepts/project-identity.md`

## 3. Requirements and Traceability

| Requirement or Spec Reference | Design Element | Verification Approach |
|---|---|---|
| Candidates are explainable | `RULES`, `list_candidates` | Unit and persistence tests |
| Decisions are stored locally | `decide` | Persistence tests |
| A decision holds only for its evidence | parsed-evidence comparison | Changed-evidence and reopen tests |
| Nothing is changed automatically | write-set test | Row snapshot before and after |
| Decisions are never shared | separate table, migration | Migration test |

## 4. Architecture and Design

### Architectural Approach
`decide` validates, loads the open flag, and upserts one `review_decisions` row with the flag's current evidence. `list_candidates` joins open flags to decisions, compares parsed JSON, and adds the catalogue entry. A snapshot test hashes all other tables before and after `decide`.

### Components and Responsibilities
| Component | Responsibility | Dependencies |
|---|---|---|
| `vyasa.domain.index` | `RULES`, decision statuses, error codes | none |
| `migrations/0004_review_decisions.sql` | table | none |
| `vyasa.adapters.sqlite.review` | `decide`, `list_candidates` | `sqlite3` |

### Interfaces and Contracts
See `api-contract.md`.

### Key Workflows
List candidates → reviewer decides → listing shows the decision until evidence changes.

## 5. Data and State Management

Contract §6.

## 6. Error Handling and Resilience

| Failure Scenario | Expected Behavior | Recovery or Mitigation |
|---|---|---|
| Invalid input | `INVALID_DECISION`, no write | Correct and retry |
| Flag cleared meanwhile | `CANDIDATE_NOT_FOUND` | List again |

## 7. Security and Privacy

Decisions never leave the machine; notes are bounded and never executed or interpreted.

## 8. Quality Attributes

| Attribute | Requirement or Constraint | Design Response | Verification |
|---|---|---|---|
| Safety | No automatic action | `decide` writes one table | Snapshot test |
| Explainability | Rule, criteria, evidence | Catalogue plus stored evidence | Listing tests |

## 9. Testing and Verification Strategy

### Behavioral Verification
One test per scenario.

### Test Strategy
Persistence tests on a real file using the existing helpers.

### Testability
Clock injected.

### Verification Evidence
`pytest` output.

## 10. Implementation and Migration Considerations

### Implementation Order
Migration, catalogue and listing, decide, evidence rule, safety.

### Migration and Rollout
Automatic on open, with backup.

### Documentation and Operations
Decision concept already created; log entry.

## 11. Architecture Decision Checkpoint

- **New ADR required:** Yes — `knowledge/decisions/review-decisions-stay-local.md`; see `adr.md`.
