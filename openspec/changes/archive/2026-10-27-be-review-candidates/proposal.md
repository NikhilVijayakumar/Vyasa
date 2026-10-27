# Change Proposal: be-review-candidates

## Why

Review flags exist but a person cannot say "I looked at this", and a flag does not explain itself. Vyasa needs local reviewer decisions that never touch a project, and a candidate view that shows each flag's rule, confidence, criteria, and evidence, so duplicates are explainable and no flag leads to automatic action.

## What Changes

- **review-candidates**: a new capability. A local `review_decisions` table; `decide` and `list_candidates`; a rule catalogue giving each flag kind a rule id, confidence tier, and plain criteria; a guarantee that no scan or decision modifies, archives, or deletes a project.

## 1. Problem and Motivation

### Current Situation

`be-identity-ambiguity` raises `duplicate_checkout` and `identity_unresolved` flags (`list_flags`). They carry evidence but no rule id, confidence, or criteria text, and a reviewer's judgment is not stored.

### Problem

FR-020 S4 and S5 are unmet: a flag is not explainable on its own, and a human decision has nowhere to live. Without it, a dismissed flag returns unchanged forever.

### Evidence

- Verified: `review_flags` and `list_flags` exist; no decision storage.
- Verified: owner decided on 2026-10-27 that phase 1 is entirely local and reviewer decisions are always local, never synchronized or shown in Google Sheets (Q15).
- Verified: no source of declared lifecycle exists yet (profile detection is a later package), and provider archived flags belong to phase 3.

## 2. Desired Outcome

### Goals

- [ ] Store a reviewer's decision (`open`, `dismissed`, `confirmed`, note) per flag, locally.
- [ ] Present each open flag with rule id, confidence tier, criteria, and evidence.
- [ ] Show a decision only while the evidence it was made on still holds.
- [ ] Guarantee decisions and flags never alter a project.

### Team Focus

Data model and ownership (local only), failure modes, migration, persistence tests.

### Success Criteria

- [ ] A dismissed flag lists as `dismissed`; changed evidence lists it as `open`.
- [ ] Deciding on a flag that is not open fails with a controlled error and writes nothing.
- [ ] No table other than `review_decisions` changes on `decide`.
- [ ] An inaccessible or unscanned project has no flag because of that.

## 3. Scope

### In Scope

- Migration `0004` (`review_decisions`).
- `decide`, `list_candidates`, rule catalogue constants.
- Tests for S3 to S5 behavior that exists now.

### Out of Scope

- Obsolete candidates from declared lifecycle: no lifecycle source exists until profile detection; provider archived flags are phase 3. FR-020 S2 stays open for a later change.
- Duplicate rule (b): alias ownership is unique, so two projects with one remote surface as `identity_unresolved`. Rule (c) needs root-commit identity.
- Any synchronization or Google Sheets exposure of decisions (excluded for good).
- MCP and CLI surface.

### Constraints

Standard library; decisions are Vyasa-generated local state; free-text note bounded at 500 characters.

## 4. Stakeholders and Impact

- **Primary stakeholders:** the owner.
- **Affected components or capabilities:** `vyasa.adapters.sqlite.projects` (or a new `review` module), `vyasa.domain.index`, new migration.
- **Dependencies:** `be-identity-ambiguity` (merged).
- **Compatibility considerations:** additive migration schema 3 to 4.

## 5. Proposed Direction

A decision row is keyed by project and flag kind and stores the evidence text it was made on. A candidate's review status is the decision's status only while that evidence equals the flag's current evidence. The rule catalogue is a constant mapping kind to rule id, confidence, and criteria. Considered: a status column on `review_flags` (mixes scan-owned and human-owned state) and storing decisions per flag row id (lost if flags were ever rebuilt).

## 6. Requirements Overview

| ID | Requirement | Expected Outcome | Priority |
|---|---|---|---|
| REQ-001 | Candidates are explainable | rule, confidence, criteria, evidence | Must |
| REQ-002 | Decisions are local and bounded | stored only locally | Must |
| REQ-003 | Decisions follow their evidence | stale decision shows open | Must |
| REQ-004 | Nothing is changed automatically | projects untouched | Must |
| REQ-005 | Unverifiable state raises no flag | S3 holds | Must |

## 7. Risks and Open Questions

### Risks

| Risk | Impact | Mitigation or Investigation |
|---|---|---|
| Decisions lost on index rebuild | Judgment lost | Documented; rebuild support is future work |
| A note holds sensitive text | Local only | Never synchronized; bounded length |

### Assumptions

- A candidate is identified by project and kind.

### Open Questions

- [ ] Where lifecycle comes from (profile package) for obsolete candidates.

## 8. Acceptance Summary

- [ ] Every spec scenario has a test against a real database file.
- [ ] `pytest`, `verify_workflows.py`, `verify_knowledge.py`, `openspec validate` pass.

## 9. Traceability

- **OpenSpec Change ID:** `be-review-candidates`
- **Proposing team:** be (backend — the default workflow for this repository)
- **Proposed branch:** `feature/be-review-candidates`
- **Requirement package:** `docs/requirements/project-identity/requirement.md`
- **Knowledge references:**
  - `knowledge/decisions/review-decisions-stay-local.md` — decisions are local and never synced (created with this change)
  - `knowledge/concepts/project-identity.md` — ambiguity is flagged, never guessed
  - `knowledge/concepts/field-ownership.md` — generated local state
- **Related issues or references:** None
- **Related existing specifications:** `openspec/specs/project-identity`, `openspec/specs/identity-review`
- **Related ADRs:** `knowledge/decisions/review-decisions-stay-local.md`

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
