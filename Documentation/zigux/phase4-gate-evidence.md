# Phase 4 Gate Evidence
This note records one exact readback snapshot for the current Phase 4 rollback-ownership and lab-matrix gate definitions.

## Status
- `PHASE4_EVIDENCE_DATE=2026-05-05`
- `PHASE4_EVIDENCE_MODE=github_connector_readback`
- `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`
- `PHASE4_EXACT_READBACK_HEAD=02264a3240cd30ce45c9a932047a0204b7ab5029`
- `PHASE4_SHARED_SURVEYED_COMMIT=3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3`
- `PHASE4_VALIDATION_MATRIX_BLOB_SHA=b34b22098ffdade718339b161e788656790e183f`
- `PHASE4_VALIDATOR_BLOB_SHA=41641580db76968f1afb217dd2d0c28fc5e2d777`
- `PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=f20b566bb6cc39b366c7eb4e28929b9e414234e3`
- `PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=273c7fedf6cb9968cc4288a0c0505cd79bb81d5f`
- `PHASE4_BUILD_BLOB_SHA=0561c4e4359f9ab37dcd995e5944c4458fc0c3c3`
- `PHASE4_MAKEFILE_BLOB_SHA=4bf01277fc7428fcdad7596de692e1096c63ec18`
- `PHASE4_WORKFLOW_BLOB_SHA=f884c658db081e41443ccc738bd4df6f0d349cb8`
- `PHASE4_KPROBE_EXAMPLE_MANIFEST_BLOB_SHA=1ba9fcaa0da2459c4c5e3034595ff991072c885d`
- `PHASE4_KPROBE_EXAMPLE_SURVEY_BLOB_SHA=a4dba25ebde32eb1702e3405e35c8dc71a33c353`
- `PHASE4_TEST_FSMOUNT_MANIFEST_BLOB_SHA=7171b6d3f3c407c708d56fd6bb275e2cba44add5`
- `PHASE4_TEST_FSMOUNT_SURVEY_BLOB_SHA=006f9c54cfa12c3029979f5256192465778790b6`
- `PHASE4_PERF_BASELINE_MANIFEST_BLOB_SHA=013b01cd94a378ecf9640ef2ebbd7de549c6d319`
- `PHASE4_PERF_BASELINE_SURVEY_BLOB_SHA=83a233e861c66d9816ca4504917227c00513ee79`
- `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=ae52459716b344bfa776d78a72826b3b672f7a9e`
- `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=deb5566a0b31d9d38e3b2913162fc2a066d03c60`
- `PHASE4_DOC_README_BLOB_SHA=4b64e678afa1473a044458b6d035336b56292e05`
- `PHASE4_SCRIPT_README_BLOB_SHA=fbf3023cc7d04b910384dcc9c3c639e795833a6d`
- `PHASE4_TESTS_README_BLOB_SHA=b17c87a8adea37d2a53c742fc9545debc0a78d31`
- `PHASE4_VALIDATOR_SELF_TEST=pass`
- `PHASE4_VALIDATION=pass`
- `PHASE4_REQUIRED_FILE_COUNT=27`
- `PHASE4_REQUIRED_MARKER_COUNT=92`
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

## Exact Readback Evidence
- The shared surveyed snapshot stays explicit at `3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3` across `phase4_runtime_atomic64_diff_survey.zig`, `phase4_kprobe_example_survey.zig`, `phase4_test_fsmount_survey.zig`, and `phase4_perf_baseline_survey.zig`.
- The current workflow packet still keeps `Self-test Phase 4 validator` with `python3 scripts/zigux/validate-phase4.py --self-test` beside `Validate Phase 4 diff gates` and `Run Phase 4 diff tests`.
- On the current workflow there is one `make -C zigux phase4-validate` run line and one `make -C zigux phase4-test` run line under the Phase 4 steps, so the dedicated route-count checker and this note keep the validator-first and replay hooks exact-counted together.
- The current published validator contract stays explicit here too: `PHASE4_VALIDATOR_SELF_TEST=pass`, `PHASE4_VALIDATION=pass`, `PHASE4_REQUIRED_FILE_COUNT=27`, and `PHASE4_REQUIRED_MARKER_COUNT=92` remain the current shared-validator status lines for this packet.
- The current route-count packet stays explicit here too: `PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST=pass`, `PHASE4_WORKFLOW_ROUTE_COUNTS=pass`, `PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_FILE_COUNT=5`, and `PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_CHECK_COUNT=36` remain the dedicated workflow-route status lines for this packet.
- The current artifact-diff contract packet stays explicit here too: `ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass`, `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=9`, `ARTIFACT_DIFF_CONTRACT=pass`, `ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=23`, `ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=4`, and `ARTIFACT_DIFF_CONTRACT_CASE_COUNT=27` remain visible in the exact-readback ledger instead of being left implicit behind the external checker row.
- The runtime atomic64 reversible-delivery packet stays explicit: `lib/atomic64_test.c` stays the source of truth, removing `atomic64_diff.zig` from the shared `phase4_build.zig` entrypoint is the documented rollback move, `runtime_atomic64_diff.zig` remains the single replay body, and the existing Phase 9 runtime atomic64 starter remains the forward path.
- The same packet still names `make -C zigux phase4-runtime-atomic64-diff`, `phase4-runtime-atomic64-diff-tests`, and `phase4-runtime-atomic64-diff-survey-tests` as the focused and shared replay surfaces.
- The current perf-baseline packet still carries one pending threshold-plan record per shipped rollback gate and pins `make -C zigux phase4-runtime-atomic64-diff` and `make -C zigux phase4-bitmap-diff` beside the still-unapproved benchmark-command and acceptable-limit placeholders.
- The refreshed bitmap row still treats the 115-bit fill as resolved parity rather than an open survey-only mismatch, and the isolated `zig build phase4-bitmap-bench --build-file zigux/tests/phase4_build.zig` route remains the current benchmark-ready path while threshold approval stays intentionally pending.
- The shared validator and `scripts/zigux/check-phase4-gate-evidence.py` now both exact-count the scripts-root `make -C zigux phase4-bitmap-diff` route and the paired `phase4-bitmap-diff-tests` shared-build marker so the restored scripts-root bitmap surface cannot drift behind broader Phase 4 prose.
- The validation-matrix and runtime atomic64 survey packet also stay explicit here now: `PHASE4_VALIDATION_MATRIX_BLOB_SHA=b34b22098ffdade718339b161e788656790e183f`, `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=ae52459716b344bfa776d78a72826b3b672f7a9e`, and `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=deb5566a0b31d9d38e3b2913162fc2a066d03c60` match the currently shipped matrix plus the wrapper-backed runtime atomic64 manifest and survey packet that the same exact-readback note already names.
- The kprobe survey packet remains explicit through `make -C zigux phase4-kprobe-example-survey`, `phase4-kprobe-example-survey-tests`, and the now-landed note that the shared validator now fails closed on the kprobe survey packet itself.
- `PHASE4_GATE_EVIDENCE_TARGET_COUNT=18` continues to describe the narrower gate-evidence-checker-enforced blob target set, which includes the dedicated workflow-route checker file itself.

## Current Conclusion
- The current Phase 4 exact-readback packet is refreshed to the live connector-read blob set for the shared validator, dedicated gate-evidence checker, dedicated workflow-route checker, shared build file, workflow, Makefile, docs-root summary, scripts-root summary, tests-root summary, the current validation matrix, the current runtime atomic64 survey pair, the current kprobe survey pair, the current test_fsmount survey pair, and the current perf-baseline survey pair.
- The remaining roadmap-backed gaps are still bounded and unchanged here: `samples/zigux/kprobe_example.zig` remains absent behind the current survey-only packet, `samples/zigux/test_fsmount.zig` remains absent behind the current C-anchor-only survey packet, and perf thresholds plus acceptable limits for `zigux/tests/atomic64_diff.zig` and `zigux/tests/bitmap_diff.zig` remain intentionally unapproved.
