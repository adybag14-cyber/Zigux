# Phase 4 Gate Evidence

This note records one exact readback snapshot for the current Phase 4 rollback-ownership and lab-matrix gate definitions.

## Status

- `PHASE4_EVIDENCE_DATE=2026-05-01`
- `PHASE4_EVIDENCE_MODE=github_connector_readback`
- `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`
- `PHASE4_VALIDATION_MATRIX_BLOB_SHA=da0a50dcf4c1b277b035f17c23575bd522016ec2`
- `PHASE4_VALIDATOR_BLOB_SHA=283e044543fd59f0901931fa4bb1055a54936df8`
- `PHASE4_BUILD_BLOB_SHA=57f4c3809387cac39e3153b9bbad17ca92ce3684`
- `PHASE4_MAKEFILE_BLOB_SHA=e051b3c564efa85fdc1e0f4c083415de3eca0a88`
- `PHASE4_WORKFLOW_BLOB_SHA=cc2c75b2bdfa65c4de7198b6625080caf5622589`
- `PHASE4_TEST_FSMOUNT_MANIFEST_BLOB_SHA=a89fc1d8093a9f23850c1623c843f4add3efd8e4`
- `PHASE4_TEST_FSMOUNT_SURVEY_BLOB_SHA=1b4add365fc9edbc705a80f0b1f1b1d916db2da4`
- `PHASE4_PERF_BASELINE_MANIFEST_BLOB_SHA=44058ac9597848ac0fab37b0ac3c7385b67e2297`
- `PHASE4_PERF_BASELINE_SURVEY_BLOB_SHA=8c2fbdb1debc254133a79d3b7884f8d6e4c9a08c`
- `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=38efef203cfa190f846a537564f276f319552660`
- `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=017392a6d510860e33931d396e0da305a6a4102e`
- `PHASE4_DOC_README_BLOB_SHA=42d713fb271dc01f22afe24a4d5af20a65683d7d`
- `PHASE4_SCRIPT_README_BLOB_SHA=b1e188748e818d1f0d1dc20f7ff48323ddeef10d`
- `PHASE4_TESTS_README_BLOB_SHA=3e63f0cd7d443f80921353e7b250bc6a9bb5d36d`
- `PHASE4_VALIDATOR_SELF_TEST=pass`
- `PHASE4_VALIDATION=pass`
- `PHASE4_REQUIRED_FILE_COUNT=22`
- `PHASE4_REQUIRED_MARKER_COUNT=232`

## Roadmap Contract

The current Phase 4 roadmap contract still says this tranche must make future Zigux ports measurable and reversible by keeping parity harnesses, perf baselines and thresholds, rollback ownership, lab and CI matrices, and artifact-diff checks for host-side tools reviewable together.

The current roadmap-backed destinations for that packet remain:

- `zigux/tests/atomic64_diff.zig`
- `zigux/tests/bitmap_diff.zig`
- `samples/zigux/kprobe_example.zig`
- `samples/zigux/test_fsmount.zig`
- `scripts/zigux/` diff and layout tools

## Exact Readback Evidence

The current packet stayed aligned across the following readbacks on `master`:

- the exact blob pins above match the live gate-definition files for this packet.
- `Documentation/zigux/phase4-validation-matrix.md` still names the current rollback owners, threshold posture, workflow step names, local replay commands, and reversible-delivery evidence for the two shipped rollback gates plus the two manifest-backed survey gates.
- `scripts/zigux/validate-phase4.py` now accepts the current matrix formatting for backticked gate owners and the roadmap-gap rows that spell out the Linux anchor in the first column, so the validator stays aligned with the already-published Phase 4 matrix instead of failing on formatting drift alone.
- direct validator replay on that same source snapshot returned `PHASE4_VALIDATOR_SELF_TEST=pass`, `PHASE4_VALIDATION=pass`, `PHASE4_REQUIRED_FILE_COUNT=22`, and `PHASE4_REQUIRED_MARKER_COUNT=232`.
- `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` now also keeps this exact readback note explicit by requiring the sibling manifest pins, the three index-surface pins, and the shared surveyed snapshot `ec9aa1b15a34e581625da1056956ecb5dd6cd76a` instead of leaving that evidence packet as prose-only maintenance.
- the `test_fsmount` and perf-baseline survey manifests plus their paired survey tests still pin that same shared surveyed snapshot `ec9aa1b15a34e581625da1056956ecb5dd6cd76a`, so the rollback packet now keeps the manifest-backed survey trio aligned alongside the atomic64 packet.
- `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` still expose the same Phase 4 rollback-readiness packet, and the blob pins above now keep those three index surfaces directly audit-friendly when the shared packet moves.

## Current Conclusion

The current Phase 4 rollback-ownership survey packet is internally aligned, the direct validator replay on the same file set passed both the self-test and the live gate-definition check, and the dedicated atomic64 survey now also fails if this exact readback note drops the sibling manifest pins, the index-surface pins, or the shared surveyed snapshot.

The remaining roadmap-backed gaps are still the same bounded ones:

- `samples/zigux/kprobe_example.zig` is still absent and remains C-anchor-only
- `samples/zigux/test_fsmount.zig` is still absent and remains C-anchor-only through the manifest-backed survey gate
- perf baselines and acceptable limits for the shipped `atomic64_diff.zig` and `bitmap_diff.zig` gates are still intentionally unapproved
