# Phase 4 Gate Evidence

This note records one exact readback snapshot for the current Phase 4 rollback-ownership and lab-matrix gate definitions.

## Status

- `PHASE4_EVIDENCE_DATE=2026-05-03`
- `PHASE4_EVIDENCE_MODE=github_connector_readback`
- `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`
- `PHASE4_VALIDATION_MATRIX_BLOB_SHA=6b6dd0597032ff5b61d50609e4a9af60459408d0`
- `PHASE4_VALIDATOR_BLOB_SHA=9f81ba776b76cb9b8941d538cda5edaca340e48f`
- `PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=d165dcf73fbab75c2c63802f412a0dce7b87a6af`
- `PHASE4_BUILD_BLOB_SHA=19472845adf51822a5775340c31aa3bd5db57a97`
- `PHASE4_MAKEFILE_BLOB_SHA=c6921b5ce12f60abbada4c5d8905b60b616701e5`
- `PHASE4_WORKFLOW_BLOB_SHA=00bcad2fb5fe8fb71ca48807531ca7027e90517d`
- `PHASE4_TEST_FSMOUNT_MANIFEST_BLOB_SHA=7171b6d3f3c407c708d56fd6bb275e2cba44add5`
- `PHASE4_TEST_FSMOUNT_SURVEY_BLOB_SHA=006f9c54cfa12c3029979f5256192465778790b6`
- `PHASE4_PERF_BASELINE_MANIFEST_BLOB_SHA=e66248e68cfa3a844b469ae83390b49f50fa57e7`
- `PHASE4_PERF_BASELINE_SURVEY_BLOB_SHA=4925d39bf888cdc80f3e25fff78bff9e0ea6c1ad`
- `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=0e077abb153279e91dad4a52ad89152092e287df`
- `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=7ccaa0c395eeaa8129249943f0752540b0c4ffa0`
- `PHASE4_DOC_README_BLOB_SHA=123baa93cc31d1033e8a4cca0675f28ec768f293`
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

- the exact blob pins above now match the live gate-definition files for this packet, including the refreshed `zigux/tests/phase4_build.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`, the three index-surface README blobs that the previous snapshot had drifted behind, and the refreshed matrix blob that now records the resolved 115-bit bitmap fill parity wording.
- the current shared surveyed snapshot `3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3` is still carried together by `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`, `zigux/tests/phase4_test_fsmount_survey.zig`, and `zigux/tests/phase4_perf_baseline_survey.zig`, and the sibling manifests for those three survey packets still keep the same `surveyed_commit` on the inspected head.
- the current workflow still keeps `Self-test Phase 4 validator` with `python3 scripts/zigux/validate-phase4.py --self-test` beside `Validate Phase 4 diff gates` and `Run Phase 4 diff tests`; on `PHASE4_WORKFLOW_BLOB_SHA=00bcad2fb5fe8fb71ca48807531ca7027e90517d` there is one `make -C zigux phase4-validate` run line and one `make -C zigux phase4-test` run line under the Phase 4 steps.
- the current `make -C zigux phase4-validate` route in `zigux/Makefile` still expands to `python3 scripts/zigux/artifact_diff.py --self-test`, `python3 scripts/zigux/check-artifact-diff-contract.py`, `python3 scripts/zigux/validate-phase4.py`, `python3 scripts/zigux/validate-phase4.py --self-test`, `python3 scripts/zigux/check-phase4-gate-evidence.py --self-test`, and `python3 scripts/zigux/check-phase4-gate-evidence.py`, so the self-test row, the external `check-artifact-diff-contract.py` row, the shared validator row, and the dedicated gate-evidence checker row remain the current published host-side preflight packet.
- the current `make -C zigux phase4-test` route still flows through `zigux/tests/phase4_build.zig` and currently replays `phase4-runtime-atomic64-diff-tests`, `phase4-runtime-atomic64-diff-survey-tests`, `phase4-test-fsmount-survey-tests`, `phase4-kprobe-example-survey-tests`, `phase4-perf-baseline-survey-tests`, and `phase4-bitmap-diff-tests`, so the two shipped Zig rollback gates plus the three survey-backed roadmap-gap packets remain on one shared replay surface.
- the current published validator contract for this packet still records `PHASE4_VALIDATOR_SELF_TEST=pass`, `PHASE4_VALIDATION=pass`, `PHASE4_REQUIRED_FILE_COUNT=23`, and `PHASE4_REQUIRED_MARKER_COUNT=236`, and the dedicated checker still records `PHASE4_GATE_EVIDENCE_SELF_TEST=pass`, `PHASE4_GATE_EVIDENCE_CHECK=pass`, and `PHASE4_GATE_EVIDENCE_TARGET_COUNT=15` for this broader blob-ledger packet.
- `Documentation/zigux/phase4-validation-matrix.md` still names the self-test row, the external `check-artifact-diff-contract.py` row, the `zigux/tests/atomic64_diff.zig` rollback row, the `zigux/tests/bitmap_diff.zig` rollback row, and the manifest-backed `phase4_test_fsmount_survey.zig`, `phase4_kprobe_example_survey.zig`, and `phase4_perf_baseline_survey.zig` survey rows with the current owners, rollback owners, workflow step names, local replay commands, reversible delivery evidence, and threshold posture strings, and the refreshed bitmap row now treats the 115-bit fill as resolved parity rather than an open survey-only mismatch.
- the runtime atomic64 reversible-delivery packet remains explicit on the inspected head: `lib/atomic64_test.c` stays the source of truth, removing `atomic64_diff.zig` from the shared `phase4_build.zig` entrypoint is the documented rollback move, `runtime_atomic64_diff.zig` remains the single replay body, and the existing Phase 9 runtime atomic64 starter remains the forward path.
- the current perf-baseline packet still carries one pending threshold-plan record per shipped rollback gate, pinning `make -C zigux phase4-runtime-atomic64-diff` and `make -C zigux phase4-bitmap-diff` beside the still-unapproved benchmark-command and acceptable-limit placeholders, so the benchmark command and acceptable limit remain intentionally unapproved rather than implied.
- `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` still expose the same Phase 4 rollback-readiness packet, including the `phase4-test-fsmount-survey` and `phase4-perf-baseline-survey` local replay routes, the `phase4-runtime-atomic64-diff-survey-tests`, `phase4-test-fsmount-survey-tests`, and `phase4-perf-baseline-survey-tests` shared build entries, the dedicated `check-phase4-gate-evidence.py` checker, and the current `perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land` posture.
- the current shared build already carries the separate `phase4-kprobe-example-survey-tests` packet too, but that roadmap row still remains a shared-build-backed survey follow-up rather than a validator-owned packet because `samples/zigux/kprobe_example.zig` is still absent on `master` and there is still no dedicated `make -C zigux phase4-kprobe-example-survey` wrapper.

## Current Conclusion

The current Phase 4 rollback-ownership and lab-matrix packet is again pinned to the live published head: the matrix, validator, dedicated checker, Makefile, workflow, two shipped rollback gates, the three manifest-backed survey packets, and the three index surfaces named above now match the exact blob ledger recorded in this note.

The remaining roadmap-backed gaps are still the same bounded ones:

- `samples/zigux/kprobe_example.zig` is still absent, while the shared build-backed survey packet exists and still needs its dedicated local wrapper plus validator-owned promotion.
- `samples/zigux/test_fsmount.zig` is still absent and remains C-anchor-only through `make M=samples/vfs` and `c_anchor_only_until_test_fsmount_starter_lands`.
- perf baselines and acceptable limits for `zigux/tests/atomic64_diff.zig` and `zigux/tests/bitmap_diff.zig` are still intentionally unapproved.
