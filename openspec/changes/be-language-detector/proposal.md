# Change Proposal: be-language-detector

## Why

FR-023 asks Vyasa to report the programming languages of a checkout with a status that says how each was found. File composition already counts code files by extension but cannot say which language they are, so an agent cannot tell a Python project from a Rust one without opening it. This change adds a language detector on the same bounded walk.

## What Changes

- **language-detection**: a library core that classifies code files into one language label each from versioned data (`files_detected`), records languages declared by recognized manifest file names (`declared`), keeps the two separate, and returns a completeness marker and evidence. The file-type data gains a `languages` map and a `manifests` map.

## 1. Problem and Motivation

### Current Situation
`compose` (FR-021) returns code, documentation, and other counts from `src/vyasa/data/file_types.json` (version 1: code and documentation extension lists). No language is named anywhere in the code. The requirement package `docs/requirements/language-detection/` is grilled and its recommendations are confirmed by the owner (2026-10-27).

### Problem
FR-023 cannot be verified. The file-composition requirement already promises that the code count equals the sum of a language histogram, and nothing produces that histogram.

### Evidence
- `src/vyasa/application/scanning/file_composition.py` and `src/vyasa/data/file_types.json` (verified 2026-10-27): code extensions are one flat list with no label.
- `docs/requirements/file-composition/features/grill-additions.feature` scenario "One walk for languages and counts".
- The inventory (§9.3) requires the output meaning to be stated and the evidence types kept distinguishable.

## 2. Desired Outcome

### Goals
- [ ] A function returns, per checkout, `files_detected` counts per language and a set of `declared` languages.
- [ ] The `files_detected` counts sum to the `compose` code count on the same tree.
- [ ] A partial walk never reports a language as absent.

### Team Focus
Changes are judged on MCP tool and interface contracts, data model, and trust boundaries; failure modes, data integrity, provenance of detected facts, and migration impact; and the verification layer that owns each behavior.

### Success Criteria
- [ ] Every scenario in `specs/language-detection/spec.md` has a passing test.
- [ ] Fixtures cover a mixed tree, a manifest-only tree, `.h` and unknown types, a tree over the entry cap, and shuffled directory order.
- [ ] The histogram sum equals the code count on every fixture.

## 3. Scope

### In Scope
- Extending the file-type data (version 2) with `languages` (extension to label) and `manifests` (file name to label), and validating them.
- `detect_languages(root, types, limits, exclusions, clock)` over the existing bounded walk, and its result types.

### Out of Scope
- Reading file or manifest content; versions, dependencies, frameworks (framework detector, §9.4).
- Persistence, MCP tools, project details, and the language search filter (`be-language-query`).
- Synchronization of languages (machine-local in phase 1).

### Constraints
Standard library only. Python 3.12+. File content is never read; no path is returned.

## 4. Stakeholders and Impact

- **Primary stakeholders:** maintainers and agents that will query projects.
- **Affected components or capabilities:** `vyasa.domain` (new module), `vyasa.application.scanning` (new module, loader extended), `vyasa/data/file_types.json`.
- **Dependencies:** the existing walk adapter and `compose`; none new.
- **Compatibility considerations:** `compose` is unchanged. The loader accepts version 1 data (no languages) and rejects a languages map that disagrees with `code_extensions`.

## 5. Proposed Direction

A pure domain function maps the walked file names to label counts and declared labels; an application function walks once and calls it. The data stays one file so extension lists cannot drift. Alternatives (merged status, content-based resolution, manifest parsing) are rejected in `knowledge/decisions/language-evidence-statuses.md`.

## 6. Requirements Overview

| ID | Requirement | Expected Outcome | Priority |
|---|---|---|---|
| REQ-001 | Files detected by extension | Counts per label from the table | Must |
| REQ-002 | Histogram agrees with the code count | Sum equals `compose` code count | Must |
| REQ-003 | Declared by manifest presence | Label per recognized manifest name | Must |
| REQ-004 | Statuses stay separate | Two results for a language found both ways | Must |
| REQ-005 | Unknown ignored, shared extension one label | Nothing guessed | Must |
| REQ-006 | Partial walk | Absence reported unknown | Must |
| REQ-007 | Evidence and validated data | Table version and completeness; bad data rejected | Must |

## 7. Risks and Open Questions

### Risks
| Risk | Impact | Mitigation or Investigation |
|---|---|---|
| Two lists (`code_extensions`, `languages`) drift | Histogram does not sum to the code count | Loader rejects data where `languages` keys differ from `code_extensions`; a test pins it |
| Coarse labels (`.h`, markup) mislead | Overstated precision | Labels are documented in the data; content-based refinement is deferred |
| Nested manifests in a monorepo | `declared` is checkout-wide, not per package | Documented; per-directory results are deferred |

### Assumptions
- A manifest anywhere in the walked tree declares its language for the checkout.
- Matching a manifest name is case-insensitive.

### Open Questions
- [ ] None blocking. `*.csproj` (a pattern, not a name) is not recognized in this change.

## 8. Acceptance Summary

- [ ] All spec scenarios pass as automated tests.
- [ ] `python scripts/verify_workflows.py` shows no new failure.

## 9. Traceability

- **OpenSpec Change ID:** `be-language-detector`
- **Proposing team:** be (backend — the default workflow for this repository)
- **Proposed branch:** `feature/be-language-detector`
- **Requirement package:** `docs/requirements/language-detection/requirement.md`
- **Knowledge references:** `knowledge/architecture/scanning-and-evidence/detector-inventory.md` — §9.3 detector; `knowledge/decisions/language-evidence-statuses.md` — statuses and fixed table; `knowledge/decisions/file-composition-data-and-limits.md` — shared data and walk; `knowledge/decisions/partial-results-never-imply-absence.md` — partial results; `knowledge/practices/vertical-slices.md` — slicing
- **Related issues or references:** None
- **Related existing specifications:** `openspec/specs/file-composition` (unchanged)
- **Related ADRs:** `knowledge/decisions/language-evidence-statuses.md`

## 10. Readiness Review

- [x] The problem and motivation are clear.
- [x] Goals and success criteria are observable.
- [x] Scope and non-goals are explicit.
- [x] Important stakeholders, constraints, and dependencies are identified.
- [x] Assumptions and unresolved questions are visible.
- [x] The proposing team is identified and its focus and skills applied.
- [x] The proposal is consistent with existing specifications and project conventions.
- [x] Significant ambiguities have been challenged and resolved (`docs/requirements/language-detection/grill-log.md`).
- [x] The change has a stable OpenSpec ID and follows the project's Git discipline.

**Status:** Ready for specification and design
