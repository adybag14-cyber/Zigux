# Phase 4 Artifact-Diff Tooling Survey

## Status
- `PHASE4_ARTIFACT_DIFF_TOOLING_STATUS=roadmap_gap_closed_on_current_master`
- scope: record whether the roadmap-backed Phase 4 host-side artifact-diff tooling packet still lacks a deterministic checker or whether the current `scripts/zigux/` surface already closes that gap
- current repo reality:
  - `scripts/zigux/artifact_diff.py`
  - `scripts/zigux/check-artifact-diff-contract.py`
  - `scripts/zigux/check-phase4-artifact-diff-determinism.py`
  - `scripts/zigux/validate-phase4.py`
  - `Documentation/zigux/artifact-diff.md`
  - `Documentation/zigux/phase4-validation-matrix.md`
  - `zigux/Makefile`
  - `.github/workflows/zigux-bootstrap.yml`

## Roadmap Comparison

Phase 4 in `ZAR_TO_ZIGUX_PRODUCT_ROADMAP (1).md` calls for artifact-diff checks for host-side tools and points the work toward `scripts/zigux/` diff and layout tooling.

Current `master` already closes the deterministic-check slice of that requirement:
- `scripts/zigux/artifact_diff.py` ships the bounded text, JSON, and SHA-256 comparison helper plus a deterministic `--self-test` packet.
- `scripts/zigux/check-artifact-diff-contract.py` replays the helper's outward CLI contract, including help-output, missing-required-args, missing-actual-operand, invalid-mode, missing-path, malformed-JSON, and repeat-run cases, and it also keeps the isolated checker self-test entrypoint reviewable beside the live contract replay.
- `scripts/zigux/check-phase4-artifact-diff-determinism.py` separately rechecks the helper self-test catalog, the contract self-test catalog, the base-case catalog, the repeat-case catalog, the full contract catalog, the dedicated review note, the docs-root and scripts-root reminder surfaces, and this roadmap-facing survey packet so case-count or reminder-surface drift fails closed.
- `scripts/zigux/validate-phase4.py` already treats both artifact-diff checkers as part of the shared Phase 4 validator-first route before the Zig rollback gates run.
- `zigux/Makefile` and `.github/workflows/zigux-bootstrap.yml` already expose the same validator-first replay surface through `make -C zigux phase4-validate` and the bootstrap workflow.

## Deterministic Contract Packet
- `PHASE4_ARTIFACT_DIFF_HELPER_SELF_TEST_CASE_COUNT=19`
- `PHASE4_ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=24`
- `PHASE4_ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=23`
- `PHASE4_ARTIFACT_DIFF_CONTRACT_BASE_CASES=helper_self_test,cli_help_output,cli_missing_required_args,cli_missing_actual_operand,cli_invalid_mode,text_pass,text_mismatch,text_missing_expected,text_missing_actual,text_missing_both,json_pass,json_mismatch,json_missing_expected,json_missing_actual,json_missing_both,json_invalid_expected,json_invalid_actual,json_invalid_both,sha256_pass,sha256_missing_expected,sha256_missing_actual,sha256_missing_both,sha256_drift`
- `PHASE4_ARTIFACT_DIFF_CONTRACT_REPEAT_CASES=helper_self_test_repeat,cli_help_output_repeat,text_pass_repeat,json_mismatch_repeat,sha256_drift_repeat`
- `PHASE4_ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=5`
- `PHASE4_ARTIFACT_DIFF_CONTRACT_CASE_COUNT=28`
- `PHASE4_ARTIFACT_DIFF_CONTRACT_CASES=helper_self_test,helper_self_test_repeat,cli_help_output,cli_help_output_repeat,cli_missing_required_args,cli_missing_actual_operand,cli_invalid_mode,text_pass,text_pass_repeat,text_mismatch,text_missing_expected,text_missing_actual,text_missing_both,json_pass,json_mismatch,json_mismatch_repeat,json_missing_expected,json_missing_actual,json_missing_both,json_invalid_expected,json_invalid_actual,json_invalid_both,sha256_pass,sha256_missing_expected,sha256_missing_actual,sha256_missing_both,sha256_drift,sha256_drift_repeat`
- `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT=21`

## Current Conclusion

The live Phase 4 artifact-diff tooling gap is not a missing deterministic checker anymore. The current same-lane follow-through is a fail-closed reminder surface: this survey now records the live helper, contract, and determinism packet counts plus the exact base-case and full-case contract catalogs, so the paired `cli_help_output` replays stay visible as part of the published contract packet while the dedicated checker keeps the review note plus the docs-root and scripts-root reminder surfaces aligned before the broader Phase 4 validator-first route runs.

## Owner And Rollback Reminder
- `Documentation/zigux/artifact-diff.md` remains the dedicated owner and rollback note for the shared host-side helper packet; the broader Phase 4 Zig rollback-gate ownership still stays in `Documentation/zigux/phase4-validation-matrix.md`.
- if `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-artifact-diff-contract.py`, or `scripts/zigux/check-phase4-artifact-diff-determinism.py` changes any published helper, contract, or determinism catalog lines, refresh this survey and `Documentation/zigux/artifact-diff.md` in the same change before treating the tooling slice as closed again.

## Direct Replay Surface
- `python3 scripts/zigux/artifact_diff.py --self-test`
- `python3 scripts/zigux/check-artifact-diff-contract.py --self-test`
- `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test`
- `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py`
- `python3 scripts/zigux/check-artifact-diff-contract.py`
- `python3 scripts/zigux/validate-phase4.py`
- `make -C zigux phase4-validate`

## Boundary
- this survey closes only the roadmap-backed deterministic tooling question for the shared host-side artifact-diff packet
- this survey does not claim that the parked `samples/zigux/kprobe_example.zig` or `samples/zigux/test_fsmount.zig` starter gaps are closed
- this survey does not promote the dedicated local-only perf-baseline packet into shared CI perf coverage
- reopen this lane only for helper-contract drift, catalog drift, validator-route drift, or reminder-surface drift tied directly to the existing artifact-diff checker packet
