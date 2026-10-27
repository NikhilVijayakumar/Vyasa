# Change Proposal: openspec-okf-knowledge-rules

## Why

The knowledge bundle checks structure and links but not content shape. A decision can lack alternatives, a stable concept can carry unresolved questions, a deprecated decision can point nowhere, and delivery vocabulary can leak in. A review of a more mature OKF tree showed cheap rules that close these gaps.

## What Changes

- **knowledge-bundle-verification**: the verifier enforces per-type required sections, banned delivery words, no Open questions in a stable concept, and a replacement pointer on every deprecated decision, all configured in `knowledge/profile.json`.

## 1. Problem and Motivation

### Current Situation
`scripts/verify_knowledge.py` enforces frontmatter, folder per type, indexes, links, independence from delivery paths, and a 400-line cap. `knowledge/profile.json` carries the rules.

### Problem
Content-shape rules live only in reviewers' heads. The 18 decisions all happen to have Context, Decision, Alternatives considered, and Consequences, but nothing keeps the next one honest.

### Evidence
- Verified 2026-10-27: all 18 decisions carry the four headings; the bundle has no `# Open questions` sections and no hits for "this change", "ticket", "sprint", or "TODO" (grep over `knowledge/`).
- Reference reviewed 2026-10-27: an external OKF tree enforces required sections per kind, reserved Evidence and Open questions sections, immutable accepted decisions, and task-word bans.

## 2. Desired Outcome

### Goals
- [ ] A new concept that breaks a content-shape rule fails `verify_knowledge.py`.
- [ ] The rules are data in `profile.json`; the verifier holds no type-specific constants.
- [ ] The current bundle still verifies with zero errors.

### Team Focus
Changes are judged on MCP tool and interface contracts, data model, and trust boundaries; failure modes, data integrity, provenance of detected facts, and migration impact; and the verification layer that owns each behavior.

### Success Criteria
- [ ] `python3 scripts/verify_knowledge.py` reports 0 errors on the bundle after the profile gains the new keys.
- [ ] Unit tests cover each rule failing and passing.
- [ ] A profile without the new keys verifies as before.

## 3. Scope

### In Scope
- Profile keys `required_sections` and `forbidden_words`; frontmatter key `superseded_by`.
- Verifier checks and unit tests for the four rules.
- Knowledge: the Writing Knowledge practice and one draft decision (already added).
- One pointer line in the `knowledge-first` skill.

### Out of Scope
- Per-kind template catalogue, profiles per product type, layered link direction.
- Enforcing decision immutability (needs version history; stays a review rule).
- Evidence-dating checks (meaning tier, review only).

### Constraints
Standard library only. Python 3.12+. No machine-local data is involved.

## 4. Stakeholders and Impact

- **Primary stakeholders:** maintainers and agents writing knowledge.
- **Affected components or capabilities:** `scripts/verify_knowledge.py`, `scripts/test_verify_knowledge.py`, `knowledge/profile.json`, `skills/shared/knowledge-first/SKILL.md`.
- **Dependencies:** none; no MCP tool, index, or sync data is touched.
- **Compatibility considerations:** each new profile key is optional; a bundle without it verifies as before.

## 5. Proposed Direction

Add optional profile keys and small checks to the existing verifier, reusing `split_frontmatter` and the error and warning lists. Alternatives (full kind catalogue, warnings only) are recorded in `knowledge/decisions/knowledge-profile-section-rules.md`.

## 6. Requirements Overview

| ID | Requirement | Expected Outcome | Priority |
|---|---|---|---|
| REQ-001 | Required sections per type | A missing or empty section fails | Must |
| REQ-002 | Banned delivery words | A hit fails | Must |
| REQ-003 | Stable concepts have no Open questions | A stable concept with one fails | Must |
| REQ-004 | Deprecated decisions name a replacement | A missing or dangling pointer fails | Should |
| REQ-005 | Old profiles keep working | A missing key disables its check | Must |

## 7. Risks and Open Questions

### Risks
| Risk | Impact | Mitigation or Investigation |
|---|---|---|
| Word list flags legitimate prose | False errors | Patterns are narrow (`this change`, `this ticket`, `this sprint`, `TODO:`); the list is data in `profile.json` |
| Heading match is too literal | Valid concept fails | Match top-level `# Name`, case-insensitive, trimmed |

### Assumptions
- Existing decisions keep top-level `#` headings, as verified 2026-10-27.

### Open Questions
- [ ] Should `required_sections` later cover Practice and Runbook? Deferred; add per type in `profile.json` when needed.

## 8. Acceptance Summary

- [ ] Each requirement in `specs/knowledge-bundle-verification/spec.md` has a passing unit test.
- [ ] `python3 scripts/verify_workflows.py` passes.

## 9. Traceability

- **OpenSpec Change ID:** `openspec-okf-knowledge-rules`
- **Proposing team:** be (backend — the default workflow for this repository)
- **Proposed branch:** `feature/openspec-okf-knowledge-rules`
- **Requirement package:** None. Process change (`openspec-` prefix); the source is the review of an external OKF tree.
- **Knowledge references:** `knowledge/practices/writing-knowledge.md` — the rules as authored; `knowledge/decisions/knowledge-profile-section-rules.md` — why these and not more; `knowledge/technologies/okf.md` — the format.
- **Related issues or references:** None
- **Related existing specifications:** None
- **Related ADRs:** `knowledge/decisions/knowledge-profile-section-rules.md`

## 10. Readiness Review

- [x] The problem and motivation are clear.
- [x] Goals and success criteria are observable.
- [x] Scope and non-goals are explicit.
- [x] Important stakeholders, constraints, and dependencies are identified.
- [x] Assumptions and unresolved questions are visible.
- [x] The proposing team is identified and its focus and skills applied.
- [x] The proposal is consistent with existing specifications and project conventions.
- [x] Significant ambiguities have been challenged and resolved (`docs/reviews/okf-knowledge-rules-grill.md`).
- [x] The change has a stable OpenSpec ID and follows the project's Git discipline.

**Status:** Draft
