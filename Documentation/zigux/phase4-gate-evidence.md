# Phase 4 Gate Evidence
This note records the current connector-readback checkpoint for the shipped Phase 4 rollback-ownership and lab-matrix packet. Newer validator-local status lines still need a later full schema refresh when this lane intentionally widens.

## Status
- `PHASE4_EVIDENCE_DATE=2026-05-11`
- `PHASE4_EVIDENCE_MODE=github_connector_readback`
- `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`
- `PHASE4_EXACT_READBACK_REF=master`
- `PHASE4_VALIDATION_MATRIX_BLOB_SHA=ee28bc6be404bd09343d21a6517f9e1bafc197e2`
- `PHASE4_VALIDATOR_BLOB_SHA=abe089ee72dbb13fa5d7de9c2b4ac8915b9a9658`
- `PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=ba90537233d10e11bf65dc4f369aca4d866bcb4e`
- `PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=13f09796351802416e830d0bb75f8970985e0954`
- `PHASE4_ARTIFACT_DIFF_DOC_BLOB_SHA=fabeb85868d4e5f82e82999199cb3b746b15009e`
- `PHASE4_ARTIFACT_DIFF_CONTRACT_CHECKER_BLOB_SHA=5272b8c9573fdabb733b66ce655842d9fdfa0cc5`
- `PHASE4_BUILD_BLOB_SHA=86f88d03cd82e2e11ea6ed4a02175b77b472fdb4`
- `PHASE4_MAKEFILE_BLOB_SHA=2f46eb0f74567c0d709a399ee9a33b1717e50e6d`
- `PHASE4_WORKFLOW_BLOB_SHA=82d867a110189a726681f082a21d8d13e2a44901`
- `PHASE4_DOC_README_BLOB_SHA=e62de0139b11e9710d5a08edf6f9f9be1f1a0fea`
- `PHASE4_SCRIPT_README_BLOB_SHA=a89676c6512f127d015bf2f901689ffb6314d808`
- `PHASE4_TESTS_README_BLOB_SHA=d59190614f950d896b768c0fb762096467a6b637`
- `PHASE4_ATOMIC64_DIFF_BLOB_SHA=2e2b586a41ad473cd96e7fd5528a35ebcbf8feae`
- `PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA=8965f1c3cbeaa4411cc5a82b8d1ea15aaf5a03a3`
- `PHASE4_BITMAP_DIFF_BLOB_SHA=dd1e2da578cd1a55c4ac28692aed8d8afa7aa671`
- `PHASE4_BITMAP_LIVE_HELPER_REPLAY_BLOB_SHA=24418ad890696a59b95276fe8dec7eaeecf25172`
- `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=72eb288ec46ab0037391ee705233e3d38b8b942d`
- `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=d845a19f877ead27a68607404ee5c3d62852d1bb`
- `PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA=f7ebe6a5b4d4421416936b9f5d76798f2cd13eed`
- `PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=16`
- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=21`
- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=baseline_round_trip,shipped_target_count_drift,missing_exact_readback_heading,validator_blob_pin_drift,phase4_build_manifest_blob_pin_drift,phase4_build_survey_blob_pin_drift,phase9_build_manifest_blob_pin_drift,phase9_build_survey_blob_pin_drift,gate_evidence_self_test_case_count_drift,gate_evidence_self_test_cases_drift,shared_validator_reruns_gate_evidence_self_test_drift,shared_validator_expected_target_count_drift,shared_validator_expected_self_test_case_count_drift,bitmap_diff_survey_replay_marker_drift,kprobe_gap_packet_presence_drift,perf_baseline_packet_presence_drift,perf_baseline_note_split_marker_drift,perf_baseline_owner_drift,perf_baseline_shared_promotion_status_drift,test_fsmount_gap_packet_presence_drift,missing_note_file`
- `PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true`
- `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true`
- `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true`
- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=16`
- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=21`
- `PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`
- `PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true`
- `PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=true`
- `PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true`

## Exact Readback Evidence
- `Documentation/zigux/artifact-diff.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, and the newer dedicated `scripts/zigux/check-phase4-workflow-route-counts.py` checker now agree on the currently shipped Phase 4 rollback-readiness packet surfaces that the validator and shared build still own on `master`.
- `scripts/zigux/check-phase4-gate-evidence.py` remains the dedicated exact-readback checker for this narrower rollback-ownership packet.
- `zigux/tests/phase4_runtime_atomic64_diff_manifest.json` and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` remain the manifest-backed runtime atomic64 survey pair, and `phase4-runtime-atomic64-diff-survey-tests` plus `phase4-bitmap-live-helper-replay-tests` stay wired through the shared Phase 4 build entrypoint.
- The current bounded atomic64 rollback gate now has an exact check inventory in this note: two arithmetic checks (`v0 arithmetic path mirrors add/sub/add_return/sub_return/inc_return/dec_return sequencing` and `negative-one arithmetic path keeps decrement-style updates visible`), three exchange checks (`v0 to v1 keeps the original counter visible as the exchange return value`, `v1 to v2 keeps wide negative and positive 64-bit values distinct`, and `high-bit starter from atomic64_test.c still round-trips through exchange`), two `cmpxchg` checks (success and mismatch), two `add_unless` checks (blocked and changed), three bitwise checks (`and`, `or`, and `xor`), the selftest-family ordering replay, empty-batch rejection for `runThresholdReplay(0)`, and deterministic threshold replays for `runThresholdReplay(1)` and `runThresholdReplay(4)` with final counters `130322557735600377` and `130322557735600376` plus checksums `3626254113632800175` and `9210681150676220922`.
- That published twenty-one-case self-test catalog now also exercises the runtime atomic64 packet's `validate-phase4.py`, `phase4-validation-matrix.md`, and `Documentation/zigux/review-checklist.md` manifest and survey blob drift paths inside the existing manifest-backed drift coverage, and it now checks the shipped perf-baseline packet's manifest-presence drift path, the local-only perf-baseline note split-marker drift path, the shipped perf-baseline owner drift path, the shared-promotion status drift path, and the adjacent `test_fsmount` gap packet's manifest-presence drift path too, so those validator, matrix, reviewer-checklist, perf-baseline packet, local-only split marker, perf-baseline ownership, shared-promotion posture, and parked `test_fsmount` packet expectations are no longer an unstated self-test gap.
- The current exact-readback set now truthfully pins the shared rollback-ownership and lab-matrix packet again, and the adjacent manifest-backed runtime atomic64 survey pair now agrees with the current validator, review-checklist, and matrix blob pins instead of trailing the shared packet.
- The current helper-backed bitmap rollback lab replay routes remain `zig build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig` and `make -C zigux phase4-bitmap-live-helper-replay`, and the helper-backed row still records `Shared Subsystems Pod` as both owner and rollback owner for `zigux/tests/phase4_bitmap_live_helper_replay.zig`.
- The current bounded bitmap rollback gate now also has an exact check inventory in this note: thirteen bounded range and prefix cases, two `find_nth_bit` replays, twelve copy-tail cases, explicit zero-length range/prefix and zero-length copy no-op coverage, the aligned 97-bit copy replay that keeps the second copied word intact before the cleared tail resumes, bounded out-of-bounds rejection coverage, explicit rollback-governance and manifest-backed rollback-packet alignment coverage, empty-batch rejection for `runThresholdReplay(0)`, deterministic threshold replays for `runThresholdReplay(1)` and `runThresholdReplay(4)` with checksums `5216946504564592253` and `7942141539243507472`, final markers `final_first_zero=109`, `final_weight=1005`, and `final_nth_seven=123`, and a current source-inventory tally of `13 DiffCase`, `12 CopyCase`, and `13 mixThresholdChecksum()` checkpoints.
- The helper-backed bitmap rollback row still keeps `threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks` explicit until a later bounded Phase 4 perf packet intentionally approves a harder threshold.
- `zigux/tests/phase4_perf_baseline_manifest.json` and `zigux/tests/phase4_perf_baseline_survey.zig` also remain shipped on `master` as the dedicated local-only perf-baseline posture packet, and `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` stays the bounded replay route outside the shared validator-backed exact-readback target set while the approved local-only command-and-limit evidence for both rollback gates remains intentionally separate from shared CI perf approval.
- `zigux/Makefile` still exposes `make -C zigux phase4-validate`, `make -C zigux phase4-test`, `make -C zigux phase4-runtime-atomic64-diff`, `make -C zigux phase4-runtime-atomic64-diff-survey`, `make -C zigux phase4-perf-baseline-survey`, `make -C zigux phase4-bitmap-diff`, `make -C zigux phase4-bitmap-live-helper-replay`, `make -C zigux phase4-test-fsmount-survey`, `make -C zigux phase4-kprobe-example-survey`, and `make -C zigux phase4`, so the Linux-style local replay surface matches the current shared Phase 4 packet plus the adjacent local-only perf-baseline, kprobe, and test_fsmount survey wrappers instead of hiding those routes in the build file alone.
- The broader shared build and Makefile surface also still carries `make -C zigux phase4-bitmap-diff-survey` plus `zig build phase4-bitmap-diff-survey --build-file zigux/tests/phase4_build.zig`, so the bitmap survey packet remains reviewable beside the helper-backed replay without widening the lane into perf-threshold approval.
- The parked kprobe gap packet at `Documentation/zigux/phase4-kprobe-example-gap-survey.md`, `zigux/tests/phase4_kprobe_example_manifest.json`, and `zigux/tests/phase4_kprobe_example_survey.zig` now stays explicit in this shared gate-evidence note as adjacent parked evidence only, its Linux replay remains `make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m`, and the shared gate-evidence note now keeps that adjacent parked packet explicit without claiming a shipped Zig starter while `samples/zigux/kprobe_example.zig` remains absent on current `master`.
- The dedicated parked `test_fsmount` gap packet at `Documentation/zigux/phase4-test-fsmount-gap-survey.md`, `zigux/tests/phase4_test_fsmount_manifest.json`, and `zigux/tests/phase4_test_fsmount_survey.zig` now also stays under the dedicated exact-readback checker, its Linux replay remains `make M=samples/vfs`, and the shared validator route now picks that same parked packet up through `scripts/zigux/check-phase4-gate-evidence.py` while `samples/zigux/test_fsmount.zig` remains absent on current `master`.
- The shipped local perf-baseline survey packet is intentionally separate from that shared exact-readback set: it exact-pins the approved local-only command-and-limit evidence for both rollback gates while keeping shared CI perf coverage out of scope.

## Current Conclusion
- shared CI perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved.
- that shared-CI-only unapproved posture now lives beside a different local-only truth: the dedicated perf-baseline survey packet already approves the local benchmark commands and local acceptable limits for both rollback gates while still keeping shared CI perf coverage out of scope.
- the dedicated local perf-baseline survey packet is still the truthful way to keep that split posture measurable: it exact-pins the approved local-only command-and-limit evidence for both rollback gates while keeping shared CI perf coverage out of scope.
- `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `Documentation/zigux/phase4-validation-matrix.md` now all mirror that local-only split and the current decision-owner packet: the Validation and Perf Team stays named as the decision owner for any broader shared-CI perf promotion, while the ABI and Runtime Team plus Shared Subsystems Pod stay named as coordination owners for that policy call.
- the currently shipped docs-root, scripts-root, tests-root, Makefile, validator, gate-evidence checker, and workflow-route checker surfaces now agree on the freshly re-read blob pins recorded in this checkpoint, even though the broader gate-evidence status schema still needs a later dedicated refresh.
