# Design: be-workspace-config

## 1. Overview

### Purpose
Give discovery a trustworthy list of roots, or a clear reason there is none.

### Scope
Result types in the domain; locating, parsing, validating, and checking in one application module.

### Design Principles
Explicit, validated as a whole, fail closed (`knowledge/practices/configuration.md`). Standard library only. Platform differences live in one pure function whose inputs include the platform name.

## 2. Context and Constraints

### Current State
`src/vyasa` holds the file composition core. No configuration code exists.

### Constraints
- Technical constraints: Python 3.12+, `tomllib`.
- Security and privacy constraints: roots are machine-local; nothing is scanned or opened under a root; no credentials in the file.
- Performance and reliability constraints: one small file; one directory listing per root.
- Compatibility and migration constraints: none.
- Operational constraints: tests must pass on Windows and Linux alike.

### Existing Decisions and Conventions
Configuration practice; the data directory choice recorded in the local-index requirement.

### Knowledge References
- `knowledge/decisions/configuration-file-format-and-location.md` — format, order, outcomes.
- `knowledge/practices/configuration.md` — rules.
- `knowledge/architecture/scanning-and-evidence/discovery-and-inspection.md` — configured roots (§4.1).

## 3. Requirements and Traceability

| Requirement or Spec Reference | Design Element | Verification Approach |
|---|---|---|
| Locate the configuration file | `data_directory`, `_locate` | Unit tests with injected environment, home, platform |
| Load several workspace roots | `_roots` | Tests on temp files |
| Not configured | `NotConfigured` return | Tests |
| Invalid configuration is rejected as a whole | `ConfigError` with collected problems | Tests |
| Each root is checked on its own | `check_roots` | Tests on temp directories; unreadable via a patched `os.scandir` |

## 4. Architecture and Design

### Architectural Approach
`load_workspace_config` locates a file, reads it, parses it with `tomllib`, validates into a list of problems, and either raises one `ConfigError` or returns `WorkspaceConfig` or `NotConfigured`. `check_roots` is a separate pure-ish step so a caller can choose when to touch the disk.

### Components and Responsibilities
| Component | Responsibility | Dependencies |
|---|---|---|
| `vyasa.domain.workspace_config` | `WorkspaceConfig`, `NotConfigured`, `RootCheck`, `ConfigError` | stdlib |
| `vyasa.application.configuration.workspace` | `data_directory`, `load_workspace_config`, `check_roots` | domain, `tomllib`, `os` |

### Interfaces and Contracts
See `api-contract.md`.

### Key Workflows
Locate (explicit, then `VYASA_CONFIG`, then data directory) → read → parse → validate (collect problems) → normalize and de-duplicate → return.

## 5. Data and State Management

No stored state. Roots are normalized with `os.path.expanduser`, `os.path.normpath`, and compared with `os.path.normcase`, so case-insensitive file systems de-duplicate correctly without branching on the platform. Nesting is found by comparing `normcase`d parts. A path is "absolute" by `Path.is_absolute`, so a Windows path without a drive is rejected.

## 6. Error Handling and Resilience

| Failure Scenario | Expected Behavior | Recovery or Mitigation |
|---|---|---|
| Several problems | One `ConfigError` listing all | Fix the file |
| Default file absent | `NotConfigured` | Create the file |
| Explicit file absent | `ConfigError` | Fix the path |
| Root problem | That root's status only | Fix that root |

## 7. Security and Privacy

Trust boundary as in the contract. The file is validated before use and unknown keys are rejected, so a typo cannot silently widen or narrow scope. No root is created, scanned, or resolved through links. The loader never prints the whole file.

## 8. Quality Attributes

| Attribute | Requirement or Constraint | Design Response | Verification |
|---|---|---|---|
| Portability | Same behavior on Windows and Linux | Platform, home, and environment are inputs | Tests for all three layouts on any system |
| Usability | Fix all errors in one run | Collected problems | Test |

## 9. Testing and Verification Strategy

### Behavioral Verification
One test per scenario in `specs/workspace-configuration/spec.md`.

### Test Strategy
Unit tests with `pytest` and `tmp_path`. No real home or environment is read: tests pass them in.

### Testability
`environ`, `home`, and `platform` parameters default to the running process and are overridden in tests.

### Verification Evidence
`pytest` output; skips reported.

## 10. Implementation and Migration Considerations

### Implementation Order
Result types, `data_directory`, then load and validate, then `check_roots`.

### Migration and Rollout
None.

### Documentation and Operations
Add a short example configuration to the README.

## 11. Architecture Decision Checkpoint

- **New ADR required:** Yes — `knowledge/decisions/configuration-file-format-and-location.md`; see `adr.md`.
