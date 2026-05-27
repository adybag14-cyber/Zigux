# Phase 4 Measurability Gap Survey

This note keeps the remaining Phase 4 roadmap-backed measurability gaps reviewable in one place without widening the already-landed rollback gates into new starter work.

## Status
  * `PHASE4_MEASURABILITY_GAP_STATUS=roadmap_gap_survey_landed`
  * `PHASE4_MEASURABILITY_GAP_LANE_KEY=P4-L19`
  * `PHASE4_MEASURABILITY_GAP_PHASE=Phase 4`
  * `PHASE4_MEASURABILITY_GAP_REF=master`
  * `PHASE4_MEASURABILITY_GAP_ROADMAP_ANCHORS=lib/atomic64_test.c;lib/test_bitmap.c;samples/kprobes/kprobe_example.c;samples/vfs/test-fsmount.c`
  * `PHASE4_MEASURABILITY_GAP_LANDED_GATES=zigux/tests/atomic64_diff.zig;zigux/tests/bitmap_diff.zig`
  * `PHASE4_MEASURABILITY_GAP_REMAINING_PACKET_COUNT=3`

## What Is Measurable Now

Current `master` already keeps the roadmap-named landed rollback gates measurable through:
  * `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`, and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`
  * `zigux/tests/bitmap_diff.zig`, `zigux/tests/phase4_bitmap_diff_manifest.json`, `zigux/tests/phase4_bitmap_diff_survey.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig`
  * `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-reversible-delivery-evidence.md`, and `scripts/zigux/validate-phase4.py`
  * `zigux/tests/phase4_perf_baseline_manifest.json` plus `zigux/tests/phase4_perf_baseline_survey.zig` for the current local-only perf posture

Those surfaces already satisfy the roadmap requirement that the landed atomic64 and bitmap gates stay measurable and reversible.

## Remaining Roadmap-Backed Gaps

### `samples/zigux/kprobe_example.zig`
  * roadmap anchor: `samples/kprobes/kprobe_example.c`
  * current measurable surface: `Documentation/zigux/phase4-kprobe-example-gap-survey.md`, `zigux/tests/phase4_kprobe_example_manifest.json`, and `zigux/tests/phase4_kprobe_example_survey.zig`
  * owner: `Validation and Perf Team`
  * rollback owner: `Validation and Perf Team`
  * current posture: the C anchor is reviewable and replayable, but the Zig starter itself is still absent on current `master`
  * next bounded step: land `samples/zigux/kprobe_example.zig` only in a later dedicated starter lane with an updated rollback-readiness contract

### `samples/zigux/test_fsmount.zig`
  * roadmap anchor: `samples/vfs/test-fsmount.c`
  * current measurable surface: `Documentation/zigux/phase4-test-fsmount-gap-survey.md`, `zigux/tests/phase4_test_fsmount_manifest.json`, and `zigux/tests/phase4_test_fsmount_survey.zig`
  * owner: `Validation and Perf Team`
  * rollback owner: `Validation and Perf Team`
  * current posture: the C anchor, local survey wrappers, and no-perf-threshold boundary are measurable, but the Zig starter itself is still absent on current `master`
  * next bounded step: land `samples/zigux/test_fsmount.zig` only in a later dedicated starter or validator lane with an updated rollback-readiness contract

### Shared CI Perf Promotion
  * current measurable surface: `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, and `scripts/zigux/check-phase4-perf-threshold-matrix.py`
  * decision owner: `Validation and Perf Team`
  * coordination owners: `ABI and Runtime Team` and `Shared Subsystems Pod`
  * rollback owner: `Validation and Perf Team`
  * current posture: local benchmark commands and acceptable limits are measurable today, but shared CI perf promotion is still intentionally pending
  * next bounded step: widen the perf packet only after a later bounded lane approves shared-lab evidence for both landed rollback gates

## Why These Stay Gaps

Phase 4 is not blocked on missing proof for the landed atomic64 or bitmap gates. The remaining gaps are the still-absent roadmap sample starters and the still-unapproved shared CI perf promotion path. Keeping those three items explicit prevents the matrix from overstating Phase 4 completion while preserving the already-landed rollback-owner and lab-matrix evidence.
