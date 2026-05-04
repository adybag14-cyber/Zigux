# Phase 9 Runtime Bitmap Module Slice

This document tracks the first bounded Phase 9 runtime bitmap starter under `samples/zigux/`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-bitmap-module-starter`
- `PHASE9_LANE_KEY=P9-Y08`
- `PHASE9_SURVEYED_COMMIT=c0b506e3254e63fe007a72d420bb275846a89093`
- scope: lifecycle starter, bitmap range mutation and copy behavior, bounded differential coverage, bounded parse-and-print replay including duplicate bit-list normalization, empty formatting, and transactional failed-init recovery, adjacent loader scaffold plus shared loader-request binding, prepared loader-summary snapshot replay, focused top-bit companion replay plus its dedicated sample-side build file, dedicated Phase 9 sample, module, diff, and loader test wiring, and adjacent manifest plus survey packet alignment only
- product boundary:
  - `samples/zigux/runtime_bitmap.zig`
  - `samples/zigux/runtime_bitmap_loader.zig`
  - `samples/zigux/runtime_bitmap_top_bit_contract.zig`
  - `samples/zigux/runtime_bitmap_top_bit_build.zig`
  - `zigux/kernel/runtime_loader.zig`
  - `zigux/tests/runtime_bitmap_module.zig`
  - `zigux/tests/runtime_bitmap_diff.zig`
  - `zigux/tests/runtime_bitmap_manifest.json`
  - `zigux/tests/runtime_bitmap_survey.zig`
  - `zigux/tests/phase9_build.zig`

## Why this slice exists

The Phase 9 roadmap explicitly names `lib/test_bitmap.c` as a runtime pilot anchor and recommends `zigux/tests/runtime_*` plus `samples/zigux/runtime_*` as the bounded Zigux destinations.

The live repo already has matching atomic64 and bitmap starters under the same Phase 9 review path. This slice now tracks the bitmap side of that pair as the smallest honest bitmap follow-on step: a sample-backed lifecycle scaffold that reuses the existing bitmap-view helper without claiming loadable-module parity or broad bitmap API coverage.

This bounded starter also stays underneath the freeze map's study boundary. `Documentation/zigux/freeze-map.md` keeps `kernel/workqueue.c` in `Study / Boundary Only`, so this starter may describe the bounded in-memory sample, the sample-side loader scaffold, the focused top-bit companion replay, and the shared loader-request binding, but it must not imply workqueue parity, scheduler transport ownership, or any Architecture Council-approved status change for that study-only anchor.

No parity scorecard entry or Architecture Council status-change request is attached to this runtime bitmap starter packet. This module slice only records the active study boundary and does not reopen the scheduler-facing freeze posture.

## Landed starter surface

- module descriptor metadata naming the `lib/test_bitmap.c` anchor
- guarded lifecycle transitions for `cold`, `initialized`, `selftest_complete`, and `exited`
- a bounded two-word runtime bitmap backing store with explicit `setRange`, `clearRange`, `copyFrom`, source-lifecycle guard behavior, and a direct post-selftest mutation replay proof that stays reviewable before exit
- summary checks that reuse `zigux/helpers/bitmap_view.zig` for `first_set`, `first_zero`, and `weight`
- a bounded parse-and-print replay that keeps direct sample bit-list parsing and formatting reviewable through `initFromBitList()` and `formatSetBits()`, including duplicate bit-list normalization to canonical set-bit output plus empty parse-and-print replay, while failed parsed or direct init attempts stay cold and empty until a clean follow-up init succeeds, without claiming a broader runtime parsing or printing surface
- a focused companion replay under `samples/zigux/runtime_bitmap_top_bit_contract.zig` plus `samples/zigux/runtime_bitmap_top_bit_build.zig` that keeps bit `127` reviewable as the highest valid bounded bit through direct init, parse, summary, `nthSetBit()`, range counting, and canonical formatting without widening this lane into another approved Phase 5 idiom
- a table-driven differential gate that replays a few `lib/test_bitmap.c` expectations for set, clear, summary, and copy behavior
- a tiny sample-side loader handoff scaffold that names bounded entry and exit symbols, pins the full `first_set`, `first_zero`, `weight`, and `nbits` handoff summary, freezes the prepared summary before later sample mutation so pending waiting and released request shapes keep the pre-mutation counters and bitmap facts machine-checkable, preserves explicit shared command-name handoff evidence for both waiting and released request shapes, and emits both waiting and released shared runtime-loader request shapes for the no-substrate path without claiming a real module loader
- a shared runtime-loader request binding in `zigux/kernel/runtime_loader.zig` that now consumes the bitmap handoff shape, allocator posture, staged entry or exit symbols, and explicit shared command-name preservation without claiming live execution
- dedicated Phase 9 tests and manifest coverage wired into the shared `zigux/tests/phase9_build.zig` gate, including the direct `phase9-runtime-bitmap-sample-tests`, `phase9-runtime-bitmap-module-tests`, `phase9-runtime-bitmap-diff-tests`, and `phase9-runtime-bitmap-loader-tests` legs

## Non-goals

This slice does not yet claim:

- a kernel-loadable Zigux bitmap module
- runtime module init and exit macro parity
- direct parity for the full `lib/test_bitmap.c` surface beyond the bounded starter, focused top-bit companion replay, and diff gate
- broader parse-and-print differential coverage beyond the bounded starter replay
- region-allocation or performance-path differentials
- parity or ownership for `kernel/workqueue.c`
- any freeze-map status change for the scheduler-facing workqueue boundary without an Architecture Council decision

## Gates

1. run the dedicated Phase 9 build
- `zig build test --build-file zigux/tests/phase9_build.zig --summary all`
- this shared entrypoint keeps the direct sample, module, diff, and loader legs explicit for the bounded bitmap packet

2. run the convenience target
- `make -C zigux phase9`

## Next bounded step

Stay in the Phase 9 runtime bitmap lane and keep the next step on the remaining broader shared runtime-loader control surface or real lifecycle-parity blocker, rather than inventing another bitmap-local binding surface now that `zigux/kernel/runtime_loader.zig` already consumes the current handoff plan, while keeping the focused top-bit companion replay and the separate `kernel/workqueue.c` freeze-map boundary in study-only status unless the Architecture Council explicitly reopens it.
