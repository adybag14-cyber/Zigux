# Phase 4 Validation Matrix

This document records the live Phase 4 differential-validation ownership and replay matrix.

## Status
- `PHASE4_STATUS=differential_validation_matrix_landed`
- scope: keep the currently shipped Phase 4 rollback-readiness gates, the host-side artifact-diff contract replay, the dedicated exact-readback gate-evidence packet, and the manifest-backed runtime atomic64 handoff survey reviewable, name the rollback owners for each bounded gate or survey, and make the current CI and local replay paths explicit
- current repo reality:
  - `scripts/zigux/artifact_diff.py`
  - `scripts/zigux/check-artifact-diff-contract.py`
  - `scripts/zigux/check-phase4-gate-evidence.py`
  - `Documentation/zigux/artifact-diff.md`
  - `Documentation/zigux/phase4-gate-evidence.md`
  - `Documentation/zigux/README.md`
  - `scripts/zigux/README.md`
  - `zigux/tests/README.md`
  - `zigux/tests/atomic64_diff.zig`
  - `zigux/tests/runtime_atomic64_diff.zig`
  - `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`
  - `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`
  - `zigux/tests/bitmap_diff.zig`
  - `zigux/tests/phase4_bitmap_live_helper_replay.zig`
  - `zigux/tests/phase4_build.zig`
  - `scripts/zigux/validate-phase4.py`
  - `.github/workflows/zigux-bootstrap.yml`
- roadmap note: live `master` now carries the roadmap-named Phase 4 entrypoints at `zigux/tests/atomic64_diff.zig` and `zigux/tests/bitmap_diff.zig`, while the manifest-backed `phase4_runtime_atomic64_diff` survey packet keeps the wrapper-to-runtime atomic64 handoff measurable until the still-absent `samples/zigux/kprobe_example.zig` and `samples/zigux/test_fsmount.zig` follow-up work is intentionally opened, and `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` keep that validator-first packet visible from the three shared root summaries

## Why this exists

The roadmap says Phase 4 must make future Zigux ports measurable and reversible. The repo already had the shared Phase 4 build entrypoint, validator wiring, and the bounded host-side `artifact_diff.py` contract replay, but it still needed one reviewable record that names:
- the bounded rollback owner for each live Phase 4 gate
- the current perf threshold status for those gates
- the manifest-backed survey packet that keeps the atomic64 wrapper-to-runtime handoff measurable
- the shipped host-side artifact-diff contract packet and the dedicated gate-evidence checker-plus-note packet that the broader validator already depends on
- the remaining roadmap-backed gaps that are still intentionally outside the shipped Phase 4 packet

Without that record, Phase 4 validation exists in code but not yet as a product-facing ownership note.

## Gate Ownership

### `scripts/zigux/check-artifact-diff-contract.py`
- anchor: `scripts/zigux/artifact_diff.py`
- phase bucket: `Phase 4 host-side differential-validation tooling contract replay`
- owner: `Tooling and Validation Team`
- rollback owner: `Tooling and Validation Team`
- implementation note: `scripts/zigux/check-artifact-diff-contract.py` reruns the shipped text, JSON, SHA-256, missing-path, malformed-input, and repeat-run determinism cases through the outward `scripts/zigux/artifact_diff.py` CLI so the shared host-side helper contract stays reviewable before the broader Phase 4 validator and Zig rollback gates run
- fallback path: keep `Documentation/zigux/artifact-diff.md` plus the current helper self-test as the truthful contract record if the direct CLI replay regresses until the outward checker is repaired
- perf threshold status: reviewability-only gate today; there is no timing claim on the host-side helper contract packet

### `scripts/zigux/check-phase4-gate-evidence.py`
- anchor: `Documentation/zigux/phase4-gate-evidence.md`
- phase bucket: `Phase 4 rollback-ownership and lab-matrix exact-readback gate`
- owner: `Tooling and Validation Team`
- rollback owner: `Tooling and Validation Team`
- implementation note: `scripts/zigux/check-phase4-gate-evidence.py` reruns the shipped exact-readback note against the current narrower packet, exact-counting the validator-backed blob pins, the manifest-backed runtime atomic64 survey pair, and the still-absent sample and perf-baseline packet flags before the broader Phase 4 validator and Zig rollback gates continue
- fallback path: keep `Documentation/zigux/phase4-gate-evidence.md` plus the current validator-backed packet as the truthful exact-readback record if the dedicated checker regresses until that narrower gate is repaired
- perf threshold status: reviewability-only gate today; there is no timing claim on the exact-readback packet

### `zigux/tests/atomic64_diff.zig`
- anchor: `lib/atomic64_test.c`
- phase bucket: `Phase 4 differential validation via the current live atomic64 replay gate`
- owner: `ABI and Runtime Team`
- rollback owner: `ABI and Runtime Team`
- implementation note: `zigux/tests/atomic64_diff.zig` imports `zigux/tests/runtime_atomic64_diff.zig` so Phase 4 keeps the roadmap path without cloning the shared runtime-backed replay logic that Phase 9 already reuses directly
- survey packet: `zigux/tests/phase4_runtime_atomic64_diff_manifest.json` and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` keep the wrapper-to-runtime handoff, the shared build wiring, and the matrix wording reviewable beside the executable replay
- fallback path: keep the current C anchor plus the existing Phase 9 runtime atomic64 starter surface as the source of truth if the Zig replay gate regresses
- perf threshold status: correctness-only gate today; no hard timing threshold is approved until the lane widens beyond the current bounded exchange, cmpxchg, add_unless, and selftest-family replay set

### `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`
- anchor: `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`
- phase bucket: `Phase 4 reviewability survey for the runtime atomic64 wrapper handoff`
- owner: `ABI and Runtime Team`
- rollback owner: `ABI and Runtime Team`
- implementation note: the survey keeps `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/phase4_build.zig`, `scripts/zigux/validate-phase4.py`, and this matrix aligned around the same bounded wrapper-first handoff
- fallback path: keep the wrapper, the runtime replay body, and this matrix as the source of truth and remove the survey from the shared Phase 4 build entrypoint if the manifest drifts
- perf threshold status: reviewability-only survey today; it inherits `threshold_pending_until_runtime_atomic64_scope_widens`

### `zigux/tests/bitmap_diff.zig`
- anchor: `lib/test_bitmap.c`
- phase bucket: `Phase 4 differential validation for the broad bitmap rollback gate`
- owner: `Shared Subsystems Pod`
- rollback owner: `Shared Subsystems Pod`
- implementation note: `zigux/tests/bitmap_diff.zig` remains the roadmap-named synthetic rollback gate, while `zigux/tests/phase4_bitmap_live_helper_replay.zig` keeps the shipped `tools/lib/bitmap.zig` and `tools/lib/find_bit.zig` semantics explicit on the same shared `phase4_build.zig` entrypoint without changing the rollback owner or widening this lane into direct helper implementation ownership
- fallback path: keep the current C anchor as the source of truth and drop back to the existing broad bitmap parity checks if the Zig replay gate regresses
- perf threshold status: correctness-only gate today; no hard timing threshold is approved until the lane grows past the current bounded range, prefix, and copy-behavior checkpoints

### `zigux/tests/phase4_bitmap_live_helper_replay.zig`
- anchor: `tools/lib/bitmap.zig` and `tools/lib/find_bit.zig`
- phase bucket: `Phase 4 helper-backed bitmap rollback replay`
- owner: `Shared Subsystems Pod`
- rollback owner: `Shared Subsystems Pod`
- implementation note: the helper-backed replay keeps the shipped bitmap and find-bit helper semantics explicit on the shared `zigux/tests/phase4_build.zig` entrypoint, so the rollback-ready bitmap lane can prove the live helper path without widening Phase 4 into broader helper implementation ownership or a new perf-claim packet
- fallback path: keep `zigux/tests/bitmap_diff.zig`, the current C anchor at `lib/test_bitmap.c`, and the shipped helper sources as the truthful rollback surface if the helper-backed replay regresses and has to leave the shared Phase 4 entrypoint
- perf threshold status: correctness-only gate today; it inherits `threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks`

## Lab And CI Matrix

lane surface purpose owner rollback owner bootstrap CI replay local lab replay threshold posture
`scripts/zigux/check-artifact-diff-contract.py` bounded host-side `artifact_diff.py` CLI contract replay for text, JSON, SHA-256, missing-path, malformed-input, and repeat-run determinism `Tooling and Validation Team` `Tooling and Validation Team` `python3 scripts/zigux/validate-phase4.py` in `.github/workflows/zigux-bootstrap.yml`, which reruns the contract checker before the Zig gates `python3 scripts/zigux/check-artifact-diff-contract.py` then `python3 scripts/zigux/validate-phase4.py` `reviewability_only_no_perf_threshold`
`scripts/zigux/check-phase4-gate-evidence.py` dedicated exact-readback replay for the shipped rollback-ownership note, validator-backed blob pins, the runtime atomic64 manifest-backed survey pair, and the still-absent sample and perf-baseline packet flags `Tooling and Validation Team` `Tooling and Validation Team` `python3 scripts/zigux/validate-phase4.py` in `.github/workflows/zigux-bootstrap.yml`, which reruns the gate-evidence checker before the Zig gates `python3 scripts/zigux/check-phase4-gate-evidence.py` then `python3 scripts/zigux/validate-phase4.py` `reviewability_only_no_perf_threshold`
`zigux/tests/atomic64_diff.zig` bounded atomic64 exchange, cmpxchg, add_unless, and selftest-family replay via the shared runtime-backed gate `ABI and Runtime Team` `ABI and Runtime Team` `python3 scripts/zigux/validate-phase4.py` then `zig build test --build-file zigux/tests/phase4_build.zig` in `.github/workflows/zigux-bootstrap.yml` `zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig` `threshold_pending_until_runtime_atomic64_scope_widens`
`zigux/tests/phase4_runtime_atomic64_diff_survey.zig` manifest-backed survey that keeps the wrapper, runtime replay body, validator, and matrix aligned around the same bounded atomic64 handoff `ABI and Runtime Team` `ABI and Runtime Team` `python3 scripts/zigux/validate-phase4.py` then `zig build test --build-file zigux/tests/phase4_build.zig` in `.github/workflows/zigux-bootstrap.yml` `zig build phase4-runtime-atomic64-diff-survey --build-file zigux/tests/phase4_build.zig` `threshold_pending_until_runtime_atomic64_scope_widens`
`zigux/tests/bitmap_diff.zig` bounded broad bitmap rollback-readiness replay `Shared Subsystems Pod` `Shared Subsystems Pod` `python3 scripts/zigux/validate-phase4.py` then `zig build test --build-file zigux/tests/phase4_build.zig` in `.github/workflows/zigux-bootstrap.yml` `zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig` `threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks`
`zigux/tests/phase4_bitmap_live_helper_replay.zig` helper-backed replay of the shipped `tools/lib/bitmap.zig` and `tools/lib/find_bit.zig` semantics on the shared Phase 4 entrypoint `Shared Subsystems Pod` `Shared Subsystems Pod` `python3 scripts/zigux/validate-phase4.py` then `zig build test --build-file zigux/tests/phase4_build.zig` in `.github/workflows/zigux-bootstrap.yml` `zig build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig` `threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks`
The shared `zigux/tests/phase4_build.zig` entrypoint now runs `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` beside `zigux/tests/atomic64_diff.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` so the manifest-backed wrapper handoff and the shipped helper-backed bitmap semantics stay reviewable on the same bounded Phase 4 replay surface.
The matching Linux-style local wrappers are `make -C zigux phase4-validate`, `make -C zigux phase4-test`, `make -C zigux phase4-runtime-atomic64-diff`, `make -C zigux phase4-runtime-atomic64-diff-survey`, `make -C zigux phase4-bitmap-diff`, `make -C zigux phase4-bitmap-live-helper-replay`, and `make -C zigux phase4`, so the lab matrix and the current `zigux/Makefile` replay surface stay aligned instead of leaving those local routes implicit beside the direct `python3` and `zig build` commands listed above.
The same validator-first route also keeps `Documentation/zigux/artifact-diff.md` aligned with the shipped host-side helper contract, `Documentation/zigux/phase4-gate-evidence.md` aligned with the dedicated exact-readback checker, and the three shared root README summaries aligned with that same narrower validator-backed packet instead of leaving any of those review surfaces implied.

## Remaining Roadmap Gaps
- `samples/zigux/kprobe_example.zig` is still absent behind the current C anchor at `samples/kprobes/kprobe_example.c`
- `samples/zigux/test_fsmount.zig` is still absent behind the current C anchor at `samples/vfs/test-fsmount.c`
- hard perf thresholds and acceptable limits for the atomic64 and bitmap gates remain intentionally unapproved on current `master`; there is not yet a committed dedicated perf-baseline manifest or survey packet that promotes those limits into the shipped Phase 4 replay surface

This matrix, `scripts/zigux/validate-phase4.py`, and the shared `zigux/tests/phase4_build.zig` entrypoint should stay aligned around that still-pending threshold posture until a later Phase 4 lane intentionally lands a committed threshold-approval packet.

## Review Rules
- Phase 4 remains a rollback-readiness lane first, not a performance-claim lane
- any future hard timing threshold must name the benchmark command, acceptable limit, owner, and rollback owner in this record before the lane claims perf coverage
- if the shared runtime backing regresses, repair `zigux/tests/runtime_atomic64_diff.zig` or remove `zigux/tests/atomic64_diff.zig` and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` from the shared Phase 4 entrypoint until the runtime-backed replay is honest again
- if either gate regresses, the rollback owner must keep the current C anchor and the existing Phase 4 documentation truthful while the Zig replay gate is repaired or removed from the shared entrypoint
- if the host-side helper contract regresses, the rollback owner must keep `Documentation/zigux/artifact-diff.md` and the direct `artifact_diff.py` self-test truthful while the outward CLI replay is repaired or removed from the shared validator path
