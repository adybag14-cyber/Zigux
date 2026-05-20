# Phase 9 Runtime Bitmap Module Slice

This document tracks the current bounded runtime bitmap slice.

## Status
- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-bitmap-partial-slice`
- `PHASE9_LANE_KEY=P9-L08`
- `PHASE9_SURVEYED_COMMIT=66e60700501fc8bb08d645b081064c4698562427`
- scope: partial runtime bitmap reminder packet, bounded build-bundle vocabulary, and no broader shared runtime-loader claim

## Current visible slice
- `Documentation/zigux/phase9-runtime-bitmap-survey.md`
- `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`
- `zigux/tests/runtime_bitmap_survey.zig`
- `zigux/tests/phase9_build.zig`

## Repo-reality gaps inside the bitmap family
- `samples/zigux/runtime_bitmap.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_bitmap_top_bit_contract.zig`
- `zigux/tests/runtime_bitmap_module.zig`
- `zigux/tests/runtime_bitmap_diff.zig`
- `zigux/tests/runtime_bitmap_manifest.json`

## Repo-reality gaps outside this bitmap reminder packet
- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- the broader shared `zigux/tests/runtime_*` replay family beyond this bitmap-side reminder packet

## Why This Slice Exists

The runtime bitmap lane still needs a family-local note that keeps the visible reminder packet explicit without turning it into false proof that the broader shared runtime-loader substrate returned too.

The shared `zigux/tests/phase9_build.zig` bundle names bitmap-local rerun handles, but that bundle still does not prove the broader shared runtime-loader packet returned.

The shared runtime substrate is still absent, and the direct bitmap sample-family files are still absent on the trusted read path, so this slice must stay bitmap-local and keep that wider blocked handoff explicit.

## Roadmap Gap

- the Phase 9 roadmap target is still `first loadable Zigux runtime modules with selftest hooks and runtime module lifecycle parity`
- the current runtime bitmap packet is still `partial_packet_without_loadable_runtime_substrate`: the survey note, module-slice note, survey gate, and bounded build bundle are visible, but the direct sample, loader companion, top-bit companion, module gate, diff gate, manifest-backed ownership packet, and broader shared runtime-loader substrate are not
- the blocked follow-through remains `broader shared runtime-loader substrate parity`

## Gates
1. `zig test zigux/tests/runtime_bitmap_survey.zig`
2. `zig build phase9-runtime-bitmap-top-bit-tests --build-file zigux/tests/phase9_build.zig`
3. `zig build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig`

Treat gates 2 and 3 as bitmap-family rerun handles only while the direct bitmap sample-family files stay absent on the trusted path; they do not prove the broader shared runtime-loader packet returned.

## Next Bounded Step

Keep the next same-lane shared reminder surface aligned with this partial bitmap packet, starting with `Documentation/zigux/review-checklist.md`.
