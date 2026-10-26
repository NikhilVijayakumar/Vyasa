# Synchronization — parts

Parts of [Synchronization](/architecture/synchronization.md).

* [Principles and Architecture](principles-and-architecture.md) - Why and how the registry is synchronized, its design principles, and its components.
* [Registry Structure, Ownership, and Identity](registry-and-ownership.md) - The three registry tabs, which side owns each field, and how projects are matched across devices.
* [Synchronization Modes and Workflow](modes-and-workflow.md) - Export, import, and bidirectional modes and the step-by-step synchronization workflow.
* [Conflicts, Upserts, and Idempotency](conflicts-and-idempotency.md) - Detecting and resolving conflicts, and making repeated runs converge.
* [Change Detection and Deletion](change-detection-and-deletion.md) - Detecting what changed since the last sync, and why records are retired rather than deleted.
* [Authentication, API Limits, and Cross-Device Behaviour](auth-limits-and-devices.md) - Google authentication options, quotas and retries, and behaviour across devices.
* [Results, MCP Interaction, and Observability](results-and-mcp.md) - Run result reporting, how sync relates to MCP, and diagnostics.
* [Testing, Sequence, and Acceptance](testing-and-acceptance.md) - Test strategy, implementation order, open decisions, and acceptance criteria.
