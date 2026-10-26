---
type: Architecture
title: "Data Model: Open Decisions and Acceptance"
description: Decisions the model still needs, acceptance criteria, and the governing principle.
tags: [data-model, index, evidence]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/data-model.md
    title: Data Model
---

# Data Model: Open Decisions and Acceptance

*Sections 23–25 of [Data Model](/architecture/data-model.md).*

## 23. Open Decisions

The following decisions must be finalized before the affected implementation begins.

| ID | Decision | Target |
|---|---|---|
| DM-001 | Project ID generation and normalization rules | Phase 1 |
| DM-002 | Repository identity rules for forks, mirrors, and renamed remotes | Phase 1 |
| DM-003 | Canonical project profile format and location | Phase 1 |
| DM-004 | Exact metadata field registry and initial detector inventory | Phase 1 |
| DM-005 | Retention policy for metadata observations and scan history | Phase 1 |
| DM-006 | Physical SQLite schema, indexes, and migration strategy | Phase 1 |
| DM-007 | Approved lifecycle status vocabulary and ownership | Phase 1 |
| DM-008 | ~~Definition of OKF and its metadata representation~~ Resolved: Google Cloud OKF; one observation per declared bundle (root path, declared version, concept count, non-conforming count), per scanning §9.11 | Phase 1 |
| DM-009 | Deterministic README quality criteria, or not-assessed-only policy | Phase 1 |
| DM-010 | Google Sheets field mapping and export allowlist | Phase 2 |
| DM-011 | Portfolio-field ownership and synchronization conflict rules | Phase 2 |
| DM-012 | Provider-specific identity and remote revision requirements | Phase 3 |

Unresolved decisions must remain explicit. They must not be silently encoded into the database or MCP contract.

---

## 24. Data Model Acceptance Criteria

The model is ready for Phase 1 implementation when:

1. Projects, repositories, and local checkouts are distinct entities.
2. Stable identity rules are documented.
3. Project metadata is separated from source observations.
4. Detected and declared facts remain distinguishable.
5. Evidence references identify the source of supported facts.
6. Unknown, not detected, inaccessible, stale, and conflicting values are represented distinctly.
7. Ownership and precedence are defined for every implemented metadata field.
8. Local paths and machine-specific data are isolated from shareable metadata.
9. Project relationships include provenance and deterministic derivation rules.
10. Scan history can represent partial failures and interrupted operations.
11. The model can support shared registry records without making Google Sheets the core authority.
12. Remote repository metadata can be incorporated without provider-specific types becoming mandatory core concepts.
13. Schema changes can be versioned and migrated safely.
14. Automated tests can validate identity, ownership, provenance, and serialization rules.

## 25. Governing Principle

Vyasa must model not only **what it knows**, but also **where that knowledge came from, who owns it, when it was observed, and how confidently it can be used**.

Projects are logical identities. Repositories are source-control units. Checkouts are local instances. Observations record evidence. Ownership rules determine authoritative values.

**The data model must preserve these distinctions even as Vyasa grows from a local index into a shared and remote-aware project intelligence system.**

---

## Proposed resolutions

These are drafts, not approvals.

| Decision | Proposed in |
|---|---|
| DM-001 project ID generation, DM-002 repository identity | [Stored Identity With Aliases](/decisions/stored-identity-with-aliases.md), [Remote Identity Normalization](/decisions/remote-identity-normalization.md) |
| DM-003 canonical profile | [Canonical Profile and Draft Handling](/decisions/canonical-profile-and-draft.md) |
| DM-004 field registry and detector inventory | [Technology Registry as Versioned Data](/decisions/technology-registry-as-data.md) |
| DM-010, DM-011 registry mapping and conflict rules | [Ownership-Based Conflict Resolution](/decisions/ownership-based-conflict-resolution.md) |
| DM-005, LS-005, LS-014 retention | [Retention Defaults](/decisions/retention-defaults.md) |
| Run status vocabulary | [Unified Run Status Vocabulary](/decisions/unified-run-status-vocabulary.md) |
