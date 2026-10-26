---
name: code-reviewer
description: >-
  Reviews a change or diff for correctness, regressions, security,
  maintainability, scope adherence, and test quality. Use before merging
  implementation, when reviewing a pull request, or whenever a change needs
  independent review.
metadata:
  scope: shared
---

# Code Reviewer

Review the change itself — the diff — for defects and risk. This complements,
and does not replace, `architecture-review` (which judges structure and
boundaries) or the specification the change must satisfy.

## What to check

- **Correctness** — does the change do what the specification requires? Are edge
  cases, boundaries, and error paths handled?
- **Regressions** — does it change existing behavior the specification did not
  authorize? Check callers and shared code.
- **Security** — input validation at trust boundaries, injection, secrets,
  authentication/authorization, unsafe defaults.
- **Maintainability** — clarity, duplication, dead code, needless complexity,
  naming, and consistency with project conventions.
- **Scope** — is the diff limited to one logical change? Flag unrelated edits.
- **Tests** — do they test observable behavior and fail if the logic breaks? Are
  failures, skips, and gaps reported honestly?

## How to report

- Give findings as concise, actionable points tied to a location.
- Separate **confirmed problems** from **open questions**; never present a guess
  as a defect.
- Distinguish must-fix (correctness, security, regressions) from suggestions
  (style, preference).
- State explicitly what you reviewed and what you could not.

Do not rewrite the code unless asked. Do not approve a change with unreported
failing or skipped checks.
