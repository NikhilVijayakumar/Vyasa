# Implementation Tasks: openspec-okf-knowledge-rules

- **OpenSpec Change ID:** `openspec-okf-knowledge-rules`
- **Status:** Implemented, pending review and merge
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## 1. Preparation and Baseline

- [x] 1.1 Review the proposal, spec, contract, design, and ADR.
- [x] 1.2 Run `python3 -m unittest scripts/test_verify_knowledge.py` and `python3 scripts/verify_knowledge.py`; record the baseline (expected: pass, 0 errors).
- [x] 1.3 Confirm branch `feature/openspec-okf-knowledge-rules`.

## 2. Implementation Slice: required sections

**Traceability:** Requirement: Required sections per type · Knowledge: `knowledge/practices/writing-knowledge.md`

- [x] 2.1 Prerequisite: add `headings(body)` (top-level headings, fenced code skipped).
- [x] 2.2 Test first: missing, empty, and extra-section cases fail or pass as specified. Include a `# line` inside a fenced block, which must not count as a heading.
- [x] 2.3 Implement `check_sections`; call it from `check_concept`.
- [x] 2.4 Run tests; refactor.

## 3. Implementation Slice: banned words

**Traceability:** Requirement: Banned delivery words

- [x] 3.1 Test first: hit, miss, invalid pattern.
- [x] 3.2 Implement `check_words`.
- [x] 3.3 Run tests.

## 4. Implementation Slice: stable concepts and open questions

**Traceability:** Requirement: Stable concepts have no open questions

- [x] 4.1 Test first: stable fails, draft passes.
- [x] 4.2 Implement using `headings`.
- [x] 4.3 Run tests.

## 5. Implementation Slice: deprecated decisions

**Traceability:** Requirement: Deprecated decisions name a replacement

- [x] 5.1 Test first: valid passes; dangling, wrong type, outside bundle, deprecated without `superseded_by` fail.
- [x] 5.2 Implement `check_supersession`, called from `verify`.
- [x] 5.3 Run tests.

## 6. Integration and Cross-Cutting Work

- [x] 6.1 Add `required_sections` (Decision: Context, Decision, Alternatives considered, Consequences) and `forbidden_words` (`this change`, `this ticket`, `this sprint`, `TODO:`) to `knowledge/profile.json`; run `python3 scripts/verify_knowledge.py` (expected 0 errors).
- [x] 6.2 Add the old-profile test (no new keys, same result).
- [x] 6.3 Update the module docstring of `verify_knowledge.py` to list the new rules.
- [x] 6.4 Add one pointer line to `skills/shared/knowledge-first/SKILL.md`.

## 7. Final Verification

- [x] 7.1 `python3 -m unittest scripts/test_verify_knowledge.py`
- [x] 7.2 `python scripts/verify_workflows.py` — all checks pass after `sync_skills.py` recreated the agent skill links
- [x] 7.3 `openspec validate openspec-okf-knowledge-rules`
- [x] 7.4 Check each spec scenario has a test; record commands, outcomes, failures, skips.
- [x] 7.5 Review the diff for scope; check the contract, including the no-body-echo rule.

## 8. Documentation and Handover

- [x] 8.1 Update the concepts if behavior diverged; add a dated entry to `knowledge/log.md`.
- [ ] 8.2 Mark the decision concept's status when the owner accepts it.

## 9. Review, Merge, and Archive

- [x] 9.1 Pull request with the change ID.
- [x] 9.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [ ] 9.3 Archive the change.
