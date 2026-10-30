---
type: Concept
title: Workspace Names
description: Human-managed local names distinguish configured workspace roots without changing their identity.
tags: [workspace, naming, ownership, local]
status: draft
generated: { by: codex/gpt-6, at: 2026-10-30T00:00:00Z }
---

# Workspace Names

A workspace root is a machine-local configured boundary for discovery. A person may give that root a local display name. The name is human-managed metadata: scanning must not infer or overwrite it, and it does not change the root or project identity. Names may be duplicated, so the root remains available for disambiguation. Without a name, the root is the display fallback.

Names and root paths remain local to the installation. An explicit edit changes a name; queries only read it. Invalid or unreadable stored metadata must be reported rather than treated as a successful edit. Backups of local metadata should include workspace names alongside configuration and index data.
