# Phase 9 Runtime Atomic64 Survey

This note tracks the bounded Phase 9 runtime atomic64 packet on current `master`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-atomic64-survey`
- `PHASE9_LANE_KEY=P9-L04`
- `PHASE9_SURVEYED_COMMIT=9f8c05368242414084e4bc94ea979604c2b6b712`
- scope: direct atomic64 sample, module gate, diff gate, survey gate, bounded loader scaffold, and the visible shared loader-facing reminder packet only

## Current Packet

Current `master` keeps these direct atomic64 packet files visible:

- `samples/zigux/runtime_atomic64.zig`
- `samples/zigux/runtime_atomic64_loader.zig`
- `zigux/tests/runtime_atomic64_module.zig`
- `zigux/tests/runtime_atomic64_diff.zig`
- `zigux/tests/runtime_atomic64_survey.zig`
- `zigux/tests/runtime_atomic64_manifest.json`
- `Documentation/zigux/phase9-runtime-atomic64-module-slice.md`

Current `master` also keeps these adjacent shared-loader reminder surfaces visible:

- `Documentation/zigux/phase9-runtime-loader-gap-survey.md`
- `scripts/zigux/check-phase9-build-only-surface.py`
- `.github/workflows/zigux-bootstrap.yml`
- `zigux/tests/phase9_build.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `zigux/tests/runtime_loader_selftest_complete_exit_parity.zig`
- `zigux/tests/runtime_loader_gap_manifest.json`
- `zigux/tests/runtime_loader_gap_survey.zig`
- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/Makefile`

That means the honest current packet is a direct atomic64 sample, module, diff, survey, and bounded loader-scaffold packet plus a visible shared-loader reminder packet. It is not a completed loadable runtime-module path, and it does not clear the broader runtime-substrate blocker.

## Routes

1. `zigux/tests/runtime_atomic64_module.zig` keeps the direct lifecycle packet reviewable.
2. `zigux/tests/runtime_atomic64_diff.zig` keeps the `lib/atomic64_test.c` operation families machine-checkable.
3. `zigux/tests/runtime_atomic64_survey.zig` keeps the direct packet and the visible shared-loader reminder packet fail-closed.
4. `zig build phase9-runtime-atomic64-loader-tests --build-file zigux/tests/phase9_build.zig` keeps the landed loader-scaffold replay explicit as first-class shared-build evidence beside the direct sample leg, including the prepared `RuntimeAtomic64LoadSummary` snapshot that keeps the anchor, checked operation families, counter snapshot, and selftest-run count reviewable even if later counter mutation, later selftest activity, or later exit activity changes the live sample before the still-blocked runtime handoff, including the prepared shared selftest-hook drift guard that still fails before any live atomic64 claim, and including the paired shared-release desynchronization proofs that keep loader state and shared release state synchronized whether the local release fires too early or the shared request advances before the loader-owned release path runs.
5. `make -C zigux phase9-runtime-atomic64-test` keeps the shipped family-local convenience route explicit beside the direct sample, loader, module, diff, and survey packet instead of leaving the atomic64 replay visible only through the shared Phase 9 build file.
6. `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `scripts/zigux/check-phase9-build-only-surface.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/phase9_build.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/tests/runtime_loader_selftest_complete_exit_parity.zig`, `zigux/tests/runtime_loader_gap_manifest.json`, `zigux/tests/runtime_loader_gap_survey.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, and `zigux/Makefile` remain visible shared loader-facing review surfaces, including the focused `phase9-runtime-loader-shared-tests` replay, the shared build-only surface checker, and the workflow-backed `make -C zigux phase9` route, while the broader runtime substrate stays blocked.

## Boundaries

1. Keep this packet inside the direct atomic64 starter, module gate, diff gate, survey gate, and bounded loader scaffold.
2. Keep the visible shared-loader reminder packet explicit as review-only evidence instead of treating it as completed live loader binding or proof that the broader runtime substrate already exists.
3. Keep lifecycle, selftest, and direct counter replay evidence visible without widening into scheduler-facing or workqueue-facing ownership.

## Freeze-Map Governance Evidence

- `Documentation/zigux/freeze-map.md` keeps `kernel/workqueue.c` in the study-only bucket, so this packet stays review-only beside that workqueue-facing boundary instead of claiming scheduler or workqueue delivery.
- No parity scorecard entry or Architecture Council status-change request is attached to this packet on current `master`.
- Any future freeze-map status change for this family must route through `Documentation/zigux/phase15-architecture-council-review-process.md` and `Documentation/zigux/phase15-freeze-map-governance.md` instead of being inferred from the landed atomic64 starter, bounded loader scaffold, or visible shared loader-facing reminder packet.

## Recommended Next Step

Keep the next same-lane move inside one exact atomic64 packet truthfulness repair while the shared-loader reminder packet remains visible review-only evidence and the broader runtime substrate is still blocked.