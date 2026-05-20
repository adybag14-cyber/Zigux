# Phase 9 Runtime Atomic64 Module Slice

This note tracks the bounded Phase 9 runtime atomic64 starter packet on `master`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-atomic64-module-starter`
- `PHASE9_LANE_KEY=P9-L04`
- `PHASE9_SURVEYED_COMMIT=2026-05-20-runtime-atomic64-module-build-route-truthfulness`
- scope: selftest hook surface, guarded lifecycle parity evidence, direct atomic64 starter packet truthfulness, bounded loader-scaffold review only, and dedicated survey-note plus manifest closure only

## Direct Packet

- `samples/zigux/runtime_atomic64.zig`
- `samples/zigux/runtime_atomic64_loader.zig`
- `zigux/tests/runtime_atomic64_module.zig`
- `zigux/tests/runtime_atomic64_diff.zig`
- `zigux/tests/runtime_atomic64_survey.zig`
- `zigux/tests/runtime_atomic64_manifest.json`
- `Documentation/zigux/phase9-runtime-atomic64-survey.md`

## Adjacent Shared Reminder Packet

- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
- `Documentation/zigux/phase9-first-loadable-runtime-module-parity.md`
- `Documentation/zigux/phase9-runtime-loader-gap-survey.md`
- `scripts/zigux/check-phase9-build-only-surface.py`
- `.github/workflows/zigux-bootstrap.yml`
- `zigux/tests/phase9_build.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `zigux/tests/runtime_loader_selftest_complete_exit_parity.zig`
- `zigux/tests/runtime_loader_gap_survey.zig`
- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/Makefile`

These shared reminder surfaces are still review-only evidence on current `master`, but the honest packet is now broader than the older three-file shorthand. Fresh exact rereads show a mixed-source reminder packet: `zigux/tests/phase9_build.zig` now keeps both the direct `phase9-runtime-atomic64-diff` rerun and the family-local `phase9-runtime-atomic64-sample-tests` handle explicit, while the broader loader-facing reminder packet also stays visible through the sequencing note, first-loadable parity survey, loader-gap survey, workflow and build-only checker, allocator/init-flow and selftest-complete parity proofs, deeper loader survey replay, fallback-readable kernel loader files, and `zigux/Makefile`.

That broader mixed-source reminder packet still does not turn this family-local slice into a completed loadable runtime-module path, and it still does not clear the blocked runtime-substrate or dedicated family-local make-route gaps.

## Why This Slice Exists

The direct starter keeps the selftest hook surface and guarded lifecycle parity evidence visible around `lib/atomic64_test.c` without claiming a real loadable runtime module.
The bounded loader scaffold under `samples/zigux/runtime_atomic64_loader.zig` still keeps the intended entry symbol, exit symbol, and handoff-plan shape reviewable.
It also keeps the prepared `RuntimeAtomic64LoadSummary` snapshot reviewable: once `prepare()` captures the anchor, checked operation families, counter snapshot, and selftest-run count, later counter mutation, later selftest activity, or later exit activity do not rewrite the shared request that this pilot hands toward the still-blocked runtime substrate.
It also keeps the prepared shared selftest-hook drift guard and the paired shared-release desynchronization proofs reviewable: loader state stays aligned when local release is attempted too early, and shared release state stays aligned when the shared request advances before the loader-owned release path runs.
The adjacent shared reminder packet now stays visible on current `master` through the mixed-source sequencing note, first-loadable parity survey, loader-gap survey, workflow/build-only surfaces, bounded `zigux/tests/phase9_build.zig` bundle, allocator/init-flow and selftest-complete parity proofs, deeper loader survey replay, fallback-readable kernel loader files, and `zigux/Makefile`, but it remains review-only evidence while the broader runtime substrate stays blocked.
That means the honest current atomic64 packet is a direct starter plus a bounded shared-reminder packet, not a completed loadable runtime-module path.

## Gates

1. `zigux/tests/runtime_atomic64_module.zig` remains the dedicated lifecycle gate for the direct starter packet.
2. `zigux/tests/runtime_atomic64_diff.zig` remains the narrow differential gate against `lib/atomic64_test.c`.
3. `zigux/tests/runtime_atomic64_survey.zig` remains the truthfulness gate for the direct packet and the bounded shared reminder packet.
4. No dedicated `make -C zigux phase9-runtime-atomic64-test` route is currently materialized on current `master`, so that family-local convenience handle stays backlog vocabulary instead of shipped make-route evidence.
5. `zigux/tests/phase9_build.zig` currently keeps the direct `phase9-runtime-atomic64-diff` rerun and the family-local `phase9-runtime-atomic64-sample-tests` handle explicit; it still does not currently expose a family-local atomic64 module gate, survey gate, loader scaffold, or aggregate route packet on current `master`.
6. `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/phase9-first-loadable-runtime-module-parity.md`, `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `scripts/zigux/check-phase9-build-only-surface.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/phase9_build.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/tests/runtime_loader_selftest_complete_exit_parity.zig`, `zigux/tests/runtime_loader_gap_survey.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, and `zigux/Makefile` stay adjacent mixed-source review surfaces only until the broader runtime substrate actually lands.

## Review Surface

- `samples/zigux/runtime_atomic64.zig` keeps the direct starter and selftest hook surface explicit.
- `zigux/tests/runtime_atomic64_module.zig`, `zigux/tests/runtime_atomic64_diff.zig`, and `zigux/tests/runtime_atomic64_survey.zig` keep the direct packet machine-checkable.
- `Documentation/zigux/phase9-runtime-atomic64-survey.md` and `zigux/tests/runtime_atomic64_manifest.json` keep the packet truthfulness explicit, including the bounded shared reminder packet and the still-blocked broader runtime substrate.
- `samples/zigux/runtime_atomic64_loader.zig` remains a bounded loader scaffold only; it owns the prepared `RuntimeAtomic64LoadSummary` snapshot replay across later counter mutation and later lifecycle changes, the prepared shared selftest-hook drift guard, and the shared-release desynchronization proofs, but it does not currently prove completed runtime-substrate parity.
- Shared reminder evidence for the broader backlog now lives across `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/phase9-first-loadable-runtime-module-parity.md`, `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `scripts/zigux/check-phase9-build-only-surface.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/phase9_build.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/tests/runtime_loader_selftest_complete_exit_parity.zig`, `zigux/tests/runtime_loader_gap_survey.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, and `zigux/Makefile` rather than only the older three-file shorthand, but that broader packet is still mixed-source review evidence rather than proof of completed runtime-loader kernel parity or dedicated atomic64 make routes.

## Freeze-Map Governance Boundary

- `Documentation/zigux/freeze-map.md` still keeps `kernel/workqueue.c` in the study-only bucket, so this slice stays review-only beside that workqueue-facing boundary instead of claiming scheduler or workqueue parity.
- No parity scorecard entry or Architecture Council status-change request is attached to this slice on current `master`.
- Any future freeze-map status change for this family must route through `Documentation/zigux/phase15-architecture-council-review-process.md` and `Documentation/zigux/phase15-freeze-map-governance.md` instead of being inferred from this family-local packet.

## Non-goals

- No claim that the real runtime substrate is available.
- No claim of scheduler-facing or workqueue parity.
- No claim of full loadable module lifecycle parity before the shared runtime substrate lands.
- No claim that the bounded shared reminder packet is the same thing as a completed live loader binding.

## Next Bounded Step

Keep future follow-through inside one exact atomic64 packet truthfulness repair, with the strongest next candidate being manifest or survey-gate wording if either surface still overstates the absent family-local build or make routes.
