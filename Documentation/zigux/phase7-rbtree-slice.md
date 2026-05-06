# Phase 7 Rbtree Slice

This document records the bounded Phase 7 runtime leaf-helper slice for Zigux around `lib/rbtree.c`.

## Status

- `PHASE7_STATUS=parked`
- `PHASE7_SLICE=rbtree-runtime-leaf`
- `PHASE7_LANE_KEY=P7-Y04`
- scope: first bounded balancing, traversal, and cached-leftmost helpers
- lane state: helper, fixture, dedicated survey, parity checker, shared validator, and make-wrapper slice landed; parked unless a new `lib/rbtree.c` parity issue appears
- product boundary:
  - `lib/rbtree.zig`
  - `samples/zigux/README.md`
  - `scripts/zigux/validate-phase7.py`
  - `scripts/zigux/check-phase7-rbtree-parity.py`
  - `zigux/tests/phase7_rbtree.zig`
  - `zigux/tests/phase7_rbtree_survey.zig`
  - `zigux/tests/phase7_rbtree_manifest.json`
  - `zigux/tests/phase7_build.zig`
  - `zigux/tests/fixtures/phase7_rbtree.json`
  - `zigux/tests/fixtures/phase7_rbtree_c_harness.c`
  - `zigux/Makefile`

## Why this slice exists

Phase 7 explicitly calls out `lib/rbtree.c` as one of the first reusable in-kernel leaf libraries that should move into the Zigux product path.

This slice stays intentionally narrow and ports the first practical runtime-safe red-black tree surface:

- root and node initialization
- empty-node and empty-root state helpers
- explicit node linking
- balancing and ordered insertion helpers
- cached leftmost-root helpers for O(1) first-node tracking
- comparison-based plain-tree lookup helpers
- ordered erase, erase-and-detach, and direct node replacement
- in-order and postorder traversal helpers
- shared reviewability through `zigux/tests/phase7_rbtree_survey.zig`, `scripts/zigux/check-phase7-rbtree-parity.py`, `scripts/zigux/validate-phase7.py`, `zigux/tests/phase7_build.zig`, and `make -C zigux phase7`

This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane.

Current `master` still ships no `samples/zigux/*rbtree*` Phase 5 reference sample; keep `rbtree` reviewability under this slice, `samples/zigux/README.md`, `lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, and `zigux/tests/phase7_build.zig` instead of counting it as a fifth Phase 5 sample.

## Gates

1. run the focused Zig module tests
- `zig test lib/rbtree.zig`

2. run the shared Phase 7 helper gate
- `zig build test --build-file zigux/tests/phase7_build.zig`

3. keep the survey record machine-checked
- `zig test zigux/tests/phase7_rbtree_survey.zig`

4. check the committed C parity fixture
- `python3 scripts/zigux/check-phase7-rbtree-parity.py`

5. keep the shared validator-first packet explicit
- `python3 scripts/zigux/validate-phase7.py`
- `python3 scripts/zigux/check-phase7-rbtree-parity.py`
- `make -C zigux phase7-validate`

6. keep the shared Linux-style replay route explicit
- `make -C zigux phase7`

This lane is parked after the bounded helper surface compiled cleanly, the focused module tests passed, the shared Phase 7 helper gate continued to import and exercise the live `rbtree` slice, the shared validator-first and Linux-style `make -C zigux phase7-validate` plus `make -C zigux phase7` routes stayed aligned around the same parked packet, and the committed parity fixture now locks ordered insert, duplicate-range lookup, erase-and-detach reset, replace, reverse traversal, and postorder behavior against the C helper surface. The cached leftmost helpers come from the header-side runtime surface rather than `lib/rbtree.c` itself, so they stay reviewable through the focused Zig module tests instead of the committed C parity fixture. This slice does not carry an open parity-fixture follow-up.

## Current parity surface

The current starter slice covers:

- `RB_EMPTY_ROOT()`
- `RB_EMPTY_NODE()`
- `RB_CLEAR_NODE()`
- `rb_link_node()`
- `rb_insert_color()` via `insertColor()`
- `rb_insert_color_cached()` via `insertColorCached()`
- `rb_add()` via `add()`
- `rb_add_cached()` via `addCached()`
- `rb_find()` via `find()`
- `rb_find_first()` via `findFirst()`
- `rb_next_match()` via `nextMatch()`
- `rb_erase()` via `erase()`
- `rb_erase_cached()` via `eraseCached()`
- `rb_erase_init()` via `eraseInit()`
- `rb_first_cached()` via `firstCached()`
- `rb_first()`
- `rb_last()`
- `rb_next()`
- `rb_prev()`
- `rb_replace_node()`
- `rb_replace_node_cached()` via `replaceNodeCached()`
- `rb_first_postorder()`
- `rb_next_postorder()`

The current tests check:

- committed C-vs-Zig parity for ordered insert, reverse traversal, replace, duplicate-key lookup order, erase-and-detach ownership reset, and postorder traversal
- ordered inserts and sorted forward traversal
- reverse traversal via `last()` and `prev()`
- duplicate-key lookup ranges via `findFirst()` and `nextMatch()`
- cached-leftmost tracking across `addCached()`, `replaceNodeCached()`, and `eraseCached()`
- erase-and-replace consistency after structural updates
- replacement of dirty detached nodes by copying the full victim link-and-color shape before reconnecting the new node
- erase-and-detach ownership reset via `eraseInit()`
- postorder walking on a minimally balanced tree
- terminal postorder handoff accepts null input so callers can finish walks without a separate pre-check
- detached-node clearing semantics
- a machine-checked manifest that records the `lib/rbtree.c` anchor and the landed Phase 7 review surfaces

## Non-goals

This slice still does not claim:

- augmented-rbtree support
- lockless-iteration or memory-ordering guarantees beyond the local helper semantics

## Next bounded step

Leave this lane parked unless fresh repo inspection finds a concrete need for one tiny additional C-vs-Zig parity shape over the existing insert, cached-leftmost, duplicate-key lookup, erase, erase-and-detach, replace, reverse traversal, or postorder surface.
