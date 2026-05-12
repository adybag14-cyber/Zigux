# Phase 9 Runtime Atomic64 Survey

This note tracks the bounded Phase 9 runtime atomic64 packet on current `master`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-atomic64-survey`
- `PHASE9_LANE_KEY=P9-L04`
- `PHASE9_SURVEYED_COMMIT=ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`
- scope: direct atomic64 sample, module gate, diff gate, survey gate, bounded loader scaffold, shared request-surface proof, and the adjacent review-only shared loader-facing packet only

## Current Packet

Current `master` keeps these direct atomic64 packet files visible:

- `samples/zigux/runtime_atomic64.zig`
- `zigux/tests/runtime_atomic64_module.zig`
- `zigux/tests/runtime_atomic64_diff.zig`
- `zigux/tests/runtime_atomic64_survey.zig`
- `samples/zigux/runtime_atomic64_loader.zig`
- `Documentation/zigux/phase9-runtime-atomic64-module-slice.md`
- `zigux/tests/runtime_atomic64_manifest.json`

Current `master` also keeps these adjacent shared loader-facing review surfaces visible:

- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `zigux/tests/phase9_build.zig`
- `zigux/Makefile`

That means the honest current packet is a direct atomic64 sample, lifecycle, diff, survey, and bounded loader-scaffold packet plus the adjacent review-only shared loader-facing packet, not a completed loadable runtime-module path.

## Routes

1. `zig build phase9-runtime-atomic64-tests --build-file zigux/tests/phase9_build.zig`
2. `zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig`
3. `make -C zigux phase9-runtime-loader-shared-tests`
4. `make -C zigux phase9`

## Boundaries

1. Keep this packet inside the direct atomic64 starter, module gate, diff gate, survey gate, bounded loader scaffold, and adjacent shared loader-facing review surfaces.
2. Keep the shared runtime substrate blocker explicit instead of implying loadable runtime parity.
3. Keep lifecycle, selftest, shared-request snapshot, and bounded counter replay evidence visible without widening into scheduler-facing or workqueue-facing ownership.

## Recommended Next Step

Keep the next same-lane move inside one exact survey-backed direct-packet or adjacent shared-loader truthfulness repair while the shared runtime substrate remains blocked.
