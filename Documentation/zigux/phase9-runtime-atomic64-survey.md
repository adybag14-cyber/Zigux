# Phase 9 Runtime Atomic64 Survey

This note tracks the bounded Phase 9 runtime atomic64 packet on current `master`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-atomic64-survey`
- `PHASE9_LANE_KEY=P9-L04`
- `PHASE9_SURVEYED_COMMIT=2026-05-21-runtime-atomic64-direct-packet-truthfulness`
- scope: direct atomic64 note-plus-test packet truthfulness together with the visible shared first-loadable reminder surfaces only

## Current Packet

Current `master` keeps these direct atomic64-facing packet files visible:

- `Documentation/zigux/phase9-runtime-atomic64-survey.md`
- `Documentation/zigux/phase9-runtime-atomic64-module-slice.md`
- `zigux/tests/runtime_atomic64_module.zig`
- `zigux/tests/runtime_atomic64_diff.zig`

Current `master` also keeps these adjacent shared reminder surfaces visible:

- `Documentation/zigux/phase9-first-loadable-runtime-module-parity.md`
- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
- `Documentation/zigux/README.md`
- `samples/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/tests/phase9_build.zig`

Trusted current-master reads in this runtime still do not return these family-local atomic64 files on the same path:

- `samples/zigux/runtime_atomic64.zig`
- `samples/zigux/runtime_atomic64_loader.zig`
- `zigux/tests/runtime_atomic64_survey.zig`
- `zigux/tests/runtime_atomic64_manifest.json`

Trusted current-master reads in this runtime also still do not return these deeper shared loader files on the same path:

- `Documentation/zigux/phase9-runtime-loader-gap-survey.md`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `zigux/tests/runtime_loader_gap_survey.zig`
- `zigux/tests/runtime_loader_selftest_complete_exit_parity.zig`
- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`

That means the honest current packet is still the direct atomic64 note-plus-test packet together with a visible shared reminder packet. It is not a completed loadable runtime-module path, it does not clear the broader runtime-substrate blocker, and it does not currently rematerialize the family-local sample, loader, survey, or manifest surfaces on the trusted read path used in this run.

## Routes

1. `zigux/tests/runtime_atomic64_module.zig` keeps the direct lifecycle packet reviewable.
2. `zigux/tests/runtime_atomic64_diff.zig` keeps the `lib/atomic64_test.c` operation families machine-checkable.
3. `zigux/tests/phase9_build.zig` keeps the direct `phase9-runtime-atomic64-diff` rerun explicit and keeps the build-local `phase9-runtime-atomic64-sample-tests` handle visible as reminder vocabulary; it does not currently materialize the missing family-local sample, loader, survey, or manifest files on the same trusted path.
4. No dedicated `make -C zigux phase9-runtime-atomic64-test` route is currently materialized on current `master`, so that family-local convenience handle stays backlog vocabulary instead of shipped make-route evidence.
5. `Documentation/zigux/phase9-first-loadable-runtime-module-parity.md`, `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/README.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, and `zigux/tests/phase9_build.zig` remain visible shared reminder surfaces, while the broader runtime substrate stays blocked and the deeper shared loader packet stays non-returned on the trusted read path used in this run.

## Boundaries

1. Keep this packet inside the direct atomic64 note-plus-test packet and the visible shared reminder surfaces.
2. Keep the shared reminder packet explicit as review-only evidence instead of treating it as completed live loader binding or proof that the broader runtime substrate already exists.
3. Keep lifecycle, selftest, and direct counter replay evidence visible without widening into scheduler-facing or workqueue-facing ownership.
4. Do not describe missing family-local sample, loader, survey, or manifest files as directly returned current-master evidence until a fresh trusted reread actually returns them.

## Freeze-Map Governance Evidence

- `Documentation/zigux/freeze-map.md` keeps `kernel/workqueue.c` in the study-only bucket, so this packet stays review-only beside that workqueue-facing boundary instead of claiming scheduler or workqueue delivery.
- No parity scorecard entry or Architecture Council status-change request is attached to this packet on current `master`.
- Any future freeze-map status change for this family must route through `Documentation/zigux/phase15-architecture-council-review-process.md` and `Documentation/zigux/phase15-freeze-map-governance.md` instead of being inferred from the landed atomic64 notes, direct test packet, or visible shared reminder packet.

## Recommended Next Step

Keep the next same-lane move inside one exact atomic64 packet truthfulness repair while the shared reminder packet remains visible review-only evidence and the broader runtime substrate is still blocked. If a future trusted reread returns the missing family-local sample, loader, survey, or manifest files, widen this note only to that newly returned packet and not beyond it.