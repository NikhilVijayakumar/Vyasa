# Vyasa (व्यास)

**Workspace Intelligence MCP**

A local-first project intelligence system that helps coding agents discover, understand, and reuse knowledge across software projects.

Vyasa maintains a structured index of software projects across local workspaces and, eventually, remote Git repositories. It exposes project information through the Model Context Protocol (MCP), synchronizes shared project metadata across devices using Google Sheets, and supports remote repository discovery through platform APIs.

The goal is simple: **help coding agents understand what already exists before building something new.**

---

## 1. Vision

Software projects often become difficult to manage as the number of repositories, domains, experiments, and applications grows. Although individual repositories may be well organized, their information remains distributed across different workspaces and documentation.

This creates several problems:

- Developers must remember which repository contains a particular implementation.
- Coding agents have limited awareness of projects outside their current workspace.
- Existing libraries and solutions may be recreated unnecessarily.
- Project status, technology stacks, and documentation quality are difficult to review centrally.
- Moving between devices makes it harder to retain useful project context.
- Obsolete, duplicated, or abandoned projects are difficult to identify.

Vyasa addresses these problems through a shared project index, local MCP access, and cross-device metadata synchronization.

## 2. Core Objectives

1. Discover projects across configured local workspace roots.
2. Maintain structured metadata about each project.
3. Detect programming languages, frameworks, and relevant development conventions.
4. Track README files, documentation, OpenSpec, OKF, and tests.
5. Expose project discovery and context retrieval through MCP.
6. Synchronize shared project information through Google Sheets.
7. Preserve machine-specific information locally.
8. Support future discovery of remote GitHub and Bitbucket repositories without cloning them.
9. Help identify related projects, reusable components, and potential obsolete projects.

## 3. Implementation Roadmap

Vyasa will be implemented in three phases.

### Phase 1 — Local Workspace Intelligence MCP

**Objective:** Deliver a fully usable local MCP server that provides cross-project awareness to coding agents.

Scope:

- Configurable workspace roots and exclusion rules.
- Local project discovery and classification.
- Git repository and origin detection.
- Programming language and framework detection.
- README and documentation discovery.
- OpenSpec and OKF detection.
- Test presence detection.
- Local SQLite project index.
- Stable project identifiers.
- Project summaries and tracking levels.
- Incremental rescanning and index freshness.
- MCP tools for project search, context retrieval, related-project discovery, and index status.
- Evidence references for detected information.
- Local-only storage of clone locations and machine-specific metadata.

Phase 1 must operate independently of Google Sheets and remote repository APIs.

The core data model and synchronization boundary must be designed during this phase, but Google Sheets integration will not be implemented until Phase 2.

**Completion criteria:**

- An MCP-compatible coding agent can discover and query indexed projects.
- Project information is traceable to repository evidence.
- Local clone paths remain local.
- Repeated scans update existing records instead of creating duplicates.
- The index remains usable without external services.

### Phase 2 — Google Sheets Synchronization

**Objective:** Provide a shared project registry accessible from multiple devices.

Scope:

- Google Sheets API integration.
- Project Registry worksheet.
- Documentation & Standards worksheet.
- Scan History worksheet.
- Safe synchronization and idempotent updates.
- Stable cross-device project identity.
- Field ownership and conflict handling.
- Retry and error reporting.
- Preservation of human-maintained fields.
- Strict separation of shared metadata and local-only information.
- Ability to discover existing shared records on a new device.

Google Sheets is the shared cross-device registry, not a replacement for local project repositories.

**Completion criteria:**

- Project metadata can be synchronized from multiple devices.
- Existing project records are updated rather than duplicated.
- Local clone paths and machine-specific information are never exported.
- Synchronization failures do not invalidate the local index.
- Conflicting edits are detected and handled according to defined rules.

### Phase 3 — Remote Repository Discovery

**Objective:** Extend Vyasa to discover and analyze repositories hosted remotely, without cloning or checking out their source code.

Initial platforms:

- GitHub public repositories.
- Private Bitbucket Cloud repositories through appropriately scoped authentication.

Scope:

- Repository enumeration.
- Repository metadata retrieval.
- Remote README and manifest inspection.
- Programming language and framework detection.
- Documentation and OpenSpec detection.
- Remote repository identity and project mapping.
- Pagination, rate-limit handling, and API error recovery.
- Authentication configuration and secret management.
- Detection of potential duplicates and obsolete-project candidates.

Remote repositories will use the same core project model as locally discovered repositories.

**Completion criteria:**

- Accessible remote repositories can be inventoried without checkout.
- Remote project metadata can be synchronized to Google Sheets.
- Local and remote records can be related without creating unnecessary duplicates.
- Potentially obsolete projects are flagged for human review rather than automatically deleted or archived.

## 4. Architecture

Vyasa follows a modular, local-first architecture.

```text
                    Coding Agents
                          |
                     MCP Server
                          |
              Workspace Intelligence Core
                          |
          +---------------+---------------+
          |               |               |
     Discovery        Project Model    Retrieval
          |               |               |
     Local Scanner    Validation       Search
          |               |
          +------- Local SQLite ---------+
                          |
               Phase 2: Sheets Adapter
                          |
                 Google Sheets
                          |
              Phase 3: Repository APIs
                     /          \
                 GitHub       Bitbucket
```

The architecture is conceptual and does not prescribe a specific implementation language.

### Core components

**Workspace Discovery**

Discovers eligible project roots, Git repositories, manifests, and documentation entry points.

**Project Catalog**

Maintains stable project identifiers, project metadata, tracking levels, relationships, and lifecycle information.

**Technology Detection**

Detects programming languages, frameworks, dependencies, and relevant development tools from available evidence.

**Documentation Analysis**

Tracks documentation presence and structure, README files, OpenSpec, OKF, recognized agent instructions, and tests.

**Local Index**

Stores project records, local paths, scan state, indexed metadata, and other machine-specific information.

**MCP Interface**

Exposes project search, project details, context retrieval, related-project discovery, dependency lookup, and index status to coding agents.

**Google Sheets Adapter**

Synchronizes approved shared metadata with the cross-device project registry.

**Remote Repository Adapters**

Introduced in Phase 3 to discover and inspect repositories through platform APIs.

## 5. Project Tracking Model

Vyasa supports different tracking levels because not every project requires detailed analysis.

| Tracking level | Description |
|---|---|
| `inventory` | Project identity, repository origin, technologies, and basic metadata |
| `summary` | Inventory plus purpose, documentation, and high-level status |
| `detailed` | Summary plus current objectives, decisions, blockers, relationships, and next actions |
| `excluded` | Excluded from normal indexing and tracking |

A project can move between tracking levels without changing its identity.

### Project metadata

The shared project record should support:

- Stable project ID.
- Project name.
- Domain and project type.
- Remote repository identity and URL, when applicable.
- Programming languages.
- Frameworks and technologies.
- Lifecycle status.
- Tracking level.
- Project purpose, when available.
- Documentation profile.
- OpenSpec status.
- OKF status.
- Test presence.
- Recognized agent instruction files.
- Last scan timestamp.
- Analysis and verification status.
- Related projects and dependencies, when known.

Fields that cannot be verified must be represented as unknown or requiring review rather than fabricated.

## 6. Google Sheets Structure

Google Sheets will contain three worksheets.

### Project Registry

One row per logical project.

Suggested fields:

- Project ID
- Project Name
- Domain
- Project Type
- Git Origin
- Repository URL
- Programming Languages
- Frameworks & Technologies
- Lifecycle Status
- Tracking Level
- Last Scanned
- Details Status

### Documentation & Standards

One row per project.

Suggested fields:

- Project ID
- README Present
- README Quality
- Documentation Present
- Documentation Structure
- OpenSpec Enabled
- OpenSpec Configuration
- OKF Enabled
- Agent Instructions
- Tests Present
- Documentation Entry Point

OKF means Google Cloud's [Open Knowledge Format](knowledge/technologies/okf.md); Vyasa recognizes bundles that declare `okf_version` and reports their version and conformance.

### Scan History

Records scan and synchronization activity.

Suggested fields:

- Run ID
- Timestamp
- Scan Scope
- Projects Discovered
- Projects Added or Updated
- Projects Requiring Review
- Skipped Projects
- Errors
- Synchronization Result

The exact worksheet schema should be finalized before Phase 2 implementation.

## 7. Local-Only Information

Machine-specific information must never be synchronized to Google Sheets.

Examples include:

- Absolute clone paths.
- Local workspace roots.
- Machine-specific filesystem metadata.
- Local index database locations.
- Credentials, API tokens, and secrets.
- Other explicitly excluded local information.

The local index may contain a mapping such as:

`Project ID -> Local Clone Path`

Google Sheets may contain:

`Project ID -> Remote Repository URL`

The shared registry must not expose the local clone path.

The Sheets adapter must use an explicit allowlist of exportable fields rather than attempting to remove sensitive fields from a complete local record.

## 8. Design Principles

### Local-first

Phase 1 must be fully functional without Google Sheets or remote APIs.

### Modular architecture

Core project logic must not depend directly on MCP, Google Sheets, GitHub, or Bitbucket.

### Evidence-based detection

Detected technologies and project characteristics should reference the files or metadata that support them.

### Incremental scanning

Rescanning should update existing records and avoid unnecessary repeated analysis.

### Stable identity

Projects must retain stable identifiers when directory names change or records are synchronized across devices.

### Safe synchronization

Synchronization must be idempotent, preserve human-maintained fields, and handle conflicts explicitly.

### Privacy by design

Local filesystem paths and credentials must not be exported to shared systems.

### Human-controlled lifecycle decisions

Vyasa may recommend that a project is obsolete, duplicated, or abandoned. It must not automatically delete or archive projects.

### Progressive implementation

Each phase must deliver independently useful functionality while preserving compatibility with later phases.

## 9. Non-Goals

Vyasa is not intended to:

- Replace GitHub, Bitbucket, or Git.
- Replace project management tools.
- Replace existing project documentation.
- Clone or check out remote repositories for inventory purposes.
- Automatically rewrite project documentation during discovery.
- Automatically delete or archive obsolete projects.
- Upload complete source repositories to Google Sheets.
- Store credentials in the project registry.
- Require every project to receive detailed AI analysis.

## 10. Security and Reliability

- Restrict scanning to configured workspace roots.
- Support exclusions for generated directories, secrets, and unrelated content.
- Keep API credentials in secure local configuration or a secret store.
- Use read-only repository permissions wherever possible.
- Validate records before synchronization.
- Detect missing or moved projects without immediately deleting their records.
- Record scan and synchronization errors.
- Distinguish last scan time from last successful content verification.
- Avoid presenting stale metadata as freshly verified information.

## 11. Implementation Approach

Implementation should proceed phase by phase.

Before coding each phase:

1. Establish the detailed requirements.
2. Define the relevant data contracts and interfaces.
3. Identify acceptance criteria.
4. Implement the smallest useful vertical slice.
5. Add automated tests.
6. Verify behavior using representative repositories.
7. Update the documentation and implementation status.

The project must not treat planned capabilities as implemented until they have been verified.

## 12. Success Criteria

Vyasa will be successful when:

- Coding agents can discover existing projects and reuse their knowledge.
- Project metadata is searchable across domains.
- Documentation and technology inventories are accurate and traceable.
- Shared project knowledge is available across devices.
- Local paths remain private to each device.
- Remote repositories can eventually be inventoried without checkout.
- Potentially obsolete projects can be identified for deliberate review.
- Adding new repository platforms does not require redesigning the core.

---

**Project name:** Vyasa (व्यास)

**Project type:** Local-first workspace intelligence and MCP server.

**Implementation strategy:** Local MCP → Google Sheets synchronization → Remote repository APIs.

**Guiding principle:** Organize knowledge about existing projects so that developers and coding agents can find and reuse it before creating something new.

---

## Development

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

Requires Python 3.12 or newer. The tests are platform independent; tests that need a directory symlink or a Windows junction skip with a stated reason where the platform cannot create one.

## Configuration

Vyasa scans only the workspace roots you list; nothing is scanned by default. Create `config.toml` in the data directory (`%LOCALAPPDATA%\Vyasa` on Windows, `~/Library/Application Support/Vyasa` on macOS, `~/.local/share/vyasa` on Linux), or point `VYASA_CONFIG` at a file, or set `VYASA_HOME` to move the data directory:

```toml
[workspace]
roots = ["E:/Python", "D:/Projects", "~/work"]
```

Use absolute paths. On Windows write them with forward slashes or in single quotes, for example `'E:\Python'`. Roots may sit on different drives. A root inside another is kept and reported.

### Telling Vyasa what to skip inside a repository

A repository can list directories Vyasa must not scan in a `.vyasaignore` file at its root, for example reference data for coding agents or large fixtures:

```text
# one directory pattern per line
data/novel/output     # a path from the repository root
fixtures              # a name, at any depth
data/*/cache          # * stays inside one folder, ** crosses folders, ? is one character
```

The file can only remove directories from scanning. Negation (`!`), drive letters and `..` are reported and skipped, and a file over 64 KiB is ignored. When Vyasa skips directories because of the depth limit, its report says how many, gives examples, and suggests adding them here.
