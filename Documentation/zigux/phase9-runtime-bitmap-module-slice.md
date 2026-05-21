# Phase 9 Runtime Bitmap Module Slice

This document tracks the current bounded runtime bitmap slice.

## Status
- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-bitmap-partial-slice`
- `PHASE9_LANE_KEY=P9-L08`
- `PHASE9_SURVEYED_COMMIT=2026-05-20-runtime-bitmap-loader-partial-return`
- scope: partial runtime bitmap reminder packet, direct sample proof, direct loader proof, top-bit companion proof, bounded build-bundle vocabulary, and no broader shared runtime-loader claim

## Current visible slice
- `Documentation/zigux/phase9-runtime-bitmap-survey.md`
- `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`
- `zigux/tests/runtime_bitmap_survey.zig`
- `zigux/tests/phase9_build.zig`
- `samples/zigux/runtime_bitmap.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_bitmap_top_bit_contract.zig`

## Repo-reality gaps inside the bitmap family
- `zigux/tests/runtime_bitmap_module.zig`
- `zigux/tests/runtime_bitmap_diff.zig`
- `zigux/tests/runtime_bitmap_manifest.json`

## Repo-reality gaps outside this bitmap reminder packet
- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- the broader shared `zigux/tests/runtime_*` replay family beyond this bitmap-side reminder packet

## Why This Slice Exists

The runtime bitmap lane still needs a family-local note that keeps the visible reminder packet explicit without turning it into false proof that the broader shared runtime-loader substrate returned too.

The current visible packet includes the direct bitmap sample, direct loader companion, and focused top-bit companion alongside the survey note, module-slice note, survey gate, and bounded build bundle. The shared `zigux/tests/phase9_build.zig` bundle now reruns the direct sample, loader, survey gate, and top-bit companion and still does not prove that the broader runtime bitmap module, diff, or manifest packet returned.

The shared runtime substrate is still absent, and the module, diff, and manifest legs are still absent on the trusted read path, so this slice must stay bitmap-local and keep that wider blocked handoff explicit.

## Roadmap Gap

- the Phase 9 roadmap target is still `first loadable Zigux runtime modules with selftest hooks and runtime module lifecycle parity`
- the current runtime bitmap packet is still `partial_packet_without_loadable_runtime_substrate`: the survey note, module-slice note, survey gate, bounded build bundle, direct sample, direct loader companion, and top-bit companion are visible, but the module gate, diff gate, manifest-backed ownership packet, and broader shared runtime-loader substrate are not
- the blocked follow-through remains `broader shared runtime-loader substrate parity`

## Gates
1. `zig test zigux/tests/runtime_bitmap_survey.zig`
2. `zig build phase9-runtime-bitmap-loader-tests --build-file zigux/tests/phase9_build.zig`
3. `zig build phase9-runtime-bitmap-top-bit-tests --build-file zigux/tests/phase9_build.zig`
4. `zig build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig`

Treat the shared `zigux/tests/phase9_build.zig` bitmap route names as rerun handles for the visible sample, loader, survey, and top-bit packet only while the module, diff, and manifest surfaces stay absent on the trusted path; they do not prove the broader shared runtime-loader packet returned.

## Next Bounded Step

Advance the next same-lane surface inside the module-side runtime bitmap family, starting with `zigux/tests/runtime_bitmap_module.zig`, and widen only when a coherent module-side packet is directly readable again.
