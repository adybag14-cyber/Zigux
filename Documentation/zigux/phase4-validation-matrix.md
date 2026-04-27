# Phase 4 Validation Matrix

This document records the live Phase 4 differential-validation ownership and replay matrix.

## Status

- `PHASE4_STATUS=differential_validation_matrix_landed`
- scope: keep the currently shipped Phase 4 rollback-readiness gates reviewable, name the rollback owners for each bounded gate, and make the current CI and local replay paths explicit
- current repo reality:
  - `zigux/tests/runtime_atomic64_diff.zig`
  - `zigux/tests/bitmap_diff.zig`
  - `zigux/tests/phase4_build.zig`
  - `scripts/zigux/validate-phase4.py`
  - `.github/workflows/zigux-bootstrap.yml`
- roadmap note: the roadmap names `zigux/tests/atomic64_diff.zig`, but live `master` currently carries the bounded atomic64 replay gate at `zigux/tests/runtime_atomic64_diff.zig`; this record follows the shipped tree instead of inventing a second parallel gate

## Why this exists

The roadmap says Phase 4 must make future Zigux ports measurable and reversible. The repo already had the shared Phase 4 build entrypoint and validator wiring, but it did not yet keep one reviewable record that named:

- the bounded rollback owner for each live Phase 4 gate
- the current perf threshold status for those gates
- the lab and CI matrix that replays the gates today
- the shared artifact comparator self-test that now runs before the Phase 4 validator claims the rollback-readiness bundle is still aligned

Without that record, Phase 4 validation existed in code but not yet as a product-facing ownership note.

## Gate Ownership

### `zigux/tests/runtime_atomic64_diff.zig`

- anchor: `lib/atomic64_test.c`
- phase bucket: `Phase 4 differential validation via the current live atomic64 replay gate`
- owner: `ABI and Runtime Team`
- rollback owner: `ABI and Runtime Team`
- fallback path: keep the current C anchor plus the existing Phase 9 runtime atomic64 starter surface as the source of truth if the Zig replay gate regresses
- perf threshold status: correctness-only gate today; no hard timing threshold is approved until the lane widens beyond the current bounded exchange, cmpxchg, add_unless, inc_not_zero, and selftest-family replay set

### `zigux/tests/bitmap_diff.zig`

- anchor: `lib/test_bitmap.c`
- phase bucket: `Phase 4 differential validation for the broad bitmap rollback gate`
- owner: `Shared Subsystems Pod`
- rollback owner: `Shared Subsystems Pod`
- fallback path: keep the current C anchor as the source of truth and drop back to the existing broad bitmap parity checks if the Zig replay gate regresses
- perf threshold status: correctness-only gate today; no hard timing threshold is approved until the lane grows past the current bounded range, rounded-prefix, summary, exact nth-lookup, and copy-behavior checkpoints

## Lab And CI Matrix

| lane surface | purpose | owner | rollback owner | bootstrap CI replay | local lab replay | threshold posture |
| --- | --- | --- | --- | --- | --- | --- |
| `zigux/tests/runtime_atomic64_diff.zig` | bounded atomic64 exchange, cmpxchg, add_unless, inc_not_zero, and selftest-family replay | `ABI and Runtime Team` | `ABI and Runtime Team` | workflow steps `Validate Phase 4 diff gates` and `Run Phase 4 diff tests`, which call `make -C zigux phase4-validate` then `make -C zigux phase4-test` in `.github/workflows/zigux-bootstrap.yml` | `make -C zigux phase4-validate`, then `make -C zigux phase4-test`, which runs the shared `phase4-runtime-atomic64-diff-tests` entry in `zigux/tests/phase4_build.zig` | `threshold_pending_until_runtime_atomic64_scope_widens` |
| `zigux/tests/bitmap_diff.zig` | bounded bitmap range, rounded-prefix, summary, exact nth-lookup, and copy-behavior replay | `Shared Subsystems Pod` | `Shared Subsystems Pod` | workflow steps `Validate Phase 4 diff gates` and `Run Phase 4 diff tests`, which call `make -C zigux phase4-validate` then `make -C zigux phase4-test` in `.github/workflows/zigux-bootstrap.yml` | `make -C zigux phase4-validate`, then `make -C zigux phase4-test`, which runs the shared `phase4-bitmap-diff-tests` entry in `zigux/tests/phase4_build.zig` | `threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks` |

## Remaining Measurability Gaps Vs Roadmap

| roadmap item | current repo state | measurability gap | next bounded step |
| --- | --- | --- | --- |
| `samples/zigux/kprobe_example.zig` from the `samples/kprobes/kprobe_example.c` anchor | not present on `master` | rollback owner and lab matrix stay unassigned until a bounded Zig surface lands | add a survey or starter gate that names one owner, one rollback owner, and one replay command before claiming this anchor as active Phase 4 work |
| `samples/zigux/test_fsmount.zig` from the `samples/vfs/test-fsmount.c` anchor | not present on `master` | rollback owner and lab matrix stay unassigned until a bounded Zig surface lands | add a survey or starter gate that names one owner, one rollback owner, and one replay command before claiming this anchor as active Phase 4 work |
| perf baselines and thresholds for the two shipped rollback gates | `zigux/tests/runtime_atomic64_diff.zig` and `zigux/tests/bitmap_diff.zig` are still correctness-only gates today | benchmark command and acceptable limit are still unapproved for both landed gates | land one bounded benchmark command and one acceptable limit per gate before Phase 4 claims perf coverage |

## Review Rules

- Phase 4 remains a rollback-readiness lane first, not a performance-claim lane
- any future hard timing threshold must name the benchmark command, acceptable limit, owner, and rollback owner in this record before the lane claims perf coverage
- any future broad `atomic64_diff.zig` return should replace the current runtime atomic64 path here instead of sitting beside it as a duplicate gate
- if either gate regresses, the rollback owner must keep the current C anchor and the existing Phase 4 documentation truthful while the Zig replay gate is repaired or removed from the shared entrypoint
- if the workflow step names or shared `phase4_build.zig` test names change, update this matrix in the same change so the local lab and CI replay paths stay measurable instead of falling back to generic wording