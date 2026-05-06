# Phase 9 Runtime Bitmap Module Slice

This document tracks the first bounded Phase 9 runtime bitmap starter under `samples/zigux/`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-bitmap-module-starter`
- `PHASE9_LANE_KEY=P9-Y05`
- scope: lifecycle starter, sample-side loader scaffold, focused top-bit companion replay, bitmap range mutation and copy behavior, bounded differential coverage, dedicated Phase 9 survey and test wiring, the shared runtime-loader facade plus allocator/init-flow contract replay, and lane-local survey-note plus manifest closure only
- product boundary:
  - `samples/zigux/runtime_bitmap.zig`
  - `samples/zigux/runtime_bitmap_loader.zig`
  - `samples/zigux/runtime_bitmap_top_bit_build.zig`
  - `samples/zigux/runtime_bitmap_top_bit_contract.zig`
  - `zigux/tests/runtime_bitmap_module.zig`
  - `zigux/tests/runtime_bitmap_diff.zig`
  - `zigux/tests/runtime_bitmap_manifest.json`
  - `zigux/tests/runtime_bitmap_survey.zig`
  - `Documentation/zigux/phase9-runtime-bitmap-survey.md`
  - `zigux/kernel/runtime_loader.zig`
  - `zigux/kernel/runtime_loader_contract.zig`
  - `zigux/tests/runtime_loader_allocator_init_flow.zig`
  - `zigux/tests/phase9_build.zig`
  - `zigux/Makefile`

## Why this slice exists

The Phase 9 roadmap explicitly names `lib/test_bitmap.c` as a runtime pilot anchor and recommends `zigux/tests/runtime_*` plus `samples/zigux/runtime_*` as the bounded Zigux destinations.

The live repo already had an atomic64 starter under the same Phase 9 review path, but it still had no matching bitmap pilot. This slice now records the smallest honest bitmap follow-on packet: a sample-backed lifecycle scaffold, its sample-side loader handoff, the focused highest-valid-bit companion replay, and the dedicated survey and test gates that keep the current sample contract reviewable without claiming loadable-module parity or broad bitmap API coverage.

This runtime bitmap pair also stays outside the four approved Phase 5 reference samples: `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_bitmap_top_bit_{build,contract}.zig` remain the separate Phase 9 runtime bitmap family rooted in `lib/test_bitmap.c`, not a fifth Phase 5 sample-root idiom under `samples/zigux/`.
The shared sample-root catalog at `samples/zigux/README.md` keeps the approved Phase 5 anchors limited to `bytestream_fifo.zig`, `kobject_example.zig`, `kretprobe_example.zig`, and `trace_events_sample.zig`, while listing the runtime bitmap pair plus the focused top-bit companion replay only under the separate Phase 9 runtime pilot family.

## Landed starter surface

- module descriptor metadata naming the `lib/test_bitmap.c` anchor and keeping the roadmap-required selftest hook explicit through `provides_selftest_hook=true`
- guarded lifecycle transitions for `cold`, `initialized`, `selftest_complete`, and `exited`
- a bounded two-word runtime bitmap backing store with explicit `setRange`, `clearRange`, `copyFrom`, and source-lifecycle guard behavior
- summary checks that reuse `zigux/helpers/bitmap_view.zig` for `first_set`, `first_zero`, and `weight`
- a focused top-bit companion replay that keeps bit `127` as the highest valid bit, replays one-bit summary behavior at the top boundary, and rejects out-of-range mutation past `128`
- a table-driven differential gate that replays a few `lib/test_bitmap.c` expectations for set, clear, summary, and copy behavior
- a tiny sample-side loader handoff scaffold that names bounded entry and exit symbols, captures the handoff bitmap summary, and keeps no-substrate release behavior explicit without claiming a real module loader
- dedicated Phase 9 tests, survey coverage, manifest closure, the shared `zigux/kernel/runtime_loader.zig` facade, the shared `zigux/kernel/runtime_loader_contract.zig` plus `zigux/tests/runtime_loader_allocator_init_flow.zig` replay, and the focused `zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig` shard wired into the shared `zigux/tests/phase9_build.zig` gate and `make -C zigux phase9`

## Non-goals

This slice does not yet claim:

- a kernel-loadable Zigux bitmap module
- runtime module init and exit macro parity
- direct parity for the full `lib/test_bitmap.c` surface
- parse, print, region-allocation, or performance-path differentials

## Gates

1. run the focused top-bit companion replay
- `zig build phase9-runtime-bitmap-top-bit-tests --build-file zigux/tests/phase9_build.zig`

2. run the focused shared runtime-loader shard
- `zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig`

3. run the dedicated Phase 9 build
- `zig build test --build-file zigux/tests/phase9_build.zig`

4. run the convenience target
- `make -C zigux phase9`

## Next bounded step

Stay in the Phase 9 runtime bitmap lane and keep the next step on the remaining shared runtime-substrate blocker, most likely a future `zigux/kernel/runtime_loader.zig` or equivalent binding surface that can consume the new handoff plan without pretending full kernel module parity already exists.
