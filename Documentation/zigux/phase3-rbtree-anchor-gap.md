# Phase 3 Rbtree Anchor Gap

This note records the current bounded `lib/rbtree.c` anchor gap inside the Phase 3 ABI and bindings survey surface on `master`.

## Roadmap Anchor

- the Phase 3 roadmap names `lib/rbtree.c` as one of the permanent C/Zigux boundary anchors beside `rust/exports.c`, `lib/bitmap.c`, and `lib/cpumask.c`

## Current Repo Reality

- `include/zigux/abi.h` already exposes `zigux_rbtree_root_view`, `zigux_rbtree_root_view_is_cached()`, `zigux_rbtree_root_view_has_leftmost()`, `zigux_rbtree_root_view_is_valid()`, and `zigux_rbtree_root_view_canonicalize()`
- `zigux/bindings/abi.zig` already mirrors that shared ABI surface through `RbtreeRootView`, `rbtreeRootViewIsCached()`, `rbtreeRootViewHasLeftmost()`, `rbtreeRootViewIsValid()`, and `canonicalizeRbtreeRootView()`
- `zigux/kernel/export_shim.zig` already keeps the runtime status relay explicit through `validateRbtreeRootView()`
- `zigux/tests/phase3_abi.zig` already replays the shared `RbtreeRootView` layout and validation path
- `Documentation/zigux/phase3-bitmap-cpumask-slice.md`, `zigux/helpers/bitmap_view.zig`, and `zigux/helpers/cpumask_view.zig` already provide a dedicated bounded packet for the `lib/bitmap.c` and `lib/cpumask.c` anchor family
- `Documentation/zigux/phase3-list-hlist-slice.md`, `zigux/helpers/list_view.zig`, and `zigux/helpers/hlist_view.zig` already provide a dedicated adjacent boundary packet for list and hlist follow-through

## Current Gap

Current `master` carries shared `RbtreeRootView` ABI and validation evidence, but it does not yet carry a dedicated manifest-backed `lib/rbtree.c` boundary packet comparable to the landed bitmap/cpumask and list/hlist survey slices. The roadmap anchor is therefore only partially materialized at the ABI-and-layout layer rather than as its own bounded interop packet.

## Next Bounded Step

- add a dedicated `phase3-rbtree` survey packet that reuses the existing `RbtreeRootView` ABI surface, keeps the scope at boundary and layout validation, and does not widen into broader runtime-core delivery
