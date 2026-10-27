---
type: Decision
title: "Project Markers Are Presence-Only With Three States and Capped Relative Paths"
description: README, documentation, agent instruction, OpenSpec, and test markers are found from names and directories only, reported as detected, not detected, or unknown, with capped repository-relative evidence.
tags: [adr, scanner, markers, evidence]
status: stable
generated: { by: claude-code/sonnet-5.5, at: 2026-10-27T20:00:00Z }
---

# Status

Accepted. Implemented and verified.

# Context

Agents want to know whether a project has a README, documentation, agent instructions, an OpenSpec setup, and tests. File names answer each cheaply, but a name proves presence, not quality, and a scan that stopped early cannot say a marker is missing. Reading file contents would add parsing and untrusted-input risk the scan has not taken on.

# Decision

Markers are found by documented rules from names and directories only, with the rules held as versioned data. README, documentation, and OpenSpec markers are looked for at the checkout root; agent instruction files and tests are looked for at any depth. The OpenSpec indicators are separate markers. Each marker is `detected` with its rule and repository-relative paths (at most twenty stored, with the total), `not_detected` only after a complete assessment, or `unknown` when the walk stopped early and the marker was not found. Agent instruction files carry their scope. An observation made before markers existed is `not_assessed`, and each observation records the rules version it used. Markers are detected from the same walk as the counts and languages and stored with that observation. A search matches a project when any active checkout has the requested marker in the requested state; an unknown checkout matches neither state.

# Alternatives considered

- **Detect OKF, OpenSpec validity, and README sections now.** Rejected: each opens files and needs its own parsing and size limits.
- **Count-only indicators with no paths.** Rejected: loses the evidence path the inventory asks for.
- **Uncapped paths.** Rejected: a monorepo with thousands of test files bloats the index and tool output.
- **Look for every marker at any depth.** Rejected: a README in a vendored subfolder makes "has a README" meaningless.
- **Treat older observations as not detected.** Rejected: it tells agents a project has no README until the next scan.
- **One boolean parameter per marker.** Rejected: the tool signature would grow with each detector.

# Consequences

- Markers mean "detected by these rules", never quality or completeness.
- Adding a recognized name is a data change.
- Projects scanned before this decision show `not_assessed` until the next scan.
- OKF detection and OpenSpec validity remain unbuilt until file reading is reviewed.

# Related

- [One Walk Per Checkout Feeds Counts and Languages on One Observation](/decisions/checkout-walk-observation.md)
- [Partial Results Never Imply Absence](/decisions/partial-results-never-imply-absence.md)
- [MCP Omits Local Paths by Default](/decisions/mcp-local-paths-omitted-by-default.md)
