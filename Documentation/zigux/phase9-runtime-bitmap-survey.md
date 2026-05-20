# Phase 9 Runtime Bitmap Survey

This note tracks the bounded Phase 9 runtime bitmap packet.

## Status
- `PHASE9_STATUS=active`
- `PHASE9_LANE_KEY=P9-L08`
- `PHASE9_SURVEYED_COMMIT=66e60700501fc8bb08d645b081064c4698562427`
- scope: returned runtime bitmap packet, bounded build bundle, and no broader shared runtime-loader claim

## Current repo reality
- fresh public-tree reread on 2026-05-20 reconfirms `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_diff.zig`, `zigux/tests/runtime_bitmap_manifest.json`, `zigux/tests/runtime_bitmap_survey.zig`, and `zigux/tests/phase9_build.zig`
- keep `zigux/tests/phase9_build.zig` explicit only as a bounded Phase 9 build bundle whose live body names the same runtime bitmap sample, loader, top-bit, module, diff, and survey targets beside `zigux/tests/runtime_atomic64_diff.zig`
- current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample
- the returned runtime bitmap family is still separate from the broader shared runtime-loader packet

## Boundaries
- keep the visible bitmap-side packet inside `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_diff.zig`, `zigux/tests/runtime_bitmap_manifest.json`, `zigux/tests/runtime_bitmap_survey.zig`, and the shared `zigux/tests/phase9_build.zig` bundle
- keep the broader shared runtime-loader substrate explicit as absent
- do not claim the returned runtime bitmap packet proves the broader shared runtime-loader packet returned
- do not present the returned bitmap family as evidence that a fifth approved Phase 5 sample family landed here
- keep `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, and the broader shared `zigux/tests/runtime_*` replay family framed as same-lane repo-reality gaps until fresh rereads prove they returned
- keep the focused `phase9-runtime-bitmap-tests` and `phase9-runtime-bitmap-top-bit-tests` route names framed as bitmap-family rerun handles, not shared-loader proof

## Roadmap gap
- the Phase 9 roadmap target is still `first loadable Zigux runtime modules with selftest hooks and runtime module lifecycle parity`
- the current runtime bitmap packet is now `returned_bitmap_family_without_broader_shared_loader_substrate`: the survey note, module-slice note, sample, loader, top-bit, module, diff, manifest, survey gate, and bounded build bundle are visible, but the broader shared runtime-loader substrate is not
- the blocked follow-through remains `broader shared runtime-loader substrate parity`

## Gates
1. `zig test zigux/tests/runtime_bitmap_survey.zig`
2. `zig build phase9-runtime-bitmap-top-bit-tests --build-file zigux/tests/phase9_build.zig`
3. `zig build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig`

Treat gates 2 and 3 as bitmap-family rerun handles only; they do not prove the broader shared runtime-loader packet returned.

## Next bounded step

Keep the returned bitmap packet aligned across this note, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `zigux/tests/runtime_bitmap_survey.zig`, and `samples/zigux/README.md`. If the lane reopens soon, compare `samples/zigux/README.md` against this packet first for the next one-file truthfulness repair.
