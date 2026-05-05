# Phase 4 Gate Evidence
This note records one exact readback snapshot for the current Phase 4 rollback-ownership and lab-matrix gate definitions.

## Status
- `PHASE4_EVIDENCE_DATE=2026-05-05`
- `PHASE4_EVIDENCE_MODE=github_connector_readback`
- `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`
- `PHASE4_EXACT_READBACK_REF=master`
- `PHASE4_VALIDATION_MATRIX_BLOB_SHA=ab41bb2d0dc190ef56597a1620d2f411783e4f7b`
- `PHASE4_VALIDATOR_BLOB_SHA=e01d58b425152841a145462c4eb368690935c801`
- `PHASE4_ARTIFACT_DIFF_DOC_BLOB_SHA=417421e73aafe2f8e443e8260913a3b4f7cf551a`
- `PHASE4_ARTIFACT_DIFF_CONTRACT_CHECKER_BLOB_SHA=ab25384a9d6cbe926cb98f0e6a2bd33f2a6f0218`
- `PHASE4_BUILD_BLOB_SHA=ca6672b21f08b77305ecf048346026fe474aff43`
- `PHASE4_MAKEFILE_BLOB_SHA=0f35b06ea9b2bb2dfdbdfee7b89697cc2baa29e0`
- `PHASE4_WORKFLOW_BLOB_SHA=c32f78766956e0b60e95a573e356a7b97c01358b`
- `PHASE4_DOC_README_BLOB_SHA=274f1cb74b01598311a41e56955bd4c2774b37a9`
- `PHASE4_SCRIPT_README_BLOB_SHA=86498270e4b53c47310f35b4d2e3bf12e1d01ab3`
- `PHASE4_TESTS_README_BLOB_SHA=e8f22181902e86539eba998e7991d3bc3f7004fa`
- `PHASE4_ATOMIC64_DIFF_BLOB_SHA=b40b2f44d51c7a15b19b0901f6f86c5eeea5f245`
- `PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA=d65abeb53eb0248e1f0978a54cc48a7f561b148e`
- `PHASE4_BITMAP_DIFF_BLOB_SHA=9d35b967233469b4a13975a67191483e89c75288`
- `PHASE4_BITMAP_LIVE_HELPER_REPLAY_BLOB_SHA=75d26e94d322da8b9c14e5a9e53cded8576432d3`
- `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=1d56e11b8b423ff502cef9f2aa607c16daf75302`
- `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=30e9b69af3204d766fb45a43c182d8ebf4e6ca3a`
- `PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=16`
- `PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true`
- `PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`
- `PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=false`
- `PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=false`
- `PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=false`

## Exact Readback Evidence
- The current validator-backed Phase 4 packet is the live set recorded directly in `scripts/zigux/validate-phase4.py`: `Documentation/zigux/phase4-gate-evidence.md`, `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-artifact-diff-contract.py`, `scripts/zigux/validate-phase4.py`, `Documentation/zigux/artifact-diff.md`, `Documentation/zigux/phase4-validation-matrix.md`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`, `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`, `zigux/tests/bitmap_diff.zig`, `zigux/tests/phase4_bitmap_live_helper_replay.zig`, and `zigux/tests/phase4_build.zig`.
- The shared build packet on current `master` wires exactly four replay surfaces: `phase4-runtime-atomic64-diff-tests`, `phase4-runtime-atomic64-diff-survey-tests`, `phase4-bitmap-diff-tests`, and `phase4-bitmap-live-helper-replay-tests`.
- `Documentation/zigux/artifact-diff.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` now truthfully name that four-surface build packet, including `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` as a distinct shipped runtime-atomic64 handoff gate across the three root README summaries.
- The current matrix still records the live ownership and threshold posture the roadmap allows on `master`: the host-side artifact-diff contract remains reviewability-only, the atomic64 wrapper gate remains correctness-only with threshold approval still pending, the runtime atomic64 handoff survey inherits that same pending threshold posture, and the bitmap rollback gate remains correctness-only with threshold approval still pending.
- The runtime atomic64 handoff remains explicit in the live Phase 4 packet through `zigux/tests/atomic64_diff.zig`, `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`, `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`, `Documentation/zigux/phase4-validation-matrix.md`, and the three root README surfaces, but that manifest-backed survey packet still self-pins an older `validate-phase4.py` blob hash than the exact-readback set listed above.
- Current `master` does ship a separate `scripts/zigux/check-phase4-gate-evidence.py`, and that checker now exact-counts the same current narrower packet pinned here: the validator, artifact-diff contract surfaces, the shared build entrypoints, the three root README summaries, and the manifest-backed runtime atomic64 survey handoff.
- Current `master` also does not ship shared-gate blob targets for `phase4_kprobe_example`, `phase4_test_fsmount`, or `phase4_perf_baseline`; the live matrix treats those as remaining roadmap gaps or gap-owning notes rather than part of the shipped validator-backed gate packet that should be blob-pinned here.

## Current Conclusion
- The current Phase 4 exact-readback packet is limited to the files that live `master` actually ships for rollback ownership, matrix wording, validator wiring, the gate-evidence note, the artifact-diff contract, the shared build route, the bitmap helper replay, and the runtime-atomic64 wrapper handoff plus its manifest-backed survey evidence.
- The shared validator and the dedicated gate-evidence checker now fail closed on the current shipped blob-pin set, and the shared validator now also requires the scripts-root, tests-root, and docs-root Phase 4 summaries to keep `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` explicit as a distinct shipped handoff gate.
- The remaining roadmap-backed gaps are unchanged and still truthful in the matrix: `samples/zigux/kprobe_example.zig` remains absent, `samples/zigux/test_fsmount.zig` remains absent, and hard perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved.
