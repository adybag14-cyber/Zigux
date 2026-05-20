# Phase 9 Runtime Bitmap Module Slice

This document tracks the current bounded runtime bitmap slice.

## Status
- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-bitmap-returned-slice`
- `PHASE9_LANE_KEY=P9-L08`
- `PHASE9_SURVEYED_COMMIT=66e60700501fc8bb08d645b081064c4698562427`
- scope: returned runtime bitmap packet, bounded build-bundle vocabulary, and no broader shared runtime-loader claim

## Current returned slice
- `Documentation/zigux/phase9-runtime-bitmap-survey.md`
- `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`
- `samples/zigux/runtime_bitmap.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_bitmap_top_bit_contract.zig`
- `zigux/tests/runtime_bitmap_module.zig`
- `zigux/tests/runtime_bitmap_diff.zig`
- `zigux/tests/runtime_bitmap_manifest.json`
- `zigux/tests/runtime_bitmap_survey.zig`
- `zigux/tests/phase9_build.zig`

## Repo-reality gaps outside this returned packet
- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- the broader shared `zigux/tests/runtime_*` replay family beyond this bitmap-local packet

## Why This Slice Exists

The runtime bitmap lane now needs a family-local note that keeps the returned bitmap packet explicit without turning it into fake proof that the broader shared runtime-loader substrate returned too.

The shared `zigux/tests/phase9_build.zig` bundle names bitmap-local rerun handles, but that bundle still does not prove the broader shared runtime-loader packet returned.

The shared runtime substrate is still absent, so this slice must stay bitmap-local and keep that wider blocked handoff explicit.

## Roadmap Gap

- the Phase 9 roadmap target is still `first loadable Zigux runtime modules with selftest hooks and runtime module lifecycle parity`
- the current runtime bitmap packet is now `returned_bitmap_family_without_broader_shared_loader_substrate`: the survey note, module-slice note, sample, loader, top-bit, module, diff, manifest, survey gate, and bounded build bundle are visible, but the broader shared runtime-loader substrate is not
- the blocked follow-through remains `broader shared runtime-loader substrate parity`

## Gates
1. `zig test zigux/tests/runtime_bitmap_survey.zig`
2. `zig build phase9-runtime-bitmap-top-bit-tests --build-file zigux/tests/phase9_build.zig`
3. `zig build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig`

Treat gates 2 and 3 as bitmap-family rerun handles only; they do not prove the broader shared runtime-loader packet returned.

## Next Bounded Step

Keep the next same-lane shared reminder surface aligned with this returned bitmap packet, starting with `samples/zigux/README.md`.
