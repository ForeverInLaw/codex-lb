# frontend-architecture Specification (Delta)

## MODIFIED Requirements

### Requirement: Accounts page

The Accounts page SHALL keep the existing account import entry point and SHALL allow the import dialog to upload either one single `auth.json` file or one or more supported batch JSON files.

#### Scenario: Account import supports batch JSON

- **WHEN** a user opens the account import dialog and uploads one or more supported batch JSON files
- **THEN** the app calls the dashboard batch import API through a TanStack Query mutation
- **AND** the accounts list and related dashboard queries are invalidated on success
- **AND** the dialog shows a concise summary of imported, skipped, and failed entries

#### Scenario: Batch import errors remain visible

- **WHEN** the batch import API rejects the uploaded file
- **THEN** the import dialog remains open
- **AND** the error message is visible without clearing the selected file
