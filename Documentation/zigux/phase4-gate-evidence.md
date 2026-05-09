# Phase 4 Gate Evidence
This note records one exact readback snapshot for the current Phase 4 rollback-ownership and lab-matrix gate definitions.

## Status
- `PHASE4_EVIDENCE_DATE=2026-05-09`
- `PHASE4_EVIDENCE_MODE=github_connector_readback`
- `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`
- `PHASE4_EXACT_READBACK_REF=master`
- `PHASE4_VALIDATION_MATRIX_BLOB_SHA=b1ccff581dd305b6137e80bbd33d8fce1d2b1316`
- `PHASE4_VALIDATOR_BLOB_SHA=b03d10e18821c2a239c39906f81943e73f7fb306`
- `PHASE4_ARTIFACT_DIFF_DOC_BLOB_SHA=41eb858a9d224cddc57286df418467f6b3d9beee`
- `PHASE4_ARTIFACT_DIFF_CONTRACT_CHECKER_BLOB_SHA=b18cde58722cbb8bc7028575dcabd00f20eb9ba7`
- `PHASE4_BUILD_BLOB_SHA=86f88d03cd82e2e11ea6ed4a02175b77b472fdb4`
- `PHASE4_MAKEFILE_BLOB_SHA=cfb5a1ebd283c5f86ccc264ceccaf704fd8c47b5`
- `PHASE4_WORKFLOW_BLOB_SHA=522ce12ba8cfb436e05e17f8e4d57bcdbd92ae3a`
- `PHASE4_DOC_README_BLOB_SHA=683cad280aa69287b7ffba02df25cef1ed711000`
- `PHASE4_SCRIPT_README_BLOB_SHA=9c2c3bace094098258bfe8ef6cc5f654df8ffe25`
- `PHASE4_TESTS_README_BLOB_SHA=c19b08ca153be3b696db1abbb0a026a82d0db2d5`
- `PHASE4_ATOMIC64_DIFF_BLOB_SHA=6f50e3adac88dbeac02353cfb9b698ee02c6d2da`
- `PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA=8965f1c3cbeaa4411cc5a82b8d1ea15aaf5a03a3`
- `PHASE4_BITMAP_DIFF_BLOB_SHA=0cfd20c304476d560bd125abb496a4656f22ba9f`
- `PHASE4_BITMAP_LIVE_HELPER_REPLAY_BLOB_SHA=24418ad890696a59b95276fe8dec7eaeecf25172`
- `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=e283ee121626569a375e60c3834d6c9a76978153`
- `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=51e2cfef51c5f57ce68cb543c889e89d56173d05`
- `PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA=25534f350062ffe0fb7171f83be52841e83b89e2`
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
- `PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=false`
- `PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true`

## Exact Readback Evidence
- `Documentation/zigux/artifact-diff.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` now all point at the same currently shipped Phase 4 rollback-readiness packet surfaces that the validator and shared build still own on `master`.
- `scripts/zigux/check-phase4-gate-evidence.py` remains the dedicated exact-readback checker for this narrower rollback-ownership packet.
- `zigux/tests/phase4_runtime_atomic64_diff_manifest.json` and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` remain the manifest-backed runtime atomic64 survey pair, and `phase4-runtime-atomic64-diff-survey-tests` plus `phase4-bitmap-live-helper-replay-tests` stay wired through the shared Phase 4 build entrypoint.
- The current bounded atomic64 rollback gate now has an exact check inventory in this note: two arithmetic checks (`v0 arithmetic path mirrors add/sub/add_return/sub_return/inc_return/dec_return sequencing` and `negative-one arithmetic path keeps decrement-style updates visible`), three exchange checks (`v0 to v1 keeps the original counter visible as the exchange return value`, `v1 to v2 keeps wide negative and positive 64-bit values distinct`, and `high-bit starter from atomic64_test.c still round-trips through exchange`), two `cmpxchg` checks (success and mismatch), two `add_unless` checks (blocked and changed), three bitwise checks (`and`, `or`, and `xor`), the selftest-family ordering replay, empty-batch rejection for `runThresholdReplay(0)`, and deterministic threshold replays for `runThresholdReplay(1)` and `runThresholdReplay(4)` with final counters `130322557735600377` and `130322557735600376` plus checksums `3626254113632800175` and `9210681150676220922`.
- That published twenty-one-case self-test catalog now also exercises the runtime atomic64 packet's `validate-phase4.py`, `phase4-validation-matrix.md`, and `Documentation/zigux/review-checklist.md` manifest and survey blob drift paths inside the existing manifest-backed drift coverage, and it now checks the shipped perf-baseline packet's manifest-presence drift path, the local-only perf-baseline note split-marker drift path, the shipped perf-baseline owner drift path, the shared-promotion status drift path, and the adjacent `test_fsmount` gap packet's manifest-presence drift path too, so those validator, matrix, reviewer-checklist, perf-baseline packet, local-only split marker, perf-baseline ownership, shared-promotion posture, and parked `test_fsmount` packet expectations are no longer an unstated self-test gap.
- The exact-readback set is current again for the shared rollback-ownership and lab-matrix packet, and the manifest-backed runtime atomic64 survey pair now pins the same current `phase4_build.zig`, `validate-phase4.py`, `phase4-validation-matrix.md`, `Documentation/zigux/review-checklist.md`, and `phase9_build.zig` blobs that the shared validator and review packet now depend on.
- The current helper-backed bitmap rollback lab replay route remains `zig build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig`, and the helper-backed row still records `Shared Subsystems Pod` as both owner and rollback owner for `zigux/tests/phase4_bitmap_live_helper_replay.zig`.
- The current bounded bitmap rollback gate now also has an exact check inventory in this note: thirteen bounded range and prefix cases, two `find_nth_bit` replays, eleven copy-tail cases, explicit zero-length range/prefix and zero-length copy no-op coverage, the aligned 97-bit copy replay that keeps the second copied word intact before the cleared tail resumes, bounded out-of-bounds rejection coverage, empty-batch rejection for `runThresholdReplay(0)`, deterministic threshold replays for `runThresholdReplay(1)` and `runThresholdReplay(4)` with checksums `5216946504564592253` and `7942141539243507472`, final markers `final_first_zero=109`, `final_weight=1005`, and `final_nth_seven=123`, and a current source-inventory tally of `13 DiffCase`, `11 CopyCase`, and `13 mixThresholdChecksum()` checkpoints.
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
- `Documentation/zigux/review-checklist.md` already mirrors that local-only split and the current decision-owner packet, but `scripts/zigux/README.md` still leaves the broader shared-CI perf-promotion owner map implicit, so the next same-lane follow-through is to align that scripts-root reminder with `Documentation/zigux/phase4-validation-matrix.md` before any broader policy change.
- The current exact-readback note is aligned again to the live validator, workflow, Makefile, and the full docs-root, scripts-root, and tests-root Phase 4 packet on `master`; `zigux/tests/README.md` now explicitly carries the shipped local-only perf-baseline pair `zigux/tests/phase4_perf_baseline_manifest.json` plus `zigux/tests/phase4_perf_baseline_survey.zig`, the adjacent parked kprobe gap survey, and the parked `test_fsmount` gap packet, so the compact tests-root reminder now matches the existing exact-readback note and dedicated local survey wrappers.
