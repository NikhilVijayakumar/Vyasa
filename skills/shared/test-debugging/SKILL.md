---
name: test-debugging
description: >-
  Diagnoses failing tests systematically using evidence — traces, logs,
  screenshots, response payloads, and database state — and distinguishes
  product bugs from test bugs. Use when any automated check fails, flakes, or
  behaves unexpectedly during implementation or verification.
---

# Test Debugging

A failing test is information, not an obstacle. Diagnose before touching
anything. Technology-agnostic: use the evidence your stack actually produces.

## Workflow

1. **Reproduce.** Run the failing check in isolation. A failure that only
   appears in the full suite is an ordering/parallelism/fixture problem — note
   which, and say so.
2. **Read the evidence, in order:** assertion diff → captured error/output →
   trace or video (browser tests) → server/API response payload → logs →
   database state at failure time.
3. **Classify before fixing:**
   - **Product bug** — the behavior violates the specification. Fix the product.
   - **Test bug** — the check asserts wrongly, depends on order, or uses stale
     data. Fix the test.
   - **Environment/infra problem** — service down, port conflict, missing
     dependency. Fix the environment; do not paper over it.
   - **Genuine flake** — nondeterministic timing, shared state, external
     dependency. Add the fix's root cause to the report; do not just retry.
4. **Fix the root cause, once.** Before editing a shared helper or fixture,
   grep for its other callers — one guard in the shared function beats a guard
   in every caller.
5. **Re-run the check and the surrounding suite** to confirm no regression.

## Rules

- Never weaken, delete, skip, or loosen an assertion to make a failure pass.
  That converts a finding into a cover-up.
- Never add blind retries as the "fix" for a flake. Diagnose the
  nondeterminism (timing, shared state, ordering) and remove it.
- Preserve evidence: a failing-run trace, screenshot, or payload attached to
  the change record is worth more than a prose claim.
- If the specification is ambiguous and the product behavior is arguably
  correct, raise the ambiguity — do not silently rewrite the test to match
  whatever the code does.

## Evidence

Report per failure: the observed error, the classification (product / test /
environment / flake), the root cause, the fix, and the re-run result. If a
failure could not be diagnosed, record it as unresolved with the evidence
gathered — never as passed.
