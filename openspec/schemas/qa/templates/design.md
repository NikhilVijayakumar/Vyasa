# Design: {{change-name}}

## 1. Overview

### Purpose
Describe the design's purpose and how it supports the approved proposal.

### Scope
Summarize the components, capabilities, interfaces, and workflows covered by this design.

### Design Principles
List the principles that materially influence this design, including applicable project conventions and existing architectural decisions.

## 2. Context and Constraints

### Current State
Describe the relevant existing architecture, components, workflows, and dependencies.

Reference existing documentation and source code where appropriate. Do not assume that undocumented behavior exists.

### Constraints
- Technical constraints:
- Security and privacy constraints:
- Performance and reliability constraints:
- Compatibility and migration constraints:
- Operational constraints:

### Existing Decisions and Conventions
Identify applicable ADRs, architecture standards, technology-specific extensions, and other authoritative project guidance.

## 3. Requirements and Traceability

Explain how the design addresses the requirements established in the proposal and specifications.

| Requirement or Spec Reference | Design Element | Verification Approach |
|---|---|---|
| Requirement/spec ID | Component, interface, or flow | Test, inspection, or other evidence |

Use actual identifiers and paths where available. Do not invent requirement IDs or verification evidence.

## 4. Architecture and Design

### Architectural Approach
Describe the chosen approach and how it fits the existing system.

Explain relevant boundaries, responsibilities, dependencies, and integration points. Reference existing architecture diagrams or documentation rather than duplicating them unnecessarily.

### Components and Responsibilities
| Component | Responsibility | Dependencies |
|---|---|---|
| Component A | Responsibility | Dependencies |
| Component B | Responsibility | Dependencies |

Include only components affected by the change.

### Interfaces and Contracts
Describe relevant interfaces, APIs, events, data contracts, schemas, or other boundaries.

For each applicable interface, identify:

- Purpose and owner.
- Inputs and outputs.
- Preconditions and postconditions.
- Validation and error behavior.
- Compatibility expectations.

Use the appropriate team or technology extension for implementation-specific details.

### Key Workflows
Describe important interactions and state transitions.

Use a sequence diagram, flow diagram, state diagram, or C4 diagram when it materially improves understanding. Keep diagrams consistent with the written design and existing system boundaries.

## 5. Data and State Management

Describe the relevant data structures, ownership, persistence, lifecycle, and consistency requirements.

Address applicable concerns such as:

- Data validation and integrity.
- State transitions and concurrency.
- Persistence and schema evolution.
- Data migration and backward compatibility.
- Retention, deletion, and recovery.

If the change does not affect data or state management, explicitly state that this section is not applicable.

## 6. Error Handling and Resilience

Describe expected failure modes and how the design handles them.

| Failure Scenario | Expected Behavior | Recovery or Mitigation |
|---|---|---|
| Failure scenario | Observable system behavior | Recovery approach |

Consider applicable concerns such as timeouts, retries, partial failures, cancellation, duplicate requests, resource exhaustion, and degraded operation.

Do not introduce retries or fallback behavior without considering their consequences.

## 7. Security and Privacy

Describe relevant trust boundaries and security controls.

Consider authentication, authorization, input validation, secret handling, sensitive data, logging, external integrations, and applicable compliance requirements.

If the change introduces no material security or privacy impact, document the assessment and rationale rather than omitting the review.

## 8. Quality Attributes

Identify the quality attributes that materially affect the design.

| Attribute | Requirement or Constraint | Design Response | Verification |
|---|---|---|---|
| Performance, reliability, maintainability, accessibility, or other relevant attribute | Expected level or constraint | Design mechanism | Validation method |

Use measurable thresholds when requirements or project conventions define them. Do not invent targets.

## 9. Testing and Verification Strategy

Describe how the implementation will be verified against the specifications and design.

### Behavioral Verification
Identify the required acceptance scenarios, including relevant normal, boundary, and failure cases.

### Test Strategy
Describe the applicable levels of testing, such as:

- Unit tests.
- Integration tests.
- Contract tests.
- Component or UI tests.
- End-to-end or acceptance tests.
- Performance, security, accessibility, or platform-specific tests.

Select test types based on the change and applicable team standards; not every change requires every test category.
  Place each behavior in the verification layer that owns it, and state the
  seam each check relies on.


### Testability
Explain any required test seams, fixtures, test data, mocks, fakes, environments, or observability.

### Verification Evidence
Specify the expected evidence, such as test results, static analysis, build output, screenshots, measurements, or manual validation records.

The implementation phase must record actual results and distinguish passed, failed, skipped, and unverified checks.

## 10. Implementation and Migration Considerations

Describe important sequencing, dependencies, and compatibility considerations.

### Implementation Order
Identify dependencies or ordering constraints that affect implementation. Detailed, executable work items belong in `tasks.md`.

### Migration and Rollout
Describe applicable migration, rollout, rollback, feature-flag, or deployment considerations.

If no migration or rollout changes are needed, state that explicitly.

### Documentation and Operations
Identify required updates to user documentation, developer guidance, runbooks, monitoring, or support procedures.

## 11. Architecture Decision Checkpoint

Identify consequential decisions that require an ADR.

- **New ADR required:** Yes / No
- **Related ADRs:** Paths or identifiers
- **Decision rationale or checkpoint reference:** Brief explanation

If a significant decision remains unresolved, document the alternatives and constraints that must be resolved before implementation. Record the accepted decision in `adr.md` and keep the design consistent with it.

## 12. Risks, Trade-offs, and Open Questions

### Risks
| Risk | Impact | Mitigation |
|---|---|---|
| Risk description | Potential consequence | Mitigation |

### Trade-offs
Describe material compromises introduced by the design and why they are acceptable.

### Open Questions
- [ ] Question requiring resolution.

Identify whether each unresolved question blocks implementation or can be resolved during implementation under the project's decision-making rules.

## 13. Traceability

- **OpenSpec Change ID:** `{{change-id}}`
- **Proposal:** `proposal.md`
- **Specifications:** Paths under `specs/`
- **Test plan:** `testplan.md`
- **ADRs:** `adr.md` or referenced ADRs
- **Tasks:** `tasks.md`
- **Related existing architecture and documentation:** Paths or links

## 14. Design Readiness Review

- [ ] The design addresses the approved proposal and applicable specifications.
- [ ] Component responsibilities and boundaries are clear.
- [ ] Relevant interfaces, contracts, and workflows are defined.
- [ ] Applicable data, failure, security, and quality concerns are addressed.
- [ ] Testing and verification approaches are defined.
- [ ] Existing architectural decisions and team conventions are respected.
- [ ] The ADR checkpoint is complete.
- [ ] Risks and unresolved questions are explicit.
- [ ] The design is sufficiently detailed to derive implementation tasks without prescribing unnecessary implementation details.

**Status:** Draft / Ready for task breakdown / Approved