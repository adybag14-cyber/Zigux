# Phase 9 Runtime Atomic64 Module Slice

This note tracks the bounded Phase 9 runtime atomic64 starter packet on `master`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-atomic64-module-starter`
- `PHASE9_LANE_KEY=P9-L04`
- `PHASE9_SURVEYED_COMMIT=ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`
- scope: selftest hook surface, guarded lifecycle parity evidence, direct atomic64 starter packet truthfulness, bounded loader-scaffold review only, and dedicated survey-note plus manifest closure only

## Direct Packet

- `samples/zigux/runtime_atomic64.zig`
- `samples/zigux/runtime_atomic64_loader.zig`
- `zigux/tests/runtime_atomic64_module.zig`
- `zigux/tests/runtime_atomic64_diff.zig`
- `zigux/tests/runtime_atomic64_survey.zig`
- `zigux/tests/runtime_atomic64_manifest.json`
- `Documentation/zigux/phase9-runtime-atomic64-survey.md`

## Adjacent Stale Shared Loader-Facing Scaffolds

- `zigux/tests/phase9_build.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `zigux/Makefile`
- current reads for `zigux/kernel/runtime_loader.zig` and `zigux/kernel/runtime_loader_contract.zig` return missing-file results on `master`, so this lane keeps those shared loader-facing files in a blocked posture instead of counting them as visible current-packet evidence

## Why This Slice Exists

The direct starter keeps the selftest hook surface and guarded lifecycle parity evidence visible around `lib/atomic64_test.c` without claiming a real loadable runtime module.

The bounded loader scaffold under `samples/zigux/runtime_atomic64_loader.zig` still keeps the intended entry symbol, exit symbol, and handoff-plan shape reviewable, but the shared runtime-loader files it points at are not currently readable on `master`.

That means the honest current atomic64 packet is a direct starter plus a stale adjacent shared-loader scaffold, not a replayable shared-loader route and not a completed loadable runtime-module path.

## Gates

1. `zigux/tests/runtime_atomic64_module.zig` remains the dedicated lifecycle gate for the direct starter packet.
2. `zigux/tests/runtime_atomic64_diff.zig` remains the narrow differential gate against `lib/atomic64_test.c`.
3. `zigux/tests/runtime_atomic64_survey.zig` remains the truthfulness gate for the direct packet and the blocked shared-loader readback.
4. `zigux/tests/phase9_build.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, and `zigux/Makefile` stay adjacent scaffolds only until `zigux/kernel/runtime_loader.zig` and `zigux/kernel/runtime_loader_contract.zig` are readable again on current `master`.

## Review Surface

- `samples/zigux/runtime_atomic64.zig` keeps the direct starter and selftest hook surface explicit.
- `zigux/tests/runtime_atomic64_module.zig`, `zigux/tests/runtime_atomic64_diff.zig`, and `zigux/tests/runtime_atomic64_survey.zig` keep the direct packet machine-checkable.
- `Documentation/zigux/phase9-runtime-atomic64-survey.md` and `zigux/tests/runtime_atomic64_manifest.json` keep the packet truthfulness explicit, including the current missing-file state of the shared runtime-loader files.
- `samples/zigux/runtime_atomic64_loader.zig` remains a bounded loader scaffold only; it does not currently prove a replayable shared runtime-loader route.

## Non-goals

- No claim that the real runtime substrate is available.
- No claim of scheduler-facing or workqueue parity.
- No claim of full loadable module lifecycle parity before the shared runtime substrate lands.
- No claim that the shared runtime-loader packet is currently readable on `master`.

## Next Bounded Step

Keep future follow-through inside the landed direct atomic64 packet until either the shared runtime-loader files return to readable current-master state or the adjacent shared scaffolds are retold to the same blocked posture across their own lane.