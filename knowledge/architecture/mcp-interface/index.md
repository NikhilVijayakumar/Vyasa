# MCP Interface — parts

Parts of [MCP Interface](/architecture/mcp-interface.md).

* [Purpose, Principles, Transport, and Tool Inventory](purpose-and-principles.md) - Why the interface exists, its design principles, server responsibilities, transport, and the tool list.
* [Shared Response Conventions](response-conventions.md) - The response envelope, identifiers, missing values, evidence objects, observation status, and freshness.
* [Search and Project Details Tools](search-and-details.md) - Contracts for search_projects and get_project.
* [Project Context and Related Projects Tools](context-and-related.md) - Contracts for get_project_context and find_related_projects.
* [Dependencies, Index Status, and Refresh Tools](dependencies-status-refresh.md) - Contracts for get_project_dependencies, get_index_status, and the optional refresh_index.
* [Errors, Pagination, and Security](errors-pagination-security.md) - Error codes and shape, validation, pagination, response limits, and the MCP security rules.
* [Later Phases and Client Configuration](phases-and-client-config.md) - How Sheets and remote operations attach later, and how MCP clients launch the server.
* [Testing, Package Layout, and Decisions](testing-and-decisions.md) - Contract and compatibility testing, the proposed package layout, open decisions, and acceptance.
