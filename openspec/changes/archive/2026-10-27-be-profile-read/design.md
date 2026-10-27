# Design: be-profile-read

## 1. Overview

### Purpose
Let a repository tell Vyasa what no scanner can know, safely.

### Scope
Pure validation, a bounded reader, storage per checkout, one query addition.

### Design Principles
Untrusted text is bounded and parsed, not evaluated. Validate per field. Declared is labelled declared. Read-only toward repositories.

## 2. Context and Constraints

### Current State
`Candidate` carries `remote`; the walk reads Git config the same way this reads the profile.

### Constraints
- Technical: Python 3.12+, `tomllib`.
- Security and privacy: no links, 64 KiB cap, no execution, no echo of file content in errors.
- Reliability: a bad profile never stops a scan.

### Existing Decisions and Conventions
Canonical profile and draft (format updated to TOML); untrusted content; read-only access policy.

### Knowledge References
- `knowledge/decisions/canonical-profile-and-draft.md`
- `knowledge/concepts/untrusted-content.md`
- `knowledge/concepts/field-ownership.md`

## 3. Requirements and Traceability

| Requirement or Spec Reference | Design Element | Verification Approach |
|---|---|---|
| The profile is read safely | `read_profile` | Temp-directory cases: link, large, malformed |
| Fields are validated one by one | `validate_profile` | Table tests |
| Declared values keep their source | `checkout_profiles`, `upsert` | Persistence tests |
| Project details show the profile | `get_project` | Query tests |

## 4. Architecture and Design

### Architectural Approach
`read_profile` checks `.vyasa` and the file are real (not links), reads at most 64 KiB, decodes UTF-8, parses with `tomllib`, and calls `validate_profile`. `validate_profile` handles each field independently and returns `ProfileResult`. The walk attaches the result when it creates an eligible candidate. `upsert` writes or replaces the checkout's profile row inside the project's transaction. `get_project` picks the profile row of the first active checkout with `valid` or `invalid` status (ordered by first seen), else the first checkout's row, else `absent`.

### Components and Responsibilities
| Component | Responsibility | Dependencies |
|---|---|---|
| `vyasa.domain.profile` | schema constants, `ProfileResult`, `validate_profile` | none |
| `vyasa.adapters.filesystem.profile_file` | `read_profile` | `tomllib` |
| `vyasa.domain.discovery.Candidate` | `profile` field | domain |
| `vyasa.adapters.filesystem.repository_walk` | attach | adapter |
| `migrations/0005_checkout_profiles.sql` | table | none |
| `vyasa.adapters.sqlite.projects` | store, load | `sqlite3` |
| `vyasa.application.query` | `profile` in `get_project` | adapter |

### Interfaces and Contracts
See `api-contract.md`.

### Key Workflows
Recognize a project → read profile → validate → attach → store → show in details.

## 5. Data and State Management

Contract §6.

## 6. Error Handling and Resilience

| Failure Scenario | Expected Behavior | Recovery or Mitigation |
|---|---|---|
| Link, oversize, malformed, unreadable | Status `unreadable`; scan continues | Fix the file |
| Invalid field | Kept others; problem listed | Fix the field |
| Unsupported version | Nothing kept | Update the profile |

## 7. Security and Privacy

Contract §5. Problem reasons are fixed strings.

## 8. Quality Attributes

| Attribute | Requirement or Constraint | Design Response | Verification |
|---|---|---|---|
| Safety | Scan changes nothing | Read-only | Tree hash |
| Robustness | Hostile files cannot stop a scan | Statuses, not exceptions | Hostile-file tests |
| Determinism | Same file, same result | Pure validation | Table tests |

## 9. Testing and Verification Strategy

### Behavioral Verification
One test per scenario.

### Test Strategy
Pure table tests for validation; temp-directory tests for the reader; discovery tests with profiles written into fixture repositories; persistence and query tests.

### Testability
Everything but the reader is pure or database-bound.

### Verification Evidence
`pytest` output; a real profile in a scratch repository scanned and queried over MCP.

## 10. Implementation and Migration Considerations

### Implementation Order
Domain validation, reader, discovery attach, storage, query.

### Migration and Rollout
Automatic on open, with backup.

### Documentation and Operations
Update the profile decision to TOML; log entry; README note.

## 11. Architecture Decision Checkpoint

- **New ADR required:** Yes — the profile decision is updated (TOML, per-field validation, MCP-guided filling); see `adr.md`.
