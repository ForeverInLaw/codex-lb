## 1. OpenSpec Tooling

- [x] 1.1 Add a local `openspec` project script so `uv run openspec ...` works in this repository.
- [x] 1.2 Validate existing specs with `uv run openspec validate --specs`.

## 2. Backend

- [x] 2.1 Add typed batch import schemas for summary, successes, and per-entry failures.
- [x] 2.2 Add a focused batch JSON normalizer for the three supported input shapes across one or more files.
- [x] 2.3 Refactor account import service internals so single and batch imports share account creation.
- [x] 2.4 Add idempotent existing-account detection so batch imports skip instead of overwrite.
- [x] 2.5 Add `POST /api/accounts/import/batch` with dashboard auth, audit events, and no token echoing.

## 3. Frontend

- [x] 3.1 Add batch import response schema and API function.
- [x] 3.2 Add a TanStack Query batch import mutation with account/dashboard invalidation.
- [x] 3.3 Extend the import dialog to choose single or batch JSON import, accept multiple batch files, and show batch summary.
- [x] 3.4 Wire the Accounts page to the batch import mutation and busy/error states.

## 4. Tests

- [x] 4.1 Add backend integration tests for envelope, single flat object, array of flat objects, multiple files, idempotent skips, unsupported shape, and partial failure.
- [x] 4.2 Add frontend tests for schema/API/hook/dialog behavior.
- [x] 4.3 Run targeted backend and frontend tests plus `uv run openspec validate add-batch-account-json-import --strict`.
