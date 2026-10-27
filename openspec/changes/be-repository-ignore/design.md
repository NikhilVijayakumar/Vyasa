# Design: be-repository-ignore

## 1. Overview

### Purpose
Let a repository remove its own directories from scanning without being able to widen it.

### Scope
A pure parser and matcher, a bounded reader, and their use in the repository walk and the checkout walk.

### Design Principles
Untrusted input is bounded, parsed as text, and can only narrow. Pure logic in the domain. No platform branching.

## 2. Context and Constraints

### Current State
`find_repositories` and `walk_checkout` prune excluded names and links per directory.

### Constraints
- Technical constraints: Python 3.12+, standard library.
- Security and privacy constraints: at most 64 KiB read; no evaluation; patterns cannot leave the repository; evidence holds a digest, not text.
- Performance and reliability constraints: one bounded read per repository; compiled patterns.
- Compatibility and migration constraints: absent file means unchanged behavior.
- Operational constraints: tests pass on Windows and Linux.

### Existing Decisions and Conventions
Untrusted content; repository recognition and run status; file composition data and limits.

### Knowledge References
- `knowledge/decisions/repository-ignore-file.md` — format, bounds, trust.
- `knowledge/decisions/repository-recognition-and-run-status.md` — warnings do not change status.
- `knowledge/concepts/untrusted-content.md`.

## 3. Requirements and Traceability

| Requirement or Spec Reference | Design Element | Verification Approach |
|---|---|---|
| Patterns name directories | `parse_ignore`, `IgnoreRules.matches` | Table-driven unit tests |
| The file cannot widen the scan | validation in `parse_ignore` | Unit tests |
| The file is bounded | `read_ignore_file` and the pattern cap | Tests with large files |
| Discovery honors the file | rule stack in `find_repositories` | Tests on temp trees |
| Mistakes are reported | `ScanWarning` with `details` | Tests |
| File composition honors the file | `walk_checkout` and `compose` | Tests |
| Only the ignore file is read | single `open` site | Recording test |

## 4. Architecture and Design

### Architectural Approach
`parse_ignore` turns text into `IgnoreRules` (compiled regular expressions) plus problems. `read_ignore_file` reads at most 64 KiB + 1 byte and calls it. The repository walk keeps, per directory, the tuple of `(repository directory, rules)` inherited from its parents; finding a repository adds its own rules for everything below it. Before entering a child, each inherited rule set is asked about the child's path relative to its repository. `walk_checkout` takes optional rules for the checkout root.

### Components and Responsibilities
| Component | Responsibility | Dependencies |
|---|---|---|
| `vyasa.domain.ignore` | `IgnoreRules`, `parse_ignore`, limits | `re`, `hashlib` |
| `vyasa.adapters.filesystem.ignore_file` | `read_ignore_file` | domain |
| `vyasa.adapters.filesystem.repository_walk` | Rule stack; excluded count; problems | above |
| `vyasa.adapters.filesystem.checkout_walk` | Optional rules; ignored directories skipped | above |
| application `discovery` and `file_composition` | Warning and evidence | above |

### Interfaces and Contracts
See `api-contract.md`.

### Key Workflows
Walk → at a repository, read its rules → for each child: ignored by any inherited rule set → count as excluded; otherwise prune, depth, enter.

## 5. Data and State Management

No stored state. Rules are compiled once per repository. Glob translation: `**` becomes `.*`, `*` becomes `[^/]*`, `?` becomes `[^/]`, everything else is escaped; a pattern without a slash is matched against the last path segment, one with a slash against the whole relative path; matching is case-folded.

## 6. Error Handling and Resilience

| Failure Scenario | Expected Behavior | Recovery or Mitigation |
|---|---|---|
| Invalid line | Reported; skipped; the rest applies | Fix the file |
| Oversized file | Reported; skipped as a whole | Shrink the file |
| Unreadable file | Reported; no rules | Fix permissions |

## 7. Security and Privacy

Trust boundary as in the contract. A hostile file can hide only its own repository's directories. It cannot read, add, or point anywhere. No catastrophic matching: the translated expressions use only bounded character classes and `.*`, matched against short paths.

## 8. Quality Attributes

| Attribute | Requirement or Constraint | Design Response | Verification |
|---|---|---|---|
| Safety | Narrow only | Invalid forms rejected | Tests |
| Determinism | Same files give the same result | No ordering dependence | Existing repeat tests |

## 9. Testing and Verification Strategy

### Behavioral Verification
One test per scenario in the spec.

### Test Strategy
Pure unit tests for the parser and matcher; adapter tests with `tmp_path` for reading and bounds; discovery and composition tests on temp trees.

### Testability
Small inputs; limits are module constants that tests exceed with generated text.

### Verification Evidence
`pytest` output; skips reported.

## 10. Implementation and Migration Considerations

### Implementation Order
Domain, reader, discovery, composition.

### Migration and Rollout
None.

### Documentation and Operations
README gains a short `.vyasaignore` section.

## 11. Architecture Decision Checkpoint

- **New ADR required:** Yes — `knowledge/decisions/repository-ignore-file.md`; see `adr.md`.
