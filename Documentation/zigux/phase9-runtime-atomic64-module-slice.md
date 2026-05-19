# Phase 9 Runtime Atomic64 Module Slice

This note tracks the bounded Phase 9 runtime atomic64 starter packet on `master`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-atomic64-module-starter`
- `PHASE9_LANE_KEY=P9-L16`
- `PHASE9_SURVEYED_COMMIT=9f8c05368242414084e4bc94ea979604c2b6b712`
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
- `.github/workflows/zigux-bootstrap.yml`
- `zigux/tests/phase9_build.zig`

These shared reminder surfaces are review-only evidence on current `master`. They keep the Phase 9 backlog boundary readable beside the atomic64 loader scaffold without turning this family-local slice into a completed loadable runtime-module path. Fresh shared rereads now treat the broader runtime-loader kernel packet and dedicated family-local make routes as absent backlog evidence rather than returned current proof.

## Why This Slice Exists

The direct starter keeps the selftest hook surface and guarded lifecycle parity evidence visible around `lib/atomic64_test.c` without claiming a real loadable runtime module.
The bounded loader scaffold under `samples/zigux/runtime_atomic64_loader.zig` still keeps the intended entry symbol, exit symbol, and handoff-plan shape reviewable.
It also keeps the prepared `RuntimeAtomic64LoadSummary` snapshot reviewable: once `prepare()` captures the anchor, checked operation families, counter snapshot, and selftest-run count, later counter mutation, later selftest activity, or later exit activity do not rewrite the shared request that this pilot hands toward the still-blocked runtime substrate.
It also keeps the prepared shared selftest-hook drift guard and the paired shared-release desynchronization proofs reviewable: loader state stays aligned when local release is attempted too early, and shared release state stays aligned when the shared request advances before the loader-owned release path runs.
The adjacent shared reminder packet now stays visible on current `master` through the shared sequencing note, the workflow rerun guard, and the bounded `zigux/tests/phase9_build.zig` bundle, but it remains review-only evidence while the broader runtime substrate stays blocked.
That means the honest current atomic64 packet is a direct starter plus a bounded shared-reminder packet, not a completed loadable runtime-module path.

## Gates

1. `zigux/tests/runtime_atomic64_module.zig` remains the dedicated lifecycle gate for the direct starter packet.
2. `zigux/tests/runtime_atomic64_diff.zig` remains the narrow differential gate against `lib/atomic64_test.c`.
3. `zigux/tests/runtime_atomic64_survey.zig` remains the truthfulness gate for the direct packet and the bounded shared reminder packet.
4. No dedicated `make -C zigux phase9-runtime-atomic64-test` route is currently materialized on current `master`, so that family-local convenience handle stays backlog vocabulary instead of shipped make-route evidence.
5. `zigux/tests/phase9_build.zig` currently keeps only the direct atomic64 diff shard explicit through `phase9-runtime-atomic64-diff`; it does not currently expose the broader atomic64 sample, module, loader, survey, or aggregate family routes, and the same bundle is otherwise dominated by the separate runtime bitmap packet plus a shared build-handle route.
6. `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `.github/workflows/zigux-bootstrap.yml`, and the bounded `zigux/tests/phase9_build.zig` diff shard stay adjacent shared review surfaces only until the broader runtime substrate actually lands.

## Review Surface

- `samples/zigux/runtime_atomic64.zig` keeps the direct starter and selftest hook surface explicit.
- `zigux/tests/runtime_atomic64_module.zig`, `zigux/tests/runtime_atomic64_diff.zig`, and `zigux/tests/runtime_atomic64_survey.zig` keep the direct packet machine-checkable.
- `Documentation/zigux/phase9-runtime-atomic64-survey.md` and `zigux/tests/runtime_atomic64_manifest.json` keep the packet truthfulness explicit, including the bounded shared reminder packet and the still-blocked broader runtime substrate.
- `samples/zigux/runtime_atomic64_loader.zig` remains a bounded loader scaffold only; it owns the prepared `RuntimeAtomic64LoadSummary` snapshot replay across later counter mutation and later lifecycle changes, the prepared shared selftest-hook drift guard, and the shared-release desynchronization proofs, but it does not currently prove completed runtime-substrate parity.
- Shared reminder evidence for the broader backlog currently lives in `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `.github/workflows/zigux-bootstrap.yml`, and the bounded `zigux/tests/phase9_build.zig` diff shard rather than in returned runtime-loader kernel files or dedicated Phase 9 make routes.

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