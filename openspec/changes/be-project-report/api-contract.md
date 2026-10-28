# Interface and Data Contract: be-project-report

- **OpenSpec Change ID:** `be-project-report`
- **Proposing team:** be (backend team)
- **Related proposal:** `proposal.md`
- **Related specifications:** `specs/`
- **Related design:** `design.md`

## 1. Purpose

Fixes the report file, the template, the stored shape, the two new tools, and the added `get_project` field.

## 2. Scope

In: `vyasa.domain.report`, the scan read, migration `0011`, `get_report_template`, `get_project_report`, `get_project.report`, the context workflow step. Out: Sheets and provider calls (not affected); any repository write.

## 3. Interface Surface

| Operation | Kind | Access | Input | Success output | Errors |
|---|---|---|---|---|---|
| `report_template()` | Python function | none; pure | none | template dictionary | none |
| `read_report(text)` | Python function | none; pure | report text | status, sections, dropped | none |
| `get_report_template` | MCP tool | none; reads no file or index | none | `{"schema_version": "1", "data": <template>, "meta": {"generated_at"}}` | none |
| `get_project_report` | MCP tool | index, read-only | `project_id` (string), optional `section` (string) | per-checkout report, see below | `PROJECT_NOT_FOUND`, `INVALID_INPUT`, `INDEX_UNAVAILABLE`, `INTERNAL_ERROR` |
| `get_project` | MCP tool | index, read-only | unchanged | adds `report` per checkout | unchanged |

Template `data`: `path` (`.vyasa/project-report.md`), `format` (`markdown`), `max_bytes` (262144), `max_section_bytes` (16384), `sections` (list of `{name, purpose}`), `example` (markdown text), `rules` (list of strings), `schema_version` (1).

Sections (fixed order): Overview; Purpose and Users; Architecture; Modules; Key Flows; Interfaces; Data and Storage; Build, Run, and Test; Dependencies and Integrations; Risks and Limitations; Open Questions.

`get_project_report` `data`: `project_id`, `checkouts` (list of `{checkout_id, status, content_hash, scanned_at, sections: [{name, text, size}], dropped: [{heading, reason}], origin: "declared", warning}`). `status` is one of `present`, `not_present`, `unreadable`, `invalid`, `not_assessed`. With `section`, `sections` holds only that one. `checkout_id` is the opaque id already used by `get_project`.

`get_project.report` per checkout: `{status, sections: [{name, size}], dropped: [{heading, reason}], content_hash, scanned_at}`; no text.

Tool annotations: read-only, non-destructive, idempotent, closed-world.

## 4. Error Model

| Condition | Code | Detail returned |
|---|---|---|
| unknown `project_id` | `PROJECT_NOT_FOUND` | the id |
| `section` not in the template | `INVALID_INPUT` | the allowed names |
| no index | `INDEX_UNAVAILABLE` | existing hint |
| unexpected exception | `INTERNAL_ERROR` | generic message; detail to standard error |

Report content problems are not errors: they are per-checkout `status` and `dropped` entries.

## 5. Trust Boundary

The report file is untrusted repository content. The scan reads it as text only, size-capped, through no link. Stored text has control characters stripped and credential-bearing URLs rejected. Tools return it as data under `declared` with a warning, never as instructions. No local path is stored in the report record or returned.

## 6. Data Model

Migration `0011_project_report.sql` (additive):

| Table | Columns | Constraints |
|---|---|---|
| `report_observations` | `checkout_id` (PK, FK), `status`, `content_hash`, `scanned_at`, `dropped_json` | one row per checkout |
| `report_sections` | `checkout_id` (FK), `name`, `text`, `size`, `position` | PK (`checkout_id`, `name`); text at most 16 KiB |

Invariants: sections exist only when status is `present`; a failed read keeps the previous rows and records the failure status in a separate column `last_failure` so earlier text stays servable; deleting a checkout deletes its rows.

## 7. Migration and Compatibility

Additive migration; older indexes upgrade on the next scan. Existing tools are unchanged except the added `report` key. Rollout order: domain and reader, migration and storage, tools, workflow step.

## 8. Traceability

| Item | Requirement |
|---|---|
| reader and limits | The report is read safely; Sections are kept by name and bounded |
| tables | Stored reports keep their provenance |
| template | The template is generated from the section definition |
| tools | The report template needs no index; The stored report is served as declared data; Project details show the report status only |

## 9. Open Questions

- [ ] Staleness comparison against the head commit.
- [ ] Component reports for monorepos.
