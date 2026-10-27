# Vyasa (व्यास) — Data Ownership and Source of Truth

**Document:** `docs/requirements/data-ownership.md`  
**Product:** Vyasa — Workspace Intelligence MCP  
**Status:** Draft v0.1  
**Related Documents:**
- `knowledge/product/vision.md`
- `knowledge/product/scope-and-roadmap.md`
- `docs/requirements/functional-requirements.md`
- `docs/requirements/non-functional-requirements.md`

---

## 1. Purpose

This document defines ownership, authority, precedence, and synchronization rules for project information managed or discovered by Vyasa.

Vyasa receives information from multiple sources:

- Local repository files and Git metadata.
- Project-maintained documentation and canonical profiles.
- Generated draft profiles.
- The local SQLite index.
- The shared Google Sheets registry.
- GitHub and Bitbucket APIs.

These sources serve different purposes and must not be treated as interchangeable authorities.

The central rule is:

> **The source that owns a piece of information determines who may change it. Vyasa may discover, index, and expose information, but it must not silently overwrite information owned by a project maintainer or another authoritative source.**

This document defines the ownership model independently of any particular database schema or MCP tool implementation.

## 2. Core Principles

### 2.1 One Authoritative Owner per Field

Every managed field must have a defined owner and an explicit policy for accepting updates.

Multiple sources may provide observations about the same field, but only the designated owner may change its authoritative value.

### 2.2 Repository-Owned Knowledge

Project-specific knowledge belongs to the project repository and its maintainers.

Examples include:

- Project purpose and goals.
- Architectural decisions and conventions.
- Development instructions.
- Project-specific lifecycle declarations.
- Human-authored project profiles.

Vyasa reads and indexes this information. It does not become the authoring authority for it.

### 2.3 Detected Facts Are Observations

Information discovered from files or repository configuration is an observation about the repository at a particular time.

For example, finding `pyproject.toml` is evidence that a recognized Python project manifest exists. It is not, by itself, proof that every dependency declared elsewhere is installed or that a particular framework is actively used.

Vyasa must retain the distinction between observed evidence and authoritative declarations.

### 2.4 Generated State Is Not Project Knowledge

The SQLite index, scan history, evidence inventory, and machine-specific repository mappings are operational state maintained by Vyasa.

They may be updated automatically without changing project-owned documentation.

### 2.5 Shared Registry Data Has Explicit Ownership

Google Sheets provides shared project visibility and may contain human-maintained portfolio fields.

A successful synchronization must not automatically grant Vyasa ownership of every field in the workbook.

### 2.6 No Silent Conflict Resolution

When two authoritative sources disagree, Vyasa must apply a previously defined resolution rule or report the conflict. It must not select a value arbitrarily.

### 2.7 Unknown Is a Valid State

If an authoritative source does not provide a value, Vyasa should preserve that absence explicitly.

It must not invent values merely to populate a complete-looking project record.

---

## 3. Ownership Categories

Each field must belong to one of the following ownership categories.

| Category | Owner | Examples |
|---|---|---|
| Repository-owned | Project maintainers | Purpose, project conventions, canonical profile |
| Repository-observed | Repository state, observed by Vyasa | Detected manifests, README presence, Git remote |
| Vyasa-generated | Vyasa | Local index, scan results, evidence inventory |
| Portfolio-owned | Authorized human portfolio maintainer | Tracking level, review notes, portfolio priority |
| Provider-owned | External platform | Provider repository ID, provider visibility, provider-reported metadata |
| Machine-local | Current device or Vyasa installation | Clone paths, workspace roots, local configuration |
| Derived | A deterministic rule applied to owned or observed inputs | Related-project matches, completeness indicators |

A derived value is not an independent source of truth. It must remain traceable to its inputs and the rule that produced it.

## 4. Canonical Sources of Truth

### 4.1 Local Repository

The local repository is authoritative for the files and Git metadata actually observed in that checkout.

It is the primary source for Phase 1 discovery.

Examples:

- A recognized manifest exists in the current checkout.
- A README exists at a particular path.
- A Git remote is configured in the local repository.
- A recognized OpenSpec configuration is present.

A local checkout may be incomplete, stale, or divergent from the remote repository. Vyasa must not assume that local state and remote state are identical.

### 4.2 Canonical Project Profile

A canonical project profile is a project-maintained document that provides explicit project metadata.

The exact canonical path and schema must be finalized before implementation.

Proposed convention:

- `.vyasa/project-profile.toml`

Alternative:

- `VYASA.md` at the repository root.

Only one canonical format should be selected as the primary authority for structured profile fields. If both formats are eventually supported, precedence and duplicate-field handling must be explicitly specified.

The canonical profile:

- Is owned and maintained by the project owner.
- May be committed to version control.
- Must not be overwritten by the scanner.
- Must be parsed using a documented schema.
- Must be treated as untrusted input and validated before use.

### 4.3 Generated Draft Profile

A generated draft profile is an optional convenience for repositories that lack a canonical profile.

Proposed location:

- `.vyasa/project-profile.draft.toml`

The draft should be git-ignored by default.

The draft:

- Contains only supported facts and clearly marked missing fields.
- Must be distinguishable from the canonical profile.
- Must never override the canonical profile.
- Must never be automatically promoted to canonical status.
- Must never be committed automatically by Vyasa.
- May be regenerated only according to an explicit draft lifecycle policy.

If a canonical profile already exists, draft generation must not overwrite it or create a competing draft that appears authoritative.

The maintainer remains responsible for reviewing the draft and deciding whether to create or update the canonical profile.

**Important:** Draft generation is optional and must be explicitly enabled if it writes a file. Ordinary scanning remains read-only.

### 4.4 SQLite Index

SQLite is authoritative only for Vyasa's local generated state.

It owns:

- Local project index records.
- Local filesystem mappings.
- Scan and refresh history.
- Cached observations.
- Evidence references.
- Local freshness and error status.
- Local database schema version.
- Local mapping between a logical project and its checkouts.

SQLite is not authoritative for project-maintained descriptions, human-managed portfolio fields, or the current state of an inaccessible remote repository.

### 4.5 Google Sheets Registry

Google Sheets is the shared portfolio registry introduced in Phase 2.

It owns only explicitly designated shared fields, such as:

- Portfolio tracking level.
- Human-managed review notes.
- Portfolio priority, if approved.
- Other explicitly assigned portfolio-management fields.

It may also hold synchronized copies of repository-owned or repository-observed fields. Such copies are shared representations, not automatically new authorities for those fields.

A local scan must not overwrite a human-managed field merely because that field is stored in the same spreadsheet row.

### 4.6 GitHub and Bitbucket APIs

Remote providers are authoritative for provider-owned facts, including provider identifiers and repository properties exposed by their APIs.

Examples include:

- Provider repository ID.
- Provider URL.
- Provider visibility, where available.
- Provider-reported default branch.
- Provider-reported repository state.

For remote file content, the relevant remote repository revision is the source of the observed file data.

A provider API response must not silently replace a local observation made against a different revision. Both observations may be retained, with their sources and timestamps.

---

## 5. Field-Level Ownership Matrix

The following matrix defines the proposed initial ownership model.

| Field | Authoritative owner | Local SQLite | Google Sheets |
|---|---|---|---|
| Project ID | Vyasa identity rules | Store | Store shared ID |
| Project name | Canonical profile if declared; otherwise defined repository evidence | Cache | Synchronized copy |
| Project purpose | Canonical project profile or explicit project documentation | Cache | Approved summary/copy |
| Git remote URL | Observed local Git config or remote provider, with source context | Store observations | Approved URL |
| Provider repository ID | GitHub or Bitbucket | Store when available | Store when approved |
| Programming languages | Deterministic repository observations | Store | Synchronized summary |
| Frameworks and technologies | Recognized manifests/configuration evidence | Store | Synchronized summary |
| README presence and path | Current repository observation | Store | Share presence; exclude local-only paths |
| Documentation structure | Deterministic repository observation | Store | Share approved summary |
| OpenSpec presence/configuration | Recognized repository evidence | Store | Share status |
| OKF status | OKF detector over declared bundles (`knowledge/technologies/okf.md`) | Store | Share status |
| Agent instruction files | Recognized repository evidence | Store | Share approved names/status |
| Test indicators | Recognized repository evidence | Store | Share summary |
| README quality | Explicitly defined deterministic assessment, or not assessed | Store status | Share status if approved |
| Lifecycle status | Canonical profile or authorized portfolio owner, depending on field definition | Cache | Store portfolio-owned value if applicable |
| Tracking level | Portfolio maintainer | Cache synchronized value if needed | Authoritative |
| Portfolio priority | Portfolio maintainer, if enabled | Cache synchronized value if needed | Authoritative |
| Portfolio notes | Portfolio maintainer | Cache synchronized value if needed | Authoritative |
| Local clone path | Current device | Authoritative local mapping | Never export |
| Workspace root | Current device | Authoritative local configuration | Never export |
| Local scan timestamp | Vyasa scan operation | Authoritative locally | Shared scan timestamp only under defined semantics |
| Local scan status | Vyasa scan operation | Authoritative locally | Share only a clearly labeled summary if needed |
| Remote scan timestamp | Vyasa remote discovery operation | Cache | Shared only under defined semantics |
| Provider visibility | Remote provider | Cache | Synchronized copy if approved |
| Generated draft profile | Vyasa, as a non-authoritative draft producer | Optional local file/state | Never export as canonical |
| Related-project relationship | Deterministic relation rules | Derived cache | Optional derived summary |
| Obsolete-project candidate | Deterministic review rules | Derived state | Optional review flag, never automatic lifecycle change |

This table is the initial ownership proposal. Fields marked as conditional or awaiting definition must be finalized before their associated functionality is implemented.

---

## 6. Field Precedence Rules

Precedence is field-specific. There must not be one universal rule that makes one source override every other source.

### 6.1 Project Name

Proposed resolution order:

1. Canonical project profile, when it declares a valid project name.
2. Explicit project name from a recognized manifest or other configured authoritative source.
3. Repository directory name as a fallback.

Vyasa should retain the original observed values and evidence where useful.

A name change must not automatically create a new project identity.

### 6.2 Project Purpose

Proposed resolution order:

1. Canonical project profile.
2. Explicit project purpose in a recognized documentation field.
3. Unknown or not documented.

Vyasa must not infer purpose from the programming language, framework, directory name, or unrelated file names.

### 6.3 Technologies and Dependencies

Recognized manifests and configuration files provide the evidence for supported technology and dependency detections.

If multiple manifests disagree, Vyasa should preserve the source-specific observations or apply documented detector rules. It must not invent a single universal dependency list without accounting for project structure, optional groups, workspaces, and environment-specific files.

### 6.4 Repository Identity

Stable identity should use normalized repository identity when reliable remote identity is available.

Display names, directory names, and URLs are attributes used to resolve or display identity; they are not universally reliable standalone identifiers.

Provider-specific identifiers should be retained when available.

Forks, mirrors, renamed repositories, and multiple repositories belonging to one logical project require explicit identity and relationship rules.

### 6.5 Portfolio Fields

Portfolio-owned fields are controlled by authorized maintainers in the shared registry or another explicitly selected portfolio-management source.

Local scans must not overwrite these fields.

If portfolio fields are cached locally, the cached values must retain their ownership and synchronization metadata.

### 6.6 Conflicting Sources

When sources disagree:

1. Identify the field and its designated owner.
2. Identify the source and observation time for each value.
3. Apply the field-specific precedence policy if it resolves the conflict.
4. Otherwise mark the conflict and retain enough evidence for review.
5. Never silently overwrite a human-owned value with a detected value.

---

## 7. Data Classification and Storage Boundaries

### 7.1 Local-Only Data

The following data must remain local by default:

- Absolute filesystem paths.
- Workspace root paths.
- Local database path.
- Machine-specific checkout mappings.
- Local environment details.
- Authentication credentials and tokens.
- Secrets discovered accidentally in repository content.
- Local-only error diagnostics containing sensitive information.

These fields must never be included in shared registry exports unless a future, explicit and approved requirement changes the policy for a particular field.

### 7.2 Shareable Project Metadata

Potentially shareable metadata includes:

- Stable project ID.
- Project name.
- Repository URL.
- Programming languages.
- Frameworks and technologies.
- Documentation and standards status.
- Explicitly approved lifecycle information.
- Shared registry fields maintained by humans.

Only fields in an explicit export allowlist may be synchronized.

A field being present in the local database does not automatically make it eligible for export.

### 7.3 Secrets and Sensitive Content

Vyasa must not deliberately collect or synchronize secret values.

Recognizing a configuration file does not authorize reading every value in it. Each detector should read only the information needed for its documented purpose.

Logs and error messages must not expose credentials or secret values.

---

## 8. Synchronization Ownership Rules

These rules apply when Google Sheets integration is introduced in Phase 2.

### 8.1 Export

When publishing local observations to Google Sheets:

- Export only allowlisted fields.
- Include stable project identity.
- Preserve source and timestamp information where useful.
- Exclude local paths and secrets.
- Update only fields owned by the local synchronization process.
- Preserve portfolio-owned fields.

### 8.2 Import

When importing shared registry data:

- Import only explicitly designated shared fields.
- Validate values against the registry schema.
- Preserve field ownership.
- Do not treat a shared copy of a detected fact as fresher than a direct observation merely because the spreadsheet was edited more recently.
- Do not write imported portfolio fields into a canonical project profile automatically.

### 8.3 Conflicts

A conflict exists when two sources attempt to change the same field or when the source of an authoritative value is ambiguous.

The synchronization process must:

- Identify the field.
- Identify the relevant sources and versions or timestamps.
- Apply the documented ownership policy.
- Record unresolved conflicts.
- Avoid destructive last-write-wins behaviour for human-maintained fields.

### 8.4 Retry Safety

Repeated synchronization must not create duplicate project rows or reset human-maintained fields.

If synchronization partially fails, successful updates may be retained, but the overall result must report partial completion and permit safe retry.

### 8.5 Registry Schema Changes

Changes to spreadsheet columns, field definitions, or ownership rules must be versioned or otherwise detected.

Vyasa must validate the registry structure before performing writes that could place values in incorrect columns.

---

## 9. Remote Repository Ownership Rules

These rules apply in Phase 3.

### 9.1 Local and Remote Observations

Local and remote observations must be distinguishable.

For example, a local checkout may contain uncommitted changes while the remote default branch contains a different README. Both observations may be valid for their respective sources.

Vyasa must not merge them into a fictional single repository state.

### 9.2 Revision Awareness

Where practical, remote file observations should identify the commit or revision inspected.

Local observations should record enough context to identify when the files were scanned and which local repository they came from.

### 9.3 Provider Metadata

Provider-owned values should be refreshed from the corresponding provider when a successful authorized query is performed.

A failed API request must not be interpreted as proof that the repository was deleted or made private.

### 9.4 Matching and Reconciliation

When matching local, shared, and remote records:

- Use stable identity evidence.
- Preserve the provenance of matched observations.
- Flag ambiguous matches.
- Avoid automatic destructive merging.
- Retain separate repository identities when a relationship is not established.

---

## 10. Project Profile Lifecycle

The profile lifecycle must follow a controlled sequence.

### 10.1 Discovery

Vyasa scans the repository and extracts supported metadata into its local index.

No repository file is modified during ordinary scanning.

### 10.2 Optional Draft Generation

If draft generation is explicitly enabled and no canonical profile exists, Vyasa may generate a draft.

The draft must:

- Follow the agreed git-ignored location.
- Contain only supported values.
- Identify missing or uncertain fields.
- Be clearly marked as generated and non-authoritative.
- Never overwrite a canonical profile.

### 10.3 Human Review

A maintainer reviews the draft and decides whether to create a canonical profile.

The promotion process is a human action, not an automatic scanner operation.

### 10.4 Canonical Maintenance

The canonical profile becomes the authoritative source for fields assigned to it.

The maintainer or the project's normal development workflow updates it. Vyasa reads the new values during subsequent scans.

### 10.5 Subsequent Scans

Vyasa may refresh its local observations and index.

It must not automatically regenerate or overwrite the canonical profile.

If a generated draft already exists and its source observations change, the draft lifecycle policy must define whether it is preserved, marked stale, or regenerated. This policy must avoid destroying manual edits to a draft.

---

## 11. Derived Data Ownership

Some information is calculated from other fields rather than directly authored.

Examples include:

- Related-project matches.
- Project documentation completeness indicators.
- Potential duplicate flags.
- Potential obsolete-project review flags.
- Technology-based search facets.

For derived data:

1. The calculation rule must be documented.
2. Inputs must retain their source provenance.
3. The derived value must be reproducible from those inputs and the rule version.
4. Stale inputs must be reflected in the derived result.
5. Derived results must not be treated as human declarations.
6. A review flag must not automatically change a project's lifecycle status.

---

## 12. Ownership Enforcement Requirements

### DOR-001 — Field Ownership Registry

Every persisted field that may be changed by scanning, synchronization, or human editing must have a defined ownership category.

### DOR-002 — Source Provenance

Extracted and synchronized values must retain sufficient provenance to distinguish their origins.

### DOR-003 — No Silent Overwrite

A process must not overwrite a field owned by another source without an explicit, documented authorization rule.

### DOR-004 — Local Data Isolation

Machine-specific information must not enter shared exports.

### DOR-005 — Draft Isolation

Generated draft profiles must remain distinct from canonical project profiles.

### DOR-006 — Explicit Promotion

Draft-to-canonical promotion must require a human decision or a separately approved workflow.

### DOR-007 — Conflict Visibility

Unresolved conflicts must be visible through appropriate status, diagnostics, or review output.

### DOR-008 — Deterministic Derived Data

Derived fields must be reproducible and must not be presented as independently authored facts.

### DOR-009 — Safe Failure

Failed scans and synchronization operations must not silently destroy previously valid information.

### DOR-010 — Schema Validation

Canonical profiles and shared registry records must be validated before their fields are accepted into the internal model.

### DOR-011 — Export Allowlist

Shared synchronization must use an explicit field allowlist, not a blanket export of the local project object.

### DOR-012 — Testable Ownership

Automated tests must verify that each adapter respects field ownership and conflict policies.

---

## 13. Ownership Examples

### Example A — README Removed

A project previously had a README. The file is removed from the current checkout.

Expected behaviour:

- A successful scan updates the local observation to indicate that the README is not currently detected.
- The old observation remains available in scan history if the implementation retains history.
- The canonical profile is not modified.
- The shared registry is updated only according to its field ownership and synchronization policy.

### Example B — Human Changes Project Purpose

A maintainer updates the purpose field in the canonical project profile.

Expected behaviour:

- Vyasa reads the new declared value.
- The local index reflects the updated profile after a successful scan.
- The scanner does not replace the purpose with a directory-name or technology-based guess.
- The shared registry receives an approved copy during synchronization if the field is allowlisted.

### Example C — Portfolio Tracking Level Changed in Sheets

A portfolio maintainer changes a project's tracking level.

Expected behaviour:

- The shared registry remains authoritative for that field.
- Local scanning does not overwrite it.
- If the local application caches the value, it imports it according to the synchronization policy.
- The canonical project profile is not modified automatically.

### Example D — Local and Remote README Differ

A local checkout has a modified README, while the remote repository has a different committed version.

Expected behaviour:

- Local and remote observations remain distinguishable.
- Evidence identifies the relevant source and, where practical, revision.
- Vyasa does not claim that the two README versions are identical.
- No repository content is modified.

### Example E — Project Not Accessible on a New Device

A project exists in Google Sheets, but its repository is not cloned on the current device.

Expected behaviour:

- Vyasa can return the shared project metadata.
- Local source availability is reported as unavailable on this device.
- A local path from another device is not exposed as a usable local path.
- No local clone is created automatically.

---

## 14. Decisions Required Before Implementation

| ID | Decision | Recommendation |
|---|---|---|
| DO-001 | Canonical profile format | Choose one structured canonical format; `.vyasa/project-profile.toml` is a reasonable candidate. |
| DO-002 | Human-readable profile | Decide whether a root-level `VYASA.md` is required in addition to the structured profile. Avoid maintaining two independent authorities for the same fields. |
| DO-003 | Draft generation | Keep it optional, git-ignored, and separate from the canonical profile. |
| DO-004 | Project ID algorithm | Define normalized remote identity and deterministic local fallback behaviour. |
| DO-005 | Project purpose precedence | Approve the canonical profile and explicit-documentation precedence rules. |
| DO-006 | Portfolio-owned fields | Finalize tracking level, priority, notes, and any other human-managed fields. |
| DO-007 | Lifecycle ownership | Decide whether lifecycle status is project-owned, portfolio-owned, or split into distinct fields. |
| DO-008 | Synchronization conflict policy | Define field-specific handling for concurrent edits and stale observations. |
| DO-009 | Shared scan timestamps | Decide whether timestamps represent local scanning, remote scanning, or last successful synchronization. Keep these meanings distinct. |
| DO-010 | Remote source revision | Define the revision metadata retained for remote file observations. |

No implementation should silently treat these recommendations as approved decisions.

---

## 15. Governing Rule

Vyasa must maintain a clear boundary between **what a project declares, what a scanner observes, what a person manages centrally, and what Vyasa calculates for convenience**.

Repository maintainers own project knowledge. Vyasa owns its generated index and observations. Portfolio maintainers own designated shared management fields. Remote providers own their provider-specific metadata.

**Synchronization shares information; it does not transfer ownership.**
