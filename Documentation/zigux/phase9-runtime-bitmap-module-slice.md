# Phase 9 Runtime Bitmap Module Slice

This document tracks the current bounded runtime bitmap starter packet.

## Status
- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-bitmap-module-starter`
- `PHASE9_LANE_KEY=P9-L08`
- `PHASE9_SURVEYED_COMMIT=66e60700501fc8bb08d645b081064c4698562427`
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

The runtime bitmap packet needs a family-local review surface that keeps the sample lifecycle, repeat-init rejection, focused diff cases, shared-request handoff, top-bit boundary contract, and focused tests visible without implying live runtime substrate parity.

The direct `samples/zigux/runtime_bitmap.zig` starter now also keeps repeat-init rejection explicit across initialized, selftested, and exited retries, so the review packet fails closed on state-preserving lifecycle rejection before widening into live runtime claims.

The `zigux/tests/runtime_bitmap_diff.zig` gate owns the bounded `lib/test_bitmap.c` replay plus the selftest-complete and exit lifecycle guards, so those checks stay bitmap-local review proof instead of borrowing coverage from the shared loader packet.

The `samples/zigux/runtime_bitmap_loader.zig` scaffold now also keeps the prepared shared-request plan drift guard explicit before `requestSharedRuntimeLoad()` advances the bitmap-local loader to `waiting_on_runtime_substrate`, so approved-family anchor and symbol drift, selftest-hook drift, allocator drift, and init-flow drift fail closed inside the same bitmap-local ownership packet instead of being deferred to the broader shared loader lane.

The focused `samples/zigux/runtime_bitmap_top_bit_contract.zig` companion replay plus the dedicated `phase9-runtime-bitmap-top-bit-tests` route keep the highest-valid-bit boundary contract explicit inside the same bitmap-local packet instead of letting that boundary disappear into the broader shared loader bundle.

The live runtime substrate is still missing, so this slice must stay review-only and keep the broader blocked handoff explicit.

## Roadmap Gap

- the Phase 9 roadmap target is still `first loadable Zigux runtime modules with selftest hooks and runtime module lifecycle parity`
- the current runtime bitmap packet is still `starter_landed_without_loadable_runtime_substrate`: the sample starter, diff gate, survey gate, top-bit companion replay, and loader scaffold are visible, but the shared runtime substrate is still missing
- the blocked deliverable remains `loadable Phase 9 runtime bitmap pilot module parity`

## Gates
1. `zig test zigux/tests/runtime_bitmap_module.zig`
2. `zig test zigux/tests/runtime_bitmap_diff.zig`
3. `zig test zigux/tests/runtime_bitmap_survey.zig`
4. `zig build phase9-runtime-bitmap-top-bit-tests --build-file zigux/tests/phase9_build.zig`
5. `zig build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig`
6. `zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig`

## Next Bounded Step

Leave the runtime bitmap packet parked unless a smaller same-lane lifecycle, repeat-init, diff, top-bit boundary, prepared-plan handoff, or selftest-hook reviewability gap appears before the blocked shared runtime substrate work moves again.
