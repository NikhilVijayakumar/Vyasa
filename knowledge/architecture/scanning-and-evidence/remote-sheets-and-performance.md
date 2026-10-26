---
type: Architecture
title: "Scanning and Evidence: Local and Remote Evidence, Sheets, and Performance"
description: How evidence differs locally and remotely, how it reaches the registry, and resource expectations.
tags: [scanning, detectors, evidence, provenance]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/scanning-and-evidence.md
    title: Scanning and Evidence
---

# Scanning and Evidence: Local and Remote Evidence, Sheets, and Performance

*Sections 15–17 of [Scanning and Evidence](/architecture/scanning-and-evidence.md).*

## 15. Local and Remote Evidence

Phase 3 introduces remote file inspection. Remote observations must use the same conceptual evidence model as local observations while preserving their source distinctions.

### 15.1 Local Evidence

Local observations may include:

- Local checkout identity.
- Relative file paths.
- Local source state.
- Current local revision when available.
- Local scan time.

Local working-tree changes may differ from committed remote content.

### 15.2 Remote Evidence

Remote observations should include:

- Provider.
- Repository identity.
- Repository-relative file path.
- Remote revision or commit when available.
- Provider request outcome.
- Observation time.

### 15.3 Source Separation

Local and remote observations must not be silently merged into a fictional common revision.

For example, if a local README contains uncommitted changes and the remote default branch contains a different version, both observations remain distinct.

### 15.4 Provider Failure

A failed remote API request is not evidence that the repository or file is absent.

Vyasa must distinguish:

- Confirmed absence under a successfully inspected scope.
- Inaccessible content.
- Authentication failure.
- Rate limiting.
- Provider outage.
- Incomplete discovery.

### 15.5 No-Clone Rule

Remote inspection must use supported provider APIs rather than requiring a clone or checkout.

The same detector logic may be reused when a provider returns the relevant file content in a form the detector supports.

---

## 16. Google Sheets and Evidence

Google Sheets is a shared metadata registry, not the authoritative source of local file evidence.

### 16.1 Export

The registry may contain approved summaries of detection results, such as:

- README present.
- OpenSpec configuration valid.
- Recognized agent instructions detected.
- Test indicators detected.
- Last successful scan timestamp.

Only approved fields may be exported.

Local paths, machine-specific state, and secrets must remain local.

### 16.2 Import

Imported shared metadata must retain its shared-registry provenance.

A shared spreadsheet value must not be treated as direct evidence that a local file currently exists.

### 16.3 Freshness

The registry should distinguish a synchronized summary from a freshly verified local observation.

The last successful local scan and the last successful synchronization are different facts and must not be represented by one ambiguous timestamp.

---

## 17. Performance and Resource Constraints

The scanner must be designed for a large collection of independent projects.

Requirements:

- Avoid reading unrelated source files.
- Avoid rescanning every repository for every query.
- Respect configured traversal boundaries.
- Use incremental detection where safe.
- Limit parsing resources.
- Record skipped work and reasons.
- Support cancellation or interruption without corrupting committed state.
- Avoid unbounded memory growth from repository inventories or provider responses.

Numerical performance targets will be established through representative benchmarks and the non-functional requirements.

A performance optimization must not convert an incomplete scan into a falsely complete result.
