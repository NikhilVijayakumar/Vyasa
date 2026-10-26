# Vyasa (व्यास) — Functional Requirements

**Document:** `docs/requirements/functional-requirements.md`  
**Status:** Draft v0.1  
**Product:** Vyasa — Workspace Intelligence MCP  
**Related Documents:** `docs/product/vision.md`, `docs/product/scope-and-roadmap.md`

## 1. Purpose

This document defines the functional behaviour required of Vyasa.

It specifies how Vyasa discovers projects, extracts metadata, maintains its local index, exposes project information through MCP, synchronizes shared metadata, and discovers remote repositories.

Requirements are written to be verifiable through automated tests or explicit acceptance checks.

## 2. Requirement Conventions

Requirements use stable identifiers to support traceability between specifications, implementation tasks, and tests.

- **MUST:** Required for acceptance.
- **SHOULD:** Recommended unless a documented reason justifies an exception.
- **MAY:** Optional capability.

Phase labels identify the intended delivery phase:

- **P1:** Phase 1 — Local Workspace Intelligence.
- **P2:** Phase 2 — Shared Project Registry.
- **P3:** Phase 3 — Remote Repository Discovery.

Each scenario describes observable behaviour rather than prescribing internal implementation details unless a specific implementation constraint is essential.

## 3. Functional Areas

| ID | Area | Phase |
|---|---|---|
| FR-001 | Configuration and workspace roots | P1 |
| FR-002 | Project and repository discovery | P1 |
| FR-003 | Project identity | P1 |
| FR-004 | Deterministic metadata extraction | P1 |
| FR-005 | Documentation and standards detection | P1 |
| FR-006 | Evidence and unknown values | P1 |
| FR-007 | Local project index | P1 |
| FR-008 | Incremental scanning and refresh | P1 |
| FR-009 | Project search | P1 |
| FR-010 | Project details and context | P1 |
| FR-011 | Related-project discovery | P1 |
| FR-012 | Project dependencies | P1 |
| FR-013 | MCP interface | P1 |
| FR-014 | Project profile lifecycle | P1 |
| FR-015 | Error handling and scan reporting | P1 |
| FR-016 | Shared registry synchronization | P2 |
| FR-017 | Cross-device project visibility | P2 |
| FR-018 | Remote repository discovery | P3 |
| FR-019 | Remote metadata inspection | P3 |
| FR-020 | Duplicate and obsolete candidates | P1–P3 |

# 4. Phase 1 — Local Workspace Intelligence

## FR-001 — Configuration and Workspace Roots

Vyasa MUST allow users to configure the local filesystem locations that it scans.

### Scenarios

**Scenario 1: Multiple workspace roots**

Given multiple workspace roots are configured, when Vyasa scans the workspace, then it discovers eligible projects within each configured root.

**Scenario 2: Excluded directories**

Given exclusion rules are configured, when the scanner encounters an excluded directory, then it does not discover projects beneath that directory.

**Scenario 3: Missing workspace root**

Given a configured root does not exist or is inaccessible, when scanning starts, then Vyasa reports the problem and continues scanning other accessible roots.

**Scenario 4: Invalid configuration**

Given configuration contains an invalid value, when Vyasa loads the configuration, then it reports a useful validation error instead of silently applying an unintended configuration.

**Scenario 5: No workspace roots**

Given no valid workspace roots are configured, when Vyasa starts, then it reports that workspace discovery is not configured and does not scan unintended filesystem locations.

## FR-002 — Project and Repository Discovery

Vyasa MUST discover eligible local projects and Git repositories according to documented discovery rules.

### Scenarios

**Scenario 1: Git repository**

Given a workspace contains a valid Git repository, when the scanner processes it, then Vyasa identifies the repository and records its available metadata.

**Scenario 2: Project without Git**

Given a workspace contains an eligible project directory without a Git repository, when the scanner processes it, then Vyasa may register it as a local project if it satisfies the documented discovery criteria.

**Scenario 3: Nested repositories**

Given a repository contains another Git repository, when the scanner processes the directory tree, then it follows documented nested-repository rules and does not accidentally merge their metadata.

**Scenario 4: Irrelevant directories**

Given a directory does not satisfy the project discovery criteria, when scanning completes, then it is not registered as a project solely because it exists.

**Scenario 5: Malformed repository**

Given a directory contains incomplete or malformed Git metadata, when scanning encounters it, then Vyasa reports the issue and continues processing other eligible projects.

**Scenario 6: Repeated discovery**

Given the same workspace is scanned repeatedly without relevant changes, when each scan completes, then Vyasa does not create duplicate project records.

## FR-003 — Project Identity

Vyasa MUST maintain stable project identity independently of a project's display name and local filesystem path wherever reliable identity evidence exists.

### Scenarios

**Scenario 1: Repository with a remote**

Given a repository has a supported, identifiable remote origin, when Vyasa registers the repository, then it derives identity using the documented repository identity rules.

**Scenario 2: Repository without a remote**

Given a repository has no usable remote, when Vyasa registers it, then it assigns a deterministic local fallback identity.

**Scenario 3: Directory rename**

Given a registered repository is moved or renamed while its repository identity remains unchanged, when the scanner rediscovers it, then Vyasa updates the local path mapping without creating an unnecessary duplicate.

**Scenario 4: Duplicate remote identity**

Given two local directories resolve to the same remote identity, when Vyasa scans them, then it detects the duplicate mapping and applies the documented policy rather than silently treating them as unrelated projects.

**Scenario 5: Ambiguous identity**

Given identity evidence is insufficient to determine whether two records represent the same project, when Vyasa processes them, then it preserves the uncertainty and flags the records for review.

**Scenario 6: Logical project with multiple repositories**

Given a logical project may span multiple repositories, when Vyasa discovers those repositories, then it does not automatically merge them unless the documented grouping rules establish the relationship.

## FR-004 — Deterministic Metadata Extraction

Vyasa MUST extract supported project metadata through documented, deterministic rules applied to recognized repository sources.

### Supported metadata categories

- Project name.
- Explicitly documented purpose or description.
- Git origin and repository URL.
- Programming languages.
- Frameworks and technologies.
- Recognized manifests and configuration files.
- Project-owned profile fields.
- Relevant source paths and observation timestamps.

### Scenarios

**Scenario 1: Project name**

Given a project has a recognized canonical name in an authoritative source, when Vyasa extracts metadata, then it uses that name according to the documented source precedence rules.

**Scenario 2: Explicit purpose**

Given a project purpose is explicitly documented in a recognized source, when Vyasa extracts metadata, then it records the documented value with its source.

**Scenario 3: Missing purpose**

Given no recognized source documents the project purpose, when Vyasa extracts metadata, then it marks the purpose as unknown or not documented.

**Scenario 4: Technology detection**

Given a project contains a recognized manifest declaring a supported dependency or framework, when Vyasa scans it, then it records the technology according to the corresponding detection rule.

**Scenario 5: Unsupported evidence**

Given a technology is mentioned only in an arbitrary text file that is not a recognized evidence source for that technology, when Vyasa scans the project, then it does not automatically report the technology as a confirmed dependency.

**Scenario 6: Conflicting sources**

Given multiple recognized sources provide conflicting values for a field, when Vyasa extracts metadata, then it follows a documented precedence policy or reports the conflict rather than silently choosing an arbitrary value.

**Scenario 7: Deterministic output**

Given repository files and configuration remain unchanged, when equivalent scans run under the same detector version, then the extracted facts remain consistent.

**Scenario 8: No LLM dependency**

Given the local indexing pipeline runs, when metadata is extracted and search results are generated, then no LLM is required to infer or fabricate project metadata.

## FR-005 — Documentation and Standards Detection

Vyasa MUST identify supported documentation, engineering configuration, and agent instruction artifacts.

### Required detection categories

- README presence and path.
- Documentation directories and recognized documentation entry points.
- Recognized documentation structure.
- OpenSpec directory and configuration presence.
- OpenSpec configuration validity according to supported rules.
- Presence of meaningful OpenSpec specification or change files.
- Recognized agent instruction files.
- Test-related files and configuration.
- Other explicitly supported conventions, once defined.

### Scenarios

**Scenario 1: README presence**

Given a repository contains a README matching a supported naming rule, when scanned, then Vyasa records its presence and path.

**Scenario 2: No README**

Given no supported README is found, when scanned, then Vyasa records that the README was not detected.

**Scenario 3: OpenSpec directory only**

Given a repository contains an OpenSpec-related directory but no valid recognized configuration, when scanned, then Vyasa distinguishes directory presence from valid OpenSpec configuration.

**Scenario 4: OpenSpec configuration**

Given a repository contains a recognized, valid OpenSpec configuration, when scanned, then Vyasa records the configuration status separately from the presence of specification or change files.

**Scenario 5: Agent instructions**

Given a repository contains recognized agent instruction files, when scanned, then Vyasa records their supported names and locations.

**Scenario 6: Test indicators**

Given a repository contains recognized test directories, test files, or test configuration, when scanned, then Vyasa records the detected indicators and the evidence supporting them.

**Scenario 7: README quality**

Given README quality assessment has not been implemented or assessed, when a project is queried, then Vyasa reports the status as not assessed rather than claiming a subjective quality rating.

**Scenario 8: Undefined convention**

Given a convention has not been defined well enough to detect reliably, when the scanner processes a project, then Vyasa does not claim that the convention is enabled or disabled.

## FR-006 — Evidence and Unknown Values

Vyasa MUST make the origin and certainty of extracted metadata understandable to users and calling agents.

### Scenarios

**Scenario 1: Evidence-backed fact**

Given a metadata field is derived from a repository file, when the fact is returned, then the response includes an evidence reference identifying the relevant source wherever practical.

**Scenario 2: Declared fact**

Given a field is explicitly declared in a recognized project profile, when returned, then Vyasa distinguishes the declared value from independently detected facts.

**Scenario 3: Unknown value**

Given a field cannot be established, when returned, then Vyasa uses a defined unknown or not-documented state instead of inventing a value.

**Scenario 4: Missing versus false**

Given a test configuration was not found, when Vyasa reports test status, then it distinguishes “not detected” from a confirmed assertion that the project has no tests.

**Scenario 5: Stale evidence**

Given a source file has changed since a previous scan, when its previously extracted facts are queried before a successful refresh, then Vyasa exposes their freshness limitations according to the documented freshness policy.

**Scenario 6: Evidence unavailable**

Given a previous evidence source is no longer accessible, when the corresponding metadata is queried, then Vyasa does not present stale evidence as if it were freshly verified.

## FR-007 — Local Project Index

Vyasa MUST maintain a local index that supports project discovery and retrieval without requiring external services.

### Scenarios

**Scenario 1: Persisted index**

Given a successful scan has populated the index, when Vyasa restarts, then previously indexed project records remain available subject to their freshness status.

**Scenario 2: New project**

Given a new eligible project is discovered, when the index is updated, then the project becomes searchable.

**Scenario 3: Changed project**

Given relevant project metadata changes, when a rescan completes, then the index reflects the newly detected information and its evidence.

**Scenario 4: Removed or inaccessible project**

Given a previously indexed project can no longer be found or accessed, when a scan runs, then Vyasa applies a documented stale, missing, or inaccessible state instead of silently erasing all evidence of the record.

**Scenario 5: Index migration**

Given the local schema version changes, when Vyasa opens an existing database, then it applies supported migrations or reports a controlled recovery error.

**Scenario 6: Offline operation**

Given external network access is unavailable, when Phase 1 operations run against local workspaces and the local index, then they continue without requiring an external service.

## FR-008 — Incremental Scanning and Refresh

Vyasa MUST support refreshing the local index while minimizing unnecessary work where practical.

### Scenarios

**Scenario 1: Initial scan**

Given a new index has no project records, when a scan is requested, then Vyasa discovers eligible projects and builds the index.

**Scenario 2: Unchanged project**

Given a project has not changed in ways relevant to supported detectors, when an incremental scan runs, then Vyasa may reuse valid prior results according to its invalidation rules.

**Scenario 3: Changed manifest**

Given a recognized manifest changes, when a scan runs, then affected metadata is recalculated.

**Scenario 4: Deleted metadata file**

Given a previously recognized file has been deleted, when a successful scan runs, then facts dependent on that file are updated or removed according to the field ownership and evidence rules.

**Scenario 5: Interrupted scan**

Given a scan is interrupted, when the index is accessed afterward, then previously committed valid records remain usable and incomplete updates are not falsely reported as a successful complete scan.

**Scenario 6: Concurrent refresh requests**

Given overlapping refresh requests are submitted, when the service processes them, then it follows a documented concurrency policy and avoids inconsistent index state.

**Scenario 7: Refresh result**

Given a scan finishes, when its outcome is reported, then the result identifies the relevant scope, counts, errors, and completion status.

## FR-009 — Project Search

Vyasa MUST support searching the indexed project portfolio using supported metadata fields.

### Scenarios

**Scenario 1: Name search**

Given the index contains projects, when a user searches by project name, then Vyasa returns matching projects according to documented matching rules.

**Scenario 2: Technology search**

Given multiple projects declare or detect a supported technology, when a user searches for that technology, then Vyasa returns the matching projects and indicates the evidence for the match.

**Scenario 3: Combined filters**

Given the search interface supports multiple filters, when a query combines technology and documentation criteria, then results satisfy all specified filter conditions according to the documented semantics.

**Scenario 4: Empty result**

Given no project matches the search, when the query is executed, then Vyasa returns an empty result set with an understandable response.

**Scenario 5: Match provenance**

Given a project matches because of a particular field, when the search result is returned, then the response identifies the matching metadata and its evidence where practical.

**Scenario 6: Stable ordering**

Given the same indexed data and query are used, when equivalent searches run, then results follow a documented, deterministic ordering policy.

## FR-010 — Project Details and Context

Vyasa MUST provide detailed metadata and a concise, structured context view for a selected project.

### Scenarios

**Scenario 1: Project details**

Given a valid project identifier is provided, when its details are requested, then Vyasa returns available metadata, local availability information, and freshness status.

**Scenario 2: Unknown project identifier**

Given an identifier does not resolve to a known project, when details are requested, then Vyasa returns a clear not-found result.

**Scenario 3: Context retrieval**

Given a project is indexed, when its context is requested, then Vyasa returns a structured summary of available identity, purpose, technologies, documentation, conventions, tests, and repository information.

**Scenario 4: Limited information**

Given only partial metadata is available, when context is requested, then Vyasa returns the known fields and explicitly marks missing fields rather than failing the entire request.

**Scenario 5: Agent consumption**

Given an MCP client requests project context, when the response is produced, then the structure is suitable for programmatic consumption and does not require parsing a free-form narrative to recover individual facts.

**Scenario 6: Local accessibility**

Given a project is registered but its repository is not available on the current device, when context is requested, then Vyasa distinguishes known shared metadata from locally accessible repository content.

## FR-011 — Related-Project Discovery

Vyasa MUST support deterministic discovery of potentially related projects.

### Scenarios

**Scenario 1: Shared technologies**

Given projects share one or more recognized technologies, when related-project discovery is requested, then Vyasa can identify them using the documented relation rules.

**Scenario 2: Shared explicit dependency**

Given a project declares a dependency on another identifiable project, when related projects are queried, then Vyasa can report that explicit relationship.

**Scenario 3: No relationship evidence**

Given no configured relation rule establishes a relationship, when related projects are queried, then Vyasa does not invent one.

**Scenario 4: Explainable result**

Given a related project is returned, when the result is examined, then it explains which supported criteria established the relationship.

**Scenario 5: Ranking**

Given multiple projects satisfy relation rules, when ranking is supported, then ordering is deterministic and based on documented criteria rather than an LLM-generated similarity judgment.

## FR-012 — Project Dependencies

Vyasa MUST expose dependency information only where it can be established from recognized evidence.

### Scenarios

**Scenario 1: Manifest dependency**

Given a supported manifest declares dependencies, when dependency information is requested, then Vyasa returns the recognized dependency names and available version constraints.

**Scenario 2: Unsupported format**

Given dependency information exists only in an unsupported format, when dependencies are requested, then Vyasa reports that the information is unavailable or partially supported.

**Scenario 3: Internal project dependency**

Given a recognized dependency can be mapped to another indexed project, when project dependencies are queried, then Vyasa reports the relationship and the supporting evidence.

**Scenario 4: External dependency**

Given a dependency does not map to an indexed project, when dependencies are queried, then Vyasa may report it as an external dependency without creating a fictional local project.

**Scenario 5: Incomplete dependency information**

Given dependency metadata is incomplete, when results are returned, then Vyasa identifies the available coverage and does not claim an exhaustive dependency graph.

## FR-013 — MCP Interface

Vyasa MUST expose its supported Phase 1 capabilities through a documented MCP interface.

### Required tools

- `search_projects`
- `get_project`
- `get_project_context`
- `find_related_projects`
- `get_project_dependencies`
- `get_index_status`

An optional refresh tool may be provided to update the generated local index.

### Scenarios

**Scenario 1: Tool discovery**

Given an MCP client connects successfully, when it lists the available tools, then it can discover the supported tool names, descriptions, and input schemas.

**Scenario 2: Valid request**

Given a tool receives valid input, when the request is processed, then the response conforms to its documented output contract.

**Scenario 3: Invalid input**

Given a tool receives invalid input, when the request is processed, then Vyasa returns a structured validation error.

**Scenario 4: Unknown project**

Given a project-specific tool receives an unknown project identifier, when the request is processed, then Vyasa reports a not-found outcome rather than returning another project's details.

**Scenario 5: Operational failure**

Given a storage or scanning error prevents a request from completing, when the error is returned, then the response communicates the failure without exposing secrets or sensitive local configuration.

**Scenario 6: Read-only behaviour**

Given an agent uses ordinary project query tools, when the tools execute, then they do not modify project source files or maintained project metadata.

**Scenario 7: Refresh isolation**

Given an authorized client invokes the optional refresh operation, when the index is refreshed, then only generated index and scan state are updated according to the defined policy.

## FR-014 — Project Profile Lifecycle

Vyasa MUST distinguish machine-generated draft information from project-maintained canonical information.

### Scenarios

**Scenario 1: No canonical profile**

Given a repository has no recognized canonical project profile, when scanned, then Vyasa extracts available metadata without pretending that a canonical profile exists.

**Scenario 2: Optional draft generation**

Given draft generation is enabled and a repository lacks a profile, when draft generation runs, then it creates a draft containing only supported extracted facts and clearly identifies missing information.

**Scenario 3: Ignored draft**

Given the agreed draft policy uses a git-ignored file, when a draft is generated, then the draft follows that policy and does not unintentionally become a committed project artifact.

**Scenario 4: Existing canonical profile**

Given a repository contains a recognized canonical profile, when Vyasa scans it, then it reads supported fields without overwriting the file.

**Scenario 5: Conflicting canonical and detected values**

Given canonical profile values differ from detected facts, when metadata is returned, then Vyasa preserves source provenance and follows documented field precedence rules.

**Scenario 6: Human edits**

Given a maintainer edits canonical project metadata, when the project is rescanned, then the maintained values are read according to the documented schema and no automatic replacement occurs.

**Note:** The canonical profile format, file paths, and precedence rules must be finalized before this requirement is implemented.

## FR-015 — Error Handling and Scan Reporting

Vyasa MUST report scan and indexing outcomes in a way that makes failures and partial results distinguishable from successful complete operations.

### Scenarios

**Scenario 1: Partial scan**

Given some repositories can be scanned while others fail, when the scan finishes, then Vyasa reports partial completion and identifies failed or skipped items.

**Scenario 2: File access failure**

Given a recognized file cannot be read, when the scanner processes it, then the failure is recorded without terminating unrelated project scans.

**Scenario 3: Unsupported file format**

Given a manifest or configuration format is unsupported, when the scanner encounters it, then Vyasa reports the limitation where relevant and does not fabricate extracted facts.

**Scenario 4: Scan history**

Given a scan completes or fails, when its outcome is recorded, then the index retains an appropriate run status, timestamp, scope, and summary.

**Scenario 5: Safe diagnostics**

Given an error contains sensitive local configuration or credential information, when the error is reported or logged, then sensitive values are redacted or excluded.

---

# 5. Phase 2 — Shared Project Registry

## FR-016 — Shared Registry Synchronization

Vyasa MUST synchronize an approved subset of project metadata with Google Sheets.

### Scenarios

**Scenario 1: New project synchronization**

Given a new eligible project is indexed locally, when synchronization runs, then Vyasa creates or updates its shared registry record using the stable project identity.

**Scenario 2: Existing project synchronization**

Given a project already exists in the registry, when its approved metadata changes, then Vyasa updates the fields it owns according to the synchronization policy.

**Scenario 3: Human-managed fields**

Given the registry contains human-managed values such as tracking level or notes, when synchronization runs, then those values are preserved unless an explicitly authorized operation changes them.

**Scenario 4: Export allowlist**

Given a local project record contains local paths or machine-specific data, when metadata is synchronized, then those fields are excluded from export.

**Scenario 5: Synchronization failure**

Given Google Sheets is unavailable or authentication fails, when synchronization is attempted, then Vyasa reports the failure and preserves the usable local index.

**Scenario 6: Conflicting values**

Given a shared field has changed locally and remotely, when synchronization detects the conflict, then it applies the documented ownership and conflict policy rather than silently overwriting an owned value.

**Scenario 7: Scan history**

Given synchronization runs, when the operation finishes, then the corresponding outcome is recorded with counts and relevant errors.

**Scenario 8: Registry schema**

Given the shared workbook is missing required tabs or columns, when synchronization starts, then Vyasa reports a schema validation error rather than writing values into unrelated columns.

## FR-017 — Cross-Device Project Visibility

Vyasa MUST allow a device to retrieve shared project metadata even when the corresponding repository is not cloned locally.

### Scenarios

**Scenario 1: Registry-only project**

Given a project exists in Google Sheets but is absent from the current device's workspace roots, when the registry is loaded, then Vyasa makes the project discoverable as a shared record.

**Scenario 2: Local and shared match**

Given a local project matches a shared registry record, when records are reconciled, then Vyasa associates them according to the documented identity rules.

**Scenario 3: No local repository**

Given a shared project has no local repository mapping, when its details are requested, then Vyasa reports that local source files are unavailable on the current device.

**Scenario 4: Local path isolation**

Given two devices use different local paths for the same project, when shared metadata is synchronized, then the shared record does not require either device's local path to identify the project.

**Scenario 5: Stale shared record**

Given a shared record has not been recently verified, when returned to a client, then its verification status and last-known scan information are represented accurately.

---

# 6. Phase 3 — Remote Repository Discovery

## FR-018 — Remote Repository Discovery

Vyasa MUST support discovering eligible repositories through configured GitHub and Bitbucket Cloud APIs.

### Scenarios

**Scenario 1: GitHub public repositories**

Given the configured GitHub discovery scope includes accessible public repositories, when discovery runs, then Vyasa retrieves the repositories permitted by that scope.

**Scenario 2: Authenticated repository access**

Given valid credentials and appropriate permissions are configured, when discovery runs, then Vyasa retrieves repositories accessible to the configured account or organization scope.

**Scenario 3: Bitbucket Cloud repositories**

Given valid Bitbucket Cloud credentials and repository permissions are configured, when discovery runs, then Vyasa retrieves accessible repositories within the configured scope.

**Scenario 4: Pagination**

Given a provider returns results across multiple pages, when discovery runs, then Vyasa processes all pages required by the configured scope, subject to provider limits and failures.

**Scenario 5: API rate limits**

Given a provider rate limit is reached, when discovery continues, then Vyasa follows the documented retry or stop policy and records the incomplete outcome.

**Scenario 6: Authentication failure**

Given credentials are missing, expired, or unauthorized, when discovery runs, then Vyasa reports an access failure rather than returning an empty successful result.

**Scenario 7: No cloning**

Given remote discovery is requested, when repositories are enumerated, then Vyasa does not clone or check out repositories solely to perform discovery.

## FR-019 — Remote Metadata Inspection

Vyasa MUST inspect supported remote repository metadata through provider APIs when access and provider capabilities permit.

### Scenarios

**Scenario 1: Repository metadata**

Given an accessible remote repository, when its metadata is retrieved, then Vyasa records supported repository identity and metadata fields.

**Scenario 2: README inspection**

Given the provider API exposes a recognized README, when remote inspection runs, then Vyasa extracts only supported metadata using the documented rules.

**Scenario 3: Manifest inspection**

Given a recognized manifest is available through the provider API, when remote inspection runs, then Vyasa extracts supported dependencies or technology indicators without requiring a checkout.

**Scenario 4: Unavailable file**

Given a file cannot be retrieved due to permissions, provider limitations, or absence, when inspection runs, then Vyasa distinguishes the known outcome from an unverified assumption wherever possible.

**Scenario 5: Remote evidence**

Given a fact is extracted remotely, when returned, then the evidence identifies the repository and the relevant path or provider reference where practical.

**Scenario 6: Consistent metadata model**

Given the same supported fact is extracted from a local repository and a remote provider, when results are reconciled, then both use the shared domain representation while retaining their source provenance.

## FR-020 — Duplicate and Obsolete Candidates

Vyasa MUST help users identify potentially duplicate or obsolete projects without automatically performing destructive actions.

### Scenarios

**Scenario 1: Potential duplicate**

Given two project records share identity or metadata indicators that satisfy documented duplicate rules, when the portfolio is reviewed, then Vyasa flags the candidates for human review.

**Scenario 2: Possible obsolete project**

Given a project has explicit lifecycle metadata or defined review indicators suggesting it may be obsolete, when the portfolio is reviewed, then Vyasa identifies it as a candidate for review.

**Scenario 3: Insufficient evidence**

Given a project has not been scanned recently or its repository is inaccessible, when the portfolio is reviewed, then Vyasa does not declare the project obsolete solely because its current state could not be verified.

**Scenario 4: Human decision**

Given a candidate has been flagged, when a user reviews it, then Vyasa does not automatically delete, archive, or modify the project.

**Scenario 5: Explainable flag**

Given a project is flagged for review, when the result is retrieved, then Vyasa exposes the deterministic criteria and evidence supporting the flag.

---

# 7. Shared Behaviour and Data Rules

The following rules apply across functional areas.

## 7.1 Source Provenance

Every supported extracted fact SHOULD retain sufficient source information to explain how it was established.

## 7.2 Field Ownership

Each mutable field MUST have an explicitly defined owner and precedence policy. Local scanning, project-maintained profiles, shared registry edits, and remote provider data MUST NOT silently overwrite one another.

## 7.3 Unknown and Missing Values

Unknown, not documented, not detected, inaccessible, stale, and explicitly false MUST remain distinguishable where the source evidence supports that distinction.

## 7.4 Deterministic Processing

Metadata extraction, matching, filtering, and ranking MUST follow documented deterministic rules. LLM inference is not required for routine project discovery.

## 7.5 Non-Destructive Operation

Ordinary project query tools MUST be read-only. Index refresh and synchronization may update their designated generated state but MUST NOT silently edit repository source files or canonical project documentation.

## 7.6 Local and Shared Data

Local filesystem paths, workspace roots, local database locations, credentials, and secrets MUST NOT be exported to Google Sheets.

## 7.7 Versioning

The metadata schema, MCP tool contracts, registry mappings, and supported detector rules SHOULD be versioned or otherwise traceable so behaviour changes can be tested and documented.

---

# 8. Deferred Functional Decisions

The following decisions must be resolved before their corresponding functionality is implemented.

| ID | Decision | Required before |
|---|---|---|
| DFR-001 | Confirm the meaning and detection rules for OKF. | P1 standards detection |
| DFR-002 | Define deterministic README quality criteria or leave quality unassessed. | P1 documentation detection |
| DFR-003 | Define project discovery boundaries and criteria for non-Git project directories. | P1 discovery |
| DFR-004 | Define canonical project profile format, draft location, and source precedence. | P1 profile lifecycle |
| DFR-005 | Define normalized remote identity rules, including forks and multiple repositories. | P1 identity |
| DFR-006 | Define supported manifest and technology detectors. | P1 metadata extraction |
| DFR-007 | Define related-project rules and deterministic ranking. | P1 related-project discovery |
| DFR-008 | Define exact dependency relationships to report and their supported sources. | P1 dependency queries |
| DFR-009 | Define Google Sheets field ownership and conflict resolution. | P2 synchronization |
| DFR-010 | Define the supported Google authentication and permission model. | P2 integration |
| DFR-011 | Define GitHub and Bitbucket Cloud discovery scopes. | P3 remote discovery |
| DFR-012 | Define remote matching rules and handling for inaccessible repositories. | P3 reconciliation |

Unresolved decisions MUST remain visible as open items rather than being silently interpreted as settled requirements.

---

# 9. Requirements Traceability

Each functional requirement should be traceable to:

1. Its originating product objective.
2. Its OpenSpec specification or change.
3. Its implementation module or interface.
4. Its acceptance tests.
5. Its completion status.

A requirement is not complete merely because code exists. Its defined behaviour must be verified by tests or an explicit acceptance check.

## 10. Completion Principle

Vyasa's functional contract is to discover supported project facts, preserve their provenance, make them searchable through MCP, and maintain a trustworthy distinction between known information and unknown information.

The implementation MUST favour verifiable facts, explicit ownership, predictable behaviour, and safe failure handling over speculative summaries or unverified assumptions.
