# Phase 4 Gate Evidence

## Status
  * `PHASE4_VALIDATION_MATRIX_BLOB_SHA=33d4fa1a339ef355621b5596420c5f1601ffe3cd`
  * `PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=c1fa46fad53adc7327a03fbe12d3510e854e8bfa`
  * `PHASE4_ARTIFACT_DIFF_DOC_BLOB_SHA=c7467097823b0a0968036cfcf83030074ce4a4fd`
  * `PHASE4_ARTIFACT_DIFF_HELPER_BLOB_SHA=4dc6294c98aea9475d4d5965ac541cab9a7dc725`
  * `PHASE4_ARTIFACT_DIFF_CONTRACT_CHECKER_BLOB_SHA=b566704292eb9d58d7c0736e3fdc6e22ce8a1e8d`
  * `PHASE4_MAKEFILE_BLOB_SHA=86af6657cf4abec7ed7ca07bec82c051d974e327`
  * `PHASE4_WORKFLOW_BLOB_SHA=8c7fdf65ee906111f8d9a1468cb52bfa8d242763`
  * `PHASE4_DOC_README_BLOB_SHA=dc07edabf4236743a141850f5df2e5c4f05ff342`
  * `PHASE4_SCRIPT_README_BLOB_SHA=d318cf01b3f25e9ba0ad756e4ebcc23de3070323`
  * `PHASE4_TESTS_README_BLOB_SHA=9f6d435f401e92b1f073d1cd8ef60853165494a9`
  * `PHASE4_VALIDATOR_BLOB_SHA=ff0ce79cfda11991f7bdbe1ab3b6b9b6145daf3f`
  * `PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=560dc13c941f42585b86a46f265d37dd167012b9`
  * `PHASE4_ATOMIC64_DIFF_BLOB_SHA=dc399ea34ecae4a747ae77ca29cf8b0780680336`
  * `PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA=907c937190fcb0266d58cb80bcff44ccf6092874`
  * `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=d0588889fa4001257944188661a9d204f17ec199`
  * `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=ef0e3d311379ea1b96e515b304f0ad599832148a`
  * `PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA=ab9d72d33cc03d35fc3ec06ebfeac428f2ae0a38`
  * `PHASE4_PHASE9_BUILD_BLOB_SHA=a2852900fb265c6afd4c78f397c516775e0bb039`
  * `PHASE4_REVERSIBLE_DELIVERY_EVIDENCE_BLOB_SHA=f718a139114fce8fc6a9cccb84a58047ac16378b`
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
  * The bounded bitmap rollback packet stays directly reviewable through `PHASE4_BITMAP_DIFF_BLOB_SHA=683160d3a86552a2a1be34b445fd6e0fb38dc122` and `PHASE4_BITMAP_LIVE_HELPER_REPLAY_BLOB_SHA=4a4c07e5f7b90fc96f06c86a17d3d30aa0d5b694`, keeping the roadmap-named synthetic gate and the shipped helper-backed replay explicit on the same exact-readback note.
  * That same bitmap packet keeps a current source-inventory tally of `13 DiffCase`, `16 CopyCase`, and `13 mixThresholdChecksum()` checkpoints beside the exact 35-bit and 115-bit `bitmap_fill` prefixes plus the rounded 64-bit and 128-bit `bitmap_zero` boundaries.
  * The adjacent local-only perf packet remains explicit through `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, and the shared posture that local-only benchmark commands and acceptable limits are approved today while shared CI perf promotion pending remains unchanged.
  * `scripts/zigux/check-phase4-workflow-route-counts.py` keeps the shared `make -C zigux phase4-validate` and `make -C zigux phase4-test` wrapper inventory explicit beside the dedicated local survey wrappers so the validator-first route packet cannot drift away from this exact-readback note unnoticed.
  * The parked starter-gap packet keeps `PHASE4_KPROBE_SHARED_LAB_AND_CI_MATRIX_ANCHOR=Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix` explicit beside the current `make -C zigux phase4-kprobe-example-survey` and `make -C zigux phase4-test-fsmount-survey` wrappers.
