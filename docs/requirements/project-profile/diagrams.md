# Diagrams: Project Profile Lifecycle

C4 vocabulary: `knowledge/architecture/c4-system-views.md`. The question here is who may change what, and when.

## How does a profile move from nothing to canonical? (lifecycle)

```mermaid
stateDiagram-v2
  [*] --> NoProfile
  NoProfile --> Draft: explicit draft command (opt-in, one named file)
  Draft --> Canonical: a person edits and commits it
  NoProfile --> Canonical: a person writes one
  Canonical --> Canonical: a person edits
  Canonical --> Unsupported: schema version not supported
  Unsupported --> Canonical: a person upgrades the file
  note right of Draft
    Never promoted by Vyasa.
    Never overwritten by a scan.
  end note
  note right of Canonical
    Read by every scan.
    Never written by Vyasa.
  end note
```
