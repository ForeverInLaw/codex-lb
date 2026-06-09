# account-auth-import Specification (Delta)

## ADDED Requirements

### Requirement: Dashboard batch account JSON import

The dashboard accounts API SHALL accept one or more uploaded JSON files where each file may contain one account or multiple account credentials. It SHALL import every supported valid new entry using the same persistence, encryption, identity reconciliation, and cache invalidation behavior as the existing single `auth.json` import path.

#### Scenario: Import export-envelope accounts array

- **GIVEN** a JSON file with an `accounts` array whose entries contain `name`, `type: "oauth"`, and `credentials.access_token`, `credentials.refresh_token`, and optional `credentials.chatgpt_account_id`, `credentials.expires_at`, and `credentials.plan_type`
- **WHEN** the dashboard posts the file to the batch import endpoint
- **THEN** each valid account entry is imported
- **AND** the response includes a success result for each imported entry

#### Scenario: Import a single flat Codex token object

- **GIVEN** a JSON file containing one object with `type: "codex"`, `email`, `access_token`, `refresh_token`, optional `id_token`, `account_id`, `expired`, and `saved_at`
- **WHEN** the dashboard posts the file to the batch import endpoint
- **THEN** the object is imported as one account
- **AND** the response includes one success result

#### Scenario: Import an array of flat Codex token objects

- **GIVEN** a JSON file containing an array of objects with `type: "codex"`, `email`, `id_token`, `access_token`, `refresh_token`, optional `account_id`, `last_refresh`, and `expired`
- **WHEN** the dashboard posts the file to the batch import endpoint
- **THEN** every valid object is imported as an account
- **AND** the response includes one success result per imported object

#### Scenario: Import multiple files in one request

- **GIVEN** a multipart request contains several `accounts_json` files
- **AND** some files contain one account while other files contain multiple accounts
- **WHEN** the dashboard posts the request to the batch import endpoint
- **THEN** the API processes every supported account entry across every file
- **AND** each result includes the source filename and entry index from that file

#### Scenario: Import multiple existing auth.json files

- **GIVEN** a multipart request contains several current-format account `auth.json` files
- **WHEN** the dashboard posts the request to the batch import endpoint
- **THEN** each file is processed as one account entry
- **AND** the response includes one result per file

#### Scenario: Existing accounts are skipped without overwrite

- **GIVEN** an uploaded account entry resolves to an account identity that already exists
- **WHEN** the dashboard posts the file to the batch import endpoint
- **THEN** the existing account is not overwritten
- **AND** the entry is reported as `skipped`
- **AND** repeating the same batch import does not create duplicate accounts

#### Scenario: Import does not refresh usage inline

- **WHEN** the dashboard imports accounts through either the single or batch import endpoint
- **THEN** the import request stores new accounts without calling upstream usage refresh inline
- **AND** imported accounts remain visible until a later background refresh, probe, or proxy request changes their status

#### Scenario: Batch import reports per-entry failures

- **GIVEN** a batch JSON file contains at least one valid account and at least one invalid account entry
- **WHEN** the dashboard posts the file to the batch import endpoint
- **THEN** valid entries are imported
- **AND** invalid entries are reported with their input index and an error message
- **AND** existing entries are reported as skipped
- **AND** raw access, refresh, and id tokens are not returned in the response

#### Scenario: Unsupported batch shape is rejected

- **GIVEN** a JSON file is valid JSON but does not match any supported batch import shape
- **WHEN** the dashboard posts the file to the batch import endpoint
- **THEN** the API returns `400` with error code `invalid_auth_json`
