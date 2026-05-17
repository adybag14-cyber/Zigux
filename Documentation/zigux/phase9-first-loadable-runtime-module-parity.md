# Phase 9 First Loadable Runtime Module Parity

## Status
- `PHASE9_STATUS=active`
- `PHASE9_SLICE=first-loadable-runtime-module-parity`
- `PHASE9_LANE_KEY=P9-L01`
- scope: cross-family parity review for the bounded atomic64 and bitmap runtime pilot packets only

## Current Repo Reality
Current `master` keeps the first Phase 9 runtime pilot families reviewable through these family-local packets:
- `samples/zigux/runtime_atomic64.zig`
- `samples/zigux/runtime_atomic64_loader.zig`
- `zigux/tests/runtime_atomic64_module.zig`
- `zigux/tests/runtime_atomic64_diff.zig`
- `zigux/tests/runtime_atomic64_survey.zig`
- `zigux/tests/runtime_atomic64_manifest.json`
- `Documentation/zigux/phase9-runtime-atomic64-survey.md`
- `Documentation/zigux/phase9-runtime-atomic64-module-slice.md`
- `samples/zigux/runtime_bitmap.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_bitmap_top_bit_contract.zig`
- `zigux/tests/runtime_bitmap_module.zig`
- `zigux/tests/runtime_bitmap_diff.zig`
- `zigux/tests/runtime_bitmap_survey.zig`
- `zigux/tests/runtime_bitmap_manifest.json`
- `Documentation/zigux/phase9-runtime-bitmap-survey.md`
- `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`

Current `master` also keeps these adjacent shared reminder surfaces visible beside both families:
- `Documentation/zigux/phase9-runtime-loader-gap-survey.md`
- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
- `zigux/tests/runtime_loader_gap_manifest.json`
- `zigux/tests/runtime_loader_gap_survey.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `zigux/tests/runtime_loader_selftest_complete_exit_parity.zig`
- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/tests/phase9_build.zig`
- `scripts/zigux/check-phase9-build-only-surface.py`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`

## Cross-Family Parity
The bounded atomic64 and bitmap starter packets now match on the roadmap-backed first-loadable parity question that belongs to this lane:
- both families ship sample-side loader scaffolds beside the direct starter sample
- both families keep `provides_selftest_hook=true` explicit in the review packet
- both families bridge through `toSharedLoadPlan()` and the shared `runtime_loader.prepareRequest()` handoff rather than treating the shared loader path as atomic64-only or bitmap-only
- both families keep prepared-request evidence and release-without-substrate reviewable while the shared runtime substrate stays blocked
- both families still stop short of claiming live loadable runtime-module parity

That means the honest remaining Phase 9 gap is shared, not family-local: the runtime substrate still lacks the live binding path that would consume the prepared plans and turn these bounded starters into true loadable runtime modules with full lifecycle parity.

## Boundaries
Keep this note cross-family and review-only:
- do not treat family-local survey, module-slice, manifest, or gate upkeep as owned here once it falls entirely inside `P9-L04` or `P9-L08`
- do not treat shared loader-gap wording, review-checklist wording, or scripts-root reminder repairs as owned here once they fall inside `P9-L16` or `P9-L18`
- do not claim module metadata, depmod publication, live registration control, or runtime execution parity on current `master`

## Next Bounded Step
Leave this note parked unless a fresh live reread finds a new atomic64-versus-bitmap mismatch in the first-loadable review packet itself.
If the next drift is family-local, hand it back to the owning family lane.
If the next drift is shared-loader-only, hand it back to the shared loader lane.