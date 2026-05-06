# Phase 4 Gate Evidence
This note records one exact readback snapshot for the current Phase 4 rollback-ownership and lab-matrix gate definitions.

## Status
- `PHASE4_EVIDENCE_DATE=2026-05-06`
- `PHASE4_EVIDENCE_MODE=github_connector_readback`
- `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`
- `PHASE4_EXACT_READBACK_REF=master`
- `PHASE4_VALIDATION_MATRIX_BLOB_SHA=1977a58d097fd6b3e4afb14482089c44e0de6387`
- `PHASE4_VALIDATOR_BLOB_SHA=60dd5759e0c149f70802e4474b2e22513ceabcab`
- `PHASE4_ARTIFACT_DIFF_DOC_BLOB_SHA=fa92a7946d40df00a1f04217ce133f869980c5b6`
- `PHASE4_ARTIFACT_DIFF_CONTRACT_CHECKER_BLOB_SHA=4007f376d422f2d38ef3d14b6f2a9cb28281d722`
- `PHASE4_BUILD_BLOB_SHA=33d3ed8db4e40283212daa115a46e989df28ce6f`
- `PHASE4_MAKEFILE_BLOB_SHA=4ffa857f797afe54f889072f956112ab8a60d810`
- `PHASE4_WORKFLOW_BLOB_SHA=356339298945aeaed6a05f1bf37f054ed1a26501`
- `PHASE4_DOC_README_BLOB_SHA=c68b2889349498fcf08372aa074324e932c0d713`
- `PHASE4_SCRIPT_README_BLOB_SHA=8208411dd718b5d8b05d1f05576b0b0bf9a3cd57`
- `PHASE4_TESTS_README_BLOB_SHA=46bb6969b982f4dc81ef359b828138c83bf96f8f`
- `PHASE4_ATOMIC64_DIFF_BLOB_SHA=749e1045c6cb749d0d94d0b8dbe946d9b9057eb0`
- `PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA=49a10b2c4124a7c05ef77fad9c7fadf3b62480b2`
- `PHASE4_BITMAP_DIFF_BLOB_SHA=8c6f95f3ebacdfba3bf2a25ed3ed15df030bdfaa`
- `PHASE4_BITMAP_LIVE_HELPER_REPLAY_BLOB_SHA=75d26e94d322da8b9c14e5a9e53cded8576432d3`
- `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=dab85d23b72c9e156fd23a48062d884e1cd5fbcc`
- `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=8fb3992728958d73672ccc1f746c6cd614c721b3`
- `PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=16`
- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=14`
- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=baseline_round_trip,shipped_target_count_drift,missing_exact_readback_heading,validator_blob_pin_drift,phase4_build_manifest_blob_pin_drift,phase4_build_survey_blob_pin_drift,phase9_build_manifest_blob_pin_drift,phase9_build_survey_blob_pin_drift,gate_evidence_self_test_case_count_drift,gate_evidence_self_test_cases_drift,shared_validator_reruns_gate_evidence_self_test_drift,shared_validator_expected_target_count_drift,shared_validator_expected_self_test_case_count_drift,missing_note_file`
- `PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true`
- `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true`
- `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true`
- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=16`
- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=14`
- `PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`
- `PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=false`
- `PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=false`
- `PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=false`

## Exact Readback Evidence
- `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` now all name the same shipped Phase 4 rollback-readiness packet surfaces that the current validator and shared build route still own on `master`, while `Documentation/zigux/artifact-diff.md`, `scripts/zigux/artifact_diff.py`, and `scripts/zigux/check-artifact-diff-contract.py` keep the bounded host-side helper contract explicit without overclaiming the full shared packet.
- `Documentation/zigux/README.md` now names `scripts/zigux/check-phase4-gate-evidence.py` directly alongside `scripts/zigux/validate-phase4.py`, the runtime atomic64 survey pair, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig`, so the docs-root summary matches the shipped narrower Phase 4 packet instead of leaving the dedicated exact-readback gate implied.
- `scripts/zigux/check-phase4-gate-evidence.py` is present, and `Documentation/zigux/phase4-validation-matrix.md` now names it as the dedicated Phase 4 rollback-ownership gate while this note exact-pins the same current narrower packet: the validator, artifact-diff contract surfaces, the shared build entrypoint, the three root README summaries, and the manifest-backed runtime atomic64 survey pair.
- `scripts/zigux/check-phase4-gate-evidence.py --self-test` still publishes a fourteen-entry case catalog, and the shared `scripts/zigux/validate-phase4.py` route still expects that same printed catalog before the Phase 4 Zig replays continue.
- The live self-test body also directly exercises helper-backed bitmap replay command drift, helper-backed ownership-line drift, and helper-backed threshold-posture drift by mutating the dedicated helper replay command, the `Shared Subsystems Pod` ownership sentence, and the `threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks` wording inside this note, so those three anchors already fail closed even though they are still grouped under the existing printed catalog rather than broken out as separate published case names.
- That published fourteen-case self-test catalog now also exercises the runtime atomic64 packet's `validate-phase4.py` and `phase4-validation-matrix.md` manifest and survey blob drift paths inside the existing manifest-backed drift coverage, so those validator-and-matrix pins are no longer an unstated self-test gap.
- `zigux/tests/phase4_runtime_atomic64_diff_manifest.json` and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` remain the manifest-backed runtime atomic64 handoff pair, and the shared build still exposes `phase4-runtime-atomic64-diff-survey-tests` and `phase4-bitmap-live-helper-replay-tests` beside the synthetic rollback gates.
- The current helper-backed bitmap rollback lab replay route remains `zig build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig`, matching the live helper-backed row in `Documentation/zigux/phase4-validation-matrix.md`.
- The matching Linux-style wrapper remains `make -C zigux phase4-bitmap-live-helper-replay`, so the dedicated helper-backed replay row and the current `zigux/Makefile` replay surface stay aligned instead of leaving that local rollback route implied by the broader wrapper summary alone.
- That same live helper-backed row still records `Shared Subsystems Pod` as both owner and rollback owner for `zigux/tests/phase4_bitmap_live_helper_replay.zig`, and it still keeps `threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks` explicit until a later bounded Phase 4 perf packet intentionally approves a harder threshold.
- `Documentation/zigux/phase4-validation-matrix.md` still keeps the missing `samples/zigux/kprobe_example.zig` row on the current `samples/kprobes/kprobe_example.c` anchor, with `Validation and Perf Team` named as both survey owner and rollback owner, the live C-anchor replay held at `make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m`, and no hard timing threshold approved before a bounded Zig starter lands.
- The same matrix still keeps the missing `samples/zigux/test_fsmount.zig` row on the current `samples/vfs/test-fsmount.c` anchor, with `Validation and Perf Team` named as both survey owner and rollback owner, the live C-anchor replay held at `make M=samples/vfs`, and no hard timing threshold approved before a bounded Zig starter lands.
- The shipped-gate perf row is still equally explicit in that matrix: `zigux/tests/atomic64_diff.zig` and `zigux/tests/bitmap_diff.zig` remain correctness-only gates today, `runtime_atomic64_diff.zig` remains the single underlying atomic64 replay body, and the next bounded threshold step is still one benchmark command plus one acceptable limit per gate before Phase 4 claims perf coverage.
- `zigux/tests/bitmap_diff.zig` now exact-pins the rounded-prefix threshold replay batch itself: `runThresholdReplay()` still rejects empty batches, the deterministic single-iteration and repeated checksums are now `4641743358357118437` and `15640590978236698512`, and the repeated batch also pins `final_first_set=0`, `final_first_zero=109`, `final_weight=1005`, and `final_nth_seven=123` on the current rollback gate.
- `zigux/Makefile` still exposes `make -C zigux phase4-validate`, `make -C zigux phase4-test`, `make -C zigux phase4-runtime-atomic64-diff`, `make -C zigux phase4-runtime-atomic64-diff-survey`, `make -C zigux phase4-bitmap-diff`, `make -C zigux phase4-bitmap-live-helper-replay`, and `make -C zigux phase4`, so the Linux-style local replay surface matches the current shared Phase 4 packet instead of hiding those routes in the build file alone.
- The exact-readback set is now current for the shipped validator-backed packet, and `zigux/tests/atomic64_diff.zig` now exact-checks the current gate-evidence blob pins for the wrapper, runtime replay, manifest, and survey while `scripts/zigux/validate-phase4.py` now also exact-checks the manifest-backed runtime atomic64 packet's `Documentation/zigux/review-checklist.md` blob pin beside the existing `phase4_build.zig`, `validate-phase4.py`, `phase4-validation-matrix.md`, and `phase9_build.zig` exact-readbacks.
- `Documentation/zigux/review-checklist.md` still stays inside the broader shared `validate-phase4.py` packet, and the manifest-backed runtime atomic64 survey pair already carries its current review-checklist blob pin while the shared validator now fails closed if that manifest-backed review-checklist pin drifts, but this dedicated exact-readback note still does not list the checklist blob as a top-level status line, so the exact-readback note itself remains narrower than the full reviewer-facing Phase 4 surface.
- Current `master` still treats the roadmap-backed sample follow-ups as open gaps rather than shipped gate-evidence targets: `samples/zigux/kprobe_example.zig` remains absent and `samples/zigux/test_fsmount.zig` remains absent.
- The explicit `PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=false`, `PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=false`, and `PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=false` status lines therefore still mean this exact-readback packet stops at the current rollback-readiness note, matrix, helper-backed bitmap replay, runtime atomic64 survey pair, and shared validator route; it does not yet claim a shipped kprobe sample packet, test-fsmount sample packet, or approved perf-baseline packet on `master`.

## Current Conclusion
- The live Phase 4 exact-readback packet is limited to the files that `master` actually ships for rollback ownership, matrix wording, validator wiring, the artifact-diff contract, the gate-evidence note, the shared build route, the helper-backed bitmap replay, and the runtime atomic64 wrapper handoff plus its manifest-backed survey evidence.
- The dedicated gate-evidence note, its explicit rollback-owner row in `Documentation/zigux/phase4-validation-matrix.md`, and the separate runtime atomic64 manifest-backed survey packet are back in sync with the same current validator-backed blob-pin set.
- The published rollback-readiness note now also surfaces the dedicated checker self-test catalog, the shared validator's exact gate-evidence expectations, the helper-backed bitmap replay ownership line, the current checksum-pinned `bitmap_diff.zig` threshold replay batch, the live Linux-style Makefile replay routes, and the explicitly owned remaining roadmap-gap rows instead of leaving that narrower coverage implied by the Python sources alone.
- The docs-root Phase 4 summary is now aligned too: `Documentation/zigux/README.md` names `scripts/zigux/check-phase4-gate-evidence.py` directly beside the validator, the atomic64 survey pair, and the bitmap rollback surfaces, so this exact-readback packet no longer carries the older docs-only checker visibility gap.
- hard perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved.
