# Change Proposal: be-identity-ambiguity

## Why

When one repository is cloned twice, or when path and remote evidence disagree, the index records the facts but nothing tells a person to look. Vyasa needs deterministic review flags for duplicate checkouts and unresolved identity, and an `ambiguous` status that is returned as such instead of being guessed away.

## What Changes

- **identity-review**: a new capability. A `review_flags` table; a `duplicate_checkout` flag when a project has more than one active checkout; an `identity_unresolved` flag and `ambiguous` status when alias and path evidence conflict; `flagged` and `resolved` identity events.

## 1. Problem and Motivation

### Current Situation

`be-identity-create-and-rescan` groups checkouts that share a remote under one project and records an `identity_conflict` event when alias and path disagree. Nothing is raised for review, and `identity_status` is never `ambiguous`.

### Problem

A reviewer cannot list what needs a decision, and a consumer reading a conflicting project sees `resolved` (FR-003 S4, S5; FR-020 duplicate rule (a)).

### Evidence

- Verified: `identity_status` already allows `ambiguous`; conflicts and multiple active checkouts already occur in tests; no flag storage exists.
- Verified: grill Q7, Q8, Q9, Q13 are recommended or settled; the owner confirmed identity Q2, Q4, Q5, Q14 on 2026-10-27 and asked to proceed on the recommended direction.
- Assumption: Q7, Q8 and Q13 (a) are accepted as recommended; this proposal does not close the still-open Q15.

## 2. Desired Outcome

### Goals

- [ ] Flag duplicate checkouts with their rule and evidence.
- [ ] Mark conflicting identity `ambiguous` and flag it `identity_unresolved` with both pieces of evidence.
- [ ] Clear flags when the evidence no longer holds, and record that.
- [ ] Never merge, move, or delete because of a flag.

### Team Focus

Data model and invariants, failure modes, migration of an existing index, persistence-layer tests.

### Success Criteria

- [ ] Two active checkouts of one remote give one open flag; one active and one missing give none.
- [ ] A conflict makes the project `ambiguous`; fixing the evidence restores its status and clears the flag.
- [ ] Rescanning unchanged data adds no flag and no event.
- [ ] Flag evidence holds no path and no URL.

## 3. Scope

### In Scope

- Migration `0003`: `review_flags`; rebuild of `identity_events` to allow `flagged` and `resolved`.
- Deterministic flag derivation inside the existing per-project transactions.
- `list_flags`.

### Out of Scope

- Primary-checkout selection (needs configured root order, which the index does not hold).
- Duplicate rules (b) and (c), obsolete candidates, and where a reviewer's decision is stored (Q15); those are `be-review-candidates`.
- Root-commit identity, provider ids, forks.
- MCP and CLI surface.

### Constraints

Standard library; flags are generated state, never edited by a scan beyond open and clear; no deletes of rows other than the events table rebuild copying every row.

## 4. Stakeholders and Impact

- **Primary stakeholders:** the owner; later review and query work.
- **Affected components or capabilities:** `vyasa.adapters.sqlite.projects`, new migration, `vyasa.domain.index`.
- **Dependencies:** `be-local-index`, `be-identity-create-and-rescan` (merged).
- **Compatibility considerations:** schema 2 to 3 with backup; existing events are copied unchanged.

## 5. Proposed Direction

Recompute a project's flags whenever its checkouts or evidence change, in the same transaction. A flag row is unique per project and kind; opening sets it `open`, clearing sets it `cleared`; each transition writes an identity event. Considered: computing flags at query time (no history, repeats work) and storing a flag per checkout (hides the project-level problem).

## 6. Requirements Overview

| ID | Requirement | Expected Outcome | Priority |
|---|---|---|---|
| REQ-001 | Duplicate checkouts are flagged | rule and evidence | Must |
| REQ-002 | Conflicts are ambiguous and flagged | both evidences kept | Must |
| REQ-003 | Flags clear when evidence clears | status restored | Must |
| REQ-004 | Flags are idempotent and audited | no repeat rows or events | Must |
| REQ-005 | Existing indexes migrate | events kept | Must |

## 7. Risks and Open Questions

### Risks

| Risk | Impact | Mitigation or Investigation |
|---|---|---|
| Events table rebuild loses rows | Audit gap | Copy in one transaction with a backup; test counts |
| A flag hides a real merge need | Reviewer overlooks | Flags are listed and never auto-resolved |

### Assumptions

- Active checkouts of one project share a remote identity (that is how they were grouped).

### Open Questions

- [ ] Primary checkout rule once root order is stored.

## 8. Acceptance Summary

- [ ] Every spec scenario has a test against a real database file.
- [ ] `pytest`, `verify_workflows.py`, `verify_knowledge.py`, `openspec validate` pass.

## 9. Traceability

- **OpenSpec Change ID:** `be-identity-ambiguity`
- **Proposing team:** be (backend — the default workflow for this repository)
- **Proposed branch:** `feature/be-identity-ambiguity`
- **Requirement package:** `docs/requirements/project-identity/requirement.md`
- **Knowledge references:**
  - `knowledge/concepts/project-identity.md` — ambiguity is preserved and flagged
  - `knowledge/decisions/stored-identity-with-aliases.md` — conflict handling, events (extended)
  - `knowledge/decisions/partial-results-never-imply-absence.md` — flags are not cleared by absence
- **Related issues or references:** None
- **Related existing specifications:** `openspec/specs/project-identity`, `openspec/specs/local-index`
- **Related ADRs:** `knowledge/decisions/stored-identity-with-aliases.md`

## 10. Readiness Review

- [x] The problem and motivation are clear.
- [x] Goals and success criteria are observable.
- [x] Scope and non-goals are explicit.
- [x] Important stakeholders, constraints, and dependencies are identified.
- [x] Assumptions and unresolved questions are visible.
- [x] The proposing team is identified and its focus and skills applied.
- [x] The proposal is consistent with existing specifications and project conventions.
- [x] Significant ambiguities have been challenged and resolved, or explicitly recorded.
- [x] The change has a stable OpenSpec ID and follows the project's Git discipline.

**Status:** Ready for specification and design
