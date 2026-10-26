---
name: deterministic-scanner
description: >-
  Guards Vyasa's scanner and detector code: deterministic extraction, evidence
  and provenance for every value, explicit observation statuses, read-only
  scanning of untrusted repositories. Use whenever workspace discovery, file
  inventory, a detector, or metadata resolution is added or changed.
---

# Deterministic Scanner

Source of truth: `knowledge/architecture/scanning-and-evidence.md`. This skill is
the checklist; the document wins on any conflict.

## Rules

1. **No inference.** Metadata comes from deterministic rules over recognized
   evidence (manifests, config files, Git metadata). Never call an LLM, never
   guess from prose. A README that mentions "React" is not evidence of a React
   dependency (§2.1, §2.2).
2. **Evidence for every value.** Each reported value carries an evidence
   object: `source_type`, `source_ref`, `observed_at`, `revision` (null when
   unknown), and `detector` id + version. Never fabricate a field you cannot
   establish (§10, `mcp-interface.md` §6.4).
3. **Missing is not false.** Use the statuses `observed`, `declared`,
   `not_detected`, `unknown`, `unsupported`, `inaccessible`, `stale`,
   `conflicting` (§11). An empty collection means "inspected, none found";
   an unassessed field gets an explicit status, never an empty list.
4. **Read-only and non-executing.** Never run, import, build, or install
   repository content. No `subprocess` on repository scripts, no `exec`, no
   unpickling, no YAML loaders that construct objects (§2.4).
5. **Bounded.** Respect configured roots and exclusions; resolve symlinks and
   refuse paths that escape a root; enforce file-size and count limits;
   report hits as `inaccessible` or `unsupported`, not as crashes (§4.5, §5.3).
6. **Minimal content.** Store facts and locations, not raw document bodies,
   unless the spec explicitly allows it (§10.5).
7. **Versioned detectors.** Changing a detector's output bumps its version so
   stale observations can be invalidated (§6.2, §10.4).

## Tests every detector change needs

- Positive: recognized evidence yields the value with correct evidence.
- Absent: no evidence yields `not_detected`, not an error.
- Invalid: malformed manifest yields `conflicting`/`unknown` with evidence, scan continues.
- Boundary: symlink escaping the root, oversized file, unreadable file.
- Nested repositories resolve to the documented owner (§4.3).

Use `pytest-skill` for test patterns (`tmp_path` fixture repos), `test-strategy`
for layer placement.

## Output

For a review: list each rule above as pass / fail / not applicable, with
`file:line` for each failure.
