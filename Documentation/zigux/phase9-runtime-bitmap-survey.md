# Phase 9 Runtime Bitmap Survey

This note tracks the bounded Phase 9 runtime bitmap review packet under `samples/zigux/`.

## Status
- `PHASE9_STATUS=active`
- `PHASE9_LANE_KEY=P9-L08`
- `PHASE9_SURVEYED_COMMIT=00b92f22991e9124aefb308d7eb0e90f14923338`
- scope: direct sample, loader scaffold, top-bit companion replay, module gate, survey gate, and shared loader handoff packet only

## Boundaries
- keep the runtime bitmap packet inside `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_survey.zig`, and the shared `zigux/tests/phase9_build.zig` bundle
- keep the blocked shared runtime-loader substrate explicit
- do not claim loadable runtime bitmap module parity
- current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample
- keep the four approved Phase 5 reference anchors explicit here too: `samples/zigux/bytestream_fifo.zig`, `samples/zigux/kobject_example.zig`, `samples/zigux/kretprobe_example.zig`, and `samples/zigux/trace_events_sample.zig`
- keep `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig` explicit as the separate Phase 9 runtime bitmap family rather than a fifth approved Phase 5 sample idiom

## Gates
1. `zig test zigux/tests/runtime_bitmap_survey.zig`
2. `zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig`
3. `make -C zigux phase9-runtime-loader-shared-tests`
4. `make -C zigux phase9`

## Next Bounded Step

Keep the bounded runtime bitmap packet aligned with the visible sample, loader, top-bit companion, manifest, and shared build surfaces while the broader runtime substrate remains blocked.
