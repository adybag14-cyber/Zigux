# Phase 9 Runtime Bitmap Survey

This note tracks the bounded Phase 9 runtime bitmap reminder packet.

## Status
- `PHASE9_STATUS=active`
- `PHASE9_LANE_KEY=P9-L08`
- `PHASE9_SURVEYED_COMMIT=2026-05-22-runtime-bitmap-diff-returned`
- scope: partial reminder packet, direct sample proof, direct loader proof, direct module proof, direct diff proof, manifest-backed ownership packet, top-bit companion proof, and no broader runtime-loader parity claim

## Current repo reality
- trusted current-tree contents reads on 2026-05-22 do materialize `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `zigux/tests/runtime_bitmap_manifest.json`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_diff.zig`, `zigux/tests/phase9_build.zig`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig`
- keep `zigux/tests/phase9_build.zig` explicit only as a bounded Phase 9 build bundle whose live body reruns the direct sample, loader, survey, diff, and top-bit proofs; the module-side proof is directly readable beside that bundle, but the bundle alone still does not prove the broader runtime bitmap packet or shared runtime-loader parity
- current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample

## Boundaries
- keep the visible bitmap-side reminder packet inside `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `zigux/tests/runtime_bitmap_manifest.json`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_diff.zig`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, and the shared `zigux/tests/phase9_build.zig` bundle
- keep the blocked shared runtime-loader substrate explicit
- do not claim loadable runtime bitmap module parity
- do not present the visible bitmap packet as proof that the broader shared runtime-loader packet returned
- keep the focused `phase9-runtime-bitmap-tests` route name framed only as a bounded rerun handle for the visible sample, loader, survey, diff, and top-bit packet while the directly readable module-side proof sits adjacent

## Roadmap gap
- the Phase 9 roadmap target is still `first loadable Zigux runtime modules with selftest hooks and runtime module lifecycle parity`
- the current runtime bitmap reminder packet is still `partial_packet_with_diff_but_without_broader_runtime_loader_parity`: the survey note, module-slice note, manifest-backed ownership packet, survey gate, bounded build bundle, direct sample, direct loader companion, direct module proof, direct diff proof, and top-bit companion proof are visible, but the broader shared runtime-loader substrate is still only partially materialized on the trusted path
- the blocked deliverable remains `loadable Phase 9 runtime bitmap pilot module parity`

## Gates
1. `zig test zigux/tests/runtime_bitmap_survey.zig`
2. `zig test zigux/tests/runtime_bitmap_module.zig`
3. `zig test zigux/tests/runtime_bitmap_diff.zig`
4. `zig test samples/zigux/runtime_bitmap.zig`
5. `zig test samples/zigux/runtime_bitmap_loader.zig`
6. `zig test samples/zigux/runtime_bitmap_top_bit_contract.zig`

Treat the shared `zigux/tests/phase9_build.zig` bitmap route names as bounded rerun handles for the visible sample, loader, survey, diff, and top-bit packet only while the broader shared runtime-loader family remains partial.

## Next bounded step

Replay `zig build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig` on a fresh full checkout and fix only the next bitmap-local compile or note drift it exposes, leaving broader shared runtime-loader follow-through to the separate shared-owner packet.