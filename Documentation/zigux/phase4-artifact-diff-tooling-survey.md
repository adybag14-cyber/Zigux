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
  * `scripts/zigux/artifact_diff.py` is directly readable again on current `master`, so the bounded helper-side `json`, `text`, and `bytes` comparison entrypoints plus the shipped `ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=7` packet are current-head evidence rather than historical provenance.
  * `Documentation/zigux/phase4-reversible-delivery-evidence.md` still records that the broader validator, lab-matrix, and local-only perf packet is currently a repo-reality gap and treats the older contract and validator companions as historical provenance rather than current-head proof.
  * `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` keep the same repo-reality-warning posture explicit, including the host-side artifact-diff references that still matter for Phase 4 review.
  * `scripts/zigux/check-phase4-repo-reality-warning.py` fail-closes on that shared warning packet so future reruns must narrow the warning if the broader Phase 4 packet returns.
  * `scripts/zigux/check-phase4-artifact-diff-determinism.py` remains directly readable and should now fail closed if this survey or the repo-reality handoff regresses to treating `scripts/zigux/artifact_diff.py` as absent again.
  * `scripts/zigux/check-phase4-artifact-diff-validator-replays.py` is also directly readable and still fails closed with an explicit missing-target error while `scripts/zigux/validate-phase4.py` remains absent, so the last-known validator replay markers stay reviewable without pretending that the historical validator packet has already returned on current `master`.
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

The real same-lane drift was in this survey itself and in the coupled determinism handoff.

The previous version still treated `scripts/zigux/artifact_diff.py` as missing on current `master` even though current direct readback now returns it. The truthful current-head posture is narrower: the helper itself is directly readable again on current `master` through `scripts/zigux/artifact_diff.py`, while `Documentation/zigux/artifact-diff.md`, `scripts/zigux/check-artifact-diff-contract.py`, and `scripts/zigux/validate-phase4.py` remain broader missing companions.
## Next Safe Step
  * if a future same-family lane republishes `Documentation/zigux/artifact-diff.md`, `scripts/zigux/check-artifact-diff-contract.py`, or `scripts/zigux/validate-phase4.py`, re-read the exact current packet first, rerun `python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py`, and then promote the last-known broader contract counts back to current-head evidence in the same change
  * until then, keep follow-up scoped to one reminder-surface or checker repair at a time and do not widen this lane into broader Phase 4 validator, matrix, local-only perf, bitmap, atomic64, or starter-gap work
## Owner And Rollback Reminder
  * `Tooling and Validation Team` still owns the shared Phase 4 reminder packet, including the host-side artifact-diff references, repo-reality warning, historical-provenance wording for the broader contract companions, and the directly readable validator-replay checker
  * this survey now closes only the helper-return truthfulness question for the historical Phase 4 artifact-diff tooling packet; it does not claim that the broader contract or validator packet is directly readable on current `master`
## Direct Replay Surface

Current directly readable replay and warning surfaces in this run were:
  * `python3 scripts/zigux/artifact_diff.py --self-test`
  * `python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test`
  * `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test`
  * `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py`
  * `python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test`

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
