---
name: accessibility-testing
description: >-
  Verifies accessible controls, keyboard navigation, focus management, roles
  and names, and selected automated accessibility checks in browser tests.
  Use when a change affects interactive UI, forms, navigation, or when a
  specification includes accessibility requirements.
---

# Accessibility Testing

Verify that users who rely on assistive technology or the keyboard can use the
feature. Recommended: run an automated accessibility scanner (for example an
axe-based Playwright integration) plus explicit keyboard checks; substitute the
project's tooling if different.

## What to verify

- **Automated scan:** selected rules (names/roles/labels, contrast, ARIA
  validity) on each page/view the change touches, with zero *serious/critical*
  violations unless a documented, spec-approved exception exists.
- **Keyboard:** every interactive control reachable and operable in a logical
  tab order; no keyboard traps; visible focus indicator.
- **Focus management:** focus moves correctly on route/view changes, dialogs
  (focus trapped and restored on close), and after form errors.
- **Semantics:** controls expose correct roles and accessible names; form
  fields have associated labels; error messages are programmatically linked
  to their inputs.

## Rules

- Automated scans catch a subset only — a passing scan is not a claim of full
  conformance. Record keyboard/focus checks as separate evidence.
- Assert against the specification's accessibility requirements and tag tests
  with their specification IDs; where no requirement or threshold exists,
  record the gap rather than inventing a standard.
- Run these checks as part of browser tests (same journey fixtures as
  `playwright-testing`); component-level role/name assertions belong in
  `react-testing`.
- Never disable, baseline, or delete a failing accessibility check to make a
  change pass — fix the UI or record an approved exception explicitly.

## Boundaries

- Journey orchestration, fixtures, selectors → `playwright-testing`.
- Component structure assertions → `react-testing`.
- Strategy and coverage expectations → `test-strategy`.
- Failure diagnosis → `test-debugging`.
- This skill does not replace manual review with assistive technology where
  the specification requires it.

## Evidence

Report per view/flow: the scan command and result (violations by severity),
the keyboard/focus checks performed, and any approved exceptions — including
checks that could not run.
