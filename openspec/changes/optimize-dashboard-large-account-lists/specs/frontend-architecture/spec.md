## ADDED Requirements

### Requirement: Large account dashboard surfaces use bounded rendering

Dashboard and account-selection UI surfaces MUST NOT render one DOM, SVG, or menu item per account by default when account counts are large. Surfaces that display account collections MUST render a bounded initial subset, aggregate overflow where a chart requires totals, and provide search or an explicit incremental reveal control when operators need entries beyond the initial subset.

#### Scenario: Dashboard overview renders thousands of accounts without full account DOM expansion

- **WHEN** the dashboard overview receives thousands of accounts
- **THEN** the account-card grid renders only a bounded subset initially
- **AND** usage donuts aggregate overflow account slices into a bounded "other accounts" entry while preserving remaining and consumed totals
- **AND** per-row animation delays remain bounded rather than increasing with the absolute account index

#### Scenario: Account pickers remain searchable without rendering every option

- **WHEN** an account picker or account filter has thousands of account options
- **THEN** it renders only a bounded subset of matching options
- **AND** selected values remain visible even when they are outside the bounded subset
- **AND** search or incremental reveal lets an operator reach accounts outside the initial subset

#### Scenario: Accounts page list reveals large results incrementally

- **WHEN** the Accounts page has more matching accounts than the render bound
- **THEN** the list renders the first bounded subset
- **AND** it shows how many matching accounts are currently rendered
- **AND** the operator can reveal more matching accounts without forcing the whole list to render at once
