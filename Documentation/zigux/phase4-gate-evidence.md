# Phase 4 Gate Evidence

This note records one exact readback snapshot for the current Phase 4 rollback-ownership and lab-matrix gate definitions.

## Status

- `PHASE4_EVIDENCE_DATE=2026-05-01`
- `PHASE4_EVIDENCE_MODE=github_connector_readback`
- `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`
- `PHASE4_VALIDATION_MATRIX_BLOB_SHA=da0a50dcf4c1b277b035f17c23575bd522016ec2`
- `PHASE4_VALIDATOR_BLOB_SHA=9f81ba776b76cb9b8941d538cda5edaca340e48f`
- `PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=e2c0bacf1653c2f19ca6f6abfdf02eda23c43e90`
- `PHASE4_BUILD_BLOB_SHA=57f4c3809387cac39e3153b9bbad17ca92ce3684`
- `PHASE4_MAKEFILE_BLOB_SHA=cc72aabfbc191ead57e9da22760d9a23d244206e`
- `PHASE4_WORKFLOW_BLOB_SHA=baad28e89c761af30961433e34bacec2a7e75d53`
- `PHASE4_TEST_FSMOUNT_MANIFEST_BLOB_SHA=a89fc1d8093a9f23850c1623c843f4add3efd8e4`
- `PHASE4_TEST_FSMOUNT_SURVEY_BLOB_SHA=954bc9a3b7fdc58ca5bc52b6fbbd24b1e3edbef7`
- `PHASE4_PERF_BASELINE_MANIFEST_BLOB_SHA=44058ac9597848ac0fab37b0ac3c7385b67e2297`
- `PHASE4_PERF_BASELINE_SURVEY_BLOB_SHA=8c2fbdb1debc254133a79d3b7884f8d6e4c9a08c`
- `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=38efef203cfa190f846a537564f276f319552660`
- `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=37c73d0b23df8c6876ae5402ca2c9336b3fedf74`
- `PHASE4_DOC_README_BLOB_SHA=60a6371fa2eee1c89a0ef33a16397975ae3b9c3d`
- `PHASE4_SCRIPT_README_BLOB_SHA=e43fb76833d0bef58dd3f51a6b88394bae191ef7`
- `PHASE4_TESTS_README_BLOB_SHA=5cad09e003f399741be7332d0fba479e5f148d00`
- `PHASE4_VALIDATOR_SELF_TEST=pass`
- `PHASE4_VALIDATION=pass`
- `PHASE4_REQUIRED_FILE_COUNT=23`
- `PHASE4_REQUIRED_MARKER_COUNT=236`
- `PHASE4_GATE_EVIDENCE_SELF_TEST=pass`
- `PHASE4_GATE_EVIDENCE_CHECK=pass`
- `PHASE4_GATE_EVIDENCE_TARGET_COUNT=15`

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

- the exact blob pins above still match the live gate-definition files for this packet. `scripts/zigux/validate-phase4.py` now machine-checks the matrix, validator, dedicated gate-evidence checker file, exact checker Makefile wiring, build entrypoint, workflow, and the three manifest blob pins, while the dedicated `scripts/zigux/check-phase4-gate-evidence.py` helper still keeps its own implementation hash inside the same broader fail-closed survey-file and index-surface blob ledger recorded in this note.
- `Documentation/zigux/phase4-validation-matrix.md` still names the current rollback owners, threshold posture, workflow step names, local replay commands, and reversible-delivery evidence for the two shipped rollback gates plus the two manifest-backed survey gates.
- `scripts/zigux/validate-phase4.py` now accepts the current matrix formatting for backticked gate owners and the roadmap-gap rows that spell out the Linux anchor in the first column, and it now also fails closed if either dedicated `check-phase4-gate-evidence.py` Makefile line disappears or the checker file itself drops out of the shared Phase 4 packet.
- direct validator replay on that same source snapshot still returned `PHASE4_VALIDATOR_SELF_TEST=pass`, `PHASE4_VALIDATION=pass`, `PHASE4_REQUIRED_FILE_COUNT=23`, and `PHASE4_REQUIRED_MARKER_COUNT=236` for the machine-checked matrix, validator, dedicated checker, Makefile, build, workflow, and manifest subset.
- `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` now also keeps this exact readback note explicit by requiring the sibling manifest pins, the three index-surface pins, and the shared surveyed snapshot `ec9aa1b15a34e581625da1056956ecb5dd6cd76a` instead of leaving that evidence packet as prose-only maintenance.
- the `test_fsmount` and perf-baseline survey manifests plus their paired survey tests still pin that same shared surveyed snapshot `ec9aa1b15a34e581625da1056956ecb5dd6cd76a`, so the rollback packet now keeps the manifest-backed survey trio aligned alongside the atomic64 packet.
- the dedicated `scripts/zigux/check-phase4-gate-evidence.py` replay is now wired into `make -C zigux phase4-validate` beside the older validator subset, and this note now pins that checker file too, so review can prove both which survey surfaces were inspected and which checker implementation defined the broader blob-ledger contract on the inspected head.
- this note now also records the dedicated checker's own status tokens `PHASE4_GATE_EVIDENCE_SELF_TEST=pass`, `PHASE4_GATE_EVIDENCE_CHECK=pass`, and `PHASE4_GATE_EVIDENCE_TARGET_COUNT=15`, so the broader blob-ledger pass result is explicit evidence instead of living only in the surrounding narrative.
- `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` still expose the same Phase 4 rollback-readiness packet, and the dedicated checker means those three index surfaces are now part of the same fail-closed blob ledger instead of living only as summary guides under this note.

## Current Conclusion

The current Phase 4 rollback-ownership survey packet is aligned at two validator-backed layers: the direct `validate-phase4.py` replay still passes for the matrix, validator, dedicated checker, exact checker Makefile wiring, build, workflow, and manifest subset, and the dedicated `check-phase4-gate-evidence.py` path still fail-closes the survey-file plus index-surface blob pins recorded in this note while also pinning the checker implementation that owns that broader proof shape.

This note now carries both validator layers' pass tokens directly, so the machine-checked Phase 4 proof shape is visible from the evidence ledger itself instead of being inferred from prose around the checker.

That means the current README surfaces remain truthful summaries for the packet, and this note is now a fully checked blob ledger for the broader survey and index surfaces instead of the only audit-only record for them.

The remaining roadmap-backed gaps are still the same bounded ones:

- `samples/zigux/kprobe_example.zig` is still absent and remains C-anchor-only
- `samples/zigux/test_fsmount.zig` is still absent and remains C-anchor-only through the manifest-backed survey gate
- perf baselines and acceptable limits for the shipped `atomic64_diff.zig` and `bitmap_diff.zig` gates are still intentionally unapproved
