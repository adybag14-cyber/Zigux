# Phase 4 Gate Evidence
This note records one exact readback snapshot for the current Phase 4 rollback-ownership and lab-matrix gate definitions.

## Status
- `PHASE4_EVIDENCE_DATE=2026-05-05`
- `PHASE4_EVIDENCE_MODE=github_connector_readback`
- `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`
- `PHASE4_EXACT_READBACK_REF=master`
- `PHASE4_VALIDATION_MATRIX_BLOB_SHA=ab41bb2d0dc190ef56597a1620d2f411783e4f7b`
- `PHASE4_VALIDATOR_BLOB_SHA=497f0aa0d873777d5183b563e30056b95256a021`
- `PHASE4_ARTIFACT_DIFF_DOC_BLOB_SHA=417421e73aafe2f8e443e8260913a3b4f7cf551a`
- `PHASE4_ARTIFACT_DIFF_CONTRACT_CHECKER_BLOB_SHA=31cf8c2b2c8da86e823fbc8c8a39fe61c530312f`
- `PHASE4_BUILD_BLOB_SHA=ca6672b21f08b77305ecf048346026fe474aff43`
- `PHASE4_MAKEFILE_BLOB_SHA=51fd3bfa7b135de57fecd28d41b240208829176e`
- `PHASE4_WORKFLOW_BLOB_SHA=b2987490b0416f3c2e7f942320a9d8114a7688c4`
- `PHASE4_DOC_README_BLOB_SHA=f15fdff157922f8f34d4be79619f886473002b28`
- `PHASE4_SCRIPT_README_BLOB_SHA=45d447faa925e6f91c0a60170fbd45755961a250`
- `PHASE4_TESTS_README_BLOB_SHA=6233a48e6514f356c69d2eaf7a748f0284f768a8`
- `PHASE4_ATOMIC64_DIFF_BLOB_SHA=54cbcfc190cc04007f7411779d0809b53f89facf`
- `PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA=d65abeb53eb0248e1f0978a54cc48a7f561b148e`
- `PHASE4_BITMAP_DIFF_BLOB_SHA=9d35b967233469b4a13975a67191483e89c75288`
- `PHASE4_BITMAP_LIVE_HELPER_REPLAY_BLOB_SHA=75d26e94d322da8b9c14e5a9e53cded8576432d3`
- `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=0944a8c5babe769e9374773b55396354bca8c563`
- `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=a9631c4b7968ffe39e04fec769187fc78a14886f`
- `PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=16`
- `PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true`
- `PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`
- `PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=false`
- `PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=false`
- `PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=false`

## Exact Readback Evidence
- `Documentation/zigux/artifact-diff.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` now all name the same shipped Phase 4 rollback-readiness packet surfaces that the current validator and shared build route still own on `master`.
- `scripts/zigux/check-phase4-gate-evidence.py` is present and this note now exact-pins the same current narrower packet that checker audits: the validator, artifact-diff contract surfaces, the shared build entrypoint, the three root README summaries, and the manifest-backed runtime atomic64 survey pair.
- `zigux/tests/phase4_runtime_atomic64_diff_manifest.json` and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` remain the manifest-backed runtime atomic64 handoff pair, and the shared build still exposes `phase4-runtime-atomic64-diff-survey-tests` and `phase4-bitmap-live-helper-replay-tests` beside the synthetic rollback gates.
- The exact-readback set is now current for the shipped validator-backed packet, and the manifest-backed runtime atomic64 survey pair now pins the same current `validate-phase4.py` and `phase4-validation-matrix.md` blobs that this note names.
- Current `master` still treats the roadmap-backed sample follow-ups as open gaps rather than shipped gate-evidence targets: `samples/zigux/kprobe_example.zig` remains absent and `samples/zigux/test_fsmount.zig` remains absent.

## Current Conclusion
- The live Phase 4 exact-readback packet is limited to the files that `master` actually ships for rollback ownership, matrix wording, validator wiring, the artifact-diff contract, the gate-evidence note, the shared build route, the helper-backed bitmap replay, and the runtime atomic64 wrapper handoff plus its manifest-backed survey evidence.
- The dedicated gate-evidence note and the separate runtime atomic64 manifest-backed survey packet are back in sync with the same current validator-backed blob-pin set.
- hard perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved.
