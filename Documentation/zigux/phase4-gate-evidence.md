# Phase 4 Gate Evidence

## Status
  * `PHASE4_VALIDATION_MATRIX_BLOB_SHA=dbafcded83a29dcc82bbb54d45cab310a58faf8c`
  * `PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=0b1032c1de0aa4f4250422887bdd53e93797438f`
  * `PHASE4_ARTIFACT_DIFF_DOC_BLOB_SHA=89f6ae2df1ecb3d06663215d3cebf2fdd9f955ae`
  * `PHASE4_ARTIFACT_DIFF_HELPER_BLOB_SHA=3ff77318f7511d889e15a5b482d7fa486029ed09`
  * `PHASE4_ARTIFACT_DIFF_CONTRACT_CHECKER_BLOB_SHA=48e611aa0a53540d8594dbb5c2200bb258d03d08`
  * `PHASE4_MAKEFILE_BLOB_SHA=a541b6c33f1735bead90035d204cc5cb643e9712`
  * `PHASE4_WORKFLOW_BLOB_SHA=91a261679c9c2a8eafe203d80cd4d2cefacfdd87`
  * `PHASE4_DOC_README_BLOB_SHA=d519f36203a5ecde12db3c9f0735b31563aa04a5`
  * `PHASE4_SCRIPT_README_BLOB_SHA=8a0da62e51e30a7a51c8e8ff7a5a6bfa53bc9471`
  * `PHASE4_TESTS_README_BLOB_SHA=9e5384cbd33a291d58c2dc85f3a842dadb0215cb`
  * `PHASE4_VALIDATOR_BLOB_SHA=9fefd6a4f47a8e7b9d1b7e4f68755a4ffee9d6fb`
  * `PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=84136423c1b93657f1d3ee86f40a3880003a91ad`
  * `PHASE4_ATOMIC64_DIFF_BLOB_SHA=099b9601095176340fa05973449ca2506195def9`
  * `PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA=907c937190fcb0266d58cb80bcff44ccf6092874`
  * `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=c5fbc0784cb36643146ec67133c100749c51a310`
  * `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=87b72410a69b90e0cd4377ac30f7c47d0d9943c2`
  * `PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA=ec333b158200aeed62eefbcfd6046a835dcec6c4`
  * `PHASE4_PHASE9_BUILD_BLOB_SHA=0a093698e7bee23e37b6eb2fceae57bbe310ad29`
  * `PHASE4_REVERSIBLE_DELIVERY_EVIDENCE_BLOB_SHA=7d8c81efa27ae3f763c0d630131e749fd6278c12`
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
  * The broader bitmap rollback packet stays intentionally outside this exact-readback note on current `master` even though the public `zigux/tests` tree again exposes `zigux/tests/bitmap_diff.zig` and `zigux/tests/phase4_bitmap_live_helper_replay.zig`; this note remains focused on the narrower shared validator packet while the broader bitmap rollback details stay reviewable through the surrounding matrix and the paired bitmap survey packet.
  * The paired bitmap survey packet also keeps the already-landed zero-length range and prefix no-op checks plus the zero-length copy invariant explicit beside the exact 35-bit and 115-bit synthetic fill prefixes and the rounded 64-bit and 128-bit zero boundaries.
  * The broader bitmap reviewability details still belong in the surrounding matrix and reminder packet rather than this exact-readback note while the shared validator-first packet stays narrower than the coupled bitmap survey surfaces on current `master`.
  * The adjacent local-only perf packet remains explicit through `scripts/zigux/check-phase4-perf-baseline-packet.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, and the shared posture that local-only benchmark commands and acceptable limits are approved today while shared CI perf promotion pending remains unchanged.
  * `scripts/zigux/check-phase4-workflow-route-counts.py` keeps the shared `make -C zigux phase4-validate`, `make -C zigux phase4-artifact-diff-contract`, and `make -C zigux phase4-test` wrapper inventory explicit beside the dedicated local survey wrappers so the validator-first route packet cannot drift away from this exact-readback note unnoticed.
  * The parked starter-gap packet keeps `PHASE4_KPROBE_SHARED_LAB_AND_CI_MATRIX_ANCHOR=Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix` explicit beside the current `make -C zigux phase4-kprobe-example-survey` and `make -C zigux phase4-test-fsmount-survey` wrappers.
