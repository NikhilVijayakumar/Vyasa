---
type: Architecture
title: "Scanning and Evidence: Incremental, Full, and Partial Scans"
description: Invalidation rules for incremental scans and the semantics of full, partial, and interrupted scans.
tags: [scanning, detectors, evidence, provenance]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/scanning-and-evidence.md
    title: Scanning and Evidence
---

# Scanning and Evidence: Incremental, Full, and Partial Scans

*Sections 13–14 of [Scanning and Evidence](/architecture/scanning-and-evidence.md).*

## 13. Incremental Scanning

### 13.1 Objective

Incremental scanning should avoid reprocessing unchanged inputs when previous results remain valid.

Correctness takes precedence over skipping work.

### 13.2 Cache Inputs

A cached detector result may depend on:

- Relevant input file paths.
- File contents or fingerprints.
- Detector version.
- Detector configuration.
- Canonical profile schema version.
- Repository identity.
- Relevant source revision.
- Other explicit detector dependencies.

The cache key and invalidation rules must include all inputs that can change the result.

### 13.3 Invalidation Events

Existing observations must be reconsidered when:

- A relevant file is added.
- A relevant file is modified.
- A relevant file is deleted.
- A supported configuration changes.
- A detector version changes.
- A profile schema changes.
- A repository identity changes.
- A prior inspection was incomplete.
- The source becomes accessible after a previous failure.

### 13.4 File Fingerprints

File modification times and sizes may be used as optimization hints, but must not be treated as universal proof that content is unchanged.

Content fingerprints may provide stronger change detection.

The implementation should choose a practical strategy that balances scan cost and correctness. It must document any circumstances in which cached observations may remain stale.

### 13.5 Deletions

A file deletion can invalidate previous positive evidence.

After a complete successful inspection of the relevant scope, Vyasa should update the affected observation according to the detector's semantics.

If the scope was incomplete, Vyasa must not interpret the missing file as confirmed deletion.

### 13.6 Detector Version Changes

A detector version change may alter the interpretation of existing files.

When a detector changes in a way that affects its output, affected observations must be recalculated or explicitly marked as requiring revalidation.

The scanner must not claim that an old result was produced by a newer detector version.

---

## 14. Full Scans, Partial Scans, and Failures

### 14.1 Full Scan

A full scan evaluates the configured scope according to the supported discovery and detector rules.

The run is complete only if all required work for that scope has reached a terminal outcome.

### 14.2 Partial Scan

A partial scan may produce valid updates while some projects, files, or detectors fail.

It must record:

- The successful scope.
- The failed or skipped scope.
- The relevant error categories.
- Whether previous observations remain usable.
- Which observations need revalidation.

### 14.3 Interrupted Scan

An interrupted scan must not be reported as successfully complete.

Previously committed valid records may remain available, but unfinished updates must not be presented as completed observations.

### 14.4 Error Isolation

A malformed manifest should not stop README detection. An inaccessible project should not prevent other projects from being indexed.

Failures should be isolated to the smallest practical unit: detector, file, repository, or scan run.

### 14.5 Diagnostic Safety

Diagnostics must identify the failing stage and provide actionable context without exposing secrets or unnecessary absolute paths through shared interfaces.
