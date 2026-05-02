# Phase 4 Gate Evidence

This note records one exact readback snapshot for the current Phase 4 rollback-ownership and lab-matrix gate definitions.

## Status

- `PHASE4_EVIDENCE_DATE=2026-05-02`
- `PHASE4_EVIDENCE_MODE=github_connector_readback`
- `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`
- `PHASE4_VALIDATION_MATRIX_BLOB_SHA=977d0ca963e217be12c8eb3372c078b74394d309`
- `PHASE4_VALIDATOR_BLOB_SHA=9f81ba776b76cb9b8941d538cda5edaca340e48f`
- `PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=d4dd173d61fb43941b21ee98dd74463c7c7da9d8`
- `PHASE4_BUILD_BLOB_SHA=57f4c3809387cac39e3153b9bbad17ca92ce3684`
- `PHASE4_MAKEFILE_BLOB_SHA=393503231223dbdfc393bb831c807f5c0112383d`
- `PHASE4_WORKFLOW_BLOB_SHA=d8e33b54488171c873d86b80ceaff8479d999bb8`
- `PHASE4_TEST_FSMOUNT_MANIFEST_BLOB_SHA=dba16a0727fc765d1674a9cb11e4bed8849c40e4`
- `PHASE4_TEST_FSMOUNT_SURVEY_BLOB_SHA=1fc30e8e7f43001dab536eb335fdee47b568b293`
- `PHASE4_PERF_BASELINE_MANIFEST_BLOB_SHA=b17843d7ee9d34a8c4f7f30d688701be9f6478d5`
- `PHASE4_PERF_BASELINE_SURVEY_BLOB_SHA=07f586ad7e7ca89eeac1ce4fb1a8b5e693952876`
- `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=2a001ec217dc3acc6d77c08a66707346a950f353`
- `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=868a7470c48775e95e1b263316196e7dbadda1cc`
- `PHASE4_DOC_README_BLOB_SHA=4f3358383d6845e2b76faaf4dac172fe78026082`
- `PHASE4_SCRIPT_README_BLOB_SHA=98d9fc78614f30c4b59548a829ba49e1a0d2c2fb`
- `PHASE4_TESTS_README_BLOB_SHA=6b342ec6c6a3a4e1b8c99eb39e97b8facc7da1ba`
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
- `Documentation/zigux/phase4-validation-matrix.md` still names the current rollback owners, threshold posture, workflow step names, local replay commands, and reversible-delivery evidence for the two shipped rollback gates plus the two manifest-backed survey gates, and it now also names the standalone `python3 scripts/zigux/validate-phase4.py --self-test` workflow replay explicitly instead of leaving that synthetic contract surface implied by workflow prose alone.
- `scripts/zigux/validate-phase4.py` now accepts the current matrix formatting for backticked gate owners and the roadmap-gap rows that spell out the Linux anchor in the first column, and it now also fails closed if either dedicated `check-phase4-gate-evidence.py` Makefile line disappears or the checker file itself drops out of the shared Phase 4 packet.
- direct validator replay on that same source snapshot still returned `PHASE4_VALIDATOR_SELF_TEST=pass`, `PHASE4_VALIDATION=pass`, `PHASE4_REQUIRED_FILE_COUNT=23`, and `PHASE4_REQUIRED_MARKER_COUNT=236` for the machine-checked matrix, validator, dedicated checker, Makefile, build, workflow, and manifest subset.
- `zigux/tests/atomic64_diff.zig` still keeps the exact bounded atomic64 replay readable by current check name: add `onestwos` growth and `-1` decrement; sub `onestwos` decrement and `-1` increment; bitwise `or`, `and`, `xor`, and `andnot` on the `v0`/`v1` pair; exchange `v0 -> v1`, `v1 -> v2`, and `minInt(i64) -> -1`; `cmpxchg` match-store and mismatch-no-store; `addUnlessCounter()` blocked and changed paths; `incNotZeroCounter()` positive, zero, `-1`, and `minInt(i64)`; `decIfPositiveCounter()` positive, zero, and negative return-path behavior; ordered selftest families with `checked_returning_paths` and `checked_guard_paths`; single-shot init/selftest/exit transitions; and post-selftest replay across add, sub, bitwise, swap, compare-swap, add-unless, inc-not-zero, and dec-if-positive before final exit.
- the bootstrap workflow still keeps `Self-test Phase 4 validator` as a dedicated step beside `Validate Phase 4 diff gates` and `Run Phase 4 diff tests`, so the matrix's new standalone validator row matches the current shipped workflow rather than inventing a new replay path.
- the dedicated `scripts/zigux/check-phase4-gate-evidence.py` checker now also fails closed if this note keeps the validator count tokens but lets the exact `PHASE4_REQUIRED_FILE_COUNT=23` or `PHASE4_REQUIRED_MARKER_COUNT=236` values drift.
- `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` now also keeps this exact readback note explicit by requiring the sibling manifest pins, the three index-surface pins, and the shared surveyed snapshot `3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3` instead of leaving that evidence packet as prose-only maintenance.
- `zigux/tests/phase4_test_fsmount_survey.zig` and `zigux/tests/phase4_perf_baseline_survey.zig` now keep that same shared surveyed snapshot `3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3` explicit beside `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`, so the rollback packet now keeps the manifest-backed survey trio aligned alongside the atomic64 packet instead of leaving two survey surfaces implied only by prose.
- the dedicated `scripts/zigux/check-phase4-gate-evidence.py` replay is now wired into `make -C zigux phase4-validate` beside the older validator subset, and this note now pins that checker file too, so review can prove both which survey surfaces were inspected and which checker implementation defined the broader blob-ledger contract on the inspected head.
- this note now also records the dedicated checker's own status tokens `PHASE4_GATE_EVIDENCE_SELF_TEST=pass`, `PHASE4_GATE_EVIDENCE_CHECK=pass`, and `PHASE4_GATE_EVIDENCE_TARGET_COUNT=15`, so the broader blob-ledger pass result is explicit evidence instead of living only in the surrounding narrative.
- `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` still expose the same Phase 4 rollback-readiness packet, and the dedicated checker means those three index surfaces are now part of the same fail-closed blob ledger instead of living only as summary guides under this note.

## Current Conclusion

The current Phase 4 rollback-ownership survey packet is aligned at two validator-backed layers: the direct `validate-phase4.py` replay still passes for the matrix, validator, dedicated checker, exact checker Makefile wiring, build, workflow, and manifest subset, and the dedicated `check-phase4-gate-evidence.py` path still fail-closes the survey-file plus index-surface blob pins recorded in this note while also pinning the checker implementation that owns that broader proof shape.

This note now carries both validator layers' pass tokens directly, and the paired matrix now names the standalone validator self-test route explicitly, so the machine-checked Phase 4 proof shape is visible from the evidence ledger itself instead of being inferred from prose around the checker.

That means the current README surfaces remain truthful summaries for the packet, and this note is now a fully checked blob ledger for the broader survey and index surfaces instead of the only audit-only record for them.

The remaining roadmap-backed gaps are still the same bounded ones:

- `samples/zigux/kprobe_example.zig` is still absent and remains C-anchor-only
- `samples/zigux/test_fsmount.zig` is still absent and remains C-anchor-only through the manifest-backed survey gate
- perf baselines and acceptable limits for the shipped `atomic64_diff.zig` and `bitmap_diff.zig` gates are still intentionally unapproved
