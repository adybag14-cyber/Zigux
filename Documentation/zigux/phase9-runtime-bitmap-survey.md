# Phase 9 Runtime Bitmap Survey

This note tracks the bounded Phase 9 runtime bitmap reminder packet.

## Status
- `PHASE9_STATUS=active`
- `PHASE9_LANE_KEY=P9-L08`
- `PHASE9_SURVEYED_COMMIT=2026-05-21-runtime-bitmap-manifest-restored`
- scope: partial reminder packet, direct sample proof, direct loader proof, manifest-backed ownership packet, top-bit companion proof, and blocked module-side follow-through only

## Current repo reality
- trusted current-tree contents reads on 2026-05-21 do materialize `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `zigux/tests/runtime_bitmap_manifest.json`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/phase9_build.zig`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig`
- the same trusted read path still returns missing for `zigux/tests/runtime_bitmap_module.zig` and `zigux/tests/runtime_bitmap_diff.zig`
- keep `zigux/tests/phase9_build.zig` explicit only as a bounded Phase 9 build bundle whose live body reruns the direct sample, loader, survey, and top-bit proofs; do not treat that bundle alone as proof that the broader runtime bitmap packet returned or that the missing module and diff legs returned
- current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample

## Boundaries
- keep the visible bitmap-side reminder packet inside `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `zigux/tests/runtime_bitmap_manifest.json`, `zigux/tests/runtime_bitmap_survey.zig`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, and the shared `zigux/tests/phase9_build.zig` bundle
- keep the blocked shared runtime-loader substrate explicit
- do not claim loadable runtime bitmap module parity
- do not present the partial bitmap packet as proof that the broader shared runtime-loader packet returned
- keep `zigux/tests/runtime_bitmap_module.zig` and `zigux/tests/runtime_bitmap_diff.zig` framed as same-lane repo-reality gaps until the trusted current-tree read path returns them directly again
- keep the focused `phase9-runtime-bitmap-tests` route name framed only as a bounded rerun handle for the visible sample, loader, survey, and top-bit packet while the module and diff legs stay absent on the trusted path

## Roadmap gap
- the Phase 9 roadmap target is still `first loadable Zigux runtime modules with selftest hooks and runtime module lifecycle parity`
- the current runtime bitmap reminder packet is still `partial_packet_without_module_and_diff_follow_through`: the survey note, module-slice note, manifest-backed ownership packet, survey gate, bounded build bundle, direct sample, direct loader companion, and top-bit companion proof are visible, but the module gate, diff gate, and broader shared runtime-loader substrate are not currently materialized on the trusted path
- the blocked deliverable remains `loadable Phase 9 runtime bitmap pilot module parity`

## Gates
1. `zig test zigux/tests/runtime_bitmap_survey.zig`
2. `zig test samples/zigux/runtime_bitmap.zig`
3. `zig test samples/zigux/runtime_bitmap_loader.zig`
4. `zig test samples/zigux/runtime_bitmap_top_bit_contract.zig`

Treat the shared `zigux/tests/phase9_build.zig` bitmap route names as bounded rerun handles for the visible sample, loader, survey, and top-bit packet only while the module and diff legs remain absent.

## Next bounded step

Advance to the next smallest module-side bitmap proof surface, starting with `zigux/tests/runtime_bitmap_module.zig`, only if the same trusted read path returns a coherent module-side packet again.
