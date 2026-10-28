@FR-028 @P1 @project-report
Feature: Project report
  A report written in the repository is read by the scan, stored in the index, and served over MCP.

  @FR-028-S1
  Scenario: The template needs no index
    Given no index exists
    When an agent requests the report template
    Then it receives the path, the sections, the limits, and the rules for the writer

  @FR-028-S2
  Scenario: A report is stored by section
    Given a checkout with a valid project report
    When Vyasa scans it
    Then each known section is stored with the checkout, the content hash, and the scan time

  @FR-028-S3
  Scenario: Unknown headings are reported
    Given a report with a heading that is not in the template
    When Vyasa scans it
    Then that section is dropped and the heading is reported with a reason

  @FR-028-S4
  Scenario: An oversized report is not read
    Given a report larger than the file limit
    When Vyasa scans it
    Then the report status is invalid with a size reason and the scan continues

  @FR-028-S5
  Scenario: A missing report is ordinary
    Given a checkout without a report
    When Vyasa scans it
    Then the report status is not_present and nothing is reported as an error

  @FR-028-S6
  Scenario: A link is not followed
    Given a report path that is a symbolic link
    When Vyasa scans it
    Then the report status is unreadable and the link target is not read

  @FR-028-S7
  Scenario: The report is served from the index
    Given a stored report
    When an agent requests it by project and section
    Then it receives that section marked as declared, with its source and time, and no local path

  @FR-028-S8
  Scenario: Project details show status only
    Given a stored report
    When an agent requests the project details
    Then the report status lists the sections and sizes and holds no section text

  @FR-028-S9
  Scenario: A failed read keeps earlier data
    Given a stored report and a later scan where the file is unreadable
    When Vyasa scans it
    Then the other stored data is unchanged and the report status shows the failure

  @FR-028-S10
  Scenario: Vyasa writes nothing
    Given any scan or tool call
    When it finishes
    Then no file in the repository has changed
