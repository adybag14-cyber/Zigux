# Phase 4 Gate Evidence

## Status
  * `PHASE4_VALIDATION_MATRIX_BLOB_SHA=43789166370910686ce37e2f7a81e09b671e0750`
  * `PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=adbf024eaafb71f9e606f1ff6eefa6db6844a91f`
  * `PHASE4_ARTIFACT_DIFF_DOC_BLOB_SHA=6ac9c08ffdc75a5cce761f204c93babd833ea89c`
  * `PHASE4_ARTIFACT_DIFF_HELPER_BLOB_SHA=3ff77318f7511d889e15a5b482d7fa486029ed09`
  * `PHASE4_ARTIFACT_DIFF_CONTRACT_CHECKER_BLOB_SHA=48e611aa0a53540d8594dbb5c2200bb258d03d08`
  * `PHASE4_MAKEFILE_BLOB_SHA=7ae6b04af5e33a8119c5219c4c890b0dc4262797`
  * `PHASE4_WORKFLOW_BLOB_SHA=9126c791ddf71e61a5aa33125f5120fc66fb7737`
  * `PHASE4_DOC_README_BLOB_SHA=c0eeab60d4f48f7bfc0a2363ed2ef070f6790d3a`
  * `PHASE4_SCRIPT_README_BLOB_SHA=1b6ace1eb7207adf411f5136623a4315ceb257e5`
  * `PHASE4_TESTS_README_BLOB_SHA=0a29da3f11f2f1036ba6db0978980e420af21a65`
  * `PHASE4_VALIDATOR_BLOB_SHA=6840d9c60266850b9e270c527c9ce6596aee01e0`
  * `PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=366eab807fe408bbe4839a981eabf7d550d1b08b`
  * `PHASE4_ATOMIC64_DIFF_BLOB_SHA=14b756f595525973c4a65d7dac88133d97e28f0a`
  * `PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA=907c937190fcb0266d58cb80bcff44ccf6092874`
  * `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=97345269c0f5e7c63c276732202e8b04c6bcd65a`
  * `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=87b72410a69b90e0cd4377ac30f7c47d0d9943c2`
  * `PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA=5bbf3cd3796b6b576df27054c586844d924228f3`
  * `PHASE4_PHASE9_BUILD_BLOB_SHA=0a093698e7bee23e37b6eb2fceae57bbe310ad29`
  * `PHASE4_REVERSIBLE_DELIVERY_EVIDENCE_BLOB_SHA=50760595db2bd32b29b9653703f7bce66f710674`
  * `PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=19`
  * `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=45`
  * `PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=baseline_round_trip,shipped_target_count_drift,missing_exact_readback_heading,forbidden_gate_evidence_checker_self_pin,validator_blob_pin_drift,phase4_build_manifest_blob_pin_drift,phase4_build_survey_blob_pin_drift,phase9_build_manifest_blob_pin_drift,phase9_build_survey_blob_pin_drift,doc_readme_blob_pin_drift,script_readme_blob_pin_drift,tests_readme_blob_pin_drift,gate_evidence_self_test_case_count_drift,gate_evidence_self_test_cases_drift,shared_validator_reruns_gate_evidence_check_drift,shared_validator_reruns_gate_evidence_self_test_drift,shared_validator_expected_target_count_drift,shared_validator_expected_self_test_case_count_drift,runtime_atomic64_survey_packet_presence_drift,bitmap_manifest_gate_evidence_blob_drift,workflow_route_checker_matrix_presence_drift,kprobe_gap_packet_presence_drift,kprobe_owner_drift,kprobe_validation_entrypoint_drift,kprobe_next_step_drift,perf_baseline_packet_presence_drift,perf_baseline_note_split_marker_drift,perf_baseline_owner_drift,perf_baseline_shared_promotion_status_drift,test_fsmount_gap_packet_presence_drift,test_fsmount_threshold_posture_drift,test_fsmount_owner_drift,test_fsmount_validation_entrypoint_drift,test_fsmount_linux_style_wrapper_drift,test_fsmount_next_step_drift,missing_validator_file,missing_phase4_build_file,missing_artifact_diff_helper_file,missing_workflow_route_checker_file,missing_atomic64_manifest_file,missing_bitmap_manifest_file,missing_perf_survey_file,missing_kprobe_manifest_file,missing_test_fsmount_survey_file,missing_note_file`
  * `PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true`
  * `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true`
  * `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true`
  * `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=19`
  * `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=45`
  * `PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`
  * `PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true`
  * `PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=true`
  * `PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true`

## Exact Readback Evidence
  * `scripts/zigux/check-phase4-gate-evidence.py` now recomputes the broader packet blob pins from live file contents so stale readback evidence fails closed.
  * The runtime atomic64 handoff remains reviewable through `phase4-runtime-atomic64-diff-survey-tests`, `make -C zigux phase4-runtime-atomic64-diff-survey`, two `inc_not_zero` checks, and three `dec_if_positive` checks.
  * The atomic64 wrapper rollback evidence treats `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA` and `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA` as paired handoff pins: if either pin drifts, refresh the wrapper route, the manifest-backed survey, and this gate-evidence packet together before claiming the `zigux/tests/atomic64_diff.zig` lane is still reversible.
  * The broader bitmap rollback packet stays intentionally outside this exact-readback note on current `master` even though the public `zigux/tests` tree again exposes `zigux/tests/bitmap_diff.zig` and `zigux/tests/phase4_bitmap_live_helper_replay.zig`; this note remains focused on the narrower shared validator packet while the broader bitmap rollback details stay reviewable through the surrounding matrix and the paired bitmap survey packet.
  * The paired bitmap survey packet also keeps the already-landed zero-length range and prefix no-op checks plus the zero-length copy invariant explicit beside the exact 35-bit and 115-bit synthetic fill prefixes and the rounded 64-bit and 128-bit zero boundaries.
  * The broader bitmap reviewability details still belong in the surrounding matrix and reminder packet rather than this exact-readback note while the shared validator-first packet stays narrower than the coupled bitmap survey surfaces on current `master`.
  * The adjacent local-only perf packet remains explicit through `scripts/zigux/check-phase4-perf-baseline-packet.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, and the shared posture that local-only benchmark commands and acceptable limits are approved today while shared CI perf promotion pending remains unchanged.
  * `scripts/zigux/check-phase4-workflow-route-counts.py` keeps the shared `make -C zigux phase4-validate`, `make -C zigux phase4-artifact-diff-contract`, and `make -C zigux phase4-test` wrapper inventory explicit beside the dedicated local survey wrappers so the validator-first route packet cannot drift away from this exact-readback note unnoticed.
  * The parked starter-gap packet keeps `PHASE4_KPROBE_SHARED_LAB_AND_CI_MATRIX_ANCHOR=Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix` explicit beside the current `make -C zigux phase4-kprobe-example-survey` and `make -C zigux phase4-test-fsmount-survey` wrappers.
  * `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig`
  * `make -C zigux phase4-perf-baseline-survey`
  * `zig build phase4-bitmap-diff-survey --build-file zigux/tests/phase4_build.zig`
  * `make -C zigux phase4-bitmap-diff-survey`
