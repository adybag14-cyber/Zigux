# Phase 4 Gate Evidence
This note records one exact readback snapshot for the current Phase 4 rollback-ownership and lab-matrix gate definitions.

## Status
- `PHASE4_EVIDENCE_DATE=2026-05-05`
- `PHASE4_EVIDENCE_MODE=github_connector_readback`
- `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`
- `PHASE4_EXACT_READBACK_REF=master`
- `PHASE4_VALIDATION_MATRIX_BLOB_SHA=9f01421b7ca24c16808195ceef449d9bd5d06970`
- `PHASE4_VALIDATOR_BLOB_SHA=5f95efd379b1b19bb7671f74dc0f7d0a233d12e6`
- `PHASE4_ARTIFACT_DIFF_DOC_BLOB_SHA=2b305d82e9ffb7de80599c769d73c6b38e915c6d`
- `PHASE4_ARTIFACT_DIFF_CONTRACT_CHECKER_BLOB_SHA=31cf8c2b2c8da86e823fbc8c8a39fe61c530312f`
- `PHASE4_BUILD_BLOB_SHA=33d3ed8db4e40283212daa115a46e989df28ce6f`
- `PHASE4_MAKEFILE_BLOB_SHA=2d3286ee118c1d2ff19c26d2da8965f5963acea2`
- `PHASE4_WORKFLOW_BLOB_SHA=c9f09d6da8fdb29f4796a08d01c74919cef67572`
- `PHASE4_DOC_README_BLOB_SHA=f0451a810905c156e048f164d89b9dcfc03d68e7`
- `PHASE4_SCRIPT_README_BLOB_SHA=9317dc84d5d4641859966afa1c4641e3508f8cb6`
- `PHASE4_TESTS_README_BLOB_SHA=04998dbbc35effd76e4215e1ae073c07ecbcc386`
- `PHASE4_ATOMIC64_DIFF_BLOB_SHA=0b1b0b161d0a50608b26fdd59b87a1de4c31d4aa`
- `PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA=6dd5b8e0a84fe2f775011d552b629b20da222166`
- `PHASE4_BITMAP_DIFF_BLOB_SHA=9d35b967233469b4a13975a67191483e89c75288`
- `PHASE4_BITMAP_LIVE_HELPER_REPLAY_BLOB_SHA=75d26e94d322da8b9c14e5a9e53cded8576432d3`
- `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=99f3f87e98b56d758e19251e816b9d63441a8b64`
- `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=1ee8f68afa534d3ef628d388999e6020a0348739`
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
- `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` now all name the same shipped Phase 4 rollback-readiness packet surfaces that the current validator and shared build route still own on `master`, while `Documentation/zigux/artifact-diff.md` keeps the bounded host-side helper contract and wrapper-backed Phase 4 gate list explicit without overclaiming the full shared packet.
- `scripts/zigux/check-phase4-gate-evidence.py` is present, and `Documentation/zigux/phase4-validation-matrix.md` now names it as the dedicated Phase 4 rollback-ownership gate while this note exact-pins the same current narrower packet: the validator, artifact-diff contract surfaces, the shared build entrypoint, the three root README summaries, and the manifest-backed runtime atomic64 survey pair.
- `scripts/zigux/check-phase4-gate-evidence.py --self-test` currently covers fourteen dedicated drift paths, and the shared `scripts/zigux/validate-phase4.py` route still reruns both the live checker and that self-test before Phase 4 Zig replays continue, expecting the same `PHASE4_GATE_EVIDENCE_TARGET_COUNT=16` packet recorded above.
- `zigux/tests/phase4_runtime_atomic64_diff_manifest.json` and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` remain the manifest-backed runtime atomic64 handoff pair, and the shared build still exposes `phase4-runtime-atomic64-diff-survey-tests` and `phase4-bitmap-live-helper-replay-tests` beside the synthetic rollback gates.
- The exact-readback set is now current for the shipped validator-backed packet, and the manifest-backed runtime atomic64 survey pair now pins the same current `phase4_build.zig`, `validate-phase4.py`, `phase4-validation-matrix.md`, and `phase9_build.zig` blobs that this note names.
- Current `master` still treats the roadmap-backed sample follow-ups as open gaps rather than shipped gate-evidence targets: `samples/zigux/kprobe_example.zig` remains absent and `samples/zigux/test_fsmount.zig` remains absent.

## Current Conclusion
- The live Phase 4 exact-readback packet is limited to the files that `master` actually ships for rollback ownership, matrix wording, validator wiring, the artifact-diff contract, the gate-evidence note, the shared build route, the helper-backed bitmap replay, and the runtime atomic64 wrapper handoff plus its manifest-backed survey evidence.
- The dedicated gate-evidence note, its explicit rollback-owner row in `Documentation/zigux/phase4-validation-matrix.md`, and the separate runtime atomic64 manifest-backed survey packet are back in sync with the same current validator-backed blob-pin set.
- The published rollback-readiness note now also surfaces the dedicated checker self-test catalog and the shared validator's exact gate-evidence expectations instead of leaving that narrower coverage implied by the Python sources alone.
- hard perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved.
