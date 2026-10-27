# Diagrams: Framework and Technology Detection

The question here is what may be believed about a manifest read from an untrusted repository.

## How does a root manifest become a technology, or stay unknown? (flow)

```mermaid
flowchart TD
  A[Supported name at the checkout root] --> B{Regular file, not a link?}
  B -- no --> U[unreadable]
  B -- yes --> C{At most 1 MiB?}
  C -- no --> T[too_large]
  C -- yes --> D{Strict UTF-8 and parses?}
  D -- no --> M[malformed with a fixed reason]
  D -- yes --> E[parsed: scoped dependencies]
  E --> F{Dependency in the registry?}
  F -- yes --> G[technology with the scopes it was declared in]
  F -- no --> H[dependency only]
```

## When may an ecosystem be called absent? (decision flow)

```mermaid
flowchart TD
  A[Ecosystem in one observation] --> B{Assessed with a registry version?}
  B -- no --> C[not_assessed]
  B -- yes --> D{Root manifest of the ecosystem seen?}
  D -- yes --> E[detected: per-manifest status]
  D -- no --> F{Walk complete?}
  F -- yes --> G[not_detected]
  F -- no --> H[unknown]
```
