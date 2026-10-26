---
type: Architecture
title: "Scanning and Evidence: Workspace Discovery and Repository Inspection"
description: Configured roots, candidates, nesting, exclusions, symlinks, outcomes, inventory, reading, limits, and Git metadata.
tags: [scanning, detectors, evidence, provenance]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/scanning-and-evidence.md
    title: Scanning and Evidence
---

# Scanning and Evidence: Workspace Discovery and Repository Inspection

*Sections 4–5 of [Scanning and Evidence](/architecture/scanning-and-evidence.md).*

## 4. Workspace Discovery

### 4.1 Configured Roots

Vyasa MUST scan only configured workspace roots and paths permitted by the effective configuration.

The configuration must support:

- One or more workspace roots.
- Exclusion rules.
- Supported discovery depth or traversal boundaries.
- Symlink handling policy.
- Local index location.
- Enabled detector options, where applicable.

If no valid roots are configured, Vyasa must report that discovery is not configured rather than scanning an unintended default location.

### 4.2 Candidate Discovery

A directory may qualify as a candidate through recognized evidence such as:

- Git repository metadata.
- A recognized project manifest.
- A canonical project profile.
- Other explicitly configured project markers.

The final discovery policy must define how non-Git directories qualify as projects and how broad directory traversal is allowed to be.

A directory must not become a project merely because it exists.

### 4.3 Nested Repositories

Nested repositories must be handled using explicit rules.

The scanner must distinguish:

- A repository nested inside another repository.
- A Git submodule.
- A normal directory inside a repository.
- A linked worktree or another Git-managed checkout, where supported.

Metadata from separate repositories must not be merged simply because their directories are nested.

### 4.4 Exclusions

Excluded paths must not be scanned for project discovery or metadata extraction.

The implementation must define how exclusion patterns are matched, including whether rules apply to directory names, relative paths, or both.

Exclusion rules should be evaluated before expensive file inspection.

### 4.5 Symlinks and Path Boundaries

The initial recommended policy is not to follow directory symlinks during recursive traversal.

If symlinks are followed through an explicitly configured option, the scanner must resolve paths safely and enforce the permitted root boundaries.

The scanner must not unintentionally escape configured roots or repeatedly traverse filesystem cycles.

### 4.6 Discovery Outcomes

Each candidate must have an outcome that distinguishes, as applicable:

- Discovered and eligible.
- Excluded.
- Not a recognized project.
- Inaccessible.
- Malformed.
- Skipped by policy.
- Identity unresolved.

A candidate that cannot be inspected must not be reported as successfully scanned.

---

## 5. Repository Inspection and File Inventory

### 5.1 Relevant File Inventory

Vyasa should build an inventory of files relevant to supported detectors rather than read every file in every repository.

The inventory may include:

- File path relative to the repository.
- File type or recognized role.
- File size.
- Modification metadata.
- Content fingerprint, when needed.
- Readability and inspection outcome.

The inventory is generated operational state. It must not be confused with a complete or authoritative description of all repository content.

### 5.2 File Reading

The scanner MUST:

- Read only the files needed for enabled detectors.
- Use safe parsing libraries and bounded resource consumption.
- Avoid executing repository scripts.
- Avoid evaluating arbitrary configuration expressions.
- Handle malformed text and unsupported encodings without terminating unrelated scanning.
- Avoid retaining unnecessary source content in the local index.

### 5.3 File Size and Resource Limits

The implementation must define configurable or documented limits for:

- Individual file size.
- Total files inspected per project, where needed.
- Directory traversal depth.
- Parsing resource consumption.
- External API response size in later phases.

When a limit prevents inspection, the result must indicate that the source was skipped or only partially assessed. It must not claim the relevant indicator is absent.

The initial numerical limits should be selected during implementation and validated against representative repositories.

### 5.4 Git Metadata

Supported local Git observations may include:

- Remote names and URLs.
- Repository root.
- Current branch, when available.
- Current commit identifier, when available.
- Working-tree status, if explicitly enabled.
- Submodule or worktree indicators, where supported.

Git metadata inspection must not fetch, pull, checkout, or change repository state unless a separate, explicitly approved feature is introduced.

The default scanner should not require network access to inspect local Git configuration.
