# Phase 4 Artifact-Diff Tooling Survey
## Status
  * `PHASE4_ARTIFACT_DIFF_TOOLING_STATUS=helper_contract_validator_and_owner_note_direct_readback_aligned_on_current_master`
  * scope: record whether the roadmap-backed Phase 4 host-side artifact-diff packet is directly readable on current `master` and keep the helper, contract checker, determinism checker, validator-replay checker, and shared validator reminder surfaces truthful about the live packet
  * current direct-readback helper-contract-validator-and-owner-note packet:
    * `Documentation/zigux/phase4-artifact-diff-tooling-survey.md`
    * `Documentation/zigux/phase4-reversible-delivery-evidence.md`
    * `Documentation/zigux/review-checklist.md`
    * `Documentation/zigux/artifact-diff.md`
    * `scripts/zigux/check-phase4-repo-reality-warning.py`
    * `scripts/zigux/check-phase4-reversible-delivery-pins.py`
    * `scripts/zigux/check-phase4-artifact-diff-determinism.py`
    * `scripts/zigux/check-phase4-artifact-diff-validator-replays.py`
    * `scripts/zigux/validate-phase4.py`
    * `scripts/zigux/artifact_diff.py`
    * `scripts/zigux/check-artifact-diff-contract.py`
## Roadmap Comparison

Phase 4 in `ZAR_TO_ZIGUX_PRODUCT_ROADMAP (1).md` still calls for host-side artifact-diff checks under `scripts/zigux/` so future Zigux ports stay measurable and reversible.

Current `master` now keeps the directly readable helper, contract checker, determinism checker, validator-replay checker, shared validator packet, and broader owner-and-rollback note aligned around the same bytes-capable artifact-diff contract.

The broader `Documentation/zigux/artifact-diff.md` note is directly readable on current `master` again and now matches the current 23-case helper packet, the current 25-base-case / 30-case contract packet, and the current 13-case determinism self-test packet.

The directly readable Phase 4 packet therefore stays reviewable in a fully aligned state:
  * `scripts/zigux/artifact_diff.py` is directly readable on current `master`, so the bounded helper-side `text`, `json`, and `bytes` comparison entrypoints, the legacy `sha256 -> bytes` mode alias, and the shipped `ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=23` packet are current-head evidence rather than historical provenance.
  * `scripts/zigux/check-artifact-diff-contract.py` is directly readable again on current `master` and now exact-publishes the matching helper replay plus the 25-base-case / 30-case bytes-aware contract packet, including `cli_missing_mode_value` in the base catalog.
  * `scripts/zigux/check-phase4-artifact-diff-determinism.py` now exact-requires the broader `Documentation/zigux/artifact-diff.md` note to keep the refreshed helper, contract, and determinism anchor lines whenever that file is present in the checked tree.
  * `scripts/zigux/validate-phase4.py` is directly readable again on current `master` and keeps the current artifact-diff helper, contract, determinism, and validator-replay checks explicit inside the shared Phase 4 validator packet.
  * `.github/workflows/zigux-bootstrap.yml` keeps the directly readable artifact-diff packet reviewable through separate named steps for `python3 scripts/zigux/artifact_diff.py --self-test`, `python3 scripts/zigux/check-artifact-diff-contract.py --self-test`, `python3 scripts/zigux/check-artifact-diff-contract.py`, `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test`, `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py`, `python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test`, and `python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py` rather than routing the current artifact-diff packet only through one shared `make -C zigux phase4-validate` step.
  * `zigux/Makefile` also keeps the narrower `make -C zigux phase4-artifact-diff-contract` route explicit for the helper self-test plus contract self-test and live contract replay packet instead of leaving that replay path discoverable only through workflow step names.
  * `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, and `scripts/zigux/check-phase4-repo-reality-warning.py` still keep the broader validator, build, and bitmap authenticated-readback caveat explicit without treating the owner-and-rollback note itself as a missing current-head companion.
## Current Exact Helper Checks

Current exact helper-side checks verified from the live `scripts/zigux/artifact_diff.py` body in this run are:
  * `PHASE4_ARTIFACT_DIFF_CURRENT_HELPER_SELF_TEST_CASE_COUNT=23`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_HELPER_SELF_TEST_CASES=text_pass,text_mismatch,json_pass,json_mismatch,json_invalid_expected,json_invalid_actual,json_invalid_both,json_missing_expected,json_missing_actual,json_missing_both,bytes_pass,bytes_drift,text_missing_expected,text_missing_actual,text_missing_both,bytes_missing_expected,bytes_missing_actual,bytes_missing_both,legacy_sha256_alias,missing_mode_value_rejected,missing_positional_arguments_rejected,invalid_mode_rejected,extra_positional_rejected`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_HELPER_MODES=text,json,bytes`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_HELPER_LEGACY_MODE_ALIASES=sha256->bytes`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_SUCCESS_LINES=ARTIFACT_DIFF,MODE,EXPECTED,ACTUAL`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_BYTES_PASS_DETAIL=SHA256=<digest>`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_BYTES_FAIL_DETAIL=EXPECTED_SHA256=<digest>,ACTUAL_SHA256=<digest>`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_ERROR_LINES=EXPECTED_JSON_ERROR_or_ACTUAL_JSON_ERROR_or_EXPECTED_EXISTS_AND_ACTUAL_EXISTS`
## Current Exact Contract Checks

The directly readable `scripts/zigux/check-artifact-diff-contract.py` body now exact-publishes:
  * `PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_HELPER_SELF_TEST_CASE_COUNT=23`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_HELPER_SELF_TEST_CASES=text_pass,text_mismatch,json_pass,json_mismatch,json_invalid_expected,json_invalid_actual,json_invalid_both,json_missing_expected,json_missing_actual,json_missing_both,bytes_pass,bytes_drift,text_missing_expected,text_missing_actual,text_missing_both,bytes_missing_expected,bytes_missing_actual,bytes_missing_both,legacy_sha256_alias,missing_mode_value_rejected,missing_positional_arguments_rejected,invalid_mode_rejected,extra_positional_rejected`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_SELF_TEST_CASE_COUNT=24`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_BASE_CASE_COUNT=25`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_REPEAT_CASE_COUNT=5`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_CASE_COUNT=30`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_BASE_CASES=helper_self_test,cli_help_output,cli_missing_required_args,cli_missing_mode_value,cli_missing_actual_operand,cli_invalid_mode,cli_extra_positional_args,text_pass,text_mismatch,text_missing_expected,text_missing_actual,text_missing_both,json_pass,json_mismatch,json_missing_expected,json_missing_actual,json_missing_both,json_invalid_expected,json_invalid_actual,json_invalid_both,bytes_pass,bytes_missing_expected,bytes_missing_actual,bytes_missing_both,bytes_drift`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_REPEAT_CASES=helper_self_test_repeat,cli_help_output_repeat,text_pass_repeat,json_mismatch_repeat,bytes_drift_repeat`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_CASES=helper_self_test,cli_help_output,cli_missing_required_args,cli_missing_mode_value,cli_missing_actual_operand,cli_invalid_mode,cli_extra_positional_args,text_pass,text_mismatch,text_missing_expected,text_missing_actual,text_missing_both,json_pass,json_mismatch,json_missing_expected,json_missing_actual,json_missing_both,json_invalid_expected,json_invalid_actual,json_invalid_both,bytes_pass,bytes_missing_expected,bytes_missing_actual,bytes_missing_both,bytes_drift,helper_self_test_repeat,cli_help_output_repeat,text_pass_repeat,json_mismatch_repeat,bytes_drift_repeat`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_SELF_TEST_CASES=catalog_shape,review_note_marker_round_trip,review_note_owner_marker_drift,review_note_marker_drift,cli_help_round_trip,cli_help_line_drift,cli_missing_argument_parser_round_trip,cli_missing_argument_parser_stderr_drift,cli_invalid_mode_parser_round_trip,cli_invalid_mode_parser_stderr_drift,helper_summary_round_trip,contract_summary_round_trip,helper_summary_status_drift,helper_summary_count_drift,helper_summary_duplicate_case_drift,helper_summary_case_order_drift,contract_summary_status_drift,contract_summary_base_count_drift,contract_summary_base_case_order_drift,contract_summary_repeat_count_drift,contract_summary_repeat_case_order_drift,contract_summary_case_count_drift,contract_summary_duplicate_case_drift,contract_summary_case_order_drift`
## Current Conclusion

Current `master` no longer carries the older directly readable helper-versus-contract split inside the smaller artifact-diff packet. The directly readable helper, contract checker, determinism checker, validator-replay checker, shared validator packet, and the broader owner-and-rollback note now agree on the same bytes-capable artifact-diff catalog as direct current-head evidence.

No remaining owner-and-rollback note readback caveat is left inside this lane on current `master`, so the same lane should stay parked unless the broader note or exact packet drifts again.
## Next Safe Step
  * keep this lane parked unless `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-artifact-diff-contract.py`, `scripts/zigux/check-phase4-artifact-diff-determinism.py`, `Documentation/zigux/artifact-diff.md`, or this survey moves again
  * if authenticated contents reads stop returning `Documentation/zigux/artifact-diff.md` again in a future runtime, refresh the survey wording and exact determinism markers only for that narrower readback-state change
  * do not widen this lane into validator-marker, matrix, perf, bitmap, atomic64, or starter-gap work
## Owner And Rollback Reminder
  * `Documentation/zigux/artifact-diff.md` remains the dedicated owner, review-rule, and rollback note for the shared host-side helper packet, while the broader shared Phase 4 rollback-gate ownership still stays in `Documentation/zigux/phase4-validation-matrix.md`.
  * the remaining shared artifact-diff catalog-marker follow-through in `scripts/zigux/validate-phase4.py` stays owned by the neighboring validator packet, so this survey should stay note-only unless that validator packet closes first.
  * if the host-side helper, contract checker, or determinism checker changes published artifact-diff catalog lines, refresh this survey and `Documentation/zigux/artifact-diff.md` together before treating the packet as closed again.
## Direct Replay Surface

Current directly readable Python replay and warning surfaces in this run were:
  * `python3 scripts/zigux/artifact_diff.py --self-test`
  * `python3 scripts/zigux/check-artifact-diff-contract.py --self-test`
  * `python3 scripts/zigux/check-artifact-diff-contract.py`
  * `python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test`
  * `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test`
  * `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py`
  * `python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test`
  * `python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py`

The dedicated `make -C zigux phase4-artifact-diff-contract` route stays cataloged through `zigux/Makefile` and `.github/workflows/zigux-bootstrap.yml`; this lane's exact replay section keeps the directly readable Python command bodies explicit because that make route simply replays the helper self-test, contract self-test, and live contract packet listed below.

## Exact Replay Output Contract

These are the exact top-level pass markers implied by the current directly readable Python command bodies in this run. Treat them as the lane-local replay record unless a future run re-verifies the commands against a different current-head packet.

  * `python3 scripts/zigux/artifact_diff.py --self-test`
    * `ARTIFACT_DIFF_SELF_TEST=pass`
    * `ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=23`
    * `ARTIFACT_DIFF_SELF_TEST_CASES=text_pass,text_mismatch,json_pass,json_mismatch,json_invalid_expected,json_invalid_actual,json_invalid_both,json_missing_expected,json_missing_actual,json_missing_both,bytes_pass,bytes_drift,text_missing_expected,text_missing_actual,text_missing_both,bytes_missing_expected,bytes_missing_actual,bytes_missing_both,legacy_sha256_alias,missing_mode_value_rejected,missing_positional_arguments_rejected,invalid_mode_rejected,extra_positional_rejected`
  * `python3 scripts/zigux/check-artifact-diff-contract.py --self-test`
    * `ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass`
    * `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=24`
    * `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES=catalog_shape,review_note_marker_round_trip,review_note_owner_marker_drift,review_note_marker_drift,cli_help_round_trip,cli_help_line_drift,cli_missing_argument_parser_round_trip,cli_missing_argument_parser_stderr_drift,cli_invalid_mode_parser_round_trip,cli_invalid_mode_parser_stderr_drift,helper_summary_round_trip,contract_summary_round_trip,helper_summary_status_drift,helper_summary_count_drift,helper_summary_duplicate_case_drift,helper_summary_case_order_drift,contract_summary_status_drift,contract_summary_base_count_drift,contract_summary_base_case_order_drift,contract_summary_repeat_count_drift,contract_summary_repeat_case_order_drift,contract_summary_case_count_drift,contract_summary_duplicate_case_drift,contract_summary_case_order_drift`
  * `python3 scripts/zigux/check-artifact-diff-contract.py`
    * `ARTIFACT_DIFF_CONTRACT=pass`
    * `ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=25`
    * `ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=5`
    * `ARTIFACT_DIFF_CONTRACT_CASE_COUNT=30`
  * `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test`
    * `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST=pass`
    * `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT=13`
    * `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASES=round_trip,survey_marker_drift,survey_packet_drift,survey_exact_packet_drift,review_checklist_drift,note_marker_drift,broader_note_marker_drift,broader_note_stale_packet_drift,repo_warning_drift,helper_mode_drift,helper_catalog_drift,contract_catalog_drift,direct_packet_missing`
  * `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py`
    * `PHASE4_ARTIFACT_DIFF_DETERMINISM=pass`
    * `PHASE4_ARTIFACT_DIFF_DETERMINISM_DIRECT_PACKET_MEMBERS=11`
    * `PHASE4_ARTIFACT_DIFF_DETERMINISM_AUTH_MISSING_BROADER_COMPANIONS=0`
  * `python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test`
    * `PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST=pass`
    * `PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASE_COUNT=14`
    * `PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASES=catalog_shape,validator_marker_round_trip,validator_helper_marker_drift,validator_marker_drift,validator_replay_marker_drift,repo_reality_handoff_round_trip,repo_reality_handoff_drift,repo_reality_handoff_note_missing,workflow_marker_round_trip,workflow_make_route_marker_drift,workflow_marker_drift,workflow_missing,artifact_diff_note_round_trip,artifact_diff_note_marker_drift`
  * `python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py`
    * `PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS=pass`
    * `PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MODE=validator_present`
    * `PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKER_COUNT=7`
    * `PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_WORKFLOW_MARKER_COUNT=14`

## Boundary
  * this survey now closes only the lane-local truthfulness gap between the directly readable helper, contract checker, determinism checker, validator-replay checker, shared validator packet, and the broader owner-and-rollback note
  * this survey now treats `Documentation/zigux/artifact-diff.md` as direct current-head evidence on current `master`
  * this survey does not claim that the parked `samples/zigux/kprobe_example.zig` or `samples/zigux/test_fsmount.zig` starter gaps are closed
  * this survey does not promote the dedicated local-only perf-baseline packet into shared CI perf coverage
  * reopen this lane only for artifact-diff survey drift, contract-or-determinism checker drift, validator-surface truthfulness drift, or a fresh broader-note readback-state change
