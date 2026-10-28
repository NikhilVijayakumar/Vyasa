---
type: Decision
title: "A Dependency Is Internal Only When Its Name Equals a Package Another Indexed Project Declares in the Same Ecosystem"
description: Dependencies and dependents come from the direct dependencies already read from root manifests; a dependency maps to an indexed project only by exact normalized name within one ecosystem, and any other case stays external or ambiguous with the coverage stated.
tags: [adr, mcp, dependencies, evidence]
status: stable
generated: { by: claude-code/sonnet-5.5, at: 2026-10-28T14:00:00Z }
---

# Status

Accepted. Implemented and verified.

# Context

Coding agents ask what a project depends on and what depends on it. The index already holds each checkout's direct dependencies with scope and constraint from its root manifests. Linking a dependency to another project in the portfolio needs a rule that creates no edge the files do not support: names collide across ecosystems, forks and mirrors reuse names, and a partly read repository says nothing about what it lacks.

# Decision

A project's declared package names come from the same root manifests: the `[project]` or Poetry name for Python, `name` for JavaScript, `[package]` name for Rust, the `module` path for Go. A `requirements*.txt` file declares none. A dependency maps to another indexed project only when its normalized name equals a declared package name of that project in the same ecosystem; one matching project is internal, several are ambiguous and are all listed, none is external. Dependents are the same relation read in reverse. Only direct dependencies of active checkouts from the latest observation are used; transitive dependencies are never inferred. Every answer carries a coverage object that says which manifests were parsed, which were not, and whether declared names were recorded, and no answer is presented as an exhaustive graph. A project never depends on itself.

# Alternatives considered

- **Match on repository remote or path.** Rejected: a manifest does not state it, so the edge would be a guess.
- **Match across ecosystems by name.** Rejected: unrelated packages share names.
- **Pick one project when several declare the name.** Rejected: hides a real ambiguity; listing every candidate is honest.
- **Read lockfiles for transitive dependencies.** Rejected for now: a larger surface and untrusted input; out of scope in the requirements.
- **Use the project's display name as the package name.** Rejected: display names come from many sources and are not package identities.

# Consequences

- A project whose manifests declare no name cannot be the target of an internal edge; it still lists its own dependencies.
- Observations made before declared names were stored report that fact in coverage until the next scan.
- Results explain their basis: each edge names the manifest that declared the dependency and the manifest that declared the package.

# Related

- [Frameworks Come From Strictly Read Root Manifests With Scoped Dependencies and Honest States](/decisions/framework-detection-from-manifests.md)
- [Partial Results Never Imply Absence](/decisions/partial-results-never-imply-absence.md)
- [Evidence and Provenance](/concepts/evidence-and-provenance.md)
