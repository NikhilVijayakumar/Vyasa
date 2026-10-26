# Interface and Data Contract: {{change-name}}

- **OpenSpec Change ID:** `{{change-id}}`
- **Proposing team:** be (backend team)
- **Related proposal:** `proposal.md`
- **Related specifications:** `specs/`
- **Related design:** `design.md`

## 1. Purpose

Describe the interface contract this change establishes: the MCP tools, CLI
commands, sync exchanges, or provider calls involved, the payloads they
exchange, the errors they return, and the data the change stores.

## 2. Scope

Identify the operations, entities, and integrations affected by this contract,
and any explicitly excluded from it.

## 3. Interface Surface

For each affected operation, state the full contract. Coding agents build
against this section, so an unstated default is a decision nobody made.

| Operation | Kind | Access | Input | Success output | Errors |
|---|---|---|---|---|---|
| Name | MCP tool / CLI / sync / provider call | Trusted roots, paths, or credentials used | Fields and types | Fields, types, evidence | Conditions and codes |

## 4. Error Model

State which conditions produce which error, what shape the error takes, and
what the response must not reveal. State whether errors are retryable and
whether they are safe to surface to the user.

| Condition | Error code | Response shape | Safe to show the user |
|---|---|---|---|
| Condition | Code | Shape | Yes / No |

## 5. Trust Boundary

State which inputs are trusted configuration and which are untrusted
repository or provider content, which paths and data each operation may read
or return, and which data stays machine-local versus synchronized. Record the
behavior for a request outside the configured workspace roots and for
missing or invalid credentials.

Consult the `mcp-server-review` skill when access, secrets, local
paths, or synchronized data are affected.

## 6. Data Model

State the entities, fields, types, constraints, provenance, and invariants
the SQLite index (and, when affected, the Google Sheets layout) must hold.

| Entity | Field | Type | Required | Constraint or invariant |
|---|---|---|---|---|
| Name | Name | Type | Yes / No | Rule |

State the integrity rules that the persistence layer must guarantee and the
behavior when a constraint is violated.

## 7. Migrations and Backward Compatibility

State how existing MCP clients, stored indexes, and synchronized sheets
survive this change: the migration steps, their order, whether the change is
backward compatible, and the rollback path.

Consult the `database-integration-testing` skill for migration and
constraint verification.

## 8. Traceability

| Requirement | Operation | Field or rule | Acceptance scenario |
|---|---|---|---|
| Requirement ID | Operation name | Field or invariant | Scenario name |

## 9. Contract Review

- [ ] Every affected operation is listed with request, response, and errors.
- [ ] The error model states which conditions produce which error.
- [ ] The trust boundary is stated per operation, including out-of-root and credential failures.
- [ ] The data model states the invariants the index must hold.
- [ ] Migration and backward compatibility are stated.
- [ ] Every requirement in scope is traced to an operation or rule.
- [ ] Unresolved contract questions are recorded as explicit open questions.

**Status:** Draft / Ready for design
