# Phase 4 Artifact-Diff Tooling Survey

## Status
- `PHASE4_ARTIFACT_DIFF_TOOLING_STATUS=helper_newline_drift_gap_closed_on_current_master`
- scope: record whether the roadmap-backed Phase 4 host-side artifact-diff tooling packet still lacks a deterministic checker or whether the current `scripts/zigux/` surface already closes that gap
- current repo reality:
  - `scripts/zigux/artifact_diff.py`
  - `scripts/zigux/check-artifact-diff-contract.py`
  - `scripts/zigux/check-phase4-artifact-diff-determinism.py`
  - `scripts/zigux/validate-phase4.py`
  - `Documentation/zigux/artifact-diff.md`
  - `Documentation/zigux/phase4-artifact-diff-tooling-survey.md`
  - `Documentation/zigux/phase4-validation-matrix.md`
  - `zigux/Makefile`
  - `.github/workflows/zigux-bootstrap.yml`

## Roadmap Comparison

Phase 4 in `ZAR_TO_ZIGUX_PRODUCT_ROADMAP (1).md` calls for artifact-diff checks for host-side tools and points the work toward `scripts/zigux/` diff and layout tooling.

Current `master` now closes the deterministic-check packet for that requirement:
- `scripts/zigux/artifact_diff.py` ships the bounded text, JSON, and SHA-256 comparison helper plus a deterministic `--self-test` packet.
- `scripts/zigux/check-artifact-diff-contract.py` replays the helper's outward CLI contract, including help-output, missing-required-args, missing-actual-operand, invalid-mode, missing-path, malformed-JSON, and repeat-run cases, and it also keeps the isolated checker self-test entrypoint reviewable beside the live contract replay.
- `scripts/zigux/check-phase4-artifact-diff-determinism.py` separately rechecks the helper self-test catalog, the contract self-test catalog, the base-case catalog, the repeat-case catalog, the full contract catalog, the dedicated review note, the docs-root and scripts-root reminder surfaces, and this roadmap-facing survey packet so case-count or reminder-surface drift fails closed.
- `scripts/zigux/validate-phase4.py` already treats both artifact-diff checkers as part of the shared Phase 4 validator-first route before the Zig rollback gates run.
- `zigux/Makefile` already exposes the same validator-first replay surface through `make -C zigux phase4-validate`, and `.github/workflows/zigux-bootstrap.yml` keeps the helper, contract, and determinism evidence inside the named `Validate Phase 4 rollback routes` step by calling that same Phase 4 validator-first route rather than by spelling those artifact-diff commands out as separate workflow steps.
- `scripts/zigux/artifact_diff.py` now reads text-mode artifacts with `newline=""`, so `LF` and `CRLF` stay distinct while still decoding as UTF-8 text.
- the helper's published `text_mismatch` self-test witness now proves `LF` versus `CRLF` drift directly instead of only a changed content word.
- because `python3 scripts/zigux/artifact_diff.py --self-test` already runs inside `make -C zigux phase4-validate` and the bootstrap workflow's `Validate Phase 4 rollback routes` step, the shipped validator-first and workflow-backed CI evidence now fail closed on newline-style text drift too.

## Deterministic Contract Packet
- `PHASE4_ARTIFACT_DIFF_HELPER_SELF_TEST_CASE_COUNT=19`
- `PHASE4_ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=24`
- `PHASE4_ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=23`
- `PHASE4_ARTIFACT_DIFF_CONTRACT_BASE_CASES=helper_self_test,cli_help_output,cli_missing_required_args,cli_missing_actual_operand,cli_invalid_mode,text_pass,text_mismatch,text_missing_expected,text_missing_actual,text_missing_both,json_pass,json_mismatch,json_missing_expected,json_missing_actual,json_missing_both,json_invalid_expected,json_invalid_actual,json_invalid_both,sha256_pass,sha256_missing_expected,sha256_missing_actual,sha256_missing_both,sha256_drift`
- `PHASE4_ARTIFACT_DIFF_CONTRACT_REPEAT_CASES=helper_self_test_repeat,cli_help_output_repeat,text_pass_repeat,json_mismatch_repeat,sha256_drift_repeat`
- `PHASE4_ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=5`
- `PHASE4_ARTIFACT_DIFF_CONTRACT_CASE_COUNT=28`
- `PHASE4_ARTIFACT_DIFF_CONTRACT_CASES=helper_self_test,helper_self_test_repeat,cli_help_output,cli_help_output_repeat,cli_missing_required_args,cli_missing_actual_operand,cli_invalid_mode,text_pass,text_pass_repeat,text_mismatch,text_missing_expected,text_missing_actual,text_missing_both,json_pass,json_mismatch,json_mismatch_repeat,json_missing_expected,json_missing_actual,json_missing_both,json_invalid_expected,json_invalid_actual,json_invalid_both,sha256_pass,sha256_missing_expected,sha256_missing_actual,sha256_missing_both,sha256_drift,sha256_drift_repeat`
- `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT=25`
- `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASES=catalog_shape,phase4_use_marker_round_trip,phase4_use_marker_drift,survey_note_marker_round_trip,survey_note_marker_drift,survey_replay_marker_round_trip,survey_replay_marker_drift,review_note_marker_round_trip,review_note_marker_drift,docs_root_marker_round_trip,docs_root_marker_drift,scripts_root_marker_round_trip,scripts_root_marker_drift,helper_summary_round_trip,helper_summary_count_drift,helper_summary_duplicate_case_drift,helper_summary_case_order_drift,contract_self_test_round_trip,contract_self_test_count_drift,contract_self_test_duplicate_case_drift,contract_self_test_missing_owner_review_note_drift,contract_self_test_case_order_drift,contract_summary_round_trip,contract_summary_case_count_drift,contract_summary_case_order_drift`
- `PHASE4_ARTIFACT_DIFF_WORKFLOW_DIRECT_CHECKS=artifact_diff_self_test,contract_self_test,contract_replay,determinism_self_test,determinism_replay`

## Current Conclusion

The live Phase 4 artifact-diff tooling lane is no longer blocked on missing checker scaffolding or helper-local newline drift. The current packet now keeps the helper, the contract checker, the determinism checker, the shared validator-first route, and the workflow-backed replay aligned around deterministic text, JSON, and SHA-256 comparison behavior on current `master`.

That means the shared helper and checker counts above are now current closed-packet inventory rather than evidence of a remaining helper-local determinism hole.

## Next Safe Step
- park this lane unless a future change touches `scripts/zigux/artifact_diff.py`, the artifact-diff case catalogs, or the shared Phase 4 reminder surfaces that record this helper packet
- if the lane reopens, start with `python3 scripts/zigux/artifact_diff.py --self-test`, `python3 scripts/zigux/check-artifact-diff-contract.py`, and a fresh readback of this survey before widening into broader validator, bitmap, atomic64, perf-baseline, workflow-route, `kprobe_example`, or `test_fsmount` work

## Owner And Rollback Reminder
- `Documentation/zigux/artifact-diff.md` remains the dedicated owner, review-rule, and rollback note for the shared host-side helper packet; the broader Phase 4 Zig rollback-gate ownership still stays in `Documentation/zigux/phase4-validation-matrix.md`.
- if `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-artifact-diff-contract.py`, or `scripts/zigux/check-phase4-artifact-diff-determinism.py` changes any published `ARTIFACT_DIFF=*`, `MODE=*`, `EXPECTED=*`, `ACTUAL=*`, `SHA256=*`, `EXPECTED_EXISTS=*`, `ACTUAL_EXISTS=*`, `EXPECTED_JSON_ERROR=*`, or `ACTUAL_JSON_ERROR=*` helper result lines, or changes any published helper, contract, or determinism catalog lines, refresh this survey and `Documentation/zigux/artifact-diff.md` in the same change before treating the tooling slice as closed again.
- newline-style text drift is now part of the shipped helper self-test packet, so future follow-through here should stay scoped to keeping that published replay and the surrounding reminder surfaces truthful rather than reopening the older missing-determinism claim.

## Direct Replay Surface
- `python3 scripts/zigux/artifact_diff.py --self-test`
- `python3 scripts/zigux/check-artifact-diff-contract.py --self-test`
- `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test`
- `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py`
- `python3 scripts/zigux/check-artifact-diff-contract.py`
- `python3 scripts/zigux/validate-phase4.py`
- `make -C zigux phase4-validate`

## Boundary
- this survey records the current roadmap-backed deterministic tooling packet for the shared host-side artifact-diff helper
- this survey does not claim that the parked `samples/zigux/kprobe_example.zig` or `samples/zigux/test_fsmount.zig` starter gaps are closed
- this survey does not promote the dedicated local-only perf-baseline packet into shared CI perf coverage
- reopen this lane only for helper-contract drift, catalog drift, validator-route drift, or reminder-surface drift tied directly to the existing artifact-diff checker packet
