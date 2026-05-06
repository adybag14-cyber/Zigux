# Phase 9 Runtime Bitmap Module Slice

This document tracks the first bounded Phase 9 runtime bitmap starter under `samples/zigux/`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-bitmap-module-starter`
- `PHASE9_LANE_KEY=P9-Y05`
- scope: lifecycle starter, sample-side loader scaffold, bitmap range mutation and copy behavior, bounded differential coverage, dedicated Phase 9 survey and test wiring, and lane-local survey-note plus manifest closure only
- product boundary:
  - `samples/zigux/runtime_bitmap.zig`
  - `samples/zigux/runtime_bitmap_loader.zig`
  - `zigux/tests/runtime_bitmap_module.zig`
  - `zigux/tests/runtime_bitmap_diff.zig`
  - `zigux/tests/runtime_bitmap_manifest.json`
  - `zigux/tests/runtime_bitmap_survey.zig`
  - `Documentation/zigux/phase9-runtime-bitmap-survey.md`
  - `zigux/tests/phase9_build.zig`

## Why this slice exists

The Phase 9 roadmap explicitly names `lib/test_bitmap.c` as a runtime pilot anchor and recommends `zigux/tests/runtime_*` plus `samples/zigux/runtime_*` as the bounded Zigux destinations.

The live repo already had an atomic64 starter under the same Phase 9 review path, but it still had no matching bitmap pilot. This slice now records the smallest honest bitmap follow-on packet: a sample-backed lifecycle scaffold, its sample-side loader handoff, and the dedicated survey and test gates that keep the current sample contract reviewable without claiming loadable-module parity or broad bitmap API coverage.

## Landed starter surface

- module descriptor metadata naming the `lib/test_bitmap.c` anchor and keeping the roadmap-required selftest hook explicit through `provides_selftest_hook=true`
- guarded lifecycle transitions for `cold`, `initialized`, `selftest_complete`, and `exited`
- a bounded two-word runtime bitmap backing store with explicit `setRange`, `clearRange`, `copyFrom`, and source-lifecycle guard behavior
- summary checks that reuse `zigux/helpers/bitmap_view.zig` for `first_set`, `first_zero`, and `weight`
- a table-driven differential gate that replays a few `lib/test_bitmap.c` expectations for set, clear, summary, and copy behavior
- a tiny sample-side loader handoff scaffold that names bounded entry and exit symbols, captures the handoff bitmap summary, and keeps no-substrate release behavior explicit without claiming a real module loader
- a dedicated survey gate and survey note that keep this runtime bitmap packet explicit as Phase 9 follow-on work rather than a fifth approved Phase 5 sample anchor
- dedicated Phase 9 tests, survey coverage, manifest closure, and the focused `zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig` shard for the shared runtime-loader facade plus allocator/init-flow contract packet wired into the shared `zigux/tests/phase9_build.zig` gate and `make -C zigux phase9`

## Non-goals

This slice does not yet claim:

- a kernel-loadable Zigux bitmap module
- runtime module init and exit macro parity
- direct parity for the full `lib/test_bitmap.c` surface
- parse, print, region-allocation, or performance-path differentials

## Gates

1. run the focused shared runtime-loader shard
- `zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig`

2. run the dedicated Phase 9 build
- `zig build test --build-file zigux/tests/phase9_build.zig`

3. run the convenience target
- `make -C zigux phase9`

## Next bounded step

Stay in the Phase 9 runtime bitmap lane and keep the next step on the remaining shared runtime-substrate blocker, most likely a future `zigux/kernel/runtime_loader.zig` or equivalent binding surface that can consume the new handoff plan without pretending full kernel module parity already exists.
