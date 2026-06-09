## MODIFIED Requirements

### Requirement: Accounts page

The Accounts page SHALL display a two-column layout: left panel with searchable
account list, import button, and add account button; right panel with selected
account details including usage, token info, and actions
(pause/resume/delete/re-authenticate). The normal `GET /api/accounts` response
SHALL omit terminal unavailable accounts with status `reauth_required` or
`deactivated`, while preserving their persisted rows and allowing diagnostic
dashboard surfaces to continue reporting their status. The browser OAuth stage
SHALL show an authorization URL with a copy action that remains functional in
secure and non-secure contexts.

The Accounts page SHALL also allow exporting a selected account as an
OpenCode-compatible `auth.json` payload with explicit raw-token warnings.

#### Scenario: Terminal account is removed from the normal account list

- **WHEN** an account is persisted as `reauth_required` after an upstream
  credential/session failure
- **THEN** `GET /api/accounts` does not include that account
- **AND** the account row is not physically deleted
- **AND** diagnostic dashboard overview responses may still include the account
  with `status = "reauth_required"`

#### Scenario: Deactivated account is removed from the normal account list

- **WHEN** an account is persisted as `deactivated` after a clear upstream
  deactivation signal such as usage HTTP `402`
- **THEN** `GET /api/accounts` does not include that account
- **AND** the account row is not physically deleted
