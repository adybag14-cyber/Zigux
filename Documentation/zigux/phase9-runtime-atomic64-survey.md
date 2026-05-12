# Phase 9 Runtime Atomic64 Survey

This note tracks the bounded Phase 9 runtime atomic64 packet on current `master`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-atomic64-survey`
- `PHASE9_LANE_KEY=P9-L04`
- `PHASE9_SURVEYED_COMMIT=ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`
- scope: direct atomic64 sample, module gate, diff gate, survey gate, bounded loader scaffold, and the current blocked readback state of the shared loader-facing packet only

## Current Packet

Current `master` keeps these direct atomic64 packet files visible:

- `samples/zigux/runtime_atomic64.zig`
- `samples/zigux/runtime_atomic64_loader.zig`
- `zigux/tests/runtime_atomic64_module.zig`
- `zigux/tests/runtime_atomic64_diff.zig`
- `zigux/tests/runtime_atomic64_survey.zig`
- `zigux/tests/runtime_atomic64_manifest.json`
- `Documentation/zigux/phase9-runtime-atomic64-module-slice.md`

Current `master` also keeps these adjacent shared-loader scaffolds visible:

- `zigux/tests/phase9_build.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `zigux/Makefile`

Current reads for these intended shared runtime-loader files return missing-file results:

- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`

That means the honest current packet is a direct atomic64 sample, module, diff, survey, and bounded loader-scaffold packet plus stale adjacent shared-loader scaffolds, not a replayable shared-loader route and not a completed loadable runtime-module path.

## Routes

1. `zigux/tests/runtime_atomic64_module.zig` keeps the direct lifecycle packet reviewable.
2. `zigux/tests/runtime_atomic64_diff.zig` keeps the `lib/atomic64_test.c` operation families machine-checkable.
3. `zigux/tests/runtime_atomic64_survey.zig` keeps the direct packet plus the missing shared-loader readback fail-closed.
4. `zigux/tests/phase9_build.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, and `zigux/Makefile` remain adjacent stale scaffolds until `zigux/kernel/runtime_loader.zig` and `zigux/kernel/runtime_loader_contract.zig` are readable again on current `master`.

## Boundaries

1. Keep this packet inside the direct atomic64 starter, module gate, diff gate, survey gate, and bounded loader scaffold.
2. Keep the current missing-file state of `zigux/kernel/runtime_loader.zig` and `zigux/kernel/runtime_loader_contract.zig` explicit instead of implying a replayable shared-loader route.
3. Keep lifecycle, selftest, and direct counter replay evidence visible without widening into scheduler-facing or workqueue-facing ownership.

## Recommended Next Step

Keep the next same-lane move inside one exact atomic64 packet truthfulness repair while the shared runtime-loader files remain unreadable on current `master`.