# Phase 7 Rbtree Slice

This document tracks the bounded Phase 7 runtime leaf-helper slice for Zigux around `lib/rbtree.c`.

## Status

- `PHASE7_STATUS=active`
- `PHASE7_SLICE=rbtree-runtime-leaf`
- scope: starter intrusive tree helpers including balancing and traversal
- product boundary:
  - `lib/rbtree.zig`
  - `zigux/tests/phase7_rbtree.zig`
  - `zigux/tests/phase7_build.zig`

## Why this slice exists

Phase 7 explicitly calls out `lib/rbtree.c` as one of the first reusable in-kernel leaf libraries that should move into the Zigux product path.

This starter slice now covers a small but usable intrusive tree surface:

- root and node initialization
- empty-node and empty-root state helpers
- explicit node linking and ordered insertion
- recoloring and erase balancing
- in-order and postorder traversal helpers
- direct node replacement for already-linked trees

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
- `rb_insert_color()` through `insertColor()`
- ordered insertion through `add()`
- `rb_erase()` through `erase()`
- `rb_first()`
- `rb_last()`
- `rb_next()`
- `rb_prev()`
- `rb_replace_node()`
- `rb_first_postorder()`
- `rb_next_postorder()`

The current tests check:

- manual tree linking and ordered traversal
- predecessor and successor behavior around interior nodes
- fast node replacement without rebuilding the tree
- postorder walking on a linked tree
- ordered insertion and erase stability through the balancing helpers
- detached-node clearing semantics

## Non-goals

This slice does not yet claim:

- cached-tree helpers
- augmented-rbtree support
- lockless-iteration or memory-ordering guarantees beyond the local helper semantics

## Next bounded step

Add a small deterministic C-vs-Zig parity fixture layer for insert, erase, and traversal expectations derived from `lib/rbtree.c`, or close this lane if the starter balancing surface is already sufficient for current Phase 7 review.
