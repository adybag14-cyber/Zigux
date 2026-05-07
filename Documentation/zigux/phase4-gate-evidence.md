# Phase 4 Gate Evidence
This note records one exact readback snapshot for the current Phase 4 rollback-ownership and lab-matrix gate definitions.

## Status
- `PHASE4_EVIDENCE_DATE=2026-05-07`
- `PHASE4_EVIDENCE_MODE=github_connector_readback`
- `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`
- `PHASE4_EXACT_READBACK_REF=master`
- `PHASE4_VALIDATION_MATRIX_BLOB_SHA=30304290488109cc9b9fb3c7f82538f3da8ddf93`
- `PHASE4_VALIDATOR_BLOB_SHA=3552a161d1ad358c70d01a535f44755941ec597d`
- `PHASE4_ARTIFACT_DIFF_DOC_BLOB_SHA=089045c25cabf2e838aa174e9314c659453eb7fa`
- `PHASE4_ARTIFACT_DIFF_CONTRACT_CHECKER_BLOB_SHA=47bf77b976241f20351ad6b7aa97884c92c16ada`
- `PHASE4_BUILD_BLOB_SHA=3164f1e56835ae0f0511d890f150dc374b45d1f4`
- `PHASE4_MAKEFILE_BLOB_SHA=e42c8a5353b38a4973eb81ac26f3b957d68e657a`
- `PHASE4_WORKFLOW_BLOB_SHA=aac9976659b54b4fbaf2261c0b167828d937234b`
- `PHASE4_DOC_README_BLOB_SHA=972a708864ba712a7d5abb49bf0ed7bd29b879a8`
- `PHASE4_SCRIPT_README_BLOB_SHA=9f57c3338d1023239d229e4c388e380163d81fbf`
- `PHASE4_TESTS_README_BLOB_SHA=6558f2c073e1ad4436d49c6043634dc6ce242153`
- `PHASE4_ATOMIC64_DIFF_BLOB_SHA=abac49376fee5887f5e69628b329de52d96b4dcb`
- `PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA=d3c082339d3357d7f4ed458313966705a7a9c409`
- `PHASE4_BITMAP_DIFF_BLOB_SHA=825823b724a96c6d4fcca97071ddad8202686587`
- `PHASE4_BITMAP_LIVE_HELPER_REPLAY_BLOB_SHA=24418ad890696a59b95276fe8dec7eaeecf25172`
- `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=9b687999736db7e94b4de20ce58a43f6684f9266`
- `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=5668c3919ab39e7b0715182d4a0d7ffaae73846a`
- `PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA=abf7e36770e6ceb26385f73c72614bb19b5d7ef7`
- `PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=16`
- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=14`
- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=baseline_round_trip,shipped_target_count_drift,missing_exact_readback_heading,validator_blob_pin_drift,phase4_build_manifest_blob_pin_drift,phase4_build_survey_blob_pin_drift,phase9_build_manifest_blob_pin_drift,phase9_build_survey_blob_pin_drift,gate_evidence_self_test_case_count_drift,gate_evidence_self_test_cases_drift,shared_validator_reruns_gate_evidence_self_test_drift,shared_validator_expected_target_count_drift,shared_validator_expected_self_test_case_count_drift,missing_note_file`
- `PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true`
- `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true`
- `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true`
- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=16`
- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=14`
- `PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`
- `PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=false`
- `PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=false`
- `PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=false`

## Exact Readback Evidence
- `Documentation/zigux/artifact-diff.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` now all point at the same currently shipped Phase 4 rollback-readiness packet surfaces that the validator and shared build still own on `master`.
- `scripts/zigux/check-phase4-gate-evidence.py` remains the dedicated exact-readback checker for this narrower rollback-ownership packet.
- `zigux/tests/phase4_runtime_atomic64_diff_manifest.json` and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` remain the manifest-backed runtime atomic64 survey pair, and `phase4-runtime-atomic64-diff-survey-tests` plus `phase4-bitmap-live-helper-replay-tests` stay wired through the shared Phase 4 build entrypoint.
- That published fourteen-case self-test catalog now also exercises the runtime atomic64 packet's `validate-phase4.py`, `phase4-validation-matrix.md`, and `Documentation/zigux/review-checklist.md` manifest and survey blob drift paths inside the existing manifest-backed drift coverage, so those validator, matrix, and reviewer-checklist pins are no longer an unstated self-test gap.
- The exact-readback set is current for the shared rollback-ownership and lab-matrix packet, and the manifest-backed runtime atomic64 survey pair now pins the same current `phase4_build.zig`, `validate-phase4.py`, `phase4-validation-matrix.md`, `Documentation/zigux/review-checklist.md`, and `phase9_build.zig` blobs that the shared validator and review packet now depend on.
- The current helper-backed bitmap rollback lab replay route remains `zig build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig`, and the helper-backed row still records `Shared Subsystems Pod` as both owner and rollback owner for `zigux/tests/phase4_bitmap_live_helper_replay.zig`.
- The helper-backed bitmap rollback row still keeps `threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks` explicit until a later bounded Phase 4 perf packet intentionally approves a harder threshold.
- `zigux/Makefile` still exposes `make -C zigux phase4-validate`, `make -C zigux phase4-test`, `make -C zigux phase4-runtime-atomic64-diff`, `make -C zigux phase4-runtime-atomic64-diff-survey`, `make -C zigux phase4-bitmap-diff`, `make -C zigux phase4-bitmap-live-helper-replay`, and `make -C zigux phase4`, so the Linux-style local replay surface matches the current shared Phase 4 packet instead of hiding those routes in the build file alone.
- The broader shared build and Makefile surface also still carries `phase4-bitmap-diff-survey`, so the bitmap survey packet remains reviewable beside the helper-backed replay without widening the lane into perf-threshold approval.
- `samples/zigux/kprobe_example.zig` remains absent, and `samples/zigux/test_fsmount.zig` remains absent, so the current exact-readback packet still stops short of claiming either missing Zig starter as shipped evidence.

## Current Conclusion
- hard perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved.
- The current exact-readback packet is again aligned to the live validator, README, workflow, Makefile, and runtime-atomic64 survey surfaces on `master` while leaving the roadmap sample and perf-threshold gaps explicit.
