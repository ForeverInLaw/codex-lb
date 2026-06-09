## Why

Operators often receive accounts as batch JSON exports rather than one
`auth.json` file per account. Importing thousands of accounts one file at a
time is slow, error-prone, and blocks using the dashboard as the control
surface for large pools.

## What Changes

- Add a dashboard batch import endpoint for uploading one or more JSON files;
  each file may contain one account or multiple account credentials.
- Accept three input shapes:
  - an export envelope with an `accounts` array and per-account `credentials`
  - a single flat Codex token object
  - an array of flat Codex token objects
- Normalize supported shapes into the existing account import path so account
  identity, encryption, and cache invalidation stay consistent with the current
  single-file import.
- Make batch import idempotent: existing account identities are reported as
  skipped and are not overwritten.
- Preserve workspace/organization identity from supported token claims so
  accounts sharing a ChatGPT account id but belonging to different
  organizations are imported as distinct account slots.
- Extend the Accounts import dialog to upload either a single `auth.json` or a
  batch JSON file and show the import summary after success.

## Capabilities

### Modified Capabilities

- `frontend-architecture`: Accounts page import dialog supports single and
  batch JSON import from the same dashboard entry point.
- `account-auth-import`: Dashboard account import accepts supported batch JSON
  formats and returns per-entry results.

## Impact

- **Backend**: account import schemas, parser/normalizer, service method, and
  dashboard API endpoint under `app/modules/accounts`.
- **Frontend**: account API schema/function, TanStack mutation, and import
  dialog wiring.
- **Tests**: integration tests for all three batch formats and partial
  failures; frontend tests for schema/hook/dialog behavior.
