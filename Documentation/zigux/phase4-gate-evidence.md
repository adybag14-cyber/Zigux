# Phase 4 Gate Evidence

This note records one exact readback snapshot for the current Phase 4 rollback-ownership and lab-matrix gate definitions.

## Status

- `PHASE4_EVIDENCE_DATE=2026-05-04`
- `PHASE4_EVIDENCE_MODE=github_connector_readback`
- `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`
- `PHASE4_EXACT_READBACK_HEAD=0bd402fd6ca83ba2ace6b21e9e57459401b631cd`
- `PHASE4_SHARED_SURVEYED_COMMIT=3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3`
- `PHASE4_VALIDATION_MATRIX_BLOB_SHA=c45ed15ed3ac3760a6ceeeb080142a970a24ce22`
- `PHASE4_VALIDATOR_BLOB_SHA=00f9d3b13c4e92ffda62acf281bae39bb937f81e`
- `PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=894870c121bbea321bf29bbeaf236d99edf7f896`
- `PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=60d250d7de47f92fc795c8905d182bbeb9c357fa`
- `PHASE4_BUILD_BLOB_SHA=19472845adf51822a5775340c31aa3bd5db57a97`
- `PHASE4_MAKEFILE_BLOB_SHA=122517d6b90f85de696483cf4aef71091d433dfd`
- `PHASE4_WORKFLOW_BLOB_SHA=c414dcfb17ef3683424fd44f650c57b29804021e`
- `PHASE4_KPROBE_EXAMPLE_MANIFEST_BLOB_SHA=1ba9fcaa0da2459c4c5e3034595ff991072c885d`
- `PHASE4_KPROBE_EXAMPLE_SURVEY_BLOB_SHA=a4dba25ebde32eb1702e3405e35c8dc71a33c353`
- `PHASE4_TEST_FSMOUNT_MANIFEST_BLOB_SHA=7171b6d3f3c407c708d56fd6bb275e2cba44add5`
- `PHASE4_TEST_FSMOUNT_SURVEY_BLOB_SHA=006f9c54cfa12c3029979f5256192465778790b6`
- `PHASE4_PERF_BASELINE_MANIFEST_BLOB_SHA=013b01cd94a378ecf9640ef2ebbd7de549c6d319`
- `PHASE4_PERF_BASELINE_SURVEY_BLOB_SHA=83a233e861c66d9816ca4504917227c00513ee79`
- `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=fda077b24419830be10c879590154e916e899ddf`
- `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=c7abc1f7605bdb356baef1d998230371f3d0997f`
- `PHASE4_DOC_README_BLOB_SHA=381582ffe194581b74e72ac46afd69be346c2b6b`
- `PHASE4_SCRIPT_README_BLOB_SHA=aba38d52d0497483c4b32dd26b6bcbe374600638`
- `PHASE4_TESTS_README_BLOB_SHA=35187964728f61a7c667353b7d249914157f205c`
- `PHASE4_VALIDATOR_SELF_TEST=pass`
- `PHASE4_VALIDATION=pass`
- `PHASE4_REQUIRED_FILE_COUNT=27`
- `PHASE4_REQUIRED_MARKER_COUNT=64`
- `PHASE4_GATE_EVIDENCE_SELF_TEST=pass`
- `PHASE4_GATE_EVIDENCE_CHECK=pass`
- `PHASE4_GATE_EVIDENCE_TARGET_COUNT=18`
- `PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST=pass`
- `PHASE4_WORKFLOW_ROUTE_COUNTS=pass`
- `PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_FILE_COUNT=5`
- `PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_CHECK_COUNT=36`
- `ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass`
- `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=9`
- `ARTIFACT_DIFF_CONTRACT=pass`
- `ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=23`
- `ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=4`
- `ARTIFACT_DIFF_CONTRACT_CASE_COUNT=27`

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

- the exact blob pins above now match the live gate-definition files for this packet, including the refreshed `Documentation/zigux/phase4-validation-matrix.md`, `.github/workflows/zigux-bootstrap.yml`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`, plus the stable validator, dedicated gate-evidence checker, dedicated workflow-route checker, `phase4_build.zig`, `phase4_kprobe_example_{manifest,survey}`, `phase4_test_fsmount_{manifest,survey}`, and `phase4_runtime_atomic64_diff_manifest.json` surfaces.
- the last recorded inspected head for this note is now `0bd402fd6ca83ba2ace6b21e9e57459401b631cd`, which is the latest visible `master` commit at readback time on the public commit history during this connector rerun. The rerun refreshed the live `scripts/zigux/README.md` blob pin and the dedicated gate-evidence checker blob pin while confirming that the shared Phase 4 validator still lives at `PHASE4_VALIDATOR_BLOB_SHA=00f9d3b13c4e92ffda62acf281bae39bb937f81e`, the dedicated gate-evidence checker now lives at `PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=894870c121bbea321bf29bbeaf236d99edf7f896`, the dedicated workflow-route checker still lives at `PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=60d250d7de47f92fc795c8905d182bbeb9c357fa`, and the docs-root, tests-root, perf-baseline-manifest, perf-baseline-survey, and runtime-atomic64-survey blob pins remained aligned; the shared survey provenance still carried by `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`, `zigux/tests/phase4_kprobe_example_survey.zig`, `zigux/tests/phase4_test_fsmount_survey.zig`, and `zigux/tests/phase4_perf_baseline_survey.zig`, and their sibling manifests remains `3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3`.
- the current workflow still keeps `Self-test Phase 4 validator` with `python3 scripts/zigux/validate-phase4.py --self-test` beside `Validate Phase 4 diff gates` and `Run Phase 4 diff tests`; on `PHASE4_WORKFLOW_BLOB_SHA=c414dcfb17ef3683424fd44f650c57b29804021e` there is one `make -C zigux phase4-validate` run line and one `make -C zigux phase4-test` run line under the Phase 4 steps.
- the current `make -C zigux phase4-validate` route in `zigux/Makefile` still expands to `python3 scripts/zigux/artifact_diff.py --self-test`, `python3 scripts/zigux/check-artifact-diff-contract.py`, `python3 scripts/zigux/check-phase4-kprobe-example-packet.py --self-test`, `python3 scripts/zigux/check-phase4-kprobe-example-packet.py`, `python3 scripts/zigux/check-phase4-workflow-route-counts.py --self-test`, `python3 scripts/zigux/check-phase4-workflow-route-counts.py`, `python3 scripts/zigux/validate-phase4.py`, `python3 scripts/zigux/validate-phase4.py --self-test`, `python3 scripts/zigux/check-phase4-gate-evidence.py --self-test`, and `python3 scripts/zigux/check-phase4-gate-evidence.py`, so the external `check-artifact-diff-contract.py` row, the dedicated kprobe packet checker, the dedicated workflow-route checker, the shared validator row, and the dedicated gate-evidence checker row remain the current published host-side preflight packet.
- the current `make -C zigux phase4-test` route still flows through `zigux/tests/phase4_build.zig` and currently replays `phase4-runtime-atomic64-diff-tests`, `phase4-runtime-atomic64-diff-survey-tests`, `phase4-test-fsmount-survey-tests`, `phase4-kprobe-example-survey-tests`, `phase4-perf-baseline-survey-tests`, and `phase4-bitmap-diff-tests`, so the two shipped Zig rollback gates plus the shared-build-backed survey packets remain on one shared replay surface.
- the current published validator contract for this packet now records `PHASE4_VALIDATOR_SELF_TEST=pass`, `PHASE4_VALIDATION=pass`, `PHASE4_REQUIRED_FILE_COUNT=27`, and `PHASE4_REQUIRED_MARKER_COUNT=64`, the dedicated gate-evidence checker records `PHASE4_GATE_EVIDENCE_SELF_TEST=pass`, `PHASE4_GATE_EVIDENCE_CHECK=pass`, and `PHASE4_GATE_EVIDENCE_TARGET_COUNT=18`, the dedicated workflow-route checker records `PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST=pass`, `PHASE4_WORKFLOW_ROUTE_COUNTS=pass`, `PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_FILE_COUNT=5`, and `PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_CHECK_COUNT=36`, and the published artifact-diff contract checker now records `ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass`, `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=9`, `ARTIFACT_DIFF_CONTRACT=pass`, `ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=23`, `ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=4`, and `ARTIFACT_DIFF_CONTRACT_CASE_COUNT=27` for this exact blob-ledger packet. The shared validator now also fails closed if the Phase 4 matrix drops the bitmap row's zero-nbits no-op checkpoint or its zero-length range-edit checkpoint, if this exact-readback note drops the resolved 115-bit fill parity sentence, if this exact-readback note drops or duplicates the dedicated `PHASE4_GATE_EVIDENCE_TARGET_COUNT=18` status line or drops or duplicates the note that the narrower gate-evidence-checker-enforced blob target set includes the dedicated workflow-route checker file itself, if the exact-readback note drops or drifts the dedicated `PHASE4_VALIDATION_MATRIX_BLOB_SHA`, `PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA`, `PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA`, `PHASE4_TEST_FSMOUNT_MANIFEST_BLOB_SHA`, `PHASE4_PERF_BASELINE_MANIFEST_BLOB_SHA`, or `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA` pins, if `scripts/zigux/README.md` loses or duplicates the direct `make -C zigux phase4-bitmap-diff` replay route or the paired shared-build `phase4-bitmap-diff-tests` marker that the restored Phase 4 scripts-root summary now carries exactly once, or if `zigux/tests/phase4_perf_baseline_manifest.json` drops either shipped gate's threshold posture, isolated correctness replay, threshold-ready surface, concrete next-threshold-step note, or why-not-approved-yet note, while `PHASE4_GATE_EVIDENCE_TARGET_COUNT=18` still describes the narrower gate-evidence-checker-enforced blob set that includes the dedicated workflow-route checker file itself rather than the broader exact-readback contract carried by `scripts/zigux/validate-phase4.py`.
- `Documentation/zigux/phase4-validation-matrix.md` still names the self-test row, the external `check-artifact-diff-contract.py` row, the `zigux/tests/atomic64_diff.zig` rollback row, the `zigux/tests/bitmap_diff.zig` rollback row, and the manifest-backed `phase4_test_fsmount_survey.zig`, `phase4_kprobe_example_survey.zig`, and `phase4_perf_baseline_survey.zig` survey rows with the current owners, rollback owners, workflow step names, local replay commands, reversible delivery evidence, and threshold posture strings, and the refreshed bitmap row still treats the 115-bit fill as resolved parity rather than an open survey-only mismatch. The shared perf-baseline row now also carries the same threshold-ready surfaces and exact next threshold steps that the live `phase4_perf_baseline_manifest.json` already records for the atomic64 and bitmap gates.
- the runtime atomic64 reversible-delivery packet remains explicit on the inspected head: `lib/atomic64_test.c` stays the source of truth, removing `atomic64_diff.zig` from the shared `phase4_build.zig` entrypoint is the documented rollback move, `runtime_atomic64_diff.zig` remains the single replay body, and the existing Phase 9 runtime atomic64 starter remains the forward path.
- the current perf-baseline packet still carries one pending threshold-plan record per shipped rollback gate, and the refreshed manifest now also pins one concrete threshold-ready surface plus one exact next threshold step per gate: `zigux/tests/runtime_atomic64_diff.zig` keeps the explicit post-selftest replay for the atomic64 plan and now records the still-required broader benchmark entrypoint handoff for ABI and Runtime Team, while `zigux/tests/bitmap_diff.zig` keeps `runThresholdReplay()` as the deterministic bitmap batch and now records the already-landed isolated `zig build phase4-bitmap-bench --build-file zigux/tests/phase4_build.zig` route plus the still-required benchmark-command and acceptable-limit approval for Shared Subsystems Pod. The packet still pins `make -C zigux phase4-runtime-atomic64-diff` beside the still-unapproved benchmark-command and acceptable-limit placeholders, and the broader validator now mirrors that richer manifest contract directly instead of checking only the old lane key, so threshold approval remains tied to live replay-ready code and named next actions instead of placeholder prose alone.
- `Documentation/zigux/README.md` still keeps the current Phase 4 rollback-readiness packet visible from the docs root, including the dedicated `make -C zigux phase4-runtime-atomic64-diff`, `phase4-kprobe-example-survey`, `phase4-test-fsmount-survey`, and `phase4-perf-baseline-survey` local replay routes, the shared `phase4-runtime-atomic64-diff-tests`, `phase4-runtime-atomic64-diff-survey-tests`, `phase4-kprobe-example-survey-tests`, `phase4-test-fsmount-survey-tests`, and `phase4-perf-baseline-survey-tests` build entries, the dedicated `check-phase4-gate-evidence.py` checker, the dedicated `check-phase4-workflow-route-counts.py` checker, and the current `perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land` posture, while the isolated bitmap gate remains explicit elsewhere in the same packet through `zigux/tests/bitmap_diff.zig`, `Documentation/zigux/phase4-validation-matrix.md`, `zigux/tests/phase4_build.zig`, `zigux/Makefile`, and this exact-readback note.
- `zigux/tests/README.md` now exposes the kprobe survey packet directly: it names `zigux/tests/phase4_kprobe_example_manifest.json`, `zigux/tests/phase4_kprobe_example_survey.zig`, the dedicated `make -C zigux phase4-kprobe-example-survey` replay, the shared `phase4-kprobe-example-survey-tests` entry, and the current `c_anchor_only_until_kprobe_example_starter_lands` survey posture beside the existing test_fsmount and perf-baseline survey routes.
- `scripts/zigux/README.md` now carries a dedicated Phase 4 summary line, so the shared validator, the dedicated gate-evidence checker, the dedicated `check-phase4-kprobe-example-packet.py` checker, the dedicated `check-phase4-workflow-route-counts.py` checker, the `phase4-runtime-atomic64-diff`, `phase4-bitmap-diff`, `phase4-kprobe-example-survey`, `phase4-test-fsmount-survey`, and `phase4-perf-baseline-survey` local replays, and the shared build entries `phase4-runtime-atomic64-diff-tests`, `phase4-runtime-atomic64-diff-survey-tests`, `phase4-bitmap-diff-tests`, `phase4-kprobe-example-survey-tests`, `phase4-test-fsmount-survey-tests`, and `phase4-perf-baseline-survey-tests` remain reviewable directly from the scripts root beside `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/Makefile`, `Documentation/zigux/phase4-validation-matrix.md`, and this exact-readback note.
- the shared validator and `scripts/zigux/check-phase4-gate-evidence.py` now both exact-count the scripts-root `make -C zigux phase4-bitmap-diff` route and the paired `phase4-bitmap-diff-tests` shared-build marker, so the restored scripts-root bitmap surface cannot drift behind broader Phase 4 prose in this exact-readback packet.
- the current shared build still carries the separate `phase4-kprobe-example-survey-tests` packet too, and this exact blob ledger now pins that shared-build-backed survey follow-up through `zigux/tests/phase4_kprobe_example_manifest.json` plus `zigux/tests/phase4_kprobe_example_survey.zig`; the dedicated `make -C zigux phase4-kprobe-example-survey` wrapper remains part of the published local replay surface, and the refreshed gate-evidence checker now keeps the now-landed note that the shared validator fails closed on the kprobe survey packet explicit in this exact-readback packet.

## Current Conclusion

The current Phase 4 rollback-ownership and lab-matrix packet remains reviewable on live `master` for the gate-definition files enumerated above: the matrix, validator, dedicated gate-evidence checker, dedicated workflow-route checker, Makefile, workflow, the two shipped rollback gates, the four exact blob-ledger survey packets, and the three index surfaces named above still match the exact blob ledger recorded in this note, the docs-root summary and the restored scripts-root summary now both match the isolated runtime atomic64 and bitmap wording carried elsewhere in the same packet, and the isolated bitmap gate remains explicit through the shared build, Makefile, matrix, validator, scripts root, and exact-readback packet.

The shared survey provenance inside the four Phase 4 survey packets still reflects `3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3`, so this note now distinguishes the latest inspected head from the older shared survey snapshot instead of implying they are the same commit.

The separate `PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA` pin above therefore remains part of the shared validator's exact-readback contract for the dedicated workflow-route checker file itself, and the broader validator now exact-counts the dedicated `PHASE4_GATE_EVIDENCE_TARGET_COUNT=18` status line and the narrower-set note that explains why that smaller gate-evidence blob set includes the dedicated workflow-route checker file itself. It now also mirrors the richer perf-baseline manifest contract directly, so both threshold-ready surfaces, both isolated correctness replays, and both concrete next-threshold-step notes stay fail-closed alongside the existing workflow, bitmap, and blob-pin checks. The tightened checker still exact-counts the scripts-root `make -C zigux phase4-bitmap-diff` route plus the paired `phase4-bitmap-diff-tests` shared-build marker in addition to the earlier workflow and Makefile markers, while `PHASE4_GATE_EVIDENCE_TARGET_COUNT=18` continues to describe the narrower gate-evidence-checker-enforced blob target set, which now includes the dedicated workflow-route checker file itself.

The remaining roadmap-backed gaps are still the same bounded ones:

- `samples/zigux/kprobe_example.zig` is still absent, while the shared-build-backed survey packet remains reviewable through `make -C zigux phase4-kprobe-example-survey`, `phase4-kprobe-example-survey-tests`, the shared `scripts/zigux/validate-phase4.py` contract, and the exact blob-ledger evidence recorded above.
- `samples/zigux/test_fsmount.zig` is still absent and remains C-anchor-only through `make M=samples/vfs` and `c_anchor_only_until_test_fsmount_starter_lands`.
- perf baselines and acceptable limits for `zigux/tests/atomic64_diff.zig` and `zigux/tests/bitmap_diff.zig` are still intentionally unapproved.
