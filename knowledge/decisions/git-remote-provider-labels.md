---
type: Decision
title: "Git Remote Provider Labels"
description: A project's Git remote is read from the config file as text, reduced to a credential-free identity, and labelled github, bitbucket, gitlab, other, local, or none from its host.
tags: [adr, git, remote, identity]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-27T23:00:00Z }
sources:
  - id: det
    resource: /architecture/scanning-and-evidence/detector-inventory.md
    title: Metadata Detector Inventory
  - id: norm
    resource: /decisions/remote-identity-normalization.md
    title: Remote Identity Normalization
---

# Status

Proposed (draft). It becomes stable when reviewed and accepted.

# Context

Knowing where a project is hosted tells a person which projects share a platform and prepares remote discovery. The raw remote URL cannot be stored: it may carry a user name or token, and the same repository appears as ssh and https forms. Running Git to read it would execute repository-influenced code. Owners also use self-hosted servers and hosts Vyasa has never heard of.

# Decision

The remote is read from the project's `.git/config` as text, never by running Git and never over the network. Only a `.git` directory is read, up to 64 KiB, and never through a link. A `.git` pointer file (a linked worktree or submodule) reports the remote as unavailable. For a manifest project whose Git lives in a child folder, that folder's config is read.

Remote choice follows the identity decision: `origin`; otherwise the only remote; otherwise none is chosen and the status says ambiguous. A project with Git but no remote section reports none.

The chosen URL is normalized as in the identity decision (scheme, user information, default port, trailing `.git` and slash dropped; `git@host:org/repo` rewritten) and only the result is kept: the host, the `host/org/repo` identity, and a provider label. The original URL is never kept.

The provider comes from the host alone:

| Host | Provider |
|---|---|
| `github.com` (and `ssh.github.com`, treated as the same host) | `github` |
| `bitbucket.org` | `bitbucket` |
| `gitlab.com` | `gitlab` |
| any other host | `other`, with the host kept |
| a path or `file:` URL | `local`, with no identity |

A project with no usable remote has provider `none`. The label says where the URL points, not that the repository exists or is reachable.

# Alternatives considered

- **Ask Git (`git remote get-url`).** Authoritative, but it runs repository-influenced code paths.
- **Accept only a fixed list of providers.** Cleaner labels, but it hides self-hosted and unfamiliar hosts; `other` with the host keeps them visible.
- **Store the raw URL.** Simplest, but it persists credentials and duplicates one repository under several spellings.
- **Resolve worktree and submodule pointers to the shared config.** More complete, but it reads files outside the project from a path the repository supplies.

# Consequences

- Linked worktrees and submodules show an unavailable remote until a safe way to resolve them is agreed.
- A new well-known host is a one-line change to a table of data.
- A remote that is a local path is reported as local, not as a platform.
- The provider label is a claim about the URL only.

# Related

- [Remote Identity Normalization](/decisions/remote-identity-normalization.md)
- [Read-Only Repository Access and Git Policy](/decisions/read-only-access-and-git-policy.md)
- [Metadata Detector Inventory](/architecture/scanning-and-evidence/detector-inventory.md)
- [Untrusted Content](/concepts/untrusted-content.md)
