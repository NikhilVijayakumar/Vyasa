# Interface and Data Contract: be-repository-ignore

- **OpenSpec Change ID:** `be-repository-ignore`
- **Proposing team:** be (backend team)
- **Related proposal:** `proposal.md`
- **Related specifications:** `specs/`
- **Related design:** `design.md`

## 1. Purpose

Fixes the Python interface that parses, reads, and applies a repository's `.vyasaignore`, the new warning, and the evidence additions. No MCP tool, CLI command, index table, or sync exchange is involved.

## 2. Scope

In: `vyasa.domain.ignore`, `vyasa.adapters.filesystem.ignore_file`, and the changes to `discover_repositories` and `compose`. Out: MCP, SQLite, Google Sheets, provider calls (not affected).

## 3. Interface Surface

| Operation | Kind | Access | Input | Success output | Errors |
|---|---|---|---|---|---|
| `parse_ignore(text)` | Python function | None; pure | file text | `(IgnoreRules, problems)` | none |
| `IgnoreRules.matches(relative)` | Python method | None; pure | directory path relative to the repository root, `/` separated | `bool` | none |
| `read_ignore_file(directory)` | Python function | Opens `<directory>/.vyasaignore` read-only, at most 64 KiB + 1 byte | directory path | `(IgnoreRules or None, problems)`; `None` when there is no file or it is unusable | none; problems are values |
| `discover_repositories(...)` | Python function | As before, plus `.vyasaignore` of each repository found | unchanged | `DiscoveryRun` with an optional `ignore_file` warning | none |
| `compose(...)` | Python function | As before, plus `.vyasaignore` of the checkout | unchanged | `FileComposition` with `evidence.ignore` | `ValueError` as before |

Limits: `MAX_IGNORE_BYTES = 65536`, `MAX_IGNORE_PATTERNS = 1000`.

`IgnoreRules`: `patterns` (tuple of normalized pattern strings), `digest` (SHA-256 hex of the patterns joined by newlines).

`problems`: tuple of strings such as `line 3: negation is not supported`, `line 7: path must not contain '..'`, `file is larger than 64 KiB and was ignored`, `too many patterns; the first 1000 apply`.

`ScanWarning` gains `details: tuple[str, ...] = ()`. The `ignore_file` warning has `reason = "ignore_file"`, `count` the number of problems, `examples` up to five ignore files, `details` up to five messages each prefixed with the file's path relative to the root, and advice to fix or remove the lines.

`Evidence` gains `ignore: IgnoreEvidence | None`: `patterns` (int) and `digest` (string); `None` when no ignore file was used.

## 4. Error Model

| Condition | Error code | Response shape | Safe to show the user |
|---|---|---|---|
| Invalid line | none | problem in an `ignore_file` warning; line skipped | Yes |
| File larger than 64 KiB | none | problem; the whole file skipped | Yes |
| More than 1,000 patterns | none | problem; the first 1,000 apply | Yes |
| File unreadable | none | problem `cannot be read`; no rules | Yes |
| No file | none | no rules, no problem | Yes |

Nothing raises. The status of a run is unchanged by ignore problems.

## 5. Trust Boundary

`.vyasaignore` is untrusted repository content. It is read as at most 64 KiB, decoded leniently, parsed as text, and can only remove directories below its own repository from scanning. It cannot add paths, cannot name anything outside the repository (drive letters and `..` are invalid, and a leading slash means the repository root), and is never evaluated. Evidence stores a pattern count and a digest, not the text.

## 6. Data Model

| Entity | Field | Type | Required | Constraint or invariant |
|---|---|---|---|---|
| IgnoreRules | `patterns` | tuple of strings | Yes | At most 1,000; no pattern starts with `!` or a drive letter, or contains a `..` segment; patterns anchored at the root are stored with a leading `/` |
| IgnoreRules | `digest` | string | Yes | SHA-256 of the patterns joined by newlines; equal patterns give an equal digest |
| IgnoreEvidence | `patterns`, `digest` | int, string | Yes | Match the rules used |

## 7. Migrations and Backward Compatibility

A repository without the file behaves as before. `Evidence` gains a field with a default of `None`; `ScanWarning` gains `details` with a default of `()`. Rollback: revert the change.

## 8. Traceability

| Requirement | Operation | Field or rule | Acceptance scenario |
|---|---|---|---|
| Patterns name directories | `parse_ignore`, `matches` | `patterns` | Bare name at any depth; Path from the root; Glob characters; Recursive glob; Case is ignored; Comments, blanks, and slashes |
| The file cannot widen the scan | `parse_ignore` | problems | Invalid lines |
| The file is bounded | `read_ignore_file`, `parse_ignore` | limits | Oversized file; Too many patterns |
| Discovery honors the file | `discover_repositories` | `excluded` count | Ignored directory is not entered; Only below its own repository; Nested repositories keep enclosing rules; Ignored directories do not become depth warnings |
| Mistakes are reported | `discover_repositories` | `ignore_file` warning | Warning for an invalid line |
| File composition honors the file | `compose` | `evidence.ignore` | Ignored files are not counted; Evidence of use; No file |
| Only the ignore file is read | `read_ignore_file` | none | Files opened |

## 9. Contract Review

- [x] Every affected operation is listed with request, response, and errors.
- [x] The error model states which conditions produce which error.
- [x] The trust boundary is stated.
- [x] The data model states the invariants.
- [x] Migration and backward compatibility are stated.
- [x] Every requirement in scope is traced.
- [x] No unresolved contract questions.

**Status:** Draft
