---
name: test-case-design
description: "Creates complete, structured, traceable test cases for approved CAM Staffing Platform requirements and acceptance criteria."
---

# Skill: Test Case Design

## Goal
Create a practical, reviewable test-case suite for the CAM Staffing Platform prototype and MVP. This skill focuses on individual test cases and their completeness; use `test-strategy` for overall risk-based planning and `test-design` for selecting test-design techniques and identifying scenario coverage.

## Required inputs
- Approved requirement, story, or acceptance-criterion IDs and source references.
- Feature and scope classification: Prototype, MVP, or Later.
- Relevant user roles, workflows, data definitions, UI/API contracts, and confirmed business rules.
- Test environment and approved test framework, if execution automation is requested.

If required inputs are missing, create a list of gaps and clarification questions. Do not invent expected behaviour.

## Procedure
1. Read the approved source and identify each independently testable requirement or acceptance criterion.
2. Assign a unique, stable test-case ID following the repository convention; if no convention exists, propose one such as `TC-PEOPLE-001` for team approval.
3. Write a concise title that describes the behaviour being verified.
4. Define the test type, priority, scope, and linked requirement/story/acceptance criterion.
5. State preconditions, actor/role, test environment, and setup needed.
6. Define synthetic test data, including valid, invalid, missing, boundary, duplicate, or unmatched-reference data only where relevant to the approved rule.
7. Write numbered, reproducible steps. Keep each case focused on one primary behaviour.
8. Specify an observable expected result for each important outcome. Avoid vague wording such as “works as expected.”
9. Identify evidence to capture, such as a sanitized screenshot, test-run result, API response, or log.
10. Review cases for independence, repeatability, duplicate coverage, data cleanup, and requirement traceability.
11. Map every acceptance criterion to one or more test cases; report uncovered criteria and test cases without a valid requirement link.
12. Mark the execution status as `NOT RUN` until the test is actually executed. Do not generate fabricated results or evidence.

## Suggested test-case fields
- Test Case ID
- Requirement ID
- User Story ID
- Acceptance Criterion ID
- Feature
- Test Title
- Test Type
- Priority
- Scope (Prototype/MVP/Later)
- Preconditions
- Test Data
- Steps
- Expected Result
- Environment/Build
- Execution Status
- Evidence Link
- Defect ID
- Notes / Open Questions

## Project-specific coverage prompts
Consider applicable scenarios across:
- People Assignment to Projects
- Staffing Dashboard
- Admin Backoffice and file uploads
- People & Skills
- Opportunity Forecasting
- English and Spanish localization
- Role/access restrictions and sensitive data protection

Only create assertions for calculations, permission rules, file-import behaviour, status transitions, thresholds, and forecast formulas when approved specifications define them.

## Output
A clean test-case table or repository-standard test files, plus traceability gaps, open questions, data requirements, and any test-design rationale.

## Guardrails
- Do not invent business rules, test data schemas, roles, expected messages, thresholds, formulas, or outcomes.
- Prefer synthetic data; never expose real employee/client/opportunity information to unapproved tools.
- Do not confuse test-case design with test execution.
- Do not mark a case PASS without actual execution and supporting evidence.
- Reuse the existing repository's format and conventions where possible.
