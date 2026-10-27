# Diagrams: File Composition

C4 vocabulary: `knowledge/architecture/c4-system-views.md`. The question here is how one walk produces counts, and when a count may be trusted.

## How does one walk become counts and an indicator? (flow)

```mermaid
flowchart TD
  A[Checkout inside a configured root] --> B[Bounded walk: no symlink follow, exclusions applied]
  B --> C{Bound reached or directory unreadable?}
  C -- no --> D[complete]
  C -- yes --> E[partial, limit named]
  B --> F[Classify each file by extension]
  F --> G[code / documentation / other]
  G --> H[Counts and total]
  H --> I{complete and documentation > 0 and code = 0?}
  D --> I
  E --> J[documentation_only = unknown]
  I -- yes --> K[documentation_only = true]
  I -- no, complete --> L[documentation_only = false]
```

## When may a count be trusted? (state)

```mermaid
stateDiagram-v2
  [*] --> NotCounted
  NotCounted --> Complete: walk finished
  NotCounted --> Partial: bound reached or directory unreadable
  Complete --> Stale: tree or classification data changed
  Partial --> Stale: tree or classification data changed
  Stale --> Complete: rescan finished
  Stale --> Partial: rescan hit a bound
  note right of Partial
    Counts are lower bounds.
    documentation_only is unknown.
  end note
```
