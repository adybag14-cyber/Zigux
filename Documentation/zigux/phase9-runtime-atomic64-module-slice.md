# Phase 9 Runtime Atomic64 Module Slice

This note tracks the bounded Phase 9 runtime atomic64 starter packet on `master`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-atomic64-module-starter`
- `PHASE9_LANE_KEY=P9-L04`
- `PHASE9_SURVEYED_COMMIT=ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`
- scope: selftest hook surface, guarded lifecycle parity evidence, bounded loader-handoff scaffold, shared request-surface proof, dedicated runtime survey gate, survey-note ownership closure, and survey-manifest closure only

## Product Boundary

- `samples/zigux/runtime_atomic64.zig`
- `samples/zigux/runtime_atomic64_loader.zig`
- `zigux/tests/runtime_atomic64_module.zig`
- `zigux/tests/runtime_atomic64_diff.zig`
- `zigux/tests/runtime_atomic64_survey.zig`
- `zigux/tests/runtime_atomic64_manifest.json`
- `Documentation/zigux/phase9-runtime-atomic64-survey.md`
- `zigux/tests/phase9_build.zig`
- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `zigux/Makefile`

## Why This Slice Exists

The direct starter now keeps the selftest hook surface and guarded lifecycle parity evidence visible around `lib/atomic64_test.c` without claiming a real loadable runtime module.

The bounded loader-handoff scaffold under `samples/zigux/runtime_atomic64_loader.zig` keeps `toSharedLoadPlan()` and `runtime_loader.prepareRequest()` explicit, while the real runtime substrate remains unavailable.

The shared `zigux/kernel/runtime_loader.zig` facade stays a review-only Phase 9 handoff packet under the freeze map's study-only `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` boundary, so the starter keeps the shared request path explicit without implying scheduler-facing substrate closure or a freeze-map status change.

## Gates

1. `zig build phase9-runtime-atomic64-tests --build-file zigux/tests/phase9_build.zig`
2. `zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig`
3. `make -C zigux phase9-runtime-loader-shared-tests`
4. `make -C zigux phase9`

## Review Surface

- `samples/zigux/runtime_atomic64.zig` keeps the direct starter and selftest hook surface explicit.
- `samples/zigux/runtime_atomic64_loader.zig` keeps the bounded loader-handoff scaffold and shared request-surface proof explicit.
- `zigux/tests/runtime_atomic64_module.zig`, `zigux/tests/runtime_atomic64_diff.zig`, and the dedicated runtime survey gate in `zigux/tests/runtime_atomic64_survey.zig` keep the sample-backed packet machine-checkable.
- `Documentation/zigux/phase9-runtime-atomic64-survey.md` and `zigux/tests/runtime_atomic64_manifest.json` keep survey-note ownership closure and survey-manifest closure only.
- `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/tests/phase9_build.zig`, and `zigux/Makefile` keep the shared review packet adjacent without widening the atomic64 claim.

## Non-goals

- No claim that the real runtime substrate is available.
- No claim of scheduler-facing or workqueue parity.
- No claim of full loadable module lifecycle parity before the shared runtime substrate lands.

## Next Bounded Step

Keep future follow-through inside the landed survey-backed starter packet until the shared runtime substrate can actually consume the atomic64 handoff plan.
