# Phase 4 Gate Evidence

This note records one exact readback snapshot for the current Phase 4 rollback-ownership and lab-matrix gate definitions.

## Status

- `PHASE4_EVIDENCE_DATE=2026-05-02`
- `PHASE4_EVIDENCE_MODE=github_connector_readback`
- `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`
- `PHASE4_VALIDATION_MATRIX_BLOB_SHA=bbd40093d39f68163076dc104fe731f0324de4f7`
- `PHASE4_VALIDATOR_BLOB_SHA=9f81ba776b76cb9b8941d538cda5edaca340e48f`
- `PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=097167e6a37e89c46664e264014793c0525ebacf`
- `PHASE4_BUILD_BLOB_SHA=57f4c3809387cac39e3153b9bbad17ca92ce3684`
- `PHASE4_MAKEFILE_BLOB_SHA=a02ca6e2faaaeeb7b8b221cddee38022b2236bc0`
- `PHASE4_WORKFLOW_BLOB_SHA=8023d7b9c685aa5a54a142a80d394cc143b257ca`
- `PHASE4_TEST_FSMOUNT_MANIFEST_BLOB_SHA=7171b6d3f3c407c708d56fd6bb275e2cba44add5`
- `PHASE4_TEST_FSMOUNT_SURVEY_BLOB_SHA=61c22561fbfd67a9d92546c7b7ea76ad909920bc`
- `PHASE4_PERF_BASELINE_MANIFEST_BLOB_SHA=1d3534b3ae5ea9e4211269aaec7b96bce7ab36ae`
- `PHASE4_PERF_BASELINE_SURVEY_BLOB_SHA=93f6f3f479362c235db64e8aaa11e3c65edcff5b`
- `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=2a001ec217dc3acc6d77c08a66707346a950f353`
- `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=77d248a79404ba6eeac41582edd2248e9e0b2989`
- `PHASE4_DOC_README_BLOB_SHA=e6fdbfcb02df98338319f4a615329c8c9d8c5f7d`
- `PHASE4_SCRIPT_README_BLOB_SHA=29fd87bdabb981aefffb2973289d255e4b08f87b`
- `PHASE4_TESTS_README_BLOB_SHA=3df3100e7f6848b90163a56f975946ed1c41036c`
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

- the exact blob pins above still match the live gate-definition files for this packet. `scripts/zigux/validate-phase4.py` now machine-checks the matrix, validator, dedicated gate-evidence checker file, exact checker Makefile wiring, build entrypoint, the workflow step names plus the presence of `make -C zigux phase4-validate` and `make -C zigux phase4-test`, and the three manifest blob pins, while the dedicated `scripts/zigux/check-phase4-gate-evidence.py` helper still keeps its own implementation hash inside the same broader fail-closed survey-file and index-surface blob ledger recorded in this note.
- `Documentation/zigux/phase4-validation-matrix.md` still names the current rollback owners, threshold posture, workflow step names, local replay commands, and reversible-delivery evidence for the two shipped rollback gates plus the two manifest-backed survey gates, and its top current-repo-reality list now also names the dedicated `scripts/zigux/check-phase4-gate-evidence.py` checker explicitly instead of leaving that shipped packet file visible only through the later ownership rows and this evidence note.
- `scripts/zigux/validate-phase4.py` now accepts the current matrix formatting for backticked gate owners and the roadmap-gap rows that spell out the Linux anchor in the first column, and it now also fails closed if either dedicated `check-phase4-gate-evidence.py` Makefile line disappears or the checker file itself drops out of the shared Phase 4 packet.
- the current published validator contract for this packet still records `PHASE4_VALIDATOR_SELF_TEST=pass`, `PHASE4_VALIDATION=pass`, `PHASE4_REQUIRED_FILE_COUNT=23`, and `PHASE4_REQUIRED_MARKER_COUNT=236`, and the dedicated checker keeps those exact status tokens fail-closed in this ledger.
- `zigux/tests/atomic64_diff.zig` still keeps the exact bounded atomic64 replay readable by current check name: add `onestwos` growth and `-1` decrement; sub `onestwos` decrement and `-1` increment; bitwise `or`, `and`, `xor`, and `andnot` on the `v0`/`v1` pair; exchange `v0 -> v1`, `v1 -> v2`, and `minInt(i64) -> -1`; `cmpxchg` match-store and mismatch-no-store; `addUnlessCounter()` blocked and changed paths; `incNotZeroCounter()` positive, zero, `-1`, and `minInt(i64)`; `decIfPositiveCounter()` positive, zero, and negative return-path behavior; ordered selftest families with `checked_returning_paths` and `checked_guard_paths`; single-shot init/selftest/exit transitions; and post-selftest replay across add, sub, bitwise, swap, compare-swap, add-unless, inc-not-zero, and dec-if-positive before final exit.
- the runtime atomic64 reversible-delivery contract also remains explicit in the current exact-readback packet: `lib/atomic64_test.c` stays the source of truth, removing `atomic64_diff.zig` from the shared `phase4_build.zig` entrypoint is the documented rollback move, `runtime_atomic64_diff.zig` remains the single replay body, and the existing Phase 9 runtime atomic64 starter remains the forward path.
- `zigux/tests/bitmap_diff.zig` still keeps the broadened bitmap rollback packet explicit by recording the all-set and all-clear start-state printlist anchors, zero-nbits helper no-op behavior, zero-length range edits on populated anchors, the rounded `bitmap_fill(..., 35)` and `bitmap_fill(..., 115)` drift checkpoints, the `bitmap_set(..., 79, 19)` and `bitmap_clear(..., 79, 19)` cross-boundary windows, the bounded copy-tail packet, and the nth-bit cutoff replay around bit 123.
- the bootstrap workflow still keeps `Self-test Phase 4 validator` as a dedicated step beside `Validate Phase 4 diff gates` and `Run Phase 4 diff tests`, so the matrix's new standalone validator row matches the current shipped workflow rather than inventing a new replay path.
- the dedicated `scripts/zigux/check-phase4-gate-evidence.py` checker now also fails closed if this note keeps the validator count tokens but lets the exact `PHASE4_REQUIRED_FILE_COUNT=23` or `PHASE4_REQUIRED_MARKER_COUNT=236` values drift.
- the dedicated `scripts/zigux/check-phase4-gate-evidence.py` self-test now also mutates every currently pinned non-note blob line in this ledger, including the checker, validator, matrix, build, Makefile, workflow, docs/scripts/tests README, both Phase 4 survey blobs, and all three surveyed-manifest blobs, so implementation, index-surface, manifest, and survey ledger targets all fail closed in the same synthetic replay instead of relying only on live-note inspection.
- `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` now also keeps this exact readback note explicit by requiring the sibling manifest pins, the three index-surface pins, and the shared surveyed snapshot `3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3` instead of leaving that evidence packet as prose-only maintenance.
- `zigux/tests/phase4_test_fsmount_survey.zig` and `zigux/tests/phase4_test_fsmount_manifest.json` now also keep the exact shared `phase4-test-fsmount-survey-tests` replay marker, the isolated `make -C zigux phase4-test-fsmount-survey` route, and the `c_anchor_only_until_test_fsmount_starter_lands` posture explicit beside the shared surveyed snapshot `3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3`, so the remaining sample-side measurability gap stays machine-described instead of living only in the matrix prose.
- `zigux/tests/phase4_perf_baseline_survey.zig` now keeps that same shared surveyed snapshot `3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3` explicit beside `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`, and it now also checks the pending threshold-plan record per shipped rollback gate so the bitmap-side threshold posture and isolated `make -C zigux phase4-bitmap-diff` replay are no longer implied only by the manifest prose.
- `zigux/tests/phase4_perf_baseline_manifest.json` now also keeps one pending threshold-plan record per shipped rollback gate, pinning the current isolated correctness-only replay commands `make -C zigux phase4-runtime-atomic64-diff` and `make -C zigux phase4-bitmap-diff` alongside the still-unapproved benchmark-command and acceptable-limit placeholders for the atomic64 and bitmap gates.
- `samples/kprobes/Makefile` still keeps `obj-$(CONFIG_SAMPLE_KPROBES) += kprobe_example.o`, `samples/kprobes/kprobe_example.c` still anchors the current `kernel_clone` kprobe sample, and the roadmap-gap row in `Documentation/zigux/phase4-validation-matrix.md` still reserves `Validation and Perf Team` as both survey owner and rollback owner while `make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m` remains the current C-anchor replay because `samples/zigux/kprobe_example.zig` is still absent on `master`.
- the dedicated `scripts/zigux/check-phase4-gate-evidence.py` replay is now wired into `make -C zigux phase4-validate` beside the older validator subset, and this note now pins that checker file too, so review can prove both which survey surfaces were inspected and which checker implementation defined the broader blob-ledger contract on the inspected head.
- this note now also records the dedicated checker's own status tokens `PHASE4_GATE_EVIDENCE_SELF_TEST=pass`, `PHASE4_GATE_EVIDENCE_CHECK=pass`, and `PHASE4_GATE_EVIDENCE_TARGET_COUNT=15`, so the broader blob-ledger pass result is explicit evidence instead of living only in the surrounding narrative.
- `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` still expose the same Phase 4 rollback-readiness packet, and the dedicated checker means those three index surfaces are now part of the same fail-closed blob ledger instead of living only as summary guides under this note.

## Current Conclusion

The current Phase 4 rollback-ownership survey packet now has a refreshed exact-readback ledger: the matrix, validator, dedicated checker, Makefile, build, workflow, manifest, survey, and index surfaces named above all read back to the blob pins recorded in this note.

The packet still carries two validator-backed status layers as part of the published contract: the `validate-phase4.py` status bundle for the matrix, validator, dedicated checker, exact checker Makefile wiring, build, workflow, and manifest subset, and the `check-phase4-gate-evidence.py` status bundle for the broader survey-file plus index-surface blob ledger.

One bounded validator-sized gap remains parked in the same lane: current `master` still proves the workflow step names and the presence of `make -C zigux phase4-validate` plus `make -C zigux phase4-test`, but it does not yet fail closed on the exact run-line counts for those two replays inside `.github/workflows/zigux-bootstrap.yml`.

That keeps the README surfaces truthful summaries for the packet, and this note is again a current blob ledger for the broader survey and index surfaces instead of a stale audit record.

The dedicated checker now also keeps the runtime atomic64 reversible-delivery sentence fail-closed in this note, so the rollback move, single replay body, and forward-path wording cannot silently drift back into prose-only guidance.

The current correctness-only anchors for the still-unapproved Phase 4 threshold plans remain `make -C zigux phase4-runtime-atomic64-diff` and `make -C zigux phase4-bitmap-diff`, so the packet still ties future perf-baseline work back to named isolated rollback replays instead of broad shared-bundle timing claims.

The remaining roadmap-backed gaps are still the same bounded ones:

- `samples/zigux/kprobe_example.zig` is still absent, still tied to `samples/kprobes/kprobe_example.c`, and still depends on the matrix-only `make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m` replay path rather than a dedicated survey gate on current `master`
- `samples/zigux/test_fsmount.zig` is still absent and remains C-anchor-only through the manifest-backed survey gate
- perf baselines and acceptable limits for the shipped `atomic64_diff.zig` and `bitmap_diff.zig` gates are still intentionally unapproved
