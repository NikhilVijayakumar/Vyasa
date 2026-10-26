# Change Proposal: {{change-name}}

## Why

State the problem and the intended outcome in one to three sentences. The OpenSpec CLI parses
this section, so it must contain between 50 and 1000 characters, and it must stand on its own
without reading the sections below.

## What Changes

- **{{capability-name}}**: <one line describing what will be different for this capability>

The OpenSpec CLI parses this section. When the change has specification deltas, they are read
from `specs/`; this list states the same changes in brief and must agree with them.

## 1. Problem and Motivation

### Current Situation
Describe the current behavior, workflow, limitation, or gap.

### Problem
What specific problem are we solving? Who or what is affected?

### Evidence
Provide relevant observations, user feedback, incidents, existing documentation, code references, or other supporting evidence. Distinguish verified facts from assumptions.

## 2. Desired Outcome

Describe the outcome this change should achieve.

### Goals
- [ ] Goal 1
- [ ] Goal 2

### Team Focus
Frontend changes are judged on UI/UX impact and the affected screens and components; accessibility and localization behaviour; component behaviour and browser-level verification.

### Success Criteria
Define observable outcomes that can be verified during implementation or review.

- [ ] Criterion 1
- [ ] Criterion 2

## 3. Scope

### In Scope
- Item 1
- Item 2

### Out of Scope
- Item 1
- Item 2

### Constraints
Record relevant technical, organizational, operational, compatibility, security, performance, or delivery constraints.

## 4. Stakeholders and Impact

Identify the affected users, teams, systems, interfaces, workflows, or downstream consumers.

- **Primary stakeholders:**
- **Affected components or capabilities:**
- **Dependencies:**
- **Compatibility considerations:**

## 5. Proposed Direction

Describe the intended approach at a high level without prematurely prescribing implementation details.

Include alternative approaches considered when they materially affect scope, cost, risk, or maintainability.

Detailed architecture and implementation decisions belong in the design and ADR artifacts.

## 6. Requirements Overview

Summarize the expected behavioral or operational changes.

| ID | Requirement | Expected Outcome | Priority |
|---|---|---|---|
| REQ-001 | Requirement description | Observable outcome | Must |
| REQ-002 | Requirement description | Observable outcome | Should |

These identifiers are proposal-level references. Detailed, normative requirements belong in the specification artifact.

## 7. Risks and Open Questions

### Risks
| Risk | Impact | Mitigation or Investigation |
|---|---|---|
| Risk description | Potential consequence | Proposed mitigation |

### Assumptions
- Assumption requiring validation, if any.

### Open Questions
- [ ] Question requiring clarification
- [ ] Question requiring investigation

Do not silently convert unresolved questions into established requirements or facts.

## 8. Acceptance Summary

Describe the conditions under which the proposed change can be considered successfully implemented.

Acceptance criteria must be observable and verifiable. Detailed scenarios and edge cases belong in the specification artifact.

- [ ] Acceptance criterion 1
- [ ] Acceptance criterion 2

## 9. Traceability

- **OpenSpec Change ID:** `{{change-id}}`
- **Proposing team:** fe (frontend team — this schema is the frontend team's workflow)
- **Proposed branch:** `feature/{{change-id}}-{{short-description}}` or `fix/{{change-id}}-{{short-description}}`
- **Related issues or references:** None / links
- **Related existing specifications:** None / paths
- **Related ADRs:** None / paths

## 10. Readiness Review

Before moving to specification and design, confirm:

- [ ] The problem and motivation are clear.
- [ ] Goals and success criteria are observable.
- [ ] Scope and non-goals are explicit.
- [ ] Important stakeholders, constraints, and dependencies are identified.
- [ ] Assumptions and unresolved questions are visible.
- [ ] The proposing team is identified and its focus and skills applied.
- [ ] The proposal is consistent with existing specifications and project conventions.
- [ ] Significant ambiguities have been challenged and resolved, or explicitly recorded.
- [ ] The change has a stable OpenSpec ID and follows the project's Git discipline.

**Status:** Draft / Ready for specification and design