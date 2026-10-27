# Knowledge Update Log

## 2026-10-27
* **Update**: [Canonical Profile and Draft Handling](/decisions/canonical-profile-and-draft.md) now uses TOML (`.vyasa/project-profile.toml`) and says an agent or maintainer writes the profile once while Vyasa only reads it.
* **Update**: [Stored Identity With Aliases](/decisions/stored-identity-with-aliases.md) no longer uses a root-commit identity: a repository with no usable remote is a local project matched by path.
* **Creation**: Added the draft decision [Review Decisions Stay Local](/decisions/review-decisions-stay-local.md).
* **Update**: [Stored Identity With Aliases](/decisions/stored-identity-with-aliases.md) now covers the ambiguous status and the review flags for conflicts and duplicate checkouts.
* **Update**: [Stored Identity With Aliases](/decisions/stored-identity-with-aliases.md) now states how checkouts, project state, conflicts, and the no-remote fallback work.
* **Update**: [Index Lifecycle States and Single Writer](/decisions/index-lifecycle-and-single-writer.md) now says absence is only inferred when the whole tree was seen (no depth, link, or Git-link skips).
* **Creation**: Added the draft decision [Index Lifecycle States and Single Writer](/decisions/index-lifecycle-and-single-writer.md).
* **Creation**: Added the draft decision [Git Remote Provider Labels](/decisions/git-remote-provider-labels.md); the Git Detector (§9.2) now states how the provider is derived.
* **Creation**: Added the draft decision [Repository-Provided Ignore File](/decisions/repository-ignore-file.md).
* **Creation**: Added the draft decision [Repository Recognition and Discovery Run Status](/decisions/repository-recognition-and-run-status.md).
* **Creation**: Added the draft decision [Configuration File Format and Location](/decisions/configuration-file-format-and-location.md).
* **Creation**: Added the draft decision [File Composition Data and Limits](/decisions/file-composition-data-and-limits.md); the File Composition Detector (§9.13) now cites its entry cap.
* **Creation**: Added the File Composition Detector (§9.13) to the [Metadata Detector Inventory](/architecture/scanning-and-evidence/detector-inventory.md).
* **Creation**: Added the [Writing Knowledge](/practices/writing-knowledge.md) practice and the draft decision [Knowledge Profile Enforces Sections and Supersession](/decisions/knowledge-profile-section-rules.md).

## 2026-10-26
* **Creation**: Added [Views](/architecture/views/) (deployment, scan pipeline, data model, MCP, storage, synchronization, remote discovery, security) with C4, sequence, state, and decision diagrams.
* **Creation**: Added the [Glossary](/concepts/glossary.md) and five principle concepts: [Deterministic Extraction](/concepts/deterministic-extraction.md), [Freshness and Staleness](/concepts/freshness-and-staleness.md), [Untrusted Content](/concepts/untrusted-content.md), [Explicit Operations](/concepts/explicit-operations.md), [Local-First Operation](/concepts/local-first.md).
* **Creation**: Added six [technology](/technologies/) notes, five [practices](/practices/), four [runbooks](/runbooks/), and eighteen draft [decisions](/decisions/).
* **Fix**: One run-status vocabulary across the [Data Model](/architecture/data-model.md), [Local Storage](/architecture/local-storage.md), and [Synchronization](/architecture/synchronization.md); the refresh tool default in [MCP Interface](/architecture/mcp-interface.md) now reads disabled unless enabled.
* **Split**: Nine large concepts became overviews with parts ([System Architecture](/architecture/system-architecture.md), [Data Model](/architecture/data-model.md), [Scanning and Evidence](/architecture/scanning-and-evidence.md), [MCP Interface](/architecture/mcp-interface.md), [Local Storage](/architecture/local-storage.md), [Synchronization](/architecture/synchronization.md), [Remote Repositories](/architecture/remote-repositories.md), [Security and Privacy](/architecture/security-and-privacy.md), [Scope and Roadmap](/product/scope-and-roadmap.md)); no content removed. The profile now caps a concept at 400 lines.
* **Creation**: Added [C4 System Views](/architecture/c4-system-views.md), [Project Identity](/concepts/project-identity.md), and [Field Ownership](/concepts/field-ownership.md).
* **Split**: Phase acceptance criteria moved out of [Scope and Roadmap](/product/scope-and-roadmap.md) into the requirements.
* **Migration**: Moved product vision and roadmap from `docs/` into [Product](/product/).
* **Split**: [Security and Privacy](/architecture/security-and-privacy.md) now holds only the security model; normative controls moved out of the bundle.
* **Creation**: Added [Open Knowledge Format (OKF)](/technologies/okf.md); OKF detection rules defined in [Scanning and Evidence](/architecture/scanning-and-evidence.md) §9.11.
* **Initialization**: Created the bundle, its profile, and section indexes.
* **Migration**: Moved the architecture documents from `docs/architecture/` into [Architecture](/architecture/) as draft concepts.
* **Creation**: Added [Evidence and Provenance](/concepts/evidence-and-provenance.md) and [Vertical Slices](/practices/vertical-slices.md).
