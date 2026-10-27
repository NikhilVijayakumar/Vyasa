# Design: be-profile-guide

## 1. Overview

### Purpose
Make the profile self-describing for agents.

### Scope
Two pure functions, one committed file, one tool.

### Design Principles
One source of truth for rules. No input, no files, no writes.

## 2. Context and Constraints

### Current State
`vyasa.domain.profile` holds the constants and `validate_profile`.

### Constraints
- Technical: Python 3.12+, standard library.
- Security and privacy: static content only.

### Existing Decisions and Conventions
Canonical profile and draft; untrusted content; the MCP server conventions.

### Knowledge References
- `knowledge/decisions/canonical-profile-and-draft.md`
- `knowledge/concepts/untrusted-content.md`

## 3. Requirements and Traceability

| Requirement or Spec Reference | Design Element | Verification Approach |
|---|---|---|
| The guide is generated from the validation rules | `profile_guide` reads the constants | Example validates; limits equal constants |
| A JSON Schema is committed | `json_schema` and the file | Equality test |
| The profile guide needs no index | tool does not call `_run` | Missing-index test |

## 4. Architecture and Design

### Architectural Approach
`FIELD_DOCS` (name to description) sits beside the constants. `profile_guide()` assembles field entries from `TEXT`, `LISTS`, `LIFECYCLES`, `RELATIONS`, and the limits; `json_schema()` builds the schema the same way. The example is a TOML string kept in the domain and validated by a test. The tool returns the guide in an envelope without opening the index.

### Components and Responsibilities
| Component | Responsibility | Dependencies |
|---|---|---|
| `vyasa.domain.profile` | constants, guide, schema | none |
| `schemas/project-profile.v1.json` | committed schema | none |
| `vyasa.adapters.mcp.server` | `get_profile_guide` | domain |

### Interfaces and Contracts
See `api-contract.md`.

### Key Workflows
Agent calls the tool → writes the file → maintainer reviews and commits → `vyasa scan` reads it.

## 5. Data and State Management

None.

## 6. Error Handling and Resilience

| Failure Scenario | Expected Behavior | Recovery or Mitigation |
|---|---|---|
| Schema file drifts | Test fails | Regenerate and commit |

## 7. Security and Privacy

Contract §5.

## 8. Quality Attributes

| Attribute | Requirement or Constraint | Design Response | Verification |
|---|---|---|---|
| Consistency | Docs equal rules | Generated from constants | Equality and example tests |

## 9. Testing and Verification Strategy

### Behavioral Verification
One test per scenario.

### Test Strategy
Pure unit tests for the guide and schema; MCP in-process tests for the tool; the snapshot test.

### Testability
All pure.

### Verification Evidence
`pytest` output; the tool called over stdio.

## 10. Implementation and Migration Considerations

### Implementation Order
Guide, schema file, tool, snapshot.

### Migration and Rollout
None.

### Documentation and Operations
README note; log entry.

## 11. Architecture Decision Checkpoint

- **New ADR required:** No — the canonical profile decision applies; see `adr.md`.
