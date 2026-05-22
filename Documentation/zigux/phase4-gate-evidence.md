# Phase 4 Gate Evidence

## Status
  * `PHASE4_VALIDATION_MATRIX_BLOB_SHA=33d4fa1a339ef355621b5596420c5f1601ffe3cd`
  * `PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=c1fa46fad53adc7327a03fbe12d3510e854e8bfa`
  * `PHASE4_ARTIFACT_DIFF_DOC_BLOB_SHA=e3f960cf890ab4329e4995fe5edc0f89d7491dd4`
  * `PHASE4_ARTIFACT_DIFF_HELPER_BLOB_SHA=4dc6294c98aea9475d4d5965ac541cab9a7dc725`
  * `PHASE4_ARTIFACT_DIFF_CONTRACT_CHECKER_BLOB_SHA=b566704292eb9d58d7c0736e3fdc6e22ce8a1e8d`
  * `PHASE4_MAKEFILE_BLOB_SHA=3f0f3c7ecad755e76eedbddc970f02794115e814`
  * `PHASE4_WORKFLOW_BLOB_SHA=6204d59a34533b931cb84c5e0190ae25e2074931`
  * `PHASE4_DOC_README_BLOB_SHA=306b824188945a1e197cb08aec13eda3f42b53ea`
  * `PHASE4_SCRIPT_README_BLOB_SHA=e6d4c941b4a3cb3904c8a51d9972ed77049f6bc6`
  * `PHASE4_TESTS_README_BLOB_SHA=a1ec46312cd948614f1bfd8479818f85165f4253`
  * `PHASE4_VALIDATOR_BLOB_SHA=e4b89c34c26a3886d2d28641ed16a0b25fc9dd67`
  * `PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=560dc13c941f42585b86a46f265d37dd167012b9`
  * `PHASE4_ATOMIC64_DIFF_BLOB_SHA=dc399ea34ecae4a747ae77ca29cf8b0780680336`
  * `PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA=907c937190fcb0266d58cb80bcff44ccf6092874`
  * `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=7dc51c0c5e7e3a3dbb2e83c1fedc719631c4db55`
  * `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=ef0e3d311379ea1b96e515b304f0ad599832148a`
  * `PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA=da5a889c5cd3b7fb9c98d6789d04ad473564f16c`
  * `PHASE4_PHASE9_BUILD_BLOB_SHA=82494784ceddaf6d26edef3bd2d056edb232da4d`
  * `PHASE4_REVERSIBLE_DELIVERY_EVIDENCE_BLOB_SHA=49e782e805617cecb759f2c5f767eb1f120b8d71`
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
  * The broader bitmap rollback packet is intentionally outside this exact-readback note on current `master`: the public `zigux/tests` tree no longer exposes `zigux/tests/bitmap_diff.zig` or `zigux/tests/phase4_bitmap_live_helper_replay.zig`, so this note stays narrowed to directly readable rollback-ownership surfaces until a later bounded Phase 4 lane restores openly readable bitmap replay coverage that can be blob-pinned again.
  * The broader bitmap reviewability details still belong in the surrounding matrix and reminder packet rather than this exact-readback note while those replay files stay outside the directly readable `zigux/tests` Phase 4 surface on current `master`.
  * The adjacent local-only perf packet remains explicit through `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, and the shared posture that local-only benchmark commands and acceptable limits are approved today while shared CI perf promotion pending remains unchanged.
  * `scripts/zigux/check-phase4-workflow-route-counts.py` keeps the shared `make -C zigux phase4-validate` and `make -C zigux phase4-test` wrapper inventory explicit beside the dedicated local survey wrappers so the validator-first route packet cannot drift away from this exact-readback note unnoticed.
  * The parked starter-gap packet keeps `PHASE4_KPROBE_SHARED_LAB_AND_CI_MATRIX_ANCHOR=Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix` explicit beside the current `make -C zigux phase4-kprobe-example-survey` and `make -C zigux phase4-test-fsmount-survey` wrappers.
