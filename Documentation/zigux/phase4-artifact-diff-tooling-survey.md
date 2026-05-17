# Phase 4 Artifact-Diff Tooling Survey
## Status
  * `PHASE4_ARTIFACT_DIFF_TOOLING_STATUS=historical_packet_requires_repo_reality_warning_on_current_master`
  * scope: record whether the roadmap-backed Phase 4 host-side artifact-diff packet is directly readable on current `master` or whether it now survives only as historical provenance inside the current shared reversible-delivery warning packet
  * current direct-readback packet:
    * `Documentation/zigux/phase4-artifact-diff-tooling-survey.md`
    * `Documentation/zigux/phase4-reversible-delivery-evidence.md`
    * `Documentation/zigux/review-checklist.md`
    * `zigux/tests/README.md`
    * `scripts/zigux/README.md`
    * `scripts/zigux/check-phase4-repo-reality-warning.py`
    * `scripts/zigux/check-phase4-reversible-delivery-pins.py`
    * `scripts/zigux/check-phase4-artifact-diff-determinism.py`
    * `scripts/zigux/check-phase4-artifact-diff-validator-replays.py`
  * authenticated contents reads on current `master` still return missing for these historical artifact-diff companions:
    * `Documentation/zigux/artifact-diff.md`
    * `scripts/zigux/artifact_diff.py`
    * `scripts/zigux/check-artifact-diff-contract.py`
    * `scripts/zigux/validate-phase4.py`
## Roadmap Comparison

Phase 4 in `ZAR_TO_ZIGUX_PRODUCT_ROADMAP (1).md` still calls for host-side artifact-diff checks under `scripts/zigux/` so future Zigux ports stay measurable and reversible.

Current `master` no longer offers direct current-head readback for the older artifact-diff helper packet itself. Instead, the directly readable Phase 4 packet keeps the artifact-diff contract visible through reminder and warning surfaces:
  * `Documentation/zigux/phase4-reversible-delivery-evidence.md` records that the broader validator, lab-matrix, and local-only perf packet is currently a repo-reality gap and treats older artifact-diff companions as historical provenance rather than current-head proof.
  * `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` now keep the same repo-reality-warning posture explicit, including the host-side artifact-diff references that still matter for Phase 4 review.
  * `scripts/zigux/check-phase4-repo-reality-warning.py` fail-closes on that shared warning packet so future reruns must narrow the warning if the broader Phase 4 packet returns.
  * `scripts/zigux/check-phase4-artifact-diff-determinism.py` remains directly readable, but it now guards the historical-provenance handoff instead of proving that the old helper, contract, review-note, and validator files are all currently present on `master`.
  * `scripts/zigux/check-phase4-artifact-diff-validator-replays.py` is also directly readable and now fails closed with an explicit missing-target error while `scripts/zigux/validate-phase4.py` remains absent, so the last-known validator replay markers stay reviewable without pretending that the historical validator packet has already returned on current `master`.
## Historical Catalog Provenance

The last directly readable artifact-diff catalog packet recorded these counts and catalogs:
  * `PHASE4_ARTIFACT_DIFF_LAST_KNOWN_HELPER_SELF_TEST_CASE_COUNT=19`
  * `PHASE4_ARTIFACT_DIFF_LAST_KNOWN_CONTRACT_SELF_TEST_CASE_COUNT=24`
  * `PHASE4_ARTIFACT_DIFF_LAST_KNOWN_CONTRACT_BASE_CASE_COUNT=23`
  * `PHASE4_ARTIFACT_DIFF_LAST_KNOWN_CONTRACT_REPEAT_CASE_COUNT=5`
  * `PHASE4_ARTIFACT_DIFF_LAST_KNOWN_CONTRACT_CASE_COUNT=28`
  * `PHASE4_ARTIFACT_DIFF_LAST_KNOWN_CONTRACT_CASES=helper_self_test,helper_self_test_repeat,cli_help_output,cli_help_output_repeat,cli_missing_required_args,cli_missing_actual_operand,cli_invalid_mode,text_pass,text_pass_repeat,text_mismatch,text_missing_expected,text_missing_actual,text_missing_both,json_pass,json_mismatch,json_mismatch_repeat,json_missing_expected,json_missing_actual,json_missing_both,json_invalid_expected,json_invalid_actual,json_invalid_both,sha256_pass,sha256_missing_expected,sha256_missing_actual,sha256_missing_both,sha256_drift,sha256_drift_repeat`
  * `PHASE4_ARTIFACT_DIFF_LAST_KNOWN_DETERMINISM_SELF_TEST_CASE_COUNT=27`

Treat those counts as last-known catalog provenance only. They are useful for later same-lane recovery work, but this survey should not present them as fresh current-head proof while the helper, contract checker, review note, and Phase 4 validator remain unreadable on current `master`.
## Current Conclusion

The real same-lane drift was in this survey itself.

The previous version still claimed `PHASE4_ARTIFACT_DIFF_TOOLING_STATUS=roadmap_gap_closed_on_current_master` and described `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-artifact-diff-contract.py`, `scripts/zigux/validate-phase4.py`, and `Documentation/zigux/artifact-diff.md` as present current-repo surfaces. Current direct readback no longer supports that claim. The truthful current-head posture is narrower: Phase 4 still remembers the artifact-diff packet through directly readable repo-reality-warning surfaces, and the validator-replay checker now reports the missing historical validator target clearly, but the broader helper-plus-contract packet is historical provenance until a same-family lane republishes it.
## Next Safe Step
  * if a future same-family lane republishes `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-artifact-diff-contract.py`, `Documentation/zigux/artifact-diff.md`, or `scripts/zigux/validate-phase4.py`, re-read the exact current packet first, rerun `python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py`, and then promote the last-known catalog counts back to current-head evidence in the same change
  * until then, keep follow-up scoped to one reminder-surface or checker repair at a time and do not widen this lane into broader Phase 4 validator, matrix, local-only perf, bitmap, atomic64, kprobe, or `test_fsmount` work
## Owner And Rollback Reminder
  * `Tooling and Validation Team` still owns the shared Phase 4 reminder packet, including the host-side artifact-diff references, repo-reality warning, historical-provenance wording, and the directly readable validator-replay checker
  * this survey is now a catalog-truthfulness reminder only; it does not claim that the broader helper, validator, or workflow-backed artifact-diff packet is directly readable on current `master`
## Direct Replay Surface

Current directly readable replay and warning surfaces in this run were:
  * `python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test`
  * `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test`
  * `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py`
  * `python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test`

The direct validator replay command should fail closed until `scripts/zigux/validate-phase4.py` returns on current `master`:
  * `python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py`

Historical artifact-diff replay names remain part of the last-known packet only until those files return on current `master`:
  * `python3 scripts/zigux/artifact_diff.py --self-test`
  * `python3 scripts/zigux/check-artifact-diff-contract.py --self-test`
  * `python3 scripts/zigux/check-artifact-diff-contract.py`
  * `python3 scripts/zigux/validate-phase4.py`
  * `make -C zigux phase4-validate`
## Boundary
  * this survey now closes only the lane-local catalog truthfulness question for the historical Phase 4 artifact-diff tooling packet
  * this survey does not claim that the parked `samples/zigux/kprobe_example.zig` or `samples/zigux/test_fsmount.zig` starter gaps are closed
  * this survey does not promote the dedicated local-only perf-baseline packet into shared CI perf coverage
  * reopen this lane only for artifact-diff catalog drift, reminder-surface drift, or a truthful republish of the missing helper-plus-contract packet
