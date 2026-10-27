# Design: be-profile-v2

## 1. Overview

### Purpose
Add the comprehensive profile schema without a second hand-written copy of its rules.

### Scope
`domain/profile.py` (and one new domain module for the version 2 definitions), the guide, the JSON Schema, and tests.

### Design Principles
One definition drives the validator, the guide, and the schema. Validate each field alone. Reject unsafe values without echoing them. Leave the reader and the index unchanged.

## 2. Context and Constraints

### Current State
`validate_profile` is hand-written for nine version 1 fields; `profile_guide` and `json_schema` are built from the same constants and `DESCRIPTIONS`; `read_profile` bounds, parses, and validates; `checkout_profiles.fields` stores a JSON object; `get_project` returns the profile through `projects.project_profile`.

### Constraints
- Technical constraints: Python 3.12+, standard library only.
- Security and privacy constraints: untrusted text; no echo of rejected values; no credentials, emails, or unsafe paths stored.
- Performance and reliability constraints: the 64 KiB file limit; validation is linear in the fields.
- Compatibility and migration constraints: version 1 behavior and stored names unchanged.
- Operational constraints: none.

### Existing Decisions and Conventions
Canonical profile and draft handling, field ownership, stored identity with aliases.

### Knowledge References
- `knowledge/decisions/profile-schema-v2-full-template.md` — schema.
- `knowledge/decisions/canonical-profile-and-draft.md` — file, format, per-field validation.
- `knowledge/decisions/stored-identity-with-aliases.md` — identity unaffected.

## 3. Requirements and Traceability

| Requirement or Spec Reference | Design Element | Verification Approach |
|---|---|---|
| Version 2 read field by field | table-walking `_validate_v2` | Unit tests on parsed dictionaries |
| Version 1 keeps working | existing `_validate_v1` untouched; `declared` | Existing tests unchanged; accessor tests |
| Unknown fields and versions | `UNSUPPORTED` for other versions; unknown-key problems | Unit tests |
| Declared ids are labels | kind `label`; no other code reads them | Unit tests; a scan test with duplicate ids |
| Text, contacts, paths safe | kinds `text`, `contact`, `path` | Hostile-value unit tests |
| Bounded | per-kind limits and row caps | Unit tests |
| Fixed forms | kinds `enum`, `date`, `tri`, `commit` | Unit tests |
| Guide and schema | `profile_guide(2)`, `json_schema(2)` built from `FIELDS_V2` | Equality test with the committed file; example-validates test |

## 4. Architecture and Design

### Architectural Approach
`vyasa.domain.profile_v2` defines `FIELDS`, a tuple of `Field(path, kind, limit, ...)` records and the group structure for nesting. A generic `validate_table(data, group)` walks the allowed keys of a table, validates each leaf with its kind function, recurses into sub-tables, handles `rows` kinds, and collects problems with dotted names. `validate_profile` dispatches on the version. `profile_guide` and `json_schema` iterate the same records.

### Components and Responsibilities
| Component | Responsibility | Dependencies |
|---|---|---|
| `vyasa.domain.profile_v2` | field definitions, kind validators, `validate_v2`, v2 guide and schema builders | stdlib |
| `vyasa.domain.profile` | version dispatch, v1 unchanged, `declared`, `profile_guide(version)`, `json_schema(version)` | `profile_v2` |
| `schemas/project-profile.v2.json` | committed generated schema | none |
| `vyasa.adapters.mcp.server` | guide tool description | domain |

### Interfaces and Contracts
See `api-contract.md`.

### Key Workflows
Read: bytes → TOML → `validate_profile` → fields and problems → stored with the checkout (unchanged). Guide: `profile_guide()` → generated from definitions.

## 5. Data and State Management

Kind validators return `(value, problem)` as the version 1 helpers do. `text`: string, control characters removed, 1 to n characters, no URL with userinfo (pattern `[a-z][a-z0-9+.-]*://[^/\s]*@`, case-insensitive). `contact`: `text` plus no `@`-email shape (`\S+@\S+\.\S+`) and no `://`. `path`: the existing relative-path rule. `label`: `^[A-Za-z0-9][A-Za-z0-9._:-]{0,99}$`. `date`: a `datetime.date` (not datetime) or text `YYYY-MM-DD` that parses; stored as ISO text. `tri`: `True`, `False`, or the text `unknown`. `commit`: `^[0-9a-fA-F]{7,64}$`, stored lower case. `enum`: exact membership. `list`: list, within count, each item valid, duplicates removed, order kept. `rows`: list within count; each row a table with only defined keys, required keys valid; invalid rows are dropped and reported, valid rows kept. Problems name the dotted path (rows as `path[n].key`) and carry a fixed reason; the rejected value is never included. Unknown keys are reported by dotted name truncated to 100 characters.

## 6. Error Handling and Resilience

| Failure Scenario | Expected Behavior | Recovery or Mitigation |
|---|---|---|
| A field breaks a rule | Dropped and reported; others kept | Writer fixes the field |
| Not a table / wrong nesting | Reported; sibling tables kept | Writer fixes |
| Unsupported version | `unsupported`; nothing stored | Writer uses 1 or 2 |
| Huge or hostile profile | The unchanged 64 KiB limit; the validator bounds recursion to the fixed definition depth | none needed |

## 7. Security and Privacy

Trust boundary as in the contract. The validator never evaluates text, never opens a path it validates, and never includes a rejected value in a problem. The definition depth is fixed, so hostile nesting in the file cannot cause deep recursion in the validator (unknown nested tables are reported at their top key and not walked). No material privacy impact beyond the existing index.

## 8. Quality Attributes

| Attribute | Requirement or Constraint | Design Response | Verification |
|---|---|---|---|
| Consistency | Validator, guide, and schema agree | One definition | Comparison and example tests |
| Safety | No secrets or unsafe paths stored | Kind validators | Hostile fixtures |
| Compatibility | Version 1 unchanged | Separate untouched path | Existing tests |
| Honesty | Declared stays declared | No observed fields in the definitions | Review of the definition list |

## 9. Testing and Verification Strategy

### Behavioral Verification
One test per scenario in the spec.

### Test Strategy
Pure unit tests on parsed dictionaries and on TOML text for `validate_profile`, the kinds, the guide, and the schema; one reader test with a real profile file to prove the end-to-end path; the existing version 1 and guide tests are updated only where they assert the guide's version.

### Testability
All functions are pure; no filesystem needed except the reader test.

### Verification Evidence
`python -m pytest`, `python scripts/verify_workflows.py`; skips are reported.

## 10. Implementation and Migration Considerations

### Implementation Order
Kinds and rows, then the field definitions and `validate_v2`, then dispatch and `declared`, then the guide and schema, then the committed file and the tool description.

### Migration and Rollout
None.

### Documentation and Operations
Update the tool description and `knowledge/log.md`.

## 11. Architecture Decision Checkpoint

- **New ADR required:** Yes — `knowledge/decisions/profile-schema-v2-full-template.md`; see `adr.md`.

## 12. Risks, Trade-offs, and Open Questions

### Risks
A large definition table is easy to get subtly wrong; the generated guide, the example, and the schema comparison catch drift.

### Trade-offs
A full template invites over-declaration; optional fields and the guide's rules mitigate, and detail stays in linked documents.

### Open Questions
None.

## 13. Traceability

Proposal, spec, and contract share the change ID `be-profile-v2`; requirement package `docs/requirements/project-profile/`.

## 14. Design Readiness Review

- [x] Requirements are traced to design elements and checks.
- [x] Boundaries, failure handling, and the trust boundary are stated.
- [x] The architecture decision checkpoint is answered.
- [x] Risks and trade-offs are visible.

**Status:** Draft
