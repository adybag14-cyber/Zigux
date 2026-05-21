# Phase 4 Gate Evidence

This note records the current broader Phase 4 rollback-ownership and lab-matrix checkpoint: directly readable companions stay blob-pinned here, while the validator, shared build, and bitmap replay branch stays explicit as public-raw current-`master` evidence until exact authenticated blob refresh returns.

## Status
  * `PHASE4_EVIDENCE_DATE=2026-05-21`
  * `PHASE4_EVIDENCE_MODE=github_connector_readback`
  * `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_direct_readback_plus_raw_fallback_split`
  * `PHASE4_EXACT_READBACK_REF=master`
  * `PHASE4_VALIDATION_MATRIX_BLOB_SHA=0c243dd80d8ff192d43c3f2db0ca36a2f8e5f77c`
  * `PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=c1fa46fad53adc7327a03fbe12d3510e854e8bfa`
  * `PHASE4_ARTIFACT_DIFF_DOC_BLOB_SHA=5173368ba7f69587f6839931b380f1e77c456933`
  * `PHASE4_ARTIFACT_DIFF_CONTRACT_CHECKER_BLOB_SHA=92696cb02fc915fec0f5f1c4c2768a99cf99c9bf`
  * `PHASE4_MAKEFILE_BLOB_SHA=2123cbb48f7bb32293c1bb3dead619e6d437923b`
  * `PHASE4_WORKFLOW_BLOB_SHA=a4aad5b4904fb2d68f63921dc7693eea94f80780`
  * `PHASE4_DOC_README_BLOB_SHA=faa69f9fca3e5d8cf328a904dc8cbc618ba0d017`
  * `PHASE4_SCRIPT_README_BLOB_SHA=2908674dd61bbceb0b7a7474627dd4235e500ed0`
  * `PHASE4_TESTS_README_BLOB_SHA=157b874862299ac71c80b51aa3da1b5a9e7cb3d4`
  * `PHASE4_ATOMIC64_DIFF_BLOB_SHA=e84bf84b5e24428d596fe25502512fa24ce28b51`
  * `PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA=9ad41de72613cd72273b41c9cf2a64a0c46962df`
  * `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=a28a7393df1b270de8c80c57c30287d548bd0c4e`
  * `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=fa4ab6b736a3eba358630a9913b447f77569ab29`
  * `PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA=41557595b640e28985629285d40f7ad16e52340f`
  * `PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=15`
  * `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=46`
  * `PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=baseline_round_trip,shipped_target_count_drift,missing_exact_readback_heading,forbidden_gate_evidence_checker_self_pin,phase4_build_manifest_blob_pin_drift,makefile_blob_pin_drift,phase9_build_survey_blob_pin_drift,doc_readme_blob_pin_drift,script_readme_blob_pin_drift,tests_readme_blob_pin_drift,atomic64_diff_blob_pin_drift,review_checklist_blob_pin_drift,gate_evidence_self_test_case_count_drift,gate_evidence_self_test_cases_drift,shared_validator_reruns_gate_evidence_check_drift,shared_validator_reruns_gate_evidence_self_test_drift,shared_validator_expected_target_count_drift,shared_validator_expected_self_test_case_count_drift,runtime_atomic64_survey_packet_presence_drift,bitmap_diff_survey_replay_marker_drift,kprobe_gap_packet_presence_drift,kprobe_owner_drift,kprobe_validation_entrypoint_drift,kprobe_next_step_drift,perf_baseline_packet_presence_drift,perf_baseline_note_split_marker_drift,perf_baseline_owner_drift,perf_baseline_shared_promotion_status_drift,test_fsmount_gap_packet_presence_drift,test_fsmount_threshold_posture_drift,test_fsmount_owner_drift,test_fsmount_validation_entrypoint_drift,test_fsmount_linux_style_wrapper_drift,test_fsmount_next_step_drift,missing_validator_file,missing_phase4_build_file,missing_artifact_diff_helper_file,missing_atomic64_manifest_file,missing_bitmap_survey_file,missing_perf_survey_file,missing_kprobe_manifest_file,missing_test_fsmount_survey_file,missing_doc_readme_file,missing_script_readme_file,missing_atomic64_diff_file,missing_note_file`
  * `PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true`
  * `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true`
  * `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true`
  * `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=15`
  * `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=46`
  * `PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`
  * `PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true`
  * `PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=true`
  * `PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true`

## Exact Readback Evidence
  * Public current-`master` fallback rereads of `Documentation/zigux/artifact-diff.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, and the dedicated `scripts/zigux/check-phase4-workflow-route-counts.py` checker keep the broader Phase 4 rollback-readiness packet reviewable even while authenticated contents reads can still flap for some of those companions, including the dedicated local-only `scripts/zigux/check-phase4-perf-baseline-packet.py` checker, the local-only perf-baseline survey files, and the matching direct `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` and Linux-style `make -C zigux phase4-perf-baseline-survey` replay routes.
  * shared CI perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved.
  * `scripts/zigux/check-phase4-gate-evidence.py` stays explicit as the broader packet checker, but this note intentionally does not exact-pin that checker's own blob because any checker edit would invalidate a self-recorded blob immediately.
  * Use `Documentation/zigux/phase4-reversible-delivery-evidence.md` as the narrower direct-readback handoff while `scripts/zigux/check-phase4-gate-evidence.py` continues to guard this broader rollback-ownership note and `scripts/zigux/check-phase4-perf-baseline-packet.py` keeps the adjacent local-only perf packet exact.
  * The current bootstrap workflow still routes Phase 4 through `make -C zigux phase4-validate` and `make -C zigux phase4-test` before the direct artifact-diff helper and checker reruns. Current exact readback also shows direct Phase 4 workflow steps for `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-tests-readme-packet.py`, `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-phase4-artifact-diff-determinism.py`, and `scripts/zigux/check-phase4-artifact-diff-validator-replays.py`, which remain part of the current lab-and-CI gate surface this broader evidence packet has to stay compatible with.
  * Keep `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` explicit as public-raw returned current-`master` companions while exact authenticated blob-pin refresh remains pending for that broader branch of the packet.
  * The current bounded bitmap rollback gate in `zigux/tests/bitmap_diff.zig` and the shipped helper replay in `zigux/tests/phase4_bitmap_live_helper_replay.zig` remain reviewable through the direct `zig build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig` and Linux-style `make -C zigux phase4-bitmap-live-helper-replay` replays. This note now keeps the exact bitmap rollback inventory explicit: thirteen bounded range and prefix cases, two `find_nth_bit` replays, sixteen copy-tail cases, explicit zero-length range/prefix and zero-length copy no-op coverage, explicit partial-word 109-bit replay that keeps copied source tail bits through bit 126, matching pre-filled 109-bit replay that clears the padded tail before the filled tail resumes, aligned 97-bit copy replay that keeps the second copied word intact before the cleared tail resumes, bounded out-of-bounds rejection coverage, explicit rollback-governance and manifest-backed rollback-packet alignment coverage, empty-batch rejection for `runThresholdReplay(0)`, deterministic threshold replays for `runThresholdReplay(1)` and `runThresholdReplay(4)` with checksums `5216946504564592253` and `7942141539243507472`, final markers `final_first_zero=109`, `final_weight=1005`, and `final_nth_seven=123`, a current source-inventory tally of `13 DiffCase`, `16 CopyCase`, and `13 mixThresholdChecksum()` checkpoints, and the exact helper-facing fill and zero anchors `bitmap_fill(..., 35)`, `bitmap_fill(..., 115)`, `bitmap_zero(..., 35)`, and `bitmap_zero(..., 115)` with the rounded 64 and 128 visible beside them in `lib/test_bitmap.c`.
  * That narrower handoff still keeps the parked kprobe packet's shared matrix anchor explicit as `PHASE4_KPROBE_SHARED_LAB_AND_CI_MATRIX_ANCHOR=Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix`, so the broader rollback-ownership note now carries forward the same matrix-anchor discipline beside the current `make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m` Linux replay, the dedicated `make -C zigux phase4-kprobe-example-survey` local replay, and the existing `Validation and Perf Team` ownership pair while `samples/zigux/kprobe_example.zig` remains intentionally absent.