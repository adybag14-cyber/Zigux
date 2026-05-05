# Phase 4 Validation Matrix

This document records the live Phase 4 differential-validation ownership and replay matrix.

## Status

- `PHASE4_STATUS=differential_validation_matrix_landed`
- scope: keep the currently shipped Phase 4 rollback-readiness gates reviewable, name the rollback owners for each bounded gate, and make the current CI and local replay paths explicit
- current repo reality:
  - `zigux/tests/atomic64_diff.zig`
  - `zigux/tests/runtime_atomic64_diff.zig`
  - `zigux/tests/bitmap_diff.zig`
  - `zigux/tests/phase4_bitmap_live_helper_replay.zig`
  - `zigux/tests/phase4_build.zig`
  - `scripts/zigux/validate-phase4.py`
  - `.github/workflows/zigux-bootstrap.yml`
- roadmap note: live `master` now carries the roadmap-named Phase 4 entrypoint at `zigux/tests/atomic64_diff.zig`, while `zigux/tests/runtime_atomic64_diff.zig` remains the shared runtime-backed implementation that Phase 9 still imports directly

## Why this exists

The roadmap says Phase 4 must make future Zigux ports measurable and reversible. The repo already had the shared Phase 4 build entrypoint and validator wiring, but it did not yet keep one reviewable record that named:

- the bounded rollback owner for each live Phase 4 gate
- the current perf threshold status for those gates
- the lab and CI matrix that replays the gates today

Without that record, Phase 4 validation existed in code but not yet as a product-facing ownership note.

## Gate Ownership

### `zigux/tests/atomic64_diff.zig`

- anchor: `lib/atomic64_test.c`
- phase bucket: `Phase 4 differential validation via the current live atomic64 replay gate`
- owner: `ABI and Runtime Team`
- rollback owner: `ABI and Runtime Team`
- implementation note: `zigux/tests/atomic64_diff.zig` imports `zigux/tests/runtime_atomic64_diff.zig` so Phase 4 keeps the roadmap path without cloning the shared runtime-backed replay logic that Phase 9 already reuses directly
- fallback path: keep the current C anchor plus the existing Phase 9 runtime atomic64 starter surface as the source of truth if the Zig replay gate regresses
- perf threshold status: correctness-only gate today; no hard timing threshold is approved until the lane widens beyond the current bounded exchange, cmpxchg, add_unless, and selftest-family replay set

### `zigux/tests/bitmap_diff.zig`

- anchor: `lib/test_bitmap.c`
- phase bucket: `Phase 4 differential validation for the broad bitmap rollback gate`
- owner: `Shared Subsystems Pod`
- rollback owner: `Shared Subsystems Pod`
- implementation note: `zigux/tests/bitmap_diff.zig` remains the roadmap-named synthetic rollback gate, while `zigux/tests/phase4_bitmap_live_helper_replay.zig` now keeps the shipped `tools/lib/bitmap.zig` and `tools/lib/find_bit.zig` semantics explicit on the same shared `phase4_build.zig` entrypoint without changing the rollback owner or widening this lane into direct helper implementation ownership
- fallback path: keep the current C anchor as the source of truth and drop back to the existing broad bitmap parity checks if the Zig replay gate regresses
- perf threshold status: correctness-only gate today; no hard timing threshold is approved until the lane grows past the current bounded range, prefix, and copy-behavior checkpoints

## Lab And CI Matrix

| lane surface | purpose | owner | rollback owner | bootstrap CI replay | local lab replay | threshold posture |
| --- | --- | --- | --- | --- | --- | --- |
| `zigux/tests/atomic64_diff.zig` | bounded atomic64 exchange, cmpxchg, add_unless, and selftest-family replay via the shared runtime-backed gate | `ABI and Runtime Team` | `ABI and Runtime Team` | `python3 scripts/zigux/validate-phase4.py` then `zig build test --build-file zigux/tests/phase4_build.zig` in `.github/workflows/zigux-bootstrap.yml` | `python3 scripts/zigux/validate-phase4.py` then `zig build test --build-file zigux/tests/phase4_build.zig` | `threshold_pending_until_runtime_atomic64_scope_widens` |
| `zigux/tests/bitmap_diff.zig` | bounded broad bitmap rollback-readiness replay | `Shared Subsystems Pod` | `Shared Subsystems Pod` | `python3 scripts/zigux/validate-phase4.py` then `zig build test --build-file zigux/tests/phase4_build.zig` in `.github/workflows/zigux-bootstrap.yml` | `python3 scripts/zigux/validate-phase4.py` then `zig build test --build-file zigux/tests/phase4_build.zig` | `threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks` |

The shared `zigux/tests/phase4_build.zig` entrypoint now also runs `zigux/tests/phase4_bitmap_live_helper_replay.zig`, which keeps the shipped helper-backed exact-fill versus rounded-zero bitmap semantics reviewable beside the roadmap-named `zigux/tests/bitmap_diff.zig` gate without changing the matrix row ownership or threshold posture.

## Review Rules

- Phase 4 remains a rollback-readiness lane first, not a performance-claim lane
- any future hard timing threshold must name the benchmark command, acceptable limit, owner, and rollback owner in this record before the lane claims perf coverage
- if the shared runtime backing regresses, repair `zigux/tests/runtime_atomic64_diff.zig` or remove `zigux/tests/atomic64_diff.zig` from the shared Phase 4 entrypoint until the runtime-backed replay is honest again
- if either gate regresses, the rollback owner must keep the current C anchor and the existing Phase 4 documentation truthful while the Zig replay gate is repaired or removed from the shared entrypoint
