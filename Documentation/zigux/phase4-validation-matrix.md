# Phase 4 Validation Matrix
## Status
  * `PHASE4_STATUS=differential_validation_matrix_landed`
  * scope: keep the currently shipped Phase 4 rollback-readiness gates, the host-side artifact-diff contract replay, the dedicated artifact-diff determinism checker, the dedicated exact-readback gate-evidence packet, the dedicated remaining-gap matrix checker, the dedicated workflow-route-count checker, the manifest-backed runtime atomic64 and bitmap rollback survey packets, and the dedicated local perf-baseline posture survey reviewable, name the rollback owners for each bounded gate or survey, and make the current CI and local replay paths explicit
  * current repo reality:
    * `scripts/zigux/artifact_diff.py`
    * `scripts/zigux/check-artifact-diff-contract.py`
    * `scripts/zigux/check-phase4-artifact-diff-determinism.py`
    * `scripts/zigux/check-phase4-gate-evidence.py`
    * `scripts/zigux/check-phase4-remaining-gap-matrix.py`
    * `scripts/zigux/check-phase4-workflow-route-counts.py`
    * `Documentation/zigux/artifact-diff.md`
    * `Documentation/zigux/phase4-gate-evidence.md`
    * `Documentation/zigux/review-checklist.md`
    * `Documentation/zigux/README.md`
    * `scripts/zigux/README.md`
    * `zigux/tests/README.md`
    * `zigux/tests/atomic64_diff.zig`
    * `zigux/tests/runtime_atomic64_diff.zig`
    * `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`
    * `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`
    * `zigux/tests/bitmap_diff.zig`
    * `zigux/tests/phase4_bitmap_diff_manifest.json`
    * `zigux/tests/phase4_bitmap_diff_survey.zig`
    * `zigux/tests/phase4_bitmap_live_helper_replay.zig`
    * `zigux/tests/phase4_perf_baseline_manifest.json`
    * `zigux/tests/phase4_perf_baseline_survey.zig`
    * `zigux/tests/phase4_build.zig`
    * `zigux/Makefile`
    * `scripts/zigux/validate-phase4.py`
    * `.github/workflows/zigux-bootstrap.yml`
  * roadmap note: live `master` now carries the roadmap-named Phase 4 entrypoints at `zigux/tests/atomic64_diff.zig` and `zigux/tests/bitmap_diff.zig`, while the manifest-backed `phase4_runtime_atomic64_diff` and `phase4_bitmap_diff` survey packets keep the wrapper-to-runtime atomic64 handoff and the bounded bitmap rollback packet measurable until the still-absent `samples/zigux/kprobe_example.zig` and `samples/zigux/test_fsmount.zig` starters are intentionally opened, the dedicated `zigux/tests/phase4_perf_baseline_manifest.json` plus `zigux/tests/phase4_perf_baseline_survey.zig` packet now keeps the approved local benchmark commands and the approved local-only acceptable limits for both landed rollback gates measurable through a direct local survey route plus the matching Linux-style wrapper without promoting shared CI perf coverage yet, and the dedicated workflow-route-count checker now keeps that same wrapper inventory reviewable beside `zigux/Makefile` instead of leaving the local replay surface implicit.

## Why this exists

The roadmap says Phase 4 must make future Zigux ports measurable and reversible. The repo already had the shared Phase 4 build entrypoint, validator wiring, and the bounded host-side `artifact_diff.py` contract replay, but it still needed one reviewable record that names:
  * the bounded rollback owner for each live Phase 4 gate
  * the current perf threshold status for those gates
  * the manifest-backed survey packets that keep the atomic64 wrapper-to-runtime handoff and the bitmap rollback packet measurable
  * the shipped host-side artifact-diff contract packet, the dedicated artifact-diff determinism checker, the dedicated gate-evidence checker-plus-note packet, the dedicated remaining-gap matrix checker for the parked kprobe, `test_fsmount`, and local-only perf-threshold rows, and the dedicated workflow-route-count checker that the broader validator already depends on
  * the dedicated local perf-baseline survey route that keeps the approved local benchmark commands and the approved local-only acceptable limits for both landed rollback gates machine-checked without treating it as shared CI perf approval
  * the shared review-checklist guardrail that keeps the same Phase 4 packet explicit when reviewers touch it
  * the remaining roadmap-backed gaps that are still intentionally outside the shipped Phase 4 packet

Without that record, Phase 4 validation exists in code but not yet as a product-facing ownership note.

## Gate Ownership
### `scripts/zigux/check-artifact-diff-contract.py`
  * anchor: `scripts/zigux/artifact_diff.py`
  * phase bucket: `Phase 4 host-side differential-validation tooling contract replay`
  * owner: `Tooling and Validation Team`
  * rollback owner: `Tooling and Validation Team`
  * implementation note: `scripts/zigux/check-artifact-diff-contract.py` reruns the shipped CLI missing-required-args, missing-actual-operand, invalid-mode, text, JSON, SHA-256, missing-path, malformed-input, and repeat-run determinism cases through the outward `scripts/zigux/artifact_diff.py` CLI so the shared host-side helper contract stays reviewable before the broader Phase 4 validator and Zig rollback gates run
  * fallback path: keep `Documentation/zigux/artifact-diff.md` plus the current helper self-test as the truthful contract record if the direct CLI replay regresses until the outward checker is repaired
  * perf threshold status: reviewability-only gate today; there is no timing claim on the host-side helper contract packet

### `scripts/zigux/check-phase4-artifact-diff-determinism.py`
  * anchor: `scripts/zigux/artifact_diff.py` and `scripts/zigux/check-artifact-diff-contract.py`
  * phase bucket: `Phase 4 host-side differential-validation tooling determinism catalog replay`
  * owner: `Tooling and Validation Team`
  * rollback owner: `Tooling and Validation Team`
  * implementation note: `scripts/zigux/check-phase4-artifact-diff-determinism.py` reruns the helper self-test summary, the contract self-test summary, the base-case catalog, the repeat-case catalog, and the full contract catalog together with the required `Documentation/zigux/artifact-diff.md` Phase 4 markers so helper, checker, and review-note case-count or case-order drift fails closed before the broader Phase 4 validator and Zig rollback gates run
  * fallback path: keep `Documentation/zigux/artifact-diff.md`, `scripts/zigux/check-artifact-diff-contract.py`, and the current helper `--self-test` packet as the truthful deterministic catalog record if the dedicated catalog checker regresses until that narrower gate is repaired
  * perf threshold status: reviewability-only gate today; there is no timing claim on the deterministic catalog packet

### `scripts/zigux/check-phase4-gate-evidence.py`
  * anchor: `Documentation/zigux/phase4-gate-evidence.md`
  * phase bucket: `Phase 4 rollback-ownership and lab-matrix exact-readback gate`
  * owner: `Tooling and Validation Team`
  * rollback owner: `Tooling and Validation Team`
  * implementation note: `scripts/zigux/check-phase4-gate-evidence.py` reruns the shipped exact-readback note against the current narrower packet, exact-counting the validator-backed blob pins, the manifest-backed runtime atomic64 survey pair, the bitmap rollback survey pair, the helper-backed bitmap replay command plus its shared ownership and threshold-posture anchors, the adjacent parked kprobe and `test_fsmount` gap packets, and the still-absent `samples/zigux/kprobe_example.zig` plus `samples/zigux/test_fsmount.zig` starter flags before the broader Phase 4 validator and Zig rollback gates continue
  * fallback path: keep `Documentation/zigux/phase4-gate-evidence.md` plus the current validator-backed packet as the truthful exact-readback record if the dedicated checker regresses until that narrower gate is repaired
  * perf threshold status: reviewability-only gate today; there is no timing claim on the exact-readback packet

### `scripts/zigux/check-phase4-remaining-gap-matrix.py`
  * anchor: `Documentation/zigux/phase4-validation-matrix.md`
  * phase bucket: `Phase 4 parked starter and local-only perf remaining-gap matrix`
  * owner: `Tooling and Validation Team`
  * rollback owner: `Tooling and Validation Team`
  * implementation note: `scripts/zigux/check-phase4-remaining-gap-matrix.py` reruns the remaining roadmap-gap rows for `samples/zigux/kprobe_example.zig`, `samples/zigux/test_fsmount.zig`, and the local-only perf-threshold packet, exact-checking the dedicated local survey wrappers, validation entrypoints, owner and rollback-owner wording, and the still-local-only perf-promotion posture before the broader Phase 4 validator and Zig rollback gates continue
  * fallback path: keep `Documentation/zigux/phase4-validation-matrix.md` truthful about the parked starter gaps and the local-only perf-threshold policy if the dedicated remaining-gap checker regresses until that narrower gate is repaired
  * perf threshold status: reviewability-only gate today; it checks gap ownership, wrapper, and promotion-posture wording rather than claiming direct timing coverage

### `scripts/zigux/check-phase4-workflow-route-counts.py`
  * anchor: `zigux/Makefile` and `.github/workflows/zigux-bootstrap.yml`
  * phase bucket: `Phase 4 validator-first wrapper-route inventory gate`
  * owner: `Tooling and Validation Team`
  * rollback owner: `Tooling and Validation Team`
  * implementation note: `scripts/zigux/check-phase4-workflow-route-counts.py` keeps the current `phase4-validate`, `phase4-test`, `phase4-runtime-atomic64-diff`, `phase4-runtime-atomic64-diff-survey`, `phase4-bitmap-diff`, `phase4-bitmap-diff-survey`, `phase4-bitmap-live-helper-replay`, `phase4-perf-baseline-survey`, `phase4-kprobe-example-survey`, `phase4-test-fsmount-survey`, and aggregate `phase4` wrapper routes aligned across `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, and the broader validator packet so local replay-surface drift fails closed before the Zig rollback gates continue
  * fallback path: keep `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, and `scripts/zigux/README.md` truthful about the current wrapper inventory if the dedicated route-count checker regresses until that narrower gate is repaired
  * perf threshold status: reviewability-only gate today; there is no timing claim on the wrapper-route inventory packet

### `zigux/tests/atomic64_diff.zig`
  * anchor: `lib/atomic64_test.c`
  * phase bucket: `Phase 4 differential validation via the current live atomic64 replay gate`
  * owner: `ABI and Runtime Team`
  * rollback owner: `ABI and Runtime Team`
  * implementation note: `zigux/tests/atomic64_diff.zig` imports `zigux/tests/runtime_atomic64_diff.zig` so Phase 4 keeps the roadmap path without cloning the shared runtime-backed replay logic that Phase 9 already reuses directly
  * survey packet: `zigux/tests/phase4_runtime_atomic64_diff_manifest.json` and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` keep the wrapper-to-runtime handoff, the shared build wiring, and the matrix wording reviewable beside the executable replay
  * fallback path: keep the current C anchor plus the existing Phase 9 runtime atomic64 starter surface as the source of truth if the Zig replay gate regresses
  * perf threshold status: correctness-only gate today; no hard timing threshold is approved until the lane widens beyond the current bounded exchange, cmpxchg, add_unless, bitwise, and selftest-family replay set

### `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`
  * anchor: `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`
  * phase bucket: `Phase 4 reviewability survey for the runtime atomic64 wrapper handoff`
  * owner: `ABI and Runtime Team`
  * rollback owner: `ABI and Runtime Team`
  * implementation note: the survey keeps `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/phase4_build.zig`, `scripts/zigux/validate-phase4.py`, `Documentation/zigux/review-checklist.md`, and this matrix aligned around the same bounded wrapper-first handoff
  * fallback path: keep the wrapper, the runtime replay body, and this matrix as the source of truth and remove the survey from the shared Phase 4 build entrypoint if the manifest drifts
  * perf threshold status: reviewability-only survey today; it inherits `threshold_pending_until_runtime_atomic64_scope_widens`

### `zigux/tests/bitmap_diff.zig`
  * anchor: `lib/test_bitmap.c`
  * phase bucket: `Phase 4 differential validation for the broad bitmap rollback gate`
  * owner: `Shared Subsystems Pod`
  * rollback owner: `Shared Subsystems Pod`
  * implementation note: `zigux/tests/bitmap_diff.zig` remains the roadmap-named synthetic rollback gate and now exact-pins the current range, prefix, copy-tail, exact `find_nth_bit`, out-of-bounds rejection, manifest-backed source-inventory, and checksum-backed `runThresholdReplay()` checkpoints from the shipped bounded replay, while `zigux/tests/phase4_bitmap_live_helper_replay.zig` keeps the shipped `tools/lib/bitmap.zig` and `tools/lib/find_bit.zig` semantics explicit on the same shared `phase4_build.zig` entrypoint without changing the rollback owner or widening this lane into direct helper implementation ownership
  * fallback path: keep the current C anchor as the source of truth and drop back to the existing broad bitmap parity checks if the Zig replay gate regresses
  * perf threshold status: correctness-only gate today; no hard timing threshold is approved until the lane grows past the current bounded range, prefix, copy, `find_nth_bit`, and checksum-pinned threshold-replay checkpoints

### `zigux/tests/phase4_bitmap_diff_survey.zig`
  * anchor: `zigux/tests/phase4_bitmap_diff_manifest.json`
  * phase bucket: `Phase 4 reviewability survey for the bitmap rollback gate`
  * owner: `Shared Subsystems Pod`
  * rollback owner: `Shared Subsystems Pod`
  * implementation note: the survey keeps `zigux/tests/bitmap_diff.zig`, `zigux/tests/phase4_bitmap_live_helper_replay.zig`, `zigux/tests/phase4_build.zig`, `Documentation/zigux/phase4-gate-evidence.md`, and this matrix aligned around the same bounded bitmap rollback packet without widening the lane into sample work or perf-threshold approval
  * fallback path: keep `zigux/tests/bitmap_diff.zig`, `zigux/tests/phase4_bitmap_live_helper_replay.zig`, and this matrix as the truthful rollback surface and remove the survey from the shared Phase 4 build entrypoint if the manifest drifts
  * perf threshold status: reviewability-only survey today; it inherits `threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks`

### `zigux/tests/phase4_bitmap_live_helper_replay.zig`
  * anchor: `tools/lib/bitmap.zig` and `tools/lib/find_bit.zig`
  * phase bucket: `Phase 4 helper-backed bitmap rollback replay`
  * owner: `Shared Subsystems Pod`
  * rollback owner: `Shared Subsystems Pod`
  * implementation note: the helper-backed replay keeps the shipped bitmap and find-bit helper semantics explicit on the shared `zigux/tests/phase4_build.zig` entrypoint, so the rollback-ready bitmap lane can prove the live helper path without widening Phase 4 into broader helper implementation ownership or a new perf-claim packet
  * fallback path: keep `zigux/tests/bitmap_diff.zig`, the current C anchor at `lib/test_bitmap.c`, and the shipped helper sources as the truthful rollback surface if the helper-backed replay regresses and has to leave the shared Phase 4 entrypoint
  * perf threshold status: correctness-only gate today; it inherits `threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks`

### `zigux/tests/phase4_perf_baseline_survey.zig`
  * anchor: `zigux/tests/atomic64_diff.zig` and `zigux/tests/bitmap_diff.zig`
  * phase bucket: `Phase 4 dedicated perf-baseline posture survey`
  * owner: `Validation and Perf Team`
  * rollback owner: `Validation and Perf Team`
  * implementation note: `zigux/tests/phase4_perf_baseline_survey.zig` and `zigux/tests/phase4_perf_baseline_manifest.json` keep the approved local benchmark commands and the approved local-only acceptable limits for both shipped rollback gates explicit across the two shipped rollback gates, and keep the dedicated survey outside the shared `phase4-test` entrypoint until any shared CI perf promotion is intentionally approved
  * fallback path: keep this matrix truthful about the current local-only perf posture and drop the dedicated survey step from `zigux/tests/phase4_build.zig` if the survey packet drifts until it is repaired
  * perf threshold status: local-only benchmark commands and acceptable limits are approved today, while broader shared CI perf promotion still remains pending under `perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land`

## Lab And CI Matrix
  * lane surface purpose owner rollback owner bootstrap CI replay local lab replay threshold posture
  * `scripts/zigux/check-artifact-diff-contract.py` bounded host-side `artifact_diff.py` CLI contract replay for missing-required-args, missing-actual-operand, invalid-mode, text, JSON, SHA-256, missing-path, malformed-input, and repeat-run determinism `Tooling and Validation Team` `Tooling and Validation Team` `python3 scripts/zigux/validate-phase4.py` in `.github/workflows/zigux-bootstrap.yml`, which reruns the contract checker before the Zig gates `python3 scripts/zigux/check-artifact-diff-contract.py` then `python3 scripts/zigux/validate-phase4.py` `reviewability_only_no_perf_threshold`
  * `scripts/zigux/check-phase4-artifact-diff-determinism.py` bounded host-side catalog replay for the helper self-test summary, the contract self-test summary, the base-case catalog, the repeat-case catalog, and the full contract catalog, together with the required `Documentation/zigux/artifact-diff.md` Phase 4 review-note markers `Tooling and Validation Team` `Tooling and Validation Team` `python3 scripts/zigux/validate-phase4.py` in `.github/workflows/zigux-bootstrap.yml`, which reruns the determinism checker before the Zig gates `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test` then `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py` then `python3 scripts/zigux/validate-phase4.py` `reviewability_only_no_perf_threshold`
  * `scripts/zigux/check-phase4-gate-evidence.py` dedicated exact-readback replay for the shipped rollback-ownership note, validator-backed blob pins, the runtime atomic64 manifest-backed survey pair, the bitmap rollback survey pair, the helper-backed bitmap replay command plus its shared ownership and threshold-posture anchors, the adjacent parked kprobe and `test_fsmount` gap packets, and the still-absent `samples/zigux/kprobe_example.zig` plus `samples/zigux/test_fsmount.zig` starter flags `Tooling and Validation Team` `Tooling and Validation Team` `python3 scripts/zigux/validate-phase4.py` in `.github/workflows/zigux-bootstrap.yml`, which reruns the gate-evidence checker before the Zig gates `python3 scripts/zigux/check-phase4-gate-evidence.py --self-test` then `python3 scripts/zigux/check-phase4-gate-evidence.py` then `python3 scripts/zigux/validate-phase4.py` `reviewability_only_no_perf_threshold`
  * `scripts/zigux/check-phase4-remaining-gap-matrix.py` dedicated remaining-gap matrix replay for the parked `samples/zigux/kprobe_example.zig` and `samples/zigux/test_fsmount.zig` starter rows plus the local-only perf-threshold decision row `Tooling and Validation Team` `Tooling and Validation Team` `python3 scripts/zigux/validate-phase4.py` in `.github/workflows/zigux-bootstrap.yml`, which reruns the remaining-gap checker before the Zig gates `python3 scripts/zigux/check-phase4-remaining-gap-matrix.py --self-test` then `python3 scripts/zigux/check-phase4-remaining-gap-matrix.py` then `python3 scripts/zigux/validate-phase4.py` `reviewability_only_no_perf_threshold`
  * `scripts/zigux/check-phase4-workflow-route-counts.py` bounded validator-first wrapper-route inventory replay for the shared `phase4-validate`, shared `phase4-test`, atomic64, runtime atomic64 survey, bitmap, bitmap survey, helper-backed bitmap replay, perf-baseline survey, kprobe gap survey, test_fsmount gap survey, and aggregate `phase4` Linux-style wrapper routes `Tooling and Validation Team` `Tooling and Validation Team` `python3 scripts/zigux/validate-phase4.py` in `.github/workflows/zigux-bootstrap.yml`, which reruns the route-count checker before the Zig gates `python3 scripts/zigux/check-phase4-workflow-route-counts.py` then `python3 scripts/zigux/validate-phase4.py` `reviewability_only_no_perf_threshold`
  * `zigux/tests/atomic64_diff.zig` bounded atomic64 exchange, cmpxchg, add_unless, bitwise, and selftest-family replay via the shared runtime-backed gate `ABI and Runtime Team` `ABI and Runtime Team` `python3 scripts/zigux/validate-phase4.py` then `zig build test --build-file zigux/tests/phase4_build.zig` in `.github/workflows/zigux-bootstrap.yml` `zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig` `threshold_pending_until_runtime_atomic64_scope_widens`
  * `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` manifest-backed survey that keeps the wrapper, runtime replay body, validator, matrix, and reviewer checklist aligned around the same bounded atomic64 handoff `ABI and Runtime Team` `ABI and Runtime Team` `python3 scripts/zigux/validate-phase4.py` then `zig build test --build-file zigux/tests/phase4_build.zig` in `.github/workflows/zigux-bootstrap.yml` `zig build phase4-runtime-atomic64-diff-survey --build-file zigux/tests/phase4_build.zig` `threshold_pending_until_runtime_atomic64_scope_widens`
  * `zigux/tests/bitmap_diff.zig` bounded broad bitmap rollback-readiness replay covering exact range and prefix cases, copy-tail cases, exact `find_nth_bit`, out-of-bounds rejection, manifest-backed source inventory, and checksum-pinned threshold-replay checkpoints `Shared Subsystems Pod` `Shared Subsystems Pod` `python3 scripts/zigux/validate-phase4.py` then `zig build test --build-file zigux/tests/phase4_build.zig` in `.github/workflows/zigux-bootstrap.yml` `zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig` `threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks`
  * `zigux/tests/phase4_bitmap_diff_survey.zig` manifest-backed survey that keeps the bitmap rollback gate, helper-backed replay, build wiring, and gate-evidence contract reviewable on the same shared Phase 4 entrypoint `Shared Subsystems Pod` `Shared Subsystems Pod` `python3 scripts/zigux/validate-phase4.py` then `zig build test --build-file zigux/tests/phase4_build.zig` in `.github/workflows/zigux-bootstrap.yml` `zig build phase4-bitmap-diff-survey --build-file zigux/tests/phase4_build.zig` `threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks`
  * `zigux/tests/phase4_bitmap_live_helper_replay.zig` helper-backed replay of the shipped `tools/lib/bitmap.zig` and `tools/lib/find_bit.zig` semantics on the shared Phase 4 entrypoint `Shared Subsystems Pod` `Shared Subsystems Pod` `python3 scripts/zigux/validate-phase4.py` then `zig build test --build-file zigux/tests/phase4_build.zig` in `.github/workflows/zigux-bootstrap.yml` `zig build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig` `threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks`
  * `zigux/tests/phase4_perf_baseline_survey.zig` dedicated local survey that keeps the approved local benchmark commands and the approved local-only acceptable limits machine-checked for both landed rollback gates `Validation and Perf Team` `Validation and Perf Team` not on the shared workflow or validator packet yet; keep this survey local until any shared CI perf promotion is intentionally approved `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` or `make -C zigux phase4-perf-baseline-survey` `local_only_commands_and_limits_approved_shared_ci_perf_promotion_pending`
  * The shared `zigux/tests/phase4_build.zig` entrypoint still runs `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` and `zigux/tests/phase4_bitmap_diff_survey.zig` beside `zigux/tests/atomic64_diff.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` so the manifest-backed wrapper handoff, the bitmap rollback survey packet, and the shipped helper-backed bitmap semantics stay reviewable on the same bounded Phase 4 replay surface.
The dedicated perf-baseline survey stays outside the shared `phase4-test` entrypoint and the validator-backed gate-evidence packet until any shared CI perf promotion is intentionally approved.
The shipped `zigux/Makefile` wrapper surface stays inside that same bounded packet through `scripts/zigux/check-phase4-workflow-route-counts.py`, so local replay-route drift cannot quietly split away from the validator-first contract when the adjacent surveys or parked gap wrappers move again.

## Remaining Roadmap Gaps
### `samples/zigux/kprobe_example.zig`
  * current C anchor: `samples/kprobes/kprobe_example.c`
  * current replay path: `make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m`
  * explicit local lab replay marker: `make -C zigux phase4-kprobe-example-survey`
  * dedicated local survey wrapper: `make -C zigux phase4-kprobe-example-survey`
  * validation entrypoint: `zig test zigux/tests/phase4_kprobe_example_survey.zig`
  * survey owner: `Validation and Perf Team`
  * rollback owner: `Validation and Perf Team`
  * current measurable status: absent on current `master`; the dedicated parked gap packet at `Documentation/zigux/phase4-kprobe-example-gap-survey.md`, `zigux/tests/phase4_kprobe_example_manifest.json`, and `zigux/tests/phase4_kprobe_example_survey.zig` now keeps the current C anchor, replay command, explicit local lab replay marker, dedicated local survey wrapper, direct validation entrypoint, owner, and rollback owner reviewable, and the shared exact-readback packet at `Documentation/zigux/phase4-gate-evidence.md` plus `scripts/zigux/check-phase4-gate-evidence.py` now keep that same adjacent survey note, manifest, replay command, explicit local lab replay marker, direct validation entrypoint, and local survey wrapper machine-checkable without claiming a shipped Zig starter
  * next bounded evidence step: keep the dedicated parked survey packet, the explicit local lab replay marker, the dedicated local survey wrapper, and the current shared exact-readback coverage adjacent to the shared Phase 4 gate-evidence note until a later bounded lane intentionally opens either the Zig starter itself or a broader replay promotion beyond today's parked-gap packet

### `samples/zigux/test_fsmount.zig`
  * current C anchor: `samples/vfs/test-fsmount.c`
  * current replay path: `make M=samples/vfs`
  * dedicated local survey wrapper: `make -C zigux phase4-test-fsmount-survey`
  * validation entrypoint: `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`
  * survey owner: `Validation and Perf Team`
  * rollback owner: `Validation and Perf Team`
  * current measurable status: absent on current `master`; the dedicated parked gap packet at `Documentation/zigux/phase4-test-fsmount-gap-survey.md`, `zigux/tests/phase4_test_fsmount_manifest.json`, and `zigux/tests/phase4_test_fsmount_survey.zig`, together with the dedicated local survey wrapper `make -C zigux phase4-test-fsmount-survey` and the direct validation entrypoint at `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`, now keeps the current C anchor, replay command, owner, rollback owner, and the explicit reviewability-only no-perf-threshold posture reviewable, and the packet now stays under the shared exact-readback checker while still remaining outside the shared `phase4-test` target set until a later bounded promotion lands
  * next bounded evidence step: keep the dedicated parked survey packet, the Linux-style survey wrapper `make -C zigux phase4-test-fsmount-survey`, the direct validation entrypoint `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`, and the explicit reviewability-only no-perf-threshold posture adjacent to the shared Phase 4 exact-readback packet while the current validator and gate-evidence checker continue to carry that same note, manifest, replay commands, and threshold posture without claiming a shipped Zig starter; if that same-family follow-through still stays below starter work, land one focused promotion that widens the local survey packet or shared replay surface rather than reopening measurability wording alone

### `Phase 4 perf thresholds`
  * current gate anchors: `zigux/tests/atomic64_diff.zig` and `zigux/tests/bitmap_diff.zig`
  * current replay path: `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` and `make -C zigux phase4-perf-baseline-survey`
  * gate owners: `ABI and Runtime Team` and `Shared Subsystems Pod`
  * rollback owners: `ABI and Runtime Team` and `Shared Subsystems Pod`
  * current benchmark-command status: the dedicated survey packet at `zigux/tests/phase4_perf_baseline_manifest.json` and `zigux/tests/phase4_perf_baseline_survey.zig`, together with the matching Linux-style wrapper `make -C zigux phase4-perf-baseline-survey`, is now shipped, the local benchmark commands are approved for both landed gates, and the dedicated survey intentionally keeps that posture local rather than treating it as shared CI perf coverage
  * current acceptable-limit status: the dedicated survey packet now carries approved local-only acceptable limits for both atomic64 and bitmap, and shared CI perf coverage is still not claimed
  * next bounded evidence step: keep the current local-only acceptable limits survey-only until a later bounded lane intentionally decides whether the existing bounds should stay local-only or support a broader shared CI perf-coverage claim, with the Validation and Perf Team owning that policy decision in coordination with the ABI and Runtime Team and Shared Subsystems Pod as the current gate rollback owners so the validator-first packet does not widen by accident. This matrix, `scripts/zigux/validate-phase4.py`, the dedicated workflow-route-count checker, `zigux/Makefile`, and the shared `zigux/tests/phase4_build.zig` entrypoint should stay aligned around the still-correctness-only shared replay routes while the dedicated perf-baseline survey keeps the approved local benchmark commands and the approved local-only acceptable limits for both rollback gates explicit until a later Phase 4 lane intentionally decides whether any broader shared perf promotion belongs in the shipped packet.

## Review Rules
  * Phase 4 remains a rollback-readiness lane first, not a performance-claim lane
  * the dedicated perf-baseline survey may keep the approved local benchmark commands and the approved local-only acceptable limits for both landed rollback gates machine-checked, but it must stay outside the shared `phase4-test` entrypoint until any shared CI perf promotion is intentionally approved
  * any future shared CI perf-promotion claim must name the Validation and Perf Team as the decision owner and the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners before the shared packet stops calling the approved acceptable limits local-only
  * any future hard timing threshold must name the benchmark command, acceptable limit, owner, and rollback owner in this record before the lane claims perf coverage
  * if the shared runtime backing regresses, repair `zigux/tests/runtime_atomic64_diff.zig` or remove `zigux/tests/atomic64_diff.zig` and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` from the shared Phase 4 entrypoint until the runtime-backed replay is honest again
  * if the bitmap reviewability survey regresses, repair `zigux/tests/phase4_bitmap_diff_manifest.json` and `zigux/tests/phase4_bitmap_diff_survey.zig` or remove that survey from the shared Phase 4 entrypoint until the bitmap rollback packet is honest again
  * if either gate regresses, the rollback owner must keep the current C anchor and the existing Phase 4 documentation truthful while the Zig replay gate is repaired or removed from the shared entrypoint
  * if the host-side helper contract regresses, the rollback owner must keep `Documentation/zigux/artifact-diff.md` and the direct `artifact_diff.py` self-test truthful while the outward CLI replay is repaired or removed from the shared validator path
  * if the remaining-roadmap-gap matrix checker regresses, repair `scripts/zigux/check-phase4-remaining-gap-matrix.py` or keep the parked kprobe, parked `test_fsmount`, and local-only perf-threshold rows in this matrix truthful until that narrower gate is honest again
  * if the wrapper-route inventory regresses, repair `scripts/zigux/check-phase4-workflow-route-counts.py` or `zigux/Makefile`, or remove the stale wrapper from the validator-first Phase 4 packet until the local replay surface is honest again
