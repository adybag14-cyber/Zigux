# Phase 4 Gate Evidence

This note records one exact readback snapshot for the current Phase 4 rollback-ownership and lab-matrix gate definitions.

## Status

- `PHASE4_EVIDENCE_DATE=2026-05-03`
- `PHASE4_EVIDENCE_MODE=github_connector_readback`
- `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`
- `PHASE4_VALIDATION_MATRIX_BLOB_SHA=1fc207515cd2b75b0e3a7781dfa8a4bebce23e0e`
- `PHASE4_VALIDATOR_BLOB_SHA=9f81ba776b76cb9b8941d538cda5edaca340e48f`
- `PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=d165dcf73fbab75c2c63802f412a0dce7b87a6af`
- `PHASE4_BUILD_BLOB_SHA=19472845adf51822a5775340c31aa3bd5db57a97`
- `PHASE4_MAKEFILE_BLOB_SHA=c6921b5ce12f60abbada4c5d8905b60b616701e5`
- `PHASE4_WORKFLOW_BLOB_SHA=00bcad2fb5fe8fb71ca48807531ca7027e90517d`
- `PHASE4_TEST_FSMOUNT_MANIFEST_BLOB_SHA=7171b6d3f3c407c708d56fd6bb275e2cba44add5`
- `PHASE4_TEST_FSMOUNT_SURVEY_BLOB_SHA=006f9c54cfa12c3029979f5256192465778790b6`
- `PHASE4_PERF_BASELINE_MANIFEST_BLOB_SHA=e66248e68cfa3a844b469ae83390b49f50fa57e7`
- `PHASE4_PERF_BASELINE_SURVEY_BLOB_SHA=84f2fdee43f1423e708a55e8c8c8b148a95a04f1`
- `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=0e077abb153279e91dad4a52ad89152092e287df`
- `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=7ccaa0c395eeaa8129249943f0752540b0c4ffa0`
- `PHASE4_DOC_README_BLOB_SHA=3d0b129301ee059cd3d6a0d23f8efdf432133b60`
- `PHASE4_SCRIPT_README_BLOB_SHA=63dc6baf6080e45a217a3fbdb06ca53951583f16`
- `PHASE4_TESTS_README_BLOB_SHA=824cc865585149812626ec139bfa2a338e658ecd`
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

- the exact blob pins above still match the live gate-definition files for this packet. `scripts/zigux/validate-phase4.py` now machine-checks the artifact-diff note, the validation matrix, the validator and dedicated gate-evidence checker file, the exact checker Makefile wiring, the shared build entrypoint, the workflow step names plus the presence of `make -C zigux phase4-validate` and `make -C zigux phase4-test`, the runtime atomic64 and bitmap replay surfaces, the docs-root, scripts-root, and tests-root README hooks, the two Phase 4 survey files, and the three manifest-backed survey packets at the top-level status and survey-summary layer the shared validator currently owns, while the dedicated `scripts/zigux/check-phase4-gate-evidence.py` helper still keeps its own implementation hash inside the same broader fail-closed survey-file and index-surface blob ledger recorded in this note, and it now also proves the three Phase 4 survey Zig tests still carry the same shared surveyed snapshot as the sibling manifests before this ledger calls the packet aligned. The current shared build already carries the separate `phase4-kprobe-example-survey-tests` packet too, but that kprobe roadmap row is still tracked here and in the matrix as a shared-build-backed survey follow-up rather than a validator-owned packet.
- `Documentation/zigux/phase4-validation-matrix.md` still names the current rollback owners, threshold posture, workflow step names, local replay commands, and reversible-delivery evidence for the two shipped rollback gates plus the three manifest-backed survey gates, and the current atomic64 row now also spells out the bounded `subCounter()` decrement-plus-`-1` increment replay and the single-shot init/selftest/exit lifecycle checks beside the already recorded add, bitwise, exchange, cmpxchg, guard-path, and post-selftest markers.
- `scripts/zigux/validate-phase4.py` now accepts the current matrix formatting for backticked gate owners and the roadmap-gap rows that spell out the Linux anchor in the first column, and it now also fails closed if either dedicated `check-phase4-gate-evidence.py` Makefile line disappears or the checker file itself drops out of the shared Phase 4 packet.
- the current published validator contract for this packet still records `PHASE4_VALIDATOR_SELF_TEST=pass`, `PHASE4_VALIDATION=pass`, `PHASE4_REQUIRED_FILE_COUNT=23`, and `PHASE4_REQUIRED_MARKER_COUNT=236`, and the dedicated checker keeps those exact status tokens fail-closed in this ledger.
- `zigux/tests/atomic64_diff.zig` still keeps the exact bounded atomic64 replay readable by current check name: add `onestwos` growth and `-1` decrement; sub `onestwos` decrement and `-1` increment; bitwise `or`, `and`, `xor`, and `andnot` on the `v0`/`v1` pair; exchange `v0 -> v1`, `v1 -> v2`, and `minInt(i64) -> -1`; `cmpxchg` match-store and mismatch-no-store; `addUnlessCounter()` blocked and changed paths; `incNotZeroCounter()` positive, zero, `-1`, and `minInt(i64)`; `decIfPositiveCounter()` positive, zero, and negative return-path behavior; ordered selftest families with `checked_returning_paths` and `checked_guard_paths`; single-shot init/selftest/exit transitions; and post-selftest replay across add, sub, bitwise, swap, compare-swap, add-unless, inc-not-zero, and dec-if-positive before final exit.
- `zigux/tests/atomic64_diff.zig` now also keeps the dedicated `scripts/zigux/check-phase4-gate-evidence.py` path explicit from the canonical roadmap-facing wrapper by requiring the paired `zigux/Makefile` self-test and live-checker wiring, the checker blob-pin marker, and the published `PHASE4_GATE_EVIDENCE_SELF_TEST=pass`, `PHASE4_GATE_EVIDENCE_CHECK=pass`, and `PHASE4_GATE_EVIDENCE_TARGET_COUNT=15` ledger tokens instead of leaving that checker packet reviewable only through the shared validator and this note.
- the runtime atomic64 reversible-delivery contract also remains explicit in the current exact-readback packet: `lib/atomic64_test.c` stays the source of truth, removing `atomic64_diff.zig` from the shared `phase4_build.zig` entrypoint is the documented rollback move, `runtime_atomic64_diff.zig` remains the single replay body, and the existing Phase 9 runtime atomic64 starter remains the forward path.
- `zigux/tests/bitmap_diff.zig` still keeps the broadened bitmap rollback packet explicit by recording the all-set and all-clear start-state printlist anchors, zero-nbits helper no-op behavior, zero-length range edits on populated anchors, the rounded `bitmap_fill(..., 35)` and `bitmap_fill(..., 115)` checkpoints that now match the current Linux anchor behavior, the `bitmap_set(..., 79, 19)` and `bitmap_clear(..., 79, 19)` cross-boundary windows, the bounded copy-tail packet, and the nth-bit cutoff replay around bit 123.
- the bootstrap workflow still keeps `Self-test Phase 4 validator` as a dedicated step beside `Validate Phase 4 diff gates` and `Run Phase 4 diff tests`, so the matrix's new standalone validator row matches the current shipped workflow rather than inventing a new replay path.
- the dedicated `scripts/zigux/check-phase4-gate-evidence.py` checker now also fails closed if the Phase 4 workflow stops carrying exactly one `make -C zigux phase4-validate` run line or exactly one `make -C zigux phase4-test` run line under the Phase 4 steps, so that exact count is no longer prose-only drift inside this note.
- the dedicated `scripts/zigux/check-phase4-gate-evidence.py` checker now also fails closed if this note keeps the validator count tokens but lets the exact `PHASE4_REQUIRED_FILE_COUNT=23` or `PHASE4_REQUIRED_MARKER_COUNT=236` values drift.
- the dedicated `scripts/zigux/check-phase4-gate-evidence.py` self-test now also mutates every currently pinned non-note blob line in this ledger, including the checker, validator, matrix, build, Makefile, workflow, docs/scripts/tests README, both Phase 4 survey blobs, and all three surveyed-manifest blobs, so implementation, index-surface, manifest, and survey ledger targets all fail closed in the same synthetic replay instead of relying only on live-note inspection.
- `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` now also keeps this exact readback note explicit by requiring the sibling manifest pins, the three index-surface pins, the shared surveyed snapshot `3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3`, the exact published `PHASE4_REQUIRED_FILE_COUNT=23`, `PHASE4_REQUIRED_MARKER_COUNT=236`, and `PHASE4_GATE_EVIDENCE_TARGET_COUNT=15` values, and the exact atomic64 matrix row fields for the `ABI and Runtime Team` owner, `ABI and Runtime Team` rollback owner, isolated `make -C zigux phase4-runtime-atomic64-diff` and direct `zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig` replays, and `threshold_pending_until_runtime_atomic64_scope_widens` posture instead of allowing those governance markers to drift silently.
- `zigux/tests/phase4_test_fsmount_survey.zig` and `zigux/tests/phase4_test_fsmount_manifest.json` now also keep the exact shared `phase4-test-fsmount-survey-tests` replay marker, the isolated `make -C zigux phase4-test-fsmount-survey` route, and the `c_anchor_only_until_test_fsmount_starter_lands` posture explicit beside the shared surveyed snapshot `3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3`, so the remaining sample-side measurability gap stays machine-described instead of living only in the matrix prose.
- `zigux/tests/phase4_perf_baseline_survey.zig` now keeps that same shared surveyed snapshot `3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3` explicit beside `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`, and it now also checks the pending threshold-plan record per shipped rollback gate so the bitmap-side threshold posture and isolated `make -C zigux phase4-bitmap-diff` replay are no longer implied only by the manifest prose.
- the exact per-gate Phase 4 threshold placeholders are pinned in this ledger too: the atomic64 rollback gate still stays at posture `threshold_pending_until_runtime_atomic64_scope_widens` with pending status `pending_scope_widening` and placeholder `unapproved_until_runtime_atomic64_scope_widens`, while the bitmap rollback gate still stays at posture `threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks` with pending status `pending_bounded_benchmark` and placeholder `unapproved_until_bitmap_gate_grows_beyond_bounded_correctness_checks`, so the perf-baseline packet cannot silently blur those still-unapproved threshold claims back into generic prose.
- the current perf-baseline ownership split is explicit too: `scripts/zigux/validate-phase4.py` still owns the top-level `phase4_perf_baseline_manifest.json` lane, owner, rollback-owner, surveyed-gate, and survey-summary packet, while `zigux/tests/phase4_perf_baseline_survey.zig` remains the machine-checked owner for the deeper per-gate `pending_threshold_plans` rows and their isolated correctness-only replays `make -C zigux phase4-runtime-atomic64-diff` and `make -C zigux phase4-bitmap-diff`.
- `zigux/tests/phase4_perf_baseline_manifest.json` now also keeps one pending threshold-plan record per shipped rollback gate, pinning the current isolated correctness-only replay commands `make -C zigux phase4-runtime-atomic64-diff` and `make -C zigux phase4-bitmap-diff` alongside the still-unapproved benchmark-command and acceptable-limit placeholders for the atomic64 and bitmap gates.
- `samples/kprobes/Makefile` still keeps `obj-$(CONFIG_SAMPLE_KPROBES) += kprobe_example.o`, `samples/kprobes/kprobe_example.c` still anchors the current `kernel_clone` kprobe sample, and the shared `phase4_build.zig` bundle already runs `phase4-kprobe-example-survey-tests` from `zigux/tests/phase4_kprobe_example_survey.zig` against `zigux/tests/phase4_kprobe_example_manifest.json` while `samples/zigux/kprobe_example.zig` remains absent on `master`. The remaining same-family gap on this head is narrower than a prose-only absence check: the dedicated survey packet exists, but it still lacks its own local `make -C zigux phase4-kprobe-example-survey` wrapper and shared-validator ownership.
- the dedicated `scripts/zigux/check-phase4-gate-evidence.py` replay is now wired into `make -C zigux phase4-validate` beside the older validator subset, and this note now pins that checker file too, so review can prove both which survey surfaces were inspected and which checker implementation defined the broader blob-ledger contract on the inspected head.
- this note now also records the dedicated checker's own status tokens `PHASE4_GATE_EVIDENCE_SELF_TEST=pass`, `PHASE4_GATE_EVIDENCE_CHECK=pass`, and `PHASE4_GATE_EVIDENCE_TARGET_COUNT=15`, so the broader blob-ledger pass result is explicit evidence instead of living only in the surrounding narrative.
- `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` still expose the same Phase 4 rollback-readiness packet, and the dedicated checker means those three index surfaces are now part of the same fail-closed blob ledger instead of living only as summary guides under this note.

## Current Conclusion

The current Phase 4 rollback-ownership survey packet now has a refreshed exact-readback ledger: the matrix, validator, dedicated checker, Makefile, build, workflow, manifest, survey, and index surfaces named above all read back to the blob pins recorded in this note.

The packet still carries two validator-backed status layers as part of the published contract: the `validate-phase4.py` status bundle for the artifact-diff note, matrix, validator, dedicated checker, exact checker Makefile wiring, build, workflow, runtime atomic64 and bitmap replay surfaces, README hooks, survey files, and manifest-backed survey packet, and the `check-phase4-gate-evidence.py` status bundle for the broader survey-file plus index-surface blob ledger.

The shared validator does not currently own the deeper per-gate `pending_threshold_plans` rows inside `zigux/tests/phase4_perf_baseline_manifest.json`; that packet stays fail-closed through `zigux/tests/phase4_perf_baseline_survey.zig`, the isolated correctness-only replay commands it names, and this paired exact-readback note.

The shared validator still proves the workflow step names and the presence of `make -C zigux phase4-validate` plus `make -C zigux phase4-test`, and the dedicated runtime atomic64 survey now also keeps the published count tokens exact while the dedicated gate-evidence checker still fails closed on the exact single run-line counts for those two workflow commands.

On the inspected `master` head pinned by `PHASE4_WORKFLOW_BLOB_SHA=00bcad2fb5fe8fb71ca48807531ca7027e90517d`, the workflow currently contains one `make -C zigux phase4-validate` run line and one `make -C zigux phase4-test` run line under the Phase 4 steps, and that count now lives in both this exact-readback note and the dedicated checker contract.

That keeps the README surfaces truthful summaries for the packet, and this note is again a current blob ledger for the broader survey and index surfaces instead of a stale audit record.

The dedicated checker now also keeps the runtime atomic64 reversible-delivery sentence fail-closed in this note, so the rollback move, single replay body, and forward-path wording cannot silently drift back into prose-only guidance.

The current correctness-only anchors for the still-unapproved Phase 4 threshold plans remain `make -C zigux phase4-runtime-atomic64-diff` and `make -C zigux phase4-bitmap-diff`, so the packet still ties future perf-baseline work back to named isolated rollback replays instead of broad shared-bundle timing claims.

The remaining roadmap-backed gaps are still the same bounded ones:

- `samples/zigux/kprobe_example.zig` is still absent and still tied to `samples/kprobes/kprobe_example.c`, but current `master` no longer treats that roadmap row as matrix-only drift: the shared Phase 4 build already carries `phase4-kprobe-example-survey-tests` through `zigux/tests/phase4_kprobe_example_survey.zig` and `zigux/tests/phase4_kprobe_example_manifest.json`, so the remaining same-lane gap is the missing dedicated local wrapper and shared-validator promotion for that survey packet rather than the survey packet itself
- `samples/zigux/test_fsmount.zig` is still absent and remains C-anchor-only through the manifest-backed survey gate
- perf baselines and acceptable limits for the shipped `atomic64_diff.zig` and `bitmap_diff.zig` gates are still intentionally unapproved
