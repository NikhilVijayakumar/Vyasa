# Scanning and Evidence — parts

Parts of [Scanning and Evidence](/architecture/scanning-and-evidence.md).

* [Principles and Scanning Pipeline](principles-and-pipeline.md) - Core scanning principles and the stages of the scanning architecture.
* [Workspace Discovery and Repository Inspection](discovery-and-inspection.md) - Configured roots, candidates, nesting, exclusions, symlinks, outcomes, inventory, reading, limits, and Git metadata.
* [Detectors, Identity, and Profile Detection](detectors-identity-profile.md) - The detector contract and registry, identity detection inputs, and the canonical profile and draft rules.
* [Metadata Detector Inventory](detector-inventory.md) - Each supported detector: identity, Git, languages, technologies, README, documentation, OpenSpec, agent files, tests, dependencies, OKF, README quality.
* [Evidence Model, Statuses, and Resolution](evidence-and-status.md) - Evidence requirements and granularity, observation statuses, and how values and ownership are resolved.
* [Incremental, Full, and Partial Scans](incremental-and-partial.md) - Invalidation rules for incremental scans and the semantics of full, partial, and interrupted scans.
* [Local and Remote Evidence, Sheets, and Performance](remote-sheets-and-performance.md) - How evidence differs locally and remotely, how it reaches the registry, and resource expectations.
* [Detector Testing, Maintenance, and Acceptance](testing-and-acceptance.md) - Detector test strategy, inventory maintenance, acceptance criteria, and open decisions.
