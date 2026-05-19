# Phase 4 Artifact-Diff Tooling Survey
## Status
  * `PHASE4_ARTIFACT_DIFF_TOOLING_STATUS=helper_direct_readback_restored_but_broader_contract_packet_still_partial_on_current_master`
  * scope: record whether the roadmap-backed Phase 4 host-side artifact-diff packet is directly readable on current `master` or whether it now survives only as a split packet between the returned helper and the still-missing broader contract companions
  * current direct-readback helper packet:
    * `Documentation/zigux/phase4-artifact-diff-tooling-survey.md`
    * `Documentation/zigux/phase4-reversible-delivery-evidence.md`
    * `Documentation/zigux/review-checklist.md`
    * `zigux/tests/README.md`
    * `scripts/zigux/README.md`
    * `scripts/zigux/check-phase4-repo-reality-warning.py`
    * `scripts/zigux/check-phase4-reversible-delivery-pins.py`
    * `scripts/zigux/check-phase4-artifact-diff-determinism.py`
    * `scripts/zigux/check-phase4-artifact-diff-validator-replays.py`
    * `scripts/zigux/artifact_diff.py`
  * authenticated contents reads on current `master` still return missing for these broader artifact-diff companions:
    * `Documentation/zigux/artifact-diff.md`
    * `scripts/zigux/check-artifact-diff-contract.py`
    * `scripts/zigux/validate-phase4.py`
## Roadmap Comparison

Phase 4 in `ZAR_TO_ZIGUX_PRODUCT_ROADMAP (1).md` still calls for host-side artifact-diff checks under `scripts/zigux/` so future Zigux ports stay measurable and reversible.

Current `master` now offers direct current-head readback for the helper itself through `scripts/zigux/artifact_diff.py`, but it still does not expose the full older helper-plus-contract packet. The directly readable Phase 4 packet therefore keeps the artifact-diff contract visible through a split handoff:
  * `scripts/zigux/artifact_diff.py` is directly readable again on current `master`, so the bounded helper-side `text`, `json`, and `bytes` comparison entrypoints, the legacy `sha256 -> bytes` mode alias, and the shipped `ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=20` packet are current-head evidence rather than historical provenance.
  * `.github/workflows/zigux-bootstrap.yml` now keeps the directly readable artifact-diff packet reviewable through separate named steps for `python3 scripts/zigux/artifact_diff.py --self-test`, `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test`, `python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test`, and `python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py` rather than routing the current artifact-diff packet only through one shared `make -C zigux phase4-validate` step.
  * `Documentation/zigux/phase4-reversible-delivery-evidence.md` still records that the broader validator, lab-matrix, and local-only perf packet is currently a repo-reality gap and treats the older contract and validator companions as historical provenance rather than current-head proof.
  * `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` keep the same repo-reality-warning posture explicit, including the host-side artifact-diff references that still matter for Phase 4 review.
  * `scripts/zigux/check-phase4-repo-reality-warning.py` fail-closes on that shared warning packet so future reruns must narrow the warning if the broader Phase 4 packet returns.
  * `scripts/zigux/check-phase4-artifact-diff-determinism.py` remains directly readable and should now fail closed if this survey or the repo-reality handoff regresses to treating `scripts/zigux/artifact_diff.py` as absent again.
  * `scripts/zigux/check-phase4-artifact-diff-validator-replays.py` is also directly readable and still fails closed with an explicit missing-target error while `scripts/zigux/validate-phase4.py` remains absent, so the last-known validator replay markers stay reviewable without pretending that the historical validator packet has already returned on current `master`.
## Current Exact Helper Checks

Current exact helper-side checks verified from the live `scripts/zigux/artifact_diff.py` body in this run are:
  * `PHASE4_ARTIFACT_DIFF_CURRENT_HELPER_SELF_TEST_CASE_COUNT=20`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_HELPER_SELF_TEST_CASES=text_pass,text_mismatch,json_pass,json_mismatch,json_invalid_expected,json_invalid_actual,json_invalid_both,json_missing_expected,json_missing_actual,json_missing_both,bytes_pass,bytes_drift,text_missing_expected,text_missing_actual,text_missing_both,bytes_missing_expected,bytes_missing_actual,bytes_missing_both,legacy_sha256_alias,invalid_mode_rejected`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_HELPER_MODES=text,json,bytes`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_HELPER_LEGACY_MODE_ALIASES=sha256->bytes`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_SUCCESS_LINES=ARTIFACT_DIFF,MODE,EXPECTED,ACTUAL`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_BYTES_PASS_DETAIL=SHA256=<digest>`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_BYTES_FAIL_DETAIL=EXPECTED_SHA256=<digest>,ACTUAL_SHA256=<digest>`
  * `PHASE4_ARTIFACT_DIFF_CURRENT_ERROR_LINES=EXPECTED_JSON_ERROR_or_ACTUAL_JSON_ERROR_or_EXPECTED_EXISTS_AND_ACTUAL_EXISTS`

The bounded current helper output contract visible in that body is:
  * `python3 scripts/zigux/artifact_diff.py --self-test` should return `ARTIFACT_DIFF_SELF_TEST=pass`, `ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=20`, and the exact `ARTIFACT_DIFF_SELF_TEST_CASES=` catalog for the current helper packet
  * `python3 scripts/zigux/artifact_diff.py --mode json <expected> <actual>` should print `ARTIFACT_DIFF=pass`, `MODE=json`, `EXPECTED=<path>`, and `ACTUAL=<path>` when canonical decoded JSON matches even if formatting differs
  * `python3 scripts/zigux/artifact_diff.py --mode text <expected> <actual>` should print `ARTIFACT_DIFF=fail`, `MODE=text`, `EXPECTED=<path>`, and `ACTUAL=<path>` when UTF-8 text differs, with no extra mismatch detail lines beyond that status-and-path packet
  * `python3 scripts/zigux/artifact_diff.py --mode bytes <expected> <actual>` should print `ARTIFACT_DIFF=fail`, `MODE=bytes`, `EXPECTED=<path>`, `ACTUAL=<path>`, `EXPECTED_SHA256=<digest>`, and `ACTUAL_SHA256=<digest>` when the digests differ
  * `python3 scripts/zigux/artifact_diff.py --mode sha256 <expected> <actual>` should keep working as a legacy alias and still print `MODE=bytes` after normalization before the same digest-detail lines
  * `python3 scripts/zigux/artifact_diff.py --mode json <expected> <invalid-actual>` should print `ARTIFACT_DIFF=fail`, `MODE=json`, `EXPECTED=<path>`, `ACTUAL=<path>`, and the exact invalid-JSON location line while returning the normal failure exit status
## Historical Catalog Provenance

The last directly readable broader contract packet recorded these counts and catalogs:
  * `PHASE4_ARTIFACT_DIFF_LAST_KNOWN_CONTRACT_SELF_TEST_CASE_COUNT=24`
  * `PHASE4_ARTIFACT_DIFF_LAST_KNOWN_CONTRACT_BASE_CASE_COUNT=23`
  * `PHASE4_ARTIFACT_DIFF_LAST_KNOWN_CONTRACT_REPEAT_CASE_COUNT=5`
  * `PHASE4_ARTIFACT_DIFF_LAST_KNOWN_CONTRACT_CASE_COUNT=28`
  * `PHASE4_ARTIFACT_DIFF_LAST_KNOWN_CONTRACT_CASES=helper_self_test,helper_self_test_repeat,cli_help_output,cli_help_output_repeat,cli_missing_required_args,cli_missing_actual_operand,cli_invalid_mode,text_pass,text_pass_repeat,text_mismatch,text_missing_expected,text_missing_actual,text_missing_both,json_pass,json_mismatch,json_mismatch_repeat,json_missing_expected,json_missing_actual,json_missing_both,json_invalid_expected,json_invalid_actual,json_invalid_both,sha256_pass,sha256_missing_expected,sha256_missing_actual,sha256_missing_both,sha256_drift,sha256_drift_repeat`
  * `PHASE4_ARTIFACT_DIFF_LAST_KNOWN_DETERMINISM_SELF_TEST_CASE_COUNT=27`

Treat those broader contract counts as last-known provenance only. They are useful for later same-lane recovery work, but this survey should not present them as fresh current-head proof while `Documentation/zigux/artifact-diff.md`, `scripts/zigux/check-artifact-diff-contract.py`, and `scripts/zigux/validate-phase4.py` remain unreadable on current `master`.
## Current Conclusion

The real same-lane drift was that this survey still relabeled the current helper's byte-mode packet as a `sha256` mode family and undercounted the live self-test catalog.

The truthful current-head posture is narrower: the helper itself is directly readable again on current `master` through `scripts/zigux/artifact_diff.py`, its direct modes are `text`, `json`, and `bytes`, its legacy `sha256` alias normalizes to `MODE=bytes`, and it now ships a twenty-case self-test catalog, while `Documentation/zigux/artifact-diff.md`, `scripts/zigux/check-artifact-diff-contract.py`, and `scripts/zigux/validate-phase4.py` remain broader missing companions rather than fresh current-head proof.
## Next Safe Step
  * if a future same-family lane republishes `Documentation/zigux/artifact-diff.md`, `scripts/zigux/check-artifact-diff-contract.py`, or `scripts/zigux/validate-phase4.py`, re-read the exact current packet first, rerun `python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py`, and then decide whether the older broader contract counts still match the republished current-head files before promoting them back to current-head evidence in the same change
  * until then, keep follow-up scoped to one reminder-surface or checker repair at a time and do not widen this lane into broader Phase 4 validator, matrix, local-only perf, bitmap, atomic64, or starter-gap work
## Owner And Rollback Reminder
  * `Tooling and Validation Team` still owns the shared Phase 4 reminder packet, including the host-side artifact-diff references, repo-reality warning, historical-provenance wording for the broader contract companions, and the directly readable validator-replay checker
  * the remaining artifact-diff validator follow-through around `scripts/zigux/validate-phase4.py` stays owned by the neighboring validator packet, so this survey should stay narrowed to the directly readable helper and determinism surfaces until that validator packet returns on current `master`
  * this survey now closes only the helper-return truthfulness question for the historical Phase 4 artifact-diff tooling packet; it does not claim that the broader contract or validator packet is directly readable on current `master`
## Direct Replay Surface

Current directly readable replay and warning surfaces in this run were:
  * `python3 scripts/zigux/artifact_diff.py --self-test`
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
  * `python3 scripts/zigux/check-artifact-diff-contract.py --self-test`
  * `python3 scripts/zigux/check-artifact-diff-contract.py`
  * `python3 scripts/zigux/validate-phase4.py`
  * `make -C zigux phase4-validate`
## Boundary
  * this survey now closes only the lane-local truthfulness gap between the directly readable helper packet and the still-missing broader contract companions
  * this survey does not claim that the parked `samples/zigux/kprobe_example.zig` or `samples/zigux/test_fsmount.zig` starter gaps are closed
  * this survey does not promote the dedicated local-only perf-baseline packet into shared CI perf coverage
  * reopen this lane only for artifact-diff survey drift, determinism-check drift, or a truthful republish of the broader missing contract packet