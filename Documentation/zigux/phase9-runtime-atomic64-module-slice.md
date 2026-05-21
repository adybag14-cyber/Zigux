# Phase 9 Runtime Atomic64 Module Slice

This note tracks the bounded Phase 9 runtime atomic64 starter packet on `master`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-atomic64-module-starter`
- `PHASE9_LANE_KEY=P9-L04`
- `PHASE9_SURVEYED_COMMIT=2026-05-21-runtime-atomic64-direct-packet-truthfulness`
- scope: selftest-hook and guarded lifecycle reviewability through the direct atomic64 note-plus-test packet, plus the adjacent shared reminder surfaces only

## Direct Packet

- `Documentation/zigux/phase9-runtime-atomic64-survey.md`
- `Documentation/zigux/phase9-runtime-atomic64-module-slice.md`
- `zigux/tests/runtime_atomic64_module.zig`
- `zigux/tests/runtime_atomic64_diff.zig`

## Adjacent Shared Reminder Packet

- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
- `Documentation/zigux/phase9-first-loadable-runtime-module-parity.md`
- `Documentation/zigux/README.md`
- `samples/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/tests/phase9_build.zig`

These shared reminder surfaces are still review-only evidence on current `master`, and the direct atomic64 packet is narrower than the older loader-facing wording implied. Fresh exact rereads in this runtime still return missing for `samples/zigux/runtime_atomic64.zig`, `samples/zigux/runtime_atomic64_loader.zig`, `zigux/tests/runtime_atomic64_survey.zig`, `zigux/tests/runtime_atomic64_manifest.json`, `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/tests/runtime_loader_gap_survey.zig`, `zigux/tests/runtime_loader_selftest_complete_exit_parity.zig`, `zigux/kernel/runtime_loader.zig`, and `zigux/kernel/runtime_loader_contract.zig` on the same trusted path used in this run.

That means the honest current atomic64 packet is the direct note-plus-test packet together with a bounded shared-reminder packet. It is not a completed loadable runtime-module path, it still does not clear the blocked runtime substrate, and it should not be described as if the family-local sample, loader, survey, manifest, or deeper shared loader files had already returned directly on current `master`.

## Why This Slice Exists

The direct packet keeps the selftest hook surface and guarded lifecycle parity evidence visible around `lib/atomic64_test.c` without claiming a real loadable runtime module.
The direct packet also keeps the five-family operation replay explicit through `zigux/tests/runtime_atomic64_diff.zig` and the lifecycle boundary proofs explicit through `zigux/tests/runtime_atomic64_module.zig`.
The adjacent shared reminder packet keeps the current cross-family and shared-owner wording reviewable through the lane-sequencing, first-loadable parity, docs-root, sample-root, tests-root, and `phase9_build` reminder surfaces, but it remains review-only evidence while the broader runtime substrate stays blocked.
That means the honest current atomic64 packet is a direct note-plus-test packet plus a bounded shared-reminder packet, not a completed loadable runtime-module path.

## Gates

1. `zigux/tests/runtime_atomic64_module.zig` remains the dedicated lifecycle gate for the direct packet.
2. `zigux/tests/runtime_atomic64_diff.zig` remains the narrow differential gate against `lib/atomic64_test.c`.
3. No dedicated family-local survey gate or manifest file currently returns on the trusted current-master path used in this run, so `zigux/tests/runtime_atomic64_survey.zig` and `zigux/tests/runtime_atomic64_manifest.json` stay same-family repo-reality gaps instead of active direct packet members here.
4. No dedicated `make -C zigux phase9-runtime-atomic64-test` route is currently materialized on current `master`, so that family-local convenience handle stays backlog vocabulary instead of shipped make-route evidence.
5. `zigux/tests/phase9_build.zig` currently keeps the direct `phase9-runtime-atomic64-diff` rerun and the build-local `phase9-runtime-atomic64-sample-tests` handle explicit; it still does not currently expose returned family-local sample, loader, survey, manifest, or aggregate route proof on the same trusted path used in this run.
6. `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/phase9-first-loadable-runtime-module-parity.md`, `Documentation/zigux/README.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, and `zigux/tests/phase9_build.zig` stay adjacent mixed-source review surfaces only until the broader runtime substrate and family-local atomic64 packet actually return together.

## Review Surface

- `zigux/tests/runtime_atomic64_module.zig` and `zigux/tests/runtime_atomic64_diff.zig` keep the direct packet machine-checkable.
- `Documentation/zigux/phase9-runtime-atomic64-survey.md` keeps the packet truthfulness explicit, including the missing family-local sample, loader, survey, manifest, and deeper shared loader files on the trusted read path used in this run.
- Shared reminder evidence for the broader backlog now lives across `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/phase9-first-loadable-runtime-module-parity.md`, `Documentation/zigux/README.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, and `zigux/tests/phase9_build.zig` rather than being treated as proof that the deeper family-local or shared loader packet already returned directly.

## Freeze-Map Governance Boundary

- `Documentation/zigux/freeze-map.md` still keeps `kernel/workqueue.c` in the study-only bucket, so this slice stays review-only beside that workqueue-facing boundary instead of claiming scheduler or workqueue parity.
- No parity scorecard entry or Architecture Council status-change request is attached to this slice on current `master`.
- Any future freeze-map status change for this family must route through `Documentation/zigux/phase15-architecture-council-review-process.md` and `Documentation/zigux/phase15-freeze-map-governance.md` instead of being inferred from this family-local packet.

## Non-goals

- No claim that the real runtime substrate is available.
- No claim of scheduler-facing or workqueue parity.
- No claim of full loadable module lifecycle parity before the shared runtime substrate lands.
- No claim that the bounded shared reminder packet is the same thing as a completed live loader binding.
- No claim that missing family-local sample, loader, survey, or manifest files are already direct current-master evidence.

## Next Bounded Step

Keep future follow-through inside one exact atomic64 packet truthfulness repair. The strongest next candidate remains whichever family-local survey, manifest, sample, or loader surface returns first on a future trusted reread, because that is the smallest safe way to widen this slice without overstating current repo reality.