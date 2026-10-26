# Diagrams: Remote Repository Discovery and Inspection

C4 vocabulary: `knowledge/architecture/c4-system-views.md`.

## Which external systems are involved? (context view)

```mermaid
C4Context
  title Remote discovery boundary
  Person(dev, "Developer", "Configures scopes and credentials")
  System(vyasa, "Vyasa", "Provider adapters, detectors, index")
  System_Ext(gh, "GitHub API", "Repositories and files")
  System_Ext(bb, "Bitbucket Cloud API", "Repositories and files")
  System_Ext(keyring, "OS credential store", "Provider tokens")
  Rel(dev, vyasa, "Configures scopes; runs discovery")
  Rel(vyasa, keyring, "Reads tokens")
  Rel(vyasa, gh, "GET repositories and selected files")
  Rel(vyasa, bb, "GET repositories and selected files")
```

## What happens during discovery, including failure? (dynamic view)

```mermaid
sequenceDiagram
  autonumber
  actor Dev as Developer
  participant Run as Discovery run
  participant Ad as Provider adapter
  participant Api as Provider API
  participant Db as Project index
  Dev->>Run: discover scope
  Run->>Ad: list_repositories(scope)
  loop each page
    Ad->>Api: GET page
    alt 429 or provider limit
      Api-->>Ad: rate limited
      Ad-->>Ad: wait per headers (max 3 retries)
    else auth failure
      Api-->>Ad: 401 or 403
      Ad-->>Run: AuthFailure
    else success
      Api-->>Ad: repositories and next link
    end
  end
  Run->>Db: save results and mark scope complete or incomplete
  opt inspection enabled
    Run->>Ad: get_file(repo, path, pinned revision)
    Ad->>Api: GET file
    Run->>Db: save observations with evidence
  end
  Run-->>Dev: coverage, counts, failures
```
