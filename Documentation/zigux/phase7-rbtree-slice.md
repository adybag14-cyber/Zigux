# Phase 7 Rbtree Slice

This document tracks the bounded Phase 7 runtime leaf-helper slice for Zigux around `lib/rbtree.c`.

## Status

- `PHASE7_STATUS=active`
- `PHASE7_SLICE=rbtree-runtime-leaf`
- scope: first bounded balancing and traversal helpers
- product boundary:
  - `lib/rbtree.zig`
  - `zigux/tests/phase7_rbtree.zig`
  - `zigux/tests/phase7_build.zig`

## Why this slice exists

Phase 7 explicitly calls out `lib/rbtree.c` as one of the first reusable in-kernel leaf libraries that should move into the Zigux product path.

This slice stays intentionally narrow and ports the first practical runtime-safe red-black tree surface:

- root and node initialization
- empty-node and empty-root state helpers
- explicit node linking
- balancing and ordered insertion helpers
- ordered erase plus direct node replacement
- in-order and postorder traversal helpers

## Gates

1. run the focused Zig module tests
- `zig test lib/rbtree.zig`

2. run the shared Phase 7 helper gate
- `zig build test --build-file zigux/tests/phase7_build.zig`

## Current parity surface

The current starter slice covers:

- `RB_EMPTY_ROOT()`
- `RB_EMPTY_NODE()`
- `RB_CLEAR_NODE()`
- `rb_link_node()`
- `rb_insert_color()` via `insertColor()`
- `rb_add()` via `add()`
- `rb_erase()` via `erase()`
- `rb_first()`
- `rb_last()`
- `rb_next()`
- `rb_prev()`
- `rb_replace_node()`
- `rb_first_postorder()`
- `rb_next_postorder()`

The current tests check:

- ordered inserts and sorted forward traversal
- reverse traversal via `last()` and `prev()`
- erase-and-replace consistency after structural updates
- postorder walking on a minimally balanced tree
- detached-node clearing semantics

## Non-goals

This slice does not yet claim:

- cached-tree helpers
- augmented-rbtree support
- lockless-iteration or memory-ordering guarantees beyond the local helper semantics
- generated C fixture parity artifacts

## Next bounded step

Either add a tiny serialized fixture or harness layer that cross-checks this ordered insert/erase surface against `lib/rbtree.c`, or close the lane now that the runtime-family starter helper includes balancing, updates, and dedicated review coverage.
