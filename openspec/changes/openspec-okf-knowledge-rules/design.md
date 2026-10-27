# Design: openspec-okf-knowledge-rules

## 1. Overview

### Purpose
Add four content-shape checks to the knowledge verifier, driven by optional profile keys.

### Scope
`scripts/verify_knowledge.py`, its tests, `knowledge/profile.json`, one line in `skills/shared/knowledge-first/SKILL.md`.

### Design Principles
Standard library only. Rules are data in the profile, not constants in the verifier. Report every violation in one run. Reuse `split_frontmatter`, `unquote`, and the `errors` list.

## 2. Context and Constraints

### Current State
`check_concept` validates one file at a time against the profile; `verify` loops over files. Cross-file checks (indexes) already exist in `check_indexes`.

### Constraints
- Technical constraints: Python 3.12+, no new dependency.
- Security and privacy constraints: concept text is matched, never executed; messages do not echo body text.
- Performance and reliability constraints: one pass over about 134 small files.
- Compatibility and migration constraints: absent keys disable checks.
- Operational constraints: run by `verify_workflows.py` and by hand.

### Existing Decisions and Conventions
`knowledge/profile.json` is the single rule source; `knowledge/decisions/knowledge-profile-section-rules.md` records this choice.

### Knowledge References
- `knowledge/practices/writing-knowledge.md` — the rules as authors read them.
- `knowledge/decisions/knowledge-profile-section-rules.md` — scope and rejected alternatives.

## 3. Requirements and Traceability

| Requirement or Spec Reference | Design Element | Verification Approach |
|---|---|---|
| Required sections per type | `check_sections(rel, kind, body, profile, errors)` | Unit tests: missing, empty, extra |
| Banned delivery words | `check_words(rel, text, profile, errors)` | Unit tests: hit, miss, invalid pattern |
| Stable concepts have no open questions | Same heading scan as sections | Unit tests: stable, draft |
| Deprecated decisions name a replacement | `check_supersession(bundle, concepts, errors)` after the file loop | Unit tests: valid, dangling, deprecated without pointer, outside |
| Profiles without the new keys keep working | `profile.get(key)` guards | Existing tests unchanged and passing |

## 4. Architecture and Design

### Architectural Approach
A small function per rule, called from `check_concept` (per-file rules) or `verify` (the cross-file supersession rule). A top-level heading scan builds `{name.lower(): content}` once per file and feeds both the section and the open-questions rules.

### Components and Responsibilities
| Component | Responsibility | Dependencies |
|---|---|---|
| `headings(body)` | Map top-level `# Name` to its text until the next top-level heading | none |
| `check_sections` | Required sections present and non-blank | `headings` |
| `check_words` | Pattern hits in description and body | `re` |
| `check_supersession` | Resolve `superseded_by`, same type, deprecated rule | `split_frontmatter` |

### Interfaces and Contracts
See `api-contract.md`. Lines inside fenced code blocks are not headings.

### Key Workflows
`verify` → for each file `check_concept` (sections, words, open questions) → collect `(path, fields)` → `check_supersession`.

## 5. Data and State Management

No stored state. Not applicable beyond the in-memory file list.

## 6. Error Handling and Resilience

| Failure Scenario | Expected Behavior | Recovery or Mitigation |
|---|---|---|
| Invalid regular expression | One `FAIL` naming the pattern; other checks run | Fix the profile |
| Target outside the bundle | Reuse the existing outside-bundle error | Fix the link |
| Unreadable or non-UTF-8 file | Existing behavior unchanged | None |

## 7. Security and Privacy

Trust boundary as in the contract. The profile is checked-in configuration. A catastrophic-backtracking pattern could slow a run; patterns are reviewed with the profile and the run is local. No secrets or paths leave the repository.

## 8. Quality Attributes

| Attribute | Requirement or Constraint | Design Response | Verification |
|---|---|---|---|
| Maintainability | No type constants in code | Rules read from the profile | Test uses a profile fixture |
| Compatibility | Old profiles pass | `profile.get` guards | Old-profile test |

## 9. Testing and Verification Strategy

### Behavioral Verification
One unit test per scenario in `specs/knowledge-bundle-verification/spec.md`.

### Test Strategy
Unit tests in `scripts/test_verify_knowledge.py` using its temporary-bundle helper. Run `python3 scripts/verify_knowledge.py` on the real bundle and `python3 scripts/verify_workflows.py`.

### Testability
The existing `bundle()` helper builds a bundle in a temp directory; the new cases pass a modified profile.

### Verification Evidence
Test output and the real-bundle verifier summary line, recorded when tasks complete.

## 10. Implementation and Migration Considerations

### Implementation Order
Tests and code per rule in the order of the spec; profile keys last.

### Migration and Rollout
Backward compatible; see the contract.

### Documentation and Operations
`knowledge-first` skill gets one pointer to `practices/writing-knowledge.md`.

## 11. Architecture Decision Checkpoint

- **New ADR required:** Yes — already recorded as `knowledge/decisions/knowledge-profile-section-rules.md`; see `adr.md`.
