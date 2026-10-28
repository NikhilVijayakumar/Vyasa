# Requirement: Project Report

- **Package:** `docs/requirements/project-report/`
- **Status:** Grilled — owner confirmed every recommendation on 2026-10-28
- **Roadmap phase:** P1
- **Owns:** FR-028
- **Grill log:** [grill-log.md](grill-log.md)
- **Diagrams:** [diagrams.md](diagrams.md)
- **Features:** [fr-028-project-report.feature](features/fr-028-project-report.feature)

## Knowledge References

Checked with the `knowledge-first` skill before writing.

- `knowledge/decisions/profile-schema-v2-full-template.md` — the profile stays short, structured, and declared; detail stays in documents
- `knowledge/decisions/profile-context-for-agents.md` — Vyasa gives the agent facts and instructions and never launches it
- `knowledge/decisions/deterministic-extraction-without-llm.md` — Vyasa stores no model output of its own
- `knowledge/concepts/untrusted-content.md` — report text is data, never instructions
- `knowledge/decisions/project-report-in-the-repository.md` — created by this package

## Intent

The profile says what a project is in short, bounded fields. A coding agent working in a repository can understand far more than that: how it is built, how the parts fit, how to run it, what is risky. That understanding should be written down once, inside the repository, in a shape any later agent can fetch through Vyasa without opening the repository. Vyasa supplies the template and the deterministic facts, the agent supplies the reading, and a rescan brings the result into the index.

## Scope

- **Included:**
  - A markdown report at `.vyasa/project-report.md` with fixed section names.
  - A template served over MCP, with no index needed.
  - Reading the report during a scan, bounded, section by section, with its source and time.
  - Serving the stored report over MCP, whole or by section.
  - Report status in `get_project` (present, sections, sizes), without the text.
- **Excluded:**
  - Vyasa writing the report, or calling any model.
  - Report text used for identity, search ranking, or any decision.
  - Parsing the report body (code blocks, links) beyond section splitting.
- **Deferred:**
  - Per-repository limits (limits are per installation).
  - Staleness comparison against the repository head commit.
  - Multiple reports per repository (monorepo components).
  - Full-text search over reports.

## Requirements

### FR-028 — Project Report (P1)

Vyasa MUST provide a report template to coding agents over MCP, MUST read `.vyasa/project-report.md` during a scan, and MUST serve its stored content over MCP.

- The template MUST list the sections, what each is for, the limits, the file path, and the rules for the writer, including that facts come from the repository and that unknown items are omitted rather than guessed.
- The template MUST work without an index.
- The scan MUST read the file as text only when `.vyasa` is a real directory and the file is a real file, at most the file limit, and MUST NOT run anything from it.
- The scan MUST keep the sections whose heading is in the template, up to the section limit each, and MUST report each heading it drops and why.
- The file limit (default 256 KiB) and the section limit (default 16 KiB) MUST be configurable in `config.toml` under `report`, MUST be validated against fixed bounds, and MUST be stored with each observation and shown in the template when known.
- A stored report MUST carry its source (the checkout), the time of the scan, and the content hash; the text MUST be marked as declared by the repository.
- The report MUST be served only from the index, MUST include no local path of the machine, and MUST be returned as data.
- A missing report MUST be an ordinary state (`not_present`), distinct from `unreadable` and `invalid`.
- A report failure MUST NOT stop the scan or remove previously valid data of other kinds.
- Vyasa MUST NOT write the report and MUST NOT launch an agent.

## Expected Behaviour

Observable behaviour is specified as Gherkin scenarios in `features/`. The owner confirmed every grill recommendation on 2026-10-28, so all scenarios are normative.

## Constraints

- The scanner stays read-only (DOR-005, DOR-006).
- Report text is untrusted repository content (NFR-020).
- The MCP server stays read-only and opens no network listener.
- Report text is machine-local in phase 1 and is not synchronized.

## Acceptance Expectations

- Before/after hash of a repository proves a scan changes nothing.
- The template, the section reader, and the limits come from one definition and cannot drift.
- A hostile report (huge, nested, control characters, credential URLs) cannot break the scan or the server.

## Open Decisions

| Decision | Recommended direction | Grill |
|---|---|---|
| PR-001 | A markdown report beside the profile; the profile stays the structured summary. | Q1 |
| PR-002 | The scan stores a bounded copy; the MCP serves from the index. | Q2 |
| PR-003 | Fixed H2 section names; others are dropped and reported. | Q3 |
| PR-004 | Limits are configurable; defaults 256 KiB file and 16 KiB per section; hard bounds apply. | Q4 |
| PR-005 | Staleness comparison with the head commit is deferred. | Q6 |

## Delivery

Proposed OpenSpec change, as vertical slices (`knowledge/practices/vertical-slices.md`):

- `be-project-report`: template and tool, report reading and storage, report tool, status in `get_project`.
