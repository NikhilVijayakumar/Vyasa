# Design: be-git-remote

## 1. Overview

### Purpose
Say where each project's Git remote points without keeping what could be a secret.

### Scope
A pure parser and normalizer, a bounded reader, and the walk calling it.

### Design Principles
Untrusted text is bounded and parsed, not evaluated. The original URL is discarded at parse time. Pure logic in the domain. No platform branching.

## 2. Context and Constraints

### Current State
`classify_git_entry` and `_child_git` in `repository_walk` already find Git entries.

### Constraints
- Technical constraints: Python 3.12+, standard library.
- Security and privacy constraints: text only, at most 64 KiB, no links, no Git, no credentials kept.
- Performance and reliability constraints: one small read per project with Git.
- Compatibility and migration constraints: new fields default to `None`.
- Operational constraints: tests pass on Windows and Linux.

### Existing Decisions and Conventions
Remote identity normalization; read-only access and Git policy; untrusted content.

### Knowledge References
- `knowledge/decisions/git-remote-provider-labels.md`.
- `knowledge/decisions/remote-identity-normalization.md`.
- `knowledge/architecture/scanning-and-evidence/detector-inventory.md` (§9.2).

## 3. Requirements and Traceability

| Requirement or Spec Reference | Design Element | Verification Approach |
|---|---|---|
| Remotes are read from the config text | `parse_remotes` | Table-driven unit tests |
| URLs are reduced to a credential-free identity | `normalize_remote` | URL form table, credential checks |
| The provider comes from the host | provider table in the domain | Table tests |
| One remote is chosen | `choose_remote` | Unit tests |
| The config is read safely | `read_remote` | Temp-directory tests with large, linked, and pointer cases |
| Discovery attaches the remote | `repository_walk` | Discovery tests |

## 4. Architecture and Design

### Architectural Approach
`read_remote` checks that `.git` is a real directory and `config` a real file, reads at most 64 KiB, and calls `parse_remotes` then `choose_remote`. `choose_remote` normalizes only the chosen URL. The walk calls `read_remote` for a `.git` directory it classified as a repository and for the child folder holding a manifest project's Git.

### Components and Responsibilities
| Component | Responsibility | Dependencies |
|---|---|---|
| `vyasa.domain.git_remote` | `GitRemote`, `parse_remotes`, `normalize_remote`, `choose_remote`, provider table | `re` |
| `vyasa.adapters.filesystem.git_config` | `read_remote` | domain |
| `vyasa.domain.discovery` | `Candidate` fields | domain |
| `vyasa.adapters.filesystem.repository_walk` | Calls the reader | adapter |

### Interfaces and Contracts
See `api-contract.md`.

### Key Workflows
Recognize a project with Git → read its config → parse → choose → normalize the chosen URL → attach.

## 5. Data and State Management

No stored state. Normalization: if the URL has `://`, split scheme, authority, and path; `file` is local; strip user information; split host and port, dropping the scheme's default port. Otherwise a scp-style address (`user@host:path`, where host is more than one character) is rewritten; anything else, including a drive-letter path, is local. The path loses query, fragment, surrounding slashes, and a trailing `.git`.

## 6. Error Handling and Resilience

| Failure Scenario | Expected Behavior | Recovery or Mitigation |
|---|---|---|
| Unreadable or oversized config | Status `unavailable`; discovery continues | None needed |
| Odd URL | `other` or `local` | Add a case to the table |

## 7. Security and Privacy

Trust boundary as in the contract. Credentials are removed while parsing and never stored. A hostile config can only change which host a project is labelled with.

## 8. Quality Attributes

| Attribute | Requirement or Constraint | Design Response | Verification |
|---|---|---|---|
| Privacy | No credential kept | Only parsed parts are retained | Tests search every kept value |
| Determinism | Same config gives same result | Pure functions | Table tests |

## 9. Testing and Verification Strategy

### Behavioral Verification
One test per scenario in the spec.

### Test Strategy
Pure unit tests for parsing and normalizing (a table of forms); adapter tests with `tmp_path`; discovery tests with config files written into repositories.

### Testability
Everything but the reader is pure.

### Verification Evidence
`pytest` output; skips reported.

## 10. Implementation and Migration Considerations

### Implementation Order
Domain, reader, then the walk.

### Migration and Rollout
None.

### Documentation and Operations
None.

## 11. Architecture Decision Checkpoint

- **New ADR required:** Yes — `knowledge/decisions/git-remote-provider-labels.md`; see `adr.md`.
