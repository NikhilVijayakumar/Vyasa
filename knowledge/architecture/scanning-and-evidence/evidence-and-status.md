---
type: Architecture
title: "Scanning and Evidence: Evidence Model, Statuses, and Resolution"
description: Evidence requirements and granularity, observation statuses, and how values and ownership are resolved.
tags: [scanning, detectors, evidence, provenance]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/scanning-and-evidence.md
    title: Scanning and Evidence
---

# Scanning and Evidence: Evidence Model, Statuses, and Resolution

*Sections 10–12 of [Scanning and Evidence](/architecture/scanning-and-evidence.md).*

## 10. Evidence Model

### 10.1 Evidence Requirements

Each supported observation should retain enough information to identify why the scanner produced it.

Evidence should include, as applicable:

- Source category.
- Repository or entity identity.
- Repository-relative file path.
- Relevant field or configuration key.
- Line range, where reliable.
- Detector identifier and version.
- Observation timestamp.
- Repository revision, where available.
- Optional content fingerprint.

### 10.2 Evidence Examples

| Observation | Appropriate evidence |
|---|---|
| README exists | Repository-relative README path and successful inspection result |
| Python manifest detected | Path to the recognized manifest |
| Framework dependency declared | Manifest path and relevant dependency field |
| OpenSpec configuration valid | Configuration path, parser result, and supported validation version |
| Agent instructions detected | Instruction filename and scope |
| Tests detected | Test file or configuration path |
| Project purpose declared | Canonical profile or recognized documentation field |
| Remote repository discovered | Provider identity and repository reference |

### 10.3 Evidence Granularity

Evidence must be sufficiently precise to explain a result, but should not require storing the full contents of every source file.

For example, a dependency observation should ideally identify the manifest field that declares the dependency rather than merely pointing to the repository root.

### 10.4 Evidence Freshness

Evidence is an observation at a particular time, not a guarantee that the source remains unchanged forever.

If a relevant source changes, the corresponding observation must be revalidated or marked stale.

### 10.5 Sensitive Content

Evidence references must not copy credentials, tokens, or secret values into the index.

If a supported configuration contains both public metadata and sensitive values, the detector must extract only the necessary fields.

---

## 11. Observation Status and Interpretation

Vyasa must use explicit statuses with stable meanings.

| Status | Meaning | Example |
|---|---|---|
| `observed` | A supported detector found evidence for a value | A manifest declares a dependency |
| `declared` | A recognized authoritative source explicitly provides the value | Project purpose in canonical profile |
| `not_detected` | A complete supported inspection found no matching indicator | No recognized README found |
| `unknown` | Available evidence cannot establish the value | Project purpose is undocumented |
| `unsupported` | The system does not support assessing the source or format | Unknown manifest schema |
| `inaccessible` | The relevant source could not be inspected | Permission denied |
| `stale` | A prior observation may no longer reflect current source state | Source changed since extraction |
| `conflicting` | Multiple observations disagree and cannot yet be resolved | Conflicting authoritative declarations |

These statuses apply to observations and should not be used indiscriminately as project lifecycle states.

### 11.1 Absence of a File

The scanner may report `not_detected` only when the relevant search scope completed successfully.

If a directory was inaccessible or traversal stopped early, the result must indicate incomplete assessment instead.

### 11.2 Invalid Configuration

If a recognized configuration exists but fails supported validation, Vyasa should report:

- Configuration detected.
- Validation failed or unsupported.
- Relevant evidence and safe diagnostic information.

It must not reduce the result to "configuration absent."

### 11.3 Conflicting Values

When multiple sources provide conflicting values, the scanner should preserve the observations.

The application layer applies the ownership and precedence policy. If that policy cannot resolve the conflict, the result remains visibly conflicting.

---

## 12. Metadata Resolution and Ownership

Scanning and value resolution are separate operations.

The detector produces observations. The application layer decides how those observations contribute to the resolved project record.

### 12.1 Resolution Process

1. Validate the observation against its field definition.
2. Attach its source and evidence.
3. Identify the field's authoritative owner.
4. Evaluate source eligibility and freshness.
5. Apply the field-specific precedence policy.
6. Retain unresolved conflicts.
7. Update the resolved index representation.
8. Record the outcome.

### 12.2 Examples

**Project purpose**

A canonical profile declares the purpose while the README contains a different description. Vyasa retains both observations and follows the documented purpose precedence rule.

**Programming languages**

A repository contains Python files and a JavaScript manifest. Vyasa records the supported language evidence independently rather than selecting one language as the only project language.

**README presence**

A README is removed and a complete rescan succeeds. Vyasa updates the current observation to indicate that the README was not detected. It does not rewrite the canonical profile.

**Inaccessible repository**

A previously indexed repository becomes inaccessible. Vyasa marks the affected observations stale or unavailable according to the freshness policy rather than asserting that its files no longer exist.
