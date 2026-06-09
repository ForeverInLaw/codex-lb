## Architecture

Batch import stays inside the existing `accounts` module. A small normalizer converts supported JSON shapes into the current `AuthFile` contract plus explicit fallback metadata used by `AccountsService.import_account`. The service reuses a private import helper so single and batch imports share account construction, encryption, usage refresh, and cache invalidation behavior. Batch import performs an existence check before save and skips matching account identities instead of overwriting them.

## Data Flow

`POST /api/accounts/import/batch` accepts one or more multipart `accounts_json` files. The API reads every file and calls `AccountsService.import_accounts_batch`. The normalizer decodes each JSON file and emits typed batch entries with a filename, input index, `AuthFile`, and fallback metadata. The service imports entries sequentially and returns a summary with per-entry imported, skipped, and failed results.

Supported input shapes:

- envelope object with `accounts[]` and per-account `credentials`
- one flat Codex token object
- array of flat Codex token objects

For formats that do not carry a usable `id_token`, fallback metadata supplies email, account id, and plan type. The normalizer never logs or returns raw tokens.

## Error Handling

Invalid JSON or unsupported top-level shapes raise `InvalidAuthJsonError` and produce `400 invalid_auth_json` when no supported entries can be extracted from the upload. Entry-level validation failures are reported in the batch response so valid entries can still import. Duplicate existing identities are reported as skipped, not failed. Duplicate identity conflicts that cannot be resolved safely remain per-entry failures.

## Frontend

The existing import dialog remains the only Accounts-page import surface. It offers the single-file import path for current `auth.json` files and a batch path that accepts multiple JSON files. Both are TanStack Query mutations; the dialog keeps selected-file state and the last batch summary local.

## Tests

Backend integration tests cover all three requested shapes, multiple files, idempotent skip behavior, unsupported JSON, and partial failure. Frontend tests cover the API schema, hook mutation invalidation/toasts, and dialog mode behavior.
