# Phase 4 Gate Evidence

This note records the last fully pinned broader Phase 4 rollback-ownership and lab-matrix packet. Keep the narrower reversible-delivery handoff as the direct-readback source when authenticated contents reads for the broader packet still flap, while the local-only perf and parked survey packets remain intentionally separate.

## Status
  * `PHASE4_EVIDENCE_DATE=2026-05-19`
  * `PHASE4_EVIDENCE_MODE=github_connector_readback`
  * `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`
  * `PHASE4_EXACT_READBACK_REF=master`
  * `PHASE4_VALIDATION_MATRIX_BLOB_SHA=44955f39e37b9389b3b97e7d710c25b1841aedf3`
  * `PHASE4_VALIDATOR_BLOB_SHA=dea77e6385618147aba44d3714f73b6c5249e942`
  * `PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=95471df68eea2537ea547394d0311c2939ae0d33`
  * `PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=ef333c03fa97927b2be0152b613fab727bb89a11`
  * `PHASE4_ARTIFACT_DIFF_DOC_BLOB_SHA=5173368ba7f69587f6839931b380f1e77c456933`
  * `PHASE4_ARTIFACT_DIFF_CONTRACT_CHECKER_BLOB_SHA=b8fea944496bfd7e058778d8d6f8f09c2f4e5a2d`
  * `PHASE4_BUILD_BLOB_SHA=86f88d03cd82e2e11ea6ed4a02175b77b472fdb4`
  * `PHASE4_MAKEFILE_BLOB_SHA=b71641c73d23d5fde48a1bb7808c3207e9b2ed4b`
  * `PHASE4_WORKFLOW_BLOB_SHA=e07b69eaf4070b83f943e1ad41cf1a47bdc532fa`
  * `PHASE4_DOC_README_BLOB_SHA=ac515e3ed47c771b0947fde4200a90b9a1952c99`
  * `PHASE4_SCRIPT_README_BLOB_SHA=4b22006c7278280203a23e6ec568cf8f47b62c7e`
  * `PHASE4_TESTS_README_BLOB_SHA=107d5d300f43fb5c9b0c7f9439601af3507a59ff`
  * `PHASE4_ATOMIC64_DIFF_BLOB_SHA=86d3b9e3e544bda6b24399e7a2d226cb18e19ddf`
  * `PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA=9ad41de72613cd72273b41c9cf2a64a0c46962df`
  * `PHASE4_BITMAP_DIFF_BLOB_SHA=683160d3a86552a2a1be34b445fd6e0fb38dc122`
  * `PHASE4_BITMAP_LIVE_HELPER_REPLAY_BLOB_SHA=4a4c07e5f7b90fc96f06c86a17d3d30aa0d5b694`
  * `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=6e486e059c0d1caa9599c5ac54936f7c52ac8e9a`
  * `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=65c2ceed2512dcec8f86cbe3c47831c30f5547d3`
  * `PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA=0c38a3e7470f92b5b38da8659c548a51dbd09440`
  * `PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=19`
  * `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=42`
  * `PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=baseline_round_trip,shipped_target_count_drift,missing_exact_readback_heading,validator_blob_pin_drift,phase4_build_manifest_blob_pin_drift,phase4_build_survey_blob_pin_drift,phase9_build_manifest_blob_pin_drift,phase9_build_survey_blob_pin_drift,doc_readme_blob_pin_drift,script_readme_blob_pin_drift,tests_readme_blob_pin_drift,gate_evidence_self_test_case_count_drift,gate_evidence_self_test_cases_drift,shared_validator_reruns_gate_evidence_check_drift,shared_validator_reruns_gate_evidence_self_test_drift,shared_validator_expected_target_count_drift,shared_validator_expected_self_test_case_count_drift,runtime_atomic64_survey_packet_presence_drift,bitmap_diff_survey_replay_marker_drift,kprobe_gap_packet_presence_drift,kprobe_owner_drift,kprobe_validation_entrypoint_drift,kprobe_next_step_drift,perf_baseline_packet_presence_drift,perf_baseline_note_split_marker_drift,perf_baseline_owner_drift,perf_baseline_shared_promotion_status_drift,test_fsmount_gap_packet_presence_drift,test_fsmount_threshold_posture_drift,test_fsmount_owner_drift,test_fsmount_validation_entrypoint_drift,test_fsmount_linux_style_wrapper_drift,test_fsmount_next_step_drift,missing_validator_file,missing_phase4_build_file,missing_artifact_diff_helper_file,missing_atomic64_manifest_file,missing_bitmap_survey_file,missing_perf_survey_file,missing_kprobe_manifest_file,missing_test_fsmount_survey_file,missing_note_file`
  * `PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true`
  * `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true`
  * `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true`
  * `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=19`
  * `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=42`
  * `PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`
  * `PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true`
  * `PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=true`
  * `PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true`

## Exact Readback Evidence
  * Public current-`master` fallback rereads of `Documentation/zigux/artifact-diff.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, and the dedicated `scripts/zigux/check-phase4-workflow-route-counts.py` checker keep the broader Phase 4 rollback-readiness packet reviewable even while authenticated contents reads can still flap for some of those companions, including the dedicated local-only `scripts/zigux/check-phase4-perf-baseline-packet.py` checker, the local-only perf-baseline survey files, and the matching direct `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` and Linux-style `make -C zigux phase4-perf-baseline-survey` replay routes.
  * Use `Documentation/zigux/phase4-reversible-delivery-evidence.md` as the narrower direct-readback handoff while `scripts/zigux/check-phase4-gate-evidence.py` continues to guard this broader rollback-ownership note and `scripts/zigux/check-phase4-perf-baseline-packet.py` keeps the adjacent local-only perf packet exact.
  * The current bounded bitmap rollback gate in `zigux/tests/bitmap_diff.zig` and the shipped helper replay in `zigux/tests/phase4_bitmap_live_helper_replay.zig` remain reviewable through the direct `zig build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig` and Linux-style `make -C zigux phase4-bitmap-live-helper-replay` replays. This note now keeps the exact bitmap rollback inventory explicit: thirteen bounded range and prefix cases, two `find_nth_bit` replays, sixteen copy-tail cases, explicit zero-length range/prefix and zero-length copy no-op coverage, explicit partial-word 109-bit replay that keeps copied source tail bits through bit 126, matching pre-filled 109-bit replay that clears the padded tail before the filled tail resumes, aligned 97-bit copy replay that keeps the second copied word intact before the cleared tail resumes, bounded out-of-bounds rejection coverage, explicit rollback-governance and manifest-backed rollback-packet alignment coverage, empty-batch rejection for `runThresholdReplay(0)`, deterministic threshold replays for `runThresholdReplay(1)` and `runThresholdReplay(4)` with checksums `5216946504564592253` and `7942141539243507472`, final markers `final_first_zero=109`, `final_weight=1005`, and `final_nth_seven=123`, a current source-inventory tally of `13 DiffCase`, `16 CopyCase`, and `13 mixThresholdChecksum()` checkpoints, and the exact helper-facing fill and zero anchors `bitmap_fill(..., 35)`, `bitmap_fill(..., 115)`, `bitmap_zero(..., 35)`, and `bitmap_zero(..., 115)` with the rounded 64 and 128 visible beside them in `lib/test_bitmap.c`.
  * That narrower handoff still keeps the parked kprobe packet's shared matrix anchor explicit as `PHASE4_KPROBE_SHARED_LAB_AND_CI_MATRIX_ANCHOR=Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix`, so the broader rollback-ownership note now carries forward the same matrix-anchor discipline beside the current `make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m` Linux replay, the dedicated `make -C zigux phase4-kprobe-example-survey` local replay, and the existing `Validation and Perf Team` ownership pair while `samples/zigux/kprobe_example.zig` remains intentionally absent.
