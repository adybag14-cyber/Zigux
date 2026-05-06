# Phase 3 Shared Rbtree Root Contract

This note keeps one small Phase 3 reviewability guard close to the existing shared ABI packet.

## Scope

- shared source: `zigux/tests/phase3_abi.zig`
- contract focus: `abi.RbtreeRootView` validity and canonicalization rules
- bounded invalid records:
  - `rootless-uncached`
  - `cached-without-leftmost-addr`
  - `cached-without-leftmost-flag`
  - `leftmost-without-cached-flag`

## Guard

- `python3 scripts/zigux/check-phase3-shared-rbtree-root-contract.py`

## Why it exists

Recent Phase 3 work tightened the shared rbtree root-view contract inside `zigux/tests/phase3_abi.zig`, but the current repo surface does not visibly carry the dedicated rbtree packet paths described in earlier continuity notes. This narrow checker keeps the shared contract reviewable without reopening char-device growth or inventing a new wrapper family.
