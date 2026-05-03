# Phase 4 Gate Evidence

This note records one exact readback snapshot for the current Phase 4 rollback-ownership and lab-matrix gate definitions.

## Status

- `PHASE4_EVIDENCE_DATE=2026-05-03`
- `PHASE4_EVIDENCE_MODE=github_connector_readback`
- `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`
- `PHASE4_VALIDATION_MATRIX_BLOB_SHA=6b6dd0597032ff5b61d50609e4a9af60459408d0`
- `PHASE4_VALIDATOR_BLOB_SHA=9f81ba776b76cb9b8941d538cda5edaca340e48f`
- `PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=ed6e2c9afb2fc2dc942a309ec80b2e1ba913b492`
- `PHASE4_BUILD_BLOB_SHA=19472845adf51822a5775340c31aa3bd5db57a97`
- `PHASE4_MAKEFILE_BLOB_SHA=892f7bf31bcf73426eac4d3720f2e6b274345c18`
- `PHASE4_WORKFLOW_BLOB_SHA=eededc3f3767ab67656fd4444689e907e6dae172`
- `PHASE4_KPROBE_EXAMPLE_MANIFEST_BLOB_SHA=5b811166ce295cebf49ed0ae2df7b9e4d852c9fd`
- `PHASE4_KPROBE_EXAMPLE_SURVEY_BLOB_SHA=6cf535d0e870137ce717adb579c2cf8d406fd6dc`
- `PHASE4_TEST_FSMOUNT_MANIFEST_BLOB_SHA=7171b6d3f3c407c708d56fd6bb275e2cba44add5`
- `PHASE4_TEST_FSMOUNT_SURVEY_BLOB_SHA=006f9c54cfa12c3029979f5256192465778790b6`
- `PHASE4_PERF_BASELINE_MANIFEST_BLOB_SHA=e66248e68cfa3a844b469ae83390b49f50fa57e7`
- `PHASE4_PERF_BASELINE_SURVEY_BLOB_SHA=4925d39bf888cdc80f3e25fff78bff9e0ea6c1ad`
- `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=2a001ec217dc3acc6d77c08a66707346a950f353`
- `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=b67bec3a6db84cc8123f3a8703d63a63c08ed179`
- `PHASE4_DOC_README_BLOB_SHA=7073dc90aeab1d92d481a38c7a93723caa445cdc`
- `PHASE4_SCRIPT_README_BLOB_SHA=80f7925c2493581dc96b59d34baa3fe4ac5e7e3c`
- `PHASE4_TESTS_README_BLOB_SHA=1dad99ae3829530c720437a65759a5f88088e4ab`
- `PHASE4_VALIDATOR_SELF_TEST=pass`
- `PHASE4_VALIDATION=pass`
- `PHASE4_REQUIRED_FILE_COUNT=23`
- `PHASE4_REQUIRED_MARKER_COUNT=236`
- `PHASE4_GATE_EVIDENCE_SELF_TEST=pass`
- `PHASE4_GATE_EVIDENCE_CHECK=pass`
- `PHASE4_GATE_EVIDENCE_TARGET_COUNT=17`

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

- the exact blob pins above now match the live gate-definition files for this packet, including the refreshed `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`, plus the stable matrix, validator, dedicated checker, `phase4_build.zig`, `phase4_kprobe_example_{manifest,survey}`, `phase4_test_fsmount_{manifest,survey}`, and `phase4_perf_baseline_{manifest,survey}` surfaces.
- the current shared surveyed snapshot `3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3` is still carried together by `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`, `zigux/tests/phase4_kprobe_example_survey.zig`, `zigux/tests/phase4_test_fsmount_survey.zig`, and `zigux/tests/phase4_perf_baseline_survey.zig`, and the sibling manifests for those four survey packets still keep the same `surveyed_commit` on the inspected head.
- the current workflow still keeps `Self-test Phase 4 validator` with `python3 scripts/zigux/validate-phase4.py --self-test` beside `Validate Phase 4 diff gates` and `Run Phase 4 diff tests`; on `PHASE4_WORKFLOW_BLOB_SHA=eededc3f3767ab67656fd4444689e907e6dae172` there is one `make -C zigux phase4-validate` run line and one `make -C zigux phase4-test` run line under the Phase 4 steps.
- the current `make -C zigux phase4-validate` route in `zigux/Makefile` still expands to `python3 scripts/zigux/artifact_diff.py --self-test`, `python3 scripts/zigux/check-artifact-diff-contract.py`, `python3 scripts/zigux/validate-phase4.py`, `python3 scripts/zigux/validate-phase4.py --self-test`, `python3 scripts/zigux/check-phase4-gate-evidence.py --self-test`, and `python3 scripts/zigux/check-phase4-gate-evidence.py`, so the self-test row, the external `check-artifact-diff-contract.py` row, the shared validator row, and the dedicated gate-evidence checker row remain the current published host-side preflight packet.
- the current `make -C zigux phase4-test` route still flows through `zigux/tests/phase4_build.zig` and currently replays `phase4-runtime-atomic64-diff-tests`, `phase4-runtime-atomic64-diff-survey-tests`, `phase4-test-fsmount-survey-tests`, `phase4-kprobe-example-survey-tests`, `phase4-perf-baseline-survey-tests`, and `phase4-bitmap-diff-tests`, so the two shipped Zig rollback gates plus the shared-build-backed survey packets remain on one shared replay surface.
- the current published validator contract for this packet still records `PHASE4_VALIDATOR_SELF_TEST=pass`, `PHASE4_VALIDATION=pass`, `PHASE4_REQUIRED_FILE_COUNT=23`, and `PHASE4_REQUIRED_MARKER_COUNT=236`, and the dedicated checker now records `PHASE4_GATE_EVIDENCE_SELF_TEST=pass`, `PHASE4_GATE_EVIDENCE_CHECK=pass`, and `PHASE4_GATE_EVIDENCE_TARGET_COUNT=17` for this exact blob-ledger packet now that the kprobe survey manifest and survey source are pinned alongside the older evidence targets.
- `Documentation/zigux/phase4-validation-matrix.md` still names the self-test row, the external `check-artifact-diff-contract.py` row, the `zigux/tests/atomic64_diff.zig` rollback row, the `zigux/tests/bitmap_diff.zig` rollback row, and the manifest-backed `phase4_test_fsmount_survey.zig`, `phase4_kprobe_example_survey.zig`, and `phase4_perf_baseline_survey.zig` survey rows with the current owners, rollback owners, workflow step names, local replay commands, reversible delivery evidence, and threshold posture strings, and the refreshed bitmap row still treats the 115-bit fill as resolved parity rather than an open survey-only mismatch.
- the runtime atomic64 reversible-delivery packet remains explicit on the inspected head: `lib/atomic64_test.c` stays the source of truth, removing `atomic64_diff.zig` from the shared `phase4_build.zig` entrypoint is the documented rollback move, `runtime_atomic64_diff.zig` remains the single replay body, and the existing Phase 9 runtime atomic64 starter remains the forward path.
- the current perf-baseline packet still carries one pending threshold-plan record per shipped rollback gate, pinning `make -C zigux phase4-runtime-atomic64-diff` and `make -C zigux phase4-bitmap-diff` beside the still-unapproved benchmark-command and acceptable-limit placeholders, so the benchmark command and acceptable limit remain intentionally unapproved rather than implied.
- `Documentation/zigux/README.md` still exposes the full current Phase 4 rollback-readiness packet, including the `phase4-kprobe-example-survey`, `phase4-test-fsmount-survey`, and `phase4-perf-baseline-survey` local replay routes, the `phase4-runtime-atomic64-diff-survey-tests`, `phase4-kprobe-example-survey-tests`, `phase4-test-fsmount-survey-tests`, and `phase4-perf-baseline-survey-tests` shared build entries, the dedicated `check-phase4-gate-evidence.py` checker, and the current `perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land` posture.
- `zigux/tests/README.md` now exposes the kprobe survey packet directly: it names `zigux/tests/phase4_kprobe_example_manifest.json`, `zigux/tests/phase4_kprobe_example_survey.zig`, the dedicated `make -C zigux phase4-kprobe-example-survey` replay, the shared `phase4-kprobe-example-survey-tests` entry, and the current `c_anchor_only_until_kprobe_example_starter_lands` survey posture beside the existing test_fsmount and perf-baseline survey routes.
- `scripts/zigux/README.md` still exposes the narrower older Phase 4 index packet: it names the shared validator, the dedicated gate-evidence checker, the `phase4-test-fsmount-survey` and `phase4-perf-baseline-survey` local replays, and the `phase4-runtime-atomic64-diff-survey-tests`, `phase4-test-fsmount-survey-tests`, and `phase4-perf-baseline-survey-tests` shared-build entries, but it does not yet name the dedicated `phase4-kprobe-example-survey` local replay route or the `phase4-kprobe-example-survey-tests` shared-build entry.
- the current shared build still carries the separate `phase4-kprobe-example-survey-tests` packet too, and this exact blob ledger now pins that shared-build-backed survey follow-up through `zigux/tests/phase4_kprobe_example_manifest.json` plus `zigux/tests/phase4_kprobe_example_survey.zig`; the dedicated `make -C zigux phase4-kprobe-example-survey` wrapper is now part of the published local replay surface even though the shared validator still does not fail closed on the kprobe survey packet itself.

## Current Conclusion

The current Phase 4 rollback-ownership and lab-matrix packet is again pinned to the live published head: the matrix, validator, dedicated checker, Makefile, workflow, the two shipped rollback gates, the four exact blob-ledger survey packets, and the three index surfaces named above now match the exact blob ledger recorded in this note, with the tests-root Phase 4 index now carrying the full kprobe survey packet while the narrower scripts-root index is called out explicitly as the remaining local replay undercount.

The remaining roadmap-backed gaps are still the same bounded ones:

- `samples/zigux/kprobe_example.zig` is still absent, while the shared-build-backed survey packet remains reviewable through `make -C zigux phase4-kprobe-example-survey`, `phase4-kprobe-example-survey-tests`, and the exact blob-ledger evidence recorded above; the shared validator still does not fail closed on the kprobe survey packet itself, `zigux/tests/README.md` now names that dedicated replay surface, and `scripts/zigux/README.md` still does not.
- `samples/zigux/test_fsmount.zig` is still absent and remains C-anchor-only through `make M=samples/vfs` and `c_anchor_only_until_test_fsmount_starter_lands`.
- perf baselines and acceptable limits for `zigux/tests/atomic64_diff.zig` and `zigux/tests/bitmap_diff.zig` are still intentionally unapproved.
