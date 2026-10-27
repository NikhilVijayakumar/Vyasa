# Change Proposal: be-repository-ignore

## Why

Directories inside a repository, such as reference data for coding agents, are skipped or counted for nothing, and Vyasa cannot know which to ignore. On a real workspace, 868 directories below the depth limit were skipped. This change lets a repository list what to skip in its own `.vyasaignore`, without letting that file widen what Vyasa reads.

## What Changes

- **repository-ignore**: parse a repository's `.vyasaignore` into bounded rules; apply them in repository discovery and in file composition counts; report invalid lines and oversized files in a warning.

## 1. Problem and Motivation

### Current Situation
Discovery walks inside repositories to find nested ones, and counts what it skips by the depth limit. File composition counts every file below a checkout except default exclusions.

### Problem
The owner of a repository knows which directories are noise. Vyasa has no way to be told, so the same directories are skipped, warned about, or counted on every run.

### Evidence
- Run of the discovery over `E:\Python` on 2026-10-27: 65 repositories, 1,178 directories skipped by policy, 868 of them at the depth limit.
- Owner decision 2026-10-27: the repository provides the ignore file, because Vyasa cannot know what to ignore.
- Requirement FR-022 in `docs/requirements/workspace-discovery/`.

## 2. Desired Outcome

### Goals
- [ ] A repository can remove directories from scanning with one file.
- [ ] The file can only narrow scanning and cannot reach outside its repository.
- [ ] Mistakes in the file are reported and do not stop the valid lines.
- [ ] Discovery and file composition honor the same rules.

### Team Focus
Changes are judged on MCP tool and interface contracts, data model, and trust boundaries; failure modes, data integrity, provenance of detected facts, and migration impact; and the verification layer that owns each behavior.

### Success Criteria
- [ ] Every scenario in `specs/repository-ignore/spec.md` has a passing test.
- [ ] The file is bounded to 64 KiB and 1,000 patterns.

## 3. Scope

### In Scope
- Parsing, matching, and bounds of `.vyasaignore`.
- Reading it at the root of each repository found, and at the checkout root for file composition.
- Warnings for invalid lines and oversized files; evidence of use (count and digest).

### Out of Scope
- Ignoring individual files, negation, and character classes in patterns.
- `.gitignore` support.
- A workspace-level ignore list in configuration (`be-discovery-boundaries`).

### Constraints
Standard library only. No branching on the operating system. The file is untrusted repository content.

## 4. Stakeholders and Impact

- **Primary stakeholders:** repository owners; the metadata detectors that will consume discovery.
- **Affected components or capabilities:** new `vyasa.domain.ignore`, an ignore-file reader, and changes to the repository walk, the checkout walk, and their application functions.
- **Dependencies:** `be-discover-one-root` and `be-file-composition-counts`.
- **Compatibility considerations:** repositories without the file behave as before.

## 5. Proposed Direction

A pure domain parser and matcher, a bounded reader, and a rule stack in the repository walk (each repository's rules apply below it, enclosing rules still apply to nested repositories). Durable choices are in `knowledge/decisions/repository-ignore-file.md`.

## 6. Requirements Overview

| ID | Requirement | Expected Outcome | Priority |
|---|---|---|---|
| REQ-001 | Parse patterns | Names, paths, `*`, `**`, `?`, comments | Must |
| REQ-002 | Cannot widen | Negation, absolute, `..` invalid | Must |
| REQ-003 | Bounded | 64 KiB and 1,000 patterns | Must |
| REQ-004 | Discovery honors it | Ignored directories counted as excluded | Must |
| REQ-005 | Nested repositories | Own file plus enclosing files | Must |
| REQ-006 | Mistakes reported | Warning; valid lines apply | Must |
| REQ-007 | File composition honors it | Evidence of use | Must |

## 7. Risks and Open Questions

### Risks
| Risk | Impact | Mitigation or Investigation |
|---|---|---|
| A hostile file hides directories | Less scanned | Only its own repository's directories; reported as excluded |
| Pattern language grows | Complexity | Only `*`, `**`, `?`; anything else is a literal |
| Second file read per repository | Slightly more I/O | One bounded read per repository |

### Assumptions
- Directory-only patterns cover the need; file ignoring can wait.

### Open Questions
- [ ] Whether to read `.gitignore` as a fallback later (not in this change).

## 8. Acceptance Summary

- [ ] All spec scenarios pass as automated tests.
- [ ] `python scripts/verify_workflows.py` shows no new failure.

## 9. Traceability

- **OpenSpec Change ID:** `be-repository-ignore`
- **Proposing team:** be (backend — the default workflow for this repository)
- **Proposed branch:** `feature/be-repository-ignore`
- **Requirement package:** `docs/requirements/workspace-discovery/requirement.md` (FR-022)
- **Knowledge references:** `knowledge/decisions/repository-ignore-file.md` — format, bounds, trust; `knowledge/decisions/repository-recognition-and-run-status.md` — outcomes and warnings; `knowledge/concepts/untrusted-content.md` — repository files are untrusted
- **Related issues or references:** None
- **Related existing specifications:** None
- **Related ADRs:** `knowledge/decisions/repository-ignore-file.md`

## 10. Readiness Review

- [x] The problem and motivation are clear.
- [x] Goals and success criteria are observable.
- [x] Scope and non-goals are explicit.
- [x] Important stakeholders, constraints, and dependencies are identified.
- [x] Assumptions and unresolved questions are visible.
- [x] The proposing team is identified and its focus and skills applied.
- [x] The proposal is consistent with existing specifications and project conventions.
- [ ] Significant ambiguities have been challenged and resolved (grill-me not yet run on this change).
- [x] The change has a stable OpenSpec ID and follows the project's Git discipline.

**Status:** Draft
