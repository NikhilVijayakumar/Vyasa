# API and Data Contract: {{change-name}}

- **OpenSpec Change ID:** `{{change-id}}`
- **Proposing team:** be (backend team)
- **Related proposal:** `proposal.md`
- **Related specifications:** `specs/`
- **Related design:** `design.md`

## 1. Purpose

Describe the server-facing contract this change establishes: the operations
other teams call, the payloads they exchange, the errors they receive, and
the data the change stores.

## 2. Scope

Identify the operations, entities, and integrations affected by this contract,
and any explicitly excluded from it.

## 3. API Surface

For each affected operation, state the full contract. Other teams build
against this section, so an unstated default is a decision nobody made.

| Operation | Method and path or query | Authorization | Request | Success response | Error responses |
|---|---|---|---|---|---|
| Name | `METHOD /path` | Role or scope | Fields and types | Fields and types | Conditions and codes |

## 4. Error Model

State which conditions produce which error, what shape the error takes, and
what the response must not reveal. State whether errors are retryable and
whether they are safe to surface to the user.

| Condition | Error code | Response shape | Safe to show the user |
|---|---|---|---|---|
| Condition | Code | Shape | Yes / No |

## 5. Authorization Boundary

State which role or scope may invoke which operation, what the server
enforces, and what is only a client-side convenience. Record the behavior
for an unauthorized and an authenticated-but-forbidden caller.

Consult the `security-and-privacy-review` skill when access, secrets, or
sensitive data are affected.

## 6. Data Model

State the entities, fields, types, constraints, and invariants the database
must hold.

| Entity | Field | Type | Required | Constraint or invariant |
|---|---|---|---|---|
| Name | Name | Type | Yes / No | Rule |

State the integrity rules that the persistence layer must guarantee and the
behavior when a constraint is violated.

## 7. Migrations and Backward Compatibility

State how existing callers and stored data survive this change: the
migration steps, their order, whether the change is backward compatible
during rollout, and the rollback path. State what happens to in-flight
requests during the change.

Consult the `database-integration-testing` skill for migration and
constraint verification.

## 8. Traceability

| Requirement | Operation | Field or rule | Acceptance scenario |
|---|---|---|---|
| Requirement ID | Operation name | Field or invariant | Scenario name |

## 9. Contract Review

- [ ] Every affected operation is listed with request, response, and errors.
- [ ] The error model states which conditions produce which error.
- [ ] Authorization is stated per operation, including the forbidden case.
- [ ] The data model states the invariants the database must hold.
- [ ] Migration and backward compatibility are stated.
- [ ] Every requirement in scope is traced to an operation or rule.
- [ ] Unresolved contract questions are recorded as explicit open questions.

**Status:** Draft / Ready for design
