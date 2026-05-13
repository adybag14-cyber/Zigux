# Phase 9 Runtime Bitmap Module Slice

This document tracks the current bounded runtime bitmap starter packet.

## Status
- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-bitmap-module-starter`
- `PHASE9_LANE_KEY=P9-L08`
- `PHASE9_SURVEYED_COMMIT=00b92f22991e9124aefb308d7eb0e90f14923338`
- scope: sample starter, diff gate, loader scaffold, top-bit companion replay, module gate, survey gate, manifest-backed ownership packet, and shared loader handoff plus shared build routes only

## Product Boundary
- `samples/zigux/runtime_bitmap.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_bitmap_top_bit_contract.zig`
- `zigux/tests/runtime_bitmap_module.zig`
- `zigux/tests/runtime_bitmap_diff.zig`
- `zigux/tests/runtime_bitmap_survey.zig`
- `zigux/tests/runtime_bitmap_manifest.json`
- `zigux/tests/phase9_build.zig`
- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`

## Why This Slice Exists

The runtime bitmap packet needs a family-local review surface that keeps the sample lifecycle, focused diff cases, shared-request handoff, top-bit boundary contract, and focused tests visible without implying live runtime substrate parity.

The `zigux/tests/runtime_bitmap_diff.zig` gate owns the bounded `lib/test_bitmap.c` replay plus the selftest-complete and exit lifecycle guards, so those checks stay bitmap-local review proof instead of borrowing coverage from the shared loader packet.

The live runtime substrate is still missing, so this slice must stay review-only and keep the broader blocked handoff explicit.

## Roadmap Gap

- the Phase 9 roadmap target is still `first loadable Zigux runtime modules with selftest hooks and runtime module lifecycle parity`
- the current runtime bitmap packet is still `starter_landed_without_loadable_runtime_substrate`: the sample starter, diff gate, survey gate, top-bit companion replay, and loader scaffold are visible, but the shared runtime substrate is still missing
- the blocked deliverable remains `loadable Phase 9 runtime bitmap pilot module parity`

## Gates
1. `zig test zigux/tests/runtime_bitmap_module.zig`
2. `zig test zigux/tests/runtime_bitmap_diff.zig`
3. `zig test zigux/tests/runtime_bitmap_survey.zig`
4. `zig build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig`
5. `zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig`

## Next Bounded Step

Leave the runtime bitmap packet parked unless a smaller same-lane lifecycle, diff, or selftest-hook reviewability gap appears before the blocked shared runtime substrate work moves again.
