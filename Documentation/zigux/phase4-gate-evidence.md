# Phase 4 Gate Evidence

## Status
  * `PHASE4_VALIDATION_MATRIX_BLOB_SHA=33d4fa1a339ef355621b5596420c5f1601ffe3cd`
  * `PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=5d3b4d2decdc365cd3a11309d6e6187784f7a60d`
  * `PHASE4_ARTIFACT_DIFF_DOC_BLOB_SHA=7a20701fa439396b453253ee939804887d45006e`
  * `PHASE4_ARTIFACT_DIFF_HELPER_BLOB_SHA=4dc6294c98aea9475d4d5965ac541cab9a7dc725`
  * `PHASE4_ARTIFACT_DIFF_CONTRACT_CHECKER_BLOB_SHA=b566704292eb9d58d7c0736e3fdc6e22ce8a1e8d`
  * `PHASE4_MAKEFILE_BLOB_SHA=f8a77048231db020d06faa87f98e21908dc4bb6e`
  * `PHASE4_WORKFLOW_BLOB_SHA=5d07f69d341f667c96f59a26cd6957870c54997f`
  * `PHASE4_DOC_README_BLOB_SHA=43f3753ef4eed8998b07c526870808351b304784`
  * `PHASE4_SCRIPT_README_BLOB_SHA=918c12e08f4bb2e3ba1c6d1059a68038a28aecf4`
  * `PHASE4_TESTS_README_BLOB_SHA=4157319721f7e4847c8072860ba1fd44b0476de8`
  * `PHASE4_VALIDATOR_BLOB_SHA=c74df1e03d4c08c332e2ee2e0954757f29bea3ee`
  * `PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=560dc13c941f42585b86a46f265d37dd167012b9`
  * `PHASE4_ATOMIC64_DIFF_BLOB_SHA=bcf360cf079506403c699d53899af673ef8ae21b`
  * `PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA=907c937190fcb0266d58cb80bcff44ccf6092874`
  * `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=f5bca8487f4088502bf9d52007e375e067e3243c`
  * `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=ef0e3d311379ea1b96e515b304f0ad599832148a`
  * `PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA=da5a889c5cd3b7fb9c98d6789d04ad473564f16c`
  * `PHASE4_PHASE9_BUILD_BLOB_SHA=00e36f379dc2e4ee4baf3246ccefe815ccd191b5`
  * `PHASE4_REVERSIBLE_DELIVERY_EVIDENCE_BLOB_SHA=3f736fdb079fb22ad56223b7926495e150b3da71`
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
  * The broader bitmap rollback packet stays intentionally outside this exact-readback note on current `master` even though the public `zigux/tests` tree again exposes `zigux/tests/bitmap_diff.zig` and `zigux/tests/phase4_bitmap_live_helper_replay.zig`; this note remains focused on the narrower shared validator packet while the broader bitmap rollback details stay reviewable through the surrounding matrix and the paired bitmap survey packet.
  * The broader bitmap reviewability details still belong in the surrounding matrix and reminder packet rather than this exact-readback note while the shared validator-first packet stays narrower than the coupled bitmap survey surfaces on current `master`.
  * The adjacent local-only perf packet remains explicit through `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, and the shared posture that local-only benchmark commands and acceptable limits are approved today while shared CI perf promotion pending remains unchanged.
  * `scripts/zigux/check-phase4-workflow-route-counts.py` keeps the shared `make -C zigux phase4-validate` and `make -C zigux phase4-test` wrapper inventory explicit beside the dedicated local survey wrappers so the validator-first route packet cannot drift away from this exact-readback note unnoticed.
  * The parked starter-gap packet keeps `PHASE4_KPROBE_SHARED_LAB_AND_CI_MATRIX_ANCHOR=Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix` explicit beside the current `make -C zigux phase4-kprobe-example-survey` and `make -C zigux phase4-test-fsmount-survey` wrappers.
