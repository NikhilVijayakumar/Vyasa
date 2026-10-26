---
type: Architecture
title: "Vyasa (व्यास) — Data Model"
description: Entities, identifiers, observations, evidence, and relationships stored in the Vyasa index.
tags: [data-model, index, evidence]
status: draft
generated: { by: human:nikhil-vijayakumar, at: 2026-10-26T00:00:00Z }
---
# Vyasa (व्यास) — Data Model

Related architecture:

- [system-architecture](/architecture/system-architecture.md)

## Summary

This document defines the conceptual and logical data model for Vyasa.

## Parts

This concept is split into parts so each can be read on its own. Section numbers in the table are those of the original document, so references such as "§9.11" resolve to the part that contains them.

| Part | Sections | What it answers |
|---|---|---|
| [Principles and Entity Overview](data-model/principles-and-entities.md) | §1–4 | Design principles, the entity list, and the relationship diagram. |
| [Project and Repository](data-model/project-and-repository.md) | §5–6 | The logical project and the repository entities with their fields, statuses, and associations. |
| [Local Checkout and External Identity](data-model/checkout-and-identity.md) | §7–8 | Where a repository lives on a device, and how identities from other systems attach. |
| [Metadata Observations and Evidence](data-model/observations-and-evidence.md) | §9–10 | How values, statuses, sources, current-value resolution, retention, and evidence references are modelled. |
| [Relationships, Scan Runs, and Item Results](data-model/relationships-and-runs.md) | §11–12 | Project relationships, scan run fields and status rules, and per-item outcomes. |
| [Shared Registry and Remote Observations](data-model/shared-and-remote.md) | §13–15 | Phase 2 and 3 entities: registry records, synchronization runs, and remote repository observations. |
| [Field Definitions, Profile, and Uniqueness](data-model/fields-profile-uniqueness.md) | §16–18 | Value vocabularies, canonical and draft profiles, and identity and uniqueness rules. |
| [Data Boundaries, Mapping, and Schema Evolution](data-model/boundaries-and-evolution.md) | §19–22 | Local versus shared data, SQLite mapping guidance, serialization, and schema change. |
| [Open Decisions and Acceptance](data-model/decisions-and-acceptance.md) | §23–25 | Decisions the model still needs, acceptance criteria, and the governing principle. |
