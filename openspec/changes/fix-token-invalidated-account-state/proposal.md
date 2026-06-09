## Why

Compact requests can receive upstream `401` responses with
`error.code = "token_invalidated"` and the message "Your authentication token
has been invalidated. Please try signing in again." The current auth-failover
contract is implemented and specified around `invalid_api_key`, so this newer
machine code is recorded as a transient error. A Codex goal can then retry
compaction against the same bad account repeatedly, and the dashboard may still
show the account as active.

Operators also need to distinguish a credential/session that needs
re-authentication from an upstream account that has been disabled, suspended, or
deleted. Today both end up presented as deactivated in the dashboard.

## What Changes

- Treat `token_invalidated` as a permanent re-authentication-required account
  failure across the proxy failure classifier path.
- Persist a distinct `reauth_required` account status for invalidated-token and
  expired-session failures, while preserving `deactivated` for disabled,
  suspended, deleted, or explicitly deactivated upstream accounts.
- Keep `reauth_required` accounts out of account routing, normal dashboard
  account lists, account pickers, and probeable account paths until an operator
  re-authenticates them.
- Hide terminal `reauth_required` and `deactivated` accounts from the normal
  `/api/accounts` list while preserving their persisted rows and diagnostic
  dashboard overview status for audit/history.
- Add regression coverage for compact `token_invalidated` failover and
  dashboard/account status reporting.

## Capabilities

### Modified Capabilities

- `responses-api-compat`: account-local compact auth failover includes
  `token_invalidated`.
- `account-routing`: reauth-required accounts are hard-blocked from routing.
- `usage-refresh-policy`: permanent credential/session failures are marked
  re-authentication-required rather than disabled-account deactivations.
- `frontend-architecture`: normal account lists omit terminal unavailable
  accounts while diagnostic dashboard surfaces may still report their status.

## Impact

- **Code**: account status enum/migration, balancer permanent failure mapping,
  proxy auth-failure handling, dashboard account-list filtering.
- **Tests**: compact proxy integration, account-list filtering, usage/auth cache
  invalidation coverage.
