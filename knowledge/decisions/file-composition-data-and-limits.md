---
type: Decision
title: "File Composition Data and Limits"
description: File types are versioned data shared with the language detector, and counting has its own entry cap because it reads no content.
tags: [adr, scanning, detectors, limits]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-27T12:00:00Z }
sources:
  - id: inv
    resource: /architecture/scanning-and-evidence/detector-inventory.md
    title: Metadata Detector Inventory
  - id: lim
    resource: /decisions/scan-limits-and-symlink-defaults.md
    title: Scan Limits and Symlink Defaults
---

# Status

Proposed (draft). It becomes stable when reviewed and accepted.

# Context

The file composition detector counts files by extension. The accepted scan limits cap a project's inventory at 5,000 entries to bound reading and parsing. Counting reads no content, and most real repositories hold more than 5,000 files outside excluded directories, so the same cap would leave most counts partial. Code extensions are also what the language detector needs, so two lists could drift apart.

# Decision

File types are one versioned data file with a version number, a list of code extensions, and a list of documentation extensions; an extension in both lists is invalid. The language detector reads the same code list. Counting has its own entry cap of 50,000 entries (files and directories visited) with the depth and time limits unchanged at 6 levels and 60 seconds. Reaching any bound makes the count partial and names the bound. The numbers are starting points to validate against representative workspaces.

# Alternatives considered

- **Reuse the 5,000-entry inventory cap.** Simple, but most counts would be partial and the derived indicator mostly unknown.
- **No cap for counting.** Counting reads nothing, but a huge tree can still exhaust the time limit and memory for the walk.
- **Separate lists for the language and file composition detectors.** Independent, but the two would disagree at the edges.

# Consequences

- A repository over 50,000 entries, or deeper than 6 levels, reports partial counts and an unknown indicator.
- Changing the file type data changes its version, which marks existing observations stale.
- The limits must be validated against representative workspaces and may change.

# Related

- [Metadata Detector Inventory](/architecture/scanning-and-evidence/detector-inventory.md)
- [Scan Limits and Symlink Defaults](/decisions/scan-limits-and-symlink-defaults.md)
- [Partial Results Never Imply Absence](/decisions/partial-results-never-imply-absence.md)
- [Technology Registry as Versioned Data](/decisions/technology-registry-as-data.md)
