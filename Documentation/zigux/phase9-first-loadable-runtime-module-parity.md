# Phase 9 First Loadable Runtime Module Parity

## Status
- `PHASE9_STATUS=parked`
- `PHASE9_SLICE=first-loadable-runtime-module-parity`
- `PHASE9_LANE_KEY=P9-L01`
- scope: historical cross-family parity review for the bounded atomic64 and bitmap runtime pilot packets only

## Current Repo Reality
Current `master` no longer keeps the older first-loadable atomic64 and bitmap family-local packets on tree.

Fresh repo-first rereads did not find these formerly paired atomic64 packet surfaces:
- `samples/zigux/runtime_atomic64.zig`
- `samples/zigux/runtime_atomic64_loader.zig`
- `zigux/tests/runtime_atomic64_module.zig`
- `zigux/tests/runtime_atomic64_diff.zig`
- `zigux/tests/runtime_atomic64_survey.zig`
- `zigux/tests/runtime_atomic64_manifest.json`
- `Documentation/zigux/phase9-runtime-atomic64-survey.md`
- `Documentation/zigux/phase9-runtime-atomic64-module-slice.md`

Fresh repo-first rereads also did not find these formerly paired bitmap packet surfaces:
- `samples/zigux/runtime_bitmap.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_bitmap_top_bit_contract.zig`
- `zigux/tests/runtime_bitmap_module.zig`
- `zigux/tests/runtime_bitmap_diff.zig`
- `zigux/tests/runtime_bitmap_survey.zig`
- `zigux/tests/runtime_bitmap_manifest.json`
- `Documentation/zigux/phase9-runtime-bitmap-survey.md`
- `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`

Current `master` instead keeps a narrower shared Phase 9 reminder packet around the surviving trace-events runtime sample through these still-shipped surfaces:
- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`
- `scripts/zigux/check-phase9-trace-events-runtime-packet.py`
- `zigux/tests/README.md`
- `samples/zigux/runtime_trace_events.zig`
- `samples/zigux/runtime_trace_events_unregistered_gate.zig`

Current `master` also does not currently expose the broader shared runtime-loader packet that older reminder surfaces paired with the atomic64 and bitmap families. Fresh rereads did not find:
- `Documentation/zigux/phase9-runtime-loader-gap-survey.md`
- `zigux/tests/runtime_loader_gap_manifest.json`
- `zigux/tests/runtime_loader_gap_survey.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `zigux/tests/runtime_loader_selftest_complete_exit_parity.zig`
- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/tests/phase9_build.zig`
- `scripts/zigux/check-phase9-build-only-surface.py`

Current `master` does materialize `zigux/Makefile` and `.github/workflows/zigux-bootstrap.yml` again, but those live bodies stay shared repo-level surfaces rather than dedicated Phase 9 owner evidence: `zigux/Makefile` still lacks any `phase9-*` runtime-pilot routes, and `.github/workflows/zigux-bootstrap.yml` remains a broad bootstrap workflow instead of proof that the removed shared runtime-loader packet returned.

## Cross-Family Parity
The older first-loadable atomic64-versus-bitmap parity comparison is not currently live on shipped `master`.

- the atomic64 and bitmap family-local packets are both backlog-only absent surfaces until a fresh repo reread proves they have returned
- the broader shared runtime-loader packet is also backlog-only absent on current `master`
- this note must not claim shipped sample-side loader scaffolds, shipped `provides_selftest_hook=true` parity, shipped `toSharedLoadPlan()` handoffs, or shipped prepared-request evidence unless the exact atomic64, bitmap, and shared-loader file families return together
- the surviving trace-events runtime sample pair belongs to the narrow shared Phase 9 reminder packet, not to this parked first-loadable parity note

## Boundaries
Keep this note parked and repo-reality-first:
- do not reopen atomic64 family-local survey, module-slice, manifest, or gate upkeep here while those packet files remain absent; if they return and drift, hand that work to the owning atomic64 family lane
- do not reopen bitmap family-local survey, module-slice, manifest, or gate upkeep here while those packet files remain absent; if they return and drift, hand that work to `P9-L08`
- do not treat shared reminder, checklist, or scripts-root truthfulness repairs as owned here while the atomic64 and bitmap parity packet remains absent
- do not claim module metadata, depmod publication, live registration control, or runtime execution parity on current `master`

## Next Bounded Step
Leave this note parked unless a fresh live reread proves that direct atomic64 family-local packet files and direct bitmap family-local packet files have both returned on current `master`.
If only one family returns, hand it back to the owning family lane instead of reviving cross-family parity here.
If the surviving shared reminder packet drifts while both family-local packets remain absent, hand that follow-through back to the shared Phase 9 reminder lane.
