# Phase 4 Gate Evidence

## Status
  * `PHASE4_VALIDATION_MATRIX_BLOB_SHA=a50b256e9a7107a0fbb7c5dc2dab2260231cbc8e`
  * `PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=745a25f03ec45209097782ce7bfc406c939541ad`
  * `PHASE4_ARTIFACT_DIFF_DOC_BLOB_SHA=6633784ab6d5bd5da285bf6f802798990a8915a0`
  * `PHASE4_ARTIFACT_DIFF_HELPER_BLOB_SHA=4dc6294c98aea9475d4d5965ac541cab9a7dc725`
  * `PHASE4_ARTIFACT_DIFF_CONTRACT_CHECKER_BLOB_SHA=48e611aa0a53540d8594dbb5c2200bb258d03d08`
  * `PHASE4_MAKEFILE_BLOB_SHA=fbd6ff2e28f7926b49f82ad8cc8f7ec8cec4a60d`
  * `PHASE4_WORKFLOW_BLOB_SHA=142d92756396fe3ebf97bbc1da1ceba6c022a652`
  * `PHASE4_DOC_README_BLOB_SHA=ae45c1e30a338737496fc1cce4a2952f7921a68f`
  * `PHASE4_SCRIPT_README_BLOB_SHA=75e38753d526ec904fb6e0c2fe8773ebde2e205d`
  * `PHASE4_TESTS_README_BLOB_SHA=e385b78c446a089b711eb84256b44a760353551e`
  * `PHASE4_VALIDATOR_BLOB_SHA=b5eec709a027c76ffb1cba804757b54e3cdbeaef`
  * `PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=f8c3ad615dc7a9e77a3d6021b032f7e6cf8c084e`
  * `PHASE4_ATOMIC64_DIFF_BLOB_SHA=5410a951d9a31752b073fd4d8adc94fda60a54ab`
  * `PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA=907c937190fcb0266d58cb80bcff44ccf6092874`
  * `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=6f8eb7cb4be4e7fefa2fa9257f5739d1828a442d`
  * `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=bd47839a3b0b6f4c5891334c473227150bcc0ca6`
  * `PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA=eebac7e49e82339037058afbe9fc6cd00fa185b4`
  * `PHASE4_PHASE9_BUILD_BLOB_SHA=58b1db12c1bc65d5068c9f49fe4a7b5d65c40254`
  * `PHASE4_REVERSIBLE_DELIVERY_EVIDENCE_BLOB_SHA=5b6004c666643e89c8f1775081587cc8c69e25bd`
  * `PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=19`
  * `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=44`
  * `PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=baseline_round_trip,shipped_target_count_drift,missing_exact_readback_heading,forbidden_gate_evidence_checker_self_pin,validator_blob_pin_drift,phase4_build_manifest_blob_pin_drift,phase4_build_survey_blob_pin_drift,phase9_build_manifest_blob_pin_drift,phase9_build_survey_blob_pin_drift,doc_readme_blob_pin_drift,script_readme_blob_pin_drift,tests_readme_blob_pin_drift,gate_evidence_self_test_case_count_drift,gate_evidence_self_test_cases_drift,shared_validator_reruns_gate_evidence_check_drift,shared_validator_reruns_gate_evidence_self_test_drift,shared_validator_expected_target_count_drift,shared_validator_expected_self_test_case_count_drift,runtime_atomic64_survey_packet_presence_drift,bitmap_manifest_gate_evidence_blob_drift,workflow_route_checker_matrix_presence_drift,kprobe_gap_packet_presence_drift,kprobe_owner_drift,kprobe_validation_entrypoint_drift,kprobe_next_step_drift,perf_baseline_packet_presence_drift,perf_baseline_note_split_marker_drift,perf_baseline_owner_drift,perf_baseline_shared_promotion_status_drift,test_fsmount_gap_packet_presence_drift,test_fsmount_threshold_posture_drift,test_fsmount_owner_drift,test_fsmount_validation_entrypoint_drift,test_fsmount_linux_style_wrapper_drift,test_fsmount_next_step_drift,missing_validator_file,missing_phase4_build_file,missing_artifact_diff_helper_file,missing_atomic64_manifest_file,missing_bitmap_manifest_file,missing_perf_survey_file,missing_kprobe_manifest_file,missing_test_fsmount_survey_file,missing_note_file`
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
  * The broader bitmap rollback packet stays intentionally outside this exact-readback note on current `master` even though the public `zigux/tests` tree again exposes `zigux/tests/bitmap_diff.zig` and `zigux/tests/phase4_bitmap_live_helper_replay.zig`; this note remains focused on the narrower shared validator packet while the broader bitmap rollback details stay reviewable through the surrounding matrix and the paired bitmap survey packet.
  * The broader bitmap reviewability details still belong in the surrounding matrix and reminder packet rather than this exact-readback note while the shared validator-first packet stays narrower than the coupled bitmap survey surfaces on current `master`.
  * The adjacent local-only perf packet remains explicit through `scripts/zigux/check-phase4-perf-baseline-packet.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, and the shared posture that local-only benchmark commands and acceptable limits are approved today while shared CI perf promotion pending remains unchanged.
  * `scripts/zigux/check-phase4-workflow-route-counts.py` keeps the shared `make -C zigux phase4-validate`, `make -C zigux phase4-artifact-diff-contract`, and `make -C zigux phase4-test` wrapper inventory explicit beside the dedicated local survey wrappers so the validator-first route packet cannot drift away from this exact-readback note unnoticed.
  * The parked starter-gap packet keeps `PHASE4_KPROBE_SHARED_LAB_AND_CI_MATRIX_ANCHOR=Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix` explicit beside the current `make -C zigux phase4-kprobe-example-survey` and `make -C zigux phase4-test-fsmount-survey` wrappers.
