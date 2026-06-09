# Optimize Dashboard Large Account Lists

## Summary

Prevent dashboard and adjacent account-selection surfaces from hanging when an installation has thousands of accounts.

## Motivation

The current frontend can render every account as dashboard cards, account-list rows, donut chart sectors, Radix menu items, and select options in a single React pass. Thousands of accounts make those surfaces CPU-heavy and can freeze the browser even when the visible viewport is small.

## Scope

- Bound initial account rendering on dashboard overview, accounts management, request/report filters, API-key assignment, and single-account routing controls.
- Preserve existing data fetching through TanStack Query hooks and existing local UI state through component state/Zustand selectors.
- Preserve account search, selection, and selected stale values while limiting unselected DOM nodes.

## Non-Goals

- Add a new virtualization dependency.
- Change backend account response contracts.
- Change account sorting semantics or routing behavior.
