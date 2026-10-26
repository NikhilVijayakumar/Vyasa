---
type: Decision
title: "Partial Results Never Imply Absence"
description: A limit, timeout, failed page, or access error means not assessed; absence is concluded only from complete, successful inspection.
tags: [adr, completeness, partial-results, remote]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: err
    resource: /practices/error-handling.md
    title: Error Handling
  - id: rr
    resource: /architecture/remote-repositories/discovery-and-pagination.md
    title: Repository Discovery and Pagination
---

# Status

Proposed (draft). It becomes stable when reviewed and accepted.

# Context

Scans, listings, and syncs can stop early. Reading an incomplete result as a complete one deletes or denies things that still exist.

# Decision

Every inspection reports whether it was complete. Limits, timeouts, access failures, and failed or missing pages mark the affected scope incomplete and the affected indicators not assessed. A repository becomes `missing` only after two consecutive complete, successful listings omit it, and even then the record is kept. Authentication or rate-limit failures never count toward absence.

# Alternatives considered

- **Treat the latest result as truth.** Simple, but one blip deletes reality.

# Consequences

- Completeness has to be tracked and reported on every run.
- Some states stay uncertain longer.
- Records are not deleted automatically.

# Related

- [Error Handling](/practices/error-handling.md)
- [Remote Discovery Views](/architecture/views/remote-views.md)
