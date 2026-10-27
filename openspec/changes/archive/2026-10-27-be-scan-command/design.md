# Design: be-scan-command

## 1. Overview

### Purpose
Make index building a deliberate, bounded, honest command.

### Scope
Orchestration over roots, a small CLI, and tests.

### Design Principles
Explicit operation. Bounded by configuration. Report partial results as partial. Application logic outside the CLI.

## 2. Context and Constraints

### Current State
Configuration loading, discovery, and run storage are separate, tested functions.

### Constraints
- Technical: Python 3.12+, standard library `argparse`.
- Security and privacy: roots only from configuration; discovery stays read-only.
- Reliability: one run per root; a failed root does not stop others.

### Existing Decisions and Conventions
Explicit operations; configuration format and location; index lifecycle and single writer.

### Knowledge References
- `knowledge/concepts/explicit-operations.md`
- `knowledge/decisions/configuration-file-format-and-location.md`
- `knowledge/decisions/index-lifecycle-and-single-writer.md`

## 3. Requirements and Traceability

| Requirement or Spec Reference | Design Element | Verification Approach |
|---|---|---|
| Only configured roots | `scan_workspace` loop | Outside-sibling fixture |
| First run creates | `open_index`, `created` flag | Temp `VYASA_HOME` |
| Each root reported | `format_report` | Output assertions |
| Exit code | `main` mapping | Parametrized outcomes |
| Repositories unchanged | read-only walk | Tree hash before and after |

## 4. Architecture and Design

### Architectural Approach
`scan_workspace` takes a loaded config and a writable connection and returns results. `main(argv, environ, out, err)` parses arguments, loads the configuration (mapping `NotConfigured` and `ConfigError` to exit 2 without creating anything), checks whether the index file exists to decide the "created" line, opens the index, scans, prints, and returns the exit code. A concurrent scan raises `OPERATION_IN_PROGRESS` from the first `store_run`, which maps to 3.

### Components and Responsibilities
| Component | Responsibility | Dependencies |
|---|---|---|
| `vyasa.application.indexing.scan` | multi-root orchestration, `RootResult` | discovery, store |
| `vyasa.adapters.cli.main` | arguments, report, exit codes | scan, configuration |
| `vyasa.__main__` | `python -m vyasa` | cli |

### Interfaces and Contracts
See `api-contract.md`.

### Key Workflows
Load config → open index → for each root: discover, store → report → exit code.

## 5. Data and State Management

Creates the data directory and index on first use via `open_index`.

## 6. Error Handling and Resilience

| Failure Scenario | Expected Behavior | Recovery or Mitigation |
|---|---|---|
| Root missing | Failed run recorded; others continue | Fix the path |
| Crash mid-scan | Stored work stays; run interrupted | Rerun |
| Concurrent scan | Exit 3 | Retry later |

## 7. Security and Privacy

Contract §5.

## 8. Quality Attributes

| Attribute | Requirement or Constraint | Design Response | Verification |
|---|---|---|---|
| Boundedness | Only configured roots | No path option | Sibling fixture |
| Honesty | Partial is not complete | Status and exit code | Exit-code tests |

## 9. Testing and Verification Strategy

### Behavioral Verification
One test per scenario.

### Test Strategy
Call `main` with an environment mapping and string streams over temporary roots; one test starts a second process holding the lock; one subprocess test runs `python -m vyasa scan`.

### Testability
`main` takes `environ`, `out`, and `err`.

### Verification Evidence
`pytest` output; a real scan of the owner's configured roots into a scratch data directory.

## 10. Implementation and Migration Considerations

### Implementation Order
Orchestration, report, exit codes, entry points.

### Migration and Rollout
None.

### Documentation and Operations
README section on `vyasa scan`.

## 11. Architecture Decision Checkpoint

- **New ADR required:** No — explicit-operations and the configuration decision apply; see `adr.md`.
