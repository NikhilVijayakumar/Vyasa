# Architecture Decision Record: {{change-name}}

## 1. Decision Status

- **Status:** Proposed
- **Date:** YYYY-MM-DD
- **OpenSpec Change ID:** `{{change-id}}`
- **Decision owners:** TBD
- **Related artifacts:** `proposal.md`, `design.md`, `specs/`

Possible statuses: Proposed, Accepted, Rejected, Superseded, Deprecated, Not Required.

## 2. Decision Checkpoint

Select one:

- [ ] **New decision required:** This change introduces or alters a significant architectural decision.
- [ ] **Existing decision applies:** An existing ADR governs this decision.
- [ ] **No new ADR required:** The change does not introduce a significant architectural decision.

### Rationale

Explain why this classification is appropriate.

If an existing decision applies, reference its identifier and location. If no new ADR is required, briefly explain why the change does not warrant one.

If a new decision is required, complete the remaining sections.

---

## 3. Context and Problem

Describe the architectural problem or decision that must be resolved.

Include relevant constraints, existing system behavior, quality attributes, dependencies, and forces influencing the decision.

## 4. Decision Drivers

List the criteria that matter when evaluating alternatives.

Examples include:

- Functional suitability
- Maintainability and extensibility
- Security and privacy
- Performance and scalability
- Reliability and resilience
- Operational complexity
- Compatibility and migration effort
- Cost and resource constraints
- Team capabilities and existing conventions

Include only the drivers relevant to this decision.

## 5. Options Considered

### Option A: {{option-name}}

- **Description:**
- **Advantages:**
- **Disadvantages:**
- **Risks and constraints:**

### Option B: {{option-name}}

- **Description:**
- **Advantages:**
- **Disadvantages:**
- **Risks and constraints:**

Add or remove options as appropriate. Include the status quo when it is a credible alternative.

## 6. Decision

**Chosen option:** {{chosen-option}}

State the decision precisely. Describe what will be adopted, changed, retained, or prohibited.

Avoid vague statements that leave important implementation choices unresolved.

## 7. Decision Rationale

Explain why the selected option best satisfies the decision drivers.

Where relevant, explain:

- Why alternatives were rejected.
- Which trade-offs are being accepted.
- Which constraints influenced the outcome.
- Whether the decision establishes a convention for future changes.

## 8. Consequences

### Positive Consequences
- Expected benefit.

### Negative Consequences and Trade-offs
- Accepted limitation or cost.

### Risks and Mitigations
| Risk | Impact | Mitigation |
|---|---|---|
| Risk description | Potential consequence | Mitigation |

### Follow-up Work
- [ ] Required implementation, migration, documentation, or operational action.

## 9. Implementation Guidance

Describe the architectural boundaries and constraints that implementation must respect.

Include relevant interfaces, dependencies, data ownership, integration boundaries, failure handling, security controls, or migration requirements where applicable.

Detailed implementation tasks belong in `tasks.md`.

## 10. Validation and Review

Define how the decision will be evaluated or verified.

- **Validation approach:**
- **Required tests or evidence:**
- **Operational or quality attributes to observe:**
- **Review conditions:**

For decisions that cannot be fully validated before implementation, identify the evidence needed to confirm or revisit the decision.

## 11. Reversal and Reconsideration

Describe the conditions under which this decision should be reconsidered.

- **Reconsider if:**
- **Reversal or migration considerations:**
- **Evidence that would trigger review:**

## 12. Traceability

- **OpenSpec Change ID:** `{{change-id}}`
- **Related proposal:** `proposal.md`
- **Related design:** `design.md`
- **Ui/ux contract:** `ui-spec.md`
- **Related specifications:** Paths or identifiers
- **Related ADRs:** Paths or identifiers
- **Related issues or pull requests:** Links, when available

---

## Decision Summary

Complete this summary for a new decision.

- **Decision:** One-sentence statement.
- **Primary reason:** Main justification.
- **Key trade-off:** Most important accepted consequence.
- **Review trigger:** Condition that would warrant reconsideration.