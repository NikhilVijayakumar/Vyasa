# Interface and Data Contract: be-profile-context

- **OpenSpec Change ID:** `be-profile-context`
- **Proposing team:** be (backend team)
- **Related proposal:** `proposal.md`
- **Related specifications:** `specs/`
- **Related design:** `design.md`

## 1. Purpose

Fixes the context bundle, the differences, the new MCP tool, the new command, and the in-memory index helper. No table or migration is involved.

## 2. Scope

In: `differences`, `profile_context`, `live_context`, `open_memory_index`, `enrich_run`, the tool `get_profile_context`, and the command `vyasa profile-context`. Out: sync exchanges and provider calls (not affected).

## 3. Interface Surface

| Operation | Kind | Access | Input | Success output | Errors |
|---|---|---|---|---|---|
| `differences(checkout, declared)` | Python function (pure) | None | a checkout dictionary as `get_project` returns it, and the declared profile values | list of findings | none |
| `profile_context(connection, project_id, now)` | Python function | reads the index | read-only connection, project id | envelope with `data` below, `source.kind = index` | `IndexStoreError` `INVALID_INPUT`, `PROJECT_NOT_FOUND` |
| `get_profile_context` | MCP tool, read-only | reads the index | `project_id: str` | the envelope | `INVALID_INPUT`, `PROJECT_NOT_FOUND`, `INDEX_UNAVAILABLE` |
| `live_context(path, now)` | Python function | read-only walk and bounded reads of one repository; temporary in-memory index | directory path | envelope with `source.kind = live_scan` and `project_id = null` | `NotAProject` (value is a fixed message) |
| `vyasa profile-context [path]` | command | as `live_context`; writes only to standard output | optional path (default the current directory) | the envelope as JSON on standard output, exit 0 | usage error exit 2 on a missing path or a directory that is not a project root; exit 4 on an internal failure |
| `open_memory_index()` | Python function | none | none | a migrated in-memory connection | `IndexStoreError` |
| `enrich_run(run, detect)` | Python function | reads repository files through `detect` | a discovery run | the run with languages, counts, markers, and frameworks attached, partial on failure | none |

Bundle `data`: `source` (`{kind: "index" | "live_scan", generated_at}`), the `get_project` data (`project_id` — `null` for `live_scan` — `display_name`, `state`, `identity`, `checkouts`, `profile`, `review_candidates`, timestamps), each checkout extended with `differences`, and `workflow`. For `live_scan`, `identity` holds the derived status and source and no aliases beyond the repository's remote identity.

Finding: `{code, severity, subject, detail}` where `severity` is `review` or `info`, `subject` is the declared value, label, or technology key concerned (declared text is already validated and at most 200 characters), and `detail` is a fixed sentence from a table. Codes: `declared_language_not_detected`, `detected_language_not_declared`, `declared_framework_not_detected`, `detected_technology_not_declared`, `declared_not_comparable`, `declared_openspec_not_detected`, `openspec_detected_but_declared_disabled`, `declared_agent_instruction_not_detected`.

`workflow`: a fixed list of strings (version 2 guide pointer, evidence use, omit what is unsupported, no observed counts or activity in the profile, no secrets, report to the maintainer for review).

## 4. Error Model

| Condition | Error code | Response shape | Safe to show the user |
|---|---|---|---|
| `project_id` empty or not a string | `INVALID_INPUT` | message names `project_id` | Yes |
| No project has the identifier | `PROJECT_NOT_FOUND` | fixed message | Yes |
| Index missing or too new | `INDEX_UNAVAILABLE` / `SCHEMA_TOO_NEW` | as the existing tools | Yes |
| Path missing or not a directory | command exit 2, message on standard error | names the problem, not file text | Yes |
| Directory is not a project root | command exit 2, message on standard error | fixed message | Yes |
| Internal failure while scanning | command exit 4, generic message | no repository text | Yes |

## 5. Trust Boundary

Repository content is untrusted. The live scan reads exactly what the normal scan reads (names, the profile, supported root manifests under the strict reader). The bundle carries typed data: fixed codes and statuses, labels and keys from trusted data, and the validated declared profile values; it never carries manifest text, README text, or an absolute path. The workflow is fixed text. The command writes only to standard output; the in-memory index is dropped when the command ends. Vyasa starts no process and sends nothing anywhere.

## 6. Data Model

No stored data. Bundle fields are those of `get_project` plus `source`, per-checkout `differences`, and `workflow`.

## 7. Migrations and Backward Compatibility

None. `get_project`, `search_projects`, and `scan` are unchanged. The tool list gains one tool; the committed snapshot changes by that addition only. Rollback: revert the change.

## 8. Traceability

| Requirement | Operation | Field or rule | Acceptance scenario |
|---|---|---|---|
| Context bundle | `profile_context` | bundle fields | Complete bundle; No profile is an ordinary state; Never-assessed observations |
| MCP tool serves the stored observation | `get_profile_context` | `source.kind = index` | Stored context; Unknown project; Tool is read-only and pinned |
| Command scans live and writes nothing | `live_context`, command | `source.kind = live_scan` | Unindexed repository; Nothing is written; Same shape as the tool; Not a project; Missing path |
| No absolute path or file text | both | omitted fields | No absolute path; Malformed manifest text |
| Differences | `differences` | finding codes | Declared language not detected; Partial observation makes no claim; Detected language not declared; Nothing declared in the category; Declared framework not detected; Detected technology not declared; Unmatched declared names; Version 1 technologies; Declared OpenSpec not found; Declared OpenSpec disabled but found; Declared agent instruction not found; Each entry is a finding for review |
| No agent, no profile write | both | none | Profile untouched |
| Workflow | both | `workflow` | Workflow present and fixed |

## 9. Contract Review

- [x] Every affected operation is listed with request, response, and errors.
- [x] The error model states which conditions produce which error.
- [x] The trust boundary is stated.
- [x] The data model states the invariants.
- [x] Migration and backward compatibility are stated.
- [x] Every requirement in scope is traced.
- [x] No unresolved contract questions.

**Status:** Draft
