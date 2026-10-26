---
type: Decision
title: "Technology Registry as Versioned Data"
description: A versioned data file maps dependency names to technology keys, display names, and categories.
tags: [adr, technologies, detectors, search]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: det
    resource: /architecture/scanning-and-evidence/detector-inventory.md
    title: Metadata Detector Inventory
  - id: dm
    resource: /architecture/data-model/fields-profile-uniqueness.md
    title: Field Definitions, Profile, and Uniqueness
---

# Status

Proposed (draft). It becomes stable when reviewed and accepted.

# Context

Search and relation rules need one vocabulary for technologies, while manifests spell the same thing many ways. Hard-coding names in detectors scatters the vocabulary.

# Decision

Keep a versioned registry file mapping (ecosystem, dependency name) to a technology key, display name, and category, plus a list of ubiquitous technologies that never relate projects on their own. An unknown dependency remains a dependency and creates no technology. Changing the registry bumps its version and invalidates affected results.

# Alternatives considered

- **Names inside each detector.** No single vocabulary.
- **Infer technology from names.** Non-deterministic.

# Consequences

- Someone maintains the registry.
- Search results depend on its version, which is reported.

# Related

- [Deterministic Extraction](/concepts/deterministic-extraction.md)
