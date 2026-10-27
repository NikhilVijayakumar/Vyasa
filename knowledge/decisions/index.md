# Decisions

Architecture decision records. All are drafts until reviewed and accepted; each states its alternatives and consequences.

* [Local-First SQLite Index](local-first-sqlite-index.md) - The index is one SQLite file in a per-user directory, written by one writer in per-project transactions and read through read-only connections.
* [stdio-Only MCP Transport](stdio-only-mcp-transport.md) - The MCP server speaks over standard input and output only and opens no network listener.
* [Deterministic Extraction Without a Language Model](deterministic-extraction-without-llm.md) - Stored facts are produced only by versioned deterministic detectors over recognized evidence.
* [Stored Identity With Aliases](stored-identity-with-aliases.md) - A project's identifier is created once from the strongest evidence and stored; later evidence adds aliases that resolve to it.
* [Remote Identity Normalization](remote-identity-normalization.md) - Remote URLs are reduced to host/organization/repository so equivalent forms compare equal.
* [Read-Only Repository Access and Git Policy](read-only-access-and-git-policy.md) - Scanning never changes a repository, and Git is read from files; a closed set of sanitized read-only commands is the only exception.
* [Scan Limits and Symlink Defaults](scan-limits-and-symlink-defaults.md) - Conservative, configurable limits bound every scan, and directory symlinks are not followed by default.
* [Canonical Profile and Draft Handling](canonical-profile-and-draft.md) - One YAML profile at a fixed path is the declared source; an opt-in draft is separate and excluded locally.
* [Ownership-Based Conflict Resolution](ownership-based-conflict-resolution.md) - Conflicts are decided by who owns the field, field by field, and never by newest timestamp alone.
* [Credential Storage and Registry Identity](credential-storage-and-sheets-identity.md) - Credentials live in the operating system's credential store, and the shared registry is accessed by a service account by default.
* [Partial Results Never Imply Absence](partial-results-never-imply-absence.md) - A limit, timeout, failed page, or access error means not assessed; absence is concluded only from complete, successful inspection.
* [Optional Extras for Integrations](optional-extras-for-integrations.md) - Libraries for Sheets, providers, and credential stores install as optional extras, so the core runs without them.
* [Technology Registry as Versioned Data](technology-registry-as-data.md) - A versioned data file maps dependency names to technology keys, display names, and categories.
* [Observation Freshness Without Query-Time I/O](observation-freshness-without-query-time-io.md) - Queries report observation age and index freshness; they never inspect files or refresh to decide staleness.
* [Unified Run Status Vocabulary](unified-run-status-vocabulary.md) - Scan, synchronization, and discovery runs share one status set.
* [MCP Omits Local Paths by Default](mcp-local-paths-omitted-by-default.md) - Tool results contain no absolute local paths unless the user enables them.
* [Refresh and Integration Tools Are Disabled by Default](explicit-tools-disabled-by-default.md) - The refresh tool and any later synchronization or discovery tools are not offered to agents unless configured.
* [Retention Defaults](retention-defaults.md) - Observations keep the current and previous value; run history and logs are bounded by count and age.
* [Knowledge Profile Enforces Sections and Supersession](knowledge-profile-section-rules.md) - The bundle profile requires named sections per type, bans open questions in stable concepts, and makes a deprecated decision name its replacement.
* [File Composition Data and Limits](file-composition-data-and-limits.md) - File types are versioned data shared with the language detector, and counting has its own depth and entry limits because it reads no content.
* [Configuration File Format and Location](configuration-file-format-and-location.md) - One TOML file found by explicit path, then environment variable, then the data directory; no root is ever implied, and an invalid file is rejected as a whole.
* [Repository Recognition and Discovery Run Status](repository-recognition-and-run-status.md) - A Git repository is recognized from its marker without running Git, every candidate gets one closed outcome, and a run is partial whenever anything was not fully assessed.
* [Repository-Provided Ignore File](repository-ignore-file.md) - A repository may list directories Vyasa must not scan inside it, in a plain .vyasaignore file that can only narrow scanning and never reach outside the repository.
* [Git Remote Provider Labels](git-remote-provider-labels.md) - A project's Git remote is read from the config file as text, reduced to a credential-free identity, and labelled github, bitbucket, gitlab, other, local, or none from its host.
* [Index Lifecycle States and Single Writer](index-lifecycle-and-single-writer.md) - A vanished project is marked missing or inaccessible and never deleted; one writer holds a heartbeat lock; a run left running by a dead writer becomes interrupted; freshness is current, stale, partial, or unknown.
