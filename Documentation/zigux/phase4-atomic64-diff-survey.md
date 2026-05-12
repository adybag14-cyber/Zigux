# Phase 4 Atomic64 Diff Survey

This note records the current `master` readback for the roadmap-backed `zigux/tests/atomic64_diff.zig` packet so Phase 4 review stays grounded in the live rollback-readiness surface instead of reopening this lane as if the atomic64 wrapper were still missing.

## Status

- `PHASE4_LANE_KEY=P4-L01`
- `PHASE4_STATUS=atomic64_diff_roadmap_survey`
- `PHASE4_PROVENANCE_MODE=github_connector_readback`
- survey date: `2026-05-12`
- bounded scope: compare the roadmap-named `zigux/tests/atomic64_diff.zig` destination against the current shared Phase 4 packet without widening into bitmap, sample, or perf-policy delivery work

## Roadmap Target

- Phase 4's product goal is to make future Zigux ports measurable and reversible.
- The roadmap names `lib/atomic64_test.c` as one of the primary Linux anchors for this tranche.
- The recommended Zigux destination for that anchor is `zigux/tests/atomic64_diff.zig` inside the `zigux/tests/` rollback harness packet.
- The same roadmap packet also requires perf baselines and thresholds, rollback ownership, lab and CI matrices, and validation-first review surfaces around the landed replay.

## Current Master Readback

- `zigux/tests/atomic64_diff.zig` is present on `master` and already acts as the roadmap-named Phase 4 wrapper instead of leaving the atomic64 replay missing.
- The wrapper stays intentionally thin: it imports `zigux/tests/runtime_atomic64_diff.zig` so the shared runtime-backed replay body remains single-sourced while the roadmap path stays reviewable on the Phase 4 entrypoint.
- The current wrapper still pins the bounded arithmetic, exchange, `cmpxchg`, `add_unless`, bitwise, selftest-family, and threshold-replay expectations that the wider Phase 4 packet already treats as the current atomic64 rollback gate.
- `zigux/tests/phase4_runtime_atomic64_diff_manifest.json` and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` are both present on `master` and already keep the owner map, rollback owner, shared build wiring, validator linkage, matrix linkage, review-checklist linkage, gate-evidence linkage, and local perf-baseline linkage explicit around the same wrapper-to-runtime handoff.
- `Documentation/zigux/phase4-validation-matrix.md` already carries dedicated atomic64 rows for both `zigux/tests/atomic64_diff.zig` and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`, including the current owner, rollback owner, shared CI replay route, local replay route, and correctness-only threshold posture.
- `Documentation/zigux/phase4-gate-evidence.md` still names the atomic64 wrapper, runtime replay body, and manifest-backed survey pair as part of the shipped Phase 4 exact-readback packet.

## Survey Result

- `P4-L01` does not have a remaining roadmap gap at the level of target presence: the roadmap-named `zigux/tests/atomic64_diff.zig` wrapper is already landed, wired into the shared Phase 4 build and validator packet, and surrounded by the expected manifest, survey, matrix, and gate-evidence review surfaces.
- The honest same-family follow-through is now smaller than a new replay implementation step. The visible adjacent drift from this readback is that `Documentation/zigux/phase4-gate-evidence.md` still records `PHASE4_ATOMIC64_DIFF_BLOB_SHA=009636998e49a4349beeb1b2e3da85180e122801`, while the current connector readback for `zigux/tests/atomic64_diff.zig` reports blob `90076a50a671c0717a7df11b008f8f6ec2f2da0a`.
- That means the lane's truthful next job is a packet-local exact-readback refresh, not another wrapper, survey companion, or broader Phase 4 feature surface.
- Shared CI perf thresholds also remain intentionally unapproved for the atomic64 rollback gate, but that posture is already recorded through the shipped matrix, gate-evidence note, and local perf-baseline survey packet rather than representing a missing atomic64 destination.

## Next Bounded Step

- Refresh the atomic64 blob-pin line inside `Documentation/zigux/phase4-gate-evidence.md` so the shared exact-readback packet matches the current `zigux/tests/atomic64_diff.zig` head again.
- When a writable checkout and Zig toolchain are available, rerun `python3 scripts/zigux/check-phase4-gate-evidence.py --self-test`, `python3 scripts/zigux/check-phase4-gate-evidence.py`, `python3 scripts/zigux/validate-phase4.py`, `zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig`, and `zig build phase4-runtime-atomic64-diff-survey --build-file zigux/tests/phase4_build.zig` together so the exact-readback repair and the bounded atomic64 rollback packet stay replay-validated as one lane.
- Until that packet-local refresh is available, keep `P4-L01` parked and do not reopen it for bitmap, kprobe, `test_fsmount`, or shared perf-policy follow-through.
