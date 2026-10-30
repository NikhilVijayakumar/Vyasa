## ADDED Requirements

### Requirement: List supported technology filters
The CLI SHALL report the technology registry version and supported technology keys, names, categories and ecosystems without opening or creating the index.

#### Scenario: Read catalog before a first scan
- **WHEN** the catalog is requested before an index exists
- **THEN** the registered technologies are returned and no index is created

#### Scenario: Use a catalog entry
- **WHEN** a returned key is used as a technology search filter
- **THEN** the existing indexed search semantics apply
