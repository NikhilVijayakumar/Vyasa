@DOR @P1 @data-ownership
Feature: Ownership examples
  Worked examples that show the ownership rules in concrete situations.

  @DOR-EX-A
  Scenario: README removed
    Given a project previously had a README
    And the file is removed from the current checkout
    When a scan completes successfully
    Then the local observation shows the README is not currently detected
    And the previous observation remains in scan history
    And the canonical profile is not modified
    And the shared registry changes only according to its ownership and synchronization policy

  @DOR-EX-B
  Scenario: A maintainer changes the project purpose
    Given a maintainer updates the purpose in the canonical profile
    When the project is rescanned
    Then Vyasa reads the new declared value
    And the scanner does not replace it with a guess from the directory name or technology
    And the registry receives an approved copy if the field is allowlisted

  @DOR-EX-C
  Scenario: Tracking level changed in the registry
    Given a portfolio maintainer changes a project's tracking level in the sheet
    When local scanning and synchronization run
    Then the registry remains authoritative for that field
    And local scanning does not overwrite it
    And the canonical project profile is not modified

  @DOR-EX-D
  Scenario: Local and remote README differ
    Given a local checkout has a modified README
    And the remote repository has a different committed README
    When both are observed
    Then the two observations remain distinguishable
    And Vyasa does not claim the two versions are identical
    And no repository content is modified

  @DOR-EX-E
  Scenario: Project not accessible on a new device
    Given a project exists in the registry but is not cloned on this device
    When its details are requested
    Then Vyasa returns the shared metadata
    And local source availability is reported as unavailable on this device
    And no path from another device is shown
    And no local clone is created
