# Phase 4 Validation Matrix

## Status
  * `PHASE4_STATUS=differential_validation_matrix_landed`
  * scope: keep the currently shipped Phase 4 rollback-readiness gates, the host-side artifact-diff contract replay, the dedicated artifact-diff determinism checker, the dedicated artifact-diff validator-replay checker, the dedicated exact-readback gate-evidence packet, the dedicated validation-lane sequencing note and checker, the direct-readback repo-reality warning and tests-readme packet checkers, the dedicated remaining-gap matrix checker, the dedicated workflow-route-count checker, the manifest-backed runtime atomic64 and bitmap rollback survey packets, and the dedicated local perf-baseline posture survey reviewable, name the rollback owners for each bounded gate or survey, and make the current CI and local replay paths explicit
  * current repo reality:
    * `scripts/zigux/artifact_diff.py`
    * `scripts/zigux/check-artifact-diff-contract.py`
    * `scripts/zigux/check-phase4-artifact-diff-determinism.py`
    * `scripts/zigux/check-phase4-artifact-diff-validator-replays.py`
    * `scripts/zigux/check-phase4-gate-evidence.py`
    * `scripts/zigux/check-phase4-validation-lane-sequencing.py`
    * `scripts/zigux/check-phase4-perf-baseline-packet.py`
    * `scripts/zigux/check-phase4-perf-threshold-matrix.py`
    * `scripts/zigux/check-phase4-remaining-gap-matrix.py`
    * `scripts/zigux/check-phase4-repo-reality-warning.py`
    * `scripts/zigux/check-phase4-reversible-delivery-pins.py`
    * `scripts/zigux/check-phase4-tests-readme-packet.py`
    * `scripts/zigux/check-phase4-workflow-route-counts.py`
    * `Documentation/zigux/artifact-diff.md`
    * `Documentation/zigux/phase4-gate-evidence.md`
    * `Documentation/zigux/phase4-kprobe-example-gap-survey.md`
    * `Documentation/zigux/phase4-reversible-delivery-evidence.md`
    * `Documentation/zigux/phase4-test-fsmount-gap-survey.md`
    * `Documentation/zigux/phase4-validation-lane-sequencing.md`
    * `Documentation/zigux/phase4-validation-matrix.md`
    * `Documentation/zigux/review-checklist.md`
    * `Documentation/zigux/README.md`
    * `scripts/zigux/README.md`
    * `zigux/tests/README.md`
    * `zigux/tests/atomic64_diff.zig`
    * `zigux/tests/runtime_atomic64_diff.zig`
    * `zigux/tests/phase4_kprobe_example_manifest.json`
    * `zigux/tests/phase4_kprobe_example_survey.zig`
    * `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`
    * `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`
    * `zigux/tests/bitmap_diff.zig`
    * `zigux/tests/phase4_bitmap_diff_manifest.json`
    * `zigux/tests/phase4_bitmap_diff_survey.zig`
    * `zigux/tests/phase4_bitmap_live_helper_replay.zig`
    * `zigux/tests/phase4_perf_baseline_manifest.json`
    * `zigux/tests/phase4_perf_baseline_survey.zig`
    * `zigux/tests/phase4_test_fsmount_manifest.json`
    * `zigux/tests/phase4_test_fsmount_survey.zig`
    * `zigux/tests/phase4_build.zig`
    * `zigux/Makefile`
    * `scripts/zigux/validate-phase4.py`
    * `.github/workflows/zigux-bootstrap.yml`
  * direct-readback split: this broader matrix packet is still live on current `master`, but the smaller current direct-readback packet stays intentionally narrower until authenticated contents reads recover for the broader build and bitmap companions again; today that direct-readback packet already includes `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-tests-readme-packet.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig`
  * roadmap note: live `master` now carries the roadmap-named Phase 4 entrypoints at `zigux/tests/atomic64_diff.zig` and `zigux/tests/bitmap_diff.zig`, while the manifest-backed `phase4_runtime_atomic64_diff` and `phase4_bitmap_diff` survey packets keep the wrapper-to-runtime atomic64 handoff and the bounded bitmap rollback packet measurable until the still-absent `samples/zigux/kprobe_example.zig` and `samples/zigux/test_fsmount.zig` starters are intentionally opened, the dedicated `zigux/tests/phase4_perf_baseline_manifest.json` plus `zigux/tests/phase4_perf_baseline_survey.zig` packet now keeps the approved local benchmark commands and the approved local-only acceptable limits for both landed rollback gates measurable through a direct local survey route plus the matching Linux-style wrapper without promoting shared CI perf coverage yet, the dedicated validation-lane sequencing note plus checker keep the current shared matrix-side reminder lane split explicit beside the dedicated remaining-gap checker, and the dedicated workflow-route-count checker now keeps that same wrapper inventory reviewable beside `zigux/Makefile` instead of leaving the local replay surface implicit.

## Why this exists

The roadmap says Phase 4 must make future Zigux ports measurable and reversible.

The repo already had the shared Phase 4 build entrypoint, validator wiring, and the bounded host-side `artifact_diff.py` contract replay, but it still needed one reviewable record that names:
  * the bounded rollback owner for each live Phase 4 gate
  * the current perf threshold status for those gates
  * the manifest-backed survey packets that keep the atomic64 wrapper-to-runtime handoff and the bitmap rollback packet measurable
  * the shipped host-side artifact-diff contract packet, the dedicated artifact-diff determinism checker, the dedicated artifact-diff validator-replay checker, the dedicated gate-evidence checker-plus-note packet, the dedicated validation-lane sequencing note plus checker, the direct-readback repo-reality warning and tests-readme packet checkers, the dedicated remaining-gap matrix checker for the parked kprobe, `test_fsmount`, and local-only perf-threshold rows, and the dedicated workflow-route-count checker that the broader validator already depends on
  * the dedicated local perf-baseline survey route that keeps the approved local benchmark commands and the approved local-only acceptable limits for both landed rollback gates machine-checked without treating it as shared CI perf approval
  * the shared review-checklist guardrail that keeps the same Phase 4 packet explicit when reviewers touch it
  * the dedicated reversible-delivery handoff note and pin checker that keep the shared exact-readback packet, the validator-first route inventory, and the dedicated local-only perf packet exact together as the smallest current reversible-delivery evidence set
  * any future shared CI perf-promotion claim must name the Validation and Perf Team as the decision owner and rollback owner, and the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners
  * the remaining roadmap-backed gaps that are still intentionally outside the shipped Phase 4 packet

Without that record, Phase 4 validation exists in code but not yet as a product-facing ownership note.

### `zigux/tests/bitmap_diff.zig`
  * anchor: `lib/test_bitmap.c`
  * phase bucket: `Phase 4 differential validation for the broad bitmap rollback gate`
  * owner: `Shared Subsystems Pod`
  * rollback owner: `Shared Subsystems Pod`
  * implementation note: `zigux/tests/bitmap_diff.zig` remains the roadmap-named synthetic rollback gate and now exact-pins the current range, prefix, zero-length range and prefix no-op rollback checks, copy-tail and zero-length copy invariants, exact `find_nth_bit`, out-of-bounds rejection, manifest-backed source-inventory, and checksum-backed `runThresholdReplay()` checkpoints from the shipped bounded replay, while `zigux/tests/phase4_bitmap_live_helper_replay.zig` keeps the shipped `tools/lib/bitmap.zig` and `tools/lib/find_bit.zig` semantics explicit on the same shared `phase4_build.zig` entrypoint without changing the rollback owner or widening this lane into direct helper implementation ownership
  * fallback path: keep the current C anchor as the source of truth and drop back to the existing broad bitmap parity checks if the Zig replay gate regresses
  * perf threshold status: correctness-only gate today; no hard timing threshold is approved until the lane grows past the current bounded range, prefix, zero-length rollback, copy, `find_nth_bit`, and checksum-pinned threshold-replay checkpoints

## Lab And CI Matrix
  * lane surface purpose owner rollback owner bootstrap CI replay local lab replay threshold posture
  * `zigux/tests/atomic64_diff.zig` bounded runtime atomic64 rollback-readiness replay covering arithmetic, exchange, cmpxchg, add_unless, `inc_not_zero`, `dec_if_positive`, bitwise expectations, and the checksum-backed threshold-replay route shared with `zigux/tests/runtime_atomic64_diff.zig` `ABI and Runtime Team` `ABI and Runtime Team` `python3 scripts/zigux/validate-phase4.py` then `zig build test --build-file zigux/tests/phase4_build.zig` in `.github/workflows/zigux-bootstrap.yml` `zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig` `threshold_pending_until_runtime_atomic64_scope_widens`
  * `zigux/tests/bitmap_diff.zig` bounded broad bitmap rollback-readiness replay covering exact range and prefix cases, zero-length range and prefix no-op rollback checks, copy-tail and zero-length copy invariants, exact `find_nth_bit`, out-of-bounds rejection, manifest-backed source inventory, and checksum-pinned threshold-replay checkpoints `Shared Subsystems Pod` `Shared Subsystems Pod` `python3 scripts/zigux/validate-phase4.py` then `zig build test --build-file zigux/tests/phase4_build.zig` in `.github/workflows/zigux-bootstrap.yml` `zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig` `threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks`
  * `Documentation/zigux/phase4-kprobe-example-gap-survey.md` plus `zigux/tests/phase4_kprobe_example_manifest.json` and `zigux/tests/phase4_kprobe_example_survey.zig` parked sample-gap packet keeping the current C-anchor replay, dedicated local survey wrapper, direct validation entrypoint, and absent-Zig-starter boundary explicit `Validation and Perf Team` `Validation and Perf Team` reviewability only; must stay outside the shared `phase4-test` entrypoint and bootstrap workflow until a later bounded starter lane lands `samples/zigux/kprobe_example.zig` `make -C zigux phase4-kprobe-example-survey` and `zig test zigux/tests/phase4_kprobe_example_survey.zig` `c_anchor_only_until_kprobe_example_starter_lands`
  * `Documentation/zigux/phase4-test-fsmount-gap-survey.md` plus `zigux/tests/phase4_test_fsmount_manifest.json` and `zigux/tests/phase4_test_fsmount_survey.zig` parked sample-gap packet keeping the roadmap-backed C-anchor replay, both local survey wrappers, direct validation entrypoint, explicit no-perf-threshold posture, and absent-Zig-starter boundary explicit `Validation and Perf Team` `Validation and Perf Team` reviewability only; must stay outside the shared `phase4-test` entrypoint and bootstrap workflow until a later bounded validator or starter lane lands `samples/zigux/test_fsmount.zig` `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig` and `make -C zigux phase4-test-fsmount-survey` `reviewability_only_no_perf_threshold`
  * `zigux/tests/phase4_perf_baseline_manifest.json` plus `zigux/tests/phase4_perf_baseline_survey.zig` dedicated local-only perf-baseline survey keeping the approved local benchmark commands and the approved local-only acceptable limits for both landed rollback gates machine-checked without promoting shared CI perf approval `Validation and Perf Team` `Validation and Perf Team` reviewability only; must stay outside the shared `phase4-test` entrypoint until any shared CI perf promotion is intentionally approved `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` and `make -C zigux phase4-perf-baseline-survey` `approved_local_only_for_atomic64_and_bitmap_commands_shared_ci_perf_promotion_pending`

## Local-Only Perf Promotion
  * local-only benchmark commands and acceptable limits are approved today
  * the dedicated perf-baseline survey may keep the approved local benchmark commands and the approved local-only acceptable limits for both landed rollback gates machine-checked
  * must stay outside the shared `phase4-test` entrypoint until any shared CI perf promotion is intentionally approved
  * any future shared CI perf-promotion claim must name the Validation and Perf Team as the decision owner and rollback owner, and the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners
  * promotion rollback owner: `Validation and Perf Team`
  * current replay path: `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` and `make -C zigux phase4-perf-baseline-survey`
  * Validation and Perf Team owning that policy decision keeps the threshold posture bounded to current local evidence rather than shared CI approval.
  * gate owners: `ABI and Runtime Team` and `Shared Subsystems Pod`
  * rollback owners: `ABI and Runtime Team` and `Shared Subsystems Pod`
  * `zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig` approved local-only acceptable limit: `median_elapsed_ns <= 8192` over `4` iterations with `7` monotonic samples
  * `zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig` approved local-only acceptable limit: `median_elapsed_ns <= 12288` over `4` iterations with `7` monotonic samples
  * `python3 scripts/zigux/check-phase4-perf-threshold-matrix.py --self-test` then `python3 scripts/zigux/check-phase4-perf-threshold-matrix.py` keeps those exact local-only acceptable-limit lines fail-closed against the manifest-backed perf packet
  * the dedicated local perf-baseline survey may keep the approved local benchmark commands and the approved local-only acceptable limits for both landed rollback gates machine-checked while the shared promotion decision stays parked in `zigux/tests/phase4_perf_baseline_manifest.json`
  * `python3 scripts/zigux/check-phase4-perf-baseline-packet.py --self-test` then `python3 scripts/zigux/check-phase4-perf-baseline-packet.py` keeps this owner, wrapper, and threshold packet fail-closed against the matrix, the review checklist, the reversible-delivery note, and the scripts-root reminder surface
  * shared CI perf promotion pending remains the correct roadmap-facing posture until a later bounded lane widens this local-only survey packet into broader shared-lab evidence
