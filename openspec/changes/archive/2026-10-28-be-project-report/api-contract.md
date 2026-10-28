# Interface and Data Contract: be-project-report

- **OpenSpec Change ID:** `be-project-report`
- **Proposing team:** be (backend team)
- **Related proposal:** `proposal.md`
- **Related specifications:** `specs/`
- **Related design:** `design.md`

## 1. Purpose

Fixes the report file, the template, the stored shape, the two new tools, and the added `get_project` field.

## 2. Scope

In: `report` settings in the configuration, `vyasa.domain.report`, the scan read, migration `0011`, `get_report_template`, `get_project_report`, `get_project.report`, the context workflow step. Out: Sheets and provider calls (not affected); any repository write.

## 3. Interface Surface

| Operation | Kind | Access | Input | Success output | Errors |
|---|---|---|---|---|---|
| `report_template()` | Python function | none; pure | none | template dictionary | none |
| `read_report(text)` | Python function | none; pure | report text | status, sections, dropped | none |
| `get_report_template` | MCP tool | none; reads no file or index | none | `{"schema_version": "1", "data": <template>, "meta": {"generated_at"}}` | none |
| `get_project_report` | MCP tool | index, read-only | `project_id` (string), optional `section` (string) | per-checkout report, see below | `PROJECT_NOT_FOUND`, `INVALID_INPUT`, `INDEX_UNAVAILABLE`, `INTERNAL_ERROR` |
| `get_project` | MCP tool | index, read-only | unchanged | adds `report` per checkout | unchanged |

Template `data`: `path` (`.vyasa/project-report.md`), `format` (`markdown`), `limits` (`{max_file_bytes, max_section_bytes, source}` where `source` is `index` when taken from the latest report observation and `default` otherwise; defaults 262144 and 16384), `sections` (list of `{name, purpose}`), `example` (markdown text), `rules` (list of strings), `schema_version` (1).

Sections (fixed order): Overview; Purpose and Users; Architecture; Modules; Key Flows; Interfaces; Data and Storage; Build, Run, and Test; Dependencies and Integrations; Risks and Limitations; Open Questions.

`get_project_report` `data`: `project_id`, `display_name`, `warning` (the untrusted-text notice), `checkouts` (list in the order `get_project` uses, each `{state, kind, status, reason, content_hash, scanned_at, sections: [{name, text, size}], dropped: [{heading, reason}], origin: "declared"}`, plus `kept_from` when earlier sections are kept). `status` is one of `present`, `not_present`, `unreadable`, `invalid`, `not_assessed`; `reason` is present for the last two failures; when `status` is not `present` and earlier sections are kept, `kept_from` holds their `content_hash` and `scanned_at`. With `section`, `sections` holds only that one.

`get_project.report` per checkout: `{status, reason, sections: [{name, size}], dropped: [{heading, reason}], content_hash, scanned_at}` and `kept_from` when applicable; no text. A checkout never read (or an index from before reports) has status `not_assessed`.

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
| `report_observations` | `checkout_id` (PK, FK), `status`, `reason`, `content_hash`, `scanned_at`, `max_file_bytes`, `max_section_bytes`, `dropped_json`, `kept_hash`, `kept_at` | one row per checkout |
| `report_sections` | `checkout_id` (FK), `name`, `text`, `size`, `position` | PK (`checkout_id`, `name`); text at most the section limit |

`status` is the latest read: `present`, `not_present`, `unreadable`, or `invalid` (`reason` says why for the last two). `content_hash` and `scanned_at` belong to that read. `kept_hash` and `kept_at` say which read the stored sections came from.

Invariants: a `present` read replaces the sections and sets `kept_*` to its own hash and time; `not_present` deletes the sections (the report is gone, an ordinary state); an `unreadable` or `invalid` read keeps the earlier sections and `kept_*`, so earlier text stays servable and its origin is visible; checkouts are never deleted, so rows are only replaced.

### Configuration

`config.toml` gains an optional table:

```toml
[report]
max_file_kib = 256      # 16 to 4096
max_section_kib = 16    # 1 to 1024, not above max_file_kib
```

Invalid values reject the whole configuration (existing rule). Limits are per installation, read by `vyasa scan`; the MCP server does not read the configuration and learns the limits from the index.

## 7. Migration and Compatibility

Additive migration; older indexes upgrade on the next scan. Existing tools are unchanged except the added `report` key. Rollout order: domain and reader, migration and storage, tools, workflow step.

## 8. Traceability

| Item | Requirement |
|---|---|
| reader and limits | The report is read safely; Sections are kept by name and bounded |
| tables | Stored reports keep their provenance |
| limits | Report limits are configurable inside bounds |
| template | The template is generated from the section definition |
| tools | The report template needs no index; The stored report is served as declared data; Project details show the report status only |

## 9. Open Questions

- [ ] Staleness comparison against the head commit.
- [ ] Component reports for monorepos.
