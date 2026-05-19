# Phase 9 Runtime Bitmap Module Slice

This document tracks the current bounded runtime bitmap reminder slice.

## Status
- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-bitmap-reminder-slice`
- `PHASE9_LANE_KEY=P9-L08`
- `PHASE9_SURVEYED_COMMIT=66e60700501fc8bb08d645b081064c4698562427`
- scope: partial reminder packet, bounded build-bundle vocabulary, and blocked loader-substrate follow-through only

## Current visible slice
- `Documentation/zigux/phase9-runtime-bitmap-survey.md`
- `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`
- `zigux/tests/runtime_bitmap_survey.zig`
- `zigux/tests/phase9_build.zig`

## Repo-reality gaps on trusted current-tree reads
- `samples/zigux/runtime_bitmap.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_bitmap_top_bit_contract.zig`
- `zigux/tests/runtime_bitmap_module.zig`
- `zigux/tests/runtime_bitmap_diff.zig`
- `zigux/tests/runtime_bitmap_manifest.json`
- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`

## Why This Slice Exists

The runtime bitmap lane still needs a family-local note that keeps the partial bitmap-side reminder packet explicit without turning missing starter, loader, top-bit, diff, module, or manifest files into fake evidence.

The shared `zigux/tests/phase9_build.zig` bundle still names bitmap-local route vocabulary, but that bundle alone is not proof that the missing direct sample-family files returned.

The live runtime substrate is still missing, so this slice must stay review-only and keep the broader blocked handoff explicit.

## Roadmap Gap

- the Phase 9 roadmap target is still `first loadable Zigux runtime modules with selftest hooks and runtime module lifecycle parity`
- the current runtime bitmap packet is still `partial_packet_without_loadable_runtime_substrate`: the survey note, module-slice note, survey gate, and bounded build bundle are visible, but the direct sample, loader companion, top-bit companion, module gate, diff gate, manifest-backed ownership packet, and shared runtime substrate are not currently materialized on the trusted path
- the blocked deliverable remains `loadable Phase 9 runtime bitmap pilot module parity`

## Gates
1. `zig test zigux/tests/runtime_bitmap_survey.zig`
2. `zig build phase9-runtime-bitmap-top-bit-tests --build-file zigux/tests/phase9_build.zig`
3. `zig build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig`
4. `zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig`

Treat gates 2 through 4 as bounded build-bundle vocabulary only while the trusted current-tree path still leaves the direct bitmap sample-family files absent.

## Next Bounded Step

Trim the next smallest same-lane shared reminder surface that still overclaims returned runtime bitmap files, starting with `samples/zigux/README.md`.