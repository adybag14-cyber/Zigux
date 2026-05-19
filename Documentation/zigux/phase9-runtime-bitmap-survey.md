# Phase 9 Runtime Bitmap Survey

This note tracks the bounded Phase 9 runtime bitmap reminder packet.

## Status
- `PHASE9_STATUS=active`
- `PHASE9_LANE_KEY=P9-L08`
- `PHASE9_SURVEYED_COMMIT=66e60700501fc8bb08d645b081064c4698562427`
- scope: partial reminder packet, bounded build bundle, and blocked loader-substrate follow-through only

## Current repo reality
- trusted current-tree contents reads on 2026-05-19 do materialize `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `zigux/tests/runtime_bitmap_survey.zig`, and `zigux/tests/phase9_build.zig`
- the same trusted read path still returns missing for `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_diff.zig`, and `zigux/tests/runtime_bitmap_manifest.json`
- keep `zigux/tests/phase9_build.zig` explicit only as a bounded Phase 9 build bundle whose live body still names the separate runtime bitmap sample, loader, top-bit, module, diff, and survey targets beside `zigux/tests/runtime_atomic64_diff.zig`; do not treat that bundle alone as proof that the missing direct sample-family files returned
- current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample

## Boundaries
- keep the visible bitmap-side reminder packet inside `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `zigux/tests/runtime_bitmap_survey.zig`, and the shared `zigux/tests/phase9_build.zig` bundle
- keep the blocked shared runtime-loader substrate explicit
- do not claim loadable runtime bitmap module parity
- do not present the partial bitmap packet as proof that the broader shared runtime-loader packet returned
- keep `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_diff.zig`, and `zigux/tests/runtime_bitmap_manifest.json` framed as same-lane repo-reality gaps until the trusted current-tree read path returns them directly again
- keep the focused `phase9-runtime-bitmap-tests` and `phase9-runtime-bitmap-top-bit-tests` route names framed only as bounded build-bundle vocabulary while the missing direct sample-family files stay absent on the trusted path

## Roadmap gap
- the Phase 9 roadmap target is still `first loadable Zigux runtime modules with selftest hooks and runtime module lifecycle parity`
- the current runtime bitmap reminder packet is still `partial_packet_without_loadable_runtime_substrate`: the survey note, module-slice note, survey gate, and bounded build bundle are visible, but the direct sample, loader companion, top-bit companion, module gate, diff gate, and manifest-backed ownership packet are not currently materialized on the trusted path
- the blocked deliverable remains `loadable Phase 9 runtime bitmap pilot module parity`

## Gates
1. `zig test zigux/tests/runtime_bitmap_survey.zig`
2. `zig build phase9-runtime-bitmap-top-bit-tests --build-file zigux/tests/phase9_build.zig`
3. `zig build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig`

Treat gates 2 and 3 as bounded reminder-bundle handles only while the trusted current-tree path still leaves the direct bitmap sample-family files absent.

## Next bounded step

Trim the next smallest shared Phase 9 reminder surface so it matches the same partial runtime bitmap packet already described here and in `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, starting with `samples/zigux/README.md`.