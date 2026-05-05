# Phase 4 Gate Evidence
This note records one exact readback snapshot for the current Phase 4 rollback-ownership and lab-matrix gate definitions.

## Status
- `PHASE4_EVIDENCE_DATE=2026-05-05`
- `PHASE4_EVIDENCE_MODE=github_connector_readback`
- `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`
- `PHASE4_EXACT_READBACK_REF=master`
- `PHASE4_VALIDATION_MATRIX_BLOB_SHA=1806bad4982cb8bb0433164d091b09d45a0609ba`
- `PHASE4_VALIDATOR_BLOB_SHA=7d09a4957fde591f53e7b32dbfa3d5f1a3e9a1c0`
- `PHASE4_ARTIFACT_DIFF_DOC_BLOB_SHA=417421e73aafe2f8e443e8260913a3b4f7cf551a`
- `PHASE4_ARTIFACT_DIFF_CONTRACT_CHECKER_BLOB_SHA=31cf8c2b2c8da86e823fbc8c8a39fe61c530312f`
- `PHASE4_BUILD_BLOB_SHA=33d3ed8db4e40283212daa115a46e989df28ce6f`
- `PHASE4_MAKEFILE_BLOB_SHA=21322571da23a37c5150cabda0d4d16923a3d313`
- `PHASE4_WORKFLOW_BLOB_SHA=b390d5a5886f4861a0be1987d4c8a66570809841`
- `PHASE4_DOC_README_BLOB_SHA=0c8a1f120b96db315f6434e74210f8232276ecc9`
- `PHASE4_SCRIPT_README_BLOB_SHA=b5c756abe0d1a59ad415cfc62a30548cab42bd1c`
- `PHASE4_TESTS_README_BLOB_SHA=d00dfa952bb45d03764cd8d894c6ed8ed14ba1c2`
- `PHASE4_ATOMIC64_DIFF_BLOB_SHA=43f7ab9383b5653abb459eb70dbf8ba978c981e2`
- `PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA=6dd5b8e0a84fe2f775011d552b629b20da222166`
- `PHASE4_BITMAP_DIFF_BLOB_SHA=9d35b967233469b4a13975a67191483e89c75288`
- `PHASE4_BITMAP_LIVE_HELPER_REPLAY_BLOB_SHA=75d26e94d322da8b9c14e5a9e53cded8576432d3`
- `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=53e2348624d200fb1bc2193f197628541f5e653a`
- `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=e3b207e94d02047d8a128d84b576214c07ca28c5`
- `PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=16`
- `PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true`
- `PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`
- `PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=false`
- `PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=false`
- `PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=false`

## Exact Readback Evidence
- `Documentation/zigux/artifact-diff.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` now all name the same shipped Phase 4 rollback-readiness packet surfaces that the current validator and shared build route still own on `master`.
- `scripts/zigux/check-phase4-gate-evidence.py` is present, and `Documentation/zigux/phase4-validation-matrix.md` now names it as the dedicated Phase 4 rollback-ownership gate while this note exact-pins the same current narrower packet: the validator, artifact-diff contract surfaces, the shared build entrypoint, the three root README summaries, and the manifest-backed runtime atomic64 survey pair.
- `zigux/tests/phase4_runtime_atomic64_diff_manifest.json` and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` remain the manifest-backed runtime atomic64 handoff pair, and the shared build still exposes `phase4-runtime-atomic64-diff-survey-tests` and `phase4-bitmap-live-helper-replay-tests` beside the synthetic rollback gates.
- The exact-readback set is now current for the shipped validator-backed packet, and the manifest-backed runtime atomic64 survey pair now pins the same current `validate-phase4.py` and `phase4-validation-matrix.md` blobs that this note names.
- Current `master` still treats the roadmap-backed sample follow-ups as open gaps rather than shipped gate-evidence targets: `samples/zigux/kprobe_example.zig` remains absent and `samples/zigux/test_fsmount.zig` remains absent.

## Current Conclusion
- The live Phase 4 exact-readback packet is limited to the files that `master` actually ships for rollback ownership, matrix wording, validator wiring, the artifact-diff contract, the gate-evidence note, the shared build route, the helper-backed bitmap replay, and the runtime atomic64 wrapper handoff plus its manifest-backed survey evidence.
- The dedicated gate-evidence note, its explicit rollback-owner row in `Documentation/zigux/phase4-validation-matrix.md`, and the separate runtime atomic64 manifest-backed survey packet are back in sync with the same current validator-backed blob-pin set.
- hard perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved.
