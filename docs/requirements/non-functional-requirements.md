# Vyasa (व्यास) — Non-Functional Requirements

**Document:** `docs/requirements/non-functional-requirements.md`  
**Product:** Vyasa — Workspace Intelligence MCP  
**Status:** Draft v0.1  
**Related Documents:**
- `knowledge/product/vision.md`
- `knowledge/product/scope-and-roadmap.md`
- `docs/requirements/functional-requirements.md`

---

## 1. Purpose

This document defines the non-functional requirements (NFRs) for Vyasa.

While functional requirements describe what Vyasa must do, non-functional requirements define how reliably, securely, efficiently, and consistently those capabilities must operate.

The requirements apply to:

- Phase 1 — Local Workspace Intelligence.
- Phase 2 — Shared Project Registry using Google Sheets.
- Phase 3 — Remote Repository Discovery using GitHub and Bitbucket APIs.

The objective is to ensure that Vyasa remains deterministic, lightweight, maintainable, secure, portable, and dependable as its capabilities expand.

## 2. Requirement Conventions

### 2.1 Priority

| Priority | Meaning |
|---|---|
| Critical | Mandatory for a safe, correct, or usable release. |
| High | Required for phase completion unless formally deferred. |
| Medium | Recommended quality improvement. |
| Low | Optional enhancement. |

### 2.2 Requirement Keywords

- **MUST:** Mandatory.
- **MUST NOT:** Prohibited.
- **SHOULD:** Expected unless a documented exception is approved.
- **MAY:** Optional.

### 2.3 Verification Methods

- **Automated Test:** Unit, integration, or end-to-end test.
- **Benchmark:** Measured performance under controlled conditions.
- **Inspection:** Architecture, configuration, or code review.
- **Operational Test:** Verification under realistic runtime conditions.
- **Security Test:** Verification of access restrictions, data protection, or misuse handling.

### 2.4 Performance Target Status

Performance targets marked **Proposed** are initial engineering objectives, not approved service-level commitments.

They must be validated against representative workspaces before becoming release acceptance thresholds.

Correctness and safety take precedence over performance optimization.

---

# 3. Determinism and Data Integrity

## NFR-001 — Deterministic Metadata Extraction

**Priority:** Critical  
**Phase:** P1–P3  
**Verification:** Automated Test

Vyasa MUST extract metadata using explicitly defined rules and recognized evidence sources.

For identical input files, detector configuration, and detector version, the system MUST produce equivalent extracted facts.

Metadata extraction MUST NOT depend on LLM-generated interpretations.

### Acceptance Criteria

1. Repeated extraction against unchanged fixtures produces equivalent metadata.
2. Detector behaviour is covered by reproducible tests.
3. Unsupported or ambiguous values are not presented as confirmed facts.
4. Source ordering and filesystem traversal ordering do not produce arbitrary metadata differences.

## NFR-002 — Evidence Traceability

**Priority:** Critical  
**Phase:** P1–P3  
**Verification:** Automated Test, Inspection

Vyasa MUST preserve the provenance of supported extracted facts.

Evidence SHOULD include:

- Source type.
- Source identifier or file path.
- Relevant field or detection rule.
- Observation timestamp.
- Detector version where applicable.

Evidence must distinguish local observations, project-declared information, shared registry data, and remote provider data.

### Acceptance Criteria

1. Supported extracted facts can be traced to their recognized sources.
2. Conflicting evidence remains distinguishable.
3. Evidence references do not expose unauthorized information through shared interfaces.
4. Missing evidence is explicitly represented rather than fabricated.

## NFR-003 — Data Integrity

**Priority:** Critical  
**Phase:** P1–P3  
**Verification:** Automated Test

Index updates and synchronization operations MUST preserve valid records when an operation fails or is interrupted.

### Acceptance Criteria

1. Interrupted writes do not leave partially committed project records in an inconsistent state.
2. Failed scans do not silently erase previously valid metadata.
3. Failed synchronization does not corrupt the local index.
4. Database integrity is checked through appropriate automated tests.
5. Schema migrations have a documented failure and recovery policy.

## NFR-004 — Stable Identity

**Priority:** Critical  
**Phase:** P1–P3  
**Verification:** Automated Test

Project identity MUST be independent of display name and local directory path wherever reliable identity evidence is available.

Identity resolution MUST follow documented rules.

### Acceptance Criteria

1. Renaming a repository directory does not create an unnecessary duplicate when reliable identity evidence remains unchanged.
2. Multiple local checkouts of the same remote repository are recognized according to the identity policy.
3. Ambiguous identities are flagged rather than silently merged.
4. Cross-device identity reconciliation uses stable identifiers rather than machine-specific paths.

## NFR-005 — Honest Representation of Uncertainty

**Priority:** Critical  
**Phase:** P1–P3  
**Verification:** Automated Test

Vyasa MUST distinguish between information that is confirmed, declared, unknown, not detected, inaccessible, or stale where supported by evidence.

### Acceptance Criteria

1. Missing metadata is not replaced with guessed values.
2. An unavailable source is not treated as proof that information is absent.
3. File presence is not treated as proof of documentation quality or configuration validity.
4. MCP responses communicate incomplete or stale information accurately.

---

# 4. Performance and Resource Efficiency

## NFR-006 — Project Search Latency

**Priority:** High  
**Phase:** P1–P3  
**Verification:** Benchmark

Search against the local SQLite index SHOULD remain responsive without requiring a fresh repository scan for every query.

### Proposed Targets

| Operation | Proposed target |
|---|---|
| Project lookup by ID | p95 ≤ 100 ms |
| Metadata search | p95 ≤ 300 ms |
| Project context retrieval | p95 ≤ 300 ms |
| Related-project lookup | p95 ≤ 500 ms |

These targets apply to local processing under a defined benchmark dataset, excluding MCP client transport and external API latency.

**Target status:** Proposed — requires benchmark validation.

### Acceptance Criteria

1. Search queries use indexed data rather than rescanning every repository.
2. Performance is measured using a documented benchmark dataset.
3. Results remain correct under increasing project counts.
4. Performance regressions can be detected through repeatable benchmarks.

## NFR-007 — Scanning Performance

**Priority:** High  
**Phase:** P1  
**Verification:** Benchmark

Scanning SHOULD avoid unnecessary filesystem traversal and repeated processing of unchanged files.

### Requirements

1. Configured exclusions MUST be respected.
2. Incremental scanning SHOULD reuse valid previous results when its invalidation rules permit.
3. The scanner SHOULD avoid reading entire large files when only specific metadata is required.
4. Directory traversal MUST have documented boundaries and safeguards.
5. Scanning SHOULD provide progress or completion summaries.

No universal scan-duration limit is imposed until representative workspace benchmarks are available.

## NFR-008 — Memory Efficiency

**Priority:** High  
**Phase:** P1–P3  
**Verification:** Benchmark, Inspection

Vyasa SHOULD maintain bounded memory usage during discovery and metadata extraction.

### Requirements

1. Large repository inventories SHOULD be processed incrementally where practical.
2. The scanner SHOULD avoid loading unnecessary source files into memory.
3. External API pagination SHOULD be processed without retaining unlimited response histories.
4. Memory consumption SHOULD be benchmarked using representative project collections.

**Proposed baseline:** Evaluate a 500-project workspace on a development machine with 8 GB RAM or more.

This is a benchmark planning assumption, not a confirmed minimum hardware requirement.

## NFR-009 — Startup Efficiency

**Priority:** Medium  
**Phase:** P1–P3  
**Verification:** Benchmark

The MCP service SHOULD start without performing an unnecessary full workspace scan.

### Acceptance Criteria

1. An existing valid local index can be opened independently of a full rescan.
2. Startup does not require Google Sheets or remote repository availability.
3. Startup errors are reported clearly.
4. Full or incremental scanning follows the configured refresh policy.

## NFR-010 — Scalability

**Priority:** High  
**Phase:** P1–P3  
**Verification:** Benchmark, Automated Test

Vyasa MUST support growth in the number of indexed projects without requiring a redesign of its core domain model.

### Proposed Evaluation Sizes

| Dataset | Purpose |
|---|---|
| 10 projects | Basic correctness |
| 100 projects | Typical multi-project development |
| 500 projects | Initial scalability benchmark |
| 1,000 projects | Extended scalability evaluation |

These are evaluation sizes rather than guaranteed capacity limits.

### Acceptance Criteria

1. Query correctness is preserved at each tested size.
2. Project identity remains stable.
3. Incremental scanning does not require rebuilding unrelated project records unnecessarily.
4. Performance results are recorded and reviewed before defining supported capacity limits.

---

# 5. Reliability and Availability

## NFR-011 — Offline Availability

**Priority:** Critical  
**Phase:** P1–P3  
**Verification:** Operational Test

Core local indexing and MCP retrieval MUST remain usable without internet connectivity.

### Acceptance Criteria

1. Phase 1 scanning and querying work offline.
2. Loss of Google Sheets connectivity does not prevent access to valid local records.
3. Loss of GitHub or Bitbucket connectivity does not prevent local queries.
4. External integration failures are clearly distinguished from local index failures.

## NFR-012 — Fault Isolation

**Priority:** Critical  
**Phase:** P1–P3  
**Verification:** Automated Test

A failure affecting one repository, detector, or external provider MUST NOT unnecessarily terminate unrelated operations.

### Acceptance Criteria

1. A malformed repository does not stop scanning other repositories.
2. An unreadable manifest does not invalidate unrelated metadata.
3. One failed remote repository request does not automatically invalidate other successfully retrieved records.
4. Partial completion is explicitly reported.

## NFR-013 — Recoverability

**Priority:** High  
**Phase:** P1–P3  
**Verification:** Automated Test, Operational Test

Vyasa MUST support recovery from interrupted scans, failed database updates, and external synchronization errors.

### Acceptance Criteria

1. Previously committed valid records remain usable after interrupted operations.
2. Database migration failures produce actionable diagnostics.
3. Failed synchronization can be retried without unintentionally duplicating records.
4. Recovery procedures are documented for database corruption and incompatible schema versions.

## NFR-014 — Idempotency

**Priority:** Critical  
**Phase:** P1–P3  
**Verification:** Automated Test

Repeating an operation with unchanged inputs MUST NOT produce unintended duplicate records or destructive side effects.

### Acceptance Criteria

1. Repeated scans do not duplicate logical projects.
2. Repeated synchronization does not duplicate shared registry rows.
3. Repeated remote discovery does not create unnecessary duplicate repository records.
4. Index refresh does not overwrite maintained project documentation.

## NFR-015 — Concurrent Operation Safety

**Priority:** High  
**Phase:** P1–P3  
**Verification:** Automated Test

Vyasa MUST handle overlapping index reads and writes according to a documented concurrency policy.

### Acceptance Criteria

1. Concurrent reads do not observe partially committed updates.
2. Overlapping refresh operations cannot corrupt the index.
3. Lock contention and busy database conditions have defined handling.
4. Synchronization and scanning do not silently overwrite one another's owned fields.

---

# 6. Security and Privacy

## NFR-016 — Read-Only Repository Access

**Priority:** Critical  
**Phase:** P1–P3  
**Verification:** Security Test

Routine repository discovery, metadata extraction, and MCP queries MUST NOT modify repository source files or maintained documentation.

### Acceptance Criteria

1. Scanner operations do not modify tracked repository content.
2. MCP query tools have no repository-write side effects.
3. Optional draft generation, if implemented, requires explicit authorization and follows its defined lifecycle.
4. Generated indexes and operational state remain separate from maintained project knowledge.

## NFR-017 — Credential Protection

**Priority:** Critical  
**Phase:** P2–P3  
**Verification:** Security Test, Inspection

Credentials and authentication tokens MUST be protected from unauthorized exposure.

### Requirements

1. Credentials MUST NOT be stored in Google Sheets.
2. Credentials MUST NOT be committed to source control.
3. Credentials MUST NOT appear in ordinary MCP responses.
4. Credentials MUST NOT be written to application logs.
5. Remote provider access SHOULD use the minimum permissions required.
6. Credentials SHOULD be stored through an appropriate local secret-management mechanism.

## NFR-018 — Shared Data Minimization

**Priority:** Critical  
**Phase:** P2–P3  
**Verification:** Automated Test, Security Test

Only approved project metadata may be exported to shared systems.

### Prohibited Shared Fields

- Local repository paths.
- Workspace root paths.
- Local SQLite database paths.
- Machine-specific identifiers.
- Credentials and tokens.
- Environment secrets.
- Internal operational details not explicitly approved for sharing.

### Acceptance Criteria

1. Synchronization uses an explicit export allowlist.
2. Newly added local fields are not automatically exported.
3. Export tests verify prohibited fields remain excluded.
4. Diagnostic information is sanitized before shared logging or reporting.

## NFR-019 — Filesystem Access Boundaries

**Priority:** Critical  
**Phase:** P1  
**Verification:** Security Test

Vyasa MUST respect configured workspace boundaries and exclusion policies.

### Acceptance Criteria

1. Scanning is limited to explicitly configured roots and permitted paths.
2. Symlink handling follows a documented policy.
3. Directory traversal cannot escape authorized roots through unintended path resolution.
4. Unsupported file types and malformed content are handled safely.
5. Filesystem permission failures do not trigger unauthorized access attempts.

## NFR-020 — Untrusted Repository Content

**Priority:** Critical  
**Phase:** P1–P3  
**Verification:** Security Test

Repository files, manifests, README content, and remote provider responses MUST be treated as untrusted input.

### Requirements

1. Scanning MUST NOT execute repository scripts to discover metadata.
2. Manifest parsing MUST NOT invoke arbitrary code from the repository.
3. Repository-provided text MUST NOT be treated as instructions controlling Vyasa's security behaviour.
4. Parsers SHOULD enforce reasonable file-size and resource limits.
5. External URLs and identifiers MUST be validated before use in sensitive operations.

## NFR-021 — MCP Access Security

**Priority:** High  
**Phase:** P1–P3  
**Verification:** Security Test

The MCP interface MUST respect the configured trust boundary.

### Acceptance Criteria

1. The default local transport and exposure policy are documented.
2. MCP responses do not unnecessarily expose secrets.
3. Any network-exposed transport requires explicit configuration and appropriate access controls.
4. Tool permissions are limited to their documented capabilities.
5. Error responses do not expose sensitive configuration values.

## NFR-022 — Remote Provider Security

**Priority:** Critical  
**Phase:** P3  
**Verification:** Security Test

Remote repository integrations MUST operate within the configured authorization scope.

### Acceptance Criteria

1. GitHub and Bitbucket adapters do not request unnecessary write permissions.
2. Discovery does not push commits, modify branches, or alter remote repository settings.
3. Authentication failures are reported without exposing credentials.
4. Remote access is limited to configured providers and permitted repository scopes.

---

# 7. Maintainability and Architecture

## NFR-023 — Modular Architecture

**Priority:** High  
**Phase:** P1–P3  
**Verification:** Inspection, Automated Test

Vyasa MUST separate core domain logic from infrastructure and provider-specific integrations.

### Expected Boundaries

- Domain models and rules.
- Project discovery.
- Metadata detectors.
- Project identity resolution.
- Evidence and provenance.
- Local persistence.
- MCP transport and tools.
- Google Sheets synchronization.
- Remote repository providers.

### Acceptance Criteria

1. Domain logic can be tested without SQLite, MCP, or external APIs.
2. Metadata detectors can be tested independently.
3. Provider-specific structures do not become mandatory core domain types.
4. New adapters can be introduced without changing unrelated business rules.

## NFR-024 — Extensibility

**Priority:** High  
**Phase:** P1–P3  
**Verification:** Inspection, Automated Test

Vyasa SHOULD allow new metadata detectors, repository providers, and storage adapters to be introduced through defined interfaces.

### Acceptance Criteria

1. A new manifest detector can be added without rewriting workspace discovery.
2. A new repository provider can reuse the shared project model.
3. New metadata fields have defined ownership, evidence, and serialization rules.
4. Unsupported detectors do not cause unrelated detectors to fail.

## NFR-025 — Testability

**Priority:** Critical  
**Phase:** P1–P3  
**Verification:** Automated Test, Inspection

Core behaviour MUST be verifiable without requiring production repositories, live Google Sheets access, or live Git hosting credentials.

### Acceptance Criteria

1. Scanner tests use controlled filesystem fixtures.
2. Domain logic is independently testable.
3. SQLite integration tests use isolated databases.
4. MCP tools have contract tests.
5. Google Sheets and repository provider adapters support test doubles or recorded fixtures.
6. Failure conditions are reproducible in automated tests.

## NFR-026 — Code Quality

**Priority:** High  
**Phase:** P1–P3  
**Verification:** Automated Test, Inspection

The implementation MUST follow consistent code-quality standards.

### Requirements

1. Public interfaces SHOULD have explicit type annotations.
2. Core models SHOULD use validated data structures.
3. Formatting and linting SHOULD be automated.
4. Static type checking SHOULD cover the core domain and public interfaces.
5. Error handling SHOULD use defined exception or result categories.
6. Business logic SHOULD remain separate from command-line and transport concerns.

Specific tooling and coverage thresholds must be selected in the development standards rather than assumed in this document.

## NFR-027 — Dependency Management

**Priority:** High  
**Phase:** P1–P3  
**Verification:** Inspection, Automated Test

Vyasa SHOULD minimize unnecessary runtime dependencies and make dependency versions reproducible.

### Acceptance Criteria

1. Runtime and development dependencies are explicitly declared.
2. Dependency installation is reproducible using the project's selected packaging workflow.
3. External integrations do not become mandatory dependencies for local-only use unless justified.
4. Dependency updates are tested for compatibility.

## NFR-028 — Backward Compatibility

**Priority:** High  
**Phase:** P1–P3  
**Verification:** Automated Test

Changes to persisted schemas and public MCP contracts MUST follow a documented compatibility policy.

### Acceptance Criteria

1. Supported database migrations preserve existing project records.
2. Breaking MCP contract changes are identified and documented.
3. Shared registry schema changes have an explicit migration strategy.
4. Detector changes that affect previously extracted metadata are traceable.

---

# 8. Portability and Configuration

## NFR-029 — Cross-Platform Portability

**Priority:** High  
**Phase:** P1–P3  
**Verification:** Automated Test, Operational Test

Vyasa SHOULD support common development environments without depending on a specific filesystem layout.

### Target Platforms

- Linux.
- Windows.
- macOS.

### Acceptance Criteria

1. Filesystem operations use portable path handling.
2. Platform-specific Git and path behaviour is handled explicitly.
3. Configuration does not require hardcoded user directories.
4. Platform-specific limitations are documented.
5. Supported-platform verification is included in the release process.

## NFR-030 — Configuration Management

**Priority:** High  
**Phase:** P1–P3  
**Verification:** Automated Test

Vyasa MUST provide a validated configuration mechanism for workspace roots, exclusions, index location, and enabled integrations.

### Acceptance Criteria

1. Configuration values are validated before use.
2. Invalid values produce understandable errors.
3. Safe defaults are documented.
4. Optional external integrations can be disabled.
5. Secrets are separated from ordinary shareable configuration.

## NFR-031 — Installation and Setup

**Priority:** High  
**Phase:** P1–P3  
**Verification:** Operational Test

A developer SHOULD be able to install and configure Vyasa using documented procedures.

### Acceptance Criteria

1. Installation prerequisites are documented.
2. A new local index can be initialized without external accounts.
3. MCP client configuration examples are provided.
4. Phase-specific integrations have separate setup instructions.
5. Setup failures produce actionable diagnostics.

---

# 9. Observability and Diagnostics

## NFR-032 — Structured Logging

**Priority:** High  
**Phase:** P1–P3  
**Verification:** Automated Test, Inspection

Vyasa SHOULD produce structured operational logs that support troubleshooting without exposing sensitive data.

### Expected Log Context

- Operation type.
- Scan or synchronization run identifier.
- Relevant project or repository identifier.
- Outcome status.
- Duration.
- Error category.

### Acceptance Criteria

1. Logs distinguish successful, partial, and failed operations.
2. Sensitive values are redacted or excluded.
3. Log verbosity is configurable.
4. Operational logs do not corrupt MCP protocol communication.

## NFR-033 — Scan and Synchronization Reporting

**Priority:** High  
**Phase:** P1–P3  
**Verification:** Automated Test

Every scan and synchronization operation MUST produce a meaningful outcome summary.

### Acceptance Criteria

1. Operations report completion status.
2. Scan results include discovered, updated, skipped, and failed counts where applicable.
3. Synchronization results distinguish successful updates from conflicts and failures.
4. Remote discovery reports incomplete pagination or rate-limited results.
5. Reports distinguish verified absence from access failures.

## NFR-034 — Freshness Visibility

**Priority:** Critical  
**Phase:** P1–P3  
**Verification:** Automated Test

Vyasa MUST expose sufficient freshness information for clients to understand whether returned metadata may be outdated.

### Acceptance Criteria

1. Indexed project records retain relevant scan timestamps.
2. Failed refresh attempts do not incorrectly update successful verification timestamps.
3. Remote-provider failures do not mark cached records as freshly verified.
4. MCP clients can distinguish current, stale, and unavailable information according to documented rules.

---

# 10. External Integration Quality

## NFR-035 — Google Sheets Synchronization Reliability

**Priority:** High  
**Phase:** P2  
**Verification:** Automated Test, Integration Test

Google Sheets synchronization MUST handle network failures, API errors, and conflicting changes without compromising local data integrity.

### Acceptance Criteria

1. Synchronization operations are retry-safe.
2. Repeated upserts do not create unintended duplicate rows.
3. Human-managed fields are preserved.
4. Partial failures are observable.
5. Registry schema mismatches are detected before unsafe writes.
6. Local queries remain available during Sheets outages.

## NFR-036 — Remote API Resilience

**Priority:** High  
**Phase:** P3  
**Verification:** Automated Test, Integration Test

GitHub and Bitbucket adapters MUST handle provider errors predictably.

### Acceptance Criteria

1. Pagination is supported.
2. Rate limits are handled according to provider guidance.
3. Retry behaviour is bounded.
4. Authentication failures are distinguished from missing repositories.
5. Provider outages do not invalidate unrelated local records.
6. Discovery does not require repository cloning.

## NFR-037 — Integration Isolation

**Priority:** High  
**Phase:** P2–P3  
**Verification:** Automated Test, Inspection

Failures or configuration changes in one integration MUST NOT unnecessarily affect unrelated integrations.

### Acceptance Criteria

1. Google Sheets can be disabled without disabling local discovery.
2. GitHub discovery can be disabled independently of Bitbucket discovery.
3. Provider credentials and configuration are isolated.
4. Core project queries do not require live provider calls unless explicitly requested.

---

# 11. Usability and Developer Experience

## NFR-038 — Predictable MCP Responses

**Priority:** High  
**Phase:** P1–P3  
**Verification:** MCP Contract Test

MCP tools MUST return consistently structured responses suitable for AI coding agents and programmatic clients.

### Acceptance Criteria

1. Response schemas are documented.
2. Field meanings and nullability are consistent.
3. Errors are distinguishable from empty successful results.
4. Results include appropriate identity and freshness information.
5. Clients do not need to parse prose to recover structured metadata.

## NFR-039 — Actionable Errors

**Priority:** High  
**Phase:** P1–P3  
**Verification:** Automated Test

Errors SHOULD explain what failed and what corrective action may be required without revealing sensitive information.

### Acceptance Criteria

1. Configuration errors identify invalid settings.
2. Missing workspace roots are distinguishable from permission failures.
3. Authentication errors are distinguishable from provider outages.
4. Database incompatibility errors identify the migration or recovery issue.
5. Unsupported metadata formats are reported without speculative interpretations.

## NFR-040 — Documentation Quality

**Priority:** High  
**Phase:** P1–P3  
**Verification:** Inspection

Delivered capabilities MUST be supported by appropriate developer and operational documentation.

### Acceptance Criteria

1. Public MCP tools have documented contracts.
2. Configuration options have descriptions and examples.
3. Supported metadata detectors and limitations are documented.
4. Phase-specific integrations have setup instructions.
5. Breaking changes and migrations are documented.

---

# 12. Testing and Release Quality

## NFR-041 — Automated Regression Testing

**Priority:** Critical  
**Phase:** P1–P3  
**Verification:** Automated Test

Changes to supported functionality MUST be validated through an automated regression suite.

### Required Test Categories

- Domain model tests.
- Project identity tests.
- Scanner and detector fixture tests.
- Evidence and provenance tests.
- SQLite persistence and migration tests.
- MCP contract tests.
- Error and recovery tests.
- Synchronization tests in Phase 2.
- Remote provider tests in Phase 3.

### Acceptance Criteria

1. Critical domain and identity behaviour has automated tests.
2. Previously fixed defects have regression coverage where practical.
3. Test execution does not require production credentials.
4. A release candidate passes the agreed automated test suite.

## NFR-042 — Reproducible Test Environments

**Priority:** High  
**Phase:** P1–P3  
**Verification:** Automated Test

Tests MUST use controlled inputs and avoid unnecessary dependence on machine-specific paths or external services.

### Acceptance Criteria

1. Filesystem tests use temporary directories or fixtures.
2. Database tests use isolated instances.
3. Network integration tests use controlled mocks or dedicated test environments.
4. Tests can run repeatedly without leaving unintended repository modifications.

## NFR-043 — Release Readiness

**Priority:** High  
**Phase:** P1–P3  
**Verification:** Inspection, Automated Test

A phase is ready for release only when its required functional and non-functional acceptance criteria are satisfied or explicitly deferred.

### Acceptance Criteria

1. Critical requirements pass verification.
2. Known limitations are documented.
3. Schema and contract changes are reviewed.
4. Security and privacy checks are completed.
5. Installation and configuration instructions are verified.
6. Any deferred High-priority requirement has a documented rationale and owner approval.

---

# 13. Non-Functional Requirements Matrix

| Category | Requirement IDs | Primary concern |
|---|---|---|
| Determinism and integrity | NFR-001–005 | Trustworthy metadata |
| Performance | NFR-006–010 | Responsive, efficient operation |
| Reliability | NFR-011–015 | Safe operation and recovery |
| Security and privacy | NFR-016–022 | Repository and data protection |
| Architecture | NFR-023–028 | Maintainability and extensibility |
| Portability | NFR-029–031 | Multi-platform operation |
| Observability | NFR-032–034 | Explainable operational state |
| External integrations | NFR-035–037 | Resilient synchronization and discovery |
| Developer experience | NFR-038–040 | Predictable interfaces and diagnostics |
| Release quality | NFR-041–043 | Testable and controlled delivery |

---

## 13.1 Owning packages

Each requirement is owned by exactly one requirement package, which carries its grill log, scenarios, and diagrams.

| Requirements | Owning package |
|---|---|
| NFR-001, 002, 005 | [metadata-and-evidence](metadata-and-evidence/requirement.md) |
| NFR-003 | [local-index](local-index/requirement.md) |
| NFR-004 | [project-identity](project-identity/requirement.md) |
| NFR-006–015, 023–034, 040–043 | [quality-attributes](quality-attributes/requirement.md) |
| NFR-016, 017, 019, 020 | [security-and-privacy](security-and-privacy/requirement.md) |
| NFR-018, 035 | [shared-registry](shared-registry/requirement.md) |
| NFR-021, 038, 039 | [mcp-server](mcp-server/requirement.md) |
| NFR-022, 036, 037 | [remote-discovery](remote-discovery/requirement.md) |

Recommended answers to the open decisions below are in the owning packages' grill logs and are collected in
[decisions-for-review.md](decisions-for-review.md).

---

# 14. Open Decisions

The following decisions require validation or explicit approval.

| ID | Decision | Recommendation | Target phase |
|---|---|---|---|
| NFD-001 | Supported Python version | Python 3.12+ initially | P1 |
| NFD-002 | Minimum supported hardware | Benchmark before defining | P1 |
| NFD-003 | Search latency thresholds | Validate proposed p95 targets | P1 |
| NFD-004 | Supported project capacity | Benchmark at 100, 500, and 1,000 projects | P1 |
| NFD-005 | SQLite concurrency mode | Evaluate WAL and controlled single-writer design | P1 |
| NFD-006 | Symlink traversal policy | Default to not following directory symlinks | P1 |
| NFD-007 | MCP transport | Prefer local stdio initially | P1 |
| NFD-008 | Static analysis tooling | Select formatter, linter, and type checker | P1 |
| NFD-009 | Minimum test coverage | Define meaningful coverage and critical-path requirements | P1 |
| NFD-010 | Registry conflict policy | Define explicit field ownership and conflict handling | P2 |
| NFD-011 | Credentials storage | Prefer OS credential store or appropriately protected local secrets | P2–P3 |
| NFD-012 | Remote API retry policy | Use bounded, provider-aware retries | P3 |

These recommendations are not finalized architecture decisions until reviewed and accepted.

---

# 15. Phase Acceptance Gates

## Phase 1 — Local Workspace Intelligence

Phase 1 MUST demonstrate:

- Deterministic, evidence-backed metadata extraction.
- Safe and consistent project identity resolution.
- Reliable SQLite persistence.
- Offline MCP querying.
- Read-only repository access.
- Recovery from partial or interrupted scans.
- Structured and predictable MCP responses.
- Automated verification of critical requirements.
- Documented configuration and setup.

Performance targets must be measured and reviewed, but unapproved proposed targets do not independently block release.

## Phase 2 — Shared Project Registry

Phase 2 MUST additionally demonstrate:

- Safe Google Sheets synchronization.
- Explicit field export allowlisting.
- Protection of human-managed fields.
- Cross-device identity consistency.
- Offline resilience.
- Conflict detection and recovery.
- No leakage of local paths or credentials.

## Phase 3 — Remote Repository Discovery

Phase 3 MUST additionally demonstrate:

- Secure GitHub and Bitbucket API access.
- Reliable pagination and rate-limit handling.
- Remote metadata extraction without cloning.
- Consistent local and remote identity reconciliation.
- Provider failure isolation.
- Non-destructive remote operations.

---

# 16. Governing Quality Principle

Vyasa is intended to be a dependable source of discoverable project metadata, not an autonomous interpretation engine.

Its quality depends on four fundamental guarantees:

1. **Correctness:** Facts are derived from recognized evidence.
2. **Integrity:** Data remains consistent through scans, failures, and synchronization.
3. **Safety:** Project-owned information and private local data remain protected.
4. **Predictability:** Developers and AI coding agents receive consistent, explainable results.

When these qualities conflict with convenience or additional functionality, correctness, integrity, and safety take precedence.

**A smaller, trustworthy index is preferable to a larger index containing unsupported or misleading claims.**
