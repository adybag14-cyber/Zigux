# Phase 9 Runtime Bitmap Survey

This note tracks the bounded Phase 9 runtime bitmap review packet under `samples/zigux/`.

## Status
- `PHASE9_STATUS=active`
- `PHASE9_LANE_KEY=P9-L08`
- `PHASE9_SURVEYED_COMMIT=66e60700501fc8bb08d645b081064c4698562427`
- scope: direct sample, diff gate, loader scaffold, top-bit companion replay, module gate, survey gate, manifest-backed ownership packet, and shared loader handoff plus shared build routes only

## Boundaries
- keep the runtime bitmap packet inside `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_diff.zig`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/runtime_bitmap_manifest.json`, and the shared `zigux/tests/phase9_build.zig` bundle
- keep the focused `zig build phase9-runtime-bitmap-top-bit-tests --build-file zigux/tests/phase9_build.zig` route explicit as the bitmap-local highest-valid-bit companion replay instead of flattening that proof into the broader family bundle alone
- keep the blocked shared runtime-loader substrate explicit
- do not claim loadable runtime bitmap module parity
- current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample
- keep the four directly readable Phase 5 reference anchors explicit here too: `samples/zigux/bytestream_fifo.zig`, `samples/zigux/kobject_example.zig`, `samples/zigux/kretprobe_example.zig`, and `samples/zigux/trace_events_sample.zig`
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
3. `zig build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig`
4. `zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig`

## Next Bounded Step

Keep the bounded runtime bitmap packet aligned with the visible sample, direct repeat-init rejection guard, dedicated top-bit companion replay route, diff gate, loader scaffold, survey gate, manifest-backed ownership packet, and shared build surfaces while the broader runtime substrate remains blocked.
