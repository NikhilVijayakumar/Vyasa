# Specifications: be-project-report (profile-context)

## 1. Specification Overview

- **OpenSpec Change ID:** `be-project-report`
- **Purpose:** Point the context workflow at the report.
- **Related proposal:** `proposal.md`

## 2. Capability: profile-context

### Purpose

An agent that reads the context learns that a report exists to write.

## ADDED Requirements

### Requirement: The workflow names the report

The system SHALL add to the context workflow a step that tells the agent to fetch `get_report_template`, to write `.vyasa/project-report.md` from the observed facts and its own inspection, and to ask the user to run a scan afterwards, and SHALL state the report status of each checkout in the bundle.

#### Scenario: Step present

- **GIVEN** a context bundle
- **WHEN** the workflow is read
- **THEN** it names `get_report_template`, the report path, and the rescan

#### Scenario: Status per checkout

- **GIVEN** a context bundle for a project with one checkout that has a report
- **WHEN** it is read
- **THEN** the checkout shows the report status and section names, no text
