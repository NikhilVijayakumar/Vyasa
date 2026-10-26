---
type: Architecture
title: "Scanning and Evidence: Detector Testing, Maintenance, and Acceptance"
description: Detector test strategy, inventory maintenance, acceptance criteria, and open decisions.
tags: [scanning, detectors, evidence, provenance]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/scanning-and-evidence.md
    title: Scanning and Evidence
---

# Scanning and Evidence: Detector Testing, Maintenance, and Acceptance

*Sections 18–22 of [Scanning and Evidence](/architecture/scanning-and-evidence.md).*

## 18. Detector Test Strategy

Every detector must have deterministic fixture-based tests.

### 18.1 Required Test Categories

**Positive cases**

A supported input contains the expected evidence.

**Negative cases**

A complete supported inspection does not find the indicator.

**Malformed cases**

A recognized file cannot be parsed or validated.

**Unsupported cases**

The file or schema is outside the detector's declared coverage.

**Ambiguous cases**

Multiple sources disagree or evidence is insufficient to resolve a value.

**Access failure cases**

The file cannot be read.

**Incremental cases**

A source is added, modified, removed, or restored after a previous scan.

**Version cases**

Detector behaviour changes between versions and cached observations are invalidated appropriately.

### 18.2 Cross-Detector Tests

Tests should verify that:

- One detector failure does not invalidate unrelated results.
- Multiple detectors can use the same file without corrupting each other's outputs.
- Evidence references identify the correct source.
- Field ownership and precedence are applied after extraction.
- Equivalent inputs produce equivalent results.
- Unsupported formats do not produce fabricated metadata.

### 18.3 Representative Repository Fixtures

The fixture collection should include:

- A basic Git repository.
- A project without Git.
- A repository with multiple supported manifests.
- A repository with incomplete documentation.
- A repository with invalid configuration.
- A repository containing nested repositories or submodules.
- A repository with inaccessible or malformed files where testable.
- A repository with a canonical profile.
- A repository with only a generated draft.
- A repository with conflicting metadata observations.

Fixtures should be synthetic or sanitized and must not require access to production credentials.

---

## 19. Detector Inventory Maintenance

The supported detector inventory must be documented and version-controlled.

For each detector, record:

- Identifier.
- Supported file patterns.
- Supported schema versions.
- Extracted fields.
- Evidence format.
- Known limitations.
- Invalid and unsupported input behaviour.
- Cache invalidation dependencies.
- Test fixture locations.

Adding a new detector must not silently change the meaning of existing fields.

If detector behaviour changes, the implementation must determine whether existing observations need to be reprocessed.

---

## 20. Acceptance Criteria

The scanning and evidence architecture is ready for Phase 1 implementation when:

1. Workspace traversal respects configured roots and exclusions.
2. Project discovery criteria are documented.
3. Repository inspection is read-only.
4. Detector inputs and outputs are explicit.
5. Metadata is extracted only from supported evidence sources.
6. Observations distinguish detected facts from declared values.
7. Evidence references identify the source of supported facts.
8. Unknown, not detected, unsupported, inaccessible, stale, and conflicting states are distinguishable.
9. OpenSpec detection distinguishes directory presence, configuration validity, and meaningful artifact presence.
10. README quality is not assessed subjectively.
11. OKF detection recognizes only bundles declared through `okf_version`, and reports version support and conformance separately.
12. Incremental scanning has documented invalidation rules.
13. Failed or interrupted scans do not falsely claim complete verification.
14. One detector's failure does not unnecessarily invalidate other observations.
15. Remote observations can be represented without conflating local and remote revisions.
16. Shared registry data cannot masquerade as current local evidence.
17. Automated tests cover positive, negative, malformed, ambiguous, and failure cases.
18. Detector versions and known limitations are traceable.

---

## 21. Decisions Required Before Implementation

| ID | Decision | Required before |
|---|---|---|
| SE-001 | Exact workspace discovery rules and treatment of non-Git directories | Discovery implementation |
| SE-002 | Symlink and nested repository policy | Filesystem scanner |
| SE-003 | Initial manifest and language detector inventory | Metadata extraction |
| SE-004 | Canonical profile path and schema | Profile detector |
| SE-005 | Generated draft lifecycle and git-ignore policy | Optional draft generation |
| SE-006 | Supported OpenSpec format and validity rules | OpenSpec detector |
| SE-007 | ~~Meaning and representation of OKF~~ Resolved: Google Cloud OKF; rules in §9.11 | OKF detection |
| SE-008 | README quality checklist or not-assessed-only policy | Quality assessment |
| SE-009 | Evidence retention and fingerprint strategy | SQLite indexing |
| SE-010 | Incremental invalidation rules and detector versioning | Incremental scanner |
| SE-011 | Initial resource limits and benchmark dataset | Performance validation |
| SE-012 | Remote revision and evidence requirements | Phase 3 |

These decisions must remain explicit until resolved. They must not be silently inferred by the implementation agent.

## 22. Governing Principle

Vyasa's scanner must be able to explain every supported claim through recognizable evidence and documented rules.

It must preserve the difference between a fact, a declaration, a missing indicator, an inaccessible source, an unsupported format, and an unresolved conflict.

**The scanner must never claim to know more than it has actually verified.**

---

## Proposed resolutions

These are drafts, not approvals.

| Decision | Proposed in |
|---|---|
| SE-001, SE-002, SE-011 discovery, symlinks, limits | [Scan Limits and Symlink Defaults](/decisions/scan-limits-and-symlink-defaults.md) |
| SE-003 detector inventory | [Technology Registry as Versioned Data](/decisions/technology-registry-as-data.md) |
| SE-004, SE-005 profile and drafts | [Canonical Profile and Draft Handling](/decisions/canonical-profile-and-draft.md) |
| Read-only inspection and Git use | [Read-Only Repository Access and Git Policy](/decisions/read-only-access-and-git-policy.md) |
| Deterministic extraction | [Deterministic Extraction Without a Language Model](/decisions/deterministic-extraction-without-llm.md) |
