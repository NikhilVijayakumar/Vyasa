# Diagrams: Project Identity and Review Candidates

C4 vocabulary: `knowledge/architecture/c4-system-views.md`. The Identity Resolver is a domain component with
no I/O of its own, so one dynamic view is enough.

## How is an existing project found on rediscovery? (dynamic view)

```mermaid
flowchart TD
  A[Candidate repository] --> B[Parse origin and strip credentials]
  B --> C{Remote normalizes?}
  C -- yes --> D{Alias already known?}
  D -- yes --> P1[Same project; update path mapping]
  D -- no --> E{Known checkout path?}
  E -- yes --> P2[Same project; record remote_changed and add alias]
  E -- no --> N1[Create project once from the remote]
  C -- no --> F{Root commit readable?}
  F -- yes --> G{Root commit known?}
  G -- yes --> P3[Same project; update path mapping]
  G -- no --> N2[Create project from the root commit]
  F -- no --> H{Known checkout path?}
  H -- yes --> P4[Same project]
  H -- no --> N3[Create provisional project; flag for review]
  D -. conflicting evidence .-> U[identity_unresolved; flag for review]
  E -. conflicting evidence .-> U
```
