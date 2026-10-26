---
name: test-driven-development
description: >-
  Guides test-first (Red-Green-Refactor) development for implementation changes.
  Use when writing or changing production code, adding a feature, or fixing a
  bug, and when an OpenSpec tasks artifact calls for test-first implementation.
metadata:
  scope: shared
---

# Test-Driven Development (Red–Green–Refactor)

Use disciplined test-first development for code changes where practical. This
skill is technology-agnostic: substitute your project's language, test runner,
and conventions for the generic terms below.

## The cycle

1. **Red** — write the smallest failing test that expresses the next piece of
   observable behavior. Run it and confirm it fails for the expected reason. A
   test that already passes before the code exists proves nothing.
2. **Green** — write the minimum production code that makes the test pass. Do
   not add behavior the current test does not require.
3. **Refactor** — improve structure, naming, and duplication with the suite
   green. Do not change observable behavior.

Repeat in small steps. A cycle that takes more than a few minutes is usually
too large; split it.

## Rules

- Test observable behavior, not implementation details.
- One reason to fail per test; assert one logical outcome.
- Reproduce a bug with a failing test before fixing it.
- Never weaken, skip, or delete a test to make implementation pass.
- Do not write production code without a failing test that demands it.
- Run the tests after every change and report the actual result.

## When test-first is impractical

Some changes are hard to drive test-first: exploratory spikes, generated code,
pure configuration, or code with no test harness. When you skip the cycle:

- Say so explicitly, and why.
- Fall back to test-after for the risky logic, or record a concrete follow-up.
- Do not claim test-first evidence you did not produce.

## Evidence

For the OpenSpec verification step, report which tests were written, which
command ran them, and the observed result — including failures, skips, and
checks that could not run. A test count is not evidence; the executed result is.
