# Phase 4 Artifact-Diff Verified Checks

## Status
- `PHASE4_ARTIFACT_DIFF_VERIFIED_CHECKS_DATE=2026-05-26`
- `PHASE4_ARTIFACT_DIFF_VERIFIED_CHECKS_LANE=P4-L15`
- `PHASE4_ARTIFACT_DIFF_VERIFIED_CHECKS_PHASE=Phase 4`
- `PHASE4_ARTIFACT_DIFF_VERIFIED_CHECKS_MODE=focused_scratch_replay_from_current_master_file_bodies`

## Why This Note Exists

Phase 4 in the roadmap still treats `scripts/zigux/` artifact-diff tooling as a shared host-side validation surface. The existing survey and owner note already recorded the current catalogs, but this lane needed one smaller follow-through step: rerun the current helper-side and checker-side packet in a focused scratch replay and record the exact commands and observed top-level outputs instead of only restating what the current file bodies imply.

Direct repository checkout remained blocked in this runtime, so this verification used a focused scratch replay rebuilt from the current `master` file bodies returned by authenticated GitHub contents reads for:
- `scripts/zigux/artifact_diff.py`
- `scripts/zigux/check-artifact-diff-contract.py`
- `scripts/zigux/check-phase4-artifact-diff-determinism.py`
- `scripts/zigux/check-phase4-artifact-diff-validator-replays.py`

That boundary is intentional. This note verifies the current helper, contract, determinism, and validator-replay packet directly. It does not claim a broader full-tree `validate-phase4.py` live replay from a materialized checkout.

## Exact Commands Verified

The following commands were executed in this run against the focused scratch replay:
- `python3 /workspace/.scratch_p4_l15/scripts/zigux/artifact_diff.py --self-test`
- `python3 /workspace/.scratch_p4_l15/scripts/zigux/check-artifact-diff-contract.py --self-test`
- `python3 /workspace/.scratch_p4_l15/scripts/zigux/check-artifact-diff-contract.py`
- `python3 /workspace/.scratch_p4_l15/scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test`
- `python3 /workspace/.scratch_p4_l15/scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test`

Focused direct mode checks were also executed from the same scratch helper body:
- `python3 /workspace/.scratch_p4_l15/scripts/zigux/artifact_diff.py --mode json <expected.json> <actual.json>`
- `python3 /workspace/.scratch_p4_l15/scripts/zigux/artifact_diff.py --mode bytes <blob-a.bin> <blob-b.bin>`

## Observed Outputs

Observed helper self-test summary:
- `ARTIFACT_DIFF_SELF_TEST=pass`
- `ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=23`
- `ARTIFACT_DIFF_SELF_TEST_CASES=text_pass,text_mismatch,json_pass,json_mismatch,json_invalid_expected,json_invalid_actual,json_invalid_both,json_missing_expected,json_missing_actual,json_missing_both,bytes_pass,bytes_drift,text_missing_expected,text_missing_actual,text_missing_both,bytes_missing_expected,bytes_missing_actual,bytes_missing_both,legacy_sha256_alias,missing_mode_value_rejected,missing_positional_arguments_rejected,invalid_mode_rejected,extra_positional_rejected`

Observed contract self-test summary:
- `ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass`
- `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=24`
- `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES=catalog_shape,review_note_marker_round_trip,review_note_owner_marker_drift,review_note_marker_drift,cli_help_round_trip,cli_help_line_drift,cli_missing_argument_parser_round_trip,cli_missing_argument_parser_stderr_drift,cli_invalid_mode_parser_round_trip,cli_invalid_mode_parser_stderr_drift,helper_summary_round_trip,contract_summary_round_trip,helper_summary_status_drift,helper_summary_count_drift,helper_summary_duplicate_case_drift,helper_summary_case_order_drift,contract_summary_status_drift,contract_summary_base_count_drift,contract_summary_base_case_order_drift,contract_summary_repeat_count_drift,contract_summary_repeat_case_order_drift,contract_summary_case_count_drift,contract_summary_duplicate_case_drift,contract_summary_case_order_drift`

Observed live contract summary:
- `ARTIFACT_DIFF_CONTRACT=pass`
- `ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=25`
- `ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=5`
- `ARTIFACT_DIFF_CONTRACT_CASE_COUNT=30`
- `ARTIFACT_DIFF_CONTRACT_BASE_CASES=helper_self_test,cli_help_output,cli_missing_required_args,cli_missing_mode_value,cli_missing_actual_operand,cli_invalid_mode,cli_extra_positional_args,text_pass,text_mismatch,text_missing_expected,text_missing_actual,text_missing_both,json_pass,json_mismatch,json_missing_expected,json_missing_actual,json_missing_both,json_invalid_expected,json_invalid_actual,json_invalid_both,bytes_pass,bytes_missing_expected,bytes_missing_actual,bytes_missing_both,bytes_drift`
- `ARTIFACT_DIFF_CONTRACT_REPEAT_CASES=helper_self_test_repeat,cli_help_output_repeat,text_pass_repeat,json_mismatch_repeat,bytes_drift_repeat`
- `ARTIFACT_DIFF_CONTRACT_CASES=helper_self_test,cli_help_output,cli_missing_required_args,cli_missing_mode_value,cli_missing_actual_operand,cli_invalid_mode,cli_extra_positional_args,text_pass,text_mismatch,text_missing_expected,text_missing_actual,text_missing_both,json_pass,json_mismatch,json_missing_expected,json_missing_actual,json_missing_both,json_invalid_expected,json_invalid_actual,json_invalid_both,bytes_pass,bytes_missing_expected,bytes_missing_actual,bytes_missing_both,bytes_drift,helper_self_test_repeat,cli_help_output_repeat,text_pass_repeat,json_mismatch_repeat,bytes_drift_repeat`

Observed determinism self-test summary:
- `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST=pass`
- `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT=12`
- `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASES=round_trip,survey_marker_drift,survey_packet_drift,review_checklist_drift,note_marker_drift,broader_note_marker_drift,broader_note_stale_packet_drift,repo_warning_drift,helper_mode_drift,helper_catalog_drift,contract_catalog_drift,direct_packet_missing`

Observed validator-replay self-test summary:
- `PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST=pass`
- `PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASE_COUNT=14`
- `PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASES=catalog_shape,validator_marker_round_trip,validator_helper_marker_drift,validator_marker_drift,validator_replay_marker_drift,repo_reality_handoff_round_trip,repo_reality_handoff_drift,repo_reality_handoff_note_missing,workflow_marker_round_trip,workflow_make_route_marker_drift,workflow_marker_drift,workflow_missing,artifact_diff_note_round_trip,artifact_diff_note_marker_drift`

Observed direct mode spot checks:
- JSON canonicalization replay returned `ARTIFACT_DIFF=pass` with `MODE=json` for reordered-but-equivalent JSON inputs.
- Bytes drift replay returned `ARTIFACT_DIFF=fail` with `MODE=bytes` plus both `EXPECTED_SHA256=...` and `ACTUAL_SHA256=...` lines for differing blobs.

## Current Reading

The observed replay matches the current notes rather than contradicting them:
- the helper remains a 23-case `text` / `json` / `bytes` packet with the legacy `sha256 -> bytes` alias intact
- the contract checker remains a 24-case self-test plus a 25-base-case and 5-repeat-case live catalog
- the determinism checker remains a 12-case packet
- the validator-replay checker remains a 14-case packet

## Next Safe Step

Keep this lane parked unless one of the four verified Phase 4 artifact-diff files changes again or the existing survey and owner note need a catalog refresh to match a new observed replay.
