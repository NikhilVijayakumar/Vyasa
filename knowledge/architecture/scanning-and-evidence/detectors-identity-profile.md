---
type: Architecture
title: "Scanning and Evidence: Detectors, Identity, and Profile Detection"
description: The detector contract and registry, identity detection inputs, and the canonical profile and draft rules.
tags: [scanning, detectors, evidence, provenance]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/scanning-and-evidence.md
    title: Scanning and Evidence
---

# Scanning and Evidence: Detectors, Identity, and Profile Detection

*Sections 6–8 of [Scanning and Evidence](/architecture/scanning-and-evidence.md).*

## 6. Detector Architecture

Each detector must implement a defined contract.

A detector definition must specify:

1. Detector identifier and version.
2. Supported input files or metadata.
3. Output fields.
4. Validation rules.
5. Evidence generation rules.
6. Unsupported cases.
7. Failure behaviour.
8. Cache invalidation inputs.
9. Tests covering positive, negative, ambiguous, and malformed inputs.

Detectors should be independently testable.

One detector's failure must not invalidate observations from unrelated detectors.

### 6.1 Detector Output

A detector must produce structured observations rather than directly modifying the project profile or arbitrary database records.

Conceptually, a result contains:

- Entity reference.
- Field identifier.
- Value or explicit status.
- Source category.
- Evidence references.
- Detector identifier and version.
- Observation time.
- Relevant source revision, if available.
- Diagnostic information, if needed.

The application layer validates the result, applies ownership rules, and persists the observation.

### 6.2 Detector Registry

The implementation should use a registry of enabled detectors.

The registry must make it possible to determine:

- Which detectors are supported.
- Which detectors ran for a project.
- Which detectors were skipped.
- Which detectors failed.
- Which detector version produced an observation.

The initial implementation does not require a plugin marketplace or third-party executable detector system.

---

## 7. Project Identity Detection

### 7.1 Inputs

Identity resolution may use:

- Recognized canonical project profile.
- Local Git repository metadata.
- Normalized Git remote identity.
- Provider repository identifiers in later phases.
- Existing project and repository associations.
- Local fallback identity.

### 7.2 Rules

- Prefer reliable, stable repository identity when available.
- Do not use a display name alone as a stable identifier.
- Do not treat a directory rename as a new project when existing identity evidence resolves the same entity.
- Do not merge multiple repositories into one project without explicit or sufficiently strong defined evidence.
- Flag ambiguous identity matches.
- Preserve source identity information for later reconciliation.

### 7.3 Evidence

An identity decision should record the evidence that supports it, such as the normalized remote identity or provider identifier.

If a repository has no usable remote, Vyasa may assign a deterministic local fallback identity according to the approved identity policy.

The exact identity algorithm belongs in the data-model and identity design. It must not be invented independently by individual detectors.

---

## 8. Project Profile Detection

### 8.1 Canonical Profile

The canonical profile is a project-maintained source of declared metadata.

The proposed location is:

` .vyasa/project-profile.toml`

The leading space above is explanatory formatting only; the actual path begins with `.vyasa/`.

The exact profile format and schema must be finalized before the detector is implemented.

The profile detector must:

- Recognize only approved profile paths and formats.
- Validate values against the profile schema.
- Mark values as declared rather than independently detected.
- Record the source path and field reference.
- Report invalid fields or unsupported schema versions.
- Preserve conflicts between declarations and observations.

A malformed profile must not prevent the scanner from extracting unrelated metadata.

### 8.2 Missing Profile

If no canonical profile exists, Vyasa continues extracting available repository evidence.

It must not assume that a canonical profile exists merely because a draft file exists.

### 8.3 Generated Draft

An optional draft may be generated through a separate operation when explicitly enabled.

Proposed location:

`.vyasa/project-profile.draft.toml`

The draft should:

- Be git-ignored by default.
- Contain only supported values and clearly marked missing fields.
- Be distinct from the canonical profile.
- Never be automatically promoted to canonical status.
- Never be overwritten during ordinary scanning.
- Follow a defined policy for stale drafts and existing manual edits.

The routine scanner itself remains read-only.

### 8.4 Profile Precedence

The profile detector does not independently decide the final value for every field.

For each field, the ownership and resolution policy determines whether the canonical profile, an observed manifest, explicit documentation, or another source is authoritative.
