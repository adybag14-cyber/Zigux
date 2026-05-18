# Phase 4 Gate Evidence

This note records the last fully pinned broader Phase 4 rollback-ownership and lab-matrix packet. Keep the narrower reversible-delivery handoff as the direct-readback source when authenticated contents reads for the broader packet still flap, while the local-only perf and parked survey packets remain intentionally separate.
## Status
  * `PHASE4_EVIDENCE_DATE=2026-05-18`
  * `PHASE4_EVIDENCE_MODE=github_connector_readback`
  * `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`
  * `PHASE4_EXACT_READBACK_REF=master`
  * `PHASE4_VALIDATION_MATRIX_BLOB_SHA=d73679558764fcdd3fcc9962c59d4e28bf3a3b6f`
  * `PHASE4_VALIDATOR_BLOB_SHA=694ad85743612aa0a595cd1752dd03c1013603ab`
  * `PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=7b913e4ba293354fd841934a449697d230dec25a`
  * `PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=57ecc3199ca4608828771456f8b6c417c4ab9f1c`
  * `PHASE4_ARTIFACT_DIFF_DOC_BLOB_SHA=5173368ba7f69587f6839931b380f1e77c456933`
  * `PHASE4_ARTIFACT_DIFF_CONTRACT_CHECKER_BLOB_SHA=b8fea944496bfd7e058778d8d6f8f09c2f4e5a2d`
  * `PHASE4_BUILD_BLOB_SHA=86f88d03cd82e2e11ea6ed4a02175b77b472fdb4`
  * `PHASE4_MAKEFILE_BLOB_SHA=5da552c676a6522e5494b3c24fcffab647cef893`
  * `PHASE4_WORKFLOW_BLOB_SHA=20327887d490ac94feda047293e0ba320aabe3a5`
  * `PHASE4_DOC_README_BLOB_SHA=aea315a1bec0d9affeb429c3bc840ebe2223d1de`
  * `PHASE4_SCRIPT_README_BLOB_SHA=c1259eb7537b336b7e5d1ecf29c3081cdabd9877`
  * `PHASE4_TESTS_README_BLOB_SHA=ef0d5e908f05aae9c2e4ac7fa58ed492d95480ba`
  * `PHASE4_ATOMIC64_DIFF_BLOB_SHA=846d8afb1319a4f31d3522a29cb42a34a4a9a065`
  * `PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA=73d7d86e04bca860d2a8845e442d02eca7ce8d2c`
  * `PHASE4_BITMAP_DIFF_BLOB_SHA=683160d3a86552a2a1be34b445fd6e0fb38dc122`
  * `PHASE4_BITMAP_LIVE_HELPER_REPLAY_BLOB_SHA=4a4c07e5f7b90fc96f06c86a17d3d30aa0d5b694`
  * `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=a3493c3039fc771ce59c967d6a80df93bba2bd2e`
  * `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=a4d7606eb18969dc5150e4ee43a02cda643972eb`
  * `PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA=7d064cd234e87f7a1b6c23bcbed43334d3334e6a`
  * `PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=19`
  * `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=34`
  * `PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=baseline_round_trip,shipped_target_count_drift,missing_exact_readback_heading,validator_blob_pin_drift,phase4_build_manifest_blob_pin_drift,phase4_build_survey_blob_pin_drift,phase9_build_manifest_blob_pin_drift,phase9_build_survey_blob_pin_drift,doc_readme_blob_pin_drift,script_readme_blob_pin_drift,tests_readme_blob_pin_drift,gate_evidence_self_test_case_count_drift,gate_evidence_self_test_cases_drift,shared_validator_reruns_gate_evidence_check_drift,shared_validator_reruns_gate_evidence_self_test_drift,shared_validator_expected_target_count_drift,shared_validator_expected_self_test_case_count_drift,runtime_atomic64_survey_packet_presence_drift,bitmap_diff_survey_replay_marker_drift,kprobe_gap_packet_presence_drift,kprobe_owner_drift,kprobe_validation_entrypoint_drift,kprobe_next_step_drift,perf_baseline_packet_presence_drift,perf_baseline_note_split_marker_drift,perf_baseline_owner_drift,perf_baseline_shared_promotion_status_drift,test_fsmount_gap_packet_presence_drift,test_fsmount_threshold_posture_drift,test_fsmount_owner_drift,test_fsmount_validation_entrypoint_drift,test_fsmount_linux_style_wrapper_drift,test_fsmount_next_step_drift,missing_note_file`
  * `PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true`
  * `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true`
  * `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true`
  * `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=19`
  * `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=34`
  * `PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`
  * `PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true`
  * `PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=true`
  * `PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true`
## Exact Readback Evidence
  * Public current-`master` fallback rereads of `Documentation/zigux/artifact-diff.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, and the dedicated `scripts/zigux/check-phase4-workflow-route-counts.py` checker keep the broader Phase 4 rollback-readiness packet reviewable even while authenticated contents reads can still flap for some of those companions, including the dedicated local-only perf-baseline survey files plus the matching direct `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` and Linux-style `make -C zigux phase4-perf-baseline-survey` replay routes.
  * Use `Documentation/zigux/phase4-reversible-delivery-evidence.md` as the narrower direct-readback handoff while `scripts/zigux/check-phase4-gate-evidence.py` continues to guard this broader rollback-ownership note.
  * That narrower handoff still keeps the parked kprobe packet's shared matrix anchor explicit as `PHASE4_KPROBE_SHARED_LAB_AND_CI_MATRIX_ANCHOR=Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix`, so the broader rollback-ownership note now carries forward the same matrix-anchor discipline beside the current `make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m` Linux replay, the dedicated `make -C zigux phase4-kprobe-example-survey` local replay, and the existing `Validation and Perf Team` ownership pair while `samples/zigux/kprobe_example.zig` remains intentionally absent.
