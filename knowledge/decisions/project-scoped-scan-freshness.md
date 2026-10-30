---
type: Decision
title: "Project-Scoped Scans Preserve Workspace Freshness"
description: Project-scoped scans record their scope and per-checkout outcomes without asserting workspace-wide absence or freshness.
tags: [adr, scanning, index, scope]
status: draft
generated: { by: codex/implementer, at: 2026-10-30T00:00:00Z }
---

# Status

Proposed; independent review is pending.

# Context

A person may refresh an indexed project's checkouts without observing the rest of its workspace. A subset observation cannot establish that other projects are missing or that an entire index is fresh. Clients need explicit results for incomplete observations.

# Decision

Record the scope of each scan and report individual checkout outcomes for a selected project. Only configured-root eligible indexed checkouts are inspected. Workspace-wide absence reconciliation and index-wide freshness use workspace-scoped observations, never a project-scoped observation. Existing historical runs are interpreted as workspace-scoped. The local desktop interface invokes the backend over its CLI and receives structured outcomes.

# Alternatives considered

- Reuse a whole-root scan: rejected because it observes more than the selected project and delays a targeted refresh.
- Treat a targeted result as a complete workspace observation: rejected because it falsely asserts absence and freshness for unobserved items.
- Keep targeted scope only in transient output: rejected because history and freshness cannot distinguish observation boundaries.

# Consequences

- Scope and outcomes require a compatible index migration and explicit client contract.
- A failed checkout remains visible without suppressing other valid checkout results.
- Path containment and identity must be verified before updating an observation.
- No move-evidence source exists yet: an absent recorded path is reported as missing, and `MOVED` stays reserved rather than guessed.

# Related

- [Scan Run and Item Results](/architecture/data-model/relationships-and-runs.md)
- [Partial Results Never Imply Absence](/decisions/partial-results-never-imply-absence.md)
- [Field Ownership](/concepts/field-ownership.md)
