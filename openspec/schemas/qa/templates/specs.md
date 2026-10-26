# Specifications: {{change-name}}

## 1. Specification Overview

- **OpenSpec Change ID:** `{{change-id}}`
- **Purpose:** Describe the required behavior introduced or modified by this change.
- **Related proposal:** `proposal.md`
- **Related design:** `design.md`
- **Test plan:** `testplan.md`
- **Team focus:** QA changes are judged on requirement traceability and coverage; acceptance scenarios, test data, and defect evidence; and verification gates and honest reporting.

Organize specifications by capability. Create one specification file per affected capability using the project's OpenSpec conventions.

Recommended structure:

`specs/<capability-name>/spec.md`

Each capability specification must be independently understandable and must describe normative requirements rather than implementation instructions.

The OpenSpec CLI reads a change's specifications as **deltas**. Requirements are read only from a section whose heading names the operation: `## ADDED Requirements`, `## MODIFIED Requirements`, `## REMOVED Requirements`, or `## RENAMED Requirements`. Requirements written outside such a section are not read as deltas, and the change then fails validation. Use the heading that matches the change: new behavior is `ADDED`, changed behavior is `MODIFIED`, behavior that disappears is `REMOVED`, and a rename is `RENAMED`.

---

## 2. Capability: {{capability-name}}

### Purpose

Describe the capability and the behavior it provides.

### Scope

Identify the behavior covered by this specification and any relevant boundaries or exclusions.

## ADDED Requirements

### Requirement: {{requirement-name}}

The system SHALL {{specific, observable behavior}}.

#### Scenario: {{scenario-name}}

- **GIVEN** {{initial context or precondition}}
- **AND** {{additional context, if needed}}
- **WHEN** {{action or event occurs}}
- **AND** {{additional action, if needed}}
- **THEN** {{expected observable outcome}}
- **AND** {{additional expected outcome, if needed}}

#### Scenario: {{boundary-or-failure-scenario}}

- **GIVEN** {{boundary condition or failure context}}
- **WHEN** {{action or event occurs}}
- **THEN** {{required behavior under that condition}}

Add scenarios for relevant alternatives, boundary conditions, error cases, authorization rules, state transitions, and recovery behavior.

### Requirement: {{another-requirement-name}}

The system SHALL {{specific, observable behavior}}.

#### Scenario: {{scenario-name}}

- **GIVEN** {{context}}
- **WHEN** {{action or event}}
- **THEN** {{expected outcome}}

Every requirement of this capability belongs to a delta section — including cross-capability requirements and quality requirements. When a group of requirements needs its own heading, use a divider heading such as `### Cross-Capability Requirements` inside the delta section; the CLI reads the requirements and skips the divider.

---

## 3. Cross-Capability Requirements

Use this section only when requirements genuinely apply across multiple capabilities and cannot be expressed more clearly within the individual capability specifications.

Write them as requirements inside the delta section above, grouped under a divider heading, so that the CLI reads them as deltas. Avoid duplicating requirements across capabilities. Reference the relevant capability specification when appropriate.

---

## 4. Quality and Operational Requirements

Document measurable, externally verifiable quality or operational requirements that are in scope for this change.

Examples include performance, reliability, security, accessibility, compatibility, and resource constraints.

Write them as requirements inside the delta section above, using a threshold that the project actually defines. Use actual project-defined thresholds where available. Do not invent targets or claim guarantees that have not been agreed upon.

If a quality concern is relevant but no requirement or threshold has been established, record it as an open question rather than presenting an assumption as a requirement.

---

## 5. Specification Review

- [ ] Every in-scope behavior is described by a requirement.
- [ ] Every requirement sits inside a delta section heading, and every requirement heading is at level three with its scenarios at level four.
- [ ] Requirements use precise, unambiguous, observable language.
- [ ] Each requirement has a stable, descriptive name.
- [ ] Scenarios describe context, action, and expected outcome.
- [ ] Relevant normal, boundary, and failure behaviors are covered.
- [ ] Requirements are consistent with the proposal and do not prescribe unnecessary implementation details.
- [ ] Cross-capability behavior is specified without unnecessary duplication.
- [ ] Quality requirements use measurable criteria where applicable.
- [ ] Assumptions and unresolved questions are explicitly identified.
- [ ] The specifications provide sufficient detail for design, task breakdown, and verification.

**Status:** Draft / Ready for design and task breakdown
