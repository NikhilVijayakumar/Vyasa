---
type: Concept
title: "Freshness and Staleness"
description: Observation status, index freshness, and evidence age are three different signals; none requires checking files at query time.
tags: [freshness, stale, index, status]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: mcp
    resource: /architecture/mcp-interface/response-conventions.md
    title: Shared Response Conventions
  - id: inc
    resource: /architecture/scanning-and-evidence/incremental-and-partial.md
    title: Incremental, Full, and Partial Scans
---

# Three signals

| Signal | Applies to | Values |
|---|---|---|
| Observation status | One value | `observed`, `declared`, `not_detected`, `unknown`, `unsupported`, `inaccessible`, `stale`, `conflicting` |
| Index freshness | The whole index | `current`, `stale`, `partial`, `unknown` |
| Evidence age | One observation | The time it was observed, and the revision when known |

They answer different questions: is this value established, how recently was the index refreshed, and when was this
particular fact seen.[^mcp]

# Index freshness

- `current`: the latest relevant run completed successfully within the freshness threshold.
- `stale`: the latest run is older than the threshold.
- `partial`: the latest relevant run was partial or interrupted.
- `unknown`: no run has completed, or freshness cannot be established.

The threshold is configurable. A query reports the state and never refreshes the index to improve it.

# When an observation becomes stale

At the next scan, when its fingerprint or detector version differs from the stored one, or when the source can no longer
be read. Between scans a query cannot know that a file changed, because checking would be hidden work; it reports the
observation's age and the index freshness instead.[^inc]

# Related

- [Evidence and Provenance](/concepts/evidence-and-provenance.md)
- [Scan Pipeline Views](/architecture/views/scan-pipeline-views.md)

[^mcp]: Shared Response Conventions
[^inc]: Incremental, Full, and Partial Scans
