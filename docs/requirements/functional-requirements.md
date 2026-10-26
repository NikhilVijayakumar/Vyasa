# Vyasa (व्यास) — Functional Requirements

**Document:** `docs/requirements/functional-requirements.md`  
**Status:** Draft v0.1  
**Product:** Vyasa — Workspace Intelligence MCP  
**Related Documents:** `knowledge/product/vision.md`, `knowledge/product/scope-and-roadmap.md`

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

| ID | Area | Phase | Package |
|---|---|---|---|
| FR-001 | Configuration and workspace roots | P1 | [workspace-discovery](workspace-discovery/requirement.md) |
| FR-002 | Project and repository discovery | P1 | [workspace-discovery](workspace-discovery/requirement.md) |
| FR-003 | Project identity | P1 | [project-identity](project-identity/requirement.md) |
| FR-004 | Deterministic metadata extraction | P1 | [metadata-and-evidence](metadata-and-evidence/requirement.md) |
| FR-005 | Documentation and standards detection | P1 | [metadata-and-evidence](metadata-and-evidence/requirement.md) |
| FR-006 | Evidence and unknown values | P1 | [metadata-and-evidence](metadata-and-evidence/requirement.md) |
| FR-007 | Local project index | P1 | [local-index](local-index/requirement.md) |
| FR-008 | Incremental scanning and refresh | P1 | [local-index](local-index/requirement.md) |
| FR-009 | Project search | P1 | [project-query](project-query/requirement.md) |
| FR-010 | Project details and context | P1 | [project-query](project-query/requirement.md) |
| FR-011 | Related-project discovery | P1 | [project-query](project-query/requirement.md) |
| FR-012 | Project dependencies | P1 | [project-query](project-query/requirement.md) |
| FR-013 | MCP interface | P1 | [mcp-server](mcp-server/requirement.md) |
| FR-014 | Project profile lifecycle | P1 | [project-profile](project-profile/requirement.md) |
| FR-015 | Error handling and scan reporting | P1 | [workspace-discovery](workspace-discovery/requirement.md) |
| FR-016 | Shared registry synchronization | P2 | [shared-registry](shared-registry/requirement.md) |
| FR-017 | Cross-device project visibility | P2 | [shared-registry](shared-registry/requirement.md) |
| FR-018 | Remote repository discovery | P3 | [remote-discovery](remote-discovery/requirement.md) |
| FR-019 | Remote metadata inspection | P3 | [remote-discovery](remote-discovery/requirement.md) |
| FR-020 | Duplicate and obsolete candidates | P1–P3 | [project-identity](project-identity/requirement.md) |

# 4. Where the requirements live

The requirement statements and their scenarios moved into **requirement packages**, one per logical part, so each
can be grilled, specified, and delivered on its own. This document keeps the area index, the shared rules that
apply to every area, the deferred decisions, and the traceability rules.

| Package | Owns | Phase |
|---|---|---|
| [workspace-discovery](workspace-discovery/requirement.md) | FR-001, FR-002, FR-015 | P1 |
| [project-identity](project-identity/requirement.md) | FR-003, FR-020 | P1 |
| [metadata-and-evidence](metadata-and-evidence/requirement.md) | FR-004, FR-005, FR-006 | P1 |
| [local-index](local-index/requirement.md) | FR-007, FR-008 | P1 |
| [project-query](project-query/requirement.md) | FR-009, FR-010, FR-011, FR-012 | P1 |
| [mcp-server](mcp-server/requirement.md) | FR-013 | P1 |
| [project-profile](project-profile/requirement.md) | FR-014 | P1 |
| [shared-registry](shared-registry/requirement.md) | FR-016, FR-017 | P2 |
| [remote-discovery](remote-discovery/requirement.md) | FR-018, FR-019 | P3 |

Each package holds `requirement.md` (the statements), `features/` (the scenarios as Gherkin, tagged `@FR-nnn` and
`@FR-nnn-Sn`), `grill-log.md`, and `diagrams.md`. Cross-cutting packages cover
[data-ownership](data-ownership/requirement.md), [security-and-privacy](security-and-privacy/requirement.md),
and [quality-attributes](quality-attributes/requirement.md).

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
| DFR-001 | ~~Confirm the meaning and detection rules for OKF.~~ Resolved 2026-10-26: OKF is Google Cloud's Open Knowledge Format (`knowledge/technologies/okf.md`); detection rules in `knowledge/architecture/scanning-and-evidence.md` §9.11. | P1 standards detection |
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

Each decision above has a recommended answer in the grill log of its owning package. All decisions that still need a choice are collected in [decisions-for-review.md](decisions-for-review.md).

---

# 9. Requirements Traceability

Each functional requirement should be traceable to:

1. Its originating product objective.
2. Its scenarios in the owning package's `features/` and its OpenSpec specification or change.
3. Its implementation module or interface.
4. Its acceptance tests.
5. Its completion status.

A requirement is not complete merely because code exists. Its defined behaviour must be verified by tests or an explicit acceptance check.

## 10. Completion Principle

Vyasa's functional contract is to discover supported project facts, preserve their provenance, make them searchable through MCP, and maintain a trustworthy distinction between known information and unknown information.

The implementation MUST favour verifiable facts, explicit ownership, predictable behaviour, and safe failure handling over speculative summaries or unverified assumptions.
