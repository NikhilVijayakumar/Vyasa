# Change Proposal: be-discover-one-root

## Why

Vyasa needs to find the Git repositories under a configured workspace root, say what happened to every candidate, and keep a record of the run, without running Git or trusting what it reads. This change does that for one root, as a library function on top of the configuration and file composition work.

## What Changes

- **repository-discovery**: walk one root within a depth limit and default exclusions without following links; recognize Git repositories from their marker; give every candidate one outcome from a closed set; return a run record with status, counts, and a bounded list of issues.

## 1. Problem and Motivation

### Current Situation
`be-workspace-config` returns the configured roots and their accessibility. `be-file-composition-counts` counts files in a checkout. Nothing finds the checkouts.

### Problem
Without discovery there are no projects to describe. A naive scan can run repository code, follow a link out of the root, or report a scan as complete when parts were skipped.

### Evidence
- FR-002 and FR-015 scenarios in `docs/requirements/workspace-discovery/features/`.
- Grill answers Q4 (nested repositories), Q5 (depth, default exclusions), Q6 (links not followed), Q9 (closed outcome set), Q10 (run record), Q12 (no network), Q13 (no repository-controlled execution).

## 2. Desired Outcome

### Goals
- [ ] The repositories under a root are returned in a stable order.
- [ ] Every non-repository result is explained by an outcome and a reason code.
- [ ] A run says `complete`, `partial`, or `failed`, and warns about what was skipped and what to do.
- [ ] Nothing is executed and no repository file other than a `.git` pointer is opened.

### Team Focus
Changes are judged on MCP tool and interface contracts, data model, and trust boundaries; failure modes, data integrity, provenance of detected facts, and migration impact; and the verification layer that owns each behavior.

### Success Criteria
- [ ] Every scenario in `specs/repository-discovery/spec.md` has a passing test.
- [ ] Two runs over an unchanged tree return the same repositories and counts.

## 3. Scope

### In Scope
- Recognition of repositories, submodules, and linked worktrees from `.git`.
- Outcomes: eligible, excluded, inaccessible, malformed, skipped by policy.
- Depth limit 8 (owner decision 2026-10-27), default exclusions, links and junctions not followed.
- The in-memory run record.
- Reuse of the root check from `be-workspace-config` and a shared directory-pruning helper.

### Out of Scope
- Several roots at once, overlap between roots, and deduplication by real path.
- Non-Git projects and markers (DFR-003, undecided).
- Configurable exclusions, limits, and symlink following (`be-discovery-boundaries`).
- Persisting runs, run history, and retention (`local-index`).
- Identity, metadata, remotes, and any use of Git commands.

### Constraints
Standard library only. No branching on the operating system. Roots and paths stay local; the run record is not sent anywhere.

## 4. Stakeholders and Impact

- **Primary stakeholders:** the identity and metadata changes that consume the repositories.
- **Affected components or capabilities:** new `vyasa.domain.discovery`, a repository walk adapter, and an application function; a small refactor of the checkout walk and the root check.
- **Dependencies:** `be-workspace-config` (root check) and `be-file-composition-counts` (walk helper), both on this branch's ancestry.
- **Compatibility considerations:** the refactors keep existing behavior and are covered by existing tests.

## 5. Proposed Direction

Pure domain types, a filesystem adapter that walks and recognizes, and an application function that checks the root, runs the walk, bounds the issue list, and assembles the record. Durable choices are in `knowledge/decisions/repository-recognition-and-run-status.md`.

## 6. Requirements Overview

| ID | Requirement | Expected Outcome | Priority |
|---|---|---|---|
| REQ-001 | Recognize repositories | Directory and file `.git` forms, kinds | Must |
| REQ-002 | Outcomes | One closed outcome per candidate | Must |
| REQ-003 | Boundaries | Depth, exclusions, links not followed | Must |
| REQ-004 | Nested repositories | Separate candidates, not merged | Must |
| REQ-005 | Run status | Failed, partial on failures only, else complete; skips are warnings | Must |
| REQ-006 | Run record | Id, root, times, counts, bounded issues | Must |
| REQ-007 | Safety | Nothing run; only `.git` pointers opened | Must |

## 7. Risks and Open Questions

### Risks
| Risk | Impact | Mitigation or Investigation |
|---|---|---|
| Skipped directories inside repositories are numerous (3,132 at depth 6 on a real workspace) | Noise | They are summarized in warnings with advice and never change the status; a repository's `.vyasaignore` removes them |
| No entry or time bound on the walk | A huge root is slow | Depth bounds it now; limits arrive with `be-discovery-boundaries` |
| `.git` file classification by path segment is heuristic | A rare layout is mislabelled | The kind is advisory; identity resolution decides |

### Assumptions
- The depth of 8 below the root is the owner's default: his repositories sit at most 3 levels below a root, so 8 leaves margin.

### Open Questions
- [ ] Package Q8 recommends dropping a root nested inside another with a warning; `be-workspace-config` keeps and reports it. Resolved when several roots run together.

## 8. Acceptance Summary

- [ ] All spec scenarios pass as automated tests.
- [ ] `python scripts/verify_workflows.py` shows no new failure.

## 9. Traceability

- **OpenSpec Change ID:** `be-discover-one-root`
- **Proposing team:** be (backend — the default workflow for this repository)
- **Proposed branch:** `feature/be-discover-one-root`
- **Requirement package:** `docs/requirements/workspace-discovery/requirement.md` (FR-002, FR-015)
- **Knowledge references:** `knowledge/decisions/repository-recognition-and-run-status.md` — recognition, outcomes, status; `knowledge/architecture/scanning-and-evidence/discovery-and-inspection.md` — roots, nesting, exclusions, links, outcomes (§4); `knowledge/decisions/scan-limits-and-symlink-defaults.md` — depth and links; `knowledge/decisions/read-only-access-and-git-policy.md` — nothing is run
- **Related issues or references:** None
- **Related existing specifications:** None
- **Related ADRs:** `knowledge/decisions/repository-recognition-and-run-status.md`

## 10. Readiness Review

- [x] The problem and motivation are clear.
- [x] Goals and success criteria are observable.
- [x] Scope and non-goals are explicit.
- [x] Important stakeholders, constraints, and dependencies are identified.
- [x] Assumptions and unresolved questions are visible.
- [x] The proposing team is identified and its focus and skills applied.
- [x] The proposal is consistent with existing specifications and project conventions.
- [x] Significant ambiguities have been challenged and resolved (`docs/reviews/config-and-discovery-grill.md`); two decisions await the owner.
- [x] The change has a stable OpenSpec ID and follows the project's Git discipline.

**Status:** Draft
