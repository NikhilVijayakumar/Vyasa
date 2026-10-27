---
type: Decision
title: "Language Observations Are Stored by the Scan and Filtered, Never Merged"
description: Languages are detected in the scan per checkout, stored as rows with the current and previous observation, filtered by label and status, and kept apart from declared technologies.
tags: [adr, index, languages, query]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-27T15:00:00Z }
---

# Status

Proposed (draft). It becomes stable when reviewed and accepted.

# Context

Language results are only useful to an agent if they are in the index and can narrow a search. Detection walks a checkout, so where it runs, how results are kept across rescans, and how partial or missing observations are shown decide whether the answers can be trusted.

# Decision

The scan detects languages once per checkout, after discovery and before storing, and stores one observation per checkout (run, time, completeness, data version) with one row per language and status; the current and previous observation are kept. The newest observation is current even when partial, and a partial one never reports a language as gone. A search matches a project when any present checkout has the requested language, optionally limited to one status; an unknown label is rejected with the allowed labels. Details give languages per checkout, never summed, and a checkout never observed reports `not_observed`. A failed detection is stored as a failed observation and the scan continues. Detected languages stay separate from the profile's declared technologies.

# Alternatives considered

- **Detect at query time.** Rejected: hidden filesystem work and unpredictable latency.
- **A separate detection step with its own run.** Rejected: the index can hold projects with no language data and needs its own freshness story.
- **One JSON blob per checkout.** Rejected: the filter would parse JSON instead of using an index.
- **Keep the last complete observation as current.** Rejected: it serves stale counts and hides that the tree changed.
- **Merge detected languages into declared technologies.** Rejected: it mixes observed evidence with free text the owner wrote.

# Consequences

- Every scan walks every checkout again until incremental rescan exists.
- The label vocabulary is the shipped table, so adding a language is a data change.
- A query never touches the filesystem and always shows when a result was observed.

# Related

- [Language Evidence Has Two Statuses and a Fixed Table](/decisions/language-evidence-statuses.md)
- [Retention Defaults](/decisions/retention-defaults.md)
- [Partial Results Never Imply Absence](/decisions/partial-results-never-imply-absence.md)
- [Observation Freshness Without Query-Time I/O](/decisions/observation-freshness-without-query-time-io.md)
