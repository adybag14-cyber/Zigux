# Phase 1 rbtree Survey

Date: 2026-05-28
Lane: `P1-L19`
Scope: `tools/lib/rbtree.zig`

## Why this note exists

The Phase 1 roadmap names `tools/lib/rbtree.c` as one of the initial host-side helper ports, and the bootstrap ledger expects that tranche to land with shared parity coverage under the Phase 1 helper harness. This note records the current repo state for the `rbtree` slice and identifies the smallest remaining gap worth pursuing in this lane.

## Current repo state

`tools/lib/rbtree.zig` is already present in-tree and is substantive rather than scaffold-only.

Observed coverage in the live repo:
- core node, root, and cached-root types
- insert, erase, replace, traversal, postorder, duplicate-match, and cached-leftmost helpers
- Linux-style alias entry points such as `rb_add`, `rb_find_add`, `rb_first_postorder`, `rb_add_cached`, and related cached-root helpers
- direct unit tests inside `tools/lib/rbtree.zig`
- shared Phase 1 fixture replay coverage through `zigux/tests/phase1_helpers.zig` and `zigux/tests/fixtures/phase1_helpers.json`

## Roadmap comparison

The roadmap requirement for Phase 1 is to prove that Zig can live in-tree on low-risk host-side helper code with clear ownership and golden-output parity tests.

For `rbtree`, the current repo already satisfies most of that target:
- the helper exists beside the host-side `tools/lib` surface the roadmap calls for
- the port is not a stub
- the shared Phase 1 fixture harness already replays `rbtree` behavior alongside the other Phase 1 helpers

The remaining gap is narrower than implementation coverage. The repo does not yet show a dedicated `rbtree`-only validation anchor comparable to some later direct-anchor slices, so the next useful work in this lane is validation tightening rather than more API growth.

## Ledger comparison

The bootstrap ledger places `tools/lib/rbtree.zig` in the initial Phase 1 helper batch and then routes validation through the shared Phase 1 helper harness, parity fixtures, and closure gates.

The current repo matches that commit-train intent:
- the helper is landed
- the shared test harness imports it
- the committed Phase 1 fixture includes a `rbtree` section

That means the lane is no longer blocked on basic delivery. The gap is now tranche-hardening work inside the same slice.

## Next bounded step

Recommended next step for `P1-L19`:

Add a narrow `rbtree` validation hardening step, preferably one of:
- a dedicated direct-anchor test entry for `tools/lib/rbtree.zig` in `zigux/tests/build.zig`
- or an invariant-oriented test extension that exercises mixed insert and erase sequences and checks tree-structure expectations more directly than the current example-style coverage

## Conclusion

This lane should stay focused on `rbtree` validation quality. The repo evidence does not justify more helper-surface expansion here right now; the higher-value move is to make the existing `rbtree` slice easier to validate and re-run in isolation.
