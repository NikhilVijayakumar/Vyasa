# Interface and Data Contract: openspec-okf-knowledge-rules

- **OpenSpec Change ID:** `openspec-okf-knowledge-rules`
- **Proposing team:** be (backend team)
- **Related proposal:** `proposal.md`
- **Related specifications:** `specs/`
- **Related design:** `design.md`

## 1. Purpose

Fixes the contract of the knowledge bundle verifier: its command line, its output, and the profile and frontmatter keys it reads. No MCP tool, index table, or sync exchange is involved.

## 2. Scope

In: `scripts/verify_knowledge.py` CLI, `knowledge/profile.json` keys, concept frontmatter keys. Out: MCP tools, SQLite index, Google Sheets, provider calls (not affected).

## 3. Interface Surface

| Operation | Kind | Access | Input | Success output | Errors |
|---|---|---|---|---|---|
| `verify_knowledge.py [bundle]` | CLI | Reads `*.md` and `profile.json` under the bundle; writes nothing | Optional bundle path (default `knowledge/`) | `WARN`/`FAIL` lines, then `knowledge: N concept(s), E error(s), W warning(s)`; exit 0 when E is 0 | Exit 1 when E > 0; missing `profile.json` is one `FAIL` |

Profile keys (all optional, additive):

| Key | Type | Meaning |
|---|---|---|
| `required_sections` | object: type name to list of heading names | Each heading must appear as a top-level `# Name` (case-insensitive, trimmed) with non-blank content before the next top-level heading |
| `forbidden_words` | list of regular expressions | Matched case-insensitively against each concept's frontmatter description and body |

Frontmatter key (optional, required on a deprecated Decision): `superseded_by` — an in-bundle absolute path such as `/decisions/b.md`.

## 4. Error Model

| Condition | Error code | Response shape | Safe to show the user |
|---|---|---|---|
| Required section missing | none (text) | `FAIL <file>: missing required section '<name>'` | Yes |
| Required section empty | none | `FAIL <file>: required section '<name>' is empty` | Yes |
| Forbidden word matched | none | `FAIL <file>: matches forbidden pattern '<pattern>'` | Yes |
| Open questions in stable concept | none | `FAIL <file>: stable concept has an Open questions section` | Yes |
| `superseded_by` target missing or wrong type | none | `FAIL <file>: superseded_by '<target>' <reason>` | Yes |
| Deprecated Decision without `superseded_by` | none | `FAIL <file>: deprecated decision has no superseded_by` | Yes |
| Invalid regular expression in profile | none | `FAIL profile.json: forbidden_words '<pattern>' is not a valid regular expression` | Yes |

Messages name bundle-relative paths only and never echo matched body text.

## 5. Trust Boundary

The bundle and its profile are repository files in a developer's checkout. The verifier never executes them. Regular expressions come from the checked-in profile (trusted configuration); concept text is matched against them but never evaluated. A target outside the bundle is rejected by the existing path check before it is read.

## 6. Data Model

| Entity | Field | Type | Required | Constraint or invariant |
|---|---|---|---|---|
| Profile | `required_sections` | object | No | Keys are profile type names; values are non-empty lists of strings |
| Profile | `forbidden_words` | list of strings | No | Each compiles as a regular expression |
| Concept | `superseded_by` | path | Yes for a deprecated Decision | Resolves in the bundle to a concept of the same type |

A violated constraint is reported as an error; the verifier continues and reports all violations in one run.

## 7. Migrations and Backward Compatibility

Backward compatible. A profile without the new keys skips the checks. Rollout order: verifier and tests first, then the profile keys in the same commit series, so the repository never has a profile the verifier cannot read. Rollback: remove the keys from `profile.json`.

## 8. Traceability

| Requirement | Operation | Field or rule | Acceptance scenario |
|---|---|---|---|
| Required sections per type | CLI | `required_sections` | Decision without alternatives; Empty required section |
| Banned delivery words | CLI | `forbidden_words` | Task vocabulary in a concept; Invalid pattern |
| Stable concepts have no open questions | CLI | status `stable` + heading | Stable concept with a question |
| Deprecated decisions name a replacement | CLI | `superseded_by` | Dangling pointer; Deprecated without replacement; Valid replacement |
| Profiles without the new keys keep working | CLI | absent keys | Old profile |

## 9. Contract Review

- [x] Every affected operation is listed with request, response, and errors.
- [x] The error model states which conditions produce which error.
- [x] The trust boundary is stated.
- [x] The data model states the invariants.
- [x] Migration and backward compatibility are stated.
- [x] Every requirement in scope is traced.
- [x] No unresolved contract questions.

**Status:** Draft
