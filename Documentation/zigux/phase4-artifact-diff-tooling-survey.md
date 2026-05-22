# Phase 4 Artifact-Diff Tooling Survey

## Status

- `PHASE4_ARTIFACT_DIFF_TOOLING_STATUS=helper_contract_and_validator_direct_readback_aligned_but_broader_note_still_partial_on_current_master`
- scope: record whether the roadmap-backed Phase 4 host-side artifact-diff packet is directly readable on current `master` and keep the helper, contract checker, determinism checker, validator-replay checker, and shared validator reminder surfaces truthful about the live packet
- current direct-readback helper-contract-and-validator packet:
  - `Documentation/zigux/phase4-artifact-diff-tooling-survey.md`
  - `Documentation/zigux/phase4-reversible-delivery-evidence.md`
  - `Documentation/zigux/review-checklist.md`
  - `scripts/zigux/check-phase4-repo-reality-warning.py`
  - `scripts/zigux/check-phase4-reversible-delivery-pins.py`
  - `scripts/zigux/check-phase4-artifact-diff-determinism.py`
  - `scripts/zigux/check-phase4-artifact-diff-validator-replays.py`
  - `scripts/zigux/validate-phase4.py`
  - `scripts/zigux/artifact_diff.py`
  - `scripts/zigux/check-artifact-diff-contract.py`
- authenticated contents reads on current `master` still return missing for this broader artifact-diff companion:
  - `Documentation/zigux/artifact-diff.md`
- public raw GitHub fallback still reaches `Documentation/zigux/artifact-diff.md`, so the owner-and-rollback note remains reviewable even while authenticated contents reads still fail closed for that path

## Roadmap Comparison

Phase 4 in `ZAR_TO_ZIGUX_PRODUCT_ROADMAP (1).md` still calls for host-side artifact-diff checks under `scripts/zigux/` so future Zigux ports stay measurable and reversible.

Current `master` now keeps the directly readable helper, contract checker, determinism checker, validator-replay checker, and shared validator packet aligned around the same bytes-capable artifact-diff contract.

The broader `Documentation/zigux/artifact-diff.md` note now matches the current 23-case helper packet, the current 25-base-case / 30-case contract packet, and the current 12-case determinism self-test packet, but it still remains outside authenticated current-head reads in this runtime.

The directly readable Phase 4 packet therefore stays reviewable in a narrower aligned state:
- `scripts/zigux/artifact_diff.py` is directly readable on current `master`, so the bounded helper-side `text`, `json`, and `bytes` comparison entrypoints, the legacy `sha256 -> bytes` mode alias, and the shipped `ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=23` packet are current-head evidence rather than historical provenance.
- `scripts/zigux/check-artifact-diff-contract.py` is directly readable on current `master` and exact-publishes the matching helper replay plus the 25-base-case / 30-case bytes-aware contract packet, including `cli_missing_mode_value` and `cli_extra_positional_args` in the current base catalog.
- `scripts/zigux/check-phase4-artifact-diff-determinism.py` now exact-requires the broader `Documentation/zigux/artifact-diff.md` note to keep the refreshed helper, contract, and determinism anchor lines whenever that file is present in the checked tree.
- `scripts/zigux/validate-phase4.py` is directly readable again on current `master` and keeps the current artifact-diff helper, contract, determinism, and validator-replay checks explicit inside the shared Phase 4 validator packet.
- `.github/workflows/zigux-bootstrap.yml` keeps the directly readable artifact-diff packet reviewable through separate named steps for `python3 scripts/zigux/artifact_diff.py --self-test`, `python3 scripts/zigux/check-artifact-diff-contract.py --self-test`, `python3 scripts/zigux/check-artifact-diff-contract.py`, `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test`, `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py`, `python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test`, and `python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py` rather than routing the current artifact-diff packet only through one shared `make -C zigux phase4-validate` step.
- `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, and `scripts/zigux/check-phase4-repo-reality-warning.py` still keep the broader note-readback caveat explicit, which remains truthful while `Documentation/zigux/artifact-diff.md` stays outside authenticated current-head reads in this runtime.

## Current Exact Helper Checks

Current exact helper-side checks verified from the live `scripts/zigux/artifact_diff.py` body in this run are:
- `PHASE4_ARTIFACT_DIFF_CURRENT_HELPER_SELF_TEST_CASE_COUNT=23`
- `PHASE4_ARTIFACT_DIFF_CURRENT_HELPER_SELF_TEST_CASES=text_pass,text_mismatch,json_pass,json_mismatch,json_invalid_expected,json_invalid_actual,json_invalid_both,json_missing_expected,json_missing_actual,json_missing_both,bytes_pass,bytes_drift,text_missing_expected,text_missing_actual,text_missing_both,bytes_missing_expected,bytes_missing_actual,bytes_missing_both,legacy_sha256_alias,missing_mode_value_rejected,missing_positional_arguments_rejected,invalid_mode_rejected,extra_positional_rejected`
- `PHASE4_ARTIFACT_DIFF_CURRENT_HELPER_MODES=text,json,bytes`
- `PHASE4_ARTIFACT_DIFF_CURRENT_HELPER_LEGACY_MODE_ALIASES=sha256->bytes`
- `PHASE4_ARTIFACT_DIFF_CURRENT_SUCCESS_LINES=ARTIFACT_DIFF,MODE,EXPECTED,ACTUAL`
- `PHASE4_ARTIFACT_DIFF_CURRENT_BYTES_PASS_DETAIL=SHA256=<digest>`
- `PHASE4_ARTIFACT_DIFF_CURRENT_BYTES_FAIL_DETAIL=EXPECTED_SHA256=<digest>,ACTUAL_SHA256=<digest>`
- `PHASE4_ARTIFACT_DIFF_CURRENT_ERROR_LINES=EXPECTED_JSON_ERROR_or_ACTUAL_JSON_ERROR_or_EXPECTED_EXISTS_AND_ACTUAL_EXISTS`

## Current Exact Contract Checks

The directly readable `scripts/zigux/check-artifact-diff-contract.py` body now exact-publishes:
- `PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_HELPER_SELF_TEST_CASE_COUNT=23`
- `PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_HELPER_SELF_TEST_CASES=text_pass,text_mismatch,json_pass,json_mismatch,json_invalid_expected,json_invalid_actual,json_invalid_both,json_missing_expected,json_missing_actual,json_missing_both,bytes_pass,bytes_drift,text_missing_expected,text_missing_actual,text_missing_both,bytes_missing_expected,bytes_missing_actual,bytes_missing_both,legacy_sha256_alias,missing_mode_value_rejected,missing_positional_arguments_rejected,invalid_mode_rejected,extra_positional_rejected`
- `PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_SELF_TEST_CASE_COUNT=24`
- `PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_BASE_CASE_COUNT=25`
- `PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_REPEAT_CASE_COUNT=5`
- `PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_CASE_COUNT=30`
- `PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_BASE_CASES=helper_self_test,cli_help_output,cli_missing_required_args,cli_missing_mode_value,cli_missing_actual_operand,cli_invalid_mode,cli_extra_positional_args,text_pass,text_mismatch,text_missing_expected,text_missing_actual,text_missing_both,json_pass,json_mismatch,json_missing_expected,json_missing_actual,json_missing_both,json_invalid_expected,json_invalid_actual,json_invalid_both,bytes_pass,bytes_missing_expected,bytes_missing_actual,bytes_missing_both,bytes_drift`
- `PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_REPEAT_CASES=helper_self_test_repeat,cli_help_output_repeat,text_pass_repeat,json_mismatch_repeat,bytes_drift_repeat`
- `PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_CASES=helper_self_test,cli_help_output,cli_missing_required_args,cli_missing_mode_value,cli_missing_actual_operand,cli_invalid_mode,cli_extra_positional_args,text_pass,text_mismatch,text_missing_expected,text_missing_actual,text_missing_both,json_pass,json_mismatch,json_missing_expected,json_missing_actual,json_missing_both,json_invalid_expected,json_invalid_actual,json_invalid_both,bytes_pass,bytes_missing_expected,bytes_missing_actual,bytes_missing_both,bytes_drift,helper_self_test_repeat,cli_help_output_repeat,text_pass_repeat,json_mismatch_repeat,bytes_drift_repeat`
- `PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_SELF_TEST_CASES=catalog_shape,review_note_marker_round_trip,review_note_owner_marker_drift,review_note_marker_drift,cli_help_round_trip,cli_help_line_drift,cli_missing_argument_parser_round_trip,cli_missing_argument_parser_stderr_drift,cli_invalid_mode_parser_round_trip,cli_invalid_mode_parser_stderr_drift,helper_summary_round_trip,contract_summary_round_trip,helper_summary_status_drift,helper_summary_count_drift,helper_summary_duplicate_case_drift,helper_summary_case_order_drift,contract_summary_status_drift,contract_summary_base_count_drift,contract_summary_base_case_order_drift,contract_summary_repeat_count_drift,contract_summary_repeat_case_order_drift,contract_summary_case_count_drift,contract_summary_duplicate_case_drift,contract_summary_case_order_drift`

## Current Conclusion

Current `master` no longer carries the older directly readable helper-versus-contract split inside the smaller artifact-diff packet. The directly readable helper, contract checker, determinism checker, validator-replay checker, shared validator packet, and the broader owner-and-rollback note now agree on the same bytes-capable artifact-diff catalog.

The remaining limitation is narrower and operational rather than catalog-related: `Documentation/zigux/artifact-diff.md` is still only public-raw-readable in this runtime, so the same lane should stay parked unless the broader note drifts again or authenticated current-head reads start returning that path.

## Next Safe Step

- keep this lane parked unless `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-artifact-diff-contract.py`, `scripts/zigux/check-phase4-artifact-diff-determinism.py`, `Documentation/zigux/artifact-diff.md`, or this survey moves again
- if the broader note starts returning through authenticated contents reads in this runtime, refresh the survey wording and any blob-pin references only for that narrower readback-state change
- do not widen this lane into validator-marker, matrix, perf, bitmap, atomic64, or starter-gap work

## Direct Replay Surface

Current directly readable replay and warning surfaces in this run were:
- `python3 scripts/zigux/artifact_diff.py --self-test`
- `python3 scripts/zigux/check-artifact-diff-contract.py --self-test`
- `python3 scripts/zigux/check-artifact-diff-contract.py`
- `python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test`
- `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test`
- `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py`
- `python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test`
- `python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py`

## Boundary

- this survey now closes only the lane-local truthfulness gap between the directly readable helper, contract checker, determinism checker, validator-replay checker, shared validator packet, and the broader owner-and-rollback note
- this survey does not claim that `Documentation/zigux/artifact-diff.md` is authenticated-readable on current `master`
- this survey does not claim that the parked `samples/zigux/kprobe_example.zig` or `samples/zigux/test_fsmount.zig` starter gaps are closed
- this survey does not promote the dedicated local-only perf-baseline packet into shared CI perf coverage
- reopen this lane only for artifact-diff survey drift, contract-or-determinism checker drift, validator-surface truthfulness drift, or a fresh broader-note readback-state change
