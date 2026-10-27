---
type: Decision
title: "Language Evidence Has Two Statuses and a Fixed Table"
description: Languages are reported as files detected by extension or declared by a manifest, kept separate, from a fixed versioned table that never reads content.
tags: [adr, scanner, languages, evidence]
status: stable
generated: { by: claude-code/sonnet-5.5, at: 2026-10-27T12:00:00Z }
---

# Status

Accepted. Implemented and verified.

# Context

The language detector sees two kinds of evidence of different strength: a file with a recognized extension, and a manifest that declares a language. Merging them would claim more than either proves, and reading content to resolve shared extensions would break the scanner's no-content rule.

# Decision

A language result carries a status: `files_detected` (extension count) or `declared` (recognized manifest file present). Both are kept as separate evidence rows. Extensions map through one versioned table, one label each; manifests count by presence only and are not parsed. Unknown extensions and manifests are ignored.

# Alternatives considered

- **One merged "uses language" status.** Rejected: hides how strong the evidence is.
- **Resolve shared extensions by reading content.** Rejected: breaks the no-content rule and determinism.
- **Parse manifests for declared languages.** Rejected: that is the framework detector's job and adds a parser per format.

# Consequences

- The histogram sums to the code count of the shared walk.
- A shared extension such as `.h` gets a coarse label.
- Adding a language is a data change, not a code change.

# Related

- [File Composition Data and Limits](/decisions/file-composition-data-and-limits.md)
- [Partial Results Never Imply Absence](/decisions/partial-results-never-imply-absence.md)
