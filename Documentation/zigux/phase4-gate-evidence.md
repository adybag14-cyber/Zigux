# Phase 4 Gate Evidence
This note records one exact readback snapshot for the current Phase 4 rollback-ownership and lab-matrix gate definitions.

## Status
- `PHASE4_EVIDENCE_DATE=2026-05-05`
- `PHASE4_EVIDENCE_MODE=github_connector_readback`
- `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`
- `PHASE4_EXACT_READBACK_REF=master`
- `PHASE4_VALIDATION_MATRIX_BLOB_SHA=fb08ef61f56120a89ccbbbb6e9fb65135d0560b0`
- `PHASE4_VALIDATOR_BLOB_SHA=9dea37cf163067c1972931728c67ce45884d4508`
- `PHASE4_ARTIFACT_DIFF_DOC_BLOB_SHA=6c0bcd17e629e392e0a88b1d01b51f4ad1a2584d`
- `PHASE4_ARTIFACT_DIFF_CONTRACT_CHECKER_BLOB_SHA=ab25384a9d6cbe926cb98f0e6a2bd33f2a6f0218`
- `PHASE4_BUILD_BLOB_SHA=ca6672b21f08b77305ecf048346026fe474aff43`
- `PHASE4_MAKEFILE_BLOB_SHA=9a077e4609ff19ef670cf089e850aa46f6e114d1`
- `PHASE4_WORKFLOW_BLOB_SHA=c32f78766956e0b60e95a573e356a7b97c01358b`
- `PHASE4_DOC_README_BLOB_SHA=e1a7fa1a4213f421381440f09718f2ff312e9b95`
- `PHASE4_SCRIPT_README_BLOB_SHA=c8ff9f85e203684c3034127bf296ee6be817ef43`
- `PHASE4_TESTS_README_BLOB_SHA=202be189fd6aa33b7b58aff2e2d63a2dc1e499a8`
- `PHASE4_ATOMIC64_DIFF_BLOB_SHA=b40b2f44d51c7a15b19b0901f6f86c5eeea5f245`
- `PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA=d65abeb53eb0248e1f0978a54cc48a7f561b148e`
- `PHASE4_BITMAP_DIFF_BLOB_SHA=9d35b967233469b4a13975a67191483e89c75288`
- `PHASE4_BITMAP_LIVE_HELPER_REPLAY_BLOB_SHA=75d26e94d322da8b9c14e5a9e53cded8576432d3`
- `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=ae52459716b344bfa776d78a72826b3b672f7a9e`
- `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=deb5566a0b31d9d38e3b2913162fc2a066d03c60`
- `PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=16`
- `PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=false`
- `PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=false`
- `PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=false`
- `PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=false`

## Exact Readback Evidence
- The current validator-backed Phase 4 packet is the live set recorded directly in `scripts/zigux/validate-phase4.py`: `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-artifact-diff-contract.py`, `scripts/zigux/validate-phase4.py`, `Documentation/zigux/artifact-diff.md`, `Documentation/zigux/phase4-validation-matrix.md`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/bitmap_diff.zig`, `zigux/tests/phase4_bitmap_live_helper_replay.zig`, and `zigux/tests/phase4_build.zig`.
- The shared build packet on current `master` now wires exactly four replay surfaces: `phase4-runtime-atomic64-diff-tests`, `phase4-runtime-atomic64-diff-survey-tests`, `phase4-bitmap-diff-tests`, and `phase4-bitmap-live-helper-replay-tests`.
- The current root summaries keep the validator route, the roadmap-facing `zigux/tests/atomic64_diff.zig` wrapper, the shared `zigux/tests/runtime_atomic64_diff.zig` replay body, `zigux/tests/bitmap_diff.zig`, and the shared `zigux/tests/phase4_build.zig` route explicit, but they do not enumerate `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` as a distinct shipped build gate.
- The current matrix still records the live ownership and threshold posture the roadmap allows on `master`: the host-side artifact-diff contract remains reviewability-only, the atomic64 wrapper gate remains correctness-only with threshold approval still pending, the runtime atomic64 handoff survey inherits that same pending threshold posture, and the bitmap rollback gate remains correctness-only with threshold approval still pending.
- The runtime atomic64 handoff remains explicit in the live Phase 4 packet through `zigux/tests/atomic64_diff.zig`, `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`, `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`, `Documentation/zigux/phase4-validation-matrix.md`, and the three root README surfaces, but that survey packet now self-pins older `phase4_build`, `validate-phase4.py`, and `phase4-validation-matrix.md` blob hashes than the exact-readback set listed above.
- Current `master` does not ship a separate `scripts/zigux/check-phase4-gate-evidence.py` or another dedicated workflow-route checker file, so this exact-readback note should not claim a separate checker-backed gate-definition packet beyond the live validator and artifact-diff contract checker.
- Current `master` also does not ship shared-gate blob targets for `phase4_kprobe_example`, `phase4_test_fsmount`, or `phase4_perf_baseline`; the live matrix treats those as remaining roadmap gaps or gap-owning notes rather than part of the shipped validator-backed gate packet that should be blob-pinned here.

## Current Conclusion
- The current Phase 4 exact-readback packet is limited to the files that live `master` actually ships for rollback ownership, matrix wording, validator wiring, the artifact-diff contract, the shared build route, the bitmap helper replay, and the runtime-atomic64 wrapper handoff plus its manifest-backed survey evidence.
- The matrix, validator, and shared build entrypoint are aligned on the current live gate definitions, but the artifact-diff note and the three root README surfaces still under-describe the four-surface build packet by not naming the runtime atomic64 survey gate explicitly.
- The remaining roadmap-backed gaps are unchanged and still truthful in the matrix: `samples/zigux/kprobe_example.zig` remains absent, `samples/zigux/test_fsmount.zig` remains absent, and hard perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved.
