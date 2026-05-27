# Zigux Artifact-Diff Notes

This note records how the shared `scripts/zigux/artifact_diff.py` helper is used by the current Zigux validation packet and which exact catalog markers downstream checks rely on.

## Current Phase 1 use

Phase 1 still uses `scripts/zigux/artifact_diff.py` as the shared host-side comparison helper behind the committed helper parity fixtures, including `phase1_helpers.json` and the Phase 1 parity reminder packet.

## Current Phase 2 use

Phase 2 still routes focused host-tool fixture comparisons through the same helper family when validating `fixdep` and the kconfig bridge packet. The current `genksyms` bridge packet keeps its fixture comparisons local to `scripts/zigux/check-genksyms-bridge.py`.

## Current Phase 3 use

Phase 3 still treats `scripts/zigux/artifact_diff.py` as the stable comparison entrypoint behind the bounded helper and manifest-backed validation surfaces published under `scripts/zigux/` and `zigux/tests/fixtures/`.

## Current Phase 4 use

Phase 4 keeps the host-side artifact-diff packet explicit through `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-artifact-diff-contract.py`, `scripts/zigux/check-phase4-artifact-diff-determinism.py`, `scripts/zigux/check-phase4-artifact-diff-validator-replays.py`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/validate-phase4.py`, `Documentation/zigux/phase4-validation-matrix.md`, `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`, `zigux/tests/bitmap_diff.zig`, `zigux/tests/phase4_bitmap_diff_survey.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig`.

The helper now compares `text`, `json`, and `bytes` artifacts, keeps the legacy `sha256 -> bytes` alias for compatibility, and publishes a stable result surface with `ARTIFACT_DIFF_RESULT_LINES=ARTIFACT_DIFF,MODE,EXPECTED,ACTUAL[,SHA256|EXPECTED_EXISTS|ACTUAL_EXISTS|EXPECTED_JSON_ERROR|ACTUAL_JSON_ERROR|EXPECTED_UTF8_ERROR|ACTUAL_UTF8_ERROR]`; the bytes-drift fail path also emits `EXPECTED_SHA256=...` and `ACTUAL_SHA256=...` so the mismatch-side digest pair stays explicit instead of being folded into the pass-path `SHA256=...` marker.

The current helper self-test packet keeps these comparison and parser coverage families explicit:
- text pass, mismatch, and missing-path cases
- JSON pass, mismatch, invalid-input, and missing-path cases
- bytes pass, digest-drift, and missing-path cases
- legacy `sha256` alias coverage plus CLI parser rejection coverage for missing mode values, missing operands, invalid modes, and extra positionals

The current helper self-test packet keeps malformed JSON and invalid UTF-8 fail-closed behavior inside the shipped `json_invalid_expected`, `json_invalid_actual`, and `json_invalid_both` cases, so the helper still publishes the same external case catalog while rejecting undecodable JSON inputs with structured `*_UTF8_ERROR` lines.

The current helper self-test packet keeps the exact bytes-path and CLI parser coverage explicit through `bytes_pass`, `bytes_drift`, `legacy_sha256_alias`, `missing_mode_value_rejected`, `missing_positional_arguments_rejected`, `invalid_mode_rejected`, and `extra_positional_rejected`.

`scripts/zigux/check-artifact-diff-contract.py` reruns the bounded helper self-test, CLI help output, missing-required-args, missing-mode-value, missing-actual-operand, invalid-mode, and extra-positional parser coverage plus the text, JSON, bytes, missing-path, malformed-input, and repeat-run cases so the helper's outward contract stays deterministic before the broader Phase 4 validator and Zig gates run.

`scripts/zigux/check-phase4-artifact-diff-determinism.py` rechecks the helper and contract summary catalogs together so case-count, case-order, and repeat-case drift fail closed before the shared Phase 4 validator and Zig gates run.

`scripts/zigux/check-phase4-artifact-diff-validator-replays.py` rechecks that the current Phase 4 artifact-diff packet either keeps the shipped validator hook set explicit or falls back to the narrower repo-reality handoff markers when exact validator readback is unavailable, so validator-route and workflow drift fail closed before the shared Phase 4 validator and Zig gates run.

## Phase 4 Exact Check Packet

Current exact Phase 4 helper replay markers are:
- `ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=23`
- `ARTIFACT_DIFF_SELF_TEST_CASES=text_pass,text_mismatch,json_pass,json_mismatch,json_invalid_expected,json_invalid_actual,json_invalid_both,json_missing_expected,json_missing_actual,json_missing_both,bytes_pass,bytes_drift,text_missing_expected,text_missing_actual,text_missing_both,bytes_missing_expected,bytes_missing_actual,bytes_missing_both,legacy_sha256_alias,missing_mode_value_rejected,missing_positional_arguments_rejected,invalid_mode_rejected,extra_positional_rejected`

Current exact Phase 4 contract replay markers are:
- `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=24`
- `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES=catalog_shape,review_note_marker_round_trip,review_note_owner_marker_drift,review_note_marker_drift,cli_help_round_trip,cli_help_line_drift,cli_missing_argument_parser_round_trip,cli_missing_argument_parser_stderr_drift,cli_invalid_mode_parser_round_trip,cli_invalid_mode_parser_stderr_drift,helper_summary_round_trip,contract_summary_round_trip,helper_summary_status_drift,helper_summary_count_drift,helper_summary_duplicate_case_drift,helper_summary_case_order_drift,contract_summary_status_drift,contract_summary_base_count_drift,contract_summary_base_case_order_drift,contract_summary_repeat_count_drift,contract_summary_repeat_case_order_drift,contract_summary_case_count_drift,contract_summary_duplicate_case_drift,contract_summary_case_order_drift`
- `ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=25`
- `ARTIFACT_DIFF_CONTRACT_BASE_CASES=helper_self_test,cli_help_output,cli_missing_required_args,cli_missing_mode_value,cli_missing_actual_operand,cli_invalid_mode,cli_extra_positional_args,text_pass,text_mismatch,text_missing_expected,text_missing_actual,text_missing_both,json_pass,json_mismatch,json_missing_expected,json_missing_actual,json_missing_both,json_invalid_expected,json_invalid_actual,json_invalid_both,bytes_pass,bytes_missing_expected,bytes_missing_actual,bytes_missing_both,bytes_drift`
- `ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=5`
- `ARTIFACT_DIFF_CONTRACT_REPEAT_CASES=helper_self_test_repeat,cli_help_output_repeat,text_pass_repeat,json_mismatch_repeat,bytes_drift_repeat`
- `ARTIFACT_DIFF_CONTRACT_CASE_COUNT=30`
- `ARTIFACT_DIFF_CONTRACT_CASES=helper_self_test,cli_help_output,cli_missing_required_args,cli_missing_mode_value,cli_missing_actual_operand,cli_invalid_mode,cli_extra_positional_args,text_pass,text_mismatch,text_missing_expected,text_missing_actual,text_missing_both,json_pass,json_mismatch,json_missing_expected,json_missing_actual,json_missing_both,json_invalid_expected,json_invalid_actual,json_invalid_both,bytes_pass,bytes_missing_expected,bytes_missing_actual,bytes_missing_both,bytes_drift,helper_self_test_repeat,cli_help_output_repeat,text_pass_repeat,json_mismatch_repeat,bytes_drift_repeat`

Current exact Phase 4 determinism replay markers are:
- `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT=13`
- `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASES=round_trip,survey_marker_drift,survey_packet_drift,survey_exact_packet_drift,review_checklist_drift,note_marker_drift,broader_note_marker_drift,broader_note_stale_packet_drift,repo_warning_drift,helper_mode_drift,helper_catalog_drift,contract_catalog_drift,direct_packet_missing`
- `PHASE4_ARTIFACT_DIFF_DETERMINISM_DIRECT_PACKET_MEMBERS=11`
- `PHASE4_ARTIFACT_DIFF_DETERMINISM_AUTH_MISSING_BROADER_COMPANIONS=0`

Current exact Phase 4 validator replay markers are:
- `PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASE_COUNT=14`
- `PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASES=catalog_shape,validator_marker_round_trip,validator_helper_marker_drift,validator_marker_drift,validator_replay_marker_drift,repo_reality_handoff_round_trip,repo_reality_handoff_drift,repo_reality_handoff_note_missing,workflow_marker_round_trip,workflow_make_route_marker_drift,workflow_marker_drift,workflow_missing,artifact_diff_note_round_trip,artifact_diff_note_marker_drift`
- `PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKER_COUNT=7`
- `PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_WORKFLOW_MARKER_COUNT=14`

## Phase 4 Tooling Review Note

`Tooling and Validation Team` owns the shared Phase 4 artifact-diff note packet for `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-artifact-diff-contract.py`, `scripts/zigux/check-phase4-artifact-diff-determinism.py`, and `scripts/zigux/check-phase4-artifact-diff-validator-replays.py`.

The note stays intentionally narrower than a full Phase 4 closure claim: it documents the current host-side artifact-diff helper, the current exact contract replay, the determinism guard, the validator-replay guard, and the Phase 4 validator touchpoints without claiming that every broader validator, bitmap, or build companion is authenticated-readable in this runtime.

Near-term follow-through should stay limited to truthful catalog refreshes, helper-contract guard alignment, validator-replay guard alignment, and direct replay evidence for the current host-side packet rather than widening into unrelated validator, perf, bitmap, atomic64, or starter-gap work.

Keep this owner note parked unless a fresh same-family drift appears between `Documentation/zigux/artifact-diff.md`, `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-artifact-diff-contract.py`, `scripts/zigux/check-phase4-artifact-diff-determinism.py`, `scripts/zigux/check-phase4-artifact-diff-validator-replays.py`, or the direct Phase 4 workflow replay surface. The remaining shared artifact-diff catalog-marker follow-through in `scripts/zigux/validate-phase4.py` belongs to the neighboring validator packet rather than to this note-only lane.