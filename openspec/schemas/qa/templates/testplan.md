# Test Plan: {{change-name}}

- **OpenSpec Change ID:** `{{change-id}}`
- **Proposing team:** qa (QA team)
- **Related proposal:** `proposal.md`
- **Related specifications:** `specs/`
- **Related design:** `design.md`

## 1. Purpose

State how this change will be verified, at which layers, and what counts as
evidence that it is correct.

## 2. Scope

Identify the behavior, requirements, and layers covered by this plan, and any
explicitly excluded from it.

## 3. Verification Layers

Assign every behavior to the layer that owns it. A behavior with no layer is
unverified behavior.

| Layer | Scope covered | Tool or approach | Owner | Runs when |
|---|---|---|---|---|
| Unit / component / contract / integration / end-to-end / manual | What this layer proves | Tooling | Team | Trigger |

Consult the `test-strategy` skill for layer boundaries and the tools this
project already uses.

## 4. Requirement Coverage Matrix

| Requirement | Layer | Test or check | Expected evidence | Status |
|---|---|---|---|---|
| Requirement ID | Layer name | Test or check name | Evidence artifact | Covered / Not run / Blocked |

Name the gaps explicitly. A requirement with no row, or a row with no
executable check, is a gap this plan declares rather than hides.

Consult the `traceability-and-coverage` skill for the coverage map.

## 5. Test Data and Environments

State the environments the checks run in, how test data is created,
isolated, and kept synthetic, and which scenarios need data that cannot be
synthetic.

Consult the `test-data-design` skill for fixtures and import validation.

## 6. Execution and Automation

State which checks are automated and how they are triggered, which run on
demand, and which are manual. State the expected duration or frequency where
it matters.

## 7. Entry and Exit Gates

- **Entry criteria:** what must hold before the checks run.
- **Exit criteria:** what must hold before the change is called verified.
- **Blocking conditions:** what prevents completion.

## 8. Defect Handling

State how a defect is raised, what evidence it carries, and what happens when
a defect blocks a gate.

Consult the `defect-reporting` skill for the expected defect report.

## 9. Traceability

| Requirement | Layer | Test or check | Evidence | Result |
|---|---|---|---|---|
| Requirement ID | Layer name | Test or check name | Evidence artifact | Passed / Failed / Not run |

## 10. Test Plan Review

- [ ] Every requirement in scope has a coverage row.
- [ ] Every layer states scope, tooling, and owner.
- [ ] Test data and environment requirements are stated.
- [ ] Entry and exit criteria are stated.
- [ ] Gaps and not-run checks are named, not implied.
- [ ] The plan does not claim coverage that no executed check produced.

**Status:** Draft / Ready for task breakdown
