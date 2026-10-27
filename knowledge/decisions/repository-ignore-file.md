---
type: Decision
title: "Repository-Provided Ignore File"
description: A repository may list directories Vyasa must not scan inside it, in a plain .vyasaignore file that can only narrow scanning and never reach outside the repository.
tags: [adr, discovery, ignore, trust]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-27T21:00:00Z }
sources:
  - id: disc
    resource: /architecture/scanning-and-evidence/discovery-and-inspection.md
    title: Workspace Discovery and Repository Inspection
  - id: untrusted
    resource: /concepts/untrusted-content.md
    title: Untrusted Content
---

# Status

Proposed (draft). It becomes stable when reviewed and accepted.

# Context

Vyasa cannot know which directories inside a repository are irrelevant: reference material for coding agents, generated data, large fixtures. On one real workspace, 868 directories below the depth limit were skipped, almost all of them such data folders inside projects. The repository's owner knows what to skip. A repository is also untrusted content, so whatever it provides must not be able to widen what Vyasa reads.

# Decision

A repository may contain a file named `.vyasaignore` at its root. It is plain UTF-8 text, at most 64 KiB and 1,000 patterns, read once per repository.

Each non-blank line that does not start with `#` is a pattern for a directory:

- A pattern without a slash matches a directory of that name at any depth below the repository root.
- A pattern with a slash, or with a leading slash, matches a path relative to the repository root; a leading slash means the root, not the file system.
- `*` matches within one path segment, `**` across segments, and `?` one character. Matching ignores case. A trailing slash is allowed and changes nothing.
- Backslashes are read as slashes.

Patterns can only remove directories from scanning. Negation (`!`), drive letters, and `..` segments are invalid. An invalid line is reported in a warning and skipped, and the valid lines still apply; a file that is too large is skipped as a whole and reported. Skipping a line makes Vyasa scan more, never less than the repository asked.

The patterns apply only to directories below the repository that holds the file. A nested repository has its own file, and the files of every enclosing repository still apply to it. An ignored directory is not entered, is counted as excluded, and is not reported as a skip. Evidence records that a file was used, how many patterns it held, and a digest of them, not the text.

# Alternatives considered

- **Honor `.gitignore`.** Already present in most repositories, but its rules (negation, anchoring, nested files) are complex, and Git-ignored nested repositories would disappear from discovery.
- **A central ignore list in Vyasa's configuration.** Keeps repositories untouched, but the person who knows what to skip is the repository's owner, and a central list drifts as projects change.
- **Ignore nothing and report skips.** Honest, but leaves hundreds of warnings the person cannot resolve.

# Consequences

- A repository's owner can silence its own noise with one file.
- The file is repository content: its size, pattern count, and reach are bounded, and it can never add paths or point outside its repository.
- Files and glob classes beyond `*`, `**`, and `?` are not supported yet.
- A malicious file can hide its own repository's directories from Vyasa but nothing else.

# Related

- [Workspace Discovery and Repository Inspection](/architecture/scanning-and-evidence/discovery-and-inspection.md)
- [Untrusted Content](/concepts/untrusted-content.md)
- [Repository Recognition and Discovery Run Status](/decisions/repository-recognition-and-run-status.md)
- [File Composition Data and Limits](/decisions/file-composition-data-and-limits.md)
