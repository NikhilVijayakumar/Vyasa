# Interface and Data Contract: be-profile-v2

- **OpenSpec Change ID:** `be-profile-v2`
- **Proposing team:** be (backend team)
- **Related proposal:** `proposal.md`
- **Related specifications:** `specs/`
- **Related design:** `design.md`

## 1. Purpose

Fixes the version 2 profile fields, their limits, the stored shape, the accessor, the guide, and the JSON Schema. No new tool, command, or table is involved.

## 2. Scope

In: `validate_profile` (now version 1 or 2), `declared()`, `profile_guide()`, `json_schema()`, `schemas/project-profile.v2.json`. Out: sync exchanges and provider calls (not affected); the context tool and command (`be-profile-context`).

## 3. Interface Surface

| Operation | Kind | Access | Input | Success output | Errors |
|---|---|---|---|---|---|
| `validate_profile(data)` (changed) | Python function (pure) | None | parsed TOML | `ProfileResult(status, fields, problems)` | none; failures are statuses |
| `declared(fields, name)` | Python function (pure) | None | stored fields and a logical name from the accessor list below | the declared value or `None` | none |
| `profile_guide(version=2)` (changed) | Python function (pure) | None | version 1 or 2 | guide dictionary | `ValueError` for another version |
| `json_schema(version=2)` (changed) | Python function (pure) | None | version 1 or 2 | JSON Schema dictionary | `ValueError` for another version |
| `get_profile_guide` (MCP, changed) | MCP tool, read-only | None | none | the version 2 guide, with `supported_versions: [1, 2]` | unchanged |

Statuses are unchanged: `valid`, `invalid`, `unsupported`, `unreadable`, `absent`. `unsupported` is returned for a `schema_version` that is neither 1 nor 2.

Accessor logical names: `name`, `summary`, `purpose`, `lifecycle`, `domain`, `declared_languages`, `declared_frameworks`, `documentation_entry`, `openspec_enabled`, `agent_instruction_paths`. Each maps to the version 2 dotted name if present, else to the version 1 name where one exists (`name`, `purpose` ← `project.description`, `lifecycle` ← `project.lifecycle_status`, `domain`, `declared_frameworks` ← `technologies`, `documentation_entry` ← `project.documentation.overview` / `documentation.entry_point`).

## 4. Error Model

| Condition | Result | Safe to show the user |
|---|---|---|
| Not a table | status `unreadable`, problem `profile` | Yes |
| `schema_version` neither 1 nor 2 | status `unsupported` | Yes |
| A field breaks a rule | problem `(dotted name, reason)`; field dropped; status `invalid` | Yes; reasons are fixed texts and never echo the value |
| Unknown field | problem `(dotted name, "unknown field")` | Yes; the unknown key is reduced to letters, digits, `_`, `.`, and `-` and cut to 40 characters |

## 5. Trust Boundary

The profile is untrusted repository content. Values are typed data: text is stripped of control characters and length-capped, never evaluated or followed. Rejections never echo the rejected value. URLs carrying credentials, email contacts, absolute paths, parent segments, and non-label ids are rejected before storage. No path is read from the repository other than the profile file itself, which the unchanged reader bounds to 64 KiB and refuses through a link.

## 6. Data Model

Stored fields (`checkout_profiles.fields`, JSON object) use these dotted names for version 2; version 1 names are unchanged. Kinds: `text(n)` text of 1 to n characters; `label` 1–100 characters of letters, digits, and `._:-` starting with a letter or digit; `path` repository-relative path up to 200 characters; `date` ISO calendar date; `tri` `true`, `false`, or `"unknown"`; `list(n, m)` at most 20 unless stated, unique items of 1 to n characters; `rows(k)` list of at most k tables.

| Group | Fields |
|---|---|
| `project.` | `id` label; `name` text(100); `codename` text(100); `summary` text(200); `description` text(1000); `project_type` enum(application, library, service, platform, tool, game, documentation, other, unknown); `domain` text(100); `lifecycle_status` enum(planned, active, maintenance, paused, deprecated, archived, unknown); `created_date` date; `last_reviewed_date` date |
| `project.owner.` | `team`, `role`, `contact_reference` text(100), none an email address or URL |
| `project.business.` | `problem_statement` text(1000); `target_users` list(200); `business_objectives`, `success_criteria`, `constraints`, `non_goals` list(300) |
| `project.scope.` | `in_scope`, `out_of_scope`, `known_limitations` list(300) |
| `project.capabilities` | rows(30) of `id` label, `name` text(100) required, `description` text(500), `status` enum(planned, in_progress, available, deprecated, unknown), `source` path |
| `project.technology.` | `declared_languages`, `declared_frameworks`, `declared_platforms`, `declared_datastores`, `declared_integrations`, `infrastructure`, `deployment_targets` list(64), at most 30 items |
| `project.architecture.` | `style` text(100); `summary` text(1000); `entry_points`, `major_components`, `trust_boundaries` list(200); `architecture_document` path |
| `project.interfaces` | rows(30) of `name` text(100) required, `type` enum(api, mcp, cli, event, library, file, other), `purpose` text(300), `contract_reference` path |
| `project.dependencies.` | `internal_projects` list(200); `external_services`, `critical_dependencies` list(100), at most 30 items |
| `project.engineering.openspec.` | `enabled` tri; `root` path; `configuration` path |
| `project.engineering.okf.` | `enabled` tri; `root` path; `format_version` text(20) |
| `project.engineering.agent_instructions` | rows(10) of `path` path required, `purpose` text(200) |
| `project.engineering.testing.` | `strategy_reference` path; `test_entry_points`, `required_checks` list(200) |
| `project.engineering.security.` | `classification` enum(public, internal, confidential, restricted, unknown); `authentication_summary` text(500); `sensitive_data_summary` text(500); `security_document` path |
| `project.engineering.operations.` | `deployment_document`, `runbook`, `monitoring_reference`, `backup_recovery_reference` path |
| `project.documentation.` | `overview`, `vision`, `scope_and_roadmap`, `requirements`, `architecture`, `decisions`, `developer_guide`, `api_reference`, `operations`, `security`, `contributing` path |
| `project.collaboration.` | `coding_agents` list(64), at most 10 items; `contribution_rules` list(300); `branch_policy_reference`, `review_policy_reference` path |
| `project.relationships.` | `parent_project_id` label; `related_project_ids`, `replaces_project_ids` list of labels; `replaced_by_project_id` label |
| `project.profile_maintenance.` | `maintained_by` text(100), not an email or URL; `review_frequency` enum(weekly, monthly, quarterly, yearly, on_change, unknown); `last_verified_commit` 7–64 hexadecimal characters; `verification_notes` text(500) |

Invariants: every stored value passed its rule; `fields` never contains an unknown name; a row of a list of tables is stored only if every key in it is defined and its required keys are valid.

## 7. Migrations and Backward Compatibility

No migration: `checkout_profiles.fields` is a JSON object. Version 1 names and values are unchanged. The guide's `schema_version` becomes 2 and gains `supported_versions`; the committed `schemas/project-profile.v1.json` stays. Rollback: revert the change; stored version 2 fields would then be reported as unsupported at the next scan.

## 8. Traceability

| Requirement | Operation | Field or rule | Acceptance scenario |
|---|---|---|---|
| Version 2 read field by field | `validate_profile` | dotted names | Valid profile; One invalid field; Empty profile; Nested tables |
| Version 1 keeps working | `validate_profile`, `declared` | v1 names | Version 1 unchanged; Accessor reads either version |
| Unknown fields and versions | `validate_profile` | statuses | Unknown field; Unsupported version; Wrong shape of a table |
| Declared ids are labels | `validate_profile` | `label` | Label accepted; Label rejected; Identity unaffected |
| Text, contacts, paths safe | `validate_profile` | safety rules | Credentials in a URL; Email as a contact; Absolute or parent path; Control characters; Plain URL allowed |
| Bounded | `validate_profile` | limits | Too long; Too many rows; Duplicates; Row with an unknown key |
| Fixed forms | `validate_profile` | enum, date, tri, commit | Enumeration; Date; Tri-state; Commit reference |
| Guide and schema | `profile_guide`, `json_schema` | generated | Guide lists every field; Example validates; Schema file matches; Every stored name has a definition |

## 9. Contract Review

- [x] Every affected operation is listed with request, response, and errors.
- [x] The error model states which conditions produce which error.
- [x] The trust boundary is stated.
- [x] The data model states the invariants.
- [x] Migration and backward compatibility are stated.
- [x] Every requirement in scope is traced.
- [x] No unresolved contract questions.

**Status:** Draft
