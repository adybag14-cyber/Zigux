# Phase 9 Runtime Bitmap Module Slice

This document tracks the first bounded Phase 9 runtime bitmap starter under `samples/zigux/`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-bitmap-module-starter`
- scope: lifecycle starter, bitmap range mutation, ordered sparse-bit replay, copy behavior, bounded differential coverage, dedicated Phase 9 test wiring, and lane-local manifest closure only
- product boundary:
  - `samples/zigux/runtime_bitmap.zig`
  - `samples/zigux/runtime_bitmap_loader.zig`
  - `zigux/tests/runtime_bitmap_module.zig`
  - `zigux/tests/runtime_bitmap_diff.zig`
  - `zigux/tests/runtime_bitmap_manifest.json`
  - `zigux/tests/runtime_bitmap_survey.zig`
  - `zigux/tests/phase9_build.zig`

## Why this slice exists

The Phase 9 roadmap explicitly names `lib/test_bitmap.c` as a runtime pilot anchor and recommends `zigux/tests/runtime_*` plus `samples/zigux/runtime_*` as the bounded Zigux destinations.

The live repo already had an atomic64 starter under the same Phase 9 review path, but it still had no matching bitmap pilot. This slice lands the smallest honest bitmap follow-on step: a sample-backed lifecycle scaffold that reuses the existing bitmap-view helper without claiming loadable-module parity or broad bitmap API coverage.

## Landed starter surface

- module descriptor metadata naming the `lib/test_bitmap.c` anchor
- guarded lifecycle transitions for `cold`, `initialized`, `selftest_complete`, and `exited`
- a bounded two-word runtime bitmap backing store with explicit `setRange`, `clearRange`, ordered `nthSetBit()` sparse replay, `copyFrom`, source-lifecycle guard behavior, and a direct post-selftest mutation replay proof that stays reviewable before exit
- summary checks that reuse `zigux/helpers/bitmap_view.zig` for `first_set`, `first_zero`, and `weight`
- a table-driven differential gate that replays a few `lib/test_bitmap.c` expectations for set, clear, summary, and copy behavior
- a tiny sample-side loader handoff scaffold that names bounded entry and exit symbols, pins the full `first_set`, `first_zero`, `weight`, and `nbits` handoff summary, and emits both waiting and released shared runtime-loader request shapes for the no-substrate path without claiming a real module loader
- a shared runtime-loader request binding in `zigux/kernel/runtime_loader.zig` that now consumes the bitmap handoff shape, allocator posture, and staged entry or exit symbols without claiming live execution
- dedicated Phase 9 tests and manifest coverage wired into the shared `zigux/tests/phase9_build.zig` gate

## Non-goals

This slice does not yet claim:

- a kernel-loadable Zigux bitmap module
- runtime module init and exit macro parity
- direct parity for the full `lib/test_bitmap.c` surface
- parse, print, region-allocation, or performance-path differentials

## Gates

1. run the dedicated Phase 9 build
- `zig build test --build-file zigux/tests/phase9_build.zig`

2. run the convenience target
- `make -C zigux phase9`

## Next bounded step

Stay in the Phase 9 runtime bitmap lane and keep the next step on the remaining broader shared runtime-loader control surface or real lifecycle-parity blocker, rather than inventing another bitmap-local binding surface now that `zigux/kernel/runtime_loader.zig` already consumes the current handoff plan.