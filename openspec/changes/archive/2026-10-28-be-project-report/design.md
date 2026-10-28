# Design: be-project-report

## 1. Overview

### Purpose
Make an agent's detailed reading of a repository durable and queryable, without Vyasa writing or inferring anything.

### Scope
One domain module, one scan step, one migration, two tools, one added field, one workflow step.

### Design Principles
One source of truth for sections and limits. Untrusted text bounded and typed. Read-only everywhere except the existing scan write path.

## 2. Context and Constraints

### Current State
The scan already reads `.vyasa/project-profile.toml` safely and stores validated fields; the guide, validator, and JSON Schema share one definition. The MCP server is read-only.

### Constraints
- Technical: Python 3.12+, standard library, SQLite.
- Security and privacy: report text is untrusted; no local paths returned.

### Existing Decisions and Conventions
Profile read and storage pattern; per-checkout observation tables; envelope and error codes.

### Knowledge References
- `knowledge/decisions/project-report-in-the-repository.md`
- `knowledge/decisions/profile-context-for-agents.md`
- `knowledge/concepts/untrusted-content.md`

## 3. Requirements and Traceability

| Requirement or Spec Reference | Design Element | Verification Approach |
|---|---|---|
| The report is read safely | `report_reader.read(checkout_root)` reuses the profile's safe-read helper | Fixture tests: missing, link, oversize |
| Sections are kept by name and bounded | `vyasa.domain.report.read_report(text)` | Unit tests incl. hostile text |
| Report limits are configurable inside bounds | `ReportLimits` and the `report` table in `load_workspace_config` | Config tests: defaults, values, bounds, section above file, type, unknown key |
| Stored reports keep their provenance | store step and tables | Database test, failed-read keeps rows |
| Template from the section definition | `report_template()` from `SECTIONS` | Example reads clean; limits equal constants |
| Tools | `get_report_template`, `get_project_report`, `get_project.report` | MCP contract tests, snapshot |
| Workflow names the report | step added in `profile_context` | Bundle test |

## 4. Architecture and Design

### Architectural Approach
`vyasa.domain.report` holds `SECTIONS` (name, purpose), `ReportLimits` (defaults 256 KiB and 16 KiB, bounds 16 to 4096 and 1 to 1024), the limits, `read_report(text, limits)` (pure: split on `## `, match names, bound, strip, reject credential URLs, return status/sections/dropped), `report_template()`, and `EXAMPLE`. `load_workspace_config` parses the optional `report` table into `ReportLimits` (all problems reported together, as for roots) and carries it on `WorkspaceConfig`; the scan passes it to the reader and the store records it on the observation. `report_template()` takes optional stored limits; the MCP tool reads them from the latest observation, so the server never reads the configuration. The scanner step reads the file with the profile's existing safe-read helper (extended to a size parameter) and calls `read_report`. The store step writes `report_observations` and `report_sections` in the checkout's existing transaction. Query functions `get_project_report` and the `report` object assemble from those tables. The MCP adapter adds two thin tools.

### Components and Responsibilities
| Component | Responsibility | Dependencies |
|---|---|---|
| `vyasa.domain.report` | definition, reader, template | none |
| scanner step | safe file read | profile read helper |
| store and migration `0011` | persist | SQLite |
| `application.query` | assemble responses | store |
| `adapters.mcp.server` | tools | query |

### Interfaces and Contracts
See `api-contract.md`.

### Data Model and Storage
See `api-contract.md` §6.

### Error Handling and Failure Modes
Reader failures become a status, never an exception. A failed read keeps earlier rows. A migration failure follows the existing migration behaviour.

### Security, Privacy, and Compliance
Text only, size-capped, no link following, control characters stripped, credential URLs rejected, returned as `declared` data with a warning. No path in records or responses.

### Observability and Operations
Dropped headings and statuses are visible in `get_project` and the scan summary count of checkouts with a report.

## 5. Testing and Verification Strategy

| Layer | What it checks |
|---|---|
| Unit | reader and template, hostile text, example validity, limits equal constants |
| Scanner fixtures | missing, link, oversize, valid, repository unchanged |
| Database | migration, rows, failed read keeps rows, checkout delete cascades |
| MCP contract | tool list snapshot, errors, no path, status-only in `get_project` |
| End to end | temp workspace: write report, scan, query with the built MCP |

## 6. Alternatives and Trade-offs

Store the whole file as one blob: simpler, but no section retrieval and no per-section bound. Parse markdown fully: heavier and not needed for fixed headings.

## 7. Risks and Open Questions

Prompt injection in stored text is mitigated by typing and a warning, not eliminated; consumers must treat it as data. Staleness is deferred.

## 8. Rollout and Migration

Additive migration `0011`; run `vyasa scan` once after upgrading. No client change is required for existing tools.

## 9. Readiness Review

- [x] Design traces to the specifications.
- [x] Failure modes and verification are stated.
