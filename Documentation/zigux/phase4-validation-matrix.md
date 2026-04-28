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
- the reversible-delivery evidence that ties each shipped Zig gate back to its current C anchor if the shared entrypoint has to drop that gate
- the shared artifact comparator self-test that now runs before the Phase 4 validator claims the rollback-readiness bundle is still aligned
- one isolated runtime atomic64 replay command that can be run without depending on the bitmap lane staying green on the same head

Without that record, Phase 4 validation existed in code but not yet as a product-facing ownership note.

## Gate Ownership

### `zigux/tests/runtime_atomic64_diff.zig`

- anchor: `lib/atomic64_test.c`
- phase bucket: `Phase 4 differential validation via the current live atomic64 replay gate`
- owner: `ABI and Runtime Team`
- rollback owner: `ABI and Runtime Team`
- fallback path: keep the current C anchor plus the existing Phase 9 runtime atomic64 starter surface as the source of truth if the Zig replay gate regresses
- perf threshold status: correctness-only gate today; no hard timing threshold is approved until the lane widens beyond the current bounded add, exchange, cmpxchg, add_unless, inc_not_zero, dec_if_positive, and selftest-family plus post-selftest replay set

### `zigux/tests/bitmap_diff.zig`

- anchor: `lib/test_bitmap.c`
- phase bucket: `Phase 4 differential validation for the broad bitmap rollback gate`
- owner: `Shared Subsystems Pod`
- rollback owner: `Shared Subsystems Pod`
- fallback path: keep the current C anchor as the source of truth and drop back to the existing broad bitmap parity checks if the Zig replay gate regresses
- exact bounded checks: `bitmap_fill(..., 35)` rounds to one full word, `bitmap_zero(..., 115)` rounds to two full words, the cross-boundary `bitmap_set(..., 79, 19)` and `bitmap_clear(..., 79, 19)` cases keep the 64..78 and 98..1023 boundaries explicit, full-width `bitmap_fill(..., 1024)` and `bitmap_zero(..., 1024)` keep the endpoints honest, `bitmap_scnprintf()` preserves both the full `1-3,7,10-11` summary and the truncated `1-3` rendering, `bitmap_copy()` replays the 109-bit partial-tail and 97-bit aligned-copy cases while `bitmap.copyClearTail()` keeps the 109-bit cleared-tail contract, and `find_nth_bit()` records both the full-width nth-7 and nth-8 outcomes plus the reduced-width `64 * 3 - 1` cutoff that still returns bit 123 for nth 6 and the cutoff width for nth 7
- current rollback evidence gap: paired `bitmap_zero(..., 35)` and `bitmap_fill(..., 115)` rounded-prefix checkpoints stay out of the shipped gate until `tools/lib/bitmap.zig` matches the `lib/test_bitmap.c` anchor on those cases
- perf threshold status: correctness-only gate today; no hard timing threshold is approved until the lane grows past the current bounded range, cross-boundary set-clear, summary, exact nth-lookup, and copy-behavior checkpoints

## Lab And CI Matrix

| lane surface | purpose | owner | rollback owner | bootstrap CI replay | local lab replay | reversible delivery evidence | threshold posture |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `zigux/tests/runtime_atomic64_diff.zig` | bounded atomic64 add, exchange, cmpxchg, add_unless, inc_not_zero, dec_if_positive, and selftest-family plus post-selftest replay | `ABI and Runtime Team` | `ABI and Runtime Team` | workflow steps `Validate Phase 4 diff gates` and `Run Phase 4 diff tests`, which call `make -C zigux phase4-validate` then `make -C zigux phase4-test` in `.github/workflows/zigux-bootstrap.yml` | `make -C zigux phase4-validate`, then `make -C zigux phase4-test`, which runs the shared `phase4-runtime-atomic64-diff-tests` entry in `zigux/tests/phase4_build.zig`; an isolated `zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig` replay remains optional when that dedicated step exists locally | `lib/atomic64_test.c` stays the source of truth, and removing `runtime_atomic64_diff.zig` from the shared `phase4_build.zig` entrypoint is the documented rollback move while the existing Phase 9 runtime atomic64 starter remains the forward path | `threshold_pending_until_runtime_atomic64_scope_widens` |
| `zigux/tests/bitmap_diff.zig` | bounded bitmap range, cross-boundary set-clear, summary, exact nth-lookup, and copy-behavior replay | `Shared Subsystems Pod` | `Shared Subsystems Pod` | workflow steps `Validate Phase 4 diff gates` and `Run Phase 4 diff tests`, which call `make -C zigux phase4-validate` then `make -C zigux phase4-test` in `.github/workflows/zigux-bootstrap.yml` | `make -C zigux phase4-validate`, then `make -C zigux phase4-test`, which runs the shared `phase4-bitmap-diff-tests` entry in `zigux/tests/phase4_build.zig` | `lib/test_bitmap.c` stays the source of truth, and removing `bitmap_diff.zig` from the shared `phase4_build.zig` entrypoint falls back to the existing broad bitmap parity checks | `threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks` |

## Remaining Measurability Gaps Vs Roadmap

| roadmap item | current repo state | measurability gap | next bounded step |
| --- | --- | --- | --- |
| `samples/zigux/kprobe_example.zig` from the `samples/kprobes/kprobe_example.c` anchor | not present on `master`; the current anchor remains `samples/kprobes/kprobe_example.c` through `samples/kprobes/Makefile` and `CONFIG_SAMPLE_KPROBES` | reserve `Validation and Perf Team` as both survey owner and rollback owner while the current replay stays on the C anchor via `make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m`; no hard timing threshold is approved before a bounded Zig sample lands | land one bounded survey manifest or starter gate under `samples/zigux/` that keeps the same owner, rollback owner, and replay command before claiming this anchor as active Phase 4 work |
| `samples/zigux/test_fsmount.zig` from the `samples/vfs/test-fsmount.c` anchor | not present on `master`; the current anchor remains `samples/vfs/test-fsmount.c` through `samples/vfs/Makefile` and `userprogs-always-y += test-fsmount` | survey owner, rollback owner, and Zig lab matrix stay unassigned while the current replay stays on the C anchor via `make M=samples/vfs`; no hard timing threshold is approved before a bounded Zig sample lands | add a survey or starter gate that names one survey owner, one rollback owner, and one replay command before claiming this anchor as active Phase 4 work |
| perf baselines and thresholds for the two shipped rollback gates | `zigux/tests/runtime_atomic64_diff.zig` and `zigux/tests/bitmap_diff.zig` are still correctness-only gates today | benchmark command and acceptable limit are still unapproved for both landed gates | land one bounded benchmark command and one acceptable limit per gate before Phase 4 claims perf coverage |

## Review Rules

- Phase 4 remains a rollback-readiness lane first, not a performance-claim lane
- any future hard timing threshold must name the benchmark command, acceptable limit, owner, and rollback owner in this record before the lane claims perf coverage
- any future broad `atomic64_diff.zig` return should replace the current runtime atomic64 path here instead of sitting beside it as a duplicate gate
- if either gate regresses, the rollback owner must keep the current C anchor and the existing Phase 4 documentation truthful while the Zig replay gate is repaired or removed from the shared entrypoint
- if the workflow step names or shared `phase4_build.zig` test names change, update this matrix in the same change so the local lab and CI replay paths stay measurable instead of falling back to generic wording
