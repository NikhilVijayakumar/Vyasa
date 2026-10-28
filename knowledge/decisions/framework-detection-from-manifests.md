---
type: Decision
title: "Frameworks Come From Strictly Read Root Manifests With Scoped Dependencies and Honest States"
description: Technologies are declared by supported root manifests read under strict rules, kept with their scopes, mapped through a registry, and reported per ecosystem with absence claimed only after a complete assessment.
tags: [adr, scanner, frameworks, security]
status: stable
generated: { by: claude-code/sonnet-5.5, at: 2026-10-28T09:00:00Z }
---

# Status

Accepted. Implemented and verified.

# Context

The framework detector is the first detector that opens files from repositories it does not trust. Manifests state what a project is built with, but a file can be huge, a link, binary, malformed, or crafted to exhaust a parser, and a scan that stopped early or skipped a monorepo's nested manifests cannot say a framework is missing.

# Decision

Only supported manifests at the checkout root are read: Python `pyproject.toml` and `requirements*.txt`, JavaScript `package.json`, Rust `Cargo.toml`, Go `go.mod`. A manifest is opened only if it is a regular file and not a link, at most 1 MiB of it is read, it must decode as strict UTF-8, and any parser failure, including excessive nesting, makes it `malformed` with a fixed reason code; its text is never stored. Nothing is executed or imported, and `setup.py` is never read. Each manifest has its own status, so one bad file does not hide another. Direct dependencies are recorded with their declared constraint and a scope of runtime, dev, optional, or build, at most 200 per manifest with the total; unsupported kinds such as platform-specific tables and Go indirect requirements are counted as skipped. A versioned registry maps dependencies to technologies; a technology carries the set of scopes it was declared in, and an unknown dependency creates no technology. Nested manifests of a supported name are counted per ecosystem and not parsed; a workspace declaration is a flag. Each ecosystem is `detected`, `not_detected` only after a complete assessment, `unknown` when the walk stopped early, or `not_assessed` for an observation made before this detector. Results are stored on the checkout's observation with the registry version. A search matches a technology key in the current observation of any active checkout.

# Alternatives considered

- **Parse every manifest at any depth.** Rejected: multiplies reads, storage, and time, and needs per-path caps.
- **Lenient parsing that salvages malformed files.** Rejected: interpreting a broken file speculatively produces facts the file does not state.
- **Follow symlinked manifests inside the checkout.** Rejected: breaks the rule used everywhere else that links are not followed.
- **Runtime dependencies only.** Rejected: loses test and lint frameworks and drops declared scopes silently.
- **Merge all scopes.** Rejected: the inventory forbids flattening scopes.
- **Free-text dependency-name search.** Rejected: an open surface and many index rows for no closed vocabulary.
- **Import a YAML library to read compose files now.** Rejected for the first version: it adds a dependency; Docker and compose are deferred.

# Consequences

- A monorepo reads as incompletely assessed rather than as having no frameworks.
- Adding an ecosystem or a technology is a parser or data change with its own tests.
- The registry version is part of every result; changing it makes earlier results stale at the next scan.
- Declared dependencies say what a project declares, not what is installed or used.

# Related

- [Technology Registry as Versioned Data](/decisions/technology-registry-as-data.md)
- [Scan Limits and Symlink Defaults](/decisions/scan-limits-and-symlink-defaults.md)
- [Partial Results Never Imply Absence](/decisions/partial-results-never-imply-absence.md)
- [One Walk Per Checkout Feeds Counts and Languages on One Observation](/decisions/checkout-walk-observation.md)
