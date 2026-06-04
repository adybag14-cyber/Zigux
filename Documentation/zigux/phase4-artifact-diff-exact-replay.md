# Phase 4 Artifact-Diff Exact Replay

This note records the current exact Phase 4 artifact-diff replay packet and the top-level pass markers that must stay aligned with the current helper and checker catalogs.

## Commands
  * `python3 scripts/zigux/artifact_diff.py --self-test`
  * `python3 scripts/zigux/check-artifact-diff-contract.py --self-test`
  * `python3 scripts/zigux/check-artifact-diff-contract.py`
  * `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test`
  * `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py`
  * `python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test`
  * `python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py`
  * `python3 scripts/zigux/check-phase4-artifact-diff-exact-replay.py --self-test`
  * `python3 scripts/zigux/check-phase4-artifact-diff-exact-replay.py`

## Top-Level Pass Markers
These are the exact top-level pass markers required by the current directly readable command packet in this run.
  * `ARTIFACT_DIFF_SELF_TEST=pass`
  * `ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=23`
  * `ARTIFACT_DIFF_SELF_TEST_CASES=text_pass,text_mismatch,json_pass,json_mismatch,json_invalid_expected,json_invalid_actual,json_invalid_both,json_missing_expected,json_missing_actual,json_missing_both,bytes_pass,bytes_drift,text_missing_expected,text_missing_actual,text_missing_both,bytes_missing_expected,bytes_missing_actual,bytes_missing_both,legacy_sha256_alias,missing_mode_value_rejected,missing_positional_arguments_rejected,invalid_mode_rejected,extra_positional_rejected`
  * `ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass`
  * `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=24`
  * `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES=catalog_shape,review_note_marker_round_trip,review_note_owner_marker_drift,review_note_marker_drift,cli_help_round_trip,cli_help_line_drift,cli_missing_argument_parser_round_trip,cli_missing_argument_parser_stderr_drift,cli_invalid_mode_parser_round_trip,cli_invalid_mode_parser_stderr_drift,helper_summary_round_trip,contract_summary_round_trip,helper_summary_status_drift,helper_summary_count_drift,helper_summary_duplicate_case_drift,helper_summary_case_order_drift,contract_summary_status_drift,contract_summary_base_count_drift,contract_summary_base_case_order_drift,contract_summary_repeat_count_drift,contract_summary_repeat_case_order_drift,contract_summary_case_count_drift,contract_summary_duplicate_case_drift,contract_summary_case_order_drift`
  * `ARTIFACT_DIFF_CONTRACT=pass`
  * `ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=25`
  * `ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=5`
  * `ARTIFACT_DIFF_CONTRACT_CASE_COUNT=30`
  * `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST=pass`
  * `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT=13`
  * `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASES=round_trip,survey_marker_drift,survey_packet_drift,survey_exact_packet_drift,review_checklist_drift,note_marker_drift,broader_note_marker_drift,broader_note_stale_packet_drift,repo_warning_drift,helper_mode_drift,helper_catalog_drift,contract_catalog_drift,direct_packet_missing`
  * `PHASE4_ARTIFACT_DIFF_DETERMINISM=pass`
  * `PHASE4_ARTIFACT_DIFF_DETERMINISM_DIRECT_PACKET_MEMBERS=11`
  * `PHASE4_ARTIFACT_DIFF_DETERMINISM_AUTH_MISSING_BROADER_COMPANIONS=0`
  * `PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST=pass`
  * `PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASE_COUNT=14`
  * `PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASES=catalog_shape,validator_marker_round_trip,validator_helper_marker_drift,validator_marker_drift,validator_replay_marker_drift,repo_reality_handoff_round_trip,repo_reality_handoff_drift,repo_reality_handoff_note_missing,workflow_marker_round_trip,workflow_make_route_marker_drift,workflow_marker_drift,workflow_missing,artifact_diff_note_round_trip,artifact_diff_note_marker_drift`
  * `PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS=pass`
  * `PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MODE=validator_present`
  * `PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKER_COUNT=7`
  * `PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_WORKFLOW_MARKER_COUNT=16`
  * `PHASE4_ARTIFACT_DIFF_EXACT_REPLAY_SELF_TEST=pass`
  * `PHASE4_ARTIFACT_DIFF_EXACT_REPLAY_SELF_TEST_CASE_COUNT=8`
  * `PHASE4_ARTIFACT_DIFF_EXACT_REPLAY_SELF_TEST_CASES=catalog_shape,note_command_round_trip,note_command_drift,note_helper_catalog_drift,note_contract_catalog_drift,note_determinism_catalog_drift,note_validator_catalog_drift,note_exact_replay_catalog_drift`
  * `PHASE4_ARTIFACT_DIFF_EXACT_REPLAY=pass`
  * `PHASE4_ARTIFACT_DIFF_EXACT_REPLAY_COMMAND_COUNT=9`
