# Interface and Data Contract: be-profile-guide

- **OpenSpec Change ID:** `be-profile-guide`
- **Proposing team:** be (backend team)
- **Related proposal:** `proposal.md`
- **Related specifications:** `specs/`
- **Related design:** `design.md`

## 1. Purpose

Fixes the guide's shape, the JSON Schema file, and the new tool.

## 2. Scope

In: `vyasa.domain.profile.profile_guide`, `json_schema`, `schemas/project-profile.v1.json`, the MCP tool. Out: Sheets, provider calls (not affected); any repository write.

## 3. Interface Surface

| Operation | Kind | Access | Input | Success output | Errors |
|---|---|---|---|---|---|
| `profile_guide()` | Python function | None; pure | none | guide dictionary | none |
| `json_schema()` | Python function | None; pure | none | JSON Schema (draft 2020-12) dictionary | none |
| `get_profile_guide` | MCP tool | None; reads no file | none | structured content `{"schema_version": "1", "data": <guide>, "meta": {"generated_at"}}` | none |

Guide `data`: `path` (`.vyasa/project-profile.toml`), `format` (`toml`), `schema_version` (1), `max_bytes`, `fields` (list of `{name, type, required, description, max_length?, max_items?, allowed_values?}` for every field including `documentation.entry_point` and the `related_projects` entry fields), `example` (TOML text), `rules` (list of strings), `schema_file` (`schemas/project-profile.v1.json`).

Tool annotations: read-only, non-destructive, idempotent, closed-world. The tool takes no properties.

## 4. Error Model

None; the tool cannot fail on input. An unexpected exception maps to `INTERNAL_ERROR` as for the other tools.

## 5. Trust Boundary

No input and no file access. The guide text is static, authored by Vyasa, and contains no repository content.

## 6. Data Model

None.

## 7. Migration and Compatibility

One tool added; the committed snapshot changes in this change and is noted here.

## 8. Traceability

| Requirement | Operation |
|---|---|
| The guide is generated from the validation rules | `profile_guide` |
| A JSON Schema is committed | `json_schema`, `schemas/` |
| The profile guide needs no index | `get_profile_guide` |

## 9. Open Contract Questions

- [ ] A `check_profile` tool taking profile text.
