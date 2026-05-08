# Phase 4 Gate Evidence
This note records one exact readback snapshot for the current Phase 4 rollback-ownership and lab-matrix gate definitions.

## Status
- `PHASE4_EVIDENCE_DATE=2026-05-08`
- `PHASE4_EVIDENCE_MODE=github_connector_readback`
- `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`
- `PHASE4_EXACT_READBACK_REF=master`
- `PHASE4_VALIDATION_MATRIX_BLOB_SHA=55dfa2ef288e8052ce4505bc39209595c0fc0c4f`
- `PHASE4_VALIDATOR_BLOB_SHA=d3f208106ad4ca905cf2eae3c1c55937cd8a7779`
- `PHASE4_ARTIFACT_DIFF_DOC_BLOB_SHA=20597dee59e9c14799776788a4b5899772240c75`
- `PHASE4_ARTIFACT_DIFF_CONTRACT_CHECKER_BLOB_SHA=b18cde58722cbb8bc7028575dcabd00f20eb9ba7`
- `PHASE4_BUILD_BLOB_SHA=9944a72ef3d53ff098dd44ea9c8a905d7f212db3`
- `PHASE4_MAKEFILE_BLOB_SHA=6be2efca61f56bb3dc09cbff7e3186f9f26663fb`
- `PHASE4_WORKFLOW_BLOB_SHA=7f3edd26f04f9e37a52bd802476b6a74fc072dc5`
- `PHASE4_DOC_README_BLOB_SHA=500ec915ca5fb8ad0ef44427f3cd955cbcd85c1d`
- `PHASE4_SCRIPT_README_BLOB_SHA=9bf5564a3056b606b6dcbcb519df35c94fb142b6`
- `PHASE4_TESTS_README_BLOB_SHA=57f439983be71241a22d76c351352de250a2fe05`
- `PHASE4_ATOMIC64_DIFF_BLOB_SHA=c805a2d198ad6b632e6eddb9738a37e0d98f23ea`
- `PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA=8965f1c3cbeaa4411cc5a82b8d1ea15aaf5a03a3`
- `PHASE4_BITMAP_DIFF_BLOB_SHA=b52320323e1e6718245621253d11293d5cae03da`
- `PHASE4_BITMAP_LIVE_HELPER_REPLAY_BLOB_SHA=24418ad890696a59b95276fe8dec7eaeecf25172`
- `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=720ab5892345d2bbc0d06d015c52c03b50f0fb35`
- `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=5ad60a86ccb6e9e9a6a59e52b2ef3d7c567aa256`
- `PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA=a7803e891f84333f4791a2dd0d0733b8bb46c4a9`
- `PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=16`
- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=18`
- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=baseline_round_trip,shipped_target_count_drift,missing_exact_readback_heading,validator_blob_pin_drift,phase4_build_manifest_blob_pin_drift,phase4_build_survey_blob_pin_drift,phase9_build_manifest_blob_pin_drift,phase9_build_survey_blob_pin_drift,gate_evidence_self_test_case_count_drift,gate_evidence_self_test_cases_drift,shared_validator_reruns_gate_evidence_self_test_drift,shared_validator_expected_target_count_drift,shared_validator_expected_self_test_case_count_drift,bitmap_diff_survey_replay_marker_drift,kprobe_gap_packet_presence_drift,perf_baseline_packet_presence_drift,test_fsmount_gap_packet_presence_drift,missing_note_file`
- `PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true`
- `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true`
- `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true`
- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=16`
- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=18`
- `PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`
- `PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true`
- `PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=false`
- `PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true`

## Exact Readback Evidence
- `Documentation/zigux/artifact-diff.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` now all point at the same currently shipped Phase 4 rollback-readiness packet surfaces that the validator and shared build still own on `master`.
- `scripts/zigux/check-phase4-gate-evidence.py` remains the dedicated exact-readback checker for this narrower rollback-ownership packet.
- `scripts/zigux/check-artifact-diff-contract.py` currently reruns the shipped 28-case artifact-diff contract packet exactly as read back on `master`: `helper_self_test`, `helper_self_test_repeat`, `cli_help_output`, `cli_help_output_repeat`, `cli_missing_required_args`, `cli_missing_actual_operand`, `cli_invalid_mode`, `text_pass`, `text_pass_repeat`, `text_mismatch`, `text_missing_expected`, `text_missing_actual`, `text_missing_both`, `json_pass`, `json_mismatch`, `json_mismatch_repeat`, `json_missing_expected`, `json_missing_actual`, `json_missing_both`, `json_invalid_expected`, `json_invalid_actual`, `json_invalid_both`, `sha256_pass`, `sha256_missing_expected`, `sha256_missing_actual`, `sha256_missing_both`, `sha256_drift`, and `sha256_drift_repeat`.
- Its paired 18-case checker self-test still exact-pins `catalog_shape`, `review_note_marker_round_trip`, `review_note_marker_drift`, `helper_summary_round_trip`, `contract_summary_round_trip`, `helper_summary_status_drift`, `helper_summary_count_drift`, `helper_summary_duplicate_case_drift`, `helper_summary_case_order_drift`, `contract_summary_status_drift`, `contract_summary_base_count_drift`, `contract_summary_base_case_order_drift`, `contract_summary_repeat_count_drift`, `contract_summary_repeat_case_order_drift`, `contract_summary_case_count_drift`, `contract_summary_duplicate_case_drift`, `contract_summary_case_order_drift`, and the adjacent `test_fsmount` gap-packet presence drift, so the published case counts and ordering remain part of the bounded Phase 4 artifact-diff packet.
- `make -C zigux phase4-validate` now also reruns `scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test` and the live determinism checker so the shipped helper self-test catalog and the published contract catalog stay machine-checked in the Linux-style Phase 4 route alongside the existing validator and contract replay.
- `zigux/tests/phase4_runtime_atomic64_diff_manifest.json` and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` remain the manifest-backed runtime atomic64 survey pair, and `phase4-runtime-atomic64-diff-survey-tests` plus `phase4-bitmap-live-helper-replay-tests` stay wired through the shared Phase 4 build entrypoint.
- That published eighteen-case self-test catalog now also exercises the runtime atomic64 packet's `validate-phase4.py`, `phase4-validation-matrix.md`, and `Documentation/zigux/review-checklist.md` manifest and survey blob drift paths inside the existing manifest-backed drift coverage, and it now checks the shipped perf-baseline packet's manifest-presence drift path plus the adjacent `test_fsmount` gap packet's manifest-presence drift path too, so those validator, matrix, reviewer-checklist, perf-baseline packet, and parked `test_fsmount` packet expectations are no longer an unstated self-test gap.
- The exact-readback set is current again for the shared rollback-ownership and lab-matrix packet, and the manifest-backed runtime atomic64 survey pair now pins the same current `phase4_build.zig`, `validate-phase4.py`, `phase4-validation-matrix.md`, `Documentation/zigux/review-checklist.md`, and `phase9_build.zig` blobs that the shared validator and review packet now depend on.
- The current helper-backed bitmap rollback lab replay route remains `zig build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig`, and the helper-backed row still records `Shared Subsystems Pod` as both owner and rollback owner for `zigux/tests/phase4_bitmap_live_helper_replay.zig`.
- The helper-backed bitmap rollback row still keeps `threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks` explicit until a later bounded Phase 4 perf packet intentionally approves a harder threshold.
- `zigux/tests/phase4_perf_baseline_manifest.json` and `zigux/tests/phase4_perf_baseline_survey.zig` also remain shipped on `master` as the dedicated local-only perf-baseline posture packet, and `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` stays the bounded replay route outside the shared validator-backed exact-readback target set until benchmark commands and acceptable limits are intentionally approved.
- The dedicated exact-readback checker now also rereads that shipped perf-baseline manifest-and-survey pair so the still-unapproved benchmark-command and acceptable-limit posture cannot drift out of the Phase 4 review packet unnoticed.
- `zigux/Makefile` still exposes `make -C zigux phase4-validate`, `make -C zigux phase4-test`, `make -C zigux phase4-runtime-atomic64-diff`, `make -C zigux phase4-runtime-atomic64-diff-survey`, `make -C zigux phase4-bitmap-diff`, `make -C zigux phase4-bitmap-live-helper-replay`, and `make -C zigux phase4`, so the Linux-style local replay surface matches the current shared Phase 4 packet instead of hiding those routes in the build file alone.
- The broader shared build and Makefile surface also still carries `make -C zigux phase4-bitmap-diff-survey` plus `zig build phase4-bitmap-diff-survey --build-file zigux/tests/phase4_build.zig`, so the bitmap survey packet remains reviewable beside the helper-backed replay without widening the lane into perf-threshold approval.
- `zigux/tests/bitmap_diff.zig` currently exact-pins thirteen bounded range and prefix cases, two `find_nth_bit` replays (the eight-bit starter population plus the full `exp1_find_nth_bits` enumeration), ten copy-tail cases, the empty threshold replay rejection, bounded out-of-bounds rejection coverage, the deterministic threshold batch checks (`single.checksum=5216946504564592253`, `repeated.checksum=7942141539243507472`, `final_first_zero=109`, `final_weight=1005`, and `final_nth_seven=123`), explicit rollback governance, and the source-inventory cardinality guard for the 13 `DiffCase`, 10 `CopyCase`, and 13 `mixThresholdChecksum()` checkpoints.
- The parked kprobe gap packet at `Documentation/zigux/phase4-kprobe-example-gap-survey.md`, `zigux/tests/phase4_kprobe_example_manifest.json`, and `zigux/tests/phase4_kprobe_example_survey.zig` now stays explicit in this shared gate-evidence note as adjacent parked evidence only, its Linux replay remains `make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m`, the dedicated local survey wrapper remains `make -C zigux phase4-kprobe-example-survey`, and the shared gate-evidence note now keeps that adjacent parked packet explicit without claiming a shipped Zig starter while `samples/zigux/kprobe_example.zig` remains absent on current `master`.
- The dedicated parked `test_fsmount` gap packet at `Documentation/zigux/phase4-test-fsmount-gap-survey.md`, `zigux/tests/phase4_test_fsmount_manifest.json`, and `zigux/tests/phase4_test_fsmount_survey.zig` now also stays under the dedicated exact-readback checker, its Linux replay remains `make M=samples/vfs`, and the shared validator route now picks that same parked packet up through `scripts/zigux/check-phase4-gate-evidence.py` while `samples/zigux/test_fsmount.zig` remains absent on current `master`.
- The shipped local perf-baseline survey packet is intentionally separate from that shared exact-readback set: it keeps the still-unapproved benchmark-command and acceptable-limit posture machine-checked locally without turning the Phase 4 validator or CI path into a perf-approval claim before one bounded threshold packet lands for each rollback gate.
- `samples/zigux/test_fsmount.zig` remains absent, and the adjacent survey packet now makes that missing-starter boundary reviewable while the shared validator route and dedicated exact-readback checker both reread the parked note, manifest, and survey packet without pretending that the shared exact-readback gate owns a shipped Zig starter.

## Current Conclusion
- hard perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved.
- the dedicated local perf-baseline survey packet is still the truthful way to keep that unapproved posture measurable until one bounded benchmark command and one acceptable limit are promoted for each shipped rollback gate.
- The current exact-readback note is aligned again to the live validator, README, workflow, Makefile, and Phase 4 gate surfaces on `master`, and `zigux/tests/README.md` now explicitly carries the shipped local-only perf-baseline pair `zigux/tests/phase4_perf_baseline_manifest.json` plus `zigux/tests/phase4_perf_baseline_survey.zig`, while the adjacent `test_fsmount` gap packet is now visible as parked evidence with its own note, manifest, and survey route and is reread by the dedicated exact-readback checker before the shared validator continues.
