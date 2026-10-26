# Remote Repository Discovery — parts

Parts of [Remote Repository Discovery](/architecture/remote-repositories.md).

* [Purpose, Goals, Position, and Providers](purpose-and-position.md) - Why remote discovery exists, its goals and non-goals, where it sits in the architecture, and provider support.
* [Configuration, Scope, and Authentication](config-and-auth.md) - How scopes are configured and how provider credentials are handled.
* [Repository Discovery and Pagination](discovery-and-pagination.md) - How repositories are enumerated and how pages and partial coverage are tracked.
* [Remote File Inspection and Detectors](inspection-and-detectors.md) - Which files are read through APIs and how the deterministic detectors apply to them.
* [Remote Identity and Reconciliation With Local Data](identity-and-reconciliation.md) - Matching remote repositories to projects, and reconciling remote with local observations.
* [Sheets Integration and SQLite Persistence](sheets-and-persistence.md) - What remote data may reach the registry and how it is stored locally.
* [Incremental Discovery, Limits, and Untrusted Content](caching-limits-security.md) - Caching and refresh, rate limits and failures, and handling untrusted remote content.
* [MCP Interface, Testing, and Acceptance](mcp-testing-acceptance.md) - Remote operations in MCP, test strategy, implementation sequence, decisions, and acceptance.
