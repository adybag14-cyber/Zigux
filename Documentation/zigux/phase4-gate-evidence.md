# Phase 4 Gate Evidence

## Status
  * `PHASE4_VALIDATION_MATRIX_BLOB_SHA=0c243dd80d8ff192d43c3f2db0ca36a2f8e5f77c`
  * `PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=c1fa46fad53adc7327a03fbe12d3510e854e8bfa`
  * `PHASE4_ARTIFACT_DIFF_DOC_BLOB_SHA=5173368ba7f69587f6839931b380f1e77c456933`
  * `PHASE4_ARTIFACT_DIFF_HELPER_BLOB_SHA=4dc6294c98aea9475d4d5965ac541cab9a7dc725`
  * `PHASE4_ARTIFACT_DIFF_CONTRACT_CHECKER_BLOB_SHA=92696cb02fc915fec0f5f1c4c2768a99cf99c9bf`
  * `PHASE4_MAKEFILE_BLOB_SHA=2123cbb48f7bb32293c1bb3dead619e6d437923b`
  * `PHASE4_WORKFLOW_BLOB_SHA=d33dbde416395f8d7cd0e79da73d90b6e5dea3bb`
  * `PHASE4_DOC_README_BLOB_SHA=8dedec9dde2aaffd3d83300046262c1b8d7cb50a`
  * `PHASE4_SCRIPT_README_BLOB_SHA=cad8480ef579f8dfb6d4c602134bf73076a7842b`
  * `PHASE4_TESTS_README_BLOB_SHA=f68a22bb7857d4a1d82e644e131c45825fb979b1`
  * `PHASE4_VALIDATOR_BLOB_SHA=4ef6d3c50ee6111e6855ff05fe92928c5700097b`
  * `PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=6e3df94a0b80ece5d4e747d6cdc683e01575133e`
  * `PHASE4_ATOMIC64_DIFF_BLOB_SHA=e84bf84b5e24428d596fe25502512fa24ce28b51`
  * `PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA=9ad41de72613cd72273b41c9cf2a64a0c46962df`
  * `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=0c7e843708eefefd688d4909110b81bf3782176c`
  * `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=8ac70b09fb17b97f0c067547f2ad8b3855c4a908`
  * `PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA=dcaabeefb1c5b1b7ddf0db0d7001cf0482c70f2a`
  * `PHASE4_PHASE9_BUILD_BLOB_SHA=2ac6379e587fe059115df6a12c879e6d84590a66`
  * `PHASE4_REVERSIBLE_DELIVERY_EVIDENCE_BLOB_SHA=76c83983235d4701fca5b3eb26aadd063b303525`
  * `PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=19`
  * `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=44`
  * `PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=baseline_round_trip,shipped_target_count_drift,missing_exact_readback_heading,forbidden_gate_evidence_checker_self_pin,validator_blob_pin_drift,phase4_build_manifest_blob_pin_drift,phase4_build_survey_blob_pin_drift,phase9_build_manifest_blob_pin_drift,phase9_build_survey_blob_pin_drift,doc_readme_blob_pin_drift,script_readme_blob_pin_drift,tests_readme_blob_pin_drift,gate_evidence_self_test_case_count_drift,gate_evidence_self_test_cases_drift,shared_validator_reruns_gate_evidence_check_drift,shared_validator_reruns_gate_evidence_self_test_drift,shared_validator_expected_target_count_drift,shared_validator_expected_self_test_case_count_drift,runtime_atomic64_survey_packet_presence_drift,bitmap_diff_survey_replay_marker_drift,workflow_route_checker_matrix_presence_drift,kprobe_gap_packet_presence_drift,kprobe_owner_drift,kprobe_validation_entrypoint_drift,kprobe_next_step_drift,perf_baseline_packet_presence_drift,perf_baseline_note_split_marker_drift,perf_baseline_owner_drift,perf_baseline_shared_promotion_status_drift,test_fsmount_gap_packet_presence_drift,test_fsmount_threshold_posture_drift,test_fsmount_owner_drift,test_fsmount_validation_entrypoint_drift,test_fsmount_linux_style_wrapper_drift,test_fsmount_next_step_drift,missing_validator_file,missing_phase4_build_file,missing_artifact_diff_helper_file,missing_atomic64_manifest_file,missing_bitmap_survey_file,missing_perf_survey_file,missing_kprobe_manifest_file,missing_test_fsmount_survey_file,missing_note_file`
  * `PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true`
  * `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true`
  * `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true`
  * `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=19`
  * `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=44`
  * `PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`
  * `PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true`
  * `PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=true`
  * `PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true`

## Exact Readback Evidence
  * `scripts/zigux/check-phase4-gate-evidence.py` now recomputes the broader packet blob pins from live file contents so stale readback evidence fails closed.
  * The runtime atomic64 handoff remains reviewable through `phase4-runtime-atomic64-diff-survey-tests`, `make -C zigux phase4-runtime-atomic64-diff-survey`, two `inc_not_zero` checks, and three `dec_if_positive` checks.
  * The adjacent local-only perf packet remains explicit through `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, and the shared posture that local-only benchmark commands and acceptable limits are approved today while shared CI perf promotion pending remains unchanged.
  * `scripts/zigux/check-phase4-workflow-route-counts.py` keeps the shared `make -C zigux phase4-validate` and `make -C zigux phase4-test` wrapper inventory explicit beside the dedicated local survey wrappers so the validator-first route packet cannot drift away from this exact-readback note unnoticed.
  * The parked starter-gap packet keeps `PHASE4_KPROBE_SHARED_LAB_AND_CI_MATRIX_ANCHOR=Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix` explicit beside the current `make -C zigux phase4-kprobe-example-survey` and `make -C zigux phase4-test-fsmount-survey` wrappers.
