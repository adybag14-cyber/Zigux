# Phase 4 Gate Evidence

This note records one exact readback snapshot for the current Phase 4 rollback-ownership and lab-matrix gate definitions.

## Status

- `PHASE4_EVIDENCE_DATE=2026-05-01`
- `PHASE4_EVIDENCE_MODE=github_connector_readback`
- `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`
- `PHASE4_VALIDATION_MATRIX_BLOB_SHA=d795871544361664c2c02ebe6b99ca36e32dedfa`
- `PHASE4_VALIDATOR_BLOB_SHA=283e044543fd59f0901931fa4bb1055a54936df8`
- `PHASE4_BUILD_BLOB_SHA=57f4c3809387cac39e3153b9bbad17ca92ce3684`
- `PHASE4_MAKEFILE_BLOB_SHA=e051b3c564efa85fdc1e0f4c083415de3eca0a88`
- `PHASE4_WORKFLOW_BLOB_SHA=cc2c75b2bdfa65c4de7198b6625080caf5622589`
- `PHASE4_TEST_FSMOUNT_MANIFEST_BLOB_SHA=a89fc1d8093a9f23850c1623c843f4add3efd8e4`
- `PHASE4_PERF_BASELINE_MANIFEST_BLOB_SHA=44058ac9597848ac0fab37b0ac3c7385b67e2297`
- `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=38efef203cfa190f846a537564f276f319552660`
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

## Current Conclusion

The current Phase 4 rollback-ownership survey packet is internally aligned, and the direct validator replay on the same file set passed both the self-test and the live gate-definition check.

The remaining roadmap-backed gaps are still the same bounded ones:

- `samples/zigux/kprobe_example.zig` is still absent and remains C-anchor-only
- `samples/zigux/test_fsmount.zig` is still absent and remains C-anchor-only through the manifest-backed survey gate
- perf baselines and acceptable limits for the shipped `atomic64_diff.zig` and `bitmap_diff.zig` gates are still intentionally unapproved
