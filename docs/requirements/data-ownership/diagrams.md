# Diagrams: Data Ownership and Source of Truth

C4 vocabulary: `knowledge/architecture/c4-system-views.md`. The question here is who owns each kind of value and
which way it may flow.

## Who owns what, and what may cross? (data-flow view)

```mermaid
flowchart LR
  subgraph Repo["Repository (project-owned)"]
    PF[Canonical profile<br/>declared values]
    MF[Manifests and files<br/>observed facts]
  end
  subgraph Local["This device (machine-local)"]
    IDX[(Vyasa index<br/>generated and derived)]
    LP[Paths, roots, config<br/>never exported to Sheets]
  end
  subgraph Shared["Google Sheets (shared)"]
    SUM[Approved summaries]
    PORT[Portfolio fields<br/>tracking, priority, notes]
  end
  PROV[Provider APIs<br/>provider-owned metadata]
  PF -->|read-only| IDX
  MF -->|read-only| IDX
  PROV -->|read-only| IDX
  IDX -->|allowlist only| SUM
  PORT -->|imported, authoritative| IDX
```

Arrows show the only permitted directions. A scan never writes the repository or the portfolio fields; a sync
never writes declared values or local data.
