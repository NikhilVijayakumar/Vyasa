# Design: be-discover-one-root

## 1. Overview

### Purpose
Find repositories under one root safely and explain everything that was not found.

### Scope
Domain types, a filesystem adapter, an application function, and two small refactors for reuse.

### Design Principles
Dependencies point toward the domain. Standard library only. A filesystem problem is part of the result, never an exception. No platform branching: links and junctions are handled with `os.path.islink` and `os.path.isjunction`, which exist everywhere.

## 2. Context and Constraints

### Current State
`checkout_walk` already prunes links, junctions, and excluded names. `check_roots` already classifies a root.

### Constraints
- Technical constraints: Python 3.12+, standard library.
- Security and privacy constraints: nothing is run; only `.git` pointer files (at most 1 KiB) are opened; paths stay in the local record.
- Performance and reliability constraints: depth-bounded sorted walk; no entry or time bound yet (see the proposal's risks).
- Compatibility and migration constraints: refactors keep behavior.
- Operational constraints: tests pass on Windows and Linux.

### Existing Decisions and Conventions
Scan limits and symlink defaults; read-only access and Git policy; partial results never imply absence.

### Knowledge References
- `knowledge/decisions/repository-recognition-and-run-status.md` — recognition, outcomes, status.
- `knowledge/architecture/scanning-and-evidence/discovery-and-inspection.md` — roots, nesting, exclusions, links, outcomes.
- `knowledge/decisions/read-only-access-and-git-policy.md` — nothing is run.

## 3. Requirements and Traceability

| Requirement or Spec Reference | Design Element | Verification Approach |
|---|---|---|
| Recognize Git repositories | `classify_git_entry` | Tests on temp trees |
| Nested repositories stay separate | the walk continues below a repository | Test |
| Every candidate has one closed outcome | `Candidate` and the adapter | Tests, including a patched `os.scandir` and `open` |
| Traversal boundaries | `prune` in the adapter | Tests with real links, a junction on Windows |
| Run status | `discover_repositories` | Tests |
| Run record | `DiscoveryRun` | Tests with injected clock and id |
| Nothing is executed or read beyond pointers | no subprocess; `open` only for pointers | A test that records every opened path |

## 4. Architecture and Design

### Architectural Approach
`discover_repositories` checks the root with the shared root check, calls the adapter, counts outcomes, bounds the issue list, decides the status, and builds the record. The adapter walks with `os.walk(topdown=True, followlinks=False)`, looks for `.git` in the raw directory and file lists before pruning, classifies it, then prunes.

### Components and Responsibilities
| Component | Responsibility | Dependencies |
|---|---|---|
| `vyasa.domain.discovery` | Types, constants, `DISCOVERY_EXCLUSIONS` | stdlib |
| `vyasa.adapters.filesystem.pruning` | `prune(dirpath, dirnames, excluded)` returning kept, excluded count, linked names | `os` |
| `vyasa.adapters.filesystem.repository_walk` | Walk, `classify_git_entry`, findings | domain, pruning |
| `vyasa.adapters.filesystem.checkout_walk` | Uses `prune` (refactor) | pruning |
| `vyasa.application.configuration.workspace` | Exposes `check_root` (refactor) | domain |
| `vyasa.application.scanning.discovery` | `discover_repositories` | the above |

### Interfaces and Contracts
See `api-contract.md`.

### Key Workflows
Check root → walk: at each directory, recognize a project (`.git`, then a manifest); a project is recorded and, by default, not entered; otherwise drop `.git` from the names; prune; at the depth limit report each remaining directory as skipped and do not enter → count, bound, status → record.

## 5. Data and State Management

No stored state. The record is a frozen value. Counts are computed from the findings so the invariants in the contract hold by construction. A directory unreadable during the walk is reported through `os.walk`'s error callback with the path from the error.

## 6. Error Handling and Resilience

| Failure Scenario | Expected Behavior | Recovery or Mitigation |
|---|---|---|
| Root problem | Failed run with a reason | Fix the root |
| Unreadable directory | Issue and partial; walk continues | Fix permissions |
| Bad `.git` | Issue and partial; walk continues | Repair the repository |
| Many issues | Listed up to the bound; counted in full | Raise `max_issues` |

## 7. Security and Privacy

Trust boundary as in the contract. The only file opened is a `.git` pointer, read as at most 1 KiB of text and parsed for one line. No subprocess is created. Links and junctions are never entered, so listing cannot leave the root. The record holds absolute paths and stays local.

## 8. Quality Attributes

| Attribute | Requirement or Constraint | Design Response | Verification |
|---|---|---|---|
| Determinism | Same tree gives the same record contents | Sorted traversal; stable counts | Repeat and reversed-order tests |
| Portability | Same behavior on Windows and Linux | No platform branch | Tests run on Windows; link tests skip with a reason where links cannot be made |
| Safety | Nothing run, nothing read beyond pointers | No subprocess; one `open` site | Recording test |

## 9. Testing and Verification Strategy

### Behavioral Verification
One test per scenario in the spec.

### Test Strategy
Unit and adapter tests with `pytest` and `tmp_path`. A helper builds repositories as `.git/HEAD`. Unreadable cases patch `os.scandir` and `builtins.open` for a specific path. No integration or persistence layer exists.

### Testability
`now` and `new_id` are injected. `options` carries small limits.

### Verification Evidence
`pytest` output; skips reported.

## 10. Implementation and Migration Considerations

### Implementation Order
Refactor (prune, `check_root`) with existing tests green, then types, adapter, application function.

### Migration and Rollout
None.

### Documentation and Operations
README unchanged until there is a command to run.

## 11. Architecture Decision Checkpoint

- **New ADR required:** Yes — `knowledge/decisions/repository-recognition-and-run-status.md`; see `adr.md`.
