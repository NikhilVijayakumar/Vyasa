---
name: test-design
description: "Designs detailed, risk-aware test cases from approved CAM Staffing Platform requirements and acceptance criteria."
---

# Skill: Test Design

## Goal
Design clear, traceable, and maintainable tests for the CAM Staffing Platform prototype and MVP.

## Inputs
Approved requirements, user stories, acceptance criteria, business rules, data dictionaries, UI designs, API contracts, risk notes, and clarification decisions.

## Procedure
1. Confirm the requirement/story/acceptance-criterion IDs and source versions.
2. Identify the feature, actor/role, preconditions, workflow state, dependencies, and test environment.
3. Select appropriate techniques: equivalence partitioning, boundary value analysis, decision tables, state transitions, pairwise testing, exploratory testing, and negative testing.
4. Consider positive, negative, boundary, permission, validation, data integrity, integration, regression, localization, accessibility, and usability cases when relevant to the approved scope.
5. For each case, define a unique ID, title, objective, priority, preconditions, synthetic test data, steps, observable expected result, requirement links, and evidence needs.
6. Ensure expected results come from approved criteria. If behaviour is undefined, add a clarification instead of guessing.
7. Check test independence, repeatability, meaningful coverage, duplicate scenarios, and test-data cleanup.
8. Map every acceptance criterion to one or more tests and report uncovered criteria.
9. Keep prototype/demo cases distinct from MVP/release regression coverage.

## CAM Staffing Platform considerations
- People Assignment to Projects: resource-request workflows and any approved status/validation rules.
- Staffing Dashboard: metric display and reconciliation against approved data/formulas.
- Admin Backoffice: permitted admin actions and file-upload validation.
- People & Skills: employee/skill data, search/filter behaviour if specified.
- Opportunity Forecasting: only approved forecasting inputs and calculations.
- English/Spanish: relevant UI text and error states where in scope.

## Output
A test-case table or repository-standard test files, plus coverage gaps, assumptions/open questions, and test-data notes.

## Guardrails
- Never invent thresholds, calculations, role permissions, status transitions, messages, or data rules.
- Never use real employee/client/opportunity data unless explicitly authorized.
- Do not treat a designed test as an executed test.
- Reuse repository conventions and approved tooling.
