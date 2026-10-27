# OKF Knowledge Rules Grill

A review of change `openspec-okf-knowledge-rules`, run with the `grill-me` skill. The author answered each question
with a recommendation and a priority, checking claims against the real bundle rather than from memory.

**How it was run.** Every Decision concept was parsed for the four required sections; every concept was scanned for
the proposed banned words and for fenced lines that look like headings; the change was validated with
`openspec validate`; the bundle with `scripts/verify_knowledge.py` (134 concepts, 0 errors after the fixes).
**What it was not.** The verifier code does not exist yet, so no rule was exercised by an implementation, only by
the scans above.

**Status key.** *Fixed*: artifacts changed. *Verified*: checked and fine. *Recommended*: my answer, low risk.
*Open*: not done, with a reason. **Priority:** P1 blocks implementation, P2 do during implementation, P3 later.

## Questions

**Q1. Do the new rules pass the bundle that ships with the change?** (P1)

- **Finding:** No. The Writing Knowledge practice said "does not name a change, ticket, sprint, or task". A plain
  `\bticket\b` and `\bsprint\b` ban would have failed the concept that states the rule. The scan found that one hit
  and no other.
- **Action:** Patterns are narrow phrases, not bare words: `\bthis change\b`, `\bthis ticket\b`, `\bthis sprint\b`,
  `\bTODO:`. The practice now says "refer to 'this change' or a work item" and points to the profile for the list.
- **Status:** Fixed

**Q2. Why two supersession fields?** (P1)

- **Finding:** `supersedes` and `superseded_by` state one fact twice, and the spec had to check they agreed. Two
  fields to keep in step by hand is the likelier failure than the one it prevents.
- **Action:** Dropped `supersedes`. One field, `superseded_by`, required on a deprecated Decision, must resolve to a
  concept of the same type. Spec, contract, design, tasks, ADR pointer, practice, and decision concept updated; the
  rejected alternative is recorded in the decision.
- **Status:** Fixed

**Q3. Do all existing decisions satisfy the required sections?** (P1)

- **Finding:** Yes. All 18 have non-empty Context, Decision, Alternatives considered, and Consequences (scanned
  2026-10-27). The rule costs nothing today.
- **Status:** Verified

**Q4. Will a `#` line in a code block be read as a heading?** (P2)

- **Finding:** No concept has one today (0 fenced lines starting `# `). The risk is a future shell snippet.
- **Action:** The design already says fenced lines are not headings; task 2.2 now has a test for it.
- **Status:** Recommended

**Q5. Is "stable has no Open questions" testable today?** (P3)

- **Finding:** No concept is `stable` and none has an Open questions heading, so the rule is checked only by unit
  tests until the first promotion. That is acceptable; it prevents the first bad promotion.
- **Status:** Verified

**Q6. Immutability of accepted decisions is the headline rule in the reference tree. Why is it not enforced?** (P3)

- **Finding:** The verifier reads files, not history. A check needs `git` or a stored hash. Neither is justified
  while all 18 decisions are `draft`; there is nothing accepted to protect yet.
- **Action:** Kept as a review rule in the practice. Revisit when the first decision is accepted.
- **Status:** Open

**Q7. Errors or warnings?** (P2)

- **Finding:** The bundle already passes every rule, so errors cost nothing now and a warning would be ignored. The
  risk is a false positive from a future word. Patterns are data in `profile.json`, so removing one is a one-line
  edit.
- **Status:** Recommended (errors)

**Q8. Should `required_sections` cover Practice, Runbook, Technology too?** (P3)

- **Finding:** No evidence of drift in those types: no incident, no review comment. Adding sections nobody asked for
  is the over-build this change avoids.
- **Status:** Open (add per type when a real gap appears)

**Q9. Does an old profile keep working?** (P1)

- **Finding:** By design each key is optional and guarded with `profile.get`. A test is planned (task 6.2). Without
  it, any other bundle using this verifier could break.
- **Status:** Recommended

**Q10. Is a regular expression in the profile a risk?** (P3)

- **Finding:** The profile is checked-in trusted configuration, so a pattern is code-reviewed with it. A
  catastrophic pattern would slow a local run, not expose data. Invalid patterns are an error, not a crash.
- **Status:** Verified

## Outcome

Two fixes (Q1, Q2) and no blockers. Proposal readiness box "ambiguities challenged" is now checked. Next: implement
in the order of `tasks.md`; revisit Q6 and Q8 at the first accepted decision or the first observed drift.
