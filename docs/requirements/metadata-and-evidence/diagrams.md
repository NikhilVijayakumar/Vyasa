# Diagrams: Metadata Extraction and Evidence

C4 vocabulary: `knowledge/architecture/c4-system-views.md`. This view zooms into the one place where facts are
made, so the rule 'no value without evidence' can be seen as a data flow.

## How does a file become a fact with evidence? (component view)

```mermaid
flowchart LR
  subgraph Repo["Repository (untrusted, read-only)"]
    F[Recognized files]
  end
  subgraph Server["Vyasa scanner"]
    INV[Repository Inspector<br/>bounded inventory and reader]
    REG[Detector Registry<br/>versioned detectors]
    NORM[Normalizer and Ownership Policy<br/>precedence, conflicts, statuses]
  end
  DB[(Project index)]
  F -->|bounded reads| INV
  INV -->|inventory and file bytes| REG
  REG -->|observations: value, status, evidence| NORM
  NORM -->|resolved values, previous values, conflicts| DB
  REG -. exception .-> ERR[Item error; other detectors continue]
```

Every arrow into the index carries a status and an evidence record; there is no path that stores a value
without them.
