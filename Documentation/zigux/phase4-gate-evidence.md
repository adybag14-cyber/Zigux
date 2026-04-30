# Phase 4 Gate Evidence

This note records one exact readback snapshot for the current Phase 4 rollback-ownership and lab-matrix gate definitions.

## Status

- `PHASE4_EVIDENCE_DATE=2026-04-30`
- `PHASE4_EVIDENCE_MODE=github_connector_readback`
- `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`
- `PHASE4_VALIDATION_MATRIX_BLOB_SHA=58104151fdea65e0374da5fd4e4215dd1619b8bb`
- `PHASE4_VALIDATOR_BLOB_SHA=7482e53a6c0d219f1dab3a7cdb4ea46ddac11cf9`
- `PHASE4_BUILD_BLOB_SHA=57f4c3809387cac39e3153b9bbad17ca92ce3684`
- `PHASE4_MAKEFILE_BLOB_SHA=10bafe47e25f26cca614761701e010b12e295bf0`
- `PHASE4_WORKFLOW_BLOB_SHA=0176a4198db35b19ae34d57e018db15631bead14`
- `PHASE4_TEST_FSMOUNT_MANIFEST_BLOB_SHA=30b793cf4ec5eb13f9d074ae4c5cc21d8fefc540`
- `PHASE4_PERF_BASELINE_MANIFEST_BLOB_SHA=8e78f9f1ab3b5b871e8827585fb101498c2e5652`
- `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=36f20e6c532d4008681d05f895fa20b576dd5da7`

## Roadmap Contract

The current Phase 4 roadmap contract still says this tranche must make future Zigux ports measurable and reversible by keeping parity harnesses, perf baselines and thresholds, rollback ownership, lab and CI matrices, and artifact-diff checks for host-side tools reviewable together.

The current roadmap-backed destinations for that packet remain:

- `zigux/tests/atomic64_diff.zig`
- `zigux/tests/bitmap_diff.zig`
- `samples/zigux/kprobe_example.zig`
- `samples/zigux/test_fsmount.zig`
- `scripts/zigux/` diff and layout tools

## Verified Live Gates

### Host-side artifact-diff preflight

- matrix row: `scripts/zigux/artifact_diff.py --self-test`
- matrix owner: `Validation and Perf Team`
- rollback owner: `Validation and Perf Team`
- threshold posture: `deterministic_preflight_required_for_host_side_diff_tools`
- bootstrap CI replay: workflow step `Validate Phase 4 diff gates`
- local replay: `make -C zigux phase4-validate` or direct `python3 scripts/zigux/artifact_diff.py --self-test`
- validator evidence: `scripts/zigux/validate-phase4.py` still requires `scripts/zigux/artifact_diff.py`, the self-test marker, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`

### Host-side artifact-diff external contract replay

- matrix row: `python3 scripts/zigux/check-artifact-diff-contract.py`
- matrix owner: `Validation and Perf Team`
- rollback owner: `Validation and Perf Team`
- threshold posture: `deterministic_preflight_required_for_host_side_diff_tools`
- bootstrap CI replay: workflow step `Validate Phase 4 diff gates`
- local replay: `make -C zigux phase4-validate` or direct `python3 scripts/zigux/check-artifact-diff-contract.py`
- validator evidence: `scripts/zigux/validate-phase4.py` still requires the external contract row plus the emitted `EXPECTED_JSON_ERROR=...`, `ACTUAL_JSON_ERROR=...`, `EXPECTED_SHA256=...`, and `ACTUAL_SHA256=...` surface

### Canonical atomic64 rollback gate

- matrix row: `zigux/tests/atomic64_diff.zig`
- matrix owner: `ABI and Runtime Team`
- rollback owner: `ABI and Runtime Team`
- threshold posture: `threshold_pending_until_runtime_atomic64_scope_widens`
- bootstrap CI replay: workflow steps `Validate Phase 4 diff gates` and `Run Phase 4 diff tests`
- local replay: `make -C zigux phase4-validate`, `make -C zigux phase4-test`, and the isolated `make -C zigux phase4-runtime-atomic64-diff`
- build-entry evidence: `zigux/tests/phase4_build.zig` still wires `atomic64_diff.zig`, `phase4_runtime_atomic64_diff_survey.zig`, `phase4-runtime-atomic64-diff-tests`, and `phase4-runtime-atomic64-diff-survey-tests`
- manifest evidence: `zigux/tests/phase4_runtime_atomic64_diff_manifest.json` still records `roadmap_atomic64_diff_present`, `roadmap_atomic64_wrapper_targets_runtime_diff`, `phase4_build_uses_atomic64_wrapper`, `phase4_validator_atomic64_diff_present`, and the bounded threshold plan for the current correctness-only scope

### `test_fsmount` survey gate

- matrix row: `zigux/tests/phase4_test_fsmount_survey.zig`
- matrix owner: `Validation and Perf Team`
- rollback owner: `Validation and Perf Team`
- threshold posture: `c_anchor_only_until_test_fsmount_starter_lands`
- bootstrap CI replay: workflow steps `Validate Phase 4 diff gates` and `Run Phase 4 diff tests`
- local replay: `make -C zigux phase4-test-fsmount-survey`, direct `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`, and the current C-anchor replay `make M=samples/vfs`
- manifest evidence: `zigux/tests/phase4_test_fsmount_manifest.json` still records `zig_sample_present: false`, `phase4_build_present: true`, `phase4_validator_present: true`, `phase4_validation_matrix_present: true`, and the remaining `samples/zigux/test_fsmount.zig` starter gap

### Perf-baseline survey gate

- matrix row: `zigux/tests/phase4_perf_baseline_survey.zig`
- matrix owner: `Validation and Perf Team`
- rollback owner: `Validation and Perf Team`
- threshold posture: `perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land`
- bootstrap CI replay: workflow steps `Validate Phase 4 diff gates` and `Run Phase 4 diff tests`
- local replay: `make -C zigux phase4-perf-baseline-survey` and direct `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig`
- manifest evidence: `zigux/tests/phase4_perf_baseline_manifest.json` still records both shipped rollback gates, the `threshold_pending_until_runtime_atomic64_scope_widens` and `threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks` postures, and the still-unapproved benchmark-command plus acceptable-limit state

### Bitmap rollback gate

- matrix row: `zigux/tests/bitmap_diff.zig`
- matrix owner: `Shared Subsystems Pod`
- rollback owner: `Shared Subsystems Pod`
- threshold posture: `threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks`
- bootstrap CI replay: workflow steps `Validate Phase 4 diff gates` and `Run Phase 4 diff tests`
- local replay: `make -C zigux phase4-validate`, `make -C zigux phase4-test`, and the isolated `make -C zigux phase4-bitmap-diff`
- build-entry evidence: `zigux/tests/phase4_build.zig` still wires `bitmap_diff.zig` and `phase4-bitmap-diff-tests`
- matrix evidence: `Documentation/zigux/phase4-validation-matrix.md` still keeps the current rounded two-word `bitmap_fill(..., 115)` mismatch survey-only instead of overstating parity

## Exact Readback Evidence

The current packet stayed aligned across the following readbacks on `master`:

- `Documentation/zigux/phase4-validation-matrix.md` still names the current rollback owners, threshold posture, workflow step names, local replay commands, and reversible-delivery evidence for the two shipped rollback gates plus the two manifest-backed survey gates.
- `scripts/zigux/validate-phase4.py` still requires the matrix note, workflow markers, `zigux/Makefile` hooks, `zigux/tests/phase4_build.zig`, `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`, `zigux/tests/phase4_test_fsmount_manifest.json`, `zigux/tests/phase4_test_fsmount_survey.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, and `zigux/tests/bitmap_diff.zig` together.
- `zigux/Makefile` still exposes `phase4-validate`, `phase4-test`, `phase4-runtime-atomic64-diff`, `phase4-test-fsmount-survey`, `phase4-perf-baseline-survey`, and `phase4-bitmap-diff`.
- `.github/workflows/zigux-bootstrap.yml` still drives `make -C zigux phase4-validate` in `Validate Phase 4 diff gates` and `make -C zigux phase4-test` in `Run Phase 4 diff tests`.
- `zigux/tests/phase4_build.zig` still exposes `phase4-runtime-atomic64-diff-tests`, `phase4-runtime-atomic64-diff-survey-tests`, `phase4-test-fsmount-survey-tests`, `phase4-perf-baseline-survey-tests`, and `phase4-bitmap-diff-tests`.

## Current Conclusion

The current live Phase 4 rollback-ownership and lab-matrix packet is aligned at the gate-definition level.

The open work is still the already-documented bounded roadmap gap, not a fresh matrix-definition mismatch:

- `samples/zigux/kprobe_example.zig` is still absent and remains C-anchor-only
- `samples/zigux/test_fsmount.zig` is still absent and remains C-anchor-only through the manifest-backed survey gate
- perf baselines and acceptable limits for the shipped `atomic64_diff.zig` and `bitmap_diff.zig` gates are still intentionally unapproved
