# Phase 3 List/HList Interop Slice

This document defines the third bounded Phase 3 slice for Zigux.

## Status

- `PHASE3_STATUS=active`
- `PHASE3_SLICE=list-hlist-view-interop`
- scope: curated `list_head` / `hlist` boundary helpers only
- product boundary:
  - `include/zigux/abi.h`
  - `include/linux/zigux.h`
  - `zigux/helpers/list_view.zig`
  - `zigux/helpers/hlist_view.zig`
  - `zigux/tests/phase3_list_hlist_dump.zig`

## Why this slice exists

Bitmap and cpumask were the first reusable Linux-facing interop seam.
The next correct structure seam is linked-list state, because Linux-facing code depends on it everywhere and it is still small enough to validate tightly.

The correct bounded step is:

- stable list and hlist view descriptors
- stable list and hlist summary structs
- bounded empty/singular/terminated/circular/truncated semantics
- raw traversal isolated behind the existing narrow unsafe layer
- one committed C-vs-Zig parity fixture

This keeps the slice reviewable while making future container and scheduler-facing Zigux work materially easier.

## Gates

1. validate Phase 3 slice shape
- `python3 scripts/zigux/validate-phase3.py`

2. check C-vs-Zig list/hlist parity
- `python3 scripts/zigux/run-phase3-checks.py --slug list-hlist`

3. run the wider Phase 3 substrate tests
- `zig build phase3-test --build-file zigux/tests/build.zig`

- `PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py`
- `PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug list-hlist`
- `PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig`
- `PHASE3_LIST_HLIST_BOUNDARY=descriptor-only-no-container-of-no-lockless-no-rcu-no-notifier-chains`

## Interop rules

- `zigux_list_view` and `zigux_hlist_view` stay address-plus-budget descriptors, not ownership containers.
- `zigux_list_summary` and `zigux_hlist_summary` stay plain layout-only ABI structs.
- raw address dereference stays inside `zigux/unsafe/narrow.zig`, `zigux/helpers/list_view.zig`, and `zigux/helpers/hlist_view.zig`.
- traversal must stay bounded by `max_nodes`.
- no allocator behavior is introduced in this slice.

## Boundary

This slice does not claim:

- full `include/linux/list.h` replacement
- full `include/linux/hlist.h` replacement
- container-of helpers
- lockless list semantics
- RCU list semantics
- notifier-chain ownership or callback delivery
- scheduler ownership or queue integration

This slice only closes the first permanent list/hlist interop seam on top of the existing Phase 3 ABI substrate.
