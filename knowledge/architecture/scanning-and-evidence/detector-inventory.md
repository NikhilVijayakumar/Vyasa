---
type: Architecture
title: "Scanning and Evidence: Metadata Detector Inventory"
description: Each supported detector: identity, Git, languages, technologies, README, documentation, OpenSpec, agent files, tests, dependencies, OKF, README quality, file composition.
tags: [scanning, detectors, evidence, provenance]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/scanning-and-evidence.md
    title: Scanning and Evidence
---

# Scanning and Evidence: Metadata Detector Inventory

*Sections 9 of [Scanning and Evidence](/architecture/scanning-and-evidence.md).*

## 9. Metadata Detector Inventory

The initial detector inventory is grouped by domain. Exact supported file patterns must be maintained as a versioned detector specification and tested against fixtures.

### 9.1 Project Identity and Description Detector

**Purpose:** Extract project name and explicitly documented descriptive metadata.

Potential sources:

- Canonical project profile.
- Recognized manifest metadata.
- Explicit project description fields.
- README metadata or defined sections, if a deterministic parser is implemented.
- Repository directory name as a fallback display name.

Rules:

- Record the source of each value.
- Apply the documented field precedence rules.
- Do not infer project purpose from technology choices or filenames.
- If no supported source establishes purpose, report it as unknown or not documented.

### 9.2 Git Detector

**Purpose:** Inspect local Git identity and repository metadata.

Potential outputs:

- Repository root.
- Remote names and URLs.
- Current revision, when available.
- Local checkout mapping.
- Supported repository structure indicators.

Rules:

- Do not fetch remote content as part of local scanning.
- Do not treat a remote URL alone as proof that the remote repository is accessible.
- Keep local checkout paths separate from shareable repository identity.
- Do not automatically merge forks and upstream repositories.

### 9.3 Programming Language Detector

**Purpose:** Identify languages supported by deterministic file and manifest rules.

Potential evidence:

- Recognized source-file extensions.
- Recognized language-specific manifests.
- Recognized build or project configuration files.

Rules:

- File extension detection establishes that files of a recognized type are present.
- A manifest may provide stronger evidence that a language is part of the project's declared build configuration.
- The detector must document whether its output means "files detected," "language declared," or another specific status.
- It must not claim that a language is actively used at runtime solely from a filename.
- Generated files and vendored directories may require explicit exclusions.

If multiple evidence types are combined, their meanings must remain distinguishable.

### 9.4 Framework and Technology Detector

**Purpose:** Identify supported frameworks, libraries, and technologies from recognized manifests and configuration.

Candidate input formats may include:

- `package.json`
- `pyproject.toml`
- `requirements.txt`
- `Cargo.toml`
- `pom.xml`
- `build.gradle`
- `build.gradle.kts`
- `*.uproject`
- Other formats explicitly added to the detector inventory

This list is illustrative, not a guarantee that every format or framework is already supported.

Rules:

- Each manifest format must have a dedicated parsing and validation policy.
- Technology mappings must be explicit and testable.
- Dependency names should be normalized to stable identifiers when possible.
- Declared versions and constraints must be retained where useful.
- Optional dependencies, development dependencies, workspaces, and platform-specific declarations must not be silently flattened into one misleading list.
- Unsupported manifests must be reported as unsupported rather than interpreted speculatively.

### 9.5 README Detector

**Purpose:** Determine README presence and supported metadata extraction.

The detector may record:

- Whether a recognized README exists.
- Its repository-relative path.
- Whether it can be read.
- Its format.
- Explicit metadata or sections recognized by a documented parser.

The detector must distinguish:

- README detected.
- README not detected after a complete supported search.
- README inaccessible.
- README unsupported or malformed.

### 9.6 Documentation Structure Detector

**Purpose:** Identify documentation directories, entry points, and recognized structures.

Potential observations include:

- Documentation directory presence.
- Recognized entry-point documents.
- Known architecture, requirements, or operations documents.
- Recognized documentation index files.
- Known specification and change directories.

Rules:

- Presence is not quality.
- A directory name alone does not prove that the expected documentation is complete.
- The detector must distinguish a recognized structure from a partially matching structure.
- It must not infer undocumented architectural content from filenames.

### 9.7 OpenSpec Detector

**Purpose:** Determine whether recognized OpenSpec artifacts are present and which supported configuration state can be established.

The detector must evaluate separate indicators rather than a single boolean.

Proposed indicators:

1. OpenSpec-related directory detected.
2. Recognized configuration file detected.
3. Configuration parses successfully under supported validation rules.
4. Recognized specifications detected.
5. Recognized change artifacts detected.
6. Recognized templates or instructions detected, if included in the detector specification.

These indicators must remain separate.

For example, a repository may contain an OpenSpec directory but lack a valid configuration. Another repository may have a valid configuration but no meaningful specifications yet.

The detector must:

- Follow the supported OpenSpec version and format rules.
- Avoid treating arbitrary directories or similarly named files as valid OpenSpec.
- Report unsupported schema versions explicitly.
- Distinguish configuration validity from meaningful artifact presence.
- Preserve evidence paths for each reported indicator.

The exact validity rules must be documented against the supported OpenSpec format before implementation.

### 9.8 Agent Instruction Detector

**Purpose:** Detect recognized coding-agent instruction files.

Candidate files may include:

- `AGENTS.md`
- `CLAUDE.md`
- Other explicitly supported instruction files.

The supported inventory must be maintained as a documented list rather than assumed to include every possible agent convention.

The detector may record:

- Filename and repository-relative path.
- Whether the file is readable.
- Whether it applies at the repository root or a nested path.
- The recognized instruction convention.

It must not execute instructions or treat repository instructions as commands to the Vyasa scanner.

Nested instruction files must be represented with their scope rather than incorrectly treated as a single global instruction file.

### 9.9 Test Indicator Detector

**Purpose:** Identify supported evidence that a project has test-related artifacts or configuration.

Potential evidence includes:

- Recognized test directories.
- Recognized test file naming patterns.
- Test framework configuration.
- Build tool test configuration.
- Recognized test-related package dependencies.

Rules:

- Test-related artifacts establish the presence of indicators, not successful test execution.
- Vyasa must not execute test suites during routine scanning.
- A lack of recognized test indicators means "not detected by supported rules," not necessarily "no tests exist."
- The detector must record which evidence established the indicator.

### 9.10 Dependency Detector

**Purpose:** Extract supported declared dependencies and identify relationships to indexed projects when reliable identity evidence exists.

Rules:

- Parse only supported manifests.
- Preserve dependency names and declared version constraints where available.
- Distinguish direct declarations from transitive dependencies when the source permits.
- Distinguish optional and development dependencies when represented by the manifest.
- Do not claim a complete resolved dependency graph when only declarations were inspected.
- Do not invent internal project relationships from similar package names alone.

Internal dependency matching is a separate deterministic resolution step after extraction.

### 9.11 OKF Detector

**Purpose:** Determine whether the repository contains one or more bundles in Google Cloud's [Open Knowledge Format](/technologies/okf.md), which version they declare, and whether they conform.

OKF here always means the Open Knowledge Format specification (v0.2 current, v0.1 accepted). No other expansion is considered.

**Recognition rule.** A bundle is recognized only by an `index.md` whose YAML frontmatter declares `okf_version`. The directory containing that file is the bundle root. Frontmatter with a `type` key alone is not evidence, because static-site generators and documentation tools use the same convention.

Indicators, kept separate:

1. **Bundle declared** — repository-relative path of each declaring `index.md`, and the declared version.
2. **Version supported** — `0.1` and `0.2` are supported; any other value is reported as `unsupported` with the declared value as evidence.
3. **Concept count** — number of non-reserved `.md` files under the bundle root (excluding nested bundle roots).
4. **Conformance (OKF §11)** — count of concept files without parseable frontmatter or without a non-empty `type`; zero means conformant.
5. **Trust coverage** — counts of concepts carrying `generated`, `verified`, and `status: deprecated`, if included in the detector specification.

The detector must:

- Search within the repository using the scanner's normal exclusions, depth, file-count, and file-size limits.
- Read frontmatter only; never store concept bodies, `sources` values, or executor/attester code, and never run attesters or executors.
- Report multiple bundles independently; a nested bundle root ends the parent bundle's scope.
- Report `not_detected` when no declaring `index.md` exists after a complete inspection, `inaccessible` when the search could not complete, and `unsupported` for an unknown declared version.
- Treat an undeclared directory of frontmatter documents as `not_detected`, documenting this as a known limitation rather than guessing.
- Preserve evidence paths for each indicator.

### 9.12 README Quality Assessment

README quality is not a directly observable binary fact.

If assessment is implemented, it must use an explicit deterministic checklist, such as whether specified sections, links, or usage instructions are present.

The system must distinguish:

- Not assessed.
- Checklist passed.
- Checklist partially satisfied.
- Checklist failed.
- Assessment unavailable.

A checklist result must not be presented as a subjective or universal quality judgment.

Until a checklist is approved, the recommended default is `not_assessed`.

### 9.13 File Composition Detector

**Purpose:** Report how many files of a checkout are code, documentation, or other, so that a documentation-only or code-heavy project can be told apart without reading any file.

Output, per checkout:

- `code_files`, `documentation_files`, `other_files`, and `total_files`, which always sum.
- `documentation_only`, derived: documentation files exist and no code files do.
- A completeness marker: `complete`, or `partial` with the limit that stopped the count.

Rules:

- Classification is by file extension only, from versioned data: a code extension is one the language detector (§9.3) recognizes; a documentation extension comes from a documentation list in the same data. Content is never read.
- An extension in neither list is `other`. An unknown file type is never counted as code.
- A file is counted once. Directory symlinks are not followed, and a symlinked file is counted as itself, not as its target.
- Vendored, generated, and version-control directories are excluded by the configured exclusion rules; the exclusion list is part of the evidence.
- The count is "files detected", in the sense of §9.3. It does not say a language is used or documentation is complete (§9.6).
- The count walk is bounded by depth and time. Reaching a bound makes the observation `partial`: the counts are lower bounds and `documentation_only` is `unknown`. A partial count never supports a conclusion that something is absent.
- The language detector's per-language histogram and these counts come from one walk, so they agree.
- The counts describe one checkout. The same project in two workspace roots has two observations; they are never summed.

Evidence: the checkout, the extension data version, the exclusion rules, the completeness marker, and the observation time.

Failure and limit cases:

- Unreadable directory: counted as skipped; the observation is `partial`.
- Checkout with no files: all counts are zero, complete, `documentation_only` is false.
- Case-differing extensions (`.MD`, `.md`) are the same extension.
