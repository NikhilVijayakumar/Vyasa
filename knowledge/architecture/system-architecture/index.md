# System Architecture — parts

Parts of [System Architecture](/architecture/system-architecture.md).

* [Context and Vision](context-and-vision.md) - Why Vyasa exists architecturally, its guiding principles, and the external systems it touches.
* [Architectural Layers](layers.md) - The domain, application, adapter, and entry-point layers and what each may depend on.
* [Component Responsibilities](components.md) - What each component owns: configuration, discovery, inspection, detectors, identity, normalization, index, persistence, query, MCP, Sheets, providers.
* [Dependency Direction and Package Structure](structure.md) - The allowed dependency direction and the proposed Python package layout.
* [Core Domain Model](domain-model.md) - Logical project, repository, checkout, observation, evidence, and relationship as architectural building blocks.
* [Scan, Query, MCP, and Storage Data Flows](data-flows.md) - How data moves through a scan, an incremental scan, a query, an MCP call, and storage.
* [Phase 2 and 3 Integrations and Security Architecture](phase-integrations.md) - How Google Sheets and provider adapters attach to the core and where the security boundaries sit.
* [Error Handling, Testing, and Technology Choices](operations.md) - Error and observability architecture, the testing architecture, and the technology baseline.
* [Decisions, Evolution, and Acceptance](decisions-and-evolution.md) - Mandatory constraints, undecided items, how the architecture grows by phase, and its acceptance criteria.
