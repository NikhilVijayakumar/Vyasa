# Concepts

* [Project Identity](project-identity.md) - A project is identified by stable evidence, never by its name or path; ambiguity is preserved, not guessed away.
* [Field Ownership](field-ownership.md) - Every mutable field has one authoritative owner; other processes read or cache it but never overwrite it silently.
* [Evidence and Provenance](evidence-and-provenance.md) - Every value Vyasa reports carries the evidence it was derived from and an explicit observation status.
* [Deterministic Extraction](deterministic-extraction.md) - Every extracted fact comes from a recognized source by a documented rule, so the same input always gives the same output.
* [Freshness and Staleness](freshness-and-staleness.md) - Observation status, index freshness, and evidence age are three different signals; none requires checking files at query time.
* [Untrusted Content](untrusted-content.md) - Anything read from a repository, provider, or spreadsheet is data to be bounded and sanitized, never instructions or code.
* [Explicit Operations](explicit-operations.md) - Queries only read the index; anything that scans, writes, or contacts another system is a separate operation the user chose.
* [Local-First Operation](local-first.md) - The core works entirely on the local machine and offline; integrations extend it without becoming required.
* [Glossary](glossary.md) - Definitions of the terms Vyasa documents use, in one place.

* [Workspace Names](workspace-names.md) - Human-managed local display names for configured workspace roots.
