---
type: Architecture
title: "Vyasa (व्यास) — Scanning and Evidence"
description: Deterministic workspace discovery, detectors, evidence model, and observation statuses.
tags: [scanning, detectors, evidence, provenance]
status: draft
generated: { by: human:nikhil-vijayakumar, at: 2026-10-26T00:00:00Z }
---
# Vyasa (व्यास) — Scanning and Evidence

Related architecture:

- [system-architecture](/architecture/system-architecture.md)
- [data-model](/architecture/data-model.md)

## Summary

This document defines how Vyasa discovers project information, extracts metadata, records evidence, evaluates freshness, and decides when existing observations must be updated.

## Parts

This concept is split into parts so each can be read on its own. Section numbers in the table are those of the original document, so references such as "§9.11" resolve to the part that contains them.

| Part | Sections | What it answers |
|---|---|---|
| [Principles and Scanning Pipeline](scanning-and-evidence/principles-and-pipeline.md) | §1–3 | Core scanning principles and the stages of the scanning architecture. |
| [Workspace Discovery and Repository Inspection](scanning-and-evidence/discovery-and-inspection.md) | §4–5 | Configured roots, candidates, nesting, exclusions, symlinks, outcomes, inventory, reading, limits, and Git metadata. |
| [Detectors, Identity, and Profile Detection](scanning-and-evidence/detectors-identity-profile.md) | §6–8 | The detector contract and registry, identity detection inputs, and the canonical profile and draft rules. |
| [Metadata Detector Inventory](scanning-and-evidence/detector-inventory.md) | §9 | Each supported detector: identity, Git, languages, technologies, README, documentation, OpenSpec, agent files, tests, dependencies, OKF, README quality, file composition. |
| [Evidence Model, Statuses, and Resolution](scanning-and-evidence/evidence-and-status.md) | §10–12 | Evidence requirements and granularity, observation statuses, and how values and ownership are resolved. |
| [Incremental, Full, and Partial Scans](scanning-and-evidence/incremental-and-partial.md) | §13–14 | Invalidation rules for incremental scans and the semantics of full, partial, and interrupted scans. |
| [Local and Remote Evidence, Sheets, and Performance](scanning-and-evidence/remote-sheets-and-performance.md) | §15–17 | How evidence differs locally and remotely, how it reaches the registry, and resource expectations. |
| [Detector Testing, Maintenance, and Acceptance](scanning-and-evidence/testing-and-acceptance.md) | §18–22 | Detector test strategy, inventory maintenance, acceptance criteria, and open decisions. |
