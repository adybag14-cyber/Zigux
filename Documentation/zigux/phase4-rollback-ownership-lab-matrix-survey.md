# Phase 4 Rollback Ownership and Lab Matrix Survey

## Status
- `PHASE4_ROLLBACK_LAB_MATRIX_SURVEY_STATUS=roadmap_gap_narrowed_to_parked_sample_and_perf_promotion_followthrough`
- `PHASE4_ROLLBACK_LAB_MATRIX_LANE_KEY=P4-L19`
- `PHASE4_ROLLBACK_LAB_MATRIX_PHASE=Phase 4`
- `PHASE4_ROLLBACK_LAB_MATRIX_REF=master`
- scope: compare the roadmap's rollback-ownership and lab-matrix requirements against current `master`, record which parts of the shipped Phase 4 packet are already measurable, and name only the remaining measurable gaps that still belong to this lane family
- current repo reality:
  - `Documentation/zigux/phase4-validation-matrix.md`
  - `Documentation/zigux/phase4-gate-evidence.md`
  - `Documentation/zigux/phase4-kprobe-example-gap-survey.md`
  - `Documentation/zigux/phase4-test-fsmount-gap-survey.md`
  - `Documentation/zigux/artifact-diff.md`
  - `Documentation/zigux/phase4-artifact-diff-tooling-survey.md`
  - `scripts/zigux/validate-phase4.py`
  - `scripts/zigux/check-phase4-gate-evidence.py`
  - `scripts/zigux/check-phase4-workflow-route-counts.py`
  - `scripts/zigux/check-phase4-artifact-diff-determinism.py`
  - `zigux/tests/atomic64_diff.zig`
  - `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`
  - `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`
  - `zigux/tests/bitmap_diff.zig`
  - `zigux/tests/phase4_bitmap_diff_manifest.json`
  - `zigux/tests/phase4_bitmap_diff_survey.zig`
  - `zigux/tests/phase4_bitmap_live_helper_replay.zig`
  - `zigux/tests/phase4_perf_baseline_manifest.json`
  - `zigux/tests/phase4_perf_baseline_survey.zig`
  - `zigux/tests/phase4_kprobe_example_manifest.json`
  - `zigux/tests/phase4_kprobe_example_survey.zig`
  - `zigux/tests/phase4_test_fsmount_manifest.json`
  - `zigux/tests/phase4_test_fsmount_survey.zig`
  - `zigux/tests/phase4_build.zig`
  - `zigux/Makefile`
  - `.github/workflows/zigux-bootstrap.yml`

## Roadmap Comparison

Phase 4 in `ZAR_TO_ZIGUX_PRODUCT_ROADMAP (1).md` requires parity harnesses, perf baselines and thresholds, rollback ownership, lab and CI matrices, and artifact-diff checks so future Zigux ports stay measurable and reversible.

Current `master` already closes most of that packet for the shipped Phase 4 surfaces:
- `Documentation/zigux/phase4-validation-matrix.md` names the current gate owners, rollback owners, bootstrap replay routes, local lab replay routes, and threshold posture for the shipped Phase 4 gates and surveys.
- `Documentation/zigux/phase4-gate-evidence.md` plus `scripts/zigux/check-phase4-gate-evidence.py` keep the rollback-ownership and lab-matrix packet exact-readback reviewable on current `master`.
- `scripts/zigux/check-phase4-workflow-route-counts.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` keep the shared wrapper routes explicit instead of leaving the local replay surface implied.
- `zigux/tests/atomic64_diff.zig`, `zigux/tests/bitmap_diff.zig`, `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`, `zigux/tests/phase4_bitmap_diff_survey.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` already give the shipped rollback gates and their reviewability surveys a concrete validation surface.
- `zigux/tests/phase4_perf_baseline_manifest.json` plus `zigux/tests/phase4_perf_baseline_survey.zig` already keep the approved local benchmark commands and approved local-only acceptable limits measurable for the shipped atomic64 and bitmap gates without pretending that shared CI perf coverage has been approved.
- `Documentation/zigux/artifact-diff.md` plus `Documentation/zigux/phase4-artifact-diff-tooling-survey.md` record the bounded host-side artifact-diff packet that the roadmap also asks Phase 4 to carry.

## Current Conclusion

The roadmap gap for rollback ownership and lab-matrix measurability is no longer a missing shipped matrix or missing rollback-owner packet. Current `master` already carries the shared matrix, the exact-readback checker packet, the wrapper-route checker, the artifact-diff tooling packet, the shipped rollback gates, and the dedicated local perf-baseline survey.

The remaining measurable gaps are narrower and already parked in this same lane family:
1. `samples/zigux/kprobe_example.zig` is still absent, but the dedicated parked packet at `Documentation/zigux/phase4-kprobe-example-gap-survey.md`, `zigux/tests/phase4_kprobe_example_manifest.json`, and `zigux/tests/phase4_kprobe_example_survey.zig` keeps that absence measurable with an explicit owner, rollback owner, Linux replay command, local survey wrapper, and direct validation entrypoint.
2. `samples/zigux/test_fsmount.zig` is still absent, but the dedicated parked packet at `Documentation/zigux/phase4-test-fsmount-gap-survey.md`, `zigux/tests/phase4_test_fsmount_manifest.json`, and `zigux/tests/phase4_test_fsmount_survey.zig` keeps that absence measurable with an explicit owner, rollback owner, Linux replay command, local survey wrappers, direct validation entrypoint, and reviewability-only threshold posture.
3. Shared CI perf promotion is still intentionally unapproved. The measurable current truth is the dedicated local-only perf-baseline packet, not a broader shared-CI perf claim.

## Direct Replay Surface
- `python3 scripts/zigux/check-phase4-gate-evidence.py --self-test`
- `python3 scripts/zigux/check-phase4-gate-evidence.py`
- `python3 scripts/zigux/check-phase4-workflow-route-counts.py`
- `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py`
- `python3 scripts/zigux/validate-phase4.py`
- `make -C zigux phase4-kprobe-example-survey`
- `make -C zigux phase4-test-fsmount-survey`
- `make -C zigux phase4-perf-baseline-survey`
- `make -C zigux phase4-validate`

## Boundary
- this survey does not claim that `samples/zigux/kprobe_example.zig` or `samples/zigux/test_fsmount.zig` have landed
- this survey does not promote the dedicated local-only perf-baseline packet into shared CI perf approval
- this survey does not widen into atomic64 or bitmap harness-body work, manifest rewrites, or validator-schema refresh work that belongs to neighboring Phase 4 lanes
- reopen `P4-L19` only if the parked `kprobe` or `test_fsmount` gap packets drift, if the shared matrix or exact-readback packet stops describing those parked gaps honestly, or if a later bounded lane intentionally promotes the current local-only perf posture into a broader shared-CI decision
