# Phase 3 Roadmap Interop Gap Survey

This note compares the current Phase 3 ABI and interop roadmap expectations against current `master` without widening into later lanes.

## Roadmap Baseline

Phase 3 in the roadmap is anchored on:

- `rust/exports.c`
- `lib/bitmap.c`
- `lib/rbtree.c`
- `lib/cpumask.c`

The roadmap also requires:

- explicit export shims
- generated or curated bindings
- layout assertions
- explicit panic policy
- explicit allocator policy
- approved atomic, barrier, and MMIO wrappers
- narrow unsafe surface

## Current Repo Reality

Current `master` already carries a substantive bounded ABI packet through:

- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `include/zigux/dev_t.h`
- `zigux/bindings/abi.zig`
- `zigux/bindings/notifier_abi.zig`
- `zigux/bindings/header_family.zig`
- `zigux/kernel/export_shim.zig`
- `zigux/helpers/layout_assert.zig`
- `zigux/helpers/panic_policy.zig`
- `zigux/helpers/allocator_policy.zig`
- `zigux/helpers/atomic.zig`
- `zigux/helpers/barrier.zig`
- `zigux/helpers/mmio.zig`
- `zigux/helpers/unsafe_policy.zig`
- `zigux/unsafe/narrow.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_export_uapi_layout.zig`
- `zigux/tests/phase3_low_level_wrappers.zig`

Current `master` also carries adjacent helper-local interop follow-through for two of the roadmap anchors through:

- `zigux/helpers/bitmap_view.zig`
- `zigux/helpers/cpumask_view.zig`
- `Documentation/zigux/phase3-bitmap-cpumask-slice.md`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`

That means the lane is no longer at a skeleton-only stage. The export boundary, header-family relay, layout assertions, policy helpers, low-level wrappers, and two helper-local anchor families are all materially present on current `master`.

## Current Gap

The remaining bounded interop gap is narrower than the original Phase 3 skeleton, but it is still real.

1. The roadmap anchor at `lib/rbtree.c` does not yet have matching repo-visible Phase 3 follow-through. Current `master` has no `zigux/helpers/rbtree_view.zig` companion and no bounded `phase3_rbtree` replay route.
2. The shared ABI packet still does not expose a direct differential C-fixture route for the starter ABI surface. The original ledger shape referenced `zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c` and `zigux/tests/fixtures/phase3_abi/expected.json`, but current `master` does not yet carry that packet-local parity route.
3. The helper-local bitmap/cpumask and list/hlist follow-through exists, but it remains adjacent evidence rather than closure of the full roadmap anchor set.

## Lane Discipline

This survey is intentionally limited to Phase 3 ABI and interop truthfulness.

It does not claim:

- scheduler or driver follow-through
- wider xarray closure
- full Phase 3 completion
- Phase 4 differential validation closure

## Next Safe Step

Stay in the same lane and close one of these bounded gaps before widening further:

- add a bounded `rbtree` interop slice with a replay route, or
- add the missing shared-ABI C harness and expected-output fixture route promised by the earlier starter-packet plan
