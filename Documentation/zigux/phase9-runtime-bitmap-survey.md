# Phase 9 Runtime Bitmap Survey

This note tracks the bounded Phase 9 runtime bitmap reminder packet.

## Status
- `PHASE9_STATUS=active`
- `PHASE9_LANE_KEY=P9-L08`
- `PHASE9_SURVEYED_COMMIT=2026-05-22-runtime-bitmap-diff-returned`
- scope: partial reminder packet, direct sample proof, direct direct-init companion proof, direct cold-stage guard proof, direct loader proof, direct module proof, direct diff proof, manifest-backed ownership packet, top-bit and active-word-boundary companion proof, and no broader runtime-loader parity claim

## Current repo reality
- trusted current-tree contents reads on 2026-05-22 do materialize `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `zigux/tests/runtime_bitmap_manifest.json`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_diff.zig`, `zigux/tests/phase9_build.zig`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_cold_stage_guard.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig`
- trusted current-tree contents reads on 2026-05-25 also materialize `samples/zigux/runtime_bitmap_direct_init_contract.zig` as a bounded direct-init normalization companion for the same Phase 9 packet
- the top-bit companion now also keeps active word-width boundary bits explicit by deriving the second-word tail, second-word start, and sparse follow-on bit from `RuntimeBitmapSample.bitmap_nbits` instead of treating only the highest valid bit as reviewable
- keep `zigux/tests/phase9_build.zig` explicit only as a bounded Phase 9 build bundle whose live body reruns the direct sample, direct-init companion, cold-stage guard, loader, module, survey, diff, and top-bit proofs; that bundle still does not prove the broader runtime bitmap packet or shared runtime-loader parity
- keep `zigux/Makefile` explicit as the narrow wrapper rerun handle for the same packet: current `master` now exposes `phase9-runtime-bitmap-test`, and that wrapper still shells into `zig build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig --summary all` rather than proving the broader runtime bitmap packet or shared runtime-loader parity
- current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample
- keep the runtime bitmap family Phase 9 only; it is not one of the four approved Phase 5 reference samples.
- Keep the direct sample zero-length and rejected range-mutation replay explicit when reminder text summarizes sample-local range, summary, and parse stability.
- Keep the direct sample whitespace-only bit-list path explicit as an initialized empty bitmap plus direct-exit guard when reminder text summarizes sample-local parse, summary, and lifecycle stability.
- Keep the direct sample duplicate bit-list normalization, malformed-bit-list cold-state rejection, and re-selftest or re-init summary-stability guards explicit when reminder text summarizes the returned bitmap sample packet, rather than leaving those newer direct-sample checks implied only by the manifest-backed ownership packet.
- Keep the direct-init companion explicit when reminder text summarizes sample-local init normalization, unsorted duplicate input collapse, nth-set ordering, and formatted sparse-summary stability.
- Keep `samples/zigux/runtime_bitmap_cold_stage_guard.zig` explicit as the returned cold-stage sample-root guard companion; it is visible on the trusted path and the shared `zigux/tests/phase9_build.zig` bundle now reruns it through the dedicated `phase9-runtime-bitmap-cold-stage-guard-tests` route plus the aggregate `phase9-runtime-bitmap-tests` handle.
- Keep the loader empty-payload direct-exit guard plus the newer loader re-init, re-selftest, direct-exit summary-stability, and rejected re-exit rollback guards explicit when reminder text summarizes runtime lifecycle evidence for the returned bitmap packet.

## Boundaries
- keep the visible bitmap-side reminder packet inside `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `zigux/tests/runtime_bitmap_manifest.json`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_diff.zig`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_direct_init_contract.zig`, `samples/zigux/runtime_bitmap_cold_stage_guard.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, the shared `zigux/tests/phase9_build.zig` bundle, and the narrow `zigux/Makefile` wrapper
- keep the blocked shared runtime-loader substrate explicit
- do not claim loadable runtime bitmap module parity
- do not present the visible bitmap packet as proof that the broader shared runtime-loader packet returned
- keep the focused `phase9-runtime-bitmap-tests` route name and the narrower `phase9-runtime-bitmap-test` Makefile wrapper framed only as bounded rerun handles for the visible sample, direct-init companion, cold-stage guard, loader, module, survey, diff, and top-bit packet

## Roadmap gap
- the Phase 9 roadmap target is still `first loadable Zigux runtime modules with selftest hooks and runtime module lifecycle parity`
- the current runtime bitmap reminder packet is still `partial_packet_with_diff_but_without_broader_runtime_loader_parity`: the survey note, module-slice note, manifest-backed ownership packet, survey gate, bounded build bundle, direct sample, direct-init normalization companion, direct cold-stage guard companion, direct loader companion, direct module proof, direct diff proof, and top-bit plus active-word-boundary companion proof are visible, but the broader shared runtime-loader substrate is still only partially materialized on the trusted path
- the blocked deliverable remains `loadable Phase 9 runtime bitmap pilot module parity`

## Gates
1. `zig test zigux/tests/runtime_bitmap_survey.zig`
2. `zig test zigux/tests/runtime_bitmap_module.zig`
3. `zig test zigux/tests/runtime_bitmap_diff.zig`
4. `zig test samples/zigux/runtime_bitmap.zig`
5. `zig test samples/zigux/runtime_bitmap_cold_stage_guard.zig`
6. `zig test samples/zigux/runtime_bitmap_loader.zig`
7. `zig test samples/zigux/runtime_bitmap_top_bit_contract.zig`
8. `zig test samples/zigux/runtime_bitmap_direct_init_contract.zig`
9. `zig build phase9-runtime-bitmap-cold-stage-guard-tests --build-file zigux/tests/phase9_build.zig`
10. `make -C zigux phase9-runtime-bitmap-test`

Treat the shared `zigux/tests/phase9_build.zig` bitmap route names plus the narrow `zigux/Makefile` wrapper as bounded rerun handles for the visible sample, direct-init companion, cold-stage guard, loader, module, survey, diff, and top-bit packet only while the broader shared runtime-loader family remains partial.

## Next bounded step

Replay `zig build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig` on a fresh full checkout and fix only the next bitmap-local compile or note drift it exposes, leaving broader shared runtime-loader follow-through to the separate shared-owner packet.
