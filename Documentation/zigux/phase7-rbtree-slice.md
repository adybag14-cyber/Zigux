# Phase 7 Rbtree Slice

This document records the bounded Phase 7 runtime leaf-helper slice for Zigux around `lib/rbtree.c`.

## Status

- `PHASE7_STATUS=parked`
- `PHASE7_SLICE=rbtree-runtime-leaf`
- scope: first bounded balancing and traversal helpers
- product boundary:
  - `lib/rbtree.zig`
  - `zigux/tests/phase7_rbtree.zig`
  - `zigux/tests/phase7_rbtree_survey.zig`
  - `zigux/tests/phase7_rbtree_manifest.json`
  - `zigux/tests/phase7_build.zig`
  - `zigux/tests/fixtures/phase7_rbtree.json`
  - `zigux/tests/fixtures/phase7_rbtree_c_harness.c`

## Why this slice exists

Phase 7 explicitly calls out `lib/rbtree.c` as one of the first reusable in-kernel leaf libraries that should move into the Zigux product path.

This current slice keeps the work bounded to runtime-safe leaf helpers with explicit integration with validation substrate through `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-build-inventory.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, `zigux/tests/phase7_build.zig`, and `scripts/zigux/check-phase7-rbtree-parity.py`.

This slice stays intentionally narrow and ports the first practical runtime-safe red-black tree surface:

- root and node initialization
- empty-node and empty-root state helpers
- explicit node linking
- balancing and ordered insertion helpers
- comparison-based plain-tree lookup helpers
- plain-tree find-or-insert helper
- ordered erase plus direct node replacement
- erase-and-detach ownership reset for reusable nodes
- in-order and postorder traversal helpers

## Gates

1. prove the shared Phase 7 validator packet plus the build-inventory and make-wrapper gates still fail closed before the helper replay runs
- `python3 scripts/zigux/validate-phase7.py --self-test`
- `python3 scripts/zigux/validate-phase7.py`
- `python3 scripts/zigux/check-phase7-build-inventory.py --self-test`
- `python3 scripts/zigux/check-phase7-build-inventory.py`
- `python3 scripts/zigux/check-phase7-make-wrapper.py --self-test`
- `python3 scripts/zigux/check-phase7-make-wrapper.py`
- `make -C zigux phase7-validate`

2. run the focused Zig module tests
- `zig test lib/rbtree.zig`

3. run the shared Phase 7 helper gate
- `zig build test --build-file zigux/tests/phase7_build.zig --summary all`

4. keep the survey record machine-checked
- `zig test zigux/tests/phase7_rbtree_survey.zig`

5. check the committed C parity fixture
- `python3 scripts/zigux/check-phase7-rbtree-parity.py`

This lane is parked after the bounded helper surface compiled cleanly, the shared Phase 7 validator packet plus the build-inventory and make-wrapper self-tests now remain the published fail-closed handoff before helper replay, the focused module tests passed, the shared Phase 7 helper gate continued to import and exercise the live `rbtree` slice, the survey record captures the fully landed parity surface, and the committed parity fixture now locks ordered insert, standalone erase traversal, erase-plus-replace traversal, duplicate-range lookup, reverse traversal, and postorder behavior against the C helper surface.

The shared build-inventory gate stays in that same review packet, so the committed `zigux/tests/fixtures/phase7_build_inventory.json` snapshot and the published `make -C zigux phase7-validate` wrapper path remain explicit instead of living only in the broader shared Phase 7 notes.

## Current parity surface

The current starter slice covers:

- `RB_EMPTY_ROOT()`
- `RB_EMPTY_NODE()`
- `RB_CLEAR_NODE()`
- `rb_link_node()`
- `rb_insert_color()` via `insertColor()`
- `rb_add()` via `add()`
- `rb_find()` via `find()`
- `rb_find_first()` via `findFirst()`
- `rb_next_match()` via `nextMatch()`
- duplicate-range iterator helper via `iterateMatches()`
- `rb_find_add()` via `findAdd()`
- `rb_erase()` via `erase()`
- `rb_erase_init()`-style detached-node reset via `eraseInit()`
- `rb_first()`
- `rb_last()`
- `rb_next()`
- `rb_prev()`
- `rb_replace_node()`
- `rb_first_postorder()`
- `rb_next_postorder()`

The current tests check:

- committed C-vs-Zig parity for ordered insert, standalone erase traversal, erase-plus-replace traversal, reverse traversal, duplicate-range lookup order, and postorder traversal
- ordered inserts and sorted forward traversal
- reverse traversal via `last()` and `prev()`
- duplicate-key lookup ranges via `findFirst()`, `nextMatch()`, and `iterateMatches()`
- duplicate-aware find-or-insert behavior via `findAdd()`
- erase-and-replace consistency after structural updates
- detached-node ownership discipline after `erase()` and `replaceNode()`, where callers must still run `clearNode()` before `emptyNode()` becomes true
- erase-and-detach reuse semantics via `eraseInit()`
- postorder walking on a minimally balanced tree
- detached-node clearing semantics
- a machine-checked manifest that records the `lib/rbtree.c` anchor and the landed Phase 7 review surfaces

## Non-goals

This slice still does not claim:

- cached-tree helpers
- augmented-rbtree support
- lockless-iteration or memory-ordering guarantees beyond the local helper semantics

## Next bounded step

Leave this lane parked unless fresh repo inspection finds a concrete need for one tiny additional C-vs-Zig parity shape over the existing insert, find-or-insert, duplicate-key lookup, erase, replace, reverse traversal, or postorder surface.
