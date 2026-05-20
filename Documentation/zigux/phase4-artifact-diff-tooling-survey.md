# Phase 4 Artifact-Diff Tooling Survey
## Status
  * `PHASE4_ARTIFACT_DIFF_TOOLING_STATUS=helper_and_contract_checker_direct_readback_aligned_but_broader_note_and_validator_packet_still_partial_on_current_master`
  * scope: record whether the roadmap-backed Phase 4 host-side artifact-diff packet is directly readable on current `master` and keep the helper, contract checker, and determinism reminder surfaces truthful about the live packet
  * current direct-readback helper-and-contract packet:
    * `Documentation/zigux/phase4-artifact-diff-tooling-survey.md`
    * `Documentation/zigux/phase4-reversible-delivery-evidence.md`
    * `Documentation/zigux/review-checklist.md`
    * `scripts/zigux/check-phase4-repo-reality-warning.py`
    * `scripts/zigux/check-phase4-reversible-delivery-pins.py`
    * `scripts/zigux/check-phase4-artifact-diff-determinism.py`
    * `scripts/zigux/check-phase4-artifact-diff-validator-replays.py`
    * `scripts/zigux/artifact_diff.py`
    * `scripts/zigux/check-artifact-diff-contract.py`
  * authenticated contents reads on current `master` still return missing for these broader artifact-diff companions:
    * `Documentation/zigux/artifact-diff.md`
    * `scripts/zigux/validate-phase4.py`
  * public raw GitHub fallback still reaches `Documentation/zigux/artifact-diff.md`, so the owner-and-rollback note remains reviewable even while authenticated contents reads still fail closed for that path
## Roadmap Comparison

Phase 4 in `ZAR_TO_ZIGUX_PRODUCT_ROADMAP (1).md` still calls for host-side artifact-diff checks under `scripts/zigux/` so future Zigux ports stay measurable and reversible.

Current `master` now keeps the directly readable helper and contract checker aligned around the same bytes-capable packet instead of splitting them between a newer helper and an older outward contract catalog.

The directly readable Phase 4 packet therefore remains reviewable without overstating broader recovery:
  * `scripts/zigux/artifact_diff.py` is directly readable on current `master`, so the bounded helper-side `text`, `json`, and `bytes` comparison entrypoints, the legacy `sha256 -> bytes` mode alias, and the shipped `ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=21` packet are current-head evidence rather than historical provenance.
  * that current helper packet includes `extra_positional_rejected` in addition to the `bytes_*` cases and `legacy_sha256_alias`, so any same-lane note that stops at the older helper catalog is stale.
  * `scripts/zigux/check-artifact-diff-contract.py` is also directly readable again on current `master` and now publishes the same bytes-oriented outward packet rather than the older `sha256_*` catalog.
  * `.github/workflows/zigux-bootstrap.yml` keeps the directly readable artifact-diff packet reviewable through separate named steps for `python3 scripts/zigux/artifact_diff.py --self-test`, `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test`, `python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test`, and `python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py` rather than routing the current artifact-diff packet only through one shared `make -C zigux phase4-validate` step.
  * `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, and `scripts/zigux/check-phase4-repo-reality-warning.py` still keep the broader validator and note-recovery caveat explicit, which is truthful while `Documentation/zigux/artifact-diff.md` and `scripts/zigux/validate-phase4.py` remain outside authenticated current-head reads in this runtime.
## Current Exact Helper Checks

Current exact helper-side checks verified from the live `scripts/zigux/artifact_diff.py` body in this run are:
  * `PHASE4_ARTIFACT_DIFF_CURRENT_HELPER_SELF_TEST_CASE_COUNT=21`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_HELPER_SELF_TEST_CASES=text_pass,text_mismatch,json_pass,json_mismatch,json_invalid_expected,json_invalid_actual,json_invalid_both,json_missing_expected,json_missing_actual,json_missing_both,bytes_pass,bytes_drift,text_missing_expected,text_missing_actual,text_missing_both,bytes_missing_expected,bytes_missing_actual,bytes_missing_both,legacy_sha256_alias,invalid_mode_rejected,extra_positional_rejected`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_HELPER_MODES=text,json,bytes`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_HELPER_LEGACY_MODE_ALIASES=sha256->bytes`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_SUCCESS_LINES=ARTIFACT_DIFF,MODE,EXPECTED,ACTUAL`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_BYTES_PASS_DETAIL=SHA256=<digest>`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_BYTES_FAIL_DETAIL=EXPECTED_SHA256=<digest>,ACTUAL_SHA256=<digest>`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_ERROR_LINES=EXPECTED_JSON_ERROR_or_ACTUAL_JSON_ERROR_or_EXPECTED_EXISTS_AND_ACTUAL_EXISTS`
## Current Exact Contract Checks

The directly readable `scripts/zigux/check-artifact-diff-contract.py` body now exact-publishes:
  * `PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_SELF_TEST_CASE_COUNT=24`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_BASE_CASE_COUNT=24`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_REPEAT_CASE_COUNT=5`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_CASE_COUNT=29`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_BASE_CASES=helper_self_test,cli_help_output,cli_missing_required_args,cli_missing_actual_operand,cli_invalid_mode,cli_extra_positional_args,text_pass,text_mismatch,text_missing_expected,text_missing_actual,text_missing_both,json_pass,json_mismatch,json_missing_expected,json_missing_actual,json_missing_both,json_invalid_expected,json_invalid_actual,json_invalid_both,bytes_pass,bytes_missing_expected,bytes_missing_actual,bytes_missing_both,bytes_drift`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_REPEAT_CASES=helper_self_test_repeat,cli_help_output_repeat,text_pass_repeat,json_mismatch_repeat,bytes_drift_repeat`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_CASES=helper_self_test,cli_help_output,cli_missing_required_args,cli_missing_actual_operand,cli_invalid_mode,cli_extra_positional_args,text_pass,text_mismatch,text_missing_expected,text_missing_actual,text_missing_both,json_pass,json_mismatch,json_missing_expected,json_missing_actual,json_missing_both,json_invalid_expected,json_invalid_actual,json_invalid_both,bytes_pass,bytes_missing_expected,bytes_missing_actual,bytes_missing_both,bytes_drift,helper_self_test_repeat,cli_help_output_repeat,text_pass_repeat,json_mismatch_repeat,bytes_drift_repeat`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_SELF_TEST_CASES=catalog_shape,review_note_marker_round_trip,review_note_owner_marker_drift,review_note_marker_drift,cli_help_round_trip,cli_help_line_drift,cli_missing_argument_parser_round_trip,cli_missing_argument_parser_stderr_drift,cli_invalid_mode_parser_round_trip,cli_invalid_mode_parser_stderr_drift,helper_summary_round_trip,contract_summary_round_trip,helper_summary_status_drift,helper_summary_count_drift,helper_summary_duplicate_case_drift,helper_summary_case_order_drift,contract_summary_status_drift,contract_summary_base_count_drift,contract_summary_base_case_order_drift,contract_summary_repeat_count_drift,contract_summary_repeat_case_order_drift,contract_summary_case_count_drift,contract_summary_duplicate_case_drift,contract_summary_case_order_drift`
## Current Conclusion

The same-lane deterministic-check gap against the roadmap was the stale contract reminder packet, not the helper implementation itself.

That gap is now narrowed on current `master`: the helper, the contract checker, and the determinism checker all describe the same directly readable bytes-capable artifact-diff surface, while the broader note and validator companions remain explicitly partial rather than being promoted into recovered current-head proof.

Treat the broader packet as still partial rather than fully recovered: `Documentation/zigux/artifact-diff.md` is publicly readable through the raw GitHub fallback but still 404s through authenticated contents reads in this runtime, and `scripts/zigux/validate-phase4.py` remains the missing broader validator companion in authenticated reads.
## Next Safe Step
  * keep follow-through outside this lane bounded to the broader note-and-validator packet, not to more helper-or-contract churn
  * if the broader authenticated-read companions return later, rerun the survey and determinism checker so they can truthfully narrow the warning without touching unrelated Phase 4 work
  * until then, do not widen this lane into validator, matrix, perf, bitmap, atomic64, or starter-gap work
## Owner And Rollback Reminder
  * `Tooling and Validation Team` still owns the shared Phase 4 reminder packet, including the host-side artifact-diff references, repo-reality warning, current-head helper and contract-checker truthfulness, and the directly readable validator-replay checker
  * the remaining artifact-diff validator follow-through around `scripts/zigux/validate-phase4.py` stays owned by the neighboring validator packet, so this survey should stay narrowed to the directly readable helper, contract, and determinism surfaces until that validator packet returns on current `master`
  * this survey now closes only the lane-local truthfulness gap for the directly readable helper, contract checker, and determinism packet; it does not claim that the broader note companion is authenticated-readable or that the validator packet is directly readable on current `master`
## Direct Replay Surface

Current directly readable replay and warning surfaces in this run were:
  * `python3 scripts/zigux/artifact_diff.py --self-test`
  * `python3 scripts/zigux/check-artifact-diff-contract.py --self-test`
  * `python3 scripts/zigux/check-artifact-diff-contract.py`
  * `python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test`
  * `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test`
  * `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py`
  * `python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test`

Current directly readable workflow step names in this run were:
  * `Self-test current Phase 4 artifact-diff helper`
  * `Self-test current Phase 4 artifact-diff determinism checker`
  * `Self-test current Phase 4 artifact-diff validator replay checker`
  * `Check current Phase 4 artifact-diff validator replay packet`

The direct validator replay command should fail closed until `scripts/zigux/validate-phase4.py` returns on current `master`:
  * `python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py`

Historical broader companion replay names remain outside current direct-readback proof until those files return on current `master`:
  * `python3 scripts/zigux/validate-phase4.py`
  * `make -C zigux phase4-validate`
## Boundary
  * this survey now closes only the lane-local truthfulness gap between the directly readable helper, contract checker, determinism checker, the raw-fallback-readable owner note, and the still-missing broader validator companion
  * this survey does not claim that the parked `samples/zigux/kprobe_example.zig` or `samples/zigux/test_fsmount.zig` starter gaps are closed
  * this survey does not promote the dedicated local-only perf-baseline packet into shared CI perf coverage
  * reopen this lane only for artifact-diff survey drift, contract-or-determinism checker drift, or a truthful republish of the broader missing note or validator packet
