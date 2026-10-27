# Implementation Tasks: openspec-okf-knowledge-rules

- **OpenSpec Change ID:** `openspec-okf-knowledge-rules`
- **Status:** Not Started
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## 1. Preparation and Baseline

- [ ] 1.1 Review the proposal, spec, contract, design, and ADR.
- [ ] 1.2 Run `python3 -m unittest scripts/test_verify_knowledge.py` and `python3 scripts/verify_knowledge.py`; record the baseline (expected: pass, 0 errors).
- [ ] 1.3 Confirm branch `feature/openspec-okf-knowledge-rules`.

## 2. Implementation Slice: required sections

**Traceability:** Requirement: Required sections per type · Knowledge: `knowledge/practices/writing-knowledge.md`

- [ ] 2.1 Prerequisite: add `headings(body)` (top-level headings, fenced code skipped).
- [ ] 2.2 Test first: missing, empty, and extra-section cases fail or pass as specified. Include a `# line` inside a fenced block, which must not count as a heading.
- [ ] 2.3 Implement `check_sections`; call it from `check_concept`.
- [ ] 2.4 Run tests; refactor.

## 3. Implementation Slice: banned words

**Traceability:** Requirement: Banned delivery words

- [ ] 3.1 Test first: hit, miss, invalid pattern.
- [ ] 3.2 Implement `check_words`.
- [ ] 3.3 Run tests.

## 4. Implementation Slice: stable concepts and open questions

**Traceability:** Requirement: Stable concepts have no open questions

- [ ] 4.1 Test first: stable fails, draft passes.
- [ ] 4.2 Implement using `headings`.
- [ ] 4.3 Run tests.

## 5. Implementation Slice: deprecated decisions

**Traceability:** Requirement: Deprecated decisions name a replacement

- [ ] 5.1 Test first: valid passes; dangling, wrong type, outside bundle, deprecated without `superseded_by` fail.
- [ ] 5.2 Implement `check_supersession`, called from `verify`.
- [ ] 5.3 Run tests.

## 6. Integration and Cross-Cutting Work

- [ ] 6.1 Add `required_sections` (Decision: Context, Decision, Alternatives considered, Consequences) and `forbidden_words` (`this change`, `this ticket`, `this sprint`, `TODO:`) to `knowledge/profile.json`; run `python3 scripts/verify_knowledge.py` (expected 0 errors).
- [ ] 6.2 Add the old-profile test (no new keys, same result).
- [ ] 6.3 Update the module docstring of `verify_knowledge.py` to list the new rules.
- [ ] 6.4 Add one pointer line to `skills/shared/knowledge-first/SKILL.md`.

## 7. Final Verification

- [ ] 7.1 `python3 -m unittest scripts/test_verify_knowledge.py`
- [ ] 7.2 `python3 scripts/verify_workflows.py`
- [ ] 7.3 `openspec validate openspec-okf-knowledge-rules`
- [ ] 7.4 Check each spec scenario has a test; record commands, outcomes, failures, skips.
- [ ] 7.5 Review the diff for scope; check the contract, including the no-body-echo rule.

## 8. Documentation and Handover

- [ ] 8.1 Update the concepts if behavior diverged; add a dated entry to `knowledge/log.md`.
- [ ] 8.2 Mark the decision concept's status when the owner accepts it.

## 9. Review, Merge, and Archive

- [ ] 9.1 Pull request with the change ID.
- [ ] 9.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [ ] 9.3 Archive the change.
