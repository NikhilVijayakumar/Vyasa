# Interface and Data Contract: be-git-remote

- **OpenSpec Change ID:** `be-git-remote`
- **Proposing team:** be (backend team)
- **Related proposal:** `proposal.md`
- **Related specifications:** `specs/`
- **Related design:** `design.md`

## 1. Purpose

Fixes the Python interface that parses and normalizes Git remotes, the reader of `.git/config`, and the fields added to discovered projects. No MCP tool, CLI command, index table, or sync exchange is involved yet.

## 2. Scope

In: `vyasa.domain.git_remote`, `vyasa.adapters.filesystem.git_config`, and two fields on `Candidate`. Out: MCP, SQLite, Google Sheets, provider calls (not affected).

## 3. Interface Surface

| Operation | Kind | Access | Input | Success output | Errors |
|---|---|---|---|---|---|
| `parse_remotes(text)` | Python function | None; pure | config text | ordered mapping of remote name to URL | none |
| `normalize_remote(url)` | Python function | None; pure | URL or address | `(provider, host, identity)` | none |
| `choose_remote(remotes)` | Python function | None; pure | mapping from `parse_remotes` | `(GitRemote or None, status)` | none |
| `read_remote(directory)` | Python function | Reads `<directory>/.git/config`, at most 64 KiB + 1 byte | directory path | `(GitRemote or None, status)` | none; problems are statuses |
| `discover_repositories(...)` | Python function | As before, plus the config reads | unchanged | candidates with `remote` and `remote_status` | none |

`GitRemote`: `name` (the remote's name), `provider` (`github`, `bitbucket`, `gitlab`, `other`, `local`, or `none`), `host` (lower-case, or `None`), `identity` (`host/org/repo`, or `None`). The original URL is not a field.

Status values: `origin`, `only`, `ambiguous`, `none`, `unavailable`.

`Candidate` gains `remote: GitRemote | None = None` and `remote_status: str | None = None`; both are `None` for a project without Git.

Provider table: `github.com`, `ssh.github.com` → `github`; `bitbucket.org` → `bitbucket`; `gitlab.com` → `gitlab`. Any other host → `other`. A path, relative path, drive-letter path, or `file:` URL → `local` with no identity. Default ports dropped: `https` 443, `http` 80, `ssh` 22, `git` 9418.

## 4. Error Model

| Condition | Error code | Response shape | Safe to show the user |
|---|---|---|---|
| `.git` is a pointer file or link | none | status `unavailable` | Yes |
| Config unreadable, linked, or over 64 KiB | none | status `unavailable` | Yes |
| No remote section | none | status `none` | Yes |
| Several remotes, none `origin` | none | `remote` is `None`, status `ambiguous` | Yes |
| Unparseable URL | none | provider `other` or `local`, identity possibly `None` | Yes |

Nothing raises.

## 5. Trust Boundary

`.git/config` is untrusted repository content. It is read as text, at most 64 KiB, never through a link, and never by running Git. Only the host, the identity, the provider, and the remote's name are kept; the original URL, user information, and tokens are discarded at parse time. A pointer file is not followed, so nothing outside the project is read.

## 6. Data Model

| Entity | Field | Type | Required | Constraint or invariant |
|---|---|---|---|---|
| GitRemote | `name` | string | Yes | A remote name from the config |
| GitRemote | `provider` | enum | Yes | One of the six labels |
| GitRemote | `host` | string | No | Lower-case; `None` for `local` |
| GitRemote | `identity` | string | No | `host[:port]/path`; `None` for `local`; lower-case for `github` and `bitbucket` |
| Candidate | `remote_status` | enum | No | `None` exactly when the project has no Git; `remote` is `None` unless status is `origin` or `only` |

## 7. Migrations and Backward Compatibility

New fields with `None` defaults. Rollback: revert the change.

## 8. Traceability

| Requirement | Operation | Field or rule | Acceptance scenario |
|---|---|---|---|
| Remotes are read from the config text | `parse_remotes` | name to URL | Several remotes; Other sections and comments; Quoted value |
| URLs are reduced to a credential-free identity | `normalize_remote` | `host`, `identity` | Equivalent forms; Credentials are dropped; Non-default port is kept; Case is kept on other hosts |
| The provider comes from the host | `normalize_remote` | `provider` | Known providers; Unknown host; Local forms |
| One remote is chosen | `choose_remote` | status | Origin preferred; Only remote; Ambiguous; No remote |
| The config is read safely | `read_remote` | status `unavailable` | Config is read; Pointer file; Oversized config; Linked config |
| Discovery attaches the remote | `discover_repositories` | `remote`, `remote_status` | Repository; Git in a child folder; Project without Git; Only listed files are opened |

## 9. Contract Review

- [x] Every affected operation is listed with request, response, and errors.
- [x] The error model states which conditions produce which error.
- [x] The trust boundary is stated.
- [x] The data model states the invariants.
- [x] Migration and backward compatibility are stated.
- [x] Every requirement in scope is traced.
- [x] No unresolved contract questions.

**Status:** Draft
