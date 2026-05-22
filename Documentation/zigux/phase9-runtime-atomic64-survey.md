# Phase 9 Runtime Atomic64 Survey

This note tracks the bounded Phase 9 runtime atomic64 packet on current `master`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-atomic64-survey`
- `PHASE9_LANE_KEY=P9-L04`
- `PHASE9_SURVEYED_COMMIT=9f8c05368242414084e4bc94ea979604c2b6b712`
- scope: direct atomic64 starter truthfulness together with the visible shared-loader reminder surfaces only

## Current Packet

Current `master` keeps these direct atomic64-facing packet files visible:

- `Documentation/zigux/phase9-runtime-atomic64-survey.md`
- `Documentation/zigux/phase9-runtime-atomic64-module-slice.md`
- `samples/zigux/runtime_atomic64.zig`
- `zigux/tests/runtime_atomic64_module.zig`
- `zigux/tests/runtime_atomic64_diff.zig`
- `zigux/tests/runtime_atomic64_survey.zig`
- `zigux/tests/runtime_atomic64_manifest.json`

Current `master` also keeps these shared-loader reminder surfaces visible:

- `Documentation/zigux/phase9-first-loadable-runtime-module-parity.md`
- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
- `Documentation/zigux/README.md`
- `samples/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/tests/phase9_build.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `zigux/tests/runtime_loader_gap_survey.zig`
- `zigux/tests/runtime_loader_selftest_complete_exit_parity.zig`
- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/Makefile`

That means the honest current packet is the direct atomic64 starter packet together with a visible shared-loader reminder packet. The shared-loader reminder surfaces visible here keep the broader runtime-substrate blocker explicit, so this packet is still not a completed loadable runtime-module path.

## Routes

1. `zigux/tests/runtime_atomic64_module.zig` keeps the direct lifecycle packet reviewable.
2. `zigux/tests/runtime_atomic64_diff.zig` keeps the `lib/atomic64_test.c` operation families machine-checkable.
3. `zigux/tests/runtime_atomic64_survey.zig` and `zigux/tests/runtime_atomic64_manifest.json` keep the direct sample leg, note packet, and exact bounded blocker wording fail-closed.
4. `zigux/tests/phase9_build.zig` keeps `phase9-runtime-atomic64-diff`, `phase9-runtime-atomic64-module-tests`, `phase9-runtime-atomic64-sample-tests`, `phase9-runtime-atomic64-tests`, and `phase9-runtime-loader-shared-tests` explicit, including `zig build phase9-runtime-atomic64-sample-tests --build-file zigux/tests/phase9_build.zig`.
5. The shared Phase 9 reminder packet keeps the broader runtime-substrate blocker explicit instead of being treated as proof that the missing runtime substrate has already landed.

## Loader Reminder Evidence

The visible shared-loader reminder packet keeps a prepared `RuntimeAtomic64LoadSummary` snapshot reviewable without claiming live loader binding. The packet keeps the anchor, checked operation families, counter snapshot, and selftest-run count reviewable even when later counter mutation, later selftest activity, or later exit activity changes the live sample.

The same shared-loader reminder packet also keeps the prepared shared selftest-hook drift guard explicit, the paired shared-release desynchronization proofs explicit, and the direct shared runtime-load transition guard that keeps the loader stage and shared release state synchronized even if the shared request advances before the loader-owned release path runs.

## Boundaries

1. Keep this packet inside the direct atomic64 starter packet and the visible shared-loader reminder surfaces only.
2. Keep the visible shared-loader reminder packet explicit as review-only evidence instead of treating it as completed live loader binding or proof that the broader runtime substrate already exists.
3. Keep lifecycle, selftest, and direct counter replay evidence visible without widening into scheduler-facing or workqueue-facing ownership.
4. Do not describe the visible loader reminder packet as shipped end-to-end runtime-module parity while the broader runtime substrate remains the blocker recorded in the manifest.

## Freeze-Map Governance Evidence

- `Documentation/zigux/freeze-map.md` keeps `kernel/workqueue.c` in the study-only bucket, so this packet stays review-only beside that workqueue-facing boundary instead of claiming scheduler or workqueue delivery.
- No parity scorecard entry or Architecture Council status-change request is attached to this packet on current `master`.
- Any future freeze-map status change for this family must route through `Documentation/zigux/phase15-architecture-council-review-process.md` and `Documentation/zigux/phase15-freeze-map-governance.md` instead of being inferred from the landed atomic64 notes, starter packet, or visible shared-loader reminder packet.

## Recommended Next Step

Keep the next same-lane move inside one exact atomic64 packet truthfulness repair while the visible shared-loader reminder packet remains review-only evidence and the broader runtime-substrate blocker is still explicit. The best next same-lane target is whichever direct atomic64 note, manifest, survey, or loader-reminder assertion drifts first against the current direct sample leg and visible shared-loader reminder packet.
