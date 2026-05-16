# Phase 9 Runtime Bitmap Survey

This note tracks the bounded Phase 9 runtime bitmap review packet under `samples/zigux/`.

## Status
- `PHASE9_STATUS=active`
- `PHASE9_LANE_KEY=P9-L08`
- `PHASE9_SURVEYED_COMMIT=6726fdd9da4eef55498fb06c38815317a684bcbf`
- scope: direct sample, sample-root summary, diff gate, loader scaffold, top-bit companion replay, module gate, survey gate, manifest-backed ownership packet, shared selftest-complete exit parity replay, and shared loader handoff plus shared build routes only

## Boundaries
- keep the runtime bitmap packet inside `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, `samples/zigux/README.md`, `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_diff.zig`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/runtime_bitmap_manifest.json`, `zigux/tests/runtime_loader_selftest_complete_exit_parity.zig`, and the shared `zigux/tests/phase9_build.zig` bundle
- keep `samples/zigux/README.md` explicit as the shared sample-root summary that still names the separate Phase 9 runtime bitmap family, the bitmap-local `phase9-runtime-bitmap-top-bit-tests` companion replay, and the shared `phase9-runtime-loader-shared-tests` boundary without recasting this packet as a fifth approved Phase 5 sample idiom
- keep the focused `zig build phase9-runtime-bitmap-top-bit-tests --build-file zigux/tests/phase9_build.zig` plus `make -C zigux phase9-runtime-bitmap-top-bit-test` route explicit as the bitmap-local highest-valid-bit companion replay instead of flattening that proof into the broader family bundle alone
- keep `zigux/tests/runtime_loader_selftest_complete_exit_parity.zig` explicit as the shared selftest-complete proof that a prepared bitmap request stays pinned even if the live sample later exits, so this packet stays review-only beside the blocked substrate instead of overclaiming loadable runtime parity
- keep the blocked shared runtime-loader substrate explicit
- do not claim loadable runtime bitmap module parity
- current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample
- keep the four directly readable Phase 5 reference anchors explicit here too: `samples/zigux/bytestream_fifo.zig`, `samples/zigux/kretprobe_example.zig`, `samples/zigux/trace_events_sample.zig`, and `samples/zigux/kobject_example.zig`
- keep the narrower Phase 5 kobject companion packet explicit here too: `Documentation/zigux/phase5-kobject-sample-survey.md`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json`
- keep `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig` explicit as the separate Phase 9 runtime bitmap family rather than a fifth approved Phase 5 sample idiom, and keep the direct repeat-init rejection state-preservation proof in `samples/zigux/runtime_bitmap.zig` visible as part of that bounded sample packet
- keep the focused `phase9-runtime-bitmap-tests` route explicit as the shared build packet that now bundles the sample, module, diff, loader, top-bit, survey, and shared loader-adjacent replay surfaces without implying live runtime substrate parity

## Roadmap Gap
- the Phase 9 roadmap target is still `first loadable Zigux runtime modules with selftest hooks and runtime module lifecycle parity`
- the current runtime bitmap packet is still `starter_landed_without_loadable_runtime_substrate`: the sample starter, diff gate, survey gate, top-bit companion replay, and loader scaffold are visible, but the shared runtime substrate is still missing
- the blocked deliverable remains `loadable Phase 9 runtime bitmap pilot module parity`

## Gates
1. `zig test zigux/tests/runtime_bitmap_survey.zig`
2. `zig build phase9-runtime-bitmap-top-bit-tests --build-file zigux/tests/phase9_build.zig`
3. `make -C zigux phase9-runtime-bitmap-top-bit-test`
4. `zig build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig`
5. `zig build phase9-runtime-loader-selftest-complete-exit-parity-tests --build-file zigux/tests/phase9_build.zig`
6. `zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig`
7. `make -C zigux phase9-runtime-loader-shared-tests`
8. `make -C zigux phase9`

## Next Bounded Step

Keep the bounded runtime bitmap packet aligned with the visible sample, sample-root summary, direct repeat-init rejection guard, dedicated top-bit companion replay route, diff gate, loader scaffold, shared selftest-complete exit parity replay, survey gate, manifest-backed ownership packet, and shared build surfaces while the broader runtime substrate remains blocked.
