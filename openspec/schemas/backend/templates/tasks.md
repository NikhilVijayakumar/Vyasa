# Implementation Tasks: {{change-name}}

- **OpenSpec Change ID:** `{{change-id}}`
- **Status:** Not Started
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## Task Planning Rules

- Organize work into logical phases and implementation slices.
- Map tasks to relevant requirements, scenarios, design elements, or ADRs.
- Prefer small tasks that produce independently verifiable progress.
- Identify dependencies and preserve the order required for safe implementation.
- Use test-first development where applicable: establish a failing test, implement the behavior, and verify the result.
- Include relevant regression, integration, acceptance, security, accessibility, performance, or platform-specific checks based on the change and team conventions.
- Include documentation, migration, configuration, and operational work when required.
- Do not create tasks for behavior outside the approved scope without first updating the relevant artifacts.
- Do not mark a task complete without the required implementation and verification evidence.
- Apply the applicable team and technology extensions without duplicating their instructions here.

---

## 1. Preparation and Baseline

- [ ] 1.1 Review the proposal, all capability specifications, design, and ADR checkpoint.
- [ ] 1.2 Inspect relevant existing code, tests, interfaces, and project conventions.
- [ ] 1.3 Confirm the working branch follows the project Git policy and includes the OpenSpec change ID.
- [ ] 1.4 Record relevant baseline checks and existing failures when needed to distinguish pre-existing issues from regressions.

## 2. Implementation Slice: {{capability-or-behavior}}

**Traceability:** Requirement(s): `{{requirement-reference}}`

- [ ] 2.1 Add or update tests for the expected behavior and confirm the relevant test fails for the intended reason.
- [ ] 2.2 Implement the minimum change required to satisfy the behavior.
- [ ] 2.3 Run the relevant tests and refactor while keeping them passing.
- [ ] 2.4 Verify applicable boundary, error, and regression scenarios.
- [ ] 2.5 Update relevant documentation or contracts.

Repeat this section for each meaningful capability or implementation slice. Adapt or omit individual steps when they do not apply, and explain material deviations where useful.

## 3. Integration and Cross-Cutting Work

- [ ] 3.1 Integrate the affected components and verify their interfaces and contracts.
- [ ] 3.2 Verify relevant cross-capability behavior and end-to-end workflows.
- [ ] 3.3 Complete applicable security, privacy, performance, accessibility, compatibility, and reliability checks.
- [ ] 3.4 Complete required data migration, configuration, deployment, or rollback work.
- [ ] 3.5 Verify that existing functionality remains compatible where required.

## 4. Final Verification

- [ ] 4.1 Run the required unit, integration, contract, component, and acceptance tests applicable to this change.
- [ ] 4.2 Run required build, lint, type-check, static-analysis, and other project quality checks.
- [ ] 4.3 Verify each in-scope specification requirement and scenario.
- [ ] 4.4 Review the implementation for unintended scope changes, security concerns, and consistency with the design and applicable ADRs.
- [ ] 4.5 Record verification commands, outcomes, failures, skips, and unverified checks.
- [ ] 4.6 Resolve failures introduced by the change or explicitly document approved exceptions and outstanding risks.
- [ ] 4.7 Verify the implementation against the API and data contract,
      including authorization enforcement at the server boundary and the
      documented error model.


## 5. Documentation and Handover

- [ ] 5.1 Update developer, user, API, architecture, or operational documentation as applicable.
- [ ] 5.2 Record relevant decisions, deviations, limitations, and follow-up work.
- [ ] 5.3 Prepare a change summary with links to requirements, tests, and verification evidence.

## 6. Review, Merge, and Archive

- [ ] 6.1 Review the diff and confirm all in-scope requirements are addressed.
- [ ] 6.2 Ensure the required review and verification gates are satisfied.
- [ ] 6.3 Prepare the pull request with the OpenSpec change ID and traceability references.
- [ ] 6.4 Merge the normal feature or fix change into `develop` only after required review and verification.
- [ ] 6.5 Confirm the change is integrated according to project policy before archiving its OpenSpec artifacts.
- [ ] 6.6 Archive the change and preserve the relevant traceability and durable knowledge.

Release promotion from `develop` to `main` follows the project's release process. Production hotfixes originating from `main` must be reconciled back into `develop`.

---

## Verification Record

Complete this record during implementation. Do not pre-fill outcomes before checks are executed.

| Check | Command or Evidence | Result | Notes |
|---|---|---|---|
| Unit tests | Actual command or report | Not Run | |
| Integration / acceptance tests | Actual command or report | Not Run | |
| Build and static checks | Actual command or report | Not Run | |
| Specification coverage | Requirement-to-evidence mapping | Not Verified | |
| Other applicable checks | Actual command or report | Not Run | |

Use explicit result values such as **Passed**, **Failed**, **Skipped**, **Blocked**, or **Not Verified**. Explain skipped, blocked, or unverified checks.

## Completion Summary

- **Implementation status:** Not Started / In Progress / Blocked / Complete
- **Requirements verified:** Summary or reference
- **Outstanding failures or risks:** None / details
- **Known deviations:** None / details
- **Pull request:** Link when available
- **Archive status:** Not Archived / Archived

A change is not ready for completion merely because all task checkboxes are marked. The implementation, specification alignment, verification evidence, review, and integration requirements must also be satisfied.