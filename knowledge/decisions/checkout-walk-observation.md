---
type: Decision
title: "One Walk Per Checkout Feeds Counts and Languages on One Observation"
description: The scan walks each checkout once and stores file-type counts and language results on the same observation; the documentation-only indicator is derived when read.
tags: [adr, index, scanner, file-composition]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-27T18:00:00Z }
---

# Status

Proposed (draft). It becomes stable when reviewed and accepted.

# Context

The scan reports languages and file-type counts for a checkout. Each needs the same list of file names. Two walks would double the scan's input and output cost and could see different trees if files change during the scan, so a language total could disagree with the code count.

# Decision

The scan walks each checkout once and derives both results from that file list. They are stored on one observation of that walk, so they share its time, completeness, and failure status, and the same retention of the current and previous observation. The code, documentation, and other counts are stored; the documentation-only indicator is not, and is derived when read from the counts and the observation's completeness. An observation made before counts existed, or a failed one, reports its counts as not counted, never as zero. A project matches a documentation-only search when any active checkout has the requested indicator; a checkout whose indicator is unknown matches neither value.

# Alternatives considered

- **A second walk for counts.** Rejected: doubles scan cost and lets counts and languages disagree.
- **Separate tables with their own status and retention.** Rejected: duplicates completeness and failure columns and lets the two results drift apart in time.
- **Store the indicator.** Rejected: it could disagree with the counts it comes from.
- **Require every active checkout to agree.** Rejected: one partial checkout would hide the project from both values.
- **A project-level rollup.** Rejected: counts describe one checkout and are never summed.

# Consequences

- Counts and the language histogram agree by construction.
- Observations made before this decision report not counted until the next scan.
- The observation is no longer only about languages; its tables keep their names until a rename is worth a migration.

# Related

- [File Composition Data and Limits](/decisions/file-composition-data-and-limits.md)
- [Language Observations Are Stored by the Scan and Filtered, Never Merged](/decisions/language-observations-in-index.md)
- [Partial Results Never Imply Absence](/decisions/partial-results-never-imply-absence.md)
